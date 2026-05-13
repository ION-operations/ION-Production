//! Implements 4D Morton (Z-order) curve encoding for spatial indexing
//! This provides cache-coherent locality for 4D spacetime coordinates (x, y, z, τ)

use crate::math::Vec4;

/// A 64-bit Morton key representing an interleaved (x, y, z, τ) coordinate
/// Assumes each 16-bit coordinate is normalized to u16
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct MortonKey(pub u64);

/// Encodes a 4D position vector (x,y,z,τ) into a 64-bit Morton key
///
/// This function assumes the Vec4 components are in a normalized range [0.0, 1.0]
/// and maps them to u16 integers before interleaving.
///
/// Performance target: < 100ns per encode operation
pub fn morton4d_encode(pos: &Vec4) -> MortonKey {
    // Normalize and convert f32 to u16
    let x = (pos.x.max(0.0).min(1.0) * 65535.0) as u16;
    let y = (pos.y.max(0.0).min(1.0) * 65535.0) as u16;
    let z = (pos.z.max(0.0).min(1.0) * 65535.0) as u16;
    let tau = (pos.tau.max(0.0).min(1.0) * 65535.0) as u16;

    // Efficient bit-interleaving using lookup tables or magic bits
    // For now, using direct bit manipulation (can be optimized with lookup tables)
    let mut key: u64 = 0;

    // Interleave bits: x[15] y[15] z[15] τ[15] x[14] y[14] z[14] τ[14] ...
    for i in 0..16 {
        let shift = 15 - i;
        key |= ((x as u64 >> shift) & 1) << (4 * i + 3);
        key |= ((y as u64 >> shift) & 1) << (4 * i + 2);
        key |= ((z as u64 >> shift) & 1) << (4 * i + 1);
        key |= ((tau as u64 >> shift) & 1) << (4 * i + 0);
    }

    MortonKey(key)
}

/// Decodes a 64-bit Morton key back into a 4D position vector (x,y,z,τ)
///
/// The resulting Vec4 components will be in the normalized range [0.0, 1.0]
///
/// Performance target: < 100ns per decode operation
pub fn morton4d_decode(key: MortonKey) -> Vec4 {
    let mut x: u16 = 0;
    let mut y: u16 = 0;
    let mut z: u16 = 0;
    let mut tau: u16 = 0;

    // Deinterleave bits
    for i in 0..16 {
        let shift = 15 - i;
        x |= (((key.0 >> (4 * i + 3)) & 1) as u16) << shift;
        y |= (((key.0 >> (4 * i + 2)) & 1) as u16) << shift;
        z |= (((key.0 >> (4 * i + 1)) & 1) as u16) << shift;
        tau |= (((key.0 >> (4 * i + 0)) & 1) as u16) << shift;
    }

    Vec4 {
        x: x as f32 / 65535.0,
        y: y as f32 / 65535.0,
        z: z as f32 / 65535.0,
        tau: tau as f32 / 65535.0,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_morton_round_trip() {
        let pos = Vec4 {
            x: 0.5,
            y: 0.25,
            z: 0.75,
            tau: 0.125,
        };

        let encoded = morton4d_encode(&pos);
        let decoded = morton4d_decode(encoded);

        // Allow for small floating-point errors
        assert!((decoded.x - pos.x).abs() < 1e-3);
        assert!((decoded.y - pos.y).abs() < 1e-3);
        assert!((decoded.z - pos.z).abs() < 1e-3);
        assert!((decoded.tau - pos.tau).abs() < 1e-3);
    }

    #[test]
    fn test_morton_determinism() {
        let pos = Vec4 {
            x: 0.123,
            y: 0.456,
            z: 0.789,
            tau: 0.321,
        };

        let key1 = morton4d_encode(&pos);
        let key2 = morton4d_encode(&pos);

        assert_eq!(key1, key2, "Morton encoding must be deterministic");
    }

    #[test]
    fn test_morton_spatial_locality() {
        // Test that nearby points produce nearby keys
        let pos1 = Vec4 {
            x: 0.5,
            y: 0.5,
            z: 0.5,
            tau: 0.5,
        };

        let pos2 = Vec4 {
            x: 0.5001,
            y: 0.5,
            z: 0.5,
            tau: 0.5,
        };

        let key1 = morton4d_encode(&pos1);
        let key2 = morton4d_encode(&pos2);

        // Keys should be close (small difference)
        let diff = if key1.0 > key2.0 {
            key1.0 - key2.0
        } else {
            key2.0 - key1.0
        };

        // Difference should be small (within reasonable bounds)
        assert!(diff < 1000, "Nearby points should produce nearby keys");
    }

    #[test]
    fn test_morton_boundaries() {
        // Test boundary conditions
        let min_pos = Vec4 {
            x: 0.0,
            y: 0.0,
            z: 0.0,
            tau: 0.0,
        };

        let max_pos = Vec4 {
            x: 1.0,
            y: 1.0,
            z: 1.0,
            tau: 1.0,
        };

        let min_key = morton4d_encode(&min_pos);
        let max_key = morton4d_encode(&max_pos);

        assert!(min_key.0 < max_key.0, "Min should be less than max");
    }
}

