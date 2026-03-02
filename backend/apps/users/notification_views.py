"""
Views для уведомлений пользователя.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.analytics.models import Notification


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_list_view(request):
    """Список уведомлений — непрочитанные первыми."""
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('read', '-created_at')[:50]

    data = [
        {
            'id': n.id,
            'type': n.type,
            'message': n.message,
            'read': n.read,
            'created_at': n.created_at,
        }
        for n in notifications
    ]
    return Response({
        'notifications': data,
        'unread_count': Notification.objects.filter(user=request.user, read=False).count(),
    })


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def notification_read_view(request, notification_id):
    """Отметить уведомление как прочитанное."""
    updated = Notification.objects.filter(
        id=notification_id,
        user=request.user
    ).update(read=True)

    if updated:
        return Response({'message': 'Уведомление отмечено как прочитанное.'})
    return Response({'error': 'Уведомление не найдено.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def notification_read_all_view(request):
    """Отметить все уведомления как прочитанные."""
    count = Notification.objects.filter(user=request.user, read=False).update(read=True)
    return Response({'message': f'Отмечено прочитанными: {count} уведомлений.'})
