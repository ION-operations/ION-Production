/**
 * Test Helpers - Utilities for deterministic testing
 */

/**
 * Flush microtasks (promise resolution)
 */
export const flushMicrotasks = (): Promise<void> => {
    return new Promise<void>((resolve) => {
        queueMicrotask(() => resolve());
    });
};

/**
 * Wait for specified milliseconds
 */
export const tick = (ms: number = 0): Promise<void> => {
    return new Promise<void>((resolve) => {
        setTimeout(() => resolve(), ms);
    });
};

/**
 * Get temporary file path for testing
 */
import { tmpdir } from 'os';
import * as path from 'path';
import { randomUUID } from 'crypto';

export const tmpFile = (name: string = 'dlq.json'): string => {
    return path.join(tmpdir(), `aimos-${randomUUID()}-${name}`);
};

