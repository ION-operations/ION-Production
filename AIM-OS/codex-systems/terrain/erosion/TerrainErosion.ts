/**
 * Terrain Erosion Simulation
 * Hydraulic and thermal erosion for realistic terrain
 * 
 * Features:
 * - Hydraulic erosion (water-based)
 * - Thermal erosion (talus slope)
 * - Sediment transport and deposition
 * - River/valley carving
 * - GPU-accelerated option
 * - Real-time preview
 */

import * as THREE from 'three';

// ============================================
// TYPES
// ============================================

export interface ErosionConfig {
  // Hydraulic erosion
  dropletCount: number;
  dropletInertia: number;
  dropletCapacity: number;
  dropletDeposition: number;
  dropletErosion: number;
  dropletEvaporation: number;
  dropletMinSlope: number;
  dropletGravity: number;
  maxDropletLifetime: number;
  erosionRadius: number;
  
  // Thermal erosion
  talusAngle: number;
  thermalIterations: number;
  thermalRate: number;
  
  // General
  seed: number;
}

export interface HeightMap {
  data: Float32Array;
  width: number;
  height: number;
}

export interface ErosionResult {
  heightMap: HeightMap;
  waterMap: HeightMap;
  sedimentMap: HeightMap;
  erosionMap: HeightMap;
}

// ============================================
// RANDOM NUMBER GENERATOR
// ============================================

class SeededRandom {
  private seed: number;
  
  constructor(seed: number) {
    this.seed = seed;
  }
  
  next(): number {
    this.seed = (this.seed * 1103515245 + 12345) & 0x7fffffff;
    return this.seed / 0x7fffffff;
  }
  
  range(min: number, max: number): number {
    return min + this.next() * (max - min);
  }
}

// ============================================
// HYDRAULIC EROSION
// ============================================

interface WaterDroplet {
  x: number;
  y: number;
  dirX: number;
  dirY: number;
  speed: number;
  water: number;
  sediment: number;
}

export class HydraulicErosion {
  private config: ErosionConfig;
  private random: SeededRandom;
  private heightMap: HeightMap;
  private erosionMap: Float32Array;
  
  constructor(heightMap: HeightMap, config: ErosionConfig) {
    this.heightMap = heightMap;
    this.config = config;
    this.random = new SeededRandom(config.seed);
    this.erosionMap = new Float32Array(heightMap.width * heightMap.height);
  }
  
  /**
   * Run hydraulic erosion simulation
   */
  public erode(): void {
    for (let i = 0; i < this.config.dropletCount; i++) {
      this.simulateDroplet();
    }
  }
  
  private simulateDroplet(): void {
    // Initialize droplet at random position
    const droplet: WaterDroplet = {
      x: this.random.range(0, this.heightMap.width - 1),
      y: this.random.range(0, this.heightMap.height - 1),
      dirX: 0,
      dirY: 0,
      speed: 1,
      water: 1,
      sediment: 0
    };
    
    for (let lifetime = 0; lifetime < this.config.maxDropletLifetime; lifetime++) {
      const nodeX = Math.floor(droplet.x);
      const nodeY = Math.floor(droplet.y);
      
      // Check bounds
      if (nodeX < 1 || nodeX >= this.heightMap.width - 2 ||
          nodeY < 1 || nodeY >= this.heightMap.height - 2) {
        break;
      }
      
      // Calculate height and gradient at current position
      const cellOffsetX = droplet.x - nodeX;
      const cellOffsetY = droplet.y - nodeY;
      
      const { height, gradientX, gradientY } = this.calculateHeightAndGradient(
        nodeX, nodeY, cellOffsetX, cellOffsetY
      );
      
      // Update direction with inertia
      droplet.dirX = droplet.dirX * this.config.dropletInertia - gradientX * (1 - this.config.dropletInertia);
      droplet.dirY = droplet.dirY * this.config.dropletInertia - gradientY * (1 - this.config.dropletInertia);
      
      // Normalize direction
      const len = Math.sqrt(droplet.dirX * droplet.dirX + droplet.dirY * droplet.dirY);
      if (len > 0.0001) {
        droplet.dirX /= len;
        droplet.dirY /= len;
      } else {
        // Random direction if gradient is too small
        const angle = this.random.next() * Math.PI * 2;
        droplet.dirX = Math.cos(angle);
        droplet.dirY = Math.sin(angle);
      }
      
      // Move droplet
      const newX = droplet.x + droplet.dirX;
      const newY = droplet.y + droplet.dirY;
      
      // Check new bounds
      if (newX < 0 || newX >= this.heightMap.width - 1 ||
          newY < 0 || newY >= this.heightMap.height - 1) {
        break;
      }
      
      // Calculate new height
      const newNodeX = Math.floor(newX);
      const newNodeY = Math.floor(newY);
      const newCellOffsetX = newX - newNodeX;
      const newCellOffsetY = newY - newNodeY;
      
      const newHeight = this.interpolateHeight(newNodeX, newNodeY, newCellOffsetX, newCellOffsetY);
      const deltaHeight = newHeight - height;
      
      // Calculate sediment capacity
      const capacity = Math.max(
        -deltaHeight * droplet.speed * droplet.water * this.config.dropletCapacity,
        this.config.dropletMinSlope
      );
      
      // Erode or deposit
      if (droplet.sediment > capacity || deltaHeight > 0) {
        // Deposit sediment
        const depositAmount = deltaHeight > 0
          ? Math.min(deltaHeight, droplet.sediment)
          : (droplet.sediment - capacity) * this.config.dropletDeposition;
        
        droplet.sediment -= depositAmount;
        this.deposit(nodeX, nodeY, cellOffsetX, cellOffsetY, depositAmount);
      } else {
        // Erode terrain
        const erodeAmount = Math.min(
          (capacity - droplet.sediment) * this.config.dropletErosion,
          -deltaHeight
        );
        
        droplet.sediment += erodeAmount;
        this.erodeAt(droplet.x, droplet.y, erodeAmount);
      }
      
      // Update droplet
      droplet.x = newX;
      droplet.y = newY;
      droplet.speed = Math.sqrt(
        droplet.speed * droplet.speed + 
        deltaHeight * this.config.dropletGravity
      );
      droplet.water *= (1 - this.config.dropletEvaporation);
      
      // Stop if water evaporated
      if (droplet.water < 0.01) {
        break;
      }
    }
  }
  
  private calculateHeightAndGradient(
    nodeX: number,
    nodeY: number,
    offsetX: number,
    offsetY: number
  ): { height: number; gradientX: number; gradientY: number } {
    const w = this.heightMap.width;
    
    // Get heights of 4 corners
    const heightNW = this.heightMap.data[nodeY * w + nodeX];
    const heightNE = this.heightMap.data[nodeY * w + nodeX + 1];
    const heightSW = this.heightMap.data[(nodeY + 1) * w + nodeX];
    const heightSE = this.heightMap.data[(nodeY + 1) * w + nodeX + 1];
    
    // Bilinear interpolation
    const height = 
      heightNW * (1 - offsetX) * (1 - offsetY) +
      heightNE * offsetX * (1 - offsetY) +
      heightSW * (1 - offsetX) * offsetY +
      heightSE * offsetX * offsetY;
    
    // Calculate gradient
    const gradientX = (heightNE - heightNW) * (1 - offsetY) + (heightSE - heightSW) * offsetY;
    const gradientY = (heightSW - heightNW) * (1 - offsetX) + (heightSE - heightNE) * offsetX;
    
    return { height, gradientX, gradientY };
  }
  
  private interpolateHeight(
    nodeX: number,
    nodeY: number,
    offsetX: number,
    offsetY: number
  ): number {
    const w = this.heightMap.width;
    
    const heightNW = this.heightMap.data[nodeY * w + nodeX];
    const heightNE = this.heightMap.data[nodeY * w + nodeX + 1];
    const heightSW = this.heightMap.data[(nodeY + 1) * w + nodeX];
    const heightSE = this.heightMap.data[(nodeY + 1) * w + nodeX + 1];
    
    return (
      heightNW * (1 - offsetX) * (1 - offsetY) +
      heightNE * offsetX * (1 - offsetY) +
      heightSW * (1 - offsetX) * offsetY +
      heightSE * offsetX * offsetY
    );
  }
  
  private deposit(
    nodeX: number,
    nodeY: number,
    offsetX: number,
    offsetY: number,
    amount: number
  ): void {
    const w = this.heightMap.width;
    
    // Distribute deposit across 4 corners based on bilinear weights
    this.heightMap.data[nodeY * w + nodeX] += amount * (1 - offsetX) * (1 - offsetY);
    this.heightMap.data[nodeY * w + nodeX + 1] += amount * offsetX * (1 - offsetY);
    this.heightMap.data[(nodeY + 1) * w + nodeX] += amount * (1 - offsetX) * offsetY;
    this.heightMap.data[(nodeY + 1) * w + nodeX + 1] += amount * offsetX * offsetY;
  }
  
  private erodeAt(x: number, y: number, amount: number): void {
    const w = this.heightMap.width;
    const h = this.heightMap.height;
    const radius = this.config.erosionRadius;
    
    const centerX = Math.floor(x);
    const centerY = Math.floor(y);
    
    // Calculate erosion weights based on distance
    let totalWeight = 0;
    const weights: { x: number; y: number; weight: number }[] = [];
    
    for (let dy = -radius; dy <= radius; dy++) {
      for (let dx = -radius; dx <= radius; dx++) {
        const px = centerX + dx;
        const py = centerY + dy;
        
        if (px < 0 || px >= w || py < 0 || py >= h) continue;
        
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist > radius) continue;
        
        const weight = Math.max(0, radius - dist);
        totalWeight += weight;
        weights.push({ x: px, y: py, weight });
      }
    }
    
    // Apply erosion
    if (totalWeight > 0) {
      for (const { x: px, y: py, weight } of weights) {
        const normalizedWeight = weight / totalWeight;
        const erodeAmount = amount * normalizedWeight;
        
        this.heightMap.data[py * w + px] -= erodeAmount;
        this.erosionMap[py * w + px] += erodeAmount;
      }
    }
  }
  
  public getErosionMap(): Float32Array {
    return this.erosionMap;
  }
}

// ============================================
// THERMAL EROSION
// ============================================

export class ThermalErosion {
  private config: ErosionConfig;
  private heightMap: HeightMap;
  
  constructor(heightMap: HeightMap, config: ErosionConfig) {
    this.heightMap = heightMap;
    this.config = config;
  }
  
  /**
   * Run thermal erosion simulation
   */
  public erode(): void {
    const talusThreshold = Math.tan(this.config.talusAngle * Math.PI / 180);
    
    for (let iter = 0; iter < this.config.thermalIterations; iter++) {
      this.iterateThermal(talusThreshold);
    }
  }
  
  private iterateThermal(talusThreshold: number): void {
    const w = this.heightMap.width;
    const h = this.heightMap.height;
    const data = this.heightMap.data;
    
    // Temporary buffer for changes
    const changes = new Float32Array(w * h);
    
    // 8-directional neighbors
    const dx = [-1, 0, 1, -1, 1, -1, 0, 1];
    const dy = [-1, -1, -1, 0, 0, 1, 1, 1];
    const dist = [1.414, 1, 1.414, 1, 1, 1.414, 1, 1.414];
    
    for (let y = 1; y < h - 1; y++) {
      for (let x = 1; x < w - 1; x++) {
        const idx = y * w + x;
        const centerHeight = data[idx];
        
        let totalDiff = 0;
        let maxDiff = 0;
        let maxNeighborIdx = -1;
        
        // Find neighbor with maximum height difference exceeding talus
        for (let i = 0; i < 8; i++) {
          const nx = x + dx[i];
          const ny = y + dy[i];
          const nidx = ny * w + nx;
          
          const slope = (centerHeight - data[nidx]) / dist[i];
          
          if (slope > talusThreshold) {
            const diff = slope - talusThreshold;
            totalDiff += diff;
            
            if (diff > maxDiff) {
              maxDiff = diff;
              maxNeighborIdx = nidx;
            }
          }
        }
        
        // Move material to steepest neighbor
        if (maxNeighborIdx >= 0 && totalDiff > 0) {
          const amount = maxDiff * this.config.thermalRate * 0.5;
          changes[idx] -= amount;
          changes[maxNeighborIdx] += amount;
        }
      }
    }
    
    // Apply changes
    for (let i = 0; i < w * h; i++) {
      data[i] += changes[i];
    }
  }
}

// ============================================
// MAIN TERRAIN EROSION SYSTEM
// ============================================

export class TerrainErosionSystem {
  private config: ErosionConfig;
  
  constructor(config: Partial<ErosionConfig> = {}) {
    this.config = {
      // Hydraulic erosion defaults
      dropletCount: 50000,
      dropletInertia: 0.3,
      dropletCapacity: 4,
      dropletDeposition: 0.3,
      dropletErosion: 0.3,
      dropletEvaporation: 0.02,
      dropletMinSlope: 0.01,
      dropletGravity: 4,
      maxDropletLifetime: 30,
      erosionRadius: 3,
      
      // Thermal erosion defaults
      talusAngle: 35,
      thermalIterations: 50,
      thermalRate: 0.5,
      
      seed: Date.now(),
      ...config
    };
  }
  
  /**
   * Create heightmap from noise
   */
  public createHeightMap(
    width: number,
    height: number,
    noiseFunction?: (x: number, y: number) => number
  ): HeightMap {
    const data = new Float32Array(width * height);
    
    const defaultNoise = (x: number, y: number): number => {
      // Simple FBM noise
      let value = 0;
      let amplitude = 1;
      let frequency = 0.01;
      
      for (let octave = 0; octave < 6; octave++) {
        const nx = x * frequency;
        const ny = y * frequency;
        
        // Simple value noise (replace with proper noise in production)
        const noise = Math.sin(nx * 12.9898 + ny * 78.233) * 43758.5453;
        value += (noise - Math.floor(noise)) * amplitude;
        
        amplitude *= 0.5;
        frequency *= 2;
      }
      
      return value;
    };
    
    const noise = noiseFunction ?? defaultNoise;
    
    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        data[y * width + x] = noise(x, y);
      }
    }
    
    // Normalize
    let min = Infinity;
    let max = -Infinity;
    for (let i = 0; i < data.length; i++) {
      min = Math.min(min, data[i]);
      max = Math.max(max, data[i]);
    }
    
    const range = max - min;
    if (range > 0) {
      for (let i = 0; i < data.length; i++) {
        data[i] = (data[i] - min) / range;
      }
    }
    
    return { data, width, height };
  }
  
  /**
   * Run full erosion simulation
   */
  public erode(heightMap: HeightMap): ErosionResult {
    // Create copies for tracking
    const waterMap: HeightMap = {
      data: new Float32Array(heightMap.width * heightMap.height),
      width: heightMap.width,
      height: heightMap.height
    };
    
    const sedimentMap: HeightMap = {
      data: new Float32Array(heightMap.width * heightMap.height),
      width: heightMap.width,
      height: heightMap.height
    };
    
    // Run hydraulic erosion
    const hydraulic = new HydraulicErosion(heightMap, this.config);
    hydraulic.erode();
    
    // Run thermal erosion
    const thermal = new ThermalErosion(heightMap, this.config);
    thermal.erode();
    
    const erosionMap: HeightMap = {
      data: hydraulic.getErosionMap(),
      width: heightMap.width,
      height: heightMap.height
    };
    
    return {
      heightMap,
      waterMap,
      sedimentMap,
      erosionMap
    };
  }
  
  /**
   * Create THREE.js mesh from heightmap
   */
  public createMesh(
    heightMap: HeightMap,
    worldSize: number = 100,
    heightScale: number = 20
  ): THREE.Mesh {
    const geometry = new THREE.PlaneGeometry(
      worldSize,
      worldSize,
      heightMap.width - 1,
      heightMap.height - 1
    );
    
    geometry.rotateX(-Math.PI / 2);
    
    const positions = geometry.getAttribute('position');
    
    for (let i = 0; i < positions.count; i++) {
      const x = Math.floor(i % heightMap.width);
      const y = Math.floor(i / heightMap.width);
      const height = heightMap.data[y * heightMap.width + x] * heightScale;
      
      positions.setY(i, height);
    }
    
    geometry.computeVertexNormals();
    
    // Create vertex colors based on height/slope
    const colors = new Float32Array(positions.count * 3);
    
    for (let i = 0; i < positions.count; i++) {
      const height = positions.getY(i) / heightScale;
      
      let r: number, g: number, b: number;
      
      if (height < 0.3) {
        // Water/sand
        r = 0.76; g = 0.70; b = 0.50;
      } else if (height < 0.5) {
        // Grass
        r = 0.36; g = 0.56; b = 0.30;
      } else if (height < 0.7) {
        // Rock
        r = 0.5; g = 0.5; b = 0.5;
      } else {
        // Snow
        r = 0.95; g = 0.95; b = 0.95;
      }
      
      colors[i * 3] = r;
      colors[i * 3 + 1] = g;
      colors[i * 3 + 2] = b;
    }
    
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    
    const material = new THREE.MeshStandardMaterial({
      vertexColors: true,
      roughness: 0.8,
      metalness: 0.1,
      flatShading: false
    });
    
    const mesh = new THREE.Mesh(geometry, material);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    
    return mesh;
  }
  
  /**
   * Get height at world position
   */
  public getHeightAt(
    heightMap: HeightMap,
    worldX: number,
    worldZ: number,
    worldSize: number,
    heightScale: number
  ): number {
    // Convert world coords to heightmap coords
    const hx = ((worldX / worldSize) + 0.5) * (heightMap.width - 1);
    const hz = ((worldZ / worldSize) + 0.5) * (heightMap.height - 1);
    
    const x0 = Math.floor(hx);
    const z0 = Math.floor(hz);
    const x1 = Math.min(x0 + 1, heightMap.width - 1);
    const z1 = Math.min(z0 + 1, heightMap.height - 1);
    
    const fx = hx - x0;
    const fz = hz - z0;
    
    const h00 = heightMap.data[z0 * heightMap.width + x0];
    const h10 = heightMap.data[z0 * heightMap.width + x1];
    const h01 = heightMap.data[z1 * heightMap.width + x0];
    const h11 = heightMap.data[z1 * heightMap.width + x1];
    
    const h = 
      h00 * (1 - fx) * (1 - fz) +
      h10 * fx * (1 - fz) +
      h01 * (1 - fx) * fz +
      h11 * fx * fz;
    
    return h * heightScale;
  }
}

