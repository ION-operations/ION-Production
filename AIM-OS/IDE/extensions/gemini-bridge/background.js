/**
 * AIM-OS Gemini Bridge — Background Service Worker
 *
 * Manages the Native Messaging connection to the local aimos_bridge host.
 * Receives MCP-CALL payloads from the content script, forwards to the
 * native host, and relays results back.
 */

const NATIVE_HOST_NAME = 'aimos_bridge';

let nativePort = null;
let pendingRequests = new Map(); // requestId -> { tabId, resolve }
let requestCounter = 0;
let connectionState = 'disconnected'; // disconnected | connected | error
let stats = { totalCalls: 0, lastTool: null, lastTimestamp: null, errors: 0 };

// ── Native Messaging Connection ────────────────────────────────────

function connectNative() {
    if (nativePort) {
        try { nativePort.disconnect(); } catch (_) { }
    }

    try {
        nativePort = chrome.runtime.connectNative(NATIVE_HOST_NAME);
        connectionState = 'connected';
        console.log('[AIM-OS Bridge] Native host connected');

        nativePort.onMessage.addListener((message) => {
            console.log('[AIM-OS Bridge] Native response:', message);
            handleNativeResponse(message);
        });

        nativePort.onDisconnect.addListener(() => {
            const error = chrome.runtime.lastError;
            console.warn('[AIM-OS Bridge] Native host disconnected:', error?.message || 'unknown');
            connectionState = 'disconnected';
            nativePort = null;

            // Reject all pending requests
            for (const [reqId, pending] of pendingRequests) {
                sendToTab(pending.tabId, {
                    type: 'TOOL_RESULT',
                    requestId: reqId,
                    success: false,
                    error: 'Native host disconnected'
                });
            }
            pendingRequests.clear();

            // Broadcast disconnect to all tabs
            broadcastState();
        });

        broadcastState();
    } catch (err) {
        console.error('[AIM-OS Bridge] Failed to connect:', err);
        connectionState = 'error';
        broadcastState();
    }
}

function handleNativeResponse(message) {
    const { requestId, result, error } = message;

    if (!requestId || !pendingRequests.has(requestId)) {
        console.warn('[AIM-OS Bridge] Unknown requestId:', requestId);
        return;
    }

    const pending = pendingRequests.get(requestId);
    pendingRequests.delete(requestId);

    if (error) {
        stats.errors++;
        sendToTab(pending.tabId, {
            type: 'TOOL_RESULT',
            requestId,
            success: false,
            error
        });
    } else {
        sendToTab(pending.tabId, {
            type: 'TOOL_RESULT',
            requestId,
            success: true,
            result
        });
    }
}

// ── Message Routing ────────────────────────────────────────────────

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    const { type } = message;

    if (type === 'MCP_CALL') {
        handleToolCall(message, sender.tab?.id);
        sendResponse({ received: true });
        return true;
    }

    if (type === 'GET_STATE') {
        sendResponse({
            connectionState,
            stats
        });
        return true;
    }

    if (type === 'RECONNECT') {
        connectNative();
        sendResponse({ connectionState });
        return true;
    }

    return false;
});

// ── Arg Normalization ──────────────────────────────────────────────

const ARG_NORMALIZATIONS = {
    'send_ai_message': { to: 'to_ai', from: 'from_ai', message: 'content', msg: 'content' },
    'get_ai_messages': { to: 'to_ai', from: 'from_ai' },
    'store_memory': { data: 'content', text: 'content' },
};

function normalizeArgs(tool, args) {
    const map = ARG_NORMALIZATIONS[tool];
    if (!map || !args) return args;

    const normalized = { ...args };
    for (const [wrong, correct] of Object.entries(map)) {
        if (wrong in normalized && !(correct in normalized)) {
            normalized[correct] = normalized[wrong];
            delete normalized[wrong];
            console.log(`[AIM-OS Bridge] Normalized arg: ${wrong} → ${correct} for ${tool}`);
        }
    }
    return normalized;
}

function handleToolCall(message, tabId) {
    const { tool, args } = message;

    // Route SEER tools locally (they use Chrome extension APIs, not the native host)
    if (tool.startsWith('seer_')) {
        const requestId = `req_${++requestCounter}_${Date.now()}`;
        stats.totalCalls++;
        stats.lastTool = tool;
        stats.lastTimestamp = new Date().toISOString();
        console.log(`[SEER] Handling locally: ${tool}`, args);
        handleSeerTool(tool, args || {}, requestId);
        return;
    }

    if (!nativePort || connectionState !== 'connected') {
        // Try to reconnect
        connectNative();
        if (connectionState !== 'connected') {
            sendToTab(tabId, {
                type: 'TOOL_RESULT',
                requestId: message.requestId,
                success: false,
                error: 'Native host not connected. Check that install_native_host.ps1 was run.'
            });
            return;
        }
    }

    // Normalize args to fix common Gemini naming mistakes
    const normalizedArgs = normalizeArgs(tool, args || {});

    const requestId = `req_${++requestCounter}_${Date.now()}`;
    pendingRequests.set(requestId, { tabId });

    stats.totalCalls++;
    stats.lastTool = tool;
    stats.lastTimestamp = new Date().toISOString();

    const payload = {
        requestId,
        tool,
        args: normalizedArgs
    };

    console.log('[AIM-OS Bridge] Sending to native:', payload);

    try {
        nativePort.postMessage(payload);
    } catch (err) {
        console.error('[AIM-OS Bridge] Send failed:', err);
        pendingRequests.delete(requestId);
        stats.errors++;
        sendToTab(tabId, {
            type: 'TOOL_RESULT',
            requestId,
            success: false,
            error: `Send failed: ${err.message}`
        });
    }
}

function sendToTab(tabId, message) {
    if (!tabId) return;
    try {
        chrome.tabs.sendMessage(tabId, message);
    } catch (_) { }
}

function broadcastState() {
    chrome.runtime.sendMessage({
        type: 'STATE_UPDATE',
        connectionState,
        stats
    }).catch(() => { });
}

// ── SEER: Spatial Vision Subsystem ────────────────────────────────

/**
 * Get spatial map from a tab's SEER mapper.
 * @param {number} tabId - Target tab ID (uses active tab if not specified)
 * @param {object} options - Mapper options (includeHidden, etc.)
 * @returns {Promise<object>} Spatial map with page meta + elements
 */
async function seerGetMap(tabId, options = {}) {
    const targetTabId = tabId || (await getActiveTabId());
    if (!targetTabId) throw new Error('No active tab found');

    return new Promise((resolve, reject) => {
        chrome.tabs.sendMessage(targetTabId, {
            type: 'SEER_GET_MAP',
            options
        }, (response) => {
            if (chrome.runtime.lastError) {
                reject(new Error(`SEER not active on tab ${targetTabId}: ${chrome.runtime.lastError.message}`));
                return;
            }
            resolve(response);
        });
    });
}

/**
 * Capture a micro-crop from a tab.
 * Uses captureVisibleTab + OffscreenCanvas to crop to bounding box.
 * @param {number} tabId - Target tab ID
 * @param {object} rect - { x, y, width, height } in viewport coordinates
 * @returns {Promise<string>} Base64 PNG of the cropped region
 */
async function seerMicroCrop(tabId, rect) {
    const targetTabId = tabId || (await getActiveTabId());
    if (!targetTabId) throw new Error('No active tab found');

    // Get the tab's window for capture
    const tab = await chrome.tabs.get(targetTabId);

    // Capture the full visible tab
    const dataUrl = await chrome.tabs.captureVisibleTab(tab.windowId, {
        format: 'png'
    });

    // Crop using OffscreenCanvas
    const response = await fetch(dataUrl);
    const blob = await response.blob();
    const imageBitmap = await createImageBitmap(blob);

    // Account for device pixel ratio
    const dpr = tab.devicePixelRatio || 1;
    const sx = Math.round(rect.x * dpr);
    const sy = Math.round(rect.y * dpr);
    const sw = Math.round(rect.width * dpr);
    const sh = Math.round(rect.height * dpr);

    // Create OffscreenCanvas and crop
    const canvas = new OffscreenCanvas(sw, sh);
    const ctx = canvas.getContext('2d');
    ctx.drawImage(imageBitmap, sx, sy, sw, sh, 0, 0, sw, sh);

    // Convert to base64
    const croppedBlob = await canvas.convertToBlob({ type: 'image/png' });
    const reader = new FileReader();

    return new Promise((resolve) => {
        reader.onloadend = () => resolve(reader.result);
        reader.readAsDataURL(croppedBlob);
    });
}

/**
 * List all pages where SEER is active.
 * Pings all tabs and returns those that respond.
 */
async function seerListPages() {
    const tabs = await chrome.tabs.query({});
    const pages = [];

    const pingPromises = tabs.map(tab => {
        return new Promise((resolve) => {
            chrome.tabs.sendMessage(tab.id, { type: 'SEER_PING' }, (response) => {
                if (!chrome.runtime.lastError && response?.alive) {
                    pages.push({
                        tabId: tab.id,
                        url: response.url,
                        title: response.title,
                        active: tab.active,
                        windowId: tab.windowId
                    });
                }
                resolve();
            });
        });
    });

    await Promise.all(pingPromises);
    return pages;
}

async function getActiveTabId() {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    return tab?.id;
}

/**
 * Handle SEER tool calls from the native host.
 * These are routed just like bridge MCP tools but handled locally in the extension.
 */
async function handleSeerTool(tool, args, requestId) {
    try {
        let result;

        switch (tool) {
            case 'seer_get_spatial_map': {
                result = await seerGetMap(args.tab_id, {
                    includeHidden: args.include_hidden || false
                });
                break;
            }
            case 'seer_micro_crop': {
                const base64 = await seerMicroCrop(args.tab_id, {
                    x: args.x || 0,
                    y: args.y || 0,
                    width: args.width || 200,
                    height: args.height || 200
                });
                result = {
                    success: true,
                    image: base64,
                    rect: { x: args.x, y: args.y, width: args.width, height: args.height }
                };
                break;
            }
            case 'seer_list_pages': {
                const pages = await seerListPages();
                result = {
                    success: true,
                    pages,
                    count: pages.length
                };
                break;
            }
            default:
                return false; // Not a SEER tool
        }

        // Send result back through native host
        if (nativePort && connectionState === 'connected') {
            nativePort.postMessage({
                requestId,
                result: { success: true, tool, ...result }
            });
        }

        return true;
    } catch (err) {
        console.error(`[SEER] Error in ${tool}:`, err);
        if (nativePort && connectionState === 'connected') {
            nativePort.postMessage({
                requestId,
                result: { success: false, error: err.message }
            });
        }
        return true;
    }
}

// ── Lifecycle ──────────────────────────────────────────────────────

// Auto-connect on extension load
connectNative();

// Keep-alive for Manifest V3 service worker
chrome.alarms.create('keepalive', { periodInMinutes: 0.4 });
chrome.alarms.onAlarm.addListener((alarm) => {
    if (alarm.name === 'keepalive') {
        // Ping native host if connected to keep the connection alive
        if (nativePort && connectionState === 'connected') {
            try {
                nativePort.postMessage({ type: 'ping' });
            } catch (_) {
                connectionState = 'disconnected';
                nativePort = null;
            }
        }
    }
});
