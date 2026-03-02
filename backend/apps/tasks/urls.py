"""
URL маршруты для задач.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.task_list_view, name='task-list'),
    path('<int:task_id>/', views.task_detail_view, name='task-detail'),
    path('<int:task_id>/start/', views.task_start_view, name='task-start'),
    path('<int:task_id>/check/', views.task_check_view, name='task-check'),
    path('<int:task_id>/hint/', views.task_hint_view, name='task-hint'),
    path('<int:task_id>/replay/', views.task_replay_view, name='task-replay'),
]
