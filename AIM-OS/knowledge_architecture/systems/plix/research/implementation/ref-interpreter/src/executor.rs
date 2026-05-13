//! Executor: Step execution
//!
//! This module implements step execution for Core-PLIx:
//! - Parameter evaluation: `eval_params(p, σ) = p'`
//! - Action execution: `run(a, p', σ) ↠ μ over pairs (σ', e, ok)`
//! - Evidence creation: Create evidence entry with hash-chaining

use std::collections::HashMap;
use crate::types::{State, EvidenceEntry, Value};
use crate::resolver::{Resolver, PrimAction};

/// Execute step: `run(a, p', σ) ↠ μ over pairs (σ', e, ok)`
///
/// Returns: (new_state, evidence_entry, success)
pub fn execute_step(
    action: &PrimAction,
    params: &HashMap<String, Value>,
    state: &State,
    resolver: &Resolver,
    parent_hash: Option<String>,
    parents: Vec<String>,
    step_id: Option<String>,
    contract_id: Option<String>,
) -> Result<(State, EvidenceEntry, bool), String> {
    // Evaluate parameters (substitute state values)
    let evaluated_params = eval_params(params, state)?;
    
    // Execute action (simplified: just update state)
    let (new_state, success) = run_action(action, &evaluated_params, state)?;
    
    // Create evidence entry
    let input_hash = compute_hash(&evaluated_params);
    let output_hash = compute_hash(&new_state);
    
    let evidence = EvidenceEntry::new(
        step_id,
        contract_id,
        action.name.clone(),
        input_hash,
        output_hash,
        parent_hash,
        parents,
        "system".to_string(), // TODO: Use actual signer
        "sig".to_string(),   // TODO: Use actual signature
    );
    
    Ok((new_state, evidence, success))
}

/// Evaluate parameters: `eval_params(p, σ) = p'`
///
/// Substitutes state values into parameters
fn eval_params(
    params: &HashMap<String, Value>,
    state: &State,
) -> Result<HashMap<String, Value>, String> {
    let mut evaluated = HashMap::new();
    
    for (key, value) in params {
        let evaluated_value = match value {
            Value::Tag(tag) => {
                // Resolve tag from state or return as-is
                state.get(tag).cloned().unwrap_or_else(|| value.clone())
            }
            _ => value.clone(),
        };
        evaluated.insert(key.clone(), evaluated_value);
    }
    
    Ok(evaluated)
}

/// Run action: `run(a, p', σ) ↠ (σ', ok)`
///
/// Simplified implementation: updates state based on action
fn run_action(
    action: &PrimAction,
    params: &HashMap<String, Value>,
    state: &State,
) -> Result<(State, bool), String> {
    let mut new_state = state.clone();
    
    // Simplified: just mark action as executed
    // In real implementation, this would call the actual action handler
    let state_key = format!("executed:{}", action.id);
    new_state.insert(state_key, Value::Bool(true));
    
    // Compute confidence
    let confidence = (action.confidence_fn)(params, state);
    let success = confidence >= 0.5; // Simplified success criterion
    
    Ok((new_state, success))
}

/// Compute hash of value map
fn compute_hash(values: &HashMap<String, Value>) -> String {
    use sha2::{Sha256, Digest};
    let mut hasher = Sha256::new();
    
    let mut sorted_keys: Vec<&String> = values.keys().collect();
    sorted_keys.sort();
    
    for key in sorted_keys {
        hasher.update(key.as_bytes());
        if let Some(value) = values.get(key) {
            hasher.update(format!("{:?}", value).as_bytes());
        }
    }
    
    format!("{:x}", hasher.finalize())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::resolver::Effect;

    #[test]
    fn test_eval_params() {
        let mut params = HashMap::new();
        params.insert("x".to_string(), Value::Number(1.0));
        params.insert("y".to_string(), Value::Tag("state:y".to_string()));
        
        let mut state = State::new();
        state.insert("state:y".to_string(), Value::Number(2.0));
        
        let evaluated = eval_params(&params, &state).unwrap();
        
        assert_eq!(evaluated.get("x"), Some(&Value::Number(1.0)));
        assert_eq!(evaluated.get("y"), Some(&Value::Number(2.0)));
    }

    #[test]
    fn test_run_action() {
        let action = PrimAction {
            id: "test_action".to_string(),
            name: "test_action".to_string(),
            params: vec!["param1".to_string()],
            effects: vec![Effect::Io],
            confidence_fn: Box::new(|_, _| 0.9),
        };
        
        let mut params = HashMap::new();
        params.insert("param1".to_string(), Value::String("value1".to_string()));
        
        let state = State::new();
        
        let (new_state, success) = run_action(&action, &params, &state).unwrap();
        
        assert!(success);
        assert!(new_state.contains_key("executed:test_action"));
    }

    #[test]
    fn test_execute_step() {
        let action = PrimAction {
            id: "test_action".to_string(),
            name: "test_action".to_string(),
            params: vec!["param1".to_string()],
            effects: vec![Effect::Io],
            confidence_fn: Box::new(|_, _| 0.9),
        };
        
        let mut params = HashMap::new();
        params.insert("param1".to_string(), Value::String("value1".to_string()));
        
        let state = State::new();
        let resolver = Resolver::new();
        
        let (new_state, evidence, success) = execute_step(
            &action,
            &params,
            &state,
            &resolver,
            None,
            Vec::new(),
            Some("step1".to_string()),
            None,
        ).unwrap();
        
        assert!(success);
        assert_eq!(evidence.step_id, Some("step1".to_string()));
        assert!(!evidence.input_hash.is_empty());
        assert!(!evidence.output_hash.is_empty());
    }
}

