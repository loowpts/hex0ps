/**
 * AiChat — боковая панель чата с AI-ассистентом.
 * Отправляет запросы на POST /api/ai/ask/ с контекстом задачи.
 * Анимированное открытие/закрытие.
 */
import { useState, useRef, useEffect, useCallback } from 'react'
import { api } from '@/api/client'

// ─── Types ────────────────────────────────────────────────────────────────────

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

interface Props {
  taskId: number
  taskTitle: string
  isOpen: boolean
  onClose: () => void
}

// ─── Message bubble ───────────────────────────────────────────────────────────

function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === 'user'
  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      {/* Аватар */}
      <div
        className={`w-7 h-7 rounded-full shrink-0 flex items-center justify-center text-xs font-bold mt-0.5 ${
          isUser
            ? 'bg-[#00d4ff]/20 text-[#00d4ff]'
            : 'bg-[#00e676]/20 text-[#00e676]'
        }`}
      >
        {isUser ? 'Я' : 'AI'}
      </div>

      {/* Текст */}
      <div
        className={`max-w-[85%] rounded-2xl px-3.5 py-2.5 text-sm leading-relaxed ${
          isUser
            ? 'bg-[#00d4ff]/15 text-[#e2e8f0] rounded-tr-sm'
            : 'bg-[#1e2d45] text-[#e2e8f0] rounded-tl-sm'
        }`}
      >
        <p className="whitespace-pre-wrap">{message.content}</p>
        <p className="text-[10px] text-[#4a5568] mt-1 text-right">
          {message.timestamp.toLocaleTimeString('ru-RU', {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </p>
      </div>
    </div>
  )
}

// ─── Typing indicator ─────────────────────────────────────────────────────────

function TypingIndicator() {
  return (
    <div className="flex gap-3">
      <div className="w-7 h-7 rounded-full shrink-0 flex items-center justify-center text-xs font-bold bg-[#00e676]/20 text-[#00e676]">
        AI
      </div>
      <div className="bg-[#1e2d45] rounded-2xl rounded-tl-sm px-4 py-3 flex items-center gap-1">
        {[0, 1, 2].map((i) => (
          <span
            key={i}
            className="w-1.5 h-1.5 rounded-full bg-[#8899aa] animate-bounce"
            style={{ animationDelay: `${i * 0.15}s` }}
          />
        ))}
      </div>
    </div>
  )
}

// ─── Component ────────────────────────────────────────────────────────────────

export default function AiChat({ taskId, taskTitle, isOpen, onClose }: Props) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: `Привет! Я помогу тебе с задачей «${taskTitle}». Задай любой вопрос — объясню концепцию, помогу разобраться с командой или наведу на правильный путь.`,
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  // Скролл вниз при новом сообщении
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages, isLoading])

  // Фокус на input при открытии
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 200)
    }
  }, [isOpen])

  const sendMessage = useCallback(async () => {
    const text = input.trim()
    if (!text || isLoading) return

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: text,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const response = await api.post('/ai/ask/', {
        task_id: taskId,
        question: text,
        context: 'task_help',
      })

      const aiMessage: Message = {
        id: `ai-${Date.now()}`,
        role: 'assistant',
        content: response.data.answer || response.data.response || 'Не удалось получить ответ.',
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, aiMessage])
    } catch {
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: 'Ошибка соединения с AI. Проверьте, что Ollama запущен.',
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }, [input, isLoading, taskId])

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const QUICK_QUESTIONS = [
    'Объясни задачу',
    'Какие команды использовать?',
    'Как проверить результат?',
  ]

  return (
    <>
      {/* Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/30 z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <div
        className={`fixed top-0 right-0 h-full w-[360px] bg-[#0f1520] border-l border-[#1e2d45] z-50 flex flex-col shadow-2xl transition-transform duration-300 ease-in-out ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        {/* Шапка */}
        <div className="flex items-center gap-3 px-4 py-4 border-b border-[#1e2d45] shrink-0">
          <div className="w-8 h-8 rounded-xl bg-[#00e676]/20 flex items-center justify-center">
            <svg className="w-4 h-4 text-[#00e676]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.347.347a3.5 3.5 0 00-1.028 2.471v.8A2.5 2.5 0 0112 19.5a2.5 2.5 0 01-2.5-2.5v-.8a3.5 3.5 0 00-1.028-2.471l-.347-.347z" />
            </svg>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold text-[#e2e8f0]">AI-ассистент</p>
            <p className="text-xs text-[#8899aa] truncate">{taskTitle}</p>
          </div>
          <button
            onClick={onClose}
            className="w-7 h-7 rounded-lg flex items-center justify-center text-[#8899aa] hover:text-[#e2e8f0] hover:bg-[#1e2d45] transition-colors"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Сообщения */}
        <div
          ref={scrollRef}
          className="flex-1 overflow-y-auto p-4 space-y-4"
        >
          {messages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} />
          ))}
          {isLoading && <TypingIndicator />}
        </div>

        {/* Быстрые вопросы (если мало сообщений) */}
        {messages.length <= 2 && !isLoading && (
          <div className="px-4 pb-3 flex flex-wrap gap-2 shrink-0">
            {QUICK_QUESTIONS.map((q) => (
              <button
                key={q}
                onClick={() => {
                  setInput(q)
                  setTimeout(() => inputRef.current?.focus(), 50)
                }}
                className="text-xs px-3 py-1.5 rounded-lg border border-[#1e2d45] text-[#8899aa] hover:border-[#00d4ff]/40 hover:text-[#00d4ff] transition-colors"
              >
                {q}
              </button>
            ))}
          </div>
        )}

        {/* Input */}
        <div className="px-4 py-3 border-t border-[#1e2d45] shrink-0">
          <div className="flex items-end gap-2 bg-[#0a0e17] border border-[#1e2d45] rounded-xl px-3 py-2.5 focus-within:border-[#00d4ff]/40 transition-colors">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Задай вопрос... (Enter — отправить)"
              rows={1}
              className="flex-1 bg-transparent text-sm text-[#e2e8f0] placeholder-[#4a5568] outline-none resize-none max-h-32 leading-relaxed"
              style={{ lineHeight: '1.5' }}
            />
            <button
              onClick={sendMessage}
              disabled={!input.trim() || isLoading}
              className="w-7 h-7 rounded-lg bg-[#00d4ff] flex items-center justify-center disabled:opacity-40 shrink-0 transition-opacity"
            >
              <svg className="w-3.5 h-3.5 text-[#0a0e17]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 19V5m0 0l-7 7m7-7l7 7" />
              </svg>
            </button>
          </div>
          <p className="text-[10px] text-[#4a5568] mt-1.5 text-center">
            Shift+Enter — новая строка
          </p>
        </div>
      </div>
    </>
  )
}
