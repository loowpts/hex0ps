from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import User


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username', '')
        password = data.get('password', '')

        user = authenticate(request=self.context.get('request'), username=username, password=password)

        if not user:
            raise serializers.ValidationError('Неверный никнейм или пароль.')
        if not user.is_active:
            raise serializers.ValidationError('Аккаунт деактивирован.')

        data['user'] = user
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    xp_to_next_level = serializers.SerializerMethodField()
    level_progress_pct = serializers.SerializerMethodField()
    level_display = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'level', 'level_display',
            'xp', 'xp_to_next_level', 'level_progress_pct',
            'streak', 'max_streak', 'is_public', 'onboarding_done',
            'avatar_url', 'bio', 'last_active', 'created_at',
        ]
        read_only_fields = ['id', 'level', 'xp', 'streak', 'max_streak', 'created_at']

    def get_xp_to_next_level(self, obj):
        return obj.xp_to_next_level

    def get_level_progress_pct(self, obj):
        return obj.level_progress_pct

    def get_level_display(self, obj):
        return obj.level_display


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'bio', 'avatar_url']

    def validate_username(self, value):
        user = self.context['request'].user
        if User.objects.filter(username__iexact=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError('Это имя пользователя уже занято.')
        if len(value) < 3:
            raise serializers.ValidationError('Имя пользователя должно содержать не менее 3 символов.')
        return value


class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['is_public', 'onboarding_done']


class PublicProfileSerializer(serializers.ModelSerializer):
    level_display = serializers.SerializerMethodField()
    member_since = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = User
        fields = [
            'username', 'level', 'level_display', 'xp',
            'streak', 'max_streak', 'avatar_url', 'bio', 'member_since',
        ]

    def get_level_display(self, obj):
        return obj.level_display
