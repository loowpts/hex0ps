from rest_framework import serializers
from .models import (
    Course, Module, Lesson, Quiz, QuizQuestion, QuizAnswer,
    QuizAttempt, UserCourseProgress, UserLessonProgress,
)


class QuizAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizAnswer
        fields = ['id', 'text_ru']
        # is_correct — НЕ включаем (чтобы не спойлить)


class QuizAnswerWithCorrectSerializer(serializers.ModelSerializer):
    """Используется ПОСЛЕ сдачи теста — показывает правильные ответы."""
    class Meta:
        model = QuizAnswer
        fields = ['id', 'text_ru', 'is_correct']


class QuizQuestionSerializer(serializers.ModelSerializer):
    answers = QuizAnswerSerializer(many=True)

    class Meta:
        model = QuizQuestion
        fields = ['id', 'text_ru', 'question_type', 'answers']


class QuizSerializer(serializers.ModelSerializer):
    questions = QuizQuestionSerializer(many=True)

    class Meta:
        model = Quiz
        fields = ['id', 'pass_threshold', 'questions']


class UserLessonProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLessonProgress
        fields = ['viewed', 'quiz_passed', 'lab_done', 'completed', 'completed_at']


class LessonSerializer(serializers.ModelSerializer):
    user_progress = serializers.SerializerMethodField()
    lesson_type_display = serializers.CharField(source='get_lesson_type_display', read_only=True)

    class Meta:
        model = Lesson
        fields = [
            'id', 'title_ru', 'lesson_type', 'lesson_type_display',
            'order', 'xp_reward', 'user_progress',
        ]

    def get_user_progress(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        prog = obj.user_progress.filter(user=request.user).first()
        return UserLessonProgressSerializer(prog).data if prog else None


class LessonDetailSerializer(LessonSerializer):
    """Детали урока — включает контент и квиз."""
    quiz = QuizSerializer(read_only=True)
    task_id = serializers.IntegerField(source='task.id', read_only=True, allow_null=True)

    class Meta(LessonSerializer.Meta):
        fields = LessonSerializer.Meta.fields + ['content_md', 'quiz', 'task_id']


class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True)
    completed_lessons = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = ['id', 'title_ru', 'order', 'lessons', 'completed_lessons']

    def get_completed_lessons(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return 0
        return UserLessonProgress.objects.filter(
            user=request.user,
            lesson__module=obj,
            completed=True,
        ).count()


class UserCourseProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCourseProgress
        fields = ['status', 'started_at', 'completed_at', 'xp_earned']


class CourseListSerializer(serializers.ModelSerializer):
    user_progress = serializers.SerializerMethodField()
    difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)
    total_lessons = serializers.SerializerMethodField()
    completed_lessons = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'slug', 'title_ru', 'description_ru', 'icon',
            'difficulty', 'difficulty_display', 'category',
            'estimated_hours', 'xp_reward', 'order',
            'total_lessons', 'completed_lessons', 'user_progress',
        ]

    def get_user_progress(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        prog = obj.user_progress.filter(user=request.user).first()
        return UserCourseProgressSerializer(prog).data if prog else None

    def get_total_lessons(self, obj):
        return Lesson.objects.filter(module__course=obj).count()

    def get_completed_lessons(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return 0
        return UserLessonProgress.objects.filter(
            user=request.user,
            lesson__module__course=obj,
            completed=True,
        ).count()


class CourseDetailSerializer(CourseListSerializer):
    modules = ModuleSerializer(many=True)
    prerequisites_info = serializers.SerializerMethodField()

    class Meta(CourseListSerializer.Meta):
        fields = CourseListSerializer.Meta.fields + ['modules', 'prerequisites_info']

    def get_prerequisites_info(self, obj):
        request = self.context.get('request')
        result = []
        for pre in obj.prerequisites.all():
            completed = False
            if request and request.user.is_authenticated:
                completed = obj.user_progress.filter(
                    user=request.user,
                    course=pre,
                    status=UserCourseProgress.STATUS_COMPLETED,
                ).exists()
            result.append({'id': pre.id, 'slug': pre.slug, 'title_ru': pre.title_ru, 'completed': completed})
        return result


class QuizAttemptResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizAttempt
        fields = ['id', 'score', 'passed', 'xp_earned', 'created_at']
