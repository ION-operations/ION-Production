import { useState, useEffect, useCallback } from 'react'
import { memoryStore, type RawLogEntry, type SummaryEntry, type VectorEntry } from '../lib/memory-store'

export function useMemory() {
  const [isInitialized, setIsInitialized] = useState(false)
  const [stats, setStats] = useState({
    rawLogCount: 0,
    summaryCount: 0,
    vectorCount: 0,
    totalSize: 0
  })

  // Initialize memory store
  useEffect(() => {
    const init = async () => {
      try {
        await memoryStore.initialize()
        setIsInitialized(true)
        await updateStats()
      } catch (error) {
        console.error('Failed to initialize memory store:', error)
      }
    }
    init()
  }, [])

  const updateStats = useCallback(async () => {
    try {
      const newStats = await memoryStore.getMemoryStats()
      setStats(newStats)
    } catch (error) {
      console.error('Failed to get memory stats:', error)
    }
  }, [])

  // Raw Log Operations
  const addRawLogEntry = useCallback(async (entry: Omit<RawLogEntry, 'id'>) => {
    if (!isInitialized) throw new Error('Memory store not initialized')
    
    const newEntry: RawLogEntry = {
      ...entry,
      id: `raw_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    }
    
    await memoryStore.addRawLogEntry(newEntry)
    await updateStats()
    return newEntry
  }, [isInitialized, updateStats])

  const getRawLogEntries = useCallback(async (sessionId?: string, limit = 100) => {
    if (!isInitialized) throw new Error('Memory store not initialized')
    return await memoryStore.getRawLogEntries(sessionId, limit)
  }, [isInitialized])

  // Summary Operations
  const addSummaryEntry = useCallback(async (entry: Omit<SummaryEntry, 'id' | 'createdAt' | 'updatedAt'>) => {
    if (!isInitialized) throw new Error('Memory store not initialized')
    
    const now = new Date()
    const newEntry: SummaryEntry = {
      ...entry,
      id: `summary_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      createdAt: now,
      updatedAt: now
    }
    
    await memoryStore.addSummaryEntry(newEntry)
    await updateStats()
    return newEntry
  }, [isInitialized, updateStats])

  const getSummaryEntries = useCallback(async (level?: string, limit = 50) => {
    if (!isInitialized) throw new Error('Memory store not initialized')
    return await memoryStore.getSummaryEntries(level, limit)
  }, [isInitialized])

  const updateSummaryEntry = useCallback(async (id: string, updates: Partial<SummaryEntry>) => {
    if (!isInitialized) throw new Error('Memory store not initialized')
    
    await memoryStore.updateSummaryEntry(id, updates)
    await updateStats()
  }, [isInitialized, updateStats])

  // Vector Operations
  const addVectorEntry = useCallback(async (entry: Omit<VectorEntry, 'id' | 'createdAt'>) => {
    if (!isInitialized) throw new Error('Memory store not initialized')
    
    const newEntry: VectorEntry = {
      ...entry,
      id: `vector_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      createdAt: new Date()
    }
    
    await memoryStore.addVectorEntry(newEntry)
    await updateStats()
    return newEntry
  }, [isInitialized, updateStats])

  const searchVectors = useCallback(async (query: string, limit = 10) => {
    if (!isInitialized) throw new Error('Memory store not initialized')
    return await memoryStore.searchVectors(query, limit)
  }, [isInitialized])

  // Utility Operations
  const clearAllData = useCallback(async () => {
    if (!isInitialized) throw new Error('Memory store not initialized')
    
    await memoryStore.clearAllData()
    await updateStats()
  }, [isInitialized, updateStats])

  // Auto-summarization helper
  const createSessionSummary = useCallback(async (sessionId: string, messages: any[]) => {
    if (!isInitialized) throw new Error('Memory store not initialized')
    
    // Get raw log entries for this session
    const rawEntries = await getRawLogEntries(sessionId)
    
    if (rawEntries.length === 0) return null

    // Create a summary of the session
    const content = rawEntries.map(entry => entry.content).join(' ')
    const summary = content.length > 200 ? content.substring(0, 200) + '...' : content
    
    // Generate tags from content
    const words = content.toLowerCase().split(/\W+/)
    const wordCount = new Map<string, number>()
    words.forEach(word => {
      if (word.length > 3) {
        wordCount.set(word, (wordCount.get(word) || 0) + 1)
      }
    })
    
    const tags = Array.from(wordCount.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([word]) => word)

    const summaryEntry = await addSummaryEntry({
      title: `Session ${sessionId}`,
      summary,
      level: 'session',
      childrenIds: rawEntries.map(entry => entry.id),
      importance: 0.7,
      tags
    })

    return summaryEntry
  }, [isInitialized, getRawLogEntries, addSummaryEntry])

  // Semantic search helper
  const semanticSearch = useCallback(async (query: string, limit = 10) => {
    if (!isInitialized) throw new Error('Memory store not initialized')
    
    // Search both summaries and vectors
    const [summaryResults, vectorResults] = await Promise.all([
      getSummaryEntries(undefined, limit),
      searchVectors(query, limit)
    ])

    // Combine and deduplicate results
    const allResults = [...summaryResults, ...vectorResults]
    const uniqueResults = allResults.filter((result, index, self) => 
      index === self.findIndex(r => r.id === result.id)
    )

    return uniqueResults.slice(0, limit)
  }, [isInitialized, getSummaryEntries, searchVectors])

  return {
    isInitialized,
    stats,
    // Raw Log
    addRawLogEntry,
    getRawLogEntries,
    // Summary
    addSummaryEntry,
    getSummaryEntries,
    updateSummaryEntry,
    // Vector
    addVectorEntry,
    searchVectors,
    // Utilities
    clearAllData,
    createSessionSummary,
    semanticSearch,
    updateStats
  }
}
