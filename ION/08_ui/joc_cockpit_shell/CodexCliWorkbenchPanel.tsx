import { useState } from 'react';
import type { IonCockpitViewModel } from './ionRuntimeCockpitTypes';

type TabId = 'map' | 'context' | 'settings' | 'hooks' | 'traces';

const tabs: Array<{ id: TabId; label: string }> = [
  { id: 'map', label: 'system map' },
  { id: 'context', label: 'context' },
  { id: 'settings', label: 'settings' },
  { id: 'hooks', label: 'hooks / skills' },
  { id: 'traces', label: 'traces' },
];

export function CodexCliWorkbenchPanel({ runtime }: { runtime: IonCockpitViewModel }) {
  const [activeTab, setActiveTab] = useState<TabId>('map');
  const [copied, setCopied] = useState<string>('');
  const workbench = runtime.codex_cli_workbench;

  if (!workbench) {
    return (
      <section className="ion-panel ion-codex-cli-workbench-panel">
        <div className="ion-section-title">CODEX CLI WORKBENCH</div>
        <div className="ion-empty-state">NO CODEX CLI WORKBENCH MODEL FOUND</div>
      </section>
    );
  }

  const summary = obj(workbench.summary);
  const context = obj(workbench.context);
  const settings = obj(workbench.settings);
  const hooks = obj(workbench.hooks);
  const skills = obj(workbench.skills);
  const tools = obj(workbench.tools);
  const agents = obj(workbench.agents_and_roles);
  const project = obj(workbench.project_context);
  const chat = obj(workbench.chat);
  const visibility = obj(workbench.visibility_contract);
  const surfaces = list(context.surfaces);
  const hookRuntime = obj(hooks.runtime_receipts);

  async function copyText(id: string, value: unknown) {
    const textValue = text(value, '');
    if (!textValue || typeof navigator === 'undefined' || !navigator.clipboard) return;
    await navigator.clipboard.writeText(textValue);
    setCopied(id);
    window.setTimeout(() => setCopied(''), 1400);
  }

  return (
    <section className="ion-panel ion-codex-cli-workbench-panel">
      <div className="ion-section-title">CODEX CLI WORKBENCH</div>
      <div className={`ion-runtime-verdict is-${verdictClass(workbench.verdict)}`}>{text(workbench.verdict)}</div>
      <p className="ion-runtime-objective">{text(workbench.north_star)}</p>

      <div className="ion-runtime-grid ion-codex-cli-kpi-grid">
        <Metric label="operation" value={summary.operational_state} />
        <Metric label="mount" value={summary.mount_truth_state} />
        <Metric label="capsule rows" value={summary.capsule_entry_count} />
        <Metric label="ctx packages" value={summary.context_package_count} />
        <Metric label="mcp tools" value={summary.mcp_read_only_tool_count} />
        <Metric label="hooks" value={summary.hook_group_count} />
      </div>

      <div className="ion-queue-gateway-strip">
        <span>HIDDEN REASONING: {workbench.hidden_reasoning_exposed ? 'EXPOSED' : 'HIDDEN'}</span>
        <span>SECRETS: {workbench.secrets_authority ? 'AUTHORIZED' : 'BLOCKED'}</span>
        <span>LIVE EXEC: {workbench.live_execution_authority ? 'TRUE' : 'FALSE'}</span>
        <span>ACCEPTED STATE: FALSE</span>
      </div>

      <div className="ion-codex-chat-tabs" role="tablist" aria-label="Codex CLI workbench tabs">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={activeTab === tab.id ? 'is-active' : undefined}
            onClick={() => setActiveTab(tab.id)}
            type="button"
          >
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === 'map' && (
        <div className="ion-codex-tab-body">
          <div className="ion-runtime-grid">
            <Metric label="shell root" value={workbench.shell_root} />
            <Metric label="carrier mode" value={summary.carrier_mode} />
            <Metric label="slash cmds" value={summary.slash_command_count} />
            <Metric label="native skills" value={summary.native_skill_installed_count} />
            <Metric label="chat turns" value={summary.chat_turn_count} />
            <Metric label="runs" value={summary.response_run_count} />
          </div>
          <RecordList title="visible surfaces" records={list(visibility.visible)} />
          <RecordList title="blocked surfaces" records={list(visibility.not_visible)} />
          <RecordList title="capability bindings" records={list(obj(workbench.carrier_os).codex_native_capability_bindings)} />
          <PathRow label="content root" value={workbench.content_root} />
        </div>
      )}

      {activeTab === 'context' && (
        <div className="ion-codex-tab-body">
          <div className="ion-runtime-grid">
            <Metric label="route ok" value={project.route_ok} />
            <Metric label="route entries" value={project.route_entry_count} />
            <Metric label="long horizon" value={obj(context.long_horizon).epoch_count} />
          </div>
          <p className="ion-runtime-objective">{text(context.witness_policy)}</p>
          <div className="ion-context-surface-list">
            {surfaces.map((surface, index) => {
              const id = text(surface.surface_id, `surface-${index}`);
              return (
                <article className="ion-runtime-card ion-context-surface-card" key={id}>
                  <div className="ion-runtime-card-head">
                    <span>{id}</span>
                    <button type="button" onClick={() => copyText(id, surface.excerpt)}>{copied === id ? 'copied' : 'copy'}</button>
                  </div>
                  <p>{text(surface.role)} / {text(surface.line_count)} lines / {text(surface.bytes)} bytes</p>
                  <code>{text(surface.path)}</code>
                  <pre>{text(surface.excerpt, 'excerpt unavailable')}</pre>
                </article>
              );
            })}
          </div>
        </div>
      )}

      {activeTab === 'settings' && (
        <div className="ion-codex-tab-body">
          <div className="ion-runtime-grid">
            <Metric label="codex cli" value={obj(settings).codex_cli_available} />
            <Metric label="profiles" value={list(obj(obj(settings).project_config).profile_names).length} />
            <Metric label="mcp servers" value={list(obj(obj(settings).project_config).mcp_server_names).length} />
          </div>
          <PathRow label="binary" value={obj(settings).codex_binary_ref} />
          <PathRow label="project config" value={obj(obj(settings).project_config).path_ref} />
          <PathRow label="codex home" value={obj(obj(settings).codex_home).path_ref} />
          <RecordList title="mcp servers" records={list(obj(obj(settings).project_config).mcp_server_names)} />
          <RecordList title="profiles" records={list(obj(obj(settings).project_config).profile_names)} />
          <JsonBlock title="redacted config shape" value={obj(obj(settings).project_config).redacted_shape} />
        </div>
      )}

      {activeTab === 'hooks' && (
        <div className="ion-codex-tab-body ion-queue-file-grid">
          <div>
            <div className="ion-runtime-grid">
              <Metric label="hook refs" value={`${text(obj(hooks.required_refs).required_refs_present, '0')}/${text(obj(hooks.required_refs).required_ref_count, '0')}`} />
              <Metric label="hook groups" value={hookRuntime.hook_group_count} />
              <Metric label="skill refs" value={`${text(skills.required_refs_present, '0')}/${text(skills.required_ref_count, '0')}`} />
            </div>
            <RecordList title="missing hooks" records={list(obj(hooks.required_refs).missing_required_refs)} />
            <RecordList title="hook receipt groups" records={list(hookRuntime.groups).map((group) => ({ name: group.hook, status: group.receipt_count_sampled }))} />
          </div>
          <div>
            <RecordList title="slash commands" records={list(tools.slash_commands)} />
            <RecordList title="mcp read-only tools" records={list(tools.mcp_read_only_tools)} />
            <JsonBlock title="native skills" value={skills.native_codex_skill_installation} />
          </div>
        </div>
      )}

      {activeTab === 'traces' && (
        <div className="ion-codex-tab-body ion-queue-file-grid">
          <div>
            <div className="ion-runtime-grid">
              <Metric label="chat verdict" value={chat.verdict} />
              <Metric label="turn traces" value={chat.trace_count} />
              <Metric label="response runs" value={chat.response_run_count} />
            </div>
            <RecordList title="latest response runs" records={list(chat.latest_runs)} />
          </div>
          <div>
            <RecordList title="role phases" records={list(obj(agents.role_phase_contract).role_phase_sequence)} />
            <JsonBlock title="spawn plan" value={agents.spawn_plan} />
            <RecordList title="surface errors" records={list(workbench.surface_errors)} />
          </div>
        </div>
      )}
    </section>
  );
}

function Metric({ label, value }: { label: string; value: unknown }) {
  return (
    <div className="ion-runtime-metric">
      <span>{label}</span>
      <b>{text(value)}</b>
    </div>
  );
}

function PathRow({ label, value }: { label: string; value: unknown }) {
  return (
    <div className="ion-path-row">
      <span>{label}</span>
      <code>{text(value, '')}</code>
    </div>
  );
}

function RecordList({ title, records = [] }: { title: string; records?: Array<Record<string, unknown>> }) {
  return (
    <div className="ion-runtime-card">
      <div className="ion-runtime-card-head"><span>{title}</span><b>{records.length}</b></div>
      {records.map((record, index) => (
        <div className="ion-codex-record" key={`${title}-${String(record.path ?? record.command ?? record.name ?? record.capability ?? index)}`}>
          <b>{text(record.name || record.command || record.capability || record.status || record.path, `item-${index + 1}`)}</b>
          <span>{text(record.status || record.mode || record.authority || record.ion_binding || record.receipt_count_sampled, '')}</span>
          <code>{text(record.path || record.maps_to || record.primary_ref || record.error, '')}</code>
        </div>
      ))}
      {records.length === 0 && <div className="ion-empty-state">NONE</div>}
    </div>
  );
}

function JsonBlock({ title, value }: { title: string; value: unknown }) {
  return (
    <div className="ion-runtime-card">
      <div className="ion-runtime-card-head"><span>{title}</span><b>json</b></div>
      <pre>{JSON.stringify(value ?? {}, null, 2)}</pre>
    </div>
  );
}

function obj(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' && !Array.isArray(value) ? value as Record<string, unknown> : {};
}

function list(value: unknown): Array<Record<string, unknown>> {
  if (!Array.isArray(value)) return [];
  return value.map((item) => (item && typeof item === 'object' && !Array.isArray(item) ? item as Record<string, unknown> : { name: item }));
}

function text(value: unknown, fallback = 'unknown') {
  if (typeof value === 'string' && value.trim()) return value.trim();
  if (typeof value === 'number' || typeof value === 'boolean') return String(value);
  return fallback;
}

function verdictClass(value: unknown) {
  const normalized = text(value, '').toLowerCase();
  if (normalized.includes('ready') || normalized.includes('pass') || normalized.includes('ok')) return 'ready';
  if (normalized.includes('blocked') || normalized.includes('fail') || normalized.includes('error')) return 'blocked';
  return 'degraded';
}
