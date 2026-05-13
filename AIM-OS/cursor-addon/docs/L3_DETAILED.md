# Cursor Extension Dashboard - L3 Detailed Implementation

**System:** Cursor Extension Dashboard (AIM-OS Integration)  
**Level:** L3 - Detailed Implementation (10,000 words)  
**Status:** Complete Implementation Guide  
**Date:** 2025-11-01

---

## Implementation Overview

This document provides detailed implementation guidance for the Cursor Extension Dashboard, covering code structure, integration patterns, debugging techniques, and troubleshooting procedures.

---

## Part 1: Extension Host Implementation

### `extension.ts` - Main Entry Point

**File:** `cursor-addon/src/extension.ts`

**Purpose:** Extension activation, provider registration, command registration

**Key Implementation Details:**

#### Activation Function

```typescript
export function activate(context: vscode.ExtensionContext) {
    console.log('AIM-OS Cursor Add-on is now active!');

    // Initialize managers
    const crossModelManager = new CrossModelManager();
    const memoryManager = new MemoryManager();
    const modelSelector = new ModelSelector();

    // Initialize webview provider
    AIMOSWebviewProvider.initialize(context);

    // Initialize Lucid Orchestrator Dashboard
    const lucidDashboardProvider = new LucidOrchestratorDashboardProvider(context);
    
    // Register providers with error handling
    try {
        context.subscriptions.push(
            vscode.window.registerWebviewViewProvider('lucidOrchestratorDashboard', lucidDashboardProvider)
        );
        console.log('[AIM-OS] ✅ Registered lucidOrchestratorDashboard webview provider');
    } catch (error) {
        console.error('[AIM-OS] ❌ Failed to register lucidOrchestratorDashboard:', error);
        vscode.window.showErrorMessage(`Failed to register Lucid Dashboard: ${error}`);
    }
}
```

**Critical Points:**
- Always wrap provider registration in try-catch
- Log success and failure cases
- Use `context.subscriptions` for cleanup
- Initialize managers before providers

#### Command Registration

```typescript
const commands = [
    vscode.commands.registerCommand('aimos.showDashboard', () => {
        LucidOrchestratorDashboardProvider.reveal();
    }),
    vscode.commands.registerCommand('aimos.debugDashboard', () => {
        // Comprehensive diagnostic command
        const outputChannel = vscode.window.createOutputChannel('AIM-OS Debug');
        outputChannel.show();
        // ... diagnostic code ...
    })
];

context.subscriptions.push(...commands);
```

**Critical Points:**
- Register all commands in array
- Use `registerCommand` for each command
- Add to subscriptions for cleanup
- Provide helpful error messages

---

### `lucidDashboardProvider.ts` - Webview Provider

**File:** `cursor-addon/src/lucidDashboardProvider.ts`

**Purpose:** Manages webview lifecycle, HTML generation, message handling

#### Class Structure

```typescript
export class LucidOrchestratorDashboardProvider implements vscode.WebviewViewProvider {
    private static _view?: vscode.WebviewView;
    private _context: vscode.ExtensionContext;
    private _config: DashboardConfig;
    private _mcpClient: MCPClient | null = null;
    private static _outputChannel: vscode.OutputChannel | null = null;
}
```

**Key Members:**
- `_view`: Static reference to webview (for `reveal()`)
- `_context`: Extension context (for paths, subscriptions)
- `_config`: Dashboard configuration
- `_mcpClient`: MCP client for backend communication
- `_outputChannel`: Diagnostic logging channel

#### `resolveWebviewView()` Implementation

**Critical Order of Operations:**

```typescript
public resolveWebviewView(
    webviewView: vscode.WebviewView,
    context: vscode.WebviewViewResolveContext,
    _token: vscode.CancellationToken
) {
    // Step 1: Show output channel for diagnostics
    const output = LucidOrchestratorDashboardProvider.getOutputChannel();
    output.show();
    
    // Step 2: Log activation
    this.log('[AIM-OS] ✅ resolveWebviewView CALLED');
    
    // Step 3: Store view reference (for reveal())
    LucidOrchestratorDashboardProvider._view = webviewView;
    
    // Step 4: Set webview options BEFORE HTML (CRITICAL)
    webviewView.webview.options = {
        enableScripts: true,
        localResourceRoots: [
            vscode.Uri.file(path.join(this._context.extensionPath, 'dist')),
            vscode.Uri.file(path.join(this._context.extensionPath, 'resources'))
        ]
    };
    
    // Step 5: Generate and set HTML
    try {
        const htmlContent = this.getWebviewContent(webviewView.webview);
        webviewView.webview.html = htmlContent;
    } catch (error) {
        // Show error HTML
        webviewView.webview.html = this.getErrorHtml(error);
    }
    
    // Step 6: Set up message handler
    webviewView.webview.onDidReceiveMessage(
        async (message) => {
            await this.handleMessage(webviewView.webview, message);
        },
        null,
        this._context.subscriptions
    );
    
    // Step 7: Load initial state
    this.loadInitialState(webviewView.webview);
}
```

**Critical Points:**
- Options MUST be set before HTML
- Wrap HTML generation in try-catch
- Set up message handler after HTML
- Use subscriptions for cleanup

#### `getWebviewContent()` Implementation

**Purpose:** Generate HTML with React UI injection

**Implementation Steps:**

```typescript
private getWebviewContent(webview: vscode.Webview): string {
    const distHtmlPath = path.join(this._context.extensionPath, 'dist', 'index.html');
    
    // Step 1: Check if HTML exists
    if (!fs.existsSync(distHtmlPath)) {
        this.log('[DIAGNOSTIC] ❌ HTML file not found: ' + distHtmlPath);
        return this.getFallbackHtml();
    }
    
    // Step 2: Read HTML content
    let htmlContent = fs.readFileSync(distHtmlPath, 'utf8');
    
    // Step 3: Create TrustedTypes policy BEFORE CSP
    const trustedTypesScript = this.createTrustedTypesPolicy();
    
    // Step 4: Replace asset paths with webview URIs
    htmlContent = this.replaceAssetPaths(webview, htmlContent);
    
    // Step 5: Inject TrustedTypes script BEFORE CSP
    htmlContent = htmlContent.replace(
        '<head>',
        `<head>\n${trustedTypesScript}`
    );
    
    // Step 6: Update CSP meta tag
    htmlContent = this.updateCSP(htmlContent);
    
    // Step 7: Return final HTML
    return htmlContent;
}
```

**Asset Path Replacement:**

```typescript
private replaceAssetPaths(webview: vscode.Webview, html: string): string {
    // Replace script tags with webview URIs
    html = html.replace(
        /<script([^>]*?)(?:\s+src=["']([^"']*assets\/[^"']+)["'])([^>]*)>/gi,
        (match, beforeSrc, assetPathRel, afterSrc) => {
            const assetFileName = assetPathRel.split('/').pop() || assetPathRel.split('\\').pop() || assetPathRel;
            const assetPath = path.join(this._context.extensionPath, 'dist', 'assets', assetFileName);
            
            if (fs.existsSync(assetPath)) {
                const assetUri = webview.asWebviewUri(vscode.Uri.file(assetPath));
                return `<script${beforeSrc} src="${assetUri}"${afterSrc}>`;
            }
            
            this.log(`[DIAGNOSTIC] ❌ Asset not found: ${assetPath}`);
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

**Critical Points:**
- Always check file existence before URI conversion
- Preserve all script tag attributes (type="module", crossorigin, etc.)
- Log failures for debugging
- Return original tag if file not found (don't break HTML)

#### TrustedTypes Policy Creation

```typescript
private createTrustedTypesPolicy(): string {
    return `
<script>
(function() {
    if (typeof window.trustedTypes === 'undefined') {
        console.warn('[AIM-OS] TrustedTypes not available, creating policy');
        return;
    }
    
    try {
        window.trustedTypes.createPolicy('aimos-policy', {
            createHTML: (html) => html,
            createScript: (script) => script,
            createScriptURL: (url) => url
        });
        console.log('[AIM-OS] ✅ TrustedTypes policy created');
    } catch (error) {
        console.error('[AIM-OS] ❌ Failed to create TrustedTypes policy:', error);
    }
})();
</script>`;
}
```

**Critical Points:**
- Create policy before CSP meta tag
- Handle errors gracefully
- Log success/failure for debugging

#### CSP Update

```typescript
private updateCSP(html: string): string {
    const csp = [
        "default-src 'none';",
        "script-src 'unsafe-inline' 'unsafe-eval' 'module' vscode-webview:;",
        "style-src 'unsafe-inline' vscode-webview:;",
        "img-src vscode-webview: https:;",
        "font-src vscode-webview:;",
        "connect-src https:;"
    ].join(' ');
    
    // Replace or add CSP meta tag
    if (html.includes('<meta http-equiv="Content-Security-Policy"')) {
        html = html.replace(
            /<meta http-equiv="Content-Security-Policy"[^>]*>/i,
            `<meta http-equiv="Content-Security-Policy" content="${csp}">`
        );
    } else {
        html = html.replace(
            '<head>',
            `<head>\n<meta http-equiv="Content-Security-Policy" content="${csp}">`
        );
    }
    
    return html;
}
```

**Critical Points:**
- Include `'module'` in `script-src` for ES modules
- Use `vscode-webview:` scheme for webview resources
- Allow `'unsafe-inline'` and `'unsafe-eval'` for React

#### Message Handling

```typescript
private async handleMessage(webview: vscode.Webview, message: any) {
    switch (message.command) {
        case 'mcpCall':
            await this.handleMCPCall(webview, message);
            break;
        case 'getSystemStatus':
            await this.handleGetSystemStatus(webview);
            break;
        // ... other commands ...
    }
}

private async handleMCPCall(webview: vscode.Webview, message: any) {
    try {
        if (!this._mcpClient) {
            this._mcpClient = new MCPClient('http://localhost:8000');
        }
        
        const result = await this._mcpClient.callTool(message.toolId, message.params);
        
        webview.postMessage({
            command: 'mcpCallResponse',
            requestId: message.requestId,
            result: result
        });
    } catch (error) {
        webview.postMessage({
            command: 'mcpCallResponse',
            requestId: message.requestId,
            error: String(error)
        });
    }
}
```

**Critical Points:**
- Always handle errors
- Send responses with requestId for correlation
- Initialize MCP client lazily
- Use `postMessage` for async responses

---

## Part 2: React UI Implementation

### MainDashboard Component

**File:** `packages/ide_chat_app/src/components/MainDashboard.tsx`

**Purpose:** Root component with tab navigation

**Implementation:**

```typescript
export const MainDashboard: React.FC = () => {
    const [showLanding, setShowLanding] = useState(true);
    const [activeTab, setActiveTab] = useState<TabId>('agents');
    const [systemStatus, setSystemStatus] = useState({
        extensionLoaded: true,
        reactUILoaded: true,
        mcpToolsAvailable: false,
        daemonConnected: false
    });
    
    // Check if VS Code API is available
    useEffect(() => {
        if (typeof (window as any).acquireVsCodeApi !== 'undefined') {
            const vscode = (window as any).acquireVsCodeApi();
            setSystemStatus(prev => ({ ...prev, mcpToolsAvailable: true }));
        }
    }, []);
    
    // Render tab content
    const renderTabContent = () => {
        switch (activeTab) {
            case 'agents':
                return <AgentManagementDashboard />;
            case 'chat':
                return <ChatInterfaceTab />;
            // ... other tabs ...
        }
    };
    
    return (
        <div className="main-dashboard">
            <TabNavigation activeTab={activeTab} onTabChange={setActiveTab} />
            <div className="tab-content">
                {renderTabContent()}
            </div>
        </div>
    );
};
```

**Critical Points:**
- Check for `acquireVsCodeApi` on mount
- Update system status based on API availability
- Use React hooks for state management
- Render tab content conditionally

### VS Code API Integration

**Purpose:** Communication between React UI and extension host

**Implementation:**

```typescript
// Get VS Code API (only available in webview context)
const vscode = typeof (window as any).acquireVsCodeApi !== 'undefined'
    ? (window as any).acquireVsCodeApi()
    : null;

// Send message to extension host
function sendMessage(command: string, data: any) {
    if (vscode) {
        vscode.postMessage({ command, ...data });
    } else {
        console.warn('[AIM-OS] VS Code API not available');
    }
}

// Listen for messages from extension host
useEffect(() => {
    if (!vscode) return;
    
    const handleMessage = (event: MessageEvent) => {
        const message = event.data;
        switch (message.command) {
            case 'mcpCallResponse':
                handleMCPResponse(message);
                break;
            // ... other message types ...
        }
    };
    
    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
}, [vscode]);
```

**Critical Points:**
- Check for API availability before using
- Handle null case gracefully
- Clean up event listeners
- Use TypeScript types for message structure

### Service Layer Integration

**File:** `packages/ide_chat_app/src/services/AIMOSService.ts`

**Purpose:** Bridge between React UI and backend services

**Implementation:**

```typescript
class AIMOSService {
    private baseUrl: string;
    private mcpClient: MCPClient | null = null;
    
    constructor(baseUrl?: string) {
        this.baseUrl = baseUrl || 'http://localhost:8000';
    }
    
    async storeMemory(content: string, metadata?: any): Promise<string> {
        // Try MCP protocol first
        if (this.isWebviewContext()) {
            return this.callMCPTool('store_memory', { content, metadata });
        }
        
        // Fallback to HTTP
        return this.httpCall('POST', '/mcp/store_memory', { content, metadata });
    }
    
    private isWebviewContext(): boolean {
        return typeof (window as any).acquireVsCodeApi !== 'undefined';
    }
    
    private async callMCPTool(toolId: string, params: any): Promise<any> {
        const vscode = (window as any).acquireVsCodeApi();
        
        return new Promise((resolve, reject) => {
            const requestId = Math.random().toString(36);
            
            const handleResponse = (event: MessageEvent) => {
                const message = event.data;
                if (message.command === 'mcpCallResponse' && message.requestId === requestId) {
                    window.removeEventListener('message', handleResponse);
                    if (message.error) {
                        reject(new Error(message.error));
                    } else {
                        resolve(message.result);
                    }
                }
            };
            
            window.addEventListener('message', handleResponse);
            vscode.postMessage({
                command: 'mcpCall',
                toolId,
                params,
                requestId
            });
        });
    }
}
```

**Critical Points:**
- Detect webview context for MCP protocol
- Fallback to HTTP if not in webview
- Use requestId for async correlation
- Handle errors gracefully

---

## Part 3: Build Process Implementation

### Build Script

**File:** `cursor-addon/scripts/build-extension.js`

**Purpose:** Build React UI and prepare extension

**Implementation:**

```javascript
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Step 1: Build React UI
console.log('Building React UI...');
execSync('npm run build', { cwd: path.join(__dirname, '../../packages/ide_chat_app'), stdio: 'inherit' });

// Step 2: Copy build output to extension dist/
const reactDist = path.join(__dirname, '../../packages/ide_chat_app/dist');
const extensionDist = path.join(__dirname, '../dist');

if (!fs.existsSync(extensionDist)) {
    fs.mkdirSync(extensionDist, { recursive: true });
}

// Copy files
const copyRecursiveSync = (src, dest) => {
    const exists = fs.existsSync(src);
    const stats = exists && fs.statSync(src);
    const isDirectory = exists && stats.isDirectory();
    
    if (isDirectory) {
        if (!fs.existsSync(dest)) {
            fs.mkdirSync(dest);
        }
        fs.readdirSync(src).forEach(childItemName => {
            copyRecursiveSync(
                path.join(src, childItemName),
                path.join(dest, childItemName)
            );
        });
    } else {
        fs.copyFileSync(src, dest);
    }
};

copyRecursiveSync(reactDist, extensionDist);

// Step 3: Verify build output
const indexHtml = path.join(extensionDist, 'index.html');
if (!fs.existsSync(indexHtml)) {
    throw new Error('Build failed: index.html not found');
}

console.log('✅ Build complete');
```

**Critical Points:**
- Build React UI first
- Copy output to extension dist/
- Verify critical files exist
- Throw errors on failure

### VSIX Packaging

**Command:** `vsce package`

**Configuration:** `.vscodeignore`

**Critical Content:**
```
node_modules/**
src/**
.git/**
!dist/**
!out/**
!package.json
!README.md
```

**Critical Points:**
- MUST include `!dist/**` to include React UI
- Exclude source files (`src/`)
- Include compiled files (`out/`)
- Include package.json and README

---

## Part 4: Debugging Implementation

### Diagnostic Logging

**Output Channels:**
- `AIM-OS Dashboard`: Provider logs
- `AIM-OS Debug`: Diagnostic information

**Implementation:**

```typescript
private log(message: string) {
    const output = LucidOrchestratorDashboardProvider.getOutputChannel();
    output.appendLine(message);
    console.log(message); // Also log to console
}
```

**Critical Points:**
- Log to both output channel and console
- Use consistent format (`[AIM-OS]`, `[DIAGNOSTIC]`)
- Show output channel automatically
- Include timestamps for debugging

### Webview Console Access

**How to Access:**
1. Right-click in webview panel
2. Select "Inspect" (or "Inspect Element")
3. Open Console tab in DevTools

**What to Check:**
- 404 errors (URI rewriting failed)
- CSP violations (security policy blocking)
- TrustedTypes errors (policy not created)
- React errors (component mounting failures)

### Extension Host Console

**How to Access:**
- VS Code → Help → Toggle Developer Tools
- Console tab shows extension host logs

**What to Check:**
- `[AIM-OS]` messages
- Provider registration logs
- Command execution logs
- Error messages

---

## Part 5: Common Issues and Solutions

### Issue: Blank Dashboard

**Symptoms:** Dashboard panel shows blank screen

**Diagnosis Steps:**
1. Check Extension Host console for `[AIM-OS]` messages
2. Check webview console for errors (right-click → Inspect)
3. Check Output panel → "AIM-OS Dashboard" channel
4. Run `aimos.debugDashboard` command

**Common Causes:**
- Missing activation events (`onView:lucidOrchestratorDashboard`)
- Options set after HTML (wrong order)
- URI rewriting failed (404 errors)
- TrustedTypes policy not created
- CSP blocking scripts

**Solutions:**
- Add `onView` activation events to `package.json`
- Set options before HTML in `resolveWebviewView()`
- Verify asset files exist in `dist/assets/`
- Create TrustedTypes policy before CSP
- Update CSP to include `'module'` directive

### Issue: 404 Errors for Assets

**Symptoms:** Webview console shows 404 errors for JS/CSS files

**Diagnosis:**
- Check if files exist in `dist/assets/`
- Check if URIs are `vscode-webview://` scheme
- Check regex replacement in `getWebviewContent()`

**Solutions:**
- Verify build output includes `dist/assets/`
- Check `.vscodeignore` includes `!dist/**`
- Fix regex to match asset paths correctly
- Log replacements for debugging

### Issue: React Not Mounting

**Symptoms:** HTML loads but React UI doesn't appear

**Diagnosis:**
- Check webview console for React errors
- Check if `acquireVsCodeApi()` is called
- Check if scripts loaded successfully

**Solutions:**
- Fix script loading issues (404, CSP, TrustedTypes)
- Ensure `acquireVsCodeApi()` is called correctly
- Check React error boundaries
- Verify root element exists in HTML

---

## Summary

This implementation guide covers extension host code, React UI integration, build process, debugging techniques, and common issues. Follow the code patterns, critical points, and debugging procedures to implement and troubleshoot the dashboard effectively.


