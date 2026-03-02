/**
 * NotesEditor — Markdown редактор с preview (split view).
 * Использует @uiw/react-md-editor.
 * Автосохранение через debounce 1000ms.
 */
import { useState, useEffect, useRef } from 'react'
import MDEditor from '@uiw/react-md-editor'
import '@uiw/react-md-editor/markdown-editor.css'
import '@uiw/react-markdown-preview/markdown.css'
import { useNote, useSaveNote } from '@/api/hooks/useNotes'

// ─── Props ────────────────────────────────────────────────────────────────────

interface Props {
  taskId: number
}

// ─── Component ────────────────────────────────────────────────────────────────

export default function NotesEditor({ taskId }: Props) {
  const { data: note } = useNote(taskId)
  const saveNote = useSaveNote()

  const [content, setContent] = useState('')
  const [saveState, setSaveState] = useState<'saved' | 'saving' | 'unsaved'>('saved')
  const saveTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

  // Инициализируем контент из API
  useEffect(() => {
    if (note?.content !== undefined) {
      setContent(note.content)
    }
  }, [note])

  const handleChange = (val: string | undefined) => {
    const newContent = val ?? ''
    setContent(newContent)
    setSaveState('unsaved')

    if (saveTimer.current) clearTimeout(saveTimer.current)
    saveTimer.current = setTimeout(() => {
      setSaveState('saving')
      saveNote.mutate(
        { taskId, content: newContent },
        {
          onSuccess: () => setSaveState('saved'),
          onError: () => setSaveState('unsaved'),
        }
      )
    }, 1000)
  }

  useEffect(() => {
    return () => {
      if (saveTimer.current) clearTimeout(saveTimer.current)
    }
  }, [])

  return (
    <div className="space-y-2" data-color-mode="dark">
      {/* Шапка с индикатором */}
      <div className="flex items-center justify-between">
        <span className="text-xs text-[#8899aa]">Заметки к задаче</span>
        <div className="flex items-center gap-1.5">
          {saveState === 'saving' && (
            <span className="w-1.5 h-1.5 rounded-full bg-[#ff9500] animate-pulse" />
          )}
          {saveState === 'saved' && (
            <span className="w-1.5 h-1.5 rounded-full bg-[#00e676]" />
          )}
          {saveState === 'unsaved' && (
            <span className="w-1.5 h-1.5 rounded-full bg-[#8899aa]" />
          )}
          <span
            className={`text-xs ${
              saveState === 'saved'
                ? 'text-[#00e676]'
                : saveState === 'saving'
                ? 'text-[#ff9500]'
                : 'text-[#8899aa]'
            }`}
          >
            {saveState === 'saved'
              ? 'Сохранено'
              : saveState === 'saving'
              ? 'Сохранение...'
              : 'Не сохранено'}
          </span>
        </div>
      </div>

      {/* Markdown редактор (split view) */}
      <div
        className="rounded-xl overflow-hidden border border-[#1e2d45]"
        style={{
          '--md-editor-bg': '#0a0e17',
          '--color-canvas-default': '#0a0e17',
          '--color-border-default': '#1e2d45',
        } as React.CSSProperties}
      >
        <MDEditor
          value={content}
          onChange={handleChange}
          preview="live"
          height={280}
          visibleDragbar={false}
          style={{
            background: '#0a0e17',
            borderRadius: '0.75rem',
          }}
          textareaProps={{
            placeholder: 'Пишите заметки, команды, идеи...',
            style: { fontFamily: '"JetBrains Mono", monospace', fontSize: 13 },
          }}
        />
      </div>

      {/* Подсказка по markdown */}
      <p className="text-[10px] text-[#4a5568]">
        Поддерживает **жирный**, *курсив*, `код`, ## заголовки
      </p>
    </div>
  )
}
