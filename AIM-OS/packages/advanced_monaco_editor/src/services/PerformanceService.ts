/**
 * Performance Service
 * 
 * Provides comprehensive performance monitoring and optimization for the Advanced Monaco Editor
 * including:
 * - Performance metrics collection
 * - Memory usage monitoring
 * - CPU usage tracking
 * - Lazy loading management
 * - Caching optimization
 * - Performance profiling
 * - Resource cleanup
 */

import { EventEmitter } from 'events';

export interface PerformanceMetrics {
  timestamp: number;
  memoryUsage: {
    used: number;
    total: number;
    percentage: number;
  };
  cpuUsage: {
    average: number;
    peak: number;
    current: number;
  };
  renderTime: {
    average: number;
    peak: number;
    current: number;
  };
  analysisTime: {
    average: number;
    peak: number;
    current: number;
  };
  cacheHitRate: {
    average: number;
    current: number;
  };
  lazyLoading: {
    loadedModules: number;
    totalModules: number;
    loadingTime: number;
  };
}

export interface PerformanceConfig {
  enableMonitoring: boolean;
  enableProfiling: boolean;
  enableMemoryTracking: boolean;
  enableCpuTracking: boolean;
  enableRenderTracking: boolean;
  enableAnalysisTracking: boolean;
  enableCacheTracking: boolean;
  enableLazyLoading: boolean;
  maxMemoryUsage: number; // in bytes
  maxCpuUsage: number; // percentage
  maxRenderTime: number; // in milliseconds
  maxAnalysisTime: number; // in milliseconds
  minCacheHitRate: number; // percentage
  monitoringInterval: number; // in milliseconds
  profilingInterval: number; // in milliseconds
  maxMetricsHistory: number;
  enableAlerts: boolean;
  alertThresholds: {
    memory: number; // percentage
    cpu: number; // percentage
    render: number; // milliseconds
    analysis: number; // milliseconds
    cache: number; // percentage
  };
}

export interface LazyLoadConfig {
  enabled: boolean;
  preloadThreshold: number; // distance from viewport
  loadTimeout: number; // milliseconds
  maxConcurrentLoads: number;
  retryAttempts: number;
  retryDelay: number; // milliseconds
  cacheEnabled: boolean;
  cacheSize: number;
  cacheTimeout: number; // milliseconds
}

export interface CacheConfig {
  enabled: boolean;
  maxSize: number; // in bytes
  maxAge: number; // in milliseconds
  cleanupInterval: number; // in milliseconds
  enableCompression: boolean;
  enableEncryption: boolean;
  strategy: 'lru' | 'lfu' | 'fifo' | 'ttl';
}

export class PerformanceService extends EventEmitter {
  private config: PerformanceConfig;
  private lazyLoadConfig: LazyLoadConfig;
  private cacheConfig: CacheConfig;
  private metrics: PerformanceMetrics[] = [];
  private monitoringInterval: NodeJS.Timeout | null = null;
  private profilingInterval: NodeJS.Timeout | null = null;
  private isMonitoring: boolean = false;
  private isProfiling: boolean = false;
  private performanceObserver: PerformanceObserver | null = null;
  private memoryObserver: PerformanceObserver | null = null;
  private renderTimes: number[] = [];
  private analysisTimes: number[] = [];
  private cacheHits: number = 0;
  private cacheMisses: number = 0;
  private loadedModules: Set<string> = new Set();
  private loadingModules: Set<string> = new Set();
  private cache: Map<string, { data: any; timestamp: number; size: number }> = new Map();

  constructor(
    config: Partial<PerformanceConfig> = {},
    lazyLoadConfig: Partial<LazyLoadConfig> = {},
    cacheConfig: Partial<CacheConfig> = {}
  ) {
    super();
    
    this.config = {
      enableMonitoring: true,
      enableProfiling: false,
      enableMemoryTracking: true,
      enableCpuTracking: true,
      enableRenderTracking: true,
      enableAnalysisTracking: true,
      enableCacheTracking: true,
      enableLazyLoading: true,
      maxMemoryUsage: 100 * 1024 * 1024, // 100MB
      maxCpuUsage: 80, // 80%
      maxRenderTime: 16, // 16ms (60fps)
      maxAnalysisTime: 100, // 100ms
      minCacheHitRate: 70, // 70%
      monitoringInterval: 1000, // 1 second
      profilingInterval: 5000, // 5 seconds
      maxMetricsHistory: 1000,
      enableAlerts: true,
      alertThresholds: {
        memory: 80,
        cpu: 70,
        render: 20,
        analysis: 200,
        cache: 50
      },
      ...config
    };

    this.lazyLoadConfig = {
      enabled: true,
      preloadThreshold: 100, // 100px
      loadTimeout: 5000, // 5 seconds
      maxConcurrentLoads: 3,
      retryAttempts: 3,
      retryDelay: 1000, // 1 second
      cacheEnabled: true,
      cacheSize: 50,
      cacheTimeout: 300000, // 5 minutes
      ...lazyLoadConfig
    };

    this.cacheConfig = {
      enabled: true,
      maxSize: 50 * 1024 * 1024, // 50MB
      maxAge: 300000, // 5 minutes
      cleanupInterval: 60000, // 1 minute
      enableCompression: false,
      enableEncryption: false,
      strategy: 'lru',
      ...cacheConfig
    };

    this.initializeObservers();
  }

  private initializeObservers(): void {
    if (typeof window !== 'undefined' && 'PerformanceObserver' in window) {
      // Performance observer for render timing
      if (this.config.enableRenderTracking) {
        this.performanceObserver = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          for (const entry of entries) {
            if (entry.entryType === 'measure' && entry.name.includes('render')) {
              this.recordRenderTime(entry.duration);
            }
          }
        });
        this.performanceObserver.observe({ entryTypes: ['measure'] });
      }

      // Memory observer
      if (this.config.enableMemoryTracking) {
        this.memoryObserver = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          for (const entry of entries) {
            if (entry.entryType === 'memory') {
              this.recordMemoryUsage((entry as any).usedJSHeapSize, (entry as any).totalJSHeapSize);
            }
          }
        });
        this.memoryObserver.observe({ entryTypes: ['memory'] });
      }
    }
  }

  public startMonitoring(): void {
    if (this.isMonitoring) return;

    this.isMonitoring = true;
    this.emit('monitoringStarted');

    if (this.config.enableMonitoring) {
      this.monitoringInterval = setInterval(() => {
        this.collectMetrics();
      }, this.config.monitoringInterval);
    }

    if (this.config.enableProfiling) {
      this.profilingInterval = setInterval(() => {
        this.collectProfilingData();
      }, this.config.profilingInterval);
    }

    // Start cache cleanup
    if (this.cacheConfig.enabled) {
      setInterval(() => {
        this.cleanupCache();
      }, this.cacheConfig.cleanupInterval);
    }
  }

  public stopMonitoring(): void {
    if (!this.isMonitoring) return;

    this.isMonitoring = false;
    this.emit('monitoringStopped');

    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
    }

    if (this.profilingInterval) {
      clearInterval(this.profilingInterval);
      this.profilingInterval = null;
    }
  }

  private collectMetrics(): void {
    const metrics: PerformanceMetrics = {
      timestamp: Date.now(),
      memoryUsage: this.getMemoryUsage(),
      cpuUsage: this.getCpuUsage(),
      renderTime: this.getRenderTimeMetrics(),
      analysisTime: this.getAnalysisTimeMetrics(),
      cacheHitRate: this.getCacheHitRate(),
      lazyLoading: this.getLazyLoadingMetrics()
    };

    this.metrics.push(metrics);

    // Keep only recent metrics
    if (this.metrics.length > this.config.maxMetricsHistory) {
      this.metrics = this.metrics.slice(-this.config.maxMetricsHistory);
    }

    // Check for alerts
    if (this.config.enableAlerts) {
      this.checkAlerts(metrics);
    }

    this.emit('metricsCollected', metrics);
  }

  private collectProfilingData(): void {
    if (!this.isProfiling) return;

    const profile = {
      timestamp: Date.now(),
      memoryUsage: this.getMemoryUsage(),
      cpuUsage: this.getCpuUsage(),
      renderTimes: [...this.renderTimes],
      analysisTimes: [...this.analysisTimes],
      cacheStats: this.getCacheStats(),
      loadedModules: Array.from(this.loadedModules),
      loadingModules: Array.from(this.loadingModules)
    };

    this.emit('profileCollected', profile);
  }

  private getMemoryUsage(): { used: number; total: number; percentage: number } {
    if (typeof window !== 'undefined' && 'memory' in performance) {
      const memory = (performance as any).memory;
      return {
        used: memory.usedJSHeapSize,
        total: memory.totalJSHeapSize,
        percentage: (memory.usedJSHeapSize / memory.totalJSHeapSize) * 100
      };
    }
    return { used: 0, total: 0, percentage: 0 };
  }

  private getCpuUsage(): { average: number; peak: number; current: number } {
    // Simplified CPU usage estimation based on render times
    const recentRenderTimes = this.renderTimes.slice(-10);
    const average = recentRenderTimes.length > 0 
      ? recentRenderTimes.reduce((sum, time) => sum + time, 0) / recentRenderTimes.length 
      : 0;
    const peak = recentRenderTimes.length > 0 ? Math.max(...recentRenderTimes) : 0;
    const current = recentRenderTimes.length > 0 ? recentRenderTimes[recentRenderTimes.length - 1] : 0;

    return { average, peak, current };
  }

  private getRenderTimeMetrics(): { average: number; peak: number; current: number } {
    const average = this.renderTimes.length > 0 
      ? this.renderTimes.reduce((sum, time) => sum + time, 0) / this.renderTimes.length 
      : 0;
    const peak = this.renderTimes.length > 0 ? Math.max(...this.renderTimes) : 0;
    const current = this.renderTimes.length > 0 ? this.renderTimes[this.renderTimes.length - 1] : 0;

    return { average, peak, current };
  }

  private getAnalysisTimeMetrics(): { average: number; peak: number; current: number } {
    const average = this.analysisTimes.length > 0 
      ? this.analysisTimes.reduce((sum, time) => sum + time, 0) / this.analysisTimes.length 
      : 0;
    const peak = this.analysisTimes.length > 0 ? Math.max(...this.analysisTimes) : 0;
    const current = this.analysisTimes.length > 0 ? this.analysisTimes[this.analysisTimes.length - 1] : 0;

    return { average, peak, current };
  }

  private getCacheHitRate(): { average: number; current: number } {
    const total = this.cacheHits + this.cacheMisses;
    const current = total > 0 ? (this.cacheHits / total) * 100 : 0;
    
    // Calculate average over recent metrics
    const recentMetrics = this.metrics.slice(-10);
    const average = recentMetrics.length > 0 
      ? recentMetrics.reduce((sum, metric) => sum + metric.cacheHitRate.current, 0) / recentMetrics.length 
      : 0;

    return { average, current };
  }

  private getLazyLoadingMetrics(): { loadedModules: number; totalModules: number; loadingTime: number } {
    return {
      loadedModules: this.loadedModules.size,
      totalModules: this.loadedModules.size + this.loadingModules.size,
      loadingTime: 0 // This would be tracked per module
    };
  }

  private getCacheStats(): { size: number; entries: number; hitRate: number } {
    let totalSize = 0;
    for (const entry of this.cache.values()) {
      totalSize += entry.size;
    }

    const total = this.cacheHits + this.cacheMisses;
    const hitRate = total > 0 ? (this.cacheHits / total) * 100 : 0;

    return {
      size: totalSize,
      entries: this.cache.size,
      hitRate
    };
  }

  private recordMemoryUsage(used: number, total: number): void {
    // Memory usage is already handled by the observer
  }

  private recordRenderTime(time: number): void {
    this.renderTimes.push(time);
    
    // Keep only recent render times
    if (this.renderTimes.length > 100) {
      this.renderTimes = this.renderTimes.slice(-100);
    }
  }

  public recordAnalysisTime(time: number): void {
    this.analysisTimes.push(time);
    
    // Keep only recent analysis times
    if (this.analysisTimes.length > 100) {
      this.analysisTimes = this.analysisTimes.slice(-100);
    }
  }

  public recordCacheHit(): void {
    this.cacheHits++;
  }

  public recordCacheMiss(): void {
    this.cacheMisses++;
  }

  private checkAlerts(metrics: PerformanceMetrics): void {
    const thresholds = this.config.alertThresholds;

    if (metrics.memoryUsage.percentage > thresholds.memory) {
      this.emit('alert', {
        type: 'memory',
        level: 'warning',
        message: `High memory usage: ${metrics.memoryUsage.percentage.toFixed(1)}%`,
        value: metrics.memoryUsage.percentage,
        threshold: thresholds.memory
      });
    }

    if (metrics.cpuUsage.current > thresholds.cpu) {
      this.emit('alert', {
        type: 'cpu',
        level: 'warning',
        message: `High CPU usage: ${metrics.cpuUsage.current.toFixed(1)}%`,
        value: metrics.cpuUsage.current,
        threshold: thresholds.cpu
      });
    }

    if (metrics.renderTime.current > thresholds.render) {
      this.emit('alert', {
        type: 'render',
        level: 'warning',
        message: `Slow render time: ${metrics.renderTime.current.toFixed(1)}ms`,
        value: metrics.renderTime.current,
        threshold: thresholds.render
      });
    }

    if (metrics.analysisTime.current > thresholds.analysis) {
      this.emit('alert', {
        type: 'analysis',
        level: 'warning',
        message: `Slow analysis time: ${metrics.analysisTime.current.toFixed(1)}ms`,
        value: metrics.analysisTime.current,
        threshold: thresholds.analysis
      });
    }

    if (metrics.cacheHitRate.current < thresholds.cache) {
      this.emit('alert', {
        type: 'cache',
        level: 'warning',
        message: `Low cache hit rate: ${metrics.cacheHitRate.current.toFixed(1)}%`,
        value: metrics.cacheHitRate.current,
        threshold: thresholds.cache
      });
    }
  }

  // Lazy loading methods
  public async loadModule(moduleId: string, loader: () => Promise<any>): Promise<any> {
    if (!this.lazyLoadConfig.enabled) {
      return loader();
    }

    if (this.loadedModules.has(moduleId)) {
      return this.getFromCache(moduleId);
    }

    if (this.loadingModules.has(moduleId)) {
      // Wait for existing load to complete
      return new Promise((resolve, reject) => {
        const checkLoaded = () => {
          if (this.loadedModules.has(moduleId)) {
            resolve(this.getFromCache(moduleId));
          } else if (!this.loadingModules.has(moduleId)) {
            reject(new Error(`Module ${moduleId} failed to load`));
          } else {
            setTimeout(checkLoaded, 100);
          }
        };
        checkLoaded();
      });
    }

    if (this.loadingModules.size >= this.lazyLoadConfig.maxConcurrentLoads) {
      throw new Error('Maximum concurrent loads reached');
    }

    this.loadingModules.add(moduleId);

    try {
      const startTime = Date.now();
      const module = await Promise.race([
        loader(),
        new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Load timeout')), this.lazyLoadConfig.loadTimeout)
        )
      ]);

      const loadTime = Date.now() - startTime;
      
      this.loadedModules.add(moduleId);
      this.loadingModules.delete(moduleId);

      if (this.lazyLoadConfig.cacheEnabled) {
        this.setCache(moduleId, module, loadTime);
      }

      this.emit('moduleLoaded', { moduleId, loadTime });
      return module;
    } catch (error) {
      this.loadingModules.delete(moduleId);
      this.emit('moduleLoadFailed', { moduleId, error });
      throw error;
    }
  }

  public preloadModule(moduleId: string, loader: () => Promise<any>): void {
    if (!this.lazyLoadConfig.enabled || this.loadedModules.has(moduleId)) {
      return;
    }

    // Preload in background
    this.loadModule(moduleId, loader).catch(error => {
      console.warn(`Failed to preload module ${moduleId}:`, error);
    });
  }

  // Caching methods
  public setCache(key: string, data: any, size?: number): void {
    if (!this.cacheConfig.enabled) return;

    const entry = {
      data,
      timestamp: Date.now(),
      size: size || this.estimateSize(data)
    };

    this.cache.set(key, entry);

    // Check if cache needs cleanup
    if (this.getCacheSize() > this.cacheConfig.maxSize) {
      this.cleanupCache();
    }
  }

  public getFromCache(key: string): any {
    if (!this.cacheConfig.enabled) return null;

    const entry = this.cache.get(key);
    if (!entry) {
      this.recordCacheMiss();
      return null;
    }

    // Check if entry is expired
    if (Date.now() - entry.timestamp > this.cacheConfig.maxAge) {
      this.cache.delete(key);
      this.recordCacheMiss();
      return null;
    }

    this.recordCacheHit();
    return entry.data;
  }

  public clearCache(): void {
    this.cache.clear();
    this.cacheHits = 0;
    this.cacheMisses = 0;
    this.emit('cacheCleared');
  }

  private cleanupCache(): void {
    const now = Date.now();
    const entriesToDelete: string[] = [];

    for (const [key, entry] of this.cache.entries()) {
      if (now - entry.timestamp > this.cacheConfig.maxAge) {
        entriesToDelete.push(key);
      }
    }

    for (const key of entriesToDelete) {
      this.cache.delete(key);
    }

    // If still over size limit, remove oldest entries
    if (this.getCacheSize() > this.cacheConfig.maxSize) {
      const sortedEntries = Array.from(this.cache.entries())
        .sort((a, b) => a[1].timestamp - b[1].timestamp);

      for (const [key] of sortedEntries) {
        this.cache.delete(key);
        if (this.getCacheSize() <= this.cacheConfig.maxSize) {
          break;
        }
      }
    }

    this.emit('cacheCleanup', { deleted: entriesToDelete.length });
  }

  private getCacheSize(): number {
    let totalSize = 0;
    for (const entry of this.cache.values()) {
      totalSize += entry.size;
    }
    return totalSize;
  }

  private estimateSize(data: any): number {
    try {
      return JSON.stringify(data).length * 2; // Rough estimate
    } catch {
      return 1024; // Default size
    }
  }

  // Performance optimization methods
  public optimizePerformance(): void {
    // Clear old metrics
    if (this.metrics.length > this.config.maxMetricsHistory) {
      this.metrics = this.metrics.slice(-this.config.maxMetricsHistory);
    }

    // Clear old render times
    if (this.renderTimes.length > 100) {
      this.renderTimes = this.renderTimes.slice(-100);
    }

    // Clear old analysis times
    if (this.analysisTimes.length > 100) {
      this.analysisTimes = this.analysisTimes.slice(-100);
    }

    // Force garbage collection if available
    if (typeof window !== 'undefined' && 'gc' in window) {
      (window as any).gc();
    }

    this.emit('performanceOptimized');
  }

  public getMetrics(): PerformanceMetrics[] {
    return [...this.metrics];
  }

  public getLatestMetrics(): PerformanceMetrics | null {
    return this.metrics.length > 0 ? this.metrics[this.metrics.length - 1] : null;
  }

  public getPerformanceReport(): {
    summary: {
      averageMemoryUsage: number;
      averageCpuUsage: number;
      averageRenderTime: number;
      averageAnalysisTime: number;
      averageCacheHitRate: number;
      totalModulesLoaded: number;
    };
    recommendations: string[];
  } {
    const recentMetrics = this.metrics.slice(-10);
    
    if (recentMetrics.length === 0) {
      return {
        summary: {
          averageMemoryUsage: 0,
          averageCpuUsage: 0,
          averageRenderTime: 0,
          averageAnalysisTime: 0,
          averageCacheHitRate: 0,
          totalModulesLoaded: this.loadedModules.size
        },
        recommendations: []
      };
    }

    const summary = {
      averageMemoryUsage: recentMetrics.reduce((sum, m) => sum + m.memoryUsage.percentage, 0) / recentMetrics.length,
      averageCpuUsage: recentMetrics.reduce((sum, m) => sum + m.cpuUsage.average, 0) / recentMetrics.length,
      averageRenderTime: recentMetrics.reduce((sum, m) => sum + m.renderTime.average, 0) / recentMetrics.length,
      averageAnalysisTime: recentMetrics.reduce((sum, m) => sum + m.analysisTime.average, 0) / recentMetrics.length,
      averageCacheHitRate: recentMetrics.reduce((sum, m) => sum + m.cacheHitRate.average, 0) / recentMetrics.length,
      totalModulesLoaded: this.loadedModules.size
    };

    const recommendations: string[] = [];

    if (summary.averageMemoryUsage > 80) {
      recommendations.push('Consider reducing memory usage by clearing caches or optimizing data structures');
    }

    if (summary.averageCpuUsage > 70) {
      recommendations.push('Consider optimizing CPU-intensive operations or reducing analysis frequency');
    }

    if (summary.averageRenderTime > 16) {
      recommendations.push('Consider optimizing rendering performance or reducing visual complexity');
    }

    if (summary.averageAnalysisTime > 100) {
      recommendations.push('Consider optimizing code analysis or reducing analysis depth');
    }

    if (summary.averageCacheHitRate < 70) {
      recommendations.push('Consider improving cache strategy or increasing cache size');
    }

    return { summary, recommendations };
  }

  public destroy(): void {
    this.stopMonitoring();
    
    if (this.performanceObserver) {
      this.performanceObserver.disconnect();
    }
    
    if (this.memoryObserver) {
      this.memoryObserver.disconnect();
    }

    this.clearCache();
    this.removeAllListeners();
  }
}
