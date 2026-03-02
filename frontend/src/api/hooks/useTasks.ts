import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { api } from '@/api/client'
import type { Task, TerminalSession, CheckResult, HintResult, ReplaySolution } from '@/types'

interface TaskFilters {
  category?: string
  difficulty?: string
  task_type?: string
  status?: string
}

// Список задач
export function useTasks(filters?: TaskFilters) {
  return useQuery<Task[]>({
    queryKey: ['tasks', filters],
    queryFn: () => api.get('/tasks/', { params: filters }).then((r) => r.data),
  })
}

// Детали задачи
export function useTask(taskId: number) {
  return useQuery<Task>({
    queryKey: ['task', taskId],
    queryFn: () => api.get(`/tasks/${taskId}/`).then((r) => r.data),
    enabled: !!taskId,
  })
}

// Начать задачу
export function useStartTask() {
  const qc = useQueryClient()
  return useMutation<TerminalSession, Error, number>({
    mutationFn: (taskId) => api.post(`/tasks/${taskId}/start/`).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['tasks'] }),
    onError: (error) => {
      const axiosError = error as unknown as { response?: { data?: { error?: string } } }
      toast.error(axiosError.response?.data?.error || 'Не удалось начать задачу')
    },
  })
}

// Проверить задачу
export function useCheckTask() {
  const qc = useQueryClient()
  return useMutation<CheckResult, Error, number>({
    mutationFn: (taskId) => api.post(`/tasks/${taskId}/check/`).then((r) => r.data),
    onSuccess: (_data, taskId) => {
      qc.invalidateQueries({ queryKey: ['task', taskId] })
      qc.invalidateQueries({ queryKey: ['tasks'] })
      qc.invalidateQueries({ queryKey: ['me'] })
    },
  })
}

// Получить подсказку
export function useHint() {
  return useMutation<HintResult, Error, { taskId: number; level: 1 | 2 | 3 }>({
    mutationFn: ({ taskId, level }) =>
      api.post(`/tasks/${taskId}/hint/`, { level }).then((r) => r.data),
    onError: (error) => {
      const axiosError = error as unknown as { response?: { data?: { error?: string } } }
      toast.error(axiosError.response?.data?.error || 'Ошибка получения подсказки')
    },
  })
}

// Получить эталонное решение
export function useReplay(taskId: number, enabled: boolean) {
  return useQuery<ReplaySolution>({
    queryKey: ['replay', taskId],
    queryFn: () => api.get(`/tasks/${taskId}/replay/`).then((r) => r.data),
    enabled: enabled && !!taskId,
  })
}

// Дорожная карта
export function useRoadmap() {
  return useQuery({
    queryKey: ['roadmap'],
    queryFn: () => api.get('/roadmap/').then((r) => r.data),
  })
}
