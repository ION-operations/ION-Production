/**
 * Automation API Endpoint Tests
 * 
 * Tests for GET /metrics endpoint
 * Uses mocked ScriptEngine to control execution state
 */

import express from 'express';
import request from 'supertest';
import { createAutomationRouter } from '../src/api/automation';

// --- Mock ScriptEngine ---

class MockScriptEngine {
    private mockMetrics = {
        totalExecutions: 10,
        successRate: 0.8,
        averageDuration: 2.5,
        lastExecution: '2026-03-02T12:00:00.000Z',
        errorCount: 2
    };

    getMetrics() {
        return this.mockMetrics;
    }

    // Set custom metrics for specific test scenarios
    setMockMetrics(metrics: typeof this.mockMetrics) {
        this.mockMetrics = metrics;
    }

    // Other required methods (stubbed)
    async executeScript() {
        return {
            success: true,
            results: [],
            duration: 1000
        };
    }

    getExecutionStatus(executionId: string) {
        if (executionId === 'test-exec-1') {
            return {
                status: 'running' as const,
                currentStep: 2,
                totalSteps: 5,
                stepName: 'click: #submit',
                progress: 0.4,
                results: []
            };
        }
        return null;
    }

    pauseExecution() { }
    resumeExecution() { }
    stopExecution() { }
}

// --- Test Suite ---

describe('Automation API - Metrics Endpoint', () => {
    let app: express.Application;
    let scriptEngine: MockScriptEngine;

    beforeAll(() => {
        scriptEngine = new MockScriptEngine();
        app = express();
        app.use(express.json());
        app.use('/api/automation', createAutomationRouter(scriptEngine as any));
    });

    // =============================================
    // GET /api/automation/metrics
    // =============================================
    describe('GET /api/automation/metrics', () => {
        it('should return execution metrics', async () => {
            const res = await request(app)
                .get('/api/automation/metrics');

            expect(res.status).toBe(200);
            expect(res.body.success).toBe(true);
            expect(res.body.metrics).toBeDefined();

            const { metrics } = res.body;
            expect(metrics.totalExecutions).toBe(10);
            expect(metrics.successRate).toBe(0.8);
            expect(metrics.averageDuration).toBe(2.5);
            expect(metrics.errorCount).toBe(2);
            expect(metrics.lastExecution).toBe('2026-03-02T12:00:00.000Z');
        });

        it('should return zero metrics when no executions exist', async () => {
            scriptEngine.setMockMetrics({
                totalExecutions: 0,
                successRate: 0,
                averageDuration: 0,
                lastExecution: undefined as any,
                errorCount: 0
            });

            const res = await request(app)
                .get('/api/automation/metrics');

            expect(res.status).toBe(200);
            expect(res.body.success).toBe(true);
            expect(res.body.metrics.totalExecutions).toBe(0);
            expect(res.body.metrics.successRate).toBe(0);
            expect(res.body.metrics.errorCount).toBe(0);
        });

        it('should return correct structure for metrics response', async () => {
            scriptEngine.setMockMetrics({
                totalExecutions: 5,
                successRate: 1.0,
                averageDuration: 1.2,
                lastExecution: '2026-03-02T13:00:00.000Z',
                errorCount: 0
            });

            const res = await request(app)
                .get('/api/automation/metrics');

            expect(res.status).toBe(200);

            // Verify all expected keys are present
            const expectedKeys = ['totalExecutions', 'successRate', 'averageDuration', 'lastExecution', 'errorCount'];
            for (const key of expectedKeys) {
                expect(res.body.metrics).toHaveProperty(key);
            }
        });
    });
});
