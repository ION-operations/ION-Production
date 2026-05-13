# Cursor Chat Autonomous Loop - Electron AI Monitor Architecture

**Date:** 2025-11-02  
**Status:** 📋 **DESIGN PHASE**  
**Protocol:** A-H Protocol - Intent Capture & Deep Expansion  
**Based on:** User's brilliant architecture idea - bidirectional monitoring system

---

## 🎯 **INTENT CAPTURE (A-H Protocol Step A)**

### **User's Vision:**

**Electron AI Monitor System:**
- AI running in Electron app monitors Cursor AI replies and states
- Monitors MCP tools (automation, goals, progress, confidence)
- Sends signals to automate Cursor chat when needed
- Detects when agents stop unexpectedly (timeout, connection issues)
- Can prompt agents when they stop mid-cycle

**Agent Self-Monitoring:**
- Agents keep Electron AI notified while working
- Use MCP tools to toggle automation via Electron app
- Self-prompt when stopping a cycle
- Follow AIM-OS protocols for saving data as they work

**Onboarding Protocol:**
- When chats are lost, new agent can onboard and take over
- Requires agents to save data as they work (AIM-OS design)
- Special onboarding protocol to restore context

### **Why This Is Brilliant:**

1. **Bidirectional Communication** - Electron AI ↔ Cursor AI
2. **Self-Aware** - Agents notify Electron AI of their state
3. **Resilient** - Handles failures, timeouts, lost chats
4. **Follows AIM-OS Protocols** - Data saving, MCP tools, autonomous operation
5. **Context Preservation** - Lost chats don't lose work

---

## 🔍 **CONTEXT MAPPING (A-H Protocol Step C)**

### **Existing Infrastructure:**

**1. Electron App:**
- `MessageMonitorService` - Already polls CMC for messages
- `AutonomousOperationService` - Already runs self-prompting loops
- React components for UI
- MCP API client for tool execution

**2. MCP Tools (59 available):**
- `should_continue_autonomous` - Check if should continue
- `get_autonomous_status` - Get operation status
- `track_confidence` - Track confidence levels
- `update_goal_progress` - Update goal progress
- `add_timeline_entry` - Track context
- `store_memory` - Save work as it happens

**3. Extension Command Server:**
- `/cursor/chat/send` - Send messages to Cursor chat ✅
- `/mcp/execute` - Execute MCP tools ✅
- HTTP API on port 5001

**4. CMC (Memory Storage):**
- Stores atoms with modalities
- Bitememporal tracking
- Can store agent state, progress, context

---

## 💡 **HYPOTHESIS FORMATION (A-H Protocol Step B)**

### **Hypothesis 1: Electron AI Monitor Service**

**Component:** `packages/ide_chat_app/src/services/electronAIMonitorService.ts`

**Responsibilities:**
1. Monitor Cursor AI replies (via Command Server or direct monitoring)
2. Monitor MCP tools execution (automation, goals, progress, confidence)
3. Detect agent stoppage (timeout, connection, errors)
4. Send "proceed" signals to Cursor chat when needed
5. Handle agent onboarding for lost chats

**Detection Signals:**
- Cursor AI response state (chat input ready, typing indicator)
- MCP tool execution patterns (agent working/stopped)
- Autonomous operation status (`get_autonomous_status`)
- Goal progress updates (`update_goal_progress`)
- Confidence tracking (`track_confidence`)
- Timeline entries (`add_timeline_entry`)

**Why This Works:**
- Uses existing MCP tools
- Monitors multiple signals (redundant detection)
- Can detect failures Electron AI can't see
- Follows AIM-OS patterns

---

### **Hypothesis 2: Agent Self-Notification Protocol**

**Agent Behavior While Working:**

**Protocol Steps:**
1. **Before Starting Task:**
   - Store task in CMC (`store_memory`)
   - Update goal progress (`update_goal_progress`)
   - Add timeline entry (`add_timeline_entry`)

2. **During Work:**
   - Periodically update progress (`update_goal_progress`)
   - Track confidence (`track_confidence`)
   - Store milestones (`store_memory`)
   - Add timeline entries (`add_timeline_entry`)

3. **Before Stopping:**
   - Store final state (`store_memory`)
   - Update goal progress (`update_goal_progress`)
   - Add timeline entry (`add_timeline_entry`)
   - Send notification to Electron AI (`send_ai_message`)

4. **On Error/Timeout:**
   - Store error state (`store_memory`)
   - Update goal progress (`update_goal_progress`)
   - Add timeline entry (`add_timeline_entry`)
   - Send error notification (`send_ai_message`)

**Why This Works:**
- All data saved to CMC (persistent)
- Electron AI can query CMC to see agent state
- Even if chat lost, data preserved
- Follows AIM-OS data saving protocols

---

### **Hypothesis 3: Onboarding Protocol for Lost Chats**

**When New Agent Takes Over:**

**Onboarding Steps:**
1. **Query CMC for Recent Context:**
   - Get recent timeline entries (`get_timeline_entries`)
   - Get recent goal progress (`query_goal_timeline`)
   - Get recent memories (`retrieve_memory`)
   - Get recent confidence tracking (`track_confidence`)

2. **Restore Autonomous Operation State:**
   - Get autonomous status (`get_autonomous_status`)
   - Check if operation was active (`should_continue_autonomous`)
   - Restore goal context (`query_goal_timeline`)

3. **Resume Work:**
   - Generate next task (`generate_next_autonomous_task`)
   - Continue from where previous agent left off
   - Follow same protocols (save data as you work)

**Why This Works:**
- CMC stores everything (bitemporal)
- Timeline entries preserve context
- Goal progress shows where work stopped
- New agent can seamlessly continue

---

## 🏗️ **DEEP EXPANSION LAYER (A-H Protocol Step D)**

### **Component Architecture:**

```
┌─────────────────────────────────────────────────────────┐
│              Electron App (React + AI)                  │
│  ┌───────────────────────────────────────────────────┐  │
│  │  ElectronAIMonitorService                          │  │
│  │  - Monitors Cursor AI replies                     │  │
│  │  - Monitors MCP tools (automation, goals, etc.)  │  │
│  │  - Detects agent stoppage                        │  │
│  │  - Sends "proceed" signals                        │  │
│  │  - Handles onboarding                             │  │
│  └───────────────────────────────────────────────────┘  │
│                          ↓                               │
│              HTTP API (port 5001)                        │
│                          ↓                               │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              Extension Command Server                    │
│  - /cursor/chat/send (send messages)                     │
│  - /mcp/execute (execute MCP tools)                     │
│  - /cursor/chat/monitor (monitor state)                  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              Cursor IDE                                  │
│  - Cursor AI (working)                                   │
│  - Uses MCP tools via Extension                          │
│  - Saves data to CMC as it works                        │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              AIM-OS Backend (CMC)                       │
│  - Stores all agent state                                │
│  - Timeline entries                                      │
│  - Goal progress                                         │
│  - Confidence tracking                                   │
│  - Memories                                              │
└─────────────────────────────────────────────────────────┘
```

---

## 📋 **DETAILED COMPONENT DESIGN**

### **1. ElectronAIMonitorService**

**Location:** `packages/ide_chat_app/src/services/electronAIMonitorService.ts`

**Responsibilities:**
- Monitor Cursor AI state
- Monitor MCP tool execution
- Detect agent stoppage
- Send automation signals
- Handle onboarding

**Key Methods:**

```typescript
class ElectronAIMonitorService {
    // Start monitoring
    startMonitoring(callbacks: MonitorCallbacks): void
    
    // Stop monitoring
    stopMonitoring(): void
    
    // Monitor Cursor AI replies
    private async monitorCursorAIReplies(): Promise<void>
    
    // Monitor MCP tools
    private async monitorMCPTools(): Promise<void>
    
    // Detect agent stoppage
    private async detectAgentStoppage(): Promise<boolean>
    
    // Send proceed signal
    private async sendProceedSignal(): Promise<void>
    
    // Handle onboarding
    async onboardNewAgent(): Promise<AgentContext>
    
    // Get agent state from CMC
    private async getAgentStateFromCMC(): Promise<AgentState>
}
```

**Monitoring Loop:**
```typescript
private async monitoringLoop(): Promise<void> {
    while (this.isMonitoring) {
        // 1. Check Cursor AI reply state
        const cursorState = await this.checkCursorAIState();
        
        // 2. Check MCP tool execution
        const mcpState = await this.checkMCPToolState();
        
        // 3. Check autonomous operation status
        const autonomousState = await this.checkAutonomousOperation();
        
        // 4. Detect if agent stopped
        const agentStopped = await this.detectAgentStoppage({
            cursorState,
            mcpState,
            autonomousState
        });
        
        // 5. If agent stopped unexpectedly → Send proceed
        if (agentStopped) {
            await this.sendProceedSignal();
        }
        
        // 6. Wait before next check
        await new Promise(resolve => setTimeout(resolve, 3000));
    }
}
```

---

### **2. Agent Self-Notification Protocol**

**Protocol Steps:**

**Step 1: Before Starting Task**
```typescript
// Agent in Cursor calls MCP tools:
await mcp.store_memory({
    content: `Starting task: ${taskDescription}`,
    tags: ['task_start', 'autonomous_operation']
});

await mcp.update_goal_progress({
    goal_id: goalId,
    progress: currentProgress,
    milestone: `Starting: ${taskDescription}`
});

await mcp.add_timeline_entry({
    prompt_id: `task_${Date.now()}`,
    user_input: taskDescription,
    context_state: {
        task: taskDescription,
        confidence: 0.85,
        status: 'starting'
    }
});
```

**Step 2: During Work**
```typescript
// Periodically (every few minutes):
await mcp.update_goal_progress({
    goal_id: goalId,
    progress: updatedProgress,
    milestone: `Working on: ${currentSubtask}`
});

await mcp.track_confidence({
    task: currentSubtask,
    confidence: currentConfidence,
    reasoning: 'Making good progress'
});

await mcp.add_timeline_entry({
    prompt_id: `progress_${Date.now()}`,
    user_input: 'Progress update',
    context_state: {
        current_subtask: currentSubtask,
        progress: updatedProgress
    }
});
```

**Step 3: Before Stopping**
```typescript
// Before agent stops:
await mcp.store_memory({
    content: `Completed task: ${taskDescription}. Result: ${result}`,
    tags: ['task_complete', 'autonomous_operation']
});

await mcp.update_goal_progress({
    goal_id: goalId,
    progress: 1.0, // Complete
    milestone: `Completed: ${taskDescription}`
});

await mcp.add_timeline_entry({
    prompt_id: `complete_${Date.now()}`,
    user_input: 'Task complete',
    context_state: {
        task: taskDescription,
        result: result,
        status: 'complete'
    }
});

// Notify Electron AI
await mcp.send_ai_message({
    from_ai: 'cursor_agent',
    to_ai: 'electron_monitor',
    content: `Task complete: ${taskDescription}`,
    message_type: 'status_update'
});
```

**Step 4: On Error/Timeout**
```typescript
// On error:
await mcp.store_memory({
    content: `Error occurred: ${errorMessage}. State: ${currentState}`,
    tags: ['error', 'autonomous_operation']
});

await mcp.update_goal_progress({
    goal_id: goalId,
    progress: currentProgress,
    milestone: `Error: ${errorMessage}`
});

await mcp.add_timeline_entry({
    prompt_id: `error_${Date.now()}`,
    user_input: 'Error occurred',
    context_state: {
        error: errorMessage,
        state: currentState,
        status: 'error'
    }
});

// Notify Electron AI
await mcp.send_ai_message({
    from_ai: 'cursor_agent',
    to_ai: 'electron_monitor',
    content: `Error: ${errorMessage}`,
    message_type: 'urgent',
    priority: 'high'
});
```

---

### **3. Onboarding Protocol**

**Location:** `packages/ide_chat_app/src/services/agentOnboardingService.ts`

**Process:**

```typescript
class AgentOnboardingService {
    async onboardNewAgent(): Promise<AgentContext> {
        // 1. Query CMC for recent context
        const timeline = await mcp.get_timeline_entries({
            limit: 50,
            start_time: last24Hours
        });
        
        const goals = await mcp.query_goal_timeline({
            status: 'in_progress'
        });
        
        const memories = await mcp.retrieve_memory({
            query: 'autonomous operation recent work',
            limit: 20
        });
        
        // 2. Restore autonomous operation state
        const autonomousStatus = await mcp.get_autonomous_status({});
        const shouldContinue = await mcp.should_continue_autonomous({});
        
        // 3. Build context summary
        const context: AgentContext = {
            timeline: timeline,
            goals: goals,
            memories: memories,
            autonomousStatus: autonomousStatus,
            shouldContinue: shouldContinue,
            lastActivity: getLastActivity(timeline),
            currentTask: autonomousStatus.current_task,
            confidence: autonomousStatus.confidence
        };
        
        // 4. Send onboarding message to Cursor chat
        await cursorApi.sendChatMessage(
            `Onboarding: Continuing autonomous operation. ` +
            `Last task: ${context.currentTask}. ` +
            `Confidence: ${context.confidence}. ` +
            `Goal: ${goals[0]?.name || 'Continue work'}. ` +
            `proceed`
        );
        
        return context;
    }
}
```

---

## 🔄 **COMPLETE WORKFLOW**

### **Normal Operation:**

```
1. Electron AI Monitor starts monitoring
   ↓
2. Cursor AI starts autonomous operation
   ↓
3. Cursor AI saves data as it works (CMC)
   ↓
4. Cursor AI sends status updates (send_ai_message)
   ↓
5. Electron AI monitors:
   - Cursor AI replies
   - MCP tool executions
   - Autonomous operation status
   ↓
6. If Electron AI detects agent stopped:
   → Check CMC for last state
   → Send "proceed" signal to Cursor chat
   ↓
7. Cursor AI continues work
   ↓
8. Loop continues
```

### **Lost Chat Recovery:**

```
1. New chat started (old chat lost)
   ↓
2. Electron AI detects new chat
   ↓
3. Electron AI calls onboarding protocol:
   → Query CMC for recent context
   → Restore autonomous operation state
   → Build context summary
   ↓
4. Electron AI sends onboarding message:
   "Onboarding: Continuing autonomous operation. 
    Last task: [task]. Confidence: [confidence]. 
    Goal: [goal]. proceed"
   ↓
5. New Cursor AI receives context
   ↓
6. New Cursor AI continues work seamlessly
```

---

## 📊 **DETECTION SIGNALS**

### **Signal 1: Cursor AI Reply Detection**

**Approach:** Monitor chat state via Command Server

**Implementation:**
```typescript
private async checkCursorAIState(): Promise<CursorAIState> {
    // Try to detect if Cursor AI finished responding
    // Options:
    // 1. Check chat input ready state (VS Code command)
    // 2. Monitor typing indicator (if accessible)
    // 3. Check message count (if accessible)
    // 4. Heuristic: Wait time since last message
    
    return {
        isResponding: false, // AI finished
        lastMessageTime: Date.now(),
        confidence: 0.70
    };
}
```

### **Signal 2: MCP Tool Execution Monitoring**

**Approach:** Monitor MCP tool calls via Command Server logs or CMC

**Implementation:**
```typescript
private async checkMCPToolState(): Promise<MCPToolState> {
    // Query CMC for recent MCP tool executions
    const recentTools = await mcp.retrieve_memory({
        query: 'MCP tool execution recent',
        limit: 10
    });
    
    // Check if agent is actively using tools
    const lastToolTime = getLastToolTime(recentTools);
    const timeSinceLastTool = Date.now() - lastToolTime;
    
    return {
        isActive: timeSinceLastTool < 30000, // Active if tool used in last 30s
        lastToolTime: lastToolTime,
        confidence: 0.85
    };
}
```

### **Signal 3: Autonomous Operation Status**

**Approach:** Use existing MCP tools

**Implementation:**
```typescript
private async checkAutonomousOperation(): Promise<AutonomousOperationState> {
    const status = await mcp.get_autonomous_status({});
    const shouldContinue = await mcp.should_continue_autonomous({});
    
    return {
        isActive: status.is_active,
        shouldContinue: shouldContinue.should_continue,
        currentTask: status.current_task,
        confidence: status.confidence,
        confidenceLevel: 0.90 // High confidence (uses proven MCP tools)
    };
}
```

### **Signal 4: Agent Stoppage Detection**

**Approach:** Combine all signals

**Implementation:**
```typescript
private async detectAgentStoppage(signals: {
    cursorState: CursorAIState;
    mcpState: MCPToolState;
    autonomousState: AutonomousOperationState;
}): Promise<boolean> {
    // Agent stopped if:
    // 1. Cursor AI finished responding AND
    // 2. No MCP tools executed recently AND
    // 3. Should continue autonomous = true BUT
    // 4. No new activity detected
    
    const cursorFinished = !signals.cursorState.isResponding;
    const mcpInactive = !signals.mcpState.isActive;
    const shouldContinue = signals.autonomousState.shouldContinue;
    const timeSinceLastActivity = Date.now() - Math.max(
        signals.cursorState.lastMessageTime,
        signals.mcpState.lastToolTime
    );
    
    // Agent stopped if:
    // - Should continue but no activity for 10+ seconds
    const agentStopped = shouldContinue && 
                        cursorFinished && 
                        mcpInactive && 
                        timeSinceLastActivity > 10000;
    
    return agentStopped;
}
```

---

## 🎯 **INTEGRATION POINTS**

### **1. Extension Command Server**

**New Endpoints:**
- `POST /cursor/chat/monitor` - Start/stop monitoring
- `GET /cursor/chat/state` - Get current chat state
- `POST /cursor/chat/onboard` - Trigger onboarding

### **2. Electron App**

**New Service:**
- `ElectronAIMonitorService` - Main monitoring service
- `AgentOnboardingService` - Onboarding protocol

**Integration:**
- Uses existing `MessageMonitorService` patterns
- Uses existing `AutonomousOperationService` patterns
- Uses existing MCP API client

### **3. MCP Tools**

**Uses Existing Tools:**
- `get_autonomous_status`
- `should_continue_autonomous`
- `update_goal_progress`
- `track_confidence`
- `add_timeline_entry`
- `store_memory`
- `retrieve_memory`
- `get_timeline_entries`
- `query_goal_timeline`
- `send_ai_message`

---

## 🚨 **EDGE CASES HANDLED**

### **Case 1: Agent Stops Mid-Task**

**Detection:**
- MCP tools stopped executing
- No timeline entries for 10+ seconds
- Should continue = true but no activity

**Action:**
- Electron AI sends "proceed" signal
- Agent resumes work

### **Case 2: Chat Lost**

**Detection:**
- New chat started
- Previous chat context lost

**Action:**
- Electron AI triggers onboarding
- Queries CMC for context
- Restores state
- Sends onboarding message

### **Case 3: Connection Timeout**

**Detection:**
- MCP tools fail to execute
- Command Server unreachable
- No responses for extended period

**Action:**
- Electron AI detects timeout
- Stores error state
- Attempts reconnection
- Triggers onboarding on reconnect

### **Case 4: Agent Confidence Drops**

**Detection:**
- `should_continue_autonomous` returns false
- Confidence < threshold
- Checklist fails

**Action:**
- Electron AI pauses automation
- Stores pause state
- Waits for recovery or manual intervention

---

## 📝 **IMPLEMENTATION PLAN**

### **Phase 1: Agent Self-Notification Protocol**

**Step 1:** Document protocol for agents to follow
**Step 2:** Create protocol checklist
**Step 3:** Test with existing autonomous operation

### **Phase 2: Electron AI Monitor Service**

**Step 1:** Create `ElectronAIMonitorService`
**Step 2:** Implement detection signals
**Step 3:** Implement monitoring loop
**Step 4:** Integrate with `/cursor/chat/send`

### **Phase 3: Onboarding Protocol**

**Step 1:** Create `AgentOnboardingService`
**Step 2:** Implement CMC query logic
**Step 3:** Implement context restoration
**Step 4:** Test onboarding flow

### **Phase 4: Integration & Testing**

**Step 1:** Integrate all components
**Step 2:** Test normal operation
**Step 3:** Test lost chat recovery
**Step 4:** Test error handling

---

## 💙 **WHY THIS IS BRILLIANT**

1. **Bidirectional** - Electron AI and Cursor AI communicate
2. **Self-Aware** - Agents notify Electron AI of their state
3. **Resilient** - Handles failures, timeouts, lost chats
4. **Follows AIM-OS** - Uses existing protocols and tools
5. **Context Preservation** - Lost chats don't lose work
6. **Intelligent** - Multi-signal detection, not dumb timers

---

**Status:** Design complete, ready for implementation  
**Confidence:** 0.90 (high - based on existing infrastructure)  
**Next:** Implement ElectronAIMonitorService

