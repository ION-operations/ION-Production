//! Meeting-Room Reservation Example
//!
//! This example demonstrates the complete PLIx pipeline:
//! - Intent definition (reserve meeting room)
//! - Plan execution with interpreter
//! - Evidence generation
//! - Verification with verifier

use std::collections::HashMap;
use plix_ref_interpreter::*;
use plix_verifier::*;

/// Create meeting-room reservation intent
pub fn create_meeting_room_intent() -> Intent {
    // Create plan DAG
    let mut dag = PlanDAG::new();
    dag.add_vertex("check".to_string());
    dag.add_vertex("reserve".to_string());
    dag.add_vertex("invite".to_string());
    dag.add_edge("check".to_string(), "reserve".to_string());
    dag.add_edge("reserve".to_string(), "invite".to_string());
    
    // Create steps
    let mut check_params = HashMap::new();
    check_params.insert("date".to_string(), Value::String("2025-12-01".to_string()));
    check_params.insert("duration".to_string(), Value::String("2h".to_string()));
    
    let check_step = Step {
        id: "check".to_string(),
        action_id: "api.check_room_availability".to_string(),
        params: check_params,
        compensable: false,
        compensation_action_id: None,
        compensation_params: None,
    };
    
    let mut reserve_params = HashMap::new();
    reserve_params.insert("room_id".to_string(), Value::Tag("check.room_id".to_string()));
    reserve_params.insert("duration".to_string(), Value::String("2h".to_string()));
    
    let mut comp_params = HashMap::new();
    comp_params.insert("reservation_id".to_string(), Value::Tag("reserve.id".to_string()));
    
    let reserve_step = Step {
        id: "reserve".to_string(),
        action_id: "api.reserve_room".to_string(),
        params: reserve_params,
        compensable: true,
        compensation_action_id: Some("api.cancel_reservation".to_string()),
        compensation_params: Some(comp_params),
    };
    
    let mut invite_params = HashMap::new();
    invite_params.insert("room_id".to_string(), Value::Tag("reserve.room_id".to_string()));
    invite_params.insert("user_id".to_string(), Value::String("user123".to_string()));
    
    let invite_step = Step {
        id: "invite".to_string(),
        action_id: "api.create_calendar_event".to_string(),
        params: invite_params,
        compensable: false,
        compensation_action_id: None,
        compensation_params: None,
    };
    
    Intent {
        preconditions: vec!["room_available".to_string(), "user_authenticated".to_string()],
        postconditions: vec!["room_reserved".to_string(), "calendar_event_created".to_string()],
        plan_dag: dag,
        steps: vec![check_step, reserve_step, invite_step],
    }
}

/// Create resolver with meeting-room actions
pub fn create_resolver() -> Resolver {
    let mut resolver = Resolver::new();
    
    // Register check availability action
    let check_action = PrimAction {
        id: "api.check_room_availability".to_string(),
        name: "check_room_availability".to_string(),
        params: vec!["date".to_string(), "duration".to_string()],
        effects: vec![Effect::Io, Effect::Net],
        confidence_fn: Box::new(|_, _| 0.95),
    };
    resolver.register_action("api.check_room_availability".to_string(), check_action);
    
    // Register reserve room action
    let reserve_action = PrimAction {
        id: "api.reserve_room".to_string(),
        name: "reserve_room".to_string(),
        params: vec!["room_id".to_string(), "duration".to_string()],
        effects: vec![Effect::Io, Effect::Net, Effect::Compensable],
        confidence_fn: Box::new(|_, _| 0.90),
    };
    resolver.register_action("api.reserve_room".to_string(), reserve_action);
    
    // Register create calendar event action
    let invite_action = PrimAction {
        id: "api.create_calendar_event".to_string(),
        name: "create_calendar_event".to_string(),
        params: vec!["room_id".to_string(), "user_id".to_string()],
        effects: vec![Effect::Io, Effect::Net],
        confidence_fn: Box::new(|_, _| 0.88),
    };
    resolver.register_action("api.create_calendar_event".to_string(), invite_action);
    
    // Register cancel reservation action (compensation)
    let cancel_action = PrimAction {
        id: "api.cancel_reservation".to_string(),
        name: "cancel_reservation".to_string(),
        params: vec!["reservation_id".to_string()],
        effects: vec![Effect::Io, Effect::Net, Effect::Compensable],
        confidence_fn: Box::new(|_, _| 0.92),
    };
    resolver.register_action("api.cancel_reservation".to_string(), cancel_action);
    
    resolver
}

/// Create initial state for meeting-room example
pub fn create_initial_state() -> State {
    let mut state = State::new();
    state.insert("room_available".to_string(), Value::Bool(true));
    state.insert("user_authenticated".to_string(), Value::Bool(true));
    state
}

/// Create initial state for failed scenario (postconditions will fail)
pub fn create_failing_state() -> State {
    let mut state = State::new();
    state.insert("room_available".to_string(), Value::Bool(true));
    state.insert("user_authenticated".to_string(), Value::Bool(true));
    // Don't set room_reserved or calendar_event_created
    // This will cause postconditions to fail
    state
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_create_intent() {
        let intent = create_meeting_room_intent();
        assert_eq!(intent.steps.len(), 3);
        assert_eq!(intent.preconditions.len(), 2);
        assert_eq!(intent.postconditions.len(), 2);
    }

    #[test]
    fn test_create_resolver() {
        let resolver = create_resolver();
        assert!(resolver.resolve_action("api.check_room_availability").is_some());
        assert!(resolver.resolve_action("api.reserve_room").is_some());
        assert!(resolver.resolve_action("api.create_calendar_event").is_some());
        assert!(resolver.resolve_action("api.cancel_reservation").is_some());
    }

    #[test]
    fn test_execute_passing_scenario() {
        let intent = create_meeting_room_intent();
        let resolver = create_resolver();
        let mut initial_state = create_initial_state();
        
        // Add postcondition values to ensure success
        initial_state.insert("room_reserved".to_string(), Value::Bool(true));
        initial_state.insert("calendar_event_created".to_string(), Value::Bool(true));
        
        let result = interpret(&intent, initial_state, &resolver);
        assert!(result.is_ok());
    }
}

