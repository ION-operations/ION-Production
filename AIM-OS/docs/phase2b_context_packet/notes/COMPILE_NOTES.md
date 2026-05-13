# Current compile notes (lab and kernel)

## Lab (context_mapper_lab)

- `cargo build` / `cargo run` succeed.
- One known warning: `print_contracts` in main.rs is dead code (only used in single-file path; gauntlet uses different printing). Harness-only; not part of promotion.

## Kernel (src-tauri) after Phase 2B

- `cargo build` succeeds (exit code 0).
- Warnings (10) are all in pre-existing SAIOS code (webview_manager, injection, actuator, lib.rs unused imports; process.rs unused BOOL; etc.). None in `context_mapper/`.
- No errors in promoted context_mapper module.
