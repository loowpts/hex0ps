import { useState, useEffect } from 'react'
import { useParams, useSearchParams, Link } from 'react-router-dom'
import { useCourse, useLesson, useLessonComplete, useQuizSubmit, useExplainLesson } from '@/api/hooks/useCourses'
import type { LessonDetail, QuizSubmitResult } from '@/types'
import ReactMarkdown from 'react-markdown'

// ─── LessonViewer (теория) ────────────────────────────────────────────────────

function LessonViewer({ lesson }: { lesson: LessonDetail }) {
  const complete = useLessonComplete()
  const explainMutation = useExplainLesson()
  const [selectedText, setSelectedText] = useState('')
  const [explanation, setExplanation] = useState('')
  const [showExplain, setShowExplain] = useState(false)

  const handleMouseUp = () => {
    const sel = window.getSelection()?.toString().trim()
    if (sel && sel.length > 10) setSelectedText(sel)
    else setSelectedText('')
  }

  const handleExplain = async () => {
    if (!selectedText) return
    setShowExplain(true)
    setExplanation('')
    try {
      const result = await explainMutation.mutateAsync({
        lessonTitle: lesson.title_ru,
        selectedText,
      })
      setExplanation(result.explanation)
    } catch {
      setExplanation('AI-объяснение временно недоступно.')
    }
  }

  return (
    <div className="flex gap-6 h-full">
      {/* Контент */}
      <div className="flex-1 min-w-0">
        <div
          className="prose prose-invert prose-sm max-w-none text-[#c8d6e8] select-text"
          onMouseUp={handleMouseUp}
        >
          <ReactMarkdown
            components={{
              h2: ({ children }) => <h2 className="text-[#e2e8f0] text-xl font-semibold mt-6 mb-3">{children}</h2>,
              h3: ({ children }) => <h3 className="text-[#e2e8f0] text-base font-semibold mt-4 mb-2">{children}</h3>,
              code: ({ children, className }) => {
                const isBlock = className?.includes('language-')
                return isBlock
                  ? <code className="block bg-[#0a0e17] border border-[#1e2d45] rounded-lg p-4 text-[#00e676] text-sm font-mono whitespace-pre overflow-x-auto">{children}</code>
                  : <code className="bg-[#1e2d45] text-[#00d4ff] px-1.5 py-0.5 rounded text-sm font-mono">{children}</code>
              },
              table: ({ children }) => <div className="overflow-x-auto"><table className="w-full text-sm border-collapse">{children}</table></div>,
              th: ({ children }) => <th className="text-left p-2 border border-[#1e2d45] text-[#e2e8f0] bg-[#1e2d45]/50">{children}</th>,
              td: ({ children }) => <td className="p-2 border border-[#1e2d45] text-[#8899aa]">{children}</td>,
              p: ({ children }) => <p className="text-[#8899aa] leading-relaxed mb-3">{children}</p>,
              li: ({ children }) => <li className="text-[#8899aa] mb-1">{children}</li>,
            }}
          >
            {lesson.content_md}
          </ReactMarkdown>
        </div>

        {/* Кнопка "Объясни" при выделении */}
        {selectedText && !showExplain && (
          <div className="mt-4 p-3 bg-[#00d4ff]/5 border border-[#00d4ff]/20 rounded-xl">
            <p className="text-[#8899aa] text-sm mb-2">Выделено: «{selectedText.slice(0, 60)}...»</p>
            <button
              onClick={handleExplain}
              className="px-4 py-1.5 rounded-lg text-sm font-medium bg-[#00d4ff]/10 text-[#00d4ff] border border-[#00d4ff]/30 hover:bg-[#00d4ff]/20 transition-colors"
            >
              Объяснить AI
            </button>
          </div>
        )}

        {/* AI объяснение */}
        {showExplain && (
          <div className="mt-4 p-4 bg-[#00d4ff]/5 border border-[#00d4ff]/20 rounded-xl">
            <div className="flex items-center justify-between mb-2">
              <p className="text-[#00d4ff] text-sm font-medium">AI-объяснение</p>
              <button onClick={() => { setShowExplain(false); setSelectedText('') }} className="text-[#8899aa] hover:text-[#e2e8f0] text-xs">✕</button>
            </div>
            {explainMutation.isPending ? (
              <div className="space-y-2">
                {[1, 2, 3].map(i => <div key={i} className="h-4 bg-[#1e2d45] rounded animate-pulse" />)}
              </div>
            ) : (
              <p className="text-[#8899aa] text-sm leading-relaxed">{explanation}</p>
            )}
          </div>
        )}

        {/* Кнопка завершить */}
        {!lesson.user_progress?.completed && (
          <button
            onClick={() => complete.mutate(lesson.id)}
            disabled={complete.isPending}
            className="mt-6 w-full py-3 rounded-xl font-semibold text-[#0a0e17] bg-[#00d4ff] hover:bg-[#00bfe8] disabled:opacity-50 transition-colors"
          >
            {complete.isPending ? 'Сохраняем...' : 'Отметить как прочитанное →'}
          </button>
        )}
        {lesson.user_progress?.completed && (
          <div className="mt-6 py-3 rounded-xl text-center text-[#00e676] border border-[#00e676]/30 bg-[#00e676]/5 text-sm font-medium">
            ✓ Урок завершён
          </div>
        )}
      </div>
    </div>
  )
}

// ─── QuizPlayer ───────────────────────────────────────────────────────────────

function QuizPlayer({ lesson }: { lesson: LessonDetail }) {
  const quiz = lesson.quiz!
  const submit = useQuizSubmit()
  const [selected, setSelected] = useState<Record<number, Set<number>>>({})
  const [result, setResult] = useState<QuizSubmitResult | null>(null)

  const toggle = (qId: number, aId: number, isMulti: boolean) => {
    setSelected(prev => {
      const current = new Set(prev[qId] ?? [])
      if (isMulti) {
        current.has(aId) ? current.delete(aId) : current.add(aId)
      } else {
        current.clear()
        current.add(aId)
      }
      return { ...prev, [qId]: current }
    })
  }

  const handleSubmit = async () => {
    const answers: Record<string, number[]> = {}
    for (const [qId, aIds] of Object.entries(selected)) {
      answers[qId] = Array.from(aIds)
    }
    const res = await submit.mutateAsync({ quizId: quiz.id, answers })
    setResult(res)
  }

  const allAnswered = quiz.questions.every(q => (selected[q.id]?.size ?? 0) > 0)

  if (result) {
    return (
      <div className="space-y-6">
        {/* Итог */}
        <div className={`p-5 rounded-2xl border ${result.passed ? 'bg-[#00e676]/5 border-[#00e676]/30' : 'bg-red-500/5 border-red-500/30'}`}>
          <p className={`text-2xl font-bold mb-1 ${result.passed ? 'text-[#00e676]' : 'text-red-400'}`}>
            {result.score}% {result.passed ? '— Зачёт!' : '— Не сдан'}
          </p>
          <p className="text-[#8899aa] text-sm">
            {result.correct_count} из {result.total} правильных.
            {result.xp_earned > 0 && ` +${result.xp_earned} XP`}
          </p>
          {!result.passed && (
            <p className="text-[#8899aa] text-xs mt-1">Нужно {result.pass_threshold}% для зачёта. Попробуй ещё раз.</p>
          )}
        </div>

        {/* Разбор ответов */}
        <div className="space-y-4">
          {result.results.map(r => (
            <div
              key={r.question_id}
              className={`p-4 rounded-xl border ${r.is_correct ? 'border-[#00e676]/20 bg-[#00e676]/5' : 'border-red-500/20 bg-red-500/5'}`}
            >
              <p className="text-[#e2e8f0] text-sm font-medium mb-3">{r.question_text}</p>
              <div className="space-y-1.5 mb-3">
                {r.answers.map(a => (
                  <div
                    key={a.id}
                    className={`flex items-center gap-2 text-sm px-3 py-2 rounded-lg ${
                      a.is_correct ? 'bg-[#00e676]/10 text-[#00e676]' :
                      r.selected_ids.includes(a.id) ? 'bg-red-500/10 text-red-400' :
                      'text-[#8899aa]'
                    }`}
                  >
                    <span>{a.is_correct ? '✓' : r.selected_ids.includes(a.id) ? '✗' : '○'}</span>
                    {a.text_ru}
                  </div>
                ))}
              </div>
              {r.explanation_ru && (
                <p className="text-[#8899aa] text-xs">{r.explanation_ru}</p>
              )}
            </div>
          ))}
        </div>

        {!result.passed && (
          <button
            onClick={() => { setResult(null); setSelected({}) }}
            className="w-full py-3 rounded-xl font-semibold border border-[#1e2d45] text-[#8899aa] hover:border-[#00d4ff]/40 hover:text-[#00d4ff] transition-colors"
          >
            Пройти снова
          </button>
        )}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <p className="text-[#8899aa] text-sm">Порог сдачи: {quiz.pass_threshold}%</p>
      {quiz.questions.map((q, qi) => (
        <div key={q.id} className="bg-[#0a0e17] border border-[#1e2d45] rounded-xl p-4">
          <p className="text-[#e2e8f0] text-sm font-medium mb-3">{qi + 1}. {q.text_ru}</p>
          <p className="text-[#4a5568] text-xs mb-3">{q.question_type === 'multi' ? 'Выберите все верные' : 'Выберите один'}</p>
          <div className="space-y-2">
            {q.answers.map(a => {
              const isSelected = selected[q.id]?.has(a.id) ?? false
              return (
                <button
                  key={a.id}
                  onClick={() => toggle(q.id, a.id, q.question_type === 'multi')}
                  className={`w-full text-left px-3 py-2 rounded-lg text-sm border transition-colors ${
                    isSelected
                      ? 'border-[#00d4ff]/40 bg-[#00d4ff]/10 text-[#00d4ff]'
                      : 'border-[#1e2d45] text-[#8899aa] hover:border-[#00d4ff]/30'
                  }`}
                >
                  <span className="mr-2">{isSelected ? (q.question_type === 'multi' ? '☑' : '◉') : (q.question_type === 'multi' ? '☐' : '○')}</span>
                  {a.text_ru}
                </button>
              )
            })}
          </div>
        </div>
      ))}

      <button
        onClick={handleSubmit}
        disabled={!allAnswered || submit.isPending}
        className="w-full py-3 rounded-xl font-semibold text-[#0a0e17] bg-[#00d4ff] hover:bg-[#00bfe8] disabled:opacity-50 transition-colors"
      >
        {submit.isPending ? 'Проверяем...' : 'Сдать тест'}
      </button>
    </div>
  )
}

// ─── LabLesson ────────────────────────────────────────────────────────────────

function LabLesson({ lesson }: { lesson: LessonDetail }) {
  return (
    <div className="space-y-4">
      <div className="p-4 bg-[#ff9500]/5 border border-[#ff9500]/20 rounded-xl">
        <p className="text-[#ff9500] font-medium mb-1">🖥️ Лабораторная работа</p>
        <p className="text-[#8899aa] text-sm">
          Эта лабораторная связана с практической задачей. Выполни её в терминале.
        </p>
      </div>
      {lesson.task_id && (
        <Link
          to={`/tasks/${lesson.task_id}`}
          className="block w-full py-3 rounded-xl font-semibold text-center text-[#0a0e17] bg-[#ff9500] hover:bg-[#e68900] transition-colors"
        >
          Открыть задачу →
        </Link>
      )}
      {lesson.user_progress?.lab_done && (
        <div className="py-3 rounded-xl text-center text-[#00e676] border border-[#00e676]/30 bg-[#00e676]/5 text-sm font-medium">
          ✓ Лабораторная выполнена
        </div>
      )}
    </div>
  )
}

// ─── Sidebar навигации ────────────────────────────────────────────────────────

function LessonNav({ course, currentLessonId, onSelect }:
  { course: NonNullable<ReturnType<typeof useCourse>['data']>; currentLessonId: number; onSelect: (id: number) => void }) {
  return (
    <div className="w-72 shrink-0 bg-[#0f1520] border border-[#1e2d45] rounded-2xl overflow-hidden h-fit sticky top-6">
      <div className="p-4 border-b border-[#1e2d45]">
        <p className="text-[#e2e8f0] font-semibold text-sm truncate">{course.title_ru}</p>
        <p className="text-xs text-[#8899aa] mt-0.5">{course.completed_lessons}/{course.total_lessons} уроков</p>
      </div>
      <div className="overflow-y-auto max-h-[calc(100vh-200px)]">
        {course.modules.map((mod, mi) => (
          <div key={mod.id}>
            <div className="px-4 py-2 bg-[#0a0e17] border-b border-[#1e2d45]">
              <p className="text-xs text-[#8899aa] font-medium uppercase tracking-wide">{mi + 1}. {mod.title_ru}</p>
            </div>
            {mod.lessons.map((lesson, li) => {
              const isActive = lesson.id === currentLessonId
              const isDone = lesson.user_progress?.completed
              return (
                <button
                  key={lesson.id}
                  onClick={() => onSelect(lesson.id)}
                  className={`w-full text-left px-4 py-3 flex items-center gap-3 border-b border-[#1e2d45] transition-colors ${
                    isActive ? 'bg-[#00d4ff]/5 text-[#00d4ff]' : 'hover:bg-[#1e2d45]/30'
                  }`}
                >
                  <span className={`text-xs w-5 h-5 rounded flex items-center justify-center shrink-0 ${
                    isDone ? 'bg-[#00e676]/10 text-[#00e676]' : isActive ? 'bg-[#00d4ff]/10 text-[#00d4ff]' : 'bg-[#1e2d45] text-[#4a5568]'
                  }`}>
                    {isDone ? '✓' : `${mi + 1}.${li + 1}`}
                  </span>
                  <span className={`text-xs ${isActive ? 'text-[#00d4ff]' : isDone ? 'text-[#4a5568]' : 'text-[#8899aa]'}`}>
                    {lesson.title_ru}
                  </span>
                </button>
              )
            })}
          </div>
        ))}
      </div>
    </div>
  )
}

// ─── Main ─────────────────────────────────────────────────────────────────────

export default function CourseLearner() {
  const { slug } = useParams<{ slug: string }>()
  const [searchParams, setSearchParams] = useSearchParams()
  const lessonId = Number(searchParams.get('lesson')) || null
  const { data: course } = useCourse(slug ?? '')
  const { data: lesson, isLoading } = useLesson(lessonId)

  // Автовыбор первого урока
  useEffect(() => {
    if (!lessonId && course?.modules[0]?.lessons[0]) {
      setSearchParams({ lesson: String(course.modules[0].lessons[0].id) })
    }
  }, [course, lessonId, setSearchParams])

  const handleSelectLesson = (id: number) => setSearchParams({ lesson: String(id) })

  const renderLesson = () => {
    if (!lesson) return null
    if (lesson.lesson_type === 'theory') return <LessonViewer lesson={lesson} />
    if (lesson.lesson_type === 'quiz') return lesson.quiz ? <QuizPlayer lesson={lesson} /> : null
    if (lesson.lesson_type === 'lab') return <LabLesson lesson={lesson} />
    return <p className="text-[#8899aa]">Тип урока не поддерживается</p>
  }

  return (
    <div className="min-h-screen bg-[#0a0e17] p-6">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-[#8899aa] mb-6">
        <Link to="/courses" className="hover:text-[#e2e8f0] transition-colors">Курсы</Link>
        <span>/</span>
        <Link to={`/courses/${slug}`} className="hover:text-[#e2e8f0] transition-colors">{course?.title_ru}</Link>
        {lesson && (
          <>
            <span>/</span>
            <span className="text-[#e2e8f0]">{lesson.title_ru}</span>
          </>
        )}
      </div>

      <div className="flex gap-6 max-w-7xl mx-auto">
        {/* Sidebar */}
        {course && (
          <LessonNav
            course={course}
            currentLessonId={lessonId ?? 0}
            onSelect={handleSelectLesson}
          />
        )}

        {/* Контент урока */}
        <div className="flex-1 min-w-0">
          {isLoading ? (
            <div className="space-y-4">
              <div className="h-8 bg-[#1e2d45]/30 rounded-xl animate-pulse w-64" />
              <div className="h-96 bg-[#1e2d45]/30 rounded-2xl animate-pulse" />
            </div>
          ) : lesson ? (
            <div className="bg-[#0f1520] border border-[#1e2d45] rounded-2xl p-6">
              <div className="flex items-center gap-3 mb-6">
                <h2 className="text-xl font-bold text-[#e2e8f0]">{lesson.title_ru}</h2>
                <span className="text-xs px-2 py-0.5 rounded-md bg-[#1e2d45] text-[#8899aa]">
                  {lesson.lesson_type_display}
                </span>
                <span className="text-xs text-[#00e676] ml-auto">+{lesson.xp_reward} XP</span>
              </div>
              {renderLesson()}
            </div>
          ) : (
            <div className="flex items-center justify-center h-64">
              <p className="text-[#8899aa]">Выберите урок</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
