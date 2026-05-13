# Phase 1: PLIx→ACL Compiler - Architecture Design

**Date:** 2025-01-27  
**Status:** ✅ **COMPLETE**  
**Time:** ~30 minutes  
**Confidence:** 0.92

---

## 🎯 **COMPILER ARCHITECTURE**

### **Core Components:**

```
┌─────────────────────────────────────────────────────────────┐
│                    PLIxToACLCompiler                         │
│  Main orchestrator - compiles PLIx intent to ACL plan        │
└─────────────────────────────────────────────────────────────┘
                            │
                ┌───────────┼───────────┬────────────┐
                ↓           ↓           ↓            ↓
        ┌───────────┐  ┌────────────┐  ┌────────┐  ┌──────────┐
        │  Purity   │  │Compensation│  │ Retry  │  │  Parser  │
        │  Checker  │  │ Generator  │  │  Gen   │  │  Bridge  │
        └───────────┘  └────────────┘  └────────┘  └──────────┘
              │              │              │            │
              └──────────────┴──────────────┴────────────┘
                            ↓
                    ┌──────────────┐
                    │   ACL Plan   │
                    └──────────────┘
```

### **Component Interfaces:**

**1. PLIxToACLCompiler (Main)**
```python
def compile(plix_intent: PLIxIntent) -> ExecutionPlan
def validate_purity(contract: Contract) -> bool
def map_steps(plan: Plan) -> List[Step]
def map_gates(contract: Contract) -> List[Gate]
```

**2. PurityChecker**
```python
def check(constraint: Constraint) -> PurityResult
def check_expression(expr: Expression) -> PurityResult
def get_effects(constraint: Constraint) -> Set[Effect]
```

**3. CompensationGenerator**
```python
def generate(compensation: Compensation) -> Dict[str, Any]
def resolve_params(params: Dict) -> Dict
```

**4. RetryPolicyGenerator**
```python
def generate(retry: RetryPolicy) -> Dict[str, Any]
def validate_policy(policy: RetryPolicy) -> ValidationResult
```

**5. PLIxParserBridge**
```python
def parse(text: str) -> PLIxIntent  # Already implemented ✅
```

---

## 🔧 **COMPILATION FLOW**

```python
# Step 1: Parse PLIx text
parser_bridge = PLIxParserBridge()
plix_intent = parser_bridge.parse(plix_text)

# Step 2: Validate purity
compiler = PLIxToACLCompiler()
compiler._validate_purity(plix_intent.contract)

# Step 3: Map components
acl_plan = ExecutionPlan(
    name=compiler._generate_plan_name(plix_intent),
    roles=compiler._map_roles(plix_intent),
    steps=compiler._map_steps(plix_intent.plan),
    gates=compiler._map_contract_gates(plix_intent.contract)
)

# Step 4: Return compiled plan
return acl_plan
```

---

## 📊 **MAPPING STRATEGY**

### **PLIx → ACL Construct Mappings:**

| PLIx | ACL | Handler |
|------|-----|---------|
| `requires con:X` | `GATE precondition: X` | `_map_contract_gates()` |
| `ensures con:Y` | `GATE postcondition: Y` | `_map_contract_gates()` |
| `depends_on: [a, b]` | `REQUIRES a, b` | `_map_dependencies()` |
| `compensate s -> Act()` | `compensation: {...}` | `CompensationGenerator` |
| `retry: exponential(...)` | `retry_policy: {...}` | `RetryPolicyGenerator` |
| `confidence: 0.95` | `GATE confidence >= 0.95` | `_create_step_gates()` |

---

## ✅ **ARCHITECTURE COMPLETE**

**Design validated:**
- ✅ Clear component responsibilities
- ✅ Clean interfaces
- ✅ Testable components
- ✅ Extensible design

**Ready for implementation!**

**Next:** Step 1.2 - Implement PurityChecker 💙

