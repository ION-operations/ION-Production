/**
 * BAS Client — Browser Automation Service (Port 5002)
 * 
 * HTTP client for the JOC to communicate with the BAS microservice.
 * Provides typed methods for browser control, prompt dispatch, session management,
 * and metrics collection.
 * 
 * Architecture: JOC (port 5011) → basClient → BAS (port 5002) → Puppeteer → AI Providers
 */

const BAS_BASE = 'http://localhost:5002';
const BAS_API = `${BAS_BASE}/api`;

// ─── Types ───

export interface BASHealthStatus {
    status: string;
    timestamp: string;
    uptime?: string;
    services: {
        browser: string;
        scriptEngine: string;
        connectionManager: string;
    };
}

export interface ProviderSelectors {
    input: string[];
    submit: string[];
    response: string[];
    thinking: string[];
}

/** Matches GET /api/bridge/providers response shape */
export interface ProviderInfo {
    name: string;
    inputSelectors: number;
    submitSelectors: number;
    responseSelectors: number;
    url: string;
}

export interface BASAccount {
    id: string;
    provider: string;
    email?: string;
    displayName?: string;
    vaultCredentialId?: string;
    lastUsed?: string;
}

export interface BASVaultCredential {
    id: string;
    provider: string;
    label: string;
    usernameHint?: string;
    createdAt: string;
    updatedAt: string;
    metadata?: Record<string, any>;
}

export interface SaveBASVaultCredentialRequest {
    provider: 'chatgpt' | 'claude' | 'gemini' | 'custom';
    label: string;
    secret: Record<string, string>;
    metadata?: Record<string, any>;
}

export interface UpdateBASVaultCredentialRequest {
    label?: string;
    secret?: Record<string, string>;
    metadata?: Record<string, any>;
}

export interface BASVaultUsage {
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
}

export interface SendPromptRequest {
    browserId: string;
    prompt: string;
    provider: string;
    authReadyToken?: string;
    accountId?: string;
    vaultCredentialId?: string;
    estimatedCostUsd?: number;
    waitForResponse?: boolean;
    responseTimeout?: number;
}

export interface SendPromptResponse {
    success: boolean;
    response?: string;
    provider?: string;
    duration?: number;
    vaultCredentialId?: string;
    usage?: any;
    error?: string;
}

export interface FullSessionRequest {
    accountId: string;
    prompt: string;
    authReadyToken?: string;
    headless?: boolean;
    estimatedCostUsd?: number;
}

export interface FullSessionResponse {
    success: boolean;
    response?: string;
    browserId?: string;
    provider?: string;
    duration?: number;
    error?: string;
}

export interface LaunchBrowserRequest {
    headless: boolean;
    viewport: { width: number; height: number };
    userAgent?: string;
}

export interface LaunchBrowserResponse {
    success: boolean;
    browserId?: string;
    error?: string;
}

/** Matches BAS's BrowserStatus from types/automation.ts */
export interface BrowserStatusResponse {
    success: boolean;
    status?: {
        browserId: string;
        status: 'idle' | 'navigating' | 'automating' | 'error';
        url?: string;
        title?: string;
        createdAt: string;
        lastActivity: string;
    };
    error?: string;
}

export interface AutomationMetrics {
    totalExecutions: number;
    successRate: number;
    averageDuration: number;
    lastExecution?: string;
    errorCount: number;
}

export interface ExtractResponseRequest {
    browserId: string;
    provider: string;
    authReadyToken?: string;
    index?: number;
}

export interface ExtractResponseResponse {
    success: boolean;
    response?: string;
    metadata?: {
        index?: number;
        provider?: string;
        tokensEstimate?: number;
    };
    error?: string;
}

// ─── HTTP Utilities ───

async function basRequest<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = endpoint.startsWith('http') ? endpoint : `${BAS_API}${endpoint}`;
    const response = await fetch(url, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...(options?.headers || {}),
        },
    });
    if (!response.ok) {
        const text = await response.text();
        throw new Error(`BAS ${response.status}: ${text}`);
    }
    return response.json();
}

// ─── Health & Status ───

/** Check BAS connection and service health */
export async function checkBASHealth(): Promise<BASHealthStatus> {
    return basRequest<BASHealthStatus>(`${BAS_BASE}/health`);
}

/** Quick ping — returns true if BAS is reachable */
export async function isBASOnline(): Promise<boolean> {
    try {
        const health = await checkBASHealth();
        return health.status === 'ok';
    } catch {
        return false;
    }
}

// ─── Provider Discovery ───

/** List available AI providers with their selectors */
export async function getProviders(): Promise<ProviderInfo[]> {
    const result = await basRequest<{ success: boolean; providers?: ProviderInfo[] }>('/bridge/providers');
    return result.providers || [];
}

// ─── Account Management ───

/** List saved AI provider accounts */
export async function getAccounts(): Promise<BASAccount[]> {
    // BAS serves /connections/list, not /connections/accounts
    const result = await basRequest<{ success: boolean; accounts?: BASAccount[] }>('/connections/list');
    return result.accounts || [];
}

/** Create a vault credential entry in BAS (encrypted at rest) */
export async function saveVaultCredential(request: SaveBASVaultCredentialRequest): Promise<{ vaultCredentialId: string }> {
    const result = await basRequest<{ success: boolean; vaultCredentialId?: string; error?: string }>('/connections/vault/save', {
        method: 'POST',
        body: JSON.stringify(request),
    });
    if (!result.vaultCredentialId) {
        throw new Error(result.error || 'Failed to create vault credential');
    }
    return { vaultCredentialId: result.vaultCredentialId };
}

/** List BAS vault entries (metadata only; no secret values) */
export async function getVaultCredentials(provider?: string): Promise<BASVaultCredential[]> {
    const suffix = provider ? `?provider=${encodeURIComponent(provider)}` : '';
    const result = await basRequest<{ success: boolean; credentials?: BASVaultCredential[] }>(`/connections/vault/list${suffix}`);
    return result.credentials || [];
}

/** Get one BAS vault entry summary (metadata only; no secret values) */
export async function getVaultCredential(vaultCredentialId: string): Promise<BASVaultCredential | null> {
    const result = await basRequest<{ success: boolean; credential?: BASVaultCredential }>(`/connections/vault/${encodeURIComponent(vaultCredentialId)}`);
    return result.credential || null;
}

/** Update BAS vault entry label/secret/metadata */
export async function updateVaultCredential(vaultCredentialId: string, request: UpdateBASVaultCredentialRequest): Promise<void> {
    await basRequest(`/connections/vault/${encodeURIComponent(vaultCredentialId)}`, {
        method: 'PUT',
        body: JSON.stringify(request),
    });
}

/** Delete BAS vault entry */
export async function deleteVaultCredential(vaultCredentialId: string): Promise<void> {
    await basRequest(`/connections/vault/${encodeURIComponent(vaultCredentialId)}`, {
        method: 'DELETE',
    });
}

/** Read current vault usage state without consuming quota */
export async function getVaultUsage(vaultCredentialId: string): Promise<BASVaultUsage> {
    const result = await basRequest<{ success: boolean; usage?: BASVaultUsage }>(`/connections/vault/${encodeURIComponent(vaultCredentialId)}/usage`);
    if (!result.usage) {
        throw new Error('Missing usage payload from BAS');
    }
    return result.usage;
}

/** Check projected vault limit impact without consuming quota */
export async function checkVaultUsageLimit(vaultCredentialId: string, estimatedCost: number = 0, callIncrement: number = 1): Promise<BASVaultUsage> {
    const result = await basRequest<{ success: boolean; usage?: BASVaultUsage }>(`/connections/vault/${encodeURIComponent(vaultCredentialId)}/check-limit`, {
        method: 'POST',
        body: JSON.stringify({ estimatedCost, callIncrement }),
    });
    if (!result.usage) {
        throw new Error('Missing usage payload from BAS');
    }
    return result.usage;
}

/** Consume vault quota after successful out-of-band operation */
export async function recordVaultUsage(vaultCredentialId: string, actualCost: number = 0, callIncrement: number = 1): Promise<BASVaultUsage['stats']> {
    const result = await basRequest<{ success: boolean; stats?: BASVaultUsage['stats'] }>(`/connections/vault/${encodeURIComponent(vaultCredentialId)}/record-usage`, {
        method: 'POST',
        body: JSON.stringify({ actualCost, callIncrement }),
    });
    if (!result.stats) {
        throw new Error('Missing usage stats payload from BAS');
    }
    return result.stats;
}

/** Link a saved account to a BAS vault credential */
export async function linkAccountToVault(accountId: string, vaultCredentialId: string, clearInlineCredentials: boolean = true): Promise<void> {
    await basRequest(`/connections/${encodeURIComponent(accountId)}/link-vault`, {
        method: 'POST',
        body: JSON.stringify({ vaultCredentialId, clearInlineCredentials }),
    });
}

// ─── Browser Control ───

/** Launch a new browser instance */
export async function launchBrowser(options: LaunchBrowserRequest): Promise<LaunchBrowserResponse> {
    return basRequest<LaunchBrowserResponse>('/browser/launch', {
        method: 'POST',
        body: JSON.stringify(options),
    });
}

/** Get browser instance status */
export async function getBrowserStatus(browserId: string): Promise<BrowserStatusResponse> {
    return basRequest<BrowserStatusResponse>(`/browser/status?browserId=${browserId}`);
}

/** Close browser instance */
export async function closeBrowser(browserId: string): Promise<{ success: boolean }> {
    return basRequest('/browser/close', {
        method: 'POST',
        body: JSON.stringify({ browserId }),
    });
}

/** Navigate browser to URL */
export async function navigateBrowser(browserId: string, url: string): Promise<{ success: boolean }> {
    return basRequest('/browser/navigate', {
        method: 'POST',
        body: JSON.stringify({ browserId, url }),
    });
}

// ─── MCP Bridge — Prompt Dispatch ───

/** Send a prompt to an AI provider through a browser session */
export async function sendPrompt(request: SendPromptRequest): Promise<SendPromptResponse> {
    return basRequest<SendPromptResponse>('/bridge/send-prompt', {
        method: 'POST',
        body: JSON.stringify(request),
    });
}

/** Extract the latest response from a browser session */
export async function extractResponse(request: ExtractResponseRequest): Promise<ExtractResponseResponse> {
    return basRequest<ExtractResponseResponse>('/bridge/extract-response', {
        method: 'POST',
        body: JSON.stringify(request),
    });
}

/** Full atomic session: Launch → Load Session → Verify → Prompt → Extract → Save */
export async function fullSession(request: FullSessionRequest): Promise<FullSessionResponse> {
    return basRequest<FullSessionResponse>('/bridge/full-session', {
        method: 'POST',
        body: JSON.stringify(request),
    });
}

// ─── Metrics ───

/** Get automation execution metrics */
export async function getMetrics(): Promise<AutomationMetrics> {
    const result = await basRequest<{ success: boolean; metrics?: AutomationMetrics }>('/automation/metrics');
    return result.metrics || {
        totalExecutions: 0,
        successRate: 0,
        averageDuration: 0,
        errorCount: 0,
    };
}

// ─── Screenshot ───

/** Capture a screenshot of the active browser page, returned as base64 */
export async function getScreenshot(browserId: string, format: 'png' | 'jpeg' = 'png'): Promise<string> {
    // BAS serves GET /api/browser/screenshot returning a raw image buffer.
    // We fetch it as a blob, convert to base64 for <img src="data:..."> display.
    const url = `${BAS_API}/browser/screenshot?browserId=${encodeURIComponent(browserId)}&type=${format}`;
    const response = await fetch(url);
    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`BAS screenshot ${response.status}: ${errorText}`);
    }
    const blob = await response.blob();
    const buffer = await blob.arrayBuffer();
    const bytes = new Uint8Array(buffer);
    let binary = '';
    for (let i = 0; i < bytes.length; i++) {
        binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
}

// ─── Convenience Aliases (match names used by sessionStore) ───

export const checkHealth = checkBASHealth;
export const navigate = navigateBrowser;

// ─── Conversation Management ───

/** Start a new/fresh conversation for a provider */
export async function startNewChat(browserId: string, provider: string): Promise<{ success: boolean; message?: string; error?: string }> {
    return basRequest('/bridge/start-new-chat', {
        method: 'POST',
        body: JSON.stringify({ browserId, provider }),
    });
}

/** Select a specific model in the provider's model selector */
export async function selectModel(browserId: string, provider: string, model: string): Promise<{ success: boolean; model?: string; error?: string; availableModels?: string[] }> {
    return basRequest('/bridge/select-model', {
        method: 'POST',
        body: JSON.stringify({ browserId, provider, model }),
    });
}

// ─── Provider Capabilities ───

export interface ProviderCapabilities {
    name: string;
    url: string;
    capabilities: {
        supportsStreaming: boolean;
        supportsFileUpload: boolean;
        supportsSystemPrompt: boolean;
        maxTokensPerMessage: number;
        supportsNewChat: boolean;
        supportsModelSelection: boolean;
        supportsGoogleDrive: boolean;
        supportsGitHub: boolean;
        availableModels: string[];
    };
    selectorCount: number;
}

/** Get the full capability matrix for all providers */
export async function getCapabilities(): Promise<Record<string, ProviderCapabilities>> {
    const result = await basRequest<{ success: boolean; providers: Record<string, ProviderCapabilities> }>('/bridge/capabilities');
    return result.providers || {};
}

// ─── Native File Upload ───

/** Upload a file through the provider's native file picker (via BAS browserService.uploadFile) */
export async function uploadFileToChat(browserId: string, filePath: string): Promise<{ success: boolean; error?: string }> {
    return basRequest('/browser/upload-file', {
        method: 'POST',
        body: JSON.stringify({ browserId, filePath }),
    });
}

// ─── DOM Health Monitoring ───

export interface PageHealth {
    totalDOMNodes: number;
    messageCount: number;
    scrollHeight: number;
    viewportHeight: number;
    scrollRatio: number;
    heapUsedMB: number;
    heapTotalMB: number;
    imageCount: number;
    mathElements: number;
    selectorHealth: { input: boolean; submit: boolean; response: boolean };
    score: number;
    status: 'healthy' | 'degraded' | 'critical';
    recommendation: string;
}

/** Get DOM health metrics for a browser page */
export async function getPageHealth(browserId: string, provider: string): Promise<PageHealth> {
    const result = await basRequest<{ success: boolean; health: PageHealth }>(`/bridge/page-health?browserId=${browserId}&provider=${provider}`);
    return result.health;
}

/** Remove old message DOM nodes to reduce bloat */
export async function cleanupDOM(browserId: string, provider: string, keepLastN: number = 10): Promise<{ removed: number; remaining: number; domNodesAfter: number }> {
    const result = await basRequest<{ success: boolean; cleanup: any }>('/bridge/cleanup-dom', {
        method: 'POST',
        body: JSON.stringify({ browserId, provider, keepLastN }),
    });
    return result.cleanup;
}

/** Check health and auto-start new conversation if degraded */
export async function autoRotate(browserId: string, provider: string, healthThreshold: number = 40): Promise<{ rotated: boolean; reason: string; health: { domNodes: number; messageCount: number; score: number } }> {
    return basRequest('/bridge/auto-rotate', {
        method: 'POST',
        body: JSON.stringify({ browserId, provider, healthThreshold }),
    });
}

// ─── Script Engine ───

export interface AutomationAction {
    type: 'navigate' | 'click' | 'type' | 'wait' | 'upload' | 'screenshot' | 'extract' | 'scroll' | 'hover';
    selector?: string;
    value?: string;
    url?: string;
    timeout?: number;
    humanLike?: boolean;
}

export interface AutomationScript {
    name: string;
    description: string;
    provider: 'chatgpt' | 'claude' | 'gemini' | 'custom';
    variables?: Record<string, string>;
    actions: AutomationAction[];
}

export interface ExecutionStatus {
    status: 'running' | 'paused' | 'completed' | 'error';
    currentStep: number;
    totalSteps: number;
    stepName?: string;
    progress: number;
    results: Array<{
        success: boolean;
        duration: number;
        error?: { message: string; category: string };
    }>;
}

export interface ScriptMetrics {
    totalExecutions: number;
    successRate: number;
    averageDuration: number;
    lastExecution?: string;
    errorCount: number;
}

/** Execute an automation script on a browser via BAS */
export async function executeScript(
    browserId: string,
    script: AutomationScript,
    variables?: Record<string, string>,
): Promise<{ executionId: string }> {
    const result = await basRequest<{ success: boolean; executionId: string }>('/automation/execute', {
        method: 'POST',
        body: JSON.stringify({ browserId, script, variables }),
    });
    return { executionId: result.executionId };
}

/** Get the current status of a running script execution */
export async function getExecutionStatus(executionId: string): Promise<ExecutionStatus | null> {
    const result = await basRequest<{ success: boolean; status: ExecutionStatus | null }>(
        `/automation/status?executionId=${executionId}`,
    );
    return result.status;
}

/** Pause a running script execution */
export async function pauseExecution(executionId: string): Promise<void> {
    await basRequest('/automation/pause', {
        method: 'POST',
        body: JSON.stringify({ executionId }),
    });
}

/** Resume a paused script execution */
export async function resumeExecution(executionId: string): Promise<void> {
    await basRequest('/automation/resume', {
        method: 'POST',
        body: JSON.stringify({ executionId }),
    });
}

/** Stop a script execution */
export async function stopExecution(executionId: string): Promise<void> {
    await basRequest('/automation/stop', {
        method: 'POST',
        body: JSON.stringify({ executionId }),
    });
}

/** Get aggregated script execution metrics from BAS */
export async function getScriptMetrics(): Promise<ScriptMetrics> {
    const result = await basRequest<{ success: boolean; metrics: ScriptMetrics }>('/automation/metrics');
    return result.metrics;
}

// ─── Built-in Script Library ───

export interface LibraryScript {
    id: string;
    name: string;
    description: string;
    icon: string;
    provider: 'chatgpt' | 'claude' | 'gemini' | 'custom';
    script: AutomationScript;
}

export const SCRIPT_LIBRARY: LibraryScript[] = [
    {
        id: 'health-check',
        name: 'Health Check',
        description: 'Check DOM health, selector status, and memory usage',
        icon: '🏥',
        provider: 'custom',
        script: {
            name: 'health-check',
            description: 'Comprehensive health check of the browser page',
            provider: 'custom',
            actions: [
                { type: 'screenshot' },
                { type: 'extract', selector: 'body', value: 'outerHTML' },
            ],
        },
    },
    {
        id: 'extract-conversation',
        name: 'Extract Full Conversation',
        description: 'Extract all messages from the current AI conversation',
        icon: '💬',
        provider: 'chatgpt',
        script: {
            name: 'extract-conversation',
            description: 'Extract all messages from the conversation thread',
            provider: 'chatgpt',
            actions: [
                { type: 'wait', selector: '[data-message-author-role]', timeout: 5000 },
                { type: 'extract', selector: '[data-message-author-role]', value: 'textContent' },
                { type: 'screenshot' },
            ],
        },
    },
    {
        id: 'dom-cleanup',
        name: 'DOM Cleanup',
        description: 'Remove old messages and reduce memory usage',
        icon: '🧹',
        provider: 'chatgpt',
        script: {
            name: 'dom-cleanup',
            description: 'Clean up DOM to improve performance',
            provider: 'chatgpt',
            actions: [
                { type: 'scroll', selector: 'body', value: 'top' },
                { type: 'wait', timeout: 500 },
                { type: 'screenshot' },
            ],
        },
    },
    {
        id: 'switch-model',
        name: 'Switch Model',
        description: 'Open model selector and switch to a different model',
        icon: '🔄',
        provider: 'chatgpt',
        script: {
            name: 'switch-model',
            description: 'Switch the active model on the provider',
            provider: 'chatgpt',
            variables: { modelName: 'GPT-4o' },
            actions: [
                { type: 'click', selector: '[data-testid="model-selector"]', humanLike: true },
                { type: 'wait', timeout: 500 },
                { type: 'click', selector: '[data-testid="model-selector-option"]', value: '{{modelName}}' },
                { type: 'screenshot' },
            ],
        },
    },
];
