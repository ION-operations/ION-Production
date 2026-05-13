//! Strike 1 — Typed system envelope and deterministic XML-style renderer.
//! Phase 1G + 1J: build artifact from target + pruned dependency contracts; provenance by source path.

use crate::types::{Contract, ParseConfidence};
use std::collections::BTreeMap;
use std::path::Path;

/// Escape only what is needed for XML attribute values (e.g. path="...").
/// Do not escape Rust code; the envelope body must contain raw `->`, etc.
fn escape_attr(s: &str) -> String {
    s.replace('&', "&amp;")
        .replace('<', "&lt;")
        .replace('>', "&gt;")
        .replace('"', "&quot;")
}

/// Normalize path for XML output: backslashes to forward slashes.
fn normalize_path(s: &str) -> String {
    s.replace('\\', "/")
}

/// Parse mode string for display.
fn parse_mode_str(c: ParseConfidence) -> &'static str {
    match c {
        ParseConfidence::High => "High",
        ParseConfidence::Degraded => "Degraded",
        ParseConfidence::Fallback => "Fallback",
    }
}

/// Typed system envelope: target file + pruned outbound contracts + metadata.
#[derive(Debug, Clone)]
pub struct SystemEnvelope {
    pub version: String,
    pub intent: String,
    pub edit_rules: Vec<String>,
    pub parse_mode: ParseConfidence,
    /// Resolved dependency file paths (for index).
    pub dependency_paths: Vec<String>,
    /// Pruned dependency contracts only.
    pub outbound_contracts: Vec<Contract>,
    /// Path of the target file (for display).
    pub target_path: String,
    /// Full target file source.
    pub target_source: String,
    /// Optional: symbols from pruned set (for dependency_index summary).
    pub target_symbol_usage: Vec<String>,
}

impl SystemEnvelope {
    /// Build from pipeline outputs.
    pub fn new(
        target_path: impl AsRef<str>,
        target_source: impl AsRef<str>,
        pruned_contracts: Vec<Contract>,
        parse_mode: ParseConfidence,
        dependency_paths: impl IntoIterator<Item = impl AsRef<Path>>,
    ) -> Self {
        let target_symbol_usage: Vec<String> = pruned_contracts.iter().map(|c| c.name.clone()).collect();
        let dependency_paths: Vec<String> = dependency_paths
            .into_iter()
            .map(|p| p.as_ref().to_string_lossy().into_owned())
            .collect();
        SystemEnvelope {
            version: "1.0".to_string(),
            intent: "Active Context Envelope for requested file.".to_string(),
            edit_rules: vec![
                "Modify only the target_file unless explicitly instructed.".to_string(),
                "Treat outbound_contracts as read-only.".to_string(),
                "Preserve public API compatibility unless the task requires otherwise.".to_string(),
                "If context appears incomplete, request additional envelope or directory info.".to_string(),
            ],
            parse_mode,
            dependency_paths,
            outbound_contracts: pruned_contracts,
            target_path: target_path.as_ref().to_string(),
            target_source: target_source.as_ref().to_string(),
            target_symbol_usage,
        }
    }

    /// Render to a deterministic XML-style string. Paths use forward slashes.
    /// No HTML-escaping of Rust code: target source and outbound contracts are raw.
    pub fn render_xml(&self) -> String {
        let mut out = String::new();
        out.push_str(&format!(
            "<system_envelope version=\"{}\">\n",
            escape_attr(&self.version)
        ));
        out.push_str(&format!("  <intent>{}</intent>\n\n", self.intent));
        out.push_str("  <edit_rules>\n");
        for r in &self.edit_rules {
            out.push_str(&format!("    - {}\n", r));
        }
        out.push_str("  </edit_rules>\n\n");
        out.push_str(&format!(
            "  <parse_mode>{}</parse_mode>\n\n",
            parse_mode_str(self.parse_mode)
        ));
        out.push_str("  <dependency_index>\n");
        for p in &self.dependency_paths {
            let path_norm = normalize_path(p);
            out.push_str(&format!("    <dep path=\"{}\"/>\n", escape_attr(&path_norm)));
        }
        out.push_str("  </dependency_index>\n\n");
        out.push_str("  <outbound_contracts>\n");
        let by_source: BTreeMap<String, Vec<&Contract>> = {
            let mut map: BTreeMap<String, Vec<&Contract>> = BTreeMap::new();
            for c in &self.outbound_contracts {
                let key = if c.source_path.is_empty() {
                    "_unknown_".to_string()
                } else {
                    normalize_path(&c.source_path)
                };
                map.entry(key).or_default().push(c);
            }
            map
        };
        for (source_path, contracts) in &by_source {
            out.push_str(&format!("  // --- FROM: {} ---\n", source_path));
            for c in contracts {
                let line = c
                    .signature
                    .as_deref()
                    .unwrap_or(c.name.as_str());
                out.push_str(line);
                out.push_str("\n\n");
            }
        }
        out.push_str("  </outbound_contracts>\n\n");
        let target_path_norm = normalize_path(&self.target_path);
        out.push_str(&format!(
            "  <target_file path=\"{}\">\n",
            escape_attr(&target_path_norm)
        ));
        out.push_str(&self.target_source);
        if !self.target_source.ends_with('\n') {
            out.push('\n');
        }
        out.push_str("  </target_file>\n");
        out.push_str("</system_envelope>\n");
        out
    }
}

// Legacy placeholder for code that may still reference Envelope/EnvelopeMeta.
use crate::types::{ExtractedFile};

#[derive(Debug, Clone)]
pub struct Envelope {
    pub source: String,
    pub file: ExtractedFile,
}

#[derive(Debug, Clone)]
pub struct EnvelopeMeta {
    pub confidence: ParseConfidence,
    pub contract_count: usize,
}

impl Envelope {
    pub fn from_extracted(file: ExtractedFile) -> Self {
        let source = file.path.clone();
        Envelope { source, file }
    }

    pub fn meta(&self) -> EnvelopeMeta {
        EnvelopeMeta {
            confidence: self.file.confidence,
            contract_count: self.file.contracts.len(),
        }
    }
}
