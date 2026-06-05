import { useState, type CSSProperties, type ReactNode } from 'react';
import type { IonCockpitViewModel } from './ionRuntimeCockpitTypes';
import {
  AuthorityIcon,
  BlockersIcon,
  BranchIcon,
  ChatIcon,
  CheckIcon,
  DomainsIcon,
  EvidenceIcon,
  GraphIcon,
  QueueIcon,
  ReceiptIcon,
  RouteIcon,
  SourceIcon,
  StatusIcon,
  WorkSurfaceIcon,
} from './icons';

type AnyRecord = Record<string, unknown>;
type DomainWeaverLens = 'map' | 'team' | 'signals' | 'timeline' | 'proof' | 'context' | 'actions';
type DomainWeaverInspectorMode = 'selected' | 'evidence' | 'context' | 'authority' | 'raw';
type WeaverTone = 'ready' | 'working' | 'blocked' | 'watch';
type TeamWorker = {
  id: string;
  label: string;
  stage: string;
  status: string;
  detail: string;
  requestId: string;
  returnPath: string;
  proofStatus: string;
  tone: WeaverTone;
};
type WeaverEvent = {
  id: string;
  label: string;
  meta: string;
  detail: string;
  lane: string;
  tone: WeaverTone;
};
type DomainCluster = {
  id: string;
  label: string;
  status: string;
  agentCount: string;
  x: number;
  y: number;
  tone: WeaverTone;
};
type RecoveryEventInputs = {
  faninRetryGate: AnyRecord;
  modelEndpointBlocked: boolean;
  modelEndpointReproofReady: boolean;
  modelEndpointReceiptPath: string;
  noCarrierMessagesProjected: boolean;
  nextUiPacket: AnyRecord;
  operatorFeedbackPath: string;
  operatorRejected: boolean;
  routeExecutionSummary: AnyRecord;
  visualProofReady: boolean;
};
const WRITE_CONFIRMATION_TOKEN = 'ION_BOUNDED_WRITE_CONFIRMED';

export function DomainWeaverCockpitPanel({
  runtime,
  onRuntimeRefresh,
}: {
  runtime: IonCockpitViewModel;
  onRuntimeRefresh?: () => void;
}) {
  const [actionBusy, setActionBusy] = useState<string | null>(null);
  const [actionResult, setActionResult] = useState<AnyRecord>({});
  const [activeLens, setActiveLens] = useState<DomainWeaverLens>('map');
  const [leftDrawerOpen, setLeftDrawerOpen] = useState(defaultSurfacePanelOpen);
  const [rightInspectorOpen, setRightInspectorOpen] = useState(defaultSurfacePanelOpen);
  const [inspectorMode, setInspectorMode] = useState<DomainWeaverInspectorMode>('selected');
  const [selectedWorkerId, setSelectedWorkerId] = useState('');
  const [selectedEventId, setSelectedEventId] = useState('');
  const agentControl = asRecord(runtime.agent_control_plane);
  const domainWeaver = asRecord(agentControl.domain_weaver);
  const summary = asRecord(domainWeaver.summary);
  const operatingLoop = asRecord(domainWeaver.operating_loop);
  const loopSummary = asRecord(operatingLoop.summary);
  const queueGovernance = asRecord(domainWeaver.queue_governance);
  const queueSummary = asRecord(queueGovernance.summary);
  const queueGovernor = asRecord(queueGovernance.queue_governor);
  const queueDogfood = asRecord(queueGovernance.queue_governor_dogfood);
  const queueDogfoodSummary = asRecord(queueDogfood.summary);
  const queueDogfoodScenarios = records(queueDogfood.scenarios);
  const uiDevelopment = asRecord(domainWeaver.ui_development);
  const uiSummary = asRecord(uiDevelopment.summary);
  const surfaceQuality = asRecord(uiDevelopment.surface_quality);
  const surfaceQualitySummary = asRecord(surfaceQuality.summary);
  const knownGoodSurfaces = records(surfaceQuality.known_good_surfaces);
  const nativeCapability = asRecord(uiDevelopment.native_ui_development);
  const specialistRoute = records(nativeCapability.specialist_route);
  const contextRefs = records(nativeCapability.context_refs);
  const routeExecutionGate = asRecord(uiDevelopment.route_execution_gate);
  const routeExecutionSummary = asRecord(routeExecutionGate.summary);
  const routeProofRows = records(routeExecutionGate.proof_rows);
  const faninRetryGate = asRecord(uiDevelopment.ui_specialist_fanin_retry_gate);
  const nextUiPacket = asRecord(uiDevelopment.next_packet);
  const visualStewardshipReview = asRecord(uiDevelopment.ui_visual_stewardship_review);
  const sourceVisualStewardshipReview = asRecord(nextUiPacket.source_visual_stewardship_review);
  const sourceMockProof = asRecord(nextUiPacket.source_semantic_redesign_mock_proof);
  const nextUiPacketAcceptanceGates = strings(nextUiPacket.acceptance_gates);
  const nextUiPacketBlockedUntil = strings(nextUiPacket.blocked_until_implementation_packet);
  const nextUiPacketContextRefs = strings(nextUiPacket.context_refs);
  const sourceFaninRetryGate = asRecord(nextUiPacket.source_fanin_retry_gate);
  const operatorRejected = uiSummary.operator_rejected_current_ui === true || surfaceQualitySummary.operator_rejected_current_ui === true;
  const visualProofReady = uiSummary.visual_proof_ready === true || surfaceQualitySummary.visual_smoke_ok === true;
  const modelEndpointReproofReady = summary.visual_proof_live_hydration_reproof_ready === true
    || visualStewardshipReview.model_endpoint_live_hydration_proved === true;
  const modelEndpointBlocked = !modelEndpointReproofReady && (visualStewardshipReview.model_endpoint_blocked === true
    || sourceVisualStewardshipReview.model_endpoint_blocked === true
    || sourceMockProof.model_degraded_state_required === true
    || uiSummary.ui_visual_model_endpoint_blocked === true);
  const modelEndpointReceiptPath = text(
    summary.visual_proof_live_hydration_reproof_path,
    visualStewardshipReview.model_endpoint_receipt_path,
    sourceVisualStewardshipReview.model_endpoint_receipt_path,
    'ION/05_context/current/domain_weaver/visual_smoke/DOMAIN_WEAVER_UI_MODEL_ENDPOINT_HANG_20260601_LOCAL.json',
  );
  const operatorFeedbackPath = text(surfaceQualitySummary.operator_feedback_path, 'ION/05_context/current/domain_weaver/operator_feedback/LATEST_UI_OPERATOR_FEEDBACK.candidate.json');
  const readinessLevels = entries(uiDevelopment.readiness_levels);
  const liveCarrierBinding = asRecord(domainWeaver.live_carrier_binding);
  const workRequestTemplates = records(liveCarrierBinding.work_request_templates);
  const liveReturnMonitor = asRecord(domainWeaver.live_return_monitor);
  const observedReturns = records(liveReturnMonitor.observed_returns);
  const faninSettlement = asRecord(domainWeaver.live_fanin_settlement);
  const settlementRecords = records(faninSettlement.return_records);
  const semanticSettlement = asRecord(domainWeaver.live_fanin_semantic_settlement);
  const semanticRecords = records(semanticSettlement.semantic_return_records);
  const promotionReview = asRecord(domainWeaver.promotion_review);
  const promotionGate = asRecord(domainWeaver.promotion_gate);
  const promotionSummary = asRecord(promotionReview.summary);
  const gateSummary = asRecord(promotionGate.summary);
  const operatorActionHistory = asRecord(domainWeaver.operator_action_history);
  const operatorActionRows = records(operatorActionHistory.records);
  const operatorActionSummary = asRecord(operatorActionHistory.summary);
  const domains = records(domainWeaver.domains).length ? records(domainWeaver.domains) : records(agentControl.domains);
  const agents = records(domainWeaver.agents);
  const edges = records(domainWeaver.edges);
  const blockers = records(operatingLoop.blockers);
  const loopSteps = records(operatingLoop.loop);
  const loopPackets = records(operatingLoop.next_packets);
  const queuePackets = records(queueGovernance.next_packets);
  const nextPackets = [
    ...loopPackets,
    ...queuePackets.filter((packet) => {
      const packetId = text(packet.packet_id);
      return packetId && !loopPackets.some((row) => text(row.packet_id) === packetId);
    }),
  ];
  const queueFindings = records(queueGovernance.findings);
  const flaggedRequests = records(queueGovernance.flagged_requests);
  const statusCounts = entries(queueGovernance.status_counts);
  const laneCounts = entries(queueGovernance.lane_counts);
  const workLaneCounts = entries(queueGovernance.work_lane_counts);
  const uiSurfaces = records(uiDevelopment.surfaces);
  const chatgptBrowserMcp = runtime.chatgpt_browser_mcp;
  const carrierMessages = records(chatgptBrowserMcp?.latest_carrier_messages).slice(-8).reverse();
  const noCarrierMessagesProjected = carrierMessages.length === 0;
  const activeQueueRuns = records(asRecord(chatgptBrowserMcp?.codex_queue_runner).latest_runs)
    .filter((request) => text(request.request_id).includes('domain_weaver'))
    .slice(0, 8);
  const receipts = records(runtime.receipts)
    .filter((receipt) => {
      const haystack = `${text(receipt.path)} ${text(receipt.name)} ${text(receipt.authority_class)}`.toLowerCase();
      return haystack.includes('domain_weaver') || haystack.includes('domainweaver') || haystack.includes('weave');
    })
    .slice(0, 12);
  const domainRows = domains.slice(0, 18);
  const routeProofCompleteCount = Number(text(routeExecutionSummary.proof_complete_count, '0'));
  const routeDeclaredCount = Number(text(routeExecutionSummary.declared_route_count, '0'));
  const routeExecutionReady = routeExecutionSummary.route_execution_ready === true
    || (routeDeclaredCount > 0 && routeProofCompleteCount === routeDeclaredCount);
  const uiReady = text(uiDevelopment.status) === 'ui_development_ready';
  const actionPaths = strings(actionResult.evidence_paths);
  const actionReceipts = strings(actionResult.receipt_paths);
  const hasActionResult = Object.keys(actionResult).length > 0;
  const teamWorkers = buildTeamWorkers(specialistRoute, workRequestTemplates, observedReturns, settlementRecords, semanticRecords, routeProofRows);
  const currentWorker = teamWorkers.find((worker) => worker.id === selectedWorkerId) ?? teamWorkers[0];
  const domainClusters = buildDomainClusters(domainRows, agents);
  const activityEvents = buildWeaverEvents(operatorActionRows, observedReturns, semanticRecords, carrierMessages, blockers, {
    faninRetryGate,
    modelEndpointBlocked,
    modelEndpointReproofReady,
    modelEndpointReceiptPath,
    noCarrierMessagesProjected,
    nextUiPacket,
    operatorFeedbackPath,
    operatorRejected,
    routeExecutionSummary,
    visualProofReady,
  });
  const selectedEvent = activityEvents.find((event) => event.id === selectedEventId) ?? activityEvents[0];
  const eventLaneCounts = summarizeEventLanes(activityEvents);
  const proofRows = [
    ['returns', `${text(asRecord(liveReturnMonitor.summary).accepted_return_count, text(summary.live_return_accepted_count, '0'))}/${text(asRecord(liveReturnMonitor.summary).expected_return_count, text(summary.expected_return_count, '0'))}`],
    ['semantic', `${text(asRecord(semanticSettlement.summary).semantic_clean_return_count, text(summary.live_fanin_semantic_clean_return_count, '0'))}/${text(asRecord(semanticSettlement.summary).expected_return_count, text(summary.expected_return_count, '0'))}`],
    ['route proof', `${text(routeExecutionSummary.proof_complete_count, '0')}/${text(routeExecutionSummary.declared_route_count, '0')}`],
    ['fan-in gate', boolText(faninRetryGate.retry_gate_ready)],
    ['visual proof', boolText(visualProofReady)],
    ['operator', operatorRejected ? 'rejected' : 'not rejected'],
  ] as Array<[string, unknown]>;
  const selectWorker = (workerId: string) => {
    setSelectedWorkerId(workerId);
    const worker = teamWorkers.find((row) => row.id === workerId);
    const relatedEvent = worker ? activityEvents.find((event) => eventMatchesWorker(event, worker)) : undefined;
    if (relatedEvent) setSelectedEventId(relatedEvent.id);
  };
  const selectEvent = (eventId: string) => {
    setSelectedEventId(eventId);
    const event = activityEvents.find((row) => row.id === eventId);
    const relatedWorker = event ? teamWorkers.find((worker) => eventMatchesWorker(event, worker)) : undefined;
    if (relatedWorker) setSelectedWorkerId(relatedWorker.id);
    setInspectorMode('selected');
    setRightInspectorOpen(true);
  };
  const workSurfaceReadinessTokens = [
    'TOP_BAR',
    'LEFT_ICON_RAIL',
    'LEFT_DRAWER',
    'MAIN_WORK_SURFACE',
    'RIGHT_INSPECTOR',
    'RIGHT_ICON_RAIL',
    'BOTTOM_TIMELINE',
    'NEXT BOUNDED PACKETS',
    'PROMOTION / RECEIPT PROOF',
  ];

  async function runDomainWeaverAction(action: string) {
    if (actionBusy) return;
    setActionBusy(action);
    try {
      const response = await fetch('/cockpit/domain-weaver/action', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ action, confirmation: WRITE_CONFIRMATION_TOKEN }),
      });
      const parsed = await response.json().catch(() => ({
        ok: false,
        finding: 'invalid_json_response',
      }));
      const result: AnyRecord = {
        ...asRecord(parsed),
        http_status: response.status,
      };
      setActionResult(result);
      if (response.ok && result.ok !== false) {
        onRuntimeRefresh?.();
      }
    } catch (error) {
      setActionResult({
        ok: false,
        finding: 'request_failed',
        error: error instanceof Error ? error.name : 'unknown_error',
      });
    } finally {
      setActionBusy(null);
    }
  }

  return (
    <section className="ion-domain-weaver-panel" aria-label="Domain Weaver cockpit workbench">
      <header className="ion-domain-weaver-top-bar">
        <div className="ion-domain-weaver-title">
          <div className="ion-section-title">DOMAIN WEAVER</div>
          <h2>Activity City</h2>
          <p>Autonomous-team route, branch events, worker sync, proof classes, blockers, and next lawful action for /cockpit#weave.</p>
        </div>
        <div className="ion-domain-weaver-top-status">
          <StatusBadge ready={routeExecutionReady} label={routeExecutionReady ? 'route ready' : 'route blocked'} />
          <StatusBadge ready={false} label="candidate-only" />
          <StatusBadge ready={uiReady && !operatorRejected} label={uiReady && !operatorRejected ? 'surface ready' : 'surface rejected'} />
          <StatusBadge ready={visualProofReady} label={visualProofReady ? 'fresh visual proof' : 'visual proof pending'} />
          <StatusBadge ready={!operatorRejected} label={operatorRejected ? 'operator rejection visible' : 'operator proof clear'} />
          <StatusBadge ready={!modelEndpointBlocked} label={modelEndpointBlocked ? 'model endpoint degraded' : modelEndpointReproofReady ? 'endpoint reproof recorded' : 'model endpoint unproven'} />
          {onRuntimeRefresh ? (
            <button className="ion-domain-weaver-refresh" onClick={onRuntimeRefresh} type="button">
              <StatusIcon /> REFRESH
            </button>
          ) : null}
        </div>
        <div className="ion-domain-weaver-activity-contract-strip" data-activity-city-contract="operator_rejection hydration_evidence_only candidate_only next_lawful_action">
          <div className="is-blocked">
            <span>Operator</span>
            <b>{operatorRejected ? 'rejection active' : 'no rejection flag'}</b>
          </div>
          <div className="is-watch">
            <span>Hydration</span>
            <b>{modelEndpointReproofReady ? 'evidence only' : modelEndpointBlocked ? 'degraded evidence' : 'unproven'}</b>
          </div>
          <div className="is-working">
            <span>Posture</span>
            <b>candidate only</b>
          </div>
          <div className="is-ready">
            <span>Next</span>
            <b>{shortId(text(nextUiPacket.packet_id, 'bounded implementation preview'))}</b>
          </div>
        </div>
        {operatorRejected ? (
          <div className="ion-domain-weaver-rejection-evidence" role="status">
            <div>
              <div className="ion-section-title">ACTIVE OPERATOR REJECTION</div>
              <b>Current /cockpit#weave remains candidate-only until fresh visual proof supersedes the rejected surface.</b>
            </div>
            <code>{operatorFeedbackPath}</code>
          </div>
        ) : null}
        <div className={`ion-domain-weaver-model-evidence${modelEndpointBlocked ? ' is-blocked' : ' is-watch'}`} role="status">
          <div>
            <div className="ion-section-title">{modelEndpointBlocked ? 'MODEL ENDPOINT DEGRADED STATE' : 'MODEL ENDPOINT PROOF STATE'}</div>
            <b>{modelEndpointBlocked ? 'Model endpoint mock-gated: layout remains usable while /cockpit/model.json proof is pending.' : modelEndpointReproofReady ? 'Endpoint reproof recorded; operator rejection remains active until quality settlement.' : 'Model endpoint parity is not settlement proof until fresh visual proof records it.'}</b>
          </div>
          <code title={modelEndpointReceiptPath}>{modelEndpointBlocked ? `mock gate: ${shortPath(modelEndpointReceiptPath)}` : modelEndpointReproofReady ? `reproof: ${shortPath(modelEndpointReceiptPath)}` : shortPath(modelEndpointReceiptPath)}</code>
        </div>
      </header>

      <div
        className="ion-domain-weaver-work-surface"
        data-shell-zones={workSurfaceReadinessTokens.join(' ')}
      >
        <nav className="ion-domain-weaver-left-rail" aria-label="Domain Weaver work lenses">
          <button
            aria-label={leftDrawerOpen ? 'Hide left drawer' : 'Show left drawer'}
            className={`ion-domain-weaver-drawer-toggle${leftDrawerOpen ? ' is-active' : ''}`}
            onClick={() => setLeftDrawerOpen((open) => !open)}
            title="Lens drawer"
            type="button"
          >
            <QueueIcon />
            <span>Drawer</span>
          </button>
          {([
            ['map', <GraphIcon />, 'Activity'],
            ['team', <WorkSurfaceIcon />, 'Team'],
            ['signals', <ChatIcon />, 'Messages'],
            ['timeline', <BranchIcon />, 'Timeline'],
            ['proof', <ReceiptIcon />, 'Proof'],
            ['context', <SourceIcon />, 'Context'],
            ['actions', <BlockersIcon />, 'Actions'],
          ] as Array<[DomainWeaverLens, ReactNode, string]>).map(([lens, icon, label]) => (
            <button
              aria-label={label}
              className={activeLens === lens ? 'is-active' : undefined}
              key={lens}
              onClick={() => {
                setActiveLens(lens);
                setLeftDrawerOpen(true);
              }}
              title={label}
              type="button"
            >
              {icon}
              <span>{label}</span>
            </button>
          ))}
        </nav>

        {leftDrawerOpen ? (
          <aside className="ion-domain-weaver-left-drawer" aria-label="Domain Weaver command drawer">
            <div className="ion-domain-weaver-section-head">
              <div>
                <div className="ion-section-title">MISSION CONTROL</div>
                <b>{actionBusy ? 'running bounded write' : 'candidate controls'}</b>
              </div>
              <StatusBadge ready={!actionBusy} label={actionBusy ? text(actionBusy) : 'ready'} />
            </div>
            <div className="ion-domain-weaver-command-summary">
              <Metric icon={<DomainsIcon />} label="domains" value={`${text(summary.covered_domain_count, '0')}/${text(summary.domain_count, String(domains.length))}`} />
              <Metric icon={<GraphIcon />} label="edges" value={summary.edge_count ?? edges.length} />
              <Metric icon={<BlockersIcon />} label="blockers" value={loopSummary.blocker_count ?? blockers.length} />
              <Metric icon={<QueueIcon />} label="queue" value={text(queueGovernance.status, 'missing')} />
            </div>
            <div className="ion-domain-weaver-drawer-context">
              <div>
                <span>active lens</span>
                <b>{activeLens === 'map' ? 'Activity City' : activeLens}</b>
              </div>
              <div>
                <span>selected worker</span>
                <b>{currentWorker?.label ?? 'none'}</b>
              </div>
              <div>
                <span>selected event</span>
                <b>{selectedEvent?.label ?? 'none'}</b>
              </div>
              <div>
                <span>messages</span>
                <b>{noCarrierMessagesProjected ? 'no current carrier messages projected' : `${carrierMessages.length} projected`}</b>
              </div>
            </div>
            <div className="ion-domain-weaver-lane-filters" aria-label="Activity lane filters">
              {eventLaneCounts.map(([lane, count]) => (
                <button
                  key={lane}
                  onClick={() => {
                    const laneEvent = activityEvents.find((event) => event.lane === lane);
                    if (laneEvent) selectEvent(laneEvent.id);
                    setActiveLens(lane === 'proof' ? 'proof' : lane === 'action' ? 'actions' : lane === 'comms' ? 'signals' : 'timeline');
                    setRightInspectorOpen(true);
                    setInspectorMode('selected');
                  }}
                  type="button"
                >
                  <span>{lane}</span>
                  <b>{count}</b>
                </button>
              ))}
            </div>
            <div className="ion-domain-weaver-action-grid">
              <button
                className="ion-domain-weaver-action"
                disabled={Boolean(actionBusy)}
                onClick={() => void runDomainWeaverAction('refresh_queue_governor')}
                type="button"
              >
                <QueueIcon />
                <span>QUEUE REFRESH</span>
                <b>refresh route status, context capsule, and ready review</b>
              </button>
              <button
                className="ion-domain-weaver-action"
                disabled={Boolean(actionBusy)}
                onClick={() => void runDomainWeaverAction('materialize_promotion_review')}
                type="button"
              >
                <SourceIcon />
                <span>PROMOTION REVIEW</span>
                <b>prepare candidate review evidence without registry promotion</b>
              </button>
            </div>
            <div className="ion-domain-weaver-worker-switcher" aria-label="Specialist route">
              {teamWorkers.map((worker) => (
                <button
                  className={`${currentWorker?.id === worker.id ? 'is-active ' : ''}is-${worker.tone}`}
                  key={worker.id}
                  onClick={() => {
                    selectWorker(worker.id);
                    setActiveLens('team');
                  }}
                  title={worker.label}
                  type="button"
                >
                  <span>{worker.stage}</span>
                  <b>{worker.label}</b>
                </button>
              ))}
            </div>
            <BoundaryStrip projection={domainWeaver} />
            <PathRow label="projection" value={text(domainWeaver.projection_path)} />
            <PathRow label="page source" value={text(uiDevelopment.page_component_path)} />
          </aside>
        ) : null}

        <main className="ion-domain-weaver-main-surface" aria-label="Domain Weaver main work surface">
          <div className="ion-domain-weaver-lens-tabs" role="tablist" aria-label="Domain Weaver work surface lenses">
            {([
              ['map', 'Activity City'],
              ['team', 'Workers'],
              ['signals', 'Messages'],
              ['timeline', 'Timeline'],
              ['proof', 'Proof Trail'],
              ['context', 'Context'],
              ['actions', 'Actions'],
            ] as Array<[DomainWeaverLens, string]>).map(([lens, label]) => (
              <button
                className={activeLens === lens ? 'is-active' : undefined}
                key={lens}
                onClick={() => setActiveLens(lens)}
                role="tab"
                type="button"
              >
                {label}
              </button>
            ))}
          </div>

          {activeLens === 'map' ? (
            <section className="ion-domain-weaver-lens-body">
              <TeamMapLens
                activityEvents={activityEvents}
                currentWorker={currentWorker}
                domainClusters={domainClusters}
                onSelectWorker={selectWorker}
                onSelectEvent={selectEvent}
                selectedEvent={selectedEvent}
                selectedEventId={selectedEvent?.id ?? ''}
                modelEndpointBlocked={modelEndpointBlocked}
                modelEndpointReproofReady={modelEndpointReproofReady}
                modelEndpointReceiptPath={modelEndpointReceiptPath}
                noCarrierMessagesProjected={noCarrierMessagesProjected}
                operatorFeedbackPath={operatorFeedbackPath}
                operatorRejected={operatorRejected}
                proofRows={proofRows}
                routeExecutionSummary={routeExecutionSummary}
                faninRetryGate={faninRetryGate}
                setActiveLens={setActiveLens}
                teamWorkers={teamWorkers}
                nextUiPacket={nextUiPacket}
                visualProofReady={visualProofReady}
              />
            </section>
          ) : null}

          {activeLens === 'team' ? (
            <section className="ion-domain-weaver-lens-body">
              <div className="ion-domain-weaver-split">
                <article className="ion-domain-weaver-team-roster ion-domain-weaver-section">
                  <div className="ion-domain-weaver-section-head">
                    <div>
                      <div className="ion-section-title">WORKER LANES</div>
                      <b>{teamWorkers.length} specialists</b>
                    </div>
                    <StatusBadge ready={teamWorkers.every((worker) => worker.tone !== 'blocked')} label="candidate route" />
                  </div>
                  <div className="ion-domain-weaver-worker-grid">
                    {teamWorkers.map((worker) => (
                      <TeamWorkerCard
                        key={worker.id}
                        onSelect={() => selectWorker(worker.id)}
                        selected={currentWorker?.id === worker.id}
                        worker={worker}
                      />
                    ))}
                  </div>
                </article>
                <article className="ion-domain-weaver-section">
                  <div className="ion-domain-weaver-section-head">
                    <div>
                      <div className="ion-section-title">SELECTED WORKER</div>
                      <b>{currentWorker?.label ?? 'none selected'}</b>
                    </div>
                    <StatusBadge ready={currentWorker?.tone === 'ready'} label={currentWorker?.tone ?? 'missing'} />
                  </div>
                  <div className="ion-domain-weaver-worker-detail">
                    <Metric icon={<RouteIcon />} label="stage" value={currentWorker?.stage ?? 'n/a'} />
                    <Metric icon={<StatusIcon />} label="status" value={currentWorker?.status ?? 'n/a'} />
                    <Metric icon={<ReceiptIcon />} label="proof" value={currentWorker?.proofStatus ?? 'n/a'} />
                    <Metric icon={<QueueIcon />} label="request" value={shortId(currentWorker?.requestId ?? '') || 'n/a'} />
                    <PathRow label="return" value={currentWorker?.returnPath ?? ''} />
                    <PathRow label="request" value={currentWorker?.requestId ?? ''} />
                  </div>
                </article>
              </div>
              <div className="ion-domain-weaver-split">
                <article className="ion-domain-weaver-section">
                  <div className="ion-domain-weaver-section-head">
                    <div>
                      <div className="ion-section-title">ACTION RESULT</div>
                      <b>{hasActionResult ? resultTitle(actionResult) : 'no action run'}</b>
                    </div>
                    <StatusBadge ready={actionResult.ok === true} label={hasActionResult ? (actionResult.ok === true ? 'ok' : 'blocked') : 'idle'} />
                  </div>
                  <div className="ion-domain-weaver-metric-grid compact">
                    <Metric label="history" value={operatorActionSummary.record_count} />
                    <Metric label="latest" value={operatorActionSummary.latest_action || 'none'} />
                    <Metric label="ok" value={boolText(operatorActionSummary.latest_ok)} />
                    <Metric label="failed" value={operatorActionSummary.failed_record_count} />
                  </div>
                  {hasActionResult ? (
                    <div className="ion-domain-weaver-action-result">
                      <div>
                        <span>action</span>
                        <b>{text(actionResult.action, 'unknown')}</b>
                      </div>
                      <div>
                        <span>http</span>
                        <b>{text(actionResult.http_status, 'n/a')}</b>
                      </div>
                      <List values={[...actionReceipts, ...actionPaths].slice(0, 8)} empty="no action evidence paths" />
                    </div>
                  ) : (
                    <div className="ion-empty-state">NO DOMAIN WEAVER ACTION RESULT</div>
                  )}
                </article>
                <Lane
                  icon={<WorkSurfaceIcon />}
                  title="UI DEVELOPMENT"
                  verdict={text(uiDevelopment.status, 'missing')}
                  metrics={[
                    ['page', boolText(uiSummary.page_component_ready)],
                    ['route', boolText(uiSummary.shell_route_ready)],
                    ['build', boolText(uiSummary.dist_bundle_mentions_domain_weaver)],
                    ['usable', boolText(uiSummary.operator_usable)],
                    ['visual', boolText(visualProofReady)],
                    ['rejected', boolText(operatorRejected)],
                  ]}
                >
                  <List values={uiSurfaces.map((surface) => `${text(surface.surface_id)} / ${text(surface.status)} / ${text(surface.path)}`)} empty="no UI surfaces projected" />
                </Lane>
              </div>
              <div className="ion-domain-weaver-split">
                <article className="ion-domain-weaver-section">
                  <div className="ion-domain-weaver-section-head">
                    <div>
                      <div className="ion-section-title">QUEUE GOVERNOR DOGFOOD</div>
                      <b>{text(queueDogfood.status, 'missing')}</b>
                    </div>
                    <StatusBadge ready={text(queueDogfood.status) === 'queue_governor_dogfood_ready'} label={`${text(queueDogfoodSummary.passed_scenario_count, '0')}/${text(queueDogfoodSummary.scenario_count, '0')} scenarios`} />
                  </div>
                  <div className="ion-domain-weaver-scenario-list">
                    {queueDogfoodScenarios.map((scenario, index) => (
                      <article key={text(scenario.scenario_id, `scenario-${index}`)}>
                        <div>
                          <b>{text(scenario.scenario_id)}</b>
                          <span>{text(scenario.passed, 'false')}</span>
                        </div>
                        <code>{strings(scenario.covered_behaviors).join(' / ')}</code>
                      </article>
                    ))}
                    {queueDogfoodScenarios.length === 0 ? <div className="ion-empty-state">NO QUEUE GOVERNOR SCENARIOS PROJECTED</div> : null}
                  </div>
                </article>
                <article className="ion-domain-weaver-section">
                  <div className="ion-domain-weaver-section-head">
                    <div>
                      <div className="ion-section-title">ROUTE COUNTS</div>
                      <b>{text(queueGovernor.status, text(queueGovernance.status, 'missing'))}</b>
                    </div>
                    <StatusBadge ready={queueSummary.work_lane_projection_ready === true} label={queueSummary.work_lane_projection_ready === true ? 'routes current' : 'routes stale'} />
                  </div>
                  <div className="ion-domain-weaver-count-grid">
                    <CountList title="statuses" rows={statusCounts} />
                    <CountList title="classified routes" rows={laneCounts} />
                    <CountList title="work routes" rows={workLaneCounts} />
                  </div>
                </article>
              </div>
            </section>
          ) : null}

          {activeLens === 'signals' ? (
            <section className="ion-domain-weaver-lens-body">
              <div className="ion-domain-weaver-signal-board">
                <article className="ion-domain-weaver-section ion-domain-weaver-event-stream">
                  <div className="ion-domain-weaver-section-head">
                    <div>
                      <div className="ion-section-title">COMMS / EVENTS</div>
                      <b>{activityEvents.length} live signals</b>
                    </div>
                    <StatusBadge ready={activityEvents.some((event) => event.tone !== 'blocked')} label="stream" />
                  </div>
                  <EventStream events={activityEvents} onSelect={selectEvent} selectedEventId={selectedEvent?.id ?? ''} />
                </article>
                <article className="ion-domain-weaver-section">
                  <div className="ion-domain-weaver-section-head">
                    <div>
                      <div className="ion-section-title">BLOCKERS</div>
                      <b>{blockers.length} open</b>
                    </div>
                    <StatusBadge ready={blockers.length === 0} label={blockers.length ? 'attention' : 'clear'} />
                  </div>
                  <List values={blockers.map((blocker) => `${text(blocker.code || blocker.status)} ${text(blocker.finding_count || '')}`)} empty="no blockers projected" />
                  <div className="ion-domain-weaver-section-head">
                    <div>
                      <div className="ion-section-title">NEXT ACTIONS</div>
                      <b>{nextPackets.length} projected</b>
                    </div>
                  </div>
                  <NextStepList packets={nextPackets} />
                </article>
              </div>
              <article className="ion-domain-weaver-section">
                <div className="ion-domain-weaver-section-head">
                  <div>
                    <div className="ion-section-title">ACTIVE QUEUE</div>
                    <b>{activeQueueRuns.length} Domain Weaver runs</b>
                  </div>
                  <StatusBadge ready={queueSummary.work_lane_projection_ready === true} label={queueSummary.work_lane_projection_ready === true ? 'routes current' : 'routes stale'} />
                </div>
                <div className="ion-domain-weaver-count-grid">
                  <CountList title="statuses" rows={statusCounts} />
                  <CountList title="classified routes" rows={laneCounts} />
                  <CountList title="work routes" rows={workLaneCounts} />
                </div>
                <List values={activeQueueRuns.map((request) => `${text(request.status)} / ${text(request.lane_id)} / ${text(request.request_id)}`)} empty="no active Domain Weaver queue rows" />
                <List values={queueFindings.map((finding) => `${text(finding.code)} ${text(finding.count || '')}`).slice(0, 6)} empty="no queue findings" />
                <List values={flaggedRequests.map((request) => `${text(request.status)} / ${text(request.lane_id)} / ${text(request.path)}`).slice(0, 6)} empty="no flagged requests" />
              </article>
            </section>
          ) : null}

          {activeLens === 'timeline' ? (
            <section className="ion-domain-weaver-lens-body">
              <article className="ion-domain-weaver-section ion-domain-weaver-timeline-lens" data-activity-city-timeline="route fanout worker comms proof blocker model operator action fanin">
                <div className="ion-domain-weaver-section-head">
                  <div>
                    <div className="ion-section-title">ANIMATED BRANCH TIMELINE</div>
                    <b>route to fanout to worker to comms to proof to blocker to fan-in</b>
                  </div>
                  <StatusBadge ready={activityEvents.length > 0} label={`${activityEvents.length} events`} />
                </div>
                <TimelineEventList events={activityEvents} onSelect={selectEvent} selectedEventId={selectedEvent?.id ?? ''} />
              </article>
              <RecoveryGateStrip
                faninRetryGate={faninRetryGate}
                modelEndpointBlocked={modelEndpointBlocked}
                modelEndpointReproofReady={modelEndpointReproofReady}
                modelEndpointReceiptPath={modelEndpointReceiptPath}
                nextUiPacket={nextUiPacket}
                operatorFeedbackPath={operatorFeedbackPath}
                operatorRejected={operatorRejected}
                routeExecutionSummary={routeExecutionSummary}
                visualProofReady={visualProofReady}
              />
            </section>
          ) : null}

          {activeLens === 'proof' ? (
            <section className="ion-domain-weaver-lens-body">
              <article className="ion-domain-weaver-section">
                <div className="ion-section-title">PROMOTION / RECEIPT PROOF</div>
                <div className="ion-domain-weaver-metric-grid compact">
                  <Metric icon={<AuthorityIcon />} label="gate clean" value={`${text(gateSummary.clean_count, '0')}/${text(gateSummary.candidate_domain_count, '0')}`} />
                  <Metric icon={<SourceIcon />} label="drafts" value={promotionSummary.ready_for_registry_draft_count} />
                  <Metric icon={<ReceiptIcon />} label="recent receipts" value={receipts.length} />
                  <Metric icon={<BlockersIcon />} label="accepted state" value="false" />
                  <Metric icon={<EvidenceIcon />} label="visual proof" value={boolText(visualProofReady)} />
                  <Metric icon={<BlockersIcon />} label="operator rejected" value={boolText(operatorRejected)} />
                </div>
                <List values={receipts.map((receipt) => text(receipt.path)).filter(Boolean)} empty="no Domain Weaver receipts in runtime rail" />
              </article>
              <article className="ion-domain-weaver-section">
                <div className="ion-domain-weaver-section-head">
                  <div>
                    <div className="ion-section-title">RETURN PROOF MATRIX</div>
                    <b>{semanticRecords.length} semantic rows</b>
                  </div>
                  <StatusBadge ready={semanticRecords.every((record) => statusTone(text(record.semantic_status)) === 'ready')} label={text(semanticSettlement.status, 'semantic status')} />
                </div>
                <div className="ion-domain-weaver-proof-matrix">
                  {teamWorkers.map((worker) => (
                    <article className={`is-${worker.tone}`} key={`proof-${worker.id}`}>
                      <b>{worker.label}</b>
                      <span>{worker.proofStatus}</span>
                      <code>{worker.returnPath || worker.requestId}</code>
                    </article>
                  ))}
                </div>
              </article>
              <article className="ion-domain-weaver-section">
                <div className="ion-domain-weaver-section-head">
                  <div>
                    <div className="ion-section-title">NEXT STEPS</div>
                    <b>{nextPackets.length} projected</b>
                  </div>
                  <StatusBadge ready={nextPackets.length === 0} label={nextPackets.length === 0 ? 'none open' : 'open work'} />
                </div>
                <NextStepList packets={nextPackets} />
              </article>
              <article className="ion-domain-weaver-section">
                <div className="ion-section-title">AUTHORITY AND RAW MODEL</div>
                <BoundaryStrip projection={domainWeaver} />
                <PathRow label="operator feedback" value={operatorFeedbackPath} />
                <PathRow label="fan-in body" value={text(faninRetryGate.task_return_body_path)} />
                <details className="ion-domain-weaver-raw">
                  <summary>DOMAIN WEAVER RAW PROJECTION</summary>
                  <pre>{JSON.stringify(domainWeaver, null, 2)}</pre>
                </details>
              </article>
            </section>
          ) : null}

          {activeLens === 'context' ? (
            <section className="ion-domain-weaver-lens-body">
              <div className="ion-domain-weaver-split">
                <article className="ion-domain-weaver-section">
                  <div className="ion-section-title">KNOWN GOOD COCKPIT REFERENCES</div>
                  <List values={knownGoodSurfaces.map((surface) => `${text(surface.surface_id)} / ${boolText(surface.exists)} / ${text(surface.path)}`)} empty="no known good surfaces projected" />
                </article>
                <article className="ion-domain-weaver-section">
                  <div className="ion-section-title">UI FRONTEND EXCELLENCE ROUTE</div>
                  <List values={specialistRoute.map((row) => `${text(row.ordinal)}. ${text(row.agent_id)} / ${text(row.status)}`)} empty="no specialist route projected" />
                </article>
              </div>
              <article className="ion-domain-weaver-section">
                <div className="ion-section-title">CONTEXT SOURCES</div>
                <List values={contextRefs.map((ref) => `${boolText(ref.exists)} / ${text(ref.path)} / ${text(ref.reason)}`)} empty="no context refs projected" />
              </article>
              <article className="ion-domain-weaver-section">
                <div className="ion-domain-weaver-section-head">
                  <div>
                    <div className="ion-section-title">DOMAIN NETWORK</div>
                    <b>{domains.length} domains / {agents.length} agents</b>
                  </div>
                  <StatusBadge ready={Number(summary.gap_count || 0) === 0} label={`${text(summary.gap_count, '0')} gaps`} />
                </div>
                <DomainTable rows={domainRows} />
              </article>
              <article className="ion-domain-weaver-section">
                <div className="ion-domain-weaver-section-head">
                  <div>
                    <div className="ion-section-title">UI DEVELOPMENT</div>
                    <b>{text(uiDevelopment.status, 'missing')}</b>
                  </div>
                  <StatusBadge ready={uiReady} label={uiReady ? 'usable' : 'recovery'} />
                </div>
                <div className="ion-domain-weaver-metric-grid compact">
                  <Metric icon={<WorkSurfaceIcon />} label="page" value={boolText(uiSummary.page_component_ready)} />
                  <Metric icon={<RouteIcon />} label="route" value={boolText(uiSummary.shell_route_ready)} />
                  <Metric icon={<CheckIcon />} label="build" value={boolText(uiSummary.dist_bundle_mentions_domain_weaver)} />
                  <Metric icon={<EvidenceIcon />} label="visual" value={boolText(uiSummary.visual_proof_ready)} />
                </div>
                <List values={uiSurfaces.map((surface) => `${text(surface.surface_id)} / ${text(surface.status)} / ${text(surface.path)}`)} empty="no UI surfaces projected" />
              </article>
            </section>
          ) : null}

          {activeLens === 'actions' ? (
            <section className="ion-domain-weaver-lens-body ion-domain-weaver-action-lens">
              <article className="ion-domain-weaver-section ion-domain-weaver-next-action">
                <div className="ion-domain-weaver-section-head">
                  <div>
                    <div className="ion-section-title">NEXT LAWFUL ACTION</div>
                    <b>{text(nextUiPacket.packet_id, 'no UI retry packet projected')}</b>
                  </div>
                  <StatusBadge ready={text(nextUiPacket.work_class).includes('implementation')} label={text(nextUiPacket.lane_id, 'candidate')} />
                </div>
                <p>{text(nextUiPacket.objective, 'No bounded implementation retry objective is projected.')}</p>
                <div className="ion-domain-weaver-metric-grid compact">
                  <Metric icon={<RouteIcon />} label="route ready" value={boolText(routeExecutionSummary.route_execution_ready)} />
                  <Metric icon={<ReceiptIcon />} label="proof complete" value={`${text(routeExecutionSummary.proof_complete_count, '0')}/${text(routeExecutionSummary.declared_route_count, '0')}`} />
                  <Metric icon={<CheckIcon />} label="fan-in ready" value={boolText(faninRetryGate.retry_gate_ready || sourceFaninRetryGate.retry_gate_ready)} />
                  <Metric icon={<EvidenceIcon />} label="visual ready" value={boolText(visualProofReady)} />
                </div>
                <List values={nextUiPacketAcceptanceGates} empty="no acceptance gates projected" />
              </article>
              <div className="ion-domain-weaver-split">
                <article className="ion-domain-weaver-section">
                  <div className="ion-domain-weaver-section-head">
                    <div>
                      <div className="ion-section-title">VISIBLE BLOCKERS</div>
                      <b>{operatorRejected ? 'operator rejection still active' : 'no operator rejection flag'}</b>
                    </div>
                    <StatusBadge ready={!operatorRejected && visualProofReady} label={operatorRejected ? 'must remain visible' : 'review proof'} />
                  </div>
                  <List values={nextUiPacketBlockedUntil} empty="no implementation blockers projected" />
                  <PathRow label="operator feedback" value={operatorFeedbackPath} />
                  <PathRow label="old rejected screenshot" value={text(surfaceQualitySummary.operator_feedback_screenshot_path)} />
                </article>
                <article className="ion-domain-weaver-section">
                  <div className="ion-domain-weaver-section-head">
                    <div>
                      <div className="ion-section-title">FANOUT / FANIN / PROOF</div>
                      <b>{text(routeExecutionGate.status, 'route gate missing')}</b>
                    </div>
                    <StatusBadge ready={routeExecutionSummary.route_execution_ready === true} label={routeExecutionSummary.route_execution_ready === true ? 'route execution ready' : 'route blocked'} />
                  </div>
                  <div className="ion-domain-weaver-gate-grid">
                    <Metric label="declared route" value={routeExecutionSummary.declared_route_count} />
                    <Metric label="proof complete" value={routeExecutionSummary.proof_complete_count} />
                    <Metric label="worker returns" value={routeExecutionSummary.independent_worker_return_count} />
                    <Metric label="delegation" value={routeExecutionSummary.governed_delegation_count} />
                    <Metric label="stale context" value={routeExecutionSummary.stale_context_worker_return_count} />
                    <Metric label="missing proof" value={routeExecutionSummary.missing_route_proof_count} />
                  </div>
                  <List values={nextUiPacketContextRefs.slice(0, 8)} empty="no retry context refs projected" />
                </article>
              </div>
              <article className="ion-domain-weaver-section">
                <div className="ion-domain-weaver-section-head">
                  <div>
                    <div className="ion-section-title">ACTION RESULT</div>
                    <b>{hasActionResult ? resultTitle(actionResult) : 'no action run'}</b>
                  </div>
                  <StatusBadge ready={actionResult.ok === true} label={hasActionResult ? (actionResult.ok === true ? 'ok' : 'blocked') : 'idle'} />
                </div>
                {hasActionResult ? (
                  <div className="ion-domain-weaver-action-result">
                    <div>
                      <span>action</span>
                      <b>{text(actionResult.action, 'unknown')}</b>
                    </div>
                    <div>
                      <span>http</span>
                      <b>{text(actionResult.http_status, 'n/a')}</b>
                    </div>
                    <List values={[...actionReceipts, ...actionPaths].slice(0, 8)} empty="no action evidence paths" />
                  </div>
                ) : (
                  <div className="ion-empty-state">NO DOMAIN WEAVER ACTION RESULT</div>
                )}
              </article>
            </section>
          ) : null}
        </main>

        {rightInspectorOpen ? (
          <aside className="ion-domain-weaver-right-inspector" aria-label="Domain Weaver inspector">
            <div className="ion-domain-weaver-inspector-head">
              <div>
                <div className="ion-section-title">RIGHT INSPECTOR</div>
                <b>{inspectorMode}</b>
              </div>
              <StatusBadge ready={inspectorMode !== 'raw'} label={selectedEvent?.lane ?? currentWorker?.stage ?? 'selected'} />
            </div>
            {inspectorMode === 'selected' ? (
              <>
                {selectedEvent ? (
                  <div className={`ion-domain-weaver-inspector-event is-${selectedEvent.tone}`}>
                    <span>{selectedEvent.lane}</span>
                    <b>{selectedEvent.label}</b>
                    <em>{selectedEvent.meta}</em>
                    <code>{selectedEvent.detail}</code>
                  </div>
                ) : null}
                {currentWorker ? (
                  <div className={`ion-domain-weaver-inspector-worker is-${currentWorker.tone}`}>
                    <b>{currentWorker.label}</b>
                    <span>{currentWorker.status}</span>
                    <code>{currentWorker.proofStatus}</code>
                  </div>
                ) : null}
              </>
            ) : null}
            {inspectorMode === 'evidence' ? (
              <>
                <List values={[
                  operatorFeedbackPath,
                  modelEndpointReceiptPath,
                  text(asRecord(surfaceQuality.summary).visual_smoke_receipt_path),
                  text(faninRetryGate.return_path),
                  text(faninRetryGate.task_return_body_path),
                  currentWorker?.returnPath ?? '',
                  text(nextUiPacket.packet_id),
                ].filter(Boolean)} empty="no selected evidence paths" />
                <PathRow label="model endpoint" value={modelEndpointBlocked || modelEndpointReproofReady ? modelEndpointReceiptPath : 'unproven'} />
              </>
            ) : null}
            {inspectorMode === 'context' ? (
              <>
                <List values={nextUiPacketContextRefs.slice(0, 12)} empty="no context refs projected" />
                <PathRow label="projection" value={text(domainWeaver.projection_path)} />
                <PathRow label="shell route" value={text(uiDevelopment.shell_route_path)} />
              </>
            ) : null}
            {inspectorMode === 'authority' ? (
              <>
                <BoundaryStrip projection={domainWeaver} />
                <div className="ion-domain-weaver-metric-grid compact">
                  <Metric label="accepted" value="false" />
                  <Metric label="production" value="false" />
                  <Metric label="live" value="false" />
                  <Metric label="secrets" value="false" />
                </div>
                <PathRow label="operator feedback" value={operatorFeedbackPath} />
              </>
            ) : null}
            {inspectorMode === 'raw' ? (
              <details className="ion-domain-weaver-raw" open>
                <summary>SELECTED RAW STATE</summary>
                <pre>{JSON.stringify({ selectedEvent, currentWorker, modelEndpointBlocked, modelEndpointReproofReady, modelEndpointReceiptPath, next_packet: nextUiPacket.packet_id, visualProofReady, operatorRejected }, null, 2)}</pre>
              </details>
            ) : null}
            <div className="ion-domain-weaver-metric-grid compact">
              <Metric label="route" value={text(queueGovernance.status, 'missing')} />
              <Metric label="surface" value={text(uiDevelopment.status, 'missing')} />
              <Metric label="proofs" value={receipts.length} />
              <Metric label="next" value={nextPackets.length} />
            </div>
          </aside>
        ) : null}

        <nav className="ion-domain-weaver-right-rail" aria-label="Domain Weaver inspector modes">
          {([
            ['selected', <StatusIcon />, 'Selected'],
            ['evidence', <EvidenceIcon />, 'Evidence'],
            ['context', <SourceIcon />, 'Context'],
            ['authority', <AuthorityIcon />, 'Authority'],
            ['raw', <ReceiptIcon />, 'Raw'],
          ] as Array<[DomainWeaverInspectorMode, ReactNode, string]>).map(([mode, icon, label]) => (
            <button
              className={rightInspectorOpen && inspectorMode === mode ? 'is-active' : undefined}
              key={mode}
              onClick={() => {
                setInspectorMode(mode);
                setRightInspectorOpen(true);
              }}
              title={label}
              type="button"
            >
              {icon}
              <span>{label}</span>
            </button>
          ))}
        </nav>
      </div>

      <footer className="ion-domain-weaver-bottom-timeline" aria-label="Domain Weaver bottom timeline">
        <div className="ion-domain-weaver-section-head">
          <div>
            <div className="ion-section-title">TEAM TIMELINE</div>
            <b>{activityEvents.length} signals / {operatorActionRows.length} actions</b>
          </div>
          <StatusBadge ready={activityEvents.length > 0} label={activityEvents.length > 0 ? 'timeline ready' : 'timeline empty'} />
        </div>
        <div className="ion-domain-weaver-action-history ion-domain-weaver-event-timeline">
          {activityEvents.slice(0, 10).map((row, index) => (
            <button
              className={`is-${row.tone}${selectedEvent?.id === row.id ? ' is-selected' : ''}`}
              key={text(row.id, `event-${index}`)}
              onClick={() => {
                selectEvent(row.id);
                setInspectorMode('selected');
                setRightInspectorOpen(true);
              }}
              type="button"
            >
              <div>
                <b>{row.label}</b>
                <span>{row.meta}</span>
              </div>
              <code>{row.detail}</code>
            </button>
          ))}
          {activityEvents.length === 0 ? <div className="ion-empty-state">NO DOMAIN WEAVER EVENT HISTORY</div> : null}
        </div>
      </footer>
    </section>
  );
}

function TeamMapLens({
  activityEvents,
  currentWorker,
  domainClusters,
  faninRetryGate,
  modelEndpointBlocked,
  modelEndpointReproofReady,
  modelEndpointReceiptPath,
  nextUiPacket,
  noCarrierMessagesProjected,
  onSelectEvent,
  onSelectWorker,
  operatorFeedbackPath,
  operatorRejected,
  proofRows,
  routeExecutionSummary,
  selectedEvent,
  selectedEventId,
  setActiveLens,
  teamWorkers,
  visualProofReady,
}: {
  activityEvents: WeaverEvent[];
  currentWorker?: TeamWorker;
  domainClusters: DomainCluster[];
  faninRetryGate: AnyRecord;
  modelEndpointBlocked: boolean;
  modelEndpointReproofReady: boolean;
  modelEndpointReceiptPath: string;
  nextUiPacket: AnyRecord;
  noCarrierMessagesProjected: boolean;
  onSelectEvent: (eventId: string) => void;
  onSelectWorker: (workerId: string) => void;
  operatorFeedbackPath: string;
  operatorRejected: boolean;
  proofRows: Array<[string, unknown]>;
  routeExecutionSummary: AnyRecord;
  selectedEvent?: WeaverEvent;
  selectedEventId: string;
  setActiveLens: (lens: DomainWeaverLens) => void;
  teamWorkers: TeamWorker[];
  visualProofReady: boolean;
}) {
  const workerPositions = [
    [18, 22],
    [38, 15],
    [62, 18],
    [78, 36],
    [64, 64],
    [38, 72],
    [20, 54],
    [84, 68],
  ];
  const eventPositions = [
    [25, 34],
    [48, 28],
    [72, 48],
    [54, 70],
    [30, 66],
  ];
  return (
    <>
      <ActivityNow
        activityEvents={activityEvents}
        currentWorker={currentWorker}
        modelEndpointBlocked={modelEndpointBlocked}
        modelEndpointReproofReady={modelEndpointReproofReady}
        modelEndpointReceiptPath={modelEndpointReceiptPath}
        nextUiPacket={nextUiPacket}
        noCarrierMessagesProjected={noCarrierMessagesProjected}
        onSelectEvent={onSelectEvent}
        operatorRejected={operatorRejected}
        selectedEvent={selectedEvent}
        selectedEventId={selectedEventId}
        setActiveLens={setActiveLens}
        visualProofReady={visualProofReady}
      />
      <ProofClassOverlay
        faninRetryGate={faninRetryGate}
        modelEndpointBlocked={modelEndpointBlocked}
        modelEndpointReproofReady={modelEndpointReproofReady}
        operatorRejected={operatorRejected}
        routeExecutionSummary={routeExecutionSummary}
        visualProofReady={visualProofReady}
      />
      <div className="ion-domain-weaver-map-stage">
        <article className="ion-domain-weaver-city-map" aria-label="Autonomous team activity map">
          <svg aria-hidden="true" className="ion-domain-weaver-map-lines" preserveAspectRatio="none" viewBox="0 0 100 100">
            <path className="is-route" d="M16 24 C28 8 50 12 58 24 C68 38 82 32 86 48 C88 64 70 82 48 78 C30 76 12 64 16 46 C18 34 10 32 16 24" />
            <path className="is-proof" d="M18 54 C32 46 45 52 56 42 C68 30 78 36 86 48" />
            <path className="is-comms" d="M38 15 C42 34 38 52 38 72" />
            <path className="is-context" d="M20 54 C36 58 50 66 64 64 C74 62 80 54 84 68" />
          </svg>
          <div className="ion-domain-weaver-map-core">
            <GraphIcon />
            <b>TEAM FAN-IN</b>
            <span>{currentWorker?.label ?? 'route pending'}</span>
          </div>
          {domainClusters.slice(0, 6).map((cluster) => (
            <button
              className={`ion-domain-weaver-map-node is-domain is-${cluster.tone}`}
              key={cluster.id}
              style={{ '--x': `${cluster.x}%`, '--y': `${cluster.y}%` } as CSSProperties}
              title={`${cluster.label}: ${cluster.status}`}
              type="button"
            >
              <DomainsIcon />
              <b>{cluster.label}</b>
              <span>{cluster.agentCount}</span>
            </button>
          ))}
          {teamWorkers.map((worker, index) => {
            const [x, y] = workerPositions[index % workerPositions.length];
            return (
              <button
                className={`ion-domain-weaver-map-node is-worker is-${worker.tone}${currentWorker?.id === worker.id ? ' is-active' : ''}`}
                key={worker.id}
                onClick={() => {
                  onSelectWorker(worker.id);
                }}
                style={{ '--x': `${x}%`, '--y': `${y}%` } as CSSProperties}
                title={`${worker.label}: ${worker.status}`}
                type="button"
              >
                <WorkSurfaceIcon />
                <b>{worker.stage}</b>
                <span>{worker.label}</span>
              </button>
            );
          })}
          {activityEvents.slice(0, 5).map((event, index) => {
            const [x, y] = eventPositions[index % eventPositions.length];
            return (
              <button
                className={`ion-domain-weaver-map-node is-event is-${event.tone}${selectedEventId === event.id ? ' is-active' : ''}`}
                key={`map-event-${event.id}`}
                onClick={() => onSelectEvent(event.id)}
                style={{ '--x': `${x}%`, '--y': `${y}%` } as CSSProperties}
                title={`${event.label}: ${event.meta}`}
                type="button"
              >
                <BranchIcon />
                <b>{shortId(event.id)}</b>
                <span>{event.lane}</span>
              </button>
            );
          })}
        </article>
        <aside className="ion-domain-weaver-map-proof">
          <div className="ion-section-title">STATUS</div>
          <div className="ion-domain-weaver-metric-grid compact">
            {proofRows.map(([label, value]) => <Metric key={label} label={label} value={value} />)}
          </div>
          <div className="ion-domain-weaver-map-legend">
            <span className="is-ready">ready</span>
            <span className="is-working">working</span>
            <span className="is-watch">watch</span>
            <span className="is-blocked">blocked</span>
          </div>
        </aside>
      </div>
      <RecoveryGateStrip
        faninRetryGate={faninRetryGate}
        modelEndpointBlocked={modelEndpointBlocked}
        modelEndpointReproofReady={modelEndpointReproofReady}
        modelEndpointReceiptPath={modelEndpointReceiptPath}
        nextUiPacket={nextUiPacket}
        operatorFeedbackPath={operatorFeedbackPath}
        operatorRejected={operatorRejected}
        routeExecutionSummary={routeExecutionSummary}
        visualProofReady={visualProofReady}
      />
      <article className="ion-domain-weaver-section ion-domain-weaver-branch-flow">
        <div className="ion-domain-weaver-section-head">
          <div>
            <div className="ion-section-title">BRANCH FLOW</div>
            <b>{activityEvents.length} event signals</b>
          </div>
          <StatusBadge ready={activityEvents.some((event) => event.tone !== 'blocked')} label="live map" />
        </div>
        <div className="ion-domain-weaver-branch-tracks">
          {teamWorkers.slice(0, 6).map((worker, index) => (
            <section className={`is-${worker.tone}`} key={`track-${worker.id}`}>
              <header>
                <BranchIcon />
                <b>{worker.stage}</b>
                <span>{worker.label}</span>
              </header>
              <button
                onClick={() => {
                  onSelectWorker(worker.id);
                  setActiveLens('team');
                }}
                style={{ '--track-start': String((index % 3) + 1), '--track-span': String(3 + (index % 2)) } as CSSProperties}
                title={worker.detail}
                type="button"
              >
                <b>{worker.status}</b>
                <span>{worker.proofStatus}</span>
              </button>
            </section>
          ))}
        </div>
      </article>
    </>
  );
}

function ActivityNow({
  activityEvents,
  currentWorker,
  modelEndpointBlocked,
  modelEndpointReproofReady,
  modelEndpointReceiptPath,
  nextUiPacket,
  noCarrierMessagesProjected,
  onSelectEvent,
  operatorRejected,
  selectedEvent,
  selectedEventId,
  setActiveLens,
  visualProofReady,
}: {
  activityEvents: WeaverEvent[];
  currentWorker?: TeamWorker;
  modelEndpointBlocked: boolean;
  modelEndpointReproofReady: boolean;
  modelEndpointReceiptPath: string;
  nextUiPacket: AnyRecord;
  noCarrierMessagesProjected: boolean;
  onSelectEvent: (eventId: string) => void;
  operatorRejected: boolean;
  selectedEvent?: WeaverEvent;
  selectedEventId: string;
  setActiveLens: (lens: DomainWeaverLens) => void;
  visualProofReady: boolean;
}) {
  const latestEvents = activityEvents.slice(0, 4);
  return (
    <article
      className="ion-domain-weaver-section ion-domain-weaver-activity-now"
      data-activity-city-proof="activity comms events messages model_endpoint_degraded operator_rejection active_branch next_lawful_action"
    >
      <div className="ion-domain-weaver-section-head">
        <div>
          <div className="ion-section-title">ACTIVITY / COMMS / EVENTS NOW</div>
          <b>{selectedEvent?.label ?? 'Domain Weaver Activity City'}</b>
        </div>
        <StatusBadge ready={!operatorRejected && visualProofReady && !modelEndpointBlocked} label={operatorRejected ? 'operator rejection active' : 'activity proof pending'} />
      </div>
      <div className="ion-domain-weaver-now-grid">
        <Metric icon={<ChatIcon />} label="latest activity" value={latestEvents[0]?.label ?? 'no current activity'} />
        <Metric icon={<BranchIcon />} label="active branch" value={currentWorker?.label ?? 'route fanout'} />
        <Metric icon={<BlockersIcon />} label="blocker" value={operatorRejected ? 'operator rejection active' : visualProofReady ? 'none projected' : 'fresh visual proof pending'} />
        <Metric icon={<StatusIcon />} label="model" value={modelEndpointBlocked ? 'model endpoint degraded' : modelEndpointReproofReady ? 'endpoint reproof recorded' : 'endpoint unproven'} />
      </div>
      <div className="ion-domain-weaver-now-brief">
        <div>
          <span>next lawful action</span>
          <b>{text(nextUiPacket.packet_id, 'bounded implementation packet')}</b>
        </div>
        <div>
          <span>comms state</span>
          <b>{noCarrierMessagesProjected ? 'no current carrier messages projected; task returns and proof receipts are rendered as activity events' : 'carrier messages projected into activity stream'}</b>
        </div>
        <div>
          <span>model proof</span>
          <b>{modelEndpointBlocked ? `degraded receipt: ${modelEndpointReceiptPath}` : modelEndpointReproofReady ? `reproof: ${modelEndpointReceiptPath}` : 'fresh endpoint proof still required'}</b>
        </div>
      </div>
      <div className="ion-domain-weaver-mobile-sheet-preview" data-mobile-sheets="left_lens_sheet right_inspector_sheet">
        <div>
          <span>Left sheet</span>
          <b>Lens filters, worker focus, and selected event summary stay page-local.</b>
        </div>
        <div>
          <span>Right sheet</span>
          <b>Selected proof, authority, evidence, and raw detail stay inspector-only.</b>
        </div>
      </div>
      <div className="ion-domain-weaver-now-event-grid">
        {latestEvents.map((event) => (
          <button
            className={`is-${event.tone}${selectedEventId === event.id ? ' is-selected' : ''}`}
            key={event.id}
            onClick={() => {
              onSelectEvent(event.id);
              setActiveLens(event.lane === 'comms' ? 'signals' : 'timeline');
            }}
            type="button"
          >
            <span>{event.lane}</span>
            <b>{event.label}</b>
            <code>{event.meta}</code>
          </button>
        ))}
      </div>
    </article>
  );
}

function ProofClassOverlay({
  faninRetryGate,
  modelEndpointBlocked,
  modelEndpointReproofReady,
  operatorRejected,
  routeExecutionSummary,
  visualProofReady,
}: {
  faninRetryGate: AnyRecord;
  modelEndpointBlocked: boolean;
  modelEndpointReproofReady: boolean;
  operatorRejected: boolean;
  routeExecutionSummary: AnyRecord;
  visualProofReady: boolean;
}) {
  const proofClasses = [
    {
      label: 'Hydration',
      status: modelEndpointReproofReady ? 'endpoint hydrated' : modelEndpointBlocked ? 'degraded evidence' : 'unproven',
      detail: 'Proves endpoint/model response only; does not settle usability.',
      tone: modelEndpointReproofReady ? 'watch' : 'blocked',
    },
    {
      label: 'Visual',
      status: visualProofReady ? 'viewport proof projected' : 'fresh proof pending',
      detail: 'Proves screenshots/selectors only; operator acceptance remains separate.',
      tone: visualProofReady ? 'ready' : 'blocked',
    },
    {
      label: 'Operator',
      status: operatorRejected ? 'rejection active' : 'no rejection flag',
      detail: 'Superseded only by a later operator settlement receipt.',
      tone: operatorRejected ? 'blocked' : 'watch',
    },
    {
      label: 'Route/Return',
      status: `${text(routeExecutionSummary.proof_complete_count, '0')}/${text(routeExecutionSummary.declared_route_count, '0')} route proof`,
      detail: faninRetryGate.retry_gate_ready === true ? 'Fan-in gate is evidence, not accepted state.' : 'Fan-in gate still requires proof.',
      tone: routeExecutionSummary.route_execution_ready === true ? 'ready' : 'working',
    },
    {
      label: 'Accepted State',
      status: 'absent',
      detail: 'No accepted-state, production, live execution, or secrets authority is claimed.',
      tone: 'blocked',
    },
  ] as Array<{ detail: string; label: string; status: string; tone: WeaverTone }>;
  return (
    <article className="ion-domain-weaver-proof-overlay" data-proof-overlay="hydration visual operator route_return accepted_state_absent">
      <div className="ion-domain-weaver-section-head">
        <div>
          <div className="ion-section-title">PROOF CLASS OVERLAY</div>
          <b>what the evidence proves, and what it does not prove</b>
        </div>
        <StatusBadge ready={false} label="accepted state absent" />
      </div>
      <div>
        {proofClasses.map((proof) => (
          <section className={`is-${proof.tone}`} key={proof.label}>
            <span>{proof.label}</span>
            <b>{proof.status}</b>
            <em>{proof.detail}</em>
          </section>
        ))}
      </div>
    </article>
  );
}

function RecoveryGateStrip({
  faninRetryGate,
  modelEndpointBlocked,
  modelEndpointReproofReady,
  modelEndpointReceiptPath,
  nextUiPacket,
  operatorFeedbackPath,
  operatorRejected,
  routeExecutionSummary,
  visualProofReady,
}: {
  faninRetryGate: AnyRecord;
  modelEndpointBlocked: boolean;
  modelEndpointReproofReady: boolean;
  modelEndpointReceiptPath: string;
  nextUiPacket: AnyRecord;
  operatorFeedbackPath: string;
  operatorRejected: boolean;
  routeExecutionSummary: AnyRecord;
  visualProofReady: boolean;
}) {
  const blockedUntil = strings(nextUiPacket.blocked_until_implementation_packet);
  return (
    <article className="ion-domain-weaver-section ion-domain-weaver-recovery-strip">
      <div className="ion-domain-weaver-section-head">
        <div>
          <div className="ion-section-title">RECOVERY GATE</div>
          <b>{text(nextUiPacket.packet_id, 'implementation retry candidate')}</b>
        </div>
        <StatusBadge ready={routeExecutionSummary.route_execution_ready === true && faninRetryGate.retry_gate_ready === true} label={operatorRejected ? 'rejection visible' : 'review proof'} />
      </div>
      <div className="ion-domain-weaver-gate-grid">
        <Metric label="route proof" value={`${text(routeExecutionSummary.proof_complete_count, '0')}/${text(routeExecutionSummary.declared_route_count, '0')}`} />
        <Metric label="fan-in accepted" value={boolText(faninRetryGate.accepted)} />
        <Metric label="visual proof" value={boolText(visualProofReady)} />
        <Metric label="operator rejected" value={boolText(operatorRejected)} />
        <Metric label="model reproof" value={modelEndpointReproofReady ? 'true' : boolText(!modelEndpointBlocked)} />
      </div>
      <List values={blockedUntil.slice(0, 4)} empty="no recovery blockers projected" />
      <PathRow label="model endpoint" value={modelEndpointReceiptPath} />
      <PathRow label="operator feedback" value={operatorFeedbackPath} />
      <PathRow label="fan-in body" value={text(faninRetryGate.task_return_body_path)} />
    </article>
  );
}

function TeamWorkerCard({ onSelect, selected, worker }: { onSelect: () => void; selected: boolean; worker: TeamWorker }) {
  return (
    <button className={`ion-domain-weaver-worker-card is-${worker.tone}${selected ? ' is-selected' : ''}`} onClick={onSelect} type="button">
      <span>{worker.stage}</span>
      <b>{worker.label}</b>
      <em>{worker.status}</em>
      <code>{worker.proofStatus}</code>
    </button>
  );
}

function EventStream({
  events,
  onSelect,
  selectedEventId,
}: {
  events: WeaverEvent[];
  onSelect?: (eventId: string) => void;
  selectedEventId?: string;
}) {
  return (
    <div className="ion-domain-weaver-event-stream-list">
      {events.map((event) => (
        <button
          className={`is-${event.tone}${selectedEventId === event.id ? ' is-selected' : ''}`}
          key={event.id}
          onClick={() => onSelect?.(event.id)}
          type="button"
        >
          <span>{event.lane}</span>
          <div>
            <b>{event.label}</b>
            <small>{event.meta}</small>
          </div>
          <code>{event.detail}</code>
        </button>
      ))}
      {events.length === 0 ? <div className="ion-empty-state">NO DOMAIN WEAVER SIGNALS</div> : null}
    </div>
  );
}

function TimelineEventList({
  events,
  onSelect,
  selectedEventId,
}: {
  events: WeaverEvent[];
  onSelect: (eventId: string) => void;
  selectedEventId: string;
}) {
  const lanes = ['route', 'fanin', 'operator', 'model', 'comms', 'proof', 'action', 'return', 'blocker'];
  return (
    <div className="ion-domain-weaver-timeline-grid">
      {lanes.map((lane) => {
        const laneEvents = events.filter((event) => event.lane === lane);
        return (
          <section key={lane}>
            <header>
              <BranchIcon />
              <b>{lane}</b>
              <span>{laneEvents.length} events</span>
            </header>
            <div>
              {laneEvents.map((event, index) => (
                <button
                  className={`is-${event.tone}${selectedEventId === event.id ? ' is-selected' : ''}`}
                  key={event.id}
                  onClick={() => onSelect(event.id)}
                  style={{ '--timeline-index': String(index + 1) } as CSSProperties}
                  type="button"
                >
                  <b>{event.label}</b>
                  <span>{event.meta}</span>
                </button>
              ))}
              {laneEvents.length === 0 ? <span className="ion-domain-weaver-timeline-empty">no {lane} events projected</span> : null}
            </div>
          </section>
        );
      })}
    </div>
  );
}

function buildTeamWorkers(
  specialistRoute: AnyRecord[],
  templates: AnyRecord[],
  observedReturns: AnyRecord[],
  settlementRecords: AnyRecord[],
  semanticRecords: AnyRecord[],
  routeProofRows: AnyRecord[],
): TeamWorker[] {
  return specialistRoute.map((row, index) => {
    const label = text(row.agent_id, `worker-${index + 1}`);
    const needle = roleRequestNeedle(label);
    const request = templates.find((template) => text(template.request_id).toLowerCase().includes(needle));
    const requestId = text(request?.request_id);
    const observed = observedReturns.find((record) => text(record.request_id) === requestId);
    const settlement = settlementRecords.find((record) => text(record.request_id) === requestId);
    const semantic = semanticRecords.find((record) => text(record.request_id) === requestId);
    const routeProof = routeProofRows.find((proof) => text(proof.agent_id) === label);
    const routeProofReady = routeProof?.proof_ready === true;
    const routeProofRef = text(routeProof?.proof_ref);
    const routeProofType = text(routeProof?.proof_type);
    const delegatedRole = text(routeProof?.delegated_active_role || row.delegated_active_role);
    const status = text(
      routeProofType ? `${routeProofType}${routeProofReady ? ' ready' : ''}` : '',
      semantic?.semantic_status
      || observed?.run_status
      || settlement?.status
      || request?.status
      || row.status,
      'candidate route',
    );
    const proofStatus = text(
      routeProofReady ? 'proof ready' : '',
      semantic?.body_result && semantic?.semantic_status ? `${text(semantic.body_result)} / ${text(semantic.semantic_status)}` : '',
      text(settlement?.template_action_proof_accepted) === 'true' ? 'proof accepted' : delegatedRole ? `delegated ${delegatedRole}` : text(row.status, 'candidate'),
    );
    return {
      id: label,
      label: humanizeRole(label),
      stage: String(index + 1).padStart(2, '0'),
      status,
      detail: text(request?.objective, text(row.status, 'candidate worker')),
      requestId,
      returnPath: text(routeProofRef || semantic?.task_return_body_path || observed?.latest_return_packet_path || settlement?.task_return_packet_path),
      proofStatus,
      tone: routeProofReady ? 'ready' : statusTone(`${status} ${proofStatus}`),
    };
  });
}

function buildDomainClusters(domains: AnyRecord[], agents: AnyRecord[]): DomainCluster[] {
  const positions = [
    [12, 18],
    [74, 18],
    [84, 50],
    [68, 82],
    [24, 78],
    [10, 48],
  ];
  return domains.slice(0, 6).map((domain, index) => {
    const domainId = text(domain.domain_id || domain.display_name, `domain-${index}`);
    const agentCount = text(
      domain.agent_count,
      String(agents.filter((agent) => strings(agent.domain_ids).includes(domainId) || text(agent.primary_domain) === domainId).length),
    );
    const [x, y] = positions[index % positions.length];
    return {
      id: domainId,
      label: shortId(domainId.replace(/^domain\./, '')),
      status: text(domain.status || domain.fact_posture, 'candidate'),
      agentCount,
      x,
      y,
      tone: statusTone(text(domain.status || domain.fact_posture)),
    };
  });
}

function buildWeaverEvents(
  operatorActions: AnyRecord[],
  observedReturns: AnyRecord[],
  semanticRecords: AnyRecord[],
  carrierMessages: AnyRecord[],
  blockers: AnyRecord[],
  recovery: RecoveryEventInputs,
): WeaverEvent[] {
  const events: WeaverEvent[] = [];
  if (recovery.routeExecutionSummary.route_execution_ready === true) {
    events.push({
      id: 'route-execution-ready',
      label: 'Declared route execution ready',
      meta: `${text(recovery.routeExecutionSummary.proof_complete_count, '0')}/${text(recovery.routeExecutionSummary.declared_route_count, '0')} proof rows`,
      detail: 'DOMAIN_WEAVER_ROUTE_EXECUTION_GATE.candidate.json',
      lane: 'route',
      tone: 'ready',
    });
  }
  if (recovery.faninRetryGate.retry_gate_ready === true) {
    events.push({
      id: 'fanin-retry-gate-ready',
      label: 'Fan-in retry gate accepted',
      meta: 'accepted no-code fan-in controls this retry',
      detail: text(recovery.faninRetryGate.task_return_body_path || recovery.faninRetryGate.return_path),
      lane: 'fanin',
      tone: 'ready',
    });
  }
  if (recovery.operatorRejected) {
    events.push({
      id: 'operator-rejection-active',
      label: 'Operator rejection active',
      meta: 'current surface remains candidate-only',
      detail: recovery.operatorFeedbackPath,
      lane: 'operator',
      tone: 'blocked',
    });
  }
  if (!recovery.visualProofReady) {
    events.push({
      id: 'visual-proof-pending',
      label: 'Fresh visual proof pending',
      meta: 'desktop tablet mobile proof required',
      detail: 'visual_smoke_fresh false until this retry is captured',
      lane: 'proof',
      tone: 'blocked',
    });
  }
  if (recovery.modelEndpointBlocked) {
    events.push({
      id: 'model-endpoint-degraded',
      label: 'Model endpoint degraded',
      meta: '/cockpit/model.json timed out or returned partial proof',
      detail: recovery.modelEndpointReceiptPath,
      lane: 'model',
      tone: 'blocked',
    });
  } else if (recovery.modelEndpointReproofReady) {
    events.push({
      id: 'model-endpoint-reproof-recorded',
      label: 'Endpoint reproof recorded',
      meta: 'live weave model endpoint returned hydrated projection',
      detail: recovery.modelEndpointReceiptPath,
      lane: 'model',
      tone: 'ready',
    });
  }
  if (recovery.noCarrierMessagesProjected) {
    events.push({
      id: 'no-current-carrier-messages-projected',
      label: 'No current carrier messages projected',
      meta: 'task returns, proof receipts, operator feedback, and model events are rendered as activity',
      detail: 'ION/05_context/current/ACTIVE_CARRIER_MESSAGE_QUEUE.json',
      lane: 'comms',
      tone: 'watch',
    });
  }
  if (text(recovery.nextUiPacket.packet_id)) {
    events.push({
      id: `next-${text(recovery.nextUiPacket.packet_id)}`,
      label: 'Next lawful packet',
      meta: text(recovery.nextUiPacket.lane_id, 'implementation lane'),
      detail: text(recovery.nextUiPacket.packet_id),
      lane: 'action',
      tone: 'working',
    });
  }
  operatorActions.slice(0, 6).forEach((row, index) => {
    events.push({
      id: `action-${index}-${text(row.created_at)}`,
      label: humanizeRole(text(row.action, 'operator action')),
      meta: `${text(row.created_at)} / ${boolText(row.ok)}`,
      detail: text(row.record_path),
      lane: 'action',
      tone: row.ok === false ? 'blocked' : 'ready',
    });
  });
  semanticRecords.slice(0, 8).forEach((row, index) => {
    events.push({
      id: `semantic-${index}-${text(row.request_id)}`,
      label: humanizeRole(roleFromRequestId(text(row.request_id))),
      meta: text(row.semantic_status, 'semantic pending'),
      detail: text(row.task_return_body_path),
      lane: 'proof',
      tone: statusTone(text(row.semantic_status)),
    });
  });
  observedReturns.slice(0, 5).forEach((row, index) => {
    events.push({
      id: `return-${index}-${text(row.request_id)}`,
      label: humanizeRole(roleFromRequestId(text(row.request_id))),
      meta: text(row.latest_return_packet_path, 'return observed'),
      detail: text(row.request_id),
      lane: 'return',
      tone: 'ready',
    });
  });
  carrierMessages.slice(0, 4).forEach((row, index) => {
    events.push({
      id: `carrier-${index}-${text(row.message_id)}`,
      label: text(row.channel, 'carrier message'),
      meta: `${text(row.sender_carrier_id)} -> ${text(row.recipient)}`,
      detail: text(row.body),
      lane: 'comms',
      tone: statusTone(text(row.status, 'watch')),
    });
  });
  blockers.slice(0, 4).forEach((row, index) => {
    events.push({
      id: `blocker-${index}-${text(row.code)}`,
      label: text(row.code || row.status, 'blocker'),
      meta: text(row.status, 'attention'),
      detail: text(row.finding_count || row.terminal_repair_request_count || row.stale_waiting_request_count, 'open'),
      lane: 'blocker',
      tone: 'blocked',
    });
  });
  return events.slice(0, 18);
}

function summarizeEventLanes(events: WeaverEvent[]): Array<[string, number]> {
  const preferredOrder = ['route', 'fanin', 'operator', 'model', 'comms', 'proof', 'action', 'return', 'blocker'];
  const counts = new Map<string, number>();
  events.forEach((event) => counts.set(event.lane, (counts.get(event.lane) ?? 0) + 1));
  return preferredOrder
    .filter((lane) => counts.has(lane))
    .map((lane) => [lane, counts.get(lane) ?? 0]);
}

function eventMatchesWorker(event: WeaverEvent, worker: TeamWorker): boolean {
  const eventText = `${event.id} ${event.label} ${event.meta} ${event.detail}`.toLowerCase();
  const candidates = [
    worker.id,
    worker.label,
    worker.requestId,
    shortId(worker.requestId),
    roleRequestNeedle(worker.id),
    roleRequestNeedle(worker.label),
  ]
    .map((value) => value.toLowerCase())
    .filter((value) => value.length > 2);
  return candidates.some((candidate) => eventText.includes(candidate));
}

function statusTone(value: string): WeaverTone {
  const lowered = value.toLowerCase();
  if (lowered.includes('blocked') || lowered.includes('rejected') || lowered.includes('failed') || lowered.includes('invalid')) return 'blocked';
  if (lowered.includes('ready') || lowered.includes('clean') || lowered.includes('complete') || lowered.includes('accepted') || lowered.includes('usable') || lowered === 'true') return 'ready';
  if (lowered.includes('running') || lowered.includes('claimed') || lowered.includes('queued') || lowered.includes('pending')) return 'working';
  return 'watch';
}

function defaultSurfacePanelOpen(): boolean {
  if (typeof window === 'undefined') return true;
  return window.matchMedia('(min-width: 901px)').matches;
}

function roleRequestNeedle(label: string): string {
  return label.toLowerCase().replace(/^role[._-]/, '').replace(/[^a-z0-9]+/g, '_').replace(/^_+|_+$/g, '');
}

function roleFromRequestId(requestId: string): string {
  const marker = 'act_req_';
  const index = requestId.indexOf(marker);
  if (index >= 0) return requestId.slice(index + marker.length);
  const fissionMarker = 'fanout_';
  const fissionIndex = requestId.indexOf(fissionMarker);
  if (fissionIndex >= 0) return requestId.slice(fissionIndex + fissionMarker.length);
  return requestId;
}

function humanizeRole(value: string): string {
  return shortId(value.replace(/^role[._-]/, '').replace(/^act_req_/, '').replace(/_/g, ' ')).toUpperCase();
}

function shortId(value: string): string {
  if (!value) return '';
  const cleaned = value.replace(/^codex_req_domain_weaver_approval_fanout_/, '').replace(/^codex_req_domain_weaver_/, '');
  return cleaned.length > 42 ? `${cleaned.slice(0, 39)}...` : cleaned;
}

function shortPath(value: string): string {
  if (!value) return '';
  const parts = value.split('/').filter(Boolean);
  if (parts.length <= 2) return value;
  return parts.slice(-2).join('/');
}

function DomainTable({ rows }: { rows: AnyRecord[] }) {
  return (
    <div className="ion-domain-weaver-table-wrap">
      <table className="ion-domain-weaver-table">
        <thead>
          <tr>
            <th>route</th>
            <th>status</th>
            <th>agents</th>
            <th>posture</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((domain, index) => (
            <tr key={text(domain.domain_id, `domain-${index}`)}>
              <td>{text(domain.domain_id || domain.display_name)}</td>
              <td>{text(domain.status || domain.fact_posture)}</td>
              <td>{text(domain.agent_count ?? records(domain.agents).length ?? '0')}</td>
              <td>{text(domain.maturity_estimate || domain.promotion_posture || domain.policy, 'candidate')}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {rows.length === 0 ? <div className="ion-empty-state">NO DOMAINS PROJECTED</div> : null}
    </div>
  );
}

function NextStepList({ packets }: { packets: AnyRecord[] }) {
  return (
    <div className="ion-domain-weaver-packet-list">
      {packets.map((packet, index) => (
        <article key={text(packet.packet_id, `packet-${index}`)}>
          <div>
            <b>{text(packet.packet_id)}</b>
            <span>{text(packet.lane_id)} / {text(packet.work_class)}</span>
          </div>
          <code>{text(packet.objective)}</code>
        </article>
      ))}
      {packets.length === 0 ? <div className="ion-empty-state">NO NEXT STEPS DECLARED</div> : null}
    </div>
  );
}

function Lane({
  children,
  icon,
  metrics,
  title,
  verdict,
}: {
  children: ReactNode;
  icon: ReactNode;
  metrics: Array<[string, unknown]>;
  title: string;
  verdict: string;
}) {
  return (
    <article className="ion-domain-weaver-lane">
      <header>
        <span aria-hidden="true">{icon}</span>
        <div>
          <div className="ion-section-title">{title}</div>
          <b>{verdict}</b>
        </div>
      </header>
      <div className="ion-domain-weaver-metric-grid compact">
        {metrics.map(([label, value]) => (
          <Metric key={label} label={label} value={value} />
        ))}
      </div>
      {children}
    </article>
  );
}

function Metric({ icon, label, value }: { icon?: ReactNode; label: string; value: unknown }) {
  return (
    <div className="ion-domain-weaver-metric">
      <span>{icon}{label}</span>
      <b>{text(value, '0')}</b>
    </div>
  );
}

function StatusBadge({ label, ready }: { label: string; ready: boolean }) {
  return <span className={`ion-domain-weaver-badge is-${ready ? 'ready' : 'blocked'}`}>{label}</span>;
}

function PathRow({ label, value }: { label: string; value: string }) {
  if (!value) return null;
  return (
    <div className="ion-domain-weaver-path">
      <span>{label}</span>
      <code>{value}</code>
    </div>
  );
}

function BoundaryStrip({ projection }: { projection: AnyRecord }) {
  const authority = asRecord(projection.authority);
  const items = [
    ['production', authority.production_authority ?? projection.production_authority],
    ['live', authority.live_execution_authority ?? projection.live_execution_authority],
    ['accepted', authority.accepted_state_authority ?? projection.accepted_state_authority],
    ['secrets', authority.secrets_authority ?? projection.secrets_authority],
  ];
  return (
    <div className="ion-domain-weaver-authority">
      {items.map(([label, value]) => (
        <span key={String(label)}>{String(label)}: {boolText(value)}</span>
      ))}
    </div>
  );
}

function List({ empty, values }: { empty: string; values: string[] }) {
  return (
    <div className="ion-domain-weaver-list">
      {values.map((value, index) => <span key={`${value}-${index}`}>{value}</span>)}
      {values.length === 0 ? <span>{empty}</span> : null}
    </div>
  );
}

function CountList({ rows, title }: { rows: Array<[string, unknown]>; title: string }) {
  return (
    <div className="ion-domain-weaver-count-list">
      <b>{title}</b>
      {rows.slice(0, 8).map(([label, value]) => (
        <span key={`${label}-${text(value)}`}>{label}: {text(value, '0')}</span>
      ))}
      {rows.length === 0 ? <span>none</span> : null}
    </div>
  );
}

function resultTitle(result: AnyRecord): string {
  if (result.ok === true) return 'ok';
  return text(result.finding || result.error, 'blocked');
}

function asRecord(value: unknown): AnyRecord {
  return value && typeof value === 'object' && !Array.isArray(value) ? value as AnyRecord : {};
}

function records(value: unknown): AnyRecord[] {
  return Array.isArray(value) ? value.filter((item): item is AnyRecord => item !== null && typeof item === 'object' && !Array.isArray(item)) : [];
}

function strings(value: unknown): string[] {
  return Array.isArray(value) ? value.map((item) => text(item)).filter(Boolean) : [];
}

function entries(value: unknown): Array<[string, unknown]> {
  const record = asRecord(value);
  return Object.entries(record).sort(([a], [b]) => a.localeCompare(b));
}

function boolText(value: unknown): string {
  return value === true ? 'true' : 'false';
}

function text(value: unknown, fallback = ''): string {
  if (value === null || value === undefined || value === '') return fallback;
  if (typeof value === 'string') return value;
  if (typeof value === 'number' || typeof value === 'boolean') return String(value);
  return fallback;
}
