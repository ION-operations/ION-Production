//! Core types for Core-PLIx reference interpreter
//!
//! This module defines the fundamental types used throughout the interpreter:
//! - State: Variable-to-value mapping
//! - EvLog: Evidence log (append-only monoid)
//! - Config: Process configuration (state, evidence, ready set, done, failed)
//! - EvidenceEntry: Individual evidence log entry

use std::collections::{HashMap, HashSet};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

/// State: Partial map from variables to values
pub type State = HashMap<String, Value>;

/// Evidence log: Append-only monoid with hash-chaining
pub type EvLog = Vec<EvidenceEntry>;

/// Step identifier
pub type StepId = String;

/// Process configuration: ⟨σ, ε, Q, done, failed⟩
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Config {
    /// Current state
    pub state: State,
    /// Evidence log
    pub evidence_log: EvLog,
    /// Ready set of runnable steps
    pub ready_set: HashSet<StepId>,
    /// Completed steps
    pub done: HashSet<StepId>,
    /// Failed steps
    pub failed: HashSet<StepId>,
}

impl Config {
    /// Create new configuration
    pub fn new(initial_state: State) -> Self {
        Self {
            state: initial_state,
            evidence_log: Vec::new(),
            ready_set: HashSet::new(),
            done: HashSet::new(),
            failed: HashSet::new(),
        }
    }

    /// Append evidence to log (monoid operation)
    pub fn append_evidence(&mut self, entry: EvidenceEntry) {
        self.evidence_log.push(entry);
    }
}

/// Value type
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(tag = "type")]
pub enum Value {
    Bool(bool),
    Number(f64),
    String(String),
    Tag(String),
    Entity(String),
    Action(String),
    Capability(String),
    Null,
}

/// Evidence entry: (time, tool, input_hash, output_hash, parent_hash)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EvidenceEntry {
    /// Unique identifier
    pub id: String,
    /// Step ID (if applicable)
    pub step_id: Option<StepId>,
    /// Contract ID (if applicable)
    pub contract_id: Option<String>,
    /// Timestamp
    pub time: DateTime<Utc>,
    /// Tool identifier
    pub tool: String,
    /// Input hash
    pub input_hash: String,
    /// Output hash
    pub output_hash: String,
    /// Parent hash (for hash-chaining)
    pub parent_hash: Option<String>,
    /// Parent evidence IDs
    pub parents: Vec<String>,
    /// Signer identifier
    pub signer: String,
    /// Cryptographic signature
    pub sig: String,
}

impl EvidenceEntry {
    /// Create new evidence entry
    pub fn new(
        step_id: Option<StepId>,
        contract_id: Option<String>,
        tool: String,
        input_hash: String,
        output_hash: String,
        parent_hash: Option<String>,
        parents: Vec<String>,
        signer: String,
        sig: String,
    ) -> Self {
        Self {
            id: Uuid::new_v4().to_string(),
            step_id,
            contract_id,
            time: Utc::now(),
            tool,
            input_hash,
            output_hash,
            parent_hash,
            parents,
            signer,
            sig,
        }
    }

    /// Compute hash of this entry
    pub fn compute_hash(&self) -> String {
        use sha2::{Sha256, Digest};
        let mut hasher = Sha256::new();
        hasher.update(self.id.as_bytes());
        hasher.update(self.time.to_rfc3339().as_bytes());
        hasher.update(self.tool.as_bytes());
        hasher.update(self.input_hash.as_bytes());
        hasher.update(self.output_hash.as_bytes());
        if let Some(ref parent) = self.parent_hash {
            hasher.update(parent.as_bytes());
        }
        format!("{:x}", hasher.finalize())
    }
}

/// Plan DAG representation
#[derive(Debug, Clone)]
pub struct PlanDAG {
    /// Vertices (step IDs)
    pub vertices: HashSet<StepId>,
    /// Edges (dependencies): (from, to)
    pub edges: Vec<(StepId, StepId)>,
}

impl PlanDAG {
    /// Create new DAG
    pub fn new() -> Self {
        Self {
            vertices: HashSet::new(),
            edges: Vec::new(),
        }
    }

    /// Add vertex
    pub fn add_vertex(&mut self, step_id: StepId) {
        self.vertices.insert(step_id);
    }

    /// Add edge (dependency)
    pub fn add_edge(&mut self, from: StepId, to: StepId) {
        self.edges.push((from, to));
    }

    /// Get incoming edges for a vertex
    pub fn incoming(&self, v: &StepId) -> impl Iterator<Item = &StepId> {
        self.edges
            .iter()
            .filter(move |(_, to)| to == v)
            .map(|(from, _)| from)
    }

    /// Check if DAG is acyclic
    pub fn is_acyclic(&self) -> bool {
        // Simple DFS-based cycle detection
        let mut visited = HashSet::new();
        let mut rec_stack = HashSet::new();

        for v in &self.vertices {
            if !visited.contains(v) {
                if self.has_cycle(v, &mut visited, &mut rec_stack) {
                    return false;
                }
            }
        }
        true
    }

    fn has_cycle(
        &self,
        v: &StepId,
        visited: &mut HashSet<StepId>,
        rec_stack: &mut HashSet<StepId>,
    ) -> bool {
        visited.insert(v.clone());
        rec_stack.insert(v.clone());

        for u in self.incoming(v) {
            if !visited.contains(u) {
                if self.has_cycle(u, visited, rec_stack) {
                    return true;
                }
            } else if rec_stack.contains(u) {
                return true;
            }
        }

        rec_stack.remove(v);
        false
    }
}

impl Default for PlanDAG {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_config_new() {
        let state = State::new();
        let config = Config::new(state);
        assert_eq!(config.ready_set.len(), 0);
        assert_eq!(config.done.len(), 0);
        assert_eq!(config.failed.len(), 0);
    }

    #[test]
    fn test_evidence_entry_hash() {
        let entry = EvidenceEntry::new(
            Some("step1".to_string()),
            Some("contract1".to_string()),
            "tool1".to_string(),
            "input_hash".to_string(),
            "output_hash".to_string(),
            None,
            Vec::new(),
            "signer1".to_string(),
            "sig1".to_string(),
        );
        let hash = entry.compute_hash();
        assert!(!hash.is_empty());
    }

    #[test]
    fn test_dag_acyclic() {
        let mut dag = PlanDAG::new();
        dag.add_vertex("a".to_string());
        dag.add_vertex("b".to_string());
        dag.add_vertex("c".to_string());
        dag.add_edge("a".to_string(), "b".to_string());
        dag.add_edge("b".to_string(), "c".to_string());
        assert!(dag.is_acyclic());
    }

    #[test]
    fn test_dag_cyclic() {
        let mut dag = PlanDAG::new();
        dag.add_vertex("a".to_string());
        dag.add_vertex("b".to_string());
        dag.add_edge("a".to_string(), "b".to_string());
        dag.add_edge("b".to_string(), "a".to_string());
        assert!(!dag.is_acyclic());
    }
}

