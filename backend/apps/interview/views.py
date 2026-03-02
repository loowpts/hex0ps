from django.db.models import Count
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import InterviewQuestion, InterviewAttempt


@api_view(['GET'])
@permission_classes([AllowAny])
def categories_view(request):
    totals = {
        item['category']: item['count']
        for item in InterviewQuestion.objects.filter(is_active=True)
        .values('category').annotate(count=Count('id'))
    }

    if request.user.is_authenticated:
        answered = {
            item['question__category']: item['count']
            for item in InterviewAttempt.objects.filter(user=request.user)
            .values('question__category')
            .annotate(count=Count('question', distinct=True))
        }
    else:
        answered = {}

    categories = [
        {
            'category': value,
            'label': label,
            'total': totals.get(value, 0),
            'answered': answered.get(value, 0),
        }
        for value, label in InterviewQuestion.CATEGORY_CHOICES
        if totals.get(value, 0) > 0
    ]
    return Response(categories)


@api_view(['GET'])
@permission_classes([AllowAny])
def question_list_view(request):
    queryset = InterviewQuestion.objects.filter(is_active=True)

    category = request.query_params.get('category')
    if category:
        queryset = queryset.filter(category=category)

    difficulty = request.query_params.get('difficulty')
    if difficulty:
        queryset = queryset.filter(difficulty=difficulty)

    data = [
        {
            'id': q.id,
            'question_ru': q.question_ru,
            'category': q.category,
            'difficulty': q.difficulty,
            'tags': q.tags,
        }
        for q in queryset
    ]
    return Response(data)


@api_view(['GET'])
@permission_classes([AllowAny])
def question_detail_view(request, question_id):
    try:
        q = InterviewQuestion.objects.get(id=question_id, is_active=True)
    except InterviewQuestion.DoesNotExist:
        return Response({'error': 'Вопрос не найден.'}, status=status.HTTP_404_NOT_FOUND)

    return Response({
        'id': q.id,
        'question_ru': q.question_ru,
        'category': q.category,
        'difficulty': q.difficulty,
        'tags': q.tags,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def answer_view(request):
    question_id = request.data.get('question_id')
    answer = request.data.get('answer', '').strip()

    if not question_id or not answer:
        return Response(
            {'error': 'question_id и answer обязательны.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if len(answer) < 20:
        return Response(
            {'error': 'Ответ слишком короткий. Напиши развёрнутый ответ.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        question = InterviewQuestion.objects.get(id=question_id, is_active=True)
    except InterviewQuestion.DoesNotExist:
        return Response({'error': 'Вопрос не найден.'}, status=status.HTTP_404_NOT_FOUND)

    from apps.ai.ollama_client import OllamaClient
    evaluation = OllamaClient().evaluate_interview_answer(
        question.question_ru,
        answer,
        question.sample_answer_ru,
    )

    attempt = InterviewAttempt.objects.create(
        user=request.user,
        question=question,
        user_answer=answer,
        ai_score=evaluation.get('score'),
        ai_feedback=evaluation.get('feedback', ''),
        ai_strengths=evaluation.get('strengths', []),
        ai_improvements=evaluation.get('improvements', []),
    )

    return Response({
        'attempt_id': attempt.id,
        'score': attempt.ai_score,
        'feedback': attempt.ai_feedback,
        'strengths': attempt.ai_strengths,
        'improvements': attempt.ai_improvements,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def history_view(request):
    attempts = InterviewAttempt.objects.filter(
        user=request.user
    ).select_related('question').order_by('-created_at')[:50]

    data = [
        {
            'id': a.id,
            'question_id': a.question_id,
            'question_ru': a.question.question_ru[:100],
            'category': a.question.category,
            'ai_score': a.ai_score,
            'created_at': a.created_at,
        }
        for a in attempts
    ]
    return Response(data)
