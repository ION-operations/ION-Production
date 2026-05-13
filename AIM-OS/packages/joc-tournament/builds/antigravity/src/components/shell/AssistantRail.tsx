import React from 'react';
import { useShellStore, type RailMode } from '../../store/shellStore';
import { MOCK_CHAT } from '../../data/mockData';

const RAIL_MODES: { id: RailMode; icon: string; label: string }[] = [
    { id: 'chat', icon: 'C', label: 'Chat' },
    { id: 'context', icon: 'X', label: 'Context' },
    { id: 'actions', icon: 'A', label: 'Actions' },
    { id: 'memory', icon: 'M', label: 'Memory' },
];

export function RightIconBar() {
    const { railMode, setRailMode, railExpanded, toggleRail } = useShellStore();

    return (
        <div className="right-icon-bar textured">
            {RAIL_MODES.map((mode) => (
                <button
                    key={mode.id}
                    className={`icon-bar-btn ${railMode === mode.id && railExpanded ? 'active' : ''}`}
                    title={mode.label}
                    onClick={() => {
                        if (railMode === mode.id && railExpanded) {
                            toggleRail();
                        } else {
                            setRailMode(mode.id);
                        }
                    }}
                >
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, fontWeight: 600 }}>{mode.icon}</span>
                </button>
            ))}
        </div>
    );
}


export function AssistantRail() {
    const { railExpanded, railMode } = useShellStore();

    return (
        <div className={`assistant-rail ${railExpanded ? '' : 'collapsed'}`}>
            {railExpanded && (
                <>
                    <div className="rail-header">
                        <span className="rail-mode-label">
                            {RAIL_MODES.find((m) => m.id === railMode)?.label}
                        </span>
                        <span className="truth-badge-mock" style={{ marginLeft: 'auto' }} />
                    </div>

                    <div className="rail-content">
                        {railMode === 'chat' && <ChatMode />}
                        {railMode === 'context' && <ContextMode />}
                        {railMode === 'actions' && <ActionsMode />}
                        {railMode === 'memory' && <MemoryMode />}
                    </div>

                    {railMode === 'chat' && (
                        <div className="rail-input-area">
                            <textarea
                                className="rail-input"
                                placeholder="Ask JARVIS..."
                                rows={2}
                            />
                        </div>
                    )}
                </>
            )}
        </div>
    );
}


function ChatMode() {
    return (
        <div>
            {MOCK_CHAT.map((msg, i) => (
                <div key={i} className="chat-msg">
                    <div className={`chat-msg-role ${msg.role}`}>
                        {msg.role === 'user' ? 'OPERATOR' : 'JARVIS'}
                    </div>
                    <div className="chat-msg-body">{msg.content}</div>
                    {msg.confidence !== undefined && (
                        <div className="chat-msg-confidence">
                            <span>VIF κ</span>
                            <span style={{ color: msg.confidence > 0.85 ? 'var(--led-green)' : 'var(--led-amber)' }}>
                                {msg.confidence.toFixed(2)}
                            </span>
                        </div>
                    )}
                </div>
            ))}
        </div>
    );
}

function ContextMode() {
    return (
        <div>
            <div style={{
                fontFamily: 'var(--font-mono)',
                fontSize: 9,
                fontWeight: 600,
                textTransform: 'uppercase' as const,
                letterSpacing: '0.12em',
                color: 'var(--text-label)',
                marginBottom: 12,
            }}>WORKSPACE CONTEXT</div>
            <div className="lcd-readout" style={{ marginBottom: 10 }}>
                <div className="lcd-readout-label">Active Workspace</div>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-bright)' }}>Mission Control</div>
            </div>
            <div className="lcd-readout" style={{ marginBottom: 10 }}>
                <div className="lcd-readout-label">Active Agents</div>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-bright)' }}>4 / 6</div>
            </div>
            <div className="lcd-readout" style={{ marginBottom: 10 }}>
                <div className="lcd-readout-label">Running Missions</div>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-bright)' }}>3</div>
            </div>
            <div className="lcd-readout" style={{ marginBottom: 10 }}>
                <div className="lcd-readout-label">Pending Approvals</div>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--led-amber)' }}>3</div>
            </div>
            <div className="lcd-readout">
                <div className="lcd-readout-label">System Health</div>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--led-green)' }}>11/14 NOMINAL</div>
            </div>
        </div>
    );
}

function ActionsMode() {
    return (
        <div>
            <div style={{
                fontFamily: 'var(--font-mono)',
                fontSize: 9,
                fontWeight: 600,
                textTransform: 'uppercase' as const,
                letterSpacing: '0.12em',
                color: 'var(--text-label)',
                marginBottom: 12,
            }}>PENDING ACTIONS</div>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--text-dim)', marginBottom: 16 }}>
                3 items require operator approval
            </div>
            {[
                { label: 'Deploy AI Engine v2.0', agent: 'Opus', risk: 'HIGH' },
                { label: 'Execute debate topology', agent: 'Severina', risk: 'MED' },
                { label: 'Batch index 47 atoms', agent: 'Codex', risk: 'LOW' },
            ].map((item, i) => (
                <div key={i} style={{
                    padding: '6px 8px',
                    borderRadius: 3,
                    border: '1px solid rgba(0,0,0,0.4)',
                    background: 'linear-gradient(180deg, #171717 0%, #131313 100%)',
                    boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.03), inset 0 -1px 2px rgba(0,0,0,0.3)',
                    marginBottom: 4,
                }}>
                    <div style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--text-bright)' }}>
                        {item.label}
                    </div>
                    <div style={{ fontFamily: 'var(--font-mono)', fontSize: 9, color: 'var(--text-dim)', marginTop: 2 }}>
                        {item.agent} · Risk: <span style={{
                            color: item.risk === 'HIGH' ? 'var(--led-red)' :
                                item.risk === 'MED' ? 'var(--led-amber)' : 'var(--led-green)',
                        }}>{item.risk}</span>
                    </div>
                </div>
            ))}
        </div>
    );
}

function MemoryMode() {
    return (
        <div>
            <div style={{
                fontFamily: 'var(--font-mono)',
                fontSize: 9,
                fontWeight: 600,
                textTransform: 'uppercase' as const,
                letterSpacing: '0.12em',
                color: 'var(--text-label)',
                marginBottom: 12,
            }}>MEMORY & EVIDENCE</div>
            <div className="lcd-readout" style={{ marginBottom: 10 }}>
                <div className="lcd-readout-label">CMC Atoms</div>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-bright)' }}>194</div>
            </div>
            <div className="lcd-readout" style={{ marginBottom: 10 }}>
                <div className="lcd-readout-label">HHNI Index Size</div>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-bright)' }}>1,247 nodes</div>
            </div>
            <div className="lcd-readout" style={{ marginBottom: 10 }}>
                <div className="lcd-readout-label">SEG Entities</div>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-bright)' }}>342</div>
            </div>
            <div className="lcd-readout">
                <div className="lcd-readout-label">VIF Witnesses</div>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-bright)' }}>89</div>
            </div>
        </div>
    );
}
