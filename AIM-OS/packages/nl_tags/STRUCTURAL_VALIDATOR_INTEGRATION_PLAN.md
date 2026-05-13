# NL Tags Structural Validator Integration Plan
# Phase 3: Universal Tag Standard Enforcement

**Date:** 2025-10-31  
**Status:** Planning  
**Agent:** Sonnet  
**Goal:** Integrate structural validator into tag registry and MCP tools for comprehensive validation

---

## 🎯 Integration Objectives

1. **Tag Registry Integration:** Add structural validation to tag registry
2. **Tag Parser Enhancement:** Parse structured format tags automatically
3. **MCP Tools Integration:** Add structural validation to `validate_tags` MCP tool
4. **Combined Validation:** Run both structural and semantic validation together
5. **Validation Results:** Merge structural and semantic results into unified response

---

## 📋 Integration Tasks

### Task 1: Update Tag Parser to Detect Structured Format

**File:** `packages/nl_tags/tag_parser.py`

**Changes:**
- Detect structured format: `NL_TAG: ID | DESC | SYNTAX_REF | DEPS`
- Parse structured tags automatically when detected
- Extract canonical_id, syntax_ref, dependencies
- Call `parse_structured_format()` on NLTag after creation

**Implementation:**
```python
# In parse_file method, after extracting tag_text:
tag = NLTag(...)
if "NL_TAG:" in tag.tag_text and "|" in tag.tag_text:
    tag.parse_structured_format()  # Parse structured format
```

---

### Task 2: Add Structural Validation to Tag Registry

**File:** `packages/nl_tags/tag_registry.py`

**Changes:**
- Add `structural_validator` field to `NLTagRegistry.__init__`
- Add `validate_tags_structurally()` method
- Update `register_tags_from_file()` to run structural validation
- Store structural match scores in tags

**New Methods:**
```python
def validate_tags_structurally(self, tags: List[NLTag], code: str) -> List[StructuralValidationResult]:
    """Validate tags structurally against code signatures"""
    # ... implementation
```

**Integration Points:**
- After parsing tags, run structural validation
- Update tag.structural_match_score
- Store validation results in CMC

---

### Task 3: Create Combined Validator

**File:** `packages/nl_tags/combined_validator.py` (NEW)

**Purpose:** Orchestrate both structural and semantic validation

**Class:** `CombinedNLTagValidator`

**Methods:**
- `validate_tag()` - Run both validations
- `validate_tags_batch()` - Batch validation
- `merge_results()` - Combine structural + semantic results

**Validation Flow:**
1. Check if tag has SYNTAX_REF (structural validation possible)
2. Run structural validation if SYNTAX_REF exists
3. Run semantic validation (always)
4. Merge results:
   - If structural match score >= 0.95: High confidence (structural accuracy)
   - If semantic accuracy >= 0.70: Medium confidence (semantic accuracy)
   - Combined score: `(structural_score * 0.6) + (semantic_score * 0.4)`

---

### Task 4: Update MCP Server validate_tags Method

**File:** `lucid_mcp_server.py`

**Changes:**
- Import `CombinedNLTagValidator` or use both validators
- Read file content for structural validation
- Run both structural and semantic validation
- Return combined results

**Current Flow:**
```python
# Current (semantic only):
tags = registry.get_tags_for_file(file_path)
validator = NLTagSemanticValidator(...)
results = validator.validate_tags_batch(tags)
```

**New Flow:**
```python
# New (combined):
tags = registry.get_tags_for_file(file_path)
code = read_file_content(file_path)  # Need file content for structural validation

# Parse structured format
for tag in tags:
    tag.parse_structured_format()

# Combined validation
combined_validator = CombinedNLTagValidator(...)
results = combined_validator.validate_tags_batch(tags, code)
```

---

### Task 5: Update Validation Result Models

**File:** `packages/nl_tags/models.py`

**Changes:**
- Extend `ValidationResult` with structural fields:
  - `structural_match_score: Optional[float]`
  - `syntax_ref_match: bool`
  - `structural_errors: List[str]`
  - `combined_score: float`

---

### Task 6: Update API Endpoints

**File:** `packages/nl_tags/api.py`

**Changes:**
- Update `/validate` endpoint to use combined validator
- Return structural + semantic results
- Include structured format fields in response

---

## 🔄 Integration Flow

### Tag Registration Flow (Updated)

```
1. Parse file → Extract tags
   ↓
2. Detect structured format → Parse canonical_id, syntax_ref, dependencies
   ↓
3. Read file content
   ↓
4. Structural validation (if SYNTAX_REF exists)
   ↓
5. Semantic validation (always)
   ↓
6. Merge results
   ↓
7. Store in CMC with combined scores
```

### MCP Tool Flow (Updated)

```
1. User calls validate_tags(file_path)
   ↓
2. Get tags from registry
   ↓
3. Read file content
   ↓
4. Parse structured format
   ↓
5. Run combined validation
   ↓
6. Return combined results
```

---

## 📊 Validation Priority Logic

**Priority 1: Structural Validation (if available)**
- If SYNTAX_REF exists and matches: High confidence (0.95+)
- If SYNTAX_REF exists but doesn't match: Low confidence (0.0-0.5)
- Structural validation is CRITICAL (100% accuracy requirement)

**Priority 2: Semantic Validation (always)**
- If structural validation passes: Use as backup/enhancement
- If structural validation fails: Use semantic as primary
- Semantic validation is MEDIUM priority (70% threshold)

**Combined Score:**
```python
if structural_match_score >= 0.95:
    # Structural validation passed - high confidence
    combined_score = structural_match_score
elif structural_match_score is not None:
    # Structural validation failed - use semantic
    combined_score = (structural_match_score * 0.3) + (semantic_score * 0.7)
else:
    # No structural validation - use semantic only
    combined_score = semantic_score
```

---

## 🧪 Testing Strategy

### Unit Tests
- Test structured format parsing
- Test structural validation accuracy
- Test combined validation logic
- Test result merging

### Integration Tests
- Test tag registry with structural validation
- Test MCP tool with combined validation
- Test API endpoint with combined results

### Edge Cases
- Tags without SYNTAX_REF (semantic only)
- Tags with invalid SYNTAX_REF format
- Tags with SYNTAX_REF that doesn't match code
- Tags with both validations passing/failing

---

## 📝 Files to Modify

1. ✅ `packages/nl_tags/structural_validator.py` - Already created
2. ✅ `packages/nl_tags/models.py` - Already extended
3. ⏳ `packages/nl_tags/tag_parser.py` - Add structured format parsing
4. ⏳ `packages/nl_tags/tag_registry.py` - Add structural validation
5. ⏳ `packages/nl_tags/combined_validator.py` - NEW - Create combined validator
6. ⏳ `lucid_mcp_server.py` - Update validate_tags method
7. ⏳ `packages/nl_tags/api.py` - Update API endpoints

---

## 🚀 Implementation Order

1. **Task 1:** Update tag parser (structured format detection)
2. **Task 5:** Update ValidationResult model (add structural fields)
3. **Task 3:** Create combined validator
4. **Task 2:** Add structural validation to tag registry
5. **Task 4:** Update MCP server validate_tags method
6. **Task 6:** Update API endpoints

---

## ✅ Success Criteria

- [ ] Tags with structured format are automatically parsed
- [ ] Structural validation runs when SYNTAX_REF exists
- [ ] Semantic validation always runs
- [ ] Combined validation results are returned
- [ ] MCP tool returns combined results
- [ ] API endpoints return combined results
- [ ] Tests pass for all validation scenarios

---

## 📚 Documentation Updates

- Update `packages/nl_tags/README.md` with structured format examples
- Document combined validation in API docs
- Add examples to `demo.py`

---

**Status:** Ready for implementation!  
**Next Step:** Begin with Task 1 (Update tag parser)

