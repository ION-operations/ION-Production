/**
 * Browser Automation Service - API Types
 * 
 * REST API request/response types
 */

import { BrowserOptions, BrowserStatus, AutomationScript, ScriptResult, ChatAccount, Cookie } from './automation';

// Browser Control API
export interface LaunchBrowserRequest {
  headless: boolean;
  viewport: { width: number; height: number };
  userAgent?: string;
  args?: string[];
}

export interface LaunchBrowserResponse {
  success: boolean;
  browserId?: string;
  error?: string;
}

export interface NavigateRequest {
  browserId: string;
  url: string;
}

export interface NavigateResponse {
  success: boolean;
  error?: string;
}

export interface BrowserStatusResponse {
  success: boolean;
  status?: BrowserStatus;
  error?: string;
}

export interface ViewportResponse {
  success: boolean;
  viewportUrl?: string | null;
  error?: string;
}

export interface DetectElementsRequest {
  browserId: string;
  selector?: string;
}

export interface DetectedElement {
  selector: string;
  xpath: string;
  text?: string;
  tag: string;
  attributes: Record<string, string>;
  bounds: { x: number; y: number; width: number; height: number };
  confidence: number;
}

export interface DetectElementsResponse {
  success: boolean;
  elements?: DetectedElement[];
  error?: string;
}

// Automation API
export interface ExecuteScriptRequest {
  browserId: string;
  scriptId?: string;
  script?: AutomationScript;
  variables?: Record<string, string>;
}

export interface ExecuteScriptResponse {
  success: boolean;
  executionId?: string;
  result?: ScriptResult;
  error?: string;
}

export interface ExecutionStatusResponse {
  success: boolean;
  status?: {
    status: 'running' | 'paused' | 'completed' | 'error';
    currentStep: number;
    totalSteps: number;
    stepName?: string;
    progress: number;
    results?: Array<{
      action: AutomationScript['actions'][number];
      success: boolean;
      duration: number;
      error?: {
        message: string;
        category: string;
      };
      hasScreenshot?: boolean;
      hasExtractedData?: boolean;
    }>;
  };
  error?: string;
}

export interface PauseExecutionRequest {
  executionId: string;
}

export interface ResumeExecutionRequest {
  executionId: string;
}

export interface StopExecutionRequest {
  executionId: string;
}

export interface ExecutionControlResponse {
  success: boolean;
  error?: string;
}

export interface MetricsResponse {
  success: boolean;
  metrics?: {
    totalExecutions: number;
    successRate: number;
    averageDuration: number;
    lastExecution?: string;
    errorCount: number;
  };
  error?: string;
}

// Script Management API
export interface SaveScriptRequest {
  name: string;
  description: string;
  provider: 'chatgpt' | 'claude' | 'gemini' | 'custom';
  script: AutomationScript;
}

export interface SaveScriptResponse {
  success: boolean;
  scriptId?: string;
  error?: string;
}

export interface ListScriptsResponse {
  success: boolean;
  scripts?: Array<{
    id: string;
    name: string;
    provider: string;
    createdAt: string;
  }>;
  error?: string;
}

export interface GetScriptResponse {
  success: boolean;
  script?: AutomationScript;
  error?: string;
}

// Connection Management API
export interface SaveAccountRequest {
  provider: 'chatgpt' | 'claude' | 'gemini' | 'custom';
  email?: string;
  displayName?: string;
  credentials?: any;
  vaultCredentialId?: string;
}

export interface SaveAccountResponse {
  success: boolean;
  accountId?: string;
  error?: string;
}

export interface ListAccountsResponse {
  success: boolean;
  accounts?: Array<{
    id: string;
    provider: string;
    email?: string;
    displayName?: string;
    vaultCredentialId?: string;
    lastUsed?: string;
  }>;
  error?: string;
}

export interface GetAccountResponse {
  success: boolean;
  account?: ChatAccount;
  error?: string;
}

export interface LoadSessionRequest {
  browserId: string;
}

export interface LoadSessionResponse {
  success: boolean;
  error?: string;
}

export interface SaveSessionRequest {
  browserId: string;
}

export interface SaveSessionResponse {
  success: boolean;
  error?: string;
}

export interface VerifySessionRequest {
  browserId: string;
}

export interface VerifySessionResponse {
  success: boolean;
  sessionValid?: boolean;
  error?: string;
}

export interface UpdateCookiesRequest {
  cookies: Cookie[];
}

export interface UpdateCookiesResponse {
  success: boolean;
  error?: string;
}

// Credential Vault API
export interface SaveVaultCredentialRequest {
  provider: 'chatgpt' | 'claude' | 'gemini' | 'custom';
  label: string;
  secret: Record<string, string>;
  metadata?: Record<string, any>;
}

export interface SaveVaultCredentialResponse {
  success: boolean;
  vaultCredentialId?: string;
  error?: string;
}

export interface UpdateVaultCredentialRequest {
  label?: string;
  secret?: Record<string, string>;
  metadata?: Record<string, any>;
}

export interface UpdateVaultCredentialResponse {
  success: boolean;
  vaultCredentialId?: string;
  error?: string;
}

export interface ListVaultCredentialsResponse {
  success: boolean;
  credentials?: Array<{
    id: string;
    provider: string;
    label: string;
    usernameHint?: string;
    createdAt: string;
    updatedAt: string;
    metadata?: Record<string, any>;
  }>;
  error?: string;
}

export interface GetVaultCredentialResponse {
  success: boolean;
  credential?: {
    id: string;
    provider: string;
    label: string;
    usernameHint?: string;
    createdAt: string;
    updatedAt: string;
    metadata?: Record<string, any>;
  };
  error?: string;
}

export interface LinkVaultCredentialRequest {
  vaultCredentialId: string;
  clearInlineCredentials?: boolean;
}

export interface LinkVaultCredentialResponse {
  success: boolean;
  accountId?: string;
  vaultCredentialId?: string;
  error?: string;
}

export interface CheckVaultUsageRequest {
  estimatedCost?: number;
  callIncrement?: number;
}

export interface CheckVaultUsageResponse {
  success: boolean;
  usage?: {
    allowed: boolean;
    reason?: string;
    remaining: {
      callsThisHour?: number;
      callsToday?: number;
      costToday?: number;
      costThisMonth?: number;
    };
    alerts: string[];
    limits: {
      maxCallsPerHour?: number;
      maxCallsPerDay?: number;
      maxCostPerDay?: number;
      maxCostPerMonth?: number;
      alertThreshold?: number;
    };
    stats: {
      callsToday: number;
      callsThisHour: number;
      costToday: number;
      costThisMonth: number;
      lastUsed?: string;
      callTimestamps: number[];
      dayKey?: string;
      monthKey?: string;
    };
    projected: {
      callsThisHour: number;
      callsToday: number;
      costToday: number;
      costThisMonth: number;
    };
  };
  error?: string;
}

export interface RecordVaultUsageRequest {
  actualCost?: number;
  callIncrement?: number;
}

export interface RecordVaultUsageResponse {
  success: boolean;
  stats?: {
    callsToday: number;
    callsThisHour: number;
    costToday: number;
    costThisMonth: number;
    lastUsed?: string;
    callTimestamps: number[];
    dayKey?: string;
    monthKey?: string;
  };
  error?: string;
}

