import { useHotkeys } from 'react-hotkeys-hook'

interface HotkeyConfig {
  onCommandPalette?: () => void
  onHint?: () => void
  onReplay?: () => void
  onNotes?: () => void
  onTerminal?: () => void
  onCheck?: () => void
}

export function useAppHotkeys(config: HotkeyConfig) {
  // Ctrl+K — Command Palette
  useHotkeys('ctrl+k, meta+k', (e) => {
    e.preventDefault()
    config.onCommandPalette?.()
  })

  // Ctrl+H — следующая подсказка
  useHotkeys('ctrl+h', (e) => {
    e.preventDefault()
    config.onHint?.()
  }, { enableOnFormTags: false })

  // Ctrl+R — Replay
  useHotkeys('ctrl+r', (e) => {
    e.preventDefault()
    config.onReplay?.()
  }, { enableOnFormTags: false })

  // Ctrl+N — фокус на заметки
  useHotkeys('ctrl+n', (e) => {
    e.preventDefault()
    config.onNotes?.()
  }, { enableOnFormTags: false })

  // Ctrl+T — фокус на терминал
  useHotkeys('ctrl+t', (e) => {
    e.preventDefault()
    config.onTerminal?.()
  })

  // Ctrl+Enter — проверить задачу
  useHotkeys('ctrl+enter', (e) => {
    e.preventDefault()
    config.onCheck?.()
  })
}
