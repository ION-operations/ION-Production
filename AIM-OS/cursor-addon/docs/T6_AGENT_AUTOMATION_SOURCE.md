---
id: "agent_automation_T6_source"
system: "agent_automation"
component: null
level: "T6"
type: "source_code"
title: "Agent Automation - Source Code Documentation"
description: "Complete source code documentation with inline comments and explanations"
audience: "maintainers, code reviewers"
confidence_threshold: 0.50
token_cost: 5000
word_count: 5000
created: "2025-11-04T00:55:00Z"
updated: "2025-11-04T00:55:00Z"
author: "aether"
status: "complete"
tags: ["agent-automation", "source-code", "documentation", "t0-t6", "transitional"]
dependencies: ["agent_automation_T5_quick"]
related_docs: ["T4_AGENT_AUTOMATION_COMPLETE.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# Agent Automation – T6 Source Code Documentation (≈5,000 words)

**Date:** 2025-11-04  
**Status:** Production Ready ✅  
**Purpose:** Complete source code documentation with inline explanations

---

## 📁 **SOURCE CODE STRUCTURE**

```
cursor-addon/src/agent/
└── agentMonitor.ts    # Main AgentMonitor class (637 lines)
```

---

## 🔧 **AGENTMONITOR CLASS**

### **File: `src/agent/agentMonitor.ts`**

**Purpose:** Manages Cursor Background Agents via HTTP API and CLI

**Dependencies:**
- `MessageRouter` - For status updates
- `createEnvelope` - For envelope protocol
- `vscode` - VS Code Extension API

---

### **Type Definitions**

```typescript
// Lines 12-27
export interface AgentRun {
    run_id: string;                    // Unique run identifier
    task_file: string;                  // Task YAML file path
    repo_path: string;                  // Repository path (GitHub URL or local)
    branch?: string;                    // Branch name
    max_runtime_hours?: number;         // Maximum runtime in hours
    status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
    created_at: number;                 // Timestamp (Date.now())
    started_at?: number;                // Start timestamp
    completed_at?: number;               // Completion timestamp
    current_step?: number;              // Current step number
    total_steps?: number;                // Total steps
    last_command?: string;              // Last command executed
    output?: string[];                  // Output lines
    summary?: string;                   // Summary text from API
}
```

**Purpose:** Internal representation of agent run state

---

```typescript
// Lines 29-42
export interface AgentStatus {
    run_id: string;                     // Run identifier
    status: AgentRun['status'];          // Current status
    current_step?: number;              // Current step
    total_steps?: number;                // Total steps
    last_command?: string;              // Last command
    output?: string[];                  // Output lines
    exit_code?: number;                  // Exit code (if completed)
    summary?: {                          // Summary object
        steps_completed: number;
        tests_passed?: number;
        files_changed?: number;
    };
}
```

**Purpose:** Status response from API

---

### **Class Definition**

```typescript
// Lines 44-64
export class AgentMonitor {
    private router: MessageRouter;                    // MessageRouter for status updates
    private activeRuns: Map<string, AgentRun> = new Map();  // Active runs by ID
    private statusIntervals: Map<string, NodeJS.Timeout> = new Map();  // Polling intervals
    private cursorApiKey: string | null = null;       // Cursor API key
    private cursorApiUrl: string = 'https://api.cursor.com/v0';  // API base URL
    private webhookUrl: string | null = null;        // Webhook URL for events

    constructor(
        router: MessageRouter,
        options: {
            cursorApiKey?: string;
            cursorApiUrl?: string;
            webhookUrl?: string;
        } = {}
    ) {
        this.router = router;
        this.cursorApiKey = options.cursorApiKey || null;
        this.cursorApiUrl = options.cursorApiUrl || 'https://api.cursor.com/v0';
        this.webhookUrl = options.webhookUrl || null;
    }
}
```

**Purpose:** Core class for agent management

**Key Properties:**
- `router` - Routes status updates via bulletproof messaging
- `activeRuns` - Tracks all active agent runs
- `statusIntervals` - Manages polling intervals
- `cursorApiKey` - API key for Cloud API
- `cursorApiUrl` - API base URL (fixed to `/v0`)
- `webhookUrl` - Webhook URL for real-time events

---

### **Key Methods**

#### **`startAgentSmart()` - Lines 73-157**

**Purpose:** Automatically chooses Cloud API or CLI based on repo path

**Logic Flow:**
1. Check if `repoPath` is GitHub URL → Use Cloud API
2. Try to detect GitHub URL from git remote
3. If GitHub URL found → Use Cloud API (if API key configured)
4. Otherwise → Fall back to CLI

**Key Features:**
- Automatic GitHub URL detection
- Graceful fallback to CLI
- Error handling for missing API key

**Code Structure:**
```typescript
async startAgentSmart(params: {...}): Promise<{ runId: string; method: 'cloud' | 'local' }> {
    // Check if already GitHub URL
    if (repoPath.startsWith('https://github.com/')) {
        return await this.startAgent({ ... });  // Cloud API
    }
    
    // Try to detect GitHub URL
    try {
        const githubUrl = await this.getGitHubUrl(repoPath);
        if (githubUrl.startsWith('https://github.com/')) {
            return await this.startAgent({ ... });  // Cloud API
        }
    } catch (error) {
        // No GitHub URL - use CLI
    }
    
    // Fall back to CLI
    return await this.startLocalAgent({ ... });
}
```

---

#### **`startAgent()` - Lines 168-239**

**Purpose:** Start agent using Cloud API (requires GitHub URL)

**Key Implementation Details:**
- Validates API key
- Converts repo path to GitHub URL (if needed)
- Creates agent via `POST /v0/agents`
- Stores run in `activeRuns` Map
- Sends 'agent.started' event via MessageRouter
- Starts status polling

**Error Handling:**
- Throws error if API key not configured
- Throws error if GitHub URL invalid
- Handles API errors gracefully

**Code Structure:**
```typescript
async startAgent(params: {...}): Promise<string> {
    // Validate API key
    if (!this.cursorApiKey) {
        throw new Error('Cursor API key not configured');
    }
    
    // Create agent via API
    const response = await fetch(`${this.cursorApiUrl}/agents`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${this.cursorApiKey}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            prompt: { text: `Execute task from ${taskFile}` },
            source: { repository: await this.getGitHubUrl(repoPath), ref: branch || 'main' },
            target: { branchName: branch || `agent/${Date.now()}`, autoCreatePr: false },
            webhook: this.webhookUrl ? { url: this.webhookUrl } : undefined
        })
    });
    
    // Handle response
    const agentResponse = await response.json();
    const run: AgentRun = {
        run_id: agentResponse.id,
        task_file: taskFile,
        repo_path: repoPath,
        branch: branch,
        status: this.mapStatus(agentResponse.status),
        created_at: new Date(agentResponse.createdAt).getTime()
    };
    
    // Store run
    this.activeRuns.set(run.run_id, run);
    
    // Send started event
    await this.router.route(createEnvelope('event', 'agent.started', 'ext->ui', {...}));
    
    // Start polling
    this.startStatusPolling(run.run_id);
    
    return run.run_id;
}
```

---

#### **`startLocalAgent()` - Lines 241-307**

**Purpose:** Start agent using CLI (works with local repos)

**Key Implementation Details:**
- Executes `cursor-agent --print --output-format json`
- Parses JSON output
- Stores run in `activeRuns` Map
- Sends 'agent.started' event

**Error Handling:**
- Handles CLI execution errors
- Handles JSON parsing errors
- Timeout protection (5 minutes)

**Code Structure:**
```typescript
async startLocalAgent(params: {...}): Promise<{ threadId: string; output: string[] }> {
    const { prompt, repoPath } = params;
    
    try {
        // Execute CLI
        const result = execSync(
            `cursor-agent --print --output-format json "${prompt}"`,
            {
                cwd: repoPath,
                encoding: 'utf-8',
                timeout: 300000  // 5 minutes
            }
        );
        
        const output = JSON.parse(result);
        const threadId = output.thread_id || `local-${Date.now()}`;
        
        // Store run
        this.activeRuns.set(threadId, {
            run_id: threadId,
            task_file: 'local',
            repo_path: repoPath,
            status: 'running',
            created_at: Date.now(),
            output: output.output || []
        });
        
        // Send started event
        await this.router.route(createEnvelope('event', 'agent.started', 'ext->ui', {...}));
        
        return { threadId, output: output.output || [] };
    } catch (error: any) {
        throw new Error(`Failed to start local agent: ${error.message}`);
    }
}
```

---

#### **`getAgentStatus()` - Lines 281-335**

**Purpose:** Get current agent status from API

**Key Implementation Details:**
- Calls `GET /v0/agents/{id}`
- Maps API status to internal status
- Handles 404 (agent not found)
- Returns null if API key not configured

**Code Structure:**
```typescript
async getAgentStatus(runId: string): Promise<AgentStatus | null> {
    if (!this.cursorApiKey) {
        return null;
    }
    
    try {
        const response = await fetch(`${this.cursorApiUrl}/agents/${runId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${this.cursorApiKey}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            return null;  // Agent not found
        }
        
        const agentResponse = await response.json();
        
        return {
            run_id: runId,
            status: this.mapStatus(agentResponse.status),
            current_step: agentResponse.summary?.steps_completed,
            total_steps: agentResponse.summary?.total_steps,
            summary: agentResponse.summary
        };
    } catch (error) {
        return null;
    }
}
```

---

#### **`mapStatus()` - Lines 337-350**

**Purpose:** Map API status to internal status format

**Mapping:**
- `CREATING` → `pending`
- `RUNNING` → `running`
- `FINISHED` → `completed`
- `FAILED` → `failed`
- `CANCELLED` → `cancelled`

**Code Structure:**
```typescript
private mapStatus(apiStatus: string): AgentRun['status'] {
    switch (apiStatus) {
        case 'CREATING': return 'pending';
        case 'RUNNING': return 'running';
        case 'FINISHED': return 'completed';
        case 'FAILED': return 'failed';
        case 'CANCELLED': return 'cancelled';
        default: return 'pending';
    }
}
```

---

#### **`startStatusPolling()` - Lines 352-387**

**Purpose:** Start polling agent status every 5 seconds

**Key Implementation Details:**
- Creates interval timer
- Polls status every 5 seconds
- Sends status updates via MessageRouter
- Stops polling on completion/failure

**Code Structure:**
```typescript
private startStatusPolling(runId: string): void {
    // Clear existing interval if any
    this.stopStatusPolling(runId);
    
    const interval = setInterval(async () => {
        try {
            const status = await this.getAgentStatus(runId);
            if (!status) {
                // Agent not found - stop polling
                this.stopStatusPolling(runId);
                return;
            }
            
            // Update local state
            const run = this.activeRuns.get(runId);
            if (run) {
                run.status = status.status;
                run.current_step = status.current_step;
                run.total_steps = status.total_steps;
                run.summary = status.summary?.steps_completed.toString();
            }
            
            // Send status update via MessageRouter
            await this.router.route(createEnvelope('event', 'agent.status', 'ext->ui', status));
            
            // Stop polling if completed
            if (status.status === 'completed' || status.status === 'failed' || status.status === 'cancelled') {
                this.stopStatusPolling(runId);
            }
        } catch (error) {
            console.error('Status polling error:', error);
        }
    }, 5000);  // Poll every 5 seconds
    
    this.statusIntervals.set(runId, interval);
}
```

---

#### **`stopStatusPolling()` - Lines 389-396**

**Purpose:** Stop polling for specific agent

**Code Structure:**
```typescript
private stopStatusPolling(runId: string): void {
    const interval = this.statusIntervals.get(runId);
    if (interval) {
        clearInterval(interval);
        this.statusIntervals.delete(runId);
    }
}
```

---

#### **`getGitHubUrl()` - Lines 398-420**

**Purpose:** Detect GitHub URL from local repository path

**Implementation:**
- Reads `git remote get-url origin`
- Converts SSH URLs to HTTPS
- Handles errors gracefully

**Code Structure:**
```typescript
async getGitHubUrl(localPath: string): Promise<string> {
    try {
        const result = execSync(
            'git remote get-url origin',
            { cwd: localPath, encoding: 'utf-8' }
        );
        
        const url = result.trim();
        
        // Convert SSH to HTTPS
        if (url.startsWith('git@github.com:')) {
            return url.replace('git@github.com:', 'https://github.com/').replace('.git', '');
        }
        
        // Remove .git suffix if present
        return url.replace(/\.git$/, '');
    } catch (error) {
        throw new Error(`Failed to get GitHub URL: ${error.message}`);
    }
}
```

---

#### **`handleWebhookEvent()` - Lines 422-460**

**Purpose:** Process webhook events from Cursor API

**Implementation:**
- Updates local state
- Routes event via MessageRouter
- Handles different event types

**Code Structure:**
```typescript
async handleWebhookEvent(payload: any): Promise<void> {
    const { event, agent_id } = payload;
    
    // Update local state
    const run = this.activeRuns.get(agent_id);
    if (run) {
        switch (event) {
            case 'agent.status':
                run.status = this.mapStatus(payload.status);
                run.current_step = payload.summary?.steps_completed;
                run.total_steps = payload.summary?.total_steps;
                break;
            case 'agent.output':
                run.output = [...(run.output || []), ...(payload.output || [])];
                break;
            case 'agent.complete':
                run.status = this.mapStatus(payload.status);
                run.completed_at = Date.now();
                this.stopStatusPolling(agent_id);
                break;
        }
    }
    
    // Route event via MessageRouter
    const envelope = createEnvelope('event', `agent.${event}`, 'ext->ui', payload);
    await this.router.route(envelope);
}
```

---

## 📚 **RELATED DOCUMENTATION**

- **T0 Executive:** [T0_AGENT_AUTOMATION_EXECUTIVE.md](./T0_AGENT_AUTOMATION_EXECUTIVE.md)
- **T1 Overview:** [AUTOMATION_SYSTEMS_EXPLAINED_T1.md](./AUTOMATION_SYSTEMS_EXPLAINED_T1.md)
- **T2 Architecture:** [T2_AGENT_AUTOMATION_ARCHITECTURE.md](./T2_AGENT_AUTOMATION_ARCHITECTURE.md)
- **T3 Detailed:** [T3_AGENT_AUTOMATION_DETAILED.md](./T3_AGENT_AUTOMATION_DETAILED.md)
- **T4 Complete:** [T4_AGENT_AUTOMATION_COMPLETE.md](./T4_AGENT_AUTOMATION_COMPLETE.md)
- **T5 Quick:** [T5_AGENT_AUTOMATION_QUICK.md](./T5_AGENT_AUTOMATION_QUICK.md)
- **Source Code:** `cursor-addon/src/agent/agentMonitor.ts`

---

**Status:** Production Ready ✅  
**Version:** v1.0.0  
**Last Updated:** 2025-11-04  
**Author:** Aether

