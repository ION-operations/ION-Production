// ═══════════════════════════════════════════════════════════════
// JOC AI Drivers — Abstract Interface + ChatGPT/Gemini Implementations
//
// Drivers know how to interact with specific AI provider pages:
//   - Where to inject prompts (CSS selectors)
//   - Where to extract responses
//   - How to detect session state (logged in, model selected, etc.)
//   - How to verify DOM health
//
// SELECTOR SOURCE: packages/shared/providerSelectors.ts
// All DOM selectors are imported from the shared registry.
// When providers update their DOM, update selectors THERE.
// ═══════════════════════════════════════════════════════════════

import type { OverlayMarker, AIProvider, SessionEvent } from '../store/sessionStore';
import {
    CHATGPT_SELECTORS,
    GEMINI_SELECTORS,
    CLAUDE_SELECTORS,
    type DOMSelector,
    type ProviderSelectorConfig,
} from '../../../shared/providerSelectors';

// ─── Abstract Driver Interface ───
// DOMSelector is now imported from shared/providerSelectors
export type { DOMSelector } from '../../../shared/providerSelectors';

export interface DriverConfig extends ProviderSelectorConfig {
    partition: string;      // Electron session partition (JOC-specific)
}

export interface HealthCheck {
    selector: string;
    found: boolean;
    rect?: { x: number; y: number; width: number; height: number };
}

export interface AIDriver {
    config: DriverConfig;

    // Health & status
    checkHealth: (webview: HTMLElement) => Promise<HealthCheck[]>;
    isLoggedIn: (webview: HTMLElement) => Promise<boolean>;
    getModel: (webview: HTMLElement) => Promise<string | null>;

    // Core actions
    injectPrompt: (webview: HTMLElement, prompt: string) => Promise<boolean>;
    triggerSend: (webview: HTMLElement) => Promise<boolean>;
    extractResponse: (webview: HTMLElement) => Promise<string | null>;
    isStreaming: (webview: HTMLElement) => Promise<boolean>;

    // Overlay
    getOverlayMarkers: (webview: HTMLElement) => Promise<OverlayMarker[]>;
}

// ─── Helper: Execute JS in webview ───

async function executeInWebview(webview: HTMLElement, code: string): Promise<unknown> {
    // In Electron, <webview> elements have executeJavaScript
    const wv = webview as unknown as { executeJavaScript: (code: string) => Promise<unknown> };
    if (typeof wv.executeJavaScript === 'function') {
        return wv.executeJavaScript(code);
    }
    // Fallback for dev mode (non-Electron) — return null
    console.warn('[AIDriver] executeJavaScript not available — running in browser mode');
    return null;
}

// ─── ChatGPT Driver ───
// Selectors imported from shared registry

export const ChatGPTDriverConfig: DriverConfig = {
    ...CHATGPT_SELECTORS,
    partition: 'persist:joc-chatgpt',
};

export const ChatGPTDriver: AIDriver = {
    config: ChatGPTDriverConfig,

    checkHealth: async (webview) => {
        const selectors = ChatGPTDriverConfig.selectors;
        const checks: HealthCheck[] = [];

        for (const [_key, sel] of Object.entries(selectors)) {
            if (!sel) continue;
            const result = await executeInWebview(webview, `
        (() => {
          const el = document.querySelector('${sel.selector}');
          if (!el) return null;
          const rect = el.getBoundingClientRect();
          return { x: rect.x, y: rect.y, width: rect.width, height: rect.height };
        })()
      `);
            checks.push({
                selector: sel.selector,
                found: result !== null,
                rect: result as HealthCheck['rect'] || undefined,
            });
        }
        return checks;
    },

    isLoggedIn: async (webview) => {
        const sel = ChatGPTDriverConfig.selectors.loginIndicator;
        const found = await executeInWebview(webview, `
      !!document.querySelector('${sel.selector}')
    `);
        return found === true;
    },

    getModel: async (webview) => {
        const sel = ChatGPTDriverConfig.selectors.modelSelector;
        if (!sel) return null;
        const model = await executeInWebview(webview, `
      (() => {
        const btn = document.querySelector('${sel.selector}');
        return btn ? btn.textContent?.trim() : null;
      })()
    `);
        return model as string | null;
    },

    injectPrompt: async (webview, prompt) => {
        const sel = ChatGPTDriverConfig.selectors.promptInput;
        const escaped = prompt.replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/\n/g, '\\n');
        const result = await executeInWebview(webview, `
      (() => {
        const el = document.querySelector('${sel.selector}');
        if (!el) return false;
        // ChatGPT uses a ProseMirror editor — set innerHTML as paragraph
        el.innerHTML = '<p>${escaped}</p>';
        el.dispatchEvent(new Event('input', { bubbles: true }));
        return true;
      })()
    `);
        return result === true;
    },

    triggerSend: async (webview) => {
        const sel = ChatGPTDriverConfig.selectors.sendButton;
        const result = await executeInWebview(webview, `
      (() => {
        const btn = document.querySelector('${sel.selector}');
        if (!btn) return false;
        btn.click();
        return true;
      })()
    `);
        return result === true;
    },

    extractResponse: async (webview) => {
        const sel = ChatGPTDriverConfig.selectors.responseArea;
        const text = await executeInWebview(webview, `
      (() => {
        const el = document.querySelector('${sel.selector}');
        return el ? el.textContent : null;
      })()
    `);
        return text as string | null;
    },

    isStreaming: async (webview) => {
        const sel = ChatGPTDriverConfig.selectors.streamingIndicator;
        if (!sel) return false;
        const found = await executeInWebview(webview, `
      !!document.querySelector('${sel.selector}')
    `);
        return found === true;
    },

    getOverlayMarkers: async (webview) => {
        // Get actual bounding rects from the live page
        const viewportSize = await executeInWebview(webview, `
      ({ width: window.innerWidth, height: window.innerHeight })
    `) as { width: number; height: number } | null;

        if (!viewportSize) {
            // Return default markers if we can't query the DOM
            return [];
        }

        const markers: OverlayMarker[] = [];
        const selectorEntries = Object.entries(ChatGPTDriverConfig.selectors);

        for (const [key, sel] of selectorEntries) {
            if (!sel) continue;
            const rect = await executeInWebview(webview, `
        (() => {
          const el = document.querySelector('${sel.selector}');
          if (!el) return null;
          const r = el.getBoundingClientRect();
          return { x: r.x, y: r.y, width: r.width, height: r.height };
        })()
      `) as { x: number; y: number; width: number; height: number } | null;

            const typeMap: Record<string, OverlayMarker['type']> = {
                promptInput: 'injection-point',
                sendButton: 'nav-element',
                responseArea: 'extraction-zone',
                modelSelector: 'nav-element',
                loginIndicator: 'session-indicator',
                streamingIndicator: 'nav-element',
            };

            markers.push({
                id: `chatgpt-${key}`,
                type: typeMap[key] || 'nav-element',
                label: sel.description,
                x: rect ? (rect.x / viewportSize.width) * 100 : 0,
                y: rect ? (rect.y / viewportSize.height) * 100 : 0,
                width: rect ? (rect.width / viewportSize.width) * 100 : 0,
                height: rect ? (rect.height / viewportSize.height) * 100 : 0,
                status: rect ? 'healthy' : 'missing',
                selector: sel.selector,
            });
        }

        return markers;
    },
};

// ─── Gemini Driver ───
// Selectors imported from shared registry

export const GeminiDriverConfig: DriverConfig = {
    ...GEMINI_SELECTORS,
    partition: 'persist:joc-gemini',
};

// Gemini driver uses the same pattern as ChatGPT — just different selectors
export const GeminiDriver: AIDriver = {
    config: GeminiDriverConfig,

    checkHealth: async (webview) => {
        const selectors = GeminiDriverConfig.selectors;
        const checks: HealthCheck[] = [];
        for (const [_key, sel] of Object.entries(selectors)) {
            if (!sel) continue;
            const result = await executeInWebview(webview, `
        (() => {
          const el = document.querySelector('${sel.selector.split(',')[0].trim()}');
          if (!el) return null;
          const rect = el.getBoundingClientRect();
          return { x: rect.x, y: rect.y, width: rect.width, height: rect.height };
        })()
      `);
            checks.push({ selector: sel.selector, found: result !== null, rect: result as HealthCheck['rect'] || undefined });
        }
        return checks;
    },

    isLoggedIn: async (webview) => {
        const sel = GeminiDriverConfig.selectors.loginIndicator;
        const found = await executeInWebview(webview, `!!document.querySelector('${sel.selector.split(',')[0].trim()}')`);
        return found === true;
    },

    getModel: async (webview) => {
        const sel = GeminiDriverConfig.selectors.modelSelector;
        if (!sel) return null;
        const model = await executeInWebview(webview, `
      (() => { const btn = document.querySelector('${sel.selector.split(',')[0].trim()}'); return btn ? btn.textContent?.trim() : null; })()
    `);
        return model as string | null;
    },

    injectPrompt: async (webview, prompt) => {
        const escaped = prompt.replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/\n/g, '\\n');
        const sel = GeminiDriverConfig.selectors.promptInput;
        const result = await executeInWebview(webview, `
      (() => {
        const el = document.querySelector('${sel.selector.split(',')[0].trim()}');
        if (!el) return false;
        el.innerHTML = '<p>${escaped}</p>';
        el.dispatchEvent(new Event('input', { bubbles: true }));
        return true;
      })()
    `);
        return result === true;
    },

    triggerSend: async (webview) => {
        const sel = GeminiDriverConfig.selectors.sendButton;
        const result = await executeInWebview(webview, `
      (() => { const btn = document.querySelector('${sel.selector.split(',')[0].trim()}'); if (!btn) return false; btn.click(); return true; })()
    `);
        return result === true;
    },

    extractResponse: async (webview) => {
        const sel = GeminiDriverConfig.selectors.responseArea;
        const text = await executeInWebview(webview, `
      (() => { const el = document.querySelector('${sel.selector.split(',')[0].trim()}'); return el ? el.textContent : null; })()
    `);
        return text as string | null;
    },

    isStreaming: async (webview) => {
        const sel = GeminiDriverConfig.selectors.streamingIndicator;
        if (!sel) return false;
        const found = await executeInWebview(webview, `!!document.querySelector('${sel.selector.split(',')[0].trim()}')`);
        return found === true;
    },

    getOverlayMarkers: async (webview) => {
        const viewportSize = await executeInWebview(webview, `({ width: window.innerWidth, height: window.innerHeight })`) as { width: number; height: number } | null;
        if (!viewportSize) return [];
        const markers: OverlayMarker[] = [];
        const typeMap: Record<string, OverlayMarker['type']> = {
            promptInput: 'injection-point', sendButton: 'nav-element', responseArea: 'extraction-zone',
            modelSelector: 'nav-element', loginIndicator: 'session-indicator', streamingIndicator: 'nav-element',
        };
        for (const [key, sel] of Object.entries(GeminiDriverConfig.selectors)) {
            if (!sel) continue;
            const primarySel = sel.selector.split(',')[0].trim();
            const rect = await executeInWebview(webview, `
        (() => { const el = document.querySelector('${primarySel}'); if (!el) return null; const r = el.getBoundingClientRect(); return { x: r.x, y: r.y, width: r.width, height: r.height }; })()
      `) as { x: number; y: number; width: number; height: number } | null;
            markers.push({
                id: `gemini-${key}`, type: typeMap[key] || 'nav-element', label: sel.description,
                x: rect ? (rect.x / viewportSize.width) * 100 : 0, y: rect ? (rect.y / viewportSize.height) * 100 : 0,
                width: rect ? (rect.width / viewportSize.width) * 100 : 0, height: rect ? (rect.height / viewportSize.height) * 100 : 0,
                status: rect ? 'healthy' : 'missing', selector: sel.selector,
            });
        }
        return markers;
    },
};

// ─── Driver Registry ───

export const DRIVERS: Record<AIProvider, AIDriver> = {
    chatgpt: ChatGPTDriver,
    gemini: GeminiDriver,
    claude: ChatGPTDriver,      // Placeholder — Claude uses similar DOM patterns
    perplexity: ChatGPTDriver,  // Placeholder — will need its own driver
    'gemini-cli': GeminiDriver, // CLI doesn't use a browser driver
    local: ChatGPTDriver,       // Local models don't use a browser driver
};

export function getDriver(provider: AIProvider): AIDriver {
    return DRIVERS[provider] || ChatGPTDriver;
}
