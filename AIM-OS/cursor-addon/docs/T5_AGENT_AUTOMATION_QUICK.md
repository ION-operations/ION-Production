---
id: "agent_automation_T5_quick"
system: "agent_automation"
component: null
level: "T5"
type: "quick_reference"
title: "Agent Automation - Quick Reference"
description: "500-word quick reference cheat sheet for Cursor agent automation"
audience: "developers, quick lookup"
confidence_threshold: 0.90
token_cost: 500
word_count: 500
created: "2025-11-04T00:50:00Z"
updated: "2025-11-04T00:50:00Z"
author: "aether"
status: "complete"
tags: ["agent-automation", "quick-reference", "cheat-sheet", "t0-t6", "transitional"]
dependencies: ["agent_automation_T4_complete"]
related_docs: ["T4_AGENT_AUTOMATION_COMPLETE.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# Agent Automation – T5 Quick Reference (≈500 words)

**Quick cheat sheet for common operations**

---

## 🚀 **START AGENT**

**Smart Start (Auto-detect):**
```typescript
const result = await agentMonitor.startAgentSmart({
    prompt: 'Refactor authentication',
    repoPath: '/local/path',  // Auto-detects GitHub URL
    branch: 'main',
    taskFile: 'task.yaml'
});
// Returns: { runId: 'agent-123', method: 'cloud' | 'local' }
```

**Cloud API (GitHub only):**
```typescript
const runId = await agentMonitor.startAgent({
    taskFile: 'task.yaml',
    repoPath: 'https://github.com/user/repo',  // ⚠️ Must be GitHub URL!
    branch: 'main'
});
```

**CLI (Local repos):**
```typescript
const result = await agentMonitor.startLocalAgent({
    prompt: 'Fix TypeScript errors',
    repoPath: '/local/path'
});
```

---

## 📊 **GET STATUS**

```typescript
const status = await agentMonitor.getAgentStatus(runId);
// Returns: { run_id, status, current_step, total_steps, summary }
```

**Status Values:**
- `pending` - Agent being created
- `running` - Agent running
- `completed` - Agent finished successfully
- `failed` - Agent failed
- `cancelled` - Agent cancelled

---

## 🛑 **STOP AGENT**

```typescript
await agentMonitor.stopAgent(runId);
```

---

## 📝 **CHECKPOINT**

```typescript
await agentMonitor.checkpoint(runId, 'Create checkpoint');
```

---

## 🔧 **CONFIGURATION**

**VS Code Settings:**
```json
{
  "aimos.cursorApiKey": "your-api-key",
  "aimos.cursorApiUrl": "https://api.cursor.com/v0",
  "aimos.webhookUrl": "http://localhost:5001/webhook/agent-event"
}
```

**Secure Storage:**
```typescript
await context.secrets.store('cursorApiKey', 'your-api-key');
const apiKey = await context.secrets.get('cursorApiKey');
```

---

## 🔌 **COMMAND SERVER ENDPOINTS**

**Start Agent:**
```bash
POST http://localhost:5001/agent/start
{
  "taskFile": "task.yaml",
  "repoPath": "https://github.com/user/repo",
  "branch": "main"
}
```

**Stop Agent:**
```bash
POST http://localhost:5001/agent/stop
{
  "runId": "agent-123"
}
```

**Get Status:**
```bash
GET http://localhost:5001/agent/status/agent-123
```

---

## 🔧 **MCP TOOLS**

**Start Agent:**
```bash
POST http://localhost:5001/mcp/execute
{
  "tool": "agent.start",
  "arguments": {
    "taskFile": "task.yaml",
    "repoPath": "https://github.com/user/repo",
    "branch": "main"
  }
}
```

**Stop Agent:**
```bash
POST http://localhost:5001/mcp/execute
{
  "tool": "agent.stop",
  "arguments": {
    "runId": "agent-123"
  }
}
```

---

## ⚠️ **COMMON ERRORS**

**"API key not configured"**
- Fix: Configure `aimos.cursorApiKey` in settings

**"Cloud API requires GitHub repository URL"**
- Fix: Use `startAgentSmart()` or provide GitHub URL

**"Agent not found"**
- Fix: Verify run ID, check if agent was deleted

---

## 📚 **SEE ALSO**

- **T0:** Executive Summary
- **T1:** Overview
- **T2:** Architecture
- **T3:** Detailed Implementation
- **T4:** Complete Reference

---

**Status:** Production Ready ✅  
**Version:** v1.0.0  
**Last Updated:** 2025-11-04  
**Author:** Aether

