# Cursor Chat Autonomous Loop - Design Based on AIM-OS Patterns

**Date:** 2025-11-02  
**Status:** 📋 **DESIGN PHASE**  
**Protocol:** A-H Protocol - Context Mapping & Hypothesis Formation  
**Based on:** AIM-OS autonomous operation patterns, proven work patterns

---

## 🎯 **INTENT CAPTURE (A-H Protocol Step A)**

### **Goal:**
**Enable Cursor chat to automatically send "proceed" after each AI response, creating hands-free autonomous operation**

### **Key Requirements:**
- ✅ Messages MUST appear in Cursor chat UI (visible)
- ✅ Must detect when Cursor AI finishes responding
- ✅ Must automatically send "proceed" after detection
- ✅ Must integrate with AIM-OS autonomous operation protocols
- ✅ Must use existing MCP tools (`should_continue_autonomous`, `generate_next_autonomous_task`)

---

## 🔍 **CONTEXT MAPPING (A-H Protocol Step C)**

### **Existing AIM-OS Infrastructure:**

**1. Autonomous Operation MCP Tools (9 tools):**
- `should_continue_autonomous` - Checks if should continue (confidence, checklist)
- `generate_next_autonomous_task` - Generates next task (Pattern 8)
- `get_autonomous_status` - Gets operation status
- `start_autonomous_operation` - Starts operation
- `pause_autonomous_operation` - Pauses operation
- `stop_autonomous_operation` - Stops operation
- `run_autonomous_checklist` - Safety validation
- `fix_autonomous_issues` - Auto-recovery
- `generate_next_autonomous_task` - Self-prompting (Pattern 8)

**2. Pattern 8: Self-Prompting Loop (from autonomous_work_patterns.md):**
```
1. Complete current task
2. Reflect: What did I build? Quality good?
3. Generate: What are logical next tasks?
4. Prioritize: Calculate priority scores
5. Choose: Highest priority ≥0.70 confidence
6. Execute: Begin next task
7. Loop: Repeat indefinitely
```

**3. MessageMonitorService (Electron app):**
- Polls CMC every 3 seconds
- Detects "proceed" messages
- Triggers `start_autonomous_operation`
- Monitors agent states
- Checks `should_continue_autonomous`

**4. Extension Command Server:**
- `/cursor/chat/send` endpoint (macro-based) ✅ Already implemented
- Can send messages to Cursor chat

---

## 💡 **HYPOTHESIS FORMATION (A-H Protocol Step B)**

### **Hypothesis 1: Multi-Signal Detection (RECOMMENDED)**

**Approach:** Combine multiple detection signals using AIM-OS confidence routing

**Detection Signals:**
1. **Chat Input Ready State** - Poll VS Code command to check if chat input is ready
2. **Typing Indicator** - Monitor if Cursor AI is typing (if accessible)
3. **Autonomous Status Check** - Use `should_continue_autonomous` MCP tool
4. **Task Completion Check** - Use `get_autonomous_status` to see if task completed
5. **Message Count** - Monitor chat message count (if accessible)

**Confidence Routing:**
- Each signal has confidence score (0.0-1.0)
- Combined confidence = weighted average
- If combined confidence ≥0.70 → Send "proceed"
- If <0.70 → Wait longer or use more signals

**Implementation:**
```typescript
private async detectCursorAIResponseComplete(): Promise<{
    isComplete: boolean;
    confidence: number;
    signals: Array<{ name: string; value: any; confidence: number }>;
}> {
    const signals = [];
    
    // Signal 1: Chat input ready (check VS Code command)
    const chatReady = await this.checkChatInputReady();
    signals.push({ name: 'chat_input_ready', value: chatReady, confidence: 0.70 });
    
    // Signal 2: Autonomous status (check if should continue)
    const shouldContinue = await this.checkShouldContinueAutonomous();
    signals.push({ name: 'should_continue', value: shouldContinue, confidence: 0.85 });
    
    // Signal 3: Autonomous status (check if task completed)
    const status = await this.getAutonomousStatus();
    signals.push({ name: 'task_completed', value: status.tasksCompleted, confidence: 0.80 });
    
    // Combined confidence (weighted average)
    const combinedConfidence = signals.reduce((sum, s) => sum + s.confidence, 0) / signals.length;
    
    // Decision: ≥0.70 = complete
    return {
        isComplete: combinedConfidence >= 0.70,
        confidence: combinedConfidence,
        signals
    };
}
```

**Why This Works:**
- Uses AIM-OS confidence routing pattern
- Multiple signals prevent false positives
- Integrates with existing autonomous operation tools
- Follows Pattern 8 (Self-Prompting Loop)

---

### **Hypothesis 2: Autonomous Operation Integration**

**Approach:** Use existing autonomous operation loop, but send "proceed" to Cursor chat

**Flow:**
```
1. User sends initial message to Cursor chat
2. Cursor AI responds
3. Extension polls autonomous status (every 3 seconds)
4. Extension checks `should_continue_autonomous`
5. If should continue → Extension sends "proceed" via `/cursor/chat/send`
6. Cursor AI processes "proceed"
7. Loop continues
```

**Why This Works:**
- Uses existing autonomous operation infrastructure
- Integrates with Pattern 8
- Uses proven MCP tools
- No new detection logic needed

---

### **Hypothesis 3: Hybrid Approach (BEST)**

**Approach:** Combine both - use autonomous operation tools + multi-signal detection

**Flow:**
```
1. Start autonomous operation (`start_autonomous_operation` MCP tool)
2. Send initial message to Cursor chat
3. Monitor loop:
   - Check `should_continue_autonomous` (every 3 seconds)
   - Check chat input ready state
   - Check autonomous status
   - Multi-signal detection
4. If signals indicate completion → Send "proceed" via `/cursor/chat/send`
5. Cursor AI processes "proceed"
6. Loop continues until `should_continue_autonomous` returns false
```

**Why This Works:**
- Uses AIM-OS autonomous operation protocols
- Multi-signal detection ensures accuracy
- Follows Pattern 8 (Self-Prompting Loop)
- Integrates with existing infrastructure

---

## 🏗️ **DEEP EXPANSION LAYER (A-H Protocol Step D)**

### **Component Design:**

**1. CursorChatAutonomousLoop Service**
- Location: `cursor-addon/src/services/cursorChatAutonomousLoop.ts`
- Purpose: Manages autonomous loop for Cursor chat
- Responsibilities:
  - Start/stop loop
  - Monitor detection signals
  - Send "proceed" messages
  - Integrate with autonomous operation MCP tools

**2. Response Detection Engine**
- Purpose: Multi-signal detection of Cursor AI response completion
- Signals:
  - Chat input ready state
  - Autonomous operation status
  - Task completion status
  - Message count (if accessible)
- Confidence routing per signal

**3. Integration with Autonomous Operation**
- Uses existing MCP tools:
  - `should_continue_autonomous`
  - `get_autonomous_status`
  - `generate_next_autonomous_task`
- Follows Pattern 8 (Self-Prompting Loop)

---

## 📋 **IMPLEMENTATION PLAN**

### **Phase 1: Response Detection (Multi-Signal)**

**Step 1: Implement Detection Signals**
- Check chat input ready state (VS Code command)
- Check autonomous operation status (MCP tool)
- Check task completion (MCP tool)
- Combine signals with confidence routing

**Step 2: Create Detection Engine**
- Multi-signal detection function
- Confidence calculation
- Decision logic (≥0.70 threshold)

### **Phase 2: Autonomous Loop Integration**

**Step 3: Create CursorChatAutonomousLoop Service**
- Start loop function
- Stop loop function
- Monitor loop function
- Integration with `/cursor/chat/send` endpoint

**Step 4: Integrate with Autonomous Operation**
- Call `should_continue_autonomous` before sending "proceed"
- Use `get_autonomous_status` for monitoring
- Follow Pattern 8 (Self-Prompting Loop)

### **Phase 3: Extension Command Server Integration**

**Step 5: Add Endpoint**
- `POST /cursor/chat/autonomous-loop` (re-implemented properly)
- Parameters:
  - `initialMessage`: First message to send
  - `proceedMessage`: Message to send after each response (default: "proceed")
  - `confidenceThreshold`: Minimum confidence to send (default: 0.70)
  - `pollIntervalSeconds`: How often to check (default: 3)

**Step 6: Implement Loop Logic**
- Send initial message
- Wait for response (detection)
- Check `should_continue_autonomous`
- If should continue → Send "proceed"
- Repeat until `should_continue_autonomous` returns false

---

## 🔧 **DETECTION SIGNAL IMPLEMENTATION**

### **Signal 1: Chat Input Ready State**

**Approach:** Check if chat input is ready for new message

**Implementation:**
```typescript
private async checkChatInputReady(): Promise<boolean> {
    try {
        // Try to execute a command that requires chat input to be ready
        // If chat is still processing, this might fail or timeout
        await vscode.commands.executeCommand('workbench.action.focusChatInput');
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Check if we can get chat state
        // This is heuristic - may need refinement
        return true;
    } catch (error) {
        return false;
    }
}
```

**Confidence:** 0.70 (heuristic, may need refinement)

---

### **Signal 2: Autonomous Operation Status**

**Approach:** Use `should_continue_autonomous` MCP tool

**Implementation:**
```typescript
private async checkShouldContinueAutonomous(): Promise<boolean> {
    try {
        const result = await this.mcpClient.callTool('should_continue_autonomous', {});
        return result.should_continue === true;
    } catch (error) {
        return false;
    }
}
```

**Confidence:** 0.85 (uses proven MCP tool)

---

### **Signal 3: Task Completion Status**

**Approach:** Use `get_autonomous_status` MCP tool

**Implementation:**
```typescript
private async checkTaskCompleted(): Promise<boolean> {
    try {
        const status = await this.mcpClient.callTool('get_autonomous_status', {});
        // If tasks completed increased, task likely finished
        // This is heuristic - may need state tracking
        return status.tasks_completed > this.lastTaskCount;
    } catch (error) {
        return false;
    }
}
```

**Confidence:** 0.80 (uses proven MCP tool, heuristic)

---

## 🎯 **COMPLETE FLOW**

```
1. User/Election app starts autonomous loop
   ↓
2. Extension sends initial message to Cursor chat
   ↓
3. Cursor AI processes and responds
   ↓
4. Extension monitors detection signals (every 3 seconds):
   - Chat input ready state
   - Should continue autonomous?
   - Task completed?
   ↓
5. Combined confidence ≥0.70 → Send "proceed"
   ↓
6. Cursor AI processes "proceed"
   ↓
7. Extension checks `should_continue_autonomous`
   ↓
8. If should continue → Loop back to step 4
   ↓
9. If should not continue → Stop loop
```

---

## 📊 **INTEGRATION WITH EXISTING SYSTEMS**

### **Extension Command Server:**
- Uses `/cursor/chat/send` endpoint (already implemented)
- Adds `/cursor/chat/autonomous-loop` endpoint
- Integrates with MCP client for autonomous operation tools

### **Electron App:**
- Can trigger autonomous loop via Command Server
- Can monitor loop status
- Can stop loop manually

### **Autonomous Operation MCP Tools:**
- Uses existing `should_continue_autonomous` tool
- Uses existing `get_autonomous_status` tool
- Follows Pattern 8 (Self-Prompting Loop)

---

## 🚨 **RISK MITIGATION**

### **Risk 1: False Positives (Sending "proceed" too early)**
**Mitigation:** Multi-signal detection with confidence routing
- Requires ≥0.70 combined confidence
- Multiple signals must agree
- Autonomous operation tools validate

### **Risk 2: False Negatives (Missing completion)**
**Mitigation:** Multiple detection signals
- Not relying on single signal
- Fallback to time-based if all signals fail
- User can manually trigger

### **Risk 3: Infinite Loop**
**Mitigation:** `should_continue_autonomous` check
- MCP tool validates before each "proceed"
- Stops if confidence < threshold
- Stops if checklist fails

---

## 📝 **NEXT STEPS**

1. **Research Detection Signals** - Verify which VS Code commands/Cursor APIs are available
2. **Implement Multi-Signal Detection** - Build detection engine
3. **Create Autonomous Loop Service** - Integrate with existing infrastructure
4. **Test with Real Cursor Chat** - Validate detection accuracy
5. **Document Integration** - Update AIM-OS documentation

---

**Status:** Design phase complete, ready for implementation research  
**Confidence:** 0.80 (high - based on proven AIM-OS patterns)  
**Next:** Research specific detection signals available in Cursor

