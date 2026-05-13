/**
 * Buoyancy Physics System
 * Realistic water buoyancy and floating object simulation
 * 
 * Features:
 * - Archimedes principle
 * - Partial submersion
 * - Wave interaction
 * - Drag forces
 * - Angular damping
 * - Multi-hull support
 * - Voxel-based volume calculation
 */

import * as THREE from 'three';

// ============================================
// TYPES
// ============================================

export interface BuoyancyConfig {
  waterDensity: number;       // kg/m³ (1000 for fresh water)
  gravity: number;            // m/s² (9.81)
  linearDrag: number;         // Linear drag coefficient
  angularDrag: number;        // Angular drag coefficient
  waterViscosity: number;     // Water viscosity
  voxelResolution: number;    // Voxels per meter for volume calculation
}

export interface FloatingObject {
  id: string;
  mesh: THREE.Mesh;
  mass: number;               // kg
  volume: number;             // m³
  centerOfMass: THREE.Vector3;
  buoyancyPoints: THREE.Vector3[];  // Sample points for buoyancy
  velocity: THREE.Vector3;
  angularVelocity: THREE.Vector3;
  submergedVolume: number;
  isKinematic: boolean;
}

export interface WaterSurface {
  getHeightAt(x: number, z: number): number;
  getNormalAt(x: number, z: number): THREE.Vector3;
  getVelocityAt(x: number, z: number): THREE.Vector3;
}

// ============================================
// SIMPLE WATER SURFACE
// ============================================

export class SimpleWaterSurface implements WaterSurface {
  private waterLevel: number;
  private waveAmplitude: number;
  private waveFrequency: number;
  private time: number = 0;
  
  constructor(
    waterLevel: number = 0,
    waveAmplitude: number = 0.5,
    waveFrequency: number = 1
  ) {
    this.waterLevel = waterLevel;
    this.waveAmplitude = waveAmplitude;
    this.waveFrequency = waveFrequency;
  }
  
  public update(deltaTime: number): void {
    this.time += deltaTime;
  }
  
  public getHeightAt(x: number, z: number): number {
    const wave1 = Math.sin(x * 0.5 + this.time * this.waveFrequency) * this.waveAmplitude;
    const wave2 = Math.sin(z * 0.3 + this.time * this.waveFrequency * 0.7) * this.waveAmplitude * 0.5;
    const wave3 = Math.sin((x + z) * 0.2 + this.time * this.waveFrequency * 1.3) * this.waveAmplitude * 0.3;
    
    return this.waterLevel + wave1 + wave2 + wave3;
  }
  
  public getNormalAt(x: number, z: number): THREE.Vector3 {
    const delta = 0.1;
    const h = this.getHeightAt(x, z);
    const hx = this.getHeightAt(x + delta, z);
    const hz = this.getHeightAt(x, z + delta);
    
    const dx = (hx - h) / delta;
    const dz = (hz - h) / delta;
    
    return new THREE.Vector3(-dx, 1, -dz).normalize();
  }
  
  public getVelocityAt(x: number, z: number): THREE.Vector3 {
    // Simplified orbital velocity
    const speed = this.waveAmplitude * this.waveFrequency;
    const phase = x * 0.5 + this.time * this.waveFrequency;
    
    return new THREE.Vector3(
      Math.cos(phase) * speed,
      0,
      Math.sin(phase) * speed * 0.5
    );
  }
  
  public setWaterLevel(level: number): void {
    this.waterLevel = level;
  }
}

// ============================================
// BUOYANCY POINT GENERATOR
// ============================================

export class BuoyancyPointGenerator {
  /**
   * Generate buoyancy sample points for a mesh
   */
  public static generatePoints(
    geometry: THREE.BufferGeometry,
    count: number = 8
  ): THREE.Vector3[] {
    const points: THREE.Vector3[] = [];
    
    // Get bounding box
    geometry.computeBoundingBox();
    const bbox = geometry.boundingBox!;
    
    const size = new THREE.Vector3();
    bbox.getSize(size);
    
    const center = new THREE.Vector3();
    bbox.getCenter(center);
    
    // Generate points in a grid pattern
    const gridSize = Math.ceil(Math.cbrt(count));
    
    for (let x = 0; x < gridSize; x++) {
      for (let y = 0; y < gridSize; y++) {
        for (let z = 0; z < gridSize; z++) {
          if (points.length >= count) break;
          
          const point = new THREE.Vector3(
            bbox.min.x + (x + 0.5) * size.x / gridSize,
            bbox.min.y + (y + 0.5) * size.y / gridSize,
            bbox.min.z + (z + 0.5) * size.z / gridSize
          );
          
          points.push(point);
        }
      }
    }
    
    return points;
  }
  
  /**
   * Generate hull points (surface-focused)
   */
  public static generateHullPoints(
    geometry: THREE.BufferGeometry,
    count: number = 16
  ): THREE.Vector3[] {
    const points: THREE.Vector3[] = [];
    const positions = geometry.getAttribute('position');
    
    if (!positions) return points;
    
    // Sample vertices from geometry
    const step = Math.max(1, Math.floor(positions.count / count));
    
    for (let i = 0; i < positions.count && points.length < count; i += step) {
      points.push(new THREE.Vector3(
        positions.getX(i),
        positions.getY(i),
        positions.getZ(i)
      ));
    }
    
    return points;
  }
}

// ============================================
// VOLUME CALCULATOR
// ============================================

export class VolumeCalculator {
  /**
   * Calculate volume of geometry using signed tetrahedron method
   */
  public static calculateVolume(geometry: THREE.BufferGeometry): number {
    const positions = geometry.getAttribute('position');
    const indices = geometry.getIndex();
    
    if (!positions) return 0;
    
    let volume = 0;
    
    const v0 = new THREE.Vector3();
    const v1 = new THREE.Vector3();
    const v2 = new THREE.Vector3();
    
    const triangleCount = indices 
      ? indices.count / 3 
      : positions.count / 3;
    
    for (let i = 0; i < triangleCount; i++) {
      let i0: number, i1: number, i2: number;
      
      if (indices) {
        i0 = indices.getX(i * 3);
        i1 = indices.getX(i * 3 + 1);
        i2 = indices.getX(i * 3 + 2);
      } else {
        i0 = i * 3;
        i1 = i * 3 + 1;
        i2 = i * 3 + 2;
      }
      
      v0.set(positions.getX(i0), positions.getY(i0), positions.getZ(i0));
      v1.set(positions.getX(i1), positions.getY(i1), positions.getZ(i1));
      v2.set(positions.getX(i2), positions.getY(i2), positions.getZ(i2));
      
      // Signed volume of tetrahedron with origin
      volume += v0.dot(v1.clone().cross(v2)) / 6;
    }
    
    return Math.abs(volume);
  }
  
  /**
   * Calculate submerged volume using voxelization
   */
  public static calculateSubmergedVolume(
    mesh: THREE.Mesh,
    waterSurface: WaterSurface,
    voxelSize: number = 0.1
  ): { volume: number; centroid: THREE.Vector3 } {
    const geometry = mesh.geometry;
    geometry.computeBoundingBox();
    const bbox = geometry.boundingBox!.clone();
    
    // Transform bbox to world space
    bbox.applyMatrix4(mesh.matrixWorld);
    
    const size = new THREE.Vector3();
    bbox.getSize(size);
    
    let submergedVolume = 0;
    const centroid = new THREE.Vector3();
    let count = 0;
    
    const voxelVolume = voxelSize * voxelSize * voxelSize;
    
    for (let x = bbox.min.x; x < bbox.max.x; x += voxelSize) {
      for (let y = bbox.min.y; y < bbox.max.y; y += voxelSize) {
        for (let z = bbox.min.z; z < bbox.max.z; z += voxelSize) {
          const waterHeight = waterSurface.getHeightAt(x, z);
          
          if (y < waterHeight) {
            // This voxel is underwater
            const submergedDepth = Math.min(voxelSize, waterHeight - y);
            const volumeContribution = voxelSize * voxelSize * submergedDepth;
            
            submergedVolume += volumeContribution;
            centroid.add(new THREE.Vector3(x, y, z).multiplyScalar(volumeContribution));
            count++;
          }
        }
      }
    }
    
    if (submergedVolume > 0) {
      centroid.divideScalar(submergedVolume);
    }
    
    return { volume: submergedVolume, centroid };
  }
}

// ============================================
// BUOYANCY SYSTEM
// ============================================

export class BuoyancySystem {
  private config: BuoyancyConfig;
  private objects: Map<string, FloatingObject> = new Map();
  private waterSurface: WaterSurface;
  
  constructor(waterSurface: WaterSurface, config: Partial<BuoyancyConfig> = {}) {
    this.waterSurface = waterSurface;
    
    this.config = {
      waterDensity: 1000,      // Fresh water
      gravity: 9.81,
      linearDrag: 0.5,
      angularDrag: 1.0,
      waterViscosity: 0.001,
      voxelResolution: 10,
      ...config
    };
  }
  
  /**
   * Add floating object
   */
  public addObject(
    id: string,
    mesh: THREE.Mesh,
    mass: number,
    buoyancyPointCount: number = 8
  ): FloatingObject {
    const geometry = mesh.geometry;
    geometry.computeBoundingBox();
    
    // Calculate volume
    const volume = VolumeCalculator.calculateVolume(geometry);
    
    // Generate buoyancy sample points
    const buoyancyPoints = BuoyancyPointGenerator.generatePoints(geometry, buoyancyPointCount);
    
    // Calculate center of mass (assume uniform density)
    const centerOfMass = new THREE.Vector3();
    geometry.boundingBox!.getCenter(centerOfMass);
    
    const obj: FloatingObject = {
      id,
      mesh,
      mass,
      volume,
      centerOfMass,
      buoyancyPoints,
      velocity: new THREE.Vector3(),
      angularVelocity: new THREE.Vector3(),
      submergedVolume: 0,
      isKinematic: false
    };
    
    this.objects.set(id, obj);
    return obj;
  }
  
  /**
   * Remove object
   */
  public removeObject(id: string): void {
    this.objects.delete(id);
  }
  
  /**
   * Update physics
   */
  public update(deltaTime: number): void {
    for (const obj of this.objects.values()) {
      if (obj.isKinematic) continue;
      
      this.updateObject(obj, deltaTime);
    }
  }
  
  private updateObject(obj: FloatingObject, dt: number): void {
    const mesh = obj.mesh;
    mesh.updateMatrixWorld(true);
    
    // Forces
    const totalForce = new THREE.Vector3();
    const totalTorque = new THREE.Vector3();
    
    // Gravity
    const gravity = new THREE.Vector3(0, -this.config.gravity * obj.mass, 0);
    totalForce.add(gravity);
    
    // Calculate buoyancy at each sample point
    let submergedVolume = 0;
    const submergedCenter = new THREE.Vector3();
    let submergedCount = 0;
    
    const pointVolume = obj.volume / obj.buoyancyPoints.length;
    
    for (const localPoint of obj.buoyancyPoints) {
      // Transform point to world space
      const worldPoint = localPoint.clone().applyMatrix4(mesh.matrixWorld);
      
      const waterHeight = this.waterSurface.getHeightAt(worldPoint.x, worldPoint.z);
      const depth = waterHeight - worldPoint.y;
      
      if (depth > 0) {
        // Point is underwater
        const submersionRatio = Math.min(1, depth / 0.5); // Smooth transition
        const pointSubmergedVolume = pointVolume * submersionRatio;
        
        // Buoyancy force (Archimedes principle)
        const buoyancyMagnitude = this.config.waterDensity * 
                                   this.config.gravity * 
                                   pointSubmergedVolume;
        
        const waterNormal = this.waterSurface.getNormalAt(worldPoint.x, worldPoint.z);
        const buoyancyForce = waterNormal.multiplyScalar(buoyancyMagnitude);
        
        totalForce.add(buoyancyForce);
        
        // Torque from buoyancy
        const r = worldPoint.clone().sub(mesh.position);
        const torque = r.clone().cross(buoyancyForce);
        totalTorque.add(torque);
        
        submergedVolume += pointSubmergedVolume;
        submergedCenter.add(worldPoint.multiplyScalar(pointSubmergedVolume));
        submergedCount++;
      }
    }
    
    obj.submergedVolume = submergedVolume;
    
    if (submergedVolume > 0) {
      submergedCenter.divideScalar(submergedVolume);
      
      // Drag forces
      const waterVelocity = this.waterSurface.getVelocityAt(
        mesh.position.x, 
        mesh.position.z
      );
      const relativeVelocity = obj.velocity.clone().sub(waterVelocity);
      
      // Linear drag
      const dragArea = Math.pow(submergedVolume, 2/3); // Approximate cross-section
      const dragMagnitude = 0.5 * this.config.waterDensity * 
                            this.config.linearDrag * 
                            dragArea * 
                            relativeVelocity.lengthSq();
      
      if (dragMagnitude > 0) {
        const dragForce = relativeVelocity.clone()
          .normalize()
          .multiplyScalar(-dragMagnitude);
        totalForce.add(dragForce);
      }
      
      // Angular drag
      const angularDragMagnitude = this.config.angularDrag * 
                                    submergedVolume * 
                                    obj.angularVelocity.lengthSq();
      
      if (angularDragMagnitude > 0) {
        const angularDrag = obj.angularVelocity.clone()
          .normalize()
          .multiplyScalar(-angularDragMagnitude);
        totalTorque.add(angularDrag);
      }
    }
    
    // Apply forces
    const acceleration = totalForce.divideScalar(obj.mass);
    obj.velocity.add(acceleration.multiplyScalar(dt));
    
    // Apply torque (simplified - assumes sphere for moment of inertia)
    const momentOfInertia = 0.4 * obj.mass * Math.pow(obj.volume, 2/3);
    const angularAcceleration = totalTorque.divideScalar(momentOfInertia);
    obj.angularVelocity.add(angularAcceleration.multiplyScalar(dt));
    
    // Update position
    mesh.position.add(obj.velocity.clone().multiplyScalar(dt));
    
    // Update rotation
    const rotationAxis = obj.angularVelocity.clone().normalize();
    const rotationAngle = obj.angularVelocity.length() * dt;
    
    if (rotationAngle > 0.0001) {
      const deltaRotation = new THREE.Quaternion()
        .setFromAxisAngle(rotationAxis, rotationAngle);
      mesh.quaternion.premultiply(deltaRotation);
    }
    
    // Damping
    obj.velocity.multiplyScalar(0.999);
    obj.angularVelocity.multiplyScalar(0.99);
  }
  
  /**
   * Get object by ID
   */
  public getObject(id: string): FloatingObject | undefined {
    return this.objects.get(id);
  }
  
  /**
   * Get all objects
   */
  public getObjects(): FloatingObject[] {
    return Array.from(this.objects.values());
  }
  
  /**
   * Set water surface
   */
  public setWaterSurface(surface: WaterSurface): void {
    this.waterSurface = surface;
  }
  
  /**
   * Check if point is underwater
   */
  public isUnderwater(point: THREE.Vector3): boolean {
    const waterHeight = this.waterSurface.getHeightAt(point.x, point.z);
    return point.y < waterHeight;
  }
  
  /**
   * Get water height at position
   */
  public getWaterHeight(x: number, z: number): number {
    return this.waterSurface.getHeightAt(x, z);
  }
  
  /**
   * Dispose
   */
  public dispose(): void {
    this.objects.clear();
  }
}

