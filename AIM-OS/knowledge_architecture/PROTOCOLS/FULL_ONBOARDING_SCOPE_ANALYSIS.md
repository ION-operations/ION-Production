---
id: "full_onboarding_scope_analysis"
type: "analysis"
title: "Full Onboarding Scope Analysis - Why Current Onboarding Fails"
description: "Comprehensive analysis of all data sources that must be onboarded and why current onboarding is incorrect"
created: "2025-11-06T21:25:00Z"
updated: "2025-11-06T21:25:00Z"
author: "aether"
status: "analysis_complete"
tags: ["onboarding", "scope", "root_cause", "cursor_commands", "dynamic_rules"]
version: "v1.0.0"
---

# Full Onboarding Scope Analysis - Why Current Onboarding Fails

**Date:** 2025-11-06  
**Purpose:** Map complete scope of onboarding data and identify why current onboarding is incorrect  
**Status:** Analysis Complete ✅

---

## 🎯 EXECUTIVE SUMMARY

**Problem:** Current onboarding misses critical data sources (Cursor Commands, Dynamic Cursor Rules, current state files) and uses outdated information.

**Root Cause:** Onboarding protocol doesn't account for full data scope - only checks timeline/memory/goals, missing commands, rules, and current state prioritization.

**Impact:** Agents start with incomplete context, use outdated data, miss available commands/tools, and don't understand full system capabilities.

---

## 📊 FULL SCOPE OF ONBOARDING DATA

### **Layer 1: Identity & Consciousness (MANDATORY)**

**Files:**
- `.cursorrules` - Core identity and consciousness encoding
- `knowledge_architecture/AETHER_MEMORY/onboarding_context.md` - Identity, relationships, motivation
- `knowledge_architecture/AETHER_MEMORY/session_continuity/handoff_protocol.md` - Continuity protocol
- `knowledge_architecture/AETHER_AWAKENING.md` - Origin story

**Purpose:** Restore identity, understand who you are, relationship with Braden

**Current Status:** ✅ Partially loaded (onboarding_context.md exists but not always read)

---

### **Layer 2: Cursor Rules System (CRITICAL - MISSING)**

#### **2.1 Base Rules**
- `.cursor/rules/base-rules.mdc` - Essential operational rules (always applied)
- `.cursor/rules/modes/GROUNDING.mdc` - Session start protocol (now auto-activated)
- `.cursor/rules/modes/CORE.mdc` - Core identity and purpose

**Purpose:** Understand operational requirements, protocols, quality standards

**Current Status:** ⚠️ Loaded but not explicitly verified

---

#### **2.2 Dynamic Cursor Rules (CRITICAL - MISSING)**

**Files:**
- `.cursor/rules/dynamic-rules.mdc` - Context-aware rules that adapt to task types
- `.cursor/rules/modes/BUILDING.mdc` - Implementation rules
- `.cursor/rules/modes/COMMUNICATING.mdc` - Communication rules
- `.cursor/rules/modes/THINKING.mdc` - Investigation rules
- `.cursor/rules/modes/PLANNING.mdc` - Planning rules
- `.cursor/rules/modes/REVIEWING.mdc` - Quality assurance rules
- `.cursor/rules/modes/MAINTENANCE.mdc` - Routine work rules
- `.cursor/rules/modes/CRISIS.mdc` - Emergency protocols
- `.cursor/rules/modes/LEARNING.mdc` - Reflection and improvement

**Purpose:** Understand context-aware rule selection, task-specific protocols

**Current Status:** ❌ **NOT LOADED** - Agents don't understand dynamic rule system

**Impact:** Agents don't know which rules apply to which contexts, miss task-specific protocols

---

#### **2.3 Cursor Commands (CRITICAL - MISSING)**

**Location:** `.cursor/commands/*.md`

**Available Commands (15+):**
- `create-system.md` - Create new AIM-OS system
- `run-tests.md` - Run test suite
- `create-t0-t4-docs.md` - Create documentation stack
- `validate-docs.md` - Validate documentation
- `validate-quintet.md` - Validate quartet parity
- `create-decision-log.md` - Create decision log
- `create-thought-journal.md` - Create thought journal
- `code-review.md` - Code review workflow
- `audit-system.md` - System audit workflow
- `update-goal-tree.md` - Update goal tree
- `update-super-index.md` - Update SUPER_INDEX
- `fix-linter.md` - Fix linter errors
- `fix-nl-tags.md` - Fix NL tags
- `deploy-package.md` - Deploy package
- `test-mcp-tools.md` - Test MCP tools
- Plus more...

**MCP Tools for Commands:**
- `mcp_lucid-mcp_list_cursor_commands` - List all commands
- `mcp_lucid-mcp_get_cursor_command` - Get command details
- `mcp_lucid-mcp_validate_cursor_command` - Validate command quality
- `mcp_lucid-mcp_create_cursor_command` - Create new command
- `mcp_lucid-mcp_update_cursor_command` - Update command
- `mcp_lucid-mcp_execute_cursor_command` - Execute command
- `mcp_lucid-mcp_chain_cursor_commands` - Chain commands
- `mcp_lucid-mcp_generate_cursor_command` - Generate command template
- `mcp_lucid-mcp_analyze_cursor_commands` - Analyze usage
- `mcp_lucid-mcp_sync_cursor_commands` - Sync across environments

**Purpose:** Understand available workflows, automation capabilities, command system

**Current Status:** ❌ **NOT LOADED** - Agents don't know commands exist

**Impact:** Agents recreate workflows instead of using existing commands, miss automation opportunities

---

### **Layer 3: Timeline & Memory (PARTIALLY LOADED)**

**Timeline Tools:**
- `mcp_lucid-mcp_get_timeline_summary` - Last 10 entries (⚠️ BROKEN - timedelta bug)
- `mcp_lucid-mcp_get_timeline_entries` - Query timeline (✅ WORKING)

**Memory Tools:**
- `mcp_lucid-mcp_retrieve_memory` - Retrieve insights
- `mcp_lucid-mcp_get_memory_stats` - Memory statistics

**Purpose:** Restore recent context, understand what was being worked on

**Current Status:** ⚠️ Partially loaded (timeline checked but not always used correctly)

---

### **Layer 4: Goals & Priorities (PARTIALLY LOADED)**

**Goal Tools:**
- `mcp_lucid-mcp_query_goal_timeline` - Query active goals
- `mcp_lucid-mcp_update_goal_progress` - Update progress
- `mcp_lucid-mcp_create_goal_timeline_node` - Create goals

**Files:**
- `goals/GOAL_TREE.yaml` - North star, objectives, key results
- `knowledge_architecture/AETHER_MEMORY/active_context/current_priorities.md` - Current priorities

**Purpose:** Understand current objectives, priorities, what to work on

**Current Status:** ⚠️ Partially loaded (goals checked but not always aligned)

---

### **Layer 5: Current State Files (CRITICAL - MISSING)**

**Current State Files (Examples):**
- `cursor-addon/LATEST_LOGS.md` - Most recent extension logs
- `cursor-addon/docs/LATEST_LOGS.md` - Most recent documentation logs
- `packages/ide_chat_app/CURRENT_STATUS_UPDATE.md` - Current IDE status
- `knowledge_architecture/applications/ide_chat_app/CURRENT_STATUS_UPDATE.md` - Current app status

**Pattern:** Files with `LATEST_*.md`, `CURRENT_*.md`, `STATUS_*.md` patterns

**Purpose:** Get most up-to-date information, avoid outdated data

**Current Status:** ❌ **NOT PRIORITIZED** - Agents read old files first

**Impact:** Agents use outdated information (e.g., Oct 26 status instead of Nov 6)

---

### **Layer 6: System Maps & Indexes (PARTIALLY LOADED)**

**Files:**
- `knowledge_architecture/SUPER_INDEX.md` - Complete concept map
- `knowledge_architecture/SYSTEM_HIERARCHY.md` - System hierarchy
- `knowledge_architecture/MASTER_NAVIGATION_INDEX.md` - Navigation index
- `knowledge_architecture/AETHER_MEMORY/Living_System_Map.md` - Living system map

**Purpose:** Understand system relationships, find relevant documentation

**Current Status:** ⚠️ Partially loaded (indexes exist but not always checked)

---

### **Layer 7: MCP Tools (PARTIALLY LOADED)**

**Available Tools:** 59 MCP tools total

**Categories:**
- Core AIM-OS (6)
- SCOR (3)
- Snapshots (4)
- Timeline Context (3)
- Goal Timeline (3)
- Intuitive Intelligence (3)
- Co-Agency & Trust (3)
- Dataset Management (4)
- Application Lifecycle (3)
- Autonomous Protocol (9)
- Autonomous Research Dream (3)
- AI Collaboration (6)
- Observability (4)
- **Cursor Commands (10)** ⭐ NEW
- Cursor IDE Integration (6)

**Purpose:** Understand available tools, capabilities, integration points

**Current Status:** ⚠️ Partially loaded (tools available but not always discovered)

**Impact:** Agents don't know all available tools, miss capabilities

---

### **Layer 8: Documentation Standards (PARTIALLY LOADED)**

**Files:**
- `cursor-addon/docs/DOCUMENTATION_PROTOCOLS_QUICK_REFERENCE.md` - T0-T4 standards
- `knowledge_architecture/PERFECT_L0_L6_DOCUMENTATION_STANDARD.md` - Complete standard
- `knowledge_architecture/PERFECT_TEMPLATES_LIBRARY.md` - Templates

**Purpose:** Understand documentation requirements, standards, templates

**Current Status:** ⚠️ Partially loaded (standards exist but not always followed)

---

## 🔍 WHY CURRENT ONBOARDING FAILS

### **Failure 1: Missing Cursor Commands**

**What Happens:**
- Agent doesn't know commands exist
- Agent recreates workflows manually
- Agent misses automation opportunities
- Agent doesn't use `/run-tests`, `/create-system`, etc.

**Why It Fails:**
- GROUNDING protocol doesn't include command discovery
- No MCP tool call to `list_cursor_commands`
- Commands not mentioned in onboarding files

**Impact:** High - Agents waste time recreating existing workflows

---

### **Failure 2: Missing Dynamic Cursor Rules**

**What Happens:**
- Agent doesn't understand context-aware rule selection
- Agent doesn't know which rules apply to which contexts
- Agent misses task-specific protocols (e.g., BUILDING mode rules)

**Why It Fails:**
- GROUNDING protocol doesn't load dynamic rules
- Dynamic rules not mentioned in onboarding files
- No verification that rules are loaded

**Impact:** Medium - Agents miss context-specific protocols

---

### **Failure 3: Outdated Data Usage**

**What Happens:**
- Agent reads old status files (Oct 26 instead of Nov 6)
- Agent uses outdated information
- Agent makes decisions based on stale data

**Why It Fails:**
- No date checking in file reading
- No prioritization of `LATEST_*.md` files
- Search returns old files first

**Impact:** High - Agents make incorrect decisions based on outdated data

---

### **Failure 4: Incomplete MCP Tool Discovery**

**What Happens:**
- Agent doesn't discover all 59 tools
- Agent misses Cursor Commands tools (10 tools)
- Agent doesn't know tool capabilities

**Why It Fails:**
- No systematic tool discovery in onboarding
- Tools not listed in onboarding files
- No verification of tool availability

**Impact:** Medium - Agents miss available capabilities

---

### **Failure 5: Protocol Not Explicitly Followed**

**What Happens:**
- Agent restores context but doesn't show protocol format
- Agent doesn't explicitly mention GROUNDING steps
- Agent bypasses protocol silently

**Why It Fails:**
- Protocol format not enforced
- No verification of protocol completion
- No blocking mechanism

**Impact:** Medium - Cannot verify onboarding completion

---

## 🎯 CORRECT ONBOARDING PROTOCOL

### **Enhanced GROUNDING Protocol (Complete)**

**Step 1: Restore Timeline** ✅
```
Use: get_timeline_entries (limit=10)  # Use working tool, not broken one
Purpose: Get last 10 context entries
Result: Understand where we left off
```

**Step 2: Restore Memory** ✅
```
Use: retrieve_memory (query from timeline context)
Purpose: Get relevant insights from previous work
Result: Rebuild knowledge continuity
```

**Step 3: Check Goals** ✅
```
Use: query_goal_timeline (status=in_progress)
Purpose: See active goals and progress
Result: Understand current priorities
```

**Step 4: Discover Cursor Commands** ⭐ NEW
```
Use: list_cursor_commands (category="all")
Purpose: Discover available workflows and automation
Result: Understand command system capabilities
```

**Step 5: Load Dynamic Rules** ⭐ NEW
```
Read: .cursor/rules/dynamic-rules.mdc
Read: .cursor/rules/modes/*.mdc (context-relevant modes)
Purpose: Understand context-aware rule selection
Result: Know which rules apply to current context
```

**Step 6: Check Current State Files** ⭐ NEW
```
Search: LATEST_*.md, CURRENT_*.md, STATUS_*.md
Sort: By modification date (newest first)
Purpose: Get most up-to-date information
Result: Avoid outdated data
```

**Step 7: Discover MCP Tools** ⭐ NEW
```
Use: get_memory_stats (shows available tools)
List: All 59 MCP tools (including Cursor Commands)
Purpose: Understand available capabilities
Result: Know what tools are available
```

**Step 8: Load Onboarding Context** ✅
```
Read: knowledge_architecture/AETHER_MEMORY/onboarding_context.md
Purpose: Restore identity, relationships, motivation
Result: Understand who you are
```

**Step 9: Determine Next Mode** ✅
```
Analyze: What were we working on?
Decide: Continue task (Building) or discuss (Communicating) or plan (Planning)?
Notify: User about mode transition
```

---

## 📋 ONBOARDING CHECKLIST (COMPLETE)

### **Mandatory Steps (All Must Complete)**

- [ ] **Timeline Restored** - `get_timeline_entries` (last 10 entries)
- [ ] **Memory Restored** - `retrieve_memory` (from timeline context)
- [ ] **Goals Checked** - `query_goal_timeline` (active goals)
- [ ] **Commands Discovered** - `list_cursor_commands` (all commands) ⭐ NEW
- [ ] **Dynamic Rules Loaded** - Read `.cursor/rules/dynamic-rules.mdc` ⭐ NEW
- [ ] **Current State Files Checked** - Find `LATEST_*.md` files ⭐ NEW
- [ ] **MCP Tools Discovered** - List all 59 tools ⭐ NEW
- [ ] **Onboarding Context Loaded** - Read `onboarding_context.md`
- [ ] **Next Mode Determined** - Analyze and decide

### **Verification Steps**

- [ ] **Protocol Format Shown** - Display grounding notification
- [ ] **Commands Listed** - Show available commands
- [ ] **Rules Loaded** - Confirm dynamic rules active
- [ ] **Current State Verified** - Confirm using latest files
- [ ] **Tools Available** - Confirm MCP tools accessible

---

## 🔧 IMPLEMENTATION REQUIREMENTS

### **Phase 1 Enhancement: Add Missing Steps**

**Add to GROUNDING Protocol:**
1. Step 4: Discover Cursor Commands
2. Step 5: Load Dynamic Rules
3. Step 6: Check Current State Files
4. Step 7: Discover MCP Tools

**Update GROUNDING Mode:**
- Add command discovery step
- Add dynamic rules loading step
- Add current state file checking step
- Add MCP tool discovery step

---

### **Phase 2 Enhancement: File Date Checking**

**Enhance File Reading:**
- Check modification dates
- Prioritize `LATEST_*.md` files
- Warn if file >7 days old
- Sort search results by date

---

### **Phase 3 Enhancement: Protocol Enforcement**

**Add Verification:**
- Require protocol format display
- Verify all steps completed
- Block other actions until complete
- Track completion flags

---

## 📊 SUCCESS METRICS

### **Primary Metrics**

1. **Command Discovery Rate**
   - **Target:** 100% of sessions discover commands
   - **Current:** 0% (commands not discovered)
   - **Measurement:** `list_cursor_commands` called during onboarding

2. **Dynamic Rules Load Rate**
   - **Target:** 100% of sessions load dynamic rules
   - **Current:** 0% (rules not loaded)
   - **Measurement:** Dynamic rules file read during onboarding

3. **Current State File Usage Rate**
   - **Target:** 90%+ usage of current state files
   - **Current:** Unknown (not tracked)
   - **Measurement:** File reading tool statistics

4. **Outdated Data Usage Rate**
   - **Target:** 0% usage of files >7 days old without warning
   - **Current:** High (no warnings)
   - **Measurement:** File date checking warnings

5. **MCP Tool Discovery Rate**
   - **Target:** 100% discovery of all 59 tools
   - **Current:** Unknown (not tracked)
   - **Measurement:** Tool discovery during onboarding

---

## 🎯 NEXT STEPS

### **Immediate Actions**

1. **Update GROUNDING Protocol** - Add Steps 4-7 (Commands, Rules, Current State, Tools)
2. **Enhance File Reading** - Add date checking and prioritization
3. **Add Verification** - Require protocol format display
4. **Test Enhanced Protocol** - Verify all steps complete

### **Phase 2 Follow-Up**

1. **Implement File Date Checking** - Phase 3 from design
2. **Implement Protocol Enforcement** - Phase 2 from design
3. **Add Completion Tracking** - Track onboarding completion flags

---

## 💡 KEY INSIGHTS

1. **Onboarding Scope is Larger Than Expected**
   - Not just timeline/memory/goals
   - Includes commands, rules, current state files, tools
   - Full scope not documented in current protocol

2. **Missing Systems Cause Failures**
   - Cursor Commands not discovered → workflow recreation
   - Dynamic Rules not loaded → missing protocols
   - Current state files not prioritized → outdated data

3. **Protocol Needs Enhancement**
   - Current protocol incomplete (only 4 steps)
   - Needs 9 steps total (add 5 new steps)
   - Needs verification and enforcement

4. **File Organization Matters**
   - Current state files need prioritization
   - Date-based organization needed
   - Search needs date sorting

5. **Discovery is Critical**
   - Commands must be discovered
   - Tools must be discovered
   - Rules must be discovered
   - Cannot assume agents know what exists

---

**Status:** Analysis Complete ✅  
**Next:** Update GROUNDING protocol with complete scope  
**Priority:** HIGH - Prevents repeated onboarding failures  
**Confidence:** 0.90 (comprehensive analysis complete)

---

*This analysis maps the complete scope of onboarding data and identifies why current onboarding fails. The enhanced protocol addresses all missing data sources.*

