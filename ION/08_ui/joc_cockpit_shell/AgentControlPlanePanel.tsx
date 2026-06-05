import { useMemo, useState } from 'react';
import type { IonAgentControlPlane, IonCockpitViewModel } from './ionRuntimeCockpitTypes';

export type AgentControlTabId = 'agents' | 'comms' | 'weave' | 'domains' | 'automations' | 'settings';
type WorkTabId = 'assistant' | 'tools' | 'context' | 'mount' | 'edits' | 'agents' | 'events' | 'receipts' | 'raw';
type AgentPageTabId = 'overview' | 'chat' | 'context' | 'codex' | 'hooks' | 'skills' | 'tools' | 'runs' | 'files' | 'receipts' | 'diag' | 'settings';
type AgentCommsInspectorMode = 'profile' | 'timeline' | 'relays' | 'contacts' | 'rooms';

export const agentControlTabs: Array<{ id: AgentControlTabId; label: string }> = [
  { id: 'agents', label: 'AGENT' },
  { id: 'comms', label: 'TEAM COMMS' },
  { id: 'weave', label: 'DOMAIN WEAVE' },
  { id: 'domains', label: 'DOMAINS' },
  { id: 'automations', label: 'AUTOMATIONS' },
  { id: 'settings', label: 'SETTINGS' },
];

const workTabs: Array<{ id: WorkTabId; label: string }> = [
  { id: 'assistant', label: 'ASSISTANT' },
  { id: 'tools', label: 'TOOLS' },
  { id: 'context', label: 'CONTEXT' },
  { id: 'mount', label: 'MOUNT' },
  { id: 'edits', label: 'EDITS' },
  { id: 'agents', label: 'AGENTS' },
  { id: 'events', label: 'EVENTS' },
  { id: 'receipts', label: 'RECEIPTS' },
  { id: 'raw', label: 'RAW' },
];

const agentPageTabs: Array<{ id: AgentPageTabId; label: string }> = [
  { id: 'overview', label: 'OVERVIEW' },
  { id: 'chat', label: 'CHAT' },
  { id: 'context', label: 'CONTEXT' },
  { id: 'codex', label: 'CODEX CLI' },
  { id: 'hooks', label: 'HOOKS' },
  { id: 'skills', label: 'SKILLS' },
  { id: 'tools', label: 'TOOLS' },
  { id: 'runs', label: 'RUNS' },
  { id: 'files', label: 'FILES' },
  { id: 'receipts', label: 'RECEIPTS' },
  { id: 'diag', label: 'DIAG' },
  { id: 'settings', label: 'SETTINGS' },
];

const MENTION_TARGET = '__mentions__';

export function AgentControlPlanePanel({
  runtime,
  onRuntimeRefresh,
  activeTab: controlledActiveTab,
  hideSubtabs = false,
  onActiveTabChange,
}: {
  runtime: IonCockpitViewModel;
  onRuntimeRefresh?: () => void;
  activeTab?: AgentControlTabId;
  hideSubtabs?: boolean;
  onActiveTabChange?: (tab: AgentControlTabId) => void;
}) {
  const model = runtime.agent_control_plane;
  const agents = records(model?.agents);
  const domains = records(model?.domains);
  const [localActiveTab, setLocalActiveTab] = useState<AgentControlTabId>(() => {
    if (typeof window === 'undefined') return 'agents';
    if (window.location.hash === '#team-comms') return 'comms';
    if (window.location.hash === '#domain-weave') return 'weave';
    if (window.location.hash === '#domains') return 'domains';
    if (window.location.hash === '#automations') return 'automations';
    if (window.location.hash === '#agent-settings') return 'settings';
    return 'agents';
  });
  const [selectedDomainId, setSelectedDomainId] = useState<string>('');
  const [requestState, setRequestState] = useState<Record<string, unknown> | null>(null);
  const [busy, setBusy] = useState(false);
  const activeTab = controlledActiveTab ?? localActiveTab;
  const setActiveAgentTab = (tab: AgentControlTabId) => {
    if (controlledActiveTab === undefined) setLocalActiveTab(tab);
    onActiveTabChange?.(tab);
    if (typeof window !== 'undefined') {
      window.location.hash = tab === 'comms' ? 'team-comms' : tab === 'weave' ? 'domain-weave' : tab === 'settings' ? 'agent-settings' : tab;
    }
  };
  const selectedDomain = useMemo(() => {
    const id = selectedDomainId || text(domains[0]?.domain_id);
    return domains.find((domain) => text(domain.domain_id) === id) ?? domains[0] ?? {};
  }, [domains, selectedDomainId]);

  if (!model) {
    return <section className="ion-panel ion-agent-empty">AGENT CONTROL PLANE MODEL MISSING</section>;
  }

  return (
    <section className={`ion-agent-cockpit-shell${hideSubtabs ? ' has-external-subnav' : ''}`} aria-label="ION agent control plane">
      <header className="ion-agent-top-strip">
        <div>
          <div className="ion-section-title">ION AGENT CONTROL PLANE</div>
          <b>{text(model.verdict, 'UNKNOWN')}</b>
        </div>
        <Metric label="agents" value={model.summary?.agent_count} />
        <Metric label="invocable" value={model.summary?.invocable_agent_count} />
        <Metric label="domains" value={model.summary?.domain_count} />
        <Metric label="mounts" value={`${text(model.summary?.materialized_codex_mount_count, '0')}/${text(model.summary?.codex_mount_count, '0')}`} />
        <Metric label="weave" value={`${text(model.summary?.covered_domain_count, text(model.summary?.domain_weaver_usable_domain_count, '0'))}/${text(model.summary?.domain_count, '0')}`} />
        <Metric label="gaps" value={model.summary?.domain_weaver_gap_count} />
        <Metric label="queued" value={model.summary?.queued_agent_codex_work_request_count} />
        <Metric label="active" value={model.summary?.active_process_running ? 'yes' : 'no'} />
        <Metric label="dispatch" value={`${text(model.summary?.dispatcher_actionable_run_count, '0')}/${text(model.summary?.dispatcher_active_worker_count, '0')}`} />
      </header>

      {!hideSubtabs ? (
        <nav className="ion-agent-subtabs" aria-label="Agent control plane sections">
          {agentControlTabs.map((tab) => (
            <button
              className={activeTab === tab.id ? 'is-active' : undefined}
              key={tab.id}
              onClick={() => setActiveAgentTab(tab.id)}
              type="button"
            >
              {tab.label}
            </button>
          ))}
        </nav>
      ) : null}

      <div className="ion-agent-layout">
        <main className="ion-agent-main-pane">
          {activeTab === 'agents' && (
            <AgentsDirectoryView
              agents={agents}
              busy={busy}
              model={model}
              onRuntimeRefresh={onRuntimeRefresh}
              setBusy={setBusy}
              setRequestState={setRequestState}
            />
          )}
          {activeTab === 'comms' && (
            <TeamCommsView
              agents={agents}
              busy={busy}
              runtime={runtime}
              taskReturnAutomationDiagnoses={records(runtime.codex_capsule_chat?.latest_task_return_automation_diagnoses)}
              taskReturnMachineReceipts={records(runtime.codex_capsule_chat?.latest_task_return_machine_receipts)}
              model={model}
              onRuntimeRefresh={onRuntimeRefresh}
              setBusy={setBusy}
              setRequestState={setRequestState}
            />
          )}
          {activeTab === 'weave' && (
            <DomainWeaverOpsView
              domainWeaver={record(model.domain_weaver)}
              runtime={runtime}
              domains={domains}
            />
          )}
          {activeTab === 'domains' && (
            <DomainsView
              domainWeaver={record(model.domain_weaver)}
              domains={domains}
              selectedDomain={selectedDomain}
              setSelectedDomainId={setSelectedDomainId}
            />
          )}
          {activeTab === 'automations' && (
            <AutomationKernelView
              automation={record(runtime.automation_control_plane)}
              busy={busy}
              onRuntimeRefresh={onRuntimeRefresh}
              setBusy={setBusy}
              setRequestState={setRequestState}
            />
          )}
          {activeTab === 'settings' && <AgentSettingsView model={model} requestState={requestState} />}
        </main>
      </div>
    </section>
  );
}

function AgentsDirectoryView({
  agents,
  busy,
  model,
  onRuntimeRefresh,
  setBusy,
  setRequestState,
}: {
  agents: Array<Record<string, unknown>>;
  busy: boolean;
  model: IonAgentControlPlane;
  onRuntimeRefresh?: () => void;
  setBusy: (busy: boolean) => void;
  setRequestState: (state: Record<string, unknown> | null) => void;
}) {
  const starter = record(model.starter_capsule);
  const preferredAgent = agents.find((agent) => text(agent.role_id) === 'role.steward')
    ?? agents.find((agent) => text(agent.role_id) === 'role.codex_carrier_steward')
    ?? agents[0];
  const [openAgentId, setOpenAgentId] = useState(() => {
    if (typeof window === 'undefined') return '';
    const match = window.location.hash.match(/^#agent:(.+)$/);
    return match ? decodeURIComponent(match[1]) : '';
  });
  const openAgentPage = (id: string) => {
    setOpenAgentId(id);
    if (typeof window !== 'undefined') {
      window.location.hash = `agent:${encodeURIComponent(id)}`;
    }
  };
  const closeAgentPage = () => {
    setOpenAgentId('');
    if (typeof window !== 'undefined' && window.location.hash.startsWith('#agent:')) {
      window.history.replaceState(null, '', `${window.location.pathname}${window.location.search}`);
    }
  };
  const openAgent = openAgentId
    ? agents.find((agent) => text(agent.role_id || agent.agent_id) === openAgentId) ?? {}
    : {};
  if (Object.keys(openAgent).length) {
    return <AgentPageView agent={openAgent} model={model} onBack={closeAgentPage} />;
  }
  return (
    <section className="ion-agent-directory-view">
      <header className="ion-agent-directory-head">
        <div>
          <div className="ion-section-title">AGENT ROSTER</div>
          <h1>ION AGENTS</h1>
          <p>Registry-backed roster, domain bindings, context/capsule status, Codex mounts, comms packets, and broker-prepared workpacks.</p>
        </div>
        <Metric label="agents" value={agents.length} />
        <Metric label="invocable" value={agents.filter((agent) => truth(agent.invocable)).length} />
      </header>
      <AgentRosterPanel
        agents={agents}
        busy={busy}
        model={model}
        onRuntimeRefresh={onRuntimeRefresh}
        setBusy={setBusy}
        setRequestState={setRequestState}
      />
      <section className="ion-agent-starter-strip">
        <div>
          <div className="ion-section-title">NEW CONTEXT STARTER</div>
          <b>{text(starter.verdict, 'STARTER NOT MATERIALIZED')}</b>
          <p>Single-capsule starter for registry/domain-backed folders.</p>
        </div>
        <Path label="operator final" value={text(starter.operator_final_path)} />
        <Path label="copy policy" value={text(starter.copy_policy)} />
        <Path label="launch" value={text(starter.launch_command_template)} />
        <Path label="create" value={text(starter.create_command_template)} />
      </section>
      <div className="ion-agent-page-grid">
        {agents.map((agent) => {
          const mount = record(agent.native_codex_mount);
          const evidence = record(agent.agent_page_evidence);
          const identity = record(evidence.identity);
          const proof = record(evidence.proof);
          const contextSystem = record(evidence.context_system);
          const checks = records(proof.checks);
          const id = text(agent.role_id || agent.agent_id);
          return (
            <button className={`ion-agent-page-card${id === text(preferredAgent?.role_id || preferredAgent?.agent_id) ? ' is-primary' : ''}`} key={id} onClick={() => openAgentPage(id)} type="button">
              <div className="ion-agent-page-card-head">
                <div>
                  <span>{text(identity.agent_kind || agent.registry_primary_domain || agent.backend_carrier_id, 'domain pending')}</span>
                  <h2>{text(agent.display_name || agent.role_id)}</h2>
                </div>
                <b>{truth(proof.critical_ready) ? 'PROVEN' : truth(agent.invocable) ? 'READY' : text(agent.context_system_status, 'CONTEXT')}</b>
              </div>
              <p>{text(contextSystem.package_strategy || agent.package_strategy || agent.default_mount_posture || agent.context_system_card)}</p>
              <div className="ion-agent-page-tab-strip is-proof">
                <span className={truth(identity.is_ion_context_system) ? 'is-on' : undefined}>ION</span>
                <span className={truth(identity.is_capsule_agent) ? 'is-on' : undefined}>CAPSULE</span>
                <span className={truth(identity.is_codex_native_mount) ? 'is-on' : undefined}>CODEX</span>
                <span className={truth(identity.is_portable_package_agent) ? 'is-on' : undefined}>PACKAGE</span>
              </div>
              <div className="ion-agent-page-facts">
                <Path label="context card" value={text(agent.context_system_card)} />
                <Path label="active package" value={text(mount.active_context_package_md_path)} />
                <Path label="codex cwd" value={text(record(mount.native_codex).launch_cwd || mount.mount_path)} />
              </div>
              <div className="ion-agent-page-lists">
                <List label="proof checks" values={checks.map((check) => `${truth(check.ok) ? 'ok' : 'missing'}: ${text(check.label)}`).slice(0, 6)} />
                <List label="read zones" values={recordsToStrings(agent.default_read_zones).slice(0, 5)} />
              </div>
              <div className="ion-agent-open-row">OPEN AGENT PAGE</div>
            </button>
          );
        })}
      </div>
    </section>
  );
}

function AgentRosterPanel({
  agents,
  busy,
  model,
  onRuntimeRefresh,
  setBusy,
  setRequestState,
}: {
  agents: Array<Record<string, unknown>>;
  busy: boolean;
  model: IonAgentControlPlane;
  onRuntimeRefresh?: () => void;
  setBusy: (busy: boolean) => void;
  setRequestState: (state: Record<string, unknown> | null) => void;
}) {
  const roster = record(model.roster);
  const communicationDirectory = record(roster.communication_directory);
  const automationPolicy = record(communicationDirectory.automation_comms_policy);
  const automationLimits = record(automationPolicy.limits);
  const rosterAgents = records(roster.agents).length ? records(roster.agents) : agents;
  const rosterDomains = records(roster.domains);
  const templates = records(roster.spawn_templates);
  const firstAgent = rosterAgents.find((agent) => truth(agent.spawn_supported) || truth(agent.invocable)) ?? rosterAgents[0] ?? {};
  const [selectedAgentId, setSelectedAgentId] = useState(text(firstAgent.role_id || firstAgent.agent_id));
  const selectedAgent = rosterAgents.find((agent) => text(agent.role_id || agent.agent_id) === selectedAgentId) ?? firstAgent;
  const defaultDomain = text(selectedAgent.registry_primary_domain || first(recordsToStrings(selectedAgent.domain_ids)) || rosterDomains[0]?.domain_id);
  const [selectedDomainId, setSelectedDomainId] = useState(defaultDomain);
  const selectedDomain = rosterDomains.find((domain) => text(domain.domain_id) === (selectedDomainId || defaultDomain)) ?? rosterDomains[0] ?? {};
  const [templateId, setTemplateId] = useState(text(templates[0]?.template_id, 'agent_workpack_decision'));
  const selectedTemplate = templates.find((template) => text(template.template_id) === templateId) ?? templates[0] ?? {};
  const [objective, setObjective] = useState('Review this packet and return the next proof-bound decision.');
  const [body, setBody] = useState('');
  const [automationGuard, setAutomationGuard] = useState(false);
  const [automationId, setAutomationId] = useState('cockpit-agent-comms');
  const [automationWindowMinutes, setAutomationWindowMinutes] = useState(Number(automationLimits.default_window_minutes ?? 60));
  const [automationPromptLimit, setAutomationPromptLimit] = useState(Number(automationLimits.default_prompt_limit ?? 12));
  const [automationTimeBudgetMinutes, setAutomationTimeBudgetMinutes] = useState(Number(automationLimits.default_time_budget_minutes ?? 120));

  const spawnFromTemplate = async (dispatchMode: 'comms_only' | 'prepare_workpack' | 'queue_workpack') => {
    if (!selectedAgentId || !objective.trim() || busy) {
      setRequestState({ ok: false, finding: selectedAgentId ? 'objective_required' : 'agent_required' });
      return;
    }
    setBusy(true);
    try {
      const response = await fetch('/cockpit/agents/spawn-template', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({
          template_id: templateId,
          dispatch_mode: dispatchMode,
          agent: selectedAgentId,
          domain_id: selectedDomainId || defaultDomain || undefined,
          objective,
          body: body || objective,
          ...(automationGuard
            ? {
                dispatch_source: 'automation',
                automation_id: automationId || 'cockpit-agent-comms',
                automation_window_minutes: automationWindowMinutes,
                automation_prompt_limit: automationPromptLimit,
                automation_time_budget_minutes: automationTimeBudgetMinutes,
              }
            : {}),
          source_refs: [
            text(selectedAgent.context_system_card),
            text(selectedDomain.source_registry),
            text(selectedDomain.path),
          ].filter(Boolean),
          artifact_refs: [
            text(selectedAgent.active_context_package),
            text(selectedAgent.codex_mount_path),
          ].filter(Boolean),
        }),
      });
      const result = (await response.json()) as Record<string, unknown>;
      setRequestState(result);
      await onRuntimeRefresh?.();
    } catch (error) {
      setRequestState({ ok: false, finding: error instanceof Error ? error.message : 'spawn_template_failed' });
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="ion-agent-roster-panel">
      <div className="ion-agent-roster-summary">
        <div>
          <div className="ion-section-title">ROSTER / DOMAIN MAP</div>
          <b>{text(roster.policy, 'Registry/domain/context projection')}</b>
        </div>
        <Metric label="agents" value={roster.agent_count ?? rosterAgents.length} />
        <Metric label="capsule" value={roster.capsule_agent_count ?? 0} />
        <Metric label="available" value={communicationDirectory.available_agent_count ?? 0} />
        <Metric label="domains built" value={roster.domain_built_count ?? 0} />
        <Metric label="templates" value={templates.length} />
      </div>
      <div className="ion-agent-roster-workbench">
        <section className="ion-agent-roster-table">
          <div className="ion-section-title">AGENT ROSTER</div>
          <div className="ion-agent-roster-scroll">
            {rosterAgents.map((agent) => {
              const id = text(agent.role_id || agent.agent_id);
              return (
                <button className={id === selectedAgentId ? 'is-active' : undefined} key={id} onClick={() => {
                  setSelectedAgentId(id);
                  setSelectedDomainId(text(agent.registry_primary_domain || first(recordsToStrings(agent.domain_ids)) || selectedDomainId));
                }} type="button">
                  <b>{text(agent.display_name || id)}</b>
                  <span>{text(agent.roster_status || agent.context_system_status, 'unknown')}</span>
                  <code>{text(agent.registry_primary_domain || first(recordsToStrings(agent.domain_ids)), 'no domain')}</code>
                  <small>{truth(agent.is_capsule_agent) ? 'capsule' : 'context'} / {truth(agent.is_codex_native_mount) ? 'codex' : 'mount pending'} / {truth(agent.available_for_comms) ? 'comms' : 'quiet'} / {truth(agent.spawn_supported || agent.invocable) ? 'spawn ready' : 'context only'}</small>
                </button>
              );
            })}
          </div>
        </section>
        <section className="ion-agent-domain-matrix">
          <div className="ion-section-title">DOMAIN AGENT MATRIX</div>
          <div className="ion-agent-domain-scroll">
            {rosterDomains.map((domain) => (
              <button className={text(domain.domain_id) === selectedDomainId ? 'is-active' : undefined} key={text(domain.domain_id)} onClick={() => setSelectedDomainId(text(domain.domain_id))} type="button">
                <b>{text(domain.domain_id)}</b>
                <span>{text(domain.roster_status, 'needs review')}</span>
                <small>{text(domain.agent_count, '0')} agents / {text(domain.capsule_agent_count, '0')} capsule / {text(domain.invocable_agent_count, '0')} invocable</small>
              </button>
            ))}
            {rosterDomains.length === 0 ? <div className="ion-empty-state">NO DOMAIN ROSTER PROJECTION</div> : null}
          </div>
        </section>
        <section className="ion-agent-spawn-template-panel">
          <div className="ion-section-title">SPAWN TEMPLATE</div>
          <div className="ion-agent-spawn-form">
            <select aria-label="Spawn template" value={templateId} onChange={(event) => setTemplateId(event.target.value)}>
              {templates.map((template) => (
                <option key={text(template.template_id)} value={text(template.template_id)}>
                  {text(template.label || template.template_id)}
                </option>
              ))}
              {templates.length === 0 ? <option value="agent_workpack_decision">WORKPACK DECISION</option> : null}
            </select>
            <select aria-label="Spawn agent" value={selectedAgentId} onChange={(event) => setSelectedAgentId(event.target.value)}>
              {rosterAgents.map((agent) => (
                <option key={text(agent.role_id || agent.agent_id)} value={text(agent.role_id || agent.agent_id)}>
                  {text(agent.display_name || agent.role_id)}
                </option>
              ))}
            </select>
            <select aria-label="Spawn domain" value={selectedDomainId || defaultDomain} onChange={(event) => setSelectedDomainId(event.target.value)}>
              {rosterDomains.map((domain) => (
                <option key={text(domain.domain_id)} value={text(domain.domain_id)}>
                  {text(domain.domain_id)}
                </option>
              ))}
            </select>
            <input aria-label="Spawn objective" value={objective} onChange={(event) => setObjective(event.target.value)} />
            <textarea aria-label="Spawn body" rows={4} value={body} onChange={(event) => setBody(event.target.value)} placeholder={text(selectedTemplate.description, 'Packet body')} />
            <div className="ion-agent-automation-limits">
              <label>
                <input checked={automationGuard} onChange={(event) => setAutomationGuard(event.target.checked)} type="checkbox" />
                <span>AUTOMATION LIMITS</span>
              </label>
              <input aria-label="Automation id" disabled={!automationGuard} value={automationId} onChange={(event) => setAutomationId(event.target.value)} />
              <input aria-label="Automation window minutes" disabled={!automationGuard} min={1} type="number" value={automationWindowMinutes} onChange={(event) => setAutomationWindowMinutes(Number(event.target.value || 1))} />
              <input aria-label="Automation prompt limit" disabled={!automationGuard} min={1} type="number" value={automationPromptLimit} onChange={(event) => setAutomationPromptLimit(Number(event.target.value || 1))} />
              <input aria-label="Automation time budget minutes" disabled={!automationGuard} min={1} type="number" value={automationTimeBudgetMinutes} onChange={(event) => setAutomationTimeBudgetMinutes(Number(event.target.value || 1))} />
              <small>window / prompts / time budget</small>
            </div>
            <div className="ion-agent-spawn-actions">
              <button disabled={busy || !objective.trim()} onClick={() => void spawnFromTemplate('comms_only')} type="button">SEND COMMS</button>
              <button disabled={busy || !objective.trim()} onClick={() => void spawnFromTemplate('prepare_workpack')} type="button">PREPARE WORKPACK</button>
              <button disabled={busy || !objective.trim()} onClick={() => void spawnFromTemplate('queue_workpack')} type="button">QUEUE WORKPACK</button>
            </div>
          </div>
        </section>
      </div>
    </section>
  );
}

function AgentPageView({
  agent,
  model,
  onBack,
}: {
  agent: Record<string, unknown>;
  model: IonAgentControlPlane;
  onBack: () => void;
}) {
  const [tab, setTab] = useState<AgentPageTabId>('overview');
  const mount = record(agent.native_codex_mount);
  const evidence = record(agent.agent_page_evidence);
  const identity = record(evidence.identity);
  const authority = record(evidence.authority);
  const contextSystem = record(evidence.context_system);
  const contextCard = record(contextSystem.card);
  const codexMount = record(evidence.codex_mount);
  const nativeCodex = coalesceRecord(codexMount.native_codex, mount.native_codex);
  const capsule = record(evidence.capsule);
  const addressBook = record(evidence.address_book);
  const addressBookSummary = record(addressBook.summary);
  const addressBookGroups = record(addressBook.contact_groups);
  const portablePackage = record(evidence.portable_package);
  const domainEvidence = record(evidence.domain);
  const proof = record(evidence.proof);
  const diagnostics = record(evidence.diagnostics);
  const proofChecks = records(proof.checks);
  const mountFiles = records(codexMount.files);
  const capsuleFiles = records(capsule.files);
  const contextPaths = records(contextSystem.context_paths);
  const packagePathProbes = records(portablePackage.path_probes);
  const allRuns = records(model.runs?.recent_invocations);
  const runs = allRuns.filter((run) => agentMatchesRecord(run, agent));
  const communications = record(model.communications);
  const teamComms = record(communications.team_comms);
  const compactHomeViews = records(teamComms.agent_home_views);
  const compactHomeView = selectAgentHomeView(compactHomeViews, text(agent.role_id || agent.agent_id));
  const agentMessages = records(teamComms.recent_messages)
    .filter((message) => agentMatchesRecord(message, agent))
    .sort((left, right) => text(left.created_at).localeCompare(text(right.created_at)));
  const timeline = records(communications.timeline).filter((event) => agentMatchesRecord(event, agent));
  const relays = records(communications.relays).filter((relay) => agentMatchesRecord(relay, agent));
  const receipts = records(communications.receipts).filter((receipt) => agentMatchesRecord(receipt, agent));
  const agentKind = text(identity.agent_kind, 'registry_only_candidate');
  return (
    <section className="ion-agent-detail-page">
      <header className="ion-agent-detail-hero">
        <button onClick={onBack} type="button">ALL AGENTS</button>
        <div>
          <div className="ion-section-title">AGENT PAGE</div>
          <h1>{text(agent.display_name || agent.role_id, 'NO AGENT')}</h1>
          <p>{agentKind} / {text(contextSystem.package_strategy || agent.package_strategy || agent.default_mount_posture || agent.context_system_card)}</p>
        </div>
        <Metric label="domain" value={identity.domain_id || agent.registry_primary_domain} />
        <Metric label="ION" value={truth(identity.is_ion_context_system) ? 'yes' : 'no'} />
        <Metric label="capsule" value={truth(identity.is_capsule_agent) ? 'yes' : 'no'} />
        <Metric label="contacts" value={addressBookSummary.contact_count ?? 0} />
        <Metric label="package" value={truth(identity.is_portable_package_agent) ? 'yes' : 'no'} />
        <Metric label="runs" value={runs.length} />
      </header>
      <nav className="ion-agent-detail-tabs">
        {agentPageTabs.map((item) => (
          <button className={tab === item.id ? 'is-active' : undefined} key={item.id} onClick={() => setTab(item.id)} type="button">
            {item.label}
          </button>
        ))}
      </nav>
      <main className="ion-agent-detail-body">
        {tab === 'overview' && (
          <div className="ion-agent-detail-grid">
            <section>
              <div className="ion-section-title">IDENTITY</div>
              <div className="ion-agent-evidence-badges">
                <span className={truth(identity.is_ion_context_system) ? 'is-on' : undefined}>ION CONTEXT</span>
                <span className={truth(identity.is_capsule_agent) ? 'is-on' : undefined}>CAPSULE</span>
                <span className={truth(identity.is_codex_native_mount) ? 'is-on' : undefined}>CODEX NATIVE</span>
                <span className={truth(identity.is_portable_package_agent) ? 'is-on' : undefined}>DROP-IN</span>
              </div>
              <Path label="kind" value={agentKind} />
              <Path label="role" value={text(identity.role_id || agent.role_id)} />
              <Path label="domain" value={text(identity.domain_id || agent.registry_primary_domain)} />
              <Path label="carrier" value={text(identity.backend_carrier_id || agent.backend_carrier_id)} />
              <Path label="context card" value={text(contextCard.relpath || contextCard.path || agent.context_system_card)} />
              <Path label="continuity" value={text(identity.continuity_home || agent.continuity_home)} />
            </section>
            <section>
              <div className="ion-section-title">PROOF CHECKS</div>
              <EvidenceCheckList checks={proofChecks} />
            </section>
            <section>
              <div className="ion-section-title">AUTHORITY</div>
              <Metric label="production" value={truth(authority.production_authority) ? 'yes' : 'no'} />
              <Metric label="live exec" value={truth(authority.live_execution_authority) ? 'yes' : 'no'} />
              <Metric label="accepted" value={truth(authority.accepted_state_authority) ? 'yes' : 'no'} />
              <Metric label="secrets" value={truth(authority.secrets_authority) ? 'yes' : 'no'} />
              <Metric label="write" value={authority.write_posture ?? 'none'} />
              <Metric label="invocable" value={truth(authority.invocable) ? 'yes' : 'no'} />
            </section>
            <section>
              <div className="ion-section-title">CODEX MOUNT</div>
              <Path label="cwd" value={text(nativeCodex.launch_cwd || mount.mount_abspath || mount.mount_path)} />
              <Path label="package" value={text(mount.active_context_package_md_path)} />
              <Path label="AGENTS.md" value={text(mount.agents_md_path)} />
              <Path label="config" value={text(mount.config_path)} />
              <List label="command" values={recordsToStrings(nativeCodex.interactive_command_preview || nativeCodex.command_preview).slice(0, 8)} />
            </section>
            <section>
              <div className="ion-section-title">CAPSULE SYSTEM</div>
              <Path label="manifest" value={text(rowByLabel(capsuleFiles, 'ion_context_capsule').relpath || mount.portable_context_manifest_path)} />
              <Path label="mini" value={text(rowByLabel(capsuleFiles, 'mini').relpath || mount.portable_mini_path)} />
              <Path label="capsule" value={text(rowByLabel(capsuleFiles, 'capsule').relpath || mount.portable_capsule_path)} />
              <Path label="long horizon" value={text(rowByLabel(capsuleFiles, 'long_horizon').relpath || mount.portable_long_horizon_path)} />
              <Path label="relationships" value={text(rowByLabel(capsuleFiles, 'relationships').relpath || mount.portable_relationships_path)} />
              <Path label="address book" value={text(rowByLabel(capsuleFiles, 'address_book').relpath || mount.portable_address_book_path)} />
            </section>
            <section>
              <div className="ion-section-title">ADDRESS BOOK</div>
              <Metric label="contacts" value={addressBookSummary.contact_count ?? 0} />
              <Metric label="peers" value={addressBookSummary.shared_domain_peer_count ?? 0} />
              <Metric label="review" value={addressBookSummary.review_contact_count ?? 0} />
              <Path label="path" value={text(addressBook.path || mount.portable_address_book_path)} />
              <List
                label="contact groups"
                values={Object.entries(addressBookGroups)
                  .filter(([, value]) => recordsToStrings(value).length)
                  .map(([key, value]) => `${key}: ${recordsToStrings(value).slice(0, 4).join(', ')}`)
                  .slice(0, 6)}
              />
            </section>
            <section>
              <div className="ion-section-title">PORTABLE PACKAGE</div>
              <Metric label="drop-in" value={truth(portablePackage.drop_in_ready) ? 'ready' : 'missing'} />
              <Metric label="refs copied" value={portablePackage.source_ref_copied_count} />
              <Metric label="refs missing" value={portablePackage.source_ref_missing_count} />
              <Path label="drop-in path" value={text(portablePackage.drop_in_path)} />
              <Path label="zip" value={text(portablePackage.zip_path)} />
              <Path label="sha256" value={text(portablePackage.zip_sha256)} />
            </section>
            <section className="is-wide">
              <div className="ion-section-title">AGENT HOME (COMPACT PROJECTION)</div>
              <CompactHomeProjectionCard homeView={compactHomeView} />
            </section>
            <section className="is-wide">
              <div className="ion-section-title">ACTIVE CONTEXT PACKAGE</div>
              <Path label="class" value={text(contextSystem.default_active_package_class || agent.default_active_package_class)} />
              <Path label="strategy" value={text(contextSystem.package_strategy || agent.package_strategy)} />
              <ExcerptBlock value={text(rowByLabel(mountFiles, 'active_context_package_md').excerpt || rowByLabel(capsuleFiles, 'active_context_package_md').excerpt)} />
            </section>
            <section>
              <div className="ion-section-title">ACTIVITY</div>
              <Metric label="runs" value={runs.length} />
              <Metric label="relays" value={relays.length} />
              <Metric label="receipts" value={receipts.length} />
              <Metric label="events" value={timeline.length} />
              <Path label="latest request" value={text(runs[0]?.codex_work_request_path)} />
              <Path label="latest return" value={text(runs[0]?.latest_return_packet_path)} />
            </section>
          </div>
        )}
        {tab === 'chat' && <AgentConversationPanel messages={agentMessages} relays={relays} timeline={timeline} title={`${text(agent.display_name || agent.role_id)} CHAT`} />}
        {tab === 'context' && (
          <div className="ion-agent-detail-grid">
            <section className="is-wide">
              <div className="ion-section-title">CONTEXT SYSTEM CARD</div>
              <Path label="path" value={text(contextCard.relpath || contextCard.path)} />
              <Metric label="exists" value={truth(contextCard.exists) ? 'yes' : 'no'} />
              <Metric label="bytes" value={contextCard.bytes} />
              <ExcerptBlock value={text(contextCard.excerpt)} />
            </section>
            <section>
              <div className="ion-section-title">DOMAIN</div>
              <Path label="domain" value={text(domainEvidence.domain_id)} />
              <Path label="source" value={text(domainEvidence.source_registry)} />
              <Path label="posture" value={text(domainEvidence.fact_posture)} />
              <Path label="maturity" value={text(domainEvidence.maturity_estimate)} />
              <List label="paths" values={recordsToStrings(domainEvidence.paths).slice(0, 8)} />
            </section>
            <section><ProbeList title="CONTEXT REFS" probes={contextPaths} /></section>
            <section><List label="read zones" values={recordsToStrings(contextSystem.read_zones || agent.default_read_zones)} /></section>
            <section><List label="proof obligations" values={recordsToStrings(contextSystem.proof_obligations || agent.default_proof_obligations)} /></section>
            <section><List label="templates" values={recordsToStrings(contextSystem.primary_templates || agent.primary_templates)} /></section>
          </div>
        )}
        {tab === 'codex' && (
          <div className="ion-agent-detail-grid">
            <section>
              <div className="ion-section-title">CODEX CLI</div>
              <Path label="cwd" value={text(nativeCodex.launch_cwd || mount.mount_abspath)} />
              <Path label="prompt probe" value={text(nativeCodex.prompt_visibility_probe)} />
              <List label="interactive" values={recordsToStrings(nativeCodex.interactive_command_preview)} />
              <List label="exec" values={recordsToStrings(nativeCodex.command_preview)} />
            </section>
            <section><ProbeList title="MOUNT FILES" probes={mountFiles} /></section>
            <section><ProbeList title="CAPSULE FILES" probes={capsuleFiles} /></section>
            <section className="is-wide">
              <div className="ion-section-title">AGENTS.MD / CONFIG PROOF</div>
              <ExcerptBlock value={[text(rowByLabel(mountFiles, 'agents_md').excerpt), text(rowByLabel(mountFiles, 'codex_config').excerpt)].filter(Boolean).join('\n\n---\n\n')} />
            </section>
          </div>
        )}
        {tab === 'hooks' && (
          <div className="ion-agent-detail-grid">
            <section>
              <div className="ion-section-title">HOOK POSTURE</div>
              <Path label="strategy" value={text(codexMount.hook_strategy || mount.hook_strategy)} />
              <Metric label="shared ION hooks" value={truth(nativeCodex.uses_shared_ion_hooks) ? 'yes' : 'no'} />
              <Metric label="project config" value={truth(nativeCodex.uses_project_codex_config) ? 'yes' : 'no'} />
              <Metric label="folder capsule" value={truth(nativeCodex.uses_portable_ion_context_capsule) ? 'yes' : 'no'} />
            </section>
            <section className="is-wide">
              <div className="ion-section-title">CONFIG EXCERPT</div>
              <Path label="config" value={text(rowByLabel(mountFiles, 'codex_config').relpath || mount.config_path)} />
              <ExcerptBlock value={text(rowByLabel(mountFiles, 'codex_config').excerpt)} />
            </section>
          </div>
        )}
        {tab === 'skills' && (
          <div className="ion-agent-detail-grid">
            <section><List label="templates" values={recordsToStrings(contextSystem.primary_templates || agent.primary_templates)} /></section>
            <section><List label="proof obligations" values={recordsToStrings(contextSystem.proof_obligations || agent.default_proof_obligations)} /></section>
            <section><List label="read first" values={recordsToStrings(capsule.read_first)} /></section>
            <section className="is-wide">
              <div className="ion-section-title">AGENT DESCRIPTOR</div>
              <ExcerptBlock value={text(rowByLabel(capsuleFiles, 'agent').excerpt || rowByLabel(mountFiles, 'agent_system_card').excerpt)} />
            </section>
          </div>
        )}
        {tab === 'tools' && <AgentRecordsPanel title="TOOLS / MCP" records={[record(model.settings), record(model.source_model), nativeCodex]} />}
        {tab === 'runs' && <AgentRecordsPanel title="RUNS" records={runs} />}
        {tab === 'files' && (
          <div className="ion-agent-detail-grid">
            <section><ProbeList title="CONTEXT FILES" probes={contextPaths} /></section>
            <section><ProbeList title="MOUNT FILES" probes={mountFiles} /></section>
            <section><ProbeList title="CAPSULE FILES" probes={capsuleFiles} /></section>
            <section><ProbeList title="PACKAGE FILES" probes={packagePathProbes} /></section>
            <section className="is-wide"><AgentRecordsPanel title="RUN FILES / DIFF WITNESSES" records={runs.map((run) => ({ request: run.codex_work_request_path, return: run.latest_return_packet_path, receipt_paths: run.receipt_paths }))} /></section>
          </div>
        )}
        {tab === 'receipts' && <AgentRecordsPanel title="RECEIPTS" records={receipts.length ? receipts : runs.map((run) => ({ receipt_paths: run.receipt_paths, return: run.latest_return_packet_path }))} />}
        {tab === 'diag' && <JsonView title="DIAGNOSTICS" value={{ evidence, diagnostics, agent, mount, global: model.diagnostics }} />}
        {tab === 'settings' && <JsonView title="SETTINGS" value={{ authority, agent, mount, settings: model.settings, model_authority: model.authority }} />}
      </main>
    </section>
  );
}

function EvidenceCheckList({ checks }: { checks: Array<Record<string, unknown>> }) {
  return (
    <div className="ion-agent-evidence-checks">
      {checks.map((check, index) => (
        <div className={truth(check.ok) ? 'is-ok' : 'is-missing'} key={`${text(check.label, 'check')}-${index}`}>
          <b>{truth(check.ok) ? 'OK' : 'MISS'}</b>
          <span>{text(check.label)}</span>
          <code>{text(check.path)}</code>
        </div>
      ))}
      {checks.length === 0 ? <div className="ion-empty-state">NO PROOF CHECKS</div> : null}
    </div>
  );
}

function ProbeList({ title, probes }: { title: string; probes: Array<Record<string, unknown>> }) {
  return (
    <div className="ion-agent-probe-list">
      <div className="ion-section-title">{title}</div>
      {probes.map((probe, index) => (
        <article className={truth(probe.exists) ? 'is-present' : 'is-missing'} key={`${text(probe.label || probe.path, 'probe')}-${index}`}>
          <header>
            <b>{text(probe.label || probe.kind || `probe ${index + 1}`)}</b>
            <span>{truth(probe.exists) ? text(probe.kind, 'present') : 'missing'}</span>
          </header>
          <code>{text(probe.relpath || probe.path)}</code>
          {probe.bytes !== undefined ? <small>{text(probe.bytes)} bytes</small> : null}
          {recordsToStrings(probe.sample_files).slice(0, 5).map((item) => <small key={item}>{item}</small>)}
        </article>
      ))}
      {probes.length === 0 ? <div className="ion-empty-state">NO PATH PROBES</div> : null}
    </div>
  );
}

function ExcerptBlock({ value }: { value: string }) {
  return value ? <pre className="ion-agent-evidence-excerpt">{value}</pre> : <div className="ion-empty-state">NO EXCERPT</div>;
}

function AgentRecordsPanel({ title, records, fallback = [] }: { title: string; records: Array<Record<string, unknown>>; fallback?: string[] }) {
  return (
    <section className="ion-agent-records-panel">
      <div className="ion-section-title">{title}</div>
      <div className="ion-agent-record-stack">
        {records.map((item, index) => (
          <article className="ion-agent-record-card" key={`${title}-${index}`}>
            <b>{text(item.status || item.event || item.kind || item.role_id || item.agent_display_name || item.hook_strategy || item.path || `record ${index + 1}`)}</b>
            <p>{text(item.question || item.summary || item.result || item.finding || item.path || item.codex_work_request_path || item.latest_return_packet_path)}</p>
            <code>{text(item.path || item.codex_work_request_path || item.latest_return_packet_path || item.active_context_package_md_path || item.manifest_path)}</code>
          </article>
        ))}
        {records.length === 0 && fallback.map((item) => <code className="ion-agent-record-line" key={item}>{item}</code>)}
        {records.length === 0 && fallback.length === 0 ? <div className="ion-empty-state">NO RECORDS</div> : null}
      </div>
    </section>
  );
}

function TeamCommsView({
  agents,
  busy,
  model,
  runtime,
  onRuntimeRefresh,
  setBusy,
  setRequestState,
  taskReturnAutomationDiagnoses,
  taskReturnMachineReceipts,
}: {
  agents: Array<Record<string, unknown>>;
  busy: boolean;
  model: IonAgentControlPlane;
  runtime: IonCockpitViewModel;
  onRuntimeRefresh?: () => void;
  setBusy: (busy: boolean) => void;
  setRequestState: (state: Record<string, unknown> | null) => void;
  taskReturnAutomationDiagnoses: Array<Record<string, unknown>>;
  taskReturnMachineReceipts: Array<Record<string, unknown>>;
}) {
  const communications = record(model.communications);
  const communicationDirectory = record(record(model.roster).communication_directory);
  const contactContract = (() => {
    const full = record(communicationDirectory.contact_contract);
    return Object.keys(full).length ? full : record(communications.contact_contract);
  })();
  const roomContract = (() => {
    const full = record(communicationDirectory.room_contract);
    return Object.keys(full).length ? full : record(communications.room_contract);
  })();
  const contactTemplateContracts = record(contactContract.template_contracts);
  const dispatcher = record(model.dispatcher);
  const dispatcherSummary = record(dispatcher.summary);
  const dispatcherNextAction = record(dispatcher.next_action);
  const dispatcherQueue = records(dispatcher.queue);
  const dispatcherRunner = record(dispatcher.runner);
  const relays = records(communications.relays);
  const pendingRelays = records(communications.pending_relays);
  const timeline = records(communications.timeline);
  const teamComms = record(communications.team_comms);
  const jocComms = record(runtime.joc_comms);
  const chainAudit = record(communications.team_comms_chain_audit);
  const chainAuditGate = record(communications.team_comms_chain_gate);
  const channels = records(teamComms.channels);
  const threads = records(teamComms.threads);
  const messages = records(teamComms.recent_messages);
  const projectionChannels = records(jocComms.channels);
  const projectionThreads = records(jocComms.threads);
  const projectionMessages = records(jocComms.messages);
  const projectionReadOnly = truth(jocComms.read_only_projection) || !truth(record(jocComms.authority).write_authority);
  const usingJocProjection = projectionChannels.length > 0 || projectionThreads.length > 0 || projectionMessages.length > 0;
  const readOnlyJocComms = usingJocProjection && projectionReadOnly;
  const commsRuns = record(teamComms.runs);
  const roomProjection = record(teamComms.rooms);
  const unreadByRole = record(teamComms.unread_by_role);
  const [channelId, setChannelId] = useState('');
  const [threadId, setThreadId] = useState('');
  const [target, setTarget] = useState(MENTION_TARGET);
  const [kind, setKind] = useState('operator_intent');
  const [subject, setSubject] = useState('Team coordination');
  const [message, setMessage] = useState('');
  const [replyToMessageId, setReplyToMessageId] = useState('');
  const [runDispatchMode, setRunDispatchMode] = useState('queue_workpack');
  const [runDirectiveLimit, setRunDirectiveLimit] = useState(3);
  const [runPromptLimit, setRunPromptLimit] = useState(6);
  const [selectedMessageId, setSelectedMessageId] = useState('');
  const [dispatcherDetailsExpanded, setDispatcherDetailsExpanded] = useState(false);
  const [rightPanel, setRightPanel] = useState<AgentCommsInspectorMode>('profile');
  const displayChannels = usingJocProjection ? projectionChannels : channels;
  const displayThreads = usingJocProjection ? projectionThreads : threads;
  const displayMessages = usingJocProjection ? projectionMessages : messages;
  const displayRelays = relays;
  const displayPendingRelays = pendingRelays;
  const displayTimeline = timeline;
  const displayUnreadByRole = unreadByRole;
  const compactHomeViews = mergeAgentHomeViews(records(teamComms.agent_home_views), records(jocComms.agent_home_views));
  const displaySummary = usingJocProjection
    ? {
      channel_count: displayChannels.length,
      thread_count: displayThreads.length,
      message_count: displayMessages.length,
    }
    : record(teamComms.summary);
  const displayRuns = records(commsRuns.runs);
  const chainAuditMetrics = record(chainAudit.metrics);
  const chainAuditFindings = recordsToStrings(chainAudit.findings);
  const chainAuditOk = truth(chainAudit.ok);
  const activeRun = displayRuns.find(runHasActiveWorker) ?? displayRuns.find(runIsActionable) ?? displayRuns[0] ?? {};
  const activeRunAuditGate = record(activeRun.audit_gate);
  const displayAuditGate = Object.keys(activeRunAuditGate).length ? activeRunAuditGate : chainAuditGate;
  const auditGateClean = truth(displayAuditGate.clean);
  const auditGateReasons = recordsToStrings(displayAuditGate.stale_reasons);
  const latestMessage = [...displayMessages].sort((left, right) => text(left.created_at).localeCompare(text(right.created_at))).at(-1) ?? {};
  const defaultChannelId = text(latestMessage.channel_id) || text(displayChannels.find((channel) => Number(channel.message_count) > 0)?.channel_id) || text(displayChannels[0]?.channel_id, 'team');
  const activeChannelId = channelId || defaultChannelId;
  const visibleThreads = displayThreads
    .filter((thread) => text(thread.channel_id) === activeChannelId)
    .sort((left, right) => text(right.updated_at || right.created_at).localeCompare(text(left.updated_at || left.created_at)));
  const activeThreadId = threadId && visibleThreads.some((thread) => text(thread.thread_id) === threadId)
    ? threadId
    : text(visibleThreads.find((thread) => text(thread.thread_id) === text(latestMessage.thread_id))?.thread_id || visibleThreads[0]?.thread_id);
  const selectedChannel = displayChannels.find((channel) => text(channel.channel_id) === activeChannelId) ?? displayChannels[0] ?? {};
  const selectedThread = visibleThreads.find((thread) => text(thread.thread_id) === activeThreadId) ?? visibleThreads[0] ?? {};
  const threadMessages = displayMessages
    .filter((item) => text(item.thread_id) === activeThreadId || (!activeThreadId && text(item.channel_id) === activeChannelId))
    .sort((left, right) => text(left.created_at).localeCompare(text(right.created_at)));
  const selectedMessage = threadMessages.find((item) => text(item.message_id) === selectedMessageId) ?? threadMessages[threadMessages.length - 1] ?? {};
  const selectedMessageRole = text(selectedMessage.from_role || record(selectedMessage.work_panel).from_role || selectedThread.owner_role);
  const activeHomeView = selectAgentHomeView(compactHomeViews, selectedMessageRole) || compactHomeViews[0] || {};
  const replyToMessage = threadMessages.find((item) => text(item.message_id) === replyToMessageId) ?? displayMessages.find((item) => text(item.message_id) === replyToMessageId) ?? {};
  const mentionAgents = agents.filter((agent) => text(agent.role_id || agent.agent_id)).slice(0, 12);
  const channelUnread = displayMessages.reduce<Record<string, number>>((counts, item) => {
    const key = text(item.channel_id, 'team');
    counts[key] = (counts[key] ?? 0) + (text(item.status) === 'read' || text(item.status) === 'acknowledged' ? 0 : 1);
    return counts;
  }, {});
  const routeTargets = target === MENTION_TARGET ? [] : [target].filter(Boolean);
  const dispatcherPaused = truth(dispatcher.paused);
  const readOnlyFinding = 'joc_comms_read_only_projection';
  const guardReadOnlyProjection = () => {
    if (!readOnlyJocComms) return false;
    setRequestState({
      ok: false,
      finding: readOnlyFinding,
      detail: 'Team Comms is projection-driven and read-only in this slice. Live send/ack/invoke/queue actions remain gated.',
    });
    return true;
  };

  const appendMention = (agent: Record<string, unknown>) => {
    const alias = mentionAliasForAgent(agent);
    if (!alias) return;
    setTarget(MENTION_TARGET);
    setMessage((current) => {
      const nextPrefix = current && !/\s$/.test(current) ? `${current} ` : current;
      return `${nextPrefix}@${alias} `;
    });
  };

  const replyTo = (replyMessage: Record<string, unknown>) => {
    const nextMessageId = text(replyMessage.message_id);
    if (!nextMessageId) return;
    setReplyToMessageId(nextMessageId);
    setSelectedMessageId(nextMessageId);
    setThreadId(text(replyMessage.thread_id, activeThreadId));
    setTarget(MENTION_TARGET);
    const alias = mentionAliasFromRole(text(replyMessage.from_role || record(replyMessage.work_panel).from_role));
    if (alias) {
      setMessage((current) => current.trim() ? current : `@${alias} `);
    }
  };

  const sendMessage = async () => {
    if (guardReadOnlyProjection()) return;
    if (!message.trim() || busy) {
      setRequestState({ ok: false, finding: 'message_required' });
      return;
    }
    setBusy(true);
    try {
      const response = await fetch('/cockpit/agents/comms/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({
          channel_id: activeChannelId,
          thread_id: activeThreadId || undefined,
          from_role: 'operator',
          to_roles: routeTargets,
          message_kind: kind,
          subject,
          body: message,
          parent_message_id: replyToMessageId || undefined,
          requires_response: true,
          source_refs: [text(selectedThread.path)].filter(Boolean),
        }),
      });
      const result = (await response.json()) as Record<string, unknown>;
      setRequestState(result);
      if (truth(result.ok)) {
        setMessage('');
        setReplyToMessageId('');
      }
      await onRuntimeRefresh?.();
    } catch (error) {
      setRequestState({ ok: false, finding: error instanceof Error ? error.message : 'team_comms_relay_failed' });
    } finally {
      setBusy(false);
    }
  };

  const openBranch = async (sourceMessageId: string) => {
    if (guardReadOnlyProjection()) return;
    if (!sourceMessageId || busy) return;
    setBusy(true);
    try {
      const response = await fetch('/cockpit/agents/comms/branch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({
          source_message_id: sourceMessageId,
          from_role: 'operator',
          to_roles: routeTargets,
          parent_message_id: replyToMessageId || undefined,
          channel_id: activeChannelId,
          subject: `Branch: ${text(selectedThread.subject, 'agent comms')}`,
        }),
      });
      const result = (await response.json()) as Record<string, unknown>;
      setRequestState(result);
      if (truth(result.ok)) {
        setChannelId(text(result.channel_id, activeChannelId));
        setThreadId(text(result.new_thread_id || result.branch_thread_id));
      }
      await onRuntimeRefresh?.();
    } catch (error) {
      setRequestState({ ok: false, finding: error instanceof Error ? error.message : 'agent_comms_branch_failed' });
    } finally {
      setBusy(false);
    }
  };

  const openDisplayedBranch = (sourceMessageId: string) => void openBranch(sourceMessageId);

  const openInScope = () => {
    const nextThreadId = text(selectedThread.thread_id);
    if (!nextThreadId || typeof window === 'undefined') {
      return;
    }
    window.location.hash = `scope?thread_id=${encodeURIComponent(nextThreadId)}`;
  };

  const startCommsRun = async () => {
    if (guardReadOnlyProjection()) return;
    const objective = subject.trim() || `Run for #${text(selectedChannel.label || selectedChannel.channel_id, 'team')}`;
    const body = message.trim() || objective;
    if (!body || busy) {
      setRequestState({ ok: false, finding: 'run_body_required' });
      return;
    }
    setBusy(true);
    try {
      const response = await fetch('/cockpit/agents/comms/run/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({
          objective,
          body,
          from_role: 'operator',
          target_roles: routeTargets,
          dispatch_mode: runDispatchMode,
          channel_id: activeChannelId,
          thread_id: activeThreadId || undefined,
          max_directives: runDirectiveLimit,
          max_agents: Math.max(2, Math.min(runDirectiveLimit + 1, 12)),
          max_workpacks: Math.max(2, Math.min(runDirectiveLimit + 1, 25)),
          automation_prompt_limit: runPromptLimit,
          automation_window_minutes: 60,
          automation_time_budget_minutes: 120,
          source_refs: [text(selectedThread.path)].filter(Boolean),
        }),
      });
      const result = (await response.json()) as Record<string, unknown>;
      setRequestState(result);
      if (truth(result.ok)) {
        setMessage('');
        setReplyToMessageId('');
        setThreadId(first(recordsToStrings(result.thread_ids)) || activeThreadId);
      }
      await onRuntimeRefresh?.();
    } catch (error) {
      setRequestState({ ok: false, finding: error instanceof Error ? error.message : 'agent_comms_run_start_failed' });
    } finally {
      setBusy(false);
    }
  };

  const pickupRunDirectives = async (runId: string) => {
    if (guardReadOnlyProjection()) return;
    if (!runId || busy) return;
    setBusy(true);
    try {
      const response = await fetch('/cockpit/agents/comms/run/pickup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({ run_id: runId, max_directives: runDirectiveLimit }),
      });
      const result = (await response.json()) as Record<string, unknown>;
      setRequestState(result);
      await onRuntimeRefresh?.();
    } catch (error) {
      setRequestState({ ok: false, finding: error instanceof Error ? error.message : 'agent_comms_run_pickup_failed' });
    } finally {
      setBusy(false);
    }
  };

  const continueRun = async (runId: string) => {
    if (guardReadOnlyProjection()) return;
    if (!runId || busy) return;
    setBusy(true);
    try {
      const response = await fetch('/cockpit/agents/comms/run/continue', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({
          run_id: runId,
          max_directives: runDirectiveLimit,
          max_worker_starts: 1,
          start_workers: true,
          timeout_seconds: 1800,
        }),
      });
      const result = (await response.json()) as Record<string, unknown>;
      setRequestState(result);
      await onRuntimeRefresh?.();
    } catch (error) {
      setRequestState({ ok: false, finding: error instanceof Error ? error.message : 'agent_comms_run_continue_failed' });
    } finally {
      setBusy(false);
    }
  };

  const auditRun = async (runId: string) => {
    if (guardReadOnlyProjection()) return;
    if (!runId || busy) return;
    setBusy(true);
    try {
      const response = await fetch('/cockpit/agents/comms/run/audit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({ run_id: runId, strict_pristine: true, write_receipt: true }),
      });
      const result = (await response.json()) as Record<string, unknown>;
      setRequestState(result);
      await onRuntimeRefresh?.();
    } catch (error) {
      setRequestState({ ok: false, finding: error instanceof Error ? error.message : 'agent_comms_run_audit_failed' });
    } finally {
      setBusy(false);
    }
  };

  const startRunWorker = async (run: Record<string, unknown>) => {
    if (guardReadOnlyProjection()) return;
    const runId = text(run.run_id);
    const workpackPath = runWorkpackPath(run);
    if (!runId || !workpackPath || busy) {
      setRequestState({ ok: false, finding: 'run_workpack_required' });
      return;
    }
    setBusy(true);
    try {
      const response = await fetch('/cockpit/agents/comms/run/start-worker', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({ run_id: runId, workpack_path: workpackPath, timeout_seconds: 1800 }),
      });
      const result = (await response.json()) as Record<string, unknown>;
      setRequestState(result);
      await onRuntimeRefresh?.();
    } catch (error) {
      setRequestState({ ok: false, finding: error instanceof Error ? error.message : 'agent_comms_worker_start_failed' });
    } finally {
      setBusy(false);
    }
  };

  const routeDispatcher = async () => {
    if (guardReadOnlyProjection()) return;
    const objective = subject.trim() || `Dispatch for #${text(selectedChannel.label || selectedChannel.channel_id, 'team')}`;
    const body = message.trim() || objective;
    if (!body || busy) {
      setRequestState({ ok: false, finding: 'dispatcher_body_required' });
      return;
    }
    setBusy(true);
    try {
      const response = await fetch('/cockpit/agents/dispatcher/route', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({
          objective,
          body,
          from_role: 'operator',
          target_roles: routeTargets,
          dispatch_mode: runDispatchMode,
          channel_id: activeChannelId,
          thread_id: activeThreadId || undefined,
          max_directives: runDirectiveLimit,
          max_agents: Math.max(2, Math.min(runDirectiveLimit + 1, 12)),
          max_workpacks: Math.max(2, Math.min(runDirectiveLimit + 1, 25)),
          automation_prompt_limit: runPromptLimit,
          automation_window_minutes: 60,
          automation_time_budget_minutes: 120,
          source_refs: [text(selectedThread.path)].filter(Boolean),
        }),
      });
      const result = (await response.json()) as Record<string, unknown>;
      setRequestState(result);
      if (truth(result.ok)) {
        setMessage('');
        setReplyToMessageId('');
        setThreadId(first(recordsToStrings(result.thread_ids)) || activeThreadId);
      }
      await onRuntimeRefresh?.();
    } catch (error) {
      setRequestState({ ok: false, finding: error instanceof Error ? error.message : 'steward_dispatch_route_failed' });
    } finally {
      setBusy(false);
    }
  };

  const tickDispatcher = async (runId: string) => {
    if (guardReadOnlyProjection()) return;
    if (!runId || busy) return;
    setBusy(true);
    try {
      const response = await fetch('/cockpit/agents/dispatcher/tick', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({
          run_id: runId,
          max_directives: runDirectiveLimit,
          max_worker_starts: 1,
          start_workers: true,
          timeout_seconds: 1800,
        }),
      });
      const result = (await response.json()) as Record<string, unknown>;
      setRequestState(result);
      await onRuntimeRefresh?.();
    } catch (error) {
      setRequestState({ ok: false, finding: error instanceof Error ? error.message : 'steward_dispatch_tick_failed' });
    } finally {
      setBusy(false);
    }
  };

  const runDispatcherRunner = async () => {
    if (guardReadOnlyProjection()) return;
    if (busy || dispatcherPaused) return;
    setBusy(true);
    try {
      const response = await fetch('/cockpit/agents/dispatcher/runner', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({
          run_id: text(dispatcherNextAction.run_id || activeRun.run_id) || undefined,
          max_ticks: 3,
          max_directives_per_tick: runDirectiveLimit,
          max_worker_starts_per_tick: 1,
          max_worker_starts: 1,
          max_runtime_seconds: 30,
          start_workers: true,
          timeout_seconds: 1800,
        }),
      });
      const result = (await response.json()) as Record<string, unknown>;
      setRequestState(result);
      await onRuntimeRefresh?.();
    } catch (error) {
      setRequestState({ ok: false, finding: error instanceof Error ? error.message : 'steward_dispatch_runner_failed' });
    } finally {
      setBusy(false);
    }
  };

  const pauseDispatcher = async () => {
    if (guardReadOnlyProjection()) return;
    if (busy) return;
    setBusy(true);
    try {
      const response = await fetch('/cockpit/agents/dispatcher/pause', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({
          paused: !dispatcherPaused,
          reason: dispatcherPaused ? 'operator_resumed_from_cockpit' : 'operator_paused_from_cockpit',
        }),
      });
      const result = (await response.json()) as Record<string, unknown>;
      setRequestState(result);
      await onRuntimeRefresh?.();
    } catch (error) {
      setRequestState({ ok: false, finding: error instanceof Error ? error.message : 'steward_dispatch_pause_failed' });
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="ion-agent-team-comms-view ion-agent-discord-comms">
      <aside className="ion-agent-discord-server-rail" aria-label="Agent comms channels">
        <div className="ion-agent-discord-server-mark">ION</div>
        <div className="ion-agent-discord-server-stack">
          {displayChannels.map((channel) => (
            <button
              className={text(channel.channel_id) === activeChannelId ? 'is-active' : undefined}
              key={text(channel.channel_id)}
              onClick={() => {
                setChannelId(text(channel.channel_id));
                setThreadId('');
                setSelectedMessageId('');
                setReplyToMessageId('');
              }}
              title={`#${text(channel.label || channel.channel_id)} / ${text(channel.purpose)}`}
              type="button"
            >
              <span>{text(channel.label || channel.channel_id).slice(0, 2)}</span>
              {channelUnread[text(channel.channel_id)] ? <b>{channelUnread[text(channel.channel_id)]}</b> : null}
            </button>
          ))}
        </div>
      </aside>
      <aside className="ion-agent-discord-channel-rail" aria-label="Team comms threads">
        <header>
          <div>
            <span>TEAM COMMS</span>
            <b>DURABLE AGENT BUS</b>
          </div>
        </header>
        <div className="ion-agent-discord-channel-list">
          {displayChannels.map((channel) => (
            <AgentCommsChannelButton
              active={text(channel.channel_id) === activeChannelId}
              channel={channel}
              key={text(channel.channel_id)}
              onClick={() => {
                setChannelId(text(channel.channel_id));
                setThreadId('');
                setSelectedMessageId('');
                setReplyToMessageId('');
              }}
              unread={channelUnread[text(channel.channel_id)] ?? 0}
            />
          ))}
          {displayChannels.length === 0 ? <div className="ion-empty-state">NO CHANNEL PROJECTION</div> : null}
        </div>
        <div className="ion-agent-discord-thread-head">
          <span>THREADS</span>
          <b>{visibleThreads.length}</b>
        </div>
        <div className="ion-agent-discord-thread-list">
          {visibleThreads.map((thread) => (
            <button
              className={text(thread.thread_id) === activeThreadId ? 'is-active' : undefined}
              key={text(thread.thread_id)}
              onClick={() => {
                setThreadId(text(thread.thread_id));
                setSelectedMessageId('');
                setReplyToMessageId('');
              }}
              type="button"
            >
              <b>{text(thread.subject, 'thread')}</b>
              <span>{text(thread.message_count, '0')} messages / {text(thread.status, 'active')}</span>
              <small>{text(thread.latest_summary)}</small>
            </button>
          ))}
          {visibleThreads.length === 0 ? <div className="ion-empty-state">NO THREADS IN CHANNEL</div> : null}
        </div>
      </aside>
      <main className="ion-agent-discord-room">
        <header className="ion-agent-discord-room-header">
          <div>
            <span>#{text(selectedChannel.label || selectedChannel.channel_id, 'team')}</span>
            <b>{text(selectedThread.subject, 'Agent Communication Center')}</b>
            {readOnlyJocComms ? <small>READ-ONLY JOC PROJECTION MODE (live send/ack/invoke/queue disabled)</small> : null}
          </div>
          <div className="ion-agent-discord-room-actions">
            <AgentCommsPill label="messages" value={threadMessages.length} />
            <AgentCommsPill label="relays" value={displayRelays.length} />
            <AgentCommsPill label="pending" value={displayPendingRelays.length} />
            <AgentCommsPill label="runs" value={`${text(commsRuns.active_run_count, '0')}/${text(commsRuns.run_count, '0')}`} />
            <AgentCommsPill label="dispatch" value={text(dispatcher.dispatcher_state, 'idle')} />
            <AgentCommsPill label="automation" value={taskReturnAutomationDiagnoses.length} />
            <AgentCommsPill label="receipts" value={taskReturnMachineReceipts.length} />
            <AgentCommsPill label="audit" value={text(displayAuditGate.state, text(chainAudit.audit_state, 'none'))} />
            <AgentCommsPill label="contacts" value={text(contactContract.contact_edge_count, '0')} />
            <AgentCommsPill label="templates" value={text(contactContract.template_contract_count, String(Object.keys(contactTemplateContracts).length))} />
            <AgentCommsPill label="rooms" value={text(roomProjection.room_count, text(roomContract.room_count, '0'))} />
            {readOnlyJocComms ? <AgentCommsPill label="mode" value="read-only" /> : null}
            <button className="ion-open-scope" disabled={!text(selectedThread.thread_id)} onClick={openInScope} type="button">OPEN IN SCOPE</button>
            <button className={rightPanel === 'profile' ? 'is-active' : undefined} onClick={() => setRightPanel('profile')} type="button">DETAIL</button>
            <button className={rightPanel === 'timeline' ? 'is-active' : undefined} onClick={() => setRightPanel('timeline')} type="button">TRACE</button>
            <button className={rightPanel === 'relays' ? 'is-active' : undefined} onClick={() => setRightPanel('relays')} type="button">RELAYS</button>
            <button className={rightPanel === 'contacts' ? 'is-active' : undefined} onClick={() => setRightPanel('contacts')} type="button">CONTACTS</button>
            <button className={rightPanel === 'rooms' ? 'is-active' : undefined} onClick={() => setRightPanel('rooms')} type="button">ROOMS</button>
          </div>
        </header>

        <div className="ion-agent-discord-message-scroll">
          {threadMessages.map((item) => (
            <AgentCommsChatMessage
              active={text(item.message_id) === text(selectedMessage.message_id)}
              key={text(item.message_id)}
              message={item}
              onBranch={openDisplayedBranch}
              onOpenThread={(nextThreadId) => {
                setThreadId(nextThreadId);
                setSelectedMessageId('');
                setReplyToMessageId('');
              }}
              onReply={replyTo}
              onSelect={() => {
                setSelectedMessageId(text(item.message_id));
                setRightPanel('profile');
              }}
            />
          ))}
          {threadMessages.length === 0 ? (
            <div className="ion-agent-comms-empty">
              <b>No messages in this thread</b>
              <span>Pick a channel/thread or send the first agent packet below.</span>
            </div>
          ) : null}
        </div>

        <form className="ion-agent-discord-composer" onSubmit={(event) => { event.preventDefault(); void sendMessage(); }}>
          <div className="ion-agent-discord-compose-meta">
            <select aria-label="Agent comms channel" value={activeChannelId} onChange={(event) => {
              setChannelId(event.target.value);
              setThreadId('');
              setSelectedMessageId('');
              setReplyToMessageId('');
            }} disabled={readOnlyJocComms}>
              {displayChannels.map((channel) => (
                <option key={text(channel.channel_id)} value={text(channel.channel_id)}>
                  #{text(channel.label || channel.channel_id)}
                </option>
              ))}
            </select>
            <select aria-label="Agent comms target" value={target} onChange={(event) => setTarget(event.target.value)} disabled={readOnlyJocComms}>
              <option value={MENTION_TARGET}>@MENTIONS</option>
              <option value="operator">OPERATOR</option>
              {agents.map((agent) => (
                <option key={text(agent.role_id || agent.agent_id)} value={text(agent.role_id || agent.agent_id)}>
                  {text(agent.display_name || agent.role_id)}
                </option>
              ))}
            </select>
            <select aria-label="Agent comms packet kind" value={kind} onChange={(event) => setKind(event.target.value)} disabled={readOnlyJocComms}>
              <option value="operator_intent">OPERATOR INTENT</option>
              <option value="relay_packet">RELAY PACKET</option>
              <option value="task_dispatch">TASK DISPATCH</option>
              <option value="handoff">HANDOFF</option>
              <option value="question">QUESTION</option>
              <option value="answer">ANSWER</option>
              <option value="signal">SIGNAL</option>
              <option value="audit">AUDIT</option>
              <option value="blocker">BLOCKER</option>
              <option value="decision_request">DECISION REQUEST</option>
            </select>
            <input aria-label="Agent comms subject" value={subject} onChange={(event) => setSubject(event.target.value)} disabled={readOnlyJocComms} />
          </div>
          <div className="ion-agent-discord-mention-row" aria-label="Mention available agents">
            {mentionAgents.map((agent) => {
              const alias = mentionAliasForAgent(agent);
              return (
                <button key={text(agent.role_id || agent.agent_id)} onClick={() => appendMention(agent)} title={text(agent.role_id || agent.agent_id)} type="button" disabled={readOnlyJocComms}>
                  @{alias}
                </button>
              );
            })}
          </div>
          {replyToMessageId ? (
            <div className="ion-agent-discord-reply-chip">
              <span>REPLY</span>
              <b>{displayRole(text(replyToMessage.from_role, 'agent'))}</b>
              <code>{replyToMessageId}</code>
              <button onClick={() => setReplyToMessageId('')} type="button" disabled={readOnlyJocComms}>CLEAR</button>
            </div>
          ) : null}
          <div className="ion-agent-discord-run-strip">
            <div className={`ion-agent-dispatcher-board is-${slug(text(dispatcher.dispatcher_state, 'idle'))} ${dispatcherDetailsExpanded ? 'is-details-expanded' : 'is-details-collapsed'}`}>
              <header className="ion-agent-dispatcher-summary">
                <div>
                  <span>STEWARD DISPATCHER</span>
                  <b>{text(dispatcher.dispatcher_state, 'idle')}</b>
                  <code>{dispatcherPaused ? `paused / ${text(dispatcher.pause_reason, 'manual')}` : `next / ${text(dispatcherNextAction.next_action, 'observe')}`}</code>
                </div>
                <div className="ion-agent-dispatcher-metrics">
                  <code>{text(dispatcherSummary.actionable_run_count, '0')} actionable</code>
                  <code>{text(dispatcherSummary.active_worker_count, '0')} workers</code>
                  <code>{text(dispatcherSummary.pending_directive_count, '0')} directives</code>
                  <code>{text(dispatcherSummary.domain_gap_count, '0')} gaps</code>
                  <code>{text(dispatcherRunner.latest_finding, 'runner idle')}</code>
                </div>
                <button
                  className="ion-agent-dispatcher-toggle"
                  onClick={() => setDispatcherDetailsExpanded((current) => !current)}
                  type="button"
                >
                  {dispatcherDetailsExpanded ? 'COLLAPSE' : 'DETAILS'}
                </button>
              </header>
              <div className={`ion-agent-dispatcher-details ${dispatcherDetailsExpanded ? 'is-open' : 'is-closed'}`}>
                <div className="ion-agent-dispatcher-next">
                  <b>{text(dispatcherNextAction.objective, text(activeRun.objective, 'No routed run'))}</b>
                  <span>{text(dispatcherNextAction.run_id || activeRun.run_id, 'no run')} / {text(dispatcherNextAction.policy_state, 'policy unknown')} / {text(dispatcherNextAction.followup_state, 'decision pending')}</span>
                </div>
                <div className="ion-agent-dispatcher-actions">
                  <button disabled={busy || readOnlyJocComms || dispatcherPaused || !message.trim()} onClick={() => void routeDispatcher()} type="button">DISPATCH</button>
                  <button disabled={busy || readOnlyJocComms || dispatcherPaused || !text(dispatcherNextAction.run_id || activeRun.run_id)} onClick={() => void tickDispatcher(text(dispatcherNextAction.run_id || activeRun.run_id))} type="button">TICK</button>
                  <button disabled={busy || readOnlyJocComms || dispatcherPaused || !text(dispatcherNextAction.run_id || activeRun.run_id)} onClick={() => void runDispatcherRunner()} type="button">RUNNER</button>
                  <button disabled={busy || readOnlyJocComms} onClick={() => void pauseDispatcher()} type="button">{dispatcherPaused ? 'RESUME' : 'PAUSE'}</button>
                </div>
                <div className="ion-agent-dispatcher-runner">
                  <code>{text(dispatcherRunner.latest_tick_count, '0')} ticks</code>
                  <code>{text(record(dispatcherRunner.latest_usage).worker_start_count, '0')} workers</code>
                  <code>{text(record(dispatcherRunner.latest_usage).processed_directive_count, '0')} directives</code>
                  <code>{shortPath(text(dispatcherRunner.latest_receipt_path))}</code>
                </div>
                <div className="ion-agent-dispatcher-queue">
                  {dispatcherQueue.slice(0, 3).map((row) => (
                    <code key={text(row.run_id)}>{text(row.state)} / {text(row.next_action)} / {shortPath(text(row.run_id))}</code>
                  ))}
                  {dispatcherQueue.length === 0 ? <code>no dispatcher queue</code> : null}
                </div>
              </div>
            </div>
            <div>
              <span>TASK RUN</span>
              <b>{text(activeRun.objective, 'NO ACTIVE RUN')}</b>
              <code>{text(activeRun.status, 'idle')} / {runOperationalText(activeRun)} / {runUsageText(activeRun)}</code>
              <div className={`ion-agent-discord-run-proof-inline is-${slug(text(activeRun.operational_state, 'idle'))}`}>
                <code>{runProofLabel(activeRun)}</code>
                <code>{runPolicyText(activeRun)}</code>
                <code>{runFollowupDecisionText(activeRun)}</code>
                <code>{runLatestReturnPath(activeRun) ? 'return linked' : runWorkpackPath(activeRun) ? 'waiting return' : 'no workpack'}</code>
                <code className={truth(record(activeRun.worker_runtime).has_active_worker) ? 'is-worker-running' : undefined}>{runWorkerText(activeRun)}</code>
              </div>
              <div className={`ion-agent-comms-chain-audit is-${slug(text(displayAuditGate.state, text(chainAudit.audit_state, 'unknown')))}`}>
                <code>{auditGateClean ? 'audit clean' : chainAuditOk ? 'audit pass receipt required' : 'audit fail'}</code>
                <code>{auditGateReasons.length ? auditGateReasons.slice(0, 3).join(' / ') : chainAuditFindings.length ? chainAuditFindings.slice(0, 3).join(' / ') : 'machine checks closed'}</code>
                <code>{text(chainAuditMetrics.workpack_count, '0')} workpacks / {text(chainAuditMetrics.accepted_return_count, '0')} accepted</code>
                <code>{shortPath(text(displayAuditGate.latest_audit_path || chainAudit.run_path))}</code>
              </div>
            </div>
            <select aria-label="Comms run dispatch mode" value={runDispatchMode} onChange={(event) => setRunDispatchMode(event.target.value)} disabled={readOnlyJocComms}>
              <option value="comms_only">COMMS ONLY</option>
              <option value="prepare_workpack">PREPARE WORKPACK</option>
              <option value="queue_workpack">QUEUE WORKPACK</option>
            </select>
            <input aria-label="Run directive limit" min={1} max={25} type="number" value={runDirectiveLimit} onChange={(event) => setRunDirectiveLimit(Number(event.target.value || 1))} disabled={readOnlyJocComms} />
            <input aria-label="Run prompt limit" min={1} max={100} type="number" value={runPromptLimit} onChange={(event) => setRunPromptLimit(Number(event.target.value || 1))} disabled={readOnlyJocComms} />
            <button disabled={busy || readOnlyJocComms || !message.trim()} onClick={() => void startCommsRun()} type="button">START RUN</button>
            <button disabled={busy || readOnlyJocComms || !text(activeRun.run_id) || text(activeRun.status) !== 'active'} onClick={() => void pickupRunDirectives(text(activeRun.run_id))} type="button">PICKUP</button>
            <button disabled={busy || readOnlyJocComms || !text(activeRun.run_id) || text(activeRun.status) !== 'active'} onClick={() => void continueRun(text(activeRun.run_id))} type="button">CONTINUE</button>
            <button disabled={busy || readOnlyJocComms || !canStartRunWorker(activeRun)} onClick={() => void startRunWorker(activeRun)} title={runWorkpackPath(activeRun) || 'Run workpack required'} type="button">WORKER</button>
            <button disabled={busy || readOnlyJocComms || !text(activeRun.run_id)} onClick={() => void auditRun(text(activeRun.run_id))} type="button">AUDIT</button>
          </div>
          <div className="ion-agent-discord-compose-box">
            <textarea value={message} onChange={(event) => setMessage(event.target.value)} placeholder={`@ionologist message #${text(selectedChannel.label || selectedChannel.channel_id, 'team')}`} rows={3} disabled={readOnlyJocComms} />
            <button className="is-active" disabled={busy || readOnlyJocComms || !message.trim()} type="submit">{readOnlyJocComms ? 'READ ONLY' : busy ? 'SENDING' : 'SEND'}</button>
          </div>
        </form>
      </main>
      <aside className="ion-agent-discord-inspector" aria-label="Agent comms inspector">
        <AgentCommsInspector
          agents={agents}
          message={selectedMessage}
          mode={rightPanel}
          relays={[...displayPendingRelays, ...displayRelays]}
          runs={displayRuns}
          chainAudit={chainAudit}
          chainAuditGate={displayAuditGate}
          contactContract={contactContract}
          roomContract={roomContract}
          roomProjection={roomProjection}
          summary={displaySummary}
          homeView={activeHomeView}
          taskReturnAutomationDiagnoses={taskReturnAutomationDiagnoses}
          taskReturnMachineReceipts={taskReturnMachineReceipts}
          timeline={displayTimeline}
          unreadByRole={displayUnreadByRole}
        />
      </aside>
    </section>
  );
}

function AgentConversationPanel({
  messages,
  relays,
  timeline,
  title,
}: {
  messages: Array<Record<string, unknown>>;
  relays: Array<Record<string, unknown>>;
  timeline: Array<Record<string, unknown>>;
  title: string;
}) {
  return (
    <section className="ion-agent-conversation-page">
      <header>
        <div>
          <div className="ion-section-title">AGENT CONVERSATION</div>
          <h2>{title}</h2>
          <p>Durable team messages rendered as Codex-style work panels, with routing, context, branch, agent, and raw evidence tabs.</p>
        </div>
        <Metric label="messages" value={messages.length} />
        <Metric label="relays" value={relays.length} />
        <Metric label="events" value={timeline.length} />
      </header>
      <div className="ion-agent-conversation-scroll">
        {messages.map((message) => <AgentCommsWorkPanel key={text(message.message_id)} message={message} />)}
        {messages.length === 0 ? (
          <div className="ion-empty-state">NO DURABLE TEAM COMMS MESSAGES FOR THIS AGENT YET</div>
        ) : null}
      </div>
    </section>
  );
}

function AgentCommsChannelButton({
  active,
  channel,
  onClick,
  unread,
}: {
  active: boolean;
  channel: Record<string, unknown>;
  onClick: () => void;
  unread: number;
}) {
  return (
    <button className={active ? 'is-active' : undefined} onClick={onClick} type="button">
      <span>#{text(channel.label || channel.channel_id)}</span>
      <b>{text(channel.thread_count, '0')} threads</b>
      <small>{text(channel.purpose || channel.kind, 'agent comms')}</small>
      {unread ? <em>{unread}</em> : null}
    </button>
  );
}

function AgentCommsChatMessage({
  active,
  message,
  onBranch,
  onOpenThread,
  onReply,
  onSelect,
}: {
  active: boolean;
  message: Record<string, unknown>;
  onBranch: (messageId: string) => void;
  onOpenThread: (threadId: string) => void;
  onReply: (message: Record<string, unknown>) => void;
  onSelect: () => void;
}) {
  const panel = record(message.work_panel);
  const role = text(message.from_role || panel.from_role, 'agent');
  const kind = text(message.message_kind || panel.message_kind, 'message');
  const body = text(message.body || panel.summary);
  const mentionedRoles = recordsToStrings(message.mentioned_roles);
  return (
    <article className={`ion-agent-discord-message${active ? ' is-active' : ''} is-${slug(kind)}`} onClick={onSelect}>
      <div className="ion-agent-discord-avatar" aria-hidden="true">{roleInitials(role)}</div>
      <div className="ion-agent-discord-message-body">
        <header>
          <div>
            <b>{displayRole(role)}</b>
            <span>{kind}</span>
            <code>{text(message.message_id || panel.message_id)}</code>
          </div>
          <div className="ion-agent-discord-message-actions">
            <time>{text(message.created_at || panel.created_at)}</time>
            <button onClick={(event) => { event.stopPropagation(); onReply(message); }} type="button">REPLY</button>
          </div>
        </header>
        {text(message.parent_message_id) ? (
          <div className="ion-agent-discord-parent-link">
            <span>REPLY</span>
            <code>{text(message.parent_message_id)}</code>
          </div>
        ) : null}
        {body ? <p>{body}</p> : null}
        {mentionedRoles.length ? (
          <div className="ion-agent-discord-message-mentions">
            {mentionedRoles.map((roleId) => <code key={roleId}>@{mentionAliasFromRole(roleId)}</code>)}
          </div>
        ) : null}
        <AgentCommsWorkPanel message={message} onBranch={onBranch} onOpenThread={onOpenThread} />
      </div>
    </article>
  );
}

function AgentCommsInspector({
  agents,
  chainAudit,
  chainAuditGate,
  contactContract,
  homeView,
  message,
  mode,
  relays,
  roomContract,
  roomProjection,
  runs,
  summary,
  taskReturnAutomationDiagnoses,
  taskReturnMachineReceipts,
  timeline,
  unreadByRole,
}: {
  agents: Array<Record<string, unknown>>;
  chainAudit: Record<string, unknown>;
  chainAuditGate: Record<string, unknown>;
  contactContract: Record<string, unknown>;
  homeView: Record<string, unknown>;
  message: Record<string, unknown>;
  mode: AgentCommsInspectorMode;
  relays: Array<Record<string, unknown>>;
  roomContract: Record<string, unknown>;
  roomProjection: Record<string, unknown>;
  runs: Array<Record<string, unknown>>;
  summary: Record<string, unknown>;
  taskReturnAutomationDiagnoses: Array<Record<string, unknown>>;
  taskReturnMachineReceipts: Array<Record<string, unknown>>;
  timeline: Array<Record<string, unknown>>;
  unreadByRole: Record<string, unknown>;
}) {
  const panel = record(message.work_panel);
  const tabs = records(panel.tabs);
  const chainAuditMetrics = record(chainAudit.metrics);
  const chainAuditFindings = recordsToStrings(chainAudit.findings);
  const chainAuditGateReasons = recordsToStrings(chainAuditGate.stale_reasons);
  const participants = recordsToStrings(message.participants).concat(recordsToStrings(message.to_roles)).filter(Boolean);
  const uniqueParticipants = Array.from(new Set(participants));
  const unreadRows = Object.entries(unreadByRole).filter(([, value]) => Number(value) > 0);
  if (mode === 'timeline') {
    return <AgentRecordsPanel title="COMMS TRACE" records={timeline.slice(0, 80)} />;
  }
  if (mode === 'relays') {
    return <AgentRecordsPanel title="RELAYS / PENDING" records={relays.slice(0, 80)} />;
  }
  if (mode === 'contacts') {
    return <AgentContactContractPanel agents={agents} contactContract={contactContract} />;
  }
  if (mode === 'rooms') {
    return <AgentRoomContractPanel roomContract={roomContract} roomProjection={roomProjection} />;
  }
  return (
    <div className="ion-agent-discord-inspector-profile">
      <header>
        <span>MESSAGE INSPECTOR</span>
        <b>{text(message.subject || panel.subject, 'No message selected')}</b>
        <code>{text(message.message_id || panel.message_id, 'select a message')}</code>
      </header>
      <div className="ion-agent-discord-inspector-metrics">
        <Metric label="channels" value={summary.channel_count} />
        <Metric label="threads" value={summary.thread_count} />
        <Metric label="messages" value={summary.message_count} />
      </div>
      <div className="ion-agent-discord-inspector-section">
        <span>participants</span>
        <div className="ion-agent-discord-profile-list">
          {uniqueParticipants.slice(0, 12).map((role) => (
            <div className="ion-agent-discord-profile-chip" key={role}>
              <b>{roleInitials(role)}</b>
              <span>{displayRole(role)}</span>
            </div>
          ))}
          {uniqueParticipants.length === 0 ? <code>none</code> : null}
        </div>
      </div>
      <div className="ion-agent-discord-inspector-section">
        <span>work panel tabs</span>
        <div className="ion-agent-discord-tab-ledger">
          {tabs.map((tab) => (
            <code key={text(tab.tab_id)}>{text(tab.label || tab.tab_id)} {text(tab.count, '0')}</code>
          ))}
          {tabs.length === 0 ? <code>none</code> : null}
        </div>
      </div>
      <div className="ion-agent-discord-inspector-section">
        <span>active roster</span>
        <div className="ion-agent-discord-profile-list">
          {agents.slice(0, 10).map((agent) => (
            <div className="ion-agent-discord-profile-chip" key={text(agent.role_id || agent.agent_id)}>
              <b>{roleInitials(text(agent.role_id || agent.agent_id))}</b>
              <span>{text(agent.display_name || agent.role_id || agent.agent_id)}</span>
            </div>
          ))}
        </div>
      </div>
      <div className="ion-agent-discord-inspector-section">
        <span>chain audit</span>
        <div className="ion-agent-discord-tab-ledger">
          <code>{truth(chainAuditGate.clean) ? 'CLEAN' : text(chainAuditGate.state, truth(chainAudit.ok) ? 'PASS_NEEDS_RECEIPT' : 'FAIL')} / {text(chainAudit.run_id, 'no run')}</code>
          <code>{chainAuditGateReasons.length ? chainAuditGateReasons.slice(0, 4).join(' / ') : chainAuditFindings.length ? chainAuditFindings.slice(0, 4).join(' / ') : 'machine checks closed'}</code>
          <code>{text(chainAuditMetrics.workpack_count, '0')} workpacks / {text(chainAuditMetrics.accepted_return_count, '0')} accepted returns</code>
          <code>{shortPath(text(chainAuditGate.latest_audit_path || chainAudit.run_path))}</code>
        </div>
      </div>
      <div className="ion-agent-discord-inspector-section">
        <span>task runs</span>
        <div className="ion-agent-discord-run-ledger">
          {runs.slice(0, 6).map((run) => <AgentCommsRunCard key={text(run.run_id)} run={run} />)}
          {runs.length === 0 ? <code>none</code> : null}
        </div>
      </div>
      <div className="ion-agent-discord-inspector-section">
        <span>return automation</span>
        <div className="ion-agent-discord-tab-ledger">
          {taskReturnAutomationDiagnoses.slice(0, 4).map((row, index) => (
            <code key={`${text(row.request_id, 'diagnosis')}-${index}`}>
              {text(row.classification, 'pending')} / manual {text(row.manual_ai_receipt_required, 'false')} / {shortPath(text(row.machine_receipt_path || row.return_packet_path))}
            </code>
          ))}
          {taskReturnAutomationDiagnoses.length === 0 ? <code>none</code> : null}
        </div>
      </div>
      <div className="ion-agent-discord-inspector-section">
        <span>machine receipts</span>
        <div className="ion-agent-discord-tab-ledger">
          {taskReturnMachineReceipts.slice(0, 4).map((row, index) => (
            <code key={`${text(row.path, 'receipt')}-${index}`}>
              {text(row.receipt_source, 'unknown')} / manual {text(row.manual_ai_authored, 'false')} / {shortPath(text(row.path))}
            </code>
          ))}
          {taskReturnMachineReceipts.length === 0 ? <code>none</code> : null}
        </div>
      </div>
      <div className="ion-agent-discord-inspector-section">
        <span>unread by role</span>
        <div className="ion-agent-discord-tab-ledger">
          {unreadRows.map(([role, value]) => <code key={role}>{displayRole(role)} {text(value)}</code>)}
          {unreadRows.length === 0 ? <code>none</code> : null}
        </div>
      </div>
      <div className="ion-agent-discord-inspector-section">
        <span>agent home projection</span>
        <CompactHomeProjectionCard homeView={homeView} compact />
      </div>
    </div>
  );
}

function AgentContactContractPanel({
  agents,
  contactContract,
}: {
  agents: Array<Record<string, unknown>>;
  contactContract: Record<string, unknown>;
}) {
  const aliasesByToken = record(contactContract.aliases_by_token);
  const aliasConflicts = record(contactContract.alias_conflicts);
  const templateContracts = Object.values(record(contactContract.template_contracts)).filter((item): item is Record<string, unknown> => (
    item !== null && typeof item === 'object' && !Array.isArray(item)
  ));
  const routingRules = records(contactContract.routing_rules);
  const escalationRoutes = records(contactContract.escalation_routes);
  const contactsByRole = record(contactContract.contacts_by_role);
  const groupsByRole = record(contactContract.contact_groups_by_role);
  const displayedRoles = agents
    .map((agent) => text(agent.role_id || agent.agent_id))
    .filter((roleId) => roleId && (Array.isArray(contactsByRole[roleId]) || groupsByRole[roleId]))
    .slice(0, 8);

  return (
    <section className="ion-agent-records-panel ion-agent-contact-contract-panel">
      <div className="ion-section-title">CONTACT CONTRACT</div>
      <div className="ion-agent-discord-inspector-metrics">
        <Metric label="agents" value={contactContract.available_agent_count ?? contactContract.agent_count} />
        <Metric label="edges" value={contactContract.contact_edge_count} />
        <Metric label="aliases" value={contactContract.alias_count ?? Object.keys(aliasesByToken).length} />
        <Metric label="conflicts" value={contactContract.alias_conflict_count ?? Object.keys(aliasConflicts).length} />
      </div>
      <div className="ion-agent-discord-inspector-section">
        <span>source</span>
        <div className="ion-agent-discord-tab-ledger">
          <code>{text(contactContract.schema_id, 'ion.agent_contact_contract.v1')}</code>
          <code>{text(contactContract.routing_source_of_truth, 'COMMUNICATION_DIRECTORY.json#contact_contract')}</code>
          <code>{text(contactContract.agent_decision_boundary, 'agent-owned contact decisions')}</code>
        </div>
      </div>
      <div className="ion-agent-discord-inspector-section">
        <span>routing rules</span>
        <div className="ion-agent-discord-tab-ledger">
          {routingRules.slice(0, 8).map((rule) => (
            <code key={text(rule.need || rule.contact_group)}>
              {text(rule.need)} / {text(rule.contact_group)} / {text(rule.template_hint)}
            </code>
          ))}
          {routingRules.length === 0 ? <code>none</code> : null}
        </div>
      </div>
      <div className="ion-agent-discord-inspector-section">
        <span>templates</span>
        <div className="ion-agent-discord-tab-ledger">
          {templateContracts.map((template) => (
            <code key={text(template.template_id)}>
              {text(template.template_id)} / {recordsToStrings(template.dispatch_modes).join(', ') || 'dispatch'} / {text(template.directive_schema_id)}
            </code>
          ))}
          {templateContracts.length === 0 ? <code>none</code> : null}
        </div>
      </div>
      <div className="ion-agent-discord-inspector-section">
        <span>escalations</span>
        <div className="ion-agent-discord-tab-ledger">
          {escalationRoutes.slice(0, 8).map((route) => (
            <code key={text(route.route_id)}>
              {text(route.route_id)} / {recordsToStrings(route.available_roles).join(', ') || 'no available role'} / {text(route.default_template_id)}
            </code>
          ))}
          {escalationRoutes.length === 0 ? <code>none</code> : null}
        </div>
      </div>
      <div className="ion-agent-discord-inspector-section">
        <span>agent contact groups</span>
        <div className="ion-agent-discord-run-ledger">
          {displayedRoles.map((roleId) => {
            const contacts = records(contactsByRole[roleId]);
            const groups = record(groupsByRole[roleId]);
            const populatedGroups = Object.entries(groups)
              .filter(([, value]) => Array.isArray(value) && value.length)
              .slice(0, 4);
            return (
              <article className="ion-agent-discord-run-card" key={roleId}>
                <header className="ion-agent-discord-run-card-head">
                  <div>
                    <b>{displayRole(roleId)}</b>
                    <span>{contacts.length} contacts</span>
                  </div>
                  <code>{roleId}</code>
                </header>
                <div className="ion-agent-discord-policy-row">
                  {populatedGroups.map(([groupId, value]) => (
                    <code key={groupId}>{groupId} {recordsToStrings(value).length}</code>
                  ))}
                  {populatedGroups.length === 0 ? <code>no groups</code> : null}
                </div>
                {contacts.slice(0, 4).map((contact) => (
                  <small key={text(contact.role_id)}>
                    {displayRole(text(contact.role_id))} / {recordsToStrings(contact.relationship_tags).join(', ') || 'general'}
                  </small>
                ))}
              </article>
            );
          })}
          {displayedRoles.length === 0 ? <code>none</code> : null}
        </div>
      </div>
    </section>
  );
}

function AgentRoomContractPanel({
  roomContract,
  roomProjection,
}: {
  roomContract: Record<string, unknown>;
  roomProjection: Record<string, unknown>;
}) {
  const roomKinds = records(roomContract.room_kinds);
  const routingRules = records(roomContract.routing_rules);
  const reportingRules = records(roomContract.reporting_rules);
  const defaultRooms = records(roomContract.default_rooms);
  const domainRooms = records(roomContract.domain_rooms);
  const activeRooms = records(roomProjection.rooms);
  const contextLoading = record(roomContract.context_loading);
  const kindCounts = record(roomProjection.room_kind_counts);

  return (
    <section className="ion-agent-records-panel ion-agent-room-contract-panel">
      <div className="ion-section-title">ROOM CONTRACT</div>
      <div className="ion-agent-discord-inspector-metrics">
        <Metric label="contract" value={roomContract.room_count ?? defaultRooms.length + domainRooms.length} />
        <Metric label="active" value={roomProjection.room_count ?? activeRooms.length} />
        <Metric label="kinds" value={roomKinds.length || Object.keys(kindCounts).length} />
        <Metric label="reports" value={reportingRules.length} />
      </div>
      <div className="ion-agent-discord-inspector-section">
        <span>source</span>
        <div className="ion-agent-discord-tab-ledger">
          <code>{text(roomContract.schema_id, 'ion.agent_room_contract.v1')}</code>
          <code>{text(roomContract.routing_source_of_truth, 'COMMUNICATION_DIRECTORY.json#room_contract')}</code>
          <code>{text(roomContract.agent_decision_boundary, 'agent-owned room selection')}</code>
          <code>{text(contextLoading.rule, 'read room capsule first')}</code>
        </div>
      </div>
      <div className="ion-agent-discord-inspector-section">
        <span>room kinds</span>
        <div className="ion-agent-discord-tab-ledger">
          {roomKinds.map((kind) => (
            <code key={text(kind.room_kind)}>
              {text(kind.room_kind)} / {text(kind.default_visibility)} / summary {text(kind.summary_required)}
            </code>
          ))}
          {roomKinds.length === 0 ? <code>none</code> : null}
        </div>
      </div>
      <div className="ion-agent-discord-inspector-section">
        <span>routing</span>
        <div className="ion-agent-discord-tab-ledger">
          {routingRules.slice(0, 8).map((rule) => (
            <code key={text(rule.need || rule.default_room_id)}>
              {text(rule.need)} / {text(rule.room_kind)} / {text(rule.default_room_id || rule.channel_id)}
            </code>
          ))}
          {routingRules.length === 0 ? <code>none</code> : null}
        </div>
      </div>
      <div className="ion-agent-discord-inspector-section">
        <span>reports</span>
        <div className="ion-agent-discord-tab-ledger">
          {reportingRules.map((rule) => (
            <code key={text(rule.room_kind)}>
              {text(rule.room_kind)}{' -> '}{text(rule.report_to_room_id)} / {text(rule.rule)}
            </code>
          ))}
          {reportingRules.length === 0 ? <code>none</code> : null}
        </div>
      </div>
      <div className="ion-agent-discord-inspector-section">
        <span>default rooms</span>
        <div className="ion-agent-discord-run-ledger">
          {[...defaultRooms, ...domainRooms].slice(0, 8).map((room) => (
            <article className="ion-agent-discord-run-card" key={text(room.room_id)}>
              <header className="ion-agent-discord-run-card-head">
                <div>
                  <b>{text(room.display_name || room.room_id)}</b>
                  <span>{text(room.room_kind)} / #{text(room.channel_id)}</span>
                </div>
                <code>{text(room.room_id)}</code>
              </header>
              <small>{text(room.purpose)}</small>
              <div className="ion-agent-discord-policy-row">
                <code>{recordsToStrings(room.default_participants).length} participants</code>
                <code>report {text(room.report_to_room_id, 'none')}</code>
                <code>summary {text(room.summary_required)}</code>
              </div>
            </article>
          ))}
          {defaultRooms.length + domainRooms.length === 0 ? <code>none</code> : null}
        </div>
      </div>
      <div className="ion-agent-discord-inspector-section">
        <span>active capsules</span>
        <div className="ion-agent-discord-run-ledger">
          {activeRooms.slice(0, 8).map((room) => (
            <article className="ion-agent-discord-run-card" key={text(room.room_id)}>
              <header className="ion-agent-discord-run-card-head">
                <div>
                  <b>{text(room.room_id)}</b>
                  <span>{text(room.room_kind)} / {text(room.thread_count, '0')} threads</span>
                </div>
                <code>{shortPath(text(room.room_capsule_path))}</code>
              </header>
              <small>{text(room.latest_summary, 'no summary')}</small>
              <div className="ion-agent-discord-policy-row">
                <code>latest {text(room.latest_message_id, 'none')}</code>
                <code>report {text(room.report_to_room_id, 'none')}</code>
                <code>{recordsToStrings(room.participants).length} participants</code>
              </div>
            </article>
          ))}
          {activeRooms.length === 0 ? <code>none</code> : null}
        </div>
      </div>
    </section>
  );
}

function AgentCommsRunCard({ run }: { run: Record<string, unknown> }) {
  const graph = record(run.graph);
  const policyGate = record(run.policy_gate);
  const policyChecks = records(policyGate.checks);
  const graphEdges = records(graph.edges);
  const workItems = records(run.work_items);
  const workerRuntime = record(run.worker_runtime);
  const latestAgentMessage = record(run.latest_agent_message);
  const latestReturnPath = runLatestReturnPath(run);
  const latestReplyPath = runLatestReplyPath(run);
  const workpackPath = runWorkpackPath(run);
  const followupDecision = record(run.followup_decision);
  const latestDecision = record(followupDecision.latest_decision);
  return (
    <article className={`ion-agent-discord-run-card is-${slug(text(run.operational_state, 'unknown'))}${truth(workerRuntime.has_active_worker) ? ' is-worker-running' : ''}`}>
      <header className="ion-agent-discord-run-card-head">
        <div>
          <b>{text(run.objective, 'run')}</b>
          <span>{text(run.status, 'idle')} / {runOperationalText(run)} / {runWorkerText(run)} / {runPolicyText(run)}</span>
        </div>
        <code>{runProofLabel(run)}</code>
      </header>
      <div className="ion-agent-discord-proof-chain" aria-label="Run proof chain">
        <AgentCommsProofStep label="message" state={recordsToStrings(run.root_message_ids).length ? 'sent' : 'missing'} value={first(recordsToStrings(run.root_message_ids)) || text(run.run_id)} />
        <AgentCommsProofStep label="workpack" state={workpackPath ? text(workItems[0]?.response_state || workItems[0]?.work_request_status, 'active') : 'missing'} value={workpackPath} />
        <AgentCommsProofStep label="worker" state={runWorkerState(run)} value={runWorkerValue(run)} />
        <AgentCommsProofStep label="return" state={latestReturnPath ? text(workItems[0]?.latest_return_summary, 'accepted') : 'waiting'} value={latestReturnPath} />
        <AgentCommsProofStep label="decision" state={runFollowupDecisionText(run)} value={text(latestDecision.reason || latestDecision.agent || followupDecision.state)} />
        <AgentCommsProofStep label="reply" state={latestReplyPath ? displayRole(text(latestAgentMessage.from_role, 'agent')) : 'waiting'} value={latestReplyPath || text(latestAgentMessage.message_id)} />
      </div>
      <small>graph {text(graph.node_count, '0')} nodes / {text(graph.edge_count, '0')} edges</small>
      <div className="ion-agent-discord-policy-row">
        {policyChecks.slice(0, 6).map((check) => (
          <code className={truth(check.ok) ? 'is-ok' : 'is-blocked'} key={text(check.limit)}>
            {text(check.limit)} {text(check.used, '0')}/{text(check.max, '0')}
          </code>
        ))}
      </div>
      <div className="ion-agent-discord-graph-flow">
        {graphEdges.slice(-5).map((edge) => (
          <code key={text(edge.id)}>{text(edge.kind)}: {compactGraphId(text(edge.source))}{' -> '}{compactGraphId(text(edge.target))}</code>
        ))}
      </div>
      {workItems.slice(0, 2).map((item) => (
        <small key={text(item.workpack_path)}>
          {text(item.response_state, 'pending')} / {text(item.agent_display_name || item.agent_role_id, 'agent')} / returns {text(item.task_return_count, '0')} / {text(item.work_request_status, 'queued')}
          {' / '}{runWorkItemDecisionText(item)}
        </small>
      ))}
    </article>
  );
}

function AgentCommsProofStep({ label, state, value }: { label: string; state: string; value: string }) {
  const hasValue = Boolean(value);
  return (
    <div className={`ion-agent-discord-proof-step${hasValue ? '' : ' is-missing'}`}>
      <span>{label}</span>
      <b>{state || 'missing'}</b>
      <code>{value || 'missing'}</code>
    </div>
  );
}

function AgentCommsWorkPanel({
  message,
  onBranch,
  onOpenThread,
}: {
  message: Record<string, unknown>;
  onBranch?: (messageId: string) => void;
  onOpenThread?: (threadId: string) => void;
}) {
  const panel = record(message.work_panel);
  const tabs = records(panel.tabs);
  const defaultTab = text(tabs[0]?.tab_id, 'message');
  const [activeTab, setActiveTab] = useState(defaultTab);
  const selectedTab = tabs.find((tab) => text(tab.tab_id) === activeTab) ?? tabs[0] ?? {};
  const selectedRecords = records(selectedTab.records);
  const navigation = record(panel.navigation);
  const messageId = text(message.message_id || panel.message_id);
  const subject = text(panel.subject || message.subject, 'Agent message');
  const body = text(message.body || panel.summary);
  const copyPanel = () => {
    if (typeof navigator === 'undefined' || !navigator.clipboard) return;
    const payload = {
      message_id: messageId,
      thread_id: text(message.thread_id || panel.thread_id),
      subject,
      body,
      work_panel: panel,
    };
    void navigator.clipboard.writeText(JSON.stringify(payload, null, 2));
  };
  return (
    <article className={`ion-codex-assistant-work-panel ion-agent-work-message is-${slug(text(message.message_kind, 'thread_note'))}`}>
      <div className="ion-codex-work-tabbar ion-agent-work-message-tabbar">
        <div className="ion-codex-work-tabs ion-agent-work-message-tabs" role="tablist" aria-label="Agent message work tabs">
          {tabs.map((tab) => (
            <button
              className={text(tab.tab_id) === activeTab ? 'is-active' : undefined}
              key={text(tab.tab_id)}
              onClick={() => setActiveTab(text(tab.tab_id))}
              type="button"
            >
              <span>{text(tab.label || tab.tab_id)}</span>
              <b>{text(tab.count, '0')}</b>
            </button>
          ))}
        </div>
        <div className="ion-codex-work-tab-actions ion-agent-work-message-actions">
          <div className="ion-codex-message-actions is-inline">
            <button onClick={copyPanel} title={`${text(panel.body_chars, '0')} chars plus tab metadata`} type="button">COPY</button>
            <button disabled={!onBranch || !truth(navigation.can_branch)} onClick={() => onBranch?.(messageId)} title={`branch from ${messageId}`} type="button">BRANCH</button>
          </div>
          <time>{text(message.created_at || panel.created_at)}</time>
        </div>
      </div>
      <div className="ion-agent-work-message-meta">
        <b>{text(message.from_role || panel.from_role)}</b>
        <span>{text(message.message_kind || panel.message_kind)} / {text(message.status, 'sent')}</span>
        <code>{messageId}</code>
      </div>
      <div className="ion-codex-work-body ion-agent-work-message-body">
        <div className="ion-codex-work-event-stack">
          {selectedRecords.map((item, index) => (
            <AgentCommsWorkRecord
              key={`${text(item.kind || item.title)}-${index}`}
              record={item}
              onOpenThread={onOpenThread}
            />
          ))}
          {selectedRecords.length === 0 ? <div className="ion-empty-state">NO {text(selectedTab.label, 'TAB')} RECORDS</div> : null}
        </div>
      </div>
    </article>
  );
}

function AgentCommsWorkRecord({
  record: row,
  onOpenThread,
}: {
  record: Record<string, unknown>;
  onOpenThread?: (threadId: string) => void;
}) {
  const detail = text(row.detail || row.summary || row.message_id || row.thread_id);
  const threadId = text(row.thread_id);
  return (
    <div className={`ion-codex-work-event ion-agent-work-record is-${slug(text(row.kind, 'record'))}`}>
      <div>
        <span>{text(row.title || row.kind, 'record')}</span>
        {text(row.status) ? <b>{text(row.status)}</b> : null}
        {threadId && onOpenThread ? (
          <button onClick={() => onOpenThread(threadId)} type="button">OPEN</button>
        ) : null}
      </div>
      {detail ? <p>{detail}</p> : null}
    </div>
  );
}

function AutomationKernelView({
  automation,
  busy,
  onRuntimeRefresh,
  setBusy,
  setRequestState,
}: {
  automation: Record<string, unknown>;
  busy: boolean;
  onRuntimeRefresh?: () => void;
  setBusy: (busy: boolean) => void;
  setRequestState: (state: Record<string, unknown> | null) => void;
}) {
  const actions = records(automation.actions);
  const summary = record(automation.summary);
  const starter = record(automation.starter_capsule);
  const portable = record(automation.portable_packages);
  const directivePickup = record(automation.agent_comms_directive_pickup);
  const directiveAction = actions.find((action) => text(action.action_id) === 'agent_comms.process_directives');
  const directiveProcessed = records(directivePickup.recent_processed);
  const directiveReceipts = records(directivePickup.recent_receipts);
  const directiveModes = recordsToStrings(directivePickup.allowed_dispatch_modes);
  const receipts = records(automation.recent_receipts);
  const confirmation = text(automation.confirmation_token, 'ION_BOUNDED_WRITE_CONFIRMED');
  const [directiveText, setDirectiveText] = useState('');
  const [directiveLimit, setDirectiveLimit] = useState(25);

  const runAction = async (action: Record<string, unknown>) => {
    if (busy) return;
    const actionId = text(action.action_id);
    const payload: Record<string, unknown> = {
      action_id: actionId,
      confirmation: truth(action.requires_confirmation) ? confirmation : undefined,
    };
    if (actionId === 'agent_comms.process_directives') {
      payload.text = directiveText.trim() || undefined;
      payload.source_ref = 'cockpit://automations/agent_comms.process_directives';
      payload.from_role = 'operator';
      payload.limit = directiveLimit;
      payload.max_directives = Math.max(1, Math.min(Number(directiveLimit) || 25, 50));
    }
    setBusy(true);
    try {
      const response = await fetch('/cockpit/automations/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify(payload),
      });
      const result = (await response.json()) as Record<string, unknown>;
      setRequestState(result);
      await onRuntimeRefresh?.();
    } catch (error) {
      setRequestState({ ok: false, finding: error instanceof Error ? error.message : 'automation_request_failed' });
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="ion-agent-automation-view">
      <header className="ion-agent-automation-head">
        <div>
          <div className="ion-section-title">ION / CAPSULE AUTOMATION KERNEL</div>
          <h1>{text(automation.verdict, 'AUTOMATION MODEL MISSING')}</h1>
          <p>Bounded Python/kernel actions exposed through the cockpit. These are generated-artifact and context operations, not production or accepted-state authority.</p>
        </div>
        <Metric label="actions" value={summary.action_count} />
        <Metric label="starter" value={truth(summary.starter_ready) ? 'ready' : 'missing'} />
        <Metric label="packages" value={summary.portable_package_count} />
        <Metric label="files" value={summary.portable_package_files} />
      </header>
      <div className="ion-agent-automation-grid">
        <section>
          <div className="ion-section-title">CONTEXT STARTER</div>
          <Path label="operator final" value={text(starter.operator_final_path)} />
          <Path label="copy policy" value={text(starter.copy_policy)} />
          <Path label="launch" value={text(starter.launch_command_template)} />
          <Path label="create" value={text(starter.create_command_template)} />
          <Metric label="ready" value={truth(starter.ready) ? 'yes' : 'no'} />
        </section>
        <section>
          <div className="ion-section-title">PORTABLE PACKAGES</div>
          <Path label="root" value={text(portable.root)} />
          <Path label="snapshot policy" value={text(portable.directory_snapshot_policy)} />
          <Metric label="latest" value={portable.latest_count} />
          <Metric label="files" value={record(portable.tree_stats).files} />
        </section>
        <section className="is-wide ion-agent-directive-pickup">
          <div className="ion-section-title">DIRECTIVE PICKUP</div>
          <div className="ion-agent-directive-pickup-metrics">
            <Metric label="processed" value={directivePickup.processed_count} />
            <Metric label="receipts" value={directivePickup.receipt_count} />
            <Metric label="schema" value={directivePickup.directive_schema_id} />
            <Metric label="fence" value={directivePickup.directive_fence} />
          </div>
          <Path label="action" value={text(directivePickup.action_id)} />
          <Path label="ledger" value={text(directivePickup.ledger_path)} />
          <Path label="receipt dir" value={text(directivePickup.receipt_dir)} />
          <div className="ion-agent-directive-modes">
            {directiveModes.map((mode) => <code key={mode}>{mode}</code>)}
          </div>
          <textarea
            aria-label="Agent comms directive block"
            onChange={(event) => setDirectiveText(event.target.value)}
            placeholder={'```ion-agent-comms\n{\n  "schema_id": "ion.agent_comms.directive.v1",\n  "agent": "role.ionologist",\n  "objective": "Review the packet.",\n  "body": "Return a bounded decision."\n}\n```'}
            rows={8}
            value={directiveText}
          />
          <div className="ion-agent-directive-actions">
            <label>
              <span>limit</span>
              <input
                min={1}
                max={50}
                onChange={(event) => setDirectiveLimit(Number(event.target.value) || 25)}
                type="number"
                value={directiveLimit}
              />
            </label>
            <button disabled={busy || !directiveAction} onClick={() => directiveAction && void runAction(directiveAction)} type="button">PICK UP</button>
          </div>
          <div className="ion-agent-directive-ledger">
            {directiveProcessed.slice(0, 4).map((item) => (
              <article className="ion-agent-record-card" key={text(item.directive_id)}>
                <b>{text(item.agent || item.directive_id)}</b>
                <p>{text(item.finding || item.spawn_status || item.dispatch_mode)}</p>
                <code>{text(item.workpack_path || item.comms_message_id || item.source_ref)}</code>
              </article>
            ))}
            {directiveProcessed.length === 0 ? <div className="ion-empty-state">NO PROCESSED DIRECTIVES</div> : null}
          </div>
          <div className="ion-agent-directive-ledger">
            {directiveReceipts.slice(0, 3).map((receipt) => (
              <article className="ion-agent-record-card" key={text(receipt.path)}>
                <b>{truth(receipt.ok) ? 'ok' : 'finding'}</b>
                <p>{text(receipt.processed_directive_count, '0')} processed / {text(receipt.finding_count, '0')} findings</p>
                <code>{text(receipt.path)}</code>
              </article>
            ))}
            {directiveReceipts.length === 0 ? <div className="ion-empty-state">NO DIRECTIVE RECEIPTS</div> : null}
          </div>
        </section>
        <section className="is-wide">
          <div className="ion-section-title">RUN ACTIONS</div>
          <div className="ion-agent-automation-actions">
            {actions.map((action) => {
              const actionId = text(action.action_id);
              return (
              <article key={actionId}>
                <header>
                  <b>{text(action.label || action.action_id)}</b>
                  <span>{text(action.mode)}</span>
                </header>
                <p>{text(action.description)}</p>
                <footer>
                  <code>{actionId}</code>
                  <button disabled={busy} onClick={() => void runAction(action)} type="button">
                    {actionId === 'agent_comms.process_directives' ? 'PICK UP' : truth(action.requires_confirmation) ? 'RUN GATED' : 'RUN'}
                  </button>
                </footer>
              </article>
              );
            })}
            {actions.length === 0 ? <div className="ion-empty-state">NO AUTOMATIONS REGISTERED</div> : null}
          </div>
        </section>
        <section>
          <div className="ion-section-title">RECENT AUTOMATION RECEIPTS</div>
          <div className="ion-agent-record-stack">
            {receipts.map((receipt) => (
              <article className="ion-agent-record-card" key={text(receipt.path)}>
                <b>{text(receipt.action_id)}</b>
                <p>{text(receipt.summary)}</p>
                <code>{text(receipt.path)}</code>
              </article>
            ))}
            {receipts.length === 0 ? <div className="ion-empty-state">NO AUTOMATION RECEIPTS</div> : null}
          </div>
        </section>
      </div>
    </section>
  );
}

function AgentSettingsView({ model, requestState }: { model: IonAgentControlPlane; requestState: Record<string, unknown> | null }) {
  return (
    <section className="ion-agent-settings-view">
      <JsonView title="SETTINGS" value={{ source_model: model.source_model, settings: model.settings, authority: model.authority }} />
      <JsonView title="DIAGNOSTICS" value={model.diagnostics} />
      <JsonView title="LATEST REQUEST" value={requestState ?? model.runs?.latest_state ?? {}} />
    </section>
  );
}

function AgentRail({
  agents,
  selectedAgent,
  setSelectedAgentId,
}: {
  agents: Array<Record<string, unknown>>;
  selectedAgent: Record<string, unknown>;
  setSelectedAgentId: (id: string) => void;
}) {
  return (
    <aside className="ion-agent-selector">
      <div className="ion-agent-rail-header">
        <div className="ion-section-title">AGENTS</div>
        <b>{agents.length}</b>
      </div>
      <div className="ion-agent-rail-list">
        {agents.map((agent) => {
          const id = text(agent.role_id || agent.agent_id);
          return (
            <button
              className={text(selectedAgent.role_id || selectedAgent.agent_id) === id ? 'is-active' : undefined}
              key={id}
              onClick={() => setSelectedAgentId(id)}
              type="button"
            >
              <b>{text(agent.display_name || agent.role_id)}</b>
              <span>{text(agent.registry_primary_domain || agent.backend_carrier_id)}</span>
              <code>{truth(agent.invocable) ? 'invocable' : text(agent.context_system_status, 'context')}</code>
            </button>
          );
        })}
      </div>
    </aside>
  );
}

function AgentConsoleView({
  busy,
  copyLaunchPacket,
  invoke,
  objective,
  requestState,
  selectedAgent,
  selectedDomain,
  selectedMount,
  selectedRuns,
  selectedTimeline,
  setObjective,
}: {
  busy: boolean;
  copyLaunchPacket: () => void;
  invoke: (endpoint: string) => Promise<void>;
  objective: string;
  requestState: Record<string, unknown> | null;
  selectedAgent: Record<string, unknown>;
  selectedDomain: Record<string, unknown>;
  selectedMount: Record<string, unknown>;
  selectedRuns: Array<Record<string, unknown>>;
  selectedTimeline: Array<Record<string, unknown>>;
  setObjective: (objective: string) => void;
}) {
  const latestRun = selectedRuns[0] ?? {};
  const runStatus = text(latestRun.status || requestState?.status || requestState?.finding, 'idle');
  return (
    <section className="ion-agent-console-view">
      <header className="ion-agent-console-hero">
        <div>
          <div className="ion-section-title">AGENT PAGE</div>
          <h1>{text(selectedAgent.display_name || selectedAgent.role_id, 'NO AGENT')}</h1>
          <p>{text(selectedAgent.package_strategy || selectedDomain.purpose || selectedAgent.default_mount_posture)}</p>
        </div>
        <div className="ion-agent-console-status">
          <Metric label="domain" value={selectedAgent.registry_primary_domain} />
          <Metric label="context" value={selectedAgent.context_system_status} />
          <Metric label="mount" value={truth(selectedMount.materialized) ? 'ready' : 'planned'} />
          <Metric label="package" value={truth(selectedMount.active_context_package_md_exists) ? 'ready' : 'missing'} />
        </div>
      </header>

      <div className="ion-agent-console-grid">
        <section className="ion-agent-talk-panel">
          <div className="ion-section-title">TALK / TASK</div>
          <textarea value={objective} onChange={(event) => setObjective(event.target.value)} rows={8} />
          <div className="ion-agent-primary-actions">
            <button disabled={busy} onClick={() => void invoke('/cockpit/agents/prepare')} type="button">PREPARE TASK</button>
            <button disabled={busy} onClick={() => void invoke('/cockpit/agents/start')} type="button">START WORKER</button>
            <button onClick={copyLaunchPacket} type="button">COPY LAUNCH</button>
          </div>
        </section>

        <section className="ion-agent-now-panel">
          <div className="ion-section-title">CURRENT WORK</div>
          <div className={`ion-agent-work-state is-${slug(runStatus)}`}>{runStatus}</div>
          <Path label="invocation" value={text(latestRun.invocation_id || requestState?.invocation_id)} />
          <Path label="request" value={text(latestRun.codex_work_request_path || requestState?.codex_work_request_path)} />
          <Path label="return" value={text(latestRun.latest_return_packet_path || requestState?.latest_return_packet_path)} />
          <Path label="receipt" value={text(first(recordsToStrings(latestRun.receipt_paths)))} />
        </section>

        <section className="ion-agent-context-summary">
          <div className="ion-section-title">ACTIVE CONTEXT</div>
          <Path label="package" value={text(selectedMount.active_context_package_md_path)} />
          <Path label="agents" value={text(selectedMount.agents_md_path)} />
          <Path label="config" value={text(selectedMount.config_path)} />
          <List label="read first" values={recordsToStrings(selectedAgent.context_paths).slice(0, 6)} />
        </section>

        <section className="ion-agent-evidence-panel">
          <div className="ion-section-title">RECENT EVIDENCE</div>
          {selectedTimeline.map((event, index) => (
            <TimelineRow event={event} key={`${text(event.kind)}-${text(event.timestamp)}-${index}`} />
          ))}
          {selectedTimeline.length === 0 ? <div className="ion-empty-state">NO RECENT EVENTS FOR THIS AGENT</div> : null}
        </section>
      </div>
    </section>
  );
}

function AgentContextView({
  selectedAgent,
  selectedDomain,
  selectedMount,
}: {
  selectedAgent: Record<string, unknown>;
  selectedDomain: Record<string, unknown>;
  selectedMount: Record<string, unknown>;
}) {
  return (
    <section className="ion-agent-context-view">
      <AgentCard agent={selectedAgent} />
      <DomainCard domain={selectedDomain} />
      <MountCard mount={selectedMount} />
    </section>
  );
}

function AgentInspector({
  model,
  requestState,
  selectedAgent,
  selectedMount,
  selectedTimeline,
}: {
  model: IonAgentControlPlane;
  requestState: Record<string, unknown> | null;
  selectedAgent: Record<string, unknown>;
  selectedMount: Record<string, unknown>;
  selectedTimeline: Array<Record<string, unknown>>;
}) {
  const latestRun = records(model.runs?.recent_invocations).find((run) => agentMatchesRecord(run, selectedAgent)) ?? {};
  return (
    <aside className="ion-agent-inspector">
      <section>
        <div className="ion-section-title">SELECTED AGENT</div>
        <h2>{text(selectedAgent.display_name || selectedAgent.role_id, 'NO AGENT')}</h2>
        <div className="ion-agent-boundary-grid">
          <Metric label="production" value={model.production_authority ? 'yes' : 'no'} />
          <Metric label="live exec" value={model.live_execution_authority ? 'yes' : 'no'} />
          <Metric label="accepted" value={model.accepted_state_authority ? 'yes' : 'no'} />
          <Metric label="secrets" value={model.secrets_authority ? 'yes' : 'no'} />
        </div>
      </section>
      <section>
        <div className="ion-section-title">CODEX MOUNT</div>
        <Path label="cwd" value={text(record(selectedMount.native_codex).launch_cwd || selectedMount.mount_abspath || selectedMount.mount_path)} />
        <Path label="context package" value={text(selectedMount.active_context_package_md_path)} />
        <Path label="manifest" value={text(selectedMount.manifest_path)} />
        <Path label="config" value={text(selectedMount.config_path)} />
      </section>
      <section>
        <div className="ion-section-title">LAST RESULT</div>
        <p>{text(requestState?.finding || requestState?.status || latestRun.status || 'No active request selected.')}</p>
        <Path label="request" value={text(requestState?.codex_work_request_path || latestRun.codex_work_request_path)} />
        <Path label="return" value={text(requestState?.latest_return_packet_path || latestRun.latest_return_packet_path)} />
      </section>
      <section>
        <div className="ion-section-title">AGENT EVENTS</div>
        {selectedTimeline.slice(0, 8).map((event, index) => (
          <TimelineRow event={event} key={`${text(event.kind)}-${text(event.timestamp)}-${index}`} compact />
        ))}
        {selectedTimeline.length === 0 ? <div className="ion-empty-state">NO EVENTS</div> : null}
      </section>
    </aside>
  );
}

function CommsView({
  agents,
  busy,
  model,
  onRuntimeRefresh,
  selectedAgent,
  setBusy,
  setRequestState,
}: {
  agents: Array<Record<string, unknown>>;
  busy: boolean;
  model: IonAgentControlPlane;
  onRuntimeRefresh?: () => void;
  selectedAgent: Record<string, unknown>;
  setBusy: (busy: boolean) => void;
  setRequestState: (state: Record<string, unknown> | null) => void;
}) {
  const communications = record(model.communications);
  const allInvocations = records(communications.invocations);
  const allRelays = records(communications.relays);
  const selectedAgentId = text(selectedAgent.role_id || selectedAgent.agent_id);
  const invocations = allInvocations.filter((invocation) => agentMatchesRecord(invocation, selectedAgent));
  const relays = allRelays.filter((relay) => agentMatchesRecord(relay, selectedAgent));
  const pendingRelays = records(communications.pending_relays).filter((relay) => agentMatchesRecord(relay, selectedAgent));
  const timeline = records(communications.timeline).filter((event) => agentMatchesRecord(event, selectedAgent));
  const preferredTarget = text(selectedAgent.role_id) === 'role.ionologist'
    ? agents.find((agent) => text(agent.role_id) === 'role.codex_carrier_steward')
    : agents.find((agent) => text(agent.role_id) === 'role.ionologist');
  const firstTarget = text(preferredTarget?.role_id || agents.find((agent) => text(agent.role_id) !== selectedAgentId)?.role_id, 'chatgpt_browser');
  const [selectedInvocationId, setSelectedInvocationId] = useState('');
  const [target, setTarget] = useState(firstTarget);
  const [question, setQuestion] = useState('Review this agent invocation and respond with the next proof-bound step.');
  const [relayResponse, setRelayResponse] = useState('Acknowledged. Continue with proof-bound context and receipt preservation.');
  const [settlementSummary, setSettlementSummary] = useState('Visible agent communication reviewed with relay/receipt evidence.');
  const invocationId = selectedInvocationId || text(invocations[0]?.invocation_id);
  const selectedInvocation = invocations.find((item) => text(item.invocation_id) === invocationId) ?? invocations[0] ?? {};
  const selectedRelay = pendingRelays[0] ?? relays[0] ?? {};
  const selectedRelayId = text(selectedRelay.relay_id);
  const targetValue = target || firstTarget;

  const post = async (endpoint: string, payload: Record<string, unknown>) => {
    if (busy) return;
    setBusy(true);
    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify(payload),
      });
      const result = (await response.json()) as Record<string, unknown>;
      setRequestState(result);
      await onRuntimeRefresh?.();
    } catch (error) {
      setRequestState({ ok: false, finding: error instanceof Error ? error.message : 'agent_comms_request_failed' });
    } finally {
      setBusy(false);
    }
  };

  const createRelay = () => {
    if (!invocationId) {
      setRequestState({ ok: false, finding: 'prepare_or_start_an_invocation_before_creating_relay' });
      return;
    }
    void post('/cockpit/agents/relay/create', {
      invocation_id: invocationId,
      to: targetValue,
      question_type: targetValue.startsWith('role.') ? 'agent_to_agent' : 'operator_or_carrier',
      question,
      evidence_refs: [text(selectedInvocation.path), text(selectedInvocation.codex_work_request_path)].filter(Boolean),
    });
  };

  const answerRelay = () => {
    if (!selectedRelayId) {
      setRequestState({ ok: false, finding: 'no_pending_or_recent_relay_to_answer' });
      return;
    }
    void post('/cockpit/agents/relay/respond', {
      relay_id: selectedRelayId,
      answered_by: targetValue,
      response: relayResponse,
      continue: true,
    });
  };

  const settleInvocation = () => {
    if (!invocationId) {
      setRequestState({ ok: false, finding: 'no_invocation_to_settle' });
      return;
    }
    void post('/cockpit/agents/settle', {
      invocation_id: invocationId,
      terminal_state: 'accepted',
      settled_by: 'operator_cockpit',
      summary: settlementSummary,
      evidence_refs: [text(selectedInvocation.path), text(selectedInvocation.codex_work_request_path), text(selectedRelay.path)].filter(Boolean),
    });
  };

  return (
    <section className="ion-agent-comms-view">
      <div className="ion-agent-comms-composer">
        <div className="ion-section-title">AGENT CONVERSATION</div>
        <select value={invocationId} onChange={(event) => setSelectedInvocationId(event.target.value)}>
          {invocations.map((invocation) => (
            <option key={text(invocation.invocation_id)} value={text(invocation.invocation_id)}>
              {text(invocation.agent_display_name || invocation.agent_role_id)} / {text(invocation.status)}
            </option>
          ))}
          {invocations.length === 0 ? <option value="">NO WORK THREAD FOR SELECTED AGENT</option> : null}
        </select>
        <select value={targetValue} onChange={(event) => setTarget(event.target.value)}>
          <option value="chatgpt_browser">CHATGPT BROWSER</option>
          <option value="operator">OPERATOR</option>
          {agents.filter((agent) => text(agent.role_id) !== selectedAgentId).map((agent) => (
            <option key={text(agent.role_id)} value={text(agent.role_id)}>
              {text(agent.display_name || agent.role_id)}
            </option>
          ))}
        </select>
        <textarea value={question} onChange={(event) => setQuestion(event.target.value)} rows={4} />
        <textarea value={relayResponse} onChange={(event) => setRelayResponse(event.target.value)} rows={4} />
        <textarea value={settlementSummary} onChange={(event) => setSettlementSummary(event.target.value)} rows={3} />
        <div className="ion-agent-action-grid">
          <button disabled={busy || !invocationId} onClick={createRelay} type="button">RELAY</button>
          <button disabled={busy || !selectedRelayId} onClick={answerRelay} type="button">ANSWER</button>
          <button disabled={busy || !invocationId} onClick={settleInvocation} type="button">SETTLE</button>
          <button disabled={busy} onClick={() => void onRuntimeRefresh?.()} type="button">SYNC</button>
        </div>
      </div>
      <div className="ion-agent-comms-lanes">
        <div className="ion-agent-comms-summary">
          <Metric label="invocations" value={record(communications.summary).invocation_count} />
          <Metric label="relays" value={record(communications.summary).relay_count} />
          <Metric label="pending" value={record(communications.summary).pending_relay_count} />
          <Metric label="receipts" value={record(communications.summary).receipt_count} />
        </div>
        <div className="ion-agent-relay-list">
          <div className="ion-section-title">RELAYS</div>
          {relays.map((relay) => (
            <article className={text(relay.relay_id) === selectedRelayId ? 'is-active' : undefined} key={text(relay.relay_id)}>
              <b>{text(relay.from_agent)} {'->'} {text(relay.to)}</b>
              <span>{text(relay.status)} / {text(relay.question_type)}</span>
              <p>{text(relay.question)}</p>
              <code>{text(relay.path)}</code>
            </article>
          ))}
          {relays.length === 0 ? <div className="ion-empty-state">NO RELAYS</div> : null}
        </div>
        <div className="ion-agent-comms-timeline">
          <div className="ion-section-title">TIMELINE</div>
          {timeline.map((event, index) => (
            <article className={`ion-agent-comms-row is-${text(event.kind, 'event')}`} key={`${text(event.kind)}-${text(event.timestamp)}-${index}`}>
              <span>{text(event.kind)}</span>
              <b>{text(event.status || event.event || event.question_type)}</b>
              <p>{text(event.question || event.agent_display_name || event.from_agent || event.receipt_id || event.invocation_id)}</p>
              <code>{text(event.path || event.codex_work_request_path)}</code>
            </article>
          ))}
          {timeline.length === 0 ? <div className="ion-empty-state">NO COMMS EVENTS</div> : null}
        </div>
      </div>
    </section>
  );
}

function ChainView({ model }: { model: IonAgentControlPlane }) {
  const steps = records(model.chain?.steps);
  return (
    <section className="ion-agent-chain-panel">
      <div className="ion-agent-chain">
        {steps.map((step) => (
          <article className={`ion-agent-chain-step is-${text(step.direction, 'work')}`} key={text(step.step_id)}>
            <span>{text(step.label)}</span>
            <b>{text(step.phase)}</b>
            <code>{text(step.agent_display_name)}</code>
          </article>
        ))}
      </div>
      <div className="ion-agent-chain-footer">
        <Metric label="active process" value={model.chain?.active_process_running ? 'yes' : 'no'} />
        <Metric label="return path" value={model.chain?.return_path} />
        <Metric label="carrier" value={model.chain?.single_carrier_sequential ? 'sequential' : 'unknown'} />
      </div>
    </section>
  );
}

function AgentsView({
  agents,
  selectedAgent,
  setSelectedAgentId,
}: {
  agents: Array<Record<string, unknown>>;
  selectedAgent: Record<string, unknown>;
  setSelectedAgentId: (id: string) => void;
}) {
  return (
    <section className="ion-agent-grid-view">
      <div className="ion-agent-card-grid">
        {agents.map((agent) => (
          <button
            className={text(selectedAgent.role_id) === text(agent.role_id) ? 'is-active' : undefined}
            key={text(agent.role_id || agent.agent_id)}
            onClick={() => setSelectedAgentId(text(agent.role_id || agent.agent_id))}
            type="button"
          >
            <b>{text(agent.display_name || agent.role_id)}</b>
            <span>{text(agent.context_system_status, 'unknown')} / {truth(agent.invocable) ? 'invocable' : 'context'}</span>
            <code>{text(agent.context_system_card, 'no card')}</code>
          </button>
        ))}
      </div>
      <AgentCard agent={selectedAgent} />
    </section>
  );
}

function DomainWeaverOpsView({
  domainWeaver,
  runtime,
  domains,
}: {
  domainWeaver: Record<string, unknown>;
  runtime: IonCockpitViewModel;
  domains: Array<Record<string, unknown>>;
}) {
  const summary = record(domainWeaver.summary);
  const operatingLoop = record(domainWeaver.operating_loop);
  const loopSummary = record(operatingLoop.summary);
  const promotionReview = record(domainWeaver.promotion_review);
  const promotionSummary = record(promotionReview.summary);
  const promotionGate = record(domainWeaver.promotion_gate);
  const promotionGateSummary = record(promotionGate.summary);
  const queueGovernance = record(domainWeaver.queue_governance);
  const queueSummary = record(queueGovernance.summary);
  const loopSteps = records(operatingLoop.loop);
  const blockers = records(operatingLoop.blockers);
  const nextPackets = records(operatingLoop.next_packets);
  const queuePackets = records(queueGovernance.next_packets);
  const queueFindings = records(queueGovernance.findings);
  const flaggedRequests = records(queueGovernance.flagged_requests);
  const receipts = records(runtime.receipts).filter((receipt) => text(receipt.path).includes('domain_weaver')).slice(0, 8);
  const decisions = records(promotionReview.decisions);
  const cleanDecisions = records(promotionGate.decisions).filter((decision) => truth(decision.clean));
  const comms = record(runtime.joc_comms?.summary);
  const status = text(operatingLoop.status || domainWeaver.weave_status, 'projection missing');
  const ready = status.includes('ready') || status.includes('clean') || status.includes('usable');
  return (
    <section className="ion-agent-grid-view" aria-label="Domain Weaver operating loop">
      <div className="ion-agent-roster-summary">
        <div>
          <div className="ion-section-title">DOMAIN WEAVER OPERATING LOOP</div>
          <b>{status}</b>
          <p>Reads context, classifies domains, routes next packets, validates, visualizes proof, and never claims accepted state.</p>
        </div>
        <Metric label="domains" value={`${text(summary.covered_domain_count, '0')}/${text(summary.domain_count, String(domains.length))}`} />
        <Metric label="agents" value={summary.agent_count} />
        <Metric label="edges" value={summary.edge_count} />
        <Metric label="gaps" value={summary.gap_count} />
        <Metric label="gate" value={`${text(promotionGateSummary.clean_count, '0')}/${text(promotionGateSummary.candidate_domain_count, '0')}`} />
        <Metric label="next" value={loopSummary.next_packet_count ?? nextPackets.length} />
        <Metric label="queue" value={text(queueSummary.request_count, '0')} />
        <Metric label="comms" value={`${text(comms.channel_count, '0')}/${text(comms.message_count, '0')}`} />
      </div>

      <section className="ion-agent-work-card">
        <div className={`ion-runtime-verdict is-${ready ? 'ready' : 'blocked'}`}>
          {ready ? 'DOGFOOD LOOP VISIBLE' : 'DOGFOOD LOOP NEEDS ATTENTION'}
        </div>
        <div className="ion-agent-metric-row">
          <Metric label="ready agents" value={loopSummary.ready_agent_count} />
          <Metric label="covered domains" value={loopSummary.covered_domain_count} />
          <Metric label="drafts" value={promotionSummary.ready_for_registry_draft_count} />
          <Metric label="blockers" value={loopSummary.blocker_count ?? blockers.length} />
        </div>
        <Path label="projection" value={text(domainWeaver.projection_path)} />
        <Path label="promotion review" value={text(promotionReview.review_path)} />
        <Path label="promotion gate" value={text(promotionGate.gate_path)} />
        <Path label="receipt dir" value={text(domainWeaver.receipt_dir)} />
        <List label="blockers" values={blockers.map((blocker) => `${text(blocker.code)} ${text(blocker.count || blocker.clean_count || '')}`).slice(0, 8)} />
      </section>

      <section className="ion-agent-work-card">
        <div className="ion-section-title">QUEUE GOVERNANCE</div>
        <div className="ion-agent-metric-row">
          <Metric label="status" value={text(queueGovernance.status, 'missing')} />
          <Metric label="waiting" value={queueSummary.waiting_request_count} />
          <Metric label="stale" value={queueSummary.stale_waiting_request_count} />
          <Metric label="repair" value={queueSummary.terminal_repair_request_count} />
        </div>
        <Path label="queue" value={text(queueGovernance.queue_path)} />
        <Path label="runner state" value={text(queueGovernance.runner_state_path)} />
        <List label="findings" values={queueFindings.map((finding) => `${text(finding.code)} ${text(finding.count || '')}`).slice(0, 8)} />
        <List label="flagged requests" values={flaggedRequests.map((request) => `${text(request.status)} / ${text(request.lane_id)} / ${text(request.path)}`).slice(0, 6)} />
        <List label="queue packets" values={queuePackets.map((packet) => `${text(packet.packet_id)} / ${text(packet.lane_id)}`).slice(0, 6)} />
      </section>

      <section className="ion-agent-work-card">
        <div className="ion-section-title">SELF-DOGFOOD STEPS</div>
        <div className="ion-agent-history-view">
          {loopSteps.map((step) => (
            <article className="ion-agent-history-row" key={text(step.step)}>
              <b>{text(step.step)}</b>
              <span>{text(step.label)}</span>
              <code>{text(step.proof_surface)}</code>
            </article>
          ))}
          {loopSteps.length === 0 ? <div className="ion-empty-state">OPERATING LOOP NOT MATERIALIZED</div> : null}
        </div>
      </section>

      <section className="ion-agent-work-card">
        <div className="ion-section-title">NEXT BOUNDED PACKETS</div>
        <div className="ion-agent-run-list">
          {nextPackets.map((packet) => (
            <article className="ion-agent-run-row" key={text(packet.packet_id)}>
              <b>{text(packet.packet_id)}</b>
              <span>{text(packet.lane_id)} / {text(packet.work_class)}</span>
              <code>{text(packet.objective)}</code>
            </article>
          ))}
          {nextPackets.length === 0 ? <div className="ion-empty-state">NO NEXT PACKETS DECLARED</div> : null}
        </div>
      </section>

      <section className="ion-agent-work-card">
        <div className="ion-section-title">PROMOTION / RECEIPT PROOF</div>
        <div className="ion-agent-metric-row">
          <Metric label="decisions" value={decisions.length} />
          <Metric label="clean" value={cleanDecisions.length} />
          <Metric label="receipts" value={receipts.length} />
        </div>
        <List
          label="clean decisions"
          values={cleanDecisions.map((decision) => `${text(decision.candidate_domain_id)} -> ${text(decision.proposed_active_registry_target)}`).slice(0, 8)}
        />
        <List label="recent receipts" values={receipts.map((receipt) => text(receipt.path)).filter(Boolean)} />
      </section>

      <JsonView title="DOMAIN WEAVER OPERATING LOOP RAW" value={operatingLoop} />
    </section>
  );
}

function DomainsView({
  domainWeaver,
  domains,
  selectedDomain,
  setSelectedDomainId,
}: {
  domainWeaver: Record<string, unknown>;
  domains: Array<Record<string, unknown>>;
  selectedDomain: Record<string, unknown>;
  setSelectedDomainId: (id: string) => void;
}) {
  const summary = record(domainWeaver.summary);
  const weaverDomains = records(domainWeaver.domains);
  const selectedWeave = weaverDomains.find((domain) => text(domain.domain_id) === text(selectedDomain.domain_id)) ?? {};
  const selectedGaps = records(domainWeaver.gaps).filter((gap) => text(gap.scope) === 'domain' && text(gap.id) === text(selectedDomain.domain_id));
  const capsuleExports = record(domainWeaver.capsule_exports);
  const mountContexts = records(capsuleExports.mount_contexts);
  const promotionReview = record(domainWeaver.promotion_review);
  const promotionSummary = record(promotionReview.summary);
  const promotionGate = record(domainWeaver.promotion_gate);
  const promotionGateSummary = record(promotionGate.summary);
  const selectedPromotionDecision = records(promotionReview.decisions).find((decision) => text(decision.candidate_domain_id) === text(selectedDomain.domain_id)) ?? {};
  const selectedGateDecision = records(promotionGate.decisions).find((decision) => text(decision.candidate_domain_id) === text(selectedDomain.domain_id)) ?? {};
  return (
    <section className="ion-agent-grid-view">
      <div className="ion-agent-roster-summary">
        <div>
          <div className="ion-section-title">DOMAIN WEAVER</div>
          <b>{text(domainWeaver.weave_status, 'projection missing')}</b>
        </div>
        <Metric label="covered" value={`${text(summary.covered_domain_count, text(summary.usable_domain_count, '0'))}/${text(summary.domain_count, String(domains.length))}`} />
        <Metric label="usable" value={`${text(summary.usable_domain_count, '0')}/${text(summary.active_domain_count, '0')}`} />
        <Metric label="candidate" value={`${text(summary.candidate_covered_domain_count, '0')}/${text(summary.candidate_domain_count, '0')}`} />
        <Metric label="agents" value={summary.agent_count} />
        <Metric label="capsules" value={summary.capsule_agent_count} />
        <Metric label="drafts" value={promotionSummary.ready_for_registry_draft_count} />
        <Metric label="gate" value={`${text(promotionGateSummary.clean_count, '0')}/${text(promotionGateSummary.candidate_domain_count, '0')}`} />
        <Metric label="edges" value={summary.edge_count} />
        <Metric label="gaps" value={summary.gap_count} />
      </div>
      <div className="ion-domain-card-grid">
        {domains.map((domain) => (
          <button
            className={text(selectedDomain.domain_id) === text(domain.domain_id) ? 'is-active' : undefined}
            key={text(domain.domain_id)}
            onClick={() => setSelectedDomainId(text(domain.domain_id))}
            type="button"
          >
            <b>{text(domain.domain_id)}</b>
            <span>{text(weaverDomains.find((row) => text(row.domain_id) === text(domain.domain_id))?.status || domain.fact_posture)} / {text(domain.maturity_estimate)}</span>
            <code>{text(first(recordsToStrings(domain.paths)), 'no path')}</code>
          </button>
        ))}
      </div>
      <div className="ion-agent-work-card">
        <div className="ion-section-title">WEAVE DETAIL</div>
        <h2>{text(selectedDomain.display_name || selectedDomain.domain_id)}</h2>
        <div className="ion-agent-metric-row">
          <Metric label="status" value={selectedWeave.status} />
          <Metric label="agents" value={selectedWeave.agent_count} />
          <Metric label="coverage" value={selectedWeave.candidate_coverage_count} />
          <Metric label="capsules" value={selectedWeave.capsule_agent_count} />
          <Metric label="mounts" value={selectedWeave.materialized_mount_count} />
          <Metric label="comms" value={selectedWeave.communication_agent_count} />
        </div>
        <Path label="projection" value={text(domainWeaver.projection_path)} />
        <Path label="shared comms" value={text(domainWeaver.shared_comms_directory_path)} />
        <Path label="promotion review" value={text(promotionReview.review_path)} />
        <Path label="promotion gate" value={text(promotionGate.gate_path)} />
        {Object.keys(selectedPromotionDecision).length ? (
          <>
            <Path label="proposed active id" value={text(selectedPromotionDecision.proposed_active_domain_id)} />
            <Path label="draft path" value={text(selectedPromotionDecision.candidate_draft_path)} />
            <List label="promotion blockers" values={recordsToStrings(selectedPromotionDecision.blockers)} />
          </>
        ) : null}
        {Object.keys(selectedGateDecision).length ? (
          <>
            <div className={`ion-runtime-verdict is-${truth(selectedGateDecision.clean) ? 'ready' : 'blocked'}`}>
              promotion gate / {text(selectedGateDecision.gate_state)}
            </div>
            <Path label="gate target" value={text(selectedGateDecision.proposed_active_registry_target)} />
            <List label="gate blockers" values={recordsToStrings(selectedGateDecision.blockers)} />
            <List
              label="gate checks"
              values={records(selectedGateDecision.checks)
                .map((check) => `${text(check.check_id)} / ${truth(check.ok) ? 'pass' : 'fail'}`)
                .slice(0, 10)}
            />
          </>
        ) : null}
        <List label="domain gaps" values={selectedGaps.map((gap) => text(gap.gap)).filter(Boolean)} />
        <List
          label="candidate coverage"
          values={records(selectedWeave.candidate_coverage_roles)
            .map((item) => `${text(item.role_id)} / ${text(item.mount_domain)}`)
            .slice(0, 6)}
        />
        <List
          label="capsule exports"
          values={mountContexts
            .filter((item) => text(item.domain_id) === text(selectedDomain.domain_id))
            .map((item) => `${text(item.agent_role_id)} -> ${text(item.portable_context_manifest_path)}`)
            .slice(0, 6)}
        />
      </div>
      <DomainCard domain={selectedDomain} />
    </section>
  );
}

function RunsView({
  model,
  requestState,
  selectedAgent,
}: {
  model: IonAgentControlPlane;
  requestState: Record<string, unknown> | null;
  selectedAgent?: Record<string, unknown>;
}) {
  const allRuns = records(model.runs?.recent_invocations);
  const runs = selectedAgent ? allRuns.filter((run) => agentMatchesRecord(run, selectedAgent)) : allRuns;
  return (
    <section className="ion-agent-runs-view">
      <div className="ion-agent-run-list">
        {runs.map((run) => (
          <article className="ion-agent-run-row" key={text(run.invocation_id || run.path)}>
            <b>{text(run.agent_display_name || run.agent_role_id)}</b>
            <span>{text(run.status)} / {text(run.codex_work_request_status)}</span>
            <code>{text(run.invocation_id)}</code>
          </article>
        ))}
        {runs.length === 0 ? <div className="ion-empty-state">NO AGENT RUNS</div> : null}
      </div>
      <JsonView title="LATEST REQUEST" value={requestState ?? model.runs?.latest_state ?? {}} />
    </section>
  );
}

function MountsView({ mounts, selectedAgent }: { mounts: Array<Record<string, unknown>>; selectedAgent: Record<string, unknown> }) {
  const selectedRole = text(selectedAgent.role_id);
  const selectedMount = mounts.find((mount) => text(mount.agent_role_id) === selectedRole) ?? coalesceRecord(selectedAgent.native_codex_mount, mounts[0]);
  return (
    <section className="ion-agent-grid-view">
      <div className="ion-mount-card-grid">
        {mounts.map((mount) => (
          <article className={text(mount.agent_role_id) === selectedRole ? 'is-active' : undefined} key={text(mount.mount_id)}>
            <b>{text(mount.agent_display_name)}</b>
            <span>{text(mount.domain_id)} / {truth(mount.materialized) ? 'materialized' : 'planned'}</span>
            <code>{text(mount.mount_path)}</code>
          </article>
        ))}
      </div>
      <MountCard mount={selectedMount} />
    </section>
  );
}

function HistoryView({ model }: { model: IonAgentControlPlane }) {
  const runs = records(model.runs?.recent_invocations);
  return (
    <section className="ion-agent-history-view">
      {runs.map((run) => (
        <article className="ion-agent-history-row" key={text(run.invocation_id || run.path)}>
          <time>{text(run.created_at || run.updated_at)}</time>
          <b>{text(run.agent_display_name || run.agent_role_id)}</b>
          <span>{text(run.status)}</span>
          <code>{text(run.codex_work_request_path || run.path)}</code>
        </article>
      ))}
      {runs.length === 0 ? <div className="ion-empty-state">NO HISTORY</div> : null}
    </section>
  );
}

function InvocationWorkPanel({
  model,
  requestState,
  selectedAgent,
}: {
  model: IonAgentControlPlane;
  requestState: Record<string, unknown> | null;
  selectedAgent: Record<string, unknown>;
}) {
  const [tab, setTab] = useState<WorkTabId>('assistant');
  const activeRun = record(model.runs?.active_run);
  const latestRun = records(model.runs?.recent_invocations)[0] ?? {};
  const source = requestState ?? activeRun ?? latestRun ?? {};
  const mount = coalesceRecord(source.codex_agent_mount, selectedAgent.native_codex_mount);
  return (
    <section className="ion-agent-work-card">
      <div className="ion-agent-work-tabs">
        {workTabs.map((item) => (
          <button className={tab === item.id ? 'is-active' : undefined} key={item.id} onClick={() => setTab(item.id)} type="button">
            {item.label}
          </button>
        ))}
      </div>
      {tab === 'assistant' && <SummaryPanel source={source} selectedAgent={selectedAgent} />}
      {tab === 'tools' && <JsonView title="TOOLS / CODEX" value={model.runs?.live_worker_telemetry ?? source} />}
      {tab === 'context' && <JsonView title="CONTEXT" value={{ agent: selectedAgent, mount, source_model: model.source_model }} />}
      {tab === 'mount' && <JsonView title="CODEX NATIVE MOUNT" value={mount} />}
      {tab === 'edits' && <JsonView title="EDITS / DIFF" value={{ planned_writes: source.planned_writes, latest_return_packet_path: source.latest_return_packet_path }} />}
      {tab === 'agents' && <JsonView title="AGENT" value={selectedAgent} />}
      {tab === 'events' && <JsonView title="EVENTS" value={record(model.runs?.live_worker_telemetry).latest_worker_lifecycle_event ?? model.runs} />}
      {tab === 'receipts' && <JsonView title="RECEIPTS" value={{ receipt_paths: source.receipt_paths, task_return: source.latest_return_packet_path }} />}
      {tab === 'raw' && <JsonView title="RAW" value={source} />}
    </section>
  );
}

function SummaryPanel({ source, selectedAgent }: { source: Record<string, unknown>; selectedAgent: Record<string, unknown> }) {
  const mount = coalesceRecord(source.codex_agent_mount, selectedAgent.native_codex_mount);
  return (
    <div className="ion-agent-summary-panel">
      <div className="ion-section-title">CURRENT WORK</div>
      <h2>{text(selectedAgent.display_name || selectedAgent.role_id)}</h2>
      <p>{text(source.result || source.status || source.finding || 'No active request selected.')}</p>
      <div className="ion-path-list">
        <Path label="invocation" value={text(source.invocation_path || source.path || source.invocation_id)} />
        <Path label="work request" value={text(source.codex_work_request_path)} />
        <Path label="codex mount" value={text(mount.mount_path)} />
        <Path label="return" value={text(source.latest_return_packet_path)} />
      </div>
    </div>
  );
}

function AgentCard({ agent, compact = false }: { agent: Record<string, unknown>; compact?: boolean }) {
  return (
    <article className={`ion-agent-detail-card ${compact ? 'is-compact' : ''}`}>
      <div className="ion-section-title">AGENT DETAIL</div>
      <h2>{text(agent.display_name || agent.role_id, 'NO AGENT')}</h2>
      <div className="ion-agent-detail-metrics">
        <Metric label="role" value={agent.role_id} />
        <Metric label="status" value={agent.context_system_status} />
        <Metric label="write" value={agent.write_posture ?? 'none'} />
        <Metric label="invocable" value={truth(agent.invocable) ? 'yes' : 'no'} />
      </div>
      {!compact ? (
        <>
          <p>{text(agent.package_strategy)}</p>
          <Path label="card" value={text(agent.context_system_card)} />
          <Path label="class" value={text(agent.default_active_package_class)} />
          <Path label="codex mount" value={text(record(agent.native_codex_mount).mount_path)} />
          <List label="templates" values={recordsToStrings(agent.primary_templates).slice(0, 5)} />
          <List label="missing witness refs" values={recordsToStrings(agent.missing_legacy_context_paths).slice(0, 5)} />
        </>
      ) : null}
    </article>
  );
}

function MountCard({ mount }: { mount: Record<string, unknown> }) {
  return (
    <article className="ion-agent-detail-card">
      <div className="ion-section-title">CODEX NATIVE MOUNT</div>
      <h2>{text(mount.mount_id, 'NO MOUNT')}</h2>
      <p>{text(mount.hook_strategy)}</p>
      <div className="ion-agent-detail-metrics">
        <Metric label="agent" value={mount.agent_display_name} />
        <Metric label="domain" value={mount.domain_id} />
        <Metric label="state" value={truth(mount.materialized) ? 'materialized' : 'planned'} />
      </div>
      <Path label="cwd" value={text(mount.mount_path)} />
      <Path label="manifest" value={text(mount.manifest_path)} />
      <Path label="config" value={text(mount.config_path)} />
      <List label="context refs" values={recordsToStrings(mount.context_refs).slice(0, 6)} />
    </article>
  );
}

function DomainCard({ domain }: { domain: Record<string, unknown> }) {
  return (
    <article className="ion-agent-detail-card">
      <div className="ion-section-title">DOMAIN DETAIL</div>
      <h2>{text(domain.domain_id, 'NO DOMAIN')}</h2>
      <p>{text(domain.purpose)}</p>
      <div className="ion-agent-detail-metrics">
        <Metric label="posture" value={domain.fact_posture} />
        <Metric label="maturity" value={domain.maturity_estimate} />
        <Metric label="steward" value={domain.suggested_steward_class} />
        <Metric label="split review" value={truth(domain.requires_split_merge_review) ? 'yes' : 'no'} />
      </div>
      <List label="paths" values={recordsToStrings(domain.paths).slice(0, 4)} />
      <List label="read first" values={recordsToStrings(domain.local_read_first_files).slice(0, 5)} />
      <List label="blockers" values={recordsToStrings(domain.blockers).slice(0, 5)} />
    </article>
  );
}

function TimelineRow({ event, compact = false }: { event: Record<string, unknown>; compact?: boolean }) {
  return (
    <article className={`ion-agent-comms-row is-${text(event.kind, 'event')} ${compact ? 'is-compact' : ''}`}>
      <span>{text(event.kind || event.event_type, 'event')}</span>
      <b>{text(event.status || event.event || event.question_type || event.receipt_id, 'record')}</b>
      <p>{text(event.question || event.agent_display_name || event.from_agent || event.to || event.invocation_id || event.summary)}</p>
      <code>{text(event.path || event.codex_work_request_path || event.receipt_path)}</code>
    </article>
  );
}

function JsonView({ title, value }: { title: string; value: unknown }) {
  return (
    <section className="ion-agent-json-panel">
      <div className="ion-section-title">{title}</div>
      <pre>{JSON.stringify(value ?? {}, null, 2)}</pre>
    </section>
  );
}

function Metric({ label, value }: { label: string; value: unknown }) {
  return (
    <div className="ion-agent-metric">
      <span>{label}</span>
      <b>{text(value, '0')}</b>
    </div>
  );
}

function AgentCommsPill({ label, value }: { label: string; value: unknown }) {
  return (
    <div className="ion-codex-context-pill">
      <small>{label}</small>
      <b>{text(value, '0')}</b>
    </div>
  );
}

function runUsageText(run: Record<string, unknown>) {
  const usage = record(run.usage);
  const limits = record(run.limits);
  return `${text(usage.processed_directive_count, '0')}/${text(limits.max_directives, '0')} directives`;
}

function runOperationalText(run: Record<string, unknown>) {
  const workItems = records(run.work_items);
  const workpackCount = text(run.workpack_count, String(workItems.length || recordsToStrings(run.workpack_paths).length));
  const state = text(run.operational_state, 'no_operational_evidence').replaceAll('_', ' ');
  return `${state} / work ${workpackCount} / returns ${text(run.task_return_count, '0')} / replies ${text(run.agent_response_count, '0')}`;
}

function runCompletionState(run: Record<string, unknown>) {
  return text(record(run.completion_state).state);
}

function runHasActiveWorker(run: Record<string, unknown>) {
  const runtime = record(run.worker_runtime);
  const latestWorker = record(runtime.latest_worker || run.latest_worker);
  return truth(runtime.has_active_worker) || text(latestWorker.status) === 'running';
}

function runIsActionable(run: Record<string, unknown>) {
  if (text(run.status) !== 'active') return false;
  const state = runCompletionState(run);
  return ['worker_running', 'awaiting_return', 'ready_to_start_worker', 'pending_directive', 'workpack_active'].includes(state);
}

function runProofLabel(run: Record<string, unknown>) {
  const state = text(run.operational_state, 'no_operational_evidence');
  if (state === 'response_observed') return 'real response observed';
  if (state === 'workpack_active') return 'workpack active';
  if (state === 'messages_delivered') return 'messages delivered';
  if (state === 'blocked_by_policy' || text(run.status).includes('blocked')) return 'blocked by policy';
  return state.replaceAll('_', ' ');
}

function runFollowupDecision(run: Record<string, unknown>) {
  return record(run.followup_decision || record(run.completion_state).followup_decision);
}

function runFollowupDecisionText(run: Record<string, unknown>) {
  const followup = runFollowupDecision(run);
  const state = text(followup.state, 'decision unknown');
  if (state === 'followup_directive_observed') return 'follow-up directive observed';
  if (state === 'no_followup_declared') return 'no follow-up declared';
  if (state === 'terminal_decision_missing') return 'terminal decision missing';
  if (state === 'call_agent_missing_directive') return 'call requested without directive';
  if (state === 'waiting_return') return 'decision waiting return';
  if (state === 'decision_missing') return 'decision missing';
  if (state === 'not_applicable') return 'decision n/a';
  return state.replaceAll('_', ' ');
}

function runWorkItemDecisionText(item: Record<string, unknown>) {
  const decision = record(item.followup_decision);
  const state = text(decision.state, 'decision_missing');
  if (state === 'followup_directive') return 'calls agent';
  if (state === 'no_followup') return 'no follow-up';
  if (state === 'call_agent_missing_directive') return 'call missing directive';
  if (state === 'waiting_return') return 'decision waiting';
  if (state === 'decision_missing') return 'decision missing';
  return state.replaceAll('_', ' ');
}

function runWorkerState(run: Record<string, unknown>) {
  const runtime = record(run.worker_runtime);
  const latestWorker = record(runtime.latest_worker || run.latest_worker);
  if (truth(runtime.has_active_worker) || text(latestWorker.status) === 'running') return 'running';
  const state = text(latestWorker.status);
  if (state) return state.replaceAll('_', ' ');
  if (Number(runtime.worker_count || 0) > 0) return 'not running';
  return 'not started';
}

function runWorkerValue(run: Record<string, unknown>) {
  const runtime = record(run.worker_runtime);
  const latestWorker = record(runtime.latest_worker || run.latest_worker);
  const pid = text(latestWorker.pid);
  const agent = displayRole(text(latestWorker.agent_role_id || latestWorker.agent_display_name, 'agent'));
  if (pid) return `pid ${pid} / ${agent}`;
  return text(latestWorker.run_packet_path || latestWorker.workpack_path);
}

function runWorkerText(run: Record<string, unknown>) {
  const state = runWorkerState(run);
  const value = runWorkerValue(run);
  return value ? `worker ${state} / ${value}` : `worker ${state}`;
}

function runWorkpackPath(run: Record<string, unknown>) {
  const workItems = records(run.work_items);
  const openWorkItem = workItems.find((item) => {
    const state = text(item.response_state);
    return text(item.workpack_path) && state !== 'returned' && !text(item.latest_return_packet_path);
  });
  return text(openWorkItem?.workpack_path || workItems[0]?.workpack_path || first(recordsToStrings(run.workpack_paths)));
}

function canStartRunWorker(run: Record<string, unknown>) {
  const status = text(run.status);
  const workItems = records(run.work_items);
  const openWorkItem = workItems.find((item) => {
    const state = text(item.response_state);
    return text(item.workpack_path) && state !== 'returned' && !text(item.latest_return_packet_path);
  });
  return Boolean(text(run.run_id) && (openWorkItem || (!workItems.length && runWorkpackPath(run))) && !status.includes('blocked'));
}

function runLatestReturnPath(run: Record<string, unknown>) {
  const returnMessagePaths = record(run.return_message_paths);
  const returnPaths = Object.keys(returnMessagePaths).map((item) => text(item)).filter(Boolean);
  return text(run.latest_return_packet_path || first(returnPaths));
}

function runLatestReplyPath(run: Record<string, unknown>) {
  const returnMessagePaths = record(run.return_message_paths);
  const replyPaths = Object.values(returnMessagePaths).map((item) => text(item)).filter(Boolean);
  return text(first(replyPaths) || record(run.latest_agent_message).message_path);
}

function runPolicyText(run: Record<string, unknown>) {
  return text(record(run.policy_gate).state, 'policy unknown').replaceAll('_', ' ');
}

function compactGraphId(value: string) {
  const clean = text(value).replace(/^(run|thread|message|workpack|return):/, '');
  return clean.length > 18 ? `${clean.slice(0, 15)}...` : clean;
}

function displayRole(value: string) {
  return text(value, 'agent').replace(/^role\./, '').replaceAll('_', ' ');
}

function shortPath(value: string) {
  const clean = text(value);
  if (!clean) return 'missing';
  const parts = clean.split('/').filter(Boolean);
  return parts.slice(-3).join('/');
}

function mentionAliasFromRole(value: string) {
  const role = text(value).replace(/^role\./, '');
  return role.toLowerCase().replace(/[^a-z0-9_.-]+/g, '_').replace(/^[_\-.]+|[_\-.]+$/g, '') || 'agent';
}

function mentionAliasForAgent(agent: Record<string, unknown>) {
  const roleAlias = mentionAliasFromRole(text(agent.role_id || agent.agent_id));
  if (roleAlias !== 'agent') return roleAlias;
  return mentionAliasFromRole(text(agent.display_name || agent.role_id || agent.agent_id));
}

function mergeAgentHomeViews(
  primary: Array<Record<string, unknown>>,
  secondary: Array<Record<string, unknown>>,
): Array<Record<string, unknown>> {
  const merged = [...primary];
  const seenRoles = new Set(primary.map((item) => text(item.role_id)).filter(Boolean));
  for (const row of secondary) {
    const roleId = text(row.role_id);
    if (!roleId || seenRoles.has(roleId)) continue;
    merged.push(row);
    seenRoles.add(roleId);
  }
  return merged;
}

function selectAgentHomeView(
  homeViews: Array<Record<string, unknown>>,
  roleId: string,
): Record<string, unknown> {
  const targetRole = text(roleId);
  if (!targetRole) return homeViews[0] ?? {};
  const exact = homeViews.find((row) => text(row.role_id) === targetRole);
  if (exact) return exact;
  const roleAlias = mentionAliasFromRole(targetRole);
  return homeViews.find((row) => mentionAliasFromRole(text(row.role_id)) === roleAlias) ?? homeViews[0] ?? {};
}

function CompactHomeProjectionCard({
  homeView,
  compact = false,
}: {
  homeView: Record<string, unknown>;
  compact?: boolean;
}) {
  if (!Object.keys(homeView).length) {
    return <div className="ion-empty-state">NO COMPACT HOME PROJECTION</div>;
  }
  const scout = record(homeView.scout_context_card);
  const loop = record(homeView.self_improvement_loop);
  const loopCounts = record(loop.counts);
  const compactDefaults = record(scout.compact_defaults);
  const readOrder = records(scout.context_read_order);
  const loopItems = records(loop.items);
  const forbidden = recordsToStrings(
    scout.forbidden_default_surfaces
      || record(homeView.source_surfaces).not_used_for_orientation,
  );
  const files = recordsToStrings(record(homeView.source_surfaces).files);
  const itemsToShow = compact ? loopItems.slice(0, 3) : loopItems.slice(0, 6);
  return (
    <div className="ion-agent-list">
      <code>{text(homeView.role_id, 'role unknown')} / {text(homeView.updated_at, 'no timestamp')}</code>
      <code>{text(scout.schema_id, 'scout missing')} / {text(loop.schema_id, 'loop missing')}</code>
      <code>scan caps: inbox {text(compactDefaults.inbox_scan_cap, 'n/a')} / thread {text(compactDefaults.thread_scan_cap, 'n/a')} / carrier {text(compactDefaults.carrier_queue_scan_cap, 'n/a')}</code>
      <code>work items: {text(loopCounts.total, '0')} total / blockers {text(loopCounts.blockers, '0')} / follow-ups {text(loopCounts.follow_ups, '0')}</code>
      {readOrder.map((row) => (
        <code key={`${text(row.step)}-${text(row.surface)}`}>
          read {text(row.step, '?')}: {shortPath(text(row.surface))} (cap {text(row.scan_cap, '?')})
        </code>
      ))}
      {itemsToShow.map((item) => (
        <code key={text(item.work_item_id, text(item.summary))}>
          [{text(item.kind, 'item')}] {text(item.summary, 'work item')} / {text(item.suggested_action, 'no action')}
        </code>
      ))}
      {forbidden.slice(0, 4).map((surface) => <code key={surface}>forbidden default surface: {shortPath(surface)}</code>)}
      {!compact && files.slice(0, 6).map((surface) => <code key={surface}>source: {shortPath(surface)}</code>)}
      {itemsToShow.length === 0 ? <code>no loop items</code> : null}
    </div>
  );
}

function roleInitials(value: string) {
  const normalized = displayRole(value);
  const words = normalized.split(/[^a-zA-Z0-9]+/).filter(Boolean);
  return (words.length ? words.map((word) => word[0]).join('') : normalized.slice(0, 2)).slice(0, 3).toUpperCase();
}

function Path({ label, value }: { label: string; value?: string }) {
  return <div className="ion-path-row"><span>{label}</span><code>{value || 'missing'}</code></div>;
}

function List({ label, values }: { label: string; values: string[] }) {
  return (
    <div className="ion-agent-list">
      <span>{label}</span>
      {values.length ? values.map((value) => <code key={value}>{value}</code>) : <code>none</code>}
    </div>
  );
}

function records(value: unknown): Array<Record<string, unknown>> {
  return Array.isArray(value) ? value.filter((item): item is Record<string, unknown> => Boolean(item) && typeof item === 'object' && !Array.isArray(item)) : [];
}

function record(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' && !Array.isArray(value) ? value as Record<string, unknown> : {};
}

function coalesceRecord(...values: unknown[]): Record<string, unknown> {
  for (const value of values) {
    const row = record(value);
    if (Object.keys(row).length) return row;
  }
  return {};
}

function recordsToStrings(value: unknown): string[] {
  return Array.isArray(value) ? value.map((item) => text(item)).filter(Boolean) : [];
}

function first(values: string[]): string {
  return values[0] ?? '';
}

function rowByLabel(rows: Array<Record<string, unknown>>, label: string): Record<string, unknown> {
  return rows.find((row) => text(row.label) === label) ?? {};
}

function agentMatchesRecord(item: Record<string, unknown>, agent: Record<string, unknown>): boolean {
  const role = text(agent.role_id || agent.agent_id);
  const name = text(agent.display_name || agent.role_id);
  if (!role && !name) return false;
  const candidates = [
    item.agent_role_id,
    item.role_id,
    item.agent_id,
    item.from_agent,
    item.from_role,
    item.to,
    item.answered_by,
    record(item.work_panel).from_role,
    ...recordsToStrings(item.to_roles),
    ...recordsToStrings(item.cc_roles),
    ...recordsToStrings(item.participants),
    ...recordsToStrings(record(item.work_panel).to_roles),
  ].map((value) => text(value));
  return candidates.some((value) => value === role || value === name);
}

function slug(value: string): string {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_+|_+$/g, '') || 'unknown';
}

function truth(value: unknown): boolean {
  return value === true || value === 'true' || value === 1;
}

function text(value: unknown, fallback = ''): string {
  if (value === undefined || value === null || value === '') return fallback;
  if (typeof value === 'string') return value;
  if (typeof value === 'number' || typeof value === 'boolean') return String(value);
  return fallback || JSON.stringify(value);
}
