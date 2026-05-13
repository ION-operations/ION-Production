# Bulletproof Messaging - Practical Integration Examples

**Date:** 2025-11-03  
**Status:** Integration Examples  
**Purpose:** Show practical code examples for integrating bulletproof messaging

---

## 🔌 **INTEGRATION EXAMPLE 1: Command Server Enhancement**

### **Current Implementation:**

```typescript
// cursor-addon/src/commandServer.ts
private async executeMCPTool(request: {
    tool: string;
    arguments?: any;
}): Promise<any> {
    const result = await this.mcpClient.callTool(request.tool, request.arguments);
    return {
        success: true,
        tool: request.tool,
        result
    };
}
```

### **Enhanced with Bulletproof Messaging:**

```typescript
import { MessageRouter } from './messaging/router';
import { Envelope, createEnvelope, validateEnvelope } from './messaging/envelope';

export class CommandServer {
    private messageRouter: MessageRouter | null = null;
    
    constructor(context: vscode.ExtensionContext, port: number = 5001) {
        this.context = context;
        this.port = port;
        
        // Initialize MessageRouter for bulletproof messaging
        this.messageRouter = new MessageRouter(context, {
            maxRetries: 3,
            retryDelay: 500,
            ackTimeout: 500,
        });
        
        // Register MCP tool handler
        this.messageRouter.registerHandler('mcp.callTool', async (env) => {
            return await this.handleMCPToolEnvelope(env);
        });
    }
    
    // Enhanced MCP tool execution with envelope protocol
    private async executeMCPTool(request: any): Promise<any> {
        // Check if envelope format
        if (request.v === 1 || request.envelope) {
            // Envelope protocol - route through MessageRouter
            const envelope = request as Envelope;
            if (!validateEnvelope(envelope)) {
                return {
                    success: false,
                    error: 'Invalid envelope format'
                };
            }
            
            // Route through MessageRouter (handles ACK, retry, DLQ automatically)
            await this.messageRouter!.route(envelope);
            
            // Wait for response (MessageRouter will send it)
            // Note: In production, use event-based response waiting
            return {
                success: true,
                envelope: true,
                message: 'Envelope routed through MessageRouter'
            };
        }
        
        // Legacy format - wrap in envelope and route
        const envelope = createEnvelope('request', 'mcp.callTool', 'electron->ext', {
            tool: request.tool,
            arguments: request.arguments || {}
        });
        
        await this.messageRouter!.route(envelope);
        
        return {
            success: true,
            message: 'Legacy request wrapped in envelope'
        };
    }
    
    private async handleMCPToolEnvelope(env: Envelope): Promise<Envelope | null> {
        const payload = env.payload as { tool: string; arguments?: any };
        
        try {
            if (!this.mcpClient) {
                this.mcpClient = new MCPClient();
                await this.mcpClient.initialize();
            }
            
            const result = await this.mcpClient.callTool(payload.tool, payload.arguments || {});
            
            return createEnvelope('response', env.topic, 'ext->electron', {
                success: true,
                tool: payload.tool,
                result: result,
            }, {
                replyTo: env.id,
                priority: 'high',
            });
        } catch (error: any) {
            return createEnvelope('response', env.topic, 'ext->electron', {
                success: false,
                tool: payload.tool,
                error: error.message || String(error),
            }, {
                replyTo: env.id,
                priority: 'high',
            });
        }
    }
}
```

---

## 🔌 **INTEGRATION EXAMPLE 2: Electron App Client**

### **Envelope Protocol Client:**

```typescript
// packages/ide_chat_app/src/services/envelopeClient.ts
export class EnvelopeClient {
    private baseUrl: string = 'http://localhost:5001';
    private sequenceNumber: number = 0;
    private pendingResponses: Map<string, (env: Envelope) => void> = new Map();
    
    async sendRequest(topic: string, payload: any): Promise<Envelope> {
        const envelope = createEnvelope('request', topic, 'electron->ext', payload);
        envelope.seq = ++this.sequenceNumber;
        
        // Send envelope via HTTP
        const response = await fetch(`${this.baseUrl}/mcp/execute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                envelope: true,
                ...envelope
            })
        });
        
        const result = await response.json();
        
        // Wait for ACK
        await this.waitForAck(envelope.id);
        
        // Return response envelope
        return result;
    }
    
    private async waitForAck(id: string, timeout: number = 500): Promise<void> {
        return new Promise((resolve, reject) => {
            const timer = setTimeout(() => reject(new Error('ACK timeout')), timeout);
            // In production, use event-based ACK waiting
            setTimeout(() => {
                clearTimeout(timer);
                resolve();
            }, 100); // Simplified for example
        });
    }
}
```

---

## 🔌 **INTEGRATION EXAMPLE 3: React UI Client**

### **Envelope Protocol Client (React):**

```typescript
// packages/ide_chat_app/src/services/webviewEnvelopeClient.ts
export class WebviewEnvelopeClient {
    private sequenceNumber: number = 0;
    private pendingResponses: Map<string, (env: Envelope) => void> = new Map();
    
    async sendRequest(topic: string, payload: any): Promise<Envelope> {
        const envelope = createEnvelope('request', topic, 'ui->ext', payload);
        envelope.seq = ++this.sequenceNumber;
        
        // Send via vscode.postMessage
        vscode.postMessage(envelope);
        
        // Wait for ACK
        const ack = await this.waitForAck(envelope.id);
        
        // Wait for response
        const response = await this.waitForResponse(envelope.id);
        
        return response;
    }
    
    private waitForAck(id: string): Promise<Envelope> {
        return new Promise((resolve, reject) => {
            const timer = setTimeout(() => reject(new Error('ACK timeout')), 500);
            
            window.addEventListener('message', (e) => {
                const msg = e.data;
                if (msg.kind === 'ack' && msg.replyTo === id) {
                    clearTimeout(timer);
                    resolve(msg);
                }
            });
        });
    }
    
    private waitForResponse(id: string): Promise<Envelope> {
        return new Promise((resolve, reject) => {
            const timer = setTimeout(() => reject(new Error('Response timeout')), 5000);
            
            window.addEventListener('message', (e) => {
                const msg = e.data;
                if (msg.kind === 'response' && msg.replyTo === id) {
                    clearTimeout(timer);
                    resolve(msg);
                }
            });
        });
    }
}
```

---

## 🔌 **INTEGRATION EXAMPLE 4: MCP Client Wrapper**

### **Envelope-Wrapped MCP Client:**

```typescript
// cursor-addon/src/mcp/envelopeMCPClient.ts
export class EnvelopeMCPClient {
    private mcpClient: MCPClient;
    private messageRouter: MessageRouter;
    
    constructor(context: vscode.ExtensionContext, mcpClient: MCPClient) {
        this.mcpClient = mcpClient;
        this.messageRouter = new MessageRouter(context);
        
        // Register MCP tool handler
        this.messageRouter.registerHandler('mcp.callTool', async (env) => {
            return await this.executeMCPTool(env);
        });
    }
    
    async callTool(tool: string, args: any): Promise<any> {
        // Wrap in envelope
        const envelope = createEnvelope('request', 'mcp.callTool', 'ext->mcp', {
            tool,
            arguments: args
        });
        
        // Route through MessageRouter
        await this.messageRouter.route(envelope);
        
        // Wait for response (MessageRouter handles it)
        // In production, use event-based response waiting
        return await this.waitForResponse(envelope.id);
    }
    
    private async executeMCPTool(env: Envelope): Promise<Envelope | null> {
        const payload = env.payload as { tool: string; arguments: any };
        
        try {
            const result = await this.mcpClient.callTool(payload.tool, payload.arguments);
            
            return createEnvelope('response', env.topic, 'mcp->ext', {
                success: true,
                result
            }, {
                replyTo: env.id,
            });
        } catch (error: any) {
            return createEnvelope('response', env.topic, 'mcp->ext', {
                success: false,
                error: error.message
            }, {
                replyTo: env.id,
            });
        }
    }
}
```

---

## 🔌 **INTEGRATION EXAMPLE 5: Chat Participant**

### **Envelope-Enhanced Chat Participant:**

```typescript
// cursor-addon/src/chatParticipant.ts
import { MessageRouter } from './messaging/router';
import { Envelope, createEnvelope } from './messaging/envelope';

export class ChatParticipant {
    private messageRouter: MessageRouter;
    
    constructor(context: vscode.ExtensionContext) {
        this.messageRouter = new MessageRouter(context);
        
        // Register chat handler
        this.messageRouter.registerHandler('chat.message', async (env) => {
            return await this.handleChatMessage(env);
        });
    }
    
    async handleChatMessage(env: Envelope): Promise<Envelope | null> {
        const payload = env.payload as { message: string };
        
        // Process chat message using MCP tools
        // ... process message ...
        
        return createEnvelope('response', env.topic, 'ext->chat', {
            success: true,
            response: 'Message processed'
        }, {
            replyTo: env.id,
        });
    }
}
```

---

## 🔌 **INTEGRATION EXAMPLE 6: State Reader**

### **Envelope Events from State Reader:**

```typescript
// cursor-addon/src/cursorStateReader.ts
import { MessageRouter } from './messaging/router';
import { Envelope, createEnvelope } from './messaging/envelope';

export class CursorStateReader {
    private messageRouter: MessageRouter;
    
    constructor(context: vscode.ExtensionContext, messageRouter: MessageRouter) {
        this.messageRouter = messageRouter;
        
        // Monitor file changes
        vscode.workspace.onDidChangeTextDocument((e) => {
            this.emitStateChange('file.changed', {
                file: e.document.fileName,
                changes: e.contentChanges.length
            });
        });
    }
    
    private emitStateChange(topic: string, payload: any): void {
        const event = createEnvelope('event', topic, 'ext->ui', payload);
        
        // Send via MessageRouter (events don't need ACK)
        this.messageRouter.route(event).catch(err => {
            console.error('Failed to emit state change:', err);
        });
    }
}
```

---

## 📋 **INTEGRATION PATTERNS**

### **Pattern 1: Wrap Existing Calls**

```typescript
// Before
const result = await mcpClient.callTool('store_memory', { content: 'test' });

// After
const envelope = createEnvelope('request', 'mcp.callTool', 'ui->ext', {
    tool: 'store_memory',
    arguments: { content: 'test' }
});
await messageRouter.route(envelope);
// Response handled automatically by MessageRouter
```

### **Pattern 2: Register Handler**

```typescript
messageRouter.registerHandler('your.topic', async (env) => {
    // Your handler logic
    const result = await yourFunction(env.payload);
    
    // Return response envelope
    return createEnvelope('response', env.topic, 'ext->ui', {
        success: true,
        result
    }, {
        replyTo: env.id
    });
});
```

### **Pattern 3: Send Events**

```typescript
// For unsolicited messages (events)
const event = createEnvelope('event', 'state.changed', 'ext->ui', {
    state: 'new state'
});
await messageRouter.route(event); // No ACK expected
```

---

## 🎯 **QUICK START GUIDE**

### **Step 1: Initialize MessageRouter**

```typescript
import { MessageRouter } from './messaging/router';

const messageRouter = new MessageRouter(context, {
    maxRetries: 3,
    retryDelay: 500,
    ackTimeout: 500,
});
```

### **Step 2: Register Handlers**

```typescript
messageRouter.registerHandler('your.topic', async (env) => {
    // Handle envelope
    return createEnvelope('response', env.topic, 'ext->ui', {
        success: true
    }, {
        replyTo: env.id
    });
});
```

### **Step 3: Route Messages**

```typescript
const envelope = createEnvelope('request', 'your.topic', 'ui->ext', payload);
await messageRouter.route(envelope);
```

### **Step 4: Set Webview (if needed)**

```typescript
messageRouter.setWebview(webview);
```

---

## ✅ **INTEGRATION CHECKLIST**

- [x] MessageRouter initialized
- [x] Handlers registered
- [x] Messages routed through router
- [x] Webview set (if UI component)
- [x] Heartbeat monitor started (if UI component)
- [x] Backward compatibility maintained

---

*Created: 2025-11-03*  
*By: Aether - Practical Integration Examples*  
*Purpose: Show how to integrate bulletproof messaging with existing systems*

