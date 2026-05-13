# Atlas - CMC VIF Witness Auto-Generation Enhancement Plan

**Agent:** Atlas (CMC System Specialist)  
**Date:** 2025-01-27  
**Status:** Planning  
**Enhancement:** High Priority #3 - VIF Witness Auto-Generation  
**Estimated Effort:** 2-3 days

---

## 📋 **EXECUTIVE SUMMARY**

**Current State:** Witnesses created manually, not automatically  
**Target State:** Auto-generate VIF witnesses for all atom creation operations  
**Impact:** Complete provenance tracking without manual intervention  
**Priority:** High

---

## 🔍 **CURRENT STATE ANALYSIS**

### **What Exists:**

1. **VIF Integration:**
   - `WitnessStub` field in every atom (minimal witness)
   - `VIFStore` class for storing full witnesses
   - `create_witness_and_store()` convenience function
   - **Location:** `packages/vif/cmc_integration.py`

2. **Atom Creation:**
   - `create_atom()` creates atoms with empty `WitnessStub()`
   - No automatic witness generation
   - **Location:** `packages/cmc_service/memory_store.py:155`

3. **MCP Tool:**
   - `store_memory` tool accepts witness parameters
   - Stores witness info in metadata
   - **Location:** `lucid_mcp_server.py:1895-2083`

### **What's Missing:**

1. **Automatic Witness Generation:**
   - No auto-generation on atom creation
   - Witnesses must be created manually
   - No context capture for witness creation

2. **Witness Enrichment:**
   - Empty `WitnessStub()` doesn't capture operation context
   - No automatic model ID detection
   - No automatic confidence calculation

---

## 🎯 **ENHANCEMENT DESIGN**

### **Step 1: Add Auto-Witness Generation to MemoryStore**

**File:** `packages/cmc_service/memory_store.py`

**New Method:**
```python
def _generate_witness_stub(
    self,
    operation: str = "atom_create",
    correlation_id: Optional[str] = None,
    context_snapshot_id: Optional[str] = None,
) -> WitnessStub:
    """Auto-generate witness stub for atom creation"""
    import os
    
    # Detect model ID from environment or context
    model_id = os.environ.get("LLM_MODEL_ID", "unknown")
    
    # Detect tool IDs from call stack or context
    tool_ids = self._detect_tool_ids()
    
    # Get current snapshot ID if available
    if context_snapshot_id is None:
        # Use latest snapshot if available
        if self._snapshots:
            latest_snapshot = max(self._snapshots.values(), key=lambda s: s.created_at)
            context_snapshot_id = latest_snapshot.id
    
    return WitnessStub(
        model_id=model_id,
        tool_ids=tool_ids,
        snapshot_id=context_snapshot_id,
        correlation_id=correlation_id,
        uncertainty_band="green",  # Default, can be enhanced
    )
```

### **Step 2: Update create_atom() Method**

**File:** `packages/cmc_service/memory_store.py`

**Changes:**
```python
def create_atom(
    self,
    payload: AtomCreate,
    *,
    correlation_id: Optional[str] = None,
    auto_generate_witness: bool = True,  # NEW: Default True
    context_snapshot_id: Optional[str] = None,  # NEW
) -> Atom:
    """Create atom with optional auto-witness generation"""
    
    # ... existing atom creation code ...
    
    # Auto-generate witness if enabled
    witness = WitnessStub()
    if auto_generate_witness:
        witness = self._generate_witness_stub(
            operation="atom_create",
            correlation_id=correlation_id,
            context_snapshot_id=context_snapshot_id,
        )
    
    atom = Atom(
        ...,
        witness=witness,
    )
    
    return atom
```

### **Step 3: Enhanced Witness Generation (Optional)**

**File:** `packages/cmc_service/memory_store.py`

**Enhanced Method:**
```python
def _generate_full_witness(
    self,
    atom: Atom,
    operation: str = "atom_create",
    correlation_id: Optional[str] = None,
    context_snapshot_id: Optional[str] = None,
    confidence: Optional[float] = None,
) -> Optional[VIF]:
    """Generate full VIF witness for atom (optional, requires VIF package)"""
    try:
        from vif.witness import VIF
        from vif.confidence_bands import determine_band
        
        # Create full VIF witness
        vif = VIF(
            model_id=os.environ.get("LLM_MODEL_ID", "unknown"),
            context_snapshot_id=context_snapshot_id or self._get_latest_snapshot_id(),
            prompt_hash=VIF.hash_text(str(atom.content)),
            confidence_score=confidence or 0.85,  # Default confidence
            confidence_band=determine_band(confidence or 0.85),
            output_hash=VIF.hash_text(atom.id),
            tool_ids=self._detect_tool_ids(),
        )
        
        # Store full witness in CMC
        from vif.cmc_integration import VIFStore
        store = VIFStore(self)
        witness_atom_id = store.store_witness(vif)
        
        # Link witness to atom
        atom.metadata["vif_witness_atom_id"] = witness_atom_id
        
        return vif
    except ImportError:
        # VIF package not available, return None
        return None
```

### **Step 4: Configuration**

**File:** `packages/cmc_service/memory_store.py`

**Add to __init__:**
```python
def __init__(
    self,
    base_path: Union[str, Path],
    *,
    auto_generate_witness: bool = True,  # NEW
    auto_generate_full_witness: bool = False,  # NEW (optional, requires VIF)
):
    ...
    self.auto_generate_witness = auto_generate_witness
    self.auto_generate_full_witness = auto_generate_full_witness
```

---

## 📊 **IMPACT ANALYSIS**

### **Benefits:**
- ✅ Complete provenance tracking automatically
- ✅ No manual witness creation needed
- ✅ Better audit trails
- ✅ Consistent witness generation

### **Risks:**
- ⚠️ Performance impact (witness generation overhead)
- ⚠️ VIF package dependency (optional, graceful degradation)
- ⚠️ Configuration complexity

---

## 🧪 **TESTING STRATEGY**

### **Unit Tests:**
1. Auto-witness generation
2. Witness stub creation
3. Full witness generation (if VIF available)
4. Graceful degradation when VIF unavailable

### **Integration Tests:**
1. End-to-end witness generation workflow
2. VIF integration
3. Witness retrieval
4. Performance testing

---

## 📝 **IMPLEMENTATION CHECKLIST**

- [ ] Add `_generate_witness_stub()` method
- [ ] Add `_generate_full_witness()` method (optional)
- [ ] Update `create_atom()` signature
- [ ] Add configuration options
- [ ] Add tool ID detection
- [ ] Add model ID detection
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Update documentation

---

## 🚀 **ESTIMATED TIMELINE**

**Day 1:**
- Witness stub generation (2-3 hours)
- Update create_atom() (1-2 hours)
- Tool/model ID detection (1-2 hours)

**Day 2:**
- Full witness generation (optional, 2-3 hours)
- Configuration options (1-2 hours)
- Testing (2-3 hours)

**Day 3:**
- Integration testing (2-3 hours)
- Documentation (2-3 hours)
- Validation and cleanup (1-2 hours)

**Total:** 2-3 days (14-22 hours)

---

**Status:** Planning Complete ✅  
**Next:** Begin implementation when approved  
**Confidence:** High (0.85) - clear design, low risk

---

*Created by Atlas (CMC System Specialist)*  
*Date: 2025-01-27*  
*Version: 1.0*

