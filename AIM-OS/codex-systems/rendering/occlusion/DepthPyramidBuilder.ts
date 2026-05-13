/**
 * Depth Pyramid Builder (Hi-Z) for WebGL2
 * Generates a mipmapped depth pyramid usable for occlusion culling.
 *
 * Notes:
 * - WebGL2 lacks native depth texture mipmaps; we downsample depth into RGBA targets.
 * - For true depth compare, shaders should reconstruct depth and take min.
 * - This is a scaffold for integration with GPUOcclusionCulling.
 */

import * as THREE from 'three';

export interface DepthPyramidConfig {
  width: number;
  height: number;
  levels?: number; // optional override
}

export class DepthPyramidBuilder {
  private renderer: THREE.WebGLRenderer;
  private config: DepthPyramidConfig;
  private pyramid: THREE.WebGLRenderTarget[];
  private downsampleMaterial: THREE.ShaderMaterial;

  constructor(renderer: THREE.WebGLRenderer, config: DepthPyramidConfig) {
    this.renderer = renderer;
    this.config = config;

    const maxDim = Math.max(config.width, config.height);
    const levels = config.levels ?? Math.floor(Math.log2(maxDim)) + 1;

    this.pyramid = [];
    for (let i = 0; i < levels; i++) {
      const w = Math.max(1, config.width >> i);
      const h = Math.max(1, config.height >> i);
      this.pyramid.push(
        new THREE.WebGLRenderTarget(w, h, {
          minFilter: THREE.NearestFilter,
          magFilter: THREE.NearestFilter,
          format: THREE.RGBAFormat,
          type: THREE.UnsignedByteType,
          depthBuffer: false,
          stencilBuffer: false,
        })
      );
    }

    this.downsampleMaterial = new THREE.ShaderMaterial({
      uniforms: {
        tDepth: { value: null },
        texelSize: { value: new THREE.Vector2() },
      },
      vertexShader: `
        varying vec2 vUv;
        void main() {
          vUv = uv;
          gl_Position = vec4(position.xy, 0.0, 1.0);
        }
      `,
      fragmentShader: `
        uniform sampler2D tDepth;
        uniform vec2 texelSize;
        varying vec2 vUv;
        void main() {
          // 2x2 min reduction
          float d0 = texture2D(tDepth, vUv + vec2(0.0, 0.0) * texelSize).r;
          float d1 = texture2D(tDepth, vUv + vec2(texelSize.x, 0.0)).r;
          float d2 = texture2D(tDepth, vUv + vec2(0.0, texelSize.y)).r;
          float d3 = texture2D(tDepth, vUv + texelSize).r;
          float m = min(min(d0, d1), min(d2, d3));
          gl_FragColor = vec4(m, m, m, 1.0);
        }
      `,
      depthTest: false,
      depthWrite: false,
    });
  }

  /**
   * Build pyramid from a depth texture (depth rendered to color).
   * level0 is assumed to already contain the base depth in pyramid[0].
   */
  public build(baseDepth: THREE.Texture): THREE.WebGLRenderTarget[] {
    const current = this.renderer.getRenderTarget();
    const quadScene = new THREE.Scene();
    const quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), this.downsampleMaterial);
    const ortho = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
    quadScene.add(quad);

    // level 0
    this.downsampleMaterial.uniforms.tDepth.value = baseDepth;
    this.downsampleMaterial.uniforms.texelSize.value.set(
      1 / this.pyramid[0].width,
      1 / this.pyramid[0].height
    );
    this.renderer.setRenderTarget(this.pyramid[0]);
    this.renderer.render(quadScene, ortho);

    // subsequent levels
    for (let i = 1; i < this.pyramid.length; i++) {
      const prev = this.pyramid[i - 1].texture;
      this.downsampleMaterial.uniforms.tDepth.value = prev;
      this.downsampleMaterial.uniforms.texelSize.value.set(
        1 / this.pyramid[i - 1].width,
        1 / this.pyramid[i - 1].height
      );
      this.renderer.setRenderTarget(this.pyramid[i]);
      this.renderer.render(quadScene, ortho);
    }

    this.renderer.setRenderTarget(current);
    return this.pyramid;
  }

  public dispose(): void {
    this.pyramid.forEach(rt => rt.dispose());
    this.downsampleMaterial.dispose();
  }
}

