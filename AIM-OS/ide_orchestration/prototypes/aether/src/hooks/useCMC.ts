import { useState, useCallback } from 'react'
import type { Memory, MemoryStats, CMCInterface } from './types'

/**
 * useCMC Hook
 * 
 * Individual hook for CMC (Context Memory Core) system
 * Provides store, retrieve, and getStats functionality
 */
export function useCMC(): CMCInterface {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  const store = useCallback(async (content: string, tags?: Record<string, any>): Promise<string> => {
    setLoading(true)
    setError(null)
    try {
      // TODO: Replace with real MCP call when connected
      await new Promise(resolve => setTimeout(resolve, 100))
      const atomId = `atom_${Date.now()}`
      return atomId
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to store memory')
      setError(error)
      throw error
    } finally {
      setLoading(false)
    }
  }, [])

  const retrieve = useCallback(async (query: string, limit = 10): Promise<Memory[]> => {
    setLoading(true)
    setError(null)
    try {
      // TODO: Replace with real MCP call when connected
      await new Promise(resolve => setTimeout(resolve, 100))
      return [
        {
          id: 'atom_1',
          content: `Mock memory for: ${query}`,
          tags: { query },
          timestamp: new Date().toISOString(),
          confidence: 0.85
        }
      ]
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to retrieve memory')
      setError(error)
      throw error
    } finally {
      setLoading(false)
    }
  }, [])

  const getStats = useCallback(async (): Promise<MemoryStats> => {
    setLoading(true)
    setError(null)
    try {
      // TODO: Replace with real MCP call when connected
      await new Promise(resolve => setTimeout(resolve, 100))
      return {
        total: 150,
        byTag: { insight: 50, decision: 30, learning: 70 },
        recent: 10
      }
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to get stats')
      setError(error)
      throw error
    } finally {
      setLoading(false)
    }
  }, [])

  return {
    store,
    retrieve,
    getStats,
    loading,
    error
  }
}

