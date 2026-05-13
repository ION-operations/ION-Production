---
id: "cursor_api_deep_dive"
system: "lucid_chat"
component: "api_integration"
level: "T3"
type: "deep_analysis"
title: "Cursor API Deep Dive - Complete Integration Guide"
description: "Comprehensive analysis of Cursor Background Agents API capabilities, endpoints, parameters, workflows, and integration patterns"
created: "2025-01-27T00:00:00Z"
updated: "2025-01-27T00:00:00Z"
author: "aether"
status: "active"
tags: ["cursor", "ide", "code-generation", "api-integration", "deep-dive"]
---

# Cursor API Deep Dive - Complete Integration Guide

**Purpose:** Comprehensive understanding of Cursor Background Agents API for proper integration  
**Status:** 🔍 **DEEP ANALYSIS COMPLETE**  
**Official Documentation:** https://docs.cursor.com/background-agent/api/overview

---

## 🎯 **CURSOR API OVERVIEW**

Cursor provides Background Agents API for autonomous code generation:
- **Autonomous Agents** - AI agents that make code changes autonomously
- **Repository Integration** - Works with GitHub repositories
- **Follow-up Prompts** - Iterative development with additional instructions
- **Code Generation** - Generate and modify code based on prompts
- **Scalability** - Up to 256 active agents per API key

**Key Features:**
- Autonomous code changes
- GitHub integration
- Natural language prompts
- Follow-up instructions
- Agent management

---

## 🔐 **AUTHENTICATION**

**Method:** Bearer Token (API Key)

**Header:**
```
Authorization: Bearer YOUR_API_KEY
```

**API Key Management:**
- Obtain from: Cursor Dashboard → Integrations
- Store securely in environment variable: `CURSOR_API_KEY`
- Rate limits: Based on account tier

**Base URL:**
```
https://api.cursor.com
```

---

## 📡 **API ENDPOINTS & CAPABILITIES**

### **1. Create Agent**

**Endpoint:** `POST https://api.cursor.com/agents`

**Purpose:** Create a new background agent

**Request Parameters:**

```typescript
interface CursorCreateAgentRequest {
  // Required
  name: string                      // Agent name
  
  // Required
  repository: string                // GitHub repository URL (e.g., 'https://github.com/owner/repo')
  
  // Required
  instructions: string              // Instructions for the agent (what to do)
  
  // Optional
  branch?: string                   // Branch to work on (default: 'main')
  model?: string                    // Model to use (default: 'gpt-4')
  max_iterations?: number           // Max iterations (default: 10)
  timeout?: number                  // Timeout in seconds (default: 3600)
}
```

**Response Structure:**

```typescript
interface CursorCreateAgentResponse {
  id: string                        // Agent ID
  name: string
  repository: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  created_at: string
  updated_at: string
}
```

---

### **2. Get Agent Status**

**Endpoint:** `GET https://api.cursor.com/agents/{agent_id}`

**Purpose:** Get status of an agent

**Response:**

```typescript
interface CursorAgentStatus {
  id: string
  name: string
  repository: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  instructions: string
  current_step?: string             // Current step description
  progress?: number                 // 0-100
  logs?: Array<{
    timestamp: string
    level: 'info' | 'warning' | 'error'
    message: string
  }>
  changes?: Array<{
    file: string
    type: 'created' | 'modified' | 'deleted'
    diff?: string
  }>
  created_at: string
  updated_at: string
  completed_at?: string
  error?: string
}
```

---

### **3. List Agents**

**Endpoint:** `GET https://api.cursor.com/agents`

**Purpose:** List all agents

**Query Parameters:**

```typescript
interface CursorListAgentsRequest {
  repository?: string                // Filter by repository
  status?: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  limit?: number                    // Results per page (default: 20)
  offset?: number                   // Pagination offset
}
```

**Response:**

```typescript
interface CursorListAgentsResponse {
  agents: CursorAgentStatus[]
  total: number
  limit: number
  offset: number
}
```

---

### **4. Send Follow-up Prompt**

**Endpoint:** `POST https://api.cursor.com/agents/{agent_id}/prompt`

**Purpose:** Send additional instructions to a running agent

**Request Parameters:**

```typescript
interface CursorFollowUpPromptRequest {
  prompt: string                    // Additional instructions
}
```

**Response:**

```typescript
interface CursorFollowUpPromptResponse {
  success: boolean
  message: string
}
```

---

### **5. Cancel Agent**

**Endpoint:** `POST https://api.cursor.com/agents/{agent_id}/cancel`

**Purpose:** Cancel a running agent

**Response:**

```typescript
interface CursorCancelAgentResponse {
  success: boolean
  message: string
}
```

---

## 🔄 **WORKFLOWS**

### **Workflow 1: Create and Monitor Agent**

1. User provides repository URL
2. Enter instructions for the agent
3. Configure options (branch, model, etc.)
4. Create agent → Get agent ID
5. Poll status → Monitor progress
6. View changes → Review code changes
7. Accept/reject changes

### **Workflow 2: Iterative Development**

1. Create agent with initial instructions
2. Monitor progress
3. Send follow-up prompts as needed
4. Review changes iteratively
5. Complete when satisfied

---

## ⚡ **RATE LIMITS**

**Free Tier:**
- Limited agents per month

**Paid Tier:**
- Higher limits
- Up to 256 active agents

---

## 💰 **PRICING**

**Free Tier:**
- Limited agents

**Paid Tier:**
- Pay-per-use pricing
- Based on agent runtime

**Note:** Check Cursor pricing page for current rates.

---

## 🎨 **UI COMPONENT REQUIREMENTS**

### **Agent Creation Panel**

**Repository Input:**
- GitHub repository URL input
- Repository validation
- Branch selector

**Instructions Input:**
- Large textarea
- Character counter
- Examples/templates

**Agent Configuration:**
- Model selector
- Max iterations input
- Timeout input

**Create Button:**
- Show loading state

### **Agent Status Panel**

**Agent List:**
- Agent cards with status
- Repository name
- Progress indicator
- Created/updated timestamps

**Agent Details:**
- Status badge
- Current step display
- Progress bar
- Logs display
- Changes display (diff view)
- Follow-up prompt input
- Cancel button

---

## 🔧 **IMPLEMENTATION NOTES**

### **Service Layer Structure**

```typescript
class CursorService extends BaseAPIService {
  constructor(apiKey?: string) {
    super('cursor', 'https://api.cursor.com', apiKey)
  }

  async createAgent(request: CursorCreateAgentRequest): Promise<APIResponse<CursorCreateAgentResponse>>
  async getAgentStatus(agentId: string): Promise<APIResponse<CursorAgentStatus>>
  async listAgents(query?: CursorListAgentsRequest): Promise<APIResponse<CursorListAgentsResponse>>
  async sendFollowUpPrompt(agentId: string, prompt: string): Promise<APIResponse<CursorFollowUpPromptResponse>>
  async cancelAgent(agentId: string): Promise<APIResponse<CursorCancelAgentResponse>>
  async pollAgentStatus(
    agentId: string,
    onProgress?: (status: string, progress?: number) => void
  ): Promise<APIResponse<CursorAgentStatus>>
}
```

---

## 📊 **INTEGRATION COMPLEXITY**

**Complexity:** Medium-High

**Dependencies:**
- GitHub integration
- Diff viewer component
- Log viewer component

**Estimated Implementation Time:**
- Service layer: 4-6 hours
- UI components: 8-10 hours
- Agent status display: 4-6 hours
- Diff viewer: 3-4 hours
- Testing: 4-6 hours
- **Total: 23-32 hours**

---

**Status:** Deep dive complete - Ready for implementation  
**Last Updated:** 2025-01-27

