//! Strike 1 — Symbol usage and v1 fixpoint contract slicer.
//! Wildcard imports (use crate::bar::*) are not proof of use. Only keep items whose identifiers appear in the active text.

use crate::types::Contract;
use regex::Regex;
use std::collections::HashSet;

/// Placeholder for tracking where a symbol is used.
#[derive(Debug, Clone)]
pub struct SymbolUsage {
    pub symbol: String,
    pub references: Vec<String>,
}

/// Placeholder: no analysis in Phase 1.
pub fn collect_usage(_contracts: &[Contract]) -> Vec<SymbolUsage> {
    Vec::new()
}

/// Build the text of a contract for inclusion in active_text (name + signature so transitive refs appear).
fn contract_text(c: &Contract) -> String {
    let sig = c.signature.as_deref().unwrap_or("");
    format!("{} {}", c.name, sig)
}

/// v1 fixpoint slicer: keep only dependency contracts whose names appear as distinct identifiers in
/// the target source or in already-kept contract text. Repeat until no new contracts are added.
pub fn slice_contracts(target_source: &str, dep_contracts: Vec<Contract>) -> Vec<Contract> {
    let mut active_text = target_source.to_string();
    let mut remaining: Vec<Contract> = dep_contracts;
    let mut kept: Vec<Contract> = Vec::new();
    let mut seen_names: HashSet<String> = HashSet::new();

    loop {
        let mut changed = false;
        let mut still_remaining = Vec::new();
        for c in remaining {
            if seen_names.contains(&c.name) {
                still_remaining.push(c);
                continue;
            }
            let pattern = format!(r"\b{}\b", regex::escape(&c.name));
            let re = match Regex::new(&pattern) {
                Ok(r) => r,
                Err(_) => {
                    still_remaining.push(c);
                    continue;
                }
            };
            if re.is_match(&active_text) {
                active_text.push_str(&contract_text(&c));
                active_text.push(' ');
                seen_names.insert(c.name.clone());
                kept.push(c);
                changed = true;
            } else {
                still_remaining.push(c);
            }
        }
        remaining = still_remaining;
        if !changed {
            break;
        }
    }
    kept
}
