/**
 * TerminalPanel — полноценный терминал на xterm.js с WebSocket подключением.
 * Подключается к ws/terminal/{sessionId}/?token={accessToken}
 * Поддерживает: темы, шрифты, resize, историю команд.
 */
import { useEffect, useRef, useCallback } from 'react'
import { Terminal } from '@xterm/xterm'
import type { ITheme } from '@xterm/xterm'
import { FitAddon } from '@xterm/addon-fit'
import { WebLinksAddon } from '@xterm/addon-web-links'
import '@xterm/xterm/css/xterm.css'
import { useAuthStore, getStoredToken } from '@/store/auth'
import { useTerminalSettings, TERMINAL_THEMES } from '@/hooks/useTerminalSettings'
import { api } from '@/api/client'
import type { TerminalTheme } from '@/types'

// ─── Props ────────────────────────────────────────────────────────────────────

interface Props {
  sessionId: string
  onDangerousCommand?: (cmd: string) => void
  onExpired?: () => void
  readOnly?: boolean
  wsPath?: string  // 'terminal' | 'playground' (default: 'terminal')
}

// ─── WebSocket URL helpers ────────────────────────────────────────────────────

function buildWsUrl(sessionId: string, param: string, value: string, wsPath = 'terminal'): string {
  const proto = window.location.protocol === 'https:' ? 'wss' : 'ws'
  const host = import.meta.env.VITE_WS_URL ?? window.location.host
  return `${proto}://${host}/ws/${wsPath}/${sessionId}/?${param}=${value}`
}

/** Получает одноразовый ticket из Redis через защищённый HTTP-запрос. */
async function fetchWsTicket(): Promise<string | null> {
  try {
    const { data } = await api.post<{ ticket: string }>('/terminal/ticket/')
    return data.ticket
  } catch {
    return null
  }
}

// ─── Component ────────────────────────────────────────────────────────────────

export default function TerminalPanel({
  sessionId,
  onDangerousCommand,
  onExpired,
  readOnly = false,
  wsPath = 'terminal',
}: Props) {
  const containerRef = useRef<HTMLDivElement>(null)
  const termRef = useRef<Terminal | null>(null)
  const fitRef = useRef<FitAddon | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const resizeObserverRef = useRef<ResizeObserver | null>(null)

  const storeToken = useAuthStore((s) => s.accessToken)
  const accessToken = storeToken ?? getStoredToken()
  const { fontSize, theme } = useTerminalSettings()

  // --- Инициализация терминала ---
  const initTerminal = useCallback(() => {
    if (!containerRef.current || termRef.current) return

    const term = new Terminal({
      fontFamily: '"JetBrains Mono", "Fira Code", monospace',
      fontSize,
      theme: theme as ITheme,
      cursorBlink: true,
      cursorStyle: 'block',
      scrollback: 5000,
      convertEol: true,
      disableStdin: readOnly,
      allowProposedApi: true,
    })

    const fitAddon = new FitAddon()
    const webLinksAddon = new WebLinksAddon()

    term.loadAddon(fitAddon)
    term.loadAddon(webLinksAddon)
    term.open(containerRef.current)
    fitAddon.fit()

    termRef.current = term
    fitRef.current = fitAddon

    // Приветственное сообщение
    if (!readOnly) {
      term.writeln('\x1b[36m╔══════════════════════════════════╗\x1b[0m')
      term.writeln('\x1b[36m║  DevOps Learning Platform       ║\x1b[0m')
      term.writeln('\x1b[36m╚══════════════════════════════════╝\x1b[0m')
      term.writeln('')
    }

    return term
  }, [fontSize, theme, readOnly])

  // --- WebSocket подключение ---
  const connectWs = useCallback(async (term: Terminal) => {
    if (!accessToken || !sessionId) return
    if (wsRef.current?.readyState === WebSocket.OPEN) return

    // Получаем одноразовый ticket — JWT не попадает в URL и логи сервера
    const ticket = await fetchWsTicket()
    const wsUrl = ticket
      ? buildWsUrl(sessionId, 'ticket', ticket, wsPath)
      : buildWsUrl(sessionId, 'token', accessToken, wsPath) // fallback если Redis недоступен

    const ws = new WebSocket(wsUrl)
    wsRef.current = ws

    ws.onopen = () => {
      // Отправляем начальный размер терминала
      const { cols, rows } = term
      ws.send(JSON.stringify({ type: 'resize', cols, rows }))
    }

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data)
        handleMessage(msg, term)
      } catch {
        // Если не JSON — выводим напрямую (raw output)
        term.write(event.data)
      }
    }

    ws.onclose = (event) => {
      if (event.code !== 1000) {
        term.writeln('\r\n\x1b[31m[Соединение разорвано]\x1b[0m')
      }
    }

    ws.onerror = () => {
      term.writeln('\r\n\x1b[31m[Ошибка WebSocket соединения]\x1b[0m')
    }

    // Обработка ввода пользователя
    if (!readOnly) {
      term.onData((data) => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: 'input', data }))
        }
      })
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [accessToken, sessionId, readOnly, wsPath])

  // --- Обработка сообщений от сервера ---
  const handleMessage = useCallback(
    (msg: Record<string, unknown>, term: Terminal) => {
      switch (msg.type) {
        case 'output':
          term.write(msg.data as string)
          break

        case 'error':
          term.writeln(`\r\n\x1b[31m[Ошибка: ${msg.message}]\x1b[0m`)
          break

        case 'timer':
          // Таймер обновляется через отдельный компонент TaskTimer
          break

        case 'warning':
          // Опасная команда — уведомляем родительский компонент
          onDangerousCommand?.(msg.command as string)
          break

        case 'expired':
          term.writeln('\r\n\x1b[33m[Время истекло! Сессия завершена.]\x1b[0m')
          onExpired?.()
          break

        case 'history':
          // Восстановление истории при реконнекте
          if (Array.isArray(msg.commands)) {
            // История уже в терминале через output
          }
          break

        default:
          break
      }
    },
    [onDangerousCommand, onExpired]
  )

  // --- ResizeObserver для авторесайза ---
  const setupResize = useCallback((term: Terminal, fitAddon: FitAddon) => {
    const observer = new ResizeObserver(() => {
      try {
        fitAddon.fit()
        const { cols, rows } = term
        if (wsRef.current?.readyState === WebSocket.OPEN) {
          wsRef.current.send(JSON.stringify({ type: 'resize', cols, rows }))
        }
      } catch {
        // Игнорируем ошибки resize
      }
    })

    if (containerRef.current) {
      observer.observe(containerRef.current)
    }
    resizeObserverRef.current = observer
  }, [])

  // --- Монтирование ---
  // Откладываем инит в requestAnimationFrame: xterm.js внутри term.open()
  // запускает setTimeout для Viewport, который упадёт если контейнер
  // ещё не прошёл layout (dimensions === undefined).
  useEffect(() => {
    let cleanup: (() => void) | undefined
    const frame = requestAnimationFrame(() => {
      const term = initTerminal()
      if (!term) return

      const fitAddon = fitRef.current!
      connectWs(term)
      setupResize(term, fitAddon)

      cleanup = () => {
        wsRef.current?.close(1000)
        wsRef.current = null
        resizeObserverRef.current?.disconnect()
        term.dispose()
        termRef.current = null
        fitRef.current = null
      }
    })

    return () => {
      cancelAnimationFrame(frame)
      cleanup?.()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId])

  // --- Обновление настроек терминала ---
  useEffect(() => {
    if (!termRef.current) return
    termRef.current.options.fontSize = fontSize
    termRef.current.options.theme = theme as ITheme
    fitRef.current?.fit()
  }, [fontSize, theme])

  // --- Фокус на терминал ---
  const focusTerminal = () => {
    termRef.current?.focus()
  }

  return (
    <div
      className="w-full h-full flex flex-col bg-[#050810] rounded-xl border border-[#1e2d45] overflow-hidden"
      onClick={focusTerminal}
    >
      {/* Шапка в стиле macOS */}
      <div className="flex items-center gap-2 px-4 py-2.5 border-b border-[#1e2d45] shrink-0 select-none">
        <div className="w-3 h-3 rounded-full bg-[#ff5f57] hover:bg-[#e0443e] transition-colors cursor-pointer" />
        <div className="w-3 h-3 rounded-full bg-[#ffbc2e] hover:bg-[#d4a017] transition-colors cursor-pointer" />
        <div className="w-3 h-3 rounded-full bg-[#28c840] hover:bg-[#1aab29] transition-colors cursor-pointer" />
        <span className="ml-3 text-[#8899aa] text-xs font-mono">
          {readOnly ? 'replay' : `session:${sessionId?.slice(0, 8) ?? 'disconnected'}`}
        </span>
        {readOnly && (
          <span className="ml-auto text-xs px-2 py-0.5 rounded bg-[#8899aa]/10 text-[#8899aa] border border-[#8899aa]/20">
            только чтение
          </span>
        )}
      </div>

      {/* Контейнер xterm.js */}
      <div
        ref={containerRef}
        className="flex-1 min-h-0 p-1"
        style={{ overflow: 'hidden' }}
      />
    </div>
  )
}

// ─── Экспорт настроек для внешнего использования ─────────────────────────────

export { TERMINAL_THEMES }
export type { TerminalTheme }
