/**
 * Forward+ Lighting System
 * Tiled/clustered forward rendering for many lights
 *
 * Features:
 * - Screen-space tiling (Forward+)
 * - Per-tile light lists (CPU reference)
 * - Depth-aware light assignment
 * - Configurable tile size
 * - Frustum culling for lights
 *
 * Notes:
 * - This is a CPU-side scaffold for a Forward+ pipeline. In production,
 *   light assignment happens in a compute shader and light lists are stored in
 *   SSBOs or textures. Here we compute tile lists on CPU and upload as uniforms
 *   for smaller light counts.
 */

import * as THREE from 'three';

// ============================================
// TYPES
// ============================================

export interface ForwardPlusConfig {
  tileSize: number; // in pixels
  maxLightsPerTile: number;
}

export interface LightData {
  position: THREE.Vector3;
  color: THREE.Color;
  range: number;
  intensity: number;
}

export interface TileLightList {
  indices: number[]; // indices into lights array
}

// ============================================
// FORWARD+ LIGHTING
// ============================================

export class ForwardPlusLighting {
  private config: ForwardPlusConfig;
  private lights: LightData[] = [];
  private tileLists: TileLightList[] = [];
  private tilesX = 0;
  private tilesY = 0;

  constructor(config: Partial<ForwardPlusConfig> = {}) {
    this.config = {
      tileSize: 32,
      maxLightsPerTile: 64,
      ...config,
    };
  }

  /**
   * Set lights for this frame.
   */
  public setLights(lights: LightData[]): void {
    this.lights = lights;
  }

  /**
   * Build tile light lists given camera and depth (optional).
   * Depth texture is optional; if provided, we can cull lights by min/max depth per tile.
   */
  public buildLightLists(
    renderer: THREE.WebGLRenderer,
    camera: THREE.Camera,
    depthTexture?: THREE.DepthTexture
  ): void {
    const size = renderer.getSize(new THREE.Vector2());
    this.tilesX = Math.ceil(size.x / this.config.tileSize);
    this.tilesY = Math.ceil(size.y / this.config.tileSize);
    this.tileLists = new Array(this.tilesX * this.tilesY)
      .fill(0)
      .map(() => ({ indices: [] }));

    // Precompute inverse projection for depth->view conversion if depth provided
    let invProj = new THREE.Matrix4();
    if (depthTexture) {
      const persp = camera as THREE.PerspectiveCamera;
      invProj.copy(persp.projectionMatrix).invert();
    }

    // Optional depth min/max per tile (not implemented fully; placeholder)
    const tileMinDepth = new Float32Array(this.tilesX * this.tilesY).fill(0);
    const tileMaxDepth = new Float32Array(this.tilesX * this.tilesY).fill(1);
    // In a full implementation, we would downsample depth to tiles and read min/max.

    // For each light, project to screen and assign tiles conservatively
    for (let i = 0; i < this.lights.length; i++) {
      const light = this.lights[i];

      // Frustum cull (rough)
      const posView = light.position.clone().applyMatrix4(camera.matrixWorldInverse);
      if (posView.z > light.range || posView.z < -camera.far) continue;

      // Project to NDC
      const ndc = light.position.clone().project(camera as THREE.PerspectiveCamera);
      const screenX = (ndc.x * 0.5 + 0.5) * size.x;
      const screenY = (1 - (ndc.y * 0.5 + 0.5)) * size.y;

      // Compute screen-space radius (approx)
      const proj = (camera as THREE.PerspectiveCamera).projectionMatrix.elements;
      const radiusPixels = (light.range * proj[5]) / Math.max(0.0001, -posView.z);
      const radiusPx = Math.abs(radiusPixels);

      const minX = Math.floor((screenX - radiusPx) / this.config.tileSize);
      const maxX = Math.floor((screenX + radiusPx) / this.config.tileSize);
      const minY = Math.floor((screenY - radiusPx) / this.config.tileSize);
      const maxY = Math.floor((screenY + radiusPx) / this.config.tileSize);

      for (let ty = minY; ty <= maxY; ty++) {
        if (ty < 0 || ty >= this.tilesY) continue;
        for (let tx = minX; tx <= maxX; tx++) {
          if (tx < 0 || tx >= this.tilesX) continue;
          const idx = ty * this.tilesX + tx;
          const list = this.tileLists[idx];
          if (list.indices.length < this.config.maxLightsPerTile) {
            list.indices.push(i);
          }
        }
      }
    }
  }

  /**
   * Get tile lists and metadata for shading.
   */
  public getTileData(): {
    tileLists: TileLightList[];
    tilesX: number;
    tilesY: number;
    tileSize: number;
  } {
    return {
      tileLists: this.tileLists,
      tilesX: this.tilesX,
      tilesY: this.tilesY,
      tileSize: this.config.tileSize,
    };
  }
}

