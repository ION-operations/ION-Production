//! Strike 1 — Resolver: basic local module resolution + single-hop re-exports (Phase 1I).
//! Phase 1M: grouped submodule expansion — probe symbol names as submodule files.

use std::path::{Path, PathBuf};
use std::fs;

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

/// Resolve local file paths from normalized ImportRefs (Phase 1H).
/// Uses each ref's normalized path; only refs with is_local are resolved.
pub fn resolve_import_refs(
    crate_root: &Path,
    refs: &[crate::types::ImportRef],
) -> Vec<PathBuf> {
    let mut out: Vec<PathBuf> = Vec::new();
    for r in refs {
        if !r.is_local {
            continue;
        }
        let segments: Vec<&str> = crate_path_segments(&r.normalized);
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

/// True if the symbol looks like a module name (lowercase, not a type).
/// Used to avoid probing for type names as submodule files (Phase 1M).
fn is_module_like_symbol(symbol: &str) -> bool {
    let s = symbol.trim();
    if s.is_empty() {
        return false;
    }
    s.chars().next().map(|c| c.is_ascii_lowercase()).unwrap_or(false)
}

/// Expand grouped import symbols to submodule files when the base path is a module.
/// For e.g. `use crate::actuator::{input, screen, accessibility, process}` we already
/// resolve `crate::actuator` to `actuator/mod.rs`. This adds `actuator/input.rs`,
/// `actuator/screen.rs`, etc. when they exist. Only probes for module-like (lowercase) symbols.
pub fn expand_grouped_submodules(
    crate_root: &Path,
    refs: &[crate::types::ImportRef],
) -> Vec<PathBuf> {
    let mut out: Vec<PathBuf> = Vec::new();
    for r in refs {
        if !r.is_local || r.imported_symbols.is_empty() {
            continue;
        }
        let segments: Vec<&str> = crate_path_segments(&r.normalized);
        if segments.is_empty() {
            continue;
        }
        let base_path = match resolve_one(crate_root, &segments) {
            Some(p) => p,
            None => continue,
        };
        let parent_dir = match base_path.parent() {
            Some(d) => d,
            None => continue,
        };
        for symbol in &r.imported_symbols {
            let sym = symbol.trim();
            if sym.is_empty() || sym == "self" {
                continue;
            }
            if !is_module_like_symbol(sym) {
                continue;
            }
            let as_file = parent_dir.join(sym).with_extension("rs");
            if as_file.exists() {
                if !out.iter().any(|q| q == &as_file) {
                    out.push(as_file);
                }
            }
            let as_mod = parent_dir.join(sym).join("mod.rs");
            if as_mod.exists() {
                if !out.iter().any(|q| q == &as_mod) {
                    out.push(as_mod);
                }
            }
        }
    }
    out
}

/// Thin wrapper: resolve imports from an ExtractedFile (raw strings).
pub fn resolve_local_deps(extracted: &crate::types::ExtractedFile, crate_root: &Path) -> Vec<PathBuf> {
    resolve_imports(crate_root, &extracted.imports)
}

/// Parse simple same-crate `pub use path::...;` from file contents.
/// Returns (module_path, symbols) for each pub use. Only crate:: paths; no wildcard.
fn parse_pub_use_same_crate(contents: &str) -> Vec<(String, Vec<String>)> {
    let mut out = Vec::new();
    for line in contents.lines() {
        let line = line.trim();
        let rest = match line.strip_prefix("pub use ") {
            Some(r) => r.trim_end_matches(';').trim(),
            None => continue,
        };
        if !rest.starts_with("crate::") {
            continue;
        }
        if rest.contains("::*") || rest.ends_with('*') {
            continue;
        }
        if let Some(pos) = rest.find('{') {
            let path = rest[..pos].trim_end_matches(':').trim();
            let inner = rest[pos..].trim_start_matches('{').trim_end_matches('}');
            let symbols: Vec<String> = inner
                .split(',')
                .map(|s| s.trim().to_string())
                .filter(|s| !s.is_empty())
                .collect();
            if !path.is_empty() {
                out.push((path.to_string(), symbols));
            }
        } else {
            let path_str = rest.to_string();
            let segments: Vec<&str> = path_str.split("::").collect();
            if segments.len() >= 2 {
                let module_path = segments[..segments.len() - 1].join("::");
                let symbol = segments[segments.len() - 1].to_string();
                out.push((module_path, vec![symbol]));
            }
        }
    }
    out
}

/// One-hop re-export resolution: from already-resolved files, find files referenced by
/// simple same-crate `pub use`. Returns additional paths not in `resolved_paths`.
pub fn re_export_resolve(
    crate_root: &Path,
    resolved_paths: &[PathBuf],
) -> Vec<PathBuf> {
    let mut out: Vec<PathBuf> = Vec::new();
    for path in resolved_paths {
        let contents = match fs::read_to_string(path) {
            Ok(c) => c,
            Err(_) => continue,
        };
        for (module_path, _symbols) in parse_pub_use_same_crate(&contents) {
            if !module_path.starts_with("crate::") {
                continue;
            }
            let segments: Vec<&str> = crate_path_segments(&module_path);
            if segments.is_empty() {
                continue;
            }
            if let Some(p) = resolve_one(crate_root, &segments) {
                if !resolved_paths.iter().any(|q| q == &p) && !out.iter().any(|q| q == &p) {
                    out.push(p);
                }
            }
        }
    }
    out
}

/// Placeholder for deeper re-export chains.
pub fn resolve_reexports(_extracted: &crate::types::ExtractedFile) -> Vec<String> {
    Vec::new()
}
