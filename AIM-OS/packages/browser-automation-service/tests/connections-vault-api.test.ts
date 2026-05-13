import { promises as fs } from 'fs';
import { join } from 'path';
import { tmpdir } from 'os';
import express from 'express';
import request from 'supertest';
import { createConnectionsRouter } from '../src/api/connections';
import { CredentialVaultService } from '../src/services/credentialVaultService';

function createTempVaultPath(): string {
  return join(tmpdir(), `aimos-connections-vault-test-${Date.now()}-${Math.random().toString(36).slice(2)}.json`);
}

describe('Connections API - Vault limiter endpoints', () => {
  let app: express.Application;
  let vaultService: CredentialVaultService;
  let storagePath: string;

  beforeEach(() => {
    storagePath = createTempVaultPath();
    vaultService = new CredentialVaultService(storagePath, 'unit-test-key-change-me-32chars!!');

    app = express();
    app.use(express.json());
    app.use(
      '/api/connections',
      createConnectionsRouter(
        {} as any,
        {} as any,
        vaultService
      )
    );
  });

  afterEach(async () => {
    try {
      await fs.unlink(storagePath);
    } catch {
      // no-op
    }
  });

  it('returns 404 for usage lookup on missing vault credential', async () => {
    const res = await request(app).get('/api/connections/vault/missing-id/usage');

    expect(res.status).toBe(404);
    expect(res.body.success).toBe(false);
    expect(String(res.body.error || '')).toContain('not found');
  });

  it('returns 429 when record-usage exceeds configured limits', async () => {
    const vaultCredentialId = await vaultService.createCredential({
      provider: 'chatgpt',
      label: 'zero-calls',
      secret: { value: 'secret' },
      metadata: {
        usageLimits: {
          maxCallsPerDay: 0
        }
      }
    });

    const res = await request(app)
      .post(`/api/connections/vault/${vaultCredentialId}/record-usage`)
      .send({ actualCost: 0, callIncrement: 1 });

    expect(res.status).toBe(429);
    expect(res.body.success).toBe(false);
    expect(String(res.body.error || '')).toContain('limit');
  });
});
