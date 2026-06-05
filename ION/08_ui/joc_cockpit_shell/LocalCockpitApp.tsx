import { useCallback, useEffect, useRef, useState } from 'react';
import { JocCockpitShell } from './JocCockpitShell';
import type { IonCockpitViewModel } from './ionRuntimeCockpitTypes';

type LoadState = {
  model?: IonCockpitViewModel;
  error?: string;
  loading: boolean;
};

export function LocalCockpitApp() {
  const [state, setState] = useState<LoadState>({ loading: true });
  const refreshInFlightRef = useRef(false);

  const refresh = useCallback(async () => {
    if (refreshInFlightRef.current) return;
    refreshInFlightRef.current = true;
    try {
      const endpoint = modelEndpoint();
      const response = await fetch(endpoint, { headers: { Accept: 'application/json' }, cache: 'no-store' });
      if (!response.ok) {
        throw new Error(`model_http_${response.status}`);
      }
      const model = normalizeModel(await response.json(), endpoint);
      setState({ model, loading: false });
    } catch (error) {
      setState((previous) => ({
        model: previous.model,
        loading: false,
        error: error instanceof Error ? error.message : 'model_fetch_failed',
      }));
    } finally {
      refreshInFlightRef.current = false;
    }
  }, []);

  useEffect(() => {
    let timer = 0;
    let cancelled = false;
    const refreshDelay = () => (document.visibilityState === 'visible' ? 3000 : 15000);
    const schedule = () => {
      if (cancelled) return;
      timer = window.setTimeout(async () => {
        await refresh();
        schedule();
      }, refreshDelay());
    };
    const handleVisibilityChange = () => {
      window.clearTimeout(timer);
      schedule();
    };
    refresh();
    schedule();
    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => {
      cancelled = true;
      window.clearTimeout(timer);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [refresh]);

  if (state.model) {
    return <JocCockpitShell runtimeProjection={state.model} onRuntimeRefresh={refresh} />;
  }

  return (
    <main className="ion-joc-shell" data-mode="local-model-loading">
      <header className="ion-topbar">
        <div className="ion-brand">CodeGPT</div>
        <div className="ion-state-strip"><span>{state.loading ? 'LOADING MODEL' : 'MODEL UNAVAILABLE'}</span></div>
      </header>
      <section className="ion-main-work-surface">
        <section className="ion-panel ion-hero-panel">
          <div className="ion-section-title">LOCAL COCKPIT MODEL</div>
          <h1>{state.error ?? `Loading ${modelEndpointLabel()}`}</h1>
          <div className="ion-runtime-source-note">No production or live execution authority is granted by this UI.</div>
        </section>
      </section>
    </main>
  );
}

function modelEndpoint() {
  if (typeof window === 'undefined') return '/model.json';
  const cockpit = window.location.pathname.startsWith('/cockpit');
  return cockpit ? cockpitSurfaceEndpoint() : '/model.json';
}

function cockpitSurfaceEndpoint() {
  const hash = (window.location.hash || '').replace(/^#/, '').split('?')[0].toLowerCase();
  const path = window.location.pathname || '';
  if (hash === 'weave' || hash === 'domain-weave' || path.startsWith('/cockpit/weave') || path.startsWith('/cockpit/domain-weave')) return '/cockpit/weave/model.json';
  if (hash === 'ide' || path.startsWith('/cockpit/ide')) return '/cockpit/ide/model.json';
  if (hash === 'codex' || path.startsWith('/cockpit/chat')) return '/cockpit/codex/model.json';
  if (hash === 'apps' || hash.startsWith('apps:') || path.startsWith('/cockpit/apps')) return '/cockpit/apps/model.json';
  if (hash === 'projects' || hash.startsWith('projects:') || path.startsWith('/cockpit/projects')) return '/cockpit/projects/model.json';
  if (hash === 'browser-gpt' || path.startsWith('/cockpit/browser-gpt') || path.startsWith('/cockpit/chatgpt-dom-twin')) return '/cockpit/browser-gpt/model.json';
  if (hash === 'system' || hash === 'diagnostics' || path.startsWith('/cockpit/system')) return '/cockpit/system/model.json';
  if (hash === 'build') return '/cockpit/build/model.json';
  return '/cockpit/model.json';
}

function modelEndpointLabel() {
  return modelEndpoint().split('?')[0];
}

function normalizeModel(payload: unknown, endpoint: string): IonCockpitViewModel {
  if (endpoint.includes('/cockpit/system/model.json') && isRecord(payload) && payload.schema_id === 'ion.system_diagnostics.v1') {
    return systemDiagnosticsShellModel(payload);
  }
  return payload as IonCockpitViewModel;
}

function systemDiagnosticsShellModel(systemDiagnostics: Record<string, unknown>): IonCockpitViewModel {
  const summary = isRecord(systemDiagnostics.summary) ? systemDiagnostics.summary : {};
  const issueCount = numberValue(summary.issue_count);
  const activeDevServers = numberValue(summary.active_dev_server_count);
  const verifiedDevServers = numberValue(summary.http_verified_dev_server_count);
  const generatedAt = stringValue(systemDiagnostics.generated_at) || new Date().toISOString();
  return {
    schema_id: 'ion.cockpit_surface_view_model.v1',
    surface: 'system',
    runtime: {
      version: 'system-diagnostics',
      status: issueCount ? 'attention' : 'ready',
      blocked: false,
      shell_root: 'local-system-control',
    },
    top_bar: {
      objective: 'Local System Control',
      gate_count: 0,
      steward_queue_count: 0,
      operator_queue_pending: 0,
      system_cpu_percent: numberValue(summary.cpu_percent),
      system_swap_percent: numberValue(summary.swap_percent),
      codex_work_request_count: 0,
      browser_carrier_message_count: 0,
      project_count: activeDevServers,
      project_open_blocker_count: issueCount,
    },
    timeline: [
      {
        time: generatedAt,
        source: 'system',
        event_type: 'diagnostics',
        status: issueCount ? 'attention' : 'ready',
        detail: `${activeDevServers} active dev servers / ${verifiedDevServers} HTTP verified / ${issueCount} issues`,
      },
    ],
    receipts: [],
    authority_classes: [],
    queues: { human_gates: [], steward_integration: [], operator_messages: [] },
    system_diagnostics: systemDiagnostics,
  } as IonCockpitViewModel;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function numberValue(value: unknown): number {
  return typeof value === 'number' && Number.isFinite(value) ? value : 0;
}

function stringValue(value: unknown): string {
  return typeof value === 'string' ? value : '';
}
