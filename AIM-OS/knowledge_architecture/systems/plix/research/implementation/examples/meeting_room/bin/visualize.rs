//! Visualize evidence DAG
//!
//! This binary:
//! - Loads evidence DAG from JSON
//! - Generates GraphViz DOT file
//! - Optionally renders to PNG

use plix_verifier::*;
use serde_json;
use std::fs;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("=== Visualize Evidence DAG ===\n");
    
    // Step 1: Load evidence DAG
    println!("[1/2] Loading evidence DAG...");
    let dag_json = fs::read_to_string("meeting_room_evidence_dag.json")?;
    let dag: EvidenceDAG = serde_json::from_str(&dag_json)?;
    println!("  ✓ Loaded DAG with {} nodes and {} edges", dag.nodes.len(), dag.edges.len());
    
    // Step 2: Generate DOT file
    println!("[2/2] Generating GraphViz DOT file...");
    let dot = generate_dot(&dag);
    fs::write("meeting_room_evidence_dag.dot", dot)?;
    println!("  ✓ Saved to: meeting_room_evidence_dag.dot");
    
    println!("\n=== VISUALIZATION SUCCESSFUL ===");
    println!("\nTo render as PNG, run:");
    println!("  dot -Tpng meeting_room_evidence_dag.dot -o meeting_room_evidence_dag.png");
    
    Ok(())
}

/// Generate GraphViz DOT representation
fn generate_dot(dag: &EvidenceDAG) -> String {
    let mut dot = String::from("digraph EvidenceDAG {\n");
    dot.push_str("  rankdir=TB;\n");
    dot.push_str("  node [shape=box, style=rounded];\n\n");
    
    // Add nodes
    for node in &dag.nodes {
        let color = match node.node_type.as_str() {
            "source" => "lightblue",
            "claim" => "lightgreen",
            "derivation" => "lightyellow",
            "proof" => "lightpink",
            _ => "white",
        };
        
        let label = format!(
            "{}\\n{}\\n{}",
            node.id.chars().take(8).collect::<String>(),
            node.node_type,
            node.tool
        );
        
        dot.push_str(&format!(
            "  \"{}\" [label=\"{}\", fillcolor={}, style=filled];\n",
            node.id, label, color
        ));
    }
    
    dot.push_str("\n");
    
    // Add edges
    for edge in &dag.edges {
        let style = match edge.edge_type.as_str() {
            "supports" => "solid",
            "derives" => "dashed",
            "witnesses" => "bold",
            _ => "dotted",
        };
        
        let label = format!(
            "{} ({})",
            edge.edge_type,
            edge.strength.map(|s| format!("{:.2}", s)).unwrap_or_else(|| "N/A".to_string())
        );
        
        dot.push_str(&format!(
            "  \"{}\" -> \"{}\" [label=\"{}\", style={}];\n",
            edge.from, edge.to, label, style
        ));
    }
    
    dot.push_str("}\n");
    dot
}

