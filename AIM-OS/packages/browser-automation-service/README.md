# Browser Automation Service

**Status:** 🚀 **IN DEVELOPMENT**  
**Version:** 0.1.0  
**Purpose:** Browser automation service for DAC V2 IDE to automate AI chat pages (ChatGPT, Claude, etc.)

---

## 🎯 **OVERVIEW**

This package provides browser automation capabilities using Puppeteer/Playwright for:
- Automating AI chat pages (ChatGPT, Claude, Gemini, etc.)
- Script-based automation execution
- Account and session management
- Element detection and interaction
- Screenshot capture and analysis

---

## 📋 **FEATURES**

- ✅ **Browser Control** - Launch, navigate, interact with browsers
- ✅ **Script Execution** - JSON-based automation scripts
- ✅ **Connection Management** - Secure account and session storage
- ✅ **Element Detection** - Visual and DOM-based element detection
- ✅ **Error Recovery** - Intelligent retry and fallback mechanisms
- ✅ **REST API** - Complete REST API for browser automation

---

## 🚀 **QUICK START**

### **Installation**

```bash
cd packages/browser-automation-service
npm install
npm run build
```

### **Start Server**

```bash
npm start
# Server runs on http://localhost:5002
```

### **Usage - Programmatic**

```typescript
import { BrowserService } from './services/browserService';
import { ScriptEngine } from './services/scriptEngine';
import { ConnectionManager } from './services/connectionManager';

// Initialize services
const browserService = new BrowserService();
const connectionManager = new ConnectionManager();
const scriptEngine = new ScriptEngine(browserService, connectionManager);

// Launch browser
const browserId = await browserService.launchBrowser({
  headless: false,
  viewport: { width: 1280, height: 720 }
});

// Execute script
const result = await scriptEngine.executeScript(browserId, script);
```

### **Usage - REST API**

```bash
# Launch browser
curl -X POST http://localhost:5002/api/browser/launch \
  -H "Content-Type: application/json" \
  -d '{"headless": false, "viewport": {"width": 1280, "height": 720}}'

# Navigate
curl -X POST http://localhost:5002/api/browser/navigate \
  -H "Content-Type: application/json" \
  -d '{"browserId": "browser_123", "url": "https://chat.openai.com"}'

# Execute script
curl -X POST http://localhost:5002/api/automation/execute \
  -H "Content-Type: application/json" \
  -d '{"browserId": "browser_123", "script": {...}}'
```

---

## 📚 **DOCUMENTATION**

- **Specification:** `knowledge_architecture/AETHER_MEMORY/BROWSER_AUTOMATION_PANEL_SPECIFICATION_T3.md`
- **Design:** `knowledge_architecture/systems/lucid-ide/backend-api-system/BROWSER_AUTOMATION_PANEL_DESIGN.md`
- **Implementation Plan:** `knowledge_architecture/systems/lucid-ide/backend-api-system/BROWSER_AUTOMATION_PANEL_IMPLEMENTATION_PLAN.md`

---

## 🏗️ **ARCHITECTURE**

```
src/
├── index.ts                    # Main entry point
├── services/
│   ├── browserService.ts       # Puppeteer/Playwright service
│   ├── scriptEngine.ts         # Script execution engine
│   ├── connectionManager.ts   # Account & session management
│   └── elementDetection.ts     # Element detection service
├── types/
│   ├── automation.ts           # TypeScript interfaces
│   └── api.ts                  # API request/response types
├── api/
│   ├── browser.ts               # Browser control endpoints
│   ├── automation.ts            # Automation endpoints
│   ├── scripts.ts               # Script management endpoints
│   └── connections.ts           # Connection management endpoints
└── utils/
    ├── validation.ts            # Input validation
    ├── encryption.ts            # Credential encryption
    └── logging.ts               # Logging utilities
```

---

## ✅ **STATUS**

**Phase 1.1:** ✅ Package structure created  
**Phase 1.2:** ✅ Browser service implementation complete  
**Phase 1.3:** ✅ Script engine implementation complete  
**Phase 1.4:** ✅ Connection manager implementation complete  
**Phase 1.5:** ✅ REST API endpoints complete

**Backend Service:** ✅ **COMPLETE** - Ready for frontend integration

---

## 📡 **API ENDPOINTS**

### **Browser Control**
- `POST /api/browser/launch` - Launch browser
- `POST /api/browser/navigate` - Navigate to URL
- `GET /api/browser/screenshot` - Capture screenshot
- `GET /api/browser/status` - Get browser status
- `GET /api/browser/viewport` - Get embeddable viewport URL (or `null` for screenshot fallback)
- `POST /api/browser/detect-elements` - Detect interactive page elements
- `POST /api/browser/close` - Close browser

### **Automation**
- `POST /api/automation/execute` - Execute inline script or saved `scriptId`
- `GET /api/automation/status` - Get execution status
- `GET /api/automation/metrics` - Get aggregated execution metrics
- `POST /api/automation/pause` - Pause execution
- `POST /api/automation/resume` - Resume execution
- `POST /api/automation/stop` - Stop execution

### **Script Management**
- `POST /api/scripts/save` - Save script
- `GET /api/scripts/list` - List scripts
- `GET /api/scripts/:id` - Get script
- `DELETE /api/scripts/:id` - Delete script

### **Connection Management**
- `POST /api/connections/save` - Save account
- `GET /api/connections/list` - List accounts
- `GET /api/connections/:id` - Get account
- `POST /api/connections/:id/load-session` - Load session
- `POST /api/connections/:id/save-session` - Save session from active browser
- `POST /api/connections/:id/verify-session` - Verify session validity in browser context
- `POST /api/connections/:id/link-vault` - Link account to server-side vault credential
- `POST /api/connections/:id/update-cookies` - Update cookies
- `DELETE /api/connections/:id` - Delete account

### **Credential Vault (Server-Side)**
- `POST /api/connections/vault/save` - Save encrypted credential secret
- `GET /api/connections/vault/list` - List vault entries (metadata only, no secret values)
- `GET /api/connections/vault/:id` - Get one vault entry summary
- `GET /api/connections/vault/:id/usage` - Read normalized usage stats + limits
- `POST /api/connections/vault/:id/check-limit` - Check projected quota impact (non-consuming)
- `POST /api/connections/vault/:id/record-usage` - Consume quota after successful operation (returns `429` on limit exceed)
- `PUT /api/connections/vault/:id` - Update vault entry label/secret/metadata
- `DELETE /api/connections/vault/:id` - Delete vault entry

Limiter behavior:
- Vault writes are serialized per credential ID to prevent lost usage increments under concurrent requests.
- Bridge routes gate before send, then record with non-enforcing mode after successful send so actual usage is still accounted if concurrent calls race the quota boundary.

### **MCP Bridge**
- `POST /api/bridge/send-prompt` - Send prompt through provider UI (fails fast on auth/challenge, optional vault quota gate)
- `POST /api/bridge/extract-response` - Extract latest model response
- `POST /api/bridge/full-session` - Launch + session-load + prompt flow (honors account-linked vault quota)
- `GET /api/bridge/providers` - List provider selector counts
- `GET /api/bridge/capabilities` - Provider capability matrix
- `GET /api/bridge/page-health` - DOM + selector health score
- `GET /api/bridge/web-diagnostics` - Deep diagnostics (auth gates, selector drift, HTTP/request failures, console/page errors)
- `POST /api/bridge/start-new-chat` - Start fresh provider conversation
- `POST /api/bridge/select-model` - Select model via provider UI
- `POST /api/bridge/cleanup-dom` - Remove older message nodes
- `POST /api/bridge/auto-rotate` - Auto-rotate to new chat on low page health

Authenticated gate lock (ChatGPT):
- `send-prompt` with `waitForResponse=true`, `extract-response`, and `full-session` now require explicit token `AUTH_READY`.
- Provide token via request body `authReadyToken` or header `x-aimos-auth-ready` (or `x-auth-ready-token`).
- Missing token returns `428` with `status: "PENDING_AUTH"`.

---

**Last Updated:** 2026-03-04  
**Next Step:** Session reliability hardening and validation

---

*Browser Automation Service*  
*Part of AIM-OS Project* 💙✨

