//! Strike 1 — Symbol usage (shape only).
//! Inbound callers and usage analysis not implemented yet.

use crate::types::Contract;

/// Placeholder for tracking where a symbol is used.
/// No implementation in Phase 1.
#[derive(Debug, Clone)]
pub struct SymbolUsage {
    pub symbol: String,
    pub references: Vec<String>,
}

/// Placeholder: no analysis in Phase 1.
pub fn collect_usage(_contracts: &[Contract]) -> Vec<SymbolUsage> {
    Vec::new()
}
