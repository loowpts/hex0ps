import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { TerminalTheme } from '@/types'

interface SettingsStore {
  theme: 'dark' | 'light'
  terminalFontSize: number
  terminalTheme: TerminalTheme
  toggleTheme: () => void
  setTerminalFontSize: (size: number) => void
  setTerminalTheme: (theme: TerminalTheme) => void
}

export const useSettingsStore = create<SettingsStore>()(
  persist(
    (set, get) => ({
      theme: 'dark',
      terminalFontSize: 14,
      terminalTheme: 'dracula',

      toggleTheme: () => {
        const next = get().theme === 'dark' ? 'light' : 'dark'
        set({ theme: next })
        // Применяем класс к <html>
        document.documentElement.classList.toggle('dark', next === 'dark')
        document.documentElement.classList.toggle('light', next === 'light')
      },

      setTerminalFontSize: (size) =>
        set({ terminalFontSize: Math.min(20, Math.max(12, size)) }),

      setTerminalTheme: (theme) => set({ terminalTheme: theme }),
    }),
    { name: 'devops-settings' }
  )
)
