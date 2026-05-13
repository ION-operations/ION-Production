// ═══════════════════════════════════════════════════════════════
// TypeScript declarations for the JOC Electron IPC bridge
// Exposed as window.jocBridge by the preload script
// ═══════════════════════════════════════════════════════════════

export interface JOCBridge {
    isElectron: true;
    platform: NodeJS.Platform;

    window: {
        minimize: () => void;
        maximize: () => void;
        close: () => void;
    };

    session: {
        getCookies: (provider: string) => Promise<{
            success: boolean;
            cookies?: Array<{ name: string; domain: string; expirationDate?: number }>;
            error?: string;
        }>;
        clear: (provider: string) => Promise<{ success: boolean; error?: string }>;
    };

    webview: {
        executeJS: (webviewId: string, code: string) => Promise<{ success: boolean; result?: unknown; error?: string }>;
        getElementRect: (webviewId: string, selector: string) => Promise<{
            success: boolean;
            rect?: { x: number; y: number; width: number; height: number };
            error?: string;
        }>;
    };

    on: (channel: string, callback: (...args: unknown[]) => void) => void;
    removeAllListeners: (channel: string) => void;
}

declare global {
    interface Window {
        jocBridge?: JOCBridge;
    }
}
