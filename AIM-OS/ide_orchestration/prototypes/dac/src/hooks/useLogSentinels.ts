// Log-Sentinels Hook - Data fetching and state management for Log-Sentinels panels
// Provides Scout reports, Forensics reports, and telemetry

import { useState, useEffect, useCallback } from 'react'

export interface ScoutReport {
  window_id: string
  summary: string
  confidence: number
  severity: 'low' | 'medium' | 'high'
  tags: string[]
  suggested_tools: string[]
  timestamp: string
}

export interface ForensicsReport extends ScoutReport {
  root_cause?: string
  fix_suggestion?: {
    patch?: string
    steps?: string[]
  }
  evidence: string[]
  gate?: {
    passed: boolean
    reasons?: string[]
  }
}

export interface LogSentinelsTelemetry {
  scout_calls: number
  forensics_calls: number
  escalations: number
  tool_suggestions: number
  timeline: Array<{
    timestamp: string
    scout_calls: number
    forensics_calls: number
    escalations: number
  }>
}

// Mock data for development (until API endpoints are implemented)
const MOCK_SCOUTS: ScoutReport[] = [
  {
    window_id: 'scout-001',
    summary: 'Detected unusual error pattern in authentication flow',
    confidence: 0.85,
    severity: 'medium',
    tags: ['authentication', 'error-pattern'],
    suggested_tools: ['analyze_logs', 'check_auth_config'],
    timestamp: new Date().toISOString()
  }
]

const MOCK_FORENSICS: ForensicsReport[] = [
  {
    window_id: 'forensic-001',
    summary: 'High severity: Memory leak detected in event handler',
    confidence: 0.92,
    severity: 'high',
    tags: ['memory-leak', 'event-handler', 'performance'],
    suggested_tools: ['fix_memory_leak', 'profile_memory'],
    timestamp: new Date(Date.now() - 3600000).toISOString(),
    root_cause: 'Event listener not properly removed when component unmounts, causing memory accumulation over time.',
    fix_suggestion: {
      patch: `useEffect(() => {
  const handler = () => { /* ... */ }
  window.addEventListener('resize', handler)
  return () => window.removeEventListener('resize', handler) // Cleanup
}, [])`,
      steps: [
        'Add cleanup function to useEffect',
        'Remove event listener in cleanup',
        'Test memory usage after fix'
      ]
    },
    evidence: ['memory-usage-graph', 'event-listener-count', 'component-lifecycle-log'],
    gate: {
      passed: false,
      reasons: ['Memory usage exceeds threshold', 'No cleanup function detected']
    }
  },
  {
    window_id: 'forensic-002',
    summary: 'Medium severity: Slow query performance detected',
    confidence: 0.78,
    severity: 'medium',
    tags: ['performance', 'database', 'query'],
    suggested_tools: ['optimize_query', 'add_index'],
    timestamp: new Date(Date.now() - 7200000).toISOString(),
    root_cause: 'Database query missing index on frequently filtered column.',
    fix_suggestion: {
      steps: [
        'Add index to users.email column',
        'Review query execution plan',
        'Monitor performance after index creation'
      ]
    },
    evidence: ['query-execution-time', 'missing-index-warning'],
    gate: {
      passed: true
    }
  }
]

const MOCK_TELEMETRY: LogSentinelsTelemetry = {
  scout_calls: 42,
  forensics_calls: 8,
  escalations: 2,
  tool_suggestions: 15,
  timeline: [
    {
      timestamp: new Date(Date.now() - 3600000).toISOString(),
      scout_calls: 10,
      forensics_calls: 2,
      escalations: 0
    },
    {
      timestamp: new Date(Date.now() - 1800000).toISOString(),
      scout_calls: 15,
      forensics_calls: 3,
      escalations: 1
    },
    {
      timestamp: new Date().toISOString(),
      scout_calls: 17,
      forensics_calls: 3,
      escalations: 1
    }
  ]
}

export function useLogSentinels() {
  const [scouts, setScouts] = useState<ScoutReport[]>([])
  const [forensics, setForensics] = useState<ForensicsReport[]>([])
  const [telemetry, setTelemetry] = useState<LogSentinelsTelemetry | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchScouts = useCallback(async () => {
    try {
      const response = await fetch('/api/log-sentinels/scouts')
      if (!response.ok) {
        throw new Error('Failed to fetch Scout reports')
      }
      
      const data = await response.json()
      setScouts(data.reports || [])
    } catch (err) {
      // Use mock data if API is not available
      console.warn('API not available, using mock data for scouts:', err)
      setScouts(MOCK_SCOUTS)
    }
  }, [])

  const fetchForensics = useCallback(async () => {
    try {
      const response = await fetch('/api/log-sentinels/forensics')
      if (!response.ok) {
        throw new Error('Failed to fetch Forensics reports')
      }
      
      const data = await response.json()
      setForensics(data.reports || [])
    } catch (err) {
      // Use mock data if API is not available
      console.warn('API not available, using mock data for forensics:', err)
      setForensics(MOCK_FORENSICS)
    }
  }, [])

  const fetchTelemetry = useCallback(async () => {
    try {
      const response = await fetch('/api/log-sentinels/telemetry')
      if (!response.ok) {
        throw new Error('Failed to fetch Log-Sentinels telemetry')
      }
      
      const data = await response.json()
      setTelemetry(data)
    } catch (err) {
      // Use mock data if API is not available
      console.warn('API not available, using mock data for telemetry:', err)
      setTelemetry(MOCK_TELEMETRY)
    }
  }, [])

  useEffect(() => {
    const loadData = async () => {
      setLoading(true)
      setError(null)
      try {
        await Promise.all([
          fetchScouts(),
          fetchForensics(),
          fetchTelemetry()
        ])
      } catch (err) {
        // Errors are handled in individual fetch functions with mock data fallback
        console.warn('Error loading Log-Sentinels data:', err)
      } finally {
        setLoading(false)
      }
    }
    
    loadData()
    
    // Set up SSE connection for real-time updates (only if API is available)
    let eventSource: EventSource | null = null
    try {
      eventSource = new EventSource('/api/log-sentinels/stream')
      
      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          
          if (data.type === 'scout') {
            setScouts(prev => [data.payload, ...prev].slice(0, 50))
          } else if (data.type === 'forensics') {
            setForensics(prev => [data.payload, ...prev].slice(0, 50))
          }
        } catch (err) {
          console.warn('Failed to parse SSE message:', err)
        }
      }
      
      eventSource.onerror = () => {
        // SSE connection failed (likely API not available), silently fail
        if (eventSource) {
          eventSource.close()
          eventSource = null
        }
      }
    } catch (err) {
      // EventSource not supported or API not available
      console.warn('SSE not available, using polling mode:', err)
    }
    
    // Refresh telemetry every 10 seconds
    const interval = setInterval(fetchTelemetry, 10000)
    
    return () => {
      if (eventSource) {
        eventSource.close()
      }
      clearInterval(interval)
    }
  }, [fetchScouts, fetchForensics, fetchTelemetry])

  const runTool = useCallback(async (toolName: string) => {
    try {
      const response = await fetch('/api/log-sentinels/run-tool', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tool: toolName })
      })
      
      if (!response.ok) {
        throw new Error('Failed to run tool')
      }
      
      return await response.json()
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : 'Failed to run tool')
    }
  }, [])

  return {
    scouts,
    forensics,
    telemetry,
    loading,
    error,
    runTool,
    refresh: () => {
      fetchScouts()
      fetchForensics()
      fetchTelemetry()
    }
  }
}

