//! Reference Interpreter for Core-PLIx Semantics v0.1
//!
//! This module implements a reference interpreter for Core-PLIx based on
//! the formal semantics defined in `core_semantics_v01_final.md`.
//!
//! # Architecture
//!
//! - **Types**: Core types (State, EvLog, Config, etc.)
//! - **Resolver**: Namespace resolution (Σ)
//! - **DAG Scheduler**: Ready set formation, topological execution
//! - **Retry/Fallback**: Retry/fallback logic with precedence
//! - **Compensation**: Compensation engine (reverse topological order)
//! - **Effect Checker**: Effect & confidence checking
//! - **Executor**: Step execution
//! - **Interpreter**: Main interpreter loop
//!
//! # Example
//!
//! ```rust
//! use plix_ref_interpreter::*;
//!
//! let intent = parse_intent("...")?;
//! let resolver = Resolver::new();
//! let initial_state = State::new();
//!
//! let (final_state, evidence_log) = interpret(&intent, initial_state, &resolver)?;
//! ```

pub mod types;
pub mod resolver;
pub mod dag_scheduler;
pub mod retry_fallback;
pub mod compensation;
pub mod effect_checker;
pub mod executor;
pub mod interpreter;

pub use interpreter::{interpret, Intent, Step};
pub use types::{State, EvLog, Config, StepId, EvidenceEntry, Value, PlanDAG};
pub use resolver::{Resolver, PrimAction, Effect};

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_basic_interpretation() {
        // TODO: Implement basic interpretation test
    }
}

