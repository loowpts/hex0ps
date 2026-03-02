import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useTasks } from '@/api/hooks/useTasks'
import type { Task, TaskCategory, TaskDifficulty, TaskStatus } from '@/types'

const CATEGORIES: { value: string; label: string }[] = [
  { value: '', label: 'Все' },
  { value: 'linux', label: 'Linux' },
  { value: 'systemd', label: 'Systemd' },
  { value: 'nginx', label: 'Nginx' },
  { value: 'docker', label: 'Docker' },
  { value: 'networks', label: 'Сети' },
  { value: 'git', label: 'Git' },
  { value: 'cicd', label: 'CI/CD' },
]

const DIFFICULTIES: { value: string; label: string }[] = [
  { value: '', label: 'Любая' },
  { value: 'beginner', label: 'Начинающий' },
  { value: 'intermediate', label: 'Средний' },
  { value: 'advanced', label: 'Сложный' },
]

const TASK_TYPES: { value: string; label: string }[] = [
  { value: '', label: 'Все типы' },
  { value: 'regular', label: 'Обычная' },
  { value: 'break_and_fix', label: 'Break&Fix' },
]

const STATUSES: { value: string; label: string }[] = [
  { value: '', label: 'Все статусы' },
  { value: 'not_started', label: 'Не начата' },
  { value: 'in_progress', label: 'В процессе' },
  { value: 'completed', label: 'Выполнена' },
  { value: 'failed', label: 'Провалена' },
]

const DIFF_COLORS: Record<string, string> = {
  beginner: 'bg-[#00e676]/10 text-[#00e676] border-[#00e676]/30',
  intermediate: 'bg-[#ff9500]/10 text-[#ff9500] border-[#ff9500]/30',
  advanced: 'bg-red-500/10 text-red-400 border-red-400/30',
}

const STATUS_COLORS: Record<string, string> = {
  not_started: 'text-[#8899aa]',
  in_progress: 'text-[#00d4ff]',
  completed: 'text-[#00e676]',
  failed: 'text-red-400',
}

const STATUS_LABELS: Record<string, string> = {
  not_started: 'Не начата',
  in_progress: 'В процессе',
  completed: 'Выполнена',
  failed: 'Провалена',
}

const CATEGORY_ICONS: Record<string, string> = {
  linux: '🐧',
  nginx: '🌐',
  systemd: '⚙️',
  docker: '🐳',
  networks: '🔌',
  git: '📦',
  cicd: '🚀',
  onboarding: '👋',
}

function FilterPill({
  value: _value,
  label,
  active,
  onClick,
}: {
  value?: string
  label: string
  active: boolean
  onClick: () => void
}) {
  return (
    <button
      onClick={onClick}
      className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors border ${
        active
          ? 'bg-[#00d4ff]/10 text-[#00d4ff] border-[#00d4ff]/40'
          : 'bg-[#0f1520] text-[#8899aa] border-[#1e2d45] hover:border-[#00d4ff]/30 hover:text-[#e2e8f0]'
      }`}
    >
      {label}
    </button>
  )
}

function TaskCard({ task }: { task: Task }) {
  const icon = CATEGORY_ICONS[task.category] ?? '📋'
  const diffClass = DIFF_COLORS[task.difficulty] ?? 'bg-[#1e2d45] text-[#8899aa] border-[#1e2d45]'
  const statusColor = task.user_status ? STATUS_COLORS[task.user_status] : STATUS_COLORS.not_started
  const statusLabel = task.user_status ? STATUS_LABELS[task.user_status] : STATUS_LABELS.not_started

  return (
    <Link
      to={`/tasks/${task.id}`}
      className={`block bg-[#0f1520] border rounded-2xl p-5 hover:border-[#00d4ff]/40 transition-all group ${
        task.is_locked ? 'opacity-50 pointer-events-none border-[#1e2d45]' : 'border-[#1e2d45]'
      }`}
    >
      <div className="flex items-start justify-between gap-2 mb-3">
        <div className="flex items-center gap-2">
          <span className="text-xl">{icon}</span>
          <span className="text-xs text-[#8899aa] uppercase tracking-wide">{task.category_display}</span>
        </div>
        {task.is_locked && (
          <svg className="w-4 h-4 text-[#8899aa] shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
        )}
      </div>

      <h3 className="text-[#e2e8f0] font-medium text-sm mb-3 group-hover:text-[#00d4ff] transition-colors line-clamp-2">
        {task.title_ru}
      </h3>

      <div className="flex flex-wrap items-center gap-2">
        <span className={`text-xs px-2 py-0.5 rounded-md border ${diffClass}`}>
          {task.difficulty_display}
        </span>

        {task.task_type === 'break_and_fix' && (
          <span className="text-xs px-2 py-0.5 rounded-md bg-red-500/10 text-red-400 border border-red-400/30">
            Break&Fix
          </span>
        )}

        <span className="ml-auto text-xs font-semibold text-[#00e676]">+{task.xp_reward} XP</span>
      </div>

      <div className="flex items-center justify-between mt-3 pt-3 border-t border-[#1e2d45]">
        <span className={`text-xs font-medium ${statusColor}`}>{statusLabel}</span>
        {task.user_task?.completed_at && (
          <svg className="w-4 h-4 text-[#00e676]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        )}
      </div>
    </Link>
  )
}

function SkeletonCard() {
  return (
    <div className="bg-[#0f1520] border border-[#1e2d45] rounded-2xl p-5 animate-pulse">
      <div className="h-4 bg-[#1e2d45] rounded w-1/3 mb-3" />
      <div className="h-4 bg-[#1e2d45] rounded w-3/4 mb-2" />
      <div className="h-4 bg-[#1e2d45] rounded w-1/2 mb-4" />
      <div className="h-6 bg-[#1e2d45] rounded w-1/4" />
    </div>
  )
}

export default function Tasks() {
  const [category, setCategory] = useState('')
  const [difficulty, setDifficulty] = useState('')
  const [taskType, setTaskType] = useState('')
  const [status, setStatus] = useState('')

  const filters = {
    ...(category ? { category: category as TaskCategory } : {}),
    ...(difficulty ? { difficulty: difficulty as TaskDifficulty } : {}),
    ...(taskType ? { task_type: taskType } : {}),
    ...(status ? { status: status as TaskStatus } : {}),
  }

  const { data: tasks, isLoading, error } = useTasks(filters)

  return (
    <div className="min-h-screen bg-[#0a0e17] p-6 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-[#e2e8f0] mb-1">Задачи</h1>
        <p className="text-[#8899aa] text-sm">Практические DevOps задачи с реальными сценариями</p>
      </div>

      {/* Category Tabs */}
      <div className="flex flex-wrap gap-2 mb-5">
        {CATEGORIES.map((cat) => (
          <button
            key={cat.value}
            onClick={() => setCategory(cat.value)}
            className={`px-4 py-2 rounded-xl text-sm font-medium transition-colors ${
              category === cat.value
                ? 'bg-[#00d4ff] text-[#0a0e17]'
                : 'bg-[#0f1520] text-[#8899aa] border border-[#1e2d45] hover:text-[#e2e8f0]'
            }`}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-2 mb-6">
        <div className="flex flex-wrap gap-2">
          {DIFFICULTIES.map((d) => (
            <FilterPill
              key={d.value}
              value={d.value}
              label={d.label}
              active={difficulty === d.value}
              onClick={() => setDifficulty(d.value)}
            />
          ))}
        </div>

        <div className="w-px bg-[#1e2d45] mx-1 self-stretch hidden sm:block" />

        <div className="flex flex-wrap gap-2">
          {TASK_TYPES.map((t) => (
            <FilterPill
              key={t.value}
              value={t.value}
              label={t.label}
              active={taskType === t.value}
              onClick={() => setTaskType(t.value)}
            />
          ))}
        </div>

        <div className="w-px bg-[#1e2d45] mx-1 self-stretch hidden sm:block" />

        <div className="flex flex-wrap gap-2">
          {STATUSES.map((s) => (
            <FilterPill
              key={s.value}
              value={s.value}
              label={s.label}
              active={status === s.value}
              onClick={() => setStatus(s.value)}
            />
          ))}
        </div>
      </div>

      {/* Tasks Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      ) : error ? (
        <div className="text-center py-16">
          <p className="text-red-400">Ошибка загрузки задач</p>
        </div>
      ) : tasks && tasks.length > 0 ? (
        <>
          <p className="text-[#8899aa] text-sm mb-4">
            Найдено задач: <span className="text-[#e2e8f0] font-medium">{tasks.length}</span>
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {tasks.map((task) => (
              <TaskCard key={task.id} task={task} />
            ))}
          </div>
        </>
      ) : (
        <div className="text-center py-16">
          <p className="text-[#8899aa] text-lg mb-2">Задачи не найдены</p>
          <p className="text-[#8899aa] text-sm">Попробуйте изменить фильтры</p>
          <button
            onClick={() => {
              setCategory('')
              setDifficulty('')
              setTaskType('')
              setStatus('')
            }}
            className="mt-4 px-4 py-2 rounded-xl text-sm text-[#00d4ff] border border-[#00d4ff]/30 hover:bg-[#00d4ff]/10 transition-colors"
          >
            Сбросить фильтры
          </button>
        </div>
      )}
    </div>
  )
}
