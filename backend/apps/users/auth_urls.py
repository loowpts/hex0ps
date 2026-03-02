from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='auth-login'),
    path('refresh/', views.refresh_token_view, name='auth-refresh'),
]
