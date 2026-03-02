import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import { api } from '@/api/client'

// ─── Types ────────────────────────────────────────────────────────────────────

interface CollabSession {
  id: number
  invite_token: string
  owner: string
  task: {
    id: number
    title_ru: string
    category: string
    category_display: string
    difficulty: string
    difficulty_display: string
  }
  current_controller: string
  observers: string[]
  created_at: string
  expires_at: string
}

// ─── Hooks ────────────────────────────────────────────────────────────────────

function useCollabSession(inviteToken: string) {
  return useQuery<CollabSession>({
    queryKey: ['collab', inviteToken],
    queryFn: () => api.get(`/collab/${inviteToken}/`).then((r) => r.data),
    enabled: !!inviteToken,
    retry: false,
    refetchInterval: 5000,
  })
}

function useJoinCollab() {
  return useMutation<{ joined: boolean; role: string }, Error, string>({
    mutationFn: (inviteToken) =>
      api.post(`/collab/${inviteToken}/join/`).then((r) => r.data),
  })
}

function useRequestControl() {
  return useMutation<{ granted: boolean }, Error, string>({
    mutationFn: (inviteToken) =>
      api.post(`/collab/${inviteToken}/request-control/`).then((r) => r.data),
  })
}

// ─── Terminal placeholder ─────────────────────────────────────────────────────

function CollabTerminal({
  isObserver,
  ownerName,
}: {
  isObserver: boolean
  ownerName: string
}) {
  return (
    <div className="w-full bg-[#050810] rounded-xl border border-[#1e2d45] overflow-hidden">
      <div className="flex items-center gap-2 px-4 py-3 border-b border-[#1e2d45]">
        <div className="w-3 h-3 rounded-full bg-red-500" />
        <div className="w-3 h-3 rounded-full bg-yellow-500" />
        <div className="w-3 h-3 rounded-full bg-green-500" />
        <span className="ml-2 text-[#8899aa] text-xs font-mono">
          collab — {ownerName}
        </span>
        {isObserver && (
          <span className="ml-auto text-xs px-2 py-0.5 rounded bg-[#8899aa]/10 text-[#8899aa] border border-[#8899aa]/20">
            Только просмотр
          </span>
        )}
      </div>
      <div
        className="flex items-center justify-center text-[#8899aa] font-mono text-sm"
        style={{ height: 400 }}
      >
        <div className="text-center">
          <p className="mb-2">
            {isObserver
              ? '👁 Режим наблюдателя — следите за терминалом'
              : '⌨ Ожидание подключения к сессии...'}
          </p>
          <p className="text-xs text-[#4a5568]">WebSocket-сессия</p>
        </div>
      </div>
    </div>
  )
}

// ─── Observer Badge ───────────────────────────────────────────────────────────

function ObserverBadge({ username }: { username: string }) {
  return (
    <div className="flex items-center gap-2 px-3 py-1.5 bg-[#0a0e17] border border-[#1e2d45] rounded-lg">
      <div className="w-2 h-2 rounded-full bg-[#00e676]" />
      <span className="text-[#e2e8f0] text-xs">{username}</span>
    </div>
  )
}

// ─── Main ────────────────────────────────────────────────────────────────────

const DIFF_COLORS: Record<string, string> = {
  beginner: 'bg-[#00e676]/10 text-[#00e676] border-[#00e676]/30',
  intermediate: 'bg-[#ff9500]/10 text-[#ff9500] border-[#ff9500]/30',
  advanced: 'bg-red-500/10 text-red-400 border-red-400/30',
}

export default function CollabPage() {
  const { inviteToken } = useParams<{ inviteToken: string }>()
  const { data: session, isLoading, error } = useCollabSession(inviteToken ?? '')
  const joinCollab = useJoinCollab()
  const requestControl = useRequestControl()

  const [joined, setJoined] = useState(false)
  const [role, setRole] = useState<'observer' | 'participant'>('observer')
  const [controlRequested, setControlRequested] = useState(false)

  const handleJoin = () => {
    if (!inviteToken) return
    joinCollab.mutate(inviteToken, {
      onSuccess: (data) => {
        setJoined(true)
        setRole(data.role === 'participant' ? 'participant' : 'observer')
      },
    })
  }

  const handleRequestControl = () => {
    if (!inviteToken) return
    requestControl.mutate(inviteToken, {
      onSuccess: () => {
        setControlRequested(true)
      },
    })
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#0a0e17] flex items-center justify-center">
        <div className="animate-pulse space-y-4 w-full max-w-3xl px-6">
          <div className="h-24 bg-[#1e2d45] rounded-2xl" />
          <div className="h-80 bg-[#1e2d45] rounded-2xl" />
        </div>
      </div>
    )
  }

  if (error || !session) {
    return (
      <div className="min-h-screen bg-[#0a0e17] flex items-center justify-center px-4">
        <div className="text-center max-w-md">
          <div className="text-6xl mb-4">🔗</div>
          <h1 className="text-2xl font-bold text-[#e2e8f0] mb-2">Сессия не найдена</h1>
          <p className="text-[#8899aa]">
            Ссылка для совместной работы недействительна или сессия завершена.
          </p>
        </div>
      </div>
    )
  }

  const diffClass = DIFF_COLORS[session.task.difficulty] ?? 'bg-[#1e2d45] text-[#8899aa] border-[#1e2d45]'
  const isObserver = role === 'observer'

  return (
    <div className="min-h-screen bg-[#0a0e17] p-6 max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-start gap-4">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <div className="w-2 h-2 rounded-full bg-[#00e676] animate-pulse" />
            <span className="text-xs text-[#00e676] font-medium">Активная сессия</span>
          </div>
          <h1 className="text-xl font-bold text-[#e2e8f0] mb-1">
            {session.task.title_ru}
          </h1>
          <div className="flex flex-wrap items-center gap-2">
            <span className={`text-xs px-2 py-0.5 rounded-md border ${diffClass}`}>
              {session.task.difficulty_display}
            </span>
            <span className="text-xs text-[#8899aa] uppercase tracking-wide">
              {session.task.category_display}
            </span>
          </div>
        </div>

        {/* Info */}
        <div className="bg-[#0f1520] border border-[#1e2d45] rounded-xl p-4 min-w-[200px]">
          <div className="space-y-2">
            <div>
              <p className="text-[#8899aa] text-xs">Владелец сессии</p>
              <p className="text-[#00d4ff] text-sm font-semibold">{session.owner}</p>
            </div>
            <div>
              <p className="text-[#8899aa] text-xs">Управляет</p>
              <p className="text-[#e2e8f0] text-sm font-medium">
                {session.current_controller}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Control indicator */}
      <div className="flex items-center justify-between bg-[#0f1520] border border-[#1e2d45] rounded-xl px-4 py-3">
        <div className="flex items-center gap-2">
          <span className="text-sm text-[#8899aa]">Управляет:</span>
          <span className="text-sm font-semibold text-[#00d4ff]">
            {session.current_controller}
          </span>
        </div>

        {joined && isObserver && !controlRequested && (
          <button
            onClick={handleRequestControl}
            className="px-4 py-1.5 rounded-lg text-xs font-medium bg-[#ff9500]/10 text-[#ff9500] border border-[#ff9500]/30 hover:bg-[#ff9500]/20 transition-colors"
          >
            Запросить управление
          </button>
        )}
        {controlRequested && (
          <span className="text-xs text-[#8899aa]">Запрос отправлен...</span>
        )}
      </div>

      {/* Terminal */}
      {joined ? (
        <CollabTerminal isObserver={isObserver} ownerName={session.owner} />
      ) : (
        /* Join screen */
        <div className="bg-[#0f1520] border border-[#1e2d45] rounded-2xl p-8 text-center">
          <div className="text-5xl mb-4">👥</div>
          <h2 className="text-xl font-bold text-[#e2e8f0] mb-2">
            Совместная работа
          </h2>
          <p className="text-[#8899aa] mb-6 max-w-sm mx-auto">
            Вас пригласили наблюдать за решением задачи пользователя{' '}
            <span className="text-[#00d4ff]">{session.owner}</span>. Подключитесь как наблюдатель.
          </p>

          <button
            onClick={handleJoin}
            disabled={joinCollab.isPending}
            className="px-6 py-3 rounded-xl font-semibold text-[#0a0e17] bg-[#00d4ff] hover:bg-[#00bfe8] disabled:opacity-50 transition-colors"
          >
            {joinCollab.isPending ? 'Подключаемся...' : 'Подключиться как наблюдатель'}
          </button>
        </div>
      )}

      {/* Observers */}
      {joined && session.observers.length > 0 && (
        <div className="bg-[#0f1520] border border-[#1e2d45] rounded-xl p-4">
          <p className="text-[#8899aa] text-xs mb-3">
            Наблюдатели ({session.observers.length})
          </p>
          <div className="flex flex-wrap gap-2">
            {session.observers.map((username) => (
              <ObserverBadge key={username} username={username} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
