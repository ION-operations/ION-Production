/**
 * Progress Monitor Component
 * Displays task progress with status indicator
 */

import React from 'react'
import { CheckCircle, XCircle, Loader2, Clock } from 'lucide-react'

export interface ProgressMonitorProps {
  taskId: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number // 0-100
  error?: string
  onCancel?: () => void
  showCancel?: boolean
}

export const ProgressMonitor: React.FC<ProgressMonitorProps> = ({
  taskId,
  status,
  progress,
  error,
  onCancel,
  showCancel = true,
}) => {
  const getStatusIcon = () => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />
      case 'processing':
        return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
      default:
        return <Clock className="w-5 h-5 text-gray-500" />
    }
  }

  const getStatusText = () => {
    switch (status) {
      case 'completed':
        return 'Completed'
      case 'failed':
        return 'Failed'
      case 'processing':
        return 'Processing'
      default:
        return 'Pending'
    }
  }

  return (
    <div className="p-4 bg-gray-900 rounded-lg border border-gray-700">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          {getStatusIcon()}
          <span className="text-sm font-medium text-gray-300">
            {getStatusText()}
          </span>
        </div>
        {showCancel && status === 'processing' && onCancel && (
          <button
            onClick={onCancel}
            className="text-xs text-red-400 hover:text-red-300 px-2 py-1 rounded hover:bg-red-900/20 transition-colors"
          >
            Cancel
          </button>
        )}
      </div>

      {/* Progress Bar */}
      {status === 'processing' && (
        <div className="mb-2">
          <div className="w-full bg-gray-700 rounded-full h-2 overflow-hidden">
            <div
              className="bg-blue-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
          <div className="flex justify-between mt-1">
            <span className="text-xs text-gray-400">Task ID: {taskId.slice(0, 8)}...</span>
            <span className="text-xs text-gray-400">{progress}%</span>
          </div>
        </div>
      )}

      {/* Error Display */}
      {status === 'failed' && error && (
        <div className="mt-2 p-2 bg-red-900/20 border border-red-700/50 rounded text-sm text-red-300">
          {error}
        </div>
      )}

      {/* Success Message */}
      {status === 'completed' && (
        <div className="mt-2 text-sm text-green-400">
          Task completed successfully!
        </div>
      )}
    </div>
  )
}

