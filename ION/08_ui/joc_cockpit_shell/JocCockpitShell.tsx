import './joc-cockpit.css';
import './dispatch-authorization.css';
import './operator-approval.css';
import './ion-runtime-cockpit.css';
import { useEffect, useLayoutEffect, useRef, useState, type ReactNode } from 'react';
import { AutomationOverlayPanel } from './AutomationOverlayPanel';
import { CognitiveExplorerPanel } from './CognitiveExplorerPanel';
import { InfiniteContextCommandPalette } from './InfiniteContextCommandPalette';
import { DispatchAuthorizationPanel } from './DispatchAuthorizationPanel';
import { OperatorApprovalQueuePanel } from './OperatorApprovalQueuePanel';
import { DryRunDispatchHandoffPanel } from './DryRunDispatchHandoffPanel';
import { MissionDispatchRouterPanel } from './MissionDispatchRouterPanel';
import { ModelRouteMatrixPanel } from './ModelRouteMatrixPanel';
import { ReactiveOsStreamPanel } from './ReactiveOsStreamPanel';
import { RuntimeStatusPanel } from './RuntimeStatusPanel';
import { ServiceConsolePanel } from './ServiceConsolePanel';
import { SystemDiagnosticsPanel } from './SystemDiagnosticsPanel';
import { BranchGatewayConsumersPanel } from './BranchGatewayConsumersPanel';
import { HelixionEvolutionPanel } from './HelixionEvolutionPanel';
import { HelixionDevelopmentPanel } from './HelixionDevelopmentPanel';
import { HelixionAppsPreviewPanel } from './HelixionAppsPreviewPanel';
import { ProjectMissionControlPanel, projectMissionTabs, type ProjectTabId } from './VNextMissionControlPanel';
import { QueueGatewayCockpitPanel } from './QueueGatewayCockpitPanel';
import { AgentControlPlanePanel, agentControlTabs, type AgentControlTabId } from './AgentControlPlanePanel';
import { CodexWorkbenchShell, codexWorkbenchTabs, type CodexTabId } from './CodexWorkbenchShell';
import { CodexIdeWorkbenchPanel } from './CodexIdeWorkbenchPanel';
import { ExtensionMicroShellPanel } from './ExtensionMicroShellPanel';
import { BrowserGptDomTwinPanel } from './BrowserGptDomTwinPanel';
import { ScopeCockpitPanel } from './ScopeCockpitPanel';
import { DomainWeaverCockpitPanel } from './DomainWeaverCockpitPanel';
import { DocsProjectsPackagesPanel } from './DocsProjectsPackagesPanel';
import { CarrierTurnPanel } from './CarrierTurnPanel';
import { TaskReturnLedgerPanel } from './TaskReturnLedgerPanel';
import { StewardIntegrationQueuePanel } from './StewardIntegrationQueuePanel';
import { HumanGateQueuePanel } from './HumanGateQueuePanel';
import { OperatorMessageQueuePanel } from './OperatorMessageQueuePanel';
import { CursorHookStatePanel } from './CursorHookStatePanel';
import { ContextPackageInspectorPanel } from './ContextPackageInspectorPanel';
import { FrontDoorProofTracePanel } from './FrontDoorProofTracePanel';
import { LaneTimelinePanel } from './LaneTimelinePanel';
import { ReceiptHydrationPanel } from './ReceiptHydrationPanel';
import { RuntimeDebugOverlayPanel } from './RuntimeDebugOverlayPanel';
import { BuildWorkbenchPage } from './BuildWorkbenchPage';
import {
  AgentsIcon,
  ArchiveIcon,
  AssistantIcon,
  AuthorityIcon,
  BlockersIcon,
  ChatIcon,
  CodexIcon,
  DocsIcon,
  DomainsIcon,
  ExtensionIcon,
  GatesIcon,
  GraphIcon,
  HooksIcon,
  IdeIcon,
  LensIcon,
  ProjectsIcon,
  QueueIcon,
  QuestionsIcon,
  ReceiptIcon,
  RouteIcon,
  RunIcon,
  SettingsIcon,
  SkillsIcon,
  SourceIcon,
  StreamIcon,
  SystemIcon,
  ToolsIcon,
  TracesIcon,
  WorkSurfaceIcon,
  StatusIcon,
} from './icons';
import { v56CockpitProjectionFixture, type CockpitProjectionFixture } from './projectionFixtures';
import type { IonCockpitViewModel } from './ionRuntimeCockpitTypes';

export type JocCockpitShellProps = {
  projection?: CockpitProjectionFixture;
  runtimeProjection?: IonCockpitViewModel;
  onRuntimeRefresh?: () => void;
};

type LivePageId = 'mission' | 'scope' | 'weave' | 'system' | 'apps' | 'build' | 'projects' | 'agents' | 'queue' | 'codex' | 'ide' | 'browser-gpt' | 'extension' | 'docs' | 'gates' | 'receipts';
type LiveDrawerId = 'receipts' | 'context' | 'debug' | 'timeline';
type LiveSubnavItem = {
  id: string;
  label: string;
  icon: ReactNode;
  active: boolean;
  onSelect: () => void;
};
type RuntimeTimelineEvent = IonCockpitViewModel['timeline'][number];
type LivePageControls = {
  activeProjectTab: ProjectTabId;
  activeAgentTab: AgentControlTabId;
  activeCodexTab: CodexTabId;
  setProjectTab: (tab: ProjectTabId) => void;
  setAgentTab: (tab: AgentControlTabId) => void;
  setCodexTab: (tab: CodexTabId) => void;
  setActiveProjectTab: (tab: ProjectTabId) => void;
  setActiveAgentTab: (tab: AgentControlTabId) => void;
  setActiveCodexTab: (tab: CodexTabId) => void;
};

const liveTopNav: Array<{ id: LivePageId; icon: ReactNode; label: string; title: string; summary: string }> = [
  { id: 'mission', icon: <RunIcon />, label: 'RUN', title: 'Mission Control', summary: 'Runtime health, service console, rebuild state, and local development route status.' },
  { id: 'scope', icon: <WorkSurfaceIcon />, label: 'SCOPE', title: 'Scope Cockpit', summary: 'Objective, route, scheduler, context, proof, and accepted-state projection for selected Team Comms threads.' },
  { id: 'weave', icon: <GraphIcon />, label: 'WEAVE', title: 'Domain Weaver', summary: 'Domain map, queue governance, UI development readiness, bounded packets, and proof receipts.' },
  { id: 'system', icon: <SystemIcon />, label: 'SYS', title: 'System Diagnostics', summary: 'Same-port machine diagnostics, task manager, stale port cleanup, and lag evidence.' },
  { id: 'apps', icon: <WorkSurfaceIcon />, label: 'APPS', title: 'Helixion App Previews', summary: 'Select available apps, launch managed local previews, open active windows, stop servers, and capture diagnostics.' },
  { id: 'build', icon: <AssistantIcon />, label: 'BUILD', title: 'Build', summary: 'Blank crash-isolated builder surface with a floating Codex CLI builder chat and sandboxed preview stage.' },
  { id: 'projects', icon: <ProjectsIcon />, label: 'PROJECTS', title: 'Projects Mission Control', summary: 'Project spine, missions, blockers, open questions, evolution timeline, and vNext proof context.' },
  { id: 'agents', icon: <AgentsIcon />, label: 'AGENTS', title: 'ION Agent Control Plane', summary: 'Persona, Relay, Steward, role agents, Domain Weave, direct Codex runs, diagnostics, and proof history.' },
  { id: 'queue', icon: <QueueIcon />, label: 'QUEUE', title: 'Queue Gateway', summary: 'GPT Actions bridge, browser carrier queue, packet files, and queue authority boundaries.' },
  { id: 'codex', icon: <CodexIcon />, label: 'CODEX', title: 'Codex Workbench', summary: 'Context chat, response runs, worker handoffs, spawn queue, and task-return ledger.' },
  { id: 'ide', icon: <IdeIcon />, label: 'IDE', title: 'Codex IDE', summary: 'File tabs, diffs, live preview, rendered docs, media artifacts, and embedded Codex chat.' },
  { id: 'browser-gpt', icon: <ChatIcon />, label: 'GPT', title: 'Browser GPT', summary: 'ChatGPT DOM twin, mirrored controls, composer state, and selector health.' },
  { id: 'extension', icon: <ExtensionIcon />, label: 'EXT', title: 'Extension Micro-Shell', summary: 'Portable dAimon companion, browser extension contract, DOM perception, and page safety law.' },
  { id: 'docs', icon: <DocsIcon />, label: 'DOCS/PKG', title: 'Docs / Projects / Packages', summary: 'Project favorites, context packages, candidate zips, safe package state, and Custom GPT materials.' },
  { id: 'gates', icon: <GatesIcon />, label: 'GATES', title: 'Gates and Approvals', summary: 'Human gates, operator queue, steward queue, and blocked runtime state.' },
  { id: 'receipts', icon: <ReceiptIcon />, label: 'RECEIPTS', title: 'Receipts and Proof', summary: 'Hydrated receipts, proof trace, lane timeline, and accepted-state evidence.' },
] as const;

const drawerTabs: Array<{ id: LiveDrawerId; icon: ReactNode; label: string }> = [
  { id: 'receipts', icon: <ReceiptIcon />, label: 'receipts' },
  { id: 'context', icon: <LensIcon />, label: 'context' },
  { id: 'debug', icon: <SystemIcon />, label: 'debug' },
  { id: 'timeline', icon: <StreamIcon />, label: 'timeline' },
];
const SUBNAV_LABEL_MIN_WIDTH = 88;
const SUBNAV_MAX_WIDTH = 760;
const SUBNAV_VIEWPORT_RATIO = 0.56;
const AGENT_HASH_PREFIX = 'agent:';

export function JocCockpitShell({ projection = v56CockpitProjectionFixture, runtimeProjection, onRuntimeRefresh }: JocCockpitShellProps) {
  if (runtimeProjection) {
    return <LiveRuntimeCockpit projection={projection} runtime={runtimeProjection} onRuntimeRefresh={onRuntimeRefresh} />;
  }
  return <FixtureCockpit projection={projection} />;
}

function LiveRuntimeCockpit({ projection, runtime, onRuntimeRefresh }: { projection: CockpitProjectionFixture; runtime: IonCockpitViewModel; onRuntimeRefresh?: () => void }) {
  const defaultPage: LivePageId = (runtime.project_cockpit && runtime.project_cockpit.status !== 'missing') || (runtime.vnext_mission_control && runtime.vnext_mission_control.status !== 'missing') ? 'projects' : 'mission';
  const [activePage, setActivePage] = useState<LivePageId>(() => initialLivePageFromLocation(defaultPage));
  const [activeProjectTab, setActiveProjectTab] = useState<ProjectTabId>('projects');
  const [activeAgentTab, setActiveAgentTab] = useState<AgentControlTabId>('agents');
  const [activeCodexTab, setActiveCodexTab] = useState<CodexTabId>('chat');
  const [activeDrawer, setActiveDrawer] = useState<LiveDrawerId>('receipts');
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [timelineExpanded, setTimelineExpanded] = useState(false);
  const [subnavCompact, setSubnavCompact] = useState(false);
  const topbarRef = useRef<HTMLElement | null>(null);
  const brandRef = useRef<HTMLDivElement | null>(null);
  const primaryNavZoneRef = useRef<HTMLDivElement | null>(null);
  const page = liveTopNav.find((item) => item.id === activePage) ?? liveTopNav[0];
  const pageHashById = {
    mission: '',
    system: '#system',
    scope: '#scope',
    weave: '#weave',
    apps: '#apps',
    build: '#build',
    projects: '#projects',
    agents: '#agents',
    queue: '#queue',
    codex: '#codex',
    ide: '#ide',
    'browser-gpt': '#browser-gpt',
    extension: '#extension',
    docs: '#docs-packages',
    gates: '#gates',
    receipts: '#receipts',
  } as const satisfies Record<LivePageId, string>;

  const applyLocationHash = (nextPage: LivePageId, options?: { replace?: boolean }) => {
    if (typeof window === 'undefined') return;
    const nextHash = pageHashById[nextPage];
    const pathname = (window.location.pathname || '/cockpit').startsWith('/cockpit/chat')
      ? '/cockpit'
      : (window.location.pathname || '/cockpit');
    const search = window.location.search || '';
    const nextHashPath = nextHash || '';
    const nextLocation = nextHashPath ? `${pathname}${search}${nextHashPath}` : `${pathname}${search}`;
    if (options?.replace) {
      window.history.replaceState(null, '', nextLocation);
    } else {
      window.location.hash = nextHash || '';
    }
  };

  const syncPageFromLocation = () => {
    if (typeof window === 'undefined') return;
    const nextHash = (window.location.hash || '').replace(/^#/, '');
    const [nextHashPage] = nextHash.split('?');
    if (nextHash === 'projects' || nextHash === 'projects:vnext' || nextHash === 'vnext') {
      setActivePage('projects');
      if (nextHash === 'projects:vnext' || nextHash === 'vnext') setActiveProjectTab('vnext');
      return;
    }
    if (nextHashPage === 'scope') {
      setActivePage('scope');
      return;
    }
    if (nextHash === 'system' || nextHash === 'sys') {
      setActivePage('system');
      return;
    }
    if (nextHash === 'apps' || nextHash === 'app-previews' || window.location.pathname.startsWith('/cockpit/apps')) {
      setActivePage('apps');
      return;
    }
    if (nextHash === 'build') {
      setActivePage('build');
      return;
    }
    if (nextHash === 'agents' || window.location.pathname.startsWith('/cockpit/agents')) {
      setActivePage('agents');
      return;
    }
    if (nextHash === 'team-comms') {
      setActivePage('agents');
      setActiveAgentTab('comms');
      return;
    }
    if (nextHash === 'domain-weave' || nextHash === 'weave') {
      setActivePage('weave');
      setActiveAgentTab('weave');
      return;
    }
    if (nextHash === 'domains') {
      setActivePage('agents');
      setActiveAgentTab('domains');
      return;
    }
    if (nextHash === 'automations') {
      setActivePage('agents');
      setActiveAgentTab('automations');
      return;
    }
    if (nextHash === 'agent-settings') {
      setActivePage('agents');
      setActiveAgentTab('settings');
      return;
    }
    if (nextHash === 'docs-packages') {
      setActivePage('docs');
      return;
    }
    if (nextHash === 'codex') {
      setActivePage('codex');
      return;
    }
    if (nextHash === 'ide') {
      setActivePage('ide');
      return;
    }
    if (nextHash === 'browser-gpt' || window.location.pathname.startsWith('/cockpit/browser-gpt')) {
      setActivePage('browser-gpt');
      return;
    }
    if (window.location.pathname.startsWith('/cockpit/chatgpt-dom-twin')) {
      setActivePage('browser-gpt');
      return;
    }
    if (nextHash === 'extension') {
      setActivePage('extension');
      return;
    }
    if (nextHash === 'queue') {
      setActivePage('queue');
      return;
    }
    if (nextHash === 'gates') {
      setActivePage('gates');
      return;
    }
    if (nextHash === 'receipts') {
      setActivePage('receipts');
      return;
    }
    if (nextHash.startsWith(AGENT_HASH_PREFIX)) {
      setActivePage('agents');
      return;
    }
    if (window.location.pathname.startsWith('/cockpit/chat')) {
      setActivePage('codex');
      return;
    }
    if (window.location.pathname.startsWith('/cockpit/browser-gpt')) {
      setActivePage('browser-gpt');
      return;
    }
    setActivePage(defaultPage);
  };

  const selectPage = (nextPage: LivePageId) => {
    setActivePage(nextPage);
    applyLocationHash(nextPage, { replace: true });
  };

  const selectAgentTab = (nextTab: AgentControlTabId) => {
    setActiveAgentTab(nextTab);
    if (nextTab === 'weave') {
      setActivePage('weave');
      applyLocationHash('weave', { replace: true });
      return;
    }
    applyLocationHash('agents', { replace: true });
    if (typeof window !== 'undefined') {
      window.location.hash = nextTab === 'comms' ? 'team-comms' : nextTab === 'settings' ? 'agent-settings' : nextTab;
    }
  };

  const selectProjectTab = (nextTab: ProjectTabId) => {
    setActiveProjectTab(nextTab);
    applyLocationHash('projects', { replace: true });
    if (typeof window !== 'undefined') {
      window.location.hash = nextTab === 'vnext' ? 'projects:vnext' : 'projects';
    }
  };

  const selectCodexTab = (nextTab: CodexTabId) => {
    setActiveCodexTab(nextTab);
    applyLocationHash('codex', { replace: true });
  };
  const pageControls: LivePageControls = {
    activeProjectTab,
    activeAgentTab,
    activeCodexTab,
    setProjectTab: selectProjectTab,
    setAgentTab: selectAgentTab,
    setCodexTab: selectCodexTab,
    setActiveProjectTab,
    setActiveAgentTab,
    setActiveCodexTab,
  };
  const activeSubnav = subnavForPage(activePage, pageControls);
  const subnavMeasureKey = activeSubnav.map((item) => item.id).join('|');
  const latestTimelineEvent = runtime.timeline[0];
  const liveDrawerSuppressed = activePage === 'codex' || activePage === 'ide' || activePage === 'weave' || activePage === 'build';
  const selectDrawer = (id: LiveDrawerId) => {
    setActiveDrawer(id);
    setDrawerOpen((open) => activeDrawer !== id || !open);
  };

  useEffect(() => {
    if (typeof window === 'undefined') return;
    syncPageFromLocation();
    window.addEventListener('hashchange', syncPageFromLocation);
    window.addEventListener('popstate', syncPageFromLocation);
    return () => {
      window.removeEventListener('hashchange', syncPageFromLocation);
      window.removeEventListener('popstate', syncPageFromLocation);
    };
  }, []);

  useLayoutEffect(() => {
    if (typeof window === 'undefined') return undefined;
    const topbar = topbarRef.current;
    const brand = brandRef.current;
    const primaryNavZone = primaryNavZoneRef.current;
    if (!topbar || !brand || !primaryNavZone) return undefined;

    let frame = 0;
    const measure = () => {
      const styles = window.getComputedStyle(topbar);
      const gap = Number.parseFloat(styles.columnGap || styles.gap || '0') || 0;
      const padding = (Number.parseFloat(styles.paddingLeft) || 0) + (Number.parseFloat(styles.paddingRight) || 0);
      const available = topbar.clientWidth - padding - brand.offsetWidth - primaryNavZone.offsetWidth - (gap * 2);
      const subnavMax = Math.min(topbar.clientWidth * SUBNAV_VIEWPORT_RATIO, SUBNAV_MAX_WIDTH);
      const effectiveAvailable = Math.max(0, Math.min(available, subnavMax));
      const required = activeSubnav.length * SUBNAV_LABEL_MIN_WIDTH;
      const shouldCompact = required > effectiveAvailable;
      setSubnavCompact((previous) => previous === shouldCompact ? previous : shouldCompact);
    };
    const schedule = () => {
      window.cancelAnimationFrame(frame);
      frame = window.requestAnimationFrame(measure);
    };
    const resizeObserver = typeof ResizeObserver === 'undefined' ? null : new ResizeObserver(schedule);
    resizeObserver?.observe(topbar);
    resizeObserver?.observe(brand);
    resizeObserver?.observe(primaryNavZone);
    window.addEventListener('resize', schedule);
    schedule();

    return () => {
      window.cancelAnimationFrame(frame);
      resizeObserver?.disconnect();
      window.removeEventListener('resize', schedule);
    };
  }, [activeSubnav.length, subnavMeasureKey]);

  return (
    <main className={`ion-joc-shell is-page-${activePage} ${liveDrawerSuppressed ? 'is-live-drawer-suppressed' : ''} ${timelineExpanded ? 'is-timeline-expanded' : 'is-timeline-collapsed'} ${drawerOpen ? 'is-drawer-open' : 'is-drawer-closed'}`} data-version={runtime.runtime.version} data-mode="live-runtime">
      <header className="ion-topbar" ref={topbarRef}>
        <div className="ion-brand" ref={brandRef}>CodeGPT</div>
        <div className="ion-primary-nav-zone" ref={primaryNavZoneRef}>
          <nav className="ion-topnav ion-primary-page-nav" aria-label="Primary cockpit groups">
            {liveTopNav.map((item) => (
            <button aria-label={item.title} className={activePage === item.id ? 'is-active' : undefined} key={item.id} onClick={() => selectPage(item.id)} title={item.title} type="button">
                <span className="ion-nav-icon" aria-hidden="true">{item.icon}</span>
                <span className="ion-nav-label">{item.label}</span>
              </button>
            ))}
          </nav>
        </div>
        <nav className={`ion-cockpit-subnav${subnavCompact ? ' is-compact' : ''}`} aria-label={`${page.title} pages`}>
          {activeSubnav.map((item) => (
            <button aria-label={item.label} className={item.active ? 'is-active' : undefined} key={item.id} onClick={item.onSelect} title={item.label} type="button">
              <span className="ion-nav-icon" aria-hidden="true">{item.icon}</span>
              <span className="ion-nav-label">{item.label}</span>
            </button>
          ))}
        </nav>
      </header>

      <section className={`ion-main-work-surface ion-live-page is-${activePage}`} aria-label="Maintained work surface">
        <div className="ion-live-page-header">
          <div>
            <div className="ion-section-title">ACTIVE PAGE</div>
            <h1>{page.title}</h1>
            <p>{page.summary}</p>
          </div>
          <div className="ion-live-page-mode">PAGE / {page.label}</div>
        </div>
        <div className="ion-live-page-body">
          {renderLivePage(activePage, runtime, projection, onRuntimeRefresh, pageControls)}
        </div>
      </section>

      {!liveDrawerSuppressed ? (
        <aside className={`ion-right-inspector ion-live-drawer${drawerOpen ? ' is-open' : ' is-closed'}`} aria-hidden={!drawerOpen} aria-label="Receipt and evidence inspector">
          <div className="ion-live-drawer-tabs">
            {drawerTabs.map((tab) => (
              <button className={drawerOpen && activeDrawer === tab.id ? 'is-active' : undefined} key={tab.id} onClick={() => selectDrawer(tab.id)} title={tab.label} type="button">
                <span className="ion-drawer-tab-icon" aria-hidden="true">{tab.icon}</span>
                {drawerOpen ? <span>{tab.label}</span> : null}
              </button>
            ))}
          </div>
          <div className="ion-live-drawer-content">
            {renderLiveDrawer(activeDrawer, runtime)}
          </div>
        </aside>
      ) : null}

      <footer className={`ion-bottom-timeline ${timelineExpanded ? 'is-expanded' : 'is-collapsed'}`} aria-label="Reactive OS stream">
        <div className="ion-bottom-timeline-bar">
          <span className="ion-section-title">LIVE RUNTIME STREAM</span>
          <b>{runtime.timeline.length}</b>
          {renderLatestTimelineEvent(latestTimelineEvent)}
          {renderRuntimeStateStrip(runtime)}
          {activePage === 'codex' ? <span className="ion-codex-context-map-bottom-slot" id="ion-codex-context-map-bottom-slot" /> : null}
          <button onClick={() => setTimelineExpanded((previous) => !previous)} type="button">
            {timelineExpanded ? 'MINIMIZE' : 'EXPAND'}
          </button>
        </div>
        {timelineExpanded ? (
          <div className="ion-stream-stack">
            {runtime.timeline.map((event, index) => (
              <article className={`ion-stream-event is-${event.status}`} key={`${event.source}-${index}`}>
                <div className="ion-stream-event-head"><span>{event.source}</span><span>{event.event_type}</span><b>{event.status}</b></div>
                <p>{event.detail || event.path}</p>
              </article>
            ))}
          </div>
        ) : null}
      </footer>
    </main>
  );
}

function initialLivePageFromLocation(fallback: LivePageId): LivePageId {
  if (typeof window === 'undefined') return fallback;
  const hash = (window.location.hash || '').replace(/^#/, '').split('?')[0];
  const path = window.location.pathname || '';
  if (hash === 'codex' || path.startsWith('/cockpit/chat')) return 'codex';
  if (hash === 'ide' || path.startsWith('/cockpit/ide')) return 'ide';
  if (hash === 'browser-gpt' || path.startsWith('/cockpit/browser-gpt') || path.startsWith('/cockpit/chatgpt-dom-twin')) return 'browser-gpt';
  if (hash === 'scope') return 'scope';
  if (hash === 'system' || hash === 'sys') return 'system';
  if (hash === 'apps' || hash === 'app-previews' || path.startsWith('/cockpit/apps')) return 'apps';
  if (hash === 'build') return 'build';
  if (hash === 'projects' || hash === 'projects:vnext' || hash === 'vnext') return 'projects';
  if (hash === 'agents' || hash === 'team-comms' || hash.startsWith(AGENT_HASH_PREFIX) || path.startsWith('/cockpit/agents')) return 'agents';
  if (hash === 'domain-weave' || hash === 'weave') return 'weave';
  if (hash === 'queue') return 'queue';
  if (hash === 'extension') return 'extension';
  if (hash === 'docs-packages') return 'docs';
  if (hash === 'gates') return 'gates';
  if (hash === 'receipts') return 'receipts';
  return fallback;
}

function subnavForPage(activePage: LivePageId, controls: LivePageControls): LiveSubnavItem[] {
  if (activePage === 'projects') {
    return projectMissionTabs.map((tab) => ({
      id: tab.id,
      label: tab.label,
      icon: projectNavIcon(tab.id),
      active: controls.activeProjectTab === tab.id,
      onSelect: () => controls.setActiveProjectTab(tab.id),
    }));
  }
  if (activePage === 'agents') {
    return agentControlTabs.map((tab) => ({
      id: tab.id,
      label: tab.label,
      icon: agentNavIcon(tab.id),
      active: controls.activeAgentTab === tab.id,
      onSelect: () => controls.setAgentTab(tab.id),
    }));
  }
  if (activePage === 'codex') {
    return codexWorkbenchTabs.map((tab) => ({
      id: tab.id,
      label: tab.label,
      icon: codexNavIcon(tab.id),
      active: controls.activeCodexTab === tab.id,
      onSelect: () => controls.setCodexTab(tab.id),
    }));
  }
  return [{
    id: `${activePage}:overview`,
    label: 'OVERVIEW',
    icon: <WorkSurfaceIcon />,
    active: true,
    onSelect: () => undefined,
  }];
}

function projectNavIcon(tab: ProjectTabId): ReactNode {
  switch (tab) {
    case 'projects': return <ProjectsIcon />;
    case 'vnext': return <WorkSurfaceIcon />;
    case 'missions': return <GraphIcon />;
    case 'blockers': return <BlockersIcon />;
    case 'questions': return <QuestionsIcon />;
    case 'timeline': return <StreamIcon />;
    case 'protocols': return <RouteIcon />;
    case 'context': return <LensIcon />;
    default: return <WorkSurfaceIcon />;
  }
}

function agentNavIcon(tab: AgentControlTabId): ReactNode {
  switch (tab) {
    case 'agents': return <AgentsIcon />;
    case 'comms': return <ChatIcon />;
    case 'domains': return <DomainsIcon />;
    case 'settings': return <SettingsIcon />;
    default: return <AgentsIcon />;
  }
}

function codexNavIcon(tab: CodexTabId): ReactNode {
  switch (tab) {
    case 'chat': return <ChatIcon />;
    case 'ion': return <AgentsIcon />;
    case 'ide': return <IdeIcon />;
    case 'archive': return <ArchiveIcon />;
    case 'context': return <LensIcon />;
    case 'settings': return <SettingsIcon />;
    case 'hooks': return <HooksIcon />;
    case 'skills': return <SkillsIcon />;
    case 'tools': return <ToolsIcon />;
    case 'traces': return <TracesIcon />;
    case 'queue': return <QueueIcon />;
    default: return <CodexIcon />;
  }
}

function renderLatestTimelineEvent(event: RuntimeTimelineEvent | undefined): ReactNode {
  if (!event) {
    return (
      <span className="ion-bottom-timeline-latest ion-bottom-event-chip" aria-label="No timeline events" title="No timeline events">
        <StreamIcon />
        <span>0</span>
      </span>
    );
  }
  const source = String(event.source ?? 'EVENT');
  const eventType = String(event.event_type ?? 'STATE');
  const status = String(event.status ?? 'UNKNOWN');
  const title = `${source} / ${eventType} / ${status}`;
  return (
    <span className="ion-bottom-timeline-latest ion-bottom-event-chip" aria-label={title} title={title}>
      {timelineIconForValue(source)}
      {timelineIconForValue(eventType)}
      <span>{status}</span>
    </span>
  );
}

function timelineIconForValue(value: string): ReactNode {
  const normalized = value.toLowerCase();
  if (normalized.includes('hook')) return <HooksIcon />;
  if (normalized.includes('cursor') || normalized.includes('system')) return <SystemIcon />;
  if (normalized.includes('queue')) return <QueueIcon />;
  if (normalized.includes('codex') || normalized.includes('chat')) return <CodexIcon />;
  if (normalized.includes('project')) return <ProjectsIcon />;
  if (normalized.includes('agent')) return <AgentsIcon />;
  if (normalized.includes('receipt') || normalized.includes('proof')) return <ReceiptIcon />;
  if (normalized.includes('gate') || normalized.includes('authority')) return <AuthorityIcon />;
  if (normalized.includes('package') || normalized.includes('pkg')) return <ArchiveIcon />;
  return <StreamIcon />;
}

function renderRuntimeStateStrip(runtime: IonCockpitViewModel): ReactNode {
  const topBar = runtime.top_bar;
  return (
    <div className="ion-state-strip ion-bottom-state-strip">
      <BottomMetric icon={<SourceIcon />} label="Host" value="CARRIER-CONTROL" />
      <BottomMetric icon={<AuthorityIcon />} label="Steward" value="QUEUED AUTHORITY" />
      <BottomMetric icon={<SystemIcon />} label="System / swap" value={`${Math.round(topBar.system_cpu_percent ?? 0)}% / ${Math.round(topBar.system_swap_percent ?? 0)}%`} />
      <BottomMetric icon={<QueueIcon />} label="Action queue" value={`${topBar.browser_carrier_message_count ?? 0}/${topBar.codex_work_request_count ?? 0}`} />
      <BottomMetricPair
        firstIcon={<ProjectsIcon />}
        firstLabel="Projects"
        firstValue={topBar.project_count ?? 0}
        secondIcon={<BlockersIcon />}
        secondLabel="Blockers"
        secondValue={topBar.project_open_blocker_count ?? 0}
      />
      <BottomMetricPair
        firstIcon={<AgentsIcon />}
        firstLabel="Agents"
        firstValue={topBar.agent_control_plane_agent_count ?? 0}
        secondIcon={<DomainsIcon />}
        secondLabel="Domains"
        secondValue={topBar.agent_control_plane_domain_count ?? 0}
      />
      <BottomMetricPair
        firstIcon={<WorkSurfaceIcon />}
        firstLabel="vNext"
        firstValue={topBar.vnext_current_packet ?? 'NA'}
        secondIcon={<GatesIcon />}
        secondLabel="Gates"
        secondValue={topBar.vnext_open_gate_count ?? 0}
      />
      <BottomMetricPair
        firstIcon={<ChatIcon />}
        firstLabel="Codex chat turns"
        firstValue={topBar.codex_capsule_chat_turn_count ?? 0}
        secondIcon={<CodexIcon />}
        secondLabel="Codex response runs"
        secondValue={topBar.codex_capsule_chat_response_run_count ?? 0}
      />
      <BottomMetricPair
        firstIcon={<ExtensionIcon />}
        firstLabel="Extension"
        firstValue={topBar.extension_version ?? 'NA'}
        secondIcon={<DomainsIcon />}
        secondLabel="DOM"
        secondValue={topBar.page_perception_domain_count ?? 0}
      />
      <BottomMetricPair
        firstIcon={<ArchiveIcon />}
        firstLabel="Context packages"
        firstValue={topBar.context_package_count ?? 0}
        secondIcon={<ReceiptIcon />}
        secondLabel="Artifact packages"
        secondValue={topBar.artifact_package_count ?? 0}
      />
      <BottomMetric className={runtime.runtime.blocked ? 'ion-runtime-top-warning' : undefined} icon={<StatusIcon />} label="Status" value={runtime.runtime.status} />
    </div>
  );
}

function BottomMetric({ className, icon, label, value }: { className?: string; icon: ReactNode; label: string; value: ReactNode }) {
  const title = `${label}: ${String(value)}`;
  return (
    <span className={`ion-bottom-metric${className ? ` ${className}` : ''}`} aria-label={title} title={title}>
      {icon}
      <span>{value}</span>
    </span>
  );
}

function BottomMetricPair({
  firstIcon,
  firstLabel,
  firstValue,
  secondIcon,
  secondLabel,
  secondValue,
}: {
  firstIcon: ReactNode;
  firstLabel: string;
  firstValue: ReactNode;
  secondIcon: ReactNode;
  secondLabel: string;
  secondValue: ReactNode;
}) {
  const title = `${firstLabel}: ${String(firstValue)} / ${secondLabel}: ${String(secondValue)}`;
  return (
    <span className="ion-bottom-metric ion-bottom-metric-pair" aria-label={title} title={title}>
      <span className="ion-bottom-metric-part">{firstIcon}<span>{firstValue}</span></span>
      <span className="ion-bottom-metric-part">{secondIcon}<span>{secondValue}</span></span>
    </span>
  );
}

function renderLivePage(
  activePage: LivePageId,
  runtime: IonCockpitViewModel,
  projection: CockpitProjectionFixture,
  onRuntimeRefresh: (() => void) | undefined,
  controls: LivePageControls,
): ReactNode {
    switch (activePage) {
    case 'scope':
      return <ScopeCockpitPanel onRuntimeRefresh={onRuntimeRefresh} />;
    case 'weave':
      return <DomainWeaverCockpitPanel runtime={runtime} onRuntimeRefresh={onRuntimeRefresh} />;
    case 'mission':
      return (
        <>
          <RuntimeStatusPanel runtime={runtime} />
          <BranchGatewayConsumersPanel runtime={runtime} />
          <ServiceConsolePanel runtime={runtime} onRuntimeRefresh={onRuntimeRefresh} />
          <HelixionEvolutionPanel runtime={runtime} />
          <HelixionDevelopmentPanel runtime={runtime} />
        </>
      );
    case 'system':
      return <SystemDiagnosticsPanel runtime={runtime} onRuntimeRefresh={onRuntimeRefresh} />;
    case 'apps':
      return <HelixionAppsPreviewPanel runtime={runtime} onRuntimeRefresh={onRuntimeRefresh} />;
    case 'build':
      return <BuildWorkbenchPage runtime={runtime} />;
    case 'projects':
      return (
        <ProjectMissionControlPanel
          activeTab={controls.activeProjectTab}
          hideSubtabs
          onActiveTabChange={controls.setProjectTab}
          onRuntimeRefresh={onRuntimeRefresh}
          runtime={runtime}
        />
      );
    case 'agents':
      return (
        <AgentControlPlanePanel
          activeTab={controls.activeAgentTab}
          hideSubtabs
          onActiveTabChange={controls.setAgentTab}
          onRuntimeRefresh={onRuntimeRefresh}
          runtime={runtime}
        />
      );
    case 'queue':
      return (
        <>
          <QueueGatewayCockpitPanel runtime={runtime} />
          <CarrierTurnPanel runtime={runtime} />
          <OperatorMessageQueuePanel runtime={runtime} />
        </>
      );
    case 'codex':
      return (
        <CodexWorkbenchShell
          activeTab={controls.activeCodexTab}
          hideSubtabs
          onActiveTabChange={controls.setCodexTab}
          onRuntimeRefresh={onRuntimeRefresh}
          runtime={runtime}
        />
      );
    case 'ide':
      return <CodexIdeWorkbenchPanel runtime={runtime} onRuntimeRefresh={onRuntimeRefresh} />;
    case 'browser-gpt':
      return <BrowserGptDomTwinPanel runtime={runtime} onRuntimeRefresh={onRuntimeRefresh} />;
    case 'extension':
      return (
        <>
          <ExtensionMicroShellPanel runtime={runtime} />
          <FrontDoorProofTracePanel runtime={runtime} />
          <AutomationOverlayPanel events={projection.reactiveEvents} />
        </>
      );
    case 'docs':
      return (
        <>
          <DocsProjectsPackagesPanel runtime={runtime} />
          <ContextPackageInspectorPanel runtime={runtime} />
        </>
      );
    case 'gates':
      return (
        <>
          <HumanGateQueuePanel runtime={runtime} />
          <OperatorMessageQueuePanel runtime={runtime} />
          <StewardIntegrationQueuePanel runtime={runtime} />
        </>
      );
    case 'receipts':
      return (
        <>
          <ReceiptHydrationPanel runtime={runtime} />
          <TaskReturnLedgerPanel runtime={runtime} />
          <FrontDoorProofTracePanel runtime={runtime} />
        </>
      );
    default:
      return <RuntimeStatusPanel runtime={runtime} />;
  }
}

function renderLiveDrawer(activeDrawer: LiveDrawerId, runtime: IonCockpitViewModel): ReactNode {
  if (activeDrawer === 'context') {
    return (
      <>
        <ContextPackageInspectorPanel runtime={runtime} />
        <div className="ion-section-title">AUTHORITY CLASSES</div>
        <div className="ion-blocked-list">{runtime.authority_classes.map((cap) => <span key={cap}>{cap}</span>)}</div>
      </>
    );
  }
  if (activeDrawer === 'debug') {
    return <RuntimeDebugOverlayPanel runtime={runtime} />;
  }
  if (activeDrawer === 'timeline') {
    return <LaneTimelinePanel runtime={runtime} />;
  }
  return (
    <>
      <ReceiptHydrationPanel runtime={runtime} />
      <div className="ion-section-title">LIVE RECEIPT RAIL</div>
      {runtime.receipts.map((receipt, index) => (
        <article className="ion-receipt-card" key={`${String(receipt.path ?? index)}`}>
          <div className="ion-receipt-head"><span>{String(receipt.authority_class ?? 'RECEIPT')}</span><b>{String(receipt.name ?? 'receipt')}</b></div>
          <div className="ion-receipt-verdict">{String(receipt.path ?? '')}</div>
        </article>
      ))}
      {runtime.receipts.length === 0 && <div className="ion-empty-state">NO RECEIPTS FOUND</div>}
    </>
  );
}

function FixtureCockpit({ projection }: { projection: CockpitProjectionFixture }) {
  return (
    <main className="ion-joc-shell" data-version={projection.version}>
      <header className="ion-topbar">
        <div className="ion-brand">CodeGPT</div>
        <nav className="ion-topnav" aria-label="Primary cockpit groups">
          <button>OPERATIONS</button>
          <button>INTELLIGENCE</button>
          <button>INFRASTRUCTURE</button>
          <button>TOOLS</button>
        </nav>
        <div className="ion-state-strip">
          <span>STEWARD: {projection.stewardState}</span>
          <span>ORACLE: {projection.oracleMode}</span>
          <span>MISSION: {projection.missionRoute.verdict}</span>
        </div>
      </header>

      <section className="ion-main-work-surface" aria-label="Maintained work surface">
        <div className="ion-panel ion-hero-panel">
          <div className="ion-section-title">ACTIVE SURFACE</div>
          <h1>{projection.activeSurface}</h1>
          <div className="ion-verdict-band">{projection.missionRoute.verdict}</div>
          <div className="ion-grid-3">
            <Metric label="visual lineage" value="V44/V45/V48/V53/V54" />
            <Metric label="ui route" value="V55/V56/V57/V58/V59" />
            <Metric label="authority" value="preview only" />
          </div>
        </div>

        <InfiniteContextCommandPalette route={projection.cognitiveRoute} />
        <CognitiveExplorerPanel route={projection.cognitiveRoute} />
        <MissionDispatchRouterPanel route={projection.missionRoute} />
        <ModelRouteMatrixPanel route={projection.missionRoute} />
        <DispatchAuthorizationPanel />
        <OperatorApprovalQueuePanel />
        <DryRunDispatchHandoffPanel />

        <div className="ion-panel ion-visual-lens">
          <div className="ion-section-title">VISUAL EVIDENCE LENS</div>
          <div className="ion-evidence-chain">
            <span>OBSERVE</span><span>DIAGNOSE</span><span>VERIFY</span><span>RUN</span><span>BIND</span><span>ROUTE</span><span>DISPATCH PREVIEW</span>
          </div>
          <p>Closure, context routes, and mission routes may be displayed only as scoped evidence. Production automation, paid cloud launch, and unrestricted browser control remain blocked.</p>
        </div>

        <AutomationOverlayPanel events={projection.reactiveEvents} />
      </section>

      <aside className="ion-right-inspector" aria-label="Receipt and evidence inspector">
        <div className="ion-section-title">RECEIPT RAIL</div>
        {projection.receiptSummaries.map((receipt) => (
          <article className="ion-receipt-card" key={receipt.id}>
            <div className="ion-receipt-head"><span>{receipt.family}</span><b>{receipt.claimLane}</b></div>
            <div className="ion-receipt-verdict">{receipt.verdict}</div>
            <div className="ion-receipt-scope">{receipt.authorityScope}</div>
            <ul>{receipt.evidenceRefs.map((ref) => <li key={ref}>{ref}</li>)}</ul>
          </article>
        ))}
        <div className="ion-section-title">BLOCKED CAPABILITIES</div>
        <div className="ion-blocked-list">{projection.blockedCapabilities.map((cap) => <span key={cap}>{cap}</span>)}</div>
      </aside>

      <footer className="ion-bottom-timeline" aria-label="Reactive OS stream">
        <span className="ion-section-title">REACTIVE OS STREAM</span>
        <ReactiveOsStreamPanel events={projection.reactiveEvents} />
      </footer>
    </main>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return <div className="ion-metric"><span>{label}</span><b>{value}</b></div>;
}
