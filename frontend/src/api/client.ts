import axios from 'axios'
import { useAuthStore } from '@/store/auth'

const BASE_URL = import.meta.env.VITE_API_URL || ''

export const api = axios.create({
  baseURL: `${BASE_URL}/api`,
  headers: { 'Content-Type': 'application/json' },
})

// Добавляем JWT к каждому запросу
api.interceptors.request.use((config) => {
  let token = useAuthStore.getState().accessToken
  if (!token) {
    // Fallback: читаем напрямую из localStorage пока Zustand ещё не гидрировался
    try {
      const raw = localStorage.getItem('devops-auth')
      if (raw) token = JSON.parse(raw)?.state?.accessToken ?? null
    } catch { /* ignore */ }
  }
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// При 401 — обновляем токен и повторяем запрос
let isRefreshing = false
let failedQueue: Array<{ resolve: (value: string) => void; reject: (error: unknown) => void }> = []

const processQueue = (error: unknown, token: string | null) => {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) reject(error)
    else resolve(token!)
  })
  failedQueue = []
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status !== 401 || originalRequest._retry) {
      return Promise.reject(error)
    }

    const { setAccessToken, logout } = useAuthStore.getState()
    let { refreshToken } = useAuthStore.getState()
    if (!refreshToken) {
      try {
        const raw = localStorage.getItem('devops-auth')
        if (raw) refreshToken = JSON.parse(raw)?.state?.refreshToken ?? null
      } catch { /* ignore */ }
    }

    if (!refreshToken) {
      logout()
      return Promise.reject(error)
    }

    if (isRefreshing) {
      return new Promise<string>((resolve, reject) => {
        failedQueue.push({ resolve, reject })
      }).then((token) => {
        originalRequest.headers.Authorization = `Bearer ${token}`
        return api(originalRequest)
      })
    }

    originalRequest._retry = true
    isRefreshing = true

    try {
      const response = await axios.post(`${BASE_URL}/api/auth/refresh/`, {
        refresh: refreshToken,
      })
      const newToken = response.data.access
      setAccessToken(newToken)
      processQueue(null, newToken)
      originalRequest.headers.Authorization = `Bearer ${newToken}`
      return api(originalRequest)
    } catch (refreshError) {
      processQueue(refreshError, null)
      logout()
      window.location.href = '/login'
      return Promise.reject(refreshError)
    } finally {
      isRefreshing = false
    }
  }
)
