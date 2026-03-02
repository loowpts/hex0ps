import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { api } from '@/api/client'
import type { InterviewQuestion, InterviewAttemptResult } from '@/types'

// ─── Hooks ────────────────────────────────────────────────────────────────────

function useInterviewCategories() {
  return useQuery<{ category: string; label: string; total: number; answered: number }[]>({
    queryKey: ['interview-categories'],
    queryFn: () => api.get('/interview/categories/').then((r) => r.data),
  })
}

function useInterviewQuestions(category?: string) {
  return useQuery<InterviewQuestion[]>({
    queryKey: ['interview-questions', category],
    queryFn: () =>
      api.get('/interview/questions/', { params: category ? { category } : {} }).then((r) => r.data),
    enabled: true,
  })
}

function useSubmitAnswer() {
  return useMutation<InterviewAttemptResult, Error, { questionId: number; answer: string }>({
    mutationFn: ({ questionId, answer }) =>
      api
        .post('/interview/answer/', { question_id: questionId, answer }, { timeout: 60_000 })
        .then((r) => r.data),
    onError: () => {
      toast.error('Не удалось отправить ответ. Попробуй ещё раз.')
    },
  })
}

// ─── Components ───────────────────────────────────────────────────────────────

function ScoreBar({ score }: { score: number }) {
  const pct = (score / 10) * 100
  const color =
    score >= 8 ? 'bg-[#00e676]' : score >= 5 ? 'bg-[#ff9500]' : 'bg-red-400'
  const textColor =
    score >= 8 ? 'text-[#00e676]' : score >= 5 ? 'text-[#ff9500]' : 'text-red-400'

  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-[#8899aa]">Оценка AI</span>
        <span className={`font-bold ${textColor}`}>{score}/10</span>
      </div>
      <div className="h-3 bg-[#1e2d45] rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-700 ${color}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}

const CATEGORY_LABELS: Record<string, string> = {
  linux: 'Linux',
  nginx: 'Nginx',
  systemd: 'Systemd',
  docker: 'Docker',
  networks: 'Сети',
  git: 'Git',
  cicd: 'CI/CD',
}

const DIFF_COLORS: Record<string, string> = {
  beginner: 'text-[#00e676] bg-[#00e676]/10',
  intermediate: 'text-[#ff9500] bg-[#ff9500]/10',
  advanced: 'text-red-400 bg-red-400/10',
}

function CategoryCard({
  category: _category,
  label,
  total,
  answered,
  active,
  onClick,
}: {
  category?: string
  label: string
  total: number
  answered: number
  active: boolean
  onClick: () => void
}) {
  const pct = total > 0 ? Math.round((answered / total) * 100) : 0

  return (
    <button
      onClick={onClick}
      className={`w-full text-left p-4 rounded-xl border transition-colors ${
        active
          ? 'border-[#00d4ff]/40 bg-[#00d4ff]/5'
          : 'border-[#1e2d45] bg-[#0a0e17] hover:border-[#00d4ff]/30'
      }`}
    >
      <p className={`text-sm font-medium mb-1 ${active ? 'text-[#00d4ff]' : 'text-[#e2e8f0]'}`}>
        {label}
      </p>
      <div className="flex justify-between text-xs text-[#8899aa] mb-1.5">
        <span>{answered}/{total} вопросов</span>
        <span>{pct}%</span>
      </div>
      <div className="h-1.5 bg-[#1e2d45] rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all ${active ? 'bg-[#00d4ff]' : 'bg-[#1e2d45]'}`}
          style={{ width: `${pct}%`, backgroundColor: pct > 0 ? '#00d4ff' : undefined }}
        />
      </div>
    </button>
  )
}

// ─── Main ────────────────────────────────────────────────────────────────────

export default function Interview() {
  const [selectedCategory, setSelectedCategory] = useState<string>('')
  const [selectedQuestion, setSelectedQuestion] = useState<InterviewQuestion | null>(null)
  const [answer, setAnswer] = useState('')
  const [result, setResult] = useState<InterviewAttemptResult | null>(null)
  const [validationError, setValidationError] = useState<string | null>(null)

  const { data: categories, isLoading: catsLoading } = useInterviewCategories()
  const { data: questions, isLoading: qsLoading } = useInterviewQuestions(selectedCategory || undefined)
  const submitAnswer = useSubmitAnswer()

  const handleSubmit = () => {
    if (!selectedQuestion) return
    const trimmed = answer.trim()
    if (trimmed.length < 20) {
      setValidationError('Ответ слишком короткий. Постарайся развёрнуто объяснить тему (минимум 20 символов).')
      return
    }
    setValidationError(null)
    submitAnswer.mutate(
      { questionId: selectedQuestion.id, answer: trimmed },
      {
        onSuccess: (data) => {
          setResult(data)
        },
      }
    )
  }

  const handleNextQuestion = () => {
    setAnswer('')
    setResult(null)
    setSelectedQuestion(null)
    setValidationError(null)
  }

  return (
    <div className="min-h-screen bg-[#0a0e17] p-6 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-[#e2e8f0] mb-1">Подготовка к интервью</h1>
        <p className="text-[#8899aa] text-sm">Практические вопросы с AI-оценкой ответов</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Categories */}
        <div className="lg:col-span-1">
          <h2 className="text-[#e2e8f0] font-semibold mb-3">Категории</h2>

          {catsLoading ? (
            <div className="space-y-3 animate-pulse">
              {Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="h-16 bg-[#1e2d45] rounded-xl" />
              ))}
            </div>
          ) : categories ? (
            <div className="space-y-2">
              <button
                onClick={() => setSelectedCategory('')}
                className={`w-full text-left p-3 rounded-xl border text-sm transition-colors ${
                  selectedCategory === ''
                    ? 'border-[#00d4ff]/40 bg-[#00d4ff]/5 text-[#00d4ff]'
                    : 'border-[#1e2d45] bg-[#0a0e17] text-[#8899aa] hover:border-[#00d4ff]/30 hover:text-[#e2e8f0]'
                }`}
              >
                Все категории
              </button>
              {categories.map((cat) => (
                <CategoryCard
                  key={cat.category}
                  category={cat.category}
                  label={cat.label || CATEGORY_LABELS[cat.category] || cat.category}
                  total={cat.total}
                  answered={cat.answered}
                  active={selectedCategory === cat.category}
                  onClick={() => {
                    setSelectedCategory(cat.category)
                    setSelectedQuestion(null)
                    setResult(null)
                    setAnswer('')
                  }}
                />
              ))}
            </div>
          ) : (
            <div className="space-y-2">
              {Object.entries(CATEGORY_LABELS).map(([cat, label]) => (
                <button
                  key={cat}
                  onClick={() => {
                    setSelectedCategory(cat)
                    setSelectedQuestion(null)
                    setResult(null)
                    setAnswer('')
                  }}
                  className={`w-full text-left p-3 rounded-xl border text-sm transition-colors ${
                    selectedCategory === cat
                      ? 'border-[#00d4ff]/40 bg-[#00d4ff]/5 text-[#00d4ff]'
                      : 'border-[#1e2d45] bg-[#0a0e17] text-[#8899aa] hover:border-[#00d4ff]/30'
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Right: Questions & Answer */}
        <div className="lg:col-span-2 space-y-4">
          {!selectedQuestion ? (
            /* Question List */
            <div>
              <h2 className="text-[#e2e8f0] font-semibold mb-3">
                Вопросы{selectedCategory ? ` — ${CATEGORY_LABELS[selectedCategory] ?? selectedCategory}` : ''}
              </h2>

              {qsLoading ? (
                <div className="space-y-3 animate-pulse">
                  {Array.from({ length: 4 }).map((_, i) => (
                    <div key={i} className="h-20 bg-[#1e2d45] rounded-xl" />
                  ))}
                </div>
              ) : questions && questions.length > 0 ? (
                <div className="space-y-3">
                  {questions.map((q) => (
                    <button
                      key={q.id}
                      onClick={() => {
                        setSelectedQuestion(q)
                        setAnswer('')
                        setResult(null)
                      }}
                      className="w-full text-left bg-[#0f1520] border border-[#1e2d45] rounded-xl p-4 hover:border-[#00d4ff]/40 transition-colors group"
                    >
                      <div className="flex items-start justify-between gap-3">
                        <p className="text-[#e2e8f0] text-sm group-hover:text-[#00d4ff] transition-colors">
                          {q.question_ru}
                        </p>
                        <span
                          className={`shrink-0 text-xs px-2 py-0.5 rounded-md ${
                            DIFF_COLORS[q.difficulty] ?? 'text-[#8899aa] bg-[#1e2d45]'
                          }`}
                        >
                          {q.difficulty}
                        </span>
                      </div>
                      {q.tags.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-2">
                          {q.tags.map((tag) => (
                            <span
                              key={tag}
                              className="text-xs px-1.5 py-0.5 rounded bg-[#1e2d45] text-[#8899aa]"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </button>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <p className="text-[#8899aa]">Нет вопросов для выбранной категории</p>
                </div>
              )}
            </div>
          ) : (
            /* Question Detail & Answer */
            <div className="space-y-4">
              <button
                onClick={handleNextQuestion}
                className="flex items-center gap-2 text-[#8899aa] hover:text-[#e2e8f0] transition-colors text-sm"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
                Назад к вопросам
              </button>

              {/* Question */}
              <div className="bg-[#0f1520] border border-[#1e2d45] rounded-2xl p-5">
                <div className="flex items-start justify-between gap-3 mb-3">
                  <h3 className="text-[#e2e8f0] font-medium leading-relaxed">
                    {selectedQuestion.question_ru}
                  </h3>
                  <span
                    className={`shrink-0 text-xs px-2 py-0.5 rounded-md ${
                      DIFF_COLORS[selectedQuestion.difficulty] ?? 'text-[#8899aa] bg-[#1e2d45]'
                    }`}
                  >
                    {selectedQuestion.difficulty}
                  </span>
                </div>
                {selectedQuestion.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {selectedQuestion.tags.map((tag) => (
                      <span key={tag} className="text-xs px-1.5 py-0.5 rounded bg-[#1e2d45] text-[#8899aa]">
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Answer */}
              {!result ? (
                <div className="space-y-3">
                  <label className="block text-sm font-medium text-[#8899aa]">Ваш ответ</label>
                  <textarea
                    value={answer}
                    onChange={(e) => { setAnswer(e.target.value); setValidationError(null) }}
                    placeholder="Напишите подробный ответ..."
                    rows={8}
                    className={`w-full bg-[#0f1520] border rounded-xl px-4 py-3 text-[#e2e8f0] text-sm placeholder-[#4a5568] focus:outline-none resize-none transition-colors ${
                      validationError ? 'border-red-500/60 focus:border-red-500' : 'border-[#1e2d45] focus:border-[#00d4ff]/50'
                    }`}
                  />
                  {validationError && (
                    <p className="text-red-400 text-xs">{validationError}</p>
                  )}
                  {submitAnswer.isError && (
                    <p className="text-red-400 text-xs text-center">
                      Ошибка при отправке. Проверь соединение и попробуй ещё раз.
                    </p>
                  )}
                  <button
                    onClick={handleSubmit}
                    disabled={!answer.trim() || submitAnswer.isPending}
                    className="w-full py-3 rounded-xl font-semibold text-[#0a0e17] bg-[#00d4ff] hover:bg-[#00bfe8] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {submitAnswer.isPending ? 'Оцениваем ответ...' : 'Отправить на проверку AI'}
                  </button>
                </div>
              ) : (
                /* Result */
                <div className="space-y-4">
                  {/* Score */}
                  <div className="bg-[#0f1520] border border-[#1e2d45] rounded-2xl p-5">
                    <ScoreBar score={result.score} />
                  </div>

                  {/* Feedback */}
                  <div className="bg-[#0f1520] border border-[#1e2d45] rounded-2xl p-5">
                    <h4 className="text-[#e2e8f0] font-medium mb-3">Обратная связь</h4>
                    <p className="text-[#8899aa] text-sm leading-relaxed">{result.feedback}</p>
                  </div>

                  {/* Strengths */}
                  {result.strengths.length > 0 && (
                    <div className="bg-[#00e676]/5 border border-[#00e676]/20 rounded-2xl p-5">
                      <h4 className="text-[#00e676] font-medium mb-3">Сильные стороны</h4>
                      <ul className="space-y-1">
                        {result.strengths.map((s, i) => (
                          <li key={i} className="flex items-start gap-2 text-sm text-[#8899aa]">
                            <svg className="w-4 h-4 text-[#00e676] shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                            {s}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Improvements */}
                  {result.improvements.length > 0 && (
                    <div className="bg-[#ff9500]/5 border border-[#ff9500]/20 rounded-2xl p-5">
                      <h4 className="text-[#ff9500] font-medium mb-3">Что улучшить</h4>
                      <ul className="space-y-1">
                        {result.improvements.map((imp, i) => (
                          <li key={i} className="flex items-start gap-2 text-sm text-[#8899aa]">
                            <svg className="w-4 h-4 text-[#ff9500] shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                            </svg>
                            {imp}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <button
                    onClick={handleNextQuestion}
                    className="w-full py-3 rounded-xl font-semibold border border-[#1e2d45] text-[#8899aa] hover:border-[#00d4ff]/40 hover:text-[#00d4ff] transition-colors"
                  >
                    Следующий вопрос
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
