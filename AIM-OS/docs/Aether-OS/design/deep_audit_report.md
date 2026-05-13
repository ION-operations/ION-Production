# ION Deep Audit Report — Operation Victus
**Auditor:** Opus (Claude 4.6, COO)  
**Date:** 2026-03-23  
**Scope:** Full `operation-victus/` — 101 source modules, 40+ test files, SeedOS runtime, ion-ui, all on-disk ion data

---

## Executive Summary

The codebase splits into **two distinct layers** built at different times. The newer layer (model, store, parser, index, graph, bootstrap, governed_write, navigator, aether_engine, gemini_api, ingest_v2, context_compiler) is well-architected and uses correct enum values. The older layer (~23 source files) references dead enum values and will crash on import or use. **The architecture is sound. The wiring is broken.**

20 issues documented in separate [issue registry](file:///home/sev/.gemini/antigravity/brain/a3309e2f-655e-4268-90d4-d573df19f97f/ion_issue_registry.md). 4 critical, 7 high, 3 medium, 6 low.

---

## 1. Architecture Map — What Exists

### The Two Code Layers

````carousel
### ✅ New Layer (Clean — Correct Enums)
| Module | Lines | Role |
|--------|-------|------|
| `model.py` | 846 | Core data model: Ion, IonType, AuthorityClass, 8 enums |
| `store.py` | 381 | Filesystem CRUD for ions |
| `parser.py` | 377 | YAML frontmatter ↔ Ion roundtrip |
| `index.py` | 319 | In-memory index with type/authority/bond lookups |
| `graph.py` | 385 | Directed graph: topo-sort, cycles, impact analysis |
| `bootstrap.py` | 469 | Genesis bootstrapper — creates 6 protocols + manifest |
| `governed_write.py` | 422 | 10-stage validation pipeline (W1-W10) |
| `navigator.py` | 625 | §7 cognitive loop implementation |
| `aether_engine.py` | 457 | Full cognitive engine with Gemini API |
| `gemini_api.py` | 300 | Direct Gemini SDK client with retry/tracking |
| `ingest_v2.py` | 753 | 3-layer specialist creation pipeline |
| `context_compiler.py` | ~200 | Ion→LLM prompt compilation with token budgets |
| `bridge.py` | 45 | Singleton `get_ion_store()`/`get_ion_index()` |
| `events.py` | ~120 | Internal event system |
| `invariants.py` | ~150 | Constitutional invariant checker |
| `compliance.py` | ~100 | Governance compliance reports |
<!-- slide -->
### ❌ Old Layer (Drifted — Dead Enums)
| Module | Dead Refs | Impact |
|--------|-----------|--------|
| `capsule.py` | `A4_SYSTEM`, `IonType.EVIDENCE` | Capsules created wrong |
| `governance.py` | `A3_CORE`, `A4_SYSTEM` | Governance checks crash |
| `conflict.py` | `A4_SYSTEM` | Conflict resolution crashes |
| `verification.py` | `A4_SYSTEM` | Verification crashes |
| `registry.py` | `A4_SYSTEM` | Registry crashes |
| `escalation.py` | `A4_SYSTEM` | Escalation crashes |
| `bounties.py` | `A4_SYSTEM` | Bounty system crashes |
| `agent_manifest.py` | `IonType.AGENT`, `A4_SYSTEM` | Can't create agent ions |
| `persona.py` | `IonType.AGENT` | Persona loading fails |
| `voting.py` | `A1_LOCAL` | Voting authority crash |
| `penalty.py` | `A1_LOCAL` | Penalty system crash |
| `viz.py` | `A1_LOCAL`, `A3_CORE`, `A4_SYSTEM` | Mermaid CSS broken |
| `server.py` | `A3_CORE` | API ion creation crashes |
| `tools.py` | `A3_CORE` | Tool ion creation crashes |
| `query_v2.py` | `except 'Exception'` | Silent error swallowing |
````

### Parallel Systems (Not Integrated)

```mermaid
graph TD
    A["ION Cognitive Loop<br/>(navigator.py, aether_engine.py)"] --> B["GovernedWritePipeline<br/>(10-stage validation)"]
    A --> C["IonStore + IonIndex<br/>(filesystem DB)"]
    A --> D["GeminiAPIClient<br/>(direct SDK)"]
    
    E["SeedOS Runtime<br/>(seedos_runtime.py, 744 lines)"] --> F["SeedOS Tools<br/>(5 capability tiers)"]
    E --> G["SeedOS Workspace<br/>(capsules/beliefs/reflections)"]
    E --> H["ReAct Loop<br/>(separate from ION)"]
    
    I["K-Gate Router<br/>(k_gate.py, ~800 lines)"] --> J["Gemini CLI Runner"]
    I --> K["Ollama Runner<br/>(192.168.2.25:11434)"]
    
    L["Server (server.py)"] --> M["MockAdapter ❌"]
    L --> N["Simple AetherEngine ❌<br/>(victus/aether/engine.py, 60 lines)"]
    
    style M fill:#ff6b6b
    style N fill:#ff6b6b
    style A fill:#51cf66
    style E fill:#ffd43b
    style I fill:#74c0fc
```

> [!WARNING]
> The server uses the **mock/simple** versions of everything. The real implementations exist but aren't wired in.

---

## 2. Data Integrity — What's On Disk

### Ion Store (`data/.ion/`)

| Type | Count | Status |
|------|-------|--------|
| **Protocols** | 6 | ✅ Healthy — A0 constitution + 5 A1 kernel protocols |
| **Evidence** | 14 | ✅ Valid chain: E1→E2→E3→E4→E5→E6 + genesis + tests |
| **Memory (Specialists)** | 370 | ✅ Auto-ingested, correct `A4` authority |
| **Manifests** | 2 | ✅ Root manifest + Victus manifest |
| **Branches** | 4 | ✅ `build_aether`, `spec_compiler`, `verify_phase1`, `E2_threshold_test` |
| **SeedOS Sessions** | 35 | ⚠️ Mostly `degraded`/`emergency` states, never cleaned up |

**Serialization roundtrip:** Verified. `Ion.from_dict()` uses `AuthorityClass("A4")` — the enum values are the short codes (`A0`-`A7`), so stored frontmatter parses correctly. No data corruption.

**Key finding:** `model.py` has `create_capsule_ion()` factory (line 750) that correctly uses `IonType.CAPSULE` + `AuthorityClass.A5_INFRA`. But `capsule.py` ignores this factory and manually constructs with wrong types.

---

## 3. Server — Why Nothing Works at Runtime

The FastAPI server ([server.py](file:///home/sev/operation-victus/victus/ion/server.py), 137 lines) has **5 compounding problems**:

| # | Problem | Line | Effect |
|---|---------|------|--------|
| 1 | `GovernedWritePipeline(data_dir)` — passes string, expects `IonStore` | 39 | Any write crashes with `AttributeError` |
| 2 | `index = IonIndex()` — never calls `build_from_store()` | 40 | Reports `ions_indexed: 0` despite 396 ions on disk |
| 3 | `llm = MockAdapter()` — returns canned strings | 43 | `/aether/think` returns fake data |
| 4 | Uses `victus.aether.engine.AetherEngine` (60-line mock) | 44 | Not the real 457-line cognitive engine |
| 5 | `/ion/create` uses `AuthorityClass.A3_CORE` | 61 | Every ion creation crashes |

**`bridge.py` already solves problems #1 and #2** — it has `get_ion_store()`, `get_ion_index()` (with `build_from_store()`), and `get_pipeline()`. The server just doesn't use them.

---

## 4. The Two AetherEngines

| | Simple (Mock) | Full (Real) |
|---|---|---|
| **File** | `victus/aether/engine.py` | `victus/ion/aether_engine.py` |
| **Lines** | ~60 | 457 |
| **LLM** | `LLMAdapter` ABC → `MockAdapter` | `GeminiAPIClient` + K-Gate fallback |
| **Cognitive Loop** | Basic event publishing | Full §7: Contextualize→Reflect→Plan→Gate→Execute→Audit→Deliver |
| **Governance** | None | `GovernedWritePipeline` for all mutations |
| **Context** | Simple string concat | `HybridQueryEngine` with AST + bond traversal |
| **Used By** | Server ❌ | Nothing (orphaned) ❌ |

---

## 5. The Two Capsule Systems

| | ION Capsule | SeedOS Capsule |
|---|---|---|
| **File** | `victus/ion/capsule.py` | `victus/seedos_runtime.py` |
| **Writes To** | `data/.ion/capsules/` via governed write | `data/seedos_sessions/*/capsules/` |
| **IonType** | Should be `CAPSULE`, uses `EVIDENCE` ❌ | N/A (plain JSON/text) |
| **Shared Code** | None | None |
| **Active Data** | 0 capsule ions on disk | 35 sessions with capsule dirs |

---

## 6. LLM Integration Layers

Three separate LLM integration paths exist:

| Path | Module | Provider | Used By |
|------|--------|----------|---------|
| **Direct API** | `victus/ion/gemini_api.py` | Gemini SDK (`google-generativeai`) | `aether_engine.py`, `navigator.py` |
| **K-Gate Router** | `victus/k_gate.py` | Gemini CLI + Ollama (score-based routing) | SeedOS runtime |
| **LLM Adapter** | `victus/ion/llm_adapter.py` | ABC with `MockAdapter` only | Server (mock) |

**API Key:** `AIzaSyBvsjLqbPmPLtOyQCSAAdnVqrB9ozRSf-w` found in bash history. Never persisted to `.env`. `gemini_api.py` only checks `GOOGLE_API_KEY`, not `GEMINI_API_KEY`.

---

## 7. Module Quality Summary

### Clean Modules (No Issues Found)
`model.py`, `store.py`, `parser.py`, `index.py`, `graph.py`, `bootstrap.py`, `governed_write.py`, `navigator.py`, `aether_engine.py`, `gemini_api.py`, `ingest_v2.py`, `context_compiler.py`, `bridge.py`, `events.py`, `invariants.py`, `compliance.py`, `compactor.py`, `pubsub.py`, `locking.py`, `llm_adapter.py` (interface only), `seedos_runtime.py`, `seedos_tools.py`, `k_gate.py`, `gemini_cli_runner.py`, `ollama_runner.py`

### Drifted Modules (Enum Issues)
`capsule.py`, `governance.py`, `conflict.py`, `verification.py`, `registry.py`, `escalation.py`, `bounties.py`, `agent_manifest.py`, `persona.py`, `voting.py`, `penalty.py`, `viz.py`, `server.py`, `tools.py`

### Bug (Non-Enum)
`query_v2.py` — `except 'Exception'` at line 211

---

## 8. What's Working vs What's Broken

| System | Status | Evidence |
|--------|--------|----------|
| Ion Data Model | ✅ Working | 846 lines, clean enums, roundtrips correctly |
| Filesystem Store | ✅ Working | 396 ions on disk, CRUD verified |
| YAML Parser | ✅ Working | PyYAML + fallback, handles all ion types |
| Ion Index | ✅ Working | But server never calls `build_from_store()` |
| Graph Algorithms | ✅ Working | Topo-sort, cycle detection, impact analysis |
| Governed Write Pipeline | ✅ Working | 10-stage validation, authority matrix |
| Bootstrap/Genesis | ✅ Working | Created all 6 protocols + evidence + manifest |
| Specialist Ingestion | ✅ Working | 370 specialists created via 3-layer pipeline |
| Cognitive Navigator | ✅ Working | §7 loop implementation |
| Full AetherEngine | ✅ Working | But orphaned — not wired to server |
| Bridge Singletons | ✅ Working | But server doesn't use them |
| FastAPI Server | ❌ Broken | 5 compounding issues, returns mock data |
| Capsule System | ❌ Broken | Wrong IonType, wrong AuthorityClass |
| Governance Modules | ❌ Broken | All reference dead enums |
| Agent System | ❌ Broken | `IonType.AGENT` removed from model |
| ion-ui Frontend | ⚠️ Partial | Connects to WS, shows comms only |
| SeedOS Runtime | ⚠️ Separate | Complete but parallel to ION, not integrated |

---

## 9. Root Cause Analysis

**One event caused ~80% of the issues:** The `model.py` enum refactoring that renamed:
- `A4_SYSTEM` → `A4_RUNTIME`
- `A3_CORE` → `A3_HISTORY` 
- `A1_LOCAL` → `A1_KERNEL`
- Removed `IonType.AGENT`

The newer modules were written after this refactoring. The older modules were written before and never updated. No migration script, no grep-and-replace, no test suite caught it because the tests themselves use the old enums.

---

## 10. Recommended Fix Order

| Priority | Fix | Impact | Effort |
|----------|-----|--------|--------|
| 1 | Re-add `IonType.AGENT` to `model.py` | Unblocks agent system | 1 line |
| 2 | Find-replace dead enums in 23 source files | Unblocks all drifted modules | Mechanical |
| 3 | Fix `except 'Exception'` in `query_v2.py` | Prevents silent failures | 1 line |
| 4 | Wire server to use `bridge.py` singletons | Server sees 396 ions | ~10 lines |
| 5 | Wire server to use real `AetherEngine` | Live LLM responses | ~15 lines |
| 6 | Fix `capsule.py` to use `IonType.CAPSULE` | Correct capsule creation | ~5 lines |
| 7 | Create `.env` for API key persistence | Survives process restart | 2 lines |
| 8 | Fix dead enum references in 22 test files | Tests can run | Mechanical |
| 9 | Address SeedOS/ION integration strategy | Architectural decision | Design work |
| 10 | Address hardcoded paths | Portability | ~10 lines |

> [!IMPORTANT]
> Fixes 1-3 would take under 5 minutes and unblock the entire old layer. Fix 4-5 would make the server functional in ~30 minutes.
