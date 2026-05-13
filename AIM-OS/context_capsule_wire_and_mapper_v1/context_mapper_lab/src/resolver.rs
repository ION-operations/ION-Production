//! Strike 1 — Resolver: basic local module resolution.
//! Re-export chasing and deep graph traversal not implemented yet.

use std::path::{Path, PathBuf};

/// Normalize a raw import line: strip `use ` / `pub use `, trailing `;`, trim.
/// Returns the path part only (e.g. `crate::dummy_models::SampleModel`).
fn normalize_import(s: &str) -> &str {
    let s = s.trim();
    let s = s.strip_prefix("pub use ").unwrap_or(s);
    let s = s.strip_prefix("use ").unwrap_or(s);
    s.trim_end_matches(';').trim()
}

/// True if the normalized path is a local crate import (crate::...).
/// Ignores std::, core::, alloc::, and anything else.
fn is_crate_import(normalized: &str) -> bool {
    normalized.starts_with("crate::")
}

/// Path segments after `crate::` (e.g. "crate::dummy_models::SampleModel" -> ["dummy_models", "SampleModel"]).
fn crate_path_segments(normalized: &str) -> Vec<&str> {
    let after = normalized.strip_prefix("crate::").unwrap_or("");
    after.split("::").filter(|s| !s.is_empty()).collect()
}

/// Resolve a single crate import to a file path, if it exists.
/// Tries iteratively: full path as .rs, full path as /mod.rs, then pop one segment, repeat.
fn resolve_one(crate_root: &Path, segments: &[&str]) -> Option<PathBuf> {
    let mut segs = segments.to_vec();
    while !segs.is_empty() {
        let path: PathBuf = segs.iter().fold(PathBuf::new(), |p, s| p.join(s));
        let as_file = crate_root.join(&path).with_extension("rs");
        if as_file.exists() {
            return Some(as_file);
        }
        let as_mod = crate_root.join(&path).join("mod.rs");
        if as_mod.exists() {
            return Some(as_mod);
        }
        segs.pop();
    }
    None
}

/// Resolve local file paths for `crate::...` imports only.
/// Ignores std::, core::, alloc::, and other non-local imports.
/// Strips `use ` / `pub use ` / trailing `;`, splits by `::`, iteratively
/// tries `<path>.rs` and `<path>/mod.rs` (popping trailing segments), returns
/// first existing match per import, deduplicated.
pub fn resolve_imports(crate_root: &Path, imports: &[String]) -> Vec<PathBuf> {
    let mut out: Vec<PathBuf> = Vec::new();
    for u in imports {
        let normalized = normalize_import(u);
        if !is_crate_import(normalized) {
            continue;
        }
        let segments: Vec<&str> = crate_path_segments(normalized);
        if segments.is_empty() {
            continue;
        }
        if let Some(p) = resolve_one(crate_root, &segments) {
            if !out.iter().any(|q| q == &p) {
                out.push(p);
            }
        }
    }
    out
}

/// Thin wrapper: resolve imports from an ExtractedFile.
pub fn resolve_local_deps(extracted: &crate::types::ExtractedFile, crate_root: &Path) -> Vec<PathBuf> {
    resolve_imports(crate_root, &extracted.imports)
}

/// Placeholder for resolving re-exports and deeper graph.
/// TODO: implement when moving beyond basic local resolution.
pub fn resolve_reexports(_extracted: &crate::types::ExtractedFile) -> Vec<String> {
    Vec::new()
}
