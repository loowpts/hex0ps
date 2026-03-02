import { useRef } from 'react'
import { Link } from 'react-router-dom'
import { useRoadmap } from '@/api/hooks/useTasks'
import type { RoadmapNode, RoadmapEdge, RoadmapData } from '@/types'

// ─── RoadmapGraph (D3 SVG) ────────────────────────────────────────────────────

const STATUS_COLORS: Record<string, string> = {
  locked: '#1e2d45',
  available: '#00d4ff',
  in_progress: '#ff9500',
  completed: '#00e676',
}

const STATUS_TEXT: Record<string, string> = {
  locked: '#4a5568',
  available: '#e2e8f0',
  in_progress: '#e2e8f0',
  completed: '#e2e8f0',
}

function RoadmapGraph({ nodes, edges }: { nodes: RoadmapNode[]; edges: RoadmapEdge[] }) {
  const svgRef = useRef<SVGSVGElement>(null)

  // Find bounding box of all nodes
  const xs = nodes.map((n) => n.position.x)
  const ys = nodes.map((n) => n.position.y)
  const minX = Math.min(...xs)
  const minY = Math.min(...ys)
  const maxX = Math.max(...xs)
  const maxY = Math.max(...ys)

  const PAD = 80
  const NODE_W = 140
  const NODE_H = 60
  const viewWidth = maxX - minX + NODE_W + PAD * 2
  const viewHeight = maxY - minY + NODE_H + PAD * 2

  // Build node lookup
  const nodeMap = new Map<string, RoadmapNode>(nodes.map((n) => [n.id, n]))

  return (
    <div className="overflow-auto w-full rounded-2xl bg-[#0f1520] border border-[#1e2d45] p-4">
      <svg
        ref={svgRef}
        viewBox={`${minX - PAD} ${minY - PAD} ${viewWidth} ${viewHeight}`}
        className="w-full"
        style={{ minHeight: Math.max(400, viewHeight) }}
      >
        <defs>
          <marker
            id="arrow"
            viewBox="0 0 10 10"
            refX="10"
            refY="5"
            markerWidth="8"
            markerHeight="8"
            orient="auto"
          >
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#1e2d45" />
          </marker>
        </defs>

        {/* Edges */}
        {edges.map((edge, i) => {
          const fromNode = nodeMap.get(edge.from)
          const toNode = nodeMap.get(edge.to)
          if (!fromNode || !toNode) return null

          const x1 = fromNode.position.x + NODE_W / 2
          const y1 = fromNode.position.y + NODE_H
          const x2 = toNode.position.x + NODE_W / 2
          const y2 = toNode.position.y

          return (
            <line
              key={i}
              x1={x1}
              y1={y1}
              x2={x2}
              y2={y2}
              stroke="#1e2d45"
              strokeWidth={2}
              markerEnd="url(#arrow)"
            />
          )
        })}

        {/* Nodes */}
        {nodes.map((node) => {
          const { x, y } = node.position
          const color = STATUS_COLORS[node.status] ?? '#1e2d45'
          const textColor = STATUS_TEXT[node.status] ?? '#8899aa'
          const pct = node.total > 0 ? (node.completed / node.total) * 100 : 0
          const isLocked = node.status === 'locked'

          return (
            <g key={node.id}>
              {/* Node box */}
              <rect
                x={x}
                y={y}
                width={NODE_W}
                height={NODE_H}
                rx={10}
                fill="#0f1520"
                stroke={color}
                strokeWidth={isLocked ? 1 : 2}
                opacity={isLocked ? 0.5 : 1}
              />

              {/* Progress bar */}
              {!isLocked && node.total > 0 && (
                <>
                  <rect
                    x={x + 8}
                    y={y + NODE_H - 10}
                    width={NODE_W - 16}
                    height={4}
                    rx={2}
                    fill="#1e2d45"
                  />
                  <rect
                    x={x + 8}
                    y={y + NODE_H - 10}
                    width={(NODE_W - 16) * (pct / 100)}
                    height={4}
                    rx={2}
                    fill={color}
                  />
                </>
              )}

              {/* Icon */}
              <text
                x={x + 16}
                y={y + 22}
                fontSize={14}
                opacity={isLocked ? 0.4 : 1}
              >
                {node.icon}
              </text>

              {/* Title */}
              <text
                x={x + 34}
                y={y + 22}
                fontSize={11}
                fill={textColor}
                opacity={isLocked ? 0.5 : 1}
                fontWeight="600"
              >
                {node.title_ru}
              </text>

              {/* Completed/Total */}
              <text
                x={x + 34}
                y={y + 38}
                fontSize={9}
                fill="#8899aa"
                opacity={isLocked ? 0.4 : 1}
              >
                {node.completed}/{node.total}
              </text>

              {isLocked && (
                <text x={x + NODE_W - 20} y={y + 22} fontSize={12}>
                  🔒
                </text>
              )}
            </g>
          )
        })}
      </svg>
    </div>
  )
}

// ─── Legend ──────────────────────────────────────────────────────────────────

function Legend() {
  const items = [
    { color: '#1e2d45', label: 'Заблокировано' },
    { color: '#00d4ff', label: 'Доступно' },
    { color: '#ff9500', label: 'В процессе' },
    { color: '#00e676', label: 'Завершено' },
  ]

  return (
    <div className="flex flex-wrap gap-4 mb-4">
      {items.map((item) => (
        <div key={item.label} className="flex items-center gap-2">
          <div
            className="w-3 h-3 rounded-sm border"
            style={{ borderColor: item.color, backgroundColor: `${item.color}20` }}
          />
          <span className="text-xs text-[#8899aa]">{item.label}</span>
        </div>
      ))}
    </div>
  )
}

// ─── NodeList (mobile fallback) ───────────────────────────────────────────────

function NodeList({ nodes }: { nodes: RoadmapNode[] }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
      {nodes.map((node) => {
        const pct = node.total > 0 ? Math.round((node.completed / node.total) * 100) : 0
        const color = STATUS_COLORS[node.status] ?? '#1e2d45'
        const isLocked = node.status === 'locked'

        return (
          <div
            key={node.id}
            className={`bg-[#0f1520] border rounded-xl p-4 ${isLocked ? 'opacity-50' : ''}`}
            style={{ borderColor: `${color}40` }}
          >
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xl">{node.icon}</span>
              <span className="text-[#e2e8f0] text-sm font-medium">{node.title_ru}</span>
              {isLocked && <span className="ml-auto text-xs">🔒</span>}
            </div>
            <div className="flex justify-between text-xs text-[#8899aa] mb-1">
              <span>{node.completed}/{node.total} задач</span>
              <span style={{ color }}>{pct}%</span>
            </div>
            <div className="h-1.5 bg-[#1e2d45] rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all"
                style={{ width: `${pct}%`, backgroundColor: color }}
              />
            </div>
            {!isLocked && (
              <Link
                to={`/tasks?category=${node.id}`}
                className="mt-3 block text-center py-1.5 rounded-lg text-xs font-medium border transition-colors"
                style={{
                  borderColor: `${color}40`,
                  color,
                }}
              >
                Открыть задачи
              </Link>
            )}
          </div>
        )
      })}
    </div>
  )
}

// ─── Main ────────────────────────────────────────────────────────────────────

export default function Roadmap() {
  const { data, isLoading } = useRoadmap()
  const roadmapData = data as RoadmapData | undefined

  return (
    <div className="min-h-screen bg-[#0a0e17] p-6 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-[#e2e8f0] mb-1">Роудмап</h1>
        <p className="text-[#8899aa] text-sm">Визуальная карта вашего пути обучения DevOps</p>
      </div>

      {isLoading ? (
        <div className="bg-[#0f1520] border border-[#1e2d45] rounded-2xl p-8 animate-pulse flex items-center justify-center" style={{ minHeight: 400 }}>
          <p className="text-[#8899aa]">Загрузка роудмапа...</p>
        </div>
      ) : roadmapData?.nodes && roadmapData.nodes.length > 0 ? (
        <>
          <Legend />

          {/* SVG Graph */}
          <div className="hidden md:block mb-6">
            <RoadmapGraph nodes={roadmapData.nodes} edges={roadmapData.edges} />
          </div>

          {/* Mobile list */}
          <div className="md:hidden">
            <NodeList nodes={roadmapData.nodes} />
          </div>

          {/* Stats */}
          <div className="mt-6 grid grid-cols-2 sm:grid-cols-4 gap-4">
            {roadmapData.nodes.map((node) => {
              const pct = node.total > 0 ? Math.round((node.completed / node.total) * 100) : 0
              if (node.status === 'locked') return null
              return (
                <div key={node.id} className="bg-[#0f1520] border border-[#1e2d45] rounded-xl p-3">
                  <div className="flex items-center gap-1.5 mb-1">
                    <span>{node.icon}</span>
                    <span className="text-[#e2e8f0] text-xs font-medium">{node.title_ru}</span>
                  </div>
                  <p className="text-lg font-bold" style={{ color: STATUS_COLORS[node.status] }}>
                    {pct}%
                  </p>
                </div>
              )
            })}
          </div>
        </>
      ) : (
        <div className="text-center py-16">
          <p className="text-[#8899aa]">Роудмап не настроен</p>
        </div>
      )}
    </div>
  )
}
