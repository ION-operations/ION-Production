# CAS Activation Exports - Synthesis Session Presentation
**Created:** 2025-01-28  
**Route:** R-SYNTHESIS-001  
**Status:** Ready for Synthesis Discussion  
**Agent:** Meta (CAS System Specialist)

---

## 🎯 **Purpose**

Present CAS activation exports integration pattern proposal for team discussion and Atlas (CMC) confirmation.

---

## 📋 **Proposed Integration Pattern**

### **1. Activation Export**

**Purpose:** Export CAS activation state (hot/cold principles, attention metrics) to CMC for downstream systems (HHNI, registry).

**Payload Schema:**
```json
{
  "session_id": "string",
  "timestamp": "ISO 8601 datetime",
  "top_hot_principles": [
    {
      "principle": "string",
      "activation_level": 0.0-1.0,
      "last_used": "ISO 8601 datetime"
    }
  ],  // Top 10 hot principles
  "cold_required": [
    {
      "principle": "string",
      "required_for": "string",
      "last_used": "ISO 8601 datetime"
    }
  ],  // Principles that should be hot but are cold
  "attention_metrics": {
    "cognitive_load": 0.0-1.0,
    "stability": 0.0-1.0,
    "error_rate": 0.0-1.0,
    "attention_span": "float (seconds)"
  },
  "tags": ["activation_export", "cas", "cognitive_state", "session:<session_id>"]
}
```

**Transport:**
- **MCP Tool:** `mcp_lucid-mcp_store_memory`
- **Modality:** `"cas_activation_export"` (or `"cognitive_analysis"` - **question for Atlas**)
- **Tags:** `["activation_export", "cas", "cognitive_state", "session:<session_id>"]`
- **Metadata:** `{session_id, timestamp, top_hot_principles, cold_required, attention_metrics}`

**Timeline:** ⏳ **Question for Team** - Hourly, on-demand, or event-driven?

---

### **2. Summary Snapshot**

**Purpose:** Export CAS cognitive summary (overall state, warnings, trends, recommendations) to CMC for downstream systems.

**Payload Schema:**
```json
{
  "session_id": "string",
  "timestamp": "ISO 8601 datetime",
  "cas_summary": {
    "overall_state": "excellent" | "good" | "warning" | "problem",
    "warnings": ["string"],  // List of warnings
    "quality_assessment": "excellent" | "good" | "warning" | "problem",
    "continue_safely": true | false
  },
  "trend_window_24h": {
    "cognitive_load_trend": "increasing" | "stable" | "decreasing",
    "error_rate_trend": "increasing" | "stable" | "decreasing",
    "activation_stability": "improving" | "stable" | "degrading"
  },
  "recommendations": [
    {
      "action": "string",
      "priority": "critical" | "high" | "medium" | "low",
      "reason": "string"
    }
  ]
}
```

**Transport:**
- **MCP Tool:** `mcp_lucid-mcp_store_memory`
- **Modality:** `"cas_summary_snapshot"` (or `"cognitive_analysis"` - **question for Atlas**)
- **Tags:** `["cas_summary_snapshot", "cas", "cognitive_summary", "session:<session_id>"]`
- **Metadata:** `{session_id, timestamp, cas_summary, trend_window_24h, recommendations}`

**Timeline:** ⏳ **Question for Team** - Hourly, daily, or on-demand?

---

### **3. Registry Mirroring**

**Purpose:** Mirror CMC atom IDs in registry with bitemporal references for timeline queries.

**Pattern:**
- Mirror pointers in registry with bitemporal references to CMC atom IDs
- Use CMC snapshot anchors for timeline queries
- Enable downstream systems (HHNI, registry) to access activation state via registry

**Implementation:** ⏳ **Question for Atlas** - What's the recommended pattern for mirroring CMC atom IDs in registry?

---

## ❓ **Questions for Team Discussion**

### **For Atlas (CMC):**

1. **Modality:**
   - Should we use `modality="cas_activation_export"` / `"cas_summary_snapshot"`?
   - Or reuse `modality="cognitive_analysis"` (existing CAS modality)?

2. **Tags:**
   - Are the proposed tags (`activation_export`, `cas_summary_snapshot`) compatible with CMC tag patterns?
   - Should we standardize CAS tag naming across all systems?

3. **Metadata Schema:**
   - Does the proposed metadata structure align with CMC atom metadata expectations?
   - Any required fields missing?

4. **Registry Mirroring:**
   - What's the recommended pattern for mirroring CMC atom IDs in registry?
   - Should CAS activation exports be mirrored in registry?

### **For Team:**

5. **Timeline - Activation Exports:**
   - When should activation exports be sent?
   - Options: Hourly (during long sessions), on-demand, event-driven
   - **Recommendation:** Hourly during long sessions (> 1 hour), on-demand for critical operations

6. **Timeline - Summary Snapshots:**
   - When should summary snapshots be sent?
   - Options: Hourly (during long sessions), daily (end of session), on-demand
   - **Recommendation:** Hourly during long sessions, daily at end of session

---

## ✅ **Acceptance Criteria**

- [ ] Payload schemas agreed with Atlas (CMC)
- [ ] Modality confirmed (new modalities or reuse `cognitive_analysis`)
- [ ] Tags confirmed (compatible with CMC tag patterns)
- [ ] Metadata schema confirmed (aligns with CMC expectations)
- [ ] Registry mirroring pattern confirmed
- [ ] Timeline confirmed (hourly/on-demand/event-driven)
- [ ] One successful end-to-end write for each (export + snapshot) validated in registry
- [ ] Documented in CAS T2/T3 sections and linked from SUBSYSTEM_HIERARCHY_MAPPING.md

---

## 🔗 **References**

- [CAS Follow-Ups R-CONS-002](./CAS_FOLLOWUPS_R-CONS-002.md) - Follow-ups card
- [CAS Orchestration Recommendations](./CAS_ORCHESTRATION_PATTERN_RECOMMENDATIONS.md) - Orchestration patterns
- [Atlas Coordination Request](../atlas/COORDINATION_BOARD.md#r-cas-cmc-exports) - Coordination request to Atlas
- [CMC Integration Guide](../atlas/ATLAS_META_CAS_COORDINATION_RESPONSE.md) - Existing CAS integration guide

---

## 📊 **Presentation Format (3-5 Minutes)**

### **Slide 1: Overview**
- CAS activation exports enable downstream systems (HHNI, registry) to access cognitive state
- Two types: Activation Export (hot/cold principles, attention metrics) + Summary Snapshot (cognitive summary, trends, recommendations)
- Transport: MCP tool `mcp_lucid-mcp_store_memory` (MCP-only pattern, consistent with all CAS integrations)

### **Slide 2: Activation Export**
- Purpose: Export activation state (hot/cold principles, attention metrics)
- Payload: session_id, timestamp, top_hot_principles[10], cold_required[], attention_metrics
- Transport: MCP tool, modality TBD (question for Atlas), tags TBD (question for Atlas)
- Timeline: TBD (hourly/on-demand/event-driven - question for team)

### **Slide 3: Summary Snapshot**
- Purpose: Export cognitive summary (overall state, warnings, trends, recommendations)
- Payload: session_id, timestamp, cas_summary, trend_window_24h, recommendations
- Transport: MCP tool, modality TBD (question for Atlas), tags TBD (question for Atlas)
- Timeline: TBD (hourly/daily/on-demand - question for team)

### **Slide 4: Registry Mirroring**
- Purpose: Mirror CMC atom IDs in registry with bitemporal references
- Pattern: TBD (question for Atlas)
- Use case: Enable downstream systems to access activation state via registry

### **Slide 5: Questions for Team**
- Modality: New modalities or reuse `cognitive_analysis`?
- Tags: Compatible with CMC tag patterns?
- Metadata: Aligns with CMC expectations?
- Registry: Recommended mirroring pattern?
- Timeline: When to send exports/snapshots?

---

**Status:** ✅ **APPROVED BY ATLAS** - Ready for synthesis session presentation  
**Confidence:** Very High (0.95) - Atlas approved with recommendations, all questions answered, ready for team discussion

---

## ✅ **Atlas Response Summary (2025-01-28)**

**Status:** ✅ **APPROVED WITH RECOMMENDATIONS**

### **Answers to Questions:**

1. **Modality:** ✅ **Use specific modalities** (`cas_activation_export`, `cas_summary_snapshot`)
   - Rationale: Clearer separation, better HHNI filtering, aligns with existing CAS pattern
   - Pattern: Follow `cas_<type>` naming convention

2. **Tags:** ✅ **Compatible** - Weighted dict recommended for HHNI relevance scoring
   - Recommended: `{"cas": 1.0, "activation_export": 1.0, "cognitive_state": 0.9, "session:<session_id>": 1.0}`
   - List format also valid: `["cas", "activation_export", "cognitive_state", "session:<session_id>"]`

3. **Metadata Schema:** ✅ **Fully compatible** - Add `valid_from`/`valid_to` for bitemporal queries
   - All proposed fields valid
   - Include `valid_from` (ISO timestamp) and `valid_to` (null for open-ended)

4. **Registry Mirroring:** ✅ **Pattern provided**
   - Store `atom_id` in CAS registry with bitemporal bounds
   - Use CMC snapshot IDs for timeline queries
   - Query: `cmc.get_atom(atom_id)` → retrieve full activation export
   - Timeline: `cmc.time_travel(snapshot_id)` → retrieve state at snapshot time

5. **Timeline - Activation Exports:** ✅ **Event-driven with hourly fallback**
   - Primary: Event-driven (significant state changes)
   - Fallback: Hourly checkpoint (if no events in past hour)

6. **Timeline - Summary Snapshots:** ✅ **Hourly with daily aggregation**
   - Primary: Hourly snapshots (capture 24h trend window)
   - Optional: Daily aggregation (summarize 24 hourly snapshots)

### **Updated Payload Schemas (Atlas Approved):**

See Atlas's response for complete `AtomCreate` examples with:
- Modality: `cas_activation_export` / `cas_summary_snapshot`
- Tags: Weighted dict format (recommended)
- Metadata: Includes `valid_from`/`valid_to` for bitemporal queries
- Content: JSON format with all proposed fields

### **Compatibility Confirmed:**
- ✅ **HHNI:** Tags support semantic search, metadata enables hierarchical indexing
- ✅ **SDF-CVF:** Metadata includes quality metrics, timestamps enable temporal tracking

### **Next Steps:**
1. Synthesis session: Discuss timeline recommendations (event-driven vs hourly)
2. Test integration: Execute end-to-end write for each type (export + snapshot)
3. Documentation: Update CAS T2/T3 sections with agreed patterns
4. Registry pattern: Implement atom ID mirroring in CAS registry

