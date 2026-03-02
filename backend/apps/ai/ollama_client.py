import json
import re
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class OllamaClient:

    SYSTEM_PROMPT = """Ты — опытный DevOps-инженер и ментор.
Всегда отвечай только на русском языке.
Будь краток и конкретен — максимум 3-4 абзаца.
Когда помогаешь с задачей — задавай наводящие вопросы, НЕ давай готовый ответ.
Используй примеры из реальной практики DevOps.
Если объясняешь ошибку — объясни причину и как её избежать в будущем."""

    FALLBACK_MESSAGES = {
        'hint': 'AI-ментор временно недоступен. Попробуй проверить документацию или man страницу команды.',
        'explain': 'AI-ментор временно недоступен. Обратись к официальной документации.',
        'interview': 'AI-оценка временно недоступна. Твой ответ сохранён.',
        'insight': 'Продолжай в том же темпе! Регулярная практика — ключ к успеху в DevOps.',
    }

    @property
    def base_url(self):
        return settings.OLLAMA_URL

    @property
    def model(self):
        return settings.OLLAMA_MODEL

    def generate(self, prompt: str, system: str = None, num_predict: int = 512, timeout: int = None) -> str:
        try:
            response = requests.post(
                f'{self.base_url}/api/generate',
                json={
                    'model': self.model,
                    'prompt': prompt,
                    'system': system or self.SYSTEM_PROMPT,
                    'stream': False,
                    'options': {
                        'temperature': 0.7,
                        'num_predict': num_predict,
                    },
                },
                timeout=timeout or getattr(settings, 'OLLAMA_TIMEOUT', 30),
            )
            response.raise_for_status()
            return response.json().get('response', '')

        except requests.exceptions.ConnectionError:
            logger.warning('Ollama unavailable (connection refused)')
            return ''
        except requests.exceptions.Timeout:
            logger.warning('Ollama timeout')
            return ''
        except Exception as e:
            logger.error(f'Ollama API error: {e}')
            return ''

    def generate_hint(self, task, terminal_output: str = '') -> str:
        prompt = f'Задача: {task.title_ru}\nОписание: {task.description_ru}\nКатегория: {task.category}'

        if terminal_output:
            prompt += f'\n\nЧто пользователь уже пробовал:\n{terminal_output[:500]}'

        prompt += '\n\nДай наводящий вопрос или подсказку направления. НЕ давай готовый ответ и не показывай команды.'

        return self.generate(prompt) or self.FALLBACK_MESSAGES['hint']

    def explain_error(self, command: str, error_output: str, task=None) -> str:
        prompt = f'Пользователь выполнил команду: {command}\n\nПолучил такой вывод/ошибку:\n{error_output[:500]}'

        if task:
            prompt += f'\n\nКонтекст задачи: {task.title_ru} (категория: {task.category})'

        prompt += '\n\nОбъясни что пошло не так, почему это происходит, и как исправить.'

        return self.generate(prompt) or self.FALLBACK_MESSAGES['explain']

    def explain_breakfix(self, task, what_was_broken: str = '') -> str:
        prompt = f'Задача Break & Fix: {task.title_ru}\n{task.description_ru}'

        if what_was_broken:
            prompt += f'\n\nЧто было сломано: {what_was_broken}'

        prompt += '\n\nПользователь успешно решил задачу. Теперь объясни:\n1. Что именно было сломано и почему\n2. Как такое случается в реальной практике\n3. Как предотвратить подобные проблемы'

        return self.generate(prompt) or 'Отличная работа! Ты нашёл и исправил проблему.'

    def evaluate_interview_answer(self, question: str, answer: str, sample_answer: str = '') -> dict:
        stripped = answer.strip()
        if len(stripped) < 30 or stripped.lower() in (
            'не знаю', 'незнаю', 'не знаю.', "i don't know", 'idk', 'хз', '?'
        ):
            return {
                'score': 1,
                'feedback': 'Ответ не предоставлен или слишком краткий. Постарайся развёрнуто объяснить тему.',
                'strengths': [],
                'improvements': ['Изучи тему и попробуй ответить развёрнуто'],
            }

        prompt = f'Вопрос для собеседования DevOps: {question}\n\nОтвет кандидата:\n{answer}'

        if sample_answer:
            prompt += f'\n\nЭталонный ответ (только для твоей оценки, НЕ показывай его):\n{sample_answer}'

        prompt += """

Оцени ответ строго и объективно по шкале 1-10.
Шкала: 1-3 неверно, 4-5 поверхностно, 6-7 частично верно, 8-10 полно и точно.
Если ответ бессмысленный или не по теме — ставь 1-2.

Верни ТОЛЬКО JSON (без пояснений до или после), заполни все поля на русском:
{"score": 7, "feedback": "Кандидат верно объяснил основное, но не упомянул детали реализации.", "strengths": ["Правильно названы основные понятия", "Понимание цели практики"], "improvements": ["Не хватает конкретных примеров инструментов", "Нет описания процесса настройки"]}"""

        try:
            response_text = self.generate(
                prompt,
                system=(
                    'Ты — строгий технический интервьюер DevOps. '
                    'Отвечай ТОЛЬКО на русском языке. '
                    'Возвращай ТОЛЬКО валидный JSON без дополнительного текста. '
                    'Никогда не используй английские слова в feedback, strengths, improvements.'
                ),
                num_predict=256,
                timeout=90,
            )
            if response_text:
                cleaned = re.sub(r'[\u4e00-\u9fff\u3000-\u303f]', '', response_text)
                json_match = re.search(r'\{[^{}]*"score"[^{}]*\}', cleaned, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    data['score'] = max(1.0, min(10.0, float(data.get('score', 5))))
                    return data
        except Exception as e:
            logger.error(f'Interview evaluation parse error: {e}')

        return {
            'score': 5.0,
            'feedback': self.FALLBACK_MESSAGES['interview'],
            'strengths': ['Ответ получен'],
            'improvements': ['AI-оценка временно недоступна'],
        }

    def explain_lesson_content(self, lesson_title: str, selected_text: str) -> str:
        prompt = f"""Урок: {lesson_title}

Пользователь хочет понять этот фрагмент:
{selected_text[:600]}

Объясни проще, с коротким практическим примером из реальной работы DevOps-инженера.
Максимум 3 абзаца. Только на русском языке."""
        return self.generate(prompt) or self.FALLBACK_MESSAGES['explain']

    def generate_quiz_question(self, topic: str, difficulty: str, existing_questions: list) -> dict:
        existing = ', '.join(existing_questions[:5]) if existing_questions else 'нет'
        prompt = f"""Тема: {topic}. Сложность: {difficulty}.
Уже есть вопросы: {existing}

Создай ОДИН новый вопрос по теме (не повторяй существующие).
Ответ строго в JSON без пояснений:
{{"text_ru":"Вопрос?","question_type":"single","answers":[{{"text_ru":"Вариант 1","is_correct":true}},{{"text_ru":"Вариант 2","is_correct":false}},{{"text_ru":"Вариант 3","is_correct":false}},{{"text_ru":"Вариант 4","is_correct":false}}],"explanation_ru":"Почему правильный ответ именно такой..."}}"""

        try:
            response_text = self.generate(
                prompt,
                system='Ты DevOps-преподаватель. Отвечай только на русском, строго в JSON.',
            )
            if response_text:
                cleaned = re.sub(r'[\u4e00-\u9fff]', '', response_text)
                json_match = re.search(r'\{.*"text_ru".*"answers".*\}', cleaned, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
        except Exception as e:
            logger.error(f'Quiz question generation error: {e}')
        return {}

    def generate_personal_insight(self, user_stats: dict) -> str:
        skills = user_stats.get('skills', {})
        weak_skills = [k for k, v in skills.items() if v.get('pct', 0) < 50]
        strong_skills = [k for k, v in skills.items() if v.get('pct', 0) >= 70]

        prompt = f"""Статистика пользователя:
- Уровень: {user_stats.get('level', 'beginner')}
- XP: {user_stats.get('xp', 0)}
- Стрик: {user_stats.get('streak', 0)} дней
- Задач выполнено на этой неделе: {user_stats.get('weekly_tasks', 0)}
- Слабые категории (< 50%): {', '.join(weak_skills) if weak_skills else 'нет'}
- Сильные категории (> 70%): {', '.join(strong_skills) if strong_skills else 'нет'}

Дай краткий персональный анализ (2-3 предложения): что хорошо, над чем работать, и конкретная рекомендация."""

        return self.generate(prompt) or self.FALLBACK_MESSAGES['insight']

    def generate_task(self, category: str, difficulty: str, task_type: str) -> dict:
        prompt = f"""Создай новую задачу для DevOps обучающей платформы.

Параметры:
- Категория: {category}
- Сложность: {difficulty}
- Тип: {task_type}

Ответь строго в JSON формате:
{{
  "title_ru": "Название задачи",
  "description_ru": "Подробное описание что нужно сделать",
  "hint_1_ru": "Направление без ответа",
  "hint_2_ru": "Более конкретная подсказка",
  "hint_3_ru": "Почти готовый ответ",
  "checker_type": "command_output",
  "checker_config": {{"command": "команда_проверки", "expected": "ожидаемый_вывод"}},
  "solution_steps": [
    {{"command": "команда", "explanation": "объяснение"}}
  ],
  "xp_reward": 150,
  "time_limit": 30
}}"""

        try:
            response_text = self.generate(prompt)
            if response_text:
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
        except Exception as e:
            logger.error(f'Task generation error: {e}')

        return {}
