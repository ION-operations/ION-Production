/**
 * Lazy Loading Service Tests
 * 
 * Comprehensive unit tests for the LazyLoadingService class
 */

import { LazyLoadingService, LazyLoadingConfig, LazyLoadingItem, LazyLoadingMetrics } from '../src/services/LazyLoadingService';

describe('LazyLoadingService', () => {
  let lazyLoadingService: LazyLoadingService;

  beforeEach(() => {
    lazyLoadingService = new LazyLoadingService({
      enabled: true,
      preloadThreshold: 100,
      loadTimeout: 5000,
      maxConcurrentLoads: 3,
      retryAttempts: 3,
      retryDelay: 1000,
      cacheEnabled: true,
      cacheSize: 50,
      cacheTimeout: 300000, // 5 minutes
      enablePreloading: true,
      enableIntersectionObserver: true,
      enableResourceHints: true,
      enableServiceWorker: false
    });
  });

  afterEach(() => {
    lazyLoadingService.destroy();
  });

  describe('Initialization', () => {
    it('should initialize with default configuration', () => {
      const defaultService = new LazyLoadingService();
      expect(defaultService).toBeDefined();
      expect(defaultService.getConfig().enabled).toBe(true);
      expect(defaultService.getConfig().preloadThreshold).toBe(100);
      expect(defaultService.getConfig().loadTimeout).toBe(5000);
      expect(defaultService.getConfig().maxConcurrentLoads).toBe(3);
      expect(defaultService.getConfig().retryAttempts).toBe(3);
      expect(defaultService.getConfig().retryDelay).toBe(1000);
      expect(defaultService.getConfig().cacheEnabled).toBe(true);
      expect(defaultService.getConfig().cacheSize).toBe(50);
      expect(defaultService.getConfig().cacheTimeout).toBe(300000);
      expect(defaultService.getConfig().enablePreloading).toBe(true);
      expect(defaultService.getConfig().enableIntersectionObserver).toBe(true);
      expect(defaultService.getConfig().enableResourceHints).toBe(true);
      expect(defaultService.getConfig().enableServiceWorker).toBe(false);
      defaultService.destroy();
    });

    it('should initialize with custom configuration', () => {
      const customConfig: Partial<LazyLoadingConfig> = {
        enabled: false,
        preloadThreshold: 200,
        loadTimeout: 10000,
        maxConcurrentLoads: 5,
        retryAttempts: 5,
        retryDelay: 2000,
        cacheEnabled: false,
        cacheSize: 100,
        cacheTimeout: 600000,
        enablePreloading: false,
        enableIntersectionObserver: false,
        enableResourceHints: false,
        enableServiceWorker: true
      };

      const customService = new LazyLoadingService(customConfig);
      expect(customService.getConfig().enabled).toBe(false);
      expect(customService.getConfig().preloadThreshold).toBe(200);
      expect(customService.getConfig().loadTimeout).toBe(10000);
      expect(customService.getConfig().maxConcurrentLoads).toBe(5);
      expect(customService.getConfig().retryAttempts).toBe(5);
      expect(customService.getConfig().retryDelay).toBe(2000);
      expect(customService.getConfig().cacheEnabled).toBe(false);
      expect(customService.getConfig().cacheSize).toBe(100);
      expect(customService.getConfig().cacheTimeout).toBe(600000);
      expect(customService.getConfig().enablePreloading).toBe(false);
      expect(customService.getConfig().enableIntersectionObserver).toBe(false);
      expect(customService.getConfig().enableResourceHints).toBe(false);
      expect(customService.getConfig().enableServiceWorker).toBe(true);
      customService.destroy();
    });
  });

  describe('Item Management', () => {
    it('should register lazy loading item', () => {
      const item: LazyLoadingItem = {
        id: 'test-item',
        type: 'image',
        src: 'https://example.com/image.jpg',
        priority: 'high',
        preload: true,
        cache: true,
        retry: true,
        timeout: 5000,
        onLoad: jest.fn(),
        onError: jest.fn(),
        onProgress: jest.fn()
      };

      lazyLoadingService.registerItem(item);
      const items = lazyLoadingService.getItems();
      expect(items).toHaveLength(1);
      expect(items[0].id).toBe('test-item');
      expect(items[0].type).toBe('image');
      expect(items[0].src).toBe('https://example.com/image.jpg');
      expect(items[0].priority).toBe('high');
      expect(items[0].preload).toBe(true);
      expect(items[0].cache).toBe(true);
      expect(items[0].retry).toBe(true);
      expect(items[0].timeout).toBe(5000);
      expect(items[0].onLoad).toBeDefined();
      expect(items[0].onError).toBeDefined();
      expect(items[0].onProgress).toBeDefined();
    });

    it('should unregister lazy loading item', () => {
      const item: LazyLoadingItem = {
        id: 'test-item',
        type: 'image',
        src: 'https://example.com/image.jpg',
        priority: 'high',
        preload: true,
        cache: true,
        retry: true,
        timeout: 5000,
        onLoad: jest.fn(),
        onError: jest.fn(),
        onProgress: jest.fn()
      };

      lazyLoadingService.registerItem(item);
      expect(lazyLoadingService.getItems()).toHaveLength(1);

      lazyLoadingService.unregisterItem('test-item');
      expect(lazyLoadingService.getItems()).toHaveLength(0);
    });

    it('should get item by id', () => {
      const item: LazyLoadingItem = {
        id: 'test-item',
        type: 'image',
        src: 'https://example.com/image.jpg',
        priority: 'high',
        preload: true,
        cache: true,
        retry: true,
        timeout: 5000,
        onLoad: jest.fn(),
        onError: jest.fn(),
        onProgress: jest.fn()
      };

      lazyLoadingService.registerItem(item);
      const retrievedItem = lazyLoadingService.getItem('test-item');
      expect(retrievedItem).toBeDefined();
      expect(retrievedItem?.id).toBe('test-item');
      expect(retrievedItem?.type).toBe('image');
      expect(retrievedItem?.src).toBe('https://example.com/image.jpg');
      expect(retrievedItem?.priority).toBe('high');
      expect(retrievedItem?.preload).toBe(true);
      expect(retrievedItem?.cache).toBe(true);
      expect(retrievedItem?.retry).toBe(true);
      expect(retrievedItem?.timeout).toBe(5000);
      expect(retrievedItem?.onLoad).toBeDefined();
      expect(retrievedItem?.onError).toBeDefined();
      expect(retrievedItem?.onProgress).toBeDefined();
    });

    it('should get items by type', () => {
      const item1: LazyLoadingItem = {
        id: 'test-item-1',
        type: 'image',
        src: 'https://example.com/image1.jpg',
        priority: 'high',
        preload: true,
        cache: true,
        retry: true,
        timeout: 5000,
        onLoad: jest.fn(),
        onError: jest.fn(),
        onProgress: jest.fn()
      };

      const item2: LazyLoadingItem = {
        id: 'test-item-2',
        type: 'script',
        src: 'https://example.com/script.js',
        priority: 'medium',
        preload: false,
        cache: true,
        retry: true,
        timeout: 10000,
        onLoad: jest.fn(),
        onError: jest.fn(),
        onProgress: jest.fn()
      };

      lazyLoadingService.registerItem(item1);
      lazyLoadingService.registerItem(item2);

      const imageItems = lazyLoadingService.getItemsByType('image');
      expect(imageItems).toHaveLength(1);
      expect(imageItems[0].id).toBe('test-item-1');

      const scriptItems = lazyLoadingService.getItemsByType('script');
      expect(scriptItems).toHaveLength(1);
      expect(scriptItems[0].id).toBe('test-item-2');
    });

    it('should get items by priority', () => {
      const item1: LazyLoadingItem = {
        id: 'test-item-1',
        type: 'image',
        src: 'https://example.com/image1.jpg',
        priority: 'high',
        preload: true,
        cache: true,
        retry: true,
        timeout: 5000,
        onLoad: jest.fn(),
        onError: jest.fn(),
        onProgress: jest.fn()
      };

      const item2: LazyLoadingItem = {
        id: 'test-item-2',
        type: 'image',
        src: 'https://example.com/image2.jpg',
        priority: 'medium',
        preload: false,
        cache: true,
        retry: true,
        timeout: 5000,
        onLoad: jest.fn(),
        onError: jest.fn(),
        onProgress: jest.fn()
      };

      lazyLoadingService.registerItem(item1);
      lazyLoadingService.registerItem(item2);

      const highPriorityItems = lazyLoadingService.getItemsByPriority('high');
      expect(highPriorityItems).toHaveLength(1);
      expect(highPriorityItems[0].id).toBe('test-item-1');

      const mediumPriorityItems = lazyLoadingService.getItemsByPriority('medium');
      expect(mediumPriorityItems).toHaveLength(1);
      expect(mediumPriorityItems[0].id).toBe('test-item-2');
    });

    it('should get items by status', () => {
      const item: LazyLoadingItem = {
        id: 'test-item',
        type: 'image',
        src: 'https://example.com/image.jpg',
        priority: 'high',
        preload: true,
        cache: true,
        retry: true,
        timeout: 5000,
        onLoad: jest.fn(),
        onError: jest.fn(),
        onProgress: jest.fn()
      };

      lazyLoadingService.registerItem(item);
      const pendingItems = lazyLoadingService.getItemsByStatus('pending');
      expect(pendingItems).toHaveLength(1);
      expect(pendingItems[0].id).toBe('test-item');
    });

    it('should update item', () => {
      const item: LazyLoadingItem = {
        id: 'test-item',
        type: 'image',
        src: 'https://example.com/image.jpg',
        priority: 'high',
        preload: true,
        cache: true,
        retry: true,
        timeout: 5000,
        onLoad: jest.fn(),
        onError: jest.fn(),
        onProgress: jest.fn()
      };

      lazyLoadingService.registerItem(item);
      expect(lazyLoadingService.getItems()).toHaveLength(1);

      const updatedItem = { ...item, priority: 'medium' as const, preload: false };
      lazyLoadingService.updateItem('test-item', updatedItem);
      const items = lazyLoadingService.getItems();
      expect(items[0].priority).toBe('medium');
      expect(items[0].preload).toBe(false);
    });
  });

  describe('Loading', () => {
    it('should load item', async () => {
      const item: LazyLoadingItem = {
        id: 'test-item',
        type: 'image',
        src: 'https://example.com/image.jpg',
        priority: 'high',
        preload: true,
        cache: true,
        retry: true,
        timeout: 5000,
        onLoad: jest.fn(),
        onError: jest.fn(),
        onProgress: jest.fn()
      };

      lazyLoadingService.registerItem(item);
      const result = await lazyLoadingService.loadItem('test-item');
      expect(result).toBeDefined();
      expect(result.id).toBe('test-item');
      expect(result.status).toBe('loaded');
      expect(result.loadTime).toBeGreaterThan(0);
      expect(result.retryCount).toBe(0);
      expect(result.error).toBeUndefined();
    });

    it('should load item with error', async () => {
      const item: LazyLoadingItem = {
        id: 'test-item',
        type: 'image',
        src: 'https://invalid-url.com/image.jpg',
        priority: 'high',
        preload: true,
        cache: true,
        retry: true,
        timeout: 5000,
        onLoad: jest.fn(),
        onError: jest.fn(),
        onProgress: jest.fn()
      };

      lazyLoadingService.registerItem(item);
      const result = await lazyLoadingService.loadItem('test-item');
      expect(result).toBeDefined();
      expect(result.id).toBe('test-item');
      expect(result.status).toBe('error');
      expect(result.loadTime).toBeGreaterThan(0);
      expect(result.retryCount).toBe(0);
      expect(result.error).toBeDefined();
    });

    it('should load item with retry', async () => {
      const item: LazyLoadingItem = {
        id: 'test-item',
        type: 'image',
        src: 'https://invalid-url.com/image.jpg',
        priority: 'high',
        preload: true,
        cache: true,
        retry: true,
        timeout: 5000,
        onLoad: jest.fn(),
        onError: jest.fn(),
        onProgress: jest.fn()
      };

      lazyLoadingService.registerItem(item);
      const result = await lazyLoadingService.loadItem('test-item');
      expect(result).toBeDefined();
      expect(result.id).toBe('test-item');
      expect(result.status).toBe('error');
      expect(result.loadTime).toBeGreaterThan(0);
      expect(result.retryCount).toBe(0);
      expect(result.error).toBeDefined();
    });

    it('should load item with timeout', async () => {
      const item: LazyLoadingItem = {
        id: 'test-item',
        type: 'image',
        src: 'https://example.com/image.jpg',
        priority: 'high',
        preload: true,
        cache: true,
        retry: true,
        timeout: 100, // Very short timeout
        onLoad: jest.fn(),
        onError: jest.fn(),
        onProgress: jest.fn()
      };

      lazyLoadingService.registerItem(item);
      const result = await lazyLoadingService.loadItem('test-item');
      expect(result).toBeDefined();
      expect(result.id).toBe('test-item');
      expect(result.status).toBe('timeout');
      expect(result.loadTime).toBeGreaterThan(0);
      expect(result.retryCount).toBe(0);
      expect(result.error).toBeDefined();
    });

    it('should load item with progress', async () => {
      const item: LazyLoadingItem = {
        id: 'test-item',
        type: 'image',
        src: 'https://example.com/image.jpg',
        priority: 'high',
        preload: true,
        cache: true,
        retry: true,
        timeout: 5000,
        onLoad: jest.fn(),
        onError: jest.fn(),
        onProgress: jest.fn()
      };

      lazyLoadingService.registerItem(item);
      const result = await lazyLoadingService.loadItem('test-item');
      expect(result).toBeDefined();
      expect(result.id).toBe('test-item');
      expect(result.status).toBe('loaded');
      expect(result.loadTime).toBeGreaterThan(0);
      expect(result.retryCount).toBe(0);
      expect(result.error).toBeUndefined();
    });

    it('should load item with custom options', async () => {
      const item: LazyLoadingItem = {
        id: 'test-item',
        type: 'image',
        src: 'https://example.com/image.jpg',
        priority: 'high',
        preload: true,
        cache: true,
        retry: true,
        timeout: 5000,
        onLoad: jest.fn(),
        onError: jest.fn(),
        onProgress: jest.fn()
      };

      lazyLoadingService.registerItem(item);
      const result = await lazyLoadingService.loadItem('test-item', {
        enableCaching: false,
        enableRetry: false,
        enableTimeout: false,
        enableProgress: false,
        maxConcurrentLoads: 1,
        retryAttempts: 1,
        retryDelay: 500,
        loadTimeout: 1000
      });
      expect(result).toBeDefined();
      expect(result.id).toBe('test-item');
      expect(result.status).toBe('loaded');
      expect(result.loadTime).toBeGreaterThan(0);
      expect(result.retryCount).toBe(0);
      expect(result.error).toBeUndefined();
    });
  });

  describe('Batch Loading', () => {
    it('should load multiple items', async () => {
      const item1: LazyLoadingItem = {
        id: 'test-item-1',
        type: 'image',
        src: 'https://example.com/image1.jpg',
        priority: 'high',
        preload: true,
        cache: true,
        retry: true,
        timeout: 5000,
        onLoad: jest.fn(),
        onError: jest.fn(),
        onProgress: jest.fn()
      };

      const item2: LazyLoadingItem = {
        id: 'test-item-2',
        type: 'image',
        src: 'https://example.com/image2.jpg',
        priority: 'medium',
        preload: false,
        cache: true,
        retry: true,
        timeout: 5000,
        onLoad: jest.fn(),
        onError: jest.fn(),
        onProgress: jest.fn()
      };

      lazyLoadingService.registerItem(item1);
      lazyLoadingService.registerItem(item2);

      const results = await lazyLoadingService.loadItems(['test-item-1', 'test-item-2']);
      expect(results).toHaveLength(2);
      expect(results[0].id).toBe('test-item-1');
      expect(results[0].status).toBe('loaded');
      expect(results[1].id).toBe('test-item-2');
      expect(results[1].status).toBe('loaded');
    });

    it('should load multiple items with errors', async () => {
      const item1: LazyLoadingItem = {
        id: 'test-item-1',
        type: 'image',
        src: 'https://example.com/image1.jpg',
        priority: 'high',
        preload: true,
        cache: true,
        retry: true,
        timeout: 5000,
        onLoad: jest.fn(),
        onError: jest.fn(),
        onProgress: jest.fn()
      };

      const item2: LazyLoadingItem = {
        id: 'test-item-2',
        type: 'image',
        src: 'https://invalid-url.com/image2.jpg',
        priority: 'medium',
        preload: false,
        cache: true,
        retry: true,
        timeout: 5000,
        onLoad: jest.fn(),
        onError: jest.fn(),
        onProgress: jest.fn()
      };

      lazyLoadingService.registerItem(item1);
      lazyLoadingService.registerItem(item2);

      const results = await lazyLoadingService.loadItems(['test-item-1', 'test-item-2']);
      expect(results).toHaveLength(2);
      expect(results[0].id).toBe('test-item-1');
      expect(results[0].status).toBe('loaded');
      expect(results[1].id).toBe('test-item-2');
      expect(results[1].status).toBe('error');
    });

    it('should load multiple items with custom options', async () => {
      const item1: LazyLoadingItem = {
        id: 'test-item-1',
        type: 'image',
        src: 'https://example.com/image1.jpg',
        priority: 'high',
        preload: true,
        cache: true,
        retry: true,
        timeout: 5000,
        onLoad: jest.fn(),
        onError: jest.fn(),
        onProgress: jest.fn()
      };

      const item2: LazyLoadingItem = {
        id: 'test-item-2',
        type: 'image',
        src: 'https://example.com/image2.jpg',
        priority: 'medium',
        preload: false,
        cache: true,
        retry: true,
        timeout: 5000,
        onLoad: jest.fn(),
        onError: jest.fn(),
        onProgress: jest.fn()
      };

      lazyLoadingService.registerItem(item1);
      lazyLoadingService.registerItem(item2);

      const results = await lazyLoadingService.loadItems(['test-item-1', 'test-item-2'], {
        enableCaching: false,
        enableRetry: false,
        enableTimeout: false,
        enableProgress: false,
        maxConcurrentLoads: 1,
        retryAttempts: 1,
        retryDelay: 500,
        loadTimeout: 1000
      });
      expect(results).toHaveLength(2);
      expect(results[0].id).toBe('test-item-1');
      expect(results[0].status).toBe('loaded');
      expect(results[1].id).toBe('test-item-2');
      expect(results[1].status).toBe('loaded');
    });
  });

  describe('Preloading', () => {
    it('should preload items', async () => {
      const item1: LazyLoadingItem = {
        id: 'test-item-1',
        type: 'image',
        src: 'https://example.com/image1.jpg',
        priority: 'high',
        preload: true,
        cache: true,
        retry: true,
        timeout: 5000,
        onLoad: jest.fn(),
        onError: jest.fn(),
        onProgress: jest.fn()
      };

      const item2: LazyLoadingItem = {
        id: 'test-item-2',
        type: 'image',
        src: 'https://example.com/image2.jpg',
        priority: 'medium',
        preload: false,
        cache: true,
        retry: true,
        timeout: 5000,
        onLoad: jest.fn(),
        onError: jest.fn(),
        onProgress: jest.fn()
      };

      lazyLoadingService.registerItem(item1);
      lazyLoadingService.registerItem(item2);

      const results = await lazyLoadingService.preloadItems();
      expect(results).toHaveLength(1);
      expect(results[0].id).toBe('test-item-1');
      expect(results[0].status).toBe('loaded');
    });

    it('should preload items with custom options', async () => {
      const item1: LazyLoadingItem = {
        id: 'test-item-1',
        type: 'image',
        src: 'https://example.com/image1.jpg',
        priority: 'high',
        preload: true,
        cache: true,
        retry: true,
        timeout: 5000,
        onLoad: jest.fn(),
        onError: jest.fn(),
        onProgress: jest.fn()
      };

      const item2: LazyLoadingItem = {
        id: 'test-item-2',
        type: 'image',
        src: 'https://example.com/image2.jpg',
        priority: 'medium',
        preload: false,
        cache: true,
        retry: true,
        timeout: 5000,
        onLoad: jest.fn(),
        onError: jest.fn(),
        onProgress: jest.fn()
      };

      lazyLoadingService.registerItem(item1);
      lazyLoadingService.registerItem(item2);

      const results = await lazyLoadingService.preloadItems({
        enableCaching: false,
        enableRetry: false,
        enableTimeout: false,
        enableProgress: false,
        maxConcurrentLoads: 1,
        retryAttempts: 1,
        retryDelay: 500,
        loadTimeout: 1000
      });
      expect(results).toHaveLength(1);
      expect(results[0].id).toBe('test-item-1');
      expect(results[0].status).toBe('loaded');
    });
  });

  describe('Caching', () => {
    it('should cache loaded items', async () => {
      const item: LazyLoadingItem = {
        id: 'test-item',
        type: 'image',
        src: 'https://example.com/image.jpg',
        priority: 'high',
        preload: true,
        cache: true,
        retry: true,
        timeout: 5000,
        onLoad: jest.fn(),
        onError: jest.fn(),
        onProgress: jest.fn()
      };

      lazyLoadingService.registerItem(item);
      const result1 = await lazyLoadingService.loadItem('test-item');
      expect(result1.status).toBe('loaded');

      const result2 = await lazyLoadingService.loadItem('test-item');
      expect(result2.status).toBe('loaded');
      expect(result2.loadTime).toBeLessThan(result1.loadTime); // Should be faster due to cache
    });

    it('should not cache loaded items when disabled', async () => {
      const service = new LazyLoadingService({ cacheEnabled: false });
      const item: LazyLoadingItem = {
        id: 'test-item',
        type: 'image',
        src: 'https://example.com/image.jpg',
        priority: 'high',
        preload: true,
        cache: false,
        retry: true,
        timeout: 5000,
        onLoad: jest.fn(),
        onError: jest.fn(),
        onProgress: jest.fn()
      };

      service.registerItem(item);
      const result1 = await service.loadItem('test-item');
      expect(result1.status).toBe('loaded');

      const result2 = await service.loadItem('test-item');
      expect(result2.status).toBe('loaded');
      expect(result2.loadTime).toBeGreaterThanOrEqual(result1.loadTime); // Should be similar due to no cache

      service.destroy();
    });

    it('should clear cache', async () => {
      const item: LazyLoadingItem = {
        id: 'test-item',
        type: 'image',
        src: 'https://example.com/image.jpg',
        priority: 'high',
        preload: true,
        cache: true,
        retry: true,
        timeout: 5000,
        onLoad: jest.fn(),
        onError: jest.fn(),
        onProgress: jest.fn()
      };

      lazyLoadingService.registerItem(item);
      const result1 = await lazyLoadingService.loadItem('test-item');
      expect(result1.status).toBe('loaded');

      lazyLoadingService.clearCache();

      const result2 = await lazyLoadingService.loadItem('test-item');
      expect(result2.status).toBe('loaded');
      expect(result2.loadTime).toBeGreaterThanOrEqual(result1.loadTime); // Should be similar due to cleared cache
    });
  });

  describe('Metrics', () => {
    it('should collect loading metrics', async () => {
      const item: LazyLoadingItem = {
        id: 'test-item',
        type: 'image',
        src: 'https://example.com/image.jpg',
        priority: 'high',
        preload: true,
        cache: true,
        retry: true,
        timeout: 5000,
        onLoad: jest.fn(),
        onError: jest.fn(),
        onProgress: jest.fn()
      };

      lazyLoadingService.registerItem(item);
      await lazyLoadingService.loadItem('test-item');

      const metrics = lazyLoadingService.getMetrics();
      expect(metrics).toBeDefined();
      expect(metrics.totalItems).toBe(1);
      expect(metrics.loadedItems).toBe(1);
      expect(metrics.failedItems).toBe(0);
      expect(metrics.pendingItems).toBe(0);
      expect(metrics.averageLoadTime).toBeGreaterThan(0);
      expect(metrics.loadTimeByType).toBeDefined();
      expect(metrics.loadTimeByType['image']).toBeGreaterThan(0);
      expect(metrics.loadTimeByPriority).toBeDefined();
      expect(metrics.loadTimeByPriority['high']).toBeGreaterThan(0);
      expect(metrics.cacheHitRate).toBeGreaterThanOrEqual(0);
      expect(metrics.cacheMissRate).toBeGreaterThanOrEqual(0);
      expect(metrics.retryRate).toBeGreaterThanOrEqual(0);
      expect(metrics.timeoutRate).toBeGreaterThanOrEqual(0);
      expect(metrics.preloadRate).toBeGreaterThanOrEqual(0);
      expect(metrics.intersectionObserverRate).toBeGreaterThanOrEqual(0);
      expect(metrics.resourceHintsRate).toBeGreaterThanOrEqual(0);
      expect(metrics.serviceWorkerRate).toBeGreaterThanOrEqual(0);
      expect(metrics.lastUpdated).toBeDefined();
    });

    it('should reset metrics', async () => {
      const item: LazyLoadingItem = {
        id: 'test-item',
        type: 'image',
        src: 'https://example.com/image.jpg',
        priority: 'high',
        preload: true,
        cache: true,
        retry: true,
        timeout: 5000,
        onLoad: jest.fn(),
        onError: jest.fn(),
        onProgress: jest.fn()
      };

      lazyLoadingService.registerItem(item);
      await lazyLoadingService.loadItem('test-item');

      let metrics = lazyLoadingService.getMetrics();
      expect(metrics.totalItems).toBe(1);

      lazyLoadingService.resetMetrics();

      metrics = lazyLoadingService.getMetrics();
      expect(metrics.totalItems).toBe(0);
      expect(metrics.loadedItems).toBe(0);
      expect(metrics.failedItems).toBe(0);
      expect(metrics.pendingItems).toBe(0);
      expect(metrics.averageLoadTime).toBe(0);
      expect(metrics.loadTimeByType).toEqual({});
      expect(metrics.loadTimeByPriority).toEqual({});
      expect(metrics.cacheHitRate).toBe(0);
      expect(metrics.cacheMissRate).toBe(0);
      expect(metrics.retryRate).toBe(0);
      expect(metrics.timeoutRate).toBe(0);
      expect(metrics.preloadRate).toBe(0);
      expect(metrics.intersectionObserverRate).toBe(0);
      expect(metrics.resourceHintsRate).toBe(0);
      expect(metrics.serviceWorkerRate).toBe(0);
      expect(metrics.lastUpdated).toBeDefined();
    });
  });

  describe('Configuration', () => {
    it('should update configuration', () => {
      const newConfig = {
        enabled: false,
        preloadThreshold: 200,
        loadTimeout: 10000,
        maxConcurrentLoads: 5,
        retryAttempts: 5,
        retryDelay: 2000,
        cacheEnabled: false,
        cacheSize: 100,
        cacheTimeout: 600000,
        enablePreloading: false,
        enableIntersectionObserver: false,
        enableResourceHints: false,
        enableServiceWorker: true
      };

      lazyLoadingService.updateConfig(newConfig);
      const config = lazyLoadingService.getConfig();
      expect(config.enabled).toBe(false);
      expect(config.preloadThreshold).toBe(200);
      expect(config.loadTimeout).toBe(10000);
      expect(config.maxConcurrentLoads).toBe(5);
      expect(config.retryAttempts).toBe(5);
      expect(config.retryDelay).toBe(2000);
      expect(config.cacheEnabled).toBe(false);
      expect(config.cacheSize).toBe(100);
      expect(config.cacheTimeout).toBe(600000);
      expect(config.enablePreloading).toBe(false);
      expect(config.enableIntersectionObserver).toBe(false);
      expect(config.enableResourceHints).toBe(false);
      expect(config.enableServiceWorker).toBe(true);
    });

    it('should merge configuration properly', () => {
      const newConfig = {
        enabled: false,
        preloadThreshold: 200,
        loadTimeout: 10000,
        maxConcurrentLoads: 5,
        retryAttempts: 5,
        retryDelay: 2000,
        cacheEnabled: false,
        cacheSize: 100,
        cacheTimeout: 600000,
        enablePreloading: false,
        enableIntersectionObserver: false,
        enableResourceHints: false,
        enableServiceWorker: true
      };

      lazyLoadingService.updateConfig(newConfig);
      const config = lazyLoadingService.getConfig();
      expect(config.enabled).toBe(false);
      expect(config.preloadThreshold).toBe(200);
      expect(config.loadTimeout).toBe(10000);
      expect(config.maxConcurrentLoads).toBe(5);
      expect(config.retryAttempts).toBe(5);
      expect(config.retryDelay).toBe(2000);
      expect(config.cacheEnabled).toBe(false);
      expect(config.cacheSize).toBe(100);
      expect(config.cacheTimeout).toBe(600000);
      expect(config.enablePreloading).toBe(false);
      expect(config.enableIntersectionObserver).toBe(false);
      expect(config.enableResourceHints).toBe(false);
      expect(config.enableServiceWorker).toBe(true);
    });
  });

  describe('Error Handling', () => {
    it('should handle loading errors gracefully', async () => {
      // Mock loadItem to throw error
      const originalLoadItem = lazyLoadingService.loadItem;
      lazyLoadingService.loadItem = jest.fn().mockImplementation(() => {
        throw new Error('Loading error');
      });

      // Should not throw error
      await expect(lazyLoadingService.loadItem('test-item')).rejects.toThrow('Loading error');

      // Restore original method
      lazyLoadingService.loadItem = originalLoadItem;
    });

    it('should handle batch loading errors gracefully', async () => {
      // Mock loadItems to throw error
      const originalLoadItems = lazyLoadingService.loadItems;
      lazyLoadingService.loadItems = jest.fn().mockImplementation(() => {
        throw new Error('Batch loading error');
      });

      // Should not throw error
      await expect(lazyLoadingService.loadItems(['test-item-1', 'test-item-2'])).rejects.toThrow('Batch loading error');

      // Restore original method
      lazyLoadingService.loadItems = originalLoadItems;
    });
  });

  describe('Cleanup', () => {
    it('should destroy service', async () => {
      const item: LazyLoadingItem = {
        id: 'test-item',
        type: 'image',
        src: 'https://example.com/image.jpg',
        priority: 'high',
        preload: true,
        cache: true,
        retry: true,
        timeout: 5000,
        onLoad: jest.fn(),
        onError: jest.fn(),
        onProgress: jest.fn()
      };

      lazyLoadingService.registerItem(item);
      await lazyLoadingService.loadItem('test-item');
      
      const metrics = lazyLoadingService.getMetrics();
      expect(metrics.totalItems).toBeGreaterThan(0);
      
      lazyLoadingService.destroy();
      
      const metricsAfterDestroy = lazyLoadingService.getMetrics();
      expect(metricsAfterDestroy.totalItems).toBe(0);
    });
  });
});
