import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/api/client'
import type { Recording } from '@/types'
import { format } from 'date-fns'
import { ru } from 'date-fns/locale'

// ─── Hook ─────────────────────────────────────────────────────────────────────

function useRecording(shareId: string) {
  return useQuery<Recording>({
    queryKey: ['recording', shareId],
    queryFn: () => api.get(`/recordings/${shareId}/`).then((r) => r.data),
    enabled: !!shareId,
    retry: false,
  })
}

// ─── Terminal Replay Player ───────────────────────────────────────────────────

function TerminalReplayPlayer({
  recording,
  playing,
  speed,
}: {
  recording: Recording
  playing: boolean
  speed: number
}) {
  // In a real implementation this would use @xterm/xterm to replay the events.
  // Here we show a placeholder that communicates the state.
  return (
    <div className="w-full bg-[#050810] rounded-xl border border-[#1e2d45] overflow-hidden">
      <div className="flex items-center gap-2 px-4 py-3 border-b border-[#1e2d45]">
        <div className="w-3 h-3 rounded-full bg-red-500" />
        <div className="w-3 h-3 rounded-full bg-yellow-500" />
        <div className="w-3 h-3 rounded-full bg-green-500" />
        <span className="ml-2 text-[#8899aa] text-xs font-mono">
          replay:{recording.share_id.slice(0, 8)} — {recording.cols}x{recording.rows}
        </span>
        {playing && (
          <div className="ml-auto flex items-center gap-1.5">
            <div className="w-1.5 h-1.5 rounded-full bg-[#00e676] animate-pulse" />
            <span className="text-xs text-[#00e676]">{speed}x</span>
          </div>
        )}
      </div>
      <div
        className="flex items-center justify-center text-[#8899aa] font-mono text-sm"
        style={{ height: 320 }}
      >
        {playing ? (
          <span className="animate-pulse">▶ Воспроизведение записи...</span>
        ) : (
          <span>⏸ Нажмите Play для воспроизведения</span>
        )}
      </div>
    </div>
  )
}

// ─── Progress Bar ─────────────────────────────────────────────────────────────

function ProgressBar({ duration, playing: _playing }: { duration: number; playing: boolean }) {
  const [progress, setProgress] = useState(0)

  // In a real implementation, this would track actual playback progress
  return (
    <div className="space-y-1">
      <div
        className="h-2 bg-[#1e2d45] rounded-full overflow-hidden cursor-pointer"
        onClick={(e) => {
          const rect = (e.currentTarget as HTMLElement).getBoundingClientRect()
          const pct = (e.clientX - rect.left) / rect.width
          setProgress(Math.max(0, Math.min(100, pct * 100)))
        }}
      >
        <div
          className="h-full bg-[#00d4ff] rounded-full transition-all"
          style={{ width: `${progress}%` }}
        />
      </div>
      <div className="flex justify-between text-xs text-[#8899aa]">
        <span>{Math.floor((progress / 100) * duration)}с</span>
        <span>{duration}с</span>
      </div>
    </div>
  )
}

// ─── Main ────────────────────────────────────────────────────────────────────

const SPEED_OPTIONS = [0.5, 1, 2, 3] as const
type Speed = (typeof SPEED_OPTIONS)[number]

export default function ReplayRecording() {
  const { shareId } = useParams<{ shareId: string }>()
  const { data: recording, isLoading, error } = useRecording(shareId ?? '')

  const [playing, setPlaying] = useState(false)
  const [speed, setSpeed] = useState<Speed>(1)
  const [copied, setCopied] = useState(false)

  const handleCopyUrl = () => {
    navigator.clipboard.writeText(window.location.href)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#0a0e17] flex items-center justify-center">
        <div className="animate-pulse space-y-4 w-full max-w-3xl px-6">
          <div className="h-8 bg-[#1e2d45] rounded w-1/2" />
          <div className="h-80 bg-[#1e2d45] rounded-2xl" />
          <div className="h-16 bg-[#1e2d45] rounded-xl" />
        </div>
      </div>
    )
  }

  if (error || !recording) {
    return (
      <div className="min-h-screen bg-[#0a0e17] flex items-center justify-center px-4">
        <div className="text-center max-w-md">
          <div className="text-6xl mb-4">📼</div>
          <h1 className="text-2xl font-bold text-[#e2e8f0] mb-2">Запись не найдена</h1>
          <p className="text-[#8899aa]">
            Запись <span className="text-[#00d4ff] font-mono">{shareId}</span> не существует или была удалена.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#0a0e17] p-6 max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-[#e2e8f0] mb-1">
            {recording.task.title_ru}
          </h1>
          <div className="flex flex-wrap items-center gap-3 text-sm text-[#8899aa]">
            <span className="flex items-center gap-1">
              👤 <span className="text-[#00d4ff]">{recording.author}</span>
            </span>
            <span>·</span>
            <span>{format(new Date(recording.created_at), 'd MMM yyyy', { locale: ru })}</span>
            <span>·</span>
            <span>{recording.duration_seconds}с</span>
            <span>·</span>
            <span className="uppercase text-xs tracking-wide">{recording.task.category}</span>
          </div>
        </div>

        <button
          onClick={handleCopyUrl}
          className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium border border-[#1e2d45] text-[#8899aa] hover:border-[#00d4ff]/40 hover:text-[#00d4ff] transition-colors shrink-0"
        >
          {copied ? (
            <>
              <svg className="w-4 h-4 text-[#00e676]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Скопировано!
            </>
          ) : (
            <>
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
              </svg>
              Поделиться
            </>
          )}
        </button>
      </div>

      {/* Terminal Player */}
      <TerminalReplayPlayer
        recording={recording}
        playing={playing}
        speed={speed}
      />

      {/* Controls */}
      <div className="bg-[#0f1520] border border-[#1e2d45] rounded-2xl p-4 space-y-4">
        {/* Progress */}
        <ProgressBar duration={recording.duration_seconds} playing={playing} />

        {/* Buttons */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {/* Play/Pause */}
            <button
              onClick={() => setPlaying((v) => !v)}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl font-semibold text-sm text-[#0a0e17] bg-[#00d4ff] hover:bg-[#00bfe8] transition-colors"
            >
              {playing ? (
                <>
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
                  </svg>
                  Пауза
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M8 5v14l11-7z"/>
                  </svg>
                  Воспроизвести
                </>
              )}
            </button>

            {/* Restart */}
            <button
              onClick={() => setPlaying(false)}
              className="flex items-center gap-1.5 px-3 py-2.5 rounded-xl text-sm border border-[#1e2d45] text-[#8899aa] hover:border-[#1e2d45] hover:text-[#e2e8f0] transition-colors"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Начало
            </button>
          </div>

          {/* Speed selector */}
          <div className="flex items-center gap-1">
            <span className="text-[#8899aa] text-xs mr-1">Скорость:</span>
            {SPEED_OPTIONS.map((s) => (
              <button
                key={s}
                onClick={() => setSpeed(s)}
                className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-colors ${
                  speed === s
                    ? 'bg-[#00d4ff]/20 text-[#00d4ff] border border-[#00d4ff]/40'
                    : 'bg-[#0a0e17] text-[#8899aa] border border-[#1e2d45] hover:border-[#00d4ff]/30'
                }`}
              >
                {s}x
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Info */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: 'Автор', value: recording.author },
          { label: 'Задача', value: `#${recording.task.id}` },
          { label: 'Длительность', value: `${recording.duration_seconds}с` },
          { label: 'Терминал', value: `${recording.cols}×${recording.rows}` },
        ].map((item) => (
          <div key={item.label} className="bg-[#0f1520] border border-[#1e2d45] rounded-xl p-3">
            <p className="text-[#8899aa] text-xs mb-1">{item.label}</p>
            <p className="text-[#e2e8f0] text-sm font-medium">{item.value}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
