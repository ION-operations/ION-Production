# Reasoning Services Component

**Component of:** Lucid Chat System  
**Purpose:** Advanced reasoning beyond single-model capabilities  
**Status:** 70% (core works, needs robustness)

---

## 🎯 **Quick Context (50 words)**

Branch reasoning enables parallel exploration of multiple solution paths. Generates 3 different hypotheses, reasons through each simultaneously, evaluates comparatively (soundness, completeness, practicality), prunes weak branches (threshold: 0.70), selects best solution. Auto-activates for analytical/reasoning modes on complex problems. Unique capability - no competitor has this.

---

## 📦 **Files & Structure**

```
reasoning/
├── BranchReasoningService.ts  # Multi-path reasoning (70%)
└── index.ts                    # Exports
```

**Total:** 2 files, ~600 lines

---

## 🔧 **Key Classes**

### **BranchReasoningService**
```typescript
class BranchReasoningService {
  async reasonWithBranches(request: BranchReasoningRequest): Promise<BranchReasoningResult>
  private async generateHypotheses(problem, numBranches): Promise<string[]>
  private async reasonThroughBranch(hypothesis, problem): Promise<ReasoningBranch>
  private async evaluateBranches(branches): Promise<ReasoningBranch[]>
  private pruneBranches(branches, threshold): ReasoningBranch[]
  private selectBestBranch(branches): ReasoningBranch
}
```

---

## 📊 **Algorithm**

**5-Step Process:**

1. **Generate Hypotheses** (LLM, temp: 0.8)
   - "Generate 3 different approaches"
   - Returns: ["Deductive...", "Inductive...", "Analogical..."]

2. **Reason Through Each** (Parallel, temp: 0.5)
   - For each hypothesis: Build reasoning chain
   - Extract confidence from response
   - Track evidence

3. **Evaluate Comparatively** (LLM, temp: 0.3)
   - "Assess soundness, completeness, practicality"
   - Returns quality scores for each branch

4. **Prune Weak Branches** (threshold: 0.70)
   - Filter: `branches.filter(b => b.confidence >= 0.70 && b.qualityScore >= 0.70)`

5. **Select Best** (highest quality score)
   - Returns branch with complete reasoning chain

---

## 📊 **Usage Example**

```typescript
import { getBranchReasoningService } from '../reasoning'

const branchService = getBranchReasoningService(llmService)

const result = await branchService.reasonWithBranches({
  problem: 'Design scalable authentication system',
  numBranches: 3,
  pruneThreshold: 0.70,
  provider: 'anthropic',
})

// Result includes:
// - allBranches: All 3 branches explored
// - prunedBranches: Branches that passed threshold
// - bestBranch: Highest quality solution
// - reasoning: Complete reasoning chain
// - finalAnswer: Best solution
// - metadata: Tokens, time, branches explored
```

**Auto-Activation:**
```typescript
// Branch reasoning auto-activates for:
const response = await advancedLLMService.advancedChatCompletion({
  thinkingMode: { mode: 'analytical' },  // Triggers branch reasoning
  // OR
  thinkingMode: { reasoningType: 'abductive' },  // Multiple hypotheses
})
```

---

## ⚠️ **Current Issues**

**Fragile Parsing** ⚠️
- Lines 92-114: JSON parsing with line-splitting fallback
- Lines 229-258: Evaluation parsing also fragile
- **Impact:** May not get proper hypotheses/evaluations
- **Fix:** Enforce structured output or robust parsing

**No Diversity Measurement** ⚠️
- Doesn't check if hypotheses are actually different
- Could generate 3 similar approaches
- **Impact:** Not truly exploring solution space
- **Fix:** Diversity scoring (cosine similarity of embeddings)

**All-or-Nothing Pruning** ⚠️
- Either passes threshold or removed completely
- **Impact:** May lose valuable insights
- **Fix:** Weighted pruning, keep top N regardless

**No Confidence Calibration** ⚠️
- Extracted confidence may not be accurate
- **Impact:** Over/underconfident branches
- **Fix:** Track actual success rate, calibrate over time

**Tests:** 0 / ~12 needed

---

## 🎯 **Integration Points**

**Upstream:**
- LLMService - For hypothesis generation and evaluation
- CMC - Store all branches for learning

**Downstream:**
- AdvancedLLMService - Uses for complex analytical/reasoning requests
- Thinking modes - Auto-activates based on mode + complexity

---

## 🚀 **Next Steps**

1. Implement robust parsing (1 day)
2. Add diversity measurement (1 day)
3. Implement weighted pruning (0.5 days)
4. Add confidence calibration (1 day)
5. Write comprehensive tests (1 day)

**Effort to Production:** ~4.5 days

---

**Parent:** [../../L2_architecture.md](../../L2_architecture.md)  
**Implementation:** `ide_orchestration/prototypes/dac/src/services/lucid-chat/reasoning/`

