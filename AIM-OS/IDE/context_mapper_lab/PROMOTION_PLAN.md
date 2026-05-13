# Context Mapper Lab — Promotion Plan (Phase 2A)

**Purpose:** Prepare the proven mapper for future migration into the SAIOS kernel (`src-tauri/src/context_mapper/`) by separating production-worthy core from lab-only harness code.

**Status:** Lab frozen through Phase 1M. This document defines the handoff boundary.

---

## 1. Production-candidate modules (ready for promotion)

These files contain the deterministic mapper logic and no harness/printing. They are the units to move into a future `context_mapper` crate or `src-tauri/src/context_mapper/` subtree.

| File | Role |
|------|------|
| `src/types.rs` | Core types: `Contract`, `ExtractedFile`, `ImportRef`, `ParseConfidence`, `ContractExtractor`. |
| `src/extractor.rs` | Tree-sitter–based extraction: imports, public contracts (struct/enum/trait/fn/type/const). |
| `src/imports.rs` | Import normalization: raw `use` lines → `ImportRef` (grouped, alias, glob). |
| `src/resolver.rs` | Local crate resolution: path→file, single-hop re-exports, grouped submodule expansion. |
| `src/symbol_usage.rs` | Symbol-driven slicing: collect usage from target source, prune dependency contracts. |
| `src/envelope.rs` | System envelope: build + deterministic XML-style render; provenance by source path. |
| `src/lib.rs` | Library surface: re-exports the above. This is the single entry point for promotion. |

**Dependencies (must move or be satisfied in kernel):** `tree-sitter`, `tree-sitter-rust`, `regex`. Build: `cc` for tree-sitter. No Tauri or daemon deps.

---

## 2. Lab-only / harness code (do not promote as-is)

| Item | Role |
|------|------|
| `src/main.rs` | CLI harness: single-file run, gauntlet mode, all terminal printing, `RunResult`/summary table. |
| `fixtures/` | Synthetic crates: `basic_crate/`, `reexport_crate/` for tests and demos. |
| `sample.rs` | Ad hoc sample file at repo root (if still used). |

The production kernel will not use `main.rs` or fixtures; it will call the library API (extractor → imports → resolve → slice → envelope) from Tauri/command path.

---

## 3. Current known limitations

- **Re-exports:** Single-hop only. Multi-hop `pub use A → B → C` is not followed.
- **Resolution:** Crate-local only. No `std`/external crate resolution; no `path` or workspace crate mapping.
- **Grouped submodules:** Only module-like (lowercase) symbols are expanded to `<base>/<symbol>.rs` or `<base>/<symbol>/mod.rs`. Type-only imports (e.g. single type from a module) are not expanded to submodules.
- **Glob imports:** `use crate::foo::*` is normalized but not expanded to a list of symbols; pruning is name-based from target source.
- **Macros/cfg:** No macro expansion; `#[cfg]` is not evaluated. Extractor may see both branches of `cfg`-gated code.
- **Caching:** None. Every request recomputes extraction and resolution.
- **IO:** Extractor and resolver assume file paths and `std::fs::read_to_string`. Kernel may need a small IO abstraction if reading from virtual or in-memory buffers.

---

## 4. Next steps before production integration

1. **Copy or subtree:** Move the production-candidate files (or the whole `src/` minus `main.rs`) into `src-tauri/src/context_mapper/` (or a sibling crate `context_mapper`), preserving module layout.
2. **Crate boundary:** Add `context_mapper` as a library dependency of the Tauri app; replace any `context_mapper_lab` reference with `context_mapper`.
3. **API surface:** Keep the same public API used by the lab (`TreeSitterExtractor`, `parse_imports`, `resolve_import_refs`, `expand_grouped_submodules`, `re_export_resolve`, `slice_contracts`, `SystemEnvelope::new` + `render_xml`). No behavioral change.
4. **IO (optional):** If the kernel needs to feed content from non-filesystem sources, introduce a thin `ReadSource` trait or pass `(path, contents)` everywhere and keep file reading at the call site.
5. **Testing:** After promotion, run the existing lab harness against the same fixtures and real SAIOS paths to confirm parity; or add a small integration test in the kernel that builds an envelope for one real file.

---

## 5. Summary

| Category | Files |
|----------|--------|
| **Production-candidate** | `src/types.rs`, `src/extractor.rs`, `src/imports.rs`, `src/resolver.rs`, `src/symbol_usage.rs`, `src/envelope.rs`, `src/lib.rs` |
| **Lab-only** | `src/main.rs`, `fixtures/`, `sample.rs` |

The mapper core is ready to promote; the lab remains the place for harness evolution and fixture-based validation.
