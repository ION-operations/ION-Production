//! Generate passing execution trace for meeting-room example
//!
//! This binary:
//! - Creates meeting-room intent
//! - Executes with interpreter (passing scenario)
//! - Captures evidence log
//! - Saves to JSON file

use plix_meeting_room_example::*;
use serde_json;
use std::fs;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("=== Meeting-Room Passing Execution Trace ===\n");
    
    // Step 1: Create intent
    println!("[1/5] Creating intent...");
    let intent = create_meeting_room_intent();
    println!("  ✓ Intent created with {} steps", intent.steps.len());
    
    // Step 2: Create resolver
    println!("[2/5] Creating resolver...");
    let resolver = create_resolver();
    println!("  ✓ Resolver created with 4 actions");
    
    // Step 3: Create initial state (will succeed)
    println!("[3/5] Creating initial state...");
    let mut initial_state = create_initial_state();
    // Add postcondition values to ensure success
    initial_state.insert(
        "room_reserved".to_string(),
        plix_ref_interpreter::Value::Bool(true),
    );
    initial_state.insert(
        "calendar_event_created".to_string(),
        plix_ref_interpreter::Value::Bool(true),
    );
    println!("  ✓ Initial state created (passing scenario)");
    
    // Step 4: Execute intent
    println!("[4/5] Executing intent...");
    let (final_state, evidence_log) = plix_ref_interpreter::interpret(&intent, initial_state, &resolver)?;
    println!("  ✓ Execution successful");
    println!("  ✓ Evidence entries: {}", evidence_log.len());
    
    // Step 5: Save evidence log
    println!("[5/5] Saving evidence log...");
    let evidence_json = serde_json::to_string_pretty(&evidence_log)?;
    fs::write(
        "meeting_room_passing_trace.json",
        evidence_json,
    )?;
    println!("  ✓ Saved to: meeting_room_passing_trace.json");
    
    println!("\n=== EXECUTION SUCCESSFUL ===");
    println!("Final state variables: {}", final_state.len());
    println!("Evidence entries: {}", evidence_log.len());
    
    Ok(())
}

