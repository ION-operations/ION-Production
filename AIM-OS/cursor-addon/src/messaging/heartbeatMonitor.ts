/**
 * Heartbeat Monitor
 * 
 * Monitors connection health between UI and Extension
 * Sends periodic heartbeats and measures RTT
 */

import * as vscode from 'vscode';
import { Envelope, createHeartbeatEnvelope } from './envelope';

export interface HeartbeatStats {
    rtt: number; // Round-trip time in ms
    status: 'healthy' | 'degraded' | 'broken';
    lastHeartbeat: number;
    missedBeats: number;
}

export class HeartbeatMonitor {
    private webview: vscode.Webview | null = null;
    private interval: number = 10000; // 10 seconds
    private timer: NodeJS.Timeout | null = null;
    private stats: HeartbeatStats = {
        rtt: 0,
        status: 'healthy',
        lastHeartbeat: Date.now(),
        missedBeats: 0,
    };
    private pendingHeartbeats: Map<string, number> = new Map(); // id -> timestamp
    private listeners: Array<(stats: HeartbeatStats) => void> = [];

    constructor(interval: number = 10000) {
        this.interval = interval;
    }

    /**
     * Set webview for sending heartbeats
     */
    setWebview(webview: vscode.Webview): void {
        this.webview = webview;
        
        // Listen for heartbeat echoes
        webview.onDidReceiveMessage((message: any) => {
            if (message.kind === 'ack' && message.replyTo) {
                const heartbeatId = message.replyTo;
                const sentTime = this.pendingHeartbeats.get(heartbeatId);
                if (sentTime) {
                    const rtt = Date.now() - sentTime;
                    this.pendingHeartbeats.delete(heartbeatId);
                    this.updateStats(rtt);
                }
            }
        });
    }

    /**
     * Start heartbeat monitoring
     */
    start(): void {
        if (this.timer) return; // Already started

        this.timer = setInterval(() => {
            this.sendHeartbeat();
        }, this.interval);
    }

    /**
     * Stop heartbeat monitoring
     */
    stop(): void {
        if (this.timer) {
            clearInterval(this.timer);
            this.timer = null;
        }
    }

    /**
     * Send heartbeat
     */
    private sendHeartbeat(): void {
        if (!this.webview) return;

        const heartbeat = createHeartbeatEnvelope('ext->ui');
        this.pendingHeartbeats.set(heartbeat.id, Date.now());
        this.webview.postMessage(heartbeat);

        // Check for missed beats
        const now = Date.now();
        if (now - this.stats.lastHeartbeat > this.interval * 3) {
            this.stats.missedBeats++;
            this.updateStats(0); // No response
        }
    }

    /**
     * Update statistics
     */
    private updateStats(rtt: number): void {
        this.stats.rtt = rtt;
        this.stats.lastHeartbeat = Date.now();
        this.stats.missedBeats = 0;

        // Determine status
        if (rtt === 0 || rtt > 2000) {
            this.stats.status = 'broken';
        } else if (rtt > 500) {
            this.stats.status = 'degraded';
        } else {
            this.stats.status = 'healthy';
        }

        // Notify listeners
        this.listeners.forEach(listener => listener(this.stats));
    }

    /**
     * Get current statistics
     */
    getStats(): HeartbeatStats {
        return { ...this.stats };
    }

    /**
     * Add listener for stats updates
     */
    onStatsUpdate(listener: (stats: HeartbeatStats) => void): void {
        this.listeners.push(listener);
    }

    /**
     * Remove listener
     */
    removeStatsListener(listener: (stats: HeartbeatStats) => void): void {
        const index = this.listeners.indexOf(listener);
        if (index !== -1) {
            this.listeners.splice(index, 1);
        }
    }
}

