# APOE Spec Sync Tool Update Plan
**Date:** 2025-01-28  
**Route:** R-SYNTHESIS-001  
**Status:** ⏳ **FOR SYNTHESIS DISCUSSION** (Non-blocking)  
**Owner:** Alex (APOE)

---

## 🎯 **Purpose**

This document outlines the proposed update plan for `packages/apoe/tools/apoe_cmc_spec_sync.py` to explicitly validate all 5 required tags per `APOE_CMC_PAYLOAD_SPEC_v1.md`.

---

## 📋 **Current State**

### **Current Validation:**
- ✅ Modality: Validates `modality == "plan_execution"`
- ✅ Tags: Validates tags exist (regex-based, finds tags in spec and tests)
- ⚠️ Tag Coverage: Checks if spec tags appear in tests, but doesn't explicitly validate all 5 required tags

### **Current Limitations:**
1. **Tag Pattern Matching:** Uses regex to find tags, but doesn't explicitly check for all 5 required tags:
   - `"apoe"` ✅
   - `"plan"` ✅
   - `"execution"` ⚠️ (may not be explicitly validated)
   - `"plan_name:<name>"` ⚠️ (validates pattern exists, but doesn't check all required tags)
   - `"status:<status>"` ⚠️ (validates pattern exists, but doesn't check all required tags)

2. **Tag Completeness:** Doesn't verify that tests assert all 5 required tags explicitly

---

## 🔧 **Proposed Updates**

### **Update 1: Explicit Tag Validation**

**Add required tag list:**
```python
REQUIRED_TAGS = {
    "apoe",                    # System identifier
    "plan",                    # Entity type
    "execution",               # Operation type
    "plan_name:<name>",        # Plan name pattern (validated via prefix)
    "status:<status>",         # Status pattern (validated via prefix)
}
```

**Update validation logic:**
```python
def validate_required_tags(tags: Set[str]) -> tuple[bool, List[str]]:
    """Validate all 5 required tags are present.
    
    Returns:
        (is_valid, missing_tags)
    """
    missing = []
    
    # Check exact tags
    if "apoe" not in tags:
        missing.append("apoe")
    if "plan" not in tags:
        missing.append("plan")
    if "execution" not in tags:
        missing.append("execution")
    
    # Check pattern tags
    has_plan_name = any(tag.startswith("plan_name:") for tag in tags)
    if not has_plan_name:
        missing.append("plan_name:<name>")
    
    has_status = any(tag.startswith("status:") for tag in tags)
    if not has_status:
        missing.append("status:<status>")
    
    return (len(missing) == 0, missing)
```

### **Update 2: Enhanced Test Validation**

**Update `load_tests()` to extract all tag assertions:**
```python
def load_tests(test_path: Path) -> TestSnapshot:
    # ... existing code ...
    
    # Enhanced tag extraction: look for explicit assertions
    tag_assertions = set()
    
    # Find explicit tag assertions
    for line in text.splitlines():
        # Pattern: assert "apoe" in tags
        if re.search(r'assert\s+"(apoe|plan|execution)"\s+in\s+tags', line):
            tag_assertions.add(re.search(r'"([^"]+)"', line).group(1))
        
        # Pattern: assert any(tag.startswith("plan_name:") for tag in tags)
        if 'startswith("plan_name:")' in line:
            tag_assertions.add("plan_name:<name>")
        
        # Pattern: assert any(tag.startswith("status:") for tag in tags)
        if 'startswith("status:")' in line:
            tag_assertions.add("status:<status>")
    
    return TestSnapshot(modality=modality, tags=tag_assertions, metadata_keys=metadata_keys)
```

### **Update 3: Enhanced Comparison Logic**

**Update `compare()` to validate all 5 tags:**
```python
def compare(spec: SpecSnapshot, tests: TestSnapshot) -> int:
    # ... existing modality check ...
    
    # Enhanced tag validation
    is_valid, missing_tags = validate_required_tags(tests.tags)
    if not is_valid:
        print(
            f"[apoe-cmc-spec-sync] MISMATCH: missing required tag assertions in tests: {missing_tags}",
            file=sys.stderr,
        )
        status = 1
    
    # ... rest of comparison ...
```

---

## 📊 **Implementation Plan**

### **Phase 1: Core Validation (P0)**
1. Add `REQUIRED_TAGS` constant
2. Add `validate_required_tags()` function
3. Update `compare()` to call validation
4. Test with current test file (should pass after test updates)

### **Phase 2: Enhanced Test Extraction (P1)**
1. Update `load_tests()` to extract explicit tag assertions
2. Improve regex patterns for tag assertion detection
3. Add validation for pattern-based tags (`plan_name:`, `status:`)

### **Phase 3: Documentation (P1)**
1. Update tool docstring with tag validation details
2. Add examples of valid/invalid tag sets
3. Document tag pattern matching rules

---

## ✅ **Success Criteria**

**After Update:**
- ✅ Tool explicitly validates all 5 required tags
- ✅ Tool reports missing tag assertions in tests
- ✅ Tool passes with current test suite (after test updates)
- ✅ Tool fails if any required tag is missing from tests

---

## 🔗 **Dependencies**

**Prerequisites:**
- ✅ Test suite updated to assert all 5 tags (already done - 18/18 tests passing)
- ✅ Spec defines all 5 required tags (already done - `APOE_CMC_PAYLOAD_SPEC_v1.md`)

**Post-Update:**
- Run tool to verify it passes with updated tests
- Add tool to CI/CD pipeline if needed
- Update documentation if tool behavior changes

---

## 📝 **Synthesis Discussion Points**

### **Question 1: Validation Strictness**
- **Option A:** Tool validates that all 5 tags are present in test assertions (strict)
- **Option B:** Tool validates that tags exist in test code (lenient)
- **Recommendation:** Option A (strict validation ensures test coverage)

### **Question 2: Pattern Tag Validation**
- **Option A:** Validate pattern tags via prefix matching (`plan_name:`, `status:`)
- **Option B:** Validate pattern tags via exact match (requires specific plan_name/status values)
- **Recommendation:** Option A (prefix matching is more flexible)

### **Question 3: Implementation Priority**
- **Option A:** Implement immediately (P0)
- **Option B:** Implement post-synthesis (P1)
- **Recommendation:** Option B (non-blocking, can be done post-synthesis)

---

## 🔗 **References**

- Spec: `ide_orchestration/prototypes/dac/docs/agents/alex/APOE_CMC_PAYLOAD_SPEC_v1.md`
- Tool: `packages/apoe/tools/apoe_cmc_spec_sync.py`
- Tests: `packages/apoe/tests/test_cmc_integration.py` (18/18 passing)
- Decisions: `ide_orchestration/prototypes/dac/docs/agents/alex/APOE_CMC_V1_DECISIONS.md`

---

**Status:** ⏳ **READY FOR SYNTHESIS DISCUSSION**  
**Priority:** P1 (Non-blocking, post-synthesis implementation)  
**Confidence:** High (0.90) - Clear update plan, straightforward implementation

