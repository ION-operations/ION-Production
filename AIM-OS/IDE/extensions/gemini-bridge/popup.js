/**
 * AIM-OS Gemini Bridge — Popup Script
 *
 * Controls the extension popup UI: shows connection state,
 * tool call stats, and provides reconnect functionality.
 */

document.addEventListener('DOMContentLoaded', () => {
    const statusDot = document.getElementById('statusDot');
    const statusLabel = document.getElementById('statusLabel');
    const statusDetail = document.getElementById('statusDetail');
    const totalCalls = document.getElementById('totalCalls');
    const lastTool = document.getElementById('lastTool');
    const errorCount = document.getElementById('errorCount');
    const lastTimestamp = document.getElementById('lastTimestamp');
    const reconnectBtn = document.getElementById('reconnectBtn');

    function updateUI(state, stats) {
        // Status dot
        statusDot.className = 'status-dot ' + (state === 'connected' ? 'connected' : 'disconnected');

        // Labels
        if (state === 'connected') {
            statusLabel.textContent = 'Connected';
            statusDetail.textContent = 'Native host active — listening for MCP-CALL blocks';
        } else {
            statusLabel.textContent = 'Disconnected';
            statusDetail.textContent = 'Click Reconnect or check native host installation';
        }

        // Stats
        if (stats) {
            totalCalls.textContent = stats.totalCalls || '0';
            lastTool.textContent = stats.lastTool || '—';
            errorCount.textContent = stats.errors || '0';

            if (stats.lastTimestamp) {
                const d = new Date(stats.lastTimestamp);
                lastTimestamp.textContent = d.toLocaleTimeString();
            } else {
                lastTimestamp.textContent = '—';
            }
        }
    }

    // Initial state
    chrome.runtime.sendMessage({ type: 'GET_STATE' }, (resp) => {
        if (resp) {
            updateUI(resp.connectionState, resp.stats);
        } else {
            updateUI('disconnected', null);
        }
    });

    // Listen for updates
    chrome.runtime.onMessage.addListener((message) => {
        if (message.type === 'STATE_UPDATE') {
            updateUI(message.connectionState, message.stats);
        }
    });

    // Reconnect button
    reconnectBtn.addEventListener('click', () => {
        reconnectBtn.textContent = '⟳ Connecting...';
        reconnectBtn.disabled = true;

        chrome.runtime.sendMessage({ type: 'RECONNECT' }, (resp) => {
            setTimeout(() => {
                reconnectBtn.textContent = '↻ Reconnect';
                reconnectBtn.disabled = false;

                chrome.runtime.sendMessage({ type: 'GET_STATE' }, (resp2) => {
                    if (resp2) updateUI(resp2.connectionState, resp2.stats);
                });
            }, 1000);
        });
    });
});
