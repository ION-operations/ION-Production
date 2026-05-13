//! Evidence completeness
//!
//! This module implements evidence completeness checking:
//! - Check all preconditions have evidence support
//! - Check all postconditions have evidence support
//! - Verify source paths (BFS from claims to sources)

use std::collections::HashSet;
use crate::types::{EvidenceDAG, EvidenceNode};

/// Completeness error
#[derive(Debug, thiserror::Error)]
pub enum CompletenessError {
    #[error("Missing precondition evidence: {0}")]
    MissingPreconditionEvidence(String),
    
    #[error("Missing postcondition evidence: {0}")]
    MissingPostconditionEvidence(String),
    
    #[error("Claim has no source path: {0}")]
    NoSourcePath(String),
    
    #[error("Invalid evidence structure: {0}")]
    InvalidStructure(String),
}

/// Contract definition (simplified)
pub struct Contract {
    pub preconditions: Vec<String>,
    pub postconditions: Vec<String>,
}

/// Verify evidence completeness
///
/// Checks that:
/// 1. All preconditions have evidence support
/// 2. All postconditions have evidence support
/// 3. All claims have source paths
pub fn verify_evidence_completeness(
    contract: &Contract,
    evidence_dag: &EvidenceDAG,
) -> Result<(), CompletenessError> {
    // Check preconditions
    for precondition in &contract.preconditions {
        if !has_evidence_support(precondition, evidence_dag)? {
            return Err(CompletenessError::MissingPreconditionEvidence(
                precondition.clone(),
            ));
        }
    }
    
    // Check postconditions
    for postcondition in &contract.postconditions {
        if !has_evidence_support(postcondition, evidence_dag)? {
            return Err(CompletenessError::MissingPostconditionEvidence(
                postcondition.clone(),
            ));
        }
    }
    
    Ok(())
}

/// Check if constraint has evidence support
fn has_evidence_support(
    constraint: &str,
    evidence_dag: &EvidenceDAG,
) -> Result<bool, CompletenessError> {
    // Find claim nodes for this constraint
    let claim_nodes: Vec<&EvidenceNode> = evidence_dag
        .nodes
        .iter()
        .filter(|n| n.node_type == "claim")
        .filter(|n| {
            if let Some(ref content) = n.content {
                content.contains(constraint) || constraint.contains(content)
            } else {
                false
            }
        })
        .collect();
    
    if claim_nodes.is_empty() {
        return Ok(false);
    }
    
    // Check each claim has source path
    for claim in claim_nodes {
        if !has_source_path(claim, evidence_dag)? {
            return Ok(false);
        }
    }
    
    Ok(true)
}

/// Check if claim has path to source
fn has_source_path(
    claim: &EvidenceNode,
    evidence_dag: &EvidenceDAG,
) -> Result<bool, CompletenessError> {
    // BFS from claim to sources
    let mut queue = vec![claim.id.clone()];
    let mut visited = HashSet::new();
    
    while let Some(node_id) = queue.pop() {
        if visited.contains(&node_id) {
            continue;
        }
        visited.insert(node_id.clone());
        
        let node = evidence_dag
            .get_node(&node_id)
            .ok_or_else(|| CompletenessError::InvalidStructure(format!("Node not found: {}", node_id)))?;
        
        // If we reached a source, path exists
        if node.node_type == "source" {
            return Ok(true);
        }
        
        // Follow edges backwards (from claim to supports/derives)
        for edge in &evidence_dag.edges {
            if edge.to == node_id && 
               (edge.edge_type == "supports" || edge.edge_type == "derives") {
                if !visited.contains(&edge.from) {
                    queue.push(edge.from.clone());
                }
            }
        }
        
        // Also follow parent references
        for parent_id in &node.parents {
            if !visited.contains(parent_id) {
                queue.push(parent_id.clone());
            }
        }
    }
    
    // No source found
    Ok(false)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::types::{EvidenceNode, EvidenceDAG, EvidenceEdge};

    #[test]
    fn test_extract_variables() {
        let constraint = "room_available(date, duration) == true";
        let vars = extract_variables(constraint).unwrap();
        assert!(vars.len() >= 2);
    }

    #[test]
    fn test_has_evidence_support() {
        let mut dag = EvidenceDAG::new();
        
        // Create source node
        let mut source = EvidenceNode::new(
            "source".to_string(),
            None,
            None,
            "availability_service".to_string(),
            "input".to_string(),
            "output".to_string(),
            None,
            Vec::new(),
            "signer".to_string(),
            "sig".to_string(),
        );
        source.content = Some("room_availability_witness".to_string());
        let source_id = source.id.clone();
        dag.add_node(source);
        
        // Create claim node
        let mut claim = EvidenceNode::new(
            "claim".to_string(),
            None,
            None,
            "constraint_checker".to_string(),
            "input".to_string(),
            "output".to_string(),
            None,
            vec![source_id.clone()],
            "signer".to_string(),
            "sig".to_string(),
        );
        claim.content = Some("room_available == true".to_string());
        claim.result = Some(true);
        let claim_id = claim.id.clone();
        dag.add_node(claim);
        
        // Add edge
        let edge = EvidenceEdge::new(
            "supports".to_string(),
            source_id,
            claim_id,
            Some(0.95),
            None,
        );
        dag.add_edge(edge);
        
        let result = has_evidence_support("room_available == true", &dag).unwrap();
        assert!(result);
    }

    #[test]
    fn test_verify_evidence_completeness() {
        let mut dag = EvidenceDAG::new();
        
        // Create source
        let mut source = EvidenceNode::new(
            "source".to_string(),
            None,
            None,
            "service".to_string(),
            "input".to_string(),
            "output".to_string(),
            None,
            Vec::new(),
            "signer".to_string(),
            "sig".to_string(),
        );
        source.content = Some("witness".to_string());
        let source_id = source.id.clone();
        dag.add_node(source);
        
        // Create claim
        let mut claim = EvidenceNode::new(
            "claim".to_string(),
            None,
            None,
            "checker".to_string(),
            "input".to_string(),
            "output".to_string(),
            None,
            vec![source_id.clone()],
            "signer".to_string(),
            "sig".to_string(),
        );
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
        
        let contract = Contract {
            preconditions: vec!["precondition1 == true".to_string()],
            postconditions: vec![],
        };
        
        let result = verify_evidence_completeness(&contract, &dag);
        assert!(result.is_ok());
    }

    #[test]
    fn test_missing_evidence() {
        let dag = EvidenceDAG::new();
        
        let contract = Contract {
            preconditions: vec!["missing_precondition == true".to_string()],
            postconditions: vec![],
        };
        
        let result = verify_evidence_completeness(&contract, &dag);
        assert!(result.is_err());
    }
}


