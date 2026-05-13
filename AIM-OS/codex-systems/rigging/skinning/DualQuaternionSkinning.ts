/**
 * Dual Quaternion Skinning (DQS)
 * Solves the "candy wrapper" artifact problem in Linear Blend Skinning
 * 
 * Based on: "Geometric Skinning with Approximate Dual Quaternion Blending"
 * by Kavan et al.
 */

import * as THREE from 'three';

/**
 * Dual Quaternion representation
 * q = q_r + ε * q_d
 * where q_r is the rotation quaternion
 * and q_d is the dual part encoding translation
 */
export class DualQuaternion {
  // Real part (rotation)
  public real: THREE.Quaternion;
  // Dual part (translation encoded)
  public dual: THREE.Quaternion;

  constructor() {
    this.real = new THREE.Quaternion(0, 0, 0, 1);
    this.dual = new THREE.Quaternion(0, 0, 0, 0);
  }

  /**
   * Create from rotation quaternion and translation vector
   */
  public static fromRotationTranslation(
    rotation: THREE.Quaternion,
    translation: THREE.Vector3
  ): DualQuaternion {
    const dq = new DualQuaternion();
    dq.real.copy(rotation);
    
    // dual = 0.5 * translation_quat * rotation
    const t = new THREE.Quaternion(
      translation.x,
      translation.y,
      translation.z,
      0
    );
    dq.dual.copy(t);
    dq.dual.multiply(rotation);
    dq.dual.x *= 0.5;
    dq.dual.y *= 0.5;
    dq.dual.z *= 0.5;
    dq.dual.w *= 0.5;
    
    return dq;
  }

  /**
   * Create from transformation matrix
   */
  public static fromMatrix4(matrix: THREE.Matrix4): DualQuaternion {
    const position = new THREE.Vector3();
    const rotation = new THREE.Quaternion();
    const scale = new THREE.Vector3();
    
    matrix.decompose(position, rotation, scale);
    
    return DualQuaternion.fromRotationTranslation(rotation, position);
  }

  /**
   * Convert to transformation matrix
   */
  public toMatrix4(): THREE.Matrix4 {
    const matrix = new THREE.Matrix4();
    const translation = this.getTranslation();
    
    matrix.makeRotationFromQuaternion(this.real);
    matrix.setPosition(translation);
    
    return matrix;
  }

  /**
   * Extract translation from dual quaternion
   */
  public getTranslation(): THREE.Vector3 {
    // t = 2 * dual * conjugate(real)
    const t = new THREE.Quaternion();
    t.copy(this.dual);
    t.multiply(this.conjugateReal());
    
    return new THREE.Vector3(t.x * 2, t.y * 2, t.z * 2);
  }

  private conjugateReal(): THREE.Quaternion {
    return new THREE.Quaternion(-this.real.x, -this.real.y, -this.real.z, this.real.w);
  }

  /**
   * Normalize dual quaternion
   */
  public normalize(): DualQuaternion {
    const mag = Math.sqrt(
      this.real.x * this.real.x +
      this.real.y * this.real.y +
      this.real.z * this.real.z +
      this.real.w * this.real.w
    );
    
    if (mag > 0.0001) {
      const invMag = 1.0 / mag;
      this.real.x *= invMag;
      this.real.y *= invMag;
      this.real.z *= invMag;
      this.real.w *= invMag;
      this.dual.x *= invMag;
      this.dual.y *= invMag;
      this.dual.z *= invMag;
      this.dual.w *= invMag;
    }
    
    return this;
  }

  /**
   * Add another dual quaternion (for blending)
   */
  public add(other: DualQuaternion): DualQuaternion {
    this.real.x += other.real.x;
    this.real.y += other.real.y;
    this.real.z += other.real.z;
    this.real.w += other.real.w;
    this.dual.x += other.dual.x;
    this.dual.y += other.dual.y;
    this.dual.z += other.dual.z;
    this.dual.w += other.dual.w;
    return this;
  }

  /**
   * Scale dual quaternion (for weighted blending)
   */
  public scale(s: number): DualQuaternion {
    this.real.x *= s;
    this.real.y *= s;
    this.real.z *= s;
    this.real.w *= s;
    this.dual.x *= s;
    this.dual.y *= s;
    this.dual.z *= s;
    this.dual.w *= s;
    return this;
  }

  /**
   * Clone this dual quaternion
   */
  public clone(): DualQuaternion {
    const dq = new DualQuaternion();
    dq.real.copy(this.real);
    dq.dual.copy(this.dual);
    return dq;
  }
}

/**
 * Dual Quaternion Skinning System
 */
export class DualQuaternionSkinning {
  private boneDualQuats: DualQuaternion[] = [];
  private bindPoseDualQuats: DualQuaternion[] = [];
  private inverseBind: DualQuaternion[] = [];
  
  // Temp objects
  private readonly _dq = new DualQuaternion();
  private readonly _blendedDQ = new DualQuaternion();
  private readonly _v = new THREE.Vector3();

  /**
   * Initialize with skeleton bind pose
   */
  public initFromSkeleton(skeleton: THREE.Skeleton): void {
    this.boneDualQuats = [];
    this.bindPoseDualQuats = [];
    this.inverseBind = [];
    
    for (let i = 0; i < skeleton.bones.length; i++) {
      // Current pose (identity initially)
      this.boneDualQuats.push(new DualQuaternion());
      
      // Bind pose inverse
      const inverseMatrix = skeleton.boneInverses[i].clone();
      this.inverseBind.push(DualQuaternion.fromMatrix4(inverseMatrix));
      
      // Bind pose
      const bindMatrix = new THREE.Matrix4().copy(inverseMatrix).invert();
      this.bindPoseDualQuats.push(DualQuaternion.fromMatrix4(bindMatrix));
    }
  }

  /**
   * Update bone transforms from skeleton
   */
  public updateFromSkeleton(skeleton: THREE.Skeleton): void {
    for (let i = 0; i < skeleton.bones.length; i++) {
      const bone = skeleton.bones[i];
      bone.updateMatrixWorld(true);
      
      // Bone world matrix * inverse bind pose
      const skinMatrix = new THREE.Matrix4();
      skinMatrix.multiplyMatrices(bone.matrixWorld, skeleton.boneInverses[i]);
      
      this.boneDualQuats[i] = DualQuaternion.fromMatrix4(skinMatrix);
    }
  }

  /**
   * Transform vertex using DQS
   * @param position Original vertex position
   * @param boneIndices Up to 4 bone indices
   * @param boneWeights Up to 4 bone weights (must sum to 1)
   * @returns Transformed position
   */
  public transformVertex(
    position: THREE.Vector3,
    boneIndices: number[],
    boneWeights: number[]
  ): THREE.Vector3 {
    // Blend dual quaternions
    this._blendedDQ.real.set(0, 0, 0, 0);
    this._blendedDQ.dual.set(0, 0, 0, 0);
    
    // Check for antipodality and flip if needed
    const pivot = this.boneDualQuats[boneIndices[0]];
    
    for (let i = 0; i < 4; i++) {
      const weight = boneWeights[i];
      if (weight <= 0.0001) continue;
      
      const boneDQ = this.boneDualQuats[boneIndices[i]];
      
      // Check if we need to flip (antipodality)
      const dot = 
        pivot.real.x * boneDQ.real.x +
        pivot.real.y * boneDQ.real.y +
        pivot.real.z * boneDQ.real.z +
        pivot.real.w * boneDQ.real.w;
      
      const sign = dot < 0 ? -1 : 1;
      
      // Add weighted contribution
      this._blendedDQ.real.x += sign * weight * boneDQ.real.x;
      this._blendedDQ.real.y += sign * weight * boneDQ.real.y;
      this._blendedDQ.real.z += sign * weight * boneDQ.real.z;
      this._blendedDQ.real.w += sign * weight * boneDQ.real.w;
      this._blendedDQ.dual.x += sign * weight * boneDQ.dual.x;
      this._blendedDQ.dual.y += sign * weight * boneDQ.dual.y;
      this._blendedDQ.dual.z += sign * weight * boneDQ.dual.z;
      this._blendedDQ.dual.w += sign * weight * boneDQ.dual.w;
    }
    
    // Normalize blended dual quaternion
    this._blendedDQ.normalize();
    
    // Transform vertex: v' = q_r * v * conj(q_r) + t
    const result = new THREE.Vector3();
    
    // Rotation: v' = q * v * q^-1
    const qr = this._blendedDQ.real;
    const vx = position.x;
    const vy = position.y;
    const vz = position.z;
    
    // Optimized quaternion-vector rotation
    const ix = qr.w * vx + qr.y * vz - qr.z * vy;
    const iy = qr.w * vy + qr.z * vx - qr.x * vz;
    const iz = qr.w * vz + qr.x * vy - qr.y * vx;
    const iw = -qr.x * vx - qr.y * vy - qr.z * vz;
    
    result.x = ix * qr.w + iw * -qr.x + iy * -qr.z - iz * -qr.y;
    result.y = iy * qr.w + iw * -qr.y + iz * -qr.x - ix * -qr.z;
    result.z = iz * qr.w + iw * -qr.z + ix * -qr.y - iy * -qr.x;
    
    // Add translation
    const translation = this._blendedDQ.getTranslation();
    result.add(translation);
    
    return result;
  }

  /**
   * Transform normal using DQS (rotation only)
   */
  public transformNormal(
    normal: THREE.Vector3,
    boneIndices: number[],
    boneWeights: number[]
  ): THREE.Vector3 {
    // Blend rotations only
    const blendedQ = new THREE.Quaternion(0, 0, 0, 0);
    const pivot = this.boneDualQuats[boneIndices[0]];
    
    for (let i = 0; i < 4; i++) {
      const weight = boneWeights[i];
      if (weight <= 0.0001) continue;
      
      const boneDQ = this.boneDualQuats[boneIndices[i]];
      
      const dot = 
        pivot.real.x * boneDQ.real.x +
        pivot.real.y * boneDQ.real.y +
        pivot.real.z * boneDQ.real.z +
        pivot.real.w * boneDQ.real.w;
      
      const sign = dot < 0 ? -1 : 1;
      
      blendedQ.x += sign * weight * boneDQ.real.x;
      blendedQ.y += sign * weight * boneDQ.real.y;
      blendedQ.z += sign * weight * boneDQ.real.z;
      blendedQ.w += sign * weight * boneDQ.real.w;
    }
    
    blendedQ.normalize();
    
    // Rotate normal
    const result = normal.clone();
    result.applyQuaternion(blendedQ);
    
    return result;
  }

  /**
   * Get shader uniforms for GPU skinning
   */
  public getShaderUniforms(): {
    boneDualQuatsReal: Float32Array;
    boneDualQuatsDual: Float32Array;
  } {
    const count = this.boneDualQuats.length;
    const real = new Float32Array(count * 4);
    const dual = new Float32Array(count * 4);
    
    for (let i = 0; i < count; i++) {
      const dq = this.boneDualQuats[i];
      real[i * 4] = dq.real.x;
      real[i * 4 + 1] = dq.real.y;
      real[i * 4 + 2] = dq.real.z;
      real[i * 4 + 3] = dq.real.w;
      dual[i * 4] = dq.dual.x;
      dual[i * 4 + 1] = dq.dual.y;
      dual[i * 4 + 2] = dq.dual.z;
      dual[i * 4 + 3] = dq.dual.w;
    }
    
    return {
      boneDualQuatsReal: real,
      boneDualQuatsDual: dual
    };
  }

  /**
   * Get vertex shader code for DQS
   */
  public static getVertexShaderGLSL(): string {
    return `
      // Dual Quaternion Skinning
      uniform vec4 boneDualQuatsReal[MAX_BONES];
      uniform vec4 boneDualQuatsDual[MAX_BONES];
      
      attribute vec4 skinIndex;
      attribute vec4 skinWeight;
      
      vec3 dqsTransform(vec3 position) {
        // Blend dual quaternions
        vec4 blendReal = vec4(0.0);
        vec4 blendDual = vec4(0.0);
        
        // Get pivot for antipodality check
        vec4 pivotReal = boneDualQuatsReal[int(skinIndex.x)];
        
        for (int i = 0; i < 4; i++) {
          int idx = int(skinIndex[i]);
          float weight = skinWeight[i];
          
          vec4 real = boneDualQuatsReal[idx];
          vec4 dual = boneDualQuatsDual[idx];
          
          // Antipodality check
          float sign = dot(pivotReal, real) < 0.0 ? -1.0 : 1.0;
          
          blendReal += sign * weight * real;
          blendDual += sign * weight * dual;
        }
        
        // Normalize
        float invLen = 1.0 / length(blendReal);
        blendReal *= invLen;
        blendDual *= invLen;
        
        // Transform position
        // Rotation: v' = q * v * q^-1
        vec3 t = 2.0 * (blendReal.w * blendDual.xyz - blendDual.w * blendReal.xyz + cross(blendReal.xyz, blendDual.xyz));
        vec3 rotated = position + 2.0 * cross(blendReal.xyz, cross(blendReal.xyz, position) + blendReal.w * position);
        
        return rotated + t;
      }
      
      vec3 dqsTransformNormal(vec3 normal) {
        // Same blending as position but only rotation
        vec4 blendReal = vec4(0.0);
        vec4 pivotReal = boneDualQuatsReal[int(skinIndex.x)];
        
        for (int i = 0; i < 4; i++) {
          int idx = int(skinIndex[i]);
          float weight = skinWeight[i];
          vec4 real = boneDualQuatsReal[idx];
          float sign = dot(pivotReal, real) < 0.0 ? -1.0 : 1.0;
          blendReal += sign * weight * real;
        }
        
        blendReal = normalize(blendReal);
        
        return normal + 2.0 * cross(blendReal.xyz, cross(blendReal.xyz, normal) + blendReal.w * normal);
      }
    `;
  }
}

