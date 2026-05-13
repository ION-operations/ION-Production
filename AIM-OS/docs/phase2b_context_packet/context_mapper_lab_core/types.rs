//! Strike 1 — Context Mapper lab: core types.
//! ParseConfidence, ExtractedFile, ContractExtractor, ImportRef.

/// Normalized import reference (Phase 1H).
#[derive(Debug, Clone)]
pub struct ImportRef {
    /// Original raw use line.
    pub raw: String,
    /// Normalized path (e.g. `crate::foo` or `crate::bar::Bar`).
    pub normalized: String,
    /// True if path starts with `crate::`.
    pub is_local: bool,
    /// First path segment after `crate::` (e.g. `foo`), if local.
    pub source_module: Option<String>,
    /// Imported symbol names (from grouped or single).
    pub imported_symbols: Vec<String>,
    /// True for `use crate::bar::*;`.
    pub is_glob: bool,
    /// Alias from `Thing as RenamedThing`, if present.
    pub alias: Option<String>,
}

/// Confidence in the parse result for a single file.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ParseConfidence {
    /// Full parse; all expected constructs recognized.
    High,
    /// Parse succeeded but some constructs skipped or simplified.
    Degraded,
    /// Fallback path (e.g. regex or line-based); less reliable.
    Fallback,
}

/// One extracted public contract (signature or declaration shape).
#[derive(Debug, Clone)]
pub struct Contract {
    /// Kind: struct, enum, trait, fn, type, const.
    pub kind: String,
    /// Name of the item (e.g. struct name, function name).
    pub name: String,
    /// Optional signature/signature snippet (e.g. fn foo(x: i32) -> bool).
    pub signature: Option<String>,
    /// Source file path this contract was extracted from (Phase 1J provenance).
    pub source_path: String,
}

/// Result of extracting contracts from a single Rust file.
#[derive(Debug, Clone)]
pub struct ExtractedFile {
    /// Path of the file (as given to the extractor).
    pub path: String,
    /// Use statements (raw lines or normalized form).
    pub imports: Vec<String>,
    /// Top-level public contracts (struct, enum, trait, fn, type, const).
    pub contracts: Vec<Contract>,
    /// Parse confidence for this file.
    pub confidence: ParseConfidence,
}

/// Abstraction for a backend that extracts contracts from Rust source.
pub trait ContractExtractor: Send + Sync {
    /// Extract imports and top-level public declarations from file contents.
    /// path: logical path for reporting; contents: full file text.
    fn extract(&self, path: &str, contents: &str) -> ExtractedFile;
}
