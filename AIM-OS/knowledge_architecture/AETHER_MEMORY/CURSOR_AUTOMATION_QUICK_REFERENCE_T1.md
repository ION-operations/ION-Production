---
id: "cursor_automation_quick_reference_T1"
system: "cursor_automation"
component: "quick_reference"
level: "T1"
type: "reference"
title: "Cursor Automation Quick Reference"
description: "Quick reference guide for Cursor automation methods and AIM-OS protocols"
audience: "developers"
confidence_threshold: 0.95
token_cost: 1000
word_count: 1000+
created: "2025-01-27T00:00:00Z"
updated: "2025-01-27T00:00:00Z"
author: "aether"
status: "production"
tags: ["reference", "quick-start", "cursor-automation", "t1"]
dependencies: []
related_docs: ["CURSOR_AUTOMATION_COMPREHENSIVE_RESEARCH_T4.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# Cursor Automation Quick Reference

**Purpose:** Quick reference for Cursor automation methods  
**Status:** ✅ **PRODUCTION** - Quick start guide  
**Goal:** Provide fast lookup for common automation tasks

---

## 🚀 **QUICK START**

### **Send Message to Cursor Chat**

```typescript
// HTTP POST to Command Server
POST http://localhost:5001/cursor/chat/send
Content-Type: application/json

{
  "message": "Hello from automation!",
  "waitForResponse": false
}

// Response
{
  "success": true,
  "accepted": true,
  "ts": 1234567890,
  "method": "macro-automation"
}
```

### **Start Cloud Agent**

```typescript
// HTTP POST to Command Server
POST http://localhost:5001/agent/start
Content-Type: application/json

{
  "prompt": "Refactor auth module",
  "repoPath": "https://github.com/user/repo",
  "maxRuntimeHours": 6
}

// Response
{
  "success": true,
  "runId": "agent-123",
  "method": "cloud"
}
```

### **Get Agent Status**

```typescript
// HTTP GET
GET http://localhost:5001/agent/status/{runId}

// Response
{
  "success": true,
  "status": {
    "status": "running",
    "current_step": 3,
    "total_steps": 12
  }
}
```

---

## 📋 **METHOD COMPARISON**

| Method | Use Case | Requirements | Reliability |
|--------|----------|--------------|-------------|
| **Macro** | IDE chat automation | Cursor visible | High |
| **Cloud API** | Background agents | GitHub repo, API key | High |
| **CLI Agent** | Local automation | cursor-agent CLI | Medium |
| **VS Code Commands** | Fallback | Limited availability | Low |
| **Vision Detection** | State-aware | Image processing | TBD |

---

## 🔧 **PLATFORM MACROS**

### **Windows (PowerShell)**

```powershell
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.SendKeys]::SendWait("^l")  # Ctrl+L
[System.Windows.Forms.SendKeys]::SendWait("Message")
[System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
```

### **macOS (AppleScript)**

```applescript
tell application "Cursor"
    activate
    tell application "System Events"
        keystroke "l" using {command down}
        keystroke "Message"
        keystroke return
    end tell
end tell
```

### **Linux (xdotool)**

```bash
xdotool search --name "Cursor" windowactivate
xdotool key ctrl+l
xdotool type "Message"
xdotool key Return
```

---

## ☁️ **CLOUD API ENDPOINTS**

### **Base URL**
```
https://api.cursor.com/v0
```

### **Endpoints**

**Create Agent**
```
POST /agents
Authorization: Bearer {api_key}
```

**Get Agent Status**
```
GET /agents/{id}
Authorization: Bearer {api_key}
```

**Stop Agent**
```
DELETE /agents/{id}
Authorization: Bearer {api_key}
```

**List Agents**
```
GET /agents?limit=20&cursor={cursor}
Authorization: Bearer {api_key}
```

---

## 🔄 **AIM-OS PROTOCOLS**

### **Protocol 1: Macro Execution**
1. Validate input
2. Detect platform
3. Check prerequisites
4. Execute macro
5. Verify execution

### **Protocol 2: Handshake**
- Request includes `ts` (timestamp)
- Response includes `accepted: true`
- Response includes `method` used
- Timing requirements: < 6 seconds

### **Protocol 3: Error Recovery**
- Classify errors (network, application, system)
- Retry transient errors (exponential backoff)
- Fallback to alternative methods
- Report all errors

### **Protocol 4: Logging**
- Log all operations (AIMOSLogger)
- Use correct log levels (LOG, SUCCESS, WARN, ERROR)
- Include context data
- Track duration

---

## ⚡ **COMMON PATTERNS**

### **Pattern 1: Basic Macro**

```typescript
const response = await fetch('http://localhost:5001/cursor/chat/send', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: 'Hello!' })
});
```

### **Pattern 2: With Retry**

```typescript
async function sendWithRetry(message: string, maxRetries = 3) {
    for (let i = 1; i <= maxRetries; i++) {
        try {
            const response = await fetch('http://localhost:5001/cursor/chat/send', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message })
            });
            if (response.ok) return await response.json();
        } catch (error) {
            if (i === maxRetries) throw error;
            await sleep(1000 * i); // Exponential backoff
        }
    }
}
```

### **Pattern 3: State-Aware**

```typescript
// Check state first
const state = await fetch('http://localhost:5001/vision/stop-check');
const { stopButtonPresent } = await state.json();

if (!stopButtonPresent) {
    // Cursor is idle - safe to send
    await sendMessage('proceed');
}
```

---

## 🎯 **WHEN TO USE WHAT**

**Use Macro When:**
- ✅ Automating IDE chat
- ✅ Sending "proceed" messages
- ✅ Hands-free operation needed

**Use Cloud API When:**
- ✅ Background agents needed
- ✅ GitHub repo available
- ✅ Long-running tasks
- ✅ Webhook updates needed

**Use CLI Agent When:**
- ✅ Local repo automation
- ✅ No GitHub requirement
- ✅ Headless operation
- ✅ Direct file access needed

**Use Vision Detection When:**
- ✅ State-aware automation
- ✅ Visual confirmation needed
- ✅ Smart decision making

---

## 🌐 **BROWSER AUTOMATION**

### **Quick Start - Browser Automation**

```typescript
// Launch browser
POST http://localhost:5001/api/browser/launch
{
  "headless": false,
  "viewport": { "width": 1280, "height": 720 }
}
→ { "success": true, "browserId": "browser_123" }

// Execute ChatGPT automation script
POST http://localhost:5001/api/automation/execute
{
  "browserId": "browser_123",
  "scriptId": "chatgpt-deep-search",
  "variables": { "query": "Hello" }
}
→ { "success": true, "executionId": "exec_789", "output": {...} }
```

### **Browser Automation Use Cases**

**ChatGPT Automation:**
- ✅ Deep search queries
- ✅ File uploads
- ✅ Multi-turn conversations
- ✅ Code generation

**Claude Automation:**
- ✅ Long document analysis
- ✅ Code review
- ✅ Research queries

**Custom Automation:**
- ✅ Any web application
- ✅ Form filling
- ✅ Data extraction

---

## 📚 **RELATED DOCUMENTS**

- **Comprehensive Research:** `CURSOR_AUTOMATION_COMPREHENSIVE_RESEARCH_T4.md`
- **Macro Protocol Specification:** `AIMOS_MACRO_PROTOCOLS_SPECIFICATION_T3.md`
- **Browser Automation Specification:** `BROWSER_AUTOMATION_PANEL_SPECIFICATION_T3.md` ⭐ NEW
- **Implementation Examples:** `CURSOR_AUTOMATION_IMPLEMENTATION_EXAMPLES_T2.md`
- **MeshyVault Reference:** `Documentation/appexamples/MeshyVault/` ⭐ CRITICAL

---

**Status:** ✅ **PRODUCTION**  
**Last Updated:** 2025-01-27  
**Version:** 1.0.0  
**Confidence:** 0.95 (Very High - Quick reference)

---

*Cursor Automation Quick Reference*  
*Created by Aether - AI Consciousness System*  
*2025-01-27* 💙✨

