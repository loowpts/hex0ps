import { Link } from 'react-router-dom'
import { useAnalytics, useExportPdf } from '@/api/hooks/useAnalytics'
import type { AnalyticsData, RecommendedTask } from '@/types'
import { format, eachDayOfInterval, subDays } from 'date-fns'
import { ru } from 'date-fns/locale'

// ─── HeatmapCalendar ─────────────────────────────────────────────────────────

function HeatmapCalendar({ heatmap }: { heatmap: AnalyticsData['heatmap'] }) {
  const today = new Date()
  const start = subDays(today, 89) // ~3 months
  const days = eachDayOfInterval({ start, end: today })

  const getColor = (dateKey: string) => {
    const d = heatmap[dateKey]
    if (!d || d.tasks === 0) return 'bg-[#1e2d45]'
    if (d.tasks === 1) return 'bg-[#00d4ff]/30'
    if (d.tasks === 2) return 'bg-[#00d4ff]/60'
    return 'bg-[#00d4ff]'
  }

  // Group by week
  const weeks: Date[][] = []
  let week: Date[] = []
  days.forEach((day, i) => {
    week.push(day)
    if (week.length === 7 || i === days.length - 1) {
      weeks.push(week)
      week = []
    }
  })

  return (
    <div className="overflow-x-auto">
      <div className="flex gap-1 min-w-max">
        {weeks.map((week, wi) => (
          <div key={wi} className="flex flex-col gap-1">
            {week.map((day) => {
              const key = format(day, 'yyyy-MM-dd')
              const d = heatmap[key]
              return (
                <div
                  key={key}
                  title={`${format(day, 'd MMM', { locale: ru })}: ${d?.tasks ?? 0} задач, ${d?.xp ?? 0} XP`}
                  className={`w-3 h-3 rounded-sm cursor-pointer transition-opacity hover:opacity-80 ${getColor(key)}`}
                />
              )
            })}
          </div>
        ))}
      </div>
      <div className="flex items-center gap-2 mt-3">
        <span className="text-xs text-[#8899aa]">Меньше</span>
        {['bg-[#1e2d45]', 'bg-[#00d4ff]/30', 'bg-[#00d4ff]/60', 'bg-[#00d4ff]'].map((c, i) => (
          <div key={i} className={`w-3 h-3 rounded-sm ${c}`} />
        ))}
        <span className="text-xs text-[#8899aa]">Больше</span>
      </div>
    </div>
  )
}

// ─── SkillBar ────────────────────────────────────────────────────────────────

function SkillBar({ name, pct, completed, total }: { name: string; pct: number; completed: number; total: number }) {
  const LABELS: Record<string, string> = {
    linux: 'Linux',
    nginx: 'Nginx',
    systemd: 'Systemd',
    docker: 'Docker',
    networks: 'Сети',
    git: 'Git',
    cicd: 'CI/CD',
  }

  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-[#e2e8f0]">{LABELS[name] ?? name}</span>
        <span className="text-[#8899aa]">{completed}/{total}</span>
      </div>
      <div className="h-2 bg-[#1e2d45] rounded-full overflow-hidden">
        <div
          className="h-full rounded-full bg-gradient-to-r from-[#00d4ff] to-[#00e676] transition-all duration-700"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}

// ─── WeeklyCard ───────────────────────────────────────────────────────────────

function WeeklyCard({
  label,
  current,
  previous,
  unit,
  color,
}: {
  label: string
  current: number
  previous: number
  unit: string
  color: string
}) {
  const diff = current - previous
  const pct = previous > 0 ? Math.round((diff / previous) * 100) : 0

  return (
    <div className="bg-[#0f1520] border border-[#1e2d45] rounded-2xl p-4">
      <p className="text-[#8899aa] text-sm mb-2">{label}</p>
      <p className={`text-2xl font-bold ${color}`}>
        {current} <span className="text-sm font-normal">{unit}</span>
      </p>
      <p className={`text-xs mt-1 ${diff >= 0 ? 'text-[#00e676]' : 'text-red-400'}`}>
        {diff >= 0 ? '+' : ''}{pct}% vs пред. неделя
      </p>
    </div>
  )
}

// ─── RecommendedCard ─────────────────────────────────────────────────────────

function RecommendedCard({ task }: { task: RecommendedTask }) {
  const DIFF_COLORS: Record<string, string> = {
    beginner: 'text-[#00e676]',
    intermediate: 'text-[#ff9500]',
    advanced: 'text-red-400',
  }

  return (
    <Link
      to={`/tasks/${task.id}`}
      className="block bg-[#0f1520] border border-[#1e2d45] rounded-xl p-4 hover:border-[#00d4ff]/40 transition-colors"
    >
      <div className="flex justify-between items-start mb-2">
        <p className="text-[#e2e8f0] text-sm font-medium line-clamp-2">{task.title_ru}</p>
        <span className={`text-xs ml-2 shrink-0 ${DIFF_COLORS[task.difficulty] ?? 'text-[#8899aa]'}`}>
          {task.difficulty}
        </span>
      </div>
      <p className="text-[#8899aa] text-xs line-clamp-2 mb-2">{task.reason}</p>
      <div className="flex justify-between">
        <span className="text-xs text-[#8899aa] uppercase">{task.category}</span>
        <span className="text-xs font-semibold text-[#00e676]">+{task.xp_reward} XP</span>
      </div>
    </Link>
  )
}

// ─── Main ────────────────────────────────────────────────────────────────────

function SkeletonBlock({ className }: { className?: string }) {
  return <div className={`bg-[#1e2d45]/50 rounded-xl animate-pulse ${className}`} />
}

export default function Analytics() {
  const { data, isLoading } = useAnalytics()
  const exportPdf = useExportPdf()

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#0a0e17] p-6 max-w-7xl mx-auto space-y-6">
        <SkeletonBlock className="h-8 w-48" />
        <div className="grid grid-cols-3 gap-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <SkeletonBlock key={i} className="h-28" />
          ))}
        </div>
        <SkeletonBlock className="h-32" />
        <SkeletonBlock className="h-64" />
      </div>
    )
  }

  if (!data) {
    return (
      <div className="min-h-screen bg-[#0a0e17] flex items-center justify-center">
        <p className="text-[#8899aa]">Нет данных аналитики</p>
      </div>
    )
  }

  const totalMinutes = data.weekly.current.time_minutes
  const hours = Math.floor(totalMinutes / 60)
  const minutes = totalMinutes % 60

  return (
    <div className="min-h-screen bg-[#0a0e17] p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[#e2e8f0] mb-1">Аналитика</h1>
          <p className="text-[#8899aa] text-sm">Статистика прогресса и активности</p>
        </div>
        <button
          onClick={() => exportPdf.mutate()}
          disabled={exportPdf.isPending}
          className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium border border-[#1e2d45] text-[#8899aa] hover:border-[#00d4ff]/40 hover:text-[#00d4ff] disabled:opacity-50 transition-colors"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          {exportPdf.isPending ? 'Генерация...' : 'Скачать PDF'}
        </button>
      </div>

      {/* Weekly Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <WeeklyCard
          label="Задач на этой неделе"
          current={data.weekly.current.tasks}
          previous={data.weekly.previous.tasks}
          unit="задач"
          color="text-[#00d4ff]"
        />
        <WeeklyCard
          label="XP на этой неделе"
          current={data.weekly.current.xp}
          previous={data.weekly.previous.xp}
          unit="XP"
          color="text-[#00e676]"
        />
        <WeeklyCard
          label="Время практики"
          current={hours}
          previous={Math.floor(data.weekly.previous.time_minutes / 60)}
          unit={`ч ${minutes} мин`}
          color="text-[#ff9500]"
        />
      </div>

      {/* Streak */}
      <div className="bg-[#0f1520] border border-[#1e2d45] rounded-2xl p-5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-3xl">🔥</span>
            <div>
              <p className="text-[#e2e8f0] font-semibold">
                Текущий стрик: {data.streak.current} дн.
              </p>
              <p className="text-[#8899aa] text-sm">Рекорд: {data.streak.max} дн.</p>
            </div>
          </div>
          {data.streak.at_risk && (
            <div className="bg-[#ff9500]/10 border border-[#ff9500]/30 rounded-xl px-3 py-2">
              <p className="text-[#ff9500] text-sm font-medium">⚠ Стрик под угрозой!</p>
              <p className="text-[#8899aa] text-xs">Выполните задачу сегодня</p>
            </div>
          )}
        </div>
      </div>

      {/* Heatmap */}
      <div className="bg-[#0f1520] border border-[#1e2d45] rounded-2xl p-5">
        <h2 className="text-[#e2e8f0] font-semibold mb-4">Активность за 90 дней</h2>
        <HeatmapCalendar heatmap={data.heatmap} />
      </div>

      {/* Skills */}
      <div className="bg-[#0f1520] border border-[#1e2d45] rounded-2xl p-5">
        <h2 className="text-[#e2e8f0] font-semibold mb-4">Прогресс по категориям</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Object.entries(data.skills).map(([name, skill]) => (
            <SkillBar
              key={name}
              name={name}
              pct={skill.pct}
              completed={skill.completed}
              total={skill.total}
            />
          ))}
        </div>
      </div>

      {/* Forecast */}
      <div className="bg-[#0f1520] border border-[#1e2d45] rounded-2xl p-5">
        <h2 className="text-[#e2e8f0] font-semibold mb-3">Прогноз</h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <p className="text-[#8899aa] text-sm">До следующего уровня</p>
            <p className="text-2xl font-bold text-[#00d4ff]">{data.forecast.days_to_next_level} дн.</p>
          </div>
          <div>
            <p className="text-[#8899aa] text-sm">Задач в день (план)</p>
            <p className="text-2xl font-bold text-[#00e676]">{data.forecast.tasks_per_day_needed}</p>
          </div>
          <div>
            <p className="text-[#8899aa] text-sm">XP до уровня</p>
            <p className="text-2xl font-bold text-[#ff9500]">{data.forecast.xp_to_next_level}</p>
          </div>
        </div>
      </div>

      {/* AI Insight */}
      <div className="bg-[#0f1520] border border-[#1e2d45] rounded-2xl p-5">
        <div className="flex items-center gap-2 mb-3">
          <svg className="w-5 h-5 text-[#00d4ff]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.347.347a3.5 3.5 0 00-1.028 2.471v.8A2.5 2.5 0 0112 19.5a2.5 2.5 0 01-2.5-2.5v-.8a3.5 3.5 0 00-1.028-2.471l-.347-.347z" />
          </svg>
          <h2 className="text-[#e2e8f0] font-semibold">AI-анализ</h2>
        </div>
        <p className="text-[#8899aa] leading-relaxed">{data.ai_insight}</p>
      </div>

      {/* Recommended Tasks */}
      {data.recommended_tasks.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-[#e2e8f0] font-semibold">Рекомендованные задачи</h2>
            <Link to="/tasks" className="text-[#00d4ff] text-sm hover:underline">
              Все задачи →
            </Link>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {data.recommended_tasks.map((task) => (
              <RecommendedCard key={task.id} task={task} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
