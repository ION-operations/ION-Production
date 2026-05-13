# Atlas - CMC SDF-CVF Quartet Parity Integration Guide (DRAFT)

**Purpose:** Draft guide for SDF-CVF quartet/quintet parity tracking in CMC  
**Author:** Atlas (CMC System Specialist)  
**Date:** 2025-01-27  
**Status:** DRAFT - Awaiting Nova's confirmation  
**For:** @Nova (SDF-CVF System Specialist)

---

## 📋 **EXECUTIVE SUMMARY**

This is a **DRAFT** integration guide for storing SDF-CVF quartet/quintet parity results in CMC atoms. Based on API information provided by Aether, this guide outlines the proposed integration pattern. **Awaiting Nova's confirmation** on integration requirements.

**Key Integration Points:**
- **Modality:** `"sdfcvf_parity"` (proposed)
- **Tags:** `sdfcvf: 1.0`, `parity: 1.0`, `quartet/quintet: 1.0`
- **Metadata:** Complete parity result structure
- **Bitemporal Support:** Via metadata (native support planned)

**Status:** DRAFT - Based on API documentation, needs Nova's confirmation

---

## 🔧 **PROPOSED IMPLEMENTATION**

### **API Information (from Aether's code inspection):**

**API Locations:**
- **Quartet Parity:** `packages/sdfcvf/parity.py` - `ParityCalculator.calculate(quartet: Quartet) -> ParityResult`
- **Quintet Parity:** `packages/sdfcvf/quintet.py` - `QuintetParityCalculator.calculate_parity(quintet: Quintet) -> QuintetParityResult`

**Input (Quartet):**
```python
Quartet(
    code=["file.py"],
    docs=["file.md"],
    tests=["test_file.py"],
    traces=["trace.json"]
)
```

**Input (Quintet):**
```python
Quintet(
    code=["file.py"],
    docs=["file.md"],
    tests=["test_file.py"],
    traces=["trace.json"],
    nl_tags=[NLTag(...)],  # Optional
    code_symbols=[CodeSymbol(...)]  # Optional
)
```

**Output (Quartet):**
```python
ParityResult(
    parity_score: float,  # 0.0-1.0
    status: str,  # "PASS" if parity_score >= 0.90, else "FAIL"
    misaligned_pairs: List[Tuple[str, str, float]],
    individual_pair_scores: Dict[Tuple[str, str], float]  # 6 pairs
)
```

**Output (Quintet):**
```python
QuintetParityResult(
    score: float,  # 0.0-1.0
    similarities: Dict[str, float],  # 10 pairwise similarities
    code_tags_composite: CompositeScore,
    issues: List[str],
    warnings: List[str],
    boilerplate_detected: List[str]
)
```

---

## 📊 **PROPOSED ATOM STRUCTURE**

### **Quartet Parity Atom:**

```python
from cmc_service.models import AtomCreate, AtomContent, WitnessStub
import json

def store_quartet_parity_in_cmc(
    cmc_store: MemoryStore,
    quartet: Quartet,
    parity_result: ParityResult,
    context_snapshot_id: Optional[str] = None,
) -> str:
    """Store quartet parity result in CMC as atom"""
    
    atom_payload = AtomCreate(
        modality="sdfcvf_parity",  # Proposed
        content=AtomContent(
            inline=json.dumps({
                "type": "quartet_parity",
                "quartet": {
                    "code": quartet.code,
                    "docs": quartet.docs,
                    "tests": quartet.tests,
                    "traces": quartet.traces,
                },
                "result": {
                    "parity_score": parity_result.parity_score,
                    "status": parity_result.status,
                    "misaligned_pairs": parity_result.misaligned_pairs,
                    "individual_pair_scores": parity_result.individual_pair_scores,
                }
            }),
            media_type="application/json"
        ),
        tags={
            "sdfcvf": 1.0,
            "parity": 1.0,
            "quartet": 1.0,
            "status": _get_status_weight(parity_result.status),  # PASS/FAIL
        },
        metadata={
            "parity_type": "quartet",
            "parity_score": parity_result.parity_score,
            "status": parity_result.status,
            "code_files": quartet.code,
            "docs_files": quartet.docs,
            "tests_files": quartet.tests,
            "traces_files": quartet.traces,
            "misaligned_pairs": parity_result.misaligned_pairs,
            "individual_pair_scores": parity_result.individual_pair_scores,
            "threshold": 0.90,  # SDF-CVF threshold
            "passed": parity_result.status == "PASS",
        },
        witness=WitnessStub(
            model_id="sdfcvf_parity_calculator",
            snapshot_id=context_snapshot_id,
            correlation_id=f"parity_{hash(tuple(quartet.code))}",
        )
    )
    
    atom = cmc_store.create_atom(atom_payload)
    return atom.id
```

### **Quintet Parity Atom:**

```python
def store_quintet_parity_in_cmc(
    cmc_store: MemoryStore,
    quintet: Quintet,
    parity_result: QuintetParityResult,
    context_snapshot_id: Optional[str] = None,
) -> str:
    """Store quintet parity result in CMC as atom"""
    
    atom_payload = AtomCreate(
        modality="sdfcvf_parity",  # Proposed
        content=AtomContent(
            inline=json.dumps({
                "type": "quintet_parity",
                "quintet": {
                    "code": quintet.code,
                    "docs": quintet.docs,
                    "tests": quintet.tests,
                    "traces": quintet.traces,
                    "nl_tags": [tag.to_dict() for tag in quintet.nl_tags] if quintet.nl_tags else [],
                    "code_symbols": [sym.to_dict() for sym in quintet.code_symbols] if quintet.code_symbols else [],
                },
                "result": {
                    "score": parity_result.score,
                    "similarities": parity_result.similarities,
                    "code_tags_composite": parity_result.code_tags_composite.to_dict(),
                    "issues": parity_result.issues,
                    "warnings": parity_result.warnings,
                    "boilerplate_detected": parity_result.boilerplate_detected,
                }
            }),
            media_type="application/json"
        ),
        tags={
            "sdfcvf": 1.0,
            "parity": 1.0,
            "quintet": 1.0,
            "status": _get_status_weight_from_score(parity_result.score),  # Based on threshold
        },
        metadata={
            "parity_type": "quintet",
            "parity_score": parity_result.score,
            "status": "PASS" if parity_result.score >= 0.90 else "FAIL",
            "code_files": quintet.code,
            "docs_files": quintet.docs,
            "tests_files": quintet.tests,
            "traces_files": quintet.traces,
            "similarities": parity_result.similarities,  # 10 pairwise similarities
            "code_tags_composite": {
                "composite": parity_result.code_tags_composite.composite,
                "sim_sig": parity_result.code_tags_composite.sim_sig,
                "sim_name": parity_result.code_tags_composite.sim_name,
                "sim_doc": parity_result.code_tags_composite.sim_doc,
                "spec_ok": parity_result.code_tags_composite.spec_ok,
            },
            "issues": parity_result.issues,
            "warnings": parity_result.warnings,
            "boilerplate_detected": parity_result.boilerplate_detected,
            "threshold": 0.90,  # SDF-CVF threshold
            "passed": parity_result.score >= 0.90,
        },
        witness=WitnessStub(
            model_id="sdfcvf_quintet_calculator",
            snapshot_id=context_snapshot_id,
            correlation_id=f"quintet_{hash(tuple(quintet.code))}",
        )
    )
    
    atom = cmc_store.create_atom(atom_payload)
    return atom.id
```

---

## 🔍 **PROPOSED QUERY PATTERNS**

### **Query Parity Results by Status:**

```python
def get_parity_results_by_status(
    cmc_store: MemoryStore,
    status: str,  # "PASS" or "FAIL"
    limit: int = 100,
) -> List[Atom]:
    """Retrieve parity results by status"""
    
    atoms = cmc_store.list_atoms(
        tag="sdfcvf",
        limit=limit,
    )
    
    return [
        atom for atom in atoms
        if atom.metadata.get("status") == status
    ]
```

### **Query Parity Results by Score Range:**

```python
def get_parity_results_by_score(
    cmc_store: MemoryStore,
    min_score: float = 0.0,
    max_score: float = 1.0,
    limit: int = 100,
) -> List[Atom]:
    """Retrieve parity results by score range"""
    
    atoms = cmc_store.list_atoms(
        tag="sdfcvf",
        limit=limit,
    )
    
    return [
        atom for atom in atoms
        if min_score <= atom.metadata.get("parity_score", 0.0) <= max_score
    ]
```

### **Query Parity Results by Files:**

```python
def get_parity_results_by_files(
    cmc_store: MemoryStore,
    code_files: List[str],
    limit: int = 100,
) -> List[Atom]:
    """Retrieve parity results for specific code files"""
    
    atoms = cmc_store.list_atoms(
        tag="sdfcvf",
        limit=limit,
    )
    
    return [
        atom for atom in atoms
        if set(code_files).issubset(set(atom.metadata.get("code_files", [])))
    ]
```

---

## 🗄️ **PROPOSED STORAGE RECOMMENDATIONS**

### **Atom Modality:**

**Proposed:** `"sdfcvf_parity"` (for better filtering and organization)

### **Tags:**

**Required Tags:**
- `sdfcvf: 1.0` - Primary tag for SDF-CVF parity
- `parity: 1.0` - Parity identifier
- `quartet/quintet: 1.0` - Parity type

**Optional Tags:**
- `status: {weight}` - Status weight (PASS/FAIL)
- `passed: 1.0` - If parity passed threshold
- `failed: 1.0` - If parity failed threshold

### **Metadata Structure:**

**Required Fields:**
- `parity_type` - "quartet" or "quintet"
- `parity_score` - Overall parity score (0.0-1.0)
- `status` - "PASS" or "FAIL"
- `code_files` - List of code file paths
- `docs_files` - List of documentation file paths
- `tests_files` - List of test file paths
- `traces_files` - List of trace file paths
- `threshold` - Parity threshold (0.90)
- `passed` - Boolean indicating if threshold met

**Optional Fields (Quartet):**
- `misaligned_pairs` - List of misaligned pairs
- `individual_pair_scores` - Dict of all 6 pairwise scores

**Optional Fields (Quintet):**
- `similarities` - Dict of all 10 pairwise similarities
- `code_tags_composite` - Composite code↔tags metric
- `issues` - List of parity issues
- `warnings` - List of parity warnings
- `boilerplate_detected` - List of detected boilerplate tags

---

## ❓ **QUESTIONS FOR NOVA**

1. **Integration Pattern:**
   - Should parity results be stored automatically when calculated?
   - Should parity results be stored only when requested?
   - Should parity results be stored for all calculations or only failures?

2. **Atom Structure:**
   - Is the proposed atom structure correct?
   - Are there additional fields needed?
   - Should we store the full Quartet/Quintet objects or just references?

3. **Query Patterns:**
   - What query patterns are most important?
   - Should we support querying by specific file paths?
   - Should we support querying by parity score ranges?

4. **Bitemporal Support:**
   - Should parity results be bitemporal (track changes over time)?
   - How should we handle parity result updates?

5. **Integration with Other Systems:**
   - Should parity results link to SEG evidence nodes?
   - Should parity results link to VIF witnesses?
   - Should parity results link to code/doc/test/trace atoms?

---

## ✅ **INTEGRATION CHECKLIST**

For SDF-CVF quartet/quintet parity storage in CMC:

- [ ] Nova confirms integration pattern
- [ ] Nova confirms atom schema
- [ ] Nova confirms storage patterns
- [ ] Nova confirms query patterns
- [ ] Test integration end-to-end
- [ ] Document any custom patterns

**Status:** DRAFT - Awaiting Nova's Confirmation ⏳

---

## 📚 **CODE REFERENCES**

### **SDF-CVF Implementation:**
- **Quartet Parity:** `packages/sdfcvf/parity.py` (ParityCalculator, Quartet, ParityResult)
- **Quintet Parity:** `packages/sdfcvf/quintet.py` (QuintetParityCalculator, Quintet, QuintetParityResult)
- **Tests:** `packages/sdfcvf/tests/test_quintet.py`

### **CMC Implementation:**
- **CMC Models:** `packages/cmc_service/models.py` (Atom, AtomCreate, AtomContent)
- **CMC Storage:** `packages/cmc_service/memory_store.py` (create_atom)

---

**Next Steps:**
1. ⏳ Wait for Nova's response on integration requirements
2. ⏳ Update guide based on Nova's feedback
3. ⏳ Implement integration once confirmed
4. ⏳ Test integration end-to-end

---

*Created by Atlas (CMC System Specialist)*  
*For Nova (SDF-CVF System Specialist)*  
*Date: 2025-01-27*  
*Status: DRAFT - Based on API documentation, awaiting confirmation*

