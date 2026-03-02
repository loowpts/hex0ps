"""
Сериализаторы для задач.
"""
from rest_framework import serializers
from .models import Task, UserTask


class TaskListSerializer(serializers.ModelSerializer):
    """
    Краткая карточка задачи для списка.
    Подсказки НЕ включаются — только через /hint/.
    """

    category_display = serializers.CharField(read_only=True)
    difficulty_display = serializers.CharField(read_only=True)
    user_status = serializers.SerializerMethodField()
    is_locked = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'title_ru', 'category', 'category_display',
            'difficulty', 'difficulty_display', 'task_type',
            'xp_reward', 'time_limit', 'is_active', 'order',
            'user_status', 'is_locked',
        ]

    def get_user_status(self, obj):
        """Статус задачи для текущего пользователя.

        Использует кешированный словарь из context['user_task_statuses']
        чтобы избежать N+1 запросов при сериализации списка задач.
        Context заполняется один раз в task_list_view.
        """
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None

        cached = self.context.get('user_task_statuses')
        if cached is not None:
            return cached.get(obj.id, 'not_started')

        # Fallback: serializer вызван без предзаполненного context
        try:
            ut = obj.user_tasks.get(user=request.user)
            return ut.status
        except UserTask.DoesNotExist:
            return 'not_started'

    def get_is_locked(self, obj):
        """Заблокирована ли задача (не выполнены предпосылки).

        Использует кешированный set из context['completed_ids']
        чтобы избежать N+1 запросов при сериализации списка задач.
        Context заполняется один раз в task_list_view.
        """
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False

        prerequisites = obj.prerequisites.all()
        if not prerequisites.exists():
            return False

        completed_ids = self.context.get('completed_ids')
        if completed_ids is None:
            # Fallback: serializer вызван без предзаполненного context
            completed_ids = set(
                UserTask.objects.filter(
                    user=request.user,
                    status='completed'
                ).values_list('task_id', flat=True)
            )

        return not all(p.id in completed_ids for p in prerequisites)


class TaskDetailSerializer(serializers.ModelSerializer):
    """
    Детальная информация о задаче.
    Включает статус пользователя, но НЕ включает подсказки.
    """

    category_display = serializers.CharField(read_only=True)
    difficulty_display = serializers.CharField(read_only=True)
    user_task = serializers.SerializerMethodField()
    prerequisites_info = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'title_ru', 'description_ru',
            'category', 'category_display',
            'difficulty', 'difficulty_display',
            'task_type', 'xp_reward', 'time_limit',
            'docker_image', 'checker_type',
            'order', 'prerequisites_info',
            'user_task',
        ]

    def get_user_task(self, obj):
        """UserTask текущего пользователя если есть."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        try:
            ut = obj.user_tasks.get(user=request.user)
            return UserTaskSerializer(ut).data
        except UserTask.DoesNotExist:
            return None

    def get_prerequisites_info(self, obj):
        """Информация о задачах-предпосылках."""
        return [
            {'id': p.id, 'title_ru': p.title_ru}
            for p in obj.prerequisites.all()
        ]


class UserTaskSerializer(serializers.ModelSerializer):
    """Прогресс пользователя по задаче."""

    class Meta:
        model = UserTask
        fields = [
            'id', 'status', 'attempts', 'hints_used',
            'xp_earned', 'xp_multiplier',
            'started_at', 'completed_at', 'time_spent',
        ]
        read_only_fields = fields
