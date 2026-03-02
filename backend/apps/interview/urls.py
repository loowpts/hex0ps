from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.categories_view, name='interview-categories'),
    path('questions/', views.question_list_view, name='interview-question-list'),
    path('questions/<int:question_id>/', views.question_detail_view, name='interview-question-detail'),
    path('answer/', views.answer_view, name='interview-answer'),
    path('history/', views.history_view, name='interview-history'),
]
