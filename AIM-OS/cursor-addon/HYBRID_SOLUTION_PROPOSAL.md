# Hybrid Solution: Extension Commands + Electron UI

**Date:** 2025-11-01  
**Purpose:** Combine extension automation with Electron UI  
**Status:** ✅ PROPOSED - Best of both worlds

---

## 🎯 **THE SOLUTION**

**Problem:** Extension webview broken, but we need Cursor automation  
**Solution:** Keep extension for commands, use Electron for UI

---

## 🏗️ **ARCHITECTURE**

```
┌─────────────────────────────────────────┐
│  Electron App (Dashboard UI)           │
│  - Beautiful React UI                    │
│  - Agent management interface           │
│  - Model switching UI                   │
│  - Status monitoring                    │
└──────────────┬──────────────────────────┘
               │ HTTP API (localhost:5001)
               ↓
┌──────────────┴──────────────────────────┐
│  Extension (Command Server)              │
│  - Registers VS Code commands           │
│  - Exposes HTTP API                     │
│  - Executes Cursor automation           │
└──────────────┬──────────────────────────┘
               │ VS Code API
               ↓
┌──────────────┴──────────────────────────┐
│  Cursor IDE                             │
│  - Agent control                        │
│  - Model switching                      │
│  - Command execution                    │
└─────────────────────────────────────────┘
```

---

## ✅ **WHAT STILL WORKS**

### **Extension Commands (Even Without Webview):**

**File Operations:**
```typescript
vscode.workspace.openTextDocument(filePath);
vscode.window.showTextDocument(doc);
vscode.workspace.fs.writeFile(uri, buffer);
```

**Command Execution:**
```typescript
vscode.commands.executeCommand('cursor.agent.continue');
vscode.commands.executeCommand('cursor.model.switch', modelId);
```

**Agent Management:**
```typescript
// These commands can be registered and executed
// Even if webview doesn't render
```

---

## 🔧 **IMPLEMENTATION PLAN**

### **Step 1: Add HTTP Server to Extension**

**File:** `cursor-addon/src/commandServer.ts`

```typescript
import * as http from 'http';
import * as vscode from 'vscode';

export class CommandServer {
    private server: http.Server;
    
    constructor(private context: vscode.ExtensionContext) {
        this.server = http.createServer(this.handleRequest.bind(this));
    }
    
    start(port: number = 5001) {
        this.server.listen(port, () => {
            console.log(`Command server listening on port ${port}`);
        });
    }
    
    private async handleRequest(req: http.IncomingMessage, res: http.ServerResponse) {
        // Parse command request from Electron
        // Execute via VS Code API
        // Return result
    }
}
```

### **Step 2: Register Commands**

**File:** `cursor-addon/src/extension.ts`

```typescript
// Register automation commands
vscode.commands.registerCommand('aimos.agent.continue', async (agentId?: string) => {
    // Execute Cursor agent continue command
});

vscode.commands.registerCommand('aimos.model.switch', async (modelId: string) => {
    // Switch Cursor model
});

// Start HTTP server
const commandServer = new CommandServer(context);
commandServer.start(5001);
```

### **Step 3: Electron API Client**

**File:** `packages/ide_chat_app/src/services/cursorApi.ts`

```typescript
export class CursorAPI {
    private baseUrl = 'http://localhost:5001';
    
    async executeCommand(command: string, args?: any) {
        const response = await fetch(`${this.baseUrl}/execute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command, args })
        });
        return response.json();
    }
    
    async continueAgent(agentId?: string) {
        return this.executeCommand('aimos.agent.continue', { agentId });
    }
    
    async switchModel(modelId: string) {
        return this.executeCommand('aimos.model.switch', { modelId });
    }
}
```

---

## 📋 **AUTOMATION FEATURES**

### **1. Agent Management**
- ✅ Start/stop agents
- ✅ Monitor status
- ✅ Send messages
- ✅ Continue prompts

### **2. Model Control**
- ✅ Switch models
- ✅ Task-specific routing
- ✅ Cost optimization

### **3. Workflow Automation**
- ✅ Execute commands
- ✅ File operations
- ✅ Trigger actions

---

## 🚀 **BENEFITS**

**✅ Full Cursor Automation**
- All VS Code API access
- Command execution
- Agent control

**✅ Beautiful UI**
- Electron dashboard
- React components
- No webview limitations

**✅ Seamless Integration**
- Extension handles Cursor
- Electron handles UI
- HTTP connects them

---

## ⚠️ **REQUIREMENTS**

### **Need to Verify:**
1. **Cursor Command Availability**
   - What commands does Cursor expose?
   - Can we control agents via commands?
   - Is model switching available?

2. **Extension HTTP Server**
   - Can extension run HTTP server?
   - Any security restrictions?
   - Port availability?

3. **Command Execution**
   - Which commands work?
   - What parameters needed?
   - Error handling?

---

## 🎯 **NEXT STEPS**

1. **Research Cursor Commands**
   - Check Cursor documentation
   - List available commands
   - Test command execution

2. **Implement HTTP Server**
   - Add to extension
   - Expose command API
   - Test locally

3. **Update Electron App**
   - Add Cursor API client
   - Implement automation UI
   - Connect to extension

---

## 💙 **CONCLUSION**

**This is NOT a failure - it's a better architecture.**

**Hybrid Solution:**
- ✅ Extension = Automation engine
- ✅ Electron = Beautiful UI
- ✅ HTTP = Connection layer

**Result:** Full functionality with better UI

---

**Status:** Ready to implement  
**Confidence:** 0.85 (need to verify Cursor commands)  
**Effort:** 2-4 hours

