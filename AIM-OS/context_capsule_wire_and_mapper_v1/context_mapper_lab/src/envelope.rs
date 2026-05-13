//! Strike 1 — Envelope types (shape only).
//! No XML or token packing yet; just the structs for future use.

use crate::types::{ExtractedFile, ParseConfidence};

/// Placeholder for a serializable envelope that will carry extracted context.
/// Not serialized in Phase 1.
#[derive(Debug, Clone)]
pub struct Envelope {
    /// Source path or module id.
    pub source: String,
    /// Extracted file data (imports + contracts).
    pub file: ExtractedFile,
}

/// Optional metadata for envelope (e.g. parse confidence summary).
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
