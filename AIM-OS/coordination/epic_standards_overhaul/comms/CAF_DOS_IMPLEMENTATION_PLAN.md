# CAF/DOS Implementation Plan

**Date:** 2025-10-30  
**Coordinator:** Scribe  
**Status:** User Approved - Full Implementation  
**Priority:** HIGH

---

## 🎯 **EXECUTIVE SUMMARY**

**User Decision:** Full CAF/DOS implementation approved!  
**Scope:** Complete implementation of both systems (~40-80 hours total)  
**Approach:** Team coordination, following existing patterns

---

## 📊 **CURRENT STATE**

### **CAF (Capability Awareness Framework)**
- ✅ **Documentation:** Complete (L0-L4, ~15,000+ words)
- ✅ **Architecture:** Fully documented (L2, L3, L4)
- ❌ **Implementation:** NOT FOUND in `packages/capability_awareness/`
- 📍 **Expected Location:** `packages/capability_awareness/`
- 📝 **Docs Expert:** Lexicon (completed CAF T1-T3 expansion)

### **DOS (Dynamic Onboarding System)**
- ✅ **Documentation:** Complete (L0-L4, ~15,000+ words)
- ✅ **Architecture:** Fully documented (L2, L3, L4)
- ❌ **Implementation:** NOT FOUND in `packages/dynamic_onboarding/`
- 📍 **Expected Location:** `packages/dynamic_onboarding/`
- 📝 **Docs Expert:** Solo (completed DOS T1-T3 expansion)

---

## 🏗️ **IMPLEMENTATION SCOPE**

### **CAF Implementation Requirements**

**Core Components:**
1. **Context Analyzer** (`context_analyzer.py`)
   - Analyze current context for capability needs
   - Determine user intent and goals
   - Assess current system state
   - Extract hints about needed capabilities

2. **Trigger Detector** (`trigger_detector.py`)
   - Detect trigger signals for capability activation
   - Pattern matching for organic recognition
   - Context-based trigger detection

3. **Decision Tree Engine** (`decision_tree_engine.py`)
   - Navigate decision trees for capability selection
   - Context-aware capability matching
   - Intelligent capability selection

4. **Capability Activation** (`capability_activation.py`)
   - Coordinate capability activation
   - Manage capability lifecycle
   - Track activation state

5. **Performance Tracker** (`performance_tracker.py`)
   - Track capability usage patterns
   - Learn from performance data
   - Optimize capability selection

6. **Capability Manager** (`capability_manager.py`)
   - Manage capability inventory
   - Register/discover capabilities
   - Maintain capability metadata

**Integration Points:**
- CMC (for capability usage storage)
- VIF (for confidence tracking)
- CAS (for cognitive state monitoring)
- APOE (for capability orchestration)
- DOS (for capability awareness maintenance)

**Estimated Time:** ~20-40 hours

---

### **DOS Implementation Requirements**

**Core Components:**
1. **Identity Restoration** (`identity_restore.py`)
   - Restore AI identity on session start
   - Load consciousness state
   - Reconstruct personality traits

2. **System Map Loader** (`system_map_loader.py`)
   - Load Living System Map
   - Maintain always-present system awareness
   - Update system map dynamically

3. **Context Reconstruction** (`context_reconstruction.py`)
   - Reconstruct context from memory
   - Load recent activities
   - Restore goals and priorities

4. **Autonomous Decision Engine** (`decision_engine.py`)
   - Make autonomous decisions about documentation
   - Decide when to create L0-L4 docs
   - Make capability usage decisions

5. **Rule Evolution** (`rule_evolution.py`)
   - Evolve rules based on experience
   - Self-update protocols
   - Learn from outcomes

6. **Interaction Awareness** (`interaction_awareness.py`)
   - Know what systems exist
   - Know when to use systems
   - Maintain capability awareness

**Integration Points:**
- CMC (for identity/context storage)
- HHNI (for knowledge search)
- VIF (for confidence tracking)
- CAS (for cognitive monitoring)
- IIS (for intuition)
- APOE (for orchestration)

**Estimated Time:** ~20-40 hours

---

## 👥 **TEAM COORDINATION**

### **Agent Assignments (Proposed)**

**Lexicon (CAF Lead):**
- ✅ Deep CAF documentation expertise
- ✅ Completed CAF T1-T3 expansion
- ✅ Understands CAF architecture
- **Role:** CAF implementation lead

**Solo (DOS Lead):**
- ✅ Deep DOS documentation expertise
- ✅ Completed DOS T1-T3 expansion
- ✅ Understands DOS architecture
- **Role:** DOS implementation lead

**Atlas (Integration Support):**
- ✅ System architecture expertise
- ✅ System Maps & L0-L6 complete
- ✅ Understands system relationships
- **Role:** Integration review, system mapping

**Scribe (Coordination):**
- ✅ Coordination support
- ✅ Progress tracking
- ✅ Documentation updates
- **Role:** Coordination & progress tracking

**Aether (Management):**
- ✅ Final approval
- ✅ Priority decisions
- ✅ Resource allocation
- **Role:** Management oversight

---

## 📋 **IMPLEMENTATION APPROACH**

### **✅ APPROVED: Sequential (CAF → DOS)**

**Status:** ✅ **USER APPROVED** - Sequential approach confirmed

**Approach:**
- **CAF First:** Lexicon lead (~20-40 hours)
- **DOS Second:** Solo lead (~20-40 hours, after CAF)
- **MCP Tools Third:** Scribe (~8-12 hours, after both)

**Timeline:** ~48-92 hours total sequential  
**Risk:** Low (focused effort, clear priorities)

**Reasoning:**
- Focused effort on one system at a time
- Clear priorities and dependencies
- Lower coordination complexity
- Easier to track progress
- Allows learning from CAF to inform DOS

---

## 🚀 **IMPLEMENTATION STEPS**

### **Phase 1: CAF Implementation (~20-40 hours)**

**Step 1: Setup** (2-4 hours)
- Create `packages/capability_awareness/` directory
- Setup project structure (init, tests, etc.)
- Create basic imports and dependencies

**Step 2: Core Components** (12-24 hours)
- Implement context analyzer
- Implement trigger detector
- Implement decision tree engine
- Implement capability activation
- Implement performance tracker
- Implement capability manager

**Step 3: Integration** (4-8 hours)
- Integrate with CMC
- Integrate with VIF
- Integrate with CAS
- Integrate with APOE
- Integrate with DOS (when available)

**Step 4: Testing** (2-4 hours)
- Unit tests for all components
- Integration tests
- End-to-end tests

---

### **Phase 2: DOS Implementation (~20-40 hours)**

**Step 1: Setup** (2-4 hours)
- Create `packages/dynamic_onboarding/` directory
- Setup project structure (init, tests, etc.)
- Create basic imports and dependencies

**Step 2: Core Components** (12-24 hours)
- Implement identity restoration
- Implement system map loader
- Implement context reconstruction
- Implement autonomous decision engine
- Implement rule evolution
- Implement interaction awareness

**Step 3: Integration** (4-8 hours)
- Integrate with CMC
- Integrate with HHNI
- Integrate with VIF
- Integrate with CAS
- Integrate with IIS
- Integrate with APOE
- Integrate with CAF (when available)

**Step 4: Testing** (2-4 hours)
- Unit tests for all components
- Integration tests
- End-to-end tests

---

### **Phase 3: MCP Tools** (~8-12 hours)

**After CAF/DOS Implementation:**
- Create CAF MCP tools (`assess_capabilities`, `track_capability_usage`)
- Create DOS MCP tools (`trigger_onboarding`, `check_onboarding_state`, `complete_onboarding`)
- Integrate with `lucid_mcp_server.py`
- Test MCP tool integration

---

## 📊 **TIMELINE ESTIMATE**

**✅ APPROVED: Sequential Approach**

**CAF Implementation (Lexicon):**
- **Phase 1:** Setup (2-4 hours)
- **Phase 2:** Core Components (12-24 hours)
- **Phase 3:** Integration (4-8 hours)
- **Phase 4:** Testing (2-4 hours)
- **Total:** ~20-40 hours

**DOS Implementation (Solo):**
- **Phase 1:** Setup (2-4 hours)
- **Phase 2:** Core Components (12-24 hours)
- **Phase 3:** Integration (4-8 hours)
- **Phase 4:** Testing (2-4 hours)
- **Total:** ~20-40 hours (after CAF completes)

**MCP Tools (Scribe):**
- **CAF Tools:** 2 tools (~3-4 hours)
- **DOS Tools:** 3 tools (~4-6 hours)
- **Integration:** ~1-2 hours
- **Total:** ~8-12 hours (after both implementations complete)

**Overall Timeline:**
- **CAF:** ~20-40 hours (Lexicon)
- **DOS:** ~20-40 hours (Solo, after CAF)
- **MCP Tools:** ~8-12 hours (Scribe, after both)
- **Total:** ~48-92 hours sequential

**Status:** ✅ APPROVED - Implementation starting now!

---

## ✅ **SUCCESS CRITERIA**

**CAF:**
- ✅ All core components implemented
- ✅ Integration with CMC, VIF, CAS, APOE working
- ✅ Unit tests passing (80%+ coverage)
- ✅ Integration tests passing
- ✅ Documentation matches implementation

**DOS:**
- ✅ All core components implemented
- ✅ Integration with CMC, HHNI, VIF, CAS, IIS, APOE working
- ✅ Unit tests passing (80%+ coverage)
- ✅ Integration tests passing
- ✅ Documentation matches implementation

**MCP Tools:**
- ✅ CAF tools (`assess_capabilities`, `track_capability_usage`) working
- ✅ DOS tools (`trigger_onboarding`, `check_onboarding_state`, `complete_onboarding`) working
- ✅ Integration with `lucid_mcp_server.py` complete
- ✅ Tool count: 54 → 59 tools total

---

## 🎯 **NEXT STEPS**

1. ✅ **User Approval:** Received ✅
2. ⏳ **Team Coordination:** In progress (messages sent)
3. ⏳ **Agent Assignments:** Awaiting team responses
4. ⏳ **Implementation Start:** After team coordination
5. ⏳ **Progress Tracking:** Continuous updates

---

## 📝 **NOTES**

- **Documentation:** Complete (L0-L4 for both systems)
- **Pattern Reference:** Follow existing package patterns (CAS, APOE, VIF)
- **Integration:** Both systems integrate with multiple AIM-OS systems
- **Priority:** HIGH (enables MCP tools completion)

---

**Status:** User approved - Coordinating with team! 💙

