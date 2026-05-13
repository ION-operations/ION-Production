//! Context Mapper — promoted from context_mapper_lab (Phase 2B).
//! Deterministic Rust context envelope: extract, resolve, slice, render.
//! Phase 2C: kernel-facing entry in api.rs.

pub mod api;
pub mod envelope;
pub mod extractor;
pub mod imports;
pub mod resolver;
pub mod symbol_usage;
pub mod types;

pub use api::{build_envelope_for_file, build_rendered_envelope_for_file, ContextMapperError};
pub use envelope::{Envelope, EnvelopeMeta, SystemEnvelope};
pub use extractor::TreeSitterExtractor;
pub use types::{Contract, ContractExtractor, ExtractedFile, ImportRef, ParseConfidence};
pub use imports::{parse_imports, parse_one};
pub use resolver::{
    expand_grouped_submodules, re_export_resolve, resolve_import_refs, resolve_imports,
    resolve_local_deps, resolve_reexports,
};
pub use symbol_usage::{collect_usage, slice_contracts, SymbolUsage};
