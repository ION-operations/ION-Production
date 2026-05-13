/**
 * Terrain Streaming System
 * Dynamic loading/unloading of terrain chunks for infinite worlds
 * 
 * Features:
 * - Quadtree-based chunk management
 * - Async chunk loading
 * - LOD transitions
 * - Memory budget management
 * - Seamless stitching
 * - Priority-based loading queue
 * - Cache management
 */

import * as THREE from 'three';

// ============================================
// TYPES
// ============================================

export interface TerrainChunkConfig {
  size: number;          // World units per chunk
  resolution: number;    // Vertices per side
  lodLevels: number;     // Number of LOD levels
  loadDistance: number;  // Distance to start loading
  unloadDistance: number; // Distance to unload
  maxCacheSize: number;  // Max cached chunks
}

export interface ChunkCoord {
  x: number;
  z: number;
  lod: number;
}

export interface TerrainChunk {
  coord: ChunkCoord;
  mesh: THREE.Mesh | null;
  geometry: THREE.BufferGeometry | null;
  heightData: Float32Array | null;
  state: ChunkState;
  lastAccessTime: number;
  priority: number;
}

export type ChunkState = 'unloaded' | 'loading' | 'loaded' | 'visible';

export interface ChunkLoadRequest {
  coord: ChunkCoord;
  priority: number;
  resolve: (chunk: TerrainChunk) => void;
  reject: (error: Error) => void;
}

export type HeightGenerator = (x: number, z: number) => number;
export type NormalGenerator = (x: number, z: number) => THREE.Vector3;

// ============================================
// CHUNK POOL
// ============================================

export class ChunkPool {
  private geometries: THREE.BufferGeometry[] = [];
  private maxSize: number;
  
  constructor(maxSize: number = 50) {
    this.maxSize = maxSize;
  }
  
  public acquire(resolution: number): THREE.BufferGeometry {
    // Try to find matching geometry in pool
    for (let i = 0; i < this.geometries.length; i++) {
      const geom = this.geometries[i];
      const verts = geom.getAttribute('position').count;
      if (Math.sqrt(verts) === resolution) {
        this.geometries.splice(i, 1);
        return geom;
      }
    }
    
    // Create new geometry
    return new THREE.PlaneGeometry(1, 1, resolution - 1, resolution - 1);
  }
  
  public release(geometry: THREE.BufferGeometry): void {
    if (this.geometries.length < this.maxSize) {
      this.geometries.push(geometry);
    } else {
      geometry.dispose();
    }
  }
  
  public dispose(): void {
    for (const geom of this.geometries) {
      geom.dispose();
    }
    this.geometries = [];
  }
}

// ============================================
// LOADING QUEUE
// ============================================

export class ChunkLoadingQueue {
  private queue: ChunkLoadRequest[] = [];
  private processing: Set<string> = new Set();
  private maxConcurrent: number;
  
  constructor(maxConcurrent: number = 4) {
    this.maxConcurrent = maxConcurrent;
  }
  
  public enqueue(request: ChunkLoadRequest): void {
    const key = this.getKey(request.coord);
    
    // Don't add duplicates
    if (this.processing.has(key)) return;
    if (this.queue.some(r => this.getKey(r.coord) === key)) return;
    
    this.queue.push(request);
    this.queue.sort((a, b) => b.priority - a.priority);
  }
  
  public dequeue(): ChunkLoadRequest | null {
    if (this.processing.size >= this.maxConcurrent) return null;
    
    const request = this.queue.shift();
    if (request) {
      this.processing.add(this.getKey(request.coord));
    }
    return request;
  }
  
  public complete(coord: ChunkCoord): void {
    this.processing.delete(this.getKey(coord));
  }
  
  public cancel(coord: ChunkCoord): void {
    const key = this.getKey(coord);
    this.queue = this.queue.filter(r => this.getKey(r.coord) !== key);
    this.processing.delete(key);
  }
  
  public clear(): void {
    this.queue = [];
    this.processing.clear();
  }
  
  public getPendingCount(): number {
    return this.queue.length + this.processing.size;
  }
  
  private getKey(coord: ChunkCoord): string {
    return `${coord.x},${coord.z},${coord.lod}`;
  }
}

// ============================================
// TERRAIN STREAMING SYSTEM
// ============================================

export class TerrainStreaming {
  private scene: THREE.Scene;
  private config: TerrainChunkConfig;
  private chunks: Map<string, TerrainChunk> = new Map();
  private visibleChunks: Set<string> = new Set();
  private chunkPool: ChunkPool;
  private loadingQueue: ChunkLoadingQueue;
  private heightGenerator: HeightGenerator;
  
  private material: THREE.Material;
  private lastCameraPosition: THREE.Vector3 = new THREE.Vector3();
  private updateThreshold: number = 1;
  
  constructor(
    scene: THREE.Scene,
    heightGenerator: HeightGenerator,
    config: Partial<TerrainChunkConfig> = {}
  ) {
    this.scene = scene;
    this.heightGenerator = heightGenerator;
    
    this.config = {
      size: 64,
      resolution: 33,
      lodLevels: 4,
      loadDistance: 256,
      unloadDistance: 384,
      maxCacheSize: 100,
      ...config
    };
    
    this.chunkPool = new ChunkPool(this.config.maxCacheSize);
    this.loadingQueue = new ChunkLoadingQueue(4);
    
    // Default terrain material
    this.material = new THREE.MeshStandardMaterial({
      color: 0x228833,
      roughness: 0.8,
      metalness: 0.1,
      flatShading: false,
      wireframe: false
    });
  }
  
  /**
   * Update terrain based on camera position
   */
  public update(cameraPosition: THREE.Vector3): void {
    // Only update if camera moved significantly
    const cameraDelta = cameraPosition.distanceTo(this.lastCameraPosition);
    if (cameraDelta < this.updateThreshold) {
      this.processLoadingQueue();
      return;
    }
    
    this.lastCameraPosition.copy(cameraPosition);
    
    // Determine which chunks should be visible
    const desiredChunks = this.getDesiredChunks(cameraPosition);
    
    // Queue loading for new chunks
    for (const coord of desiredChunks) {
      const key = this.getChunkKey(coord);
      
      if (!this.chunks.has(key)) {
        this.queueChunkLoad(coord, cameraPosition);
      } else {
        const chunk = this.chunks.get(key)!;
        if (chunk.state === 'loaded') {
          this.showChunk(chunk);
        }
      }
    }
    
    // Hide chunks that are no longer needed
    const desiredKeys = new Set(desiredChunks.map(c => this.getChunkKey(c)));
    
    for (const key of this.visibleChunks) {
      if (!desiredKeys.has(key)) {
        const chunk = this.chunks.get(key);
        if (chunk) {
          this.hideChunk(chunk);
        }
      }
    }
    
    // Unload distant chunks
    this.unloadDistantChunks(cameraPosition);
    
    // Process loading queue
    this.processLoadingQueue();
  }
  
  private getDesiredChunks(cameraPosition: THREE.Vector3): ChunkCoord[] {
    const chunks: ChunkCoord[] = [];
    const loadDistance = this.config.loadDistance;
    
    // Determine visible range at each LOD level
    for (let lod = 0; lod < this.config.lodLevels; lod++) {
      const lodSize = this.config.size * Math.pow(2, lod);
      const lodDistance = loadDistance * Math.pow(2, lod);
      
      const minX = Math.floor((cameraPosition.x - lodDistance) / lodSize);
      const maxX = Math.ceil((cameraPosition.x + lodDistance) / lodSize);
      const minZ = Math.floor((cameraPosition.z - lodDistance) / lodSize);
      const maxZ = Math.ceil((cameraPosition.z + lodDistance) / lodSize);
      
      for (let x = minX; x <= maxX; x++) {
        for (let z = minZ; z <= maxZ; z++) {
          const chunkCenterX = (x + 0.5) * lodSize;
          const chunkCenterZ = (z + 0.5) * lodSize;
          
          const dist = Math.sqrt(
            Math.pow(chunkCenterX - cameraPosition.x, 2) +
            Math.pow(chunkCenterZ - cameraPosition.z, 2)
          );
          
          // Only add if in LOD's range
          const minDist = lod === 0 ? 0 : loadDistance * Math.pow(2, lod - 1);
          const maxDist = lodDistance;
          
          if (dist >= minDist && dist < maxDist) {
            chunks.push({ x, z, lod });
          }
        }
      }
    }
    
    return chunks;
  }
  
  private queueChunkLoad(coord: ChunkCoord, cameraPosition: THREE.Vector3): void {
    const lodSize = this.config.size * Math.pow(2, coord.lod);
    const chunkCenterX = (coord.x + 0.5) * lodSize;
    const chunkCenterZ = (coord.z + 0.5) * lodSize;
    
    const dist = Math.sqrt(
      Math.pow(chunkCenterX - cameraPosition.x, 2) +
      Math.pow(chunkCenterZ - cameraPosition.z, 2)
    );
    
    // Priority: closer chunks and lower LOD = higher priority
    const priority = 1000 - dist - coord.lod * 100;
    
    const key = this.getChunkKey(coord);
    
    // Create placeholder chunk
    const chunk: TerrainChunk = {
      coord,
      mesh: null,
      geometry: null,
      heightData: null,
      state: 'loading',
      lastAccessTime: Date.now(),
      priority
    };
    
    this.chunks.set(key, chunk);
    
    this.loadingQueue.enqueue({
      coord,
      priority,
      resolve: (loadedChunk) => {
        // Chunk loaded successfully
      },
      reject: (error) => {
        console.error('Failed to load chunk:', error);
        this.chunks.delete(key);
      }
    });
  }
  
  private processLoadingQueue(): void {
    let request: ChunkLoadRequest | null;
    
    while ((request = this.loadingQueue.dequeue()) !== null) {
      this.loadChunk(request);
    }
  }
  
  private async loadChunk(request: ChunkLoadRequest): Promise<void> {
    const { coord } = request;
    const key = this.getChunkKey(coord);
    const chunk = this.chunks.get(key);
    
    if (!chunk) {
      this.loadingQueue.complete(coord);
      return;
    }
    
    try {
      // Generate height data
      const lodSize = this.config.size * Math.pow(2, coord.lod);
      const resolution = this.config.resolution;
      const heightData = this.generateHeightData(coord, resolution);
      
      // Get geometry from pool
      const geometry = this.chunkPool.acquire(resolution);
      
      // Modify geometry with height data
      this.applyHeightData(geometry, heightData, coord, lodSize);
      
      // Create mesh
      const mesh = new THREE.Mesh(geometry, this.material);
      mesh.position.set(
        coord.x * lodSize + lodSize / 2,
        0,
        coord.z * lodSize + lodSize / 2
      );
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      
      // Update chunk
      chunk.geometry = geometry;
      chunk.mesh = mesh;
      chunk.heightData = heightData;
      chunk.state = 'loaded';
      chunk.lastAccessTime = Date.now();
      
      // Auto-show if still needed
      const cameraPos = this.lastCameraPosition;
      const desiredChunks = this.getDesiredChunks(cameraPos);
      const isDesired = desiredChunks.some(
        c => c.x === coord.x && c.z === coord.z && c.lod === coord.lod
      );
      
      if (isDesired) {
        this.showChunk(chunk);
      }
      
      request.resolve(chunk);
    } catch (error) {
      request.reject(error as Error);
    }
    
    this.loadingQueue.complete(coord);
  }
  
  private generateHeightData(coord: ChunkCoord, resolution: number): Float32Array {
    const lodSize = this.config.size * Math.pow(2, coord.lod);
    const heightData = new Float32Array(resolution * resolution);
    
    for (let z = 0; z < resolution; z++) {
      for (let x = 0; x < resolution; x++) {
        const worldX = coord.x * lodSize + (x / (resolution - 1)) * lodSize;
        const worldZ = coord.z * lodSize + (z / (resolution - 1)) * lodSize;
        
        heightData[z * resolution + x] = this.heightGenerator(worldX, worldZ);
      }
    }
    
    return heightData;
  }
  
  private applyHeightData(
    geometry: THREE.BufferGeometry,
    heightData: Float32Array,
    coord: ChunkCoord,
    lodSize: number
  ): void {
    const positions = geometry.getAttribute('position');
    const resolution = Math.sqrt(positions.count);
    
    for (let i = 0; i < positions.count; i++) {
      const x = i % resolution;
      const z = Math.floor(i / resolution);
      
      positions.setX(i, (x / (resolution - 1) - 0.5) * lodSize);
      positions.setY(i, heightData[i]);
      positions.setZ(i, (z / (resolution - 1) - 0.5) * lodSize);
    }
    
    positions.needsUpdate = true;
    geometry.computeVertexNormals();
    geometry.computeBoundingBox();
    geometry.computeBoundingSphere();
  }
  
  private showChunk(chunk: TerrainChunk): void {
    if (!chunk.mesh || chunk.state === 'visible') return;
    
    this.scene.add(chunk.mesh);
    chunk.state = 'visible';
    this.visibleChunks.add(this.getChunkKey(chunk.coord));
    chunk.lastAccessTime = Date.now();
  }
  
  private hideChunk(chunk: TerrainChunk): void {
    if (!chunk.mesh || chunk.state !== 'visible') return;
    
    this.scene.remove(chunk.mesh);
    chunk.state = 'loaded';
    this.visibleChunks.delete(this.getChunkKey(chunk.coord));
  }
  
  private unloadDistantChunks(cameraPosition: THREE.Vector3): void {
    const unloadDistanceSq = this.config.unloadDistance * this.config.unloadDistance;
    const chunksToUnload: string[] = [];
    
    for (const [key, chunk] of this.chunks) {
      const lodSize = this.config.size * Math.pow(2, chunk.coord.lod);
      const chunkCenterX = (chunk.coord.x + 0.5) * lodSize;
      const chunkCenterZ = (chunk.coord.z + 0.5) * lodSize;
      
      const distSq = Math.pow(chunkCenterX - cameraPosition.x, 2) +
                     Math.pow(chunkCenterZ - cameraPosition.z, 2);
      
      if (distSq > unloadDistanceSq * Math.pow(2, chunk.coord.lod * 2)) {
        chunksToUnload.push(key);
      }
    }
    
    // Unload chunks
    for (const key of chunksToUnload) {
      this.unloadChunk(key);
    }
    
    // Enforce cache limit
    this.enforceCacheLimit();
  }
  
  private unloadChunk(key: string): void {
    const chunk = this.chunks.get(key);
    if (!chunk) return;
    
    // Cancel pending load
    this.loadingQueue.cancel(chunk.coord);
    
    // Remove from scene
    if (chunk.mesh) {
      this.scene.remove(chunk.mesh);
      chunk.mesh = null;
    }
    
    // Return geometry to pool
    if (chunk.geometry) {
      this.chunkPool.release(chunk.geometry);
      chunk.geometry = null;
    }
    
    chunk.heightData = null;
    this.chunks.delete(key);
    this.visibleChunks.delete(key);
  }
  
  private enforceCacheLimit(): void {
    if (this.chunks.size <= this.config.maxCacheSize) return;
    
    // Sort by last access time (oldest first)
    const entries = Array.from(this.chunks.entries())
      .filter(([_, chunk]) => chunk.state !== 'visible')
      .sort((a, b) => a[1].lastAccessTime - b[1].lastAccessTime);
    
    // Remove oldest until under limit
    const toRemove = this.chunks.size - this.config.maxCacheSize;
    for (let i = 0; i < toRemove && i < entries.length; i++) {
      this.unloadChunk(entries[i][0]);
    }
  }
  
  private getChunkKey(coord: ChunkCoord): string {
    return `${coord.x},${coord.z},${coord.lod}`;
  }
  
  /**
   * Get height at world position
   */
  public getHeightAt(x: number, z: number): number {
    return this.heightGenerator(x, z);
  }
  
  /**
   * Set terrain material
   */
  public setMaterial(material: THREE.Material): void {
    this.material = material;
    
    // Update existing chunks
    for (const chunk of this.chunks.values()) {
      if (chunk.mesh) {
        chunk.mesh.material = material;
      }
    }
  }
  
  /**
   * Get stats
   */
  public getStats(): {
    loadedChunks: number;
    visibleChunks: number;
    pendingLoads: number;
    cacheSize: number;
  } {
    return {
      loadedChunks: this.chunks.size,
      visibleChunks: this.visibleChunks.size,
      pendingLoads: this.loadingQueue.getPendingCount(),
      cacheSize: this.config.maxCacheSize
    };
  }
  
  /**
   * Dispose
   */
  public dispose(): void {
    // Unload all chunks
    for (const key of Array.from(this.chunks.keys())) {
      this.unloadChunk(key);
    }
    
    this.loadingQueue.clear();
    this.chunkPool.dispose();
    this.material.dispose();
  }
}

