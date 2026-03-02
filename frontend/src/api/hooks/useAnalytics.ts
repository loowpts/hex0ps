import { useQuery, useMutation } from '@tanstack/react-query'
import { api } from '@/api/client'
import type { AnalyticsData } from '@/types'

export function useAnalytics() {
  return useQuery<AnalyticsData>({
    queryKey: ['analytics'],
    queryFn: () => api.get('/analytics/me/').then((r) => r.data),
    staleTime: 1000 * 60 * 10, // 10 минут
  })
}

export function useStatus() {
  return useQuery({
    queryKey: ['status'],
    queryFn: () => api.get('/status/').then((r) => r.data),
    refetchInterval: 30_000, // Каждые 30 секунд
  })
}

export function useChangelog() {
  return useQuery({
    queryKey: ['changelog'],
    queryFn: () => api.get('/changelog/').then((r) => r.data),
  })
}

export function useExportPdf() {
  return useMutation({
    mutationFn: async () => {
      const response = await api.get('/analytics/export/pdf/', { responseType: 'blob' })
      const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }))
      const a = document.createElement('a')
      a.href = url
      a.download = 'progress_report.pdf'
      a.click()
      window.URL.revokeObjectURL(url)
    },
  })
}
