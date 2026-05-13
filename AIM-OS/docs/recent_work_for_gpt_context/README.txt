Recent work for GPT context — zip contents

Location in real repo (SAIOS):
  src-tauri/src/context_mapper/
  - api.rs   (NEW in Phase 2C)
  - mod.rs   (MODIFIED in Phase 2C — added pub mod api; and pub use api::{...})

Phase 2C: Kernel-facing entry for the promoted Context Mapper.
- build_envelope_for_file(target_path, crate_root) -> Result<SystemEnvelope, ContextMapperError>
- build_rendered_envelope_for_file(target_path, crate_root) -> Result<String, ContextMapperError>
- ContextMapperError::Io(std::io::Error)

No router/webview/daemon integration. One callable door only.
Full context_mapper (types, envelope, extractor, imports, resolver, symbol_usage) lives in SAIOS repo; this zip contains only the altered files for Phase 2C.
