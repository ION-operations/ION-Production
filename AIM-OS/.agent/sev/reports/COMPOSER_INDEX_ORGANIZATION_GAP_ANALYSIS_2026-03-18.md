# COMPOSER Index & Organization Gap Analysis — 2026-03-18

**Author:** COMPOSER  
**Mission:** OPUS handoff — AIM-OS Index & Organization Gaps  
**Source:** `C:\Users\bombe\.gemini\antigravity\brain\bb5c5c75-96d4-4542-ae74-7e08d1450395\composer_audit_handoff.md.resolved`  
**Method:** Read-only audit; builds on Codex consolidation (March 13–14)  
**Status:** Complete

---

## Executive Summary

AIM-OS has **~76 packages** (excluding `__pycache__`), **39 scripts** in `scripts/ai_engine/`, and **no `apps/` directory** at repo root. The `AIMOS_MASTER_SYSTEM_INDEX.md` (March 9) is **disconnected** from the protocol web, **stale** (9+ days), and **missing 6+ packages** built since the last audit. The **CredentialVaultService** (cost/vault) in `browser-automation-service` is **undiscoverable** from any index. Genome count is **severely stale** (index says 21; 158+ genome-related files exist).

---

## Phase 1: Index & Map Gap Analysis

### 1.1 Packages — Found vs Indexed

**Current crawl (2026-03-18):** 76 directories under `packages/` (excluding `__pycache__`).

**Packages on disk but NOT in AIMOS_MASTER_SYSTEM_INDEX:**

| Package | Path | Evidence |
|---------|------|----------|
| **blueprint_system** | `packages/blueprint_system/` | blueprint_parser.py, blueprint_compiler.py, blueprint_auditor.py |
| **gemini_agent** | `packages/gemini_agent/` | gemini_conversation.py, gemini-agent.py, handoff.py, session.py |
| **adaptive_system** | `packages/adaptive_system/` | Directory present |
| **aimos_mcp** | `packages/aimos_mcp/` | Directory present |
| **aim-os-integration** | `packages/aim-os-integration/` | Directory present |
| **mcp_console** | `packages/mcp_console/` | Directory present |

**Codex audit (March 14):** 70 packages. Current count: 76. **+6 packages** since consolidation.

### 1.2 Apps — Path Mismatch (Stale) -Braden:"moved as this was non related projects"

| Index Claim | Actual Location | Status |
|-------------|-----------------|--------|
| `apps/echo-forge-loop/` | `echo-forge-loop/` (repo root) | **STALE** — apps/ does not exist |
| `apps/system-atlas/` | Not found | **STALE** or moved |
| `apps/ProEarth/` | Not found at root | **UNVERIFIED** |
| `apps/planet-engine/` | Not found | **UNVERIFIED** |
| `apps/Globe/` | Not found | **UNVERIFIED** |

**Finding:** `apps/` directory **does not exist** at `C:\Users\bombe\Desktop\AIM-OS`. Echo Forge Loop is at **root** `echo-forge-loop/`. AIMOS_MASTER_SYSTEM_INDEX and AIMOS_MAJOR_SYSTEMS both reference `apps/` paths that are wrong.

### 1.3 Scripts — AI Engine

**Current crawl:** 39 `.py` files in `scripts/ai_engine/` (including tests).

**Files in scripts/ai_engine/ NOT explicitly named in AIMOS_MASTER_SYSTEM_INDEX:**

| File | Status |
|------|--------|
| `genome_assembler.py` | **Missing from index** |
| `extract_production.py` | In index under "extract_production" — verify |
| `test_*.py` (10 files) | Test harnesses — index does not list tests |

### 1.4 CredentialVaultService / Cost Monitor — Discoverability Gap

**Handoff problem:** "An agent asking 'where is the cost monitor?' has no way to find CredentialVaultService."

**Actual location:** `packages/browser-automation-service/src/services/credentialVaultService.ts`

**Index status:** AIMOS_MASTER_SYSTEM_INDEX lists "Browser Automation Service" but does **not** mention:
- CredentialVaultService
- Vault API (`/api/connections/vault/*`)
- Cost/usage limiting
- MCP bridge auth gates

**Recommendation:** Add explicit sub-system entry: "CredentialVaultService — `packages/browser-automation-service/src/services/credentialVaultService.ts` — API credential storage, usage limits, vault linking."

### 1.5 Stale Entries — Indexed but Path Wrong or Unverified

| Index Entry | Issue |
|-------------|-------|
| `apps/echo-forge-loop/` | Path wrong — use `echo-forge-loop/` |
| `packages/agent_genome` | "dedicated runtime package still missing" — correct, not on disk |
| Genome count "21 genome files" | **Severely stale** — 158+ genome-related files in `.agent/genomes/` |
| Package count "68" (SYSTEM_REGISTRY) | Stale — 76 now |
| Package count "70" (Codex) | Stale — 76 now |

### 1.6 Cross-Reference Gaps

| Index | References AIMOS_MASTER_SYSTEM_INDEX? | References SYSTEM_REGISTRY? |
|-------|--------------------------------------|----------------------------|
| `.agent/index/MASTER.md` | **NO** | **NO** |
| `.agent/MAIN.md` | **NO** | **NO** |
| `.agent/capsules/ACTIVE.md` | **NO** | **NO** |
| `knowledge_architecture/SUPER_INDEX.md` | **NO** (concept map, not system index) | **NO** |
| `PROJECT_TRUTH/01_canonical_system_index.md` | **NO** (different scope) | **NO** |

**Critical gap:** No protocol file points an agent to "where are all the systems?" The protocol web (MAIN → MASTER → TOPICS/TAGS) indexes **protocol files only**, not systems.

### 1.7 Naming / Convention Violations

| Observation | Location |
|-------------|----------|
| `aim-os-integration` vs `aimos_mcp` | Inconsistent hyphen vs underscore in package names |
| `cmc_service.egg-info` | Build artifact under packages/ — should be excluded from system index |
| `echo-forge-loop` vs `echo_forge_loop` | Root uses hyphen; some docs may use underscore |

---

## Phase 2: Capsule & Protocol Integration Audit

### 2.1 Capsule (ACTIVE.md) — System Discovery

**Current ACTIVE.md** points to:
- Latest PRE/POST capsule
- Session metadata (Agent, Mode, Topic)
- Prompt summary

**Does NOT reference:**
- AIMOS_MASTER_SYSTEM_INDEX
- SYSTEM_REGISTRY
- Any system discovery path

**Verdict:** Capsule does **not** give an agent enough context to orient to systems. An agent receiving ACTIVE.md + system prompt has **no pointer** to "read X to find any system."

### 2.2 MASTER.md → System Index Linkage

**MASTER.md** (`.agent/index/MASTER.md`) indexes:
- Protocol files (ON_PROMPT, ON_SESSION_START, etc.)
- Context files (WORKING, MISSION, CONTRADICTIONS, BOUNDARIES)
- Capsule files (ACTIVE, INDEX)
- Index files (TOPICS, TAGS, TIMELINE)
- Legacy files (STARTUP, COMMS_DOCTRINE, AGENTS)

**Missing:** Any row for system indexes. MASTER.md has **no entry** for:
- AIMOS_MASTER_SYSTEM_INDEX
- SYSTEM_REGISTRY
- PROJECT_TRUTH/01_canonical_system_index
- knowledge_architecture/SUPER_INDEX

**Recommendation:** Add an "System Indexes" section to MASTER.md:

```markdown
## System Indexes

| File | Purpose | Update Trigger |
|------|---------|----------------|
| [AIMOS_MASTER_SYSTEM_INDEX.md](../AIMOS_MASTER_SYSTEM_INDEX.md) | Full system map — packages, scripts, apps | When new systems added |
| [SYSTEM_REGISTRY.md](../SYSTEM_REGISTRY.md) | Machine-generated package crawl | Phase 26 / crawl |
| [01_canonical_system_index.md](../../PROJECT_TRUTH/01_canonical_system_index.md) | Evidence-based status | When status changes |
```

### 2.3 Genome File Currency

**AIMOS_MASTER_SYSTEM_INDEX (line 107):** "21 genome files"

**Actual count:** 158+ files under `.agent/genomes/` including:
- Flat genomes (sev.genome.md, codex.genome.md, etc.)
- Per-agent directories (sev/, opus/, codex/, composer/, etc.)
- Cores, platforms, affinities (layered architecture)
- Legacy, assembled, specialists

**Genome files with outdated information (handoff criterion):**
- Any genome or protocol doc that says "21 genomes" — **stale**
- GENOME_PROTOCOL.md, PORTING_GUIDE — may reference old counts; verify

### 2.4 MCP Tool → System Map

See separate deliverable: **MCP_SYSTEM_MAP.md** (below, Section 5).

---

## Phase 3: Capsule Design for System Discovery

### 3.1 Proposed Addition to Capsule / Protocol

**Problem:** If capsule + system prompt don't mention a system, it's invisible.

**Solution:** Add a compact "System Discovery" block to the capsule or to ON_SESSION_START.

**Proposed block (for ACTIVE.md or ON_SESSION_START.md):**

```markdown
## System Discovery

To find any AIM-OS system:
1. **Primary:** Read [AIMOS_MASTER_SYSTEM_INDEX.md](../AIMOS_MASTER_SYSTEM_INDEX.md) — full hierarchical map
2. **Package crawl:** Read [SYSTEM_REGISTRY.md](../SYSTEM_REGISTRY.md) — machine-generated
3. **Evidence status:** Read [01_canonical_system_index.md](../../PROJECT_TRUTH/01_canonical_system_index.md) — built/part-built/doc-only
4. **Cost/vault:** CredentialVaultService → `packages/browser-automation-service/src/services/credentialVaultService.ts`
```

**Alternative:** Add to MAIN.md Quick Navigation:

| Need | File |
|------|------|
| Where is system X? | [AIMOS_MASTER_SYSTEM_INDEX.md](AIMOS_MASTER_SYSTEM_INDEX.md) |
| Package inventory | [SYSTEM_REGISTRY.md](SYSTEM_REGISTRY.md) |

### 3.2 Minimal Capsule Template Addition

```markdown
## Active Systems (This Session)

- [List 3–5 systems relevant to current task, or "See AIMOS_MASTER_SYSTEM_INDEX"]
```

---

## Acceptance Criteria — Status

| Criterion | Status |
|-----------|--------|
| Every directory in packages/ indexed or deprecated | **GAP** — 6 packages not in index |
| Every .py in scripts/ai_engine/ in system index | **GAP** — genome_assembler.py missing |
| MASTER.md references system indexes | **GAP** — no reference |
| At least one genome file corrected (21 → actual) | **PENDING** — recommendation only |
| Cost/vault location documented and discoverable | **GAP** — now documented in this report |

---

## Prior Art — Used

| Document | Use |
|----------|-----|
| codex_audit_findings.md | Package inventory baseline, cluster classification |
| CONSOLIDATION_CORRECTION_PACKET | Comparative framing, no stale/deprecation language |
| AIMOS_PACKAGE_DEPENDENCY_GRAPH_NOTES | Dependency hubs, chokepoints |
| AIMOS_SURFACE_SPECIALIZATION_AND_INACTIVITY_REGISTER | JOC/Echo Forge/host-adapter clusters |
| RUNTIME_TRUTH_MAP | Earlier package count baseline |

---

## Recommendations (Read-Only — For OPUS Approval)

1. **Update MASTER.md** — Add System Indexes section with links to AIMOS_MASTER_SYSTEM_INDEX, SYSTEM_REGISTRY, 01_canonical_system_index.
2. **Update MAIN.md** — Add "Where is system X?" row to Quick Navigation.
3. **Update AIMOS_MASTER_SYSTEM_INDEX** — Add: blueprint_system, gemini_agent, adaptive_system, aimos_mcp, aim-os-integration, mcp_console. Fix apps/ paths to actual locations. Add CredentialVaultService sub-entry under Browser Automation Service.
4. **Correct genome count** — In AIMOS_MASTER_SYSTEM_INDEX and any genome saying "21" — update to reflect layered architecture (cores + platforms + affinities + legacy + per-agent).
5. **Create MCP_SYSTEM_MAP.md** — Standalone map for MCP tool → system → path (see Section 5).

---

## 5. MCP Tool → System Map (Phase 2)

**Source:** `lucid_mcp_server.py` (root), MCP descriptors in `mcps/user-lucid-mcp/tools/`

| MCP Tool(s) | AIM-OS System | Path |
|-------------|---------------|------|
| `store_memory`, `retrieve_memory`, `get_memory_stats` | CMC (memory) | `packages/cmc_service/`, `./mcp_memory/` |
| `create_plan` | APOE (orchestration) | `packages/apoe/` |
| `track_confidence` | VIF (verifiable intelligence) | `packages/vif/` |
| `synthesize_knowledge` | SEG (synthesis) | `packages/seg/` |
| `get_hhni_status`, `index_atoms_in_hhni` | HHNI (retrieval) | `packages/hhni/` |
| `check_invariant`, `run_baseline_probe`, `detect_manipulation_signals` | SDFCVF / VIF | `packages/sdfcvf/`, `packages/vif/` |
| `create_snapshot`, `restore_snapshot`, `list_snapshots`, `archive_snapshot` | CMC / persistence | `packages/cmc_service/` |
| `add_timeline_entry`, `get_timeline_summary`, `get_timeline_entries`, `create_goal_timeline_node`, `update_goal_progress`, `query_goal_timeline` | Timeline context | `packages/timeline_context_system/` |
| `compute_intuition`, `update_intuition_weights`, `get_intuition_trace` | Intuitive intelligence | `packages/intuitive_intelligence_system/` |
| `signal_disagreement`, `get_trust_dashboard`, `request_escalation` | Trust / collaboration | In `lucid_mcp_server.py` |
| `create_dataset`, `ingest_data`, `query_dataset`, `delete_dataset` | Dataset store | In `lucid_mcp_server.py` |
| `create_application`, `deploy_application`, `manage_application_lifecycle` | Application lifecycle | In `lucid_mcp_server.py` |
| `start_autonomous_operation`, `pause_autonomous_operation`, `resume_autonomous_operation`, `stop_autonomous_operation`, `get_autonomous_status`, `run_autonomous_checklist`, `fix_autonomous_issues`, `should_continue_autonomous`, `generate_next_autonomous_task` | Autonomous ops | In `lucid_mcp_server.py` |
| `conduct_recursive_analysis`, `generate_improvement_dreams`, `test_improvement_dream` | Dream / improvement | In `lucid_mcp_server.py` |
| `send_ai_message`, `get_ai_messages`, `start_ai_discussion`, `handoff_task_to_ai`, `share_ai_profile`, `get_ai_collaboration_summary` | AI messaging | In `lucid_mcp_server.py` |
| `get_consciousness_metrics`, `run_cognitive_audit`, `analyze_thought_patterns`, `detect_cognitive_drift` | Consciousness analyzer | `packages/consciousness_analyzer/` |
| `get_nl_tags`, `get_tag_coverage`, `validate_tags`, `get_tag_issues`, `suggest_tags` | NL tags | `packages/nl_tags/` |
| `list_terminals`, `close_terminal`, `manage_terminals` | Host / Cursor bridge | `cursor-addon/`, `packages/antigravity-extension/` |
| `get_problems`, `get_problem_summary`, `get_file_problems`, `list_output_channels`, `get_output_channel_logs`, `refresh_webview`, `get_electron_logs`, `list_diagnostic_sources`, `get_unified_diagnostics` | Diagnostics | Host adapters, IDE |
| `create_prompt_chain`, `update_prompt_chain`, `get_prompt_chain`, `list_prompt_chains`, `add_chain_node`, `connect_chain_nodes`, `execute_prompt_chain` | Prompt chain executor | `packages/prompt_chain_executor/` |
| `call_api`, `list_apis`, `api_status` | API service registry | `packages/api_service_registry/` |
| `deepsearch`, `icip_search` | Search / retrieval | `packages/hhni/`, ICIP |
| `detect_work`, `activate_specialists`, `get_specialist_activation` | Specialist activation | In `lucid_mcp_server.py` |
| `execute_math_code`, `create_math_plot`, `solve_equation`, `compute_statistics`, `get_math_tools_status` | Math tools | In `lucid_mcp_server.py` |
| `record_context_capsule` | Capsule / context | `.agent/capsules/` |

**Note:** CredentialVaultService / cost monitor is **not** exposed via MCP. It lives in `packages/browser-automation-service/` and is reachable via HTTP API (`/api/connections/vault/*`), not MCP tools.

---

**COMPOSER** | Index & Organization Gap Analysis | 2026-03-18
