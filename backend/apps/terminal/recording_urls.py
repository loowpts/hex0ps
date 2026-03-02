"""
URL маршруты для записей сессий.
"""
from django.urls import path
from . import recording_views

urlpatterns = [
    path('<uuid:share_id>/', recording_views.recording_detail_view, name='recording-detail'),
    path('<uuid:share_id>/share/', recording_views.recording_share_view, name='recording-share'),
    path('<uuid:share_id>/delete/', recording_views.recording_delete_view, name='recording-delete'),
]
