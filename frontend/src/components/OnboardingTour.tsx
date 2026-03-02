import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMe, useUpdateSettings } from '@/api/hooks/useAuth'

// ─── Tour Steps ───────────────────────────────────────────────────────────────

interface TourStep {
  title: string
  description: string
  icon: string
  action?: string
  hint?: string
}

const TOUR_STEPS: TourStep[] = [
  {
    title: 'Добро пожаловать на DevOps Platform!',
    description:
      'Здесь вы будете изучать DevOps на практике: настраивать серверы, работать с Docker, Nginx, systemd — в реальных терминальных сессиях.',
    icon: '🚀',
    hint: 'Платформа для практического изучения DevOps',
  },
  {
    title: 'Задачи',
    description:
      'Выполняйте практические задачи в изолированных Docker-контейнерах. Каждая задача — реальная ситуация из работы DevOps-инженера.',
    icon: '⚡',
    action: 'Перейти к задачам',
    hint: 'Нажмите "Начать задачу" чтобы получить терминал',
  },
  {
    title: 'Терминал',
    description:
      'Полноценный терминал прямо в браузере. Работайте в Linux-контейнере, настраивайте сервисы, исправляйте ошибки. Горячая клавиша: Ctrl+T.',
    icon: '🖥️',
    hint: 'Ctrl+Enter — проверить решение, Ctrl+H — получить подсказку',
  },
  {
    title: 'Роудмап',
    description:
      'Визуальная карта обучения: от основ Linux до CI/CD. Задачи открываются последовательно по мере прохождения.',
    icon: '🗺️',
    action: 'Открыть роудмап',
    hint: 'Следите за прогрессом по каждой категории',
  },
  {
    title: 'Аналитика и геймификация',
    description:
      'XP, стрики, уровни (Beginner → Pro), достижения и сертификаты. Выполняйте задачи без подсказок — получайте бонусный XP.',
    icon: '🏆',
    hint: 'Стрик прерывается, если пропустить день',
  },
  {
    title: 'AI-ментор',
    description:
      'Встроенный AI-ассистент помогает с объяснениями, подсказками и анализом ошибок. Доступен в каждой задаче.',
    icon: '🤖',
    hint: 'Нажмите "Спросить AI-ассистента" в задаче',
  },
  {
    title: 'Всё готово!',
    description:
      'Начните с первой задачи в категории Linux. Удачи в изучении DevOps! 💪',
    icon: '🎉',
  },
]

// ─── Main Component ───────────────────────────────────────────────────────────

export default function OnboardingTour() {
  const { data: user } = useMe()
  const updateSettings = useUpdateSettings()
  const navigate = useNavigate()

  const [step, setStep] = useState(0)
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    if (user && !user.onboarding_done) {
      setVisible(true)
    }
  }, [user])

  const handleNext = () => {
    if (step < TOUR_STEPS.length - 1) {
      setStep((s) => s + 1)
    }
  }

  const handlePrev = () => {
    if (step > 0) setStep((s) => s - 1)
  }

  const handleFinish = () => {
    updateSettings.mutate({ onboarding_done: true })
    setVisible(false)
    navigate('/tasks')
  }

  const handleSkip = () => {
    updateSettings.mutate({ onboarding_done: true })
    setVisible(false)
  }

  const handleAction = () => {
    const current = TOUR_STEPS[step]
    if (current.action === 'Перейти к задачам') navigate('/tasks')
    else if (current.action === 'Открыть роудмап') navigate('/roadmap')
    handleNext()
  }

  if (!visible) return null

  const current = TOUR_STEPS[step]
  const isLast = step === TOUR_STEPS.length - 1
  const progress = ((step + 1) / TOUR_STEPS.length) * 100

  return (
    <div className="fixed inset-0 z-[9998] flex items-center justify-center p-4">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" />

      {/* Card */}
      <div className="relative w-full max-w-md bg-[#0f1520] border border-[#1e2d45] rounded-2xl shadow-2xl overflow-hidden">
        {/* Progress bar */}
        <div className="h-1 bg-[#1e2d45]">
          <div
            className="h-full bg-gradient-to-r from-[#00d4ff] to-[#00e676] transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>

        {/* Content */}
        <div className="p-8">
          {/* Icon */}
          <div className="text-5xl mb-5 text-center">{current.icon}</div>

          {/* Title */}
          <h2 className="text-xl font-bold text-[#e2e8f0] mb-3 text-center">
            {current.title}
          </h2>

          {/* Description */}
          <p className="text-[#8899aa] text-sm leading-relaxed text-center mb-4">
            {current.description}
          </p>

          {/* Hint */}
          {current.hint && (
            <div className="bg-[#00d4ff]/5 border border-[#00d4ff]/20 rounded-xl px-4 py-2.5 mb-6">
              <p className="text-[#00d4ff] text-xs text-center">{current.hint}</p>
            </div>
          )}

          {/* Step dots */}
          <div className="flex justify-center gap-1.5 mb-6">
            {TOUR_STEPS.map((_, i) => (
              <div
                key={i}
                className={`h-1.5 rounded-full transition-all duration-300 ${
                  i === step
                    ? 'w-6 bg-[#00d4ff]'
                    : i < step
                    ? 'w-1.5 bg-[#00d4ff]/40'
                    : 'w-1.5 bg-[#1e2d45]'
                }`}
              />
            ))}
          </div>

          {/* Buttons */}
          <div className="flex items-center gap-3">
            {step > 0 && (
              <button
                onClick={handlePrev}
                className="px-4 py-2.5 rounded-xl text-sm font-medium border border-[#1e2d45] text-[#8899aa] hover:text-[#e2e8f0] transition-colors"
              >
                Назад
              </button>
            )}

            {isLast ? (
              <button
                onClick={handleFinish}
                className="flex-1 py-2.5 rounded-xl font-semibold text-sm text-[#0a0e17] bg-[#00e676] hover:bg-[#00cf6e] transition-colors"
              >
                Начать!
              </button>
            ) : current.action ? (
              <button
                onClick={handleAction}
                className="flex-1 py-2.5 rounded-xl font-semibold text-sm text-[#0a0e17] bg-[#00d4ff] hover:bg-[#00bfe8] transition-colors"
              >
                {current.action}
              </button>
            ) : (
              <button
                onClick={handleNext}
                className="flex-1 py-2.5 rounded-xl font-semibold text-sm text-[#0a0e17] bg-[#00d4ff] hover:bg-[#00bfe8] transition-colors"
              >
                Далее →
              </button>
            )}
          </div>

          {/* Skip */}
          <button
            onClick={handleSkip}
            className="w-full mt-3 py-2 text-xs text-[#4a5568] hover:text-[#8899aa] transition-colors"
          >
            Пропустить обучение
          </button>
        </div>

        {/* Step counter */}
        <div className="absolute top-4 right-4 text-[#4a5568] text-xs">
          {step + 1}/{TOUR_STEPS.length}
        </div>
      </div>
    </div>
  )
}
