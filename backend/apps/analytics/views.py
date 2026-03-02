import logging
import redis as redis_client
from datetime import timedelta
from collections import defaultdict
from django.conf import settings
from django.core.cache import cache
from django.db.models import Count
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.tasks.models import ActivityLog, Task, UserTask

logger = logging.getLogger(__name__)

ANALYTICS_CACHE_TTL = 5 * 60


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analytics_me_view(request):
    user = request.user
    cache_key = f'analytics_me:{user.id}'
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return Response(cached_data)

    # Heatmap за 365 дней
    since = timezone.now() - timedelta(days=365)
    heatmap = defaultdict(lambda: {'tasks': 0, 'xp': 0, 'time_minutes': 0})
    for created_at, metadata in ActivityLog.objects.filter(
        user=user,
        action=ActivityLog.ACTION_TASK_COMPLETED,
        created_at__gte=since,
    ).values_list('created_at', 'metadata'):
        date_key = created_at.date().isoformat()
        heatmap[date_key]['tasks'] += 1
        heatmap[date_key]['xp'] += metadata.get('xp_earned', 0)
        heatmap[date_key]['time_minutes'] += metadata.get('time_spent', 0) // 60

    # Навыки по категориям — 2 запроса
    categories = ['linux', 'nginx', 'systemd', 'docker', 'networks', 'git', 'cicd']
    total_by_cat = dict(
        Task.objects.filter(is_active=True, category__in=categories)
        .values('category').annotate(n=Count('id')).values_list('category', 'n')
    )
    completed_by_cat = dict(
        UserTask.objects.filter(user=user, status='completed')
        .values('task__category').annotate(n=Count('id')).values_list('task__category', 'n')
    )
    skills = {
        cat: {
            'completed': completed_by_cat.get(cat, 0),
            'total': total_by_cat.get(cat, 0),
            'pct': round(completed_by_cat.get(cat, 0) / total_by_cat[cat] * 100, 1) if total_by_cat.get(cat) else 0,
        }
        for cat in categories
    }

    completed_tasks = UserTask.objects.filter(user=user, status='completed')

    # Недельная статистика — один запрос на период, один проход по данным
    now = timezone.now()

    def week_stats(start, end):
        rows = list(
            ActivityLog.objects.filter(
                user=user,
                action=ActivityLog.ACTION_TASK_COMPLETED,
                created_at__gte=start,
                created_at__lt=end,
            ).values_list('metadata', flat=True)
        )
        xp = sum(m.get('xp_earned', 0) for m in rows)
        time_m = sum(m.get('time_spent', 0) for m in rows) // 60
        return {'tasks': len(rows), 'xp': xp, 'time_minutes': time_m}

    current_week = week_stats(now - timedelta(days=7), now)
    previous_week = week_stats(now - timedelta(days=14), now - timedelta(days=7))

    prev_tasks = previous_week['tasks'] or 1
    change_pct = round((current_week['tasks'] - previous_week['tasks']) / prev_tasks * 100)

    # Стрик
    today = now.date()
    yesterday = today - timedelta(days=1)
    streak_at_risk = (
        user.streak > 0
        and user.last_active is not None
        and user.last_active < today
        and user.last_active != yesterday
    )

    # Прогноз — один проход
    rows_14d = list(
        ActivityLog.objects.filter(
            user=user,
            action=ActivityLog.ACTION_TASK_COMPLETED,
            created_at__gte=now - timedelta(days=14),
        ).values_list('metadata', flat=True)
    )
    total_xp_14d = sum(m.get('xp_earned', 0) for m in rows_14d)
    xp_per_day = total_xp_14d / 14 if total_xp_14d > 0 else 1
    xp_to_next = user.xp_to_next_level
    days_to_next = round(xp_to_next / xp_per_day) if xp_per_day > 0 and xp_to_next > 0 else 0

    ai_insight = _get_ai_insight(user, skills, current_week)

    weak_categories = [cat for cat, s in skills.items() if s['pct'] < 50 and s['total'] > 0]
    recommended = _get_recommended_tasks(user, weak_categories, completed_tasks)

    data = {
        'heatmap': dict(heatmap),
        'skills': skills,
        'total_completed': sum(completed_by_cat.values()),
        'weekly': {
            'current': current_week,
            'previous': previous_week,
            'change_pct': change_pct,
        },
        'streak': {
            'current': user.streak,
            'max': user.max_streak,
            'at_risk': streak_at_risk,
        },
        'forecast': {
            'days_to_next_level': days_to_next,
            'tasks_per_day_needed': round(xp_per_day / 100, 1),
            'xp_to_next_level': xp_to_next,
        },
        'ai_insight': ai_insight,
        'recommended_tasks': recommended,
        'user': {
            'level': user.level,
            'xp': user.xp,
            'level_progress_pct': user.level_progress_pct,
        },
    }

    cache.set(cache_key, data, timeout=ANALYTICS_CACHE_TTL)
    return Response(data)


def _get_ai_insight(user, skills: dict, weekly: dict) -> str:
    try:
        r = redis_client.from_url(settings.REDIS_URL)
        cache_key = f'ai_insight:{user.id}'
        cached = r.get(cache_key)
        if cached:
            return cached.decode('utf-8')

        from apps.ai.ollama_client import OllamaClient
        insight = OllamaClient().generate_personal_insight({
            'level': user.level,
            'xp': user.xp,
            'streak': user.streak,
            'weekly_tasks': weekly.get('tasks', 0),
            'skills': skills,
        })

        if insight:
            r.setex(cache_key, 3600, insight)
        return insight or 'Продолжай в том же темпе!'

    except Exception as e:
        logger.warning(f'AI insight error: {e}')
        return 'Продолжай практиковаться — регулярность важнее скорости!'


def _get_recommended_tasks(user, weak_categories: list, completed_tasks) -> list:
    completed_ids = {ut.task_id for ut in completed_tasks}
    recommended = []
    for cat in weak_categories[:3]:
        task = Task.objects.filter(
            category=cat,
            is_active=True,
        ).exclude(id__in=completed_ids).order_by('order').first()
        if task:
            recommended.append({
                'id': task.id,
                'title_ru': task.title_ru,
                'category': task.category,
                'difficulty': task.difficulty,
                'xp_reward': task.xp_reward,
                'reason': f'Слабое место: {cat}',
            })
    return recommended


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analytics_export_pdf_view(request):
    from .export import generate_progress_report
    from django.http import HttpResponse

    pdf_bytes = generate_progress_report(request.user)

    if not pdf_bytes:
        return Response({'error': 'Не удалось сгенерировать PDF. Попробуйте позже.'}, status=503)

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="progress_{request.user.username}.pdf"'
    return response
