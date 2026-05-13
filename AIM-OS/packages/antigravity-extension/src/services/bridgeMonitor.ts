import * as http from 'http';
import { GhostStatus } from '../types';

/**
 * Monitors the ghost bridge at Victus (192.168.2.25:9090).
 * Polls /health endpoint and checks for new messages.
 */
export class BridgeMonitor {
    private bridgeUrl: string;
    private lastMessageId = 0;
    private lastStatus: GhostStatus = {
        bridgeHealthy: false,
        lastChecked: new Date().toISOString(),
        latencyMs: null,
        lastMessageTimestamp: null,
        unreadCount: 0
    };

    constructor(bridgeUrl: string = 'http://192.168.2.25:9090') {
        this.bridgeUrl = bridgeUrl;
    }

    /**
     * Check ghost bridge health via GET /health.
     */
    async checkHealth(): Promise<GhostStatus> {
        const start = Date.now();
        try {
            const response = await this.httpGet(`${this.bridgeUrl}/health`, 5000);
            const latency = Date.now() - start;
            this.lastStatus = {
                bridgeHealthy: true,
                lastChecked: new Date().toISOString(),
                latencyMs: latency,
                lastMessageTimestamp: this.lastStatus.lastMessageTimestamp,
                unreadCount: this.lastStatus.unreadCount
            };
        } catch {
            this.lastStatus = {
                bridgeHealthy: false,
                lastChecked: new Date().toISOString(),
                latencyMs: null,
                lastMessageTimestamp: this.lastStatus.lastMessageTimestamp,
                unreadCount: this.lastStatus.unreadCount
            };
        }
        return this.lastStatus;
    }

    /**
     * Send a message to the ghost via POST /message.
     */
    async sendMessage(from: string, content: string): Promise<boolean> {
        try {
            await this.httpPost(`${this.bridgeUrl}/message`, { from, content });
            return true;
        } catch {
            return false;
        }
    }

    /**
     * Poll for new messages from ghost via GET /messages?since=N.
     */
    async pollMessages(): Promise<{ messages: Array<{ id: number; from: string; content: string; timestamp: string }> }> {
        try {
            const response = await this.httpGet(`${this.bridgeUrl}/messages?since=${this.lastMessageId}`, 5000);
            const data = JSON.parse(response);
            if (data.messages && data.messages.length > 0) {
                const maxId = Math.max(...data.messages.map((m: { id: number }) => m.id));
                this.lastMessageId = maxId;
                this.lastStatus.unreadCount += data.messages.length;
                this.lastStatus.lastMessageTimestamp = data.messages[data.messages.length - 1].timestamp;
            }
            return data;
        } catch {
            return { messages: [] };
        }
    }

    /** Mark messages as read */
    markRead(): void {
        this.lastStatus.unreadCount = 0;
    }

    /** Get cached status */
    getLastStatus(): GhostStatus {
        return this.lastStatus;
    }

    /** Update bridge URL from settings */
    setBridgeUrl(url: string): void {
        this.bridgeUrl = url;
    }

    // --- HTTP helpers ---

    private httpGet(url: string, timeoutMs: number): Promise<string> {
        return new Promise((resolve, reject) => {
            const req = http.get(url, { timeout: timeoutMs }, (res) => {
                let data = '';
                res.on('data', chunk => { data += chunk; });
                res.on('end', () => resolve(data));
            });
            req.on('error', reject);
            req.on('timeout', () => { req.destroy(); reject(new Error('timeout')); });
        });
    }

    private httpPost(url: string, body: Record<string, unknown>): Promise<string> {
        return new Promise((resolve, reject) => {
            const bodyStr = JSON.stringify(body);
            const urlObj = new URL(url);
            const req = http.request({
                hostname: urlObj.hostname,
                port: urlObj.port,
                path: urlObj.pathname,
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(bodyStr) },
                timeout: 10000
            }, (res) => {
                let data = '';
                res.on('data', chunk => { data += chunk; });
                res.on('end', () => resolve(data));
            });
            req.on('error', reject);
            req.on('timeout', () => { req.destroy(); reject(new Error('timeout')); });
            req.write(bodyStr);
            req.end();
        });
    }
}
