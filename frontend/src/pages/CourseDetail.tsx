import { useParams, Link, useNavigate } from 'react-router-dom'
import { useCourse, useEnrollCourse } from '@/api/hooks/useCourses'
import type { Module, LessonListItem } from '@/types'

const LESSON_ICONS: Record<string, string> = {
  theory: '📖',
  quiz:   '✏️',
  lab:    '🖥️',
  exam:   '🎓',
}

const DIFF_STYLES: Record<string, string> = {
  beginner:     'text-[#00e676] border-[#00e676]/40',
  intermediate: 'text-[#ff9500] border-[#ff9500]/40',
  advanced:     'text-red-400 border-red-400/40',
}

function LessonRow({ lesson, courseSlug, moduleIndex, lessonIndex }:
  { lesson: LessonListItem; courseSlug: string; moduleIndex: number; lessonIndex: number }) {
  const p = lesson.user_progress
  const completed = p?.completed ?? false

  return (
    <Link
      to={`/courses/${courseSlug}/learn?lesson=${lesson.id}`}
      className="flex items-center gap-4 p-4 rounded-xl bg-[#0a0e17] border border-[#1e2d45] hover:border-[#00d4ff]/40 transition-colors group"
    >
      <div className={`w-8 h-8 rounded-lg flex items-center justify-center text-sm shrink-0 ${
        completed ? 'bg-[#00e676]/10 border border-[#00e676]/30' : 'bg-[#1e2d45]'
      }`}>
        {completed ? '✓' : `${moduleIndex}.${lessonIndex}`}
      </div>
      <div className="flex-1 min-w-0">
        <p className={`text-sm font-medium transition-colors ${completed ? 'text-[#8899aa]' : 'text-[#e2e8f0] group-hover:text-[#00d4ff]'}`}>
          {LESSON_ICONS[lesson.lesson_type]} {lesson.title_ru}
        </p>
        <p className="text-xs text-[#4a5568] capitalize">{lesson.lesson_type_display}</p>
      </div>
      <span className="text-xs font-semibold text-[#00e676] shrink-0">+{lesson.xp_reward} XP</span>
    </Link>
  )
}

function ModuleSection({ module: mod, courseSlug, index }:
  { module: Module; courseSlug: string; index: number }) {
  const total = mod.lessons.length
  const completed = mod.completed_lessons

  return (
    <div className="bg-[#0f1520] border border-[#1e2d45] rounded-2xl overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b border-[#1e2d45]">
        <div>
          <h3 className="text-[#e2e8f0] font-semibold">{index}. {mod.title_ru}</h3>
          <p className="text-xs text-[#8899aa] mt-0.5">{completed}/{total} уроков выполнено</p>
        </div>
        {completed === total && total > 0 && (
          <span className="text-xs px-2 py-0.5 rounded-md bg-[#00e676]/10 text-[#00e676]">Пройден ✓</span>
        )}
      </div>
      <div className="p-4 space-y-2">
        {mod.lessons.map((lesson, li) => (
          <LessonRow
            key={lesson.id}
            lesson={lesson}
            courseSlug={courseSlug}
            moduleIndex={index}
            lessonIndex={li + 1}
          />
        ))}
      </div>
    </div>
  )
}

export default function CourseDetail() {
  const { slug } = useParams<{ slug: string }>()
  const navigate = useNavigate()
  const { data: course, isLoading } = useCourse(slug ?? '')
  const enroll = useEnrollCourse()

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#0a0e17] p-6 max-w-5xl mx-auto space-y-4">
        <div className="h-48 bg-[#1e2d45]/30 rounded-2xl animate-pulse" />
        <div className="h-64 bg-[#1e2d45]/30 rounded-2xl animate-pulse" />
      </div>
    )
  }

  if (!course) {
    return (
      <div className="min-h-screen bg-[#0a0e17] flex items-center justify-center">
        <p className="text-[#8899aa]">Курс не найден</p>
      </div>
    )
  }

  const progress = course.user_progress
  const isEnrolled = !!progress
  const isCompleted = progress?.status === 'completed'
  const totalLessons = course.total_lessons
  const completedLessons = course.completed_lessons
  const pct = totalLessons > 0 ? Math.round((completedLessons / totalLessons) * 100) : 0

  const handleStart = async () => {
    if (!isEnrolled) {
      await enroll.mutateAsync(course.slug)
    }
    // Найти первый незавершённый урок
    for (const mod of course.modules) {
      for (const lesson of mod.lessons) {
        if (!lesson.user_progress?.completed) {
          navigate(`/courses/${course.slug}/learn?lesson=${lesson.id}`)
          return
        }
      }
    }
    // Все пройдены — открыть первый
    const first = course.modules[0]?.lessons[0]
    if (first) navigate(`/courses/${course.slug}/learn?lesson=${first.id}`)
  }

  return (
    <div className="min-h-screen bg-[#0a0e17] p-6 max-w-5xl mx-auto">
      <Link to="/courses" className="flex items-center gap-2 text-[#8899aa] hover:text-[#e2e8f0] transition-colors text-sm mb-6">
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
        Все курсы
      </Link>

      {/* Header */}
      <div className="bg-[#0f1520] border border-[#1e2d45] rounded-2xl p-6 mb-6">
        <div className="flex items-start gap-5">
          <div className="text-5xl shrink-0">{course.icon}</div>
          <div className="flex-1">
            <div className="flex flex-wrap items-center gap-3 mb-2">
              <h1 className="text-2xl font-bold text-[#e2e8f0]">{course.title_ru}</h1>
              <span className={`text-xs px-2.5 py-1 rounded-lg border font-medium ${DIFF_STYLES[course.difficulty]}`}>
                {course.difficulty_display}
              </span>
            </div>
            <p className="text-[#8899aa] mb-4">{course.description_ru}</p>
            <div className="flex flex-wrap gap-4 text-sm text-[#8899aa]">
              <span>⏱ {course.estimated_hours} часов</span>
              <span>📚 {totalLessons} уроков</span>
              <span className="text-[#00e676] font-medium">+{course.xp_reward} XP</span>
            </div>
          </div>
        </div>

        {/* Prerequisites */}
        {course.prerequisites_info.length > 0 && (
          <div className="mt-4 p-3 bg-[#0a0e17] rounded-xl border border-[#1e2d45]">
            <p className="text-xs text-[#8899aa] mb-2">Необходимые курсы:</p>
            <div className="flex flex-wrap gap-2">
              {course.prerequisites_info.map(pre => (
                <Link
                  key={pre.id}
                  to={`/courses/${pre.slug}`}
                  className={`text-xs px-2.5 py-1 rounded-lg border ${
                    pre.completed
                      ? 'border-[#00e676]/40 text-[#00e676]'
                      : 'border-[#ff9500]/40 text-[#ff9500]'
                  }`}
                >
                  {pre.completed ? '✓ ' : '○ '}{pre.title_ru}
                </Link>
              ))}
            </div>
          </div>
        )}

        {/* Progress */}
        {isEnrolled && (
          <div className="mt-4">
            <div className="flex justify-between text-xs text-[#8899aa] mb-1">
              <span>{completedLessons}/{totalLessons} уроков</span>
              <span>{pct}%</span>
            </div>
            <div className="h-2 bg-[#1e2d45] rounded-full overflow-hidden">
              <div
                className="h-full rounded-full bg-gradient-to-r from-[#00d4ff] to-[#00e676] transition-all duration-700"
                style={{ width: `${pct}%` }}
              />
            </div>
          </div>
        )}

        <button
          onClick={handleStart}
          disabled={enroll.isPending}
          className="mt-4 px-6 py-2.5 rounded-xl font-semibold text-[#0a0e17] bg-[#00d4ff] hover:bg-[#00bfe8] disabled:opacity-50 transition-colors"
        >
          {isCompleted ? 'Повторить' : isEnrolled ? 'Продолжить' : 'Начать курс'}
        </button>
      </div>

      {/* Modules */}
      <div className="space-y-4">
        {course.modules.map((mod, i) => (
          <ModuleSection
            key={mod.id}
            module={mod}
            courseSlug={course.slug}
            index={i + 1}
          />
        ))}
      </div>
    </div>
  )
}
