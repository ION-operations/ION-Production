/**
 * Persistent Outbox Manager
 * 
 * Manages outbox queue that survives reloads and crashes
 * Uses VS Code Memento API for persistence
 */

import * as vscode from 'vscode';
import { Envelope } from './envelope';

interface OutboxEntry {
    id: string;
    timestamp: number;
    envelope: Envelope;
    delivered: boolean;
    attempts: number;
    lastAttempt?: number;
}

export class PersistentOutbox {
    private store: vscode.Memento;
    private key: string;
    private maxSize: number = 2000;

    constructor(context: vscode.ExtensionContext, key: string = 'aimos.outbox') {
        this.store = context.globalState;
        this.key = key;
    }

    /**
     * Get all outbox entries
     */
    getAll(): OutboxEntry[] {
        return this.store.get<OutboxEntry[]>(this.key, []);
    }

    /**
     * Get undelivered entries
     */
    getUndelivered(): OutboxEntry[] {
        return this.getAll().filter(entry => !entry.delivered);
    }

    /**
     * Add envelope to outbox
     */
    push(envelope: Envelope): void {
        const entries = this.getAll();
        
        const entry: OutboxEntry = {
            id: envelope.id,
            timestamp: Date.now(),
            envelope,
            delivered: false,
            attempts: 0,
        };
        
        entries.push(entry);
        
        // Trim if too large (keep most recent)
        if (entries.length > this.maxSize) {
            entries.splice(0, entries.length - this.maxSize);
        }
        
        this.store.update(this.key, entries);
    }

    /**
     * Mark envelope as delivered
     */
    markDelivered(id: string): void {
        const entries = this.getAll();
        const index = entries.findIndex(e => e.id === id);
        
        if (index !== -1) {
            entries[index].delivered = true;
            this.store.update(this.key, entries);
        }
    }

    /**
     * Mark envelope as attempted (increment retry count)
     */
    markAttempted(id: string): void {
        const entries = this.getAll();
        const index = entries.findIndex(e => e.id === id);
        
        if (index !== -1) {
            entries[index].attempts++;
            entries[index].lastAttempt = Date.now();
            this.store.update(this.key, entries);
        }
    }

    /**
     * Remove delivered entries (cleanup)
     */
    cleanup(maxAge: number = 24 * 60 * 60 * 1000): void {
        const entries = this.getAll();
        const now = Date.now();
        
        // Remove delivered entries older than maxAge
        const filtered = entries.filter(entry => {
            if (!entry.delivered) return true; // Keep undelivered
            if (now - entry.timestamp < maxAge) return true; // Keep recent delivered
            return false; // Remove old delivered
        });
        
        if (filtered.length !== entries.length) {
            this.store.update(this.key, filtered);
        }
    }

    /**
     * Clear all entries
     */
    clear(): void {
        this.store.update(this.key, []);
    }

    /**
     * Get statistics
     */
    getStats(): {
        total: number;
        undelivered: number;
        delivered: number;
        oldestUndelivered: number | null;
    } {
        const entries = this.getAll();
        const undelivered = entries.filter(e => !e.delivered);
        const oldestUndelivered = undelivered.length > 0
            ? Math.min(...undelivered.map(e => e.timestamp))
            : null;
        
        return {
            total: entries.length,
            undelivered: undelivered.length,
            delivered: entries.length - undelivered.length,
            oldestUndelivered,
        };
    }
}

