//! DAG Scheduler: Ready set formation and topological execution
//!
//! This module implements the DAG scheduler for Core-PLIx:
//! - Ready set formation: `ready(G, S_done) = { v ∈ V | ∀(u→v)∈E. u ∈ S_done } \ S_done`
//! - Topological execution: Execute steps in topological order

use std::collections::HashSet;
use crate::types::{PlanDAG, StepId};

/// Ready set formation: `ready(G, S_done) = { v ∈ V | ∀(u→v)∈E. u ∈ S_done } \ S_done`
///
/// Returns the set of vertices whose dependencies are all satisfied
pub fn ready_set(
    graph: &PlanDAG,
    done: &HashSet<StepId>,
) -> HashSet<StepId> {
    graph.vertices
        .iter()
        .filter(|v| {
            // All incoming edges (dependencies) must be in done set
            graph.incoming(v).all(|u| done.contains(u))
        })
        .filter(|v| !done.contains(v)) // Exclude already done steps
        .cloned()
        .collect()
}

/// Execute plan in topological order
///
/// Returns the order of execution (topological sort)
pub fn topological_order(graph: &PlanDAG) -> Result<Vec<StepId>, String> {
    if !graph.is_acyclic() {
        return Err("Graph contains cycles".to_string());
    }

    let mut result = Vec::new();
    let mut done = HashSet::new();
    let mut remaining: HashSet<StepId> = graph.vertices.clone();

    while !remaining.is_empty() {
        let ready = ready_set(graph, &done);
        
        if ready.is_empty() {
            // Should not happen if graph is acyclic
            return Err("No ready steps but graph not empty (possible cycle)".to_string());
        }

        // Add ready steps to result (order within ready set is arbitrary)
        for step_id in &ready {
            result.push(step_id.clone());
            done.insert(step_id.clone());
            remaining.remove(step_id);
        }
    }

    Ok(result)
}

/// Get reverse topological order (for compensation)
pub fn reverse_topological_order(graph: &PlanDAG) -> Result<Vec<StepId>, String> {
    let mut order = topological_order(graph)?;
    order.reverse();
    Ok(order)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_ready_set_empty() {
        let mut dag = PlanDAG::new();
        dag.add_vertex("a".to_string());
        dag.add_vertex("b".to_string());
        
        let done = HashSet::new();
        let ready = ready_set(&dag, &done);
        
        // Both should be ready (no dependencies)
        assert_eq!(ready.len(), 2);
        assert!(ready.contains("a"));
        assert!(ready.contains("b"));
    }

    #[test]
    fn test_ready_set_with_dependencies() {
        let mut dag = PlanDAG::new();
        dag.add_vertex("a".to_string());
        dag.add_vertex("b".to_string());
        dag.add_vertex("c".to_string());
        dag.add_edge("a".to_string(), "b".to_string());
        dag.add_edge("b".to_string(), "c".to_string());
        
        let mut done = HashSet::new();
        let ready1 = ready_set(&dag, &done);
        
        // Only "a" should be ready (no dependencies)
        assert_eq!(ready1.len(), 1);
        assert!(ready1.contains("a"));
        
        // Mark "a" as done
        done.insert("a".to_string());
        let ready2 = ready_set(&dag, &done);
        
        // Now "b" should be ready
        assert_eq!(ready2.len(), 1);
        assert!(ready2.contains("b"));
        
        // Mark "b" as done
        done.insert("b".to_string());
        let ready3 = ready_set(&dag, &done);
        
        // Now "c" should be ready
        assert_eq!(ready3.len(), 1);
        assert!(ready3.contains("c"));
    }

    #[test]
    fn test_topological_order() {
        let mut dag = PlanDAG::new();
        dag.add_vertex("a".to_string());
        dag.add_vertex("b".to_string());
        dag.add_vertex("c".to_string());
        dag.add_edge("a".to_string(), "b".to_string());
        dag.add_edge("b".to_string(), "c".to_string());
        
        let order = topological_order(&dag).unwrap();
        
        // Order should be: a, b, c (or compatible)
        assert_eq!(order.len(), 3);
        assert_eq!(order[0], "a");
        assert_eq!(order[1], "b");
        assert_eq!(order[2], "c");
    }

    #[test]
    fn test_reverse_topological_order() {
        let mut dag = PlanDAG::new();
        dag.add_vertex("a".to_string());
        dag.add_vertex("b".to_string());
        dag.add_vertex("c".to_string());
        dag.add_edge("a".to_string(), "b".to_string());
        dag.add_edge("b".to_string(), "c".to_string());
        
        let order = reverse_topological_order(&dag).unwrap();
        
        // Reverse order should be: c, b, a (for compensation)
        assert_eq!(order.len(), 3);
        assert_eq!(order[0], "c");
        assert_eq!(order[1], "b");
        assert_eq!(order[2], "a");
    }
}

