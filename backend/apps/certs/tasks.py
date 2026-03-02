"""
Celery задача для асинхронной генерации PDF сертификатов.
"""
import logging
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def generate_certificate_pdf(cert_id: int):
    """
    Асинхронно генерирует PDF для сертификата.
    Вызывается после создания Certificate.
    """
    from apps.certs.models import Certificate
    try:
        cert = Certificate.objects.get(id=cert_id)
        path = cert.generate_pdf()
        logger.info(f'Сертификат {cert.cert_id} сгенерирован: {path}')
    except Certificate.DoesNotExist:
        logger.error(f'Сертификат с id={cert_id} не найден')
    except Exception as e:
        logger.error(f'Ошибка генерации PDF сертификата {cert_id}: {e}')
