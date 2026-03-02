import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { useTheme } from '@/hooks/useTheme'
import { useAuthStore, hasStoredToken } from '@/store/auth'
import Sidebar from '@/components/Sidebar'

// Страницы
import Dashboard from '@/pages/Dashboard'
import Login from '@/pages/Login'
import Tasks from '@/pages/Tasks'
import TaskDetail from '@/pages/TaskDetail'
import Roadmap from '@/pages/Roadmap'
import Analytics from '@/pages/Analytics'
import Profile from '@/pages/Profile'
import PublicProfile from '@/pages/PublicProfile'
import Notes from '@/pages/Notes'
import Interview from '@/pages/Interview'
import Status from '@/pages/Status'
import Changelog from '@/pages/Changelog'
import ReplayRecording from '@/pages/ReplayRecording'
import CollabPage from '@/pages/CollabPage'
import CourseCatalog from '@/pages/CourseCatalog'
import CourseDetail from '@/pages/CourseDetail'
import CourseLearner from '@/pages/CourseLearner'
import DailyChallenge from '@/pages/DailyChallenge'
import PlaygroundPage from '@/pages/PlaygroundPage'
import CheatSheets from '@/pages/CheatSheets'

// Компоненты
import CommandPalette from '@/components/CommandPalette'
import OnboardingTour from '@/components/OnboardingTour'

// ─── Framer Motion page variant ───────────────────────────────────────────────

const pageVariants = {
  initial: { opacity: 0, y: 8 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.22, ease: 'easeOut' } },
  exit: { opacity: 0, y: -8, transition: { duration: 0.16, ease: 'easeIn' } },
}

function PageWrapper({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      variants={pageVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      style={{ minHeight: '100%' }}
    >
      {children}
    </motion.div>
  )
}

// ─── Private route ────────────────────────────────────────────────────────────

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const storeToken = useAuthStore((s) => s.accessToken)
  const isAuthenticated = storeToken !== null ? !!storeToken : hasStoredToken()
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return (
    <div className="flex min-h-screen bg-[#0a0e17]">
      <Sidebar />
      <main className="flex-1 overflow-auto">{children}</main>
    </div>
  )
}

// ─── Offline banner ───────────────────────────────────────────────────────────

function OfflineBanner() {
  const [offline, setOffline] = useState(!navigator.onLine)

  useEffect(() => {
    const handleOnline = () => setOffline(false)
    const handleOffline = () => setOffline(true)
    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)
    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  if (!offline) return null

  return (
    <div className="fixed bottom-4 left-1/2 -translate-x-1/2 z-50">
      <div className="flex items-center gap-2 bg-[#0f1520] border border-[#ff9500]/50 rounded-xl px-4 py-2.5 shadow-2xl">
        <div className="w-2 h-2 rounded-full bg-[#ff9500] animate-pulse" />
        <span className="text-sm text-[#e2e8f0]">
          Оффлайн режим — данные могут быть устаревшими
        </span>
      </div>
    </div>
  )
}

// ─── Animated routes ──────────────────────────────────────────────────────────

function AnimatedRoutes() {
  const location = useLocation()

  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        {/* Публичные */}
        <Route path="/login" element={<PageWrapper><Login /></PageWrapper>} />
        <Route path="/u/:username" element={<PageWrapper><PublicProfile /></PageWrapper>} />
        <Route path="/status" element={<PageWrapper><Status /></PageWrapper>} />
        <Route path="/changelog" element={<PageWrapper><Changelog /></PageWrapper>} />
        <Route path="/replay/:shareId" element={<PageWrapper><ReplayRecording /></PageWrapper>} />
        <Route path="/collab/:inviteToken" element={<PageWrapper><CollabPage /></PageWrapper>} />

        {/* Приватные */}
        <Route path="/" element={<PrivateRoute><Navigate to="/dashboard" replace /></PrivateRoute>} />
        <Route path="/dashboard" element={<PrivateRoute><PageWrapper><Dashboard /></PageWrapper></PrivateRoute>} />
        <Route path="/tasks" element={<PrivateRoute><PageWrapper><Tasks /></PageWrapper></PrivateRoute>} />
        <Route path="/tasks/:taskId" element={<PrivateRoute><PageWrapper><TaskDetail /></PageWrapper></PrivateRoute>} />
        <Route path="/roadmap" element={<PrivateRoute><PageWrapper><Roadmap /></PageWrapper></PrivateRoute>} />
        <Route path="/analytics" element={<PrivateRoute><PageWrapper><Analytics /></PageWrapper></PrivateRoute>} />
        <Route path="/profile" element={<PrivateRoute><PageWrapper><Profile /></PageWrapper></PrivateRoute>} />
        <Route path="/notes" element={<PrivateRoute><PageWrapper><Notes /></PageWrapper></PrivateRoute>} />
        <Route path="/interview" element={<PrivateRoute><PageWrapper><Interview /></PageWrapper></PrivateRoute>} />
        <Route path="/courses" element={<PrivateRoute><PageWrapper><CourseCatalog /></PageWrapper></PrivateRoute>} />
        <Route path="/courses/:slug" element={<PrivateRoute><PageWrapper><CourseDetail /></PageWrapper></PrivateRoute>} />
        <Route path="/courses/:slug/learn" element={<PrivateRoute><PageWrapper><CourseLearner /></PageWrapper></PrivateRoute>} />
        <Route path="/daily" element={<PrivateRoute><PageWrapper><DailyChallenge /></PageWrapper></PrivateRoute>} />
        <Route path="/playground" element={<PrivateRoute><PageWrapper><PlaygroundPage /></PageWrapper></PrivateRoute>} />
        <Route path="/cheatsheets" element={<PrivateRoute><PageWrapper><CheatSheets /></PageWrapper></PrivateRoute>} />

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </AnimatePresence>
  )
}

// ─── Service Worker registration ──────────────────────────────────────────────

function useServiceWorker() {
  useEffect(() => {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker
        .register('/sw.js')
        .catch(() => {
          // SW регистрация не критична
        })
    }
  }, [])
}

// ─── App ─────────────────────────────────────────────────────────────────────

export default function App() {
  useTheme()
  useServiceWorker()

  return (
    <BrowserRouter>
      <CommandPalette />
      <OnboardingTour />
      <OfflineBanner />
      <AnimatedRoutes />
    </BrowserRouter>
  )
}
