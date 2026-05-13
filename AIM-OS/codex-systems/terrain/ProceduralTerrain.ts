/**
 * Procedural Terrain Generation System
 * Multi-octave noise + erosion simulation
 * 
 * Features:
 * - Heightmap generation (FBM, ridged, terraced)
 * - Hydraulic erosion simulation
 * - Thermal erosion
 * - Biome mapping
 * - LOD with geomorphing
 */

import * as THREE from 'three';

export interface TerrainConfig {
  // Grid
  size: number;              // World size in units
  resolution: number;        // Grid resolution (power of 2 + 1)
  
  // Height
  heightScale: number;       // Maximum height
  baseFrequency: number;     // Base noise frequency
  
  // Noise
  octaves: number;           // FBM octaves
  lacunarity: number;        // Frequency multiplier
  persistence: number;       // Amplitude multiplier
  
  // Features
  ridgeWeight: number;       // Ridged noise contribution
  terraceCount: number;      // Number of terrace levels (0 = none)
  
  // Erosion
  enableHydraulicErosion: boolean;
  hydraulicIterations: number;
  enableThermalErosion: boolean;
  thermalIterations: number;
  
  // Biomes
  enableBiomes: boolean;
  moistureScale: number;
  temperatureScale: number;
}

export const DEFAULT_TERRAIN_CONFIG: TerrainConfig = {
  size: 1000,
  resolution: 257,
  heightScale: 200,
  baseFrequency: 0.002,
  octaves: 8,
  lacunarity: 2.0,
  persistence: 0.5,
  ridgeWeight: 0.3,
  terraceCount: 0,
  enableHydraulicErosion: true,
  hydraulicIterations: 50000,
  enableThermalErosion: true,
  thermalIterations: 50,
  enableBiomes: true,
  moistureScale: 0.001,
  temperatureScale: 0.0005
};

export interface TerrainData {
  heightmap: Float32Array;
  normalmap: Float32Array;
  moisture: Float32Array;
  temperature: Float32Array;
  biomeIndices: Uint8Array;
}

export enum BiomeType {
  OCEAN = 0,
  BEACH = 1,
  GRASSLAND = 2,
  FOREST = 3,
  DESERT = 4,
  TUNDRA = 5,
  SNOW = 6,
  MOUNTAIN = 7
}

export class ProceduralTerrain {
  private config: TerrainConfig;
  private data!: TerrainData;
  
  public geometry!: THREE.BufferGeometry;
  public mesh!: THREE.Mesh;
  private material!: THREE.ShaderMaterial;
  
  // Noise permutation table
  private perm: number[] = [];

  constructor(config: Partial<TerrainConfig> = {}) {
    this.config = { ...DEFAULT_TERRAIN_CONFIG, ...config };
    this.initPermutation();
  }

  private initPermutation(): void {
    // Generate permutation table for noise
    for (let i = 0; i < 256; i++) {
      this.perm[i] = i;
    }
    // Shuffle
    for (let i = 255; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [this.perm[i], this.perm[j]] = [this.perm[j], this.perm[i]];
    }
    // Duplicate for wrapping
    for (let i = 0; i < 256; i++) {
      this.perm[256 + i] = this.perm[i];
    }
  }

  /**
   * Generate complete terrain
   */
  public generate(seed?: number): void {
    if (seed !== undefined) {
      // Re-seed permutation
      const rng = this.seededRandom(seed);
      for (let i = 255; i > 0; i--) {
        const j = Math.floor(rng() * (i + 1));
        [this.perm[i], this.perm[j]] = [this.perm[j], this.perm[i]];
      }
      for (let i = 0; i < 256; i++) {
        this.perm[256 + i] = this.perm[i];
      }
    }

    const res = this.config.resolution;
    const totalVerts = res * res;

    this.data = {
      heightmap: new Float32Array(totalVerts),
      normalmap: new Float32Array(totalVerts * 3),
      moisture: new Float32Array(totalVerts),
      temperature: new Float32Array(totalVerts),
      biomeIndices: new Uint8Array(totalVerts)
    };

    // 1. Generate base heightmap
    this.generateHeightmap();

    // 2. Apply erosion
    if (this.config.enableHydraulicErosion) {
      this.hydraulicErosion();
    }
    if (this.config.enableThermalErosion) {
      this.thermalErosion();
    }

    // 3. Calculate normals
    this.calculateNormals();

    // 4. Generate biome data
    if (this.config.enableBiomes) {
      this.generateBiomes();
    }

    // 5. Create geometry
    this.createGeometry();
  }

  private generateHeightmap(): void {
    const { resolution, size, heightScale, baseFrequency, octaves, lacunarity, persistence, ridgeWeight, terraceCount } = this.config;

    for (let z = 0; z < resolution; z++) {
      for (let x = 0; x < resolution; x++) {
        const idx = z * resolution + x;
        const wx = (x / (resolution - 1)) * size - size / 2;
        const wz = (z / (resolution - 1)) * size - size / 2;

        // FBM noise
        let height = this.fbm(wx * baseFrequency, wz * baseFrequency, octaves, lacunarity, persistence);

        // Add ridged noise for mountains
        if (ridgeWeight > 0) {
          const ridged = this.ridgedNoise(wx * baseFrequency * 0.5, wz * baseFrequency * 0.5, octaves);
          height = height * (1 - ridgeWeight) + ridged * ridgeWeight;
        }

        // Apply terracing
        if (terraceCount > 0) {
          height = Math.floor(height * terraceCount) / terraceCount;
        }

        // Scale to world height
        this.data.heightmap[idx] = height * heightScale;
      }
    }
  }

  private fbm(x: number, y: number, octaves: number, lacunarity: number, persistence: number): number {
    let total = 0;
    let frequency = 1;
    let amplitude = 1;
    let maxValue = 0;

    for (let i = 0; i < octaves; i++) {
      total += this.perlin(x * frequency, y * frequency) * amplitude;
      maxValue += amplitude;
      amplitude *= persistence;
      frequency *= lacunarity;
    }

    return total / maxValue;
  }

  private ridgedNoise(x: number, y: number, octaves: number): number {
    let total = 0;
    let frequency = 1;
    let amplitude = 1;
    let maxValue = 0;

    for (let i = 0; i < octaves; i++) {
      let n = this.perlin(x * frequency, y * frequency);
      n = 1 - Math.abs(n); // Ridged
      n = n * n;           // Sharpen
      total += n * amplitude;
      maxValue += amplitude;
      amplitude *= 0.5;
      frequency *= 2;
    }

    return total / maxValue;
  }

  private perlin(x: number, y: number): number {
    const xi = Math.floor(x) & 255;
    const yi = Math.floor(y) & 255;
    const xf = x - Math.floor(x);
    const yf = y - Math.floor(y);

    const u = this.fade(xf);
    const v = this.fade(yf);

    const aa = this.perm[this.perm[xi] + yi];
    const ab = this.perm[this.perm[xi] + yi + 1];
    const ba = this.perm[this.perm[xi + 1] + yi];
    const bb = this.perm[this.perm[xi + 1] + yi + 1];

    const x1 = this.lerp(this.grad(aa, xf, yf), this.grad(ba, xf - 1, yf), u);
    const x2 = this.lerp(this.grad(ab, xf, yf - 1), this.grad(bb, xf - 1, yf - 1), u);

    return this.lerp(x1, x2, v);
  }

  private fade(t: number): number {
    return t * t * t * (t * (t * 6 - 15) + 10);
  }

  private lerp(a: number, b: number, t: number): number {
    return a + t * (b - a);
  }

  private grad(hash: number, x: number, y: number): number {
    const h = hash & 3;
    const u = h < 2 ? x : y;
    const v = h < 2 ? y : x;
    return ((h & 1) === 0 ? u : -u) + ((h & 2) === 0 ? v : -v);
  }

  /**
   * Hydraulic erosion simulation
   */
  private hydraulicErosion(): void {
    const res = this.config.resolution;
    const iterations = this.config.hydraulicIterations;

    // Erosion parameters
    const inertia = 0.05;
    const capacity = 4;
    const deposition = 0.3;
    const erosion = 0.3;
    const evaporation = 0.01;
    const minSlope = 0.01;
    const gravity = 4;

    for (let iter = 0; iter < iterations; iter++) {
      // Random starting position
      let x = Math.random() * (res - 2) + 1;
      let y = Math.random() * (res - 2) + 1;

      let dirX = 0;
      let dirY = 0;
      let speed = 1;
      let water = 1;
      let sediment = 0;

      const maxSteps = 64;

      for (let step = 0; step < maxSteps; step++) {
        const xi = Math.floor(x);
        const yi = Math.floor(y);

        if (xi < 1 || xi >= res - 1 || yi < 1 || yi >= res - 1) break;

        const idx = yi * res + xi;

        // Calculate gradient
        const h = this.data.heightmap[idx];
        const hL = this.data.heightmap[idx - 1];
        const hR = this.data.heightmap[idx + 1];
        const hU = this.data.heightmap[idx - res];
        const hD = this.data.heightmap[idx + res];

        const gx = hL - hR;
        const gy = hU - hD;

        // Update direction
        dirX = dirX * inertia - gx * (1 - inertia);
        dirY = dirY * inertia - gy * (1 - inertia);

        const len = Math.sqrt(dirX * dirX + dirY * dirY);
        if (len < 0.001) break;

        dirX /= len;
        dirY /= len;

        // Move
        x += dirX;
        y += dirY;

        const newXi = Math.floor(x);
        const newYi = Math.floor(y);
        if (newXi < 0 || newXi >= res || newYi < 0 || newYi >= res) break;

        const newIdx = newYi * res + newXi;
        const newH = this.data.heightmap[newIdx];
        const deltaH = newH - h;

        // Calculate sediment capacity
        const c = Math.max(-deltaH, minSlope) * speed * water * capacity;

        if (sediment > c || deltaH > 0) {
          // Deposit sediment
          const depositAmount = deltaH > 0
            ? Math.min(deltaH, sediment)
            : (sediment - c) * deposition;
          sediment -= depositAmount;
          this.data.heightmap[idx] += depositAmount;
        } else {
          // Erode
          const erodeAmount = Math.min((c - sediment) * erosion, -deltaH);
          sediment += erodeAmount;
          this.data.heightmap[idx] -= erodeAmount;
        }

        // Update speed and water
        speed = Math.sqrt(speed * speed + deltaH * gravity);
        water *= (1 - evaporation);

        if (water < 0.001) break;
      }
    }
  }

  /**
   * Thermal erosion simulation
   */
  private thermalErosion(): void {
    const res = this.config.resolution;
    const iterations = this.config.thermalIterations;
    const talusAngle = 0.5; // Angle of repose

    for (let iter = 0; iter < iterations; iter++) {
      for (let y = 1; y < res - 1; y++) {
        for (let x = 1; x < res - 1; x++) {
          const idx = y * res + x;
          const h = this.data.heightmap[idx];

          let maxDiff = 0;
          let maxIdx = -1;

          // Check neighbors
          const neighbors = [
            idx - 1, idx + 1,
            idx - res, idx + res,
            idx - res - 1, idx - res + 1,
            idx + res - 1, idx + res + 1
          ];

          for (const nIdx of neighbors) {
            const diff = h - this.data.heightmap[nIdx];
            if (diff > maxDiff && diff > talusAngle) {
              maxDiff = diff;
              maxIdx = nIdx;
            }
          }

          if (maxIdx >= 0) {
            const transfer = maxDiff * 0.5 * 0.1;
            this.data.heightmap[idx] -= transfer;
            this.data.heightmap[maxIdx] += transfer;
          }
        }
      }
    }
  }

  private calculateNormals(): void {
    const res = this.config.resolution;
    const scale = this.config.size / (res - 1);

    for (let y = 0; y < res; y++) {
      for (let x = 0; x < res; x++) {
        const idx = y * res + x;

        // Sample heights
        const hL = x > 0 ? this.data.heightmap[idx - 1] : this.data.heightmap[idx];
        const hR = x < res - 1 ? this.data.heightmap[idx + 1] : this.data.heightmap[idx];
        const hU = y > 0 ? this.data.heightmap[idx - res] : this.data.heightmap[idx];
        const hD = y < res - 1 ? this.data.heightmap[idx + res] : this.data.heightmap[idx];

        // Calculate normal
        const nx = (hL - hR) / (2 * scale);
        const ny = 1;
        const nz = (hU - hD) / (2 * scale);

        const len = Math.sqrt(nx * nx + ny * ny + nz * nz);
        this.data.normalmap[idx * 3] = nx / len;
        this.data.normalmap[idx * 3 + 1] = ny / len;
        this.data.normalmap[idx * 3 + 2] = nz / len;
      }
    }
  }

  private generateBiomes(): void {
    const res = this.config.resolution;
    const { size, moistureScale, temperatureScale } = this.config;

    let maxHeight = 0;
    for (let i = 0; i < this.data.heightmap.length; i++) {
      maxHeight = Math.max(maxHeight, this.data.heightmap[i]);
    }

    for (let y = 0; y < res; y++) {
      for (let x = 0; x < res; x++) {
        const idx = y * res + x;
        const wx = (x / (res - 1)) * size - size / 2;
        const wz = (y / (res - 1)) * size - size / 2;
        const height = this.data.heightmap[idx];

        // Generate moisture and temperature from noise
        const moisture = (this.fbm(wx * moistureScale, wz * moistureScale, 4, 2, 0.5) + 1) * 0.5;
        const baseTemp = (this.fbm(wx * temperatureScale + 100, wz * temperatureScale + 100, 4, 2, 0.5) + 1) * 0.5;
        const temperature = baseTemp - (height / maxHeight) * 0.5; // Colder at higher altitudes

        this.data.moisture[idx] = moisture;
        this.data.temperature[idx] = temperature;

        // Determine biome
        let biome: BiomeType;
        const normalizedHeight = height / maxHeight;

        if (normalizedHeight < 0.1) {
          biome = BiomeType.OCEAN;
        } else if (normalizedHeight < 0.15) {
          biome = BiomeType.BEACH;
        } else if (normalizedHeight > 0.8) {
          biome = BiomeType.SNOW;
        } else if (normalizedHeight > 0.6) {
          biome = BiomeType.MOUNTAIN;
        } else if (temperature < 0.3) {
          biome = BiomeType.TUNDRA;
        } else if (moisture < 0.3) {
          biome = BiomeType.DESERT;
        } else if (moisture > 0.6) {
          biome = BiomeType.FOREST;
        } else {
          biome = BiomeType.GRASSLAND;
        }

        this.data.biomeIndices[idx] = biome;
      }
    }
  }

  private createGeometry(): void {
    const res = this.config.resolution;
    const size = this.config.size;

    const vertices = new Float32Array(res * res * 3);
    const normals = new Float32Array(res * res * 3);
    const uvs = new Float32Array(res * res * 2);
    const indices: number[] = [];

    for (let y = 0; y < res; y++) {
      for (let x = 0; x < res; x++) {
        const idx = y * res + x;

        // Position
        vertices[idx * 3] = (x / (res - 1)) * size - size / 2;
        vertices[idx * 3 + 1] = this.data.heightmap[idx];
        vertices[idx * 3 + 2] = (y / (res - 1)) * size - size / 2;

        // Normal
        normals[idx * 3] = this.data.normalmap[idx * 3];
        normals[idx * 3 + 1] = this.data.normalmap[idx * 3 + 1];
        normals[idx * 3 + 2] = this.data.normalmap[idx * 3 + 2];

        // UV
        uvs[idx * 2] = x / (res - 1);
        uvs[idx * 2 + 1] = y / (res - 1);
      }
    }

    // Generate indices
    for (let y = 0; y < res - 1; y++) {
      for (let x = 0; x < res - 1; x++) {
        const i = y * res + x;
        indices.push(i, i + res, i + 1);
        indices.push(i + 1, i + res, i + res + 1);
      }
    }

    this.geometry = new THREE.BufferGeometry();
    this.geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));
    this.geometry.setAttribute('normal', new THREE.BufferAttribute(normals, 3));
    this.geometry.setAttribute('uv', new THREE.BufferAttribute(uvs, 2));
    this.geometry.setIndex(indices);

    // Create material
    this.material = new THREE.ShaderMaterial({
      uniforms: {
        uHeightScale: { value: this.config.heightScale }
      },
      vertexShader: `
        varying vec3 vNormal;
        varying vec2 vUv;
        varying float vHeight;
        
        void main() {
          vNormal = normal;
          vUv = uv;
          vHeight = position.y;
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
      `,
      fragmentShader: `
        uniform float uHeightScale;
        varying vec3 vNormal;
        varying vec2 vUv;
        varying float vHeight;
        
        void main() {
          float h = vHeight / uHeightScale;
          
          vec3 color;
          if (h < 0.1) {
            color = vec3(0.1, 0.3, 0.6); // Water
          } else if (h < 0.15) {
            color = vec3(0.9, 0.85, 0.7); // Beach
          } else if (h < 0.5) {
            color = mix(vec3(0.2, 0.5, 0.2), vec3(0.15, 0.4, 0.15), (h - 0.15) / 0.35); // Grass
          } else if (h < 0.75) {
            color = mix(vec3(0.4, 0.35, 0.3), vec3(0.5, 0.5, 0.5), (h - 0.5) / 0.25); // Rock
          } else {
            color = vec3(0.95, 0.95, 1.0); // Snow
          }
          
          vec3 light = normalize(vec3(0.5, 1.0, 0.5));
          float diffuse = max(dot(vNormal, light), 0.0);
          color *= 0.3 + 0.7 * diffuse;
          
          gl_FragColor = vec4(color, 1.0);
        }
      `
    });

    this.mesh = new THREE.Mesh(this.geometry, this.material);
  }

  private seededRandom(seed: number): () => number {
    return function() {
      seed = (seed * 9301 + 49297) % 233280;
      return seed / 233280;
    };
  }

  public getHeightAt(x: number, z: number): number {
    const res = this.config.resolution;
    const size = this.config.size;

    // Convert world to grid coords
    const gx = ((x + size / 2) / size) * (res - 1);
    const gz = ((z + size / 2) / size) * (res - 1);

    if (gx < 0 || gx >= res - 1 || gz < 0 || gz >= res - 1) {
      return 0;
    }

    // Bilinear interpolation
    const xi = Math.floor(gx);
    const zi = Math.floor(gz);
    const xf = gx - xi;
    const zf = gz - zi;

    const h00 = this.data.heightmap[zi * res + xi];
    const h10 = this.data.heightmap[zi * res + xi + 1];
    const h01 = this.data.heightmap[(zi + 1) * res + xi];
    const h11 = this.data.heightmap[(zi + 1) * res + xi + 1];

    return this.lerp(
      this.lerp(h00, h10, xf),
      this.lerp(h01, h11, xf),
      zf
    );
  }

  public dispose(): void {
    this.geometry.dispose();
    this.material.dispose();
  }
}

