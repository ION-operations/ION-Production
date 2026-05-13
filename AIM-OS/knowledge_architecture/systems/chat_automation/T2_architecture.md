---
id: "chat_automation_T2_architecture"
system: "chat_automation"
component: null
level: "T2"
type: "architecture"
title: "Chat Automation Architecture"
description: "2000-word architecture document for Chat Automation"
audience: "developers, architects"
confidence_threshold: 0.70
token_cost: 2000
word_count: 2000
created: "2025-11-05T15:30:00Z"
updated: "2025-11-05T15:30:00Z"
author: "aether"
status: "complete"
tags: ["chat-automation", "architecture", "multi-signal", "autonomous-loop", "t0-t6"]
dependencies: ["autonomous_protocols", "cursor_extension", "mcp_tools", "message_monitor"]
related_docs: ["chat_automation_T0_executive", "chat_automation_T1_overview", "CURSOR_CHAT_AUTONOMOUS_LOOP_DESIGN.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# Chat Automation – T2 Architecture (≈2,000 words)

## 🏗️ **COMPLETE SYSTEM ARCHITECTURE**

### **The Challenge**

**Enable hours-long autonomous Cursor chat sessions** without manual "proceed" intervention. This requires:
1. Accurate detection of when AI response completes
2. Automatic "proceed" sending to continue session
3. Integration with autonomous operation protocols
4. Safety validation before each iteration

### **The Solution: Three-Layer Architecture**

```
┌────────────────────────────────────────────────────────────────────┐
│               CHAT AUTOMATION ARCHITECTURE                          │
├────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │        LAYER 1: MULTI-SIGNAL DETECTION ENGINE                │  │
│  │  ┌────────────────────────────────────────────────────────┐  │  │
│  │  │  Signal 1: Chat Input Ready State (VS Code command)    │  │  │
│  │  │  Confidence: 0.70 (heuristic, may need refinement)     │  │  │
│  │  └────────────────────────────────────────────────────────┘  │  │
│  │                                                                │  │
│  │  ┌────────────────────────────────────────────────────────┐  │  │
│  │  │  Signal 2: Should Continue Autonomous (MCP tool)       │  │  │
│  │  │  Confidence: 0.85 (proven tool, high reliability)     │  │  │
│  │  └────────────────────────────────────────────────────────┘  │  │
│  │                                                                │  │
│  │  ┌────────────────────────────────────────────────────────┐  │  │
│  │  │  Signal 3: Task Completion Status (MCP tool)           │  │  │
│  │  │  Confidence: 0.80 (proven tool, heuristic)            │  │  │
│  │  └────────────────────────────────────────────────────────┘  │  │
│  │                                                                │  │
│  │  ┌────────────────────────────────────────────────────────┐  │  │
│  │  │  Confidence Router (VIF pattern)                       │  │  │
│  │  │  - Weighted average of all signals                     │  │  │
│  │  │  - Decision: ≥0.70 = proceed, <0.70 = wait           │  │  │
│  │  └────────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                         ↓ Detection Result                           │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │        LAYER 2: AUTONOMOUS LOOP SERVICE                      │  │
│  │  ┌────────────────────────────────────────────────────────┐  │  │
│  │  │  CursorChatAutonomousLoop                              │  │  │
│  │  │  - Start/Stop/Pause/Resume loop                        │  │  │
│  │  │  - Monitor detection signals (poll every 3 seconds)    │  │  │
│  │  │  - Send "proceed" via Extension Command Server         │  │  │
│  │  │  - Check should_continue_autonomous before each send   │  │  │
│  │  │  - Store audit trail in CMC                            │  │  │
│  │  └────────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                         ↓ Integration                                │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │          LAYER 3: INTEGRATION LAYER                          │  │
│  │  ┌────────────┐  ┌─────────────┐  ┌──────────────────┐    │  │
│  │  │  Extension │  │  MCP Tools  │  │  Message Monitor │    │  │
│  │  │  Command   │  │  (9 tools)  │  │  Service         │    │  │
│  │  │  Server    │  │  Autonomous │  │  (Electron)      │    │  │
│  │  └────────────┘  └─────────────┘  └──────────────────┘    │  │
│  │       │                │                    │                │  │
│  │       └────────────────┴────────────────────┘                │  │
│  │                        │                                      │  │
│  │                        ↓                                      │  │
│  │  ┌────────────────────────────────────────────────────────┐  │  │
│  │  │  CMC Storage (Complete Audit Trail)                    │  │  │
│  │  │  - All detection events                                │  │  │
│  │  │  - All "proceed" sends                                 │  │  │
│  │  │  - All autonomous status checks                        │  │  │
│  │  └────────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
└────────────────────────────────────────────────────────────────────┘
```

---

## 📦 **CORE COMPONENTS**

### **1. Multi-Signal Detection Engine**

**Purpose:** Accurately detect when Cursor AI response completes

**Location:** `cursor-addon/src/services/responseDetectionEngine.ts` (planned)

**Data Model:**

```typescript
interface DetectionSignal {
    name: string;                    // Signal identifier
    value: boolean | number | string; // Signal value
    confidence: number;              // Signal confidence (0.0-1.0)
    timestamp: number;               // When checked
}

interface DetectionResult {
    isComplete: boolean;             // Final decision
    confidence: number;              // Combined confidence
    signals: DetectionSignal[];      // All signals checked
    recommendation: string;          // Human-readable
}
```

**Core Method:**

```typescript
class ResponseDetectionEngine {
    async detectResponseComplete(): Promise<DetectionResult> {
        const signals: DetectionSignal[] = [];
        
        // Signal 1: Chat Input Ready
        const chatReady = await this.checkChatInputReady();
        signals.push({
            name: 'chat_input_ready',
            value: chatReady,
            confidence: 0.70,  // Heuristic
            timestamp: Date.now()
        });
        
        // Signal 2: Should Continue Autonomous (MCP tool)
        const shouldContinue = await this.mcpClient.callTool(
            'should_continue_autonomous',
            {}
        );
        signals.push({
            name: 'should_continue_autonomous',
            value: shouldContinue.should_continue,
            confidence: 0.85,  // Proven tool
            timestamp: Date.now()
        });
        
        // Signal 3: Task Completion (MCP tool)
        const status = await this.mcpClient.callTool(
            'get_autonomous_status',
            {}
        );
        const taskCompleted = status.tasks_completed > this.lastTaskCount;
        signals.push({
            name: 'task_completed',
            value: taskCompleted,
            confidence: 0.80,  // Proven tool, heuristic
            timestamp: Date.now()
        });
        
        // Calculate combined confidence (weighted average)
        const combinedConfidence = signals.reduce(
            (sum, s) => sum + s.confidence, 
            0
        ) / signals.length;
        
        // Decision: ≥0.70 = complete
        return {
            isComplete: combinedConfidence >= 0.70,
            confidence: combinedConfidence,
            signals,
            recommendation: combinedConfidence >= 0.70 
                ? 'Send proceed now'
                : 'Wait for higher confidence'
        };
    }
}
```

**Why Multi-Signal:**
- **Single signal unreliable:** Chat state can be misleading
- **Multiple signals robust:** Require agreement across signals
- **Confidence routing:** AIM-OS VIF pattern for decisions
- **False positive prevention:** Won't send "proceed" prematurely

---

### **2. Autonomous Loop Service**

**Purpose:** Manage autonomous loop lifecycle and execution

**Location:** `cursor-addon/src/services/cursorChatAutonomousLoop.ts` (planned)

**Data Model:**

```typescript
interface LoopConfig {
    initialMessage: string;          // First message to send
    proceedMessage: string;          // Message to send after each response (default: "proceed")
    confidenceThreshold: number;     // Minimum confidence (default: 0.70)
    pollIntervalSeconds: number;     // How often to check (default: 3)
    maxIterations?: number;          // Safety limit (optional)
    timeoutMinutes?: number;         // Maximum session duration (optional)
}

interface LoopStatus {
    active: boolean;                 // Is loop running?
    iterationsCompleted: number;     // How many "proceed" sent
    lastDetection: DetectionResult | null;
    startedAt: number;
    pausedAt?: number;
}
```

**Core Class:**

```typescript
class CursorChatAutonomousLoop {
    private config: LoopConfig;
    private status: LoopStatus;
    private detectionEngine: ResponseDetectionEngine;
    private commandServer: CommandServerClient;
    private mcpClient: MCPClient;
    private intervalId: NodeJS.Timeout | null;
    
    constructor(config: LoopConfig) {
        this.config = config;
        this.status = {
            active: false,
            iterationsCompleted: 0,
            lastDetection: null,
            startedAt: 0
        };
        this.detectionEngine = new ResponseDetectionEngine();
        this.commandServer = new CommandServerClient();
        this.mcpClient = new MCPClient();
    }
    
    async start(): Promise<void> {
        // Start autonomous operation (MCP tool)
        await this.mcpClient.callTool('start_autonomous_operation', {
            operation_type: 'cursor_chat_autonomous'
        });
        
        // Send initial message
        await this.commandServer.sendChatMessage(this.config.initialMessage);
        
        // Update status
        this.status.active = true;
        this.status.startedAt = Date.now();
        
        // Start monitoring loop
        this.intervalId = setInterval(
            () => this.monitorAndSendProceed(),
            this.config.pollIntervalSeconds * 1000
        );
    }
    
    async stop(): Promise<void> {
        // Stop monitoring loop
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
        
        // Stop autonomous operation (MCP tool)
        await this.mcpClient.callTool('stop_autonomous_operation', {});
        
        // Update status
        this.status.active = false;
    }
    
    private async monitorAndSendProceed(): Promise<void> {
        try {
            // Check if should continue (MCP tool validation)
            const shouldContinue = await this.mcpClient.callTool(
                'should_continue_autonomous',
                {}
            );
            
            if (!shouldContinue.should_continue) {
                // Stop condition met
                await this.stop();
                return;
            }
            
            // Detect if response complete
            const detection = await this.detectionEngine.detectResponseComplete();
            this.status.lastDetection = detection;
            
            // If complete with sufficient confidence, send "proceed"
            if (detection.isComplete && detection.confidence >= this.config.confidenceThreshold) {
                await this.commandServer.sendChatMessage(this.config.proceedMessage);
                this.status.iterationsCompleted++;
                
                // Store audit trail in CMC
                await this.mcpClient.callTool('store_memory', {
                    mpd_id: `chat-automation-proceed-${Date.now()}`,
                    data: {
                        iteration: this.status.iterationsCompleted,
                        detection,
                        message: this.config.proceedMessage
                    },
                    category: 'chat_automation'
                });
            }
        } catch (error) {
            console.error('Error in autonomous loop:', error);
            // Don't stop on error - continue monitoring
        }
    }
}
```

---

### **3. Extension Command Server Integration**

**New Endpoint:** `POST /cursor/chat/autonomous-loop`

**Request:**
```typescript
{
    "action": "start" | "stop" | "pause" | "resume" | "status",
    "config": {  // For "start" action
        "initialMessage": "Begin autonomous work on feature X",
        "proceedMessage": "proceed",
        "confidenceThreshold": 0.70,
        "pollIntervalSeconds": 3
    }
}
```

**Response:**
```typescript
{
    "success": true,
    "status": {
        "active": true,
        "iterationsCompleted": 15,
        "startedAt": 1730847234000,
        "lastDetection": {
            "isComplete": true,
            "confidence": 0.78,
            "signals": [...]
        }
    }
}
```

**Implementation:**

```typescript
// In extension command server
app.post('/cursor/chat/autonomous-loop', async (req, res) => {
    const { action, config } = req.body;
    
    if (action === 'start') {
        // Create new loop instance
        const loop = new CursorChatAutonomousLoop(config);
        await loop.start();
        
        // Store loop instance globally
        activeLoops.set(loop.id, loop);
        
        res.json({ success: true, loop_id: loop.id });
    }
    else if (action === 'stop') {
        const loop = activeLoops.get(req.body.loop_id);
        await loop.stop();
        res.json({ success: true });
    }
    else if (action === 'status') {
        const loop = activeLoops.get(req.body.loop_id);
        res.json({ success: true, status: loop.status });
    }
});
```

---

## 🔗 **INTEGRATION ARCHITECTURE**

### **MCP Tools Integration (9 Tools)**

**Autonomous Operation Tools:**
- `should_continue_autonomous` - Validates before each "proceed" (confidence, checklist, quality)
- `get_autonomous_status` - Gets current status (tasks completed, confidence, issues)
- `start_autonomous_operation` - Starts autonomous mode
- `stop_autonomous_operation` - Stops autonomous mode
- `pause_autonomous_operation` - Pauses autonomous mode
- `resume_autonomous_operation` - Resumes after pause
- `run_autonomous_checklist` - Safety validation
- `fix_autonomous_issues` - Auto-recovery if issues detected
- `generate_next_autonomous_task` - Pattern 8 (Self-Prompting)

**Usage Pattern:**

```typescript
// Before sending "proceed"
const validation = await mcpClient.callTool('should_continue_autonomous', {});

if (validation.should_continue) {
    // Safe to proceed
    await sendProceed();
} else {
    // Stop condition met
    await stopLoop();
    console.log(`Stopped: ${validation.stop_reason}`);
}
```

---

### **Extension Command Server Integration**

**Existing Endpoints (Reused):**
- `POST /cursor/chat/send` - Send message to Cursor chat (macro-based)

**New Endpoints (Added):**
- `POST /cursor/chat/autonomous-loop` - Control autonomous loop

**Protocol Flow:**

```
Electron App / External Client
        ↓ HTTP POST
Extension Command Server (:5001)
        ↓ VS Code Commands
Cursor Chat Interface
        ↓ AI Processing
Cursor AI Response
        ↓ Detection
Multi-Signal Detection Engine
        ↓ Confidence ≥0.70
Send "proceed"
        ↓ Loop
```

---

### **MessageMonitorService Integration (Electron)**

**Purpose:** Electron app can monitor autonomous loop and trigger it

**Integration:**

```typescript
// MessageMonitorService already polls CMC for "proceed" messages
// Extend to also trigger autonomous loop

class MessageMonitorService {
    async checkForNewMessages(): Promise<void> {
        const messages = await this.mcpClient.callTool('get_ai_messages', {
            filters: { priority: 'urgent', to_ai: 'electron-app' }
        });
        
        for (const msg of messages) {
            if (msg.content.toLowerCase().includes('proceed')) {
                // Option 1: Trigger autonomous loop in Cursor
                await this.commandServer.post('/cursor/chat/autonomous-loop', {
                    action: 'start',
                    config: {
                        initialMessage: msg.content,
                        proceedMessage: 'proceed'
                    }
                });
                
                // Option 2: Trigger autonomous operation (existing)
                await this.mcpClient.callTool('start_autonomous_operation', {
                    initial_task: msg.content
                });
            }
        }
    }
}
```

---

## 🎯 **COMPLETE FLOW DIAGRAMS**

### **Flow 1: Starting Autonomous Loop**

```
User/Electron App
  ↓
POST /cursor/chat/autonomous-loop {"action": "start", ...}
  ↓
Extension Command Server
  ↓
CursorChatAutonomousLoop.start()
  ↓
MCP: start_autonomous_operation
  ↓
Extension: Send initial message to Cursor chat
  ↓
Cursor AI: Process message
  ↓
Loop Active: Monitoring begins (every 3 seconds)
```

### **Flow 2: Detection and "Proceed" Sending**

```
Monitor Loop (every 3 seconds)
  ↓
Check Signal 1: Chat input ready? (VS Code command)
Check Signal 2: Should continue? (MCP tool)
Check Signal 3: Task completed? (MCP tool)
  ↓
Calculate combined confidence (weighted average)
  ↓
Confidence ≥0.70?
  ├─ YES → Send "proceed" via /cursor/chat/send
  │         ↓
  │         Cursor AI processes "proceed"
  │         ↓
  │         Loop continues
  │
  └─ NO  → Wait (check again in 3 seconds)
```

### **Flow 3: Stopping Autonomous Loop**

```
Monitor Loop detects stop condition:
  - should_continue_autonomous returns false
  - Max iterations reached
  - Timeout exceeded
  - Manual stop requested
  ↓
Stop monitoring interval
  ↓
MCP: stop_autonomous_operation
  ↓
Store final audit trail in CMC
  ↓
Loop Inactive
```

---

## 🔒 **SAFETY & VALIDATION**

### **Safety Mechanisms**

**1. Confidence Gating:**
- Every "proceed" requires combined confidence ≥0.70
- Multiple signals must agree
- Low confidence = wait, don't send

**2. Autonomous Operation Validation:**
- `should_continue_autonomous` checks:
  - Confidence still ≥0.70?
  - Quality maintained?
  - Alignment preserved?
  - No capability boundaries hit?

**3. Manual Override:**
- User can stop loop anytime
- Electron app provides stop button
- Extension provides pause/resume

**4. Safety Limits:**
- Max iterations (prevent infinite loops)
- Timeout (prevent runaway sessions)
- Error handling (don't crash on detection failure)

### **Validation Checklist**

**Before Each "Proceed":**
- [ ] Combined confidence ≥0.70?
- [ ] `should_continue_autonomous` returns true?
- [ ] No errors in detection?
- [ ] Within max iterations limit?
- [ ] Within timeout limit?

**All must pass before sending "proceed"**

---

## 📋 **IMPLEMENTATION PHASES**

### **Phase 1: Detection Engine (Week 1)**
1. Implement ResponseDetectionEngine class
2. Implement all 3 detection signals
3. Implement confidence routing
4. Test detection accuracy

### **Phase 2: Autonomous Loop Service (Week 1)**
5. Implement CursorChatAutonomousLoop class
6. Integrate with MCP tools
7. Add start/stop/pause/resume
8. Add safety limits

### **Phase 3: Extension Integration (Week 2)**
9. Add `/cursor/chat/autonomous-loop` endpoint
10. Integrate with existing `/cursor/chat/send`
11. Add CMC audit trail storage
12. Test complete flow

### **Phase 4: Electron Integration (Week 2)**
13. Update MessageMonitorService
14. Add autonomous loop UI controls
15. Add real-time status display
16. End-to-end testing

---

## 📊 **EXPECTED METRICS**

**Detection Accuracy:**
- Target: >95% accuracy (no false positives, <5% false negatives)
- Actual: TBD after implementation

**Performance:**
- Poll interval: 3 seconds (configurable)
- Detection latency: <500ms per check
- "Proceed" send latency: <1 second

**Autonomous Session Duration:**
- Target: 2-6 hours continuous
- Max iterations: 100-200 (depending on task complexity)

---

**Status:** Design Complete (Nov 2, 2025) | **Implementation:** Planned  
**Next:** T3 Detailed with complete detection engine and loop service implementation  
**Impact:** Enables true hands-free autonomous operation for Cursor chat
