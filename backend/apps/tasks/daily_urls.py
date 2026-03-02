"""
URL маршруты для Daily Challenge.
"""
from django.urls import path
from . import daily_views

urlpatterns = [
    path('', daily_views.daily_challenge_view, name='daily-challenge'),
    path('start/', daily_views.daily_challenge_start_view, name='daily-start'),
    path('complete/', daily_views.daily_challenge_complete_view, name='daily-complete'),
]
