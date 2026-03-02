import { useState, useEffect, useRef } from 'react'
import { useNotes, useSaveNote } from '@/api/hooks/useNotes'
import type { Note } from '@/types'
import { format } from 'date-fns'
import { ru } from 'date-fns/locale'

// ─── NoteCard ────────────────────────────────────────────────────────────────

function NoteCard({ note, onClick }: { note: Note; onClick: () => void }) {
  const preview = note.content.slice(0, 120).replace(/\n/g, ' ')

  return (
    <button
      onClick={onClick}
      className="text-left w-full bg-[#0f1520] border border-[#1e2d45] rounded-2xl p-4 hover:border-[#00d4ff]/40 transition-colors group"
    >
      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="flex items-center gap-2">
          <svg className="w-4 h-4 text-[#8899aa] group-hover:text-[#00d4ff] transition-colors shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
          <span className="text-[#8899aa] text-xs">Задача #{note.task_id}</span>
        </div>
        {note.updated_at && (
          <span className="text-[#8899aa] text-xs shrink-0">
            {format(new Date(note.updated_at), 'd MMM', { locale: ru })}
          </span>
        )}
      </div>
      <p className="text-[#e2e8f0] text-sm line-clamp-3 font-mono">
        {preview || <span className="italic text-[#8899aa]">Пустая заметка</span>}
      </p>
    </button>
  )
}

// ─── NoteEditor ──────────────────────────────────────────────────────────────

function NoteEditorModal({ note, onClose }: { note: Note; onClose: () => void }) {
  const [content, setContent] = useState(note.content)
  const [saved, setSaved] = useState(true)
  const saveNote = useSaveNote()
  const saveTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

  const handleChange = (val: string) => {
    setContent(val)
    setSaved(false)
    if (saveTimer.current) clearTimeout(saveTimer.current)
    saveTimer.current = setTimeout(() => {
      saveNote.mutate(
        { taskId: note.task_id, content: val },
        { onSuccess: () => setSaved(true) }
      )
    }, 1500)
  }

  const handleExport = () => {
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `note-task-${note.task_id}.txt`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <div className="bg-[#0f1520] border border-[#1e2d45] rounded-2xl w-full max-w-2xl flex flex-col max-h-[80vh]">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-[#1e2d45] shrink-0">
          <div className="flex items-center gap-3">
            <h2 className="text-[#e2e8f0] font-semibold">Задача #{note.task_id}</h2>
            <span className={`text-xs ${saved ? 'text-[#00e676]' : 'text-[#ff9500]'}`}>
              {saved ? 'Сохранено' : 'Сохранение...'}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleExport}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs text-[#8899aa] border border-[#1e2d45] hover:border-[#00d4ff]/40 hover:text-[#00d4ff] transition-colors"
            >
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Экспорт
            </button>
            <button
              onClick={onClose}
              className="text-[#8899aa] hover:text-[#e2e8f0] transition-colors"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Editor */}
        <textarea
          value={content}
          onChange={(e) => handleChange(e.target.value)}
          placeholder="Начните писать..."
          className="flex-1 bg-transparent text-[#e2e8f0] text-sm font-mono p-5 resize-none focus:outline-none placeholder-[#4a5568]"
        />
      </div>
    </div>
  )
}

// ─── Main ────────────────────────────────────────────────────────────────────

export default function Notes() {
  const [searchInput, setSearchInput] = useState('')
  const [search, setSearch] = useState('')
  const [editingNote, setEditingNote] = useState<Note | null>(null)
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const { data: notes, isLoading } = useNotes(search || undefined)

  // Debounce search
  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => {
      setSearch(searchInput)
    }, 300)
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current)
    }
  }, [searchInput])

  const handleExportAll = () => {
    if (!notes || notes.length === 0) return
    const text = notes
      .map((n) => `=== Задача #${n.task_id} ===\n${n.content}`)
      .join('\n\n')
    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'all-notes.txt'
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="min-h-screen bg-[#0a0e17] p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-[#e2e8f0]">Заметки</h1>
          <p className="text-[#8899aa] text-sm mt-1">Ваши записи к задачам</p>
        </div>
        <button
          onClick={handleExportAll}
          disabled={!notes || notes.length === 0}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium border border-[#1e2d45] text-[#8899aa] hover:border-[#00d4ff]/40 hover:text-[#00d4ff] disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Экспортировать все
        </button>
      </div>

      {/* Search */}
      <div className="relative mb-6">
        <svg
          className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-[#8899aa]"
          fill="none" viewBox="0 0 24 24" stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <input
          type="text"
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
          placeholder="Поиск по заметкам..."
          className="w-full bg-[#0f1520] border border-[#1e2d45] rounded-xl pl-11 pr-4 py-3 text-[#e2e8f0] placeholder-[#4a5568] focus:outline-none focus:border-[#00d4ff]/50 transition-colors"
        />
        {searchInput && (
          <button
            onClick={() => setSearchInput('')}
            className="absolute right-4 top-1/2 -translate-y-1/2 text-[#8899aa] hover:text-[#e2e8f0]"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>

      {/* Content */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="bg-[#0f1520] border border-[#1e2d45] rounded-2xl p-4 animate-pulse">
              <div className="h-3 bg-[#1e2d45] rounded w-1/3 mb-3" />
              <div className="h-3 bg-[#1e2d45] rounded w-full mb-2" />
              <div className="h-3 bg-[#1e2d45] rounded w-4/5" />
            </div>
          ))}
        </div>
      ) : notes && notes.length > 0 ? (
        <>
          <p className="text-[#8899aa] text-sm mb-4">
            Заметок: <span className="text-[#e2e8f0] font-medium">{notes.length}</span>
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {notes.map((note) => (
              <NoteCard
                key={note.id ?? note.task_id}
                note={note}
                onClick={() => setEditingNote(note)}
              />
            ))}
          </div>
        </>
      ) : (
        <div className="text-center py-16">
          <div className="text-5xl mb-4">📝</div>
          <p className="text-[#e2e8f0] text-lg mb-2">
            {search ? 'Ничего не найдено' : 'Нет заметок'}
          </p>
          <p className="text-[#8899aa] text-sm">
            {search
              ? 'Попробуйте изменить запрос'
              : 'Добавляйте заметки во время выполнения задач'}
          </p>
        </div>
      )}

      {/* Editor Modal */}
      {editingNote && (
        <NoteEditorModal
          note={editingNote}
          onClose={() => setEditingNote(null)}
        />
      )}
    </div>
  )
}
