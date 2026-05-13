/**
 * Browser API Endpoint Tests
 * 
 * Tests for GET /viewport and POST /detect-elements endpoints
 * Uses mocked BrowserService to avoid launching real browsers
 */

import express from 'express';
import request from 'supertest';
import { createBrowserRouter } from '../src/api/browser';

// --- Mock BrowserService ---

class MockBrowserService {
    private instances = new Map<string, any>();

    constructor() {
        // Pre-seed a test browser instance
        this.instances.set('test-browser-1', {
            browserId: 'test-browser-1',
            browser: {
                wsEndpoint: () => 'ws://127.0.0.1:9222/devtools/browser/abc123',
                close: async () => { }
            },
            page: {
                url: () => 'https://example.com',
                title: async () => 'Example',
                evaluate: async (fn: Function, ...args: any[]) => {
                    // Return mock detected elements for detect-elements tests
                    return [
                        {
                            selector: '#submit-btn',
                            xpath: '//*[@id="submit-btn"]',
                            text: 'Submit',
                            tag: 'button',
                            attributes: { id: 'submit-btn', type: 'submit' },
                            bounds: { x: 100, y: 200, width: 120, height: 40 },
                            confidence: 0.95
                        },
                        {
                            selector: 'input.email-field',
                            xpath: '//input[1]',
                            text: '',
                            tag: 'input',
                            attributes: { type: 'email', class: 'email-field', name: 'email' },
                            bounds: { x: 100, y: 150, width: 300, height: 32 },
                            confidence: 0.85
                        }
                    ];
                },
                screenshot: async () => Buffer.from('fake-png'),
                goto: async () => { },
                setUserAgent: async () => { },
                evaluateOnNewDocument: async () => { },
                $: async () => null,
                waitForSelector: async () => { },
                click: async () => { },
                type: async () => { },
                hover: async () => { }
            },
            status: 'idle',
            createdAt: new Date(),
            lastActivity: new Date()
        });
    }

    getInstance(browserId: string) {
        const instance = this.instances.get(browserId);
        if (!instance) throw new Error(`Browser instance not found: ${browserId}`);
        return instance;
    }

    async getViewportUrl(browserId: string): Promise<string | null> {
        const instance = this.getInstance(browserId);
        try {
            return instance.browser.wsEndpoint();
        } catch {
            return null;
        }
    }

    async detectElements(browserId: string, selector?: string) {
        const instance = this.getInstance(browserId);
        return instance.page.evaluate(() => { }, selector);
    }

    async getBrowserStatus(browserId: string) {
        const instance = this.getInstance(browserId);
        return {
            browserId,
            status: instance.status,
            url: instance.page.url(),
            title: await instance.page.title(),
            createdAt: instance.createdAt,
            lastActivity: instance.lastActivity
        };
    }

    async screenshot(browserId: string) {
        const instance = this.getInstance(browserId);
        return instance.page.screenshot();
    }

    async launchBrowser() { return 'test-browser-new'; }
    async navigateTo() { }
    async closeBrowser(browserId: string) { this.instances.delete(browserId); }
}

// --- Test Suite ---

describe('Browser API - New Endpoints', () => {
    let app: express.Application;
    let browserService: MockBrowserService;

    beforeAll(() => {
        browserService = new MockBrowserService();
        app = express();
        app.use(express.json());
        app.use('/api/browser', createBrowserRouter(browserService as any));
    });

    // =============================================
    // GET /api/browser/viewport
    // =============================================
    describe('GET /api/browser/viewport', () => {
        it('should return viewport URL for valid browserId', async () => {
            const res = await request(app)
                .get('/api/browser/viewport')
                .query({ browserId: 'test-browser-1' });

            expect(res.status).toBe(200);
            expect(res.body.success).toBe(true);
            expect(res.body.viewportUrl).toBe('ws://127.0.0.1:9222/devtools/browser/abc123');
        });

        it('should return 400 when browserId is missing', async () => {
            const res = await request(app)
                .get('/api/browser/viewport');

            expect(res.status).toBe(400);
            expect(res.body.success).toBe(false);
            expect(res.body.error).toContain('browserId');
        });

        it('should return 500 for invalid browserId', async () => {
            const res = await request(app)
                .get('/api/browser/viewport')
                .query({ browserId: 'nonexistent' });

            expect(res.status).toBe(500);
            expect(res.body.success).toBe(false);
            expect(res.body.error).toContain('not found');
        });
    });

    // =============================================
    // POST /api/browser/detect-elements
    // =============================================
    describe('POST /api/browser/detect-elements', () => {
        it('should return detected elements for valid browserId', async () => {
            const res = await request(app)
                .post('/api/browser/detect-elements')
                .send({ browserId: 'test-browser-1' });

            expect(res.status).toBe(200);
            expect(res.body.success).toBe(true);
            expect(Array.isArray(res.body.elements)).toBe(true);
            expect(res.body.elements.length).toBe(2);

            // Verify element structure
            const btn = res.body.elements[0];
            expect(btn).toHaveProperty('selector');
            expect(btn).toHaveProperty('xpath');
            expect(btn).toHaveProperty('tag');
            expect(btn).toHaveProperty('bounds');
            expect(btn).toHaveProperty('confidence');
            expect(btn.bounds).toHaveProperty('x');
            expect(btn.bounds).toHaveProperty('y');
            expect(btn.bounds).toHaveProperty('width');
            expect(btn.bounds).toHaveProperty('height');
        });

        it('should accept optional selector filter', async () => {
            const res = await request(app)
                .post('/api/browser/detect-elements')
                .send({ browserId: 'test-browser-1', selector: 'button' });

            expect(res.status).toBe(200);
            expect(res.body.success).toBe(true);
        });

        it('should return 400 when browserId is missing', async () => {
            const res = await request(app)
                .post('/api/browser/detect-elements')
                .send({});

            expect(res.status).toBe(400);
            expect(res.body.success).toBe(false);
            expect(res.body.error).toContain('browserId');
        });

        it('should return 500 for invalid browserId', async () => {
            const res = await request(app)
                .post('/api/browser/detect-elements')
                .send({ browserId: 'nonexistent' });

            expect(res.status).toBe(500);
            expect(res.body.success).toBe(false);
        });
    });
});
