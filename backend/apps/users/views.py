import logging

from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.certs.models import Certificate
from apps.tasks.models import UserTask
from apps.users.achievements import get_user_achievements_data

from .models import User
from .serializers import (
    UserLoginSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    UserSettingsSerializer,
    PublicProfileSerializer,
)
from .throttles import LoginThrottle

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([LoginThrottle])
def login_view(request):
    serializer = UserLoginSerializer(data=request.data, context={'request': request})
    if not serializer.is_valid():
        return Response(
            {'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = serializer.validated_data['user']
    refresh = RefreshToken.for_user(user)

    user.update_streak()

    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': UserProfileSerializer(user).data,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token_view(request):
    refresh_token = request.data.get('refresh')
    if not refresh_token:
        return Response(
            {'error': 'Refresh token обязателен.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        refresh = RefreshToken(refresh_token)
        return Response({
            'access': str(refresh.access_token),
        })
    except TokenError:
        return Response(
            {'error': 'Недействительный или просроченный refresh token.'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def me_view(request):
    if request.method == 'GET':
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    serializer = UserProfileUpdateSerializer(
        request.user,
        data=request.data,
        partial=True,
        context={'request': request}
    )
    if not serializer.is_valid():
        return Response(
            {'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    serializer.save()
    return Response(UserProfileSerializer(request.user).data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def me_settings_view(request):
    serializer = UserSettingsSerializer(
        request.user,
        data=request.data,
        partial=True
    )
    if not serializer.is_valid():
        return Response(
            {'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    serializer.save()
    return Response({
        'message': 'Настройки обновлены.',
        **serializer.data,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def public_profile_view(request, username):
    user = get_object_or_404(User, username__iexact=username)

    if not user.is_public:
        return Response(
            {'error': 'Профиль пользователя скрыт.'},
            status=status.HTTP_404_NOT_FOUND
        )

    skills = dict(
        UserTask.objects.filter(user=user, status='completed')
        .values('task__category')
        .annotate(count=Count('id'))
        .values_list('task__category', 'count')
    )
    completed_tasks_count = sum(skills.values())

    try:
        certs = Certificate.objects.filter(user=user)
        certs_data = [
            {
                'category': c.category,
                'issued_at': c.issued_at.date().isoformat(),
                'cert_id': str(c.cert_id),
            }
            for c in certs
        ]
    except Exception as e:
        logger.error(f'Ошибка загрузки сертификатов для {user.username}: {e}')
        certs_data = []

    try:
        achievements_data = get_user_achievements_data(user)
    except Exception as e:
        logger.error(f'Ошибка загрузки достижений для {user.username}: {e}')
        achievements_data = []

    serializer = PublicProfileSerializer(user)
    data = serializer.data
    data['skills'] = skills
    data['completed_tasks_count'] = completed_tasks_count
    data['certificates'] = certs_data
    data['achievements'] = achievements_data

    return Response(data)
