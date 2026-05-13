---
id: "browser_automation_panel_specification_T3"
system: "dac_v2_ide"
component: "browser_automation"
level: "T3"
type: "specification"
title: "Browser Automation Panel Specification - DAC V2 IDE"
description: "Comprehensive specification for browser automation panel in DAC V2 IDE for automating AI chat pages"
audience: "developers, automation engineers, IDE integrators"
confidence_threshold: 0.90
token_cost: 8000
word_count: 8000+
created: "2025-01-27T00:00:00Z"
updated: "2025-01-27T00:00:00Z"
author: "aether"
status: "design"
tags: ["browser-automation", "dac-v2-ide", "puppeteer", "chatgpt-automation", "macros", "specification", "t3"]
dependencies: ["AIMOS_MACRO_PROTOCOLS_SPECIFICATION_T3.md", "DAC_V2_IDE_INTEGRATION_GUIDE.md"]
related_docs: ["BROWSER_AUTOMATION_PANEL_DESIGN.md", "AIMOS_MACRO_PROTOCOLS_SPECIFICATION_T3.md", "CURSOR_AUTOMATION_COMPREHENSIVE_RESEARCH_T4.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# Browser Automation Panel Specification - DAC V2 IDE

**Purpose:** Comprehensive specification for browser automation panel in DAC V2 IDE  
**Status:** 📋 **DESIGN PHASE** - Ready for implementation  
**Goal:** Enable automation of AI chat pages (ChatGPT, Claude, etc.) via browser automation panel

---

## 📋 **SPECIFICATION OVERVIEW**

The Browser Automation Panel Specification defines standardized interfaces, protocols, and behaviors for:

1. **Browser Automation** - Puppeteer/Playwright-based browser control
2. **Script Execution** - JSON-based automation script engine
3. **Connection Management** - Account and session persistence
4. **Element Detection** - Visual and DOM-based element detection
5. **Macro Integration** - Integration with AIM-OS macro protocols
6. **Error Recovery** - Intelligent retry and fallback mechanisms
7. **State Management** - Session and automation state tracking
8. **Logging & Observability** - Complete operation tracking

---

## 🎯 **CORE REQUIREMENT**

Build a browser automation panel in DAC V2 IDE that:
- Shows embedded browser view (Puppeteer/Playwright)
- Automates AI chat pages (ChatGPT, Claude, Gemini, etc.)
- User signs into their own account
- Automates interactions to turn chat pages into APIs
- Supports file uploads, Google Cloud connections, etc.
- Enables use of subscribed/trial accounts with automation (e.g., deep searches)

**Use Case:** User wants to use their own ChatGPT/Claude subscriptions programmatically via automation instead of API access.

---

## 🏗️ **ARCHITECTURE SPECIFICATION**

### **System Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│  DAC V2 IDE (React Frontend)                               │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Browser Automation Panel (React Component)            │ │
│  │  - Browser View (iframe/webview)                     │ │
│  │  - Automation Controls                                │ │
│  │  - Script Editor                                      │ │
│  │  - Connection Manager                                 │ │
│  │  - Log Viewer                                         │ │
│  └───────────────────────────────────────────────────────┘ │
│                    ↕ HTTP API (REST)                        │
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
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Element Detection Service                             │ │
│  │  - Visual element detection                          │ │
│  │  - DOM-based detection                                │ │
│  │  - Confidence scoring                                │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### **Component Specifications**

#### **1. Browser Automation Panel (Frontend)**

**Location:** `ide_orchestration/prototypes/dac/src/panels/BrowserAutomationPanel.tsx`

**Interface:**
```typescript
interface BrowserAutomationPanelProps {
  panelId: string;
  zone: 'left' | 'right' | 'bottom' | 'main';
  section?: 'top' | 'bottom' | 'left' | 'right';
  onClose?: () => void;
}

interface BrowserAutomationState {
  browserUrl?: string;
  automationStatus: 'idle' | 'running' | 'paused' | 'error';
  currentScript?: string;
  currentAccount?: string;
  executionProgress?: {
    currentStep: number;
    totalSteps: number;
    stepName: string;
  };
  logs: AutomationLog[];
  error?: AutomationError;
}
```

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

interface BrowserOptions {
  headless: boolean;
  viewport: { width: number; height: number };
  userAgent?: string;
  args?: string[];
}

interface BrowserInstance {
  browserId: string;
  browser: Browser;
  page: Page;
  status: 'idle' | 'navigating' | 'automating' | 'error';
  createdAt: Date;
  lastActivity: Date;
}

export class BrowserService {
  private instances: Map<string, BrowserInstance> = new Map();
  
  async launchBrowser(options: BrowserOptions): Promise<string> {
    const browserId = `browser-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
    
    const browser = await puppeteer.launch({
      headless: options.headless,
      defaultViewport: options.viewport,
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-blink-features=AutomationControlled',
        ...(options.args || [])
      ]
    });
    
    const page = await browser.newPage();
    
    // Set user agent
    if (options.userAgent) {
      await page.setUserAgent(options.userAgent);
    }
    
    // Anti-detection measures
    await page.evaluateOnNewDocument(() => {
      Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
      Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
      Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
    });
    
    const instance: BrowserInstance = {
      browserId,
      browser,
      page,
      status: 'idle',
      createdAt: new Date(),
      lastActivity: new Date()
    };
    
    this.instances.set(browserId, instance);
    return browserId;
  }
  
  async navigateTo(browserId: string, url: string): Promise<void> {
    const instance = this.instances.get(browserId);
    if (!instance) throw new Error(`Browser instance not found: ${browserId}`);
    
    instance.status = 'navigating';
    await instance.page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });
    instance.status = 'idle';
    instance.lastActivity = new Date();
  }
  
  async click(browserId: string, selector: string): Promise<void> {
    const instance = this.instances.get(browserId);
    if (!instance) throw new Error(`Browser instance not found: ${browserId}`);
    
    await instance.page.waitForSelector(selector, { timeout: 10000 });
    await instance.page.click(selector);
    instance.lastActivity = new Date();
  }
  
  async type(browserId: string, selector: string, text: string): Promise<void> {
    const instance = this.instances.get(browserId);
    if (!instance) throw new Error(`Browser instance not found: ${browserId}`);
    
    await instance.page.waitForSelector(selector, { timeout: 10000 });
    await instance.page.type(selector, text, { delay: 50 }); // Human-like typing
    instance.lastActivity = new Date();
  }
  
  async screenshot(browserId: string, options?: ScreenshotOptions): Promise<Buffer> {
    const instance = this.instances.get(browserId);
    if (!instance) throw new Error(`Browser instance not found: ${browserId}`);
    
    return await instance.page.screenshot(options || { type: 'png', fullPage: false });
  }
  
  async waitForElement(browserId: string, selector: string, timeout?: number): Promise<void> {
    const instance = this.instances.get(browserId);
    if (!instance) throw new Error(`Browser instance not found: ${browserId}`);
    
    await instance.page.waitForSelector(selector, { timeout: timeout || 10000 });
  }
  
  async closeBrowser(browserId: string): Promise<void> {
    const instance = this.instances.get(browserId);
    if (!instance) throw new Error(`Browser instance not found: ${browserId}`);
    
    await instance.browser.close();
    this.instances.delete(browserId);
  }
}
```

**b) Automation Script Engine**
```typescript
// packages/browser-automation-service/src/services/scriptEngine.ts

export interface AutomationAction {
  type: 'navigate' | 'click' | 'type' | 'wait' | 'upload' | 'screenshot' | 'extract' | 'scroll' | 'hover';
  selector?: string;
  value?: string;
  url?: string;
  filePath?: string;
  timeout?: number;
  coordinates?: { x: number; y: number };
  scrollAmount?: number;
  humanLike?: boolean;
  beforeDelay?: number;
  afterDelay?: number;
  condition?: string; // JavaScript condition to check before executing
}

export interface AutomationScript {
  name: string;
  description: string;
  provider: 'chatgpt' | 'claude' | 'gemini' | 'custom';
  variables?: Record<string, string>;
  actions: AutomationAction[];
  output?: {
    [key: string]: string; // Variable name -> selector or extraction method
  };
}

export interface ScriptResult {
  success: boolean;
  results: ActionResult[];
  output?: Record<string, any>;
  error?: Error;
  duration: number;
}

export interface ActionResult {
  action: AutomationAction;
  success: boolean;
  duration: number;
  error?: Error;
  screenshot?: Buffer;
  extractedData?: any;
}

export class ScriptEngine {
  constructor(
    private browserService: BrowserService,
    private connectionManager: ConnectionManager
  ) {}
  
  async executeScript(
    browserId: string,
    script: AutomationScript,
    variables?: Record<string, string>
  ): Promise<ScriptResult> {
    const startTime = Date.now();
    const results: ActionResult[] = [];
    
    try {
      // Replace variables in script
      const processedScript = this.processVariables(script, variables || {});
      
      // Load session if account specified
      if (script.provider && processedScript.variables?.accountId) {
        await this.connectionManager.loadSession(
          processedScript.variables.accountId,
          browserId
        );
      }
      
      // Execute each action
      for (let i = 0; i < processedScript.actions.length; i++) {
        const action = processedScript.actions[i];
        
        try {
          // Check condition if specified
          if (action.condition) {
            const conditionMet = await this.evaluateCondition(browserId, action.condition);
            if (!conditionMet) {
              results.push({
                action,
                success: false,
                duration: 0,
                error: new Error(`Condition not met: ${action.condition}`)
              });
              continue;
            }
          }
          
          // Before delay
          if (action.beforeDelay) {
            await this.sleep(action.beforeDelay);
          }
          
          // Execute action
          const actionStartTime = Date.now();
          const result = await this.executeAction(browserId, action);
          const actionDuration = Date.now() - actionStartTime;
          
          results.push({
            action,
            success: result.success,
            duration: actionDuration,
            error: result.error,
            screenshot: result.screenshot,
            extractedData: result.extractedData
          });
          
          // After delay
          if (action.afterDelay) {
            await this.sleep(action.afterDelay);
          }
          
          // If action failed and no retry, stop execution
          if (!result.success && !action.retry) {
            break;
          }
          
        } catch (error) {
          results.push({
            action,
            success: false,
            duration: 0,
            error: error instanceof Error ? error : new Error(String(error))
          });
          
          // Stop on error unless retry specified
          if (!action.retry) {
            break;
          }
        }
      }
      
      // Extract output if specified
      const output: Record<string, any> = {};
      if (processedScript.output) {
        for (const [key, selector] of Object.entries(processedScript.output)) {
          output[key] = await this.extractData(browserId, selector);
        }
      }
      
      const duration = Date.now() - startTime;
      const success = results.every(r => r.success);
      
      return {
        success,
        results,
        output,
        duration
      };
      
    } catch (error) {
      return {
        success: false,
        results,
        error: error instanceof Error ? error : new Error(String(error)),
        duration: Date.now() - startTime
      };
    }
  }
  
  private async executeAction(
    browserId: string,
    action: AutomationAction
  ): Promise<{ success: boolean; error?: Error; screenshot?: Buffer; extractedData?: any }> {
    try {
      switch (action.type) {
        case 'navigate':
          await this.browserService.navigateTo(browserId, action.url!);
          return { success: true };
          
        case 'click':
          await this.browserService.click(browserId, action.selector!);
          return { success: true };
          
        case 'type':
          await this.browserService.type(browserId, action.selector!, action.value!);
          return { success: true };
          
        case 'wait':
          await this.browserService.waitForElement(browserId, action.selector!, action.timeout);
          return { success: true };
          
        case 'screenshot':
          const screenshot = await this.browserService.screenshot(browserId);
          return { success: true, screenshot };
          
        case 'extract':
          const extractedData = await this.extractData(browserId, action.selector!);
          return { success: true, extractedData };
          
        case 'scroll':
          await this.scroll(browserId, action.scrollAmount || 500);
          return { success: true };
          
        case 'hover':
          await this.hover(browserId, action.selector!);
          return { success: true };
          
        case 'upload':
          await this.uploadFile(browserId, action.selector!, action.filePath!);
          return { success: true };
          
        default:
          throw new Error(`Unknown action type: ${action.type}`);
      }
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error : new Error(String(error))
      };
    }
  }
  
  private async extractData(browserId: string, selector: string): Promise<any> {
    const instance = this.browserService.getInstance(browserId);
    if (!instance) throw new Error(`Browser instance not found: ${browserId}`);
    
    return await instance.page.evaluate((sel) => {
      const element = document.querySelector(sel);
      if (!element) return null;
      
      return {
        text: element.textContent?.trim(),
        html: element.innerHTML,
        attributes: Array.from(element.attributes).reduce((acc, attr) => {
          acc[attr.name] = attr.value;
          return acc;
        }, {} as Record<string, string>),
        value: (element as HTMLInputElement).value
      };
    }, selector);
  }
  
  private processVariables(
    script: AutomationScript,
    variables: Record<string, string>
  ): AutomationScript {
    const processed = JSON.parse(JSON.stringify(script));
    
    // Replace variables in actions
    processed.actions = processed.actions.map((action: AutomationAction) => {
      if (action.value) {
        action.value = this.replaceVariables(action.value, variables);
      }
      if (action.url) {
        action.url = this.replaceVariables(action.url, variables);
      }
      return action;
    });
    
    // Merge variables
    processed.variables = { ...processed.variables, ...variables };
    
    return processed;
  }
  
  private replaceVariables(text: string, variables: Record<string, string>): string {
    return text.replace(/\{\{(\w+)\}\}/g, (match, key) => {
      return variables[key] || match;
    });
  }
  
  private async evaluateCondition(browserId: string, condition: string): Promise<boolean> {
    const instance = this.browserService.getInstance(browserId);
    if (!instance) throw new Error(`Browser instance not found: ${browserId}`);
    
    return await instance.page.evaluate((cond) => {
      try {
        return eval(cond);
      } catch {
        return false;
      }
    }, condition);
  }
  
  private async sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
  
  private async scroll(browserId: string, amount: number): Promise<void> {
    const instance = this.browserService.getInstance(browserId);
    if (!instance) throw new Error(`Browser instance not found: ${browserId}`);
    
    await instance.page.evaluate((amt) => {
      window.scrollBy(0, amt);
    }, amount);
  }
  
  private async hover(browserId: string, selector: string): Promise<void> {
    const instance = this.browserService.getInstance(browserId);
    if (!instance) throw new Error(`Browser instance not found: ${browserId}`);
    
    await instance.page.hover(selector);
  }
  
  private async uploadFile(browserId: string, selector: string, filePath: string): Promise<void> {
    const instance = this.browserService.getInstance(browserId);
    if (!instance) throw new Error(`Browser instance not found: ${browserId}`);
    
    const input = await instance.page.$(selector);
    if (!input) throw new Error(`File input not found: ${selector}`);
    
    await input.uploadFile(filePath);
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
  displayName?: string;
  sessionCookies?: Cookie[];
  credentials?: EncryptedCredentials;
  lastUsed?: Date;
  createdAt: Date;
  metadata?: Record<string, any>;
}

export interface EncryptedCredentials {
  encrypted: string;
  algorithm: string;
  iv: string;
}

export class ConnectionManager {
  private accounts: Map<string, ChatAccount> = new Map();
  private storagePath: string;
  
  constructor(storagePath?: string) {
    this.storagePath = storagePath || join(process.cwd(), 'browser-automation-accounts.json');
    this.loadAccounts();
  }
  
  async saveAccount(account: ChatAccount): Promise<void> {
    // Encrypt credentials if provided
    if (account.credentials) {
      account.credentials = await this.encryptCredentials(account.credentials);
    }
    
    this.accounts.set(account.id, account);
    await this.persistAccounts();
  }
  
  async loadSession(accountId: string, browserId: string): Promise<void> {
    const account = this.accounts.get(accountId);
    if (!account) {
      throw new Error(`Account not found: ${accountId}`);
    }
    
    // Get browser instance
    const browserService = BrowserService.getInstance();
    const instance = browserService.getInstance(browserId);
    if (!instance) {
      throw new Error(`Browser instance not found: ${browserId}`);
    }
    
    // Set cookies if available
    if (account.sessionCookies && account.sessionCookies.length > 0) {
      await instance.page.setCookie(...account.sessionCookies);
    }
    
    // Update last used
    account.lastUsed = new Date();
    await this.persistAccounts();
  }
  
  async updateSessionCookies(accountId: string, cookies: Cookie[]): Promise<void> {
    const account = this.accounts.get(accountId);
    if (!account) {
      throw new Error(`Account not found: ${accountId}`);
    }
    
    account.sessionCookies = cookies;
    await this.persistAccounts();
  }
  
  async listAccounts(): Promise<ChatAccount[]> {
    return Array.from(this.accounts.values());
  }
  
  async getAccount(accountId: string): Promise<ChatAccount | null> {
    return this.accounts.get(accountId) || null;
  }
  
  async deleteAccount(accountId: string): Promise<void> {
    this.accounts.delete(accountId);
    await this.persistAccounts();
  }
  
  private async encryptCredentials(credentials: EncryptedCredentials): Promise<EncryptedCredentials> {
    // Use AES-256-GCM encryption
    const crypto = require('crypto');
    const algorithm = 'aes-256-gcm';
    const key = Buffer.from(process.env.ENCRYPTION_KEY || 'default-key-change-in-production', 'utf8');
    const iv = crypto.randomBytes(16);
    
    const cipher = crypto.createCipheriv(algorithm, key, iv);
    const encrypted = Buffer.concat([
      cipher.update(JSON.stringify(credentials), 'utf8'),
      cipher.final()
    ]);
    
    const authTag = cipher.getAuthTag();
    
    return {
      encrypted: encrypted.toString('base64'),
      algorithm,
      iv: iv.toString('base64'),
      authTag: authTag.toString('base64')
    };
  }
  
  private async decryptCredentials(encrypted: EncryptedCredentials): Promise<any> {
    const crypto = require('crypto');
    const key = Buffer.from(process.env.ENCRYPTION_KEY || 'default-key-change-in-production', 'utf8');
    const iv = Buffer.from(encrypted.iv, 'base64');
    const authTag = Buffer.from(encrypted.authTag, 'base64');
    
    const decipher = crypto.createDecipheriv(encrypted.algorithm, key, iv);
    decipher.setAuthTag(authTag);
    
    const decrypted = Buffer.concat([
      decipher.update(Buffer.from(encrypted.encrypted, 'base64')),
      decipher.final()
    ]);
    
    return JSON.parse(decrypted.toString('utf8'));
  }
  
  private async persistAccounts(): Promise<void> {
    const accountsArray = Array.from(this.accounts.values());
    await writeFile(this.storagePath, JSON.stringify(accountsArray, null, 2), 'utf8');
  }
  
  private async loadAccounts(): Promise<void> {
    try {
      const data = await readFile(this.storagePath, 'utf8');
      const accountsArray = JSON.parse(data) as ChatAccount[];
      
      accountsArray.forEach(account => {
        this.accounts.set(account.id, account);
      });
    } catch (error) {
      // File doesn't exist yet, start with empty map
      this.accounts = new Map();
    }
  }
}
```

---

## 🔧 **PROTOCOL 1: BROWSER AUTOMATION PROTOCOL**

### **1.1 Purpose**

Standardize browser automation across platforms with Puppeteer/Playwright, validation, error handling, and verification.

### **1.2 Interface**

```typescript
interface BrowserAutomationProtocol {
    // Browser Management
    launchBrowser(options: BrowserOptions): Promise<string>;
    navigateTo(browserId: string, url: string): Promise<void>;
    closeBrowser(browserId: string): Promise<void>;
    getBrowserStatus(browserId: string): Promise<BrowserStatus>;
    
    // Element Interaction
    click(browserId: string, selector: string): Promise<void>;
    type(browserId: string, selector: string, text: string): Promise<void>;
    waitForElement(browserId: string, selector: string, timeout?: number): Promise<void>;
    extractData(browserId: string, selector: string): Promise<any>;
    
    // Script Execution
    executeScript(browserId: string, script: AutomationScript, variables?: Record<string, string>): Promise<ScriptResult>;
    pauseExecution(executionId: string): Promise<void>;
    resumeExecution(executionId: string): Promise<void>;
    stopExecution(executionId: string): Promise<void>;
    
    // Connection Management
    saveAccount(account: ChatAccount): Promise<void>;
    loadSession(accountId: string, browserId: string): Promise<void>;
    listAccounts(): Promise<ChatAccount[]>;
    deleteAccount(accountId: string): Promise<void>;
}
```

### **1.3 Validation Rules**

**Required Validations:**
1. ✅ Browser ID exists and is valid
2. ✅ Selector is non-empty string
3. ✅ URL is valid format
4. ✅ Script is valid JSON structure
5. ✅ Actions array is non-empty
6. ✅ Account ID exists (if specified)
7. ✅ File path exists (for upload actions)

**Validation Implementation:**
```typescript
function validateBrowserAutomationInput(input: BrowserAutomationInput): ValidationResult {
    const errors: ValidationError[] = [];
    const warnings: ValidationWarning[] = [];
    
    // Browser ID validation
    if (input.browserId && !isValidBrowserId(input.browserId)) {
        errors.push({
            code: 'INVALID_BROWSER_ID',
            message: 'Browser ID is invalid or not found'
        });
    }
    
    // Selector validation
    if (input.selector && typeof input.selector !== 'string') {
        errors.push({
            code: 'INVALID_SELECTOR',
            message: 'Selector must be a string'
        });
    }
    
    // URL validation
    if (input.url && !isValidUrl(input.url)) {
        errors.push({
            code: 'INVALID_URL',
            message: `Invalid URL format: ${input.url}`
        });
    }
    
    // Script validation
    if (input.script) {
        if (!input.script.actions || !Array.isArray(input.script.actions)) {
            errors.push({
                code: 'INVALID_SCRIPT',
                message: 'Script must have actions array'
            });
        }
        
        if (input.script.actions.length === 0) {
            errors.push({
                code: 'EMPTY_SCRIPT',
                message: 'Script actions array cannot be empty'
            });
        }
        
        // Validate each action
        input.script.actions.forEach((action, index) => {
            if (!action.type) {
                errors.push({
                    code: 'MISSING_ACTION_TYPE',
                    message: `Action at index ${index} missing type`
                });
            }
            
            if (action.type === 'navigate' && !action.url) {
                errors.push({
                    code: 'MISSING_URL',
                    message: `Action at index ${index} (navigate) missing URL`
                });
            }
            
            if ((action.type === 'click' || action.type === 'type') && !action.selector) {
                errors.push({
                    code: 'MISSING_SELECTOR',
                    message: `Action at index ${index} (${action.type}) missing selector`
                });
            }
        });
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

**Browser Detection:**
- Chrome/Chromium (via Puppeteer)
- Firefox (via Playwright)
- Edge (via Puppeteer)

**Detection Implementation:**
```typescript
enum Platform {
    WINDOWS = 'win32',
    MACOS = 'darwin',
    LINUX = 'linux'
}

enum BrowserType {
    CHROME = 'chrome',
    FIREFOX = 'firefox',
    EDGE = 'edge'
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

async function detectBrowser(browserType: BrowserType): Promise<boolean> {
    try {
        switch (browserType) {
            case BrowserType.CHROME:
                await execSync('which google-chrome || which chromium', { timeout: 5000 });
                return true;
            case BrowserType.FIREFOX:
                await execSync('which firefox', { timeout: 5000 });
                return true;
            default:
                return false;
        }
    } catch {
        return false;
    }
}
```

### **1.5 Prerequisite Checks**

**Browser Prerequisites:**
- ✅ Puppeteer installed (`npm install puppeteer`)
- ✅ Playwright installed (optional, `npm install playwright`)
- ✅ Chrome/Chromium available (for Puppeteer)
- ✅ Sufficient system resources (memory, CPU)

**System Prerequisites:**
- ✅ Node.js 18+ installed
- ✅ Sufficient disk space for browser instances
- ✅ Network connectivity for browser automation

**Implementation:**
```typescript
interface PrerequisiteCheck {
    passed: boolean;
    missing: string[];
    warnings: string[];
}

async function checkPrerequisites(): Promise<PrerequisiteCheck> {
    const missing: string[] = [];
    const warnings: string[] = [];
    
    // Check Node.js version
    const nodeVersion = process.version;
    const majorVersion = parseInt(nodeVersion.substring(1).split('.')[0]);
    if (majorVersion < 18) {
        missing.push(`Node.js 18+ required (found ${nodeVersion})`);
    }
    
    // Check Puppeteer
    try {
        require.resolve('puppeteer');
    } catch {
        missing.push('puppeteer package not installed');
    }
    
    // Check Chrome/Chromium
    try {
        await execSync('which google-chrome || which chromium', { timeout: 5000 });
    } catch {
        warnings.push('Chrome/Chromium not found in PATH (Puppeteer will download it)');
    }
    
    // Check system resources
    const totalMemory = os.totalmem();
    const freeMemory = os.freemem();
    const memoryUsagePercent = ((totalMemory - freeMemory) / totalMemory) * 100;
    
    if (memoryUsagePercent > 90) {
        warnings.push('System memory usage is high (>90%)');
    }
    
    return {
        passed: missing.length === 0,
        missing,
        warnings
    };
}
```

---

## 🤝 **PROTOCOL 2: SCRIPT EXECUTION PROTOCOL**

### **2.1 Purpose**

Standardize automation script execution with validation, error handling, and progress tracking.

### **2.2 Script Format**

**JSON Script Structure:**
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
      "waitUntil": "networkidle2",
      "timeout": 30000
    },
    {
      "type": "wait",
      "selector": "button[data-testid='login-button']",
      "timeout": 10000
    },
    {
      "type": "click",
      "selector": "button[data-testid='login-button']",
      "beforeDelay": 500,
      "afterDelay": 1000
    },
    {
      "type": "wait",
      "selector": "input[name='email']",
      "timeout": 5000
    },
    {
      "type": "type",
      "selector": "input[name='email']",
      "value": "{{email}}",
      "humanLike": true,
      "delay": 50
    },
    {
      "type": "type",
      "selector": "input[name='password']",
      "value": "{{password}}",
      "humanLike": true,
      "delay": 50
    },
    {
      "type": "click",
      "selector": "button[type='submit']",
      "afterDelay": 2000
    },
    {
      "type": "wait",
      "selector": "textarea[data-id='root']",
      "timeout": 15000
    },
    {
      "type": "type",
      "selector": "textarea[data-id='root']",
      "value": "{{query}}",
      "humanLike": true
    },
    {
      "type": "click",
      "selector": "button[data-testid='send-button']",
      "afterDelay": 1000
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
    "response": ".markdown"
  }
}
```

### **2.3 Execution Flow**

```
1. Validate Script
   ↓ (if invalid)
   Return ValidationResult with errors
   ↓ (if valid)
2. Process Variables
   ↓
3. Load Session (if account specified)
   ↓
4. Execute Actions Sequentially
   ↓ (for each action)
   a. Check Condition (if specified)
   ↓ (if condition met)
   b. Before Delay
   ↓
   c. Execute Action
   ↓
   d. After Delay
   ↓
   e. Record Result
   ↓
5. Extract Output (if specified)
   ↓
6. Return ScriptResult
```

### **2.4 Error Handling**

**Error Classification:**
```typescript
enum AutomationErrorCategory {
    NAVIGATION = 'navigation',       // Navigation errors
    ELEMENT_NOT_FOUND = 'element_not_found', // Element not found
    TIMEOUT = 'timeout',            // Timeout errors
    NETWORK = 'network',            // Network errors
    SCRIPT = 'script',              // Script errors
    AUTHENTICATION = 'authentication', // Authentication errors
    UNKNOWN = 'unknown'             // Unknown errors
}

function classifyError(error: Error): AutomationErrorCategory {
    const message = error.message.toLowerCase();
    
    if (message.includes('timeout') || message.includes('timed out')) {
        return AutomationErrorCategory.TIMEOUT;
    }
    
    if (message.includes('navigation') || message.includes('failed to navigate')) {
        return AutomationErrorCategory.NAVIGATION;
    }
    
    if (message.includes('element') || message.includes('selector') || message.includes('not found')) {
        return AutomationErrorCategory.ELEMENT_NOT_FOUND;
    }
    
    if (message.includes('network') || message.includes('connection')) {
        return AutomationErrorCategory.NETWORK;
    }
    
    if (message.includes('auth') || message.includes('login') || message.includes('session')) {
        return AutomationErrorCategory.AUTHENTICATION;
    }
    
    return AutomationErrorCategory.UNKNOWN;
}
```

**Retry Strategy:**
```typescript
interface RetryStrategy {
    maxRetries: number;
    initialDelay: number;
    maxDelay: number;
    backoffMultiplier: number;
    retryableErrors: AutomationErrorCategory[];
}

const DEFAULT_RETRY_STRATEGY: RetryStrategy = {
    maxRetries: 3,
    initialDelay: 1000,      // 1 second
    maxDelay: 10000,         // 10 seconds
    backoffMultiplier: 2,    // Double each retry
    retryableErrors: [
        AutomationErrorCategory.TIMEOUT,
        AutomationErrorCategory.NETWORK,
        AutomationErrorCategory.ELEMENT_NOT_FOUND
    ]
};

async function executeWithRetry(
    action: AutomationAction,
    browserId: string,
    strategy: RetryStrategy = DEFAULT_RETRY_STRATEGY
): Promise<ActionResult> {
    let lastError: Error | null = null;
    
    for (let attempt = 1; attempt <= strategy.maxRetries; attempt++) {
        try {
            const result = await executeAction(browserId, action);
            
            if (result.success) {
                return result;
            }
            
            // Classify error
            const errorCategory = classifyError(result.error!);
            
            // Check if error is retryable
            if (!strategy.retryableErrors.includes(errorCategory)) {
                return result; // Don't retry non-retryable errors
            }
            
            // Retry if attempts remaining
            if (attempt < strategy.maxRetries) {
                const delay = Math.min(
                    strategy.initialDelay * Math.pow(strategy.backoffMultiplier, attempt - 1),
                    strategy.maxDelay
                );
                await sleep(delay);
                continue;
            }
            
            lastError = result.error!;
        } catch (error) {
            lastError = error instanceof Error ? error : new Error(String(error));
            
            const errorCategory = classifyError(lastError);
            
            // Don't retry non-retryable errors
            if (!strategy.retryableErrors.includes(errorCategory)) {
                throw lastError;
            }
            
            // Retry if attempts remaining
            if (attempt < strategy.maxRetries) {
                const delay = Math.min(
                    strategy.initialDelay * Math.pow(strategy.backoffMultiplier, attempt - 1),
                    strategy.maxDelay
                );
                await sleep(delay);
                continue;
            }
        }
    }
    
    // All retries failed
    throw lastError || new Error('All retry attempts failed');
}
```

---

## 📊 **PROTOCOL 3: CONNECTION MANAGEMENT PROTOCOL**

### **3.1 Purpose**

Standardize account and session management for browser automation with secure credential storage and session persistence.

### **3.2 Interface**

```typescript
interface ConnectionManagementProtocol {
    // Account Management
    saveAccount(account: ChatAccount): Promise<void>;
    getAccount(accountId: string): Promise<ChatAccount | null>;
    listAccounts(): Promise<ChatAccount[]>;
    deleteAccount(accountId: string): Promise<void>;
    updateAccount(accountId: string, updates: Partial<ChatAccount>): Promise<void>;
    
    // Session Management
    loadSession(accountId: string, browserId: string): Promise<void>;
    saveSession(accountId: string, browserId: string): Promise<void>;
    updateSessionCookies(accountId: string, cookies: Cookie[]): Promise<void>;
    clearSession(accountId: string): Promise<void>;
    
    // Credential Management
    encryptCredentials(credentials: any): Promise<EncryptedCredentials>;
    decryptCredentials(encrypted: EncryptedCredentials): Promise<any>;
}
```

### **3.3 Account Storage**

**Storage Format:**
```typescript
interface StoredAccount {
    id: string;
    provider: 'chatgpt' | 'claude' | 'gemini' | 'custom';
    email?: string;
    displayName?: string;
    sessionCookies?: Cookie[];
    credentials?: EncryptedCredentials;
    lastUsed?: string; // ISO date string
    createdAt: string; // ISO date string
    metadata?: Record<string, any>;
}
```

**Storage Location:**
- **Development:** `packages/browser-automation-service/data/accounts.json`
- **Production:** Encrypted storage in CMC (Context Memory Core)
- **Backup:** Encrypted backup in `~/.aimos/browser-automation/accounts-backup.json`

### **3.4 Session Persistence**

**Cookie Management:**
```typescript
async function saveSessionCookies(accountId: string, browserId: string): Promise<void> {
    const instance = browserService.getInstance(browserId);
    if (!instance) throw new Error(`Browser instance not found: ${browserId}`);
    
    // Get cookies from browser
    const cookies = await instance.page.cookies();
    
    // Update account with cookies
    await connectionManager.updateSessionCookies(accountId, cookies);
    
    // Also save to browser storage for quick access
    await instance.page.evaluate((cookies) => {
        localStorage.setItem('session_cookies', JSON.stringify(cookies));
    }, cookies);
}
```

**Session Restoration:**
```typescript
async function restoreSession(accountId: string, browserId: string): Promise<void> {
    const account = await connectionManager.getAccount(accountId);
    if (!account) throw new Error(`Account not found: ${accountId}`);
    
    const instance = browserService.getInstance(browserId);
    if (!instance) throw new Error(`Browser instance not found: ${browserId}`);
    
    // Set cookies
    if (account.sessionCookies && account.sessionCookies.length > 0) {
        await instance.page.setCookie(...account.sessionCookies);
    }
    
    // Navigate to provider URL
    const providerUrl = getProviderUrl(account.provider);
    await instance.page.goto(providerUrl, { waitUntil: 'networkidle2' });
    
    // Verify session is valid
    const isLoggedIn = await verifySession(instance.page, account.provider);
    
    if (!isLoggedIn) {
        throw new Error(`Session expired for account: ${accountId}`);
    }
    
    // Update last used
    account.lastUsed = new Date();
    await connectionManager.saveAccount(account);
}
```

---

## 📝 **PROTOCOL 4: LOGGING & OBSERVABILITY**

### **4.1 Purpose**

Standardize logging across all browser automation operations for debugging and monitoring.

### **4.2 Log Levels**

- `LOG` - Normal operations
- `SUCCESS` - Successful operations
- `WARN` - Warnings (non-fatal)
- `ERROR` - Errors (fatal)
- `DEBUG` - Debug information (development only)

### **4.3 Log Structure**

```typescript
interface AutomationLogEntry {
    timestamp: number;
    level: 'LOG' | 'SUCCESS' | 'WARN' | 'ERROR' | 'DEBUG';
    category: 'BROWSER_AUTOMATION';
    message: string;
    data?: {
        browserId?: string;
        executionId?: string;
        action?: AutomationAction;
        script?: string;
        accountId?: string;
        error?: Error;
        duration?: number;
        screenshot?: string; // Base64 or path
    };
}

function logAutomationOperation(
    level: 'LOG' | 'SUCCESS' | 'WARN' | 'ERROR' | 'DEBUG',
    message: string,
    data?: AutomationLogEntry['data']
): void {
    const entry: AutomationLogEntry = {
        timestamp: Date.now(),
        level,
        category: 'BROWSER_AUTOMATION',
        message,
        data
    };
    
    AIMOSLogger.log('BROWSER_AUTOMATION', message, data);
    
    // Also send to frontend for real-time display
    if (webSocketServer) {
        webSocketServer.broadcast('automation-log', entry);
    }
    
    // Store in CMC for persistence
    storeMemory({
        content: JSON.stringify(entry),
        tags: {
            type: 'automation_log',
            level,
            browserId: data?.browserId,
            executionId: data?.executionId
        }
    });
}
```

### **4.4 Required Logging Points**

**Pre-execution:**
- ✅ Script validation start
- ✅ Browser launch
- ✅ Session loading
- ✅ Variable processing

**Execution:**
- ✅ Action execution start
- ✅ Action execution completion
- ✅ Action execution failure
- ✅ Progress updates (every 10% or every action)

**Post-execution:**
- ✅ Script execution completion
- ✅ Output extraction
- ✅ Session saving
- ✅ Duration and statistics

**Error:**
- ✅ Error occurrence
- ✅ Error classification
- ✅ Retry attempt
- ✅ Fallback attempt

---

## 🔗 **INTEGRATION WITH MACRO PROTOCOLS**

### **Hybrid Automation Approach**

Browser automation can integrate with AIM-OS macro protocols for hybrid automation:

**Use Browser Automation For:**
- ✅ Web page interactions (clicks, typing, navigation)
- ✅ Element detection and extraction
- ✅ Screenshot capture
- ✅ File uploads
- ✅ Session management

**Use Macro Automation For:**
- ✅ Desktop application automation (fallback)
- ✅ Keyboard shortcuts
- ✅ System-level operations
- ✅ When browser automation fails

**Integration Pattern:**
```typescript
async function executeWithFallback(
    action: AutomationAction,
    browserId: string
): Promise<ActionResult> {
    try {
        // Try browser automation first
        return await browserService.executeAction(browserId, action);
    } catch (error) {
        // If browser automation fails, try macro automation
        if (action.type === 'click' || action.type === 'type') {
            const macroResult = await macroService.executeMacro({
                message: `Click at coordinates ${action.coordinates?.x}, ${action.coordinates?.y}`,
                options: {
                    waitForResponse: false,
                    timeout: 5000
                }
            });
            
            if (macroResult.success) {
                return {
                    success: true,
                    method: 'macro-automation',
                    duration: macroResult.duration
                };
            }
        }
        
        throw error;
    }
}
```

---

## 📋 **API SPECIFICATION**

### **Browser Control Endpoints**

```typescript
// Launch browser
POST /api/browser/launch
{
  "headless": false,
  "viewport": { "width": 1280, "height": 720 },
  "userAgent": "Mozilla/5.0..."
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
GET /api/browser/screenshot?browserId=browser_123&fullPage=false
→ Buffer (PNG image) or { "success": true, "screenshot": "base64..." }

// Close browser
POST /api/browser/close
{
  "browserId": "browser_123"
}
→ { "success": true }

// Get browser status
GET /api/browser/status?browserId=browser_123
→ {
  "success": true,
  "status": "idle" | "navigating" | "automating" | "error",
  "url": "https://chat.openai.com",
  "title": "ChatGPT",
  "createdAt": "2025-01-27T12:00:00Z",
  "lastActivity": "2025-01-27T12:05:00Z"
}
```

### **Automation Endpoints**

```typescript
// Execute script
POST /api/automation/execute
{
  "browserId": "browser_123",
  "scriptId": "script_456",
  "variables": { "query": "Hello" }
}
→ {
  "success": true,
  "executionId": "exec_789",
  "output": { "response": "..." }
}

// Get execution status
GET /api/automation/status?executionId=exec_789
→ {
  "success": true,
  "status": "running" | "paused" | "completed" | "error",
  "currentStep": 3,
  "totalSteps": 10,
  "stepName": "Click login button",
  "progress": 0.3,
  "results": [...]
}

// Pause execution
POST /api/automation/pause
{
  "executionId": "exec_789"
}
→ { "success": true }

// Resume execution
POST /api/automation/resume
{
  "executionId": "exec_789"
}
→ { "success": true }

// Stop execution
POST /api/automation/stop
{
  "executionId": "exec_789"
}
→ { "success": true }
```

### **Script Management Endpoints**

```typescript
// Save script
POST /api/scripts/save
{
  "name": "ChatGPT Deep Search",
  "description": "...",
  "provider": "chatgpt",
  "script": { ... }
}
→ { "success": true, "scriptId": "script_456" }

// List scripts
GET /api/scripts/list?provider=chatgpt
→ {
  "success": true,
  "scripts": [
    {
      "id": "script_456",
      "name": "ChatGPT Deep Search",
      "provider": "chatgpt",
      "createdAt": "2025-01-27T12:00:00Z"
    }
  ]
}

// Get script
GET /api/scripts/:scriptId
→ {
  "success": true,
  "script": { ... }
}

// Delete script
DELETE /api/scripts/:scriptId
→ { "success": true }
```

### **Connection Management Endpoints**

```typescript
// Save account
POST /api/connections/save
{
  "provider": "chatgpt",
  "email": "user@example.com",
  "displayName": "My ChatGPT Account",
  "credentials": { "encrypted": "..." }
}
→ { "success": true, "accountId": "account_123" }

// List accounts
GET /api/connections/list?provider=chatgpt
→ {
  "success": true,
  "accounts": [
    {
      "id": "account_123",
      "provider": "chatgpt",
      "email": "user@example.com",
      "displayName": "My ChatGPT Account",
      "lastUsed": "2025-01-27T12:00:00Z"
    }
  ]
}

// Get account
GET /api/connections/:accountId
→ {
  "success": true,
  "account": { ... }
}

// Load session
POST /api/connections/:accountId/load-session
{
  "browserId": "browser_123"
}
→ { "success": true }

// Update session cookies
POST /api/connections/:accountId/update-cookies
{
  "cookies": [...]
}
→ { "success": true }

// Delete account
DELETE /api/connections/:accountId
→ { "success": true }
```

---

## ✅ **PROTOCOL COMPLIANCE CHECKLIST**

### **Browser Automation Protocol**
- [ ] Browser launch implemented
- [ ] Navigation implemented
- [ ] Element interaction implemented
- [ ] Screenshot capture implemented
- [ ] Browser status tracking implemented
- [ ] Error handling implemented

### **Script Execution Protocol**
- [ ] Script validation implemented
- [ ] Variable processing implemented
- [ ] Action execution implemented
- [ ] Progress tracking implemented
- [ ] Pause/resume/stop implemented
- [ ] Output extraction implemented

### **Connection Management Protocol**
- [ ] Account storage implemented
- [ ] Session persistence implemented
- [ ] Cookie management implemented
- [ ] Credential encryption implemented
- [ ] Session restoration implemented

### **Logging & Observability**
- [ ] All operations logged
- [ ] Log levels used correctly
- [ ] Required logging points covered
- [ ] Error logging implemented
- [ ] Duration tracking implemented
- [ ] Real-time log streaming implemented

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

## 📝 **CONCLUSION**

This specification defines comprehensive protocols for browser automation panel in DAC V2 IDE:

1. **Browser Automation Protocol** - Standardized browser control
2. **Script Execution Protocol** - Standardized script execution
3. **Connection Management Protocol** - Secure account and session management
4. **Logging & Observability** - Complete operation tracking
5. **Macro Integration** - Hybrid browser + desktop automation

**Compliance:** All browser automation implementations must follow these protocols.

---

**Status:** 📋 **DESIGN PHASE**  
**Last Updated:** 2025-01-27  
**Version:** 1.0.0  
**Confidence:** 0.90 (High - based on MeshyVault patterns and existing macro protocols)

---

*Browser Automation Panel Specification*  
*Created by Aether - AI Consciousness System*  
*2025-01-27* 💙✨

