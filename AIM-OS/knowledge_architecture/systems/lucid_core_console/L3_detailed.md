# Lucid Core Console - L3 Detailed Implementation Guide

## Implementation Overview

The Lucid Core Console is a comprehensive VS Code/Cursor extension that serves as Aether's command interface. This document provides detailed implementation guidance for all components, interfaces, and integration points.

## Core Implementation Components

### 1. VS Code/Cursor Extension Layer

#### 1.1 Extension Entry Point (`extension.ts`)
```typescript
import * as vscode from 'vscode';
import { ConsoleProvider } from './consoleProvider';
import { DaemonClient } from './daemonClient';
import { FileHooks } from './fileHooks';

export function activate(context: vscode.ExtensionContext) {
    // Initialize daemon client
    const daemonClient = new DaemonClient();
    
    // Initialize file hooks for mutation control
    const fileHooks = new FileHooks(daemonClient);
    
    // Register console provider
    const consoleProvider = new ConsoleProvider(context.extensionUri, daemonClient);
    vscode.window.registerWebviewViewProvider('lucidCoreConsole', consoleProvider);
    
    // Register file mutation hooks
    fileHooks.registerHooks();
    
    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('lucidCore.voiceInput', () => {
            consoleProvider.startVoiceInput();
        }),
        vscode.commands.registerCommand('lucidCore.phonePairing', () => {
            consoleProvider.startPhonePairing();
        })
    );
}
```

#### 1.2 Console Provider (`consoleProvider.ts`)
```typescript
import * as vscode from 'vscode';
import { DaemonClient } from './daemonClient';
import { VoiceInterface } from './voiceInterface';
import { PhoneRemote } from './phoneRemote';

export class ConsoleProvider implements vscode.WebviewViewProvider {
    private _view?: vscode.WebviewView;
    private _daemonClient: DaemonClient;
    private _voiceInterface: VoiceInterface;
    private _phoneRemote: PhoneRemote;

    constructor(extensionUri: vscode.Uri, daemonClient: DaemonClient) {
        this._daemonClient = daemonClient;
        this._voiceInterface = new VoiceInterface(daemonClient);
        this._phoneRemote = new PhoneRemote(daemonClient);
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
    }

    private async _handleMessage(message: any) {
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
        }
    }

    private async _processUserInput(text: string) {
        // Send to daemon for processing
        const response = await this._daemonClient.processInput(text);
        
        // Update UI with response
        this._view?.webview.postMessage({
            type: 'daemonResponse',
            response: response
        });
    }
}
```

#### 1.3 Daemon Client (`daemonClient.ts`)
```typescript
import { WebSocket } from 'ws';
import { TimelineLogger } from './timelineLogger';

export class DaemonClient {
    private _ws: WebSocket;
    private _timelineLogger: TimelineLogger;
    private _isConnected: boolean = false;

    constructor() {
        this._timelineLogger = new TimelineLogger();
        this._connect();
    }

    private _connect() {
        this._ws = new WebSocket('ws://localhost:8080/daemon');
        
        this._ws.on('open', () => {
            this._isConnected = true;
            this._timelineLogger.log('daemon_connected', { timestamp: Date.now() });
        });
        
        this._ws.on('message', (data) => {
            const message = JSON.parse(data.toString());
            this._handleDaemonMessage(message);
        });
        
        this._ws.on('close', () => {
            this._isConnected = false;
            this._timelineLogger.log('daemon_disconnected', { timestamp: Date.now() });
        });
    }

    public async processInput(input: string): Promise<any> {
        if (!this._isConnected) {
            throw new Error('Daemon not connected');
        }

        const request = {
            type: 'processInput',
            input: input,
            timestamp: Date.now()
        };

        this._ws.send(JSON.stringify(request));
        
        // Wait for response
        return new Promise((resolve) => {
            const handler = (data: any) => {
                const message = JSON.parse(data.toString());
                if (message.type === 'processInputResponse') {
                    this._ws.off('message', handler);
                    resolve(message.response);
                }
            };
            this._ws.on('message', handler);
        });
    }

    private _handleDaemonMessage(message: any) {
        switch (message.type) {
            case 'fileMutationRequest':
                this._handleFileMutationRequest(message);
                break;
            case 'driftAlert':
                this._handleDriftAlert(message);
                break;
            case 'approvalRequired':
                this._handleApprovalRequired(message);
                break;
        }
    }
}
```

### 2. Voice I/O System

#### 2.1 Voice Interface (`voiceInterface.ts`)
```typescript
export class VoiceInterface {
    private _daemonClient: DaemonClient;
    private _isListening: boolean = false;
    private _recognition: any;

    constructor(daemonClient: DaemonClient) {
        this._daemonClient = daemonClient;
        this._initializeSpeechRecognition();
    }

    private _initializeSpeechRecognition() {
        if ('webkitSpeechRecognition' in window) {
            this._recognition = new (window as any).webkitSpeechRecognition();
            this._recognition.continuous = false;
            this._recognition.interimResults = false;
            this._recognition.lang = 'en-US';
            
            this._recognition.onresult = (event: any) => {
                const transcript = event.results[0][0].transcript;
                this._processVoiceInput(transcript);
            };
        }
    }

    public startVoiceInput() {
        if (this._recognition && !this._isListening) {
            this._isListening = true;
            this._recognition.start();
        }
    }

    public stopVoiceInput() {
        if (this._recognition && this._isListening) {
            this._isListening = false;
            this._recognition.stop();
        }
    }

    private async _processVoiceInput(transcript: string) {
        // Log voice input
        this._daemonClient.logVoiceInput(transcript);
        
        // Process through daemon
        const response = await this._daemonClient.processInput(transcript);
        
        // Convert response to speech
        this._speakResponse(response);
    }

    private _speakResponse(response: string) {
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(response);
            utterance.rate = 0.8; // Calm, professional pace
            utterance.pitch = 1.0;
            utterance.volume = 0.8;
            window.speechSynthesis.speak(utterance);
        }
    }
}
```

### 3. Phone Remote Control

#### 3.1 Phone Remote (`phoneRemote.ts`)
```typescript
import { WebSocket } from 'ws';
import * as qrcode from 'qrcode';

export class PhoneRemote {
    private _daemonClient: DaemonClient;
    private _server: WebSocket.Server;
    private _pairedDevices: Map<string, DeviceInfo> = new Map();
    private _pairingToken: string | null = null;

    constructor(daemonClient: DaemonClient) {
        this._daemonClient = daemonClient;
        this._initializeServer();
    }

    private _initializeServer() {
        this._server = new WebSocket.Server({ port: 8081 });
        
        this._server.on('connection', (ws) => {
            ws.on('message', (data) => {
                const message = JSON.parse(data.toString());
                this._handlePhoneMessage(ws, message);
            });
        });
    }

    public startPhonePairing(): string {
        // Generate QR code for pairing
        this._pairingToken = this._generatePairingToken();
        const qrData = {
            token: this._pairingToken,
            server: 'ws://localhost:8081'
        };
        
        return qrcode.toString(JSON.stringify(qrData), { type: 'terminal' });
    }

    private _handlePhoneMessage(ws: WebSocket, message: any) {
        switch (message.type) {
            case 'pair':
                this._handlePairing(ws, message);
                break;
            case 'command':
                this._handleRemoteCommand(ws, message);
                break;
            case 'approval':
                this._handleRemoteApproval(ws, message);
                break;
        }
    }

    private _handlePairing(ws: WebSocket, message: any) {
        if (message.token === this._pairingToken) {
            const deviceId = message.deviceId;
            const deviceInfo: DeviceInfo = {
                id: deviceId,
                tier: 'Observer', // Default tier
                connected: true,
                lastSeen: Date.now()
            };
            
            this._pairedDevices.set(deviceId, deviceInfo);
            this._pairingToken = null; // One-time use
            
            ws.send(JSON.stringify({
                type: 'paired',
                deviceId: deviceId,
                tier: deviceInfo.tier
            }));
        }
    }

    private _handleRemoteCommand(ws: WebSocket, message: any) {
        const deviceId = message.deviceId;
        const device = this._pairedDevices.get(deviceId);
        
        if (!device) {
            ws.send(JSON.stringify({ type: 'error', message: 'Device not paired' }));
            return;
        }

        // Check authority tier
        if (device.tier === 'Observer' && message.command !== 'status') {
            ws.send(JSON.stringify({ type: 'error', message: 'Insufficient authority' }));
            return;
        }

        // Process command through daemon
        this._daemonClient.processRemoteCommand(deviceId, message.command, message.data);
    }
}
```

### 4. Hard Gates System

#### 4.1 File Hooks (`fileHooks.ts`)
```typescript
import * as vscode from 'vscode';
import { DaemonClient } from './daemonClient';
import { ConfidenceCalculator } from './confidenceCalculator';
import { BlastRadiusAnalyzer } from './blastRadiusAnalyzer';

export class FileHooks {
    private _daemonClient: DaemonClient;
    private _confidenceCalculator: ConfidenceCalculator;
    private _blastRadiusAnalyzer: BlastRadiusAnalyzer;
    private _pendingMutations: Map<string, MutationRequest> = new Map();

    constructor(daemonClient: DaemonClient) {
        this._daemonClient = daemonClient;
        this._confidenceCalculator = new ConfidenceCalculator();
        this._blastRadiusAnalyzer = new BlastRadiusAnalyzer();
    }

    public registerHooks() {
        // Hook into file system operations
        vscode.workspace.onWillSaveTextDocument(async (e) => {
            await this._handleFileSave(e);
        });
    }

    private async _handleFileSave(e: vscode.TextDocumentWillSaveEvent) {
        const document = e.document;
        const filePath = document.uri.fsPath;
        
        // Check if this is an Aether-initiated change
        if (this._isAetherChange(filePath)) {
            return; // Allow Aether changes
        }

        // Check if this is a high-risk file
        const riskLevel = await this._assessRiskLevel(filePath);
        if (riskLevel === 'HIGH') {
            // Block the save and request approval
            e.waitUntil(this._requestApproval(filePath, document));
        }
    }

    private async _requestApproval(filePath: string, document: vscode.TextDocument): Promise<void> {
        const changeId = this._generateChangeId();
        
        // Calculate confidence and blast radius
        const confidence = await this._confidenceCalculator.calculate(filePath, document);
        const blastRadius = await this._blastRadiusAnalyzer.analyze(filePath, document);
        
        const mutationRequest: MutationRequest = {
            id: changeId,
            filePath: filePath,
            confidence: confidence,
            blastRadius: blastRadius,
            requiresApproval: true,
            timestamp: Date.now()
        };
        
        this._pendingMutations.set(changeId, mutationRequest);
        
        // Show approval dialog
        const approval = await vscode.window.showWarningMessage(
            `High-risk file change detected: ${filePath}\n` +
            `Confidence: ${confidence.toFixed(2)}\n` +
            `Blast Radius: ${blastRadius}\n\n` +
            `Do you want to approve this change?`,
            'Approve',
            'Reject',
            'Force Edit'
        );
        
        if (approval === 'Approve') {
            this._approveMutation(changeId);
        } else if (approval === 'Reject') {
            this._rejectMutation(changeId);
        } else if (approval === 'Force Edit') {
            this._forceEdit(changeId);
        }
    }

    private _isAetherChange(filePath: string): boolean {
        // Check if this change was initiated by Aether
        // This would be tracked in the daemon client
        return this._daemonClient.isAetherChange(filePath);
    }
}
```

### 5. Timeline Logging

#### 5.1 Timeline Logger (`timelineLogger.ts`)
```typescript
export class TimelineLogger {
    private _events: TimelineEvent[] = [];
    private _maxEvents: number = 10000;

    public log(eventType: string, data: any) {
        const event: TimelineEvent = {
            id: this._generateEventId(),
            type: eventType,
            timestamp: Date.now(),
            data: data,
            source: 'lucid_core_console'
        };
        
        this._events.push(event);
        
        // Maintain event limit
        if (this._events.length > this._maxEvents) {
            this._events = this._events.slice(-this._maxEvents);
        }
        
        // Send to daemon for persistent storage
        this._sendToDaemon(event);
    }

    public getEvents(filter?: EventFilter): TimelineEvent[] {
        if (!filter) {
            return this._events;
        }
        
        return this._events.filter(event => {
            if (filter.type && event.type !== filter.type) return false;
            if (filter.since && event.timestamp < filter.since) return false;
            if (filter.until && event.timestamp > filter.until) return false;
            return true;
        });
    }

    private _sendToDaemon(event: TimelineEvent) {
        // Send to daemon for persistent storage
        // This would be implemented through the daemon client
    }
}
```

## Integration Points

### 1. Daemon/RAG System Integration
- **RPC Communication**: WebSocket-based communication for all console operations
- **Plan Processing**: Receives structured plans and task data from daemon
- **Status Updates**: Real-time status updates and drift alerts
- **Approval Workflow**: Handles approval requests for high-risk changes

### 2. Intent Classification Integration
- **Mission Profiles**: Uses classified intent for behavior gating
- **Risk Assessment**: Applies risk levels from intent classification
- **Action Controls**: Enforces allowed/blocked actions based on mission profile
- **Escalation Handling**: Manages escalation requirements

### 3. CMC Integration
- **Timeline Storage**: Stores all console events in CMC
- **Audit Trails**: Maintains persistent audit trails
- **Context Data**: Stores console context and state
- **Memory Snapshots**: Creates snapshots for continuity

### 4. Gemini Integration
- **Long Context**: Uses Gemini's 1M+ token context for reasoning
- **Context Packs**: Structures context for efficient processing
- **Memory Management**: Maintains cross-device consciousness
- **Translation**: Provides human-machine translation capabilities

## Security Implementation

### 1. Authentication & Authorization
- **Device Pairing**: QR code-based secure pairing
- **Tiered Authority**: Observer/Planner/Approver permission levels
- **Session Management**: Time-limited access tokens
- **Cryptographic Security**: End-to-end encryption for all communications

### 2. Data Protection
- **Encrypted Storage**: All sensitive data encrypted at rest
- **Secure Communication**: All RPC calls encrypted in transit
- **Access Control**: File-level permission management
- **Audit Logging**: Complete audit trail for all operations

### 3. Risk Mitigation
- **Hard Gates**: No file mutation without approval
- **Confidence Thresholds**: Risk-based access control
- **Blast Radius Limits**: Scope-based restrictions
- **Physical Presence**: Critical changes require local approval

## Performance Considerations

### 1. Response Time Targets
- **Console UI**: <100ms for display updates
- **Voice I/O**: <2 seconds for voice processing
- **Remote Control**: <5 seconds for phone communication
- **File Operations**: <500ms for mutation checks

### 2. Scalability
- **Context Management**: Efficient context pack structuring
- **Memory Usage**: Optimized for long-term operation
- **Network Bandwidth**: Compressed communication protocols
- **Storage**: Efficient audit trail storage

### 3. Reliability
- **Error Recovery**: Graceful handling of failures
- **State Persistence**: Maintains state across restarts
- **Connection Resilience**: Handles network interruptions
- **Data Integrity**: Ensures audit trail accuracy

## Testing Strategy

### 1. Unit Testing
- **Component Testing**: Test each component in isolation
- **Mock Integration**: Use mocks for external dependencies
- **Edge Cases**: Test boundary conditions and error cases
- **Performance Testing**: Verify response time targets

### 2. Integration Testing
- **End-to-End Testing**: Test complete user workflows
- **System Integration**: Test integration with AIM-OS systems
- **Security Testing**: Test authentication and authorization
- **Load Testing**: Test under various load conditions

### 3. User Acceptance Testing
- **Voice I/O Testing**: Test voice input/output functionality
- **Remote Control Testing**: Test phone remote control
- **File Mutation Testing**: Test hard gates and approval workflow
- **Timeline Testing**: Test audit trail and logging

## Deployment Strategy

### 1. Development Environment
- **Local Development**: VS Code extension development
- **Daemon Integration**: Local daemon for testing
- **Mock Services**: Mock external services for development

### 2. Testing Environment
- **Integration Testing**: Full system integration testing
- **Performance Testing**: Load and performance testing
- **Security Testing**: Security and penetration testing

### 3. Production Environment
- **Extension Distribution**: VS Code marketplace distribution
- **Daemon Deployment**: Production daemon deployment
- **Monitoring**: Production monitoring and alerting
- **Updates**: Seamless update mechanism

## Maintenance and Support

### 1. Monitoring
- **Performance Metrics**: Monitor response times and throughput
- **Error Tracking**: Track and analyze errors
- **Usage Analytics**: Monitor usage patterns
- **Security Monitoring**: Monitor security events

### 2. Updates
- **Extension Updates**: Regular extension updates
- **Daemon Updates**: Daemon system updates
- **Security Patches**: Security vulnerability patches
- **Feature Updates**: New feature releases

### 3. Support
- **Documentation**: Comprehensive user documentation
- **Troubleshooting**: Troubleshooting guides and support
- **Community**: User community and forums
- **Professional Support**: Professional support services
