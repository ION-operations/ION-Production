import React, { useState, useEffect, useCallback } from 'react'
import { Eye, GitBranch, Clock, AlertTriangle, CheckCircle, XCircle, Zap, Activity, Shield } from 'lucide-react'
import { httpLucidDaemonService, SpecBlock, BlueprintSlice, TimelineSummary, ChangeProposal } from '../services/HttpLucidDaemonService'
import { LucidGraphVisualization } from './LucidGraphVisualization'
import { ProgressTelemetryPanel } from './LucidOrchestrator/ProgressTelemetryPanel'
import { ConfidenceRoutingPanel } from './LucidOrchestrator/ConfidenceRoutingPanel'
import { progressTelemetryService, ProgressTelemetrySnapshot } from '@/services/progressTelemetryService'
import { confidenceRoutingService, ConfidenceRoutingSnapshot } from '@/services/confidenceRoutingService'

interface LucidOrchestratorPanelProps {
  nodeId?: string
  onNodeFocus?: (nodeId: string) => void
}

export const LucidOrchestratorPanel: React.FC<LucidOrchestratorPanelProps> = ({
  nodeId,
  onNodeFocus
}) => {
  const [activeTab, setActiveTab] = useState<'spec' | 'blueprint' | 'timeline' | 'telemetry' | 'confidence'>('spec')
  const [specData, setSpecData] = useState<SpecBlock | null>(null)
  const [blueprintData, setBlueprintData] = useState<BlueprintSlice | null>(null)
  const [timelineData, setTimelineData] = useState<TimelineSummary | null>(null)
  const [loading, setLoading] = useState(false)
  const [daemonConnected, setDaemonConnected] = useState(false)
  const [telemetrySnapshot, setTelemetrySnapshot] = useState<ProgressTelemetrySnapshot | null>(null)
  const [telemetryLoading, setTelemetryLoading] = useState(false)
  const [telemetryError, setTelemetryError] = useState<string | null>(null)
  const [confidenceSnapshot, setConfidenceSnapshot] = useState<ConfidenceRoutingSnapshot | null>(null)
  const [confidenceLoading, setConfidenceLoading] = useState(false)
  const [confidenceError, setConfidenceError] = useState<string | null>(null)

  useEffect(() => {
    setDaemonConnected(httpLucidDaemonService.isDaemonConnected())
  }, [])

  const loadTelemetry = useCallback(async () => {
    setTelemetryLoading(true)
    setTelemetryError(null)
    try {
      const snapshot = await progressTelemetryService.getSnapshot()
      setTelemetrySnapshot(snapshot)
    } catch (err) {
      console.error('Failed to load telemetry snapshot', err)
      setTelemetryError('Unable to load predictive metrics prototype')
    } finally {
      setTelemetryLoading(false)
    }
  }, [])

  const loadConfidence = useCallback(async () => {
    setConfidenceLoading(true)
    setConfidenceError(null)
    try {
      const data = await confidenceRoutingService.getSnapshot()
      setConfidenceSnapshot(data)
    } catch (err) {
      console.error('Failed to load confidence routing snapshot', err)
      setConfidenceError('Unable to load confidence routing prototype')
    } finally {
      setConfidenceLoading(false)
    }
  }, [])

  useEffect(() => {
    if (nodeId) {
      loadData(nodeId)
    } else {
      // Load default data if no nodeId provided
      loadData('test')
    }
  }, [nodeId, loadData])

  useEffect(() => {
    loadTelemetry()
  }, [loadTelemetry])

  useEffect(() => {
    loadConfidence()
  }, [loadConfidence])

  const loadData = useCallback(async (id: string) => {
    setLoading(true)
    try {
      const [spec, blueprint, timeline] = await Promise.all([
        httpLucidDaemonService.getSpecBlock(id),
        httpLucidDaemonService.getBlueprintSlice(id),
        httpLucidDaemonService.getTimelineSummary(id)
      ])
      
      setSpecData(spec)
      setBlueprintData(blueprint)
      setTimelineData(timeline)
    } catch (error) {
      console.error('Failed to load Lucid data:', error)
    } finally {
      setLoading(false)
    }
  }, [])

  const handleProposeChange = async () => {
    if (!nodeId) return
    
    try {
      const proposal = await httpLucidDaemonService.proposeChange(nodeId)
      // Handle change proposal UI
      console.log('Change proposal:', proposal)
    } catch (error) {
      console.error('Failed to get change proposal:', error)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'clean': return <CheckCircle className="w-4 h-4 text-green-400" />
      case 'drift': return <AlertTriangle className="w-4 h-4 text-yellow-400" />
      case 'violation': return <XCircle className="w-4 h-4 text-red-400" />
      default: return <Zap className="w-4 h-4 text-gray-400" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'clean': return 'text-green-400'
      case 'drift': return 'text-yellow-400'
      case 'violation': return 'text-red-400'
      default: return 'text-gray-400'
    }
  }

  const renderSpecTab = () => {
    if (!specData) return <div className="p-4 text-gray-400">No spec data available</div>

    return (
      <div className="p-4 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-white">Specification</h3>
          <div className="flex items-center gap-2">
            {getStatusIcon(specData.status)}
            <span className={`text-sm font-medium ${getStatusColor(specData.status)}`}>
              {specData.status.toUpperCase()}
            </span>
          </div>
        </div>

        <div className="space-y-3">
          <div>
            <label className="text-sm font-medium text-gray-300">Responsibility</label>
            <p className="text-gray-200 mt-1">{specData.responsibility}</p>
          </div>

          <div>
            <label className="text-sm font-medium text-gray-300">Must Never</label>
            <ul className="mt-1 space-y-1">
              {specData.must_never.map((constraint, index) => (
                <li key={index} className="text-red-300 text-sm flex items-start gap-2">
                  <span className="text-red-500">•</span>
                  {constraint}
                </li>
              ))}
            </ul>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-gray-300">Inputs</label>
              <p className="text-gray-200 text-sm mt-1">{specData.inputs.join(', ')}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-300">Outputs</label>
              <p className="text-gray-200 text-sm mt-1">{specData.outputs.join(', ')}</p>
            </div>
          </div>

          <div>
            <label className="text-sm font-medium text-gray-300">Side Effects</label>
            <p className="text-gray-200 text-sm mt-1">{specData.side_effects.join(', ')}</p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-gray-300">Security Level</label>
              <p className="text-yellow-400 text-sm mt-1 font-medium">{specData.security_level.toUpperCase()}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-300">Performance Budget</label>
              <p className="text-gray-200 text-sm mt-1">{specData.perf_budget_ms}ms</p>
            </div>
          </div>

          {specData.drift_reason && (
            <div className="bg-yellow-900/20 border border-yellow-500/30 rounded p-3">
              <label className="text-sm font-medium text-yellow-300">Drift Reason</label>
              <p className="text-yellow-200 text-sm mt-1">{specData.drift_reason}</p>
            </div>
          )}

          <button
            onClick={handleProposeChange}
            className="w-full bg-blue-600 hover:bg-blue-500 text-white py-2 px-4 rounded text-sm font-medium transition-colors"
          >
            Propose Change
          </button>
        </div>
      </div>
    )
  }

  const renderBlueprintTab = () => {
    if (!blueprintData) return <div className="p-4 text-gray-400">No blueprint data available</div>

    return (
      <div className="p-4 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-white">Blueprint</h3>
          <div className="text-sm text-gray-400">
            Blast Radius: {blueprintData.blast_radius.direct} direct, {blueprintData.blast_radius.indirect} indirect
          </div>
        </div>

        {/* Interactive Graph Visualization */}
        <div className="mb-4">
          <LucidGraphVisualization
            centerNode={{
              id: blueprintData.center.node_id,
              name: blueprintData.center.name,
              kind: blueprintData.center.kind,
              status: blueprintData.center.status,
              security_level: blueprintData.center.security_level
            }}
            incoming={blueprintData.incoming.map(edge => ({
              id: edge.node_id,
              name: edge.name,
              kind: edge.kind,
              status: edge.status,
              security_level: edge.security_level
            }))}
            outgoing={blueprintData.outgoing.map(edge => ({
              id: edge.node_id,
              name: edge.name,
              kind: edge.kind,
              status: edge.status,
              security_level: edge.security_level
            }))}
            onNodeClick={(nodeId) => {
              if (onNodeFocus) {
                onNodeFocus(nodeId)
              }
            }}
            width={350}
            height={250}
          />
        </div>

        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium text-gray-300">Center Node</label>
            <div className="mt-1 p-3 bg-gray-800 rounded border">
              <div className="flex items-center gap-2">
                {getStatusIcon(blueprintData.center.status)}
                <span className="text-white font-medium">{blueprintData.center.name}</span>
                <span className="text-gray-400 text-sm">({blueprintData.center.kind})</span>
              </div>
              {blueprintData.center.security_level && (
                <div className="text-yellow-400 text-xs mt-1">
                  Security: {blueprintData.center.security_level.toUpperCase()}
                </div>
              )}
            </div>
          </div>

          <div>
            <label className="text-sm font-medium text-gray-300">Incoming Dependencies ({blueprintData.incoming.length})</label>
            <div className="mt-1 space-y-2">
              {blueprintData.incoming.map((edge, index) => (
                <div key={index} className="p-2 bg-gray-800 rounded border border-gray-700">
                  <div className="flex items-center gap-2">
                    {getStatusIcon(edge.status)}
                    <span className="text-white text-sm">{edge.name}</span>
                    <span className="text-gray-400 text-xs">({edge.kind})</span>
                    <span className="text-blue-400 text-xs">{edge.edge_type}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div>
            <label className="text-sm font-medium text-gray-300">Outgoing Dependencies ({blueprintData.outgoing.length})</label>
            <div className="mt-1 space-y-2">
              {blueprintData.outgoing.map((edge, index) => (
                <div key={index} className="p-2 bg-gray-800 rounded border border-gray-700">
                  <div className="flex items-center gap-2">
                    {getStatusIcon(edge.status)}
                    <span className="text-white text-sm">{edge.name}</span>
                    <span className="text-gray-400 text-xs">({edge.kind})</span>
                    <span className="text-green-400 text-xs">{edge.edge_type}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    )
  }

  const renderTimelineTab = () => {
    if (!timelineData) return <div className="p-4 text-gray-400">No timeline data available</div>

    return (
      <div className="p-4 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-white">Timeline</h3>
          <div className="text-sm text-gray-400">
            {timelineData.recent_runs.length} recent runs
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium text-gray-300">Recent Executions</label>
            <div className="mt-1 space-y-2">
              {timelineData.recent_runs.map((run, index) => (
                <div key={index} className="p-2 bg-gray-800 rounded border border-gray-700">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      {getStatusIcon(run.status)}
                      <span className="text-white text-sm">{run.duration_ms}ms</span>
                      <span className="text-gray-400 text-xs">{run.thread}</span>
                    </div>
                    <span className="text-gray-400 text-xs">
                      {new Date(run.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  {run.violations.length > 0 && (
                    <div className="text-red-400 text-xs mt-1">
                      Violations: {run.violations.join(', ')}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {timelineData.worst_run_cascade.length > 0 && (
            <div>
              <label className="text-sm font-medium text-gray-300">Worst Execution Cascade</label>
              <div className="mt-1 space-y-1">
                {timelineData.worst_run_cascade.map((step, index) => (
                  <div key={index} className="flex items-center gap-2 text-sm">
                    <span className="text-gray-400">{'  '.repeat(index)}</span>
                    <span className="text-white">{step.symbol}</span>
                    <span className="text-gray-400">- {step.action}</span>
                    <span className="text-yellow-400">{step.duration_ms}ms</span>
                    {step.thread && (
                      <span className="text-blue-400 text-xs">({step.thread})</span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    )
  }

  const renderTelemetryTab = () => (
    <ProgressTelemetryPanel
      snapshot={telemetrySnapshot}
      loading={telemetryLoading}
      error={telemetryError}
      onRefresh={loadTelemetry}
    />
  )

  const renderConfidenceTab = () => (
    <ConfidenceRoutingPanel
      snapshot={confidenceSnapshot}
      loading={confidenceLoading}
      error={confidenceError}
      onRefresh={loadConfidence}
    />
  )

  // Always show the panel, load default data if no nodeId

  return (
    <div className="h-full flex flex-col bg-gray-900">
      {/* Header */}
      <div className="flex items-center gap-2 px-4 py-3 bg-gray-800 border-b border-gray-700">
        <div className="flex items-center gap-2">
          <Eye className="w-4 h-4 text-blue-400" />
          <span className="text-sm font-medium text-white">Lucid Intelligence</span>
        </div>
        <div className="flex items-center gap-1 ml-auto">
          <div className={`w-2 h-2 rounded-full ${daemonConnected ? 'bg-green-400' : 'bg-red-400'}`} />
          <span className="text-xs text-gray-400">
            {daemonConnected ? 'Connected' : 'Offline'}
          </span>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-700">
        <button
          onClick={() => setActiveTab('spec')}
          className={`px-4 py-2 text-sm font-medium transition-colors ${
            activeTab === 'spec'
              ? 'text-blue-400 border-b-2 border-blue-400'
              : 'text-gray-400 hover:text-white'
          }`}
        >
          <Eye className="w-4 h-4 inline mr-2" />
          Spec
        </button>
        <button
          onClick={() => setActiveTab('blueprint')}
          className={`px-4 py-2 text-sm font-medium transition-colors ${
            activeTab === 'blueprint'
              ? 'text-green-400 border-b-2 border-green-400'
              : 'text-gray-400 hover:text-white'
          }`}
        >
          <GitBranch className="w-4 h-4 inline mr-2" />
          Blueprint
        </button>
        <button
          onClick={() => setActiveTab('timeline')}
          className={`px-4 py-2 text-sm font-medium transition-colors ${
            activeTab === 'timeline'
              ? 'text-orange-400 border-b-2 border-orange-400'
              : 'text-gray-400 hover:text-white'
          }`}
        >
          <Clock className="w-4 h-4 inline mr-2" />
          Timeline
        </button>
        <button
          onClick={() => setActiveTab('telemetry')}
          className={`px-4 py-2 text-sm font-medium transition-colors ${
            activeTab === 'telemetry'
              ? 'text-indigo-400 border-b-2 border-indigo-400'
              : 'text-gray-400 hover:text-white'
          }`}
        >
          <Activity className="w-4 h-4 inline mr-2" />
          Telemetry
        </button>
        <button
          onClick={() => setActiveTab('confidence')}
          className={`px-4 py-2 text-sm font-medium transition-colors ${
            activeTab === 'confidence'
              ? 'text-emerald-400 border-b-2 border-emerald-400'
              : 'text-gray-400 hover:text-white'
          }`}
        >
          <Shield className="w-4 h-4 inline mr-2" />
          Confidence
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="p-4 text-center text-gray-400">
            <div className="animate-spin w-6 h-6 border-2 border-blue-400 border-t-transparent rounded-full mx-auto mb-2" />
            Loading intelligence data...
          </div>
        ) : (
          <>
            {activeTab === 'spec' && renderSpecTab()}
            {activeTab === 'blueprint' && renderBlueprintTab()}
            {activeTab === 'timeline' && renderTimelineTab()}
            {activeTab === 'telemetry' && renderTelemetryTab()}
            {activeTab === 'confidence' && renderConfidenceTab()}
          </>
        )}
      </div>
    </div>
  )
}
