"""
URL маршруты для профилей пользователей.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('me/', views.me_view, name='user-me'),
    path('me/settings/', views.me_settings_view, name='user-settings'),
    path('<str:username>/', views.public_profile_view, name='user-public-profile'),
]
