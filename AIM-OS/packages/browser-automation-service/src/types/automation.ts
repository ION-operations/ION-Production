/**
 * Browser Automation Service - Type Definitions
 * 
 * Based on: BROWSER_AUTOMATION_PANEL_SPECIFICATION_T3.md
 */

// Browser Options
export interface BrowserOptions {
  headless: boolean;
  viewport: { width: number; height: number };
  userAgent?: string;
  args?: string[];
}

// Browser Instance
export interface BrowserInstance {
  browserId: string;
  browser: any; // Puppeteer Browser type
  page: any; // Puppeteer Page type
  status: 'idle' | 'navigating' | 'automating' | 'error';
  createdAt: Date;
  lastActivity: Date;
}

// Browser Status
export interface BrowserStatus {
  browserId: string;
  status: 'idle' | 'navigating' | 'automating' | 'error';
  url?: string;
  title?: string;
  createdAt: Date;
  lastActivity: Date;
}

// Automation Actions
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
  retry?: boolean;
}

// Automation Script
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

// Script Result
export interface ScriptResult {
  success: boolean;
  results: ActionResult[];
  output?: Record<string, any>;
  error?: Error;
  duration: number;
}

// Action Result
export interface ActionResult {
  action: AutomationAction;
  success: boolean;
  duration: number;
  error?: Error;
  screenshot?: Buffer;
  extractedData?: any;
}

// Chat Account
export interface ChatAccount {
  id: string;
  provider: 'chatgpt' | 'claude' | 'gemini' | 'custom';
  email?: string;
  displayName?: string;
  vaultCredentialId?: string;
  sessionCookies?: Cookie[];
  credentials?: EncryptedCredentials;
  lastUsed?: Date;
  createdAt: Date;
  metadata?: Record<string, any>;
}

// Encrypted Credentials
export interface EncryptedCredentials {
  encrypted: string;
  algorithm: string;
  iv: string;
  authTag?: string;
}

// Cookie (Puppeteer/Playwright compatible)
export interface Cookie {
  name: string;
  value: string;
  domain?: string;
  path?: string;
  expires?: number;
  httpOnly?: boolean;
  secure?: boolean;
  sameSite?: 'Strict' | 'Lax' | 'None';
}

// Error Categories
export enum AutomationErrorCategory {
  NAVIGATION = 'navigation',
  ELEMENT_NOT_FOUND = 'element_not_found',
  TIMEOUT = 'timeout',
  NETWORK = 'network',
  SCRIPT = 'script',
  AUTHENTICATION = 'authentication',
  UNKNOWN = 'unknown'
}

// Retry Strategy
export interface RetryStrategy {
  maxRetries: number;
  initialDelay: number;
  maxDelay: number;
  backoffMultiplier: number;
  retryableErrors: AutomationErrorCategory[];
}

// Log Entry
export interface AutomationLogEntry {
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

// Screenshot Options
export interface ScreenshotOptions {
  type?: 'png' | 'jpeg';
  fullPage?: boolean;
  quality?: number;
  clip?: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
}

