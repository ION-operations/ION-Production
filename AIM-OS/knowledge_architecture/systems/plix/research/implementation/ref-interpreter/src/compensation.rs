//! Compensation: Enhanced compensation engine
//!
//! This module implements enhanced compensation for Core-PLIx:
//! - Reverse topological order execution
//! - Left-inverse assumption (Assumption A1)
//! - Compensation evidence tracking

use crate::types::{PlanDAG, StepId};
use crate::dag_scheduler::reverse_topological_order;

/// Compensation plan
#[derive(Debug, Clone)]
pub struct CompensationPlan {
    /// Steps to compensate (in reverse topological order)
    pub steps: Vec<StepId>,
}

impl CompensationPlan {
    /// Create compensation plan from DAG and done steps
    pub fn from_dag(
        dag: &PlanDAG,
        done: &std::collections::HashSet<StepId>,
        compensable: &std::collections::HashSet<StepId>,
    ) -> Result<Self, String> {
        let reverse_order = reverse_topological_order(dag)?;
        
        let steps = reverse_order
            .into_iter()
            .filter(|step_id| done.contains(step_id) && compensable.contains(step_id))
            .collect();
        
        Ok(Self { steps })
    }
}

/// Compensation result
#[derive(Debug, Clone)]
pub enum CompensationResult {
    /// Compensation succeeded
    Success,
    /// Compensation failed at step
    Failed {
        step_id: StepId,
        error: String,
    },
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashSet;

    #[test]
    fn test_compensation_plan() {
        let mut dag = PlanDAG::new();
        dag.add_vertex("a".to_string());
        dag.add_vertex("b".to_string());
        dag.add_vertex("c".to_string());
        dag.add_edge("a".to_string(), "b".to_string());
        dag.add_edge("b".to_string(), "c".to_string());
        
        let mut done = HashSet::new();
        done.insert("a".to_string());
        done.insert("b".to_string());
        done.insert("c".to_string());
        
        let mut compensable = HashSet::new();
        compensable.insert("a".to_string());
        compensable.insert("c".to_string());
        
        let plan = CompensationPlan::from_dag(&dag, &done, &compensable).unwrap();
        
        // Should have steps c, a (in reverse order, only compensable)
        assert_eq!(plan.steps.len(), 2);
        assert_eq!(plan.steps[0], "c");
        assert_eq!(plan.steps[1], "a");
    }
}

