//! Strike 1 — Context Mapper lab.
//! Standalone Rust harness: one file in, contracts out.
//!
//! **Promotion (Phase 2A):** This library is the production-candidate surface. The modules
//! below (types, extractor, imports, resolver, symbol_usage, envelope) are intended for future
//! migration into `src-tauri/src/context_mapper/`. See `PROMOTION_PLAN.md`.

pub mod envelope;
pub mod extractor;
pub mod imports;
pub mod resolver;
pub mod symbol_usage;
pub mod types;

pub use envelope::{Envelope, SystemEnvelope};
pub use extractor::TreeSitterExtractor;
pub use types::{Contract, ContractExtractor, ExtractedFile, ImportRef, ParseConfidence};
pub use imports::{parse_imports, parse_one};
pub use resolver::{expand_grouped_submodules, re_export_resolve, resolve_import_refs, resolve_imports, resolve_local_deps, resolve_reexports};
pub use symbol_usage::{collect_usage, slice_contracts, SymbolUsage};
