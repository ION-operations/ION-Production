import { useEffect, useRef, useState, useCallback } from 'react';
import '../styles/session.css';
import { useSessionStore, type PipelineStage, type SessionState } from '../store/sessionStore';
import { CloseIcon, ChevronDownIcon, BoltIcon, AutomationIcon, ShieldKeyIcon } from '../components/icons';
import * as basClient from '../services/basClient';

// ─── Pipeline Stage Config ───

const PIPELINE_STAGES: Array<{ stage: PipelineStage; label: string }> = [
    { stage: 'idle', label: 'IDLE' },
    { stage: 'packaging', label: 'PACKAGE' },
    { stage: 'injecting', label: 'INJECT' },
    { stage: 'waiting', label: 'WAIT' },
    { stage: 'extracting', label: 'EXTRACT' },
    { stage: 'routing', label: 'ROUTE' },
    { stage: 'complete', label: 'DONE' },
];

// ─── Session SVG Icons ───

function InjectIcon({ size = 13 }: { size?: number }) {
    return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 3v12" />
            <path d="M8 11l4 4 4-4" />
            <rect x="6" y="19" width="12" height="2" rx="1" opacity="0.5" />
        </svg>
    );
}

function ExtractIcon({ size = 13 }: { size?: number }) {
    return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 19V7" />
            <path d="M8 11l4-4 4 4" />
            <rect x="6" y="3" width="12" height="2" rx="1" opacity="0.5" />
        </svg>
    );
}

function RefreshIcon({ size = 13 }: { size?: number }) {
    return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 12a9 9 0 0 1-15.36 6.36" />
            <path d="M3 12a9 9 0 0 1 15.36-6.36" />
            <polyline points="21 3 21 9 15 9" />
            <polyline points="3 21 3 15 9 15" />
        </svg>
    );
}

function EyeIcon({ size = 13 }: { size?: number }) {
    return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
            <circle cx="12" cy="12" r="3" />
        </svg>
    );
}

function FileIcon({ size = 13 }: { size?: number }) {
    return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
        </svg>
    );
}

function ScreenshotIcon({ size = 13 }: { size?: number }) {
    return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <rect x="3" y="3" width="18" height="18" rx="2" />
            <circle cx="12" cy="12" r="3" />
            <path d="M3 9h2" opacity="0.5" />
            <path d="M19 9h2" opacity="0.5" />
        </svg>
    );
}

// Lock icon for URL bar (replaces 🔒 emoji)
function LockIcon({ size = 10 }: { size?: number }) {
    return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
            <path d="M7 11V7a5 5 0 0 1 10 0v4" />
        </svg>
    );
}

// Send arrow icon (replaces 📤 emoji)
function SendIcon({ size = 11 }: { size?: number }) {
    return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="22" y1="2" x2="11" y2="13" />
            <polygon points="22 2 15 22 11 13 2 9 22 2" />
        </svg>
    );
}

// Launch icon (replaces 🚀 emoji)
function LaunchIcon({ size = 13 }: { size?: number }) {
    return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 2L8 8h8L12 2z" />
            <rect x="10" y="8" width="4" height="10" />
            <path d="M8 18l-2 4" opacity="0.5" />
            <path d="M16 18l2 4" opacity="0.5" />
            <path d="M10 18h4" />
        </svg>
    );
}

// Pause icon (replaces ⏸ emoji)
function PauseIcon({ size = 11 }: { size?: number }) {
    return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
            <rect x="6" y="4" width="4" height="16" />
            <rect x="14" y="4" width="4" height="16" />
        </svg>
    );
}

// Play icon (replaces ▶ emoji)
function PlayIcon({ size = 11 }: { size?: number }) {
    return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
            <polygon points="5 3 19 12 5 21 5 3" />
        </svg>
    );
}

// Stop icon (replaces ⏹ emoji)
function StopIcon({ size = 11 }: { size?: number }) {
    return (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
            <rect x="4" y="4" width="16" height="16" rx="2" />
        </svg>
    );
}

// ─── Automation Overlay ───

function ScriptRunner({ session }: { session: SessionState }) {
    const [executionId, setExecutionId] = useState<string | null>(null);
    const [status, setStatus] = useState<basClient.ExecutionStatus | null>(null);
    const [expanded, setExpanded] = useState(true);

    const scripts = basClient.SCRIPT_LIBRARY.filter(
        s => s.provider === session.provider || s.provider === 'custom'
    );

    // Poll execution status
    useEffect(() => {
        if (!executionId) return;
        const interval = setInterval(async () => {
            try {
                const s = await basClient.getExecutionStatus(executionId);
                setStatus(s);
                if (s?.status === 'completed' || s?.status === 'error') {
                    setExecutionId(null);
                }
            } catch { /* BAS offline */ }
        }, 1000);
        return () => clearInterval(interval);
    }, [executionId]);

    const runScript = useCallback(async (script: basClient.LibraryScript) => {
        if (!session.browserId) return;
        try {
            const result = await basClient.executeScript(session.browserId, script.script);
            setExecutionId(result.executionId);
        } catch (err) {
            console.error('Script execution failed:', err);
        }
    }, [session.browserId]);

    return (
        <div className="script-runner">
            <div
                className="script-runner-header"
                onClick={() => setExpanded(!expanded)}
            >
                <span style={{ transform: expanded ? 'rotate(90deg)' : 'rotate(0)', transition: 'transform 0.15s', display: 'inline-block', fontSize: '8px' }}>▸</span>
                <BoltIcon size={10} />
                SCRIPTS
                {executionId && (
                    <span className="script-runner-badge">RUNNING</span>
                )}
            </div>

            {expanded && (
                <div style={{ padding: '0 10px 6px' }}>
                    {/* Active execution */}
                    {executionId && status && (
                        <div className="script-execution">
                            <div className="script-execution-header">
                                <span className="script-execution-step">
                                    Step {status.currentStep}/{status.totalSteps}
                                </span>
                                {status.stepName && (
                                    <span className="script-execution-name">{status.stepName}</span>
                                )}
                                <div style={{ marginLeft: 'auto', display: 'flex', gap: 3 }}>
                                    {status.status === 'running' && (
                                        <button
                                            className="control-btn"
                                            style={{ fontSize: '7px', padding: '1px 5px' }}
                                            onClick={() => basClient.pauseExecution(executionId)}
                                        ><PauseIcon size={9} /></button>
                                    )}
                                    {status.status === 'paused' && (
                                        <button
                                            className="control-btn"
                                            style={{ fontSize: '7px', padding: '1px 5px' }}
                                            onClick={() => basClient.resumeExecution(executionId)}
                                        ><PlayIcon size={9} /></button>
                                    )}
                                    <button
                                        className="control-btn danger"
                                        style={{ fontSize: '7px', padding: '1px 5px' }}
                                        onClick={() => { basClient.stopExecution(executionId); setExecutionId(null); }}
                                    ><StopIcon size={9} /></button>
                                </div>
                            </div>
                            <div className="script-progress-bar">
                                <div className="script-progress-fill" style={{ width: `${status.progress}%` }} />
                            </div>
                        </div>
                    )}

                    {/* Script library */}
                    {scripts.map(script => (
                        <div key={script.id} className="script-item">
                            <span className="script-item-icon">
                                <AutomationIcon size={12} />
                            </span>
                            <div className="script-item-info">
                                <div className="script-item-name">{script.name}</div>
                                <div className="script-item-desc">{script.description}</div>
                            </div>
                            <button
                                className="control-btn"
                                onClick={() => runScript(script)}
                                disabled={!session.browserId || !!executionId}
                                style={{ fontSize: '7px', padding: '2px 6px' }}
                            >
                                <PlayIcon size={8} /> RUN
                            </button>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

// ─── Automation Overlay ───

function AutomationOverlay({ session }: { session: SessionState }) {
    if (!session.overlayVisible) return null;

    return (
        <div className="session-overlay">
            {session.overlayMarkers.map(marker => (
                <div
                    key={marker.id}
                    className={`overlay-marker ${marker.status} ${marker.type}`}
                    style={{
                        left: `${marker.x}%`,
                        top: `${marker.y}%`,
                        width: `${marker.width}%`,
                        height: `${marker.height}%`,
                    }}
                    title={`${marker.label} — ${marker.status}\n${marker.selector || ''}`}
                >
                    <span className="overlay-marker-label">{marker.label}</span>
                    {marker.selector && (
                        <span className="overlay-marker-selector">{marker.selector}</span>
                    )}
                </div>
            ))}
        </div>
    );
}

// ─── Debug Rail ───

function DebugRail({ session }: { session: SessionState }) {
    const eventsEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        eventsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [session.events.length]);

    return (
        <div className="debug-rail">
            <div className="debug-rail-header">
                <span className="debug-rail-title">Debug Rail</span>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '8px', color: 'var(--ses-text-mute)' }}>
                    {session.events.length} events
                </span>
            </div>
            <div className="debug-rail-events">
                {session.events.map(event => (
                    <div key={event.id} className={`debug-event ${event.severity}`}>
                        <span className="debug-event-time">{event.timestamp}</span>
                        <span className="debug-event-msg">{event.message}</span>
                    </div>
                ))}
                <div ref={eventsEndRef} />
            </div>
        </div>
    );
}

// ─── Pipeline Bar ───

function PipelineBar({ session }: { session: SessionState }) {
    const currentIdx = PIPELINE_STAGES.findIndex(s => s.stage === session.pipeline.stage);

    return (
        <div className="pipeline-bar">
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: '7px', color: 'var(--ses-text-mute)', marginRight: '6px', textTransform: 'uppercase' as const, letterSpacing: '1px' }}>
                Pipeline:
            </span>
            {PIPELINE_STAGES.map((s, i) => {
                const isActive = s.stage === session.pipeline.stage;
                const isComplete = i < currentIdx || session.pipeline.stage === 'complete';
                return (
                    <span key={s.stage} style={{ display: 'flex', alignItems: 'center', gap: '2px' }}>
                        {i > 0 && (
                            <span className={`pipeline-connector ${isComplete ? 'complete' : isActive ? 'active' : ''}`} />
                        )}
                        <span className={`pipeline-stage ${isActive ? 'active' : ''} ${isComplete ? 'complete' : ''}`}>
                            {s.label}
                        </span>
                    </span>
                );
            })}
            {session.pipeline.stage !== 'idle' && (
                <span style={{ marginLeft: 'auto', fontFamily: 'var(--font-mono)', fontSize: '8px', color: 'var(--ses-led-green)' }}>
                    {session.pipeline.progress}%
                </span>
            )}
        </div>
    );
}

// ─── BAS Browser Viewport ───

function BASViewport({ session }: { session: SessionState }) {
    const isConnected = session.status === 'connected' && session.browserId;

    if (!isConnected) {
        return (
            <div className="session-mock-ui" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '12px' }}>
                <div className="session-launch-icon">
                    <AutomationIcon size={20} />
                </div>
                <div style={{ textAlign: 'center' }}>
                    <div className="session-launch-title">
                        {session.provider.charAt(0).toUpperCase() + session.provider.slice(1)} Session
                    </div>
                    <div className="session-launch-hint">
                        {session.status === 'connecting' ? 'Connecting to BAS...' :
                            session.status === 'error' ? 'Connection failed — check BAS (port 5002)' :
                                session.basConnected ? 'BAS online — ready to launch' : 'Launch browser to start session'}
                    </div>
                </div>
                {session.status === 'connecting' && (
                    <div style={{
                        width: '20px', height: '20px',
                        border: '2px solid #1e1e1e',
                        borderTopColor: 'var(--ses-led-green)',
                        borderRadius: '50%',
                        animation: 'spin 1s linear infinite',
                    }} />
                )}
            </div>
        );
    }

    // Connected — show screenshot or stream
    return (
        <div className="session-mock-ui" style={{ display: 'flex', flexDirection: 'column', width: '100%', height: '100%' }}>
            {session.lastScreenshot ? (
                <img
                    src={`data:image/png;base64,${session.lastScreenshot}`}
                    alt={`${session.provider} browser viewport`}
                    style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                />
            ) : (
                <div style={{
                    flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center',
                    color: 'var(--ses-text-mute)', fontFamily: 'var(--font-mono)', fontSize: '9px',
                }}>
                    Browser connected — click CAPTURE for screenshot
                </div>
            )}
            {session.lastResponse && (
                <div className="session-last-response">
                    <div className="session-last-response-label">Last Response:</div>
                    <div>
                        {session.lastResponse.slice(0, 300)}{session.lastResponse.length > 300 ? '...' : ''}
                    </div>
                </div>
            )}
        </div>
    );
}

// ─── Session Page (Main Export) ───

export function SessionPage({ sessionId }: { sessionId: string }) {
    const {
        sessions, toggleOverlay, attachFile, removeFile,
        launchSession, injectPrompt, extractResponse, captureScreenshot, refreshBASStatus,
    } = useSessionStore();
    const session = sessions[sessionId];
    const [promptText, setPromptText] = useState('');
    const [sending, setSending] = useState(false);
    const convoEndRef = useRef<HTMLDivElement>(null);

    // Auto-refresh BAS status every 10s when browser is active
    useEffect(() => {
        if (!session?.browserId) return;
        const interval = setInterval(() => {
            refreshBASStatus(sessionId);
            captureScreenshot(sessionId);
        }, 10000);
        return () => clearInterval(interval);
    }, [session?.browserId, sessionId, refreshBASStatus, captureScreenshot]);

    // Auto-scroll conversation to bottom
    useEffect(() => {
        convoEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [session?.conversation?.length]);

    if (!session) {
        return (
            <div className="joc-page-content" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <div style={{ color: 'var(--ses-text-mute)', fontFamily: 'var(--font-mono)', fontSize: '10px' }}>
                    Session "{sessionId}" not found
                </div>
            </div>
        );
    }

    const handleSend = async () => {
        if (!promptText.trim() || sending) return;
        setSending(true);
        const text = promptText;
        setPromptText('');
        try {
            await injectPrompt(sessionId, text);
        } finally {
            setSending(false);
        }
    };

    const handleAttachFile = () => {
        attachFile(sessionId, {
            id: `f-${Date.now()}`,
            name: 'context.txt',
            path: 'attached-file',
            size: 0,
            tokenEstimate: 0,
        });
    };

    return (
        <div className="session-layout">
            {/* ─── Viewport + Controls Column ─── */}
            <div className="session-viewport-wrapper">
                {/* URL bar */}
                <div className="session-viewport-header">
                    <span className={`session-provider-badge ${session.provider}`}>
                        {session.provider}
                    </span>
                    <div className="session-url-bar">
                        <span className="lock-icon"><LockIcon size={9} /></span>
                        <span>{session.url}</span>
                    </div>
                    {/* BAS Connection Badge */}
                    <span className={`session-bas-badge ${session.basConnected ? 'online' : 'offline'}`}>
                        <span className={`status-dot ${session.basConnected ? 'active' : 'error'}`} />
                        BAS {session.basConnected ? 'ONLINE' : 'OFFLINE'}
                    </span>
                    <span className="session-health-indicator">
                        <span className={`status-dot ${session.status === 'connected' ? 'active' : session.status === 'connecting' ? 'warning' : 'error'}`} />
                        {session.health}%
                    </span>
                </div>

                {/* Browser viewport with overlay */}
                <div className="session-viewport">
                    <div className="session-viewport-content">
                        <BASViewport session={session} />
                    </div>
                    <AutomationOverlay session={session} />
                </div>

                {/* Pipeline visualization */}
                <PipelineBar session={session} />

                {/* Conversation Thread */}
                {session.conversation.length > 0 && (
                    <div className="session-conversation">
                        {session.conversation.map(turn => (
                            <div key={turn.id} className={`session-turn ${turn.role}`}>
                                <div className="session-turn-header">
                                    <span className={`session-turn-role ${turn.role}`}>
                                        {turn.role === 'user' ? '▸ YOU' : '◂ AI'}
                                    </span>
                                    <span className="session-turn-time">{turn.timestamp}</span>
                                    <span className="session-turn-tokens">{turn.tokens} tok</span>
                                </div>
                                <div className="session-turn-content">
                                    {turn.content.slice(0, 500)}{turn.content.length > 500 ? '...' : ''}
                                </div>
                            </div>
                        ))}
                        <div ref={convoEndRef} />
                    </div>
                )}

                {/* Inline Prompt Bar */}
                <div className="session-prompt-bar">
                    <input
                        className="session-prompt-input"
                        type="text"
                        placeholder={session.browserId ? 'Type a follow-up prompt...' : 'Launch browser first...'}
                        value={promptText}
                        onChange={e => setPromptText(e.target.value)}
                        onKeyDown={e => {
                            if (e.key === 'Enter' && !e.shiftKey) {
                                e.preventDefault();
                                handleSend();
                            }
                        }}
                        disabled={!session.browserId || sending}
                    />
                    <button
                        className="control-btn primary"
                        onClick={handleSend}
                        disabled={!session.browserId || !promptText.trim() || sending}
                    >
                        {sending ? (
                            <span style={{ width: 10, height: 10, border: '1.5px solid var(--ses-led-amber)', borderTopColor: 'transparent', borderRadius: '50%', display: 'inline-block', animation: 'spin 0.6s linear infinite' }} />
                        ) : (
                            <SendIcon size={10} />
                        )} SEND
                    </button>
                </div>

                {/* Attached files */}
                {session.attachedFiles.length > 0 && (
                    <div className="attached-files">
                        {session.attachedFiles.map(f => (
                            <div key={f.id} className="attached-file">
                                <FileIcon size={10} />
                                <span>{f.name}</span>
                                <span style={{ color: 'var(--ses-text-mute)' }}>~{f.tokenEstimate} tok</span>
                                <button className="attached-file-remove" onClick={() => removeFile(sessionId, f.id)}>
                                    <CloseIcon size={8} />
                                </button>
                            </div>
                        ))}
                    </div>
                )}

                {/* Control bar */}
                <div className="session-controls">
                    {/* Launch / Connect */}
                    <button
                        className="control-btn primary"
                        onClick={() => launchSession(sessionId)}
                        disabled={session.status === 'connecting'}
                        title="Launch Puppeteer browser via BAS and navigate to provider"
                    >
                        <LaunchIcon size={11} /> {session.browserId ? 'RELAUNCH' : 'LAUNCH'}
                    </button>

                    <span className="control-divider" />

                    {/* Extract response */}
                    <button
                        className="control-btn"
                        onClick={() => extractResponse(sessionId)}
                        disabled={!session.browserId}
                        title="Extract the latest AI response from the browser"
                    >
                        <ExtractIcon /> EXTRACT
                    </button>

                    {/* Screenshot */}
                    <button
                        className="control-btn"
                        onClick={() => captureScreenshot(sessionId)}
                        disabled={!session.browserId}
                        title="Capture a screenshot of the current browser state"
                    >
                        <ScreenshotIcon /> CAPTURE
                    </button>

                    {/* File attachment */}
                    <button className="control-btn" onClick={handleAttachFile}>
                        <FileIcon /> + FILES
                    </button>

                    {/* Overlay toggle */}
                    <button className="control-btn" onClick={() => toggleOverlay(sessionId)}>
                        <EyeIcon /> {session.overlayVisible ? 'HIDE' : 'SHOW'} OVERLAY
                    </button>

                    {/* Refresh */}
                    <button
                        className="control-btn"
                        onClick={() => refreshBASStatus(sessionId)}
                        title="Refresh BAS connection status"
                    >
                        <RefreshIcon /> REFRESH
                    </button>

                    <div className="control-spacer" />

                    <div className="control-status">
                        <span className={`status-dot ${session.status === 'connected' ? 'active' : session.status === 'error' ? 'error' : 'warning'}`} />
                        {session.status.toUpperCase()}
                        {session.browserId && (
                            <>
                                <span>·</span>
                                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '7px' }}>
                                    {session.browserId.slice(0, 8)}
                                </span>
                            </>
                        )}
                    </div>
                </div>

            </div>

            {/* ─── Script Runner ─── */}
            <ScriptRunner session={session} />

            {/* ─── Debug Rail ─── */}
            <DebugRail session={session} />
        </div>
    );
}
