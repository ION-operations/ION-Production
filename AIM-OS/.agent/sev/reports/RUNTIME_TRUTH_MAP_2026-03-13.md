# AIM-OS Runtime Truth Map — 2026-03-13

**Author:** OPUS  
**Goal:** CONSOLIDATION-01.B  
**Method:** Live MCP probes + package directory scan + system tool calls  
**Status:** Draft v1 — verified by automated testing, not manual QA

---

## 1. Core System Status (Verified via MCP Probes)

| System | MCP Status | Live Test Result | Verdict |
|--------|-----------|-----------------|---------|
| **CMC (Memory)** | ✅ operational | 427 atoms, sqlite, integrity OK, 0 write errors | **ALIVE** |
| **HHNI (Retrieval)** | ❌ not initialized | 0 index nodes, 0 retriever, falls back to text search | **BROKEN** — disabled since Mar 6 to prevent torch crash on Windows |
| **VIF (Confidence)** | ⚠️ partial | κ-gate logic works, 0 predictions ever tracked, ECE at 0.0 | **FUNCTIONAL but UNUSED** |
| **APOE (Planning)** | ⚠️ untested | `create_plan` tool exists, no live execution test done yet | **EXISTS, needs verification** |
| **SEG (Evidence)** | ⚠️ untested | `synthesize_knowledge` tool exists | **EXISTS, needs verification** |
| **CAS (Introspection)** | ❌ critical | 5 core principles cold, overall score 0.78, not healthy | **DEGRADED** |
| **SIS (Improvement)** | ⚠️ untested | Package exists with init | **EXISTS, needs verification** |
| **SDF-CVF (Evolution)** | ⚠️ untested | Package exists with init | **EXISTS, needs verification** |

## 2. MCP Transport

| Transport | Status | Details |
|-----------|--------|---------|
| **stdio (native)** | ✅ WORKING | Primary transport. 103+ tools registered. Active in this session |
| **HTTP fallback (5001)** | ⚠️ SLOW/INTERMITTENT | Sometimes responsive, sometimes times out |
| **SSE (8000)** | ❓ UNKNOWN | Not tested in this session |
| **Cursor extension** | ❌ DISCONNECTED | Command server returning 404 |

## 3. Package Inventory (68 directories under packages/)

### Importable (44 packages — have `__init__.py`)
```
CORE SYSTEMS:     cmc_service, hhni, vif, apoe, seg, cas, sis, sdfcvf
MCP:              lucid_mcp_server, mcp_server, mcp_data_integration
ORCHESTRATION:    apoe_runner, prompt_chain_executor, orchestration_builder
AI:               ai_collaboration, llm_client, intent_classification, specialist_system
AGENTS:           agent, autonomous_research_dream
SEARCH:           deepsearch, icip_search
CONSCIOUSNESS:    consciousness_analyzer, consciousness_creativity_engine,
                  consciousness_error_learning, consciousness_learning_engine,
                  consciousness_optimization_detector, temporal_consciousness
INFRASTRUCTURE:   router, router_api_server, schemas, api_service_registry,
                  doc_builder, log_sentinels, unified, shared(?), scor,
                  nl_tags, holographic_memory, meta_optimizer
CAPABILITY:       capability_awareness, intuitive_intelligence_system
MATH:             quaternion_math
INTEGRATION:      integration_tests
```

### Not Importable (24 packages — missing `__init__.py`)
```
FRONTEND/UI:      advanced_monaco_editor, antigravity-extension, ide_chat_app,
                  joc, joc-tournament, lucid_core_console, lucid_document_editor,
                  lucid_orchestrator, plix
INFRA (no init):  browser-automation-service, context_bootloader, mcp_debugging_system,
                  mcp_rag_proxy, prompt_chains, safety_systems, shared,
                  timeline_context_system, knowledge_architecture
DEAD/UNKNOWN:     aimos-sdk, aimos_mobile_app, autonomous_protocol, igodn,
                  jarvis_injector, lumin_snap_system, meta_reasoning,
                  quaternion_kernel
BUILD ARTIFACT:   cmc_service.egg-info, __pycache__
```

## 4. Key Findings

### What's Actually Working
1. **CMC memory** — the single most critical system, it works
2. **MCP stdio transport** — the backbone, it works
3. **AI collaboration bus** — inter-agent messaging works
4. **44 importable Python packages** — half the ecosystem has structure
5. **Goal timeline** — just started working today (was never used before)

### What's Critically Broken
1. **HHNI** — semantic retrieval is dead, has been since Mar 6. Root cause: torch/transformers crashes on Windows. Fix: either `AIMOS_HHNI_EAGER_INIT=1` env var, or restructure to avoid heavy ML deps
2. **CAS** — 5 core principles completely cold, making introspection unreliable
3. **Goal system** — existed but was never used until today (0 goals tracked before this session)
4. **VIF** — functional code with zero actual usage data. Never been used in real decision-making

### What's Unknown
1. **APOE, SEG, SIS, SDF-CVF** — these claim to be "built" in the genome but haven't been live-tested
2. **24 non-importable packages** — some are frontend (expected), some might be dead code
3. **Consciousness packages (6)** — all importable but unclear if they're wired into anything

### Sediment Candidates
1. `aimos-sdk`, `aimos_mobile_app`, `jarvis_injector`, `lumin_snap_system` — likely historical/aspirational
2. `quaternion_kernel` vs `quaternion_math` — duplication?
3. `igodn` — unknown purpose
4. `lucid_orchestrator` vs `orchestration_builder` — duplication?
5. `mcp_server` vs `lucid_mcp_server` — two MCP servers?

---

## 5. Acceptance Gate Status (Track B)

SEV's acceptance gate: "Every active host has one verified transport truth card and one known degraded-mode fallback."

| Requirement | Status |
|-------------|--------|
| Transport truth card for Windows host | ⚠️ PARTIAL — stdio verified, HTTP intermittent, SSE unknown |
| Degraded-mode fallback documented | ✅ YES — fail-closed law + mcp_bootstrap.cmd |
| Core systems verified | ⚠️ PARTIAL — 3/8 verified (CMC, VIF partial, CAS degraded), 5 untested |

**Track B gate: NOT YET PASSED.** Need to verify APOE, SEG, SIS, SDF-CVF and resolve HHNI.
