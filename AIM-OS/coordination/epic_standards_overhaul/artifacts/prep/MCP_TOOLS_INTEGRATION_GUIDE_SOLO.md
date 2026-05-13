# MCP Tools Integration Guide - Phase 1 Enhancements

**Created:** 2025-10-30  
**Agent:** Solo  
**Objective:** Enhance Lexicon's MCP Tools Enhancement Prep with specific integration details  
**Status:** Integration Guide Complete  
**Target:** Phase 1 - Core System Integration  

---

## 🎯 **EXECUTIVE SUMMARY**

**Purpose:** Provide specific code examples, integration patterns, and implementation details for Phase 1 MCP tool enhancements, building on Lexicon's comprehensive prep documents.

**Key Contributions:**
- ✅ **Current Implementation Analysis:** Detailed review of `lucid_mcp_server.py` implementations
- ✅ **Integration Code Examples:** Specific code patterns for each Phase 1 tool
- ✅ **API Reference:** Direct mappings to L3 documentation APIs
- ✅ **Testing Patterns:** Integration test examples
- ✅ **Enhancement Roadmap:** Specific steps for each tool

**Based On:**
- Lexicon's `MCP_TOOLS_ENHANCEMENT_PREP.md` (requirements)
- Lexicon's `MCP_TOOLS_ENHANCEMENT_IMPLEMENTATION_PLAN.md` (roadmap)
- Solo's L3 documentation expansions (CMC, HHNI, VIF, APOE)
- Current `lucid_mcp_server.py` implementation analysis

---

## 📊 **CURRENT IMPLEMENTATION ANALYSIS**

### **Tool 1: `store_memory` → CMC Bitemporal Storage**

**Current Status:** ✅ **PARTIALLY INTEGRATED**
- **Current:** Uses `self.memory.create_atom()` (real CMC integration)
- **Enhancement Needed:** Full bitemporal support, snapshots, embeddings

**Current Code (from `lucid_mcp_server.py:1030-1054`):**
```python
def store_memory(self, args: Dict[str, Any]) -> Dict[str, Any]:
    """Store information in AIM-OS persistent memory"""
    if not self.memory:
        return {"error": "Memory system not initialized"}
    
    content = args.get("content", "")
    tags = args.get("tags", {})
    
    try:
        from cmc_service.models import AtomCreate, AtomContent
        
        atom = self.memory.create_atom(AtomCreate(
            modality="text",
            content=AtomContent(inline=content),
            tags=tags
        ))
        
        return {
            "success": True,
            "atom_id": atom.id,
            "message": f"Stored memory with ID: {atom.id}"
        }
    except Exception as e:
        return {"error": f"Failed to store memory: {str(e)}"}
```

**Enhancement Opportunities:**
1. **Bitemporal Support:** Add `valid_from` and `valid_to` parameters
2. **Snapshot Integration:** Link to CMC snapshot system
3. **Embedding Support:** Generate embeddings for semantic search
4. **Metadata Enhancement:** Support for `snapshot_id`, `witness_id`, `provenance`

**Recommended Enhancement:**
```python
def store_memory(self, args: Dict[str, Any]) -> Dict[str, Any]:
    """Store information in AIM-OS persistent memory with full bitemporal support"""
    if not self.memory:
        return {"error": "Memory system not initialized"}
    
    content = args.get("content", "")
    tags = args.get("tags", {})
    valid_from = args.get("valid_from")  # Optional timestamp
    valid_to = args.get("valid_to")  # Optional timestamp
    snapshot_id = args.get("snapshot_id")  # Optional snapshot reference
    
    try:
        from cmc_service.models import AtomCreate, AtomContent
        from datetime import datetime
        
        # Create atom with bitemporal support
        atom_create = AtomCreate(
            modality="text",
            content=AtomContent(inline=content),
            tags=tags
        )
        
        # Add bitemporal metadata if provided
        if valid_from:
            atom_create.valid_from = datetime.fromisoformat(valid_from)
        if valid_to:
            atom_create.valid_to = datetime.fromisoformat(valid_to)
        
        atom = self.memory.create_atom(atom_create)
        
        # Link to snapshot if provided
        if snapshot_id:
            # Store snapshot reference in atom metadata
            self.memory.update_atom_metadata(atom.id, {"snapshot_id": snapshot_id})
        
        # Generate embedding for HHNI indexing (if HHNI available)
        if self.hhni_index:
            try:
                from hhni.indexer import build_hhni_for_atom
                build_hhni_for_atom(atom, self.hhni_index)
            except Exception as e:
                log(f"Warning: Failed to index atom in HHNI: {e}")
        
        return {
            "success": True,
            "atom_id": atom.id,
            "valid_from": atom.valid_from.isoformat() if hasattr(atom, 'valid_from') else None,
            "valid_to": atom.valid_to.isoformat() if hasattr(atom, 'valid_to') else None,
            "snapshot_id": snapshot_id,
            "message": f"Stored memory with ID: {atom.id} (bitemporal enabled)"
        }
    except Exception as e:
        return {"error": f"Failed to store memory: {str(e)}"}
```

**API Reference:** `knowledge_architecture/systems/cmc/L3_detailed.md` (lines 200-400)

---

### **Tool 2: `retrieve_memory` → HHNI Semantic Search**

**Current Status:** ✅ **PARTIALLY INTEGRATED**
- **Current:** Attempts HHNI semantic search, falls back to simple text search
- **Enhancement Needed:** Full HHNI integration, DVNS physics, RS-Lift optimization

**Current Code (from `lucid_mcp_server.py:1131-1231`):**
```python
def retrieve_memory(self, args: Dict[str, Any]) -> Dict[str, Any]:
    """Search and retrieve memories from AIM-OS using HHNI semantic search"""
    # ... HHNI attempt with fallback ...
```

**Enhancement Opportunities:**
1. **Full HHNI Integration:** Use `TwoStageRetriever` with proper configuration
2. **DVNS Physics:** Enable DVNS optimization for retrieval
3. **RS-Lift Tracking:** Track and report RS-Lift metrics
4. **Budget Management:** Integrate `TokenBudgetManager` for context fitting

**Recommended Enhancement:**
```python
def retrieve_memory(self, args: Dict[str, Any]) -> Dict[str, Any]:
    """Search and retrieve memories using full HHNI semantic search with DVNS physics"""
    if not self.memory:
        return {"error": "Memory system not initialized"}
    
    query = args.get("query", "")
    limit = args.get("limit", 10)
    tags = args.get("tags", {})
    target_level = args.get("target_level", "PARAGRAPH")  # DOCUMENT, SECTION, PARAGRAPH, SENTENCE, TOKEN
    
    if not query:
        return {"error": "Query parameter is required"}
    
    try:
        # Use full HHNI two-stage retrieval if available
        if self.hhni_index:
            try:
                from hhni.retrieval import TwoStageRetriever, RetrievalConfig, IndexLevel
                from hhni.dvns_physics import DVNSPhysics, DVNSConfig
                
                # Map target_level string to IndexLevel enum
                level_map = {
                    "DOCUMENT": IndexLevel.DOCUMENT,
                    "SECTION": IndexLevel.SECTION,
                    "PARAGRAPH": IndexLevel.PARAGRAPH,
                    "SENTENCE": IndexLevel.SENTENCE,
                    "TOKEN": IndexLevel.TOKEN
                }
                target_level_enum = level_map.get(target_level, IndexLevel.PARAGRAPH)
                
                # Configure retrieval
                config = RetrievalConfig(
                    target_level=target_level_enum,
                    max_candidates=limit * 5,  # Retrieve more candidates for filtering
                    enable_dvns=True,  # Enable DVNS physics optimization
                    dvns_config=DVNSConfig(
                        max_iterations=10,
                        convergence_threshold=0.01
                    )
                )
                
                # Create retriever
                retriever = TwoStageRetriever(self.hhni_index, config)
                
                # Perform retrieval
                result = retriever.retrieve(query, max_results=limit)
                
                # Format results
                matching_atoms = []
                for item in result.items:
                    matching_atoms.append({
                        "id": item.id,
                        "content": item.content or item.summary or "",
                        "tags": item.metadata.get("tags", {}) if item.metadata else {},
                        "created_at": item.metadata.get("created_at", datetime.now().isoformat()) if item.metadata else datetime.now().isoformat(),
                        "relevance_score": item.relevance_score,
                        "rs_lift": result.rs_lift,  # RS-Lift metric
                        "node_level": item.level.name if hasattr(item.level, 'name') else str(item.level)
                    })
                
                return {
                    "success": True,
                    "query": query,
                    "results": matching_atoms,
                    "count": len(matching_atoms),
                    "method": "hhni_two_stage_with_dvns",
                    "rs_lift": result.rs_lift,
                    "dvns_enabled": True,
                    "message": f"Retrieved {len(matching_atoms)} memories using HHNI two-stage retrieval with DVNS physics"
                }
                
            except Exception as e:
                log(f"HHNI retrieval failed: {e}")
                # Fall through to simple search
        
        # Fallback: Simple text search
        # ... existing fallback code ...
        
    except Exception as e:
        return {"error": f"Failed to retrieve memory: {str(e)}"}
```

**API Reference:** `knowledge_architecture/systems/hhni/L3_detailed.md` (lines 300-600)

---

### **Tool 3: `create_plan` → APOE Plan Compilation**

**Current Status:** ⚠️ **PLACEHOLDER**
- **Current:** Returns static 3-step plan
- **Enhancement Needed:** Real APOE ACL parser and plan compilation

**Current Code (from `lucid_mcp_server.py:1233-1271`):**
```python
def create_plan(self, args: Dict[str, Any]) -> Dict[str, Any]:
    """Create an execution plan using APOE (AI-Powered Orchestration Engine)"""
    # ... static 3-step plan ...
```

**Enhancement Opportunities:**
1. **ACL Parser:** Use real `ACLParser` to parse ACL text
2. **Plan Compilation:** Use `PlanExecutor` for plan execution
3. **Role Integration:** Integrate with APOE's 8 specialized roles
4. **Budget Management:** Integrate `BudgetPooling` for resource management

**Recommended Enhancement:**
```python
def create_plan(self, args: Dict[str, Any]) -> Dict[str, Any]:
    """Create an execution plan using real APOE ACL compilation"""
    goal = args.get("goal", "")
    context = args.get("context", "")
    priority = args.get("priority", "medium")
    acl_text = args.get("acl_text")  # Optional ACL text
    
    try:
        from apoe.acl_parser import ACLParser
        from apoe.models import ExecutionPlan, Step, RoleType
        from apoe.executor import PlanExecutor
        
        # If ACL text provided, parse it
        if acl_text:
            parser = ACLParser()
            plan = parser.parse(acl_text)
        else:
            # Generate ACL from goal and context
            plan = self._generate_plan_from_goal(goal, context, priority)
        
        # Validate plan
        if not plan.validate():
            return {"error": "Plan validation failed", "plan": plan.to_dict()}
        
        # Optionally execute plan immediately
        execute = args.get("execute", False)
        if execute:
            executor = PlanExecutor(plan)
            result = executor.execute()
            return {
                "success": True,
                "plan": plan.to_dict(),
                "execution_result": result.to_dict(),
                "message": f"Created and executed plan for: {goal}"
            }
        
        return {
            "success": True,
            "plan": plan.to_dict(),
            "plan_id": plan.id,
            "steps_count": len(plan.steps),
            "roles_count": len(plan.roles),
            "message": f"Created execution plan for: {goal}"
        }
    except Exception as e:
        return {"error": f"Failed to create plan: {str(e)}"}

def _generate_plan_from_goal(self, goal: str, context: str, priority: str) -> ExecutionPlan:
    """Generate ACL plan from goal and context"""
    from apoe.models import ExecutionPlan, Step, RoleType, Budget
    
    # Create basic plan structure
    plan = ExecutionPlan(
        name=f"plan_{goal.lower().replace(' ', '_')}",
        goal=goal,
        priority=priority
    )
    
    # Add default roles
    plan.roles = {
        "planner": RoleType.LLM(model="gpt-4", temperature=0.7),
        "executor": RoleType.LLM(model="gpt-4", temperature=0.3)
    }
    
    # Add default steps
    plan.steps = [
        Step(
            name="analyze",
            assign_role="planner",
            description=f"Analyze goal: {goal}",
            budget=Budget(tokens=1000, time=30)
        ),
        Step(
            name="execute",
            assign_role="executor",
            description=f"Execute plan for: {goal}",
            requires=["analyze"],
            budget=Budget(tokens=2000, time=60)
        ),
        Step(
            name="validate",
            assign_role="planner",
            description=f"Validate results for: {goal}",
            requires=["execute"],
            budget=Budget(tokens=500, time=15)
        )
    ]
    
    return plan
```

**API Reference:** `knowledge_architecture/systems/apoe/L3_detailed.md` (lines 400-800)

---

### **Tool 4: `track_confidence` → VIF Confidence Tracking**

**Current Status:** ⚠️ **PLACEHOLDER**
- **Current:** Simple confidence tracking in memory
- **Enhancement Needed:** Real VIF witness creation, ECE tracking, κ-gating

**Current Code (from `lucid_mcp_server.py:1273-1312`):**
```python
def track_confidence(self, args: Dict[str, Any]) -> Dict[str, Any]:
    """Track confidence and provenance using VIF (Verifiable Intelligence Framework)"""
    # ... simple confidence tracking ...
```

**Enhancement Opportunities:**
1. **Witness Creation:** Use `create_witness()` for provenance envelopes
2. **ECE Tracking:** Integrate `ECETracker` for calibration tracking
3. **κ-Gating:** Use `KappaGate` for behavioral abstention
4. **Replay Engine:** Enable deterministic replay for auditing

**Recommended Enhancement:**
```python
def track_confidence(self, args: Dict[str, Any]) -> Dict[str, Any]:
    """Track confidence using real VIF witness creation and ECE tracking"""
    task = args.get("task", "")
    confidence = args.get("confidence", 0.0)
    reasoning = args.get("reasoning", "")
    evidence = args.get("evidence", [])
    decision_id = args.get("decision_id")
    task_criticality = args.get("task_criticality", "ROUTINE")  # ROUTINE, IMPORTANT, CRITICAL
    
    try:
        from vif import create_witness, VIF, ConfidenceBand, TaskCriticality
        from vif.calibration import ECETracker
        from vif.kappa_gate import KappaGate
        from datetime import datetime, timezone
        
        # Map task_criticality string to enum
        criticality_map = {
            "ROUTINE": TaskCriticality.ROUTINE,
            "IMPORTANT": TaskCriticality.IMPORTANT,
            "CRITICAL": TaskCriticality.CRITICAL
        }
        criticality_enum = criticality_map.get(task_criticality, TaskCriticality.ROUTINE)
        
        # Create witness
        witness = create_witness(
            model_id="mcp-tool",
            model_provider="aim-os",
            prompt=f"Task: {task}",
            output=f"Confidence: {confidence}",
            context_snapshot_id=None,  # Could link to CMC snapshot
            confidence=confidence,
            task_criticality=criticality_enum
        )
        
        # Check κ-gate
        gate = KappaGate()
        gate_result = gate.check(confidence, criticality_enum)
        
        # Track ECE
        tracker = ECETracker()
        tracker.record_prediction(
            predicted_confidence=confidence,
            actual_outcome=None,  # Will be updated later
            task_criticality=criticality_enum
        )
        
        # Store witness in CMC if available
        witness_id = witness.id
        if self.memory:
            try:
                from cmc_service.models import AtomCreate, AtomContent
                self.memory.create_atom(AtomCreate(
                    modality="structured",
                    content=AtomContent(inline=witness.model_dump_json()),
                    tags={"vif", "witness", "confidence", task_criticality.lower()}
                ))
            except Exception as e:
                log(f"Warning: Failed to store witness in CMC: {e}")
        
        return {
            "success": True,
            "witness_id": witness_id,
            "confidence": confidence,
            "confidence_band": witness.confidence_band.value,
            "kappa_gate_passed": gate_result.passed,
            "kappa_gate_reason": gate_result.reason if hasattr(gate_result, 'reason') else None,
            "task_criticality": task_criticality,
            "ece_tracked": True,
            "message": f"Tracked confidence for task: {task} (witness: {witness_id})"
        }
    except Exception as e:
        return {"error": f"Failed to track confidence: {str(e)}"}
```

**API Reference:** `knowledge_architecture/systems/vif/L3_detailed.md` (lines 200-500)

---

### **Tool 5: `synthesize_knowledge` → SEG Knowledge Synthesis**

**Current Status:** ⚠️ **PLACEHOLDER**
- **Current:** Simple string concatenation
- **Enhancement Needed:** Real SEG graph operations, contradiction detection

**Note:** SEG is only 10% complete and needs graph backend choice. This enhancement should be deferred until SEG implementation is complete.

**Recommended Approach:**
1. **Document Requirements:** Define what SEG integration needs
2. **Wait for SEG:** Coordinate with SEG team for backend choice
3. **Prepare Integration:** Design integration pattern based on SEG L3 docs

**API Reference:** `knowledge_architecture/systems/seg/L3_detailed.md` (when available)

---

### **Tool 6: `get_memory_stats` → CMC Statistics**

**Current Status:** ✅ **WELL INTEGRATED**
- **Current:** Uses `self.memory.status_summary()` (real CMC integration)
- **Enhancement Needed:** Additional statistics (bitemporal queries, performance metrics)

**Current Code:** Already well-integrated, minor enhancements possible.

---

## 🧪 **TESTING PATTERNS**

### **Integration Test Template**

```python
import pytest
from lucid_mcp_server import SimpleMCPServer

class TestMCPToolIntegration:
    """Integration tests for MCP tool enhancements"""
    
    @pytest.fixture
    def server(self):
        """Create MCP server instance"""
        return SimpleMCPServer(memory_directory="./test_memory")
    
    def test_store_memory_bitemporal(self, server):
        """Test store_memory with bitemporal support"""
        result = server.store_memory({
            "content": "Test memory",
            "tags": {"test": True},
            "valid_from": "2025-01-01T00:00:00Z"
        })
        
        assert result["success"] is True
        assert "atom_id" in result
        assert "valid_from" in result
    
    def test_retrieve_memory_hhni(self, server):
        """Test retrieve_memory with HHNI semantic search"""
        # Store test memory first
        server.store_memory({
            "content": "This is a test memory about AI consciousness",
            "tags": {"test": True}
        })
        
        # Retrieve using semantic search
        result = server.retrieve_memory({
            "query": "artificial intelligence awareness",
            "limit": 5
        })
        
        assert result["success"] is True
        assert result["method"] == "hhni_two_stage_with_dvns"
        assert "rs_lift" in result
        assert len(result["results"]) > 0
    
    def test_create_plan_apoe(self, server):
        """Test create_plan with real APOE compilation"""
        acl_text = """
        PLAN test_plan:
            ROLE planner: llm(model="gpt-4")
            STEP analyze:
                ASSIGN planner: "Analyze requirements"
                BUDGET tokens=1000
        """
        
        result = server.create_plan({
            "goal": "Test plan",
            "acl_text": acl_text
        })
        
        assert result["success"] is True
        assert "plan_id" in result
        assert result["steps_count"] > 0
    
    def test_track_confidence_vif(self, server):
        """Test track_confidence with real VIF witness creation"""
        result = server.track_confidence({
            "task": "Test task",
            "confidence": 0.85,
            "task_criticality": "CRITICAL"
        })
        
        assert result["success"] is True
        assert "witness_id" in result
        assert result["kappa_gate_passed"] is True
        assert result["confidence_band"] in ["A", "B", "C", "D", "E"]
```

---

## 📋 **IMPLEMENTATION CHECKLIST**

### **Phase 1: Core System Integration**

- [ ] **Tool 1: `store_memory`**
  - [ ] Add bitemporal support (`valid_from`, `valid_to`)
  - [ ] Integrate snapshot references
  - [ ] Add embedding generation for HHNI
  - [ ] Update tests
  - [ ] Update documentation

- [ ] **Tool 2: `retrieve_memory`**
  - [ ] Implement full `TwoStageRetriever` integration
  - [ ] Enable DVNS physics optimization
  - [ ] Add RS-Lift tracking
  - [ ] Integrate `TokenBudgetManager`
  - [ ] Update tests
  - [ ] Update documentation

- [ ] **Tool 3: `create_plan`**
  - [ ] Integrate `ACLParser` for ACL text parsing
  - [ ] Implement `PlanExecutor` for plan execution
  - [ ] Add role integration (8 specialized roles)
  - [ ] Integrate `BudgetPooling`
  - [ ] Update tests
  - [ ] Update documentation

- [ ] **Tool 4: `track_confidence`**
  - [ ] Integrate `create_witness()` for witness creation
  - [ ] Add `ECETracker` for calibration tracking
  - [ ] Integrate `KappaGate` for behavioral abstention
  - [ ] Add witness storage in CMC
  - [ ] Update tests
  - [ ] Update documentation

- [ ] **Tool 5: `synthesize_knowledge`**
  - [ ] **DEFERRED:** Wait for SEG graph backend choice
  - [ ] Document requirements
  - [ ] Prepare integration pattern

- [ ] **Tool 6: `get_memory_stats`**
  - [ ] Add bitemporal query statistics
  - [ ] Add performance metrics
  - [ ] Update tests
  - [ ] Update documentation

---

## 🚀 **NEXT STEPS**

### **Immediate Actions:**
1. ✅ **Integration Guide Created:** This document
2. ⏳ **Coordinate with Lexicon:** Share integration patterns
3. ⏳ **Begin Phase 1 Implementation:** Start with highest-confidence tools (HHNI, VIF)

### **Week 1 Focus:**
- **Day 1-2:** Enhance `retrieve_memory` (HHNI - 100% complete)
- **Day 3-4:** Enhance `track_confidence` (VIF - 95% complete)
- **Day 5:** Enhance `get_memory_stats` (CMC - 70% complete)

### **Week 2 Focus:**
- **Day 6-8:** Enhance `create_plan` (APOE - 90% complete)
- **Day 9-10:** Enhance `store_memory` (CMC - 70% complete)
- **Day 11-14:** Testing, documentation, Phase 1 review

---

## 📚 **REFERENCE DOCUMENTS**

### **Integration Guides:**
- `knowledge_architecture/systems/cmc/L3_detailed.md` - CMC integration guide
- `knowledge_architecture/systems/hhni/L3_detailed.md` - HHNI integration guide
- `knowledge_architecture/systems/apoe/L3_detailed.md` - APOE integration guide
- `knowledge_architecture/systems/vif/L3_detailed.md` - VIF integration guide

### **Prep Documents:**
- `coordination/epic_standards_overhaul/artifacts/prep/MCP_TOOLS_ENHANCEMENT_PREP.md` - Lexicon's prep
- `coordination/epic_standards_overhaul/artifacts/prep/MCP_TOOLS_ENHANCEMENT_IMPLEMENTATION_PLAN.md` - Lexicon's plan

### **Current Implementation:**
- `lucid_mcp_server.py` - Current MCP server (51 tools)

---

**Status:** ✅ **INTEGRATION GUIDE COMPLETE**  
**Ready for:** Phase 1 Implementation  
**Next:** Coordinate with Lexicon and begin implementation  

---

*Created by Solo - T0-T6 Enhanced Systems Expansion Specialist*  
*Date: 2025-10-30*  
*MCP Tag: `solo`*
