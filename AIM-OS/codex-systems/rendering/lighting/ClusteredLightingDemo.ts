/**
 * Clustered Lighting Demo
 * Builds clustered light lists and exposes uniform-ready buffers (CPU scaffold).
 */

import * as THREE from 'three';
import { ClusteredLighting, ClusteredLight } from './ClusteredLighting';

export class ClusteredLightingDemo {
  private clustered: ClusteredLighting;
  private camera: THREE.PerspectiveCamera;
  private lights: ClusteredLight[] = [];

  constructor(camera: THREE.PerspectiveCamera) {
    this.camera = camera;
    this.clustered = new ClusteredLighting({
      slicesX: 16,
      slicesY: 9,
      slicesZ: 24,
      near: 0.1,
      far: camera.far,
      depthMode: 'exponential',
    });
  }

  public setLights(lights: ClusteredLight[]): void {
    this.lights = lights;
  }

  public build() {
    this.clustered.setLights(this.lights);
    return this.clustered.buildClusters(this.camera);
  }
}

