"""
Модели сертификатов — выдаются при 100% завершении категории.
"""
import uuid
from django.db import models
from django.conf import settings


class Certificate(models.Model):
    """
    Сертификат о прохождении категории.
    Генерируется PDF через WeasyPrint.
    """

    CATEGORY_NAMES = {
        'linux': 'Linux',
        'nginx': 'Nginx',
        'systemd': 'Systemd',
        'docker': 'Docker',
        'networks': 'Сети',
        'git': 'Git',
        'cicd': 'CI/CD',
    }

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='certificates',
        verbose_name='Пользователь'
    )
    category = models.CharField(max_length=20, verbose_name='Категория')
    cert_id = models.UUIDField(default=uuid.uuid4, unique=True, verbose_name='ID сертификата')
    issued_at = models.DateTimeField(auto_now_add=True, verbose_name='Выдан')
    pdf_url = models.CharField(max_length=200, blank=True, verbose_name='URL PDF')

    class Meta:
        verbose_name = 'Сертификат'
        verbose_name_plural = 'Сертификаты'
        unique_together = ['user', 'category']

    def __str__(self):
        return f'{self.user.username} — {self.get_category_display()} ({self.cert_id})'

    def get_category_display(self):
        return self.CATEGORY_NAMES.get(self.category, self.category)

    def generate_pdf(self) -> str:
        """
        Генерирует PDF через WeasyPrint.
        Возвращает путь к файлу.
        """
        import os
        from django.template.loader import render_to_string
        from weasyprint import HTML

        context = {
            'username': self.user.username,
            'category_name': self.get_category_display(),
            'issued_at': self.issued_at.strftime('%d.%m.%Y'),
            'cert_id': str(self.cert_id),
            'verify_url': f'{settings.SITE_URL}/cert/{self.cert_id}',
        }

        html_content = render_to_string('certificate.html', context)

        # Путь для сохранения
        pdf_dir = os.path.join(settings.MEDIA_ROOT, 'certs')
        os.makedirs(pdf_dir, exist_ok=True)
        pdf_path = os.path.join(pdf_dir, f'{self.cert_id}.pdf')

        HTML(string=html_content).write_pdf(pdf_path)

        # Сохраняем URL
        self.pdf_url = f'/media/certs/{self.cert_id}.pdf'
        self.save(update_fields=['pdf_url'])

        return pdf_path
