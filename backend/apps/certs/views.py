"""
Views для сертификатов.
"""
import os
from django.http import FileResponse, Http404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import Certificate


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cert_list_view(request):
    """Список сертификатов текущего пользователя."""
    certs = Certificate.objects.filter(user=request.user).order_by('-issued_at')
    data = [
        {
            'cert_id': str(c.cert_id),
            'category': c.category,
            'category_display': c.get_category_display(),
            'issued_at': c.issued_at,
            'pdf_url': c.pdf_url or None,
        }
        for c in certs
    ]
    return Response(data)


@api_view(['GET'])
@permission_classes([AllowAny])
def cert_verify_view(request, cert_id):
    """
    Публичная верификация сертификата по UUID.
    Доступна без авторизации.
    """
    try:
        cert = Certificate.objects.select_related('user').get(cert_id=cert_id)
    except Certificate.DoesNotExist:
        return Response(
            {'error': 'Сертификат не найден или недействителен.'},
            status=status.HTTP_404_NOT_FOUND
        )

    return Response({
        'valid': True,
        'cert_id': str(cert.cert_id),
        'username': cert.user.username,
        'category': cert.category,
        'category_display': cert.get_category_display(),
        'issued_at': cert.issued_at,
        'message': f'Сертификат действителен. {cert.user.username} завершил(а) курс {cert.get_category_display()}.',
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def cert_download_view(request, cert_id):
    """Скачать PDF сертификата."""
    try:
        cert = Certificate.objects.get(cert_id=cert_id)
    except Certificate.DoesNotExist:
        raise Http404('Сертификат не найден')

    # Если PDF ещё не создан — создаём синхронно
    if not cert.pdf_url:
        try:
            cert.generate_pdf()
        except Exception:
            return Response(
                {'error': 'PDF временно недоступен. Попробуй позже.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

    from django.conf import settings
    pdf_path = os.path.join(settings.MEDIA_ROOT, 'certs', f'{cert.cert_id}.pdf')

    if not os.path.exists(pdf_path):
        raise Http404('PDF файл не найден')

    return FileResponse(
        open(pdf_path, 'rb'),
        content_type='application/pdf',
        as_attachment=True,
        filename=f'devops_cert_{cert.category}_{cert.cert_id}.pdf'
    )
