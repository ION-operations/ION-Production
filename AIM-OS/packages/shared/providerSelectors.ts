/**
 * ═══════════════════════════════════════════════════════════════
 * AIM-OS Provider Selector Registry — Single Source of Truth
 * 
 * This file is the ONLY place DOM selectors for AI providers
 * should be defined. Both systems import from here:
 * 
 *   System A: JOC Native Drivers (aiDrivers.ts)  → Electron <webview>
 *   System B: BAS Microservice (mcpBridge.ts)     → Puppeteer
 * 
 * When a provider (ChatGPT, Gemini, Claude) changes their DOM,
 * update selectors HERE ONCE and both systems stay in sync.
 * ═══════════════════════════════════════════════════════════════
 */

// ─── Core Types ───

/** Individual selector with description and fallback chain */
export interface DOMSelector {
    /** Primary CSS selector */
    selector: string;
    /** Human-readable description of what this targets */
    description: string;
    /** Fallback selectors tried in order if primary fails */
    fallbacks: string[];
}

/** Complete selector set for interacting with an AI provider */
export interface ProviderSelectorConfig {
    /** Provider identifier */
    provider: string;
    /** Human-readable provider name */
    name: string;
    /** Provider chat URL */
    url: string;
    /** Selectors for core interaction elements */
    selectors: {
        /** Where to type/inject prompts */
        promptInput: DOMSelector;
        /** Button to submit the prompt */
        sendButton: DOMSelector;
        /** Area where AI responses appear */
        responseArea: DOMSelector;
        /** Model selection UI (if available) */
        modelSelector?: DOMSelector;
        /** Element indicating user is logged in */
        loginIndicator: DOMSelector;
        /** Element indicating response is being streamed */
        streamingIndicator?: DOMSelector;
        /** Button/link to start a new conversation */
        newChatButton?: DOMSelector;
        /** File upload trigger (paperclip/attachment button) */
        fileUploadButton?: DOMSelector;
        /** Conversation list in the sidebar */
        conversationList?: DOMSelector;
    };
    /** Provider capabilities */
    capabilities: {
        supportsStreaming: boolean;
        supportsFileUpload: boolean;
        supportsSystemPrompt: boolean;
        maxTokensPerMessage: number;
        supportsNewChat: boolean;
        supportsModelSelection: boolean;
        supportsGoogleDrive: boolean;
        supportsGitHub: boolean;
        /** Known models available via web UI */
        availableModels: string[];
    };
}

// ─── ChatGPT ───

export const CHATGPT_SELECTORS: ProviderSelectorConfig = {
    provider: 'chatgpt',
    name: 'ChatGPT',
    url: 'https://chatgpt.com/',
    selectors: {
        promptInput: {
            selector: '#prompt-textarea',
            description: 'Main prompt textarea',
            fallbacks: ['textarea[data-id="root"]', '[contenteditable="true"]', 'textarea'],
        },
        sendButton: {
            selector: 'button[data-testid="send-button"]',
            description: 'Send message button',
            fallbacks: ['button[aria-label="Send prompt"]', 'button svg path[d*="M15.1918"]'],
        },
        responseArea: {
            selector: '[data-message-author-role="assistant"]:last-child',
            description: 'Latest assistant response',
            fallbacks: ['.markdown.prose', '.agent-turn .markdown', '.agent-turn:last-child'],
        },
        modelSelector: {
            selector: 'button[data-testid="model-selector"]',
            description: 'Model selection dropdown',
            fallbacks: ['[class*="model"]'],
        },
        loginIndicator: {
            selector: '[data-testid="profile-button"]',
            description: 'Profile button (indicates logged in)',
            fallbacks: ['img[alt*="User"]', 'button[aria-label*="profile"]'],
        },
        streamingIndicator: {
            selector: '[data-testid="stop-button"]',
            description: 'Stop generation button (visible during streaming)',
            fallbacks: ['button[aria-label="Stop generating"]', '.result-thinking', '.text-token-text-secondary', '[data-testid="thinking"]'],
        },
        newChatButton: {
            selector: 'a[href="/"]',
            description: 'New chat link (sidebar or header)',
            fallbacks: ['nav a[href="/"]', 'button[data-testid="new-chat-button"]', 'a[data-testid="create-new-chat-button"]'],
        },
        fileUploadButton: {
            selector: 'button[aria-label="Attach files"]',
            description: 'Paperclip/attachment button',
            fallbacks: ['button[data-testid="composer-attach-button"]', '[aria-label="Upload file"]', 'input[type="file"]'],
        },
        conversationList: {
            selector: 'nav ol',
            description: 'Conversation history list in sidebar',
            fallbacks: ['nav [data-testid*="conversation"]', '.scrollbar-trigger ol'],
        },
    },
    capabilities: {
        supportsStreaming: true,
        supportsFileUpload: true,
        supportsSystemPrompt: false,
        maxTokensPerMessage: 128000,
        supportsNewChat: true,
        supportsModelSelection: true,
        supportsGoogleDrive: false,
        supportsGitHub: true,
        availableModels: ['gpt-4o', 'gpt-4o-mini', 'o3-mini', 'o3', 'gpt-4.1'],
    },
};

// ─── Gemini ───

export const GEMINI_SELECTORS: ProviderSelectorConfig = {
    provider: 'gemini',
    name: 'Gemini',
    url: 'https://gemini.google.com/',
    selectors: {
        promptInput: {
            selector: 'rich-textarea .ql-editor',
            description: 'Prompt input area (Quill editor)',
            fallbacks: ['.ql-editor', 'rich-textarea', '.text-input-field textarea', '[contenteditable="true"][aria-label*="prompt"]', 'textarea', '[contenteditable="true"]'],
        },
        sendButton: {
            selector: 'button[aria-label="Send message"]',
            description: 'Send button',
            fallbacks: ['button.send-button', '.send-button-container button', 'button[mattooltip="Send"]'],
        },
        responseArea: {
            selector: '.response-container .markdown',
            description: 'Latest model response',
            fallbacks: ['.response-container:last-child', '.model-response-text:last-child', 'message-content .markdown', '.response-container-content:last-child', 'message-content:last-of-type'],
        },
        modelSelector: {
            selector: '.model-selector',
            description: 'Model selection',
            fallbacks: ['[data-test-id="model-selector"]'],
        },
        loginIndicator: {
            selector: '.gb_d',
            description: 'Google account avatar',
            fallbacks: ['a[aria-label*="Account"]', 'img[data-noaft]', '[data-ogsr-up]'],
        },
        streamingIndicator: {
            selector: '.loading-indicator',
            description: 'Response streaming indicator',
            fallbacks: ['.streaming-indicator', '[aria-label="Stop"]', '.thinking-indicator'],
        },
        newChatButton: {
            selector: 'button[aria-label="New chat"]',
            description: 'New chat button',
            fallbacks: ['a[href="/app"]', 'button.new-chat', '[data-test-id="new-chat"]'],
        },
        fileUploadButton: {
            selector: 'button[aria-label="Add files"]',
            description: 'File attachment button',
            fallbacks: ['button[aria-label="Upload a file"]', '[aria-label="Add image"]', 'input[type="file"]'],
        },
        conversationList: {
            selector: '.conversation-list',
            description: 'Conversation history sidebar',
            fallbacks: ['[role="list"]', '.chat-history'],
        },
    },
    capabilities: {
        supportsStreaming: true,
        supportsFileUpload: true,
        supportsSystemPrompt: true,
        maxTokensPerMessage: 1000000,
        supportsNewChat: true,
        supportsModelSelection: true,
        supportsGoogleDrive: true,
        supportsGitHub: false,
        availableModels: ['gemini-2.5-pro', 'gemini-2.5-flash', 'gemini-2.0-flash'],
    },
};

// ─── Claude ───

export const CLAUDE_SELECTORS: ProviderSelectorConfig = {
    provider: 'claude',
    name: 'Claude',
    url: 'https://claude.ai/',
    selectors: {
        promptInput: {
            selector: '[contenteditable="true"].ProseMirror',
            description: 'ProseMirror prompt editor',
            fallbacks: ['textarea', '[contenteditable="true"]'],
        },
        sendButton: {
            selector: 'button[aria-label="Send Message"]',
            description: 'Send message button',
            fallbacks: ['button.send-button'],
        },
        responseArea: {
            selector: '.font-claude-message',
            description: 'Claude response area',
            fallbacks: ['[data-is-streaming]', '.prose'],
        },
        loginIndicator: {
            selector: 'button[data-testid="user-menu"]',
            description: 'User menu button (indicates logged in)',
            fallbacks: ['[class*="avatar"]', 'img[alt*="User"]'],
        },
        streamingIndicator: {
            selector: '[data-is-streaming="true"]',
            description: 'Streaming indicator',
            fallbacks: ['.animate-pulse'],
        },
        newChatButton: {
            selector: 'a[href="/new"]',
            description: 'New chat link',
            fallbacks: ['button[data-testid="new-chat-button"]', 'a[data-testid="new-thread-button"]', '[aria-label="Start new chat"]'],
        },
        fileUploadButton: {
            selector: 'button[aria-label="Attach file"]',
            description: 'File attachment button',
            fallbacks: ['button[data-testid="file-upload"]', '[aria-label="Upload content"]', 'input[type="file"]'],
        },
        modelSelector: {
            selector: 'button[data-testid="model-selector"]',
            description: 'Model selection dropdown',
            fallbacks: ['[class*="model-selector"]', 'button[aria-haspopup="listbox"]'],
        },
        conversationList: {
            selector: 'nav[aria-label="Chat history"]',
            description: 'Chat history sidebar',
            fallbacks: ['[data-testid="chat-history"]', '.conversation-list'],
        },
    },
    capabilities: {
        supportsStreaming: true,
        supportsFileUpload: true,
        supportsSystemPrompt: true,
        maxTokensPerMessage: 200000,
        supportsNewChat: true,
        supportsModelSelection: true,
        supportsGoogleDrive: false,
        supportsGitHub: false,
        availableModels: ['claude-4-sonnet', 'claude-3.5-sonnet', 'claude-3.5-haiku'],
    },
};

// ─── Registry ───

export type ProviderKey = 'chatgpt' | 'gemini' | 'claude';

/** Master registry — all providers */
export const PROVIDER_REGISTRY: Record<ProviderKey, ProviderSelectorConfig> = {
    chatgpt: CHATGPT_SELECTORS,
    gemini: GEMINI_SELECTORS,
    claude: CLAUDE_SELECTORS,
};

/** Get provider config, or null if unknown */
export function getProviderConfig(provider: string): ProviderSelectorConfig | null {
    return PROVIDER_REGISTRY[provider as ProviderKey] || null;
}

// ─── BAS-Compatible Flat Selector Arrays ───
// Helper that converts structured DOMSelector → BAS ordered array format

export interface FlatSelectors {
    input: string[];
    submit: string[];
    response: string[];
    thinking: string[];
}

/** Convert a ProviderSelectorConfig to the flat array format used by BAS/mcpBridge */
export function toFlatSelectors(config: ProviderSelectorConfig): FlatSelectors {
    const s = config.selectors;
    return {
        input: [s.promptInput.selector, ...s.promptInput.fallbacks],
        submit: [s.sendButton.selector, ...s.sendButton.fallbacks],
        response: [s.responseArea.selector, ...s.responseArea.fallbacks],
        thinking: s.streamingIndicator
            ? [s.streamingIndicator.selector, ...s.streamingIndicator.fallbacks]
            : [],
    };
}

/** Get all providers as flat selector maps (drop-in replacement for BAS PROVIDER_SELECTORS) */
export function getAllFlatSelectors(): Record<string, FlatSelectors> {
    const result: Record<string, FlatSelectors> = {};
    for (const [key, config] of Object.entries(PROVIDER_REGISTRY)) {
        result[key] = toFlatSelectors(config);
    }
    return result;
}
