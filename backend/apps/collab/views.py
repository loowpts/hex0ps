from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import CollabSession


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_invite_view(request):
    session_id = request.data.get('terminal_session_id')
    if not session_id:
        return Response({'error': 'terminal_session_id обязателен.'}, status=400)

    from apps.terminal.models import TerminalSession
    try:
        terminal_session = TerminalSession.objects.get(
            id=session_id,
            user=request.user,
            status='active',
        )
    except TerminalSession.DoesNotExist:
        return Response(
            {'error': 'Активная терминальная сессия не найдена.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    collab = CollabSession.objects.create(
        owner=request.user,
        terminal_session=terminal_session,
        active_user=request.user,
    )

    return Response({
        'collab_id': str(collab.id),
        'invite_token': str(collab.invite_token),
        'invite_url': f'/collab/{collab.invite_token}',
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny])
def collab_info_view(request, invite_token):
    try:
        collab = CollabSession.objects.select_related(
            'owner', 'terminal_session__task'
        ).get(invite_token=invite_token)
    except CollabSession.DoesNotExist:
        return Response({'error': 'Приглашение не найдено.'}, status=status.HTTP_404_NOT_FOUND)

    return Response({
        'collab_id': str(collab.id),
        'owner': collab.owner.username,
        'task': {
            'id': collab.terminal_session.task.id,
            'title_ru': collab.terminal_session.task.title_ru,
        },
        'status': collab.status,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_collab_view(request, invite_token):
    try:
        collab = CollabSession.objects.select_related('owner').get(
            invite_token=invite_token,
            status=CollabSession.STATUS_WAITING,
        )
    except CollabSession.DoesNotExist:
        return Response(
            {'error': 'Приглашение не найдено или уже использовано.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    if collab.owner == request.user:
        return Response(
            {'error': 'Нельзя присоединиться к своей же сессии.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    collab.guest = request.user
    collab.status = CollabSession.STATUS_ACTIVE
    collab.save(update_fields=['guest', 'status'])

    return Response({
        'collab_id': str(collab.id),
        'ws_url': f'/ws/collab/{collab.id}/',
        'message': f'Ты присоединился к сессии {collab.owner.username}!',
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_control_view(request, invite_token):
    try:
        collab = CollabSession.objects.select_related('owner', 'guest').get(
            invite_token=invite_token,
        )
    except CollabSession.DoesNotExist:
        return Response({'error': 'Сессия не найдена.'}, status=status.HTTP_404_NOT_FOUND)

    if request.user not in (collab.owner, collab.guest):
        return Response({'error': 'Нет доступа к этой сессии.'}, status=status.HTTP_403_FORBIDDEN)

    collab.active_user = request.user
    collab.save(update_fields=['active_user'])

    return Response({
        'active_user': request.user.username,
        'message': 'Управление передано.',
    })
