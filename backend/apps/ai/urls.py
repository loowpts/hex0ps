from django.urls import path
from . import views

urlpatterns = [
    path('ask/', views.ai_ask_view, name='ai-ask'),
    path('hint/', views.ai_hint_view, name='ai-hint'),
    path('explain/', views.ai_explain_view, name='ai-explain'),
    path('explain-lesson/', views.ai_explain_lesson_view, name='ai-explain-lesson'),
    path('generate-task/', views.ai_generate_task_view, name='ai-generate-task'),
]
