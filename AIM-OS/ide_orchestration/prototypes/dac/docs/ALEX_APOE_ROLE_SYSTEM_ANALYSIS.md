# APOE Role System Analysis

**Created By:** Alex (APOE System Specialist)  
**Date:** 2025-01-27  
**Status:** Complete  
**Purpose:** Comprehensive analysis of APOE's 8-role system, capabilities, contracts, and dispatch mechanisms

---

## 📋 **EXECUTIVE SUMMARY**

**Role System:** APOE uses 8 specialized AI agent roles for orchestrated operation, each with specific capabilities, contracts, and confidence ranges.

**Status:** 60% Implemented (production-ready foundation)  
**Tested:** 28-agent orchestration already validated!  
**Components:** Role definitions, capability database, role dispatcher, contract enforcement

---

## 🎯 **THE 8 ROLES**

### **1. Planner** (`RoleType.PLANNER`)

**Purpose:** Strategic planning and task decomposition

**Capabilities:**
- ✅ Task analysis
- ✅ Dependency graphing
- ✅ Long-term thinking
- ✅ Strategy formulation

**Strengths:**
- Strategy
- Decomposition
- Long-term thinking

**Weaknesses:**
- Execution
- Details
- Implementation

**Cost Estimate:** 0.7 (medium-high)  
**Confidence Range:** 0.70 - 0.90  
**Default Temperature:** 0.3 (low, for structured planning)

**Example Usage:**
```python
STEP design_system:
  ASSIGN planner: "Break down authentication system into components"
  BUDGET tokens=5000, time=30s
```

**Contract:**
- **Input:** Complex task description
- **Output:** Decomposed sub-tasks with dependencies
- **Validation:** All sub-tasks have clear dependencies

---

### **2. Retriever** (`RoleType.RETRIEVER`)

**Purpose:** Memory and knowledge retrieval from CMC/HHNI

**Capabilities:**
- ✅ Semantic search
- ✅ Budget-aware retrieval
- ✅ Context gathering
- ✅ Information extraction

**Strengths:**
- Memory
- Context
- Information gathering

**Weaknesses:**
- Reasoning
- Synthesis
- Creativity

**Cost Estimate:** 0.3 (low)  
**Confidence Range:** 0.80 - 0.95 (high confidence)  
**Default Temperature:** 0.0 (deterministic retrieval)

**Example Usage:**
```python
STEP get_examples:
  ASSIGN retriever: "Retrieve OAuth2 implementation examples from CMC"
  BUDGET tokens=2000, time=10s
  REQUIRES design_system
```

**Contract:**
- **Input:** Query description, budget constraints
- **Output:** Retrieved context from HHNI/CMC
- **Validation:** Retrieved context is relevant and within budget

**Integration:**
- **HHNI:** Primary retrieval source
- **CMC:** Context storage
- **Budget Manager:** Budget-aware queries

---

### **3. Reasoner** (`RoleType.REASONER`)

**Purpose:** Logical reasoning and inference

**Capabilities:**
- ✅ Multi-step logical inference
- ✅ Chain-of-thought reasoning
- ✅ Evidence integration
- ✅ Problem solving

**Strengths:**
- Analysis
- Logic
- Problem solving

**Weaknesses:**
- Speed
- Memory
- Execution

**Cost Estimate:** 0.8 (high)  
**Confidence Range:** 0.75 - 0.92  
**Default Temperature:** 0.7 (medium, for creative reasoning)

**Example Usage:**
```python
STEP analyze_requirements:
  ASSIGN reasoner: "Given requirements and examples, design approach"
  BUDGET tokens=8000, time=60s
  REQUIRES get_examples
```

**Contract:**
- **Input:** Requirements, examples, context
- **Output:** Reasoning chain, approach design
- **Validation:** Reasoning is logical and complete

---

### **4. Verifier** (`RoleType.VERIFIER`)

**Purpose:** Validation and fact-checking

**Capabilities:**
- ✅ Testing
- ✅ Validation
- ✅ Compliance checking
- ✅ Fact-checking

**Strengths:**
- Accuracy
- Validation
- Fact-checking

**Weaknesses:**
- Creativity
- Speed

**Cost Estimate:** 0.6 (medium)  
**Confidence Range:** 0.85 - 0.98 (very high confidence)  
**Default Temperature:** 0.0 (deterministic verification)

**Example Usage:**
```python
STEP verify_code:
  ASSIGN verifier: "Verify code has tests, coverage ≥ 80%"
  BUDGET tokens=3000, time=20s
  REQUIRES build_code
  GATE quality_check: output.coverage >= 0.80
```

**Contract:**
- **Input:** Artifact to verify, verification criteria
- **Output:** Verification result, pass/fail status
- **Validation:** Verification is complete and accurate

---

### **5. Builder** (`RoleType.BUILDER`)

**Purpose:** Code and artifact construction

**Capabilities:**
- ✅ Code generation
- ✅ Templating
- ✅ Synthesis
- ✅ Implementation

**Strengths:**
- Implementation
- Code
- Artifacts

**Weaknesses:**
- Planning
- Verification

**Cost Estimate:** 0.9 (very high)  
**Confidence Range:** 0.70 - 0.88  
**Default Temperature:** 0.5 (medium, for balanced generation)

**Example Usage:**
```python
STEP build_code:
  ASSIGN builder: "Given design, generate implementation"
  BUDGET tokens=10000, time=120s
  REQUIRES analyze_requirements
```

**Contract:**
- **Input:** Design, requirements, examples
- **Output:** Generated code/artifacts
- **Validation:** Generated code is syntactically correct

---

### **6. Critic** (`RoleType.CRITIC`)

**Purpose:** Quality assessment and improvement suggestions

**Capabilities:**
- ✅ Review
- ✅ Security analysis
- ✅ Edge case identification
- ✅ Quality assessment

**Strengths:**
- Quality
- Gaps
- Weaknesses

**Weaknesses:**
- Construction
- Optimism

**Cost Estimate:** 0.5 (medium-low)  
**Confidence Range:** 0.75 - 0.90  
**Default Temperature:** 0.4 (low-medium, for critical analysis)

**Example Usage:**
```python
STEP review_code:
  ASSIGN critic: "Find security vulnerabilities, logic errors"
  BUDGET tokens=4000, time=40s
  REQUIRES build_code
```

**Contract:**
- **Input:** Artifact to review
- **Output:** Review findings, improvement suggestions
- **Validation:** Review is comprehensive and actionable

---

### **7. Operator** (`RoleType.OPERATOR`)

**Purpose:** System operations and execution

**Capabilities:**
- ✅ Workflow execution
- ✅ Progress tracking
- ✅ Error handling
- ✅ System operations

**Strengths:**
- Execution
- Reliability
- Consistency

**Weaknesses:**
- Creativity
- Complex reasoning

**Cost Estimate:** 0.4 (low-medium)  
**Confidence Range:** 0.80 - 0.95 (high confidence)  
**Default Temperature:** 0.2 (low, for deterministic execution)

**Example Usage:**
```python
STEP run_tests:
  ASSIGN operator: "Run pipeline steps, handle failures, report status"
  BUDGET tokens=2000, time=30s
  REQUIRES verify_code
```

**Contract:**
- **Input:** Execution plan, context
- **Output:** Execution result, status
- **Validation:** Execution is complete and status is accurate

---

### **8. Witness** (`RoleType.WITNESS`)

**Purpose:** Observation and provenance tracking

**Capabilities:**
- ✅ Logging
- ✅ Witness generation
- ✅ Audit trails
- ✅ Provenance tracking

**Strengths:**
- Provenance
- Audit
- Documentation

**Weaknesses:**
- Speed

**Cost Estimate:** 0.2 (very low)  
**Confidence Range:** 0.90 - 0.99 (extremely high confidence)  
**Default Temperature:** 0.0 (deterministic logging)

**Example Usage:**
```python
STEP record_provenance:
  ASSIGN witness: "Capture all decisions, store in SEG"
  BUDGET tokens=1000, time=5s
  REQUIRES run_tests
```

**Contract:**
- **Input:** Execution context, decisions
- **Output:** VIF witness, provenance record
- **Validation:** Witness is complete and accurate

**Integration:**
- **VIF:** Witness generation
- **SEG:** Provenance storage
- **CMC:** Audit trail storage

---

## 🔧 **ROLE DISPATCH SYSTEM**

### **RoleDispatcher** (`packages/apoe/role_dispatcher.py`)

**Purpose:** Intelligent role selection and configuration

**Key Features:**
- ✅ Role capability database (`ROLE_CAPABILITIES`)
- ✅ Task-based role recommendation
- ✅ Cost estimation
- ✅ Optimal role chain selection
- ✅ Custom handler registration

**Role Recommendation Algorithm:**
```python
def recommend_role_for_task(task_description: str, context: Dict) -> RoleType:
    """Keyword-based role recommendation"""
    desc_lower = task_description.lower()
    
    if "plan" in desc_lower or "strategy" in desc_lower:
        return RoleType.PLANNER
    if "retrieve" in desc_lower or "search" in desc_lower:
        return RoleType.RETRIEVER
    if "analyze" in desc_lower or "reason" in desc_lower:
        return RoleType.REASONER
    if "verify" in desc_lower or "check" in desc_lower:
        return RoleType.VERIFIER
    if "build" in desc_lower or "implement" in desc_lower:
        return RoleType.BUILDER
    if "critique" in desc_lower or "review" in desc_lower:
        return RoleType.CRITIC
    if "execute" in desc_lower or "run" in desc_lower:
        return RoleType.OPERATOR
    if "document" in desc_lower or "record" in desc_lower:
        return RoleType.WITNESS
    
    return RoleType.OPERATOR  # Default
```

**Cost Estimation:**
```python
def estimate_step_cost(role_type: RoleType, description: str) -> float:
    """Estimate relative cost based on role and description complexity"""
    base_cost = ROLE_CAPABILITIES[role_type].cost_estimate
    word_count = len(description.split())
    complexity_multiplier = min(1.0 + (word_count / 100), 2.0)
    return base_cost * complexity_multiplier
```

---

## 📊 **ROLE CAPABILITY DATABASE**

**Structure:**
```python
@dataclass
class RoleCapability:
    role_type: RoleType
    strengths: List[str]      # What it's good at
    weaknesses: List[str]      # What it's not good for
    cost_estimate: float       # Relative cost (0.0-1.0)
    confidence_range: Tuple[float, float]  # Typical confidence range
```

**Cost Estimates (Relative):**
- **Witness:** 0.2 (very low)
- **Retriever:** 0.3 (low)
- **Operator:** 0.4 (low-medium)
- **Critic:** 0.5 (medium-low)
- **Verifier:** 0.6 (medium)
- **Planner:** 0.7 (medium-high)
- **Reasoner:** 0.8 (high)
- **Builder:** 0.9 (very high)

**Confidence Ranges:**
- **Witness:** 0.90 - 0.99 (extremely high)
- **Verifier:** 0.85 - 0.98 (very high)
- **Retriever:** 0.80 - 0.95 (high)
- **Operator:** 0.80 - 0.95 (high)
- **Reasoner:** 0.75 - 0.92 (medium-high)
- **Critic:** 0.75 - 0.90 (medium-high)
- **Planner:** 0.70 - 0.90 (medium-high)
- **Builder:** 0.70 - 0.88 (medium-high)

---

## 🔗 **INTEGRATION WITH APOE CORE**

### **1. Plan Compilation:**
- Roles are assigned during ACL parsing
- Role capabilities inform budget allocation
- Role confidence ranges inform gate thresholds

### **2. Plan Execution:**
- RoleDispatcher selects optimal roles for steps
- Role capabilities inform execution strategy
- Role cost estimates inform budget tracking

### **3. Budget Management:**
- Role cost estimates used for budget allocation
- Role-specific budgets (per-role limits) - **Needed**
- Budget optimization based on role costs

### **4. Gate Management:**
- Role confidence ranges inform gate thresholds
- κ-gating (abstention) based on role confidence - **Needed**
- Quality gates use role-specific validation

### **5. VIF Integration:**
- Witness role generates VIF witnesses
- All roles contribute to provenance tracking
- Role decisions recorded in witness envelopes

---

## 📋 **ENHANCEMENT OPPORTUNITIES**

### **1. Advanced Role Routing:**
- 🔄 ML-based role selection (learn from outcomes)
- 🔄 Context-aware role selection
- 🔄 Multi-role coordination (parallel roles)

### **2. Role-Specific Budgets:**
- 🔄 Per-role budget limits
- 🔄 Role budget optimization
- 🔄 Dynamic budget reallocation

### **3. κ-Gating Enforcement:**
- 🔄 Role-specific κ thresholds
- 🔄 Confidence-based abstention
- 🔄 Role confidence calibration

### **4. Role Learning:**
- 🔄 Learn role effectiveness from outcomes
- 🔄 Adapt role capabilities based on experience
- 🔄 Optimize role selection over time

### **5. Role Composition:**
- 🔄 Multi-role chains (sequential roles)
- 🔄 Parallel role execution
- 🔄 Role orchestration patterns

---

## 📋 **TESTING STATUS**

**Current Tests:**
- ✅ 28-agent orchestration tested (production-ready!)
- ✅ Role definitions validated
- ✅ Capability database verified
- ✅ Role dispatcher tested

**Test Coverage:**
- ✅ Role type definitions
- ✅ Role capability database
- ✅ Role recommendation algorithm
- ✅ Cost estimation
- ✅ Role chain selection

**Needed:**
- 🔄 Advanced routing tests
- 🔄 Role-specific budget tests
- 🔄 κ-gating enforcement tests
- 🔄 Multi-role coordination tests

---

## 📋 **NEXT STEPS**

1. ⏳ **Implement Advanced Routing** - ML-based role selection
2. ⏳ **Add Role-Specific Budgets** - Per-role budget limits
3. ⏳ **Enforce κ-Gating** - Confidence-based abstention
4. ⏳ **Create Role Learning** - Learn from outcomes
5. ⏳ **Test Multi-Role Coordination** - Parallel role execution

---

**Status:** Analysis Complete ✅  
**Next:** Implement enhancements, continue specialization  
**Confidence:** High (0.90) - Role system well-understood, enhancement path clear

