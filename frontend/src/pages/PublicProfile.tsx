import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/api/client'
import type { User, Achievement, Certificate } from '@/types'
import { format } from 'date-fns'
import { ru } from 'date-fns/locale'

interface PublicProfileData {
  user: User
  achievements: Achievement[]
  certificates: Certificate[]
  skills: Record<string, { completed: number; total: number; pct: number }>
}

function usePublicProfile(username: string) {
  return useQuery<PublicProfileData>({
    queryKey: ['public-profile', username],
    queryFn: () => api.get(`/users/${username}/public/`).then((r) => r.data),
    enabled: !!username,
    retry: false,
  })
}

const LEVEL_COLORS: Record<string, string> = {
  beginner: 'text-[#8899aa] border-[#8899aa]',
  junior: 'text-[#00e676] border-[#00e676]',
  middle: 'text-[#00d4ff] border-[#00d4ff]',
  senior: 'text-[#ff9500] border-[#ff9500]',
  pro: 'text-purple-400 border-purple-400',
}

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
        </div>
      )}
    </div>
  )
}

export default function PublicProfile() {
  const { username } = useParams<{ username: string }>()
  const { data, isLoading, error } = usePublicProfile(username ?? '')
  const [copied, setCopied] = useState(false)

  const handleShare = () => {
    navigator.clipboard.writeText(window.location.href)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#0a0e17] flex items-center justify-center">
        <div className="animate-pulse space-y-4 w-full max-w-2xl px-6">
          <div className="h-24 bg-[#1e2d45] rounded-2xl" />
          <div className="h-64 bg-[#1e2d45] rounded-2xl" />
        </div>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-[#0a0e17] flex items-center justify-center px-4">
        <div className="text-center max-w-md">
          <div className="text-6xl mb-4">🔒</div>
          <h1 className="text-2xl font-bold text-[#e2e8f0] mb-2">Профиль скрыт</h1>
          <p className="text-[#8899aa]">
            Пользователь <span className="text-[#00d4ff]">@{username}</span> скрыл свой профиль или он не существует.
          </p>
        </div>
      </div>
    )
  }

  const { user, achievements, certificates, skills } = data
  const levelColor = LEVEL_COLORS[user.level] ?? 'text-[#e2e8f0] border-[#e2e8f0]'

  return (
    <div className="min-h-screen bg-[#0a0e17] p-6 max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-[#e2e8f0]">Публичный профиль</h1>
        <button
          onClick={handleShare}
          className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium border border-[#1e2d45] text-[#8899aa] hover:border-[#00d4ff]/40 hover:text-[#00d4ff] transition-colors"
        >
          {copied ? (
            <>
              <svg className="w-4 h-4 text-[#00e676]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Скопировано!
            </>
          ) : (
            <>
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              Поделиться
            </>
          )}
        </button>
      </div>

      {/* Profile Card */}
      <div className="bg-[#0f1520] border border-[#1e2d45] rounded-2xl p-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-5">
          <div className="w-20 h-20 rounded-2xl bg-[#1e2d45] border border-[#1e2d45] flex items-center justify-center overflow-hidden shrink-0">
            {user.avatar_url ? (
              <img src={user.avatar_url} alt={user.username} className="w-full h-full object-cover" />
            ) : (
              <span className="text-3xl font-bold text-[#00d4ff]">
                {user.username.charAt(0).toUpperCase()}
              </span>
            )}
          </div>

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
            {user.bio && <p className="text-[#8899aa] text-sm">{user.bio}</p>}
            <p className="text-[#8899aa] text-xs mt-2">
              На платформе с{' '}
              {format(new Date(user.created_at), 'd MMMM yyyy', { locale: ru })}
            </p>
          </div>

          <div className="sm:text-right">
            <p className="text-2xl font-bold text-[#00e676]">{user.xp} XP</p>
            <p className="text-[#8899aa] text-xs">Рекорд стрика: {user.max_streak} дн.</p>
          </div>
        </div>

        {/* XP Progress */}
        <div className="mt-4">
          <div className="flex justify-between text-xs text-[#8899aa] mb-1">
            <span>Прогресс уровня</span>
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
      {skills && Object.keys(skills).length > 0 && (
        <div className="bg-[#0f1520] border border-[#1e2d45] rounded-2xl p-5">
          <h2 className="text-[#e2e8f0] font-semibold mb-4">Навыки</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(skills).map(([name, skill]) => (
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
      {certificates.length > 0 && (
        <div className="bg-[#0f1520] border border-[#1e2d45] rounded-2xl p-5">
          <h2 className="text-[#e2e8f0] font-semibold mb-4">
            Сертификаты <span className="text-[#8899aa] font-normal text-sm">({certificates.length})</span>
          </h2>
          <div className="space-y-3">
            {certificates.map((cert) => (
              <div key={cert.cert_id} className="flex items-center gap-3 p-4 bg-[#0a0e17] border border-[#1e2d45] rounded-xl">
                <span className="text-xl">🏆</span>
                <div>
                  <p className="text-[#e2e8f0] text-sm font-medium">{cert.category_display}</p>
                  <p className="text-[#8899aa] text-xs">
                    {format(new Date(cert.issued_at), 'd MMM yyyy', { locale: ru })}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
