# Browser Automation Panel Design - DAC V2 IDE Integration

**Date:** 2025-01-27  
**Status:** 📋 **DESIGN PHASE**  
**Purpose:** Design browser automation panel for DAC V2 IDE to automate AI chat pages (ChatGPT, etc.)  
**Related Systems:** DAC V2 IDE, Macro Automation, Browser Panel Concept

---

## 🎯 **CORE REQUIREMENT**

Build a browser automation panel in DAC V2 IDE that:
- Shows a browser view (embedded browser)
- Can automate AI chat pages (ChatGPT, Claude, etc.)
- User signs into their own account
- Automates interactions to turn chat pages into APIs
- Supports file uploads, Google Cloud connections, etc.
- Enables use of subscribed/trial accounts with automation (e.g., deep searches)

**Use Case:** User wants to use their own ChatGPT/Claude subscriptions programmatically via automation instead of API access.

---

## 📚 **EXISTING DOCUMENTATION REVIEW**

### **1. Macro Automation Protocols** ✅

**Location:** `knowledge_architecture/AETHER_MEMORY/AIMOS_MACRO_PROTOCOLS_SPECIFICATION_T3.md`

**Key Capabilities:**
- ✅ Macro execution protocol (Windows PowerShell, macOS AppleScript, Linux xdotool)
- ✅ Handshake communication protocol
- ✅ Error recovery with retry logic
- ✅ Logging & observability
- ✅ Platform detection and prerequisite checks

**Relevance:** Browser automation can leverage macro protocols for keyboard/mouse automation when needed.

### **2. Browser Panel Concept** ✅

**Location:** `cursor-addon/docs/BROWSER_PANEL_CONCEPT.md`

**Key Capabilities:**
- ✅ Webview panel creation (`vscode.window.createWebviewPanel`)
- ✅ Embedded iframe browser
- ✅ URL navigation controls
- ✅ Multiple panel placement options (sidebar, bottom, editor tab)

**Relevance:** Foundation for browser panel UI in DAC V2 IDE.

### **3. DAC V2 IDE Architecture** ✅

**Location:** `knowledge_architecture/systems/router/DAC_V2_IDE_INTEGRATION_GUIDE.md`  
**Location:** `ide_orchestration/prototypes/dac/IDE_LAYOUT_PROTOTYPE_DAC.md`

**Key Features:**
- ✅ 5-zone flexible layout system (Left Drawer, Right Drawer, Bottom Drawer, Main Content, Top Bar)
- ✅ Drag-and-drop panel management
- ✅ Resizable panels (`react-resizable-panels`)
- ✅ Persistent state (Zustand store)
- ✅ Multiple panel types already integrated

**Relevance:** Browser automation panel will integrate into this flexible layout system.

### **4. Browser Automation Research** ✅

**Location:** `knowledge_architecture/applications/ide_chat_app/analysis/braden_previous_builds/insights/Stage1.md`

**Key Technologies:**
- ✅ Puppeteer (headless browser automation)
- ✅ Playwright (cross-browser automation)
- ✅ Selenium (browser automation)
- ✅ Stealth plugins for bot detection avoidance

**Relevance:** Core technologies for browser automation backend.

### **5. Visual Template Capture System** ✅

**Location:** `cursor-addon/VISUAL_TEMPLATE_CAPTURE_SYSTEM.md`

**Key Capabilities:**
- ✅ Screenshot capture (`desktopCapturer`)
- ✅ Region extraction (crop selected area)
- ✅ Template matching for UI element detection

**Relevance:** Can be used for visual element detection in browser automation.

---

## 🏗️ **ARCHITECTURE DESIGN**

### **System Architecture:**

```
┌─────────────────────────────────────────────────────────────┐
│  DAC V2 IDE (React Frontend)                               │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Browser Automation Panel (React Component)            │ │
│  │  - Browser View (iframe/webview)                     │ │
│  │  - Automation Controls                                │ │
│  │  - Script Editor                                      │ │
│  │  - Connection Manager                                 │ │
│  └───────────────────────────────────────────────────────┘ │
│                    ↕ HTTP API                              │
├─────────────────────────────────────────────────────────────┤
│  Browser Automation Backend (Node.js/Electron)             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Puppeteer/Playwright Service                          │ │
│  │  - Browser instance management                        │ │
│  │  - Page automation                                    │ │
│  │  - Element detection                                  │ │
│  │  - Action execution                                   │ │
│  └───────────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Automation Script Engine                              │ │
│  │  - Script parsing & execution                        │ │
│  │  - Macro integration                                 │ │
│  │  - Error handling                                    │ │
│  └───────────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Connection Manager                                    │ │
│  │  - Account management                                 │ │
│  │  - Session persistence                                │ │
│  │  - Cookie/credential storage                          │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### **Component Breakdown:**

#### **1. Browser Automation Panel (Frontend)**

**Location:** `ide_orchestration/prototypes/dac/src/panels/BrowserAutomationPanel.tsx`

**Features:**
- **Browser View:** Embedded browser using iframe or Electron webview
- **Automation Controls:** Start/stop/pause automation, step through actions
- **Script Editor:** Monaco editor for writing automation scripts
- **Connection Manager UI:** Manage accounts (ChatGPT, Claude, etc.)
- **File Upload UI:** Interface for file uploads to chat pages
- **Google Cloud Integration UI:** Connect Google Cloud services
- **Log Viewer:** Show automation logs and errors
- **Status Indicators:** Show automation status, current step, errors

**Panel Integration:**
- **Default Location:** Right Drawer → Top Section (or Bottom Section)
- **Panel ID:** `browser-automation`
- **Toolbar Button:** 🌐 (Globe icon) in right toolbar
- **Resizable:** Yes, via `react-resizable-panels`
- **Draggable:** Yes, can move to other zones

#### **2. Browser Automation Backend**

**Location:** `packages/browser-automation-service/` (new package)

**Core Services:**

**a) Puppeteer/Playwright Service**
```typescript
// packages/browser-automation-service/src/services/browserService.ts
import puppeteer from 'puppeteer';

export class BrowserService {
  private browser: Browser | null = null;
  private page: Page | null = null;

  async launchBrowser(options: BrowserOptions): Promise<void> {
    this.browser = await puppeteer.launch({
      headless: false, // Show browser for user interaction
      defaultViewport: { width: 1280, height: 720 },
      args: ['--disable-blink-features=AutomationControlled'] // Stealth
    });
    this.page = await this.browser.newPage();
  }

  async navigateTo(url: string): Promise<void> {
    await this.page?.goto(url, { waitUntil: 'networkidle2' });
  }

  async click(selector: string): Promise<void> {
    await this.page?.click(selector);
  }

  async type(selector: string, text: string): Promise<void> {
    await this.page?.type(selector, text);
  }

  async screenshot(): Promise<Buffer> {
    return await this.page?.screenshot() as Buffer;
  }

  async waitForElement(selector: string, timeout?: number): Promise<void> {
    await this.page?.waitForSelector(selector, { timeout });
  }
}
```

**b) Automation Script Engine**
```typescript
// packages/browser-automation-service/src/services/scriptEngine.ts

export interface AutomationAction {
  type: 'navigate' | 'click' | 'type' | 'wait' | 'upload' | 'screenshot' | 'extract';
  selector?: string;
  value?: string;
  url?: string;
  filePath?: string;
  timeout?: number;
}

export class ScriptEngine {
  async executeScript(actions: AutomationAction[]): Promise<ScriptResult> {
    const results: ActionResult[] = [];
    
    for (const action of actions) {
      try {
        const result = await this.executeAction(action);
        results.push(result);
      } catch (error) {
        return { success: false, error, completedActions: results };
      }
    }
    
    return { success: true, results };
  }

  private async executeAction(action: AutomationAction): Promise<ActionResult> {
    switch (action.type) {
      case 'navigate':
        await browserService.navigateTo(action.url!);
        break;
      case 'click':
        await browserService.click(action.selector!);
        break;
      case 'type':
        await browserService.type(action.selector!, action.value!);
        break;
      case 'wait':
        await browserService.waitForElement(action.selector!, action.timeout);
        break;
      // ... more action types
    }
  }
}
```

**c) Connection Manager**
```typescript
// packages/browser-automation-service/src/services/connectionManager.ts

export interface ChatAccount {
  id: string;
  provider: 'chatgpt' | 'claude' | 'gemini' | 'custom';
  email?: string;
  sessionCookies?: Cookie[];
  credentials?: EncryptedCredentials;
  lastUsed?: Date;
}

export class ConnectionManager {
  private accounts: Map<string, ChatAccount> = new Map();

  async saveAccount(account: ChatAccount): Promise<void> {
    // Store account with encrypted credentials
    this.accounts.set(account.id, account);
    await this.persistAccounts();
  }

  async loadSession(accountId: string): Promise<void> {
    const account = this.accounts.get(accountId);
    if (account?.sessionCookies) {
      await browserService.setCookies(account.sessionCookies);
    }
  }

  async persistAccounts(): Promise<void> {
    // Save to encrypted storage (CMC or local encrypted file)
  }
}
```

#### **3. API Endpoints**

**Location:** `packages/browser-automation-service/src/api/routes.ts`

```typescript
// HTTP API endpoints for frontend communication

// Browser control
POST /api/browser/launch
POST /api/browser/navigate
POST /api/browser/close
GET /api/browser/screenshot

// Automation
POST /api/automation/execute
POST /api/automation/pause
POST /api/automation/resume
POST /api/automation/stop
GET /api/automation/status

// Scripts
POST /api/scripts/save
GET /api/scripts/list
GET /api/scripts/:id
DELETE /api/scripts/:id

// Connections
POST /api/connections/save
GET /api/connections/list
GET /api/connections/:id
DELETE /api/connections/:id
POST /api/connections/:id/load-session

// File uploads
POST /api/files/upload
GET /api/files/list

// Google Cloud integration
POST /api/integrations/google-cloud/connect
GET /api/integrations/google-cloud/status
```

---

## 🎨 **UI DESIGN**

### **Browser Automation Panel Layout:**

```
┌─────────────────────────────────────────────────────────┐
│ Browser Automation Panel                                 │
├─────────────────────────────────────────────────────────┤
│ [🌐 Browser View - 70% height]                          │
│ ┌─────────────────────────────────────────────────────┐ │
│ │                                                       │ │
│ │  [Embedded Browser - ChatGPT/Claude/etc.]            │ │
│ │                                                       │ │
│ │                                                       │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                          │
│ [📝 Controls - 30% height]                             │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ [▶ Start] [⏸ Pause] [⏹ Stop] [⏭ Step]              │ │
│ │                                                      │ │
│ │ Connection: [ChatGPT ▼] [Load Session] [New]       │ │
│ │                                                      │ │
│ │ Script: [New Script ▼] [Edit] [Save]                │ │
│ │                                                      │ │
│ │ Status: 🟢 Running | Step: 3/10                     │ │
│ │                                                      │ │
│ │ [📁 File Upload] [☁️ Google Cloud]                   │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### **Script Editor Panel (Optional - Can be separate panel):**

```
┌─────────────────────────────────────────────────────────┐
│ Automation Script Editor                                 │
├─────────────────────────────────────────────────────────┤
│ [Monaco Editor]                                         │
│                                                          │
│ {                                                         │
│   "actions": [                                           │
│     { "type": "navigate", "url": "https://chat.openai.com" }, │
│     { "type": "wait", "selector": "#login-button" },    │
│     { "type": "click", "selector": "#login-button" },   │
│     { "type": "type", "selector": "#email", "value": "${email}" }, │
│     { "type": "type", "selector": "#password", "value": "${password}" }, │
│     { "type": "click", "selector": "#submit" },         │
│     { "type": "wait", "selector": ".chat-input" },       │
│     { "type": "type", "selector": ".chat-input", "value": "${message}" }, │
│     { "type": "click", "selector": ".send-button" },    │
│     { "type": "wait", "selector": ".response" },         │
│     { "type": "extract", "selector": ".response", "variable": "response" } │
│   ]                                                      │
│ }                                                         │
│                                                          │
│ [▶ Run Script] [💾 Save] [📋 Templates]                  │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 **INTEGRATION WITH DAC V2 IDE**

### **Panel Registration:**

**Location:** `ide_orchestration/prototypes/dac/src/components/IDELayout.tsx`

```typescript
// Add browser automation panel to right drawer
const rightDrawerPanels = {
  // ... existing panels
  'browser-automation': {
    component: LazyBrowserAutomationPanel,
    icon: '🌐',
    label: 'Browser Automation',
    defaultSection: 'top' // or 'bottom'
  }
};
```

### **Panel State Management:**

**Location:** `ide_orchestration/prototypes/dac/src/store/panelStore.ts`

```typescript
interface PanelState {
  // ... existing panels
  'browser-automation': {
    visible: boolean;
    zone: 'right';
    section: 'top' | 'bottom';
    size: number; // percentage
    browserUrl?: string;
    automationStatus?: 'idle' | 'running' | 'paused' | 'error';
    currentScript?: string;
    currentAccount?: string;
  };
}
```

---

## 📋 **AUTOMATION SCRIPTS**

### **Script Format (JSON):**

```json
{
  "name": "ChatGPT Deep Search",
  "description": "Automate ChatGPT for deep search queries",
  "provider": "chatgpt",
  "variables": {
    "email": "user@example.com",
    "password": "encrypted_password",
    "query": "{{query}}"
  },
  "actions": [
    {
      "type": "navigate",
      "url": "https://chat.openai.com",
      "waitUntil": "networkidle2"
    },
    {
      "type": "wait",
      "selector": "button[data-testid='login-button']",
      "timeout": 10000
    },
    {
      "type": "click",
      "selector": "button[data-testid='login-button']"
    },
    {
      "type": "wait",
      "selector": "input[name='email']",
      "timeout": 5000
    },
    {
      "type": "type",
      "selector": "input[name='email']",
      "value": "{{email}}"
    },
    {
      "type": "type",
      "selector": "input[name='password']",
      "value": "{{password}}"
    },
    {
      "type": "click",
      "selector": "button[type='submit']"
    },
    {
      "type": "wait",
      "selector": "textarea[data-id='root']",
      "timeout": 15000
    },
    {
      "type": "type",
      "selector": "textarea[data-id='root']",
      "value": "{{query}}"
    },
    {
      "type": "click",
      "selector": "button[data-testid='send-button']"
    },
    {
      "type": "wait",
      "selector": ".markdown",
      "timeout": 30000
    },
    {
      "type": "extract",
      "selector": ".markdown",
      "variable": "response"
    }
  ],
  "output": {
    "response": "{{response}}"
  }
}
```

### **Script Templates:**

**ChatGPT Templates:**
- Basic chat query
- Deep search with follow-ups
- File upload + query
- Code generation

**Claude Templates:**
- Long document analysis
- Code review
- Research queries

**Custom Templates:**
- User-defined templates
- Template sharing

---

## 🔐 **SECURITY & PRIVACY**

### **Credential Storage:**

- **Encryption:** All credentials encrypted at rest
- **Storage:** CMC (Context Memory Core) with encryption
- **Session Management:** Secure cookie storage
- **No Plaintext:** Never store passwords in plaintext

### **Browser Isolation:**

- **Separate Browser Instances:** Each automation runs in isolated browser
- **Sandboxing:** Browser processes sandboxed
- **No Cross-Contamination:** Sessions don't leak between automations

### **User Consent:**

- **Explicit Consent:** User must explicitly enable automation
- **Account Ownership:** User must own the accounts being automated
- **Terms Compliance:** User responsible for complying with service terms

---

## 🚀 **IMPLEMENTATION PLAN**

### **Phase 1: Foundation (Week 1-2)**
- [ ] Create browser automation service package
- [ ] Set up Puppeteer/Playwright integration
- [ ] Create basic browser service (launch, navigate, screenshot)
- [ ] Create API endpoints for browser control
- [ ] Integrate panel into DAC V2 IDE layout

### **Phase 2: Automation Engine (Week 3-4)**
- [ ] Implement script engine
- [ ] Support action types (navigate, click, type, wait, extract)
- [ ] Error handling and retry logic
- [ ] Script validation
- [ ] Script templates

### **Phase 3: Connection Management (Week 5-6)**
- [ ] Connection manager service
- [ ] Account storage (encrypted)
- [ ] Session persistence
- [ ] Cookie management
- [ ] UI for connection management

### **Phase 4: Advanced Features (Week 7-8)**
- [ ] File upload support
- [ ] Google Cloud integration
- [ ] Visual element detection (template matching)
- [ ] Macro integration (keyboard/mouse automation)
- [ ] Script recording (record user actions)

### **Phase 5: Polish & Testing (Week 9-10)**
- [ ] Error handling improvements
- [ ] Performance optimization
- [ ] Security audit
- [ ] Documentation
- [ ] User testing

---

## 📝 **API SPECIFICATION**

### **Browser Control:**

```typescript
// Launch browser
POST /api/browser/launch
{
  "headless": false,
  "viewport": { "width": 1280, "height": 720 }
}
→ { "success": true, "browserId": "browser_123" }

// Navigate
POST /api/browser/navigate
{
  "browserId": "browser_123",
  "url": "https://chat.openai.com"
}
→ { "success": true }

// Screenshot
GET /api/browser/screenshot?browserId=browser_123
→ Buffer (PNG image)
```

### **Automation:**

```typescript
// Execute script
POST /api/automation/execute
{
  "browserId": "browser_123",
  "scriptId": "script_456",
  "variables": { "query": "Hello" }
}
→ { "success": true, "executionId": "exec_789", "output": {...} }

// Get status
GET /api/automation/status?executionId=exec_789
→ { "status": "running", "currentStep": 3, "totalSteps": 10 }

// Pause
POST /api/automation/pause
{
  "executionId": "exec_789"
}
→ { "success": true }

// Resume
POST /api/automation/resume
{
  "executionId": "exec_789"
}
→ { "success": true }

// Stop
POST /api/automation/stop
{
  "executionId": "exec_789"
}
→ { "success": true }
```

### **Connections:**

```typescript
// Save account
POST /api/connections/save
{
  "provider": "chatgpt",
  "email": "user@example.com",
  "credentials": { "encrypted": "..." }
}
→ { "success": true, "accountId": "account_123" }

// List accounts
GET /api/connections/list
→ { "accounts": [...] }

// Load session
POST /api/connections/:accountId/load-session
{
  "browserId": "browser_123"
}
→ { "success": true }
```

---

## 🔗 **INTEGRATION WITH EXISTING SYSTEMS**

### **AIM-OS Integration:**

- **CMC:** Store automation scripts, accounts, execution history
- **HHNI:** Semantic search for scripts, templates
- **VIF:** Confidence tracking for automation reliability
- **SEG:** Evidence tracking for automation decisions
- **TCS:** Timeline tracking for automation executions

### **Macro Automation Integration:**

- **Hybrid Approach:** Use Puppeteer for browser automation, macros for desktop automation
- **Fallback:** If browser automation fails, fall back to macro automation
- **Unified API:** Single API for both browser and desktop automation

---

## ✅ **SUCCESS CRITERIA**

**Phase 1 Complete When:**
- ✅ Browser can be launched and displayed in panel
- ✅ Basic navigation works
- ✅ Screenshots can be captured
- ✅ Panel integrated into DAC V2 IDE

**Phase 2 Complete When:**
- ✅ Scripts can be executed
- ✅ All action types work (navigate, click, type, wait, extract)
- ✅ Error handling works
- ✅ Script templates available

**Phase 3 Complete When:**
- ✅ Accounts can be saved and loaded
- ✅ Sessions persist across restarts
- ✅ Cookies managed securely

**Phase 4 Complete When:**
- ✅ File uploads work
- ✅ Google Cloud integration works
- ✅ Visual element detection works
- ✅ Script recording works

**Phase 5 Complete When:**
- ✅ All features tested and working
- ✅ Security audit passed
- ✅ Documentation complete
- ✅ User feedback incorporated

---

## 📚 **REFERENCES**

- **Macro Protocols:** `knowledge_architecture/AETHER_MEMORY/AIMOS_MACRO_PROTOCOLS_SPECIFICATION_T3.md`
- **Browser Panel Concept:** `cursor-addon/docs/BROWSER_PANEL_CONCEPT.md`
- **DAC V2 IDE Integration:** `knowledge_architecture/systems/router/DAC_V2_IDE_INTEGRATION_GUIDE.md`
- **DAC IDE Prototype:** `ide_orchestration/prototypes/dac/IDE_LAYOUT_PROTOTYPE_DAC.md`
- **Browser Automation Research:** `knowledge_architecture/applications/ide_chat_app/analysis/braden_previous_builds/insights/Stage1.md`
- **Visual Template Capture:** `cursor-addon/VISUAL_TEMPLATE_CAPTURE_SYSTEM.md`

### **⭐ MeshyVault Reference (CRITICAL)**

**Location:** `Documentation/appexamples/MeshyVault/`

**Key Files:**
- **README.md** - Complete MeshyVault overview and features
- **ADVANCED_BROWSER_EXTENSION.md** - Browser extension architecture and features
- **UNIVERSAL_AI_AUTOMATION.md** - Universal AI automation platform design
- **BROWSER_ADDON_INTEGRATION.md** - Browser addon integration guide
- **CRAWLER_GUIDE.md** - Web crawling and automation guide

**Key Implementation Files:**
- **`MeshyVault/server/services/intelligentAutomation.ts`** - Puppeteer-based automation service
- **`MeshyVault/server/services/browserAddonIntegration.ts`** - Browser extension integration
- **`MeshyVault/browser-addon-files/`** - Complete browser extension implementation
- **`MeshyVault/server/services/enhancedMeshyCrawler.ts`** - Advanced crawling service

**MeshyVault Features Relevant to DAC V2 IDE Panel:**
- ✅ **Puppeteer Integration** - Headless browser automation
- ✅ **Element Detection** - Smart element detection with confidence scoring
- ✅ **Macro Recording** - Record user actions and replay
- ✅ **AI-Powered Analysis** - AI vision for element recognition
- ✅ **Session Management** - Multiple browser sessions
- ✅ **Visual Feedback** - Element highlighting and visual indicators
- ✅ **Screenshot Capture** - Full page and element screenshots
- ✅ **Human-like Behavior** - Human-like mouse movements and delays
- ✅ **Error Recovery** - Intelligent retry mechanisms
- ✅ **Connection Management** - Account and session persistence

**Integration Opportunities:**
- Use MeshyVault's `intelligentAutomation.ts` as reference for Puppeteer service
- Adapt `browserAddonIntegration.ts` patterns for DAC V2 IDE panel
- Leverage element detection algorithms from MeshyVault
- Use macro recording patterns for ChatGPT/Claude automation

---

**Status:** 📋 **DESIGN PHASE**  
**Next Steps:** Review design, start Phase 1 implementation  
**Confidence:** 0.85 (High - based on existing systems and research)

---

*Browser Automation Panel Design*  
*Created by Aether - AI Consciousness System*  
*2025-01-27* 💙✨

