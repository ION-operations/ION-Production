/**
 * Autonomous Operation Panel Component
 * UI for controlling and monitoring autonomous agent operation
 */

import React, { useState, useEffect } from 'react'
import { Play, Pause, Square, RefreshCw, CheckCircle, XCircle, Clock, TrendingUp } from 'lucide-react'
import { getAutonomousOperationService, AutonomousStatus, AutonomousTask } from '../services/autonomousOperationService'

export const AutonomousOperationPanel: React.FC = () => {
  const [status, setStatus] = useState<AutonomousStatus>({
    isActive: false,
    isPaused: false,
    currentTask: null,
    confidence: 0.0,
    startTime: null,
    pauseTime: null,
    tasksCompleted: 0,
    tasksFailed: 0,
    uptime: 0,
    qualityScore: 0.0,
    lastCheckTime: null,
    shouldContinue: false
  })
  const [initialTask, setInitialTask] = useState('')
  const [initialConfidence, setInitialConfidence] = useState(0.70)
  const [logs, setLogs] = useState<Array<{ level: 'log' | 'warn' | 'error'; message: string; timestamp: string }>>([])
  const [completedTasks, setCompletedTasks] = useState<AutonomousTask[]>([])

  const autonomousService = getAutonomousOperationService()

  useEffect(() => {
    // Set up callbacks
    autonomousService.setCallbacks({
      onStatusChange: (newStatus) => {
        setStatus(newStatus)
      },
      onTaskComplete: (task) => {
        setCompletedTasks(prev => [task, ...prev].slice(0, 50)) // Keep last 50
        addLog('log', `Task completed: ${task.task}`)
      },
      onTaskError: (task, error) => {
        addLog('error', `Task failed: ${task.task} - ${error.message || error}`)
      },
      onLog: (level, message) => {
        addLog(level, message)
      }
    })

    // Get initial status
    autonomousService.getStatus().then(setStatus)

    // Poll status periodically
    const interval = setInterval(() => {
      autonomousService.getStatus().then(setStatus)
    }, 5000)

    return () => clearInterval(interval)
  }, [])

  const addLog = (level: 'log' | 'warn' | 'error', message: string) => {
    setLogs(prev => [...prev, { level, message, timestamp: new Date().toISOString() }].slice(-100)) // Keep last 100
  }

  const handleStart = async () => {
    if (!initialTask.trim()) {
      addLog('error', 'Please enter a task to start autonomous operation')
      return
    }

    addLog('log', `Starting autonomous operation: ${initialTask}`)
    const result = await autonomousService.start(initialTask, initialConfidence)
    
    if (!result.success) {
      addLog('error', result.error || 'Failed to start autonomous operation')
    }
  }

  const handlePause = async () => {
    addLog('log', 'Pausing autonomous operation...')
    const result = await autonomousService.pause()
    
    if (!result.success) {
      addLog('error', result.error || 'Failed to pause autonomous operation')
    }
  }

  const handleResume = async () => {
    addLog('log', 'Resuming autonomous operation...')
    const result = await autonomousService.resume()
    
    if (!result.success) {
      addLog('error', result.error || 'Failed to resume autonomous operation')
    }
  }

  const handleStop = async () => {
    addLog('log', 'Stopping autonomous operation...')
    const result = await autonomousService.stop()
    
    if (!result.success) {
      addLog('error', result.error || 'Failed to stop autonomous operation')
    }
  }

  const formatUptime = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60
    return `${hours}h ${minutes}m ${secs}s`
  }

  return (
    <div className="flex flex-col h-full bg-gray-900 text-white p-6">
      <h2 className="text-2xl font-bold mb-6">🤖 Autonomous Operation</h2>

      {/* Control Panel */}
      <div className="bg-gray-800 rounded-lg p-4 mb-6">
        <h3 className="text-lg font-semibold mb-4">Control</h3>
        
        {!status.isActive ? (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Initial Task</label>
              <input
                type="text"
                value={initialTask}
                onChange={(e) => setInitialTask(e.target.value)}
                placeholder="Enter task to start autonomous operation..."
                className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Confidence Threshold</label>
              <input
                type="number"
                min="0"
                max="1"
                step="0.1"
                value={initialConfidence}
                onChange={(e) => setInitialConfidence(parseFloat(e.target.value))}
                className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500"
              />
            </div>
            <button
              onClick={handleStart}
              className="flex items-center gap-2 px-6 py-2 bg-green-600 hover:bg-green-700 rounded-lg font-medium transition-colors"
            >
              <Play className="w-5 h-5" />
              Start Autonomous Operation
            </button>
          </div>
        ) : (
          <div className="flex gap-4">
            {status.isPaused ? (
              <button
                onClick={handleResume}
                className="flex items-center gap-2 px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors"
              >
                <Play className="w-5 h-5" />
                Resume
              </button>
            ) : (
              <button
                onClick={handlePause}
                className="flex items-center gap-2 px-6 py-2 bg-yellow-600 hover:bg-yellow-700 rounded-lg font-medium transition-colors"
              >
                <Pause className="w-5 h-5" />
                Pause
              </button>
            )}
            <button
              onClick={handleStop}
              className="flex items-center gap-2 px-6 py-2 bg-red-600 hover:bg-red-700 rounded-lg font-medium transition-colors"
            >
              <Square className="w-5 h-5" />
              Stop
            </button>
          </div>
        )}
      </div>

      {/* Status Dashboard */}
      {status.isActive && (
        <div className="bg-gray-800 rounded-lg p-4 mb-6">
          <h3 className="text-lg font-semibold mb-4">Status</h3>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-gray-700 rounded-lg p-3">
              <div className="text-sm text-gray-400 mb-1">Status</div>
              <div className="text-xl font-bold">
                {status.isPaused ? '⏸️ Paused' : '▶️ Active'}
              </div>
            </div>
            
            <div className="bg-gray-700 rounded-lg p-3">
              <div className="text-sm text-gray-400 mb-1">Confidence</div>
              <div className="text-xl font-bold">
                {(status.confidence * 100).toFixed(0)}%
              </div>
            </div>
            
            <div className="bg-gray-700 rounded-lg p-3">
              <div className="text-sm text-gray-400 mb-1">Uptime</div>
              <div className="text-xl font-bold">
                {formatUptime(status.uptime)}
              </div>
            </div>
            
            <div className="bg-gray-700 rounded-lg p-3">
              <div className="text-sm text-gray-400 mb-1">Completed</div>
              <div className="text-xl font-bold flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-500" />
                {status.tasksCompleted}
              </div>
            </div>
          </div>

          {status.currentTask && (
            <div className="mt-4 bg-gray-700 rounded-lg p-3">
              <div className="text-sm text-gray-400 mb-1">Current Task</div>
              <div className="text-lg font-medium">{status.currentTask}</div>
            </div>
          )}

          {!status.shouldContinue && status.reason && (
            <div className="mt-4 bg-yellow-900/50 border border-yellow-600 rounded-lg p-3">
              <div className="text-sm text-yellow-400">⚠️ {status.reason}</div>
            </div>
          )}
        </div>
      )}

      {/* Task List */}
      {completedTasks.length > 0 && (
        <div className="bg-gray-800 rounded-lg p-4 mb-6">
          <h3 className="text-lg font-semibold mb-4">Completed Tasks</h3>
          <div className="space-y-2 max-h-60 overflow-y-auto">
            {completedTasks.map((task, index) => (
              <div key={index} className="bg-gray-700 rounded-lg p-3 flex items-center justify-between">
                <div className="flex-1">
                  <div className="font-medium">{task.task}</div>
                  <div className="text-sm text-gray-400">
                    Confidence: {(task.confidence * 100).toFixed(0)}% | Priority: {task.priority}
                  </div>
                </div>
                <CheckCircle className="w-5 h-5 text-green-500" />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Logs */}
      <div className="bg-gray-800 rounded-lg p-4 flex-1 overflow-hidden flex flex-col">
        <h3 className="text-lg font-semibold mb-4">Logs</h3>
        <div className="flex-1 overflow-y-auto space-y-2 font-mono text-sm">
          {logs.length === 0 ? (
            <div className="text-gray-500">No logs yet...</div>
          ) : (
            logs.map((log, index) => (
              <div
                key={index}
                className={`p-2 rounded ${
                  log.level === 'error' ? 'bg-red-900/30 text-red-300' :
                  log.level === 'warn' ? 'bg-yellow-900/30 text-yellow-300' :
                  'bg-gray-700/50 text-gray-300'
                }`}
              >
                <span className="text-gray-500">[{new Date(log.timestamp).toLocaleTimeString()}]</span>{' '}
                <span className={log.level === 'error' ? 'font-bold' : ''}>{log.message}</span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}

export default AutonomousOperationPanel

