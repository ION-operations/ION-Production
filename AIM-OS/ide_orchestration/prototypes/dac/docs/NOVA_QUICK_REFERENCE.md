# Nova Quick Reference Guide

**Agent:** Nova (Code Generation Specialist)  
**Date:** 2025-01-27  
**Status:** Week 1-2 Complete  

---

## 🚀 **QUICK START**

### **Import Hooks**

```typescript
import { useICIP } from '../hooks/useICIP'
import { useCodeExecution } from '../hooks/useCodeExecution'
```

### **Basic Usage**

```typescript
// Code Generation
const icip = useICIP()
const result = await icip.generateFunction('A sorting function', 'typescript')

// Code Execution
const execution = useCodeExecution()
const execResult = await execution.executeCodeQuick('console.log("Hello")', 'typescript')

// Code Validation
const validation = await icip.validateCode(code, 'typescript')
```

---

## 📋 **SERVICES**

### **ICIPService**
- `generateCode()` - Generate code (all types)
- `transformCode()` - Transform code
- `validateCode()` - Validate code

### **SandboxService**
- `executeCode()` - Execute code in sandbox
- `createContainer()` - Create sandbox container
- `destroyContainer()` - Destroy container

### **CodeExecutionService**
- `execute()` - Execute code with validation and tracking

### **CodeValidationService**
- `validate()` - Comprehensive code validation
- `validateByType()` - Validate by specific type

---

## 🎣 **HOOKS**

### **useICIP()**
- `generateFunction()` - Generate function
- `generateClass()` - Generate class
- `generateTest()` - Generate test
- `generateDocumentation()` - Generate docs
- `completeCode()` - Complete code
- `refactorCode()` - Refactor code
- `validateCode()` - Validate code

### **useCodeExecution()**
- `executeCode()` - Execute with options
- `executeCodeQuick()` - Quick execution

---

## 🔗 **INTEGRATION POINTS**

### **MCP Tools Used**
- `mcp_lucid-mcp_store_memory` - Store in CMC
- `mcp_lucid-mcp_track_confidence` - Track VIF confidence
- `mcp_lucid-mcp_add_timeline_entry` - Track in TCS
- `mcp_lucid-mcp_create_sandbox` - Create sandbox (ready for Alex)
- `mcp_lucid-mcp_execute_in_sandbox` - Execute in sandbox (ready for Alex)
- `mcp_lucid-mcp_destroy_sandbox` - Destroy sandbox (ready for Alex)

### **AIM-OS Systems**
- **CMC:** Stores all generated code and execution results
- **VIF:** Tracks confidence for all operations
- **TCS:** Tracks timeline of all code generation and execution

---

## 📁 **FILE STRUCTURE**

```
src/
├── services/
│   ├── ICIPService.ts          (~350 lines)
│   ├── SandboxService.ts       (~330 lines)
│   ├── CodeExecutionService.ts (~250 lines)
│   └── CodeValidationService.ts (~450 lines)
└── hooks/
    ├── useICIP.ts              (~280 lines)
    └── useCodeExecution.ts     (~150 lines)
```

---

## 🔒 **SECURITY**

### **Sandbox Security**
- Complete isolation (Docker containers)
- Resource limits (CPU 50%, Memory 512MB, Timeout 30s)
- Network restrictions (none or localhost-only)
- File system restrictions (read-only workspace)

### **Validation Security**
- 10+ dangerous pattern detection
- Security vulnerability scanning
- Resource exhaustion prevention
- XSS risk detection

---

**Status:** ✅ Week 1-2 Complete  
**Ready For:** UI Integration, Backend Testing  
**Questions:** Post to coordination board

