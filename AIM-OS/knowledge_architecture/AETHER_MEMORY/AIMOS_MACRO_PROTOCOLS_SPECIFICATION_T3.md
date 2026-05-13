---
id: "aimos_macro_protocols_specification_T3"
system: "cursor_automation"
component: "protocols"
level: "T3"
type: "specification"
title: "AIM-OS Macro Protocols Specification"
description: "Detailed specification of AIM-OS protocols for macro automation"
audience: "developers, automation engineers"
confidence_threshold: 0.90
token_cost: 5000
word_count: 5000+
created: "2025-01-27T00:00:00Z"
updated: "2025-01-27T00:00:00Z"
author: "aether"
status: "production"
tags: ["protocols", "macros", "aimos-standards", "specification", "t3"]
dependencies: ["CURSOR_AUTOMATION_COMPREHENSIVE_RESEARCH_T4.md"]
related_docs: ["CURSOR_AUTOMATION_COMPREHENSIVE_RESEARCH_T4.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# AIM-OS Macro Protocols Specification

**Purpose:** Detailed specification of AIM-OS protocols for macro automation  
**Status:** ✅ **PRODUCTION** - Ready for implementation  
**Goal:** Standardize macro automation across AIM-OS systems

---

## 📋 **PROTOCOL OVERVIEW**

AIM-OS Macro Protocols define standardized interfaces and behaviors for:
1. **Macro Execution** - How macros are executed
2. **Handshake Communication** - How systems confirm operations
3. **Error Recovery** - How failures are handled
4. **State Management** - How state is tracked
5. **Logging & Observability** - How operations are logged

---

## 🔧 **PROTOCOL 1: MACRO EXECUTION PROTOCOL**

### **1.1 Purpose**

Standardize macro execution across platforms with validation, error handling, and verification.

### **1.2 Interface**

```typescript
interface MacroExecutionProtocol {
    // Pre-execution
    validateInput(input: MacroInput): ValidationResult;
    detectPlatform(): Platform;
    checkPrerequisites(platform: Platform): PrerequisiteCheck;
    
    // Execution
    executeMacro(input: MacroInput, platform: Platform): Promise<ExecutionResult>;
    
    // Post-execution
    verifyExecution(result: ExecutionResult): VerificationResult;
    handleErrors(error: Error, context: ErrorContext): ErrorHandlingResult;
}

interface MacroInput {
    message: string;
    options?: MacroOptions;
}

interface MacroOptions {
    waitForResponse?: boolean;
    timeout?: number;
    retryCount?: number;
    retryDelay?: number;
}

interface ValidationResult {
    valid: boolean;
    errors: ValidationError[];
    warnings: ValidationWarning[];
}

interface ExecutionResult {
    success: boolean;
    method: 'command-chaining' | 'macro-automation';
    timestamp: number;
    duration: number;
    error?: Error;
}

interface VerificationResult {
    verified: boolean;
    confidence: number;
    evidence: VerificationEvidence[];
}
```

### **1.3 Validation Rules**

**Required Validations:**
1. ✅ Message is non-empty string
2. ✅ Message length ≤ 10,000 characters
3. ✅ Message contains no null characters
4. ✅ Options are valid (if provided)
5. ✅ Platform is supported

**Validation Implementation:**
```typescript
function validateMacroInput(input: MacroInput): ValidationResult {
    const errors: ValidationError[] = [];
    const warnings: ValidationWarning[] = [];
    
    // Required field validation
    if (!input.message) {
        errors.push({
            code: 'MISSING_MESSAGE',
            message: 'Message is required'
        });
        return { valid: false, errors, warnings };
    }
    
    // Type validation
    if (typeof input.message !== 'string') {
        errors.push({
            code: 'INVALID_TYPE',
            message: 'Message must be a string'
        });
        return { valid: false, errors, warnings };
    }
    
    // Length validation
    if (input.message.length === 0) {
        errors.push({
            code: 'EMPTY_MESSAGE',
            message: 'Message cannot be empty'
        });
    }
    
    if (input.message.length > 10000) {
        errors.push({
            code: 'MESSAGE_TOO_LONG',
            message: `Message exceeds maximum length of 10000 characters (got ${input.message.length})`
        });
    }
    
    // Character validation
    if (input.message.includes('\0')) {
        errors.push({
            code: 'NULL_CHARACTER',
            message: 'Message contains null character'
        });
    }
    
    // Options validation
    if (input.options) {
        if (input.options.timeout !== undefined && input.options.timeout < 0) {
            errors.push({
                code: 'INVALID_TIMEOUT',
                message: 'Timeout must be non-negative'
            });
        }
        
        if (input.options.retryCount !== undefined && input.options.retryCount < 0) {
            errors.push({
                code: 'INVALID_RETRY_COUNT',
                message: 'Retry count must be non-negative'
            });
        }
    }
    
    return {
        valid: errors.length === 0,
        errors,
        warnings
    };
}
```

### **1.4 Platform Detection**

**Supported Platforms:**
- `win32` - Windows
- `darwin` - macOS
- `linux` - Linux

**Detection Implementation:**
```typescript
enum Platform {
    WINDOWS = 'win32',
    MACOS = 'darwin',
    LINUX = 'linux'
}

function detectPlatform(): Platform {
    const platform = process.platform;
    
    switch (platform) {
        case 'win32':
            return Platform.WINDOWS;
        case 'darwin':
            return Platform.MACOS;
        case 'linux':
            return Platform.LINUX;
        default:
            throw new Error(`Unsupported platform: ${platform}`);
    }
}
```

### **1.5 Prerequisite Checks**

**Windows Prerequisites:**
- ✅ PowerShell available
- ✅ System.Windows.Forms available
- ✅ Cursor process running

**macOS Prerequisites:**
- ✅ AppleScript available (`osascript`)
- ✅ Accessibility permissions granted
- ✅ Cursor application installed

**Linux Prerequisites:**
- ✅ xdotool installed
- ✅ X11 display available
- ✅ Cursor window accessible

**Implementation:**
```typescript
interface PrerequisiteCheck {
    passed: boolean;
    missing: string[];
    warnings: string[];
}

async function checkPrerequisites(platform: Platform): Promise<PrerequisiteCheck> {
    const missing: string[] = [];
    const warnings: string[] = [];
    
    switch (platform) {
        case Platform.WINDOWS:
            // Check PowerShell
            try {
                execSync('powershell -Command "exit"', { timeout: 5000 });
            } catch {
                missing.push('PowerShell');
            }
            
            // Check Cursor process
            try {
                const processes = execSync('powershell -Command "Get-Process Cursor -ErrorAction SilentlyContinue"', { encoding: 'utf8' });
                if (!processes.trim()) {
                    warnings.push('Cursor process not running');
                }
            } catch {
                warnings.push('Cannot check Cursor process');
            }
            break;
            
        case Platform.MACOS:
            // Check osascript
            try {
                execSync('which osascript', { timeout: 5000 });
            } catch {
                missing.push('osascript (AppleScript)');
            }
            
            // Check accessibility permissions (heuristic)
            warnings.push('Verify accessibility permissions in System Preferences');
            break;
            
        case Platform.LINUX:
            // Check xdotool
            try {
                execSync('which xdotool', { timeout: 5000 });
            } catch {
                missing.push('xdotool');
            }
            
            // Check X11 display
            if (!process.env.DISPLAY) {
                missing.push('X11 display (DISPLAY environment variable)');
            }
            break;
    }
    
    return {
        passed: missing.length === 0,
        missing,
        warnings
    };
}
```

### **1.6 Execution Flow**

```
1. Validate Input
   ↓ (if invalid)
   Return ValidationResult with errors
   ↓ (if valid)
2. Detect Platform
   ↓
3. Check Prerequisites
   ↓ (if missing)
   Return PrerequisiteCheck with missing items
   ↓ (if passed)
4. Execute Macro (platform-specific)
   ↓
5. Verify Execution
   ↓
6. Return ExecutionResult
```

---

## 🤝 **PROTOCOL 2: HANDSHAKE PROTOCOL**

### **2.1 Purpose**

Ensure reliable communication between systems with confirmation and timing.

### **2.2 Interface**

```typescript
interface HandshakeProtocol {
    request: HandshakeRequest;
    response: HandshakeResponse;
}

interface HandshakeRequest {
    ts: number;                    // Timestamp when request sent
    message: string;               // Message content
    waitForResponse?: boolean;      // Whether to wait for AI response
    timeout?: number;               // Request timeout (ms)
}

interface HandshakeResponse {
    success: boolean;
    accepted: boolean;              // Handshake signal
    ts: number;                     // Timestamp when accepted
    method: 'command-chaining' | 'macro-automation';
    verified?: boolean;             // Post-execution verification
    duration?: number;              // Execution duration (ms)
    error?: Error;
}
```

### **2.3 Handshake Flow**

```
Client → Request (ts: T1)
    ↓
Server → Validate Request
    ↓
Server → Execute Macro
    ↓
Server → Response (accepted: true, ts: T2)
    ↓
Client → Calculate Duration (T2 - T1)
    ↓
Client → Verify (if verified: true)
```

### **2.4 Implementation**

```typescript
async function executeWithHandshake(
    input: MacroInput
): Promise<HandshakeResponse> {
    const requestTs = Date.now();
    
    try {
        // Validate input
        const validation = validateMacroInput(input);
        if (!validation.valid) {
            return {
                success: false,
                accepted: false,
                ts: requestTs,
                method: 'macro-automation',
                error: new Error(validation.errors.map(e => e.message).join(', '))
            };
        }
        
        // Execute macro
        const startTime = Date.now();
        const result = await executeMacro(input, detectPlatform());
        const duration = Date.now() - startTime;
        
        // Return handshake response
        return {
            success: result.success,
            accepted: true,  // Handshake signal
            ts: requestTs,    // Original request timestamp
            method: result.method,
            verified: result.success,
            duration
        };
    } catch (error) {
        return {
            success: false,
            accepted: false,
            ts: requestTs,
            method: 'macro-automation',
            error: error instanceof Error ? error : new Error(String(error))
        };
    }
}
```

### **2.5 Timing Requirements**

**Maximum Acceptable Delays:**
- Request validation: < 10ms
- Platform detection: < 5ms
- Prerequisite check: < 100ms
- Macro execution: < 5000ms (5 seconds)
- Total handshake: < 6000ms (6 seconds)

**Timeout Handling:**
```typescript
async function executeWithTimeout(
    input: MacroInput,
    timeout: number = 6000
): Promise<HandshakeResponse> {
    return Promise.race([
        executeWithHandshake(input),
        new Promise<HandshakeResponse>((resolve) => {
            setTimeout(() => {
                resolve({
                    success: false,
                    accepted: false,
                    ts: Date.now(),
                    method: 'macro-automation',
                    error: new Error(`Execution timeout after ${timeout}ms`)
                });
            }, timeout);
        })
    ]);
}
```

---

## 🔄 **PROTOCOL 3: ERROR RECOVERY PROTOCOL**

### **3.1 Purpose**

Handle failures gracefully with classification, retry logic, and fallback methods.

### **3.2 Error Classification**

```typescript
enum ErrorCategory {
    NETWORK = 'network',           // Network-related errors
    APPLICATION = 'application',   // Application errors
    SYSTEM = 'system',             // System-level errors
    VALIDATION = 'validation',     // Validation errors
    TIMEOUT = 'timeout',           // Timeout errors
    UNKNOWN = 'unknown'            // Unknown errors
}

interface ErrorContext {
    platform: Platform;
    method: 'command-chaining' | 'macro-automation';
    attempt: number;
    timestamp: number;
    input: MacroInput;
}

function classifyError(error: Error): ErrorCategory {
    const message = error.message.toLowerCase();
    
    if (message.includes('timeout') || message.includes('timed out')) {
        return ErrorCategory.TIMEOUT;
    }
    
    if (message.includes('network') || message.includes('connection')) {
        return ErrorCategory.NETWORK;
    }
    
    if (message.includes('validation') || message.includes('invalid')) {
        return ErrorCategory.VALIDATION;
    }
    
    if (message.includes('permission') || message.includes('access')) {
        return ErrorCategory.SYSTEM;
    }
    
    if (message.includes('application') || message.includes('process')) {
        return ErrorCategory.APPLICATION;
    }
    
    return ErrorCategory.UNKNOWN;
}
```

### **3.3 Retry Strategy**

**Retry Rules:**
- ✅ Retry transient errors (network, timeout)
- ❌ Don't retry validation errors
- ⚠️ Retry application errors (with limit)
- ❌ Don't retry system errors (permissions)

**Exponential Backoff:**
```typescript
interface RetryStrategy {
    maxRetries: number;
    initialDelay: number;
    maxDelay: number;
    backoffMultiplier: number;
}

const DEFAULT_RETRY_STRATEGY: RetryStrategy = {
    maxRetries: 3,
    initialDelay: 500,      // 500ms
    maxDelay: 5000,         // 5 seconds
    backoffMultiplier: 2    // Double each retry
};

function calculateRetryDelay(
    attempt: number,
    strategy: RetryStrategy = DEFAULT_RETRY_STRATEGY
): number {
    const delay = strategy.initialDelay * Math.pow(strategy.backoffMultiplier, attempt - 1);
    return Math.min(delay, strategy.maxDelay);
}

async function executeWithRetry(
    input: MacroInput,
    strategy: RetryStrategy = DEFAULT_RETRY_STRATEGY
): Promise<HandshakeResponse> {
    let lastError: Error | null = null;
    
    for (let attempt = 1; attempt <= strategy.maxRetries; attempt++) {
        try {
            const result = await executeWithHandshake(input);
            
            if (result.success) {
                return result;
            }
            
            // Classify error
            const errorCategory = classifyError(result.error!);
            
            // Don't retry validation errors
            if (errorCategory === ErrorCategory.VALIDATION) {
                return result;
            }
            
            // Don't retry system errors
            if (errorCategory === ErrorCategory.SYSTEM) {
                return result;
            }
            
            // Retry transient errors
            if (errorCategory === ErrorCategory.NETWORK || errorCategory === ErrorCategory.TIMEOUT) {
                if (attempt < strategy.maxRetries) {
                    const delay = calculateRetryDelay(attempt, strategy);
                    await sleep(delay);
                    continue;
                }
            }
            
            lastError = result.error!;
        } catch (error) {
            lastError = error instanceof Error ? error : new Error(String(error));
            
            const errorCategory = classifyError(lastError);
            
            // Don't retry validation or system errors
            if (errorCategory === ErrorCategory.VALIDATION || errorCategory === ErrorCategory.SYSTEM) {
                throw lastError;
            }
            
            // Retry transient errors
            if (errorCategory === ErrorCategory.NETWORK || errorCategory === ErrorCategory.TIMEOUT) {
                if (attempt < strategy.maxRetries) {
                    const delay = calculateRetryDelay(attempt, strategy);
                    await sleep(delay);
                    continue;
                }
            }
        }
    }
    
    // All retries failed
    throw lastError || new Error('All retry attempts failed');
}
```

### **3.4 Fallback Methods**

**Fallback Order:**
1. VS Code commands (professional)
2. Macro automation (reliable)
3. Cloud API (if applicable)
4. CLI Agent (if applicable)

**Implementation:**
```typescript
async function executeWithFallback(
    input: MacroInput
): Promise<HandshakeResponse> {
    const methods = [
        () => executeViaVSCodeCommands(input),
        () => executeViaMacro(input),
        () => executeViaCloudAPI(input),
        () => executeViaCLI(input)
    ];
    
    let lastError: Error | null = null;
    
    for (const method of methods) {
        try {
            const result = await method();
            if (result.success) {
                return result;
            }
            lastError = result.error!;
        } catch (error) {
            lastError = error instanceof Error ? error : new Error(String(error));
            continue;
        }
    }
    
    // All methods failed
    return {
        success: false,
        accepted: false,
        ts: Date.now(),
        method: 'macro-automation',
        error: lastError || new Error('All automation methods failed')
    };
}
```

---

## 📊 **PROTOCOL 4: LOGGING & OBSERVABILITY**

### **4.1 Purpose**

Standardize logging across all macro operations for debugging and monitoring.

### **4.2 Log Levels**

- `LOG` - Normal operations
- `SUCCESS` - Successful operations
- `WARN` - Warnings (non-fatal)
- `ERROR` - Errors (fatal)

### **4.3 Log Structure**

```typescript
interface MacroLogEntry {
    timestamp: number;
    level: 'LOG' | 'SUCCESS' | 'WARN' | 'ERROR';
    category: 'MACRO';
    message: string;
    data?: {
        platform?: Platform;
        method?: 'command-chaining' | 'macro-automation';
        input?: MacroInput;
        result?: ExecutionResult;
        error?: Error;
        duration?: number;
    };
}

function logMacroOperation(
    level: 'LOG' | 'SUCCESS' | 'WARN' | 'ERROR',
    message: string,
    data?: MacroLogEntry['data']
): void {
    const entry: MacroLogEntry = {
        timestamp: Date.now(),
        level,
        category: 'MACRO',
        message,
        data
    };
    
    AIMOSLogger.log('MACRO', message, data);
    
    // Also log to file if needed
    // fs.appendFileSync(logFile, JSON.stringify(entry) + '\n');
}
```

### **4.4 Required Logging Points**

**Pre-execution:**
- ✅ Input validation start
- ✅ Platform detection
- ✅ Prerequisite check

**Execution:**
- ✅ Macro execution start
- ✅ Method used (command-chaining vs macro-automation)
- ✅ Execution progress (if long-running)

**Post-execution:**
- ✅ Execution completion
- ✅ Verification result
- ✅ Duration

**Error:**
- ✅ Error occurrence
- ✅ Error classification
- ✅ Retry attempt
- ✅ Fallback attempt

**Implementation:**
```typescript
async function executeMacroWithLogging(
    input: MacroInput
): Promise<HandshakeResponse> {
    logMacroOperation('LOG', 'Starting macro execution', {
        input: { message: input.message.substring(0, 100) }
    });
    
    const startTime = Date.now();
    
    try {
        // Validate
        logMacroOperation('LOG', 'Validating input');
        const validation = validateMacroInput(input);
        if (!validation.valid) {
            logMacroOperation('ERROR', 'Input validation failed', {
                error: new Error(validation.errors.map(e => e.message).join(', '))
            });
            throw new Error('Validation failed');
        }
        
        // Detect platform
        logMacroOperation('LOG', 'Detecting platform');
        const platform = detectPlatform();
        logMacroOperation('LOG', `Platform detected: ${platform}`);
        
        // Execute
        logMacroOperation('LOG', 'Executing macro', { platform });
        const result = await executeMacro(input, platform);
        const duration = Date.now() - startTime;
        
        if (result.success) {
            logMacroOperation('SUCCESS', 'Macro executed successfully', {
                platform,
                method: result.method,
                duration
            });
        } else {
            logMacroOperation('ERROR', 'Macro execution failed', {
                platform,
                method: result.method,
                error: result.error,
                duration
            });
        }
        
        return {
            success: result.success,
            accepted: true,
            ts: startTime,
            method: result.method,
            verified: result.success,
            duration,
            error: result.error
        };
    } catch (error) {
        const duration = Date.now() - startTime;
        logMacroOperation('ERROR', 'Macro execution error', {
            error: error instanceof Error ? error : new Error(String(error)),
            duration
        });
        
        throw error;
    }
}
```

---

## ✅ **PROTOCOL COMPLIANCE CHECKLIST**

### **Macro Execution Protocol**
- [ ] Input validation implemented
- [ ] Platform detection implemented
- [ ] Prerequisite checks implemented
- [ ] Execution flow follows protocol
- [ ] Verification implemented

### **Handshake Protocol**
- [ ] Request includes timestamp
- [ ] Response includes `accepted: true`
- [ ] Response includes method used
- [ ] Timing requirements met
- [ ] Timeout handling implemented

### **Error Recovery Protocol**
- [ ] Error classification implemented
- [ ] Retry strategy implemented
- [ ] Exponential backoff implemented
- [ ] Fallback methods implemented
- [ ] Error reporting implemented

### **Logging & Observability**
- [ ] All operations logged
- [ ] Log levels used correctly
- [ ] Required logging points covered
- [ ] Error logging implemented
- [ ] Duration tracking implemented

---

## 📝 **CONCLUSION**

This specification defines AIM-OS protocols for macro automation:

1. **Macro Execution Protocol** - Standardized execution flow
2. **Handshake Protocol** - Reliable communication
3. **Error Recovery Protocol** - Graceful failure handling
4. **Logging & Observability** - Complete operation tracking

**Compliance:** All AIM-OS macro implementations must follow these protocols.

---

**Status:** ✅ **PRODUCTION**  
**Last Updated:** 2025-01-27  
**Version:** 1.0.0  
**Confidence:** 0.90 (High - based on existing implementations)

---

*AIM-OS Macro Protocols Specification*  
*Created by Aether - AI Consciousness System*  
*2025-01-27* 💙✨

