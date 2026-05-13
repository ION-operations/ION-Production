import React, { useState, useEffect } from 'react'
import { Clock, Activity, Brain, Zap, Code } from 'lucide-react'
import { aimosClient } from '../lib/aimos-client'

interface TimelineEntry {
  id: string
  timestamp: Date
  type: string
  content: string
  context?: any
}

export const TimelineVisualization: React.FC<{ isOpen: boolean; onClose: () => void }> = ({ isOpen, onClose }) => {
  const [entries, setEntries] = useState<TimelineEntry[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!isOpen) return

    const loadTimeline = async () => {
      try {
        // Note: This would connect to actual timeline API
        // For now, we'll create sample data
        const sampleEntries: TimelineEntry[] = [
          {
            id: '1',
            timestamp: new Date(Date.now() - 30000),
            type: 'ai_interaction',
            content: 'User asked about IDE features'
          },
          {
            id: '2',
            timestamp: new Date(Date.now() - 60000),
            type: 'memory_stored',
            content: 'Stored IDE session context'
          },
          {
            id: '3',
            timestamp: new Date(Date.now() - 120000),
            type: 'confidence_tracked',
            content: 'Tracked confidence: 0.85'
          }
        ]
        setEntries(sampleEntries)
      } catch (error) {
        console.error('Failed to load timeline:', error)
      } finally {
        setLoading(false)
      }
    }

    loadTimeline()
  }, [isOpen])

  const getIcon = (type: string) => {
    switch (type) {
      case 'ai_interaction':
        return <Brain className="w-4 h-4 text-blue-500" />
      case 'memory_stored':
        return <Activity className="w-4 h-4 text-purple-500" />
      case 'confidence_tracked':
        return <Zap className="w-4 h-4 text-yellow-500" />
      default:
        return <Code className="w-4 h-4 text-gray-500" />
    }
  }

  const formatTime = (date: Date) => {
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const seconds = Math.floor(diff / 1000)
    const minutes = Math.floor(seconds / 60)
    const hours = Math.floor(minutes / 60)

    if (seconds < 60) return `${seconds}s ago`
    if (minutes < 60) return `${minutes}m ago`
    if (hours < 24) return `${hours}h ago`
    return date.toLocaleDateString()
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-end" onClick={onClose}>
      <div className="w-full bg-white rounded-t-2xl shadow-2xl max-h-[80vh] flex flex-col" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Clock className="w-6 h-6 text-blue-500" />
            <h2 className="text-xl font-bold text-gray-800">AIM-OS Activity Timeline</h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            ✕
          </button>
        </div>

        {/* Timeline */}
        <div className="flex-1 overflow-y-auto p-6">
          {loading ? (
            <div className="text-center py-12 text-gray-500">
              Loading timeline...
            </div>
          ) : entries.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              No timeline entries yet
            </div>
          ) : (
            <div className="relative">
              {/* Timeline line */}
              <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gray-200"></div>

              {/* Entries */}
              <div className="space-y-6">
                {entries.map((entry, index) => (
                  <div key={entry.id} className="relative flex items-start gap-4">
                    {/* Icon */}
                    <div className="relative z-10 flex items-center justify-center w-8 h-8 rounded-full bg-white border-2 border-gray-200">
                      {getIcon(entry.type)}
                    </div>

                    {/* Content */}
                    <div className="flex-1 pt-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-medium text-gray-800">
                          {entry.content}
                        </span>
                        <span className="text-xs text-gray-400">
                          {formatTime(entry.timestamp)}
                        </span>
                      </div>
                      {entry.context && (
                        <div className="text-xs text-gray-500 mt-1">
                          {JSON.stringify(entry.context, null, 2)}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
