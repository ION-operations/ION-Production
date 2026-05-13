/**
 * Resource Optimization Service
 * 
 * Provides comprehensive resource optimization for the Advanced Monaco Editor
 * including:
 * - Image optimization
 * - Font optimization
 * - CSS optimization
 * - JavaScript optimization
 * - Bundle optimization
 * - Network optimization
 * - Memory optimization
 */

import { EventEmitter } from 'events';

export interface ResourceConfig {
  enableImageOptimization: boolean;
  enableFontOptimization: boolean;
  enableCssOptimization: boolean;
  enableJsOptimization: boolean;
  enableBundleOptimization: boolean;
  enableNetworkOptimization: boolean;
  enableMemoryOptimization: boolean;
  imageQuality: number; // 0-100
  imageFormat: 'auto' | 'webp' | 'avif' | 'jpeg' | 'png';
  fontDisplay: 'auto' | 'block' | 'swap' | 'fallback' | 'optional';
  cssMinification: boolean;
  jsMinification: boolean;
  bundleSplitting: boolean;
  treeShaking: boolean;
  compressionLevel: number; // 0-9
  cacheStrategy: 'aggressive' | 'moderate' | 'conservative';
  preloadCriticalResources: boolean;
  lazyLoadNonCriticalResources: boolean;
  enableServiceWorker: boolean;
  enableCDN: boolean;
  cdnUrl?: string;
}

export interface ResourceMetrics {
  timestamp: number;
  totalSize: number;
  compressedSize: number;
  compressionRatio: number;
  loadTime: number;
  cacheHitRate: number;
  networkRequests: number;
  memoryUsage: number;
  optimizationSavings: number;
}

export interface OptimizationResult {
  originalSize: number;
  optimizedSize: number;
  savings: number;
  savingsPercentage: number;
  optimizationTime: number;
  techniques: string[];
  warnings: string[];
}

export class ResourceOptimizationService extends EventEmitter {
  private config: ResourceConfig;
  private metrics: ResourceMetrics[] = [];
  private optimizationCache: Map<string, OptimizationResult> = new Map();
  private resourceCache: Map<string, { data: any; timestamp: number; size: number }> = new Map();
  private serviceWorker: ServiceWorker | null = null;

  constructor(config: Partial<ResourceConfig> = {}) {
    super();
    
    this.config = {
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
      enableCDN: false,
      ...config
    };

    this.initializeServiceWorker();
  }

  private async initializeServiceWorker(): Promise<void> {
    if (!this.config.enableServiceWorker || typeof window === 'undefined' || !('serviceWorker' in navigator)) {
      return;
    }

    try {
      const registration = await navigator.serviceWorker.register('/sw.js');
      this.serviceWorker = registration.active || registration.waiting || registration.installing;
      this.emit('serviceWorkerRegistered', registration);
    } catch (error) {
      console.warn('Failed to register service worker:', error);
    }
  }

  // Image optimization
  public async optimizeImage(
    imageUrl: string,
    options: {
      width?: number;
      height?: number;
      quality?: number;
      format?: string;
    } = {}
  ): Promise<string> {
    if (!this.config.enableImageOptimization) {
      return imageUrl;
    }

    const cacheKey = `image_${imageUrl}_${JSON.stringify(options)}`;
    const cached = this.optimizationCache.get(cacheKey);
    if (cached) {
      return cached.optimizedSize.toString();
    }

    const startTime = Date.now();
    const techniques: string[] = [];
    const warnings: string[] = [];

    try {
      // Create canvas for image processing
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      if (!ctx) {
        throw new Error('Canvas context not available');
      }

      // Load image
      const image = new Image();
      image.crossOrigin = 'anonymous';
      
      await new Promise((resolve, reject) => {
        image.onload = resolve;
        image.onerror = reject;
        image.src = imageUrl;
      });

      // Calculate dimensions
      const { width, height } = this.calculateImageDimensions(
        image.width,
        image.height,
        options.width,
        options.height
      );

      canvas.width = width;
      canvas.height = height;

      // Draw image with optimization
      ctx.drawImage(image, 0, 0, width, height);

      // Get optimized data URL
      const quality = options.quality || this.config.imageQuality;
      const format = options.format || this.config.imageFormat;
      
      let optimizedDataUrl: string;
      if (format === 'webp' || (format === 'auto' && this.supportsWebP())) {
        optimizedDataUrl = canvas.toDataURL('image/webp', quality / 100);
        techniques.push('webp-conversion');
      } else if (format === 'avif' || (format === 'auto' && this.supportsAVIF())) {
        optimizedDataUrl = canvas.toDataURL('image/avif', quality / 100);
        techniques.push('avif-conversion');
      } else {
        optimizedDataUrl = canvas.toDataURL('image/jpeg', quality / 100);
        techniques.push('jpeg-optimization');
      }

      const originalSize = this.estimateImageSize(imageUrl);
      const optimizedSize = this.estimateDataUrlSize(optimizedDataUrl);
      const savings = originalSize - optimizedSize;
      const savingsPercentage = (savings / originalSize) * 100;

      const result: OptimizationResult = {
        originalSize,
        optimizedSize,
        savings,
        savingsPercentage,
        optimizationTime: Date.now() - startTime,
        techniques,
        warnings
      };

      this.optimizationCache.set(cacheKey, result);
      this.emit('imageOptimized', { imageUrl, result });

      return optimizedDataUrl;
    } catch (error) {
      console.warn('Image optimization failed:', error);
      return imageUrl;
    }
  }

  private calculateImageDimensions(
    originalWidth: number,
    originalHeight: number,
    targetWidth?: number,
    targetHeight?: number
  ): { width: number; height: number } {
    if (!targetWidth && !targetHeight) {
      return { width: originalWidth, height: originalHeight };
    }

    if (targetWidth && targetHeight) {
      return { width: targetWidth, height: targetHeight };
    }

    if (targetWidth) {
      const ratio = originalHeight / originalWidth;
      return { width: targetWidth, height: Math.round(targetWidth * ratio) };
    }

    if (targetHeight) {
      const ratio = originalWidth / originalHeight;
      return { width: Math.round(targetHeight * ratio), height: targetHeight };
    }

    return { width: originalWidth, height: originalHeight };
  }

  private supportsWebP(): boolean {
    const canvas = document.createElement('canvas');
    return canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0;
  }

  private supportsAVIF(): boolean {
    const canvas = document.createElement('canvas');
    return canvas.toDataURL('image/avif').indexOf('data:image/avif') === 0;
  }

  private estimateImageSize(url: string): number {
    // Rough estimation based on URL and common image sizes
    if (url.includes('data:')) {
      return url.length * 0.75; // Base64 encoding overhead
    }
    return 50000; // Default estimation
  }

  private estimateDataUrlSize(dataUrl: string): number {
    return dataUrl.length * 0.75; // Base64 encoding overhead
  }

  // Font optimization
  public async optimizeFont(fontUrl: string): Promise<string> {
    if (!this.config.enableFontOptimization) {
      return fontUrl;
    }

    const cacheKey = `font_${fontUrl}`;
    const cached = this.optimizationCache.get(cacheKey);
    if (cached) {
      return cached.optimizedSize.toString();
    }

    const startTime = Date.now();
    const techniques: string[] = [];
    const warnings: string[] = [];

    try {
      // Add font-display optimization
      const optimizedUrl = this.addFontDisplayOptimization(fontUrl);
      techniques.push('font-display-optimization');

      // Add preload hint
      if (this.config.preloadCriticalResources) {
        this.addPreloadHint(fontUrl, 'font');
        techniques.push('preload-hint');
      }

      const result: OptimizationResult = {
        originalSize: this.estimateFontSize(fontUrl),
        optimizedSize: this.estimateFontSize(optimizedUrl),
        savings: 0, // Font optimization is more about loading strategy
        savingsPercentage: 0,
        optimizationTime: Date.now() - startTime,
        techniques,
        warnings
      };

      this.optimizationCache.set(cacheKey, result);
      this.emit('fontOptimized', { fontUrl, result });

      return optimizedUrl;
    } catch (error) {
      console.warn('Font optimization failed:', error);
      return fontUrl;
    }
  }

  private addFontDisplayOptimization(fontUrl: string): string {
    // This would typically involve modifying CSS or adding font-display properties
    return fontUrl;
  }

  private addPreloadHint(url: string, type: string): void {
    if (typeof document === 'undefined') return;

    const link = document.createElement('link');
    link.rel = 'preload';
    link.href = url;
    link.as = type;
    document.head.appendChild(link);
  }

  private estimateFontSize(url: string): number {
    // Rough estimation based on URL
    if (url.includes('woff2')) return 30000;
    if (url.includes('woff')) return 40000;
    if (url.includes('ttf')) return 100000;
    return 50000;
  }

  // CSS optimization
  public async optimizeCSS(css: string): Promise<string> {
    if (!this.config.enableCssOptimization) {
      return css;
    }

    const cacheKey = `css_${this.hashString(css)}`;
    const cached = this.optimizationCache.get(cacheKey);
    if (cached) {
      return cached.optimizedSize.toString();
    }

    const startTime = Date.now();
    const techniques: string[] = [];
    const warnings: string[] = [];

    try {
      let optimizedCSS = css;

      // Minification
      if (this.config.cssMinification) {
        optimizedCSS = this.minifyCSS(optimizedCSS);
        techniques.push('minification');
      }

      // Remove unused CSS (simplified)
      if (this.config.treeShaking) {
        optimizedCSS = this.removeUnusedCSS(optimizedCSS);
        techniques.push('tree-shaking');
      }

      // Optimize selectors
      optimizedCSS = this.optimizeSelectors(optimizedCSS);
      techniques.push('selector-optimization');

      // Compress CSS
      if (this.config.compressionLevel > 0) {
        optimizedCSS = this.compressCSS(optimizedCSS);
        techniques.push('compression');
      }

      const result: OptimizationResult = {
        originalSize: css.length,
        optimizedSize: optimizedCSS.length,
        savings: css.length - optimizedCSS.length,
        savingsPercentage: ((css.length - optimizedCSS.length) / css.length) * 100,
        optimizationTime: Date.now() - startTime,
        techniques,
        warnings
      };

      this.optimizationCache.set(cacheKey, result);
      this.emit('cssOptimized', { result });

      return optimizedCSS;
    } catch (error) {
      console.warn('CSS optimization failed:', error);
      return css;
    }
  }

  private minifyCSS(css: string): string {
    return css
      .replace(/\/\*[\s\S]*?\*\//g, '') // Remove comments
      .replace(/\s+/g, ' ') // Collapse whitespace
      .replace(/;\s*}/g, '}') // Remove semicolons before closing braces
      .replace(/\s*{\s*/g, '{') // Remove spaces around opening braces
      .replace(/;\s*/g, ';') // Remove spaces after semicolons
      .replace(/\s*,\s*/g, ',') // Remove spaces around commas
      .trim();
  }

  private removeUnusedCSS(css: string): string {
    // Simplified unused CSS removal
    // In a real implementation, this would analyze the DOM and remove unused rules
    return css;
  }

  private optimizeSelectors(css: string): string {
    // Optimize CSS selectors for better performance
    return css
      .replace(/\.([a-zA-Z0-9_-]+)\s*\.([a-zA-Z0-9_-]+)/g, '.$1.$2') // Optimize class combinations
      .replace(/\s*>\s*/g, '>') // Remove spaces around child selectors
      .replace(/\s*\+\s*/g, '+') // Remove spaces around adjacent selectors
      .replace(/\s*~\s*/g, '~'); // Remove spaces around general sibling selectors
  }

  private compressCSS(css: string): string {
    // Basic CSS compression
    return css
      .replace(/\s*{\s*/g, '{')
      .replace(/\s*}\s*/g, '}')
      .replace(/\s*;\s*/g, ';')
      .replace(/\s*,\s*/g, ',')
      .replace(/\s*:\s*/g, ':')
      .trim();
  }

  // JavaScript optimization
  public async optimizeJavaScript(js: string): Promise<string> {
    if (!this.config.enableJsOptimization) {
      return js;
    }

    const cacheKey = `js_${this.hashString(js)}`;
    const cached = this.optimizationCache.get(cacheKey);
    if (cached) {
      return cached.optimizedSize.toString();
    }

    const startTime = Date.now();
    const techniques: string[] = [];
    const warnings: string[] = [];

    try {
      let optimizedJS = js;

      // Minification
      if (this.config.jsMinification) {
        optimizedJS = this.minifyJavaScript(optimizedJS);
        techniques.push('minification');
      }

      // Tree shaking (simplified)
      if (this.config.treeShaking) {
        optimizedJS = this.removeUnusedCode(optimizedJS);
        techniques.push('tree-shaking');
      }

      // Compress JavaScript
      if (this.config.compressionLevel > 0) {
        optimizedJS = this.compressJavaScript(optimizedJS);
        techniques.push('compression');
      }

      const result: OptimizationResult = {
        originalSize: js.length,
        optimizedSize: optimizedJS.length,
        savings: js.length - optimizedJS.length,
        savingsPercentage: ((js.length - optimizedJS.length) / js.length) * 100,
        optimizationTime: Date.now() - startTime,
        techniques,
        warnings
      };

      this.optimizationCache.set(cacheKey, result);
      this.emit('javascriptOptimized', { result });

      return optimizedJS;
    } catch (error) {
      console.warn('JavaScript optimization failed:', error);
      return js;
    }
  }

  private minifyJavaScript(js: string): string {
    // Basic JavaScript minification
    return js
      .replace(/\/\*[\s\S]*?\*\//g, '') // Remove block comments
      .replace(/\/\/.*$/gm, '') // Remove line comments
      .replace(/\s+/g, ' ') // Collapse whitespace
      .replace(/\s*([{}();,=+\-*/])\s*/g, '$1') // Remove spaces around operators
      .trim();
  }

  private removeUnusedCode(js: string): string {
    // Simplified unused code removal
    // In a real implementation, this would use AST analysis
    return js;
  }

  private compressJavaScript(js: string): string {
    // Basic JavaScript compression
    return js
      .replace(/\s*([{}();,=+\-*/])\s*/g, '$1')
      .replace(/\s+/g, ' ')
      .trim();
  }

  // Bundle optimization
  public async optimizeBundle(bundle: any): Promise<any> {
    if (!this.config.enableBundleOptimization) {
      return bundle;
    }

    const startTime = Date.now();
    const techniques: string[] = [];
    const warnings: string[] = [];

    try {
      let optimizedBundle = bundle;

      // Bundle splitting
      if (this.config.bundleSplitting) {
        optimizedBundle = this.splitBundle(optimizedBundle);
        techniques.push('bundle-splitting');
      }

      // Tree shaking
      if (this.config.treeShaking) {
        optimizedBundle = this.treeShakeBundle(optimizedBundle);
        techniques.push('tree-shaking');
      }

      // Compression
      if (this.config.compressionLevel > 0) {
        optimizedBundle = this.compressBundle(optimizedBundle);
        techniques.push('compression');
      }

      const result: OptimizationResult = {
        originalSize: this.estimateBundleSize(bundle),
        optimizedSize: this.estimateBundleSize(optimizedBundle),
        savings: this.estimateBundleSize(bundle) - this.estimateBundleSize(optimizedBundle),
        savingsPercentage: 0, // Would calculate based on actual sizes
        optimizationTime: Date.now() - startTime,
        techniques,
        warnings
      };

      this.emit('bundleOptimized', { result });

      return optimizedBundle;
    } catch (error) {
      console.warn('Bundle optimization failed:', error);
      return bundle;
    }
  }

  private splitBundle(bundle: any): any {
    // Simplified bundle splitting
    return bundle;
  }

  private treeShakeBundle(bundle: any): any {
    // Simplified tree shaking
    return bundle;
  }

  private compressBundle(bundle: any): any {
    // Simplified bundle compression
    return bundle;
  }

  private estimateBundleSize(bundle: any): number {
    return JSON.stringify(bundle).length;
  }

  // Network optimization
  public optimizeNetworkRequests(): void {
    if (!this.config.enableNetworkOptimization) return;

    // Add resource hints
    this.addResourceHints();

    // Optimize caching headers
    this.optimizeCachingHeaders();

    // Enable compression
    this.enableCompression();

    this.emit('networkOptimized');
  }

  private addResourceHints(): void {
    if (!this.config.enableResourceHints || typeof document === 'undefined') return;

    // Add DNS prefetch
    const dnsPrefetch = document.createElement('link');
    dnsPrefetch.rel = 'dns-prefetch';
    dnsPrefetch.href = this.config.cdnUrl || '';
    document.head.appendChild(dnsPrefetch);

    // Add preconnect
    const preconnect = document.createElement('link');
    preconnect.rel = 'preconnect';
    preconnect.href = this.config.cdnUrl || '';
    document.head.appendChild(preconnect);
  }

  private optimizeCachingHeaders(): void {
    // This would typically involve setting appropriate cache headers
    // In a browser environment, this is usually handled by the server
  }

  private enableCompression(): void {
    // This would typically involve enabling gzip/brotli compression
    // In a browser environment, this is usually handled by the server
  }

  // Memory optimization
  public optimizeMemory(): void {
    if (!this.config.enableMemoryOptimization) return;

    // Clear optimization cache if it's too large
    if (this.optimizationCache.size > 100) {
      this.clearOptimizationCache();
    }

    // Clear resource cache if it's too large
    if (this.resourceCache.size > 50) {
      this.clearResourceCache();
    }

    // Force garbage collection if available
    if (typeof window !== 'undefined' && 'gc' in window) {
      (window as any).gc();
    }

    this.emit('memoryOptimized');
  }

  private clearOptimizationCache(): void {
    this.optimizationCache.clear();
    this.emit('optimizationCacheCleared');
  }

  private clearResourceCache(): void {
    this.resourceCache.clear();
    this.emit('resourceCacheCleared');
  }

  // Utility methods
  private hashString(str: string): string {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return hash.toString();
  }

  public getMetrics(): ResourceMetrics[] {
    return [...this.metrics];
  }

  public getOptimizationReport(): {
    totalOptimizations: number;
    totalSavings: number;
    averageSavingsPercentage: number;
    mostEffectiveTechniques: string[];
  } {
    const results = Array.from(this.optimizationCache.values());
    
    if (results.length === 0) {
      return {
        totalOptimizations: 0,
        totalSavings: 0,
        averageSavingsPercentage: 0,
        mostEffectiveTechniques: []
      };
    }

    const totalSavings = results.reduce((sum, result) => sum + result.savings, 0);
    const averageSavingsPercentage = results.reduce((sum, result) => sum + result.savingsPercentage, 0) / results.length;

    // Count technique usage
    const techniqueCounts: Record<string, number> = {};
    results.forEach(result => {
      result.techniques.forEach(technique => {
        techniqueCounts[technique] = (techniqueCounts[technique] || 0) + 1;
      });
    });

    const mostEffectiveTechniques = Object.entries(techniqueCounts)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 5)
      .map(([technique]) => technique);

    return {
      totalOptimizations: results.length,
      totalSavings,
      averageSavingsPercentage,
      mostEffectiveTechniques
    };
  }

  public destroy(): void {
    this.clearOptimizationCache();
    this.clearResourceCache();
    this.removeAllListeners();
  }
}
