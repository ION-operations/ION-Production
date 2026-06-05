import { useEffect, useMemo, useRef, useState } from 'react';
import type {
  IonCockpitViewModel,
  IonProjectCockpitProject,
  IonProjectLauncherRecord,
  IonProjectPortfolioFamily,
  IonProjectPortfolioVersion,
  IonProjectPreviewComparison,
  IonProjectPreviewSession,
} from './ionRuntimeCockpitTypes';

type AppPreviewRow = {
  key: string;
  label: string;
  source: 'portfolio' | 'project' | 'launcher';
  domainLabel?: string;
  family?: IonProjectPortfolioFamily;
  version?: IonProjectPortfolioVersion;
  project?: IonProjectCockpitProject;
  launchId?: string;
  launchable: boolean;
  path?: string;
  framework?: string;
  status?: string;
  runtimeState?: string;
  previewHref?: string;
  launcherUrl?: string;
  catalogUrl?: string;
};

type FilterId = 'launchable' | 'running' | 'all';
type DiagnosticsTimelineModel = {
  ok?: boolean;
  config?: Record<string, unknown>;
  summary?: Record<string, unknown>;
  lanes?: Array<Record<string, unknown>>;
  source_health?: Array<Record<string, unknown>>;
  event_type_registry?: Array<Record<string, unknown>>;
  events?: Array<Record<string, unknown>>;
  paths?: Record<string, unknown>;
};

type DiagnosticsMatrixRun = {
  app_id?: string;
  ok?: boolean;
  launch_id?: string;
  timeline_event_count?: number;
  coverage?: Record<string, boolean>;
  expected_coverage?: string[];
  expected_coverage_met?: boolean;
  screenshot_href?: string;
  screenshot_path?: string;
  stop_ok?: boolean | null;
};

type DiagnosticsMatrixResult = {
  ok?: boolean;
  matrix_id?: string;
  mode?: string;
  receipt_path?: string;
  snapshot_path?: string;
  snapshot_receipt_path?: string;
  coverage?: Record<string, unknown>;
  runs?: DiagnosticsMatrixRun[];
  finding?: string;
  error?: string;
};

export function HelixionAppsPreviewPanel({ runtime, onRuntimeRefresh }: { runtime: IonCockpitViewModel; onRuntimeRefresh?: () => void }) {
  const projectCockpit = runtime.project_cockpit;
  const portfolio = projectCockpit?.portfolio;
  const previewSessionModel = projectCockpit?.preview_sessions;
  const previewSessions = previewSessionModel?.sessions ?? [];
  const previewComparisons = previewSessionModel?.comparisons ?? [];
  const localLaunchConfirmation = projectCockpit?.local_launch_confirmation ?? projectCockpit?.launcher?.confirmation ?? 'ION_PROJECT_LOCAL_LAUNCH_CONFIRMED';
  const [projectLaunchRecords, setProjectLaunchRecords] = useState<IonProjectLauncherRecord[]>([]);
  const [launchBusyKey, setLaunchBusyKey] = useState('');
  const [launchDiagnostics, setLaunchDiagnostics] = useState<Record<string, Record<string, unknown>>>({});
  const [selectedKey, setSelectedKey] = useState('');
  const [query, setQuery] = useState('');
  const [filter, setFilter] = useState<FilterId>('launchable');
  const [actionMessage, setActionMessage] = useState('');
  const [diagnosticsTimeline, setDiagnosticsTimeline] = useState<DiagnosticsTimelineModel | undefined>();
  const [diagnosticsBusy, setDiagnosticsBusy] = useState('');
  const [diagnosticsMatrixBusy, setDiagnosticsMatrixBusy] = useState('');
  const [diagnosticsMatrixResult, setDiagnosticsMatrixResult] = useState<DiagnosticsMatrixResult | undefined>();
  const diagnosticsRequestId = useRef(0);

  useEffect(() => {
    setProjectLaunchRecords(projectCockpit?.launcher?.launches ?? []);
  }, [projectCockpit?.launcher?.generated_at, projectCockpit?.launcher?.launch_count]);

  const launchRecords = useMemo(
    () => mergeLaunchRecords(projectCockpit?.launcher?.launches ?? [], projectLaunchRecords),
    [projectCockpit?.launcher?.launches, projectLaunchRecords],
  );
  const catalogAppRows = useMemo(() => buildAppRows(projectCockpit?.projects ?? [], portfolio?.families ?? []), [portfolio?.families, projectCockpit?.projects]);
  const appRows = useMemo(() => mergeLauncherRows(catalogAppRows, launchRecords), [catalogAppRows, launchRecords]);
  const runningPathSet = useMemo(() => new Set(launchRecords.filter((record) => isManagedLaunchRunning(record) && record.path).map((record) => record.path as string)), [launchRecords]);
  const visibleApps = useMemo(() => {
    const needle = query.trim().toLowerCase();
    return appRows.filter((app) => {
      if (filter === 'launchable' && !app.launchable && !app.launcherUrl && !app.previewHref && app.source !== 'launcher') return false;
      if (filter === 'running' && (!app.path || !runningPathSet.has(app.path))) return false;
      if (!needle) return true;
      return [app.label, app.domainLabel, app.family?.family_id, app.version?.version_id, app.project?.project_id, app.launchId, app.path, app.framework, app.status, app.runtimeState]
        .join(' ')
        .toLowerCase()
        .includes(needle);
    });
  }, [appRows, filter, query, runningPathSet]);

  const selectedApp = visibleApps.find((app) => app.key === selectedKey) ?? visibleApps[0] ?? appRows[0];
  const selectedRecord = launchRecordForApp(selectedApp, launchRecords);
  const selectedPreviewSession = previewSessionForApp(selectedApp, previewSessions, selectedRecord);
  const selectedComparison = comparisonForSession(selectedPreviewSession, previewComparisons);
  const runningCount = launchRecords.filter((record) => isManagedLaunchRunning(record)).length;
  const detachedCount = launchRecords.filter((record) => record.detached).length;
  const launchableCount = appRows.filter((app) => app.launchable || app.launcherUrl || app.previewHref).length;
  const previewSessionSummary = previewSessionModel?.summary ?? {};

  useEffect(() => {
    if (!selectedKey && selectedApp?.key) setSelectedKey(selectedApp.key);
  }, [selectedApp?.key, selectedKey]);

  useEffect(() => {
    refreshDiagnosticsTimeline(selectedRecord?.launch_id);
  }, [selectedRecord?.launch_id]);

  function upsertProjectLaunch(record: IonProjectLauncherRecord | undefined) {
    if (!record?.launch_id) return;
    setProjectLaunchRecords((current) => {
      const next = current.filter((item) => item.launch_id !== record.launch_id);
      return [record, ...next].slice(0, 32);
    });
  }

  async function refreshDiagnosticsTimeline(launchId = selectedRecord?.launch_id) {
    const requestId = diagnosticsRequestId.current + 1;
    diagnosticsRequestId.current = requestId;
    setDiagnosticsBusy('timeline');
    try {
      const response = await fetch('/cockpit/projects/launch/diagnostics/timeline', {
        method: 'POST',
        headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
        body: JSON.stringify({ launch_id: launchId ?? '', limit: 900 }),
      });
      const result = await response.json();
      if (requestId === diagnosticsRequestId.current) setDiagnosticsTimeline(result);
    } catch (error) {
      if (requestId === diagnosticsRequestId.current) setDiagnosticsTimeline({ ok: false, summary: { finding: error instanceof Error ? error.message : 'timeline failed' }, events: [] });
    } finally {
      if (requestId === diagnosticsRequestId.current) setDiagnosticsBusy('');
    }
  }

  async function setDiagnosticsMode(mode: string, enabled: boolean) {
    setDiagnosticsBusy(`mode:${mode}`);
    setActionMessage('');
    try {
      const response = await fetch('/cockpit/projects/launch/diagnostics/config', {
        method: 'POST',
        headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
        body: JSON.stringify({ confirmation: 'ION_APP_DIAGNOSTICS_CONFIG_CONFIRMED', mode, enabled }),
      });
      const result = await response.json();
      if (!response.ok || !result.ok) {
        setActionMessage(String(result.finding ?? result.error ?? 'diagnostics config failed'));
        return;
      }
      setActionMessage(`diagnostics mode: ${mode}`);
      await refreshDiagnosticsTimeline(selectedRecord?.launch_id);
    } catch (error) {
      setActionMessage(error instanceof Error ? error.message : 'diagnostics config failed');
    } finally {
      setDiagnosticsBusy('');
    }
  }

  async function runDiagnosticsMatrix(mode: 'standard' | 'forensic' | 'exhaustive') {
    setDiagnosticsMatrixBusy(mode);
    setDiagnosticsMatrixResult(undefined);
    setActionMessage('');
    try {
      const response = await fetch('/cockpit/projects/launch/diagnostics/matrix', {
        method: 'POST',
        headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
        body: JSON.stringify({
          confirmation: 'ION_APP_DIAGNOSTICS_MATRIX_CONFIRMED',
          mode,
          include_framework: true,
          stop_after: true,
          timeout_seconds: mode === 'exhaustive' ? 70 : 45,
          base_url: typeof window !== 'undefined' ? window.location.origin : 'http://127.0.0.1:8765',
        }),
      });
      const result = await response.json();
      setDiagnosticsMatrixResult(result);
      if (!response.ok || !result.ok) {
        setActionMessage(String(result.finding ?? result.error ?? 'diagnostics matrix failed'));
      } else {
        setActionMessage(`diagnostics matrix ${mode}: ${String(result.coverage?.passed_count ?? 0)}/${String(result.coverage?.run_count ?? 0)} passed`);
      }
      await refreshDiagnosticsTimeline(selectedRecord?.launch_id);
      onRuntimeRefresh?.();
    } catch (error) {
      setDiagnosticsMatrixResult({ ok: false, finding: error instanceof Error ? error.message : 'diagnostics matrix failed' });
      setActionMessage(error instanceof Error ? error.message : 'diagnostics matrix failed');
    } finally {
      setDiagnosticsMatrixBusy('');
    }
  }

  async function startApp(app: AppPreviewRow | undefined) {
    if (!app?.version) {
      setActionMessage('launch unavailable: select a managed portfolio app version');
      return;
    }
    const launch = app.version.launch ?? {};
    const launchPath = launch.project_path ?? app.version.path ?? app.path;
    if (!launchPath) {
      setActionMessage('launch failed: path missing');
      return;
    }
    let openedWindow: Window | null = null;
    if (typeof window !== 'undefined') openedWindow = window.open('about:blank', '_blank');
    setLaunchBusyKey(app.key);
    setActionMessage('');
    try {
      const response = await fetch(launch.action_path ?? '/cockpit/projects/launch/start', {
        method: 'POST',
        headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
        body: JSON.stringify({
          confirmation: localLaunchConfirmation,
          path: launchPath,
          project_id: launch.project_id ?? app.version.project_id ?? app.family?.family_id,
          version_id: launch.version_id ?? app.version.version_id ?? versionKey(app.version),
          label: launch.label ?? app.version.display_label ?? app.version.label ?? app.label,
          install_repair: launch.install_repair_on_launch !== false,
        }),
      });
      const result = await response.json();
      if (!response.ok || !result.ok) {
        openedWindow?.close();
        setActionMessage(String(result.finding ?? result.error ?? 'project launch failed'));
        return;
      }
      const launchRecord = result.launch as IonProjectLauncherRecord;
      upsertProjectLaunch(launchRecord);
      refreshDiagnosticsTimeline(launchRecord?.launch_id);
      const openHref = String(result.open_href ?? result.launch?.open_href ?? result.url ?? '');
      if (openHref) {
        if (openedWindow) openedWindow.location.href = openHref;
        else if (typeof window !== 'undefined') window.open(openHref, '_blank', 'noopener,noreferrer');
      } else {
        openedWindow?.close();
      }
      setActionMessage(result.reused ? 'existing app preview opened' : 'managed app preview started');
      onRuntimeRefresh?.();
    } catch (error) {
      openedWindow?.close();
      setActionMessage(error instanceof Error ? error.message : 'project launch failed');
    } finally {
      setLaunchBusyKey('');
    }
  }

  async function stopLaunch(record: IonProjectLauncherRecord | undefined) {
    if (!record?.launch_id) {
      setActionMessage('stop unavailable: no launch record selected');
      return;
    }
    setLaunchBusyKey(record.launch_id);
    setActionMessage('');
    try {
      const response = await fetch(record.stop_path ?? '/cockpit/projects/launch/stop', {
        method: 'POST',
        headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
        body: JSON.stringify({ confirmation: localLaunchConfirmation, launch_id: record.launch_id }),
      });
      const result = await response.json();
      if (!response.ok || !result.ok) {
        setActionMessage(String(result.finding ?? result.error ?? 'project stop failed'));
        return;
      }
      const launchRecord = result.launch as IonProjectLauncherRecord;
      upsertProjectLaunch(launchRecord);
      refreshDiagnosticsTimeline(launchRecord?.launch_id);
      setActionMessage('managed app preview stopped');
      onRuntimeRefresh?.();
    } catch (error) {
      setActionMessage(error instanceof Error ? error.message : 'project stop failed');
    } finally {
      setLaunchBusyKey('');
    }
  }

  async function captureDiagnostics(record: IonProjectLauncherRecord | undefined) {
    if (!record?.launch_id) {
      setActionMessage('diagnostics unavailable: no launch record selected');
      return;
    }
    setLaunchBusyKey(`diagnostics:${record.launch_id}`);
    setActionMessage('');
    try {
      const response = await fetch(record.diagnostics_path ?? '/cockpit/projects/launch/diagnostics', {
        method: 'POST',
        headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
        body: JSON.stringify({ confirmation: localLaunchConfirmation, launch_id: record.launch_id, capture: true, width: 1365, height: 900 }),
      });
      const result = await response.json();
      if (result.launch) upsertProjectLaunch(result.launch as IonProjectLauncherRecord);
      setLaunchDiagnostics((current) => ({ ...current, [record.launch_id as string]: result }));
      if (!response.ok || !result.ok) {
        setActionMessage(String(result.finding ?? result.error ?? 'diagnostics failed'));
        return;
      }
      setActionMessage('app preview diagnostics captured');
      refreshDiagnosticsTimeline(record.launch_id);
      onRuntimeRefresh?.();
    } catch (error) {
      setActionMessage(error instanceof Error ? error.message : 'diagnostics failed');
    } finally {
      setLaunchBusyKey('');
    }
  }

  if (!projectCockpit) {
    return (
      <section className="ion-panel ion-app-preview-page">
        <div className="ion-section-title">HELIXION APP PREVIEWS</div>
        <div className="ion-empty-state">PROJECT COCKPIT MODEL MISSING</div>
      </section>
    );
  }

  return (
    <section className="ion-panel ion-app-preview-page">
      <div className="ion-app-preview-hero">
        <div>
          <div className="ion-section-title">HELIXION APP PREVIEWS</div>
          <h2>Local app launch and preview control</h2>
          <p>Pick a discovered app, start a managed local preview, open the generated preview window, stop the server, or capture diagnostics. This uses the existing project launcher lane.</p>
        </div>
        <div className="ion-runtime-grid compact">
          <Metric label="apps" value={String(appRows.length)} />
          <Metric label="launchable" value={String(launchableCount)} />
          <Metric label="running" value={String(runningCount)} />
          <Metric label="detached" value={String(previewSessionSummary.detached_count ?? detachedCount)} />
          <Metric label="sessions" value={String(previewSessionSummary.session_count ?? previewSessions.length)} />
          <Metric label="pairs" value={String(previewSessionSummary.comparison_count ?? previewSessionModel?.comparisons?.length ?? 0)} />
          <Metric label="observe" value={String(previewSessionSummary.ai_observe_target_count ?? previewSessionModel?.ai_observe_preview?.target_count ?? 0)} />
          <Metric label="providers" value={String(previewSessionSummary.provider_count ?? previewSessionModel?.providers?.length ?? 0)} />
        </div>
      </div>

      <div className="ion-app-preview-toolbar">
        <input aria-label="Search app previews" onChange={(event) => setQuery(event.target.value)} placeholder="Search apps, domains, paths..." value={query} />
        <div className="ion-app-preview-filters" role="tablist" aria-label="App preview filters">
          {(['launchable', 'running', 'all'] as FilterId[]).map((id) => (
            <button className={filter === id ? 'is-active' : undefined} key={id} onClick={() => setFilter(id)} type="button">{id}</button>
          ))}
        </div>
      </div>

      <div className="ion-app-preview-layout">
        <div className="ion-app-preview-list" aria-label="Available apps">
          {visibleApps.map((app) => {
            const record = launchRecordForApp(app, launchRecords);
            const previewSession = previewSessionForApp(app, previewSessions, record);
            const active = selectedApp?.key === app.key;
            const runtimeClass = launcherRuntimeClass(record, previewSession);
            const tone = runtimeClass === 'running' ? 'running' : runtimeClass === 'orphaned' ? 'orphaned' : ['detached', 'stale'].includes(runtimeClass) ? 'stale' : app.launchable ? 'ready' : 'watch';
            return (
              <button className={`ion-app-preview-row is-${safeClassToken(tone, 'watch')}${active ? ' is-active' : ''}`} key={app.key} onClick={() => setSelectedKey(app.key)} type="button">
                <span>{runtimeClass === 'registered' || runtimeClass === 'ready' ? app.framework ?? app.source : runtimeClass.toUpperCase()}</span>
                <b>{app.label}</b>
                <small>{previewSession?.provider_id ?? app.domainLabel ?? app.family?.family_id ?? app.project?.project_id ?? 'app'}</small>
              </button>
            );
          })}
          {visibleApps.length === 0 && <div className="ion-empty-state">NO APPS MATCH FILTER</div>}
        </div>

        <AppPreviewDetail
          app={selectedApp}
          busyKey={launchBusyKey}
          diagnostics={selectedRecord?.launch_id ? launchDiagnostics[selectedRecord.launch_id] : undefined}
          onCapture={() => captureDiagnostics(selectedRecord)}
          onStart={() => startApp(selectedApp)}
          onStop={() => stopLaunch(selectedRecord)}
          previewSession={selectedPreviewSession}
          comparison={selectedComparison}
          record={selectedRecord}
        />
      </div>

      <AppDiagnosticsTimeline
        busy={diagnosticsBusy}
        model={diagnosticsTimeline}
        onRefresh={() => refreshDiagnosticsTimeline(selectedRecord?.launch_id)}
        onSetMode={setDiagnosticsMode}
        selectedLaunchId={selectedRecord?.launch_id}
      />

      <AppDiagnosticsMatrixPanel
        busy={diagnosticsMatrixBusy}
        onRun={runDiagnosticsMatrix}
        result={diagnosticsMatrixResult}
      />

      {actionMessage && <div className="ion-app-preview-message">{actionMessage}</div>}

      <div className="ion-app-preview-nonclaims">
        <span>candidate local runtime control only</span>
        <span>no accepted state</span>
        <span>no production authority</span>
        <span>no secrets authority</span>
      </div>
    </section>
  );
}

function AppDiagnosticsMatrixPanel({
  busy,
  onRun,
  result,
}: {
  busy: string;
  onRun: (mode: 'standard' | 'forensic' | 'exhaustive') => void;
  result?: DiagnosticsMatrixResult;
}) {
  const coverage = result?.coverage ?? {};
  const runs = Array.isArray(result?.runs) ? result.runs : [];
  return (
    <section className={`ion-app-diagnostics-matrix is-${result?.ok ? 'passed' : result ? 'failed' : 'idle'}`}>
      <div className="ion-app-diagnostics-matrix-head">
        <div>
          <div className="ion-section-title">DIAGNOSTICS MATRIX</div>
          <b>{result?.ok ? 'coverage proven' : result ? 'needs attention' : 'fixture proof runner'}</b>
          <p>Runs bounded local fixtures through the managed preview proxy, executes them in Playwright, records timelines, writes snapshots, and stops launched servers.</p>
        </div>
        <div className="ion-app-diagnostics-matrix-actions">
          <button disabled={Boolean(busy)} onClick={() => onRun('standard')} type="button">{busy === 'standard' ? 'Running' : 'Run Standard'}</button>
          <button disabled={Boolean(busy)} onClick={() => onRun('forensic')} type="button">{busy === 'forensic' ? 'Running' : 'Run Forensic'}</button>
          <button disabled={Boolean(busy)} onClick={() => onRun('exhaustive')} type="button">{busy === 'exhaustive' ? 'Running' : 'Run Exhaustive'}</button>
        </div>
      </div>
      <div className="ion-app-diagnostics-matrix-metrics">
        <Metric label="mode" value={text(result?.mode, 'not run')} />
        <Metric label="passed" value={`${text(coverage.passed_count, '0')}/${text(coverage.run_count, '0')}`} />
        <Metric label="browser" value={coverage.browser ? 'yes' : 'pending'} />
        <Metric label="network" value={coverage.network ? 'yes' : 'pending'} />
        <Metric label="react/r3f" value={coverage.react && coverage.r3f ? 'yes' : 'pending'} />
        <Metric label="three/webgl" value={coverage.three && coverage.webgl ? 'yes' : 'pending'} />
      </div>
      {result && (
        <div className="ion-app-diagnostics-matrix-paths">
          <PathRow label="matrix receipt" value={result.receipt_path ?? result.finding ?? result.error} />
          <PathRow label="snapshot" value={result.snapshot_path} />
          <PathRow label="snapshot receipt" value={result.snapshot_receipt_path} />
        </div>
      )}
      <div className="ion-app-diagnostics-matrix-runs">
        {runs.map((run) => {
          const runCoverage = run.coverage ?? {};
          return (
            <article className={`ion-app-diagnostics-matrix-run is-${run.ok ? 'passed' : 'failed'}`} key={`${run.app_id ?? 'run'}:${run.launch_id ?? 'none'}`}>
              <span>{run.ok ? 'passed' : 'failed'}</span>
              <b>{text(run.app_id, 'fixture')}</b>
              <small>{String(run.timeline_event_count ?? 0)} events / stop {run.stop_ok === false ? 'failed' : 'ok'}</small>
              <div className="ion-app-diagnostics-event-tags">
                {['browser', 'performance', 'network', 'react', 'r3f', 'three', 'webgl'].map((key) => (
                  <small className={runCoverage[key] ? 'is-on' : undefined} key={key}>{key}</small>
                ))}
              </div>
              {run.screenshot_href && <a href={run.screenshot_href} target="_blank" rel="noreferrer">screenshot</a>}
            </article>
          );
        })}
        {runs.length === 0 && <div className="ion-empty-state">RUN A MATRIX TO SEE FIXTURE COVERAGE</div>}
      </div>
    </section>
  );
}

function AppDiagnosticsTimeline({
  busy,
  model,
  onRefresh,
  onSetMode,
  selectedLaunchId,
}: {
  busy: string;
  model?: DiagnosticsTimelineModel;
  onRefresh: () => void;
  onSetMode: (mode: string, enabled: boolean) => void;
  selectedLaunchId?: string;
}) {
  const config = model?.config ?? {};
  const summary = model?.summary ?? {};
  const events = Array.isArray(model?.events) ? model.events : [];
  const lanes = Array.isArray(model?.lanes) ? model.lanes : [];
  const sourceHealth = Array.isArray(model?.source_health) ? model.source_health : [];
  const mode = text(config.mode, 'off');
  const enabled = Boolean(config.enabled);
  const [laneFilter, setLaneFilter] = useState('all');
  const [sourceFilter, setSourceFilter] = useState('all');
  const [severityFilter, setSeverityFilter] = useState('all');
  const [eventQuery, setEventQuery] = useState('');
  const [selectedEventId, setSelectedEventId] = useState('');
  const [snapshotBusy, setSnapshotBusy] = useState(false);
  const [snapshotResult, setSnapshotResult] = useState<Record<string, unknown> | undefined>();
  const laneOptions = lanes.filter((lane) => Number(lane.event_count ?? 0) > 0).map((lane) => text(lane.lane_id, 'unknown'));
  const sourceOptions = sourceHealth.filter((source) => Number(source.event_count ?? 0) > 0).map((source) => text(source.source_id, 'unknown'));
  const severityOptions = Array.from(new Set(events.map((event) => text(event.severity, 'info'))));
  const filteredEvents = events.filter((event) => {
    const haystack = JSON.stringify({
      type: event.event_type,
      summary: event.summary,
      detail: event.detail,
      source: event.source,
      lane: event.lane,
      trace: event.trace_id,
      run: event.run_id,
    }).toLowerCase();
    if (laneFilter !== 'all' && text(event.lane, 'unknown') !== laneFilter) return false;
    if (sourceFilter !== 'all' && text(event.source, 'unknown') !== sourceFilter) return false;
    if (severityFilter !== 'all' && text(event.severity, 'info') !== severityFilter) return false;
    if (eventQuery.trim() && !haystack.includes(eventQuery.trim().toLowerCase())) return false;
    return true;
  });
  const selectedEvent =
    filteredEvents.find((event) => diagnosticEventId(event) === selectedEventId) ??
    filteredEvents[filteredEvents.length - 1] ??
    events[events.length - 1];
  const selectedCorrelations = selectedEvent
    ? filteredEvents
        .filter((event) => diagnosticEventId(event) !== diagnosticEventId(selectedEvent) && sharesDiagnosticsCorrelation(event, selectedEvent))
        .slice(-18)
    : [];

  async function writeSnapshot() {
    setSnapshotBusy(true);
    setSnapshotResult(undefined);
    try {
      const response = await fetch('/cockpit/projects/launch/diagnostics/snapshot', {
        method: 'POST',
        headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
        body: JSON.stringify({
          confirmation: 'ION_APP_DIAGNOSTICS_SNAPSHOT_CONFIRMED',
          launch_id: selectedLaunchId ?? '',
          limit: 900,
          lane: laneFilter,
          source: sourceFilter,
          severity: severityFilter,
          query: eventQuery,
        }),
      });
      const result = await response.json();
      setSnapshotResult(result);
    } catch (error) {
      setSnapshotResult({ ok: false, finding: error instanceof Error ? error.message : 'snapshot failed' });
    } finally {
      setSnapshotBusy(false);
    }
  }

  return (
    <section className={`ion-app-diagnostics-timeline is-${enabled ? mode : 'off'}`}>
      <div className="ion-app-diagnostics-head">
        <div>
          <div className="ion-section-title">APP DIAGNOSTICS TIMELINE</div>
          <b>{enabled ? mode : 'off'}</b>
          <p>Mode-controlled event forensics. Forensic and exhaustive modes intentionally add overhead for testing.</p>
        </div>
        <div className="ion-app-diagnostics-modebar">
          <button className={!enabled || mode === 'off' ? 'is-active' : undefined} disabled={busy === 'mode:off'} onClick={() => onSetMode('off', false)} type="button">Off</button>
          <button className={enabled && mode === 'standard' ? 'is-active' : undefined} disabled={busy === 'mode:standard'} onClick={() => onSetMode('standard', true)} type="button">Standard</button>
          <button className={enabled && mode === 'forensic' ? 'is-active' : undefined} disabled={busy === 'mode:forensic'} onClick={() => onSetMode('forensic', true)} type="button">Forensic</button>
          <button className={enabled && mode === 'exhaustive' ? 'is-active' : undefined} disabled={busy === 'mode:exhaustive'} onClick={() => onSetMode('exhaustive', true)} type="button">Exhaustive</button>
          <button disabled={busy === 'timeline'} onClick={onRefresh} type="button">{busy === 'timeline' ? 'Refreshing' : 'Refresh'}</button>
          <button disabled={snapshotBusy} onClick={writeSnapshot} type="button">{snapshotBusy ? 'Snapshotting' : 'Snapshot'}</button>
        </div>
      </div>
      <div className="ion-app-diagnostics-metrics">
        <Metric label="selected launch" value={selectedLaunchId ?? 'none'} />
        <Metric label="events" value={String(summary.event_count ?? events.length)} />
        <Metric label="stored" value={String(summary.stored_event_count ?? 0)} />
        <Metric label="receipts" value={String(summary.receipt_event_count ?? 0)} />
        <Metric label="lanes" value={String(summary.lane_count ?? lanes.filter((lane) => Number(lane.event_count ?? 0) > 0).length)} />
        <Metric label="slowdown" value={summary.slowdown_intentional ? 'intentional' : 'off'} />
      </div>
      <div className="ion-app-diagnostics-casegraph" aria-label="Diagnostics evidence graph">
        <div className="ion-app-diagnostics-lanes">
          <div className="ion-app-diagnostics-subhead">Evidence lanes</div>
          {lanes.map((lane) => (
            <article className={`ion-app-diagnostics-lane is-${Number(lane.event_count ?? 0) > 0 ? 'active' : 'quiet'}`} key={text(lane.lane_id, text(lane.label, 'lane'))}>
              <span>{text(lane.label, 'lane')}</span>
              <b>{String(lane.event_count ?? 0)}</b>
              <small>{text(lane.description, 'no description')}</small>
              <em>{Number(lane.error_count ?? 0) > 0 ? `${String(lane.error_count)} errors` : text(lane.latest_at, 'no events')}</em>
            </article>
          ))}
          {lanes.length === 0 && <div className="ion-empty-state">LANES NOT EMITTED</div>}
        </div>
        <div className="ion-app-diagnostics-sources">
          <div className="ion-app-diagnostics-subhead">Source health</div>
          {sourceHealth.slice(0, 14).map((source) => (
            <article className={`ion-app-diagnostics-source is-${text(source.status, 'unavailable')}`} key={text(source.source_id, 'source')}>
              <span>{text(source.source_id, 'source')}</span>
              <b>{text(source.status, 'unavailable')}</b>
              <small>{String(source.event_count ?? 0)} events / {String(source.error_count ?? 0)} errors</small>
            </article>
          ))}
          {sourceHealth.length === 0 && <div className="ion-empty-state">SOURCE HEALTH NOT EMITTED</div>}
        </div>
      </div>
      <div className="ion-app-diagnostics-filterbar">
        <select aria-label="Filter diagnostics lane" onChange={(event) => setLaneFilter(event.target.value)} value={laneFilter}>
          <option value="all">All lanes</option>
          {laneOptions.map((lane) => <option key={lane} value={lane}>{lane}</option>)}
        </select>
        <select aria-label="Filter diagnostics source" onChange={(event) => setSourceFilter(event.target.value)} value={sourceFilter}>
          <option value="all">All sources</option>
          {sourceOptions.map((source) => <option key={source} value={source}>{source}</option>)}
        </select>
        <select aria-label="Filter diagnostics severity" onChange={(event) => setSeverityFilter(event.target.value)} value={severityFilter}>
          <option value="all">All severities</option>
          {severityOptions.map((severity) => <option key={severity} value={severity}>{severity}</option>)}
        </select>
        <input aria-label="Search diagnostics events" onChange={(event) => setEventQuery(event.target.value)} placeholder="Search event type, trace, source..." value={eventQuery} />
      </div>
      {snapshotResult && (
        <div className={`ion-app-diagnostics-snapshot is-${snapshotResult.ok ? 'active' : 'error'}`}>
          <span>{snapshotResult.ok ? 'snapshot written' : 'snapshot failed'}</span>
          <code>{text(snapshotResult.snapshot_path ?? snapshotResult.finding, 'no snapshot path')}</code>
        </div>
      )}
      <div className="ion-app-diagnostics-workbench">
        <div className="ion-app-diagnostics-rail">
          {filteredEvents.slice().reverse().map((event, index) => {
            const eventId = diagnosticEventId(event, `event-${index}`);
            const selected = selectedEvent ? diagnosticEventId(selectedEvent) === eventId : false;
            return (
              <button className={`ion-app-diagnostics-event is-${safeClassToken(event.severity, 'info')}${selected ? ' is-active' : ''}`} key={eventId} onClick={() => setSelectedEventId(eventId)} type="button">
                <div className="ion-app-diagnostics-marker" />
                <div className="ion-app-diagnostics-event-body">
                  <div className="ion-runtime-card-head">
                    <span>{text(event.lane_label ?? event.lane, 'event')} / {text(event.source, 'event')}</span>
                    <b>{text(event.event_type, 'diagnostic')}</b>
                  </div>
                  <p>{text(event.summary ?? event.detail, 'timeline event')}</p>
                  <div className="ion-app-diagnostics-event-tags">
                    <small>{text(event.signal, 'signal')}</small>
                    <small>{text(event.event_kind, 'instant')}</small>
                    <small>{text(event.source_kind, 'source')}</small>
                  </div>
                  <div className="ion-vnext-packet-meta">
                    <small>{text(event.created_at, 'time unknown')}</small>
                    <small>{text(event.state, 'state unknown')}</small>
                    <small>{event.running === true ? 'running' : event.running === false ? 'not running' : 'runtime unknown'}</small>
                  </div>
                </div>
              </button>
            );
          })}
          {filteredEvents.length === 0 && <div className="ion-empty-state">NO DIAGNOSTIC EVENTS MATCH FILTER</div>}
        </div>
        <div className="ion-app-diagnostics-selected">
          {selectedEvent ? (
            <>
              <div className="ion-app-diagnostics-selected-head">
                <span>{text(selectedEvent.source_of_truth_classification, 'candidate evidence')}</span>
                <b>{text(selectedEvent.event_type, 'diagnostic event')}</b>
                <p>Correlation is shown as shared evidence context, not causality unless a source declares a causal edge.</p>
              </div>
              <PathRow label="url" value={selectedEvent.url} />
              <PathRow label="path" value={selectedEvent.path ?? selectedEvent.receipt_path} />
              <PathRow label="trace" value={selectedEvent.trace_id ?? selectedEvent.span_id ?? selectedEvent.run_id} />
              <div className="ion-app-diagnostics-correlation">
                <span>correlated events</span>
                {selectedCorrelations.map((event) => (
                  <button key={diagnosticEventId(event)} onClick={() => setSelectedEventId(diagnosticEventId(event))} type="button">
                    <b>{text(event.event_type, 'event')}</b>
                    <small>{text(event.source, 'source')} / {text(event.created_at, 'time')}</small>
                  </button>
                ))}
                {selectedCorrelations.length === 0 && <small>no same-trace/run/correlation events in current filter</small>}
              </div>
              <details className="ion-app-diagnostics-inspector" open>
                <summary>evidence envelope</summary>
                <pre>{JSON.stringify({
                  event_id: selectedEvent.event_id,
                  lane: selectedEvent.lane,
                  correlation_ids: selectedEvent.correlation_ids,
                  attributes: selectedEvent.attributes,
                  payload: selectedEvent.payload,
                  artifacts: selectedEvent.artifact_refs,
                  redaction: selectedEvent.redaction,
                  integrity: selectedEvent.integrity,
                  authority: selectedEvent.authority,
                }, null, 2)}</pre>
              </details>
              {selectedEvent.log_tail ? <pre className="ion-project-launch-log">{text(selectedEvent.log_tail, '')}</pre> : null}
            </>
          ) : (
            <div className="ion-empty-state">SELECT A DIAGNOSTIC EVENT</div>
          )}
        </div>
      </div>
    </section>
  );
}

function diagnosticEventId(event: Record<string, unknown>, fallback = 'event'): string {
  return text(event.event_id ?? event.span_id ?? event.trace_id ?? event.run_id ?? event.created_at, fallback);
}

function safeClassToken(value: unknown, fallback = 'unknown'): string {
  return text(value, fallback).toLowerCase().replace(/[^a-z0-9_-]+/g, '-').replace(/^-+|-+$/g, '') || fallback;
}

function sharesDiagnosticsCorrelation(left: Record<string, unknown>, right: Record<string, unknown>): boolean {
  const ids = new Set<string>();
  for (const value of [right.trace_id, right.span_id, right.parent_span_id, right.run_id, right.launch_id]) {
    const item = text(value, '');
    if (item) ids.add(item);
  }
  if (Array.isArray(right.correlation_ids)) {
    right.correlation_ids.forEach((value) => {
      const item = text(value, '');
      if (item) ids.add(item);
    });
  }
  for (const value of [left.trace_id, left.span_id, left.parent_span_id, left.run_id, left.launch_id]) {
    if (ids.has(text(value, ''))) return true;
  }
  if (Array.isArray(left.correlation_ids)) {
    return left.correlation_ids.some((value) => ids.has(text(value, '')));
  }
  return false;
}

function AppPreviewDetail({
  app,
  busyKey,
  diagnostics,
  comparison,
  onCapture,
  onStart,
  onStop,
  previewSession,
  record,
}: {
  app?: AppPreviewRow;
  busyKey: string;
  diagnostics?: Record<string, unknown>;
  comparison?: IonProjectPreviewComparison;
  onCapture: () => void;
  onStart: () => void;
  onStop: () => void;
  previewSession?: IonProjectPreviewSession;
  record?: IonProjectLauncherRecord;
}) {
  if (!app) return <div className="ion-app-preview-detail"><div className="ion-empty-state">NO APP SELECTED</div></div>;
  const runtimeClass = launcherRuntimeClass(record, previewSession);
  const sessionFromLaunch = previewSession?.source_kind === 'launcher_record';
  const running = runtimeClass === 'running' && isManagedLaunchRunning(record);
  const stopAvailable = Boolean(record?.stop_available && running);
  const diagnosticsAvailable = Boolean(record?.launch_id && running);
  const launchBusy = busyKey === app.key || busyKey === record?.launch_id;
  const diagnosticsBusy = record?.launch_id ? busyKey === `diagnostics:${record.launch_id}` : false;
  const managedOpenHref = running ? previewSession?.same_origin_embed_url ?? record?.instrumented_open_href ?? record?.url : undefined;
  const openHref = sessionFromLaunch ? managedOpenHref : previewSession?.same_origin_embed_url ?? previewSession?.public_url ?? app.previewHref;
  const instrumentedHref = running ? previewSession?.same_origin_embed_url ?? record?.instrumented_open_href : undefined;
  const screenshot = diagnostics?.screenshot as Record<string, unknown> | undefined;
  const detailTone = running ? 'running' : ['detached', 'orphaned', 'stale'].includes(runtimeClass) ? runtimeClass : app.launchable ? 'ready' : 'watch';
  return (
    <article className={`ion-app-preview-detail is-${safeClassToken(detailTone, 'watch')}`}>
      <div className="ion-runtime-card-head">
        <span>{running ? 'active preview' : ['detached', 'orphaned', 'stale'].includes(runtimeClass) ? runtimeClass : app.launchable ? 'ready to launch' : 'external or catalog preview'}</span>
        <b>{app.label}</b>
      </div>
      <p>{app.domainLabel ?? app.family?.family_id ?? app.project?.summary ?? 'Discovered app preview target.'}</p>
      <div className="ion-vnext-packet-meta">
        <small>{app.framework ?? 'app'}</small>
        <small>{app.source}</small>
        <small>{record?.port && running ? `port ${record.port}` : runtimeClass || previewSession?.lifecycle_state || app.status || 'preview'}</small>
      </div>
      <PathRow label="source" value={app.path ?? app.project?.path} />
      <PathRow label="preview session" value={previewSession?.preview_id} />
      <PathRow label="provider" value={previewSession?.provider_id} />
      <PathRow label="runner" value={previewSession?.runner_location} />
      <PathRow label="session source ref" value={previewSession?.source_root_ref} />
      <PathRow label="runtime" value={runtimeClass} />
      <PathRow label="state basis" value={previewSession?.state_basis} />
      <PathRow label="ownership" value={previewSession?.ownership_confidence ?? record?.ownership_confidence} />
      <PathRow label="control" value={previewSession?.process_control_level ?? record?.process_control_level} />
      <PathRow label="last known" value={previewSession?.last_known_state ?? record?.last_known_state} />
      <PathRow label="finding" value={previewSession?.launcher_finding ?? text(record?.runtime_truth?.finding, '')} />
      <PathRow label="pair" value={comparison?.comparison_id} />
      <PathRow label="pair status" value={comparison ? `${text(comparison.status, 'registered')} / ${text(comparison.verdict, 'not compared')}` : ''} />
      <PathRow label="surface pair" value={comparison?.surface_pair} />
      <PathRow label="comparison route" value={comparison?.route} />
      <PathRow label="active url" value={running ? record?.url ?? app.previewHref : app.previewHref} />
      <PathRow label="launcher" value={app.launcherUrl} />
      <div className="ion-project-launch-actions">
        {app.version && <button disabled={!app.launchable || launchBusy} onClick={onStart} type="button">{running ? 'Open Managed' : launchBusy ? 'Starting' : 'Launch Preview'}</button>}
        {openHref && <a href={openHref} target="_blank" rel="noreferrer">Open Preview</a>}
        {instrumentedHref && <a href={instrumentedHref} target="_blank" rel="noreferrer">Instrumented Preview</a>}
        {app.launcherUrl && <a href={app.launcherUrl} target="_blank" rel="noreferrer">Open Launcher</a>}
        {app.catalogUrl && <a href={app.catalogUrl}>Catalog</a>}
        {stopAvailable && <button disabled={launchBusy} onClick={onStop} type="button">Stop Server</button>}
        {diagnosticsAvailable && <button disabled={diagnosticsBusy} onClick={onCapture} type="button">{diagnosticsBusy ? 'Capturing' : 'Diagnostics'}</button>}
      </div>
      {record?.message && <p>{record.message}</p>}
      {screenshot?.screenshot_href && <img alt="App preview diagnostic capture" className="ion-app-preview-screenshot" src={String(screenshot.screenshot_href)} />}
      <PathRow label="screenshot proof" value={screenshot?.screenshot_path} />
      {record?.log_tail && <pre className="ion-project-launch-log">{record.log_tail}</pre>}
    </article>
  );
}

function buildAppRows(projects: IonProjectCockpitProject[], families: IonProjectPortfolioFamily[]): AppPreviewRow[] {
  const rows: AppPreviewRow[] = [];
  families.forEach((family) => {
    (family.versions ?? []).forEach((version) => {
      const launch = version.launch ?? {};
      const launchable = Boolean(launch.launchable ?? version.launchable);
      if (!launchable && !version.path) return;
      rows.push({
        key: `version:${versionKey(version)}:${launch.project_path ?? version.path ?? family.family_id}`,
        label: text(launch.label ?? version.display_label ?? version.label ?? family.label ?? family.family_id),
        source: 'portfolio',
        domainLabel: family.domain_label ?? family.domain_id ?? family.group_id,
        family,
        version,
        launchable,
        path: launch.project_path ?? version.path,
        framework: launch.framework ?? version.stack,
        status: launch.status ?? (launchable ? 'ready' : 'metadata'),
      });
    });
  });
  projects.forEach((project) => {
    if (!project.preview_href && !project.launcher_url && !project.app_catalog_url) return;
    rows.push({
      key: `project:${project.project_id}`,
      label: text(project.label ?? project.project_id),
      source: 'project',
      project,
      launchable: Boolean(project.launcher_url || project.preview_href),
      path: project.path,
      framework: project.kind,
      status: project.status,
      previewHref: project.preview_href,
      launcherUrl: project.launcher_url,
      catalogUrl: project.app_catalog_url,
    });
  });
  const byKey = new Map<string, AppPreviewRow>();
  rows.forEach((row) => byKey.set(row.key, row));
  return Array.from(byKey.values()).sort((left, right) => {
    const leftLaunch = left.launchable ? 0 : 1;
    const rightLaunch = right.launchable ? 0 : 1;
    if (leftLaunch !== rightLaunch) return leftLaunch - rightLaunch;
    return left.label.localeCompare(right.label);
  });
}

function mergeLauncherRows(rows: AppPreviewRow[], records: IonProjectLauncherRecord[]) {
  const merged = [...rows];
  records.forEach((record) => {
    if (!record.launch_id) return;
    const matched = merged.some((row) => matchesLaunch(record, row.version?.launch?.project_path ?? row.version?.path ?? row.path, row.version?.launch?.version_id ?? row.version?.version_id, row.version?.launch?.project_id ?? row.version?.project_id ?? row.project?.project_id));
    if (matched) return;
    const runtimeState = launcherRuntimeClass(record);
    merged.push({
      key: `launch:${record.launch_id}`,
      label: text(record.label ?? record.launch_id, 'Recovered launch'),
      source: 'launcher',
      launchId: record.launch_id,
      launchable: false,
      path: record.path,
      framework: record.framework,
      status: record.ownership_confidence ?? record.state,
      runtimeState,
    });
  });
  return merged;
}

function launchRecordForApp(app: AppPreviewRow | undefined, records: IonProjectLauncherRecord[]) {
  if (!app) return undefined;
  if (app.launchId) return records.find((record) => record.launch_id === app.launchId);
  const path = app.version?.launch?.project_path ?? app.version?.path ?? app.path;
  const versionId = app.version?.launch?.version_id ?? app.version?.version_id;
  const projectId = app.version?.launch?.project_id ?? app.version?.project_id ?? app.project?.project_id;
  return records.find((record) => isManagedLaunchRunning(record) && matchesLaunch(record, path, versionId, projectId))
    ?? records.find((record) => matchesLaunch(record, path, versionId, projectId));
}

function previewSessionForApp(app: AppPreviewRow | undefined, sessions: IonProjectPreviewSession[], record?: IonProjectLauncherRecord) {
  if (record?.launch_id) {
    const launchSession = sessions.find((session) => session.preview_id === `launch:${record.launch_id}`);
    if (launchSession) return launchSession;
  }
  if (!app) return undefined;
  const versionId = app.version?.launch?.version_id ?? app.version?.version_id;
  const projectId = app.version?.launch?.project_id ?? app.version?.project_id ?? app.project?.project_id;
  return sessions.find((session) => Boolean(versionId && session.version_id === versionId))
    ?? sessions.find((session) => Boolean(projectId && session.project_id === projectId));
}

function comparisonForSession(session: IonProjectPreviewSession | undefined, comparisons: IonProjectPreviewComparison[]) {
  const previewId = session?.preview_id;
  if (!previewId) return undefined;
  return comparisons.find((comparison) => comparison.baseline_preview_id === previewId || comparison.candidate_preview_id === previewId);
}

function matchesLaunch(record: IonProjectLauncherRecord, path?: string, versionId?: string, projectId?: string) {
  return Boolean((path && record.path === path) || (versionId && record.version_id === versionId) || (projectId && record.project_id === projectId));
}

function isManagedLaunchRunning(record?: IonProjectLauncherRecord) {
  return Boolean(record?.running && !record.detached && record.actual_process_control !== false);
}

function launcherRuntimeClass(record?: IonProjectLauncherRecord, previewSession?: IonProjectPreviewSession) {
  if (previewSession?.runtime_state_class) return previewSession.runtime_state_class;
  if (!record) return previewSession?.lifecycle_state ?? 'registered';
  if (isManagedLaunchRunning(record)) return 'running';
  if (record.ownership_confidence === 'orphaned_local_preview_unverified') return 'orphaned';
  if (record.detached && record.ownership_confidence === 'stale_manifest_no_listener') return 'stale';
  if (record.detached) return 'detached';
  return text(record.state, 'not_running');
}

function mergeLaunchRecords(...sets: IonProjectLauncherRecord[][]) {
  const byId = new Map<string, IonProjectLauncherRecord>();
  sets.flat().forEach((record) => {
    const key = record.launch_id ?? `${record.path ?? ''}:${record.port ?? ''}`;
    if (!key.trim()) return;
    byId.set(key, record);
  });
  return Array.from(byId.values()).sort((left, right) => {
    const leftRunning = isManagedLaunchRunning(left) ? 0 : 1;
    const rightRunning = isManagedLaunchRunning(right) ? 0 : 1;
    if (leftRunning !== rightRunning) return leftRunning - rightRunning;
    return String(right.updated_at ?? '').localeCompare(String(left.updated_at ?? ''));
  });
}

function versionKey(version: IonProjectPortfolioVersion) {
  return text(version.version_id ?? version.project_id ?? version.path ?? version.label, 'version');
}

function Metric({ label, value }: { label: string; value: string }) {
  return <div className="ion-runtime-metric"><span>{label}</span><b>{value}</b></div>;
}

function PathRow({ label, value }: { label: string; value: unknown }) {
  return (
    <div className="ion-path-row">
      <span>{label}</span>
      <code>{text(value, '')}</code>
    </div>
  );
}

function text(value: unknown, fallback = 'unknown') {
  if (Array.isArray(value)) return value.map((item) => text(item)).join(', ');
  if (typeof value === 'string' && value.trim()) return value.trim();
  if (typeof value === 'number' || typeof value === 'boolean') return String(value);
  return fallback;
}
