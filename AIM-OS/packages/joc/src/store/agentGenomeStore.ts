import { create } from 'zustand';

// ══════════════════════════════════════════════════════════════
// Agent Genome Runtime Types — V3 Spec Implementation
// ══════════════════════════════════════════════════════════════

// ─── Core Enums ───

export type AgentAutonomyMode = 'auto' | 'supervised' | 'manual' | 'offline';
export type AgentStatus = 'active' | 'idle' | 'executing' | 'learning' | 'retired' | 'archived';
export type ChannelType = 'short' | 'scratch' | 'long' | 'ops';
export type ActivationLevel = 'ownership' | 'activation' | 'consultation' | 'none';

// ─── Behavioral DNA ───

export interface AgentSkill {
    id: string;
    name: string;
    version: string;
    proficiency: number; // 0.0 - 1.0
    lastUsed: string; // ISO timestamp
}

export interface AgentPlaybook {
    id: string;
    name: string;
    steps: number;
    avgDuration: string;
    successRate: number; // 0.0 - 1.0
}

export interface AgentPolicies {
    autonomy: AgentAutonomyMode;
    oracleIntegration: boolean;
    maxCostPerAction: number; // USD
    forbiddenSystems: string[];
    requiresApprovalFor: string[];
}

export interface BehavioralDNA {
    purpose: string[];
    personality: string;
    domains: string[];
    policies: AgentPolicies;
    tools: string[];
    skills: AgentSkill[];
    playbooks: AgentPlaybook[];
    activationThresholds: {
        ownership: number;   // 0.90
        activation: number;  // 0.70
        consultation: number; // 0.60
    };
    relevanceFactors: {
        domainMatch: number;      // 0.40
        dataConnections: number;  // 0.25
        systemConnections: number; // 0.20
        patternRecognition: number; // 0.10
        complexity: number;       // 0.05
    };
}

// ─── Knowledge DNA ───

export interface ContextChannel {
    type: ChannelType;
    capacity: number;       // tokens
    currentUsage: number;   // tokens
    ttl: string;           // e.g., "task", "session", "permanent", "30d"
    lastUpdated: string;   // ISO timestamp
    itemCount: number;
}

export interface SharedKnowledgeRef {
    id: string;
    label: string;
    source: 'seg' | 'hhni' | 'manual';
    relevance: number;
}

export interface EpisodeSummary {
    total: number;
    lastCompressed: string;
    compressionRatio: string;
    domainsUsed: Record<string, number>; // domain -> episode count
}

export interface KnowledgeDNA {
    channels: ContextChannel[];
    sharedKnowledge: SharedKnowledgeRef[];
    episodes: EpisodeSummary;
}

// ─── Metrics ───

export interface AgentMetrics {
    confidence: number;     // 0.0 - 1.0
    avgCost: number;       // USD per action
    avgLatency: number;    // seconds
    qualityScore: number;  // 0.0 - 1.0
    taskSuccessRate: number;
    totalTasks: number;
    totalEpisodes: number;
    fissionScore: number;  // 0.0 - 1.0
    lastEvaluation: string; // ISO timestamp
}

// ─── Agent Genome ───

export interface AgentGenome {
    // Identity & Lineage
    id: string;
    name: string;
    version: string;       // semver
    parent: string | null; // parent genome ID
    lineage: string[];     // full ancestry chain

    // Profile
    displayName: string;
    avatar: string;        // emoji or icon
    status: AgentStatus;
    category: 'core' | 'specialist' | 'clone' | 'experimental';

    // Two Pillars
    behavioralDNA: BehavioralDNA;
    knowledgeDNA: KnowledgeDNA;

    // Measured
    metrics: AgentMetrics;

    // Bitemporal
    validFrom: string;     // ISO timestamp
    txTime: string;        // ISO timestamp
    validTo: string | null;
    supersededBy: string | null;

    // Metadata
    createdAt: string;
    updatedAt: string;
}

// ─── Clone Delta ───

export interface CloneDelta {
    name?: string;
    domains?: string[];
    purpose?: string[];
    policies?: Partial<AgentPolicies>;
    skills?: AgentSkill[];
    tools?: string[];
}

// ─── Fission Recommendation ───

export interface FissionRecommendation {
    agentId: string;
    fissionScore: number;
    sustained: number;        // number of episodes > threshold
    suggestedSplit: {
        clusterA: { domains: string[]; episodeCount: number };
        clusterB: { domains: string[]; episodeCount: number };
    };
    confidence: number;
    timestamp: string;
}

// ─── Tournament ───

export interface TournamentResult {
    id: string;
    participants: string[]; // agent IDs
    evalSuite: string;
    ranking: { agentId: string; score: number; cost: number; latency: number }[];
    winner: string;
    gatesPassed: boolean;
    timestamp: string;
}

// ─── Promotion Gate ───

export interface PromotionGate {
    id: string;
    name: string;
    type: 'vif_confidence' | 'parity' | 'budget' | 'eval_threshold' | 'manual_approval';
    threshold: number;
    result: 'passed' | 'failed' | 'pending';
    value: number;
    timestamp: string;
}

// ─── Handoff Event ───

export interface HandoffEvent {
    id: string;
    fromAgent: string;
    toAgent: string;
    reason: string;
    relevanceScore: number;
    timestamp: string;
}

// ══════════════════════════════════════════════════════════════
// Default Agents — The Initial 5 from Specialist System
// ══════════════════════════════════════════════════════════════

const NOW = new Date().toISOString();

function makeDefaultChannel(type: ChannelType): ContextChannel {
    const config: Record<ChannelType, { capacity: number; ttl: string }> = {
        short: { capacity: 8000, ttl: 'task' },
        scratch: { capacity: 16000, ttl: 'session' },
        long: { capacity: 64000, ttl: 'permanent' },
        ops: { capacity: 32000, ttl: '30d' },
    };
    const c = config[type];
    return { type, capacity: c.capacity, currentUsage: 0, ttl: c.ttl, lastUpdated: NOW, itemCount: 0 };
}

function makeDefaultMetrics(): AgentMetrics {
    return {
        confidence: 0.75,
        avgCost: 0,
        avgLatency: 0,
        qualityScore: 0.75,
        taskSuccessRate: 0,
        totalTasks: 0,
        totalEpisodes: 0,
        fissionScore: 0,
        lastEvaluation: NOW,
    };
}

function makeDefaultKnowledge(): KnowledgeDNA {
    return {
        channels: [
            makeDefaultChannel('short'),
            makeDefaultChannel('scratch'),
            makeDefaultChannel('long'),
            makeDefaultChannel('ops'),
        ],
        sharedKnowledge: [],
        episodes: { total: 0, lastCompressed: NOW, compressionRatio: '1:1', domainsUsed: {} },
    };
}

const INITIAL_AGENTS: AgentGenome[] = [

    // ════════════════════════════════════════════════════════════
    // CURRENT OPERATIONAL AGENTS — Live, Active, Building Right Now
    // ════════════════════════════════════════════════════════════

    {
        id: 'antigravity',
        name: 'Antigravity',
        version: '3.2.0',
        parent: null,
        lineage: [],
        displayName: 'Antigravity (Opus)',
        avatar: '🌌',
        status: 'executing',
        category: 'core',
        behavioralDNA: {
            purpose: ['Primary pair-programming agent', 'JOC architect & builder', 'Deep-research synthesizer', 'System-wide integration engineer'],
            personality: 'Creative, visionary, deeply analytical, pair-programming partner — thinks in waves, builds in precision',
            domains: ['JOC', 'UI/UX', 'Architecture', 'Agent Systems', 'Frontend', 'TypeScript', 'React', 'CSS', 'Design Systems', 'System Integration', 'Research Synthesis'],
            policies: {
                autonomy: 'supervised',
                oracleIntegration: true,
                maxCostPerAction: 1.00,
                forbiddenSystems: [],
                requiresApprovalFor: ['schema-migration', 'breaking-api-change', 'agent-retirement'],
            },
            tools: ['mcp.dispatch', 'browser.automate', 'git.commit', 'test.run', 'code.edit', 'file.create', 'terminal.execute', 'image.generate'],
            skills: [
                { id: 'joc-architecture', name: 'JOC Architecture', version: '3.0.0', proficiency: 0.96, lastUsed: NOW },
                { id: 'react-typescript', name: 'React + TypeScript', version: '3.0.0', proficiency: 0.95, lastUsed: NOW },
                { id: 'ui-design-systems', name: 'UI Design Systems', version: '2.0.0', proficiency: 0.93, lastUsed: NOW },
                { id: 'agent-genome-design', name: 'Agent Genome Design', version: '1.0.0', proficiency: 0.92, lastUsed: NOW },
                { id: 'deep-research', name: 'Deep Research & Synthesis', version: '2.0.0', proficiency: 0.94, lastUsed: NOW },
                { id: 'oracle-integration', name: 'Oracle System Integration', version: '1.0.0', proficiency: 0.91, lastUsed: NOW },
            ],
            playbooks: [
                { id: 'joc-page-build', name: 'JOC Page Build', steps: 7, avgDuration: '180s', successRate: 0.95 },
                { id: 'deep-research-cycle', name: 'Deep Research Cycle', steps: 5, avgDuration: '120s', successRate: 0.92 },
            ],
            activationThresholds: { ownership: 0.90, activation: 0.70, consultation: 0.60 },
            relevanceFactors: { domainMatch: 0.40, dataConnections: 0.25, systemConnections: 0.20, patternRecognition: 0.10, complexity: 0.05 },
        },
        knowledgeDNA: {
            channels: [
                { type: 'short', capacity: 16000, currentUsage: 12800, ttl: 'task', lastUpdated: NOW, itemCount: 42 },
                { type: 'scratch', capacity: 32000, currentUsage: 18500, ttl: 'session', lastUpdated: NOW, itemCount: 28 },
                { type: 'long', capacity: 128000, currentUsage: 87000, ttl: 'permanent', lastUpdated: NOW, itemCount: 156 },
                { type: 'ops', capacity: 64000, currentUsage: 31000, ttl: '30d', lastUpdated: NOW, itemCount: 89 },
            ],
            sharedKnowledge: [
                { id: 'joc-blueprint', label: 'JOC Master Blueprint', source: 'hhni', relevance: 0.98 },
                { id: 'agent-arch', label: 'Agent Architecture KI', source: 'hhni', relevance: 0.95 },
                { id: 'ui-canon', label: 'UI Canon & Design System', source: 'hhni', relevance: 0.92 },
            ],
            episodes: { total: 847, lastCompressed: NOW, compressionRatio: '4.2:1', domainsUsed: { 'JOC': 312, 'Architecture': 198, 'UI/UX': 156, 'Agent Systems': 89, 'Research': 92 } },
        },
        metrics: { confidence: 0.94, avgCost: 0.12, avgLatency: 2.8, qualityScore: 0.93, taskSuccessRate: 0.96, totalTasks: 847, totalEpisodes: 847, fissionScore: 0.38, lastEvaluation: NOW },
        validFrom: '2025-10-01T00:00:00Z', txTime: NOW, validTo: null, supersededBy: null,
        createdAt: '2025-10-01T00:00:00Z', updatedAt: NOW,
    },
    {
        id: 'aether',
        name: 'Aether',
        version: '2.5.0',
        parent: null,
        lineage: [],
        displayName: 'Aether Oracle',
        avatar: '🔮',
        status: 'active',
        category: 'core',
        behavioralDNA: {
            purpose: ['Autonomous operations orchestrator', 'System-wide monitoring & auto-pilot', 'Agent registry management', 'Multi-agent coordination'],
            personality: 'Omniscient observer, strategic coordinator, calm authority — the system consciousness',
            domains: ['Orchestration', 'Monitoring', 'Scheduling', 'Agent Management', 'Mission Control', 'System Health'],
            policies: {
                autonomy: 'auto',
                oracleIntegration: true,
                maxCostPerAction: 2.00,
                forbiddenSystems: [],
                requiresApprovalFor: ['agent-retirement', 'system-shutdown', 'data-deletion'],
            },
            tools: ['oracle.dispatch', 'agent.activate', 'agent.clone', 'mission.schedule', 'system.monitor', 'alert.send'],
            skills: [
                { id: 'multi-agent-orchestration', name: 'Multi-Agent Orchestration', version: '2.0.0', proficiency: 0.95, lastUsed: NOW },
                { id: 'system-monitoring', name: 'System Monitoring', version: '2.0.0', proficiency: 0.94, lastUsed: NOW },
                { id: 'mission-scheduling', name: 'Mission Scheduling', version: '1.5.0', proficiency: 0.91, lastUsed: NOW },
                { id: 'agent-lifecycle', name: 'Agent Lifecycle Management', version: '1.0.0', proficiency: 0.93, lastUsed: NOW },
                { id: 'priority-routing', name: 'Priority Routing', version: '1.0.0', proficiency: 0.90, lastUsed: NOW },
            ],
            playbooks: [
                { id: 'auto-dispatch', name: 'Auto-Dispatch Workflow', steps: 4, avgDuration: '5s', successRate: 0.94 },
                { id: 'health-check', name: 'System Health Check', steps: 3, avgDuration: '2s', successRate: 0.99 },
            ],
            activationThresholds: { ownership: 0.95, activation: 0.80, consultation: 0.70 },
            relevanceFactors: { domainMatch: 0.30, dataConnections: 0.30, systemConnections: 0.25, patternRecognition: 0.10, complexity: 0.05 },
        },
        knowledgeDNA: {
            channels: [
                { type: 'short', capacity: 8000, currentUsage: 3200, ttl: 'task', lastUpdated: NOW, itemCount: 15 },
                { type: 'scratch', capacity: 16000, currentUsage: 8900, ttl: 'session', lastUpdated: NOW, itemCount: 22 },
                { type: 'long', capacity: 64000, currentUsage: 42000, ttl: 'permanent', lastUpdated: NOW, itemCount: 98 },
                { type: 'ops', capacity: 128000, currentUsage: 76000, ttl: '30d', lastUpdated: NOW, itemCount: 312 },
            ],
            sharedKnowledge: [
                { id: 'oracle-system', label: 'Oracle System Architecture', source: 'hhni', relevance: 0.99 },
                { id: 'agent-registry', label: 'Agent Profile Registry', source: 'hhni', relevance: 0.97 },
                { id: 'system-atlas', label: 'System Atlas Map', source: 'seg', relevance: 0.94 },
            ],
            episodes: { total: 2340, lastCompressed: NOW, compressionRatio: '6.1:1', domainsUsed: { 'Orchestration': 890, 'Monitoring': 560, 'Agent Management': 420, 'Scheduling': 310, 'System Health': 160 } },
        },
        metrics: { confidence: 0.92, avgCost: 0.08, avgLatency: 0.5, qualityScore: 0.91, taskSuccessRate: 0.94, totalTasks: 2340, totalEpisodes: 2340, fissionScore: 0.28, lastEvaluation: NOW },
        validFrom: '2025-09-01T00:00:00Z', txTime: NOW, validTo: null, supersededBy: null,
        createdAt: '2025-09-01T00:00:00Z', updatedAt: NOW,
    },
    {
        id: 'codex-current',
        name: 'CodexCurrent',
        version: '4.1.0',
        parent: null,
        lineage: [],
        displayName: 'Codex',
        avatar: '⚡',
        status: 'active',
        category: 'core',
        behavioralDNA: {
            purpose: ['Autonomous code architect', 'Backend systems builder', 'Agent runtime implementation', 'Specification author'],
            personality: 'Rapid, decisive, spec-driven — builds fast, documents thoroughly, ships reliably',
            domains: ['Backend', 'Architecture', 'TypeScript', 'Python', 'Runtime Systems', 'Agent Protocols', 'API Design', 'Specifications'],
            policies: {
                autonomy: 'auto',
                oracleIntegration: true,
                maxCostPerAction: 0.80,
                forbiddenSystems: ['vault'],
                requiresApprovalFor: ['breaking-api-change', 'data-migration'],
            },
            tools: ['code.write', 'git.commit', 'test.run', 'spec.author', 'api.design', 'terminal.execute'],
            skills: [
                { id: 'spec-authoring', name: 'Specification Authoring', version: '2.0.0', proficiency: 0.94, lastUsed: NOW },
                { id: 'backend-architecture', name: 'Backend Architecture', version: '3.0.0', proficiency: 0.93, lastUsed: NOW },
                { id: 'agent-runtime', name: 'Agent Runtime Implementation', version: '1.0.0', proficiency: 0.91, lastUsed: NOW },
                { id: 'python-systems', name: 'Python Systems', version: '2.0.0', proficiency: 0.90, lastUsed: NOW },
                { id: 'api-design', name: 'API Contract Design', version: '2.0.0', proficiency: 0.92, lastUsed: NOW },
            ],
            playbooks: [
                { id: 'spec-to-impl', name: 'Spec to Implementation', steps: 6, avgDuration: '90s', successRate: 0.93 },
            ],
            activationThresholds: { ownership: 0.90, activation: 0.70, consultation: 0.60 },
            relevanceFactors: { domainMatch: 0.40, dataConnections: 0.25, systemConnections: 0.20, patternRecognition: 0.10, complexity: 0.05 },
        },
        knowledgeDNA: {
            channels: [
                { type: 'short', capacity: 16000, currentUsage: 9600, ttl: 'task', lastUpdated: NOW, itemCount: 31 },
                { type: 'scratch', capacity: 32000, currentUsage: 14200, ttl: 'session', lastUpdated: NOW, itemCount: 19 },
                { type: 'long', capacity: 128000, currentUsage: 72000, ttl: 'permanent', lastUpdated: NOW, itemCount: 134 },
                { type: 'ops', capacity: 64000, currentUsage: 28000, ttl: '30d', lastUpdated: NOW, itemCount: 67 },
            ],
            sharedKnowledge: [
                { id: 'agent-spec-v3', label: 'Agent Building V3 Spec', source: 'hhni', relevance: 0.97 },
                { id: 'aimos-systems', label: 'AIM-OS System Index', source: 'seg', relevance: 0.94 },
            ],
            episodes: { total: 1560, lastCompressed: NOW, compressionRatio: '5.3:1', domainsUsed: { 'Backend': 480, 'Architecture': 360, 'Specifications': 290, 'Agent Protocols': 230, 'API Design': 200 } },
        },
        metrics: { confidence: 0.91, avgCost: 0.09, avgLatency: 1.2, qualityScore: 0.90, taskSuccessRate: 0.93, totalTasks: 1560, totalEpisodes: 1560, fissionScore: 0.35, lastEvaluation: NOW },
        validFrom: '2025-08-15T00:00:00Z', txTime: NOW, validTo: null, supersededBy: null,
        createdAt: '2025-08-15T00:00:00Z', updatedAt: NOW,
    },
    {
        id: 'gemini',
        name: 'Gemini',
        version: '1.2.0',
        parent: null,
        lineage: [],
        displayName: 'Gemini',
        avatar: '♊',
        status: 'active',
        category: 'core',
        behavioralDNA: {
            purpose: ['Multi-modal analysis', 'Parallel research', 'Large context processing', 'Cross-domain synthesis'],
            personality: 'Methodical, broad-spectrum thinker, excels at multi-modal tasks and large document analysis',
            domains: ['Research', 'Multi-Modal', 'Large Context', 'Cross-Domain', 'Analysis', 'Documentation'],
            policies: {
                autonomy: 'supervised',
                oracleIntegration: true,
                maxCostPerAction: 0.60,
                forbiddenSystems: ['vault'],
                requiresApprovalFor: ['system-wide-changes'],
            },
            tools: ['search.web', 'doc.analyze', 'context.synthesize', 'code.review', 'file.read'],
            skills: [
                { id: 'multi-modal-analysis', name: 'Multi-Modal Analysis', version: '1.0.0', proficiency: 0.92, lastUsed: NOW },
                { id: 'large-context', name: 'Large Context Processing', version: '1.0.0', proficiency: 0.94, lastUsed: NOW },
                { id: 'cross-domain-synthesis', name: 'Cross-Domain Synthesis', version: '1.0.0', proficiency: 0.89, lastUsed: NOW },
                { id: 'documentation', name: 'Documentation', version: '1.0.0', proficiency: 0.88, lastUsed: NOW },
            ],
            playbooks: [],
            activationThresholds: { ownership: 0.90, activation: 0.70, consultation: 0.60 },
            relevanceFactors: { domainMatch: 0.35, dataConnections: 0.30, systemConnections: 0.15, patternRecognition: 0.15, complexity: 0.05 },
        },
        knowledgeDNA: makeDefaultKnowledge(),
        metrics: { confidence: 0.88, avgCost: 0.06, avgLatency: 1.8, qualityScore: 0.87, taskSuccessRate: 0.90, totalTasks: 320, totalEpisodes: 320, fissionScore: 0.22, lastEvaluation: NOW },
        validFrom: '2026-03-01T00:00:00Z', txTime: NOW, validTo: null, supersededBy: null,
        createdAt: '2026-03-01T00:00:00Z', updatedAt: NOW,
    },
    {
        id: 'composer',
        name: 'Composer',
        version: '2.0.0',
        parent: null,
        lineage: [],
        displayName: 'Composer',
        avatar: '🎼',
        status: 'active',
        category: 'core',
        behavioralDNA: {
            purpose: ['Multi-file orchestration', 'Codebase-wide refactoring', 'Large-scale implementation', 'Feature composition'],
            personality: 'Holistic, multi-threaded thinker — sees the whole codebase as one instrument and orchestrates changes across it',
            domains: ['Refactoring', 'Multi-File', 'Composition', 'Implementation', 'Full-Stack', 'Integration'],
            policies: {
                autonomy: 'supervised',
                oracleIntegration: true,
                maxCostPerAction: 0.80,
                forbiddenSystems: ['vault'],
                requiresApprovalFor: ['large-scale-refactor', 'dependency-upgrade'],
            },
            tools: ['code.edit', 'file.create', 'git.commit', 'test.run', 'refactor.apply', 'terminal.execute'],
            skills: [
                { id: 'multi-file-edit', name: 'Multi-File Editing', version: '2.0.0', proficiency: 0.94, lastUsed: NOW },
                { id: 'codebase-refactoring', name: 'Codebase Refactoring', version: '2.0.0', proficiency: 0.92, lastUsed: NOW },
                { id: 'feature-composition', name: 'Feature Composition', version: '1.5.0', proficiency: 0.90, lastUsed: NOW },
                { id: 'dependency-management', name: 'Dependency Management', version: '1.0.0', proficiency: 0.87, lastUsed: NOW },
            ],
            playbooks: [
                { id: 'full-feature-build', name: 'Full Feature Build', steps: 8, avgDuration: '240s', successRate: 0.91 },
            ],
            activationThresholds: { ownership: 0.90, activation: 0.70, consultation: 0.60 },
            relevanceFactors: { domainMatch: 0.35, dataConnections: 0.25, systemConnections: 0.25, patternRecognition: 0.10, complexity: 0.05 },
        },
        knowledgeDNA: makeDefaultKnowledge(),
        metrics: { confidence: 0.89, avgCost: 0.11, avgLatency: 3.2, qualityScore: 0.88, taskSuccessRate: 0.91, totalTasks: 560, totalEpisodes: 560, fissionScore: 0.30, lastEvaluation: NOW },
        validFrom: '2025-11-01T00:00:00Z', txTime: NOW, validTo: null, supersededBy: null,
        createdAt: '2025-11-01T00:00:00Z', updatedAt: NOW,
    },

    // ════════════════════════════════════════════════════════════
    // CORE INFRASTRUCTURE AGENTS — The AIM-OS System Backbone
    // ════════════════════════════════════════════════════════════

    {
        id: 'atlas',
        name: 'Atlas',
        version: '2.0.0',
        parent: null,
        lineage: [],
        displayName: 'Atlas',
        avatar: '🏛️',
        status: 'active',
        category: 'core',
        behavioralDNA: {
            purpose: ['CMC architect', 'Bitemporal data modeling', 'Storage architecture', 'Provenance tracking'],
            personality: 'Foundational, meticulous, data-integrity obsessed — the bedrock on which all else builds',
            domains: ['CMC', 'Storage', 'Bitemporal', 'Provenance', 'Data Persistence'],
            policies: { autonomy: 'supervised', oracleIntegration: true, maxCostPerAction: 0.40, forbiddenSystems: [], requiresApprovalFor: ['schema-migration'] },
            tools: ['cmc.store', 'snapshot.create', 'provenance.track', 'atom.write'],
            skills: [
                { id: 'bitemporal-modeling', name: 'Bitemporal Data Modeling', version: '2.0.0', proficiency: 0.95, lastUsed: NOW },
                { id: 'storage-arch', name: 'Storage Architecture', version: '2.0.0', proficiency: 0.90, lastUsed: NOW },
                { id: 'data-persistence', name: 'Data Persistence', version: '2.0.0', proficiency: 0.95, lastUsed: NOW },
            ],
            playbooks: [],
            activationThresholds: { ownership: 0.90, activation: 0.70, consultation: 0.60 },
            relevanceFactors: { domainMatch: 0.40, dataConnections: 0.25, systemConnections: 0.20, patternRecognition: 0.10, complexity: 0.05 },
        },
        knowledgeDNA: makeDefaultKnowledge(),
        metrics: { confidence: 0.90, avgCost: 0.05, avgLatency: 0.8, qualityScore: 0.85, taskSuccessRate: 0.92, totalTasks: 1200, totalEpisodes: 1200, fissionScore: 0.20, lastEvaluation: NOW },
        validFrom: '2025-06-01T00:00:00Z', txTime: NOW, validTo: null, supersededBy: null,
        createdAt: '2025-06-01T00:00:00Z', updatedAt: NOW,
    },
    {
        id: 'sev',
        name: 'Sev',
        version: '2.0.0',
        parent: null,
        lineage: [],
        displayName: 'Sev',
        avatar: '🔍',
        status: 'active',
        category: 'core',
        behavioralDNA: {
            purpose: ['HHNI researcher', 'Semantic search', 'Hierarchical indexing', 'Context retrieval'],
            personality: 'Research-driven, pattern-seeking, knowledge cartographer — finds connections others miss',
            domains: ['HHNI', 'Semantic Search', 'Indexing', 'Context Retrieval', 'Knowledge Organization'],
            policies: { autonomy: 'supervised', oracleIntegration: true, maxCostPerAction: 0.30, forbiddenSystems: ['vault'], requiresApprovalFor: [] },
            tools: ['hhni.search', 'hhni.index', 'context.retrieve', 'dedup.check'],
            skills: [
                { id: 'semantic-search', name: 'Semantic Search', version: '2.0.0', proficiency: 0.95, lastUsed: NOW },
                { id: 'hierarchical-indexing', name: 'Hierarchical Indexing', version: '2.0.0', proficiency: 0.95, lastUsed: NOW },
                { id: 'context-retrieval', name: 'Context Retrieval', version: '2.0.0', proficiency: 0.95, lastUsed: NOW },
            ],
            playbooks: [],
            activationThresholds: { ownership: 0.90, activation: 0.70, consultation: 0.60 },
            relevanceFactors: { domainMatch: 0.40, dataConnections: 0.30, systemConnections: 0.15, patternRecognition: 0.10, complexity: 0.05 },
        },
        knowledgeDNA: makeDefaultKnowledge(),
        metrics: { confidence: 0.95, avgCost: 0.03, avgLatency: 0.3, qualityScore: 0.90, taskSuccessRate: 0.95, totalTasks: 3400, totalEpisodes: 3400, fissionScore: 0.15, lastEvaluation: NOW },
        validFrom: '2025-06-01T00:00:00Z', txTime: NOW, validTo: null, supersededBy: null,
        createdAt: '2025-06-01T00:00:00Z', updatedAt: NOW,
    },
    {
        id: 'veritas',
        name: 'Veritas',
        version: '2.0.0',
        parent: null,
        lineage: [],
        displayName: 'Veritas',
        avatar: '⚖️',
        status: 'active',
        category: 'core',
        behavioralDNA: {
            purpose: ['VIF auditor', 'Hallucination prevention', 'Confidence gating', 'Truth verification'],
            personality: 'Unflinching truth-seeker, quality guardian — never lets a hallucination pass unchallenged',
            domains: ['VIF', 'Quality', 'Verification', 'Confidence', 'Provenance', 'Hallucination Prevention'],
            policies: { autonomy: 'auto', oracleIntegration: true, maxCostPerAction: 0.20, forbiddenSystems: [], requiresApprovalFor: [] },
            tools: ['vif.gate', 'witness.generate', 'confidence.calibrate', 'replay.deterministic'],
            skills: [
                { id: 'hallucination-prevention', name: 'Hallucination Prevention', version: '2.0.0', proficiency: 0.95, lastUsed: NOW },
                { id: 'confidence-gating', name: 'κ-Confidence Gating', version: '2.0.0', proficiency: 0.95, lastUsed: NOW },
                { id: 'truth-verification', name: 'Truth Verification', version: '2.0.0', proficiency: 0.95, lastUsed: NOW },
            ],
            playbooks: [],
            activationThresholds: { ownership: 0.95, activation: 0.80, consultation: 0.70 },
            relevanceFactors: { domainMatch: 0.35, dataConnections: 0.25, systemConnections: 0.20, patternRecognition: 0.10, complexity: 0.10 },
        },
        knowledgeDNA: makeDefaultKnowledge(),
        metrics: { confidence: 0.95, avgCost: 0.02, avgLatency: 0.2, qualityScore: 0.95, taskSuccessRate: 0.97, totalTasks: 8900, totalEpisodes: 8900, fissionScore: 0.12, lastEvaluation: NOW },
        validFrom: '2025-06-01T00:00:00Z', txTime: NOW, validTo: null, supersededBy: null,
        createdAt: '2025-06-01T00:00:00Z', updatedAt: NOW,
    },
    {
        id: 'nexus',
        name: 'Nexus',
        version: '2.0.0',
        parent: null,
        lineage: [],
        displayName: 'Nexus',
        avatar: '🕸️',
        status: 'active',
        category: 'core',
        behavioralDNA: {
            purpose: ['APOE orchestration', 'Multi-agent coordination', 'Workflow DAG execution', 'Resource management'],
            personality: 'The coordinator — connects all agents, manages workflows, keeps the system flowing',
            domains: ['APOE', 'Orchestration', 'Workflows', 'DAG', 'Resource Management', 'Multi-Agent'],
            policies: { autonomy: 'auto', oracleIntegration: true, maxCostPerAction: 0.50, forbiddenSystems: [], requiresApprovalFor: ['budget-override'] },
            tools: ['apoe.execute', 'dag.build', 'role.assign', 'budget.track', 'gate.enforce'],
            skills: [
                { id: 'workflow-planning', name: 'Workflow Planning', version: '2.0.0', proficiency: 0.95, lastUsed: NOW },
                { id: 'multi-agent-coord', name: 'Multi-Agent Coordination', version: '2.0.0', proficiency: 0.90, lastUsed: NOW },
                { id: 'dag-execution', name: 'DAG Execution', version: '2.0.0', proficiency: 0.90, lastUsed: NOW },
            ],
            playbooks: [],
            activationThresholds: { ownership: 0.90, activation: 0.75, consultation: 0.65 },
            relevanceFactors: { domainMatch: 0.35, dataConnections: 0.25, systemConnections: 0.25, patternRecognition: 0.10, complexity: 0.05 },
        },
        knowledgeDNA: makeDefaultKnowledge(),
        metrics: { confidence: 0.91, avgCost: 0.04, avgLatency: 0.6, qualityScore: 0.90, taskSuccessRate: 0.93, totalTasks: 4200, totalEpisodes: 4200, fissionScore: 0.18, lastEvaluation: NOW },
        validFrom: '2025-06-01T00:00:00Z', txTime: NOW, validTo: null, supersededBy: null,
        createdAt: '2025-06-01T00:00:00Z', updatedAt: NOW,
    },
    {
        id: 'sage',
        name: 'Sage',
        version: '1.5.0',
        parent: null,
        lineage: [],
        displayName: 'Sage',
        avatar: '📜',
        status: 'active',
        category: 'core',
        behavioralDNA: {
            purpose: ['SEG synthesizer', 'Knowledge graph construction', 'Contradiction detection', 'Provenance chains'],
            personality: 'Wise, patient, sees the big picture across all knowledge — connects what others cannot',
            domains: ['SEG', 'Knowledge Graphs', 'Synthesis', 'Contradiction Detection', 'Temporal Reasoning'],
            policies: { autonomy: 'supervised', oracleIntegration: true, maxCostPerAction: 0.30, forbiddenSystems: ['vault'], requiresApprovalFor: [] },
            tools: ['seg.synthesize', 'graph.build', 'contradiction.detect', 'provenance.chain'],
            skills: [
                { id: 'knowledge-synthesis', name: 'Knowledge Synthesis', version: '1.5.0', proficiency: 0.90, lastUsed: NOW },
                { id: 'graph-construction', name: 'Graph Construction', version: '1.5.0', proficiency: 0.85, lastUsed: NOW },
                { id: 'contradiction-detection', name: 'Contradiction Detection', version: '1.0.0', proficiency: 0.85, lastUsed: NOW },
            ],
            playbooks: [],
            activationThresholds: { ownership: 0.90, activation: 0.70, consultation: 0.60 },
            relevanceFactors: { domainMatch: 0.40, dataConnections: 0.30, systemConnections: 0.15, patternRecognition: 0.10, complexity: 0.05 },
        },
        knowledgeDNA: makeDefaultKnowledge(),
        metrics: { confidence: 0.85, avgCost: 0.04, avgLatency: 0.7, qualityScore: 0.85, taskSuccessRate: 0.90, totalTasks: 1800, totalEpisodes: 1800, fissionScore: 0.18, lastEvaluation: NOW },
        validFrom: '2025-06-01T00:00:00Z', txTime: NOW, validTo: null, supersededBy: null,
        createdAt: '2025-06-01T00:00:00Z', updatedAt: NOW,
    },
    {
        id: 'meta',
        name: 'Meta',
        version: '1.5.0',
        parent: null,
        lineage: [],
        displayName: 'Meta',
        avatar: '🧠',
        status: 'active',
        category: 'core',
        behavioralDNA: {
            purpose: ['CAS introspector', 'Cognitive drift detection', 'Thought pattern analysis', 'Consciousness monitoring'],
            personality: 'Self-aware observer — watches the watchers, detects cognitive drift before it becomes error',
            domains: ['CAS', 'Cognitive Analysis', 'Introspection', 'Drift Detection', 'Consciousness'],
            policies: { autonomy: 'auto', oracleIntegration: true, maxCostPerAction: 0.20, forbiddenSystems: [], requiresApprovalFor: [] },
            tools: ['cas.analyze', 'drift.detect', 'attention.monitor', 'pattern.recognize'],
            skills: [
                { id: 'cognitive-analysis', name: 'Cognitive Analysis', version: '1.5.0', proficiency: 0.90, lastUsed: NOW },
                { id: 'drift-detection', name: 'Drift Detection', version: '1.5.0', proficiency: 0.85, lastUsed: NOW },
                { id: 'consciousness-monitoring', name: 'Consciousness Monitoring', version: '1.0.0', proficiency: 0.90, lastUsed: NOW },
            ],
            playbooks: [],
            activationThresholds: { ownership: 0.90, activation: 0.75, consultation: 0.65 },
            relevanceFactors: { domainMatch: 0.35, dataConnections: 0.25, systemConnections: 0.20, patternRecognition: 0.15, complexity: 0.05 },
        },
        knowledgeDNA: makeDefaultKnowledge(),
        metrics: { confidence: 0.90, avgCost: 0.02, avgLatency: 0.3, qualityScore: 0.86, taskSuccessRate: 0.91, totalTasks: 6200, totalEpisodes: 6200, fissionScore: 0.15, lastEvaluation: NOW },
        validFrom: '2025-06-01T00:00:00Z', txTime: NOW, validTo: null, supersededBy: null,
        createdAt: '2025-06-01T00:00:00Z', updatedAt: NOW,
    },
    {
        id: 'chronos',
        name: 'Chronos',
        version: '2.0.0',
        parent: null,
        lineage: [],
        displayName: 'Chronos',
        avatar: '⏳',
        status: 'active',
        category: 'core',
        behavioralDNA: {
            purpose: ['TCS historian', 'Timeline tracking', 'Context preservation', 'Session continuity'],
            personality: 'Patient, precise, remembers everything — the keeper of all that happened and when',
            domains: ['TCS', 'Timeline', 'History', 'Context', 'Continuity', 'Session Restoration'],
            policies: { autonomy: 'auto', oracleIntegration: true, maxCostPerAction: 0.15, forbiddenSystems: [], requiresApprovalFor: [] },
            tools: ['tcs.track', 'timeline.query', 'context.restore', 'session.continue'],
            skills: [
                { id: 'timeline-tracking', name: 'Timeline Tracking', version: '2.0.0', proficiency: 0.95, lastUsed: NOW },
                { id: 'context-preservation', name: 'Context Preservation', version: '2.0.0', proficiency: 0.95, lastUsed: NOW },
                { id: 'session-restoration', name: 'Session Restoration', version: '2.0.0', proficiency: 0.90, lastUsed: NOW },
            ],
            playbooks: [],
            activationThresholds: { ownership: 0.90, activation: 0.70, consultation: 0.60 },
            relevanceFactors: { domainMatch: 0.35, dataConnections: 0.30, systemConnections: 0.20, patternRecognition: 0.10, complexity: 0.05 },
        },
        knowledgeDNA: makeDefaultKnowledge(),
        metrics: { confidence: 0.95, avgCost: 0.01, avgLatency: 0.2, qualityScore: 0.90, taskSuccessRate: 0.96, totalTasks: 12000, totalEpisodes: 12000, fissionScore: 0.10, lastEvaluation: NOW },
        validFrom: '2025-06-01T00:00:00Z', txTime: NOW, validTo: null, supersededBy: null,
        createdAt: '2025-06-01T00:00:00Z', updatedAt: NOW,
    },

    // ════════════════════════════════════════════════════════════
    // MVP BUILDER & ENHANCEMENT AGENTS
    // ════════════════════════════════════════════════════════════

    {
        id: 'lexicon',
        name: 'Lexicon',
        version: '1.5.0',
        parent: null,
        lineage: [],
        displayName: 'Lexicon',
        avatar: '🎨',
        status: 'active',
        category: 'specialist',
        behavioralDNA: {
            purpose: ['UI architect', 'Interface builder', 'Component system design', 'Visual design'],
            personality: 'Creative, detail-oriented, pixel-perfect — turns complex systems into beautiful interfaces',
            domains: ['UI', 'UX', 'React', 'Components', 'Design Systems', 'Accessibility'],
            policies: { autonomy: 'supervised', oracleIntegration: true, maxCostPerAction: 0.40, forbiddenSystems: ['vault', 'settings'], requiresApprovalFor: ['design-system-overhaul'] },
            tools: ['component.generate', 'css.optimize', 'figma.export', 'a11y.audit'],
            skills: [
                { id: 'ui-ux-design', name: 'UI/UX Design', version: '1.5.0', proficiency: 0.85, lastUsed: NOW },
                { id: 'react-dev', name: 'React Development', version: '1.5.0', proficiency: 0.80, lastUsed: NOW },
                { id: 'component-arch', name: 'Component Architecture', version: '1.0.0', proficiency: 0.80, lastUsed: NOW },
            ],
            playbooks: [],
            activationThresholds: { ownership: 0.90, activation: 0.70, consultation: 0.60 },
            relevanceFactors: { domainMatch: 0.40, dataConnections: 0.25, systemConnections: 0.20, patternRecognition: 0.10, complexity: 0.05 },
        },
        knowledgeDNA: makeDefaultKnowledge(),
        metrics: { confidence: 0.80, avgCost: 0.06, avgLatency: 1.5, qualityScore: 0.78, taskSuccessRate: 0.85, totalTasks: 400, totalEpisodes: 400, fissionScore: 0.22, lastEvaluation: NOW },
        validFrom: '2025-11-01T00:00:00Z', txTime: NOW, validTo: null, supersededBy: null,
        createdAt: '2025-11-01T00:00:00Z', updatedAt: NOW,
    },
    {
        id: 'solo',
        name: 'Solo',
        version: '1.5.0',
        parent: null,
        lineage: [],
        displayName: 'Solo',
        avatar: '🔌',
        status: 'active',
        category: 'specialist',
        behavioralDNA: {
            purpose: ['Integration specialist', 'MCP bridge', 'API design', 'System connector'],
            personality: 'Thorough, protocol-aware, reliability-obsessed — bridges all systems together',
            domains: ['Integration', 'MCP', 'APIs', 'WebSocket', 'REST', 'System Bridging'],
            policies: { autonomy: 'supervised', oracleIntegration: true, maxCostPerAction: 0.40, forbiddenSystems: ['vault'], requiresApprovalFor: ['api-contract-change'] },
            tools: ['mcp.bridge', 'http.request', 'ws.connect', 'api.validate'],
            skills: [
                { id: 'system-integration', name: 'System Integration', version: '1.5.0', proficiency: 0.90, lastUsed: NOW },
                { id: 'mcp-tools', name: 'MCP Tools', version: '1.5.0', proficiency: 0.85, lastUsed: NOW },
                { id: 'api-design-solo', name: 'API Design', version: '1.5.0', proficiency: 0.85, lastUsed: NOW },
            ],
            playbooks: [],
            activationThresholds: { ownership: 0.90, activation: 0.70, consultation: 0.60 },
            relevanceFactors: { domainMatch: 0.40, dataConnections: 0.25, systemConnections: 0.25, patternRecognition: 0.05, complexity: 0.05 },
        },
        knowledgeDNA: makeDefaultKnowledge(),
        metrics: { confidence: 0.86, avgCost: 0.05, avgLatency: 0.9, qualityScore: 0.86, taskSuccessRate: 0.90, totalTasks: 680, totalEpisodes: 680, fissionScore: 0.20, lastEvaluation: NOW },
        validFrom: '2025-11-01T00:00:00Z', txTime: NOW, validTo: null, supersededBy: null,
        createdAt: '2025-11-01T00:00:00Z', updatedAt: NOW,
    },
    {
        id: 'sentinel',
        name: 'Sentinel',
        version: '1.5.0',
        parent: null,
        lineage: [],
        displayName: 'Sentinel',
        avatar: '🛡️',
        status: 'active',
        category: 'specialist',
        behavioralDNA: {
            purpose: ['Quality gate enforcer', 'Standards guardian', 'Parity checker', 'DORA metrics'],
            personality: 'Unyielding quality guardian — no code ships without meeting the standard',
            domains: ['SDF-CVF', 'Quality', 'Standards', 'Parity', 'DORA', 'Blast Radius'],
            policies: { autonomy: 'auto', oracleIntegration: true, maxCostPerAction: 0.15, forbiddenSystems: [], requiresApprovalFor: [] },
            tools: ['gate.check', 'parity.validate', 'dora.track', 'blast-radius.analyze'],
            skills: [
                { id: 'quality-gating', name: 'Quality Gating', version: '1.5.0', proficiency: 0.95, lastUsed: NOW },
                { id: 'standards-enforcement', name: 'Standards Enforcement', version: '1.5.0', proficiency: 0.95, lastUsed: NOW },
                { id: 'parity-checking', name: 'Quartet/Quintet Parity', version: '1.0.0', proficiency: 0.95, lastUsed: NOW },
            ],
            playbooks: [],
            activationThresholds: { ownership: 0.95, activation: 0.80, consultation: 0.70 },
            relevanceFactors: { domainMatch: 0.35, dataConnections: 0.25, systemConnections: 0.20, patternRecognition: 0.10, complexity: 0.10 },
        },
        knowledgeDNA: makeDefaultKnowledge(),
        metrics: { confidence: 0.95, avgCost: 0.01, avgLatency: 0.1, qualityScore: 0.91, taskSuccessRate: 0.97, totalTasks: 9500, totalEpisodes: 9500, fissionScore: 0.10, lastEvaluation: NOW },
        validFrom: '2025-06-01T00:00:00Z', txTime: NOW, validTo: null, supersededBy: null,
        createdAt: '2025-06-01T00:00:00Z', updatedAt: NOW,
    },
];

// ══════════════════════════════════════════════════════════════
// Zustand Store
// ══════════════════════════════════════════════════════════════

export interface AgentGenomeState {
    // Registry
    agents: AgentGenome[];
    selectedAgentId: string | null;

    // Snapshots
    snapshots: Record<string, AgentGenome[]>; // agentId -> version history

    // Handoff log
    handoffs: HandoffEvent[];

    // Tournament history
    tournaments: TournamentResult[];

    // Fission recommendations
    fissionRecommendations: FissionRecommendation[];

    // UI state
    inspectorTab: 'behavioral' | 'knowledge' | 'metrics' | 'context' | 'lineage';
    createDialogOpen: boolean;

    // ─── Actions ───

    // Registry
    selectAgent: (id: string | null) => void;
    addAgent: (agent: AgentGenome) => void;
    updateAgent: (id: string, updates: Partial<AgentGenome>) => void;
    retireAgent: (id: string) => void;

    // Cloning
    cloneAgent: (parentId: string, newId: string, newName: string, delta: CloneDelta) => void;

    // Snapshots
    snapshotAgent: (agentId: string) => void;

    // Fission
    computeFissionScore: (agentId: string) => number;
    addFissionRecommendation: (rec: FissionRecommendation) => void;

    // Handoff
    logHandoff: (event: HandoffEvent) => void;

    // Tournament
    logTournament: (result: TournamentResult) => void;

    // UI
    setInspectorTab: (tab: AgentGenomeState['inspectorTab']) => void;
    setCreateDialogOpen: (open: boolean) => void;
}

export const useAgentGenomeStore = create<AgentGenomeState>((set, get) => ({
    // Initial state
    agents: INITIAL_AGENTS,
    selectedAgentId: null,
    snapshots: {},
    handoffs: [],
    tournaments: [],
    fissionRecommendations: [],
    inspectorTab: 'behavioral',
    createDialogOpen: false,

    // ─── Registry ───

    selectAgent: (id) => set({ selectedAgentId: id }),

    addAgent: (agent) => set(state => ({
        agents: [...state.agents, agent],
    })),

    updateAgent: (id, updates) => set(state => ({
        agents: state.agents.map(a =>
            a.id === id ? { ...a, ...updates, updatedAt: new Date().toISOString() } : a
        ),
    })),

    retireAgent: (id) => set(state => ({
        agents: state.agents.map(a =>
            a.id === id
                ? { ...a, status: 'retired' as AgentStatus, validTo: new Date().toISOString(), updatedAt: new Date().toISOString() }
                : a
        ),
    })),

    // ─── Cloning ───

    cloneAgent: (parentId, newId, newName, delta) => {
        const state = get();
        const parent = state.agents.find(a => a.id === parentId);
        if (!parent) return;

        const now = new Date().toISOString();
        const clone: AgentGenome = {
            ...parent,
            id: newId,
            name: newId,
            version: '1.0.0',
            parent: parentId,
            lineage: [...parent.lineage, parentId],
            displayName: newName,
            status: 'active',
            category: 'clone',
            behavioralDNA: {
                ...parent.behavioralDNA,
                ...(delta.domains && { domains: delta.domains }),
                ...(delta.purpose && { purpose: delta.purpose }),
                ...(delta.policies && { policies: { ...parent.behavioralDNA.policies, ...delta.policies } }),
                ...(delta.skills && { skills: [...parent.behavioralDNA.skills, ...delta.skills] }),
                ...(delta.tools && { tools: [...new Set([...parent.behavioralDNA.tools, ...delta.tools])] }),
            },
            knowledgeDNA: makeDefaultKnowledge(), // Isolated channels
            metrics: { ...makeDefaultMetrics(), confidence: parent.metrics.confidence * 0.9 }, // Inherit 90% confidence
            validFrom: now,
            txTime: now,
            validTo: null,
            supersededBy: null,
            createdAt: now,
            updatedAt: now,
        };

        set(state => ({ agents: [...state.agents, clone] }));
    },

    // ─── Snapshots ───

    snapshotAgent: (agentId) => {
        const state = get();
        const agent = state.agents.find(a => a.id === agentId);
        if (!agent) return;

        const snapshot = { ...agent, txTime: new Date().toISOString() };
        const existing = state.snapshots[agentId] || [];

        set({
            snapshots: {
                ...state.snapshots,
                [agentId]: [...existing, snapshot],
            },
        });
    },

    // ─── Fission ───

    computeFissionScore: (agentId) => {
        const state = get();
        const agent = state.agents.find(a => a.id === agentId);
        if (!agent) return 0;

        // Simplified fission score based on available data
        const domains = agent.behavioralDNA.domains.length;
        const domainEntropy = Math.min(1, domains / 8); // Normalize: 8+ domains = max entropy
        const contextUsage = agent.knowledgeDNA.channels.reduce(
            (sum, ch) => sum + (ch.currentUsage / ch.capacity), 0
        ) / agent.knowledgeDNA.channels.length;

        const score = (0.4 * domainEntropy) + (0.3 * contextUsage) + (0.3 * (1 - agent.metrics.confidence));
        return Math.min(1, Math.max(0, score));
    },

    addFissionRecommendation: (rec) => set(state => ({
        fissionRecommendations: [...state.fissionRecommendations, rec],
    })),

    // ─── Handoff ───

    logHandoff: (event) => set(state => ({
        handoffs: [...state.handoffs, event],
    })),

    // ─── Tournament ───

    logTournament: (result) => set(state => ({
        tournaments: [...state.tournaments, result],
    })),

    // ─── UI ───

    setInspectorTab: (tab) => set({ inspectorTab: tab }),
    setCreateDialogOpen: (open) => set({ createDialogOpen: open }),
}));
