# Research Brief: Program-Level Budget Governance

**Phase:** 3 of 8  
**Priority:** High (10-Day "Ship It Harder")  
**Status:** Research In Progress  
**Date:** 2025-11-07

---

## 🎯 **Research Objective**

**Goal:** Research and document how to extend APOE per-step budgets to program-level envelopes (tokens/latency/$/I/O) with breach policies, rolling windows, and VIF confidence integration.

**Key Questions:**
1. How do per-step budgets aggregate to program/epic level?
2. What breach policies are needed (WARN/ABSTAIN/PASS semantics)?
3. How do rolling windows work for budget tracking?
4. How does budget breach history affect VIF confidence?
5. How do budget ledgers integrate with CMC and SEG?

---

## 📊 **Current State Analysis**

### **What Exists in AIM-OS:**

**1. APOE Budget System**
- ✅ Per-step budgets: Token, Time, Tool budgets
- ✅ Budget tracking: Token and time tracking working (70% implemented)
- ✅ Budget enforcement: Steps blocked if budget exceeded
- ✅ Budget gates: Budget gates exist and enforced
- ❌ **Missing:** Program-level aggregation
- ❌ **Missing:** Breach policies (WARN/ABSTAIN/PASS)
- ❌ **Missing:** Rolling windows
- ❌ **Missing:** $ cost tracking
- ❌ **Missing:** VIF confidence integration

**2. Budget Model:**
```python
class Budget(BaseModel):
    token_limit: Optional[int] = None
    time_limit_seconds: Optional[float] = None
    tool_call_limit: Optional[int] = None
    tokens_consumed: int = 0
    time_elapsed_seconds: float = 0.0
    tool_calls_made: int = 0
```

**3. Budget Enforcement:**
- Budget checked before step execution
- Budget monitored during execution
- Execution halted if budget exceeded

---

## 🔍 **Integration Analysis**

### **Program-Level Budget Aggregation:**

**Current Flow:**
```
Plan → Steps → Per-Step Budgets → Budget Enforcement → Execution
```

**Enhanced Flow:**
```
Plan → Steps → Per-Step Budgets → Aggregate to Program Level ← NEW
                                              ↓
                                    Program Budget Envelope
                                              ↓
                                    Breach Policy Check ← NEW
                                              ↓
                                    Rolling Window Tracking ← NEW
                                              ↓
                                    VIF Confidence Adjustment ← NEW
                                              ↓
                                    Budget Enforcement → Execution
```

### **Program Budget Envelope:**

```python
class ProgramBudgetEnvelope(BaseModel):
    """Program-level budget envelope"""
    program_id: str
    epic_id: Optional[str] = None
    phase_id: Optional[str] = None
    
    # Budget limits (aggregated from steps)
    token_limit: int
    time_limit_seconds: float
    cost_limit_dollars: float  # NEW
    io_limit_mb: float  # NEW
    
    # Current consumption
    tokens_consumed: int = 0
    time_elapsed_seconds: float = 0.0
    cost_dollars: float = 0.0  # NEW
    io_mb: float = 0.0  # NEW
    
    # Rolling windows
    rolling_windows: Dict[str, RollingWindow] = Field(default_factory=dict)
    
    # Breach history
    breach_history: List[BudgetBreach] = Field(default_factory=list)
    
    def aggregate_from_steps(self, steps: List[Step]) -> None:
        """Aggregate budgets from plan steps"""
        self.token_limit = sum(step.budget.token_limit or 0 for step in steps)
        self.time_limit_seconds = sum(step.budget.time_limit_seconds or 0.0 for step in steps)
        # Cost and IO calculated from API calls and data transfers
    
    def check_breach_policy(self) -> BreachPolicyResult:
        """Check breach policy based on history"""
        recent_breaches = self.get_recent_breaches(window_hours=24)
        
        if len(recent_breaches) == 0:
            return BreachPolicyResult(action="PASS", confidence_penalty=0.0)
        elif len(recent_breaches) == 1:
            return BreachPolicyResult(action="WARN", confidence_penalty=0.05)
        elif len(recent_breaches) == 2:
            return BreachPolicyResult(action="ABSTAIN", confidence_penalty=0.10)
        else:
            return BreachPolicyResult(action="FAIL", confidence_penalty=0.20)
```

### **Rolling Window Tracking:**

```python
class RollingWindow(BaseModel):
    """Rolling window for budget tracking"""
    window_type: str  # "24h", "7d", "30d"
    start_time: datetime
    end_time: datetime
    
    # Consumption in window
    tokens_consumed: int = 0
    time_elapsed_seconds: float = 0.0
    cost_dollars: float = 0.0
    io_mb: float = 0.0
    
    # Breach count
    breach_count: int = 0
    
    def update(self, consumption: BudgetConsumption) -> None:
        """Update window with new consumption"""
        # Remove old data outside window
        self.prune_old_data()
        
        # Add new consumption
        self.tokens_consumed += consumption.tokens
        self.time_elapsed_seconds += consumption.time_seconds
        self.cost_dollars += consumption.cost_dollars
        self.io_mb += consumption.io_mb
        
        # Check for breach
        if self.is_breached():
            self.breach_count += 1
```

### **VIF Confidence Integration:**

```python
def adjust_confidence_for_budget_breaches(
    base_confidence: float,
    breach_history: List[BudgetBreach]
) -> float:
    """Adjust confidence based on budget breach history"""
    
    # Calculate breach penalty
    recent_breaches = [b for b in breach_history if b.is_recent(hours=24)]
    breach_penalty = len(recent_breaches) * 0.05  # 5% per breach
    
    # Calculate rolling window penalty
    rolling_penalty = 0.0
    for window in breach_history.rolling_windows.values():
        if window.breach_count > 0:
            rolling_penalty += window.breach_count * 0.02  # 2% per window breach
    
    # Adjust confidence
    adjusted_confidence = base_confidence - breach_penalty - rolling_penalty
    
    # Clamp to valid range
    return max(0.0, min(1.0, adjusted_confidence))
```

---

## 🏗️ **Implementation Approach**

### **Step 1: Extend Budget Model**

1. **Add Cost Tracking:**
   - API cost per call
   - Compute cost per token
   - Storage cost per MB
   - Network cost per MB

2. **Add IO Tracking:**
   - Data read/write volumes
   - Network transfer volumes
   - Storage operations

3. **Add Program-Level Aggregation:**
   - Aggregate step budgets to program level
   - Track consumption across steps
   - Calculate remaining budget

### **Step 2: Implement Breach Policies**

1. **Breach Policy Logic:**
   - First breach: WARN (continue, flag)
   - Second breach: ABSTAIN (escalate, reduce confidence)
   - Third+ breach: FAIL (block, significant confidence penalty)

2. **Breach History Tracking:**
   - Store breach events in CMC
   - Link to SEG evidence
   - Track breach patterns

### **Step 3: Implement Rolling Windows**

1. **Window Types:**
   - 24-hour window
   - 7-day window
   - 30-day window

2. **Window Management:**
   - Prune old data
   - Update consumption
   - Track breach counts

### **Step 4: Integrate with VIF**

1. **Confidence Adjustment:**
   - Calculate breach penalties
   - Adjust confidence scores
   - Update confidence bands

2. **VIF Witness Enhancement:**
   - Include budget breach history
   - Include breach policy results
   - Include confidence adjustments

---

## 📋 **Operational Examples**

### **Example 1: Program Budget Aggregation**

```python
# Create plan with multiple steps
plan = APOEPlan.parse("""
pipeline TestPipeline {
  step step1 {
    budget { tokens: 1000, time: 10 }
  }
  step step2 {
    budget { tokens: 2000, time: 20 }
  }
  step step3 {
    budget { tokens: 1500, time: 15 }
  }
}
""")

# Aggregate to program level
program_budget = ProgramBudgetEnvelope(program_id=plan.id)
program_budget.aggregate_from_steps(plan.steps)

# Results
print(f"Program token limit: {program_budget.token_limit}")  # 4500
print(f"Program time limit: {program_budget.time_limit_seconds}s")  # 45s
```

### **Example 2: Breach Policy Check**

```python
# Check breach policy
breach_result = program_budget.check_breach_policy()

# Results
print(f"Action: {breach_result.action}")  # WARN/ABSTAIN/FAIL
print(f"Confidence penalty: {breach_result.confidence_penalty}")  # 0.05, 0.10, 0.20

# Adjust VIF confidence
base_confidence = 0.85
adjusted_confidence = base_confidence - breach_result.confidence_penalty
print(f"Adjusted confidence: {adjusted_confidence}")  # 0.80 (if WARN)
```

---

## 🎯 **Success Criteria**

1. ✅ **Program Budget Envelopes:** Aggregation from steps to program/epic level
2. ✅ **Breach Policies:** WARN/ABSTAIN/FAIL semantics implemented
3. ✅ **Rolling Windows:** 24h/7d/30d window tracking
4. ✅ **Cost Tracking:** $ cost tracking for APIs/compute/storage
5. ✅ **VIF Integration:** Confidence adjustment based on breach history
6. ✅ **CMC Integration:** Budget breach history stored in CMC
7. ✅ **SEG Integration:** Budget breaches linked to SEG evidence
8. ✅ **Tests:** Comprehensive tests for budget governance

---

**Status:** Research Brief Created ✅  
**Next:** Integration Analysis 💙

