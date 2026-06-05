import { useState } from 'react';
import type { IonCockpitViewModel } from './ionRuntimeCockpitTypes';

type TabId = 'companion' | 'extension' | 'perception' | 'browser-gpt' | 'authority';

const tabs: Array<{ id: TabId; label: string }> = [
  { id: 'companion', label: 'companion' },
  { id: 'extension', label: 'extension' },
  { id: 'perception', label: 'perception' },
  { id: 'authority', label: 'authority' },
];

export function ExtensionMicroShellPanel({ runtime }: { runtime: IonCockpitViewModel }) {
  const [activeTab, setActiveTab] = useState<TabId>('companion');
  const shell = runtime.extension_micro_shell;

  if (!shell) {
    return (
      <section className="ion-panel ion-extension-shell-panel">
        <div className="ion-section-title">DAIMON EXTENSION MICRO-SHELL</div>
        <div className="ion-empty-state">NO EXTENSION MICRO-SHELL PROJECTION FOUND</div>
      </section>
    );
  }

  const manifest = shell.manifest ?? {};
  const contract = shell.agent_lane_contract ?? {};
  const companion = shell.portable_companion ?? {};
  const perception = shell.page_perception ?? {};
  const browserGptDom = (shell.browser_gpt_dom ?? {}) as Record<string, unknown>;
  const priorDomEvidence = (browserGptDom.prior_live_dom_evidence ?? {}) as Record<string, unknown>;
  const probeIntake = (browserGptDom.probe_intake ?? {}) as Record<string, unknown>;
  const latestUsableProbe = (probeIntake.latest_usable_probe ?? {}) as Record<string, unknown>;
  const latestDegradedProbe = (probeIntake.latest_degraded_probe ?? {}) as Record<string, unknown>;
  const latestSurfaceCoverage = (
    probeIntake.latest_surface_coverage ??
    latestUsableProbe.surface_coverage ??
    latestDegradedProbe.surface_coverage ??
    {}
  ) as Record<string, unknown>;
  const effectiveSurfaceCoverage = (
    probeIntake.effective_surface_coverage ??
    latestSurfaceCoverage
  ) as Record<string, unknown>;
  const issueResolution = (probeIntake.issue_resolution ?? {}) as Record<string, unknown>;
  const issueRows = asRecords(issueResolution.rows);
  const chatgptDomTwin = (browserGptDom.chatgpt_dom_twin ?? {}) as Record<string, unknown>;
  const twinComposer = (chatgptDomTwin.composer ?? {}) as Record<string, unknown>;
  const twinSend = (chatgptDomTwin.send ?? {}) as Record<string, unknown>;
  const twinTranscript = (chatgptDomTwin.transcript ?? {}) as Record<string, unknown>;
  const twinState = (chatgptDomTwin.state ?? {}) as Record<string, unknown>;
  const twinIssueResolution = (chatgptDomTwin.issue_resolution ?? {}) as Record<string, unknown>;
  const twinControls = asRecords(chatgptDomTwin.controls);
  const twinControlById = new Map(twinControls.map((control) => [text(control.surface_id, ''), control]));
  const twinToolbarControls = [
    'new_chat_button',
    'left_sidebar_toggle',
    'model_picker',
    'thinking_mode_control',
    'tools_menu_opener',
    'file_attach_button',
    'voice_mic_button',
    'send_button',
  ]
    .map((surfaceId) => twinControlById.get(surfaceId))
    .filter((control): control is Record<string, unknown> => Boolean(control));
  const twinMenuControls = twinControls.filter((control) => ['model_menu_option', 'thinking_effort_option', 'tools_menu_option', 'file_upload_menu_option', 'left_drawer', 'drawer_surface'].includes(text(control.surface_id, '')));
  const twinMessages = asRecords(twinTranscript.messages).filter(hasReadableMessage);
  const phaseSweep = (probeIntake.phase_sweep ?? {}) as Record<string, unknown>;
  const phaseCaptureActions = asRecords(latestSurfaceCoverage.phase_capture_actions);
  const phaseSweepRows = asRecords(phaseSweep.phases);
  const priorSelectors = [
    ...Object.entries((priorDomEvidence.selectors ?? {}) as Record<string, unknown>),
    ...Object.entries((priorDomEvidence.browser_gpt_selectors ?? {}) as Record<string, unknown>),
  ]
    .map(([key, value]) => `${key}: ${text(value, '')}`)
    .filter((item) => item.trim().length > 1);
  const authority = shell.current_v1_authority ?? {};

  return (
    <section className="ion-panel ion-extension-shell-panel">
      <div className="ion-section-title">DAIMON EXTENSION MICRO-SHELL</div>
      <div className={`ion-runtime-verdict is-${statusClass(shell.status)}`}>{text(shell.status)}</div>
      <p className="ion-runtime-objective">
        Portable page companion, browser extension bridge, DOM perception, queue packs, and bounded agent lane projected as one JOC surface.
      </p>

      <div className="ion-runtime-grid">
        <Metric label="extension" value={`${text(manifest.name)} ${text(manifest.version, '')}`} />
        <Metric label="agent panels" value={String((contract.panel_surfaces as unknown[] | undefined)?.length ?? 0)} />
        <Metric label="bg messages" value={String(contract.background_message_count ?? 0)} />
        <Metric label="perception domains" value={String(perception.domain_count ?? 0)} />
        <Metric label="dom profile" value={text(browserGptDom.status)} />
        <Metric label="content scripts" value={String(manifest.content_script_count ?? 0)} />
        <Metric label="joc decision" value={text(companion.joc_decision)} />
      </div>

      <div className="ion-codex-chat-tabs" role="tablist" aria-label="Extension micro-shell tabs">
        {tabs.map((tab) => (
          <button key={tab.id} className={activeTab === tab.id ? 'is-active' : undefined} onClick={() => setActiveTab(tab.id)} type="button">
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === 'companion' && (
        <div className="ion-codex-tab-body">
          <div className="ion-runtime-card">
            <div className="ion-runtime-card-head"><span>portable thesis</span><b>{text(companion.status)}</b></div>
            <p>{text(companion.product_thesis)}</p>
          </div>
          <ChipBlock title="layout zones" items={asList(companion.layout_zones)} />
          <ChipBlock title="inherited protocols" items={asList(companion.inherited_protocols)} />
          <PathRow label="context" value={companion.path} />
          <PathRow label="extension root" value={shell.extension_root} />
        </div>
      )}

      {activeTab === 'extension' && (
        <div className="ion-codex-tab-body">
          <div className="ion-runtime-card">
            <div className="ion-runtime-card-head"><span>agent lane contract</span><b>{text(contract.status)}</b></div>
            <p>{text(contract.purpose)}</p>
          </div>
          <ChipBlock title="panel surfaces" items={asList(contract.panel_surfaces)} />
          <ChipBlock title="background messages" items={asList(contract.background_messages)} />
          <ChipBlock title="host permissions" items={asList(manifest.host_permissions)} />
          <ChipBlock title="content matches" items={asList(manifest.content_script_matches)} />
          <PathRow label="manifest" value={manifest.path} />
          <PathRow label="contract" value={contract.path} />
        </div>
      )}

      {activeTab === 'perception' && (
        <div className="ion-codex-tab-body">
          <div className="ion-extension-domain-grid">
            {asRecords(perception.domains).map((domain, index) => (
              <article className="ion-runtime-card" key={text(domain.domain_id, `domain-${index + 1}`)}>
                <div className="ion-runtime-card-head"><span>{text(domain.domain_id)}</span><b>DOM</b></div>
                <p>{text(domain.purpose)}</p>
                <code>{text(domain.safety_boundary)}</code>
              </article>
            ))}
          </div>
          <ChipBlock title="task return headings" items={asList(perception.task_return_headings)} />
          <PathRow label="domain registry" value={perception.domain_registry_path} />
          <PathRow label="task return" value={perception.task_return_path} />
        </div>
      )}

      {activeTab === 'browser-gpt' && (
        <div className="ion-codex-tab-body">
          <section className={`ion-browser-gpt-twin is-${statusClass(chatgptDomTwin.status)}`}>
            <div className="ion-browser-gpt-twin-head">
              <div>
                <span>chatgpt dom twin</span>
                <b>{text(chatgptDomTwin.status, 'missing')}</b>
              </div>
              <div className="ion-browser-gpt-twin-state">
                <span>composer {text(twinState.composer_present, 'false')}</span>
                <span>send {text(twinState.send_available, 'false')}</span>
                <span>stream {text(twinState.response_streaming, 'false')}</span>
                <span>issues {text(twinIssueResolution.blocking_issue_count, '0')}</span>
              </div>
            </div>
            <div className="ion-browser-gpt-twin-toolbar" aria-label="Mirrored ChatGPT controls">
              {twinToolbarControls.map((control) => (
                <button
                  type="button"
                  disabled
                  className={`is-${statusClass(control.state)}`}
                  key={text(control.surface_id)}
                  title={`${text(control.surface_id)} · ${text(control.selector, 'no selector')}`}
                >
                  <span>{text(control.label)}</span>
                  <b>{text(control.state)}</b>
                </button>
              ))}
            </div>
            <div className="ion-browser-gpt-twin-body">
              <section className="ion-browser-gpt-transcript">
                <div className="ion-browser-gpt-pane-head">
                  <span>conversation</span>
                  <b>{String(twinMessages.length || twinTranscript.message_count || 0)}</b>
                </div>
                {twinMessages.length > 0 ? (
                  twinMessages.slice(0, 8).map((message, index) => (
                    <article className={`ion-browser-gpt-message is-${text(message.role, 'unknown')}`} key={`${text(message.role)}-${index}`}>
                      <b>{text(message.role)}</b>
                      <p>{text(message.text_preview, '')}</p>
                    </article>
                  ))
                ) : (
                  <div className="ion-browser-gpt-empty">
                    <b>{text(twinTranscript.readability_status, 'empty transcript')}</b>
                    <code>{`raw anchors ${text(twinTranscript.raw_visible_message_count ?? twinTranscript.message_count, '0')}`}</code>
                  </div>
                )}
              </section>
              <section className="ion-browser-gpt-control-map">
                <div className="ion-browser-gpt-pane-head">
                  <span>menus and drawers</span>
                  <b>{String(twinMenuControls.length)}</b>
                </div>
                {twinMenuControls.map((control) => (
                  <div className={`ion-browser-gpt-control is-${statusClass(control.state)}`} key={text(control.surface_id)}>
                    <span>{text(control.label)}</span>
                    <b>{text(control.state)}</b>
                    <code>{text(control.selector, '')}</code>
                  </div>
                ))}
              </section>
            </div>
            <div className="ion-browser-gpt-composer">
              <div>
                <span>composer</span>
                <code>{text(twinComposer.selector, '')}</code>
              </div>
              <button type="button" disabled title="Approved send remains gated">
                <span>send</span>
                <b>{text(twinSend.state, 'missing')}</b>
              </button>
            </div>
          </section>
          <div className="ion-runtime-card">
            <div className="ion-runtime-card-head"><span>selector profile</span><b>{text(browserGptDom.verdict ?? browserGptDom.status)}</b></div>
            <p>{text(browserGptDom.recommended_action)}</p>
          </div>
          <div className="ion-runtime-grid">
            <Metric label="profiles" value={String(browserGptDom.profile_count ?? 0)} />
            <Metric label="origin" value={text(browserGptDom.origin)} />
            <Metric label="target" value={text(browserGptDom.target_url)} />
            <Metric label="failed" value={String(asList(browserGptDom.failed_required_surfaces).length)} />
            <Metric label="prior live dom" value={text(priorDomEvidence.status, 'missing')} />
            <Metric label="prior gpt dom" value={text(priorDomEvidence.browser_gpt_status, 'missing')} />
            <Metric label="probe intake" value={text(probeIntake.status)} />
            <Metric label="in-page script" value={text(probeIntake.latest_in_page_script_build_status ?? probeIntake.latest_extension_build_status, 'unknown')} />
            <Metric label="usable probe" value={text(latestUsableProbe.status)} />
            <Metric label="degraded probe" value={text(latestDegradedProbe.status)} />
            <Metric label="probe found" value={String(latestSurfaceCoverage.found_surface_count ?? 0)} />
            <Metric label="probe missing" value={String(latestSurfaceCoverage.missing_required_surface_count ?? 0)} />
            <Metric label="effective missing" value={String(effectiveSurfaceCoverage.missing_required_surface_count ?? 0)} />
            <Metric label="blocking issues" value={String(issueResolution.blocking_issue_count ?? 0)} />
            <Metric label="operator action" value={text(issueResolution.operator_action_required, 'false')} />
            <Metric label="phase captures" value={String(latestSurfaceCoverage.phase_capture_action_count ?? 0)} />
            <Metric label="sweep phases" value={String(phaseSweep.phase_count ?? 0)} />
            <Metric label="sweep found" value={String(phaseSweep.merged_found_surface_count ?? 0)} />
          </div>
          <div className="ion-runtime-card">
            <div className="ion-runtime-card-head"><span>issue resolution</span><b>{text(issueResolution.status, 'ready')}</b></div>
            <p>{`Handled ${text(issueResolution.handled_issue_count, '0')} / blocking ${text(issueResolution.blocking_issue_count, '0')} / operator action ${text(issueResolution.operator_action_required, 'false')}`}</p>
            <code>{`next ${text(issueResolution.next_action, 'continue')}`}</code>
          </div>
          {issueRows.length > 0 && (
            <div className="ion-extension-domain-grid">
              {issueRows.slice(0, 4).map((row, index) => (
                <article className="ion-runtime-card" key={text(row.finding, `issue-${index + 1}`)}>
                  <div className="ion-runtime-card-head"><span>{text(row.finding)}</span><b>{text(row.status)}</b></div>
                  <p>{text(row.detail)}</p>
                  <code>{`blocking ${text(row.blocking)} · operator ${text(row.operator_action_required)} · ${text(row.resolution)}`}</code>
                </article>
              ))}
            </div>
          )}
          <div className="ion-runtime-card">
            <div className="ion-runtime-card-head"><span>probe intake guard</span><b>{text(probeIntake.profile_preservation_guard)}</b></div>
            <p>{`Normal latest advances only on usable probe: ${text(probeIntake.normal_latest_advances_only_on_usable_probe)}`}</p>
            <p>{`Fresh probes are arriving. Unmarked means the ChatGPT page script did not include the current marker: ${text(probeIntake.expected_chatops_probe_build_marker, 'unmarked')}`}</p>
            <code>{`usable ${text(latestUsableProbe.captured_at)} · degraded ${text(latestDegradedProbe.captured_at)}`}</code>
          </div>
          <PathRow label="usable probe" value={latestUsableProbe.path} />
          <PathRow label="degraded probe" value={latestDegradedProbe.path} />
          <ChipBlock title="latest probe surfaces" items={asList(latestSurfaceCoverage.found_surface_ids)} />
          <ChipBlock title="latest probe missing required" items={asList(latestSurfaceCoverage.missing_required_surface_ids)} />
          <ChipBlock title="effective surfaces" items={asList(effectiveSurfaceCoverage.found_surface_ids)} />
          <ChipBlock title="profile backfilled surfaces" items={asList(effectiveSurfaceCoverage.profile_backfilled_surface_ids)} />
          <ChipBlock title="phase sweep merged surfaces" items={asList(phaseSweep.merged_found_surface_ids)} />
          <div className="ion-extension-domain-grid">
            {phaseCaptureActions.map((action, index) => (
              <article className="ion-runtime-card" key={text(action.surface_id, `phase-${index + 1}`)}>
                <div className="ion-runtime-card-head"><span>{text(action.surface_id)}</span><b>{text(action.phase)}</b></div>
                <p>{text(action.instruction)}</p>
                <code>{`opener ${text(action.opener_surface_id)} · found ${text(action.opener_found)}`}</code>
              </article>
            ))}
          </div>
          <div className="ion-extension-domain-grid">
            {phaseSweepRows.slice(0, 6).map((phase, index) => (
              <article className="ion-runtime-card" key={text(phase.path, `sweep-${index + 1}`)}>
                <div className="ion-runtime-card-head"><span>{text(phase.phase)}</span><b>{text(phase.status)}</b></div>
                <p>{asList(phase.found_surface_ids).map((item) => text(item)).join(', ') || 'none'}</p>
                <code>{`clicked ${text(phase.click_performed)} · controls ${text(phase.visible_control_count, '0')}`}</code>
              </article>
            ))}
          </div>
          {text(priorDomEvidence.status, '') === 'present' && (
            <>
              <div className="ion-runtime-card">
                <div className="ion-runtime-card-head"><span>prior live DOM evidence</span><b>{text(priorDomEvidence.source_kind)}</b></div>
                <p>{text(priorDomEvidence.url)}</p>
                <code>{`captured ${text(priorDomEvidence.captured_at)} · drawer ${text(priorDomEvidence.native_drawer_is_open)}`}</code>
              </div>
              <ChipBlock title="prior selectors" items={priorSelectors} />
              <PathRow label="prior snapshot" value={priorDomEvidence.source_path} />
            </>
          )}
          <div className="ion-extension-domain-grid">
            {asRecords(browserGptDom.surfaces).map((surface, index) => (
              <article className="ion-runtime-card" key={text(surface.surface_id, `surface-${index + 1}`)}>
                <div className="ion-runtime-card-head"><span>{text(surface.surface_id)}</span><b>{text(surface.health ?? surface.status)}</b></div>
                <p>{text(surface.selector)}</p>
                <code>{`confidence ${text(surface.confidence, '0')} · fallbacks ${text(surface.fallback_count, '0')}`}</code>
              </article>
            ))}
            {asRecords(browserGptDom.surfaces).length === 0 && <div className="ion-empty-state">NO DOM PROFILE RECORDED</div>}
          </div>
          <ChipBlock title="runtime commands" items={asList(browserGptDom.runtime_commands)} />
          <ChipBlock title="safety boundaries" items={asList(browserGptDom.safety_boundaries)} />
          <PathRow label="profile" value={browserGptDom.latest_profile_path} />
          <PathRow label="health" value={browserGptDom.latest_health_path} />
          <PathRow label="receipt" value={browserGptDom.latest_receipt_path} />
        </div>
      )}

      {activeTab === 'authority' && (
        <div className="ion-codex-tab-body">
          <div className="ion-queue-gateway-strip">
            <span>PRODUCTION: {shell.production_authority ? 'TRUE' : 'FALSE'}</span>
            <span>LIVE EXEC: {shell.live_execution_authority ? 'TRUE' : 'FALSE'}</span>
            <span>BROWSER CONTROL: {shell.unrestricted_browser_control ? 'TRUE' : 'FALSE'}</span>
            <span>SILENT SEND: {shell.silent_browser_send_authority ? 'TRUE' : 'FALSE'}</span>
            <span>VISIBLE GATES</span>
          </div>
          <AuthorityGrid authority={authority} />
          <ChipBlock title="safety law" items={shell.safety_law ?? []} />
          <ChipBlock title="required boundaries" items={shell.required_boundaries ?? []} />
          <ChipBlock title="non-claim boundaries" items={shell.non_claim_boundaries ?? []} />
        </div>
      )}
    </section>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="ion-runtime-metric">
      <span>{label}</span>
      <b>{value}</b>
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

function ChipBlock({ title, items }: { title: string; items: unknown[] }) {
  return (
    <div className="ion-runtime-card">
      <div className="ion-runtime-card-head"><span>{title}</span><b>{items.length}</b></div>
      <div className="ion-extension-chip-row">
        {items.map((item, index) => <span key={`${title}-${index}`}>{text(item)}</span>)}
        {items.length === 0 && <span>none</span>}
      </div>
    </div>
  );
}

function AuthorityGrid({ authority }: { authority: Record<string, unknown> }) {
  const entries = Object.entries(authority);
  return (
    <div className="ion-extension-authority-grid">
      {entries.map(([key, value]) => (
        <div className={`ion-runtime-metric is-${String(value).toLowerCase()}`} key={key}>
          <span>{key}</span>
          <b>{text(value)}</b>
        </div>
      ))}
      {entries.length === 0 && <div className="ion-empty-state">NO AUTHORITY MAP</div>}
    </div>
  );
}

function asList(value: unknown): unknown[] {
  return Array.isArray(value) ? value : [];
}

function asRecords(value: unknown): Array<Record<string, unknown>> {
  return Array.isArray(value) ? value.filter((item): item is Record<string, unknown> => Boolean(item) && typeof item === 'object' && !Array.isArray(item)) : [];
}

function hasReadableMessage(value: Record<string, unknown>) {
  return text(value.text_preview, '').length > 0;
}

function text(value: unknown, fallback = 'unknown') {
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
