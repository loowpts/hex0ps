import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '@/api/client'
import type { CourseList, CourseDetail, LessonDetail, QuizSubmitResult, SkillTreeData } from '@/types'

export function useCourses() {
  return useQuery<CourseList[]>({
    queryKey: ['courses'],
    queryFn: () => api.get('/courses/').then((r) => r.data),
    staleTime: 1000 * 60 * 5,
  })
}

export function useCourse(slug: string) {
  return useQuery<CourseDetail>({
    queryKey: ['course', slug],
    queryFn: () => api.get(`/courses/${slug}/`).then((r) => r.data),
    enabled: !!slug,
  })
}

export function useSkillTree() {
  return useQuery<SkillTreeData>({
    queryKey: ['skill-tree'],
    queryFn: () => api.get('/courses/skill-tree/').then((r) => r.data),
    staleTime: 1000 * 60 * 10,
  })
}

export function useLesson(lessonId: number | null) {
  return useQuery<LessonDetail>({
    queryKey: ['lesson', lessonId],
    queryFn: () => api.get(`/courses/lessons/${lessonId}/`).then((r) => r.data),
    enabled: !!lessonId,
  })
}

export function useEnrollCourse() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (slug: string) =>
      api.post(`/courses/${slug}/enroll/`).then((r) => r.data),
    onSuccess: (_, slug) => {
      qc.invalidateQueries({ queryKey: ['course', slug] })
      qc.invalidateQueries({ queryKey: ['courses'] })
    },
  })
}

export function useLessonComplete() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (lessonId: number) =>
      api.post(`/courses/lessons/${lessonId}/complete/`).then((r) => r.data),
    onSuccess: (_data, lessonId) => {
      qc.invalidateQueries({ queryKey: ['courses'] })
      qc.invalidateQueries({ queryKey: ['course'] })
      qc.invalidateQueries({ queryKey: ['lesson', lessonId] })
      qc.invalidateQueries({ queryKey: ['me'] })
    },
  })
}

export function useQuizSubmit() {
  const qc = useQueryClient()
  return useMutation<QuizSubmitResult, Error, { quizId: number; answers: Record<string, number[]> }>({
    mutationFn: ({ quizId, answers }) =>
      api.post(`/courses/quiz/${quizId}/submit/`, { answers }).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['courses'] })
      qc.invalidateQueries({ queryKey: ['course'] })
      qc.invalidateQueries({ queryKey: ['me'] })
    },
  })
}

export function useExplainLesson() {
  return useMutation<{ explanation: string }, Error, { lessonTitle: string; selectedText: string }>({
    mutationFn: ({ lessonTitle, selectedText }) =>
      api.post('/ai/explain-lesson/', { lesson_title: lessonTitle, selected_text: selectedText }).then((r) => r.data),
  })
}
