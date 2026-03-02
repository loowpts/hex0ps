import { useChangelog } from '@/api/hooks/useAnalytics'
import { format } from 'date-fns'
import { ru } from 'date-fns/locale'

// ─── Types ────────────────────────────────────────────────────────────────────

interface ChangelogEntry {
  id: number
  version: string
  title: string
  body_md: string
  released_at: string
  type?: 'feature' | 'fix' | 'improvement' | 'breaking'
}

const TYPE_CONFIG = {
  feature: { label: 'Новая функция', color: 'bg-[#00e676]/10 text-[#00e676] border-[#00e676]/30' },
  fix: { label: 'Исправление', color: 'bg-red-400/10 text-red-400 border-red-400/30' },
  improvement: { label: 'Улучшение', color: 'bg-[#00d4ff]/10 text-[#00d4ff] border-[#00d4ff]/30' },
  breaking: { label: 'Критическое', color: 'bg-[#ff9500]/10 text-[#ff9500] border-[#ff9500]/30' },
}

// Render markdown-ish body as plain paragraphs
function RenderBody({ text }: { text: string }) {
  const lines = text.split('\n')
  const elements: JSX.Element[] = []

  lines.forEach((line, i) => {
    if (line.startsWith('## ')) {
      elements.push(
        <h3 key={i} className="text-[#e2e8f0] font-semibold mt-4 mb-1 text-sm">
          {line.slice(3)}
        </h3>
      )
    } else if (line.startsWith('### ')) {
      elements.push(
        <h4 key={i} className="text-[#e2e8f0] font-medium mt-3 mb-1 text-sm">
          {line.slice(4)}
        </h4>
      )
    } else if (line.startsWith('- ')) {
      elements.push(
        <li key={i} className="text-[#8899aa] text-sm ml-4 list-disc">
          {line.slice(2)}
        </li>
      )
    } else if (line.startsWith('* ')) {
      elements.push(
        <li key={i} className="text-[#8899aa] text-sm ml-4 list-disc">
          {line.slice(2)}
        </li>
      )
    } else if (line.trim() === '') {
      elements.push(<div key={i} className="h-1" />)
    } else {
      elements.push(
        <p key={i} className="text-[#8899aa] text-sm">
          {line}
        </p>
      )
    }
  })

  return <div className="space-y-0.5">{elements}</div>
}

// ─── ChangelogCard ────────────────────────────────────────────────────────────

function ChangelogCard({ entry }: { entry: ChangelogEntry }) {
  const typeCfg = entry.type ? TYPE_CONFIG[entry.type] : null

  return (
    <div className="bg-[#0f1520] border border-[#1e2d45] rounded-2xl p-6">
      <div className="flex flex-wrap items-start justify-between gap-3 mb-3">
        <div className="flex flex-wrap items-center gap-2">
          <span className="font-mono text-sm font-bold text-[#00d4ff]">
            v{entry.version}
          </span>
          {typeCfg && (
            <span className={`text-xs px-2 py-0.5 rounded-md border ${typeCfg.color}`}>
              {typeCfg.label}
            </span>
          )}
        </div>
        <span className="text-[#8899aa] text-xs">
          {format(new Date(entry.released_at), 'd MMMM yyyy', { locale: ru })}
        </span>
      </div>

      <h3 className="text-[#e2e8f0] font-semibold mb-3">{entry.title}</h3>

      <RenderBody text={entry.body_md} />
    </div>
  )
}

// ─── Main ────────────────────────────────────────────────────────────────────

const MOCK_ENTRIES: ChangelogEntry[] = [
  {
    id: 1,
    version: '1.0.0',
    title: 'Запуск платформы',
    body_md: '## Что нового\n- Задачи по Linux, Docker, Nginx, Systemd\n- AI-ассистент для подсказок\n- Система XP и уровней\n- Аналитика прогресса',
    released_at: new Date().toISOString(),
    type: 'feature',
  },
]

export default function Changelog() {
  const { data, isLoading } = useChangelog()
  const entries = (data as ChangelogEntry[] | undefined) ?? MOCK_ENTRIES

  return (
    <div className="min-h-screen bg-[#0a0e17] p-6 max-w-3xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-[#e2e8f0] mb-1">История изменений</h1>
        <p className="text-[#8899aa] text-sm">Обновления и улучшения платформы</p>
      </div>

      {isLoading ? (
        <div className="space-y-4 animate-pulse">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-48 bg-[#1e2d45] rounded-2xl" />
          ))}
        </div>
      ) : entries.length > 0 ? (
        <div className="space-y-4">
          {entries.map((entry) => (
            <ChangelogCard key={entry.id} entry={entry} />
          ))}
        </div>
      ) : (
        <div className="text-center py-16">
          <p className="text-[#8899aa]">Нет записей об изменениях</p>
        </div>
      )}
    </div>
  )
}
