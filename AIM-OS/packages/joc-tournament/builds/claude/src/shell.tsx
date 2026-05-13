import React from 'react';
import {
  useDashboardStore,
  WORKSPACES,
  NAV_GROUPS,
  MOCK_AGENTS,
  MOCK_SYSTEMS,
  MOCK_MISSIONS,
  MOCK_ACTIVITY,
  type NavGroup,
  type LeftDrawerPanel,
  type BottomTab,
  type AssistantMode,
} from './store';
import {
  JOCLogo, RadarIcon, ConstellationIcon, LaunchVectorIcon,
  CloseIcon, ChevronUpIcon, ChevronDownIcon,
} from './icons';
import { LED, LCD } from './instruments';

// ═══════════════════════════════════════════════════════════════
// TOP BAR — Primary navigation fascia
// ═══════════════════════════════════════════════════════════════

export const TopBar: React.FC = () => {
  const { activeWorkspace, setActiveWorkspace, oracleMode, pendingApprovals } = useDashboardStore();

  const activeGroup = WORKSPACES.find(w => w.id === activeWorkspace)?.navGroup;

  return (
    <div className="topbar">
      <div className="topbar-logo">
        <JOCLogo size={22} />
        <span className="topbar-logo-text">JARVIS</span>
      </div>

      <nav className="topbar-nav">
        {NAV_GROUPS.map(group => (
          <button
            key={group.id}
            className={`topbar-group${activeGroup === group.id ? ' active' : ''}`}
            onClick={() => setActiveWorkspace(group.defaultWorkspace)}
          >
            {group.label}
          </button>
        ))}
      </nav>

      <div className="topbar-right">
        <div className="topbar-oracle">
          <LED color={oracleMode === 'OFFLINE' ? 'off' : 'green'} size={5} />
          <span className="topbar-oracle-mode">{oracleMode}</span>
          {pendingApprovals > 0 && (
            <span className="topbar-oracle-count">{pendingApprovals}</span>
          )}
        </div>
        <span className="topbar-shortcut">Ctrl+Shift+P</span>
      </div>
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════
// LEFT ICON RAIL — 48px drawer trigger column
// ═══════════════════════════════════════════════════════════════

const RAIL_ITEMS: { panel: LeftDrawerPanel; icon: React.FC<{ size?: number }>; label: string }[] = [
  { panel: 'system-status', icon: RadarIcon, label: 'System Status' },
  { panel: 'agent-fleet', icon: ConstellationIcon, label: 'Agent Fleet' },
  { panel: 'mission-queue', icon: LaunchVectorIcon, label: 'Mission Queue' },
];

export const LeftRail: React.FC = () => {
  const { leftDrawerOpen, leftDrawerPanel, toggleLeftDrawer } = useDashboardStore();

  return (
    <div className="left-rail">
      {RAIL_ITEMS.map(item => (
        <button
          key={item.panel}
          className={`rail-btn${leftDrawerOpen && leftDrawerPanel === item.panel ? ' active' : ''}`}
          onClick={() => toggleLeftDrawer(item.panel)}
          title={item.label}
        >
          <item.icon size={18} />
        </button>
      ))}
      <div className="rail-separator" />
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════
// LEFT DRAWER — Context panel bay
// ═══════════════════════════════════════════════════════════════

const DRAWER_TITLES: Record<LeftDrawerPanel, string> = {
  'system-status': 'SYSTEM STATUS',
  'agent-fleet': 'AGENT FLEET',
  'mission-queue': 'MISSION QUEUE',
};

const SystemStatusDrawer: React.FC = () => (
  <div>
    {MOCK_SYSTEMS.map(sys => (
      <div key={sys.id} className="drawer-item">
        <LED color={sys.status === 'online' ? 'green' : sys.status === 'degraded' ? 'amber' : 'off'} />
        <span style={{ fontFamily: 'var(--font-data)', fontSize: 10, fontWeight: 600, width: 32 }}>{sys.id}</span>
        <span style={{ flex: 1, fontSize: 10, color: 'var(--text-tertiary)' }}>{sys.name}</span>
        <span className="drawer-item-value">{Math.round(sys.health * 100)}%</span>
      </div>
    ))}
  </div>
);

const AgentFleetDrawer: React.FC = () => (
  <div>
    {MOCK_AGENTS.map(agent => (
      <div key={agent.id} className="drawer-item">
        <LED color={
          agent.status === 'active' ? 'green' :
          agent.status === 'idle' ? 'blue' :
          agent.status === 'error' ? 'red' : 'off'
        } />
        <span style={{ fontWeight: 500, fontSize: 11 }}>{agent.name}</span>
        <span style={{ flex: 1, fontSize: 9, color: 'var(--text-ghost)' }}>{agent.role}</span>
        <span className="drawer-item-value">{agent.uptime}</span>
      </div>
    ))}
  </div>
);

const MissionQueueDrawer: React.FC = () => (
  <div>
    {MOCK_MISSIONS.map(mission => (
      <div key={mission.id} className="drawer-item" style={{ flexWrap: 'wrap' }}>
        <LED color={
          mission.status === 'running' ? 'green' :
          mission.status === 'complete' ? 'blue' :
          mission.status === 'failed' ? 'red' :
          mission.status === 'queued' ? 'off' : 'amber'
        } />
        <span style={{ fontSize: 11, fontWeight: 500, flex: 1 }}>{mission.name}</span>
        <span className="drawer-item-value">
          {mission.status === 'running' ? `${Math.round(mission.progress * 100)}%` : mission.status}
        </span>
      </div>
    ))}
  </div>
);

const DRAWER_CONTENT: Record<LeftDrawerPanel, React.FC> = {
  'system-status': SystemStatusDrawer,
  'agent-fleet': AgentFleetDrawer,
  'mission-queue': MissionQueueDrawer,
};

export const LeftDrawer: React.FC = () => {
  const { leftDrawerOpen, leftDrawerPanel, closeLeftDrawer } = useDashboardStore();

  if (!leftDrawerOpen || !leftDrawerPanel) return null;

  const Content = DRAWER_CONTENT[leftDrawerPanel];

  return (
    <div className={`left-drawer${leftDrawerOpen ? '' : ' closed'}`}>
      <div className="drawer-header">
        <span className="drawer-title">{DRAWER_TITLES[leftDrawerPanel]}</span>
        <button className="drawer-close" onClick={closeLeftDrawer}>
          <CloseIcon size={12} />
        </button>
      </div>
      <div className="drawer-content">
        <Content />
      </div>
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════
// BOTTOM BAR — Status strip + expandable diagnostic panel
// ═══════════════════════════════════════════════════════════════

const BOTTOM_TABS: { id: BottomTab; label: string }[] = [
  { id: 'timeline', label: 'Timeline' },
  { id: 'comms', label: 'Comms' },
  { id: 'output', label: 'Output' },
  { id: 'terminal', label: 'Terminal' },
  { id: 'diagnostics', label: 'Diag' },
];

const DiagnosticsContent: React.FC = () => (
  <div>
    {[
      { time: '14:23:08', tag: 'agent', label: 'AGENT', msg: 'Lex: PDAS scan complete — 2 contradictions found' },
      { time: '14:21:45', tag: 'sys', label: 'SYS', msg: 'CAS cognitive drift: 0.12 above threshold' },
      { time: '14:19:22', tag: 'err', label: 'ERR', msg: 'Rev: HHNI index rebuild failed — insufficient atoms' },
      { time: '14:17:56', tag: 'agent', label: 'AGENT', msg: 'Aether: Context synthesis 72% — 34 evidence chains' },
      { time: '14:15:30', tag: 'sys', label: 'SYS', msg: 'Braden approved Oracle escalation policy v2.1' },
      { time: '14:12:11', tag: 'mcp', label: 'MCP', msg: 'Latency nominal at 8ms — 92 tools registered' },
      { time: '14:09:44', tag: 'agent', label: 'AGENT', msg: 'Codex: MCP gateway TLS hardened — gate 7 passed' },
      { time: '14:05:18', tag: 'agent', label: 'AGENT', msg: 'Dac: Dashboard UI Sprint completed' },
    ].map((entry, i) => (
      <div key={i} className="bottom-log-entry">
        <span className="bottom-log-time">{entry.time}</span>
        <span className={`bottom-log-tag ${entry.tag}`}>{entry.label}</span>
        <span className="bottom-log-msg">{entry.msg}</span>
      </div>
    ))}
  </div>
);

export const BottomBar: React.FC = () => {
  const { bottomBarSize, setBottomBarSize, bottomActiveTab, setBottomActiveTab } = useDashboardStore();

  // Calculate mission progress for the mini bar
  const runningMissions = MOCK_MISSIONS.filter(m => m.status === 'running');
  const avgProgress = runningMissions.length > 0
    ? runningMissions.reduce((sum, m) => sum + m.progress, 0) / runningMissions.length
    : 0;

  const activeAgents = MOCK_AGENTS.filter(a => a.status === 'active').length;
  const totalAtoms = 192;
  const mcpLatency = 8;

  return (
    <div className={`bottom-bar ${bottomBarSize}`}>
      <div className="bottom-header">
        {/* Size controls */}
        <div className="bottom-size-controls">
          <button
            className={`bottom-size-btn s1${bottomBarSize === 'collapsed' ? ' active' : ''}`}
            onClick={() => setBottomBarSize('collapsed')}
          />
          <button
            className={`bottom-size-btn s2${bottomBarSize === 'mid' ? ' active' : ''}`}
            onClick={() => setBottomBarSize('mid')}
          />
          <button
            className={`bottom-size-btn s3${bottomBarSize === 'full' ? ' active' : ''}`}
            onClick={() => setBottomBarSize('full')}
          />
        </div>

        {/* Mission progress */}
        <div className="bottom-metric">
          <span className="bottom-metric-label">Missions</span>
          <div className="bottom-mission-bar">
            <div
              className="bottom-mission-fill"
              style={{
                width: `${avgProgress * 100}%`,
                background: `linear-gradient(90deg, var(--led-green), var(--led-amber))`,
              }}
            />
          </div>
        </div>

        {/* Key metrics as LCD readouts */}
        <div className="bottom-metrics">
          <div className="bottom-metric">
            <span className="bottom-metric-label">MCP</span>
            <LCD>{mcpLatency}ms</LCD>
          </div>
          <div className="bottom-metric">
            <span className="bottom-metric-label">Agents</span>
            <LCD>{activeAgents}/6</LCD>
          </div>
          <div className="bottom-metric">
            <span className="bottom-metric-label">Atoms</span>
            <LCD>{totalAtoms}</LCD>
          </div>
        </div>

        {/* Tab buttons */}
        <div className="bottom-tabs">
          {BOTTOM_TABS.map(tab => (
            <button
              key={tab.id}
              className={`bottom-tab${bottomActiveTab === tab.id ? ' active' : ''}`}
              onClick={() => {
                setBottomActiveTab(tab.id);
                if (bottomBarSize === 'collapsed') setBottomBarSize('mid');
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Expanded content */}
      {bottomBarSize !== 'collapsed' && (
        <div className="bottom-panel">
          <DiagnosticsContent />
        </div>
      )}
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════
// ASSISTANT RAIL — Right-side intelligence companion
// ═══════════════════════════════════════════════════════════════

const RAIL_MODES: { id: AssistantMode; label: string }[] = [
  { id: 'chat', label: 'Chat' },
  { id: 'context', label: 'Context' },
  { id: 'actions', label: 'Actions' },
  { id: 'memory', label: 'Memory' },
];

const ChatContent: React.FC = () => (
  <>
    <div className="chat-messages">
      <div className="chat-msg system">
        J.A.R.V.I.S. online — 14 subsystems, 92 tools, 6 agents registered.
        <div className="chat-meta">
          <span>14:00:00</span>
          <span>SYS</span>
        </div>
      </div>
      <div className="chat-msg user">
        Show me the current agent force status and any failing missions.
        <div className="chat-meta">
          <span>14:12:30</span>
          <span>Braden</span>
        </div>
      </div>
      <div className="chat-msg assistant">
        4 agents active, 1 idle, 1 offline. Rev has a failing mission — HHNI
        index rebuild hit an atom limit at 34% progress. Recommend: increase
        atom allocation or reassign to Codex.
        <div className="chat-meta">
          <span>14:12:31</span>
          <span style={{ color: 'var(--led-green)' }}>0.94</span>
        </div>
      </div>
      <div className="chat-msg user">
        What's the CAS drift situation?
        <div className="chat-meta">
          <span>14:21:50</span>
          <span>Braden</span>
        </div>
      </div>
      <div className="chat-msg assistant">
        CAS reports cognitive drift at 0.12 above threshold. Health at 65%.
        Latency is elevated at 156ms. This correlates with the SEG degradation
        — both share evidence chain dependencies. Suggest: run CAS recalibration
        after SEG stabilizes.
        <div className="chat-meta">
          <span>14:21:51</span>
          <span style={{ color: 'var(--led-amber)' }}>0.87</span>
        </div>
      </div>
    </div>
  </>
);

const ContextContent: React.FC = () => (
  <div>
    <div className="context-section">
      <div className="context-label">Active Workspace</div>
      <div className="context-value">Mission Control</div>
    </div>
    <div className="context-section">
      <div className="context-label">System State</div>
      <div className="context-metric">
        <span className="context-metric-label">MCP Latency</span>
        <span className="context-metric-value">8ms</span>
      </div>
      <div className="context-metric">
        <span className="context-metric-label">Memory Atoms</span>
        <span className="context-metric-value">192</span>
      </div>
      <div className="context-metric">
        <span className="context-metric-label">Cognitive Drift</span>
        <span className="context-metric-value" style={{ color: 'var(--led-amber)' }}>0.12</span>
      </div>
      <div className="context-metric">
        <span className="context-metric-label">Active Goals</span>
        <span className="context-metric-value">4</span>
      </div>
      <div className="context-metric">
        <span className="context-metric-label">Evidence Chains</span>
        <span className="context-metric-value">34</span>
      </div>
    </div>
    <div className="context-section">
      <div className="context-label">Degraded Systems</div>
      <div className="context-metric">
        <span className="context-metric-label">SEG</span>
        <span className="context-metric-value" style={{ color: 'var(--led-amber)' }}>78% — 89ms</span>
      </div>
      <div className="context-metric">
        <span className="context-metric-label">CAS</span>
        <span className="context-metric-value" style={{ color: 'var(--led-amber)' }}>65% — 156ms</span>
      </div>
    </div>
  </div>
);

const ActionsContent: React.FC = () => (
  <div>
    <div className="context-section">
      <div className="context-label">Oracle Mode</div>
      <LCD variant="green">SUPERVISED</LCD>
    </div>

    <div className="context-section" style={{ marginTop: 16 }}>
      <div className="context-label">Pending Approvals</div>
      {[
        { title: 'Escalate HHNI rebuild to priority queue', agent: 'Rev', time: '14:19' },
        { title: 'Auto-merge evidence chains for Q1 synthesis', agent: 'Aether', time: '14:17' },
        { title: 'Deploy MCP gateway patch to production', agent: 'Codex', time: '14:09' },
      ].map((item, i) => (
        <div key={i} className="action-item">
          <LED color="amber" />
          <div className="action-item-content">
            <div className="action-item-title">{item.title}</div>
            <div className="action-item-meta">{item.agent} — {item.time}</div>
            <div className="action-btn-row">
              <button className="action-btn approve">APPROVE</button>
              <button className="action-btn deny">DENY</button>
            </div>
          </div>
        </div>
      ))}
    </div>
  </div>
);

const MemoryContent: React.FC = () => (
  <div>
    <div className="context-section">
      <div className="context-label">Memory Overview</div>
      <div className="context-metric">
        <span className="context-metric-label">Total Atoms</span>
        <span className="context-metric-value">192</span>
      </div>
      <div className="context-metric">
        <span className="context-metric-label">Total Tags</span>
        <span className="context-metric-value">47</span>
      </div>
      <div className="context-metric">
        <span className="context-metric-label">Evidence Chains</span>
        <span className="context-metric-value">34</span>
      </div>
    </div>
    <div className="context-section">
      <div className="context-label">Recent Sessions</div>
      {[
        { id: 'S-042', agent: 'Aether', topic: 'Q1 roadmap context synthesis', time: '4h 23m' },
        { id: 'S-041', agent: 'Codex', topic: 'MCP gateway hardening sprint', time: '6h 11m' },
        { id: 'S-040', agent: 'Lex', topic: 'PDAS contradiction audit', time: '3h 08m' },
      ].map((session, i) => (
        <div key={i} className="action-item">
          <LED color="blue" />
          <div className="action-item-content">
            <div className="action-item-title">{session.topic}</div>
            <div className="action-item-meta">{session.agent} — {session.id} — {session.time}</div>
          </div>
        </div>
      ))}
    </div>
  </div>
);

const RAIL_CONTENT: Record<AssistantMode, React.FC> = {
  chat: ChatContent,
  context: ContextContent,
  actions: ActionsContent,
  memory: MemoryContent,
};

export const AssistantRail: React.FC = () => {
  const { assistantExpanded, assistantMode, setAssistantMode } = useDashboardStore();

  if (!assistantExpanded) return null;

  const Content = RAIL_CONTENT[assistantMode];
  const activeAgents = MOCK_AGENTS.filter(a => a.status === 'active').length;

  return (
    <div className={`assistant-rail${assistantExpanded ? '' : ' collapsed'}`}>
      {/* Intelligence summary — always visible */}
      <div className="rail-summary">
        <div className="rail-summary-row">
          <LED color="green" size={5} />
          <span>Agents:</span>
          <span className="rail-summary-value">{activeAgents} active</span>
        </div>
        <div className="rail-summary-row">
          <LED color="amber" size={5} />
          <span>Approvals:</span>
          <span className="rail-summary-value">3 pending</span>
        </div>
        <div className="rail-summary-row">
          <LED color="blue" size={5} />
          <span>Last event:</span>
          <span className="rail-summary-value">14:23:08</span>
        </div>
      </div>

      {/* Mode tabs */}
      <div className="rail-modes">
        {RAIL_MODES.map(mode => (
          <button
            key={mode.id}
            className={`rail-mode-btn${assistantMode === mode.id ? ' active' : ''}`}
            onClick={() => setAssistantMode(mode.id)}
          >
            {mode.label}
          </button>
        ))}
      </div>

      {/* Content area */}
      <div className="rail-content">
        <Content />
      </div>

      {/* Chat input (only in chat mode) */}
      {assistantMode === 'chat' && (
        <div className="chat-input-area">
          <input className="chat-input" placeholder="Ask J.A.R.V.I.S..." />
          <button className="chat-send">&#8593;</button>
        </div>
      )}
    </div>
  );
};
