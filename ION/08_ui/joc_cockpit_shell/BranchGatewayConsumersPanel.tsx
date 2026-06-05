import { useMemo, useState } from 'react';
import type { IonBranchGatewayServiceControl, IonCockpitViewModel } from './ionRuntimeCockpitTypes';

const CONFIRMATION_TOKEN = 'ION_BOUNDED_WRITE_CONFIRMED';

export function BranchGatewayConsumersPanel({ runtime }: { runtime: IonCockpitViewModel }) {
  const consumers = runtime.branch_gateway_consumers;
  const worker = consumers?.worker_shift;
  const runtimeServices = consumers?.runtime_services;
  const workerSummary = delegated(worker?.status_summary).worker_shift_summary as Record<string, unknown> | undefined;
  const activeWorkers = delegated(worker?.active_workers).workers as Array<Record<string, unknown>> | undefined;
  const coordination = delegated(worker?.coordination_state).queue_coordination_state as Record<string, unknown> | undefined;
  const controls = runtimeServices?.service_controls ?? [];
  const [serviceId, setServiceId] = useState<string>(controls[0]?.service_id ?? '');
  const [confirmation, setConfirmation] = useState('');
  const [idempotencyKey, setIdempotencyKey] = useState('');
  const [prepared, setPrepared] = useState(false);
  const selected = useMemo(
    () => controls.find((control) => control.service_id === serviceId) ?? controls[0],
    [controls, serviceId],
  );
  const plan = selected?.service_reload_plan ?? {};
  const retest = delegated(runtimeServices?.retest_service);
  const gateReady = Boolean(
    selected?.allowed_service_id
    && selected?.shows_plan_before_action
    && confirmation === CONFIRMATION_TOKEN
    && idempotencyKey.trim(),
  );

  return (
    <section className="ion-panel ion-branch-gateway-panel">
      <div className="ion-section-title">BRANCH GATEWAY CONSUMERS</div>
      <div className="ion-runtime-objective">worker_shift and runtime_services are rendered from Branch Gateway read routes. Restart and reload are preview-only in this cockpit pass.</div>
      <div className="ion-branch-gateway-grid">
        <article className="ion-runtime-card is-ready">
          <div className="ion-runtime-card-head"><b>worker_shift</b><span>{String(worker?.status_summary?.ok ?? false)}</span></div>
          <div className="ion-runtime-grid compact">
            <Metric label="active" value={String(workerSummary?.active_worker_count ?? 0)} />
            <Metric label="stale" value={String(workerSummary?.stale_worker_count ?? 0)} />
            <Metric label="leases" value={String(workerSummary?.active_lease_count ?? 0)} />
          </div>
          <div className="ion-branch-list">
            {(activeWorkers ?? []).slice(0, 4).map((row, index) => (
              <span key={`${String(row.worker_id ?? index)}`}>{String(row.worker_id ?? row.status ?? 'worker')}</span>
            ))}
            {(activeWorkers ?? []).length === 0 && <span>no active workers</span>}
          </div>
          <code>{String(coordination?.pressure_hint ?? 'coordination_state_unavailable')}</code>
        </article>

        <article className="ion-runtime-card is-watch">
          <div className="ion-runtime-card-head"><b>runtime_services</b><span>{String(runtimeServices?.service_status?.ok ?? false)}</span></div>
          <div className="ion-runtime-grid compact">
            <Metric label="services" value={String(delegated(runtimeServices?.service_status).service_count ?? controls.length)} />
            <Metric label="plans" value={String(Object.keys(runtimeServices?.service_reload_plans ?? {}).length)} />
            <Metric label="retest" value={String(retest.ok ?? runtimeServices?.retest_service?.ok ?? false)} />
          </div>
          <code>{String(runtimeServices?.mutation_gate?.receipt_handoff_dir ?? 'ION/05_context/current/runtime_services/receipts')}</code>
        </article>
      </div>

      <div className="ion-gated-action-surface">
        <div className="ion-service-gate-fields">
          <label>
            <span>service</span>
            <select value={serviceId} onChange={(event) => { setServiceId(event.target.value); setPrepared(false); }}>
              {controls.map((control) => (
                <option key={control.service_id} value={control.service_id}>{control.service_id}</option>
              ))}
            </select>
          </label>
          <label>
            <span>confirmation</span>
            <input value={confirmation} onChange={(event) => { setConfirmation(event.target.value); setPrepared(false); }} placeholder={CONFIRMATION_TOKEN} />
          </label>
          <label>
            <span>idempotency</span>
            <input value={idempotencyKey} onChange={(event) => { setIdempotencyKey(event.target.value); setPrepared(false); }} placeholder="required" />
          </label>
          <button type="button" disabled={!gateReady} onClick={() => setPrepared(true)}>Prepare handoff</button>
        </div>
        <ReloadPlanPreview selected={selected} plan={plan} prepared={prepared} />
      </div>
    </section>
  );
}

function delegated(value: unknown): Record<string, unknown> {
  if (!value || typeof value !== 'object') return {};
  const payload = value as Record<string, unknown>;
  const delegatedResult = payload.delegated_result;
  return delegatedResult && typeof delegatedResult === 'object'
    ? delegatedResult as Record<string, unknown>
    : {};
}

function Metric({ label, value }: { label: string; value: string }) {
  return <div className="ion-runtime-metric"><span>{label}</span><b>{value}</b></div>;
}

function ReloadPlanPreview({ selected, plan, prepared }: { selected?: IonBranchGatewayServiceControl; plan: Record<string, unknown>; prepared: boolean }) {
  const serviceId = selected?.service_id ?? 'no_service';
  return (
    <div className="ion-reload-plan-preview">
      <div className="ion-section-title">RELOAD PLAN PREVIEW</div>
      <div className="ion-runtime-card-head"><b>{serviceId}</b><span>{selected?.allowed_service_id ? 'allowlisted' : 'blocked'}</span></div>
      <div className="ion-runtime-grid compact">
        <Metric label="would restart" value={String(plan.would_restart ?? false)} />
        <Metric label="self defer" value={String(plan.self_restart_deferred ?? false)} />
        <Metric label="executes here" value={String(selected?.cockpit_executes_mutation ?? false)} />
      </div>
      <code>{Array.isArray(plan.restart_command_shape) ? plan.restart_command_shape.join(' ') : 'plan_unavailable'}</code>
      <p>{String(plan.action_gateway_down_recovery ?? 'Receipt handoff is required after any later approved Branch Gateway action.')}</p>
      <div className="ion-branch-list">
        <span>{selected?.requires_confirmation ? 'confirmation required' : 'confirmation missing'}</span>
        <span>{selected?.requires_idempotency_key ? 'idempotency required' : 'idempotency missing'}</span>
        <span>{selected?.shows_plan_before_action ? 'plan shown first' : 'plan missing'}</span>
        <span>{selected?.receipt_handoff_dir ?? 'receipt handoff missing'}</span>
      </div>
      {prepared && <div className="ion-runtime-source-note">HANDOFF READY: use Branch Gateway {selected?.reload_and_retest_route_id ?? 'reload_and_retest'} with the entered confirmation and idempotency key. No cockpit restart was executed.</div>}
    </div>
  );
}
