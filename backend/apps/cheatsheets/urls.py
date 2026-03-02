"""
URL маршруты для Cheat Sheets.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.cheatsheet_list_view, name='cheatsheet-list'),
    path('<int:pk>/', views.cheatsheet_detail_view, name='cheatsheet-detail'),
    path('<int:pk>/bookmark/', views.cheatsheet_bookmark_view, name='cheatsheet-bookmark'),
    path('entry/<int:entry_id>/learned/', views.cheatsheet_entry_learned_view, name='cheatsheet-entry-learned'),
]
