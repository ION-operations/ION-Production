import React from 'react'
import { useApp } from '../contexts/AppContext'
import { Brain, Cpu, Database, Network, X } from 'lucide-react'

export function AIProcessVisualization() {
  const { state, dispatch } = useApp()

  if (!state.aiProcessVisualization.isVisible) {
    return null
  }

  const processes = [
    { id: 'input', name: 'Input Processing', icon: Brain, progress: 85, status: 'active' },
    { id: 'reasoning', name: 'Reasoning Engine', icon: Cpu, progress: 60, status: 'active' },
    { id: 'memory', name: 'Memory Retrieval', icon: Database, progress: 40, status: 'pending' },
    { id: 'response', name: 'Response Generation', icon: Network, progress: 0, status: 'pending' }
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'text-blue-400'
      case 'completed':
        return 'text-green-400'
      case 'pending':
        return 'text-gray-400'
      case 'error':
        return 'text-red-400'
      default:
        return 'text-gray-400'
    }
  }

  const getProgressColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-blue-500'
      case 'completed':
        return 'bg-green-500'
      case 'error':
        return 'bg-red-500'
      default:
        return 'bg-gray-500'
    }
  }

  return (
    <div className="fixed bottom-4 right-4 w-80 bg-black/80 backdrop-blur-md border border-white/20 rounded-2xl p-4 z-50 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Brain className="w-5 h-5 text-blue-400" />
          <h3 className="font-semibold text-white">AI Process Visualization</h3>
        </div>
        <button
          onClick={() => dispatch({ type: 'TOGGLE_AI_PROCESS_VISUALIZATION' })}
          className="p-1 hover:bg-white/10 rounded-lg transition-colors"
        >
          <X className="w-4 h-4 text-gray-400" />
        </button>
      </div>

      {/* Current Step */}
      {state.aiProcessVisualization.currentStep && (
        <div className="mb-4 p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg">
          <p className="text-sm text-blue-400">
            Current Step: {state.aiProcessVisualization.currentStep}
          </p>
          <div className="mt-2 bg-blue-500/20 rounded-full h-2">
            <div
              className="bg-blue-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${state.aiProcessVisualization.progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Process List */}
      <div className="space-y-3">
        {processes.map((process) => (
          <div key={process.id} className="flex items-center space-x-3">
            <div className={`p-2 rounded-lg ${getStatusColor(process.status)}`}>
              <process.icon className="w-4 h-4" />
            </div>
            
            <div className="flex-1">
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm text-white">{process.name}</span>
                <span className={`text-xs ${getStatusColor(process.status)}`}>
                  {process.progress}%
                </span>
              </div>
              
              <div className="bg-gray-700 rounded-full h-1.5">
                <div
                  className={`h-1.5 rounded-full transition-all duration-500 ${getProgressColor(process.status)}`}
                  style={{ width: `${process.progress}%` }}
                />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Neural Network Visualization */}
      <div className="mt-4 p-3 bg-purple-500/10 border border-purple-500/20 rounded-lg">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-purple-400">Neural Network</span>
          <span className="text-xs text-gray-400">Active</span>
        </div>
        
        <div className="flex items-center justify-center space-x-1">
          {[...Array(5)].map((_, i) => (
            <div
              key={i}
              className="w-2 h-2 bg-purple-400 rounded-full animate-pulse"
              style={{ animationDelay: `${i * 0.2}s` }}
            />
          ))}
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="mt-4 grid grid-cols-2 gap-3">
        <div className="text-center">
          <div className="text-lg font-bold text-green-400">99.9%</div>
          <div className="text-xs text-gray-400">Accuracy</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold text-blue-400">45ms</div>
          <div className="text-xs text-gray-400">Response Time</div>
        </div>
      </div>
    </div>
  )
}
