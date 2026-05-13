//! Hash chain verification
//!
//! This module implements hash chain verification for evidence DAGs:
//! - Verify DAG structure (no cycles, valid parents)
//! - Verify parent hash chain (each node → parent)
//! - Verify node hashes (recompute and compare)

use std::collections::HashSet;
use crate::types::{EvidenceDAG, EvidenceNode};

/// Hash chain error
#[derive(Debug, thiserror::Error)]
pub enum HashChainError {
    #[error("Duplicate node ID: {0}")]
    DuplicateId(String),
    
    #[error("Parent not found: node={node}, parent={parent}")]
    ParentNotFound { node: String, parent: String },
    
    #[error("Parent hash mismatch: node={node}, expected={expected}, actual={actual}")]
    ParentHashMismatch { node: String, expected: String, actual: String },
    
    #[error("Node hash mismatch: node={node}, expected={expected}, actual={actual}")]
    NodeHashMismatch { node: String, expected: String, actual: String },
    
    #[error("Cycle detected in evidence DAG")]
    CycleDetected,
    
    #[error("Orphaned node: node={0} has no path to root")]
    OrphanedNode(String),
}

/// Verify hash chain
///
/// Checks:
/// 1. No duplicate node IDs
/// 2. All parents exist
/// 3. Parent hash chain is valid
/// 4. Node hashes are correct
/// 5. DAG structure (no cycles)
pub fn verify_hash_chain(dag: &EvidenceDAG) -> Result<(), HashChainError> {
    let mut seen_ids = HashSet::new();
    let mut node_map = std::collections::HashMap::new();
    
    // Step 1: Build node map and check for duplicates
    for node in &dag.nodes {
        if seen_ids.contains(&node.id) {
            return Err(HashChainError::DuplicateId(node.id.clone()));
        }
        seen_ids.insert(node.id.clone());
        node_map.insert(node.id.clone(), node);
    }
    
    // Step 2: Verify each node
    for node in &dag.nodes {
        verify_node(node, &node_map)?;
    }
    
    // Step 3: Check DAG structure (no cycles)
    verify_acyclic(dag)?;
    
    // Step 4: Check all nodes are reachable from roots
    verify_connectivity(dag)?;
    
    Ok(())
}

/// Verify individual node
fn verify_node(
    node: &EvidenceNode,
    node_map: &std::collections::HashMap<String, &EvidenceNode>,
) -> Result<(), HashChainError> {
    // Verify all parents exist
    for parent_id in &node.parents {
        if !node_map.contains_key(parent_id) {
            return Err(HashChainError::ParentNotFound {
                node: node.id.clone(),
                parent: parent_id.clone(),
            });
        }
    }
    
    // Verify parent hash chain
    if let Some(ref previous_hash) = node.previous_hash {
        // Find the previous node (typically the last parent)
        if let Some(parent_id) = node.parents.last() {
            if let Some(parent_node) = node_map.get(parent_id) {
                let expected_hash = parent_node.hash.clone();
                if *previous_hash != expected_hash {
                    return Err(HashChainError::ParentHashMismatch {
                        node: node.id.clone(),
                        expected: expected_hash,
                        actual: previous_hash.clone(),
                    });
                }
            }
        }
    }
    
    // Verify node hash
    let computed_hash = compute_node_hash(node);
    if node.hash != computed_hash {
        return Err(HashChainError::NodeHashMismatch {
            node: node.id.clone(),
            expected: computed_hash,
            actual: node.hash.clone(),
        });
    }
    
    Ok(())
}

/// Compute hash of a node
fn compute_node_hash(node: &EvidenceNode) -> String {
    use sha2::{Sha256, Digest};
    let mut hasher = Sha256::new();
    
    hasher.update(node.id.as_bytes());
    hasher.update(node.time.to_rfc3339().as_bytes());
    hasher.update(node.tool.as_bytes());
    hasher.update(node.input_hash.as_bytes());
    hasher.update(node.output_hash.as_bytes());
    
    if let Some(ref previous_hash) = node.previous_hash {
        hasher.update(previous_hash.as_bytes());
    }
    
    format!("{:x}", hasher.finalize())
}

/// Verify DAG is acyclic
fn verify_acyclic(dag: &EvidenceDAG) -> Result<(), HashChainError> {
    let mut visited = HashSet::new();
    let mut rec_stack = HashSet::new();
    
    for node in &dag.nodes {
        if !visited.contains(&node.id) {
            if has_cycle(node, dag, &mut visited, &mut rec_stack)? {
                return Err(HashChainError::CycleDetected);
            }
        }
    }
    
    Ok(())
}

/// Check for cycles using DFS
fn has_cycle(
    node: &EvidenceNode,
    dag: &EvidenceDAG,
    visited: &mut HashSet<String>,
    rec_stack: &mut HashSet<String>,
) -> Result<bool, HashChainError> {
    visited.insert(node.id.clone());
    rec_stack.insert(node.id.clone());
    
    // Visit all parents
    for parent_id in &node.parents {
        if !visited.contains(parent_id) {
            if let Some(parent_node) = dag.get_node(parent_id) {
                if has_cycle(parent_node, dag, visited, rec_stack)? {
                    return Ok(true);
                }
            }
        } else if rec_stack.contains(parent_id) {
            return Ok(true);
        }
    }
    
    rec_stack.remove(&node.id);
    Ok(false)
}

/// Verify all nodes are reachable from roots
fn verify_connectivity(dag: &EvidenceDAG) -> Result<(), HashChainError> {
    // Find root nodes (nodes with no parents)
    let roots: Vec<&EvidenceNode> = dag.nodes.iter()
        .filter(|n| n.parents.is_empty())
        .collect();
    
    if roots.is_empty() && !dag.nodes.is_empty() {
        // No roots but nodes exist - all nodes are orphaned
        return Err(HashChainError::OrphanedNode(
            dag.nodes.first().unwrap().id.clone()
        ));
    }
    
    // BFS from roots to find all reachable nodes
    let mut reachable = HashSet::new();
    let mut queue: Vec<String> = roots.iter().map(|n| n.id.clone()).collect();
    
    while let Some(node_id) = queue.pop() {
        if reachable.contains(&node_id) {
            continue;
        }
        reachable.insert(node_id.clone());
        
        // Add children to queue (nodes that have this node as parent)
        for node in &dag.nodes {
            if node.parents.contains(&node_id) && !reachable.contains(&node.id) {
                queue.push(node.id.clone());
            }
        }
    }
    
    // Check if any nodes are unreachable
    for node in &dag.nodes {
        if !reachable.contains(&node.id) {
            return Err(HashChainError::OrphanedNode(node.id.clone()));
        }
    }
    
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::types::{EvidenceNode, EvidenceDAG};
    use chrono::Utc;

    #[test]
    fn test_verify_hash_chain_empty() {
        let dag = EvidenceDAG::new();
        assert!(verify_hash_chain(&dag).is_ok());
    }

    #[test]
    fn test_verify_hash_chain_single_node() {
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
        dag.add_node(node);
        
        assert!(verify_hash_chain(&dag).is_ok());
    }

    #[test]
    fn test_verify_hash_chain_duplicate_id() {
        let mut dag = EvidenceDAG::new();
        let node1 = EvidenceNode::new(
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
        let id = node1.id.clone();
        
        let mut node2 = node1.clone();
        node2.id = id;
        
        dag.add_node(node1);
        dag.add_node(node2);
        
        let result = verify_hash_chain(&dag);
        assert!(result.is_err());
        assert!(matches!(result.unwrap_err(), HashChainError::DuplicateId(_)));
    }

    #[test]
    fn test_verify_hash_chain_parent_not_found() {
        let mut dag = EvidenceDAG::new();
        let node = EvidenceNode::new(
            "claim".to_string(),
            None,
            None,
            "tool1".to_string(),
            "input_hash".to_string(),
            "output_hash".to_string(),
            Some("parent_hash".to_string()),
            vec!["nonexistent_parent".to_string()],
            "signer1".to_string(),
            "sig1".to_string(),
        );
        dag.add_node(node);
        
        let result = verify_hash_chain(&dag);
        assert!(result.is_err());
        assert!(matches!(result.unwrap_err(), HashChainError::ParentNotFound { .. }));
    }

    #[test]
    fn test_verify_hash_chain_valid_chain() {
        let mut dag = EvidenceDAG::new();
        
        // Create parent node
        let parent = EvidenceNode::new(
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
        let parent_id = parent.id.clone();
        let parent_hash = parent.hash.clone();
        dag.add_node(parent);
        
        // Create child node with correct parent hash
        let child = EvidenceNode::new(
            "claim".to_string(),
            None,
            None,
            "tool2".to_string(),
            "input_hash2".to_string(),
            "output_hash2".to_string(),
            Some(parent_hash.clone()),
            vec![parent_id],
            "signer2".to_string(),
            "sig2".to_string(),
        );
        dag.add_node(child);
        
        assert!(verify_hash_chain(&dag).is_ok());
    }
}


