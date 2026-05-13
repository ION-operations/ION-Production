//! Interpreter: Main interpreter loop
//!
//! This module implements the main interpreter loop for Core-PLIx:
//! - Precondition checking
//! - Plan execution (DAG-based)
//! - Postcondition checking
//! - Compensation (if postconditions fail)

use crate::types::{Config, State, EvLog};
use crate::resolver::Resolver;
use crate::dag_scheduler::{ready_set, reverse_topological_order};
use crate::executor::execute_step;

/// Intent representation (simplified)
pub struct Intent {
    pub preconditions: Vec<String>, // Simplified: just strings
    pub postconditions: Vec<String>,
    pub plan_dag: crate::types::PlanDAG,
    pub steps: Vec<Step>,
}

/// Step representation (simplified)
pub struct Step {
    pub id: String,
    pub action_id: String,
    pub params: std::collections::HashMap<String, crate::types::Value>,
    pub compensable: bool,
    pub compensation_action_id: Option<String>,
    pub compensation_params: Option<std::collections::HashMap<String, crate::types::Value>>,
}

/// Interpret intent: Main interpreter loop
///
/// Returns: (final_state, evidence_log)
pub fn interpret(
    intent: &Intent,
    initial_state: State,
    resolver: &Resolver,
) -> Result<(State, EvLog), String> {
    // Step 1: Check preconditions
    if !check_preconditions(&intent.preconditions, &initial_state)? {
        return Err("Preconditions not satisfied".to_string());
    }
    
    // Step 2: Initialize configuration
    let mut config = Config::new(initial_state);
    
    // Step 3: Initialize ready set
    config.ready_set = ready_set(&intent.plan_dag, &config.done);
    
    // Step 4: Execute plan (main loop)
    loop {
        if config.ready_set.is_empty() {
            break;
        }
        
        // Execute all ready steps
        let ready_steps: Vec<String> = config.ready_set.iter().cloned().collect();
        
        for step_id in ready_steps {
            // Find step
            let step = intent.steps.iter()
                .find(|s| s.id == step_id)
                .ok_or_else(|| format!("Step not found: {}", step_id))?;
            
            // Find action
            let action = resolver.resolve_action(&step.action_id)
                .ok_or_else(|| format!("Action not found: {}", step.action_id))?;
            
            // Get parent hash (from last evidence entry)
            let parent_hash = config.evidence_log.last()
                .map(|e| e.compute_hash());
            
            // Get parent IDs
            let parents: Vec<String> = config.evidence_log.iter()
                .map(|e| e.id.clone())
                .collect();
            
            // Execute step
            match execute_step(
                &action,
                &step.params,
                &config.state,
                resolver,
                parent_hash,
                parents,
                Some(step_id.clone()),
                None,
            ) {
                Ok((new_state, evidence, success)) => {
                    config.state = new_state;
                    config.append_evidence(evidence);
                    
                    if success {
                        config.done.insert(step_id.clone());
                    } else {
                        config.failed.insert(step_id.clone());
                    }
                }
                Err(e) => {
                    config.failed.insert(step_id.clone());
                    return Err(format!("Step execution failed: {}", e));
                }
            }
        }
        
        // Update ready set
        config.ready_set = ready_set(&intent.plan_dag, &config.done);
    }
    
    // Step 5: Check postconditions
    if !check_postconditions(&intent.postconditions, &config.state)? {
        // Step 6: Compensate (if postconditions fail)
        compensate_plan(intent, &mut config, resolver)?;
        return Err("Postconditions not satisfied, compensation executed".to_string());
    }
    
    Ok((config.state, config.evidence_log))
}

/// Check preconditions
fn check_preconditions(
    preconditions: &[String],
    state: &State,
) -> Result<bool, String> {
    // Simplified: just check if all precondition keys exist in state
    for precondition in preconditions {
        // In real implementation, this would evaluate the constraint expression
        if !state.contains_key(precondition) {
            return Ok(false);
        }
    }
    Ok(true)
}

/// Check postconditions
fn check_postconditions(
    postconditions: &[String],
    state: &State,
) -> Result<bool, String> {
    // Simplified: just check if all postcondition keys exist in state
    for postcondition in postconditions {
        // In real implementation, this would evaluate the constraint expression
        if !state.contains_key(postcondition) {
            return Ok(false);
        }
    }
    Ok(true)
}

/// Compensate plan: Execute compensation in reverse topological order
fn compensate_plan(
    intent: &Intent,
    config: &mut Config,
    resolver: &Resolver,
) -> Result<(), String> {
    // Get reverse topological order
    let compensation_order = reverse_topological_order(&intent.plan_dag)?;
    
    // Filter to only compensable steps that are done
    let compensable_steps: Vec<String> = compensation_order
        .into_iter()
        .filter(|step_id| {
            intent.steps.iter()
                .any(|s| s.id == *step_id && s.compensable && config.done.contains(step_id))
        })
        .collect();
    
    // Execute compensation in reverse order
    for step_id in compensable_steps {
        let step = intent.steps.iter()
            .find(|s| s.id == step_id)
            .ok_or_else(|| format!("Step not found: {}", step_id))?;
        
        if let (Some(comp_action_id), Some(comp_params)) = (
            &step.compensation_action_id,
            &step.compensation_params,
        ) {
            let comp_action = resolver.resolve_action(comp_action_id)
                .ok_or_else(|| format!("Compensation action not found: {}", comp_action_id))?;
            
            let parent_hash = config.evidence_log.last()
                .map(|e| e.compute_hash());
            
            let parents: Vec<String> = config.evidence_log.iter()
                .map(|e| e.id.clone())
                .collect();
            
            match execute_step(
                &comp_action,
                comp_params,
                &config.state,
                resolver,
                parent_hash,
                parents,
                Some(format!("compensate:{}", step_id)),
                None,
            ) {
                Ok((new_state, evidence, _)) => {
                    config.state = new_state;
                    config.append_evidence(evidence);
                }
                Err(e) => {
                    return Err(format!("Compensation failed for step {}: {}", step_id, e));
                }
            }
        }
    }
    
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::types::PlanDAG;
    use crate::resolver::{Resolver, PrimAction, Effect};
    use std::collections::HashMap;

    #[test]
    fn test_interpret_simple() {
        // Create simple intent
        let mut dag = PlanDAG::new();
        dag.add_vertex("step1".to_string());
        
        let mut resolver = Resolver::new();
        let action = PrimAction {
            id: "action1".to_string(),
            name: "action1".to_string(),
            params: vec![],
            effects: vec![Effect::Io],
            confidence_fn: Box::new(|_, _| 0.9),
        };
        resolver.register_action("action1".to_string(), action);
        
        let mut params = HashMap::new();
        params.insert("key".to_string(), crate::types::Value::String("value".to_string()));
        
        let intent = Intent {
            preconditions: vec!["precondition1".to_string()],
            postconditions: vec!["postcondition1".to_string()],
            plan_dag: dag,
            steps: vec![Step {
                id: "step1".to_string(),
                action_id: "action1".to_string(),
                params,
                compensable: false,
                compensation_action_id: None,
                compensation_params: None,
            }],
        };
        
        let mut initial_state = State::new();
        initial_state.insert("precondition1".to_string(), crate::types::Value::Bool(true));
        
        let result = interpret(&intent, initial_state, &resolver);
        
        // Should succeed (simplified test)
        assert!(result.is_ok());
    }
}

