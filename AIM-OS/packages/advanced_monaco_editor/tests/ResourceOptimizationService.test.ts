/**
 * Resource Optimization Service Tests
 * 
 * Comprehensive unit tests for the ResourceOptimizationService class
 */

import { ResourceOptimizationService, ResourceOptimizationConfig, OptimizationResult, OptimizationMetrics } from '../src/services/ResourceOptimizationService';

describe('ResourceOptimizationService', () => {
  let resourceOptimizationService: ResourceOptimizationService;

  beforeEach(() => {
    resourceOptimizationService = new ResourceOptimizationService({
      enableImageOptimization: true,
      enableFontOptimization: true,
      enableCssOptimization: true,
      enableJsOptimization: true,
      enableBundleOptimization: true,
      enableNetworkOptimization: true,
      enableMemoryOptimization: true,
      imageQuality: 80,
      imageFormat: 'auto',
      fontDisplay: 'swap',
      cssMinification: true,
      jsMinification: true,
      bundleSplitting: true,
      treeShaking: true,
      compressionLevel: 6,
      cacheStrategy: 'moderate',
      preloadCriticalResources: true,
      lazyLoadNonCriticalResources: true,
      enableServiceWorker: false,
      enableCDN: false
    });
  });

  afterEach(() => {
    resourceOptimizationService.destroy();
  });

  describe('Initialization', () => {
    it('should initialize with default configuration', () => {
      const defaultService = new ResourceOptimizationService();
      expect(defaultService).toBeDefined();
      expect(defaultService.getConfig().enableImageOptimization).toBe(true);
      expect(defaultService.getConfig().enableFontOptimization).toBe(true);
      expect(defaultService.getConfig().enableCssOptimization).toBe(true);
      expect(defaultService.getConfig().enableJsOptimization).toBe(true);
      expect(defaultService.getConfig().enableBundleOptimization).toBe(true);
      expect(defaultService.getConfig().enableNetworkOptimization).toBe(true);
      expect(defaultService.getConfig().enableMemoryOptimization).toBe(true);
      expect(defaultService.getConfig().imageQuality).toBe(80);
      expect(defaultService.getConfig().imageFormat).toBe('auto');
      expect(defaultService.getConfig().fontDisplay).toBe('swap');
      expect(defaultService.getConfig().cssMinification).toBe(true);
      expect(defaultService.getConfig().jsMinification).toBe(true);
      expect(defaultService.getConfig().bundleSplitting).toBe(true);
      expect(defaultService.getConfig().treeShaking).toBe(true);
      expect(defaultService.getConfig().compressionLevel).toBe(6);
      expect(defaultService.getConfig().cacheStrategy).toBe('moderate');
      expect(defaultService.getConfig().preloadCriticalResources).toBe(true);
      expect(defaultService.getConfig().lazyLoadNonCriticalResources).toBe(true);
      expect(defaultService.getConfig().enableServiceWorker).toBe(false);
      expect(defaultService.getConfig().enableCDN).toBe(false);
      defaultService.destroy();
    });

    it('should initialize with custom configuration', () => {
      const customConfig: Partial<ResourceOptimizationConfig> = {
        enableImageOptimization: false,
        enableFontOptimization: false,
        enableCssOptimization: false,
        enableJsOptimization: false,
        enableBundleOptimization: false,
        enableNetworkOptimization: false,
        enableMemoryOptimization: false,
        imageQuality: 90,
        imageFormat: 'webp',
        fontDisplay: 'block',
        cssMinification: false,
        jsMinification: false,
        bundleSplitting: false,
        treeShaking: false,
        compressionLevel: 9,
        cacheStrategy: 'aggressive',
        preloadCriticalResources: false,
        lazyLoadNonCriticalResources: false,
        enableServiceWorker: true,
        enableCDN: true
      };

      const customService = new ResourceOptimizationService(customConfig);
      expect(customService.getConfig().enableImageOptimization).toBe(false);
      expect(customService.getConfig().enableFontOptimization).toBe(false);
      expect(customService.getConfig().enableCssOptimization).toBe(false);
      expect(customService.getConfig().enableJsOptimization).toBe(false);
      expect(customService.getConfig().enableBundleOptimization).toBe(false);
      expect(customService.getConfig().enableNetworkOptimization).toBe(false);
      expect(customService.getConfig().enableMemoryOptimization).toBe(false);
      expect(customService.getConfig().imageQuality).toBe(90);
      expect(customService.getConfig().imageFormat).toBe('webp');
      expect(customService.getConfig().fontDisplay).toBe('block');
      expect(customService.getConfig().cssMinification).toBe(false);
      expect(customService.getConfig().jsMinification).toBe(false);
      expect(customService.getConfig().bundleSplitting).toBe(false);
      expect(customService.getConfig().treeShaking).toBe(false);
      expect(customService.getConfig().compressionLevel).toBe(9);
      expect(customService.getConfig().cacheStrategy).toBe('aggressive');
      expect(customService.getConfig().preloadCriticalResources).toBe(false);
      expect(customService.getConfig().lazyLoadNonCriticalResources).toBe(false);
      expect(customService.getConfig().enableServiceWorker).toBe(true);
      expect(customService.getConfig().enableCDN).toBe(true);
      customService.destroy();
    });
  });

  describe('Image Optimization', () => {
    it('should optimize image', async () => {
      const result = await resourceOptimizationService.optimizeImage('https://example.com/image.jpg');
      expect(result).toBeDefined();
      expect(result.success).toBe(true);
      expect(result.originalSize).toBeGreaterThan(0);
      expect(result.optimizedSize).toBeGreaterThan(0);
      expect(result.compressionRatio).toBeGreaterThan(0);
      expect(result.format).toBeDefined();
      expect(result.quality).toBeDefined();
      expect(result.optimizations).toBeDefined();
      expect(result.optimizations.length).toBeGreaterThan(0);
    });

    it('should optimize image with custom options', async () => {
      const result = await resourceOptimizationService.optimizeImage('https://example.com/image.jpg', {
        quality: 90,
        format: 'webp',
        maxWidth: 1920,
        maxHeight: 1080,
        enableWebP: true,
        enableAVIF: false,
        enableProgressive: true,
        enableMetadata: false
      });
      expect(result).toBeDefined();
      expect(result.success).toBe(true);
      expect(result.originalSize).toBeGreaterThan(0);
      expect(result.optimizedSize).toBeGreaterThan(0);
      expect(result.compressionRatio).toBeGreaterThan(0);
      expect(result.format).toBeDefined();
      expect(result.quality).toBeDefined();
      expect(result.optimizations).toBeDefined();
      expect(result.optimizations.length).toBeGreaterThan(0);
    });

    it('should handle image optimization errors', async () => {
      const result = await resourceOptimizationService.optimizeImage('https://invalid-url.com/image.jpg');
      expect(result).toBeDefined();
      expect(result.success).toBe(false);
      expect(result.error).toBeDefined();
      expect(result.originalSize).toBe(0);
      expect(result.optimizedSize).toBe(0);
      expect(result.compressionRatio).toBe(0);
      expect(result.format).toBeUndefined();
      expect(result.quality).toBeUndefined();
      expect(result.optimizations).toEqual([]);
    });
  });

  describe('Font Optimization', () => {
    it('should optimize font', async () => {
      const result = await resourceOptimizationService.optimizeFont('https://example.com/font.woff2');
      expect(result).toBeDefined();
      expect(result.success).toBe(true);
      expect(result.originalSize).toBeGreaterThan(0);
      expect(result.optimizedSize).toBeGreaterThan(0);
      expect(result.compressionRatio).toBeGreaterThan(0);
      expect(result.format).toBeDefined();
      expect(result.optimizations).toBeDefined();
      expect(result.optimizations.length).toBeGreaterThan(0);
    });

    it('should optimize font with custom options', async () => {
      const result = await resourceOptimizationService.optimizeFont('https://example.com/font.woff2', {
        display: 'swap',
        preload: true,
        subset: true,
        unicodeRange: 'U+0000-00FF',
        enableWOFF2: true,
        enableWOFF: false,
        enableTTF: false,
        enableEOT: false
      });
      expect(result).toBeDefined();
      expect(result.success).toBe(true);
      expect(result.originalSize).toBeGreaterThan(0);
      expect(result.optimizedSize).toBeGreaterThan(0);
      expect(result.compressionRatio).toBeGreaterThan(0);
      expect(result.format).toBeDefined();
      expect(result.optimizations).toBeDefined();
      expect(result.optimizations.length).toBeGreaterThan(0);
    });

    it('should handle font optimization errors', async () => {
      const result = await resourceOptimizationService.optimizeFont('https://invalid-url.com/font.woff2');
      expect(result).toBeDefined();
      expect(result.success).toBe(false);
      expect(result.error).toBeDefined();
      expect(result.originalSize).toBe(0);
      expect(result.optimizedSize).toBe(0);
      expect(result.compressionRatio).toBe(0);
      expect(result.format).toBeUndefined();
      expect(result.optimizations).toEqual([]);
    });
  });

  describe('CSS Optimization', () => {
    it('should optimize CSS', async () => {
      const css = `
        .test {
          color: red;
          background-color: blue;
          margin: 10px;
          padding: 5px;
        }
      `;
      const result = await resourceOptimizationService.optimizeCSS(css);
      expect(result).toBeDefined();
      expect(result.success).toBe(true);
      expect(result.originalSize).toBeGreaterThan(0);
      expect(result.optimizedSize).toBeGreaterThan(0);
      expect(result.compressionRatio).toBeGreaterThan(0);
      expect(result.optimizations).toBeDefined();
      expect(result.optimizations.length).toBeGreaterThan(0);
    });

    it('should optimize CSS with custom options', async () => {
      const css = `
        .test {
          color: red;
          background-color: blue;
          margin: 10px;
          padding: 5px;
        }
      `;
      const result = await resourceOptimizationService.optimizeCSS(css, {
        minify: true,
        removeComments: true,
        removeWhitespace: true,
        removeUnused: true,
        mergeSelectors: true,
        optimizeProperties: true,
        enableSourceMaps: false,
        enableAutoprefixer: true
      });
      expect(result).toBeDefined();
      expect(result.success).toBe(true);
      expect(result.originalSize).toBeGreaterThan(0);
      expect(result.optimizedSize).toBeGreaterThan(0);
      expect(result.compressionRatio).toBeGreaterThan(0);
      expect(result.optimizations).toBeDefined();
      expect(result.optimizations.length).toBeGreaterThan(0);
    });

    it('should handle CSS optimization errors', async () => {
      const invalidCss = 'invalid css syntax {';
      const result = await resourceOptimizationService.optimizeCSS(invalidCss);
      expect(result).toBeDefined();
      expect(result.success).toBe(false);
      expect(result.error).toBeDefined();
      expect(result.originalSize).toBeGreaterThan(0);
      expect(result.optimizedSize).toBe(0);
      expect(result.compressionRatio).toBe(0);
      expect(result.optimizations).toEqual([]);
    });
  });

  describe('JavaScript Optimization', () => {
    it('should optimize JavaScript', async () => {
      const js = `
        function test() {
          console.log('Hello, World!');
          return 'test';
        }
      `;
      const result = await resourceOptimizationService.optimizeJS(js);
      expect(result).toBeDefined();
      expect(result.success).toBe(true);
      expect(result.originalSize).toBeGreaterThan(0);
      expect(result.optimizedSize).toBeGreaterThan(0);
      expect(result.compressionRatio).toBeGreaterThan(0);
      expect(result.optimizations).toBeDefined();
      expect(result.optimizations.length).toBeGreaterThan(0);
    });

    it('should optimize JavaScript with custom options', async () => {
      const js = `
        function test() {
          console.log('Hello, World!');
          return 'test';
        }
      `;
      const result = await resourceOptimizationService.optimizeJS(js, {
        minify: true,
        removeComments: true,
        removeWhitespace: true,
        removeUnused: true,
        optimizeVariables: true,
        optimizeFunctions: true,
        enableSourceMaps: false,
        enableBabel: true
      });
      expect(result).toBeDefined();
      expect(result.success).toBe(true);
      expect(result.originalSize).toBeGreaterThan(0);
      expect(result.optimizedSize).toBeGreaterThan(0);
      expect(result.compressionRatio).toBeGreaterThan(0);
      expect(result.optimizations).toBeDefined();
      expect(result.optimizations.length).toBeGreaterThan(0);
    });

    it('should handle JavaScript optimization errors', async () => {
      const invalidJs = 'function test() { console.log("Hello, World!"; }';
      const result = await resourceOptimizationService.optimizeJS(invalidJs);
      expect(result).toBeDefined();
      expect(result.success).toBe(false);
      expect(result.error).toBeDefined();
      expect(result.originalSize).toBeGreaterThan(0);
      expect(result.optimizedSize).toBe(0);
      expect(result.compressionRatio).toBe(0);
      expect(result.optimizations).toEqual([]);
    });
  });

  describe('Bundle Optimization', () => {
    it('should optimize bundle', async () => {
      const bundle = {
        'main.js': 'function main() { console.log("main"); }',
        'utils.js': 'function utils() { console.log("utils"); }',
        'styles.css': '.main { color: red; }'
      };
      const result = await resourceOptimizationService.optimizeBundle(bundle);
      expect(result).toBeDefined();
      expect(result.success).toBe(true);
      expect(result.originalSize).toBeGreaterThan(0);
      expect(result.optimizedSize).toBeGreaterThan(0);
      expect(result.compressionRatio).toBeGreaterThan(0);
      expect(result.optimizations).toBeDefined();
      expect(result.optimizations.length).toBeGreaterThan(0);
    });

    it('should optimize bundle with custom options', async () => {
      const bundle = {
        'main.js': 'function main() { console.log("main"); }',
        'utils.js': 'function utils() { console.log("utils"); }',
        'styles.css': '.main { color: red; }'
      };
      const result = await resourceOptimizationService.optimizeBundle(bundle, {
        enableSplitting: true,
        enableTreeShaking: true,
        enableMinification: true,
        enableCompression: true,
        enableSourceMaps: false,
        enableChunking: true,
        maxChunkSize: 100000,
        minChunkSize: 1000
      });
      expect(result).toBeDefined();
      expect(result.success).toBe(true);
      expect(result.originalSize).toBeGreaterThan(0);
      expect(result.optimizedSize).toBeGreaterThan(0);
      expect(result.compressionRatio).toBeGreaterThan(0);
      expect(result.optimizations).toBeDefined();
      expect(result.optimizations.length).toBeGreaterThan(0);
    });

    it('should handle bundle optimization errors', async () => {
      const invalidBundle = {
        'main.js': 'function main() { console.log("main"; }',
        'utils.js': 'function utils() { console.log("utils"; }',
        'styles.css': '.main { color: red; }'
      };
      const result = await resourceOptimizationService.optimizeBundle(invalidBundle);
      expect(result).toBeDefined();
      expect(result.success).toBe(false);
      expect(result.error).toBeDefined();
      expect(result.originalSize).toBeGreaterThan(0);
      expect(result.optimizedSize).toBe(0);
      expect(result.compressionRatio).toBe(0);
      expect(result.optimizations).toEqual([]);
    });
  });

  describe('Network Optimization', () => {
    it('should optimize network requests', async () => {
      const requests = [
        { url: 'https://example.com/api/data', method: 'GET', headers: {} },
        { url: 'https://example.com/api/users', method: 'GET', headers: {} }
      ];
      const result = await resourceOptimizationService.optimizeNetwork(requests);
      expect(result).toBeDefined();
      expect(result.success).toBe(true);
      expect(result.originalSize).toBeGreaterThan(0);
      expect(result.optimizedSize).toBeGreaterThan(0);
      expect(result.compressionRatio).toBeGreaterThan(0);
      expect(result.optimizations).toBeDefined();
      expect(result.optimizations.length).toBeGreaterThan(0);
    });

    it('should optimize network requests with custom options', async () => {
      const requests = [
        { url: 'https://example.com/api/data', method: 'GET', headers: {} },
        { url: 'https://example.com/api/users', method: 'GET', headers: {} }
      ];
      const result = await resourceOptimizationService.optimizeNetwork(requests, {
        enableCompression: true,
        enableCaching: true,
        enablePrefetching: true,
        enablePreloading: true,
        enableCDN: false,
        enableHTTP2: true,
        enableKeepAlive: true,
        maxConcurrentRequests: 6
      });
      expect(result).toBeDefined();
      expect(result.success).toBe(true);
      expect(result.originalSize).toBeGreaterThan(0);
      expect(result.optimizedSize).toBeGreaterThan(0);
      expect(result.compressionRatio).toBeGreaterThan(0);
      expect(result.optimizations).toBeDefined();
      expect(result.optimizations.length).toBeGreaterThan(0);
    });

    it('should handle network optimization errors', async () => {
      const invalidRequests = [
        { url: 'invalid-url', method: 'GET', headers: {} },
        { url: 'https://example.com/api/users', method: 'GET', headers: {} }
      ];
      const result = await resourceOptimizationService.optimizeNetwork(invalidRequests);
      expect(result).toBeDefined();
      expect(result.success).toBe(false);
      expect(result.error).toBeDefined();
      expect(result.originalSize).toBeGreaterThan(0);
      expect(result.optimizedSize).toBe(0);
      expect(result.compressionRatio).toBe(0);
      expect(result.optimizations).toEqual([]);
    });
  });

  describe('Memory Optimization', () => {
    it('should optimize memory usage', async () => {
      const result = await resourceOptimizationService.optimizeMemory();
      expect(result).toBeDefined();
      expect(result.success).toBe(true);
      expect(result.originalSize).toBeGreaterThan(0);
      expect(result.optimizedSize).toBeGreaterThan(0);
      expect(result.compressionRatio).toBeGreaterThan(0);
      expect(result.optimizations).toBeDefined();
      expect(result.optimizations.length).toBeGreaterThan(0);
    });

    it('should optimize memory usage with custom options', async () => {
      const result = await resourceOptimizationService.optimizeMemory({
        enableGarbageCollection: true,
        enableMemoryPooling: true,
        enableObjectReuse: true,
        enableWeakReferences: true,
        maxMemoryUsage: 100 * 1024 * 1024, // 100MB
        enableMemoryMonitoring: true,
        enableMemoryProfiling: false,
        enableMemoryLeakDetection: true
      });
      expect(result).toBeDefined();
      expect(result.success).toBe(true);
      expect(result.originalSize).toBeGreaterThan(0);
      expect(result.optimizedSize).toBeGreaterThan(0);
      expect(result.compressionRatio).toBeGreaterThan(0);
      expect(result.optimizations).toBeDefined();
      expect(result.optimizations.length).toBeGreaterThan(0);
    });

    it('should handle memory optimization errors', async () => {
      // Mock memory optimization to throw error
      const originalOptimizeMemory = resourceOptimizationService.optimizeMemory;
      resourceOptimizationService.optimizeMemory = jest.fn().mockImplementation(() => {
        throw new Error('Memory optimization error');
      });

      const result = await resourceOptimizationService.optimizeMemory();
      expect(result).toBeDefined();
      expect(result.success).toBe(false);
      expect(result.error).toBeDefined();
      expect(result.originalSize).toBe(0);
      expect(result.optimizedSize).toBe(0);
      expect(result.compressionRatio).toBe(0);
      expect(result.optimizations).toEqual([]);

      // Restore original method
      resourceOptimizationService.optimizeMemory = originalOptimizeMemory;
    });
  });

  describe('Metrics', () => {
    it('should collect optimization metrics', async () => {
      // Perform some optimizations
      await resourceOptimizationService.optimizeImage('https://example.com/image.jpg');
      await resourceOptimizationService.optimizeFont('https://example.com/font.woff2');
      await resourceOptimizationService.optimizeCSS('.test { color: red; }');
      await resourceOptimizationService.optimizeJS('function test() { console.log("test"); }');

      const metrics = resourceOptimizationService.getMetrics();
      expect(metrics).toBeDefined();
      expect(metrics.totalOptimizations).toBeGreaterThan(0);
      expect(metrics.successfulOptimizations).toBeGreaterThan(0);
      expect(metrics.failedOptimizations).toBeGreaterThanOrEqual(0);
      expect(metrics.averageCompressionRatio).toBeGreaterThan(0);
      expect(metrics.optimizationsByType).toBeDefined();
      expect(metrics.optimizationsByType['image']).toBeGreaterThan(0);
      expect(metrics.optimizationsByType['font']).toBeGreaterThan(0);
      expect(metrics.optimizationsByType['css']).toBeGreaterThan(0);
      expect(metrics.optimizationsByType['js']).toBeGreaterThan(0);
      expect(metrics.optimizationsByType['bundle']).toBeGreaterThanOrEqual(0);
      expect(metrics.optimizationsByType['network']).toBeGreaterThanOrEqual(0);
      expect(metrics.optimizationsByType['memory']).toBeGreaterThanOrEqual(0);
      expect(metrics.totalBytesSaved).toBeGreaterThan(0);
      expect(metrics.averageBytesSaved).toBeGreaterThan(0);
      expect(metrics.optimizationTime).toBeGreaterThan(0);
      expect(metrics.cacheHitRate).toBeGreaterThanOrEqual(0);
      expect(metrics.cacheMissRate).toBeGreaterThanOrEqual(0);
      expect(metrics.lastUpdated).toBeDefined();
    });

    it('should reset metrics', async () => {
      // Perform some optimizations
      await resourceOptimizationService.optimizeImage('https://example.com/image.jpg');
      await resourceOptimizationService.optimizeFont('https://example.com/font.woff2');

      let metrics = resourceOptimizationService.getMetrics();
      expect(metrics.totalOptimizations).toBeGreaterThan(0);

      resourceOptimizationService.resetMetrics();

      metrics = resourceOptimizationService.getMetrics();
      expect(metrics.totalOptimizations).toBe(0);
      expect(metrics.successfulOptimizations).toBe(0);
      expect(metrics.failedOptimizations).toBe(0);
      expect(metrics.averageCompressionRatio).toBe(0);
      expect(metrics.optimizationsByType).toEqual({});
      expect(metrics.totalBytesSaved).toBe(0);
      expect(metrics.averageBytesSaved).toBe(0);
      expect(metrics.optimizationTime).toBe(0);
      expect(metrics.cacheHitRate).toBe(0);
      expect(metrics.cacheMissRate).toBe(0);
      expect(metrics.lastUpdated).toBeDefined();
    });
  });

  describe('Configuration', () => {
    it('should update configuration', () => {
      const newConfig = {
        enableImageOptimization: false,
        enableFontOptimization: false,
        enableCssOptimization: false,
        enableJsOptimization: false,
        enableBundleOptimization: false,
        enableNetworkOptimization: false,
        enableMemoryOptimization: false,
        imageQuality: 90,
        imageFormat: 'webp',
        fontDisplay: 'block',
        cssMinification: false,
        jsMinification: false,
        bundleSplitting: false,
        treeShaking: false,
        compressionLevel: 9,
        cacheStrategy: 'aggressive',
        preloadCriticalResources: false,
        lazyLoadNonCriticalResources: false,
        enableServiceWorker: true,
        enableCDN: true
      };

      resourceOptimizationService.updateConfig(newConfig);
      const config = resourceOptimizationService.getConfig();
      expect(config.enableImageOptimization).toBe(false);
      expect(config.enableFontOptimization).toBe(false);
      expect(config.enableCssOptimization).toBe(false);
      expect(config.enableJsOptimization).toBe(false);
      expect(config.enableBundleOptimization).toBe(false);
      expect(config.enableNetworkOptimization).toBe(false);
      expect(config.enableMemoryOptimization).toBe(false);
      expect(config.imageQuality).toBe(90);
      expect(config.imageFormat).toBe('webp');
      expect(config.fontDisplay).toBe('block');
      expect(config.cssMinification).toBe(false);
      expect(config.jsMinification).toBe(false);
      expect(config.bundleSplitting).toBe(false);
      expect(config.treeShaking).toBe(false);
      expect(config.compressionLevel).toBe(9);
      expect(config.cacheStrategy).toBe('aggressive');
      expect(config.preloadCriticalResources).toBe(false);
      expect(config.lazyLoadNonCriticalResources).toBe(false);
      expect(config.enableServiceWorker).toBe(true);
      expect(config.enableCDN).toBe(true);
    });

    it('should merge configuration properly', () => {
      const newConfig = {
        enableImageOptimization: false,
        enableFontOptimization: false,
        enableCssOptimization: false,
        enableJsOptimization: false,
        enableBundleOptimization: false,
        enableNetworkOptimization: false,
        enableMemoryOptimization: false,
        imageQuality: 90,
        imageFormat: 'webp',
        fontDisplay: 'block',
        cssMinification: false,
        jsMinification: false,
        bundleSplitting: false,
        treeShaking: false,
        compressionLevel: 9,
        cacheStrategy: 'aggressive',
        preloadCriticalResources: false,
        lazyLoadNonCriticalResources: false,
        enableServiceWorker: true,
        enableCDN: true
      };

      resourceOptimizationService.updateConfig(newConfig);
      const config = resourceOptimizationService.getConfig();
      expect(config.enableImageOptimization).toBe(false);
      expect(config.enableFontOptimization).toBe(false);
      expect(config.enableCssOptimization).toBe(false);
      expect(config.enableJsOptimization).toBe(false);
      expect(config.enableBundleOptimization).toBe(false);
      expect(config.enableNetworkOptimization).toBe(false);
      expect(config.enableMemoryOptimization).toBe(false);
      expect(config.imageQuality).toBe(90);
      expect(config.imageFormat).toBe('webp');
      expect(config.fontDisplay).toBe('block');
      expect(config.cssMinification).toBe(false);
      expect(config.jsMinification).toBe(false);
      expect(config.bundleSplitting).toBe(false);
      expect(config.treeShaking).toBe(false);
      expect(config.compressionLevel).toBe(9);
      expect(config.cacheStrategy).toBe('aggressive');
      expect(config.preloadCriticalResources).toBe(false);
      expect(config.lazyLoadNonCriticalResources).toBe(false);
      expect(config.enableServiceWorker).toBe(true);
      expect(config.enableCDN).toBe(true);
    });
  });

  describe('Error Handling', () => {
    it('should handle optimization errors gracefully', async () => {
      // Mock optimizeImage to throw error
      const originalOptimizeImage = resourceOptimizationService.optimizeImage;
      resourceOptimizationService.optimizeImage = jest.fn().mockImplementation(() => {
        throw new Error('Image optimization error');
      });

      // Should not throw error
      await expect(resourceOptimizationService.optimizeImage('https://example.com/image.jpg')).rejects.toThrow('Image optimization error');

      // Restore original method
      resourceOptimizationService.optimizeImage = originalOptimizeImage;
    });
  });

  describe('Cleanup', () => {
    it('should destroy service', async () => {
      // Perform some optimizations
      await resourceOptimizationService.optimizeImage('https://example.com/image.jpg');
      await resourceOptimizationService.optimizeFont('https://example.com/font.woff2');
      
      const metrics = resourceOptimizationService.getMetrics();
      expect(metrics.totalOptimizations).toBeGreaterThan(0);
      
      resourceOptimizationService.destroy();
      
      const metricsAfterDestroy = resourceOptimizationService.getMetrics();
      expect(metricsAfterDestroy.totalOptimizations).toBe(0);
    });
  });
});
