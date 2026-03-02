from django.urls import path
from . import views

urlpatterns = [
    # Courses
    path('', views.course_list_view, name='course-list'),
    path('skill-tree/', views.skill_tree_view, name='skill-tree'),
    path('<slug:slug>/', views.course_detail_view, name='course-detail'),
    path('<slug:slug>/enroll/', views.course_enroll_view, name='course-enroll'),
    path('<slug:slug>/progress/', views.course_progress_view, name='course-progress'),

    # Lessons
    path('lessons/<int:lesson_id>/', views.lesson_detail_view, name='lesson-detail'),
    path('lessons/<int:lesson_id>/complete/', views.lesson_complete_view, name='lesson-complete'),

    # Quiz
    path('quiz/<int:quiz_id>/submit/', views.quiz_submit_view, name='quiz-submit'),
    path('quiz/<int:quiz_id>/attempts/', views.quiz_attempts_view, name='quiz-attempts'),
]
