// Enhanced AIM-OS Hooks System - V2 Foundation Enhancement
// Adds caching, error handling, retry logic, and performance optimizations

import { useState, useEffect, useCallback, useRef } from 'react'
import {
  useCMC as useCMCBase,
  useHHNI as useHNNIBase,
  useVIF as useVIFBase,
  useSEG as useSEGBase,
  useTCS as useTCSBase,
  useCAS as useCASBase,
  useAPOE as useAPOEBase,
  useContextWeb as useContextWebBase,
  type CMCAtom,
  type HHNISearchResult,
  type VIFWitness,
  type SEGEntity,
  type SEGRelation,
  type SEGContradiction,
  type TimelineEntry,
  type CASAttentionMetrics,
} from './useAIMOS'

// ===== CACHE CONFIGURATION =====

interface CacheConfig {
  ttl: number  // Time to live in milliseconds
  maxSize: number  // Maximum cache entries
}

const DEFAULT_CACHE_CONFIG: CacheConfig = {
  ttl: 5 * 60 * 1000,  // 5 minutes
  maxSize: 100,
}

// ===== CACHE IMPLEMENTATION =====

class SimpleCache<T> {
  private cache: Map<string, { data: T; timestamp: number }> = new Map()
  private config: CacheConfig

  constructor(config: CacheConfig = DEFAULT_CACHE_CONFIG) {
    this.config = config
  }

  get(key: string): T | null {
    const entry = this.cache.get(key)
    if (!entry) return null

    const age = Date.now() - entry.timestamp
    if (age > this.config.ttl) {
      this.cache.delete(key)
      return null
    }

    return entry.data
  }

  set(key: string, data: T): void {
    // Evict oldest entries if cache is full
    if (this.cache.size >= this.config.maxSize) {
      const oldestKey = Array.from(this.cache.entries())
        .sort((a, b) => a[1].timestamp - b[1].timestamp)[0][0]
      this.cache.delete(oldestKey)
    }

    this.cache.set(key, { data, timestamp: Date.now() })
  }

  clear(): void {
    this.cache.clear()
  }

  invalidate(keyPattern?: string): void {
    if (!keyPattern) {
      this.cache.clear()
      return
    }

    for (const key of this.cache.keys()) {
      if (key.includes(keyPattern)) {
        this.cache.delete(key)
      }
    }
  }
}

// ===== ERROR HANDLING =====

export interface HookError {
  message: string
  code?: string
  retryable: boolean
  timestamp: string
}

class ErrorHandler {
  static createError(message: string, code?: string, retryable: boolean = false): HookError {
    return {
      message,
      code,
      retryable,
      timestamp: new Date().toISOString(),
    }
  }

  static isRetryable(error: HookError): boolean {
    return error.retryable
  }
}

// ===== RETRY LOGIC =====

async function withRetry<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  delay: number = 1000
): Promise<T> {
  let lastError: Error | null = null

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn()
    } catch (error) {
      lastError = error as Error
      if (attempt < maxRetries) {
        await new Promise((resolve) => setTimeout(resolve, delay * (attempt + 1)))
      }
    }
  }

  throw lastError || new Error('Retry failed')
}

// ===== ENHANCED HOOKS =====

// Enhanced CMC Hook
export const useCMCEnhanced = () => {
  const baseHook = useCMCBase()
  const cache = useRef(new SimpleCache<CMCAtom[]>({ ttl: 2 * 60 * 1000, maxSize: 50 }))
  const [error, setError] = useState<HookError | null>(null)
  const [loading, setLoading] = useState(false)

  const retrieveAtomsCached = useCallback(
    async (query?: string, tags?: Record<string, number>): Promise<CMCAtom[]> => {
      const cacheKey = `cmc_atoms_${JSON.stringify({ query, tags })}`
      
      // Check cache first
      const cached = cache.current.get(cacheKey)
      if (cached) {
        return cached
      }

      setLoading(true)
      setError(null)

      try {
        const atoms = await withRetry(
          () => baseHook.retrieveAtoms(query, tags),
          3,
          500
        )
        cache.current.set(cacheKey, atoms)
        return atoms
      } catch (err) {
        const hookError = ErrorHandler.createError(
          `Failed to retrieve CMC atoms: ${err instanceof Error ? err.message : 'Unknown error'}`,
          'CMC_RETRIEVE_ERROR',
          true
        )
        setError(hookError)
        throw hookError
      } finally {
        setLoading(false)
      }
    },
    [baseHook]
  )

  const storeAtomCached = useCallback(
    async (atom: Partial<CMCAtom>): Promise<CMCAtom> => {
      setLoading(true)
      setError(null)

      try {
        const stored = await withRetry(
          () => baseHook.storeAtom(atom),
          3,
          500
        )
        // Invalidate cache after storing
        cache.current.invalidate('cmc_atoms')
        return stored
      } catch (err) {
        const hookError = ErrorHandler.createError(
          `Failed to store CMC atom: ${err instanceof Error ? err.message : 'Unknown error'}`,
          'CMC_STORE_ERROR',
          true
        )
        setError(hookError)
        throw hookError
      } finally {
        setLoading(false)
      }
    },
    [baseHook]
  )

  return {
    ...baseHook,
    retrieveAtoms: retrieveAtomsCached,
    storeAtom: storeAtomCached,
    error,
    loading,
    clearCache: () => cache.current.clear(),
  }
}

// Enhanced HHNI Hook
export const useHHNIEnhanced = () => {
  const baseHook = useHNNIBase()
  const cache = useRef(new SimpleCache<HHNISearchResult[]>({ ttl: 3 * 60 * 1000, maxSize: 50 }))
  const [error, setError] = useState<HookError | null>(null)
  const [loading, setLoading] = useState(false)

  const searchCached = useCallback(
    async (
      query: string,
      levels?: ('document' | 'paragraph' | 'sentence')[]
    ): Promise<HHNISearchResult[]> => {
      const cacheKey = `hhni_search_${query}_${JSON.stringify(levels)}`
      
      // Check cache first
      const cached = cache.current.get(cacheKey)
      if (cached) {
        return cached
      }

      setLoading(true)
      setError(null)

      try {
        const results = await withRetry(
          () => baseHook.search(query, levels),
          3,
          500
        )
        cache.current.set(cacheKey, results)
        return results
      } catch (err) {
        const hookError = ErrorHandler.createError(
          `Failed to search HHNI: ${err instanceof Error ? err.message : 'Unknown error'}`,
          'HHNI_SEARCH_ERROR',
          true
        )
        setError(hookError)
        throw hookError
      } finally {
        setLoading(false)
      }
    },
    [baseHook]
  )

  return {
    ...baseHook,
    search: searchCached,
    error,
    loading,
    clearCache: () => cache.current.clear(),
  }
}

// Enhanced VIF Hook
export const useVIFEnhanced = () => {
  const baseHook = useVIFBase()
  const cache = useRef(new SimpleCache<VIFWitness[]>({ ttl: 5 * 60 * 1000, maxSize: 50 }))
  const [error, setError] = useState<HookError | null>(null)
  const [loading, setLoading] = useState(false)

  const trackConfidenceCached = useCallback(
    async (
      modelId: string,
      confidence: number,
      taskCriticality?: 'critical' | 'important' | 'routine' | 'low_stakes'
    ): Promise<VIFWitness> => {
      setLoading(true)
      setError(null)

      try {
        const witness = await withRetry(
          () => baseHook.trackConfidence(modelId, confidence, taskCriticality),
          3,
          500
        )
        // Invalidate cache after tracking
        cache.current.invalidate('vif_witnesses')
        return witness
      } catch (err) {
        const hookError = ErrorHandler.createError(
          `Failed to track VIF confidence: ${err instanceof Error ? err.message : 'Unknown error'}`,
          'VIF_TRACK_ERROR',
          true
        )
        setError(hookError)
        throw hookError
      } finally {
        setLoading(false)
      }
    },
    [baseHook]
  )

  const getWitnessesCached = useCallback(
    async (filters?: { modelId?: string; minConfidence?: number }): Promise<VIFWitness[]> => {
      const cacheKey = `vif_witnesses_${JSON.stringify(filters)}`
      
      // Check cache first
      const cached = cache.current.get(cacheKey)
      if (cached) {
        return cached
      }

      setLoading(true)
      setError(null)

      try {
        const witnesses = await withRetry(
          () => baseHook.getWitnesses(filters),
          3,
          500
        )
        cache.current.set(cacheKey, witnesses)
        return witnesses
      } catch (err) {
        const hookError = ErrorHandler.createError(
          `Failed to get VIF witnesses: ${err instanceof Error ? err.message : 'Unknown error'}`,
          'VIF_GET_ERROR',
          true
        )
        setError(hookError)
        throw hookError
      } finally {
        setLoading(false)
      }
    },
    [baseHook]
  )

  return {
    ...baseHook,
    trackConfidence: trackConfidenceCached,
    getWitnesses: getWitnessesCached,
    error,
    loading,
    clearCache: () => cache.current.clear(),
  }
}

// Enhanced SEG Hook
export const useSEGEnhanced = () => {
  const baseHook = useSEGBase()
  const cache = useRef(new SimpleCache<SEGContradiction[]>({ ttl: 2 * 60 * 1000, maxSize: 50 }))
  const [error, setError] = useState<HookError | null>(null)
  const [loading, setLoading] = useState(false)

  const detectContradictionsCached = useCallback(
    async (query?: string): Promise<SEGContradiction[]> => {
      const cacheKey = `seg_contradictions_${query || 'all'}`
      
      // Check cache first
      const cached = cache.current.get(cacheKey)
      if (cached) {
        return cached
      }

      setLoading(true)
      setError(null)

      try {
        const contradictions = await withRetry(
          () => baseHook.detectContradictions(query),
          3,
          500
        )
        cache.current.set(cacheKey, contradictions)
        return contradictions
      } catch (err) {
        const hookError = ErrorHandler.createError(
          `Failed to detect SEG contradictions: ${err instanceof Error ? err.message : 'Unknown error'}`,
          'SEG_DETECT_ERROR',
          true
        )
        setError(hookError)
        throw hookError
      } finally {
        setLoading(false)
      }
    },
    [baseHook]
  )

  return {
    ...baseHook,
    detectContradictions: detectContradictionsCached,
    error,
    loading,
    clearCache: () => cache.current.clear(),
  }
}

// Enhanced TCS Hook
export const useTCSEnhanced = () => {
  const baseHook = useTCSBase()
  const cache = useRef(new SimpleCache<TimelineEntry[]>({ ttl: 1 * 60 * 1000, maxSize: 50 }))
  const [error, setError] = useState<HookError | null>(null)
  const [loading, setLoading] = useState(false)

  const getSummaryCached = useCallback(
    async (limit: number = 10): Promise<TimelineEntry[]> => {
      const cacheKey = `tcs_summary_${limit}`
      
      // Check cache first
      const cached = cache.current.get(cacheKey)
      if (cached) {
        return cached
      }

      setLoading(true)
      setError(null)

      try {
        const entries = await withRetry(
          () => baseHook.getSummary(limit),
          3,
          500
        )
        cache.current.set(cacheKey, entries)
        return entries
      } catch (err) {
        const hookError = ErrorHandler.createError(
          `Failed to get TCS summary: ${err instanceof Error ? err.message : 'Unknown error'}`,
          'TCS_GET_ERROR',
          true
        )
        setError(hookError)
        throw hookError
      } finally {
        setLoading(false)
      }
    },
    [baseHook]
  )

  return {
    ...baseHook,
    getSummary: getSummaryCached,
    error,
    loading,
    clearCache: () => cache.current.clear(),
  }
}

// Enhanced CAS Hook
export const useCASEnhanced = () => {
  const baseHook = useCASBase()
  const cache = useRef(new SimpleCache<CASAttentionMetrics>({ ttl: 30 * 1000, maxSize: 10 }))
  const [error, setError] = useState<HookError | null>(null)
  const [loading, setLoading] = useState(false)

  const getMetricsCached = useCallback(
    async (): Promise<CASAttentionMetrics | null> => {
      const cacheKey = 'cas_metrics_latest'
      
      // Check cache first (short TTL for real-time data)
      const cached = cache.current.get(cacheKey)
      if (cached) {
        return cached
      }

      setLoading(true)
      setError(null)

      try {
        const metrics = await withRetry(
          () => baseHook.getMetrics(),
          3,
          500
        )
        if (metrics) {
          cache.current.set(cacheKey, metrics)
        }
        return metrics
      } catch (err) {
        const hookError = ErrorHandler.createError(
          `Failed to get CAS metrics: ${err instanceof Error ? err.message : 'Unknown error'}`,
          'CAS_GET_ERROR',
          true
        )
        setError(hookError)
        throw hookError
      } finally {
        setLoading(false)
      }
    },
    [baseHook]
  )

  return {
    ...baseHook,
    getMetrics: getMetricsCached,
    error,
    loading,
    clearCache: () => cache.current.clear(),
  }
}

// Re-export base hooks for backward compatibility
export {
  useCMCBase as useCMC,
  useHNNIBase as useHHNI,
  useVIFBase as useVIF,
  useSEGBase as useSEG,
  useTCSBase as useTCS,
  useCASBase as useCAS,
  useAPOEBase as useAPOE,
  useContextWebBase as useContextWeb,
}

