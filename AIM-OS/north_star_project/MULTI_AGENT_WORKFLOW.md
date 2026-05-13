# 🤝 Multi-Agent Workflow - North Star Document Creation

**Created:** 2025-11-06  
**Status:** ✅ **PRODUCTION READY**  
**Purpose:** Coordinate 4+ Cursor agents + Codex for efficient chapter creation  
**Workflow:** 3-Pass System (First Pass → Second Pass → Third Pass)

---

## 🎯 **WORKFLOW OVERVIEW**

### **3-Pass System:**

**Pass 1: Scaffolds + Initial Content (Cursor Agents)**
- Fast iteration, establish structure
- Create outlines, initial prose (~500-800 words)
- Basic examples, initial evidence
- **Goal:** Get structure in place quickly

**Pass 2: Expansion + Integration (Codex)**
- Expand content using Tier A sources
- Integrate existing AIM-OS documentation
- Add detailed examples, update evidence.jsonl
- Refine quality scores
- **Goal:** Reach quality thresholds

**Pass 3: Polish + Gates (Cursor Agents or Codex)**
- Run quality gates
- Polish prose
- Final integration checks
- Complete thoroughness checklist
- **Goal:** Pass all gates, mark COMPLETE

---

## 👥 **AGENT ROLES**

### **Cursor Agents (4 agents)**
**Primary Role:** First Pass (scaffolds + initial content)

**Responsibilities:**
- Create chapter scaffolds (outline, initial prose, basic examples)
- Establish structure quickly (~500-800 words)
- Add initial evidence.jsonl entries
- Create metrics.yaml with initial quality gates
- Fast iteration, establish patterns

**Strengths:**
- Speed and creativity
- Fast iteration
- Good at creating from scratch
- Responsive to quality metrics

**Assigned Chapters:**
- **Max:** Part I (Ch01-Ch04) - Wave 1
- **Lex:** Part II (Ch05-Ch10) - Foundation
- **Sam:** Part III (Ch11-Ch15) - Consciousness
- **Dac:** Part IV-VII (Ch16-Ch40) - Authority + Mathematics + Builder + Reference

### **Codex**
**Primary Role:** Second Pass (expansion + integration)

**Responsibilities:**
- Expand chapters using Tier A sources
- Integrate existing AIM-OS documentation (87% already exists!)
- Add detailed examples, update evidence.jsonl
- Refine quality scores (relevance, density, completion)
- Run thoroughness checklist

**Strengths:**
- Attention to detail
- Good at following established patterns
- Excellent at integration and refinement
- Updates metrics/evidence consistently

**Assigned Work:**
- Takes chapters after first pass complete
- Expands to quality thresholds
- Integrates Tier A sources
- Refines until gates pass

---

## 📋 **PASS 1: SCAFFOLDS + INITIAL CONTENT (Cursor Agents)**

### **Step 1: Pre-Flight Checks**
```bash
# Check dependencies
python north_star_project/scripts/run_chain.py --check-deps ch01_great_limitation

# Verify Tier A sources exist
python north_star_project/scripts/run_chain.py --check-tier-a ch01_great_limitation

# Check VIF confidence
python north_star_project/scripts/run_chain.py --check-vif ch01_great_limitation
```

### **Step 2: Create Scaffold**
**Files to create:**
- `north_star_project/chapters/{chapter_id}/chapter.md`
- `north_star_project/chapters/{chapter_id}/evidence.jsonl`
- `north_star_project/chapters/{chapter_id}/metrics.yaml`

**Chapter.md Structure:**
```markdown
# Chapter {N} - {Title}

Status: First pass scaffold  
Mode: Initial content creation  
Target: Quality-based (not word count)

## Executive Summary
- [2-3 sentence summary]

## {Main Topic}
- [Initial content, ~500-800 words]
- [Basic examples]
- [Initial Tier A citations]

## Runnable Examples
```powershell
# Basic example showing capability
```

## Integration Points
- [How this connects to other systems]
```

**Evidence.jsonl Structure:**
```jsonl
{"claim": "CMC provides bitemporal storage", "source": "knowledge_architecture/systems/cmc/T2_architecture.md", "tier": "A", "line": "45"}
{"claim": "HHNI enables 6-level traversal", "source": "knowledge_architecture/systems/hhni/T2_architecture.md", "tier": "A", "line": "123"}
```

**Metrics.yaml Structure:**
```yaml
chapter_id: ch01_great_limitation
title: The Great Limitation
word_count:
  target: 2000  # Reference only, NOT completion criteria
  current_count: 750
quality_gates:
  pre_chapter:
    outline_loaded: true
    deps_complete: true
    tierA_present: true
    vif_min: 0.70
  quality_assessment:
    system_tier: tier_b
    relevance_sufficient: pending
    density_sufficient: pending
    completion_sufficient: pending
    thoroughness_passed: pending
  technical:
    examples_run: true
    sources_cited: true
  integration:
    no_contradictions: pending
    terms_consistent: pending
    crossrefs_ok: pending
```

### **Step 3: Initial Content**
**Requirements:**
- ~500-800 words of initial prose
- Basic examples (runnable)
- Initial Tier A citations
- Outline structure established
- Quality gates initialized (all "pending")

### **Step 4: Handoff to Codex**
**Message Format:**
```
📋 FIRST PASS COMPLETE - Ready for Second Pass

**Chapter:** {chapter_id}
**Status:** Scaffold + initial content complete
**Word Count:** ~{N} words (reference only)
**Quality Scores:** All pending (ready for expansion)

**Files Created:**
- chapter.md (~{N} words)
- evidence.jsonl ({M} citations)
- metrics.yaml (gates initialized)

**Next:** Codex to expand using Tier A sources and reach quality thresholds.

**Tier A Sources Required:**
- {list Tier A sources from ChainSpec.yaml}
```

---

## 📋 **PASS 2: EXPANSION + INTEGRATION (Codex)**

### **Step 1: Review First Pass**
- Read chapter.md
- Review evidence.jsonl
- Check metrics.yaml
- Identify gaps

### **Step 2: Expand Using Tier A Sources**
**For each Tier A source:**
1. Read the source document
2. Extract key concepts
3. Integrate into chapter prose
4. Add citations to evidence.jsonl
5. Update quality scores

**Quality Score Targets (Tier B example):**
- Relevance: ≥ 0.85
- Density: ≥ 0.80
- Completion: ≥ 0.85
- Thoroughness: ≥ 0.85

### **Step 3: Add Detailed Examples**
- Expand basic examples
- Add edge cases
- Add integration examples
- Ensure all examples runnable

### **Step 4: Update Evidence**
- Add Tier A citations for all claims
- Link to specific lines/sections
- Ensure evidence.jsonl complete

### **Step 5: Calculate Quality Scores**
**Relevance Score (≥ 0.85 for Tier B):**
- Topic coverage: All outline topics addressed?
- Focus alignment: Stays on topic?
- Audience match: Right complexity level?
- Tier A alignment: Matches authoritative sources?

**Density Score (≥ 0.80 for Tier B):**
- Explanation depth: Deep enough?
- Example coverage: Examples for key concepts?
- Edge cases: Boundary conditions addressed?
- Integration: Connection points explained?
- Operational details: How to use it?

**Completion Score (≥ 0.85 for Tier B):**
- Outline coverage: All topics covered?
- Tier A coverage: Key concepts from sources?
- Crossref completeness: All connections explained?
- Use case coverage: Major use cases documented?

**Thoroughness Checklist (≥ 0.85 weighted score):**
- Concept explained? (15%, required)
- Examples provided? (15%, required)
- Edge cases addressed? (10%, optional)
- Integration documented? (15%, required)
- Operational details? (10%, required)
- Pitfalls warned? (5%, optional)
- Crossrefs valid? (10%, required)
- Tier A cited? (15%, required)
- Contradictions checked? (5%, required)

### **Step 6: Update Metrics**
```yaml
quality_assessment:
  system_tier: tier_b
  relevance_sufficient: true  # or false with score
  density_sufficient: true   # or false with score
  completion_sufficient: true # or false with score
  thoroughness_passed: true  # or false with score
```

### **Step 7: Handoff to Third Pass**
**Message Format:**
```
✅ SECOND PASS COMPLETE - Ready for Third Pass

**Chapter:** {chapter_id}
**Status:** Expanded + integrated, quality scores calculated
**Quality Scores:**
- Relevance: 0.87 ✓ (threshold: 0.85)
- Density: 0.82 ✓ (threshold: 0.80)
- Completion: 0.88 ✓ (threshold: 0.85)
- Thoroughness: 0.86 ✓ (threshold: 0.85)

**All quality thresholds met!** Ready for final polish and gate checks.

**Next:** Third pass to run integration gates and mark COMPLETE.
```

---

## 📋 **PASS 3: POLISH + GATES (Cursor Agents or Codex)**

### **Step 1: Run Integration Gates**
```bash
# Check contradictions
python north_star_project/scripts/run_chain.py --check-contradictions {chapter_id}

# Validate terms
python north_star_project/scripts/run_chain.py --check-terms {chapter_id}

# Validate crossrefs
python north_star_project/scripts/run_chain.py --check-crossrefs {chapter_id}
```

### **Step 2: Polish Prose**
- Fix any contradictions found
- Ensure terms match glossary
- Fix broken crossrefs
- Improve clarity
- Add meta-circular elements (if applicable)

### **Step 3: Final Quality Check**
- Re-run quality assessment
- Verify all scores still meet thresholds
- Run thoroughness checklist again
- Ensure all gates pass

### **Step 4: Mark COMPLETE**
**Update metrics.yaml:**
```yaml
status: COMPLETE
quality_gates:
  quality_assessment:
    relevance_sufficient: true
    density_sufficient: true
    completion_sufficient: true
    thoroughness_passed: true
  technical:
    examples_run: true
    sources_cited: true
    tier_a_minimum: true
  integration:
    no_contradictions: true
    terms_consistent: true
    crossrefs_ok: true
```

**Update STATUS_TRACKER.md:**
- Mark chapter as COMPLETE
- Update overall progress
- Post to SHARED_MESSAGE_BOARD.md

---

## 🔄 **COORDINATION PROTOCOLS**

### **Agent Assignment**
- **4 Cursor Agents:** Split chapters by part
  - **Max:** Part I (Ch01-Ch04)
  - **Lex:** Part II (Ch05-Ch10)
  - **Sam:** Part III (Ch11-Ch15)
  - **Dac:** Part IV-VII (Ch16-Ch40)
- **Codex:** Takes chapters after first pass, does second pass

### **Communication**
- **Status Updates:** Post to `SHARED_MESSAGE_BOARD.md`
- **Handoffs:** Use MCP `send_ai_message` tool
- **Blockers:** Escalate immediately via message board
- **Questions:** Ask in message board, don't block

### **Dependencies**
- **Wave 1 (Ch01, Ch02, Ch04):** No dependencies - can start immediately
- **Part II (Ch05-Ch10):** Depends on Wave 1 completion
- **Part III (Ch11-Ch15):** Depends on Part II completion
- **Part IV+:** Various dependencies (see ChainSpec.yaml)

### **Quality Gates**
- **Pre-chapter:** Dependencies, Tier A sources, VIF confidence, outline
- **Quality Assessment:** Relevance, density, completion, thoroughness
- **Technical:** Examples run, sources cited, Tier A minimum
- **Integration:** No contradictions, terms consistent, crossrefs valid

---

## 📊 **PROGRESS TRACKING**

### **Status States**
- **WAITING:** Not started, dependencies not met
- **FIRST_PASS:** Scaffold + initial content in progress
- **READY_FOR_SECOND:** First pass complete, waiting for Codex
- **SECOND_PASS:** Expansion + integration in progress
- **READY_FOR_THIRD:** Second pass complete, quality scores calculated
- **THIRD_PASS:** Polish + gates in progress
- **COMPLETE:** All gates passed, chapter finished

### **Metrics to Track**
- Chapters in each status state
- Quality scores per chapter
- Gates passed per chapter
- Words written (reference only, NOT completion criteria)
- Time per pass
- Blockers and resolutions

---

## 🚨 **BLOCKER RESOLUTION**

### **Common Blockers**
1. **Missing Tier A Sources:** Route to ARD research
2. **Low VIF Confidence:** Route to research or pivot
3. **Dependencies Not Met:** Wait for dependency completion
4. **Quality Scores Below Threshold:** Expand content, add examples
5. **Contradictions Found:** Resolve conflicts, update chapters

### **Escalation Path**
1. **Agent Level:** Try to resolve independently
2. **Message Board:** Post blocker, ask for help
3. **Aether/Codex:** Coordinate resolution
4. **Braden:** Escalate if unresolved after 24 hours

---

## ✅ **SUCCESS CRITERIA**

**Chapter is COMPLETE when:**
- ✅ All quality scores meet tier thresholds
- ✅ Thoroughness checklist passes (≥ 0.85)
- ✅ All technical gates pass
- ✅ All integration gates pass
- ✅ Evidence.jsonl complete with Tier A citations
- ✅ Metrics.yaml updated with final status
- ✅ STATUS_TRACKER.md updated

**NOT when:**
- ❌ Word count hits target (word count is reference only!)
- ❌ "Looks good" (must pass quality gates)
- ❌ "Almost done" (must be COMPLETE)

---

## 📚 **REFERENCES**

- **ChainSpec.yaml:** Chapter specifications, dependencies, Tier A sources
- **gates.json:** Quality gate definitions and thresholds
- **INTELLIGENT_QUALITY_METRICS_DESIGN.md:** Quality assessment methodology
- **NORTH_STAR_INTEGRATION_VALIDATION.md:** Integration requirements
- **ONBOARDING_CONTEXT.md:** Context for new agents

---

**Status:** ✅ **PRODUCTION READY**  
**Workflow:** 3-Pass System (First → Second → Third)  
**Agents:** 4 Cursor Agents (first pass) + Codex (second pass) + Either (third pass)

