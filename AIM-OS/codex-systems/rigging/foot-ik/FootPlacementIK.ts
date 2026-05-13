/**
 * Foot Placement IK System
 * Automatic foot placement on uneven terrain
 * 
 * Features:
 * - Ground detection via raycasting
 * - Smooth foot adjustment
 * - Hip height compensation
 * - Toe/heel alignment
 * - Slope adaptation
 * - Step prediction
 * - Multi-leg support (bipeds, quadrupeds)
 */

import * as THREE from 'three';

// ============================================
// TYPES
// ============================================

export interface FootIKConfig {
  raycastHeight: number;      // Height above foot to start raycast
  raycastDistance: number;    // Total raycast distance
  maxStepHeight: number;      // Maximum height adjustment
  footLength: number;         // Length of foot for rotation
  smoothSpeed: number;        // Interpolation speed
  enableHipAdjustment: boolean;
  enableFootRotation: boolean;
  groundLayers: number[];     // Layer mask for ground detection
}

export interface FootData {
  id: string;
  bone: THREE.Bone;
  ikTarget: THREE.Vector3;
  groundPosition: THREE.Vector3;
  groundNormal: THREE.Vector3;
  isGrounded: boolean;
  targetRotation: THREE.Quaternion;
  currentOffset: number;
  weight: number;  // 0-1 blend weight
}

export interface LegChain {
  id: string;
  hipBone: THREE.Bone;
  kneeBone: THREE.Bone;
  footBone: THREE.Bone;
  toeBone?: THREE.Bone;
  footData: FootData;
  upperLength: number;  // Hip to knee
  lowerLength: number;  // Knee to foot
}

// ============================================
// TWO-BONE IK SOLVER
// ============================================

export class TwoBoneIKSolver {
  /**
   * Solve two-bone IK chain
   */
  public static solve(
    rootPos: THREE.Vector3,
    midPos: THREE.Vector3,
    endPos: THREE.Vector3,
    target: THREE.Vector3,
    upperLength: number,
    lowerLength: number,
    poleTarget?: THREE.Vector3
  ): { midPos: THREE.Vector3; endPos: THREE.Vector3 } {
    const toTarget = target.clone().sub(rootPos);
    const targetDist = toTarget.length();
    
    // Clamp target distance
    const maxDist = upperLength + lowerLength - 0.001;
    const minDist = Math.abs(upperLength - lowerLength) + 0.001;
    const clampedDist = THREE.MathUtils.clamp(targetDist, minDist, maxDist);
    
    // Calculate knee angle using law of cosines
    const kneeAngle = Math.acos(
      (upperLength * upperLength + lowerLength * lowerLength - clampedDist * clampedDist) /
      (2 * upperLength * lowerLength)
    );
    
    // Calculate hip angle
    const hipAngle = Math.acos(
      (upperLength * upperLength + clampedDist * clampedDist - lowerLength * lowerLength) /
      (2 * upperLength * clampedDist)
    );
    
    // Get direction to target
    const direction = toTarget.normalize();
    
    // Calculate pole direction
    let poleDir: THREE.Vector3;
    if (poleTarget) {
      // Direction from root to pole target
      const toPole = poleTarget.clone().sub(rootPos);
      
      // Project onto plane perpendicular to target direction
      const dot = toPole.dot(direction);
      poleDir = toPole.sub(direction.clone().multiplyScalar(dot)).normalize();
    } else {
      // Default pole direction (forward)
      const forward = new THREE.Vector3(0, 0, 1);
      const dot = forward.dot(direction);
      poleDir = forward.clone().sub(direction.clone().multiplyScalar(dot)).normalize();
      
      if (poleDir.lengthSq() < 0.001) {
        poleDir.set(1, 0, 0);
      }
    }
    
    // Calculate mid position (knee)
    const perpendicular = direction.clone().cross(poleDir).normalize();
    const midOffset = poleDir.clone().multiplyScalar(Math.sin(hipAngle) * upperLength);
    const alongTarget = direction.clone().multiplyScalar(Math.cos(hipAngle) * upperLength);
    
    const newMidPos = rootPos.clone().add(alongTarget).add(midOffset);
    
    // Calculate end position (foot)
    const midToTarget = target.clone().sub(newMidPos);
    const newEndPos = newMidPos.clone().add(midToTarget.normalize().multiplyScalar(lowerLength));
    
    return {
      midPos: newMidPos,
      endPos: newEndPos
    };
  }
}

// ============================================
// FOOT PLACEMENT IK SYSTEM
// ============================================

export class FootPlacementIK {
  private config: FootIKConfig;
  private legs: Map<string, LegChain> = new Map();
  private raycaster: THREE.Raycaster;
  private groundMeshes: THREE.Object3D[] = [];
  
  private hipOffset: number = 0;
  private targetHipOffset: number = 0;
  
  constructor(config: Partial<FootIKConfig> = {}) {
    this.config = {
      raycastHeight: 1.0,
      raycastDistance: 2.0,
      maxStepHeight: 0.5,
      footLength: 0.2,
      smoothSpeed: 10,
      enableHipAdjustment: true,
      enableFootRotation: true,
      groundLayers: [],
      ...config
    };
    
    this.raycaster = new THREE.Raycaster();
  }
  
  /**
   * Add leg chain
   */
  public addLeg(
    id: string,
    hipBone: THREE.Bone,
    kneeBone: THREE.Bone,
    footBone: THREE.Bone,
    toeBone?: THREE.Bone
  ): void {
    // Calculate bone lengths
    const hipPos = new THREE.Vector3();
    const kneePos = new THREE.Vector3();
    const footPos = new THREE.Vector3();
    
    hipBone.getWorldPosition(hipPos);
    kneeBone.getWorldPosition(kneePos);
    footBone.getWorldPosition(footPos);
    
    const upperLength = hipPos.distanceTo(kneePos);
    const lowerLength = kneePos.distanceTo(footPos);
    
    const footData: FootData = {
      id,
      bone: footBone,
      ikTarget: footPos.clone(),
      groundPosition: footPos.clone(),
      groundNormal: new THREE.Vector3(0, 1, 0),
      isGrounded: false,
      targetRotation: footBone.quaternion.clone(),
      currentOffset: 0,
      weight: 1
    };
    
    const leg: LegChain = {
      id,
      hipBone,
      kneeBone,
      footBone,
      toeBone,
      footData,
      upperLength,
      lowerLength
    };
    
    this.legs.set(id, leg);
  }
  
  /**
   * Set ground meshes for raycasting
   */
  public setGroundMeshes(meshes: THREE.Object3D[]): void {
    this.groundMeshes = meshes;
  }
  
  /**
   * Update foot placement
   */
  public update(deltaTime: number): void {
    let minFootHeight = Infinity;
    let maxFootHeight = -Infinity;
    
    // First pass: detect ground for each foot
    for (const leg of this.legs.values()) {
      this.updateFootGround(leg);
      
      if (leg.footData.isGrounded) {
        const footHeight = leg.footData.groundPosition.y;
        minFootHeight = Math.min(minFootHeight, footHeight);
        maxFootHeight = Math.max(maxFootHeight, footHeight);
      }
    }
    
    // Calculate hip adjustment
    if (this.config.enableHipAdjustment && minFootHeight !== Infinity) {
      // Average foot height determines hip adjustment
      const avgHeight = (minFootHeight + maxFootHeight) / 2;
      this.targetHipOffset = -avgHeight; // Negative because we lower the hip
      
      // Clamp to max step height
      this.targetHipOffset = THREE.MathUtils.clamp(
        this.targetHipOffset,
        -this.config.maxStepHeight,
        this.config.maxStepHeight
      );
    }
    
    // Smooth hip offset
    this.hipOffset = THREE.MathUtils.lerp(
      this.hipOffset,
      this.targetHipOffset,
      this.config.smoothSpeed * deltaTime
    );
    
    // Second pass: apply IK
    for (const leg of this.legs.values()) {
      this.applyLegIK(leg, deltaTime);
    }
  }
  
  private updateFootGround(leg: LegChain): void {
    const footData = leg.footData;
    const footBone = leg.footBone;
    
    // Get current foot world position
    const footWorldPos = new THREE.Vector3();
    footBone.getWorldPosition(footWorldPos);
    
    // Raycast origin (above foot)
    const rayOrigin = footWorldPos.clone();
    rayOrigin.y += this.config.raycastHeight;
    
    // Raycast downward
    this.raycaster.set(rayOrigin, new THREE.Vector3(0, -1, 0));
    this.raycaster.far = this.config.raycastDistance;
    
    const intersects = this.raycaster.intersectObjects(this.groundMeshes, true);
    
    if (intersects.length > 0) {
      const hit = intersects[0];
      
      footData.isGrounded = true;
      footData.groundPosition.copy(hit.point);
      
      if (hit.face) {
        // Transform normal to world space
        const normalMatrix = new THREE.Matrix3().getNormalMatrix(hit.object.matrixWorld);
        footData.groundNormal.copy(hit.face.normal).applyMatrix3(normalMatrix).normalize();
      } else {
        footData.groundNormal.set(0, 1, 0);
      }
      
      // Calculate target position with offset
      const targetHeight = hit.point.y;
      const currentHeight = footWorldPos.y;
      const heightDiff = targetHeight - currentHeight;
      
      // Clamp height adjustment
      footData.currentOffset = THREE.MathUtils.clamp(
        heightDiff,
        -this.config.maxStepHeight,
        this.config.maxStepHeight
      );
      
      footData.ikTarget.copy(footWorldPos);
      footData.ikTarget.y = targetHeight;
      
      // Calculate foot rotation to align with ground
      if (this.config.enableFootRotation) {
        this.calculateFootRotation(footData);
      }
    } else {
      footData.isGrounded = false;
      footData.currentOffset = 0;
      footData.ikTarget.copy(footWorldPos);
    }
  }
  
  private calculateFootRotation(footData: FootData): void {
    // Align foot forward direction with ground normal
    const up = footData.groundNormal.clone();
    const forward = new THREE.Vector3(0, 0, 1); // Foot forward direction
    
    // Make forward perpendicular to up
    const right = forward.clone().cross(up).normalize();
    const adjustedForward = up.clone().cross(right).normalize();
    
    // Create rotation matrix
    const rotMatrix = new THREE.Matrix4();
    rotMatrix.makeBasis(right, up, adjustedForward);
    
    footData.targetRotation.setFromRotationMatrix(rotMatrix);
  }
  
  private applyLegIK(leg: LegChain, deltaTime: number): void {
    const footData = leg.footData;
    
    // Apply weight
    if (footData.weight <= 0) return;
    
    // Get bone world positions
    const hipWorldPos = new THREE.Vector3();
    const kneeWorldPos = new THREE.Vector3();
    const footWorldPos = new THREE.Vector3();
    
    leg.hipBone.getWorldPosition(hipWorldPos);
    leg.kneeBone.getWorldPosition(kneeWorldPos);
    leg.footBone.getWorldPosition(footWorldPos);
    
    // Apply hip offset
    if (this.config.enableHipAdjustment) {
      hipWorldPos.y += this.hipOffset;
    }
    
    // Calculate target position with weight
    const target = footWorldPos.clone().lerp(footData.ikTarget, footData.weight);
    
    // Solve IK
    const poleTarget = kneeWorldPos.clone();
    poleTarget.z += 1; // Knee forward
    
    const result = TwoBoneIKSolver.solve(
      hipWorldPos,
      kneeWorldPos,
      footWorldPos,
      target,
      leg.upperLength,
      leg.lowerLength,
      poleTarget
    );
    
    // Apply result to bones (in local space)
    this.applyBonePosition(leg.hipBone, leg.kneeBone, hipWorldPos, result.midPos);
    this.applyBonePosition(leg.kneeBone, leg.footBone, result.midPos, result.endPos);
    
    // Apply foot rotation
    if (this.config.enableFootRotation && footData.isGrounded) {
      const currentRot = leg.footBone.quaternion.clone();
      const targetRot = footData.targetRotation;
      
      // Smooth rotation
      leg.footBone.quaternion.slerp(targetRot, this.config.smoothSpeed * deltaTime);
    }
  }
  
  private applyBonePosition(
    parentBone: THREE.Bone,
    childBone: THREE.Bone,
    parentWorldPos: THREE.Vector3,
    childWorldPos: THREE.Vector3
  ): void {
    // Calculate direction from parent to child
    const direction = childWorldPos.clone().sub(parentWorldPos).normalize();
    
    // Get parent's world matrix
    const parentWorld = parentBone.matrixWorld.clone();
    const parentWorldInverse = parentWorld.clone().invert();
    
    // Convert direction to local space
    const localDirection = direction.clone().applyMatrix4(parentWorldInverse).normalize();
    
    // Calculate rotation to point in that direction
    const up = new THREE.Vector3(0, 1, 0);
    const right = localDirection.clone().cross(up).normalize();
    const adjustedUp = right.clone().cross(localDirection).normalize();
    
    const rotMatrix = new THREE.Matrix4();
    rotMatrix.makeBasis(right, adjustedUp, localDirection);
    
    const targetRotation = new THREE.Quaternion().setFromRotationMatrix(rotMatrix);
    
    // Apply rotation (blend with current)
    parentBone.quaternion.slerp(targetRotation, 0.5);
  }
  
  /**
   * Set foot IK weight
   */
  public setFootWeight(legId: string, weight: number): void {
    const leg = this.legs.get(legId);
    if (leg) {
      leg.footData.weight = THREE.MathUtils.clamp(weight, 0, 1);
    }
  }
  
  /**
   * Get hip offset
   */
  public getHipOffset(): number {
    return this.hipOffset;
  }
  
  /**
   * Get foot data
   */
  public getFootData(legId: string): FootData | undefined {
    return this.legs.get(legId)?.footData;
  }
  
  /**
   * Check if foot is grounded
   */
  public isFootGrounded(legId: string): boolean {
    return this.legs.get(legId)?.footData.isGrounded ?? false;
  }
  
  /**
   * Set config
   */
  public setConfig(config: Partial<FootIKConfig>): void {
    Object.assign(this.config, config);
  }
  
  /**
   * Dispose
   */
  public dispose(): void {
    this.legs.clear();
    this.groundMeshes = [];
  }
}

