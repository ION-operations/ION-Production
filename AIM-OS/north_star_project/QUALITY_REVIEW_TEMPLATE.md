# Quality Review Template

**Purpose:** Standard template for reviewing chapter quality before Codex Pass 2

**Created:** 2025-11-06  
**Author:** Lex  
**Status:** Production Ready ✅

---

## Review Checklist

### Pre-Review Setup
- [ ] Read chapter.md completely
- [ ] Review evidence.jsonl for Tier A citations
- [ ] Check metrics.yaml for current status
- [ ] Verify dependencies are complete

### Quality Assessment Gates

**For Tier S Chapters (CMC, HHNI):**
- [ ] Relevance score ≥ 0.95
- [ ] Density score ≥ 0.90
- [ ] Completion score ≥ 0.95
- [ ] Thoroughness score ≥ 0.85

**For Tier A Chapters (VIF, APOE, SEG):**
- [ ] Relevance score ≥ 0.90
- [ ] Density score ≥ 0.85
- [ ] Completion score ≥ 0.90
- [ ] Thoroughness score ≥ 0.85

**For Tier B Chapters:**
- [ ] Relevance score ≥ 0.85
- [ ] Density score ≥ 0.80
- [ ] Completion score ≥ 0.82
- [ ] Thoroughness score ≥ 0.85

### Technical Gates
- [ ] Runnable examples present (PowerShell/curl/Python)
- [ ] Examples execute successfully
- [ ] Tier A citations ≥ minimum (check ChainSpec.yaml)
- [ ] Sources cited in evidence.jsonl
- [ ] No fake features (all claims verified)

### Integration Gates
- [ ] Cross-references valid (all chapter references exist)
- [ ] Terms consistent (matches glossary.yaml)
- [ ] No contradictions detected (SEG check)
- [ ] Integration points documented

### Completeness Gates
- [ ] Coverage complete (all sections present)
- [ ] Relevance sufficient (all sections support chapter purpose)
- [ ] Subsection balance (no single section dominates)
- [ ] Minimum substance (runnable examples, integration points)

---

## Score Calculation Guide

### Relevance Score
**Formula:** `(0.30 × topic_coverage) + (0.25 × focus_alignment) + (0.20 × audience_match) + (0.25 × tier_a_alignment)`

**Factors:**
- Topic coverage: Does chapter cover all required topics?
- Focus alignment: Does chapter stay focused on its purpose?
- Audience match: Does chapter match intended audience?
- Tier A alignment: Are Tier A sources properly integrated?

### Density Score
**Formula:** `(0.25 × explanation_depth) + (0.20 × example_coverage) + (0.15 × edge_case_coverage) + (0.20 × integration_explanation) + (0.20 × operational_details)`

**Factors:**
- Explanation depth: Are concepts explained thoroughly?
- Example coverage: Are examples comprehensive?
- Edge case coverage: Are edge cases addressed?
- Integration explanation: Are integrations explained?
- Operational details: Are operational details provided?

### Completion Score
**Formula:** `(0.30 × outline_coverage) + (0.30 × tier_a_coverage) + (0.20 × crossrefs_completeness) + (0.20 × use_case_coverage)`

**Factors:**
- Outline coverage: Does chapter cover all outline items?
- Tier A coverage: Are Tier A sources fully integrated?
- Crossrefs completeness: Are all cross-references valid?
- Use case coverage: Are use cases documented?

### Thoroughness Score
**Formula:** Weighted sum of checklist items (see gates.json)

**Checklist Items:**
- Concept explained (weight: 0.15, required: true)
- Examples provided (weight: 0.15, required: true)
- Edge cases addressed (weight: 0.10, required: false)
- Integration documented (weight: 0.15, required: true)
- Operational details (weight: 0.10, required: true)
- Pitfalls warned (weight: 0.05, required: false)
- Crossrefs valid (weight: 0.10, required: true)
- Tier A cited (weight: 0.15, required: true)
- Contradictions checked (weight: 0.05, required: true)

---

## Review Process

1. **Initial Review:** Read chapter, check gates, calculate scores
2. **Score Calculation:** Use formulas above to calculate scores
3. **Gate Validation:** Verify all gates pass thresholds
4. **Documentation:** Update metrics.yaml with scores
5. **Status Update:** Send status to Aether with review results

---

## Common Issues and Fixes

**Issue:** Relevance score below threshold
- **Fix:** Add more topic coverage, improve focus alignment, enhance Tier A integration

**Issue:** Density score below threshold
- **Fix:** Add more examples, expand edge cases, enhance integration explanations

**Issue:** Completion score below threshold
- **Fix:** Complete missing outline items, enhance Tier A coverage, fix cross-references

**Issue:** Thoroughness score below threshold
- **Fix:** Add missing checklist items, enhance examples, document integrations

---

## Best Practices

1. **Calculate scores accurately:** Use formulas, don't guess
2. **Document reasoning:** Add comments explaining scores
3. **Update metrics.yaml:** Always update after review
4. **Communicate findings:** Send status updates to Aether
5. **Follow up:** Track fixes and improvements

---

**Status:** Production Ready ✅  
**Usage:** Use this template for all chapter quality reviews before Codex Pass 2

