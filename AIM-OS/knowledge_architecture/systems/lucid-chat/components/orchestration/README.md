# APOE Orchestration Component

**Component of:** Lucid Chat System  
**Purpose:** Execute complex workflows using 8 specialized AI roles  
**Status:** Framework 90%, Implementation 60%

---

## 🎯 **Quick Context (50 words)**

APOE orchestration enables sophisticated multi-step workflows by coordinating 8 specialized AI roles (Planner, Retriever, Reasoner, Verifier, Builder, Critic, Operator, Witness). Each role has specific capabilities, temperature settings, and VIF integration. Workflow executor manages dependencies, budgets, and quality gates. Currently sequential; DAG execution needed for true parallelism.

---

## 📦 **Files & Structure**

```
orchestration/
├── RoleExecutor.ts          # Base class for all roles
├── PlannerExecutor.ts        # Strategic planning (temp: 0.3)
├── RetrieverExecutor.ts      # Knowledge retrieval (temp: 0.1)
├── ReasonerExecutor.ts       # Logical reasoning (temp: 0.2)
├── VerifierExecutor.ts       # Validation (temp: 0.1)
├── BuilderExecutor.ts        # Code generation (temp: 0.5)
├── CriticExecutor.ts         # Quality assessment (temp: 0.4)
├── OperatorExecutor.ts       # System operations (temp: 0.1)
├── WitnessExecutor.ts        # Provenance tracking (temp: 0.0)
├── RoleDispatcher.ts         # Routes tasks to roles
├── WorkflowExecutor.ts       # Executes multi-step workflows
├── BudgetTracker.ts          # Token/time/cost management
└── QualityGates.ts           # VIF κ-gates, SEG consistency
```

**Total:** 13 files, ~2,500 lines

---

## 🔧 **Key Classes**

### **RoleExecutor (Base)**
```typescript
abstract class RoleExecutor {
  abstract async execute(task: string, context?: any): Promise<RoleResult>
  protected async trackExecution(task, result, confidence): Promise<void>
}
```

### **WorkflowExecutor**
```typescript
class WorkflowExecutor {
  async execute(plan: WorkflowPlan): Promise<WorkflowResult>
}
```

### **RoleDispatcher**
```typescript
class RoleDispatcher {
  dispatch(role: RoleType): RoleExecutor
}
```

---

## 📊 **Usage Example**

```typescript
import { getAdvancedLLMService } from '../llm/AdvancedLLMService'

const service = getAdvancedLLMService()

const response = await service.advancedChatCompletion({
  provider: 'anthropic',
  messages: [{ role: 'user', content: 'Build authentication system' }],
  apoe: {
    useAPOE: true,
    roles: [
      { role: 'planner' },
      { role: 'retriever' },
      { role: 'reasoner' },
      { role: 'builder' },
      { role: 'critic' },
    ],
    budget: { tokens: 10000, time: 60 },
  },
})

// Automatically:
// 1. Planner breaks down into subtasks
// 2. Retriever gets relevant examples from HHNI
// 3. Reasoner designs approach logically
// 4. Builder generates implementation
// 5. Critic reviews quality
```

---

## ⚠️ **Current Status**

**Working:**
- ✅ All 8 role executors defined
- ✅ Sequential workflow execution
- ✅ Role dispatcher routing
- ✅ Basic CMC integration

**Not Working:**
- ❌ DAG execution (only sequential, needs topological sort)
- ❌ Budget tracking (placeholder, needs token counting)
- ❌ Quality gates (placeholder, needs VIF/SEG integration)
- ❌ Error recovery (no retry logic)

**Tests:** 0 / ~50 needed

---

## 🎯 **Integration Points**

**Upstream (Uses):**
- LLMService - For role execution
- CMC - Store execution traces
- HHNI - Retriever role queries
- VIF - Quality gates, confidence tracking
- SEG - Consistency checking

**Downstream (Used By):**
- AdvancedLLMService - Orchestrates complex requests
- Thinking modes - Auto-configure roles per mode

---

## 🚀 **Next Steps**

1. Implement DAG execution with topological sort (2 days)
2. Implement budget tracking with tiktoken (1 day)
3. Implement quality gates with VIF/SEG (2 days)
4. Add error recovery and retry logic (1 day)
5. Write comprehensive tests (3 days)

**Effort to Production:** ~9 days

---

**Parent:** [../../L2_architecture.md](../../L2_architecture.md)  
**Implementation:** `ide_orchestration/prototypes/dac/src/services/lucid-chat/orchestration/`

