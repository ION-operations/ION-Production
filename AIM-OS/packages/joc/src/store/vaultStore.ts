/**
 * Vault Store — Zustand state for credential vault
 *
 * Encrypted persistence via localStorage.
 * Manages vault entries, usage stats, and alerts.
 */

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import {
    type VaultEntry,
    type VaultEntryType,
    type VaultCategory,
    type UsageLimit,
    type UsageStats,
    encryptValue,
    createVaultEntry,
} from '../services/vaultService';
import { encryptedStorage } from '../services/sessionPersist';

// ─── Store Types ───

export interface VaultAlert {
    id: string;
    entryId: string;
    entryName: string;
    message: string;
    severity: 'warning' | 'critical';
    timestamp: string;
    dismissed: boolean;
}

export interface VaultStoreState {
    entries: Record<string, VaultEntry>;
    alerts: VaultAlert[];

    // CRUD
    addEntry: (
        name: string,
        type: VaultEntryType,
        category: VaultCategory,
        plainValue: string,
        options?: {
            provider?: string;
            metadata?: Record<string, string>;
            usageLimits?: Partial<UsageLimit>;
        },
    ) => Promise<string>; // returns entry ID

    updateEntry: (
        entryId: string,
        updates: {
            name?: string;
            plainValue?: string;
            metadata?: Record<string, string>;
            usageLimits?: Partial<UsageLimit>;
        },
    ) => Promise<void>;

    deleteEntry: (entryId: string) => void;

    // Usage
    recordUsage: (entryId: string, stats: UsageStats) => void;
    resetDailyStats: () => void;

    // Alerts
    addAlert: (alert: Omit<VaultAlert, 'id' | 'timestamp' | 'dismissed'>) => void;
    dismissAlert: (alertId: string) => void;

    // Queries
    getEntriesByCategory: (category: VaultCategory) => VaultEntry[];
    getEntry: (entryId: string) => VaultEntry | undefined;
}

// ─── Store ───

export const useVaultStore = create<VaultStoreState>()(
    (persist as any)(
        (set: any, get: any) => ({
            entries: {},
            alerts: [],

            // ─── CRUD ───

            addEntry: async (
                name: string,
                type: VaultEntryType,
                category: VaultCategory,
                plainValue: string,
                options?: {
                    provider?: string;
                    metadata?: Record<string, string>;
                    usageLimits?: Partial<UsageLimit>;
                },
            ): Promise<string> => {
                const encrypted = await encryptValue(plainValue);
                const entry = createVaultEntry(name, type, category, encrypted, options);

                set((state: VaultStoreState) => ({
                    entries: { ...state.entries, [entry.id]: entry },
                }));

                return entry.id;
            },

            updateEntry: async (
                entryId: string,
                updates: {
                    name?: string;
                    plainValue?: string;
                    metadata?: Record<string, string>;
                    usageLimits?: Partial<UsageLimit>;
                },
            ): Promise<void> => {
                const entries = { ...get().entries };
                const entry = entries[entryId];
                if (!entry) return;

                const updated = { ...entry, updatedAt: new Date().toISOString() };

                if (updates.name !== undefined) updated.name = updates.name;
                if (updates.metadata !== undefined) updated.metadata = updates.metadata;
                if (updates.usageLimits !== undefined) {
                    updated.usageLimits = { ...updated.usageLimits, ...updates.usageLimits };
                }
                if (updates.plainValue !== undefined) {
                    updated.encryptedValue = await encryptValue(updates.plainValue);
                }

                entries[entryId] = updated;
                set({ entries });
            },

            deleteEntry: (entryId: string) => {
                set((state: VaultStoreState) => {
                    const entries = { ...state.entries };
                    delete entries[entryId];
                    return { entries };
                });
            },

            // ─── Usage ───

            recordUsage: (entryId: string, stats: UsageStats) => {
                const entries = { ...get().entries };
                if (entries[entryId]) {
                    entries[entryId] = { ...entries[entryId], usageStats: stats };
                    set({ entries });
                }
            },

            resetDailyStats: () => {
                const entries = { ...get().entries };
                for (const id of Object.keys(entries)) {
                    entries[id] = {
                        ...entries[id],
                        usageStats: {
                            ...entries[id].usageStats,
                            callsToday: 0,
                            callsThisHour: 0,
                            costToday: 0,
                            callTimestamps: [],
                        },
                    };
                }
                set({ entries });
            },

            // ─── Alerts ───

            addAlert: (alert: Omit<VaultAlert, 'id' | 'timestamp' | 'dismissed'>) => {
                const newAlert: VaultAlert = {
                    ...alert,
                    id: `alert-${Date.now()}`,
                    timestamp: new Date().toISOString(),
                    dismissed: false,
                };
                set((state: VaultStoreState) => ({
                    alerts: [newAlert, ...state.alerts].slice(0, 50), // keep last 50
                }));
            },

            dismissAlert: (alertId: string) => {
                set((state: VaultStoreState) => ({
                    alerts: state.alerts.map((a: VaultAlert) =>
                        a.id === alertId ? { ...a, dismissed: true } : a,
                    ),
                }));
            },

            // ─── Queries ───

            getEntriesByCategory: (category: VaultCategory): VaultEntry[] => {
                return (Object.values(get().entries) as VaultEntry[]).filter(
                    (e: VaultEntry) => e.category === category,
                );
            },

            getEntry: (entryId: string): VaultEntry | undefined => {
                return get().entries[entryId];
            },
        }),
        {
            name: 'aim-os-vault',
            storage: createJSONStorage(() => encryptedStorage as any),
            partialize: (state: any) => ({
                entries: state.entries,
                alerts: (state.alerts || []).filter((a: VaultAlert) => !a.dismissed),
            }),
        },
    ),
);
