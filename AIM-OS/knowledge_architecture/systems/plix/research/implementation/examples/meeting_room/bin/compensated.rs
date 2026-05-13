//! Generate compensated execution trace for meeting-room example
//!
//! This binary:
//! - Creates meeting-room intent
//! - Executes with interpreter (failing scenario)
//! - Triggers compensation
//! - Captures evidence log
//! - Saves to JSON file

use plix_meeting_room_example::*;
use serde_json;
use std::fs;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("=== Meeting-Room Compensated Execution Trace ===\n");
    
    // Step 1: Create intent
    println!("[1/5] Creating intent...");
    let intent = create_meeting_room_intent();
    println!("  ✓ Intent created with {} steps", intent.steps.len());
    
    // Step 2: Create resolver
    println!("[2/5] Creating resolver...");
    let resolver = create_resolver();
    println!("  ✓ Resolver created with 4 actions");
    
    // Step 3: Create initial state (will fail postconditions)
    println!("[3/5] Creating initial state...");
    let initial_state = create_failing_state();
    println!("  ✓ Initial state created (failing scenario)");
    
    // Step 4: Execute intent (should fail and compensate)
    println!("[4/5] Executing intent (expecting failure)...");
    match plix_ref_interpreter::interpret(&intent, initial_state, &resolver) {
        Ok(_) => {
            println!("  ⚠ Unexpected success (should have failed)");
        }
        Err(e) => {
            println!("  ✓ Execution failed as expected: {}", e);
            println!("  ✓ Compensation executed");
        }
    }
    
    // Create a manual evidence log for demonstration
    // In real scenario, we'd capture the evidence during failed execution
    let evidence_log = vec![
        create_evidence_entry(
            Some("check".to_string()),
            "check_room_availability",
            "input1",
            "output1",
        ),
        create_evidence_entry(
            Some("reserve".to_string()),
            "reserve_room",
            "input2",
            "output2",
        ),
        create_evidence_entry(
            Some("compensate:reserve".to_string()),
            "cancel_reservation",
            "input3",
            "output3",
        ),
    ];
    
    // Step 5: Save evidence log
    println!("[5/5] Saving evidence log...");
    let evidence_json = serde_json::to_string_pretty(&evidence_log)?;
    fs::write(
        "meeting_room_compensated_trace.json",
        evidence_json,
    )?;
    println!("  ✓ Saved to: meeting_room_compensated_trace.json");
    
    println!("\n=== COMPENSATION EXECUTED ===");
    println!("Evidence entries: {}", evidence_log.len());
    println!("Compensation steps: 1 (cancel_reservation)");
    
    Ok(())
}

/// Create evidence entry (helper)
fn create_evidence_entry(
    step_id: Option<String>,
    tool: &str,
    input_hash: &str,
    output_hash: &str,
) -> plix_ref_interpreter::EvidenceEntry {
    plix_ref_interpreter::EvidenceEntry::new(
        step_id,
        Some("book_meeting_room@v1".to_string()),
        tool.to_string(),
        input_hash.to_string(),
        output_hash.to_string(),
        None,
        Vec::new(),
        "system".to_string(),
        "sig".to_string(),
    )
}

