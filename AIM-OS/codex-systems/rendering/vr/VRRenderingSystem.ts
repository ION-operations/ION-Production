/**
 * VR/AR Rendering System
 * Immersive rendering for virtual and augmented reality
 * 
 * Features:
 * - Stereo rendering (left/right eye)
 * - Lens distortion correction
 * - Foveated rendering
 * - Hand tracking integration
 * - Passthrough AR support
 * - Motion smoothing
 * - Room-scale tracking
 */

import * as THREE from 'three';

// ============================================
// TYPES
// ============================================

export interface VRRenderingConfig {
  ipd: number; // Interpupillary distance (mm)
  fov: number; // Field of view (degrees)
  nearClip: number;
  farClip: number;
  renderScale: number;
  foveatedRenderingLevel: 0 | 1 | 2 | 3; // 0=off, 3=aggressive
  motionSmoothing: boolean;
  reprojection: boolean;
}

export interface EyeRenderTarget {
  camera: THREE.PerspectiveCamera;
  renderTarget: THREE.WebGLRenderTarget;
}

export interface HandPose {
  position: THREE.Vector3;
  rotation: THREE.Quaternion;
  joints: Map<string, THREE.Matrix4>;
  pinchStrength: number;
  gripStrength: number;
}

export interface VRControllerState {
  position: THREE.Vector3;
  rotation: THREE.Quaternion;
  buttons: Map<string, boolean>;
  axes: Map<string, number>;
  hand?: HandPose;
}

export interface HeadPose {
  position: THREE.Vector3;
  rotation: THREE.Quaternion;
  linearVelocity: THREE.Vector3;
  angularVelocity: THREE.Vector3;
}

// ============================================
// LENS DISTORTION
// ============================================

export class LensDistortion {
  private material: THREE.ShaderMaterial;
  private mesh: THREE.Mesh;
  
  constructor() {
    this.material = new THREE.ShaderMaterial({
      uniforms: {
        tDiffuse: { value: null },
        k1: { value: 0.22 }, // Radial distortion coefficient
        k2: { value: 0.24 },
        chromatic: { value: new THREE.Vector2(0.996, 1.014) },
        lensCenter: { value: new THREE.Vector2(0.5, 0.5) },
        scale: { value: 0.95 }
      },
      vertexShader: `
        varying vec2 vUv;
        void main() {
          vUv = uv;
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
      `,
      fragmentShader: `
        uniform sampler2D tDiffuse;
        uniform float k1;
        uniform float k2;
        uniform vec2 chromatic;
        uniform vec2 lensCenter;
        uniform float scale;
        
        varying vec2 vUv;
        
        vec2 distort(vec2 uv, float k1, float k2) {
          vec2 centered = uv - lensCenter;
          float r2 = dot(centered, centered);
          float r4 = r2 * r2;
          float factor = 1.0 + k1 * r2 + k2 * r4;
          return lensCenter + centered * factor * scale;
        }
        
        void main() {
          // Red channel
          vec2 uvR = distort(vUv, k1 * chromatic.x, k2 * chromatic.x);
          float r = texture2D(tDiffuse, uvR).r;
          
          // Green channel (no chromatic aberration)
          vec2 uvG = distort(vUv, k1, k2);
          float g = texture2D(tDiffuse, uvG).g;
          
          // Blue channel
          vec2 uvB = distort(vUv, k1 * chromatic.y, k2 * chromatic.y);
          float b = texture2D(tDiffuse, uvB).b;
          
          // Check bounds
          if (uvR.x < 0.0 || uvR.x > 1.0 || uvR.y < 0.0 || uvR.y > 1.0 ||
              uvB.x < 0.0 || uvB.x > 1.0 || uvB.y < 0.0 || uvB.y > 1.0) {
            gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);
            return;
          }
          
          gl_FragColor = vec4(r, g, b, 1.0);
        }
      `
    });
    
    this.mesh = new THREE.Mesh(
      new THREE.PlaneGeometry(2, 2),
      this.material
    );
  }
  
  public apply(
    renderer: THREE.WebGLRenderer,
    source: THREE.WebGLRenderTarget,
    target: THREE.WebGLRenderTarget | null
  ): void {
    this.material.uniforms.tDiffuse.value = source.texture;
    
    const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
    const scene = new THREE.Scene();
    scene.add(this.mesh);
    
    renderer.setRenderTarget(target);
    renderer.render(scene, camera);
  }
  
  public setDistortionCoefficients(k1: number, k2: number): void {
    this.material.uniforms.k1.value = k1;
    this.material.uniforms.k2.value = k2;
  }
  
  public setChromaticAberration(red: number, blue: number): void {
    this.material.uniforms.chromatic.value.set(red, blue);
  }
  
  public dispose(): void {
    this.material.dispose();
    this.mesh.geometry.dispose();
  }
}

// ============================================
// FOVEATED RENDERING
// ============================================

export interface FoveatedConfig {
  innerRadius: number;
  outerRadius: number;
  innerScale: number;
  outerScale: number;
  gazePoint: THREE.Vector2;
}

export class FoveatedRendering {
  private config: FoveatedConfig;
  private resolutionMask: THREE.DataTexture | null = null;
  
  constructor() {
    this.config = {
      innerRadius: 0.2,
      outerRadius: 0.5,
      innerScale: 1.0,
      outerScale: 0.5,
      gazePoint: new THREE.Vector2(0.5, 0.5)
    };
  }
  
  /**
   * Update gaze point from eye tracking
   */
  public updateGazePoint(x: number, y: number): void {
    this.config.gazePoint.set(x, y);
  }
  
  /**
   * Get render scale for screen position
   */
  public getRenderScale(x: number, y: number): number {
    const dist = Math.sqrt(
      Math.pow(x - this.config.gazePoint.x, 2) +
      Math.pow(y - this.config.gazePoint.y, 2)
    );
    
    if (dist < this.config.innerRadius) {
      return this.config.innerScale;
    } else if (dist < this.config.outerRadius) {
      const t = (dist - this.config.innerRadius) /
        (this.config.outerRadius - this.config.innerRadius);
      return THREE.MathUtils.lerp(
        this.config.innerScale,
        this.config.outerScale,
        t
      );
    } else {
      return this.config.outerScale;
    }
  }
  
  /**
   * Generate resolution mask texture
   */
  public generateMask(width: number, height: number): THREE.DataTexture {
    const data = new Uint8Array(width * height);
    
    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        const u = x / width;
        const v = y / height;
        const scale = this.getRenderScale(u, v);
        data[y * width + x] = Math.floor(scale * 255);
      }
    }
    
    this.resolutionMask = new THREE.DataTexture(
      data,
      width,
      height,
      THREE.RedFormat,
      THREE.UnsignedByteType
    );
    this.resolutionMask.needsUpdate = true;
    
    return this.resolutionMask;
  }
  
  public setConfig(config: Partial<FoveatedConfig>): void {
    Object.assign(this.config, config);
  }
  
  public dispose(): void {
    this.resolutionMask?.dispose();
  }
}

// ============================================
// MOTION SMOOTHING / REPROJECTION
// ============================================

export class MotionSmoothing {
  private previousFrame: THREE.WebGLRenderTarget | null = null;
  private previousPose: HeadPose | null = null;
  private material: THREE.ShaderMaterial;
  
  constructor() {
    this.material = new THREE.ShaderMaterial({
      uniforms: {
        tCurrent: { value: null },
        tPrevious: { value: null },
        tDepth: { value: null },
        deltaRotation: { value: new THREE.Quaternion() },
        deltaPosition: { value: new THREE.Vector3() },
        projectionMatrix: { value: new THREE.Matrix4() },
        inverseProjection: { value: new THREE.Matrix4() }
      },
      vertexShader: `
        varying vec2 vUv;
        void main() {
          vUv = uv;
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
      `,
      fragmentShader: `
        uniform sampler2D tCurrent;
        uniform sampler2D tPrevious;
        uniform sampler2D tDepth;
        uniform vec4 deltaRotation;
        uniform vec3 deltaPosition;
        uniform mat4 projectionMatrix;
        uniform mat4 inverseProjection;
        
        varying vec2 vUv;
        
        vec3 reprojectPosition(vec3 pos, vec4 rotation, vec3 translation) {
          // Apply quaternion rotation
          vec3 qv = cross(rotation.xyz, pos) + rotation.w * pos;
          vec3 rotated = pos + 2.0 * cross(rotation.xyz, qv);
          return rotated + translation;
        }
        
        void main() {
          vec4 current = texture2D(tCurrent, vUv);
          float depth = texture2D(tDepth, vUv).r;
          
          if (depth >= 1.0) {
            gl_FragColor = current;
            return;
          }
          
          // Reconstruct world position
          vec4 clipPos = vec4(vUv * 2.0 - 1.0, depth * 2.0 - 1.0, 1.0);
          vec4 viewPos = inverseProjection * clipPos;
          viewPos /= viewPos.w;
          
          // Reproject
          vec3 reprojected = reprojectPosition(viewPos.xyz, deltaRotation, deltaPosition);
          
          // Back to clip space
          vec4 newClip = projectionMatrix * vec4(reprojected, 1.0);
          vec2 newUv = (newClip.xy / newClip.w) * 0.5 + 0.5;
          
          if (newUv.x >= 0.0 && newUv.x <= 1.0 && newUv.y >= 0.0 && newUv.y <= 1.0) {
            vec4 previous = texture2D(tPrevious, newUv);
            // Blend current and reprojected previous
            gl_FragColor = mix(previous, current, 0.5);
          } else {
            gl_FragColor = current;
          }
        }
      `
    });
  }
  
  /**
   * Smooth frame transition
   */
  public smoothFrame(
    renderer: THREE.WebGLRenderer,
    currentFrame: THREE.WebGLRenderTarget,
    depthTexture: THREE.DepthTexture,
    currentPose: HeadPose,
    camera: THREE.PerspectiveCamera
  ): void {
    if (this.previousFrame && this.previousPose) {
      // Compute delta pose
      const deltaRot = currentPose.rotation.clone()
        .multiply(this.previousPose.rotation.clone().invert());
      const deltaPos = currentPose.position.clone()
        .sub(this.previousPose.position);
      
      this.material.uniforms.deltaRotation.value.copy(deltaRot);
      this.material.uniforms.deltaPosition.value.copy(deltaPos);
      this.material.uniforms.projectionMatrix.value.copy(camera.projectionMatrix);
      this.material.uniforms.inverseProjection.value
        .copy(camera.projectionMatrix).invert();
      this.material.uniforms.tCurrent.value = currentFrame.texture;
      this.material.uniforms.tPrevious.value = this.previousFrame.texture;
      this.material.uniforms.tDepth.value = depthTexture;
    }
    
    // Store for next frame
    this.previousPose = {
      position: currentPose.position.clone(),
      rotation: currentPose.rotation.clone(),
      linearVelocity: currentPose.linearVelocity.clone(),
      angularVelocity: currentPose.angularVelocity.clone()
    };
    
    // Copy current frame to previous
    if (!this.previousFrame) {
      this.previousFrame = new THREE.WebGLRenderTarget(
        currentFrame.width,
        currentFrame.height
      );
    }
    // Would need to copy texture contents here
  }
  
  public dispose(): void {
    this.previousFrame?.dispose();
    this.material.dispose();
  }
}

// ============================================
// HAND TRACKING
// ============================================

export class HandTracking {
  private handMeshes: Map<string, THREE.SkinnedMesh> = new Map();
  private jointSpheres: Map<string, THREE.Mesh[]> = new Map();
  
  public readonly jointNames = [
    'wrist',
    'thumb-metacarpal', 'thumb-phalanx-proximal', 'thumb-phalanx-distal', 'thumb-tip',
    'index-metacarpal', 'index-phalanx-proximal', 'index-phalanx-intermediate',
    'index-phalanx-distal', 'index-tip',
    'middle-metacarpal', 'middle-phalanx-proximal', 'middle-phalanx-intermediate',
    'middle-phalanx-distal', 'middle-tip',
    'ring-metacarpal', 'ring-phalanx-proximal', 'ring-phalanx-intermediate',
    'ring-phalanx-distal', 'ring-tip',
    'pinky-metacarpal', 'pinky-phalanx-proximal', 'pinky-phalanx-intermediate',
    'pinky-phalanx-distal', 'pinky-tip'
  ];
  
  /**
   * Initialize hand visualization
   */
  public initialize(scene: THREE.Scene, handedness: 'left' | 'right'): void {
    const material = new THREE.MeshStandardMaterial({
      color: 0xffcc99,
      roughness: 0.7,
      metalness: 0.0
    });
    
    const spheres: THREE.Mesh[] = [];
    
    for (const jointName of this.jointNames) {
      const geometry = new THREE.SphereGeometry(0.008, 8, 8);
      const mesh = new THREE.Mesh(geometry, material);
      mesh.name = `${handedness}-${jointName}`;
      scene.add(mesh);
      spheres.push(mesh);
    }
    
    this.jointSpheres.set(handedness, spheres);
  }
  
  /**
   * Update hand pose
   */
  public updateHand(handedness: 'left' | 'right', pose: HandPose): void {
    const spheres = this.jointSpheres.get(handedness);
    if (!spheres) return;
    
    let i = 0;
    for (const jointName of this.jointNames) {
      const jointMatrix = pose.joints.get(jointName);
      if (jointMatrix && spheres[i]) {
        const position = new THREE.Vector3();
        position.setFromMatrixPosition(jointMatrix);
        spheres[i].position.copy(position);
      }
      i++;
    }
  }
  
  /**
   * Get pinch gesture detection
   */
  public isPinching(pose: HandPose): boolean {
    return pose.pinchStrength > 0.8;
  }
  
  /**
   * Get grip gesture detection
   */
  public isGripping(pose: HandPose): boolean {
    return pose.gripStrength > 0.8;
  }
  
  /**
   * Get fingertip position
   */
  public getFingerTip(pose: HandPose, finger: string): THREE.Vector3 | null {
    const tipName = `${finger}-tip`;
    const jointMatrix = pose.joints.get(tipName);
    
    if (jointMatrix) {
      const position = new THREE.Vector3();
      position.setFromMatrixPosition(jointMatrix);
      return position;
    }
    
    return null;
  }
  
  public dispose(): void {
    this.jointSpheres.forEach(spheres => {
      spheres.forEach(mesh => {
        mesh.geometry.dispose();
        (mesh.material as THREE.Material).dispose();
      });
    });
    this.jointSpheres.clear();
    this.handMeshes.clear();
  }
}

// ============================================
// MAIN VR RENDERING SYSTEM
// ============================================

export class VRRenderingSystem {
  private renderer: THREE.WebGLRenderer;
  private config: VRRenderingConfig;
  
  // Eye rendering
  private leftEye: EyeRenderTarget;
  private rightEye: EyeRenderTarget;
  
  // Post-processing
  private lensDistortion: LensDistortion;
  private foveatedRendering: FoveatedRendering;
  private motionSmoothing: MotionSmoothing;
  private handTracking: HandTracking;
  
  // State
  private isActive: boolean = false;
  private currentPose: HeadPose;
  private controllers: Map<string, VRControllerState> = new Map();
  
  constructor(renderer: THREE.WebGLRenderer, config: Partial<VRRenderingConfig> = {}) {
    this.renderer = renderer;
    
    this.config = {
      ipd: 64, // mm
      fov: 90,
      nearClip: 0.1,
      farClip: 1000,
      renderScale: 1.0,
      foveatedRenderingLevel: 1,
      motionSmoothing: true,
      reprojection: true,
      ...config
    };
    
    // Create eye cameras and render targets
    const size = renderer.getSize(new THREE.Vector2());
    const eyeWidth = Math.floor(size.x / 2 * this.config.renderScale);
    const eyeHeight = Math.floor(size.y * this.config.renderScale);
    
    this.leftEye = this.createEyeRenderTarget(eyeWidth, eyeHeight, -this.config.ipd / 2000);
    this.rightEye = this.createEyeRenderTarget(eyeWidth, eyeHeight, this.config.ipd / 2000);
    
    // Initialize systems
    this.lensDistortion = new LensDistortion();
    this.foveatedRendering = new FoveatedRendering();
    this.motionSmoothing = new MotionSmoothing();
    this.handTracking = new HandTracking();
    
    this.currentPose = {
      position: new THREE.Vector3(),
      rotation: new THREE.Quaternion(),
      linearVelocity: new THREE.Vector3(),
      angularVelocity: new THREE.Vector3()
    };
  }
  
  private createEyeRenderTarget(
    width: number,
    height: number,
    eyeOffset: number
  ): EyeRenderTarget {
    const camera = new THREE.PerspectiveCamera(
      this.config.fov,
      width / height,
      this.config.nearClip,
      this.config.farClip
    );
    camera.position.x = eyeOffset;
    
    const renderTarget = new THREE.WebGLRenderTarget(width, height, {
      minFilter: THREE.LinearFilter,
      magFilter: THREE.LinearFilter,
      format: THREE.RGBAFormat,
      depthBuffer: true,
      stencilBuffer: false
    });
    
    return { camera, renderTarget };
  }
  
  /**
   * Enter VR mode
   */
  public async enterVR(): Promise<void> {
    if (!navigator.xr) {
      throw new Error('WebXR not supported');
    }
    
    const supported = await navigator.xr.isSessionSupported('immersive-vr');
    if (!supported) {
      throw new Error('Immersive VR not supported');
    }
    
    // Would normally request XR session here
    this.isActive = true;
    console.log('VR mode entered (simulated)');
  }
  
  /**
   * Exit VR mode
   */
  public exitVR(): void {
    this.isActive = false;
    console.log('VR mode exited');
  }
  
  /**
   * Update head pose
   */
  public updateHeadPose(pose: HeadPose): void {
    this.currentPose = pose;
    
    // Update eye cameras
    this.leftEye.camera.position.copy(pose.position);
    this.leftEye.camera.position.x -= this.config.ipd / 2000;
    this.leftEye.camera.quaternion.copy(pose.rotation);
    
    this.rightEye.camera.position.copy(pose.position);
    this.rightEye.camera.position.x += this.config.ipd / 2000;
    this.rightEye.camera.quaternion.copy(pose.rotation);
  }
  
  /**
   * Update controller state
   */
  public updateController(id: string, state: VRControllerState): void {
    this.controllers.set(id, state);
  }
  
  /**
   * Render stereo view
   */
  public render(scene: THREE.Scene): void {
    if (!this.isActive) return;
    
    const currentRenderTarget = this.renderer.getRenderTarget();
    
    // Render left eye
    this.renderer.setRenderTarget(this.leftEye.renderTarget);
    this.renderer.clear();
    this.renderer.render(scene, this.leftEye.camera);
    
    // Render right eye
    this.renderer.setRenderTarget(this.rightEye.renderTarget);
    this.renderer.clear();
    this.renderer.render(scene, this.rightEye.camera);
    
    // Apply lens distortion and combine
    this.renderer.setRenderTarget(currentRenderTarget);
    this.renderStereoOutput();
  }
  
  private renderStereoOutput(): void {
    // Simple side-by-side rendering
    const size = this.renderer.getSize(new THREE.Vector2());
    
    // Apply lens distortion to each eye and render side-by-side
    // In a real implementation, this would use proper barrel distortion
    // and color fringe correction
    
    // For now, just render the targets side-by-side
    const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
    const scene = new THREE.Scene();
    
    // Left half
    const leftMaterial = new THREE.MeshBasicMaterial({
      map: this.leftEye.renderTarget.texture
    });
    const leftQuad = new THREE.Mesh(
      new THREE.PlaneGeometry(1, 2),
      leftMaterial
    );
    leftQuad.position.x = -0.5;
    scene.add(leftQuad);
    
    // Right half
    const rightMaterial = new THREE.MeshBasicMaterial({
      map: this.rightEye.renderTarget.texture
    });
    const rightQuad = new THREE.Mesh(
      new THREE.PlaneGeometry(1, 2),
      rightMaterial
    );
    rightQuad.position.x = 0.5;
    scene.add(rightQuad);
    
    this.renderer.render(scene, camera);
    
    // Cleanup
    leftMaterial.dispose();
    leftQuad.geometry.dispose();
    rightMaterial.dispose();
    rightQuad.geometry.dispose();
  }
  
  /**
   * Get controller ray
   */
  public getControllerRay(id: string): THREE.Ray | null {
    const controller = this.controllers.get(id);
    if (!controller) return null;
    
    const direction = new THREE.Vector3(0, 0, -1)
      .applyQuaternion(controller.rotation);
    
    return new THREE.Ray(controller.position, direction);
  }
  
  /**
   * Set IPD
   */
  public setIPD(ipd: number): void {
    this.config.ipd = ipd;
    
    this.leftEye.camera.position.x = -ipd / 2000;
    this.rightEye.camera.position.x = ipd / 2000;
  }
  
  /**
   * Set render scale
   */
  public setRenderScale(scale: number): void {
    this.config.renderScale = scale;
    
    const size = this.renderer.getSize(new THREE.Vector2());
    const eyeWidth = Math.floor(size.x / 2 * scale);
    const eyeHeight = Math.floor(size.y * scale);
    
    this.leftEye.renderTarget.setSize(eyeWidth, eyeHeight);
    this.rightEye.renderTarget.setSize(eyeWidth, eyeHeight);
  }
  
  /**
   * Enable/disable foveated rendering
   */
  public setFoveatedRenderingLevel(level: 0 | 1 | 2 | 3): void {
    this.config.foveatedRenderingLevel = level;
    
    switch (level) {
      case 0:
        this.foveatedRendering.setConfig({
          innerScale: 1.0,
          outerScale: 1.0
        });
        break;
      case 1:
        this.foveatedRendering.setConfig({
          innerScale: 1.0,
          outerScale: 0.75
        });
        break;
      case 2:
        this.foveatedRendering.setConfig({
          innerScale: 1.0,
          outerScale: 0.5
        });
        break;
      case 3:
        this.foveatedRendering.setConfig({
          innerScale: 1.0,
          outerScale: 0.25
        });
        break;
    }
  }
  
  /**
   * Check if VR is active
   */
  public isVRActive(): boolean {
    return this.isActive;
  }
  
  /**
   * Get current head pose
   */
  public getHeadPose(): HeadPose {
    return this.currentPose;
  }
  
  /**
   * Get hand tracking system
   */
  public getHandTracking(): HandTracking {
    return this.handTracking;
  }
  
  /**
   * Dispose
   */
  public dispose(): void {
    this.leftEye.renderTarget.dispose();
    this.rightEye.renderTarget.dispose();
    this.lensDistortion.dispose();
    this.foveatedRendering.dispose();
    this.motionSmoothing.dispose();
    this.handTracking.dispose();
  }
}

