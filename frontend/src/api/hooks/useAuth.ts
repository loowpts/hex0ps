import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { api } from '@/api/client'
import { useAuthStore, hasStoredToken } from '@/store/auth'
import type { User } from '@/types'

export function useMe() {
  const storeToken = useAuthStore((s) => s.accessToken)
  const isAuthenticated = storeToken !== null ? !!storeToken : hasStoredToken()
  return useQuery<User>({
    queryKey: ['me'],
    queryFn: () => api.get('/users/me/').then((r) => r.data),
    enabled: isAuthenticated,
  })
}

export function useLogin() {
  const { setTokens, setUser } = useAuthStore()
  const navigate = useNavigate()
  const qc = useQueryClient()

  return useMutation({
    mutationFn: (data: { username: string; password: string }) =>
      api.post('/auth/login/', data).then((r) => r.data),
    onSuccess: (data) => {
      setTokens(data.access, data.refresh)
      setUser(data.user)
      qc.setQueryData(['me'], data.user)
      navigate('/dashboard')
    },
    onError: () => {
      toast.error('Неверный никнейм или пароль')
    },
  })
}

export function useLogout() {
  const { logout } = useAuthStore()
  const navigate = useNavigate()
  const qc = useQueryClient()

  return () => {
    logout()
    qc.clear()
    navigate('/login')
  }
}

export function useUpdateProfile() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<{ username: string; bio: string; avatar_url: string }>) =>
      api.patch('/users/me/', data).then((r) => r.data),
    onSuccess: (data) => {
      qc.setQueryData(['me'], data)
      toast.success('Профиль обновлён')
    },
  })
}

export function useUpdateSettings() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<{ is_public: boolean; onboarding_done: boolean }>) =>
      api.patch('/users/me/settings/', data).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['me'] }),
  })
}
