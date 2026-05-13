# Integration Analysis: Program-Level Budget Governance

**Phase:** 3 of 8  
**Priority:** High  
**Status:** Analysis Complete  
**Date:** 2025-11-07

---

## 🎯 **Integration Objective**

**Goal:** Integrate program-level budget envelopes with breach policies, rolling windows, and VIF confidence adjustment into APOE budget system and VIF witness generation.

**Key Integration Points:**
1. APOE Budget System → Program-Level Aggregation
2. Budget Breaches → VIF Confidence Adjustment
3. Budget Ledgers → CMC Storage
4. Budget Breaches → SEG Evidence

---

## 🔗 **System Integration Map**

### **APOE Budget System Enhancement**

**Current Budget Flow:**
```
Plan → Steps → Per-Step Budgets → Budget Enforcement → Execution
```

**Enhanced Budget Flow (with Program-Level):**
```
Plan → Steps → Per-Step Budgets → Aggregate to Program Level ← NEW
                                              ↓
                                    Program Budget Envelope
                                              ↓
                                    Breach Policy Check ← NEW
                                              ↓
                                    Rolling Window Update ← NEW
                                              ↓
                                    VIF Confidence Adjustment ← NEW
                                              ↓
                                    Budget Enforcement → Execution
```

---

## 🏗️ **Technical Integration**

### **1. APOE Budget System Enhancement**

**Current Budget Model:**
```python
class Budget(BaseModel):
    token_limit: Optional[int] = None
    time_limit_seconds: Optional[float] = None
    tool_call_limit: Optional[int] = None
    tokens_consumed: int = 0
    time_elapsed_seconds: float = 0.0
    tool_calls_made: int = 0
```

**Enhanced Budget Model (with Program-Level):**
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
        
        # Calculate cost from API calls and compute
        self.cost_limit_dollars = self._calculate_cost_limit(steps)
        
        # Calculate IO from data transfers
        self.io_limit_mb = self._calculate_io_limit(steps)
    
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

**APOE Budget Tracker Enhancement:**
```python
class BudgetTracker:
    """Enhanced budget tracker with program-level aggregation"""
    
    def __init__(self):
        self.program_envelopes: Dict[str, ProgramBudgetEnvelope] = {}
        self.rolling_windows: Dict[str, RollingWindow] = {}
    
    def create_program_envelope(
        self,
        plan: Plan,
        epic_id: Optional[str] = None,
        phase_id: Optional[str] = None
    ) -> ProgramBudgetEnvelope:
        """Create program-level budget envelope from plan"""
        envelope = ProgramBudgetEnvelope(
            program_id=plan.id,
            epic_id=epic_id,
            phase_id=phase_id
        )
        envelope.aggregate_from_steps(plan.steps)
        
        # Initialize rolling windows
        envelope.rolling_windows = {
            "24h": RollingWindow(window_type="24h"),
            "7d": RollingWindow(window_type="7d"),
            "30d": RollingWindow(window_type="30d")
        }
        
        self.program_envelopes[plan.id] = envelope
        return envelope
    
    def track_consumption(
        self,
        program_id: str,
        consumption: BudgetConsumption
    ) -> BudgetBreach:
        """Track consumption and detect breaches"""
        envelope = self.program_envelopes[program_id]
        
        # Update consumption
        envelope.tokens_consumed += consumption.tokens
        envelope.time_elapsed_seconds += consumption.time_seconds
        envelope.cost_dollars += consumption.cost_dollars
        envelope.io_mb += consumption.io_mb
        
        # Update rolling windows
        for window in envelope.rolling_windows.values():
            window.update(consumption)
        
        # Check for breach
        breach = self._check_breach(envelope, consumption)
        if breach:
            envelope.breach_history.append(breach)
            self._store_breach_in_cmc(breach)
            self._link_breach_to_seg(breach)
        
        return breach
```

---

### **2. VIF Confidence Integration**

**VIF Witness Enhancement (with Budget Breach History):**
```python
class VIF(BaseModel):
    # ... existing fields ...
    
    # Budget Breach History (NEW)
    budget_breach_history: List[BudgetBreach] = Field(default_factory=list)
    breach_policy_result: Optional[BreachPolicyResult] = None
    confidence_adjustment: float = 0.0  # Penalty from breaches
    
    @classmethod
    def create_with_budget_breaches(
        cls,
        base_confidence: float,
        breach_history: List[BudgetBreach],
        **kwargs
    ) -> VIF:
        """Create VIF witness with budget breach adjustment"""
        
        # Calculate breach policy result
        breach_policy = BreachPolicy()
        policy_result = breach_policy.evaluate(breach_history)
        
        # Adjust confidence
        adjusted_confidence = base_confidence - policy_result.confidence_penalty
        
        return cls(
            confidence_score=adjusted_confidence,
            budget_breach_history=breach_history,
            breach_policy_result=policy_result,
            confidence_adjustment=policy_result.confidence_penalty,
            # Update confidence band based on adjustment
            confidence_band=ConfidenceBand.from_score(adjusted_confidence),
            **kwargs
        )
```

**Confidence Adjustment Function:**
```python
def adjust_confidence_for_budget_breaches(
    base_confidence: float,
    breach_history: List[BudgetBreach],
    rolling_windows: Dict[str, RollingWindow]
) -> float:
    """Adjust confidence based on budget breach history"""
    
    # Calculate breach penalty
    recent_breaches = [b for b in breach_history if b.is_recent(hours=24)]
    breach_penalty = len(recent_breaches) * 0.05  # 5% per breach
    
    # Calculate rolling window penalty
    rolling_penalty = 0.0
    for window in rolling_windows.values():
        if window.breach_count > 0:
            rolling_penalty += window.breach_count * 0.02  # 2% per window breach
    
    # Adjust confidence
    adjusted_confidence = base_confidence - breach_penalty - rolling_penalty
    
    # Clamp to valid range
    return max(0.0, min(1.0, adjusted_confidence))
```

---

### **3. CMC Integration**

**Budget Breach Storage:**
```python
def store_budget_breach_in_cmc(breach: BudgetBreach) -> Atom:
    """Store budget breach in CMC"""
    atom = cmc_store.store_atom(
        content=breach.to_dict(),
        tags={
            "type": "budget_breach",
            "program_id": breach.program_id,
            "breach_type": breach.breach_type,
            "severity": breach.severity
        },
        metadata={
            "breach_id": breach.id,
            "program_id": breach.program_id,
            "breach_timestamp": breach.timestamp.isoformat(),
            "breach_policy_action": breach.policy_action.value
        }
    )
    return atom
```

---

### **4. SEG Integration**

**Budget Breach Evidence Linking:**
```python
def link_budget_breach_to_seg(
    breach: BudgetBreach,
    program_id: str,
    vif_witness_id: str
) -> List[SEGNode]:
    """Link budget breach to SEG evidence graph"""
    nodes = []
    
    # Create breach node
    breach_node = SEGNode(
        id=f"budget_breach_{breach.id}",
        type="budget_breach",
        data={
            "breach_id": breach.id,
            "program_id": program_id,
            "breach_type": breach.breach_type,
            "breach_timestamp": breach.timestamp.isoformat(),
            "policy_action": breach.policy_action.value,
            "confidence_penalty": breach.confidence_penalty
        },
        links=[
            SEGLink(target_id=program_id, link_type="breaches"),
            SEGLink(target_id=vif_witness_id, link_type="witnessed_by")
        ]
    )
    nodes.append(breach_node)
    
    return nodes
```

---

## 🔄 **Execution Flow Integration**

### **Budget-Aware Plan Execution:**

```python
def execute_plan_with_budget_governance(plan: Plan) -> ExecutionResult:
    """Execute plan with program-level budget governance"""
    
    # 1. Create program budget envelope
    budget_tracker = BudgetTracker()
    envelope = budget_tracker.create_program_envelope(plan)
    
    # 2. Check breach policy before execution
    breach_policy_result = envelope.check_breach_policy()
    
    if breach_policy_result.action == "FAIL":
        return ExecutionResult(
            success=False,
            reason="Budget breach policy violation",
            breach_policy_result=breach_policy_result
        )
    
    # 3. Execute plan with budget tracking
    execution_result = apoe.execute_plan(plan)
    
    # 4. Track consumption
    consumption = BudgetConsumption.from_execution(execution_result)
    breach = budget_tracker.track_consumption(plan.id, consumption)
    
    # 5. Adjust VIF confidence if breach occurred
    if breach:
        base_confidence = execution_result.vif_witness.confidence_score
        adjusted_confidence = adjust_confidence_for_budget_breaches(
            base_confidence,
            envelope.breach_history,
            envelope.rolling_windows
        )
        execution_result.vif_witness.confidence_score = adjusted_confidence
        execution_result.vif_witness.confidence_adjustment = (
            base_confidence - adjusted_confidence
        )
    
    # 6. Store breach in CMC
    if breach:
        store_budget_breach_in_cmc(breach)
    
    # 7. Link breach to SEG
    if breach:
        seg_nodes = link_budget_breach_to_seg(
            breach,
            plan.id,
            execution_result.vif_witness.id
        )
        for node in seg_nodes:
            seg_graph.add_node(node)
    
    return execution_result
```

---

## 🧪 **Testing Integration**

### **Test 1: Program Budget Aggregation**

```python
def test_program_budget_aggregation():
    """Test program-level budget aggregation"""
    
    # Create plan with multiple steps
    plan = APOEPlan.parse("""
    pipeline TestPipeline {
      step step1 {
        budget { tokens: 1000, time: 10 }
      }
      step step2 {
        budget { tokens: 2000, time: 20 }
      }
    }
    """)
    
    # Create program envelope
    budget_tracker = BudgetTracker()
    envelope = budget_tracker.create_program_envelope(plan)
    
    # Assert aggregation
    assert envelope.token_limit == 3000
    assert envelope.time_limit_seconds == 30.0
```

### **Test 2: Breach Policy**

```python
def test_breach_policy():
    """Test breach policy enforcement"""
    
    envelope = ProgramBudgetEnvelope(program_id="test")
    
    # Simulate breaches
    breach1 = BudgetBreach(breach_type="token", timestamp=datetime.now())
    breach2 = BudgetBreach(breach_type="time", timestamp=datetime.now())
    breach3 = BudgetBreach(breach_type="cost", timestamp=datetime.now())
    
    envelope.breach_history = [breach1, breach2, breach3]
    
    # Check breach policy
    policy_result = envelope.check_breach_policy()
    
    # Assert FAIL action
    assert policy_result.action == "FAIL"
    assert policy_result.confidence_penalty == 0.20
```

---

## 📋 **Implementation Checklist**

- [ ] Extend `Budget` model with cost and IO tracking
- [ ] Create `ProgramBudgetEnvelope` class
- [ ] Implement `BudgetTracker` with program-level aggregation
- [ ] Implement `RollingWindow` class
- [ ] Implement `BreachPolicy` class
- [ ] Enhance VIF witness with budget breach fields
- [ ] Implement confidence adjustment function
- [ ] Create CMC storage for budget breaches
- [ ] Create SEG nodes for budget breaches
- [ ] Integrate into APOE execution flow
- [ ] Create integration tests
- [ ] Create operational examples

---

**Status:** Integration Analysis Complete ✅  
**Next:** Implementation Planning 💙

