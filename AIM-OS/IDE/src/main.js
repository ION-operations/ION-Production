// AIM-OS JOC — Joint Operations Center
// Main Controller: tabs, service monitoring, credential vault, SEER controls

// ─── Tauri IPC ──────────────────────────────────────────────
const invoke = window.__TAURI__
    ? window.__TAURI__.invoke
    : async (cmd, args) => {
        console.log(`[JOC] Tauri not available, stub: ${cmd}`, args);
        return { success: false, data: null };
    };

const { listen, emit } = window.__TAURI__ ? window.__TAURI__.event : { 
    listen: async () => () => { },
    emit: async () => { }
};

// ─── Config ─────────────────────────────────────────────────
const CONFIG = {
    BAS_URL: 'http://localhost:5002',
    MCP_SSE_URL: 'http://localhost:5001',
    JOC_URL: 'http://localhost:5011',
    POLL_INTERVAL: 5000,
    FAST_POLL: 2000,
};

// ─── DOM Helpers ────────────────────────────────────────────
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

// ─── Service Definitions ────────────────────────────────────
const SERVICES = [
    {
        id: 'mcp-lucid',
        name: 'MCP Server',
        description: 'lucid-mcp — 92 tools via stdio',
        port: 'stdio',
        healthUrl: null,
        type: 'mcp',
        icon: '◇',
        startCmd: null, // Managed by Antigravity IDE
    },
    {
        id: 'mcp-sse',
        name: 'MCP SSE Bridge',
        description: 'SSE transport for ChatGPT MCP',
        port: 5001,
        healthUrl: `${CONFIG.MCP_SSE_URL}/health`,
        type: 'http',
        icon: '⇄',
        startCmd: 'python scripts/mcp_sse_server.py',
    },
    {
        id: 'bas',
        name: 'BAS Server',
        description: 'Browser Automation + Credential Vault',
        port: 5002,
        healthUrl: `${CONFIG.BAS_URL}/health`,
        type: 'http',
        icon: '⚙',
        startCmd: 'cd packages/browser-automation-service && npm start',
    },
    {
        id: 'gemini-ext',
        name: 'Gemini Extension',
        description: 'Chrome bridge → Gemini via native messaging',
        port: null,
        healthUrl: null,
        type: 'extension',
        icon: '✦',
        startCmd: null,
    },
    {
        id: 'chatgpt-mcp',
        name: 'ChatGPT MCP',
        description: 'Native MCP connection via SSE/ngrok',
        port: null,
        healthUrl: null,
        type: 'mcp-remote',
        icon: '⬡',
        startCmd: null,
    },
    {
        id: 'seer',
        name: 'SEER Engine',
        description: 'Desktop vision + automation (32 MCP tools)',
        port: null,
        healthUrl: null,
        type: 'python',
        icon: '👁',
        startCmd: 'python scripts/seer/test_seer.py',
    },
];

// ═══════════════════════════════════════════════════════════
// TAB SYSTEM
// ═══════════════════════════════════════════════════════════

function initTabs() {
    $$('.tab').forEach(tab => {
        tab.addEventListener('click', () => {
            const targetId = tab.dataset.tab;

            // Update tab buttons
            $$('.tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            // Update tab content
            $$('.tab-content').forEach(c => c.classList.remove('active'));
            const target = $(`#tab-${targetId}`);
            if (target) target.classList.add('active');

            // Tab-specific actions
            if (targetId === 'services') refreshAllServices();
            if (targetId === 'vault') refreshVault();
        });
    });
}

// ═══════════════════════════════════════════════════════════
// SERVICE MONITOR
// ═══════════════════════════════════════════════════════════

const serviceStatus = {};

function createServiceCard(service) {
    const status = serviceStatus[service.id] || { state: 'unknown', latency: null };
    const stateClass = {
        'online': 'svc-online',
        'offline': 'svc-offline',
        'unknown': 'svc-unknown',
        'checking': 'svc-checking',
    }[status.state] || 'svc-unknown';

    return `
        <div class="service-card ${stateClass}" data-service="${service.id}">
            <div class="svc-header">
                <span class="svc-icon">${service.icon}</span>
                <div class="svc-info">
                    <span class="svc-name">${service.name}</span>
                    <span class="svc-desc">${service.description}</span>
                </div>
                <div class="svc-status-wrap">
                    <span class="svc-dot"></span>
                    <span class="svc-state">${status.state.toUpperCase()}</span>
                </div>
            </div>
            <div class="svc-details">
                ${service.port ? `<span class="svc-detail">Port: ${service.port}</span>` : ''}
                ${status.latency ? `<span class="svc-detail">Latency: ${status.latency}ms</span>` : ''}
                ${status.lastCheck ? `<span class="svc-detail">Last: ${formatTime(status.lastCheck)}</span>` : ''}
            </div>
            <div class="svc-actions">
                <button class="btn btn-sm btn-ghost" onclick="checkService('${service.id}')">↻ Check</button>
                ${service.startCmd ? `<button class="btn btn-sm" onclick="startService('${service.id}')">▸ Start</button>` : ''}
                ${service.healthUrl ? `<button class="btn btn-sm" onclick="openServiceUrl('${service.healthUrl}')">🔗 Health</button>` : ''}
            </div>
        </div>
    `;
}

function renderServices() {
    const grid = $('#services-grid');
    if (!grid) return;
    grid.innerHTML = SERVICES.map(createServiceCard).join('');
}

function renderDashServiceList() {
    const list = $('#dash-service-list');
    if (!list) return;
    list.innerHTML = SERVICES.map(svc => {
        const status = serviceStatus[svc.id] || { state: 'unknown' };
        const dotClass = {
            'online': 'dot-green',
            'offline': 'dot-red',
            'unknown': 'dot-muted',
        }[status.state] || 'dot-muted';
        return `
            <div class="dash-service-item">
                <span class="activity-dot ${dotClass}"></span>
                <span class="dash-svc-name">${svc.name}</span>
                <span class="dash-svc-state">${status.state}</span>
            </div>
        `;
    }).join('');
}

async function checkService(serviceId) {
    const service = SERVICES.find(s => s.id === serviceId);
    if (!service) return;

    serviceStatus[serviceId] = { state: 'checking', lastCheck: Date.now() };
    renderServices();

    if (service.healthUrl) {
        try {
            const start = performance.now();
            const res = await fetch(service.healthUrl, {
                signal: AbortSignal.timeout(5000)
            });
            const latency = Math.round(performance.now() - start);

            if (res.ok) {
                const data = await res.json().catch(() => ({}));
                serviceStatus[serviceId] = {
                    state: 'online',
                    latency,
                    lastCheck: Date.now(),
                    data
                };
            } else {
                serviceStatus[serviceId] = {
                    state: 'offline',
                    lastCheck: Date.now(),
                    error: `HTTP ${res.status}`
                };
            }
        } catch (e) {
            serviceStatus[serviceId] = {
                state: 'offline',
                lastCheck: Date.now(),
                error: e.message
            };
        }
    } else {
        // For non-HTTP services, mark as unknown (needs deeper check)
        serviceStatus[serviceId] = {
            state: 'unknown',
            lastCheck: Date.now()
        };
    }

    renderServices();
    renderDashServiceList();
    updateDashboard();
}

async function refreshAllServices() {
    logToConsole('Refreshing all services...', 'system');
    for (const svc of SERVICES) {
        await checkService(svc.id);
    }
    logToConsole(`Service check complete: ${Object.values(serviceStatus).filter(s => s.state === 'online').length}/${SERVICES.length} online`, 'success');
}

async function startService(serviceId) {
    const service = SERVICES.find(s => s.id === serviceId);
    if (!service || !service.startCmd) return;

    logToConsole(`Starting ${service.name}...`, 'command');
    try {
        await invoke('run_command', { command: service.startCmd });
        logToConsole(`${service.name} start command sent`, 'success');
        // Check after a delay
        setTimeout(() => checkService(serviceId), 3000);
    } catch (e) {
        logToConsole(`Failed to start ${service.name}: ${e}`, 'error');
    }
}

function openServiceUrl(url) {
    window.open(url, '_blank');
}

// ═══════════════════════════════════════════════════════════
// CREDENTIAL VAULT
// ═══════════════════════════════════════════════════════════

let vaultCredentials = [];

async function refreshVault() {
    try {
        const res = await fetch(`${CONFIG.BAS_URL}/api/connections/vault`, {
            signal: AbortSignal.timeout(5000)
        });
        if (res.ok) {
            const data = await res.json();
            vaultCredentials = data.credentials || data || [];
            renderVault();
            updateDashboard();
        } else {
            renderVaultError('BAS server returned error. Is it running?');
        }
    } catch (e) {
        renderVaultError('Cannot connect to BAS (port 5002). Start the BAS server first.');
    }
}

function renderVault() {
    const list = $('#vault-list');
    if (!list) return;

    if (!vaultCredentials.length) {
        list.innerHTML = `
            <div class="vault-empty">
                <p>No credentials stored.</p>
                <p class="hint">Add API keys, tokens, and service credentials.</p>
            </div>
        `;
        return;
    }

    list.innerHTML = vaultCredentials.map(cred => `
        <div class="vault-cred-card" data-id="${cred.id}">
            <div class="vault-cred-header">
                <div class="vault-cred-info">
                    <span class="vault-cred-provider">${cred.provider}</span>
                    <span class="vault-cred-label">${cred.label}</span>
                </div>
                <div class="vault-cred-meta">
                    ${cred.usernameHint ? `<span class="vault-hint">${cred.usernameHint}</span>` : ''}
                    <span class="vault-date">${formatDate(cred.createdAt)}</span>
                </div>
            </div>
            <div class="vault-cred-actions">
                <button class="btn btn-sm btn-ghost" onclick="deleteCredential('${cred.id}')">🗑 Delete</button>
            </div>
        </div>
    `).join('');
}

function renderVaultError(message) {
    const list = $('#vault-list');
    if (!list) return;
    list.innerHTML = `
        <div class="vault-error">
            <span class="vault-error-icon">⚠</span>
            <p>${message}</p>
        </div>
    `;
}

async function addCredential() {
    const provider = $('#vault-provider').value;
    const label = $('#vault-label').value;
    const apiKey = $('#vault-api-key').value;
    const email = $('#vault-email').value;
    const limitHour = $('#vault-limit-hour').value;
    const limitDay = $('#vault-limit-day').value;

    if (!label || !apiKey) {
        logToConsole('Label and API key are required', 'error');
        return;
    }

    try {
        const body = {
            provider,
            label,
            secret: {
                apiKey,
                ...(email && { email }),
            },
            metadata: {
                ...(limitHour && { maxCallsPerHour: parseInt(limitHour) }),
                ...(limitDay && { maxCallsPerDay: parseInt(limitDay) }),
            },
        };

        const res = await fetch(`${CONFIG.BAS_URL}/api/connections/vault`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });

        if (res.ok) {
            logToConsole(`Credential "${label}" saved to vault`, 'success');
            closeModal('modal-add-credential');
            clearVaultForm();
            refreshVault();
        } else {
            const err = await res.json().catch(() => ({}));
            logToConsole(`Vault error: ${err.error || 'Unknown'}`, 'error');
        }
    } catch (e) {
        logToConsole(`Cannot save credential: ${e.message}`, 'error');
    }
}

async function deleteCredential(id) {
    if (!confirm('Delete this credential? This cannot be undone.')) return;

    try {
        const res = await fetch(`${CONFIG.BAS_URL}/api/connections/vault/${id}`, {
            method: 'DELETE',
        });
        if (res.ok) {
            logToConsole('Credential deleted', 'success');
            refreshVault();
        }
    } catch (e) {
        logToConsole(`Delete failed: ${e.message}`, 'error');
    }
}

function clearVaultForm() {
    $('#vault-provider').value = 'gemini';
    $('#vault-label').value = '';
    $('#vault-api-key').value = '';
    $('#vault-email').value = '';
    $('#vault-limit-hour').value = '';
    $('#vault-limit-day').value = '';
}

// ═══════════════════════════════════════════════════════════
// DASHBOARD
// ═══════════════════════════════════════════════════════════

function updateDashboard() {
    const online = Object.values(serviceStatus).filter(s => s.state === 'online').length;
    const dashUp = $('#dash-services-up');
    if (dashUp) dashUp.textContent = online;

    const dashKeys = $('#dash-vault-keys');
    if (dashKeys) dashKeys.textContent = vaultCredentials.length;
}

// ═══════════════════════════════════════════════════════════
// CONSOLE
// ═══════════════════════════════════════════════════════════

function logToConsole(message, type = 'system') {
    const output = $('#console-output');
    if (!output) return;

    const now = new Date();
    const timestamp = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;

    const line = document.createElement('div');
    line.className = `console-line ${type}`;
    line.innerHTML = `
        <span class="timestamp">[${timestamp}]</span>
        <span class="message">${escapeHtml(message)}</span>
    `;
    output.appendChild(line);
    output.scrollTop = output.scrollHeight;
    
    // Also add to dashboard activity
    addActivity(message, type);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

async function handleCommand(input) {
    const trimmed = input.trim();
    if (!trimmed) return;
    
    logToConsole(trimmed, 'command');

    // Built-in commands
    const lower = trimmed.toLowerCase();
    if (lower === 'help') {
        logToConsole('Commands: status, services, vault, clear, kill', 'response');
    } else if (lower === 'status') {
        refreshAllServices();
    } else if (lower === 'services') {
        $$('.tab')[1].click(); // Switch to services tab
    } else if (lower === 'vault') {
        $$('.tab')[4].click(); // Switch to vault tab
    } else if (lower === 'clear') {
        const output = $('#console-output');
        if (output) output.innerHTML = '';
    } else if (lower === 'kill') {
        try {
            await invoke('kill_all');
            logToConsole('Kill switch activated', 'error');
        } catch (e) {
            logToConsole(`Kill failed: ${e}`, 'error');
        }
    } else {
        // Forward to Tauri backend
        try {
            const result = await invoke('handle_command', { command: trimmed });
            if (result && result.data) {
                logToConsole(result.data, 'response');
            }
        } catch (e) {
            logToConsole(`Command error: ${e}`, 'error');
        }
    }
}

// ═══════════════════════════════════════════════════════════
// ACTIVITY FEED
// ═══════════════════════════════════════════════════════════

function addActivity(text, type = 'system') {
    const feed = $('#dash-activity');
    if (!feed) return;

    const dotClass = {
        'system': 'dot-cyan',
        'success': 'dot-green',
        'error': 'dot-red',
        'command': 'dot-amber',
    }[type] || 'dot-cyan';

    const item = document.createElement('div');
    item.className = 'activity-item';
    item.innerHTML = `
        <span class="activity-dot ${dotClass}"></span>
        <span class="activity-text">${escapeHtml(text)}</span>
        <span class="activity-time">now</span>
    `;

    // Insert at top
    feed.insertBefore(item, feed.firstChild);

    // Keep max 20 items
    while (feed.children.length > 20) {
        feed.removeChild(feed.lastChild);
    }
}

// ═══════════════════════════════════════════════════════════
// MODALS
// ═══════════════════════════════════════════════════════════

function openModal(id) {
    const modal = $(`#${id}`);
    if (modal) modal.classList.remove('hidden');
}

function closeModal(id) {
    const modal = $(`#${id}`);
    if (modal) modal.classList.add('hidden');
}

// ═══════════════════════════════════════════════════════════
// WEBVIEW MANAGEMENT (Agent Fleet)
// ═══════════════════════════════════════════════════════════

async function deployWebview() {
    const id = $('#input-webview-id')?.value?.trim();
    const providerSelect = $('#select-provider');
    const customUrl = $('#input-custom-url')?.value?.trim();
    const role = $('#select-role')?.value;

    const url = providerSelect.value === 'custom' ? customUrl : providerSelect.value;
    
    if (!id || !url) {
        logToConsole('Agent ID and URL are required', 'error');
        return;
    }

    logToConsole(`Deploying agent: ${id} → ${url}`, 'command');

    try {
        const result = await invoke('deploy_webview', { id, url, role });
        logToConsole(`Agent ${id} deployed`, 'success');
        closeModal('modal-add-webview');
            updateAgentCount();
    } catch (e) {
        logToConsole(`Deploy failed: ${e}`, 'error');
    }
}

function addWebviewCard(id, url, role) {
    const list = $('#webview-list');
    if (!list) return;

    // Remove empty state
    const empty = list.querySelector('.fleet-empty');
    if (empty) empty.remove();
    
    const card = document.createElement('div');
    card.className = 'fleet-card';
    card.innerHTML = `
        <div class="fleet-card-header">
            <span class="fleet-card-id">${escapeHtml(id)}</span>
            <span class="fleet-card-role">${escapeHtml(role)}</span>
        </div>
        <div class="fleet-card-url">${escapeHtml(url)}</div>
    `;
    list.appendChild(card);
}

async function updateAgentCount() {
    try {
        const result = await invoke('get_status');
        if (result.data) {
            const status = JSON.parse(result.data);
            const dashAgents = $('#dash-agents-active');
            if (dashAgents) dashAgents.textContent = status.webviews || 0;
        }
    } catch (e) { /* silent */ }
}

// ═══════════════════════════════════════════════════════════
// UTILITIES
// ═══════════════════════════════════════════════════════════

function formatTime(timestamp) {
    if (!timestamp) return '';
    const d = new Date(timestamp);
    return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}:${d.getSeconds().toString().padStart(2, '0')}`;
}

function formatDate(dateStr) {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

// ═══════════════════════════════════════════════════════════
// STATE UPDATES (from Tauri IPC)
// ═══════════════════════════════════════════════════════════

function updateState(state) {
    const indicator = $('#state-indicator');
    if (!indicator) return;

    // Remove all state classes
    indicator.className = 'state-badge';

    const stateMap = {
        idle: 'state-idle',
        inject: 'state-active',
        wait: 'state-active',
        parse: 'state-active',
        execute: 'state-executing',
        verify: 'state-executing',
        killed: 'state-killed',
    };

    const stateClass = stateMap[state.toLowerCase()] || 'state-idle';
    indicator.classList.add(stateClass);

    const text = indicator.querySelector('.state-text');
    if (text) text.textContent = state.toUpperCase();
}

// ═══════════════════════════════════════════════════════════
// EVENT LISTENERS
// ═══════════════════════════════════════════════════════════

function initEventListeners() {
// Console input
    const consoleInput = $('#console-input');
    if (consoleInput) {
        consoleInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
                handleCommand(consoleInput.value);
                consoleInput.value = '';
            }
        });
    }

    // Console buttons
    $('#btn-send')?.addEventListener('click', () => {
        if (consoleInput) {
            handleCommand(consoleInput.value);
            consoleInput.value = '';
        }
    });

    $('#btn-clear')?.addEventListener('click', () => {
        const output = $('#console-output');
        if (output) output.innerHTML = '';
});

// Kill switch
    $('#btn-kill')?.addEventListener('click', async () => {
        try {
            await invoke('kill_all');
            updateState('killed');
            logToConsole('KILL SWITCH ACTIVATED', 'error');
    } catch (e) {
            logToConsole(`Kill failed: ${e}`, 'error');
        }
    });

    // Status button
    $('#btn-status')?.addEventListener('click', () => {
        refreshAllServices();
    });

    // Service refresh
    $('#btn-refresh-all')?.addEventListener('click', refreshAllServices);

    // Webview modal
    $('#btn-add-webview')?.addEventListener('click', () => openModal('modal-add-webview'));
    $('#btn-modal-cancel')?.addEventListener('click', () => closeModal('modal-add-webview'));
    $('#btn-modal-deploy')?.addEventListener('click', deployWebview);

// Provider select  
    $('#select-provider')?.addEventListener('change', (e) => {
        const customGroup = $('#custom-url-group');
        if (customGroup) {
    if (e.target.value === 'custom') {
                customGroup.classList.remove('hidden');
    } else {
                customGroup.classList.add('hidden');
            }
        }
    });

    // Vault modal
    $('#btn-vault-add')?.addEventListener('click', () => openModal('modal-add-credential'));
    $('#btn-vault-cancel')?.addEventListener('click', () => closeModal('modal-add-credential'));
    $('#btn-vault-save')?.addEventListener('click', addCredential);
    $('#btn-vault-refresh')?.addEventListener('click', refreshVault);

    // Modal backdrop close
    $$('.modal-backdrop').forEach(backdrop => {
        backdrop.addEventListener('click', () => {
            backdrop.closest('.modal')?.classList.add('hidden');
        });
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.shiftKey && e.key === 'F12') {
            e.preventDefault();
            invoke('kill_all').catch(() => { });
            updateState('killed');
        }
    });

    // Tauri events
    listen('webview-created', (event) => {
        const { id, url, role } = event.payload;
        addWebviewCard(id, url, role);
        logToConsole(`Agent ${id} online`, 'success');
        updateAgentCount();
    });

    listen('state-changed', (event) => {
        updateState(event.payload.state);
    });

    listen('console-log', (event) => {
        logToConsole(event.payload.message, event.payload.type || 'system');
    });
}

// ═══════════════════════════════════════════════════════════
// INITIALIZATION
// ═══════════════════════════════════════════════════════════

function init() {
    initTabs();
    initEventListeners();
    renderServices();
    renderDashServiceList();

    logToConsole('AIM-OS JOC v2.0 initialized', 'system');
    logToConsole('Checking services...', 'system');

    // Initial service check
    setTimeout(refreshAllServices, 1000);

    // Periodic polling
    setInterval(async () => {
        // Only poll HTTP services silently
        for (const svc of SERVICES.filter(s => s.healthUrl)) {
            await checkService(svc.id);
        }
    }, CONFIG.POLL_INTERVAL);

    // Poll Tauri status
setInterval(async () => {
    try {
        const result = await invoke('get_status');
        if (result.data) {
            const status = JSON.parse(result.data);
            if (status.state) updateState(status.state.replace(/"/g, ''));
                if (status.webviews !== undefined) {
                    const dashAgents = $('#dash-agents-active');
                    if (dashAgents) dashAgents.textContent = status.webviews;
                }
        }
        } catch (e) { /* silent */ }
    }, CONFIG.FAST_POLL);
    }

// Boot
init();
