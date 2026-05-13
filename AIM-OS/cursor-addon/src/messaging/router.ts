/**
 * Message Router
 * 
 * Routes messages with ordering, deduplication, retry logic, and dead letter queue
 * Integrates all reliability features into a single router
 */

import * as vscode from 'vscode';
import { Envelope, MessageKind, createAckEnvelope, createNackEnvelope } from './envelope';
import { IdempotencyKeyManager } from './idempotencyManager';
import { MessageOrderingManager } from './orderingManager';
import { DeadLetterQueueManager } from './deadLetterQueue';
import { Resequencer } from './resequencer';

export interface RoutingOptions {
    maxRetries?: number;
    retryDelay?: number;
    ackTimeout?: number;
}

export class MessageRouter {
    private idempotencyManager: IdempotencyKeyManager;
    private orderingManager: MessageOrderingManager;
    private deadLetterQueue: DeadLetterQueueManager;
    private resequencer: Resequencer;
    private pendingAcks: Map<string, NodeJS.Timeout> = new Map();
    private handlers: Map<string, (env: Envelope) => Promise<Envelope | null>> = new Map();
    private options: Required<RoutingOptions>;
    private webview: vscode.Webview | null = null;
    private inflight: number = 0;
    private drainScheduled: boolean = false;

    constructor(context: vscode.ExtensionContext, options: RoutingOptions = {}) {
        this.idempotencyManager = new IdempotencyKeyManager(context);
        this.orderingManager = new MessageOrderingManager();
        this.deadLetterQueue = new DeadLetterQueueManager(context);
        this.resequencer = new Resequencer(2000, 1); // TTL 2s, start at seq 1
        
        this.options = {
            maxRetries: options.maxRetries || 3,
            retryDelay: options.retryDelay || 500,
            ackTimeout: options.ackTimeout || 500,
        };

        // Save processed IDs on shutdown
        context.subscriptions.push({
            dispose: () => {
                this.idempotencyManager.checkpoint();
            }
        });

        // Process ordered queue periodically
        setInterval(() => this.processOrderedQueue(), 50);
        
        // Expire resequencer gaps periodically
        setInterval(() => {
            const expired = this.resequencer.expire();
            for (const env of expired) {
                this.deadLetterQueue.add(env, 'RESEQ_TTL', {
                    code: 'RESEQ_TTL',
                    message: 'Message expired waiting for gap fill',
                }).catch(console.error);
            }
        }, 1000);
    }

    /**
     * Tests can await this to avoid arbitrary timeouts
     */
    async idle(pollMs: number = 5): Promise<void> {
        while (this.drainScheduled || this.inflight > 0) {
            await new Promise(resolve => setTimeout(resolve, pollMs));
        }
    }

    /**
     * Set webview for sending messages
     */
    setWebview(webview: vscode.Webview): void {
        this.webview = webview;
    }

    /**
     * Register handler for topic
     */
    registerHandler(topic: string, handler: (env: Envelope) => Promise<Envelope | null>): void {
        this.handlers.set(topic, handler);
    }

    /**
     * Route incoming message
     */
    async route(envelope: Envelope): Promise<void> {
        // Validate envelope
        if (!this.validateEnvelope(envelope)) {
            console.error('Invalid envelope:', envelope);
            return;
        }

        // Check idempotency (has this been processed before?)
        if (this.idempotencyManager.hasBeenProcessed(envelope.id)) {
            console.warn(`Duplicate message detected: ${envelope.id}`);
            // Send ACK anyway (already processed)
            await this.sendAck(envelope, true);
            return;
        }

        // Handle requests (need ACK)
        if (envelope.kind === 'request') {
            // Send immediate ACK
            await this.sendAck(envelope, true);

            // Schedule drain (handles resequencing)
            this.scheduleDrain(envelope);
        } else {
            // Handle other message types directly
            await this.processMessage(envelope);
        }
    }

    /**
     * Schedule drain (handles resequencing)
     * Adds immediate microtask drain for deterministic test behavior
     */
    private scheduleDrain(latest?: Envelope): void {
        if (latest) {
            // Enqueue into resequencer
            const ready = this.resequencer.enqueue(latest);
            for (const env of ready) {
                this.dispatch(env);
            }
        }

        // Handle expirations (gaps -> DLQ)
        const expired = this.resequencer.expire();
        for (const e of expired) {
            this.deadLetterQueue.add(e, 'RESEQ_TTL', {
                code: 'RESEQ_TTL',
                message: 'Message expired waiting for gap fill',
            }).catch(console.error);
        }

        // Immediate drain via microtask (for deterministic tests)
        if (!this.drainScheduled) {
            this.drainScheduled = true;
            queueMicrotask(async () => {
                try {
                    // Process any ready messages immediately
                    await this.processOrderedQueue();
                } finally {
                    this.drainScheduled = false;
                }
            });
        }
    }

    /**
     * Drain all pending messages (for tests)
     * Returns Promise that resolves when drain completes
     */
    async drain(): Promise<void> {
        while (this.drainScheduled || this.inflight > 0) {
            await this.processOrderedQueue();
            await new Promise(resolve => setTimeout(resolve, 5)); // Small delay
        }
    }

    /**
     * Dispatch message to handler
     */
    private dispatch(envelope: Envelope): void {
        const handler = this.handlers.get(envelope.topic);
        
        if (!handler) {
            this.deadLetterQueue.add(envelope, 'NO_HANDLER', {
                code: 'NO_HANDLER',
                message: `No handler registered for topic: ${envelope.topic}`,
            }).catch(console.error);
            return;
        }

        if (this.idempotencyManager.hasBeenProcessed(envelope.id)) {
            return; // Already processed
        }

        this.idempotencyManager.markAsProcessed(envelope.id);
        this.inflight++;

        handler(envelope)
            .then(result => {
                if (result && this.webview) {
                    this.webview.postMessage(result);
                }
            })
            .catch(err => {
                this.deadLetterQueue.add(envelope, 'HANDLER_ERROR', {
                    code: 'HANDLER_ERROR',
                    message: err.message || String(err),
                    data: { error: String(err) },
                }).catch(console.error);
            })
            .finally(() => {
                this.inflight--;
            });
    }

    /**
     * Process message from ordered queue (legacy - kept for compatibility)
     */
    private async processOrderedQueue(): Promise<void> {
        const envelope = this.orderingManager.dequeue();
        if (!envelope) return;

        try {
            await this.processMessage(envelope);
            this.orderingManager.markProcessed(envelope);
            this.idempotencyManager.markAsProcessed(envelope.id);
        } catch (error: any) {
            const attempts = ((envelope as any).attempts || 0) + 1;
            (envelope as any).attempts = attempts;
            
            if (attempts >= this.options.maxRetries) {
                // Max retries exceeded - move to dead letter queue
                this.deadLetterQueue.add(
                    envelope,
                    'Max retries exceeded',
                    {
                        code: 'MAX_RETRIES_EXCEEDED',
                        message: error.message || String(error),
                        data: { attempts, error: String(error) },
                    },
                    attempts
                ).catch(console.error);
                this.orderingManager.markFailed(envelope, false); // Don't retry
            } else {
                // Retry after delay
                setTimeout(() => {
                    this.orderingManager.markFailed(envelope, true); // Retry
                }, this.options.retryDelay);
            }
        }
    }

    /**
     * Process message (legacy - kept for compatibility)
     */
    private async processMessage(envelope: Envelope): Promise<void> {
        const handler = this.handlers.get(envelope.topic);
        
        if (!handler) {
            // No handler - send NACK
            await this.sendNack(envelope, {
                code: 'NO_HANDLER',
                message: `No handler registered for topic: ${envelope.topic}`,
            });
            return;
        }

        try {
            const response = await handler(envelope);
            
            if (response && envelope.kind === 'request') {
                // Send response
                await this.sendMessage(response);
            }
        } catch (error: any) {
            // Send NACK with error
            await this.sendNack(envelope, {
                code: 'HANDLER_ERROR',
                message: error.message || String(error),
                data: { error: String(error) },
            });
            throw error; // Re-throw for retry logic
        }
    }

    /**
     * Send ACK
     */
    private async sendAck(envelope: Envelope, ok: boolean): Promise<void> {
        const ack = createAckEnvelope(envelope.id, this.reverseDirection(envelope.dir), envelope.topic, ok);
        await this.sendMessage(ack);
    }

    /**
     * Send NACK
     */
    private async sendNack(envelope: Envelope, error: { code: string; message: string; data?: any }): Promise<void> {
        const nack = createNackEnvelope(envelope.id, this.reverseDirection(envelope.dir), envelope.topic, error);
        await this.sendMessage(nack);
    }

    /**
     * Send message to webview
     */
    private async sendMessage(envelope: Envelope): Promise<void> {
        if (!this.webview) {
            console.warn('No webview set, cannot send message');
            return;
        }

        this.webview.postMessage(envelope);
    }

    /**
     * Reverse direction
     */
    private reverseDirection(dir: string): 'ui->ext' | 'ext->ui' | 'ext->agent' | 'agent->ext' {
        if (dir === 'ui->ext') return 'ext->ui';
        if (dir === 'ext->ui') return 'ui->ext';
        if (dir === 'ext->agent') return 'agent->ext';
        if (dir === 'agent->ext') return 'ext->agent';
        return 'ext->ui'; // Default
    }

    /**
     * Validate envelope
     */
    private validateEnvelope(env: any): env is Envelope {
        if (!env || typeof env !== 'object') return false;
        if (env.v !== 1) return false;
        if (typeof env.id !== 'string') return false;
        if (typeof env.seq !== 'number') return false;
        if (typeof env.ts !== 'number') return false;
        if (!['ui->ext', 'ext->ui', 'ext->agent', 'agent->ext'].includes(env.dir)) return false;
        if (!['request', 'response', 'event', 'ack', 'nack', 'heartbeat'].includes(env.kind)) return false;
        if (typeof env.topic !== 'string') return false;
        return true;
    }

    /**
     * Get statistics
     */
    async getStats(): Promise<{
        idempotency: { count: number; storagePath: string };
        ordering: { totalQueues: number; totalMessages: number; queues: Array<{ sender: string; count: number; nextSeq: number }> };
        resequencer: { expectedSeqs: Record<string, number>; bufferSizes: Record<string, number>; totalBuffered: number; expiredCount: number };
        deadLetterQueue: { count: number; byTopic: Record<string, number>; byErrorCode: Record<string, number>; oldest: number | null; newest: number | null };
    }> {
        return {
            idempotency: this.idempotencyManager.getStats(),
            ordering: this.orderingManager.getStats(),
            resequencer: this.resequencer.getStats(),
            deadLetterQueue: await this.deadLetterQueue.getStats(),
        };
    }

    /**
     * Get dead letter queue entries
     */
    async getDeadLetterQueue(): Promise<ReturnType<DeadLetterQueueManager['getAll']>> {
        return await this.deadLetterQueue.getAll();
    }

    /**
     * Retry dead letter entry
     */
    async retryDeadLetter(id: string): Promise<Envelope | null> {
        const envelope = await this.deadLetterQueue.retry(id);
        if (envelope) {
            // Re-queue for processing via resequencer
            this.scheduleDrain(envelope);
        }
        return envelope;
    }
}

