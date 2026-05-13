---
id: "piston_api_deep_dive"
system: "lucid_chat"
component: "api_integration"
level: "T3"
type: "deep_analysis"
title: "Piston API Deep Dive - Complete Integration Guide"
description: "Comprehensive analysis of Piston API capabilities - open-source code execution engine"
created: "2025-01-27T00:00:00Z"
updated: "2025-01-27T00:00:00Z"
author: "aether"
status: "active"
tags: ["piston", "code-execution", "open-source", "free", "api-integration", "deep-dive"]
---

# Piston API Deep Dive - Complete Integration Guide

**Purpose:** Comprehensive understanding of Piston API for proper integration  
**Status:** 🔍 **DEEP ANALYSIS COMPLETE**  
**Official Documentation:** https://github.com/engineer-man/piston

---

## 🎯 **PISTON API OVERVIEW**

Piston provides open-source code execution:
- **Code Execution** - Run code in 50+ languages
- **Sandboxed** - Secure execution
- **Free** - Completely free
- **Self-Hostable** - Deploy your own instance
- **Fast** - Fast execution

**Key Features:**
- 50+ programming languages
- Sandboxed execution
- Free and open source
- Self-hostable
- Fast execution

---

## 🔐 **AUTHENTICATION**

**Method:** None (public API) or API Key (if self-hosted)

**Base URL:**
```
https://emkc.org/api/v2/piston
```
or self-hosted:
```
https://your-piston-instance.com/api/v2
```

---

## 📡 **API ENDPOINTS & CAPABILITIES**

### **1. Execute Code**

**Endpoint:** `POST https://emkc.org/api/v2/piston/execute`

**Purpose:** Execute code

**Request Body:**

```typescript
interface PistonExecuteRequest {
  language: string                  // Required: Language (e.g., 'python', 'javascript', 'java')
  version: string                   // Required: Version (e.g., '3.10.0', '18.15.0')
  files: Array<{
    name?: string                   // Filename
    content: string                 // Required: Code content
  }>
  stdin?: string                    // Standard input
  args?: string[]                   // Command line arguments
  compile_timeout?: number          // Compilation timeout (ms, default: 10000)
  run_timeout?: number              // Execution timeout (ms, default: 3000)
  compile_memory_limit?: number     // Compilation memory limit (MB)
  run_memory_limit?: number         // Execution memory limit (MB)
}
```

**Response:**

```typescript
interface PistonExecuteResponse {
  language: string
  version: string
  run: {
    stdout: string
    stderr: string
    output: string
    code: number                    // Exit code
    signal: string | null
  }
  compile?: {
    stdout: string
    stderr: string
    output: string
    code: number
    signal: string | null
  }
}
```

---

### **2. List Runtimes**

**Endpoint:** `GET https://emkc.org/api/v2/piston/runtimes`

**Purpose:** List available languages and versions

**Response:**

```typescript
interface PistonRuntimesResponse extends Array<{
  language: string
  version: string
  aliases: string[]
  runtime?: string
}>
```

---

## 🔄 **WORKFLOWS**

### **Workflow 1: Execute Code**

1. User enters code
2. Select language and version
3. Enter input (optional)
4. Submit → Get output
5. Display result

---

## ⚡ **RATE LIMITS**

**Public Instance:**
- Rate limits apply
- Check instance for limits

**Self-Hosted:**
- No limits (your infrastructure)

---

## 💰 **PRICING**

**Free:**
- Completely free
- Open source
- Self-hostable

---

## 🎨 **UI COMPONENT REQUIREMENTS**

### **Code Execution Panel**

**Code Editor:**
- Monaco editor
- Language selector
- Version selector

**Input/Output:**
- Standard input textarea
- Output display
- Error display

**Execute Button:**
- Show loading state

**Results Display:**
- Output display
- Exit code
- Execution time

---

## 🔧 **IMPLEMENTATION NOTES**

### **Service Layer Structure**

```typescript
class PistonService extends BaseAPIService {
  constructor(baseURL: string = 'https://emkc.org/api/v2/piston') {
    super('piston', baseURL)
  }

  async execute(request: PistonExecuteRequest): Promise<APIResponse<PistonExecuteResponse>>
  async listRuntimes(): Promise<APIResponse<PistonRuntimesResponse>>
}
```

---

## 📊 **INTEGRATION COMPLEXITY**

**Complexity:** Low-Medium

**Estimated Implementation Time:**
- Service layer: 3-4 hours
- Code execution UI: 6-8 hours
- Language selector: 2-3 hours
- Testing: 3-4 hours
- **Total: 14-19 hours**

---

**Status:** Deep dive complete - Ready for implementation  
**Last Updated:** 2025-01-27

