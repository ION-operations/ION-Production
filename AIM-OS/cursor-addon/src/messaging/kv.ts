/**
 * KV Contract - Abstract key-value storage for Dead Letter Queue
 * 
 * Supports both file-based (production) and in-memory (testing) storage
 * with atomic writes for reliability
 */

import { promises as fs } from 'fs';
import * as path from 'path';

export interface KV {
    read(): Promise<any[]>;
    write(v: any[]): Promise<void>;
}

/**
 * File-based KV with atomic writes
 */
export class FileKV implements KV {
    constructor(private filename: string) {}

    async read(): Promise<any[]> {
        try {
            const s = await fs.readFile(this.filename, 'utf8');
            return s ? JSON.parse(s) : [];
        } catch {
            return [];
        }
    }

    async write(v: any[]): Promise<void> {
        // Ensure directory exists
        await fs.mkdir(path.dirname(this.filename), { recursive: true });
        
        // Write to temp file first
        const tmp = this.filename + '.tmp';
        const fd = await fs.open(tmp, 'w');
        
        try {
            await fd.writeFile(JSON.stringify(v, null, 2), 'utf8');
            // Ensure data is written to disk
            await fd.sync();
            await fd.close();
            
            // Atomic rename
            await fs.rename(tmp, this.filename);
        } catch (error) {
            await fd.close().catch(() => {});
            await fs.unlink(tmp).catch(() => {});
            throw error;
        }
    }
}

/**
 * In-memory KV for testing
 */
export class MemoryKV implements KV {
    private v: any[] = [];

    async read(): Promise<any[]> {
        return [...this.v];
    }

    async write(v: any[]): Promise<void> {
        this.v = [...v];
    }

    /**
     * Get current state (for testing)
     */
    getState(): any[] {
        return [...this.v];
    }

    /**
     * Clear state (for testing)
     */
    clear(): void {
        this.v = [];
    }
}

