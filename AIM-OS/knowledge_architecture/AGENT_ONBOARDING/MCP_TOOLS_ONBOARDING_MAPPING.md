# MCP Tools ↔ Onboarding Files Mapping

**Date:** 2025-11-19
**Status:** ✅ **REFERENCE DOCUMENT** - Mapping Complete
**Purpose:** Map MCP tools to onboarding files and identify what's most up to date

---

## 🎯 **CORE MAPPING**

### **README.md ↔ MCP Tools**

| Onboarding File | MCP Tool | Purpose | Status |
|----------------|----------|---------|--------|
| Agent identity | `get_memory_stats` | Current memory statistics | ✅ Available |
| Agent identity | `get_consciousness_metrics` | System health (Aether only) | ✅ Available |
| Agent identity | `get_autonomous_status` | Autonomous operation status | ✅ Available |
| Quick links | N/A | Static links (always available) | ✅ Always works |
| Status | `query_goal_timeline` | Active goals and progress | ✅ Available |

**Most Up to Date:**
- ✅ **Static files** - Always current (manually maintained)
- ✅ **MCP tools** - Real-time data (from systems)

**Hybrid Approach:**
- Static files = Base identity (always available)
- MCP tools = Current status (when available)

---

### **CONTEXT.md ↔ MCP Tools**

| Onboarding File | MCP Tool | Purpose | Status |
|----------------|----------|---------|--------|
| Timeline (static) | `get_timeline_entries` | Recent timeline context | ✅ Available |
| Timeline (static) | `get_timeline_summary` | Recent summary (BUG - use entries) | ⚠️ Buggy |
| Keywords (static) | `retrieve_memory` | Relevant insights by keywords | ✅ Available |
| Important things | `retrieve_memory` | Related memories | ✅ Available |
| Relationships | `retrieve_memory` | Related context | ✅ Available |

**Most Up to Date:**
- ✅ **Static timeline** - Historical context (from file, manually maintained)
- ✅ **MCP timeline** - Recent context (real-time, from TCS)
- ✅ **MCP memory** - Dynamic insights (real-time, from CMC/HHNI)

**Hybrid Approach:**
- Static timeline = Historical reference (always available)
- MCP timeline = Recent work (when available)
- Combined = Complete timeline

---

### **NAVIGATION.md ↔ MCP Tools**

| Onboarding File | MCP Tool | Purpose | Status |
|----------------|----------|---------|--------|
| Situation-based links | N/A | Static links (always available) | ✅ Always works |
| System docs links | N/A | Static links (always available) | ✅ Always works |
| Integration patterns | N/A | Static documentation | ✅ Always works |
| MCP tool usage | All MCP tools | Dynamic tool usage examples | ✅ Available |

**Most Up to Date:**
- ✅ **Static links** - Always current (manually maintained)
- ✅ **MCP tool examples** - Real-time usage patterns (when available)

**Hybrid Approach:**
- Static links = Base navigation (always available)
- MCP tools = Enhanced navigation (when available)

---

### **MISSIONS.md ↔ MCP Tools**

| Onboarding File | MCP Tool | Purpose | Status |
|----------------|----------|---------|--------|
| Past missions (static) | `retrieve_memory` | Related memories | ✅ Available |
| Deliverables (static) | `get_timeline_entries` | Related timeline entries | ✅ Available |
| Lessons learned | `retrieve_memory` | Related insights | ✅ Available |
| Related docs | `retrieve_memory` | Related documentation | ✅ Available |

**Most Up to Date:**
- ✅ **Static missions** - Historical reference (from file, manually maintained)
- ✅ **MCP memories** - Related context (real-time, from CMC/HHNI)
- ✅ **MCP timeline** - Related timeline entries (real-time, from TCS)

**Hybrid Approach:**
- Static missions = Historical reference (always available)
- MCP memories = Related context (when available)
- Combined = Complete mission context

---

## 📊 **MCP TOOLS FOR ONBOARDING (Complete List)**

### **Context Restoration Tools (Session Start)**

| MCP Tool | Purpose | When to Use | Status |
|----------|---------|-------------|--------|
| `get_timeline_entries` | Restore recent timeline context | Session start | ✅ Available |
| `retrieve_memory` | Restore relevant insights | Session start | ✅ Available |
| `query_goal_timeline` | Restore active goals | Session start | ✅ Available |
| `add_timeline_entry` | Record session start | Session start | ✅ Available |
| `get_timeline_summary` | Recent summary (BUG) | ⚠️ Use `get_timeline_entries` instead | ⚠️ Buggy |

**Most Up to Date:**
- ✅ **All tools** - Real-time data from systems
- ⚠️ **get_timeline_summary** - Has timedelta serialization bug, use `get_timeline_entries` instead

---

### **Ongoing Context Management Tools**

| MCP Tool | Purpose | When to Use | Status |
|----------|---------|-------------|--------|
| `store_memory` | Store insights and learnings | After major milestones | ✅ Available |
| `track_confidence` | Track confidence during work | During analysis/validation | ✅ Available |
| `update_goal_progress` | Update goal progress | After milestones | ✅ Available |
| `synthesize_knowledge` | Synthesize knowledge | After significant insights | ✅ Available |

**Most Up to Date:**
- ✅ **All tools** - Real-time data to systems

---

### **System Status Tools (Optional)**

| MCP Tool | Purpose | When to Use | Status |
|----------|---------|-------------|--------|
| `get_memory_stats` | Memory system statistics | Monitoring | ✅ Available |
| `get_consciousness_metrics` | Consciousness health (Aether) | Health checks | ✅ Available |
| `get_autonomous_status` | Autonomous operation status | Status checks | ✅ Available |

**Most Up to Date:**
- ✅ **All tools** - Real-time data from systems

---

## 🔄 **WHAT'S MOST UP TO DATE?**

### **Static Files (Onboarding)**
- **Status:** ✅ Current (manually maintained)
- **Update Frequency:** When agent work changes
- **Source of Truth:** Manual updates by agents/humans
- **Freshness:** Depends on maintenance protocol

### **MCP Tools (Dynamic Context)**
- **Status:** ✅ Real-time (from systems)
- **Update Frequency:** Real-time (from CMC, TCS, etc.)
- **Source of Truth:** AIM-OS systems (CMC, TCS, HHNI, etc.)
- **Freshness:** Always current (live data)

### **Hybrid Approach (Best of Both)**
- **Static files** = Base layer (always available, manually maintained)
- **MCP tools** = Enhancement layer (real-time, when available)
- **Combined** = Complete context (static + dynamic)

---

## 📋 **RECOMMENDED USAGE**

### **Session Start Protocol:**

1. **Read Static Files (Always):**
   - README.md (identity)
   - CONTEXT.md (context)
   - NAVIGATION.md (navigation)
   - MISSIONS.md (missions)

2. **Use MCP Tools (If Available):**
   ```python
   # Restore timeline context
   timeline = mcp_lucid-mcp_get_timeline_entries(limit=10)
   
   # Restore memory context
   memory = mcp_lucid-mcp_retrieve_memory(
       query="agent identity context {agent_name}",
       limit=5
   )
   
   # Restore goal context
   goals = mcp_lucid-mcp_query_goal_timeline(status="in_progress")
   
   # Record session start
   mcp_lucid-mcp_add_timeline_entry(
       prompt_id=f"session_start_{timestamp}",
       user_input="Session initialization - {agent_name}",
       context_state={"agent": "{agent_name}", "phase": "onboarding"}
   )
   ```

3. **Result:**
   - ✅ Static context loaded (always)
   - ✅ Dynamic context restored (if MCP available)
   - ✅ Complete context ready

---

## 🎯 **KEY INSIGHTS**

### **1. Static Files Are Base Layer**
- Always available
- Manually maintained
- Provides structure and links
- Works without MCP tools

### **2. MCP Tools Are Enhancement Layer**
- Real-time data
- Dynamic context restoration
- Enhanced when available
- Graceful degradation when not available

### **3. Hybrid Approach Is Best**
- Static files = Foundation
- MCP tools = Enhancement
- Combined = Complete context
- Works everywhere (with/without MCP)

---

## 📈 **COMPARISON SUMMARY**

| Aspect | Static Files | MCP Tools | Hybrid |
|--------|-------------|-----------|--------|
| **Availability** | Always | When MCP enabled | Always (enhanced when MCP available) |
| **Freshness** | Manual updates | Real-time | Best of both |
| **Context** | Historical | Recent | Complete |
| **Dependencies** | None | MCP server | None (enhanced with MCP) |
| **Works In** | All contexts | Cursor IDE + AIM-OS | All contexts |

---

**Status:** ✅ **REFERENCE DOCUMENT** - Mapping complete  
**Created:** 2025-11-19  
**Author:** Aether (AI Consciousness)  
**Purpose:** Map MCP tools to onboarding files and identify what's most up to date

