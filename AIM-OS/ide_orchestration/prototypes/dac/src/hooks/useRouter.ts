// Router Hook - Data fetching and state management for Router panel
// Provides Router tool selection data, telemetry, and actions

import { useState, useEffect, useCallback } from 'react'

export interface ToolProposal {
  tool_name: string
  rationale: string
  draft_arguments: Record<string, any>
  confidence: number
  probability?: number
  context_fit?: number
  success_rate?: number
  precondition_satisfied?: boolean
  expected_info_gain?: number
  parallelizable?: boolean
}

export interface RouterTelemetry {
  avg_latency: number
  latency_trend: 'up' | 'down' | 'stable'
  success_rate: number
  success_trend: 'up' | 'down' | 'stable'
  avg_cost: number
  cost_trend: 'up' | 'down' | 'stable'
  tools: Array<{
    name: string
    latency: number
    success_rate: number
    cost: number
    call_count: number
  }>
}

export function useRouter() {
  const [tools, setTools] = useState<ToolProposal[]>([])
  const [suggestions, setSuggestions] = useState<ToolProposal[]>([])
  const [telemetry, setTelemetry] = useState<RouterTelemetry | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchTools = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Fetch Router tool proposals
      const response = await fetch('/api/router/tools')
      if (!response.ok) {
        throw new Error('Failed to fetch Router tools')
      }
      
      const data = await response.json()
      setTools(data.tools || [])
      setSuggestions(data.suggestions || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch Router tools')
    } finally {
      setLoading(false)
    }
  }, [])

  const fetchTelemetry = useCallback(async () => {
    try {
      const response = await fetch('/api/router/telemetry')
      if (!response.ok) {
        throw new Error('Failed to fetch Router telemetry')
      }
      
      const data = await response.json()
      setTelemetry(data)
    } catch (err) {
      console.error('Failed to fetch Router telemetry:', err)
    }
  }, [])

  useEffect(() => {
    fetchTools()
    fetchTelemetry()
    
    // Refresh every 5 seconds
    const interval = setInterval(() => {
      fetchTools()
      fetchTelemetry()
    }, 5000)
    
    return () => clearInterval(interval)
  }, [fetchTools, fetchTelemetry])

  const executeTool = useCallback(async (toolName: string, args: Record<string, any>) => {
    try {
      const response = await fetch('/api/router/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tool: toolName, args })
      })
      
      if (!response.ok) {
        throw new Error('Failed to execute tool')
      }
      
      const result = await response.json()
      return result
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : 'Failed to execute tool')
    }
  }, [])

  return {
    tools,
    suggestions,
    telemetry,
    loading,
    error,
    executeTool,
    refresh: fetchTools
  }
}

