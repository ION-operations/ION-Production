// Unified AIM-OS Hook - Real Integration with Graceful Fallback
// Pattern: Real AIM-OS first, mock fallback
import { useState, useCallback, useEffect } from 'react'
import { CMCAtom, CMCStats, HHNISearchResult, VIFWitness, VIFConfidence, APOEPlan, SEGContradiction, TimelineEntry, Agent } from '@/types'
import { mockCMCAtoms, mockCMCStats } from '@/mockData/cmc'
import { mockVIFWitnesses, mockVIFConfidences } from '@/mockData/vif'
import { mockTimelineEntries } from '@/mockData/timeline'
import { mockAgents } from '@/mockData/agents'
import { mockSEGContradictions } from '@/mockData/seg'
import { aimosService } from '@/services/aimosService'

interface UseAIMOSOptions {
  useRealAIMOS?: boolean // Feature flag to enable/disable real AIM-OS
  fallbackToMock?: boolean // Whether to fallback to mock when real fails
}

interface UseAIMOSReturn {
  // Connection status
  isConnected: boolean
  isLoading: boolean
  error: string | null

  // CMC
  cmc: {
    atoms: CMCAtom[]
    stats: CMCStats
    storeAtom: (content: string, tags?: string[], confidence?: number) => Promise<CMCAtom>
    retrieveAtoms: (query: string) => Promise<CMCAtom[]>
    getStats: () => CMCStats
  }

  // HHNI
  hhni: {
    search: (query: string) => Promise<HHNISearchResult>
    retrieve: (atomIds: string[]) => Promise<CMCAtom[]>
  }

  // VIF
  vif: {
    witnesses: VIFWitness[]
    confidences: VIFConfidence[]
    trackConfidence: (task: string, confidence: number, evidence?: string[], reasoning?: string) => Promise<VIFWitness>
    getWitnesses: (taskId?: string) => VIFWitness[]
    getConfidence: (task: string) => VIFConfidence | null
  }

  // APOE
  apoe: {
    plans: APOEPlan[]
    tasks: any[]
    createPlan: (goal: string) => Promise<APOEPlan>
    executePlan: (planId: string) => Promise<void>
  }

  // SEG
  seg: {
    contradictions: SEGContradiction[]
    detectContradictions: (content: string) => SEGContradiction[]
    synthesizeKnowledge: (topics: string[]) => Promise<void>
  }

  // TCS
  tcs: {
    entries: TimelineEntry[]
    addEntry: (entry: Omit<TimelineEntry, 'id' | 'timestamp'>) => Promise<TimelineEntry>
    getSummary: (limit?: number) => TimelineEntry[]
    getEntries: (startTime?: string, endTime?: string) => TimelineEntry[]
  }

  // Agents
  agents: {
    agents: Agent[]
    getActiveAgents: () => Agent[]
    getAgent: (agentId: string) => Agent | undefined
  }
}

export const useAIMOS = (options: UseAIMOSOptions = {}): UseAIMOSReturn => {
  const { useRealAIMOS = true, fallbackToMock = true } = options

  const [isConnected, setIsConnected] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // State for all systems
  const [atoms, setAtoms] = useState<CMCAtom[]>(mockCMCAtoms)
  const [stats, setStats] = useState<CMCStats>(mockCMCStats)
  const [witnesses, setWitnesses] = useState<VIFWitness[]>(mockVIFWitnesses)
  const [confidences, setConfidences] = useState<VIFConfidence[]>(mockVIFConfidences)
  const [timelineEntries, setTimelineEntries] = useState<TimelineEntry[]>(mockTimelineEntries)
  const [agents, setAgents] = useState<Agent[]>(mockAgents)
  const [contradictions, setContradictions] = useState<SEGContradiction[]>(mockSEGContradictions)
  const [plans, setPlans] = useState<APOEPlan[]>([])

  // Check connection on mount
  useEffect(() => {
    const checkConnection = async () => {
      if (!useRealAIMOS) {
        setIsConnected(false)
        setIsLoading(false)
        return
      }

      try {
        setIsLoading(true)
        const memoryStats = await aimosService.getMemoryStats()
        setIsConnected(Object.keys(memoryStats).length > 0)
        setError(null)

        // Load initial data from real AIM-OS
        if (isConnected) {
          const timeline = await aimosService.getTimelineSummary(10)
          setTimelineEntries(timeline.map((entry: any) => ({
            id: entry.prompt_id || `entry_${Date.now()}`,
            timestamp: entry.timestamp || new Date().toISOString(),
            type: entry.type || 'system_event',
            content: entry.user_input || entry.content || '',
            agentId: entry.agent_id,
            confidence: entry.confidence,
          })))
        }
      } catch (err) {
        setIsConnected(false)
        if (fallbackToMock) {
          setError(null) // Silent fallback
        } else {
          setError(err instanceof Error ? err.message : 'Failed to connect to AIM-OS')
        }
      } finally {
        setIsLoading(false)
      }
    }

    checkConnection()
  }, [useRealAIMOS, fallbackToMock])

  // CMC Operations
  const storeAtom = useCallback(
    async (content: string, tags: string[] = [], confidence: number = 0.8): Promise<CMCAtom> => {
      if (useRealAIMOS && isConnected) {
        try {
          const result = await aimosService.storeMemory(content, { tags: tags.join(',') })
          if (result.success && result.atom_id) {
            const newAtom: CMCAtom = {
              id: result.atom_id,
              content,
              timestamp: new Date().toISOString(),
              tags,
              confidence,
            }
            setAtoms((prev) => [newAtom, ...prev])
            return newAtom
          }
        } catch (err) {
          if (!fallbackToMock) throw err
        }
      }

      // Fallback to mock
      const newAtom: CMCAtom = {
        id: `atom_${Date.now()}`,
        content,
        timestamp: new Date().toISOString(),
        tags,
        confidence,
      }
      setAtoms((prev) => [newAtom, ...prev])
      return newAtom
    },
    [useRealAIMOS, isConnected, fallbackToMock]
  )

  const retrieveAtoms = useCallback(
    async (query: string): Promise<CMCAtom[]> => {
      if (useRealAIMOS && isConnected) {
        try {
          const results = await aimosService.retrieveMemory(query, 10)
          if (results.length > 0) {
            return results.map((result: any) => ({
              id: result.atom_id || `atom_${Date.now()}`,
              content: result.content || '',
              timestamp: result.created_at || new Date().toISOString(),
              tags: result.tags ? Object.keys(result.tags) : [],
              confidence: 0.8,
            }))
          }
        } catch (err) {
          if (!fallbackToMock) return []
        }
      }

      // Fallback to mock
      return atoms.filter(
        (atom) =>
          atom.content.toLowerCase().includes(query.toLowerCase()) ||
          atom.tags.some((tag) => tag.toLowerCase().includes(query.toLowerCase()))
      )
    },
    [useRealAIMOS, isConnected, fallbackToMock, atoms]
  )

  const getStats = useCallback((): CMCStats => {
    return stats
  }, [stats])

  // HHNI Operations
  const hhniSearch = useCallback(
    async (query: string): Promise<HHNISearchResult> => {
      if (useRealAIMOS && isConnected) {
        try {
          const results = await aimosService.retrieveMemory(query, 10)
          return {
            atomIds: results.map((r: any) => r.atom_id || `atom_${Date.now()}`),
            relevance: results.map(() => Math.random() * 0.5 + 0.5), // Mock relevance
            query,
          }
        } catch (err) {
          if (!fallbackToMock) {
            return { atomIds: [], relevance: [], query }
          }
        }
      }

      // Fallback to mock
      const results = atoms
        .map((atom, index) => ({
          atomId: atom.id,
          relevance: Math.random() * 0.5 + 0.5,
        }))
        .sort((a, b) => b.relevance - a.relevance)
        .slice(0, 10)

      return {
        atomIds: results.map((r) => r.atomId),
        relevance: results.map((r) => r.relevance),
        query,
      }
    },
    [useRealAIMOS, isConnected, fallbackToMock, atoms]
  )

  const hhniRetrieve = useCallback(
    (atomIds: string[]): Promise<CMCAtom[]> => {
      return Promise.resolve(atoms.filter((atom) => atomIds.includes(atom.id)))
    },
    [atoms]
  )

  // VIF Operations
  const trackConfidence = useCallback(
    async (task: string, confidence: number, evidence: string[] = [], reasoning: string = ''): Promise<VIFWitness> => {
      if (useRealAIMOS && isConnected) {
        try {
          const result = await aimosService.trackConfidence(task, confidence, evidence, reasoning)
          if (result.success) {
            const newWitness: VIFWitness = {
              id: `witness_${Date.now()}`,
              task,
              confidence,
              evidence,
              timestamp: new Date().toISOString(),
            }
            setWitnesses((prev) => [newWitness, ...prev])
            return newWitness
          }
        } catch (err) {
          if (!fallbackToMock) throw err
        }
      }

      // Fallback to mock
      const newWitness: VIFWitness = {
        id: `witness_${Date.now()}`,
        task,
        confidence,
        evidence,
        timestamp: new Date().toISOString(),
      }
      setWitnesses((prev) => [newWitness, ...prev])
      return newWitness
    },
    [useRealAIMOS, isConnected, fallbackToMock]
  )

  const getWitnesses = useCallback(
    (taskId?: string): VIFWitness[] => {
      if (taskId) {
        return witnesses.filter((w) => w.task.includes(taskId))
      }
      return witnesses
    },
    [witnesses]
  )

  const getConfidence = useCallback(
    (task: string): VIFConfidence | null => {
      return confidences.find((c) => c.task === task) || null
    },
    [confidences]
  )

  // APOE Operations
  const createPlan = useCallback(
    async (goal: string): Promise<APOEPlan> => {
      if (useRealAIMOS && isConnected) {
        try {
          const result = await aimosService.createPlan(goal)
          if (result.success && result.result) {
            const plan: APOEPlan = {
              id: result.result.plan_id || `plan_${Date.now()}`,
              goal,
              tasks: result.result.steps || [],
              status: 'planned',
            }
            setPlans((prev) => [plan, ...prev])
            return plan
          }
        } catch (err) {
          if (!fallbackToMock) throw err
        }
      }

      // Fallback to mock
      const plan: APOEPlan = {
        id: `plan_${Date.now()}`,
        goal,
        tasks: [],
        status: 'planned',
      }
      setPlans((prev) => [plan, ...prev])
      return plan
    },
    [useRealAIMOS, isConnected, fallbackToMock]
  )

  const executePlan = useCallback(
    async (planId: string): Promise<void> => {
      console.log(`Executing plan: ${planId}`)
      // Real implementation would call APOE API
    },
    []
  )

  // SEG Operations
  const detectContradictions = useCallback(
    (content: string): SEGContradiction[] => {
      return contradictions.filter(
        (c) =>
          content.toLowerCase().includes(c.source.toLowerCase()) ||
          content.toLowerCase().includes(c.target.toLowerCase())
      )
    },
    [contradictions]
  )

  const synthesizeKnowledge = useCallback(
    async (topics: string[]): Promise<void> => {
      if (useRealAIMOS && isConnected) {
        try {
          await aimosService.synthesizeKnowledge(topics)
        } catch (err) {
          if (!fallbackToMock) throw err
        }
      }
      console.log(`Synthesizing knowledge for topics: ${topics.join(', ')}`)
    },
    [useRealAIMOS, isConnected, fallbackToMock]
  )

  // TCS Operations
  const addTimelineEntry = useCallback(
    async (entry: Omit<TimelineEntry, 'id' | 'timestamp'>): Promise<TimelineEntry> => {
      if (useRealAIMOS && isConnected) {
        try {
          const promptId = `prompt_${Date.now()}`
          await aimosService.addTimelineEntry(promptId, entry.content || '', {
            type: entry.type,
            agentId: entry.agentId,
            confidence: entry.confidence,
          })
          const newEntry: TimelineEntry = {
            ...entry,
            id: promptId,
            timestamp: new Date().toISOString(),
          }
          setTimelineEntries((prev) => [newEntry, ...prev])
          return newEntry
        } catch (err) {
          if (!fallbackToMock) throw err
        }
      }

      // Fallback to mock
      const newEntry: TimelineEntry = {
        ...entry,
        id: `entry_${Date.now()}`,
        timestamp: new Date().toISOString(),
      }
      setTimelineEntries((prev) => [newEntry, ...prev])
      return newEntry
    },
    [useRealAIMOS, isConnected, fallbackToMock]
  )

  const getSummary = useCallback(
    (limit: number = 10): TimelineEntry[] => {
      return timelineEntries.slice(0, limit)
    },
    [timelineEntries]
  )

  const getEntries = useCallback(
    (startTime?: string, endTime?: string): TimelineEntry[] => {
      if (startTime && endTime) {
        return timelineEntries.filter((e) => e.timestamp >= startTime && e.timestamp <= endTime)
      }
      return timelineEntries
    },
    [timelineEntries]
  )

  // Agent Operations
  const getActiveAgents = useCallback((): Agent[] => {
    return agents.filter((a) => a.status === 'active')
  }, [agents])

  const getAgent = useCallback(
    (agentId: string): Agent | undefined => {
      return agents.find((a) => a.id === agentId)
    },
    [agents]
  )

  return {
    isConnected,
    isLoading,
    error,

    cmc: {
      atoms,
      stats,
      storeAtom,
      retrieveAtoms,
      getStats,
    },

    hhni: {
      search: hhniSearch,
      retrieve: hhniRetrieve,
    },

    vif: {
      witnesses,
      confidences,
      trackConfidence,
      getWitnesses,
      getConfidence,
    },

    apoe: {
      plans,
      tasks: plans.flatMap((p) => p.tasks || []),
      createPlan,
      executePlan,
    },

    seg: {
      contradictions,
      detectContradictions,
      synthesizeKnowledge,
    },

    tcs: {
      entries: timelineEntries,
      addEntry: addTimelineEntry,
      getSummary,
      getEntries,
    },

    agents: {
      agents,
      getActiveAgents,
      getAgent,
    },
  }
}

// Individual hooks for backward compatibility
export const useCMC = () => {
  const { cmc } = useAIMOS()
  return cmc
}

export const useHHNI = () => {
  const { hhni } = useAIMOS()
  return hhni
}

export const useVIF = () => {
  const { vif } = useAIMOS()
  return vif
}

export const useAPOE = () => {
  const { apoe } = useAIMOS()
  return apoe
}

export const useSEG = () => {
  const { seg } = useAIMOS()
  return seg
}

export const useTCS = () => {
  const { tcs } = useAIMOS()
  return tcs
}

export const useAgents = () => {
  const { agents } = useAIMOS()
  return agents
}
