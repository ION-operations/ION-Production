/**
 * Bulletproof Messaging Protocol - Test Suite
 * 
 * Comprehensive tests for all messaging components
 * Tests can be run manually or with a test framework
 */

import './test-setup'; // Mock vscode before any other imports
import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';
import { createEnvelope, createAckEnvelope, createNackEnvelope, createHeartbeatEnvelope, validateEnvelope } from './envelope';
import { IdempotencyKeyManager } from './idempotencyManager';
import { MessageOrderingManager } from './orderingManager';
import { DeadLetterQueueManager } from './deadLetterQueue';
import { MessageRouter } from './router';
import { HeartbeatMonitor } from './heartbeatMonitor';
import { PersistentOutbox } from './persistentOutbox';
import { Resequencer } from './resequencer';
import { MemoryKV, FileKV } from './kv';
import { flushMicrotasks, tick, tmpFile } from './testHelpers';
import { Envelope } from './envelope';

// Simple test framework
interface TestResult {
    name: string;
    passed: boolean;
    error?: string;
    duration: number;
}

class TestRunner {
    private tests: Array<{ name: string; fn: () => Promise<void> | void }> = [];
    private results: TestResult[] = [];

    test(name: string, fn: () => Promise<void> | void) {
        this.tests.push({ name, fn });
    }

    async run(): Promise<TestResult[]> {
        console.log(`\n🧪 Running ${this.tests.length} tests...\n`);
        
        for (const test of this.tests) {
            const start = Date.now();
            try {
                await test.fn();
                const duration = Date.now() - start;
                this.results.push({ name: test.name, passed: true, duration });
                console.log(`✅ ${test.name} (${duration}ms)`);
            } catch (error: any) {
                const duration = Date.now() - start;
                this.results.push({ name: test.name, passed: false, error: error.message, duration });
                console.log(`❌ ${test.name} (${duration}ms)`);
                console.log(`   Error: ${error.message}`);
            }
        }

        return this.results;
    }

    getSummary(): { total: number; passed: number; failed: number } {
        const total = this.results.length;
        const passed = this.results.filter(r => r.passed).length;
        const failed = total - passed;
        return { total, passed, failed };
    }
}

// Mock VS Code ExtensionContext for testing
function createMockContext(): any {
    const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'aimos-test-'));
    
    // Create a simple in-memory storage
        const storage: Map<string, any> = new Map();
        
        return {
            subscriptions: [],
            workspaceState: {
                get: (key: string, defaultValue?: any) => {
                    const value = storage.get(`workspace:${key}`);
                    return value !== undefined ? value : defaultValue;
                },
                update: (key: string, value: any) => {
                    storage.set(`workspace:${key}`, value);
                    return Promise.resolve();
                },
            },
            globalState: {
                get: (key: string, defaultValue?: any) => {
                    const value = storage.get(`global:${key}`);
                    return value !== undefined ? value : defaultValue;
                },
                update: (key: string, value: any) => {
                    storage.set(`global:${key}`, value);
                    return Promise.resolve();
                },
            },
        extensionPath: tempDir,
        globalStorageUri: vscode.Uri.file(tempDir),
        extensionUri: vscode.Uri.file(tempDir),
    };
}

// Helper to clean up temp files
function cleanup(context: vscode.ExtensionContext) {
    try {
        const tempDir = context.extensionPath;
        if (fs.existsSync(tempDir)) {
            fs.rmSync(tempDir, { recursive: true, force: true });
        }
    } catch (error) {
        // Ignore cleanup errors
    }
}

// ============================================================================
// TEST SUITE 1: ENVELOPE PROTOCOL
// ============================================================================

export function testEnvelopeProtocol(): TestRunner {
    const runner = new TestRunner();

    runner.test('createEnvelope creates valid envelope', () => {
        const env = createEnvelope('request', 'test.topic', 'ui->ext', { data: 'test' });
        
        if (env.v !== 1) throw new Error('Version must be 1');
        if (!env.id) throw new Error('ID must be set');
        if (env.seq !== 0) throw new Error('Seq should default to 0');
        if (env.kind !== 'request') throw new Error('Kind must be request');
        if (env.topic !== 'test.topic') throw new Error('Topic must match');
        if (env.dir !== 'ui->ext') throw new Error('Direction must match');
    });

    runner.test('createAckEnvelope creates valid ACK', () => {
        const originalId = 'test-id-123';
        const ack = createAckEnvelope(originalId, 'ext->ui', 'test.topic', true);
        
        if (ack.kind !== 'ack') throw new Error('Kind must be ack');
        if (ack.replyTo !== originalId) throw new Error('replyTo must match original ID');
        if (ack.ok !== true) throw new Error('ok must be true');
    });

    runner.test('createNackEnvelope creates valid NACK', () => {
        const originalId = 'test-id-123';
        const nack = createNackEnvelope(originalId, 'ext->ui', 'test.topic', {
            code: 'TEST_ERROR',
            message: 'Test error',
        });
        
        if (nack.kind !== 'nack') throw new Error('Kind must be nack');
        if (nack.replyTo !== originalId) throw new Error('replyTo must match original ID');
        if (nack.ok !== false) throw new Error('ok must be false');
        if (!nack.err) throw new Error('err must be set');
        if (nack.err.code !== 'TEST_ERROR') throw new Error('Error code must match');
    });

    runner.test('createHeartbeatEnvelope creates valid heartbeat', () => {
        const heartbeat = createHeartbeatEnvelope('ext->ui');
        
        if (heartbeat.kind !== 'heartbeat') throw new Error('Kind must be heartbeat');
        if (heartbeat.topic !== 'link') throw new Error('Topic must be link');
        if (heartbeat.priority !== 'critical') throw new Error('Priority must be critical');
    });

    runner.test('validateEnvelope validates correct envelope', () => {
        const env = createEnvelope('request', 'test.topic', 'ui->ext');
        if (!validateEnvelope(env)) throw new Error('Valid envelope should pass validation');
    });

    runner.test('validateEnvelope rejects invalid envelope', () => {
        const invalid = { v: 1, id: 'test' }; // Missing required fields
        if (validateEnvelope(invalid)) throw new Error('Invalid envelope should fail validation');
    });

    return runner;
}

// ============================================================================
// TEST SUITE 2: IDEMPOTENCY MANAGER
// ============================================================================

export function testIdempotencyManager(): TestRunner {
    const runner = new TestRunner();
    let context: vscode.ExtensionContext;

    runner.test('hasBeenProcessed returns false for new ID', () => {
        context = createMockContext();
        const manager = new IdempotencyKeyManager(context);
        
        if (manager.hasBeenProcessed('new-id-123')) {
            throw new Error('New ID should not be processed');
        }
    });

    runner.test('markAsProcessed marks ID as processed', () => {
        context = createMockContext();
        const manager = new IdempotencyKeyManager(context);
        
        manager.markAsProcessed('test-id-123');
        
        if (!manager.hasBeenProcessed('test-id-123')) {
            throw new Error('Marked ID should be processed');
        }
    });

    runner.test('processed IDs persist across instances', () => {
        context = createMockContext();
        const manager1 = new IdempotencyKeyManager(context);
        manager1.markAsProcessed('persistent-id-123');
        manager1.checkpoint(); // Force save
        
        const manager2 = new IdempotencyKeyManager(context);
        if (!manager2.hasBeenProcessed('persistent-id-123')) {
            throw new Error('ID should persist across instances');
        }
        
        cleanup(context);
    });

    runner.test('manager trims oversized cache', () => {
        context = createMockContext();
        const manager = new IdempotencyKeyManager(context);
        
        // Add more than maxSize IDs
        for (let i = 0; i < 6000; i++) {
            manager.markAsProcessed(`id-${i}`);
        }
        
        const stats = manager.getStats();
        if (stats.count > 5000) {
            throw new Error('Cache should be trimmed to maxSize');
        }
        
        cleanup(context);
    });

    return runner;
}

// ============================================================================
// TEST SUITE 3: ORDERING MANAGER
// ============================================================================

export function testOrderingManager(): TestRunner {
    const runner = new TestRunner();

    runner.test('messages processed in order', () => {
        const manager = new MessageOrderingManager();
        
        // Enqueue messages in order
        const env1 = createEnvelope('request', 'test', 'ui->ext');
        env1.seq = 1;
        manager.enqueue(env1);
        
        const env2 = createEnvelope('request', 'test', 'ui->ext');
        env2.seq = 2;
        manager.enqueue(env2);
        
        const env3 = createEnvelope('request', 'test', 'ui->ext');
        env3.seq = 3;
        manager.enqueue(env3);
        
        // Dequeue should return in order
        let msg = manager.dequeue();
        if (!msg || msg.seq !== 1) {
            const stats = manager.getStats();
            throw new Error(`Should return seq 1 first, got ${msg?.seq || 'null'}. Stats: ${JSON.stringify(stats)}`);
        }
        manager.markProcessed(msg);
        
        msg = manager.dequeue();
        if (!msg || msg.seq !== 2) throw new Error(`Should return seq 2 second, got ${msg?.seq || 'null'}`);
        manager.markProcessed(msg);
        
        msg = manager.dequeue();
        if (!msg || msg.seq !== 3) throw new Error(`Should return seq 3 third, got ${msg?.seq || 'null'}`);
        manager.markProcessed(msg);
    });

    runner.test('out-of-order messages rejected', () => {
        const manager = new MessageOrderingManager();
        
        const env1 = createEnvelope('request', 'test', 'ui->ext');
        env1.seq = 1;
        manager.enqueue(env1);
        manager.dequeue(); // Process seq 1
        
        const env2 = createEnvelope('request', 'test', 'ui->ext');
        env2.seq = 1; // Duplicate seq
        manager.enqueue(env2);
        
        const msg = manager.dequeue();
        if (msg) throw new Error('Should not return duplicate seq');
    });

    runner.test('one sender processed at a time', () => {
        const manager = new MessageOrderingManager();
        
        const env1 = createEnvelope('request', 'test', 'ui->ext');
        env1.seq = 1;
        manager.enqueue(env1);
        
        const msg = manager.dequeue();
        if (!msg || msg.seq !== 1) throw new Error('Should return message with seq 1');
        
        // Try to dequeue again (should be null - sender is processing)
        const msg2 = manager.dequeue();
        if (msg2) throw new Error('Should not return another message while processing');
        
        // Mark as processed
        manager.markProcessed(msg);
        
        // Now should be able to dequeue again
        const env2 = createEnvelope('request', 'test', 'ui->ext');
        env2.seq = 2;
        manager.enqueue(env2);
        const msg3 = manager.dequeue();
        if (!msg3 || msg3.seq !== 2) throw new Error('Should return message with seq 2 after processing');
        manager.markProcessed(msg3);
    });

    return runner;
}

// ============================================================================
// TEST SUITE 4: DEAD LETTER QUEUE
// ============================================================================

export function testDeadLetterQueue(): TestRunner {
    const runner = new TestRunner();
    let context: vscode.ExtensionContext;

    runner.test('add message to DLQ', async () => {
        context = createMockContext();
        // Use MemoryKV for testing (test-safe)
        const dlq = new DeadLetterQueueManager(context, new MemoryKV());
        
        const env = createEnvelope('request', 'test.topic', 'ui->ext');
        await dlq.add(env, 'Test reason', {
            code: 'TEST_ERROR',
            message: 'Test error message',
        }, 3);
        
        const entries = await dlq.getAll();
        if (entries.length !== 1) throw new Error('Should have 1 entry');
        if (entries[0].envelope.id !== env.id) throw new Error('Entry ID should match');
        
        cleanup(context);
    });

    runner.test('DLQ persists across instances', async () => {
        context = createMockContext();
        const file = tmpFile('dlq.json');
        
        // Ensure directory exists
        const dir = path.dirname(file);
        await fs.promises.mkdir(dir, { recursive: true });
        
        const dlq1 = new DeadLetterQueueManager(context, new FileKV(file));
        
        const env = createEnvelope('request', 'test.topic', 'ui->ext');
        await dlq1.add(env, 'Test reason', {
            code: 'TEST_ERROR',
            message: 'Test error',
        });
        
        // Ensure write completes
        await new Promise(resolve => setTimeout(resolve, 100));
        
        // Force save by creating new instance (which loads from disk)
        const dlq2 = new DeadLetterQueueManager(context, new FileKV(file));
        const entries = await dlq2.getAll();
        if (entries.length !== 1) {
            throw new Error(`Should have 1 entry in DLQ, got ${entries.length}`);
        }
        
        cleanup(context);
    });

    runner.test('retry removes from DLQ', async () => {
        context = createMockContext();
        const dlq = new DeadLetterQueueManager(context, new MemoryKV());
        
        const env = createEnvelope('request', 'test.topic', 'ui->ext');
        await dlq.add(env, 'Test reason', {
            code: 'TEST_ERROR',
            message: 'Test error',
        });
        
        const entriesBefore = await dlq.getAll();
        if (entriesBefore.length !== 1) throw new Error('Should have 1 entry before retry');
        
        const retried = await dlq.retry(env.id);
        if (!retried) throw new Error('Should return envelope');
        
        const entriesAfter = await dlq.getAll();
        if (entriesAfter.length !== 0) throw new Error('Should remove from DLQ after retry');
        
        cleanup(context);
    });

    runner.test('filter by topic', async () => {
        context = createMockContext();
        const dlq = new DeadLetterQueueManager(context, new MemoryKV());
        
        const env1 = createEnvelope('request', 'topic1', 'ui->ext');
        const env2 = createEnvelope('request', 'topic2', 'ui->ext');
        
        await dlq.add(env1, 'Reason 1', { code: 'ERR1', message: 'Error 1' });
        await dlq.add(env2, 'Reason 2', { code: 'ERR2', message: 'Error 2' });
        
        const filtered = await dlq.getFiltered({ topic: 'topic1' });
        if (filtered.length !== 1) throw new Error('Should filter by topic');
        if (filtered[0].envelope.topic !== 'topic1') throw new Error('Should return correct topic');
        
        cleanup(context);
    });

    return runner;
}

// ============================================================================
// TEST SUITE 5: MESSAGE ROUTER
// ============================================================================

export function testMessageRouter(): TestRunner {
    const runner = new TestRunner();
    let context: vscode.ExtensionContext;

    runner.test('router routes messages to handlers', async () => {
        context = createMockContext();
        const router = new MessageRouter(context);
        
        let handled = false;
        router.registerHandler('test.topic', async (env) => {
            handled = true;
            return createEnvelope('response', env.topic, 'ext->ui', { success: true }, { replyTo: env.id });
        });
        
        const env = createEnvelope('request', 'test.topic', 'ui->ext', { senderId: 'test-sender' });
        env.seq = 1;
        await router.route(env);
        
        // Wait for router to finish processing using drain() helper
        await router.drain();
        
        if (!handled) throw new Error('Handler should be called');
        
        cleanup(context);
    });

    runner.test('router checks idempotency', async () => {
        context = createMockContext();
        const router = new MessageRouter(context);
        
        let callCount = 0;
        router.registerHandler('test.topic', async (env) => {
            callCount++;
            return createEnvelope('response', env.topic, 'ext->ui', { success: true }, { replyTo: env.id });
        });
        
        const env = createEnvelope('request', 'test.topic', 'ui->ext', { senderId: 'test-sender' });
        env.seq = 1;
        
        // Send same message twice
        await router.route(env);
        await router.drain();
        
        await router.route(env); // Duplicate
        await router.drain();
        
        if (callCount !== 1) throw new Error(`Handler should be called only once, got ${callCount}`);
        
        cleanup(context);
    });

    runner.test('router sends ACK for requests', async () => {
        context = createMockContext();
        const router = new MessageRouter(context);
        
        const receivedAcks: Envelope[] = [];
        const mockWebview = {
            postMessage: (msg: any) => {
                if (msg.kind === 'ack') {
                    receivedAcks.push(msg);
                }
            }
        } as any;
        
        router.setWebview(mockWebview);
        
        router.registerHandler('test.topic', async (env) => {
            return createEnvelope('response', env.topic, 'ext->ui', {}, { replyTo: env.id });
        });
        
        const env = createEnvelope('request', 'test.topic', 'ui->ext');
        env.seq = 1;
        await router.route(env);
        
        await new Promise(resolve => setTimeout(resolve, 100));
        
        if (receivedAcks.length === 0) throw new Error('Should send ACK');
        
        cleanup(context);
    });

    runner.test('router moves to DLQ after max retries', async () => {
        context = createMockContext();
        const router = new MessageRouter(context, { maxRetries: 2 });
        
        let attemptCount = 0;
        router.registerHandler('test.topic', async (env) => {
            attemptCount++;
            throw new Error('Always fails');
        });
        
        const env = createEnvelope('request', 'test.topic', 'ui->ext');
        env.seq = 1;
        await router.route(env);
        
        // Wait for retries
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        const dlq = await router.getDeadLetterQueue();
        if (dlq.length === 0) throw new Error('Should move to DLQ after max retries');
        
        cleanup(context);
    });

    return runner;
}

// ============================================================================
// TEST SUITE 6: PERSISTENT OUTBOX
// ============================================================================

export function testPersistentOutbox(): TestRunner {
    const runner = new TestRunner();
    let context: vscode.ExtensionContext;

    runner.test('outbox stores undelivered messages', () => {
        context = createMockContext();
        const outbox = new PersistentOutbox(context);
        
        const env = createEnvelope('request', 'test.topic', 'ui->ext');
        outbox.push(env);
        
        const undelivered = outbox.getUndelivered();
        if (undelivered.length !== 1) throw new Error('Should have 1 undelivered');
        if (undelivered[0].id !== env.id) throw new Error('Should match envelope ID');
        
        cleanup(context);
    });

    runner.test('markDelivered removes from undelivered', () => {
        context = createMockContext();
        const outbox = new PersistentOutbox(context);
        
        const env = createEnvelope('request', 'test.topic', 'ui->ext');
        outbox.push(env);
        outbox.markDelivered(env.id);
        
        const undelivered = outbox.getUndelivered();
        if (undelivered.length !== 0) throw new Error('Should have 0 undelivered');
        
        cleanup(context);
    });

    runner.test('outbox persists across instances', () => {
        context = createMockContext();
        const outbox1 = new PersistentOutbox(context);
        
        const env = createEnvelope('request', 'test.topic', 'ui->ext');
        outbox1.push(env);
        
        const outbox2 = new PersistentOutbox(context);
        const undelivered = outbox2.getUndelivered();
        if (undelivered.length !== 1) throw new Error('Should persist across instances');
        
        cleanup(context);
    });

    return runner;
}

// ============================================================================
// TEST SUITE 7: INTEGRATION TESTS
// ============================================================================

export function testIntegration(): TestRunner {
    const runner = new TestRunner();
    let context: vscode.ExtensionContext;

    runner.test('full flow: send -> ACK -> process -> response', async () => {
        context = createMockContext();
        const router = new MessageRouter(context);
        
        const receivedMessages: Envelope[] = [];
        const mockWebview = {
            postMessage: (msg: any) => {
                receivedMessages.push(msg);
            }
        } as any;
        
        router.setWebview(mockWebview);
        
        router.registerHandler('test.topic', async (env) => {
            return createEnvelope('response', env.topic, 'ext->ui', {
                result: 'success'
            }, { replyTo: env.id });
        });
        
        const request = createEnvelope('request', 'test.topic', 'ui->ext', { senderId: 'test-sender' });
        request.seq = 1;
        
        await router.route(request);
        await router.drain(); // Wait for all processing
        
        // Should receive: ACK + Response
        const acks = receivedMessages.filter(m => m.kind === 'ack');
        const responses = receivedMessages.filter(m => m.kind === 'response');
        
        if (acks.length === 0) throw new Error('Should receive ACK');
        if (responses.length === 0) throw new Error(`Should receive response, got ${receivedMessages.length} messages: ${receivedMessages.map(m => m.kind).join(', ')}`);
        if (responses[0].replyTo !== request.id) throw new Error('Response should reference request');
        
        cleanup(context);
    });

    runner.test('ordering + idempotency work together', async () => {
        context = createMockContext();
        const router = new MessageRouter(context);
        
        const processed: string[] = [];
        router.registerHandler('test.topic', async (env) => {
            processed.push(env.id);
            return createEnvelope('response', env.topic, 'ext->ui', { success: true }, { replyTo: env.id });
        });
        
        const mockWebview = {
            postMessage: () => {}
        } as any;
        router.setWebview(mockWebview);
        
        // Send 3 messages in order
        const env1 = createEnvelope('request', 'test.topic', 'ui->ext', { senderId: 'test-sender' });
        env1.seq = 1;
        const env2 = createEnvelope('request', 'test.topic', 'ui->ext', { senderId: 'test-sender' });
        env2.seq = 2;
        const env3 = createEnvelope('request', 'test.topic', 'ui->ext', { senderId: 'test-sender' });
        env3.seq = 3;
        
        await router.route(env1);
        await router.route(env2);
        await router.route(env3);
        
        await router.drain(); // Wait for all processing
        
        if (processed.length !== 3) throw new Error(`Should process 3 messages, got ${processed.length}. Processed: ${processed.join(', ')}`);
        
        // Try to send duplicate
        await router.route(env2); // Duplicate
        await router.drain();
        
        if (processed.length !== 3) throw new Error(`Should still process only 3 messages after duplicate, got ${processed.length}`);
        
        cleanup(context);
    });

    return runner;
}

// ============================================================================
// RUN ALL TESTS
// ============================================================================

export async function runAllTests(): Promise<void> {
    console.log('🚀 Starting Bulletproof Messaging Protocol Test Suite\n');
    console.log('='.repeat(60));
    
    const suites = [
        { name: 'Envelope Protocol', fn: testEnvelopeProtocol },
        { name: 'Idempotency Manager', fn: testIdempotencyManager },
        { name: 'Ordering Manager', fn: testOrderingManager },
        { name: 'Dead Letter Queue', fn: testDeadLetterQueue },
        { name: 'Message Router', fn: testMessageRouter },
        { name: 'Persistent Outbox', fn: testPersistentOutbox },
        { name: 'Integration Tests', fn: testIntegration },
    ];
    
    let totalPassed = 0;
    let totalFailed = 0;
    let totalTests = 0;
    
    for (const suite of suites) {
        console.log(`\n📦 ${suite.name}`);
        console.log('-'.repeat(60));
        
        const runner = suite.fn();
        const results = await runner.run();
        const summary = runner.getSummary();
        
        totalPassed += summary.passed;
        totalFailed += summary.failed;
        totalTests += summary.total;
    }
    
    console.log('\n' + '='.repeat(60));
    console.log('\n📊 TEST SUMMARY');
    console.log('-'.repeat(60));
    console.log(`Total Tests: ${totalTests}`);
    console.log(`✅ Passed: ${totalPassed}`);
    console.log(`❌ Failed: ${totalFailed}`);
    console.log(`Success Rate: ${((totalPassed / totalTests) * 100).toFixed(1)}%`);
    
    if (totalFailed === 0) {
        console.log('\n🎉 All tests passed! Bulletproof messaging protocol is working correctly.');
    } else {
        console.log(`\n⚠️  ${totalFailed} test(s) failed. Please review the errors above.`);
    }
    
    console.log('\n' + '='.repeat(60));
}

// Export for manual execution
if (require.main === module) {
    runAllTests().catch(console.error);
}

