import { useEffect } from 'react'
import { useSettingsStore } from '@/store/settings'

export function useTheme() {
  const { theme, toggleTheme } = useSettingsStore()

  useEffect(() => {
    const root = document.documentElement
    root.classList.toggle('dark', theme === 'dark')
    root.classList.toggle('light', theme === 'light')
  }, [theme])

  return { theme, toggleTheme, isDark: theme === 'dark' }
}
