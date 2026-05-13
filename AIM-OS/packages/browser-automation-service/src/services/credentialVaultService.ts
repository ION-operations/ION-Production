/**
 * Credential Vault Service
 *
 * Stores provider credentials encrypted at rest and returns references
 * that can be linked to chat accounts.
 */

import { promises as fs } from 'fs';
import { join } from 'path';
import * as crypto from 'crypto';
import { EncryptedCredentials } from '../types/automation';

type SupportedProvider = 'chatgpt' | 'claude' | 'gemini' | 'custom';

export interface VaultSecretPayload {
  username?: string;
  email?: string;
  password?: string;
  token?: string;
  apiKey?: string;
  [key: string]: string | undefined;
}

export interface VaultCredential {
  id: string;
  provider: SupportedProvider;
  label: string;
  usernameHint?: string;
  encryptedSecret: EncryptedCredentials;
  createdAt: Date;
  updatedAt: Date;
  metadata?: Record<string, any>;
}

export interface VaultCredentialSummary {
  id: string;
  provider: SupportedProvider;
  label: string;
  usernameHint?: string;
  createdAt: Date;
  updatedAt: Date;
  metadata?: Record<string, any>;
}

interface CreateVaultCredentialInput {
  provider: SupportedProvider;
  label: string;
  secret: VaultSecretPayload;
  metadata?: Record<string, any>;
}

interface UpdateVaultCredentialInput {
  label?: string;
  secret?: VaultSecretPayload;
  metadata?: Record<string, any>;
}

export interface VaultUsageLimits {
  maxCallsPerHour?: number;
  maxCallsPerDay?: number;
  maxCostPerDay?: number;
  maxCostPerMonth?: number;
  alertThreshold?: number;
}

export interface VaultUsageStats {
  callsToday: number;
  callsThisHour: number;
  costToday: number;
  costThisMonth: number;
  lastUsed?: string;
  callTimestamps: number[];
  dayKey?: string;
  monthKey?: string;
}

export interface VaultUsageCheckResult {
  allowed: boolean;
  reason?: string;
  remaining: {
    callsThisHour?: number;
    callsToday?: number;
    costToday?: number;
    costThisMonth?: number;
  };
  alerts: string[];
  limits: VaultUsageLimits;
  stats: VaultUsageStats;
  projected: {
    callsThisHour: number;
    callsToday: number;
    costToday: number;
    costThisMonth: number;
  };
}

export interface RecordVaultUsageOptions {
  enforceLimits?: boolean;
}

export class VaultCredentialNotFoundError extends Error {
  readonly code = 'VAULT_CREDENTIAL_NOT_FOUND';

  constructor(id: string) {
    super(`Vault credential not found: ${id}`);
    this.name = 'VaultCredentialNotFoundError';
  }
}

export class VaultUsageLimitExceededError extends Error {
  readonly code = 'VAULT_USAGE_LIMIT_EXCEEDED';
  readonly usage: VaultUsageCheckResult;

  constructor(usage: VaultUsageCheckResult) {
    super(usage.reason || 'Vault usage limit exceeded');
    this.name = 'VaultUsageLimitExceededError';
    this.usage = usage;
  }
}

export class CredentialVaultService {
  private static readonly ONE_HOUR_MS = 3_600_000;
  private static readonly ONE_DAY_MS = 86_400_000;
  private static readonly RETAIN_TIMESTAMP_MS = 35 * CredentialVaultService.ONE_DAY_MS;
  private credentials: Map<string, VaultCredential> = new Map();
  private usageLocks: Set<string> = new Set();
  private usageLockQueue: Map<string, Array<() => void>> = new Map();
  private ready: Promise<void>;
  private storagePath: string;
  private encryptionKey: Buffer;

  constructor(storagePath?: string, encryptionKey?: string) {
    this.storagePath = storagePath || join(process.cwd(), 'browser-automation-vault.json');
    const keyString = encryptionKey || process.env.BROWSER_AUTOMATION_ENCRYPTION_KEY || 'default-key-change-in-production-32-chars!!';
    this.encryptionKey = crypto.scryptSync(keyString, 'salt', 32);

    this.ready = this.loadCredentials();
    this.ready.catch(error => {
      console.error('Failed to load vault credentials:', error);
    });
  }

  async createCredential(input: CreateVaultCredentialInput): Promise<string> {
    await this.ensureReady();
    if (!input.label?.trim()) {
      throw new Error('label is required');
    }

    const nonEmptySecretValues = Object.values(input.secret || {}).filter(v => typeof v === 'string' && v.trim().length > 0);
    if (nonEmptySecretValues.length === 0) {
      throw new Error('secret must include at least one non-empty credential value');
    }

    const id = `vault-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
    const encryptedSecret = await this.encryptSecret(input.secret);
    const now = new Date();

    const usernameHintSource = input.secret.username || input.secret.email;
    const usernameHint = usernameHintSource ? this.maskUsername(usernameHintSource) : undefined;

    const credential: VaultCredential = {
      id,
      provider: input.provider,
      label: input.label.trim(),
      usernameHint,
      encryptedSecret,
      createdAt: now,
      updatedAt: now,
      metadata: input.metadata,
    };

    this.credentials.set(id, credential);
    await this.persistCredentials();

    this.log('SUCCESS', `Vault credential created: ${id}`, { id, provider: input.provider, label: input.label });
    return id;
  }

  async listCredentials(provider?: SupportedProvider): Promise<VaultCredentialSummary[]> {
    await this.ensureReady();
    const all = Array.from(this.credentials.values());
    const filtered = provider ? all.filter(item => item.provider === provider) : all;
    return filtered.map(item => this.toSummary(item));
  }

  async getCredential(id: string): Promise<VaultCredentialSummary | null> {
    await this.ensureReady();
    const item = this.credentials.get(id);
    return item ? this.toSummary(item) : null;
  }

  async getCredentialSecret(id: string): Promise<VaultSecretPayload | null> {
    await this.ensureReady();
    const item = this.credentials.get(id);
    if (!item) {
      return null;
    }
    return this.decryptSecret(item.encryptedSecret);
  }

  async updateCredentialSecret(id: string, secret: VaultSecretPayload): Promise<void> {
    await this.ensureReady();
    const item = this.getCredentialOrThrow(id);

    const encryptedSecret = await this.encryptSecret(secret);
    const usernameHintSource = secret.username || secret.email;

    const updated: VaultCredential = {
      ...item,
      usernameHint: usernameHintSource ? this.maskUsername(usernameHintSource) : item.usernameHint,
      encryptedSecret,
      updatedAt: new Date(),
    };

    this.credentials.set(id, updated);
    await this.persistCredentials();
    this.log('SUCCESS', `Vault credential updated: ${id}`, { id });
  }

  async updateCredential(id: string, updates: UpdateVaultCredentialInput): Promise<void> {
    await this.ensureReady();
    const item = this.getCredentialOrThrow(id);

    const mergedMetadata = updates.metadata !== undefined
      ? updates.metadata
      : item.metadata;

    let encryptedSecret = item.encryptedSecret;
    let usernameHint = item.usernameHint;
    if (updates.secret) {
      const nonEmptySecretValues = Object.values(updates.secret).filter(v => typeof v === 'string' && v.trim().length > 0);
      if (nonEmptySecretValues.length === 0) {
        throw new Error('secret must include at least one non-empty credential value');
      }
      encryptedSecret = await this.encryptSecret(updates.secret);
      const usernameHintSource = updates.secret.username || updates.secret.email;
      if (usernameHintSource) {
        usernameHint = this.maskUsername(usernameHintSource);
      }
    }

    const updated: VaultCredential = {
      ...item,
      label: updates.label?.trim() || item.label,
      metadata: mergedMetadata,
      encryptedSecret,
      usernameHint,
      updatedAt: new Date(),
    };

    this.credentials.set(id, updated);
    await this.persistCredentials();
    this.log('SUCCESS', `Vault credential metadata/label updated: ${id}`, { id });
  }

  async deleteCredential(id: string): Promise<void> {
    await this.ensureReady();
    this.getCredentialOrThrow(id);
    this.credentials.delete(id);
    await this.persistCredentials();
    this.log('SUCCESS', `Vault credential deleted: ${id}`, { id });
  }

  async exists(id: string): Promise<boolean> {
    await this.ensureReady();
    return this.credentials.has(id);
  }

  async getUsageState(id: string): Promise<VaultUsageCheckResult> {
    await this.ensureReady();
    return this.checkUsageLimit(id, 0, 0);
  }

  async checkUsageLimit(id: string, estimatedCost: number = 0, callIncrement: number = 1): Promise<VaultUsageCheckResult> {
    await this.ensureReady();
    const item = this.getCredentialOrThrow(id);

    const nowMs = Date.now();
    const limits = this.getUsageLimits(item);
    const stats = this.normalizeUsageStats(this.getUsageStats(item), nowMs);
    return this.evaluateUsageGate(limits, stats, estimatedCost, callIncrement);
  }

  async recordUsage(id: string, actualCost: number = 0, callIncrement: number = 1, options: RecordVaultUsageOptions = {}): Promise<VaultUsageStats> {
    await this.ensureReady();
    const enforceLimits = options.enforceLimits !== false;
    await this.acquireUsageLock(id);
    try {
      const item = this.getCredentialOrThrow(id);
      const nowMs = Date.now();
      const limits = this.getUsageLimits(item);
      const stats = this.normalizeUsageStats(this.getUsageStats(item), nowMs);
      const effectiveCallIncrement = this.asNonNegativeInt(callIncrement, 1);
      const effectiveCostIncrement = this.asNonNegativeNumber(actualCost, 0);

      if (enforceLimits) {
        const gate = this.evaluateUsageGate(limits, stats, effectiveCostIncrement, effectiveCallIncrement);
        if (!gate.allowed) {
          throw new VaultUsageLimitExceededError(gate);
        }
      }

      const nextCallTimestamps = [...stats.callTimestamps];
      for (let i = 0; i < effectiveCallIncrement; i += 1) {
        nextCallTimestamps.push(nowMs);
      }

      const nextStats = this.normalizeUsageStats({
        ...stats,
        callTimestamps: nextCallTimestamps,
        costToday: stats.costToday + effectiveCostIncrement,
        costThisMonth: stats.costThisMonth + effectiveCostIncrement,
        lastUsed: new Date(nowMs).toISOString(),
      }, nowMs);

      await this.persistUsage(item, limits, nextStats);
      this.log('SUCCESS', `Recorded vault usage`, {
        vaultCredentialId: id,
        callIncrement: effectiveCallIncrement,
        actualCost: effectiveCostIncrement,
        callsToday: nextStats.callsToday,
        callsThisHour: nextStats.callsThisHour,
        enforceLimits,
      });
      return nextStats;
    } finally {
      this.releaseUsageLock(id);
    }
  }

  private evaluateUsageGate(
    limits: VaultUsageLimits,
    stats: VaultUsageStats,
    estimatedCost: number = 0,
    callIncrement: number = 1
  ): VaultUsageCheckResult {
    const effectiveCallIncrement = this.asNonNegativeInt(callIncrement, 1);
    const effectiveCostIncrement = this.asNonNegativeNumber(estimatedCost, 0);
    const projected = {
      callsThisHour: stats.callsThisHour + effectiveCallIncrement,
      callsToday: stats.callsToday + effectiveCallIncrement,
      costToday: stats.costToday + effectiveCostIncrement,
      costThisMonth: stats.costThisMonth + effectiveCostIncrement,
    };

    const threshold = this.clampThreshold(limits.alertThreshold);
    const alerts: string[] = [];

    if (limits.maxCallsPerHour !== undefined && projected.callsThisHour > limits.maxCallsPerHour) {
      return {
        allowed: false,
        reason: `Hourly call limit exceeded (${projected.callsThisHour}/${limits.maxCallsPerHour})`,
        remaining: { callsThisHour: 0 },
        alerts,
        limits,
        stats,
        projected,
      };
    }

    if (limits.maxCallsPerDay !== undefined && projected.callsToday > limits.maxCallsPerDay) {
      return {
        allowed: false,
        reason: `Daily call limit exceeded (${projected.callsToday}/${limits.maxCallsPerDay})`,
        remaining: { callsToday: 0 },
        alerts,
        limits,
        stats,
        projected,
      };
    }

    if (limits.maxCostPerDay !== undefined && projected.costToday > limits.maxCostPerDay) {
      return {
        allowed: false,
        reason: `Daily cost limit exceeded ($${projected.costToday.toFixed(2)}/$${limits.maxCostPerDay.toFixed(2)})`,
        remaining: { costToday: 0 },
        alerts,
        limits,
        stats,
        projected,
      };
    }

    if (limits.maxCostPerMonth !== undefined && projected.costThisMonth > limits.maxCostPerMonth) {
      return {
        allowed: false,
        reason: `Monthly cost limit exceeded ($${projected.costThisMonth.toFixed(2)}/$${limits.maxCostPerMonth.toFixed(2)})`,
        remaining: { costThisMonth: 0 },
        alerts,
        limits,
        stats,
        projected,
      };
    }

    if (limits.maxCallsPerHour !== undefined && limits.maxCallsPerHour > 0) {
      const ratio = projected.callsThisHour / limits.maxCallsPerHour;
      if (ratio >= threshold) {
        alerts.push(`Approaching hourly call limit (${Math.round(ratio * 100)}%)`);
      }
    }
    if (limits.maxCallsPerDay !== undefined && limits.maxCallsPerDay > 0) {
      const ratio = projected.callsToday / limits.maxCallsPerDay;
      if (ratio >= threshold) {
        alerts.push(`Approaching daily call limit (${Math.round(ratio * 100)}%)`);
      }
    }
    if (limits.maxCostPerDay !== undefined && limits.maxCostPerDay > 0) {
      const ratio = projected.costToday / limits.maxCostPerDay;
      if (ratio >= threshold) {
        alerts.push(`Approaching daily cost limit (${Math.round(ratio * 100)}%)`);
      }
    }
    if (limits.maxCostPerMonth !== undefined && limits.maxCostPerMonth > 0) {
      const ratio = projected.costThisMonth / limits.maxCostPerMonth;
      if (ratio >= threshold) {
        alerts.push(`Approaching monthly cost limit (${Math.round(ratio * 100)}%)`);
      }
    }

    return {
      allowed: true,
      remaining: {
        callsThisHour: limits.maxCallsPerHour !== undefined ? Math.max(0, limits.maxCallsPerHour - projected.callsThisHour) : undefined,
        callsToday: limits.maxCallsPerDay !== undefined ? Math.max(0, limits.maxCallsPerDay - projected.callsToday) : undefined,
        costToday: limits.maxCostPerDay !== undefined ? Math.max(0, limits.maxCostPerDay - projected.costToday) : undefined,
        costThisMonth: limits.maxCostPerMonth !== undefined ? Math.max(0, limits.maxCostPerMonth - projected.costThisMonth) : undefined,
      },
      alerts,
      limits,
      stats,
      projected,
    };
  }

  private toSummary(item: VaultCredential): VaultCredentialSummary {
    return {
      id: item.id,
      provider: item.provider,
      label: item.label,
      usernameHint: item.usernameHint,
      createdAt: item.createdAt,
      updatedAt: item.updatedAt,
      metadata: item.metadata,
    };
  }

  private maskUsername(value: string): string {
    const trimmed = value.trim();
    if (trimmed.length <= 2) return '***';
    const first = trimmed.substring(0, 2);
    return `${first}***`;
  }

  private getUsageLimits(item: VaultCredential): VaultUsageLimits {
    const raw = item.metadata?.usageLimits;
    if (!raw || typeof raw !== 'object') {
      return { alertThreshold: 0.8 };
    }
    const source = raw as Record<string, unknown>;
    return {
      maxCallsPerHour: this.asOptionalPositiveNumber(source.maxCallsPerHour),
      maxCallsPerDay: this.asOptionalPositiveNumber(source.maxCallsPerDay),
      maxCostPerDay: this.asOptionalPositiveNumber(source.maxCostPerDay),
      maxCostPerMonth: this.asOptionalPositiveNumber(source.maxCostPerMonth),
      alertThreshold: this.clampThreshold(source.alertThreshold),
    };
  }

  private getUsageStats(item: VaultCredential): VaultUsageStats {
    const raw = item.metadata?.usageStats;
    if (!raw || typeof raw !== 'object') {
      return {
        callsToday: 0,
        callsThisHour: 0,
        costToday: 0,
        costThisMonth: 0,
        callTimestamps: [],
      };
    }

    const source = raw as Record<string, unknown>;
    return {
      callsToday: this.asNonNegativeInt(source.callsToday, 0),
      callsThisHour: this.asNonNegativeInt(source.callsThisHour, 0),
      costToday: this.asNonNegativeNumber(source.costToday, 0),
      costThisMonth: this.asNonNegativeNumber(source.costThisMonth, 0),
      lastUsed: typeof source.lastUsed === 'string' ? source.lastUsed : undefined,
      callTimestamps: Array.isArray(source.callTimestamps)
        ? source.callTimestamps.filter(v => typeof v === 'number' && Number.isFinite(v)) as number[]
        : [],
      dayKey: typeof source.dayKey === 'string' ? source.dayKey : undefined,
      monthKey: typeof source.monthKey === 'string' ? source.monthKey : undefined,
    };
  }

  private normalizeUsageStats(stats: VaultUsageStats, nowMs: number): VaultUsageStats {
    const now = new Date(nowMs);
    const currentDayKey = now.toISOString().slice(0, 10);
    const currentMonthKey = now.toISOString().slice(0, 7);
    const dayStartMs = new Date(`${currentDayKey}T00:00:00.000Z`).getTime();
    const hourAgoMs = nowMs - CredentialVaultService.ONE_HOUR_MS;
    const retainAfter = nowMs - CredentialVaultService.RETAIN_TIMESTAMP_MS;

    const retainedTimestamps = stats.callTimestamps
      .filter(ts => ts >= retainAfter)
      .sort((a, b) => a - b);

    const callsThisHour = retainedTimestamps.filter(ts => ts >= hourAgoMs).length;
    const callsToday = retainedTimestamps.filter(ts => ts >= dayStartMs).length;

    const dayChanged = stats.dayKey !== undefined && stats.dayKey !== currentDayKey;
    const monthChanged = stats.monthKey !== undefined && stats.monthKey !== currentMonthKey;

    return {
      callsToday,
      callsThisHour,
      costToday: dayChanged ? 0 : this.asNonNegativeNumber(stats.costToday, 0),
      costThisMonth: monthChanged ? 0 : this.asNonNegativeNumber(stats.costThisMonth, 0),
      lastUsed: stats.lastUsed,
      callTimestamps: retainedTimestamps,
      dayKey: currentDayKey,
      monthKey: currentMonthKey,
    };
  }

  private async persistUsage(item: VaultCredential, limits: VaultUsageLimits, stats: VaultUsageStats): Promise<void> {
    const updated: VaultCredential = {
      ...item,
      metadata: {
        ...(item.metadata || {}),
        usageLimits: limits,
        usageStats: stats,
      },
      updatedAt: new Date(),
    };
    this.credentials.set(item.id, updated);
    await this.persistCredentials();
  }

  private getCredentialOrThrow(id: string): VaultCredential {
    const item = this.credentials.get(id);
    if (!item) {
      throw new VaultCredentialNotFoundError(id);
    }
    return item;
  }

  private async acquireUsageLock(id: string): Promise<void> {
    if (!this.usageLocks.has(id)) {
      this.usageLocks.add(id);
      return;
    }

    await new Promise<void>((resolve) => {
      const queue = this.usageLockQueue.get(id) || [];
      queue.push(resolve);
      this.usageLockQueue.set(id, queue);
    });
  }

  private releaseUsageLock(id: string): void {
    const queue = this.usageLockQueue.get(id);
    if (queue && queue.length > 0) {
      const next = queue.shift();
      if (queue.length === 0) {
        this.usageLockQueue.delete(id);
      }
      next?.();
      return;
    }
    this.usageLocks.delete(id);
  }

  private asOptionalPositiveNumber(value: unknown): number | undefined {
    if (typeof value !== 'number' || !Number.isFinite(value) || value < 0) {
      return undefined;
    }
    return value;
  }

  private asNonNegativeNumber(value: unknown, fallback: number): number {
    if (typeof value !== 'number' || !Number.isFinite(value) || value < 0) {
      return fallback;
    }
    return value;
  }

  private asNonNegativeInt(value: unknown, fallback: number): number {
    if (typeof value !== 'number' || !Number.isFinite(value) || value < 0) {
      return fallback;
    }
    return Math.floor(value);
  }

  private clampThreshold(value: unknown): number {
    if (typeof value !== 'number' || !Number.isFinite(value)) {
      return 0.8;
    }
    return Math.min(0.99, Math.max(0.01, value));
  }

  private async encryptSecret(secret: VaultSecretPayload): Promise<EncryptedCredentials> {
    const algorithm = 'aes-256-gcm';
    const iv = crypto.randomBytes(16);

    const cipher = crypto.createCipheriv(algorithm, this.encryptionKey, iv) as crypto.CipherGCM;
    const encrypted = Buffer.concat([
      cipher.update(JSON.stringify(secret), 'utf8'),
      cipher.final()
    ]);

    const authTag = cipher.getAuthTag();
    return {
      encrypted: encrypted.toString('base64'),
      algorithm,
      iv: iv.toString('base64'),
      authTag: authTag.toString('base64'),
    };
  }

  private async decryptSecret(encrypted: EncryptedCredentials): Promise<VaultSecretPayload> {
    const iv = Buffer.from(encrypted.iv, 'base64');
    const authTag = Buffer.from(encrypted.authTag || '', 'base64');
    const encryptedData = Buffer.from(encrypted.encrypted, 'base64');

    const decipher = crypto.createDecipheriv(encrypted.algorithm, this.encryptionKey, iv) as crypto.DecipherGCM;
    decipher.setAuthTag(authTag);

    const decrypted = Buffer.concat([
      decipher.update(encryptedData),
      decipher.final()
    ]);

    return JSON.parse(decrypted.toString('utf8')) as VaultSecretPayload;
  }

  private async persistCredentials(): Promise<void> {
    const serialized = JSON.stringify(Array.from(this.credentials.values()), null, 2);
    await fs.writeFile(this.storagePath, serialized, 'utf8');
  }

  private async loadCredentials(): Promise<void> {
    try {
      const raw = await fs.readFile(this.storagePath, 'utf8');
      const parsed = JSON.parse(raw) as VaultCredential[];
      parsed.forEach(item => {
        item.createdAt = new Date(item.createdAt as any);
        item.updatedAt = new Date(item.updatedAt as any);
        this.credentials.set(item.id, item);
      });
      this.log('SUCCESS', `Loaded ${parsed.length} vault credentials`, { count: parsed.length });
    } catch (error: any) {
      if (error.code === 'ENOENT') {
        this.credentials = new Map();
        this.log('LOG', 'No vault file found, starting empty vault', {});
        return;
      }
      this.log('ERROR', `Failed to load vault credentials: ${error}`, { error });
      throw error;
    }
  }

  private async ensureReady(): Promise<void> {
    await this.ready;
  }

  private log(level: 'LOG' | 'SUCCESS' | 'WARN' | 'ERROR' | 'DEBUG', message: string, data?: any): void {
    const logMethod = level === 'ERROR' ? console.error :
      level === 'WARN' ? console.warn :
        level === 'DEBUG' ? console.debug :
          console.log;

    logMethod(`[${level}] ${message}`, data || '');
  }
}
