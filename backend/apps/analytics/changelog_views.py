"""
View для списка обновлений платформы.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Changelog


@api_view(['GET'])
@permission_classes([AllowAny])
def changelog_view(request):
    """Список всех обновлений, новые первыми."""
    entries = Changelog.objects.all().order_by('-published_at')
    data = [
        {
            'id': e.id,
            'version': e.version,
            'title': e.title,
            'body_md': e.body_md,
            'published_at': e.published_at,
        }
        for e in entries
    ]
    return Response(data)
