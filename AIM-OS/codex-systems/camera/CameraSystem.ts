/**
 * Camera System
 * Versatile camera controllers and effects
 * 
 * Features:
 * - Orbit camera
 * - First-person camera
 * - Third-person camera
 * - Cinematic camera (dolly, crane, follow)
 * - Camera shake
 * - Smooth transitions
 */

import * as THREE from 'three';

// ============================================
// BASE CAMERA CONTROLLER
// ============================================

export abstract class CameraController {
  protected camera: THREE.PerspectiveCamera;
  protected target = new THREE.Vector3();
  protected enabled = true;

  constructor(camera: THREE.PerspectiveCamera) {
    this.camera = camera;
  }

  abstract update(dt: number): void;

  public setTarget(target: THREE.Vector3): void {
    this.target.copy(target);
  }

  public setEnabled(enabled: boolean): void {
    this.enabled = enabled;
  }

  public getCamera(): THREE.PerspectiveCamera {
    return this.camera;
  }
}

// ============================================
// ORBIT CAMERA
// ============================================

export interface OrbitConfig {
  distance: number;
  minDistance: number;
  maxDistance: number;
  rotationSpeed: number;
  zoomSpeed: number;
  damping: number;
  minPolarAngle: number;      // Radians
  maxPolarAngle: number;      // Radians
  autoRotate: boolean;
  autoRotateSpeed: number;
}

export const DEFAULT_ORBIT_CONFIG: OrbitConfig = {
  distance: 5,
  minDistance: 1,
  maxDistance: 100,
  rotationSpeed: 0.5,
  zoomSpeed: 1,
  damping: 0.1,
  minPolarAngle: 0.1,
  maxPolarAngle: Math.PI - 0.1,
  autoRotate: false,
  autoRotateSpeed: 0.5
};

export class OrbitCamera extends CameraController {
  private config: OrbitConfig;
  
  // Spherical coordinates
  private theta: number = 0;           // Horizontal angle
  private phi: number = Math.PI / 3;   // Vertical angle
  private radius: number;
  
  // Target values for damping
  private targetTheta: number = 0;
  private targetPhi: number = Math.PI / 3;
  private targetRadius: number;
  
  // Input state
  private isRotating = false;
  private isPanning = false;
  private lastMouse = new THREE.Vector2();

  constructor(camera: THREE.PerspectiveCamera, config: Partial<OrbitConfig> = {}) {
    super(camera);
    this.config = { ...DEFAULT_ORBIT_CONFIG, ...config };
    this.radius = this.config.distance;
    this.targetRadius = this.radius;
  }

  public handleMouseDown(button: number, x: number, y: number): void {
    if (button === 0) this.isRotating = true;
    if (button === 2) this.isPanning = true;
    this.lastMouse.set(x, y);
  }

  public handleMouseUp(): void {
    this.isRotating = false;
    this.isPanning = false;
  }

  public handleMouseMove(x: number, y: number): void {
    const dx = x - this.lastMouse.x;
    const dy = y - this.lastMouse.y;
    this.lastMouse.set(x, y);
    
    if (this.isRotating) {
      this.targetTheta -= dx * this.config.rotationSpeed * 0.01;
      this.targetPhi -= dy * this.config.rotationSpeed * 0.01;
      
      // Clamp polar angle
      this.targetPhi = THREE.MathUtils.clamp(
        this.targetPhi,
        this.config.minPolarAngle,
        this.config.maxPolarAngle
      );
    }
    
    if (this.isPanning) {
      const panSpeed = this.radius * 0.001;
      const right = new THREE.Vector3()
        .setFromMatrixColumn(this.camera.matrix, 0)
        .multiplyScalar(-dx * panSpeed);
      const up = new THREE.Vector3()
        .setFromMatrixColumn(this.camera.matrix, 1)
        .multiplyScalar(dy * panSpeed);
      
      this.target.add(right).add(up);
    }
  }

  public handleWheel(delta: number): void {
    this.targetRadius += delta * this.config.zoomSpeed * 0.1;
    this.targetRadius = THREE.MathUtils.clamp(
      this.targetRadius,
      this.config.minDistance,
      this.config.maxDistance
    );
  }

  public update(dt: number): void {
    if (!this.enabled) return;
    
    // Auto rotate
    if (this.config.autoRotate && !this.isRotating) {
      this.targetTheta += this.config.autoRotateSpeed * dt;
    }
    
    // Apply damping
    this.theta += (this.targetTheta - this.theta) * this.config.damping;
    this.phi += (this.targetPhi - this.phi) * this.config.damping;
    this.radius += (this.targetRadius - this.radius) * this.config.damping;
    
    // Calculate camera position
    const x = this.radius * Math.sin(this.phi) * Math.cos(this.theta);
    const y = this.radius * Math.cos(this.phi);
    const z = this.radius * Math.sin(this.phi) * Math.sin(this.theta);
    
    this.camera.position.set(
      this.target.x + x,
      this.target.y + y,
      this.target.z + z
    );
    
    this.camera.lookAt(this.target);
  }

  public setOrbit(theta: number, phi: number, radius: number): void {
    this.targetTheta = theta;
    this.targetPhi = phi;
    this.targetRadius = radius;
  }
}

// ============================================
// FIRST PERSON CAMERA
// ============================================

export interface FirstPersonConfig {
  movementSpeed: number;
  lookSpeed: number;
  height: number;
  headBob: boolean;
  headBobAmount: number;
  headBobSpeed: number;
}

export const DEFAULT_FIRST_PERSON_CONFIG: FirstPersonConfig = {
  movementSpeed: 5,
  lookSpeed: 0.002,
  height: 1.7,
  headBob: true,
  headBobAmount: 0.05,
  headBobSpeed: 10
};

export class FirstPersonCamera extends CameraController {
  private config: FirstPersonConfig;
  
  private yaw: number = 0;
  private pitch: number = 0;
  private velocity = new THREE.Vector3();
  private moveForward = false;
  private moveBackward = false;
  private moveLeft = false;
  private moveRight = false;
  
  private bobPhase: number = 0;
  private isMoving = false;

  constructor(camera: THREE.PerspectiveCamera, config: Partial<FirstPersonConfig> = {}) {
    super(camera);
    this.config = { ...DEFAULT_FIRST_PERSON_CONFIG, ...config };
  }

  public handleMouseMove(dx: number, dy: number): void {
    this.yaw -= dx * this.config.lookSpeed;
    this.pitch -= dy * this.config.lookSpeed;
    
    // Clamp pitch
    this.pitch = THREE.MathUtils.clamp(this.pitch, -Math.PI / 2 + 0.1, Math.PI / 2 - 0.1);
  }

  public handleKeyDown(code: string): void {
    switch (code) {
      case 'KeyW': this.moveForward = true; break;
      case 'KeyS': this.moveBackward = true; break;
      case 'KeyA': this.moveLeft = true; break;
      case 'KeyD': this.moveRight = true; break;
    }
  }

  public handleKeyUp(code: string): void {
    switch (code) {
      case 'KeyW': this.moveForward = false; break;
      case 'KeyS': this.moveBackward = false; break;
      case 'KeyA': this.moveLeft = false; break;
      case 'KeyD': this.moveRight = false; break;
    }
  }

  public update(dt: number): void {
    if (!this.enabled) return;
    
    // Calculate movement direction
    const forward = new THREE.Vector3(
      Math.sin(this.yaw),
      0,
      Math.cos(this.yaw)
    );
    const right = new THREE.Vector3(
      Math.sin(this.yaw + Math.PI / 2),
      0,
      Math.cos(this.yaw + Math.PI / 2)
    );
    
    // Apply movement
    this.velocity.set(0, 0, 0);
    
    if (this.moveForward) this.velocity.add(forward);
    if (this.moveBackward) this.velocity.sub(forward);
    if (this.moveRight) this.velocity.add(right);
    if (this.moveLeft) this.velocity.sub(right);
    
    this.isMoving = this.velocity.length() > 0;
    
    if (this.isMoving) {
      this.velocity.normalize().multiplyScalar(this.config.movementSpeed * dt);
      this.camera.position.add(this.velocity);
    }
    
    // Head bob
    let bobOffset = 0;
    if (this.config.headBob && this.isMoving) {
      this.bobPhase += dt * this.config.headBobSpeed;
      bobOffset = Math.sin(this.bobPhase) * this.config.headBobAmount;
    }
    
    // Set height
    this.camera.position.y = this.config.height + bobOffset;
    
    // Apply rotation
    const quaternion = new THREE.Quaternion();
    quaternion.setFromEuler(new THREE.Euler(this.pitch, this.yaw, 0, 'YXZ'));
    this.camera.quaternion.copy(quaternion);
  }

  public setPosition(position: THREE.Vector3): void {
    this.camera.position.copy(position);
    this.camera.position.y = this.config.height;
  }

  public setRotation(yaw: number, pitch: number): void {
    this.yaw = yaw;
    this.pitch = pitch;
  }
}

// ============================================
// THIRD PERSON CAMERA
// ============================================

export interface ThirdPersonConfig {
  distance: number;
  height: number;
  shoulderOffset: number;
  lookAtOffset: number;       // Height offset for look target
  damping: number;
  collisionRadius: number;
  collisionLayers: number;
}

export const DEFAULT_THIRD_PERSON_CONFIG: ThirdPersonConfig = {
  distance: 4,
  height: 2,
  shoulderOffset: 0.5,
  lookAtOffset: 1.5,
  damping: 0.1,
  collisionRadius: 0.3,
  collisionLayers: 0xffffffff
};

export class ThirdPersonCamera extends CameraController {
  private config: ThirdPersonConfig;
  private currentDistance: number;
  private targetPosition = new THREE.Vector3();
  private raycaster = new THREE.Raycaster();
  private collisionMeshes: THREE.Object3D[] = [];

  constructor(camera: THREE.PerspectiveCamera, config: Partial<ThirdPersonConfig> = {}) {
    super(camera);
    this.config = { ...DEFAULT_THIRD_PERSON_CONFIG, ...config };
    this.currentDistance = this.config.distance;
  }

  public addCollisionMesh(mesh: THREE.Object3D): void {
    this.collisionMeshes.push(mesh);
  }

  public update(dt: number): void {
    if (!this.enabled) return;
    
    // Calculate ideal camera position
    const idealPosition = new THREE.Vector3(
      this.target.x + this.config.shoulderOffset,
      this.target.y + this.config.height,
      this.target.z - this.config.distance
    );
    
    // Check for collisions
    let finalDistance = this.config.distance;
    
    if (this.collisionMeshes.length > 0) {
      const direction = idealPosition.clone().sub(this.target).normalize();
      this.raycaster.set(this.target, direction);
      this.raycaster.far = this.config.distance + this.config.collisionRadius;
      
      const intersects = this.raycaster.intersectObjects(this.collisionMeshes, true);
      if (intersects.length > 0) {
        finalDistance = Math.min(
          finalDistance,
          intersects[0].distance - this.config.collisionRadius
        );
      }
    }
    
    // Smooth distance
    this.currentDistance += (finalDistance - this.currentDistance) * this.config.damping;
    
    // Calculate actual position
    const offset = new THREE.Vector3(
      this.config.shoulderOffset,
      this.config.height,
      -this.currentDistance
    );
    
    this.targetPosition.copy(this.target).add(offset);
    
    // Smooth camera movement
    this.camera.position.lerp(this.targetPosition, this.config.damping);
    
    // Look at target
    const lookAtTarget = this.target.clone();
    lookAtTarget.y += this.config.lookAtOffset;
    this.camera.lookAt(lookAtTarget);
  }
}

// ============================================
// CAMERA SHAKE
// ============================================

export interface ShakeConfig {
  intensity: number;
  frequency: number;
  decay: number;
  rotationIntensity: number;
}

export class CameraShake {
  private offset = new THREE.Vector3();
  private rotation = new THREE.Euler();
  private trauma: number = 0;
  private config: ShakeConfig;
  private time: number = 0;

  constructor(config: Partial<ShakeConfig> = {}) {
    this.config = {
      intensity: 0.5,
      frequency: 25,
      decay: 3,
      rotationIntensity: 0.02,
      ...config
    };
  }

  /**
   * Add trauma (0-1)
   */
  public addTrauma(amount: number): void {
    this.trauma = Math.min(1, this.trauma + amount);
  }

  /**
   * Update shake
   */
  public update(dt: number): void {
    this.time += dt;
    
    // Decay trauma
    this.trauma = Math.max(0, this.trauma - this.config.decay * dt);
    
    // Calculate shake using Perlin-like noise
    const shake = this.trauma * this.trauma; // Quadratic for snappier feel
    
    const t = this.time * this.config.frequency;
    
    this.offset.set(
      this.noise(t, 0) * shake * this.config.intensity,
      this.noise(t, 1) * shake * this.config.intensity,
      this.noise(t, 2) * shake * this.config.intensity * 0.5
    );
    
    this.rotation.set(
      this.noise(t, 3) * shake * this.config.rotationIntensity,
      this.noise(t, 4) * shake * this.config.rotationIntensity,
      this.noise(t, 5) * shake * this.config.rotationIntensity * 0.5
    );
  }

  private noise(t: number, seed: number): number {
    return Math.sin(t + seed * 100) * Math.cos(t * 1.5 + seed * 50);
  }

  public getOffset(): THREE.Vector3 {
    return this.offset;
  }

  public getRotation(): THREE.Euler {
    return this.rotation;
  }

  public applyToCamera(camera: THREE.Camera): void {
    camera.position.add(this.offset);
    camera.rotation.x += this.rotation.x;
    camera.rotation.y += this.rotation.y;
    camera.rotation.z += this.rotation.z;
  }
}

// ============================================
// CAMERA TRANSITION
// ============================================

export class CameraTransition {
  private fromPosition = new THREE.Vector3();
  private fromRotation = new THREE.Quaternion();
  private toPosition = new THREE.Vector3();
  private toRotation = new THREE.Quaternion();
  
  private progress: number = 0;
  private duration: number = 0;
  private isActive: boolean = false;
  private easing: (t: number) => number;

  constructor() {
    this.easing = (t) => t < 0.5 
      ? 4 * t * t * t 
      : 1 - Math.pow(-2 * t + 2, 3) / 2; // easeInOutCubic
  }

  public start(
    fromCamera: THREE.Camera,
    toPosition: THREE.Vector3,
    toRotation: THREE.Quaternion,
    duration: number
  ): void {
    this.fromPosition.copy(fromCamera.position);
    this.fromRotation.copy(fromCamera.quaternion);
    this.toPosition.copy(toPosition);
    this.toRotation.copy(toRotation);
    this.duration = duration;
    this.progress = 0;
    this.isActive = true;
  }

  public update(dt: number, camera: THREE.Camera): boolean {
    if (!this.isActive) return false;
    
    this.progress += dt / this.duration;
    
    if (this.progress >= 1) {
      this.progress = 1;
      this.isActive = false;
    }
    
    const t = this.easing(this.progress);
    
    camera.position.lerpVectors(this.fromPosition, this.toPosition, t);
    camera.quaternion.slerpQuaternions(this.fromRotation, this.toRotation, t);
    
    return this.isActive;
  }

  public isTransitioning(): boolean {
    return this.isActive;
  }
}

