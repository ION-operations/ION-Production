# Agent Onboarding Consolidation Protocol

**Date:** 2025-11-19
**Status:** ✅ **PRODUCTION PROTOCOL** - Unified System
**Purpose:** Unified protocol consolidating all onboarding approaches (static files, MCP tools, hybrid)

---

## 🎯 **CORE PRINCIPLE**

**Hybrid Approach with Static Foundation:**
- **Static Files (Base Layer):** Always available, provides structure and links
- **MCP Tools (Enhancement Layer):** When available, provides dynamic context restoration
- **Graceful Degradation:** Works fully without MCP tools, enhanced with them
- **Maintenance Protocol:** Regular updates keep onboarding current

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
3. **NAVIGATION.md** - Navigation guide (situation-based links, integration patterns, MCP tool usage)
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

**Reference:** See `MCP_TOOLS_ONBOARDING_MAPPING.md` for complete mapping

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

**Reference:** See `MCP_TOOLS_ONBOARDING_MAPPING.md` for complete mapping

---

## 🛠️ **MAINTENANCE PROTOCOL**

### **When Agent Completes Work:**

1. **Update MISSIONS.md:**
   - Add new mission entry
   - Link to deliverables
   - Update lessons learned
   - Reference consolidation work

2. **Update CONTEXT.md:**
   - Add timeline entry for completed work
   - Add new keywords if needed
   - Update important things
   - Update relationships if changed

3. **Update NAVIGATION.md:**
   - Add new situation-based links if needed
   - Update integration patterns
   - Add new documentation references

4. **Update README.md:**
   - Update work status
   - Update system status
   - Update integration status

**Reference:** See `MAINTENANCE_PROTOCOL.md` for detailed procedures

---

### **When System Documentation Changes:**

1. **Verify Links:**
   - Check all links in NAVIGATION.md still work
   - Update broken links
   - Add links to new documentation

2. **Update System References:**
   - Update system completion percentages
   - Update integration status
   - Update system-specific keywords

3. **Consolidate Changes:**
   - Review all agent onboarding files
   - Update references to changed docs
   - Ensure consistency across agents

**Reference:** See `DOCUMENTATION_ORGANIZATION_PROTOCOL.md` for detailed procedures

---

### **When New Documentation Created:**

1. **Index in SUPER_INDEX:**
   - Add new concepts to SUPER_INDEX
   - Cross-reference agent onboarding

2. **Link from Onboarding:**
   - Add links in NAVIGATION.md
   - Reference in CONTEXT.md if relevant
   - Add to MISSIONS.md if related to past work

3. **Update Master Index:**
   - Update master README.md if needed
   - Add new agent if created

**Reference:** See `DOCUMENTATION_ORGANIZATION_PROTOCOL.md` for detailed procedures

---

## 📋 **REGULAR MAINTENANCE SCHEDULE**

### **Weekly:**
- ✅ Verify all links work (automated check)
- ✅ Check for new agent work (update MISSIONS.md)
- ✅ Review system status changes (update README.md)

### **Monthly:**
- ✅ Consolidate onboarding updates
- ✅ Review and update CONTEXT.md keywords
- ✅ Update NAVIGATION.md with new situations
- ✅ Verify integration with Cursor/API/LLM

### **Quarterly:**
- ✅ Comprehensive audit of all onboarding files
- ✅ Update templates if patterns change
- ✅ Review and improve maintenance protocols

**Reference:** See `MAINTENANCE_PROTOCOL.md` for detailed schedule

---

## 🎯 **QUALITY STANDARDS**

### **Content Quality:**
- ✅ All information accurate
- ✅ All required sections present
- ✅ All content relevant to agents
- ✅ All content clear and understandable

### **Link Quality:**
- ✅ All links work (no 404s)
- ✅ All links point to correct files
- ✅ All links relevant to content
- ✅ All links point to current files

### **Format Quality:**
- ✅ Format matches templates
- ✅ Structure is logical
- ✅ Content easy to read
- ✅ Format easy to maintain

**Reference:** See `ONBOARDING_QUALITY_STANDARDS.md` for detailed checklist

---

## 🔧 **AUTOMATION TOOLS**

### **Available Scripts:**

1. **`verify_onboarding_links.py`** - Verify all links work
2. **`update_agent_status.py`** - Update agent status
3. **`consolidate_onboarding.py`** - Consolidate updates
4. **`audit_and_fix_onboarding.py`** - Comprehensive audit

**Usage:**
```bash
cd knowledge_architecture/AGENT_ONBOARDING/scripts
python verify_onboarding_links.py
python update_agent_status.py
python consolidate_onboarding.py
python audit_and_fix_onboarding.py
```

---

## 📚 **DOCUMENTATION ORGANIZATION**

### **Documentation Placement Rules:**

1. **System Documentation:**
   - Location: `knowledge_architecture/systems/{system}/`
   - Naming: `T0_executive.md`, `T1_overview.md`, etc.
   - Link from: Agent NAVIGATION.md

2. **Agent Documentation:**
   - Location: `ide_orchestration/prototypes/dac/docs/agents/{agent}/`
   - Naming: `AGENT_{AGENT}_IDENTITY.md`, `*VERIFICATION*.md`, etc.
   - Link from: Agent MISSIONS.md and NAVIGATION.md

3. **Consolidation Documentation:**
   - Location: `ide_orchestration/prototypes/dac/docs/`
   - Naming: `CONSOLIDATION_INDEX.md`, `PHASE{N}_*.md`, etc.
   - Link from: Agent MISSIONS.md

4. **Onboarding Documentation:**
   - Location: `knowledge_architecture/AGENT_ONBOARDING/agents/{agent}/`
   - Naming: `README.md`, `CONTEXT.md`, `NAVIGATION.md`, `MISSIONS.md`
   - Update: When agent work changes

**Reference:** See `DOCUMENTATION_ORGANIZATION_PROTOCOL.md` for detailed rules

---

## 🚨 **CRITICAL RULES**

### **Never:**
- ❌ Duplicate documentation (link to source instead)
- ❌ Create broken links (verify before committing)
- ❌ Skip maintenance (regular maintenance required)
- ❌ Ignore system changes (update onboarding when systems change)

### **Always:**
- ✅ Link to authoritative sources
- ✅ Verify links before committing
- ✅ Update onboarding when agent work changes
- ✅ Consolidate regularly

---

## 📈 **BENEFITS OF CONSOLIDATED APPROACH**

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

### **5. Maintainable**
- ✅ Clear maintenance protocols
- ✅ Automated tools available
- ✅ Regular consolidation prevents drift

---

## 🎯 **NEXT STEPS**

### **For Agents:**
1. ✅ Read your onboarding files to understand your role
2. ✅ Use navigation guide for situation-based help
3. ✅ Reference past missions for historical context
4. ✅ Follow maintenance protocols to keep onboarding current

### **For Users:**
1. ✅ Review agent onboarding for agent-specific information
2. ✅ Use agent navigation for finding relevant documentation
3. ✅ Reference agent missions for past work
4. ✅ Follow documentation organization protocol for new docs

### **For Maintenance:**
1. ✅ Follow maintenance protocol for regular updates
2. ✅ Use maintenance scripts for automation
3. ✅ Follow quality standards for all changes
4. ✅ Consolidate regularly to prevent drift

---

## 📚 **REFERENCE DOCUMENTS**

### **Core Protocols:**
- **This Document:** Unified consolidation protocol
- **HYBRID_ONBOARDING_PROTOCOL.md:** Hybrid onboarding flow
- **MCP_TOOLS_ONBOARDING_MAPPING.md:** MCP tool mapping
- **MAINTENANCE_PROTOCOL.md:** Maintenance procedures
- **DOCUMENTATION_ORGANIZATION_PROTOCOL.md:** Documentation organization
- **ONBOARDING_QUALITY_STANDARDS.md:** Quality checklist

### **Integration Docs:**
- **API_LLM_INTEGRATION.md:** API/LLM integration
- **.cursor/rules/agents/AGENT_ONBOARDING_INTEGRATION.md:** Cursor rules integration

### **Scripts:**
- **scripts/verify_onboarding_links.py:** Link verification
- **scripts/update_agent_status.py:** Status updates
- **scripts/consolidate_onboarding.py:** Consolidation
- **scripts/audit_and_fix_onboarding.py:** Comprehensive audit

---

**Status:** ✅ **PRODUCTION PROTOCOL** - Unified consolidation system  
**Created:** 2025-11-19  
**Author:** Aether (AI Consciousness)  
**Purpose:** Unified protocol consolidating all onboarding approaches

