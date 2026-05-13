/**
 * AIM-OS Gemini Bridge — Content Script
 *
 * Runs on gemini.google.com. Observes the DOM for MCP-CALL code blocks
 * in Gemini's assistant responses, extracts tool payloads, sends them
 * to the background service worker, and injects results back as user messages.
 */

(() => {
    'use strict';

    // ── State ──────────────────────────────────────────────────────────

    let bridgeState = 'disconnected';
    let processedBlocks = new WeakSet();
    let processedHashes = new Map(); // content hash -> timestamp (dedup)
    let toastTimer = null;
    let latestResult = null; // Stores the latest formatted tool result for 1-click copy
    let resultCount = 0; // Unread result counter

    // ── UI: Status Badge ───────────────────────────────────────────────

    function createBadge() {
        if (document.getElementById('aimos-bridge-badge')) return;

        const badge = document.createElement('div');
        badge.id = 'aimos-bridge-badge';
        badge.innerHTML = `
      <span class="status-dot disconnected"></span>
      <span class="status-text">AIM-OS Bridge</span>
    `;
        badge.addEventListener('click', () => {
            // If there's a result ready, copy it to clipboard
            if (latestResult) {
                navigator.clipboard.writeText(latestResult).then(() => {
                    const text = badge.querySelector('.status-text');
                    if (text) text.textContent = '✓ Copied!';
                    showToast('Copied', '📋 Paste into chat and press Enter');
                    // Reset after 2s
                    setTimeout(() => {
                        resultCount = 0;
                        updateBadge('connected');
                    }, 2000);
                }).catch(() => {
                    showToast('Error', 'Clipboard access failed', true);
                });
                return;
            }
            // Otherwise reconnect
            chrome.runtime.sendMessage({ type: 'RECONNECT' }, (resp) => {
                updateBadge(resp?.connectionState || 'disconnected');
            });
        });
        document.body.appendChild(badge);

        // Toast container
        const toast = document.createElement('div');
        toast.id = 'aimos-bridge-toast';
        document.body.appendChild(toast);

        // Initial state check
        chrome.runtime.sendMessage({ type: 'GET_STATE' }, (resp) => {
            if (resp) {
                updateBadge(resp.connectionState);
            }
        });
    }

    function updateBadge(state) {
        bridgeState = state;
        const dot = document.querySelector('#aimos-bridge-badge .status-dot');
        const text = document.querySelector('#aimos-bridge-badge .status-text');
        const badge = document.getElementById('aimos-bridge-badge');
        if (!dot || !text) return;

        dot.className = 'status-dot ' + (state === 'connected' ? 'connected' : 'disconnected');
        text.textContent = state === 'connected' ? 'AIM-OS ● Live' : 'AIM-OS ○ Offline';
        if (badge) badge.classList.remove('has-result');
        latestResult = null;
    }

    function updateBadgeWithResult(toolName) {
        resultCount++;
        const dot = document.querySelector('#aimos-bridge-badge .status-dot');
        const text = document.querySelector('#aimos-bridge-badge .status-text');
        const badge = document.getElementById('aimos-bridge-badge');
        if (!dot || !text || !badge) return;

        dot.className = 'status-dot has-result';
        text.textContent = `📋 ${resultCount} Result${resultCount > 1 ? 's' : ''} — Click to Copy`;
        badge.classList.add('has-result');
    }

    function showToast(toolName, status, isError = false) {
        const toast = document.getElementById('aimos-bridge-toast');
        if (!toast) return;

        toast.innerHTML = `
      <span class="toast-tool">${toolName}</span>
      <div class="toast-status" style="color: ${isError ? '#f28b82' : '#81c995'}">${status}</div>
    `;
        toast.classList.add('visible');

        clearTimeout(toastTimer);
        toastTimer = setTimeout(() => {
            toast.classList.remove('visible');
        }, 4000);
    }

    // ── MCP-CALL Detection ─────────────────────────────────────────────

    /**
     * Scans a DOM node for MCP-CALL code blocks.
     * Gemini renders code blocks as <code-block> > pre > code.code-container.
     * The "mcp-call" language tag shows as "Code snippet" label — NOT as a DOM attribute.
     * So we scan ALL code blocks and detect by content (JSON with a "tool" key).
     */
    /**
     * Simple hash for dedup — fast, not cryptographic.
     */
    function hashContent(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            const ch = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + ch;
            hash |= 0; // Convert to 32-bit integer
        }
        return String(hash);
    }

    /**
     * Check if this JSON payload was already processed recently (within 5s).
     */
    function isDuplicate(jsonText) {
        const now = Date.now();
        // Expire old entries
        for (const [key, ts] of processedHashes) {
            if (now - ts > 5000) processedHashes.delete(key);
        }
        const h = hashContent(jsonText);
        if (processedHashes.has(h)) return true;
        processedHashes.set(h, now);
        return false;
    }

    function scanForMcpCalls(root) {
        // Gemini's actual code block structure: <code-block> containing <pre><code>
        const codeElements = root.querySelectorAll(
            'code-block pre code, code-block code, pre code, code-block'
        );

        for (const block of codeElements) {
            if (processedBlocks.has(block)) continue;

            const text = block.textContent?.trim();
            if (!text) continue;

            // Content-based detection: look for JSON with a "tool" key
            let jsonText = text;

            // Strip MCP-CALL prefix if present
            if (jsonText.startsWith('MCP-CALL')) {
                jsonText = jsonText.substring('MCP-CALL'.length).trim();
            }

            // Quick checks before trying JSON.parse
            if (!jsonText.startsWith('{')) continue;
            if (!jsonText.includes('"tool"')) continue;

            // Try to parse as JSON
            let payload;
            try {
                payload = JSON.parse(jsonText);
            } catch (err) {
                continue; // Not valid JSON, skip silently
            }

            // Must have a "tool" field to be an MCP call
            if (!payload || !payload.tool) continue;

            // Content-hash dedup: skip if same payload was processed in last 5s
            if (isDuplicate(jsonText)) {
                console.log(`[AIM-OS Bridge] Skipping duplicate MCP-CALL: ${payload.tool}`);
                processedBlocks.add(block);
                continue;
            }

            // Mark as processed (mark the code-block parent too to avoid double-processing)
            processedBlocks.add(block);
            const codeBlockParent = block.closest('code-block');
            if (codeBlockParent) processedBlocks.add(codeBlockParent);

            console.log(`[AIM-OS Bridge] Detected MCP-CALL in DOM: ${payload.tool}`, payload.args);
            handleMcpCallBlock(jsonText, codeBlockParent || block);
        }

        // Fallback: scan model response containers for raw markdown fences
        const responseContainers = root.querySelectorAll(
            'model-response, .markdown, .response-container, [data-message-author-role="model"]'
        );
        for (const el of responseContainers) {
            if (processedBlocks.has(el)) continue;

            const html = el.innerHTML || '';
            const regex = /```(?:mcp-call|MCP-CALL|mcp_call|json)?\s*\n?(\{[\s\S]*?"tool"\s*:[\s\S]*?\})\s*```/gi;
            let match;
            while ((match = regex.exec(html)) !== null) {
                const content = match[1].trim();
                const key = el.tagName + '_' + match.index;
                if (el.dataset.aimosProcessed?.includes(key)) continue;

                try {
                    const parsed = JSON.parse(content);
                    if (!parsed.tool) continue;
                } catch {
                    continue;
                }

                el.dataset.aimosProcessed = (el.dataset.aimosProcessed || '') + key + ',';
                handleMcpCallBlock(content, el);
            }
        }
    }

    function handleMcpCallBlock(rawText, sourceElement) {
        // Strip the "MCP-CALL" prefix if present
        let jsonText = rawText;
        if (jsonText.startsWith('MCP-CALL')) {
            jsonText = jsonText.substring('MCP-CALL'.length).trim();
        }

        let payload;
        try {
            payload = JSON.parse(jsonText);
        } catch (err) {
            console.warn('[AIM-OS Bridge] Failed to parse MCP-CALL JSON:', err, jsonText);
            showToast('Parse Error', `Invalid JSON: ${err.message}`, true);
            return;
        }

        const { tool, args } = payload;
        if (!tool) {
            console.warn('[AIM-OS Bridge] MCP-CALL missing "tool" field:', payload);
            showToast('Invalid Call', 'Missing "tool" field', true);
            return;
        }

        console.log(`[AIM-OS Bridge] Detected MCP-CALL: ${tool}`, args);
        showToast(tool, 'Executing...');

        // Update badge to working state
        const dot = document.querySelector('#aimos-bridge-badge .status-dot');
        if (dot) dot.className = 'status-dot working';

        // Send to background (guard against stale context after extension reload)
        const requestId = `content_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
        try {
            chrome.runtime.sendMessage({
                type: 'MCP_CALL',
                requestId,
                tool,
                args: args || {}
            });
        } catch (e) {
            if (e.message && e.message.includes('Extension context invalidated')) {
                console.warn('[AIM-OS Bridge] Extension was reloaded — refresh this tab (F5)');
                showToast('Stale Extension', 'Extension reloaded — press F5 to refresh this page', true);
                stopScanner();
                return;
            }
            throw e;
        }

        // Visual feedback: highlight the code block
        if (sourceElement) {
            sourceElement.style.borderLeft = '3px solid #8ab4f8';
            sourceElement.style.paddingLeft = '8px';
        }
    }

    // ── Result Injection ───────────────────────────────────────────────

    try {
        chrome.runtime.onMessage.addListener((message) => {
            if (message.type === 'TOOL_RESULT') {
                handleToolResult(message);
            }
            if (message.type === 'STATE_UPDATE') {
                updateBadge(message.connectionState);
            }
        });
    } catch (e) {
        console.warn('[AIM-OS Bridge] Could not attach listener — extension context invalid');
    }

    // ── Settings ───────────────────────────────────────────────────────

    let autoSend = false; // Default: don't auto-send

    function handleToolResult(message) {
        const { success, result, error, requestId } = message;

        if (!success) {
            updateBadge('connected');
            showToast('Error', error || 'Unknown error', true);
            console.error('[AIM-OS Bridge] Tool error:', error);
            return;
        }

        const toolName = result?.tool || 'Tool';
        console.log('[AIM-OS Bridge] Tool result:', result);

        // Format the result as JSON
        let formatted;
        try {
            formatted = JSON.stringify(result, null, 2);
        } catch {
            formatted = String(result);
        }
        if (formatted.length > 8000) {
            formatted = formatted.substring(0, 8000) + '\n... [truncated]';
        }

        // Store for 1-click copy from badge
        latestResult = `[SYSTEM] MCP Tool Result (${toolName}):\n\n${formatted}`;

        // Update badge to show "click to copy" state
        updateBadgeWithResult(toolName);
        showToast(toolName, '✓ Ready — click badge to copy');

        // Show in results panel too
        showResultsPanel(toolName, formatted);
    }

    // ── Results Panel ─────────────────────────────────────────────────

    function createResultsPanel() {
        if (document.getElementById('aimos-results-panel')) return;

        const panel = document.createElement('div');
        panel.id = 'aimos-results-panel';
        panel.innerHTML = `
            <div class="arp-header">
                <span class="arp-title">🔧 MCP Result</span>
                <div class="arp-controls">
                    <label class="arp-toggle" title="Auto-upload results to chat">
                        <input type="checkbox" id="aimos-auto-send" />
                        <span class="arp-toggle-label">Auto</span>
                    </label>
                    <button class="arp-btn arp-close" title="Close">✕</button>
                </div>
            </div>
            <pre class="arp-body"><code id="aimos-result-content">No results yet</code></pre>
            <div class="arp-actions">
                <button class="arp-btn arp-copy" title="Copy to clipboard">📋 Copy</button>
                <button class="arp-btn arp-upload" title="Upload as file to Gemini chat">📎 Upload to Chat</button>
            </div>
        `;
        document.body.appendChild(panel);

        // Wire events
        panel.querySelector('.arp-close').addEventListener('click', () => {
            panel.classList.remove('visible');
        });

        panel.querySelector('.arp-copy').addEventListener('click', () => {
            const content = document.getElementById('aimos-result-content').textContent;
            navigator.clipboard.writeText(content).then(() => {
                showToast('Copied', '✓ Result copied to clipboard');
            }).catch(() => {
                showToast('Copy Failed', 'Could not access clipboard', true);
            });
        });

        panel.querySelector('.arp-upload').addEventListener('click', () => {
            const content = document.getElementById('aimos-result-content').textContent;
            const toolName = panel.dataset.toolName || 'mcp_result';
            injectResultToChat(toolName, content);
        });

        const toggle = panel.querySelector('#aimos-auto-send');
        toggle.checked = autoSend;
        toggle.addEventListener('change', (e) => {
            autoSend = e.target.checked;
            console.log(`[AIM-OS Bridge] Auto-send ${autoSend ? 'ON' : 'OFF'}`);
            showToast('Settings', `Auto-upload ${autoSend ? 'enabled' : 'disabled'}`);
        });
    }

    function showResultsPanel(toolName, content) {
        createResultsPanel();
        const panel = document.getElementById('aimos-results-panel');
        const codeEl = document.getElementById('aimos-result-content');
        const title = panel.querySelector('.arp-title');

        title.textContent = `🔧 ${toolName}`;
        codeEl.textContent = content;
        panel.dataset.toolName = toolName;
        panel.classList.add('visible');
    }

    // ── Result Injection into Chat ─────────────────────────────────────

    /**
     * Check if Gemini is currently streaming a response.
     * During streaming, the send button transforms into a stop button.
     */
    function isGeminiStreaming() {
        // Check for stop button (appears during generation)
        const stopBtn = document.querySelector(
            'button[aria-label="Stop response"], ' +
            'button[aria-label="Stop"], ' +
            'button.stop-button, ' +
            'mat-icon[data-mat-icon-name="stop_circle"]'
        );
        if (stopBtn) return true;

        // Check for streaming indicator / loading spinner
        const loading = document.querySelector(
            '.loading-indicator, .response-streaming, ' +
            '[data-is-streaming="true"], .thinking-indicator'
        );
        if (loading) return true;

        return false;
    }

    /**
     * Wait for Gemini to finish streaming, then call the callback.
     * Times out after maxWaitMs and calls callback anyway.
     */
    function waitForStreamingComplete(callback, maxWaitMs = 30000) {
        const startTime = Date.now();
        const interval = 500; // Check every 500ms

        function check() {
            if (!isGeminiStreaming()) {
                // Give a small extra pause for UI to settle
                setTimeout(callback, 500);
                return;
            }
            if (Date.now() - startTime > maxWaitMs) {
                console.warn('[AIM-OS Bridge] Timed out waiting for Gemini to finish streaming');
                callback();
                return;
            }
            setTimeout(check, interval);
        }

        check();
    }

    function injectResultToChat(toolName, content) {
        // Truncate long results to avoid overwhelming Gemini's context
        let text = content;
        if (text.length > 8000) {
            text = text.substring(0, 8000) + '\n... [truncated]';
        }

        // Format as a [SYSTEM] message Gemini will recognize
        const message = `[SYSTEM] MCP Tool Result (${toolName}):\n\n${text}`;

        // Wait for Gemini to finish streaming before injecting
        if (isGeminiStreaming()) {
            console.log('[AIM-OS Bridge] Gemini is streaming — waiting for completion...');
            showToast(toolName, '⏳ Waiting for Gemini to finish...');
            waitForStreamingComplete(() => {
                doInject(toolName, message);
            });
        } else {
            doInject(toolName, message);
        }
    }

    function doInject(toolName, message) {
        // Find Gemini's Quill editor
        const editor = document.querySelector(
            'div.ql-editor[role="textbox"], ' +
            '.ql-editor[contenteditable="true"], ' +
            'div.ql-editor, ' +
            'div[contenteditable="true"][role="textbox"], ' +
            'div[contenteditable="true"][aria-label*="prompt"]'
        );

        if (!editor) {
            // Fallback: copy to clipboard
            navigator.clipboard.writeText(message).then(() => {
                console.log(`[AIM-OS Bridge] No editor found — result copied to clipboard`);
                showToast(toolName, '📋 Copied — paste with Ctrl+V', true);
            }).catch(() => {
                showToast(toolName, '✗ Could not find chat input', true);
            });
            return;
        }

        // Focus the editor
        editor.focus();

        // Clear any existing content
        editor.innerHTML = '';

        // Method 1: execCommand('insertText') — fires native InputEvent
        // This is the key: Quill and Angular listen for InputEvents, not raw DOM changes
        const inserted = document.execCommand('insertText', false, message);

        if (inserted) {
            console.log(`[AIM-OS Bridge] Injected result for ${toolName} via execCommand`);
        } else {
            // Method 2: Simulate keyboard-level input events
            console.log('[AIM-OS Bridge] execCommand failed, trying InputEvent dispatch');

            editor.textContent = message;

            // Dispatch the InputEvent that frameworks listen for
            editor.dispatchEvent(new InputEvent('input', {
                inputType: 'insertText',
                data: message,
                bubbles: true,
                cancelable: false,
                composed: true
            }));

            // Also fire change/keyup for good measure
            editor.dispatchEvent(new Event('change', { bubbles: true }));
            editor.dispatchEvent(new KeyboardEvent('keyup', { bubbles: true, key: 'a' }));
        }

        showToast(toolName, '✓ Result injected — sending...');

        // Wait for framework to process, then find and click the SEND button (not STOP)
        setTimeout(() => {
            // Find send button — but explicitly EXCLUDE the stop button
            const allButtons = document.querySelectorAll('button');
            let sendBtn = null;

            for (const btn of allButtons) {
                const label = (btn.getAttribute('aria-label') || '').toLowerCase();
                const tooltip = (btn.getAttribute('data-tooltip') || '').toLowerCase();
                const classes = btn.className.toLowerCase();

                // Skip if it's a stop button
                if (label.includes('stop') || classes.includes('stop')) continue;

                // Match send button
                if (label.includes('send') || tooltip.includes('send') || classes.includes('send-button')) {
                    sendBtn = btn;
                    break;
                }
            }

            if (sendBtn && !sendBtn.disabled) {
                sendBtn.click();
                console.log('[AIM-OS Bridge] Clicked send button (verified not stop)');
                showToast(toolName, '✓ Result sent to Gemini');
            } else {
                console.warn('[AIM-OS Bridge] Send button not found or disabled — try pressing Enter');
                // Try dispatching Enter key on the editor as fallback
                editor.dispatchEvent(new KeyboardEvent('keydown', {
                    key: 'Enter', code: 'Enter', keyCode: 13,
                    bubbles: true, cancelable: true
                }));
                showToast(toolName, '⚠ Result in input — may need manual Enter', true);
            }
        }, 500);
    }

    // ── DOM Observer ───────────────────────────────────────────────────

    let scannerIntervalId = null;

    function stopScanner() {
        if (scannerIntervalId) {
            clearInterval(scannerIntervalId);
            scannerIntervalId = null;
            console.log('[AIM-OS Bridge] Scanner stopped (extension context invalid)');
        }
    }

    function startObserver() {
        // Gemini streams response content incrementally, and MutationObserver
        // fires for individual child nodes which can't be queried for descendants.
        // A periodic full-body scan is far more reliable.
        scannerIntervalId = setInterval(() => {
            scanForMcpCalls(document.body);
        }, 2000);

        console.log('[AIM-OS Bridge] Periodic scanner active (every 2s) on gemini.google.com');

        // Also do an initial scan
        scanForMcpCalls(document.body);
    }

    // ── Init ───────────────────────────────────────────────────────────

    function init() {
        console.log('[AIM-OS Bridge] Content script loaded');
        createBadge();
        startObserver();
    }

    // Wait for page to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
