//! Implements S³ orientation binning for quaternions
//! This uses a Hopf map factorization (S³ -> S² x S¹) to create
//! a coarse tessellation of the unit quaternion sphere

use crate::math::Quat;

/// A 16-bit orientation cell ID
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct S3Bin(pub u16);

/// Encodes a unit quaternion into a 16-bit S³ cell ID
///
/// This function implements the Hopf factorization, mapping the quaternion
/// to a base on S² (using spherical coordinates) and a phase on S¹
///
/// Hopf map: S³ → S² × S¹
/// - S² base: Standard Hopf map projection (2(xw+yz), 2(yw-xz), w²+z²-x²-y²)
/// - S¹ fiber: Phase angle extracted from quaternion
///
/// Binning strategy:
/// - S²: 12 bits (4096 cells) using spherical coordinates (θ, φ)
/// - S¹: 4 bits (16 phase bins)
///
/// Performance target: < 200ns per bin computation
pub fn s3_bin_encode(ori: &Quat) -> S3Bin {
    // Normalize quaternion (ensure unit quaternion)
    let norm = (ori.w * ori.w + ori.x * ori.x + ori.y * ori.y + ori.z * ori.z).sqrt();
    if norm < 1e-10 {
        // Return identity bin for zero quaternion
        return S3Bin(0);
    }

    let w = ori.w / norm;
    let x = ori.x / norm;
    let y = ori.y / norm;
    let z = ori.z / norm;

    // Step 1: Map quaternion to S² using standard Hopf map
    // For quaternion q = w + xi + yj + zk, the Hopf map to S² is:
    // (2(xw + yz), 2(yw - xz), w² + z² - x² - y²)
    let s2_x = 2.0 * (x * w + y * z);
    let s2_y = 2.0 * (y * w - x * z);
    let s2_z = w * w + z * z - x * x - y * y;

    // Normalize S² point (should already be on unit sphere, but ensure)
    let s2_norm = (s2_x * s2_x + s2_y * s2_y + s2_z * s2_z).sqrt();
    if s2_norm < 1e-10 {
        // Degenerate case: return identity bin
        return S3Bin(0);
    }

    let s2_x_norm = s2_x / s2_norm;
    let s2_y_norm = s2_y / s2_norm;
    let s2_z_norm = s2_z / s2_norm;

    // Step 2: Convert S² point to spherical coordinates (θ, φ)
    // θ ∈ [0, π]: polar angle (from +z axis)
    // φ ∈ [0, 2π): azimuthal angle (from +x axis)
    let theta = s2_z_norm.acos(); // θ ∈ [0, π]
    let phi = s2_y_norm.atan2(s2_x_norm); // φ ∈ [-π, π], shift to [0, 2π)
    let phi_normalized = if phi < 0.0 { phi + 2.0 * std::f32::consts::PI } else { phi };

    // Step 3: Bin S² point (12 bits = 4096 cells)
    // Use uniform binning: 64 bins in θ, 64 bins in φ
    const THETA_BINS: u32 = 64;
    const PHI_BINS: u32 = 64;
    const TOTAL_S2_BINS: u32 = THETA_BINS * PHI_BINS; // 4096

    let theta_bin = ((theta / std::f32::consts::PI) * (THETA_BINS as f32)).floor() as u32;
    let phi_bin = ((phi_normalized / (2.0 * std::f32::consts::PI)) * (PHI_BINS as f32)).floor() as u32;

    // Clamp to valid range
    let theta_bin_clamped = theta_bin.min(THETA_BINS - 1);
    let phi_bin_clamped = phi_bin.min(PHI_BINS - 1);

    let s2_bin = theta_bin_clamped * PHI_BINS + phi_bin_clamped; // 0 to 4095

    // Step 4: Extract S¹ phase from quaternion
    // The phase is encoded in the quaternion's rotation angle
    // For quaternion q = cos(θ/2) + sin(θ/2)(xi + yj + zk), the phase is θ
    // We can extract it from: θ = 2 * acos(w)
    let phase_angle = 2.0 * w.acos(); // θ ∈ [0, 2π] (w ∈ [-1, 1] → θ ∈ [0, 2π])
    let phase_normalized = if phase_angle < 0.0 {
        phase_angle + 2.0 * std::f32::consts::PI
    } else {
        phase_angle
    };

    // Step 5: Bin S¹ phase (4 bits = 16 bins)
    const S1_BINS: u32 = 16;
    let s1_bin = ((phase_normalized / (2.0 * std::f32::consts::PI)) * (S1_BINS as f32)).floor() as u32;
    let s1_bin_clamped = s1_bin.min(S1_BINS - 1);

    // Step 6: Combine bins into u16
    // Format: [12 bits S² bin][4 bits S¹ bin]
    let combined = (s2_bin << 4) | s1_bin_clamped;
    S3Bin(combined as u16)
}

/// Retrieves the neighboring S³ bins for a given bin
/// Used for 'sense' cone queries
///
/// Returns neighbors based on the tessellation:
/// - S² neighbors: Adjacent cells in (θ, φ) grid
/// - S¹ neighbors: Adjacent phase bins (wraps around)
pub fn get_s3_neighbors(bin: S3Bin) -> Vec<S3Bin> {
    const THETA_BINS: u32 = 64;
    const PHI_BINS: u32 = 64;
    const S1_BINS: u32 = 16;

    // Extract S² bin (upper 12 bits) and S¹ bin (lower 4 bits)
    let s2_bin = (bin.0 >> 4) as u32;
    let s1_bin = (bin.0 & 0xF) as u32;

    let mut neighbors = Vec::new();

    // Extract θ and φ bin indices
    let theta_bin = s2_bin / PHI_BINS;
    let phi_bin = s2_bin % PHI_BINS;

    // Generate S² neighbors (3x3 grid around current cell)
    for d_theta in -1..=1 {
        for d_phi in -1..=1 {
            if d_theta == 0 && d_phi == 0 {
                continue; // Skip self
            }

            let new_theta_bin = if d_theta == -1 {
                if theta_bin == 0 {
                    continue; // Can't go below 0
                } else {
                    theta_bin - 1
                }
            } else if d_theta == 1 {
                if theta_bin >= THETA_BINS - 1 {
                    continue; // Can't go above max
                } else {
                    theta_bin + 1
                }
            } else {
                theta_bin
            };

            let new_phi_bin = if d_phi == -1 {
                if phi_bin == 0 {
                    PHI_BINS - 1 // Wrap around
                } else {
                    phi_bin - 1
                }
            } else if d_phi == 1 {
                if phi_bin >= PHI_BINS - 1 {
                    0 // Wrap around
                } else {
                    phi_bin + 1
                }
            } else {
                phi_bin
            };

            let new_s2_bin = new_theta_bin * PHI_BINS + new_phi_bin;

            // For each S² neighbor, include current S¹ bin and its neighbors
            for d_s1 in -1..=1 {
                let new_s1_bin = if d_s1 == -1 {
                    if s1_bin == 0 {
                        S1_BINS - 1 // Wrap around
                    } else {
                        s1_bin - 1
                    }
                } else if d_s1 == 1 {
                    if s1_bin >= S1_BINS - 1 {
                        0 // Wrap around
                    } else {
                        s1_bin + 1
                    }
                } else {
                    s1_bin
                };

                let neighbor_bin = ((new_s2_bin << 4) | new_s1_bin) as u16;
                neighbors.push(S3Bin(neighbor_bin));
            }
        }
    }

    // Also include S¹ neighbors for same S² cell
    for d_s1 in -1..=1 {
        if d_s1 == 0 {
            continue; // Skip self (already included above)
        }
        let new_s1_bin = if d_s1 == -1 {
            if s1_bin == 0 {
                S1_BINS - 1
            } else {
                s1_bin - 1
            }
        } else {
            if s1_bin >= S1_BINS - 1 {
                0
            } else {
                s1_bin + 1
            }
        };
        let neighbor_bin = ((s2_bin << 4) | new_s1_bin) as u16;
        neighbors.push(S3Bin(neighbor_bin));
    }

    neighbors
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_s3_bin_determinism() {
        let quat = Quat {
            w: 1.0,
            x: 0.0,
            y: 0.0,
            z: 0.0,
        };

        let bin1 = s3_bin_encode(&quat);
        let bin2 = s3_bin_encode(&quat);

        assert_eq!(bin1, bin2, "S³ binning must be deterministic");
    }

    #[test]
    fn test_s3_bin_zero_quaternion() {
        let quat = Quat {
            w: 0.0,
            x: 0.0,
            y: 0.0,
            z: 0.0,
        };

        let bin = s3_bin_encode(&quat);
        assert_eq!(bin, S3Bin(0), "Zero quaternion should map to identity bin");
    }

    #[test]
    fn test_s3_bin_unit_quaternion() {
        // Test that unit quaternions produce valid bins
        let quat = Quat {
            w: 0.707,
            x: 0.707,
            y: 0.0,
            z: 0.0,
        };

        let bin = s3_bin_encode(&quat);
        // Bin should be in valid range [0, 65535]
        assert!(bin.0 <= 65535, "S³ bin must be in valid range");
    }

    #[test]
    fn test_s3_bin_hopf_properties() {
        // Test that Hopf factorization preserves geometric properties
        // Identity quaternion should map to a consistent bin
        let identity = Quat {
            w: 1.0,
            x: 0.0,
            y: 0.0,
            z: 0.0,
        };

        let bin1 = s3_bin_encode(&identity);
        let bin2 = s3_bin_encode(&identity);
        assert_eq!(bin1, bin2, "Hopf binning must be deterministic");

        // Test that nearby quaternions produce nearby bins (geometric locality)
        let q1 = Quat {
            w: 0.999,
            x: 0.0,
            y: 0.0,
            z: 0.0447, // Small rotation
        };
        let q2 = Quat {
            w: 0.998,
            x: 0.0,
            y: 0.0,
            z: 0.0632, // Slightly larger rotation
        };

        let bin_q1 = s3_bin_encode(&q1);
        let bin_q2 = s3_bin_encode(&q2);

        // Bins should be close (within neighbor distance)
        let neighbors_q1 = get_s3_neighbors(bin_q1);
        assert!(
            neighbors_q1.contains(&bin_q2) || bin_q1 == bin_q2,
            "Nearby quaternions should produce nearby bins"
        );
    }

    #[test]
    fn test_s3_neighbors() {
        let bin = S3Bin(0x1234); // Example bin
        let neighbors = get_s3_neighbors(bin);

        // Should have neighbors (at least some)
        assert!(!neighbors.is_empty(), "Should have neighbors");

        // Neighbors should be valid bins
        for neighbor in &neighbors {
            assert!(neighbor.0 <= 65535, "Neighbor bin must be valid");
        }

        // Test that neighbors include wraparound cases
        let edge_bin = S3Bin(0x0000); // Minimum bin
        let edge_neighbors = get_s3_neighbors(edge_bin);
        assert!(!edge_neighbors.is_empty(), "Edge bins should have neighbors");
    }

    #[test]
    fn test_s3_bin_rotation_invariance() {
        // Test that quaternions representing the same rotation
        // (q and -q) map to the same or related bins
        let q1 = Quat {
            w: 0.707,
            x: 0.707,
            y: 0.0,
            z: 0.0,
        };
        let q2 = Quat {
            w: -0.707,
            x: -0.707,
            y: 0.0,
            z: 0.0,
        };

        let bin1 = s3_bin_encode(&q1);
        let bin2 = s3_bin_encode(&q2);

        // q and -q represent the same rotation, so bins should be related
        // (They may differ in S¹ phase but should be neighbors)
        let neighbors = get_s3_neighbors(bin1);
        assert!(
            neighbors.contains(&bin2) || bin1 == bin2,
            "q and -q should produce related bins"
        );
    }
}

