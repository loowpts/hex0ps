"""
Сериализаторы для Cheat Sheets.
"""
from rest_framework import serializers
from .models import CheatSheet, CheatSheetEntry, UserCheatSheetBookmark, UserCheatSheetProgress


class CheatSheetEntrySerializer(serializers.ModelSerializer):
    learned = serializers.SerializerMethodField()

    class Meta:
        model = CheatSheetEntry
        fields = ['id', 'command', 'description_ru', 'example', 'order', 'learned']

    def get_learned(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return UserCheatSheetProgress.objects.filter(
            user=request.user, entry=obj, learned=True
        ).exists()


class CheatSheetListSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    is_bookmarked = serializers.SerializerMethodField()
    entries_count = serializers.SerializerMethodField()

    class Meta:
        model = CheatSheet
        fields = [
            'id', 'title_ru', 'category', 'category_display',
            'tags', 'order', 'is_bookmarked', 'entries_count',
        ]

    def get_is_bookmarked(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return UserCheatSheetBookmark.objects.filter(
            user=request.user, cheatsheet=obj
        ).exists()

    def get_entries_count(self, obj):
        return obj.entries.count()


class CheatSheetDetailSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    is_bookmarked = serializers.SerializerMethodField()
    entries = CheatSheetEntrySerializer(many=True, read_only=True)
    learned_count = serializers.SerializerMethodField()

    class Meta:
        model = CheatSheet
        fields = [
            'id', 'title_ru', 'category', 'category_display',
            'content_md', 'tags', 'order', 'is_bookmarked',
            'entries', 'learned_count',
        ]

    def get_is_bookmarked(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return UserCheatSheetBookmark.objects.filter(
            user=request.user, cheatsheet=obj
        ).exists()

    def get_learned_count(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return 0
        return UserCheatSheetProgress.objects.filter(
            user=request.user,
            entry__cheatsheet=obj,
            learned=True,
        ).count()
