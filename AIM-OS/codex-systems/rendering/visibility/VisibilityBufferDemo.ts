/**
 * Visibility Buffer Demo
 * Renders a scene with VisibilityBufferRenderer + VisibilityBufferShading.
 */

import * as THREE from 'three';
import { VisibilityBufferRenderer } from './VisibilityBufferRenderer';
import { VisibilityBufferShading, MaterialTableEntry } from './VisibilityBufferShading';

export class VisibilityBufferDemo {
  private vbRenderer: VisibilityBufferRenderer;
  private vbShading: VisibilityBufferShading;
  private scene: THREE.Scene;
  private camera: THREE.Camera;
  private renderer: THREE.WebGLRenderer;

  constructor(
    renderer: THREE.WebGLRenderer,
    scene: THREE.Scene,
    camera: THREE.Camera,
    width: number,
    height: number
  ) {
    this.renderer = renderer;
    this.scene = scene;
    this.camera = camera;
    this.vbRenderer = new VisibilityBufferRenderer(renderer, scene, camera, {
      width,
      height,
    });
    this.vbShading = new VisibilityBufferShading(width, height);
  }

  public setMaterialTable(entries: Record<number, MaterialTableEntry>): void {
    this.vbShading.updateMaterialTable(entries);
  }

  /**
   * Render visibility + shading. Returns the shaded color target.
   */
  public render(): THREE.WebGLRenderTarget {
    const vis = this.vbRenderer.render();
    return this.vbShading.render(this.renderer, vis);
  }

  public setSize(width: number, height: number): void {
    this.vbRenderer['config'].width = width;
    this.vbRenderer['config'].height = height;
    this.vbShading.setSize(width, height);
  }

  public dispose(): void {
    this.vbShading.dispose();
  }
}

