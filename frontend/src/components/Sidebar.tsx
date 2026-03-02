import { NavLink, useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store/auth'

const NAV_ITEMS = [
  { to: '/dashboard',  icon: '⬡',  label: 'Dashboard' },
  { to: '/tasks',      icon: '⚡',  label: 'Задачи' },
  { to: '/courses',    icon: '🎓',  label: 'Курсы' },
  { to: '/daily',      icon: '⚔️',  label: 'Daily' },
  { to: '/playground',   icon: '🖥️',  label: 'Playground' },
  { to: '/cheatsheets',  icon: '📋',  label: 'Шпаргалки' },
  { to: '/interview',    icon: '🎯',  label: 'Собеседование' },
  { to: '/analytics',  icon: '📊',  label: 'Аналитика' },
  { to: '/notes',      icon: '📝',  label: 'Заметки' },
  { to: '/roadmap',    icon: '🗺',  label: 'Roadmap' },
  { to: '/profile',    icon: '👤',  label: 'Профиль' },
]

export default function Sidebar() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <aside className="w-56 shrink-0 flex flex-col bg-[#0f1520] border-r border-[#1e2d45] min-h-screen">
      {/* Logo */}
      <div className="px-4 py-4 border-b border-[#1e2d45]">
        <span className="text-[#00d4ff] font-bold text-lg tracking-wider">HexOps</span>
        <span className="ml-1 text-[#445566] text-sm">DevOps Lab</span>
      </div>

      {/* User info */}
      {user && (
        <div className="px-4 py-3 border-b border-[#1e2d45]">
          <div className="text-[#cdd6f4] text-sm font-medium truncate">{user.username}</div>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-xs text-[#00d4ff] uppercase tracking-wide">{user.level}</span>
            <span className="text-xs text-[#445566]">·</span>
            <span className="text-xs text-[#8899aa]">{user.xp} XP</span>
          </div>
        </div>
      )}

      {/* Nav links */}
      <nav className="flex-1 py-2">
        {NAV_ITEMS.map(({ to, icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-2.5 text-sm transition-colors ${
                isActive
                  ? 'bg-[#00d4ff1a] text-[#00d4ff] border-r-2 border-[#00d4ff]'
                  : 'text-[#8899aa] hover:text-[#cdd6f4] hover:bg-[#1e2d45]'
              }`
            }
          >
            <span className="text-base w-5 text-center">{icon}</span>
            {label}
          </NavLink>
        ))}
      </nav>

      {/* Bottom actions */}
      <div className="border-t border-[#1e2d45] py-2">
        <NavLink
          to="/status"
          className={({ isActive }) =>
            `flex items-center gap-3 px-4 py-2.5 text-sm transition-colors ${
              isActive ? 'text-[#00d4ff]' : 'text-[#8899aa] hover:text-[#cdd6f4] hover:bg-[#1e2d45]'
            }`
          }
        >
          <span className="text-base w-5 text-center">🟢</span>
          Статус системы
        </NavLink>
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-[#8899aa] hover:text-red-400 hover:bg-[#1e2d45] transition-colors"
        >
          <span className="text-base w-5 text-center">⏻</span>
          Выйти
        </button>
      </div>
    </aside>
  )
}
