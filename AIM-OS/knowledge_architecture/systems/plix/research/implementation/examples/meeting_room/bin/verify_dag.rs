//! Verify evidence DAG
//!
//! This binary:
//! - Loads evidence DAG from JSON
//! - Runs verifier
//! - Prints verification result

use plix_verifier::*;
use serde_json;
use std::fs;
use ed25519_dalek::{Keypair, Signer as Ed25519Signer};
use rand::rngs::OsRng;
use std::collections::HashMap;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("=== Verify Evidence DAG ===\n");
    
    // Step 1: Load evidence DAG
    println!("[1/3] Loading evidence DAG...");
    let dag_json = fs::read_to_string("meeting_room_evidence_dag.json")?;
    let dag: EvidenceDAG = serde_json::from_str(&dag_json)?;
    println!("  ✓ Loaded DAG with {} nodes and {} edges", dag.nodes.len(), dag.edges.len());
    
    // Step 2: Create intent and trusted keys
    println!("[2/3] Setting up verification...");
    let intent = create_verification_intent();
    let trusted_keys = create_trusted_keys();
    println!("  ✓ Created intent and trusted keys");
    
    // Step 3: Verify
    println!("[3/3] Verifying evidence DAG...");
    match verify(&intent, &dag, &trusted_keys) {
        Ok(VerificationResult::Pass { preconditions, postconditions, evidence_nodes, evidence_edges }) => {
            println!("  ✓ VERIFICATION PASSED");
            println!("\nDetails:");
            println!("  - Preconditions verified: {}", preconditions);
            println!("  - Postconditions verified: {}", postconditions);
            println!("  - Evidence nodes: {}", evidence_nodes);
            println!("  - Evidence edges: {}", evidence_edges);
            println!("\n=== VERIFICATION SUCCESSFUL ===");
        }
        Ok(VerificationResult::Fail { error }) => {
            println!("  ✗ VERIFICATION FAILED");
            println!("\nError: {}", error);
        }
        Err(e) => {
            println!("  ✗ VERIFICATION ERROR");
            println!("\nError: {:?}", e);
            return Err(Box::new(e));
        }
    }
    
    Ok(())
}

/// Create verification intent
fn create_verification_intent() -> Intent {
    Intent {
        id: "meeting_room_reservation".to_string(),
        contract: Contract {
            preconditions: vec![
                "room_available == true".to_string(),
                "user_authenticated == true".to_string(),
            ],
            postconditions: vec![
                "room_reserved == true".to_string(),
                "calendar_event_created == true".to_string(),
            ],
        },
    }
}

/// Create trusted keys for verification
fn create_trusted_keys() -> HashMap<String, ed25519_dalek::PublicKey> {
    let mut csprng = OsRng{};
    let keypair: Keypair = Keypair::generate(&mut csprng);
    
    let mut keys = HashMap::new();
    keys.insert("system".to_string(), keypair.public);
    keys
}

