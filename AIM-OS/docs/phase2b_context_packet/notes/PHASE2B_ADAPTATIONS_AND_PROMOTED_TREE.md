# Phase 2B already performed: adaptations and promoted tree

## Promoted tree (src-tauri/src/context_mapper/)

```
context_mapper/
├── mod.rs
├── types.rs
├── extractor.rs
├── imports.rs
├── resolver.rs
├── symbol_usage.rs
└── envelope.rs
```

## Manifest changes (Phase 2B)

- **src-tauri/Cargo.toml**
  - `[build-dependencies]`: added `cc = "1.0"`.
  - `[dependencies]`: added `tree-sitter = "0.26"`, `tree-sitter-rust = "0.24"` (regex was already present).

- **src-tauri/src/lib.rs**
  - Added one line: `pub mod context_mapper;` (with other `pub mod` declarations).

- No workspace Cargo.toml; SAIOS is a single crate.

## Exact tiny adaptations (crate boundary only)

1. **Import paths:** Every internal reference to the lab’s crate root (`crate::types`, `crate::types::ImportRef`, etc.) was changed to `super::types` (or the appropriate `super::` path) so the promoted code lives under `saios::context_mapper` and does not depend on a top-level `types` in the kernel crate.

2. **resolver.rs:** `refs: &[crate::types::ImportRef]` → `refs: &[super::types::ImportRef]`; `extracted: &crate::types::ExtractedFile` → `extracted: &super::types::ExtractedFile`; added `use super::types::{ExtractedFile, ImportRef}` at top.

3. **imports.rs:** `use crate::types::ImportRef` → `use super::types::ImportRef`.

4. **extractor.rs:** `use crate::types::{...}` → `use super::types::{...}`.

5. **symbol_usage.rs:** `use crate::types::Contract` → `use super::types::Contract`.

6. **envelope.rs:** `use crate::types::{Contract, ParseConfidence}` and the legacy block `use crate::types::{ExtractedFile}` → single `use super::types::{Contract, ExtractedFile, ParseConfidence}` at top.

7. **mod.rs:** Same re-exports as the lab’s `lib.rs`, plus `Envelope` and `EnvelopeMeta` so the public surface matches.

No logic changes, no new dependencies beyond tree-sitter/cc, no router/webview/daemon wiring.

## Compile output (narrowest meaningful)

From `src-tauri`: `cargo build 2>&1` → exit code 0; "Finished `dev` profile [unoptimized + debuginfo] target(s)". Warnings are in existing SAIOS modules only, not in context_mapper.
