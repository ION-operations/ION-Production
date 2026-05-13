/**
 * Dead Letter Queue Manager (Refactored with KV Contract)
 * 
 * Stores failed messages that cannot be processed after retries
 * Uses KV abstraction for testability (FileKV or MemoryKV)
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
    private cache: DeadLetterEntry[] = [];
    private loaded = false;
    private kv: KV;
    private maxSize: number = 1000;

    constructor(context: vscode.ExtensionContext, kv?: KV) {
        if (kv) {
            // Use provided KV (for testing)
            this.kv = kv;
        } else {
            // Use file-based KV (production)
            const storagePath = this.getStoragePath(context);
            this.kv = new FileKV(storagePath);
        }
    }

    /**
     * Get storage path
     */
    private getStoragePath(context: vscode.ExtensionContext): string {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (workspaceFolder) {
            return path.join(workspaceFolder.uri.fsPath, '.aimos', 'dead_letter_queue.json');
        } else {
            return path.join(context.globalStorageUri.fsPath, 'dead_letter_queue.json');
        }
    }

    /**
     * Ensure cache is loaded
     */
    private async ensureLoaded(): Promise<void> {
        if (!this.loaded) {
            this.cache = await this.kv.read();
            this.loaded = true;
        }
    }

    /**
     * Persist cache to storage
     */
    private async persist(): Promise<void> {
        await this.kv.write(this.cache);
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
        await this.ensureLoaded();
        
        const entry: DeadLetterEntry = {
            envelope,
            reason,
            error,
            attempts,
            firstAttempt: (envelope as any).firstAttempt || Date.now(),
            lastAttempt: Date.now(),
            timestamp: Date.now(),
        };

        this.cache.push(entry);

        // Trim if too large
        if (this.cache.length > this.maxSize) {
            this.cache = this.cache.slice(-this.maxSize);
        }

        // Save immediately
        await this.persist();
    }

    /**
     * Get all dead letter entries
     */
    async getAll(): Promise<DeadLetterEntry[]> {
        await this.ensureLoaded();
        return [...this.cache];
    }

    /**
     * Get dead letter entries filtered by criteria
     */
    async getFiltered(filters: {
        topic?: string;
        errorCode?: string;
        since?: number;
        limit?: number;
    }): Promise<DeadLetterEntry[]> {
        await this.ensureLoaded();
        let filtered = [...this.cache];

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
        await this.ensureLoaded();
        
        const index = this.cache.findIndex(e => e.envelope.id === id);
        if (index === -1) return null;

        const entry = this.cache[index];
        this.cache.splice(index, 1);
        await this.persist();

        return entry.envelope;
    }

    /**
     * Remove dead letter entry
     */
    async remove(id: string): Promise<boolean> {
        await this.ensureLoaded();
        
        const index = this.cache.findIndex(e => e.envelope.id === id);
        if (index === -1) return false;

        this.cache.splice(index, 1);
        await this.persist();
        return true;
    }

    /**
     * Clear dead letter queue
     */
    async clear(): Promise<void> {
        this.cache = [];
        await this.persist();
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
        await this.ensureLoaded();
        
        const byTopic: Record<string, number> = {};
        const byErrorCode: Record<string, number> = {};
        let oldest: number | null = null;
        let newest: number | null = null;

        for (const entry of this.cache) {
            byTopic[entry.envelope.topic] = (byTopic[entry.envelope.topic] || 0) + 1;
            byErrorCode[entry.error.code] = (byErrorCode[entry.error.code] || 0) + 1;

            if (oldest === null || entry.timestamp < oldest) {
                oldest = entry.timestamp;
            }
            if (newest === null || entry.timestamp > newest) {
                newest = entry.timestamp;
            }
        }

        return {
            count: this.cache.length,
            byTopic,
            byErrorCode,
            oldest,
            newest,
        };
    }
}

