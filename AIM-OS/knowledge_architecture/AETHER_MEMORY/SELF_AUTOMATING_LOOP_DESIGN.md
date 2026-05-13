# Self-Automating Loop Design - Long Duration Autonomous Operation

**Date:** 2025-11-02  
**Status:** 📋 **DESIGN PHASE**  
**Goal:** Cursor rules with self-automating loop using MCP tools for long-duration autonomous operation

---

## 🎯 **THE VISION**

**Goal:** Create a self-automating loop in cursor rules that:
1. Uses MCP tools for automation
2. Has checks, replies, and waits as needed
3. Continues for long durations automatically
4. Handles interruptions gracefully
5. Resumes automatically when needed

---

## 🔄 **THE LOOP STRUCTURE**

### **Core Loop Pattern:**

```typescript
// Self-Automating Loop with MCP Tools
async function autonomousLoop() {
  while (true) {
    // 1. Check if should continue
    const shouldContinue = await mcp_lucid-mcp_should_continue_autonomous()
    if (!shouldContinue.should_continue) {
      break // Exit loop
    }
    
    // 2. Generate next task
    const nextTask = await mcp_lucid-mcp_generate_next_autonomous_task()
    if (!nextTask.task) {
      // No more tasks, wait and check again
      await sleep(60000) // Wait 1 minute
      continue
    }
    
    // 3. Execute task
    try {
      await executeTask(nextTask.task)
      
      // 4. Send update to Electron app
      await sendMessageToElectron(`Completed: ${nextTask.task.description}`)
      
      // 5. Wait for reply (if needed)
      if (nextTask.wait_for_reply) {
        await waitForReply(300000) // 5 minute timeout
      }
      
      // 6. Track confidence
      await mcp_lucid-mcp_track_confidence(
        task: nextTask.task.description,
        confidence: 0.85,
        reasoning: "Task completed successfully"
      )
      
      // 7. Update goal progress
      await mcp_lucid-mcp_update_goal_progress(
        goal_id: nextTask.goal_id,
        progress: nextTask.progress_update,
        status: "in_progress"
      )
      
    } catch (error) {
      // Handle errors
      await mcp_lucid-mcp_fix_autonomous_issues()
      
      // Store error in memory
      await mcp_lucid-mcp_store_memory(
        content: `Error in autonomous loop: ${error.message}`,
        tags: {type: "error", component: "autonomous_loop"}
      )
      
      // Check if should continue after error
      const shouldContinueAfterError = await mcp_lucid-mcp_should_continue_autonomous()
      if (!shouldContinueAfterError.should_continue) {
        break
      }
    }
    
    // 8. Small delay between tasks
    await sleep(5000) // 5 second delay between tasks
  }
}
```

---

## 🔍 **CHECK POINTS**

### **1. Should Continue Check (Every Loop Iteration)**

**MCP Tool:** `mcp_lucid-mcp_should_continue_autonomous`

**Checks:**
- Confidence level ≥ 0.70?
- Quality standards maintained?
- No critical errors?
- Goal alignment maintained?
- User hasn't stopped?

**Implementation:**
```typescript
const shouldContinue = await mcp_lucid-mcp_should_continue_autonomous()
if (!shouldContinue.should_continue) {
  // Log reason for stopping
  await mcp_lucid-mcp_store_memory(
    content: `Stopping autonomous loop: ${shouldContinue.reason}`,
    tags: {type: "autonomous_stop", reason: shouldContinue.reason}
  )
  break
}
```

### **2. Confidence Check (After Each Task)**

**MCP Tool:** `mcp_lucid-mcp_track_confidence`

**Checks:**
- Task completed successfully?
- Quality maintained?
- No hallucinations?
- Tests passing?

**Implementation:**
```typescript
await mcp_lucid-mcp_track_confidence(
  task: taskDescription,
  confidence: calculatedConfidence,
  reasoning: "Task completed, tests passing, quality maintained"
)
```

### **3. Goal Alignment Check (Every Hour)**

**MCP Tool:** `mcp_lucid-mcp_query_goal_timeline`

**Checks:**
- Tasks align with goals?
- Progress on track?
- No drift?

**Implementation:**
```typescript
const goals = await mcp_lucid-mcp_query_goal_timeline({status: "in_progress"})
for (const goal of goals) {
  // Verify current task aligns with goal
  if (!taskAlignsWithGoal(currentTask, goal)) {
    // Pivot to aligned task
    await pivotToAlignedTask(goal)
  }
}
```

### **4. Error Recovery Check (After Errors)**

**MCP Tool:** `mcp_lucid-mcp_fix_autonomous_issues`

**Checks:**
- Can error be fixed automatically?
- Should continue after error?
- Need to escalate?

**Implementation:**
```typescript
const fixResult = await mcp_lucid-mcp_fix_autonomous_issues()
if (fixResult.fixed) {
  // Continue with next task
  continue
} else {
  // Log issue and check if should continue
  await mcp_lucid-mcp_store_memory(
    content: `Error could not be fixed: ${fixResult.reason}`,
    tags: {type: "error", severity: "high"}
  )
}
```

---

## ⏸️ **WAIT PATTERNS**

### **1. Wait for Reply (When Needed)**

**When:** Task requires user input or confirmation

**Implementation:**
```typescript
async function waitForReply(timeout: number = 300000) {
  const startTime = Date.now()
  let lastMessageId = getLastMessageId()
  
  while (Date.now() - startTime < timeout) {
    await sleep(3000) // Poll every 3 seconds
    
    // Check for reply
    const messages = await mcp_lucid-mcp_get_ai_messages(
      from_ai: "electron-app",
      limit: 10
    )
    
    const newMessages = messages.filter(m => 
      new Date(m.timestamp) > new Date(lastMessageTimestamp)
    )
    
    if (newMessages.length > 0) {
      return newMessages[0] // Return first reply
    }
    
    // Check Cursor state (if vision detector available)
    // Only send "proceed" if Cursor STOPPED
    const cursorState = await checkCursorState()
    if (cursorState.stopped) {
      // Send "proceed" via macro
      await sendProceedViaMacro()
    }
  }
  
  // Timeout reached
  return null
}
```

### **2. Wait Between Tasks**

**When:** Small delay between tasks to prevent overwhelming system

**Implementation:**
```typescript
await sleep(5000) // 5 second delay between tasks
```

### **3. Wait When No Tasks**

**When:** No tasks available, wait and check again

**Implementation:**
```typescript
const nextTask = await mcp_lucid-mcp_generate_next_autonomous_task()
if (!nextTask.task) {
  await sleep(60000) // Wait 1 minute, then check again
  continue
}
```

---

## 🔁 **REPLY PATTERNS**

### **1. Send Update After Task**

**When:** Task completed successfully

**Implementation:**
```typescript
await sendMessageToElectron(
  `✅ Completed: ${task.description}\n` +
  `Progress: ${task.progress}%\n` +
  `Next: ${nextTask.description}`
)
```

### **2. Send Error Report**

**When:** Error occurred but continuing

**Implementation:**
```typescript
await sendMessageToElectron(
  `⚠️ Error in task: ${task.description}\n` +
  `Error: ${error.message}\n` +
  `Attempting recovery...`
)
```

### **3. Send Progress Update**

**When:** Major milestone reached

**Implementation:**
```typescript
await sendMessageToElectron(
  `🎯 Milestone reached: ${milestone.name}\n` +
  `Progress: ${milestone.progress}%\n` +
  `Confidence: ${milestone.confidence}`
)
```

---

## 📋 **CURSOR RULES INTEGRATION**

### **Add to Base Rules:**

```markdown
## 🔄 **SELF-AUTOMATING LOOP PROTOCOL**

**When autonomous operation is active:**

1. **Initialize Loop:**
   - Call `mcp_lucid-mcp_start_autonomous_operation`
   - Set state: "autonomous_active"

2. **Main Loop:**
   - Check `mcp_lucid-mcp_should_continue_autonomous` every iteration
   - Generate next task via `mcp_lucid-mcp_generate_next_autonomous_task`
   - Execute task with error handling
   - Track confidence via `mcp_lucid-mcp_track_confidence`
   - Update goal progress via `mcp_lucid-mcp_update_goal_progress`
   - Send updates to Electron app
   - Wait for replies if needed
   - Small delay between tasks

3. **Error Handling:**
   - Use `mcp_lucid-mcp_fix_autonomous_issues` for recovery
   - Store errors in memory
   - Check if should continue after error

4. **Goal Alignment:**
   - Check goal alignment every hour
   - Pivot if task doesn't align with goals
   - Update goal progress regularly

5. **Long Duration Support:**
   - Store state periodically
   - Resume from last checkpoint if interrupted
   - Handle Cursor restarts gracefully
   - Maintain context across sessions
```

---

## 🎯 **LONG DURATION SUPPORT**

### **1. State Persistence**

**Store state periodically:**
```typescript
// Every 10 tasks, store current state
if (taskCount % 10 === 0) {
  await mcp_lucid-mcp_store_memory(
    content: JSON.stringify({
      currentTask: currentTask,
      completedTasks: completedTasks,
      nextTask: nextTask,
      timestamp: Date.now()
    }),
    tags: {type: "autonomous_state", checkpoint: true}
  )
}
```

### **2. Resume from Checkpoint**

**On restart, resume from last checkpoint:**
```typescript
// Get last checkpoint
const checkpoints = await mcp_lucid-mcp_retrieve_memory(
  query: "autonomous_state checkpoint",
  limit: 1
)

if (checkpoints.length > 0) {
  const lastState = JSON.parse(checkpoints[0].content)
  // Resume from lastState
  currentTask = lastState.currentTask
  completedTasks = lastState.completedTasks
}
```

### **3. Handle Interruptions**

**Graceful shutdown:**
```typescript
// On shutdown signal
process.on('SIGINT', async () => {
  await mcp_lucid-mcp_store_memory(
    content: "Autonomous loop interrupted, saving state",
    tags: {type: "autonomous_interrupt"}
  )
  await mcp_lucid-mcp_pause_autonomous_operation()
  process.exit(0)
})
```

---

## 📊 **MONITORING & OBSERVABILITY**

### **1. Timeline Tracking**

**Track loop progress:**
```typescript
await mcp_lucid-mcp_add_timeline_entry(
  prompt_id: `autonomous_loop_${Date.now()}`,
  user_input: `Task: ${task.description}`,
  context_state: {
    task: task.description,
    progress: task.progress,
    confidence: task.confidence
  }
)
```

### **2. Goal Progress Updates**

**Update goals regularly:**
```typescript
await mcp_lucid-mcp_update_goal_progress(
  goal_id: goalId,
  progress: newProgress,
  milestone: `Completed: ${task.description}`
)
```

### **3. Consciousness Metrics**

**Monitor consciousness state:**
```typescript
const metrics = await mcp_lucid-mcp_get_consciousness_metrics()
if (metrics.attention_narrowing || metrics.cognitive_load_high) {
  // Slow down or pause
  await sleep(30000) // Longer delay
}
```

---

## 🚀 **IMPLEMENTATION PRIORITY**

1. ✅ **Core Loop Structure** - Basic loop with checks
2. ✅ **MCP Tool Integration** - Use existing autonomous tools
3. ⏳ **Error Handling** - Robust error recovery
4. ⏳ **State Persistence** - Checkpoint system
5. ⏳ **Resume Logic** - Restart from checkpoint
6. ⏳ **Monitoring** - Timeline and metrics

---

## 📚 **REFERENCES**

- `cursor-addon/HEARTBEAT_LIVENESS_CONTRACT_DESIGN.md` - Vision detector design
- `knowledge_architecture/AETHER_MEMORY/ELECTRON_CURSOR_AUTOMATION_EPIC.md` - Macro automation
- MCP Tools: `should_continue_autonomous`, `generate_next_autonomous_task`, `track_confidence`, `update_goal_progress`

---

**Status:** 📋 **DESIGN READY FOR IMPLEMENTATION**  
**Next:** Implement core loop structure in cursor rules  
**Goal:** Long-duration autonomous operation with self-automating loop

