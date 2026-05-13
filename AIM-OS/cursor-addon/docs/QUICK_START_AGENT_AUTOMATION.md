# Quick Start: Cursor Agent Automation

**Goal:** Get a Cursor agent running autonomously with monitoring

---

## 🚀 **STEP 1: Create Task Brief**

Create `agent-task.yaml`:

```yaml
objective: "Fix failing tests in auth module"

success_criteria:
  - "All tests pass"
  - "No regressions"

constraints:
  allowed_commands:
    - "pnpm test"
    - "pnpm build"
    - "git add"
    - "git commit -m 'agent: step {step}'"
  
  commit_every_minutes: 15
  max_runtime_hours: 2

context:
  include_dirs: ["packages/auth", "tests/auth"]
  ignore: ["node_modules", "dist", "*.log"]
```

---

## 🚀 **STEP 2: Run Agent (Headless)**

```bash
# In tmux (survives disconnects)
tmux new -s cursor-agent

# Run agent
cursor-agent run --task agent-task.yaml --repo .

# Detach: Ctrl+B, then D
# Reattach: tmux attach -t cursor-agent
```

---

## 🚀 **STEP 3: Monitor via Extension**

The bulletproof messaging system we built can monitor the agent:

```typescript
// Extension watches agent process
const agentProcess = spawn('cursor-agent', ['run', '--task', 'agent-task.yaml']);

agentProcess.stdout.on('data', (data) => {
  // Send to UI via bulletproof messaging
  router.sendMessage(createEnvelope('event', 'agent.output', 'ext->ui', {
    output: data.toString()
  }));
});
```

---

## 🚀 **STEP 4: View in UI Dashboard**

UI receives updates via envelope protocol and displays:

```typescript
// React component subscribes to agent events
useEffect(() => {
  const handleMessage = (event) => {
    if (event.data.topic === 'agent.output') {
      setOutput(prev => [...prev, event.data.payload.output]);
    }
  };
  window.addEventListener('message', handleMessage);
}, []);
```

---

## 📋 **COMPLETE EXAMPLE**

```bash
# Terminal 1: Start agent
tmux new -s cursor-agent
cursor-agent run --task agent-task.yaml --repo .

# Terminal 2: Monitor logs
tail -f agent-logs/agent_*.log

# VS Code: Extension monitors agent
# React UI: Dashboard shows status
```

---

## 🎯 **WHAT THIS ENABLES**

✅ **Multi-hour agent runs** (refactors, migrations)  
✅ **Real-time monitoring** (via UI dashboard)  
✅ **Reliable communication** (via bulletproof messaging)  
✅ **Automatic recovery** (supervisor restarts on failure)  
✅ **Checkpointing** (git commits every 15 minutes)  

---

**Next:** Implement AgentMonitor class in extension

