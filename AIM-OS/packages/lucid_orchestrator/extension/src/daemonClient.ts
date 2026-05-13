import * as vscode from 'vscode';
import WebSocket from 'ws';

export interface SpecBlock {
    node_id: string;
    responsibility: string;
    must_never: string[];
    inputs: string[];
    outputs: string[];
    side_effects: string[];
    security_level: string;
    perf_budget_ms: number;
    status: string;
    drift_reason?: string;
    governance?: any;
}

export interface BlueprintNode {
    node_id: string;
    name: string;
    kind: string;
    status: string;
    security_level?: string;
}

export interface BlueprintEdge {
    node_id: string;
    name: string;
    kind: string;
    status: string;
    security_level?: string;
    edge_type: string;
}

export interface BlueprintSlice {
    center: BlueprintNode;
    incoming: BlueprintEdge[];
    outgoing: BlueprintEdge[];
    blast_radius: {
        direct: number;
        indirect: number;
        risk_score: number;
    };
}

export interface TimelineRun {
    timestamp: number;
    duration_ms: number;
    thread: string;
    status: string;
    violations: string[];
}

export interface TimelineCascade {
    symbol: string;
    action: string;
    duration_ms: number;
    thread?: string;
}

export interface TimelineSummary {
    node_id: string;
    recent_runs: TimelineRun[];
    worst_run_cascade: TimelineCascade[];
}

export interface ChangeProposal {
    node_id: string;
    blast_radius_summary: any;
    affected_specs: any[];
    high_security_nodes: string[];
    risk_factors: string[];
    required_mitigations: string[];
    governance_template: any;
}

export class DaemonClient {
    private ws: WebSocket | null = null;
    private url: string;
    private reconnectAttempts = 0;
    private maxReconnectAttempts = 5;
    private reconnectDelay = 1000;

    constructor(url: string) {
        this.url = url;
        this.connect();
    }

    private connect() {
        try {
            this.ws = new WebSocket(this.url);
            
            this.ws.on('open', () => {
                console.log('Connected to Lucid Daemon');
                this.reconnectAttempts = 0;
            });

            this.ws.on('error', (error) => {
                console.error('WebSocket error:', error);
                this.handleReconnect();
            });

            this.ws.on('close', () => {
                console.log('Disconnected from Lucid Daemon');
                this.handleReconnect();
            });

            this.ws.on('message', (data) => {
                // Handle incoming messages if needed
                console.log('Received message from daemon:', data.toString());
            });

        } catch (error) {
            console.error('Failed to connect to daemon:', error);
            this.handleReconnect();
        }
    }

    private handleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
            
            setTimeout(() => {
                this.connect();
            }, this.reconnectDelay * this.reconnectAttempts);
        } else {
            console.error('Max reconnection attempts reached');
            vscode.window.showErrorMessage('Failed to connect to Lucid Daemon. Please ensure the daemon is running.');
        }
    }

    private async sendRequest(method: string, params: any = {}): Promise<any> {
        return new Promise((resolve, reject) => {
            if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
                reject(new Error('WebSocket not connected'));
                return;
            }

            const requestId = Math.random().toString(36).substr(2, 9);
            const request = {
                jsonrpc: '2.0',
                id: requestId,
                method: method,
                params: params
            };

            const timeout = setTimeout(() => {
                reject(new Error('Request timeout'));
            }, 10000);

            const messageHandler = (data: any) => {
                try {
                    const response = JSON.parse(data.toString());
                    if (response.id === requestId) {
                        clearTimeout(timeout);
                        this.ws?.off('message', messageHandler);
                        
                        if (response.error) {
                            reject(new Error(response.error.message || 'Unknown error'));
                        } else {
                            resolve(response.result);
                        }
                    }
                } catch (error) {
                    // Ignore non-JSON messages
                }
            };

            this.ws.on('message', messageHandler);
            this.ws.send(JSON.stringify(request));
        });
    }

    async getSpecBlock(nodeId: string): Promise<SpecBlock> {
        return await this.sendRequest('getSpecBlock', { nodeId });
    }

    async getBlueprintSlice(nodeId: string, depth: number = 1): Promise<BlueprintSlice> {
        return await this.sendRequest('getBlueprintSlice', { nodeId, depth });
    }

    async getTimelineSummary(nodeId: string, limit: number = 10): Promise<TimelineSummary> {
        return await this.sendRequest('getTimelineSummary', { nodeId, limit });
    }

    async proposeChange(nodeId: string): Promise<ChangeProposal> {
        return await this.sendRequest('proposeChange', { nodeId });
    }

    async focusNode(nodeId: string): Promise<any> {
        return await this.sendRequest('focusNode', { nodeId });
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }
}
