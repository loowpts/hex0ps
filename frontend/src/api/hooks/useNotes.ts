import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '@/api/client'
import type { Note } from '@/types'

export function useNotes(search?: string) {
  return useQuery<Note[]>({
    queryKey: ['notes', search],
    queryFn: () => api.get('/notes/', { params: search ? { search } : {} }).then((r) => r.data),
  })
}

export function useNote(taskId: number) {
  return useQuery<Note>({
    queryKey: ['note', taskId],
    queryFn: () => api.get(`/notes/${taskId}/`).then((r) => r.data),
    enabled: !!taskId,
  })
}

export function useSaveNote() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ taskId, content }: { taskId: number; content: string }) =>
      api.put(`/notes/${taskId}/upsert/`, { content }).then((r) => r.data),
    onSuccess: (_data, { taskId }) => {
      qc.invalidateQueries({ queryKey: ['note', taskId] })
      qc.invalidateQueries({ queryKey: ['notes'] })
    },
  })
}
