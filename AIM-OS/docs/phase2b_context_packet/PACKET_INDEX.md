# Phase 2B context packet — index

**Purpose:** External review and surgical promotion of the mapper core into `src-tauri/src/context_mapper/` without redesign.
**Canon tier:** **Tier E (evidence snapshot only)** per `docs/CONTEXT_SYSTEM_CANON_REGISTRY_2026-03-05.md`.
**Runtime note:** Do not treat this packet as a live runtime source of truth.

---

## Contents

### A. saios_kernel_tree/
- **TREE_SRC_TAURI_SRC.txt** — Concise tree of `src-tauri/src/`: root entries, modules, context_mapper placement, command/state_machine/etc.
- **lib.rs** — Excerpt of lib.rs showing `pub mod context_mapper` and sibling modules.
- **main.rs** — Binary entry (calls saios_lib::run()).

### B. manifests/
- **context_mapper_lab_Cargo.toml** — Lab crate manifest (tree-sitter, tree-sitter-rust, regex, cc).
- **src-tauri_Cargo.toml** — SAIOS kernel manifest (with Phase 2B additions: cc, tree-sitter, tree-sitter-rust).

No workspace Cargo.toml; SAIOS is a single crate.

### C. context_mapper_lab_core/
Live lab **production-candidate** source of truth (do not include lab-only: main.rs, fixtures/, sample.rs).

- **PROMOTION_PLAN.md**
- **lib.rs**
- **types.rs**
- **extractor.rs** (copy of lab src/extractor.rs)
- **imports.rs**
- **resolver.rs**
- **symbol_usage.rs**
- **envelope.rs**
- **README.txt** (notes if extractor was copied from lab)

### D. notes/
- **DEPENDENCY_MAP.md** — Lab crate dependency map (tree-sitter, tree-sitter-rust, regex; internal module deps).
- **CC_NOTE.md** — Whether `cc` is required (yes; tree-sitter-rust build script).
- **COMPILE_NOTES.md** — Lab and kernel compile status/warnings.
- **PHASE2B_ADAPTATIONS_AND_PROMOTED_TREE.md** — Promoted tree, manifest diffs, exact adaptations (crate:: → super::), compile outcome.

---

## Constraints (review only)

- No redesign.
- No router/webview/daemon integration.
- No caching.
- No deeper re-export handling.
- Packet is for **surgical promotion review only**.
