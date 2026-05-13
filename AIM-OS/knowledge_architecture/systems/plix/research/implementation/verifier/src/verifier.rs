//! Main verifier
//!
//! This module implements the main verification algorithm:
//! - Hash chain verification
//! - Signature verification
//! - Constraint replay
//! - Evidence completeness

use std::collections::HashMap;
use ed25519_dalek::PublicKey;
use crate::types::{EvidenceDAG, VerificationResult, VerificationError};
use crate::hash_chain::verify_hash_chain;
use crate::signature::verify_signature_with_keys;
use crate::constraint_replay::replay_constraint;
use crate::evidence_completeness::{verify_evidence_completeness, Contract};

/// Intent definition (simplified)
pub struct Intent {
    pub id: String,
    pub contract: Contract,
}

/// Verify intent
///
/// Main verification algorithm:
/// 1. Verify hash chain
/// 2. Verify signatures
/// 3. Replay constraints
/// 4. Verify evidence completeness
pub fn verify(
    intent: &Intent,
    evidence_dag: &EvidenceDAG,
    trusted_keys: &HashMap<String, PublicKey>,
) -> Result<VerificationResult, VerificationError> {
    // Step 1: Verify hash chain
    verify_hash_chain(evidence_dag)
        .map_err(|e| VerificationError::from(e))?;
    
    // Step 2: Verify signatures
    for node in &evidence_dag.nodes {
        verify_signature_with_keys(node, trusted_keys)
            .map_err(|e| VerificationError::InvalidSignature {
                node: node.id.clone(),
            })?;
    }
    
    // Step 3: Replay precondition constraints
    for precondition in &intent.contract.preconditions {
        let result = replay_constraint(precondition, evidence_dag)
            .map_err(|_| VerificationError::PreconditionFailed {
                precondition: precondition.clone(),
            })?;
        
        if !result {
            return Err(VerificationError::PreconditionFailed {
                precondition: precondition.clone(),
            });
        }
    }
    
    // Step 4: Replay postcondition constraints
    for postcondition in &intent.contract.postconditions {
        let result = replay_constraint(postcondition, evidence_dag)
            .map_err(|_| VerificationError::PostconditionFailed {
                postcondition: postcondition.clone(),
            })?;
        
        if !result {
            return Err(VerificationError::PostconditionFailed {
                postcondition: postcondition.clone(),
            });
        }
    }
    
    // Step 5: Verify evidence completeness
    verify_evidence_completeness(&intent.contract, evidence_dag)
        .map_err(|e| match e {
            crate::evidence_completeness::CompletenessError::MissingPreconditionEvidence(p) => {
                VerificationError::MissingPreconditionEvidence { precondition: p }
            }
            crate::evidence_completeness::CompletenessError::MissingPostconditionEvidence(p) => {
                VerificationError::MissingPostconditionEvidence { postcondition: p }
            }
            _ => VerificationError::InvalidSignature { node: "unknown".to_string() },
        })?;
    
    // Success: Return verification result
    Ok(VerificationResult::Pass {
        preconditions: intent.contract.preconditions.len(),
        postconditions: intent.contract.postconditions.len(),
        evidence_nodes: evidence_dag.nodes.len(),
        evidence_edges: evidence_dag.edges.len(),
    })
}

/// Convert HashChainError to VerificationError
impl From<crate::hash_chain::HashChainError> for VerificationError {
    fn from(e: crate::hash_chain::HashChainError) -> Self {
        match e {
            crate::hash_chain::HashChainError::DuplicateId(id) => {
                VerificationError::DuplicateId(id)
            }
            crate::hash_chain::HashChainError::ParentNotFound { node, parent } => {
                VerificationError::ParentNotFound { node, parent }
            }
            crate::hash_chain::HashChainError::ParentHashMismatch { node, expected, actual } => {
                VerificationError::HashMismatch { node, expected, actual }
            }
            crate::hash_chain::HashChainError::NodeHashMismatch { node, expected, actual } => {
                VerificationError::NodeHashMismatch { node, expected, actual }
            }
            _ => VerificationError::InvalidSignature { node: "unknown".to_string() },
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::types::{EvidenceNode, EvidenceDAG, EvidenceEdge};
    use ed25519_dalek::{Keypair, Signer as Ed25519Signer};
    use rand::rngs::OsRng;

    #[test]
    fn test_verify_simple_intent() {
        let mut csprng = OsRng{};
        let keypair: Keypair = Keypair::generate(&mut csprng);
        
        let mut dag = EvidenceDAG::new();
        
        // Create source node
        let mut source = EvidenceNode::new(
            "source".to_string(),
            None,
            None,
            "service".to_string(),
            "input".to_string(),
            "output".to_string(),
            None,
            Vec::new(),
            "signer1".to_string(),
            "sig1".to_string(),
        );
        
        // Sign source node
        let message = format!(
            "{}:{}:{}:{}:{}",
            source.id,
            source.time.to_rfc3339(),
            source.tool,
            source.input_hash,
            source.output_hash
        );
        let signature = keypair.sign(message.as_bytes());
        source.sig = hex::encode(signature.to_bytes());
        source.content = Some("precondition1 == true".to_string());
        
        let source_id = source.id.clone();
        dag.add_node(source);
        
        // Create claim node
        let mut claim = EvidenceNode::new(
            "claim".to_string(),
            None,
            None,
            "checker".to_string(),
            "input".to_string(),
            "output".to_string(),
            None,
            vec![source_id.clone()],
            "signer1".to_string(),
            "sig1".to_string(),
        );
        
        // Sign claim node
        let message = format!(
            "{}:{}:{}:{}:{}",
            claim.id,
            claim.time.to_rfc3339(),
            claim.tool,
            claim.input_hash,
            claim.output_hash
        );
        let signature = keypair.sign(message.as_bytes());
        claim.sig = hex::encode(signature.to_bytes());
        claim.content = Some("precondition1 == true".to_string());
        claim.result = Some(true);
        
        let claim_id = claim.id.clone();
        dag.add_node(claim);
        
        // Add edge
        let edge = EvidenceEdge::new(
            "supports".to_string(),
            source_id,
            claim_id,
            Some(1.0),
            None,
        );
        dag.add_edge(edge);
        
        // Create intent
        let intent = Intent {
            id: "test_intent".to_string(),
            contract: Contract {
                preconditions: vec!["precondition1 == true".to_string()],
                postconditions: vec![],
            },
        };
        
        // Create trusted keys
        let mut trusted_keys = HashMap::new();
        trusted_keys.insert("signer1".to_string(), keypair.public);
        
        // Verify
        let result = verify(&intent, &dag, &trusted_keys);
        assert!(result.is_ok());
        
        if let Ok(VerificationResult::Pass { preconditions, .. }) = result {
            assert_eq!(preconditions, 1);
        }
    }
}


