"""
URL для дорожной карты.
"""
from django.urls import path
from . import roadmap_views

urlpatterns = [
    path('', roadmap_views.roadmap_view, name='roadmap'),
]
