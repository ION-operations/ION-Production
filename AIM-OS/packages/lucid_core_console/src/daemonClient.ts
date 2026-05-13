import { WebSocket } from 'ws';
import { TimelineLogger } from './timelineLogger';

export interface DaemonMessage {
    type: string;
    [key: string]: any;
}

export interface ProcessInputResponse {
    type: 'success' | 'error' | 'approval_required';
    text: string;
    changeId?: string;
    confidence?: number;
    blastRadius?: string;
}

export class DaemonClient {
    private _ws?: WebSocket;
    private _timelineLogger: TimelineLogger;
    private _isConnected: boolean = false;
    private _messageHandlers: ((message: DaemonMessage) => void)[] = [];
    private _reconnectAttempts: number = 0;
    private _maxReconnectAttempts: number = 5;
    private _reconnectDelay: number = 1000;

    constructor(timelineLogger: TimelineLogger) {
        this._timelineLogger = timelineLogger;
        this._connect();
    }

    private _connect() {
        const host = process.env.LUCID_DAEMON_HOST || 'localhost';
        const port = process.env.LUCID_DAEMON_PORT || '8080';
        const url = `ws://${host}:${port}/daemon`;
        
        try {
            this._ws = new WebSocket(url);
            
            this._ws.on('open', () => {
                this._isConnected = true;
                this._reconnectAttempts = 0;
                this._timelineLogger.log('daemon_connected', { 
                    timestamp: Date.now(),
                    url: url
                });
            });
            
            this._ws.on('message', (data) => {
                try {
                    const message = JSON.parse(data.toString());
                    this._handleDaemonMessage(message);
                } catch (error) {
                    this._timelineLogger.log('daemon_message_parse_error', {
                        error: error.message,
                        data: data.toString(),
                        timestamp: Date.now()
                    });
                }
            });
            
            this._ws.on('close', () => {
                this._isConnected = false;
                this._timelineLogger.log('daemon_disconnected', { 
                    timestamp: Date.now()
                });
                this._attemptReconnect();
            });
            
            this._ws.on('error', (error) => {
                this._timelineLogger.log('daemon_connection_error', {
                    error: error.message,
                    timestamp: Date.now()
                });
            });
        } catch (error) {
            this._timelineLogger.log('daemon_connection_failed', {
                error: error.message,
                url: url,
                timestamp: Date.now()
            });
            this._attemptReconnect();
        }
    }

    private _attemptReconnect() {
        if (this._reconnectAttempts < this._maxReconnectAttempts) {
            this._reconnectAttempts++;
            const delay = this._reconnectDelay * Math.pow(2, this._reconnectAttempts - 1);
            
            this._timelineLogger.log('daemon_reconnect_attempt', {
                attempt: this._reconnectAttempts,
                delay: delay,
                timestamp: Date.now()
            });
            
            setTimeout(() => {
                this._connect();
            }, delay);
        } else {
            this._timelineLogger.log('daemon_reconnect_failed', {
                maxAttempts: this._maxReconnectAttempts,
                timestamp: Date.now()
            });
        }
    }

    public async processInput(input: string): Promise<ProcessInputResponse> {
        if (!this._isConnected || !this._ws) {
            throw new Error('Daemon not connected');
        }

        const request = {
            type: 'processInput',
            input: input,
            timestamp: Date.now()
        };

        this._ws.send(JSON.stringify(request));
        
        // Wait for response
        return new Promise((resolve, reject) => {
            const timeout = setTimeout(() => {
                reject(new Error('Request timeout'));
            }, 30000); // 30 second timeout

            const handler = (data: any) => {
                try {
                    const message = JSON.parse(data.toString());
                    if (message.type === 'processInputResponse') {
                        clearTimeout(timeout);
                        this._ws?.off('message', handler);
                        resolve(message.response);
                    }
                } catch (error) {
                    clearTimeout(timeout);
                    this._ws?.off('message', handler);
                    reject(error);
                }
            };
            this._ws.on('message', handler);
        });
    }

    public async approveChange(changeId: string): Promise<void> {
        if (!this._isConnected || !this._ws) {
            throw new Error('Daemon not connected');
        }

        const request = {
            type: 'approveChange',
            changeId: changeId,
            timestamp: Date.now()
        };

        this._ws.send(JSON.stringify(request));
        
        this._timelineLogger.log('change_approval_sent', {
            changeId: changeId,
            timestamp: Date.now()
        });
    }

    public async forceEdit(changeId: string): Promise<void> {
        if (!this._isConnected || !this._ws) {
            throw new Error('Daemon not connected');
        }

        const request = {
            type: 'forceEdit',
            changeId: changeId,
            timestamp: Date.now()
        };

        this._ws.send(JSON.stringify(request));
        
        this._timelineLogger.log('force_edit_sent', {
            changeId: changeId,
            timestamp: Date.now()
        });
    }

    public onMessage(handler: (message: DaemonMessage) => void) {
        this._messageHandlers.push(handler);
    }

    private _handleDaemonMessage(message: DaemonMessage) {
        this._timelineLogger.log('daemon_message_received', {
            type: message.type,
            timestamp: Date.now()
        });

        // Notify all handlers
        this._messageHandlers.forEach(handler => {
            try {
                handler(message);
            } catch (error) {
                this._timelineLogger.log('daemon_message_handler_error', {
                    error: error.message,
                    messageType: message.type,
                    timestamp: Date.now()
                });
            }
        });

        // Handle specific message types
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
            case 'connectionStatus':
                this._handleConnectionStatus(message);
                break;
        }
    }

    private _handleFileMutationRequest(message: DaemonMessage) {
        // This will be handled by the message handlers
        this._timelineLogger.log('file_mutation_request_received', {
            changeId: message.changeId,
            description: message.description,
            timestamp: Date.now()
        });
    }

    private _handleDriftAlert(message: DaemonMessage) {
        this._timelineLogger.log('drift_alert_received', {
            alert: message.alert,
            severity: message.severity,
            timestamp: Date.now()
        });
    }

    private _handleApprovalRequired(message: DaemonMessage) {
        this._timelineLogger.log('approval_required_received', {
            changeId: message.changeId,
            reason: message.reason,
            timestamp: Date.now()
        });
    }

    private _handleConnectionStatus(message: DaemonMessage) {
        this._isConnected = message.connected;
        this._timelineLogger.log('connection_status_updated', {
            connected: message.connected,
            timestamp: Date.now()
        });
    }

    public get isConnected(): boolean {
        return this._isConnected;
    }

    public dispose() {
        if (this._ws) {
            this._ws.close();
            this._ws = undefined;
        }
        this._messageHandlers = [];
        this._isConnected = false;
    }
}
