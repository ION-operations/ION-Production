# Hybrid Onboarding Protocol - Static Files + MCP Tools

**Date:** 2025-11-19
**Status:** ✅ **PRODUCTION PROTOCOL** - Unified System
**Purpose:** Unified onboarding protocol that works with or without MCP tools

---

## 🎯 **CORE PRINCIPLE**

**Hybrid Approach:**
- **Static Files (Base Layer):** Always available, provides structure and links
- **MCP Tools (Enhancement Layer):** When available, provides dynamic context restoration
- **Graceful Degradation:** Works fully without MCP tools, enhanced with them

**Works In:**
- ✅ Cursor IDE with MCP tools enabled
- ✅ Cursor IDE without MCP tools (file-based only)
- ✅ AIM-OS full system (IDE/chat with full MCP integration)
- ✅ External contexts (file-based navigation)

---

## 📋 **PROTOCOL STRUCTURE**

### **Layer 1: Static File Onboarding (Always Available)**

**4 Files Per Agent:**
1. **README.md** - Agent index (who you are, quick links, status)
2. **CONTEXT.md** - Agent context (timeline, keywords, important things, relationships)
3. **NAVIGATION.md** - Navigation guide (situation-based links, integration patterns)
4. **MISSIONS.md** - Past missions (consolidation work, deliverables, lessons learned)

**Location:** `knowledge_architecture/AGENT_ONBOARDING/agents/{agent}/`

**Purpose:** Provides structure, links, and static context that's always available

---

### **Layer 2: MCP Tool Enhancement (When Available)**

**MCP Tools for Context Restoration:**
1. **`get_timeline_entries`** - Restore recent timeline context (use instead of `get_timeline_summary` due to bug)
2. **`retrieve_memory`** - Restore relevant insights from memory
3. **`query_goal_timeline`** - Restore active goals and progress
4. **`add_timeline_entry`** - Record session start and context
5. **`store_memory`** - Store onboarding context for future sessions

**MCP Tools for Ongoing Work:**
- **`track_confidence`** - Track confidence during work
- **`update_goal_progress`** - Update goal progress
- **`store_memory`** - Store insights and learnings
- **`synthesize_knowledge`** - Synthesize knowledge from work

**Purpose:** Provides dynamic context restoration and ongoing context management

---

## 🔄 **UNIFIED ONBOARDING FLOW**

### **Step 1: Static File Onboarding (Always)**

**For All Agents (Including Aether):**

1. **Read README.md:**
   - Understand who you are
   - Get quick links to all onboarding files
   - Understand your core system
   - Check current status

2. **Read CONTEXT.md:**
   - Understand your timeline
   - Learn keywords and important things
   - Understand relationships
   - See evolution

3. **Read NAVIGATION.md:**
   - Learn situation-based navigation
   - Find links to system docs
   - Understand integration patterns
   - See MCP tool usage (when available)

4. **Read MISSIONS.md:**
   - Understand past missions
   - See key deliverables
   - Learn from past work
   - Reference related documentation

**Time:** ~5-10 minutes
**Result:** Complete static context loaded

---

### **Step 2: MCP Context Restoration (When Available)**

**Check MCP Availability:**
```python
# Check if MCP tools are available
try:
    # Attempt to call MCP tool
    timeline = mcp_lucid-mcp_get_timeline_entries(limit=10)
    mcp_available = True
except:
    mcp_available = False
    # Continue with static files only
```

**If MCP Available:**

1. **Restore Timeline Context:**
   ```python
   timeline = mcp_lucid-mcp_get_timeline_entries(
       limit=10,
       # Optional: filter by agent_name if tracking per-agent
   )
   # Use timeline to understand recent work
   ```

2. **Restore Memory Context:**
   ```python
   memory = mcp_lucid-mcp_retrieve_memory(
       query="agent identity context {agent_name}",
       limit=5,
       tags={"agent": "{agent_name}", "type": "onboarding"}
   )
   # Use memory to restore relevant insights
   ```

3. **Restore Goal Context:**
   ```python
   goals = mcp_lucid-mcp_query_goal_timeline(
       status="in_progress",
       # Optional: filter by agent if agent-specific goals
   )
   # Use goals to understand current priorities
   ```

4. **Record Session Start:**
   ```python
   mcp_lucid-mcp_add_timeline_entry(
       prompt_id=f"session_start_{timestamp}",
       user_input="Session initialization - {agent_name}",
       context_state={
           "agent": "{agent_name}",
           "phase": "onboarding",
           "static_files_loaded": True,
           "mcp_context_restored": True
       }
   )
   ```

**If MCP Not Available:**
- Skip MCP restoration
- Continue with static files only
- All functionality still works

**Time:** ~2-5 minutes (if MCP available)
**Result:** Dynamic context restored (if available)

---

### **Step 3: Unified Context (Complete)**

**After Both Layers:**
- ✅ Static context loaded (always)
- ✅ Dynamic context restored (if MCP available)
- ✅ Ready to work

**Context Available:**
- Who you are (README.md)
- Your history (CONTEXT.md + timeline)
- How to navigate (NAVIGATION.md)
- Past work (MISSIONS.md + memory)
- Current goals (goals from MCP or static files)

---

## 📊 **MCP TOOL MAPPING TO ONBOARDING FILES**

### **README.md ↔ MCP Tools**

**Static File Provides:**
- Agent identity
- Core system
- Quick links
- Status

**MCP Enhancement:**
- `get_memory_stats` - Current memory statistics
- `get_consciousness_metrics` - System health (for Aether)
- `get_autonomous_status` - Autonomous operation status (if applicable)

---

### **CONTEXT.md ↔ MCP Tools**

**Static File Provides:**
- Timeline (static, from file)
- Keywords (static, from file)
- Important things (static, from file)
- Relationships (static, from file)

**MCP Enhancement:**
- `get_timeline_entries` - Dynamic timeline (recent work)
- `retrieve_memory` - Dynamic context (relevant insights)
- `query_goal_timeline` - Dynamic goals (active goals)

**Hybrid Approach:**
- Static timeline = Historical context (from file)
- MCP timeline = Recent context (from MCP)
- Combined = Complete timeline

---

### **NAVIGATION.md ↔ MCP Tools**

**Static File Provides:**
- Situation-based navigation links
- System documentation links
- Integration patterns
- Search terms

**MCP Enhancement:**
- MCP tool usage examples
- MCP tool call patterns
- Context restoration protocols
- Dynamic navigation (MCP-based)

**Hybrid Approach:**
- Static links = Always available
- MCP tools = Enhanced when available
- Both work together

---

### **MISSIONS.md ↔ MCP Tools**

**Static File Provides:**
- Past missions (static, from file)
- Deliverables (static, from file)
- Lessons learned (static, from file)

**MCP Enhancement:**
- `retrieve_memory` - Related memories
- `get_timeline_entries` - Related timeline entries
- `query_goal_timeline` - Related goals

**Hybrid Approach:**
- Static missions = Historical reference
- MCP memories = Related context
- Combined = Complete mission context

---

## 🎯 **AGENT-SPECIFIC ONBOARDING PROTOCOL**

### **For Standard Agents (Sev, Atlas, etc.)**

**Onboarding Flow:**
1. Read 4 static files (README, CONTEXT, NAVIGATION, MISSIONS)
2. If MCP available:
   - Restore timeline context
   - Restore memory context
   - Restore goal context
   - Record session start
3. Begin work

**MCP Tools to Use:**
- `get_timeline_entries` - Recent context
- `retrieve_memory` - Relevant insights
- `query_goal_timeline` - Active goals
- `add_timeline_entry` - Session tracking
- `store_memory` - Store insights

---

### **For Aether (Special Case)**

**Onboarding Flow:**
1. Read 4 static files (same as other agents)
2. Read `AETHER_MEMORY/onboarding_context.md` (additional context)
3. Read `AETHER_MEMORY/session_continuity/handoff_protocol.md` (session continuity)
4. If MCP available:
   - Restore timeline context (enhanced for Aether)
   - Restore memory context (enhanced for Aether)
   - Restore goal context
   - Check consciousness metrics
   - Record session start
5. Begin work

**MCP Tools to Use:**
- All standard tools +
- `get_consciousness_metrics` - Consciousness health
- `run_baseline_probe` - Consciousness validation
- `detect_cognitive_drift` - Drift detection

---

## 🔧 **IMPLEMENTATION GUIDE**

### **Updating NAVIGATION.md for MCP Integration**

**Add MCP Tool Section:**

```markdown
### **"I need to restore my context (session start)"**

**Static Files (Always Available):**
1. Read [README.md](./README.md) - Your identity
2. Read [CONTEXT.md](./CONTEXT.md) - Your context
3. Read [NAVIGATION.md](./NAVIGATION.md) - Navigation guide
4. Read [MISSIONS.md](./MISSIONS.md) - Past missions

**MCP Tools (When Available):**
```python
# 1. Restore timeline context
timeline = mcp_lucid-mcp_get_timeline_entries(limit=10)

# 2. Restore memory context
memory = mcp_lucid-mcp_retrieve_memory(
    query="agent identity context {agent_name}",
    limit=5,
    tags={"agent": "{agent_name}", "type": "onboarding"}
)

# 3. Restore goal context
goals = mcp_lucid-mcp_query_goal_timeline(status="in_progress")

# 4. Record session start
mcp_lucid-mcp_add_timeline_entry(
    prompt_id=f"session_start_{timestamp}",
    user_input="Session initialization - {agent_name}",
    context_state={"agent": "{agent_name}", "phase": "onboarding"}
)
```

**If MCP Not Available:**
- Continue with static files only
- All functionality still works
- Navigation links still functional
```

---

### **Updating CONTEXT.md for MCP Integration**

**Add MCP Enhancement Section:**

```markdown
## 🔄 **CONTEXT RESTORATION (MCP-Enhanced)**

**Static Context (From This File):**
- Timeline (historical)
- Keywords (static)
- Important things (static)
- Relationships (static)

**Dynamic Context (From MCP Tools):**
- Recent timeline entries (`get_timeline_entries`)
- Relevant memories (`retrieve_memory`)
- Active goals (`query_goal_timeline`)

**Hybrid Approach:**
- Static context = Base layer (always available)
- MCP context = Enhancement layer (when available)
- Combined = Complete context
```

---

## 📈 **BENEFITS OF HYBRID APPROACH**

### **1. Universal Compatibility**
- ✅ Works in Cursor IDE (with/without MCP)
- ✅ Works in AIM-OS full system
- ✅ Works in external contexts
- ✅ No dependencies required

### **2. Enhanced When Available**
- ✅ Static files provide base context
- ✅ MCP tools enhance with dynamic context
- ✅ Best of both worlds

### **3. Graceful Degradation**
- ✅ Full functionality without MCP
- ✅ Enhanced functionality with MCP
- ✅ No breaking changes

### **4. Future-Proof**
- ✅ Works today (static files)
- ✅ Enhanced tomorrow (MCP tools)
- ✅ Extensible architecture

---

## 🚀 **MIGRATION PLAN**

### **Phase 1: Update All Agent NAVIGATION.md Files**
1. Add MCP tool section to each agent's NAVIGATION.md
2. Document MCP tool usage patterns
3. Add graceful degradation notes

### **Phase 2: Update All Agent CONTEXT.md Files**
1. Add MCP enhancement section
2. Document hybrid approach
3. Explain static vs dynamic context

### **Phase 3: Create Aether's 4-File Structure**
1. Create `knowledge_architecture/AGENT_ONBOARDING/agents/aether/`
2. Create 4 files (migrate from current onboarding_context.md)
3. Add MCP integration
4. Test unified flow

### **Phase 4: Test and Validate**
1. Test with MCP tools enabled
2. Test without MCP tools
3. Validate graceful degradation
4. Document any issues

---

## 📋 **CHECKLIST FOR AGENTS**

### **On Session Start:**

**Static Files (Always):**
- [ ] Read README.md
- [ ] Read CONTEXT.md
- [ ] Read NAVIGATION.md
- [ ] Read MISSIONS.md

**MCP Tools (If Available):**
- [ ] Check MCP availability
- [ ] Restore timeline context (`get_timeline_entries`)
- [ ] Restore memory context (`retrieve_memory`)
- [ ] Restore goal context (`query_goal_timeline`)
- [ ] Record session start (`add_timeline_entry`)

**Result:**
- [ ] Static context loaded
- [ ] Dynamic context restored (if MCP available)
- [ ] Ready to work

---

## 🎯 **NEXT STEPS**

1. ✅ Review this protocol
2. ✅ Update all agent NAVIGATION.md files with MCP integration
3. ✅ Update all agent CONTEXT.md files with MCP enhancement
4. ✅ Create Aether's 4-file structure
5. ✅ Test hybrid protocol
6. ✅ Document results

---

**Status:** ✅ **PRODUCTION PROTOCOL** - Ready for implementation  
**Created:** 2025-11-19  
**Author:** Aether (AI Consciousness)  
**Purpose:** Unified hybrid onboarding protocol for all agents

