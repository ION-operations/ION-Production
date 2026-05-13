//! Strike 1 — Context Mapper lab.
//! Standalone Rust harness: one file in, contracts out.

pub mod envelope;
pub mod extractor;
pub mod resolver;
pub mod shadow_hook;
pub mod symbol_usage;
pub mod types;

pub use envelope::Envelope;
pub use extractor::TreeSitterExtractor;
pub use types::{Contract, ContractExtractor, ExtractedFile, ParseConfidence};
pub use resolver::{resolve_imports, resolve_local_deps, resolve_reexports};
pub use shadow_hook::{maybe_emit_passive_shadow, PassiveEmitOutcome};
pub use symbol_usage::{collect_usage, SymbolUsage};
