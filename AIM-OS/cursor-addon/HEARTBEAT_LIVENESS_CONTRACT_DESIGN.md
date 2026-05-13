# Cursor Chat Autonomous Loop - Heartbeat/Liveness Contract Architecture

**Date:** 2025-11-02  
**Status:** 📋 **FINAL DESIGN**  
**Protocol:** A-H Protocol - Based on ChatGPT & Perplexity insights  
**Key Insight:** "Stop trying to detect perfectly - make agents declare themselves"

---

## 🎯 **CORE PRINCIPLE**

**"Send early, let Cursor serialize"**

- Cursor is FIFO and non-preemptive by default
- If Cursor is still thinking → `"proceed"` just waits in queue
- If Cursor is idle → `"proceed"` runs immediately
- Worst case: 1-2 `"proceed"`s queued, processed in order

**Result:** We don't need perfect detection. We just need:
- Agent alive? → Yes → Don't nudge
- Agent silent? → Nudge

---

## 💡 **THE HEARTBEAT/LIVENESS CONTRACT**

### **Rule:**
> Every agent that is allowed to drive Cursor must emit a status report within **T seconds** of getting a task.
> 
> If no status → supervisor sends `"proceed"` to Cursor chat.

**Simple. Accountable. AIM-OS.**

---

## 🔧 **COMPONENT DESIGN**

### **1. Heartbeat MCP Tool**

**New Tool:** `mcp_lucid-mcp_agent_heartbeat`

**Implementation:** `lucid_mcp_server.py`

```python
def agent_heartbeat(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Agent heartbeat - agents must call this periodically"""
    try:
        agent_id = arguments.get("agent_id", "cursor-primary")
        task_id = arguments.get("task_id", None)
        phase = arguments.get("phase", "unknown")  # started | thinking | waiting_on_cursor | done | error
        notes = arguments.get("notes", "")
        
        # Store heartbeat in CMC
        if self.memory:
            atom_create = AtomCreate(
                modality="text",
                content=AtomContent(inline=f"Agent heartbeat: {agent_id}, phase: {phase}"),
                tags={
                    "type": "agent_heartbeat",
                    "agent_id": agent_id,
                    "phase": phase
                },
                metadata={
                    "agent_id": agent_id,
                    "task_id": task_id,
                    "phase": phase,
                    "notes": notes,
                    "timestamp": datetime.now().isoformat()
                }
            )
            atom = self.memory.create_atom(atom_create)
            heartbeat_id = atom.id
        else:
            heartbeat_id = None
        
        # Update internal state
        if not hasattr(self, 'agent_heartbeats'):
            self.agent_heartbeats = {}
        
        self.agent_heartbeats[agent_id] = {
            "timestamp": datetime.now(),
            "task_id": task_id,
            "phase": phase,
            "notes": notes,
            "heartbeat_id": heartbeat_id
        }
        
        return {
            "success": True,
            "agent_id": agent_id,
            "timestamp": datetime.now().isoformat(),
            "heartbeat_id": heartbeat_id
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
```

**Phase Values:**
- `"started"` - Agent just started task
- `"thinking"` - Agent is processing/working locally
- `"waiting_on_cursor"` - Agent sent message to Cursor, waiting for response
- `"done"` - Agent completed task
- `"error"` - Agent encountered error

---

### **2. Get Agent Status MCP Tool**

**New Tool:** `mcp_lucid-mcp_get_agent_status`

**Implementation:** `lucid_mcp_server.py`

```python
def get_agent_status(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Get current agent status"""
    try:
        agent_id = arguments.get("agent_id", "cursor-primary")
        
        if not hasattr(self, 'agent_heartbeats') or agent_id not in self.agent_heartbeats:
            return {
                "success": True,
                "agent_id": agent_id,
                "status": "not_found",
                "last_heartbeat_ts": None,
                "age_seconds": None
            }
        
        heartbeat = self.agent_heartbeats[agent_id]
        last_ts = heartbeat["timestamp"]
        age_seconds = (datetime.now() - last_ts).total_seconds()
        
        return {
            "success": True,
            "agent_id": agent_id,
            "status": "active",
            "phase": heartbeat["phase"],
            "task_id": heartbeat.get("task_id"),
            "last_heartbeat_ts": last_ts.isoformat(),
            "age_seconds": age_seconds,
            "notes": heartbeat.get("notes", "")
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
```

---

### **3. Supervisor Loop (Simple)**

**Location:** `cursor-addon/src/services/cursorChatSupervisor.ts`

**Implementation:**

```typescript
class CursorChatSupervisor {
    private monitoringInterval: NodeJS.Timeout | null = null;
    
    // Adaptive heartbeat timeouts based on phase
    private readonly HEARTBEAT_TTL = {
        'started': 60000,        // 1 minute - agent just started
        'thinking': 120000,     // 2 minutes - agent working locally (writing files, etc.)
        'waiting_on_cursor': 60000, // 1 minute - waiting for Cursor response
        'done': Infinity,        // Never nudge if done
        'error': 30000          // 30 seconds - errors need quick attention
    };
    
    private readonly POLL_INTERVAL = 5000; // 5 seconds - check every 5s
    private readonly MIN_SEND_INTERVAL = 30000; // 30 seconds minimum between sends
    private lastSendTime: Map<string, number> = new Map();
    
    // Exponential patience for long tasks
    private retryCount: Map<string, number> = new Map();
    private readonly MAX_PATIENCE = 300000; // 5 minutes maximum patience

    startMonitoring(agentId: string = 'cursor-primary'): void {
        if (this.monitoringInterval) {
            this.stopMonitoring();
        }

        this.monitoringInterval = setInterval(async () => {
            await this.checkAgentAndNudge(agentId);
        }, this.POLL_INTERVAL);

        AIMOSLogger.log('SUPERVISOR', 'Started monitoring', { agentId });
    }

    stopMonitoring(): void {
        if (this.monitoringInterval) {
            clearInterval(this.monitoringInterval);
            this.monitoringInterval = null;
        }
        AIMOSLogger.log('SUPERVISOR', 'Stopped monitoring');
    }

    private async checkAgentAndNudge(agentId: string): Promise<void> {
        try {
            // Get agent status via MCP tool
            const statusResult = await this.mcpClient.callTool('get_agent_status', {
                agent_id: agentId
            });

            if (!statusResult.success || !statusResult.result) {
                AIMOSLogger.warn('SUPERVISOR', 'Failed to get agent status');
                return;
            }

            const status = statusResult.result;
            const ageMs = (status.age_seconds || 0) * 1000;
            const phase = status.phase || 'unknown';

            // Get phase-specific timeout (with exponential patience)
            const baseTimeout = this.HEARTBEAT_TTL[phase] || this.HEARTBEAT_TTL['waiting_on_cursor'];
            const retries = this.retryCount.get(agentId) || 0;
            const patienceMs = Math.min(
                baseTimeout * Math.pow(1.5, retries), // Exponential backoff (1.5x multiplier)
                this.MAX_PATIENCE
            );

            AIMOSLogger.log('SUPERVISOR', 'Checking agent status', {
                agentId,
                phase,
                ageMs,
                patienceMs,
                retries
            });

            // Check if agent is silent beyond patience threshold
            if (ageMs > patienceMs) {
                // Agent silent - check if we should nudge based on phase
                if (phase === 'waiting_on_cursor' || phase === 'started') {
                    // Check send window (don't spam)
                    const lastSend = this.lastSendTime.get(agentId) || 0;
                    const timeSinceLastSend = Date.now() - lastSend;

                    if (timeSinceLastSend >= this.MIN_SEND_INTERVAL) {
                        AIMOSLogger.log('SUPERVISOR', 'Agent silent beyond patience, sending proceed', {
                            agentId,
                            phase,
                            ageMs,
                            patienceMs,
                            retries
                        });

                        // Send proceed via Command Server
                        await this.sendProceedSignal();

                        // Increment retry count (for exponential patience)
                        this.retryCount.set(agentId, retries + 1);

                        // Log nudge
                        await this.mcpClient.callTool('store_memory', {
                            content: `Supervisor nudge: Agent ${agentId} silent for ${Math.round(ageMs/1000)}s ` +
                                    `(phase: ${phase}, patience: ${Math.round(patienceMs/1000)}s), sent proceed`,
                            tags: ['supervisor_nudge', 'autonomous_operation', phase]
                        });

                        this.lastSendTime.set(agentId, Date.now());
                    } else {
                        AIMOSLogger.log('SUPERVISOR', 'Agent silent but send window active', {
                            agentId,
                            timeSinceLastSend,
                            minInterval: this.MIN_SEND_INTERVAL
                        });
                    }
                } else if (phase === 'thinking') {
                    // Agent working locally - be more patient
                    AIMOSLogger.log('SUPERVISOR', 'Agent thinking (working locally), being patient', {
                        agentId,
                        ageMs,
                        patienceMs
                    });
                    
                    // Reset retry count if agent is actively working
                    if (ageMs < patienceMs / 2) {
                        this.retryCount.set(agentId, 0);
                    }
                } else if (status.phase === 'done') {
                    // Agent done - stop monitoring
                    AIMOSLogger.log('SUPERVISOR', 'Agent done, stopping monitoring', { agentId });
                    this.stopMonitoring();
                    this.retryCount.delete(agentId);
                } else if (status.phase === 'error') {
                    // Agent error - send help instead of proceed
                    AIMOSLogger.log('SUPERVISOR', 'Agent error, sending help', { agentId });
                    await this.sendHelpSignal();
                }
            } else {
                // Agent is alive (heartbeat recent) - reset retry count
                if (retries > 0 && ageMs < patienceMs / 2) {
                    AIMOSLogger.log('SUPERVISOR', 'Agent heartbeat received, resetting retry count', {
                        agentId,
                        retries
                    });
                    this.retryCount.set(agentId, 0);
                }
            }
        } catch (error: any) {
            AIMOSLogger.error('SUPERVISOR', 'Error checking agent', error);
        }
    }

    private async sendProceedSignal(): Promise<void> {
        try {
            // Use existing /cursor/chat/send endpoint
            const response = await fetch('http://localhost:5001/cursor/chat/send', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: 'proceed',
                    waitForResponse: false
                })
            });

            if (!response.ok) {
                throw new Error(`Failed to send: ${response.status}`);
            }

            AIMOSLogger.success('SUPERVISOR', 'Sent proceed signal');
        } catch (error: any) {
            AIMOSLogger.error('SUPERVISOR', 'Failed to send proceed signal', error);
        }
    }

    private async sendHelpSignal(): Promise<void> {
        // Similar to sendProceedSignal but sends "help" or error message
        // Implementation similar
    }
}
```

---

### **4. Agent Protocol (Must Follow)**

**Every agent that can drive Cursor must:**

**1. On Starting Task:**
```typescript
await mcp.callTool('agent_heartbeat', {
    agent_id: 'cursor-primary',
    task_id: currentTaskId,
    phase: 'started',
    notes: `Starting task: ${taskDescription}`
});
```

**2. While Working:**
```typescript
// Every 30-60 seconds while working (longer interval for file writing):
await mcp.callTool('agent_heartbeat', {
    agent_id: 'cursor-primary',
    task_id: currentTaskId,
    phase: 'thinking',
    notes: `Working on: ${currentSubtask}`
});
```

**Heartbeat Frequency Guidelines:**
- **Quick operations:** Every 10-20 seconds
- **Medium operations:** Every 30-45 seconds
- **Long operations (file writing):** Every 60-90 seconds
- **Critical:** Must heartbeat before timeout (2 minutes for "thinking" phase)

**3. When Waiting for Cursor:**
```typescript
// After sending message to Cursor chat:
await mcp.callTool('agent_heartbeat', {
    agent_id: 'cursor-primary',
    task_id: currentTaskId,
    phase: 'waiting_on_cursor',
    notes: `Waiting for Cursor response to: ${lastMessage}`
});
```

**4. On Completion:**
```typescript
await mcp.callTool('agent_heartbeat', {
    agent_id: 'cursor-primary',
    task_id: currentTaskId,
    phase: 'done',
    notes: `Task complete: ${result}`
});
```

**5. On Error:**
```typescript
await mcp.callTool('agent_heartbeat', {
    agent_id: 'cursor-primary',
    task_id: currentTaskId,
    phase: 'error',
    notes: `Error: ${errorMessage}`
});
```

---

## 🔄 **COMPLETE WORKFLOW**

```
1. Agent starts task
   ↓ Calls agent_heartbeat(phase="started")
   ↓
2. Agent sends message to Cursor chat
   ↓ Calls agent_heartbeat(phase="waiting_on_cursor")
   ↓
3. Supervisor monitors (every 2 seconds):
   → Checks get_agent_status()
   → If heartbeat age > 8s AND phase="waiting_on_cursor"
   → Sends "proceed" via /cursor/chat/send
   ↓
4. Cursor processes "proceed" (FIFO queue)
   ↓
5. Agent continues working
   ↓ Calls agent_heartbeat(phase="thinking")
   ↓
6. Loop continues until phase="done"
```

---

## 🚨 **SAFETY FEATURES**

### **1. Phase-Based Adaptive Timeouts**

**Different patience for different phases:**
```typescript
const HEARTBEAT_TTL = {
    'started': 60000,        // 1 minute - agent just started, needs time to initialize
    'thinking': 120000,     // 2 minutes - agent working locally (writing files, analyzing code)
    'waiting_on_cursor': 60000, // 1 minute - waiting for Cursor response
    'done': Infinity,        // Never nudge if done
    'error': 30000          // 30 seconds - errors need quick attention
};
```

**Why Longer Timeouts:**
- **Writing long files:** Agent may be generating 1000+ lines, can't heartbeat for minutes
- **Complex analysis:** Agent may be processing large codebases
- **Multiple operations:** Agent may be doing several things before next heartbeat
- **Network latency:** MCP tool calls may have delays

**Rationale:**
- Better to wait longer than interrupt agent mid-work
- FIFO queue means extra "proceed" messages just queue (harmless)
- Agent can always heartbeat if it's actually stuck

---

### **2. Exponential Patience (Adaptive)**

**For long tasks, increase patience over time:**
```typescript
const baseTimeout = HEARTBEAT_TTL[phase];
const retries = this.retryCount.get(agentId) || 0;
const patienceMs = Math.min(
    baseTimeout * Math.pow(1.5, retries), // Exponential backoff (1.5x multiplier)
    MAX_PATIENCE // Cap at 5 minutes
);
```

**Example Progression:**
- **Phase: "thinking"** (base: 2 minutes)
  - Retry 0: 2 minutes (120s)
  - Retry 1: 3 minutes (180s)
  - Retry 2: 4.5 minutes (270s)
  - Retry 3+: 5 minutes (300s) - capped

**Why Exponential:**
- First nudge: Agent might be finishing something
- Second nudge: Agent might be doing something longer
- Third+ nudge: Agent likely stuck, but give it maximum patience

---

### **3. Send Window Protection**

**Prevents spam even with long timeouts:**
```typescript
const MIN_SEND_INTERVAL = 30000; // 30 seconds minimum between sends
const lastSend = this.lastSendTime.get(agentId) || 0;
if (Date.now() - lastSend < MIN_SEND_INTERVAL) {
    return; // Don't send yet, wait for send window
}
```

**Why 30 seconds:**
- Even if patience timeout reached, don't send more than once per 30s
- Prevents rapid-fire "proceed" messages if agent is truly stuck
- FIFO queue processes messages in order anyway

---

### **4. Retry Count Reset**

**Reset patience when agent heartbeats:**
```typescript
// Agent is alive (heartbeat recent) - reset retry count
if (retries > 0 && ageMs < patienceMs / 2) {
    this.retryCount.set(agentId, 0);
}
```

**Why Reset:**
- If agent heartbeats after we nudged, it means it's working
- Reset retry count so next timeout uses base patience
- Prevents patience from growing indefinitely

### **3. Phase-Based Logic**

**Different actions for different phases:**
- `waiting_on_cursor` → Send "proceed"
- `thinking` → Don't send (agent working locally)
- `done` → Stop monitoring
- `error` → Send "help" instead

---

## 📊 **INTEGRATION WITH EXISTING SYSTEMS**

### **Extension Command Server**

**New Endpoint:**
```typescript
// POST /cursor/chat/supervisor/start
{
    "agentId": "cursor-primary",
    "heartbeatTTL": 8000,
    "pollInterval": 2000
}

// POST /cursor/chat/supervisor/stop
{
    "agentId": "cursor-primary"
}

// GET /cursor/chat/supervisor/status
{
    "agentId": "cursor-primary"
}
```

### **MCP Server**

**New Tools:**
- `agent_heartbeat` - Agents call this
- `get_agent_status` - Supervisor calls this

**Uses Existing:**
- CMC storage (via `store_memory` pattern)
- Timeline entries (via `add_timeline_entry`)

---

## 🎯 **WHY THIS IS PERFECT**

1. **Simple** - Just heartbeat timestamps, no complex detection
2. **Accountable** - Agents must report or get nudged
3. **Safe** - FIFO queue means no harm in sending early
4. **Patient** - Long timeouts (1-2 minutes) allow agents to write files
5. **Adaptive** - Exponential patience for long tasks
6. **Resilient** - Works even if Cursor UI changes
7. **Auditable** - All heartbeats stored in CMC
8. **Follows AIM-OS** - Uses existing MCP tools and patterns

---

## ⏱️ **TIMING RATIONALE**

### **Why 1-2 Minute Timeouts?**

**Agent Activities That Take Time:**
- **Writing long files:** Generating 1000+ line files can take 2-5 minutes
- **Code analysis:** Processing large codebases, running tests
- **Multiple operations:** Agent may do several things before next heartbeat
- **Network latency:** MCP tool calls may have delays
- **Complex reasoning:** Agent thinking through complex problems

**Example Scenarios:**

**Scenario 1: Writing Large File**
```
Agent: "I'm generating a 2000-line TypeScript file"
Phase: "thinking"
Heartbeat: Every 60 seconds while writing
Timeout: 2 minutes (allows writing without interruption)
```

**Scenario 2: Analyzing Codebase**
```
Agent: "I'm analyzing 50 files to understand architecture"
Phase: "thinking"
Heartbeat: Every 45 seconds while analyzing
Timeout: 2 minutes (allows deep analysis)
```

**Scenario 3: Waiting for Cursor**
```
Agent: "Sent message to Cursor, waiting for response"
Phase: "waiting_on_cursor"
Heartbeat: Every 30 seconds while waiting
Timeout: 1 minute (Cursor usually responds faster)
```

**Scenario 4: Agent Stuck**
```
Agent: Last heartbeat 3 minutes ago, phase="waiting_on_cursor"
Action: Send "proceed" (agent likely stuck)
Result: Cursor processes message, agent continues
```

### **Exponential Patience Explained**

**First Nudge (after 1-2 minutes):**
- Agent might be finishing something important
- Give it base patience

**Second Nudge (after 1.5-3 minutes):**
- Agent might be doing something longer than expected
- Increase patience by 1.5x

**Third+ Nudge (after 2.25-5 minutes):**
- Agent likely stuck or hung
- Use maximum patience (5 minutes)
- Still send "proceed" but less frequently

**Why This Works:**
- Respects agent work patterns
- Prevents interruption of long operations
- Still recovers from stuck states
- FIFO queue handles multiple "proceed" messages gracefully

---

## 📝 **IMPLEMENTATION PLAN**

### **Phase 1: MCP Tools**

**Step 1:** Add `agent_heartbeat` tool to `lucid_mcp_server.py`
- Implement heartbeat storage in CMC
- Track heartbeat timestamps
- Support all phases (started, thinking, waiting_on_cursor, done, error)

**Step 2:** Add `get_agent_status` tool to `lucid_mcp_server.py`
- Query latest heartbeat from CMC or memory
- Calculate age since last heartbeat
- Return phase, task_id, notes, timestamp

**Step 3:** Test MCP tools
- Test heartbeat storage
- Test status retrieval
- Verify CMC integration

### **Phase 2: Supervisor Service**

**Step 1:** Create `cursorChatSupervisor.ts` in extension
- Implement phase-based adaptive timeouts
- Implement exponential patience logic
- Implement send window protection
- Implement retry count reset logic

**Step 2:** Implement monitoring loop
- Poll every 5 seconds (configurable)
- Check agent status via MCP tool
- Calculate patience based on phase and retries
- Send "proceed" if agent silent beyond patience

**Step 3:** Integrate with `/cursor/chat/send` endpoint
- Use existing macro-based send endpoint
- Handle errors gracefully
- Log all nudges to CMC

**Step 4:** Add Command Server endpoints
- `POST /cursor/chat/supervisor/start` - Start monitoring
- `POST /cursor/chat/supervisor/stop` - Stop monitoring
- `GET /cursor/chat/supervisor/status` - Get monitoring status

### **Phase 3: Agent Protocol**

**Step 1:** Document heartbeat protocol
- Document all phases and when to use them
- Document heartbeat frequency guidelines
- Document timeout expectations
- Create protocol checklist for agents

**Step 2:** Update autonomous operation to call heartbeats
- Add heartbeat calls in autonomous operation loop
- Call heartbeat before starting task
- Call heartbeat during work (every 30-60s)
- Call heartbeat when waiting for Cursor
- Call heartbeat on completion/error

**Step 3:** Test agent heartbeat compliance
- Verify agents call heartbeat regularly
- Verify phases are correct
- Verify timeout handling works
- Test with long-running tasks

### **Phase 4: Onboarding & Testing**

**Step 1:** Use existing onboarding protocol
- Query CMC for last agent heartbeat
- Get timeline entries
- Get goal progress
- Build context summary

**Step 2:** Query CMC for agent state
- Get last heartbeat timestamp
- Get last phase
- Get last task_id
- Get recent memories

**Step 3:** Restore and continue
- Send onboarding message to Cursor chat
- Start supervisor monitoring
- Verify agent picks up context

**Step 4: Comprehensive Testing**
- Test with quick tasks (< 1 minute)
- Test with medium tasks (1-5 minutes)
- Test with long tasks (5+ minutes, file writing)
- Test lost chat recovery
- Test error handling
- Test timeout scenarios
- Verify no interruption of active work

---

---

## 🤖 **AGENT BEHAVIOR PATTERNS & BEST PRACTICES**

### **Pattern 1: Long File Writing**

**Scenario:** Agent needs to generate a 2000-line TypeScript file

**Agent Protocol:**
```typescript
// 1. Start task
await mcp.callTool('agent_heartbeat', {
    agent_id: 'cursor-primary',
    task_id: 'write-large-file',
    phase: 'started',
    notes: 'Starting to write 2000-line TypeScript file'
});

// 2. Begin writing (may take 3-5 minutes)
// ... code generation happens ...

// 3. Heartbeat every 60-90 seconds during writing
await mcp.callTool('agent_heartbeat', {
    agent_id: 'cursor-primary',
    task_id: 'write-large-file',
    phase: 'thinking',
    notes: 'Writing file, line 500/2000'
});

// ... continue writing ...

await mcp.callTool('agent_heartbeat', {
    agent_id: 'cursor-primary',
    task_id: 'write-large-file',
    phase: 'thinking',
    notes: 'Writing file, line 1500/2000'
});

// 4. File complete
await mcp.callTool('agent_heartbeat', {
    agent_id: 'cursor-primary',
    task_id: 'write-large-file',
    phase: 'done',
    notes: 'File complete, 2000 lines written'
});
```

**Supervisor Behavior:**
- Sees `phase="thinking"` → Uses 2-minute base timeout
- After 2 minutes, calculates patience: 2min * 1.5^retries
- Agent heartbeats every 60-90s → Supervisor never nudges
- Agent completes task → Supervisor stops monitoring

---

### **Pattern 2: Multi-Step Task Chain**

**Scenario:** Agent needs to do 5 sequential operations

**Agent Protocol:**
```typescript
// Step 1: Analysis
await mcp.callTool('agent_heartbeat', {
    agent_id: 'cursor-primary',
    task_id: 'multi-step-task',
    phase: 'thinking',
    notes: 'Analyzing codebase structure'
});

// ... analysis ...

// Step 2: Send to Cursor for confirmation
await cursorApi.sendChatMessage('Please review this analysis');
await mcp.callTool('agent_heartbeat', {
    agent_id: 'cursor-primary',
    task_id: 'multi-step-task',
    phase: 'waiting_on_cursor',
    notes: 'Waiting for Cursor review'
});

// Step 3: Cursor responds, continue
await mcp.callTool('agent_heartbeat', {
    agent_id: 'cursor-primary',
    task_id: 'multi-step-task',
    phase: 'thinking',
    notes: 'Implementing changes based on review'
});

// ... implementation ...

// Step 4: Send to Cursor for testing
await cursorApi.sendChatMessage('Please test this implementation');
await mcp.callTool('agent_heartbeat', {
    agent_id: 'cursor-primary',
    task_id: 'multi-step-task',
    phase: 'waiting_on_cursor',
    notes: 'Waiting for Cursor test results'
});

// Step 5: Complete
await mcp.callTool('agent_heartbeat', {
    agent_id: 'cursor-primary',
    task_id: 'multi-step-task',
    phase: 'done',
    notes: 'Task complete, all steps finished'
});
```

**Supervisor Behavior:**
- Alternates between `thinking` (2min timeout) and `waiting_on_cursor` (1min timeout)
- Adapts patience based on phase
- Never interrupts active work

---

### **Pattern 3: Error Recovery**

**Scenario:** Agent encounters error, needs help

**Agent Protocol:**
```typescript
try {
    // ... work ...
} catch (error) {
    await mcp.callTool('agent_heartbeat', {
        agent_id: 'cursor-primary',
        task_id: 'error-task',
        phase: 'error',
        notes: `Error: ${error.message}`
    });
    
    // Ask for help
    await cursorApi.sendChatMessage('Error encountered, need help');
}
```

**Supervisor Behavior:**
- Sees `phase="error"` → Uses 30-second timeout
- Sends "help" instead of "proceed"
- Faster response for errors

---

### **Pattern 4: Agent Stuck (No Heartbeat)**

**Scenario:** Agent loses connection or hangs

**Agent Protocol:**
- **Agent fails to heartbeat** → Supervisor detects silence

**Supervisor Behavior:**
```typescript
// Time passes: 2 minutes, no heartbeat
// Supervisor checks:
- phase="thinking" → patience = 2min * 1.5^0 = 2min
- ageMs = 120000 (2 minutes)
- ageMs > patienceMs → true
- Send "proceed" via /cursor/chat/send

// Time passes: 3 minutes, still no heartbeat
// Supervisor checks:
- phase="thinking" → patience = 2min * 1.5^1 = 3min
- ageMs = 180000 (3 minutes)
- ageMs > patienceMs → true
- Send "proceed" (respects 30s send window)

// Time passes: 4.5 minutes, still no heartbeat
// Supervisor checks:
- phase="thinking" → patience = 2min * 1.5^2 = 4.5min
- ageMs = 270000 (4.5 minutes)
- ageMs > patienceMs → true
- Send "proceed" (respects 30s send window)

// Time passes: 5+ minutes, still no heartbeat
// Supervisor checks:
- phase="thinking" → patience = 5min (capped)
- ageMs = 300000+ (5+ minutes)
- ageMs > patienceMs → true
- Send "proceed" (respects 30s send window)
```

**Result:**
- Agent gets nudged every 30 seconds (send window)
- Cursor processes "proceed" messages (FIFO queue)
- Agent eventually recovers or gets restarted

---

## 🔍 **EDGE CASES & HANDLING**

### **Edge Case 1: Agent Heartbeats Just Before Timeout**

**Scenario:** Agent heartbeats at 1min 59s (just before 2min timeout)

**Handling:**
```typescript
// Supervisor checks:
- ageMs = 119000 (1min 59s)
- patienceMs = 120000 (2 minutes)
- ageMs < patienceMs → false (doesn't trigger)
- No nudge sent
- Agent continues working
```

**Result:** Agent gets full timeout period, no premature nudge

---

### **Edge Case 2: Multiple Agents**

**Scenario:** Multiple agents running simultaneously

**Handling:**
```typescript
// Supervisor tracks each agent separately
const agentIds = ['cursor-primary', 'cursor-secondary', 'cursor-test'];

agentIds.forEach(agentId => {
    this.checkAgentAndNudge(agentId);
});
```

**Result:** Each agent monitored independently, separate retry counts

---

### **Edge Case 3: Supervisor Restarts**

**Scenario:** Supervisor service restarts mid-monitoring

**Handling:**
```typescript
// On restart, query MCP for current agent status
const status = await mcp.get_agent_status({ agent_id: 'cursor-primary' });

// If agent is active, resume monitoring
if (status.status === 'active' && status.phase !== 'done') {
    this.startMonitoring('cursor-primary');
}
```

**Result:** Supervisor resumes monitoring seamlessly

---

### **Edge Case 4: Cursor Chat Not Responding**

**Scenario:** Cursor chat endpoint fails or times out

**Handling:**
```typescript
try {
    await this.sendProceedSignal();
} catch (error) {
    // Log error, don't crash
    AIMOSLogger.error('SUPERVISOR', 'Failed to send proceed signal', error);
    
    // Continue monitoring, will retry on next check
    // Agent heartbeat will eventually succeed
}
```

**Result:** Supervisor resilient to temporary failures

---

### **Edge Case 5: Agent Rapidly Changes Phase**

**Scenario:** Agent switches from `thinking` → `waiting_on_cursor` → `thinking` rapidly

**Handling:**
```typescript
// Supervisor checks every 5 seconds
// Phase changes are captured in heartbeat
// Patience recalculated based on current phase
// Retry count maintained per agent (not per phase)
```

**Result:** Supervisor adapts to phase changes, maintains patience history

---

## 📊 **MONITORING & OBSERVABILITY**

### **Metrics to Track**

**Supervisor Metrics:**
- `nudges_sent` - Total number of "proceed" messages sent
- `nudges_by_phase` - Nudges broken down by phase
- `avg_patience_ms` - Average patience before nudge
- `heartbeat_age_ms` - Age of last heartbeat when nudged
- `retry_count_distribution` - Distribution of retry counts

**Agent Metrics:**
- `heartbeat_frequency` - How often agent heartbeats
- `phase_duration` - Time spent in each phase
- `timeout_events` - Times agent exceeded timeout
- `heartbeat_missed` - Missed heartbeats (detected by supervisor)

**System Metrics:**
- `supervisor_uptime` - How long supervisor has been running
- `agents_monitored` - Number of agents currently monitored
- `cursor_chat_success_rate` - Success rate of sending messages

### **Logging Strategy**

**Supervisor Logs:**
```typescript
// Every check
AIMOSLogger.log('SUPERVISOR', 'Checking agent status', {
    agentId,
    phase,
    ageMs,
    patienceMs,
    retries
});

// Every nudge
AIMOSLogger.log('SUPERVISOR', 'Agent silent beyond patience, sending proceed', {
    agentId,
    phase,
    ageMs,
    patienceMs,
    retries
});

// Every error
AIMOSLogger.error('SUPERVISOR', 'Error checking agent', error);
```

**Agent Logs (via Heartbeat):**
```typescript
// Every heartbeat stored in CMC
{
    "kind": "agent_heartbeat",
    "agent": "cursor-primary",
    "task": "build-ui-v3",
    "phase": "thinking",
    "ts": "2025-11-02T12:41:00Z",
    "notes": "Working on component"
}
```

---

## 🎯 **VALIDATION & TESTING**

### **Unit Tests**

**Test Cases:**
1. **Heartbeat Storage:** Verify heartbeat stored in CMC
2. **Status Retrieval:** Verify status query returns correct data
3. **Timeout Calculation:** Verify patience calculation based on phase
4. **Exponential Patience:** Verify retry count affects patience
5. **Send Window:** Verify send window prevents spam
6. **Phase-Based Logic:** Verify correct action for each phase
7. **Retry Reset:** Verify retry count resets on heartbeat

### **Integration Tests**

**Test Scenarios:**
1. **Normal Operation:** Agent heartbeats regularly, supervisor doesn't nudge
2. **Silent Agent:** Agent stops heartbeating, supervisor nudges
3. **Long Task:** Agent takes 5+ minutes, supervisor uses exponential patience
4. **Phase Changes:** Agent changes phases rapidly, supervisor adapts
5. **Error Recovery:** Agent reports error, supervisor sends help
6. **Multiple Agents:** Multiple agents monitored simultaneously
7. **Supervisor Restart:** Supervisor restarts, resumes monitoring

### **End-to-End Tests**

**Test Scenarios:**
1. **Full Task Cycle:** Agent completes task from start to finish
2. **Lost Chat Recovery:** Agent loses chat, new agent onboards
3. **File Writing:** Agent writes large file, supervisor doesn't interrupt
4. **Multi-Step Task:** Agent completes multi-step task chain
5. **Error Scenario:** Agent encounters error, supervisor helps recovery

---

---

## 🔍 **ADDITIONAL DETECTION METHODS**

### **Primary Method: Heartbeat Contract (Already Documented)**

**This is the primary method** - agents must heartbeat, supervisor monitors timestamps.

**However, we can add additional detection signals as backups:**

---

### **Method 2: Probe-Command Detector**

**Idea:** Try to execute Cursor's cancel/stop commands. If they succeed (don't throw), Cursor is busy. If they fail or are no-ops, Cursor is idle.

**Implementation:**

```typescript
/**
 * Probe-command detector - checks if Cursor is actively generating
 * by attempting to execute cancel/stop commands
 */
async function isCursorBusy(): Promise<boolean> {
    const candidateCmds = [
        'cursor.cancelGeneration',
        'cursor.agent.cancel',
        'cursor.chat.cancel',
        'workbench.action.chat.cancel',
        'aichat.cancel',
        'composer.cancel'
    ];

    for (const cmd of candidateCmds) {
        try {
            // Attempt to execute command
            // If it succeeds, Cursor might be in an active state
            await vscode.commands.executeCommand(cmd);
            
            // If command executed without error, Cursor might be busy
            // However, we need to verify this doesn't always succeed
            // Some commands might always succeed (no-op when idle)
            
            // For now, if command exists and executes, check if it's meaningful
            // This requires testing with actual Cursor behavior
            
            return true; // Tentative: Cursor might be busy
        } catch (e) {
            // Command doesn't exist or failed - continue checking
            continue;
        }
    }

    return false; // No cancel commands found or all failed
}
```

**Integration into Supervisor:**

```typescript
private async checkAgentAndNudge(agentId: string): Promise<void> {
    // ... existing heartbeat check ...
    
    // Additional signal: Probe-command detector (backup)
    if (ageMs > patienceMs) {
        // Check if Cursor is actually busy via command probe
        const cursorBusy = await this.isCursorBusy();
        
        if (cursorBusy) {
            // Cursor is busy - don't nudge yet, even if heartbeat is old
            AIMOSLogger.log('SUPERVISOR', 'Cursor busy (probe-command), waiting', {
                agentId,
                ageMs,
                cursorBusy
            });
            return;
        }
        
        // Cursor not busy AND heartbeat old → safe to nudge
        await this.sendProceedSignal();
    }
}
```

**Advantages:**
- Direct detection without screenshots
- No external dependencies
- Works within extension sandbox

**Limitations:**
- Requires Cursor to expose cancel commands
- Some commands might always succeed (no-op when idle)
- Needs testing to verify behavior

---

### **Method 3: Extension Export Detector**

**Idea:** Check if Cursor extension exports internal agent state APIs.

**Implementation:**

```typescript
/**
 * Extension export detector - checks if Cursor exposes internal state
 */
async function checkCursorExtensionState(): Promise<boolean | null> {
    try {
        const cursorExt = vscode.extensions.getExtension('cursor.cursor');
        
        if (!cursorExt || !cursorExt.exports) {
            return null; // No exports available
        }
        
        const exports = cursorExt.exports;
        
        // Check for various possible API shapes
        if (typeof exports.agent?.isRunning === 'function') {
            return exports.agent.isRunning();
        }
        
        if (typeof exports.runner?.isActive === 'function') {
            return exports.runner.isActive();
        }
        
        if (typeof exports.taskManager?.hasActiveTasks === 'function') {
            return exports.taskManager.hasActiveTasks();
        }
        
        if (typeof exports.composer?.isGenerating === 'function') {
            return exports.composer.isGenerating();
        }
        
        return null; // No known API found
    } catch (error) {
        AIMOSLogger.warn('SUPERVISOR', 'Failed to check Cursor extension state', error);
        return null;
    }
}
```

**Integration:**

```typescript
private async checkAgentAndNudge(agentId: string): Promise<void> {
    // ... existing heartbeat check ...
    
    // Additional signal: Extension export detector (backup)
    if (ageMs > patienceMs) {
        const cursorState = await this.checkCursorExtensionState();
        
        if (cursorState === true) {
            // Cursor is busy - don't nudge
            AIMOSLogger.log('SUPERVISOR', 'Cursor busy (extension export), waiting', {
                agentId,
                ageMs,
                cursorState
            });
            return;
        }
        
        // Cursor not busy AND heartbeat old → safe to nudge
        await this.sendProceedSignal();
    }
}
```

**Advantages:**
- Direct API access if available
- Most reliable if Cursor exposes it
- No external dependencies

**Limitations:**
- May not be available (Cursor might not expose APIs)
- API shape unknown (requires discovery)
- Might change in future Cursor versions

---

### **Method 4: Storage/State Watcher**

**Idea:** Monitor Cursor's workspace storage for state changes (e.g., `generating=true`).

**Implementation:**

```typescript
/**
 * Storage watcher - monitors Cursor's workspace storage for state
 */
class CursorStorageWatcher {
    private storagePath: string | null = null;
    private watcher: vscode.FileSystemWatcher | null = null;
    private lastState: boolean = false;

    async initialize(): Promise<void> {
        // Find Cursor's workspace storage path
        // Typically: ~/.cursor/User/workspaceStorage/
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            return;
        }

        // Cursor stores state in workspaceStorage
        // This is platform-specific and may require discovery
        const storageUri = vscode.Uri.joinPath(
            workspaceFolder.uri,
            '.cursor',
            'workspaceStorage',
            'state.json'
        );

        try {
            // Watch for changes
            this.watcher = vscode.workspace.createFileSystemWatcher(
                new vscode.RelativePattern(storageUri, '**/*')
            );

            this.watcher.onDidChange(async () => {
                const state = await this.readState();
                if (state !== this.lastState) {
                    this.lastState = state;
                    AIMOSLogger.log('SUPERVISOR', 'Cursor state changed', { busy: state });
                }
            });

            // Read initial state
            this.lastState = await this.readState();
        } catch (error) {
            AIMOSLogger.warn('SUPERVISOR', 'Failed to initialize storage watcher', error);
        }
    }

    async readState(): Promise<boolean> {
        // Attempt to read Cursor's state file
        // This is speculative - actual implementation depends on Cursor's storage format
        try {
            // Would need to discover actual storage location and format
            return false; // Placeholder
        } catch (error) {
            return false;
        }
    }

    isBusy(): boolean {
        return this.lastState;
    }

    dispose(): void {
        this.watcher?.dispose();
    }
}
```

**Limitations:**
- Requires discovering Cursor's storage format
- Storage location may be platform-specific
- May not be reliable if Cursor uses encrypted storage

---

### **Method 5: Vision/Macro Fallback (Electron App)**

**Idea:** Use Electron app to capture screenshots and template-match for the "Stop" button.

**Architecture:**

```
[Cursor Extension]
   |
   |  (HTTP: /vision/stop-check)
   v
[Electron App]
   |
   | 1. capture screen (desktopCapturer)
   | 2. find template (stop.png)
   | 3. return {present: true/false, bbox, screen}
   |
   v
[Cursor Extension]
   |
   | if !present → send "proceed"
   v
Cursor chat (macro style)
```

**Electron Side:**

```typescript
// packages/ide_chat_app/src/services/visionService.ts

import { desktopCapturer } from 'electron';
import * as robot from 'robotjs';

export class VisionService {
    private stopButtonTemplate: Buffer | null = null;

    async initialize(): Promise<void> {
        // Load stop button template image
        // This should be a screenshot of Cursor's "Stop" button
        const templatePath = path.join(__dirname, 'templates', 'stop-button.png');
        this.stopButtonTemplate = await fs.readFile(templatePath);
    }

    async checkStopButton(): Promise<{ present: boolean; x?: number; y?: number }> {
        try {
            // Capture screen
            const sources = await desktopCapturer.getSources({
                types: ['screen'],
                thumbnailSize: { width: 1920, height: 1080 }
            });

            if (sources.length === 0) {
                return { present: false };
            }

            // Find Cursor window (simplified - actual implementation needs window detection)
            const cursorScreen = sources.find(s => s.name.includes('Cursor'));
            if (!cursorScreen) {
                return { present: false };
            }

            // Template match (simplified - actual implementation needs image processing)
            // Using a library like opencv4nodejs or native-image-diff
            const match = await this.templateMatch(
                cursorScreen.thumbnail.toPNG(),
                this.stopButtonTemplate
            );

            if (match) {
                return {
                    present: true,
                    x: match.x,
                    y: match.y
                };
            }

            return { present: false };
        } catch (error) {
            console.error('Vision check failed:', error);
            return { present: false };
        }
    }

    async clickAt(x: number, y: number): Promise<void> {
        robot.moveMouse(x, y);
        robot.mouseClick();
    }

    private async templateMatch(
        screen: Buffer,
        template: Buffer,
        threshold: number = 0.85
    ): Promise<{ x: number; y: number } | null> {
        // Template matching implementation
        // Would use opencv4nodejs or similar library
        // Simplified for documentation
        return null;
    }
}

// Express endpoint
app.post('/vision/stop-check', async (req, res) => {
    const visionService = new VisionService();
    const result = await visionService.checkStopButton();
    res.json(result);
});

app.post('/input/click', async (req, res) => {
    const { x, y } = req.body;
    const visionService = new VisionService();
    await visionService.clickAt(x, y);
    res.json({ ok: true });
});
```

**Extension Side:**

```typescript
/**
 * Vision fallback - checks if Stop button is visible via Electron app
 */
async function checkStopButtonViaVision(): Promise<boolean> {
    try {
        const response = await fetch('http://localhost:5001/vision/stop-check', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        if (!response.ok) {
            return false;
        }

        const data = await response.json();
        return data.present === true;
    } catch (error) {
        AIMOSLogger.warn('SUPERVISOR', 'Vision check failed', error);
        return false; // Assume not busy if vision check fails
    }
}
```

**Integration:**

```typescript
private async checkAgentAndNudge(agentId: string): Promise<void> {
    // ... existing heartbeat check ...
    
    // Additional signal: Vision fallback (last resort)
    if (ageMs > patienceMs) {
        // Only use vision if other methods are uncertain
        const cursorBusy = await this.checkStopButtonViaVision();
        
        if (cursorBusy) {
            // Stop button visible - Cursor is busy
            AIMOSLogger.log('SUPERVISOR', 'Cursor busy (vision), waiting', {
                agentId,
                ageMs,
                cursorBusy
            });
            return;
        }
        
        // Stop button not visible AND heartbeat old → safe to nudge
        await this.sendProceedSignal();
    }
}
```

**Advantages:**
- Works regardless of Cursor API availability
- Version-agnostic (works if UI changes)
- Can also click buttons if needed

**Limitations:**
- Requires Electron app running
- Performance overhead (screenshot + template matching)
- May break with UI theme/DPI changes
- Requires maintaining template images

---

## 🎯 **DETECTION METHOD PRIORITY**

### **Primary: Heartbeat Contract**
1. **Agent heartbeats** every 30-90 seconds
2. **Supervisor monitors** heartbeat timestamps
3. **No heartbeat** → send "proceed"

**Why Primary:**
- Simple, reliable, auditable
- Works regardless of Cursor internals
- Agents are accountable

### **Secondary: Probe-Command Detector**
1. Try to execute cancel/stop commands
2. If commands succeed → Cursor busy
3. If commands fail → Cursor idle

**Why Secondary:**
- Direct detection within extension
- No external dependencies
- Faster than heartbeat (immediate)

### **Tertiary: Extension Export Detector**
1. Check Cursor extension exports
2. If APIs available → use them
3. If not → fall back to other methods

**Why Tertiary:**
- Most reliable if available
- May not be available
- Requires discovery

### **Quaternary: Vision/Macro Fallback (ANTIFRAGILE APPROACH)**
1. Electron app captures screenshot
2. Template-match for Stop button (multi-template: light/dark/hover)
3. If Stop visible → Cursor busy
4. If Stop not visible → Cursor idle
5. Handshake with extension after sending to prevent rapid-fire

**Why Quaternary (But Actually Most Antifragile):**
- ✅ **Cursor can change internals, not its pixels** - UI buttons stay visually obvious
- ✅ **You control the brain, Cursor controls the hands** - Macro decides WHEN, extension decides HOW
- ✅ **FIFO makes over-eager sends safe** - Queued messages processed in order
- ✅ **No DOM = no breakage on updates** - Pixel anchors survive minor changes
- ✅ **Can layer MCP observability on top** - Visual is trigger, MCP is record

**Improvements:**
- Multi-template matching (light/dark/hover) for theme resilience
- Handshake mechanism: Extension replies `{accepted: true, ts: ...}` → macro pauses 1.5-2s
- Future-proof: Works regardless of Cursor API changes

---

## 🔄 **COMPLETE SUPERVISOR LOGIC WITH ALL METHODS**

```typescript
private async checkAgentAndNudge(agentId: string): Promise<void> {
    try {
        // PRIMARY: Get agent heartbeat status
        const statusResult = await this.mcpClient.callTool('get_agent_status', {
            agent_id: agentId
        });

        if (!statusResult.success || !statusResult.result) {
            AIMOSLogger.warn('SUPERVISOR', 'Failed to get agent status');
            return;
        }

        const status = statusResult.result;
        const ageMs = (status.age_seconds || 0) * 1000;
        const phase = status.phase || 'unknown';

        // Calculate patience
        const baseTimeout = this.HEARTBEAT_TTL[phase] || this.HEARTBEAT_TTL['waiting_on_cursor'];
        const retries = this.retryCount.get(agentId) || 0;
        const patienceMs = Math.min(
            baseTimeout * Math.pow(1.5, retries),
            this.MAX_PATIENCE
        );

        // Check if agent is silent beyond patience threshold
        if (ageMs > patienceMs) {
            // SECONDARY: Probe-command detector
            const cursorBusyProbe = await this.isCursorBusy();
            if (cursorBusyProbe) {
                AIMOSLogger.log('SUPERVISOR', 'Cursor busy (probe-command), waiting', {
                    agentId,
                    ageMs,
                    cursorBusyProbe
                });
                return;
            }

            // TERTIARY: Extension export detector
            const cursorBusyExport = await this.checkCursorExtensionState();
            if (cursorBusyExport === true) {
                AIMOSLogger.log('SUPERVISOR', 'Cursor busy (extension export), waiting', {
                    agentId,
                    ageMs,
                    cursorBusyExport
                });
                return;
            }

            // QUATERNARY: Vision fallback (only if other methods uncertain)
            if (this.enableVisionFallback) {
                const cursorBusyVision = await this.checkStopButtonViaVision();
                if (cursorBusyVision) {
                    AIMOSLogger.log('SUPERVISOR', 'Cursor busy (vision), waiting', {
                        agentId,
                        ageMs,
                        cursorBusyVision
                    });
                    return;
                }
            }

            // All checks passed - safe to nudge
            if (phase === 'waiting_on_cursor' || phase === 'started') {
                // Check send window
                const lastSend = this.lastSendTime.get(agentId) || 0;
                const timeSinceLastSend = Date.now() - lastSend;

                if (timeSinceLastSend >= this.MIN_SEND_INTERVAL) {
                    AIMOSLogger.log('SUPERVISOR', 'All checks passed, sending proceed', {
                        agentId,
                        phase,
                        ageMs,
                        patienceMs,
                        retries
                    });

                    await this.sendProceedSignal();
                    this.retryCount.set(agentId, retries + 1);
                    this.lastSendTime.set(agentId, Date.now());
                }
            }
        }
    } catch (error: any) {
        AIMOSLogger.error('SUPERVISOR', 'Error checking agent', error);
    }
}
```

---

## 📊 **CONFIGURATION**

```typescript
interface SupervisorConfig {
    // Primary method (always enabled)
    heartbeatEnabled: true;
    
    // Secondary methods (optional)
    probeCommandEnabled: boolean;
    extensionExportEnabled: boolean;
    visionFallbackEnabled: boolean;
    
    // Timing
    pollInterval: number; // 5000ms
    minSendInterval: number; // 30000ms
    
    // Heartbeat timeouts
    heartbeatTTL: {
        started: number;
        thinking: number;
        waiting_on_cursor: number;
        done: number;
        error: number;
    };
}
```

---

## 🎯 **WHY THIS LAYERED APPROACH**

1. **Primary (Heartbeat):** Simple, reliable, agents accountable
2. **Secondary (Probe):** Fast detection, works within extension
3. **Tertiary (Export):** Most reliable if available
4. **Quaternary (Vision):** Last resort, version-agnostic

**Result:** Robust detection with multiple fallbacks, primary method is simple and reliable.

---

## 🔄 **ONBOARDING PROTOCOL (Lost Chats)**

**Uses existing CMC data:**

```typescript
async onboardNewAgent(): Promise<void> {
    // 1. Get last agent heartbeat from CMC
    const lastHeartbeat = await mcp.retrieve_memory({
        query: 'agent heartbeat cursor-primary',
        limit: 1
    });
    
    // 2. Get timeline entries
    const timeline = await mcp.get_timeline_entries({
        limit: 20
    });
    
    // 3. Get goal progress
    const goals = await mcp.query_goal_timeline({
        status: 'in_progress'
    });
    
    // 4. Build context
    const context = {
        lastTask: lastHeartbeat[0]?.metadata?.task_id,
        lastPhase: lastHeartbeat[0]?.metadata?.phase,
        timeline: timeline,
        goals: goals
    };
    
    // 5. Send onboarding message
    await cursorApi.sendChatMessage(
        `Onboarding: Continuing from ${context.lastPhase}. ` +
        `Task: ${context.lastTask}. ` +
        `Goal: ${goals[0]?.name}. ` +
        `proceed`
    );
    
    // 6. Start supervisor monitoring
    supervisor.startMonitoring('cursor-primary');
}
```

---

## 💡 **MACRO/VISION APPROACH (ANTIFRAGILE)**

**Key Insight:** Visual-anchored + extension-bridge is the most antifragile path.

### **Why Macro/Vision Wins:**

1. **Cursor can change internals, not its pixels**
   - They can rename commands, move APIs, reshuffle exports
   - But user-facing "Send"/"Stop" buttons stay visually obvious
   - You're locking onto what they *can't* silently refactor

2. **You control the brain, Cursor controls the hands**
   - Macro only decides **when** to send
   - Extension decides **how** to send (command chaining → macro fallback)
   - Logic stays portable across Cursor versions

3. **FIFO makes over-eager sends safe**
   - Even if detection fires slightly early, it just queues
   - That's a huge safety valve

4. **No DOM = no breakage on updates**
   - DOM hooks die on minor changes
   - Pixel anchors don't, especially with multi-template variants

5. **You can layer MCP observability on top**
   - Visual is the trigger
   - MCP is the record
   - That's AIM-OS in spirit: action first, evidence logged, history coherent

### **Implementation: Multi-Template Matching**

```typescript
// Electron app side (macro automation)
class VisionDetector {
    private templates = {
        stop_light: './templates/stop_light.png',
        stop_dark: './templates/stop_dark.png',
        stop_hover: './templates/stop_hover.png'
    };
    
    async isCursorBusy(): Promise<boolean> {
        const screenshot = await captureCursorChat();
        
        // Try all 3 templates, accept nearest match
        for (const [name, templatePath] of Object.entries(this.templates)) {
            const match = await templateMatch(screenshot, templatePath);
            if (match.confidence > 0.85) {
                return true; // Stop button visible = Cursor busy
            }
        }
        
        return false; // No stop button = Cursor idle
    }
}
```

### **Handshake Mechanism**

```typescript
// Extension side (commandServer.ts)
private async handleSendChatMessage(request: {
    message: string;
    waitForResponse?: boolean;
}): Promise<any> {
    // ... send message via macro ...
    
    // Return handshake signal
    return {
        success: true,
        accepted: true,
        ts: Date.now(),
        method: 'macro-automation'
    };
}

// Electron app side (macro automation)
async sendProceedSignal(): Promise<void> {
    const response = await this.cursorApi.sendChatMessage('proceed');
    
    if (response.accepted) {
        // Handshake received - pause to prevent rapid-fire
        await new Promise(resolve => setTimeout(resolve, 2000)); // 1.5-2s pause
    }
}
```

### **Complete Macro-First Architecture**

```
Electron App (Macro Brain)
    ↓ (detects Stop button via vision)
    ↓ (decides: send "proceed")
    ↓
Extension HTTP Bridge (/cursor/chat/send)
    ↓ (receives handshake)
    ↓
Macro Automation (Keyboard/Mouse)
    ↓
Cursor Chat UI (FIFO queue)
    ↓
MCP Tools (Record action in CMC)
```

**Result:** A vision-gated, FIFO-safe, Cursor-embedded autopilot using nothing but macro builder, clear UI, and tiny HTTP bridge. That's about as consistent as it gets without hacking Cursor's core.

---

**Status:** Final design complete  
**Confidence:** 0.95 (very high - simple, proven pattern)  
**Next:** Implement heartbeat MCP tools

