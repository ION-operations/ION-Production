//! Generate evidence DAG from execution traces
//!
//! This binary:
//! - Loads evidence log from trace JSON
//! - Converts to DAG format
//! - Adds support/derives/witnesses edges
//! - Saves as evidence_dag.json

use plix_verifier::*;
use serde_json;
use std::fs;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("=== Generate Evidence DAG ===\n");
    
    // Step 1: Load passing trace
    println!("[1/3] Loading passing trace...");
    let passing_trace = fs::read_to_string("meeting_room_passing_trace.json")?;
    let passing_evidence: Vec<plix_ref_interpreter::EvidenceEntry> = 
        serde_json::from_str(&passing_trace)?;
    println!("  ✓ Loaded {} evidence entries", passing_evidence.len());
    
    // Step 2: Convert to DAG
    println!("[2/3] Converting to evidence DAG...");
    let dag = convert_to_dag(&passing_evidence);
    println!("  ✓ Created DAG with {} nodes and {} edges", dag.nodes.len(), dag.edges.len());
    
    // Step 3: Save DAG
    println!("[3/3] Saving evidence DAG...");
    let dag_json = serde_json::to_string_pretty(&dag)?;
    fs::write("meeting_room_evidence_dag.json", dag_json)?;
    println!("  ✓ Saved to: meeting_room_evidence_dag.json");
    
    println!("\n=== DAG GENERATION SUCCESSFUL ===");
    
    Ok(())
}

/// Convert evidence log to DAG
fn convert_to_dag(evidence: &[plix_ref_interpreter::EvidenceEntry]) -> EvidenceDAG {
    let mut dag = EvidenceDAG::new();
    
    // Convert each evidence entry to node
    for (i, entry) in evidence.iter().enumerate() {
        let mut node = EvidenceNode::new(
            if i == 0 { "source" } else { "derivation" }.to_string(),
            entry.step_id.clone(),
            entry.contract_id.clone(),
            entry.tool.clone(),
            entry.input_hash.clone(),
            entry.output_hash.clone(),
            entry.parent_hash.clone(),
            entry.parents.clone(),
            entry.signer.clone(),
            entry.sig.clone(),
        );
        node.time = entry.time;
        node.id = entry.id.clone();
        node.hash = entry.compute_hash();
        
        dag.add_node(node);
    }
    
    // Add edges based on parent relationships
    for node in &dag.nodes {
        for parent_id in &node.parents {
            let edge = EvidenceEdge::new(
                "derives".to_string(),
                parent_id.clone(),
                node.id.clone(),
                Some(0.9),
                None,
            );
            dag.add_edge(edge);
        }
    }
    
    dag
}

