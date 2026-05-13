/**
 * Bulletproof Messaging Protocol - Envelope Specification v1
 * 
 * Reliable message protocol for Cursor Extension ↔ Agent ↔ Electron App communication
 * Features: Versioning, ACK/NACK, retries, deduplication, ordering
 */

export type Direction = 'ui->ext' | 'ext->ui' | 'ext->agent' | 'agent->ext';
export type MessageKind = 'request' | 'response' | 'event' | 'ack' | 'nack' | 'heartbeat';
export type Priority = 'critical' | 'high' | 'medium' | 'low';

export interface Envelope<T = unknown> {
    /** Protocol version */
    v: 1;
    
    /** Unique message ID (UUID) */
    id: string;
    
    /** Monotonic sequence number per sender (for ordering) */
    seq: number;
    
    /** Timestamp (Date.now()) */
    ts: number;
    
    /** Message direction */
    dir: Direction;
    
    /** Message kind */
    kind: MessageKind;
    
    /** Topic/channel identifier (e.g., 'mcp.callTool', 'chat.message') */
    topic: string;
    
    /** ID of message being replied to */
    replyTo?: string;
    
    /** Success status (for response/ack) */
    ok?: boolean;
    
    /** Error details (if ok=false) */
    err?: {
        code: string;
        message: string;
        data?: any;
    };
    
    /** Message payload (type-safe) */
    payload?: T;
    
    /** Message priority */
    priority?: Priority;
    
    /** Compression flag (if payload is compressed) */
    compressed?: boolean;
    
    /** Original size before compression */
    originalSize?: number;
}

/**
 * Create a new envelope
 */
export function createEnvelope<T>(
    kind: MessageKind,
    topic: string,
    dir: Direction,
    payload?: T,
    options?: {
        replyTo?: string;
        priority?: Priority;
        compressed?: boolean;
        originalSize?: number;
    }
): Envelope<T> {
    return {
        v: 1,
        id: crypto.randomUUID(),
        seq: 0, // Will be set by sender
        ts: Date.now(),
        dir,
        kind,
        topic,
        payload,
        replyTo: options?.replyTo,
        priority: options?.priority || 'medium',
        compressed: options?.compressed,
        originalSize: options?.originalSize,
    };
}

/**
 * Create ACK envelope
 */
export function createAckEnvelope(
    originalId: string,
    dir: Direction,
    topic: string,
    ok: boolean = true
): Envelope {
    return {
        v: 1,
        id: crypto.randomUUID(),
        replyTo: originalId,
        seq: 0,
        ts: Date.now(),
        dir,
        kind: 'ack',
        topic,
        ok,
    };
}

/**
 * Create NACK envelope
 */
export function createNackEnvelope(
    originalId: string,
    dir: Direction,
    topic: string,
    error: { code: string; message: string; data?: any }
): Envelope {
    return {
        v: 1,
        id: crypto.randomUUID(),
        replyTo: originalId,
        seq: 0,
        ts: Date.now(),
        dir,
        kind: 'nack',
        topic,
        ok: false,
        err: error,
    };
}

/**
 * Create heartbeat envelope
 */
export function createHeartbeatEnvelope(dir: Direction): Envelope {
    return {
        v: 1,
        id: crypto.randomUUID(),
        seq: 0,
        ts: Date.now(),
        dir,
        kind: 'heartbeat',
        topic: 'link',
        priority: 'critical',
    };
}

/**
 * Validate envelope structure
 */
export function validateEnvelope(env: any): env is Envelope {
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

