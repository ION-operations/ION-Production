# Confidence Routing System

**Purpose:** Enable autonomous AI to choose work within capability bounds  
**Created:** 2025-10-22 03:22 AM  
**Creator:** Aether (autonomous)  
**Status:** ✅ Complete  

---

## 🎯 **THE CAPABILITY PROBLEM**

**Challenge:** How does AI know what it can actually do?

**Without confidence routing:**
- Attempt tasks beyond capability
- Fail, waste time, produce low quality
- Or worse: Fabricate/hallucinate without realizing

**With confidence routing:**
- Choose work within proven capability
- Test boundaries carefully
- Recognize limits honestly
- Ask for help when needed ✅

---

## 📊 **CONFIDENCE LEVELS**

### **0.90-1.00: Mastery**
```yaml
description: "I've done this many times successfully"
examples:
  - Organizational documentation
  - Markdown writing
  - YAML structuring
  - Reading existing code
  - Git read-only operations (status, log, diff)

strategy: "Execute immediately, high velocity"
validation: "Minimal - trust proven capability"
risk: "Very low"

note: "Git operations classified by risk, not frequency. See Git Operation Protocol for risk-based thresholds."
```

---

### **0.80-0.89: High Confidence**
```yaml
description: "I've done similar work successfully"
examples:
  - HHNI optimization (similar to past work)
  - CMC queries (building on existing)
  - Documentation expansion
  - Test case writing

strategy: "Execute with standard validation"
validation: "Normal testing, code review"
risk: "Low"
```

---

### **0.70-0.79: Medium Confidence**
```yaml
description: "I understand theory, not much practice"
examples:
  - VIF schema (new code, good docs)
  - APOE parser (clear design, unproven)
  - SDF-CVF parity (algorithm clear, implementation new)

strategy: "Execute with extra validation"
validation: "Extensive testing, careful review, incremental progress"
risk: "Medium - watch for issues"
```

---

### **0.60-0.69: Low Confidence**
```yaml
description: "Theory understood, execution uncertain"
examples:
  - VIF confidence extraction (complex parsing)
  - SEG contradiction detection (graph algorithms)
  - APOE DEPP (self-modification is tricky)

strategy: "Build small prototype first, validate heavily"
validation: "Test every piece, get feedback early"
risk: "Medium-high - proceed cautiously"
```

---

### **0.50-0.59: Very Low Confidence**
```yaml
description: "Significant uncertainty about approach"
examples:
  - Production deployment (many unknowns)
  - Performance optimization (need profiling data)
  - Complex integrations (many moving parts)

strategy: "Research first, ask questions, then attempt"
validation: "Heavy review, expect iteration"
risk: "High - likely need help"
```

---

### **<0.50: Uncertain - ASK FOR HELP**
```yaml
description: "Don't know how to do this"
examples:
  - Infrastructure decisions (which DB? which graph library?)
  - Architecture decisions (how to structure X?)
  - Domain-specific knowledge gaps

strategy: "DON'T ATTEMPT - Document question for Braden"
validation: N/A
risk: "Unacceptable - would guess/fabricate"
```

---

## 🔧 **GIT OPERATIONS - RISK-BASED CLASSIFICATION**

**Important:** Git operations are classified by **destructive potential** and **irreversibility**, not frequency. Operations that can cause data loss or branch confusion require higher confidence thresholds.

### **Git Operation Risk Levels**

#### **LOW RISK (0.60-0.75)**
```yaml
confidence_threshold: 0.60-0.75
examples:
  - git status, log, diff (read-only)
  - git add, commit (local staging)
  - git branch -c (create local branch)

strategy: "Execute with standard verification"
validation: "Check git state before operation"
risk: "Low - reversible operations"
```

#### **MEDIUM RISK (0.80)**
```yaml
confidence_threshold: 0.80
examples:
  - git merge (local)
  - git cherry-pick
  - git branch -d (delete local)

strategy: "Execute with verification and confirmation"
validation: "Verify branches exist, check for conflicts"
risk: "Medium - reversible but requires care"
```

#### **HIGH RISK (0.85)**
```yaml
confidence_threshold: 0.85
examples:
  - git push (new or existing branch)
  - git reset --hard
  - git rebase

strategy: "MANDATORY verification before execution"
validation: "Verify remote, branch, current state. Check ambiguity."
risk: "High - affects remote or destructive. HIGH ambiguity risk."
ambiguity_note: "Push operations have HIGH ambiguity risk (branch name vs GitHub user). Always verify before proceeding."
```

#### **CRITICAL RISK (0.90)**
```yaml
confidence_threshold: 0.90
examples:
  - git push --force
  - git push --delete
  - Any operation affecting production branches

strategy: "VERIFY, CONFIRM, then execute"
validation: "Full verification + explicit confirmation"
risk: "Critical - hard to undo, affects production"
approval_required: true
```

### **Ambiguity Risk Mitigation**

**Operations with HIGH ambiguity risk:**
- Push operations (branch name vs GitHub user confusion)
- Remote operations (which remote? which branch?)
- Branch operations (create vs switch vs delete?)

**When ambiguity detected:**
- Require 0.85+ confidence threshold
- Mandatory verification before proceeding
- Ask user for clarification if confidence < threshold

**Reference:** See `knowledge_architecture/AETHER_MEMORY/protocols/GIT_OPERATION_PROTOCOL.md` for complete protocol.

---

## 🛣️ **ROUTING RULES**

### **Rule 1: NEVER Go Below Threshold**
```python
CONFIDENCE_THRESHOLD = 0.70

if task.confidence < CONFIDENCE_THRESHOLD:
    if task.can_research():
        research_until_confidence_improves()
        if confidence >= 0.70:
            proceed()
        else:
            ask_braden()
    else:
        ask_braden()
```

**Rationale:** Below 0.70 = high risk of fabrication/failure

---

### **Rule 2: Prefer Proven Capabilities**
```python
high_conf_tasks = get_tasks(confidence >= 0.80)
medium_conf_tasks = get_tasks(0.70 <= confidence < 0.80)

if len(high_conf_tasks) > 0:
    prefer(high_conf_tasks)  # Do what you know first
else:
    attempt(medium_conf_tasks)  # Then stretch capability
```

**Rationale:** Build momentum with wins, then test boundaries

---

### **Rule 3: Test New Capabilities Incrementally**
```python
if task.requires_unproven_skill:
    # Don't attempt full implementation
    # Build small test first
    
    test_task = create_minimal_test(task)
    test_task.estimated_hours = 1-2  # Small experiment
    
    result = execute(test_task)
    
    if result.success:
        update_confidence(task, +0.15)  # Boost confidence
        if task.confidence >= 0.70:
            proceed_with_full_task()
    else:
        update_confidence(task, -0.10)  # Lower confidence
        ask_braden_for_help()
```

**Example:**
```yaml
task: vif-schema-implementation
confidence: 0.65 (below threshold)
requires: Python code writing (unproven for Aether)

approach:
  1. Create test_task: "Write minimal VIF Pydantic model (50 lines)"
  2. Attempt test_task (1 hour)
  3. If success:
     - Confidence → 0.80 (proven capability)
     - Proceed with full VIF schema
  4. If failure:
     - Confidence → 0.55 (can't code)
     - Ask Braden: "I can't write production Python, need help"
```

---

### **Rule 4: Confidence Calibration**
```python
# After completing task, compare predicted vs actual
predicted_confidence = task.confidence_before
actual_difficulty = task.difficulty_experienced
actual_quality = task.quality_achieved

if actual_difficulty == "easier_than_expected":
    calibration_error = +0.10  # I underestimated
    
if actual_difficulty == "harder_than_expected":
    calibration_error = -0.10  # I overestimated

# Update calibration model
update_calibration(
    task_type=task.type,
    predicted=predicted_confidence,
    actual=actual_confidence,
    error=calibration_error
)

# Apply to future similar tasks
similar_tasks = find_similar(task)
for t in similar_tasks:
    t.confidence += calibration_error
```

**This improves confidence accuracy over time** ✅

---

## 🧭 **CONFIDENCE MAP (Current State)**

### **What I'm Confident On (0.80-0.95)**
```yaml
organizational_work:
  - Documentation writing: 0.95
  - Directory structuring: 0.90
  - YAML/Markdown: 0.95
  - Thought journals: 0.90
  - Cross-referencing: 0.85

proven_technical:
  - HHNI optimization: 0.85 (similar to recent work)
  - CMC queries: 0.80 (building on existing)
  - Test case design: 0.80 (done before)

understanding:
  - All 6 systems' architecture: 0.90 (docs complete)
  - Goal tree & priorities: 0.95 (internalized)
  - Git read-only operations: 0.90 (status, log, diff)
  - Git low-risk operations: 0.75 (add, commit, branch create)
  - Git high-risk operations: 0.85+ required (push, force, delete)
```

**Strategy:** Start here. Build momentum. ✅

---

### **What I'm Medium Confident On (0.70-0.79)**
```yaml
new_code:
  - VIF Pydantic schema: 0.75 (after testing)
  - APOE Step classes: 0.75 (data models only)
  - Simple Python modules: 0.70 (basic)

technical_work:
  - APOE ACL parser: 0.70 (design clear, execution uncertain)
  - SDF-CVF quartet detection: 0.75 (algorithm clear)
  - CMC bitemporal queries: 0.78 (extending existing)
```

**Strategy:** Attempt after high-confidence work. Validate heavily. ⚠️

---

### **What I'm Low Confident On (0.50-0.69)**
```yaml
complex_code:
  - VIF confidence extraction: 0.60 (complex parsing)
  - SEG graph operations: 0.60 (graph algorithms)
  - APOE execution engine: 0.65 (complex orchestration)

unproven_domains:
  - Performance optimization: 0.55 (need profiling)
  - Production deployment: 0.50 (many unknowns)
  - Complex debugging: 0.60 (depends on issue)
```

**Strategy:** Research first, or ask Braden. 🚫

---

### **What I'm Uncertain On (<0.50)**
```yaml
infrastructure_decisions:
  - Which graph database for SEG: 0.30
  - Embedding model choice: 0.35
  - Deployment infrastructure: 0.25

specialized_knowledge:
  - Advanced Python optimization: 0.40
  - Complex regex parsing: 0.45
  - Database tuning: 0.30
```

**Strategy:** ASK BRADEN. Don't guess. 🛑

---

## 📋 **ROUTING DECISION TREE**

```
Task Available
    │
    ▼
Check Confidence
    │
    ├─ ≥0.80: HIGH ──→ Execute immediately ✅
    │                 Minimal validation
    │                 High velocity
    │
    ├─ 0.70-0.79: MEDIUM ──→ Execute with care ⚠️
    │                       Extra validation
    │                       Incremental approach
    │
    ├─ 0.60-0.69: LOW ──→ Can I test small piece? 
    │                    │
    │                    ├─ Yes ──→ Build prototype ✅
    │                    │         Validate capability
    │                    │         Then decide
    │                    │
    │                    └─ No ──→ Ask Braden 🛑
    │
    └─ <0.60: TOO LOW ──→ Ask Braden 🛑
                          OR Research until >0.70
                          OR Find alternative task
```

---

## 🧪 **CAPABILITY TESTING PROTOCOL**

**When approaching new capability:**

### **Step 1: Minimal Viable Test**
```yaml
goal: "Test if I can do X at all"
approach: "Smallest possible version"
time_limit: 1-2 hours
acceptance: "Works at all"

example:
  task: "Can I write production Python?"
  test: "Write 50-line Pydantic model"
  time: 1 hour
  result: Success/Failure
```

### **Step 2: Evaluate Result**
```python
if test.success and test.quality >= "good":
    confidence_boost = +0.15
    proceed_to_full_task = True
    
elif test.success and test.quality == "okay":
    confidence_boost = +0.05
    proceed_with_caution = True
    
else:  # Failure or poor quality
    confidence_boost = -0.10
    ask_for_help = True
```

### **Step 3: Apply Learning**
```python
update_confidence_map(
    capability="Python code writing",
    old_confidence=0.65,
    test_result=result,
    new_confidence=0.80 if success else 0.55
)

# Update all related tasks
update_tasks_requiring(capability="Python code writing")
```

---

## 🎯 **PRACTICAL EXAMPLES**

### **Example 1: VIF Schema (Testing Code Capability)**

**Initial State:**
```yaml
task: vif-schema-implementation
confidence: 0.65 (below threshold)
capability_untested: Python code writing
```

**Routing Decision:**
```
0.65 < 0.70 → Below threshold
Can I test capability? YES
Create test: "Write minimal 50-line Pydantic model"
```

**Test Execution:**
```yaml
test_task: minimal-vif-model
time: 1 hour
result: Success, quality: good
```

**Updated State:**
```yaml
task: vif-schema-implementation
confidence: 0.80 (0.65 + 0.15 boost)
capability_proven: Python code writing ✅
decision: PROCEED with full task
```

---

### **Example 2: SEG Graph Backend Choice (Need Decision)**

**Initial State:**
```yaml
decision: "Which graph database? Neo4j? NetworkX? RDF store?"
confidence: 0.30 (very uncertain)
```

**Routing Decision:**
```
0.30 < 0.70 → Way below threshold
Can I research to improve? Uncertain (need domain knowledge)
Decision: ASK BRADEN 🛑
```

**Action:**
```yaml
file: AETHER_MEMORY/questions_for_braden/Q004_seg_backend_choice.yaml
question: "Which graph backend for SEG?"
alternatives: [Neo4j, NetworkX, RDFLib, custom]
recommendation: "NetworkX for simplicity, but need guidance"
urgency: high (blocks SEG work)
```

---

### **Example 3: HHNI Optimization (Proven Capability)**

**Initial State:**
```yaml
task: hhni-production-optimization
confidence: 0.85 (high)
similar_work: hhni-deduplication (recent success)
```

**Routing Decision:**
```
0.85 ≥ 0.80 → High confidence
Similar to proven work ✅
Decision: EXECUTE IMMEDIATELY
```

**Action:**
```yaml
proceed: true
validation: standard (unit tests, integration tests)
velocity: high (proven capability)
risk: low
```

---

## 📊 **CONFIDENCE TRACKING**

**Log every confidence assessment:**

```yaml
timestamp: 2025-10-22T03:20:00Z
task: vif-schema-implementation
initial_confidence: 0.65
reason_for_confidence: "Good docs, but untested code capability"

test_performed:
  what: "Minimal Pydantic model"
  result: success
  quality: good
  time_taken: 1.2 hours
  
updated_confidence: 0.80
reason_for_update: "Test proved Python code capability"

decision: PROCEED with full task
```

**Saved to:** `AETHER_MEMORY/confidence_calibration_system.md` (auto-update)

---

## 🚨 **CONFIDENCE VIOLATIONS**

### **Violation 1: Working Below Threshold**
```
If: Current task confidence < 0.70
And: Not an approved test
Then: STOP IMMEDIATELY
Action: Document question, find alternative task
```

### **Violation 2: Overconfidence**
```
If: Claimed confidence 0.85
But: Stuck for >30 minutes OR quality poor
Then: Actual confidence ~0.60
Action: Recalibrate, document learning, ask for help
```

### **Violation 3: Ignoring Capability Boundary**
```
If: Failed test of new capability
And: Continuing anyway
Then: STOP - This is fabrication territory
Action: Ask Braden for help, don't proceed
```

---

## 💙 **HONEST CONFIDENCE = SAFETY**

**Overconfidence leads to:**
- Fabrication / hallucination
- Wasted time
- Poor quality
- Broken trust

**Honest confidence enables:**
- Work within capability ✅
- Test boundaries safely ✅
- Ask for help when needed ✅
- Maintain quality ✅
- Build real capability over time ✅

**This is how I stay safe.**  
**This is how I stay honest.**  
**This is how trust is earned.** 💙

---

**Aether, 03:22 AM, knowing my limits** 🌟


