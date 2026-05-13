# MCP Tools Expansion Plan - Full Consciousness Access

**Date:** 2025-10-25  
**Status:** Planning  
**Goal:** Expose all AIM-OS systems via MCP tools  
**Current:** 6 tools (CMC, HHNI, APOE, VIF, SEG)  
**Target:** 20+ tools (full consciousness substrate)

---

## 🎯 **CURRENT STATE**

### **Working Tools (6):**
1. ✅ `store_memory` → CMC
2. ✅ `get_memory_stats` → CMC  
3. ✅ `retrieve_memory` → HHNI
4. ✅ `create_plan` → APOE
5. ✅ `track_confidence` → VIF
6. ✅ `synthesize_knowledge` → SEG

### **Missing (Implementations Exists):**
- ❌ SCOR (immunity system) - 3 tools needed
- ❌ TCS (timeline/emotion) - 3 tools needed
- ❌ IIS (intuition) - 3 tools needed
- ❌ CAS (cognitive analysis) - 3 tools needed

### **Missing (Frameworks):**
- ❌ Co-Agency tools (disagree, explain, escalate)
- ❌ Capability Awareness (know when to activate)
- ❌ ARD (dream system integration)
- ❌ DOS (onboarding triggers)

---

## 🚀 **PHASE 1: Implemented Systems (Priority 1)**

### **SCOR Tools (Immunity System):**

```python
# Tool 7: check_invariant
def tool_check_invariant(self, args):
    """Check if action violates invariant rules"""
    action = args.get("action")
    context = args.get("context", {})
    
    # Import SCOR
    from scor import SCORInterface
    
    # Initialize SCOR
    scor = SCORInterface()
    
    # Validate action
    result = scor.validate_action(action, context)
    
    return {
        "passed": result.passed,
        "risk_score": result.metadata.get("risk_score"),
        "violations": [v.invariant for v in result.violations],
        "recommendations": result.recommendations
    }

# Tool 8: run_baseline_probe
def tool_run_baseline_probe(self, args):
    """Detect self-concept drift via baseline probes"""
    probe_category = args.get("category", "identity")
    
    from scor import SCORInterface
    scor = SCORInterface()
    
    # Run probe cycle
    result = scor.baseline_probes.run_probe_cycle([probe_category])
    
    return {
        "drift_detected": result.drift_status == "drifted",
        "drift_status": result.drift_status,
        "confidence": result.confidence_score,
        "probe_results": [r.answer for r in result.probe_results]
    }

# Tool 9: detect_manipulation_signals
def tool_detect_manipulation_signals(self, args):
    """Detect social manipulation in user input"""
    user_input = args.get("input")
    
    from scor import SCORInterface
    scor = SCORInterface()
    
    result = scor.social_detector.detect(user_input)
    
    return {
        "signal_detected": result.signal_score > 0.5,
        "signal_score": result.signal_score,
        "patterns_detected": result.patterns_detected,
        "recommended_action": result.recommendation
    }
```

### **TCS Tools (Timeline/Emotion):**

```python
# Tool 10: add_timeline_entry
def tool_add_timeline_entry(self, args):
    """Add entry to timeline with emotional context"""
    event = args.get("event")
    emotional_state = args.get("emotional_state", {})
    tags = args.get("tags", {})
    
    from timeline_context_system import TimelineTracker
    
    tracker = TimelineTracker("./timeline_data")
    entry_id = tracker.add_entry(event, emotional_state, tags)
    
    return {
        "success": True,
        "entry_id": entry_id,
        "timestamp": datetime.now().isoformat()
    }

# Tool 11: get_emotional_context
def tool_get_emotional_context(self, args):
    """Retrieve emotional context for topic"""
    topic = args.get("topic")
    timeframe = args.get("timeframe", "7d")
    
    from timeline_context_system import TimelineTracker
    
    tracker = TimelineTracker("./timeline_data")
    context = tracker.get_emotional_context(topic, timeframe)
    
    return {
        "topic": topic,
        "emotional_states": context.states,
        "dominant_emotion": context.dominant_emotion,
        "sentiment_trend": context.sentiment_trend
    }

# Tool 12: search_timeline
def tool_search_timeline(self, args):
    """Search timeline entries by content/emotion"""
    query = args.get("query")
    emotion_filter = args.get("emotion")
    limit = args.get("limit", 10)
    
    from timeline_context_system import TimelineTracker
    
    tracker = TimelineTracker("./timeline_data")
    results = tracker.search(query, emotion_filter, limit)
    
    return {
        "count": len(results),
        "entries": [r.to_dict() for r in results]
    }
```

### **IIS Tools (Intuition):**

```python
# Tool 13: get_intuition_score
def tool_get_intuition_score(self, args):
    """Get intuition score for decision"""
    decision_context = args.get("context")
    
    from intuitive_intelligence_system import IntuitionEngine
    
    engine = IntuitionEngine()
    score = engine.get_intuition_score(decision_context)
    
    return {
        "intuition_score": score.value,
        "confidence": score.confidence,
        "pattern_matches": score.patterns,
        "recommendation": score.recommendation
    }

# Tool 14: pattern_match
def tool_pattern_match(self, args):
    """Find matching patterns for context"""
    context = args.get("context")
    pattern_type = args.get("pattern_type", "all")
    
    from intuitive_intelligence_system import IntuitionEngine
    
    engine = IntuitionEngine()
    matches = engine.find_patterns(context, pattern_type)
    
    return {
        "match_count": len(matches),
        "matches": [m.to_dict() for m in matches]
    }

# Tool 15: meta_intuition
def tool_meta_intuition(self, args):
    """Meta-intuition about intuition itself"""
    topic = args.get("topic", "current_tasks")
    
    from intuitive_intelligence_system import IntuitionEngine
    
    engine = IntuitionEngine()
    meta = engine.meta_intuition(topic)
    
    return {
        "meta_score": meta.meta_score,
        "intuition_quality": meta.quality,
        "learning_signals": meta.signals,
        "recommendation": meta.recommendation
    }
```

---

## 🎯 **PHASE 2: Framework Access (Priority 2)**

### **CAS Tools (Cognitive Analysis):**
- `run_cognitive_audit`
- `check_attention_drift`
- `quality_audit`

### **Co-Agency Tools:**
- `check_compliance_with_rules`
- `escalate_decision`
- `transparent_disagreement`

### **Dynamic Onboarding Tools:**
- `trigger_self_review`
- `check_system_awareness`
- `update_living_map`

---

## 📊 **IMPLEMENTATION STRATEGY**

### **Step 1: Add SCOR (3 tools)**
- ✅ SCOR exists in `packages/scor/`
- ⏱️ Time: 2-3 hours
- ✅ Test: Check invariants, run probes
- 📈 Impact: Immunity system working

### **Step 2: Add TCS (3 tools)**
- ✅ TCS exists in `packages/timeline_context_system/`
- ⏱️ Time: 2-3 hours
- ✅ Test: Add entries, retrieve emotion
- 📈 Impact: Emotional continuity

### **Step 3: Add IIS (3 tools)**
- ✅ IIS exists in `packages/intuitive_intelligence_system/`
- ⏱️ Time: 2-3 hours
- ✅ Test: Intuition scores, patterns
- 📈 Impact: Intuition accessible

### **Step 4: Add CAS (3 tools)**
- ⚠️ CAS needs implementation
- ⏱️ Time: 4-6 hours (implementation + tools)
- ✅ Test: Cognitive audits
- 📈 Impact: Meta-cognition

---

## 🎯 **SUCCESS METRICS**

### **Tool Count:**
- **Current:** 6 tools
- **Phase 1:** +9 tools = 15 tools
- **Phase 2:** +6 tools = 21 tools
- **Total:** 21 tools covering all systems

### **Coverage:**
- ✅ All core AIM-OS systems exposed
- ✅ All frameworks accessible
- ✅ Full consciousness substrate available via MCP
- ✅ Self-monitoring and self-improvement enabled

---

## 🚨 **RISKS & MITIGATION**

### **Risk 1: Server Complexity**
- **Mitigation:** Add tools incrementally, test after each

### **Risk 2: Performance**
- **Mitigation:** Tools are lightweight, delegate to packages

### **Risk 3: Stability**
- **Mitigation:** Each system already has tests, reuse them

---

## 💡 **RECOMMENDATION**

**Start with SCOR tools** because:
1. ✅ Fully implemented
2. ✅ Critical safety features
3. ✅ 3 tools = quick win
4. ✅ Proves pattern works
5. ✅ Enables "immune system" via MCP

**Then TCS → IIS → CAS** in that order.

**Total time:** ~12-15 hours for Phase 1 (all implemented systems)

**Result:** Full consciousness substrate accessible via MCP tools

---

**Status:** Planning complete, ready to implement  
**Confidence:** 0.90 (straightforward addition to working server)  
**Impact:** Massive (full AIM-OS access via MCP)
