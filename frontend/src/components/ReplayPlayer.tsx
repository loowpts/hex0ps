/**
 * ReplayPlayer — воспроизводит эталонное решение задачи в xterm.js.
 * Поддерживает скорость 0.5x / 1x / 2x и пошаговый режим.
 */
import { useEffect, useRef, useState, useCallback } from 'react'
import { Terminal } from '@xterm/xterm'
import type { ITheme } from '@xterm/xterm'
import { FitAddon } from '@xterm/addon-fit'
import '@xterm/xterm/css/xterm.css'
import { useTerminalSettings } from '@/hooks/useTerminalSettings'

// ─── Types ────────────────────────────────────────────────────────────────────

interface Step {
  command: string
  explanation: string
}

interface Props {
  steps: Step[]
}

type Speed = 0.5 | 1 | 2

// ─── Helpers ─────────────────────────────────────────────────────────────────

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

async function typeCommand(term: Terminal, command: string, speed: Speed): Promise<void> {
  // Печатаем команду посимвольно как настоящий ввод
  const delay = Math.round(60 / speed)
  for (const char of command) {
    term.write(char)
    await sleep(delay)
  }
  await sleep(300 / speed)
  term.write('\r\n')
}

// ─── Component ────────────────────────────────────────────────────────────────

export default function ReplayPlayer({ steps }: Props) {
  const containerRef = useRef<HTMLDivElement>(null)
  const termRef = useRef<Terminal | null>(null)
  const fitRef = useRef<FitAddon | null>(null)
  const playingRef = useRef(false)
  const abortRef = useRef(false)

  const [currentStep, setCurrentStep] = useState(-1)
  const [isPlaying, setIsPlaying] = useState(false)
  const [isFinished, setIsFinished] = useState(false)
  const [speed, setSpeed] = useState<Speed>(1)

  const { fontSize, theme } = useTerminalSettings()

  // --- Инициализация терминала ---
  useEffect(() => {
    if (!containerRef.current || termRef.current) return

    const term = new Terminal({
      fontFamily: '"JetBrains Mono", monospace',
      fontSize,
      theme: theme as ITheme,
      cursorBlink: false,
      disableStdin: true,
      convertEol: true,
      scrollback: 2000,
    })
    const fitAddon = new FitAddon()
    term.loadAddon(fitAddon)
    term.open(containerRef.current)
    fitAddon.fit()

    termRef.current = term
    fitRef.current = fitAddon

    // Подсказка
    term.writeln('\x1b[36m# Эталонное решение\x1b[0m')
    term.writeln('\x1b[90m# Нажмите Play для воспроизведения\x1b[0m')
    term.writeln('')

    return () => {
      abortRef.current = true
      term.dispose()
      termRef.current = null
      fitRef.current = null
    }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  // --- Обновление настроек ---
  useEffect(() => {
    if (!termRef.current) return
    termRef.current.options.fontSize = fontSize
    termRef.current.options.theme = theme as ITheme
    fitRef.current?.fit()
  }, [fontSize, theme])

  // --- Воспроизведение шагов ---
  const playSteps = useCallback(async () => {
    const term = termRef.current
    if (!term || !steps.length) return

    abortRef.current = false
    playingRef.current = true
    setIsPlaying(true)
    setIsFinished(false)
    setCurrentStep(0)

    // Очищаем терминал
    term.clear()
    term.writeln('\x1b[36m# Эталонное решение\x1b[0m')
    term.writeln('')

    for (let i = 0; i < steps.length; i++) {
      if (abortRef.current) break

      setCurrentStep(i)
      const step = steps[i]

      // Заголовок шага
      term.writeln(`\x1b[33m# Шаг ${i + 1}: ${step.explanation}\x1b[0m`)
      await sleep(400 / speed)

      // Промпт и команда
      term.write('\x1b[32mdevops@sandbox\x1b[0m:\x1b[34m~\x1b[0m$ ')
      await sleep(200 / speed)

      await typeCommand(term, step.command, speed)

      // Имитируем выполнение
      await sleep(600 / speed)

      // Разделитель между шагами
      if (i < steps.length - 1) {
        term.writeln('')
      }
    }

    if (!abortRef.current) {
      term.writeln('')
      term.writeln('\x1b[32m# ✓ Решение завершено\x1b[0m')
      setIsFinished(true)
    }

    playingRef.current = false
    setIsPlaying(false)
    setCurrentStep(-1)
  }, [steps, speed])

  // --- Пауза ---
  const handlePause = () => {
    abortRef.current = true
    playingRef.current = false
    setIsPlaying(false)
  }

  // --- Сброс ---
  const handleReset = () => {
    abortRef.current = true
    playingRef.current = false
    setIsPlaying(false)
    setIsFinished(false)
    setCurrentStep(-1)

    const term = termRef.current
    if (term) {
      term.clear()
      term.writeln('\x1b[36m# Эталонное решение\x1b[0m')
      term.writeln('\x1b[90m# Нажмите Play для воспроизведения\x1b[0m')
      term.writeln('')
    }
  }

  const SPEEDS: Speed[] = [0.5, 1, 2]

  return (
    <div className="space-y-3">
      {/* Терминал */}
      <div
        className="w-full bg-[#050810] rounded-xl border border-[#1e2d45] overflow-hidden"
        style={{ height: 280 }}
      >
        <div className="flex items-center gap-2 px-4 py-2 border-b border-[#1e2d45]">
          <div className="w-3 h-3 rounded-full bg-red-500" />
          <div className="w-3 h-3 rounded-full bg-yellow-500" />
          <div className="w-3 h-3 rounded-full bg-green-500" />
          <span className="ml-2 text-[#8899aa] text-xs font-mono">replay</span>
          {isPlaying && (
            <div className="ml-auto flex items-center gap-1.5">
              <div className="w-1.5 h-1.5 rounded-full bg-[#00e676] animate-pulse" />
              <span className="text-xs text-[#00e676]">{speed}x</span>
            </div>
          )}
        </div>
        <div ref={containerRef} className="p-1" style={{ height: 'calc(100% - 37px)' }} />
      </div>

      {/* Управление */}
      <div className="flex items-center gap-3">
        {isPlaying ? (
          <button
            onClick={handlePause}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-semibold text-[#0a0e17] bg-[#ff9500] hover:bg-[#e08500] transition-colors"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z" />
            </svg>
            Пауза
          </button>
        ) : (
          <button
            onClick={playSteps}
            disabled={isFinished && !steps.length}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-semibold text-[#0a0e17] bg-[#00d4ff] hover:bg-[#00bfe8] disabled:opacity-50 transition-colors"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8 5v14l11-7z" />
            </svg>
            {isFinished ? 'Повторить' : 'Воспроизвести'}
          </button>
        )}

        <button
          onClick={handleReset}
          className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-sm border border-[#1e2d45] text-[#8899aa] hover:text-[#e2e8f0] transition-colors"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Сброс
        </button>

        {/* Скорость */}
        <div className="ml-auto flex items-center gap-1">
          <span className="text-[#8899aa] text-xs mr-1">Скорость:</span>
          {SPEEDS.map((s) => (
            <button
              key={s}
              onClick={() => setSpeed(s)}
              disabled={isPlaying}
              className={`px-2 py-1 rounded-lg text-xs font-medium transition-colors ${
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

      {/* Текущий шаг */}
      {currentStep >= 0 && currentStep < steps.length && (
        <div className="bg-[#0f1520] border border-[#1e2d45] rounded-xl p-3">
          <p className="text-[#8899aa] text-xs mb-1">
            Шаг {currentStep + 1} из {steps.length}
          </p>
          <p className="text-[#e2e8f0] text-sm">{steps[currentStep].explanation}</p>
          <code className="text-[#00e676] text-sm font-mono block mt-1">
            $ {steps[currentStep].command}
          </code>
        </div>
      )}

      {/* Список всех шагов */}
      <div className="space-y-2">
        <p className="text-[#8899aa] text-xs font-medium uppercase tracking-wider">
          Шаги решения
        </p>
        {steps.map((step, i) => (
          <div
            key={i}
            className={`flex gap-3 p-3 rounded-xl border transition-colors ${
              i === currentStep
                ? 'border-[#00d4ff]/40 bg-[#00d4ff]/5'
                : i < currentStep
                ? 'border-[#00e676]/20 bg-[#00e676]/5'
                : 'border-[#1e2d45] bg-[#0f1520]'
            }`}
          >
            <div
              className={`w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold shrink-0 mt-0.5 ${
                i < currentStep
                  ? 'bg-[#00e676] text-[#0a0e17]'
                  : i === currentStep
                  ? 'bg-[#00d4ff] text-[#0a0e17]'
                  : 'bg-[#1e2d45] text-[#8899aa]'
              }`}
            >
              {i < currentStep ? '✓' : i + 1}
            </div>
            <div className="min-w-0">
              <code className="text-[#00e676] text-xs font-mono block truncate">
                $ {step.command}
              </code>
              <p className="text-[#8899aa] text-xs mt-0.5 leading-relaxed">
                {step.explanation}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
