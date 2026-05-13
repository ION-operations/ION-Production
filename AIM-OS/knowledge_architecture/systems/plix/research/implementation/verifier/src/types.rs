//! Core types for Core-PLIx verifier
//!
//! This module defines the fundamental types used throughout the verifier:
//! - EvidenceDAG: Evidence DAG structure
//! - EvidenceNode: Individual evidence node
//! - VerificationResult: Verification result
//! - VerificationError: Verification errors

use std::collections::{HashMap, HashSet};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

/// Evidence DAG: Graph structure for evidence
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EvidenceDAG {
    /// Nodes in the DAG
    pub nodes: Vec<EvidenceNode>,
    /// Edges in the DAG: (from, to, edge_type)
    pub edges: Vec<EvidenceEdge>,
}

impl EvidenceDAG {
    /// Create new evidence DAG
    pub fn new() -> Self {
        Self {
            nodes: Vec::new(),
            edges: Vec::new(),
        }
    }

    /// Get node by ID
    pub fn get_node(&self, id: &str) -> Option<&EvidenceNode> {
        self.nodes.iter().find(|n| n.id == id)
    }

    /// Get node by ID (mutable)
    pub fn get_node_mut(&mut self, id: &str) -> Option<&mut EvidenceNode> {
        self.nodes.iter_mut().find(|n| n.id == id)
    }

    /// Add node
    pub fn add_node(&mut self, node: EvidenceNode) {
        self.nodes.push(node);
    }

    /// Add edge
    pub fn add_edge(&mut self, edge: EvidenceEdge) {
        self.edges.push(edge);
    }
}

impl Default for EvidenceDAG {
    fn default() -> Self {
        Self::new()
    }
}

/// Evidence node
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EvidenceNode {
    /// Unique identifier
    pub id: String,
    /// Node type: "source" | "claim" | "derivation" | "proof"
    #[serde(rename = "type")]
    pub node_type: String,
    /// Step ID (if applicable)
    pub step_id: Option<String>,
    /// Contract ID (if applicable)
    pub contract_id: Option<String>,
    /// Timestamp
    pub time: DateTime<Utc>,
    /// Tool identifier
    pub tool: String,
    /// Input hash
    pub input_hash: String,
    /// Output hash
    pub output_hash: String,
    /// Previous hash (for hash-chaining)
    pub previous_hash: Option<String>,
    /// Parent evidence IDs
    pub parents: Vec<String>,
    /// Signer identifier
    pub signer: String,
    /// Cryptographic signature
    pub sig: String,
    /// Content (for claims/proofs)
    pub content: Option<String>,
    /// Result (for proofs)
    pub result: Option<bool>,
    /// Hash of this node
    pub hash: String,
}

impl EvidenceNode {
    /// Create new evidence node
    pub fn new(
        node_type: String,
        step_id: Option<String>,
        contract_id: Option<String>,
        tool: String,
        input_hash: String,
        output_hash: String,
        previous_hash: Option<String>,
        parents: Vec<String>,
        signer: String,
        sig: String,
    ) -> Self {
        let id = Uuid::new_v4().to_string();
        let hash = Self::compute_hash(&id, &tool, &input_hash, &output_hash, &previous_hash);
        
        Self {
            id,
            node_type,
            step_id,
            contract_id,
            time: Utc::now(),
            tool,
            input_hash,
            output_hash,
            previous_hash,
            parents,
            signer,
            sig,
            content: None,
            result: None,
            hash,
        }
    }

    /// Compute hash of this node
    pub fn compute_hash(
        id: &str,
        tool: &str,
        input_hash: &str,
        output_hash: &str,
        previous_hash: &Option<String>,
    ) -> String {
        use sha2::{Sha256, Digest};
        let mut hasher = Sha256::new();
        hasher.update(id.as_bytes());
        hasher.update(tool.as_bytes());
        hasher.update(input_hash.as_bytes());
        hasher.update(output_hash.as_bytes());
        if let Some(ref parent) = previous_hash {
            hasher.update(parent.as_bytes());
        }
        format!("{:x}", hasher.finalize())
    }
}

/// Evidence edge
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EvidenceEdge {
    /// Unique identifier
    pub id: String,
    /// Edge type: "supports" | "derives" | "witnesses"
    #[serde(rename = "type")]
    pub edge_type: String,
    /// From node ID
    pub from: String,
    /// To node ID
    pub to: String,
    /// Strength (for supports/derives)
    pub strength: Option<f64>,
    /// VIF hash (for witnesses)
    pub vif_hash: Option<String>,
    /// Timestamp
    pub time: DateTime<Utc>,
}

impl EvidenceEdge {
    /// Create new evidence edge
    pub fn new(
        edge_type: String,
        from: String,
        to: String,
        strength: Option<f64>,
        vif_hash: Option<String>,
    ) -> Self {
        Self {
            id: Uuid::new_v4().to_string(),
            edge_type,
            from,
            to,
            strength,
            vif_hash,
            time: Utc::now(),
        }
    }
}

/// Verification result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum VerificationResult {
    /// Verification passed
    Pass {
        /// Number of preconditions verified
        preconditions: usize,
        /// Number of postconditions verified
        postconditions: usize,
        /// Number of evidence nodes
        evidence_nodes: usize,
        /// Number of evidence edges
        evidence_edges: usize,
    },
    /// Verification failed
    Fail {
        /// Error description
        error: String,
    },
}

/// Verification error
#[derive(Debug, Clone, thiserror::Error)]
pub enum VerificationError {
    #[error("Duplicate node ID: {0}")]
    DuplicateId(String),
    
    #[error("Parent not found: node={0}, parent={1}")]
    ParentNotFound { node: String, parent: String },
    
    #[error("Hash mismatch: node={0}, expected={1}, actual={2}")]
    HashMismatch { node: String, expected: String, actual: String },
    
    #[error("Node hash mismatch: node={0}, expected={1}, actual={2}")]
    NodeHashMismatch { node: String, expected: String, actual: String },
    
    #[error("Invalid signature: node={0}")]
    InvalidSignature { node: String },
    
    #[error("Signature error: {0}")]
    SignatureError(String),
    
    #[error("Quorum not met: required={0}, actual={1}")]
    QuorumNotMet { required: usize, actual: usize },
    
    #[error("Constraint mismatch: constraint={0}, expected={1}, actual={2}")]
    ConstraintMismatch { constraint: String, expected: bool, actual: bool },
    
    #[error("Missing evidence: variable={0}")]
    MissingEvidence { variable: String },
    
    #[error("Missing precondition evidence: precondition={0}")]
    MissingPreconditionEvidence { precondition: String },
    
    #[error("Missing postcondition evidence: postcondition={0}")]
    MissingPostconditionEvidence { postcondition: String },
    
    #[error("Precondition failed: precondition={0}")]
    PreconditionFailed { precondition: String },
    
    #[error("Postcondition failed: postcondition={0}")]
    PostconditionFailed { postcondition: String },
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_evidence_dag_new() {
        let dag = EvidenceDAG::new();
        assert_eq!(dag.nodes.len(), 0);
        assert_eq!(dag.edges.len(), 0);
    }

    #[test]
    fn test_evidence_node_hash() {
        let node = EvidenceNode::new(
            "source".to_string(),
            None,
            None,
            "tool1".to_string(),
            "input_hash".to_string(),
            "output_hash".to_string(),
            None,
            Vec::new(),
            "signer1".to_string(),
            "sig1".to_string(),
        );
        assert!(!node.hash.is_empty());
    }

    #[test]
    fn test_get_node() {
        let mut dag = EvidenceDAG::new();
        let node = EvidenceNode::new(
            "source".to_string(),
            None,
            None,
            "tool1".to_string(),
            "input_hash".to_string(),
            "output_hash".to_string(),
            None,
            Vec::new(),
            "signer1".to_string(),
            "sig1".to_string(),
        );
        let node_id = node.id.clone();
        dag.add_node(node);
        
        let retrieved = dag.get_node(&node_id);
        assert!(retrieved.is_some());
    }
}

