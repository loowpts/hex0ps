import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/api/client'
import type { CheatSheetList, CheatSheetDetail } from '@/types'
import ReactMarkdown from 'react-markdown'

// ─── Helpers ──────────────────────────────────────────────────────────────────

const CATEGORIES = [
  { id: '', label: 'Все' },
  { id: 'linux', label: 'Linux' },
  { id: 'docker', label: 'Docker' },
  { id: 'nginx', label: 'Nginx' },
  { id: 'git', label: 'Git' },
  { id: 'systemd', label: 'Systemd' },
  { id: 'networks', label: 'Сети' },
  { id: 'cicd', label: 'CI/CD' },
]

function categoryColor(c: string) {
  const map: Record<string, string> = {
    linux: 'text-[#00d4ff] bg-[#00d4ff]/10',
    docker: 'text-blue-400 bg-blue-500/10',
    nginx: 'text-[#00e676] bg-[#00e676]/10',
    git: 'text-red-400 bg-red-500/10',
    systemd: 'text-orange-400 bg-orange-500/10',
    networks: 'text-purple-400 bg-purple-500/10',
    cicd: 'text-yellow-400 bg-yellow-500/10',
  }
  return map[c] ?? 'text-[#8899aa] bg-[#1e2d45]'
}

// ─── CheatSheet Card ──────────────────────────────────────────────────────────

function CheatSheetCard({
  sheet,
  onSelect,
  onBookmark,
}: {
  sheet: CheatSheetList
  onSelect: (id: number) => void
  onBookmark: (id: number) => void
}) {
  return (
    <div
      className="bg-[#0f1520] border border-[#1e2d45] rounded-2xl p-5 hover:border-[#00d4ff]/30 transition-colors cursor-pointer"
      onClick={() => onSelect(sheet.id)}
    >
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="text-[#e2e8f0] font-semibold text-sm mb-1">{sheet.title_ru}</h3>
          <span className={`text-xs px-2 py-0.5 rounded-md font-medium ${categoryColor(sheet.category)}`}>
            {sheet.category_display}
          </span>
        </div>
        <button
          onClick={(e) => { e.stopPropagation(); onBookmark(sheet.id) }}
          className={`text-lg transition-colors ${sheet.is_bookmarked ? 'text-[#ff9500]' : 'text-[#1e2d45] hover:text-[#ff9500]'}`}
        >
          {sheet.is_bookmarked ? '★' : '☆'}
        </button>
      </div>

      <div className="flex items-center gap-3 text-xs text-[#8899aa]">
        <span>{sheet.entries_count} команд</span>
        {sheet.tags.slice(0, 3).map(tag => (
          <span key={tag} className="bg-[#1e2d45] px-1.5 py-0.5 rounded text-[#4a5568]">{tag}</span>
        ))}
      </div>
    </div>
  )
}

// ─── Entry (command row) ──────────────────────────────────────────────────────

function EntryRow({
  entry,
  onLearnedToggle,
}: {
  entry: CheatSheetDetail['entries'][0]
  onLearnedToggle: (id: number) => void
}) {
  const [showExample, setShowExample] = useState(false)

  return (
    <div className={`border rounded-xl p-4 transition-colors ${entry.learned ? 'border-[#00e676]/20 bg-[#00e676]/3' : 'border-[#1e2d45] bg-[#0a0e17]'}`}>
      <div className="flex items-start gap-3">
        <div className="flex-1 min-w-0">
          <code className="text-[#00d4ff] text-sm font-mono bg-[#1e2d45] px-2 py-0.5 rounded">
            {entry.command}
          </code>
          <p className="text-[#8899aa] text-xs mt-2">{entry.description_ru}</p>
          {entry.example && (
            <button
              onClick={() => setShowExample(!showExample)}
              className="text-xs text-[#4a5568] hover:text-[#8899aa] mt-1 transition-colors"
            >
              {showExample ? '▲ Скрыть пример' : '▼ Пример'}
            </button>
          )}
          {showExample && entry.example && (
            <pre className="mt-2 text-xs font-mono bg-[#050810] border border-[#1e2d45] rounded-lg p-3 text-[#00e676] overflow-x-auto">
              {entry.example}
            </pre>
          )}
        </div>
        <button
          onClick={() => onLearnedToggle(entry.id)}
          className={`shrink-0 w-8 h-8 rounded-lg border flex items-center justify-center text-sm transition-colors ${
            entry.learned
              ? 'border-[#00e676]/30 bg-[#00e676]/10 text-[#00e676]'
              : 'border-[#1e2d45] text-[#4a5568] hover:border-[#00e676]/30 hover:text-[#00e676]'
          }`}
          title={entry.learned ? 'Знаю — убрать отметку' : 'Отметить как запомненное'}
        >
          {entry.learned ? '✓' : '○'}
        </button>
      </div>
    </div>
  )
}

// ─── Detail Panel ─────────────────────────────────────────────────────────────

function CheatSheetDetailPanel({
  sheetId,
  onBack,
}: {
  sheetId: number
  onBack: () => void
}) {
  const qc = useQueryClient()

  const { data: sheet, isLoading } = useQuery<CheatSheetDetail>({
    queryKey: ['cheatsheet', sheetId],
    queryFn: () => api.get(`/cheatsheets/${sheetId}/`).then((r) => r.data),
  })

  const learnedMutation = useMutation({
    mutationFn: (entryId: number) =>
      api.post(`/cheatsheets/entry/${entryId}/learned/`).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['cheatsheet', sheetId] }),
  })

  if (isLoading || !sheet) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map(i => <div key={i} className="h-16 bg-[#1e2d45]/30 rounded-xl animate-pulse" />)}
      </div>
    )
  }

  const learnedPct = sheet.entries.length > 0
    ? Math.round((sheet.learned_count / sheet.entries.length) * 100)
    : 0

  return (
    <div>
      {/* Back */}
      <button
        onClick={onBack}
        className="flex items-center gap-2 text-[#8899aa] hover:text-[#e2e8f0] text-sm mb-4 transition-colors"
      >
        ← Все шпаргалки
      </button>

      {/* Header */}
      <div className="bg-[#0f1520] border border-[#1e2d45] rounded-2xl p-5 mb-4">
        <div className="flex items-center gap-3 mb-3">
          <h2 className="text-[#e2e8f0] font-bold text-lg flex-1">{sheet.title_ru}</h2>
          <span className={`text-xs px-2 py-0.5 rounded-md ${categoryColor(sheet.category)}`}>
            {sheet.category_display}
          </span>
        </div>
        {sheet.entries.length > 0 && (
          <div>
            <div className="flex items-center justify-between text-xs text-[#8899aa] mb-1">
              <span>Прогресс запоминания</span>
              <span>{sheet.learned_count}/{sheet.entries.length} команд</span>
            </div>
            <div className="h-1.5 bg-[#1e2d45] rounded-full overflow-hidden">
              <div
                className="h-full bg-[#00e676] rounded-full transition-all"
                style={{ width: `${learnedPct}%` }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Markdown теория */}
      {sheet.content_md && (
        <div className="bg-[#0f1520] border border-[#1e2d45] rounded-2xl p-5 mb-4">
          <div className="prose prose-invert prose-sm max-w-none text-[#c8d6e8]">
            <ReactMarkdown
              components={{
                code: ({ children, className }) => {
                  const isBlock = className?.includes('language-')
                  return isBlock
                    ? <code className="block bg-[#0a0e17] border border-[#1e2d45] rounded-lg p-3 text-[#00e676] text-xs font-mono whitespace-pre overflow-x-auto">{children}</code>
                    : <code className="bg-[#1e2d45] text-[#00d4ff] px-1 py-0.5 rounded text-sm font-mono">{children}</code>
                },
                p: ({ children }) => <p className="text-[#8899aa] text-sm leading-relaxed mb-2">{children}</p>,
                table: ({ children }) => <div className="overflow-x-auto mb-3"><table className="w-full text-sm border-collapse">{children}</table></div>,
                th: ({ children }) => <th className="text-left p-2 border border-[#1e2d45] text-[#e2e8f0] bg-[#1e2d45]/50 text-xs">{children}</th>,
                td: ({ children }) => <td className="p-2 border border-[#1e2d45] text-[#8899aa] text-xs">{children}</td>,
              }}
            >
              {sheet.content_md}
            </ReactMarkdown>
          </div>
        </div>
      )}

      {/* Команды */}
      {sheet.entries.length > 0 && (
        <div>
          <h3 className="text-[#e2e8f0] font-semibold text-sm mb-3">
            Команды для запоминания
          </h3>
          <div className="space-y-2">
            {sheet.entries.map(entry => (
              <EntryRow
                key={entry.id}
                entry={entry}
                onLearnedToggle={learnedMutation.mutate}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// ─── Main ─────────────────────────────────────────────────────────────────────

export default function CheatSheets() {
  const qc = useQueryClient()
  const [searchParams] = useSearchParams()
  const [category, setCategory] = useState('')
  const [search, setSearch] = useState('')
  const [onlyBookmarked, setOnlyBookmarked] = useState(false)
  const [selectedId, setSelectedId] = useState<number | null>(null)

  // Поддержка ?id= из CommandPalette
  useEffect(() => {
    const id = searchParams.get('id')
    if (id) setSelectedId(Number(id))
  }, [searchParams])

  const { data: sheets = [], isLoading } = useQuery<CheatSheetList[]>({
    queryKey: ['cheatsheets', category, search, onlyBookmarked],
    queryFn: () => {
      const params = new URLSearchParams()
      if (category) params.set('category', category)
      if (search) params.set('q', search)
      if (onlyBookmarked) params.set('bookmarked', '1')
      return api.get(`/cheatsheets/?${params.toString()}`).then((r) => r.data)
    },
    staleTime: 1000 * 60 * 5,
  })

  const bookmarkMutation = useMutation({
    mutationFn: (id: number) => api.post(`/cheatsheets/${id}/bookmark/`).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['cheatsheets'] }),
  })

  if (selectedId) {
    return (
      <div className="min-h-screen bg-[#0a0e17] p-6">
        <div className="max-w-3xl mx-auto">
          <CheatSheetDetailPanel
            sheetId={selectedId}
            onBack={() => setSelectedId(null)}
          />
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#0a0e17] p-6">
      <div className="max-w-4xl mx-auto">

        {/* Header */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-[#e2e8f0] mb-1">📋 Шпаргалки</h1>
          <p className="text-[#4a5568] text-sm">
            Команды с описаниями. Отмечай что запомнил — они уйдут из очереди повторения.
          </p>
        </div>

        {/* Search + filters */}
        <div className="flex gap-3 mb-4">
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Поиск команды..."
            className="flex-1 bg-[#0f1520] border border-[#1e2d45] rounded-xl px-4 py-2.5 text-sm text-[#e2e8f0] placeholder-[#4a5568] focus:outline-none focus:border-[#00d4ff]/50"
          />
          <button
            onClick={() => setOnlyBookmarked(!onlyBookmarked)}
            className={`px-4 py-2.5 rounded-xl text-sm border transition-colors ${
              onlyBookmarked
                ? 'border-[#ff9500]/50 bg-[#ff9500]/10 text-[#ff9500]'
                : 'border-[#1e2d45] text-[#8899aa] hover:border-[#ff9500]/30'
            }`}
          >
            ★ Закладки
          </button>
        </div>

        {/* Category filter */}
        <div className="flex flex-wrap gap-2 mb-6">
          {CATEGORIES.map(cat => (
            <button
              key={cat.id}
              onClick={() => setCategory(cat.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
                category === cat.id
                  ? 'border-[#00d4ff]/50 bg-[#00d4ff]/10 text-[#00d4ff]'
                  : 'border-[#1e2d45] text-[#8899aa] hover:border-[#00d4ff]/30'
              }`}
            >
              {cat.label}
            </button>
          ))}
        </div>

        {/* List */}
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[1, 2, 3, 4].map(i => <div key={i} className="h-28 bg-[#1e2d45]/30 rounded-2xl animate-pulse" />)}
          </div>
        ) : sheets.length === 0 ? (
          <div className="text-center py-16 text-[#4a5568]">
            <p className="text-lg mb-2">Шпаргалки не найдены</p>
            <p className="text-sm">Попробуй изменить фильтры или поисковый запрос</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {sheets.map(sheet => (
              <CheatSheetCard
                key={sheet.id}
                sheet={sheet}
                onSelect={setSelectedId}
                onBookmark={bookmarkMutation.mutate}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
