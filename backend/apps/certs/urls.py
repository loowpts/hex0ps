from django.urls import path
from . import views

urlpatterns = [
    path('', views.cert_list_view, name='cert-list'),
    path('<uuid:cert_id>/', views.cert_verify_view, name='cert-verify'),
    path('<uuid:cert_id>/download/', views.cert_download_view, name='cert-download'),
]
