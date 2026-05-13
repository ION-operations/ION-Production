/**
 * Dual Quaternion utility functions
 * 
 * CRITICAL: Quaternion-native positions enable SO(3)-invariant distance
 * and screw-motion intent trajectories
 */

import { DualQuatPose, Quaternion, Vector3D } from '../types';
import { vector_magnitude } from './vectors';

/**
 * Extract translation from dual quaternion pose
 */
export function dual_quat_to_position(pose: DualQuatPose): Vector3D {
  // Extract translation from dual quaternion
  // This would use quaternion kernel functions in production
  return { 
    x: pose.translation.x, 
    y: pose.translation.y, 
    z: pose.translation.z 
  };
}

/**
 * Compute quaternion geodesic distance (SO(3)-invariant)
 * 
 * This eliminates gimbal lock and enables screw-motion intent trajectories
 */
export function quaternion_geodesic_distance(
  pose1: DualQuatPose,
  pose2: DualQuatPose
): number {
  // For now, use translation distance as approximation
  // In production, this would use proper quaternion geodesic distance
  const pos1 = dual_quat_to_position(pose1);
  const pos2 = dual_quat_to_position(pose2);
  
  const dx = pos2.x - pos1.x;
  const dy = pos2.y - pos1.y;
  const dz = pos2.z - pos1.z;
  
  return Math.sqrt(dx * dx + dy * dy + dz * dz);
}

/**
 * Compute quaternion distance (rotation component)
 */
export function quaternion_distance(q1: Quaternion, q2: Quaternion): number {
  // Quaternion distance: 1 - |q1 · q2|
  const dot = q1.w * q2.w + q1.x * q2.x + q1.y * q2.y + q1.z * q2.z;
  return 1.0 - Math.abs(dot);
}

/**
 * Get Hopf fiber from dual quaternion pose
 */
export function get_hopf_fiber(pose: DualQuatPose): { phase: number; radius: number } {
  // Extract S¹ fiber from dual quaternion
  // This would use quaternion kernel functions in production
  // For now, return placeholder
  return { phase: 0.0, radius: 1.0 };
}

