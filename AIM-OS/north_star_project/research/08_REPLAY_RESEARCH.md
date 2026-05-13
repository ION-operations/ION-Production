# Research Brief: Deterministic Replay & Operational Snapshots

**Phase:** 8 of 8  
**Priority:** High (10-Day "Ship It Harder")  
**Status:** Research In Progress  
**Date:** 2025-11-07

---

## 🎯 **Research Objective**

**Goal:** Research and document how to implement deterministic replay recipes as standard artifacts (inputs, plan hash, gate outcomes, evidence IDs), with one-command replay bundles and gates that fail if replay bundle missing.

**Key Questions:**
1. What constitutes a complete replay recipe?
2. How are replay recipes generated and stored?
3. How does one-command replay work?
4. How do replay gates enforce artifact requirements?
5. How do replay recipes integrate with VIF, CMC, and APOE?

---

## 📊 **Current State Analysis**

### **What Exists in AIM-OS:**

**1. VIF Replay Component**
- ✅ Replay component exists (`packages/vif/replay.py`)
- ✅ Replay seed stored in VIF witness
- ✅ Context snapshots for replay
- ✅ Replay theory documented
- ❌ **Missing:** Complete implementation (25% complete)
- ❌ **Missing:** Replay recipe standard format
- ❌ **Missing:** One-command replay bundle
- ❌ **Missing:** Replay gate enforcement

**2. CMC Snapshots**
- ✅ Snapshot system exists
- ✅ Deterministic snapshot IDs
- ✅ Snapshot replay functionality
- ✅ Bitemporal support

**3. APOE Execution Traces**
- ✅ Execution traces stored
- ✅ Plan execution logged
- ✅ Gate outcomes tracked

---

## 🔍 **Integration Analysis**

### **Replay Recipe Structure:**

```python
class ReplayRecipe(BaseModel):
    """Standard replay recipe format"""
    version: str = "1.0.0"
    recipe_id: str
    
    # Inputs
    plan_id: str
    plan_hash: str  # SHA-256 hash of plan
    plan_content: str  # Full plan content
    
    # Context
    context_snapshot_id: str  # CMC snapshot
    context_atom_ids: List[str]  # Specific atoms used
    
    # Execution Parameters
    execution_seed: int  # Random seed for determinism
    model_id: str
    model_provider: str
    temperature: float
    other_params: Dict[str, Any]
    
    # Gate Outcomes
    gate_outcomes: List[GateOutcome]  # All gate outcomes
    
    # Evidence IDs
    evidence_ids: List[str]  # SEG evidence IDs
    vif_witness_ids: List[str]  # VIF witness IDs
    
    # Outputs
    output_hash: str  # SHA-256 hash of output
    output_content: Optional[str] = None  # Full output (if small)
    
    # Metadata
    created_at: datetime
    created_by: str
    
    def to_bundle(self) -> ReplayBundle:
        """Create one-command replay bundle"""
        return ReplayBundle(
            recipe=self,
            replay_script=self.generate_replay_script(),
            dependencies=self.collect_dependencies()
        )
```

### **One-Command Replay Bundle:**

```python
class ReplayBundle(BaseModel):
    """One-command replay bundle"""
    recipe: ReplayRecipe
    replay_script: str  # Executable script
    dependencies: Dict[str, str]  # Required files/data
    
    def generate_replay_script(self) -> str:
        """Generate one-command replay script"""
        script = f"""#!/usr/bin/env python3
\"\"\"One-command replay for recipe {self.recipe.recipe_id}\"\"\"

import sys
from pathlib import Path

# Load recipe
recipe_path = Path(__file__).parent / "recipe.json"
recipe = ReplayRecipe.parse_file(recipe_path)

# Load context snapshot
from packages.cmc import CMCStore
cmc = CMCStore()
context = cmc.replay_snapshot(recipe.context_snapshot_id)

# Reconstruct model
model = load_model(recipe.model_id, recipe.model_provider)

# Set deterministic seed
import random
random.seed(recipe.execution_seed)

# Replay execution
output = model.generate(
    prompt=recipe.plan_content,
    context=context,
    temperature=recipe.temperature,
    **recipe.other_params
)

# Verify output hash
output_hash = sha256(output.encode()).hexdigest()
assert output_hash == recipe.output_hash, "Output hash mismatch!"

print(f"✅ Replay successful: {recipe.recipe_id}")
print(f"Output hash: {output_hash}")
"""
        return script
    
    def save(self, output_dir: Path) -> None:
        """Save replay bundle to directory"""
        # Save recipe
        (output_dir / "recipe.json").write_text(self.recipe.json())
        
        # Save replay script
        (output_dir / "replay.py").write_text(self.replay_script)
        (output_dir / "replay.py").chmod(0o755)
        
        # Save dependencies
        for dep_name, dep_content in self.dependencies.items():
            (output_dir / dep_name).write_text(dep_content)
        
        # Create README
        readme = f"""# Replay Bundle: {self.recipe.recipe_id}

## One-Command Replay

```bash
python replay.py
```

## Recipe Details

- Plan ID: {self.recipe.plan_id}
- Plan Hash: {self.recipe.plan_hash}
- Context Snapshot: {self.recipe.context_snapshot_id}
- Model: {self.recipe.model_id}
- Created: {self.recipe.created_at}

## Verification

The replay script will:
1. Load the recipe
2. Reconstruct the context
3. Replay execution with deterministic seed
4. Verify output hash matches

If output hash matches, replay is successful ✅
"""
        (output_dir / "README.md").write_text(readme)
```

### **Replay Gate:**

```python
class ReplayGate(Gate):
    """Gate that requires replay recipe for production readiness"""
    gate_type: str = "replay"
    
    def evaluate(self, execution_result: ExecutionResult) -> GateOutcome:
        """Evaluate if replay recipe exists"""
        
        # Check if replay recipe exists
        if not execution_result.replay_recipe:
            return GateOutcome.FAIL, "Replay recipe missing"
        
        # Check if replay bundle exists
        if not execution_result.replay_bundle:
            return GateOutcome.FAIL, "Replay bundle missing"
        
        # Verify replay recipe completeness
        recipe = execution_result.replay_recipe
        missing_fields = []
        
        if not recipe.plan_hash:
            missing_fields.append("plan_hash")
        if not recipe.context_snapshot_id:
            missing_fields.append("context_snapshot_id")
        if not recipe.gate_outcomes:
            missing_fields.append("gate_outcomes")
        if not recipe.evidence_ids:
            missing_fields.append("evidence_ids")
        if not recipe.output_hash:
            missing_fields.append("output_hash")
        
        if missing_fields:
            return GateOutcome.FAIL, f"Replay recipe incomplete: {missing_fields}"
        
        # Verify replay bundle is executable
        if not execution_result.replay_bundle.is_executable():
            return GateOutcome.FAIL, "Replay bundle not executable"
        
        return GateOutcome.PASS, "Replay recipe complete"
```

---

## 🏗️ **Implementation Approach**

### **Step 1: Complete VIF Replay Implementation**

1. **Replay Recipe Generation:**
   - Generate replay recipes after execution
   - Store in CMC
   - Link to VIF witnesses

2. **Replay Recipe Validation:**
   - Validate recipe completeness
   - Verify dependencies
   - Check executability

### **Step 2: Create Replay Bundle Format**

1. **Bundle Structure:**
   - Recipe JSON
   - Replay script
   - Dependencies
   - README

2. **One-Command Execution:**
   - Single script execution
   - Automatic dependency loading
   - Output verification

### **Step 3: Integrate Replay Gate**

1. **Gate Enforcement:**
   - Require replay recipe
   - Require replay bundle
   - Fail if missing

2. **Gate Integration:**
   - Integrate with SDF-CVF
   - Integrate with APOE gates
   - Integrate with VIF

---

## 📋 **Operational Examples**

### **Example 1: Generate Replay Recipe**

```python
# Execute plan
execution_result = apoe.execute_plan(plan)

# Generate replay recipe
recipe = ReplayRecipe.create_from_execution(
    execution_result=execution_result,
    plan=plan,
    context_snapshot_id=context_snapshot.id,
    evidence_ids=seg_evidence_ids,
    vif_witness_ids=vif_witness_ids
)

# Create replay bundle
bundle = recipe.to_bundle()
bundle.save(Path("replay_bundles/recipe_123"))

# Verify replay
replay_result = bundle.replay()
assert replay_result.success
assert replay_result.output_hash == recipe.output_hash
```

### **Example 2: One-Command Replay**

```bash
# One-command replay
cd replay_bundles/recipe_123
python replay.py

# Expected output:
# ✅ Replay successful: recipe_123
# Output hash: abc123...
```

---

## 🎯 **Success Criteria**

1. ✅ **Replay Recipe Standard:** Complete recipe format defined
2. ✅ **Replay Bundle:** One-command replay bundle implemented
3. ✅ **Replay Gate:** Gate enforcement for replay recipes
4. ✅ **VIF Integration:** Replay recipes in VIF witnesses
5. ✅ **CMC Integration:** Replay recipes stored in CMC
6. ✅ **APOE Integration:** Replay recipes generated after execution
7. ✅ **Tests:** Comprehensive tests for replay functionality
8. ✅ **Documentation:** Operational examples and runbooks

---

**Status:** Research Brief Created ✅  
**Next:** Integration Analysis 💙

