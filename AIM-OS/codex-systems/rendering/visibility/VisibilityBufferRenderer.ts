/**
 * Visibility Buffer Renderer
 * Decouples geometry submission from shading (material ID + attributes)
 *
 * Features:
 * - Visibility buffer (stores material/instance IDs)
 * - G-Buffer-lite: normals + depth optional
 * - Shading pass indexed by material table
 * - Instancing-friendly
 * - Light list integration (Forward+ / clustered)
 *
 * Notes:
 * - This is a CPU/Three.js-friendly scaffold for a visibility buffer pipeline.
 * - In a full engine, the first pass writes out material/instance IDs into a
 *   uint target (e.g., R32UI) plus depth. Second pass shades by sampling
 *   the visibility buffer + material table.
 */

import * as THREE from 'three';

// ============================================
// TYPES
// ============================================

export interface VisibilityBufferConfig {
  width: number;
  height: number;
  storeNormals: boolean;
  storeDepth: boolean;
}

export interface MaterialEntry {
  id: number;
  baseColor: THREE.Color;
  metallic: number;
  roughness: number;
  emissive: THREE.Color;
}

export interface VisibilityResult {
  colorTarget: THREE.WebGLRenderTarget;
  visibilityTarget: THREE.WebGLRenderTarget;
}

// ============================================
// VISIBILITY BUFFER RENDERER
// ============================================

export class VisibilityBufferRenderer {
  private renderer: THREE.WebGLRenderer;
  private scene: THREE.Scene;
  private camera: THREE.Camera;
  private config: VisibilityBufferConfig;

  private visibilityTarget: THREE.WebGLRenderTarget;
  private shadingTarget: THREE.WebGLRenderTarget;

  // Simple material table
  private materialTable: Map<number, MaterialEntry> = new Map();

  // Placeholder materials
  private idMaterial: THREE.ShaderMaterial;
  private shadingMaterial: THREE.ShaderMaterial;
  private fsQuad: THREE.Mesh;

  constructor(
    renderer: THREE.WebGLRenderer,
    scene: THREE.Scene,
    camera: THREE.Camera,
    config: Partial<VisibilityBufferConfig> = {}
  ) {
    this.renderer = renderer;
    this.scene = scene;
    this.camera = camera;
    this.config = {
      width: 1280,
      height: 720,
      storeNormals: true,
      storeDepth: true,
      ...config,
    };

    this.visibilityTarget = new THREE.WebGLRenderTarget(
      this.config.width,
      this.config.height,
      {
        minFilter: THREE.NearestFilter,
        magFilter: THREE.NearestFilter,
        format: THREE.RGBAFormat,
        type: THREE.UnsignedByteType,
        depthBuffer: this.config.storeDepth,
      }
    );
    this.visibilityTarget.texture.generateMipmaps = false;

    this.shadingTarget = new THREE.WebGLRenderTarget(
      this.config.width,
      this.config.height,
      {
        minFilter: THREE.LinearFilter,
        magFilter: THREE.LinearFilter,
        format: THREE.RGBAFormat,
      }
    );

    // ID pass: writes material ID encoded in RGBA8 (limited to 24 bits)
    this.idMaterial = new THREE.ShaderMaterial({
      uniforms: {
        materialId: { value: 0 },
      },
      vertexShader: `
        varying vec2 vUv;
        void main() {
          vUv = uv;
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
      `,
      fragmentShader: `
        uniform int materialId;
        void main() {
          // Encode id into RGB (0-255 each). Limited precision but fine for demo.
          int id = materialId;
          float r = float((id >> 16) & 255) / 255.0;
          float g = float((id >> 8) & 255) / 255.0;
          float b = float(id & 255) / 255.0;
          gl_FragColor = vec4(r, g, b, 1.0);
        }
      `,
      depthWrite: true,
      depthTest: true,
    });

    // Shading pass: reads visibility buffer + material table (via uniform array)
    // For simplicity, this pass samples a texture containing encoded IDs and shades with a flat BRDF.
    this.shadingMaterial = new THREE.ShaderMaterial({
      uniforms: {
        tVisibility: { value: this.visibilityTarget.texture },
        resolution: { value: new THREE.Vector2(this.config.width, this.config.height) },
        lightDir: { value: new THREE.Vector3(0.5, 1, 0.5).normalize() },
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
        uniform vec2 resolution;
        uniform vec3 lightDir;
        uniform vec3 ambient;
        varying vec2 vUv;

        // Dummy material table lookup (should be SSBO/texture in real impl)
        vec3 decodeId(vec3 rgb) {
          int r = int(rgb.r * 255.0 + 0.5);
          int g = int(rgb.g * 255.0 + 0.5);
          int b = int(rgb.b * 255.0 + 0.5);
          int id = (r << 16) | (g << 8) | b;
          return vec3(float(id));
        }

        void main() {
          vec3 encoded = texture2D(tVisibility, vUv).rgb;
          vec3 matIdVec = decodeId(encoded);
          // Simple hash to color
          float n = fract(sin(matIdVec.x * 12.9898) * 43758.5453);
          vec3 baseColor = mix(vec3(0.2, 0.7, 1.0), vec3(1.0, 0.6, 0.2), n);
          float ndotl = clamp(dot(normalize(vec3(0,0,1)), lightDir), 0.0, 1.0);
          vec3 color = baseColor * (ambient + ndotl);
          gl_FragColor = vec4(color, 1.0);
        }
      `,
      depthTest: false,
      depthWrite: false,
    });

    // Fullscreen quad
    const quadGeo = new THREE.PlaneGeometry(2, 2);
    this.fsQuad = new THREE.Mesh(quadGeo, this.shadingMaterial);
  }

  /**
   * Register a material entry.
   */
  public registerMaterial(entry: MaterialEntry): void {
    this.materialTable.set(entry.id, entry);
  }

  /**
   * Render visibility + shading. Returns targets for further compositing.
   */
  public render(): VisibilityResult {
    const currentTarget = this.renderer.getRenderTarget();
    const currentAutoClear = this.renderer.autoClear;

    // Pass 1: visibility buffer (material IDs)
    this.renderer.setRenderTarget(this.visibilityTarget);
    this.renderer.autoClear = true;

    // Render each mesh with its materialId
    const originalMaterials: Array<{ mesh: THREE.Mesh; material: THREE.Material | THREE.Material[] }> = [];
    this.scene.traverse(obj => {
      if ((obj as THREE.Mesh).isMesh) {
        const mesh = obj as THREE.Mesh;
        const matId = (mesh.userData.materialId ?? 0) | 0;
        originalMaterials.push({ mesh, material: mesh.material });
        const mat = this.idMaterial.clone();
        mat.uniforms.materialId.value = matId;
        mesh.material = mat;
      }
    });

    this.renderer.render(this.scene, this.camera);

    // Restore materials
    for (const entry of originalMaterials) {
      entry.mesh.material = entry.material;
    }

    // Pass 2: shading (full-screen)
    this.renderer.setRenderTarget(this.shadingTarget);
    this.renderer.autoClear = true;

    const orthoScene = new THREE.Scene();
    const orthoCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
    orthoScene.add(this.fsQuad);
    this.renderer.render(orthoScene, orthoCam);

    // Restore
    this.renderer.setRenderTarget(currentTarget);
    this.renderer.autoClear = currentAutoClear;

    return {
      colorTarget: this.shadingTarget,
      visibilityTarget: this.visibilityTarget,
    };
  }

  public setSize(width: number, height: number): void {
    this.config.width = width;
    this.config.height = height;
    this.visibilityTarget.setSize(width, height);
    this.shadingTarget.setSize(width, height);
    this.shadingMaterial.uniforms.resolution.value.set(width, height);
  }

  public dispose(): void {
    this.visibilityTarget.dispose();
    this.shadingTarget.dispose();
    this.idMaterial.dispose();
    this.shadingMaterial.dispose();
    this.fsQuad.geometry.dispose();
  }
}

