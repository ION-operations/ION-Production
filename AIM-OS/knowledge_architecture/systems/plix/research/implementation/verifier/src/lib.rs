//! Evidence Verifier for Core-PLIx Semantics v0.1
//!
//! This module implements an evidence verifier for Core-PLIx based on
//! the formal semantics defined in `core_semantics_v01_final.md`.
//!
//! # Architecture
//!
//! - **Hash Chain**: Hash chain verification (DAG structure, parent hash validation)
//! - **Signature**: Signature verification (cryptographic signature validation)
//! - **Constraint Replay**: Pure constraint replay (deterministic constraint re-evaluation)
//! - **Evidence Completeness**: Evidence completeness check (all postconditions supported)
//! - **Verifier**: Main verifier algorithm
//!
//! # Example
//!
//! ```rust
//! use plix_verifier::*;
//!
//! let intent = parse_intent("...")?;
//! let evidence_dag = load_evidence_dag("...")?;
//! let resolver = Resolver::new();
//! let trusted_keys = load_trusted_keys("...")?;
//!
//! let result = verify(&intent, &evidence_dag, &resolver, &trusted_keys)?;
//! ```

pub mod types;
pub mod hash_chain;
pub mod signature;
pub mod constraint_replay;
pub mod evidence_completeness;
pub mod verifier;

pub use types::{EvidenceDAG, EvidenceNode, EvidenceEdge, VerificationResult, VerificationError};
pub use verifier::{verify, Intent};
pub use hash_chain::verify_hash_chain;
pub use signature::{verify_signature, verify_signature_with_keys, verify_quorum_signature, QuorumSignature};
pub use constraint_replay::replay_constraint;
pub use evidence_completeness::{verify_evidence_completeness, Contract};

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_basic_verification() {
        // TODO: Implement basic verification test
    }
}

