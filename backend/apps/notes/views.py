"""
Views для заметок: CRUD, поиск, экспорт.
"""
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Note


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def note_list_view(request):
    """
    Все заметки пользователя.
    Query: ?search=текст — полнотекстовый поиск.
    """
    queryset = Note.objects.filter(user=request.user).select_related('task')

    search = request.query_params.get('search', '').strip()
    if search:
        queryset = queryset.filter(content__icontains=search)

    data = [
        {
            'id': n.id,
            'task_id': n.task_id,
            'task_title': n.task.title_ru if n.task else None,
            'preview': n.content[:200],
            'updated_at': n.updated_at,
        }
        for n in queryset
    ]
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def note_detail_view(request, task_id):
    """Заметка к конкретной задаче."""
    try:
        note = Note.objects.get(user=request.user, task_id=task_id)
        return Response({
            'id': note.id,
            'task_id': note.task_id,
            'content': note.content,
            'updated_at': note.updated_at,
        })
    except Note.DoesNotExist:
        return Response({'content': '', 'task_id': task_id})


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def note_upsert_view(request, task_id):
    """
    Создать или обновить заметку к задаче (upsert).
    Body: {content: "..."}
    """
    content = request.data.get('content', '')

    from apps.tasks.models import Task
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return Response({'error': 'Задача не найдена.'}, status=status.HTTP_404_NOT_FOUND)

    note, created = Note.objects.update_or_create(
        user=request.user,
        task=task,
        defaults={'content': content}
    )

    return Response({
        'id': note.id,
        'task_id': note.task_id,
        'content': note.content,
        'updated_at': note.updated_at,
        'created': created,
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def note_delete_view(request, task_id):
    """Удалить заметку к задаче."""
    deleted, _ = Note.objects.filter(user=request.user, task_id=task_id).delete()
    if deleted:
        return Response({'message': 'Заметка удалена.'})
    return Response({'error': 'Заметка не найдена.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def note_export_view(request):
    """
    Экспорт всех заметок в один .md файл.
    """
    notes = Note.objects.filter(user=request.user).select_related('task').order_by('-updated_at')

    lines = [
        f'# Заметки DevOps Learning Platform — {request.user.username}',
        f'> Экспорт: {timezone.now().strftime("%d.%m.%Y %H:%M")}',
        '',
    ]

    for note in notes:
        title = note.task.title_ru if note.task else 'Общие заметки'
        category = f' [{note.task.category}]' if note.task else ''
        lines.append(f'## {title}{category}')
        lines.append(f'*Обновлено: {note.updated_at.strftime("%d.%m.%Y")}*')
        lines.append('')
        lines.append(note.content)
        lines.append('')
        lines.append('---')
        lines.append('')

    content = '\n'.join(lines)

    response = HttpResponse(content, content_type='text/markdown; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="devops_notes_{request.user.username}.md"'
    return response
