import * as vscode from 'vscode';
import { AIMOSLogger } from './utils/logger';

/**
 * Custom Chat Panel Provider
 * Creates a fully customizable chat interface in the editor area
 */
export class CustomChatPanel {
    private static currentPanel: vscode.WebviewPanel | undefined = undefined;
    private static context: vscode.ExtensionContext;

    /**
     * Initialize the chat panel provider
     */
    public static initialize(context: vscode.ExtensionContext): void {
        CustomChatPanel.context = context;
    }

    /**
     * Create or reveal the custom chat panel
     */
    public static createOrShow(): void {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;

        // If panel already exists, reveal it
        if (CustomChatPanel.currentPanel) {
            CustomChatPanel.currentPanel.reveal(column);
            return;
        }

        // Create new panel
        const panel = vscode.window.createWebviewPanel(
            'aimosCustomChat',
            'AIMOS Chat',
            column || vscode.ViewColumn.One,
            {
                enableScripts: true,
                retainContextWhenHidden: true,
                localResourceRoots: [vscode.Uri.file(CustomChatPanel.context.extensionPath)]
            }
        );

        CustomChatPanel.currentPanel = panel;

        // Set initial HTML
        panel.webview.html = CustomChatPanel.getChatHTML(panel.webview);

        // Handle messages from webview
        panel.webview.onDidReceiveMessage(
            async message => {
                switch (message.command) {
                    case 'sendMessage':
                        await CustomChatPanel.handleSendMessage(message.text);
                        break;
                    case 'sendToCursor':
                        await CustomChatPanel.handleSendToCursor(message.text);
                        break;
                    case 'clearChat':
                        CustomChatPanel.clearChat();
                        break;
                }
            },
            null,
            CustomChatPanel.context.subscriptions
        );

        // Clean up when panel is closed
        panel.onDidDispose(
            () => {
                CustomChatPanel.currentPanel = undefined;
            },
            null,
            CustomChatPanel.context.subscriptions
        );

        AIMOSLogger.success('CUSTOM_CHAT', 'Custom chat panel created');
    }

    /**
     * Get the HTML content for the chat panel
     */
    private static getChatHTML(webview: vscode.Webview): string {
        const cspSource = webview.cspSource;

        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${cspSource} 'unsafe-inline'; script-src ${cspSource} 'unsafe-inline'; font-src ${cspSource} data:;">
    <title>AIMOS Chat</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #1e1e1e;
            color: #d4d4d4;
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .chat-header {
            background: #252526;
            padding: 16px 20px;
            border-bottom: 1px solid #3e3e42;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .chat-header h1 {
            font-size: 18px;
            font-weight: 600;
            color: #51cf66;
            margin: 0;
        }

        .chat-actions {
            display: flex;
            gap: 8px;
        }

        .btn {
            padding: 6px 12px;
            border: none;
            border-radius: 4px;
            background: #0e639c;
            color: white;
            cursor: pointer;
            font-size: 12px;
            transition: background 0.2s;
        }

        .btn:hover {
            background: #1177bb;
        }

        .btn-secondary {
            background: #3e3e42;
        }

        .btn-secondary:hover {
            background: #4e4e52;
        }

        .messages-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }

        .message {
            display: flex;
            gap: 12px;
            max-width: 80%;
            animation: slideIn 0.3s ease-out;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .message.user {
            align-self: flex-end;
            flex-direction: row-reverse;
        }

        .message-avatar {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 14px;
            flex-shrink: 0;
        }

        .message.user .message-avatar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .message.assistant .message-avatar {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
        }

        .message-bubble {
            padding: 12px 16px;
            border-radius: 18px;
            word-wrap: break-word;
            line-height: 1.5;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        }

        .message.user .message-bubble {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-bottom-right-radius: 4px;
        }

        .message.assistant .message-bubble {
            background: #2d2d30;
            color: #d4d4d4;
            border: 1px solid #3e3e42;
            border-bottom-left-radius: 4px;
        }

        .message-time {
            font-size: 11px;
            color: #858585;
            margin-top: 4px;
            padding: 0 4px;
        }

        .message.user .message-time {
            text-align: right;
        }

        .input-area {
            background: #252526;
            border-top: 1px solid #3e3e42;
            padding: 16px 20px;
            display: flex;
            gap: 12px;
            align-items: flex-end;
        }

        .input-wrapper {
            flex: 1;
            position: relative;
        }

        .input-field {
            width: 100%;
            min-height: 44px;
            max-height: 120px;
            padding: 12px 16px;
            background: #1e1e1e;
            border: 2px solid #3e3e42;
            border-radius: 22px;
            color: #d4d4d4;
            font-size: 14px;
            font-family: inherit;
            resize: none;
            outline: none;
            transition: border-color 0.2s;
        }

        .input-field:focus {
            border-color: #51cf66;
        }

        .input-field::placeholder {
            color: #858585;
        }

        .send-button {
            width: 44px;
            height: 44px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            color: white;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: transform 0.2s, box-shadow 0.2s;
            flex-shrink: 0;
        }

        .send-button:hover {
            transform: scale(1.05);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }

        .send-button:active {
            transform: scale(0.95);
        }

        .send-button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }

        .send-button svg {
            width: 20px;
            height: 20px;
        }

        .typing-indicator {
            display: flex;
            gap: 4px;
            padding: 12px 16px;
        }

        .typing-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #858585;
            animation: typing 1.4s infinite;
        }

        .typing-dot:nth-child(2) {
            animation-delay: 0.2s;
        }

        .typing-dot:nth-child(3) {
            animation-delay: 0.4s;
        }

        @keyframes typing {
            0%, 60%, 100% {
                transform: translateY(0);
                opacity: 0.7;
            }
            30% {
                transform: translateY(-10px);
                opacity: 1;
            }
        }

        .empty-state {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: #858585;
            text-align: center;
            padding: 40px;
        }

        .empty-state h2 {
            margin-bottom: 8px;
            color: #d4d4d4;
        }

        /* Confidence Badge */
        .confidence-badge {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            margin-top: 8px;
        }

        .confidence-badge.band-S {
            background: rgba(16, 185, 129, 0.2);
            color: #10b981;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }

        .confidence-badge.band-A {
            background: rgba(34, 197, 94, 0.2);
            color: #22c55e;
            border: 1px solid rgba(34, 197, 94, 0.3);
        }

        .confidence-badge.band-B {
            background: rgba(234, 179, 8, 0.2);
            color: #eab308;
            border: 1px solid rgba(234, 179, 8, 0.3);
        }

        .confidence-badge.band-C {
            background: rgba(239, 68, 68, 0.2);
            color: #ef4444;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }

        /* Evidence Panel */
        .evidence-panel {
            margin-top: 12px;
            background: #252526;
            border: 1px solid #3e3e42;
            border-radius: 8px;
            overflow: hidden;
        }

        .evidence-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 12px;
            cursor: pointer;
            user-select: none;
            transition: background 0.2s;
        }

        .evidence-header:hover {
            background: #2d2d30;
        }

        .evidence-header-title {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 12px;
            font-weight: 600;
            color: #d4d4d4;
        }

        .evidence-header-count {
            color: #858585;
            font-size: 11px;
        }

        .evidence-toggle {
            width: 16px;
            height: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #858585;
            transition: transform 0.2s;
        }

        .evidence-toggle.expanded {
            transform: rotate(180deg);
        }

        .evidence-content {
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease-out;
        }

        .evidence-content.expanded {
            max-height: 400px;
            overflow-y: auto;
        }

        .evidence-items {
            padding: 8px;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }

        .evidence-item {
            background: #1e1e1e;
            border: 1px solid #3e3e42;
            border-radius: 6px;
            padding: 8px;
            font-size: 11px;
        }

        .evidence-item-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 4px;
        }

        .evidence-item-source {
            color: #51cf66;
            font-weight: 600;
            flex: 1;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .evidence-item-trust {
            padding: 2px 6px;
            border-radius: 10px;
            font-size: 10px;
            font-weight: 600;
            margin-left: 8px;
        }

        .evidence-item-trust.high {
            background: rgba(16, 185, 129, 0.2);
            color: #10b981;
        }

        .evidence-item-trust.medium {
            background: rgba(234, 179, 8, 0.2);
            color: #eab308;
        }

        .evidence-item-trust.low {
            background: rgba(239, 68, 68, 0.2);
            color: #ef4444;
        }

        .evidence-item-excerpt {
            color: #858585;
            line-height: 1.4;
            overflow: hidden;
            text-overflow: ellipsis;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
        }
    </style>
</head>
<body>
    <div class="chat-header">
        <h1>💬 AIMOS Chat</h1>
        <div class="chat-actions">
            <button class="btn btn-secondary" id="clearBtn">Clear</button>
            <button class="btn" id="sendToCursorBtn">Send to Cursor</button>
        </div>
    </div>

    <div class="messages-container" id="messagesContainer">
        <div class="empty-state">
            <h2>Welcome to AIMOS Chat</h2>
            <p>Start a conversation by typing a message below</p>
        </div>
    </div>

    <div class="input-area">
        <div class="input-wrapper">
            <textarea
                id="messageInput"
                class="input-field"
                placeholder="Type your message..."
                rows="1"
            ></textarea>
        </div>
        <button class="send-button" id="sendButton" title="Send message">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/>
            </svg>
        </button>
    </div>

    <script>
        const vscode = acquireVsCodeApi();
        
        const messagesContainer = document.getElementById('messagesContainer');
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');
        const clearBtn = document.getElementById('clearBtn');
        const sendToCursorBtn = document.getElementById('sendToCursorBtn');

        let messages = [];

        // Auto-resize textarea
        messageInput.addEventListener('input', () => {
            messageInput.style.height = 'auto';
            messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + 'px';
        });

        // Send message
        function sendMessage() {
            const text = messageInput.value.trim();
            if (!text) return;

            addMessage(text, 'user');
            messageInput.value = '';
            messageInput.style.height = 'auto';

            // Disable send button
            sendButton.disabled = true;

            // Send to extension
            vscode.postMessage({
                command: 'sendMessage',
                text: text
            });

            // Show typing indicator
            showTypingIndicator();
        }

        // Send to Cursor chat
        function sendToCursor() {
            const text = messageInput.value.trim() || getLastMessage();
            if (!text) {
                vscode.postMessage({
                    command: 'sendToCursor',
                    text: 'proceed'
                });
                return;
            }

            vscode.postMessage({
                command: 'sendToCursor',
                text: text
            });
        }

        function getLastMessage() {
            const userMessages = messages.filter(m => m.type === 'user');
            return userMessages.length > 0 ? userMessages[userMessages.length - 1].text : '';
        }

        // Add message to UI
        function addMessage(text, type, confidence, evidence) {
            const emptyState = messagesContainer.querySelector('.empty-state');
            if (emptyState) {
                emptyState.remove();
            }

            const message = {
                id: Date.now(),
                text: text,
                type: type,
                time: new Date().toLocaleTimeString(),
                confidence: confidence,
                evidence: evidence
            };

            messages.push(message);

            // Build confidence badge HTML
            let confidenceBadgeHtml = '';
            if (confidence) {
                const band = confidence.band || (confidence.value >= 0.95 ? 'S' : 
                                                   confidence.value >= 0.90 ? 'A' :
                                                   confidence.value >= 0.85 ? 'B' : 'C');
                const percentage = (confidence.value * 100).toFixed(0);
                confidenceBadgeHtml = \`
                    <div class="confidence-badge band-\${band}">
                        <span>Confidence: \${band}</span>
                        <span>(\${percentage}%)</span>
                    </div>
                \`;
            }

            // Build evidence panel HTML
            let evidencePanelHtml = '';
            if (evidence && evidence.length > 0) {
                const evidenceId = \`evidence_\${message.id}\`;
                evidencePanelHtml = \`
                    <div class="evidence-panel">
                        <div class="evidence-header" onclick="toggleEvidence('\${evidenceId}')">
                            <div class="evidence-header-title">
                                <span>📚 Evidence</span>
                                <span class="evidence-header-count">(\${evidence.length})</span>
                            </div>
                            <div class="evidence-toggle" id="\${evidenceId}_toggle">▼</div>
                        </div>
                        <div class="evidence-content" id="\${evidenceId}_content">
                            <div class="evidence-items">
                                \${evidence.map(item => {
                                    const trustClass = item.trust >= 0.8 ? 'high' : 
                                                      item.trust >= 0.6 ? 'medium' : 'low';
                                    const trustPercent = (item.trust * 100).toFixed(0);
                                    return \`
                                        <div class="evidence-item">
                                            <div class="evidence-item-header">
                                                <div class="evidence-item-source">\${escapeHtml(item.sourceId)}</div>
                                                <div class="evidence-item-trust \${trustClass}">\${trustPercent}%</div>
                                            </div>
                                            <div class="evidence-item-excerpt">\${escapeHtml(item.excerpt)}</div>
                                        </div>
                                    \`;
                                }).join('')}
                            </div>
                        </div>
                    </div>
                \`;
            }

            const messageDiv = document.createElement('div');
            messageDiv.className = \`message \${type}\`;
            messageDiv.innerHTML = \`
                <div class="message-avatar">\${type === 'user' ? 'U' : 'A'}</div>
                <div class="message-content">
                    <div class="message-bubble">\${escapeHtml(text)}</div>
                    \${confidenceBadgeHtml}
                    \${evidencePanelHtml}
                    <div class="message-time">\${message.time}</div>
                </div>
            \`;

            messagesContainer.appendChild(messageDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }

        // Toggle evidence panel
        function toggleEvidence(evidenceId) {
            const content = document.getElementById(\`\${evidenceId}_content\`);
            const toggle = document.getElementById(\`\${evidenceId}_toggle\`);
            
            if (content && toggle) {
                const isExpanded = content.classList.contains('expanded');
                
                if (isExpanded) {
                    content.classList.remove('expanded');
                    toggle.classList.remove('expanded');
                } else {
                    content.classList.add('expanded');
                    toggle.classList.add('expanded');
                }
            }
        }

        // Make toggleEvidence available globally
        window.toggleEvidence = toggleEvidence;

        // Show typing indicator
        function showTypingIndicator() {
            const typingDiv = document.createElement('div');
            typingDiv.className = 'message assistant';
            typingDiv.id = 'typingIndicator';
            typingDiv.innerHTML = \`
                <div class="message-avatar">A</div>
                <div class="message-content">
                    <div class="message-bubble">
                        <div class="typing-indicator">
                            <div class="typing-dot"></div>
                            <div class="typing-dot"></div>
                            <div class="typing-dot"></div>
                        </div>
                    </div>
                </div>
            \`;

            messagesContainer.appendChild(typingDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }

        // Hide typing indicator
        function hideTypingIndicator() {
            const typingIndicator = document.getElementById('typingIndicator');
            if (typingIndicator) {
                typingIndicator.remove();
            }
        }

        // Clear chat
        function clearChat() {
            messages = [];
            messagesContainer.innerHTML = \`
                <div class="empty-state">
                    <h2>Welcome to AIMOS Chat</h2>
                    <p>Start a conversation by typing a message below</p>
                </div>
            \`;
            vscode.postMessage({ command: 'clearChat' });
        }

        // Escape HTML
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        // Event listeners
        sendButton.addEventListener('click', sendMessage);
        clearBtn.addEventListener('click', clearChat);
        sendToCursorBtn.addEventListener('click', sendToCursor);

        messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        // Listen for messages from extension
        window.addEventListener('message', event => {
            const message = event.data;
            
            switch (message.command) {
                case 'addMessage':
                    hideTypingIndicator();
                    addMessage(
                        message.text, 
                        message.type || 'assistant',
                        message.confidence,
                        message.evidence
                    );
                    sendButton.disabled = false;
                    break;
                case 'error':
                    hideTypingIndicator();
                    addMessage(\`Error: \${message.text}\`, 'assistant');
                    sendButton.disabled = false;
                    break;
            }
        });
    </script>
</body>
</html>`;
    }

    /**
     * Handle send message from webview
     * Optionally uses Aether Chat orchestrator for enhanced processing
     */
    private static async handleSendMessage(text: string): Promise<void> {
        AIMOSLogger.log('CUSTOM_CHAT', 'Message received from webview', { text });

        try {
            // Try to use Aether Chat orchestrator if available
            let responseText = `Received: ${text}`;
            let confidence: { value: number; band: 'A' | 'B' | 'C' | 'S' } | undefined;
            let evidence: Array<{
                id: string;
                kind: string;
                sourceId: string;
                excerpt: string;
                trust: number;
            }> | undefined;

            try {
                // Try to import orchestrator (may not be available in Cursor extension context)
                const orchestratorPath = require.resolve('../../ide_orchestration/prototypes/dac/src/services/aetherChatOrchestrator');
                const orchestrator = require(orchestratorPath);
                
                if (orchestrator.runAetherChatTurn) {
                    // Create RawUserTurn
                    const rawTurn = {
                        sessionId: `cursor_chat_${Date.now()}`,
                        userId: undefined,
                        source: 'cursor' as const,
                        message: text,
                        timestamp: new Date().toISOString(),
                        conversationHistory: []
                    };

                    // Process through orchestrator
                    const finalTurn = await orchestrator.runAetherChatTurn(rawTurn);
                    
                    responseText = finalTurn.assistantText;
                    confidence = finalTurn.confidence;
                    evidence = finalTurn.evidence.map((e: any) => ({
                        id: e.id,
                        kind: e.kind,
                        sourceId: e.sourceId,
                        excerpt: e.excerpt,
                        trust: e.trust
                    }));
                }
            } catch (orchestratorError) {
                // Orchestrator not available - use basic response
                AIMOSLogger.log('CUSTOM_CHAT', 'Orchestrator not available, using basic response', orchestratorError);
            }

            // Add message to panel with confidence and evidence
            if (CustomChatPanel.currentPanel) {
                CustomChatPanel.currentPanel.webview.postMessage({
                    command: 'addMessage',
                    text: responseText,
                    type: 'assistant',
                    confidence: confidence,
                    evidence: evidence
                });
            }
        } catch (error: any) {
            AIMOSLogger.error('CUSTOM_CHAT', 'Error handling message', error);
            
            // Fallback: basic response
            if (CustomChatPanel.currentPanel) {
                CustomChatPanel.currentPanel.webview.postMessage({
                    command: 'addMessage',
                    text: `Received: ${text}`,
                    type: 'assistant'
                });
            }
        }
    }

    /**
     * Handle send to Cursor chat
     */
    private static async handleSendToCursor(text: string): Promise<void> {
        AIMOSLogger.log('CUSTOM_CHAT', 'Sending to Cursor chat', { text });

        try {
            // Send to Cursor chat via Command Server
            const response = await fetch('http://localhost:5001/cursor/chat/send', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: text,
                    waitForResponse: false
                })
            });

            if (response.ok) {
                const result = await response.json();
                AIMOSLogger.success('CUSTOM_CHAT', 'Message sent to Cursor', result);

                // Update panel
                if (CustomChatPanel.currentPanel) {
                    CustomChatPanel.currentPanel.webview.postMessage({
                        command: 'addMessage',
                        text: `✅ Sent to Cursor: "${text}"`,
                        type: 'assistant'
                    });
                }
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
        } catch (error: any) {
            AIMOSLogger.error('CUSTOM_CHAT', 'Failed to send to Cursor', error);

            // Show error in panel
            if (CustomChatPanel.currentPanel) {
                CustomChatPanel.currentPanel.webview.postMessage({
                    command: 'error',
                    text: error.message || 'Failed to send to Cursor'
                });
            }
        }
    }

    /**
     * Clear chat
     */
    private static clearChat(): void {
        AIMOSLogger.log('CUSTOM_CHAT', 'Chat cleared');
        // Panel will handle UI update via message
    }

    /**
     * Add message to chat panel
     */
    public static addMessage(text: string, type: 'user' | 'assistant' = 'assistant'): void {
        if (CustomChatPanel.currentPanel) {
            CustomChatPanel.currentPanel.webview.postMessage({
                command: 'addMessage',
                text: text,
                type: type
            });
        }
    }
}
