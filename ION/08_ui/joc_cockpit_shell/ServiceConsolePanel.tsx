import type { IonCockpitViewModel } from './ionRuntimeCockpitTypes';

export function ServiceConsolePanel({ runtime }: { runtime: IonCockpitViewModel; onRuntimeRefresh?: () => void }) {
  const consoleModel = runtime.service_console;
  const services = consoleModel?.services ?? [];

  return (
    <section className="ion-panel ion-service-console-panel">
      <div className="ion-section-title">LOCAL SERVICE CONSOLE</div>
      <div className={`ion-runtime-verdict is-${consoleModel?.verdict ?? 'unknown'}`}>{consoleModel?.verdict ?? 'unknown'}</div>
      <div className="ion-runtime-objective">{consoleModel?.headline ?? 'NO SERVICE CONSOLE MODEL'}</div>
      <div className="ion-runtime-source-note">{consoleModel?.operator_message ?? 'Visibility only. Restart and reload controls are exposed through Branch Gateway gates above.'}</div>
      <div className="ion-service-console-grid">
        {services.map((service) => {
          const unit = String(service.unit ?? '');
          return (
            <article className={`ion-runtime-card is-${service.severity ?? 'watch'}`} key={unit || String(service.id)}>
              <div className="ion-runtime-card-head"><b>{String(service.label ?? service.id ?? 'service')}</b><span>{String(service.status ?? 'unknown')}</span></div>
              <p>{String(service.role ?? '')}</p>
              <code>{unit}</code>
              {service.finding && <p>{String(service.finding)}</p>}
              <button className="ion-service-action" type="button" disabled title="Use the Branch Gateway controls with service_id, plan preview, confirmation, idempotency, and receipt handoff.">
                BRANCH GATEWAY REQUIRED
              </button>
            </article>
          );
        })}
      </div>
      {services.length === 0 && <div className="ion-empty-state">NO SERVICE CONSOLE MODEL</div>}
    </section>
  );
}
