# Slash Commands for Agent Automation

**Date:** 2025-11-03  
**Status:** Ready for Implementation  
**Tags:** `#cursor-commands` `#mcp-integration` `#agent-automation`  
**Level:** L3 Implementation  
**Location:** `.cursor/commands/` (project) or `~/.cursor/commands/` (user)  
**Related:** [PROTOCOL_DESIGN.md](./PROTOCOL_DESIGN.md) | [PROTOCOL_IMPLEMENTATION_PLAN.md](./PROTOCOL_IMPLEMENTATION_PLAN.md) | [INDEX.md](./INDEX.md)

---

## 📝 **COMMAND FILES**

### **agent-start.md**

```markdown
Start a background agent run.

Usage: `/agent-start [task=task.yaml] [branch=branch-name] [max_runtime=6]`

Example:
/agent-start task=refactor.yaml branch=agent/refactor max_runtime=6

This will:
1. Start a Cursor Background Agent run
2. Use the specified task YAML file
3. Work on the specified branch
4. Run for up to max_runtime hours

The agent will:
- Execute the plan in task.yaml
- Commit checkpoints every 15 minutes
- Send status updates to the UI dashboard
- Complete or fail gracefully

Status updates appear in the React UI dashboard via bulletproof messaging.
```

---

### **agent-stop.md**

```markdown
Stop a running background agent.

Usage: `/agent-stop [run_id=run-id]`

Example:
/agent-stop run_id=abc-123

If no run_id is provided, stops the most recent active run.

This will:
1. Cancel the agent run via Cursor Background Agent API
2. Send a checkpoint if possible
3. Send stopped event to UI dashboard

The agent will:
- Finish current step (if possible)
- Create final checkpoint
- Stop gracefully
```

---

### **agent-status.md**

```markdown
Get status of background agent runs.

Usage: `/agent-status [run_id=run-id]`

Example:
/agent-status run_id=abc-123

If no run_id is provided, shows all active runs.

This will:
1. Query Cursor Background Agent API for status
2. Display current step, progress, last command
3. Show output stream
4. Display metrics

Status includes:
- Current step / total steps
- Last command executed
- Runtime hours
- Exit code (if completed)
- Summary (steps, tests, files changed)
```

---

### **agent-checkpoint.md**

```markdown
Force a checkpoint for a running agent.

Usage: `/agent-checkpoint [run_id=run-id]`

Example:
/agent-checkpoint run_id=abc-123

This will:
1. Tell the agent to create a checkpoint immediately
2. Commit current progress to git
3. Send checkpoint event to UI dashboard

Useful for:
- Before risky operations
- At natural break points
- When you want to save progress mid-run
```

---

### **agent-metrics.md**

```markdown
Get metrics for all agent runs.

Usage: `/agent-metrics`

This will:
1. Query all active runs
2. Calculate metrics:
   - Active runs count
   - Total runtime hours
   - Steps completed
   - Success rate
   - DLQ entries
3. Display in UI dashboard

Metrics include:
- agent.steps_completed
- agent.mean_step_latency_ms
- agent.green_cycles
- bus.ack_rate
- bus.nack_rate
- dlq.size
```

---

## 🔧 **MCP TOOL INTEGRATION**

Each slash command calls an MCP tool:

```typescript
// MCP tools exposed by Command Server:

1. agent.start(task_yaml, branch, max_runtime)
   → Calls Cursor Background Agent API
   → Returns run_id

2. agent.stop(run_id)
   → Cancels agent run
   → Returns success

3. agent.status(run_id)
   → Gets current status
   → Returns status object

4. agent.checkpoint(run_id)
   → Forces checkpoint
   → Returns checkpoint info

5. agent.metrics()
   → Gets all metrics
   → Returns metrics object
```

---

## 📋 **USAGE EXAMPLES**

### **Start Long Refactor:**
```
/agent-start task=refactor-auth.yaml branch=agent/auth-refactor max_runtime=6
```

### **Check Progress:**
```
/agent-status
```

### **Force Checkpoint:**
```
/agent-checkpoint run_id=abc-123
```

### **Stop Agent:**
```
/agent-stop run_id=abc-123
```

### **View Metrics:**
```
/agent-metrics
```

---

## 🎯 **INTEGRATION**

These commands:
1. Call MCP tools (via Command Server)
2. MCP tools call Cursor Background Agent API
3. Events flow via bulletproof messaging
4. UI dashboard shows status

**Complete autonomous operation!**

---

*Created: 2025-11-03*  
*Slash commands for agent automation*

