/**
 * MCP Bridge Router - Agent-to-Browser Prompt Interface
 * 
 * Enables AIM-OS agents to send prompts through browser sessions
 * and extract responses from AI chat providers.
 * 
 * SELECTOR SOURCE: packages/shared/providerSelectors.ts
 * All DOM selectors imported from the shared registry.
 */

import { Router, Request, Response } from 'express';
import { BrowserService } from '../services/browserService';
import { ConnectionManager } from '../services/connectionManager';
import { CredentialVaultService } from '../services/credentialVaultService';
import { getAllFlatSelectors, getProviderConfig } from '../../../shared/providerSelectors';

// Provider-specific selectors — imported from shared registry
const PROVIDER_SELECTORS = getAllFlatSelectors();

/**
 * Try each selector in order until one works
 */
async function findSelector(page: any, selectors: string[], timeout: number = 5000): Promise<string | null> {
    for (const selector of selectors) {
        try {
            await page.waitForSelector(selector, { timeout: Math.min(timeout, 2000) });
            return selector;
        } catch {
            continue;
        }
    }
    return null;
}

type AuthGateState = {
    blocked: boolean;
    reason: 'login_required' | 'human_check' | null;
    details: {
        hasLoginIndicator: boolean;
        hasLoginCta: boolean;
        hasSignUpCta: boolean;
        hasHumanCheckText: boolean;
        hasLoggedOutHint: boolean;
    };
};

const DEFAULT_AUTH_READY_TOKEN = (process.env.BAS_AUTH_READY_TOKEN || 'AUTH_READY').trim();
const ENFORCE_CHATGPT_AUTH_READY = (process.env.BAS_ENFORCE_CHATGPT_AUTH_READY ?? 'true').toLowerCase() !== 'false';
const AUTH_READY_HEADER_KEYS = ['x-aimos-auth-ready', 'x-auth-ready-token'] as const;

function normalizeProviderName(provider: unknown): string {
    return typeof provider === 'string' ? provider.trim().toLowerCase() : '';
}

function resolveAuthReadyToken(req: Request): string {
    const bodyToken = req.body && typeof req.body.authReadyToken === 'string'
        ? req.body.authReadyToken.trim()
        : '';
    if (bodyToken) {
        return bodyToken;
    }

    for (const headerKey of AUTH_READY_HEADER_KEYS) {
        const headerValue = req.header(headerKey);
        if (headerValue && headerValue.trim()) {
            return headerValue.trim();
        }
    }

    return '';
}

function rejectIfAuthReadyMissing(
    req: Request,
    res: Response,
    provider: string,
    gate: 'send-prompt' | 'extract-response' | 'full-session'
): boolean {
    if (!ENFORCE_CHATGPT_AUTH_READY || provider !== 'chatgpt') {
        return false;
    }

    const providedToken = resolveAuthReadyToken(req);
    if (providedToken === DEFAULT_AUTH_READY_TOKEN) {
        return false;
    }

    res.status(428).json({
        success: false,
        status: 'PENDING_AUTH',
        error: `${gate} blocked: AUTH_READY token required for ChatGPT authenticated gates`,
        gate,
        provider: 'chatgpt',
        requiredToken: DEFAULT_AUTH_READY_TOKEN,
        tokenAcceptedVia: {
            bodyField: 'authReadyToken',
            headers: AUTH_READY_HEADER_KEYS
        },
        suggestion: 'Only execute authenticated ChatGPT gates after explicit operator authorization.'
    });
    return true;
}

/**
 * Detect auth gates and human verification walls before/after prompt actions.
 * Returns a conservative "blocked" verdict to avoid silent empty responses.
 */
async function detectAuthGate(page: any, provider: string): Promise<AuthGateState> {
    const providerConfig = getProviderConfig(provider);
    const loginSelectors = providerConfig?.selectors?.loginIndicator
        ? [
            providerConfig.selectors.loginIndicator.selector,
            ...providerConfig.selectors.loginIndicator.fallbacks
        ]
        : [];

    const state = await page.evaluate((authSelectors: string[]) => {
        const text = (document.body?.innerText || '').toLowerCase();
        const actionTexts = Array.from(document.querySelectorAll('button, a'))
            .map(el => (el.textContent || '').trim().toLowerCase())
            .filter(Boolean);

        const hasLoginIndicator = authSelectors.some(sel => {
            try {
                return !!document.querySelector(sel);
            } catch {
                return false;
            }
        });

        const hasLoginCta = actionTexts.some(t =>
            t === 'log in' || t === 'login' || t.startsWith('log in')
        );
        const hasSignUpCta = actionTexts.some(t => t.includes('sign up'));
        const hasHumanCheckText =
            text.includes('verify you are human') ||
            text.includes('are you human') ||
            text.includes('captcha') ||
            text.includes('cf-turnstile') ||
            text.includes('cloudflare');
        const hasLoggedOutHint =
            text.includes('get responses tailored to you') ||
            text.includes('continue with google') ||
            text.includes('continue with apple');

        return {
            hasLoginIndicator,
            hasLoginCta,
            hasSignUpCta,
            hasHumanCheckText,
            hasLoggedOutHint,
        };
    }, loginSelectors);

    if (state.hasHumanCheckText) {
        return { blocked: true, reason: 'human_check', details: state };
    }

    // Explicit login/signup CTAs or logged-out hints are strong auth blockers.
    // Some provider UIs expose profile-like controls even when logged out.
    if (state.hasLoginCta || state.hasSignUpCta || state.hasLoggedOutHint) {
        return { blocked: true, reason: 'login_required', details: state };
    }

    return { blocked: false, reason: null, details: state };
}

async function resolveVaultCredentialId(
    explicitVaultCredentialId: string | undefined,
    accountId: string | undefined,
    connectionManager: ConnectionManager
): Promise<string | null> {
    if (explicitVaultCredentialId && explicitVaultCredentialId.trim().length > 0) {
        return explicitVaultCredentialId.trim();
    }
    if (!accountId) {
        return null;
    }
    const account = await connectionManager.getAccount(accountId);
    return account?.vaultCredentialId || null;
}

export function createMcpBridgeRouter(
    browserService: BrowserService,
    connectionManager: ConnectionManager,
    credentialVaultService: CredentialVaultService
): Router {
    const router = Router();

    /**
     * POST /api/bridge/send-prompt
     * Send a prompt through a browser session to an AI provider
     * 
     * Body: {
     *   browserId, prompt, provider,
     *   accountId?: string, vaultCredentialId?: string, estimatedCostUsd?: number,
     *   waitForResponse?: boolean, responseTimeout?: number
     * }
     */
    router.post('/send-prompt', async (req: Request, res: Response) => {
        try {
            const {
                browserId,
                prompt,
                provider,
                accountId,
                vaultCredentialId,
                estimatedCostUsd = 0,
                waitForResponse = true,
                responseTimeout = 60000
            } = req.body;

            if (!browserId || !prompt || !provider) {
                return res.status(400).json({
                    success: false,
                    error: 'Missing required fields: browserId, prompt, provider'
                });
            }

            const selectors = PROVIDER_SELECTORS[provider];
            if (!selectors) {
                return res.status(400).json({
                    success: false,
                    error: `Unsupported provider: ${provider}. Supported: ${Object.keys(PROVIDER_SELECTORS).join(', ')}`
                });
            }

            const normalizedProvider = normalizeProviderName(provider);
            if (waitForResponse && rejectIfAuthReadyMissing(req, res, normalizedProvider, 'send-prompt')) {
                return;
            }

            const instance = browserService.getInstance(browserId);
            const page = instance.page;

            // Optional vault-backed usage limit check (by explicit vaultCredentialId or accountId link).
            const resolvedVaultCredentialId = await resolveVaultCredentialId(
                vaultCredentialId,
                accountId,
                connectionManager
            );
            if (resolvedVaultCredentialId) {
                const usageGate = await credentialVaultService.checkUsageLimit(
                    resolvedVaultCredentialId,
                    typeof estimatedCostUsd === 'number' ? estimatedCostUsd : 0,
                    1
                );
                if (!usageGate.allowed) {
                    return res.status(429).json({
                        success: false,
                        error: `Vault usage limit exceeded for ${provider}: ${usageGate.reason}`,
                        vaultCredentialId: resolvedVaultCredentialId,
                        usage: usageGate
                    });
                }
            }

            // Pre-flight auth gate detection to avoid hanging on logged-out/challenge pages.
            const authPreflight = await detectAuthGate(page, provider);
            if (authPreflight.blocked) {
                return res.status(authPreflight.reason === 'human_check' ? 429 : 401).json({
                    success: false,
                    error: authPreflight.reason === 'human_check'
                        ? `Automation blocked by ${provider} human verification`
                        : `Authentication required for ${provider}`,
                    auth: authPreflight,
                    suggestion: 'Complete login/human check in the visible browser, then retry and save session cookies.'
                });
            }

            // 1. Find and focus the chat input
            const inputSelector = await findSelector(page, selectors.input);
            if (!inputSelector) {
                return res.status(404).json({
                    success: false,
                    error: `Could not find chat input for ${provider}. Are you logged in?`,
                    suggestion: 'Run the login script first or verify session.'
                });
            }

            // 2. Count existing responses before sending (to know when new one arrives)
            let responseCountBefore = 0;
            try {
                const respSelector = selectors.response[0];
                responseCountBefore = await page.evaluate((sel: string) => {
                    return document.querySelectorAll(sel).length;
                }, respSelector);
            } catch {
                responseCountBefore = 0;
            }

            // 3. Clear existing input and type the prompt
            await page.click(inputSelector);
            await page.evaluate((sel: string) => {
                const el = document.querySelector(sel);
                if (el) {
                    if (el instanceof HTMLTextAreaElement || el instanceof HTMLInputElement) {
                        el.value = '';
                    } else {
                        (el as HTMLElement).textContent = '';
                    }
                }
            }, inputSelector);

            // Type with human-like delay for providers that detect automation
            await browserService.type(browserId, inputSelector, prompt, true);

            // 4. Submit the prompt
            // Small delay after typing
            await new Promise(r => setTimeout(r, 500));

            // Try clicking the send button
            const submitSelector = await findSelector(page, selectors.submit, 3000);
            if (submitSelector) {
                await page.click(submitSelector);
            } else {
                // Fallback: press Enter
                await page.keyboard.press('Enter');
            }

            console.log(`[MCP Bridge] Prompt sent to ${provider} (${prompt.length} chars)`);

            // 5. Optionally wait for response
            if (!waitForResponse) {
                if (resolvedVaultCredentialId) {
                    try {
                        await credentialVaultService.recordUsage(
                            resolvedVaultCredentialId,
                            typeof estimatedCostUsd === 'number' ? estimatedCostUsd : 0,
                            1,
                            { enforceLimits: false }
                        );
                    } catch (usageError) {
                        console.warn('[MCP Bridge] Failed to record vault usage after send-prompt (no-wait):', usageError);
                    }
                }
                return res.json({
                    success: true,
                    message: 'Prompt sent successfully',
                    promptLength: prompt.length,
                    waitingForResponse: false
                });
            }

            // Wait for a new response to appear
            const startTime = Date.now();
            let responseText = '';
            let isComplete = false;

            while (Date.now() - startTime < responseTimeout) {
                await new Promise(r => setTimeout(r, 2000)); // Poll every 2 seconds

                // Check if still thinking/streaming
                let isThinking = false;
                for (const thinkSel of selectors.thinking) {
                    try {
                        const thinking = await page.$(thinkSel);
                        if (thinking) {
                            isThinking = true;
                            break;
                        }
                    } catch {
                        continue;
                    }
                }

                // Try to extract the latest response
                try {
                    const respSelector = selectors.response[0];
                    const result = await page.evaluate((sel: string, prevCount: number) => {
                        const elements = document.querySelectorAll(sel);
                        if (elements.length > prevCount) {
                            // Get the last (newest) response
                            const lastEl = elements[elements.length - 1];
                            return {
                                text: lastEl.textContent?.trim() || '',
                                count: elements.length
                            };
                        }
                        return null;
                    }, respSelector, responseCountBefore);

                    if (result && result.text) {
                        responseText = result.text;
                        if (!isThinking) {
                            isComplete = true;
                            break;
                        }
                    }
                } catch {
                    continue;
                }
            }

            // If no content returned, run a second auth check and surface a precise failure category.
            if (!responseText.trim()) {
                const authPostflight = await detectAuthGate(page, provider);
                if (authPostflight.blocked) {
                    return res.status(authPostflight.reason === 'human_check' ? 429 : 401).json({
                        success: false,
                        error: authPostflight.reason === 'human_check'
                            ? `Automation blocked by ${provider} human verification`
                            : `Authentication required for ${provider}`,
                        auth: authPostflight,
                        promptLength: prompt.length,
                        duration: Date.now() - startTime,
                        suggestion: 'Complete login/human check in the visible browser, then retry and save session cookies.'
                    });
                }
            }

            if (resolvedVaultCredentialId) {
                try {
                    await credentialVaultService.recordUsage(
                        resolvedVaultCredentialId,
                        typeof estimatedCostUsd === 'number' ? estimatedCostUsd : 0,
                        1,
                        { enforceLimits: false }
                    );
                } catch (usageError) {
                    console.warn('[MCP Bridge] Failed to record vault usage after send-prompt:', usageError);
                }
            }

            return res.json({
                success: true,
                message: 'Prompt sent and response received',
                promptLength: prompt.length,
                response: responseText,
                isComplete,
                duration: Date.now() - startTime
            });

        } catch (error: any) {
            console.error('[MCP Bridge] send-prompt error:', error);
            return res.status(500).json({
                success: false,
                error: error.message || 'Failed to send prompt'
            });
        }
    });

    /**
     * POST /api/bridge/extract-response
     * Extract the latest response from an AI provider chat
     * 
     * Body: { browserId, provider, index?: number }
     */
    router.post('/extract-response', async (req: Request, res: Response) => {
        try {
            const { browserId, provider, index } = req.body;

            if (!browserId || !provider) {
                return res.status(400).json({
                    success: false,
                    error: 'Missing required fields: browserId, provider'
                });
            }

            const selectors = PROVIDER_SELECTORS[provider];
            if (!selectors) {
                return res.status(400).json({
                    success: false,
                    error: `Unsupported provider: ${provider}`
                });
            }

            const normalizedProvider = normalizeProviderName(provider);
            if (rejectIfAuthReadyMissing(req, res, normalizedProvider, 'extract-response')) {
                return;
            }

            const instance = browserService.getInstance(browserId);
            const page = instance.page;

            // Extract response text
            const result = await page.evaluate((responseSels: string[], targetIndex?: number) => {
                for (const sel of responseSels) {
                    const elements = document.querySelectorAll(sel);
                    if (elements.length > 0) {
                        const idx = targetIndex !== undefined ? targetIndex : elements.length - 1;
                        const el = elements[idx];
                        if (el) {
                            return {
                                text: el.textContent?.trim() || '',
                                totalResponses: elements.length,
                                index: idx,
                                selector: sel
                            };
                        }
                    }
                }
                return null;
            }, selectors.response, index);

            if (!result || !result.text?.trim()) {
                const authState = await detectAuthGate(page, provider);
                if (authState.blocked) {
                    return res.status(authState.reason === 'human_check' ? 429 : 401).json({
                        success: false,
                        error: authState.reason === 'human_check'
                            ? `Automation blocked by ${provider} human verification`
                            : `Authentication required for ${provider}`,
                        auth: authState,
                        suggestion: 'Complete login/human check in the visible browser and retry extraction.'
                    });
                }

                return res.json({
                    success: true,
                    response: null,
                    message: 'No response found on page'
                });
            }

            return res.json({
                success: true,
                response: result.text,
                metadata: {
                    totalResponses: result.totalResponses,
                    index: result.index,
                    selector: result.selector
                }
            });

        } catch (error: any) {
            console.error('[MCP Bridge] extract-response error:', error);
            return res.status(500).json({
                success: false,
                error: error.message || 'Failed to extract response'
            });
        }
    });

    /**
     * GET /api/bridge/providers
     * List supported providers and their selector configurations
     */
    router.get('/providers', (_req: Request, res: Response) => {
        const providers = Object.entries(PROVIDER_SELECTORS).map(([name, sels]) => ({
            name,
            inputSelectors: sels.input.length,
            submitSelectors: sels.submit.length,
            responseSelectors: sels.response.length,
            url: name === 'chatgpt' ? 'https://chatgpt.com' :
                name === 'gemini' ? 'https://gemini.google.com' :
                    name === 'claude' ? 'https://claude.ai' : 'unknown'
        }));

        res.json({
            success: true,
            providers,
            total: providers.length
        });
    });

    /**
     * POST /api/bridge/full-session
     * Complete flow: launch browser → load session → verify → send prompt → extract response
     * 
     * Body: { accountId, prompt, headless?: boolean, estimatedCostUsd?: number }
     */
    router.post('/full-session', async (req: Request, res: Response) => {
        let browserId: string | null = null;

        try {
            const { accountId, prompt, headless = false, estimatedCostUsd = 0 } = req.body;

            if (!accountId || !prompt) {
                return res.status(400).json({
                    success: false,
                    error: 'Missing required fields: accountId, prompt'
                });
            }

            // 1. Get account to determine provider
            const account = await connectionManager.getAccount(accountId);
            if (!account) {
                return res.status(404).json({
                    success: false,
                    error: `Account not found: ${accountId}`
                });
            }

            const provider = account.provider;
            const providerUrl = provider === 'chatgpt' ? 'https://chatgpt.com' :
                provider === 'gemini' ? 'https://gemini.google.com' :
                    provider === 'claude' ? 'https://claude.ai' : null;

            if (!providerUrl) {
                return res.status(400).json({
                    success: false,
                    error: `Unknown provider for account: ${provider}`
                });
            }

            const normalizedProvider = normalizeProviderName(provider);
            if (rejectIfAuthReadyMissing(req, res, normalizedProvider, 'full-session')) {
                return;
            }

            // Optional vault-backed usage gate via account.vaultCredentialId.
            const accountVaultCredentialId = account.vaultCredentialId || null;
            if (accountVaultCredentialId) {
                const usageGate = await credentialVaultService.checkUsageLimit(
                    accountVaultCredentialId,
                    typeof estimatedCostUsd === 'number' ? estimatedCostUsd : 0,
                    1
                );
                if (!usageGate.allowed) {
                    return res.status(429).json({
                        success: false,
                        error: `Vault usage limit exceeded for ${provider}: ${usageGate.reason}`,
                        vaultCredentialId: accountVaultCredentialId,
                        usage: usageGate
                    });
                }
            }

            // 2. Launch browser
            browserId = await browserService.launchBrowser({
                headless,
                viewport: { width: 1280, height: 800 }
            });

            // 3. Load session cookies
            await connectionManager.loadSession(accountId, browserId, browserService);

            // 4. Navigate to provider
            await browserService.navigateTo(browserId, providerUrl);
            await new Promise(r => setTimeout(r, 3000)); // Wait for redirects

            // 5. Verify session
            const isLoggedIn = await connectionManager.verifySession(accountId, browserId, browserService);
            if (!isLoggedIn) {
                return res.status(401).json({
                    success: false,
                    error: `Session expired or invalid for ${provider}. Please run the login script first.`,
                    browserId // Keep browser open for manual login
                });
            }

            // 6. Send prompt
            const selectors = PROVIDER_SELECTORS[provider];
            const inst = browserService.getInstance(browserId);
            const inputSelector = await findSelector(inst.page, selectors.input);

            if (!inputSelector) {
                return res.status(500).json({
                    success: false,
                    error: 'Could not find chat input after login verification',
                    browserId
                });
            }

            // Type and submit
            await browserService.type(browserId, inputSelector, prompt, true);
            await new Promise(r => setTimeout(r, 500));
            const submitSelector = await findSelector(inst.page, selectors.submit, 3000);
            if (submitSelector) {
                await inst.page.click(submitSelector);
            } else {
                await inst.page.keyboard.press('Enter');
            }

            // Wait for response
            await new Promise(r => setTimeout(r, 5000)); // Initial wait

            // Poll for response completion
            let responseText = '';
            const maxWait = 60000;
            const pollStart = Date.now();

            while (Date.now() - pollStart < maxWait) {
                await new Promise(r => setTimeout(r, 2000));

                try {
                    const result = await inst.page.evaluate((sel: string) => {
                        const elements = document.querySelectorAll(sel);
                        if (elements.length > 0) {
                            return elements[elements.length - 1].textContent?.trim() || '';
                        }
                        return '';
                    }, selectors.response[0]);

                    if (result && result.length > responseText.length) {
                        responseText = result;
                    } else if (result && result === responseText && responseText.length > 0) {
                        break; // Response stopped growing
                    }
                } catch {
                    continue;
                }
            }

            // Save updated session cookies
            await connectionManager.saveSession(accountId, browserId, browserService);

            if (account.vaultCredentialId) {
                try {
                    await credentialVaultService.recordUsage(
                        account.vaultCredentialId,
                        typeof estimatedCostUsd === 'number' ? estimatedCostUsd : 0,
                        1,
                        { enforceLimits: false }
                    );
                } catch (usageError) {
                    console.warn('[MCP Bridge] Failed to record vault usage after full-session:', usageError);
                }
            }

            return res.json({
                success: true,
                provider,
                prompt: prompt.substring(0, 100) + (prompt.length > 100 ? '...' : ''),
                response: responseText,
                browserId, // Return so caller can reuse or close
                sessionSaved: true
            });

        } catch (error: any) {
            console.error('[MCP Bridge] full-session error:', error);
            return res.status(500).json({
                success: false,
                error: error.message || 'Full session flow failed',
                browserId
            });
        }
    });

    /**
     * POST /api/bridge/start-new-chat
     * Start a fresh conversation by clicking the "New Chat" button
     * 
     * Body: { browserId, provider }
     */
    router.post('/start-new-chat', async (req: Request, res: Response) => {
        try {
            const { browserId, provider } = req.body;

            if (!browserId || !provider) {
                return res.status(400).json({
                    success: false,
                    error: 'Missing required fields: browserId, provider'
                });
            }

            const { getProviderConfig } = require('../../../shared/providerSelectors');
            const config = getProviderConfig(provider);
            if (!config?.selectors?.newChatButton) {
                return res.status(400).json({
                    success: false,
                    error: `No newChatButton selector for provider: ${provider}`
                });
            }

            const instance = browserService.getInstance(browserId);
            const page = instance.page;

            // Build selector chain: primary + fallbacks
            const allSelectors = [
                config.selectors.newChatButton.selector,
                ...config.selectors.newChatButton.fallbacks
            ];

            const selector = await findSelector(page, allSelectors, 5000);
            if (!selector) {
                return res.status(404).json({
                    success: false,
                    error: `Could not find new chat button for ${provider}`
                });
            }

            await page.click(selector);
            await new Promise(r => setTimeout(r, 1500)); // Wait for navigation

            console.log(`[MCP Bridge] Started new chat for ${provider}`);

            return res.json({
                success: true,
                provider,
                message: 'New chat started'
            });

        } catch (error: any) {
            console.error('[MCP Bridge] start-new-chat error:', error);
            return res.status(500).json({
                success: false,
                error: error.message || 'Failed to start new chat'
            });
        }
    });

    /**
     * POST /api/bridge/select-model
     * Select a specific model from the model selector dropdown
     * 
     * Body: { browserId, provider, model }
     */
    router.post('/select-model', async (req: Request, res: Response) => {
        try {
            const { browserId, provider, model } = req.body;

            if (!browserId || !provider || !model) {
                return res.status(400).json({
                    success: false,
                    error: 'Missing required fields: browserId, provider, model'
                });
            }

            const { getProviderConfig } = require('../../../shared/providerSelectors');
            const config = getProviderConfig(provider);
            if (!config?.selectors?.modelSelector) {
                return res.status(400).json({
                    success: false,
                    error: `No modelSelector for provider: ${provider}`
                });
            }

            const instance = browserService.getInstance(browserId);
            const page = instance.page;

            // 1. Click the model selector to open the dropdown
            const allSelectors = [
                config.selectors.modelSelector.selector,
                ...config.selectors.modelSelector.fallbacks
            ];

            const selector = await findSelector(page, allSelectors, 5000);
            if (!selector) {
                return res.status(404).json({
                    success: false,
                    error: `Could not find model selector for ${provider}`
                });
            }

            await page.click(selector);
            await new Promise(r => setTimeout(r, 1000)); // Wait for dropdown

            // 2. Find and click the target model option
            // Try to match by text content (case-insensitive partial match)
            const modelSelected = await page.evaluate((modelName: string) => {
                const options = document.querySelectorAll('[role="option"], [role="menuitem"], [data-testid*="model"], li, button');
                for (const opt of options) {
                    const text = (opt as HTMLElement).textContent?.toLowerCase() || '';
                    if (text.includes(modelName.toLowerCase())) {
                        (opt as HTMLElement).click();
                        return true;
                    }
                }
                return false;
            }, model);

            if (!modelSelected) {
                // Close dropdown by pressing Escape
                await page.keyboard.press('Escape');
                return res.status(404).json({
                    success: false,
                    error: `Model "${model}" not found in dropdown for ${provider}`,
                    availableModels: config.capabilities.availableModels
                });
            }

            await new Promise(r => setTimeout(r, 500)); // Wait for model switch

            console.log(`[MCP Bridge] Selected model "${model}" for ${provider}`);

            return res.json({
                success: true,
                provider,
                model,
                message: `Model set to ${model}`
            });

        } catch (error: any) {
            console.error('[MCP Bridge] select-model error:', error);
            return res.status(500).json({
                success: false,
                error: error.message || 'Failed to select model'
            });
        }
    });

    /**
     * GET /api/bridge/capabilities
     * Get the full capability matrix for all providers
     */
    router.get('/capabilities', (_req: Request, res: Response) => {
        const { PROVIDER_REGISTRY } = require('../../../shared/providerSelectors');
        const capabilities: Record<string, any> = {};

        for (const [key, config] of Object.entries(PROVIDER_REGISTRY)) {
            const cfg = config as any;
            capabilities[key] = {
                name: cfg.name,
                url: cfg.url,
                capabilities: cfg.capabilities,
                selectorCount: Object.keys(cfg.selectors).length,
            };
        }

        return res.json({ success: true, providers: capabilities });
    });

    /**
     * GET /api/bridge/page-health
     * Measure DOM health metrics for detecting long-chat degradation
     * 
     * Query: browserId, provider
     */
    router.get('/page-health', async (req: Request, res: Response) => {
        try {
            const { browserId, provider } = req.query;

            if (!browserId || !provider) {
                return res.status(400).json({
                    success: false,
                    error: 'Missing required query params: browserId, provider'
                });
            }

            const instance = browserService.getInstance(browserId as string);
            const page = instance.page;

            // Gather DOM health metrics via page.evaluate
            const health = await page.evaluate(() => {
                const allElements = document.querySelectorAll('*').length;
                const messageElements = document.querySelectorAll(
                    '[data-message-author-role], .message, message-content, .response-container, .font-claude-message'
                ).length;
                const scrollHeight = document.documentElement.scrollHeight;
                const viewportHeight = window.innerHeight;

                // Memory info (Chrome only)
                let heapUsedMB = 0;
                let heapTotalMB = 0;
                if ((performance as any).memory) {
                    heapUsedMB = Math.round((performance as any).memory.usedJSHeapSize / 1024 / 1024);
                    heapTotalMB = Math.round((performance as any).memory.totalJSHeapSize / 1024 / 1024);
                }

                // Count images (can cause memory pressure)
                const imageCount = document.querySelectorAll('img, svg, canvas').length;

                // Detect MathJax/LaTeX (heavy rendering)
                const mathElements = document.querySelectorAll('.katex, mjx-container, .MathJax').length;

                return {
                    totalDOMNodes: allElements,
                    messageCount: messageElements,
                    scrollHeight,
                    viewportHeight,
                    scrollRatio: Math.round(scrollHeight / viewportHeight * 10) / 10,
                    heapUsedMB,
                    heapTotalMB,
                    imageCount,
                    mathElements,
                };
            });

            // Verify selectors are still valid
            const selectors = PROVIDER_SELECTORS[provider as string];
            let selectorHealth = { input: false, submit: false, response: false };
            if (selectors) {
                selectorHealth.input = !!(await findSelector(page, selectors.input, 2000));
                selectorHealth.submit = !!(await findSelector(page, selectors.submit, 2000));
                selectorHealth.response = !!(await findSelector(page, selectors.response, 2000));
            }

            // Compute overall health score (0-100)
            let score = 100;
            if (health.totalDOMNodes > 5000) score -= 10;
            if (health.totalDOMNodes > 10000) score -= 20;
            if (health.totalDOMNodes > 20000) score -= 30;
            if (health.messageCount > 30) score -= 10;
            if (health.messageCount > 60) score -= 20;
            if (health.heapUsedMB > 200) score -= 10;
            if (health.heapUsedMB > 500) score -= 20;
            if (!selectorHealth.input) score -= 15;
            if (!selectorHealth.submit) score -= 10;
            score = Math.max(0, score);

            const status = score >= 70 ? 'healthy' : score >= 40 ? 'degraded' : 'critical';

            console.log(`[MCP Bridge] Page health for ${provider}: ${score}/100 (${status}), ${health.totalDOMNodes} DOM nodes, ${health.messageCount} messages`);

            return res.json({
                success: true,
                provider,
                health: {
                    ...health,
                    selectorHealth,
                    score,
                    status,
                    recommendation: status === 'critical'
                        ? 'Start a new conversation immediately'
                        : status === 'degraded'
                            ? 'Consider starting a new conversation soon'
                            : 'Page is healthy',
                }
            });

        } catch (error: any) {
            console.error('[MCP Bridge] page-health error:', error);
            return res.status(500).json({
                success: false,
                error: error.message || 'Failed to check page health'
            });
        }
    });

    /**
     * GET /api/bridge/web-diagnostics
     * Deep diagnostics snapshot for auth walls, anti-bot checks, selector drift, and runtime bottlenecks.
     *
     * Query: browserId, provider
     */
    router.get('/web-diagnostics', async (req: Request, res: Response) => {
        try {
            const { browserId, provider } = req.query;

            if (!browserId || !provider) {
                return res.status(400).json({
                    success: false,
                    error: 'Missing required query params: browserId, provider'
                });
            }

            const providerKey = String(provider);
            const selectorSet = PROVIDER_SELECTORS[providerKey];
            if (!selectorSet) {
                return res.status(400).json({
                    success: false,
                    error: `Unsupported provider: ${providerKey}. Supported: ${Object.keys(PROVIDER_SELECTORS).join(', ')}`
                });
            }

            const instance = browserService.getInstance(String(browserId));
            const page = instance.page;
            const auth = await detectAuthGate(page, providerKey);

            const snapshot = await page.evaluate((selectors: { input: string[]; submit: string[]; response: string[]; thinking: string[]; }) => {
                const isVisible = (el: Element): boolean => {
                    const rect = (el as HTMLElement).getBoundingClientRect();
                    if (rect.width === 0 || rect.height === 0) return false;
                    const style = window.getComputedStyle(el as HTMLElement);
                    return style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0';
                };

                const auditGroup = (name: string, selectorList: string[]) => {
                    const perSelector = selectorList.map(sel => {
                        try {
                            const nodes = Array.from(document.querySelectorAll(sel));
                            const visible = nodes.filter(isVisible).length;
                            return { selector: sel, matches: nodes.length, visible };
                        } catch {
                            return { selector: sel, matches: 0, visible: 0, invalid: true };
                        }
                    });

                    const firstMatched = perSelector.find(s => s.matches > 0)?.selector || null;
                    const totalMatches = perSelector.reduce((acc, s: any) => acc + s.matches, 0);
                    const visibleMatches = perSelector.reduce((acc, s: any) => acc + s.visible, 0);

                    return {
                        group: name,
                        firstMatched,
                        totalMatches,
                        visibleMatches,
                        perSelector: perSelector.slice(0, 12),
                    };
                };

                const selectorAudit = {
                    input: auditGroup('input', selectors.input || []),
                    submit: auditGroup('submit', selectors.submit || []),
                    response: auditGroup('response', selectors.response || []),
                    thinking: auditGroup('thinking', selectors.thinking || []),
                };

                const bodyText = (document.body?.innerText || '').toLowerCase();
                const challengeSignals = [
                    'verify you are human',
                    'are you human',
                    'captcha',
                    'cf-turnstile',
                    'cloudflare',
                    'unusual traffic',
                ].filter(token => bodyText.includes(token));

                const allNodes = document.querySelectorAll('*').length;
                const messageNodes = document.querySelectorAll(
                    '[data-message-author-role], .message, message-content, .response-container, .font-claude-message'
                ).length;
                const scrollHeight = document.documentElement.scrollHeight;
                const viewportHeight = window.innerHeight;

                const overlayCandidates = Array.from(document.querySelectorAll(
                    '[aria-modal="true"], dialog, [role="dialog"], [class*="modal"], [class*="overlay"], [id*="cookie"], [class*="cookie"]'
                )).slice(0, 200);

                const viewportArea = Math.max(1, window.innerWidth * window.innerHeight);
                const overlays = overlayCandidates
                    .map(el => {
                        const rect = (el as HTMLElement).getBoundingClientRect();
                        const style = window.getComputedStyle(el as HTMLElement);
                        const areaRatio = Math.round(((rect.width * rect.height) / viewportArea) * 1000) / 1000;
                        return {
                            tag: el.tagName.toLowerCase(),
                            id: (el as HTMLElement).id || undefined,
                            className: ((el as HTMLElement).className || '').toString().substring(0, 120) || undefined,
                            text: ((el as HTMLElement).innerText || '').trim().substring(0, 120) || undefined,
                            visible: isVisible(el),
                            areaRatio,
                            position: style.position,
                            zIndex: style.zIndex,
                        };
                    })
                    .filter(o => o.visible && (o.position === 'fixed' || o.position === 'sticky' || o.areaRatio >= 0.2))
                    .sort((a, b) => b.areaRatio - a.areaRatio)
                    .slice(0, 12);

                const resourceEntries = (performance.getEntriesByType('resource') || []) as any[];
                const slowResources = resourceEntries
                    .map(r => ({
                        name: String(r.name || '').substring(0, 180),
                        initiatorType: r.initiatorType || 'unknown',
                        durationMs: Math.round((r.duration || 0) * 10) / 10,
                        transferSize: r.transferSize || 0,
                    }))
                    .sort((a, b) => b.durationMs - a.durationMs)
                    .slice(0, 12);

                const byType = resourceEntries.reduce((acc: Record<string, number>, r: any) => {
                    const key = r.initiatorType || 'other';
                    acc[key] = (acc[key] || 0) + 1;
                    return acc;
                }, {});

                const nav = (performance.getEntriesByType('navigation') || [])[0] as any;
                const timing = nav ? {
                    domContentLoadedMs: Math.round((nav.domContentLoadedEventEnd || 0) * 10) / 10,
                    loadMs: Math.round((nav.loadEventEnd || 0) * 10) / 10,
                    responseEndMs: Math.round((nav.responseEnd || 0) * 10) / 10,
                } : null;

                let heapUsedMB = 0;
                let heapTotalMB = 0;
                if ((performance as any).memory) {
                    heapUsedMB = Math.round((performance as any).memory.usedJSHeapSize / 1024 / 1024);
                    heapTotalMB = Math.round((performance as any).memory.totalJSHeapSize / 1024 / 1024);
                }

                const loginActions = Array.from(document.querySelectorAll('button, a'))
                    .map(el => ((el as HTMLElement).innerText || '').trim())
                    .filter(Boolean)
                    .filter(t => /log in|login|sign up|signup/i.test(t))
                    .slice(0, 10);

                return {
                    url: window.location.href,
                    title: document.title,
                    readyState: document.readyState,
                    dom: {
                        totalNodes: allNodes,
                        messageNodes,
                        scrollHeight,
                        viewportHeight,
                        scrollRatio: Math.round((scrollHeight / Math.max(1, viewportHeight)) * 10) / 10,
                    },
                    overlays,
                    challengeSignals,
                    loginActions,
                    selectorAudit,
                    performance: {
                        timing,
                        heapUsedMB,
                        heapTotalMB,
                        resourceCount: resourceEntries.length,
                        slowResources,
                        resourcesByType: byType,
                    },
                };
            }, selectorSet);

            const runtime = browserService.getRuntimeDiagnostics(String(browserId));
            const statusBreakdown = runtime.httpErrors.reduce((acc: Record<string, number>, item) => {
                const key = String(item.status);
                acc[key] = (acc[key] || 0) + 1;
                return acc;
            }, {});

            // Risk score: focus on blockers that break autonomous interactions.
            let riskScore = 0;
            if (auth.blocked) riskScore += auth.reason === 'human_check' ? 55 : 45;
            if ((snapshot.challengeSignals?.length || 0) > 0) riskScore += 30;
            if ((snapshot.overlays?.length || 0) > 0) riskScore += 10;
            if ((snapshot.selectorAudit.input.totalMatches || 0) === 0) riskScore += 20;
            if ((snapshot.selectorAudit.submit.totalMatches || 0) === 0) riskScore += 10;
            if ((runtime.requestFailures?.length || 0) > 0) riskScore += Math.min(20, runtime.requestFailures.length / 2);
            if ((runtime.httpErrors?.length || 0) > 0) riskScore += Math.min(20, runtime.httpErrors.length / 2);
            riskScore = Math.min(100, Math.round(riskScore));

            const riskLevel = riskScore >= 80
                ? 'critical'
                : riskScore >= 55
                    ? 'high'
                    : riskScore >= 30
                        ? 'moderate'
                        : 'low';

            return res.json({
                success: true,
                provider: providerKey,
                browserId,
                risk: {
                    score: riskScore,
                    level: riskLevel,
                    rationale: [
                        auth.blocked ? `auth_blocked:${auth.reason}` : null,
                        (snapshot.challengeSignals?.length || 0) > 0 ? 'challenge_signals_present' : null,
                        (snapshot.selectorAudit.input.totalMatches || 0) === 0 ? 'input_selector_missing' : null,
                        (snapshot.selectorAudit.submit.totalMatches || 0) === 0 ? 'submit_selector_missing' : null,
                        (runtime.httpErrors?.length || 0) > 0 ? 'http_errors_detected' : null,
                        (runtime.requestFailures?.length || 0) > 0 ? 'request_failures_detected' : null,
                    ].filter(Boolean),
                },
                auth,
                page: snapshot,
                runtime: {
                    totals: {
                        responsesObserved: runtime.totalResponses,
                        consoleEvents: runtime.consoleEvents.length,
                        pageErrors: runtime.pageErrors.length,
                        requestFailures: runtime.requestFailures.length,
                        httpErrors: runtime.httpErrors.length,
                    },
                    statusBreakdown,
                    recent: {
                        consoleEvents: runtime.consoleEvents.slice(-20),
                        pageErrors: runtime.pageErrors.slice(-20),
                        requestFailures: runtime.requestFailures.slice(-20),
                        httpErrors: runtime.httpErrors.slice(-20),
                    },
                    lastUpdated: runtime.lastUpdated,
                },
                recommendation: auth.blocked
                    ? 'Complete login/human-check in visible browser, then rerun diagnostics and save session.'
                    : riskLevel === 'critical' || riskLevel === 'high'
                        ? 'Investigate selector drift, overlays, and failing network requests before autonomous runs.'
                        : 'Diagnostics look stable for automation.',
            });
        } catch (error: any) {
            console.error('[MCP Bridge] web-diagnostics error:', error);
            return res.status(500).json({
                success: false,
                error: error.message || 'Failed to generate web diagnostics'
            });
        }
    });

    /**
     * POST /api/bridge/cleanup-dom
     * Remove off-screen message nodes to reduce DOM bloat
     * (Mainly for ChatGPT long conversations)
     * 
     * Body: { browserId, provider, keepLastN?: number }
     */
    router.post('/cleanup-dom', async (req: Request, res: Response) => {
        try {
            const { browserId, provider, keepLastN = 10 } = req.body;

            if (!browserId || !provider) {
                return res.status(400).json({
                    success: false,
                    error: 'Missing required fields: browserId, provider'
                });
            }

            const instance = browserService.getInstance(browserId);
            const page = instance.page;

            // Provider-specific cleanup selectors
            const messageSelectors: Record<string, string> = {
                chatgpt: '[data-testid^="conversation-turn"]',
                gemini: '.conversation-container > *',
                claude: '[class*="message"]',
            };

            const messageSelector = messageSelectors[provider] || '[data-message-author-role]';

            const result = await page.evaluate((sel: string, keep: number) => {
                const messages = document.querySelectorAll(sel);
                const totalBefore = messages.length;
                const removeCount = Math.max(0, totalBefore - keep);

                // Remove oldest messages (keep lastN)
                for (let i = 0; i < removeCount; i++) {
                    messages[i]?.remove();
                }

                // Force garbage collection hint
                const nodeCountAfter = document.querySelectorAll('*').length;

                return {
                    totalBefore,
                    removed: removeCount,
                    remaining: totalBefore - removeCount,
                    domNodesAfter: nodeCountAfter,
                };
            }, messageSelector, keepLastN);

            console.log(`[MCP Bridge] DOM cleanup for ${provider}: removed ${result.removed} of ${result.totalBefore} messages, ${result.domNodesAfter} DOM nodes remain`);

            return res.json({
                success: true,
                provider,
                cleanup: result,
            });

        } catch (error: any) {
            console.error('[MCP Bridge] cleanup-dom error:', error);
            return res.status(500).json({
                success: false,
                error: error.message || 'Failed to cleanup DOM'
            });
        }
    });

    /**
     * POST /api/bridge/auto-rotate
     * Check page health and auto-start new conversation if degraded
     * 
     * Body: { browserId, provider, healthThreshold?: number }
     */
    router.post('/auto-rotate', async (req: Request, res: Response) => {
        try {
            const { browserId, provider, healthThreshold = 40 } = req.body;

            if (!browserId || !provider) {
                return res.status(400).json({
                    success: false,
                    error: 'Missing required fields: browserId, provider'
                });
            }

            // First check health
            const instance = browserService.getInstance(browserId);
            const page = instance.page;

            const domNodes = await page.evaluate(() => document.querySelectorAll('*').length);
            const messageCount = await page.evaluate(() =>
                document.querySelectorAll('[data-message-author-role], .message, message-content, .response-container').length
            );

            let score = 100;
            if (domNodes > 5000) score -= 10;
            if (domNodes > 10000) score -= 20;
            if (domNodes > 20000) score -= 30;
            if (messageCount > 30) score -= 10;
            if (messageCount > 60) score -= 20;
            score = Math.max(0, score);

            if (score >= healthThreshold) {
                return res.json({
                    success: true,
                    rotated: false,
                    reason: `Health score ${score} is above threshold ${healthThreshold}`,
                    health: { domNodes, messageCount, score },
                });
            }

            // Health is below threshold — rotate to new chat
            const { getProviderConfig } = require('../../../shared/providerSelectors');
            const config = getProviderConfig(provider);

            if (!config?.selectors?.newChatButton) {
                return res.json({
                    success: false,
                    rotated: false,
                    reason: `No newChatButton selector for ${provider}`,
                });
            }

            const allSelectors = [
                config.selectors.newChatButton.selector,
                ...config.selectors.newChatButton.fallbacks
            ];

            const selector = await findSelector(page, allSelectors, 5000);
            if (!selector) {
                return res.json({
                    success: false,
                    rotated: false,
                    reason: `Could not find new chat button for ${provider}`,
                });
            }

            await page.click(selector);
            await new Promise(r => setTimeout(r, 1500));

            console.log(`[MCP Bridge] Auto-rotated ${provider}: score was ${score}, ${messageCount} messages, ${domNodes} DOM nodes`);

            return res.json({
                success: true,
                rotated: true,
                reason: `Health score ${score} was below threshold ${healthThreshold}`,
                health: { domNodes, messageCount, score },
            });

        } catch (error: any) {
            console.error('[MCP Bridge] auto-rotate error:', error);
            return res.status(500).json({
                success: false,
                error: error.message || 'Failed to auto-rotate'
            });
        }
    });

    return router;
}
