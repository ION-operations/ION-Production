/**
 * LOD Manager - Automatic Level of Detail Selection and Mesh Simplification
 * @module @lumin/snap-system/utils/LODManager
 * 
 * NL_TAG: LUMIN-LOD-001 | Manages level of detail for ghost preview performance | LODManager class | [GhostPreviewRenderer]
 * NL_TAG_INTENT: LUMIN-PERF-001 | Ensures 60 FPS ghost rendering by auto-selecting appropriate LOD | polygon-based selection | [PERFORMANCE_REQUIREMENTS]
 */

import * as THREE from 'three';
import { LODLevel, LODCacheEntry, LODStats, LOD_THRESHOLDS } from '../types';

/**
 * LOD Manager Singleton
 * 
 * Provides automatic level-of-detail selection and mesh simplification
 * to maintain 60 FPS during ghost preview rendering.
 * 
 * @example
 * ```typescript
 * import { LODManager } from '@lumin/snap-system';
 * 
 * const manager = LODManager.getInstance();
 * const level = manager.selectLOD(mesh);
 * const ghost = manager.createLODObject(mesh, level);
 * ```
 */
export class LODManager {
  private static instance: LODManager | null = null;
  
  /** LOD object cache: key = `${uuid}_${level}` */
  private cache: Map<string, LODCacheEntry> = new Map();
  
  /** Render time history per object */
  private renderHistory: Map<string, number[]> = new Map();
  
  /** Cache statistics */
  private stats = {
    hits: 0,
    misses: 0,
    totalRenderTime: 0,
    renderCount: 0
  };
  
  /** Maximum cache entries before cleanup */
  private readonly MAX_CACHE_SIZE = 100;
  
  /** Maximum render history samples per object */
  private readonly MAX_HISTORY_SAMPLES = 10;

  private constructor() {
    // Private constructor for singleton
  }

  /**
   * Get singleton instance
   */
  static getInstance(): LODManager {
    if (!LODManager.instance) {
      LODManager.instance = new LODManager();
    }
    return LODManager.instance;
  }

  /**
   * Reset singleton (for testing)
   */
  static resetInstance(): void {
    if (LODManager.instance) {
      LODManager.instance.clearCache();
      LODManager.instance = null;
    }
  }

  // ============================================
  // LOD Selection
  // ============================================

  /**
   * Select appropriate LOD level based on polygon count and performance history
   */
  selectLOD(object: THREE.Object3D): LODLevel {
    const polyCount = this.countPolygons(object);
    const avgRenderTime = this.getAverageRenderTime(object.uuid);
    
    // If we have performance history and it's slow, downgrade
    if (avgRenderTime > 0) {
      if (avgRenderTime > LOD_THRESHOLDS.BOUNDING_BOX.targetMs) {
        return LODLevel.BOUNDING_BOX;
      }
      if (avgRenderTime > LOD_THRESHOLDS.WIREFRAME.targetMs) {
        return LODLevel.WIREFRAME;
      }
      if (avgRenderTime > LOD_THRESHOLDS.SIMPLIFIED_MESH.targetMs) {
        return LODLevel.SIMPLIFIED_MESH;
      }
    }
    
    // Standard polygon-based selection
    if (polyCount < LOD_THRESHOLDS.FULL_DETAIL.maxPolygons) {
      return LODLevel.FULL_DETAIL;
    }
    if (polyCount < LOD_THRESHOLDS.SIMPLIFIED_MESH.maxPolygons) {
      return LODLevel.SIMPLIFIED_MESH;
    }
    if (polyCount < LOD_THRESHOLDS.WIREFRAME.maxPolygons) {
      return LODLevel.WIREFRAME;
    }
    
    return LODLevel.BOUNDING_BOX;
  }

  /**
   * Count total polygons (triangles) in object including children
   */
  countPolygons(object: THREE.Object3D): number {
    let count = 0;
    
    object.traverse((child) => {
      if (child instanceof THREE.Mesh && child.geometry) {
        const geometry = child.geometry;
        
        // Check for indexed geometry
        if (geometry.index) {
          count += geometry.index.count / 3;
        } else {
          const positions = geometry.attributes.position;
          if (positions) {
            count += positions.count / 3;
          }
        }
      }
    });
    
    return Math.floor(count);
  }

  // ============================================
  // LOD Object Creation
  // ============================================

  /**
   * Create LOD version of object based on specified level
   */
  createLODObject(object: THREE.Object3D, level: LODLevel): THREE.Object3D {
    // Check cache first
    const cacheKey = this.getCacheKey(object, level);
    const cached = this.cache.get(cacheKey);
    
    if (cached) {
      this.stats.hits++;
      cached.accessCount++;
      return cached.object.clone();
    }
    
    this.stats.misses++;
    
    // Create LOD object based on level
    let lodObject: THREE.Object3D;
    
    switch (level) {
      case LODLevel.FULL_DETAIL:
        lodObject = this.createFullDetail(object);
        break;
      case LODLevel.SIMPLIFIED_MESH:
        lodObject = this.createSimplifiedMesh(object, 0.5);
        break;
      case LODLevel.WIREFRAME:
        lodObject = this.createWireframe(object);
        break;
      case LODLevel.BOUNDING_BOX:
      default:
        lodObject = this.createBoundingBox(object);
        break;
    }
    
    // Add to cache
    this.addToCache(cacheKey, lodObject, level);
    
    return lodObject.clone();
  }

  /**
   * Full detail: Clone entire object
   */
  private createFullDetail(object: THREE.Object3D): THREE.Object3D {
    const clone = object.clone();
    
    // Reset position (will be set by GhostPreviewRenderer)
    clone.position.set(0, 0, 0);
    
    return clone;
  }

  /**
   * Simplified mesh: Reduce polygon count
   * Uses edge decimation algorithm for simplification
   */
  private createSimplifiedMesh(object: THREE.Object3D, ratio: number): THREE.Object3D {
    const simplified = new THREE.Group();
    
    object.traverse((child) => {
      if (child instanceof THREE.Mesh && child.geometry) {
        try {
          // Clone geometry for modification
          const geometry = child.geometry.clone();
          
          // Simple decimation: Keep every Nth vertex
          // (For production, use proper SimplifyModifier from three/examples)
          const simplifiedGeo = this.decimateGeometry(geometry, ratio);
          
          const mesh = new THREE.Mesh(simplifiedGeo, child.material);
          mesh.position.copy(child.position);
          mesh.rotation.copy(child.rotation);
          mesh.scale.copy(child.scale);
          
          simplified.add(mesh);
        } catch (error) {
          console.warn('[LODManager] Simplification failed, using bounding box:', error);
          return this.createBoundingBox(object);
        }
      }
    });
    
    return simplified.children.length > 0 ? simplified : this.createBoundingBox(object);
  }

  /**
   * Simple geometry decimation (placeholder for proper SimplifyModifier)
   */
  private decimateGeometry(geometry: THREE.BufferGeometry, ratio: number): THREE.BufferGeometry {
    const positions = geometry.attributes.position;
    if (!positions) return geometry;
    
    const step = Math.max(1, Math.floor(1 / ratio));
    const newPositions: number[] = [];
    
    for (let i = 0; i < positions.count; i += step * 3) {
      // Keep every Nth triangle (3 vertices)
      for (let j = 0; j < 3 && (i + j) < positions.count; j++) {
        const idx = i + j;
        newPositions.push(
          positions.getX(idx),
          positions.getY(idx),
          positions.getZ(idx)
        );
      }
    }
    
    const decimated = new THREE.BufferGeometry();
    decimated.setAttribute(
      'position',
      new THREE.Float32BufferAttribute(newPositions, 3)
    );
    
    return decimated;
  }

  /**
   * Wireframe: Bounding box + wireframe edges
   */
  private createWireframe(object: THREE.Object3D): THREE.Object3D {
    const group = new THREE.Group();
    
    // Create bounding box helper
    const box = new THREE.Box3().setFromObject(object);
    const boxHelper = new THREE.Box3Helper(box, 0x00ffff);
    group.add(boxHelper);
    
    // Add wireframe for each mesh
    object.traverse((child) => {
      if (child instanceof THREE.Mesh && child.geometry) {
        const wireframe = new THREE.WireframeGeometry(child.geometry);
        const line = new THREE.LineSegments(
          wireframe,
          new THREE.LineBasicMaterial({
            color: 0x00ffff,
            transparent: true,
            opacity: 0.3
          })
        );
        
        // Apply transforms
        line.position.copy(child.position);
        line.rotation.copy(child.rotation);
        line.scale.copy(child.scale);
        
        group.add(line);
      }
    });
    
    return group;
  }

  /**
   * Bounding box only: Fastest rendering
   */
  private createBoundingBox(object: THREE.Object3D): THREE.Object3D {
    const box = new THREE.Box3().setFromObject(object);
    
    const size = new THREE.Vector3();
    box.getSize(size);
    
    const geometry = new THREE.BoxGeometry(size.x, size.y, size.z);
    const material = new THREE.MeshBasicMaterial({
      color: 0x00ffff,
      wireframe: true,
      transparent: true,
      opacity: 0.5
    });
    
    const bbox = new THREE.Mesh(geometry, material);
    
    // Position at center of bounding box
    const center = new THREE.Vector3();
    box.getCenter(center);
    bbox.userData.originalCenter = center.clone();
    
    return bbox;
  }

  // ============================================
  // Caching
  // ============================================

  private getCacheKey(object: THREE.Object3D, level: LODLevel): string {
    return `${object.uuid}_${level}`;
  }

  private addToCache(key: string, object: THREE.Object3D, level: LODLevel): void {
    // Cleanup if cache is full
    if (this.cache.size >= this.MAX_CACHE_SIZE) {
      this.cleanupCache();
    }
    
    this.cache.set(key, {
      object,
      level,
      createdAt: Date.now(),
      accessCount: 1
    });
  }

  /**
   * Remove least recently used entries
   */
  private cleanupCache(): void {
    const entries = Array.from(this.cache.entries());
    
    // Sort by access count (ascending) and age (oldest first)
    entries.sort((a, b) => {
      if (a[1].accessCount !== b[1].accessCount) {
        return a[1].accessCount - b[1].accessCount;
      }
      return a[1].createdAt - b[1].createdAt;
    });
    
    // Remove bottom 25%
    const removeCount = Math.floor(this.MAX_CACHE_SIZE * 0.25);
    for (let i = 0; i < removeCount && i < entries.length; i++) {
      this.disposeEntry(entries[i][1]);
      this.cache.delete(entries[i][0]);
    }
  }

  /**
   * Dispose of cached entry to prevent memory leaks
   */
  private disposeEntry(entry: LODCacheEntry): void {
    entry.object.traverse((child) => {
      if (child instanceof THREE.Mesh) {
        child.geometry?.dispose();
        
        if (Array.isArray(child.material)) {
          child.material.forEach(m => m.dispose());
        } else {
          child.material?.dispose();
        }
      }
    });
  }

  /**
   * Clear entire cache
   */
  clearCache(): void {
    this.cache.forEach(entry => this.disposeEntry(entry));
    this.cache.clear();
    this.renderHistory.clear();
    this.stats = { hits: 0, misses: 0, totalRenderTime: 0, renderCount: 0 };
  }

  // ============================================
  // Performance Tracking
  // ============================================

  /**
   * Record render time for performance tracking
   */
  recordRenderTime(objectId: string, renderTimeMs: number): void {
    if (!this.renderHistory.has(objectId)) {
      this.renderHistory.set(objectId, []);
    }
    
    const history = this.renderHistory.get(objectId)!;
    history.push(renderTimeMs);
    
    // Keep limited history
    if (history.length > this.MAX_HISTORY_SAMPLES) {
      history.shift();
    }
    
    // Update global stats
    this.stats.totalRenderTime += renderTimeMs;
    this.stats.renderCount++;
  }

  /**
   * Get average render time for object
   */
  private getAverageRenderTime(objectId: string): number {
    const history = this.renderHistory.get(objectId);
    if (!history || history.length === 0) return 0;
    
    const sum = history.reduce((a, b) => a + b, 0);
    return sum / history.length;
  }

  // ============================================
  // Statistics
  // ============================================

  /**
   * Get cache and performance statistics
   */
  getStats(): LODStats {
    return {
      cacheEntries: this.cache.size,
      cacheHits: this.stats.hits,
      cacheMisses: this.stats.misses,
      averageRenderTimeMs: this.stats.renderCount > 0 
        ? this.stats.totalRenderTime / this.stats.renderCount 
        : 0,
      memoryUsageMB: this.estimateMemoryUsage()
    };
  }

  /**
   * Estimate memory usage of cache (rough estimate)
   */
  private estimateMemoryUsage(): number {
    let totalPolygons = 0;
    
    this.cache.forEach(entry => {
      totalPolygons += this.countPolygons(entry.object);
    });
    
    // Rough estimate: 36 bytes per triangle (3 vertices * 3 floats * 4 bytes)
    const bytesPerTriangle = 36;
    return (totalPolygons * bytesPerTriangle) / (1024 * 1024);
  }
}

/**
 * Default LODManager instance
 */
export default LODManager.getInstance();

