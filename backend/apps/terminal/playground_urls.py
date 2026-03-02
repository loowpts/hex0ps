"""
URL маршруты для Playground.
"""
from django.urls import path
from . import playground_views

urlpatterns = [
    path('environments/', playground_views.playground_environments_view, name='playground-environments'),
    path('start/', playground_views.playground_start_view, name='playground-start'),
    path('<int:session_id>/stop/', playground_views.playground_stop_view, name='playground-stop'),
]
