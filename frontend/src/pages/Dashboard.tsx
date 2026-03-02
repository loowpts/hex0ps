import { Link } from 'react-router-dom'
import { useMe } from '@/api/hooks/useAuth'
import { useAnalytics } from '@/api/hooks/useAnalytics'
import type { RecommendedTask } from '@/types'

const LEVEL_COLORS: Record<string, string> = {
  beginner: 'text-[#8899aa] border-[#8899aa]',
  junior: 'text-[#00e676] border-[#00e676]',
  middle: 'text-[#00d4ff] border-[#00d4ff]',
  senior: 'text-[#ff9500] border-[#ff9500]',
  pro: 'text-purple-400 border-purple-400',
}

const DIFF_COLORS: Record<string, string> = {
  beginner: 'bg-[#00e676]/10 text-[#00e676]',
  intermediate: 'bg-[#ff9500]/10 text-[#ff9500]',
  advanced: 'bg-red-500/10 text-red-400',
}

function StatCard({ label, value, sub, color }: { label: string; value: string | number; sub?: string; color: string }) {
  return (
    <div className="bg-[#0f1520] border border-[#1e2d45] rounded-2xl p-5">
      <p className="text-[#8899aa] text-sm mb-2">{label}</p>
      <p className={`text-3xl font-bold ${color}`}>{value}</p>
      {sub && <p className="text-[#8899aa] text-xs mt-1">{sub}</p>}
    </div>
  )
}

function SkeletonBlock({ className }: { className?: string }) {
  return <div className={`bg-[#1e2d45]/50 rounded-xl animate-pulse ${className}`} />
}

function RecommendedTaskCard({ task }: { task: RecommendedTask }) {
  return (
    <Link
      to={`/tasks/${task.id}`}
      className="block bg-[#0f1520] border border-[#1e2d45] rounded-xl p-4 hover:border-[#00d4ff]/40 transition-colors group"
    >
      <div className="flex items-start justify-between gap-3 mb-2">
        <p className="text-[#e2e8f0] text-sm font-medium group-hover:text-[#00d4ff] transition-colors line-clamp-2">
          {task.title_ru}
        </p>
        <span className={`shrink-0 text-xs px-2 py-0.5 rounded-md ${DIFF_COLORS[task.difficulty] ?? 'bg-[#1e2d45] text-[#8899aa]'}`}>
          {task.difficulty === 'beginner' ? 'Начинающий' : task.difficulty === 'intermediate' ? 'Средний' : 'Сложный'}
        </span>
      </div>
      <p className="text-[#8899aa] text-xs line-clamp-2 mb-3">{task.reason}</p>
      <div className="flex items-center justify-between">
        <span className="text-xs text-[#8899aa] uppercase tracking-wide">{task.category}</span>
        <span className="text-xs font-semibold text-[#00e676]">+{task.xp_reward} XP</span>
      </div>
    </Link>
  )
}

export default function Dashboard() {
  const { data: user, isLoading: userLoading } = useMe()
  const { data: analytics, isLoading: analyticsLoading } = useAnalytics()

  const levelColor = user ? (LEVEL_COLORS[user.level] ?? 'text-[#e2e8f0] border-[#e2e8f0]') : ''

  return (
    <div className="min-h-screen bg-[#0a0e17] p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        {userLoading ? (
          <div className="space-y-3">
            <SkeletonBlock className="h-8 w-64" />
            <SkeletonBlock className="h-4 w-40" />
          </div>
        ) : user ? (
          <div>
            <div className="flex flex-wrap items-center gap-3 mb-3">
              <h1 className="text-2xl font-bold text-[#e2e8f0]">
                Привет, <span className="text-[#00d4ff]">{user.username}</span>!
              </h1>
              <span className={`text-xs font-semibold px-2.5 py-1 rounded-lg border ${levelColor}`}>
                {user.level_display}
              </span>
              <span className="text-xs font-semibold px-2.5 py-1 rounded-lg bg-[#ff9500]/10 text-[#ff9500] border border-[#ff9500]/30">
                🔥 Стрик: {user.streak} дн.
              </span>
            </div>

            {/* XP Progress Bar */}
            <div className="max-w-sm">
              <div className="flex justify-between text-xs text-[#8899aa] mb-1">
                <span>{user.xp} XP</span>
                <span>{user.xp_to_next_level} XP до след. уровня</span>
              </div>
              <div className="h-2.5 bg-[#1e2d45] rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-[#00d4ff] to-[#00e676] transition-all duration-700"
                  style={{ width: `${user.level_progress_pct}%` }}
                />
              </div>
            </div>
          </div>
        ) : null}
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {analyticsLoading ? (
          Array.from({ length: 4 }).map((_, i) => (
            <SkeletonBlock key={i} className="h-28" />
          ))
        ) : analytics ? (
          <>
            <StatCard
              label="Задач решено"
              value={analytics.total_completed}
              sub="всего выполнено"
              color="text-[#00d4ff]"
            />
            <StatCard
              label="Всего XP"
              value={analytics.user.xp}
              sub={`${analytics.user.level_progress_pct}% до след. уровня`}
              color="text-[#00e676]"
            />
            <StatCard
              label="Текущий стрик"
              value={`${analytics.streak.current} дн.`}
              sub={`Рекорд: ${analytics.streak.max} дн.`}
              color="text-[#ff9500]"
            />
            <StatCard
              label="Часов практики"
              value={Math.round((analytics.weekly.current.time_minutes + analytics.weekly.previous.time_minutes) / 60)}
              sub="за последние 2 недели"
              color="text-purple-400"
            />
          </>
        ) : null}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* AI Insight */}
        <div className="lg:col-span-2 bg-[#0f1520] border border-[#1e2d45] rounded-2xl p-6">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-8 h-8 rounded-lg bg-[#00d4ff]/10 flex items-center justify-center">
              <svg className="w-4 h-4 text-[#00d4ff]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.347.347a3.5 3.5 0 00-1.028 2.471v.8A2.5 2.5 0 0112 19.5a2.5 2.5 0 01-2.5-2.5v-.8a3.5 3.5 0 00-1.028-2.471l-.347-.347z" />
              </svg>
            </div>
            <h2 className="text-[#e2e8f0] font-semibold">AI-рекомендация</h2>
          </div>

          {analyticsLoading ? (
            <div className="space-y-2">
              <SkeletonBlock className="h-4 w-full" />
              <SkeletonBlock className="h-4 w-5/6" />
              <SkeletonBlock className="h-4 w-4/6" />
            </div>
          ) : (
            <p className="text-[#8899aa] leading-relaxed">
              {analytics?.ai_insight || 'Нет данных для анализа'}
            </p>
          )}

          {analytics && (
            <div className="mt-4 p-3 bg-[#0a0e17] rounded-xl border border-[#1e2d45]">
              <p className="text-[#8899aa] text-xs">
                До следующего уровня:{' '}
                <span className="text-[#00d4ff] font-medium">
                  ~{analytics.forecast.days_to_next_level} дн.
                </span>{' '}
                (по {analytics.forecast.tasks_per_day_needed} задач/день)
              </p>
            </div>
          )}
        </div>

        {/* Quick Actions */}
        <div className="bg-[#0f1520] border border-[#1e2d45] rounded-2xl p-6">
          <h2 className="text-[#e2e8f0] font-semibold mb-4">Быстрые действия</h2>
          <div className="space-y-3">
            <Link
              to="/tasks"
              className="flex items-center gap-3 p-3 rounded-xl bg-[#0a0e17] border border-[#1e2d45] hover:border-[#00d4ff]/40 transition-colors group"
            >
              <div className="w-8 h-8 rounded-lg bg-[#00d4ff]/10 flex items-center justify-center">
                <svg className="w-4 h-4 text-[#00d4ff]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <div>
                <p className="text-[#e2e8f0] text-sm font-medium">Все задачи</p>
                <p className="text-[#8899aa] text-xs">Список задач</p>
              </div>
            </Link>

            <Link
              to="/interview"
              className="flex items-center gap-3 p-3 rounded-xl bg-[#0a0e17] border border-[#1e2d45] hover:border-[#ff9500]/40 transition-colors group"
            >
              <div className="w-8 h-8 rounded-lg bg-[#ff9500]/10 flex items-center justify-center">
                <svg className="w-4 h-4 text-[#ff9500]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
              <div>
                <p className="text-[#e2e8f0] text-sm font-medium">Интервью</p>
                <p className="text-[#8899aa] text-xs">Подготовка к собеседованию</p>
              </div>
            </Link>

            <Link
              to="/roadmap"
              className="flex items-center gap-3 p-3 rounded-xl bg-[#0a0e17] border border-[#1e2d45] hover:border-[#00e676]/40 transition-colors group"
            >
              <div className="w-8 h-8 rounded-lg bg-[#00e676]/10 flex items-center justify-center">
                <svg className="w-4 h-4 text-[#00e676]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                </svg>
              </div>
              <div>
                <p className="text-[#e2e8f0] text-sm font-medium">Роудмап</p>
                <p className="text-[#8899aa] text-xs">Путь обучения</p>
              </div>
            </Link>

            <Link
              to="/analytics"
              className="flex items-center gap-3 p-3 rounded-xl bg-[#0a0e17] border border-[#1e2d45] hover:border-purple-400/40 transition-colors group"
            >
              <div className="w-8 h-8 rounded-lg bg-purple-400/10 flex items-center justify-center">
                <svg className="w-4 h-4 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <div>
                <p className="text-[#e2e8f0] text-sm font-medium">Аналитика</p>
                <p className="text-[#8899aa] text-xs">Статистика прогресса</p>
              </div>
            </Link>
          </div>
        </div>
      </div>

      {/* Recommended Tasks */}
      {analytics?.recommended_tasks && analytics.recommended_tasks.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-[#e2e8f0] font-semibold">Рекомендованные задачи</h2>
            <Link to="/tasks" className="text-[#00d4ff] text-sm hover:underline">
              Все задачи →
            </Link>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {analytics.recommended_tasks.slice(0, 3).map((task) => (
              <RecommendedTaskCard key={task.id} task={task} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
