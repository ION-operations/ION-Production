//! AIM-OS 4D Quaternion-Native Scene Kernel
//!
//! This crate implements the foundational spatial indexing, quantum 
//! selection rules, and the four kernel syscalls.
//! It builds on the completed (Phase 1, Weeks 1-2) math library.
//!
//! - **morton**: Implements 4D Morton encoding/decoding
//! - **s3_binning**: Implements S³ orientation binning via Hopf factorization
//! - **quantum**: Implements the Quantum Kernel Address (QAddr) and selection rules
//! - **kernel**: Implements the four kernel syscalls (place, move, sense, emit)

use std::collections::HashMap;

// Math library primitives (from Phase 1, Weeks 1-2)
// TODO: Replace with actual quaternion math library bindings
mod math {
    #[derive(Debug, Clone, Copy, PartialEq)]
    pub struct Quat {
        pub w: f32,
        pub x: f32,
        pub y: f32,
        pub z: f32,
    }

    #[derive(Debug, Clone, Copy, PartialEq)]
    pub struct Vec4 {
        pub x: f32,
        pub y: f32,
        pub z: f32,
        pub tau: f32,
    }

    /// Dual quaternion for 3D rigid transformations (screw motion)
    #[derive(Debug, Clone, Copy, PartialEq)]
    pub struct DualQuat {
        pub rotation: Quat,
        pub translation: Quat, // Pure quaternion (w=0) representing translation
    }
}

pub mod morton;
pub mod s3_binning;
pub mod quantum;
pub mod kernel;
pub mod dual_quat_ops;
pub mod http_server;

// Re-export key types
pub use math::{Quat, Vec4, DualQuat};
pub use morton::{morton4d_encode, morton4d_decode, MortonKey};
pub use s3_binning::{s3_bin_encode, S3Bin, get_s3_neighbors};
pub use quantum::{
    QAddr, OrbitalClass, Spin, SelectionRules, validate_transition,
    PrincipalShell, MagneticChannel,
};
pub use kernel::{Kernel, EntityId, EntityState};
pub use dual_quat_ops::{recalculate_qaddr_from_pose};

/// The composite key for entity indexing
/// Combines the 64-bit Morton key with the 16-bit S³ orientation bin
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct CompositeKey(u128);

const S3_BIN_BITS: u32 = 16;

impl CompositeKey {
    /// Creates a new composite key from its spatial and orientation parts
    pub fn new(morton_key: MortonKey, s3_bin: S3Bin) -> Self {
        let key = ((morton_key.0 as u128) << S3_BIN_BITS) | (s3_bin.0 as u128);
        Self(key)
    }

    /// Extracts the MortonKey (spacetime location)
    pub fn morton_key(&self) -> MortonKey {
        MortonKey((self.0 >> S3_BIN_BITS) as u64)
    }

    /// Extracts the S3Bin (orientation cell)
    pub fn s3_bin(&self) -> S3Bin {
        S3Bin((self.0 & ((1 << S3_BIN_BITS) - 1)) as u16)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_composite_key() {
        let morton = MortonKey(0x1234567890ABCDEF);
        let s3 = S3Bin(0xABCD);
        let composite = CompositeKey::new(morton, s3);

        assert_eq!(composite.morton_key(), morton);
        assert_eq!(composite.s3_bin(), s3);
    }
}

