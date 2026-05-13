/**
 * Dead Letter Queue Manager
 * 
 * Stores failed messages that cannot be processed after retries
 * Enables manual review, retry, and analysis of failures
 */

import * as fs from 'fs';
import * as path from 'path';
import * as vscode from 'vscode';
import { Envelope } from './envelope';
import { KV, FileKV, MemoryKV } from './kv';

export interface DeadLetterEntry {
    envelope: Envelope;
    reason: string;
    error: {
        code: string;
        message: string;
        data?: any;
    };
    attempts: number;
    firstAttempt: number;
    lastAttempt: number;
    timestamp: number;
}

export class DeadLetterQueueManager {
    private queue: DeadLetterEntry[] = [];
    private storagePath: string = '';
    private maxSize: number = 1000; // Max entries to keep
    private kv: KV | null = null; // Optional KV for testability

    constructor(context: vscode.ExtensionContext, kv?: KV) {
        if (kv) {
            // Use provided KV (for testing)
            this.kv = kv;
        } else {
            // Use file-based storage (production)
            // Store in workspace .aimos directory
            const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
            if (workspaceFolder) {
                this.storagePath = path.join(workspaceFolder.uri.fsPath, '.aimos', 'dead_letter_queue.json');
            } else {
                // Fallback to global storage
                this.storagePath = path.join(context.globalStorageUri.fsPath, 'dead_letter_queue.json');
            }

            // Ensure directory exists
            const dir = path.dirname(this.storagePath);
            if (!fs.existsSync(dir)) {
                fs.mkdirSync(dir, { recursive: true });
            }

            // Load dead letter queue on startup
            this.loadQueue().catch(console.error);
        }
    }

    /**
     * Load dead letter queue from disk (or KV)
     */
    private async loadQueue(): Promise<void> {
        if (this.kv) {
            // Use KV storage
            this.queue = await this.kv.read();
            return;
        }
        
        // Use file-based storage
        try {
            if (fs.existsSync(this.storagePath)) {
                const data = fs.readFileSync(this.storagePath, 'utf8');
                const entries = JSON.parse(data) as DeadLetterEntry[];
                
                // Keep only most recent entries
                if (entries.length > this.maxSize) {
                    this.queue = entries.slice(-this.maxSize);
                    this.saveQueue(); // Trim file
                } else {
                    this.queue = entries;
                }
            }
        } catch (error) {
            console.error('Failed to load dead letter queue:', error);
            this.queue = [];
        }
    }

    /**
     * Save dead letter queue to disk (or KV)
     */
    private async saveQueue(): Promise<void> {
        if (this.kv) {
            // Use KV storage
            await this.kv.write(this.queue);
            return;
        }
        
        // Use file-based storage
        try {
            fs.writeFileSync(this.storagePath, JSON.stringify(this.queue, null, 2), 'utf8');
        } catch (error) {
            console.error('Failed to save dead letter queue:', error);
        }
    }

    /**
     * Add message to dead letter queue
     */
    async add(
        envelope: Envelope,
        reason: string,
        error: { code: string; message: string; data?: any },
        attempts: number = 0
    ): Promise<void> {
        if (this.kv) {
            await this.loadQueue();
        }
        
        const entry: DeadLetterEntry = {
            envelope,
            reason,
            error,
            attempts,
            firstAttempt: (envelope as any).firstAttempt || Date.now(),
            lastAttempt: Date.now(),
            timestamp: Date.now(),
        };

        this.queue.push(entry);

        // Trim if too large
        if (this.queue.length > this.maxSize) {
            this.queue = this.queue.slice(-this.maxSize);
        }

        // Save immediately
        await this.saveQueue();
    }

    /**
     * Get all dead letter entries
     */
    async getAll(): Promise<DeadLetterEntry[]> {
        if (this.kv) {
            await this.loadQueue();
        }
        return [...this.queue];
    }

    /**
     * Get dead letter entries filtered by criteria
     */
    async getFiltered(filters: {
        topic?: string;
        errorCode?: string;
        since?: number; // Timestamp
        limit?: number;
    }): Promise<DeadLetterEntry[]> {
        if (this.kv) {
            await this.loadQueue();
        }
        
        let filtered = this.queue;

        if (filters.topic) {
            filtered = filtered.filter(e => e.envelope.topic === filters.topic);
        }

        if (filters.errorCode) {
            filtered = filtered.filter(e => e.error.code === filters.errorCode);
        }

        if (filters.since) {
            filtered = filtered.filter(e => e.timestamp >= filters.since!);
        }

        if (filters.limit) {
            filtered = filtered.slice(-filters.limit);
        }

        return filtered;
    }

    /**
     * Retry dead letter entry (remove from DLQ and return envelope)
     */
    async retry(id: string): Promise<Envelope | null> {
        if (this.kv) {
            await this.loadQueue();
        }
        
        const index = this.queue.findIndex(e => e.envelope.id === id);
        if (index === -1) return null;

        const entry = this.queue[index];
        this.queue.splice(index, 1);
        await this.saveQueue();

        return entry.envelope;
    }

    /**
     * Remove dead letter entry
     */
    async remove(id: string): Promise<boolean> {
        if (this.kv) {
            await this.loadQueue();
        }
        
        const index = this.queue.findIndex(e => e.envelope.id === id);
        if (index === -1) return false;

        this.queue.splice(index, 1);
        await this.saveQueue();
        return true;
    }

    /**
     * Clear dead letter queue
     */
    async clear(): Promise<void> {
        this.queue = [];
        if (this.kv) {
            await this.kv.write([]);
        } else if (fs.existsSync(this.storagePath)) {
            fs.unlinkSync(this.storagePath);
        }
    }

    /**
     * Get statistics
     */
    async getStats(): Promise<{
        count: number;
        byTopic: Record<string, number>;
        byErrorCode: Record<string, number>;
        oldest: number | null;
        newest: number | null;
    }> {
        if (this.kv) {
            await this.loadQueue();
        }
        
        const byTopic: Record<string, number> = {};
        const byErrorCode: Record<string, number> = {};
        let oldest: number | null = null;
        let newest: number | null = null;

        for (const entry of this.queue) {
            // Count by topic
            byTopic[entry.envelope.topic] = (byTopic[entry.envelope.topic] || 0) + 1;

            // Count by error code
            byErrorCode[entry.error.code] = (byErrorCode[entry.error.code] || 0) + 1;

            // Track oldest/newest
            if (oldest === null || entry.timestamp < oldest) {
                oldest = entry.timestamp;
            }
            if (newest === null || entry.timestamp > newest) {
                newest = entry.timestamp;
            }
        }

        return {
            count: this.queue.length,
            byTopic,
            byErrorCode,
            oldest,
            newest,
        };
    }
}

