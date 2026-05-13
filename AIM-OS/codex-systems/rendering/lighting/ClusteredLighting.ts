/**
 * Clustered Lighting (CPU scaffold)
 * Divides view frustum into 3D clusters and assigns lights per cluster.
 *
 * Features:
 * - 3D frustum clustering (x,y,z slices)
 * - Per-cluster light lists (CPU reference)
 * - Depth slicing exponential or linear
 * - Ready to upload as SSBO/texture for GPU shading
 *
 * Note: This is a CPU-side reference. In production, clustering + light
 * assignment should be done in a compute shader for scalability.
 */

import * as THREE from 'three';

// ============================================
// TYPES
// ============================================

export interface ClusteredConfig {
  slicesX: number;
  slicesY: number;
  slicesZ: number;
  near: number;
  far: number;
  depthMode: 'linear' | 'exponential';
}

export interface ClusterLightList {
  indices: number[];
}

export interface ClusteredLight {
  position: THREE.Vector3;
  color: THREE.Color;
  range: number;
  intensity: number;
}

// ============================================
// CLUSTERED LIGHTING
// ============================================

export class ClusteredLighting {
  private config: ClusteredConfig;
  private clusters: ClusterLightList[] = [];
  private lights: ClusteredLight[] = [];
  private frustumCorners: THREE.Vector3[] = new Array(8).fill(0).map(() => new THREE.Vector3());

  constructor(config: Partial<ClusteredConfig> = {}) {
    this.config = {
      slicesX: 16,
      slicesY: 9,
      slicesZ: 24,
      near: 0.1,
      far: 100,
      depthMode: 'exponential',
      ...config,
    };
    this.clusters = new Array(this.config.slicesX * this.config.slicesY * this.config.slicesZ)
      .fill(0)
      .map(() => ({ indices: [] }));
  }

  public setLights(lights: ClusteredLight[]): void {
    this.lights = lights;
  }

  /**
   * Build clusters for the current camera. Returns per-cluster light lists.
   */
  public buildClusters(camera: THREE.PerspectiveCamera): {
    clusters: ClusterLightList[];
    slicesX: number;
    slicesY: number;
    slicesZ: number;
  } {
    this.clusters.forEach(c => (c.indices = []));

    // Precompute frustum corners at near/far
    this.computeFrustumCorners(camera);

    // For each light, determine overlapping clusters (conservative)
    for (let i = 0; i < this.lights.length; i++) {
      const light = this.lights[i];
      const viewPos = light.position.clone().applyMatrix4(camera.matrixWorldInverse);

      if (viewPos.z > -this.config.near || viewPos.z < -this.config.far - light.range) continue;

      // Project to NDC to get x/y bounds
      const ndc = light.position.clone().project(camera);
      const screenX = ndc.x * 0.5 + 0.5;
      const screenY = ndc.y * 0.5 + 0.5;

      // Approximate screen-space radius
      const proj = camera.projectionMatrix.elements;
      const radiusPx = (light.range * proj[5]) / Math.max(0.0001, -viewPos.z);

      const minX = Math.floor((screenX - radiusPx) * this.config.slicesX);
      const maxX = Math.floor((screenX + radiusPx) * this.config.slicesX);
      const minY = Math.floor((1 - screenY - radiusPx) * this.config.slicesY);
      const maxY = Math.floor((1 - screenY + radiusPx) * this.config.slicesY);

      // Depth slices
      const minZ = this.depthToSlice(Math.max(this.config.near, -viewPos.z - light.range));
      const maxZ = this.depthToSlice(Math.min(this.config.far, -viewPos.z + light.range));

      for (let z = minZ; z <= maxZ; z++) {
        if (z < 0 || z >= this.config.slicesZ) continue;
        for (let y = minY; y <= maxY; y++) {
          if (y < 0 || y >= this.config.slicesY) continue;
          for (let x = minX; x <= maxX; x++) {
            if (x < 0 || x >= this.config.slicesX) continue;
            const idx = this.clusterIndex(x, y, z);
            const list = this.clusters[idx];
            list.indices.push(i);
          }
        }
      }
    }

    return {
      clusters: this.clusters,
      slicesX: this.config.slicesX,
      slicesY: this.config.slicesY,
      slicesZ: this.config.slicesZ,
    };
  }

  private depthToSlice(depth: number): number {
    if (this.config.depthMode === 'linear') {
      const t = (depth - this.config.near) / (this.config.far - this.config.near);
      return Math.floor(t * this.config.slicesZ);
    } else {
      // exponential
      const logNear = Math.log(this.config.near);
      const logFar = Math.log(this.config.far);
      const t = (Math.log(depth) - logNear) / (logFar - logNear);
      return Math.floor(t * this.config.slicesZ);
    }
  }

  private clusterIndex(x: number, y: number, z: number): number {
    return z * this.config.slicesX * this.config.slicesY + y * this.config.slicesX + x;
  }

  private computeFrustumCorners(camera: THREE.PerspectiveCamera): void {
    const invProjView = new THREE.Matrix4()
      .multiplyMatrices(camera.matrixWorld, camera.projectionMatrixInverse);

    const ndcCorners = [
      new THREE.Vector3(-1, -1, -1),
      new THREE.Vector3(1, -1, -1),
      new THREE.Vector3(-1, 1, -1),
      new THREE.Vector3(1, 1, -1),
      new THREE.Vector3(-1, -1, 1),
      new THREE.Vector3(1, -1, 1),
      new THREE.Vector3(-1, 1, 1),
      new THREE.Vector3(1, 1, 1),
    ];

    for (let i = 0; i < 8; i++) {
      this.frustumCorners[i].copy(ndcCorners[i]).applyMatrix4(invProjView);
    }
  }
}

