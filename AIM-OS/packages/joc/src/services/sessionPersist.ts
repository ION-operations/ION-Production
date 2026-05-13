/**
 * Session Persistence — Encrypted localStorage storage for Zustand
 *
 * Uses AES-GCM via the Web Crypto API for encryption at rest.
 * Falls back to plaintext if crypto is unavailable (e.g., HTTP).
 */

// ─── Key Management ───

const STORAGE_KEY_NAME = 'aim-os-session-key';
const ENCODER = new TextEncoder();
const DECODER = new TextDecoder();

async function getOrCreateKey(): Promise<CryptoKey | null> {
    if (typeof crypto === 'undefined' || !crypto.subtle) return null;

    try {
        // Check for existing key in sessionStorage (survives tabs, not restarts)
        const existing = sessionStorage.getItem(STORAGE_KEY_NAME);
        if (existing) {
            const raw = Uint8Array.from(atob(existing), c => c.charCodeAt(0));
            return crypto.subtle.importKey('raw', raw, 'AES-GCM', true, ['encrypt', 'decrypt']);
        }

        // Generate new key
        const key = await crypto.subtle.generateKey({ name: 'AES-GCM', length: 256 }, true, ['encrypt', 'decrypt']);
        const exported = await crypto.subtle.exportKey('raw', key);
        sessionStorage.setItem(STORAGE_KEY_NAME, btoa(String.fromCharCode(...new Uint8Array(exported))));
        return key;
    } catch {
        return null;
    }
}

// ─── Encrypt / Decrypt ───

async function encrypt(data: string): Promise<string> {
    const key = await getOrCreateKey();
    if (!key) return btoa(data); // Fallback: base64 only

    const iv = crypto.getRandomValues(new Uint8Array(12));
    const encrypted = await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, key, ENCODER.encode(data));

    // Pack: iv (12 bytes) + ciphertext
    const packed = new Uint8Array(iv.length + encrypted.byteLength);
    packed.set(iv);
    packed.set(new Uint8Array(encrypted), iv.length);

    return 'enc:' + btoa(String.fromCharCode(...packed));
}

async function decrypt(stored: string): Promise<string> {
    if (!stored.startsWith('enc:')) {
        // Plaintext fallback (base64)
        try { return atob(stored); } catch { return stored; }
    }

    const key = await getOrCreateKey();
    if (!key) return stored;

    try {
        const packed = Uint8Array.from(atob(stored.slice(4)), c => c.charCodeAt(0));
        const iv = packed.slice(0, 12);
        const ciphertext = packed.slice(12);
        const decrypted = await crypto.subtle.decrypt({ name: 'AES-GCM', iv }, key, ciphertext);
        return DECODER.decode(decrypted);
    } catch {
        // Key mismatch (new session) — return empty to reset
        return '{}';
    }
}

// ─── Zustand Persist Storage Adapter ───

export interface EncryptedStorage {
    getItem: (name: string) => Promise<string | null>;
    setItem: (name: string, value: string) => Promise<void>;
    removeItem: (name: string) => Promise<void>;
}

export const encryptedStorage: EncryptedStorage = {
    getItem: async (name: string): Promise<string | null> => {
        const raw = localStorage.getItem(name);
        if (!raw) return null;
        return decrypt(raw);
    },

    setItem: async (name: string, value: string): Promise<void> => {
        const encrypted = await encrypt(value);
        localStorage.setItem(name, encrypted);
    },

    removeItem: async (name: string): Promise<void> => {
        localStorage.removeItem(name);
    },
};

// ─── State Partitioner (exclude non-serializable data) ───

/**
 * Filter session state for persistence.
 * Excludes volatile fields that should not survive a reload.
 */
export function partitionSessionState(state: any): any {
    const { sessions, activeSessionId } = state;
    const persistedSessions: Record<string, any> = {};

    for (const [id, session] of Object.entries(sessions)) {
        const s = session as any;
        persistedSessions[id] = {
            provider: s.provider,
            sessionId: s.sessionId,
            url: s.url,
            conversation: s.conversation || [],
            attachedFiles: s.attachedFiles || [],
            promptDraft: s.promptDraft || '',
            // Don't persist: browserId, basConnected, health, status, events, pipeline, overlay, viewport
        };
    }

    return { sessions: persistedSessions, activeSessionId };
}

/**
 * Merge persisted state with default state on hydration.
 */
export function mergeSessionState(persisted: any, current: any): any {
    if (!persisted?.sessions) return current;

    const merged = { ...current };
    merged.activeSessionId = persisted.activeSessionId || current.activeSessionId;

    for (const [id, persistedSession] of Object.entries(persisted.sessions)) {
        const ps = persistedSession as any;
        if (merged.sessions[id]) {
            // Merge persisted fields into existing session default
            merged.sessions[id] = {
                ...merged.sessions[id],
                conversation: ps.conversation || [],
                attachedFiles: ps.attachedFiles || [],
                promptDraft: ps.promptDraft || '',
            };
        }
    }

    return merged;
}
