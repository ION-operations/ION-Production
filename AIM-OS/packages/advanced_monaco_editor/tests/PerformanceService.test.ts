/**
 * Performance Service Tests
 * 
 * Comprehensive unit tests for the PerformanceService class
 */

import { PerformanceService, PerformanceConfig, PerformanceMetrics } from '../src/services/PerformanceService';

describe('PerformanceService', () => {
  let performanceService: PerformanceService;

  beforeEach(() => {
    performanceService = new PerformanceService({
      enableMonitoring: true,
      enableProfiling: false,
      enableMemoryTracking: true,
      enableCpuTracking: true,
      enableRenderTracking: true,
      enableAnalysisTracking: true,
      enableCacheTracking: true,
      enableLazyLoading: true,
      maxMemoryUsage: 100 * 1024 * 1024, // 100MB
      maxCpuUsage: 80,
      maxRenderTime: 16,
      maxAnalysisTime: 100,
      minCacheHitRate: 70,
      monitoringInterval: 1000,
      profilingInterval: 5000,
      maxMetricsHistory: 1000,
      enableAlerts: true,
      alertThresholds: {
        memory: 80,
        cpu: 70,
        render: 20,
        analysis: 200,
        cache: 50
      }
    });
  });

  afterEach(() => {
    performanceService.destroy();
  });

  describe('Initialization', () => {
    it('should initialize with default configuration', () => {
      const defaultService = new PerformanceService();
      expect(defaultService).toBeDefined();
      expect(defaultService.getConfig().enableMonitoring).toBe(true);
      expect(defaultService.getConfig().enableProfiling).toBe(false);
      defaultService.destroy();
    });

    it('should initialize with custom configuration', () => {
      const customConfig: Partial<PerformanceConfig> = {
        enableMonitoring: false,
        enableProfiling: true,
        maxMemoryUsage: 200 * 1024 * 1024
      };

      const customService = new PerformanceService(customConfig);
      expect(customService.getConfig().enableMonitoring).toBe(false);
      expect(customService.getConfig().enableProfiling).toBe(true);
      expect(customService.getConfig().maxMemoryUsage).toBe(200 * 1024 * 1024);
      customService.destroy();
    });
  });

  describe('Monitoring', () => {
    it('should start monitoring', () => {
      const startSpy = jest.spyOn(performanceService, 'startMonitoring');
      performanceService.startMonitoring();
      expect(startSpy).toHaveBeenCalled();
    });

    it('should stop monitoring', () => {
      const stopSpy = jest.spyOn(performanceService, 'stopMonitoring');
      performanceService.startMonitoring();
      performanceService.stopMonitoring();
      expect(stopSpy).toHaveBeenCalled();
    });

    it('should not start monitoring twice', () => {
      performanceService.startMonitoring();
      const startSpy = jest.spyOn(performanceService, 'startMonitoring');
      performanceService.startMonitoring();
      expect(startSpy).toHaveBeenCalledTimes(1);
    });

    it('should not stop monitoring if not started', () => {
      const stopSpy = jest.spyOn(performanceService, 'stopMonitoring');
      performanceService.stopMonitoring();
      expect(stopSpy).toHaveBeenCalledTimes(1);
    });
  });

  describe('Metrics Collection', () => {
    it('should collect metrics when monitoring', (done) => {
      performanceService.on('metricsCollected', (metrics) => {
        expect(metrics).toBeDefined();
        expect(metrics.timestamp).toBeDefined();
        expect(metrics.memoryUsage).toBeDefined();
        expect(metrics.cpuUsage).toBeDefined();
        expect(metrics.renderTime).toBeDefined();
        expect(metrics.analysisTime).toBeDefined();
        expect(metrics.cacheHitRate).toBeDefined();
        expect(metrics.lazyLoading).toBeDefined();
        done();
      });

      performanceService.startMonitoring();
    });

    it('should record analysis time', () => {
      const analysisTime = 150;
      performanceService.recordAnalysisTime(analysisTime);
      
      const metrics = performanceService.getLatestMetrics();
      expect(metrics?.analysisTime.current).toBe(analysisTime);
    });

    it('should record cache hits and misses', () => {
      performanceService.recordCacheHit();
      performanceService.recordCacheMiss();
      performanceService.recordCacheHit();
      
      const metrics = performanceService.getLatestMetrics();
      expect(metrics?.cacheHitRate.current).toBe(66.67); // 2 hits out of 3 total
    });

    it('should keep metrics history within limit', () => {
      const maxHistory = 10;
      const service = new PerformanceService({ maxMetricsHistory: maxHistory });
      
      // Generate more metrics than the limit
      for (let i = 0; i < maxHistory + 5; i++) {
        service.recordAnalysisTime(i);
      }
      
      const metrics = service.getMetrics();
      expect(metrics.length).toBeLessThanOrEqual(maxHistory);
      service.destroy();
    });
  });

  describe('Alerts', () => {
    it('should emit alert for high memory usage', (done) => {
      performanceService.on('alert', (alert) => {
        expect(alert.type).toBe('memory');
        expect(alert.level).toBe('warning');
        expect(alert.value).toBeGreaterThan(80);
        done();
      });

      // Simulate high memory usage
      const metrics: PerformanceMetrics = {
        timestamp: Date.now(),
        memoryUsage: { used: 90 * 1024 * 1024, total: 100 * 1024 * 1024, percentage: 90 },
        cpuUsage: { average: 50, peak: 60, current: 55 },
        renderTime: { average: 10, peak: 15, current: 12 },
        analysisTime: { average: 50, peak: 80, current: 60 },
        cacheHitRate: { average: 80, current: 85 },
        lazyLoading: { loadedModules: 5, totalModules: 10, loadingTime: 100 }
      };

      // Manually trigger alert check
      (performanceService as any).checkAlerts(metrics);
    });

    it('should emit alert for high CPU usage', (done) => {
      performanceService.on('alert', (alert) => {
        expect(alert.type).toBe('cpu');
        expect(alert.level).toBe('warning');
        expect(alert.value).toBeGreaterThan(70);
        done();
      });

      const metrics: PerformanceMetrics = {
        timestamp: Date.now(),
        memoryUsage: { used: 50 * 1024 * 1024, total: 100 * 1024 * 1024, percentage: 50 },
        cpuUsage: { average: 80, peak: 90, current: 85 },
        renderTime: { average: 10, peak: 15, current: 12 },
        analysisTime: { average: 50, peak: 80, current: 60 },
        cacheHitRate: { average: 80, current: 85 },
        lazyLoading: { loadedModules: 5, totalModules: 10, loadingTime: 100 }
      };

      (performanceService as any).checkAlerts(metrics);
    });

    it('should emit alert for slow render time', (done) => {
      performanceService.on('alert', (alert) => {
        expect(alert.type).toBe('render');
        expect(alert.level).toBe('warning');
        expect(alert.value).toBeGreaterThan(20);
        done();
      });

      const metrics: PerformanceMetrics = {
        timestamp: Date.now(),
        memoryUsage: { used: 50 * 1024 * 1024, total: 100 * 1024 * 1024, percentage: 50 },
        cpuUsage: { average: 50, peak: 60, current: 55 },
        renderTime: { average: 25, peak: 30, current: 28 },
        analysisTime: { average: 50, peak: 80, current: 60 },
        cacheHitRate: { average: 80, current: 85 },
        lazyLoading: { loadedModules: 5, totalModules: 10, loadingTime: 100 }
      };

      (performanceService as any).checkAlerts(metrics);
    });

    it('should emit alert for slow analysis time', (done) => {
      performanceService.on('alert', (alert) => {
        expect(alert.type).toBe('analysis');
        expect(alert.level).toBe('warning');
        expect(alert.value).toBeGreaterThan(200);
        done();
      });

      const metrics: PerformanceMetrics = {
        timestamp: Date.now(),
        memoryUsage: { used: 50 * 1024 * 1024, total: 100 * 1024 * 1024, percentage: 50 },
        cpuUsage: { average: 50, peak: 60, current: 55 },
        renderTime: { average: 10, peak: 15, current: 12 },
        analysisTime: { average: 250, peak: 300, current: 280 },
        cacheHitRate: { average: 80, current: 85 },
        lazyLoading: { loadedModules: 5, totalModules: 10, loadingTime: 100 }
      };

      (performanceService as any).checkAlerts(metrics);
    });

    it('should emit alert for low cache hit rate', (done) => {
      performanceService.on('alert', (alert) => {
        expect(alert.type).toBe('cache');
        expect(alert.level).toBe('warning');
        expect(alert.value).toBeLessThan(50);
        done();
      });

      const metrics: PerformanceMetrics = {
        timestamp: Date.now(),
        memoryUsage: { used: 50 * 1024 * 1024, total: 100 * 1024 * 1024, percentage: 50 },
        cpuUsage: { average: 50, peak: 60, current: 55 },
        renderTime: { average: 10, peak: 15, current: 12 },
        analysisTime: { average: 50, peak: 80, current: 60 },
        cacheHitRate: { average: 30, current: 25 },
        lazyLoading: { loadedModules: 5, totalModules: 10, loadingTime: 100 }
      };

      (performanceService as any).checkAlerts(metrics);
    });
  });

  describe('Caching', () => {
    it('should set and get cache', () => {
      const key = 'test-key';
      const data = { test: 'data' };
      const size = 100;

      performanceService.setCache(key, data, size);
      const cached = performanceService.getFromCache(key);
      expect(cached).toEqual(data);
    });

    it('should return null for non-existent cache key', () => {
      const cached = performanceService.getFromCache('non-existent-key');
      expect(cached).toBeNull();
    });

    it('should clear cache', () => {
      performanceService.setCache('key1', 'data1', 100);
      performanceService.setCache('key2', 'data2', 200);
      
      expect(performanceService.getFromCache('key1')).toBe('data1');
      expect(performanceService.getFromCache('key2')).toBe('data2');
      
      performanceService.clearCache();
      
      expect(performanceService.getFromCache('key1')).toBeNull();
      expect(performanceService.getFromCache('key2')).toBeNull();
    });

    it('should handle cache expiration', (done) => {
      const service = new PerformanceService({
        cacheEnabled: true,
        cacheSize: 1000,
        cacheTimeout: 100 // 100ms
      });

      service.setCache('expired-key', 'data', 100);
      
      setTimeout(() => {
        const cached = service.getFromCache('expired-key');
        expect(cached).toBeNull();
        service.destroy();
        done();
      }, 150);
    });
  });

  describe('Lazy Loading', () => {
    it('should load module successfully', async () => {
      const moduleId = 'test-module';
      const moduleData = { test: 'module' };
      const loader = jest.fn().mockResolvedValue(moduleData);

      const result = await performanceService.loadModule(moduleId, loader);
      expect(result).toEqual(moduleData);
      expect(loader).toHaveBeenCalled();
    });

    it('should handle module load failure', async () => {
      const moduleId = 'failing-module';
      const error = new Error('Load failed');
      const loader = jest.fn().mockRejectedValue(error);

      await expect(performanceService.loadModule(moduleId, loader)).rejects.toThrow('Load failed');
    });

    it('should handle load timeout', async () => {
      const moduleId = 'timeout-module';
      const loader = jest.fn().mockImplementation(() => 
        new Promise(resolve => setTimeout(resolve, 10000))
      );

      await expect(performanceService.loadModule(moduleId, loader)).rejects.toThrow('Load timeout');
    });

    it('should preload module', () => {
      const moduleId = 'preload-module';
      const loader = jest.fn().mockResolvedValue({ test: 'preload' });

      performanceService.preloadModule(moduleId, loader);
      
      // Should not throw error
      expect(() => performanceService.preloadModule(moduleId, loader)).not.toThrow();
    });
  });

  describe('Performance Optimization', () => {
    it('should optimize performance', () => {
      const optimizeSpy = jest.spyOn(performanceService, 'optimizePerformance');
      performanceService.optimizePerformance();
      expect(optimizeSpy).toHaveBeenCalled();
    });

    it('should get performance report', () => {
      // Record some metrics
      performanceService.recordAnalysisTime(100);
      performanceService.recordAnalysisTime(200);
      performanceService.recordCacheHit();
      performanceService.recordCacheMiss();

      const report = performanceService.getPerformanceReport();
      expect(report).toBeDefined();
      expect(report.summary).toBeDefined();
      expect(report.recommendations).toBeDefined();
      expect(Array.isArray(report.recommendations)).toBe(true);
    });
  });

  describe('Configuration', () => {
    it('should update configuration', () => {
      const newConfig = {
        enableMonitoring: false,
        maxMemoryUsage: 200 * 1024 * 1024
      };

      performanceService.updateConfig(newConfig);
      const config = performanceService.getConfig();
      expect(config.enableMonitoring).toBe(false);
      expect(config.maxMemoryUsage).toBe(200 * 1024 * 1024);
    });

    it('should merge configuration properly', () => {
      const newConfig = {
        alertThresholds: {
          memory: 90,
          cpu: 80
        }
      };

      performanceService.updateConfig(newConfig);
      const config = performanceService.getConfig();
      expect(config.alertThresholds.memory).toBe(90);
      expect(config.alertThresholds.cpu).toBe(80);
      expect(config.alertThresholds.render).toBe(20); // Should preserve existing value
    });
  });

  describe('Error Handling', () => {
    it('should handle monitoring errors gracefully', (done) => {
      performanceService.on('error', (error) => {
        expect(error).toBeDefined();
        done();
      });

      // Simulate an error in monitoring
      (performanceService as any).collectMetrics = jest.fn().mockImplementation(() => {
        throw new Error('Monitoring error');
      });

      performanceService.startMonitoring();
    });

    it('should handle cache errors gracefully', () => {
      // Mock localStorage to throw error
      const originalLocalStorage = global.localStorage;
      global.localStorage = {
        getItem: jest.fn().mockImplementation(() => {
          throw new Error('Storage error');
        }),
        setItem: jest.fn().mockImplementation(() => {
          throw new Error('Storage error');
        }),
        removeItem: jest.fn(),
        clear: jest.fn(),
        length: 0,
        key: jest.fn()
      };

      // Should not throw error
      expect(() => {
        performanceService.setCache('test-key', 'test-data', 100);
      }).not.toThrow();

      // Restore localStorage
      global.localStorage = originalLocalStorage;
    });
  });

  describe('Cleanup', () => {
    it('should destroy service', () => {
      performanceService.startMonitoring();
      performanceService.setCache('test-key', 'test-data', 100);
      
      expect(performanceService.getMetrics().length).toBeGreaterThan(0);
      expect(performanceService.getFromCache('test-key')).toBe('test-data');
      
      performanceService.destroy();
      
      expect(performanceService.getMetrics().length).toBe(0);
      expect(performanceService.getFromCache('test-key')).toBeNull();
    });
  });
});
