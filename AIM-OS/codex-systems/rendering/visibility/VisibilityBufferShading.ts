/**
 * Visibility Buffer Shading Pass
 * Consumes a visibility buffer (material IDs) + material table texture to shade.
 *
 * Intended to be paired with VisibilityBufferRenderer.
 */

import * as THREE from 'three';
import { VisibilityResult } from './VisibilityBufferRenderer';

export interface MaterialTableEntry {
  baseColor: THREE.Color;
  metallic: number;
  roughness: number;
  emissive: THREE.Color;
}

export class VisibilityBufferShading {
  private materialTableTex: THREE.DataTexture;
  private shadingMaterial: THREE.ShaderMaterial;
  private fsQuad: THREE.Mesh;
  private target: THREE.WebGLRenderTarget;

  constructor(width: number, height: number) {
    // Simple 1D material table encoded as RGBA32F (baseColor.rgb, metallic in A; emissive separate)
    const tex = new THREE.DataTexture(new Float32Array(4 * 256), 256, 1, THREE.RGBAFormat, THREE.FloatType);
    tex.needsUpdate = true;
    this.materialTableTex = tex;

    this.target = new THREE.WebGLRenderTarget(width, height, {
      minFilter: THREE.LinearFilter,
      magFilter: THREE.LinearFilter,
      format: THREE.RGBAFormat,
    });

    this.shadingMaterial = new THREE.ShaderMaterial({
      uniforms: {
        tVisibility: { value: null },
        tMaterialTable: { value: this.materialTableTex },
        resolution: { value: new THREE.Vector2(width, height) },
        lightDir: { value: new THREE.Vector3(0.4, 1, 0.2).normalize() },
        ambient: { value: new THREE.Color(0x222222) },
      },
      vertexShader: `
        varying vec2 vUv;
        void main() {
          vUv = uv;
          gl_Position = vec4(position, 1.0);
        }
      `,
      fragmentShader: `
        uniform sampler2D tVisibility;
        uniform sampler2D tMaterialTable;
        uniform vec2 resolution;
        uniform vec3 lightDir;
        uniform vec3 ambient;
        varying vec2 vUv;

        int decodeId(vec3 rgb) {
          int r = int(rgb.r * 255.0 + 0.5);
          int g = int(rgb.g * 255.0 + 0.5);
          int b = int(rgb.b * 255.0 + 0.5);
          return (r << 16) | (g << 8) | b;
        }

        void main() {
          vec3 enc = texture2D(tVisibility, vUv).rgb;
          int id = decodeId(enc);
          float u = (float(id) + 0.5) / 256.0;

          vec4 table = texture2D(tMaterialTable, vec2(u, 0.5)); // baseColor.rgb, metallic
          vec3 baseColor = table.rgb;
          float metallic = table.a;

          // Cheap shading
          float ndotl = clamp(dot(normalize(vec3(0,0,1)), lightDir), 0.0, 1.0);
          vec3 color = baseColor * (ambient + ndotl);
          color += baseColor * metallic * 0.1;
          gl_FragColor = vec4(color, 1.0);
        }
      `,
      depthTest: false,
      depthWrite: false,
    });

    const quadGeo = new THREE.PlaneGeometry(2, 2);
    this.fsQuad = new THREE.Mesh(quadGeo, this.shadingMaterial);
  }

  /**
   * Update material table (first 256 entries).
   */
  public updateMaterialTable(entries: Record<number, MaterialTableEntry>): void {
    const data = this.materialTableTex.image.data as Float32Array;
    Object.keys(entries).forEach(key => {
      const id = Number(key);
      if (id < 0 || id >= 256) return;
      const e = entries[id];
      const base = id * 4;
      data[base + 0] = e.baseColor.r;
      data[base + 1] = e.baseColor.g;
      data[base + 2] = e.baseColor.b;
      data[base + 3] = e.metallic;
      // roughness/emissive could go into another texture; simplified here.
    });
    this.materialTableTex.needsUpdate = true;
  }

  /**
   * Shade the visibility buffer into a color target.
   */
  public render(renderer: THREE.WebGLRenderer, visResult: VisibilityResult): THREE.WebGLRenderTarget {
    const current = renderer.getRenderTarget();
    this.shadingMaterial.uniforms.tVisibility.value = visResult.visibilityTarget.texture;
    const ortho = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
    const scene = new THREE.Scene();
    scene.add(this.fsQuad);
    renderer.setRenderTarget(this.target);
    renderer.render(scene, ortho);
    renderer.setRenderTarget(current);
    return this.target;
  }

  public setSize(width: number, height: number): void {
    this.target.setSize(width, height);
    this.shadingMaterial.uniforms.resolution.value.set(width, height);
  }

  public setLighting(ambient: THREE.Color, lightDir: THREE.Vector3): void {
    this.shadingMaterial.uniforms.ambient.value = ambient;
    this.shadingMaterial.uniforms.lightDir.value = lightDir;
  }

  public dispose(): void {
    this.target.dispose();
    this.materialTableTex.dispose();
    this.shadingMaterial.dispose();
    this.fsQuad.geometry.dispose();
  }
}

