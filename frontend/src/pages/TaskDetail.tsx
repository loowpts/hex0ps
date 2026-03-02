import { useState, useEffect, useRef, useCallback, lazy, Suspense } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import confetti from 'canvas-confetti'
import { useTask, useStartTask, useCheckTask, useHint, useReplay } from '@/api/hooks/useTasks'
import type { CheckResult, HintResult } from '@/types'
import TerminalPanel from '@/components/TerminalPanel'
import ReplayPlayer from '@/components/ReplayPlayer'
import AiChat from '@/components/AiChat'

// Ленивая загрузка тяжёлого Markdown-редактора
const NotesEditor = lazy(() => import('@/components/NotesEditor'))

// ─── TaskTimer ───────────────────────────────────────────────────────────────

function TaskTimer({ totalSeconds, onExpire }: { totalSeconds: number; onExpire?: () => void }) {
  const [remaining, setRemaining] = useState(totalSeconds)
  const expiredRef = useRef(false)

  useEffect(() => {
    setRemaining(totalSeconds)
    expiredRef.current = false
  }, [totalSeconds])

  useEffect(() => {
    if (remaining <= 0) {
      if (!expiredRef.current) {
        expiredRef.current = true
        onExpire?.()
      }
      return
    }
    const timer = setInterval(() => setRemaining((r) => Math.max(0, r - 1)), 1000)
    return () => clearInterval(timer)
  }, [remaining, onExpire])

  const pct = remaining / totalSeconds
  const mm = String(Math.floor(remaining / 60)).padStart(2, '0')
  const ss = String(remaining % 60).padStart(2, '0')
  const blink = pct < 0.1

  const colorClass =
    pct > 0.5 ? 'text-[#00e676]' : pct > 0.2 ? 'text-[#ff9500]' : 'text-red-400'

  return (
    <div className="flex items-center gap-3">
      <div className={`text-2xl font-mono font-bold ${colorClass} ${blink ? 'animate-pulse' : ''}`}>
        {mm}:{ss}
      </div>
      <div className="flex-1 h-2 bg-[#1e2d45] rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-1000 ${
            pct > 0.5 ? 'bg-[#00e676]' : pct > 0.2 ? 'bg-[#ff9500]' : 'bg-red-400'
          }`}
          style={{ width: `${pct * 100}%` }}
        />
      </div>
    </div>
  )
}

// ─── HintSystem ──────────────────────────────────────────────────────────────

interface HintSystemProps {
  taskId: number
  hintsUsed: number
}

function HintSystem({ taskId, hintsUsed }: HintSystemProps) {
  const [revealedHints, setRevealedHints] = useState<Record<number, HintResult>>({})
  const [confirmLevel, setConfirmLevel] = useState<2 | 3 | null>(null)
  const hintMutation = useHint()
  const [open, setOpen] = useState(false)

  const doRequestHint = (level: 1 | 2 | 3) => {
    if (revealedHints[level]) return
    hintMutation.mutate(
      { taskId, level },
      {
        onSuccess: (data) => {
          setRevealedHints((prev) => ({ ...prev, [level]: data }))
          setConfirmLevel(null)
        },
      }
    )
  }

  const handleHintClick = (level: 1 | 2 | 3) => {
    if (revealedHints[level]) return
    // Для уровней 2 и 3 — диалог подтверждения
    if (level === 2 || level === 3) {
      setConfirmLevel(level)
    } else {
      doRequestHint(level)
    }
  }

  const HINT_LABELS = ['Лёгкая подсказка', 'Направление', 'Детальная подсказка']
  const HINT_COST = ['−10% XP', '−25% XP', '−50% XP']

  return (
    <div className="hint-system border border-[#1e2d45] rounded-xl overflow-hidden">
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center justify-between px-4 py-3 bg-[#0a0e17] hover:bg-[#1e2d45]/30 transition-colors"
      >
        <div className="flex items-center gap-2">
          <svg className="w-4 h-4 text-[#ff9500]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.347.347a3.5 3.5 0 00-1.028 2.471v.8A2.5 2.5 0 0112 19.5a2.5 2.5 0 01-2.5-2.5v-.8a3.5 3.5 0 00-1.028-2.471l-.347-.347z" />
          </svg>
          <span className="text-sm font-medium text-[#e2e8f0]">Подсказки</span>
          {hintsUsed > 0 && (
            <span className="text-xs text-[#ff9500]">использовано: {hintsUsed}</span>
          )}
        </div>
        <svg
          className={`w-4 h-4 text-[#8899aa] transition-transform ${open ? 'rotate-180' : ''}`}
          fill="none" viewBox="0 0 24 24" stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {open && (
        <div className="p-4 space-y-3 bg-[#0a0e17]">
          {([1, 2, 3] as const).map((level) => {
            const isLocked = level > 1 && !revealedHints[level - 1]
            return (
              <div key={level} className="border border-[#1e2d45] rounded-xl p-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-[#e2e8f0]">{HINT_LABELS[level - 1]}</span>
                  <span className="text-xs text-red-400">{HINT_COST[level - 1]}</span>
                </div>
                {revealedHints[level] ? (
                  <p className="text-[#8899aa] text-sm leading-relaxed animate-fadeIn">
                    {revealedHints[level].hint_text}
                  </p>
                ) : (
                  <button
                    onClick={() => handleHintClick(level)}
                    disabled={isLocked || hintMutation.isPending}
                    className="w-full py-1.5 rounded-lg text-xs font-medium border border-[#ff9500]/30 text-[#ff9500] hover:bg-[#ff9500]/10 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-1.5"
                  >
                    {isLocked ? (
                      <>
                        <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                        </svg>
                        Сначала откройте подсказку {level - 1}
                      </>
                    ) : hintMutation.isPending ? (
                      'Загрузка...'
                    ) : (
                      '💡 Показать подсказку'
                    )}
                  </button>
                )}
              </div>
            )
          })}
        </div>
      )}

      {/* Диалог подтверждения для уровней 2 и 3 */}
      {confirmLevel && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
          <div className="bg-[#0f1520] border border-[#ff9500]/40 rounded-2xl p-6 max-w-sm w-full shadow-2xl">
            <div className="flex items-start gap-3 mb-4">
              <div className="w-10 h-10 rounded-xl bg-[#ff9500]/15 flex items-center justify-center shrink-0">
                <svg className="w-5 h-5 text-[#ff9500]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <div>
                <h3 className="text-[#e2e8f0] font-semibold mb-1">
                  Подсказка {confirmLevel} уровня
                </h3>
                <p className="text-[#8899aa] text-sm leading-relaxed">
                  Эта подсказка снизит твой XP за задачу на{' '}
                  <span className="text-red-400 font-semibold">
                    {confirmLevel === 2 ? '25%' : '50%'}
                  </span>
                  . Уверен, что хочешь открыть её?
                </p>
              </div>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => setConfirmLevel(null)}
                className="flex-1 py-2.5 rounded-xl text-sm font-medium border border-[#1e2d45] text-[#8899aa] hover:text-[#e2e8f0] transition-colors"
              >
                Отмена
              </button>
              <button
                onClick={() => doRequestHint(confirmLevel)}
                disabled={hintMutation.isPending}
                className="flex-1 py-2.5 rounded-xl text-sm font-semibold bg-[#ff9500] text-[#0a0e17] hover:bg-[#e08500] disabled:opacity-50 transition-colors"
              >
                {hintMutation.isPending ? 'Загрузка...' : 'Открыть подсказку'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// ─── DangerousCommandBanner ───────────────────────────────────────────────────

interface DangerousBannerProps {
  command: string
  onDismiss: () => void
}

function DangerousCommandBanner({ command, onDismiss }: DangerousBannerProps) {
  return (
    <div className="fixed top-4 left-1/2 -translate-x-1/2 z-50 w-full max-w-lg px-4">
      <div className="bg-[#0f1520] border border-[#ff9500]/60 rounded-2xl p-4 shadow-2xl flex gap-3">
        <div className="w-10 h-10 rounded-xl bg-[#ff9500]/15 flex items-center justify-center shrink-0">
          <svg className="w-5 h-5 text-[#ff9500]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-[#ff9500] font-semibold text-sm">⚠️ Опасная команда!</p>
          <code className="text-[#e2e8f0] text-xs font-mono block mt-0.5 truncate">
            $ {command}
          </code>
          <p className="text-[#8899aa] text-xs mt-1">
            Эта команда может повредить систему. Убедись что понимаешь последствия.
          </p>
        </div>
        <button
          onClick={onDismiss}
          className="w-6 h-6 rounded-lg flex items-center justify-center text-[#8899aa] hover:text-[#e2e8f0] shrink-0 mt-0.5"
        >
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  )
}

// ─── XP Modal ────────────────────────────────────────────────────────────────

function XpModal({ result, onClose, onShowReplay }: {
  result: CheckResult
  onClose: () => void
  onShowReplay: () => void
}) {
  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <div className="bg-[#0f1520] border border-[#1e2d45] rounded-2xl p-8 max-w-sm w-full text-center">
        <div className="text-5xl mb-4">🎉</div>
        <h2 className="text-2xl font-bold text-[#00e676] mb-2">Задача выполнена!</h2>
        <p className="text-[#8899aa] mb-4">{result.message}</p>

        {result.xp_earned !== undefined && (
          <div className="bg-[#00e676]/10 border border-[#00e676]/30 rounded-xl p-4 mb-4">
            <p className="text-3xl font-bold text-[#00e676]">+{result.xp_earned} XP</p>
            {result.xp_multiplier && result.xp_multiplier < 1 && (
              <p className="text-xs text-[#8899aa] mt-1">
                Множитель: {Math.round(result.xp_multiplier * 100)}%
              </p>
            )}
          </div>
        )}

        {result.new_achievements && result.new_achievements.length > 0 && (
          <div className="mb-4">
            <p className="text-[#8899aa] text-sm mb-2">Новые достижения:</p>
            {result.new_achievements.map((ach, i) => (
              <div key={i} className="flex items-center gap-2 text-sm text-[#e2e8f0] justify-center">
                <span>{ach.icon}</span>
                <span>{ach.title_ru}</span>
              </div>
            ))}
          </div>
        )}

        <div className="flex gap-3">
          <button
            onClick={onShowReplay}
            className="flex-1 py-3 rounded-xl font-semibold border border-[#1e2d45] text-[#8899aa] hover:text-[#e2e8f0] transition-colors text-sm"
          >
            Посмотреть решение
          </button>
          <button
            onClick={onClose}
            className="flex-1 py-3 rounded-xl font-semibold bg-[#00e676] text-[#0a0e17] hover:bg-[#00cf6e] transition-colors"
          >
            Продолжить
          </button>
        </div>
      </div>
    </div>
  )
}

// ─── ReplayTab ───────────────────────────────────────────────────────────────

function ReplayTab({ taskId }: { taskId: number }) {
  const { data: replay, isLoading } = useReplay(taskId, true)

  if (isLoading) {
    return (
      <div className="space-y-3 animate-pulse">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="h-12 bg-[#1e2d45] rounded-xl" />
        ))}
      </div>
    )
  }

  if (!replay?.solution_steps?.length) {
    return <p className="text-[#8899aa] text-sm">Решение недоступно</p>
  }

  return <ReplayPlayer steps={replay.solution_steps} />
}

// ─── Diff colors ─────────────────────────────────────────────────────────────

const DIFF_COLORS: Record<string, string> = {
  beginner: 'bg-[#00e676]/10 text-[#00e676] border-[#00e676]/30',
  intermediate: 'bg-[#ff9500]/10 text-[#ff9500] border-[#ff9500]/30',
  advanced: 'bg-red-500/10 text-red-400 border-red-400/30',
}

// ─── Main Page ───────────────────────────────────────────────────────────────

export default function TaskDetail() {
  const { taskId } = useParams<{ taskId: string }>()
  const navigate = useNavigate()
  const id = Number(taskId)

  const { data: task, isLoading } = useTask(id)
  const startTask = useStartTask()
  const checkTask = useCheckTask()

  const [sessionId, setSessionId] = useState<string | undefined>()
  const [checkResult, setCheckResult] = useState<CheckResult | null>(null)
  const [activeTab, setActiveTab] = useState<'notes' | 'replay'>('notes')
  const [isCompleted, setIsCompleted] = useState(false)
  const [dangerousCmd, setDangerousCmd] = useState<string | null>(null)
  const [aiChatOpen, setAiChatOpen] = useState(false)

  const handleStart = () => {
    startTask.mutate(id, {
      onSuccess: (session) => {
        setSessionId(session.session_id)
      },
    })
  }

  const handleCheck = () => {
    checkTask.mutate(id, {
      onSuccess: (result) => {
        if (result.success) {
          setCheckResult(result)
          setIsCompleted(true)
          confetti({
            particleCount: 150,
            spread: 80,
            origin: { y: 0.6 },
            colors: ['#00d4ff', '#00e676', '#ff9500'],
          })
        } else {
          setCheckResult(result)
        }
      },
    })
  }

  const handleTimerExpire = useCallback(() => {
    // Auto-check when time runs out
  }, [])

  const handleDangerousCommand = useCallback((cmd: string) => {
    setDangerousCmd(cmd)
    // Авто-скрытие через 8 секунд
    setTimeout(() => setDangerousCmd(null), 8000)
  }, [])

  const handleSessionExpired = useCallback(() => {
    // Можно показать уведомление
  }, [])

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#0a0e17] flex items-center justify-center">
        <div className="text-[#8899aa]">Загрузка задачи...</div>
      </div>
    )
  }

  if (!task) {
    return (
      <div className="min-h-screen bg-[#0a0e17] flex items-center justify-center">
        <div className="text-center">
          <p className="text-[#e2e8f0] text-lg mb-4">Задача не найдена</p>
          <button
            onClick={() => navigate('/tasks')}
            className="px-4 py-2 rounded-xl text-sm text-[#00d4ff] border border-[#00d4ff]/30"
          >
            Вернуться к задачам
          </button>
        </div>
      </div>
    )
  }

  const diffClass = DIFF_COLORS[task.difficulty] ?? 'bg-[#1e2d45] text-[#8899aa] border-[#1e2d45]'
  const timeLimit = (task.time_limit || 10) * 60

  return (
    <div className="min-h-screen bg-[#0a0e17] flex flex-col">
      {/* Баннер опасной команды */}
      {dangerousCmd && (
        <DangerousCommandBanner
          command={dangerousCmd}
          onDismiss={() => setDangerousCmd(null)}
        />
      )}

      {/* Top bar */}
      <div className="flex items-center gap-4 px-4 py-3 bg-[#0f1520] border-b border-[#1e2d45] shrink-0">
        <button
          onClick={() => navigate('/tasks')}
          className="text-[#8899aa] hover:text-[#e2e8f0] transition-colors"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <h1 className="text-[#e2e8f0] font-medium text-sm flex-1 truncate">{task.title_ru}</h1>
        <span className={`text-xs px-2 py-0.5 rounded-md border ${diffClass}`}>
          {task.difficulty_display}
        </span>
        {task.task_type === 'break_and_fix' && (
          <span className="text-xs px-2 py-0.5 rounded-md bg-red-500/10 text-red-400 border border-red-400/30">
            Break&Fix
          </span>
        )}
      </div>

      {/* Main content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left: Terminal (60%) */}
        <div className="w-[60%] p-4 flex flex-col gap-3">
          <div className="flex-1 min-h-0">
            {sessionId ? (
              <TerminalPanel
                sessionId={sessionId}
                onDangerousCommand={handleDangerousCommand}
                onExpired={handleSessionExpired}
              />
            ) : (
              <div className="w-full h-full bg-[#050810] rounded-xl border border-[#1e2d45] flex flex-col">
                <div className="flex items-center gap-2 px-4 py-2.5 border-b border-[#1e2d45]">
                  <div className="w-3 h-3 rounded-full bg-[#ff5f57]" />
                  <div className="w-3 h-3 rounded-full bg-[#ffbc2e]" />
                  <div className="w-3 h-3 rounded-full bg-[#28c840]" />
                  <span className="ml-3 text-[#8899aa] text-xs font-mono">терминал</span>
                </div>
                <div className="flex-1 flex items-center justify-center">
                  <div className="text-center">
                    <p className="text-[#8899aa] text-sm mb-2">Нажмите «Начать задачу»</p>
                    <p className="text-[#8899aa] text-xs font-mono">$ _</p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Start button */}
          {!sessionId && (
            <button
              onClick={handleStart}
              disabled={startTask.isPending}
              className="w-full py-3 rounded-xl font-semibold text-[#0a0e17] bg-[#00e676] hover:bg-[#00cf6e] disabled:opacity-50 transition-colors"
            >
              {startTask.isPending ? 'Запускаем...' : 'Начать задачу'}
            </button>
          )}
        </div>

        {/* Right: Info panel (40%) */}
        <div className="w-[40%] border-l border-[#1e2d45] p-4 overflow-y-auto flex flex-col gap-4">
          {/* Description */}
          <div className="bg-[#0f1520] border border-[#1e2d45] rounded-xl p-4">
            <h2 className="text-[#e2e8f0] font-semibold mb-2">Описание задачи</h2>
            <p className="text-[#8899aa] text-sm leading-relaxed whitespace-pre-wrap">
              {task.description_ru || 'Нет описания'}
            </p>
            <div className="flex items-center gap-4 mt-3 pt-3 border-t border-[#1e2d45]">
              <span className="text-xs text-[#8899aa]">
                XP: <span className="text-[#00e676] font-semibold">+{task.xp_reward}</span>
              </span>
              <span className="text-xs text-[#8899aa]">
                Время: <span className="text-[#00d4ff] font-semibold">{Math.floor(timeLimit / 60)} мин</span>
              </span>
            </div>
          </div>

          {/* Timer */}
          {sessionId && (
            <div className="bg-[#0f1520] border border-[#1e2d45] rounded-xl p-4">
              <p className="text-[#8899aa] text-xs mb-2">Оставшееся время</p>
              <TaskTimer totalSeconds={timeLimit} onExpire={handleTimerExpire} />
            </div>
          )}

          {/* Check result (non-success) */}
          {checkResult && !checkResult.success && (
            <div className="bg-red-500/10 border border-red-400/30 rounded-xl p-4">
              <p className="text-red-400 text-sm">{checkResult.message}</p>
            </div>
          )}

          {/* Check button */}
          {sessionId && !isCompleted && (
            <button
              onClick={handleCheck}
              disabled={checkTask.isPending}
              className="w-full py-3 rounded-xl font-semibold text-[#0a0e17] bg-[#00d4ff] hover:bg-[#00bfe8] disabled:opacity-50 transition-colors"
            >
              {checkTask.isPending ? 'Проверяем...' : 'Проверить решение'}
            </button>
          )}

          {/* Hints */}
          <HintSystem
            taskId={id}
            hintsUsed={task.user_task?.hints_used ?? 0}
          />

          {/* AI Chat button */}
          <button
            onClick={() => setAiChatOpen(true)}
            className="w-full py-2.5 rounded-xl text-sm font-medium border border-[#1e2d45] text-[#8899aa] hover:border-[#00d4ff]/40 hover:text-[#00d4ff] transition-colors flex items-center justify-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
            Спросить AI-ассистента
          </button>

          {/* Tabs: Notes | Replay */}
          <div className="bg-[#0f1520] border border-[#1e2d45] rounded-xl overflow-hidden">
            <div className="flex border-b border-[#1e2d45]">
              {(['notes', 'replay'] as const).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  disabled={tab === 'replay' && !isCompleted}
                  className={`flex-1 py-2.5 text-sm font-medium transition-colors disabled:opacity-40 ${
                    activeTab === tab
                      ? 'text-[#00d4ff] border-b-2 border-[#00d4ff]'
                      : 'text-[#8899aa] hover:text-[#e2e8f0]'
                  }`}
                >
                  {tab === 'notes' ? 'Заметки' : 'Решение'}
                </button>
              ))}
            </div>
            <div className="p-4">
              {activeTab === 'notes' ? (
                <Suspense fallback={<div className="h-40 bg-[#1e2d45] rounded-xl animate-pulse" />}>
                  <NotesEditor taskId={id} />
                </Suspense>
              ) : (
                <ReplayTab taskId={id} />
              )}
            </div>
          </div>
        </div>
      </div>

      {/* XP Modal */}
      {checkResult?.success && (
        <XpModal
          result={checkResult}
          onClose={() => {
            setCheckResult(null)
            navigate('/tasks')
          }}
          onShowReplay={() => {
            setCheckResult(null)
            setActiveTab('replay')
          }}
        />
      )}

      {/* AI Chat Sidebar */}
      <AiChat
        taskId={id}
        taskTitle={task.title_ru}
        isOpen={aiChatOpen}
        onClose={() => setAiChatOpen(false)}
      />
    </div>
  )
}
