import React from 'react';
import {
  MOCK_AGENTS,
  MOCK_SYSTEMS,
  MOCK_MISSIONS,
  MOCK_ACTIVITY,
  SYSTEM_COLORS,
  type AgentStatus,
  type MissionStatus,
  type ActivityType,
  type SystemId,
} from './store';
import { InstrumentPanel, LED, LCD, HealthBar } from './instruments';
import { LaunchVectorIcon, SignalPulseIcon, RadarIcon, RobotHeadIcon } from './icons';

// ═══════════════════════════════════════════════════════════════
// Status helpers
// ═══════════════════════════════════════════════════════════════

const agentLedColor = (status: AgentStatus) => {
  switch (status) {
    case 'active': return 'green' as const;
    case 'idle': return 'blue' as const;
    case 'error': return 'red' as const;
    case 'offline': return 'off' as const;
  }
};

const missionLedColor = (status: MissionStatus) => {
  switch (status) {
    case 'running': return 'green' as const;
    case 'complete': return 'blue' as const;
    case 'failed': return 'red' as const;
    case 'queued': return 'off' as const;
    case 'paused': return 'amber' as const;
  }
};

const activityIcon = (type: ActivityType) => {
  switch (type) {
    case 'mission': return <LaunchVectorIcon size={12} style={{ color: 'var(--led-green)' }} />;
    case 'agent': return <RobotHeadIcon size={12} style={{ color: 'var(--accent-amber)' }} />;
    case 'system': return <RadarIcon size={12} style={{ color: 'var(--led-blue)' }} />;
    case 'user': return <SignalPulseIcon size={12} style={{ color: 'var(--led-purple)' }} />;
  }
};

// ═══════════════════════════════════════════════════════════════
// QUADRANT 1: FORCE OVERVIEW — Agent Fleet
// ═══════════════════════════════════════════════════════════════

const ForceOverview: React.FC = () => {
  const activeCount = MOCK_AGENTS.filter(a => a.status === 'active').length;

  return (
    <InstrumentPanel
      title="FORCE OVERVIEW"
      truthState="MOCK"
      subtitle={`${activeCount}/${MOCK_AGENTS.length} active`}
    >
      <div className="agent-grid">
        {MOCK_AGENTS.map(agent => (
          <div key={agent.id} className="agent-card">
            <div className="agent-card-header">
              <LED color={agentLedColor(agent.status)} pulse={agent.status === 'active'} />
              <span className="agent-card-name">{agent.name}</span>
            </div>
            <div className="agent-card-role">{agent.role}</div>
            <div className="agent-card-task">{agent.currentTask}</div>
            <div className="agent-card-footer">
              <span className="agent-card-uptime">{agent.uptime}</span>
              <LCD variant={agent.status === 'active' ? 'green' : agent.status === 'error' ? 'red' : undefined}>
                {agent.status.toUpperCase()}
              </LCD>
            </div>
          </div>
        ))}
      </div>
    </InstrumentPanel>
  );
};

// ═══════════════════════════════════════════════════════════════
// QUADRANT 2: SYSTEM HEALTH — 8 Subsystems
// ═══════════════════════════════════════════════════════════════

const SystemHealth: React.FC = () => {
  const onlineCount = MOCK_SYSTEMS.filter(s => s.status === 'online').length;

  return (
    <InstrumentPanel
      title="SYSTEM HEALTH"
      truthState="MOCK"
      subtitle={`${onlineCount}/${MOCK_SYSTEMS.length} nominal`}
    >
      {MOCK_SYSTEMS.map(sys => (
        <div key={sys.id} className="system-row">
          <LED color={sys.status === 'online' ? 'green' : sys.status === 'degraded' ? 'amber' : 'off'} />
          <span
            className="system-row-id"
            style={{ color: SYSTEM_COLORS[sys.id as SystemId] }}
          >
            {sys.id}
          </span>
          <HealthBar value={sys.health} segments={10} showValue={false} />
          <span className="health-bar-value">{Math.round(sys.health * 100)}%</span>
          <span className="system-row-latency">
            <LCD variant={sys.latency > 100 ? 'red' : sys.latency > 50 ? undefined : 'green'}>
              {sys.latency}ms
            </LCD>
          </span>
        </div>
      ))}
    </InstrumentPanel>
  );
};

// ═══════════════════════════════════════════════════════════════
// QUADRANT 3: MISSION QUEUE — Active & Pending Missions
// ═══════════════════════════════════════════════════════════════

const MissionQueue: React.FC = () => {
  const runningCount = MOCK_MISSIONS.filter(m => m.status === 'running').length;

  return (
    <InstrumentPanel
      title="MISSION QUEUE"
      truthState="MOCK"
      subtitle={`${runningCount} running`}
    >
      {MOCK_MISSIONS.map(mission => (
        <div key={mission.id} className="mission-row">
          <LED color={missionLedColor(mission.status)} pulse={mission.status === 'running'} />
          <span className="mission-row-id">{mission.id}</span>
          <span className="mission-row-name">{mission.name}</span>
          <span className="mission-row-agent">{mission.agent}</span>
          <div className="mission-progress-bar">
            <div
              className={`mission-progress-fill ${mission.status}`}
              style={{ width: `${mission.progress * 100}%` }}
            />
          </div>
          <span className="mission-row-elapsed">{mission.elapsed}</span>
        </div>
      ))}
    </InstrumentPanel>
  );
};

// ═══════════════════════════════════════════════════════════════
// QUADRANT 4: ACTIVITY FEED — Chronological Event Log
// ═══════════════════════════════════════════════════════════════

const ActivityFeed: React.FC = () => (
  <InstrumentPanel
    title="ACTIVITY FEED"
    truthState="MOCK"
    subtitle={`${MOCK_ACTIVITY.length} events`}
  >
    {MOCK_ACTIVITY.map(event => (
      <div key={event.id} className="activity-row">
        <span className="activity-time">{event.timestamp}</span>
        <span className="activity-type-icon">{activityIcon(event.type)}</span>
        <span className="activity-message">
          {event.agent && <span className="activity-agent">{event.agent}: </span>}
          {event.message}
        </span>
      </div>
    ))}
  </InstrumentPanel>
);

// ═══════════════════════════════════════════════════════════════
// MISSION CONTROL — The Masterpiece Page
// ═══════════════════════════════════════════════════════════════

export const MissionControl: React.FC = () => (
  <div className="mission-control">
    <ForceOverview />
    <SystemHealth />
    <MissionQueue />
    <ActivityFeed />
  </div>
);
