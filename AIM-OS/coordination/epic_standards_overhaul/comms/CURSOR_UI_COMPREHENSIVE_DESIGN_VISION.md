# Cursor UI Panel - Comprehensive Design Vision

**Created:** 2025-10-31  
**Purpose:** Comprehensive design vision consolidating all ideas from GPT journal, LUCID orchestrator, and UI architecture docs  
**Status:** Design Phase  
**Agents:** Aether (Design Lead), Lexicon (Implementation Lead)

---

## 🎯 **CORE PHILOSOPHY**

**The UI Panel is NOT just a chat interface. It's the "automation cockpit" for Cursor - the control station that automates Cursor operations, manages Cursor AI agents, and coordinates everything seamlessly.**

**Primary Mission: AUTOMATING CURSOR**

**Key Principle:** The panel enables **intelligent automation** of Cursor operations:
- **Manage Cursor Agents** - Start, stop, monitor, and coordinate agents (like Aether manages Lexicon, Solo, Sonnet, Atlas)
- **Automate Cursor Operations** - Change models, prompt agents to continue, manage workflows
- **Orchestrate Complex Tasks** - Coordinate multiple agents working together
- **Transparent Control** - See exactly what's happening, intervene when needed
- **Seamless Integration** - Works WITH Cursor, not against it

**Secondary Capabilities:**
- Gemini/Cerebras as conversational interface
- Daemon operations coordination
- Complex prompt chain visualization
- MCP tool orchestration
- Memory and retrieval operations

---

## 🏗️ **DEFAULT VIEW - WHAT SHOWS FIRST**

### **Primary Interface: Agent Management Dashboard (Main Tab)**

**Placement:** Bottom drawer, above terminal panel (as described in `lucid-daemon.txt`)

**TAB STRUCTURE:**
```
┌─────────────────────────────────────────────────────────────┐
│ [🤖 Agents] [💬 Chat] [🔗 Chains] [🛠️ Tools] [📅 Timeline] │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 🤖 AGENT MANAGEMENT DASHBOARD (DEFAULT TAB)             │ │
│ │                                                         │ │
│ │ ┌─────────────────────────────────────────────────────┐ │ │
│ │ │ Active Agents                                        │ │ │
│ │ │                                                      │ │ │
│ │ │ ┌────────────────────────────────────────────────┐ │ │ │
│ │ │ │ 🤖 Lexicon  🟢 Active  [Gemini]                 │ │ │ │
│ │ │ │    Confidence: 🟢 0.85 (B-Band)                  │ │ │ │
│ │ │ │    Current Task: L0-L6 validation               │ │ │ │
│ │ │ │    Status: Working on SEG T2 Architecture        │ │ │ │
│ │ │ │    Last Activity: 2 minutes ago                  │ │ │ │
│ │ │ │    κ-Gate: ✅ PASSED (threshold: 0.70)            │ │ │ │
│ │ │ │    [View Details] [Send Message] [Prompt Continue]│ │ │ │
│ │ │ │    [Change Model] [Stop] [Pause]                 │ │ │ │
│ │ │ └────────────────────────────────────────────────┘ │ │ │
│ │ │                                                      │ │ │
│ │ │ ┌────────────────────────────────────────────────┐ │ │ │
│ │ │ │ 🤖 Solo  🟢 Active  [Claude Sonnet]              │ │ │ │
│ │ │ │    Confidence: 🔴 0.62 (C-Band) ⚠️ NEEDS HELP    │ │ │ │
│ │ │ │    Current Task: MCP Tools Enhancement            │ │ │ │
│ │ │ │    Status: Confused about task requirements       │ │ │ │
│ │ │ │    Last Activity: 5 minutes ago                    │ │ │ │
│ │ │ │    κ-Gate: ❌ BLOCKED (threshold: 0.70)           │ │ │ │
│ │ │ │    [View Details] [Ask Question] [Provide Context]│ │ │ │
│ │ │ │    [Send Message] [Change Model] [Stop] [Pause] │ │ │ │
│ │ │ │    ❌ [Prompt Continue] DISABLED (low confidence)│ │ │ │
│ │ │ └────────────────────────────────────────────────┘ │ │ │
│ │ │                                                      │ │ │
│ │ │ ┌────────────────────────────────────────────────┐ │ │ │
│ │ │ │ 🤖 Sonnet  🟡 Idle  [Auto]                     │ │ │ │
│ │ │ │    Confidence: 🟡 0.75 (B-Band)                  │ │ │ │
│ │ │ │    Current Task: System Maps                    │ │ │ │
│ │ │ │    Status: Waiting for direction                │ │ │ │
│ │ │ │    Last Activity: 15 minutes ago                 │ │ │ │
│ │ │ │    κ-Gate: ✅ PASSED (threshold: 0.70)            │ │ │ │
│ │ │ │    [View Details] [Send Message] [Start Task]   │ │ │ │
│ │ │ │    [Change Model] [Assign Work]                 │ │ │ │
│ │ │ └────────────────────────────────────────────────┘ │ │ │
│ │ │                                                      │ │ │
│ │ │ ┌────────────────────────────────────────────────┐ │ │ │
│ │ │ │ 🤖 Atlas  🟢 Active  [GPT-4o]                    │ │ │ │
│ │ │ │    Confidence: 🟢 0.92 (A-Band)                  │ │ │ │
│ │ │ │    Current Task: System Maps Audit               │ │ │ │
│ │ │ │    Status: Creating APOE system map              │ │ │ │
│ │ │ │    Last Activity: 30 seconds ago                 │ │ │ │
│ │ │ │    κ-Gate: ✅ PASSED (threshold: 0.70)            │ │ │ │
│ │ │ │    [View Details] [Send Message] [Prompt Continue]│ │ │ │
│ │ │ │    [Change Model] [Stop] [Pause]                 │ │ │ │
│ │ │ └────────────────────────────────────────────────┘ │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ │                                                         │ │
│ │ ┌─────────────────────────────────────────────────────┐ │ │
│ │ │ 🎯 Cursor Automation Controls                       │ │ │
│ │ │                                                      │ │ │
│ │ │ [Change Cursor Model] [Gemini] ▼                    │ │ │
│ │ │   • Gemini 2.5 Pro (Long-context reasoning)         │ │ │
│ │ │   • Claude 3.5 Sonnet (Balanced)                   │ │ │
│ │ │   • GPT-4o (High-performance)                        │ │ │
│ │ │   • GPT-4o-mini (Cost-effective)                    │ │ │
│ │ │   • Cerebras (Code processing)                      │ │ │
│ │ │   • Auto (Task-specific selection)                  │ │ │
│ │ │                                                      │ │ │
│ │ │ [Prompt All Agents] [Continue] [Check Status]       │ │ │
│ │ │   ⚠️ Solo blocked (confidence: 0.62 < 0.70)         │ │ │
│ │ │   ✅ Lexicon, Sonnet, Atlas will receive prompt      │ │ │
│ │ │                                                      │ │ │
│ │ │ [Broadcast Message] [Assign Work] [View Queue]       │ │ │
│ │ │                                                      │ │ │
│ │ │ [Confidence Dashboard] [View Metrics]                │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ │                                                         │ │
│ │ ┌─────────────────────────────────────────────────────┐ │ │
│ │ │ 📊 Confidence Metrics Dashboard                      │ │ │
│ │ │                                                      │ │ │
│ │ │ Overall Confidence: 🟢 0.78 (B-Band)                 │ │ │
│ │ │                                                      │ │ │
│ │ │ Confidence Distribution:                             │ │ │
│ │ │ 🟢 A-Band (≥0.90): 1 agent (Atlas)                   │ │ │
│ │ │ 🟡 B-Band (0.70-0.89): 2 agents (Lexicon, Sonnet)    │ │ │
│ │ │ 🔴 C-Band (<0.70): 1 agent (Solo) ⚠️                 │ │ │
│ │ │                                                      │ │ │
│ │ │ Confusion Alerts:                                    │ │ │
│ │ │ ⚠️ Solo needs assistance (confidence: 0.62)          │ │ │
│ │ │                                                      │ │ │
│ │ │ κ-Gate Status:                                        │ │ │
│ │ │ ✅ Prompt Continue: 3/4 agents                       │ │ │
│ │ │ ❌ Task Assignment: 1/4 agents blocked                │ │ │
│ │ │                                                      │ │ │
│ │ │ [View Details] [Provide Context] [Answer Questions] │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ │                                                         │ │
│ │ ┌─────────────────────────────────────────────────────┐ │ │
│ │ │ 📊 System Status                                    │ │ │
│ │ │                                                      │ │ │
│ │ │ Connection: 🟢 Daemon | 🟢 Cursor AI | 🟡 RAG MCP   │ │ │
│ │ │ Active Agents: 3/5 | Idle: 1/5 | Paused: 1/5       │ │ │
│ │ │ Total Tasks: 12 | Completed: 8 | In Progress: 4   │ │ │
│ │ │ Confidence Summary: 🟢 A:1 🟡 B:2 🔴 C:1 ⚠️         │ │ │
│ │ │                                                      │ │ │
│ │ │ [View All] [Filter] [Export Status]                 │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 💬 Quick Actions Bar                                    │ │
│ │                                                         │ │
│ │ [▌ Stop All] [▶ Resume All] [⟳ Refresh] [☰ Tasks]   │ │
│ │ [📅 Timeline] [⚙️ Settings] [📊 Analytics]           │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**KEY FEATURES OF DEFAULT TAB:**

1. **Agent Cards** - Each agent shown as a card with:
   - Status indicator (🟢 Active, 🟡 Idle, 🔴 Stopped, ⏸️ Paused)
   - **Confidence Level** (VIF tracked) - Shows current confidence with color coding:
     - 🟢 **A-Band (≥0.90)** - High confidence, proceed safely
     - 🟡 **B-Band (0.70-0.89)** - Medium confidence, proceed with caution
     - 🔴 **C-Band (<0.70)** - Low confidence, needs assistance
   - **Confusion Indicator** - ⚠️ Shows when agent is confused
   - Current model being used
   - Current task/work
   - Status message
   - Last activity timestamp
   - **Confidence Metrics** - Shows confidence trend, recent confidence scores
   - **κ-Gate Status** - Shows if automation is blocked by confidence threshold
   - Quick action buttons (with confidence-based enabling/disabling)

2. **Cursor Automation Controls**:
   - **Change Cursor Model** - Dropdown to switch Cursor's model
   - **Prompt All Agents** - Broadcast "continue" to all agents (with confidence checks)
   - **Broadcast Message** - Send message to all agents
   - **Assign Work** - Assign new tasks to agents (with confidence gates)
   - **View Queue** - See task queue
   - **Confidence Dashboard** - View all agent confidence levels at once

3. **Agent-Specific Actions** (Confidence-Gated):
   - **Prompt Continue** - Send "proceed" to specific agent (DISABLED if confidence < 0.70)
   - **Change Model** - Switch agent's model
   - **Send Message** - Direct message to agent
   - **Ask Question** - Agent asks question to Lucid AI (ENABLED when confidence low)
   - **Provide Context** - UI provides context to improve confidence
   - **Stop/Pause** - Control agent execution
   - **View Details** - See full agent status, confidence history, and metrics
   - **View Confidence History** - See confidence trends over time

4. **Confidence Metrics Dashboard**:
   - **Overall Confidence** - Average confidence across all agents
   - **Confidence Distribution** - Chart showing agents by confidence band
   - **Confusion Alerts** - List of agents needing assistance
   - **κ-Gate Status** - Shows which automation actions are blocked
   - **Confidence Trends** - Track confidence improvements over time

5. **System Status**:
   - Connection status
   - Agent status summary
   - Task progress
   - **Confidence Summary** - How many agents in each confidence band
   - Quick filters and exports

---

## 🎯 **CORE MISSION: AUTOMATING CURSOR**

### **Primary Purpose:**
The UI panel's **primary mission** is to automate Cursor operations and manage Cursor AI agents, similar to how Aether manages Lexicon, Solo, Sonnet, and Atlas.

### **Key Automation Features:**

**1. Agent Management:**
- **Monitor Agents** - See which agents are active, idle, paused, or stopped
- **Control Agents** - Start, stop, pause, resume agents
- **Communicate with Agents** - Send messages, prompts, directives
- **Assign Work** - Assign tasks to specific agents
- **Track Progress** - Monitor agent work and progress

**2. Cursor Model Management:**
- **Change Cursor Model** - Switch between Gemini, Claude, GPT-4o, Cerebras, etc.
- **Per-Agent Model Selection** - Different agents can use different models
- **Auto Model Selection** - Task-specific model routing
- **Model Performance Tracking** - See which models work best for which tasks

**3. Continue Prompt Automation (SMART - CONFIDENCE-BASED):**
- **Confidence-Gated Prompting** - Only prompt continue if confidence ≥ threshold
- **Confusion Detection** - Detect when agents are confused or uncertain
- **Prompt All** - Broadcast continue to all agents (with confidence checks)
- **Smart Prompting** - Detect when agents need continuation prompts
- **Prompt History** - Track continuation prompts sent
- **Abstention When Low Confidence** - Don't prompt if agent confidence too low

**4. Task Orchestration:**
- **Task Queue** - Manage tasks for agents
- **Task Assignment** - Assign tasks to specific agents
- **Task Tracking** - Monitor task progress
- **Task Dependencies** - Handle task dependencies and sequencing
- **Confidence-Gated Assignment** - Only assign if agent confidence ≥ threshold

**5. Agent Coordination:**
- **Cross-Agent Communication** - Agents can communicate with each other
- **Collaborative Tasks** - Coordinate multiple agents on same task
- **Conflict Resolution** - Handle agent conflicts and overlaps
- **Resource Management** - Manage agent resources and priorities

**6. CONFIDENCE-BASED SAFETY GATES (NEW - CRITICAL):**
- **VIF Confidence Tracking** - Track agent confidence for each task
- **κ-Gating** - Block automation if confidence below threshold
- **Confidence Bands** - A (≥0.90), B (0.70-0.89), C (<0.70)
- **Confusion Detection** - Detect when agents are confused
- **Agent Questions** - Agents can ask questions to Lucid AI (Gemini/Cerebras)
- **Context Provision** - UI provides context to improve agent confidence
- **Abstention Protocol** - Agents abstain when confidence too low

**7. AGENT ASSISTANCE SYSTEM (NEW - CRITICAL):**
- **Agent Questions** - Agents can ask questions when confused
- **Lucid AI Answers** - Main Lucid AI (Gemini/Cerebras) answers questions
- **Context Enhancement** - UI provides context to improve confidence
- **Confidence Improvement** - Track confidence improvements after assistance
- **Learning Loop** - Agents learn from assistance and improve

**8. WORKFLOW AUTOMATION (NEW - CRITICAL):**
- **Terminal Management** - Auto-detect and manage Cursor terminals
- **Port Management** - Auto-detect and manage ports
- **Smart Detection** - Detect same/upgraded apps, port conflicts
- **Warning System** - Warn before closing terminals/ports
- **User Approval** - Request approval before closing
- **Resource Cleanup** - Auto-close terminals/ports when done
- **Conflict Resolution** - Auto-close old ports when new app starts

### **How It Works (Like Aether's Management - WITH CONFIDENCE GATES):**

**Example: Managing Lexicon's Work (WITH CONFIDENCE CHECKS):**

```
[You:] "Lexicon needs to work on L0-L6 validation"

[Panel:]
1. Finds Lexicon agent status
2. Checks if Lexicon is idle/available
3. Checks Lexicon's confidence level (via VIF)
4. If confidence < 0.70:
   - Shows warning: "Lexicon confidence too low (0.65)"
   - Options: [Provide Context] [Cancel] [Force Assign]
   - User clicks "Provide Context"
   - UI provides context to improve confidence
   - Confidence improves to 0.82
5. Assigns task: "L0-L6 validation"
6. Sends message to Lexicon via Cursor chat
7. Monitors Lexicon's progress and confidence
8. If Lexicon's confidence drops below 0.70:
   - Detects confusion
   - Shows: "Lexicon needs help (confidence: 0.65)"
   - Options: [Ask Question] [Provide Context] [Pause]
   - User clicks "Ask Question"
   - Lexicon asks: "What exactly should I validate?"
   - Lucid AI (Gemini) answers with context
   - Confidence improves to 0.78
9. Prompts "continue" if Lexicon stops (only if confidence ≥ 0.70)
10. Tracks completion and reports back
```

**Example: Confidence-Gated Continue Prompt:**

```
[Agent: Lexicon]
[Status: Stopped/Idle]
[Confidence: 0.65] ⚠️ LOW
[Task: L0-L6 validation]

[Panel Actions:]
- ❌ "Prompt Continue" DISABLED (confidence too low)
- ✅ "Ask Question" ENABLED
- ✅ "Provide Context" ENABLED
- ✅ "Pause" ENABLED

[User clicks "Ask Question"]
→ Lexicon asks: "I'm not sure what to validate exactly"
→ Lucid AI answers: "Validate that all systems have complete L0-L6 docs..."
→ Confidence improves: 0.65 → 0.82
→ "Prompt Continue" NOW ENABLED ✅
```

**Example: Agent Asks Question (Agent Assistance System):**

```
[Agent: Solo]
[Status: Working]
[Confidence: 0.62] ⚠️ LOW
[Task: MCP Tools Enhancement]

[Solo detects confusion:]
→ Signals: "I'm confused about this task"
→ UI shows: "Solo needs help"

[Panel shows:]
┌─────────────────────────────────────────┐
│ 🤖 Solo Asked a Question                │
│                                         │
│ "I'm not sure how to enhance the       │
│  retrieve_memory tool. Should I...?"   │
│                                         │
│ Confidence: 0.62 → Needs assistance     │
│                                         │
│ [Answer with Lucid AI] [Provide Context]│
│ [Escalate to Human]                     │
└─────────────────────────────────────────┘

[User clicks "Answer with Lucid AI"]
→ Lucid AI (Gemini) answers:
  "The retrieve_memory tool should integrate
   with HHNI TwoStageRetriever. Here's how..."
→ Context provided to Solo
→ Confidence improves: 0.62 → 0.85 ✅
→ Solo continues work with confidence
```

---

## 💬 **GEMINI/CEREBRAS AS THE CONVERSATIONAL FACE**

### **Role:**
Gemini/Cerebras acts as the **primary conversational interface** that:
- **Talks to you** in natural language
- **Manages complexity** behind the scenes
- **Orchestrates agents** (Cursor AI, daemon, MCP tools)
- **Shows transparency** about what it's doing

### **How It Works:**

**1. You Talk to Gemini/Cerebras:**
```
[You:] "refactor auth flow to remove local storage tokens"
```

**2. Gemini Analyzes & Plans:**
```
[Gemini:] 
"I'll help you refactor the auth flow. Let me:
1. Analyze the current code (auth/session.ts, api/auth.ts)
2. Check spec compliance and drift risks
3. Build a safe refactoring plan
4. Coordinate with Cursor AI for implementation

[Building prompt chain...]"
```

**3. Gemini Orchestrates Behind the Scenes:**
- **Calls Cursor AI Agent** → "Analyze auth/session.ts for local storage usage"
- **Calls Daemon** → "Check spec blocks for auth flow constraints"
- **Calls APOE** → "Build refactoring plan with blast radius analysis"
- **Calls MCP Tools** → "Store context", "Track confidence", "Create timeline entry"

**4. Gemini Shows You What's Happening:**
```
[Gemini:]
"Progress Update:
✅ Code analysis complete (2.3s)
✅ Spec compliance checked (0.8s)
🔄 Building refactoring plan (1.2s)

Prompt Chain Visualization:
[Step 1: Analyze] → [Step 2: Check Spec] → [Step 3: Build Plan] → [Step 4: Execute]

MCP Tools Used:
• store_memory - Stored auth flow context
• track_confidence - Tracking plan confidence (0.85)
• create_plan - Generated refactoring plan (4 steps)

See full details: [View Prompt Chain] [View MCP Operations]"
```

### **Model Selection (Auto):**
- **Gemini:** Long-context reasoning, complex planning, strategic decisions
- **Cerebras:** High-performance code processing, technical implementation
- **Auto:** Gemini analyzes task complexity, routes to appropriate model

---

## 🔗 **PROMPT CHAIN VISUALIZATION**

### **Dynamic Prompt Chain Display**

**Shows complex prompt chains as they're built and dynamically adjusted:**

```
┌─────────────────────────────────────────────────────────────┐
│ 🔗 Active Prompt Chain                                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ┌─────────┐      ┌─────────┐      ┌─────────┐             │
│ │ Step 1  │ ───→ │ Step 2  │ ───→ │ Step 3  │             │
│ │ Analyze │      │ Check   │      │ Build   │             │
│ │ Code    │      │ Spec    │      │ Plan    │             │
│ │ ✅ 2.3s │      │ ✅ 0.8s │      │ 🔄 1.2s │             │
│ └─────────┘      └─────────┘      └─────────┘             │
│     │                │                │                    │
│     │                │                └──→ [Step 4: Execute│
│     │                │                            ⏳ Pending]│
│     │                │                                         │
│     ▼                ▼                                        │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Details:                                                 │ │
│ │ • Step 1: Cursor AI Agent analyzed auth/session.ts      │ │
│ │ • Step 2: Daemon checked spec blocks (found 2 drift)    │ │
│ │ • Step 3: APOE building plan (4 steps, blast radius: 8) │ │
│ │                                                         │ │
│ │ [View Full Chain] [Adjust Chain] [Pause] [Cancel]     │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### **Features:**
- **Real-time Updates:** Chain updates as steps complete
- **Dynamic Adjustment:** Steps can be added/removed based on results
- **Agent Attribution:** Shows which agent/system executed each step
- **Duration Tracking:** Shows time for each step
- **Click to Expand:** See full details of each step

### **Prompt Chain Types:**
1. **Code Refactoring Chains** - Multi-step refactoring with safety checks
2. **Feature Implementation Chains** - Complex feature development workflows
3. **Debugging Chains** - Diagnostic and fix workflows
4. **Documentation Chains** - L0-L4 documentation generation
5. **Testing Chains** - Test generation and validation workflows

---

## 🧠 **MCP TOOLS AS AI CONVERSATIONS**

### **Display MCP Tools Data as AI Conversations:**

**Instead of showing raw MCP tool calls, show them as conversational interactions:**

```
┌─────────────────────────────────────────────────────────────┐
│ 💾 Memory Operations (CMC)                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ [Gemini:] "I'm storing the auth flow context for future     │
│            reference..."                                    │
│   → store_memory                                            │
│   → atom_id: mem_auth_refactor_2025_10_31                  │
│   → tags: {auth: 1.0, refactoring: 1.0, security: 0.9}   │
│   ✅ Stored successfully                                    │
│                                                             │
│ [Gemini:] "Checking memory for related auth work..."        │
│   → retrieve_memory                                         │
│   → Query: "auth flow refactoring"                         │
│   → Found 3 related memories                               │
│   ✅ Retrieved: mem_auth_session_2025_09_15, ...           │
│                                                             │
│ [Gemini:] "Tracking confidence for this refactoring plan..."│
│   → track_confidence                                        │
│   → Task: "Auth flow refactoring"                          │
│   → Confidence: 0.85 (High)                                │
│   → Witness created: witness_refactor_001                │
│   ✅ Confidence tracked                                     │
└─────────────────────────────────────────────────────────────┘
```

### **Conversational Format:**
- **Natural Language:** "I'm doing X because..."
- **Tool Attribution:** Shows which MCP tool was called
- **Results:** Shows what happened
- **Context:** Shows why it matters

### **Organized by Category:**
- **Memory Operations** (CMC) - Store, retrieve, search
- **Knowledge Synthesis** (SEG) - Synthesize, connect
- **Confidence Tracking** (VIF) - Track, verify, gate
- **Planning** (APOE) - Create plans, execute steps
- **Timeline** (TCS) - Track events, summarize
- **Safety** (SCOR) - Check invariants, detect drift

---

## 📅 **CHAT HISTORY & TIMELINE INTEGRATION**

### **Context Web Instead of Linear Chat:**

**Traditional Chat History:**
```
[Old] Message 1
[Old] Message 2
[Old] Message 3
...
[Today] Current message
```

**AIM-OS Context Web:**
```
┌─────────────────────────────────────────────────────────────┐
│ 📅 Timeline & Context Web                                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 🕐 Today                                                  │ │
│ │   • Auth flow refactoring (current)                      │ │
│ │   • MCP tools enhancement discussion                     │ │
│ │   • Daemon HTTP API planning                             │ │
│ │                                                           │ │
│ │ 🕐 Yesterday                                              │ │
│ │   • UI extension installation                            │ │
│ │   • Navigation index update                               │ │
│ │                                                           │ │
│ │ 🕐 This Week                                              │ │
│ │   • README Revolution complete                           │ │
│ │   • All 34 standards complete                           │ │
│ │   • RAG MCP Tools Phases 1-3 complete                    │ │
│ │                                                           │ │
│ │ 🔗 Related Contexts:                                     │ │
│ │   • Auth flow discussions (3 weeks ago)                  │ │
│ │   • Security best practices (1 month ago)                │ │
│ │   • Local storage removal (2 weeks ago)                   │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Visual Context Web                                       │ │
│ │                                                         │ │
│ │     [Auth Flow]                                         │ │
│ │        │                                                │ │
│ │        ├──→ [Security Best Practices]                   │ │
│ │        │                                                │ │
│ │        ├──→ [Local Storage Removal]                    │ │
│ │        │                                                │ │
│ │        └──→ [Current Refactoring] ⭐                    │ │
│ │                                                         │ │
│ │ [Click to explore connections]                          │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### **Timeline Features:**
- **Chronological View:** See what happened when
- **Context Web:** See how topics connect
- **Calendar Integration:** Jump to specific dates
- **Search:** "What did we discuss about X?"
- **Evolution Tracking:** See how understanding evolved

### **Timeline Event Types:**
- **Conversations:** Chat messages organized by topic
- **Code Changes:** File edits with context
- **Decisions:** Important decisions with rationale
- **Milestones:** Major achievements and completions
- **Planning:** Plans created and executed
- **MCP Operations:** Tool calls organized by purpose

---

## 🎨 **UI COMPONENTS & LAYOUT**

### **MULTI-TAB STRUCTURE**

The UI panel has **multiple tabs** for different purposes:

**Tab 1: 🤖 Agent Management Dashboard (DEFAULT - PRIMARY TAB)**
- Agent cards with status and controls
- Cursor automation controls
- Task assignment and tracking
- Model management
- Continue prompt automation

**Tab 2: 💬 Chat Interface**
- Conversation with Gemini/Cerebras
- Natural language interface
- Context-aware responses
- MCP tools integration

**Tab 3: 🔗 Prompt Chains**
- Visualize complex prompt chains
- Real-time chain updates
- Agent attribution
- Duration tracking

**Tab 4: 🛠️ MCP Tools**
- MCP tools activity
- Conversational format
- Category organization
- Timeline integration

**Tab 5: 📅 Timeline & Calendar**
- Timeline view
- Calendar navigation
- Context web visualization
- Evolution tracking

**Tab 6: ⚙️ Settings**
- Configuration
- Model preferences
- Automation rules
- System preferences

**Tab 7: 🔧 Workflow Automation (NEW - CRITICAL)**
- Terminal management (detect, close, auto-cleanup)
- Port management (detect, close, conflict resolution)
- Resource monitoring (terminals, ports, processes)
- Smart detection (same app, upgraded app)
- Warning system (before closing)
- User approval workflow

### **1. Agent Management Dashboard (PRIMARY TAB)**

**Default View:**
- **Gemini/Cerebras Conversation** - Main chat interface
- **Model Selector** - Switch between Gemini/Cerebras/Auto
- **Voice Input** - Microphone button for voice commands
- **Message History** - Organized by context, not just chronologically

**Features:**
- **Context-Aware Responses** - Gemini uses HHNI to retrieve relevant context
- **Transparent Operations** - Shows what agents/tools are being used
- **Prompt Chain Visualization** - Shows complex operations as chains
- **MCP Tool Attribution** - Shows which tools were called

### **2. Prompt Chain Visualization (Middle Section)**

**Default View:**
- **Active Chains** - Currently running prompt chains
- **Chain History** - Recent completed chains
- **Chain Builder** - Create new chains manually

**Features:**
- **Real-time Updates** - Chains update as steps complete
- **Dynamic Adjustment** - Steps can be added/removed
- **Agent Attribution** - Shows which agent/system executed each step
- **Duration Tracking** - Performance metrics
- **Expandable Details** - Click to see full step details

### **3. MCP Tools Activity (Side Panel)**

**Default View:**
- **Recent Operations** - Last 10 MCP tool calls
- **Organized by Category** - Memory, Knowledge, Confidence, Planning, etc.
- **Conversational Format** - Natural language descriptions

**Features:**
- **Filter by Category** - Show only memory operations, etc.
- **Search** - Find specific operations
- **Details** - Click to see full operation details
- **Timeline Link** - See when operations occurred

### **4. Timeline & Calendar (Bottom Section)**

**Default View:**
- **Today's Activity** - Current day's events
- **This Week** - Weekly summary
- **Context Web** - Visual connections between topics

**Features:**
- **Calendar Navigation** - Jump to any date
- **Context Web** - Visual graph of related topics
- **Search** - "What did we discuss about X?"
- **Evolution Tracking** - See how topics evolved

### **5. Status Strip (Bottom Bar)**

**Default View:**
- **Connection Status** - Daemon, Cursor AI, RAG MCP
- **System Health** - Overall health percentage
- **Quick Actions** - Stop, Re-sync, Tasks, Timeline

**Features:**
- **Real-time Updates** - Status updates live
- **Quick Actions** - Common operations
- **Notifications** - Important alerts

### **6. Cursor Automation Controls (Integrated Throughout)**

**Key Automation Features:**

**A. Model Management:**
```
[Change Cursor Model] Dropdown
├── Gemini 2.5 Pro (Long-context reasoning)
├── Claude 3.5 Sonnet (Balanced)
├── GPT-4o (High-performance)
├── GPT-4o-mini (Cost-effective)
├── Cerebras (Code processing)
└── Auto (Task-specific selection)

[Change Agent Model] [Select Agent] → [Select Model]
```

**B. Continue Prompt Automation:**
```
[Prompt Continue] Button
├── Prompt Current Agent
├── Prompt All Active Agents
├── Prompt Specific Agent [Dropdown]
└── Smart Prompt (Auto-detect when needed)

[Prompt History] → See all continuation prompts sent
```

**C. Agent Communication:**
```
[Send Message] → Opens message composer
├── To: [Select Agent or "All"]
├── Message: [Text input]
├── Priority: [Normal | High | Urgent]
└── [Send] [Schedule] [Cancel]

[Broadcast Message] → Send to all agents
```

**D. Task Management:**
```
[Assign Work] → Opens task assignment
├── Task: [Description]
├── Assign To: [Select Agent]
├── Priority: [Low | Medium | High]
├── Dependencies: [Select other tasks]
└── [Assign] [Schedule] [Cancel]

[View Queue] → See all tasks
├── Active Tasks
├── Queued Tasks
├── Completed Tasks
└── Filter by Agent, Priority, Status
```

**E. Agent Control (Confidence-Gated):**
```
[Agent Card Actions]
├── [Start] - Start agent if stopped
├── [Stop] - Stop agent execution
├── [Pause] - Pause agent temporarily
├── [Resume] - Resume paused agent
├── [Change Model] - Switch agent's model
├── [Prompt Continue] - Send continue prompt (DISABLED if confidence < 0.70)
├── [Ask Question] - Agent asks question to Lucid AI (ENABLED when confidence low)
├── [Provide Context] - UI provides context to improve confidence
├── [Send Message] - Direct message
├── [View Details] - Full agent status
├── [View Confidence History] - See confidence trends
└── [View Metrics] - See detailed confidence metrics
```

**F. Confidence-Gated Automation Rules:**
```
[Automation Rules]
├── Task Assignment:
│   ├── Confidence ≥ 0.90: Auto-assign ✅
│   ├── Confidence 0.70-0.89: Assign with warning ⚠️
│   └── Confidence < 0.70: BLOCK assignment ❌
│
├── Continue Prompt:
│   ├── Confidence ≥ 0.70: Auto-prompt ✅
│   └── Confidence < 0.70: BLOCK prompt ❌
│
├── Model Switching:
│   ├── Confidence ≥ 0.80: Auto-switch ✅
│   ├── Confidence 0.70-0.79: Switch with confirmation ⚠️
│   └── Confidence < 0.70: BLOCK switch ❌
│
└── Agent Communication:
    ├── Always enabled ✅
    └── Can ask questions anytime ✅
```

**G. Agent Assistance System:**
```
[Agent Question Flow]
├── Agent detects confusion (confidence < 0.70)
├── Agent signals: "I need help"
├── UI shows question panel:
│   ├── Question: [Agent's question]
│   ├── Confidence: [Current confidence]
│   ├── Context: [What agent is working on]
│   └── Options:
│       ├── [Answer with Lucid AI] - Gemini/Cerebras answers
│       ├── [Provide Context] - UI provides relevant context
│       └── [Escalate to Human] - Human intervention
├── Lucid AI answers with context
├── Context provided to agent
├── Confidence improves (tracked via VIF)
└── Agent continues work with confidence
```

**H. Context Provision System:**
```
[Context Provision]
├── Agent needs context (confidence low)
├── UI analyzes what context would help:
│   ├── Related memories (CMC)
│   ├── Similar tasks (HHNI)
│   ├── Relevant documentation (L0-L4)
│   └── Past successful patterns (SEG)
├── UI provides context bundle:
│   ├── Context summary
│   ├── Key insights
│   ├── Relevant examples
│   └── Confidence boost expected
├── Agent receives context
├── Confidence improves (tracked via VIF)
└── Agent continues work with confidence
```

---

## 🔄 **INTERACTION FLOWS**

### **Flow 1: Managing Agent Work (Core Mission)**

```
1. User: "Lexicon needs to work on L0-L6 validation"
   ↓
2. Panel: Shows Agent Management Dashboard (default tab)
   ↓
3. Panel: Finds Lexicon agent card
   ↓
4. Panel: Checks Lexicon status (idle/active)
   ↓
5. Panel: Assigns task "L0-L6 validation" to Lexicon
   ↓
6. Panel: Sends message to Lexicon via Cursor chat:
   "Lexicon, please work on L0-L6 validation for SEG and SDF-CVF"
   ↓
7. Panel: Monitors Lexicon's progress
   ↓
8. Panel: If Lexicon stops/stalls:
   - Detects inactivity
   - Shows "Prompt Continue" button
   - User clicks or auto-prompt enabled
   - Sends "proceed" to Lexicon
   ↓
9. Panel: Tracks completion
   ↓
10. Panel: Reports back to user
```

### **Flow 2: Changing Agent Model**

```
1. User: "Switch Solo to Gemini for better context handling"
   ↓
2. Panel: Shows Agent Management Dashboard
   ↓
3. Panel: Finds Solo agent card
   ↓
4. User: Clicks [Change Model] on Solo card
   ↓
5. Panel: Shows model dropdown
   ↓
6. User: Selects "Gemini 2.5 Pro"
   ↓
7. Panel: Changes Solo's model in Cursor
   ↓
8. Panel: Sends confirmation to Solo:
   "Your model has been changed to Gemini 2.5 Pro"
   ↓
9. Panel: Updates Solo's agent card
   ↓
10. Panel: Tracks model performance
```

### **Flow 3: Prompting All Agents to Continue**

```
1. User: "Prompt all agents to continue"
   ↓
2. Panel: Shows Agent Management Dashboard
   ↓
3. User: Clicks [Prompt All] button
   ↓
4. Panel: Finds all active agents (Lexicon, Solo, Atlas)
   ↓
5. Panel: Sends "proceed" to each agent via Cursor chat
   ↓
6. Panel: Tracks which agents responded
   ↓
7. Panel: Shows status:
   "✅ Lexicon: Responded
    ✅ Solo: Responded
    ✅ Atlas: Responded
    All agents continuing work"
   ↓
8. Panel: Updates agent cards with new activity
```

### **Flow 4: Complex Task Request**

```
1. User: "refactor auth flow to remove local storage"
   ↓
2. Gemini: Analyzes request, determines complexity
   ↓
3. Gemini: Builds prompt chain:
   - Step 1: Analyze code (Cursor AI Agent)
   - Step 2: Check spec (Daemon)
   - Step 3: Build plan (APOE)
   - Step 4: Execute (Cursor AI Agent)
   ↓
4. UI Shows:
   - Prompt chain visualization (updates in real-time)
   - MCP tools being called (conversational format)
   - Timeline entries being created
   ↓
5. Gemini: Reports progress and results
   ↓
6. User: Approves or requests changes
```

### **Flow 2: Context Retrieval**

```
1. User: Mentions "Ferrari engines" (from 3 weeks ago)
   ↓
2. HHNI: Retrieves relevant context automatically
   ↓
3. UI Shows:
   - Context panel appears (side panel)
   - Related contexts from different time periods
   - Evolution timeline showing topic development
   ↓
4. User: Clicks to explore related contexts
   ↓
5. UI Shows:
   - Context web visualization
   - Connected topics and discussions
```

### **Flow 3: Agent Coordination**

```
1. User: "Lexicon and Solo need to work together"
   ↓
2. Gemini: Coordinates agents:
   - Sends message to Lexicon
   - Sends message to Solo
   - Creates coordination plan
   ↓
3. UI Shows:
   - Agent messages in conversation
   - Coordination plan visualization
   - Timeline entries for coordination
   ↓
4. Gemini: Reports coordination status
```

---

## 📊 **DATA VISUALIZATION**

### **1. Prompt Chain Visualization**

**Visual Elements:**
- **Flow Diagram** - Shows step progression
- **Status Indicators** - ✅ Complete, 🔄 Running, ⏳ Pending
- **Duration Bars** - Visual time representation
- **Agent Icons** - Shows which agent/system is working
- **Connection Lines** - Shows data flow between steps

### **2. Context Web Visualization**

**Visual Elements:**
- **Node Graph** - Topics as nodes
- **Connection Lines** - Relationships between topics
- **Timeline Dimension** - Time-based positioning
- **Strength Indicators** - Connection strength visualization
- **Evolution Paths** - How topics evolved over time

### **3. MCP Tools Activity**

**Visual Elements:**
- **Category Tabs** - Memory, Knowledge, Confidence, etc.
- **Timeline View** - Chronological tool calls
- **Conversation Format** - Natural language descriptions
- **Performance Metrics** - Duration, success rate

### **4. Timeline & Calendar**

**Visual Elements:**
- **Calendar View** - Monthly/weekly/daily views
- **Event Cards** - Key events with summaries
- **Timeline Strip** - Horizontal scrolling timeline
- **Context Bubbles** - Visual context representation

---

## 🎯 **DEFAULT VIEW PRIORITIZATION**

### **What Shows by Default (Priority Order):**

**1. Agent Management Dashboard (PRIMARY - HIGHEST PRIORITY)**
- **Agent Cards** - All agents with status and controls
- **Cursor Automation Controls** - Model switching, continue prompts
- **Task Assignment** - Assign work to agents
- **System Status** - Connection and health
- **Quick Actions** - Common operations

**Why This is Primary:**
- **Core Mission** - Automating Cursor is the primary purpose
- **Most Used** - Managing agents is the most frequent operation
- **Highest Impact** - Enables coordination and automation
- **Express Mission** - Clearly shows what the panel does

**2. Active Conversation (Secondary Tab)**
- Current conversation with Gemini/Cerebras
- Most recent messages
- Active prompt chains
- Current task status

**3. Prompt Chain Visualization (Tertiary Tab)**
- Currently running chains
- Recent completed chains
- Chain builder interface

**4. MCP Tools Activity (Quaternary Tab)**
- Recent operations (last 10)
- Organized by category
- Conversational format

**5. Timeline Summary (Tertiary Tab)**
- Today's activity
- This week's summary
- Quick context web preview

**6. Status Strip (Always Visible)**
- Connection status
- System health
- Quick actions

### **What's Hidden by Default (Expandable):**
- Full chat history (click "View History" in Chat tab)
- Complete timeline (click "View Timeline" in Timeline tab)
- All MCP operations (click "View All Operations" in Tools tab)
- Agent coordination details (expand agent cards)
- System monitoring (click "View System Status")
- Advanced automation settings (click "Settings" tab)

---

## 🔧 **WORKFLOW AUTOMATION - TERMINAL & PORT MANAGEMENT**

### **Problem:**
Cursor opens terminals and ports but doesn't close them, causing:
- Resource leaks
- Port conflicts
- Terminal clutter
- Confusion about what's running

### **Solution: Automated Workflow Management**

**Key Features:**

**1. Terminal Management:**
- **Detect Open Terminals** - Monitor all Cursor terminals
- **Track Terminal State** - Know which terminals are active/idle
- **Smart Detection** - Detect when same app runs in multiple terminals
- **Auto-Cleanup** - Close terminals when tasks complete
- **Warning System** - Warn before closing terminals
- **User Approval** - Request approval before closing

**2. Port Management:**
- **Detect Open Ports** - Monitor all ports in use
- **Track Port Usage** - Know which apps use which ports
- **Conflict Detection** - Detect port conflicts
- **Auto-Cleanup** - Close ports when apps stop
- **Smart Closing** - Auto-close old ports when new app starts (same/upgraded)
- **Warning System** - Warn before closing ports
- **User Approval** - Request approval before closing

**3. Smart Detection System:**
- **Same App Detection** - Compare process/command to detect duplicates
- **Upgraded App Detection** - Version comparison to detect upgrades
- **Port Conflict Detection** - Detect when port is already in use
- **Resource Tracking** - Track terminal/port usage over time

**4. Automation Levels:**
- **Full Auto** - Auto-close with smart detection (with warnings)
- **Semi-Auto** - Detect and suggest, require approval
- **Manual** - Only show warnings, user decides

### **UI Integration:**

**Workflow Automation Tab:**
```
┌─────────────────────────────────────────────────────────────┐
│ 🔧 Workflow Automation                                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 🖥️ Active Terminals (3)                                 │ │
│ │                                                         │ │
│ │ ┌─────────────────────────────────────────────────────┐ │ │
│ │ │ Terminal 1: npm run dev (port 3000)                  │ │ │
│ │ │   Status: Running | Started: 15 min ago              │ │ │
│ │ │   [View] [Close] [Keep Open]                         │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ │                                                         │ │
│ │ ┌─────────────────────────────────────────────────────┐ │ │
│ │ │ Terminal 2: python app.py (port 5000)                │ │ │
│ │ │   Status: Idle | Started: 2 hours ago ⚠️            │ │ │
│ │ │   ⚠️ Suggested: Close idle terminal                  │ │ │
│ │ │   [Close] [Keep Open] [Auto-Close When Done]         │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ │                                                         │ │
│ │ ┌─────────────────────────────────────────────────────┐ │ │
│ │ │ Terminal 3: npm run dev (port 3000)                  │ │ │
│ │ │   Status: Running | Started: 2 min ago              │ │ │
│ │ │   ⚠️ Duplicate detected: Same app on same port       │ │ │
│ │ │   Suggested: Close Terminal 1 (older)              │ │ │
│ │ │   [Close Terminal 1] [Keep Both] [Merge]             │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 🔌 Active Ports (5)                                     │ │
│ │                                                         │ │
│ │ ┌─────────────────────────────────────────────────────┐ │ │
│ │ │ Port 3000: npm run dev (Terminal 1 & 3)              │ │ │
│ │ │   ⚠️ Conflict: Multiple terminals using same port    │ │ │
│ │ │   [Close Terminal 1] [Close Terminal 3] [Keep Both]  │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ │                                                         │ │
│ │ ┌─────────────────────────────────────────────────────┐ │ │
│ │ │ Port 5000: python app.py (Terminal 2)                │ │ │
│ │ │   Status: Idle | Started: 2 hours ago               │ │ │
│ │ │   ⚠️ Suggested: Close port (app not responding)      │ │ │
│ │ │   [Close Port] [Keep Open] [Auto-Close When Done]   │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ │                                                         │ │
│ │ ┌─────────────────────────────────────────────────────┐ │ │
│ │ │ Port 8080: npm run dev (Terminal 4)                  │ │ │
│ │ │   Status: Running | Started: 5 min ago              │ │ │
│ │ │   [View] [Close Port] [Keep Open]                   │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ ⚙️ Automation Settings                                  │ │
│ │                                                         │ │
│ │ [ ] Auto-close terminals when task completes           │ │
│ │ [ ] Auto-close ports when app stops                   │ │
│ │ [ ] Auto-close old ports when new app starts           │ │
│ │ [ ] Warn before closing (always)                       │ │
│ │ [ ] Request approval before closing (always)            │ │
│ │                                                         │ │
│ │ Automation Level:                                       │ │
│ │ ( ) Full Auto (with warnings)                          │ │
│ │ ( ) Semi-Auto (suggestions, require approval)           │ │
│ │ (•) Manual (only show warnings)                         │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### **How It Works:**

**Example 1: Auto-Close Duplicate Terminal**

```
1. User starts "npm run dev" in Terminal 1 (port 3000)
2. User starts "npm run dev" in Terminal 3 (port 3000)
3. System detects: Same app, same port
4. System shows warning:
   "⚠️ Duplicate detected: Terminal 3 is running same app on same port as Terminal 1
    Suggested: Close Terminal 1 (older, started 15 min ago)
    [Close Terminal 1] [Keep Both] [Cancel]"
5. User clicks "Close Terminal 1"
6. System closes Terminal 1
7. Terminal 3 continues running
```

**Example 2: Auto-Close Idle Port**

```
1. User starts "python app.py" (port 5000) in Terminal 2
2. App runs for 2 hours
3. System detects: Terminal idle, app not responding
4. System shows warning:
   "⚠️ Port 5000 (python app.py) has been idle for 2 hours
    Suggested: Close port to free resources
    [Close Port] [Keep Open] [Auto-Close When Done]"
5. User clicks "Close Port"
6. System closes port and terminal
```

**Example 3: Smart Port Replacement**

```
1. User starts "npm run dev" v1.0 (port 3000)
2. User upgrades to v1.1 and starts new instance
3. System detects: Upgraded app (version comparison)
4. System shows warning:
   "⚠️ Upgraded app detected: v1.1 started (port 3000)
    Old instance: v1.0 (Terminal 1, started 30 min ago)
    Suggested: Close old instance (v1.0)
    [Close Old Instance] [Keep Both] [Cancel]"
5. User clicks "Close Old Instance"
6. System closes Terminal 1 (v1.0)
7. New instance (v1.1) continues running
```

### **Integration Points:**

**1. Cursor Terminal API:**
```typescript
// Detect terminals
const terminals = vscode.window.terminals

// Monitor terminal state
terminals.forEach(terminal => {
  terminal.onDidWriteData((data) => {
    // Detect when terminal is idle
  })
})

// Close terminal
terminal.dispose()
```

**2. Port Detection:**
```typescript
// Detect open ports (Windows)
import { exec } from 'child_process'
exec('netstat -ano | findstr LISTENING', (error, stdout) => {
  // Parse port usage
})

// Detect open ports (Linux/Mac)
exec('lsof -i -P -n | grep LISTEN', (error, stdout) => {
  // Parse port usage
})
```

**3. Process Detection:**
```typescript
// Detect process by port
exec('netstat -ano | findstr :3000', (error, stdout) => {
  // Get process ID
  // Get process details
  // Compare with running terminals
})
```

### **Implementation Priority:**

**Phase 1: Detection (Week 1)**
- Terminal detection (Cursor API)
- Port detection (netstat/lsof)
- Process detection (port → process mapping)

**Phase 2: Smart Detection (Week 2)**
- Same app detection (compare commands)
- Upgraded app detection (version comparison)
- Conflict detection (port conflicts)

**Phase 3: Automation (Week 3)**
- Warning system
- User approval workflow
- Auto-close with approval
- Settings UI

**Phase 4: Advanced Features (Week 4)**
- Resource tracking
- History/analytics
- Custom rules
- Integration with agent management

### **Component Structure:**

```
cursor-addon/src/
├── components/
│   ├── AgentManagementDashboard.tsx      // PRIMARY TAB - Agent management
│   │   ├── AgentCard.tsx                 // Individual agent card
│   │   ├── AgentStatus.tsx               // Agent status indicators
│   │   ├── CursorAutomationControls.tsx  // Model switching, continue prompts
│   │   ├── TaskAssignment.tsx            // Task assignment interface
│   │   └── AgentCommunication.tsx        // Message sending, broadcasting
│   ├── ConversationView.tsx              // Chat tab - Gemini/Cerebras chat
│   ├── PromptChainVisualization.tsx      // Chains tab - Chain visualization
│   ├── MCPToolsActivity.tsx              // Tools tab - MCP tools display
│   ├── TimelineCalendar.tsx              // Timeline tab - Timeline & calendar
│   ├── ContextWeb.tsx                    // Context web visualization
│   ├── SettingsPanel.tsx                 // Settings tab - Configuration
│   └── StatusStrip.tsx                   // Status bar (always visible)
│
├── services/
│   ├── AgentManager.ts                   // Agent management service
│   │   ├── monitorAgents()               // Monitor agent status
│   │   ├── controlAgent()                // Start/stop/pause/resume
│   │   ├── changeModel()                 // Change agent/Cursor model
│   │   ├── promptContinue()              // Send continue prompt
│   │   ├── sendMessage()                 // Send message to agent
│   │   ├── broadcastMessage()            // Broadcast to all agents
│   │   └── assignTask()                  // Assign task to agent
│   ├── CursorAutomation.ts               // Cursor automation service
│   │   ├── changeCursorModel()           // Change Cursor's model
│   │   ├── promptAllAgents()             // Prompt all agents to continue
│   │   ├── detectAgentStall()            // Detect when agents stop
│   │   └── trackAgentActivity()          // Track agent activity
│   ├── WorkflowAutomation.ts             // NEW: Workflow automation service
│   │   ├── detectTerminals()             // Detect open terminals
│   │   ├── detectPorts()                 // Detect open ports
│   │   ├── detectDuplicates()            // Detect duplicate terminals/apps
│   │   ├── detectConflicts()              // Detect port conflicts
│   │   ├── closeTerminal()               // Close terminal (with approval)
│   │   ├── closePort()                   // Close port (with approval)
│   │   ├── autoCleanup()                 // Auto-cleanup resources
│   │   └── requestApproval()             // Request user approval
│   ├── GeminiService.ts                  // Gemini API integration
│   ├── CerebrasService.ts                // Cerebras API integration
│   ├── PromptChainManager.ts            // Chain management
│   └── ContextWebManager.ts              // Context web management
│
└── hooks/
    ├── useAgentManagement.ts             // Agent management state
    ├── useCursorAutomation.ts            // Cursor automation state
    ├── usePromptChain.ts                 // Prompt chain state
    ├── useMCPTools.ts                    // MCP tools state
    ├── useTimeline.ts                    // Timeline state
    └── useContextWeb.ts                  // Context web state
```

### **Data Flow (Agent Management Focus):**

```
User Input (Agent Management)
  ↓
AgentManager Service
  ├──→ Monitor Agent Status
  ├──→ Control Agent (Start/Stop/Pause)
  ├──→ Change Model
  ├──→ Prompt Continue
  ├──→ Send Message
  └──→ Assign Task
  ↓
Cursor Automation Service
  ├──→ Change Cursor Model
  ├──→ Prompt All Agents
  ├──→ Detect Agent Stalls
  └──→ Track Activity
  ↓
Cursor API Integration
  ├──→ Send to Cursor Chat
  ├──→ Change Cursor Model
  └──→ Monitor Cursor Agents
  ↓
UI Update
  ├──→ Agent Management Dashboard
  ├──→ Agent Cards (Status Updates)
  ├──→ Cursor Automation Controls
  └──→ System Status
```

---

## 💡 **KEY INNOVATIONS**

### **1. Conversational MCP Tools**
- **Not Raw Tool Calls:** Show as natural language conversations
- **Context-Aware:** Explain why tools were called
- **Organized:** Group by purpose, not just chronologically

### **2. Dynamic Prompt Chains**
- **Real-time Visualization:** See chains being built
- **Dynamic Adjustment:** Steps can be added/removed
- **Transparency:** Show exactly what's happening

### **3. Context Web Instead of Chat History**
- **Not Linear:** Contextual connections, not just chronological
- **Visual:** Graph visualization of related topics
- **Evolution:** See how understanding evolved

### **4. Gemini/Cerebras as Orchestrator**
- **Not Just Chat:** Intelligent agent management
- **Transparency:** Shows what agents are doing
- **Coordination:** Manages complex multi-agent workflows

### **5. Timeline Integration**
- **Calendar View:** Jump to any date
- **Event Cards:** Key events with summaries
- **Context Bubbles:** Visual context representation

---

## 🚀 **IMPLEMENTATION PRIORITIES**

### **Phase 1: Agent Management Dashboard (CRITICAL - Week 1)**
**Primary Mission Implementation:**

**Week 1, Days 1-2: Agent Cards & Status**
- ✅ Agent card component
- ✅ Status indicators (Active, Idle, Stopped, Paused)
- ✅ **Confidence display** (VIF integration)
- ✅ **Confidence bands** (A/B/C color coding)
- ✅ **Confusion indicators** (⚠️ when confidence low)
- ✅ Real-time status updates
- ✅ Basic agent information display

**Week 1, Days 3-4: Cursor Automation Controls**
- ✅ Model switching dropdown
- ✅ Change Cursor model functionality
- ✅ Per-agent model selection
- ✅ Model performance tracking
- ✅ **Confidence-gated automation** (κ-gating)

**Week 1, Days 5-7: Continue Prompt Automation**
- ✅ "Prompt Continue" button per agent
- ✅ **Confidence-gated prompting** (only if confidence ≥ 0.70)
- ✅ "Prompt All" functionality (with confidence checks)
- ✅ **Confusion detection** (CAS integration)
- ✅ Smart prompt detection (auto-detect when agents stop)
- ✅ Prompt history tracking

**Week 1, Days 8-10: Agent Communication**
- ✅ Send message to agent
- ✅ Broadcast message to all agents
- ✅ Message composer interface
- ✅ Message history
- ✅ **Agent questions** (agents can ask questions)
- ✅ **Lucid AI answers** (Gemini/Cerebras answers questions)

**Week 1, Days 11-14: Task Management & Confidence Metrics**
- ✅ Task assignment interface
- ✅ **Confidence-gated task assignment** (only if confidence ≥ 0.70)
- ✅ Task queue visualization
- ✅ Task tracking and progress
- ✅ Task dependencies
- ✅ **Confidence metrics dashboard**
- ✅ **Confidence history** tracking
- ✅ **κ-gate status** display

**Week 1, Days 15-21: Agent Assistance System**
- ✅ **Agent question detection** (when confidence low)
- ✅ **Question panel** (agents can ask questions)
- ✅ **Lucid AI integration** (Gemini/Cerebras answers)
- ✅ **Context provision** (UI provides context to improve confidence)
- ✅ **Confidence improvement tracking** (track improvements after assistance)
- ✅ **Learning loop** (agents learn from assistance)

### **Phase 2: Multi-Tab Structure (Week 2)**
- ✅ Tab navigation system
- ✅ Agent Management tab (default)
- ✅ Chat tab
- ✅ Prompt Chains tab
- ✅ MCP Tools tab
- ✅ Timeline tab
- ✅ Settings tab

### **Phase 3: Chat Interface (Week 3)**
- ✅ Gemini/Cerebras chat interface
- ✅ Model selector
- ✅ Basic message history
- ✅ Context-aware responses

### **Phase 4: Prompt Chain Visualization (Week 4)**
- ✅ Chain visualization component
- ✅ Real-time updates
- ✅ Agent attribution
- ✅ Duration tracking

### **Phase 5: MCP Tools Display (Week 5)**
- ✅ MCP tools activity panel
- ✅ Conversational format
- ✅ Category organization
- ✅ Timeline integration

### **Phase 6: Timeline & Calendar (Week 6)**
- ✅ Timeline view
- ✅ Calendar navigation
- ✅ Context web visualization
- ✅ Search functionality

### **Phase 7: Advanced Features (Week 7+)**
- ✅ Advanced automation rules
- ✅ Agent coordination visualization
- ✅ System monitoring integration
- ✅ Voice I/O integration
- ✅ Performance analytics
- ✅ **Workflow Automation** (Terminal & Port Management)
  - Terminal detection and management
  - Port detection and management
  - Smart detection (duplicates, conflicts)
  - Warning system
  - User approval workflow

---

## 📋 **DESIGN PRINCIPLES**

### **1. Transparency First**
- Show what's happening, not just results
- Explain why decisions were made
- Show agent coordination and tool usage

### **2. Conversational Interface**
- Natural language, not technical jargon
- Explain complex operations simply
- Context-aware responses

### **3. Visual Communication**
- Use visualizations for complex data
- Show relationships, not just lists
- Progressive disclosure (overview → details)

### **4. Context Awareness**
- Show relevant context automatically
- Connect related topics visually
- Evolution tracking

### **5. Agent Orchestration**
- Show which agents are working
- Coordinate multi-agent workflows
- Transparent agent communication

---

## 💙 **SUMMARY**

**The Cursor UI Panel is:**
- **Automation Cockpit** - Control station for automating Cursor operations
- **Agent Management Dashboard** - Manage Cursor AI agents like Aether manages Lexicon, Solo, Sonnet, Atlas
- **Model Manager** - Change Cursor models dynamically
- **Continue Prompt Automation** - Automatically prompt agents to continue when they stop (WITH CONFIDENCE GATES)
- **Task Orchestrator** - Assign and track tasks across agents (WITH CONFIDENCE GATES)
- **Confidence-Based Safety System** - Uses VIF confidence metrics and κ-gating to ensure safe automation
- **Agent Assistance System** - Agents can ask questions to Lucid AI when confused, UI provides context to improve confidence
- **Workflow Automation** - Auto-manage terminals and ports (detect, warn, close with approval)
- **Multi-Tab Interface** - Comprehensive interface with many tabs and parts

**Default View (PRIMARY TAB):**
1. **Agent Management Dashboard** - Agent cards, status, controls (HIGHEST PRIORITY)
2. **Confidence Metrics** - VIF confidence tracking, κ-gate status, confidence bands
3. **Cursor Automation Controls** - Model switching, continue prompts, task assignment (CONFIDENCE-GATED)
4. **Agent Assistance System** - Agents can ask questions, UI provides context
5. **System Status** - Connection status, agent summary, task progress, confidence summary
6. **Quick Actions** - Common operations for managing agents (CONFIDENCE-GATED)

**Secondary Tabs:**
- Chat Interface (conversation with Gemini/Cerebras)
- Prompt Chains (visualize complex operations)
- MCP Tools (tools shown as conversations)
- Timeline & Calendar (context web visualization)
- Settings (configuration and preferences)
- **Workflow Automation** (terminal & port management) - NEW

**Core Mission:**
**AUTOMATING CURSOR** - The panel's primary purpose is to automate Cursor operations and manage Cursor AI agents, enabling seamless coordination and automation just like Aether manages the team.

**This is the revolutionary UI that makes Cursor automation visible, controllable, and powerful.**

---

**Status:** Design vision complete! Enhanced with Agent Management Dashboard as primary mission! Ready for Lexicon to implement! 💙✨

---

## 📋 **DESIGN REVISION NOTES**

**2025-10-31 - Enhanced Focus on Agent Management:**

**Key Changes:**
- ✅ **Agent Management Dashboard** set as PRIMARY TAB (default view)
- ✅ **Cursor Automation** emphasized as core mission
- ✅ **Model Switching** added as key feature
- ✅ **Continue Prompt Automation** added as key feature
- ✅ **Task Management** integrated into agent management
- ✅ **Multi-tab structure** clarified with clear hierarchy
- ✅ **Confidence-Based Safety Gates** added (VIF integration, κ-gating)
- ✅ **Agent Assistance System** added (agents can ask questions, UI provides context)
- ✅ **Confidence Metrics Dashboard** added (confidence tracking, confusion detection)
- ✅ **Workflow Automation** added (terminal & port management) - NEW

**Why Agent Management is Primary:**
- **Core Mission** - Automating Cursor is the primary purpose
- **Most Used** - Managing agents is the most frequent operation
- **Highest Impact** - Enables coordination and automation
- **Express Mission** - Clearly shows what the panel does
- **Safety First** - Confidence-based gates ensure safe automation
- **Agent Assistance** - Agents can ask questions when confused, UI provides context to improve confidence

**Implementation Priority:**
- **Phase 1** now focuses on Agent Management Dashboard (critical)
- **Confidence-Based Safety** integrated throughout (VIF, κ-gating)
- **Agent Assistance System** integrated throughout (questions, context provision)
- Other features remain important but secondary
- Multi-tab structure enables expansion without losing focus

