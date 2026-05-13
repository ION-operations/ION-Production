//! Strike 1 — Import normalization (Phase 1H).
//! Parse raw `use` lines into ImportRef; support grouped, alias, glob.

use crate::types::ImportRef;

/// Strip prefix and trailing semicolon from a use line.
fn trim_use_line(s: &str) -> &str {
    let s = s.trim();
    let s = s.strip_prefix("pub use ").unwrap_or(s);
    let s = s.strip_prefix("use ").unwrap_or(s);
    s.trim_end_matches(';').trim()
}

/// True if path is local (crate::).
fn is_local_path(path: &str) -> bool {
    path.starts_with("crate::")
}

/// First segment after crate:: (e.g. "foo" from "crate::foo::Bar").
fn source_module(path: &str) -> Option<String> {
    let after = path.strip_prefix("crate::")?;
    after.split("::").next().map(|s| s.to_string())
}

/// Parse one raw use line into one ImportRef (grouped imports yield one ref with multiple symbols).
pub fn parse_one(raw: &str) -> Option<ImportRef> {
    let s = trim_use_line(raw);
    if s.is_empty() {
        return None;
    }

    let is_glob = s.ends_with("::*") || s.ends_with(" *");
    let (path_str, symbols, alias) = if is_glob {
        let path = s.trim_end_matches('*').trim_end_matches(':').trim_end_matches(':').trim();
        (path.to_string(), Vec::new(), None)
    } else if let Some((left, right)) = s.split_once(" as ") {
        let alias = right.trim().to_string();
        let path_str = left.trim().to_string();
        let symbol = path_str.split("::").last().map(|s| s.to_string()).unwrap_or_default();
        (path_str, vec![symbol], Some(alias))
    } else if let Some(pos) = s.find('{') {
        let path = s[..pos].trim_end_matches(':').trim();
        let rest = s[pos..].trim_start_matches('{').trim_end_matches('}');
        let symbols: Vec<String> = rest
            .split(',')
            .map(|x| x.trim().to_string())
            .filter(|x| !x.is_empty())
            .collect();
        (path.to_string(), symbols, None)
    } else {
        let path_str = s.to_string();
        let symbol = path_str.split("::").last().map(|s| s.to_string()).unwrap_or_default();
        let symbols = if symbol.is_empty() {
            Vec::new()
        } else {
            vec![symbol]
        };
        (path_str, symbols, None)
    };

    Some(ImportRef {
        raw: raw.trim().to_string(),
        normalized: path_str.clone(),
        is_local: is_local_path(&path_str),
        source_module: source_module(&path_str),
        imported_symbols: symbols,
        is_glob,
        alias,
    })
}

/// Parse many raw use lines into normalized ImportRefs. Skips unparseable lines.
pub fn parse_imports(raw: &[String]) -> Vec<ImportRef> {
    raw.iter()
        .filter_map(|s| parse_one(s))
        .collect()
}
