//! Implements the Quantum Kernel Address (QAddr) and selection rules
//! This provides the security and state model for all kernel entities,
//! generalizing Multics rings to quantum-style invariants

use crate::{MortonKey, S3Bin};

/// Principal shell (n): Trust/privilege tier
/// n=0 is kernel, n=1 is drivers, n=2 is services, n>=3 is userland
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub struct PrincipalShell(pub u8);

/// Orbital class (ℓ): Capability class
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub enum OrbitalClass {
    Memory,     // ℓ=0
    Io,         // ℓ=1
    Network,    // ℓ=2
    Model,      // ℓ=3
    Crypto,     // ℓ=4
    Ui,         // ℓ=5
    Governance, // ℓ=6
}

/// Magnetic number (m): Orientation channel / S³ cone
/// This is represented by the S3Bin itself
pub type MagneticChannel = S3Bin;

/// Spin (s): Chirality / authority mode
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub enum Spin {
    Read,
    Write,
    Plan,
    Act,
}

/// Quantum Kernel Address (QAddr)
/// The complete geometric and quantum state of an entity
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct QAddr {
    pub n: PrincipalShell,   // 1s, 2s, 2p...
    pub l: OrbitalClass,     // s, p, d, f...
    pub m: MagneticChannel,  // S³ bin
    pub s: Spin,             // +/- 1/2
    pub morton_key: MortonKey, // Spacetime (x,y,z,τ)
}

/// Defines the allowed deltas for a state transition
#[derive(Debug, Clone, Copy)]
pub struct SelectionRules {
    pub delta_n: i8,  // Allowed change in principal shell (e.g., 0, +/-1)
    pub delta_l: bool, // True if ℓ can change (e.g., ℓ=0 -> ℓ=1)
    pub delta_m: bool, // True if m (orientation) can change
    pub delta_s: bool, // True if spin mode can change (e.g., Read -> Write)
}

/// Validates a state transition against a set of selection rules
/// This is the core security check for all kernel syscalls
///
/// Performance target: < 50ns per validation
pub fn validate_transition(
    from: &QAddr,
    to: &QAddr,
    rules: &SelectionRules,
) -> Result<(), &'static str> {
    // 1. Check Principal Shell (n) transition
    let n_diff = to.n.0 as i8 - from.n.0 as i8;
    if n_diff.abs() > rules.delta_n.abs() {
        // e.g., if rule is +/-1, a jump of +/-2 is forbidden
        // A jump of 0 is always allowed if delta_n >= 0
        if n_diff != 0 {
            return Err("Forbidden transition between principal shells (Δn violation)");
        }
    }
    // TODO: Add nuance for "stimulus" jumps (Δn > 1) requiring VIF/Quorum

    // 2. Check Orbital Class (ℓ) transition
    if from.l != to.l && !rules.delta_l {
        return Err("Forbidden transition between capability classes (Δℓ violation)");
    }

    // 3. Check Magnetic Channel (m) transition
    if from.m != to.m && !rules.delta_m {
        // A more complex check would see if to.m is in the S³ neighbor list of from.m
        return Err("Forbidden transition between orientation channels (Δm violation)");
    }

    // 4. Check Spin (s) transition
    if from.s != to.s && !rules.delta_s {
        return Err("Forbidden transition between spin modes (Δs violation)");
    }

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_selection_rules_valid_transition() {
        let from = QAddr {
            n: PrincipalShell(1),
            l: OrbitalClass::Memory,
            m: S3Bin(100),
            s: Spin::Read,
            morton_key: MortonKey(0),
        };

        let to = QAddr {
            n: PrincipalShell(1), // Same shell
            l: OrbitalClass::Io,  // Different class
            m: S3Bin(100),        // Same orientation
            s: Spin::Read,        // Same spin
            morton_key: MortonKey(0),
        };

        let rules = SelectionRules {
            delta_n: 0,
            delta_l: true,  // Allowed to change
            delta_m: false,
            delta_s: false,
        };

        assert!(
            validate_transition(&from, &to, &rules).is_ok(),
            "Valid transition should pass"
        );
    }

    #[test]
    fn test_selection_rules_invalid_delta_n() {
        let from = QAddr {
            n: PrincipalShell(1),
            l: OrbitalClass::Memory,
            m: S3Bin(100),
            s: Spin::Read,
            morton_key: MortonKey(0),
        };

        let to = QAddr {
            n: PrincipalShell(3), // Jump of 2
            l: OrbitalClass::Memory,
            m: S3Bin(100),
            s: Spin::Read,
            morton_key: MortonKey(0),
        };

        let rules = SelectionRules {
            delta_n: 1, // Only allow +/-1
            delta_l: false,
            delta_m: false,
            delta_s: false,
        };

        assert!(
            validate_transition(&from, &to, &rules).is_err(),
            "Invalid Δn transition should fail"
        );
    }

    #[test]
    fn test_selection_rules_invalid_delta_l() {
        let from = QAddr {
            n: PrincipalShell(1),
            l: OrbitalClass::Memory,
            m: S3Bin(100),
            s: Spin::Read,
            morton_key: MortonKey(0),
        };

        let to = QAddr {
            n: PrincipalShell(1),
            l: OrbitalClass::Network, // Different class
            m: S3Bin(100),
            s: Spin::Read,
            morton_key: MortonKey(0),
        };

        let rules = SelectionRules {
            delta_n: 0,
            delta_l: false, // Not allowed to change
            delta_m: false,
            delta_s: false,
        };

        assert!(
            validate_transition(&from, &to, &rules).is_err(),
            "Invalid Δℓ transition should fail"
        );
    }
}

