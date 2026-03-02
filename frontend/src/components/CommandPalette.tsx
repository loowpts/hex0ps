/**
 * CommandPalette — глобальная палитра команд.
 * Открывается по Ctrl+K / Cmd+K. Использует библиотеку cmdk.
 */
import { useState, useEffect } from 'react'
import { Command } from 'cmdk'
import { useNavigate } from 'react-router-dom'
import { useHotkeys } from 'react-hotkeys-hook'
import { useTasks } from '@/api/hooks/useTasks'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/api/client'
import type { CheatSheetList } from '@/types'

export default function CommandPalette() {
  const [open, setOpen] = useState(false)
  const navigate = useNavigate()
  const { data: tasks } = useTasks()
  const { data: cheatsheets } = useQuery<CheatSheetList[]>({
    queryKey: ['cheatsheets-palette'],
    queryFn: () => api.get('/cheatsheets/').then((r) => r.data),
    staleTime: 1000 * 60 * 10,
    enabled: open,
  })

  useHotkeys('ctrl+k, meta+k', (e) => {
    e.preventDefault()
    setOpen((v) => !v)
  })

  // Закрытие по Escape обрабатывается cmdk автоматически
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setOpen(false)
    }
    document.addEventListener('keydown', handler)
    return () => document.removeEventListener('keydown', handler)
  }, [])

  const runAction = (fn: () => void) => {
    fn()
    setOpen(false)
  }

  if (!open) return null

  const NAV_ITEMS = [
    { icon: '🏠', label: 'Dashboard', path: '/dashboard', desc: 'Главная страница' },
    { icon: '⚡', label: 'Задачи', path: '/tasks', desc: 'Список задач' },
    { icon: '🎓', label: 'Курсы', path: '/courses', desc: 'LMS курсы' },
    { icon: '⚔️', label: 'Daily', path: '/daily', desc: 'Задача дня' },
    { icon: '🖥️', label: 'Playground', path: '/playground', desc: 'Свободный терминал' },
    { icon: '📋', label: 'Шпаргалки', path: '/cheatsheets', desc: 'Команды и примеры' },
    { icon: '🗺️', label: 'Роудмап', path: '/roadmap', desc: 'Карта обучения' },
    { icon: '📊', label: 'Аналитика', path: '/analytics', desc: 'Статистика и прогресс' },
    { icon: '📝', label: 'Заметки', path: '/notes', desc: 'Ваши конспекты' },
    { icon: '🎤', label: 'Собеседование', path: '/interview', desc: 'Подготовка к интервью' },
    { icon: '👤', label: 'Профиль', path: '/profile', desc: 'Настройки аккаунта' },
  ]

  return (
    <div className="fixed inset-0 z-[9999] flex items-start justify-center pt-[10vh] px-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={() => setOpen(false)}
      />

      {/* Panel */}
      <div className="relative w-full max-w-xl">
        <Command
          className="bg-[#0f1520] border border-[#1e2d45] rounded-2xl shadow-2xl overflow-hidden"
          loop
        >
          {/* Input */}
          <div className="flex items-center gap-3 px-4 py-3.5 border-b border-[#1e2d45]">
            <svg className="w-4 h-4 text-[#8899aa] shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <Command.Input
              placeholder="Поиск задач, страниц..."
              className="flex-1 bg-transparent text-[#e2e8f0] placeholder-[#4a5568] outline-none text-sm"
              autoFocus
            />
            <kbd className="text-xs text-[#4a5568] border border-[#1e2d45] rounded px-1.5 py-0.5 font-mono">ESC</kbd>
          </div>

          {/* Results */}
          <Command.List className="max-h-80 overflow-y-auto py-2">
            <Command.Empty className="px-4 py-8 text-center text-[#4a5568] text-sm">
              Ничего не найдено
            </Command.Empty>

            {/* Навигация */}
            <Command.Group heading="Навигация">
              {NAV_ITEMS.map((item) => (
                <Command.Item
                  key={item.path}
                  value={`${item.label} ${item.desc}`}
                  onSelect={() => runAction(() => navigate(item.path))}
                  className="flex items-center gap-3 px-4 py-2.5 cursor-pointer data-[selected=true]:bg-[#00d4ff]/10 transition-colors"
                >
                  <span className="text-base w-6 text-center shrink-0">{item.icon}</span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-[#e2e8f0] truncate">{item.label}</p>
                    <p className="text-xs text-[#8899aa] truncate">{item.desc}</p>
                  </div>
                </Command.Item>
              ))}
            </Command.Group>

            {/* Задачи */}
            {tasks && tasks.length > 0 && (
              <Command.Group heading="Задачи">
                {tasks.slice(0, 8).map((task) => (
                  <Command.Item
                    key={task.id}
                    value={`${task.title_ru} ${task.category} ${task.difficulty}`}
                    onSelect={() => runAction(() => navigate(`/tasks/${task.id}`))}
                    className="flex items-center gap-3 px-4 py-2.5 cursor-pointer data-[selected=true]:bg-[#00d4ff]/10 transition-colors"
                  >
                    <span className="text-base w-6 text-center shrink-0">⚡</span>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-[#e2e8f0] truncate">{task.title_ru}</p>
                      <p className="text-xs text-[#8899aa] truncate">
                        {task.category_display} · {task.difficulty_display} · {task.xp_reward} XP
                      </p>
                    </div>
                  </Command.Item>
                ))}
              </Command.Group>
            )}
            {/* Шпаргалки */}
            {cheatsheets && cheatsheets.length > 0 && (
              <Command.Group heading="Шпаргалки">
                {cheatsheets.slice(0, 5).map((sheet) => (
                  <Command.Item
                    key={sheet.id}
                    value={`${sheet.title_ru} ${sheet.category} ${sheet.tags.join(' ')}`}
                    onSelect={() => runAction(() => navigate(`/cheatsheets?id=${sheet.id}`))}
                    className="flex items-center gap-3 px-4 py-2.5 cursor-pointer data-[selected=true]:bg-[#00d4ff]/10 transition-colors"
                  >
                    <span className="text-base w-6 text-center shrink-0">📋</span>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-[#e2e8f0] truncate">{sheet.title_ru}</p>
                      <p className="text-xs text-[#8899aa] truncate">
                        {sheet.category_display} · {sheet.entries_count} команд
                      </p>
                    </div>
                  </Command.Item>
                ))}
              </Command.Group>
            )}
          </Command.List>

          {/* Footer hints */}
          <div className="px-4 py-2 border-t border-[#1e2d45] flex items-center gap-4">
            {[['↑↓', 'навигация'], ['↵', 'выбрать'], ['ESC', 'закрыть']].map(([key, label]) => (
              <div key={key} className="flex items-center gap-1.5 text-[10px] text-[#4a5568]">
                <kbd className="border border-[#1e2d45] rounded px-1 py-0.5 font-mono">{key}</kbd>
                <span>{label}</span>
              </div>
            ))}
          </div>
        </Command>
      </div>

      {/* Глобальные стили для cmdk-group-heading */}
      <style>{`
        [cmdk-group-heading] {
          padding: 6px 16px;
          font-size: 10px;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.1em;
          color: #4a5568;
        }
        [cmdk-item][data-selected="true"] {
          background: rgba(0, 212, 255, 0.08);
        }
        [cmdk-item][data-selected="true"] p:first-child {
          color: #00d4ff;
        }
      `}</style>
    </div>
  )
}
