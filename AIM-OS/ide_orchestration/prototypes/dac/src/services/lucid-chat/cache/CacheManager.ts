/**
 * Cache Manager
 * 
 * In-memory cache with TTL and LRU eviction
 */

export interface CacheEntry<T> {
  value: T
  expiresAt: number
  createdAt: number
  accessCount: number
  lastAccessed: number
}

export interface CacheStats {
  size: number
  hits: number
  misses: number
  evictions: number
  hitRate: number
}

export class CacheManager {
  private cache: Map<string, CacheEntry<any>> = new Map()
  private maxSize: number
  private defaultTTL: number
  private hits: number = 0
  private misses: number = 0
  private evictions: number = 0

  constructor(options: {
    maxSize?: number
    defaultTTL?: number
  } = {}) {
    this.maxSize = options.maxSize || 1000
    this.defaultTTL = options.defaultTTL || 3600000 // 1 hour default
  }

  /**
   * Get value from cache
   */
  get<T>(key: string): T | null {
    const entry = this.cache.get(key)

    if (!entry) {
      this.misses++
      return null
    }

    // Check if expired
    if (Date.now() > entry.expiresAt) {
      this.cache.delete(key)
      this.misses++
      this.evictions++
      return null
    }

    // Update access stats
    entry.accessCount++
    entry.lastAccessed = Date.now()
    this.hits++

    return entry.value as T
  }

  /**
   * Set value in cache
   */
  set<T>(key: string, value: T, ttl?: number): void {
    const now = Date.now()
    const expiresAt = now + (ttl || this.defaultTTL)

    // Check if we need to evict
    if (this.cache.size >= this.maxSize && !this.cache.has(key)) {
      this.evictLRU()
    }

    const entry: CacheEntry<T> = {
      value,
      expiresAt,
      createdAt: now,
      accessCount: 0,
      lastAccessed: now,
    }

    this.cache.set(key, entry)
  }

  /**
   * Invalidate cache entry
   */
  invalidate(key: string): void {
    this.cache.delete(key)
  }

  /**
   * Invalidate entries matching pattern
   */
  invalidatePattern(pattern: string): void {
    const regex = new RegExp(pattern)
    let count = 0

    for (const key of this.cache.keys()) {
      if (regex.test(key)) {
        this.cache.delete(key)
        count++
      }
    }

    return count
  }

  /**
   * Clear all cache entries
   */
  clear(): void {
    this.cache.clear()
    this.hits = 0
    this.misses = 0
    this.evictions = 0
  }

  /**
   * Get cache statistics
   */
  getStats(): CacheStats {
    const total = this.hits + this.misses
    return {
      size: this.cache.size,
      hits: this.hits,
      misses: this.misses,
      evictions: this.evictions,
      hitRate: total > 0 ? this.hits / total : 0,
    }
  }

  /**
   * Evict least recently used entry
   */
  private evictLRU(): void {
    let lruKey: string | null = null
    let lruTime = Infinity

    for (const [key, entry] of this.cache.entries()) {
      if (entry.lastAccessed < lruTime) {
        lruTime = entry.lastAccessed
        lruKey = key
      }
    }

    if (lruKey) {
      this.cache.delete(lruKey)
      this.evictions++
    }
  }

  /**
   * Clean expired entries
   */
  cleanExpired(): number {
    const now = Date.now()
    let count = 0

    for (const [key, entry] of this.cache.entries()) {
      if (now > entry.expiresAt) {
        this.cache.delete(key)
        count++
        this.evictions++
      }
    }

    return count
  }

  /**
   * Generate cache key
   */
  static generateKey(prefix: string, params: Record<string, any>): string {
    const sortedParams = Object.keys(params)
      .sort()
      .map(key => `${key}=${JSON.stringify(params[key])}`)
      .join('&')
    
    return `${prefix}:${sortedParams}`
  }
}

