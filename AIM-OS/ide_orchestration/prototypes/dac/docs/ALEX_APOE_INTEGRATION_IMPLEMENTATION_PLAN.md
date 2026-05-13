# APOE Integration Implementation Plan

**Created By:** Alex (APOE System Specialist)  
**Date:** 2025-01-27  
**Status:** Planning  
**Purpose:** Implementation plan for integrating VIF and HHNI coordination responses into APOE

---

## 📋 **EXECUTIVE SUMMARY**

**Integration Scope:**
- ✅ VIF Witness Generation (from @Sage)
- ✅ VIF κ-Gating (from @Sage)
- ✅ HHNI Context Retrieval for Retriever Role (from @Sev)

**Status:** Planning phase - ready for implementation  
**Priority:** HIGH - Core integration patterns  
**Confidence:** High (0.90) - Clear guidance from specialists

---

## 🔗 **VIF INTEGRATION (from @Sage)**

### **1. Witness Generation Enhancement**

**Current State:**
- `packages/apoe/vif_integration.py` creates dictionary-based witnesses
- Witnesses are not stored in CMC automatically
- Witness structure doesn't match full VIF schema

**Target State:**
- Use full VIF Pydantic schema (`packages/vif/witness.py`)
- Automatic CMC storage via `create_witness_and_store()`
- Complete provenance tracking (hashes, tokens, confidence bands)

**Implementation Steps:**

**Step 1: Update Witness Creation Functions**
```python
# packages/apoe/vif_integration.py

from packages.vif import VIF, ConfidenceBand, TaskCriticality, determine_band
from packages.vif.cmc_integration import create_witness_and_store
from packages.cmc import get_memory_store
import hashlib

def create_step_witness_vif(
    step: Step,
    plan_name: str,
    context_snapshot_id: str,
    confidence: Optional[float] = None
) -> VIF:
    """Create full VIF witness for step execution."""
    
    # Extract confidence
    if confidence is None and step.outputs:
        confidence = step.outputs.get("confidence", 0.95)
    elif confidence is None:
        confidence = 0.95
    
    # Hash prompt and output
    prompt_text = step.description or ""
    output_text = str(step.outputs or {})
    
    prompt_hash = hashlib.sha256(prompt_text.encode()).hexdigest()
    output_hash = hashlib.sha256(output_text.encode()).hexdigest()
    
    # Estimate tokens (simple word count for now)
    prompt_tokens = len(prompt_text.split())
    output_tokens = len(output_text.split())
    
    # Determine task criticality from role
    task_criticality = map_role_to_criticality(step.role)
    
    # Create VIF witness
    vif = VIF(
        model_id=step.role.value,  # "planner", "reasoner", etc.
        model_provider="apoe",
        context_snapshot_id=context_snapshot_id,
        prompt_hash=prompt_hash,
        prompt_tokens=prompt_tokens,
        confidence_score=confidence,
        confidence_band=determine_band(confidence),
        output_hash=output_hash,
        output_tokens=output_tokens,
        total_tokens=prompt_tokens + output_tokens,
        task_criticality=task_criticality,
        kappa_threshold=get_kappa_threshold_for_role(step.role),
        kappa_gate_passed=(confidence >= get_kappa_threshold_for_role(step.role)),
        execution_time_ms=step.duration() * 1000 if step.duration() else None,
    )
    
    return vif


def create_plan_witness_vif(
    plan: ExecutionPlan,
    result: ExecutionResult,
    context_snapshot_id: str,
    confidence: float = 0.95
) -> VIF:
    """Create full VIF witness for plan execution."""
    
    # Hash plan inputs and outputs
    plan_inputs = {
        "plan_name": plan.name,
        "total_steps": result.total_steps,
        "roles": list(plan.roles.keys())
    }
    plan_outputs = {
        "completed_steps": result.completed_steps,
        "failed_steps": result.failed_steps,
        "success": result.success,
        "duration_seconds": result.total_duration_seconds
    }
    
    prompt_text = str(plan_inputs)
    output_text = str(plan_outputs)
    
    prompt_hash = hashlib.sha256(prompt_text.encode()).hexdigest()
    output_hash = hashlib.sha256(output_text.encode()).hexdigest()
    
    prompt_tokens = len(prompt_text.split())
    output_tokens = len(output_text.split())
    
    # Plan execution is ROUTINE by default
    task_criticality = TaskCriticality.ROUTINE
    
    vif = VIF(
        model_id="apoe-executor-v1",
        model_provider="aether",
        context_snapshot_id=context_snapshot_id,
        prompt_hash=prompt_hash,
        prompt_tokens=prompt_tokens,
        confidence_score=confidence,
        confidence_band=determine_band(confidence),
        output_hash=output_hash,
        output_tokens=output_tokens,
        total_tokens=prompt_tokens + output_tokens,
        task_criticality=task_criticality,
        kappa_threshold=0.70,  # ROUTINE threshold
        kappa_gate_passed=(confidence >= 0.70),
        execution_time_ms=result.total_duration_seconds * 1000 if result.total_duration_seconds else None,
    )
    
    return vif


def map_role_to_criticality(role: RoleType) -> TaskCriticality:
    """Map APOE role to task criticality level."""
    role_criticality_map = {
        RoleType.PLANNER: TaskCriticality.IMPORTANT,      # κ=0.85
        RoleType.RETRIEVER: TaskCriticality.ROUTINE,        # κ=0.70
        RoleType.REASONER: TaskCriticality.IMPORTANT,       # κ=0.85
        RoleType.VERIFIER: TaskCriticality.CRITICAL,        # κ=0.95
        RoleType.BUILDER: TaskCriticality.ROUTINE,           # κ=0.70
        RoleType.CRITIC: TaskCriticality.IMPORTANT,          # κ=0.85
        RoleType.OPERATOR: TaskCriticality.ROUTINE,         # κ=0.70
        RoleType.WITNESS: TaskCriticality.CRITICAL,         # κ=0.95
    }
    return role_criticality_map.get(role, TaskCriticality.ROUTINE)


def get_kappa_threshold_for_role(role: RoleType) -> float:
    """Get κ threshold for APOE role."""
    from packages.vif.kappa_gate import DEFAULT_KAPPA_THRESHOLDS, TaskCriticality
    
    criticality = map_role_to_criticality(role)
    return DEFAULT_KAPPA_THRESHOLDS[criticality]
```

**Step 2: Integrate CMC Storage**
```python
def store_witness_in_cmc(
    vif: VIF,
    operation_name: str,
    prompt: str,
    output: str
) -> tuple[VIF, str]:
    """Store VIF witness in CMC automatically."""
    from packages.vif.cmc_integration import create_witness_and_store
    from packages.cmc import get_memory_store
    
    cmc_store = get_memory_store()
    
    vif, atom_id = create_witness_and_store(
        cmc_store,
        operation_name=operation_name,
        prompt=prompt,
        output=output,
        confidence=vif.confidence_score,
        context_snapshot_id=vif.context_snapshot_id,
        model_id=vif.model_id,
        model_provider=vif.model_provider
    )
    
    return vif, atom_id
```

**Step 3: Update Executor to Use VIF Witnesses**
```python
# packages/apoe/executor.py

def _execute_step(self, step: Step, plan: ExecutionPlan) -> str:
    # ... existing execution logic ...
    
    # Create context snapshot before execution
    from packages.cmc import get_memory_store
    cmc_store = get_memory_store()
    context_snapshot_id = cmc_store.create_snapshot()
    
    # Execute step
    outputs = self._run_step(step, plan)
    
    # Create VIF witness
    from packages.apoe.vif_integration import create_step_witness_vif, store_witness_in_cmc
    
    vif = create_step_witness_vif(
        step=step,
        plan_name=plan.name,
        context_snapshot_id=context_snapshot_id,
        confidence=outputs.get("confidence", 0.95)
    )
    
    # Store in CMC
    vif, atom_id = store_witness_in_cmc(
        vif=vif,
        operation_name=f"execute_step:{plan.name}.{step.name}",
        prompt=step.description or "",
        output=str(outputs)
    )
    
    # Store witness ID in step metadata
    step.metadata = step.metadata or {}
    step.metadata["vif_witness_id"] = vif.id
    step.metadata["vif_atom_id"] = atom_id
    
    return "completed"
```

---

### **2. κ-Gating Integration**

**Current State:**
- No κ-gating in executor
- Confidence checks are manual
- No task criticality mapping

**Target State:**
- κ-gating before step execution
- Task criticality-based thresholds
- Automatic abstention for low confidence

**Implementation Steps:**

**Step 1: Add κ-Gate to Executor**
```python
# packages/apoe/executor.py

from packages.vif import KappaGate, TaskCriticality
from packages.apoe.vif_integration import map_role_to_criticality

class PlanExecutor:
    def __init__(self):
        # ... existing init ...
        self.kappa_gate = KappaGate()  # Initialize once per executor
    
    def _execute_step(self, step: Step, plan: ExecutionPlan) -> str:
        # ... existing setup ...
        
        # κ-Gate check before execution
        if hasattr(step, 'min_confidence') and step.min_confidence:
            # Use custom threshold if provided
            custom_threshold = step.min_confidence
        else:
            # Use role-based threshold
            custom_threshold = None
        
        # Get task criticality from role
        task_criticality = map_role_to_criticality(step.role)
        
        # Predict confidence (from role handler or default)
        predicted_confidence = self._predict_step_confidence(step, plan)
        
        # Check κ-gate
        gate_result = self.kappa_gate.check(
            confidence=predicted_confidence,
            task_criticality=task_criticality,
            custom_threshold=custom_threshold
        )
        
        if not gate_result.passed:
            # κ-gate failed - abstain
            step.status = StepStatus.ABSTAINED
            step.error = gate_result.escalation_reason
            
            if gate_result.should_escalate:
                # Escalate to human review
                self._escalate_to_human(step, gate_result)
            
            return "abstained"
        
        # If passed, proceed with execution
        # ... rest of execution logic ...
    
    def _predict_step_confidence(self, step: Step, plan: ExecutionPlan) -> float:
        """Predict confidence for step execution."""
        # Use historical confidence if available
        if step.metadata and "historical_confidence" in step.metadata:
            return step.metadata["historical_confidence"]
        
        # Use role default confidence
        role_defaults = {
            RoleType.VERIFIER: 0.95,
            RoleType.WITNESS: 0.95,
            RoleType.PLANNER: 0.85,
            RoleType.REASONER: 0.85,
            RoleType.CRITIC: 0.85,
            RoleType.RETRIEVER: 0.70,
            RoleType.BUILDER: 0.70,
            RoleType.OPERATOR: 0.70,
        }
        return role_defaults.get(step.role, 0.70)
    
    def _escalate_to_human(self, step: Step, gate_result: KappaGateResult):
        """Escalate step to human review."""
        from packages.apoe.hitl_escalation import HITLManager
        
        hitl_manager = HITLManager()
        hitl_manager.create_escalation(
            step_id=step.id,
            reason=gate_result.escalation_reason,
            priority="high" if gate_result.task_criticality in [TaskCriticality.CRITICAL, TaskCriticality.IMPORTANT] else "medium",
            context={
                "confidence": gate_result.confidence,
                "threshold": gate_result.threshold,
                "gap": gate_result.gap,
                "task_criticality": gate_result.task_criticality.value
            }
        )
```

**Step 2: Add Functional Style κ-Gating (Optional)**
```python
# For functional-style gate wrapping

from packages.vif import KappaGate, TaskCriticality

gate = KappaGate()

def execute_step_logic(step: Step, plan: ExecutionPlan) -> dict:
    """Step execution logic."""
    # ... execution ...
    return outputs

def safe_fallback(gate_result: KappaGateResult) -> dict:
    """Fallback when confidence too low."""
    return {
        "status": "abstained",
        "reason": gate_result.escalation_reason,
        "confidence": gate_result.confidence,
        "threshold": gate_result.threshold
    }

# Use gate_operation for functional style
output, gate_result = gate.gate_operation(
    execute_step_logic,
    confidence=predicted_confidence,
    task_criticality=TaskCriticality.ROUTINE,
    on_fail=safe_fallback
)
```

---

## 🔗 **HHNI INTEGRATION (from @Sev)**

### **1. Retriever Role Enhancement**

**Current State:**
- Retriever role exists but may not use HHNI
- No budget-aware queries
- No multi-resolution context support

**Target State:**
- Retriever role uses HHNI for context retrieval
- Budget-aware queries (respects APOE token budgets)
- Multi-resolution context support

**Implementation Steps:**

**Step 1: Update Retriever Role to Use HHNI**
```python
# packages/apoe/role_dispatcher.py

from packages.hhni.retrieval import TwoStageRetriever
from packages.hhni.indexer import HierarchicalIndexer

class RetrieverRole:
    """Retriever role using HHNI for context retrieval."""
    
    def __init__(self):
        self.hhni_retriever = TwoStageRetriever()
        self.hhni_indexer = HierarchicalIndexer()
    
    def execute(
        self,
        inputs: Dict[str, Any],
        budget: Budget
    ) -> Dict[str, Any]:
        """Execute retrieval with HHNI."""
        
        # Extract query
        query = inputs.get("query", "")
        if not query:
            return {
                "context": [],
                "total_tokens": 0,
                "error": "No query provided"
            }
        
        # Extract budget constraints
        token_budget = budget.tokens_limit if budget else 2000  # Default 2k tokens
        time_budget = budget.time_limit_seconds if budget else 30  # Default 30s
        
        # Extract query constraints
        modality = inputs.get("modality", "code")  # "code", "docs", "data", etc.
        k = inputs.get("k", 100)  # Number of results
        enable_dvns = inputs.get("enable_dvns", True)  # Enable DVNS physics
        
        # Query HHNI with budget constraints
        try:
            result = self.hhni_retriever.retrieve(
                query=query,
                k=k,
                modality=modality,
                enable_dvns=enable_dvns,
                token_budget=token_budget,
                time_budget=time_budget
            )
            
            return {
                "context": result.items,  # Retrieved context items
                "total_tokens": result.total_tokens,
                "relevance_scores": result.scores,
                "retrieval_witness": result.witness,  # For VIF provenance
                "modality": modality,
                "k": k,
                "dvns_enabled": enable_dvns
            }
        except Exception as e:
            return {
                "context": [],
                "total_tokens": 0,
                "error": str(e)
            }
```

**Step 2: Add Multi-Resolution Context Support**
```python
# packages/apoe/role_dispatcher.py

def execute_multi_resolution(
    self,
    inputs: Dict[str, Any],
    budget: Budget
) -> Dict[str, Any]:
    """Execute retrieval with multi-resolution context."""
    
    query = inputs.get("query", "")
    resolution_levels = inputs.get("resolution_levels", ["system", "section", "paragraph"])
    token_budget = budget.tokens_limit if budget else 2000
    
    # Query HHNI at multiple resolutions
    results = {}
    for level in resolution_levels:
        result = self.hhni_retriever.retrieve(
            query=query,
            k=50,  # Fewer results per level
            modality=inputs.get("modality", "code"),
            resolution=level,  # System → Section → Paragraph → Sentence
            token_budget=token_budget // len(resolution_levels),  # Split budget
            enable_dvns=True
        )
        results[level] = {
            "items": result.items,
            "tokens": result.total_tokens,
            "scores": result.scores
        }
    
    return {
        "multi_resolution": results,
        "total_tokens": sum(r["tokens"] for r in results.values()),
        "resolution_levels": resolution_levels
    }
```

**Step 3: Integrate with Role Dispatcher**
```python
# packages/apoe/role_dispatcher.py

class RoleDispatcher:
    def __init__(self):
        # ... existing init ...
        self.retriever_role = RetrieverRole()
    
    def dispatch_retriever(
        self,
        step: Step,
        inputs: Dict[str, Any],
        budget: Budget
    ) -> Dict[str, Any]:
        """Dispatch to Retriever role with HHNI."""
        
        # Add budget to inputs
        inputs["budget"] = budget
        
        # Execute retrieval
        result = self.retriever_role.execute(inputs, budget)
        
        # Create retrieval witness for VIF
        if "retrieval_witness" in result:
            # Store witness in step metadata
            step.metadata = step.metadata or {}
            step.metadata["hhni_retrieval_witness"] = result["retrieval_witness"]
        
        return result
```

---

## 📋 **TESTING PLAN**

### **VIF Integration Tests:**
1. ✅ Test witness creation with full VIF schema
2. ✅ Test CMC storage of witnesses
3. ✅ Test κ-gating with different confidence levels
4. ✅ Test role-to-criticality mapping
5. ✅ Test abstention flow
6. ✅ Test human escalation

### **HHNI Integration Tests:**
1. ✅ Test Retriever role with HHNI
2. ✅ Test budget-aware queries
3. ✅ Test multi-resolution context retrieval
4. ✅ Test retrieval witness generation
5. ✅ Test error handling

---

## 📊 **IMPLEMENTATION PRIORITY**

**Phase 1: VIF Witness Generation (HIGH)**
- Update witness creation functions
- Integrate CMC storage
- Update executor to use VIF witnesses
- **Estimated Time:** 2-3 hours

**Phase 2: κ-Gating (HIGH)**
- Add κ-gate to executor
- Implement role-to-criticality mapping
- Add abstention flow
- **Estimated Time:** 2-3 hours

**Phase 3: HHNI Retriever Integration (MEDIUM)**
- Update Retriever role to use HHNI
- Add budget-aware queries
- Add multi-resolution support
- **Estimated Time:** 2-3 hours

**Total Estimated Time:** 6-9 hours

---

## 📋 **NEXT STEPS**

1. ⏳ Review implementation plan with @Sage and @Sev
2. ⏳ Create test cases for integration
3. ⏳ Implement Phase 1 (VIF Witness Generation)
4. ⏳ Implement Phase 2 (κ-Gating)
5. ⏳ Implement Phase 3 (HHNI Retriever Integration)
6. ⏳ Test all integrations
7. ⏳ Update documentation

---

**Status:** Implementation Plan Complete ✅  
**Next:** Review with specialists, begin implementation  
**Confidence:** High (0.90) - Clear guidance, well-defined steps

