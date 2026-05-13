/**
 * Performance Service
 * 
 * Handles performance optimization for large codebases and real-time features.
 */

import { EventEmitter } from 'events';
import { LucidOrchestratorData, Event } from '../../../lucid_orchestrator/data_models/core_interfaces';

export interface PerformanceMetrics {
  renderTime: number;
  dataLoadTime: number;
  memoryUsage: number;
  cacheHitRate: number;
  networkLatency: number;
  cpuUsage: number;
}

export interface OptimizationStrategy {
  id: string;
  name: string;
  description: string;
  impact: 'low' | 'medium' | 'high';
  effort: 'low' | 'medium' | 'high';
  enabled: boolean;
  config: any;
}

export interface CacheConfig {
  maxSize: number;
  ttl: number;
  strategy: 'lru' | 'lfu' | 'fifo';
  compression: boolean;
}

export interface VirtualizationConfig {
  enabled: boolean;
  itemHeight: number;
  bufferSize: number;
  threshold: number;
}

export class PerformanceService extends EventEmitter {
  private metrics: PerformanceMetrics = {
    renderTime: 0,
    dataLoadTime: 0,
    memoryUsage: 0,
    cacheHitRate: 0,
    networkLatency: 0,
    cpuUsage: 0
  };

  private cache: Map<string, { data: any; timestamp: number; ttl: number }> = new Map();
  private optimizationStrategies: Map<string, OptimizationStrategy> = new Map();
  private performanceObservers: Map<string, PerformanceObserver> = new Map();
  private updateInterval: NodeJS.Timeout | null = null;

  private cacheConfig: CacheConfig = {
    maxSize: 1000,
    ttl: 300000, // 5 minutes
    strategy: 'lru',
    compression: true
  };

  private virtualizationConfig: VirtualizationConfig = {
    enabled: true,
    itemHeight: 50,
    bufferSize: 10,
    threshold: 100
  };

  constructor() {
    super();
    this.initializeOptimizationStrategies();
    this.startPerformanceMonitoring();
  }

  /**
   * Initialize optimization strategies
   */
  private initializeOptimizationStrategies(): void {
    // Data caching strategy
    this.optimizationStrategies.set('data_caching', {
      id: 'data_caching',
      name: 'Data Caching',
      description: 'Cache frequently accessed data to reduce load times',
      impact: 'high',
      effort: 'low',
      enabled: true,
      config: this.cacheConfig
    });

    // Virtual scrolling strategy
    this.optimizationStrategies.set('virtual_scrolling', {
      id: 'virtual_scrolling',
      name: 'Virtual Scrolling',
      description: 'Only render visible items in large lists',
      impact: 'high',
      effort: 'medium',
      enabled: true,
      config: this.virtualizationConfig
    });

    // Lazy loading strategy
    this.optimizationStrategies.set('lazy_loading', {
      id: 'lazy_loading',
      name: 'Lazy Loading',
      description: 'Load data only when needed',
      impact: 'medium',
      effort: 'low',
      enabled: true,
      config: { threshold: 0.8 }
    });

    // Debouncing strategy
    this.optimizationStrategies.set('debouncing', {
      id: 'debouncing',
      name: 'Debouncing',
      description: 'Debounce rapid updates to reduce processing',
      impact: 'medium',
      effort: 'low',
      enabled: true,
      config: { delay: 300 }
    });

    // Memoization strategy
    this.optimizationStrategies.set('memoization', {
      id: 'memoization',
      name: 'Memoization',
      description: 'Cache expensive computations',
      impact: 'high',
      effort: 'medium',
      enabled: true,
      config: { maxSize: 500 }
    });
  }

  /**
   * Start performance monitoring
   */
  private startPerformanceMonitoring(): void {
    // Monitor render performance
    if (typeof window !== 'undefined' && 'PerformanceObserver' in window) {
      const renderObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry) => {
          if (entry.entryType === 'measure') {
            this.metrics.renderTime = entry.duration;
            this.emit('render_metrics', { duration: entry.duration });
          }
        });
      });
      renderObserver.observe({ entryTypes: ['measure'] });
      this.performanceObservers.set('render', renderObserver);
    }

    // Monitor memory usage
    this.updateInterval = setInterval(() => {
      this.updateMemoryMetrics();
    }, 5000);
  }

  /**
   * Update memory metrics
   */
  private updateMemoryMetrics(): void {
    if (typeof window !== 'undefined' && 'memory' in performance) {
      const memory = (performance as any).memory;
      this.metrics.memoryUsage = memory.usedJSHeapSize / memory.jsHeapSizeLimit;
      this.emit('memory_metrics', { usage: this.metrics.memoryUsage });
    }
  }

  /**
   * Cache data with TTL
   */
  cacheData(key: string, data: any, ttl?: number): void {
    const effectiveTtl = ttl || this.cacheConfig.ttl;
    const timestamp = Date.now();

    // Check cache size and evict if necessary
    if (this.cache.size >= this.cacheConfig.maxSize) {
      this.evictCache();
    }

    this.cache.set(key, {
      data,
      timestamp,
      ttl: effectiveTtl
    });

    this.emit('cache_updated', { key, size: this.cache.size });
  }

  /**
   * Get cached data
   */
  getCachedData(key: string): any | null {
    const cached = this.cache.get(key);
    if (!cached) {
      return null;
    }

    const now = Date.now();
    if (now - cached.timestamp > cached.ttl) {
      this.cache.delete(key);
      return null;
    }

    this.metrics.cacheHitRate = (this.metrics.cacheHitRate + 1) / 2; // Simple moving average
    return cached.data;
  }

  /**
   * Evict cache using LRU strategy
   */
  private evictCache(): void {
    if (this.cacheConfig.strategy === 'lru') {
      // Find oldest entry
      let oldestKey = '';
      let oldestTime = Date.now();
      
      for (const [key, value] of this.cache.entries()) {
        if (value.timestamp < oldestTime) {
          oldestTime = value.timestamp;
          oldestKey = key;
        }
      }
      
      if (oldestKey) {
        this.cache.delete(oldestKey);
      }
    }
  }

  /**
   * Clear cache
   */
  clearCache(): void {
    this.cache.clear();
    this.emit('cache_cleared');
  }

  /**
   * Get cache statistics
   */
  getCacheStats(): { size: number; hitRate: number; maxSize: number } {
    return {
      size: this.cache.size,
      hitRate: this.metrics.cacheHitRate,
      maxSize: this.cacheConfig.maxSize
    };
  }

  /**
   * Debounce function calls
   */
  debounce<T extends (...args: any[]) => any>(
    func: T,
    delay: number = 300
  ): (...args: Parameters<T>) => void {
    let timeoutId: NodeJS.Timeout;
    
    return (...args: Parameters<T>) => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
  }

  /**
   * Throttle function calls
   */
  throttle<T extends (...args: any[]) => any>(
    func: T,
    limit: number = 100
  ): (...args: Parameters<T>) => void {
    let inThrottle: boolean;
    
    return (...args: Parameters<T>) => {
      if (!inThrottle) {
        func.apply(this, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  }

  /**
   * Memoize expensive computations
   */
  memoize<T extends (...args: any[]) => any>(
    func: T,
    keyGenerator?: (...args: Parameters<T>) => string
  ): T {
    const cache = new Map<string, ReturnType<T>>();
    
    return ((...args: Parameters<T>) => {
      const key = keyGenerator ? keyGenerator(...args) : JSON.stringify(args);
      
      if (cache.has(key)) {
        return cache.get(key);
      }
      
      const result = func(...args);
      cache.set(key, result);
      
      // Limit cache size
      if (cache.size > 500) {
        const firstKey = cache.keys().next().value;
        cache.delete(firstKey);
      }
      
      return result;
    }) as T;
  }

  /**
   * Virtualize large lists
   */
  virtualizeList<T>(
    items: T[],
    containerHeight: number,
    scrollTop: number
  ): { visibleItems: T[]; startIndex: number; endIndex: number; totalHeight: number } {
    if (!this.virtualizationConfig.enabled || items.length <= this.virtualizationConfig.threshold) {
      return {
        visibleItems: items,
        startIndex: 0,
        endIndex: items.length - 1,
        totalHeight: items.length * this.virtualizationConfig.itemHeight
      };
    }

    const itemHeight = this.virtualizationConfig.itemHeight;
    const bufferSize = this.virtualizationConfig.bufferSize;
    const totalHeight = items.length * itemHeight;
    
    const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - bufferSize);
    const endIndex = Math.min(
      items.length - 1,
      Math.ceil((scrollTop + containerHeight) / itemHeight) + bufferSize
    );
    
    const visibleItems = items.slice(startIndex, endIndex + 1);
    
    return {
      visibleItems,
      startIndex,
      endIndex,
      totalHeight
    };
  }

  /**
   * Optimize data loading
   */
  async optimizeDataLoading<T>(
    dataLoader: () => Promise<T>,
    cacheKey: string,
    options: { ttl?: number; lazy?: boolean } = {}
  ): Promise<T> {
    // Check cache first
    const cached = this.getCachedData(cacheKey);
    if (cached) {
      return cached;
    }

    // Load data
    const startTime = performance.now();
    const data = await dataLoader();
    const loadTime = performance.now() - startTime;
    
    this.metrics.dataLoadTime = loadTime;
    this.emit('data_loaded', { key: cacheKey, loadTime });

    // Cache the result
    this.cacheData(cacheKey, data, options.ttl);
    
    return data;
  }

  /**
   * Get performance metrics
   */
  getMetrics(): PerformanceMetrics {
    return { ...this.metrics };
  }

  /**
   * Get optimization strategies
   */
  getOptimizationStrategies(): OptimizationStrategy[] {
    return Array.from(this.optimizationStrategies.values());
  }

  /**
   * Update optimization strategy
   */
  updateOptimizationStrategy(id: string, updates: Partial<OptimizationStrategy>): void {
    const strategy = this.optimizationStrategies.get(id);
    if (strategy) {
      Object.assign(strategy, updates);
      this.emit('strategy_updated', { id, strategy });
    }
  }

  /**
   * Enable/disable optimization strategy
   */
  toggleOptimizationStrategy(id: string, enabled: boolean): void {
    this.updateOptimizationStrategy(id, { enabled });
  }

  /**
   * Get performance recommendations
   */
  getPerformanceRecommendations(): Array<{
    priority: 'low' | 'medium' | 'high';
    category: string;
    description: string;
    impact: string;
    effort: string;
  }> {
    const recommendations = [];

    // Memory usage recommendations
    if (this.metrics.memoryUsage > 0.8) {
      recommendations.push({
        priority: 'high',
        category: 'Memory',
        description: 'High memory usage detected. Consider enabling more aggressive caching strategies.',
        impact: 'High',
        effort: 'Low'
      });
    }

    // Cache hit rate recommendations
    if (this.metrics.cacheHitRate < 0.5) {
      recommendations.push({
        priority: 'medium',
        category: 'Caching',
        description: 'Low cache hit rate. Consider increasing cache size or TTL.',
        impact: 'Medium',
        effort: 'Low'
      });
    }

    // Render time recommendations
    if (this.metrics.renderTime > 16) { // 60fps threshold
      recommendations.push({
        priority: 'high',
        category: 'Rendering',
        description: 'Slow render times detected. Consider enabling virtual scrolling or reducing data complexity.',
        impact: 'High',
        effort: 'Medium'
      });
    }

    return recommendations;
  }

  /**
   * Cleanup resources
   */
  cleanup(): void {
    if (this.updateInterval) {
      clearInterval(this.updateInterval);
      this.updateInterval = null;
    }

    this.performanceObservers.forEach(observer => observer.disconnect());
    this.performanceObservers.clear();
    
    this.removeAllListeners();
    this.cache.clear();
  }
}
