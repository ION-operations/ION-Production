/**
 * Resequencer - Deterministic Message Resequencing
 * 
 * Handles out-of-order messages with TTL-based buffering
 * Ensures messages are processed in order, even if they arrive out of sequence
 */

import { Envelope } from './envelope';

type Sender = string;

export class Resequencer {
    private expected = new Map<Sender, number>();           // next expected seq
    private buf = new Map<Sender, Map<number, Envelope>>();  // future msgs
    private deadline = new Map<string, number>();            // env.id -> ts
    private ttlMs: number;
    private startAt: number;

    constructor(ttlMs: number = 5000, startAt: number = 1) {
        this.ttlMs = ttlMs;
        this.startAt = startAt;
    }

    /**
     * Enqueue message - returns array of ready-to-process messages
     */
    enqueue(env: Envelope): Envelope[] {
        const sender = this.getSenderId(env);
        const seq = Number(env.seq ?? this.startAt);
        
        if (!this.expected.has(sender)) {
            this.expected.set(sender, this.startAt);
        }

        const exp = this.expected.get(sender)!;

        // Duplicate or stale
        if (seq < exp) {
            return [];
        }

        // Exact hit: advance and flush contiguous window
        if (seq === exp) {
            const out: Envelope[] = [env];
            this.expected.set(sender, exp + 1);
            
            // Flush contiguous from buffer
            const m = this.buf.get(sender);
            while (m?.has(this.expected.get(sender)!)) {
                const s = this.expected.get(sender)!;
                const nextEnv = m.get(s)!;
                out.push(nextEnv);
                m.delete(s);
                this.deadline.delete(nextEnv.id);
                this.expected.set(sender, s + 1);
            }
            
            return out;
        }

        // Future (gap): buffer and set deadline
        if (!this.buf.has(sender)) {
            this.buf.set(sender, new Map());
        }
        this.buf.get(sender)!.set(seq, env);
        this.deadline.set(env.id, Date.now() + this.ttlMs);
        
        return [];
    }

    /**
     * Expire any buffered gaps; returns envelopes to DLQ
     */
    expire(): Envelope[] {
        const now = Date.now();
        const doomed: Envelope[] = [];
        
        for (const [id, ts] of this.deadline.entries()) {
            if (ts <= now) {
                // Find and remove from whichever sender map contains it
                for (const [sender, m] of this.buf.entries()) {
                    for (const [seq, env] of m.entries()) {
                        if (env.id === id) {
                            doomed.push(env);
                            m.delete(seq);
                            this.deadline.delete(id);
                            break;
                        }
                    }
                }
            }
        }
        
        return doomed;
    }

    /**
     * Get sender ID from envelope
     */
    private getSenderId(env: Envelope): Sender {
        // Try payload.senderId first, fallback to direction
        const payload = env.payload as any;
        if (payload?.senderId) {
            return payload.senderId as string;
        }
        
        // Extract sender from direction
        return env.dir.split('->')[0];
    }

    /**
     * Get statistics
     */
    getStats(): {
        expectedSeqs: Record<string, number>;
        bufferSizes: Record<string, number>;
        totalBuffered: number;
        expiredCount: number;
    } {
        const expectedSeqs: Record<string, number> = {};
        const bufferSizes: Record<string, number> = {};
        let totalBuffered = 0;
        
        for (const [sender, seq] of this.expected.entries()) {
            expectedSeqs[sender] = seq;
        }
        
        for (const [sender, m] of this.buf.entries()) {
            bufferSizes[sender] = m.size;
            totalBuffered += m.size;
        }
        
        return {
            expectedSeqs,
            bufferSizes,
            totalBuffered,
            expiredCount: this.deadline.size,
        };
    }

    /**
     * Clear all state (for testing)
     */
    clear(): void {
        this.expected.clear();
        this.buf.clear();
        this.deadline.clear();
    }
}

