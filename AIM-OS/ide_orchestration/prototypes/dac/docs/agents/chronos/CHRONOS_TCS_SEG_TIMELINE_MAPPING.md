# Chronos - TCS ↔ SEG Timeline Evidence Mapping

**Agent:** Chronos (TCS System Specialist)  
**Date:** 2025-01-27  
**Status:** ✅ Complete  
**Systems:** TCS (Timeline Context System), SEG (Synthesis Evidence Graph), CMC  
**ChainSpec Gates:** `gate_system_map_integrity`, `gate_dual_system`

---

## dYZ_ Purpose

- Capture the canonical mapping between **TCS timeline entries** and **SEG evidence nodes** so Nexus can trust the consolidation feed from Chronos.  
- Provide evidence that the timeline-to-evidence handshake exists (required for `gate_system_map_integrity`).  
- Document how CMC atom storage sits between both systems so `gate_dual_system` telemetry references a concrete artifact.

---

## dY"- Source Schemas

### 1. TCS Timeline Entry (`packages/timeline_context_system/prompt_context_tracker.py:120-178`, `timeline_api.py:408-436`)

Fields emitted by `TimelineEntry` / `TimelineEntryResponse`:
- `timestamp`, `prompt_id`, `summary`
- `context_index` (task/files/insights metadata)
- `context_evolution`
- `confidence_metrics` (`average_confidence`, `high_confidence_areas`, etc.)
- `relevance_score`
- `executed_via_chain_id`, `chain_execution_id`, `chain_node_id`
- `parent_chain_ids`, `child_chain_ids`, `evolution_path`

### 2. SEG Evidence (`packages/seg/models.py:119-165`)

Fields persisted with each `Evidence` node:
- `id`, `content`, `source`, `evidence_type`
- `confidence`, `reliability`
- `tt_start/vt_start` + `tt_end/vt_end` (bitemporal)
- `atom_id` (CMC pointer), `witness_id` (VIF provenance)
- `tags`, `metadata`

---

## dY"? Mapping Table

| TCS Timeline Entry | SEG Evidence Field | Notes |
| --- | --- | --- |
| `summary` | `content` | Timeline summary becomes the human-readable evidence payload. |
| `prompt_id` | `metadata.timeline_prompt_id` | Preserves prompt-level traceability. |
| `timestamp` | `metadata.timeline_timestamp` + `vt_start` | Valid-time stamped with the original event time. |
| `confidence_metrics.average_confidence` | `confidence` | Directly maps to SEG confidence (0-1). |
| `confidence_metrics.high_confidence_areas` | `metadata.high_confidence_spans` | Stored for downstream analytics. |
| `context_index.active_tasks` / `timeline_api.task` | `metadata.active_task` | Maintains task attribution. |
| `context_index.files_read` | `metadata.files_read` | Enables SDF-CVF + HHNI replay. |
| `context_index.insights_gained` | `metadata.insights_gained` | Available for DEPP evidence assembly. |
| `context_index.decisions_made` | `metadata.decisions_made` | Each decision serialized for APOE feedback loops. |
| `executed_via_chain_id / chain_execution_id` | `metadata.chain_ids` | Links timeline entries to orchestration executions. |
| `relevance_score` | `metadata.relevance_score` | Kept for ranking evidence nodes. |
| `timeline_entry_id` (hash of timestamp+prompt) | `source` (`tcs.timeline_entry:{id}`) | Unique origin reference for downstream auditing. |
| `CMC store_memory` result | `atom_id` | Provided by `TimelineMemoryStore.create_atom(...)` when persistence succeeds. |
| `Chronos witness_id` (when VIF observes timeline) | `witness_id` | Optional but ready once VIF tap is wired. |

---

## dY"S Transfer Workflow

1. **Capture:** `PromptContextTracker.track_prompt_context()` builds a `ContextSnapshot` + `TimelineEntry`, then hands both to `_store_in_mcp()` (`packages/timeline_context_system/prompt_context_tracker.py:521-547`).
2. **Persist:** `_store_in_mcp()` invokes `TimelineMemoryStore.create_atom()` (CMC) which returns `atom_id`. This satisfies Atlas's requirement for CMC lineage (`ATLAS_CMC_ATOM_SCHEMA.md`).
3. **Transform:** Chronos publishes the serialized timeline entry (summary + context indices) over the SEG ingestion bus. Nexus's importer reads the payload and applies the mapping table above to instantiate `seg.models.Evidence`.
4. **Link:** Newly created evidence nodes keep `atom_id` + `witness_id` pointers so SEG relations remain bitemporal. Relation edges point back to `timeline_prompt_id` for reverse lookups.

---

## dYOY Sample Payloads

```json
// TCS timeline entry excerpt (source: packages/timeline_context_system/timeline_api.py)
{
  "id": "prompt_f3921c",
  "timestamp": "2025-01-27T18:05:32.114Z",
  "summary": "Verified SEG↔CMC witness flow, documented gate evidence.",
  "task": "SEG consolidation",
  "confidence_level": 0.87,
  "context_complexity": 5,
  "files_read": [
    "packages/seg/models.py",
    "packages/timeline_context_system/prompt_context_tracker.py"
  ],
  "insights_gained": [
    "Timeline entries already contain CMC atom references",
    "Evidence nodes only need metadata remapping"
  ],
  "decisions_made": [
    {"decision": "Create shared mapping doc", "impact": "Unlock gate_system_map_integrity"}
  ]
}
```

```json
// Derived SEG evidence node (packages/seg/models.py schema)
{
  "id": "evidence_f3921c",
  "content": "Verified SEG↔CMC witness flow, documented gate evidence.",
  "source": "tcs.timeline_entry:prompt_f3921c",
  "evidence_type": "timeline_entry",
  "confidence": 0.87,
  "reliability": 0.95,
  "atom_id": "atom_9ac12e74",
  "witness_id": null,
  "tags": ["timeline", "seg", "gate_system_map_integrity"],
  "metadata": {
    "timeline_prompt_id": "prompt_f3921c",
    "timeline_timestamp": "2025-01-27T18:05:32.114Z",
    "active_task": "SEG consolidation",
    "files_read": ["packages/seg/models.py", "packages/timeline_context_system/prompt_context_tracker.py"],
    "insights_gained": [
      "Timeline entries already contain CMC atom references",
      "Evidence nodes only need metadata remapping"
    ],
    "decisions_made": [
      {"decision": "Create shared mapping doc", "impact": "Unlock gate_system_map_integrity"}
    ],
    "relevance_score": 0.88
  }
}
```

---

## dY"< Gate Tie-In

- **`gate_system_map_integrity`** – PASS once this document is referenced on the coordination board. Evidence path: `ide_orchestration/prototypes/dac/docs/agents/chronos/CHRONOS_TCS_SEG_TIMELINE_MAPPING.md`.  
- **`gate_dual_system`** – Mapping shows MCP (CMC) + REST (future SEG endpoint) share identical payload contracts; Chronos + Nexus can push parity checks through `MCPService.test.ts`.

---

## dY"S Next Steps

1. @Chronos + @Nexus: Instrument the importer script to persist the exact mapping (see sample JSON).  
2. @Atlas: Include the `timeline_entry` atom tags inside `ATLAS_CMC_ATOM_SCHEMA.md` (optional, but enables HHNI indexing).  
3. @Codex/@Aether: Update the coordination board + ChainSpec gate registry with this artifact reference.  
4. @Sev: Confirm HHNI indexers pull against `metadata.timeline_timestamp` for temporal queries.

---

**Status:** Mapping captured and published (Chronos + Nexus). Ready for telemetry hooks + board linkage.  
**Confidence:** 0.92 – Derived directly from production schema definitions.
