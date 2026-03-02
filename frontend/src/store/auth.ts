import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User } from '@/types'

interface AuthStore {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  setUser: (user: User) => void
  setTokens: (access: string, refresh: string) => void
  setAccessToken: (token: string) => void
  updateUser: (partial: Partial<User>) => void
  logout: () => void
  isAuthenticated: boolean
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,

      setUser: (user) => set({ user }),

      setTokens: (access, refresh) =>
        set({ accessToken: access, refreshToken: refresh }),

      setAccessToken: (token) => set({ accessToken: token }),

      updateUser: (partial) => {
        const current = get().user
        if (current) set({ user: { ...current, ...partial } })
      },

      logout: () => set({ user: null, accessToken: null, refreshToken: null }),

      get isAuthenticated() {
        return !!get().accessToken && !!get().user
      },
    }),
    {
      name: 'devops-auth',
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        user: state.user,
      }),
    }
  )
)

/** Синхронная проверка токена из localStorage (до гидрации Zustand) */
export function hasStoredToken(): boolean {
  try {
    const raw = localStorage.getItem('devops-auth')
    if (!raw) return false
    return !!JSON.parse(raw)?.state?.accessToken
  } catch {
    return false
  }
}

/** Получить токен из store или localStorage (до гидрации Zustand) */
export function getStoredToken(): string | null {
  const storeToken = useAuthStore.getState().accessToken
  if (storeToken) return storeToken
  try {
    const raw = localStorage.getItem('devops-auth')
    if (raw) return JSON.parse(raw)?.state?.accessToken ?? null
  } catch { /* ignore */ }
  return null
}
