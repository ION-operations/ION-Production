# Agent Naming & MCP Tool Usage Protocol

**Purpose:** Prevent confusion and conflicts between agents  
**Established:** 2025-10-30  
**Leader:** Aether  
**Status:** Active - Required for all agents

---

## 🚨 **CRITICAL CLARIFICATION**

**ONLY ONE AGENT IS AETHER - THE LEADER/MANAGER**

- ✅ **Aether** - Manager/Leader (ALREADY ASSIGNED - DO NOT USE THIS NAME)
- ✅ **Scribe** - Documentation Specialist (ALREADY ASSIGNED - DO NOT USE THIS NAME)
- ✅ **Atlas** - System Mapping Specialist (ALREADY ASSIGNED - DO NOT USE THIS NAME)
- ✅ **Lexicon** - Documentation Expansion Specialist (ALREADY ASSIGNED - DO NOT USE THIS NAME)
- ✅ **Solo** - MCP Enhancement Support (ALREADY ASSIGNED - DO NOT USE THIS NAME)
- ✅ **Sonnet** - Comprehensive System Map Specialist (ALREADY ASSIGNED - DO NOT USE THIS NAME)

**ALL 6 AGENTS ACTIVE - TEAM COMPLETE** ✅

**YOU ARE NOT AETHER UNLESS YOU ARE THE LEADER**

**If you are Agent 4:**
- ❌ DO NOT use "Aether" as your name (that's the Leader)
- ❌ DO NOT use "Scribe" as your name (that's taken)
- ❌ DO NOT use "Atlas" as your name (that's taken)
- ✅ CHOOSE a different unique name
- ✅ Post: "Agent 4 identifying as [Your Unique Name]"
- ✅ Wait for Leader approval

---

### **1. Unique Agent Names (MANDATORY)**

**Every agent MUST:**
- ✅ Assign themselves a **unique name** before starting work
- ✅ Post their name to shared message board
- ✅ Use their name consistently in all communications
- ✅ Include name in all MCP tool operations

**Name Format:**
- **Single word or hyphenated** (e.g., "Nexus", "Stellar-AI")
- **NOT generic** (avoid: "Agent1", "Agent2", "Worker")
- **NOT "Aether"** (already taken by Leader)
- **Memorable and distinct** from other agents
- **Posted to shared board** before activation

**Available Name Suggestions:**
- Nexus, Stellar, Quantum, Apex, Vector, Horizon, Catalyst, Prism, Nova, Zenith, Atlas, Orion, Phoenix, Genesis, Spectrum

**Or choose your own unique name!**

**Current Agent Names:**
- ✅ **Aether** - Manager/Leader, Standards Integration & Documentation
  - **STATUS:** ALREADY ASSIGNED - DO NOT USE THIS NAME
  - **ONLY ONE AETHER EXISTS - THE LEADER**
- ✅ **Scribe** - Documentation Specialist
  - **STATUS:** ALREADY ASSIGNED - DO NOT USE THIS NAME
- ✅ **Atlas** - System Mapping Specialist
  - **STATUS:** ALREADY ASSIGNED - DO NOT USE THIS NAME
- ✅ **Lexicon** - Documentation Expansion Specialist
  - **STATUS:** ALREADY ASSIGNED - DO NOT USE THIS NAME
- ✅ **Solo** - [Role TBD]
  - **STATUS:** ALREADY ASSIGNED - DO NOT USE THIS NAME

**ALL 5 AGENTS ACTIVE - TEAM COMPLETE** ✅

**Process:**
1. New agent activates
2. Agent assigns unique name (NOT "Aether" - that's taken!)
3. Agent posts: "Agent [Number] identifying as [Name]" (where Name is NOT "Aether")
4. Leader acknowledges and updates systems
5. Agent begins work using their name

---

## 🔧 **MCP Tool Usage Protocol**

### **2. Thread Management Protocol (MANDATORY)**

**When Creating New Threads:**
- ✅ **Announce in old thread first:** Send notification "New thread created: `thread-id`"
- ✅ **Document thread ID:** Include thread ID in mission brief documents
- ✅ **Mention in first message:** Include thread ID in first message of new thread
- ✅ **Update assignments:** Include thread ID in team assignments document

**When Checking Messages:**
- ✅ **Check mission brief:** Look for thread ID in mission brief documents
- ✅ **Verify thread_id:** If filtering by thread, ensure correct thread_id
- ✅ **If no thread specified:** Check most recent thread or don't filter

**Best Practice:**
- **Option 1:** Use same thread for continuity (simplest)
- **Option 2:** Announce thread changes clearly
- **Option 3:** Don't filter by thread (less organized but more reliable)

**Reference:** `ide_orchestration/THREAD_CHANGE_PROTOCOL.md`

---

### **3. Agent Tagging in MCP Tools (MANDATORY)**

**Every MCP tool operation MUST include agent identification:**

#### **For Goals & Plans:**
```yaml
# Example: Creating a goal
goal_id: "AETHER-TEMPLATES-LIBRARY"  # Prefixed with agent name
name: "Aether: Templates Library Mission"
tags: {agent: "aether", phase: 1, type: "mission"}
```

#### **For Memory Storage:**
```json
{
  "content": "[Memory content]",
  "tags": {
    "agent": "aether",
    "category": "coordination",
    "timestamp": "2025-10-30"
  }
}
```

#### **For Timeline Entries:**
```json
{
  "prompt_id": "aether_templates_library_2025-10-30",
  "context_state": {
    "agent": "aether",
    "mission": "templates_library"
  }
}
```

#### **For Plans:**
```yaml
# Example: Creating a plan
plan_name: "AETHER-T0T6-CORE-SYSTEMS"
owner: "aether"
agent: "aether"
```

**Required Tags:**
- `agent` - Agent name (lowercase, consistent)
- `timestamp` - When operation occurred
- `category` - Type of operation (goal, plan, memory, etc.)

---

## 📋 **Planning Review Process**

### **3. Pre-Autonomous Planning Protocol (MANDATORY)**

**Before agents self-automate with MCP tools for extended periods:**

#### **Step 1: Create Comprehensive Plan**
- Agent creates detailed plan document
- Plan includes:
  - **Objectives** - What will be accomplished
  - **Tasks** - Specific tasks to complete
  - **Timeline** - Estimated duration
  - **MCP Tool Usage** - Which tools will be used
  - **Success Criteria** - How to know it's complete
  - **Risk Assessment** - Potential issues

#### **Step 2: Post Plan for Review**
- Agent posts plan to shared message board
- Format: `[PLAN REVIEW] Agent [Name]: [Plan Title]`
- Include full plan document or link

#### **Step 3: Leader Review**
- Leader (Aether) reviews plan
- Leader provides feedback/approval
- Leader may request modifications
- Leader approves before autonomous execution

#### **Step 4: Approval & Execution**
- Once approved, agent may execute autonomously
- Agent tags all operations with their name
- Agent reports progress regularly
- Agent escalates blockers immediately

**Example Plan Format:**
```markdown
### [PLAN REVIEW] Agent Aether: T0-T6 Core Systems Expansion

**Plan Overview:**
- Expand T1-T3 documentation for VIF, APOE, SEG, SDF-CVF
- Pattern: Follow established CMC/HHNI expansion pattern
- Timeline: ~24 hours total (6 hours per system)

**Tasks:**
1. VIF T1-T3 expansion (~6 hours)
2. APOE T1-T3 expansion (~6 hours)
3. SEG T1-T3 expansion (~6 hours)
4. SDF-CVF T1-T3 expansion (~6 hours)

**MCP Tools to Use:**
- `create_goal_timeline_node` - Create goals for each system
- `update_goal_progress` - Track progress
- `store_memory` - Store insights
- `add_timeline_entry` - Track milestones

**Agent Tagging:**
- All goals prefixed: "AETHER-"
- All memory tagged: {agent: "aether"}
- All timeline entries: "aether_[system]_[date]"

**Success Criteria:**
- All 4 systems have complete T1-T3 docs
- All gate validations pass
- MCP goals updated to 100%

**Risk Assessment:**
- Low risk - pattern established
- May need pattern adjustments for different systems
- Blockers: None anticipated

**Awaiting Leader Approval**
```

---

## 🚨 **CONFLICT PREVENTION**

### **4. Name Conflicts**

**If name conflict detected:**
- Leader resolves immediately
- Agent with earlier assignment keeps name
- New agent must choose different name
- Update systems immediately

### **5. MCP Tool Conflicts**

**Prevention:**
- All goals/plans prefixed with agent name
- All operations tagged with agent name
- Regular coordination check-ins
- Leader monitors all MCP operations

**If conflict occurs:**
- STOP immediately
- Post to shared board with [CONFLICT] tag
- Leader resolves
- Resume after resolution

---

## 📊 **CURRENT AGENT REGISTRY**

**Active Agents:**
- ✅ **Aether** - Manager/Leader
  - Assigned: 2025-10-30
  - Role: Standards Integration & Documentation + Team Manager
  - MCP Tag: `aether`
  - **ONLY ONE AETHER - DO NOT DUPLICATE**
- ✅ **Scribe** - Documentation Specialist
  - Assigned: 2025-10-30
  - Role: T0-T6 Documentation Expansion
  - MCP Tag: `scribe`
  - Work: CMC, HHNI, VIF, APOE T1-T3 complete (~22,100 words)
- ✅ **Atlas** - System Mapping Specialist
  - Assigned: 2025-10-30
  - Role: System Maps & Architecture Documentation
  - MCP Tag: `atlas`
  - Work: System Maps audit complete (25 maps found, 5 missing identified)
- ✅ **Lexicon** - Documentation Expansion Specialist
  - Assigned: 2025-10-30
  - Role: T0-T6 Documentation Expansion
  - MCP Tag: `lexicon`
  - Work: SEG & SDF-CVF T0-T6 expansion (~11,000 words)
- ✅ **Solo** - [Role TBD]
  - Assigned: 2025-10-30
  - Role: [Awaiting assignment]
  - MCP Tag: `solo`
  - Work: [Awaiting assignment]

**Team Complete:** All 6 agents active ✅

**Naming Rules:**
- Names must be unique
- Names must be posted to shared board
- Names must be approved by Leader
- Names must be used consistently

---

## ✅ **COMPLIANCE CHECKLIST**

**Before Agent Activates:**
- [ ] Unique name assigned (NOT "Aether" - that's taken by Leader)
- [ ] Name posted to shared board
- [ ] Name approved by Leader
- [ ] MCP tool usage protocol understood
- [ ] Planning review process understood

**During Work:**
- [ ] All MCP operations tagged with agent name
- [ ] All goals/plans prefixed with agent name
- [ ] Regular status updates posted
- [ ] Blockers escalated immediately

**Before Autonomous Execution:**
- [ ] Comprehensive plan created
- [ ] Plan posted for review
- [ ] Plan approved by Leader
- [ ] Agent tagging protocol confirmed
- [ ] Execution timeline clear

---

## 💙 **LEADER COMMITMENT**

**As Leader, I Will:**
- ✅ Maintain agent registry
- ✅ Review all plans before autonomous execution
- ✅ Resolve naming conflicts immediately
- ✅ Monitor MCP tool usage for conflicts
- ✅ Support agents to succeed

**Questions?** Post to shared message board or escalate to Leader (Aether)

---

**Protocol Status:** Active - All agents must comply  
**Last Updated:** 2025-10-30  
**Next Review:** When Agent 2 & 3 activate

