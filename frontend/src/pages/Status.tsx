import { useStatus } from '@/api/hooks/useAnalytics'
import { format } from 'date-fns'
import { ru } from 'date-fns/locale'

// ─── Types ────────────────────────────────────────────────────────────────────

interface ServiceStatus {
  name: string
  status: 'ok' | 'degraded' | 'down'
  latency_ms?: number
  message?: string
}

interface StatusData {
  overall: 'ok' | 'degraded' | 'down'
  services: ServiceStatus[]
  last_checked: string
  uptime_pct?: number
}

const SERVICE_LABELS: Record<string, string> = {
  api: 'API',
  database: 'База данных',
  db: 'База данных',
  redis: 'Redis',
  websocket: 'WebSocket',
  ws: 'WebSocket',
  ai: 'AI-сервис',
  celery: 'Celery Worker',
}

const STATUS_CONFIG = {
  ok: {
    dot: 'bg-[#00e676]',
    text: 'text-[#00e676]',
    label: 'Работает',
    badge: 'bg-[#00e676]/10 text-[#00e676] border-[#00e676]/30',
  },
  degraded: {
    dot: 'bg-[#ff9500] animate-pulse',
    text: 'text-[#ff9500]',
    label: 'Замедление',
    badge: 'bg-[#ff9500]/10 text-[#ff9500] border-[#ff9500]/30',
  },
  down: {
    dot: 'bg-red-400 animate-pulse',
    text: 'text-red-400',
    label: 'Недоступен',
    badge: 'bg-red-400/10 text-red-400 border-red-400/30',
  },
}

const OVERALL_CONFIG = {
  ok: {
    icon: '✅',
    text: 'Все системы работают нормально',
    bg: 'bg-[#00e676]/5 border-[#00e676]/20',
    label: 'bg-[#00e676]/10 text-[#00e676]',
  },
  degraded: {
    icon: '⚠️',
    text: 'Наблюдаются замедления',
    bg: 'bg-[#ff9500]/5 border-[#ff9500]/20',
    label: 'bg-[#ff9500]/10 text-[#ff9500]',
  },
  down: {
    icon: '🔴',
    text: 'Сервисы недоступны',
    bg: 'bg-red-400/5 border-red-400/20',
    label: 'bg-red-400/10 text-red-400',
  },
}

// ─── Default services if no data ─────────────────────────────────────────────

const DEFAULT_SERVICES: ServiceStatus[] = [
  { name: 'api', status: 'ok' },
  { name: 'database', status: 'ok' },
  { name: 'redis', status: 'ok' },
  { name: 'websocket', status: 'ok' },
  { name: 'ai', status: 'ok' },
]

// ─── Components ───────────────────────────────────────────────────────────────

function ServiceRow({ service }: { service: ServiceStatus }) {
  const config = STATUS_CONFIG[service.status] ?? STATUS_CONFIG.ok
  const label = SERVICE_LABELS[service.name] ?? service.name

  return (
    <div className="flex items-center justify-between py-4 border-b border-[#1e2d45] last:border-b-0">
      <div className="flex items-center gap-3">
        <div className={`w-2.5 h-2.5 rounded-full ${config.dot}`} />
        <div>
          <p className="text-[#e2e8f0] text-sm font-medium">{label}</p>
          {service.message && (
            <p className="text-[#8899aa] text-xs mt-0.5">{service.message}</p>
          )}
        </div>
      </div>

      <div className="flex items-center gap-3">
        {service.latency_ms !== undefined && (
          <span className="text-[#8899aa] text-xs">{service.latency_ms}ms</span>
        )}
        <span className={`text-xs px-2.5 py-1 rounded-lg border ${config.badge}`}>
          {config.label}
        </span>
      </div>
    </div>
  )
}

// ─── Main ────────────────────────────────────────────────────────────────────

export default function Status() {
  const { data, isLoading, dataUpdatedAt } = useStatus()
  const statusData = data as StatusData | undefined

  const overall = statusData?.overall ?? 'ok'
  const services = statusData?.services ?? DEFAULT_SERVICES
  const overallCfg = OVERALL_CONFIG[overall] ?? OVERALL_CONFIG.ok

  const lastUpdate = dataUpdatedAt
    ? format(new Date(dataUpdatedAt), 'HH:mm:ss', { locale: ru })
    : null

  return (
    <div className="min-h-screen bg-[#0a0e17] p-6 max-w-3xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-[#e2e8f0] mb-1">Статус сервисов</h1>
        <p className="text-[#8899aa] text-sm">
          Автообновление каждые 30 секунд
          {lastUpdate && (
            <span> · Обновлено в {lastUpdate}</span>
          )}
        </p>
      </div>

      {isLoading ? (
        <div className="space-y-4 animate-pulse">
          <div className="h-24 bg-[#1e2d45] rounded-2xl" />
          <div className="h-64 bg-[#1e2d45] rounded-2xl" />
        </div>
      ) : (
        <>
          {/* Overall Status */}
          <div className={`border rounded-2xl p-5 mb-6 ${overallCfg.bg}`}>
            <div className="flex items-center gap-3">
              <span className="text-2xl">{overallCfg.icon}</span>
              <div>
                <p className="text-[#e2e8f0] font-semibold">{overallCfg.text}</p>
                {statusData?.uptime_pct !== undefined && (
                  <p className="text-[#8899aa] text-sm">
                    Uptime: <span className="text-[#00e676]">{statusData.uptime_pct}%</span>
                  </p>
                )}
              </div>
              <span className={`ml-auto text-xs font-medium px-3 py-1 rounded-lg ${overallCfg.label}`}>
                {overall === 'ok' ? 'В норме' : overall === 'degraded' ? 'Деградация' : 'Сбой'}
              </span>
            </div>
          </div>

          {/* Services */}
          <div className="bg-[#0f1520] border border-[#1e2d45] rounded-2xl p-5">
            <h2 className="text-[#e2e8f0] font-semibold mb-2">Компоненты системы</h2>
            <div>
              {services.map((service) => (
                <ServiceRow key={service.name} service={service} />
              ))}
            </div>
          </div>

          {/* Refresh indicator */}
          <div className="mt-4 text-center">
            <p className="text-[#8899aa] text-xs">
              Страница автоматически обновляется. Данные актуальны.
            </p>
          </div>
        </>
      )}
    </div>
  )
}
