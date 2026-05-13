# MCP Tools Enhancement: create_plan APOE Integration
**Created:** 2025-11-01  
**Objective:** OBJ-07 - MCP Tools Enhancement  
**Status:** Planning → Implementation  
**Priority:** HIGH (Core System Integration)

---

## 🎯 **EXECUTIVE SUMMARY**

**Goal:** Replace placeholder `create_plan` implementation with real APOE integration, enabling true orchestration capabilities through MCP.

**Current State:**
- **Current:** Returns static 3-step plan (lines 2002-2040 in lucid_mcp_server.py)
- **Target:** Real APOE plan creation with ACL parsing or goal-to-plan generation
- **Impact:** Enables orchestration workflows via MCP interface

**Confidence:** 0.85  
**Estimated Time:** 8-12 hours  
**Dependencies:** APOE system (90% complete, production-ready)

---

## 📊 **CURRENT IMPLEMENTATION ANALYSIS**

### **Current Code (Placeholder):**
```python
def create_plan(self, args: Dict[str, Any]) -> Dict[str, Any]:
    """Create an execution plan using APOE"""
    goal = args.get("goal", "")
    context = args.get("context", "")
    priority = args.get("priority", "medium")
    
    # Returns static 3-step plan
    plan = {
        "goal": goal,
        "steps": [
            {"id": "step_1", "description": f"Analyze goal: {goal}", "status": "pending"},
            {"id": "step_2", "description": f"Execute plan for: {goal}", "status": "pending"},
            {"id": "step_3", "description": f"Validate results for: {goal}", "status": "pending"}
        ]
    }
```

### **Issues:**
- ❌ No real APOE integration
- ❌ No ACL parsing support
- ❌ No dependency resolution
- ❌ No role assignment
- ❌ No budget tracking
- ❌ No gate validation
- ❌ No execution capability

---

## 🗺️ **TARGET IMPLEMENTATION**

### **API Design:**

**Input Parameters:**
- `goal` (required): Goal description
- `context` (optional): Additional context
- `priority` (optional): "low" | "medium" | "high" | "critical" (default: "medium")
- `acl_text` (optional): ACL source code (if provided, parse ACL instead of generating)
- `execute` (optional): Boolean - execute plan immediately (default: False)
- `store_in_cmc` (optional): Boolean - persist plan in CMC (default: True)

**Output Format:**
```json
{
  "success": true,
  "plan": {
    "name": "plan_name",
    "goal": "goal description",
    "priority": "medium",
    "roles": {...},
    "steps": [...],
    "dependencies": {...},
    "gates": [...],
    "created_at": "ISO timestamp"
  },
  "plan_id": "uuid",
  "execution_result": {...}  // if execute=true
}
```

---

## 🔧 **IMPLEMENTATION STRATEGY**

### **Phase 1: ACL Parsing Support**

**When `acl_text` provided:**
1. Import `ACLParser` from `apoe.acl_parser`
2. Parse ACL text using `ACLParser.parse()`
3. Return ExecutionPlan as JSON-serializable dict
4. Handle parse errors gracefully

**Code Structure:**
```python
if acl_text:
    try:
        from apoe.acl_parser import ACLParser
        parser = ACLParser()
        execution_plan = parser.parse(acl_text)
        # Convert ExecutionPlan to dict for response
        return self._plan_to_dict(execution_plan)
    except ValueError as e:
        return {"error": f"ACL parse error: {str(e)}"}
```

### **Phase 2: Goal-to-Plan Generation**

**When `acl_text` NOT provided:**
1. Generate simple ExecutionPlan from goal description
2. Create 3-5 steps based on goal analysis
3. Assign appropriate roles (PLANNER, BUILDER, VERIFIER)
4. Set up dependencies (sequential or parallel)
5. Add basic budgets and gates

**Goal Analysis Approach:**
- Parse goal description for keywords
- Determine complexity (simple → 3 steps, complex → 5 steps)
- Assign roles based on task type:
  - Planning tasks → PLANNER
  - Building tasks → BUILDER
  - Verification tasks → VERIFIER
  - Retrieval tasks → RETRIEVER

**Code Structure:**
```python
else:
    # Generate plan from goal
    plan_name = f"plan_{goal[:20].replace(' ', '_').lower()}"
    execution_plan = self._generate_plan_from_goal(
        goal=goal,
        context=context,
        priority=priority,
        plan_name=plan_name
    )
    return self._plan_to_dict(execution_plan)
```

### **Phase 3: Execution Support**

**When `execute=true` provided:**
1. Import `PlanExecutor` from `apoe.executor`
2. Register role handlers (if available)
3. Execute plan using `PlanExecutor.execute()`
4. Return execution results

**Code Structure:**
```python
if execute and execution_plan:
    try:
        from apoe.executor import PlanExecutor
        executor = PlanExecutor()
        # Register handlers if available
        result = executor.execute(execution_plan)
        return {
            **plan_response,
            "execution_result": self._result_to_dict(result)
        }
    except Exception as e:
        return {"error": f"Execution failed: {str(e)}"}
```

### **Phase 4: CMC Persistence**

**When `store_in_cmc=true` (default):**
1. Store plan as atom in CMC
2. Use tags: `{"type": "execution_plan", "priority": priority}`
3. Store plan JSON in metadata
4. Return atom_id in response

**Code Structure:**
```python
if store_in_cmc and self.memory:
    try:
        atom_create = AtomCreate(
            modality="plan",
            content=AtomContent(inline=json.dumps(plan_dict)),
            tags={"type": "execution_plan", "priority": priority},
            metadata={"plan_id": plan_id, "goal": goal, "created_at": datetime.now().isoformat()}
        )
        atom = self.memory.create_atom(atom_create)
        plan_response["atom_id"] = atom.id
    except Exception as e:
        log(f"Warning: Failed to store plan in CMC: {e}")
```

---

## 📋 **HELPER FUNCTIONS NEEDED**

### **1. `_plan_to_dict(execution_plan: ExecutionPlan) -> Dict`**
Convert ExecutionPlan Pydantic model to JSON-serializable dict.

### **2. `_generate_plan_from_goal(goal, context, priority, plan_name) -> ExecutionPlan`**
Generate ExecutionPlan from goal description using simple heuristics.

### **3. `_result_to_dict(result: ExecutionResult) -> Dict`**
Convert ExecutionResult to JSON-serializable dict.

### **4. `_analyze_goal_complexity(goal: str) -> int`**
Analyze goal to determine number of steps needed (3-5).

### **5. `_assign_roles_for_goal(goal: str) -> List[RoleType]`**
Determine which roles are needed based on goal keywords.

---

## ✅ **SUCCESS CRITERIA**

1. ✅ `create_plan` accepts goal/context/priority and returns ExecutionPlan
2. ✅ Supports ACL parsing when `acl_text` provided
3. ✅ Generates ExecutionPlan from goal when no ACL provided
4. ✅ Returns structured plan with steps, roles, dependencies
5. ✅ Optionally executes plan when `execute=true`
6. ✅ Persists plan in CMC when `store_in_cmc=true`
7. ✅ Comprehensive error handling
8. ✅ Logs all operations

---

## 🧪 **TESTING PLAN**

### **Unit Tests:**
1. Test ACL parsing with valid ACL
2. Test ACL parsing with invalid ACL (error handling)
3. Test goal-to-plan generation (simple goal)
4. Test goal-to-plan generation (complex goal)
5. Test execution when `execute=true`
6. Test CMC persistence when `store_in_cmc=true`
7. Test error handling for missing dependencies

### **Integration Tests:**
1. Test full workflow: create plan → execute → store
2. Test ACL plan → execution
3. Test generated plan → execution

---

## 📊 **METRICS & MONITORING**

**Track:**
- Plans created per day
- ACL vs generated plans ratio
- Execution success rate
- Average plan complexity (steps count)
- CMC storage success rate

---

## 🚀 **IMPLEMENTATION STEPS**

1. ✅ Create detailed plan document (this file)
2. ⏳ Implement ACL parsing support
3. ⏳ Implement goal-to-plan generation
4. ⏳ Implement execution support
5. ⏳ Implement CMC persistence
6. ⏳ Add comprehensive error handling
7. ⏳ Write unit tests
8. ⏳ Test integration
9. ⏳ Update documentation

---

**Status:** Ready for implementation  
**Next:** Begin Phase 1 - ACL Parsing Support

