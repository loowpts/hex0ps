from django.urls import path
from . import views

urlpatterns = [
    path('me/', views.analytics_me_view, name='analytics-me'),
    path('export/pdf/', views.analytics_export_pdf_view, name='analytics-export-pdf'),
]
