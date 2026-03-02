import { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/api/client'
import type { DailyChallengeData } from '@/types'

// ─── Helpers ──────────────────────────────────────────────────────────────────

function formatTime(seconds: number): string {
  if (seconds < 60) return `${seconds}с`
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${m}м ${s}с`
}

function difficultyColor(d: string) {
  if (d === 'beginner') return 'text-[#00e676] border-[#00e676]/30 bg-[#00e676]/5'
  if (d === 'intermediate') return 'text-[#ff9500] border-[#ff9500]/30 bg-[#ff9500]/5'
  return 'text-red-400 border-red-500/30 bg-red-500/5'
}

function categoryColor(c: string) {
  const map: Record<string, string> = {
    linux: 'bg-[#00d4ff]/10 text-[#00d4ff]',
    nginx: 'bg-[#00e676]/10 text-[#00e676]',
    docker: 'bg-blue-500/10 text-blue-400',
    networks: 'bg-purple-500/10 text-purple-400',
    systemd: 'bg-orange-500/10 text-orange-400',
    git: 'bg-red-500/10 text-red-400',
    cicd: 'bg-yellow-500/10 text-yellow-400',
  }
  return map[c] ?? 'bg-[#1e2d45] text-[#8899aa]'
}

// ─── Leaderboard ──────────────────────────────────────────────────────────────

function Leaderboard({ entries }: { entries: DailyChallengeData['leaderboard'] }) {
  if (entries.length === 0) {
    return (
      <div className="text-center py-8 text-[#4a5568] text-sm">
        Ещё никто не выполнил задачу дня. Будь первым!
      </div>
    )
  }

  const medals = ['🥇', '🥈', '🥉']

  return (
    <div className="space-y-2">
      {entries.map((entry) => (
        <div
          key={entry.rank}
          className={`flex items-center gap-3 px-4 py-3 rounded-xl border transition-colors ${
            entry.rank <= 3
              ? 'border-[#00d4ff]/20 bg-[#00d4ff]/3'
              : 'border-[#1e2d45] bg-[#0a0e17]'
          }`}
        >
          <span className="text-lg w-6 text-center">
            {entry.rank <= 3 ? medals[entry.rank - 1] : `${entry.rank}.`}
          </span>
          <span className="flex-1 text-sm font-medium text-[#e2e8f0] truncate">
            {entry.username}
          </span>
          <span className="text-sm text-[#8899aa]">{formatTime(entry.time_spent)}</span>
          <span className="text-xs text-[#00e676] ml-2">+{entry.xp_earned} XP</span>
        </div>
      ))}
    </div>
  )
}

// ─── Timer ────────────────────────────────────────────────────────────────────

function ChallengeTimer({ started, onComplete }: { started: boolean; onComplete: (seconds: number) => void }) {
  const [elapsed, setElapsed] = useState(0)
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    if (started) {
      intervalRef.current = setInterval(() => setElapsed(e => e + 1), 1000)
    }
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current)
    }
  }, [started])

  if (!started) return null

  return (
    <div className="flex items-center gap-3 bg-[#0a0e17] border border-[#1e2d45] rounded-xl px-4 py-3 mb-4">
      <div className="w-2 h-2 rounded-full bg-[#00e676] animate-pulse" />
      <span className="text-[#8899aa] text-sm">Таймер:</span>
      <span className="text-[#e2e8f0] font-mono font-bold">{formatTime(elapsed)}</span>
      <button
        onClick={() => {
          if (intervalRef.current) clearInterval(intervalRef.current)
          onComplete(elapsed)
        }}
        className="ml-auto px-4 py-1.5 rounded-lg text-sm font-semibold text-[#0a0e17] bg-[#00e676] hover:bg-[#00d068] transition-colors"
      >
        Отметить как выполнено
      </button>
    </div>
  )
}

// ─── Main ─────────────────────────────────────────────────────────────────────

export default function DailyChallenge() {
  const qc = useQueryClient()
  const [started, setStarted] = useState(false)

  const { data: challenge, isLoading } = useQuery<DailyChallengeData>({
    queryKey: ['daily-challenge'],
    queryFn: () => api.get('/daily/').then((r) => r.data),
    staleTime: 1000 * 60 * 5,
  })

  const startMutation = useMutation({
    mutationFn: () => api.post('/daily/start/').then((r) => r.data),
    onSuccess: () => setStarted(true),
  })

  const completeMutation = useMutation({
    mutationFn: (timeSpent: number) =>
      api.post('/daily/complete/', { time_spent: timeSpent }).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['daily-challenge'] }),
  })

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#0a0e17] p-6">
        <div className="max-w-4xl mx-auto space-y-4">
          <div className="h-8 bg-[#1e2d45]/30 rounded-xl animate-pulse w-48" />
          <div className="h-64 bg-[#1e2d45]/30 rounded-2xl animate-pulse" />
        </div>
      </div>
    )
  }

  if (!challenge) return null

  const { task, my_completion, leaderboard } = challenge
  const today = new Date(challenge.date).toLocaleDateString('ru-RU', {
    day: 'numeric', month: 'long', year: 'numeric',
  })

  return (
    <div className="min-h-screen bg-[#0a0e17] p-6">
      <div className="max-w-4xl mx-auto">

        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center gap-3 mb-1">
            <span className="text-2xl">⚔️</span>
            <h1 className="text-2xl font-bold text-[#e2e8f0]">Daily Challenge</h1>
            <span className="text-xs px-2 py-0.5 rounded-md border border-[#1e2d45] text-[#8899aa]">
              {today}
            </span>
          </div>
          <p className="text-[#4a5568] text-sm">
            {challenge.participants_count} участников · {challenge.completions_count} выполнений
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

          {/* Задача */}
          <div className="lg:col-span-2 space-y-4">

            {/* Карточка задачи */}
            <div className="bg-[#0f1520] border border-[#1e2d45] rounded-2xl p-6">
              <div className="flex items-start gap-3 mb-4">
                <div className="flex-1">
                  <h2 className="text-xl font-bold text-[#e2e8f0] mb-2">{task.title_ru}</h2>
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className={`text-xs px-2 py-0.5 rounded-md ${categoryColor(task.category)}`}>
                      {task.category_display}
                    </span>
                    <span className={`text-xs px-2 py-0.5 rounded-md border ${difficultyColor(task.difficulty)}`}>
                      {task.difficulty_display}
                    </span>
                    <span className="text-xs text-[#00e676] ml-auto font-medium">+{Math.round(task.xp_reward * 1.2)} XP</span>
                  </div>
                </div>
              </div>

              <p className="text-[#8899aa] text-sm leading-relaxed mb-4">
                {task.description_ru}
              </p>

              {/* Бонус */}
              <div className="flex items-center gap-2 p-3 bg-[#ff9500]/5 border border-[#ff9500]/20 rounded-xl mb-4">
                <span>⚡</span>
                <p className="text-[#ff9500] text-xs">
                  Бонус Daily Challenge: +20% XP ({Math.round(task.xp_reward * 1.2)} вместо {task.xp_reward})
                </p>
              </div>

              {/* Статус */}
              {my_completion ? (
                <div className="py-4 rounded-xl text-center bg-[#00e676]/5 border border-[#00e676]/30">
                  <p className="text-[#00e676] font-bold text-lg mb-1">✓ Выполнено!</p>
                  <p className="text-[#8899aa] text-sm">
                    Время: {formatTime(my_completion.time_spent)} · +{my_completion.xp_earned} XP
                  </p>
                </div>
              ) : (
                <>
                  {/* Таймер (если начали) */}
                  <ChallengeTimer
                    started={started}
                    onComplete={(seconds) => completeMutation.mutate(seconds)}
                  />

                  <div className="flex gap-3">
                    {!started ? (
                      <button
                        onClick={() => startMutation.mutate()}
                        disabled={startMutation.isPending}
                        className="flex-1 py-3 rounded-xl font-semibold text-[#0a0e17] bg-[#00d4ff] hover:bg-[#00bfe8] disabled:opacity-50 transition-colors"
                      >
                        {startMutation.isPending ? 'Запуск...' : 'Начать вызов'}
                      </button>
                    ) : null}
                    <Link
                      to={`/tasks/${task.id}`}
                      className="flex-1 py-3 rounded-xl font-semibold text-center border border-[#1e2d45] text-[#8899aa] hover:border-[#00d4ff]/40 hover:text-[#00d4ff] transition-colors"
                    >
                      Открыть задачу →
                    </Link>
                  </div>
                </>
              )}
            </div>

          </div>

          {/* Таблица лидеров */}
          <div className="bg-[#0f1520] border border-[#1e2d45] rounded-2xl p-5">
            <h3 className="text-[#e2e8f0] font-semibold mb-4 flex items-center gap-2">
              <span>🏆</span> Лидеры сегодня
            </h3>
            <Leaderboard entries={leaderboard} />
          </div>

        </div>
      </div>
    </div>
  )
}
