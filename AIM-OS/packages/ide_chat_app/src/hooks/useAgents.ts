/**
 * Hook for Agent Management with AIMOSService Integration
 * Fetches real agent data and confidence from AIM-OS systems
 * 
 * Created: 2025-10-31
 * Agent: Aether
 */

import { useState, useEffect, useCallback } from 'react'
import AIMOSService, { ConfidenceRecord } from '../services/AIMOSService'
import { getMCPAPI } from '../services/mcpApi'

export interface Agent {
  id: string
  name: string
  role: string
  status: 'active' | 'idle' | 'busy' | 'error' | 'offline'
  model: string
  currentTask?: string
  progress?: number
  lastActivity: string
  messages: number
  tasksCompleted: number
  autoContinue: boolean
  confidence?: number
  confidenceHistory?: ConfidenceRecord[]
}

const aimosService = new AIMOSService()
const mcpApi = getMCPAPI()

export const useAgents = () => {
  const [agents, setAgents] = useState<Agent[]>([
    {
      id: 'aether',
      name: 'Aether',
      role: 'Manager/Leader',
      status: 'active',
      model: 'claude-sonnet-4',
      currentTask: 'Reviewing standards compliance',
      progress: 75,
      lastActivity: '2 minutes ago',
      messages: 42,
      tasksCompleted: 127,
      autoContinue: true,
      confidence: 0.95
    },
    {
      id: 'lexicon',
      name: 'Lexicon',
      role: 'UI Developer',
      status: 'active',
      model: 'gpt-4',
      currentTask: 'Building Agent Management Dashboard',
      progress: 85,
      lastActivity: '30 seconds ago',
      messages: 28,
      tasksCompleted: 45,
      autoContinue: true,
      confidence: 0.92
    },
    {
      id: 'solo',
      name: 'Solo',
      role: 'Backend Developer',
      status: 'active',
      model: 'gpt-4',
      currentTask: 'MCP Tools Enhancement',
      progress: 65,
      lastActivity: '5 minutes ago',
      messages: 15,
      tasksCompleted: 89,
      autoContinue: false,
      confidence: 0.62
    },
    {
      id: 'atlas',
      name: 'Atlas',
      role: 'System Mapping Specialist',
      status: 'idle',
      model: 'claude-sonnet-4',
      lastActivity: '15 minutes ago',
      messages: 8,
      tasksCompleted: 23,
      autoContinue: true,
      confidence: 0.85
    }
  ])

  const [loading, setLoading] = useState(false)
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date())

  // Fetch agents from service (if available)
  const fetchAgents = useCallback(async () => {
    try {
      // Add timeout to prevent freezing
      const timeoutPromise = new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Timeout')), 2000)
      )
      const fetchedAgents = await Promise.race([
        aimosService.getAgents(),
        timeoutPromise
      ]) as Agent[]
      if (fetchedAgents && fetchedAgents.length > 0) {
        setAgents(fetchedAgents)
      }
    } catch (error) {
      console.log('[useAgents] Using default agents (daemon not available):', error)
      // Keep default agents on error - don't log as error, this is expected
    }
  }, [])

  // Fetch confidence history for all agents
  const fetchConfidenceHistory = useCallback(async () => {
    try {
      // Add timeout to prevent freezing
      const timeoutPromise = new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Timeout')), 2000)
      )
      
      // Try MCP API first (via Extension), fallback to direct HTTP
      const updatedAgents = await Promise.race([
        Promise.all(
          agents.map(async (agent) => {
            if (agent.currentTask) {
              try {
                // Try MCP API first
                let history: ConfidenceRecord[] = []
                let latestConfidence = agent.confidence
                
                try {
                  // Check if extension is available
                  const extensionAvailable = await mcpApi.checkExtension()
                  if (extensionAvailable) {
                    // Use MCP tool to get confidence history
                    // Note: This may need custom MCP tool or we use VIF queries
                    // For now, try direct service with timeout
                    const historyPromise = aimosService.getConfidenceHistory(agent.currentTask)
                    const timeout = new Promise((_, reject) => 
                      setTimeout(() => reject(new Error('Timeout')), 1000)
                    )
                    history = await Promise.race([historyPromise, timeout]) as ConfidenceRecord[]
                  } else {
                    // Extension not available, try direct HTTP
                    const historyPromise = aimosService.getConfidenceHistory(agent.currentTask)
                    const timeout = new Promise((_, reject) => 
                      setTimeout(() => reject(new Error('Timeout')), 1000)
                    )
                    history = await Promise.race([historyPromise, timeout]) as ConfidenceRecord[]
                  }
                  
                  // Get the most recent confidence
                  latestConfidence = history.length > 0 
                    ? history[history.length - 1].confidence 
                    : agent.confidence
                } catch (error) {
                  // Silently fail - keep agent unchanged
                  return agent
                }

                return {
                  ...agent,
                  confidence: latestConfidence,
                  confidenceHistory: history
                }
              } catch (error) {
                // Silently fail - keep agent unchanged
                return agent
              }
            }
            return agent
          })
        ),
        timeoutPromise
      ]) as Agent[]

      setAgents(updatedAgents)
      setLastUpdate(new Date())
    } catch (error) {
      // Silently fail - daemon not available, use default agents
      console.log('[useAgents] Using default confidence (services not available)')
    }
  }, [agents])

  // Track confidence for an agent
  const trackConfidence = useCallback(async (
    agentId: string,
    task: string,
    confidence: number,
    reasoning?: string
  ) => {
    try {
      // Try MCP API first (via Extension), fallback to direct HTTP
      const extensionAvailable = await mcpApi.checkExtension()
      if (extensionAvailable) {
        // Use MCP tool
        await mcpApi.trackConfidence(task, confidence, reasoning)
      } else {
        // Fallback to direct HTTP
        await aimosService.trackConfidence(task, confidence, reasoning)
      }
      
      // Update agent's confidence
      setAgents(prevAgents =>
        prevAgents.map(agent =>
          agent.id === agentId
            ? { ...agent, confidence }
            : agent
        )
      )
    } catch (error) {
      console.error(`Failed to track confidence for ${agentId}:`, error)
    }
  }, [])

  // Update agent status
  const updateAgent = useCallback((agentId: string, updates: Partial<Agent>) => {
    setAgents(prevAgents =>
      prevAgents.map(agent =>
        agent.id === agentId
          ? { ...agent, ...updates }
          : agent
      )
    )
  }, [])

  // Fetch agents from service (with delay to prevent blocking initial render)
  useEffect(() => {
    // Delay fetch to let UI render first
    const timer = setTimeout(() => {
      fetchAgents()
    }, 100)
    return () => clearTimeout(timer)
  }, [fetchAgents])

  // Poll for updates every 30 seconds (but only if daemon is available)
  useEffect(() => {
    // Delay initial fetch to prevent blocking
    const timer = setTimeout(() => {
      fetchConfidenceHistory()
    }, 500)
    
    const interval = setInterval(() => {
      fetchConfidenceHistory()
    }, 30000) // 30 seconds

    return () => {
      clearTimeout(timer)
      clearInterval(interval)
    }
  }, [fetchConfidenceHistory])

  return {
    agents,
    loading,
    lastUpdate,
    fetchConfidenceHistory,
    trackConfidence,
    updateAgent
  }
}

