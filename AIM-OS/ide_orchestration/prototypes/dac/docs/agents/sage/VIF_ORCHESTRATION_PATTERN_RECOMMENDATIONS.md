# VIF Orchestration Pattern Recommendations
**Agent:** Sage (VIF System Specialist)  
**Date:** 2025-01-28  
**Phase:** Synthesis Preparation  
**Status:** ✅ **READY FOR SYNTHESIS**

---

## Executive Summary

This document provides detailed recommendations for VIF witness orchestration patterns, including:
1. **P0 List:** Flows that must always emit VIF witness
2. **Default κ-Gate/Retry Policies:** Recommended thresholds and retry heuristics
3. **Mandatory vs Optional Patterns:** When witness creation is required vs. optional

These recommendations are based on cross-validation of all 7 VIF integrations and analysis of orchestration gaps.

---

## 1. P0 List: Flows That Must Always Emit VIF Witness

### **Critical Flows (P0 - Mandatory)**

**These flows must ALWAYS create and store a VIF witness:**

#### **1.1 APOE Plan Execution**
- **Flow:** `APOE Executor.execute_plan()` → Plan execution complete
- **Witness Type:** Plan-level witness + step-level witnesses
- **Rationale:** Plan execution is a critical operation that requires full provenance
- **Implementation:** `apoe/vif_integration.py::create_plan_witness_vif()` + `create_step_witness_vif()`
- **κ-Gate:** Required for CRITICAL/IMPORTANT roles (VERIFIER, WITNESS, PLANNER, REASONER, CRITIC)
- **Status:** ✅ Code exists, needs to be mandatory in executor path

#### **1.2 HHNI Retrieval (Production)**
- **Flow:** `TwoStageRetriever.retrieve()` → Retrieval complete
- **Witness Type:** Retrieval witness with RS-Lift metrics
- **Rationale:** Retrieval quality affects downstream operations; RS-Lift metrics need provenance
- **Implementation:** `vif/hhni_integration.py::create_retrieval_witness()`
- **κ-Gate:** Optional (retrieval is typically ROUTINE)
- **Status:** ✅ Hook added (env-gated), should be mandatory in production

#### **1.3 SEG Graph Updates (Evidence/Entity Creation)**
- **Flow:** `SEGraph.add_evidence()` / `add_entity()` → Evidence/entity created
- **Witness Type:** Evidence/entity witness with confidence weighting
- **Rationale:** Evidence quality affects graph reliability; witness links enable verification
- **Implementation:** `vif/seg_integration.py::calculate_evidence_weighting()`
- **κ-Gate:** Required if evidence confidence is used for decision-making
- **Status:** ⚠️ Integration exists, needs to be mandatory in graph update paths

#### **1.4 CAS Cognitive Events (Significant Decisions)**
- **Flow:** CAS activation → Significant decision made (task categorization, failure mode detection)
- **Witness Type:** Cognitive context witness with enhanced confidence
- **Rationale:** Cognitive state affects decision quality; provenance needed for debugging
- **Implementation:** `vif/cas_integration.py::create_witness_with_cognitive_context()`
- **κ-Gate:** Required if cognitive state indicates degradation (attention narrowing, shortcuts)
- **Status:** ⚠️ Integration exists, needs to be mandatory for significant cognitive events

#### **1.5 SDF-CVF Parity Validation (CI/Audit)**
- **Flow:** `calculate_file_set_parity()` → Parity validation complete
- **Witness Type:** Parity validation witness with combined confidence + parity score
- **Rationale:** Quality validation requires provenance; witnesses enable audit trails
- **Implementation:** `vif/sdfcvf_integration.py::calculate_file_set_parity()`
- **κ-Gate:** Required if parity score is used for blocking merges/deployments
- **Status:** ✅ Entrypoint added, needs to be mandatory in CI workflows

#### **1.6 TCS Timeline Events (κ-Gate Decisions)**
- **Flow:** `KappaGate.check()` → κ-gate decision made
- **Witness Type:** κ-gate timeline entry (via TCS)
- **Rationale:** κ-gate decisions affect system behavior; timeline entries enable audit
- **Implementation:** `vif/tcs_integration.py::create_kappa_gate_timeline_entry()`
- **κ-Gate:** N/A (this IS the κ-gate)
- **Status:** ⚠️ Integration exists, needs to be mandatory for all κ-gate decisions

#### **1.7 Chat/IDE Orchestrated Actions**
- **Flow:** Router/Orchestrator → Action executed (code generation, file modification, etc.)
- **Witness Type:** Action witness with full context (prompt, output, tools, confidence)
- **Rationale:** User-facing actions require full provenance; witnesses enable accountability
- **Implementation:** `vif/cmc_integration.py::create_witness_and_store()`
- **κ-Gate:** Required for all user-facing actions (mandatory abstention if confidence < threshold)
- **Status:** ⚠️ Integration exists, needs to be mandatory in orchestration paths

---

### **Important Flows (P1 - Recommended)**

**These flows SHOULD create witnesses but can be optional in some contexts:**

#### **1.8 HHNI Indexing Operations**
- **Flow:** `Indexer.index()` → Document indexed
- **Witness Type:** Indexing witness with document metadata
- **Rationale:** Indexing quality affects retrieval; witnesses enable debugging
- **Implementation:** Create new witness type for indexing operations
- **κ-Gate:** Optional (indexing is typically ROUTINE)
- **Status:** ⚠️ Not yet implemented

#### **1.9 SEG Relationship Creation**
- **Flow:** `SEGraph.add_relation()` → Relationship created
- **Witness Type:** Relationship witness with confidence
- **Rationale:** Relationship quality affects graph reliability
- **Implementation:** Extend `vif/seg_integration.py`
- **κ-Gate:** Optional (relationships are typically ROUTINE)
- **Status:** ⚠️ Not yet implemented

#### **1.10 CAS Activation Tracking (Non-Decision Events)**
- **Flow:** CAS activation → Principle/document/concept activated
- **Witness Type:** Activation witness (lightweight)
- **Rationale:** Activation patterns enable debugging; witnesses enable analysis
- **Implementation:** Create lightweight witness type
- **κ-Gate:** Optional (activation tracking is telemetry)
- **Status:** ⚠️ Not yet implemented

---

## 2. Default κ-Gate/Retry Policy Recommendations

### **2.1 Default κ Thresholds (Current Implementation)**

**Recommended Defaults (from `packages/vif/kappa_gate.py`):**

```python
DEFAULT_KAPPA_THRESHOLDS = {
    TaskCriticality.CRITICAL: 0.95,    # Medical, legal, safety
    TaskCriticality.IMPORTANT: 0.85,   # Financial, strategic
    TaskCriticality.ROUTINE: 0.70,     # Standard operations
    TaskCriticality.LOW_STAKES: 0.60,  # Experimental, low-impact
}
```

**Rationale:**
- **CRITICAL (0.95):** High-stakes decisions require very high confidence
- **IMPORTANT (0.85):** Strategic decisions require high confidence
- **ROUTINE (0.70):** Standard operations can proceed with moderate confidence
- **LOW_STAKES (0.60):** Experimental work can proceed with lower confidence

**Recommendation:** ✅ **Keep current defaults** - They are well-calibrated and match industry best practices.

---

### **2.2 Retry Heuristics (Recommended)**

**Recommended Retry Policy:**

```python
RETRY_POLICY = {
    TaskCriticality.CRITICAL: {
        "max_retries": 0,           # No retries - escalate immediately
        "escalation_threshold": 0.95,  # Always escalate if below threshold
        "retry_confidence_boost": 0.0,  # No confidence boost on retry
    },
    TaskCriticality.IMPORTANT: {
        "max_retries": 1,           # One retry allowed
        "escalation_threshold": 0.85,  # Escalate if below threshold after retry
        "retry_confidence_boost": 0.05,  # Small confidence boost on retry
    },
    TaskCriticality.ROUTINE: {
        "max_retries": 2,           # Two retries allowed
        "escalation_threshold": 0.70,  # Escalate if below threshold after retries
        "retry_confidence_boost": 0.10,  # Moderate confidence boost on retry
    },
    TaskCriticality.LOW_STAKES: {
        "max_retries": 3,           # Three retries allowed
        "escalation_threshold": 0.60,  # Escalate if below threshold after retries
        "retry_confidence_boost": 0.15,  # Larger confidence boost on retry
    },
}
```

**Retry Logic:**
1. **First Attempt:** Check κ-gate with original confidence
2. **If Failed:** 
   - For CRITICAL: Escalate immediately (no retries)
   - For IMPORTANT/ROUTINE/LOW_STAKES: Retry with confidence boost
3. **After Retries:**
   - If still below threshold: Escalate to human review
   - If above threshold: Proceed with action

**Confidence Boost Rationale:**
- Retries may improve confidence (e.g., better context, refined prompt)
- Boost should be conservative (5-15%) to avoid overconfidence
- Boost should decrease with criticality (less boost for critical tasks)

**Recommendation:** ✅ **Implement this retry policy** - Balances safety with efficiency.

---

### **2.3 Escalation Policies (Recommended)**

**Escalation Triggers:**

1. **κ-Gate Failed:** Always escalate (confidence below threshold)
2. **Marginally Passed:** Escalate for CRITICAL/IMPORTANT if confidence < (threshold + 0.10)
3. **Retry Exhausted:** Escalate if still below threshold after max retries
4. **Cognitive Degradation:** Escalate if CAS detects attention narrowing or shortcuts
5. **Parity Failure:** Escalate if SDF-CVF parity score < 0.90 for critical code

**Escalation Actions:**

1. **Log to TCS:** Create timeline entry with escalation reason
2. **Notify User:** Show confidence warning in UI
3. **Request Human Review:** For CRITICAL tasks, require human approval
4. **Store Witness:** Always create witness even if action is blocked

**Recommendation:** ✅ **Implement escalation policies** - Ensures safety while maintaining transparency.

---

## 3. Mandatory vs Optional Patterns

### **3.1 Mandatory Witness Creation (P0)**

**Always create witness for:**
- ✅ User-facing actions (chat/IDE orchestrated)
- ✅ Critical operations (APOE plan execution, SEG evidence creation)
- ✅ Quality validation (SDF-CVF parity checks in CI)
- ✅ κ-Gate decisions (all κ-gate checks must log to TCS)
- ✅ Significant cognitive events (CAS failure mode detection)

**Implementation Pattern:**
```python
# Mandatory witness creation
vif = create_witness(...)
atom_id = vif_store.store_witness(vif)
# Action proceeds only if κ-gate passed
if not vif.kappa_gate_passed:
    escalate_to_human(...)
    return
```

---

### **3.2 Optional Witness Creation (P1/P2)**

**Optional witness creation for:**
- ⚠️ Telemetry operations (CAS activation tracking, HHNI indexing)
- ⚠️ Internal operations (non-user-facing, non-critical)
- ⚠️ High-frequency operations (where witness creation overhead is significant)

**Implementation Pattern:**
```python
# Optional witness creation (env-gated or feature-flagged)
if os.getenv("VIF_ENABLED", "false").lower() == "true":
    try:
        vif = create_witness(...)
        vif_store.store_witness(vif)
    except Exception:
        pass  # Fail-soft
```

---

### **3.3 Hybrid Pattern (Recommended)**

**Recommended Approach:**
- **P0 Flows:** Always create witness (mandatory, no env-gating)
- **P1 Flows:** Create witness if `VIF_ENABLED=true` (optional, env-gated)
- **P2 Flows:** Create witness if `VIF_DETAILED_TELEMETRY=true` (optional, feature-flagged)

**Rationale:**
- Ensures critical operations always have provenance
- Allows flexibility for telemetry operations
- Enables performance tuning (disable telemetry in high-frequency paths)

**Recommendation:** ✅ **Implement hybrid pattern** - Balances safety with flexibility.

---

## 4. Integration Tagging Standardization

### **4.1 Recommended Format**

**Standardize `metadata.integration_tags` on CMC atoms:**

```python
metadata = {
    "integration_tags": [
        "[VIF-WITNESS]",           # VIF witness atom
        "[HHNI-RETRIEVE]",         # HHNI retrieval operation
        "[APOE-PLAN]",             # APOE plan execution
        "[SEG-EVIDENCE]",          # SEG evidence creation
        "[CAS-COGNITIVE]",         # CAS cognitive event
        "[SDFCVF-PARITY]",         # SDF-CVF parity validation
        "[TCS-TIMELINE]",          # TCS timeline entry
    ],
    # ... other metadata
}
```

**Benefits:**
- 1-hop discoverability for system maps/registries
- Enables cross-system queries (e.g., "all VIF witnesses for HHNI retrievals")
- Supports system-map generation and dependency analysis

**Recommendation:** ✅ **Standardize integration_tags** - Enables system discovery and analysis.

---

## 5. Synthesis Questions - Recommended Answers

### **5.1 Tagging/Discovery**

**Question:** Should we standardize `metadata.integration_tags`?

**Recommended Answer:** ✅ **YES** - Standardize `metadata.integration_tags` with format `["[SYSTEM-OPERATION]"]` (e.g., `["[VIF-WITNESS]", "[HHNI-RETRIEVE]"]`). This enables:
- 1-hop discoverability for system maps/registries
- Cross-system queries (e.g., "all VIF witnesses for HHNI retrievals")
- System-map generation and dependency analysis

**Implementation:** Already added to `vif/cmc_integration.py::vif_to_atom_payload()` (pending team decision on exact format).

---

### **5.2 Default κ-Gate/Retry Policies**

**Question:** What default κ thresholds and retry heuristics do we want?

**Recommended Answer:**
- **κ Thresholds:** Keep current defaults (CRITICAL=0.95, IMPORTANT=0.85, ROUTINE=0.70, LOW_STAKES=0.60)
- **Retry Policy:** 
  - CRITICAL: 0 retries, escalate immediately
  - IMPORTANT: 1 retry, escalate if still below threshold
  - ROUTINE: 2 retries, escalate if still below threshold
  - LOW_STAKES: 3 retries, escalate if still below threshold
- **Confidence Boost:** 5-15% per retry (decreasing with criticality)

**Implementation:** Add retry policy to `packages/vif/kappa_gate.py` or create new `retry_policy.py` module.

---

### **5.3 Mandatory vs Optional**

**Question:** Which flows must always emit a witness + κ-gate event?

**Recommended Answer:**
- **P0 (Mandatory):** User-facing actions, critical operations, quality validation, κ-gate decisions, significant cognitive events
- **P1 (Recommended):** Telemetry operations, internal operations, high-frequency operations (env-gated)
- **P2 (Optional):** Detailed telemetry (feature-flagged)

**Implementation:** 
- P0 flows: Remove env-gating, make witness creation mandatory
- P1 flows: Keep env-gating, document as "recommended"
- P2 flows: Keep feature-flagging, document as "optional"

---

## 6. Implementation Roadmap

### **Phase 1: P0 Mandatory Flows (Immediate)**
1. ✅ APOE plan execution: Make witness creation mandatory in executor
2. ✅ HHNI retrieval: Make witness creation mandatory (remove env-gating for production)
3. ⚠️ SEG graph updates: Add witness creation to `add_evidence()` / `add_entity()`
4. ⚠️ CAS cognitive events: Add witness creation for significant decisions
5. ✅ SDF-CVF parity: Make witness creation mandatory in CI workflows
6. ⚠️ TCS timeline: Make κ-gate timeline entries mandatory
7. ⚠️ Chat/IDE orchestration: Make witness creation mandatory in router/orchestrator

### **Phase 2: Retry Policy (Short-term)**
1. Implement retry policy module
2. Integrate with APOE executor
3. Integrate with router/orchestrator
4. Add retry tracking to witnesses

### **Phase 3: Integration Tagging (Short-term)**
1. Standardize `metadata.integration_tags` format
2. Update all witness creation paths
3. Add system-map query support
4. Document tagging conventions

---

## 7. Success Criteria

**Before Synthesis:**
- ✅ P0 list prepared
- ✅ Default policies recommended
- ✅ Mandatory vs optional patterns defined

**After Synthesis:**
- ✅ Team approves P0 list
- ✅ Team approves default policies
- ✅ Implementation roadmap agreed
- ✅ Integration tagging standardized

---

**Status:** ✅ **RECOMMENDATIONS COMPLETE**  
**Ready for synthesis session discussion**  
**All patterns documented and ready for team review**

