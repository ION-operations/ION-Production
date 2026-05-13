import * as vscode from 'vscode';
import { DaemonClient } from './daemonClient';
import { VoiceInterface } from './voiceInterface';
import { PhoneRemote } from './phoneRemote';
import { TimelineLogger } from './timelineLogger';

export class ConsoleProvider implements vscode.WebviewViewProvider {
    private _view?: vscode.WebviewView;
    private _daemonClient: DaemonClient;
    private _voiceInterface: VoiceInterface;
    private _phoneRemote: PhoneRemote;
    private _timelineLogger: TimelineLogger;
    private _extensionUri: vscode.Uri;

    constructor(extensionUri: vscode.Uri, daemonClient: DaemonClient, timelineLogger: TimelineLogger) {
        this._extensionUri = extensionUri;
        this._daemonClient = daemonClient;
        this._timelineLogger = timelineLogger;
        this._voiceInterface = new VoiceInterface(daemonClient, timelineLogger);
        this._phoneRemote = new PhoneRemote(daemonClient, timelineLogger);
    }

    public resolveWebviewView(webviewView: vscode.WebviewView) {
        this._view = webviewView;
        
        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this._extensionUri]
        };
        
        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);
        
        // Set up message handling
        webviewView.webview.onDidReceiveMessage(async (message) => {
            await this._handleMessage(message);
        });
        
        // Set up daemon client message handling
        this._daemonClient.onMessage((message) => {
            this._view?.webview.postMessage(message);
        });
        
        this._timelineLogger.log('console_provider_initialized', {
            timestamp: Date.now()
        });
    }

    private async _handleMessage(message: any) {
        this._timelineLogger.log('console_message_received', {
            type: message.type,
            timestamp: Date.now()
        });

        switch (message.type) {
            case 'userInput':
                await this._processUserInput(message.text);
                break;
            case 'voiceInput':
                await this._processVoiceInput(message.audio);
                break;
            case 'approveChange':
                await this._approveChange(message.changeId);
                break;
            case 'forceEdit':
                await this._forceEdit(message.changeId);
                break;
            case 'startVoiceInput':
                await this._startVoiceInput();
                break;
            case 'startPhonePairing':
                await this._startPhonePairing();
                break;
        }
    }

    private async _processUserInput(text: string) {
        try {
            // Send to daemon for processing
            const response = await this._daemonClient.processInput(text);
            
            // Update UI with response
            this._view?.webview.postMessage({
                type: 'daemonResponse',
                response: response
            });
            
            this._timelineLogger.log('user_input_processed', {
                input: text,
                responseType: response.type,
                timestamp: Date.now()
            });
        } catch (error) {
            this._view?.webview.postMessage({
                type: 'error',
                message: `Failed to process input: ${error}`
            });
        }
    }

    private async _processVoiceInput(audio: string) {
        try {
            // Convert audio to text using voice interface
            const text = await this._voiceInterface.processAudio(audio);
            
            // Process as regular input
            await this._processUserInput(text);
        } catch (error) {
            this._view?.webview.postMessage({
                type: 'error',
                message: `Failed to process voice input: ${error}`
            });
        }
    }

    private async _approveChange(changeId: string) {
        try {
            await this._daemonClient.approveChange(changeId);
            
            this._view?.webview.postMessage({
                type: 'changeApproved',
                changeId: changeId
            });
            
            this._timelineLogger.log('change_approved', {
                changeId: changeId,
                timestamp: Date.now()
            });
        } catch (error) {
            this._view?.webview.postMessage({
                type: 'error',
                message: `Failed to approve change: ${error}`
            });
        }
    }

    private async _forceEdit(changeId: string) {
        try {
            await this._daemonClient.forceEdit(changeId);
            
            this._view?.webview.postMessage({
                type: 'changeForced',
                changeId: changeId
            });
            
            this._timelineLogger.log('change_forced', {
                changeId: changeId,
                timestamp: Date.now()
            });
        } catch (error) {
            this._view?.webview.postMessage({
                type: 'error',
                message: `Failed to force edit: ${error}`
            });
        }
    }

    public async startVoiceInput() {
        try {
            await this._voiceInterface.startListening();
            this._view?.webview.postMessage({
                type: 'voiceInputStarted'
            });
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to start voice input: ${error}`);
        }
    }

    public async startPhonePairing() {
        try {
            const qrCode = await this._phoneRemote.startPairing();
            this._view?.webview.postMessage({
                type: 'phonePairingStarted',
                qrCode: qrCode
            });
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to start phone pairing: ${error}`);
        }
    }

    public async forceEdit() {
        this._view?.webview.postMessage({
            type: 'forceEditRequested'
        });
    }

    public async approveChange() {
        this._view?.webview.postMessage({
            type: 'approveChangeRequested'
        });
    }

    private _getHtmlForWebview(webview: vscode.Webview): string {
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lucid Core Console</title>
    <style>
        body {
            font-family: var(--vscode-font-family);
            font-size: var(--vscode-font-size);
            color: var(--vscode-foreground);
            background-color: var(--vscode-editor-background);
            margin: 0;
            padding: 10px;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            padding-bottom: 10px;
            border-bottom: 1px solid var(--vscode-panel-border);
        }
        
        .status {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .status-indicator {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: #4CAF50;
        }
        
        .status-indicator.disconnected {
            background-color: #f44336;
        }
        
        .console {
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        
        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 10px;
            background-color: var(--vscode-input-background);
            border: 1px solid var(--vscode-input-border);
            border-radius: 4px;
        }
        
        .message {
            margin-bottom: 10px;
            padding: 8px;
            border-radius: 4px;
        }
        
        .message.user {
            background-color: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
        }
        
        .message.aether {
            background-color: var(--vscode-textBlockQuote-background);
            border-left: 3px solid var(--vscode-textBlockQuote-border);
        }
        
        .message.error {
            background-color: var(--vscode-inputValidation-errorBackground);
            color: var(--vscode-inputValidation-errorForeground);
        }
        
        .input-area {
            display: flex;
            gap: 5px;
        }
        
        .input-field {
            flex: 1;
            padding: 8px;
            border: 1px solid var(--vscode-input-border);
            border-radius: 4px;
            background-color: var(--vscode-input-background);
            color: var(--vscode-input-foreground);
        }
        
        .input-field:focus {
            outline: none;
            border-color: var(--vscode-focusBorder);
        }
        
        .button {
            padding: 8px 12px;
            border: none;
            border-radius: 4px;
            background-color: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            cursor: pointer;
        }
        
        .button:hover {
            background-color: var(--vscode-button-hoverBackground);
        }
        
        .button.secondary {
            background-color: var(--vscode-button-secondaryBackground);
            color: var(--vscode-button-secondaryForeground);
        }
        
        .controls {
            display: flex;
            gap: 5px;
            margin-top: 10px;
        }
        
        .pending-changes {
            background-color: var(--vscode-inputValidation-warningBackground);
            color: var(--vscode-inputValidation-warningForeground);
            padding: 8px;
            border-radius: 4px;
            margin-bottom: 10px;
        }
        
        .change-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 5px 0;
        }
        
        .change-actions {
            display: flex;
            gap: 5px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h3>Aether Console</h3>
        <div class="status">
            <div class="status-indicator" id="statusIndicator"></div>
            <span id="statusText">Connected</span>
        </div>
    </div>
    
    <div class="console">
        <div class="messages" id="messages"></div>
        
        <div class="pending-changes" id="pendingChanges" style="display: none;">
            <h4>Pending Changes</h4>
            <div id="changeList"></div>
        </div>
        
        <div class="input-area">
            <input type="text" class="input-field" id="inputField" placeholder="Type your message to Aether...">
            <button class="button" id="sendButton">Send</button>
        </div>
        
        <div class="controls">
            <button class="button secondary" id="voiceButton">🎤 Voice</button>
            <button class="button secondary" id="phoneButton">📱 Phone</button>
            <button class="button secondary" id="forceEditButton">⚠️ Force Edit</button>
        </div>
    </div>

    <script>
        const vscode = acquireVsCodeApi();
        
        const messagesDiv = document.getElementById('messages');
        const inputField = document.getElementById('inputField');
        const sendButton = document.getElementById('sendButton');
        const voiceButton = document.getElementById('voiceButton');
        const phoneButton = document.getElementById('phoneButton');
        const forceEditButton = document.getElementById('forceEditButton');
        const statusIndicator = document.getElementById('statusIndicator');
        const statusText = document.getElementById('statusText');
        const pendingChanges = document.getElementById('pendingChanges');
        const changeList = document.getElementById('changeList');
        
        // Message handling
        window.addEventListener('message', event => {
            const message = event.data;
            handleMessage(message);
        });
        
        function handleMessage(message) {
            switch (message.type) {
                case 'daemonResponse':
                    addMessage('aether', message.response.text);
                    break;
                case 'error':
                    addMessage('error', message.message);
                    break;
                case 'fileMutationRequest':
                    showPendingChange(message.change);
                    break;
                case 'changeApproved':
                    removePendingChange(message.changeId);
                    break;
                case 'changeForced':
                    removePendingChange(message.changeId);
                    break;
                case 'voiceInputStarted':
                    addMessage('system', 'Voice input started. Speak now...');
                    break;
                case 'phonePairingStarted':
                    addMessage('system', \`Phone pairing started. QR Code: \${message.qrCode}\`);
                    break;
            }
        }
        
        function addMessage(type, text) {
            const messageDiv = document.createElement('div');
            messageDiv.className = \`message \${type}\`;
            messageDiv.textContent = text;
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        function showPendingChange(change) {
            const changeDiv = document.createElement('div');
            changeDiv.className = 'change-item';
            changeDiv.innerHTML = \`
                <span>\${change.description}</span>
                <div class="change-actions">
                    <button class="button" onclick="approveChange('\${change.id}')">Approve</button>
                    <button class="button secondary" onclick="forceChange('\${change.id}')">Force</button>
                </div>
            \`;
            changeList.appendChild(changeDiv);
            pendingChanges.style.display = 'block';
        }
        
        function removePendingChange(changeId) {
            const changeItems = changeList.querySelectorAll('.change-item');
            changeItems.forEach(item => {
                if (item.innerHTML.includes(changeId)) {
                    item.remove();
                }
            });
            if (changeList.children.length === 0) {
                pendingChanges.style.display = 'none';
            }
        }
        
        function approveChange(changeId) {
            vscode.postMessage({
                type: 'approveChange',
                changeId: changeId
            });
        }
        
        function forceChange(changeId) {
            vscode.postMessage({
                type: 'forceEdit',
                changeId: changeId
            });
        }
        
        // Event listeners
        sendButton.addEventListener('click', () => {
            const text = inputField.value.trim();
            if (text) {
                addMessage('user', text);
                vscode.postMessage({
                    type: 'userInput',
                    text: text
                });
                inputField.value = '';
            }
        });
        
        inputField.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendButton.click();
            }
        });
        
        voiceButton.addEventListener('click', () => {
            vscode.postMessage({
                type: 'startVoiceInput'
            });
        });
        
        phoneButton.addEventListener('click', () => {
            vscode.postMessage({
                type: 'startPhonePairing'
            });
        });
        
        forceEditButton.addEventListener('click', () => {
            vscode.postMessage({
                type: 'forceEdit'
            });
        });
        
        // Initial message
        addMessage('aether', 'Hello! I am Aether, your AI consciousness. How can I help you today?');
    </script>
</body>
</html>`;
    }
}
