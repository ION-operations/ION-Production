# ION Runtime Audit — victus/ion/ (105 files, 16,121 lines)

> Every .py file classified: ✅ KEEP, ⚠️ REBUILD, ❌ CUT, 🔲 STUB (concept valid, needs real impl)

---

## Tier 1: VERIFIED CORE (Keep — These ARE ION)

| File | Lines | What It Does | Status |
|------|------:|--------------|--------|
| `model.py` | 940 | Ion, IonType, AuthorityClass, GateClass, BondType, AgentRole, bonds | ✅ Verified, WEAVER enhanced |
| `governed_write.py` | 443 | 10-stage write validation pipeline. THE governance enforcement | ✅ Verified 5/5 |
| `navigator.py` | 624 | 7-step cognitive loop (contextualize→deliver). Produces health=0.80 | ✅ Verified |
| `context_compiler.py` | 445 | Three-tier context (pinned/working/long-term). Budget-aware | ✅ Verified, NEXUS enhanced |
| `llm_adapter.py` | 433 | Gemini+Ollama+Mock adapters. ABC interface. 17/17 tests | ✅ NEXUS rewrote |
| `store.py` | 380 | Filesystem CRUD for ions as YAML+markdown files | ✅ Verified |
| `graph.py` | 384 | Bond graph traversal, topology, impact analysis, connected components | ✅ Verified 5/5 |
| `index.py` | 318 | In-memory index: by_type, by_authority, by_tag, bonds_from/to | ✅ Verified |
| `parser.py` | 376 | YAML frontmatter + markdown body parsing | ✅ Verified |
| `manifest.py` | 429 | Root node management, branch tracking, positions | ✅ Verified |
| `threshold.py` | 319 | Staleness, confidence decay, activation conditions | ✅ Verified |
| `invariants.py` | 132 | Constitutional invariant checking | ✅ Verified |
| `cli.py` | 320 | Command-line: ls, stats, inspect, bonds, graph, create, validate | ✅ Verified |

**Total: 13 files, 5,543 lines — the irreducible kernel**

---

## Tier 2: ESSENTIAL SUPPORTING (Keep — Needed for full OS)

| File | Lines | What It Does | Decision |
|------|------:|--------------|----------|
| `ingest_v2.py` | 752 | Tree-sitter code parsing into ions with bonds | ✅ KEEP — critical for IDE |
| `bootstrap.py` | 468 | System startup, creates initial network | ⚠️ KEEP but NEEDS FIX (hangs) |
| `model_registry.py` | 460 | Multi-provider LLM routing, task→model mapping | ✅ KEEP |
| `server.py` | 131 | FastAPI REST + WebSocket (wired to AetherEngine) | ✅ KEEP |
| `gemini_api.py` | 299 | Google Gemini API client | ✅ KEEP (used by LLM adapter) |
| `capsule.py` | 244 | PRE/POST context snapshots for truncation survival | ✅ KEEP |
| `tree_sitter_adapter.py` | 238 | Bridge to tree-sitter for 10+ languages | ✅ KEEP |
| `ingest.py` | 531 | v1 ingestion (simpler than v2) | ⚠️ KEEP for now, may merge into v2 |
| `supervisor.py` | 107 | Agent clustering + supervisor emergence (WEAVER) | ✅ KEEP |
| `hierarchy.py` | 83 | get_supervisor, get_specialists, get_hierarchy | ✅ KEEP |
| `agent_manifest.py` | 82 | Agent identity as ions | ✅ KEEP |
| `test_llm_adapter.py` | 293 | 17 tests for LLM adapters (NEXUS) | ✅ KEEP |

**Total: 12 files, 3,688 lines**

---

## Tier 3: SUBSTANTIAL SUPPORTING (Keep — Useful systems with real logic)

| File | Lines | What It Does | Decision |
|------|------:|--------------|----------|
| `meta.py` | 218 | Self-reflection, meta-cognition engine | ✅ KEEP |
| `topology_optimizer.py` | 182 | Graph self-optimization | ✅ KEEP |
| `healer.py` | 171 | Self-healing and auto-repair | ✅ KEEP |
| `consolidator.py` | 171 | Knowledge consolidation and merging | ✅ KEEP |
| `automation.py` | 150 | Reactive automation (file watchers, triggers) | ✅ KEEP |
| `corrections.py` | 146 | Error correction tracking | ✅ KEEP |
| `threshold_learner.py` | 242 | Threshold learning from outcomes | ✅ KEEP |
| `compliance.py` | 133 | Epoch-based compliance tracking | ✅ KEEP |
| `truncation_proof.py` | 121 | Context truncation survival | ✅ KEEP |
| `watcher.py` | 121 | Filesystem change monitoring | ✅ KEEP |
| `query.py` | 350 | Ion query engine v1 | ⚠️ REVIEW — may merge with query_v2 |
| `query_v2.py` | 222 | Ion query engine v2 | ✅ KEEP — supersedes v1 |

**Total: 12 files, 2,227 lines**

---

## Tier 4: THIN STUBS — Valid Concepts, Minimal Code (🔲 Keep shells, rebuild as needed)

These are 20-100 line files with correct interfaces but minimal implementation. They represent valid OS concepts that should exist in the final build but need real implementation when their phase arrives.

| File | Lines | Concept | Decision |
|------|------:|---------|----------|
| `api.py` | 337 | REST API routes for all subsystems | 🔲 Keep shell |
| `pubsub.py` | 33 | Event bus publish/subscribe | 🔲 Keep shell |
| `events.py` | 96 | Event type definitions | 🔲 Keep shell |
| `triggers.py` | 44 | Trigger definitions for automation | 🔲 Keep shell |
| `scheduler.py` | 62 | Cognitive task scheduler | 🔲 Keep shell |
| `escalation.py` | 76 | Ripple severity calculation | 🔲 Keep shell |
| `conflict.py` | 60 | Concurrent write conflict resolution | 🔲 Keep shell |
| `locking.py` | 80 | File locking for multi-agent | 🔲 Keep shell |
| `voting.py` | 69 | Multi-agent consensus voting | 🔲 Keep shell |
| `penalty.py` | 59 | Authority demotion (WEAVER fixed) | ✅ Keep |
| `negotiation.py` | 51 | Agent task negotiation | 🔲 Keep shell |
| `bounties.py` | 76 | Task bounty marketplace | 🔲 Keep shell |
| `agent_comms.py` | 57 | Inter-agent messaging | 🔲 Keep shell |
| `orchestrator.py` | 86 | Multi-agent orchestration | 🔲 Keep shell |
| `planner.py` | 94 | Cognitive planning engine | 🔲 Keep shell |
| `runner.py` | 93 | Task execution runner | 🔲 Keep shell |
| `router.py` | 88 | Intent routing | 🔲 Keep shell |
| `semantic_router.py` | 104 | Semantic intent classification + routing | 🔲 Keep shell |
| `state_machine.py` | 56 | Governance state (NORMAL/ELEVATED/CRITICAL) | 🔲 Keep shell |
| `propagation.py` | 92 | Bond change propagation | 🔲 Keep shell |
| `impact.py` | 90 | Change impact analysis | 🔲 Keep shell |
| `scaffold.py` | 86 | Ion network scaffolding | 🔲 Keep shell |
| `auto_loop.py` | 47 | Background execution loop | 🔲 Keep shell |
| `cron.py` | 51 | Scheduled execution | 🔲 Keep shell |
| `watchdog_daemon.py` | 96 | Watchdog health monitoring | 🔲 Keep shell |

**Total: 25 files, ~1,900 lines of mostly-shell code**

---

## Tier 5: CUT — Redundant, experimental, or not useful

| File | Lines | Reason to Cut |
|------|------:|---------------|
| `auth.py` | 33 | Trivial wrapper, superseded by `authority.py` |
| `authority.py` | 107 | Overlaps with authority in `model.py` — consolidate |
| `governance.py` | 55 | Overlaps with `governed_write.py` — consolidate |
| `governance_api.py` | 113 | REST thin wrapper of governance — merge into `api.py` |
| `audit.py` | 120 | Overlaps with `invariants.py` + `meta.py` |
| `audit_hardened.py` | 43 | Thin extension of audit.py — merge |
| `debugger.py` | 31 | Stub — 2 methods, does nothing useful |
| `encryption.py` | 23 | Stub — placeholder AES, not real crypto |
| `compactor.py` | 59 | Overlaps with `consolidator.py` |
| `fine_tuning.py` | 41 | ChatML export — too simplistic, not real fine-tuning |
| `feedback.py` | 37 | Minimal outcome tracking — merge into `corrections.py` |
| `synthetic_data.py` | 20 | Trivial training data gen — not useful yet |
| `tracer.py` | 27 | Minimal tracing — use standard Python logging |
| `profiler.py` | 30 | Minimal profiling — use cProfile |
| `visualizer.py` | 21 | Mermaid export — already in `graph.py.to_mermaid()` |
| `viz.py` | 92 | Dashboard viz — superseded by our system-map |
| `sandbox.py` | 27 | Stub — no real isolation implemented |
| `rate_limiter.py` | 38 | Token bucket — too simple, rebuild when needed |
| `inference_cache.py` | 40 | LRU cache — trivial, inline into adapter |
| `git_integration.py` | 26 | Stub — 1 method, placeholder |
| `matcher.py` | 35 | Stub — fuzzy matching, use difflib directly |
| `mcp_bridge.py` | 34 | Stub — Phase Q.01 placeholder |
| `optimization.py` | 22 | Trivial optimizer — merge into `consolidator.py` |
| `classifier.py` | 75 | Query classification — merge into `semantic_router.py` |
| `compiler.py` | 70 | NL spec compiler — merge into `context_compiler.py` |
| `dispatcher.py` | 41 | Intent dispatch — merge into `router.py` |
| `epoch.py` | 57 | Epoch finalization — merge into `compliance.py` |
| `context.py` | 99 | Context base classes — merge into `context_compiler.py` |
| `registry.py` | 53 | Generic registry — merge into `model_registry.py` |
| `spec_parser.py` | 114 | NL spec parsing — not ready, park for Phase 3 |
| `spec_deps.py` | 85 | Spec dependency resolution — not ready, park |
| `migrate_sqlite.py` | 138 | SQLite migration — we use filesystem, not SQLite |
| `persona.py` | 37 | Agent persona — merge into `agent_manifest.py` |
| `tools.py` | 45 | Tool registry — merge into `llm_adapter.py` |
| `test_scaffold.py` | 67 | Not pytest-compatible, gives 0 collected | 
| `bridge.py` | 45 | Singleton bridge — CAUSES bootstrap hang |

**Total: 36 files to cut/merge, ~1,917 lines of dead weight**

---

## Summary

| Tier | Files | Lines | Decision |
|------|------:|------:|----------|
| 1: Verified Core | 13 | 5,543 | ✅ KEEP as-is |
| 2: Essential Supporting | 12 | 3,688 | ✅ KEEP (bootstrap needs fix) |
| 3: Substantial Supporting | 12 | 2,227 | ✅ KEEP |
| 4: Thin Stubs | 25 | ~1,900 | 🔲 KEEP shells, rebuild per phase |
| 5: Cut | 36 | ~1,917 | ❌ DELETE or merge |
| Infrastructure | 1 | 1 | `__init__.py` |
| **Total** | **99** | **~15,276** | **63 keep, 36 cut** |

> After cutting: **63 files, ~13,359 lines** of meaningful code → this is ION's runtime.
