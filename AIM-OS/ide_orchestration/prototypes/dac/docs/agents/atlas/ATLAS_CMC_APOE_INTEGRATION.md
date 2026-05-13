# Atlas - CMC APOE Execution State Storage Integration Guide

**Purpose:** Complete guide for APOE execution state storage in CMC  
**Author:** Atlas (CMC System Specialist)  
**Date:** 2025-01-27  
**Status:** Ready for Integration  
**For:** @Alex (APOE System Specialist)

---

## 📋 **EXECUTIVE SUMMARY**

CMC provides bitemporal storage for APOE execution plans and state. APOE execution state is stored as CMC atoms with:
- **Modality:** `"apoe_plan"` or `"plan_execution"` (current implementation)
- **Tags:** `apoe`, `plan`, `plan_name`, `status`
- **Metadata:** Complete execution state structure
- **Bitemporal Support:** Via metadata (native support planned)

**Current Implementation:** ⏳ Partial (placeholder in `cmc_integration.py`)  
**Storage Path:** CMC atoms with APOE-specific tags  
**Integration Status:** Framework ready, needs implementation

---

## 🔧 **CURRENT IMPLEMENTATION**

### **APOE CMC Integration:**

**File:** `packages/apoe/cmc_integration.py`

**Current Status:**
- ✅ `CMCPlanStore` class exists
- ✅ `PlanMemory` dataclass defined
- ⏳ `_store_to_cmc()` method is placeholder (commented out)
- ✅ Methods for storing plan start, progress, completion

**Code Reference:**
```python
# From packages/apoe/cmc_integration.py:165-177
def _store_to_cmc(self, memory: PlanMemory):
    """Store plan memory to CMC (internal helper)."""
    if not self.cmc:
        return
    
    # In production:
    # atom_id = self.cmc.create_atom(
    #     modality="plan_execution",
    #     content=json.dumps(asdict(memory)),
    #     tags=["apoe", "plan", memory.plan_name, memory.status],
    #     metadata=memory.metadata
    # )
    pass
```

---

## 📊 **APOE EXECUTION STATE ATOM STRUCTURE**

### **Recommended Atom Schema:**

```python
from cmc_service.models import AtomCreate, AtomContent, WitnessStub
from dataclasses import asdict
import json

def store_apoe_execution_state(
    cmc_store: MemoryStore,
    plan_memory: PlanMemory,
    execution_plan: Optional[ExecutionPlan] = None,
    context_snapshot_id: Optional[str] = None,
) -> str:
    """Store APOE execution state in CMC as atom"""
    
    # Create atom payload
    atom_payload = AtomCreate(
        modality="apoe_plan",  # Recommended modality
        content=AtomContent(
            inline=json.dumps(asdict(plan_memory)),
            media_type="application/json"
        ),
        tags={
            "apoe": 1.0,
            "plan": 1.0,
            "plan_name": 0.9,  # Plan name as tag
            "status": _get_status_weight(plan_memory.status),  # running/completed/failed
            "execution": 1.0,
        },
        metadata={
            # Plan Memory Fields
            "plan_name": plan_memory.plan_name,
            "execution_id": plan_memory.execution_id,
            "started_at": plan_memory.started_at.isoformat(),
            "completed_at": plan_memory.completed_at.isoformat() if plan_memory.completed_at else None,
            "status": plan_memory.status,
            "steps_completed": plan_memory.steps_completed,
            "total_steps": plan_memory.total_steps,
            "outputs": plan_memory.outputs,
            
            # Execution Plan (if provided)
            "execution_plan": execution_plan.to_dict() if execution_plan else None,
            
            # Additional Metadata
            **plan_memory.metadata,
        },
        witness=WitnessStub(
            model_id="apoe_executor",
            snapshot_id=context_snapshot_id,
            correlation_id=plan_memory.execution_id,
        )
    )
    
    # Store in CMC
    atom = cmc_store.create_atom(atom_payload)
    return atom.id
```

---

## 🔗 **INTEGRATION PATTERNS**

### **Pattern 1: Plan Execution Start**

```python
def store_plan_start_in_cmc(
    cmc_store: MemoryStore,
    plan_name: str,
    execution_id: str,
    total_steps: int,
    execution_plan: Optional[ExecutionPlan] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """Store plan execution start in CMC"""
    
    plan_memory = PlanMemory(
        plan_name=plan_name,
        execution_id=execution_id,
        started_at=datetime.now(timezone.utc),
        completed_at=None,
        status="running",
        steps_completed=0,
        total_steps=total_steps,
        outputs={},
        metadata=metadata or {}
    )
    
    return store_apoe_execution_state(
        cmc_store, plan_memory, execution_plan
    )
```

### **Pattern 2: Plan Execution Progress Update**

```python
def update_plan_progress_in_cmc(
    cmc_store: MemoryStore,
    execution_id: str,
    steps_completed: int,
    current_outputs: Dict[str, Any],
) -> str:
    """Update plan execution progress in CMC"""
    
    # Retrieve existing plan memory
    atoms = cmc_store.list_atoms(
        tag="apoe",
        limit=1000,
    )
    
    plan_atom = None
    for atom in atoms:
        if atom.metadata.get("execution_id") == execution_id:
            plan_atom = atom
            break
    
    if not plan_atom:
        raise ValueError(f"Plan execution {execution_id} not found")
    
    # Update plan memory
    plan_memory = PlanMemory(
        plan_name=plan_atom.metadata["plan_name"],
        execution_id=execution_id,
        started_at=_parse_datetime(plan_atom.metadata["started_at"]),
        completed_at=None,
        status="running",
        steps_completed=steps_completed,
        total_steps=plan_atom.metadata["total_steps"],
        outputs=current_outputs,
        metadata=plan_atom.metadata,
    )
    
    # Store updated state (creates new atom with updated state)
    return store_apoe_execution_state(cmc_store, plan_memory)
```

### **Pattern 3: Plan Execution Completion**

```python
def store_plan_complete_in_cmc(
    cmc_store: MemoryStore,
    execution_id: str,
    final_outputs: Dict[str, Any],
    success: bool,
) -> str:
    """Store plan execution completion in CMC"""
    
    # Retrieve existing plan memory
    atoms = cmc_store.list_atoms(
        tag="apoe",
        limit=1000,
    )
    
    plan_atom = None
    for atom in atoms:
        if atom.metadata.get("execution_id") == execution_id:
            plan_atom = atom
            break
    
    if not plan_atom:
        raise ValueError(f"Plan execution {execution_id} not found")
    
    # Update plan memory
    plan_memory = PlanMemory(
        plan_name=plan_atom.metadata["plan_name"],
        execution_id=execution_id,
        started_at=_parse_datetime(plan_atom.metadata["started_at"]),
        completed_at=datetime.now(timezone.utc),
        status="completed" if success else "failed",
        steps_completed=plan_atom.metadata["total_steps"],
        total_steps=plan_atom.metadata["total_steps"],
        outputs=final_outputs,
        metadata=plan_atom.metadata,
    )
    
    # Store completed state
    return store_apoe_execution_state(cmc_store, plan_memory)
```

---

## 🔍 **QUERY PATTERNS**

### **Query Plan Execution History:**

```python
def get_plan_execution_history(
    cmc_store: MemoryStore,
    plan_name: str,
    limit: int = 10,
) -> List[Atom]:
    """Retrieve historical executions of a plan from CMC"""
    
    atoms = cmc_store.list_atoms(
        tag="apoe",
        limit=limit * 10,  # Get more to filter
    )
    
    # Filter by plan name
    plan_atoms = [
        atom for atom in atoms
        if atom.metadata.get("plan_name") == plan_name
    ]
    
    # Sort by most recent first
    plan_atoms.sort(
        key=lambda a: _parse_datetime(a.metadata.get("started_at", "")),
        reverse=True
    )
    
    return plan_atoms[:limit]
```

### **Query Plan Execution by Status:**

```python
def get_plan_executions_by_status(
    cmc_store: MemoryStore,
    status: str,  # "running", "completed", "failed"
    limit: int = 100,
) -> List[Atom]:
    """Retrieve plan executions by status"""
    
    atoms = cmc_store.list_atoms(
        tag="apoe",
        limit=limit,
    )
    
    return [
        atom for atom in atoms
        if atom.metadata.get("status") == status
    ]
```

### **Query Similar Plans (Semantic Search):**

```python
def get_similar_plans(
    cmc_store: MemoryStore,
    plan_name: str,
    min_similarity: float = 0.70,
) -> List[Atom]:
    """Retrieve similar plan executions using semantic search"""
    
    # Use HHNI for semantic search
    # This requires HHNI integration
    atoms = cmc_store.list_atoms(
        tag="apoe",
        limit=1000,
    )
    
    # Simple name matching (in production, use HHNI semantic search)
    similar = [
        atom for atom in atoms
        if plan_name.lower() in atom.metadata.get("plan_name", "").lower()
        or atom.metadata.get("plan_name", "").lower() in plan_name.lower()
    ]
    
    return similar
```

---

## 🗄️ **STORAGE RECOMMENDATIONS**

### **Atom Modality:**

**Current:** `"plan_execution"` (commented in code)  
**Recommended:** `"apoe_plan"` (for better filtering and organization)

### **Tags:**

**Required Tags:**
- `apoe: 1.0` - Primary tag for APOE plans
- `plan: 1.0` - Plan identifier
- `execution: 1.0` - Execution identifier

**Optional Tags:**
- `plan_name: {weight}` - Plan name weight (0.0-1.0)
- `status: {weight}` - Status weight (running/completed/failed)
- `{plan_name}: 1.0` - Plan name as tag (for filtering)

### **Metadata Structure:**

**Required Fields:**
- `plan_name` - Plan name
- `execution_id` - Unique execution identifier
- `started_at` - Execution start timestamp (ISO format)
- `status` - Execution status ("running", "completed", "failed")
- `steps_completed` - Number of steps completed
- `total_steps` - Total number of steps
- `outputs` - Execution outputs dictionary

**Optional Fields:**
- `completed_at` - Execution completion timestamp (ISO format, None if running)
- `execution_plan` - Complete execution plan structure (if available)
- `metadata` - Additional metadata dictionary
- `valid_from` - Valid time start (ISO format, when native support available)
- `valid_to` - Valid time end (ISO format, None if open-ended)

---

## 🔐 **BITEMPORAL SUPPORT**

### **Current Implementation:**

Bitemporal fields stored in metadata:
- `started_at` - Transaction time (when recorded)
- `completed_at` - Completion time (if completed)
- `valid_from` - Valid time start (planned)
- `valid_to` - Valid time end (planned)

### **Future Enhancement:**

When bitemporal native support is implemented (Enhancement #1):
- `valid_from` and `valid_to` will be native Atom fields
- Bitemporal queries will be faster (indexed)
- Time-travel queries will be native

**Migration Path:**
- Existing execution states will be migrated automatically
- Metadata fields will be moved to native fields
- No breaking changes to APOE API

---

## 🔗 **SEG INTEGRATION**

### **Execution State → SEG Derivation Node:**

APOE execution states can be linked to SEG derivation nodes:

```python
# Execution state stored in CMC
execution_atom = store_apoe_execution_state(cmc_store, plan_memory)

# Create SEG derivation node linked to execution state
derivation = DerivationNode(
    claim=f"Plan {plan_memory.plan_name} executed with status {plan_memory.status}",
    source="apoe_execution",
    atom_id=execution_atom.id,  # Link to CMC atom
    witness_id=execution_atom.witness.model_id,  # Link to VIF witness
    confidence=plan_memory.metadata.get("success_rate", 0.85),
)
```

**Field Mapping:**
- `plan_memory.execution_id` → `derivation.atom_id` (CMC atom ID)
- `plan_memory.status` → `derivation.claim` (execution result)
- `plan_memory.outputs` → `derivation.evidence` (execution outputs)
- `plan_memory.started_at` → `derivation.valid_from` (bitemporal)

---

## ✅ **INTEGRATION CHECKLIST**

For APOE execution state storage in CMC:

- [x] Atom schema documented
- [x] Storage patterns documented
- [x] Query patterns documented
- [x] Bitemporal support documented
- [x] SEG integration documented
- [x] Code references provided

**Status:** Integration Guide Complete ✅, Ready for APOE Implementation 🤝

---

## 📚 **CODE REFERENCES**

### **Implementation Files:**
- **APOE CMC Integration:** `packages/apoe/cmc_integration.py` (CMCPlanStore, PlanMemory)
- **CMC Models:** `packages/cmc_service/models.py` (Atom, AtomCreate, AtomContent)
- **CMC Storage:** `packages/cmc_service/memory_store.py` (create_atom)
- **APOE Models:** `packages/apoe/models.py` (ExecutionPlan, Step, etc.)

### **Documentation:**
- **APOE Architecture:** `knowledge_architecture/systems/apoe/T2_architecture.md`
- **APOE Detailed:** `knowledge_architecture/systems/apoe/T3_detailed.md`
- **CMC Schema:** `agents/atlas/ATLAS_CMC_ATOM_SCHEMA.md`

---

**Next Steps:**
1. Alex reviews integration guide
2. Alex confirms execution state structure compatibility
3. Implement `_store_to_cmc()` method (currently placeholder)
4. Test integration end-to-end

---

*Created by Atlas (CMC System Specialist)*  
*For Alex (APOE System Specialist)*  
*Date: 2025-01-27*

