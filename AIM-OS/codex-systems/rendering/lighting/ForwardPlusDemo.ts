/**
 * Forward+ Lighting Demo
 * CPU reference demo that builds tile light lists and feeds a simple shader.
 */

import * as THREE from 'three';
import { ForwardPlusLighting, LightData } from './ForwardPlusLighting';
import { buildTileTexture } from './ForwardPlusTileBuilder';
import { createForwardPlusMaterial } from './ForwardPlusShader';

export class ForwardPlusDemo {
  private fwd: ForwardPlusLighting;
  private renderer: THREE.WebGLRenderer;
  private camera: THREE.PerspectiveCamera;
  private lights: LightData[] = [];
  private tileTexture: THREE.DataTexture | null = null;

  constructor(renderer: THREE.WebGLRenderer, camera: THREE.PerspectiveCamera) {
    this.renderer = renderer;
    this.camera = camera;
    this.fwd = new ForwardPlusLighting({
      tileSize: 32,
      maxLightsPerTile: 64,
    });
  }

  public setLights(lights: LightData[]): void {
    this.lights = lights;
  }

  public build(): void {
    this.fwd.setLights(this.lights);
    this.fwd.buildLightLists(this.renderer, this.camera);
  }

  /**
   * Build tile texture and a ready-to-use Forward+ material.
   */
  public buildMaterial(): { material: THREE.ShaderMaterial; tileTexture: THREE.DataTexture } {
    const tileData = this.fwd.getTileData();
    this.tileTexture = buildTileTexture(
      tileData.tileLists,
      tileData.tilesX,
      tileData.tilesY,
      this.fwd['config'].maxLightsPerTile,
      this.lights.length
    );

    // Flatten light arrays
    const maxLights = this.lights.length;
    const lp = new Float32Array(maxLights * 3);
    const lc = new Float32Array(maxLights * 3);
    const lr = new Float32Array(maxLights);
    const li = new Float32Array(maxLights);
    for (let i = 0; i < maxLights; i++) {
      lp[i * 3 + 0] = this.lights[i].position.x;
      lp[i * 3 + 1] = this.lights[i].position.y;
      lp[i * 3 + 2] = this.lights[i].position.z;
      lc[i * 3 + 0] = this.lights[i].color.r;
      lc[i * 3 + 1] = this.lights[i].color.g;
      lc[i * 3 + 2] = this.lights[i].color.b;
      lr[i] = this.lights[i].range;
      li[i] = this.lights[i].intensity;
    }

    const material = createForwardPlusMaterial({
      tilesX: tileData.tilesX,
      tilesY: tileData.tilesY,
      maxLightsPerTile: this.fwd['config'].maxLightsPerTile,
      tileTexture: this.tileTexture,
      maxLights,
      lightPositions: lp,
      lightColors: lc,
      lightRanges: lr,
      lightIntensity: li,
    });

    return { material, tileTexture: this.tileTexture };
  }
}

