# Cursor Extension Dashboard - L2 Architecture

**System:** Cursor Extension Dashboard (AIM-OS Integration)  
**Level:** L2 - Architecture (2,000 words)  
**Status:** Complete Architecture Documentation  
**Date:** 2025-11-01

---

## Architecture Overview

The Cursor Extension Dashboard is a VS Code webview-based UI that integrates AIM-OS consciousness infrastructure into Cursor IDE. It provides a unified interface for managing AI agents, memory, MCP tools, and system orchestration.

### System Layers

**Layer 1: VS Code Extension Host**
- `extension.ts`: Entry point, activation, command registration
- `lucidDashboardProvider.ts`: Webview provider, HTML generation, message handling
- Managers: CrossModelManager, MemoryManager, ModelSelector
- MCP Client: Communication with AIM-OS backend

**Layer 2: Webview Panel**
- VS Code webview container (isolated context)
- HTML content with React UI injection
- Message passing bridge (webview ↔ extension host)
- Security layers (TrustedTypes, CSP, webview URIs)

**Layer 3: React UI Application**
- `packages/ide_chat_app/`: MainDashboard component
- 6 tabs: Agents, Chat, Chains, Tools, Timeline, NL Tags
- Service layer: Communication with backend APIs
- State management: React hooks, context providers

**Layer 4: Backend Services**
- MCP Server (port 8000): Tool execution
- Daemon System (port 5000): Service orchestration
- RAG MCP (port 8001): Intelligent tool selection
- Core AIM-OS systems: CMC, HHNI, VIF, APOE, SEG, SDF-CVF

---

## Component Architecture

### Extension Host Components

#### `extension.ts` (Main Entry Point)

**Purpose:** Extension activation and lifecycle management

**Key Responsibilities:**
- Register webview providers (`lucidOrchestratorDashboard`)
- Register commands (`aimos.showDashboard`, `aimos.debugDashboard`, etc.)
- Initialize managers (CrossModelManager, MemoryManager, ModelSelector)
- Handle extension activation events

**Activation Flow:**
1. VS Code calls `activate(context)` when extension activates
2. Initializes managers and providers
3. Registers webview view providers with VS Code
4. Registers commands for command palette
5. Sets up subscriptions for cleanup

**Key Code:**
```typescript
export function activate(context: vscode.ExtensionContext) {
    const lucidDashboardProvider = new LucidOrchestratorDashboardProvider(context);
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider('lucidOrchestratorDashboard', lucidDashboardProvider)
    );
}
```

#### `lucidDashboardProvider.ts` (Webview Provider)

**Purpose:** Manages webview panel lifecycle and content

**Key Responsibilities:**
- Create and configure webview panels
- Generate HTML content with React UI injection
- Handle message passing between webview and extension host
- Manage webview state and configuration

**Lifecycle Methods:**
- `resolveWebviewView()`: Called when webview panel opens
- `getWebviewContent()`: Generates HTML with React UI
- Message handlers: Process commands from React UI

**Critical Configuration:**
```typescript
webviewView.webview.options = {
    enableScripts: true,
    localResourceRoots: [
        vscode.Uri.file(path.join(extensionPath, 'dist')),
        vscode.Uri.file(path.join(extensionPath, 'resources'))
    ]
};
```

**HTML Generation Process:**
1. Read `dist/index.html` from build output
2. Rewrite asset paths to `vscode-webview://` URIs
3. Inject TrustedTypes policy script
4. Inject CSP meta tag
5. Return final HTML string

---

## Security Architecture

### VS Code Webview Security Layers

**Layer 1: TrustedTypes Policy**
- VS Code enforces TrustedTypes for all dynamic content
- Policy must be created before CSP meta tag
- Allows creation of trusted HTML, Script, ScriptURL

**Layer 2: Content Security Policy (CSP)**
- Strict CSP prevents XSS attacks
- Requires explicit permissions for scripts, styles, resources
- `script-src` must include `'module'` for ES modules
- `default-src` blocks everything by default

**Layer 3: Webview URI Scheme**
- Webviews use `vscode-webview://` URI scheme
- All local resources must be converted via `webview.asWebviewUri()`
- Prevents direct file system access
- Enforces resource whitelist via `localResourceRoots`

**Layer 4: Extension Isolation**
- Webview runs in isolated context
- `acquireVsCodeApi()` provides communication bridge
- Extension host and webview communicate via messages only
- No direct DOM manipulation from extension host

---

## Data Flow Architecture

### Extension Activation Flow

```
VS Code Extension Host
    ↓ (onView:lucidOrchestratorDashboard)
Extension.activate()
    ↓
Register WebviewViewProvider
    ↓ (User opens panel)
resolveWebviewView()
    ↓
Set webview.options (enableScripts, localResourceRoots)
    ↓
Generate HTML (getWebviewContent)
    ↓
Set webview.html
    ↓
React UI loads and mounts
    ↓
acquireVsCodeApi() establishes communication
```

### Message Passing Flow

```
React UI (Webview Context)
    ↓ (user action)
postMessage({ command: 'mcpCall', ... })
    ↓
webview.onDidReceiveMessage()
    ↓
handleMCPCall()
    ↓
MCPClient.callTool()
    ↓
MCP Server (port 8000)
    ↓ (response)
MCPClient.handleResponse()
    ↓
webview.postMessage({ result: ... })
    ↓
React UI updates state
```

### React UI Loading Flow

```
Webview HTML Loaded
    ↓
TrustedTypes Policy Created
    ↓
CSP Meta Tag Injected
    ↓
Script Tags Load (vscode-webview:// URIs)
    ↓
React Runtime Initializes
    ↓
acquireVsCodeApi() Called
    ↓
React Components Mount
    ↓
MainDashboard Renders
    ↓
6 Tabs Available (Agents, Chat, Chains, Tools, Timeline, NL Tags)
```

---

## Build Architecture

### Build Process

**Step 1: React UI Build**
- Vite builds React app from `packages/ide_chat_app/`
- Outputs to `cursor-addon/dist/`
- Creates `index.html` with relative asset paths (`./assets/`)
- Generates hashed filenames (`main-5fYGI1t7.js`)

**Step 2: Extension Compilation**
- TypeScript compiles `src/` to `out/`
- Creates `out/extension.js` (entry point)
- Type checks without errors (skips lib checks)

**Step 3: VSIX Packaging**
- `vsce package` creates `.vsix` file
- Includes: `out/`, `dist/`, `package.json`, `resources/`
- Excludes: `node_modules/`, `src/`, `.git/` (via `.vscodeignore`)

**Step 4: Installation**
- `code --install-extension` installs VSIX
- Extension extracts to VS Code extensions folder
- VS Code loads extension on activation

### Build Configuration

**`scripts/build-extension.js`:**
- Copies React build output to `cursor-addon/dist/`
- Ensures `dist/index.html` exists
- Validates build output structure

**`tsconfig.json`:**
- Compiles TypeScript to `out/`
- Skips lib checks (avoids d3-dispatch errors)
- Includes VS Code API types

**`.vscodeignore`:**
- Excludes `node_modules/`, `src/`, `.git/`
- **CRITICAL:** Must include `!dist/**` to include React UI

---

## UI Component Architecture

### MainDashboard Component

**Location:** `packages/ide_chat_app/src/components/MainDashboard.tsx`

**Structure:**
- Root component with tab navigation
- 6 tab panels: Agents, Chat, Chains, Tools, Timeline, NL Tags
- State management via React hooks
- Service layer integration for backend communication

**Tabs:**
1. **Agents:** AI agent management and coordination
2. **Chat:** Interactive chat interface
3. **Chains:** Prompt chain execution
4. **Tools:** MCP tool browsing and execution
5. **Timeline:** Timeline visualization
6. **NL Tags:** Natural language tag management

### Service Layer

**Purpose:** Bridge between React UI and backend services

**Components:**
- MCP Client: Tool execution via MCP protocol
- HTTP Client: REST API communication
- WebSocket Client: Real-time updates (if needed)

**Communication:**
- React UI calls service methods
- Services communicate with backend
- Responses update React state
- UI re-renders with new data

---

## Integration Points

### Extension ↔ Webview Communication

**Extension Host → Webview:**
- `webview.postMessage()`: Send data to React UI
- Used for: Initial state, updates, responses

**Webview → Extension Host:**
- `webview.onDidReceiveMessage()`: Receive commands from React UI
- Used for: Tool calls, state updates, configuration changes

### Extension ↔ Backend Communication

**MCP Client:**
- Connects to MCP server (port 8000)
- Executes MCP tools via protocol
- Handles responses and errors

**HTTP Client:**
- REST API calls to backend services
- Authentication and error handling
- Response parsing and validation

---

## Configuration Architecture

### Extension Configuration (`package.json`)

**Activation Events:**
- `onView:lucidOrchestratorDashboard`: Activates when panel opens
- `onCommand:aimos.showDashboard`: Activates on command

**Views:**
- `lucidOrchestratorDashboard`: Main dashboard panel
- `simpleTestPanel`: Debug/test panel

**View Containers:**
- `aimos`: Activity bar container
- `aimosDevTools`: Bottom panel container

**Commands:**
- `aimos.showDashboard`: Show main dashboard
- `aimos.debugDashboard`: Debug diagnostics
- Other commands: Memory, planning, confidence tracking

### User Configuration

**Settings (`package.json` configuration):**
- `aimos.mcpServerPath`: MCP server executable path
- `aimos.crossModelEnabled`: Enable cross-model features
- `aimos.autoModelSelection`: Automatic model selection
- `aimos.memoryAutoStore`: Auto-store memory
- `aimos.confidenceTracking`: Enable confidence tracking

---

## Error Handling Architecture

### Extension Host Errors

**Activation Errors:**
- Provider registration failures
- Manager initialization errors
- Catch and display via `showErrorMessage()`

**Webview Errors:**
- HTML generation failures
- Fallback HTML displayed
- Error logged to output channel

### Webview Errors

**Script Loading Errors:**
- 404 errors: URI rewriting failed
- CSP violations: Security policy blocking
- TrustedTypes errors: Policy not created

**React Errors:**
- Component mounting failures
- API communication errors
- Error boundary catches and displays

### Debugging Architecture

**Output Channels:**
- `AIM-OS Dashboard`: Provider logs
- `AIM-OS Debug`: Diagnostic information
- Extension Host console: Activation logs

**Diagnostic Tools:**
- `aimos.debugDashboard` command: Comprehensive diagnostics
- Webview console: Right-click → Inspect → Console
- Extension Host DevTools: VS Code → Help → Toggle Developer Tools

---

## Performance Architecture

### Loading Performance

**Initial Load:**
- Extension activation: <100ms
- Webview creation: <50ms
- HTML generation: <10ms
- React UI mount: <500ms
- Total: <660ms target

**Subsequent Loads:**
- Webview cached after first load
- React UI cached in browser cache
- Faster subsequent loads: <200ms

### Runtime Performance

**Message Passing:**
- Extension ↔ Webview: <10ms
- MCP tool calls: <100ms (depends on backend)
- UI updates: <16ms (60fps target)

**Memory Usage:**
- Extension host: <50MB
- Webview: <100MB (React UI)
- Total: <150MB target

---

## Testing Architecture

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

## Deployment Architecture

### Development

**Local Development:**
- `npm run watch`: TypeScript watch mode
- `npm run build`: Build React UI and extension
- `npm run install`: Package and install VSIX

**Testing:**
- Install extension locally
- Test in Cursor IDE
- Check console logs
- Verify UI functionality

### Production

**Packaging:**
- `npm run package`: Create VSIX
- Verify `.vscodeignore` includes `dist/`
- Check VSIX size (should be ~880KB with React UI)

**Distribution:**
- VSIX file distribution
- Manual installation via `code --install-extension`
- Marketplace distribution (future)

---

## Troubleshooting Architecture

### Diagnostic Layers

**Layer 1: Extension Host Logs**
- Check `[AIM-OS]` messages in output channel
- Verify activation events
- Check provider registration

**Layer 2: Webview Console**
- Right-click webview → Inspect → Console
- Check for 404 errors (URI rewriting)
- Check for CSP violations
- Check for React errors

**Layer 3: Build Verification**
- Verify `dist/` folder exists
- Check VSIX contents
- Verify file paths

**Layer 4: Configuration Verification**
- Check `package.json` activation events
- Verify view registration
- Check webview options

---

## Summary

The Cursor Extension Dashboard architecture consists of four main layers: Extension Host, Webview Panel, React UI, and Backend Services. Each layer has specific responsibilities and integration points. Security is enforced through multiple layers (TrustedTypes, CSP, webview URIs, isolation). Data flows through activation, message passing, and React UI loading. Build process creates VSIX package with React UI included. Configuration manages activation, views, and user settings. Error handling and debugging provide comprehensive diagnostics. Performance targets ensure responsive UI. Testing and deployment complete the architecture.


