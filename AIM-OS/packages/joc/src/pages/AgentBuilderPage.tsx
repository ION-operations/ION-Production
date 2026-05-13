import React, { useState, useMemo, useCallback } from 'react';
import {
    useAgentGenomeStore,
    AgentGenome,
    AgentStatus,
    ChannelType,
    CloneDelta,
} from '../store/agentGenomeStore';
import { usePageOracle, OraclePageAction } from '../hooks/usePageOracle';
import '../styles/agent-builder.css';

// ══════════════════════════════════════════════════════════════
// Agent Builder Page — V3 Spec Implementation
// ══════════════════════════════════════════════════════════════

const AgentBuilderPage: React.FC = () => {
    const {
        agents,
        selectedAgentId,
        selectAgent,
        inspectorTab,
        setInspectorTab,
        cloneAgent,
        retireAgent,
        snapshotAgent,
        computeFissionScore,
        snapshots,
        handoffs,
        tournaments,
        fissionRecommendations,
        createDialogOpen,
        setCreateDialogOpen,
    } = useAgentGenomeStore();

    const [searchQuery, setSearchQuery] = useState('');
    const [cloneDialogOpen, setCloneDialogOpen] = useState(false);
    const [cloneName, setCloneName] = useState('');

    const selectedAgent = useMemo(
        () => agents.find(a => a.id === selectedAgentId) || null,
        [agents, selectedAgentId]
    );

    const filteredAgents = useMemo(() => {
        if (!searchQuery) return agents;
        const q = searchQuery.toLowerCase();
        return agents.filter(a =>
            a.displayName.toLowerCase().includes(q) ||
            a.behavioralDNA.domains.some(d => d.toLowerCase().includes(q))
        );
    }, [agents, searchQuery]);

    // ─── Oracle Integration ───

    const oracleActions: OraclePageAction[] = useMemo(() => [
        {
            id: 'agents.list',
            label: 'List All Agents',
            system: 'dispatch',
            description: 'List all registered agents in the genome registry',
            minPermission: 'supervised' as const,
            params: [],
            execute: async () => ({
                success: true,
                message: `${agents.length} agents registered`,
                data: { agents: agents.map(a => ({ id: a.id, name: a.displayName, status: a.status })) },
            }),
        },
        {
            id: 'agents.inspect',
            label: 'Inspect Agent',
            system: 'dispatch',
            description: 'Select and inspect a specific agent by ID',
            minPermission: 'supervised' as const,
            params: [{ name: 'agentId', type: 'string' as const, required: true, description: 'Agent ID to inspect' }],
            execute: async (params) => {
                const agent = agents.find(a => a.id === params?.agentId);
                if (!agent) return { success: false, message: 'Agent not found' };
                selectAgent(agent.id);
                return { success: true, message: `Inspecting ${agent.displayName}`, data: { agent: { id: agent.id, name: agent.displayName, status: agent.status, version: agent.version } } };
            },
        },
    ], [agents, selectAgent]);

    usePageOracle('agent-builder', {
        actions: oracleActions,
        getState: () => ({
            agentCount: agents.length,
            activeAgents: agents.filter(a => a.status === 'active').length,
            selectedAgent: selectedAgent?.displayName || null,
        }),
    });

    // ─── Clone Handler ───

    const handleClone = useCallback(() => {
        if (!selectedAgent || !cloneName.trim()) return;
        const newId = cloneName.toLowerCase().replace(/\s+/g, '-');
        const delta: CloneDelta = {
            name: cloneName,
        };
        cloneAgent(selectedAgent.id, newId, cloneName, delta);
        setCloneDialogOpen(false);
        setCloneName('');
        selectAgent(newId);
    }, [selectedAgent, cloneName, cloneAgent, selectAgent]);

    return (
        <div className="agent-builder">
            {/* ═══ LEFT: Registry ═══ */}
            <div className="agent-registry">
                <div className="agent-registry-header">
                    <h3>Agents ({agents.length})</h3>
                    <div className="agent-registry-actions">
                        <button
                            className="agent-registry-btn primary"
                            onClick={() => setCreateDialogOpen(true)}
                            title="Create new agent"
                        >
                            + New
                        </button>
                    </div>
                </div>

                <div className="agent-registry-search">
                    <input
                        type="text"
                        placeholder="Search agents or domains..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                    />
                </div>

                <div className="agent-registry-list">
                    {filteredAgents.map(agent => (
                        <div
                            key={agent.id}
                            className={`agent-card ${selectedAgentId === agent.id ? 'selected' : ''}`}
                            onClick={() => selectAgent(agent.id)}
                        >
                            <div className="agent-card-avatar">{agent.avatar}</div>
                            <div className="agent-card-info">
                                <div className="agent-card-name">{agent.displayName}</div>
                                <div className="agent-card-domain">
                                    {agent.behavioralDNA.domains.slice(0, 2).join(', ')}
                                </div>
                            </div>
                            <div className={`agent-card-status ${agent.status}`} />
                        </div>
                    ))}
                </div>
            </div>

            {/* ═══ CENTER: Inspector ═══ */}
            <div className="agent-inspector">
                {selectedAgent ? (
                    <>
                        <div className="agent-inspector-header">
                            <div className="agent-inspector-avatar">{selectedAgent.avatar}</div>
                            <div className="agent-inspector-title">
                                <h2>{selectedAgent.displayName}</h2>
                                <span className="version">v{selectedAgent.version}</span>
                            </div>
                            <div className="agent-inspector-meta">
                                <span className={`agent-inspector-badge ${selectedAgent.category}`}>
                                    {selectedAgent.category}
                                </span>
                                <button
                                    className="agent-registry-btn"
                                    onClick={() => setCloneDialogOpen(true)}
                                    title="Clone this agent"
                                >
                                    🧬 Clone
                                </button>
                                <button
                                    className="agent-registry-btn"
                                    onClick={() => snapshotAgent(selectedAgent.id)}
                                    title="Create snapshot"
                                >
                                    📸 Snapshot
                                </button>
                            </div>
                        </div>

                        <div className="agent-inspector-tabs">
                            {(['behavioral', 'knowledge', 'metrics', 'context', 'lineage'] as const).map(tab => (
                                <button
                                    key={tab}
                                    className={`agent-inspector-tab ${inspectorTab === tab ? 'active' : ''}`}
                                    onClick={() => setInspectorTab(tab)}
                                >
                                    {tab === 'behavioral' ? '🧠 Behavioral DNA' :
                                        tab === 'knowledge' ? '📚 Knowledge DNA' :
                                            tab === 'metrics' ? '📊 Metrics' :
                                                tab === 'context' ? '💾 Context Banks' :
                                                    '🌳 Lineage'}
                                </button>
                            ))}
                        </div>

                        <div className="agent-inspector-content">
                            {inspectorTab === 'behavioral' && (
                                <BehavioralDNAPanel agent={selectedAgent} />
                            )}
                            {inspectorTab === 'knowledge' && (
                                <KnowledgeDNAPanel agent={selectedAgent} />
                            )}
                            {inspectorTab === 'metrics' && (
                                <MetricsPanel agent={selectedAgent} computeFissionScore={computeFissionScore} />
                            )}
                            {inspectorTab === 'context' && (
                                <ContextBanksPanel agent={selectedAgent} />
                            )}
                            {inspectorTab === 'lineage' && (
                                <LineagePanel agent={selectedAgent} agents={agents} />
                            )}
                        </div>
                    </>
                ) : (
                    <div className="agent-inspector-empty">
                        <div className="agent-inspector-empty-icon">🧬</div>
                        <h3>Select an Agent</h3>
                        <p>Choose an agent from the registry to inspect its genome, or create a new one.</p>
                    </div>
                )}
            </div>

            {/* ═══ RIGHT: Lineage & Activity ═══ */}
            <div className="agent-lineage">
                <div className="agent-lineage-header">
                    <h3>Lineage Tree</h3>
                </div>
                <div className="agent-lineage-content">
                    <LineageTree agents={agents} selectedId={selectedAgentId} onSelect={selectAgent} />

                    {handoffs.length > 0 && (
                        <>
                            <div className="genome-section-title" style={{ marginTop: 24 }}>Recent Handoffs</div>
                            {handoffs.slice(-5).reverse().map(h => (
                                <div key={h.id} className="handoff-entry">
                                    <span className="handoff-agents">{h.fromAgent}</span>
                                    <span className="handoff-arrow">→</span>
                                    <span className="handoff-agents">{h.toAgent}</span>
                                    <span className="handoff-reason">{h.reason}</span>
                                </div>
                            ))}
                        </>
                    )}
                </div>
            </div>

            {/* ═══ Clone Dialog ═══ */}
            {cloneDialogOpen && selectedAgent && (
                <div style={{
                    position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000,
                }} onClick={() => setCloneDialogOpen(false)}>
                    <div style={{
                        background: '#161b22', border: '1px solid #30363d', borderRadius: 12,
                        padding: 24, width: 400, maxWidth: '90vw',
                    }} onClick={e => e.stopPropagation()}>
                        <h3 style={{ color: '#e6edf3', margin: '0 0 16px 0', fontSize: 16 }}>
                            🧬 Clone Agent: {selectedAgent.displayName}
                        </h3>
                        <p style={{ color: '#8b949e', fontSize: 13, margin: '0 0 16px 0' }}>
                            Creates a new agent inheriting {selectedAgent.displayName}'s behavioral DNA with isolated knowledge banks.
                        </p>

                        <div style={{ marginBottom: 16 }}>
                            <label style={{ display: 'block', color: '#c9d1d9', fontSize: 12, marginBottom: 4 }}>
                                Clone Name
                            </label>
                            <input
                                type="text"
                                value={cloneName}
                                onChange={e => setCloneName(e.target.value)}
                                placeholder={`${selectedAgent.displayName}-B`}
                                style={{
                                    width: '100%', background: '#0d1117', border: '1px solid #30363d',
                                    color: '#c9d1d9', padding: '8px 12px', borderRadius: 6, fontSize: 13,
                                    outline: 'none', boxSizing: 'border-box',
                                }}
                            />
                        </div>

                        <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
                            <button
                                className="agent-registry-btn"
                                onClick={() => setCloneDialogOpen(false)}
                            >
                                Cancel
                            </button>
                            <button
                                className="agent-registry-btn primary"
                                onClick={handleClone}
                                disabled={!cloneName.trim()}
                            >
                                Create Clone
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

// ══════════════════════════════════════════════════════════════
// Sub-Panels
// ══════════════════════════════════════════════════════════════

const BehavioralDNAPanel: React.FC<{ agent: AgentGenome }> = ({ agent }) => {
    const dna = agent.behavioralDNA;

    return (
        <>
            {/* Purpose & Personality */}
            <div className="genome-section">
                <div className="genome-section-title">Identity</div>
                <div className="genome-field">
                    <span className="genome-field-label">Purpose</span>
                    <span className="genome-field-value">{dna.purpose.join('; ')}</span>
                </div>
                <div className="genome-field">
                    <span className="genome-field-label">Personality</span>
                    <span className="genome-field-value">{dna.personality}</span>
                </div>
                <div className="genome-field">
                    <span className="genome-field-label">Autonomy</span>
                    <span className="genome-field-value" style={{
                        color: dna.policies.autonomy === 'auto' ? '#3fb950' :
                            dna.policies.autonomy === 'supervised' ? '#e3b341' :
                                dna.policies.autonomy === 'manual' ? '#f85149' : '#484f58'
                    }}>
                        {dna.policies.autonomy.toUpperCase()}
                    </span>
                </div>
            </div>

            {/* Domains */}
            <div className="genome-section">
                <div className="genome-section-title">Domains</div>
                <div className="genome-tags">
                    {dna.domains.map(d => (
                        <span key={d} className="genome-tag domain">{d}</span>
                    ))}
                </div>
            </div>

            {/* Skills */}
            <div className="genome-section">
                <div className="genome-section-title">Skills ({dna.skills.length})</div>
                {dna.skills.map(skill => (
                    <div key={skill.id} className="skill-bar">
                        <div className="skill-bar-header">
                            <span className="skill-bar-name">{skill.name}</span>
                            <span className="skill-bar-value">{(skill.proficiency * 100).toFixed(0)}%</span>
                        </div>
                        <div className="skill-bar-track">
                            <div
                                className={`skill-bar-fill ${skill.proficiency >= 0.8 ? 'high' :
                                    skill.proficiency >= 0.6 ? 'medium' : 'low'
                                    }`}
                                style={{ width: `${skill.proficiency * 100}%` }}
                            />
                        </div>
                    </div>
                ))}
            </div>

            {/* Tools */}
            <div className="genome-section">
                <div className="genome-section-title">Tools</div>
                <div className="genome-tags">
                    {dna.tools.map(t => (
                        <span key={t} className="genome-tag tool">{t}</span>
                    ))}
                </div>
            </div>

            {/* Activation Thresholds */}
            <div className="genome-section">
                <div className="genome-section-title">Activation Thresholds</div>
                <div className="genome-field">
                    <span className="genome-field-label">🎯 Ownership</span>
                    <span className="genome-field-value" style={{ color: '#3fb950' }}>
                        ≥ {dna.activationThresholds.ownership.toFixed(2)}
                    </span>
                </div>
                <div className="genome-field">
                    <span className="genome-field-label">🔄 Activation</span>
                    <span className="genome-field-value" style={{ color: '#58a6ff' }}>
                        ≥ {dna.activationThresholds.activation.toFixed(2)}
                    </span>
                </div>
                <div className="genome-field">
                    <span className="genome-field-label">⚠️ Consultation</span>
                    <span className="genome-field-value" style={{ color: '#e3b341' }}>
                        ≥ {dna.activationThresholds.consultation.toFixed(2)}
                    </span>
                </div>
            </div>

            {/* Policies */}
            <div className="genome-section">
                <div className="genome-section-title">Policies</div>
                <div className="genome-field">
                    <span className="genome-field-label">Max Cost/Action</span>
                    <span className="genome-field-value">${dna.policies.maxCostPerAction.toFixed(2)}</span>
                </div>
                <div className="genome-field">
                    <span className="genome-field-label">Forbidden Systems</span>
                    <span className="genome-field-value">
                        {dna.policies.forbiddenSystems.length > 0
                            ? dna.policies.forbiddenSystems.map(s => `🔒 ${s}`).join(', ')
                            : 'None'}
                    </span>
                </div>
                <div className="genome-field">
                    <span className="genome-field-label">Oracle Integration</span>
                    <span className="genome-field-value" style={{ color: dna.policies.oracleIntegration ? '#3fb950' : '#484f58' }}>
                        {dna.policies.oracleIntegration ? '✅ Enabled' : '❌ Disabled'}
                    </span>
                </div>
            </div>
        </>
    );
};

const KnowledgeDNAPanel: React.FC<{ agent: AgentGenome }> = ({ agent }) => {
    const knowledge = agent.knowledgeDNA;

    return (
        <>
            {/* Episodes */}
            <div className="genome-section">
                <div className="genome-section-title">Episode History</div>
                <div className="genome-field">
                    <span className="genome-field-label">Total Episodes</span>
                    <span className="genome-field-value">{knowledge.episodes.total}</span>
                </div>
                <div className="genome-field">
                    <span className="genome-field-label">Compression Ratio</span>
                    <span className="genome-field-value">{knowledge.episodes.compressionRatio}</span>
                </div>
                <div className="genome-field">
                    <span className="genome-field-label">Last Compressed</span>
                    <span className="genome-field-value">
                        {new Date(knowledge.episodes.lastCompressed).toLocaleDateString()}
                    </span>
                </div>
            </div>

            {/* Shared Knowledge */}
            <div className="genome-section">
                <div className="genome-section-title">Shared Knowledge (Read-Only)</div>
                {knowledge.sharedKnowledge.length > 0 ? (
                    knowledge.sharedKnowledge.map(ref => (
                        <div key={ref.id} className="genome-field">
                            <span className="genome-field-label">{ref.label}</span>
                            <span className="genome-field-value" style={{ color: '#a371f7' }}>
                                {ref.source.toUpperCase()} · {(ref.relevance * 100).toFixed(0)}%
                            </span>
                        </div>
                    ))
                ) : (
                    <div style={{ color: '#484f58', fontSize: 12, padding: '8px 0' }}>
                        No shared knowledge references yet
                    </div>
                )}
            </div>

            {/* Domains Used */}
            <div className="genome-section">
                <div className="genome-section-title">Domain Activity</div>
                {Object.entries(knowledge.episodes.domainsUsed).length > 0 ? (
                    Object.entries(knowledge.episodes.domainsUsed).map(([domain, count]) => (
                        <div key={domain} className="genome-field">
                            <span className="genome-field-label">{domain}</span>
                            <span className="genome-field-value">{count} episodes</span>
                        </div>
                    ))
                ) : (
                    <div style={{ color: '#484f58', fontSize: 12, padding: '8px 0' }}>
                        No episodes recorded yet
                    </div>
                )}
            </div>
        </>
    );
};

const MetricsPanel: React.FC<{
    agent: AgentGenome;
    computeFissionScore: (id: string) => number;
}> = ({ agent, computeFissionScore }) => {
    const fissionScore = computeFissionScore(agent.id);
    const metrics = agent.metrics;

    return (
        <>
            {/* Key Metrics Grid */}
            <div className="metrics-grid">
                <div className="metric-card">
                    <div className="metric-card-value" style={{
                        color: metrics.confidence >= 0.8 ? '#3fb950' :
                            metrics.confidence >= 0.6 ? '#e3b341' : '#f85149'
                    }}>
                        {(metrics.confidence * 100).toFixed(0)}%
                    </div>
                    <div className="metric-card-label">Confidence</div>
                </div>
                <div className="metric-card">
                    <div className="metric-card-value" style={{
                        color: metrics.qualityScore >= 0.8 ? '#3fb950' :
                            metrics.qualityScore >= 0.6 ? '#e3b341' : '#f85149'
                    }}>
                        {(metrics.qualityScore * 100).toFixed(0)}%
                    </div>
                    <div className="metric-card-label">Quality</div>
                </div>
                <div className="metric-card">
                    <div className="metric-card-value">{metrics.totalTasks}</div>
                    <div className="metric-card-label">Total Tasks</div>
                </div>
                <div className="metric-card">
                    <div className="metric-card-value">{metrics.totalEpisodes}</div>
                    <div className="metric-card-label">Episodes</div>
                </div>
            </div>

            {/* Fission Score */}
            <div className="genome-section" style={{ marginTop: 12 }}>
                <div className="genome-section-title">Fission Score</div>
                <div className="fission-gauge">
                    <div className="fission-gauge-bar">
                        <div
                            className={`fission-gauge-fill ${fissionScore < 0.45 ? 'safe' :
                                fissionScore < 0.65 ? 'warning' : 'danger'
                                }`}
                            style={{ width: `${fissionScore * 100}%` }}
                        />
                        <div className="fission-gauge-threshold" />
                    </div>
                    <div className={`fission-gauge-score ${fissionScore < 0.45 ? 'safe' :
                        fissionScore < 0.65 ? 'warning' : 'danger'
                        }`}>
                        {fissionScore.toFixed(2)}
                    </div>
                </div>
                <div style={{ fontSize: 11, color: '#8b949e', marginTop: 4 }}>
                    {fissionScore < 0.45 ? '✅ Agent is well-focused. No split needed.' :
                        fissionScore < 0.65 ? '⚠️ Agent breadth increasing. Monitor for split.' :
                            '🔴 Agent should split into specialists. Recommend fission.'}
                </div>
            </div>

            {/* Performance */}
            <div className="genome-section">
                <div className="genome-section-title">Performance</div>
                <div className="genome-field">
                    <span className="genome-field-label">Avg Cost / Action</span>
                    <span className="genome-field-value">${metrics.avgCost.toFixed(3)}</span>
                </div>
                <div className="genome-field">
                    <span className="genome-field-label">Avg Latency</span>
                    <span className="genome-field-value">{metrics.avgLatency.toFixed(1)}s</span>
                </div>
                <div className="genome-field">
                    <span className="genome-field-label">Success Rate</span>
                    <span className="genome-field-value">
                        {(metrics.taskSuccessRate * 100).toFixed(0)}%
                    </span>
                </div>
                <div className="genome-field">
                    <span className="genome-field-label">Last Evaluation</span>
                    <span className="genome-field-value">
                        {new Date(metrics.lastEvaluation).toLocaleDateString()}
                    </span>
                </div>
            </div>
        </>
    );
};

const ContextBanksPanel: React.FC<{ agent: AgentGenome }> = ({ agent }) => {
    return (
        <>
            <div className="genome-section">
                <div className="genome-section-title">Memory Channels</div>
                {agent.knowledgeDNA.channels.map(channel => {
                    const usage = channel.capacity > 0 ? channel.currentUsage / channel.capacity : 0;
                    return (
                        <div key={channel.type} className="channel-bar">
                            <div className="channel-bar-header">
                                <span className="channel-bar-type">
                                    {channel.type === 'short' ? '⚡ Short-term' :
                                        channel.type === 'scratch' ? '📝 Scratch' :
                                            channel.type === 'long' ? '🧠 Long-term' :
                                                '⚙️ Operations'}
                                </span>
                                <span className="channel-bar-usage">
                                    {(channel.currentUsage / 1000).toFixed(1)}K / {(channel.capacity / 1000).toFixed(0)}K tokens
                                </span>
                            </div>
                            <div className="channel-bar-track">
                                <div
                                    className={`channel-bar-fill ${usage < 0.6 ? 'healthy' :
                                        usage < 0.85 ? 'warning' : 'critical'
                                        }`}
                                    style={{ width: `${usage * 100}%` }}
                                />
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 2 }}>
                                <span style={{ fontSize: 10, color: '#484f58' }}>TTL: {channel.ttl}</span>
                                <span style={{ fontSize: 10, color: '#484f58' }}>{channel.itemCount} items</span>
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Total Context Health */}
            <div className="genome-section">
                <div className="genome-section-title">Context Health</div>
                {(() => {
                    const totalCapacity = agent.knowledgeDNA.channels.reduce((s, c) => s + c.capacity, 0);
                    const totalUsage = agent.knowledgeDNA.channels.reduce((s, c) => s + c.currentUsage, 0);
                    const healthPct = totalCapacity > 0 ? ((totalCapacity - totalUsage) / totalCapacity) * 100 : 100;
                    return (
                        <>
                            <div className="genome-field">
                                <span className="genome-field-label">Total Capacity</span>
                                <span className="genome-field-value">{(totalCapacity / 1000).toFixed(0)}K tokens</span>
                            </div>
                            <div className="genome-field">
                                <span className="genome-field-label">Used</span>
                                <span className="genome-field-value">{(totalUsage / 1000).toFixed(1)}K tokens</span>
                            </div>
                            <div className="genome-field">
                                <span className="genome-field-label">Health</span>
                                <span className="genome-field-value" style={{
                                    color: healthPct > 60 ? '#3fb950' : healthPct > 30 ? '#e3b341' : '#f85149'
                                }}>
                                    {healthPct.toFixed(0)}% available
                                </span>
                            </div>
                        </>
                    );
                })()}
            </div>
        </>
    );
};

const LineagePanel: React.FC<{ agent: AgentGenome; agents: AgentGenome[] }> = ({ agent, agents }) => {
    const parent = agent.parent ? agents.find(a => a.id === agent.parent) : null;
    const children = agents.filter(a => a.parent === agent.id);

    return (
        <>
            <div className="genome-section">
                <div className="genome-section-title">Lineage</div>
                <div className="genome-field">
                    <span className="genome-field-label">Agent ID</span>
                    <span className="genome-field-value">{agent.id}</span>
                </div>
                <div className="genome-field">
                    <span className="genome-field-label">Version</span>
                    <span className="genome-field-value">v{agent.version}</span>
                </div>
                <div className="genome-field">
                    <span className="genome-field-label">Parent</span>
                    <span className="genome-field-value" style={{ color: parent ? '#a371f7' : '#484f58' }}>
                        {parent ? `${parent.avatar} ${parent.displayName}` : 'None (root agent)'}
                    </span>
                </div>
                <div className="genome-field">
                    <span className="genome-field-label">Clones</span>
                    <span className="genome-field-value">{children.length}</span>
                </div>
                <div className="genome-field">
                    <span className="genome-field-label">Ancestry Depth</span>
                    <span className="genome-field-value">{agent.lineage.length}</span>
                </div>
            </div>

            {/* Children */}
            {children.length > 0 && (
                <div className="genome-section">
                    <div className="genome-section-title">Direct Clones ({children.length})</div>
                    {children.map(child => (
                        <div key={child.id} className="genome-field">
                            <span className="genome-field-label">{child.avatar} {child.displayName}</span>
                            <span className="genome-field-value" style={{
                                color: child.status === 'active' ? '#3fb950' :
                                    child.status === 'retired' ? '#484f58' : '#e3b341'
                            }}>
                                {child.status}
                            </span>
                        </div>
                    ))}
                </div>
            )}

            {/* Timestamps */}
            <div className="genome-section">
                <div className="genome-section-title">Temporal</div>
                <div className="genome-field">
                    <span className="genome-field-label">Created</span>
                    <span className="genome-field-value">
                        {new Date(agent.createdAt).toLocaleDateString()}
                    </span>
                </div>
                <div className="genome-field">
                    <span className="genome-field-label">Valid From</span>
                    <span className="genome-field-value">
                        {new Date(agent.validFrom).toLocaleDateString()}
                    </span>
                </div>
                {agent.validTo && (
                    <div className="genome-field">
                        <span className="genome-field-label">Valid To</span>
                        <span className="genome-field-value" style={{ color: '#f85149' }}>
                            {new Date(agent.validTo).toLocaleDateString()}
                        </span>
                    </div>
                )}
            </div>
        </>
    );
};

// ─── Lineage Tree Component ───

const LineageTree: React.FC<{
    agents: AgentGenome[];
    selectedId: string | null;
    onSelect: (id: string) => void;
}> = ({ agents, selectedId, onSelect }) => {
    // Build tree: root agents (no parent) and their descendants
    const roots = agents.filter(a => !a.parent);

    const renderNode = (agent: AgentGenome, depth: number = 0): React.ReactNode => {
        const children = agents.filter(a => a.parent === agent.id);
        const isSelected = selectedId === agent.id;

        return (
            <React.Fragment key={agent.id}>
                <div
                    className={`lineage-node ${isSelected ? 'current' : ''}`}
                    style={{ paddingLeft: 12 + depth * 24 }}
                    onClick={() => onSelect(agent.id)}
                >
                    <div className={`lineage-dot ${agent.parent ? 'clone' :
                        agent.status === 'retired' ? 'retired' : 'root'
                        }`} />
                    <span style={{ fontSize: 16 }}>{agent.avatar}</span>
                    <span style={{ fontSize: 12, color: isSelected ? '#58a6ff' : '#c9d1d9', flex: 1 }}>
                        {agent.displayName}
                    </span>
                    <span style={{ fontSize: 10, color: '#484f58' }}>v{agent.version}</span>
                </div>
                {depth < 3 && children.length > 0 && (
                    <div style={{ borderLeft: '2px solid #21262d', marginLeft: 24 + depth * 24 }}>
                        {children.map(child => renderNode(child, depth + 1))}
                    </div>
                )}
            </React.Fragment>
        );
    };

    return <>{roots.map(root => renderNode(root))}</>;
};

export default AgentBuilderPage;
