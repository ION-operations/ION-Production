/**
 * Outline Effect System
 * Object highlighting and selection outlines
 * 
 * Features:
 * - Silhouette edge detection
 * - Multi-pass outline rendering
 * - Configurable thickness and color
 * - Glow effect
 * - Per-object colors
 * - XRay mode (visible through other objects)
 * - Pulse animation
 */

import * as THREE from 'three';

// ============================================
// TYPES
// ============================================

export interface OutlineConfig {
  edgeStrength: number;
  edgeGlow: number;
  edgeThickness: number;
  pulsePeriod: number;
  visibleEdgeColor: THREE.Color;
  hiddenEdgeColor: THREE.Color;
  usePatternTexture: boolean;
  xray: boolean;
}

export interface OutlineTarget {
  object: THREE.Object3D;
  color: THREE.Color;
  thickness: number;
  glow: number;
  pulse: boolean;
  xray: boolean;
}

// ============================================
// OUTLINE MATERIALS
// ============================================

const prepareVertexShader = `
  void main() {
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`;

const prepareFragmentShader = `
  void main() {
    gl_FragColor = vec4(1.0, 1.0, 1.0, 1.0);
  }
`;

const outlineVertexShader = `
  varying vec2 vUv;
  void main() {
    vUv = uv;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`;

const outlineFragmentShader = `
  uniform sampler2D maskTexture;
  uniform sampler2D sceneTexture;
  uniform vec2 resolution;
  uniform vec3 outlineColor;
  uniform float outlineThickness;
  uniform float edgeGlow;
  uniform float pulseIntensity;
  uniform bool xrayMode;
  
  varying vec2 vUv;
  
  void main() {
    vec4 sceneColor = texture2D(sceneTexture, vUv);
    vec4 maskColor = texture2D(maskTexture, vUv);
    
    // Edge detection using Sobel operator
    vec2 texelSize = 1.0 / resolution;
    
    float mask00 = texture2D(maskTexture, vUv + vec2(-texelSize.x, -texelSize.y) * outlineThickness).r;
    float mask01 = texture2D(maskTexture, vUv + vec2(0.0, -texelSize.y) * outlineThickness).r;
    float mask02 = texture2D(maskTexture, vUv + vec2(texelSize.x, -texelSize.y) * outlineThickness).r;
    float mask10 = texture2D(maskTexture, vUv + vec2(-texelSize.x, 0.0) * outlineThickness).r;
    float mask12 = texture2D(maskTexture, vUv + vec2(texelSize.x, 0.0) * outlineThickness).r;
    float mask20 = texture2D(maskTexture, vUv + vec2(-texelSize.x, texelSize.y) * outlineThickness).r;
    float mask21 = texture2D(maskTexture, vUv + vec2(0.0, texelSize.y) * outlineThickness).r;
    float mask22 = texture2D(maskTexture, vUv + vec2(texelSize.x, texelSize.y) * outlineThickness).r;
    
    // Sobel edge detection
    float sobelX = mask00 + 2.0 * mask10 + mask20 - mask02 - 2.0 * mask12 - mask22;
    float sobelY = mask00 + 2.0 * mask01 + mask02 - mask20 - 2.0 * mask21 - mask22;
    float edge = sqrt(sobelX * sobelX + sobelY * sobelY);
    
    // Apply glow
    float glow = 0.0;
    if (edgeGlow > 0.0) {
      for (float i = 1.0; i <= 4.0; i++) {
        float offset = i * 2.0;
        glow += texture2D(maskTexture, vUv + vec2(texelSize.x * offset, 0.0)).r;
        glow += texture2D(maskTexture, vUv + vec2(-texelSize.x * offset, 0.0)).r;
        glow += texture2D(maskTexture, vUv + vec2(0.0, texelSize.y * offset)).r;
        glow += texture2D(maskTexture, vUv + vec2(0.0, -texelSize.y * offset)).r;
      }
      glow = glow / 16.0 * edgeGlow;
    }
    
    // Combine
    float outline = clamp(edge + glow, 0.0, 1.0);
    
    // Apply pulse
    outline *= pulseIntensity;
    
    // Final color
    vec3 finalColor = sceneColor.rgb;
    
    if (xrayMode) {
      // Show outline even when occluded
      finalColor = mix(finalColor, outlineColor, outline);
    } else {
      // Only show outline where object is visible
      if (maskColor.r < 0.5) {
        finalColor = mix(finalColor, outlineColor, outline * 0.3); // Hidden edge
      } else {
        finalColor = mix(finalColor, outlineColor, outline);
      }
    }
    
    gl_FragColor = vec4(finalColor, 1.0);
  }
`;

// ============================================
// OUTLINE EFFECT
// ============================================

export class OutlineEffect {
  private scene: THREE.Scene;
  private camera: THREE.Camera;
  private renderer: THREE.WebGLRenderer;
  
  private config: OutlineConfig;
  private targets: Map<string, OutlineTarget> = new Map();
  
  // Render targets
  private maskRenderTarget: THREE.WebGLRenderTarget;
  private sceneRenderTarget: THREE.WebGLRenderTarget;
  
  // Materials
  private prepareMaterial: THREE.ShaderMaterial;
  private outlineMaterial: THREE.ShaderMaterial;
  
  // Full-screen quad
  private fsQuad: THREE.Mesh;
  
  private time: number = 0;
  
  constructor(
    renderer: THREE.WebGLRenderer,
    scene: THREE.Scene,
    camera: THREE.Camera,
    config: Partial<OutlineConfig> = {}
  ) {
    this.renderer = renderer;
    this.scene = scene;
    this.camera = camera;
    
    this.config = {
      edgeStrength: 3,
      edgeGlow: 0,
      edgeThickness: 1,
      pulsePeriod: 0,
      visibleEdgeColor: new THREE.Color(1, 1, 1),
      hiddenEdgeColor: new THREE.Color(0.1, 0.04, 0.02),
      usePatternTexture: false,
      xray: false,
      ...config
    };
    
    const size = renderer.getSize(new THREE.Vector2());
    
    // Create render targets
    this.maskRenderTarget = new THREE.WebGLRenderTarget(size.x, size.y, {
      minFilter: THREE.LinearFilter,
      magFilter: THREE.LinearFilter,
      format: THREE.RGBAFormat
    });
    
    this.sceneRenderTarget = new THREE.WebGLRenderTarget(size.x, size.y, {
      minFilter: THREE.LinearFilter,
      magFilter: THREE.LinearFilter,
      format: THREE.RGBAFormat
    });
    
    // Create materials
    this.prepareMaterial = new THREE.ShaderMaterial({
      vertexShader: prepareVertexShader,
      fragmentShader: prepareFragmentShader,
      side: THREE.DoubleSide
    });
    
    this.outlineMaterial = new THREE.ShaderMaterial({
      uniforms: {
        maskTexture: { value: this.maskRenderTarget.texture },
        sceneTexture: { value: this.sceneRenderTarget.texture },
        resolution: { value: new THREE.Vector2(size.x, size.y) },
        outlineColor: { value: this.config.visibleEdgeColor },
        outlineThickness: { value: this.config.edgeThickness },
        edgeGlow: { value: this.config.edgeGlow },
        pulseIntensity: { value: 1 },
        xrayMode: { value: this.config.xray }
      },
      vertexShader: outlineVertexShader,
      fragmentShader: outlineFragmentShader
    });
    
    // Create full-screen quad
    const geometry = new THREE.PlaneGeometry(2, 2);
    this.fsQuad = new THREE.Mesh(geometry, this.outlineMaterial);
  }
  
  /**
   * Add object to outline
   */
  public addOutline(
    object: THREE.Object3D,
    color?: THREE.Color,
    options: Partial<Omit<OutlineTarget, 'object' | 'color'>> = {}
  ): void {
    const target: OutlineTarget = {
      object,
      color: color?.clone() ?? this.config.visibleEdgeColor.clone(),
      thickness: options.thickness ?? this.config.edgeThickness,
      glow: options.glow ?? this.config.edgeGlow,
      pulse: options.pulse ?? false,
      xray: options.xray ?? this.config.xray
    };
    
    this.targets.set(object.uuid, target);
  }
  
  /**
   * Remove object outline
   */
  public removeOutline(object: THREE.Object3D): void {
    this.targets.delete(object.uuid);
  }
  
  /**
   * Clear all outlines
   */
  public clearOutlines(): void {
    this.targets.clear();
  }
  
  /**
   * Update outline color
   */
  public setOutlineColor(object: THREE.Object3D, color: THREE.Color): void {
    const target = this.targets.get(object.uuid);
    if (target) {
      target.color.copy(color);
    }
  }
  
  /**
   * Render with outlines
   */
  public render(deltaTime: number = 0.016): void {
    if (this.targets.size === 0) {
      // No outlines, render normally
      this.renderer.render(this.scene, this.camera);
      return;
    }
    
    this.time += deltaTime;
    
    const currentRenderTarget = this.renderer.getRenderTarget();
    const currentAutoClear = this.renderer.autoClear;
    
    // Store original object visibility and materials
    const originalState = new Map<THREE.Object3D, { visible: boolean; material: THREE.Material | THREE.Material[] }>();
    
    this.scene.traverse(obj => {
      if ((obj as THREE.Mesh).isMesh) {
        const mesh = obj as THREE.Mesh;
        originalState.set(obj, {
          visible: obj.visible,
          material: mesh.material
        });
      }
    });
    
    // Render scene to texture
    this.renderer.setRenderTarget(this.sceneRenderTarget);
    this.renderer.clear();
    this.renderer.render(this.scene, this.camera);
    
    // Render mask (only outlined objects)
    this.renderer.setRenderTarget(this.maskRenderTarget);
    this.renderer.clear();
    
    // Hide all objects
    this.scene.traverse(obj => {
      obj.visible = false;
    });
    
    // Show and render only outlined objects with prepare material
    for (const target of this.targets.values()) {
      target.object.visible = true;
      target.object.traverse(obj => {
        obj.visible = true;
        if ((obj as THREE.Mesh).isMesh) {
          (obj as THREE.Mesh).material = this.prepareMaterial;
        }
      });
    }
    
    this.renderer.render(this.scene, this.camera);
    
    // Restore original state
    for (const [obj, state] of originalState) {
      obj.visible = state.visible;
      if ((obj as THREE.Mesh).isMesh) {
        (obj as THREE.Mesh).material = state.material;
      }
    }
    
    // Calculate pulse intensity
    let pulseIntensity = 1;
    if (this.config.pulsePeriod > 0) {
      pulseIntensity = 0.5 + 0.5 * Math.sin(this.time * Math.PI * 2 / this.config.pulsePeriod);
    }
    
    // Update uniforms
    this.outlineMaterial.uniforms.pulseIntensity.value = pulseIntensity;
    
    // Get dominant outline color (or use first target's color)
    const firstTarget = this.targets.values().next().value;
    if (firstTarget) {
      this.outlineMaterial.uniforms.outlineColor.value = firstTarget.color;
      this.outlineMaterial.uniforms.outlineThickness.value = firstTarget.thickness;
      this.outlineMaterial.uniforms.edgeGlow.value = firstTarget.glow;
      this.outlineMaterial.uniforms.xrayMode.value = firstTarget.xray;
    }
    
    // Render composite to screen
    this.renderer.setRenderTarget(currentRenderTarget);
    this.renderer.autoClear = false;
    
    const orthoCamera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
    const orthoScene = new THREE.Scene();
    orthoScene.add(this.fsQuad);
    
    this.renderer.render(orthoScene, orthoCamera);
    
    this.renderer.autoClear = currentAutoClear;
  }
  
  /**
   * Set resolution
   */
  public setSize(width: number, height: number): void {
    this.maskRenderTarget.setSize(width, height);
    this.sceneRenderTarget.setSize(width, height);
    this.outlineMaterial.uniforms.resolution.value.set(width, height);
  }
  
  /**
   * Set config
   */
  public setConfig(config: Partial<OutlineConfig>): void {
    Object.assign(this.config, config);
    
    if (config.visibleEdgeColor) {
      this.outlineMaterial.uniforms.outlineColor.value = config.visibleEdgeColor;
    }
    if (config.edgeThickness !== undefined) {
      this.outlineMaterial.uniforms.outlineThickness.value = config.edgeThickness;
    }
    if (config.edgeGlow !== undefined) {
      this.outlineMaterial.uniforms.edgeGlow.value = config.edgeGlow;
    }
    if (config.xray !== undefined) {
      this.outlineMaterial.uniforms.xrayMode.value = config.xray;
    }
  }
  
  /**
   * Check if object has outline
   */
  public hasOutline(object: THREE.Object3D): boolean {
    return this.targets.has(object.uuid);
  }
  
  /**
   * Get outlined objects
   */
  public getOutlinedObjects(): THREE.Object3D[] {
    return Array.from(this.targets.values()).map(t => t.object);
  }
  
  /**
   * Dispose
   */
  public dispose(): void {
    this.maskRenderTarget.dispose();
    this.sceneRenderTarget.dispose();
    this.prepareMaterial.dispose();
    this.outlineMaterial.dispose();
    this.fsQuad.geometry.dispose();
    this.targets.clear();
  }
}

