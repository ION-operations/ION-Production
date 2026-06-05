import type { IonCockpitViewModel, IonContextPackageGraphBranch } from './ionRuntimeCockpitTypes';

export function ContextPackageInspectorPanel({ runtime }: { runtime: IonCockpitViewModel }) {
  const packages = runtime.agents.context_packages ?? [];
  const graph = runtime.context_package_graph;
  const branches = graph?.branches ?? [];
  return (
    <section className="ion-panel ion-context-package-panel">
      <div className="ion-section-title">CONTEXT PACKAGE INSPECTOR</div>
      <div className={`ion-runtime-verdict is-${statusClass(graph?.status)}`}>{text(graph?.status, 'graph missing')}</div>

      <div className="ion-runtime-grid compact">
        <Metric label="branch packs" value={String(graph?.branch_count ?? branches.length)} />
        <Metric label="ready candidates" value={String(graph?.candidate_review_ready_count ?? 0)} />
        <Metric label="blocked" value={String(graph?.blocked_count ?? 0)} />
      </div>

      <div className="ion-context-graph-grid">
        {branches.map((branch) => <ContextBranchCard branch={branch} key={text(branch.path)} />)}
      </div>
      {branches.length === 0 && <div className="ion-empty-state">NO BRANCH CONTEXT GRAPH</div>}

      <div className="ion-context-package-subtitle">SPAWN CONTEXT PACKAGES</div>
      {packages.map((pkg, index) => (
        <article className="ion-runtime-card" key={index}>
          <div className="ion-runtime-card-head"><b>{String(pkg.role ?? 'ROLE')}</b><span>{String(pkg.authority_class ?? 'ACTIVE')}</span></div>
          <code>{String(pkg.path ?? '')}</code>
          {pkg.receipt_path && <code>{String(pkg.receipt_path)}</code>}
        </article>
      ))}
      {packages.length === 0 && <div className="ion-empty-state">NO CONTEXT PACKAGES</div>}
    </section>
  );
}

function ContextBranchCard({ branch }: { branch: IonContextPackageGraphBranch }) {
  const gaps = branch.gaps ?? [];
  const blockers = branch.blockers ?? [];
  const surfaceCounts = branch.surface_counts ?? {};
  const totalSurfaces = surfaceCounts.total ?? 0;
  const authority = branch.authority ?? {};
  return (
    <article className={`ion-runtime-card ${blockers.length > 0 ? 'is-blocked' : 'is-ok'}`}>
      <div className="ion-runtime-card-head"><b>{text(branch.path)}</b><span>{text(branch.package_type)}</span></div>
      <div className="ion-runtime-grid compact">
        <Metric label="surfaces" value={String(totalSurfaces)} />
        <Metric label="gaps" value={String(gaps.length)} />
        <Metric label="candidate" value={text(branch.candidate_valid, 'unknown')} />
      </div>
      <PathRow label="capsule" value={branch.candidate_capsule_path} />
      <PathRow label="parent" value={branch.parent_ref} />
      <PathRow label="readme" value={branch.readme_projection_candidate} />
      <div className="ion-branch-list">
        <span>{text(branch.promotion_readiness)}</span>
        <span>accepted: {text(authority.accepted_state_authority, 'false')}</span>
        <span>production: {text(authority.production_authority, 'false')}</span>
        <span>live: {text(authority.live_execution_authority, 'false')}</span>
        {gaps.slice(0, 3).map((gap) => <span key={gap}>{gap}</span>)}
      </div>
    </article>
  );
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

function statusClass(value: unknown) {
  const normalized = text(value, '').toLowerCase();
  if (normalized.includes('ready') || normalized.includes('active') || normalized.includes('pass')) return 'ready';
  if (normalized.includes('missing') || normalized.includes('blocked') || normalized.includes('fail')) return 'blocked';
  return 'degraded';
}
