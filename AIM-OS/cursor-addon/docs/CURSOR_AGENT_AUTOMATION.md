# Cursor Agent Automation - Complete Guide

**Date:** 2025-11-03  
**Purpose:** How to automate Cursor agents for long-running tasks (hours/days)

---

## 🎯 **WHAT WE HAVE VS WHAT WE NEED**

### **What We Built (Bulletproof Messaging)**
✅ Reliable communication between UI and extension  
✅ Message ordering, deduplication, retries  
✅ Dead letter queue for failures  
✅ **This is the infrastructure** - it enables automation!

### **What ChatGPT Suggested (Cursor Agent Automation)**
✅ Cursor Agent CLI (headless operation)  
✅ Plan Mode (longer runs)  
✅ Cloud/Web Agents (event-driven)  
✅ Terminal integration (agent can run commands)  
✅ **This is how to USE Cursor agents autonomously**

### **How They Connect**
The bulletproof messaging system we built can **bridge** between:
- **Automated Cursor agents** (running via CLI/Cloud)
- **Your extension** (monitoring, controlling, reporting)
- **React UI** (dashboard showing agent status)

---

## 🚀 **CURSOR 2.0 AUTOMATION FEATURES**

### **1. Agent CLI (Headless)**
Run Cursor agents without the IDE:
```bash
cursor-agent run --task task.yaml --repo .
```

**Use Cases:**
- Multi-hour refactors
- Test-fix cycles
- Documentation generation
- Dataset curation

**Why it matters:**
- Runs in tmux/screen (survives SSH disconnects)
- No GUI timeout issues
- Perfect for CI/CD
- Can run on remote servers

---

### **2. Plan Mode**
Agent generates multi-step plan and executes it:
- Designed for longer, complex workflows
- Reduces chatter loops
- Sequential execution
- Built-in checkpoints

**Use Cases:**
- Large refactors
- Feature implementations
- Test suite fixes
- Code migrations

---

### **3. Cloud/Web Agents**
Event-driven agents that watch repos:
- Triggered by events (CI failures, PRs, issues)
- APIs for control (start, stop, status)
- Slack/Linear integrations
- True background operation

**Use Cases:**
- Auto-fix flaky tests
- Respond to security alerts
- Auto-open PRs
- Monitor stale branches

---

### **4. Terminal Integration**
Agents can run shell commands:
- Run tests (`pnpm test`)
- Run linters (`ruff`, `prettier`)
- Build projects (`pnpm build`)
- Git operations (`git commit`, `git push`)

**Critical for automation!**

---

## 🔗 **INTEGRATING WITH OUR BULLETPROOF MESSAGING**

### **Architecture: Cursor Agent → Extension → UI**

```
┌─────────────────┐
│ Cursor Agent    │  (CLI or Cloud)
│ (Autonomous)    │
└────────┬────────┘
         │
         │ Terminal Commands
         │ (git, test, build)
         ▼
┌─────────────────┐
│ VS Code         │
│ Extension       │
│                 │
│ ┌─────────────┐ │
│ │ Command     │ │ ← Receives agent commands
│ │ Server      │ │
│ └─────────────┘ │
│                 │
│ ┌─────────────┐ │
│ │ Message     │ │ ← Routes via bulletproof
│ │ Router      │ │   messaging protocol
│ └─────────────┘ │
└────────┬────────┘
         │
         │ Envelope Protocol
         ▼
┌─────────────────┐
│ React UI        │
│ (Dashboard)     │
│                 │
│ - Agent Status  │
│ - Progress      │
│ - Failures      │
│ - Controls      │
└─────────────────┘
```

---

## 📋 **IMPLEMENTATION PATTERNS**

### **Pattern 1: Headless Agent with Extension Monitoring**

**Setup:**
1. Run Cursor Agent CLI in tmux
2. Extension monitors agent via Command Server
3. UI displays agent status via bulletproof messaging

**Flow:**
```bash
# Terminal 1: Run agent in tmux
tmux new -s cursor-agent
cursor-agent run --task refactor.yaml --repo .

# Terminal 2: Extension monitors
# Extension polls Command Server for agent status
# UI receives updates via envelope protocol
```

**Extension Handler:**
```typescript
// Register handler for agent status updates
router.registerHandler('agent.status', async (env) => {
  const status = await getCursorAgentStatus();
  return createEnvelope('response', env.topic, 'ext->ui', status);
});

// Periodic status check
setInterval(async () => {
  const status = await getCursorAgentStatus();
  router.sendMessage(createEnvelope('event', 'agent.status', 'ext->ui', status));
}, 5000); // Every 5 seconds
```

**UI Dashboard:**
```typescript
// React component
const AgentDashboard = () => {
  const [status, setStatus] = useState(null);
  
  useEffect(() => {
    // Subscribe to agent status events
    const handleMessage = (event) => {
      if (event.data.kind === 'event' && event.data.topic === 'agent.status') {
        setStatus(event.data.payload);
      }
    };
    
    window.addEventListener('message', handleMessage);
    
    // Request current status
    sendEnvelope('request', 'agent.status', 'ui->ext');
    
    return () => window.removeEventListener('message', handleMessage);
  }, []);
  
  return (
    <div>
      <h2>Agent Status</h2>
      <div>Status: {status?.state}</div>
      <div>Step: {status?.currentStep} / {status?.totalSteps}</div>
      <div>Last Command: {status?.lastCommand}</div>
      <div>Failures: {status?.failureCount}</div>
    </div>
  );
};
```

---

### **Pattern 2: Command Server Bridge for Agent Control**

**Extend Command Server to accept agent commands:**

```typescript
// In commandServer.ts
router.post('/agent/start', async (req, res) => {
  const { taskFile, repoPath } = req.body;
  
  // Spawn Cursor Agent CLI
  const agentProcess = spawn('cursor-agent', [
    'run',
    '--task', taskFile,
    '--repo', repoPath
  ]);
  
  // Monitor process
  agentProcess.stdout.on('data', (data) => {
    // Send updates via bulletproof messaging
    messageRouter.sendMessage(createEnvelope(
      'event',
      'agent.output',
      'ext->ui',
      { output: data.toString() }
    ));
  });
  
  agentProcess.on('exit', (code) => {
    messageRouter.sendMessage(createEnvelope(
      'event',
      'agent.complete',
      'ext->ui',
      { exitCode: code }
    ));
  });
  
  res.json({ success: true, pid: agentProcess.pid });
});

router.post('/agent/stop', async (req, res) => {
  const { pid } = req.body;
  process.kill(pid, 'SIGTERM');
  res.json({ success: true });
});
```

**UI Control:**
```typescript
const startAgent = async () => {
  const response = await fetch('http://localhost:5001/agent/start', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      taskFile: 'refactor.yaml',
      repoPath: process.cwd()
    })
  });
  
  const result = await response.json();
  console.log('Agent started:', result.pid);
};
```

---

### **Pattern 3: Event-Driven Cloud Agent Integration**

**Setup Cloud Agent webhook:**

```typescript
// In commandServer.ts
router.post('/webhook/cloud-agent', async (req, res) => {
  const event = req.body;
  
  // Route via bulletproof messaging
  await messageRouter.route(createEnvelope(
    'event',
    'cloud-agent.event',
    'ext->ui',
    event
  ));
  
  res.json({ success: true });
});
```

**Cloud Agent Configuration:**
```yaml
# cloud-agent.yaml
triggers:
  - type: ci_failure
    webhook: http://localhost:5001/webhook/cloud-agent
    
  - type: pr_opened
    webhook: http://localhost:5001/webhook/cloud-agent
    
actions:
  - type: run_tests
    command: pnpm test
    
  - type: create_pr
    branch: agent/fix-{issue_id}
```

---

## 📝 **TASK BRIEF TEMPLATE**

### **For Cursor Agent CLI**

```yaml
# agent-task.yaml
objective: "Refactor auth module to support passkeys while keeping API stable"

success_criteria:
  - "All existing tests pass"
  - "New passkey tests added"
  - "No public API changes"
  - "Diff < 500 lines per PR"

constraints:
  allowed_commands:
    - "pnpm test"
    - "pnpm build"
    - "pytest -q"
    - "ruff check"
    - "prettier --write"
    - "git add"
    - "git commit"
    - "git push"
  
  commit_every_minutes: 15
  max_runtime_hours: 6
  branch: "agent/passkeys-refactor"

plan_requirements:
  - "Produce 8-12 step numbered plan with checkpoints"
  - "After each step: summarize changes + next step"
  - "Stop if same test fails 3x; request human input"
  - "Checkpoint every 15 minutes (git commit)"

context:
  include_dirs:
    - "packages/auth"
    - "apps/api"
    - "tests/auth"
  
  ignore:
    - "node_modules"
    - "dist"
    - "*.log"
    - "datasets/**"
    - ".git"

monitoring:
  checkpoint_url: "http://localhost:5001/agent/checkpoint"
  status_url: "http://localhost:5001/agent/status"
  webhook_url: "http://localhost:5001/webhook/agent-event"
```

---

## 🛡️ **SUPERVISOR SCRIPT**

### **Headless Agent Supervisor**

```bash
#!/usr/bin/env bash
# supervisor.sh

set -euo pipefail

LOG_DIR="./agent-logs"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/agent_$(date +%Y%m%d_%H%M).log"
TASK_FILE="${1:-agent-task.yaml}"
REPO_PATH="${2:-.}"

# Configuration
MAX_RUNTIME_HOURS=6
CHECKPOINT_INTERVAL=900  # 15 minutes
STALL_TIMEOUT=600        # 10 minutes (no output)
RESTART_DELAY=60         # 1 minute between restarts

# Trap to cleanup on exit
trap 'kill $(jobs -p) 2>/dev/null || true' EXIT

echo "[$(date)] Starting agent supervisor" | tee -a "$LOG"
echo "Task: $TASK_FILE" | tee -a "$LOG"
echo "Repo: $REPO_PATH" | tee -a "$LOG"

start_agent() {
  local attempt=$1
  echo "[$(date)] Starting agent (attempt $attempt)" | tee -a "$LOG"
  
  # Start agent process
  cursor-agent run \
    --task "$TASK_FILE" \
    --repo "$REPO_PATH" \
    2>&1 | tee -a "$LOG" &
  
  local pid=$!
  echo "[$(date)] Agent PID: $pid" | tee -a "$LOG"
  
  # Monitor for stall
  local last_output=$(date +%s)
  while kill -0 $pid 2>/dev/null; do
    sleep 30
    
    # Check if process is alive
    if ! kill -0 $pid 2>/dev/null; then
      wait $pid
      local exit_code=$?
      echo "[$(date)] Agent exited with code $exit_code" | tee -a "$LOG"
      return $exit_code
    fi
    
    # Check for stall (no output in last N minutes)
    local now=$(date +%s)
    local last_log=$(stat -f %m "$LOG" 2>/dev/null || stat -c %Y "$LOG" 2>/dev/null || echo $now)
    local time_since_output=$((now - last_log))
    
    if [ $time_since_output -gt $STALL_TIMEOUT ]; then
      echo "[$(date)] WARNING: Agent stalled (no output for ${STALL_TIMEOUT}s)" | tee -a "$LOG"
      kill $pid 2>/dev/null || true
      return 1
    fi
  done
  
  wait $pid
  return $?
}

# Main loop
attempt=1
start_time=$(date +%s)
max_runtime=$((MAX_RUNTIME_HOURS * 3600))

while true; do
  # Check runtime limit
  current_time=$(date +%s)
  runtime=$((current_time - start_time))
  
  if [ $runtime -gt $max_runtime ]; then
    echo "[$(date)] Max runtime exceeded (${MAX_RUNTIME_HOURS}h)" | tee -a "$LOG"
    break
  fi
  
  # Start agent
  if start_agent $attempt; then
    echo "[$(date)] Agent completed successfully" | tee -a "$LOG"
    break
  else
    echo "[$(date)] Agent failed, restarting in ${RESTART_DELAY}s..." | tee -a "$LOG"
    sleep $RESTART_DELAY
    attempt=$((attempt + 1))
  fi
done

echo "[$(date)] Supervisor exiting" | tee -a "$LOG"
```

**Usage:**
```bash
# Run in tmux
tmux new -s cursor-agent supervisor.sh agent-task.yaml .

# Or as background service
nohup supervisor.sh agent-task.yaml . > supervisor.log 2>&1 &
```

---

## 📊 **MONITORING INTEGRATION**

### **Extension Agent Monitor**

```typescript
// agentMonitor.ts
import { MessageRouter } from './messaging/router';
import { createEnvelope } from './messaging/envelope';

export class AgentMonitor {
  private router: MessageRouter;
  private agentProcess: any = null;
  private statusInterval: NodeJS.Timeout | null = null;
  
  constructor(router: MessageRouter) {
    this.router = router;
  }
  
  async startAgent(taskFile: string, repoPath: string): Promise<number> {
    // Spawn agent process
    const { spawn } = require('child_process');
    this.agentProcess = spawn('cursor-agent', [
      'run',
      '--task', taskFile,
      '--repo', repoPath
    ], {
      cwd: repoPath
    });
    
    // Monitor output
    this.agentProcess.stdout.on('data', (data: Buffer) => {
      this.sendStatusUpdate({
        type: 'output',
        data: data.toString()
      });
    });
    
    this.agentProcess.stderr.on('data', (data: Buffer) => {
      this.sendStatusUpdate({
        type: 'error',
        data: data.toString()
      });
    });
    
    this.agentProcess.on('exit', (code: number) => {
      this.sendStatusUpdate({
        type: 'exit',
        code
      });
      this.stopMonitoring();
    });
    
    // Start periodic status updates
    this.startMonitoring();
    
    return this.agentProcess.pid;
  }
  
  stopAgent(): void {
    if (this.agentProcess) {
      this.agentProcess.kill('SIGTERM');
      this.agentProcess = null;
    }
    this.stopMonitoring();
  }
  
  private startMonitoring(): void {
    this.statusInterval = setInterval(() => {
      if (this.agentProcess) {
        this.sendStatusUpdate({
          type: 'heartbeat',
          pid: this.agentProcess.pid,
          alive: this.agentProcess.killed === false
        });
      }
    }, 5000); // Every 5 seconds
  }
  
  private stopMonitoring(): void {
    if (this.statusInterval) {
      clearInterval(this.statusInterval);
      this.statusInterval = null;
    }
  }
  
  private sendStatusUpdate(status: any): void {
    this.router.sendMessage(createEnvelope(
      'event',
      'agent.status',
      'ext->ui',
      status
    ));
  }
  
  async getAgentStatus(): Promise<any> {
    if (!this.agentProcess) {
      return { running: false };
    }
    
    return {
      running: !this.agentProcess.killed,
      pid: this.agentProcess.pid
    };
  }
}
```

---

## 🎯 **UI DASHBOARD FOR AGENT MONITORING**

### **React Component**

```typescript
// AgentDashboard.tsx
import React, { useState, useEffect } from 'react';
import * as vscode from 'vscode';

interface AgentStatus {
  running: boolean;
  pid?: number;
  currentStep?: number;
  totalSteps?: number;
  lastCommand?: string;
  output?: string[];
  failures?: number;
}

export const AgentDashboard: React.FC = () => {
  const [status, setStatus] = useState<AgentStatus>({ running: false });
  const [output, setOutput] = useState<string[]>([]);
  
  useEffect(() => {
    // Listen for agent status updates
    const handleMessage = (event: MessageEvent) => {
      const envelope = event.data;
      
      if (envelope.kind === 'event' && envelope.topic === 'agent.status') {
        const payload = envelope.payload;
        
        if (payload.type === 'output') {
          setOutput(prev => [...prev, payload.data]);
        } else if (payload.type === 'exit') {
          setStatus(prev => ({ ...prev, running: false }));
        } else if (payload.type === 'heartbeat') {
          setStatus(prev => ({ ...prev, running: payload.alive }));
        }
      }
    };
    
    window.addEventListener('message', handleMessage);
    
    // Request current status
    const requestStatus = () => {
      const envelope = {
        v: 1,
        id: crypto.randomUUID(),
        seq: 1,
        ts: Date.now(),
        dir: 'ui->ext',
        kind: 'request',
        topic: 'agent.status'
      };
      vscode.postMessage(envelope);
    };
    
    requestStatus();
    const interval = setInterval(requestStatus, 5000);
    
    return () => {
      window.removeEventListener('message', handleMessage);
      clearInterval(interval);
    };
  }, []);
  
  const startAgent = async () => {
    const envelope = {
      v: 1,
      id: crypto.randomUUID(),
      seq: 1,
      ts: Date.now(),
      dir: 'ui->ext',
      kind: 'request',
      topic: 'agent.start',
      payload: {
        taskFile: 'agent-task.yaml',
        repoPath: '.'
      }
    };
    vscode.postMessage(envelope);
  };
  
  const stopAgent = async () => {
    const envelope = {
      v: 1,
      id: crypto.randomUUID(),
      seq: 1,
      ts: Date.now(),
      dir: 'ui->ext',
      kind: 'request',
      topic: 'agent.stop'
    };
    vscode.postMessage(envelope);
  };
  
  return (
    <div className="agent-dashboard">
      <h2>Cursor Agent Monitor</h2>
      
      <div className="status">
        <div>Status: {status.running ? '🟢 Running' : '🔴 Stopped'}</div>
        {status.pid && <div>PID: {status.pid}</div>}
        {status.currentStep && (
          <div>Progress: Step {status.currentStep} / {status.totalSteps}</div>
        )}
        {status.failures !== undefined && (
          <div>Failures: {status.failures}</div>
        )}
      </div>
      
      <div className="controls">
        <button onClick={startAgent} disabled={status.running}>
          Start Agent
        </button>
        <button onClick={stopAgent} disabled={!status.running}>
          Stop Agent
        </button>
      </div>
      
      <div className="output">
        <h3>Agent Output</h3>
        <pre>{output.join('\n')}</pre>
      </div>
    </div>
  );
};
```

---

## 🔧 **COMMAND SERVER ENDPOINTS**

### **Add to commandServer.ts**

```typescript
// Agent control endpoints
router.post('/agent/start', async (req, res) => {
  const { taskFile, repoPath } = req.body;
  
  try {
    const agentMonitor = new AgentMonitor(this.messageRouter);
    const pid = await agentMonitor.startAgent(taskFile, repoPath);
    
    this.sendSuccess(res, { pid, message: 'Agent started' });
  } catch (error: any) {
    this.sendError(res, 500, error.message);
  }
});

router.post('/agent/stop', async (req, res) => {
  const { pid } = req.body;
  
  try {
    if (pid) {
      process.kill(pid, 'SIGTERM');
    } else {
      // Stop all agents
      // Implementation depends on your agent manager
    }
    
    this.sendSuccess(res, { message: 'Agent stopped' });
  } catch (error: any) {
    this.sendError(res, 500, error.message);
  }
});

router.get('/agent/status', async (req, res) => {
  try {
    const status = await agentMonitor.getAgentStatus();
    this.sendSuccess(res, status);
  } catch (error: any) {
    this.sendError(res, 500, error.message);
  }
});

router.post('/webhook/agent-event', async (req, res) => {
  const event = req.body;
  
  // Route via bulletproof messaging
  await this.messageRouter.route(createEnvelope(
    'event',
    'agent.webhook',
    'ext->ui',
    event
  ));
  
  this.sendSuccess(res, { received: true });
});
```

---

## 📈 **KPIs & MONITORING**

### **Track These Metrics:**

```typescript
interface AgentMetrics {
  // Work done
  linesChanged: number;
  testsPassed: number;
  commitsMade: number;
  
  // Reliability
  greenCycles: number;           // Consecutive passing test runs
  humanInterrupts: number;        // Should trend down
  revertRate: number;             // Should stay < 5%
  
  // Performance
  meanStepLatency: number;       // Time per step
  totalRuntime: number;          // Hours
  stepsCompleted: number;
  
  // Failures
  failures: number;
  dlqEntries: number;            // Dead letter queue entries
  stalls: number;               // Agent stalls detected
}
```

**Send metrics via bulletproof messaging:**
```typescript
// Periodically send metrics
setInterval(() => {
  const metrics = calculateMetrics();
  router.sendMessage(createEnvelope(
    'event',
    'agent.metrics',
    'ext->ui',
    metrics
  ));
}, 60000); // Every minute
```

---

## 🚨 **FAILURE MODES & FIXES**

### **1. Agent Stalls**
**Problem:** No output for 10+ minutes  
**Fix:** Supervisor detects stall, restarts agent  
**Integration:** Send stall event via bulletproof messaging

### **2. Token Exhaustion**
**Problem:** Context too large  
**Fix:** Use indexing/ignore controls  
**Integration:** Track token usage, alert when high

### **3. Chatty Loops**
**Problem:** Agent gets stuck in loops  
**Fix:** Use Plan Mode, require checkpoints  
**Integration:** Monitor for repeated commands

### **4. Process Dies**
**Problem:** Agent crashes on disconnect  
**Fix:** Use CLI + tmux, supervisor restarts  
**Integration:** Monitor process health, auto-restart

---

## 🎯 **NEXT STEPS**

### **1. Implement Agent Monitor**
- Add `AgentMonitor` class to extension
- Register handlers for agent commands
- Connect to Command Server

### **2. Build UI Dashboard**
- Create React component for agent status
- Display real-time output
- Add start/stop controls

### **3. Create Task Briefs**
- Write task YAML files for common tasks
- Test with short tasks first
- Scale up to longer runs

### **4. Set Up Supervisor**
- Create supervisor script
- Test in tmux
- Add monitoring/alerting

### **5. Integrate Cloud Agents**
- Set up webhook endpoint
- Configure Cloud Agent triggers
- Test event-driven automation

---

## 💡 **SUMMARY**

**What We Built:**
- Bulletproof messaging system (reliable communication)

**What ChatGPT Suggested:**
- Cursor Agent automation patterns (long-running agents)

**How They Connect:**
- Bulletproof messaging enables monitoring/controlling agents
- Extension bridges agents ↔ UI
- UI provides dashboard for agent status
- Command Server provides API for external control

**The Result:**
- **Automated Cursor agents** running for hours/days
- **Real-time monitoring** via UI dashboard
- **Reliable communication** via bulletproof messaging
- **Full control** via Command Server API

---

**Status:** Ready to implement agent automation  
**Next:** Build AgentMonitor class and UI dashboard

---

*Created: 2025-11-03*  
*Complete guide for Cursor agent automation with bulletproof messaging integration*

