from django.urls import path
from . import views

urlpatterns = [
    path('', views.note_list_view, name='note-list'),
    path('export/', views.note_export_view, name='note-export'),
    path('<int:task_id>/', views.note_detail_view, name='note-detail'),
    path('<int:task_id>/upsert/', views.note_upsert_view, name='note-upsert'),
    path('<int:task_id>/delete/', views.note_delete_view, name='note-delete'),
]
