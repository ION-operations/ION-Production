// Log-Sentinels Anomalies Panel - Bottom Left Anomalies
// Displays Forensics reports with root causes, fix suggestions, and evidence

import React, { useState } from 'react'
import { useLogSentinels } from '../hooks/useLogSentinels'
import { BasePanel } from '../components/BasePanel'
import { LoadingSpinner, ErrorDisplay } from '../components/shared/shared'
import { 
  AlertTriangle, 
  CheckCircle, 
  XCircle,
  Play,
  Code,
  FileText,
  Link as LinkIcon
} from 'lucide-react'

export const LogSentinelsAnomalies: React.FC = () => {
  const { forensics, loading, error, runTool } = useLogSentinels()

  if (loading) {
    return (
      <BasePanel id="log-sentinels-anomalies" title="Anomalies" icon={AlertTriangle}>
        <LoadingSpinner />
      </BasePanel>
    )
  }

  if (error) {
    return (
      <BasePanel id="log-sentinels-anomalies" title="Anomalies" icon={AlertTriangle}>
        <ErrorDisplay error={error} />
      </BasePanel>
    )
  }

  return (
    <BasePanel id="log-sentinels-anomalies" title="Anomalies" icon={AlertTriangle}>
      <div className="flex flex-col gap-2 p-2">
        {forensics.length === 0 ? (
          <div className="text-gray-400 text-sm text-center py-8">
            No anomalies detected
          </div>
        ) : (
          forensics.map((forensic) => (
            <ForensicsCard
              key={forensic.window_id}
              forensic={forensic}
              onRunTool={runTool}
            />
          ))
        )}
      </div>
    </BasePanel>
  )
}

interface ForensicsCardProps {
  forensic: any
  onRunTool: (toolName: string) => Promise<any>
}

const ForensicsCard: React.FC<ForensicsCardProps> = ({ forensic, onRunTool }) => {
  const [expanded, setExpanded] = useState(false)
  const [runningTool, setRunningTool] = useState<string | null>(null)

  const handleRunTool = async (toolName: string) => {
    setRunningTool(toolName)
    try {
      await onRunTool(toolName)
    } catch (err) {
      console.error('Failed to run tool:', err)
    } finally {
      setRunningTool(null)
    }
  }

  const gatePassed = forensic.gate?.passed !== false

  return (
    <div className="border border-gray-700 rounded-lg p-3 bg-gray-800/50 hover:bg-gray-800 transition-colors">
      <div className="flex items-start justify-between mb-2">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className={`text-xs px-2 py-1 rounded border ${
              forensic.severity === 'high' 
                ? 'text-red-400 border-red-500 bg-red-900/20'
                : forensic.severity === 'medium'
                ? 'text-yellow-400 border-yellow-500 bg-yellow-900/20'
                : 'text-blue-400 border-blue-500 bg-blue-900/20'
            }`}>
              {forensic.severity.toUpperCase()}
            </span>
            {gatePassed ? (
              <CheckCircle className="w-4 h-4 text-green-400" />
            ) : (
              <XCircle className="w-4 h-4 text-red-400" />
            )}
          </div>
          
          <p className="text-sm text-gray-200 mb-2">{forensic.summary}</p>
          
          {forensic.root_cause && (
            <div className="mb-2">
              <div className="text-xs text-gray-400 mb-1">Root Cause:</div>
              <p className="text-sm text-gray-300">{forensic.root_cause}</p>
            </div>
          )}
        </div>
      </div>

      {forensic.fix_suggestion && (
        <div className="mt-2 pt-2 border-t border-gray-700">
          <div className="flex items-center gap-2 mb-2">
            <Code className="w-4 h-4 text-blue-400" />
            <span className="text-xs font-semibold text-gray-300">Fix Suggestion</span>
          </div>
          
          {forensic.fix_suggestion.patch && (
            <div className="mb-2">
              <pre className="text-xs bg-gray-900 p-2 rounded overflow-x-auto">
                {forensic.fix_suggestion.patch}
              </pre>
            </div>
          )}
          
          {forensic.fix_suggestion.steps && forensic.fix_suggestion.steps.length > 0 && (
            <div className="mb-2">
              <div className="text-xs text-gray-400 mb-1">Steps:</div>
              <ol className="list-decimal list-inside text-xs text-gray-300 space-y-1">
                {forensic.fix_suggestion.steps.map((step: string, idx: number) => (
                  <li key={idx}>{step}</li>
                ))}
              </ol>
            </div>
          )}
        </div>
      )}

      {forensic.suggested_tools && forensic.suggested_tools.length > 0 && (
        <div className="mt-2 pt-2 border-t border-gray-700">
          <div className="flex items-center gap-2 mb-2">
            <Play className="w-4 h-4 text-green-400" />
            <span className="text-xs font-semibold text-gray-300">Suggested Actions</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {forensic.suggested_tools.map((tool: string, idx: number) => (
              <button
                key={idx}
                onClick={() => handleRunTool(tool)}
                disabled={runningTool === tool}
                className="text-xs px-2 py-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-700 disabled:cursor-not-allowed rounded flex items-center gap-1"
              >
                <Play className="w-3 h-3" />
                {runningTool === tool ? 'Running...' : tool}
              </button>
            ))}
          </div>
        </div>
      )}

      {forensic.evidence && forensic.evidence.length > 0 && (
        <div className="mt-2 pt-2 border-t border-gray-700">
          <div className="flex items-center gap-2 mb-1">
            <LinkIcon className="w-4 h-4 text-purple-400" />
            <span className="text-xs font-semibold text-gray-300">Evidence</span>
          </div>
          <div className="flex flex-wrap gap-1">
            {forensic.evidence.map((evidence: string, idx: number) => (
              <span
                key={idx}
                className="text-xs px-2 py-0.5 bg-purple-900/30 border border-purple-700 rounded text-purple-300"
              >
                {evidence}
              </span>
            ))}
          </div>
        </div>
      )}

      {forensic.gate && !forensic.gate.passed && forensic.gate.reasons && (
        <div className="mt-2 pt-2 border-t border-red-700">
          <div className="flex items-center gap-2 mb-1">
            <XCircle className="w-4 h-4 text-red-400" />
            <span className="text-xs font-semibold text-red-300">VIF Gate Failed</span>
          </div>
          <ul className="list-disc list-inside text-xs text-red-300 space-y-1">
            {forensic.gate.reasons.map((reason: string, idx: number) => (
              <li key={idx}>{reason}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

