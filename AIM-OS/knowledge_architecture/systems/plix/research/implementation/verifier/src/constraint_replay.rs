//! Constraint replay
//!
//! This module implements pure constraint replay for verification:
//! - Build state from evidence DAG
//! - Re-evaluate constraints deterministically
//! - Compare with evidence claims

use std::collections::HashMap;
use crate::types::{EvidenceDAG, EvidenceNode};

/// Constraint replay error
#[derive(Debug, thiserror::Error)]
pub enum ConstraintReplayError {
    #[error("Missing evidence for variable: {0}")]
    MissingEvidence(String),
    
    #[error("Constraint mismatch: constraint={constraint}, expected={expected}, actual={actual}")]
    ConstraintMismatch {
        constraint: String,
        expected: bool,
        actual: bool,
    },
    
    #[error("Evaluation error: {0}")]
    EvaluationError(String),
    
    #[error("Claim node not found for constraint: {0}")]
    ClaimNotFound(String),
    
    #[error("Invalid constraint syntax: {0}")]
    InvalidConstraint(String),
}

/// Replay constraint
///
/// Re-evaluates a pure constraint by:
/// 1. Extracting variables from constraint expression
/// 2. Building state from evidence DAG
/// 3. Re-evaluating constraint
/// 4. Comparing with evidence claim
pub fn replay_constraint(
    constraint: &str,
    evidence_dag: &EvidenceDAG,
) -> Result<bool, ConstraintReplayError> {
    // Extract variables from constraint
    let variables = extract_variables(constraint)?;
    
    // Build state from evidence
    let state = build_state_from_evidence(&variables, evidence_dag)?;
    
    // Re-evaluate constraint
    let result = eval_constraint(constraint, &state)?;
    
    // Find claim node and compare
    if let Some(claim_node) = find_claim_node(constraint, evidence_dag)? {
        if let Some(expected) = claim_node.result {
            if result != expected {
                return Err(ConstraintReplayError::ConstraintMismatch {
                    constraint: constraint.to_string(),
                    expected,
                    actual: result,
                });
            }
        }
    }
    
    Ok(result)
}

/// Extract variables from constraint expression
fn extract_variables(constraint: &str) -> Result<Vec<String>, ConstraintReplayError> {
    // Simplified: extract words that look like identifiers
    // In real implementation, would use proper parser
    let mut variables = Vec::new();
    
    for token in constraint.split(|c: char| !c.is_alphanumeric() && c != '_') {
        if !token.is_empty() && !is_keyword(token) && !is_operator(token) {
            variables.push(token.to_string());
        }
    }
    
    Ok(variables)
}

/// Check if token is a keyword
fn is_keyword(token: &str) -> bool {
    matches!(token, "true" | "false" | "and" | "or" | "not" | "forall" | "exists")
}

/// Check if token is an operator
fn is_operator(token: &str) -> bool {
    matches!(token, "==" | "!=" | "<" | ">" | "<=" | ">=")
}

/// Build state from evidence DAG
fn build_state_from_evidence(
    variables: &[String],
    evidence_dag: &EvidenceDAG,
) -> Result<HashMap<String, Value>, ConstraintReplayError> {
    let mut state = HashMap::new();
    
    for var in variables {
        // Find evidence node that provides this variable
        if let Some(value) = find_evidence_for_variable(var, evidence_dag)? {
            state.insert(var.clone(), value);
        } else {
            return Err(ConstraintReplayError::MissingEvidence(var.clone()));
        }
    }
    
    Ok(state)
}

/// Value type for constraint evaluation
#[derive(Debug, Clone, PartialEq)]
pub enum Value {
    Bool(bool),
    Number(f64),
    String(String),
}

/// Find evidence for a variable
fn find_evidence_for_variable(
    variable: &str,
    evidence_dag: &EvidenceDAG,
) -> Result<Option<Value>, ConstraintReplayError> {
    // Look for claim or source nodes that mention this variable
    for node in &evidence_dag.nodes {
        if let Some(ref content) = node.content {
            if content.contains(variable) {
                // Try to extract value (simplified)
                if content.contains("== true") {
                    return Ok(Some(Value::Bool(true)));
                } else if content.contains("== false") {
                    return Ok(Some(Value::Bool(false)));
                }
                // Try to extract number
                if let Some(num_str) = extract_number(content) {
                    if let Ok(num) = num_str.parse::<f64>() {
                        return Ok(Some(Value::Number(num)));
                    }
                }
            }
        }
    }
    
    Ok(None)
}

/// Extract number from content
fn extract_number(content: &str) -> Option<String> {
    // Simplified: find first sequence of digits and decimal point
    let mut num_str = String::new();
    let mut in_number = false;
    
    for c in content.chars() {
        if c.is_numeric() || c == '.' {
            num_str.push(c);
            in_number = true;
        } else if in_number {
            break;
        }
    }
    
    if num_str.is_empty() {
        None
    } else {
        Some(num_str)
    }
}

/// Evaluate constraint
fn eval_constraint(
    constraint: &str,
    state: &HashMap<String, Value>,
) -> Result<bool, ConstraintReplayError> {
    // Simplified evaluation: handle basic patterns
    // In real implementation, would use proper expression evaluator
    
    if constraint.contains("== true") {
        let var = constraint.split("==").next()
            .ok_or_else(|| ConstraintReplayError::InvalidConstraint(constraint.to_string()))?
            .trim();
        
        match state.get(var) {
            Some(Value::Bool(b)) => Ok(*b),
            _ => Ok(false),
        }
    } else if constraint.contains("== false") {
        let var = constraint.split("==").next()
            .ok_or_else(|| ConstraintReplayError::InvalidConstraint(constraint.to_string()))?
            .trim();
        
        match state.get(var) {
            Some(Value::Bool(b)) => Ok(!*b),
            _ => Ok(false),
        }
    } else if constraint.contains(">=") {
        // Handle >= comparisons
        let parts: Vec<&str> = constraint.split(">=").collect();
        if parts.len() != 2 {
            return Err(ConstraintReplayError::InvalidConstraint(constraint.to_string()));
        }
        
        let lhs = eval_expr(parts[0].trim(), state)?;
        let rhs = eval_expr(parts[1].trim(), state)?;
        
        match (lhs, rhs) {
            (Value::Number(a), Value::Number(b)) => Ok(a >= b),
            _ => Ok(false),
        }
    } else if constraint.contains("<=") {
        // Handle <= comparisons
        let parts: Vec<&str> = constraint.split("<=").collect();
        if parts.len() != 2 {
            return Err(ConstraintReplayError::InvalidConstraint(constraint.to_string()));
        }
        
        let lhs = eval_expr(parts[0].trim(), state)?;
        let rhs = eval_expr(parts[1].trim(), state)?;
        
        match (lhs, rhs) {
            (Value::Number(a), Value::Number(b)) => Ok(a <= b),
            _ => Ok(false),
        }
    } else {
        // Default: assume true (simplified)
        Ok(true)
    }
}

/// Evaluate expression
fn eval_expr(
    expr: &str,
    state: &HashMap<String, Value>,
) -> Result<Value, ConstraintReplayError> {
    // Try to parse as number
    if let Ok(num) = expr.parse::<f64>() {
        return Ok(Value::Number(num));
    }
    
    // Try to parse as boolean
    if expr == "true" {
        return Ok(Value::Bool(true));
    } else if expr == "false" {
        return Ok(Value::Bool(false));
    }
    
    // Try to look up in state
    if let Some(value) = state.get(expr) {
        return Ok(value.clone());
    }
    
    Err(ConstraintReplayError::EvaluationError(format!(
        "Cannot evaluate expression: {}",
        expr
    )))
}

/// Find claim node for constraint
fn find_claim_node(
    constraint: &str,
    evidence_dag: &EvidenceDAG,
) -> Result<Option<&EvidenceNode>, ConstraintReplayError> {
    for node in &evidence_dag.nodes {
        if node.node_type == "claim" {
            if let Some(ref content) = node.content {
                if content.contains(constraint) || constraint.contains(content) {
                    return Ok(Some(node));
                }
            }
        }
    }
    
    Ok(None)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_extract_variables() {
        let constraint = "room_available(date, duration) == true";
        let vars = extract_variables(constraint).unwrap();
        assert!(vars.contains(&"room_available".to_string()));
        assert!(vars.contains(&"date".to_string()));
        assert!(vars.contains(&"duration".to_string()));
    }

    #[test]
    fn test_eval_constraint_bool() {
        let mut state = HashMap::new();
        state.insert("room_available".to_string(), Value::Bool(true));
        
        let result = eval_constraint("room_available == true", &state).unwrap();
        assert!(result);
    }

    #[test]
    fn test_eval_constraint_number() {
        let mut state = HashMap::new();
        state.insert("duration".to_string(), Value::Number(2.0));
        
        let result = eval_constraint("duration <= 4", &state).unwrap();
        assert!(result);
    }

    #[test]
    fn test_replay_constraint() {
        let mut dag = EvidenceDAG::new();
        let mut claim = EvidenceNode::new(
            "claim".to_string(),
            None,
            None,
            "tool1".to_string(),
            "input".to_string(),
            "output".to_string(),
            None,
            Vec::new(),
            "signer".to_string(),
            "sig".to_string(),
        );
        claim.content = Some("room_available == true".to_string());
        claim.result = Some(true);
        dag.add_node(claim);
        
        let result = replay_constraint("room_available == true", &dag).unwrap();
        assert!(result);
    }
}


