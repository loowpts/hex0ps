import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { api } from '@/api/client'
import TerminalPanel from '@/components/TerminalPanel'

// ─── Types ────────────────────────────────────────────────────────────────────

interface Environment {
  id: string
  label: string
  description: string
  icon: string
}

interface PlaygroundStartResult {
  session_id: number
  environment: string
  environment_display: string
  expires_at: string
  duration_minutes: number
}

// ─── Constants ────────────────────────────────────────────────────────────────

const ENVIRONMENTS: Environment[] = [
  {
    id: 'ubuntu-22',
    label: 'Ubuntu 22.04',
    description: 'Чистая Ubuntu с базовыми инструментами: bash, vim, curl, git...',
    icon: '🐧',
  },
  {
    id: 'ubuntu-22-nginx',
    label: 'Ubuntu 22.04 + nginx',
    description: 'Ubuntu с предустановленным nginx. Практикуй конфигурацию веб-сервера.',
    icon: '🌐',
  },
  {
    id: 'alpine',
    label: 'Alpine Linux',
    description: 'Минималистичный Alpine Linux. Изучай базовые концепции.',
    icon: '🏔️',
  },
]

// ─── Environment Picker ───────────────────────────────────────────────────────

function EnvironmentPicker({
  selected,
  onSelect,
  onStart,
  isLoading,
}: {
  selected: string
  onSelect: (id: string) => void
  onStart: () => void
  isLoading: boolean
}) {
  return (
    <div className="min-h-screen bg-[#0a0e17] p-6 flex items-center justify-center">
      <div className="w-full max-w-2xl">

        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-[#e2e8f0] mb-2">🖥️ Playground</h1>
          <p className="text-[#8899aa]">
            Свободный терминал без задач и ограничений. 30 минут на практику.
          </p>
        </div>

        {/* Environment cards */}
        <div className="space-y-3 mb-6">
          {ENVIRONMENTS.map((env) => (
            <button
              key={env.id}
              onClick={() => onSelect(env.id)}
              className={`w-full text-left p-4 rounded-2xl border transition-all ${
                selected === env.id
                  ? 'border-[#00d4ff] bg-[#00d4ff]/5'
                  : 'border-[#1e2d45] bg-[#0f1520] hover:border-[#00d4ff]/40'
              }`}
            >
              <div className="flex items-center gap-3">
                <span className="text-2xl">{env.icon}</span>
                <div>
                  <p className={`font-semibold text-sm ${selected === env.id ? 'text-[#00d4ff]' : 'text-[#e2e8f0]'}`}>
                    {env.label}
                  </p>
                  <p className="text-xs text-[#8899aa] mt-0.5">{env.description}</p>
                </div>
                {selected === env.id && (
                  <span className="ml-auto text-[#00d4ff] text-lg">◉</span>
                )}
              </div>
            </button>
          ))}
        </div>

        {/* Info */}
        <div className="flex items-start gap-2 p-3 bg-[#ff9500]/5 border border-[#ff9500]/20 rounded-xl mb-6">
          <span>⏱️</span>
          <p className="text-[#ff9500] text-xs">
            Сессия автоматически завершится через 30 минут. XP не начисляется, но это лучшее место для экспериментов!
          </p>
        </div>

        <button
          onClick={onStart}
          disabled={isLoading}
          className="w-full py-4 rounded-2xl font-bold text-lg text-[#0a0e17] bg-[#00d4ff] hover:bg-[#00bfe8] disabled:opacity-50 transition-colors"
        >
          {isLoading ? 'Запускаем...' : 'Запустить Playground →'}
        </button>
      </div>
    </div>
  )
}

// ─── Active Playground ────────────────────────────────────────────────────────

function ActivePlayground({
  session,
  onStop,
}: {
  session: PlaygroundStartResult
  onStop: () => void
}) {
  const [expired, setExpired] = useState(false)

  const expiresAt = new Date(session.expires_at)
  const timeLabel = expiresAt.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })

  return (
    <div className="min-h-screen bg-[#0a0e17] flex flex-col p-4">

      {/* Header */}
      <div className="flex items-center gap-4 mb-4">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-[#00e676] animate-pulse" />
          <span className="text-[#e2e8f0] font-semibold">Playground</span>
          <span className="text-xs px-2 py-0.5 rounded-md bg-[#1e2d45] text-[#8899aa]">
            {session.environment_display}
          </span>
        </div>
        <span className="text-[#4a5568] text-xs ml-2">
          Истекает в {timeLabel}
        </span>
        <button
          onClick={onStop}
          className="ml-auto px-3 py-1.5 rounded-lg text-sm border border-red-500/30 text-red-400 hover:bg-red-500/10 transition-colors"
        >
          Остановить
        </button>
      </div>

      {/* Terminal */}
      {expired ? (
        <div className="flex-1 flex items-center justify-center bg-[#0f1520] border border-[#1e2d45] rounded-2xl">
          <div className="text-center">
            <p className="text-[#e2e8f0] text-xl font-bold mb-2">⏰ Сессия истекла</p>
            <p className="text-[#8899aa] text-sm mb-4">30 минут вышли. Надеюсь, было продуктивно!</p>
            <button
              onClick={onStop}
              className="px-6 py-3 rounded-xl font-semibold text-[#0a0e17] bg-[#00d4ff] hover:bg-[#00bfe8] transition-colors"
            >
              Новая сессия
            </button>
          </div>
        </div>
      ) : (
        <div className="flex-1 min-h-0">
          <TerminalPanel
            sessionId={String(session.session_id)}
            wsPath="playground"
            onExpired={() => setExpired(true)}
          />
        </div>
      )}
    </div>
  )
}

// ─── Main ─────────────────────────────────────────────────────────────────────

export default function PlaygroundPage() {
  const [selectedEnv, setSelectedEnv] = useState('ubuntu-22')
  const [session, setSession] = useState<PlaygroundStartResult | null>(null)

  const stopMutation = useMutation({
    mutationFn: (sessionId: number) =>
      api.delete(`/playground/${sessionId}/stop/`).then((r) => r.data),
    onSuccess: () => setSession(null),
  })

  const startMutation = useMutation<PlaygroundStartResult>({
    mutationFn: () =>
      api.post('/playground/start/', { environment: selectedEnv }).then((r) => r.data),
    onSuccess: (data) => setSession(data),
  })

  if (session) {
    return (
      <ActivePlayground
        session={session}
        onStop={() => stopMutation.mutate(session.session_id)}
      />
    )
  }

  return (
    <EnvironmentPicker
      selected={selectedEnv}
      onSelect={setSelectedEnv}
      onStart={() => startMutation.mutate()}
      isLoading={startMutation.isPending}
    />
  )
}
