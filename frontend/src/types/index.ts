// Типы для DevOps Learning Platform

export interface User {
  id: number
  email?: string
  username: string
  level: 'beginner' | 'junior' | 'middle' | 'senior' | 'pro'
  level_display: string
  xp: number
  xp_to_next_level: number
  level_progress_pct: number
  streak: number
  max_streak: number
  is_public: boolean
  onboarding_done: boolean
  avatar_url: string
  bio: string
  last_active: string | null
  created_at: string
}

export interface Task {
  id: number
  title_ru: string
  description_ru?: string
  category: TaskCategory
  category_display: string
  difficulty: TaskDifficulty
  difficulty_display: string
  task_type: 'regular' | 'break_and_fix'
  xp_reward: number
  time_limit: number
  docker_image?: string
  checker_type?: string
  order: number
  prerequisites_info?: { id: number; title_ru: string }[]
  user_status?: TaskStatus | null
  user_task?: UserTask | null
  is_locked?: boolean
}

export type TaskCategory = 'linux' | 'nginx' | 'systemd' | 'docker' | 'networks' | 'git' | 'cicd' | 'onboarding'
export type TaskDifficulty = 'beginner' | 'intermediate' | 'advanced'
export type TaskStatus = 'not_started' | 'in_progress' | 'completed' | 'failed'

export interface UserTask {
  id: number
  status: TaskStatus
  attempts: number
  hints_used: number
  xp_earned: number
  xp_multiplier: number
  started_at: string | null
  completed_at: string | null
  time_spent: number
}

export interface TerminalSession {
  session_id: string
  task_id: number
  expires_at: string
  time_remaining_seconds: number
}

export interface CheckResult {
  success: boolean
  message: string
  xp_earned?: number
  xp_multiplier?: number
  new_achievements?: Achievement[]
  new_certificate?: Certificate | null
  user_level?: string
  user_xp?: number
}

export interface HintResult {
  hint_text: string
  xp_multiplier: number
  hints_remaining: number
  message: string
}

export interface Achievement {
  icon: string
  title_ru: string
  description_ru?: string
  earned_at?: string
}

export interface Certificate {
  cert_id: string
  category: string
  category_display: string
  issued_at: string
  pdf_url: string | null
}

export interface Note {
  id?: number
  task_id: number
  content: string
  updated_at?: string
}

export interface Notification {
  id: number
  type: 'streak_at_risk' | 'achievement_earned' | 'level_up' | 'cert_issued'
  message: string
  read: boolean
  created_at: string
}

export interface AnalyticsData {
  heatmap: Record<string, { tasks: number; xp: number; time_minutes: number }>
  skills: Record<string, { completed: number; total: number; pct: number }>
  total_completed: number
  weekly: {
    current: { tasks: number; xp: number; time_minutes: number }
    previous: { tasks: number; xp: number; time_minutes: number }
    change_pct: number
  }
  streak: { current: number; max: number; at_risk: boolean }
  forecast: { days_to_next_level: number; tasks_per_day_needed: number; xp_to_next_level: number }
  ai_insight: string
  recommended_tasks: RecommendedTask[]
  user: { level: string; xp: number; level_progress_pct: number }
}

export interface RecommendedTask {
  id: number
  title_ru: string
  category: string
  difficulty: string
  xp_reward: number
  reason: string
}

// ─── Courses ──────────────────────────────────────────────────────────────────

export interface UserCourseProgress {
  status: 'not_started' | 'in_progress' | 'completed'
  started_at: string | null
  completed_at: string | null
  xp_earned: number
}

export interface UserLessonProgress {
  viewed: boolean
  quiz_passed: boolean
  lab_done: boolean
  completed: boolean
  completed_at: string | null
}

export interface QuizAnswer {
  id: number
  text_ru: string
  is_correct?: boolean  // только в результатах
}

export interface QuizQuestion {
  id: number
  text_ru: string
  question_type: 'single' | 'multi'
  answers: QuizAnswer[]
}

export interface Quiz {
  id: number
  pass_threshold: number
  questions: QuizQuestion[]
}

export interface LessonDetail {
  id: number
  title_ru: string
  lesson_type: 'theory' | 'quiz' | 'lab' | 'exam'
  lesson_type_display: string
  order: number
  xp_reward: number
  content_md: string
  quiz: Quiz | null
  task_id: number | null
  user_progress: UserLessonProgress | null
}

export interface LessonListItem {
  id: number
  title_ru: string
  lesson_type: 'theory' | 'quiz' | 'lab' | 'exam'
  lesson_type_display: string
  order: number
  xp_reward: number
  user_progress: UserLessonProgress | null
}

export interface Module {
  id: number
  title_ru: string
  order: number
  lessons: LessonListItem[]
  completed_lessons: number
}

export interface CourseList {
  id: number
  slug: string
  title_ru: string
  description_ru: string
  icon: string
  difficulty: 'beginner' | 'intermediate' | 'advanced'
  difficulty_display: string
  category: string
  estimated_hours: number
  xp_reward: number
  order: number
  total_lessons: number
  completed_lessons: number
  user_progress: UserCourseProgress | null
}

export interface CourseDetail extends CourseList {
  modules: Module[]
  prerequisites_info: { id: number; slug: string; title_ru: string; completed: boolean }[]
}

export interface QuizAnswerResult {
  id: number
  text_ru: string
  is_correct: boolean
}

export interface QuizQuestionResult {
  question_id: number
  question_text: string
  is_correct: boolean
  explanation_ru: string
  answers: QuizAnswerResult[]
  selected_ids: number[]
}

export interface QuizSubmitResult {
  attempt_id: number
  score: number
  passed: boolean
  correct_count: number
  total: number
  xp_earned: number
  pass_threshold: number
  results: QuizQuestionResult[]
}

export interface SkillTreeNode {
  id: string
  course_id: number
  title_ru: string
  icon: string
  difficulty: string
  estimated_hours: number
  xp_reward: number
  category: string
  status: 'locked' | 'available' | 'in_progress' | 'completed'
}

export interface SkillTreeEdge {
  source: string
  target: string
}

export interface SkillTreeData {
  nodes: SkillTreeNode[]
  edges: SkillTreeEdge[]
}

export interface RoadmapNode {
  id: string
  title_ru: string
  icon: string
  completed: number
  total: number
  status: 'locked' | 'available' | 'in_progress' | 'completed'
  position: { x: number; y: number }
}

export interface RoadmapEdge {
  from: string
  to: string
}

export interface RoadmapData {
  nodes: RoadmapNode[]
  edges: RoadmapEdge[]
}

export interface InterviewQuestion {
  id: number
  question_ru: string
  category: string
  difficulty: string
  tags: string[]
}

export interface InterviewAttemptResult {
  attempt_id: number
  score: number
  feedback: string
  strengths: string[]
  improvements: string[]
}

export interface ReplaySolution {
  task_id: number
  title_ru: string
  solution_steps: { command: string; explanation: string }[]
  completed_at: string
}

export interface Recording {
  share_id: string
  events: {
    version: number
    width: number
    height: number
    timestamp: number
    events: [number, string, string][]
  }
  cols: number
  rows: number
  duration_seconds: number
  is_public: boolean
  created_at: string
  author: string
  task: { id: number; title_ru: string; category: string }
}

export type TerminalTheme = 'dracula' | 'solarized-dark' | 'one-dark'

// ─── Cheat Sheets ─────────────────────────────────────────────────────────────

export interface CheatSheetEntry {
  id: number
  command: string
  description_ru: string
  example: string
  order: number
  learned: boolean
}

export interface CheatSheetList {
  id: number
  title_ru: string
  category: TaskCategory
  category_display: string
  tags: string[]
  order: number
  is_bookmarked: boolean
  entries_count: number
}

export interface CheatSheetDetail extends CheatSheetList {
  content_md: string
  entries: CheatSheetEntry[]
  learned_count: number
}

// ─── Daily Challenge ──────────────────────────────────────────────────────────

export interface DailyChallengeTask {
  id: number
  title_ru: string
  description_ru: string
  category: TaskCategory
  category_display: string
  difficulty: TaskDifficulty
  difficulty_display: string
  xp_reward: number
}

export interface DailyChallengeCompletion {
  completed: boolean
  time_spent: number
  xp_earned: number
  completed_at: string
}

export interface DailyLeaderboardEntry {
  rank: number
  username: string
  time_spent: number
  xp_earned: number
}

export interface DailyChallengeData {
  id: number
  date: string
  participants_count: number
  completions_count: number
  task: DailyChallengeTask
  my_completion: DailyChallengeCompletion | null
  leaderboard: DailyLeaderboardEntry[]
}
