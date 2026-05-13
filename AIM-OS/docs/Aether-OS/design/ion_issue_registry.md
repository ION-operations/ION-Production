# ION Operation Victus — Issue Registry (Rev 2)
**Auditor:** Opus (Claude 4.6)  
**Date:** 2026-03-23  
**Scope:** Full `operation-victus/` codebase (101 source modules, 40+ test files, SeedOS runtime, ion-ui)

---

## CRITICAL — Will Crash On Use

### ISS-001: Enum Drift — `A4_SYSTEM` → `A4_RUNTIME`
`model.py` defines `A4_RUNTIME`. **12 source modules** still use `A4_SYSTEM`:

| Module | Lines |
|--------|-------|
| [capsule.py](file:///home/sev/operation-victus/victus/ion/capsule.py#L24) | 24 |
| [conflict.py](file:///home/sev/operation-victus/victus/ion/conflict.py#L50) | 50 |
| [verification.py](file:///home/sev/operation-victus/victus/ion/verification.py#L46) | 46 |
| [registry.py](file:///home/sev/operation-victus/victus/ion/registry.py#L27) | 27 |
| [escalation.py](file:///home/sev/operation-victus/victus/ion/escalation.py#L58) | 58 |
| [bounties.py](file:///home/sev/operation-victus/victus/ion/bounties.py) | 25, 67 |
| [agent_manifest.py](file:///home/sev/operation-victus/victus/ion/agent_manifest.py) | 50, 73 |
| [governance.py](file:///home/sev/operation-victus/victus/ion/governance.py) | 30, 31, 43 |
| [viz.py](file:///home/sev/operation-victus/victus/ion/viz.py#L67) | 67 |

Plus **15 test files**. **Fix:** Find-replace `A4_SYSTEM` → `A4_RUNTIME`.

---

### ISS-002: Enum Drift — `A3_CORE` → `A3_HISTORY`
5 source modules reference `A3_CORE`:

| Module | Lines |
|--------|-------|
| [server.py](file:///home/sev/operation-victus/victus/ion/server.py#L61) | 61 |
| [tools.py](file:///home/sev/operation-victus/victus/ion/tools.py#L28) | 28 |
| [governance.py](file:///home/sev/operation-victus/victus/ion/governance.py#L30) | 30, 43 |

> [!WARNING]
> `server.py:61` — the `/ion/create` API endpoint uses `A3_CORE`. Every ion creation via API will crash.

Plus **8 test files**. **Fix:** Replace `A3_CORE` → `A3_HISTORY`.

> **NOTE on semantics:** `A3_CORE` meant "core system" but `A3_HISTORY` means "historical/log." Some usages (like `server.py` defaulting new ions to `A3_CORE`) may need `A4_RUNTIME` instead. Resolve per-usage.

---

### ISS-003: Enum Drift — `A1_LOCAL` → `A1_KERNEL`
3 source modules reference `A1_LOCAL`:

| Module | Lines |
|--------|-------|
| [voting.py](file:///home/sev/operation-victus/victus/ion/voting.py#L24) | 24 |
| [penalty.py](file:///home/sev/operation-victus/victus/ion/penalty.py#L40) | 40 |
| [viz.py](file:///home/sev/operation-victus/victus/ion/viz.py#L64) | 64 |

Plus **11 test files**. **Fix:** Replace `A1_LOCAL` → `A1_KERNEL`.

---

### ISS-004: `IonType.AGENT` Missing From Model
`IonType.AGENT` was removed during the model.py rewrite. This is a **bug** — the system is a multi-agent OS. 3 source modules + 7 test files reference it.

| Module | Lines |
|--------|-------|
| [persona.py](file:///home/sev/operation-victus/victus/ion/persona.py#L26) | 26 |
| [agent_manifest.py](file:///home/sev/operation-victus/victus/ion/agent_manifest.py) | 24, 49, 72 |

**Fix:** Re-add `AGENT = "agent"` to the `IonType` enum in `model.py`.

---

## HIGH — Functional Bugs & Architectural Issues

### ISS-005: `except 'Exception'` in query_v2.py
[query_v2.py line 211](file:///home/sev/operation-victus/victus/ion/query_v2.py#L211): String literal instead of Exception class. **Never catches anything.** Any LLM error = unhandled crash.

**Fix:** `except 'Exception'` → `except Exception`

---

### ISS-006: Capsule Uses Wrong IonType
[capsule.py:23](file:///home/sev/operation-victus/victus/ion/capsule.py#L23) creates capsules as `IonType.EVIDENCE`. Model has `IonType.CAPSULE` with `CapsulePhase` enum.

**Fix:** `IonType.EVIDENCE` → `IonType.CAPSULE`, add `capsule_phase` field.

---

### ISS-007: Server Index Never Loaded — `ions_indexed: 0`
[server.py:40](file:///home/sev/operation-victus/victus/ion/server.py#L40): `index = IonIndex()` creates an empty index. Never calls `build_from_store()`. Despite 16+ ions on disk (`data/.ion/`), the server reports 0 ions indexed.

**Fix:** After creating the pipeline, iterate `pipeline.store.scan()` and add ions to the index.

---

### ISS-008: Server Uses MockAdapter Instead of Real LLM
[server.py:43](file:///home/sev/operation-victus/victus/ion/server.py#L43): `llm = MockAdapter()` — the `/aether/think` endpoint returns canned mock responses, not real LLM output.

**Fix:** Use `GeminiAPIClient` from `victus.ion.gemini_api` with the API key.

---

### ISS-009: Two Separate AetherEngine Implementations
There are TWO different AetherEngine classes:

| Engine | File | Lines | LLM | Governance |
|--------|------|-------|-----|------------|
| **Simple** | [victus/aether/engine.py](file:///home/sev/operation-victus/victus/aether/engine.py) | ~60 | `LLMAdapter` ABC (mock) | Basic event publishing |
| **Full** | [victus/ion/aether_engine.py](file:///home/sev/operation-victus/victus/ion/aether_engine.py) | 457 | Gemini API, K-Gate | Full cognitive loop, governed write, diff patching |

The **server uses the simple/mock one**. The full one is what ION was designed around.

**Fix:** Server should use `victus.ion.aether_engine.create_aether_engine()`.

---

### ISS-010: Server Passes String Where IonStore Expected
[server.py:39](file:///home/sev/operation-victus/victus/ion/server.py#L39): `GovernedWritePipeline(data_dir)` passes a string path. The constructor at [governed_write.py:144](file:///home/sev/operation-victus/victus/ion/governed_write.py#L144) expects `store: IonStore`. Python accepts it silently but any method call on `self.store` will crash with `AttributeError`.

**Fix:** `pipeline = GovernedWritePipeline(IonStore(data_dir))`

---

### ISS-011: Two Separate Capsule Systems
| System | File | Writes To |
|--------|------|-----------|
| **ION capsule** | [victus/ion/capsule.py](file:///home/sev/operation-victus/victus/ion/capsule.py) | `data/.ion/capsules/` via governed write |
| **SeedOS capsule** | [victus/seedos_runtime.py](file:///home/sev/operation-victus/victus/seedos_runtime.py) | `data/seedos_sessions/*/capsules/` |

These don't share code or data. SeedOS sessions have their own workspace with capsules/beliefs/reflections.

---

## MEDIUM — Configuration & Operational

### ISS-012: No Persistent API Key
The API key `AIzaSyBvsjLqbPmPLtOyQCSAAdnVqrB9ozRSf-w` (found in bash history) was set via `os.environ` in-process by a previous AI session. Lost when that process ended. No `.env` file in `operation-victus/`.

**Fix:** Create `operation-victus/.env` with `GOOGLE_API_KEY=AIzaSyBvsjLqbPmPLtOyQCSAAdnVqrB9ozRSf-w`, load with `python-dotenv` or source in shell.

---

### ISS-013: `gemini_api.py` Only Checks `GOOGLE_API_KEY`
[gemini_api.py:68](file:///home/sev/operation-victus/victus/ion/gemini_api.py#L68): Only checks `GOOGLE_API_KEY`. Other systems store as `GEMINI_API_KEY`.

**Fix:** Check both: `os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")`

---

### ISS-014: Import Cascade — Modules That Import Dead Enums Don't Load
Any module importing `A4_SYSTEM`, `A3_CORE`, `A1_LOCAL`, or `IonType.AGENT` will crash on import. This means ~23 source files and ~22 test files cannot be imported. The server survives because its import chain only hits these when the code path is executed (runtime error, not import error), but test collection fails.

---

## LOW — Technical Debt

### ISS-015: SeedOS Runtime Is a Parallel Agent System
[seedos_runtime.py](file:///home/sev/operation-victus/victus/seedos_runtime.py) (744 lines) is a complete, separate agent framework with its own ReAct loop, 5 capability tiers, tool registry, capsule management, and progressive benchmarking. It runs alongside ION but doesn't use the ION cognitive loop, governed write, or specialist system. 35 sessions generated on disk.

---

### ISS-016: `evolution_node.py` Creates Separate Store/Pipeline
[evolution_node.py](file:///home/sev/operation-victus/victus/aether/evolution_node.py): Creates its own `IonStore` and `GovernedWritePipeline` instances separate from the server's, pointing to the same data directory. Concurrent writes could conflict.

---

### ISS-017: `viz.py` Hardcodes Dead Enum CSS Classes
Lines 64-67 hardcode CSS for `A1_LOCAL`, `A3_CORE`, `A4_SYSTEM`. Mermaid diagrams will reference non-existent styles.

---

### ISS-018: SeedOS Sessions Never Cleaned Up
35 session directories in `data/seedos_sessions/`, mostly `degraded` and `emergency` states. No archival/cleanup process.

---

### ISS-019: ion-ui Only Shows Comms
The React frontend ([ion-ui/src/App.tsx](file:///home/sev/operation-victus/ion-ui/src/App.tsx)) connects to `ws://localhost:8000/ws/comms` but only displays agent communication messages. Nexus and Crucible tabs appear to show placeholder content.

---

### ISS-020: Hardcoded Paths
- `seedos_runtime.py:51`: `SESSIONS_DIR = Path("/home/sev/operation-victus/data/seedos_sessions")`
- `evolution_node.py:24`: `IonStore("/home/sev/operation-victus/data")`
- `server.py:36`: `data_dir` defaults to `/home/sev/operation-victus/data`

These should use relative paths or environment variables.

---

## Summary

| Severity | Count | Root Cause |
|----------|-------|------------|
| **CRITICAL** | 4 | Enum rename without updating dependents |
| **HIGH** | 7 | Bugs + architectural divergence (mock engine, two engines, two capsule systems) |
| **MEDIUM** | 3 | Configuration gaps |
| **LOW** | 6 | Technical debt, parallel systems, hardcoded paths |
| **TOTAL** | **20** | |

### Answered Questions (Self-Resolved)

| Question | Answer |
|----------|--------|
| Was `IonType.AGENT` intentionally removed? | **No.** Bug from model.py rewrite. Re-add it. |
| Where's the API key? | `AIzaSyBvsjLqbPmPLtOyQCSAAdnVqrB9ozRSf-w` in bash history. Set in-memory by Gemini 3.1, not persisted. |
| Why `ions_indexed: 0`? | Server creates empty `IonIndex()` and never loads from store. |
| Why does `/aether/think` return mock data? | Server uses `MockAdapter`, not real Gemini. |
| Which AetherEngine is the real one? | `victus/ion/aether_engine.py` (457 lines, full cognitive loop with Gemini API). |
| Is the capsule system one system or two? | Two: ION capsules (ion store) and SeedOS capsules (workspace directories). |
