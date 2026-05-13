/**
 * Message Ordering Manager
 * 
 * Ensures messages are processed in order by enforcing FIFO queue per sender
 * Uses sequence numbers to guarantee ordering even across retries
 */

import { Envelope, Direction } from './envelope';

interface QueuedMessage {
    envelope: Envelope;
    attempts: number;
    firstAttempt: number;
    lastAttempt: number;
}

export class MessageOrderingManager {
    private queues: Map<string, QueuedMessage[]> = new Map(); // sender -> queue
    private nextExpectedSeq: Map<string, number> = new Map(); // sender -> next expected seq
    private processing: Set<string> = new Set(); // Currently processing sender IDs
    private epoch: Map<string, number> = new Map(); // sender -> epoch (0 or 1)

    /**
     * Add message to ordered queue
     * Handles epoch detection (seq can start at 0 or 1)
     */
    enqueue(envelope: Envelope): void {
        const sender = this.getSenderId(envelope.dir);
        const seq = envelope.seq;

        // Initialize queue if needed
        if (!this.queues.has(sender)) {
            this.queues.set(sender, []);
            // Don't set epoch yet - will detect from first message
        }

        const queue = this.queues.get(sender)!;
        let nextSeq = this.nextExpectedSeq.get(sender);

        // Detect epoch from first message
        if (nextSeq === undefined) {
            // First message from this sender
            if (seq === 0 || seq === 1) {
                this.epoch.set(sender, seq);
                this.nextExpectedSeq.set(sender, seq);
                nextSeq = seq;
            } else {
                // Unexpected first seq - default to 1
                this.epoch.set(sender, 1);
                this.nextExpectedSeq.set(sender, 1);
                nextSeq = 1;
            }
        } else {
            const senderEpoch = this.epoch.get(sender) || 1;
            nextSeq = this.nextExpectedSeq.get(sender)!;
        }

        // Check if this is the next expected message
        if (seq === nextSeq) {
            // Can process immediately
            const queued: QueuedMessage = {
                envelope,
                attempts: 0,
                firstAttempt: Date.now(),
                lastAttempt: Date.now(),
            };
            queue.push(queued);
            this.nextExpectedSeq.set(sender, seq + 1);
        } else if (seq > nextSeq) {
            // Future message - add to queue (will wait for earlier messages)
            const queued: QueuedMessage = {
                envelope,
                attempts: 0,
                firstAttempt: Date.now(),
                lastAttempt: Date.now(),
            };
            queue.push(queued);
            
            // Sort queue by sequence number
            queue.sort((a, b) => a.envelope.seq - b.envelope.seq);
        } else {
            // Duplicate or out-of-order message (seq < nextSeq)
            // This is a duplicate - ignore it
            console.warn(`Ignoring out-of-order message: seq=${seq}, expected=${nextSeq}`);
        }
    }

    /**
     * Get next message ready to process (in order)
     */
    dequeue(): Envelope | null {
        // Find queue with next message ready
        for (const [sender, queue] of this.queues.entries()) {
            if (queue.length === 0) continue;
            if (this.processing.has(sender)) continue; // Already processing this sender

            const queued = queue[0];
            const expectedSeq = this.nextExpectedSeq.get(sender)!;

            // Check if this is the next expected message
            // If queue was sorted, first item should match expectedSeq
            if (queued.envelope.seq === expectedSeq) {
                queue.shift(); // Remove from queue
                this.processing.add(sender); // Mark as processing
                this.nextExpectedSeq.set(sender, expectedSeq + 1);
                return queued.envelope;
            }
        }

        return null;
    }

    /**
     * Mark message as processed (release sender lock)
     */
    markProcessed(envelope: Envelope): void {
        const sender = this.getSenderId(envelope.dir);
        this.processing.delete(sender);
    }

    /**
     * Mark message as failed (retry or move to DLQ)
     */
    markFailed(envelope: Envelope, retry: boolean = true): void {
        const sender = this.getSenderId(envelope.dir);
        this.processing.delete(sender);

        if (retry) {
            // Re-queue at front (will retry immediately)
            const queued: QueuedMessage = {
                envelope,
                attempts: (envelope as any).attempts || 0,
                firstAttempt: (envelope as any).firstAttempt || Date.now(),
                lastAttempt: Date.now(),
            };
            (queued.envelope as any).attempts = queued.attempts + 1;
            
            const queue = this.queues.get(sender)!;
            queue.unshift(queued); // Add to front
        }
    }

    /**
     * Get sender ID from direction
     */
    private getSenderId(dir: Direction): string {
        // Extract sender from direction
        // 'ui->ext' -> 'ui'
        // 'ext->ui' -> 'ext'
        // 'ext->agent' -> 'ext'
        // 'agent->ext' -> 'agent'
        return dir.split('->')[0];
    }

    /**
     * Get queue statistics
     */
    getStats(): {
        totalQueues: number;
        totalMessages: number;
        queues: Array<{ sender: string; count: number; nextSeq: number }>;
    } {
        const queues: Array<{ sender: string; count: number; nextSeq: number }> = [];
        let totalMessages = 0;

        for (const [sender, queue] of this.queues.entries()) {
            queues.push({
                sender,
                count: queue.length,
                nextSeq: this.nextExpectedSeq.get(sender) || 0,
            });
            totalMessages += queue.length;
        }

        return {
            totalQueues: this.queues.size,
            totalMessages,
            queues,
        };
    }

    /**
     * Clear queue (for testing/debugging)
     */
    clear(): void {
        this.queues.clear();
        this.nextExpectedSeq.clear();
        this.processing.clear();
    }
}

