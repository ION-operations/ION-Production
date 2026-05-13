//! Phase 2C — Kernel-facing entry surface for the Context Mapper.
//! One clean callable door: build envelope for a target file with explicit paths.
//! No router, webview, or daemon integration.

use std::fs;
use std::path::Path;

use super::envelope::SystemEnvelope;
use super::extractor::TreeSitterExtractor;
use super::imports::parse_imports;
use super::resolver::{
    expand_grouped_submodules, re_export_resolve, resolve_import_refs,
};
use super::symbol_usage::slice_contracts;
use super::types::ContractExtractor;

/// Minimal error boundary for kernel callers.
#[derive(Debug)]
pub enum ContextMapperError {
    /// I/O error (e.g. file not found, permission denied).
    Io(std::io::Error),
}

impl std::fmt::Display for ContextMapperError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            ContextMapperError::Io(e) => write!(f, "context_mapper io: {}", e),
        }
    }
}

impl std::error::Error for ContextMapperError {
    fn source(&self) -> Option<&(dyn std::error::Error + 'static)> {
        match self {
            ContextMapperError::Io(e) => Some(e),
        }
    }
}

impl From<std::io::Error> for ContextMapperError {
    fn from(e: std::io::Error) -> Self {
        ContextMapperError::Io(e)
    }
}

/// Build a typed system envelope for the target file.
/// Primary API: read target → extract → resolve local deps → collect dep contracts → slice → envelope.
pub fn build_envelope_for_file(
    target_path: &Path,
    crate_root: &Path,
) -> Result<SystemEnvelope, ContextMapperError> {
    let contents = fs::read_to_string(target_path)?;
    let path_str = target_path.to_string_lossy().into_owned();

    let extractor = TreeSitterExtractor::new();
    let extracted = extractor.extract(&path_str, &contents);

    let refs = parse_imports(&extracted.imports);
    let mut dep_paths = resolve_import_refs(crate_root, &refs);
    for p in expand_grouped_submodules(crate_root, &refs) {
        if !dep_paths.iter().any(|q| q == &p) {
            dep_paths.push(p);
        }
    }
    for p in re_export_resolve(crate_root, &dep_paths) {
        if !dep_paths.iter().any(|q| q == &p) {
            dep_paths.push(p);
        }
    }

    let mut dep_contracts: Vec<super::types::Contract> = Vec::new();
    for dep_path in &dep_paths {
        let dep_contents = match fs::read_to_string(dep_path) {
            Ok(c) => c,
            Err(_) => continue,
        };
        let dep_extracted = extractor.extract(&dep_path.to_string_lossy(), &dep_contents);
        dep_contracts.extend(dep_extracted.contracts);
    }

    let pruned = slice_contracts(&contents, dep_contracts);

    let envelope = SystemEnvelope::new(
        &path_str,
        &contents,
        pruned,
        extracted.confidence,
        &dep_paths,
    );
    Ok(envelope)
}

/// Build a rendered (XML-style) envelope string for the target file.
/// Convenience wrapper for later injection use.
pub fn build_rendered_envelope_for_file(
    target_path: &Path,
    crate_root: &Path,
) -> Result<String, ContextMapperError> {
    let envelope = build_envelope_for_file(target_path, crate_root)?;
    Ok(envelope.render_xml())
}
