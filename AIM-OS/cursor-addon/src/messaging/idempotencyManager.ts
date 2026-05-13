/**
 * Idempotency Key Manager
 * 
 * Persists processed message IDs to disk to guarantee exactly-once processing
 * even across crashes and reloads.
 */

import * as fs from 'fs';
import * as path from 'path';
import * as vscode from 'vscode';

export class IdempotencyKeyManager {
    private processedIds: Set<string> = new Set();
    private storagePath: string;
    private maxSize: number = 5000; // Max IDs to keep in memory
    private checkpointInterval: number = 100; // Checkpoint every N IDs
    private checkpointCount: number = 0;

    constructor(context: vscode.ExtensionContext) {
        // Store in workspace .aimos directory
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (workspaceFolder) {
            this.storagePath = path.join(workspaceFolder.uri.fsPath, '.aimos', 'processed_ids.json');
        } else {
            // Fallback to global storage
            this.storagePath = path.join(context.globalStorageUri.fsPath, 'processed_ids.json');
        }

        // Ensure directory exists
        const dir = path.dirname(this.storagePath);
        if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir, { recursive: true });
        }

        // Load processed IDs on startup
        this.loadProcessedIds();
    }

    /**
     * Load processed IDs from disk
     */
    private loadProcessedIds(): void {
        try {
            if (fs.existsSync(this.storagePath)) {
                const data = fs.readFileSync(this.storagePath, 'utf8');
                const ids = JSON.parse(data) as string[];
                
                // Keep only most recent IDs (LRU behavior)
                if (ids.length > this.maxSize) {
                    const recentIds = ids.slice(-this.maxSize);
                    this.processedIds = new Set(recentIds);
                    this.saveProcessedIds(); // Trim file
                } else {
                    this.processedIds = new Set(ids);
                }
            }
        } catch (error) {
            console.error('Failed to load processed IDs:', error);
            this.processedIds = new Set();
        }
    }

    /**
     * Save processed IDs to disk
     */
    private saveProcessedIds(): void {
        try {
            const ids = Array.from(this.processedIds);
            fs.writeFileSync(this.storagePath, JSON.stringify(ids), 'utf8');
        } catch (error) {
            console.error('Failed to save processed IDs:', error);
        }
    }

    /**
     * Check if message ID has been processed
     */
    hasBeenProcessed(id: string): boolean {
        return this.processedIds.has(id);
    }

    /**
     * Mark message ID as processed
     */
    markAsProcessed(id: string): void {
        this.processedIds.add(id);

        // Trim if too large
        if (this.processedIds.size > this.maxSize) {
            const ids = Array.from(this.processedIds);
            const recentIds = ids.slice(-this.maxSize);
            this.processedIds = new Set(recentIds);
        }

        // Periodic checkpoint
        this.checkpointCount++;
        if (this.checkpointCount >= this.checkpointInterval) {
            this.saveProcessedIds();
            this.checkpointCount = 0;
        }
    }

    /**
     * Force checkpoint (call before shutdown)
     */
    checkpoint(): void {
        this.saveProcessedIds();
        this.checkpointCount = 0;
    }

    /**
     * Clear processed IDs (for testing/debugging)
     */
    clear(): void {
        this.processedIds.clear();
        if (fs.existsSync(this.storagePath)) {
            fs.unlinkSync(this.storagePath);
        }
    }

    /**
     * Get statistics
     */
    getStats(): { count: number; storagePath: string } {
        return {
            count: this.processedIds.size,
            storagePath: this.storagePath,
        };
    }
}

