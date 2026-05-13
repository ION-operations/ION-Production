//! Dual quaternion operations for 3D rigid transformations
//! Implements screw motion composition and pose extraction

use crate::{Quat, DualQuat, Vec4, MortonKey, S3Bin, morton4d_encode, s3_bin_encode, QAddr};

/// Compose two dual quaternions (screw motion composition)
///
/// Formula: dq₁ * dq₂ = (q_r₁ * q_r₂) + ε * (q_r₁ * q_d₂ + q_d₁ * q_r₂)
///
/// RTFT: Composes two geometric transformations (vortex motions)
pub fn compose_dual_quat(dq1: &DualQuat, dq2: &DualQuat) -> DualQuat {
    // Rotation part: q_r₁ * q_r₂
    let new_rotation = multiply_quat(&dq1.rotation, &dq2.rotation);

    // Dual part: q_r₁ * q_d₂ + q_d₁ * q_r₂
    let term1 = multiply_quat(&dq1.rotation, &dq2.translation);
    let term2 = multiply_quat(&dq1.translation, &dq2.rotation);

    // Add dual parts component-wise (both are pure quaternions)
    let new_translation = Quat {
        w: 0.0, // Pure quaternion
        x: term1.x + term2.x,
        y: term1.y + term2.y,
        z: term1.z + term2.z,
    };

    DualQuat {
        rotation: new_rotation,
        translation: new_translation,
    }
}

/// Extract 3D position from dual quaternion pose
///
/// For dual quaternion dq = q_r + ε * q_d where q_d = 0.5 * q_r * t:
/// Translation t = 2 * q_r⁻¹ * q_d
///
/// Returns: (x, y, z) position tuple
pub fn extract_position_from_dual_quat(dq: &DualQuat) -> (f32, f32, f32) {
    // Compute q_r⁻¹
    let rot_inv = quat_inverse(&dq.rotation);

    // Compute q_r⁻¹ * q_d
    let temp = multiply_quat(&rot_inv, &dq.translation);

    // Extract translation: t = 2 * (q_r⁻¹ * q_d)
    // Since q_d is pure (w=0), temp will have w≈0, extract vector part
    (2.0 * temp.x, 2.0 * temp.y, 2.0 * temp.z)
}

/// Extract orientation quaternion from dual quaternion pose
///
/// Returns the rotation quaternion directly
pub fn extract_orientation_from_dual_quat(dq: &DualQuat) -> Quat {
    dq.rotation
}

/// Helper: Multiply two quaternions (Hamilton product)
fn multiply_quat(q1: &Quat, q2: &Quat) -> Quat {
    Quat {
        w: q1.w * q2.w - q1.x * q2.x - q1.y * q2.y - q1.z * q2.z,
        x: q1.w * q2.x + q1.x * q2.w + q1.y * q2.z - q1.z * q2.y,
        y: q1.w * q2.y - q1.x * q2.z + q1.y * q2.w + q1.z * q2.x,
        z: q1.w * q2.z + q1.x * q2.y - q1.y * q2.x + q1.z * q2.w,
    }
}

/// Helper: Compute quaternion inverse
fn quat_inverse(q: &Quat) -> Quat {
    let norm_sq = q.w * q.w + q.x * q.x + q.y * q.y + q.z * q.z;
    if norm_sq < 1e-10 {
        return Quat { w: 1.0, x: 0.0, y: 0.0, z: 0.0 }; // Identity
    }
    let inv_norm_sq = 1.0 / norm_sq;
    Quat {
        w: q.w * inv_norm_sq,
        x: -q.x * inv_norm_sq,
        y: -q.y * inv_norm_sq,
        z: -q.z * inv_norm_sq,
    }
}

/// Recalculate QAddr from dual quaternion pose
///
/// Extracts position and orientation from pose, then calculates:
/// - Morton4D key from position
/// - S³ bin from orientation
pub fn recalculate_qaddr_from_pose(
    pose: &DualQuat,
    current_time: f32, // τ (tau) for 4D spacetime
    old_addr: &QAddr, // Preserve quantum numbers (n, ℓ, s)
) -> QAddr {
    // Extract 3D position
    let (x, y, z) = extract_position_from_dual_quat(pose);

    // Create Vec4 with current time
    let pos = Vec4 {
        x,
        y,
        z,
        tau: current_time,
    };

    // Calculate Morton4D key
    let morton_key = morton4d_encode(&pos);

    // Extract orientation
    let orientation = extract_orientation_from_dual_quat(pose);

    // Calculate S³ bin
    let s3_bin = s3_bin_encode(&orientation);

    // Create new QAddr preserving quantum numbers but updating geometric state
    QAddr {
        n: old_addr.n,
        l: old_addr.l,
        m: crate::MagneticChannel(s3_bin),
        s: old_addr.s,
        morton_key,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_dual_quat_compose() {
        let dq1 = DualQuat {
            rotation: Quat { w: 1.0, x: 0.0, y: 0.0, z: 0.0 },
            translation: Quat { w: 0.0, x: 1.0, y: 0.0, z: 0.0 },
        };

        let dq2 = DualQuat {
            rotation: Quat { w: 1.0, x: 0.0, y: 0.0, z: 0.0 },
            translation: Quat { w: 0.0, x: 0.0, y: 1.0, z: 0.0 },
        };

        let composed = compose_dual_quat(&dq1, &dq2);
        
        // Composed translation should be sum of translations (for identity rotations)
        assert!((composed.translation.x - 1.0).abs() < 1e-5);
        assert!((composed.translation.y - 1.0).abs() < 1e-5);
    }

    #[test]
    fn test_extract_position() {
        let dq = DualQuat {
            rotation: Quat { w: 1.0, x: 0.0, y: 0.0, z: 0.0 },
            translation: Quat { w: 0.0, x: 0.5, y: 0.0, z: 0.0 }, // Represents translation (1, 0, 0)
        };

        let (x, y, z) = extract_position_from_dual_quat(&dq);
        
        // Should extract translation correctly
        assert!((x - 1.0).abs() < 1e-5);
        assert!(y.abs() < 1e-5);
        assert!(z.abs() < 1e-5);
    }

    #[test]
    fn test_extract_orientation() {
        let rot = Quat { w: 0.707, x: 0.707, y: 0.0, z: 0.0 };
        let dq = DualQuat {
            rotation: rot,
            translation: Quat { w: 0.0, x: 0.0, y: 0.0, z: 0.0 },
        };

        let extracted = extract_orientation_from_dual_quat(&dq);
        assert_eq!(extracted.w, rot.w);
        assert_eq!(extracted.x, rot.x);
    }
}

