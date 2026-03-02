"""
Кастомные permissions для DevOps Learning Platform.
"""
from rest_framework.permissions import BasePermission


class IsOwnerOrReadOnly(BasePermission):
    """
    Разрешает редактирование только владельцу объекта.
    """
    def has_object_permission(self, request, view, obj):
        # Безопасные методы (GET, HEAD, OPTIONS) разрешены всем
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        # Запись — только владелец
        return obj == request.user or getattr(obj, 'user', None) == request.user


class IsPublicProfile(BasePermission):
    """
    Разрешает доступ к профилю только если он публичный.
    """
    def has_object_permission(self, request, view, obj):
        return obj.is_public
