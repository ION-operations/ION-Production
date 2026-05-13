/**
 * LOD (Level of Detail) Manager
 * Automatic mesh quality switching based on distance/importance
 * 
 * Features:
 * - Distance-based LOD
 * - Screen-space size LOD
 * - Cross-fade transitions
 * - Billboard imposters
 * - Hierarchical LOD groups
 */

import * as THREE from 'three';

export interface LODLevel {
  distance: number;           // Distance threshold
  mesh: THREE.Mesh | THREE.Object3D;
  screenCoverage?: number;    // Optional screen-space threshold
}

export interface LODConfig {
  bias: number;               // Global LOD bias (lower = higher quality)
  transitionTime: number;     // Cross-fade duration (0 = instant)
  updateFrequency: number;    // Update every N frames
  useScreenCoverage: boolean; // Use screen-space size instead of distance
  hysteresis: number;         // Prevent LOD popping (0.1 = 10% margin)
}

export const DEFAULT_LOD_CONFIG: LODConfig = {
  bias: 1.0,
  transitionTime: 0.3,
  updateFrequency: 1,
  useScreenCoverage: false,
  hysteresis: 0.1
};

interface LODObject {
  levels: LODLevel[];
  currentLevel: number;
  targetLevel: number;
  transitionProgress: number;
  group: THREE.Group;
  bounds: THREE.Sphere;
  lastDistance: number;
}

export class LODManager {
  private config: LODConfig;
  private objects: Map<string, LODObject> = new Map();
  private camera: THREE.Camera | null = null;
  private frameCount: number = 0;
  
  // Stats
  public stats = {
    totalObjects: 0,
    visibleObjects: 0,
    lodSwitches: 0,
    trianglesRendered: 0
  };

  constructor(config: Partial<LODConfig> = {}) {
    this.config = { ...DEFAULT_LOD_CONFIG, ...config };
  }

  /**
   * Set camera for distance calculations
   */
  public setCamera(camera: THREE.Camera): void {
    this.camera = camera;
  }

  /**
   * Register object with LOD levels
   */
  public register(
    id: string,
    levels: LODLevel[],
    position: THREE.Vector3,
    boundingSphere?: THREE.Sphere
  ): THREE.Group {
    // Sort levels by distance
    levels.sort((a, b) => a.distance - b.distance);
    
    // Create group
    const group = new THREE.Group();
    group.position.copy(position);
    
    // Add all levels but hide all except first
    for (let i = 0; i < levels.length; i++) {
      const level = levels[i];
      level.mesh.visible = i === 0;
      
      if (level.mesh instanceof THREE.Mesh) {
        (level.mesh.material as THREE.Material).transparent = true;
      }
      
      group.add(level.mesh);
    }
    
    // Calculate bounds
    const bounds = boundingSphere || new THREE.Sphere();
    if (!boundingSphere && levels[0].mesh instanceof THREE.Mesh) {
      levels[0].mesh.geometry.computeBoundingSphere();
      if (levels[0].mesh.geometry.boundingSphere) {
        bounds.copy(levels[0].mesh.geometry.boundingSphere);
      }
    }
    
    this.objects.set(id, {
      levels,
      currentLevel: 0,
      targetLevel: 0,
      transitionProgress: 1,
      group,
      bounds,
      lastDistance: 0
    });
    
    this.stats.totalObjects++;
    
    return group;
  }

  /**
   * Unregister object
   */
  public unregister(id: string): void {
    const obj = this.objects.get(id);
    if (obj) {
      for (const level of obj.levels) {
        if (level.mesh instanceof THREE.Mesh) {
          level.mesh.geometry.dispose();
          (level.mesh.material as THREE.Material).dispose();
        }
      }
      this.objects.delete(id);
      this.stats.totalObjects--;
    }
  }

  /**
   * Update LOD states
   */
  public update(dt: number): void {
    if (!this.camera) return;
    
    this.frameCount++;
    if (this.frameCount % this.config.updateFrequency !== 0) return;
    
    this.stats.visibleObjects = 0;
    this.stats.trianglesRendered = 0;
    
    const cameraPos = this.camera.position;
    
    for (const [id, obj] of this.objects) {
      // Calculate distance
      const worldPos = obj.group.getWorldPosition(new THREE.Vector3());
      const distance = worldPos.distanceTo(cameraPos) * this.config.bias;
      
      // Add hysteresis
      const hysteresisMargin = obj.lastDistance * this.config.hysteresis;
      
      // Determine target LOD level
      let targetLevel = obj.levels.length - 1;
      
      if (this.config.useScreenCoverage) {
        // Screen-space size calculation
        const screenSize = this.calculateScreenCoverage(obj, worldPos);
        
        for (let i = 0; i < obj.levels.length; i++) {
          if (obj.levels[i].screenCoverage && screenSize >= obj.levels[i].screenCoverage!) {
            targetLevel = i;
            break;
          }
        }
      } else {
        // Distance-based
        for (let i = 0; i < obj.levels.length; i++) {
          const threshold = obj.levels[i].distance;
          const adjustedThreshold = (i > obj.currentLevel)
            ? threshold + hysteresisMargin
            : threshold - hysteresisMargin;
          
          if (distance <= adjustedThreshold) {
            targetLevel = i;
            break;
          }
        }
      }
      
      obj.lastDistance = distance;
      
      // Handle LOD transition
      if (targetLevel !== obj.targetLevel) {
        obj.targetLevel = targetLevel;
        obj.transitionProgress = 0;
        this.stats.lodSwitches++;
      }
      
      // Update transition
      if (obj.transitionProgress < 1) {
        obj.transitionProgress += dt / this.config.transitionTime;
        
        if (obj.transitionProgress >= 1) {
          obj.transitionProgress = 1;
          obj.currentLevel = obj.targetLevel;
        }
        
        this.updateLevelVisibility(obj);
      }
      
      // Count visible objects and triangles
      if (obj.group.visible) {
        this.stats.visibleObjects++;
        
        const mesh = obj.levels[obj.currentLevel].mesh;
        if (mesh instanceof THREE.Mesh && mesh.geometry.index) {
          this.stats.trianglesRendered += mesh.geometry.index.count / 3;
        }
      }
    }
  }

  private calculateScreenCoverage(obj: LODObject, worldPos: THREE.Vector3): number {
    if (!this.camera || !(this.camera instanceof THREE.PerspectiveCamera)) return 0;
    
    const distance = worldPos.distanceTo(this.camera.position);
    const fov = THREE.MathUtils.degToRad(this.camera.fov);
    const screenHeight = 2 * distance * Math.tan(fov / 2);
    
    return (obj.bounds.radius * 2) / screenHeight;
  }

  private updateLevelVisibility(obj: LODObject): void {
    const { currentLevel, targetLevel, transitionProgress, levels } = obj;
    
    if (this.config.transitionTime === 0 || currentLevel === targetLevel) {
      // Instant switch
      for (let i = 0; i < levels.length; i++) {
        levels[i].mesh.visible = i === targetLevel;
        
        if (levels[i].mesh instanceof THREE.Mesh) {
          (levels[i].mesh.material as THREE.Material).opacity = 1;
        }
      }
    } else {
      // Cross-fade
      for (let i = 0; i < levels.length; i++) {
        if (i === currentLevel) {
          levels[i].mesh.visible = true;
          if (levels[i].mesh instanceof THREE.Mesh) {
            (levels[i].mesh.material as THREE.Material).opacity = 1 - transitionProgress;
          }
        } else if (i === targetLevel) {
          levels[i].mesh.visible = true;
          if (levels[i].mesh instanceof THREE.Mesh) {
            (levels[i].mesh.material as THREE.Material).opacity = transitionProgress;
          }
        } else {
          levels[i].mesh.visible = false;
        }
      }
    }
  }

  /**
   * Force specific LOD level for object
   */
  public setLODLevel(id: string, level: number): void {
    const obj = this.objects.get(id);
    if (obj && level >= 0 && level < obj.levels.length) {
      obj.currentLevel = level;
      obj.targetLevel = level;
      obj.transitionProgress = 1;
      this.updateLevelVisibility(obj);
    }
  }

  /**
   * Get current LOD level for object
   */
  public getLODLevel(id: string): number {
    const obj = this.objects.get(id);
    return obj ? obj.currentLevel : -1;
  }

  /**
   * Set global LOD bias
   */
  public setBias(bias: number): void {
    this.config.bias = bias;
  }

  public getStats(): typeof this.stats {
    return { ...this.stats };
  }

  public dispose(): void {
    for (const id of this.objects.keys()) {
      this.unregister(id);
    }
  }
}

/**
 * Billboard Imposter Generator
 * Creates billboard LOD from 3D mesh
 */
export class ImposterGenerator {
  private renderer: THREE.WebGLRenderer;
  private scene: THREE.Scene;
  private camera: THREE.OrthographicCamera;
  private renderTarget: THREE.WebGLRenderTarget;

  constructor(renderer: THREE.WebGLRenderer, resolution: number = 256) {
    this.renderer = renderer;
    this.scene = new THREE.Scene();
    this.camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.1, 100);
    this.renderTarget = new THREE.WebGLRenderTarget(resolution, resolution, {
      format: THREE.RGBAFormat,
      type: THREE.UnsignedByteType
    });
  }

  /**
   * Generate billboard imposter from mesh
   */
  public generate(mesh: THREE.Mesh, viewAngles: number = 8): {
    texture: THREE.Texture;
    geometry: THREE.PlaneGeometry;
    material: THREE.ShaderMaterial;
  } {
    // Calculate bounding sphere
    mesh.geometry.computeBoundingSphere();
    const bounds = mesh.geometry.boundingSphere!;
    const size = bounds.radius * 2;
    
    // Set up camera
    this.camera.left = -size / 2;
    this.camera.right = size / 2;
    this.camera.top = size / 2;
    this.camera.bottom = -size / 2;
    this.camera.updateProjectionMatrix();
    
    // Render from front
    this.scene.add(mesh);
    mesh.position.set(0, 0, 0);
    this.camera.position.set(0, 0, size);
    this.camera.lookAt(0, 0, 0);
    
    this.renderer.setRenderTarget(this.renderTarget);
    this.renderer.render(this.scene, this.camera);
    this.renderer.setRenderTarget(null);
    
    this.scene.remove(mesh);
    
    // Create billboard
    const texture = this.renderTarget.texture.clone();
    texture.needsUpdate = true;
    
    const geometry = new THREE.PlaneGeometry(size, size);
    
    const material = new THREE.ShaderMaterial({
      uniforms: {
        tImposter: { value: texture },
        uCameraPosition: { value: new THREE.Vector3() }
      },
      vertexShader: `
        uniform vec3 uCameraPosition;
        varying vec2 vUv;
        
        void main() {
          vUv = uv;
          
          // Billboard: always face camera
          vec3 look = normalize(uCameraPosition - position);
          vec3 right = normalize(cross(vec3(0.0, 1.0, 0.0), look));
          vec3 up = cross(look, right);
          
          vec3 billboardPos = position.x * right + position.y * up;
          
          gl_Position = projectionMatrix * modelViewMatrix * vec4(billboardPos, 1.0);
        }
      `,
      fragmentShader: `
        uniform sampler2D tImposter;
        varying vec2 vUv;
        
        void main() {
          vec4 color = texture2D(tImposter, vUv);
          if (color.a < 0.1) discard;
          gl_FragColor = color;
        }
      `,
      transparent: true,
      side: THREE.DoubleSide
    });
    
    return { texture, geometry, material };
  }

  public dispose(): void {
    this.renderTarget.dispose();
  }
}

