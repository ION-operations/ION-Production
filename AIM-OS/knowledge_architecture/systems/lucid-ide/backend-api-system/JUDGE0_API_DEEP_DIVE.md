---
id: "judge0_api_deep_dive"
system: "lucid_chat"
component: "api_integration"
level: "T3"
type: "deep_analysis"
title: "Judge0 API Deep Dive - Complete Integration Guide"
description: "Comprehensive analysis of Judge0 API capabilities - open-source code execution system with 60+ languages"
created: "2025-01-27T00:00:00Z"
updated: "2025-01-27T00:00:00Z"
author: "aether"
status: "active"
tags: ["judge0", "code-execution", "compiler", "free-tier", "api-integration", "deep-dive"]
---

# Judge0 API Deep Dive - Complete Integration Guide

**Purpose:** Comprehensive understanding of Judge0 API for proper integration  
**Status:** 🔍 **DEEP ANALYSIS COMPLETE**  
**Official Documentation:** https://judge0.com/docs

---

## 🎯 **JUDGE0 API OVERVIEW**

Judge0 provides online code execution:
- **Code Execution** - Run code in 60+ languages
- **Compilation** - Compile code
- **Sandboxed** - Secure execution environment
- **Batch Execution** - Execute multiple submissions
- **Free Tier** - Generous free tier
- **Open Source** - Self-hostable

**Key Features:**
- 60+ programming languages
- Sandboxed execution
- Batch processing
- Free tier available
- Open source

---

## 🔐 **AUTHENTICATION**

**Method:** API Key (Optional for free tier)

**Header:**
```
X-RapidAPI-Key: YOUR_API_KEY
```
or
```
Authorization: Bearer YOUR_API_KEY
```

**API Key Management:**
- Obtain from: https://rapidapi.com/judge0-official/api/judge0-ce
- Or self-host Judge0
- Store securely: `JUDGE0_API_KEY`
- Free tier: Limited requests

**Base URL:**
```
https://judge0-ce.p.rapidapi.com
```
or self-hosted:
```
https://your-judge0-instance.com
```

---

## 📡 **API ENDPOINTS & CAPABILITIES**

### **1. Create Submission**

**Endpoint:** `POST https://judge0-ce.p.rapidapi.com/submissions`

**Purpose:** Submit code for execution

**Request Parameters:**

```typescript
interface Judge0SubmissionRequest {
  // Required
  source_code: string               // Source code (base64 encoded)
  
  // Required
  language_id: number               // Language ID (see languages endpoint)
  
  // Optional - Input/Output
  stdin?: string                    // Standard input (base64 encoded)
  expected_output?: string          // Expected output (base64 encoded)
  cpu_time_limit?: number           // CPU time limit in seconds (default: 2)
  cpu_extra_time?: number           // Extra CPU time (default: 0.5)
  wall_time_limit?: number          // Wall time limit (default: 5)
  memory_limit?: number             // Memory limit in KB (default: 128000)
  stack_limit?: number               // Stack limit in KB (default: 64000)
  max_processes_and_or_threads?: number // Max processes/threads (default: 60)
  enable_per_process_and_thread_time_limit?: boolean // Per-process time limit
  enable_per_process_and_thread_memory_limit?: boolean // Per-process memory limit
  max_file_size?: number            // Max file size in KB (default: 1024)
  
  // Optional - Compilation
  compile_only?: boolean            // Only compile, don't run
  compiler_options?: string         // Compiler options
  command_line_arguments?: string   // Command line arguments
  
  // Optional - Other
  redirect_stderr_to_stdout?: boolean // Redirect stderr to stdout
  callback_url?: string             // Webhook URL
  base64_encoded?: boolean          // Whether inputs are base64 (default: true)
  wait?: boolean                    // Wait for result (default: false)
}
```

**Available Languages (60+):**
- C (GCC 9.4.0) - ID: 50
- C++ (GCC 9.4.0) - ID: 54
- Python (3.8.1) - ID: 92
- Java (OpenJDK 13.0.1) - ID: 62
- JavaScript (Node.js 12.14.0) - ID: 63
- TypeScript (3.7.4) - ID: 74
- Go (1.13.5) - ID: 60
- Rust (1.40.0) - ID: 73
- Ruby (2.7.0) - ID: 72
- PHP (7.4.1) - ID: 68
- Swift (5.2.3) - ID: 83
- Kotlin (1.3.70) - ID: 78
- And 50+ more...

**Response:**

```typescript
interface Judge0SubmissionResponse {
  token: string                     // Submission token (for polling)
  status?: {
    id: number
    description: string
  }
  stdout?: string                   // Standard output (base64 if base64_encoded=true)
  stderr?: string                   // Standard error (base64 if base64_encoded=true)
  compile_output?: string           // Compilation output (base64 if base64_encoded=true)
  message?: string                  // Error message
  time?: string                     // Execution time (seconds)
  memory?: number                   // Memory used (KB)
}
```

---

### **2. Get Submission**

**Endpoint:** `GET https://judge0-ce.p.rapidapi.com/submissions/{token}`

**Purpose:** Get submission result

**Query Parameters:**

```typescript
interface Judge0GetSubmissionRequest {
  base64_encoded?: boolean          // Decode base64 (default: true)
  fields?: string                   // Comma-separated fields to include
}
```

**Response:**

```typescript
interface Judge0SubmissionResult {
  source_code: string
  language_id: number
  stdin: string
  expected_output: string | null
  stdout: string | null
  status_id: number
  created_at: string
  finished_at: string
  time: string | null
  wall_time: string | null
  memory: number | null
  stack_size: number | null
  compile_output: string | null
  stderr: string | null
  token: string
  number_of_runs: number
  cpu_time_limit: string
  cpu_extra_time: string
  wall_time_limit: string
  memory_limit: number
  stack_limit: number
  max_processes_and_or_threads: number
  enable_per_process_and_thread_time_limit: boolean
  enable_per_process_and_thread_memory_limit: boolean
  max_file_size: number
  compile_time: string | null
  exit_code: number | null
  exit_signal: number | null
  message: string | null
  wasm: string | null
  status: {
    id: number
    description: string
  }
  language: {
    id: number
    name: string
  }
}
```

**Status IDs:**
- 1: In Queue
- 2: Processing
- 3: Accepted
- 4: Wrong Answer
- 5: Time Limit Exceeded
- 6: Compilation Error
- 7: Runtime Error (SIGSEGV)
- 8: Runtime Error (SIGXFSZ)
- 9: Runtime Error (SIGFPE)
- 10: Runtime Error (SIGABRT)
- 11: Runtime Error (NZEC)
- 12: Runtime Error (Other)
- 13: Internal Error
- 14: Exec Format Error

---

### **3. List Languages**

**Endpoint:** `GET https://judge0-ce.p.rapidapi.com/languages`

**Purpose:** List supported languages

**Response:**

```typescript
interface Judge0LanguagesResponse extends Array<{
  id: number
  name: string
}>
```

---

### **4. Get Language**

**Endpoint:** `GET https://judge0-ce.p.rapidapi.com/languages/{id}`

**Purpose:** Get language details

---

### **5. Get Statuses**

**Endpoint:** `GET https://judge0-ce.p.rapidapi.com/statuses`

**Purpose:** List status types

---

### **6. Batch Submissions**

**Endpoint:** `POST https://judge0-ce.p.rapidapi.com/submissions/batch`

**Purpose:** Submit multiple submissions

**Request:**

```typescript
interface Judge0BatchSubmissionRequest {
  submissions: Array<Judge0SubmissionRequest>
}
```

---

## 🔄 **WORKFLOWS**

### **Workflow 1: Execute Code**

1. User enters code
2. Select language
3. Enter input (optional)
4. Configure limits
5. Submit → Poll for result
6. Display output/error

### **Workflow 2: Batch Execution**

1. User provides multiple code snippets
2. Select languages
3. Submit batch
4. Poll all submissions
5. Display all results

---

## ⚡ **RATE LIMITS**

**Free Tier:**
- Limited requests
- Check RapidAPI for limits

**Self-Hosted:**
- No limits (your infrastructure)

---

## 💰 **PRICING**

**Free Tier:**
- Limited requests via RapidAPI
- Free forever

**Self-Hosted:**
- Free (open source)
- Deploy on your infrastructure

---

## 🎨 **UI COMPONENT REQUIREMENTS**

### **Code Execution Panel**

**Code Editor:**
- Monaco editor
- Language selector
- Syntax highlighting

**Input/Output:**
- Standard input textarea
- Expected output textarea (optional)
- Output display
- Error display

**Configuration:**
- Time limit slider
- Memory limit slider
- Compile only toggle
- Compiler options input

**Execute Button:**
- Show loading state
- Progress indicator

**Results Display:**
- Status indicator
- Output display
- Execution time
- Memory usage
- Compilation output (if compile error)

---

## 🔧 **IMPLEMENTATION NOTES**

### **Service Layer Structure**

```typescript
class Judge0Service extends BaseAPIService {
  constructor(apiKey?: string, baseURL: string = 'https://judge0-ce.p.rapidapi.com') {
    super('judge0', baseURL, apiKey)
  }

  protected getDefaultHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }
    if (this.apiKey) {
      headers['X-RapidAPI-Key'] = this.apiKey
    }
    return headers
  }

  async createSubmission(request: Judge0SubmissionRequest): Promise<APIResponse<Judge0SubmissionResponse>>
  async getSubmission(token: string, options?: Judge0GetSubmissionRequest): Promise<APIResponse<Judge0SubmissionResult>>
  async pollSubmission(
    token: string,
    onStatus?: (status: string) => void,
    interval?: number,
    maxAttempts?: number
  ): Promise<APIResponse<Judge0SubmissionResult>>
  async listLanguages(): Promise<APIResponse<Judge0LanguagesResponse>>
  async getLanguage(id: number): Promise<APIResponse<any>>
  async getStatuses(): Promise<APIResponse<any>>
  async batchSubmissions(request: Judge0BatchSubmissionRequest): Promise<APIResponse<any>>
  
  // Helper methods
  encodeBase64(text: string): string
  decodeBase64(text: string): string
}
```

---

## 📊 **INTEGRATION COMPLEXITY**

**Complexity:** Medium

**Dependencies:**
- Code editor integration
- Polling mechanism
- Base64 encoding/decoding

**Estimated Implementation Time:**
- Service layer: 6-8 hours
- Code execution UI: 8-10 hours
- Language selector: 2-3 hours
- Results display: 4-6 hours
- Polling logic: 3-4 hours
- Testing: 4-6 hours
- **Total: 27-37 hours**

---

**Status:** Deep dive complete - Ready for implementation  
**Last Updated:** 2025-01-27

