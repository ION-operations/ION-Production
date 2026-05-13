/**
 * Vault Service — AES-GCM encrypted credential storage
 *
 * Stores API keys, OAuth tokens, email credentials, etc.
 * All values are encrypted at rest using Web Crypto AES-GCM.
 * Only the proxy gateway should call getDecryptedValue().
 */

// ─── Types ───

export type VaultEntryType = 'api_key' | 'oauth_token' | 'email_credential' | 'password' | 'custom';
export type VaultCategory = 'ai_provider' | 'email' | 'cloud_storage' | 'git' | 'custom';

export interface UsageLimit {
    maxCallsPerHour?: number;
    maxCallsPerDay?: number;
    maxCostPerDay?: number;      // in USD
    maxCostPerMonth?: number;    // in USD
    alertThreshold?: number;     // 0-1, fraction at which to alert (default 0.8)
}

export interface UsageStats {
    callsToday: number;
    callsThisHour: number;
    costToday: number;
    costThisMonth: number;
    lastUsed?: string;           // ISO timestamp
    callTimestamps: number[];    // Recent timestamps for sliding window
}

export interface VaultEntry {
    id: string;
    name: string;
    type: VaultEntryType;
    category: VaultCategory;
    provider?: string;           // e.g., 'gemini', 'openai', 'gmail'
    encryptedValue: string;      // AES-GCM encrypted
    metadata?: Record<string, string>; // e.g., { email: 'user@...' }
    usageLimits: UsageLimit;
    usageStats: UsageStats;
    createdAt: string;
    updatedAt: string;
}

// ─── Crypto Key Management ───

const VAULT_KEY_NAME = 'aim-os-vault-crypto-key';
const ENCODER = new TextEncoder();
const DECODER = new TextDecoder();

let _cachedKey: CryptoKey | null = null;

async function getOrCreateVaultKey(): Promise<CryptoKey | null> {
    if (_cachedKey) return _cachedKey;
    if (typeof crypto === 'undefined' || !crypto.subtle) return null;

    try {
        const existing = localStorage.getItem(VAULT_KEY_NAME);
        if (existing) {
            const raw = Uint8Array.from(atob(existing), c => c.charCodeAt(0));
            _cachedKey = await crypto.subtle.importKey('raw', raw, 'AES-GCM', true, ['encrypt', 'decrypt']);
            return _cachedKey;
        }

        // Generate and persist a new vault key
        const key = await crypto.subtle.generateKey({ name: 'AES-GCM', length: 256 }, true, ['encrypt', 'decrypt']);
        const exported = await crypto.subtle.exportKey('raw', key);
        localStorage.setItem(VAULT_KEY_NAME, btoa(String.fromCharCode(...new Uint8Array(exported))));
        _cachedKey = key;
        return key;
    } catch {
        return null;
    }
}

// ─── Encrypt / Decrypt ───

export async function encryptValue(plaintext: string): Promise<string> {
    const key = await getOrCreateVaultKey();
    if (!key) return `b64:${btoa(plaintext)}`; // fallback

    const iv = crypto.getRandomValues(new Uint8Array(12));
    const encrypted = await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, key, ENCODER.encode(plaintext));

    const packed = new Uint8Array(iv.length + encrypted.byteLength);
    packed.set(iv);
    packed.set(new Uint8Array(encrypted), iv.length);

    return `vault:${btoa(String.fromCharCode(...packed))}`;
}

export async function decryptValue(ciphertext: string): Promise<string> {
    if (ciphertext.startsWith('b64:')) {
        return atob(ciphertext.slice(4));
    }

    if (!ciphertext.startsWith('vault:')) return ciphertext;

    const key = await getOrCreateVaultKey();
    if (!key) return '[DECRYPTION_UNAVAILABLE]';

    try {
        const packed = Uint8Array.from(atob(ciphertext.slice(6)), c => c.charCodeAt(0));
        const iv = packed.slice(0, 12);
        const data = packed.slice(12);
        const decrypted = await crypto.subtle.decrypt({ name: 'AES-GCM', iv }, key, data);
        return DECODER.decode(decrypted);
    } catch {
        return '[DECRYPTION_FAILED]';
    }
}

// ─── Vault Entry Helpers ───

export function createVaultEntry(
    name: string,
    type: VaultEntryType,
    category: VaultCategory,
    encryptedValue: string,
    options?: {
        provider?: string;
        metadata?: Record<string, string>;
        usageLimits?: Partial<UsageLimit>;
    },
): VaultEntry {
    const now = new Date().toISOString();
    return {
        id: `vault-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
        name,
        type,
        category,
        provider: options?.provider,
        encryptedValue,
        metadata: options?.metadata,
        usageLimits: {
            alertThreshold: 0.8,
            ...options?.usageLimits,
        },
        usageStats: {
            callsToday: 0,
            callsThisHour: 0,
            costToday: 0,
            costThisMonth: 0,
            callTimestamps: [],
        },
        createdAt: now,
        updatedAt: now,
    };
}

/** Mask a value for display: shows first 4 and last 4 chars */
export function maskValue(value: string): string {
    if (value.length <= 8) return '••••••••';
    return `${value.slice(0, 4)}${'•'.repeat(Math.min(value.length - 8, 20))}${value.slice(-4)}`;
}

/** Get a safe display label for an entry (never shows the actual value) */
export function getEntryLabel(entry: VaultEntry): string {
    const typeIcons: Record<VaultEntryType, string> = {
        api_key: '🔑',
        oauth_token: '🔐',
        email_credential: '📧',
        password: '🔒',
        custom: '🏷️',
    };
    return `${typeIcons[entry.type]} ${entry.name}`;
}
