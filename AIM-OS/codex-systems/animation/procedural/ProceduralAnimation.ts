/**
 * Procedural Animation System
 * Physics-driven secondary motion, breathing, look-at, etc.
 * 
 * Reduces animation data, adds life to static poses
 */

import * as THREE from 'three';

// ============================================
// SPRING DYNAMICS
// ============================================

export interface SpringConfig {
  stiffness: number;      // Spring constant (higher = stiffer)
  damping: number;        // Damping ratio (0-1, critical = 1)
  mass: number;           // Mass affects response time
}

export const DEFAULT_SPRING: SpringConfig = {
  stiffness: 150,
  damping: 0.8,
  mass: 1.0
};

export class Spring1D {
  private target: number = 0;
  private current: number = 0;
  private velocity: number = 0;
  private config: SpringConfig;

  constructor(initial: number = 0, config: Partial<SpringConfig> = {}) {
    this.current = initial;
    this.target = initial;
    this.config = { ...DEFAULT_SPRING, ...config };
  }

  public setTarget(target: number): void {
    this.target = target;
  }

  public update(dt: number): number {
    const { stiffness, damping, mass } = this.config;
    
    // Spring force: F = -k * x
    const displacement = this.current - this.target;
    const springForce = -stiffness * displacement;
    
    // Damping force: F = -c * v
    const dampingForce = -2 * damping * Math.sqrt(stiffness * mass) * this.velocity;
    
    // Acceleration: a = F / m
    const acceleration = (springForce + dampingForce) / mass;
    
    // Integrate
    this.velocity += acceleration * dt;
    this.current += this.velocity * dt;
    
    return this.current;
  }

  public getValue(): number {
    return this.current;
  }

  public reset(value: number): void {
    this.current = value;
    this.target = value;
    this.velocity = 0;
  }
}

export class Spring3D {
  private x: Spring1D;
  private y: Spring1D;
  private z: Spring1D;
  private readonly _result = new THREE.Vector3();

  constructor(initial: THREE.Vector3 = new THREE.Vector3(), config: Partial<SpringConfig> = {}) {
    this.x = new Spring1D(initial.x, config);
    this.y = new Spring1D(initial.y, config);
    this.z = new Spring1D(initial.z, config);
  }

  public setTarget(target: THREE.Vector3): void {
    this.x.setTarget(target.x);
    this.y.setTarget(target.y);
    this.z.setTarget(target.z);
  }

  public update(dt: number): THREE.Vector3 {
    this._result.set(
      this.x.update(dt),
      this.y.update(dt),
      this.z.update(dt)
    );
    return this._result;
  }

  public getValue(): THREE.Vector3 {
    return this._result.set(
      this.x.getValue(),
      this.y.getValue(),
      this.z.getValue()
    );
  }

  public reset(value: THREE.Vector3): void {
    this.x.reset(value.x);
    this.y.reset(value.y);
    this.z.reset(value.z);
  }
}

// ============================================
// JIGGLE PHYSICS
// ============================================

export interface JiggleConfig {
  spring: SpringConfig;
  gravity: THREE.Vector3;
  maxDisplacement: number;
  inheritVelocity: number;   // How much parent velocity affects jiggle
}

export const DEFAULT_JIGGLE: JiggleConfig = {
  spring: { stiffness: 100, damping: 0.6, mass: 0.5 },
  gravity: new THREE.Vector3(0, -2, 0),
  maxDisplacement: 0.2,
  inheritVelocity: 0.3
};

export class JiggleBone {
  private config: JiggleConfig;
  private spring: Spring3D;
  private lastParentPos = new THREE.Vector3();
  private parentVelocity = new THREE.Vector3();
  
  public bone: THREE.Bone;
  public restPosition: THREE.Vector3;

  constructor(bone: THREE.Bone, config: Partial<JiggleConfig> = {}) {
    this.bone = bone;
    this.config = { ...DEFAULT_JIGGLE, ...config };
    this.restPosition = bone.position.clone();
    this.spring = new Spring3D(this.restPosition, this.config.spring);
    this.lastParentPos.copy(bone.parent?.position || new THREE.Vector3());
  }

  public update(dt: number): void {
    // Calculate parent velocity
    const currentParentPos = this.bone.parent?.position || new THREE.Vector3();
    this.parentVelocity.subVectors(currentParentPos, this.lastParentPos).divideScalar(dt);
    this.lastParentPos.copy(currentParentPos);
    
    // Target is rest position plus gravity and inherited velocity
    const target = this.restPosition.clone()
      .add(this.config.gravity.clone().multiplyScalar(0.01))
      .addScaledVector(this.parentVelocity, -this.config.inheritVelocity * 0.1);
    
    this.spring.setTarget(target);
    const newPos = this.spring.update(dt);
    
    // Clamp displacement
    const displacement = newPos.clone().sub(this.restPosition);
    if (displacement.length() > this.config.maxDisplacement) {
      displacement.normalize().multiplyScalar(this.config.maxDisplacement);
      newPos.copy(this.restPosition).add(displacement);
    }
    
    this.bone.position.copy(newPos);
  }
}

// ============================================
// BREATHING ANIMATION
// ============================================

export interface BreathingConfig {
  rate: number;              // Breaths per minute
  intensity: number;         // Scale factor (0-1)
  chestExpansion: number;    // How much chest expands
  shoulderRise: number;      // How much shoulders rise
  bellyExpansion: number;    // Belly movement
  irregularity: number;      // Random variation (0-1)
}

export const DEFAULT_BREATHING: BreathingConfig = {
  rate: 15,
  intensity: 1.0,
  chestExpansion: 0.02,
  shoulderRise: 0.01,
  bellyExpansion: 0.03,
  irregularity: 0.1
};

export class BreathingController {
  private config: BreathingConfig;
  private time: number = 0;
  private phase: number = 0;
  private nextIrregularity: number = 0;
  
  // Bones to animate
  public spine?: THREE.Bone;
  public chest?: THREE.Bone;
  public leftShoulder?: THREE.Bone;
  public rightShoulder?: THREE.Bone;
  
  // Rest poses
  private spineRest?: THREE.Vector3;
  private chestRest?: THREE.Vector3;
  private leftShoulderRest?: THREE.Vector3;
  private rightShoulderRest?: THREE.Vector3;

  constructor(config: Partial<BreathingConfig> = {}) {
    this.config = { ...DEFAULT_BREATHING, ...config };
  }

  public setBones(
    spine?: THREE.Bone,
    chest?: THREE.Bone,
    leftShoulder?: THREE.Bone,
    rightShoulder?: THREE.Bone
  ): void {
    this.spine = spine;
    this.chest = chest;
    this.leftShoulder = leftShoulder;
    this.rightShoulder = rightShoulder;
    
    // Store rest positions
    if (spine) this.spineRest = spine.position.clone();
    if (chest) this.chestRest = chest.position.clone();
    if (leftShoulder) this.leftShoulderRest = leftShoulder.position.clone();
    if (rightShoulder) this.rightShoulderRest = rightShoulder.position.clone();
  }

  public update(dt: number): void {
    this.time += dt;
    
    // Calculate breath phase (0-1, with ease in/out)
    const cycleTime = 60 / this.config.rate;
    const rawPhase = (this.time % cycleTime) / cycleTime;
    
    // Add irregularity
    if (rawPhase < 0.01) {
      this.nextIrregularity = (Math.random() - 0.5) * 2 * this.config.irregularity;
    }
    
    // Smooth breathing curve (inhale faster, exhale slower)
    let breathPhase: number;
    if (rawPhase < 0.4) {
      // Inhale (0-0.4 -> 0-1)
      breathPhase = this.easeInOut(rawPhase / 0.4);
    } else {
      // Exhale (0.4-1.0 -> 1-0)
      breathPhase = 1.0 - this.easeInOut((rawPhase - 0.4) / 0.6);
    }
    
    breathPhase *= this.config.intensity * (1 + this.nextIrregularity);
    this.phase = breathPhase;
    
    // Apply to bones
    if (this.spine && this.spineRest) {
      this.spine.position.copy(this.spineRest);
      this.spine.position.z += breathPhase * this.config.bellyExpansion;
    }
    
    if (this.chest && this.chestRest) {
      this.chest.position.copy(this.chestRest);
      this.chest.position.y += breathPhase * this.config.chestExpansion * 0.5;
      this.chest.position.z += breathPhase * this.config.chestExpansion;
    }
    
    if (this.leftShoulder && this.leftShoulderRest) {
      this.leftShoulder.position.copy(this.leftShoulderRest);
      this.leftShoulder.position.y += breathPhase * this.config.shoulderRise;
    }
    
    if (this.rightShoulder && this.rightShoulderRest) {
      this.rightShoulder.position.copy(this.rightShoulderRest);
      this.rightShoulder.position.y += breathPhase * this.config.shoulderRise;
    }
  }

  private easeInOut(t: number): number {
    return t < 0.5 
      ? 2 * t * t 
      : 1 - Math.pow(-2 * t + 2, 2) / 2;
  }

  public getPhase(): number {
    return this.phase;
  }
}

// ============================================
// LOOK-AT / HEAD TRACKING
// ============================================

export interface LookAtConfig {
  speed: number;             // Rotation speed (degrees/second)
  maxHorizontal: number;     // Max horizontal rotation (degrees)
  maxVertical: number;       // Max vertical rotation (degrees)
  eyeWeight: number;         // How much eyes contribute (0-1)
  headWeight: number;        // How much head contributes (0-1)
  neckWeight: number;        // How much neck contributes (0-1)
  smoothing: number;         // Smoothing factor (0-1)
  idleMovement: boolean;     // Random idle eye movement
}

export const DEFAULT_LOOK_AT: LookAtConfig = {
  speed: 180,
  maxHorizontal: 70,
  maxVertical: 45,
  eyeWeight: 0.3,
  headWeight: 0.5,
  neckWeight: 0.2,
  smoothing: 0.1,
  idleMovement: true
};

export class LookAtController {
  private config: LookAtConfig;
  private target = new THREE.Vector3();
  private currentRotation = new THREE.Euler();
  private targetRotation = new THREE.Euler();
  private idleOffset = new THREE.Vector2();
  private idleTime = 0;
  private nextBlinkTime = 0;
  private isBlinking = false;
  private blinkProgress = 0;
  
  // Bones
  public head?: THREE.Bone;
  public neck?: THREE.Bone;
  public leftEye?: THREE.Bone;
  public rightEye?: THREE.Bone;
  
  // Rest rotations
  private headRest?: THREE.Quaternion;
  private neckRest?: THREE.Quaternion;
  private leftEyeRest?: THREE.Quaternion;
  private rightEyeRest?: THREE.Quaternion;
  
  private readonly _tempQuat = new THREE.Quaternion();
  private readonly _tempEuler = new THREE.Euler();

  constructor(config: Partial<LookAtConfig> = {}) {
    this.config = { ...DEFAULT_LOOK_AT, ...config };
  }

  public setBones(
    head?: THREE.Bone,
    neck?: THREE.Bone,
    leftEye?: THREE.Bone,
    rightEye?: THREE.Bone
  ): void {
    this.head = head;
    this.neck = neck;
    this.leftEye = leftEye;
    this.rightEye = rightEye;
    
    // Store rest rotations
    if (head) this.headRest = head.quaternion.clone();
    if (neck) this.neckRest = neck.quaternion.clone();
    if (leftEye) this.leftEyeRest = leftEye.quaternion.clone();
    if (rightEye) this.rightEyeRest = rightEye.quaternion.clone();
  }

  public setTarget(target: THREE.Vector3): void {
    this.target.copy(target);
  }

  public update(dt: number): void {
    if (!this.head) return;
    
    // Get head world position
    const headWorldPos = new THREE.Vector3();
    this.head.getWorldPosition(headWorldPos);
    
    // Direction to target
    const direction = this.target.clone().sub(headWorldPos).normalize();
    
    // Convert to local space angles
    const headWorldQuat = new THREE.Quaternion();
    this.head.getWorldQuaternion(headWorldQuat);
    const localDir = direction.clone().applyQuaternion(headWorldQuat.invert());
    
    // Calculate target angles
    let targetYaw = Math.atan2(localDir.x, localDir.z);
    let targetPitch = Math.asin(-localDir.y);
    
    // Clamp angles
    const maxH = THREE.MathUtils.degToRad(this.config.maxHorizontal);
    const maxV = THREE.MathUtils.degToRad(this.config.maxVertical);
    targetYaw = THREE.MathUtils.clamp(targetYaw, -maxH, maxH);
    targetPitch = THREE.MathUtils.clamp(targetPitch, -maxV, maxV);
    
    // Add idle movement
    if (this.config.idleMovement) {
      this.idleTime += dt;
      this.idleOffset.x = Math.sin(this.idleTime * 0.5) * 0.02;
      this.idleOffset.y = Math.sin(this.idleTime * 0.3 + 1.5) * 0.01;
      targetYaw += this.idleOffset.x;
      targetPitch += this.idleOffset.y;
    }
    
    // Smooth interpolation
    this.targetRotation.set(targetPitch, targetYaw, 0);
    this.currentRotation.x += (this.targetRotation.x - this.currentRotation.x) * this.config.smoothing;
    this.currentRotation.y += (this.targetRotation.y - this.currentRotation.y) * this.config.smoothing;
    
    // Distribute rotation across bones
    const neckYaw = this.currentRotation.y * this.config.neckWeight;
    const neckPitch = this.currentRotation.x * this.config.neckWeight;
    const headYaw = this.currentRotation.y * this.config.headWeight;
    const headPitch = this.currentRotation.x * this.config.headWeight;
    const eyeYaw = this.currentRotation.y * this.config.eyeWeight;
    const eyePitch = this.currentRotation.x * this.config.eyeWeight;
    
    // Apply to neck
    if (this.neck && this.neckRest) {
      this._tempEuler.set(neckPitch, neckYaw, 0);
      this._tempQuat.setFromEuler(this._tempEuler);
      this.neck.quaternion.copy(this.neckRest).multiply(this._tempQuat);
    }
    
    // Apply to head
    if (this.head && this.headRest) {
      this._tempEuler.set(headPitch, headYaw, 0);
      this._tempQuat.setFromEuler(this._tempEuler);
      this.head.quaternion.copy(this.headRest).multiply(this._tempQuat);
    }
    
    // Apply to eyes
    if (this.leftEye && this.leftEyeRest) {
      this._tempEuler.set(eyePitch, eyeYaw, 0);
      this._tempQuat.setFromEuler(this._tempEuler);
      this.leftEye.quaternion.copy(this.leftEyeRest).multiply(this._tempQuat);
    }
    
    if (this.rightEye && this.rightEyeRest) {
      this._tempEuler.set(eyePitch, eyeYaw, 0);
      this._tempQuat.setFromEuler(this._tempEuler);
      this.rightEye.quaternion.copy(this.rightEyeRest).multiply(this._tempQuat);
    }
    
    // Handle blinking
    this.updateBlink(dt);
  }

  private updateBlink(dt: number): void {
    if (!this.isBlinking) {
      this.nextBlinkTime -= dt;
      if (this.nextBlinkTime <= 0) {
        this.isBlinking = true;
        this.blinkProgress = 0;
        this.nextBlinkTime = 2 + Math.random() * 4; // 2-6 seconds between blinks
      }
    } else {
      this.blinkProgress += dt * 10; // Blink takes ~0.2 seconds
      if (this.blinkProgress >= 1) {
        this.isBlinking = false;
      }
    }
  }

  public getBlinkWeight(): number {
    if (!this.isBlinking) return 0;
    // Smooth blink curve (close fast, open slow)
    return this.blinkProgress < 0.5
      ? this.blinkProgress * 2
      : 1 - (this.blinkProgress - 0.5) * 2;
  }
}

// ============================================
// FOOT PLACEMENT (IK-based ground adaptation)
// ============================================

export interface FootPlacementConfig {
  raycastDistance: number;
  footHeight: number;
  maxAdjustment: number;
  blendSpeed: number;
  hipAdjustment: boolean;
}

export const DEFAULT_FOOT_PLACEMENT: FootPlacementConfig = {
  raycastDistance: 1.5,
  footHeight: 0.1,
  maxAdjustment: 0.3,
  blendSpeed: 10,
  hipAdjustment: true
};

export class FootPlacementController {
  private config: FootPlacementConfig;
  
  public leftFoot?: THREE.Bone;
  public rightFoot?: THREE.Bone;
  public hips?: THREE.Bone;
  
  private leftAdjustment = 0;
  private rightAdjustment = 0;
  private leftTarget = 0;
  private rightTarget = 0;
  
  private readonly _rayOrigin = new THREE.Vector3();
  private readonly _rayDir = new THREE.Vector3(0, -1, 0);

  constructor(config: Partial<FootPlacementConfig> = {}) {
    this.config = { ...DEFAULT_FOOT_PLACEMENT, ...config };
  }

  public setBones(leftFoot?: THREE.Bone, rightFoot?: THREE.Bone, hips?: THREE.Bone): void {
    this.leftFoot = leftFoot;
    this.rightFoot = rightFoot;
    this.hips = hips;
  }

  public update(
    dt: number,
    raycaster: (origin: THREE.Vector3, direction: THREE.Vector3) => { hit: boolean; point: THREE.Vector3 }
  ): void {
    // Raycast from each foot
    if (this.leftFoot) {
      this.leftFoot.getWorldPosition(this._rayOrigin);
      this._rayOrigin.y += this.config.footHeight;
      
      const result = raycaster(this._rayOrigin, this._rayDir);
      if (result.hit) {
        const groundY = result.point.y;
        const footY = this._rayOrigin.y - this.config.footHeight;
        this.leftTarget = THREE.MathUtils.clamp(
          groundY - footY + this.config.footHeight,
          -this.config.maxAdjustment,
          this.config.maxAdjustment
        );
      }
    }
    
    if (this.rightFoot) {
      this.rightFoot.getWorldPosition(this._rayOrigin);
      this._rayOrigin.y += this.config.footHeight;
      
      const result = raycaster(this._rayOrigin, this._rayDir);
      if (result.hit) {
        const groundY = result.point.y;
        const footY = this._rayOrigin.y - this.config.footHeight;
        this.rightTarget = THREE.MathUtils.clamp(
          groundY - footY + this.config.footHeight,
          -this.config.maxAdjustment,
          this.config.maxAdjustment
        );
      }
    }
    
    // Smooth blend
    this.leftAdjustment += (this.leftTarget - this.leftAdjustment) * this.config.blendSpeed * dt;
    this.rightAdjustment += (this.rightTarget - this.rightAdjustment) * this.config.blendSpeed * dt;
    
    // Apply adjustments
    if (this.leftFoot) {
      this.leftFoot.position.y += this.leftAdjustment;
    }
    
    if (this.rightFoot) {
      this.rightFoot.position.y += this.rightAdjustment;
    }
    
    // Adjust hips to lowest foot
    if (this.config.hipAdjustment && this.hips) {
      const hipOffset = Math.min(this.leftAdjustment, this.rightAdjustment);
      this.hips.position.y += hipOffset;
    }
  }
}

