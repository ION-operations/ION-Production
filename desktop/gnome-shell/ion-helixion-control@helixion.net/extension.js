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
const TAB_IDS = ['status', 'queue', 'agents', 'questions', 'settings'];
const REPLY_MAX_CHARS = 2000;
const CARRIER_CLI_IDS = ['cursor_cli', 'claude_cli', 'codex_cli'];
const CARRIER_SHORT_NAMES = {
    cursor_cli: 'cursor',
    claude_cli: 'claude',
    codex_cli: 'codex',
};
const CARRIER_MODE_CYCLE = ['full', 'reduced', 'premium_only'];
const CARRIER_LIMIT_STEP = 50;
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

var IonTabBarMenuItem = GObject.registerClass(
class IonTabBarMenuItem extends PopupMenu.PopupBaseMenuItem {
    _init(indicator) {
        super._init({reactive: false, can_focus: false});
        this._indicator = indicator;
        this.actor.add_style_class_name('ion-helixion-tab-bar-item');
        this._box = new St.BoxLayout({
            style_class: 'ion-helixion-tab-bar',
            x_expand: true,
        });
        this.actor.add_child(this._box);
        this._tabButtons = {};
        for (const tabId of TAB_IDS) {
            const button = new St.Button({
                style_class: 'ion-helixion-tab',
                label: tabId,
                can_focus: true,
            });
            button.connect('clicked', () => this._indicator._onTabSelected(tabId));
            this._tabButtons[tabId] = button;
            this._box.add_child(button);
        }
    }

    setTabLabel(tabId, label) {
        if (this._tabButtons[tabId])
            this._tabButtons[tabId].label = label;
    }

    setActiveTab(tabId) {
        for (const id of TAB_IDS) {
            const button = this._tabButtons[id];
            if (!button)
                continue;
            if (id === tabId)
                button.add_style_class_name('ion-helixion-tab-active');
            else
                button.remove_style_class_name('ion-helixion-tab-active');
        }
    }
});

var IonQuestionsHostMenuItem = GObject.registerClass(
class IonQuestionsHostMenuItem extends PopupMenu.PopupBaseMenuItem {
    _init() {
        super._init({reactive: false, can_focus: false});
        this._host = new St.BoxLayout({
            style_class: 'ion-helixion-questions-host',
            vertical: true,
            x_expand: true,
        });
        this.actor.add_child(this._host);
    }

    clear() {
        const children = this._host.get_children();
        for (const child of children)
            this._host.remove_child(child);
        children.forEach(child => child.destroy());
    }

    addActor(actor) {
        this._host.add_child(actor);
    }
});

var IonCarriersHostMenuItem = GObject.registerClass(
class IonCarriersHostMenuItem extends PopupMenu.PopupBaseMenuItem {
    _init() {
        super._init({reactive: false, can_focus: false});
        this._host = new St.BoxLayout({
            style_class: 'ion-helixion-carriers-host',
            vertical: true,
            x_expand: true,
        });
        this.actor.add_child(this._host);
    }

    clear() {
        const children = this._host.get_children();
        for (const child of children)
            this._host.remove_child(child);
        children.forEach(child => child.destroy());
    }

    addActor(actor) {
        this._host.add_child(actor);
    }
});

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
        this._activePage = 'status';
        this._userSelectedTab = false;
        this._pushAuthorizationReady = false;
        this._lastAcceptedCategory = null;
        this._replyOpenDecisionId = null;
        this._syncingCarrierControls = false;
        this._carriersSectionReady = false;
        this._pageMenuItems = {status: [], queue: [], agents: [], questions: [], settings: []};
        this._chromeMenuItems = [];

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
        this._panelQuestionBadge = new St.Label({
            text: '',
            style_class: 'ion-helixion-question-badge',
            y_align: Clutter.ActorAlign.CENTER,
        });
        this._panelBox.add_child(this._statusIcon);
        this._panelBox.add_child(this._panelLabel);
        this._panelBox.add_child(this._panelWarnBadge);
        this._panelBox.add_child(this._panelRunBadge);
        this._panelBox.add_child(this._panelQuestionBadge);
        this.add_child(this._panelBox);

        this._titleItem = this._makeInfoItem('ION connections', 'ion-helixion-menu-title');
        this._summaryItem = this._makeInfoItem('Checking startup connections…', 'ion-helixion-menu-summary');
        this._addChrome(this._titleItem);
        this._addChrome(this._summaryItem);

        this._tabBarItem = new IonTabBarMenuItem(this);
        this._addChrome(this._tabBarItem);
        this._addChrome(new PopupMenu.PopupSeparatorMenuItem());

        this._statusConnectionItems = {};
        for (const groupId of GROUP_IDS) {
            const line = this._makeInfoItem(`${GROUP_LABELS[groupId]}: checking…`, 'ion-helixion-group-detail');
            this._statusConnectionItems[groupId] = line;
            this._addPageItem('status', line);
        }

        this._instancesItem = this._makeInfoItem('PC-backed processes: checking');
        this._addPageItem('status', this._instancesItem);

        this._attentionSectionTitle = this._makeInfoItem('Attention', 'ion-helixion-section-title');
        this._attentionGatesItem = this._makeInfoItem('Gates: —', 'ion-helixion-group-detail');
        this._attentionAbsenceItem = this._makeInfoItem('Absence checks: —', 'ion-helixion-group-detail');
        this._attentionLoopItem = this._makeInfoItem('Loop: —', 'ion-helixion-group-detail');
        this._attentionWakeupItem = this._makeInfoItem('Wakeup: —', 'ion-helixion-group-detail');
        this._attentionCarrierItem = this._makeInfoItem('', 'ion-helixion-warn');
        this._attentionCarrierItem.hide();
        for (const item of [
            this._attentionSectionTitle,
            this._attentionGatesItem,
            this._attentionAbsenceItem,
            this._attentionLoopItem,
            this._attentionWakeupItem,
            this._attentionCarrierItem,
        ])
            this._addPageItem('status', item);

        this._checkedItem = this._makeInfoItem('Last checked: —');
        this._addPageItem('status', this._checkedItem);

        this._queueSectionTitle = this._makeInfoItem('ION queue', 'ion-helixion-section-title');
        this._addPageItem('queue', this._queueSectionTitle);

        this._timerToggles = {};
        for (const timerId of TIMER_TOGGLE_IDS) {
            const toggle = new PopupMenu.PopupSwitchMenuItem(TIMER_TOGGLE_LABELS[timerId], false);
            toggle.connect('toggled', (_item, state) => this._onTimerToggle(timerId, state));
            toggle.setSensitive(false);
            this._timerToggles[timerId] = toggle;
            this._addPageItem('queue', toggle);
        }

        this._queueCountsItem = this._makeInfoItem('pending — · executed — · quarantined —', 'ion-helixion-group-detail');
        this._queueDrainItem = this._makeInfoItem('unknown', 'ion-helixion-group-detail');
        this._queueAlertItem = this._makeInfoItem('', 'ion-helixion-warn');
        this._queueAlertItem.hide();
        for (const item of [this._queueCountsItem, this._queueDrainItem, this._queueAlertItem])
            this._addPageItem('queue', item);

        this._agentsSectionTitle = this._makeInfoItem('Agents', 'ion-helixion-section-title');
        this._agentsSummaryItem = this._makeInfoItem('In flight: —', 'ion-helixion-group-detail');
        this._addPageItem('agents', this._agentsSectionTitle);
        this._addPageItem('agents', this._agentsSummaryItem);
        this._agentRunItems = [];
        for (let i = 0; i < 3; i++) {
            const runItem = this._makeInfoItem('', 'ion-helixion-run-line');
            runItem.hide();
            this._agentRunItems.push(runItem);
            this._addPageItem('agents', runItem);
        }

        this._openRunViewItem = new PopupMenu.PopupMenuItem('Open latest run in terminal');
        this._openRunViewItem.connect('activate', () => this._onOpenLatestRunView());
        this._addPageItem('agents', this._openRunViewItem);

        this._questionsHostItem = new IonQuestionsHostMenuItem();
        this._addPageItem('questions', this._questionsHostItem);

        this._carriersSectionTitle = this._makeInfoItem('Carriers', 'ion-helixion-section-title');
        this._carriersHostItem = new IonCarriersHostMenuItem();
        this._reducedStateItem = this._makeInfoItem('Reduced-tier work: —', 'ion-helixion-group-detail');
        this._addPageItem('settings', this._carriersSectionTitle);
        this._addPageItem('settings', this._carriersHostItem);
        this._addPageItem('settings', this._reducedStateItem);
        this._addPageItem('settings', new PopupMenu.PopupSeparatorMenuItem());

        this._toggles = {};
        this._detailItems = {};
        for (const groupId of GROUP_IDS) {
            const toggle = new PopupMenu.PopupSwitchMenuItem(GROUP_LABELS[groupId], false);
            toggle.connect('toggled', (_item, state) => this._onToggle(groupId, state));
            toggle.setSensitive(false);
            this._toggles[groupId] = toggle;
            this._addPageItem('settings', toggle);

            const detail = this._makeInfoItem(`  Unknown · ${GROUP_ROUTES[groupId]}`, 'ion-helixion-group-detail');
            this._detailItems[groupId] = detail;
            this._addPageItem('settings', detail);
        }

        this._openItem = new PopupMenu.PopupMenuItem('Open ION JOC cockpit (local :8765)');
        this._openItem.connect('activate', () => this._openCockpit());
        this._addPageItem('settings', this._openItem);

        this._refreshItem = new PopupMenu.PopupMenuItem('Refresh now');
        this._refreshItem.connect('activate', () => this.refresh());
        this._addPageItem('settings', this._refreshItem);

        this._showPage(this._activePage);

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

    _addChrome(item) {
        this.menu.addMenuItem(item);
        this._chromeMenuItems.push(item);
    }

    _addPageItem(pageId, item) {
        this.menu.addMenuItem(item);
        this._pageMenuItems[pageId].push(item);
        if (pageId !== this._activePage)
            item.actor.hide();
    }

    _onTabSelected(tabId) {
        if (!TAB_IDS.includes(tabId))
            return;
        this._userSelectedTab = true;
        this._showPage(tabId);
    }

    _showPage(pageId) {
        if (!TAB_IDS.includes(pageId))
            return;
        this._activePage = pageId;
        for (const id of TAB_IDS) {
            for (const item of this._pageMenuItems[id]) {
                if (id === pageId)
                    item.actor.show();
                else
                    item.actor.hide();
            }
        }
        this._tabBarItem.setActiveTab(pageId);
    }

    _pickDefaultPage(status) {
        if (this._userSelectedTab)
            return;
        const decisions = this._safeSection(status, 'decisions');
        const pending = decisions && typeof decisions.pending_count === 'number' ? decisions.pending_count : 0;
        this._showPage(pending > 0 ? 'questions' : 'status');
    }

    _updateTabLabels(status) {
        const decisions = this._safeSection(status, 'decisions');
        const pending = decisions && typeof decisions.pending_count === 'number' ? decisions.pending_count : 0;
        const agents = this._safeSection(status, 'agents');
        const inFlight = agents && typeof agents.in_flight_count === 'number' ? agents.in_flight_count : 0;

        this._tabBarItem.setTabLabel('status', 'Status');
        this._tabBarItem.setTabLabel('queue', 'Queue');
        this._tabBarItem.setTabLabel('agents', inFlight > 0 ? `Agents (${inFlight})` : 'Agents');
        this._tabBarItem.setTabLabel('questions', pending > 0 ? `Questions (${pending})` : 'Questions');
        this._tabBarItem.setTabLabel('settings', 'Settings');
    }

    _makeInfoItem(text, styleClass = null) {
        const item = new PopupMenu.PopupMenuItem(text, {reactive: false, can_focus: false});
        if (styleClass)
            item.label.add_style_class_name(styleClass);
        return item;
    }

    _runHelper(actionOrArgv, callback) {
        const cancellable = new Gio.Cancellable();
        this._cancellables.add(cancellable);
        const argv = Array.isArray(actionOrArgv)
            ? ['/usr/bin/python3', this._helperPath, ...actionOrArgv]
            : ['/usr/bin/python3', this._helperPath, actionOrArgv];
        let process;
        try {
            process = Gio.Subprocess.new(
                argv,
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

    _refreshStatusAfterMutation() {
        this._runHelper('status', (payload, error) => {
            if (this._destroyed)
                return;
            if (error || !payload) {
                this._renderUnavailable(error || 'Status refresh failed after action.');
                Main.notify('ION connections', error || 'Status refresh failed after action.');
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

    _onDecisionAction(action, decisionId, replyText = null) {
        if (this._busy || this._destroyed || !decisionId)
            return;
        this._generation++;
        this._busy = true;
        this._setControlsSensitive(false);
        const argv = action === 'decision-reply'
            ? ['decision-reply', decisionId, String(replyText || '').slice(0, REPLY_MAX_CHARS)]
            : [action, decisionId];
        this._runHelper(argv, (payload, error) => {
            if (this._destroyed)
                return;
            this._busy = false;
            if (error || !payload) {
                Main.notify('ION questions', error || 'Decision action failed.');
                this._setControlsSensitive(true);
                return;
            }
            if (payload.ok === false) {
                const reason = payload.reason || 'Decision action failed.';
                Main.notify('ION questions', reason);
            } else {
                const summary = payload.state || payload.choice || 'ok';
                Main.notify('ION questions', `Decision ${decisionId}: ${summary}`);
                if (action === 'decision-accept' && this._lastAcceptedCategory === 'push_authorization')
                    this._pushAuthorizationReady = true;
            }
            this._replyOpenDecisionId = null;
            this._refreshStatusAfterMutation();
        });
    }

    _onCarrierMutation(argv, notifyLabel) {
        if (this._busy || this._destroyed)
            return;
        this._generation++;
        this._busy = true;
        this._setControlsSensitive(false);
        this._runHelper(argv, (payload, error) => {
            if (this._destroyed)
                return;
            this._busy = false;
            if (error || !payload) {
                Main.notify('ION carriers', error || 'Carrier action failed.');
                this._setControlsSensitive(true);
                return;
            }
            if (payload.ok === false) {
                const reason = payload.reason || 'Carrier action failed.';
                Main.notify('ION carriers', reason);
            } else if (notifyLabel)
                Main.notify('ION carriers', notifyLabel);
            this._refreshStatusAfterMutation();
        });
    }

    _onCarrierToggle(carrierId, enabled) {
        if (this._syncingCarrierControls || this._busy || this._destroyed)
            return;
        this._onCarrierMutation([enabled ? 'carrier-enable' : 'carrier-disable', carrierId]);
    }

    _onCarrierModeCycle(carrierId, currentMode) {
        if (this._syncingCarrierControls || this._busy || this._destroyed)
            return;
        const idx = CARRIER_MODE_CYCLE.indexOf(currentMode);
        const next = CARRIER_MODE_CYCLE[(idx + 1) % CARRIER_MODE_CYCLE.length];
        const shortName = CARRIER_SHORT_NAMES[carrierId] || carrierId;
        this._onCarrierMutation(
            ['carrier-mode', carrierId, next],
            `${shortName} mode → ${next}`
        );
    }

    _onCarrierLimitStep(carrierId, delta) {
        if (this._syncingCarrierControls || this._busy || this._destroyed)
            return;
        const block = this._lastStatus && this._lastStatus.carriers;
        const rows = block && block.carriers;
        const row = rows && rows[carrierId];
        if (!row || typeof row.daily_run_limit !== 'number')
            return;
        let next = row.daily_run_limit + delta;
        if (next < 0)
            next = 0;
        if (next > 10000)
            next = 10000;
        if (next === row.daily_run_limit)
            return;
        this._onCarrierMutation(['carrier-limit', carrierId, String(next)]);
    }

    _onPushReceipted() {
        if (this._busy || this._destroyed)
            return;
        this._generation++;
        this._busy = true;
        this._setControlsSensitive(false);
        this._runHelper('push-receipted', (payload, error) => {
            if (this._destroyed)
                return;
            this._busy = false;
            if (error || !payload) {
                Main.notify('ION push', error || 'push-receipted failed');
                this._setControlsSensitive(true);
                return;
            }
            Main.notify('ION push', JSON.stringify(payload));
            if (payload.ok === true)
                this._pushAuthorizationReady = false;
            this._refreshStatusAfterMutation();
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

    _renderStatusConnectionLines(status) {
        const groups = status.groups || {};
        for (const groupId of GROUP_IDS) {
            const group = groups[groupId] || {};
            const label = GROUP_LABELS[groupId];
            const detail = this._formatGroupDetail(groupId, group);
            this._statusConnectionItems[groupId].label.set_text(`${label}: ${detail.trim()}`);
        }
    }

    _updatePanelBadge(status) {
        this._panelLabel.set_text('ION');
        const queue = this._safeSection(status, 'queue');
        const agents = this._safeSection(status, 'agents');
        const attention = this._safeSection(status, 'attention');
        const decisions = this._safeSection(status, 'decisions');

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

        const pendingQuestions = decisions && typeof decisions.pending_count === 'number' ? decisions.pending_count : 0;
        if (pendingQuestions > 0)
            this._panelQuestionBadge.set_text(`?${pendingQuestions}`);
        else
            this._panelQuestionBadge.set_text('');
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

        const flagged = attention.checks_flagged != null ? attention.checks_flagged : 0;
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

        const alerts = Array.isArray(attention.carrier_alerts) ? attention.carrier_alerts : [];
        if (alerts.length > 0) {
            this._attentionCarrierItem.label.set_text(
                alerts.map(line => `⚠ ${line}`).join(' · ')
            );
            this._attentionCarrierItem.show();
        } else {
            this._attentionCarrierItem.hide();
        }
    }

    _renderCarriersSection(status) {
        const block = status && status.carriers;
        if (!block || block.error) {
            this._carriersSectionTitle.label.set_text('Carriers (unavailable)');
            this._carriersHostItem.clear();
            const label = new St.Label({
                text: 'Carrier settings unavailable',
                style_class: 'ion-helixion-group-detail',
            });
            this._carriersHostItem.addActor(label);
            this._reducedStateItem.label.set_text('Reduced-tier work: unavailable');
            this._carriersSectionReady = false;
            return;
        }
        this._carriersSectionTitle.label.set_text('Carriers');
        this._carriersSectionReady = true;
        const rows = block.carriers && typeof block.carriers === 'object' ? block.carriers : {};
        const reduced = block.reduced_state && typeof block.reduced_state === 'object'
            ? block.reduced_state
            : {};
        const ledgerRows = reduced.ledger_rows != null ? reduced.ledger_rows : '—';
        this._reducedStateItem.label.set_text(`Reduced-tier work: ${ledgerRows} runs ledgered`);

        this._syncingCarrierControls = true;
        try {
            this._carriersHostItem.clear();
            for (const carrierId of CARRIER_CLI_IDS) {
                const row = rows[carrierId];
                if (!row || typeof row !== 'object') {
                    const bad = new St.Label({
                        text: `${CARRIER_SHORT_NAMES[carrierId] || carrierId}: unavailable`,
                        style_class: 'ion-helixion-group-detail',
                    });
                    this._carriersHostItem.addActor(bad);
                    continue;
                }
                const shortName = CARRIER_SHORT_NAMES[carrierId] || carrierId;
                const runs = row.runs_today != null ? row.runs_today : '—';
                const limit = row.daily_run_limit != null ? row.daily_run_limit : '—';
                const mode = row.operation_mode || 'full';
                const line = new St.BoxLayout({style_class: 'ion-helixion-carrier-row'});
                const toggle = new St.Button({
                    style_class: 'ion-helixion-carrier-toggle',
                    label: row.enabled ? '●' : '○',
                    can_focus: true,
                });
                toggle.set_sensitive(this._carriersSectionReady && !this._busy);
                toggle.connect('clicked', () => {
                    this._onCarrierToggle(carrierId, !row.enabled);
                });
                const modeBtn = new St.Button({
                    style_class: 'ion-helixion-carrier-mode',
                    label: `${shortName} · ${runs}/${limit} today · ${mode}`,
                    can_focus: true,
                });
                modeBtn.set_sensitive(this._carriersSectionReady && !this._busy);
                modeBtn.connect('clicked', () => {
                    this._onCarrierModeCycle(carrierId, mode);
                });
                const minusBtn = new St.Button({label: '−', style_class: 'ion-helixion-carrier-step'});
                const plusBtn = new St.Button({label: '+', style_class: 'ion-helixion-carrier-step'});
                minusBtn.set_sensitive(this._carriersSectionReady && !this._busy);
                plusBtn.set_sensitive(this._carriersSectionReady && !this._busy);
                minusBtn.connect('clicked', () => this._onCarrierLimitStep(carrierId, -CARRIER_LIMIT_STEP));
                plusBtn.connect('clicked', () => this._onCarrierLimitStep(carrierId, CARRIER_LIMIT_STEP));
                line.add_child(toggle);
                line.add_child(modeBtn);
                line.add_child(minusBtn);
                line.add_child(plusBtn);
                this._carriersHostItem.addActor(line);
            }
        } finally {
            this._syncingCarrierControls = false;
        }
    }

    _decisionContextPathCount(decision) {
        if (!decision || typeof decision !== 'object')
            return 0;
        const paths = decision.context_paths;
        return Array.isArray(paths) ? paths.length : 0;
    }

    _renderQuestionsPage(status) {
        this._questionsHostItem.clear();
        const decisions = this._safeSection(status, 'decisions');
        if (!decisions) {
            const label = new St.Label({text: 'Decision queue unavailable', style_class: 'ion-helixion-group-detail'});
            this._questionsHostItem.addActor(label);
            return;
        }

        const pending = Array.isArray(decisions.pending) ? decisions.pending.slice(0, 10) : [];
        if (pending.length === 0) {
            const label = new St.Label({text: 'No pending questions.', style_class: 'ion-helixion-group-detail'});
            this._questionsHostItem.addActor(label);
        }

        for (const row of pending) {
            if (!row || typeof row !== 'object' || !row.id) {
                const badId = row && row.id ? String(row.id) : 'unknown';
                const label = new St.Label({text: `${badId} unrenderable`, style_class: 'ion-helixion-warn'});
                this._questionsHostItem.addActor(label);
                continue;
            }
            if (typeof row.question !== 'string' || !row.question) {
                const label = new St.Label({text: `${row.id} unrenderable`, style_class: 'ion-helixion-warn'});
                this._questionsHostItem.addActor(label);
                continue;
            }

            const block = new St.BoxLayout({vertical: true, style_class: 'ion-helixion-question-block'});
            const category = row.category || 'general';
            const from = row.from || 'unknown';
            const header = new St.Label({
                text: `[${category}] from ${from}`,
                style_class: 'ion-helixion-group-detail',
            });
            const question = new St.Label({
                text: row.question,
                style_class: 'ion-helixion-question',
            });
            question.clutter_text.set_line_wrap(true);
            const pathCount = this._decisionContextPathCount(row);
            const expiry = this._formatTime(row.expires_at);
            const meta = new St.Label({
                text: `context paths: ${pathCount} · expires ${expiry}`,
                style_class: 'ion-helixion-group-detail',
            });
            block.add_child(header);
            block.add_child(question);
            block.add_child(meta);

            const buttonRow = new St.BoxLayout({style_class: 'ion-helixion-question-actions'});
            const acceptBtn = new St.Button({label: 'Accept', style_class: 'ion-helixion-question-btn'});
            const denyBtn = new St.Button({label: 'Deny', style_class: 'ion-helixion-question-btn'});
            const replyBtn = new St.Button({label: 'Reply…', style_class: 'ion-helixion-question-btn'});
            const decisionId = String(row.id);
            const categoryCopy = String(category);
            acceptBtn.connect('clicked', () => {
                this._lastAcceptedCategory = categoryCopy;
                this._onDecisionAction('decision-accept', decisionId);
            });
            denyBtn.connect('clicked', () => this._onDecisionAction('decision-deny', decisionId));
            replyBtn.connect('clicked', () => {
                this._replyOpenDecisionId = this._replyOpenDecisionId === decisionId ? null : decisionId;
                this._renderQuestionsPage(this._lastStatus);
            });
            buttonRow.add_child(acceptBtn);
            buttonRow.add_child(denyBtn);
            buttonRow.add_child(replyBtn);
            block.add_child(buttonRow);

            if (this._replyOpenDecisionId === decisionId) {
                const replyRow = new St.BoxLayout({style_class: 'ion-helixion-reply-row'});
                const entry = new St.Entry({can_focus: true, x_expand: true});
                entry.clutter_text.set_max_length(REPLY_MAX_CHARS);
                const sendBtn = new St.Button({label: 'Send', style_class: 'ion-helixion-question-btn'});
                sendBtn.connect('clicked', () => {
                    const text = entry.get_text();
                    this._onDecisionAction('decision-reply', decisionId, text);
                });
                replyRow.add_child(entry);
                replyRow.add_child(sendBtn);
                block.add_child(replyRow);
            }

            this._questionsHostItem.addActor(block);
        }

        if (this._pushAuthorizationReady) {
            const pushRow = new St.BoxLayout({style_class: 'ion-helixion-push-row'});
            const pushBtn = new St.Button({label: 'Push now', style_class: 'ion-helixion-question-btn'});
            pushBtn.connect('clicked', () => this._onPushReceipted());
            pushRow.add_child(pushBtn);
            this._questionsHostItem.addActor(pushRow);
        }
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

        this._renderStatusConnectionLines(status);

        const instances = status.instances || {};
        this._instancesItem.label.set_text(
            `PC-backed processes: ${instances.local_process_count || 0} local · ${instances.cloudflared_tunnel_count || 0} tunnels`
        );

        this._renderQueueSection(status);
        this._renderAgentsSection(status);
        this._renderAttentionSection(status);
        this._renderCarriersSection(status);
        this._renderQuestionsPage(status);
        this._updatePanelBadge(status);
        this._updateTabLabels(status);
        this._pickDefaultPage(status);

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
        this._attentionCarrierItem.hide();
        this._questionsHostItem.clear();
        const label = new St.Label({text: 'Decision queue unavailable', style_class: 'ion-helixion-group-detail'});
        this._questionsHostItem.addActor(label);
        for (const groupId of GROUP_IDS)
            this._statusConnectionItems[groupId].label.set_text(`${GROUP_LABELS[groupId]}: unknown`);
        this._panelLabel.set_text('ION');
        this._panelWarnBadge.set_text('');
        this._panelRunBadge.set_text('');
        this._panelQuestionBadge.set_text('');
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
        this._updateTabLabels({});
        this._tabBarItem.setTabLabel('questions', 'Questions');
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
