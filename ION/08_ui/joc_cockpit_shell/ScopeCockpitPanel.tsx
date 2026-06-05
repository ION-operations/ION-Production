import { useEffect, useMemo, useState, type ReactNode } from 'react';
import {
  AuthorityIcon,
  EvidenceIcon,
  GraphIcon,
  QueueIcon,
  ReceiptIcon,
  RouteIcon,
  SourceIcon,
  StatusIcon,
  WorkSurfaceIcon,
} from './icons';

type ScopeLens = 'objective' | 'context' | 'graph' | 'scheduler' | 'proof' | 'raw';

export function ScopeCockpitPanel({ onRuntimeRefresh }: { onRuntimeRefresh?: () => void }) {
  const [model, setModel] = useState<Record<string, unknown> | null>(null);
  const [threadId, setThreadId] = useState('');
  const [requestState, setRequestState] = useState<{ ok: boolean; finding?: string }>({ ok: true });
  const [loading, setLoading] = useState(true);
  const [activeLens, setActiveLens] = useState<ScopeLens>('objective');
  const [rawInspectorOpen, setRawInspectorOpen] = useState(false);

  const parseThreadIdFromHash = (): string => {
    if (typeof window === 'undefined') return '';
    const nextHash = (window.location.hash || '').replace(/^#/, '');
    const [page, query = ''] = nextHash.split('?', 2);
    if (page !== 'scope') {
      return '';
    }
    return new URLSearchParams(query).get('thread_id') || '';
  };

  const fetchScopeModel = async (selectedThreadId: string) => {
    setLoading(true);
    setRequestState({ ok: true });
    try {
      const query = selectedThreadId ? `?thread_id=${encodeURIComponent(selectedThreadId)}` : '';
      const response = await fetch(`/cockpit/scope/model.json${query}`, {
        headers: { Accept: 'application/json' },
      });
      const result = await response.json().catch(() => ({
        ok: false,
        finding: `scope_model_invalid_json_${response.status}`,
      }));
      if (!response.ok || typeof result !== 'object' || result === null || result.ok !== true) {
        const permissionFinding = response.status === 401 || response.status === 403
          ? `scope_model_permission_required_${response.status}`
          : undefined;
        setRequestState({
          ok: false,
          finding: permissionFinding || (result as { finding?: string }).finding || `scope_model_http_${response.status}`,
        });
      }
      setModel(typeof result === 'object' && result !== null ? (result as Record<string, unknown>) : null);
      if (onRuntimeRefresh && typeof onRuntimeRefresh === 'function') {
        onRuntimeRefresh();
      }
    } catch (error) {
      setRequestState({ ok: false, finding: error instanceof Error ? error.message : 'scope_model_fetch_failed' });
      setModel(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const syncFromHash = () => {
      setThreadId(parseThreadIdFromHash());
    };
    syncFromHash();
    window.addEventListener('hashchange', syncFromHash);
    return () => {
      window.removeEventListener('hashchange', syncFromHash);
    };
  }, []);

  useEffect(() => {
    void fetchScopeModel(threadId);
  }, [threadId]);

  const selectedThreadId = text(model?.selected_thread_id) || threadId;
  const summary = model && typeof model === 'object' ? (model.summary as Record<string, unknown> | undefined) : undefined;
  const objectiveSpine = asRecord(model?.objective_spine);
  const scopeStack = asList(model?.scope_stack);
  const scheduler = asRecord(model?.scheduler_projection);
  const threadGraph = asRecord(model?.thread_operational_graph);
  const timelineEvents = asList(model?.timeline ?? model?.timeline_events);
  const gates = asList(model?.gates);
  const changeLedger = asList(model?.change_ledger);
  const contextSegments = asList(model?.context_matryoshka ?? threadGraph.context_segments);
  const proofProjection = asRecord(model?.proof_projection ?? threadGraph.proof_projection);
  const phaseRail = asRecord(objectiveSpine.current_phase ?? model?.phase_rail);
  const progressLanes = asList(model?.progress_lanes ?? objectiveSpine.progress_lanes);
  const policy = asList(objectiveSpine?.policy);
  const graphMessages = asList(threadGraph.messages);
  const acceptedBoundary = asRecord(threadGraph.accepted_state_boundary);
  const modelReady = Boolean(model && Object.keys(model).length);
  const statusLabel = loading ? 'loading' : requestState.ok ? (modelReady ? 'ready' : 'empty') : 'blocked';
  const statusText = requestState.ok
    ? (loading ? 'loading scope model' : (modelReady ? 'scope projection ready' : 'scope model empty'))
    : requestState.finding || 'scope model unavailable';
  const lensItems = useMemo<Array<{ id: ScopeLens; label: string; icon: ReactNode; count: string }>>(() => ([
    { id: 'objective', label: 'Objective', icon: <RouteIcon />, count: text(progressLanes.length, '0') },
    { id: 'context', label: 'Context', icon: <SourceIcon />, count: text(contextSegments.length, '0') },
    { id: 'graph', label: 'Graph', icon: <GraphIcon />, count: text(graphMessages.length, '0') },
    { id: 'scheduler', label: 'Scheduler', icon: <QueueIcon />, count: text((scheduler.summary as Record<string, unknown> | undefined)?.ready, '0') },
    { id: 'proof', label: 'Proof', icon: <ReceiptIcon />, count: text((proofProjection as Record<string, unknown>).proof_ref_count, '0') },
    { id: 'raw', label: 'Raw', icon: <EvidenceIcon />, count: modelReady ? '1' : '0' },
  ]), [contextSegments.length, graphMessages.length, modelReady, progressLanes.length, proofProjection, scheduler.summary]);

  return (
    <section className="ion-scope-cockpit-panel" aria-label="Scope cockpit work surface">
      <header className="ion-scope-top-bar">
        <div className="ion-scope-title">
          <div className="ion-section-title">SCOPE COCKPIT</div>
          <h2>{text(objectiveSpine.objective?.statement, 'Scope objective unavailable')}</h2>
          <p>Scope objective, context, graph, scheduler, proof, and raw inspection are separated into local lenses. Scheduler and graph state remain projections.</p>
        </div>
        <div className="ion-scope-top-actions">
          <ScopeStatusBadge status={statusLabel} label={statusText} />
          <button
            className="ion-scope-refresh"
            onClick={() => void fetchScopeModel(threadId)}
            type="button"
          >
            <StatusIcon /> {loading ? 'REFRESHING' : 'REFRESH'}
          </button>
        </div>
      </header>

      <div className="ion-scope-proof-strip" aria-label="Current scope proof">
        <Metric label="schema" value={text(model?.schema_id, 'ion.scope_cockpit_projection.v1')} />
        <Metric label="selected thread" value={selectedThreadId || 'auto-selected'} />
        <Metric label="threads" value={text(summary?.thread_count, '0')} />
        <Metric label="scheduler candidates" value={text(summary?.scheduler_candidate_count, '0')} />
        <Metric label="proof state" value={text(summary?.proof_state, 'unknown')} />
      </div>

      {loading ? <ScopeStatePanel state="loading" message="Loading scope projection." /> : null}
      {!loading && !requestState.ok ? <ScopeStatePanel state="blocked" message={requestState.finding || 'Scope projection unavailable.'} /> : null}
      {!loading && requestState.ok && !modelReady ? <ScopeStatePanel state="empty" message="No scope model is available yet." /> : null}

      <div className="ion-scope-work-surface">
        <nav className="ion-scope-left-rail" aria-label="Scope work lenses">
          {lensItems.map((item) => (
            <button
              aria-label={item.label}
              className={activeLens === item.id ? 'is-active' : undefined}
              key={item.id}
              onClick={() => setActiveLens(item.id)}
              title={item.label}
              type="button"
            >
              {item.icon}
              <span>{item.label}</span>
              <b>{item.count}</b>
            </button>
          ))}
        </nav>

        <main className="ion-scope-main-surface" aria-label="Scope main work surface">
          <div className="ion-scope-lens-tabs" role="tablist" aria-label="Scope work surface lenses">
            {lensItems.map((item) => (
              <button
                aria-selected={activeLens === item.id}
                className={activeLens === item.id ? 'is-active' : undefined}
                key={item.id}
                onClick={() => setActiveLens(item.id)}
                role="tab"
                type="button"
              >
                {item.label}
              </button>
            ))}
          </div>

          {activeLens === 'objective' ? (
            <section className="ion-scope-lens-body" aria-label="Objective lens">
              <div className="ion-grid-3">
                <article className="ion-panel" aria-label="Objective Spine">
                  <div className="ion-section-title">Objective Spine</div>
                  <p>{text(objectiveSpine.objective?.statement, 'Scope objective unavailable.')}</p>
                  <p>{text(objectiveSpine.objective?.why_now, 'Objective rationale unavailable.')}</p>
                </article>
                <article className="ion-panel" aria-label="Phase Rail">
                  <div className="ion-section-title">Phase Rail</div>
                  <p>{text(phaseRail.label, 'phase unknown')}</p>
                  <p>{text(objectiveSpine.trajectory?.summary, 'trajectory unavailable.')}</p>
                </article>
                <article className="ion-panel" aria-label="Next Lawful Move">
                  <div className="ion-section-title">Next Lawful Move</div>
                  <p>{text(objectiveSpine.next_lawful_move?.label, 'No next lawful move yet')}</p>
                  <p>{text(objectiveSpine.next_lawful_move?.why, 'no move rationale yet')}</p>
                </article>
              </div>
              <div className="ion-scope-card-grid">
                {progressLanes.map((laneRow, laneIndex) => (
                  <ScopeLane
                    label={text((laneRow as Record<string, unknown>).label)}
                    value={safeNumber((laneRow as Record<string, unknown>).value)}
                    basis={text(JSON.stringify((laneRow as Record<string, unknown>).basis || {}), '[]')}
                    key={text((laneRow as Record<string, unknown>).label, `lane-${laneIndex}`)}
                  />
                ))}
                {progressLanes.length === 0 ? <p className="ion-empty-state">no progress lanes available</p> : null}
              </div>
              <ListBlock title="Scope Stack" values={scopeStack.map((scopeRow, index) => {
                const scopeRecord = asRecord(scopeRow);
                return `${text(scopeRecord.scope_type)} / ${text(scopeRecord.title, `scope-${index}`)} - ${text(scopeRecord.summary)}`;
              })} empty="No scope stack available." />
            </section>
          ) : null}

          {activeLens === 'context' ? (
            <section className="ion-scope-lens-body" aria-label="Context lens">
              <div className="ion-scope-card-grid">
                {contextSegments.map((segment, index) => {
                  const segmentRecord = asRecord(segment);
                  return (
                    <article className="ion-panel" key={text(segmentRecord.segment_id, `segment-${index}`)}>
                      <div className="ion-section-title">{text(segmentRecord.label, 'Context Segment')}</div>
                      <b>{text(segmentRecord.window_class, 'window')}</b>
                      <p>{text(segmentRecord.summary)}</p>
                    </article>
                  );
                })}
                {contextSegments.length === 0 ? <p className="ion-empty-state">no context segments yet</p> : null}
              </div>
              <ListBlock title="Policy" values={policy.map((policyLine) => text(policyLine))} empty="No policy lines recorded." />
            </section>
          ) : null}

          {activeLens === 'graph' ? (
            <section className="ion-scope-lens-body" aria-label="Graph lens">
              <div className="ion-grid-3">
                <Metric label="thread lifecycle" value={text(asRecord(threadGraph.thread_lifecycle).state, 'unknown')} />
                <Metric label="messages" value={text(graphMessages.length, '0')} />
                <Metric label="selected thread" value={selectedThreadId || 'latest available thread'} />
              </div>
              <ListBlock
                title="Thread Workroom"
                values={graphMessages.slice(0, 18).map((message, index) => {
                  const messageRecord = asRecord(message);
                  return `${text(messageRecord.from_role, 'role')} / ${text(messageRecord.message_kind, 'message')} / ${text(messageRecord.created_at, `message-${index}`)}`;
                })}
                empty="No graph messages available."
              />
            </section>
          ) : null}

          {activeLens === 'scheduler' ? (
            <section className="ion-scope-lens-body" aria-label="Scheduler lens">
              <div className="ion-grid-3">
                <Metric label="ready" value={text((scheduler.summary as Record<string, unknown> | undefined)?.ready, '0')} />
                <Metric label="blocked" value={text((scheduler.summary as Record<string, unknown> | undefined)?.blocked, '0')} />
                <Metric label="in flight" value={text((scheduler.summary as Record<string, unknown> | undefined)?.in_flight, '0')} />
                <Metric label="selected candidate" value={text(scheduler.selected_candidate && (scheduler.selected_candidate as Record<string, unknown>).candidate_title)} />
                <Metric label="carrier binding" value={text(scheduler.selected_candidate && (scheduler.selected_candidate as Record<string, unknown>).selected_carrier, 'unknown')} />
                <Metric label="scope fallback" value={text(scheduler.scope_fallback, 'none')} />
              </div>
              <ListBlock
                title="Scheduler Projection"
                values={asList(scheduler.candidates).slice(0, 16).map((candidate, index) => {
                  const row = asRecord(candidate);
                  return `${text(row.candidate_title, `candidate-${index}`)} / ${text(row.state, 'state unknown')}`;
                })}
                empty="No scheduler candidates available."
              />
            </section>
          ) : null}

          {activeLens === 'proof' ? (
            <section className="ion-scope-lens-body" aria-label="Proof lens">
              <div className="ion-grid-3">
                <Metric label="accepted boundary" value={text(acceptedBoundary.state, 'candidate evidence only')} />
                <Metric label="proof refs" value={text((proofProjection as Record<string, unknown>).proof_ref_count, '0')} />
                <Metric label="proof state" value={text((proofProjection as Record<string, unknown>).proof_state, 'unknown')} />
              </div>
              <article className="ion-panel" aria-label="Accepted-state boundary">
                <div className="ion-section-title">Accepted-State Boundary</div>
                <p>{text(acceptedBoundary.summary, 'accepted state must be explicitly declared upstream')}</p>
              </article>
              <div className="ion-scope-card-grid">
                {gates.map((entry, index) => {
                  const gate = asRecord(entry);
                  return (
                    <article className="ion-receipt-card" key={text(gate.gate_id, `gate-${index}`)}>
                      <div className="ion-receipt-head">
                        <span>{text(gate.gate_type, 'gate')}</span>
                        <b>{text(gate.state, 'pending')}</b>
                      </div>
                      <div className="ion-receipt-verdict">{text(gate.summary)}</div>
                    </article>
                  );
                })}
                {gates.length === 0 ? <p className="ion-empty-state">no active gates yet</p> : null}
              </div>
              <div className="ion-scope-card-grid">
                {changeLedger.map((entry, index) => {
                  const change = asRecord(entry);
                  return (
                    <article className="ion-receipt-card" key={text(change.change_id, `change-${index}`)}>
                      <div className="ion-receipt-head">
                        <span>{text(change.change_type, 'change')}</span>
                        <b>{text(change.impact, 'none')}</b>
                      </div>
                      <div className="ion-receipt-verdict">{text(change.reason, 'no impact summary')}</div>
                    </article>
                  );
                })}
                {changeLedger.length === 0 ? <p className="ion-empty-state">no change ledger entries yet</p> : null}
              </div>
            </section>
          ) : null}

          {activeLens === 'raw' ? (
            <section className="ion-scope-lens-body" aria-label="Raw lens">
              <article className="ion-panel">
                <div className="ion-section-title">Raw Model Inspector</div>
                <p>Raw JSON is available only inside this lens or the explicit inspector toggle.</p>
                <pre className="ion-scope-raw-model">
                  {model ? JSON.stringify(model, null, 2) : (requestState.ok ? 'no model yet' : requestState.finding)}
                </pre>
              </article>
            </section>
          ) : null}
        </main>

        <aside className="ion-scope-right-inspector" aria-label="Scope proof inspector">
          <div className="ion-scope-inspector-head">
            <div>
              <div className="ion-section-title">INSPECTOR</div>
              <b>{activeLens}</b>
            </div>
            <AuthorityIcon />
          </div>
          <Metric label="thread" value={selectedThreadId || 'latest available thread'} />
          <Metric label="proof state" value={text((proofProjection as Record<string, unknown>).proof_state, 'unknown')} />
          <Metric label="accepted state" value={text(acceptedBoundary.state, 'candidate evidence only')} />
          <button
            className={rawInspectorOpen ? 'ion-scope-inspector-toggle is-active' : 'ion-scope-inspector-toggle'}
            onClick={() => setRawInspectorOpen((open) => !open)}
            type="button"
          >
            <EvidenceIcon /> {rawInspectorOpen ? 'HIDE RAW' : 'OPEN RAW'}
          </button>
          {rawInspectorOpen ? (
            <pre className="ion-scope-raw-model is-inspector">
              {model ? JSON.stringify(model, null, 2) : (requestState.ok ? 'no model yet' : requestState.finding)}
            </pre>
          ) : null}
        </aside>
      </div>

      <section className="ion-scope-bottom-timeline" aria-label="Scope four-lane timeline">
        <div className="ion-section-title">Four-Lane Timeline</div>
        {timelineEvents.map((event, index) => {
          const eventRecord = asRecord(event);
          return (
            <span key={text(eventRecord.lane, `lane-${index}`)}>
              {text(eventRecord.lane)} / {text(eventRecord.label)} — {text(eventRecord.summary)}
            </span>
          );
        })}
        {timelineEvents.length === 0 ? <span>No timeline events available.</span> : null}
      </section>
    </section>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="ion-metric">
      <span>{label}</span>
      <b>{value}</b>
    </div>
  );
}

function ScopeLane({ label, value, basis }: { label: string; value: number; basis: string }) {
  return (
    <div className="ion-scope-lane" aria-label="Scope progress lane">
      <div className="ion-section-title">{label || 'lane'}</div>
      <b>{value}%</b>
      <span style={{ width: `${Math.max(0, Math.min(value, 100))}%` }} />
      <p>{basis}</p>
    </div>
  );
}

function ScopeStatusBadge({ status, label }: { status: string; label: string }) {
  return <span className={`ion-scope-status is-${status}`}>{label}</span>;
}

function ScopeStatePanel({ state, message }: { state: string; message: string }) {
  return (
    <div className={`ion-scope-state is-${state}`} role={state === 'blocked' ? 'alert' : 'status'}>
      <WorkSurfaceIcon />
      <span>{message}</span>
    </div>
  );
}

function ListBlock({ title, values, empty }: { title: string; values: string[]; empty: string }) {
  return (
    <article className="ion-panel">
      <div className="ion-section-title">{title}</div>
      <div className="ion-blocked-list">
        {values.length ? values.map((value, index) => <span key={`${title}-${index}`}>{value}</span>) : <span>{empty}</span>}
      </div>
    </article>
  );
}

function text(value: unknown, fallback = 'na'): string {
  if (value === null || value === undefined || value === false) {
    return fallback;
  }
  if (value === 0) return '0';
  if (typeof value === 'boolean') {
    return value ? 'true' : 'false';
  }
  if (typeof value === 'number') {
    return String(value);
  }
  if (typeof value === 'string') {
    return value || fallback;
  }
  if (typeof value === 'object') {
    return fallback;
  }
  return String(value);
}

function asRecord(value: unknown): Record<string, unknown> {
  if (value && typeof value === 'object' && !Array.isArray(value)) {
    return value as Record<string, unknown>;
  }
  return {};
}

function asList(value: unknown): unknown[] {
  return Array.isArray(value) ? value : [];
}

function safeNumber(value: unknown): number {
  const asText = text(value, '0');
  const maybeNumber = Number(asText);
  return Number.isFinite(maybeNumber) ? maybeNumber : 0;
}
