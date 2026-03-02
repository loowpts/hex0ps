import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useCourses, useSkillTree } from '@/api/hooks/useCourses'
import type { CourseList, SkillTreeNode } from '@/types'

// ─── SkillTree (простая SVG визуализация без D3) ──────────────────────────────

const STATUS_COLORS: Record<string, string> = {
  completed:   '#00e676',
  in_progress: '#00d4ff',
  available:   '#1e2d45',
  locked:      '#0f1520',
}

const STATUS_BORDER: Record<string, string> = {
  completed:   '#00e676',
  in_progress: '#00d4ff',
  available:   '#334155',
  locked:      '#1e2d45',
}

function SkillTreeNode({ node, onClick }: { node: SkillTreeNode; onClick: () => void }) {
  const isLocked = node.status === 'locked'
  return (
    <button
      onClick={onClick}
      disabled={isLocked}
      className="flex flex-col items-center gap-1 group"
    >
      <div
        className="w-16 h-16 rounded-2xl flex items-center justify-center text-2xl border-2 transition-all duration-200"
        style={{
          background: STATUS_COLORS[node.status],
          borderColor: STATUS_BORDER[node.status],
          opacity: isLocked ? 0.4 : 1,
        }}
      >
        {node.status === 'completed' ? '✓' : isLocked ? '🔒' : node.icon}
      </div>
      <span className={`text-xs text-center max-w-[80px] leading-tight ${isLocked ? 'text-[#4a5568]' : 'text-[#8899aa] group-hover:text-[#e2e8f0]'}`}>
        {node.title_ru}
      </span>
    </button>
  )
}

function SkillTree() {
  const { data, isLoading } = useSkillTree()

  if (isLoading) return <div className="h-48 bg-[#1e2d45]/30 rounded-2xl animate-pulse" />
  if (!data || data.nodes.length === 0) return null

  // Группируем по статусу для простого линейного отображения
  const completed = data.nodes.filter(n => n.status === 'completed')
  const inProgress = data.nodes.filter(n => n.status === 'in_progress')
  const available = data.nodes.filter(n => n.status === 'available')
  const locked = data.nodes.filter(n => n.status === 'locked')

  return (
    <div className="bg-[#0f1520] border border-[#1e2d45] rounded-2xl p-6 mb-8">
      <h2 className="text-[#e2e8f0] font-semibold mb-6">Дерево навыков</h2>
      <div className="flex flex-wrap gap-8 items-start">
        {[...completed, ...inProgress, ...available, ...locked].map((node) => (
          <SkillTreeNode
            key={node.id}
            node={node}
            onClick={() => {
              if (node.status !== 'locked') {
                window.location.href = `/courses/${node.id}`
              }
            }}
          />
        ))}
      </div>
      <div className="flex items-center gap-6 mt-6 flex-wrap">
        {[
          { color: '#00e676', label: 'Пройден' },
          { color: '#00d4ff', label: 'В процессе' },
          { color: '#334155', label: 'Доступен' },
          { color: '#1e2d45', label: 'Заблокирован' },
        ].map(({ color, label }) => (
          <div key={label} className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-sm border" style={{ borderColor: color, background: color + '40' }} />
            <span className="text-xs text-[#8899aa]">{label}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

// ─── CourseCard ───────────────────────────────────────────────────────────────

const DIFF_STYLES: Record<string, string> = {
  beginner:     'text-[#00e676] bg-[#00e676]/10',
  intermediate: 'text-[#ff9500] bg-[#ff9500]/10',
  advanced:     'text-red-400 bg-red-400/10',
}

const DIFF_LABELS: Record<string, string> = {
  beginner:     'Начинающий',
  intermediate: 'Средний',
  advanced:     'Продвинутый',
}

function CourseCard({ course }: { course: CourseList }) {
  const progress = course.user_progress
  const pct = course.total_lessons > 0
    ? Math.round((course.completed_lessons / course.total_lessons) * 100)
    : 0
  const isCompleted = progress?.status === 'completed'
  const isStarted = progress?.status === 'in_progress'

  return (
    <Link
      to={`/courses/${course.slug}`}
      className="block bg-[#0f1520] border border-[#1e2d45] rounded-2xl p-5 hover:border-[#00d4ff]/40 transition-all group"
    >
      <div className="flex items-start gap-4 mb-4">
        <div className="text-4xl shrink-0">{course.icon}</div>
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2 mb-1">
            <h3 className="text-[#e2e8f0] font-semibold group-hover:text-[#00d4ff] transition-colors">
              {course.title_ru}
            </h3>
            {isCompleted && (
              <span className="shrink-0 text-xs px-2 py-0.5 rounded-md bg-[#00e676]/10 text-[#00e676]">✓ Пройден</span>
            )}
          </div>
          <p className="text-[#8899aa] text-sm line-clamp-2">{course.description_ru}</p>
        </div>
      </div>

      <div className="flex items-center gap-3 mb-4 flex-wrap">
        <span className={`text-xs px-2 py-0.5 rounded-md font-medium ${DIFF_STYLES[course.difficulty]}`}>
          {DIFF_LABELS[course.difficulty]}
        </span>
        <span className="text-xs text-[#8899aa]">⏱ {course.estimated_hours} ч.</span>
        <span className="text-xs text-[#00e676] font-medium">+{course.xp_reward} XP</span>
        <span className="text-xs text-[#8899aa]">{course.total_lessons} уроков</span>
      </div>

      {isStarted || isCompleted ? (
        <div>
          <div className="flex justify-between text-xs text-[#8899aa] mb-1">
            <span>{course.completed_lessons}/{course.total_lessons} уроков</span>
            <span>{pct}%</span>
          </div>
          <div className="h-1.5 bg-[#1e2d45] rounded-full overflow-hidden">
            <div
              className="h-full rounded-full bg-gradient-to-r from-[#00d4ff] to-[#00e676] transition-all"
              style={{ width: `${pct}%` }}
            />
          </div>
        </div>
      ) : (
        <div className="text-xs text-[#00d4ff]">Начать →</div>
      )}
    </Link>
  )
}

// ─── Main ─────────────────────────────────────────────────────────────────────

const CATEGORY_FILTERS = [
  { value: '', label: 'Все' },
  { value: 'linux', label: 'Linux' },
  { value: 'docker', label: 'Docker' },
  { value: 'networks', label: 'Сети' },
  { value: 'cicd', label: 'CI/CD' },
  { value: 'devops', label: 'DevOps' },
]

export default function CourseCatalog() {
  const { data: courses, isLoading } = useCourses()
  const [category, setCategory] = useState('')

  const filtered = courses?.filter(c => !category || c.category === category) ?? []

  return (
    <div className="min-h-screen bg-[#0a0e17] p-6 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-[#e2e8f0] mb-1">Курсы</h1>
        <p className="text-[#8899aa] text-sm">Структурированные учебные треки по DevOps</p>
      </div>

      <SkillTree />

      {/* Фильтры */}
      <div className="flex gap-2 mb-6 flex-wrap">
        {CATEGORY_FILTERS.map(f => (
          <button
            key={f.value}
            onClick={() => setCategory(f.value)}
            className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              category === f.value
                ? 'bg-[#00d4ff]/10 text-[#00d4ff] border border-[#00d4ff]/40'
                : 'bg-[#0f1520] text-[#8899aa] border border-[#1e2d45] hover:border-[#00d4ff]/30'
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {/* Список курсов */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-52 bg-[#1e2d45]/30 rounded-2xl animate-pulse" />
          ))}
        </div>
      ) : filtered.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map(course => (
            <CourseCard key={course.id} course={course} />
          ))}
        </div>
      ) : (
        <div className="text-center py-16">
          <p className="text-[#8899aa]">Нет курсов в этой категории</p>
        </div>
      )}
    </div>
  )
}
