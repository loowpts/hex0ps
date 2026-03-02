import { useState } from 'react'
import { useMe, useUpdateSettings } from '@/api/hooks/useAuth'
import { useAnalytics } from '@/api/hooks/useAnalytics'
import { useSettingsStore } from '@/store/settings'
import type { Achievement, Certificate } from '@/types'
import { format } from 'date-fns'
import { ru } from 'date-fns/locale'

// ─── AchievementBadge ────────────────────────────────────────────────────────

function AchievementBadge({ achievement }: { achievement: Achievement }) {
  const [tooltip, setTooltip] = useState(false)

  return (
    <div
      className="relative"
      onMouseEnter={() => setTooltip(true)}
      onMouseLeave={() => setTooltip(false)}
    >
      <div className="w-14 h-14 bg-[#0a0e17] border border-[#1e2d45] rounded-2xl flex items-center justify-center text-2xl cursor-default hover:border-[#00d4ff]/40 transition-colors">
        {achievement.icon}
      </div>
      {tooltip && (
        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 z-10 w-48 bg-[#1e2d45] border border-[#1e2d45] rounded-xl p-2 shadow-xl pointer-events-none">
          <p className="text-[#e2e8f0] text-xs font-medium">{achievement.title_ru}</p>
          {achievement.description_ru && (
            <p className="text-[#8899aa] text-xs mt-0.5">{achievement.description_ru}</p>
          )}
          {achievement.earned_at && (
            <p className="text-[#8899aa] text-xs mt-1">
              {format(new Date(achievement.earned_at), 'd MMM yyyy', { locale: ru })}
            </p>
          )}
        </div>
      )}
    </div>
  )
}

// ─── CertificateCard ─────────────────────────────────────────────────────────

function CertificateCard({ cert }: { cert: Certificate }) {
  return (
    <div className="flex items-center justify-between p-4 bg-[#0a0e17] border border-[#1e2d45] rounded-xl">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-[#ff9500]/10 flex items-center justify-center">
          <svg className="w-5 h-5 text-[#ff9500]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
          </svg>
        </div>
        <div>
          <p className="text-[#e2e8f0] text-sm font-medium">{cert.category_display}</p>
          <p className="text-[#8899aa] text-xs">
            Выдан: {format(new Date(cert.issued_at), 'd MMM yyyy', { locale: ru })}
          </p>
        </div>
      </div>
      {cert.pdf_url && (
        <a
          href={cert.pdf_url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-[#ff9500]/10 text-[#ff9500] border border-[#ff9500]/30 hover:bg-[#ff9500]/20 transition-colors"
        >
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Скачать
        </a>
      )}
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

// ─── Toggle ──────────────────────────────────────────────────────────────────

function Toggle({ enabled, onChange }: { enabled: boolean; onChange: (v: boolean) => void }) {
  return (
    <button
      onClick={() => onChange(!enabled)}
      className={`relative inline-flex h-6 w-11 rounded-full transition-colors focus:outline-none ${
        enabled ? 'bg-[#00d4ff]' : 'bg-[#1e2d45]'
      }`}
    >
      <span
        className={`inline-block h-4 w-4 rounded-full bg-white shadow transform transition-transform mt-1 ${
          enabled ? 'translate-x-6' : 'translate-x-1'
        }`}
      />
    </button>
  )
}

const LEVEL_COLORS: Record<string, string> = {
  beginner: 'text-[#8899aa] border-[#8899aa]',
  junior: 'text-[#00e676] border-[#00e676]',
  middle: 'text-[#00d4ff] border-[#00d4ff]',
  senior: 'text-[#ff9500] border-[#ff9500]',
  pro: 'text-purple-400 border-purple-400',
}

// ─── Main ────────────────────────────────────────────────────────────────────

export default function Profile() {
  const { data: user, isLoading: userLoading } = useMe()
  const { data: analytics } = useAnalytics()
  const updateSettings = useUpdateSettings()
  const { theme, toggleTheme } = useSettingsStore()

  const [achievements] = useState<Achievement[]>([
    { icon: '🚀', title_ru: 'Первый запуск', description_ru: 'Выполнена первая задача' },
    { icon: '🔥', title_ru: 'Стрик 7 дней', description_ru: 'Активность 7 дней подряд' },
    { icon: '🐳', title_ru: 'Докер-мастер', description_ru: 'Завершены все задачи Docker' },
  ])

  const [certificates] = useState<Certificate[]>([])

  const handlePrivacyToggle = (isPublic: boolean) => {
    updateSettings.mutate({ is_public: isPublic })
  }

  if (userLoading) {
    return (
      <div className="min-h-screen bg-[#0a0e17] flex items-center justify-center">
        <div className="animate-pulse space-y-4 w-full max-w-2xl px-6">
          <div className="h-24 bg-[#1e2d45] rounded-2xl" />
          <div className="h-64 bg-[#1e2d45] rounded-2xl" />
        </div>
      </div>
    )
  }

  if (!user) return null

  const levelColor = LEVEL_COLORS[user.level] ?? 'text-[#e2e8f0] border-[#e2e8f0]'

  return (
    <div className="min-h-screen bg-[#0a0e17] p-6 max-w-4xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-[#e2e8f0]">Профиль</h1>

      {/* Header card */}
      <div className="bg-[#0f1520] border border-[#1e2d45] rounded-2xl p-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-5">
          {/* Avatar */}
          <div className="w-20 h-20 rounded-2xl bg-[#1e2d45] border border-[#1e2d45] flex items-center justify-center overflow-hidden shrink-0">
            {user.avatar_url ? (
              <img src={user.avatar_url} alt={user.username} className="w-full h-full object-cover" />
            ) : (
              <span className="text-3xl font-bold text-[#00d4ff]">
                {user.username.charAt(0).toUpperCase()}
              </span>
            )}
          </div>

          {/* Info */}
          <div className="flex-1">
            <div className="flex flex-wrap items-center gap-2 mb-1">
              <h2 className="text-xl font-bold text-[#e2e8f0]">{user.username}</h2>
              <span className={`text-xs font-semibold px-2.5 py-1 rounded-lg border ${levelColor}`}>
                {user.level_display}
              </span>
              <span className="text-xs px-2.5 py-1 rounded-lg bg-[#ff9500]/10 text-[#ff9500] border border-[#ff9500]/30">
                🔥 {user.streak} дн.
              </span>
            </div>
            <p className="text-[#8899aa] text-sm">{user.email}</p>
            {user.bio && <p className="text-[#8899aa] text-sm mt-1">{user.bio}</p>}
            <p className="text-[#8899aa] text-xs mt-2">
              На платформе с{' '}
              {format(new Date(user.created_at), 'd MMMM yyyy', { locale: ru })}
            </p>
          </div>

          {/* XP */}
          <div className="sm:text-right">
            <p className="text-2xl font-bold text-[#00e676]">{user.xp} XP</p>
            <p className="text-[#8899aa] text-xs">ещё {user.xp_to_next_level} XP</p>
          </div>
        </div>

        {/* XP Progress */}
        <div className="mt-4">
          <div className="flex justify-between text-xs text-[#8899aa] mb-1">
            <span>Прогресс до следующего уровня</span>
            <span>{user.level_progress_pct}%</span>
          </div>
          <div className="h-2.5 bg-[#1e2d45] rounded-full overflow-hidden">
            <div
              className="h-full rounded-full bg-gradient-to-r from-[#00d4ff] to-[#00e676] transition-all duration-700"
              style={{ width: `${user.level_progress_pct}%` }}
            />
          </div>
        </div>
      </div>

      {/* Skills */}
      {analytics && (
        <div className="bg-[#0f1520] border border-[#1e2d45] rounded-2xl p-5">
          <h2 className="text-[#e2e8f0] font-semibold mb-4">Навыки по категориям</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(analytics.skills).map(([name, skill]) => (
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
      )}

      {/* Achievements */}
      {achievements.length > 0 && (
        <div className="bg-[#0f1520] border border-[#1e2d45] rounded-2xl p-5">
          <h2 className="text-[#e2e8f0] font-semibold mb-4">
            Достижения <span className="text-[#8899aa] font-normal text-sm">({achievements.length})</span>
          </h2>
          <div className="flex flex-wrap gap-3">
            {achievements.map((ach, i) => (
              <AchievementBadge key={i} achievement={ach} />
            ))}
          </div>
        </div>
      )}

      {/* Certificates */}
      <div className="bg-[#0f1520] border border-[#1e2d45] rounded-2xl p-5">
        <h2 className="text-[#e2e8f0] font-semibold mb-4">
          Сертификаты{' '}
          <span className="text-[#8899aa] font-normal text-sm">({certificates.length})</span>
        </h2>
        {certificates.length > 0 ? (
          <div className="space-y-3">
            {certificates.map((cert) => (
              <CertificateCard key={cert.cert_id} cert={cert} />
            ))}
          </div>
        ) : (
          <p className="text-[#8899aa] text-sm">
            Выполните все задачи категории чтобы получить сертификат
          </p>
        )}
      </div>

      {/* Settings */}
      <div className="bg-[#0f1520] border border-[#1e2d45] rounded-2xl p-5">
        <h2 className="text-[#e2e8f0] font-semibold mb-4">Настройки</h2>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-[#e2e8f0] text-sm font-medium">Тёмная тема</p>
              <p className="text-[#8899aa] text-xs">Переключить тему оформления</p>
            </div>
            <Toggle enabled={theme === 'dark'} onChange={toggleTheme} />
          </div>

          <div className="h-px bg-[#1e2d45]" />

          <div className="flex items-center justify-between">
            <div>
              <p className="text-[#e2e8f0] text-sm font-medium">Публичный профиль</p>
              <p className="text-[#8899aa] text-xs">Другие пользователи могут видеть ваш профиль</p>
            </div>
            <Toggle
              enabled={user.is_public}
              onChange={handlePrivacyToggle}
            />
          </div>
        </div>
      </div>
    </div>
  )
}
