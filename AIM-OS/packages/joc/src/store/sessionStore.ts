import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import * as basClient from '../services/basClient';
import { encryptedStorage, partitionSessionState, mergeSessionState } from '../services/sessionPersist';

// ─── Session Types ───

export type AIProvider = 'chatgpt' | 'gemini' | 'claude' | 'perplexity' | 'gemini-cli' | 'local';
export type SessionStatus = 'connected' | 'connecting' | 'disconnected' | 'error' | 'injecting' | 'extracting';
export type OverlayElement = 'injection-point' | 'extraction-zone' | 'nav-element' | 'session-indicator';
export type EventSeverity = 'info' | 'success' | 'warning' | 'error';
export type PipelineStage = 'idle' | 'packaging' | 'injecting' | 'waiting' | 'extracting' | 'routing' | 'complete' | 'failed';

export interface OverlayMarker {
    id: string;
    type: OverlayElement;
    label: string;
    x: number;      // % position on viewport
    y: number;
    width: number;   // % size
    height: number;
    status: 'healthy' | 'changed' | 'missing' | 'active';
    selector?: string; // CSS selector that targets this element
}

export interface SessionEvent {
    id: string;
    timestamp: string;
    message: string;
    severity: EventSeverity;
    stage?: PipelineStage;
    data?: Record<string, unknown>;
}

export interface PipelineState {
    stage: PipelineStage;
    progress: number;      // 0-100
    tokensIn?: number;
    tokensOut?: number;
    startTime?: string;
    elapsed?: string;
}

export interface AttachedFile {
    id: string;
    name: string;
    path: string;
    size: number;
    tokenEstimate: number;
}

export interface ConversationTurn {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    tokens: number;
    timestamp: string;
    provider?: string;
}

export interface SessionState {
    // Connection
    provider: AIProvider;
    sessionId: string;
    status: SessionStatus;
    url: string;
    health: number;
    uptime: string;

    // BAS integration
    browserId?: string;        // Puppeteer browser ID from BAS
    basConnected: boolean;     // Whether BAS is reachable
    lastResponse?: string;     // Latest extracted response text

    // Automation overlay
    overlayVisible: boolean;
    overlayMarkers: OverlayMarker[];

    // Pipeline
    pipeline: PipelineState;

    // Events
    events: SessionEvent[];
    maxEvents: number;

    // Context
    attachedFiles: AttachedFile[];
    promptDraft: string;

    // Viewport
    viewportScale: number;
    lastScreenshot?: string;   // Base64 screenshot from BAS

    // Conversation history
    conversation: ConversationTurn[];
}

// ─── Mock Session Data ───

const CHATGPT_MARKERS: OverlayMarker[] = [
    {
        id: 'inject-textarea',
        type: 'injection-point',
        label: 'Prompt Input',
        x: 15, y: 82, width: 62, height: 10,
        status: 'healthy',
        selector: '#prompt-textarea',
    },
    {
        id: 'extract-response',
        type: 'extraction-zone',
        label: 'Response Area',
        x: 15, y: 12, width: 70, height: 65,
        status: 'healthy',
        selector: '[data-message-author-role="assistant"]',
    },
    {
        id: 'nav-model-selector',
        type: 'nav-element',
        label: 'Model Selector',
        x: 15, y: 3, width: 20, height: 5,
        status: 'healthy',
        selector: 'button[data-testid="model-selector"]',
    },
    {
        id: 'session-indicator',
        type: 'session-indicator',
        label: 'Login Status',
        x: 88, y: 3, width: 8, height: 5,
        status: 'healthy',
        selector: '[data-testid="profile-button"]',
    },
];

const GEMINI_MARKERS: OverlayMarker[] = [
    {
        id: 'inject-input',
        type: 'injection-point',
        label: 'Prompt Input',
        x: 20, y: 85, width: 55, height: 8,
        status: 'healthy',
        selector: '.ql-editor',
    },
    {
        id: 'extract-response',
        type: 'extraction-zone',
        label: 'Response Area',
        x: 20, y: 10, width: 60, height: 70,
        status: 'healthy',
        selector: '.response-container',
    },
    {
        id: 'nav-model',
        type: 'nav-element',
        label: 'Model Switch',
        x: 5, y: 5, width: 15, height: 5,
        status: 'healthy',
        selector: '.model-selector',
    },
    {
        id: 'session-indicator',
        type: 'session-indicator',
        label: 'Account Status',
        x: 90, y: 3, width: 6, height: 5,
        status: 'healthy',
        selector: '.gb_d',
    },
];

const INITIAL_EVENTS: SessionEvent[] = [
    { id: 'e1', timestamp: '10:08:42', message: 'Session initialized', severity: 'info', stage: 'idle' },
    { id: 'e2', timestamp: '10:08:43', message: 'DOM selectors verified — 4/4 healthy', severity: 'success' },
    { id: 'e3', timestamp: '10:08:44', message: 'Login status: authenticated', severity: 'success' },
    { id: 'e4', timestamp: '10:08:45', message: 'Model: GPT-4o detected', severity: 'info' },
    { id: 'e5', timestamp: '10:08:46', message: 'Ready for dispatch', severity: 'info', stage: 'idle' },
];

// ─── Store ───

interface SessionStoreState {
    sessions: Record<string, SessionState>;
    activeSessionId: string | null;

    // Actions
    setActiveSession: (id: string) => void;
    toggleOverlay: (sessionId: string) => void;
    setMarkerStatus: (sessionId: string, markerId: string, status: OverlayMarker['status']) => void;
    addEvent: (sessionId: string, event: Omit<SessionEvent, 'id'>) => void;
    setPipelineStage: (sessionId: string, stage: PipelineStage, progress?: number) => void;
    updatePromptDraft: (sessionId: string, text: string) => void;
    attachFile: (sessionId: string, file: AttachedFile) => void;
    removeFile: (sessionId: string, fileId: string) => void;

    updateSession: (sessionId: string, updates: Partial<SessionState>) => void;
    addConversationTurn: (sessionId: string, turn: Omit<ConversationTurn, 'id'>) => void;
    launchSession: (sessionId: string) => Promise<void>;
    injectPrompt: (sessionId: string, prompt: string) => Promise<void>;
    extractResponse: (sessionId: string) => Promise<string | null>;
    captureScreenshot: (sessionId: string) => Promise<string | null>;
    refreshBASStatus: (sessionId: string) => Promise<void>;
}

export const useSessionStore = create<SessionStoreState>()(
    (persist as any)(
        (set: any, get: any) => ({
            sessions: {
                'chatgpt-session': {
                    provider: 'chatgpt',
                    sessionId: 'chatgpt-session',
                    status: 'disconnected',
                    url: 'https://chatgpt.com/',
                    health: 0,
                    uptime: '—',
                    basConnected: false,
                    overlayVisible: true,
                    overlayMarkers: CHATGPT_MARKERS,
                    pipeline: { stage: 'idle', progress: 0 },
                    events: [...INITIAL_EVENTS],
                    maxEvents: 100,
                    attachedFiles: [],
                    promptDraft: '',
                    viewportScale: 1,
                    conversation: [],
                },
                'gemini-session': {
                    provider: 'gemini',
                    sessionId: 'gemini-session',
                    status: 'disconnected',
                    url: 'https://gemini.google.com/',
                    health: 0,
                    uptime: '—',
                    basConnected: false,
                    overlayVisible: true,
                    overlayMarkers: GEMINI_MARKERS,
                    pipeline: { stage: 'idle', progress: 0 },
                    events: [
                        { id: 'g1', timestamp: '10:10:00', message: 'Session initialized', severity: 'info' },
                        { id: 'g2', timestamp: '10:10:01', message: 'DOM selectors verified — 4/4 healthy', severity: 'success' },
                        { id: 'g3', timestamp: '10:10:02', message: 'Google account: authenticated', severity: 'success' },
                        { id: 'g4', timestamp: '10:10:03', message: 'Model: Gemini Ultra detected', severity: 'info' },
                        { id: 'g5', timestamp: '10:10:04', message: 'Ready for dispatch', severity: 'info' },
                    ],
                    maxEvents: 100,
                    attachedFiles: [],
                    promptDraft: '',
                    viewportScale: 1,
                    conversation: [],
                },
            },
            activeSessionId: 'chatgpt-session',

            setActiveSession: (id: string) => set({ activeSessionId: id }),

            toggleOverlay: (sessionId: string) => {
                const sessions = { ...get().sessions };
                if (sessions[sessionId]) {
                    sessions[sessionId] = { ...sessions[sessionId], overlayVisible: !sessions[sessionId].overlayVisible };
                    set({ sessions });
                }
            },

            setMarkerStatus: (sessionId: string, markerId: string, status: 'pending' | 'running' | 'done' | 'error') => {
                const sessions = { ...get().sessions };
                if (sessions[sessionId]) {
                    sessions[sessionId] = {
                        ...sessions[sessionId],
                        overlayMarkers: sessions[sessionId].overlayMarkers.map((m: any) =>
                            m.id === markerId ? { ...m, status } : m
                        ),
                    };
                    set({ sessions });
                }
            },

            addEvent: (sessionId: string, event: Omit<SessionEvent, 'id'>) => {
                const sessions = { ...get().sessions };
                if (sessions[sessionId]) {
                    const newEvent = { ...event, id: `e-${Date.now()}-${Math.random().toString(36).slice(2, 6)}` };
                    const events = [...sessions[sessionId].events, newEvent].slice(-sessions[sessionId].maxEvents);
                    sessions[sessionId] = { ...sessions[sessionId], events };
                    set({ sessions });
                }
            },

            setPipelineStage: (sessionId: string, stage: PipelineStage, progress: number = 0) => {
                const sessions = { ...get().sessions };
                if (sessions[sessionId]) {
                    sessions[sessionId] = {
                        ...sessions[sessionId],
                        pipeline: { ...sessions[sessionId].pipeline, stage, progress },
                        status: stage === 'injecting' ? 'injecting' : stage === 'extracting' ? 'extracting' : sessions[sessionId].status === 'injecting' || sessions[sessionId].status === 'extracting' ? 'connected' : sessions[sessionId].status,
                    };
                    set({ sessions });
                }
            },

            updatePromptDraft: (sessionId: string, text: string) => {
                const sessions = { ...get().sessions };
                if (sessions[sessionId]) {
                    sessions[sessionId] = { ...sessions[sessionId], promptDraft: text };
                    set({ sessions });
                }
            },

            attachFile: (sessionId: string, file: AttachedFile) => {
                const sessions = { ...get().sessions };
                if (sessions[sessionId]) {
                    sessions[sessionId] = { ...sessions[sessionId], attachedFiles: [...sessions[sessionId].attachedFiles, file] };
                    set({ sessions });
                }
            },

            removeFile: (sessionId: string, fileId: string) => {
                const sessions = { ...get().sessions };
                if (sessions[sessionId]) {
                    sessions[sessionId] = { ...sessions[sessionId], attachedFiles: sessions[sessionId].attachedFiles.filter((f: AttachedFile) => f.id !== fileId) };
                    set({ sessions });
                }
            },


            // ─── BAS Live Actions (real browser automation) ───

            updateSession: (sessionId: string, updates: Partial<SessionState>) => {
                const sessions = { ...get().sessions };
                if (sessions[sessionId]) {
                    sessions[sessionId] = { ...sessions[sessionId], ...updates };
                    set({ sessions });
                }
            },

            addConversationTurn: (sessionId: string, turn: Omit<ConversationTurn, 'id'>) => {
                const sessions = { ...get().sessions };
                if (sessions[sessionId]) {
                    sessions[sessionId] = {
                        ...sessions[sessionId],
                        conversation: [
                            ...sessions[sessionId].conversation,
                            { ...turn, id: `turn-${Date.now()}-${Math.random().toString(36).slice(2, 6)}` },
                        ],
                    };
                    set({ sessions });
                }
            },

            launchSession: async (sessionId: string) => {
                const store = get();
                const session = store.sessions[sessionId];
                if (!session) return;

                const ts = () => new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });

                // Check BAS health first
                store.addEvent(sessionId, { timestamp: ts(), message: 'Checking BAS connection...', severity: 'info' });
                store.updateSession(sessionId, { status: 'connecting' });

                try {
                    const health = await basClient.checkHealth();
                    store.updateSession(sessionId, { basConnected: health.status === 'ok' });
                    store.addEvent(sessionId, { timestamp: ts(), message: `BAS online — ${health.uptime || 'ready'}`, severity: 'success' });
                } catch {
                    store.updateSession(sessionId, { basConnected: false, status: 'error' });
                    store.addEvent(sessionId, { timestamp: ts(), message: 'BAS offline — cannot launch browser', severity: 'error' });
                    return;
                }

                // Launch browser
                store.addEvent(sessionId, { timestamp: ts(), message: 'Launching Puppeteer browser...', severity: 'info' });

                try {
                    const result = await basClient.launchBrowser({ headless: false, viewport: { width: 1280, height: 800 } });
                    const browserId = result.browserId;
                    if (!browserId) {
                        store.updateSession(sessionId, { status: 'error' });
                        store.addEvent(sessionId, { timestamp: ts(), message: 'Launch returned no browserId', severity: 'error' });
                        return;
                    }
                    store.updateSession(sessionId, { browserId });
                    store.addEvent(sessionId, { timestamp: ts(), message: `Browser launched: ${browserId}`, severity: 'success' });

                    // Navigate to provider
                    store.addEvent(sessionId, { timestamp: ts(), message: `Navigating to ${session.url}...`, severity: 'info' });
                    await basClient.navigate(browserId, session.url);
                    store.updateSession(sessionId, { status: 'connected', health: 80 });
                    store.addEvent(sessionId, { timestamp: ts(), message: `Navigation complete — ready`, severity: 'success' });

                    // Start a fresh conversation (prevents context pollution between missions)
                    try {
                        store.addEvent(sessionId, { timestamp: ts(), message: 'Starting new conversation...', severity: 'info' });
                        await basClient.startNewChat(browserId, session.provider);
                        store.addEvent(sessionId, { timestamp: ts(), message: 'New conversation started', severity: 'success' });
                    } catch {
                        store.addEvent(sessionId, { timestamp: ts(), message: 'New chat button not found — using current chat', severity: 'warning' });
                    }

                    // Capture initial screenshot
                    try {
                        const screenshot = await basClient.getScreenshot(browserId, 'png');
                        if (screenshot) {
                            store.updateSession(sessionId, { lastScreenshot: screenshot });
                        }
                    } catch { /* screenshot is optional */ }

                } catch (err: any) {
                    store.updateSession(sessionId, { status: 'error' });
                    store.addEvent(sessionId, { timestamp: ts(), message: `Launch failed: ${err.message}`, severity: 'error' });
                }
            },

            injectPrompt: async (sessionId: string, prompt: string) => {
                const store = get();
                const session = store.sessions[sessionId];
                if (!session?.browserId) {
                    store.addEvent(sessionId, {
                        timestamp: new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }),
                        message: 'No browser launched — click Launch first',
                        severity: 'warning',
                    });
                    return;
                }

                const ts = () => new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });

                // Pipeline: packaging
                store.setPipelineStage(sessionId, 'packaging', 10);
                store.addEvent(sessionId, { timestamp: ts(), message: `Packaging prompt (${prompt.length} chars)...`, severity: 'info', stage: 'packaging' });
                store.setMarkerStatus(sessionId, 'inject-textarea', 'active');
                store.setMarkerStatus(sessionId, 'inject-input', 'active');

                // Record user conversation turn
                store.addConversationTurn(sessionId, {
                    role: 'user',
                    content: prompt,
                    tokens: Math.ceil(prompt.length / 4),
                    timestamp: ts(),
                });

                // Pipeline: injecting
                store.setPipelineStage(sessionId, 'injecting', 40);
                store.addEvent(sessionId, { timestamp: ts(), message: 'Sending prompt via BAS...', severity: 'info', stage: 'injecting' });

                try {
                    const result = await basClient.sendPrompt({
                        browserId: session.browserId,
                        prompt,
                        provider: session.provider,
                        waitForResponse: true,
                        responseTimeout: 60000,
                    });

                    // Pipeline: waiting → complete
                    store.setPipelineStage(sessionId, 'waiting', 70);
                    store.addEvent(sessionId, { timestamp: ts(), message: 'Prompt injected — waiting for response...', severity: 'info', stage: 'waiting' });

                    if (result.response) {
                        store.setPipelineStage(sessionId, 'complete', 100);
                        store.updateSession(sessionId, { lastResponse: result.response });
                        store.addEvent(sessionId, {
                            timestamp: ts(),
                            message: `Response received (${result.response.length} chars, ${result.duration || 0}ms)`,
                            severity: 'success',
                            stage: 'complete',
                        });
                        store.setMarkerStatus(sessionId, 'extract-response', 'active');

                        // Record assistant conversation turn
                        store.addConversationTurn(sessionId, {
                            role: 'assistant',
                            content: result.response,
                            tokens: Math.ceil(result.response.length / 4),
                            timestamp: ts(),
                            provider: session.provider,
                        });
                    } else {
                        store.setPipelineStage(sessionId, 'complete', 100);
                        store.addEvent(sessionId, { timestamp: ts(), message: 'Prompt sent (no response captured)', severity: 'warning', stage: 'complete' });
                    }

                    // Capture screenshot of response
                    try {
                        const screenshot = await basClient.getScreenshot(session.browserId, 'png');
                        if (screenshot) store.updateSession(sessionId, { lastScreenshot: screenshot });
                    } catch { /* optional */ }

                    // Proactive DOM health check — auto-rotate if page is degraded
                    try {
                        const rotateResult = await basClient.autoRotate(session.browserId, session.provider, 50);
                        if (rotateResult.rotated) {
                            store.addEvent(sessionId, {
                                timestamp: ts(),
                                message: `♻ Auto-rotated conversation (health ${rotateResult.health.score}/100, ${rotateResult.health.messageCount} msgs, ${rotateResult.health.domNodes} DOM nodes)`,
                                severity: 'warning',
                            });
                        }
                    } catch { /* auto-rotate is best-effort */ }

                    // Reset markers after delay
                    setTimeout(() => {
                        store.setMarkerStatus(sessionId, 'inject-textarea', 'healthy');
                        store.setMarkerStatus(sessionId, 'inject-input', 'healthy');
                        store.setMarkerStatus(sessionId, 'extract-response', 'healthy');
                        store.setPipelineStage(sessionId, 'idle', 0);
                    }, 2000);

                } catch (err: any) {
                    store.setPipelineStage(sessionId, 'failed', 0);
                    store.addEvent(sessionId, { timestamp: ts(), message: `Injection failed: ${err.message}`, severity: 'error', stage: 'failed' });
                    store.setMarkerStatus(sessionId, 'inject-textarea', 'missing');
                    store.setMarkerStatus(sessionId, 'inject-input', 'missing');
                }
            },

            extractResponse: async (sessionId: string) => {
                const store = get();
                const session = store.sessions[sessionId];
                if (!session?.browserId) return null;

                const ts = () => new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });

                store.setPipelineStage(sessionId, 'extracting', 30);
                store.addEvent(sessionId, { timestamp: ts(), message: 'Extracting response via BAS...', severity: 'info', stage: 'extracting' });
                store.setMarkerStatus(sessionId, 'extract-response', 'active');

                try {
                    const result = await basClient.extractResponse({
                        browserId: session.browserId,
                        provider: session.provider,
                    });

                    if (result.response) {
                        store.setPipelineStage(sessionId, 'routing', 70);
                        store.addEvent(sessionId, {
                            timestamp: ts(),
                            message: `Extracted (${result.response.length} chars, index ${result.metadata?.index ?? '?'})`,
                            severity: 'success',
                            stage: 'routing',
                        });
                        store.updateSession(sessionId, { lastResponse: result.response });

                        store.setPipelineStage(sessionId, 'complete', 100);
                        store.addEvent(sessionId, { timestamp: ts(), message: 'Response stored → ready', severity: 'success', stage: 'complete' });

                        setTimeout(() => {
                            store.setPipelineStage(sessionId, 'idle', 0);
                            store.setMarkerStatus(sessionId, 'extract-response', 'healthy');
                        }, 1500);

                        return result.response;
                    } else {
                        store.addEvent(sessionId, { timestamp: ts(), message: 'No response found on page', severity: 'warning' });
                        store.setPipelineStage(sessionId, 'idle', 0);
                        return null;
                    }
                } catch (err: any) {
                    store.addEvent(sessionId, { timestamp: ts(), message: `Extraction failed: ${err.message}`, severity: 'error' });
                    store.setPipelineStage(sessionId, 'idle', 0);
                    store.setMarkerStatus(sessionId, 'extract-response', 'missing');
                    return null;
                }
            },

            captureScreenshot: async (sessionId: string) => {
                const session = get().sessions[sessionId];
                if (!session?.browserId) return null;

                try {
                    const screenshot = await basClient.getScreenshot(session.browserId, 'png');
                    if (screenshot) {
                        get().updateSession(sessionId, { lastScreenshot: screenshot });
                    }
                    return screenshot;
                } catch {
                    return null;
                }
            },

            refreshBASStatus: async (sessionId: string) => {
                const store = get();
                const session = store.sessions[sessionId];
                if (!session) return;

                try {
                    const health = await basClient.checkHealth();
                    store.updateSession(sessionId, { basConnected: health.status === 'ok' });

                    if (session.browserId) {
                        const status = await basClient.getBrowserStatus(session.browserId);
                        const browserStatus = status.status?.status;
                        const isAlive = browserStatus === 'idle' || browserStatus === 'navigating' || browserStatus === 'automating';
                        store.updateSession(sessionId, {
                            status: isAlive ? 'connected' : 'disconnected',
                            health: isAlive ? 85 : 0,
                            url: status.status?.url || session.url,
                        });
                    }
                } catch {
                    store.updateSession(sessionId, { basConnected: false });
                }
            },
        }),
        {
            name: 'aim-os-sessions',
            storage: createJSONStorage(() => encryptedStorage as any),
            partialize: partitionSessionState,
            merge: (persisted: unknown, current: SessionStoreState) => mergeSessionState(persisted, current),
        },
    ),
);
