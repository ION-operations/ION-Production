import { useMemo, useRef, useState, type CSSProperties, type FocusEvent, type MouseEvent, type ReactNode } from 'react';
import { CodexWorkbenchShell } from './CodexWorkbenchShell';
import type { IonCockpitViewModel } from './ionRuntimeCockpitTypes';
import {
  AgentsIcon,
  BlockersIcon,
  BranchIcon,
  ChatIcon,
  CloseIcon,
  DomainsIcon,
  DocsIcon,
  EvidenceIcon,
  LensIcon,
  ProjectsIcon,
  QueueIcon,
  RollbackIcon,
  RunIcon,
  SourceIcon,
  StatusIcon,
  StreamIcon,
  SystemIcon,
} from './icons';

type IdeViewId = 'diffs' | 'preview' | 'docs' | 'media' | 'files';
type IdeDrawerId = 'explorer' | 'search' | 'source' | 'context' | 'docs' | 'runs' | 'agents';
type IdeBottomPanelId = 'problems' | 'diagnostics' | 'output' | 'terminal' | 'ports' | 'timeline';
type IdeBottomSize = 'compact' | 'normal' | 'tall';
type IdeTabKind = 'diff' | 'source' | 'doc' | 'preview' | 'media';
type IdeHoverSide = 'right' | 'left' | 'top' | 'bottom';

type IdeTab = {
  id: string;
  label: string;
  path: string;
  kind: IdeTabKind;
  status: string;
  record?: Record<string, unknown>;
};

type IdeDrawerContext = {
  archiveDiffEvidence: Array<Record<string, unknown>>;
  contextSurfaces: Array<Record<string, unknown>>;
  docsRows: Array<Record<string, unknown>>;
  drawerQuery: string;
  fileEdits: Array<Record<string, unknown>>;
  mediaRows: Array<Record<string, unknown>>;
  outputRows: Array<Record<string, unknown>>;
  portsRows: Array<Record<string, unknown>>;
  problemRows: Array<Record<string, unknown>>;
  responseRuns: Array<Record<string, unknown>>;
  runtime: IonCockpitViewModel;
  selectedPath: string;
  setActiveView: (view: IdeViewId) => void;
  setDrawerQuery: (query: string) => void;
  setSelectedTabId: (id: string) => void;
  taskReturns: Array<Record<string, unknown>>;
  terminalRows: Array<Record<string, unknown>>;
  tabs: IdeTab[];
};

type IdeDrawerSearchRow = {
  id: string;
  title: string;
  meta: string;
  path: string;
  status: string;
  tabId?: string;
  view?: IdeViewId;
};

type IdeHoverTip = {
  detail?: string;
  label: string;
  left: number;
  side: IdeHoverSide;
  top: number;
  width: number;
};

const ideViews: Array<{ id: IdeViewId; label: string; icon: ReactNode }> = [
  { id: 'diffs', label: 'DIFFS', icon: <RollbackIcon /> },
  { id: 'preview', label: 'PREVIEW', icon: <RunIcon /> },
  { id: 'docs', label: 'DOCS', icon: <DocsIcon /> },
  { id: 'media', label: 'MEDIA', icon: <EvidenceIcon /> },
  { id: 'files', label: 'FILES', icon: <SourceIcon /> },
];

const ideDrawers: Array<{ id: IdeDrawerId; label: string; icon: ReactNode }> = [
  { id: 'explorer', label: 'explorer', icon: <ProjectsIcon /> },
  { id: 'search', label: 'search', icon: <LensIcon /> },
  { id: 'source', label: 'source control', icon: <BranchIcon /> },
  { id: 'context', label: 'ion context', icon: <DomainsIcon /> },
  { id: 'docs', label: 'docs', icon: <DocsIcon /> },
  { id: 'runs', label: 'runs', icon: <StatusIcon /> },
  { id: 'agents', label: 'agents', icon: <AgentsIcon /> },
];

const bottomPanels: Array<{ id: IdeBottomPanelId; label: string; icon: ReactNode }> = [
  { id: 'problems', label: 'PROBLEMS', icon: <BlockersIcon /> },
  { id: 'diagnostics', label: 'DIAGNOSTICS', icon: <SystemIcon /> },
  { id: 'output', label: 'OUTPUT', icon: <QueueIcon /> },
  { id: 'terminal', label: 'TERMINAL', icon: <RunIcon /> },
  { id: 'ports', label: 'PORTS', icon: <SourceIcon /> },
  { id: 'timeline', label: 'TIMELINE', icon: <StreamIcon /> },
];

const previewRoutes = [
  { label: 'CODEX', value: '/cockpit#codex' },
  { label: 'IDE', value: '/cockpit#ide' },
  { label: 'WEAVE', value: '/cockpit#weave' },
  { label: 'PROJECTS', value: '/cockpit#projects' },
  { label: 'DOCS', value: '/cockpit#docs-packages' },
];

export function CodexIdeWorkbenchPanel({
  runtime,
  onRuntimeRefresh,
}: {
  runtime: IonCockpitViewModel;
  onRuntimeRefresh?: () => void;
}) {
  const workbenchRef = useRef<HTMLElement | null>(null);
  const [activeView, setActiveView] = useState<IdeViewId>('diffs');
  const [activeDrawer, setActiveDrawer] = useState<IdeDrawerId>('explorer');
  const [drawerOpen, setDrawerOpen] = useState(true);
  const [selectedTabId, setSelectedTabId] = useState('');
  const [previewRoute, setPreviewRoute] = useState('/cockpit#codex');
  const [drawerQuery, setDrawerQuery] = useState('');
  const [hoverTip, setHoverTip] = useState<IdeHoverTip | null>(null);
  const [bottomPanel, setBottomPanel] = useState<IdeBottomPanelId>('problems');
  const [bottomOpen, setBottomOpen] = useState(true);
  const [bottomSize, setBottomSize] = useState<IdeBottomSize>('normal');

  const chat = runtime.codex_capsule_chat;
  const cli = runtime.codex_cli_workbench;
  const ideWorkbench = runtime.codex_ide_workbench;
  const ideContextRegistry = record(ideWorkbench?.context_registry);
  const activeIdeBinding = record(ideContextRegistry.active_binding);
  const systemDiagnostics = runtime.system_diagnostics;
  const rollback = runtime.codex_git_rollback;
  const currentWorktree = record(rollback?.current_worktree);
  const diffStats = record(currentWorktree.diff_stats);
  const fileEdits = records(currentWorktree.file_edits);
  const archiveDiffEvidence = records(rollback?.archive_diff_evidence);
  const contextSurfaces = records(record(cli?.context).surfaces);
  const responseRuns = records(chat?.latest_response_runs);
  const taskReturns = records(chat?.latest_task_returns);
  const docsRows = useMemo(() => buildDocRows(runtime), [runtime]);
  const mediaRows = useMemo(() => buildMediaRows(runtime), [runtime]);
  const problemRows = useMemo(() => buildProblemRows(runtime, fileEdits, responseRuns, taskReturns), [fileEdits, responseRuns, runtime, taskReturns]);
  const outputRows = useMemo(() => buildOutputRows(runtime, responseRuns, taskReturns), [responseRuns, runtime, taskReturns]);
  const terminalRows = useMemo(() => buildTerminalRows(runtime, responseRuns, taskReturns), [responseRuns, runtime, taskReturns]);
  const portsRows = useMemo(() => buildPortRows(runtime), [runtime]);
  const timelineRows = useMemo(() => buildTimelineRows(runtime), [runtime]);
  const openTabs = useMemo(
    () => buildIdeTabs(fileEdits, contextSurfaces, docsRows, mediaRows),
    [contextSurfaces, docsRows, fileEdits, mediaRows],
  );
  const selectedTab = openTabs.find((tab) => tab.id === selectedTabId) ?? openTabs[0] ?? null;
  const selectedFile = selectedTab?.record ?? fileEdits[0] ?? contextSurfaces[0] ?? {};
  const selectedPath = text(selectedTab?.path || selectedFile.path || selectedFile.file_path || selectedFile.relpath, 'workspace');
  const currentEditCount = numberValue(diffStats.file_count) || fileEdits.length || numberValue(record(rollback?.current_git).scoped_porcelain_count);
  const previewReady = Boolean(previewRoute);
  const sourceCount = contextSurfaces.length + fileEdits.length;
  const contextBindingStatus = text(ideContextRegistry.status, 'no ide context registry');
  const bridgeStatus = text(ideContextRegistry.bridge_status, 'none_mounted');
  const bottomCounts: Record<IdeBottomPanelId, number> = {
    problems: problemRows.length,
    diagnostics: numberValue(systemDiagnostics?.summary?.issue_count) + numberValue(systemDiagnostics?.summary?.active_dev_server_count) + numberValue(systemDiagnostics?.summary?.listener_count),
    output: outputRows.length,
    terminal: terminalRows.length,
    ports: portsRows.length,
    timeline: timelineRows.length,
  };
  const ideContextBridgePayload = useMemo(() => buildIdeContextBridgePayload({
    activeDrawer,
    activeView,
    bottomOpen,
    bottomPanel,
    contextSurfaces,
    currentWorktree,
    diffStats,
    docsRows,
    drawerOpen,
    fileEdits,
    mediaRows,
    openTabs,
    outputRows,
    portsRows,
    previewReady,
    previewRoute,
    problemRows,
    responseRuns,
    runtime,
    selectedPath,
    selectedTab,
    systemDiagnostics: record(systemDiagnostics),
    taskReturns,
    terminalRows,
    timelineRows,
  }), [
    activeDrawer,
    activeView,
    bottomOpen,
    bottomPanel,
    contextSurfaces,
    currentWorktree,
    diffStats,
    docsRows,
    drawerOpen,
    fileEdits,
    mediaRows,
    openTabs,
    outputRows,
    portsRows,
    previewReady,
    previewRoute,
    problemRows,
    responseRuns,
    runtime,
    selectedPath,
    selectedTab,
    systemDiagnostics,
    taskReturns,
    terminalRows,
    timelineRows,
  ]);

  const selectDrawer = (id: IdeDrawerId) => {
    const same = activeDrawer === id;
    setActiveDrawer(id);
    setDrawerOpen(!same || !drawerOpen);
  };

  const hideIdeHoverTip = () => setHoverTip(null);

  const showIdeHoverTip = (
    event: MouseEvent<HTMLElement> | FocusEvent<HTMLElement>,
    label: string,
    side: IdeHoverSide,
    detail = '',
  ) => {
    const host = workbenchRef.current;
    if (!host) return;
    const hostRect = host.getBoundingClientRect();
    const rect = event.currentTarget.getBoundingClientRect();
    const width = Math.min(Math.max(rect.width + 78, 152), side === 'bottom' || side === 'top' ? 268 : 220);
    const centerLeft = rect.left - hostRect.left + rect.width / 2;
    const left = side === 'right'
      ? rect.right - hostRect.left + 7
      : side === 'left'
        ? rect.left - hostRect.left - 7
        : clampNumber(centerLeft - width / 2, 8, hostRect.width - width - 8);
    const top = side === 'bottom'
      ? rect.bottom - hostRect.top + 7
      : side === 'top'
        ? rect.top - hostRect.top - 7
        : rect.top - hostRect.top + rect.height / 2;
    setHoverTip({ detail, label, left, side, top, width });
  };

  return (
    <section className={`ion-codex-ide-workbench${drawerOpen ? ' has-left-drawer' : ''}`} aria-label="Codex IDE workbench" ref={workbenchRef}>
      <aside className="ion-codex-ide-rail" aria-label="IDE drawer controls">
        {ideDrawers.map((drawer) => (
          <button
            aria-label={drawer.label}
            className={drawerOpen && activeDrawer === drawer.id ? 'is-active' : undefined}
            key={drawer.id}
            onBlur={hideIdeHoverTip}
            onFocus={(event) => showIdeHoverTip(event, drawer.label, 'right', 'IDE drawer')}
            onMouseEnter={(event) => showIdeHoverTip(event, drawer.label, 'right', 'IDE drawer')}
            onMouseLeave={hideIdeHoverTip}
            onClick={() => selectDrawer(drawer.id)}
            type="button"
          >
            {drawer.icon}
          </button>
        ))}
      </aside>

      <aside className={`ion-codex-ide-left-drawer${drawerOpen ? ' is-open' : ''}`} aria-hidden={!drawerOpen} aria-label="IDE drawer">
        <header>
          <span>{activeDrawer}</span>
          <button
            aria-label="Close IDE drawer"
            onBlur={hideIdeHoverTip}
            onClick={() => setDrawerOpen(false)}
            onFocus={(event) => showIdeHoverTip(event, 'Close IDE drawer', 'bottom', activeDrawer)}
            onMouseEnter={(event) => showIdeHoverTip(event, 'Close IDE drawer', 'bottom', activeDrawer)}
            onMouseLeave={hideIdeHoverTip}
            type="button"
          >
            CLOSE
          </button>
        </header>
        <div className="ion-codex-ide-left-drawer-body">
          {renderIdeDrawer(activeDrawer, {
            archiveDiffEvidence,
            contextSurfaces,
            docsRows,
            drawerQuery,
            fileEdits,
            mediaRows,
            outputRows,
            portsRows,
            problemRows,
            responseRuns,
            runtime,
            selectedPath,
            setActiveView,
            setDrawerQuery,
            setSelectedTabId,
            taskReturns,
            terminalRows,
            tabs: openTabs,
          })}
        </div>
      </aside>

      <main className={`ion-codex-ide-main${bottomOpen ? ` has-bottom-panel is-bottom-${bottomSize}` : ' is-bottom-collapsed'}`}>
        <header className="ion-codex-ide-titlebar">
          <div>
            <span>CODEX IDE</span>
            <b>{shortPath(selectedPath)}</b>
            <code>{text(cli?.shell_root || runtime.runtime.shell_root, 'workspace root pending')}</code>
          </div>
          <div className="ion-codex-ide-title-metrics">
            <IdeMetric label="files" value={sourceCount} />
            <IdeMetric label="edits" value={currentEditCount} />
            <IdeMetric label="docs" value={docsRows.length} />
            <IdeMetric label="media" value={mediaRows.length} />
            <IdeMetric label="runs" value={responseRuns.length} />
            <IdeMetric label="context" value={contextBindingStatus} />
            <IdeMetric label="bridge" value={bridgeStatus} />
          </div>
        </header>

        <nav className="ion-codex-ide-file-tabs" aria-label="Open IDE tabs">
          {openTabs.map((tab) => (
            <button
              className={selectedTab?.id === tab.id ? 'is-active' : undefined}
              key={tab.id}
              onBlur={hideIdeHoverTip}
              onClick={() => {
                setSelectedTabId(tab.id);
                if (tab.kind === 'doc') setActiveView('docs');
                else if (tab.kind === 'media') setActiveView('media');
                else if (tab.kind === 'preview') setActiveView('preview');
                else setActiveView(tab.kind === 'diff' ? 'diffs' : 'files');
              }}
              onFocus={(event) => showIdeHoverTip(event, tab.label, 'bottom', `${tab.kind} / ${tab.path}`)}
              onMouseEnter={(event) => showIdeHoverTip(event, tab.label, 'bottom', `${tab.kind} / ${tab.path}`)}
              onMouseLeave={hideIdeHoverTip}
              type="button"
            >
              <span>{tab.kind}</span>
              <b>{tab.label}</b>
              <em>{tab.status}</em>
            </button>
          ))}
        </nav>

        <nav className="ion-codex-ide-viewbar" aria-label="IDE lenses">
          {ideViews.map((view) => (
            <button
              className={activeView === view.id ? 'is-active' : undefined}
              key={view.id}
              onBlur={hideIdeHoverTip}
              onClick={() => setActiveView(view.id)}
              onFocus={(event) => showIdeHoverTip(event, view.label, 'bottom', 'IDE lens')}
              onMouseEnter={(event) => showIdeHoverTip(event, view.label, 'bottom', 'IDE lens')}
              onMouseLeave={hideIdeHoverTip}
              type="button"
            >
              {view.icon}
              <span>{view.label}</span>
            </button>
          ))}
        </nav>

        <section className={`ion-codex-ide-editor-frame is-${activeView}`} aria-label="IDE main window">
          {activeView === 'diffs' ? renderDiffWorkspace(fileEdits, archiveDiffEvidence, selectedFile) : null}
          {activeView === 'preview' ? renderPreviewWorkspace(previewRoute, setPreviewRoute, previewReady) : null}
          {activeView === 'docs' ? renderDocsWorkspace(docsRows, selectedTab) : null}
          {activeView === 'media' ? renderMediaWorkspace(mediaRows, selectedTab) : null}
          {activeView === 'files' ? renderFilesWorkspace(contextSurfaces, fileEdits, selectedFile) : null}
        </section>

        <section className={`ion-codex-ide-bottom-drawer${bottomOpen ? ' is-open' : ' is-collapsed'}`} aria-label="IDE diagnostics drawer">
          <header className="ion-codex-ide-bottom-tabs">
            <nav aria-label="IDE bottom panels">
              {bottomPanels.map((panel) => (
                <button
                  className={bottomPanel === panel.id && bottomOpen ? 'is-active' : undefined}
                  key={panel.id}
                  onBlur={hideIdeHoverTip}
                  onClick={() => {
                    setBottomPanel(panel.id);
                    setBottomOpen(true);
                  }}
                  onFocus={(event) => showIdeHoverTip(event, panel.label, 'top', `${bottomCounts[panel.id]} projected rows`)}
                  onMouseEnter={(event) => showIdeHoverTip(event, panel.label, 'top', `${bottomCounts[panel.id]} projected rows`)}
                  onMouseLeave={hideIdeHoverTip}
                  type="button"
                >
                  {panel.icon}
                  <span>{panel.label}</span>
                  <b>{bottomCounts[panel.id]}</b>
                </button>
              ))}
            </nav>
            <div className="ion-codex-ide-bottom-actions">
              <button
                aria-label="Toggle bottom drawer height"
                onBlur={hideIdeHoverTip}
                onClick={() => setBottomSize((size) => size === 'compact' ? 'normal' : size === 'normal' ? 'tall' : 'compact')}
                onFocus={(event) => showIdeHoverTip(event, 'Toggle bottom drawer height', 'top', bottomSize)}
                onMouseEnter={(event) => showIdeHoverTip(event, 'Toggle bottom drawer height', 'top', bottomSize)}
                onMouseLeave={hideIdeHoverTip}
                type="button"
              >
                {bottomSize}
              </button>
              <button
                aria-label="Close bottom drawer"
                onBlur={hideIdeHoverTip}
                onClick={() => setBottomOpen(false)}
                onFocus={(event) => showIdeHoverTip(event, 'Close bottom drawer', 'top', bottomPanel)}
                onMouseEnter={(event) => showIdeHoverTip(event, 'Close bottom drawer', 'top', bottomPanel)}
                onMouseLeave={hideIdeHoverTip}
                type="button"
              >
                <CloseIcon />
              </button>
            </div>
          </header>
          {bottomOpen ? (
            <div className="ion-codex-ide-bottom-body">
              {renderBottomPanel(bottomPanel, {
                chat,
                cli,
                outputRows,
                portsRows,
                problemRows,
                runtime,
                systemDiagnostics: record(systemDiagnostics),
                terminalRows,
                timelineRows,
              })}
            </div>
          ) : null}
        </section>
      </main>

      <aside className="ion-codex-ide-chat-panel" aria-label="Codex AI chat">
        <header>
          <div>
            <span>AI CHAT</span>
            <b>{text(chat?.latest_response_status || chat?.verdict || 'ready')} / {shortPath(text(activeIdeBinding.binding_id || ideContextRegistry.active_binding_id, 'no context'))}</b>
          </div>
          <ChatIcon />
        </header>
        <CodexWorkbenchShell
          activeTab="chat"
          hideSubtabs
          ideContextBridge={ideContextBridgePayload}
          onRuntimeRefresh={onRuntimeRefresh}
          runtime={runtime}
          surface="chat-cell"
        />
      </aside>

      {renderIdeHoverTip(hoverTip)}
    </section>
  );
}

function buildIdeContextBridgePayload(input: {
  activeDrawer: IdeDrawerId;
  activeView: IdeViewId;
  bottomOpen: boolean;
  bottomPanel: IdeBottomPanelId;
  contextSurfaces: Array<Record<string, unknown>>;
  currentWorktree: Record<string, unknown>;
  diffStats: Record<string, unknown>;
  docsRows: Array<Record<string, unknown>>;
  drawerOpen: boolean;
  fileEdits: Array<Record<string, unknown>>;
  mediaRows: Array<Record<string, unknown>>;
  openTabs: IdeTab[];
  outputRows: Array<Record<string, unknown>>;
  portsRows: Array<Record<string, unknown>>;
  previewReady: boolean;
  previewRoute: string;
  problemRows: Array<Record<string, unknown>>;
  responseRuns: Array<Record<string, unknown>>;
  runtime: IonCockpitViewModel;
  selectedPath: string;
  selectedTab: IdeTab | null;
  systemDiagnostics: Record<string, unknown>;
  taskReturns: Array<Record<string, unknown>>;
  terminalRows: Array<Record<string, unknown>>;
  timelineRows: Array<Record<string, unknown>>;
}): Record<string, unknown> {
  const contextGraph = input.runtime.context_package_graph;
  const agentControl = input.runtime.agent_control_plane;
  const chatContext = record(input.runtime.codex_capsule_chat?.chat_context);
  const activeBinding = record(chatContext.active_binding);
  const contextSystems = [
    ...records(agentControl?.agents),
    ...records(agentControl?.domains),
    ...records(contextGraph?.branches),
  ];
  const agentMounts = [
    ...records(agentControl?.codex_mounts?.mounts),
    ...records(input.runtime.codex_capsule_chat?.fresh_agent_capsule_chats),
  ];
  return {
    schema_id: 'ion.codex_ide_context_bridge.client_payload.v0_1',
    source: 'codex_ide_workbench',
    active_view: input.activeView,
    active_drawer: input.activeDrawer,
    drawer_open: input.drawerOpen,
    bottom_panel: input.bottomPanel,
    bottom_open: input.bottomOpen,
    selected_path: input.selectedPath,
    selected_tab: input.selectedTab ? bridgeTabRow(input.selectedTab) : null,
    open_tabs: input.openTabs.slice(0, 18).map(bridgeTabRow),
    worktree: {
      file_count: numberValue(input.diffStats.file_count) || input.fileEdits.length,
      insertions: numberValue(input.diffStats.insertions),
      deletions: numberValue(input.diffStats.deletions),
      branch: text(record(input.currentWorktree.current_git).branch || record(input.currentWorktree.git).branch, ''),
      status: text(input.currentWorktree.status || input.runtime.codex_git_rollback?.summary?.status, 'projected'),
    },
    file_edits: bridgeRows(input.fileEdits, 28),
    context_surfaces: bridgeRows(input.contextSurfaces, 24),
    context_systems: bridgeRows(contextSystems, 24),
    docs: bridgeRows(input.docsRows, 18),
    media: bridgeRows(input.mediaRows, 18),
    problems: bridgeRows(input.problemRows, 24),
    diagnostics: bridgeRows(buildBridgeDiagnosticRows(input.runtime, input.systemDiagnostics), 18),
    output: bridgeRows([...input.outputRows, ...input.responseRuns, ...input.taskReturns], 14),
    terminal: bridgeRows(input.terminalRows, 14),
    ports: bridgeRows(input.portsRows, 14),
    timeline: bridgeRows(input.timelineRows, 24),
    agent_mounts: bridgeRows(agentMounts, 18),
    preview: {
      route: input.previewRoute,
      ready: input.previewReady,
      label: previewRoutes.find((route) => route.value === input.previewRoute)?.label ?? 'preview',
    },
    chat_context: {
      active_binding_id: text(chatContext.active_binding_id, ''),
      binding_id: text(activeBinding.binding_id, ''),
      domain_id: text(activeBinding.domain_id, ''),
      role_id: text(activeBinding.role_id, ''),
      branch_id: text(activeBinding.branch_id, ''),
      branch_title: text(activeBinding.branch_title, ''),
    },
    tool_capabilities: [
      { tool_id: 'ide.open_ref', label: 'Open file or artifact ref', authority: 'read_only' },
      { tool_id: 'ide.inspect_diff', label: 'Inspect selected worktree diff', authority: 'read_only' },
      { tool_id: 'ide.inspect_preview', label: 'Inspect active preview route', authority: 'read_only' },
      { tool_id: 'ide.inspect_diagnostics', label: 'Inspect bottom diagnostics branches', authority: 'read_only' },
    ],
  };
}

function bridgeTabRow(tab: IdeTab): Record<string, unknown> {
  return {
    id: tab.id,
    label: tab.label,
    path: tab.path,
    kind: tab.kind,
    status: tab.status,
  };
}

function bridgeRows(rows: Array<Record<string, unknown>>, limit: number) {
  return rows.slice(0, limit).map((row, index) => bridgeRow(row, `row-${index}`));
}

function bridgeRow(row: Record<string, unknown>, fallbackId: string): Record<string, unknown> {
  const path = text(row.path || row.file_path || row.relpath || row.source || row.latest_return_path || row.packet_path || row.request_path, '');
  return {
    id: text(row.id || row.run_id || row.request_id || row.session_id || path, fallbackId),
    title: text(row.title || row.label || row.display_name || row.role_id || row.agent_id || row.kind || shortPath(path), fallbackId),
    path,
    kind: text(row.kind || row.type || row.source || row.context_type || row.package_type, ''),
    status: text(row.status || row.verdict || row.state || row.severity || row.proof_status, ''),
    source: text(row.source || row.owner || row.carrier || row.agent_id, ''),
    meta: text(row.meta || row.domain_id || row.registry_primary_domain || row.model || row.route_model || row.generated_at || row.created_at, ''),
    detail: text(row.detail || row.summary || row.objective || row.message || row.finding, ''),
    line: row.line,
    column: row.column,
  };
}

function buildBridgeDiagnosticRows(runtime: IonCockpitViewModel, systemDiagnostics: Record<string, unknown>) {
  const summary = record(systemDiagnostics.summary);
  return [
    {
      id: 'system:issues',
      title: 'system diagnostics',
      status: text(systemDiagnostics.verdict || systemDiagnostics.status || 'projected'),
      detail: `${numberValue(summary.issue_count)} issues / ${numberValue(summary.listener_count)} listeners / ${numberValue(summary.active_dev_server_count)} dev servers`,
      source: 'system_diagnostics',
    },
    {
      id: 'runtime:root',
      title: 'runtime root',
      status: text(runtime.runtime?.status, 'ready'),
      path: text(runtime.runtime?.shell_root, ''),
      source: 'runtime',
    },
  ];
}

function renderIdeDrawer(id: IdeDrawerId, context: IdeDrawerContext) {
  if (id === 'search') return renderSearchDrawer(context);
  if (id === 'source') return renderSourceDrawer(context);
  if (id === 'context') return renderContextDrawer(context);
  if (id === 'docs') return renderDocsDrawer(context);
  if (id === 'runs') return renderRunsDrawer(context);
  if (id === 'agents') return renderAgentsDrawer(context);
  return renderExplorerDrawer(context);
}

function renderIdeHoverTip(tip: IdeHoverTip | null) {
  if (!tip) return null;
  return (
    <div
      className={`ion-codex-ide-hover-tip is-${tip.side}`}
      style={{
        left: tip.left,
        top: tip.top,
        width: tip.width,
      } as CSSProperties}
    >
      <span>{tip.side === 'right' || tip.side === 'left' ? 'IDE rail' : 'IDE control'}</span>
      <b>{tip.label}</b>
      {tip.detail ? <code>{tip.detail}</code> : null}
    </div>
  );
}

function renderExplorerDrawer(context: IdeDrawerContext) {
  const workspaceRows = buildWorkspaceTreeRows(context);
  const rootRows = buildWorkspaceRootRows(context.runtime);
  const folderCount = new Set(workspaceRows.map((row) => row.path.split('/').slice(0, -1).join('/')).filter(Boolean)).size;
  return (
    <div className="ion-codex-ide-drawer-stack">
      <DrawerSection title="ION explorer" value={workspaceRows.length}>
        <div className="ion-codex-ide-drawer-metrics">
          <DrawerMetric label="open" value={context.tabs.length} />
          <DrawerMetric label="files" value={context.fileEdits.length + context.contextSurfaces.length} />
          <DrawerMetric label="folders" value={folderCount} />
          <DrawerMetric label="roots" value={rootRows.length} />
        </div>
        <DrawerFact label="active" value={context.selectedPath} />
      </DrawerSection>

      <DrawerSection title="open editors" value={context.tabs.length}>
        {context.tabs.map((tab) => (
          <DrawerRowButton
            active={context.selectedPath === tab.path}
            key={tab.id}
            meta={tab.kind}
            onClick={() => selectIdeTab(tab, context)}
            path={tab.path}
            status={tab.status}
            title={tab.label}
          />
        ))}
        {!context.tabs.length ? <div className="ion-codex-ide-empty">NO OPEN EDITORS PROJECTED</div> : null}
      </DrawerSection>

      <DrawerSection title="ION roots" value={rootRows.length}>
        {rootRows.slice(0, 18).map((row) => (
          <DrawerRowButton
            key={row.id}
            meta={row.meta}
            path={row.path}
            status={row.status}
            title={row.title}
          />
        ))}
      </DrawerSection>

      <DrawerSection title="workspace tree" value={workspaceRows.length}>
        {workspaceRows.slice(0, 48).map((row) => (
          <DrawerRowButton
            key={row.id}
            meta={row.meta}
            onClick={() => selectDrawerSearchRow(row, context)}
            path={row.path}
            status={row.status}
            title={row.title}
          />
        ))}
      </DrawerSection>
    </div>
  );
}

function renderSearchDrawer(context: IdeDrawerContext) {
  const allRows = buildDrawerSearchRows(context);
  const rows = filterDrawerRows(allRows, context.drawerQuery);
  return (
    <div className="ion-codex-ide-drawer-stack">
      <DrawerSearchInput onChange={context.setDrawerQuery} value={context.drawerQuery} />
      <DrawerSection title="projected index" value={`${rows.length}/${allRows.length}`}>
        {rows.slice(0, 80).map((row) => (
          <DrawerRowButton
            key={row.id}
            meta={row.meta}
            onClick={() => selectDrawerSearchRow(row, context)}
            path={row.path}
            status={row.status}
            title={row.title}
          />
        ))}
        {!rows.length ? <div className="ion-codex-ide-empty">NO PROJECTED MATCHES</div> : null}
      </DrawerSection>
    </div>
  );
}

function renderSourceDrawer(context: IdeDrawerContext) {
  const rollback = context.runtime.codex_git_rollback;
  const currentGit = record(rollback?.current_git);
  const currentWorktree = record(rollback?.current_worktree);
  const summary = record(rollback?.summary);
  const statusEntries = records(currentWorktree.status_entries).concat(records(currentWorktree.status_sample));
  const checkpoints = records(rollback?.checkpoints);
  const rollbackReceipts = records(rollback?.rollback_receipts);
  const branch = text(currentWorktree.branch || currentGit.branch || currentGit.current_branch, 'branch pending');
  const dirty = currentWorktree.dirty === true || numberValue(currentGit.scoped_porcelain_count) > 0 || context.fileEdits.length > 0;
  return (
    <div className="ion-codex-ide-drawer-stack">
      <DrawerSection title="source control" value={dirty ? 'dirty' : 'clean'}>
        <div className="ion-codex-ide-drawer-metrics">
          <DrawerMetric label="files" value={summary.current_file_count ?? context.fileEdits.length} />
          <DrawerMetric label="added" value={summary.current_added_lines ?? record(currentWorktree.diff_stats).added_lines ?? 0} />
          <DrawerMetric label="removed" value={summary.current_removed_lines ?? record(currentWorktree.diff_stats).removed_lines ?? 0} />
          <DrawerMetric label="checkpoints" value={summary.checkpoint_count ?? checkpoints.length} />
        </div>
        <DrawerFact label="branch" value={branch} />
        <DrawerFact label="head" value={text(currentWorktree.head || currentGit.head || currentGit.head_sha, 'head pending')} />
      </DrawerSection>

      <DrawerSection title="changes" value={context.fileEdits.length || statusEntries.length}>
        {context.fileEdits.slice(0, 40).map((file, index) => (
          <DrawerRowButton
            key={`${text(file.path || file.file_path, `edit-${index}`)}-${index}`}
            meta={text(file.change_kind || file.status, 'modified')}
            onClick={() => context.setActiveView('diffs')}
            path={text(file.path || file.file_path, '')}
            status={text(file.status || file.change_kind, 'modified')}
            title={shortPath(text(file.path || file.file_path, `edit-${index}`))}
            tone={text(file.status || file.change_kind, 'modified')}
          />
        ))}
        {!context.fileEdits.length ? statusEntries.slice(0, 30).map((entry, index) => (
          <DrawerRowButton
            key={`${text(entry.path || entry.file_path, `status-${index}`)}-${index}`}
            meta={text(entry.xy || entry.status || entry.kind, 'status')}
            path={text(entry.path || entry.file_path || entry.relpath, '')}
            status={text(entry.status || entry.xy || 'changed')}
            title={shortPath(text(entry.path || entry.file_path || entry.relpath, `status-${index}`))}
          />
        )) : null}
        {!context.fileEdits.length && !statusEntries.length ? <div className="ion-codex-ide-empty">NO CURRENT WORKTREE DIFFS</div> : null}
      </DrawerSection>

      <DrawerSection title="checkpoints" value={checkpoints.length}>
        {checkpoints.slice(0, 14).map((checkpoint, index) => (
          <DrawerRowButton
            key={`${text(checkpoint.checkpoint_id || checkpoint.id || checkpoint.path, `checkpoint-${index}`)}-${index}`}
            meta={text(checkpoint.kind || checkpoint.created_at || checkpoint.generated_at, 'checkpoint')}
            path={text(checkpoint.path || checkpoint.receipt_path || checkpoint.diff_path, '')}
            status={text(checkpoint.status || checkpoint.verdict || 'recorded')}
            title={text(checkpoint.label || checkpoint.checkpoint_id || checkpoint.id, `checkpoint ${index + 1}`)}
          />
        ))}
        {!checkpoints.length ? <div className="ion-codex-ide-empty">NO CHECKPOINTS PROJECTED</div> : null}
      </DrawerSection>

      <DrawerSection title="rollback evidence" value={context.archiveDiffEvidence.length + rollbackReceipts.length}>
        {[...context.archiveDiffEvidence, ...rollbackReceipts].slice(0, 18).map((row, index) => (
          <DrawerRowButton
            key={`${text(row.diff_sha256 || row.receipt_path || row.path || row.id, `rollback-${index}`)}-${index}`}
            meta={text(row.change_kind || row.kind || row.verdict, 'rollback evidence')}
            path={text(row.path || row.file_path || row.receipt_path || row.diff_path, '')}
            status={text(row.status || row.verdict || 'recorded')}
            title={shortPath(text(row.path || row.file_path || row.receipt_path || row.diff_sha256, `rollback ${index + 1}`))}
          />
        ))}
      </DrawerSection>
    </div>
  );
}

function renderContextDrawer(context: IdeDrawerContext) {
  const ideWorkbench = record(context.runtime.codex_ide_workbench);
  const ideRegistry = record(ideWorkbench.context_registry);
  const activeBinding = record(ideRegistry.active_binding);
  const latestBridge = record(ideRegistry.latest_bridge);
  const contextSystemRows = records(ideRegistry.context_systems);
  const registryWarnings = records(ideRegistry.warnings);
  const cli = context.runtime.codex_cli_workbench;
  const activeContext = record(cli?.context?.active_context);
  const graph = context.runtime.context_package_graph;
  const graphAuthority = record(graph?.authority);
  const contextPackages = records(context.runtime.docs_projects_packages?.context_packages?.packages);
  const branches = records(graph?.branches);
  const agentControl = context.runtime.agent_control_plane;
  const agents = records(agentControl?.agents);
  const mounts = records(agentControl?.codex_mounts?.mounts);
  const contextAgentRows = agents.filter((agent) => (
    text(agent.active_context_package || agent.context_package_path || agent.context_system_status || agent.context_load_receipt_path, '') !== ''
  ));
  const activeContextPath = text(
    activeContext.minimum_context_path
    || activeContext.path
    || activeContext.capsule_path
    || cli?.context?.witness_policy,
    'active context path not projected',
  );
  return (
    <div className="ion-codex-ide-drawer-stack">
      <DrawerSection title="active chat binding" value={text(ideRegistry.status, 'no registry')}>
        <div className="ion-codex-ide-drawer-metrics">
          <DrawerMetric label="bindings" value={ideRegistry.binding_count ?? 0} />
          <DrawerMetric label="systems" value={ideRegistry.context_system_count ?? contextSystemRows.length} />
          <DrawerMetric label="bridge" value={text(ideRegistry.bridge_status, 'none')} />
          <DrawerMetric label="warnings" value={ideRegistry.warning_count ?? registryWarnings.length} />
        </div>
        <DrawerFact label="binding" value={text(activeBinding.binding_id || ideRegistry.active_binding_id, 'no active chat context binding')} />
        <DrawerFact label="agent" value={text(record(activeBinding.agent_identity).agent_instance_id || activeBinding.owner_agent_id || activeBinding.role_id, 'agent pending')} />
        <DrawerFact label="domain" value={text(activeBinding.domain_id, 'domain pending')} />
        <DrawerFact label="branch" value={text(activeBinding.branch_id || activeBinding.branch_title, 'branch pending')} />
      </DrawerSection>

      <DrawerSection title="ide bridge" value={text(ideRegistry.bridge_status, 'none_mounted')}>
        <div className="ion-codex-ide-drawer-metrics">
          <DrawerMetric label="bridges" value={ideRegistry.bridge_count ?? 0} />
          <DrawerMetric label="artifact" value={truthLabel(ideRegistry.latest_bridge_artifact_present)} />
          <DrawerMetric label="tabs" value={latestBridge.open_tab_count ?? 0} />
          <DrawerMetric label="problems" value={latestBridge.problem_count ?? 0} />
        </div>
        <DrawerFact label="selected" value={text(latestBridge.selected_path, 'no IDE bridge selected path')} />
        <DrawerFact label="artifact" value={text(latestBridge.artifact_ref, 'no bridge artifact mounted')} />
        <DrawerFact label="policy" value="read-only projection / context drawer canonical" />
      </DrawerSection>

      <DrawerSection title="context systems" value={contextSystemRows.length}>
        {contextSystemRows.slice(0, 42).map((row, index) => (
          <DrawerRowButton
            active={row.active === true}
            key={`${text(row.row_id || row.binding_id || row.path, `context-system-${index}`)}-${index}`}
            meta={`${text(row.context_kind, 'context')} / ${text(row.owner_agent_id || row.owner_chat_id || row.system_id, 'owner pending')}`}
            path={text(row.path || row.ide_bridge_artifact_ref || row.binding_id, '')}
            status={text(row.status || row.materialization_state, 'projected')}
            title={text(row.title || row.system_id || row.binding_id, `context system ${index + 1}`)}
            tone={row.active === true ? 'ready' : text(row.status || row.materialization_state, 'info')}
          />
        ))}
        {!contextSystemRows.length ? <div className="ion-codex-ide-empty">NO IDE CONTEXT SYSTEM REGISTRY PROJECTED</div> : null}
      </DrawerSection>

      {registryWarnings.length ? (
        <DrawerSection title="context warnings" value={registryWarnings.length}>
          {registryWarnings.slice(0, 12).map((warning, index) => (
            <DrawerRowButton
              key={`${text(warning.warning_id, `context-warning-${index}`)}-${index}`}
              meta={text(warning.authority_action, 'operator attention')}
              path=""
              status={text(warning.severity, 'warning')}
              title={text(warning.message || warning.warning_id, `warning ${index + 1}`)}
              tone={text(warning.severity, 'warning')}
            />
          ))}
        </DrawerSection>
      ) : null}

      <DrawerSection title="legacy active context projection" value={text(graph?.status || cli?.verdict, 'projection')}>
        <div className="ion-codex-ide-drawer-metrics">
          <DrawerMetric label="packages" value={contextPackages.length || context.runtime.top_bar.context_package_count || 0} />
          <DrawerMetric label="branches" value={graph?.branch_count ?? branches.length} />
          <DrawerMetric label="ready" value={graph?.candidate_review_ready_count ?? context.runtime.top_bar.branch_context_package_ready_count ?? 0} />
          <DrawerMetric label="blocked" value={graph?.blocked_count ?? 0} />
        </div>
        <DrawerFact label="minimum" value={activeContextPath} />
        <DrawerFact label="witness" value={text(cli?.context?.witness_policy, 'witness policy not projected')} />
        <DrawerFact label="accepted state" value={truthLabel(graphAuthority.accepted_state_authority)} />
        <DrawerFact label="live execution" value={truthLabel(graphAuthority.live_execution_authority)} />
      </DrawerSection>

      <DrawerSection title="context package graph" value={branches.length}>
        {branches.slice(0, 20).map((branch, index) => (
          <DrawerRowButton
            key={`${text(branch.path, `branch-${index}`)}-${index}`}
            meta={`${text(branch.package_type, 'package')} / ${text(branch.maturity_level || branch.classification, 'maturity pending')}`}
            path={text(branch.candidate_capsule_path || branch.accepted_capsule_path || branch.readme_projection_candidate || branch.path, '')}
            status={text(branch.promotion_readiness || (branch.candidate_valid ? 'candidate valid' : '') || 'projected')}
            title={shortPath(text(branch.path, `context branch ${index + 1}`))}
            tone={stringList(branch.blockers).length ? 'warning' : text(branch.promotion_readiness, 'info')}
          />
        ))}
        {!branches.length ? <div className="ion-codex-ide-empty">NO CONTEXT GRAPH BRANCHES PROJECTED</div> : null}
      </DrawerSection>

      <DrawerSection title="agent context systems" value={contextAgentRows.length}>
        {contextAgentRows.slice(0, 28).map((agent, index) => (
          <DrawerRowButton
            key={`${text(agent.role_id || agent.agent_id || agent.display_name, `context-agent-${index}`)}-${index}`}
            meta={`${text(agent.registry_primary_domain || agent.domain_id, 'domain pending')} / ${text(agent.backend_carrier_id || agent.carrier_id, 'carrier pending')}`}
            path={text(agent.active_context_package || agent.context_package_path || agent.context_load_receipt_path || agent.mount_receipt_path, '')}
            status={text(agent.context_system_status || agent.roster_status || agent.status, 'context pending')}
            title={text(agent.display_name || agent.role_id || agent.agent_id, `agent ${index + 1}`)}
            tone={text(agent.context_system_status || agent.roster_status || agent.status, 'info')}
          />
        ))}
        {!contextAgentRows.length ? <div className="ion-codex-ide-empty">NO AGENT CONTEXT SYSTEM ROWS PROJECTED</div> : null}
      </DrawerSection>

      <DrawerSection title="codex mounts" value={mounts.length}>
        {mounts.slice(0, 20).map((mount, index) => (
          <DrawerRowButton
            key={`${text(mount.mount_id || mount.agent_id || mount.path, `mount-${index}`)}-${index}`}
            meta={text(mount.agent_id || mount.role_id || mount.carrier_id, 'mount owner pending')}
            path={text(mount.context_package_path || mount.mount_path || mount.path || mount.receipt_path, '')}
            status={text(mount.status || mount.materialized_status || mount.prompt_visibility_status, 'mount projected')}
            title={text(mount.display_name || mount.mount_id || mount.role_id, `mount ${index + 1}`)}
          />
        ))}
        {!mounts.length ? <div className="ion-codex-ide-empty">NO CODEX MOUNTS PROJECTED</div> : null}
      </DrawerSection>

      <DrawerSection title="package definitions" value={contextPackages.length}>
        {contextPackages.slice(0, 16).map((pkg, index) => (
          <DrawerRowButton
            key={`${text(pkg.package_id || pkg.path || pkg.context_type, `pkg-${index}`)}-${index}`}
            meta={text(pkg.context_type || pkg.load_policy, 'context package')}
            path={stringList(pkg.path_refs).join(' / ') || text(pkg.path || pkg.source, '')}
            status={text(pkg.load_policy || pkg.status, 'available')}
            title={text(pkg.package_id || pkg.label || pkg.title, `package ${index + 1}`)}
          />
        ))}
      </DrawerSection>
    </div>
  );
}

function renderDocsDrawer(context: IdeDrawerContext) {
  const docsSummary = context.runtime.docs_projects_packages;
  const packageTypes = Object.entries(record(docsSummary?.context_packages?.package_types));
  const projects = records(docsSummary?.project_favorites);
  const artifactZips = records(docsSummary?.artifact_packages?.latest_zips);
  return (
    <div className="ion-codex-ide-drawer-stack">
      <DrawerSection title="docs and packages" value={context.docsRows.length}>
        <div className="ion-codex-ide-drawer-metrics">
          <DrawerMetric label="docs" value={context.docsRows.length} />
          <DrawerMetric label="projects" value={projects.length} />
          <DrawerMetric label="zips" value={artifactZips.length} />
          <DrawerMetric label="types" value={packageTypes.length} />
        </div>
        <DrawerFact label="context packages" value={text(docsSummary?.context_packages?.path, 'context packages path pending')} />
        <DrawerFact label="artifact root" value={text(docsSummary?.artifact_packages?.root, 'artifact root pending')} />
      </DrawerSection>

      <DrawerSection title="package types" value={packageTypes.length}>
        <div className="ion-codex-ide-drawer-pill-row">
          {packageTypes.map(([label, value]) => <span key={label}>{label}<b>{text(value, '0')}</b></span>)}
          {!packageTypes.length ? <div className="ion-codex-ide-empty">NO PACKAGE TYPE COUNTS PROJECTED</div> : null}
        </div>
      </DrawerSection>

      <DrawerSection title="documents" value={context.docsRows.length}>
        {context.docsRows.slice(0, 36).map((doc, index) => {
          const path = text(doc.path || doc.source || doc.relpath || doc.title, `doc-${index}`);
          return (
            <DrawerRowButton
              key={`${path}-${index}`}
              meta={text(doc.context_type || doc.kind || doc.source, 'doc')}
              onClick={() => {
                context.setSelectedTabId(`doc:${path}`);
                context.setActiveView('docs');
              }}
              path={path}
              status={text(doc.status || doc.load_policy || 'projected')}
              title={text(doc.title || doc.label || shortPath(path), `doc ${index + 1}`)}
            />
          );
        })}
      </DrawerSection>

      <DrawerSection title="project roots" value={projects.length}>
        {projects.map((project, index) => (
          <DrawerRowButton
            key={`${text(project.project_id || project.path, `project-${index}`)}-${index}`}
            meta={text(project.kind || project.context_authority, 'project')}
            path={text(project.path, '')}
            status={project.exists === true ? 'exists' : project.exists === false ? 'missing' : text(project.status, 'projected')}
            title={text(project.label || project.project_id, `project ${index + 1}`)}
            tone={project.exists === false ? 'warning' : 'ready'}
          />
        ))}
      </DrawerSection>

      <DrawerSection title="artifact packages" value={artifactZips.length}>
        {artifactZips.slice(0, 12).map((artifact, index) => (
          <DrawerRowButton
            key={`${text(artifact.path || artifact.zip_path, `artifact-${index}`)}-${index}`}
            meta={text(artifact.kind || artifact.generated_at || artifact.created_at, 'zip')}
            path={text(artifact.path || artifact.zip_path, '')}
            status={text(artifact.status || artifact.verdict || 'visible')}
            title={shortPath(text(artifact.path || artifact.zip_path || artifact.label, `artifact ${index + 1}`))}
          />
        ))}
      </DrawerSection>
    </div>
  );
}

function renderRunsDrawer(context: IdeDrawerContext) {
  const workRequests = records(context.runtime.codex_capsule_chat?.latest_work_requests);
  const agentRuns = records(context.runtime.agent_control_plane?.runs?.recent_invocations);
  const activeRun = record(context.runtime.agent_control_plane?.runs?.active_run);
  const runCount = context.responseRuns.length + context.taskReturns.length + workRequests.length + agentRuns.length + (Object.keys(activeRun).length ? 1 : 0);
  return (
    <div className="ion-codex-ide-drawer-stack">
      <DrawerSection title="runs and queues" value={runCount}>
        <div className="ion-codex-ide-drawer-metrics">
          <DrawerMetric label="responses" value={context.responseRuns.length} />
          <DrawerMetric label="returns" value={context.taskReturns.length} />
          <DrawerMetric label="requests" value={workRequests.length} />
          <DrawerMetric label="agent" value={agentRuns.length} />
        </div>
        <DrawerFact label="latest chat" value={text(context.runtime.codex_capsule_chat?.latest_response_status || context.runtime.codex_capsule_chat?.verdict, 'chat status pending')} />
      </DrawerSection>

      {Object.keys(activeRun).length ? (
        <DrawerSection title="active agent run" value={text(activeRun.status || activeRun.verdict, 'active')}>
          <DrawerRowButton
            meta={text(activeRun.agent_id || activeRun.role_id || activeRun.carrier_id, 'agent pending')}
            path={text(activeRun.path || activeRun.run_path || activeRun.receipt_path, '')}
            status={text(activeRun.status || activeRun.verdict, 'active')}
            title={text(activeRun.run_id || activeRun.id || activeRun.label, 'active run')}
            tone={text(activeRun.status || activeRun.verdict, 'info')}
          />
        </DrawerSection>
      ) : null}

      <DrawerSection title="response runs" value={context.responseRuns.length}>
        {context.responseRuns.slice(0, 20).map((run, index) => (
          <DrawerRowButton
            key={`${text(run.run_id || run.path || run.id, `response-${index}`)}-${index}`}
            meta={text(run.model || run.carrier || run.kind, 'response')}
            path={text(run.path || run.latest_return_path || run.receipt_path, '')}
            status={text(run.status || run.verdict || run.latest_status, 'recorded')}
            title={shortPath(text(run.run_id || run.id || run.name || run.path, `response ${index + 1}`))}
            tone={text(run.status || run.verdict || run.latest_status, 'info')}
          />
        ))}
      </DrawerSection>

      <DrawerSection title="task returns" value={context.taskReturns.length}>
        {context.taskReturns.slice(0, 20).map((row, index) => (
          <DrawerRowButton
            key={`${text(row.id || row.path || row.latest_return_path, `return-${index}`)}-${index}`}
            meta={text(row.role || row.source || row.carrier, 'task return')}
            path={text(row.path || row.latest_return_path || row.receipt_path, '')}
            status={text(row.status || row.verdict || row.decision, 'recorded')}
            title={shortPath(text(row.id || row.path || row.latest_return_path, `return ${index + 1}`))}
            tone={text(row.status || row.verdict || row.decision, 'info')}
          />
        ))}
      </DrawerSection>

      <DrawerSection title="work requests" value={workRequests.length}>
        {workRequests.slice(0, 16).map((request, index) => (
          <DrawerRowButton
            key={`${text(request.request_id || request.id || request.path, `request-${index}`)}-${index}`}
            meta={`${text(request.work_class || request.risk, 'work')} / ${text(request.model || request.route_model, 'model pending')}`}
            path={text(request.path || request.request_path || request.packet_path, '')}
            status={text(request.status || request.state || 'queued')}
            title={text(request.objective || request.title || request.request_id || request.id, `request ${index + 1}`)}
            tone={text(request.status || request.risk, 'info')}
          />
        ))}
      </DrawerSection>
    </div>
  );
}

function renderAgentsDrawer(context: IdeDrawerContext) {
  const agentControl = context.runtime.agent_control_plane;
  const summary = record(agentControl?.summary);
  const starterCapsule = record(agentControl?.starter_capsule);
  const codexMounts = record(agentControl?.codex_mounts);
  const agents = records(agentControl?.agents);
  const domains = records(agentControl?.domains);
  const participants = records(context.runtime.joc_comms?.participants);
  const invocations = records(agentControl?.communications?.invocations).concat(records(agentControl?.runs?.recent_invocations));
  return (
    <div className="ion-codex-ide-drawer-stack">
      <DrawerSection title="agent control plane" value={text(agentControl?.verdict || agentControl?.schema_id, 'projection')}>
        <div className="ion-codex-ide-drawer-metrics">
          <DrawerMetric label="agents" value={summary.agent_count ?? agents.length} />
          <DrawerMetric label="domains" value={summary.domain_count ?? domains.length} />
          <DrawerMetric label="mounts" value={codexMounts.mount_count ?? 0} />
          <DrawerMetric label="comms" value={summary.available_agent_comms_count ?? participants.length} />
        </div>
        <DrawerFact label="active run" value={truthLabel(summary.active_process_running)} />
        <DrawerFact label="starter capsule" value={text(starterCapsule.status || starterCapsule.verdict || starterCapsule.path, 'starter capsule not projected')} />
      </DrawerSection>

      <DrawerSection title="agents" value={agents.length}>
        {agents.slice(0, 40).map((agent, index) => (
          <DrawerRowButton
            key={`${text(agent.role_id || agent.agent_id || agent.display_name, `agent-${index}`)}-${index}`}
            meta={`${text(agent.registry_primary_domain || agent.domain_id, 'domain pending')} / ${text(agent.backend_carrier_id || agent.carrier_id, 'carrier pending')}`}
            path={text(agent.active_context_package || agent.context_package_path || agent.context_load_receipt_path || agent.mount_receipt_path, '')}
            status={text(agent.roster_status || agent.context_system_status || agent.status, 'agent projected')}
            title={text(agent.display_name || agent.role_id || agent.agent_id, `agent ${index + 1}`)}
            tone={text(agent.roster_status || agent.context_system_status || agent.status, 'info')}
          />
        ))}
        {!agents.length ? <div className="ion-codex-ide-empty">NO AGENTS PROJECTED</div> : null}
      </DrawerSection>

      <DrawerSection title="domains" value={domains.length}>
        {domains.slice(0, 30).map((domain, index) => (
          <DrawerRowButton
            key={`${text(domain.domain_id || domain.id || domain.path, `domain-${index}`)}-${index}`}
            meta={text(domain.domain_type || domain.kind || domain.owner_role, 'domain')}
            path={text(domain.path || domain.context_package_path || domain.registry_path, '')}
            status={text(domain.status || domain.maturity || domain.verdict, 'projected')}
            title={text(domain.label || domain.name || domain.domain_id || domain.id, `domain ${index + 1}`)}
          />
        ))}
      </DrawerSection>

      <DrawerSection title="comms participants" value={participants.length}>
        {participants.slice(0, 24).map((participant, index) => (
          <DrawerRowButton
            key={`${text(participant.participant_id || participant.display_name, `participant-${index}`)}-${index}`}
            meta={`${text(participant.participant_kind, 'participant')} / ${text(participant.authority_scope, 'scope pending')}`}
            path={text(participant.context_package_path || participant.mount_receipt_path, '')}
            status={participant.available_for_comms === true ? 'available' : text(participant.status, 'projected')}
            title={text(participant.display_name || participant.participant_id, `participant ${index + 1}`)}
            tone={participant.available_for_comms === true ? 'ready' : text(participant.status, 'info')}
          />
        ))}
      </DrawerSection>

      <DrawerSection title="invocations" value={invocations.length}>
        {invocations.slice(0, 18).map((invocation, index) => (
          <DrawerRowButton
            key={`${text(invocation.invocation_id || invocation.run_id || invocation.path, `invocation-${index}`)}-${index}`}
            meta={text(invocation.agent_id || invocation.role_id || invocation.sender_id, 'agent pending')}
            path={text(invocation.path || invocation.receipt_path || invocation.return_path, '')}
            status={text(invocation.status || invocation.verdict || invocation.state, 'recorded')}
            title={text(invocation.title || invocation.invocation_id || invocation.run_id, `invocation ${index + 1}`)}
            tone={text(invocation.status || invocation.verdict, 'info')}
          />
        ))}
      </DrawerSection>
    </div>
  );
}

function DrawerSection({ children, title, value }: { children: ReactNode; title: string; value: unknown }) {
  return (
    <section className="ion-codex-ide-drawer-section">
      <IdeDrawerHead title={title} value={value} />
      <div>{children}</div>
    </section>
  );
}

function DrawerSearchInput({ onChange, value }: { onChange: (value: string) => void; value: string }) {
  return (
    <label className="ion-codex-ide-drawer-search">
      <span>FILTER PROJECTED INDEX</span>
      <input
        aria-label="Filter IDE drawer index"
        onChange={(event) => onChange(event.currentTarget.value)}
        placeholder="path, role, context, run..."
        spellCheck={false}
        value={value}
      />
    </label>
  );
}

function DrawerMetric({ label, value }: { label: string; value: unknown }) {
  return <div className="ion-codex-ide-drawer-metric"><span>{label}</span><b>{text(value, '0')}</b></div>;
}

function DrawerFact({ label, value }: { label: string; value: unknown }) {
  return <div className="ion-codex-ide-drawer-fact"><span>{label}</span><code>{text(value, 'unmapped')}</code></div>;
}

function DrawerRowButton({
  active = false,
  meta,
  onClick,
  path,
  status,
  title,
  tone,
}: {
  active?: boolean;
  meta: string;
  onClick?: () => void;
  path: string;
  status: string;
  title: string;
  tone?: string;
}) {
  const className = `ion-codex-ide-drawer-row is-${tokenClass(tone || status)}${active ? ' is-active' : ''}`;
  return (
    <button className={className} disabled={!onClick} onClick={onClick} type="button">
      <span className="ion-codex-ide-drawer-row-head"><b>{title}</b><em>{status}</em></span>
      <span>{meta}</span>
      {path ? <code>{path}</code> : null}
    </button>
  );
}

function selectIdeTab(tab: IdeTab, context: IdeDrawerContext) {
  context.setSelectedTabId(tab.id);
  context.setActiveView(viewForTabKind(tab.kind));
}

function selectDrawerSearchRow(row: IdeDrawerSearchRow, context: IdeDrawerContext) {
  if (row.tabId) context.setSelectedTabId(row.tabId);
  if (row.view) context.setActiveView(row.view);
}

function viewForTabKind(kind: IdeTabKind): IdeViewId {
  if (kind === 'doc') return 'docs';
  if (kind === 'media') return 'media';
  if (kind === 'preview') return 'preview';
  if (kind === 'diff') return 'diffs';
  return 'files';
}

function buildWorkspaceTreeRows(context: IdeDrawerContext): IdeDrawerSearchRow[] {
  const rows: IdeDrawerSearchRow[] = [];
  context.tabs.forEach((tab) => rows.push({
    id: `tab:${tab.id}`,
    meta: `open editor / ${tab.kind}`,
    path: tab.path,
    status: tab.status,
    tabId: tab.id,
    title: tab.label,
    view: viewForTabKind(tab.kind),
  }));
  context.fileEdits.forEach((file, index) => {
    const path = text(file.path || file.file_path, `edit-${index}`);
    rows.push({
      id: `edit:${path}:${index}`,
      meta: text(file.change_kind || file.status, 'worktree edit'),
      path,
      status: text(file.status || file.change_kind, 'modified'),
      title: shortPath(path),
      view: 'diffs',
    });
  });
  context.contextSurfaces.forEach((surface, index) => {
    const path = text(surface.path || surface.relpath || surface.ref, `surface-${index}`);
    rows.push({
      id: `surface:${path}:${index}`,
      meta: text(surface.surface_kind || surface.kind || surface.status, 'context surface'),
      path,
      status: text(surface.status || surface.kind, 'context'),
      title: shortPath(path),
      view: 'files',
    });
  });
  context.docsRows.forEach((doc, index) => {
    const path = text(doc.path || doc.source || doc.relpath || doc.title, `doc-${index}`);
    rows.push({
      id: `doc-index:${path}:${index}`,
      meta: text(doc.context_type || doc.kind || doc.source, 'doc'),
      path,
      status: text(doc.status || doc.load_policy, 'doc'),
      title: text(doc.title || doc.label || shortPath(path), `doc ${index + 1}`),
      tabId: `doc:${path}`,
      view: 'docs',
    });
  });
  context.mediaRows.forEach((media, index) => {
    const path = text(media.path || media.src, `media-${index}`);
    rows.push({
      id: `media-index:${path}:${index}`,
      meta: mediaKind(path),
      path,
      status: text(media.status || media.kind || media.source, 'media'),
      title: shortPath(path),
      tabId: `media:${path}`,
      view: 'media',
    });
  });
  return dedupeDrawerRows(rows).slice(0, 140);
}

function buildWorkspaceRootRows(runtime: IonCockpitViewModel): IdeDrawerSearchRow[] {
  const projects = records(runtime.docs_projects_packages?.project_favorites).map((project, index) => ({
    id: `project-root:${text(project.project_id || project.path, `project-${index}`)}`,
    meta: text(project.kind || project.context_authority, 'project root'),
    path: text(project.path, ''),
    status: project.exists === true ? 'exists' : project.exists === false ? 'missing' : text(project.status, 'projected'),
    title: text(project.label || project.project_id, `project ${index + 1}`),
    view: 'files' as IdeViewId,
  }));
  const staticRoots: IdeDrawerSearchRow[] = [
    { id: 'root:kernel', title: 'ION kernel packages', meta: 'python source', path: 'ION/04_packages', status: 'source', view: 'files' },
    { id: 'root:context-current', title: 'current context', meta: 'capsules and receipts', path: 'ION/05_context/current', status: 'context', view: 'files' },
    { id: 'root:joc-cockpit', title: 'JOC cockpit shell', meta: 'React workbench', path: 'ION/08_ui/joc_cockpit_shell', status: 'ui', view: 'files' },
    { id: 'root:tests', title: 'ION tests', meta: 'focused regression', path: 'ION/tests', status: 'tests', view: 'files' },
    { id: 'root:browser-extension', title: 'ChatOps bridge', meta: 'browser extension', path: 'browser_extension/ion_chatops_bridge', status: 'extension', view: 'files' },
  ];
  const sourcePaths = Object.entries(runtime.source_paths || {}).map(([key, path], index) => ({
    id: `source-path:${key}:${index}`,
    meta: 'view model source path',
    path: text(path, ''),
    status: key,
    title: key.replace(/_/g, ' '),
    view: 'files' as IdeViewId,
  }));
  return dedupeDrawerRows([...projects, ...staticRoots, ...sourcePaths]).slice(0, 48);
}

function buildDrawerSearchRows(context: IdeDrawerContext): IdeDrawerSearchRow[] {
  const rows: IdeDrawerSearchRow[] = [
    ...buildWorkspaceRootRows(context.runtime),
    ...buildWorkspaceTreeRows(context),
  ];
  records(context.runtime.context_package_graph?.branches).forEach((branch, index) => {
    const path = text(branch.path || branch.candidate_capsule_path || branch.accepted_capsule_path, `branch-${index}`);
    rows.push({
      id: `context-branch:${path}:${index}`,
      meta: text(branch.package_type || branch.classification, 'context branch'),
      path: text(branch.candidate_capsule_path || branch.accepted_capsule_path || branch.readme_projection_candidate || path, path),
      status: text(branch.promotion_readiness || branch.maturity_level, 'context graph'),
      title: shortPath(path),
      view: 'files',
    });
  });
  records(context.runtime.docs_projects_packages?.context_packages?.packages).forEach((pkg, index) => {
    rows.push({
      id: `context-package:${text(pkg.package_id || pkg.context_type, `pkg-${index}`)}:${index}`,
      meta: text(pkg.context_type || pkg.load_policy, 'context package'),
      path: stringList(pkg.path_refs).join(' / ') || text(pkg.path || pkg.source, ''),
      status: text(pkg.load_policy || pkg.status, 'available'),
      title: text(pkg.package_id || pkg.label || pkg.title, `package ${index + 1}`),
      view: 'files',
    });
  });
  records(context.runtime.agent_control_plane?.agents).forEach((agent, index) => {
    rows.push({
      id: `agent:${text(agent.role_id || agent.agent_id || agent.display_name, `agent-${index}`)}:${index}`,
      meta: text(agent.registry_primary_domain || agent.domain_id || agent.backend_carrier_id, 'agent'),
      path: text(agent.active_context_package || agent.context_package_path || agent.context_load_receipt_path || agent.mount_receipt_path, ''),
      status: text(agent.roster_status || agent.context_system_status || agent.status, 'agent projected'),
      title: text(agent.display_name || agent.role_id || agent.agent_id, `agent ${index + 1}`),
      view: 'files',
    });
  });
  records(context.runtime.agent_control_plane?.domains).forEach((domain, index) => {
    rows.push({
      id: `domain:${text(domain.domain_id || domain.id || domain.path, `domain-${index}`)}:${index}`,
      meta: text(domain.domain_type || domain.kind || domain.owner_role, 'domain'),
      path: text(domain.path || domain.context_package_path || domain.registry_path, ''),
      status: text(domain.status || domain.maturity || domain.verdict, 'domain projected'),
      title: text(domain.label || domain.name || domain.domain_id || domain.id, `domain ${index + 1}`),
      view: 'files',
    });
  });
  [...context.responseRuns, ...context.taskReturns, ...records(context.runtime.codex_capsule_chat?.latest_work_requests)].forEach((run, index) => {
    rows.push({
      id: `run:${text(run.run_id || run.id || run.request_id || run.path, `run-${index}`)}:${index}`,
      meta: text(run.role || run.source || run.work_class || run.kind, 'run'),
      path: text(run.path || run.latest_return_path || run.receipt_path || run.request_path, ''),
      status: text(run.status || run.verdict || run.decision || run.state, 'recorded'),
      title: text(run.objective || run.title || run.run_id || run.id || run.request_id || shortPath(text(run.path, 'run')), `run ${index + 1}`),
      view: 'preview',
    });
  });
  [...context.problemRows, ...context.outputRows, ...context.terminalRows, ...context.portsRows].forEach((row, index) => {
    rows.push({
      id: `runtime-row:${text(row.id || row.path || row.title || row.port, `runtime-${index}`)}:${index}`,
      meta: text(row.source || row.kind || row.process_name || row.label, 'runtime'),
      path: text(row.path || row.evidence || row.url || row.cwd || row.command, ''),
      status: text(row.status || row.severity || row.state || row.verdict, 'projected'),
      title: text(row.title || row.label || row.port || row.id || row.source, `runtime ${index + 1}`),
      view: 'preview',
    });
  });
  return dedupeDrawerRows(rows).slice(0, 260);
}

function filterDrawerRows(rows: IdeDrawerSearchRow[], query: string) {
  const terms = query.toLowerCase().split(/\s+/).map((term) => term.trim()).filter(Boolean);
  if (!terms.length) return rows;
  return rows.filter((row) => {
    const haystack = `${row.title} ${row.meta} ${row.path} ${row.status}`.toLowerCase();
    return terms.every((term) => haystack.includes(term));
  });
}

function dedupeDrawerRows(rows: IdeDrawerSearchRow[]) {
  const seen = new Set<string>();
  return rows.filter((row, index) => {
    const key = `${row.id || index}:${row.path}:${row.title}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function renderDiffWorkspace(fileEdits: Array<Record<string, unknown>>, archiveDiffEvidence: Array<Record<string, unknown>>, selectedFile: Record<string, unknown>) {
  const activePath = text(selectedFile.path || selectedFile.file_path || selectedFile.relpath, text(fileEdits[0]?.path || fileEdits[0]?.file_path, 'no file selected'));
  const diffText = text(
    selectedFile.diff_excerpt
    || selectedFile.diff
    || selectedFile.patch
    || selectedFile.summary
    || archiveDiffEvidence[0]?.diff_excerpt
    || archiveDiffEvidence[0]?.summary,
    'No diff excerpt projected for this file.',
  );
  const diffLines = diffText.split('\n').slice(0, 220);
  return (
    <div className="ion-codex-ide-diff-layout">
      <section className="ion-codex-ide-file-list">
        <header><span>changed files</span><b>{fileEdits.length}</b></header>
        {fileEdits.map((file, index) => (
          <article className={text(file.path || file.file_path, '') === activePath ? 'is-active' : undefined} key={`${text(file.path || file.file_path, `file-${index}`)}-${index}`}>
            <b>{shortPath(text(file.path || file.file_path, `file-${index}`))}</b>
            <span>{text(file.change_kind || file.status, 'modified')}</span>
            <code>{text(file.path || file.file_path, '')}</code>
          </article>
        ))}
        {!fileEdits.length ? <div className="ion-codex-ide-empty">NO CURRENT EDITS PROJECTED</div> : null}
      </section>
      <section className="ion-codex-ide-diff-viewer">
        <header>
          <div><span>diff</span><b>{shortPath(activePath)}</b></div>
          <code>{activePath}</code>
        </header>
        <pre>
          {diffLines.map((line, index) => (
            <span className={diffLineClass(line)} key={`${index}-${line.slice(0, 24)}`}>
              <i>{String(index + 1).padStart(3, '0')}</i>{line || ' '}
            </span>
          ))}
        </pre>
      </section>
    </div>
  );
}

function renderPreviewWorkspace(previewRoute: string, setPreviewRoute: (route: string) => void, previewReady: boolean) {
  return (
    <div className="ion-codex-ide-preview-layout">
      <header className="ion-codex-ide-preview-toolbar">
        <div>
          <span>served preview</span>
          <b>{previewRoute}</b>
        </div>
        <select aria-label="Preview route" onChange={(event) => setPreviewRoute(event.currentTarget.value)} value={previewRoute}>
          {previewRoutes.map((route) => <option key={route.value} value={route.value}>{route.label}</option>)}
        </select>
      </header>
      <div className="ion-codex-ide-preview-shell">
        {previewReady ? <iframe src={previewRoute} title="Cockpit preview" /> : <div className="ion-codex-ide-empty">NO PREVIEW ROUTE</div>}
      </div>
    </div>
  );
}

function renderDocsWorkspace(docsRows: Array<Record<string, unknown>>, selectedTab: IdeTab | null) {
  const selectedDoc = selectedTab?.kind === 'doc'
    ? selectedTab.record ?? docsRows[0] ?? {}
    : docsRows[0] ?? {};
  return (
    <div className="ion-codex-ide-docs-layout">
      <aside className="ion-codex-ide-docs-index">
        <header><span>docs index</span><b>{docsRows.length}</b></header>
        {docsRows.map((doc, index) => (
          <a href={`#ide-doc-${index}`} key={`${text(doc.path || doc.title, `doc-${index}`)}-${index}`}>
            <b>{text(doc.title || doc.label || shortPath(text(doc.path, 'doc')), `Doc ${index + 1}`)}</b>
            <span>{text(doc.path || doc.source, 'workspace doc')}</span>
          </a>
        ))}
      </aside>
      <article className="ion-codex-ide-doc-render">
        <span>workspace doc</span>
        <h2>{text(selectedDoc.title || selectedDoc.label || shortPath(text(selectedDoc.path, 'Documentation')), 'Documentation')}</h2>
        <p>{text(selectedDoc.summary || selectedDoc.detail || selectedDoc.description, 'No rendered summary is projected for this document yet.')}</p>
        <h3>Source</h3>
        <code>{text(selectedDoc.path || selectedDoc.source || selectedDoc.relpath, 'unmapped')}</code>
        <h3>Format</h3>
        <pre>{renderDocSnippet(selectedDoc)}</pre>
      </article>
    </div>
  );
}

function renderMediaWorkspace(mediaRows: Array<Record<string, unknown>>, selectedTab: IdeTab | null) {
  const selectedMedia = selectedTab?.kind === 'media'
    ? selectedTab.record ?? mediaRows[0] ?? {}
    : mediaRows[0] ?? {};
  return (
    <div className="ion-codex-ide-media-layout">
      <section className="ion-codex-ide-media-stage">
        <header><span>media preview</span><b>{shortPath(text(selectedMedia.path || selectedMedia.src, 'no media selected'))}</b></header>
        {renderMediaPreview(selectedMedia)}
      </section>
      <aside className="ion-codex-ide-media-strip">
        {mediaRows.map((row, index) => (
          <article key={`${text(row.path || row.src, `media-${index}`)}-${index}`}>
            {renderMediaPreview(row, true)}
            <b>{shortPath(text(row.path || row.src, `media-${index}`))}</b>
            <span>{text(row.kind || row.status || row.source, 'artifact')}</span>
          </article>
        ))}
        {!mediaRows.length ? <div className="ion-codex-ide-empty">NO MEDIA ARTIFACTS PROJECTED</div> : null}
      </aside>
    </div>
  );
}

function renderFilesWorkspace(contextSurfaces: Array<Record<string, unknown>>, fileEdits: Array<Record<string, unknown>>, selectedFile: Record<string, unknown>) {
  const sourceRows = [...fileEdits, ...contextSurfaces].slice(0, 80);
  return (
    <div className="ion-codex-ide-files-layout">
      <section className="ion-codex-ide-source-outline">
        <header><span>source outline</span><b>{sourceRows.length}</b></header>
        {sourceRows.map((row, index) => (
          <article key={`${text(row.path || row.file_path || row.relpath, `source-${index}`)}-${index}`}>
            <b>{shortPath(text(row.path || row.file_path || row.relpath, `source-${index}`))}</b>
            <span>{text(row.kind || row.status || row.change_kind || row.surface_kind, 'source')}</span>
            <code>{text(row.path || row.file_path || row.relpath, '')}</code>
          </article>
        ))}
      </section>
      <section className="ion-codex-ide-code-viewer">
        <header>
          <div><span>source view</span><b>{shortPath(text(selectedFile.path || selectedFile.file_path || selectedFile.relpath, 'selected source'))}</b></div>
          <code>{text(selectedFile.status || selectedFile.kind || selectedFile.change_kind, 'projected')}</code>
        </header>
        <pre>{text(selectedFile.text_excerpt || selectedFile.excerpt || selectedFile.summary || selectedFile.diff_excerpt, 'No source excerpt projected for this selection.')}</pre>
      </section>
    </div>
  );
}

function renderBottomPanel(id: IdeBottomPanelId, context: {
  chat: IonCockpitViewModel['codex_capsule_chat'];
  cli: IonCockpitViewModel['codex_cli_workbench'];
  outputRows: Array<Record<string, unknown>>;
  portsRows: Array<Record<string, unknown>>;
  problemRows: Array<Record<string, unknown>>;
  runtime: IonCockpitViewModel;
  systemDiagnostics: Record<string, unknown>;
  terminalRows: Array<Record<string, unknown>>;
  timelineRows: Array<Record<string, unknown>>;
}) {
  if (id === 'diagnostics') return renderDiagnosticsPanel(context.runtime, context.systemDiagnostics);
  if (id === 'output') return renderOutputPanel(context.outputRows);
  if (id === 'terminal') return renderTerminalPanel(context.terminalRows, context.runtime, context.cli, context.chat);
  if (id === 'ports') return renderPortsPanel(context.portsRows);
  if (id === 'timeline') return renderTimelinePanel(context.timelineRows);
  return renderProblemsPanel(context.problemRows);
}

function renderProblemsPanel(rows: Array<Record<string, unknown>>) {
  return (
    <div className="ion-codex-ide-bottom-split">
      <section className="ion-codex-ide-bottom-list">
        <header><span>problems</span><b>{rows.length}</b></header>
        {rows.map((row, index) => (
          <article className={`is-${tokenClass(text(row.severity || row.status, 'info'))}`} key={`${text(row.id || row.path || row.title, `problem-${index}`)}-${index}`}>
            <div>
              <b>{text(row.title || row.label || row.status, `problem ${index + 1}`)}</b>
              <span>{text(row.source || row.severity || row.status, 'diagnostic')}</span>
            </div>
            <p>{text(row.detail || row.message || row.summary || row.path, 'No detail projected.')}</p>
            <code>{text(row.path || row.evidence || row.ref, '')}</code>
          </article>
        ))}
        {!rows.length ? <div className="ion-codex-ide-empty is-bottom">NO PROJECTED PROBLEMS</div> : null}
      </section>
      <section className="ion-codex-ide-bottom-inspector">
        <header><span>severity map</span><b>{problemSeveritySummary(rows)}</b></header>
        <div className="ion-codex-ide-bottom-metric-grid">
          <IdeMetric label="error" value={rows.filter((row) => problemSeverity(row) === 'error').length} />
          <IdeMetric label="warning" value={rows.filter((row) => problemSeverity(row) === 'warning').length} />
          <IdeMetric label="blocked" value={rows.filter((row) => problemSeverity(row) === 'blocked').length} />
          <IdeMetric label="info" value={rows.filter((row) => problemSeverity(row) === 'info').length} />
        </div>
      </section>
    </div>
  );
}

function renderDiagnosticsPanel(runtime: IonCockpitViewModel, systemDiagnostics: Record<string, unknown>) {
  const summary = record(systemDiagnostics.summary);
  const authority = record(systemDiagnostics.authority);
  const issues = records(systemDiagnostics.issues);
  const devServers = records(systemDiagnostics.dev_servers);
  const dataQuality = record(systemDiagnostics.data_quality);
  return (
    <div className="ion-codex-ide-bottom-diagnostics">
      <section>
        <header><span>machine diagnostics</span><b>{text(systemDiagnostics.status || runtime.runtime.status, 'ready')}</b></header>
        <div className="ion-codex-ide-bottom-metric-grid is-wide">
          <IdeMetric label="issues" value={summary.issue_count ?? runtime.top_bar.system_issue_count ?? 0} />
          <IdeMetric label="cpu" value={percent(summary.cpu_percent ?? runtime.top_bar.system_cpu_percent)} />
          <IdeMetric label="memory" value={percent(summary.memory_percent ?? runtime.top_bar.system_memory_percent)} />
          <IdeMetric label="swap" value={percent(summary.swap_percent ?? runtime.top_bar.system_swap_percent)} />
          <IdeMetric label="listeners" value={summary.listener_count ?? runtime.top_bar.system_listener_count ?? 0} />
          <IdeMetric label="dev servers" value={summary.active_dev_server_count ?? devServers.length} />
        </div>
      </section>
      <section>
        <header><span>authority</span><b>{authority.live_execution_authority ? 'live' : 'projected'}</b></header>
        <div className="ion-codex-ide-bottom-facts">
          <BottomFact label="accepted state" value={truthLabel(authority.accepted_state_authority)} />
          <BottomFact label="production" value={truthLabel(authority.production_authority)} />
          <BottomFact label="live execution" value={truthLabel(authority.live_execution_authority)} />
          <BottomFact label="protected stops" value={authority.protected_processes_blocked ? 'blocked' : 'unmapped'} />
          <BottomFact label="process source" value={text(dataQuality.process_source, 'ps')} />
          <BottomFact label="port source" value={text(dataQuality.port_source, 'ss')} />
        </div>
      </section>
      <section className="ion-codex-ide-bottom-list is-inline">
        <header><span>diagnostic issues</span><b>{issues.length}</b></header>
        {issues.slice(0, 8).map((issue, index) => (
          <article className={`is-${tokenClass(text(issue.severity, 'info'))}`} key={`${text(issue.id, `issue-${index}`)}-${index}`}>
            <div><b>{text(issue.title, `issue ${index + 1}`)}</b><span>{text(issue.severity, 'info')}</span></div>
            <p>{text(issue.detail, 'No issue detail projected.')}</p>
          </article>
        ))}
        {!issues.length ? <div className="ion-codex-ide-empty is-bottom">NO SYSTEM DIAGNOSTIC ISSUES</div> : null}
      </section>
    </div>
  );
}

function renderOutputPanel(rows: Array<Record<string, unknown>>) {
  return (
    <div className="ion-codex-ide-output-panel">
      <header><span>output stream</span><b>{rows.length}</b></header>
      <pre>
        {rows.map((row, index) => (
          <span className={`is-${tokenClass(text(row.status || row.severity, 'info'))}`} key={`${text(row.id || row.time || row.source, `output-${index}`)}-${index}`}>
            <i>{text(row.time || row.generated_at || row.index, String(index + 1))}</i>
            <b>{text(row.source || row.event_type || row.label, 'output')}</b>
            <em>{text(row.status || row.verdict || row.kind, 'projected')}</em>
            <code>{text(row.detail || row.summary || row.path || row.message, jsonPreview(row))}</code>
          </span>
        ))}
      </pre>
    </div>
  );
}

function renderTerminalPanel(
  rows: Array<Record<string, unknown>>,
  runtime: IonCockpitViewModel,
  cli: IonCockpitViewModel['codex_cli_workbench'],
  chat: IonCockpitViewModel['codex_capsule_chat'],
) {
  return (
    <div className="ion-codex-ide-terminal-panel">
      <header>
        <div><span>projected terminal</span><b>{text(cli?.shell_root || runtime.runtime.shell_root, 'workspace')}</b></div>
        <code>{text(chat?.latest_response_status || cli?.verdict || runtime.runtime.status, 'ready')}</code>
      </header>
      <pre>
        <span><i>$</i><b>pwd</b><code>{text(cli?.shell_root || runtime.runtime.shell_root, 'workspace root pending')}</code></span>
        {rows.map((row, index) => (
          <span className={`is-${tokenClass(text(row.status || row.kind, 'projected'))}`} key={`${text(row.id || row.command || row.path, `terminal-${index}`)}-${index}`}>
            <i>{row.command ? '$' : '>'}</i>
            <b>{text(row.command || row.label || row.source, `event-${index + 1}`)}</b>
            <code>{text(row.output || row.detail || row.status || row.path || row.summary, jsonPreview(row))}</code>
          </span>
        ))}
      </pre>
    </div>
  );
}

function renderPortsPanel(rows: Array<Record<string, unknown>>) {
  return (
    <div className="ion-codex-ide-ports-panel">
      <header><span>ports and services</span><b>{rows.length}</b></header>
      <div className="ion-codex-ide-bottom-table">
        <div className="ion-codex-ide-bottom-table-head">
          <span>port</span><span>service</span><span>workspace</span><span>state</span><span>path</span>
        </div>
        {rows.map((row, index) => (
          <article key={`${text(row.port, `port-${index}`)}-${text(row.pid, 'none')}-${index}`}>
            <b>{text(row.port, 'NA')}</b>
            <span>{text(row.process_name || row.package_name || row.name, 'listener')}</span>
            <span>{text(row.workspace || row.framework, 'workspace')}</span>
            <em>{portState(row)}</em>
            <code>{text(row.url || row.cwd || row.package_path || row.local_address || row.command, '')}</code>
          </article>
        ))}
        {!rows.length ? <div className="ion-codex-ide-empty is-bottom">NO PORT PROJECTION</div> : null}
      </div>
    </div>
  );
}

function renderTimelinePanel(rows: Array<Record<string, unknown>>) {
  return (
    <div className="ion-codex-ide-timeline-panel">
      <header><span>runtime and proof timeline</span><b>{rows.length}</b></header>
      <div>
        {rows.map((row, index) => (
          <article className={`is-${tokenClass(text(row.status || row.verdict, 'info'))}`} key={`${text(row.time || row.path || row.id, `timeline-${index}`)}-${index}`}>
            <time>{text(row.time || row.generated_at || row.created_at, `row ${index + 1}`)}</time>
            <b>{text(row.source || row.event_type || row.name, 'event')}</b>
            <span>{text(row.status || row.verdict || row.phase, 'projected')}</span>
            <p>{text(row.detail || row.path || row.summary || row.message, jsonPreview(row))}</p>
          </article>
        ))}
      </div>
    </div>
  );
}

function buildIdeTabs(
  fileEdits: Array<Record<string, unknown>>,
  contextSurfaces: Array<Record<string, unknown>>,
  docsRows: Array<Record<string, unknown>>,
  mediaRows: Array<Record<string, unknown>>,
): IdeTab[] {
  const fileTabs = fileEdits.slice(0, 8).map((file, index) => {
    const path = text(file.path || file.file_path, `edit-${index}`);
    return {
      id: `diff:${path}`,
      label: shortPath(path),
      path,
      kind: 'diff' as IdeTabKind,
      status: text(file.change_kind || file.status, 'modified'),
      record: file,
    };
  });
  const sourceTabs = contextSurfaces.slice(0, Math.max(0, 8 - fileTabs.length)).map((surface, index) => {
    const path = text(surface.path || surface.relpath || surface.ref, `source-${index}`);
    return {
      id: `source:${path}`,
      label: shortPath(path),
      path,
      kind: 'source' as IdeTabKind,
      status: text(surface.kind || surface.status, 'context'),
      record: surface,
    };
  });
  const docTabs = docsRows.slice(0, 3).map((doc, index) => {
    const path = text(doc.path || doc.source || doc.title, `doc-${index}`);
    return {
      id: `doc:${path}`,
      label: shortPath(text(doc.title || path, `doc-${index}`)),
      path,
      kind: 'doc' as IdeTabKind,
      status: 'doc',
      record: doc,
    };
  });
  const mediaTabs = mediaRows.slice(0, 2).map((media, index) => {
    const path = text(media.path || media.src, `media-${index}`);
    return {
      id: `media:${path}`,
      label: shortPath(path),
      path,
      kind: 'media' as IdeTabKind,
      status: text(media.kind || 'media'),
      record: media,
    };
  });
  const previewTab = {
    id: 'preview:/cockpit#codex',
    label: 'served preview',
    path: '/cockpit#codex',
    kind: 'preview' as IdeTabKind,
    status: 'route',
  };
  return [...fileTabs, ...sourceTabs, ...docTabs, ...mediaTabs, previewTab].slice(0, 14);
}

function buildDocRows(runtime: IonCockpitViewModel): Array<Record<string, unknown>> {
  const docs = records(runtime.docs_projects_packages?.context_packages?.packages)
    .concat(records(runtime.docs_projects_packages?.project_favorites))
    .concat(records(runtime.docs_projects_packages?.artifact_packages?.latest_zips))
    .concat(records(runtime.context_package_graph?.branches))
    .concat(records(runtime.codex_cli_workbench?.project_context?.docs))
    .concat(records(runtime.codex_cli_workbench?.context?.surfaces).filter((row) => {
      const path = text(row.path || row.relpath || row.ref, '').toLowerCase();
      return path.endsWith('.md') || path.endsWith('.mdx') || path.endsWith('.txt') || path.includes('/docs/');
    }));
  return docs.length ? dedupeByPath(docs).slice(0, 32) : [
    {
      title: 'Codex IDE Workbench',
      path: 'ION/08_ui/joc_cockpit_shell/CodexIdeWorkbenchPanel.tsx',
      summary: 'Candidate IDE surface for files, diffs, previews, docs, media, and embedded Codex chat.',
    },
  ];
}

function buildMediaRows(runtime: IonCockpitViewModel): Array<Record<string, unknown>> {
  const candidates = [
    ...records(runtime.receipts),
    ...records(runtime.codex_capsule_chat?.latest_response_runs),
    ...records(runtime.codex_capsule_chat?.latest_task_returns),
    ...records(runtime.codex_git_rollback?.archive_diff_evidence),
  ];
  const media: Array<Record<string, unknown>> = [];
  candidates.forEach((row) => {
    const refs = [
      text(row.path, ''),
      text(row.screenshot_path, ''),
      text(row.preview_path, ''),
      text(row.artifact_path, ''),
      ...stringList(row.artifact_paths),
      ...stringList(row.source_refs),
      ...stringList(row.evidence_refs),
    ].filter(isMediaPath);
    refs.forEach((path) => media.push({ ...row, path, kind: mediaKind(path), source: text(row.status || row.event_type || row.label, 'artifact') }));
  });
  return dedupeByPath(media).slice(0, 36);
}

function buildProblemRows(
  runtime: IonCockpitViewModel,
  fileEdits: Array<Record<string, unknown>>,
  responseRuns: Array<Record<string, unknown>>,
  taskReturns: Array<Record<string, unknown>>,
): Array<Record<string, unknown>> {
  const rows: Array<Record<string, unknown>> = [];
  records(runtime.system_diagnostics?.issues).forEach((issue, index) => {
    rows.push({
      id: text(issue.id, `system-issue-${index}`),
      source: 'system diagnostics',
      severity: text(issue.severity, 'warning'),
      title: text(issue.title, `system issue ${index + 1}`),
      detail: text(issue.detail, 'No system detail projected.'),
      evidence: stringList(issue.evidence).join(' / '),
    });
  });
  if (runtime.runtime.blocked) {
    rows.push({
      id: 'runtime-blocked',
      source: 'runtime',
      severity: 'blocked',
      title: 'runtime blocked',
      detail: text(runtime.runtime.status, 'blocked'),
      evidence: jsonPreview(runtime.runtime.audit_findings),
    });
  }
  const chatStatus = text(runtime.codex_capsule_chat?.latest_response_status, '');
  if (statusLooksProblem(chatStatus)) {
    rows.push({
      id: 'codex-latest-response-status',
      source: 'codex chat',
      severity: problemSeverity({ status: chatStatus }),
      title: chatStatus,
      detail: text(runtime.codex_capsule_chat?.verdict, 'latest response requires attention'),
      path: text(runtime.codex_capsule_chat?.codex_queue_path, ''),
    });
  }
  [...responseRuns, ...taskReturns].forEach((row, index) => {
    const status = text(row.status || row.verdict || row.latest_status || row.error, '');
    const detail = text(row.error || row.message || row.detail || row.summary || row.path || row.latest_return_path, '');
    if (!statusLooksProblem(status) && !statusLooksProblem(detail)) return;
    rows.push({
      id: text(row.run_id || row.id || row.path, `codex-run-problem-${index}`),
      source: text(row.source || row.carrier || row.kind, 'codex run'),
      severity: problemSeverity({ status, detail }),
      title: text(row.title || row.run_id || row.id || status, `codex run ${index + 1}`),
      detail,
      path: text(row.path || row.latest_return_path || row.receipt_path, ''),
    });
  });
  fileEdits.forEach((file, index) => {
    const status = text(file.status || file.change_kind, '');
    if (!statusLooksProblem(status)) return;
    rows.push({
      id: text(file.path || file.file_path, `file-problem-${index}`),
      source: 'worktree',
      severity: problemSeverity({ status }),
      title: shortPath(text(file.path || file.file_path, `file ${index + 1}`)),
      detail: text(file.summary || file.detail || status, 'worktree state projected'),
      path: text(file.path || file.file_path, ''),
    });
  });
  return dedupeByPath(rows).slice(0, 96);
}

function buildOutputRows(
  runtime: IonCockpitViewModel,
  responseRuns: Array<Record<string, unknown>>,
  taskReturns: Array<Record<string, unknown>>,
): Array<Record<string, unknown>> {
  const rows: Array<Record<string, unknown>> = [];
  records(runtime.timeline).forEach((event, index) => {
    rows.push({
      ...event,
      id: `timeline-output-${index}`,
      source: text(event.source, 'runtime'),
      status: text(event.status, 'projected'),
      detail: text(event.detail || event.path, 'runtime event'),
      index,
    });
  });
  responseRuns.slice(0, 24).forEach((run, index) => {
    rows.push({
      ...run,
      id: text(run.run_id || run.id || run.path, `response-run-${index}`),
      source: 'response run',
      status: text(run.status || run.verdict || run.latest_status, 'recorded'),
      detail: text(run.summary || run.detail || run.path || run.error, jsonPreview(run)),
      index: rows.length + 1,
    });
  });
  taskReturns.slice(0, 24).forEach((taskReturn, index) => {
    rows.push({
      ...taskReturn,
      id: text(taskReturn.id || taskReturn.path || taskReturn.latest_return_path, `task-return-${index}`),
      source: 'task return',
      status: text(taskReturn.status || taskReturn.verdict, 'recorded'),
      detail: text(taskReturn.summary || taskReturn.detail || taskReturn.path || taskReturn.latest_return_path, jsonPreview(taskReturn)),
      index: rows.length + 1,
    });
  });
  records(runtime.codex_capsule_chat?.latest_work_requests).slice(0, 18).forEach((request, index) => {
    rows.push({
      ...request,
      id: text(request.request_id || request.id || request.path, `work-request-${index}`),
      source: 'work request',
      status: text(request.status || request.work_class || request.risk, 'queued'),
      detail: text(request.objective || request.summary || request.path, jsonPreview(request)),
      index: rows.length + 1,
    });
  });
  return rows.slice(0, 120);
}

function buildTerminalRows(
  runtime: IonCockpitViewModel,
  responseRuns: Array<Record<string, unknown>>,
  taskReturns: Array<Record<string, unknown>>,
): Array<Record<string, unknown>> {
  const chat = runtime.codex_capsule_chat;
  const cli = runtime.codex_cli_workbench;
  const rawCli = record(chat?.raw_codex_cli);
  const settings = record(cli?.settings);
  const rows: Array<Record<string, unknown>> = [
    {
      id: 'codex-cli-status',
      label: 'codex cli status',
      status: text(rawCli.latest_status || chat?.latest_response_status || cli?.verdict || runtime.top_bar.codex_cli_workbench_verdict, 'ready'),
      detail: text(rawCli.latest_error || rawCli.error || cli?.verdict || runtime.top_bar.codex_cli_workbench_verdict, 'codex cli projection ready'),
    },
    {
      id: 'model-route',
      label: 'model route',
      status: text(record(chat?.model_moves).status || record(chat?.response_carrier).status || 'projected', 'projected'),
      detail: text(record(chat?.response_carrier).model || record(chat?.model_moves).model || settings.default_model || 'model route pending'),
    },
    {
      id: 'context-witness',
      label: 'context witness',
      status: text(cli?.context?.witness_policy, 'capsule witness'),
      detail: text(cli?.content_root || cli?.shell_root || runtime.runtime.shell_root, 'content root pending'),
    },
  ];
  responseRuns.slice(0, 16).forEach((run, index) => {
    rows.push({
      id: text(run.run_id || run.id || run.path, `terminal-response-${index}`),
      command: text(run.command || run.prompt || run.run_id || 'codex response run', 'codex response run'),
      status: text(run.status || run.verdict || run.latest_status, 'recorded'),
      output: text(run.output || run.summary || run.detail || run.error || run.path, jsonPreview(run)),
    });
  });
  taskReturns.slice(0, 16).forEach((row, index) => {
    rows.push({
      id: text(row.id || row.path || row.latest_return_path, `terminal-return-${index}`),
      command: text(row.command || row.request_id || 'task return', 'task return'),
      status: text(row.status || row.verdict, 'recorded'),
      output: text(row.output || row.summary || row.detail || row.path || row.latest_return_path, jsonPreview(row)),
    });
  });
  return rows;
}

function buildPortRows(runtime: IonCockpitViewModel): Array<Record<string, unknown>> {
  const rows: Array<Record<string, unknown>> = [];
  records(runtime.system_diagnostics?.dev_servers).forEach((server) => {
    rows.push({
      ...server,
      source: 'dev server',
      url: text(record(server.http_probe).url, ''),
      state: record(server.http_probe).serves_http ? 'http verified' : server.protected ? 'protected' : server.cleanup_candidate ? 'cleanup candidate' : 'listener',
    });
  });
  records(runtime.system_diagnostics?.ports).forEach((port) => {
    rows.push({
      ...port,
      source: 'port',
      state: port.dev_server ? 'dev server' : port.protected ? 'protected' : port.cleanup_candidate ? 'cleanup candidate' : 'listener',
    });
  });
  const seen = new Set<string>();
  return rows.filter((row, index) => {
    const key = `${text(row.port, `port-${index}`)}:${text(row.pid, 'none')}:${text(row.source, 'source')}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  }).slice(0, 96);
}

function buildTimelineRows(runtime: IonCockpitViewModel): Array<Record<string, unknown>> {
  return [
    ...records(runtime.timeline),
    ...records(runtime.lane_timeline?.events),
    ...records(runtime.receipt_hydration?.records),
    ...records(runtime.receipts),
  ].slice(0, 140);
}

function renderMediaPreview(row: Record<string, unknown>, thumb = false) {
  const path = text(row.path || row.src, '');
  if (isLoadableImagePath(path)) {
    return <img alt={shortPath(path)} src={path} />;
  }
  return (
    <div className={`ion-codex-ide-media-placeholder${thumb ? ' is-thumb' : ''}`}>
      <EvidenceIcon />
      <span>{mediaKind(path)}</span>
      <code>{path || 'media path pending'}</code>
    </div>
  );
}

function renderDocSnippet(doc: Record<string, unknown>) {
  const lines = [
    `# ${text(doc.title || doc.label || shortPath(text(doc.path, 'Document')), 'Document')}`,
    '',
    text(doc.summary || doc.detail || doc.description, 'Summary unavailable.'),
    '',
    '```text',
    text(doc.path || doc.source || doc.relpath, 'unmapped source'),
    '```',
  ];
  return lines.join('\n');
}

function IdeMetric({ label, value }: { label: string; value: unknown }) {
  return <div className="ion-codex-ide-metric"><span>{label}</span><b>{text(value, '0')}</b></div>;
}

function BottomFact({ label, value }: { label: string; value: unknown }) {
  return <div className="ion-codex-ide-bottom-fact"><span>{label}</span><b>{text(value, 'unknown')}</b></div>;
}

function IdeDrawerHead({ title, value }: { title: string; value: unknown }) {
  return <header className="ion-codex-ide-drawer-section-head"><span>{title}</span><b>{text(value, '0')}</b></header>;
}

function diffLineClass(line: string) {
  if (line.startsWith('+')) return 'is-add';
  if (line.startsWith('-')) return 'is-remove';
  if (line.startsWith('@@')) return 'is-hunk';
  return 'is-context';
}

function record(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' && !Array.isArray(value) ? value as Record<string, unknown> : {};
}

function records(value: unknown): Array<Record<string, unknown>> {
  if (!Array.isArray(value)) return [];
  return value.map((item) => record(item)).filter((item) => Object.keys(item).length > 0);
}

function text(value: unknown, fallback = 'unknown'): string {
  if (typeof value === 'string' && value.trim()) return value.trim();
  if (typeof value === 'number' || typeof value === 'boolean') return String(value);
  return fallback;
}

function numberValue(value: unknown): number {
  if (typeof value === 'number' && Number.isFinite(value)) return value;
  if (typeof value === 'string') {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : 0;
  }
  return 0;
}

function clampNumber(value: number, min: number, max: number) {
  if (max < min) return min;
  return Math.min(Math.max(value, min), max);
}

function shortPath(path: string) {
  const clean = path.replace(/^\/home\/sev\/ION - Production\/ION_Developement\//, '');
  const parts = clean.split('/').filter(Boolean);
  return parts.length > 2 ? `${parts.at(-2)}/${parts.at(-1)}` : clean || 'workspace';
}

function stringList(value: unknown): string[] {
  if (!Array.isArray(value)) return [];
  return value.map((item) => text(item, '')).filter(Boolean);
}

function isMediaPath(path: string) {
  return /\.(png|jpe?g|gif|webp|svg|mp4|webm|mov|pdf)$/i.test(path);
}

function isLoadableImagePath(path: string) {
  return /^(https?:|\/)/.test(path) && /\.(png|jpe?g|gif|webp|svg)$/i.test(path);
}

function mediaKind(path: string) {
  const ext = path.split('.').pop()?.toLowerCase() || 'artifact';
  if (['png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'].includes(ext)) return 'image';
  if (['mp4', 'webm', 'mov'].includes(ext)) return 'video';
  if (ext === 'pdf') return 'pdf';
  return ext;
}

function statusLooksProblem(value: string) {
  const lower = value.toLowerCase();
  return ['error', 'fail', 'timeout', 'blocked', 'unsupported', 'rejected', 'missing', 'degraded', 'attention', 'stale', 'invalid'].some((token) => lower.includes(token));
}

function problemSeverity(row: Record<string, unknown>) {
  const lower = `${text(row.severity, '')} ${text(row.status, '')} ${text(row.detail, '')}`.toLowerCase();
  if (lower.includes('blocked') || lower.includes('rejected')) return 'blocked';
  if (lower.includes('error') || lower.includes('fail') || lower.includes('timeout') || lower.includes('invalid') || lower.includes('unsupported')) return 'error';
  if (lower.includes('warn') || lower.includes('attention') || lower.includes('degraded') || lower.includes('stale') || lower.includes('missing')) return 'warning';
  return 'info';
}

function problemSeveritySummary(rows: Array<Record<string, unknown>>) {
  const error = rows.filter((row) => problemSeverity(row) === 'error').length;
  const warning = rows.filter((row) => problemSeverity(row) === 'warning').length;
  const blocked = rows.filter((row) => problemSeverity(row) === 'blocked').length;
  return `${error}E / ${warning}W / ${blocked}B`;
}

function percent(value: unknown) {
  const parsed = numberValue(value);
  return parsed ? `${Math.round(parsed)}%` : '0%';
}

function truthLabel(value: unknown) {
  return value === true ? 'true' : value === false ? 'false' : 'unmapped';
}

function tokenClass(value: string) {
  const lower = value.toLowerCase().replace(/[^a-z0-9_-]+/g, '-').replace(/^-+|-+$/g, '');
  if (!lower) return 'info';
  if (lower.includes('blocked') || lower.includes('rejected')) return 'blocked';
  if (lower.includes('error') || lower.includes('fail') || lower.includes('timeout') || lower.includes('invalid') || lower.includes('unsupported')) return 'error';
  if (lower.includes('warn') || lower.includes('attention') || lower.includes('degraded') || lower.includes('stale') || lower.includes('missing')) return 'warning';
  if (lower.includes('ready') || lower.includes('ok') || lower.includes('verified') || lower.includes('complete') || lower.includes('pass')) return 'ready';
  return lower.slice(0, 32);
}

function portState(row: Record<string, unknown>) {
  return text(row.state || (row.dev_server ? 'dev server' : row.protected ? 'protected' : row.cleanup_candidate ? 'cleanup candidate' : 'listener'), 'listener');
}

function jsonPreview(value: unknown) {
  if (typeof value === 'string') return value;
  try {
    const json = JSON.stringify(value);
    return json.length > 360 ? `${json.slice(0, 360)}...` : json;
  } catch {
    return 'unserializable projection';
  }
}

function dedupeByPath(rows: Array<Record<string, unknown>>) {
  const seen = new Set<string>();
  return rows.filter((row, index) => {
    const key = text(row.path || row.file_path || row.relpath || row.source || row.title, `row-${index}`);
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}
