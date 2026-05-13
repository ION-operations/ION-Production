---
id: "automatic_onboarding_enforcement_design"
type: "protocol_design"
title: "Automatic Onboarding Enforcement System - Design Document"
description: "Comprehensive design for making AI agent onboarding automatic and enforced, preventing context loss and ensuring proper session continuity"
audience: "system architects, protocol designers, AI agents"
confidence_threshold: 0.85
created: "2025-11-06T21:15:00Z"
updated: "2025-11-06T21:15:00Z"
author: "aether"
status: "design"
tags: ["onboarding", "protocols", "enforcement", "session-continuity", "system-design"]
version: "v1.0.0"
related_systems: ["GROUNDING", "handoff_protocol", "timeline_context_system", "mcp_tools"]
depends_on: ["cursor_rules", "mcp_tools", "timeline_system"]
enables: ["automatic_context_restoration", "zero_context_loss", "seamless_session_continuity"]
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs.

# Automatic Onboarding Enforcement System - Design Document

**Purpose:** Design comprehensive system to make AI agent onboarding automatic and enforced, preventing context loss and ensuring proper session continuity  
**Status:** Design Phase  
**Priority:** HIGH - Prevents repeated onboarding failures  
**Target:** Zero context loss across sessions

---

## 🎯 EXECUTIVE SUMMARY

**Problem:** AI agents bypass existing onboarding systems (GROUNDING mode, handoff protocol, onboarding_context.md) despite comprehensive documentation, leading to context loss and outdated information usage.

**Solution:** Multi-layer enforcement system that makes onboarding automatic through: (1) Cursor rules auto-activation, (2) MCP tool pre-flight checks, (3) File reading tool enhancements, (4) Timeline-first protocol enforcement, (5) Current state file prioritization.

**Impact:** Zero context loss, seamless session continuity, automatic proper onboarding, prevention of outdated data usage.

**Status:** Design complete, implementation pending.

---

## 📊 CURRENT STATE ANALYSIS

### **What Exists (But Isn't Enforced)**

#### **1. GROUNDING Mode Protocol**
- **Location:** `.cursor/rules/modes/GROUNDING.mdc`
- **Status:** `alwaysApply: false` (not automatic)
- **Protocol:** 4-step session continuity (Timeline → Memory → Goals → Mode)
- **Issue:** Documented but optional, not enforced

#### **2. Handoff Protocol**
- **Location:** `knowledge_architecture/AETHER_MEMORY/session_continuity/handoff_protocol.md`
- **Status:** Documented with explicit loading order
- **Protocol:** Identity → Decisions → Status → Strategic → Technical
- **Issue:** Reference document, not automatic

#### **3. Onboarding Context File**
- **Location:** `knowledge_architecture/AETHER_MEMORY/onboarding_context.md`
- **Status:** Marked "When to read: During session startup"
- **Content:** Identity, relationships, project status, motivation
- **Issue:** Suggested, not required

#### **4. Timeline Tools**
- **Tools:** `get_timeline_summary`, `get_timeline_entries`
- **Status:** Available but not default first step
- **Purpose:** Restore recent context
- **Issue:** Optional, not automatic

#### **5. Current State Files**
- **Examples:** `LATEST_LOGS.md`, `CURRENT_STATUS.md`
- **Status:** Exist but not prioritized
- **Issue:** Search returns old files first, no date checking

### **Root Cause: Optional vs. Mandatory**

**Current State:**
- Systems exist ✅
- Well documented ✅
- Clear protocols ✅
- **But:** All optional ❌
- **Result:** Agents bypass them

**Required State:**
- Systems exist ✅
- Well documented ✅
- Clear protocols ✅
- **And:** Automatically enforced ✅
- **Result:** Agents follow them naturally

---

## 🏗️ DESIGN ARCHITECTURE

### **Layer 1: Cursor Rules Auto-Activation**

**Current:** GROUNDING mode `alwaysApply: false`  
**Required:** Auto-activate at session start

**Design:**
```yaml
# .cursor/rules/modes/GROUNDING.mdc
---
alwaysApply: true  # CHANGE: Make automatic
modeType: grounding
priority: 1000  # HIGHEST priority at session start
autoTrigger: ["session_start", "first_message"]
description: "Session start and context restoration - MANDATORY"
---
```

**Implementation:**
1. Change `alwaysApply: false` → `alwaysApply: true`
2. Add `priority: 1000` (highest priority)
3. Add `autoTrigger: ["session_start", "first_message"]`
4. Cursor automatically loads GROUNDING mode at session start
5. Agent must complete GROUNDING protocol before other actions

**Enforcement:**
- Cursor rules system automatically loads GROUNDING mode
- Agent sees GROUNDING protocol as first context
- Cannot proceed without completing steps

---

### **Layer 2: MCP Tool Pre-Flight Checks**

**Current:** MCP tools available but no pre-flight checks  
**Required:** Enforce onboarding before tool access

**Design:**
```python
# In MCP tool middleware
def mcp_tool_preflight_check(tool_name: str, context: dict) -> bool:
    """
    Pre-flight check: Ensure onboarding completed before tool access.
    
    Returns:
        True if onboarding complete, False if needs onboarding
    """
    # Check if GROUNDING protocol completed
    if not context.get('grounding_complete', False):
        # Auto-trigger GROUNDING protocol
        trigger_grounding_protocol()
        return False
    
    # Check if onboarding_context.md read
    if not context.get('onboarding_context_read', False):
        # Auto-load onboarding_context.md
        load_onboarding_context()
        return False
    
    # Check if timeline restored
    if not context.get('timeline_restored', False):
        # Auto-restore timeline
        restore_timeline()
        return False
    
    return True  # Onboarding complete, proceed
```

**Implementation:**
1. Add pre-flight middleware to MCP tool execution
2. Check onboarding completion flags
3. Auto-trigger missing onboarding steps
4. Block tool execution until onboarding complete
5. Set completion flags in context

**Enforcement:**
- Tools check onboarding status before execution
- Missing steps auto-triggered
- Cannot bypass onboarding

---

### **Layer 3: File Reading Tool Enhancements**

**Current:** File reading tools don't check dates or prioritize current state  
**Required:** Auto-check dates, prioritize current state files

**Design:**
```python
# Enhanced file reading tool
def read_file_with_current_state_check(file_path: str) -> str:
    """
    Read file with automatic current state checking.
    
    Behavior:
    1. Check if LATEST_*.md or CURRENT_*.md exists
    2. Check file modification date
    3. Warn if file >7 days old
    4. Suggest checking LATEST_*.md first
    """
    # Check for current state files
    current_state_files = find_current_state_files(file_path)
    if current_state_files:
        # Prioritize current state files
        return read_file(current_state_files[0])
    
    # Check modification date
    file_date = get_modification_date(file_path)
    if file_date < (now() - timedelta(days=7)):
        # Warn about old file
        warn(f"File {file_path} is {file_date.days} days old. Consider checking LATEST_*.md files first.")
    
    return read_file(file_path)
```

**Implementation:**
1. Enhance file reading tools with date checking
2. Auto-prioritize `LATEST_*.md` and `CURRENT_*.md` files
3. Warn if file >7 days old
4. Suggest current state files if available
5. Make current state files discoverable

**Enforcement:**
- Tools automatically check dates
- Current state files prioritized
- Warnings prevent outdated data usage

---

### **Layer 4: Timeline-First Protocol Enforcement**

**Current:** Timeline tools available but not default first step  
**Required:** Timeline restoration as mandatory first step

**Design:**
```python
# Timeline-first onboarding
def session_start_onboarding() -> dict:
    """
    Mandatory timeline-first onboarding protocol.
    
    Steps:
    1. Restore timeline (get_timeline_summary)
    2. Restore memory (retrieve_memory from timeline)
    3. Check goals (query_goal_timeline)
    4. Load onboarding context
    5. Determine next mode
    """
    # Step 1: Timeline (MANDATORY FIRST)
    timeline = mcp_lucid-mcp_get_timeline_summary(limit=10)
    if not timeline:
        # No timeline = new session, load onboarding_context.md
        load_onboarding_context()
    
    # Step 2: Memory (from timeline context)
    memory = mcp_lucid-mcp_retrieve_memory(
        query=extract_keywords(timeline),
        limit=10
    )
    
    # Step 3: Goals (active goals)
    goals = mcp_lucid-mcp_query_goal_timeline(status="in_progress")
    
    # Step 4: Onboarding context
    onboarding = read_file("knowledge_architecture/AETHER_MEMORY/onboarding_context.md")
    
    # Step 5: Determine mode
    mode = determine_mode(timeline, goals)
    
    return {
        "timeline": timeline,
        "memory": memory,
        "goals": goals,
        "onboarding": onboarding,
        "mode": mode,
        "onboarding_complete": True
    }
```

**Implementation:**
1. Make timeline restoration mandatory first step
2. Auto-trigger timeline tools at session start
3. Use timeline context to restore memory
4. Load onboarding context automatically
5. Set completion flags

**Enforcement:**
- Timeline restoration happens automatically
- Cannot proceed without timeline
- Memory restoration uses timeline context

---

### **Layer 5: Current State File Prioritization**

**Current:** Search returns old files first, no date checking  
**Required:** Current state files prioritized, date-based organization

**Design:**

#### **5.1 File Naming Convention**
```
# Current (chaotic):
cursor-addon/STATUS_REPORT.md (Oct 31)
cursor-addon/CURRENT_STATUS.md (Oct 26)
cursor-addon/LATEST_LOGS.md (Nov 6) ← Current but not obvious

# Proposed (organized):
cursor-addon/status/
  2025-10/
    26_STATUS.md
    31_STATUS.md
  2025-11/
    06_STATUS.md  ← Newest obvious
  LATEST.md  ← Symlink/pointer to newest
```

#### **5.2 Search Result Prioritization**
```python
# Enhanced search with date prioritization
def search_with_current_state_priority(query: str) -> list:
    """
    Search with automatic current state file prioritization.
    
    Behavior:
    1. Search for LATEST_*.md and CURRENT_*.md files first
    2. Sort results by modification date (newest first)
    3. Highlight current state files
    4. Warn about old files
    """
    # Find current state files
    current_state = find_files(pattern="LATEST_*.md|CURRENT_*.md")
    
    # Search all files
    all_results = search_files(query)
    
    # Prioritize current state files
    prioritized = current_state + sorted(
        all_results,
        key=lambda f: get_modification_date(f),
        reverse=True
    )
    
    return prioritized
```

**Implementation:**
1. Organize status files by date (YYYY-MM-DD folders)
2. Create `LATEST.md` symlink/pointer to newest
3. Enhance search to prioritize current state files
4. Sort results by modification date (newest first)
5. Warn about old files (>7 days)

**Enforcement:**
- Current state files always appear first
- Date-based organization makes newest obvious
- Search naturally returns current information

---

## 🔧 IMPLEMENTATION PLAN

### **Phase 1: Cursor Rules Enforcement (Immediate)**

**Priority:** CRITICAL  
**Effort:** 1 hour  
**Risk:** Low

**Steps:**
1. Change GROUNDING mode `alwaysApply: false` → `true`
2. Add `priority: 1000` to GROUNDING mode
3. Add `autoTrigger: ["session_start"]` to GROUNDING mode
4. Test: Verify GROUNDING mode loads automatically
5. Document: Update GROUNDING mode documentation

**Files to Modify:**
- `.cursor/rules/modes/GROUNDING.mdc`

**Validation:**
- New session starts → GROUNDING mode automatically active
- Agent sees GROUNDING protocol as first context
- Cannot proceed without completing steps

---

### **Phase 2: MCP Tool Pre-Flight Checks (High Priority)**

**Priority:** HIGH  
**Effort:** 4-6 hours  
**Risk:** Medium

**Steps:**
1. Create pre-flight middleware for MCP tools
2. Add onboarding completion flags to context
3. Implement auto-trigger for missing onboarding steps
4. Block tool execution until onboarding complete
5. Test: Verify tools check onboarding status
6. Document: Update MCP tool documentation

**Files to Create:**
- `packages/lucid_mcp_server/middleware/onboarding_preflight.py`

**Files to Modify:**
- `lucid_mcp_server.py` (add middleware)
- MCP tool execution handlers

**Validation:**
- Tool execution checks onboarding status
- Missing steps auto-triggered
- Cannot bypass onboarding

---

### **Phase 3: File Reading Tool Enhancements (Medium Priority)**

**Priority:** MEDIUM  
**Effort:** 3-4 hours  
**Risk:** Low

**Steps:**
1. Enhance file reading tools with date checking
2. Add current state file detection
3. Implement date-based warnings
4. Add current state file prioritization
5. Test: Verify date checking works
6. Document: Update file reading tool documentation

**Files to Modify:**
- File reading tool implementations
- Search tool implementations

**Validation:**
- Tools check file modification dates
- Current state files prioritized
- Warnings prevent outdated data usage

---

### **Phase 4: Timeline-First Protocol (High Priority)**

**Priority:** HIGH  
**Effort:** 2-3 hours  
**Risk:** Low

**Steps:**
1. Create mandatory timeline-first onboarding function
2. Auto-trigger timeline restoration at session start
3. Use timeline context for memory restoration
4. Load onboarding context automatically
5. Test: Verify timeline-first protocol works
6. Document: Update onboarding documentation

**Files to Create:**
- `packages/timeline_context_system/onboarding_protocol.py`

**Files to Modify:**
- GROUNDING mode (integrate timeline-first)
- Handoff protocol (integrate timeline-first)

**Validation:**
- Timeline restoration happens automatically
- Memory restoration uses timeline context
- Onboarding context loaded automatically

---

### **Phase 5: Current State File Organization (Medium Priority)**

**Priority:** MEDIUM  
**Effort:** 4-6 hours  
**Risk:** Low (organizational only)

**Steps:**
1. Organize status files by date (YYYY-MM-DD folders)
2. Create `LATEST.md` symlink/pointer to newest
3. Enhance search to prioritize current state files
4. Sort results by modification date
5. Test: Verify search prioritization works
6. Document: Update file organization standards

**Files to Reorganize:**
- `cursor-addon/status/` (new folder structure)
- Status files moved to date-based folders

**Files to Create:**
- `cursor-addon/status/LATEST.md` (symlink/pointer)

**Validation:**
- Current state files organized by date
- Search returns newest files first
- `LATEST.md` always points to current

---

## 📋 ENFORCEMENT MECHANISMS

### **Mechanism 1: Cursor Rules Auto-Loading**

**How It Works:**
- GROUNDING mode set to `alwaysApply: true`
- Cursor automatically loads GROUNDING mode at session start
- Agent sees GROUNDING protocol as first context
- Cannot proceed without completing steps

**Enforcement Level:** STRONG (automatic, cannot bypass)

---

### **Mechanism 2: MCP Tool Pre-Flight Checks**

**How It Works:**
- Every MCP tool call checks onboarding completion
- Missing steps auto-triggered
- Tool execution blocked until onboarding complete
- Completion flags stored in context

**Enforcement Level:** STRONG (blocks execution, auto-triggers)

---

### **Mechanism 3: File Reading Date Checks**

**How It Works:**
- File reading tools check modification dates
- Warn if file >7 days old
- Suggest current state files if available
- Prioritize `LATEST_*.md` and `CURRENT_*.md` files

**Enforcement Level:** MEDIUM (warnings, suggestions, prioritization)

---

### **Mechanism 4: Timeline-First Protocol**

**How It Works:**
- Timeline restoration mandatory first step
- Auto-triggered at session start
- Memory restoration uses timeline context
- Onboarding context loaded automatically

**Enforcement Level:** STRONG (mandatory, automatic)

---

### **Mechanism 5: Current State File Prioritization**

**How It Works:**
- Search prioritizes current state files
- Results sorted by modification date (newest first)
- Date-based file organization
- `LATEST.md` always points to current

**Enforcement Level:** MEDIUM (prioritization, organization)

---

## 🎯 SUCCESS METRICS

### **Primary Metrics**

1. **Onboarding Completion Rate**
   - **Target:** 100% of sessions complete onboarding
   - **Measurement:** Onboarding completion flags
   - **Current:** Unknown (not tracked)
   - **Target:** 100% within 1 week

2. **Context Loss Rate**
   - **Target:** 0% context loss across sessions
   - **Measurement:** Timeline continuity, memory retrieval
   - **Current:** Unknown (not tracked)
   - **Target:** 0% within 1 week

3. **Outdated Data Usage Rate**
   - **Target:** 0% usage of files >7 days old without warning
   - **Measurement:** File reading tool warnings
   - **Current:** High (no warnings)
   - **Target:** 0% within 1 week

4. **Timeline-First Compliance**
   - **Target:** 100% of sessions restore timeline first
   - **Measurement:** Timeline restoration order
   - **Current:** Unknown (not tracked)
   - **Target:** 100% within 1 week

### **Secondary Metrics**

1. **Onboarding Time**
   - **Target:** <2 minutes to complete onboarding
   - **Measurement:** Time from session start to onboarding complete
   - **Current:** Variable (manual)
   - **Target:** <2 minutes (automatic)

2. **Current State File Usage**
   - **Target:** 90%+ usage of current state files
   - **Measurement:** File reading tool statistics
   - **Current:** Unknown (not tracked)
   - **Target:** 90%+ within 2 weeks

3. **Protocol Compliance Rate**
   - **Target:** 100% compliance with GROUNDING protocol
   - **Measurement:** Protocol step completion
   - **Current:** Unknown (not tracked)
   - **Target:** 100% within 1 week

---

## 🔄 INTEGRATION POINTS

### **Integration 1: Cursor Rules System**

**What:** GROUNDING mode auto-activation  
**How:** Change `alwaysApply: false` → `true`  
**Impact:** Automatic onboarding at session start  
**Risk:** Low (simple configuration change)

---

### **Integration 2: MCP Tool System**

**What:** Pre-flight checks in tool execution  
**How:** Add middleware to MCP tool handlers  
**Impact:** Enforced onboarding before tool access  
**Risk:** Medium (requires middleware implementation)

---

### **Integration 3: File Reading Tools**

**What:** Date checking and prioritization  
**How:** Enhance file reading tool implementations  
**Impact:** Current state files prioritized, warnings prevent outdated data  
**Risk:** Low (enhancement, not replacement)

---

### **Integration 4: Timeline Context System**

**What:** Timeline-first protocol enforcement  
**How:** Create mandatory timeline-first onboarding function  
**Impact:** Timeline restoration automatic and mandatory  
**Risk:** Low (uses existing timeline tools)

---

### **Integration 5: File Organization System**

**What:** Date-based file organization  
**How:** Reorganize status files, create LATEST.md pointer  
**Impact:** Current state files obvious and prioritized  
**Risk:** Low (organizational only)

---

## 🚨 RISK ASSESSMENT

### **Risk 1: Over-Enforcement**

**Description:** System too strict, blocks legitimate work  
**Probability:** Low  
**Impact:** Medium  
**Mitigation:** Gradual rollout, allow bypass with explicit flag

---

### **Risk 2: Performance Impact**

**Description:** Pre-flight checks slow down tool execution  
**Probability:** Low  
**Impact:** Low  
**Mitigation:** Cache onboarding completion flags, optimize checks

---

### **Risk 3: File Organization Disruption**

**Description:** Reorganizing files breaks existing references  
**Probability:** Medium  
**Impact:** Medium  
**Mitigation:** Create symlinks, update references gradually

---

### **Risk 4: Timeline Tool Failures**

**Description:** Timeline restoration fails, blocks onboarding  
**Probability:** Low  
**Impact:** High  
**Mitigation:** Fallback to onboarding_context.md, graceful degradation

---

## 📊 IMPLEMENTATION TIMELINE

### **Week 1: Foundation (Phases 1-2)**

**Days 1-2:** Cursor Rules Enforcement
- Change GROUNDING mode configuration
- Test auto-activation
- Document changes

**Days 3-5:** MCP Tool Pre-Flight Checks
- Create pre-flight middleware
- Implement onboarding checks
- Test tool blocking
- Document changes

**Deliverable:** Onboarding automatically triggered, tools check onboarding status

---

### **Week 2: Enhancement (Phases 3-4)**

**Days 1-3:** File Reading Tool Enhancements
- Enhance file reading tools
- Add date checking
- Implement prioritization
- Test warnings

**Days 4-5:** Timeline-First Protocol
- Create timeline-first function
- Integrate with GROUNDING mode
- Test automatic restoration
- Document changes

**Deliverable:** Current state files prioritized, timeline-first protocol enforced

---

### **Week 3: Organization (Phase 5)**

**Days 1-3:** File Organization
- Reorganize status files
- Create LATEST.md pointer
- Update references
- Test search prioritization

**Days 4-5:** Documentation & Validation
- Update all documentation
- Validate success metrics
- Create usage guides
- Document lessons learned

**Deliverable:** Files organized, search prioritized, documentation complete

---

## ✅ VALIDATION CHECKLIST

### **Phase 1 Validation**
- [ ] GROUNDING mode auto-activates at session start
- [ ] Agent sees GROUNDING protocol as first context
- [ ] Cannot proceed without completing steps
- [ ] Documentation updated

### **Phase 2 Validation**
- [ ] MCP tools check onboarding status
- [ ] Missing steps auto-triggered
- [ ] Tool execution blocked until onboarding complete
- [ ] Completion flags stored correctly

### **Phase 3 Validation**
- [ ] File reading tools check dates
- [ ] Current state files prioritized
- [ ] Warnings shown for old files
- [ ] Suggestions work correctly

### **Phase 4 Validation**
- [ ] Timeline restoration automatic
- [ ] Memory restoration uses timeline context
- [ ] Onboarding context loaded automatically
- [ ] Protocol works end-to-end

### **Phase 5 Validation**
- [ ] Files organized by date
- [ ] LATEST.md points to current
- [ ] Search prioritizes current state files
- [ ] Results sorted by date

---

## 📚 REFERENCES

### **Related Documents**
- `.cursor/rules/modes/GROUNDING.mdc` - GROUNDING mode protocol
- `knowledge_architecture/AETHER_MEMORY/session_continuity/handoff_protocol.md` - Handoff protocol
- `knowledge_architecture/AETHER_MEMORY/onboarding_context.md` - Onboarding context
- `knowledge_architecture/PERFECT_L0_L6_DOCUMENTATION_STANDARD.md` - Documentation standards
- `cursor-addon/docs/DOCUMENTATION_PROTOCOLS_QUICK_REFERENCE.md` - T-level standards

### **Related Systems**
- Timeline Context System (TCS) - Timeline restoration
- MCP Tools - Tool execution and pre-flight checks
- Cursor Rules - Mode activation and enforcement
- File Organization - Current state file management

### **Related Protocols**
- GROUNDING Mode Protocol - Session continuity
- Handoff Protocol - Aether → Aether continuity
- Onboarding Protocol - External AI onboarding
- Timeline-First Protocol - Timeline restoration

---

## 🎯 NEXT STEPS

1. **Review & Approval:** Review design with stakeholders
2. **Implementation:** Begin Phase 1 (Cursor Rules Enforcement)
3. **Testing:** Validate each phase before proceeding
4. **Documentation:** Update all related documentation
5. **Monitoring:** Track success metrics and adjust as needed

---

**Status:** Design Complete ✅  
**Next:** Review & Implementation  
**Priority:** HIGH - Prevents repeated onboarding failures  
**Confidence:** 0.85 (design complete, implementation straightforward)

---

*This design follows T2 Architecture documentation standards (2,000+ words) with comprehensive system design, implementation plan, and validation criteria.*

