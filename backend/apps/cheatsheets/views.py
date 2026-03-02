"""
Views для Cheat Sheets.
"""
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import CheatSheet, CheatSheetEntry, UserCheatSheetBookmark, UserCheatSheetProgress
from .serializers import CheatSheetListSerializer, CheatSheetDetailSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cheatsheet_list_view(request):
    """
    Список шпаргалок с фильтрацией и поиском.
    GET /api/cheatsheets/?category=linux&q=nginx&bookmarked=1
    """
    qs = CheatSheet.objects.filter(is_active=True).prefetch_related('entries')

    # Фильтр по категории
    category = request.query_params.get('category')
    if category:
        qs = qs.filter(category=category)

    # Поиск
    q = request.query_params.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(title_ru__icontains=q) |
            Q(tags__icontains=q) |
            Q(entries__command__icontains=q) |
            Q(entries__description_ru__icontains=q)
        ).distinct()

    # Только закладки
    bookmarked = request.query_params.get('bookmarked')
    if bookmarked:
        qs = qs.filter(bookmarks__user=request.user)

    serializer = CheatSheetListSerializer(qs, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cheatsheet_detail_view(request, pk):
    """Детальная информация о шпаргалке с командами."""
    try:
        cheatsheet = CheatSheet.objects.prefetch_related('entries').get(pk=pk, is_active=True)
    except CheatSheet.DoesNotExist:
        return Response({'error': 'Шпаргалка не найдена.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = CheatSheetDetailSerializer(cheatsheet, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cheatsheet_bookmark_view(request, pk):
    """
    Добавить/убрать закладку на шпаргалку (toggle).
    POST /api/cheatsheets/<pk>/bookmark/
    """
    try:
        cheatsheet = CheatSheet.objects.get(pk=pk, is_active=True)
    except CheatSheet.DoesNotExist:
        return Response({'error': 'Шпаргалка не найдена.'}, status=status.HTTP_404_NOT_FOUND)

    bookmark, created = UserCheatSheetBookmark.objects.get_or_create(
        user=request.user, cheatsheet=cheatsheet
    )

    if not created:
        bookmark.delete()
        return Response({'bookmarked': False})

    return Response({'bookmarked': True}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cheatsheet_entry_learned_view(request, entry_id):
    """
    Отметить команду как 'запомнил' (toggle).
    POST /api/cheatsheets/entry/<entry_id>/learned/
    """
    try:
        entry = CheatSheetEntry.objects.get(pk=entry_id)
    except CheatSheetEntry.DoesNotExist:
        return Response({'error': 'Команда не найдена.'}, status=status.HTTP_404_NOT_FOUND)

    progress, created = UserCheatSheetProgress.objects.get_or_create(
        user=request.user, entry=entry
    )

    if created:
        # Первый раз — сразу learned=True
        progress.learned = True
        progress.save()
    else:
        # Toggle
        progress.learned = not progress.learned
        progress.save()

    return Response({'learned': progress.learned})
