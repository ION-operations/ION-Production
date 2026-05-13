/**
 * Lazy Loading Service
 * 
 * Provides comprehensive lazy loading functionality for the Advanced Monaco Editor
 * including:
 * - Dynamic module loading
 * - Component lazy loading
 * - Resource lazy loading
 * - Preloading strategies
 * - Loading state management
 * - Error handling and retry logic
 */

import { EventEmitter } from 'events';

export interface LazyLoadItem {
  id: string;
  type: 'component' | 'module' | 'resource' | 'service';
  loader: () => Promise<any>;
  dependencies?: string[];
  priority: 'high' | 'medium' | 'low';
  preload: boolean;
  retryAttempts: number;
  timeout: number;
  cache: boolean;
  metadata?: Record<string, any>;
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
  enablePreloading: boolean;
  enableIntersectionObserver: boolean;
  enableResourceHints: boolean;
  enableServiceWorker: boolean;
}

export interface LoadingState {
  id: string;
  status: 'idle' | 'loading' | 'loaded' | 'error' | 'retrying';
  progress: number; // 0-100
  startTime: number;
  endTime?: number;
  error?: Error;
  retryCount: number;
  dependencies: string[];
  metadata?: Record<string, any>;
}

export class LazyLoadingService extends EventEmitter {
  private config: LazyLoadConfig;
  private items: Map<string, LazyLoadItem> = new Map();
  private loadingStates: Map<string, LoadingState> = new Map();
  private loadedItems: Map<string, any> = new Map();
  private loadingQueue: string[] = [];
  private currentlyLoading: Set<string> = new Set();
  private intersectionObserver: IntersectionObserver | null = null;
  private preloadQueue: string[] = [];
  private retryTimeouts: Map<string, NodeJS.Timeout> = new Map();

  constructor(config: Partial<LazyLoadConfig> = {}) {
    super();
    
    this.config = {
      enabled: true,
      preloadThreshold: 100, // 100px
      loadTimeout: 5000, // 5 seconds
      maxConcurrentLoads: 3,
      retryAttempts: 3,
      retryDelay: 1000, // 1 second
      cacheEnabled: true,
      cacheSize: 50,
      cacheTimeout: 300000, // 5 minutes
      enablePreloading: true,
      enableIntersectionObserver: true,
      enableResourceHints: true,
      enableServiceWorker: false,
      ...config
    };

    this.initializeIntersectionObserver();
  }

  private initializeIntersectionObserver(): void {
    if (typeof window !== 'undefined' && 'IntersectionObserver' in window && this.config.enableIntersectionObserver) {
      this.intersectionObserver = new IntersectionObserver(
        (entries) => {
          entries.forEach(entry => {
            if (entry.isIntersecting) {
              const itemId = entry.target.getAttribute('data-lazy-id');
              if (itemId) {
                this.loadItem(itemId);
              }
            }
          });
        },
        {
          rootMargin: `${this.config.preloadThreshold}px`
        }
      );
    }
  }

  public registerItem(item: LazyLoadItem): void {
    this.items.set(item.id, item);
    this.loadingStates.set(item.id, {
      id: item.id,
      status: 'idle',
      progress: 0,
      startTime: 0,
      retryCount: 0,
      dependencies: item.dependencies || [],
      metadata: item.metadata
    });

    this.emit('itemRegistered', item);

    // Add to preload queue if enabled
    if (item.preload && this.config.enablePreloading) {
      this.preloadQueue.push(item.id);
      this.processPreloadQueue();
    }
  }

  public unregisterItem(itemId: string): void {
    const item = this.items.get(itemId);
    if (!item) return;

    // Cancel any ongoing loading
    this.cancelLoading(itemId);

    // Remove from all collections
    this.items.delete(itemId);
    this.loadingStates.delete(itemId);
    this.loadedItems.delete(itemId);
    this.loadingQueue = this.loadingQueue.filter(id => id !== itemId);
    this.currentlyLoading.delete(itemId);
    this.preloadQueue = this.preloadQueue.filter(id => id !== itemId);

    // Clear retry timeout
    const retryTimeout = this.retryTimeouts.get(itemId);
    if (retryTimeout) {
      clearTimeout(retryTimeout);
      this.retryTimeouts.delete(itemId);
    }

    this.emit('itemUnregistered', itemId);
  }

  public async loadItem(itemId: string): Promise<any> {
    if (!this.config.enabled) {
      throw new Error('Lazy loading is disabled');
    }

    const item = this.items.get(itemId);
    if (!item) {
      throw new Error(`Item ${itemId} not found`);
    }

    const state = this.loadingStates.get(itemId);
    if (!state) {
      throw new Error(`Loading state for ${itemId} not found`);
    }

    // Check if already loaded
    if (this.loadedItems.has(itemId)) {
      return this.loadedItems.get(itemId);
    }

    // Check if currently loading
    if (this.currentlyLoading.has(itemId)) {
      return new Promise((resolve, reject) => {
        const checkLoaded = () => {
          if (this.loadedItems.has(itemId)) {
            resolve(this.loadedItems.get(itemId));
          } else if (!this.currentlyLoading.has(itemId) && state.status === 'error') {
            reject(state.error);
          } else {
            setTimeout(checkLoaded, 100);
          }
        };
        checkLoaded();
      });
    }

    // Check dependencies
    if (item.dependencies && item.dependencies.length > 0) {
      const dependencyResults = await Promise.allSettled(
        item.dependencies.map(depId => this.loadItem(depId))
      );

      const failedDependencies = dependencyResults
        .map((result, index) => ({ result, depId: item.dependencies![index] }))
        .filter(({ result }) => result.status === 'rejected');

      if (failedDependencies.length > 0) {
        const error = new Error(`Dependencies failed: ${failedDependencies.map(({ depId }) => depId).join(', ')}`);
        this.updateLoadingState(itemId, { status: 'error', error });
        throw error;
      }
    }

    // Check concurrent load limit
    if (this.currentlyLoading.size >= this.config.maxConcurrentLoads) {
      this.loadingQueue.push(itemId);
      return new Promise((resolve, reject) => {
        const checkQueue = () => {
          if (this.currentlyLoading.size < this.config.maxConcurrentLoads) {
            this.processLoadingQueue();
          }
          setTimeout(checkQueue, 100);
        };
        checkQueue();
      });
    }

    return this.executeLoad(itemId);
  }

  private async executeLoad(itemId: string): Promise<any> {
    const item = this.items.get(itemId)!;
    const state = this.loadingStates.get(itemId)!;

    this.currentlyLoading.add(itemId);
    this.updateLoadingState(itemId, {
      status: 'loading',
      progress: 0,
      startTime: Date.now()
    });

    try {
      // Create loading promise with timeout
      const loadPromise = item.loader();
      const timeoutPromise = new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Load timeout')), item.timeout || this.config.loadTimeout)
      );

      const result = await Promise.race([loadPromise, timeoutPromise]);

      // Update progress
      this.updateLoadingState(itemId, { progress: 100 });

      // Store loaded item
      this.loadedItems.set(itemId, result);

      // Update state
      this.updateLoadingState(itemId, {
        status: 'loaded',
        endTime: Date.now(),
        progress: 100
      });

      this.currentlyLoading.delete(itemId);
      this.emit('itemLoaded', { itemId, result, loadTime: Date.now() - state.startTime });

      // Process loading queue
      this.processLoadingQueue();

      return result;
    } catch (error) {
      this.currentlyLoading.delete(itemId);
      
      const newRetryCount = state.retryCount + 1;
      const maxRetries = item.retryAttempts || this.config.retryAttempts;

      if (newRetryCount <= maxRetries) {
        this.updateLoadingState(itemId, {
          status: 'retrying',
          error: error as Error,
          retryCount: newRetryCount
        });

        // Schedule retry
        const retryTimeout = setTimeout(() => {
          this.retryTimeouts.delete(itemId);
          this.loadItem(itemId).catch(() => {
            // Retry failed, will be handled by the retry logic
          });
        }, this.config.retryDelay);

        this.retryTimeouts.set(itemId, retryTimeout);
        this.emit('itemRetrying', { itemId, retryCount: newRetryCount, error });
      } else {
        this.updateLoadingState(itemId, {
          status: 'error',
          error: error as Error,
          retryCount: newRetryCount
        });
        this.emit('itemLoadFailed', { itemId, error, retryCount: newRetryCount });
      }

      throw error;
    }
  }

  private processLoadingQueue(): void {
    while (this.loadingQueue.length > 0 && this.currentlyLoading.size < this.config.maxConcurrentLoads) {
      const itemId = this.loadingQueue.shift()!;
      this.loadItem(itemId).catch(error => {
        console.warn(`Failed to load queued item ${itemId}:`, error);
      });
    }
  }

  private processPreloadQueue(): void {
    if (!this.config.enablePreloading) return;

    // Process preload queue with lower priority
    const preloadItem = this.preloadQueue.shift();
    if (preloadItem) {
      this.loadItem(preloadItem).catch(error => {
        console.warn(`Failed to preload item ${preloadItem}:`, error);
      });
    }
  }

  private updateLoadingState(itemId: string, updates: Partial<LoadingState>): void {
    const state = this.loadingStates.get(itemId);
    if (state) {
      Object.assign(state, updates);
      this.emit('loadingStateChanged', { itemId, state: { ...state } });
    }
  }

  public cancelLoading(itemId: string): void {
    const state = this.loadingStates.get(itemId);
    if (!state || state.status !== 'loading') return;

    // Clear retry timeout
    const retryTimeout = this.retryTimeouts.get(itemId);
    if (retryTimeout) {
      clearTimeout(retryTimeout);
      this.retryTimeouts.delete(itemId);
    }

    this.currentlyLoading.delete(itemId);
    this.loadingQueue = this.loadingQueue.filter(id => id !== itemId);

    this.updateLoadingState(itemId, {
      status: 'idle',
      progress: 0,
      startTime: 0,
      endTime: undefined,
      error: undefined
    });

    this.emit('loadingCancelled', itemId);
  }

  public preloadItem(itemId: string): void {
    const item = this.items.get(itemId);
    if (!item || this.loadedItems.has(itemId) || this.currentlyLoading.has(itemId)) {
      return;
    }

    if (this.config.enablePreloading) {
      this.preloadQueue.push(itemId);
      this.processPreloadQueue();
    }
  }

  public preloadItems(itemIds: string[]): void {
    itemIds.forEach(itemId => this.preloadItem(itemId));
  }

  public getLoadingState(itemId: string): LoadingState | undefined {
    return this.loadingStates.get(itemId);
  }

  public getAllLoadingStates(): LoadingState[] {
    return Array.from(this.loadingStates.values());
  }

  public getLoadedItem(itemId: string): any {
    return this.loadedItems.get(itemId);
  }

  public getAllLoadedItems(): Map<string, any> {
    return new Map(this.loadedItems);
  }

  public isLoaded(itemId: string): boolean {
    return this.loadedItems.has(itemId);
  }

  public isLoading(itemId: string): boolean {
    return this.currentlyLoading.has(itemId);
  }

  public getLoadingProgress(): { total: number; loaded: number; loading: number; failed: number } {
    const states = Array.from(this.loadingStates.values());
    return {
      total: states.length,
      loaded: states.filter(s => s.status === 'loaded').length,
      loading: states.filter(s => s.status === 'loading').length,
      failed: states.filter(s => s.status === 'error').length
    };
  }

  public getLoadingStats(): {
    averageLoadTime: number;
    totalLoads: number;
    successfulLoads: number;
    failedLoads: number;
    retryCount: number;
  } {
    const states = Array.from(this.loadingStates.values());
    const loadedStates = states.filter(s => s.status === 'loaded' && s.endTime);
    const failedStates = states.filter(s => s.status === 'error');

    const averageLoadTime = loadedStates.length > 0
      ? loadedStates.reduce((sum, s) => sum + (s.endTime! - s.startTime), 0) / loadedStates.length
      : 0;

    const retryCount = states.reduce((sum, s) => sum + s.retryCount, 0);

    return {
      averageLoadTime,
      totalLoads: states.length,
      successfulLoads: loadedStates.length,
      failedLoads: failedStates.length,
      retryCount
    };
  }

  public clearCache(): void {
    this.loadedItems.clear();
    this.emit('cacheCleared');
  }

  public reset(): void {
    this.cancelAllLoading();
    this.clearCache();
    this.loadingStates.clear();
    this.loadingQueue = [];
    this.preloadQueue = [];
    this.emit('reset');
  }

  private cancelAllLoading(): void {
    // Cancel all retry timeouts
    for (const timeout of this.retryTimeouts.values()) {
      clearTimeout(timeout);
    }
    this.retryTimeouts.clear();

    // Cancel all currently loading items
    for (const itemId of this.currentlyLoading) {
      this.cancelLoading(itemId);
    }
  }

  public destroy(): void {
    this.cancelAllLoading();
    this.clearCache();
    
    if (this.intersectionObserver) {
      this.intersectionObserver.disconnect();
    }

    this.removeAllListeners();
  }
}
