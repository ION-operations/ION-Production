import { useEffect, useMemo, useState } from 'react';
import type {
  IonCockpitViewModel,
  IonSystemDiagnosticsAction,
  IonSystemDiagnosticsCleanupCandidate,
  IonSystemDiagnosticsDevServer,
} from './ionRuntimeCockpitTypes';

type Props = {
  runtime: IonCockpitViewModel;
  onRuntimeRefresh?: () => void;
};

type ActionReceipt = {
  ok?: boolean;
  timestamp?: string;
  action_type?: string;
  status?: string;
  detail?: string;
  affected_pids?: number[];
  affected_ports?: number[];
  error?: string;
};

type SystemDiagnosticsView = 'overview' | 'dev' | 'security' | 'services';

function pct(value?: number) {
  return `${Math.round(value ?? 0)}%`;
}

function mb(value?: number) {
  return `${Math.round(value ?? 0)} MB`;
}

function age(seconds?: number) {
  const value = seconds ?? 0;
  if (value >= 86400) return `${Math.floor(value / 86400)}D`;
  if (value >= 3600) return `${Math.floor(value / 3600)}H`;
  if (value >= 60) return `${Math.floor(value / 60)}M`;
  return `${value}S`;
}

function compactPath(value?: string | null) {
  if (!value) return '';
  return value
    .replace('/home/sev/ION - Production/ION_Developement/', 'ION_DEV/')
    .replace('/home/sev/ION - Production/', 'ION_PROD/')
    .replace('/home/sev/Application_Dev/', 'APP_DEV/')
    .replace('/home/sev/Cosmos/', 'COSMOS/')
    .replace('/home/sev/', '~/');
}

function titleCase(value?: string | null) {
  return String(value || 'unknown').replace(/[_-]+/g, ' ').toUpperCase();
}

function yesNo(value?: boolean) {
  return value ? 'YES' : 'NO';
}

function probeLabel(server: IonSystemDiagnosticsDevServer) {
  const probe = server.http_probe;
  if (probe?.serves_http) return `HTTP ${probe.http_status ?? 'OK'}`;
  return titleCase(probe?.finding ?? 'no_http_probe');
}

function eligibilityLabel(server: IonSystemDiagnosticsDevServer, candidate?: IonSystemDiagnosticsCleanupCandidate) {
  const eligibility = candidate?.action_eligibility ?? server.action_eligibility;
  if (eligibility?.allowed) return 'STOPPABLE';
  const reasons = eligibility?.reasons ?? [];
  if (reasons.includes('PROTECTED_PROCESS')) return 'PROTECTED';
  if (reasons.includes('NOT_DEV_SERVER')) return 'NOT DEV';
  if (reasons.includes('NO_PID')) return 'NO PID';
  return 'BLOCKED';
}

function serverTitle(server: IonSystemDiagnosticsDevServer) {
  return server.package_name || server.http_probe?.title || server.process_name || `${server.framework || 'local'} server`;
}

function openServer(url?: string) {
  if (!url) return;
  window.open(url, '_blank', 'noopener,noreferrer');
}

function cleanupCandidateForServer(server: IonSystemDiagnosticsDevServer, candidates: IonSystemDiagnosticsCleanupCandidate[]) {
  return candidates.find((candidate) => candidate.id === server.id)
    ?? candidates.find((candidate) => candidate.pid && server.pid && candidate.pid === server.pid && candidate.port === server.port)
    ?? candidates.find((candidate) => candidate.port === server.port && candidate.cwd && server.cwd && candidate.cwd === server.cwd)
    ?? candidates.find((candidate) => candidate.port === server.port && candidate.process_name === server.process_name);
}

async function postJson<T>(path: string, payload: Record<string, unknown>): Promise<T> {
  const response = await fetch(path, {
    method: 'POST',
    headers: { 'content-type': 'application/json', accept: 'application/json' },
    body: JSON.stringify(payload),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(String(data.error ?? data.finding ?? `http_${response.status}`));
  }
  return data as T;
}

export function SystemDiagnosticsPanel({ runtime, onRuntimeRefresh }: Props) {
  const model = runtime.system_diagnostics;
  const summary = model?.summary ?? {};
  const candidates = useMemo(() => model?.cleanup_candidates ?? [], [model]);
  const devServers = useMemo(() => model?.dev_servers ?? [], [model]);
  const dataQuality = model?.data_quality ?? {};
  const staleCandidateIds = useMemo(() => candidates.filter((candidate) => candidate.stale).map((candidate) => candidate.id), [candidates]);
  const stoppableDevServerCount = useMemo(() => devServers.filter((server) => cleanupCandidateForServer(server, candidates)).length, [candidates, devServers]);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [selectionTouched, setSelectionTouched] = useState(false);
  const [activeView, setActiveView] = useState<SystemDiagnosticsView>('dev');
  const [busy, setBusy] = useState(false);
  const [receipt, setReceipt] = useState<ActionReceipt | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!selectionTouched) {
      setSelectedIds(staleCandidateIds);
      return;
    }
    setSelectedIds((current) => current.filter((id) => candidates.some((candidate) => candidate.id === id)));
  }, [candidates, staleCandidateIds, selectionTouched]);

  if (!model) {
    return (
      <section className="ion-panel ion-system-diagnostics-panel">
        <div className="ion-section-title">SYSTEM DIAGNOSTICS</div>
        <div className="ion-empty-state">NO SYSTEM DIAGNOSTICS MODEL</div>
      </section>
    );
  }

  const selectedCandidates = candidates.filter((candidate) => selectedIds.includes(candidate.id));
  const verifiedDevServerCount = summary.http_verified_dev_server_count ?? devServers.filter((server) => server.http_probe?.serves_http).length;
  const protectedDevServerCount = summary.protected_dev_server_count ?? devServers.filter((server) => server.protected).length;

  const executeStopCandidates = async (targets: IonSystemDiagnosticsCleanupCandidate[], label: string) => {
    if (!targets.length || busy) return;
    const ports = targets.map((candidate) => candidate.port).filter(Boolean).join(', ');
    const ok = window.confirm(`Stop ${label} local dev server${targets.length === 1 ? '' : 's'}${ports ? ` on port(s) ${ports}` : ''}?`);
    if (!ok) return;
    setBusy(true);
    setError(null);
    const receipts: ActionReceipt[] = [];
    const previewEndpoint = model.action_contract?.preview_endpoint ?? '/cockpit/system/preview_action';
    const executeEndpoint = model.action_contract?.execute_endpoint ?? '/cockpit/system/execute_action';
    try {
      for (const candidate of targets) {
        const action: IonSystemDiagnosticsAction = {
          ...candidate.action,
          confirmation: model.action_contract?.stop_confirmation,
        };
        await postJson(previewEndpoint, { action });
        receipts.push(await postJson<ActionReceipt>(executeEndpoint, { action }));
      }
      const affectedPorts = Array.from(new Set(receipts.flatMap((item) => item.affected_ports ?? []))).sort((a, b) => a - b);
      setReceipt({
        ok: true,
        status: 'ok',
        detail: `Stopped ${receipts.length} local dev server${receipts.length === 1 ? '' : 's'}.`,
        affected_ports: affectedPorts,
      });
      setSelectionTouched(false);
      setSelectedIds([]);
      await onRuntimeRefresh?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  };

  const stopSelected = async () => {
    await executeStopCandidates(selectedCandidates, 'selected');
  };

  return (
    <section className="ion-system-diagnostics-panel">
      <section className="ion-panel ion-system-hero">
        <div>
          <div className="ion-section-title">LOCAL SYSTEM CONTROL</div>
          <div className={`ion-runtime-verdict is-${summary.issue_count ? 'degraded' : 'ready'}`}>{summary.issue_count ? 'ATTENTION' : 'READY'}</div>
          <div className="ion-runtime-objective">Same-port machine diagnostics, active dev server inventory, protected process boundaries, and local stop actions.</div>
          <div className="ion-system-hero-meta">
            <span>{model.generated_at ?? 'NO TIMESTAMP'}</span>
            <span>{dataQuality.process_source ?? 'ps'} / {dataQuality.port_source ?? 'ss'}</span>
            <span>LOCAL OPERATOR</span>
            <span>PROD {model.authority?.production_authority ? 'TRUE' : 'FALSE'}</span>
            <span>LIVE {model.authority?.live_execution_authority ? 'TRUE' : 'FALSE'}</span>
          </div>
        </div>
        <div className="ion-system-action-stack">
          <button type="button" onClick={() => onRuntimeRefresh?.()} disabled={busy}>REFRESH</button>
          <button type="button" onClick={() => {
            setSelectionTouched(true);
            setSelectedIds(staleCandidateIds);
          }} disabled={busy || staleCandidateIds.length === 0}>SELECT STALE</button>
          <button type="button" onClick={() => {
            setSelectionTouched(true);
            setSelectedIds(candidates.map((candidate) => candidate.id));
          }} disabled={busy || candidates.length === 0}>SELECT STOPPABLE</button>
          <button type="button" onClick={() => {
            setSelectionTouched(true);
            setSelectedIds([]);
          }} disabled={busy || selectedIds.length === 0}>CLEAR</button>
          <button className="ion-system-stop" type="button" onClick={stopSelected} disabled={busy || selectedCandidates.length === 0}>STOP SELECTED</button>
        </div>
      </section>

      {error ? <div className="ion-system-banner is-error">{error}</div> : null}
      {receipt ? <div className="ion-system-banner is-ok">{receipt.detail}</div> : null}

      <div className="ion-system-view-tabs">
        {([
          ['overview', 'OVERVIEW'],
          ['dev', 'DEV SERVERS'],
          ['security', 'SECURITY'],
          ['services', 'SERVICES'],
        ] as Array<[SystemDiagnosticsView, string]>).map(([view, label]) => (
          <button key={view} type="button" className={activeView === view ? 'is-active' : ''} onClick={() => setActiveView(view)}>{label}</button>
        ))}
      </div>

      {(activeView === 'overview' || activeView === 'dev') ? (
        <div className="ion-runtime-grid ion-system-metric-grid">
          <Metric label="dev servers" value={String(summary.active_dev_server_count ?? devServers.length)} />
          <Metric label="verified" value={String(verifiedDevServerCount)} />
          <Metric label="stoppable" value={String(stoppableDevServerCount)} />
          <Metric label="protected dev" value={String(protectedDevServerCount)} />
          <Metric label="cleanup" value={String(summary.cleanup_candidate_count ?? 0)} />
          <Metric label="listeners" value={String(summary.listener_count ?? 0)} />
          <Metric label="cpu" value={pct(summary.cpu_percent)} />
          <Metric label="memory" value={pct(summary.memory_percent)} note={`${mb(summary.memory_used_mb)} / ${mb(summary.memory_total_mb)}`} />
          <Metric label="swap" value={pct(summary.swap_percent)} note={`${mb(summary.swap_used_mb)} / ${mb(summary.swap_total_mb)}`} />
          <Metric label="disk" value={pct(summary.disk_percent)} />
          <Metric label="issues" value={String(summary.issue_count ?? 0)} />
        </div>
      ) : null}

      {activeView === 'overview' ? <OverviewView model={model} dataQuality={dataQuality} verifiedDevServerCount={verifiedDevServerCount} devServerCount={devServers.length} /> : null}

      {activeView === 'dev' ? (
        <>
          <section className="ion-panel ion-system-dev-panel">
            <div className="ion-system-panel-head">
              <div>
                <div className="ion-section-title">ACTIVE DEV SERVERS</div>
                <p>{devServers.length} detected local project listeners / {verifiedDevServerCount} HTTP verified / {protectedDevServerCount} protected</p>
              </div>
              <div className="ion-system-pill-row">
                <span>PROBE {dataQuality.http_probe_timeout_seconds ?? 0}s</span>
                <span>{dataQuality.dev_server_count_includes_protected ? 'PROTECTED INCLUDED' : 'PROTECTED EXCLUDED'}</span>
                <span>{dataQuality.cleanup_candidates_exclude_protected ? 'SAFE STOP ONLY' : 'STOP UNFILTERED'}</span>
              </div>
            </div>
            <div className="ion-system-dev-list">
              {devServers.map((server) => {
                const cleanupCandidate = cleanupCandidateForServer(server, candidates);
                const cleanupId = cleanupCandidate?.id ?? server.id;
                return (
                  <DevServerCard
                    key={server.id}
                    server={server}
                    candidate={cleanupCandidate}
                    selected={Boolean(cleanupCandidate && selectedIds.includes(cleanupId))}
                    busy={busy}
                    onStop={() => {
                      if (cleanupCandidate) void executeStopCandidates([cleanupCandidate], 'this');
                    }}
                    onToggle={() => {
                      if (!cleanupCandidate) return;
                      setSelectionTouched(true);
                      setSelectedIds((current) => current.includes(cleanupId) ? current.filter((id) => id !== cleanupId) : [...current, cleanupId]);
                    }}
                  />
                );
              })}
              {devServers.length === 0 && <div className="ion-empty-state">NO ACTIVE DEV SERVER LISTENERS DETECTED</div>}
            </div>
          </section>

          <section className="ion-system-grid">
            <CleanupQueue candidates={candidates} selectedIds={selectedIds} setSelectionTouched={setSelectionTouched} setSelectedIds={setSelectedIds} />
            <section className="ion-panel">
              <div className="ion-section-title">TOP PROCESSES</div>
              <ProcessTable rows={(model.top_processes ?? []).slice(0, 14)} />
            </section>
            <section className="ion-panel">
              <div className="ion-section-title">LISTENING PORTS</div>
              <PortTable rows={(model.ports ?? []).slice(0, 18)} />
            </section>
          </section>
        </>
      ) : null}

      {activeView === 'security' ? (
        <section className="ion-system-grid">
          <SecuritySummaryPanel model={model} />
          <RouteMatrixPanel rows={model.route_matrix ?? []} />
        </section>
      ) : null}

      {activeView === 'services' ? (
        <section className="ion-system-grid">
          <ServiceHealthPanel model={model} />
          <RouteMatrixPanel rows={(model.route_matrix ?? []).filter((row) => row.route_class === 'local_control')} />
        </section>
      ) : null}
    </section>
  );
}

function Metric({ label, value, note }: { label: string; value: string; note?: string }) {
  return <div className="ion-runtime-metric"><span>{label}</span><b>{value}</b>{note ? <small>{note}</small> : null}</div>;
}

function OverviewView({
  model,
  dataQuality,
  verifiedDevServerCount,
  devServerCount,
}: {
  model: NonNullable<IonCockpitViewModel['system_diagnostics']>;
  dataQuality: NonNullable<IonCockpitViewModel['system_diagnostics']>['data_quality'];
  verifiedDevServerCount: number;
  devServerCount: number;
}) {
  const risk = model.risk_summary ?? {};
  return (
    <section className="ion-system-grid">
      <section className="ion-panel">
        <div className="ion-section-title">RISK POSTURE</div>
        <div className="ion-system-mini-grid">
          <Fact label="verdict" value={titleCase(risk.verdict ?? 'unknown')} />
          <Fact label="risk findings" value={String(model.risk_findings?.length ?? 0)} />
          <Fact label="security findings" value={String(risk.security_finding_count ?? 0)} />
          <Fact label="service issues" value={String(risk.critical_service_issue_count ?? 0)} />
          <Fact label="stale servers" value={String(risk.stale_dev_server_count ?? 0)} />
          <Fact label="cleanup actions" value={String(risk.actionable_cleanup_count ?? 0)} />
        </div>
      </section>

      <section className="ion-panel">
        <div className="ion-section-title">LIKELY LAG CAUSES</div>
        <div className="ion-system-list">
          {(model.risk_findings ?? []).slice(0, 8).map((finding) => (
            <article className={`ion-runtime-card is-${finding.severity}`} key={`${finding.category}-${finding.id}`}>
              <div className="ion-runtime-card-head"><span>{finding.category ?? finding.severity}</span><b>{finding.title}</b></div>
              <p>{finding.detail}</p>
              <code>{(finding.evidence ?? []).join(' / ')}</code>
            </article>
          ))}
          {(model.risk_findings ?? []).length === 0 && <div className="ion-empty-state is-ok">NO ACTIVE RISK FINDING</div>}
        </div>
      </section>

      <section className="ion-panel">
        <div className="ion-section-title">MODEL FIDELITY</div>
        <div className="ion-system-mini-grid">
          <Fact label="process source" value={dataQuality?.process_source ?? 'ps'} />
          <Fact label="port source" value={dataQuality?.port_source ?? 'ss -ltnp'} />
          <Fact label="http verified" value={`${verifiedDevServerCount}/${devServerCount}`} />
          <Fact label="cleanup policy" value={dataQuality?.cleanup_candidates_exclude_protected ? 'protected blocked' : 'unfiltered'} />
          <Fact label="redaction" value={dataQuality?.command_redaction_enabled ? 'enabled' : 'unknown'} />
          <Fact label="redacted commands" value={String(dataQuality?.redacted_process_command_count ?? 0)} />
          <Fact label="accepted state" value={model.authority?.accepted_state_authority ? 'true' : 'false'} />
          <Fact label="live execution" value={model.authority?.live_execution_authority ? 'true' : 'false'} />
        </div>
      </section>
    </section>
  );
}

function CleanupQueue({
  candidates,
  selectedIds,
  setSelectionTouched,
  setSelectedIds,
}: {
  candidates: IonSystemDiagnosticsCleanupCandidate[];
  selectedIds: string[];
  setSelectionTouched: (value: boolean) => void;
  setSelectedIds: (updater: (current: string[]) => string[]) => void;
}) {
  return (
    <section className="ion-panel">
      <div className="ion-section-title">SAFE STOP QUEUE</div>
      <div className="ion-system-cleanup-list">
        {candidates.map((candidate) => (
          <label className={`ion-system-cleanup-row ${candidate.stale ? 'is-stale' : ''}`} key={candidate.id}>
            <input
              type="checkbox"
              checked={selectedIds.includes(candidate.id)}
              onChange={() => {
                setSelectionTouched(true);
                setSelectedIds((current) => current.includes(candidate.id) ? current.filter((id) => id !== candidate.id) : [...current, candidate.id]);
              }}
            />
            <span>:{candidate.port ?? 'NA'}</span>
            <b>{candidate.process_name ?? 'dev server'}</b>
            <em>{candidate.stale ? 'STALE' : 'ACTIVE'}</em>
            <code>{candidate.cwd ?? candidate.workspace ?? ''}</code>
          </label>
        ))}
        {candidates.length === 0 && <div className="ion-empty-state is-ok">NO SAFE DEV SERVER CLEANUP CANDIDATES</div>}
      </div>
    </section>
  );
}

function SecuritySummaryPanel({ model }: { model: NonNullable<IonCockpitViewModel['system_diagnostics']> }) {
  const security = model.security_summary ?? {};
  const redaction = model.redaction_summary ?? {};
  return (
    <section className="ion-panel">
      <div className="ion-section-title">SECURITY POSTURE</div>
      <div className="ion-system-mini-grid">
        <Fact label="auth configured" value={yesNo(security.auth_configured)} />
        <Fact label="session source" value={titleCase(security.session_secret_source ?? 'unknown')} />
        <Fact label="invite tokens" value={String(security.invite_token_count ?? 0)} />
        <Fact label="google oauth" value={yesNo(security.google_oauth_configured)} />
        <Fact label="same origin" value={yesNo(security.same_origin_mutation_required)} />
        <Fact label="local-control gaps" value={String(security.unauthenticated_local_control_route_count ?? 0)} />
        <Fact label="token values" value={security.token_values_emitted ? 'EMITTED' : 'BLOCKED'} />
        <Fact label="secret values" value={security.secret_values_emitted ? 'EMITTED' : 'BLOCKED'} />
        <Fact label="redaction" value={redaction.command_redaction_enabled ? 'enabled' : 'unknown'} />
        <Fact label="redacted commands" value={String(redaction.redacted_process_command_count ?? 0)} />
      </div>
      <div className="ion-system-list">
        {(security.findings ?? []).map((finding) => (
          <article className={`ion-runtime-card is-${finding.severity}`} key={finding.id}>
            <div className="ion-runtime-card-head"><span>{finding.severity}</span><b>{finding.title}</b></div>
            <p>{finding.detail}</p>
          </article>
        ))}
        {(security.findings ?? []).length === 0 && <div className="ion-empty-state is-ok">NO ACTIVE SECURITY FINDING</div>}
      </div>
    </section>
  );
}

function ServiceHealthPanel({ model }: { model: NonNullable<IonCockpitViewModel['system_diagnostics']> }) {
  const health = model.service_health ?? {};
  return (
    <section className="ion-panel">
      <div className="ion-section-title">SERVICE HEALTH</div>
      <div className="ion-system-mini-grid">
        <Fact label="verdict" value={titleCase(health.verdict ?? 'unknown')} />
        <Fact label="services" value={String(health.service_count ?? health.services?.length ?? 0)} />
        <Fact label="required issues" value={String(health.required_issue_count ?? 0)} />
        <Fact label="warnings" value={String(health.warning_count ?? 0)} />
      </div>
      <div className="ion-system-service-list">
        {(health.services ?? []).map((service) => (
          <article className={`ion-system-service-row is-${service.severity}`} key={service.id ?? service.unit}>
            <span>{service.active ? 'ACTIVE' : 'DOWN'}</span>
            <b>{service.label ?? service.id}</b>
            <small>{service.unit}</small>
            <em>{service.critical ? 'CRITICAL' : 'OPTIONAL'}</em>
            <code>{service.finding ?? service.status}</code>
          </article>
        ))}
        {(health.services ?? []).length === 0 && <div className="ion-empty-state">NO SERVICE HEALTH MODEL</div>}
      </div>
    </section>
  );
}

function RouteMatrixPanel({ rows }: { rows: NonNullable<IonCockpitViewModel['system_diagnostics']>['route_matrix'] }) {
  return (
    <section className="ion-panel">
      <div className="ion-section-title">ROUTE MATRIX</div>
      <div className="ion-system-table-wrap">
        <table className="ion-system-table">
          <thead><tr><th>Route</th><th>Class</th><th>Auth</th><th>Origin</th><th>Confirm</th><th>Policy</th></tr></thead>
          <tbody>
            {(rows ?? []).map((row) => (
              <tr key={`${row.method}-${row.path}`}>
                <td><b>{row.method}</b><small>{row.path}</small></td>
                <td>{titleCase(row.route_class)}</td>
                <td>{yesNo(row.auth_required)}</td>
                <td>{row.same_origin_required ? 'SAME' : 'READ'}</td>
                <td>{row.confirmation_required ? 'YES' : 'NO'}</td>
                <td>{titleCase(row.policy_projection)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function DevServerCard({
  server,
  candidate,
  selected,
  busy,
  onStop,
  onToggle,
}: {
  server: IonSystemDiagnosticsDevServer;
  candidate?: IonSystemDiagnosticsCleanupCandidate;
  selected: boolean;
  busy: boolean;
  onStop: () => void;
  onToggle: () => void;
}) {
  const probe = server.http_probe;
  const canOpen = Boolean(probe?.serves_http && probe.url);
  const canQueueStop = Boolean(candidate);
  const eligibility = candidate?.action_eligibility ?? server.action_eligibility;
  const reasons = eligibility?.reasons ?? [];
  return (
    <article className={`ion-system-dev-card ${probe?.serves_http ? 'is-live' : 'is-unverified'} ${server.protected ? 'is-protected' : ''}`}>
      <div className="ion-system-dev-card-head">
        <div>
          <span className="ion-system-dev-port">:{server.port}</span>
          <b>{serverTitle(server)}</b>
          <small>{server.package_name && probe?.title ? probe.title : compactPath(server.cwd ?? server.package_path)}</small>
        </div>
        <div className="ion-system-dev-actions">
          {canQueueStop ? (
            <label className="ion-system-dev-select">
              <input type="checkbox" checked={selected} disabled={busy} onChange={onToggle} />
              <span>SELECT</span>
            </label>
          ) : null}
          {canQueueStop ? <button className="ion-system-stop-inline" type="button" disabled={busy} onClick={onStop}>STOP</button> : null}
          <button type="button" disabled={!canOpen} onClick={() => openServer(probe?.url)}>{canOpen ? 'OPEN' : 'NO HTTP'}</button>
        </div>
      </div>
      <div className="ion-system-dev-meta">
        <span>{titleCase(server.workspace)}</span>
        <span>{titleCase(server.framework)}</span>
        <span>{probeLabel(server)}</span>
        <span>{server.pid ? `PID ${server.pid}` : 'NO PID'}</span>
        <span>{age(server.elapsed_seconds)}</span>
        <span>{Math.round((server.rss_kb ?? 0) / 1024)} MB</span>
        <span className={canQueueStop ? 'is-actionable' : server.protected ? 'is-protected' : 'is-open'}>{eligibilityLabel(server, candidate)}</span>
        <span>{titleCase(server.confidence)}</span>
      </div>
      <code>{compactPath(server.cwd ?? server.package_path ?? server.command)}{reasons.length ? ` / ${reasons.join(', ')}` : ''}</code>
    </article>
  );
}

function Fact({ label, value }: { label: string; value: string }) {
  return <div className="ion-system-fact"><span>{label}</span><b>{value}</b></div>;
}

function ProcessTable({ rows }: { rows: NonNullable<IonCockpitViewModel['system_diagnostics']>['top_processes'] }) {
  return (
    <div className="ion-system-table-wrap">
      <table className="ion-system-table">
        <thead><tr><th>PID</th><th>Name</th><th>CPU</th><th>RAM</th><th>Age</th><th>Scope</th></tr></thead>
        <tbody>
          {(rows ?? []).map((row) => (
            <tr key={row.pid}>
              <td>{row.pid}</td>
              <td><b>{row.name}</b><small>{row.cwd ?? row.command}</small></td>
              <td>{(row.cpu_percent ?? 0).toFixed(1)}%</td>
              <td>{Math.round((row.rss_kb ?? 0) / 1024)} MB</td>
              <td>{age(row.elapsed_seconds)}</td>
              <td>{row.protected ? 'PROTECTED' : row.dev_server ? titleCase(row.framework ?? 'dev') : row.workspace}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function PortTable({ rows }: { rows: NonNullable<IonCockpitViewModel['system_diagnostics']>['ports'] }) {
  return (
    <div className="ion-system-table-wrap">
      <table className="ion-system-table">
        <thead><tr><th>Port</th><th>Process</th><th>Workspace</th><th>Path</th><th>State</th></tr></thead>
        <tbody>
          {(rows ?? []).map((row) => (
            <tr key={`${row.protocol}-${row.port}-${row.pid ?? 'none'}`}>
              <td>{row.port}</td>
              <td><b>{row.process_name ?? 'unknown'}</b><small>{row.pid ? `pid ${row.pid}` : 'no pid'}</small></td>
              <td>{row.workspace}</td>
              <td>{compactPath(row.cwd ?? row.local_address)}</td>
              <td>{row.dev_server ? titleCase(row.framework ?? 'dev') : row.protected ? 'PROTECTED' : row.cleanup_candidate ? 'CLEANUP' : 'OPEN'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
