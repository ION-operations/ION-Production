import { promises as fs } from 'fs';
import { join } from 'path';
import { tmpdir } from 'os';
import {
  CredentialVaultService,
  VaultUsageLimitExceededError
} from '../src/services/credentialVaultService';

function createTempVaultPath(): string {
  return join(tmpdir(), `aimos-vault-test-${Date.now()}-${Math.random().toString(36).slice(2)}.json`);
}

describe('CredentialVaultService usage limiter', () => {
  let storagePath: string;
  let vaultService: CredentialVaultService;

  beforeEach(() => {
    storagePath = createTempVaultPath();
    vaultService = new CredentialVaultService(storagePath, 'unit-test-key-change-me-32chars!!');
  });

  afterEach(async () => {
    try {
      await fs.unlink(storagePath);
    } catch {
      // no-op
    }
  });

  it('enforces usage limits in recordUsage by default', async () => {
    const vaultCredentialId = await vaultService.createCredential({
      provider: 'chatgpt',
      label: 'limited-key',
      secret: { value: 'secret' },
      metadata: {
        usageLimits: {
          maxCallsPerDay: 1
        }
      }
    });

    await vaultService.recordUsage(vaultCredentialId, 0, 1);

    await expect(vaultService.recordUsage(vaultCredentialId, 0, 1))
      .rejects
      .toBeInstanceOf(VaultUsageLimitExceededError);
  });

  it('allows non-enforcing usage recording for post-call accounting', async () => {
    const vaultCredentialId = await vaultService.createCredential({
      provider: 'chatgpt',
      label: 'soft-accounting',
      secret: { value: 'secret' },
      metadata: {
        usageLimits: {
          maxCallsPerDay: 1
        }
      }
    });

    await vaultService.recordUsage(vaultCredentialId, 0, 1);
    const stats = await vaultService.recordUsage(vaultCredentialId, 0, 1, { enforceLimits: false });
    expect(stats.callsToday).toBe(2);
  });

  it('serializes concurrent usage writes without losing increments', async () => {
    const vaultCredentialId = await vaultService.createCredential({
      provider: 'custom',
      label: 'concurrent-usage',
      secret: { value: 'secret' }
    });

    const writes = Array.from({ length: 25 }, () =>
      vaultService.recordUsage(vaultCredentialId, 0.01, 1, { enforceLimits: false })
    );

    await Promise.all(writes);
    const usage = await vaultService.getUsageState(vaultCredentialId);

    expect(usage.stats.callsToday).toBe(25);
    expect(usage.stats.callsThisHour).toBe(25);
    expect(usage.stats.costToday).toBeCloseTo(0.25, 5);
  });
});
