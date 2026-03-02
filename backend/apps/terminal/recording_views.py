"""
Views для записей сессий (шеринг и воспроизведение).
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import SessionRecording


@api_view(['GET'])
@permission_classes([AllowAny])
def recording_detail_view(request, share_id):
    """
    Публичный endpoint для просмотра записи сессии.
    Доступен без авторизации если запись публичная.
    """
    try:
        recording = SessionRecording.objects.select_related(
            'session__user', 'session__task'
        ).get(share_id=share_id)
    except SessionRecording.DoesNotExist:
        return Response(
            {'error': 'Запись не найдена.'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Приватная запись — только владелец
    if not recording.is_public:
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Эта запись приватная.'},
                status=status.HTTP_403_FORBIDDEN
            )
        if recording.session.user != request.user:
            return Response(
                {'error': 'Доступ запрещён.'},
                status=status.HTTP_403_FORBIDDEN
            )

    return Response({
        'share_id': str(recording.share_id),
        'events': recording.events_json,
        'cols': recording.cols,
        'rows': recording.rows,
        'duration_seconds': recording.duration_seconds,
        'is_public': recording.is_public,
        'created_at': recording.created_at,
        'author': recording.session.user.username,
        'task': {
            'id': recording.session.task.id,
            'title_ru': recording.session.task.title_ru,
            'category': recording.session.task.category,
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def recording_share_view(request, share_id):
    """Делает запись публичной (только владелец)."""
    try:
        recording = SessionRecording.objects.select_related('session').get(share_id=share_id)
    except SessionRecording.DoesNotExist:
        return Response({'error': 'Запись не найдена.'}, status=status.HTTP_404_NOT_FOUND)

    if recording.session.user != request.user:
        return Response({'error': 'Доступ запрещён.'}, status=status.HTTP_403_FORBIDDEN)

    recording.is_public = True
    recording.save(update_fields=['is_public'])

    return Response({
        'share_url': f'/replay/{recording.share_id}',
        'message': 'Запись опубликована! Поделись ссылкой.'
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def recording_delete_view(request, share_id):
    """Удаляет запись (только владелец)."""
    try:
        recording = SessionRecording.objects.select_related('session').get(share_id=share_id)
    except SessionRecording.DoesNotExist:
        return Response({'error': 'Запись не найдена.'}, status=status.HTTP_404_NOT_FOUND)

    if recording.session.user != request.user:
        return Response({'error': 'Доступ запрещён.'}, status=status.HTTP_403_FORBIDDEN)

    recording.delete()
    return Response({'message': 'Запись удалена.'})
