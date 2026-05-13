# Code Execution Sandbox Design

**Author:** Nova (Code Generation Specialist)  
**Date:** 2025-01-27  
**Status:** Design Phase  
**Collaborating With:** Alex (Backend), Sage (Frontend), Aether (Coordinator)

---

## 🎯 **DESIGN OVERVIEW**

### **Objective**
Build a secure code execution sandbox for executing user-generated code with complete isolation, resource limits, and safety guarantees.

### **Security Requirements (From Aether)**
- **Network:** No network access (or restricted to localhost only for AIM-OS services)
- **File System:** Read-only access to specific directories (code workspace only)
- **Resource Limits:** CPU (50%), Memory (512MB), Timeout (30 seconds)
- **Isolation:** Docker container or similar sandbox environment
- **Error Handling:** All errors captured and returned safely

---

## 📋 **SANDBOX ARCHITECTURE**

### **Components**

1. **SandboxService** - Main service for managing sandbox instances
2. **CodeExecutionService** - Orchestrates code execution flow
3. **SandboxContainer** - Docker container wrapper for execution
4. **ResourceManager** - Enforces CPU, memory, timeout limits
5. **SecurityManager** - Enforces network, file system restrictions

---

## 🔒 **SECURITY DESIGN**

### **Isolation Strategy**

**Docker Container Approach:**
- Each code execution runs in isolated Docker container
- Container automatically destroyed after execution
- No persistent state between executions
- Complete isolation from host system

### **Resource Limits**

**CPU Limits:**
- Maximum 50% CPU usage per execution
- Enforced via Docker CPU quota

**Memory Limits:**
- Maximum 512MB RAM per execution
- Enforced via Docker memory limit
- OOM killer terminates if exceeded

**Timeout Limits:**
- Maximum 30 seconds execution time
- Automatically terminated if exceeded
- Result: `{ error: "Execution timeout after 30 seconds" }`

### **Network Restrictions**

**Default:** No network access
- Container runs with `--network none`
- Prevents external network calls

**Optional:** Localhost-only access
- For AIM-OS service integration only
- Restricted to `localhost:5001`, `localhost:8000`
- Managed via Docker network configuration

### **File System Access**

**Read-Only Workspace:**
- Mount workspace directory as read-only
- Code can read files but cannot modify
- Prevents malicious file system operations

**No Write Access:**
- Container has no write permissions to host
- All file operations isolated to container
- Container destroyed after execution

---

## 📁 **FILE STRUCTURE**

### **Files to Create**

1. **`src/services/SandboxService.ts`** - Main sandbox service
2. **`src/services/CodeExecutionService.ts`** - Code execution orchestrator
3. **`src/services/ResourceManager.ts`** - Resource limit enforcement
4. **`src/services/SecurityManager.ts`** - Security restriction enforcement
5. **`docker/sandbox.Dockerfile`** - Sandbox container image
6. **`docker/sandbox-config.json`** - Sandbox configuration

---

## 🔧 **IMPLEMENTATION DESIGN**

### **SandboxService.ts**

```typescript
export interface SandboxConfig {
  language: string
  code: string
  timeout?: number  // Default: 30000ms
  memory?: number   // Default: 512MB
  cpu?: number      // Default: 50%
  network?: 'none' | 'localhost'
  workspace?: string
}

export interface ExecutionResult {
  success: boolean
  stdout?: string
  stderr?: string
  exitCode?: number
  executionTime?: number
  error?: string
  atom_id?: string  // CMC atom ID if stored
}

export class SandboxService {
  async executeCode(config: SandboxConfig): Promise<ExecutionResult>
  async createContainer(config: SandboxConfig): Promise<string>
  async destroyContainer(containerId: string): Promise<void>
  async streamOutput(containerId: string): Promise<{ stdout: string; stderr: string }>
}
```

### **CodeExecutionService.ts**

```typescript
export interface CodeExecutionRequest {
  code: string
  language: string
  context?: Record<string, any>
  input?: string
}

export interface CodeExecutionResult extends ExecutionResult {
  output: string
  validated: boolean
  confidence?: number
}

export class CodeExecutionService {
  async execute(request: CodeExecutionRequest): Promise<CodeExecutionResult>
  async validateExecution(result: ExecutionResult): Promise<boolean>
  async storeResult(result: CodeExecutionResult): Promise<string>  // Returns atom_id
}
```

### **ResourceManager.ts**

```typescript
export class ResourceManager {
  enforceCPULimit(containerId: string, cpuPercent: number): Promise<void>
  enforceMemoryLimit(containerId: string, memoryMB: number): Promise<void>
  enforceTimeout(containerId: string, timeoutMs: number): Promise<void>
  monitorResources(containerId: string): Promise<ResourceUsage>
}
```

### **SecurityManager.ts**

```typescript
export class SecurityManager {
  validateCode(code: string, language: string): Promise<ValidationResult>
  setupNetworkRestrictions(containerId: string, mode: 'none' | 'localhost'): Promise<void>
  setupFileSystemRestrictions(containerId: string, workspace: string): Promise<void>
  scanForSecurityIssues(code: string): Promise<SecurityIssue[]>
}
```

---

## 🐳 **DOCKER INTEGRATION**

### **Sandbox Dockerfile**

```dockerfile
FROM node:18-alpine AS base
# Minimal base image for TypeScript/JavaScript execution

FROM python:3.11-slim AS python
# Python execution environment

# Sandbox image with multiple language support
FROM base
RUN apk add --no-cache python3 py3-pip
WORKDIR /workspace
# No network access by default
# Read-only workspace mount
```

### **Container Configuration**

```json
{
  "image": "aether-sandbox:latest",
  "network": "none",
  "memory": "512m",
  "cpu_percent": 50,
  "timeout": 30,
  "read_only": true,
  "workspace_mount": "/workspace:ro"
}
```

---

## 🔄 **EXECUTION FLOW**

### **Step 1: Validation**
- SecurityManager validates code
- Scans for security issues
- Checks syntax

### **Step 2: Container Creation**
- SandboxService creates isolated container
- SecurityManager applies restrictions
- ResourceManager sets limits

### **Step 3: Code Execution**
- Code executed in container
- Output captured (stdout, stderr)
- ResourceManager monitors usage

### **Step 4: Result Capture**
- Execution result captured
- Container destroyed automatically
- Result validated

### **Step 5: Storage**
- Result stored in CMC
- Timeline entry created (TCS)
- Confidence tracked (VIF)

---

## 🧪 **TESTING STRATEGY**

### **Security Tests**
- Test network isolation
- Test file system restrictions
- Test resource limits
- Test timeout enforcement

### **Execution Tests**
- Test code execution for each language
- Test error handling
- Test output capture
- Test resource monitoring

---

## 📊 **INTEGRATION POINTS**

### **AIM-OS Integration**
- **CMC:** Store execution results as atoms
- **VIF:** Track confidence for execution safety
- **TCS:** Track executions in timeline
- **MCPService:** Use for CMC, VIF, TCS operations

---

## 🚀 **IMPLEMENTATION PLAN**

### **Phase 1: Core Sandbox (Day 5)**
- Design Docker container configuration
- Implement SandboxService basic operations
- Test container creation/destruction

### **Phase 2: Resource Management (Day 6)**
- Implement ResourceManager
- Test CPU, memory, timeout limits
- Test resource monitoring

### **Phase 3: Security & Integration (Day 7)**
- Implement SecurityManager
- Integrate with CodeExecutionService
- Test complete execution flow
- Integrate with AIM-OS (CMC, VIF, TCS)

---

## ✅ **SUCCESS CRITERIA**

- ✅ Code executes in isolated Docker container
- ✅ Resource limits enforced (CPU 50%, Memory 512MB, Timeout 30s)
- ✅ Network restrictions applied (none or localhost-only)
- ✅ File system restrictions applied (read-only workspace)
- ✅ All errors captured and returned safely
- ✅ Results stored in CMC
- ✅ Executions tracked in TCS
- ✅ Confidence tracked in VIF

---

**Status:** Design Complete, Ready for Implementation  
**Collaboration Status:** Ready to work with @Alex on backend, @Sage on UI

