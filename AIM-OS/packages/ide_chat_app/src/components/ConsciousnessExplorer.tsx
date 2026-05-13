import React, { useEffect, useMemo, useState } from 'react'
import {
  Brain,
  Search,
  Activity,
  Target,
  Zap,
  Clock,
  FileText,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Info,
  Sparkles,
  RefreshCw,
} from 'lucide-react'

import {
  type ConsciousnessSnapshot,
  type BlueprintNodeSummary,
  type SpecSummary,
  type TimelineEventSummary,
} from '../../../lucid_orchestrator/lucid_orchestrator'
import type { FocusEvent, UpdateEvent } from '../../../lucid_orchestrator/event_bus/event_bus'
import { getGlobalLucidIntegration } from '../lib/lucid-integration'

type NodeStatus = BlueprintNodeSummary['status']
type SpecStatus = SpecSummary['status']
type TimelineSeverity = TimelineEventSummary['severity']

const nodeStatusStyles: Record<NodeStatus, { badge: string; icon: React.ReactNode }> = {
  clean: {
    badge: 'bg-green-900/40 text-green-300 border border-green-700/40',
    icon: <CheckCircle className="w-4 h-4 text-green-300" />,
  },
  drift: {
    badge: 'bg-yellow-900/40 text-yellow-300 border border-yellow-700/40',
    icon: <AlertTriangle className="w-4 h-4 text-yellow-300" />,
  },
  violation: {
    badge: 'bg-red-900/40 text-red-300 border border-red-700/40',
    icon: <XCircle className="w-4 h-4 text-red-300" />,
  },
  proposed: {
    badge: 'bg-blue-900/40 text-blue-300 border border-blue-700/40',
    icon: <Sparkles className="w-4 h-4 text-blue-300" />,
  },
  orphan: {
    badge: 'bg-gray-900/40 text-gray-300 border border-gray-700/40',
    icon: <Info className="w-4 h-4 text-gray-300" />,
  },
}

const specStatusStyles: Record<SpecStatus, string> = {
  clean: 'bg-green-900/40 text-green-300 border border-green-700/40',
  drift: 'bg-yellow-900/40 text-yellow-300 border border-yellow-700/40',
  violation: 'bg-red-900/40 text-red-300 border border-red-700/40',
  proposed: 'bg-blue-900/40 text-blue-300 border border-blue-700/40',
  orphan: 'bg-gray-900/40 text-gray-300 border border-gray-700/40',
}

const timelineSeverityStyles: Record<
  TimelineSeverity,
  { badge: string; icon: React.ReactNode }
> = {
  info: {
    badge: 'bg-blue-900/40 text-blue-300 border border-blue-700/40',
    icon: <Info className="w-4 h-4 text-blue-300" />,
  },
  warning: {
    badge: 'bg-yellow-900/40 text-yellow-300 border border-yellow-700/40',
    icon: <AlertTriangle className="w-4 h-4 text-yellow-300" />,
  },
  error: {
    badge: 'bg-red-900/40 text-red-300 border border-red-700/40',
    icon: <XCircle className="w-4 h-4 text-red-300" />,
  },
}

const formatStatusLabel = (status: string) =>
  status.charAt(0).toUpperCase() + status.slice(1)

const formatTimestamp = (timestamp?: string | number) => {
  if (!timestamp) return '—'
  const date = typeof timestamp === 'number' ? new Date(timestamp) : new Date(timestamp)
  return date.toLocaleString()
}

const formatUptime = (ms?: number) => {
  if (!ms || ms <= 0) return '—'
  const seconds = Math.floor(ms / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  if (days > 0) return `${days}d ${hours % 24}h`
  if (hours > 0) return `${hours}h ${minutes % 60}m`
  if (minutes > 0) return `${minutes}m ${seconds % 60}s`
  return `${seconds}s`
}

const getHealthBadgeStyle = (health: number) => {
  if (health >= 85) return 'bg-green-900/40 text-green-300 border border-green-700/40'
  if (health >= 70) return 'bg-yellow-900/40 text-yellow-300 border border-yellow-700/40'
  return 'bg-red-900/40 text-red-300 border border-red-700/40'
}

export const ConsciousnessExplorer: React.FC = () => {
  const integration = useMemo(() => getGlobalLucidIntegration(), [])

  const [snapshot, setSnapshot] = useState<ConsciousnessSnapshot | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null)
  const [selectedSpecId, setSelectedSpecId] = useState<string | null>(null)

  const pullSnapshot = (force: boolean = false) => {
    const latest = force
      ? integration.getConsciousnessSnapshot(100)
      : integration.getLatestSnapshot() ?? integration.getConsciousnessSnapshot(100)

    if (latest) {
      setSnapshot(latest)
      setLoading(false)
    }
  }

  useEffect(() => {
    let mounted = true
    let focusHandler: ((event: FocusEvent) => void) | undefined
    let updateHandler: ((event: UpdateEvent) => void) | undefined
    let interval: ReturnType<typeof setInterval> | undefined

    const initialise = async () => {
      try {
        await integration.initialize()
        if (!mounted) return
        pullSnapshot(true)
      } catch (err) {
        console.error('Failed to initialize Lucid Integration Service', err)
        if (mounted) {
          setError(err instanceof Error ? err.message : String(err))
          setLoading(false)
        }
      }
    }

    initialise()

    const eventBus = integration.getEventBus()
    focusHandler = () => pullSnapshot()
    updateHandler = () => pullSnapshot()
    eventBus.onFocus(focusHandler)
    eventBus.onUpdate(updateHandler)

    interval = setInterval(() => pullSnapshot(), 8000)

    return () => {
      mounted = false
      if (focusHandler) eventBus.offFocus(focusHandler)
      if (updateHandler) eventBus.offUpdate(updateHandler)
      if (interval) clearInterval(interval)
    }
  }, [integration])

  useEffect(() => {
    if (!snapshot) return

    if (!selectedNodeId && snapshot.nodes.length > 0) {
      setSelectedNodeId(snapshot.nodes[0].id)
    } else if (
      selectedNodeId &&
      !snapshot.nodes.some((node) => node.id === selectedNodeId)
    ) {
      setSelectedNodeId(snapshot.nodes[0]?.id ?? null)
    }

    if (!selectedSpecId && snapshot.specs.length > 0) {
      setSelectedSpecId(snapshot.specs[0].id)
    } else if (
      selectedSpecId &&
      !snapshot.specs.some((spec) => spec.id === selectedSpecId)
    ) {
      setSelectedSpecId(snapshot.specs[0]?.id ?? null)
    }
  }, [snapshot, selectedNodeId, selectedSpecId])

  const nodes = snapshot?.nodes ?? []
  const specs = snapshot?.specs ?? []
  const timelineEvents = snapshot?.timeline.recentEvents ?? []
  const focusHistory = snapshot?.focusHistory ?? []
  const updateHistory = snapshot?.updateHistory ?? []

  const filteredNodes = nodes.filter((node) => {
    if (!searchTerm) return true
    const term = searchTerm.toLowerCase()
    return (
      node.name.toLowerCase().includes(term) ||
      node.filePath.toLowerCase().includes(term) ||
      node.tags.some((tag) => tag.toLowerCase().includes(term))
    )
  })

  const filteredSpecs = specs.filter((spec) => {
    if (!searchTerm) return true
    const term = searchTerm.toLowerCase()
    return (
      spec.symbol.toLowerCase().includes(term) ||
      spec.responsibility.toLowerCase().includes(term) ||
      spec.mustNever.some((rule) => rule.toLowerCase().includes(term))
    )
  })

  const selectedNode =
    selectedNodeId != null
      ? nodes.find((node) => node.id === selectedNodeId) ?? null
      : null
  const selectedSpec =
    selectedSpecId != null
      ? specs.find((spec) => spec.id === selectedSpecId) ?? null
      : null

  const selectedNodeSpecs =
    selectedNode != null
      ? specs.filter((spec) => selectedNode.linkedSpecIds.includes(spec.id))
      : []

  const selectedNodeEvents =
    selectedNode != null
      ? timelineEvents.filter((event) => event.nodeId === selectedNode.id)
      : []

  return (
    <div className="h-full overflow-y-auto bg-gray-950 text-gray-200">
      <div className="max-w-6xl mx-auto py-6 px-6 lg:px-8 space-y-8">
        <header className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <div className="flex items-center gap-3">
              <Brain className="w-8 h-8 text-purple-400" />
              <h1 className="text-3xl font-bold">Consciousness Explorer</h1>
            </div>
            <p className="text-gray-400 mt-2 max-w-2xl">
              Real-time view into the Lucid Orchestrator&apos;s blueprint nodes,
              specs, timeline events, and focus signals. Use this panel to
              understand the system&apos;s current mental state.
            </p>
          </div>
          <button
            className="inline-flex items-center gap-2 px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm hover:bg-gray-750 transition-colors"
            onClick={() => pullSnapshot(true)}
          >
            <RefreshCw className="w-4 h-4" />
            Refresh snapshot
          </button>
        </header>

        {error && (
          <div className="bg-red-950/40 border border-red-800/60 text-red-200 px-4 py-3 rounded-lg">
            Failed to load Lucid Orchestrator data: {error}
          </div>
        )}

        <section className="bg-gray-900/70 border border-gray-800 rounded-xl p-6 shadow-lg shadow-purple-900/10">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <OverviewCard
              title="Overall Health"
              icon={<Activity className="w-4 h-4" />}
              value={`${Math.round(snapshot?.health.overall ?? 0)}%`}
              subLabel="System aggregate"
              badgeClass={getHealthBadgeStyle(snapshot?.health.overall ?? 0)}
            />
            <OverviewCard
              title="Blueprint Nodes"
              icon={<Target className="w-4 h-4" />}
              value={nodes.length.toString()}
              subLabel={`Specs: ${specs.length}`}
              badgeClass="bg-blue-900/40 border border-blue-700/40 text-blue-300"
            />
            <OverviewCard
              title="Timeline Events"
              icon={<Clock className="w-4 h-4" />}
              value={timelineEvents.length.toString()}
              subLabel={`Focus signals: ${focusHistory.length}`}
              badgeClass="bg-indigo-900/40 border border-indigo-700/40 text-indigo-300"
            />
            <OverviewCard
              title="Uptime"
              icon={<Zap className="w-4 h-4" />}
              value={formatUptime(snapshot?.stats.uptime)}
              subLabel={`Last activity: ${formatTimestamp(snapshot?.lastActivity)}`}
              badgeClass="bg-emerald-900/40 border border-emerald-700/40 text-emerald-300"
            />
          </div>
        </section>

        <section className="bg-gray-900/70 border border-gray-800 rounded-xl p-6 shadow-lg shadow-purple-900/10 space-y-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h2 className="text-xl font-semibold flex items-center gap-2">
                <Target className="w-5 h-5 text-purple-300" />
                Blueprint Nodes
              </h2>
              <p className="text-sm text-gray-400">
                Explore the living graph. Select a node to inspect specs,
                metrics, and recent timeline events.
              </p>
            </div>
            <div className="relative md:w-80">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              <input
                value={searchTerm}
                onChange={(event) => setSearchTerm(event.target.value)}
                placeholder="Search nodes or specs"
                className="w-full bg-gray-950 border border-gray-800 rounded-lg py-2 pl-9 pr-3 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500/60 focus:border-purple-500/60 transition-all"
              />
            </div>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-16 text-gray-400 gap-3">
              <Sparkles className="w-5 h-5 animate-spin" />
              Loading consciousness snapshot...
            </div>
          ) : filteredNodes.length === 0 ? (
            <div className="flex items-center justify-center py-16 text-gray-500 border border-dashed border-gray-800 rounded-lg">
              No nodes matched your search.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredNodes.map((node) => {
                const statusStyle = nodeStatusStyles[node.status]
                const isSelected = node.id === selectedNodeId

                return (
                  <button
                    key={node.id}
                    type="button"
                    onClick={() => setSelectedNodeId(node.id)}
                    className={`text-left bg-gray-950/40 border border-gray-800 rounded-lg p-4 transition-all hover:border-purple-500/60 hover:shadow-lg hover:shadow-purple-900/10 focus:outline-none focus:ring-2 focus:ring-purple-500/50 ${
                      isSelected ? 'border-purple-500/70 shadow-lg shadow-purple-900/15' : ''
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="text-lg font-semibold text-gray-100">
                            {node.name}
                          </h3>
                          <span className="text-xs text-gray-500">
                            ({node.kind})
                          </span>
                        </div>
                        <p className="text-xs text-gray-500 mt-1">
                          {node.filePath}
                        </p>
                      </div>
                      <span
                        className={`inline-flex items-center gap-1 px-2 py-1 text-xs font-medium rounded-full ${statusStyle.badge}`}
                      >
                        {statusStyle.icon}
                        {formatStatusLabel(node.status)}
                      </span>
                    </div>

                    <div className="mt-3 flex flex-wrap gap-2 text-xs text-gray-400">
                      <span className="px-2 py-1 bg-gray-900 rounded">
                        Inputs: {node.inputs}
                      </span>
                      <span className="px-2 py-1 bg-gray-900 rounded">
                        Outputs: {node.outputs}
                      </span>
                      <span className="px-2 py-1 bg-gray-900 rounded">
                        Complexity: {node.metrics.complexity ?? '—'}
                      </span>
                      <span className="px-2 py-1 bg-gray-900 rounded capitalize">
                        Specs: {node.linkedSpecIds.length}
                      </span>
                    </div>

                    {node.tags.length > 0 && (
                      <div className="mt-3 flex flex-wrap gap-1">
                        {node.tags.map((tag) => (
                          <span
                            key={tag}
                            className="px-2 py-0.5 bg-purple-900/40 text-purple-200 text-[11px] rounded"
                          >
                            #{tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </button>
                )
              })}
            </div>
          )}

          {selectedNode && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-gray-950/40 border border-gray-800 rounded-lg p-5">
                <div className="flex items-center gap-2 mb-4">
                  <Activity className="w-4 h-4 text-teal-300" />
                  <h3 className="text-lg font-semibold text-gray-100">
                    Node Metrics
                  </h3>
                </div>
                <dl className="grid grid-cols-2 gap-4 text-sm">
                  <MetricItem
                    label="Status"
                    value={formatStatusLabel(selectedNode.status)}
                  />
                  <MetricItem
                    label="Estimated Complexity"
                    value={selectedNode.metrics.estimatedComplexity ?? '—'}
                  />
                  <MetricItem
                    label="Side effects"
                    value={selectedNode.metrics.hasSideEffects ? 'Yes' : 'No'}
                  />
                  <MetricItem
                    label="Async"
                    value={selectedNode.metrics.isAsync ? 'Yes' : 'No'}
                  />
                  <MetricItem
                    label="Security Level"
                    value={selectedNode.security?.level ?? '—'}
                  />
                  <MetricItem
                    label="Tags"
                    value={
                      selectedNode.tags.length > 0
                        ? selectedNode.tags.join(', ')
                        : '—'
                    }
                  />
                </dl>

                {selectedNode.sideEffects.length > 0 && (
                  <div className="mt-4 text-sm">
                    <h4 className="text-gray-300 font-medium mb-1">
                      Side effects
                    </h4>
                    <ul className="space-y-1 text-gray-400">
                      {selectedNode.sideEffects.map((effect) => (
                        <li key={effect} className="flex items-center gap-2">
                          <Sparkles className="w-3 h-3 text-purple-300" />
                          {effect}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              <div className="bg-gray-950/40 border border-gray-800 rounded-lg p-5">
                <div className="flex items-center gap-2 mb-4">
                  <FileText className="w-4 h-4 text-blue-300" />
                  <h3 className="text-lg font-semibold text-gray-100">
                    Timeline (latest {selectedNodeEvents.length})
                  </h3>
                </div>
                {selectedNodeEvents.length === 0 ? (
                  <p className="text-sm text-gray-500">
                    No recent timeline activity for this node.
                  </p>
                ) : (
                  <ul className="space-y-3 max-h-60 overflow-y-auto pr-2">
                    {selectedNodeEvents.map((event) => {
                      const severityStyle = timelineSeverityStyles[event.severity]
                      return (
                        <li
                          key={event.id}
                          className="bg-gray-900/60 border border-gray-800 rounded-lg p-3 text-sm"
                        >
                          <div className="flex items-center justify-between gap-3">
                            <span className="font-medium text-gray-200 capitalize">
                              {event.type.replace(/_/g, ' ')}
                            </span>
                            <span
                              className={`inline-flex items-center gap-1 px-2 py-1 text-[11px] font-medium rounded ${severityStyle.badge}`}
                            >
                              {severityStyle.icon}
                              {event.severity}
                            </span>
                          </div>
                          <div className="mt-1 text-xs text-gray-500 flex items-center justify-between gap-2">
                            <span>{formatTimestamp(event.timestamp)}</span>
                            {event.durationMs != null && (
                              <span>Duration: {event.durationMs}ms</span>
                            )}
                          </div>
                          {event.metadata && (
                            <pre className="mt-2 bg-gray-950/60 text-[11px] text-gray-400 rounded p-2 max-h-24 overflow-y-auto">
                              {JSON.stringify(event.metadata, null, 2)}
                            </pre>
                          )}
                        </li>
                      )
                    })}
                  </ul>
                )}
              </div>
            </div>
          )}

          {selectedNodeSpecs.length > 0 && (
            <div className="bg-gray-950/40 border border-gray-800 rounded-lg p-5">
              <div className="flex items-center gap-2 mb-4">
                <FileText className="w-4 h-4 text-emerald-300" />
                <h3 className="text-lg font-semibold text-gray-100">
                  Linked Specs ({selectedNodeSpecs.length})
                </h3>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {selectedNodeSpecs.map((spec) => (
                  <div
                    key={spec.id}
                    className="bg-gray-900/60 border border-gray-800 rounded-lg p-4 text-sm"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <p className="text-gray-200 font-medium">{spec.symbol}</p>
                        <p className="text-xs text-gray-500 mt-1">
                          {spec.responsibility}
                        </p>
                      </div>
                      <span
                        className={`px-2 py-1 text-[11px] rounded capitalize font-medium ${specStatusStyles[spec.status]}`}
                      >
                        {spec.status}
                      </span>
                    </div>
                    {spec.mustNever.length > 0 && (
                      <ul className="mt-3 text-xs text-red-300 space-y-1">
                        {spec.mustNever.slice(0, 3).map((rule, index) => (
                          <li key={`${spec.id}-rule-${index}`}>• {rule}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </section>

        <section className="bg-gray-900/70 border border-gray-800 rounded-xl p-6 shadow-lg shadow-purple-900/10 space-y-6">
          <div className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-blue-300" />
            <h2 className="text-xl font-semibold text-gray-100">
              Spec Contracts
            </h2>
          </div>
          {filteredSpecs.length === 0 ? (
            <div className="flex items-center justify-center py-10 text-gray-500 border border-dashed border-gray-800 rounded-lg">
              No specs matched your search.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredSpecs.map((spec) => (
                <button
                  key={spec.id}
                  type="button"
                  onClick={() => setSelectedSpecId(spec.id)}
                  className={`bg-gray-950/40 border border-gray-800 rounded-lg p-4 text-left transition-all hover:border-purple-500/50 hover:shadow-lg hover:shadow-purple-900/10 focus:outline-none focus:ring-2 focus:ring-purple-500/50 ${
                    selectedSpecId === spec.id
                      ? 'border-purple-500/70 shadow-lg shadow-purple-900/15'
                      : ''
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <p className="text-gray-100 font-semibold">{spec.symbol}</p>
                      <p className="text-xs text-gray-500 mt-1 capitalize">
                        Security: {spec.securityLevel}
                      </p>
                    </div>
                    <span
                      className={`px-2 py-1 text-[11px] rounded capitalize font-medium ${specStatusStyles[spec.status]}`}
                    >
                      {spec.status}
                    </span>
                  </div>
                  <p className="text-sm text-gray-400 mt-3 line-clamp-3">
                    {spec.responsibility}
                  </p>
                  {spec.mustNever.length > 0 && (
                    <ul className="mt-3 text-xs text-red-300 space-y-1">
                      {spec.mustNever.slice(0, 2).map((rule, index) => (
                        <li key={`${spec.id}-must-${index}`}>• {rule}</li>
                      ))}
                    </ul>
                  )}
                </button>
              ))}
            </div>
          )}

          {selectedSpec && (
            <div className="bg-gray-950/40 border border-gray-800 rounded-lg p-5">
              <div className="flex items-center gap-2 mb-4">
                <Activity className="w-4 h-4 text-amber-300" />
                <h3 className="text-lg font-semibold text-gray-100">
                  Spec Details: {selectedSpec.symbol}
                </h3>
              </div>
              <dl className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <MetricItem label="Risk level" value={selectedSpec.riskLevel} />
                <MetricItem
                  label="Performance budget"
                  value={`${selectedSpec.perfBudgetMs ?? '—'}ms`}
                />
                <MetricItem
                  label="Linked nodes"
                  value={selectedSpec.linkedNodeIds.length}
                />
              </dl>
              <div className="mt-4">
                <h4 className="text-sm font-medium text-gray-300 mb-1">
                  Responsibility
                </h4>
                <p className="text-sm text-gray-400">
                  {selectedSpec.responsibility}
                </p>
              </div>
            </div>
          )}
        </section>

        <section className="bg-gray-900/70 border border-gray-800 rounded-xl p-6 shadow-lg shadow-purple-900/10 space-y-6">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-purple-300" />
            <h2 className="text-xl font-semibold text-gray-100">
              Focus & Update History
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <HistoryColumn
              title="Focus History"
              icon={<Brain className="w-4 h-4 text-purple-300" />}
              emptyLabel="No focus events captured yet."
              entries={focusHistory.map((event) => ({
                id: `${event.type}-${event.timestamp}-${event.nodeId ?? ''}`,
                primary: event.type.replace(/_/g, ' '),
                secondary: event.nodeId ?? event.specId ?? event.eventId ?? '—',
                meta: `${event.sourcePane} pane`,
                timestamp: formatTimestamp(event.timestamp),
              }))}
            />

            <HistoryColumn
              title="Update History"
              icon={<FileText className="w-4 h-4 text-blue-300" />}
              emptyLabel="No update events captured yet."
              entries={updateHistory.map((event) => ({
                id: `${event.type}-${event.timestamp}-${event.nodeId ?? ''}`,
                primary: event.type.replace(/_/g, ' '),
                secondary: event.nodeId ?? event.specId ?? event.eventId ?? '—',
                meta: event.source,
                timestamp: formatTimestamp(event.timestamp),
              }))}
            />
          </div>
        </section>
      </div>
    </div>
  )
}

interface OverviewCardProps {
  title: string
  icon: React.ReactNode
  value: string
  subLabel: string
  badgeClass: string
}

const OverviewCard: React.FC<OverviewCardProps> = ({
  title,
  icon,
  value,
  subLabel,
  badgeClass,
}) => (
  <div className="bg-gray-950/40 border border-gray-800 rounded-lg p-4">
    <div className="flex items-center justify-between">
      <p className="text-sm text-gray-400">{title}</p>
      <span className={`px-2 py-1 text-xs rounded-full inline-flex items-center gap-2 ${badgeClass}`}>
        {icon}
        {subLabel}
      </span>
    </div>
    <p className="text-2xl font-semibold text-gray-100 mt-2">{value}</p>
  </div>
)

interface MetricItemProps {
  label: string
  value: React.ReactNode
}

const MetricItem: React.FC<MetricItemProps> = ({ label, value }) => (
  <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-3">
    <dt className="text-xs uppercase tracking-wide text-gray-500">{label}</dt>
    <dd className="text-sm text-gray-200 mt-1">{value}</dd>
  </div>
)

interface HistoryEntry {
  id: string
  primary: string
  secondary: string
  meta: string
  timestamp: string
}

interface HistoryColumnProps {
  title: string
  icon: React.ReactNode
  emptyLabel: string
  entries: HistoryEntry[]
}

const HistoryColumn: React.FC<HistoryColumnProps> = ({
  title,
  icon,
  emptyLabel,
  entries,
}) => (
  <div className="bg-gray-950/40 border border-gray-800 rounded-lg p-4 h-full">
    <div className="flex items-center gap-2 mb-3">
      {icon}
      <h3 className="text-lg font-semibold text-gray-100">{title}</h3>
    </div>
    {entries.length === 0 ? (
      <p className="text-sm text-gray-500">{emptyLabel}</p>
    ) : (
      <ul className="space-y-3 max-h-72 overflow-y-auto pr-2 text-sm">
        {entries.map((entry) => (
          <li key={entry.id} className="bg-gray-900/60 border border-gray-800 rounded-lg p-3">
            <div className="flex items-center justify-between text-gray-300">
              <span className="font-medium">{entry.primary}</span>
              <span className="text-xs text-gray-500">{entry.timestamp}</span>
            </div>
            <p className="text-xs text-gray-500 mt-1">{entry.secondary}</p>
            <p className="text-xs text-indigo-300 mt-1 uppercase tracking-wide">{entry.meta}</p>
          </li>
        ))}
      </ul>
    )}
  </div>
)
