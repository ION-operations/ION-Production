# Cursor Extension Dashboard - L4 Complete Reference

**System:** Cursor Extension Dashboard (AIM-OS Integration)  
**Level:** L4 - Complete Reference (15,000+ words)  
**Status:** Complete Reference Documentation  
**Date:** 2025-11-01

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Reference](#architecture-reference)
3. [Implementation Reference](#implementation-reference)
4. [API Reference](#api-reference)
5. [Configuration Reference](#configuration-reference)
6. [Build Reference](#build-reference)
7. [Debugging Reference](#debugging-reference)
8. [Troubleshooting Reference](#troubleshooting-reference)
9. [Integration Reference](#integration-reference)
10. [Performance Reference](#performance-reference)
11. [Security Reference](#security-reference)
12. [Testing Reference](#testing-reference)
13. [Deployment Reference](#deployment-reference)
14. [Maintenance Reference](#maintenance-reference)

---

## System Overview

### Purpose

The Cursor Extension Dashboard provides AIM-OS consciousness infrastructure integration within Cursor IDE, enabling visualization and interaction with AI agents, memory, MCP tools, and system orchestration through a unified React-based UI.

### Key Features

- **6-Tab Dashboard:** Agents, Chat, Chains, Tools, Timeline, NL Tags
- **VS Code Webview Integration:** Native panel support with security layers
- **MCP Protocol Support:** Direct communication with AIM-OS backend
- **Real-time Updates:** Live system status and monitoring
- **Cross-Model Consciousness:** Integration with AIM-OS core systems

### System Status

- **Current Status:** 🚨 Critical Issues - Blank Dashboard Panel
- **Issues Identified:** 8 critical issues (packaging, activation, security, URI rewriting)
- **Fixes Applied:** 3 issues fixed (packaging, options order, TrustedTypes/CSP)
- **Remaining Work:** 5 issues need verification/fixing

---

## Architecture Reference

### System Layers

**Layer 1: VS Code Extension Host**
- Entry point: `extension.ts`
- Provider: `lucidDashboardProvider.ts`
- Managers: CrossModelManager, MemoryManager, ModelSelector
- MCP Client: Communication with backend

**Layer 2: Webview Panel**
- VS Code webview container (isolated context)
- HTML content with React UI injection
- Message passing bridge
- Security layers (TrustedTypes, CSP, webview URIs)

**Layer 3: React UI Application**
- Location: `packages/ide_chat_app/`
- Component: MainDashboard with 6 tabs
- Service layer: Backend communication
- State management: React hooks, context providers

**Layer 4: Backend Services**
- MCP Server (port 8000)
- Daemon System (port 5000)
- RAG MCP (port 8001)
- Core AIM-OS systems

### Component Architecture

#### Extension Host Components

**`extension.ts`**
- **Purpose:** Extension activation and lifecycle
- **Key Functions:**
  - `activate(context)`: Main entry point
  - Provider registration
  - Command registration
  - Manager initialization

**`lucidDashboardProvider.ts`**
- **Purpose:** Webview lifecycle management
- **Key Methods:**
  - `resolveWebviewView()`: Called when panel opens
  - `getWebviewContent()`: Generates HTML with React UI
  - `handleMessage()`: Processes commands from React UI
  - `handleMCPCall()`: Forwards MCP tool calls to backend

#### React UI Components

**MainDashboard**
- **Location:** `packages/ide_chat_app/src/components/MainDashboard.tsx`
- **Purpose:** Root component with tab navigation
- **Tabs:** Agents, Chat, Chains, Tools, Timeline, NL Tags

**Service Layer**
- **Location:** `packages/ide_chat_app/src/services/`
- **Services:**
  - `AIMOSService.ts`: Core AIM-OS integration
  - `VoiceService.ts`: TTS/SST voice I/O
  - `HttpLucidDaemonService.ts`: Daemon communication

---

## Implementation Reference

### Extension Host Implementation

#### Activation Flow

```typescript
export function activate(context: vscode.ExtensionContext) {
    // 1. Initialize managers
    const crossModelManager = new CrossModelManager();
    const memoryManager = new MemoryManager();
    const modelSelector = new ModelSelector();
    
    // 2. Initialize providers
    const lucidDashboardProvider = new LucidOrchestratorDashboardProvider(context);
    
    // 3. Register providers
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider('lucidOrchestratorDashboard', lucidDashboardProvider)
    );
    
    // 4. Register commands
    const commands = [
        vscode.commands.registerCommand('aimos.showDashboard', () => {
            LucidOrchestratorDashboardProvider.reveal();
        })
    ];
    context.subscriptions.push(...commands);
}
```

#### Webview Provider Implementation

**`resolveWebviewView()` Method:**

```typescript
public resolveWebviewView(
    webviewView: vscode.WebviewView,
    context: vscode.WebviewViewResolveContext,
    _token: vscode.CancellationToken
) {
    // CRITICAL ORDER:
    // 1. Show output channel
    const output = LucidOrchestratorDashboardProvider.getOutputChannel();
    output.show();
    
    // 2. Store view reference
    LucidOrchestratorDashboardProvider._view = webviewView;
    
    // 3. Set options BEFORE HTML (CRITICAL)
    webviewView.webview.options = {
        enableScripts: true,
        localResourceRoots: [
            vscode.Uri.file(path.join(this._context.extensionPath, 'dist')),
            vscode.Uri.file(path.join(this._context.extensionPath, 'resources'))
        ]
    };
    
    // 4. Generate and set HTML
    const htmlContent = this.getWebviewContent(webviewView.webview);
    webviewView.webview.html = htmlContent;
    
    // 5. Set up message handler
    webviewView.webview.onDidReceiveMessage(
        async (message) => {
            await this.handleMessage(webviewView.webview, message);
        },
        null,
        this._context.subscriptions
    );
    
    // 6. Load initial state
    this.loadInitialState(webviewView.webview);
}
```

**`getWebviewContent()` Method:**

```typescript
private getWebviewContent(webview: vscode.Webview): string {
    const distHtmlPath = path.join(this._context.extensionPath, 'dist', 'index.html');
    
    // 1. Read HTML content
    let htmlContent = fs.readFileSync(distHtmlPath, 'utf8');
    
    // 2. Create TrustedTypes policy
    const trustedTypesScript = this.createTrustedTypesPolicy();
    
    // 3. Replace asset paths with webview URIs
    htmlContent = this.replaceAssetPaths(webview, htmlContent);
    
    // 4. Inject TrustedTypes script BEFORE CSP
    htmlContent = htmlContent.replace('<head>', `<head>\n${trustedTypesScript}`);
    
    // 5. Update CSP meta tag
    htmlContent = this.updateCSP(htmlContent);
    
    // 6. Return final HTML
    return htmlContent;
}
```

#### Asset Path Replacement

```typescript
private replaceAssetPaths(webview: vscode.Webview, html: string): string {
    // Replace script tags
    html = html.replace(
        /<script([^>]*?)(?:\s+src=["']([^"']*assets\/[^"']+)["'])([^>]*)>/gi,
        (match, beforeSrc, assetPathRel, afterSrc) => {
            const assetFileName = assetPathRel.split('/').pop() || assetPathRel.split('\\').pop() || assetPathRel;
            const assetPath = path.join(this._context.extensionPath, 'dist', 'assets', assetFileName);
            
            if (fs.existsSync(assetPath)) {
                const assetUri = webview.asWebviewUri(vscode.Uri.file(assetPath));
                return `<script${beforeSrc} src="${assetUri}"${afterSrc}>`;
            }
            
            return match; // Keep original if file doesn't exist
        }
    );
    
    // Replace CSS links similarly
    html = html.replace(
        /href=["']([^"']*assets\/[^"']+)["']/gi,
        (match, assetPathRel) => {
            const assetFileName = assetPathRel.split('/').pop() || assetPathRel.split('\\').pop() || assetPathRel;
            const assetPath = path.join(this._context.extensionPath, 'dist', 'assets', assetFileName);
            
            if (fs.existsSync(assetPath)) {
                const assetUri = webview.asWebviewUri(vscode.Uri.file(assetPath));
                return `href="${assetUri}"`;
            }
            
            return match;
        }
    );
    
    return html;
}
```

---

## API Reference

### Extension Host API

#### `LucidOrchestratorDashboardProvider`

**Static Methods:**
- `reveal()`: Reveal dashboard panel
- `getOutputChannel()`: Get diagnostic output channel

**Instance Methods:**
- `resolveWebviewView()`: Called when panel opens
- `getWebviewContent()`: Generates HTML content
- `handleMessage()`: Processes messages from webview
- `handleMCPCall()`: Forwards MCP tool calls

#### Message Protocol

**Webview → Extension Host:**
```typescript
{
    command: 'mcpCall',
    toolId: string,
    params: any,
    requestId: string
}
```

**Extension Host → Webview:**
```typescript
{
    command: 'mcpCallResponse',
    requestId: string,
    result?: any,
    error?: string
}
```

### React UI API

#### VS Code API Integration

```typescript
// Get VS Code API
const vscode = typeof (window as any).acquireVsCodeApi !== 'undefined'
    ? (window as any).acquireVsCodeApi()
    : null;

// Send message to extension host
vscode.postMessage({
    command: 'mcpCall',
    toolId: 'store_memory',
    params: { content: '...' },
    requestId: Math.random().toString(36)
});

// Listen for messages
window.addEventListener('message', (event) => {
    const message = event.data;
    if (message.command === 'mcpCallResponse') {
        // Handle response
    }
});
```

#### Service Layer API

**AIMOSService:**
```typescript
class AIMOSService {
    async storeMemory(content: string, metadata?: any): Promise<string>;
    async retrieveMemory(query: string): Promise<any>;
    async getMemoryStats(): Promise<any>;
    async trackConfidence(confidence: number, context: string): Promise<void>;
    async createPlan(goal: string, steps: string[]): Promise<any>;
    async synthesizeKnowledge(topics: string[]): Promise<any>;
}
```

---

## Configuration Reference

### `package.json` Configuration

#### Activation Events

```json
"activationEvents": [
    "onView:lucidOrchestratorDashboard",
    "onCommand:aimos.showDashboard"
]
```

#### Views

```json
"views": {
    "aimos": [
        {
            "id": "lucidOrchestratorDashboard",
            "name": "Dashboard",
            "when": "workspaceFolderCount > 0",
            "icon": "$(dashboard)"
        }
    ]
}
```

#### View Containers

```json
"viewsContainers": {
    "activitybar": [
        {
            "id": "aimos",
            "title": "AIM-OS",
            "icon": "$(sparkle)"
        }
    ]
}
```

#### Commands

```json
"commands": [
    {
        "command": "aimos.showDashboard",
        "title": "Show Dashboard",
        "icon": "$(dashboard)"
    },
    {
        "command": "aimos.debugDashboard",
        "title": "Debug Dashboard"
    }
]
```

### User Configuration

```json
"configuration": {
    "properties": {
        "aimos.mcpServerPath": {
            "type": "string",
            "default": "",
            "description": "Path to MCP server executable"
        },
        "aimos.crossModelEnabled": {
            "type": "boolean",
            "default": true,
            "description": "Enable cross-model consciousness"
        }
    }
}
```

### `.vscodeignore` Configuration

**Critical:** Must include `!dist/**` to include React UI

```
node_modules/**
src/**
.git/**
!dist/**
!out/**
!package.json
!README.md
```

---

## Build Reference

### Build Process

**Step 1: Build React UI**
```bash
cd packages/ide_chat_app
npm run build
```

**Step 2: Copy to Extension**
```bash
# Build script copies dist/ to cursor-addon/dist/
cd cursor-addon
npm run build
```

**Step 3: Compile Extension**
```bash
npm run compile
# Compiles TypeScript to out/extension.js
```

**Step 4: Package VSIX**
```bash
npm run package
# Creates aimos-cursor-addon.vsix
```

**Step 5: Install**
```bash
npm run install
# Installs VSIX to Cursor
```

### Build Scripts

**`scripts/build-extension.js`:**
- Builds React UI
- Copies to `cursor-addon/dist/`
- Verifies build output

**`tsconfig.json`:**
- Compiles TypeScript to `out/`
- Skips lib checks (avoids d3-dispatch errors)
- Includes VS Code API types

---

## Debugging Reference

### Diagnostic Tools

#### Output Channels

**"AIM-OS Dashboard":**
- Provider logs
- Activation events
- HTML generation logs

**"AIM-OS Debug":**
- Comprehensive diagnostics
- File verification
- Path checks

#### Console Access

**Extension Host Console:**
- VS Code → Help → Toggle Developer Tools
- Console tab shows extension host logs
- Look for `[AIM-OS]` messages

**Webview Console:**
- Right-click dashboard → Inspect → Console
- Shows webview errors
- 404 errors, CSP violations, React errors

#### Debug Command

**`aimos.debugDashboard`:**
- Checks extension activation
- Verifies provider registration
- Checks file existence
- Shows comprehensive diagnostics

---

## Troubleshooting Reference

### Common Issues

**Issue #1: Blank Dashboard**
- **Causes:** Missing activation events, options order, URI rewriting
- **Solutions:** Add `onView` events, set options before HTML, fix URI rewriting

**Issue #2: 404 Errors**
- **Causes:** Files not in VSIX, URI rewriting failed
- **Solutions:** Check `.vscodeignore`, verify files exist, fix regex

**Issue #3: CSP Violations**
- **Causes:** Missing `'module'` directive, wrong URI scheme
- **Solutions:** Update CSP, include `'module'`, allow `vscode-webview:`

**Issue #4: TrustedTypes Errors**
- **Causes:** Policy not created, policy after CSP
- **Solutions:** Create policy before CSP, handle errors

**Issue #5: React Not Mounting**
- **Causes:** Scripts not loading, `acquireVsCodeApi()` fails
- **Solutions:** Fix script loading, check React initialization

### Diagnostic Checklist

1. ✅ Check extension activation
2. ✅ Check build output
3. ✅ Check webview console
4. ✅ Check extension host console
5. ✅ Run debug command

---

## Integration Reference

### Backend Integration

**MCP Server (port 8000):**
- Tool execution via MCP protocol
- Communication via `MCPClient`
- Message forwarding from React UI

**Daemon System (port 5000):**
- HTTP API for orchestration
- Real-time updates
- Status monitoring

**RAG MCP (port 8001):**
- Intelligent tool selection
- Semantic search
- Context reduction

### React UI Integration

**Service Layer:**
- `AIMOSService`: Core AIM-OS integration
- `VoiceService`: TTS/SST voice I/O
- `HttpLucidDaemonService`: Daemon communication

**Component Integration:**
- MainDashboard → Service layer → Backend
- Real-time updates via polling/WebSocket
- Error handling and fallbacks

---

## Performance Reference

### Loading Performance

**Target Metrics:**
- Extension activation: <100ms
- Webview creation: <50ms
- HTML generation: <10ms
- React UI mount: <500ms
- Total: <660ms

### Runtime Performance

**Target Metrics:**
- Message passing: <10ms
- MCP tool calls: <100ms
- UI updates: <16ms (60fps)

### Memory Usage

**Target Metrics:**
- Extension host: <50MB
- Webview: <100MB
- Total: <150MB

---

## Security Reference

### Security Layers

**Layer 1: TrustedTypes Policy**
- Prevents DOM XSS
- Must be created before CSP
- Allows HTML, Script, ScriptURL creation

**Layer 2: Content Security Policy**
- Prevents XSS and data injection
- Requires explicit permissions
- Includes `'module'` for ES modules

**Layer 3: Webview URI Scheme**
- `vscode-webview://` scheme required
- Prevents direct file system access
- Enforces resource whitelist

**Layer 4: Extension Isolation**
- Webview in isolated context
- Communication via messages only
- No direct DOM manipulation

---

## Testing Reference

### Unit Tests

**Extension Host:**
- Provider initialization
- Command registration
- Message handling

**React UI:**
- Component rendering
- State management
- Service layer integration

### Integration Tests

**Extension ↔ Webview:**
- Message passing
- State synchronization
- Error handling

**Extension ↔ Backend:**
- MCP tool execution
- HTTP API calls
- Authentication

### End-to-End Tests

**Full Workflow:**
- Extension activation
- Dashboard opening
- UI interaction
- Backend communication

---

## Deployment Reference

### Development

**Local Development:**
- `npm run watch`: TypeScript watch mode
- `npm run build`: Build React UI and extension
- `npm run install`: Package and install VSIX

### Production

**Packaging:**
- `npm run package`: Create VSIX
- Verify `.vscodeignore` includes `dist/`
- Check VSIX size (~880KB with React UI)

**Distribution:**
- VSIX file distribution
- Manual installation via `code --install-extension`
- Marketplace distribution (future)

---

## Maintenance Reference

### Regular Maintenance

**Weekly:**
- Check for build errors
- Verify extension activation
- Test dashboard functionality

**Monthly:**
- Update dependencies
- Review security policies
- Performance optimization

### Update Procedures

**Code Updates:**
1. Make changes to code
2. Run `npm run build`
3. Run `npm run package`
4. Test locally
5. Install update

**Dependency Updates:**
1. Update `package.json`
2. Run `npm install`
3. Test compatibility
4. Update if needed

---

## Summary

This complete reference provides comprehensive documentation for the Cursor Extension Dashboard, covering architecture, implementation, API, configuration, build, debugging, troubleshooting, integration, performance, security, testing, deployment, and maintenance. Use this reference for complete understanding and implementation guidance.


