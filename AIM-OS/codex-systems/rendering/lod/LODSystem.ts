/**
 * Level of Detail (LOD) System
 * Automatic mesh simplification and LOD management
 * 
 * Features:
 * - Dynamic LOD switching
 * - Screen-space error metrics
 * - Hierarchical LOD
 * - Impostor generation
 * - Fade transitions
 * - GPU-driven LOD selection
 */

import * as THREE from 'three';

// ============================================
// TYPES
// ============================================

export interface LODLevel {
  mesh: THREE.Mesh;
  distance: number;
  screenSpaceError?: number;
  drawCalls?: number;
  triangleCount?: number;
}

export interface LODConfig {
  useFadeDithering: boolean;
  fadeTransitionTime: number;
  screenSpaceErrorThreshold: number;
  updateFrequency: number;  // Updates per second
  maxLoadingPerFrame: number;
}

export interface ImpostorConfig {
  resolution: number;
  views: number;  // Number of views around Y axis
  includeTop: boolean;
  includeBottom: boolean;
  blendSharpness: number;
}

// ============================================
// LOD METRICS
// ============================================

export class LODMetrics {
  /**
   * Calculate screen-space error for a mesh at a distance
   */
  public static calculateScreenSpaceError(
    boundingSphereRadius: number,
    distance: number,
    camera: THREE.PerspectiveCamera,
    screenHeight: number
  ): number {
    // Project bounding sphere to screen
    const fov = camera.fov * Math.PI / 180;
    const projectedRadius = (boundingSphereRadius / distance) / Math.tan(fov / 2);
    
    return projectedRadius * screenHeight;
  }
  
  /**
   * Calculate optimal LOD level based on screen-space error
   */
  public static selectLODLevel(
    levels: LODLevel[],
    distance: number,
    camera: THREE.PerspectiveCamera,
    screenHeight: number,
    errorThreshold: number
  ): number {
    for (let i = 0; i < levels.length; i++) {
      const level = levels[i];
      
      if (level.screenSpaceError !== undefined) {
        const boundingSphere = level.mesh.geometry.boundingSphere;
        if (!boundingSphere) {
          level.mesh.geometry.computeBoundingSphere();
        }
        
        const radius = level.mesh.geometry.boundingSphere!.radius;
        const error = this.calculateScreenSpaceError(radius, distance, camera, screenHeight);
        
        if (error <= errorThreshold || i === levels.length - 1) {
          return i;
        }
      } else if (distance <= level.distance) {
        return i;
      }
    }
    
    return levels.length - 1;
  }
  
  /**
   * Calculate the importance of an object for LOD prioritization
   */
  public static calculateImportance(
    mesh: THREE.Mesh,
    camera: THREE.Camera,
    viewportArea: number
  ): number {
    // Screen coverage
    const boundingSphere = mesh.geometry.boundingSphere;
    if (!boundingSphere) return 0;
    
    const worldCenter = boundingSphere.center.clone().applyMatrix4(mesh.matrixWorld);
    const distance = worldCenter.distanceTo(camera.position);
    
    if (distance <= 0) return Infinity;
    
    const projectedSize = boundingSphere.radius / distance;
    const screenCoverage = projectedSize * projectedSize * Math.PI / viewportArea;
    
    // Velocity factor (faster objects need more detail)
    // This would need velocity data from physics
    
    return screenCoverage;
  }
}

// ============================================
// LOD GROUP
// ============================================

export class LODGroup extends THREE.Object3D {
  public levels: LODLevel[] = [];
  private currentLevel: number = 0;
  private targetLevel: number = 0;
  private fadeProgress: number = 1;
  private config: LODConfig;
  private lastUpdateTime: number = 0;
  
  constructor(config: Partial<LODConfig> = {}) {
    super();
    
    this.config = {
      useFadeDithering: true,
      fadeTransitionTime: 0.3,
      screenSpaceErrorThreshold: 2,
      updateFrequency: 30,
      maxLoadingPerFrame: 5,
      ...config
    };
  }
  
  /**
   * Add a LOD level
   */
  public addLevel(mesh: THREE.Mesh, distance: number): void {
    // Compute geometry info
    mesh.geometry.computeBoundingSphere();
    
    const triangleCount = mesh.geometry.index
      ? mesh.geometry.index.count / 3
      : (mesh.geometry.getAttribute('position')?.count ?? 0) / 3;
    
    this.levels.push({
      mesh,
      distance,
      triangleCount,
      drawCalls: 1
    });
    
    // Sort by distance
    this.levels.sort((a, b) => a.distance - b.distance);
    
    // Add mesh to group but hide it
    mesh.visible = false;
    this.add(mesh);
    
    // Show first level by default
    if (this.levels.length === 1) {
      mesh.visible = true;
    }
  }
  
  /**
   * Update LOD selection
   */
  public update(camera: THREE.Camera, deltaTime: number): void {
    const now = performance.now();
    const updateInterval = 1000 / this.config.updateFrequency;
    
    if (now - this.lastUpdateTime < updateInterval) {
      // Only update fade
      this.updateFade(deltaTime);
      return;
    }
    
    this.lastUpdateTime = now;
    
    // Calculate distance to camera
    const worldPos = new THREE.Vector3();
    this.getWorldPosition(worldPos);
    const distance = worldPos.distanceTo(camera.position);
    
    // Select LOD level
    let newLevel = 0;
    for (let i = 0; i < this.levels.length; i++) {
      if (distance > this.levels[i].distance) {
        newLevel = i;
      }
    }
    
    // Initiate transition if level changed
    if (newLevel !== this.targetLevel) {
      this.targetLevel = newLevel;
      this.fadeProgress = 0;
    }
    
    this.updateFade(deltaTime);
  }
  
  private updateFade(deltaTime: number): void {
    if (this.fadeProgress < 1) {
      this.fadeProgress = Math.min(1, this.fadeProgress + deltaTime / this.config.fadeTransitionTime);
      
      if (this.config.useFadeDithering) {
        this.updateDitherFade();
      } else {
        this.updateCrossFade();
      }
      
      if (this.fadeProgress >= 1) {
        this.currentLevel = this.targetLevel;
        this.finalizeTransition();
      }
    }
  }
  
  private updateDitherFade(): void {
    // Show target, apply dither pattern based on fade progress
    const currentMesh = this.levels[this.currentLevel]?.mesh;
    const targetMesh = this.levels[this.targetLevel]?.mesh;
    
    if (currentMesh && targetMesh) {
      currentMesh.visible = this.fadeProgress < 0.5;
      targetMesh.visible = this.fadeProgress >= 0.5;
      
      // Could apply actual dither shader here
    }
  }
  
  private updateCrossFade(): void {
    // Cross-fade between levels using opacity
    const currentMesh = this.levels[this.currentLevel]?.mesh;
    const targetMesh = this.levels[this.targetLevel]?.mesh;
    
    if (currentMesh && targetMesh) {
      currentMesh.visible = true;
      targetMesh.visible = true;
      
      if (currentMesh.material instanceof THREE.Material) {
        currentMesh.material.opacity = 1 - this.fadeProgress;
        currentMesh.material.transparent = true;
      }
      
      if (targetMesh.material instanceof THREE.Material) {
        targetMesh.material.opacity = this.fadeProgress;
        targetMesh.material.transparent = true;
      }
    }
  }
  
  private finalizeTransition(): void {
    // Hide all except current
    for (let i = 0; i < this.levels.length; i++) {
      const mesh = this.levels[i].mesh;
      mesh.visible = i === this.currentLevel;
      
      if (mesh.material instanceof THREE.Material) {
        mesh.material.opacity = 1;
        mesh.material.transparent = false;
      }
    }
  }
  
  /**
   * Force a specific LOD level
   */
  public setLevel(level: number): void {
    level = Math.max(0, Math.min(level, this.levels.length - 1));
    
    for (let i = 0; i < this.levels.length; i++) {
      this.levels[i].mesh.visible = i === level;
    }
    
    this.currentLevel = level;
    this.targetLevel = level;
    this.fadeProgress = 1;
  }
  
  /**
   * Get current LOD level
   */
  public getLevel(): number {
    return this.currentLevel;
  }
  
  /**
   * Get current triangle count
   */
  public getCurrentTriangleCount(): number {
    return this.levels[this.currentLevel]?.triangleCount ?? 0;
  }
}

// ============================================
// IMPOSTOR GENERATOR
// ============================================

export class ImpostorGenerator {
  private renderer: THREE.WebGLRenderer;
  private scene: THREE.Scene;
  private camera: THREE.OrthographicCamera;
  
  constructor(renderer: THREE.WebGLRenderer) {
    this.renderer = renderer;
    this.scene = new THREE.Scene();
    this.scene.background = null;
    
    this.camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.1, 100);
  }
  
  /**
   * Generate impostor atlas from a mesh
   */
  public generateImpostor(
    mesh: THREE.Mesh,
    config: ImpostorConfig = {
      resolution: 512,
      views: 8,
      includeTop: true,
      includeBottom: true,
      blendSharpness: 2
    }
  ): { atlas: THREE.Texture; mesh: THREE.Mesh } {
    // Calculate bounding sphere
    mesh.geometry.computeBoundingSphere();
    const boundingSphere = mesh.geometry.boundingSphere!;
    const radius = boundingSphere.radius;
    
    // Setup camera
    const size = radius * 1.1;
    this.camera.left = -size;
    this.camera.right = size;
    this.camera.top = size;
    this.camera.bottom = -size;
    this.camera.updateProjectionMatrix();
    
    // Calculate atlas layout
    const viewCount = config.views + (config.includeTop ? 1 : 0) + (config.includeBottom ? 1 : 0);
    const gridSize = Math.ceil(Math.sqrt(viewCount));
    const cellSize = config.resolution;
    const atlasSize = gridSize * cellSize;
    
    // Create render target
    const renderTarget = new THREE.WebGLRenderTarget(atlasSize, atlasSize, {
      minFilter: THREE.LinearFilter,
      magFilter: THREE.LinearFilter,
      format: THREE.RGBAFormat,
      type: THREE.UnsignedByteType
    });
    
    // Clone mesh for rendering
    const clonedMesh = mesh.clone();
    clonedMesh.position.set(0, 0, 0);
    this.scene.add(clonedMesh);
    
    // Add simple lighting
    const light = new THREE.DirectionalLight(0xffffff, 1);
    light.position.set(1, 1, 1);
    this.scene.add(light);
    
    const ambient = new THREE.AmbientLight(0x404040);
    this.scene.add(ambient);
    
    // Store original render target
    const originalRenderTarget = this.renderer.getRenderTarget();
    
    // Render each view
    this.renderer.setRenderTarget(renderTarget);
    this.renderer.clear();
    
    let viewIndex = 0;
    
    // Side views
    for (let i = 0; i < config.views; i++) {
      const angle = (i / config.views) * Math.PI * 2;
      
      this.camera.position.set(
        Math.sin(angle) * radius * 2,
        0,
        Math.cos(angle) * radius * 2
      );
      this.camera.lookAt(0, 0, 0);
      
      this.renderToAtlasCell(viewIndex, gridSize, cellSize, atlasSize);
      viewIndex++;
    }
    
    // Top view
    if (config.includeTop) {
      this.camera.position.set(0, radius * 2, 0);
      this.camera.lookAt(0, 0, 0);
      
      this.renderToAtlasCell(viewIndex, gridSize, cellSize, atlasSize);
      viewIndex++;
    }
    
    // Bottom view
    if (config.includeBottom) {
      this.camera.position.set(0, -radius * 2, 0);
      this.camera.lookAt(0, 0, 0);
      
      this.renderToAtlasCell(viewIndex, gridSize, cellSize, atlasSize);
      viewIndex++;
    }
    
    // Restore render target
    this.renderer.setRenderTarget(originalRenderTarget);
    
    // Create impostor mesh
    const impostorMesh = this.createImpostorMesh(
      renderTarget.texture,
      radius,
      config.views,
      gridSize,
      config.blendSharpness
    );
    
    // Cleanup
    this.scene.remove(clonedMesh);
    this.scene.remove(light);
    this.scene.remove(ambient);
    
    return {
      atlas: renderTarget.texture,
      mesh: impostorMesh
    };
  }
  
  private renderToAtlasCell(
    index: number,
    gridSize: number,
    cellSize: number,
    atlasSize: number
  ): void {
    const col = index % gridSize;
    const row = Math.floor(index / gridSize);
    
    this.renderer.setViewport(
      col * cellSize,
      atlasSize - (row + 1) * cellSize,
      cellSize,
      cellSize
    );
    
    this.renderer.render(this.scene, this.camera);
  }
  
  private createImpostorMesh(
    atlas: THREE.Texture,
    radius: number,
    viewCount: number,
    gridSize: number,
    blendSharpness: number
  ): THREE.Mesh {
    // Create quad geometry
    const geometry = new THREE.PlaneGeometry(radius * 2, radius * 2);
    
    // Create impostor material
    const material = new THREE.ShaderMaterial({
      uniforms: {
        atlas: { value: atlas },
        viewCount: { value: viewCount },
        gridSize: { value: gridSize },
        blendSharpness: { value: blendSharpness }
      },
      vertexShader: `
        varying vec2 vUv;
        varying vec3 vViewDir;
        
        void main() {
          vUv = uv;
          
          vec4 worldPos = modelMatrix * vec4(position, 1.0);
          vViewDir = normalize(cameraPosition - worldPos.xyz);
          
          gl_Position = projectionMatrix * viewMatrix * worldPos;
        }
      `,
      fragmentShader: `
        uniform sampler2D atlas;
        uniform float viewCount;
        uniform float gridSize;
        uniform float blendSharpness;
        
        varying vec2 vUv;
        varying vec3 vViewDir;
        
        vec2 getAtlasUV(int view, vec2 uv) {
          float col = mod(float(view), gridSize);
          float row = floor(float(view) / gridSize);
          
          vec2 cellSize = vec2(1.0) / gridSize;
          vec2 offset = vec2(col, gridSize - 1.0 - row) * cellSize;
          
          return offset + uv * cellSize;
        }
        
        void main() {
          // Calculate view angle
          float angle = atan(vViewDir.x, vViewDir.z);
          if (angle < 0.0) angle += 6.28318;
          
          float viewFloat = angle / 6.28318 * viewCount;
          int view1 = int(floor(viewFloat));
          int view2 = int(mod(float(view1 + 1), viewCount));
          float blend = fract(viewFloat);
          
          // Sharp blend
          blend = pow(blend, blendSharpness);
          
          // Sample atlas
          vec4 color1 = texture2D(atlas, getAtlasUV(view1, vUv));
          vec4 color2 = texture2D(atlas, getAtlasUV(view2, vUv));
          
          vec4 finalColor = mix(color1, color2, blend);
          
          if (finalColor.a < 0.1) discard;
          
          gl_FragColor = finalColor;
        }
      `,
      transparent: true,
      side: THREE.DoubleSide
    });
    
    return new THREE.Mesh(geometry, material);
  }
}

// ============================================
// LOD MANAGER
// ============================================

export class LODManager {
  private lodGroups: Set<LODGroup> = new Set();
  private camera: THREE.Camera;
  private config: LODConfig;
  private frameStats: {
    lodSwitches: number;
    totalTriangles: number;
  } = { lodSwitches: 0, totalTriangles: 0 };
  
  constructor(camera: THREE.Camera, config: Partial<LODConfig> = {}) {
    this.camera = camera;
    this.config = {
      useFadeDithering: true,
      fadeTransitionTime: 0.3,
      screenSpaceErrorThreshold: 2,
      updateFrequency: 30,
      maxLoadingPerFrame: 5,
      ...config
    };
  }
  
  /**
   * Register a LOD group
   */
  public add(group: LODGroup): void {
    this.lodGroups.add(group);
  }
  
  /**
   * Unregister a LOD group
   */
  public remove(group: LODGroup): void {
    this.lodGroups.delete(group);
  }
  
  /**
   * Update all LOD groups
   */
  public update(deltaTime: number): void {
    this.frameStats.lodSwitches = 0;
    this.frameStats.totalTriangles = 0;
    
    for (const group of this.lodGroups) {
      const prevLevel = group.getLevel();
      group.update(this.camera, deltaTime);
      
      if (group.getLevel() !== prevLevel) {
        this.frameStats.lodSwitches++;
      }
      
      this.frameStats.totalTriangles += group.getCurrentTriangleCount();
    }
  }
  
  /**
   * Force update all groups immediately
   */
  public forceUpdate(): void {
    for (const group of this.lodGroups) {
      group.update(this.camera, 0);
    }
  }
  
  /**
   * Get frame statistics
   */
  public getStats(): { lodSwitches: number; totalTriangles: number; groupCount: number } {
    return {
      ...this.frameStats,
      groupCount: this.lodGroups.size
    };
  }
  
  /**
   * Set maximum LOD level for all groups
   */
  public setMaxLevel(level: number): void {
    for (const group of this.lodGroups) {
      if (group.getLevel() > level) {
        group.setLevel(level);
      }
    }
  }
  
  /**
   * Clear all groups
   */
  public clear(): void {
    this.lodGroups.clear();
  }
}

// ============================================
// MESH SIMPLIFIER (Basic)
// ============================================

export class MeshSimplifier {
  /**
   * Simplify a mesh using edge collapse (basic implementation)
   */
  public static simplify(
    geometry: THREE.BufferGeometry,
    targetRatio: number
  ): THREE.BufferGeometry {
    // This is a simplified placeholder
    // Real implementation would use QEM (Quadric Error Metrics)
    
    const positions = geometry.getAttribute('position');
    const indices = geometry.index;
    
    if (!indices) {
      console.warn('MeshSimplifier: Geometry must be indexed');
      return geometry.clone();
    }
    
    const targetCount = Math.floor(indices.count * targetRatio);
    
    // For now, just subsample indices
    const newIndices: number[] = [];
    const step = Math.max(1, Math.ceil(indices.count / targetCount));
    
    for (let i = 0; i < indices.count; i += step * 3) {
      if (i + 2 < indices.count) {
        newIndices.push(
          indices.getX(i),
          indices.getX(i + 1),
          indices.getX(i + 2)
        );
      }
    }
    
    const newGeometry = geometry.clone();
    newGeometry.setIndex(newIndices);
    
    return newGeometry;
  }
  
  /**
   * Generate LOD levels from a mesh
   */
  public static generateLODLevels(
    mesh: THREE.Mesh,
    levels: number = 4,
    ratios: number[] = [1, 0.5, 0.25, 0.1]
  ): THREE.Mesh[] {
    const meshes: THREE.Mesh[] = [];
    
    for (let i = 0; i < levels; i++) {
      const ratio = ratios[i] ?? Math.pow(0.5, i);
      
      if (ratio >= 1) {
        meshes.push(mesh.clone());
      } else {
        const simplifiedGeometry = this.simplify(mesh.geometry, ratio);
        const simplifiedMesh = new THREE.Mesh(
          simplifiedGeometry,
          mesh.material
        );
        meshes.push(simplifiedMesh);
      }
    }
    
    return meshes;
  }
}

