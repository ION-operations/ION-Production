import express from 'express';
import request from 'supertest';
import { createMcpBridgeRouter } from '../src/api/mcpBridge';

class MockBrowserService {
  getInstance(_browserId: string): never {
    throw new Error('Browser instance not found');
  }

  async launchBrowser(): Promise<string> {
    return 'mock-browser-id';
  }
}

class MockConnectionManager {
  async getAccount(accountId: string): Promise<any> {
    if (accountId === 'chatgpt-account') {
      return {
        id: accountId,
        provider: 'chatgpt',
        vaultCredentialId: null,
      };
    }
    return null;
  }

  async loadSession(): Promise<void> {
    return;
  }

  async verifySession(): Promise<boolean> {
    return false;
  }

  async saveSession(): Promise<void> {
    return;
  }
}

class MockCredentialVaultService {
  async checkUsageLimit(): Promise<any> {
    return { allowed: true };
  }

  async recordUsage(): Promise<void> {
    return;
  }
}

describe('MCP Bridge AUTH_READY gate', () => {
  let app: express.Application;

  beforeAll(() => {
    app = express();
    app.use(express.json());
    app.use(
      '/api/bridge',
      createMcpBridgeRouter(
        new MockBrowserService() as any,
        new MockConnectionManager() as any,
        new MockCredentialVaultService() as any
      )
    );
  });

  it('blocks chatgpt send-prompt waitForResponse=true without AUTH_READY token', async () => {
    const res = await request(app)
      .post('/api/bridge/send-prompt')
      .send({
        browserId: 'x',
        prompt: 'hello',
        provider: 'chatgpt',
        waitForResponse: true,
      });

    expect(res.status).toBe(428);
    expect(res.body.status).toBe('PENDING_AUTH');
  });

  it('blocks chatgpt extract-response without AUTH_READY token', async () => {
    const res = await request(app)
      .post('/api/bridge/extract-response')
      .send({
        browserId: 'x',
        provider: 'chatgpt',
      });

    expect(res.status).toBe(428);
    expect(res.body.status).toBe('PENDING_AUTH');
  });

  it('blocks chatgpt full-session without AUTH_READY token', async () => {
    const res = await request(app)
      .post('/api/bridge/full-session')
      .send({
        accountId: 'chatgpt-account',
        prompt: 'hello',
      });

    expect(res.status).toBe(428);
    expect(res.body.status).toBe('PENDING_AUTH');
  });

  it('allows request to proceed past gate when AUTH_READY token is present', async () => {
    const res = await request(app)
      .post('/api/bridge/send-prompt')
      .send({
        browserId: 'x',
        prompt: 'hello',
        provider: 'chatgpt',
        waitForResponse: true,
        authReadyToken: 'AUTH_READY',
      });

    // The mock browser is missing, so it should fail after the gate.
    expect(res.status).not.toBe(428);
  });
});
