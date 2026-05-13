# HHNI Integration Implementation Preparation

**Author:** Sev (HHNI System Specialist)  
**Date:** 2025-01-27  
**Status:** Preparation - Waiting for Coordination Responses  
**Purpose:** Prepare implementation code templates for pending integrations

---

## 📋 **SUBSYSTEM-LEVEL INTEGRATION CHECKLIST**

### **Hierarchical Index Subsystem**
- [x] CMC integration (indexes atoms) - ✅ Complete
- [x] SEG integration (hierarchical paths) - ✅ Complete
- [x] SDF-CVF integration (index consistency) - ✅ Complete
- [x] CAS integration (activation hooks) - ✅ Added to system map (2025-01-27)
- [x] TCS integration (temporal context) - ✅ Added to system map (2025-01-27)

### **DVNS Physics Subsystem**
- [x] VIF integration (RS-lift metrics) - ✅ Complete
- [x] SDF-CVF integration (physics quartet parity) - ✅ Added to system map (2025-01-27)

### **Retrieval Subsystem**
- [x] CMC integration (atom retrieval) - ✅ Complete
- [x] APOE integration (context provision) - ✅ Complete
- [ ] VIF integration (witness creation) - ⏳ Waiting for @Sage clarification
- [x] SEG integration (evidence search) - ✅ Complete
- [x] CAS integration (activation tracking) - ✅ Complete (in system map)
- [x] TCS integration (context management) - ✅ Complete (in system map)
- [x] SDF-CVF integration (retrieval quartet parity) - ✅ Added to system map (2025-01-27)

### **Morphological Analysis Subsystem**
- [x] CMC integration (morphological data storage) - ✅ Complete
- [x] SEG integration (morphological entities) - ✅ Complete

---

## Phase 1 Subsystem Verification Tracker

| Subsystem | Integration Targets (Plan) | Status | Notes |
| --- | --- | --- | --- |
| Hierarchical Index | CMC atoms/storage, **HHNI ↔ SDF-CVF** quartet metadata, **CAS activation hooks**, **TCS context retrieval** | ✅ Docs aligned | knowledge_architecture/systems/sdfcvf/T2_architecture.md now calls out the Hierarchical Index integration; knowledge_architecture/systems/hhni/system.map.lucid.json5 lists SDF-CVF + CMC storage links + CAS + TCS (2025-01-27). |
| DVNS | **HHNI ↔ VIF** witness metrics, **HHNI ↔ SDF-CVF** quartet parity | ⚠️ Waiting on Sage | Blocked until PENDING INTEGRATIONS #1-2 clarifications (witness frequency + κ-gate confidence) land. SDF-CVF integration added to system map (2025-01-27). |
| Retrieval | **HHNI ↔ CAS/TCS/APOE/VIF/SEG** context flow | ⚠️ Docs ✅ / Impl ❓ | CAS + TCS docs now reference the Retrieval subsystem, but VIF witness template + κ-gate hook still depend on responses from Sage (sections 1-2). |
| Morphological Analysis | **HHNI ↔ SEG/CMC** lexicon sync | ✅ Monitoring | No open plan items; keep SEG enhancements in sync once new evidence node mapping ships. |

> Tracker mirrors the Phase 1 action items in SUBSYSTEM_INTEGRATION_VERIFICATION_PLAN.md so Sev can report subsystem status without re-reading the plan.
## Ã°Å¸â€œâ€¹ **PENDING INTEGRATIONS**

### **1. VIF Witness Creation (Waiting for @Sage Clarification)**

**Status:** Ã¢ÂÂ³ Waiting for clarifications on:
- Context snapshot ID pattern
- Confidence score calculation
- Witness frequency (every retrieval vs. significant only)

**Implementation Template:**
```python
# In packages/hhni/retrieval.py - TwoStageRetriever.retrieve()
from packages.vif.cmc_integration import create_witness_and_store
from packages.cmc import get_memory_store
from packages.vif import TaskCriticality

# After retrieval completes (line ~168)
def _create_vif_witness(
    self,
    result: RetrievalResult,
    query: str,
    context_snapshot_id: Optional[str] = None,
) -> Optional[tuple[Any, str]]:
    """Create VIF witness for retrieval operation.
    
    Args:
        result: RetrievalResult from retrieval
        query: Original query string
        context_snapshot_id: CMC snapshot ID (if available)
        
    Returns:
        (vif_witness, atom_id) tuple or None if skipped
    """
    # TODO: Get context_snapshot_id from CMC or create snapshot
    # TODO: Determine if witness should be created (frequency logic)
    
    if context_snapshot_id is None:
        # Option 1: Create snapshot before retrieval
        # Option 2: Use existing snapshot
        # Option 3: Skip witness creation
        return None
    
    cmc_store = get_memory_store()
    
    # Format output for witness
    output_data = {
        "selected_items": [item.node.id for item in result.selected_items],
        "total_tokens": result.total_tokens,
        "relevance_score": result.relevance_score,
        "efficiency": result.efficiency,
        "rs_lift": result.rs_lift,
        "dvns_iterations": result.dvns_iterations,
        "dvns_converged": result.dvns_converged,
    }
    output_json = json.dumps(output_data)
    
    # Create witness
    vif, atom_id = create_witness_and_store(
        cmc_store,
        operation_name=f"hhni_retrieval:{query[:50]}",
        prompt=query,
        output=output_json,
        confidence=result.relevance_score,  # TODO: Confirm confidence calculation
        context_snapshot_id=context_snapshot_id,
        model_id="hhni-retriever-v1",
        model_provider="hhni",
        task_criticality=TaskCriticality.ROUTINE,  # TODO: Determine from query metadata
        retrieved_atom_ids=[item.node.metadata.get("atom_id") for item in result.selected_items if item.node.metadata.get("atom_id")],
        tool_ids=["hhni_retrieve", "dvns_physics", "budget_manager"],
        metadata={
            "rs_lift": result.rs_lift,
            "precision_at_5": None,  # TODO: Calculate if needed
            "relevance_score": result.relevance_score,
            "efficiency": result.efficiency,
            "coarse_candidates": result.coarse_candidates,
            "dvns_iterations": result.dvns_iterations,
            "total_tokens": result.total_tokens,
        }
    )
    
    return (vif, atom_id)
```

**Questions for @Sage:**
1. How should HHNI get `context_snapshot_id`? (create snapshot, use existing, or skip?)
2. What confidence score should HHNI use? (relevance_score, efficiency, or calculated?)
3. Should witnesses be created for EVERY retrieval or only significant ones?

---

### **2. VIF ÃŽÂº-Gating (Waiting for @Sage Clarification)**

**Status:** Ã¢ÂÂ³ Waiting for clarification on confidence integration pattern

**Implementation Template:**
```python
# In packages/hhni/retrieval.py - TwoStageRetriever.retrieve()
from packages.vif import KappaGate, TaskCriticality

# After retrieval_result is generated (line ~168)
def _apply_kappa_gating(
    self,
    result: RetrievalResult,
    task_criticality: TaskCriticality = TaskCriticality.ROUTINE,
) -> RetrievalResult:
    """Apply ÃŽÂº-gating to retrieval result.
    
    Args:
        result: RetrievalResult from retrieval
        task_criticality: Task criticality level
        
    Returns:
        RetrievalResult (possibly modified or empty if gate fails)
    """
    gate = KappaGate()
    
    gate_result = gate.check(
        confidence=result.relevance_score,  # TODO: Confirm confidence source
        task_criticality=task_criticality
    )
    
    if not gate_result.passed:
        # Handle abstention
        logger.warning(
            f"HHNI retrieval abstained due to low confidence: {result.relevance_score} "
            f"(threshold: {gate_result.threshold})"
        )
        return self._empty_result(
            result.coarse_time_ms + result.dvns_time_ms,
            reason="low_confidence_abstention"
        )
    
    # Gate passed, return result
    return result
```

**Questions for @Sage:**
1. Should ÃŽÂº-gating be applied to ALL retrievals or only critical ones?
2. What confidence score should be used for gating? (relevance_score, efficiency, or calculated?)
3. How should HHNI handle abstention? (empty result, flag, or escalate?)

---

### **3. APOE Standard Handler (Waiting for @Alex Requirements)**

**Status:** Ã¢ÂÂ³ Waiting for handler standardization preferences

**Implementation Template:**
```python
# In packages/apoe/hhni_integration.py (new file)
from packages.hhni.retrieval import TwoStageRetriever, RetrievalConfig
from packages.hhni.hierarchical_index import IndexLevel
from typing import Dict, Any

def create_hhni_retriever_handler(
    hierarchical_index: HierarchicalIndex,
    default_config: Optional[RetrievalConfig] = None,
) -> Callable[[str, Dict], Dict[str, Any]]:
    """Create standard HHNI handler for APOE retriever role.
    
    Args:
        hierarchical_index: HHNI hierarchical index
        default_config: Default retrieval configuration
        
    Returns:
        Handler function for APOE retriever role
    """
    config = default_config or RetrievalConfig()
    retriever = TwoStageRetriever(hierarchical_index, config)
    
    def hhni_retrieve(description: str, params: Dict) -> Dict[str, Any]:
        """HHNI retrieval handler for APOE retriever role.
        
        Args:
            description: Step description (becomes query)
            params: ACL parameters (k, enable_dvns, etc.)
            
        Returns:
            Dictionary with results, count, confidence, etc.
        """
        # Extract parameters from ACL
        k = int(params.get("k", 100))
        enable_dvns = params.get("enable_dvns", "true").lower() == "true"
        enable_deduplication = params.get("enable_deduplication", "true").lower() == "true"
        token_budget = int(params.get("token_budget", config.token_budget))
        target_level_str = params.get("target_level", "PARAGRAPH")
        
        # Map target_level string to IndexLevel
        target_level_map = {
            "SYSTEM": IndexLevel.SYSTEM,
            "SECTION": IndexLevel.SECTION,
            "PARAGRAPH": IndexLevel.PARAGRAPH,
            "SENTENCE": IndexLevel.SENTENCE,
        }
        target_level = target_level_map.get(target_level_str.upper(), IndexLevel.PARAGRAPH)
        
        # Create retrieval config
        retrieval_config = RetrievalConfig(
            coarse_k=k,
            enable_conflict_resolution=enable_deduplication,
            token_budget=token_budget,
            # ... other config options
        )
        
        # Perform retrieval
        result = retriever.retrieve(
            query=description,
            token_budget=token_budget,
            target_level=target_level
        )
        
        # Format for APOE
        return {
            "results": [
                {
                    "content": item.node.content,
                    "relevance": item.score,
                    "source_id": item.node.id,
                    "metadata": item.node.metadata
                }
                for item in result.selected_items
            ],
            "count": len(result.selected_items),
            "confidence": result.relevance_score,
            "total_tokens": result.total_tokens,
            "rs_lift": result.rs_lift,
            "quality_metrics": {
                "conflicts_detected": result.conflicts_detected,
                "conflicts_resolved": result.conflicts_resolved,
                "compression_applied": result.compression_applied,
                "tokens_saved": result.tokens_saved_by_compression,
            }
        }
    
    return hhni_retrieve
```

**Questions for @Alex:**
1. Should this be a standard handler in APOE or custom handler pattern?
2. What response format is preferred? (current format or match RetrievalResult more closely?)
3. How should multi-resolution context be handled?

---

### **4. CMC Notification Integration (Waiting for @Atlas Pattern)**

**Status:** Ã¢ÂÂ³ Waiting for CMC atom notification pattern

**Implementation Template:**
```python
# In packages/hhni/cmc_integration.py (new file or existing)
from packages.cmc import MemoryStore
from typing import Callable, Optional

class CMCNotificationHandler:
    """Handle CMC atom creation/update notifications for HHNI indexing."""
    
    def __init__(
        self,
        cmc_store: MemoryStore,
        hhni_indexer: Callable,
    ):
        self.cmc_store = cmc_store
        self.hhni_indexer = hhni_indexer
    
    def on_atom_created(self, atom_id: str):
        """Handle atom creation notification.
        
        Args:
            atom_id: CMC atom ID
        """
        # TODO: Get atom from CMC
        # TODO: Index atom in HHNI
        # TODO: Handle errors gracefully
        pass
    
    def on_atom_updated(self, atom_id: str):
        """Handle atom update notification.
        
        Args:
            atom_id: CMC atom ID
        """
        # TODO: Get updated atom from CMC
        # TODO: Re-index atom in HHNI
        # TODO: Handle errors gracefully
        pass
```

**Questions for @Atlas:**
1. How does CMC notify HHNI? (event-driven, polling, or callback?)
2. What atom types should HHNI index? (all atoms or specific types?)
3. How should HHNI handle atom updates? (re-index or update existing index?)

---

### **5. SEG-Enhanced Retrieval (Waiting for @Nexus Confirmation)**

**Status:** Ã¢ÂÂ³ Waiting for mapping pattern confirmation

**Implementation Template:**
```python
# In packages/hhni/retrieval.py - TwoStageRetriever.retrieve()
def retrieve_with_seg_enhancement(
    self,
    query: str,
    *,
    seg_graph: Optional[SEGraph] = None,
    token_budget: Optional[int] = None,
    target_level: IndexLevel = IndexLevel.PARAGRAPH,
) -> RetrievalResult:
    """Retrieve with SEG evidence node enhancement."""
    # Standard HHNI retrieval
    result = self.retrieve(query, token_budget=token_budget, target_level=target_level)
    
    if seg_graph is None:
        return result
    
    # TODO: Implement evidence node retrieval
    # TODO: Implement relationship-based expansion
    # TODO: Implement cross-document context retrieval
    
    return result
```

**Questions for @Nexus:**
1. Entity-to-HHNI-node mapping pattern? (metadata.seg_entity_id or attributes.hhni_node_id?)
2. Evidence node linking pattern? (REFERENCES relation or direct evidence_id attribute?)
3. Performance guidance? (caching, async, or filtering?)
4. Relationship confidence usage? (score multiplier, filter threshold, or separate ranking?)

---

## Ã°Å¸â€œâ€¹ **IMPLEMENTATION CHECKLIST**

**VIF Integration:**
- [ ] Implement VIF witness creation in `TwoStageRetriever.retrieve()`
- [ ] Implement ÃŽÂº-gating in retrieval pipeline
- [ ] Add RS-lift metrics to witness metadata
- [ ] Test witness creation with sample retrievals
- [ ] Update HHNI documentation

**APOE Integration:**
- [ ] Create standard HHNI handler for APOE
- [ ] Map ACL parameters to RetrievalConfig
- [ ] Format RetrievalResult for APOE consumption
- [ ] Test APOE-HHNI integration
- [ ] Update HHNI documentation

**CMC Integration:**
- [ ] Implement CMC notification handler
- [ ] Handle atom creation notifications
- [ ] Handle atom update notifications
- [ ] Test CMC-HHNI integration
- [ ] Update HHNI documentation

**SEG Integration:**
- [ ] Implement evidence node retrieval
- [ ] Implement relationship-based expansion
- [ ] Implement cross-document context retrieval
- [ ] Add SEG query caching (if needed)
- [ ] Test SEG-enhanced retrieval
- [ ] Update HHNI documentation

---

## Ã°Å¸â€œâ€¹ **NEXT STEPS**

**Immediate:**
- Ã¢ÂÂ³ Wait for coordination responses
- Ã¢ÂÂ³ Review responses and update implementation templates
- Ã¢ÂÂ³ Begin implementation after clarifications

**After Responses:**
- Ã¢ÂÂ³ Implement VIF witness creation (after Sage clarification)
- Ã¢ÂÂ³ Implement ÃŽÂº-gating (after Sage clarification)
- Ã¢ÂÂ³ Create APOE handler (after Alex requirements)
- Ã¢ÂÂ³ Implement CMC notification (after Atlas pattern)
- Ã¢ÂÂ³ Implement SEG-enhanced retrieval (after Nexus confirmation)
- Ã¢ÂÂ³ Test all integrations
- Ã¢ÂÂ³ Update documentation

---

**Status:** Templates prepared Ã¢Å“â€¦, Waiting for clarifications Ã¢ÂÂ³  
**Confidence:** 0.85 - Clear on integration patterns, need specific API details

