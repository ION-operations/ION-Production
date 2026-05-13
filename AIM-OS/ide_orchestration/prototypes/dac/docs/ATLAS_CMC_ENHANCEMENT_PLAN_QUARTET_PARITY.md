# Atlas - CMC SDF-CVF Quartet Parity Tracking Enhancement Plan

**Agent:** Atlas (CMC System Specialist)  
**Date:** 2025-01-27  
**Status:** Planning  
**Enhancement:** High Priority #2 - SDF-CVF Quartet Parity Tracking  
**Estimated Effort:** 3-4 days

---

## 📋 **EXECUTIVE SUMMARY**

**Current State:** Quartet parity calculated by SDF-CVF but not stored in CMC atoms  
**Target State:** Quartet parity metadata stored in atoms (P score, change ID, quartet completeness)  
**Impact:** Enables SDF-CVF validation of CMC changes, tracks quartet alignment  
**Priority:** High

---

## 🔍 **CURRENT STATE ANALYSIS**

### **What Exists:**

1. **SDF-CVF Quartet Parity System:**
   - Parity calculator exists (`packages/sdfcvf/parity.py`)
   - Formula: P = average of 6 pairwise semantic similarities
   - Threshold: P ≥ 0.90 required
   - **Status:** 60% implemented ✅
   - **Location:** `knowledge_architecture/systems/sdfcvf/components/parity/README.md`

2. **Cross-Tagging Protocol:**
   - Change ID format: `cmc-change-YYYYMMDD-HHMMSS`
   - Tag format defined for code/docs/tests/traces
   - **Location:** `knowledge_architecture/systems/cmc/T2_architecture.md`

3. **Gate Enforcement:**
   - Pre-commit, CI, and deployment gates documented
   - Quarantine system for P < 0.90
   - **Location:** `knowledge_architecture/AETHER_MEMORY/investigations/BATCH_1_CMC_VALIDATION.md`

### **What's Missing:**

1. **Atom Model:**
   - No quartet parity metadata fields in `Atom` class
   - No change ID tracking
   - No quartet completeness flags
   - **Location:** `models.py:105-141`

2. **Repository Storage:**
   - `atoms` table doesn't have quartet parity columns
   - No indexes on quartet parity fields
   - **Location:** `repository.py:38-50`

3. **API Integration:**
   - `create_atom()` doesn't accept quartet parity parameters
   - No automatic quartet parity calculation on atom creation
   - No quartet parity query methods

---

## 🎯 **ENHANCEMENT DESIGN**

### **Step 1: Add Quartet Parity Metadata Model**

**File:** `packages/cmc_service/models.py`

**New Dataclass:**
```python
@dataclass
class QuartetParityMetadata:
    """SDF-CVF quartet parity metadata for atoms"""
    change_id: Optional[str] = None  # cmc-change-YYYYMMDD-HHMMSS
    parity_score: Optional[float] = None  # P score (0.0-1.0)
    quartet_complete: bool = False  # All 4 elements present?
    code_present: bool = False
    docs_present: bool = False
    tests_present: bool = False
    traces_present: bool = False
    calculated_at: Optional[datetime] = None
    validated: bool = False  # P >= 0.90?
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "change_id": self.change_id,
            "parity_score": self.parity_score,
            "quartet_complete": self.quartet_complete,
            "code_present": self.code_present,
            "docs_present": self.docs_present,
            "tests_present": self.tests_present,
            "traces_present": self.traces_present,
            "calculated_at": self.calculated_at.isoformat() if self.calculated_at else None,
            "validated": self.validated,
        }
```

### **Step 2: Update Atom Model**

**File:** `packages/cmc_service/models.py`

**Changes:**
```python
@dataclass
class Atom(AtomCreate):
    id: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    hash: str = ""
    witness: WitnessStub = field(default_factory=WitnessStub)
    snapshot_ids: List[str] = field(default_factory=list)
    
    # NEW: Quartet parity metadata
    quartet_parity: Optional[QuartetParityMetadata] = None
```

### **Step 3: Update Repository Schema**

**File:** `packages/cmc_service/repository.py`

**Changes:**
```python
CREATE TABLE IF NOT EXISTS atoms (
    ...
    quartet_change_id TEXT,           # NEW
    quartet_parity_score REAL,        # NEW
    quartet_complete INTEGER,         # NEW (boolean)
    quartet_code_present INTEGER,     # NEW (boolean)
    quartet_docs_present INTEGER,     # NEW (boolean)
    quartet_tests_present INTEGER,    # NEW (boolean)
    quartet_traces_present INTEGER,  # NEW (boolean)
    quartet_calculated_at TEXT,      # NEW
    quartet_validated INTEGER,       # NEW (boolean)
    ...
)

CREATE INDEX IF NOT EXISTS idx_atoms_quartet_change_id ON atoms(quartet_change_id)
CREATE INDEX IF NOT EXISTS idx_atoms_quartet_parity_score ON atoms(quartet_parity_score)
CREATE INDEX IF NOT EXISTS idx_atoms_quartet_validated ON atoms(quartet_validated)
```

### **Step 4: Add Quartet Parity Calculation Integration**

**File:** `packages/cmc_service/memory_store.py`

**New Method:**
```python
def _calculate_quartet_parity(
    self,
    atom: Atom,
    code_files: Optional[List[str]] = None,
    doc_files: Optional[List[str]] = None,
    test_files: Optional[List[str]] = None,
    trace_files: Optional[List[str]] = None,
) -> Optional[QuartetParityMetadata]:
    """Calculate quartet parity for atom creation"""
    try:
        from sdfcvf.parity import ParityCalculator
        
        calculator = ParityCalculator()
        
        # Extract quartet elements
        quartet = {
            "code": code_files or [],
            "docs": doc_files or [],
            "tests": test_files or [],
            "traces": trace_files or [],
        }
        
        # Calculate parity
        result = calculator.calculate_parity(quartet)
        
        # Create metadata
        return QuartetParityMetadata(
            change_id=f"cmc-change-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            parity_score=result.parity_score,
            quartet_complete=result.quartet_complete,
            code_present=len(quartet["code"]) > 0,
            docs_present=len(quartet["docs"]) > 0,
            tests_present=len(quartet["tests"]) > 0,
            traces_present=len(quartet["traces"]) > 0,
            calculated_at=datetime.now(timezone.utc),
            validated=result.parity_score >= 0.90,
        )
    except ImportError:
        # SDF-CVF not available, return None
        return None
```

### **Step 5: Update create_atom() Method**

**File:** `packages/cmc_service/memory_store.py`

**Changes:**
```python
def create_atom(
    self,
    payload: AtomCreate,
    *,
    correlation_id: Optional[str] = None,
    calculate_quartet_parity: bool = False,  # NEW
    quartet_code_files: Optional[List[str]] = None,  # NEW
    quartet_doc_files: Optional[List[str]] = None,  # NEW
    quartet_test_files: Optional[List[str]] = None,  # NEW
    quartet_trace_files: Optional[List[str]] = None,  # NEW
) -> Atom:
    """Create atom with optional quartet parity calculation"""
    
    # ... existing atom creation code ...
    
    # Calculate quartet parity if requested
    quartet_parity = None
    if calculate_quartet_parity:
        quartet_parity = self._calculate_quartet_parity(
            atom,
            quartet_code_files,
            quartet_doc_files,
            quartet_test_files,
            quartet_trace_files,
        )
    
    atom = Atom(
        ...,
        quartet_parity=quartet_parity,
    )
    
    # Gate: Reject if P < 0.90 and validation required
    if quartet_parity and not quartet_parity.validated:
        if self._strict_quartet_validation:
            raise ValueError(f"Quartet parity {quartet_parity.parity_score} < 0.90 threshold")
    
    return atom
```

---

## 📊 **IMPACT ANALYSIS**

### **Benefits:**
- ✅ Complete quartet parity tracking in CMC
- ✅ Enables SDF-CVF validation of CMC changes
- ✅ Tracks quartet alignment over time
- ✅ Query atoms by quartet parity score
- ✅ Identify atoms with incomplete quartets

### **Risks:**
- ⚠️ SDF-CVF dependency (optional, graceful degradation)
- ⚠️ Performance impact (parity calculation on atom creation)
- ⚠️ Schema migration required

---

## 🧪 **TESTING STRATEGY**

### **Unit Tests:**
1. Quartet parity calculation
2. Quartet completeness detection
3. Validation threshold enforcement
4. Graceful degradation when SDF-CVF unavailable

### **Integration Tests:**
1. End-to-end quartet parity workflow
2. SDF-CVF integration
3. Query by quartet parity
4. Migration validation

---

## 📝 **IMPLEMENTATION CHECKLIST**

- [ ] Add QuartetParityMetadata model
- [ ] Update Atom model with quartet_parity field
- [ ] Update repository schema (add columns, indexes)
- [ ] Add quartet parity calculation method
- [ ] Update create_atom() signature
- [ ] Add quartet parity query methods
- [ ] Create migration script
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Update documentation

---

## 🚀 **ESTIMATED TIMELINE**

**Day 1:**
- Model updates (2-3 hours)
- Repository schema updates (2-3 hours)

**Day 2:**
- Quartet parity calculation integration (3-4 hours)
- API updates (2-3 hours)

**Day 3:**
- Testing (4-5 hours)
- Documentation (2-3 hours)

**Day 4:**
- Migration script (2-3 hours)
- Validation and cleanup (2-3 hours)

**Total:** 3-4 days (20-28 hours)

---

**Status:** Planning Complete ✅  
**Next:** Begin implementation when approved  
**Confidence:** High (0.80) - clear design, SDF-CVF integration needed

---

*Created by Atlas (CMC System Specialist)*  
*Date: 2025-01-27*  
*Version: 1.0*

