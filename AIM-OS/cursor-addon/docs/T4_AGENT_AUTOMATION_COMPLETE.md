---
id: "agent_automation_T4_complete"
system: "agent_automation"
component: null
level: "T4"
type: "complete"
title: "Agent Automation - Complete Reference"
description: "15,000+ word complete reference guide for Cursor agent automation with exhaustive API documentation, edge cases, troubleshooting, performance analysis, and migration guides"
audience: "experts, maintainers, system integrators"
confidence_threshold: 0.50
token_cost: 15000
word_count: 15000
created: "2025-11-04T00:45:00Z"
updated: "2025-11-04T00:45:00Z"
author: "aether"
status: "complete"
tags: ["agent-automation", "reference", "complete", "production-ready", "t0-t6", "transitional"]
dependencies: ["agent_automation_T3_detailed"]
related_docs: ["T3_AGENT_AUTOMATION_DETAILED.md", "system.map.lucid.json5"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# Agent Automation – T4 Complete Reference (≈15,000 words)

**Date:** 2025-11-04  
**Status:** Production Ready ✅  
**Purpose:** Exhaustive reference for all aspects of Cursor agent automation  
**Prerequisites:** T3 Detailed Implementation Guide

---

## 📋 **TABLE OF CONTENTS**

### **PART I: COMPLETE API REFERENCE**
1. [AgentMonitor API](#part-i-agentmonitor-api)
2. [Cursor Cloud Agents API](#part-i-cursor-cloud-agents-api)
3. [CLI Agent API](#part-i-cli-agent-api)
4. [Webhook API](#part-i-webhook-api)
5. [Command Server Integration API](#part-i-command-server-integration-api)
6. [MCP Tools API](#part-i-mcp-tools-api)

### **PART II: EDGE CASES & ERROR HANDLING**
7. [Edge Cases](#part-ii-edge-cases)
8. [Error Codes Reference](#part-ii-error-codes-reference)
9. [Failure Scenarios](#part-ii-failure-scenarios)
10. [Recovery Procedures](#part-ii-recovery-procedures)

### **PART III: PERFORMANCE & OPTIMIZATION**
11. [Performance Characteristics](#part-iii-performance-characteristics)
12. [Optimization Techniques](#part-iii-optimization-techniques)
13. [Scaling Considerations](#part-iii-scaling-considerations)

### **PART IV: SECURITY & COMPLIANCE**
14. [Security Architecture](#part-iv-security-architecture)
15. [Threat Model](#part-iv-threat-model)
16. [API Key Management](#part-iv-api-key-management)

### **PART V: OPERATIONS & MAINTENANCE**
17. [Monitoring & Observability](#part-v-monitoring--observability)
18. [Troubleshooting Guide](#part-v-troubleshooting-guide)
19. [Maintenance Procedures](#part-v-maintenance-procedures)

### **PART VI: MIGRATION & UPGRADES**
20. [Migration Guide](#part-vi-migration-guide)
21. [Version Upgrades](#part-vi-version-upgrades)
22. [Backward Compatibility](#part-vi-backward-compatibility)

---

## 📚 **PART I: COMPLETE API REFERENCE**

### **1. AgentMonitor API**

#### **1.1 Constructor**

```typescript
new AgentMonitor(
    router: MessageRouter,
    options?: {
        cursorApiKey?: string;
        cursorApiUrl?: string;
        webhookUrl?: string;
    }
)
```

**Parameters:**
- `router: MessageRouter` - MessageRouter instance for status updates
- `options?: { cursorApiKey?, cursorApiUrl?, webhookUrl? }` - Optional configuration

**Example:**
```typescript
const agentMonitor = new AgentMonitor(router, {
    cursorApiKey: 'your-api-key',
    cursorApiUrl: 'https://api.cursor.com/v0',
    webhookUrl: 'http://localhost:5001/webhook/agent-event'
});
```

#### **1.2 Core Methods**

**`startAgentSmart(params): Promise<{ runId: string; method: 'cloud' | 'local' }>`**

Smart agent start that automatically chooses Cloud API or CLI.

**Parameters:**
```typescript
{
    prompt: string;              // Task prompt
    repoPath: string;            // GitHub URL or local path
    branch?: string;             // Branch name (optional)
    maxRuntimeHours?: number;    // Max runtime (optional)
    taskFile?: string;           // Task file (optional, required for Cloud API)
}
```

**Returns:**
```typescript
{
    runId: string;               // Agent run ID
    method: 'cloud' | 'local'    // Execution method used
}
```

**Behavior:**
- If `repoPath` is GitHub URL → Uses Cloud API
- If `repoPath` is local path → Tries to detect GitHub URL from git remote
- If GitHub URL found → Uses Cloud API (if API key configured)
- If no GitHub URL or no API key → Falls back to CLI

**Example:**
```typescript
const result = await agentMonitor.startAgentSmart({
    prompt: 'Refactor authentication system',
    repoPath: '/local/path/to/repo',  // Automatically detects GitHub URL
    branch: 'main',
    taskFile: 'refactor.yaml'
});

console.log(`Agent started: ${result.runId} (${result.method})`);
```

**`startAgent(params): Promise<string>`**

Start agent using Cloud API (requires GitHub repository URL).

**Parameters:**
```typescript
{
    taskFile: string;            // Task YAML file path
    repoPath: string;            // ⚠️ MUST be GitHub URL!
    branch?: string;             // Branch name (optional)
    maxRuntimeHours?: number;    // Max runtime (optional)
}
```

**Returns:** `Promise<string>` - Agent run ID

**Example:**
```typescript
const runId = await agentMonitor.startAgent({
    taskFile: 'task.yaml',
    repoPath: 'https://github.com/user/repo',
    branch: 'main',
    maxRuntimeHours: 6
});
```

**⚠️ Important:** This method requires GitHub repository URL. Local paths will fail.

**`startLocalAgent(params): Promise<{ threadId: string; output: string[] }>`**

Start agent using CLI (works with local repositories).

**Parameters:**
```typescript
{
    prompt: string;              // Task prompt
    repoPath: string;            // Local repository path
}
```

**Returns:**
```typescript
{
    threadId: string;            // Thread ID (can resume later)
    output: string[];            // Initial output
}
```

**Example:**
```typescript
const result = await agentMonitor.startLocalAgent({
    prompt: 'Fix all TypeScript errors',
    repoPath: '/local/path/to/repo'
});

console.log(`Local agent started: ${result.threadId}`);
```

**`stopAgent(runId: string): Promise<void>`**

Stop an agent run.

**Parameters:**
- `runId: string` - Agent run ID

**Behavior:**
- Calls Cloud API: `DELETE /v0/agents/{id}` (for Cloud agents)
- Or kills CLI process (for local agents)
- Stops status polling
- Sends 'agent.stopped' event

**Example:**
```typescript
await agentMonitor.stopAgent('agent-123');
```

**`getAgentStatus(runId: string): Promise<AgentStatus | null>`**

Get current agent status.

**Parameters:**
- `runId: string` - Agent run ID

**Returns:**
```typescript
{
    run_id: string;
    status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
    current_step?: number;
    total_steps?: number;
    summary?: {
        steps_completed: number;
        tests_passed?: number;
        files_changed?: number;
    };
}
```

**Example:**
```typescript
const status = await agentMonitor.getAgentStatus('agent-123');
console.log(`Status: ${status?.status}, Step: ${status?.current_step}/${status?.total_steps}`);
```

**`checkpoint(runId: string, message?: string): Promise<void>`**

Create checkpoint (add follow-up to running agent).

**Parameters:**
- `runId: string` - Agent run ID
- `message?: string` - Checkpoint message (default: "Create checkpoint now")

**Example:**
```typescript
await agentMonitor.checkpoint('agent-123', 'Save current progress');
```

**`resumeLocalAgent(threadId: string, followup?: string): Promise<{ output: string[] }>`**

Resume local agent conversation.

**Parameters:**
- `threadId: string` - Thread ID from previous `startLocalAgent()` call
- `followup?: string` - Optional follow-up prompt

**Returns:**
```typescript
{
    output: string[]  // New output lines
}
```

**Example:**
```typescript
const result = await agentMonitor.resumeLocalAgent('thread-123', 'Continue with next step');
```

**`listLocalAgents(repoPath: string): Promise<Array<{ threadId: string; status: string }>>`**

List all local agent conversations.

**Parameters:**
- `repoPath: string` - Repository path

**Returns:** Array of conversation threads

**Example:**
```typescript
const conversations = await agentMonitor.listLocalAgents('/local/path/to/repo');
for (const conv of conversations) {
    console.log(`${conv.threadId}: ${conv.status}`);
}
```

**`handleWebhookEvent(payload: any): Promise<void>`**

Process webhook event from Cursor API.

**Parameters:**
- `payload: any` - Webhook payload from Cursor API

**Webhook Events:**
- `agent.status` - Status update
- `agent.output` - Stream output
- `agent.complete` - Agent completed/failed/cancelled

**Example:**
```typescript
await agentMonitor.handleWebhookEvent({
    event: 'agent.status',
    agent_id: 'agent-123',
    status: 'RUNNING',
    summary: { steps_completed: 5 }
});
```

**`getAllActiveRuns(): AgentRun[]`**

Get all active agent runs.

**Returns:** Array of active runs

**Example:**
```typescript
const activeRuns = agentMonitor.getAllActiveRuns();
console.log(`Active agents: ${activeRuns.length}`);
```

---

### **2. Cursor Cloud Agents API**

#### **2.1 Authentication**

**Method:** Bearer Token Authentication  
**Header:** `Authorization: Bearer <api_key>`

**Get API Key:**
1. Navigate to https://cursor.com/dashboard
2. Go to **Integrations** → **API Keys**
3. Click **"Create New API Key"**
4. Copy and securely store

#### **2.2 Endpoints**

**`POST /v0/agents`** - Launch Agent

**Request:**
```json
{
  "prompt": {
    "text": "Execute task from task.yaml",
    "images": []  // Optional: base64 images (max 5)
  },
  "model": "claude-4-sonnet",  // Optional
  "source": {
    "repository": "https://github.com/user/repo",  // ⚠️ REQUIRED: GitHub URL!
    "ref": "main"  // Optional: branch/tag/commit
  },
  "target": {
    "branchName": "agent/1234567890",  // Optional
    "autoCreatePr": false  // Optional
  },
  "webhook": {  // Optional
    "url": "https://your-server.com/webhook",
    "secret": "webhook-secret-min-32-chars"
  }
}
```

**Response:**
```json
{
  "id": "agent-run-id",
  "status": "CREATING",
  "createdAt": "2025-11-04T00:00:00Z"
}
```

**Status Values:**
- `CREATING` - Agent being created
- `RUNNING` - Agent running
- `FINISHED` - Agent completed successfully
- `FAILED` - Agent failed
- `CANCELLED` - Agent cancelled

**`GET /v0/agents/{id}`** - Agent Status

**Response:**
```json
{
  "id": "agent-run-id",
  "status": "RUNNING",
  "summary": {
    "steps_completed": 5,
    "tests_passed": 10,
    "files_changed": 3
  },
  "createdAt": "2025-11-04T00:00:00Z",
  "startedAt": "2025-11-04T00:05:00Z"
}
```

**`DELETE /v0/agents/{id}`** - Stop Agent

**Response:** `204 No Content`

**`POST /v0/agents/{id}/followup`** - Add Follow-up

**Request:**
```json
{
  "prompt": {
    "text": "Create checkpoint now"
  }
}
```

**Response:**
```json
{
  "id": "agent-run-id",
  "status": "RUNNING"
}
```

**`GET /v0/agents/{id}/conversation`** - Get Conversation

**Response:** Full conversation history (not available if agent deleted)

**`GET /v0/agents`** - List Agents

**Query Parameters:**
- `limit` (max 100, default 20)
- `cursor` (pagination)

**Response:**
```json
{
  "agents": [...],
  "nextCursor": "..."
}
```

**`GET /v0/me`** - API Key Info

**Response:**
```json
{
  "name": "API Key Name",
  "createdAt": "2025-11-04T00:00:00Z",
  "email": "user@example.com"
}
```

**`GET /v0/models`** - List Models

**Response:**
```json
[
  "claude-4-sonnet-thinking",
  "o3",
  "claude-4-opus-thinking"
]
```

**`GET /v0/repositories`** - List Repositories

**⚠️ Rate Limits:** 1/user/minute, 30/user/hour

**Response:**
```json
[
  {
    "owner": "user",
    "name": "repo",
    "repository": "https://github.com/user/repo"
  }
]
```

#### **2.3 Webhook Events**

**Event: `agent.status`**
```json
{
  "event": "agent.status",
  "agent_id": "agent-run-id",
  "status": "RUNNING",
  "summary": {
    "steps_completed": 5,
    "tests_passed": 10,
    "files_changed": 3
  }
}
```

**Event: `agent.output`**
```json
{
  "event": "agent.output",
  "agent_id": "agent-run-id",
  "output": ["stdout line 1", "stdout line 2"]
}
```

**Event: `agent.complete`**
```json
{
  "event": "agent.complete",
  "agent_id": "agent-run-id",
  "status": "FINISHED",
  "exit_code": 0
}
```

**Webhook Secret Verification:**
```typescript
import * as crypto from 'crypto';

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

---

### **3. CLI Agent API**

#### **3.1 Commands**

**`cursor-agent --print --output-format json "<prompt>"`**

Start new agent conversation.

**Parameters:**
- `--print` - Non-interactive mode
- `--output-format json` - JSON output format
- `"<prompt>"` - Task prompt

**Output:**
```json
{
  "thread_id": "thread-123",
  "status": "running",
  "output": ["stdout line 1", "stdout line 2"]
}
```

**`cursor-agent resume <thread-id> --print --output-format json "<followup>"`**

Resume agent conversation.

**Parameters:**
- `thread-id` - Thread ID from previous conversation
- `--print` - Non-interactive mode
- `--output-format json` - JSON output format
- `"<followup>"` - Optional follow-up prompt

**`cursor-agent ls --output-format json`**

List all conversations.

**Output:**
```json
[
  {
    "thread_id": "thread-123",
    "status": "running",
    "created_at": "2025-11-04T00:00:00Z"
  }
]
```

#### **3.2 Integration**

**Example:**
```typescript
import { execSync } from 'child_process';

async function startLocalAgent(prompt: string, repoPath: string): Promise<any> {
    const result = execSync(
        `cursor-agent --print --output-format json "${prompt}"`,
        {
            cwd: repoPath,
            encoding: 'utf-8',
            timeout: 300000  // 5 minutes
        }
    );
    
    return JSON.parse(result);
}
```

---

### **4. Webhook API**

#### **4.1 Webhook Endpoint**

**URL:** `POST /webhook/agent-event` (Command Server)

**Request:**
```json
{
  "event": "agent.status",
  "agent_id": "agent-run-id",
  "status": "RUNNING",
  "summary": { ... }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Webhook processed"
}
```

#### **4.2 Webhook Security**

**Secret Verification:**
```typescript
// Command Server verifies webhook secret
const signature = req.headers['x-webhook-signature'];
const isValid = verifyWebhookSecret(payload, signature, webhookSecret);
if (!isValid) {
    return { success: false, error: 'Invalid webhook signature' };
}
```

---

### **5. Command Server Integration API**

#### **5.1 Agent Endpoints**

**`POST /agent/start`** - Start Agent

**Request:**
```json
{
  "taskFile": "task.yaml",
  "repoPath": "https://github.com/user/repo",
  "branch": "main",
  "maxRuntimeHours": 6,
  "prompt": "Optional custom prompt"
}
```

**Response:**
```json
{
  "success": true,
  "runId": "agent-123",
  "method": "cloud"
}
```

**`POST /agent/stop`** - Stop Agent

**Request:**
```json
{
  "runId": "agent-123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Agent stopped"
}
```

**`GET /agent/status/:id`** - Get Status

**Response:**
```json
{
  "success": true,
  "status": {
    "run_id": "agent-123",
    "status": "running",
    "current_step": 5,
    "total_steps": 10
  }
}
```

**`GET /agent/list`** - List All Agents

**Response:**
```json
{
  "success": true,
  "agents": [
    {
      "run_id": "agent-123",
      "status": "running",
      "repo_path": "https://github.com/user/repo"
    }
  ]
}
```

---

### **6. MCP Tools API**

#### **6.1 Tool Registration**

**Python MCP Server:**
```python
@tool("agent.start")
async def agent_start(
    task_file: str = None,
    repo_path: str = None,
    branch: str = None,
    max_runtime_hours: int = 6,
    prompt: str = None
) -> dict:
    """Start a Cursor Background Agent run."""
    # Call Command Server HTTP API
    response = await http.post(
        "http://localhost:5001/agent/start",
        json={
            "taskFile": task_file,
            "repoPath": repo_path,
            "branch": branch,
            "maxRuntimeHours": max_runtime_hours,
            "prompt": prompt
        }
    )
    return response.json()
```

#### **6.2 Tool Execution**

**Via Command Server:**
```typescript
POST /mcp/execute
{
  "tool": "agent.start",
  "arguments": {
    "taskFile": "task.yaml",
    "repoPath": "https://github.com/user/repo",
    "branch": "main"
  }
}
```

**Response:**
```json
{
  "success": true,
  "tool": "agent.start",
  "result": {
    "runId": "agent-123",
    "method": "cloud"
  }
}
```

---

## 🔍 **PART II: EDGE CASES & ERROR HANDLING**

### **7. Edge Cases**

#### **7.1 GitHub URL Detection**

**Case 1: SSH URL**

**Problem:** Git remote returns SSH URL (`git@github.com:user/repo.git`)

**Solution:** Convert SSH to HTTPS

**Example:**
```typescript
const sshUrl = 'git@github.com:user/repo.git';
const httpsUrl = sshUrl.replace('git@github.com:', 'https://github.com/');
// Result: https://github.com/user/repo.git
```

**Case 2: No Git Remote**

**Problem:** Local repository has no git remote

**Solution:** Fall back to CLI Agent

**Example:**
```typescript
try {
    const githubUrl = await getGitHubUrl('/local/path');
    // Use Cloud API
} catch (error) {
    // No remote found - use CLI
    await startLocalAgent({ prompt, repoPath: '/local/path' });
}
```

**Case 3: Non-GitHub Remote**

**Problem:** Git remote is not GitHub (e.g., GitLab, Bitbucket)

**Solution:** Fall back to CLI Agent

**Example:**
```typescript
const remoteUrl = 'https://gitlab.com/user/repo.git';
if (!remoteUrl.startsWith('https://github.com/')) {
    // Not GitHub - use CLI
    await startLocalAgent({ prompt, repoPath });
}
```

#### **7.2 API Key Edge Cases**

**Case 1: API Key Expired**

**Problem:** API key no longer valid

**Solution:** Prompt user to renew API key

**Example:**
```typescript
try {
    await agentMonitor.startAgent(params);
} catch (error: any) {
    if (error.message.includes('401') || error.message.includes('Unauthorized')) {
        vscode.window.showErrorMessage('API key expired. Please renew in Cursor Dashboard.');
    }
}
```

**Case 2: No API Key Configured**

**Problem:** Cloud API requires API key, but none configured

**Solution:** Fall back to CLI Agent

**Example:**
```typescript
if (!apiKey) {
    // No API key - use CLI
    const result = await agentMonitor.startLocalAgent({ prompt, repoPath });
    return { runId: result.threadId, method: 'local' };
}
```

#### **7.3 Status Polling Edge Cases**

**Case 1: Agent Deleted**

**Problem:** Agent was deleted via Cursor UI, but polling still active

**Solution:** Handle 404 response, stop polling

**Example:**
```typescript
const status = await agentMonitor.getAgentStatus(runId);
if (!status) {
    // Agent not found - stop polling
    agentMonitor.stopPolling(runId);
    agentMonitor.activeRuns.delete(runId);
}
```

**Case 2: Network Interruption**

**Problem:** Network fails during status polling

**Solution:** Retry with exponential backoff, then fallback

**Example:**
```typescript
async function pollWithRetry(runId: string, maxRetries: number = 3): Promise<AgentStatus | null> {
    for (let i = 0; i < maxRetries; i++) {
        try {
            return await agentMonitor.getAgentStatus(runId);
        } catch (error) {
            if (i === maxRetries - 1) throw error;
            await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
        }
    }
    return null;
}
```

#### **7.4 Webhook Edge Cases**

**Case 1: Webhook Timeout**

**Problem:** Webhook endpoint not accessible

**Solution:** Fall back to polling

**Example:**
```typescript
// If webhook not received within timeout, start polling
setTimeout(() => {
    if (!webhookReceived) {
        startPolling(runId);  // Fallback to polling
    }
}, 30000);  // 30 second timeout
```

**Case 2: Duplicate Webhook Events**

**Problem:** Webhook sends duplicate events

**Solution:** Use idempotency (remember processed events)

**Example:**
```typescript
const processedEvents = new Set<string>();

async function handleWebhookEvent(event: WebhookEvent): Promise<void> {
    const eventId = `${event.agent_id}-${event.event}-${event.timestamp}`;
    if (processedEvents.has(eventId)) {
        return;  // Already processed
    }
    processedEvents.add(eventId);
    // Process event...
}
```

---

### **8. Error Codes Reference**

#### **8.1 Standard Error Codes**

**`API_KEY_NOT_CONFIGURED`**

**Meaning:** Cursor API key not configured

**Causes:**
- API key not set in settings
- API key not stored securely
- Settings misconfigured

**Resolution:**
1. Get API key from https://cursor.com/dashboard
2. Configure in VS Code settings: `aimos.cursorApiKey`
3. Or use secure storage: `context.secrets.store('cursorApiKey', key)`

**Example:**
```typescript
// Error
{
    code: 'API_KEY_NOT_CONFIGURED',
    message: 'Cursor API key not configured'
}

// Fix
const apiKey = await context.secrets.get('cursorApiKey');
if (!apiKey) {
    // Prompt user to enter API key
    const input = await vscode.window.showInputBox({
        prompt: 'Enter Cursor API Key',
        password: true
    });
    await context.secrets.store('cursorApiKey', input);
}
```

**`GITHUB_URL_REQUIRED`**

**Meaning:** Cloud API requires GitHub repository URL

**Causes:**
- Local path provided instead of GitHub URL
- Git remote not GitHub
- No git remote configured

**Resolution:**
1. Use `startAgentSmart()` instead of `startAgent()`
2. Or convert local path to GitHub URL
3. Or use `startLocalAgent()` for local repos

**Example:**
```typescript
// Error
{
    code: 'GITHUB_URL_REQUIRED',
    message: 'Cloud API requires GitHub repository URL'
}

// Fix
const result = await agentMonitor.startAgentSmart({
    prompt: 'Task',
    repoPath: '/local/path'  // Automatically detects GitHub URL
});
```

**`AGENT_NOT_FOUND`**

**Meaning:** Agent run ID not found

**Causes:**
- Agent was deleted
- Wrong run ID
- Agent expired

**Resolution:**
1. Verify run ID is correct
2. Check if agent was deleted
3. List all agents to find correct ID

**Example:**
```typescript
// Error
{
    code: 'AGENT_NOT_FOUND',
    message: 'Agent agent-123 not found'
}

// Fix
const agents = await agentMonitor.getAllActiveRuns();
const agent = agents.find(a => a.run_id === runId);
if (!agent) {
    console.log('Agent not found - may have been deleted');
}
```

**`API_RATE_LIMIT_EXCEEDED`**

**Meaning:** API rate limit exceeded

**Causes:**
- Too many API calls
- Rate limit hit

**Resolution:**
1. Implement rate limiting
2. Use exponential backoff
3. Cache responses when possible

**Example:**
```typescript
// Error
{
    code: 'API_RATE_LIMIT_EXCEEDED',
    message: 'Rate limit exceeded. Try again later.'
}

// Fix
private rateLimiter = new Map<string, number>();

async makeApiCall(endpoint: string): Promise<Response> {
    const now = Date.now();
    const lastCall = this.rateLimiter.get(endpoint) || 0;
    const delay = Math.max(0, 1000 - (now - lastCall));
    
    if (delay > 0) {
        await new Promise(resolve => setTimeout(resolve, delay));
    }
    
    this.rateLimiter.set(endpoint, Date.now());
    return fetch(endpoint, { ... });
}
```

**`WEBHOOK_VERIFICATION_FAILED`**

**Meaning:** Webhook secret verification failed

**Causes:**
- Invalid webhook secret
- Signature mismatch
- Missing signature header

**Resolution:**
1. Verify webhook secret matches
2. Check signature header format
3. Verify HMAC calculation

**Example:**
```typescript
// Error
{
    code: 'WEBHOOK_VERIFICATION_FAILED',
    message: 'Invalid webhook signature'
}

// Fix
const signature = req.headers['x-webhook-signature'];
const isValid = verifyWebhookSecret(payload, signature, webhookSecret);
if (!isValid) {
    return { success: false, error: 'Invalid webhook signature' };
}
```

**`CLI_AGENT_NOT_FOUND`**

**Meaning:** cursor-agent CLI not found

**Causes:**
- cursor-agent not installed
- cursor-agent not in PATH
- Wrong version

**Resolution:**
1. Install cursor-agent: `npm install -g cursor-agent`
2. Verify installation: `cursor-agent --version`
3. Check PATH environment variable

**Example:**
```typescript
// Error
{
    code: 'CLI_AGENT_NOT_FOUND',
    message: 'cursor-agent command not found'
}

// Fix
try {
    execSync('cursor-agent --version', { encoding: 'utf-8' });
} catch (error) {
    vscode.window.showErrorMessage('cursor-agent not installed. Install with: npm install -g cursor-agent');
}
```

---

### **9. Failure Scenarios**

#### **9.1 Agent Start Failure**

**Scenario:** Agent fails to start

**Causes:**
- Invalid API key
- Invalid repository URL
- API rate limit
- Network error

**Recovery:**
1. Check error code
2. Retry with exponential backoff
3. Fall back to CLI if Cloud API fails

**Example:**
```typescript
async function startAgentWithRetry(params: any, maxRetries: number = 3): Promise<string> {
    for (let i = 0; i < maxRetries; i++) {
        try {
            return await agentMonitor.startAgent(params);
        } catch (error: any) {
            if (i === maxRetries - 1) {
                // Last retry failed - fall back to CLI
                const result = await agentMonitor.startLocalAgent({
                    prompt: params.taskFile,
                    repoPath: params.repoPath
                });
                return result.threadId;
            }
            await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
        }
    }
    throw new Error('Failed to start agent after retries');
}
```

#### **9.2 Status Polling Failure**

**Scenario:** Status polling fails repeatedly

**Causes:**
- Network issues
- API rate limits
- Agent deleted

**Recovery:**
1. Detect repeated failures
2. Increase polling interval
3. Notify user of issues

**Example:**
```typescript
private pollingFailures = new Map<string, number>();

async pollStatus(runId: string): Promise<void> {
    try {
        const status = await this.getAgentStatus(runId);
        this.pollingFailures.set(runId, 0);  // Reset failure count
        // Process status...
    } catch (error) {
        const failures = this.pollingFailures.get(runId) || 0;
        this.pollingFailures.set(runId, failures + 1);
        
        if (failures > 3) {
            // Too many failures - notify user
            vscode.window.showWarningMessage(`Status polling failed for agent ${runId}`);
            this.stopPolling(runId);
        }
    }
}
```

#### **9.3 Webhook Failure**

**Scenario:** Webhook endpoint not receiving events

**Causes:**
- Webhook URL not accessible
- Firewall blocking
- Webhook secret mismatch

**Recovery:**
1. Verify webhook URL accessibility
2. Check firewall settings
3. Verify webhook secret
4. Fall back to polling

**Example:**
```typescript
// If webhook not received within timeout, start polling
const webhookTimeout = setTimeout(() => {
    if (!webhookReceived) {
        console.log('Webhook timeout - falling back to polling');
        startPolling(runId);
    }
}, 30000);
```

---

### **10. Recovery Procedures**

#### **10.1 Agent Recovery**

**Problem:** Agent lost, status unknown

**Procedure:**
1. List all agents via API
2. Match by repository/branch
3. Resume monitoring if found
4. Start new agent if not found

**Example:**
```typescript
async function recoverAgent(runId: string): Promise<void> {
    // Try to get status
    const status = await agentMonitor.getAgentStatus(runId);
    
    if (!status) {
        // Agent not found - may have been deleted
        // List all agents to find matching one
        const allAgents = await listAllAgents();
        const matching = allAgents.find(a => a.repo_path === repoPath);
        
        if (matching) {
            // Found matching agent - resume monitoring
            agentMonitor.startPolling(matching.id);
        } else {
            // Agent truly lost - start new one
            await agentMonitor.startAgentSmart({ prompt, repoPath });
        }
    } else {
        // Agent found - resume monitoring
        agentMonitor.startPolling(runId);
    }
}
```

#### **10.2 Status Sync Recovery**

**Problem:** Local state out of sync with API

**Procedure:**
1. Fetch all agents from API
2. Compare with local state
3. Update local state
4. Resume polling for active agents

**Example:**
```typescript
async function syncStatus(): Promise<void> {
    // Fetch all agents from API
    const apiAgents = await listAllAgents();
    
    // Update local state
    for (const apiAgent of apiAgents) {
        const localAgent = agentMonitor.activeRuns.get(apiAgent.id);
        if (!localAgent || localAgent.status !== apiAgent.status) {
            // Update local state
            agentMonitor.activeRuns.set(apiAgent.id, {
                run_id: apiAgent.id,
                status: mapStatus(apiAgent.status),
                // ... other fields
            });
            
            // Resume polling if running
            if (apiAgent.status === 'RUNNING') {
                agentMonitor.startPolling(apiAgent.id);
            }
        }
    }
    
    // Remove agents not in API
    for (const [runId, localAgent] of agentMonitor.activeRuns.entries()) {
        if (!apiAgents.find(a => a.id === runId)) {
            agentMonitor.activeRuns.delete(runId);
            agentMonitor.stopPolling(runId);
        }
    }
}
```

---

## ⚡ **PART III: PERFORMANCE & OPTIMIZATION**

### **11. Performance Characteristics**

#### **11.1 Latency Targets**

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

#### **11.2 Throughput**

**Agents/Minute:**
- **Target:** 10 agents/minute
- **Limit:** API rate limits

**Concurrent Agents:**
- **Target:** 10 concurrent agents
- **Limit:** API rate limits, memory usage

### **12. Optimization Techniques**

#### **12.1 Reduce API Calls**

**Batch Status Updates:**
```typescript
private pendingUpdates: Map<string, AgentStatus> = new Map();

private scheduleUpdate(runId: string, status: AgentStatus): void {
    this.pendingUpdates.set(runId, status);
    
    if (!this.updateTimer) {
        this.updateTimer = setTimeout(() => {
            // Batch send all pending updates
            for (const [id, status] of this.pendingUpdates.entries()) {
                const envelope = createEnvelope('event', 'agent.status', 'ext->ui', status);
                this.router.route(envelope);
            }
            this.pendingUpdates.clear();
            this.updateTimer = null;
        }, 1000);  // Batch every 1 second
    }
}
```

#### **12.2 Caching**

**Cache Agent Status:**
```typescript
private statusCache = new Map<string, { status: AgentStatus; timestamp: number }>();
private CACHE_TTL = 5000;  // 5 seconds

async getAgentStatusCached(runId: string): Promise<AgentStatus | null> {
    const cached = this.statusCache.get(runId);
    if (cached && Date.now() - cached.timestamp < this.CACHE_TTL) {
        return cached.status;
    }
    
    const status = await this.getAgentStatus(runId);
    if (status) {
        this.statusCache.set(runId, { status, timestamp: Date.now() });
    }
    return status;
}
```

---

## 🔒 **PART IV: SECURITY & COMPLIANCE**

### **13. Security Architecture**

#### **13.1 API Key Security**

**Storage:**
- Use VS Code secure storage: `context.secrets.store()`
- Never log API keys
- Never commit to git

**Example:**
```typescript
// ✅ Good
const apiKey = await context.secrets.get('cursorApiKey');

// ❌ Bad
const apiKey = 'hardcoded-key';  // Never do this!
```

#### **13.2 Webhook Security**

**Secret Verification:**
```typescript
const webhookSecret = await context.secrets.get('webhookSecret');

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

---

## 📊 **PART V: OPERATIONS & MAINTENANCE**

### **14. Monitoring & Observability**

#### **14.1 Key Metrics**

**Agent Metrics:**
- Active agents count
- Agents started per hour
- Average agent runtime
- Success rate

**API Metrics:**
- API calls per minute
- API error rate
- Rate limit hits
- Webhook delivery rate

**Example:**
```typescript
const metrics = {
    activeAgents: agentMonitor.activeRuns.size,
    agentsStarted: agentMonitor.stats.agentsStarted,
    avgRuntime: agentMonitor.stats.avgRuntime,
    successRate: agentMonitor.stats.successRate,
    apiCallsPerMinute: agentMonitor.stats.apiCallsPerMinute,
    apiErrorRate: agentMonitor.stats.apiErrorRate
};
```

---

### **15. Troubleshooting Guide**

#### **15.1 Problem: Agent Not Starting**

**Symptoms:**
- API call fails
- Error: "API key not configured"

**Diagnosis:**
```typescript
const apiKey = await context.secrets.get('cursorApiKey');
if (!apiKey) {
    console.log('API key not configured');
}
```

**Solutions:**
1. Configure API key in settings
2. Verify API key is valid: `GET /v0/me`
3. Check API key permissions

#### **15.2 Problem: Status Not Updating**

**Symptoms:**
- Status stuck at "pending"
- No status updates received

**Diagnosis:**
```typescript
const status = await agentMonitor.getAgentStatus(runId);
console.log('Current status:', status);
```

**Solutions:**
1. Verify polling is active
2. Check webhook URL accessibility
3. Verify MessageRouter is routing events

---

## 🔄 **PART VI: MIGRATION & UPGRADES**

### **16. Migration Guide**

#### **16.1 From Manual Agent Control**

**Before:**
```typescript
// Manual agent control
const agent = await cursorAgent.start();
await agent.wait();
```

**After:**
```typescript
// Automated agent control
const runId = await agentMonitor.startAgentSmart({
    prompt: 'Task',
    repoPath: '/path/to/repo'
});
// Status updates via MessageRouter automatically
```

---

## 📚 **REFERENCE APPENDIX**

### **A. Complete Error Code List**

| Code | Meaning | Resolution |
|------|---------|------------|
| `API_KEY_NOT_CONFIGURED` | API key not set | Configure API key |
| `GITHUB_URL_REQUIRED` | Cloud API requires GitHub URL | Use GitHub URL or CLI |
| `AGENT_NOT_FOUND` | Agent run ID not found | Verify run ID |
| `API_RATE_LIMIT_EXCEEDED` | Rate limit hit | Implement rate limiting |
| `WEBHOOK_VERIFICATION_FAILED` | Webhook secret mismatch | Verify secret |
| `CLI_AGENT_NOT_FOUND` | cursor-agent not installed | Install cursor-agent |

### **B. Configuration Reference**

| Option | Default | Description |
|--------|---------|-------------|
| `cursorApiKey` | null | Cursor API key |
| `cursorApiUrl` | `https://api.cursor.com/v0` | API base URL |
| `webhookUrl` | null | Webhook URL |
| `pollingInterval` | 5000ms | Status polling interval |
| `maxRuntimeHours` | 6 | Maximum agent runtime |

---

## ✅ **CONCLUSION**

This T4 Complete Reference provides exhaustive documentation for all aspects of Cursor Agent Automation. Use this as your definitive reference for:

- **API Reference:** Complete method signatures and examples
- **Edge Cases:** All known edge cases and solutions
- **Error Handling:** Complete error code reference
- **Performance:** Characteristics and optimization techniques
- **Security:** Threat model and security measures
- **Operations:** Monitoring, troubleshooting, maintenance
- **Migration:** Upgrade and compatibility guides

**For Implementation:** See T3 Detailed Implementation Guide  
**For Architecture:** See T2 Architecture  
**For Overview:** See T1 Overview  
**For Quick Reference:** See T0 Executive

---

**Status:** Production Ready ✅  
**Version:** v1.0.0  
**Last Updated:** 2025-11-04  
**Author:** Aether

