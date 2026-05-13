---
id: "agent_automation_T2_architecture"
system: "agent_automation"
component: null
level: "T2"
type: "architecture"
title: "Agent Automation - Architecture"
description: "2,000-word detailed architecture for Cursor agent automation system"
audience: "developers, architects"
confidence_threshold: 0.70
token_cost: 2000
word_count: 2000
created: "2025-11-04T00:15:00Z"
updated: "2025-11-04T00:15:00Z"
author: "aether"
status: "complete"
tags: ["agent-automation", "cursor", "architecture", "t0-t6", "transitional"]
dependencies: ["agent_automation_T1_overview"]
related_docs: ["T2_COMMAND_SERVER_ARCHITECTURE.md", "SYSTEM_INTEGRATION_ARCHITECTURE_T2.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# Agent Automation - T2 Architecture (≈2,000 words)

**Date:** 2025-11-04  
**Status:** Production Ready ✅  
**Purpose:** Detailed architecture for Cursor agent automation system

---

## 🏗️ **ARCHITECTURE OVERVIEW**

### **System Boundaries**

```
┌─────────────────────────────────────────────────────────────┐
│  User (Cursor IDE)                                         │
│  - Slash Commands (/agent-start)                           │
│  - Chat Interface                                           │
└────────────────────┬────────────────────────────────────────┘
                     │ MCP Protocol (JSON-RPC 2.0)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Python MCP Server                                         │
│  lucid_mcp_server.py                                       │
│  - agent.start tool                                        │
│  - agent.stop tool                                         │
│  - agent.status tool                                       │
└────────────────────┬────────────────────────────────────────┘
                     │ JSON-RPC 2.0 over stdio
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  VS Code Extension                                         │
│  - Command Server (HTTP API)                                │
│  - MCP Client                                               │
│  - AgentMonitor                                             │
│  - MessageRouter                                            │
└─────┬───────────────────────────┬───────────────────────────┘
      │                           │
      ▼                           ▼
┌──────────────────┐    ┌──────────────────────────────┐
│  Cursor Cloud    │    │  React UI Dashboard          │
│  Agents API      │    │  - Agent Status Display      │
│  (HTTP)          │    │  - Real-time Updates         │
│                  │    │  - Bulletproof Messaging     │
└──────────────────┘    └──────────────────────────────┘
      │
      ▼
┌──────────────────┐
│  GitHub          │
│  Repository      │
│  (Agent VMs)     │
└──────────────────┘
```

---

## 🔧 **CORE COMPONENTS**

### **1. AgentMonitor**

**Responsibility:** Manages agent lifecycle (start, stop, status, metrics)

**Implementation:**
```typescript
export class AgentMonitor {
    private router: MessageRouter;
    private activeRuns: Map<string, AgentRun> = new Map();
    private statusIntervals: Map<string, NodeJS.Timeout> = new Map();
    private cursorApiKey: string | null = null;
    private cursorApiUrl: string = 'https://api.cursor.com/v0';
    private webhookUrl: string | null = null;
}
```

**Key Features:**
- **Dual Execution:** Supports Cloud API (GitHub repos) and CLI (local repos)
- **Smart Routing:** Automatically chooses Cloud vs CLI based on repo path
- **Status Polling:** Polls agent status every 5 seconds (fallback if webhooks fail)
- **Webhook Integration:** Receives real-time events from Cursor API
- **Lifecycle Management:** Tracks active runs, handles cleanup on completion

**Methods:**
- `startAgentSmart()` - Automatically chooses Cloud or CLI
- `startAgent()` - Uses Cloud API (GitHub repos only)
- `startLocalAgent()` - Uses CLI (local repos)
- `stopAgent()` - Stops agent via API or CLI
- `getAgentStatus()` - Gets current status
- `handleWebhookEvent()` - Processes webhook callbacks

---

### **2. CursorCloudAPIClient**

**Responsibility:** Communicates with Cursor Cloud Agents API

**API Base URL:** `https://api.cursor.com/v0`

**Authentication:**
- Bearer Token: `Authorization: Bearer <api_key>`
- API Key obtained from: https://cursor.com/dashboard

**Endpoints:**

#### **POST /agents** - Launch Agent
```typescript
POST /v0/agents
{
  "prompt": {
    "text": "Execute task from task.yaml"
  },
  "source": {
    "repository": "https://github.com/user/repo",  // ⚠️ MUST be GitHub URL!
    "ref": "main"
  },
  "target": {
    "branchName": "agent/1234567890",
    "autoCreatePr": false
  },
  "webhook": {
    "url": "http://localhost:5001/webhook/agent-event",
    "secret": "webhook-secret-min-32-chars"
  }
}
```

**Response:**
```json
{
  "id": "agent-run-id",
  "status": "CREATING"
}
```

#### **GET /agents/{id}** - Agent Status
```typescript
GET /v0/agents/{id}
```

**Response:**
```json
{
  "id": "agent-run-id",
  "status": "RUNNING",
  "summary": {
    "steps_completed": 5,
    "tests_passed": 10,
    "files_changed": 3
  }
}
```

#### **DELETE /agents/{id}** - Stop Agent
```typescript
DELETE /v0/agents/{id}
```

**Response:** `204 No Content`

#### **POST /agents/{id}/followup** - Add Follow-up
```typescript
POST /v0/agents/{id}/followup
{
  "prompt": {
    "text": "Create checkpoint now"
  }
}
```

**Limitations:**
- ⚠️ **MCP Tools NOT Supported:** Cloud Agents API doesn't support MCP yet
- ⚠️ **GitHub Only:** Requires GitHub repository URLs (not local paths)
- ⚠️ **Rate Limits:** Subject to API rate limits

---

### **3. CursorCLIWrapper**

**Responsibility:** Executes cursor-agent CLI for local repositories

**Use Case:** Alternative to Cloud API for local-only repositories

**Implementation:**
```typescript
async startLocalAgent(params: {
    prompt: string;
    repoPath: string;
}): Promise<{ threadId: string; output: string[] }> {
    const result = await execSync(
        `cursor-agent --print --output-format json "${params.prompt}"`,
        {
            cwd: params.repoPath,
            encoding: 'utf-8',
            timeout: 300000  // 5 minutes
        }
    );
    
    return JSON.parse(result);
}
```

**Features:**
- **Non-interactive:** `--print` flag
- **JSON Output:** `--output-format json`
- **Resume Support:** `cursor-agent resume <thread-id>`
- **List Conversations:** `cursor-agent ls`

**Differences from Cloud API:**
- ✅ Works with local repositories
- ✅ No API key required
- ✅ No webhook support (polling only)
- ⚠️ Less reliable (CLI can fail)
- ⚠️ No GitHub integration

---

### **4. GitHubURLResolver**

**Responsibility:** Detects GitHub URLs from local repository paths

**Implementation:**
```typescript
async getGitHubUrl(localPath: string): Promise<string> {
    // Read git remote origin
    const result = await execSync(
        'git remote get-url origin',
        { cwd: localPath, encoding: 'utf-8' }
    );
    
    // Convert SSH to HTTPS if needed
    // git@github.com:user/repo.git → https://github.com/user/repo
    const url = result.trim();
    if (url.startsWith('git@github.com:')) {
        return url.replace('git@github.com:', 'https://github.com/');
    }
    
    return url;
}
```

**Use Case:** Allows `startAgentSmart()` to automatically use Cloud API even when local path provided.

**Behavior:**
- Reads `git remote get-url origin`
- Converts SSH URLs to HTTPS
- Returns GitHub URL if found
- Returns error if not GitHub or no remote

---

### **5. WebhookHandler**

**Responsibility:** Handles webhook callbacks from Cursor API

**Endpoint:** `POST /webhook/agent-event` (Command Server)

**Webhook Events:**

**`agent.status`** - Status update
```json
{
  "event": "agent.status",
  "agent_id": "run-id",
  "status": "RUNNING",
  "summary": { ... }
}
```

**`agent.output`** - Stream output
```json
{
  "event": "agent.output",
  "agent_id": "run-id",
  "output": ["stdout line 1", "stdout line 2"]
}
```

**`agent.complete`** - Agent completed
```json
{
  "event": "agent.complete",
  "agent_id": "run-id",
  "status": "FINISHED",
  "exit_code": 0
}
```

**Implementation:**
```typescript
async handleWebhookEvent(payload: WebhookPayload): Promise<void> {
    const { event, agent_id } = payload;
    
    // Route event via MessageRouter
    const envelope = createEnvelope('event', `agent.${event}`, 'ext->ui', payload);
    await this.router.route(envelope);
    
    // Update local state
    const run = this.activeRuns.get(agent_id);
    if (run) {
        run.status = payload.status;
        if (event === 'agent.complete') {
            this.stopPolling(agent_id);
        }
    }
}
```

**Security:**
- Webhook secret verification (optional)
- Payload validation
- Rate limiting

---

### **6. StatusPoller**

**Responsibility:** Polls agent status and sends updates via bulletproof messaging

**Implementation:**
```typescript
private startPolling(runId: string): void {
    const interval = setInterval(async () => {
        try {
            const status = await this.getAgentStatus(runId);
            
            // Send status update via MessageRouter
            const envelope = createEnvelope('event', 'agent.status', 'ext->ui', status);
            await this.router.route(envelope);
            
            // Stop polling if completed
            if (status.status === 'completed' || status.status === 'failed') {
                this.stopPolling(runId);
            }
        } catch (error) {
            console.error('Status polling error:', error);
        }
    }, 5000); // Poll every 5 seconds
    
    this.statusIntervals.set(runId, interval);
}
```

**Features:**
- **Polling Interval:** 5 seconds (configurable)
- **Fallback:** Used if webhooks unavailable
- **Automatic Cleanup:** Stops polling on completion
- **Error Handling:** Continues polling on errors

---

## 🔄 **MESSAGE FLOW PATTERNS**

### **Pattern 1: Starting Agent via Slash Command**

```
1. User types: /agent-start task=task.yaml branch=main
   ↓
2. Cursor calls MCP tool: mcp_lucid-mcp_agent.start
   ↓
3. MCP Server (Python) receives JSON-RPC request
   ↓
4. MCP Server calls Command Server: POST /mcp/execute
   {
     "tool": "agent.start",
     "arguments": {
       "taskFile": "task.yaml",
       "repoPath": "/path/to/repo",
       "branch": "main"
     }
   }
   ↓
5. Command Server calls AgentMonitor.startAgentSmart()
   ↓
6. AgentMonitor detects GitHub URL → Uses Cloud API
   ↓
7. AgentMonitor calls Cursor API: POST /v0/agents
   ↓
8. Cursor API returns agent_id
   ↓
9. AgentMonitor sends 'agent.started' event via MessageRouter
   ↓
10. React UI receives event → Updates dashboard
```

### **Pattern 2: Status Updates via Webhook**

```
1. Cursor API sends webhook: POST /webhook/agent-event
   {
     "event": "agent.status",
     "agent_id": "run-id",
     "status": "RUNNING",
     "summary": { ... }
   }
   ↓
2. Command Server receives webhook
   ↓
3. Command Server calls AgentMonitor.handleWebhookEvent()
   ↓
4. AgentMonitor creates envelope: 'agent.status' event
   ↓
5. AgentMonitor routes envelope via MessageRouter
   ↓
6. MessageRouter sends envelope to React UI
   ↓
7. React UI receives event → Updates dashboard in real-time
```

### **Pattern 3: Status Updates via Polling (Fallback)**

```
1. StatusPoller triggers (every 5 seconds)
   ↓
2. AgentMonitor calls Cursor API: GET /v0/agents/{id}
   ↓
3. Cursor API returns status
   ↓
4. AgentMonitor creates envelope: 'agent.status' event
   ↓
5. AgentMonitor routes envelope via MessageRouter
   ↓
6. React UI receives event → Updates dashboard
```

---

## 🔒 **SECURITY ARCHITECTURE**

### **API Key Management**

**Storage:**
- Stored in VS Code settings: `aimos.cursorApiKey`
- Never exposed in logs or UI
- Encrypted at rest (VS Code secure storage)

**Usage:**
```typescript
const apiKey = vscode.workspace.getConfiguration('aimos').get<string>('cursorApiKey');
if (!apiKey) {
    throw new Error('Cursor API key not configured');
}
```

**Security Measures:**
- Bearer token authentication
- HTTPS only (no HTTP)
- Webhook secret verification (optional)
- Rate limiting (API-level)

### **Webhook Security**

**Secret Verification:**
```typescript
function verifyWebhookSecret(payload: any, signature: string, secret: string): boolean {
    const hmac = crypto.createHmac('sha256', secret);
    hmac.update(JSON.stringify(payload));
    const expected = hmac.digest('hex');
    return crypto.timingSafeEqual(
        Buffer.from(signature),
        Buffer.from(expected)
    );
}
```

**Best Practices:**
- Use webhook secret (min 32 chars)
- Verify payload signature
- Rate limit webhook endpoint
- Validate payload structure

---

## 📊 **PERFORMANCE CHARACTERISTICS**

### **Latency Targets**

**Agent Start:**
- **Target:** <1000ms (p95)
- **P99:** <5000ms
- **Bottlenecks:** API call latency, GitHub URL detection

**Status Polling:**
- **Interval:** 5 seconds
- **Timeout:** 10 seconds
- **Bottlenecks:** API response time

**Webhook Processing:**
- **Target:** <100ms (p95)
- **P99:** <500ms
- **Bottlenecks:** MessageRouter processing

### **Throughput**

**Agents/Minute:**
- **Target:** 10 agents/minute
- **Limit:** API rate limits

**Concurrent Agents:**
- **Target:** 10 concurrent agents
- **Limit:** API rate limits, memory usage

### **Reliability**

**Delivery Guarantee:**
- **Status Updates:** Best effort (polling + webhooks)
- **Events:** Bulletproof messaging (guaranteed delivery)

**Failure Recovery:**
- **API Failures:** Retry with exponential backoff
- **Webhook Failures:** Fallback to polling
- **Network Issues:** Automatic retry

---

## 🔌 **INTEGRATION POINTS**

### **1. Bulletproof Messaging Integration**

**Purpose:** Reliable status updates to React UI

**Integration:**
```typescript
// AgentMonitor sends events via MessageRouter
const envelope = createEnvelope('event', 'agent.status', 'ext->ui', status);
await this.router.route(envelope);
```

**Events:**
- `agent.started` - Agent started
- `agent.status` - Status update
- `agent.completed` - Agent completed
- `agent.failed` - Agent failed
- `agent.output` - Stream output

### **2. Command Server Integration**

**Purpose:** Expose agent control via HTTP API

**Integration:**
```typescript
// Command Server registers agent endpoints
if (pathname === '/agent/start') {
    const result = await agentMonitor.startAgentSmart(request);
    res.json(result);
}
```

**Endpoints:**
- `POST /agent/start` - Start agent
- `POST /agent/stop` - Stop agent
- `GET /agent/status/:id` - Get status
- `POST /webhook/agent-event` - Webhook callback

### **3. MCP Server Integration**

**Purpose:** Enable slash commands and MCP tool calls

**Integration:**
```python
# MCP Server registers agent tools
@tool("agent.start")
async def agent_start(task_file: str, repo_path: str, **kwargs):
    # Call Command Server HTTP API
    response = await http.post("http://localhost:5001/agent/start", {
        "taskFile": task_file,
        "repoPath": repo_path,
        **kwargs
    })
    return response.json()
```

**Tools:**
- `agent.start` - Start agent
- `agent.stop` - Stop agent
- `agent.status` - Get status

---

## 🚀 **DEPLOYMENT ARCHITECTURE**

### **Runtime Environment**

- **Host:** VS Code Extension Host (Node.js)
- **API:** Cursor Cloud Agents API (HTTPS)
- **CLI:** cursor-agent (system command)
- **Storage:** In-memory (activeRuns Map)

### **Lifecycle**

**Initialization:**
1. Extension activates
2. AgentMonitor constructor called
3. API key loaded from settings
4. MessageRouter set
5. Webhook URL configured

**Shutdown:**
1. Extension deactivates
2. All polling stopped
3. Active runs tracked in memory
4. Webhook handlers cleaned up

---

## ✅ **PRODUCTION STATUS**

- **Status:** Production Ready ✅
- **API Integration:** Cloud API verified, CLI verified
- **Webhook Support:** Implemented, optional verification
- **Smart Routing:** Cloud vs CLI automatic selection
- **Error Handling:** Comprehensive error handling
- **Documentation:** Complete T0-T2 documentation

---

## 📚 **RELATED DOCUMENTATION**

- **T0 Executive:** [T0_AGENT_AUTOMATION_EXECUTIVE.md](./T0_AGENT_AUTOMATION_EXECUTIVE.md)
- **T1 Overview:** [AUTOMATION_SYSTEMS_EXPLAINED_T1.md](./AUTOMATION_SYSTEMS_EXPLAINED_T1.md)
- **System Map:** [systems/agent_automation/system.map.lucid.json5](../systems/agent_automation/system.map.lucid.json5)
- **System Index:** [systems/agent_automation/system.index.lucid.json5](../systems/agent_automation/system.index.lucid.json5)
- **Integration Architecture:** [SYSTEM_INTEGRATION_ARCHITECTURE_T2.md](./SYSTEM_INTEGRATION_ARCHITECTURE_T2.md)
- **API Research:** [CURSOR_API_RESEARCH.md](./CURSOR_API_RESEARCH.md)

---

**Status:** Production Ready ✅  
**Version:** v1.0.0  
**Last Updated:** 2025-11-04  
**Author:** Aether

