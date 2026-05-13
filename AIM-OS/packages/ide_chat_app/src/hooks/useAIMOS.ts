// Comprehensive AIM-OS Hooks
// V2 Enhancement - Week 1 Foundation
// Provides hooks for all 8 AIM-OS systems

import { useState, useEffect, useCallback } from 'react'
import { getMCPAPI } from '../services/mcpApi'
import { getMCPToolsService } from '../services/mcpToolsService'
import { aimosService } from '../services/AIMOSService'
import { daemonService, DaemonHealth, DaemonStatus } from '../services/daemonService'

// ============================================================================
// Core AIM-OS Hook - Comprehensive Integration
// ============================================================================

export interface AIMOSState {
  cmc: {
    data: any
    loading: boolean
    error: Error | null
  }
  hhni: {
    data: any
    loading: boolean
    error: Error | null
  }
  vif: {
    data: any
    loading: boolean
    error: Error | null
  }
  seg: {
    data: any
    loading: boolean
    error: Error | null
  }
  apoe: {
    data: any
    loading: boolean
    error: Error | null
  }
  tcs: {
    data: any
    loading: boolean
    error: Error | null
  }
  cas: {
    data: any
    loading: boolean
    error: Error | null
  }
  mcpTools: {
    data: any
    loading: boolean
    error: Error | null
  }
  daemon: {
    health: DaemonHealth | null
    status: DaemonStatus | null
    loading: boolean
    error: Error | null
  }
  loading: boolean
  error: Error | null
}

/**
 * Comprehensive AIM-OS hook - provides access to all 8 AIM-OS systems
 */
export function useAIMOS(): AIMOSState & {
  storeMemory: (content: string, tags: string[]) => Promise<any>
  retrieveMemory: (query: string, limit?: number) => Promise<any[]>
  getMemoryStats: () => Promise<any>
  createPlan: (goal: string, priority?: string) => Promise<any>
  trackConfidence: (task: string, confidence: number, reasoning?: string) => Promise<boolean>
  synthesizeKnowledge: (topics: string[]) => Promise<any>
  getConsciousnessMetrics: () => Promise<any>
  getTimelineEntries: (limit?: number) => Promise<any[]>
  queryGoalTimeline: (status?: string, limit?: number) => Promise<any[]>
  checkDaemonHealth: () => Promise<DaemonHealth | null>
  getDaemonStatus: () => Promise<DaemonStatus | null>
} {
  const cmc = useCMC()
  const hhni = useHHNI()
  const vif = useVIF()
  const seg = useSEG()
  const apoe = useAPOE()
  const tcs = useTCS()
  const cas = useCAS()
  const mcpTools = useMCPTools()
  const daemon = useDaemon()

  const loading = cmc.loading || hhni.loading || vif.loading || seg.loading || 
                  apoe.loading || tcs.loading || cas.loading || mcpTools.loading || daemon.loading
  const error = cmc.error || hhni.error || vif.error || seg.error || 
                apoe.error || tcs.error || cas.error || mcpTools.error || daemon.error

  return {
    cmc,
    hhni,
    vif,
    seg,
    apoe,
    tcs,
    cas,
    mcpTools,
    daemon,
    loading,
    error,
    storeMemory: cmc.storeMemory,
    retrieveMemory: cmc.retrieveMemory,
    getMemoryStats: cmc.getMemoryStats,
    createPlan: apoe.createPlan,
    trackConfidence: vif.trackConfidence,
    synthesizeKnowledge: seg.synthesizeKnowledge,
    getConsciousnessMetrics: cas.getConsciousnessMetrics,
    getTimelineEntries: tcs.getTimelineEntries,
    queryGoalTimeline: tcs.queryGoalTimeline,
    checkDaemonHealth: daemon.checkHealth,
    getDaemonStatus: daemon.getStatus
  }
}

// ============================================================================
// Individual System Hooks
// ============================================================================

/**
 * CMC (Context Memory Core) Hook
 */
export function useCMC() {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)
  const mcpApi = getMCPAPI()

  const storeMemory = useCallback(async (content: string, tags: string[]): Promise<any> => {
    setLoading(true)
    setError(null)
    try {
      const result = await mcpApi.storeMemory(content, tags)
      return result
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err))
      setError(error)
      throw error
    } finally {
      setLoading(false)
    }
  }, [mcpApi])

  const retrieveMemory = useCallback(async (query: string, limit: number = 10): Promise<any[]> => {
    setLoading(true)
    setError(null)
    try {
      const memories = await mcpApi.retrieveMemory(query, limit)
      setData(memories)
      return memories
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err))
      setError(error)
      return []
    } finally {
      setLoading(false)
    }
  }, [mcpApi])

  const getMemoryStats = useCallback(async (): Promise<any> => {
    setLoading(true)
    setError(null)
    try {
      const stats = await mcpApi.getMemoryStats()
      setData(stats)
      return stats
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err))
      setError(error)
      return {}
    } finally {
      setLoading(false)
    }
  }, [mcpApi])

  return {
    data,
    loading,
    error,
    storeMemory,
    retrieveMemory,
    getMemoryStats
  }
}

/**
 * HHNI (Hierarchical Hypergraph Neural Index) Hook
 */
export function useHHNI() {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)
  const mcpApi = getMCPAPI()

  const search = useCallback(async (query: string, limit: number = 10): Promise<any[]> => {
    setLoading(true)
    setError(null)
    try {
      // HHNI search via retrieveMemory (which uses HHNI internally)
      const results = await mcpApi.retrieveMemory(query, limit)
      setData(results)
      return results
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err))
      setError(error)
      return []
    } finally {
      setLoading(false)
    }
  }, [mcpApi])

  return {
    data,
    loading,
    error,
    search
  }
}

/**
 * VIF (Verifiable Intelligence Framework) Hook
 */
export function useVIF() {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)
  const mcpApi = getMCPAPI()

  const trackConfidence = useCallback(async (
    task: string,
    confidence: number,
    reasoning?: string
  ): Promise<boolean> => {
    setLoading(true)
    setError(null)
    try {
      const result = await mcpApi.trackConfidence(task, confidence, reasoning)
      return result
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err))
      setError(error)
      return false
    } finally {
      setLoading(false)
    }
  }, [mcpApi])

  return {
    data,
    loading,
    error,
    trackConfidence
  }
}

/**
 * SEG (Synthesis & Evidence Graph) Hook
 */
export function useSEG() {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)
  const mcpApi = getMCPAPI()

  const synthesizeKnowledge = useCallback(async (topics: string[]): Promise<any> => {
    setLoading(true)
    setError(null)
    try {
      const result = await mcpApi.synthesizeKnowledge(topics)
      setData(result)
      return result
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err))
      setError(error)
      return {}
    } finally {
      setLoading(false)
    }
  }, [mcpApi])

  return {
    data,
    loading,
    error,
    synthesizeKnowledge
  }
}

/**
 * APOE (AI-Powered Orchestration Engine) Hook
 */
export function useAPOE() {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)
  const mcpApi = getMCPAPI()

  const createPlan = useCallback(async (
    goal: string,
    priority: string = 'medium'
  ): Promise<any> => {
    setLoading(true)
    setError(null)
    try {
      const result = await mcpApi.createPlan(goal, priority)
      setData(result)
      return result
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err))
      setError(error)
      return {}
    } finally {
      setLoading(false)
    }
  }, [mcpApi])

  return {
    data,
    loading,
    error,
    createPlan
  }
}

/**
 * TCS (Timeline Context System) Hook
 */
export function useTCS() {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)
  const mcpApi = getMCPAPI()

  const getTimelineEntries = useCallback(async (limit: number = 10): Promise<any[]> => {
    setLoading(true)
    setError(null)
    try {
      const response = await mcpApi.executeTool('get_timeline_entries', { limit })
      if (response.success && response.result) {
        const entries = Array.isArray(response.result) ? response.result : 
                       (response.result.entries || [])
        setData(entries)
        return entries
      }
      return []
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err))
      setError(error)
      return []
    } finally {
      setLoading(false)
    }
  }, [mcpApi])

  const queryGoalTimeline = useCallback(async (
    status: string = 'in_progress',
    limit: number = 10
  ): Promise<any[]> => {
    setLoading(true)
    setError(null)
    try {
      const response = await mcpApi.executeTool('query_goal_timeline', { status, limit })
      if (response.success && response.result) {
        const goals = response.result.goals || response.result || []
        setData(goals)
        return goals
      }
      return []
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err))
      setError(error)
      return []
    } finally {
      setLoading(false)
    }
  }, [mcpApi])

  const addTimelineEntry = useCallback(async (
    promptId: string,
    userInput: string,
    contextState?: any
  ): Promise<boolean> => {
    setLoading(true)
    setError(null)
    try {
      const response = await mcpApi.executeTool('add_timeline_entry', {
        prompt_id: promptId,
        user_input: userInput,
        context_state: contextState || {}
      })
      return response.success
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err))
      setError(error)
      return false
    } finally {
      setLoading(false)
    }
  }, [mcpApi])

  return {
    data,
    loading,
    error,
    getTimelineEntries,
    queryGoalTimeline,
    addTimelineEntry
  }
}

/**
 * CAS (Consciousness Analysis System) Hook
 */
export function useCAS() {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)
  const mcpApi = getMCPAPI()

  const getConsciousnessMetrics = useCallback(async (): Promise<any> => {
    setLoading(true)
    setError(null)
    try {
      const response = await mcpApi.executeTool('get_consciousness_metrics', {})
      if (response.success && response.result) {
        setData(response.result)
        return response.result
      }
      return {}
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err))
      setError(error)
      return {}
    } finally {
      setLoading(false)
    }
  }, [mcpApi])

  return {
    data,
    loading,
    error,
    getConsciousnessMetrics
  }
}

/**
 * MCP Tools Hook
 */
export function useMCPTools() {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)
  const mcpToolsService = getMCPToolsService()

  useEffect(() => {
    const loadTools = async () => {
      setLoading(true)
      try {
        const tools = mcpToolsService.getAllTools()
        setData(tools)
      } catch (err) {
        const error = err instanceof Error ? err : new Error(String(err))
        setError(error)
      } finally {
        setLoading(false)
      }
    }
    loadTools()
  }, [mcpToolsService])

  const executeTool = useCallback(async (toolName: string, args: any = {}): Promise<any> => {
    setLoading(true)
    setError(null)
    try {
      const result = await mcpToolsService.executeTool(toolName, args)
      return result
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err))
      setError(error)
      throw error
    } finally {
      setLoading(false)
    }
  }, [mcpToolsService])

  const getToolsByCategory = useCallback((category: string) => {
    return mcpToolsService.getToolsByCategory(category as any)
  }, [mcpToolsService])

  const searchTools = useCallback((query: string) => {
    return mcpToolsService.searchTools(query)
  }, [mcpToolsService])

  return {
    data,
    loading,
    error,
    executeTool,
    getToolsByCategory,
    searchTools
  }
}

/**
 * Daemon Hook - OBJ-08 Integration
 */
export function useDaemon() {
  const [health, setHealth] = useState<DaemonHealth | null>(null)
  const [status, setStatus] = useState<DaemonStatus | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  const checkHealth = useCallback(async (): Promise<DaemonHealth | null> => {
    setLoading(true)
    setError(null)
    try {
      const healthData = await daemonService.checkHealth()
      setHealth(healthData)
      return healthData
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err))
      setError(error)
      return null
    } finally {
      setLoading(false)
    }
  }, [])

  const getStatus = useCallback(async (): Promise<DaemonStatus | null> => {
    setLoading(true)
    setError(null)
    try {
      const statusData = await daemonService.getStatus()
      setStatus(statusData)
      return statusData
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err))
      setError(error)
      return null
    } finally {
      setLoading(false)
    }
  }, [])

  // Auto-refresh health and status
  useEffect(() => {
    const refreshData = async () => {
      await checkHealth()
      await getStatus()
    }
    refreshData()
    const interval = setInterval(refreshData, 10000) // Refresh every 10 seconds
    return () => clearInterval(interval)
  }, [checkHealth, getStatus])

  return {
    health,
    status,
    loading,
    error,
    checkHealth,
    getStatus,
    isConnected: health?.status === 'healthy' && health?.daemon_status === 'running'
  }
}

// ============================================================================
// Convenience Hooks
// ============================================================================

/**
 * Consciousness Hook - Convenience hook for consciousness metrics
 */
export function useConsciousness() {
  const cas = useCAS()
  const [metrics, setMetrics] = useState<any>(null)

  useEffect(() => {
    const fetchMetrics = async () => {
      const result = await cas.getConsciousnessMetrics()
      setMetrics(result)
    }
    fetchMetrics()
    const interval = setInterval(fetchMetrics, 5000) // Refresh every 5 seconds
    return () => clearInterval(interval)
  }, [cas])

  const health = metrics?.health || 0
  const confidence = metrics?.confidence || 0

  return {
    metrics,
    health,
    confidence,
    loading: cas.loading,
    error: cas.error
  }
}

/**
 * Timeline Hook - Convenience hook for timeline data
 */
export function useTimeline(limit: number = 10) {
  const tcs = useTCS()
  const [entries, setEntries] = useState<any[]>([])

  useEffect(() => {
    const fetchEntries = async () => {
      const result = await tcs.getTimelineEntries(limit)
      setEntries(result)
    }
    fetchEntries()
    const interval = setInterval(fetchEntries, 5000) // Refresh every 5 seconds
    return () => clearInterval(interval)
  }, [tcs, limit])

  return {
    entries,
    loading: tcs.loading,
    error: tcs.error,
    refresh: () => tcs.getTimelineEntries(limit)
  }
}

/**
 * Goals Hook - Convenience hook for goal timeline
 */
export function useGoals(status: string = 'in_progress', limit: number = 10) {
  const tcs = useTCS()
  const [goals, setGoals] = useState<any[]>([])

  useEffect(() => {
    const fetchGoals = async () => {
      const result = await tcs.queryGoalTimeline(status, limit)
      setGoals(result)
    }
    fetchGoals()
    const interval = setInterval(fetchGoals, 5000) // Refresh every 5 seconds
    return () => clearInterval(interval)
  }, [tcs, status, limit])

  return {
    goals,
    loading: tcs.loading,
    error: tcs.error,
    refresh: () => tcs.queryGoalTimeline(status, limit)
  }
}

/**
 * Memory Hook - Convenience hook for memory operations
 */
export function useMemory() {
  const cmc = useCMC()

  return {
    storeMemory: cmc.storeMemory,
    retrieveMemory: cmc.retrieveMemory,
    getMemoryStats: cmc.getMemoryStats,
    loading: cmc.loading,
    error: cmc.error
  }
}

/**
 * Evidence Hook - Convenience hook for evidence trails
 */
export function useEvidence() {
  const seg = useSEG()
  const cmc = useCMC()

  const getEvidenceTrails = useCallback(async (query: string, limit: number = 10) => {
    // Evidence trails come from memory retrieval
    return await cmc.retrieveMemory(query, limit)
  }, [cmc])

  return {
    getEvidenceTrails,
    synthesizeKnowledge: seg.synthesizeKnowledge,
    loading: seg.loading || cmc.loading,
    error: seg.error || cmc.error
  }
}

/**
 * Confidence Hook - Convenience hook for confidence tracking
 */
export function useConfidence() {
  const vif = useVIF()

  return {
    trackConfidence: vif.trackConfidence,
    loading: vif.loading,
    error: vif.error
  }
}
