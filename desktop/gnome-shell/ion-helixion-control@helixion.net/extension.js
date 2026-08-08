const {Clutter, Gio, GLib, GObject, St} = imports.gi;
const Main = imports.ui.main;
const PanelMenu = imports.ui.panelMenu;
const PopupMenu = imports.ui.popupMenu;
const ExtensionUtils = imports.misc.extensionUtils;

const Me = ExtensionUtils.getCurrentExtension();
const UUID = 'ion-helixion-control@helixion.net';
const REFRESH_SECONDS = 30;
const GROUP_IDS = ['helixion', 'actions', 'chatops'];
const TIMER_TOGGLE_IDS = ['queue', 'loop'];
const TIMER_TOGGLE_LABELS = {
    queue: 'Queue drain (5 min timer)',
    loop: 'Autonomous loop (hourly)',
};
const GROUP_LABELS = {
    helixion: 'Helixion',
    actions: 'Actions',
    chatops: 'ChatOps',
};
const GROUP_ROUTES = {
    helixion: ':8765 + ion.helixion.net',
    actions: ':8777 + ion-actions.helixion.net',
    chatops: ':8767 local bridge',
};

var IonConnectionsIndicator = GObject.registerClass(
class IonConnectionsIndicator extends PanelMenu.Button {
    _init() {
        super._init(0.0, 'ION startup connections', false);

        this._destroyed = false;
        this._busy = false;
        this._statusRequestInFlight = false;
        this._syncingToggles = false;
        this._generation = 0;
        this._timerId = 0;
        this._cancellables = new Set();
        this._lastStatus = null;
        this._helperPath = Me.dir.get_child('control.py').get_path();

        this._panelBox = new St.BoxLayout({style_class: 'ion-helixion-panel-box'});
        this._statusIcon = new St.Icon({
            icon_name: 'content-loading-symbolic',
            style_class: 'system-status-icon ion-helixion-status-icon ion-helixion-checking',
            y_align: Clutter.ActorAlign.CENTER,
        });
        this._panelLabel = new St.Label({
            text: 'ION',
            style_class: 'ion-helixion-panel-label',
            y_align: Clutter.ActorAlign.CENTER,
        });
        this._panelWarnBadge = new St.Label({
            text: '',
            style_class: 'ion-helixion-badge',
            y_align: Clutter.ActorAlign.CENTER,
        });
        this._panelRunBadge = new St.Label({
            text: '',
            style_class: 'ion-helixion-panel-label',
            y_align: Clutter.ActorAlign.CENTER,
        });
        this._panelBox.add_child(this._statusIcon);
        this._panelBox.add_child(this._panelLabel);
        this._panelBox.add_child(this._panelWarnBadge);
        this._panelBox.add_child(this._panelRunBadge);
        this.add_child(this._panelBox);

        this._titleItem = this._makeInfoItem('ION connections', 'ion-helixion-menu-title');
        this._summaryItem = this._makeInfoItem('Checking startup connections…', 'ion-helixion-menu-summary');
        this.menu.addMenuItem(this._titleItem);
        this.menu.addMenuItem(this._summaryItem);
        this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());

        this._toggles = {};
        this._detailItems = {};
        for (const groupId of GROUP_IDS) {
            const toggle = new PopupMenu.PopupSwitchMenuItem(GROUP_LABELS[groupId], false);
            toggle.connect('toggled', (_item, state) => this._onToggle(groupId, state));
            toggle.setSensitive(false);
            this._toggles[groupId] = toggle;
            this.menu.addMenuItem(toggle);

            const detail = this._makeInfoItem(`  Unknown · ${GROUP_ROUTES[groupId]}`, 'ion-helixion-group-detail');
            this._detailItems[groupId] = detail;
            this.menu.addMenuItem(detail);
        }

        this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());
        this._instancesItem = this._makeInfoItem('PC-backed processes: checking');
        this.menu.addMenuItem(this._instancesItem);

        this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());
        this._queueSectionTitle = this._makeInfoItem('ION queue', 'ion-helixion-section-title');
        this.menu.addMenuItem(this._queueSectionTitle);

        this._timerToggles = {};
        for (const timerId of TIMER_TOGGLE_IDS) {
            const toggle = new PopupMenu.PopupSwitchMenuItem(TIMER_TOGGLE_LABELS[timerId], false);
            toggle.connect('toggled', (_item, state) => this._onTimerToggle(timerId, state));
            toggle.setSensitive(false);
            this._timerToggles[timerId] = toggle;
            this.menu.addMenuItem(toggle);
        }

        this._queueCountsItem = this._makeInfoItem('pending — · executed — · quarantined —', 'ion-helixion-group-detail');
        this._queueDrainItem = this._makeInfoItem('unknown', 'ion-helixion-group-detail');
        this._queueAlertItem = this._makeInfoItem('', 'ion-helixion-warn');
        this._queueAlertItem.hide();
        this.menu.addMenuItem(this._queueCountsItem);
        this.menu.addMenuItem(this._queueDrainItem);
        this.menu.addMenuItem(this._queueAlertItem);

        this._agentsSectionTitle = this._makeInfoItem('Agents', 'ion-helixion-section-title');
        this._agentsSummaryItem = this._makeInfoItem('In flight: —', 'ion-helixion-group-detail');
        this.menu.addMenuItem(this._agentsSectionTitle);
        this.menu.addMenuItem(this._agentsSummaryItem);
        this._agentRunItems = [];
        for (let i = 0; i < 3; i++) {
            const runItem = this._makeInfoItem('', 'ion-helixion-run-line');
            runItem.hide();
            this._agentRunItems.push(runItem);
            this.menu.addMenuItem(runItem);
        }

        this._attentionSectionTitle = this._makeInfoItem('Attention', 'ion-helixion-section-title');
        this._attentionGatesItem = this._makeInfoItem('Gates: —', 'ion-helixion-group-detail');
        this._attentionAbsenceItem = this._makeInfoItem('Absence checks: —', 'ion-helixion-group-detail');
        this._attentionLoopItem = this._makeInfoItem('Loop: —', 'ion-helixion-group-detail');
        this._attentionWakeupItem = this._makeInfoItem('Wakeup: —', 'ion-helixion-group-detail');
        this.menu.addMenuItem(this._attentionSectionTitle);
        this.menu.addMenuItem(this._attentionGatesItem);
        this.menu.addMenuItem(this._attentionAbsenceItem);
        this.menu.addMenuItem(this._attentionLoopItem);
        this.menu.addMenuItem(this._attentionWakeupItem);

        this._openRunViewItem = new PopupMenu.PopupMenuItem('Open latest run in terminal');
        this._openRunViewItem.connect('activate', () => this._onOpenLatestRunView());
        this.menu.addMenuItem(this._openRunViewItem);

        this._refreshItem = new PopupMenu.PopupMenuItem('Refresh now');
        this._refreshItem.connect('activate', () => this.refresh());
        this.menu.addMenuItem(this._refreshItem);

        this._openItem = new PopupMenu.PopupMenuItem('Open ION JOC cockpit (local :8765)');
        this._openItem.connect('activate', () => this._openCockpit());
        this.menu.addMenuItem(this._openItem);

        this._checkedItem = this._makeInfoItem('Last checked: —');
        this.menu.addMenuItem(this._checkedItem);

        this._menuSignalId = this.menu.connect('open-state-changed', (_menu, isOpen) => {
            if (isOpen)
                this.refresh();
        });

        this.refresh();
        this._timerId = GLib.timeout_add_seconds(GLib.PRIORITY_DEFAULT, REFRESH_SECONDS, () => {
            if (this._destroyed)
                return GLib.SOURCE_REMOVE;
            this.refresh();
            return GLib.SOURCE_CONTINUE;
        });
    }

    _makeInfoItem(text, styleClass = null) {
        const item = new PopupMenu.PopupMenuItem(text, {reactive: false, can_focus: false});
        if (styleClass)
            item.label.add_style_class_name(styleClass);
        return item;
    }

    _runHelper(action, callback) {
        const cancellable = new Gio.Cancellable();
        this._cancellables.add(cancellable);
        let process;
        try {
            process = Gio.Subprocess.new(
                ['/usr/bin/python3', this._helperPath, action],
                Gio.SubprocessFlags.STDOUT_PIPE | Gio.SubprocessFlags.STDERR_PIPE
            );
        } catch (error) {
            this._cancellables.delete(cancellable);
            callback(null, `Unable to start health helper: ${error.message}`);
            return;
        }
        process.communicate_utf8_async(null, cancellable, (source, result) => {
            this._cancellables.delete(cancellable);
            try {
                const [, stdout, stderr] = source.communicate_utf8_finish(result);
                if (this._destroyed)
                    return;
                if (!stdout)
                    throw new Error(stderr || 'health helper returned no data');
                callback(JSON.parse(stdout), null);
            } catch (error) {
                if (!this._destroyed && !cancellable.is_cancelled())
                    callback(null, `Health helper failed: ${error.message}`);
            }
        });
    }

    refresh() {
        if (this._destroyed || this._busy || this._statusRequestInFlight)
            return;
        const generation = ++this._generation;
        this._statusRequestInFlight = true;
        this._setPanelState('checking');
        this._runHelper('status', (payload, error) => {
            this._statusRequestInFlight = false;
            if (this._destroyed || generation !== this._generation)
                return;
            if (error) {
                this._renderUnavailable(error);
                return;
            }
            this._renderStatus(payload);
        });
    }

    _onToggle(groupId, state) {
        if (this._syncingToggles || this._busy || this._destroyed || !GROUP_IDS.includes(groupId))
            return;
        this._generation++;
        this._busy = true;
        this._setControlsSensitive(false);
        const label = GROUP_LABELS[groupId];
        this._summaryItem.label.set_text(state ? `Starting and enabling ${label}…` : `Stopping and disabling ${label}…`);
        this._setPanelState('checking');
        this._runHelper(`${groupId}-${state ? 'on' : 'off'}`, (payload, error) => {
            if (this._destroyed)
                return;
            this._busy = false;
            if (error || !payload) {
                this._renderUnavailable(error || 'The requested state change failed.');
                Main.notify('ION connections', error || 'The requested state change failed.');
                return;
            }
            const status = payload.status || payload;
            this._renderStatus(status);
            if (payload.ok === false)
                Main.notify('ION connections', `${label} did not fully reach the requested state; open the menu for details.`);
            else if (payload.health_ok === false)
                Main.notify('ION connections', `${label} changed state, but its health still needs attention.`);
        });
    }

    _onTimerToggle(timerId, state) {
        if (this._syncingToggles || this._busy || this._destroyed || !TIMER_TOGGLE_IDS.includes(timerId))
            return;
        this._generation++;
        this._busy = true;
        this._setControlsSensitive(false);
        const label = TIMER_TOGGLE_LABELS[timerId];
        this._summaryItem.label.set_text(state ? `Enabling ${label}…` : `Disabling ${label}…`);
        this._setPanelState('checking');
        this._runHelper(timerId === 'queue' ? (state ? 'queue-on' : 'queue-off') : (state ? 'loop-on' : 'loop-off'), (payload, error) => {
            if (this._destroyed)
                return;
            this._busy = false;
            if (error || !payload) {
                this._renderUnavailable(error || 'The requested timer change failed.');
                Main.notify('ION connections', error || 'The requested timer change failed.');
                return;
            }
            const status = payload.status || payload;
            this._renderStatus(status);
            if (payload.ok === false)
                Main.notify('ION connections', `${label} did not fully reach the requested state; open the menu for details.`);
        });
    }

    _onOpenLatestRunView() {
        if (this._busy || this._destroyed)
            return;
        this._generation++;
        this._busy = true;
        this._setControlsSensitive(false);
        this._runHelper('open-latest-run-view', (payload, error) => {
            if (this._destroyed)
                return;
            this._busy = false;
            if (error || !payload) {
                Main.notify('ION connections', error || 'Could not open latest run view.');
                this._setControlsSensitive(true);
                return;
            }
            if (payload.ok === true) {
                const runId = payload.run_id || 'latest';
                Main.notify('ION connections', `Viewing ${runId} — closing that window never stops the worker.`);
            } else {
                const reason = payload.error || payload.reason || 'Could not open latest run view.';
                Main.notify('ION connections', reason);
            }
            if (this._lastStatus)
                this._renderStatus(this._lastStatus);
            else
                this.refresh();
        });
    }

    _setControlsSensitive(sensitive) {
        const groups = (this._lastStatus && this._lastStatus.groups) || {};
        for (const groupId of GROUP_IDS) {
            const controllable = groups[groupId] ? groups[groupId].controllable !== false : false;
            this._toggles[groupId].setSensitive(Boolean(sensitive && controllable));
        }
        const queueOk = this._lastStatus && !this._sectionError(this._lastStatus.queue);
        for (const timerId of TIMER_TOGGLE_IDS)
            this._timerToggles[timerId].setSensitive(Boolean(sensitive && queueOk));
        this._refreshItem.setSensitive(Boolean(sensitive));
    }

    _sectionError(section) {
        return !section || typeof section !== 'object' || section.error !== undefined;
    }

    _safeSection(status, key) {
        const section = status && status[key];
        if (this._sectionError(section))
            return null;
        return section;
    }

    _shortenIonToken(value) {
        if (!value || typeof value !== 'string')
            return 'unavailable';
        let text = value;
        if (text.startsWith('ION_'))
            text = text.slice(4);
        return text.replace(/_/g, ' ');
    }

    _formatDomainShort(domainId) {
        if (!domainId || typeof domainId !== 'string')
            return 'unknown';
        let short = domainId.startsWith('domain.') ? domainId.slice(7) : domainId;
        if (short.length > 28)
            short = short.slice(0, 28);
        return short;
    }

    _updatePanelBadge(status) {
        this._panelLabel.set_text('ION');
        const queue = this._safeSection(status, 'queue');
        const agents = this._safeSection(status, 'agents');
        const attention = this._safeSection(status, 'attention');

        const checksFlagged = attention && typeof attention.checks_flagged === 'number' ? attention.checks_flagged : 0;
        const quarantined = queue && typeof queue.quarantined_count === 'number' ? queue.quarantined_count : 0;
        const loopBlocked = attention && attention.loop_status === 'BLOCKED';
        if (checksFlagged > 0 || quarantined > 0 || loopBlocked) {
            const n = checksFlagged + quarantined;
            this._panelWarnBadge.set_text(` ·${n}`);
        } else {
            this._panelWarnBadge.set_text('');
        }
        const inFlight = agents && typeof agents.in_flight_count === 'number' ? agents.in_flight_count : 0;
        if (inFlight > 0)
            this._panelRunBadge.set_text(` ⋯${inFlight}`);
        else
            this._panelRunBadge.set_text('');
    }

    _renderQueueSection(status) {
        const queue = this._safeSection(status, 'queue');
        if (!queue) {
            this._queueCountsItem.label.set_text('pending — · executed — · quarantined —');
            this._queueDrainItem.label.set_text('unavailable');
            this._queueAlertItem.hide();
            return;
        }
        const pending = queue.pending_count != null ? queue.pending_count : '—';
        const executed = queue.executed_count != null ? queue.executed_count : '—';
        const quarantined = queue.quarantined_count != null ? queue.quarantined_count : '—';
        this._queueCountsItem.label.set_text(`pending ${pending} · executed ${executed} · quarantined ${quarantined}`);

        const verdict = queue.last_drain_verdict
            ? this._shortenIonToken(queue.last_drain_verdict)
            : 'unavailable';
        const at = this._formatTime(queue.last_drain_at);
        this._queueDrainItem.label.set_text(`${verdict} · ${at}`);

        const alerts = Array.isArray(queue.absence_alerts) ? queue.absence_alerts : [];
        if (alerts.length > 0) {
            this._queueAlertItem.label.set_text(`⚠ ${alerts.join(', ')}`);
            this._queueAlertItem.show();
        } else {
            this._queueAlertItem.hide();
        }
    }

    _renderAgentsSection(status) {
        const agents = this._safeSection(status, 'agents');
        if (!agents) {
            this._agentsSummaryItem.label.set_text('In flight: unavailable');
            for (const item of this._agentRunItems)
                item.hide();
            return;
        }
        const inFlight = agents.in_flight_count != null ? agents.in_flight_count : '—';
        const carriers = agents.carrier_processes && typeof agents.carrier_processes === 'object'
            ? agents.carrier_processes
            : {};
        const claude = carriers.claude != null ? carriers.claude : '—';
        const cursor = carriers.cursor_agent != null ? carriers.cursor_agent : '—';
        const codex = carriers.codex != null ? carriers.codex : '—';
        this._agentsSummaryItem.label.set_text(
            `In flight: ${inFlight} · claude ${claude} · cursor ${cursor} · codex ${codex}`
        );

        const runs = Array.isArray(agents.recent_runs) ? agents.recent_runs.slice(0, 3) : [];
        for (let i = 0; i < this._agentRunItems.length; i++) {
            const item = this._agentRunItems[i];
            const run = runs[i];
            if (!run) {
                item.hide();
                continue;
            }
            const mark = run.finished ? '✓' : '⋯';
            const domain = this._formatDomainShort(run.domain_id);
            const workClass = run.work_class || 'unknown';
            item.label.set_text(`${mark} ${domain} · ${workClass}`);
            item.show();
        }
    }

    _renderAttentionSection(status) {
        const attention = this._safeSection(status, 'attention');
        if (!attention) {
            this._attentionGatesItem.label.set_text('Gates: unavailable');
            this._attentionAbsenceItem.label.set_text('Absence checks: unavailable');
            this._attentionLoopItem.label.set_text('Loop: unavailable');
            this._attentionWakeupItem.label.set_text('Wakeup: unavailable');
            this._attentionGatesItem.label.remove_style_class_name('ion-helixion-warn');
            this._attentionLoopItem.label.remove_style_class_name('ion-helixion-warn');
            return;
        }

        const gateCount = attention.open_gate_count != null ? attention.open_gate_count : '—';
        const nonBlocking = attention.non_blocking;
        let gatesText = `Gates: ${gateCount}`;
        this._attentionGatesItem.label.remove_style_class_name('ion-helixion-warn');
        if (nonBlocking === false) {
            gatesText += ' (BLOCKING)';
            this._attentionGatesItem.label.add_style_class_name('ion-helixion-warn');
        } else {
            gatesText += ' (non-blocking)';
        }
        this._attentionGatesItem.label.set_text(gatesText);

        const flagged = attention.checks_flagged != null ? attention.checks_flagged : '—';
        const total = attention.checks_total != null ? attention.checks_total : '—';
        const absence = this._shortenIonToken(attention.absence_verdict);
        this._attentionAbsenceItem.label.set_text(`Absence checks: ${flagged}/${total} flagged · ${absence}`);

        const loopStatus = attention.loop_status || 'unavailable';
        let loopText = `Loop: ${loopStatus}`;
        if (attention.loop_stop_reason)
            loopText += ` (${attention.loop_stop_reason})`;
        this._attentionLoopItem.label.remove_style_class_name('ion-helixion-warn');
        if (loopStatus === 'BLOCKED' || loopStatus === 'FAILED')
            this._attentionLoopItem.label.add_style_class_name('ion-helixion-warn');
        this._attentionLoopItem.label.set_text(loopText);

        const wakeup = this._shortenIonToken(attention.wakeup_verdict);
        this._attentionWakeupItem.label.set_text(`Wakeup: ${wakeup}`);
    }

    _renderStatus(status) {
        this._lastStatus = status;
        const groups = status.groups || {};
        this._setPanelState(status.overall || 'degraded');
        this._summaryItem.label.set_text(status.summary || 'Health status unavailable');

        this._syncingToggles = true;
        try {
            for (const groupId of GROUP_IDS) {
                const group = groups[groupId] || {};
                this._toggles[groupId].setToggleState(Boolean(group.toggle_on));
                this._detailItems[groupId].label.set_text(this._formatGroupDetail(groupId, group));
            }
            const queue = this._safeSection(status, 'queue');
            const drainEnabled = queue && queue.drain_timer && queue.drain_timer.enabled === true;
            const loopEnabled = queue && queue.loop_timer && queue.loop_timer.enabled === true;
            this._timerToggles.queue.setToggleState(Boolean(drainEnabled));
            this._timerToggles.loop.setToggleState(Boolean(loopEnabled));
        } finally {
            this._syncingToggles = false;
        }

        const instances = status.instances || {};
        this._instancesItem.label.set_text(
            `PC-backed processes: ${instances.local_process_count || 0} local · ${instances.cloudflared_tunnel_count || 0} tunnels`
        );

        this._renderQueueSection(status);
        this._renderAgentsSection(status);
        this._renderAttentionSection(status);
        this._updatePanelBadge(status);

        const helixion = groups.helixion || {};
        this._openItem.setSensitive(helixion.overall === 'healthy');
        this._checkedItem.label.set_text(`Last checked: ${this._formatTime(status.generated_at)}`);
        this._setControlsSensitive(true);
    }

    _formatGroupDetail(groupId, group) {
        const state = this._stateLabel(group.overall);
        const startupState = group.startup_state || (group.startup_enabled ? 'enabled' : 'disabled');
        const startup = startupState === 'enabled'
            ? 'login on'
            : (startupState === 'partial' ? 'login partial' : 'login off');
        return `  ${state} · ${GROUP_ROUTES[groupId]} · ${startup}`;
    }

    _stateLabel(state) {
        if (state === 'healthy')
            return 'Healthy';
        if (state === 'degraded')
            return 'Degraded';
        if (state === 'conflict')
            return 'Conflict';
        if (state === 'off')
            return 'Off';
        return 'Unknown';
    }

    _renderExtendedSectionsUnavailable() {
        this._queueCountsItem.label.set_text('pending — · executed — · quarantined —');
        this._queueDrainItem.label.set_text('unknown');
        this._queueAlertItem.hide();
        this._agentsSummaryItem.label.set_text('In flight: unknown');
        for (const item of this._agentRunItems)
            item.hide();
        this._attentionGatesItem.label.set_text('Gates: unknown');
        this._attentionAbsenceItem.label.set_text('Absence checks: unknown');
        this._attentionLoopItem.label.set_text('Loop: unknown');
        this._attentionWakeupItem.label.set_text('Wakeup: unknown');
        this._attentionGatesItem.label.remove_style_class_name('ion-helixion-warn');
        this._attentionLoopItem.label.remove_style_class_name('ion-helixion-warn');
        this._panelLabel.set_text('ION');
        this._panelWarnBadge.set_text('');
        this._panelRunBadge.set_text('');
    }

    _renderUnavailable(error) {
        this._lastStatus = null;
        this._setPanelState('conflict');
        this._summaryItem.label.set_text('Connection health helper unavailable');
        this._syncingToggles = true;
        try {
            for (const groupId of GROUP_IDS) {
                this._toggles[groupId].setToggleState(false);
                this._detailItems[groupId].label.set_text(`  Unknown · ${GROUP_ROUTES[groupId]}`);
                this._toggles[groupId].setSensitive(false);
            }
            for (const timerId of TIMER_TOGGLE_IDS) {
                this._timerToggles[timerId].setToggleState(false);
                this._timerToggles[timerId].setSensitive(false);
            }
        } finally {
            this._syncingToggles = false;
        }
        this._instancesItem.label.set_text('PC-backed processes: unknown');
        this._renderExtendedSectionsUnavailable();
        this._openItem.setSensitive(false);
        this._refreshItem.setSensitive(true);
        this._checkedItem.label.set_text('Last checked: failed');
        logError(new Error(error), 'ION connections extension');
    }

    _setPanelState(state) {
        const classes = [
            'ion-helixion-healthy',
            'ion-helixion-degraded',
            'ion-helixion-conflict',
            'ion-helixion-off',
            'ion-helixion-checking',
        ];
        for (const styleClass of classes)
            this._statusIcon.remove_style_class_name(styleClass);

        let iconName = 'dialog-warning-symbolic';
        let styleClass = 'ion-helixion-degraded';
        if (state === 'healthy') {
            iconName = 'emblem-ok-symbolic';
            styleClass = 'ion-helixion-healthy';
        } else if (state === 'off') {
            iconName = 'network-offline-symbolic';
            styleClass = 'ion-helixion-off';
        } else if (state === 'conflict') {
            iconName = 'dialog-error-symbolic';
            styleClass = 'ion-helixion-conflict';
        } else if (state === 'checking') {
            iconName = 'content-loading-symbolic';
            styleClass = 'ion-helixion-checking';
        }
        this._statusIcon.set_icon_name(iconName);
        this._statusIcon.add_style_class_name(styleClass);
    }

    _formatTime(value) {
        if (!value)
            return '—';
        const parsed = GLib.DateTime.new_from_iso8601(value, null);
        if (!parsed)
            return value;
        return parsed.to_local().format('%H:%M:%S');
    }

    _openCockpit() {
        const helixion = (this._lastStatus && this._lastStatus.groups && this._lastStatus.groups.helixion) || {};
        const url = helixion.open_url || 'http://127.0.0.1:8765/cockpit#system';
        if (helixion.overall !== 'healthy') {
            Main.notify('ION connections', 'Local cockpit opens only when Helixion preview is healthy on :8765.');
            return;
        }
        try {
            const context = global.create_app_launch_context(0, -1);
            Gio.AppInfo.launch_default_for_uri(url, context);
        } catch (error) {
            Main.notify('ION connections', `Could not open cockpit: ${error.message}`);
        }
    }

    destroy() {
        this._destroyed = true;
        this._generation++;
        if (this._timerId) {
            GLib.source_remove(this._timerId);
            this._timerId = 0;
        }
        if (this._menuSignalId) {
            this.menu.disconnect(this._menuSignalId);
            this._menuSignalId = 0;
        }
        for (const cancellable of this._cancellables)
            cancellable.cancel();
        this._cancellables.clear();
        super.destroy();
    }
});

let indicator = null;

function init() {
}

function enable() {
    indicator = new IonConnectionsIndicator();
    Main.panel.addToStatusArea(UUID, indicator, 0, 'right');
}

function disable() {
    if (indicator) {
        indicator.destroy();
        indicator = null;
    }
}
