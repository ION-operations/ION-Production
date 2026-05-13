# Mission Capsule: Wire and Mapper v1

## 1. What AIM-OS is

AIM-OS is a memory-native consciousness substrate and tool ecosystem: MCP tools (memory, timeline, goals, RAG, etc.), a Python MCP daemon over stdio, and a planned Tauri/Rust kernel for local actuation and context shaping. This capsule covers only the current mission: proving the Rust–Python wire and the first phase of the deterministic Context Mapper.

## 2. What this capsule includes

- **Mission docs** (docs/): Sovereign build plan, mission start, daemon/stdio/MCP findings, reply to DeepThink.
- **Daemon surface** (daemon/): `lucid_mcp_server.py` and a short README on launch and MCP stdio.
- **Wire proof** (wire_proof/): Standalone Rust crate that spawns the daemon, runs initialize, notifications/initialized, tools/list, and one tools/call (get_memory_stats).
- **Context mapper lab** (context_mapper_lab/): Standalone Rust crate — single-file extractor (Tree-sitter), extracts use lines and pub struct/enum/trait/fn/type/const with full contract text for enum/trait.
- **Logs** (logs/): One successful wire proof run summary, one successful context mapper lab run summary.
- **Orientation** (this README, REPO_MAP.txt, IMPORTANT_FILES.txt).

## 3. Current mission

- **Strike 2** — Rust ↔ Python MCP stdio wire proof (done).
- **Strike 1** — Context Mapper lab, single-file extractor phase (in progress).

No Tauri, router, or full resolver in this capsule.

## 4. What is already proven

- Rust spawns the Python AIM-OS daemon; JSON-RPC over stdio works.
- `initialize`, `notifications/initialized`, `tools/list`, and `tools/call(get_memory_stats)` succeed; the bridge sees the real tool surface (103 tools) and get_memory_stats returns real AIM-OS stats.
- Context mapper lab reads one Rust file and prints imports, contracts (with enum variants and trait method signatures), and parse confidence (High/Degraded/Fallback).

## 5. Next step

Improve contract fidelity as needed; continue Strike 1 (e.g. resolver groundwork: local use paths, basic mod mapping). Then Strike 3 (router, Tauri integration) per the build plan.

## 6. How to run

### wire_proof

- From the **capsule** `wire_proof/` directory: run `cargo run`.
- The binary expects to run the daemon from an AIM-OS workspace: it uses a hardcoded `workspace_root` (see `wire_proof/src/main.rs`). Point that at your AIM-OS repo root (or the repo that contains `lucid_mcp_server.py` and packages/) or change the code. Python must be on PATH; `PYTHONPATH` is set by the bridge to `workspace_root`.

### context_mapper_lab

- From the **capsule** `context_mapper_lab/` directory: run `cargo run -- sample.rs` (or any path to a Rust file). No daemon or AIM-OS repo required; Tree-sitter parses the file locally.

## 7. Important paths in the original repo

- **Mission docs:** AIM-OS repo `docs/` — SOVEREIGN_CONTEXT_MAPPER_AIMOS_PRIME_BUILD_PLAN.md, MISSION_START_SOVEREIGN_CONTEXT_MAPPER_2026-02-28.md, DAEMON_STDIO_MCP_AND_CONTEXT_BUS_FINDINGS.md, REPLY_TO_DEEPTHINK_AIMOS_GRAND_CONVERGENCE.md.
- **Daemon entrypoint:** AIM-OS repo root `lucid_mcp_server.py`.
- **Wire proof crate (original):** `Application_Dev/IDE/wire_proof/` (e.g. under user Documents, not under AIM-OS).
- **Context mapper lab crate (original):** `Application_Dev/IDE/context_mapper_lab/` (same).

This capsule is a snapshot for review; the live crates may be developed in the original locations.
