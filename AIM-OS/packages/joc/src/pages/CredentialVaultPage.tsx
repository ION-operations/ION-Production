import { useCallback, useEffect, useMemo, useState } from 'react';
import type {
    VaultEntry,
    VaultEntryType,
    VaultCategory,
    UsageLimit,
    UsageStats
} from '../services/vaultService';
import { checkLimit, getUsagePercent } from '../services/rateLimiter';
import {
    deleteVaultCredential,
    getVaultUsage,
    getVaultCredentials,
    saveVaultCredential,
    type BASVaultCredential,
    updateVaultCredential
} from '../services/basClient';

interface VaultAlert {
    id: string;
    message: string;
    severity: 'warning' | 'critical';
    dismissed: boolean;
}

interface SaveDialogPayload {
    id?: string;
    name: string;
    type: VaultEntryType;
    category: VaultCategory;
    provider: string;
    value?: string;
    usageLimits: Partial<UsageLimit>;
}

const categoryMeta: Record<VaultCategory, { label: string }> = {
    ai_provider: { label: 'AI Providers' },
    email: { label: 'Email and Accounts' },
    cloud_storage: { label: 'Cloud Storage' },
    git: { label: 'Git and Source' },
    custom: { label: 'Custom' },
};

const typeOptions: { value: VaultEntryType; label: string }[] = [
    { value: 'api_key', label: 'API Key' },
    { value: 'oauth_token', label: 'OAuth Token' },
    { value: 'email_credential', label: 'Email Credential' },
    { value: 'password', label: 'Password' },
    { value: 'custom', label: 'Custom' },
];

const categoryOptions: { value: VaultCategory; label: string }[] = [
    { value: 'ai_provider', label: 'AI Provider' },
    { value: 'email', label: 'Email' },
    { value: 'cloud_storage', label: 'Cloud Storage' },
    { value: 'git', label: 'Git' },
    { value: 'custom', label: 'Custom' },
];

const supportedTypes = new Set<VaultEntryType>(['api_key', 'oauth_token', 'email_credential', 'password', 'custom']);
const supportedCategories = new Set<VaultCategory>(['ai_provider', 'email', 'cloud_storage', 'git', 'custom']);

function normalizeUsageLimits(value: unknown): UsageLimit {
    if (!value || typeof value !== 'object') {
        return { alertThreshold: 0.8 };
    }
    const src = value as Record<string, unknown>;
    return {
        maxCallsPerHour: typeof src.maxCallsPerHour === 'number' ? src.maxCallsPerHour : undefined,
        maxCallsPerDay: typeof src.maxCallsPerDay === 'number' ? src.maxCallsPerDay : undefined,
        maxCostPerDay: typeof src.maxCostPerDay === 'number' ? src.maxCostPerDay : undefined,
        maxCostPerMonth: typeof src.maxCostPerMonth === 'number' ? src.maxCostPerMonth : undefined,
        alertThreshold: typeof src.alertThreshold === 'number' ? src.alertThreshold : 0.8,
    };
}

function normalizeUsageStats(value: unknown): UsageStats {
    if (!value || typeof value !== 'object') {
        return {
            callsToday: 0,
            callsThisHour: 0,
            costToday: 0,
            costThisMonth: 0,
            callTimestamps: [],
        };
    }
    const src = value as Record<string, unknown>;
    return {
        callsToday: typeof src.callsToday === 'number' ? src.callsToday : 0,
        callsThisHour: typeof src.callsThisHour === 'number' ? src.callsThisHour : 0,
        costToday: typeof src.costToday === 'number' ? src.costToday : 0,
        costThisMonth: typeof src.costThisMonth === 'number' ? src.costThisMonth : 0,
        lastUsed: typeof src.lastUsed === 'string' ? src.lastUsed : undefined,
        callTimestamps: Array.isArray(src.callTimestamps)
            ? src.callTimestamps.filter(v => typeof v === 'number') as number[]
            : [],
    };
}

function inferType(metadata: Record<string, any>): VaultEntryType {
    return typeof metadata.type === 'string' && supportedTypes.has(metadata.type as VaultEntryType)
        ? metadata.type as VaultEntryType
        : 'custom';
}

function inferCategory(metadata: Record<string, any>, provider: string): VaultCategory {
    if (typeof metadata.category === 'string' && supportedCategories.has(metadata.category as VaultCategory)) {
        return metadata.category as VaultCategory;
    }
    return provider && provider !== 'custom' ? 'ai_provider' : 'custom';
}

function mapCredentialToEntry(credential: BASVaultCredential): VaultEntry {
    const metadata = credential.metadata || {};
    const provider = typeof metadata.provider === 'string' && metadata.provider.trim().length > 0
        ? metadata.provider
        : credential.provider;

    return {
        id: credential.id,
        name: credential.label,
        type: inferType(metadata),
        category: inferCategory(metadata, provider),
        provider,
        encryptedValue: '[server-vault]',
        metadata,
        usageLimits: normalizeUsageLimits(metadata.usageLimits),
        usageStats: normalizeUsageStats(metadata.usageStats),
        createdAt: credential.createdAt,
        updatedAt: credential.updatedAt,
    };
}

function toSupportedProvider(provider: string): 'chatgpt' | 'claude' | 'gemini' | 'custom' {
    const normalized = provider.trim().toLowerCase();
    if (normalized === 'chatgpt' || normalized === 'claude' || normalized === 'gemini') {
        return normalized;
    }
    return 'custom';
}

function AddEntryDialog({
    onClose,
    onSave,
    editEntry,
}: {
    onClose: () => void;
    onSave: (payload: SaveDialogPayload) => Promise<void>;
    editEntry?: VaultEntry;
}) {
    const [name, setName] = useState(editEntry?.name || '');
    const [type, setType] = useState<VaultEntryType>(editEntry?.type || 'api_key');
    const [category, setCategory] = useState<VaultCategory>(editEntry?.category || 'ai_provider');
    const [provider, setProvider] = useState(editEntry?.provider || '');
    const [value, setValue] = useState('');
    const [maxCallsPerHour, setMaxCallsPerHour] = useState(editEntry?.usageLimits.maxCallsPerHour?.toString() || '');
    const [maxCallsPerDay, setMaxCallsPerDay] = useState(editEntry?.usageLimits.maxCallsPerDay?.toString() || '');
    const [maxCostPerDay, setMaxCostPerDay] = useState(editEntry?.usageLimits.maxCostPerDay?.toString() || '');
    const [maxCostPerMonth, setMaxCostPerMonth] = useState(editEntry?.usageLimits.maxCostPerMonth?.toString() || '');
    const [alertThreshold, setAlertThreshold] = useState(editEntry?.usageLimits.alertThreshold?.toString() || '0.8');
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState('');

    const handleSave = async () => {
        if (!name.trim()) return;
        if (!editEntry && !value.trim()) return;

        const usageLimits: Partial<UsageLimit> = {
            maxCallsPerHour: maxCallsPerHour ? parseInt(maxCallsPerHour, 10) : undefined,
            maxCallsPerDay: maxCallsPerDay ? parseInt(maxCallsPerDay, 10) : undefined,
            maxCostPerDay: maxCostPerDay ? parseFloat(maxCostPerDay) : undefined,
            maxCostPerMonth: maxCostPerMonth ? parseFloat(maxCostPerMonth) : undefined,
            alertThreshold: alertThreshold ? parseFloat(alertThreshold) : undefined,
        };

        setSaving(true);
        setError('');
        try {
            await onSave({
                id: editEntry?.id,
                name: name.trim(),
                type,
                category,
                provider: provider.trim(),
                value: value.trim() ? value.trim() : undefined,
                usageLimits,
            });
            onClose();
        } catch (err) {
            setError(err instanceof Error ? err.message : String(err));
        } finally {
            setSaving(false);
        }
    };

    return (
        <div style={styles.overlay} onClick={onClose}>
            <div style={styles.dialog} onClick={(e) => e.stopPropagation()}>
                <h3 style={styles.dialogTitle}>{editEntry ? 'Edit Credential' : 'Add Credential'}</h3>
                <label style={styles.label}>Name</label>
                <input style={styles.input} value={name} onChange={(e) => setName(e.target.value)} />

                {!editEntry && (
                    <>
                        <label style={styles.label}>Type</label>
                        <select style={styles.input} value={type} onChange={(e) => setType(e.target.value as VaultEntryType)}>
                            {typeOptions.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
                        </select>

                        <label style={styles.label}>Category</label>
                        <select style={styles.input} value={category} onChange={(e) => setCategory(e.target.value as VaultCategory)}>
                            {categoryOptions.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
                        </select>
                    </>
                )}

                <label style={styles.label}>Provider</label>
                <input style={styles.input} value={provider} onChange={(e) => setProvider(e.target.value)} placeholder="chatgpt/gemini/claude/custom" />

                <label style={styles.label}>{editEntry ? 'New Secret (optional)' : 'Secret Value'}</label>
                <input style={styles.input} type="password" value={value} onChange={(e) => setValue(e.target.value)} />

                <div style={styles.row}>
                    <input style={styles.input} type="number" value={maxCallsPerHour} onChange={(e) => setMaxCallsPerHour(e.target.value)} placeholder="Calls/hour" />
                    <input style={styles.input} type="number" value={maxCallsPerDay} onChange={(e) => setMaxCallsPerDay(e.target.value)} placeholder="Calls/day" />
                </div>
                <div style={styles.row}>
                    <input style={styles.input} type="number" step="0.01" value={maxCostPerDay} onChange={(e) => setMaxCostPerDay(e.target.value)} placeholder="Cost/day" />
                    <input style={styles.input} type="number" step="0.01" value={maxCostPerMonth} onChange={(e) => setMaxCostPerMonth(e.target.value)} placeholder="Cost/month" />
                </div>
                <input
                    style={styles.input}
                    type="number"
                    min="0.01"
                    max="0.99"
                    step="0.01"
                    value={alertThreshold}
                    onChange={(e) => setAlertThreshold(e.target.value)}
                    placeholder="Alert threshold (0.01-0.99)"
                />

                {error && <div style={styles.error}>{error}</div>}

                <div style={styles.actions}>
                    <button style={styles.btnSecondary} onClick={onClose}>Cancel</button>
                    <button style={styles.btnPrimary} onClick={() => { void handleSave(); }} disabled={saving || !name.trim() || (!editEntry && !value.trim())}>
                        {saving ? 'Saving...' : (editEntry ? 'Update' : 'Create')}
                    </button>
                </div>
            </div>
        </div>
    );
}

function EntryCard({
    entry,
    onEdit,
    onDelete,
}: {
    entry: VaultEntry;
    onEdit: () => void;
    onDelete: () => void;
}) {
    const usagePercent = getUsagePercent(entry);
    const limitCheck = checkLimit(entry);

    return (
        <div style={styles.card}>
            <div style={styles.cardHead}>
                <div>
                    <div style={styles.cardTitle}>{entry.name}</div>
                    <div style={styles.cardSub}>{entry.provider || 'custom'} . {entry.type}</div>
                </div>
                <div style={styles.row}>
                    <button style={styles.btnSmall} onClick={onEdit}>Edit</button>
                    <button style={{ ...styles.btnSmall, color: '#ff6b6b' }} onClick={onDelete}>Delete</button>
                </div>
            </div>
            <div style={styles.progressTrack}>
                <div style={{ ...styles.progressFill, width: `${Math.min(usagePercent, 100)}%` }} />
            </div>
            <div style={styles.cardSub}>Usage: {usagePercent}%</div>
            {limitCheck.alerts.map((alert, i) => (
                <div key={i} style={styles.warningText}>{alert}</div>
            ))}
            <div style={styles.cardSub}>Updated: {new Date(entry.updatedAt).toLocaleString()}</div>
        </div>
    );
}

export function CredentialVaultPage() {
    const [entries, setEntries] = useState<VaultEntry[]>([]);
    const [alerts, setAlerts] = useState<VaultAlert[]>([]);
    const [loading, setLoading] = useState(true);
    const [loadError, setLoadError] = useState('');
    const [showDialog, setShowDialog] = useState(false);
    const [editingEntry, setEditingEntry] = useState<VaultEntry | undefined>();
    const [confirmDelete, setConfirmDelete] = useState<string | null>(null);

    const addAlert = useCallback((message: string, severity: 'warning' | 'critical' = 'warning') => {
        setAlerts(prev => [{
            id: `alert-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
            message,
            severity,
            dismissed: false,
        }, ...prev].slice(0, 20));
    }, []);

    const loadEntries = useCallback(async () => {
        setLoading(true);
        setLoadError('');
        try {
            const credentials = await getVaultCredentials();
            const enrichedEntries = await Promise.all(credentials.map(async (credential) => {
                try {
                    const usage = await getVaultUsage(credential.id);
                    const mergedCredential: BASVaultCredential = {
                        ...credential,
                        metadata: {
                            ...(credential.metadata || {}),
                            usageLimits: usage.limits,
                            usageStats: usage.stats,
                        }
                    };
                    return mapCredentialToEntry(mergedCredential);
                } catch {
                    return mapCredentialToEntry(credential);
                }
            }));
            setEntries(enrichedEntries);
        } catch (error) {
            const message = error instanceof Error ? error.message : String(error);
            setLoadError(message);
            addAlert(`Vault load failed: ${message}`, 'critical');
        } finally {
            setLoading(false);
        }
    }, [addAlert]);

    useEffect(() => {
        void loadEntries();
    }, [loadEntries]);

    const handleSave = useCallback(async (payload: SaveDialogPayload) => {
        const metadata: Record<string, any> = {
            type: payload.type,
            category: payload.category,
            provider: payload.provider || undefined,
            usageLimits: payload.usageLimits,
        };

        if (payload.id) {
            const updatePayload: { label?: string; metadata?: Record<string, any>; secret?: Record<string, string> } = {
                label: payload.name,
                metadata,
            };
            if (payload.value) {
                updatePayload.secret = {
                    value: payload.value,
                    provider: payload.provider || '',
                    type: payload.type,
                    category: payload.category,
                };
            }
            await updateVaultCredential(payload.id, updatePayload);
            addAlert(`Updated vault credential: ${payload.name}`);
        } else {
            await saveVaultCredential({
                provider: toSupportedProvider(payload.provider),
                label: payload.name,
                secret: {
                    value: payload.value || '',
                    provider: payload.provider || '',
                    type: payload.type,
                    category: payload.category,
                },
                metadata,
            });
            addAlert(`Created vault credential: ${payload.name}`);
        }

        await loadEntries();
    }, [addAlert, loadEntries]);

    const handleDelete = useCallback(async (id: string) => {
        const entry = entries.find(e => e.id === id);
        await deleteVaultCredential(id);
        addAlert(`Deleted vault credential: ${entry?.name || id}`);
        setConfirmDelete(null);
        await loadEntries();
    }, [entries, addAlert, loadEntries]);

    const activeAlerts = useMemo(() => alerts.filter(a => !a.dismissed), [alerts]);
    const grouped = useMemo(() => {
        const categories: VaultCategory[] = ['ai_provider', 'email', 'cloud_storage', 'git', 'custom'];
        return categories.map(cat => ({ category: cat, entries: entries.filter(e => e.category === cat) }))
            .filter(group => group.entries.length > 0);
    }, [entries]);

    return (
        <div style={styles.page}>
            <div style={styles.header}>
                <div>
                    <h2 style={styles.heading}>Credential Vault</h2>
                    <div style={styles.subheading}>Canonical BAS server-side vault for automation credentials</div>
                </div>
                <div style={styles.row}>
                    <button style={styles.btnSecondary} onClick={() => { void loadEntries(); }} disabled={loading}>Refresh</button>
                    <button style={styles.btnPrimary} onClick={() => { setEditingEntry(undefined); setShowDialog(true); }}>Add Credential</button>
                </div>
            </div>

            <div style={styles.banner}>
                Server-side encrypted storage. Secret values are not returned to this UI after creation.
            </div>

            {loadError && <div style={styles.error}>{loadError}</div>}

            {activeAlerts.length > 0 && (
                <div style={styles.alerts}>
                    {activeAlerts.slice(0, 3).map(alert => (
                        <div key={alert.id} style={styles.alertItem}>{alert.message}</div>
                    ))}
                </div>
            )}

            {loading ? (
                <div style={styles.empty}>Loading vault entries...</div>
            ) : grouped.length === 0 ? (
                <div style={styles.empty}>No credentials found. Add one to start BAS-linked automation.</div>
            ) : (
                grouped.map(group => (
                    <div key={group.category} style={{ marginBottom: 20 }}>
                        <div style={styles.groupTitle}>{categoryMeta[group.category].label} ({group.entries.length})</div>
                        <div style={styles.grid}>
                            {group.entries.map(entry => (
                                <EntryCard
                                    key={entry.id}
                                    entry={entry}
                                    onEdit={() => { setEditingEntry(entry); setShowDialog(true); }}
                                    onDelete={() => setConfirmDelete(entry.id)}
                                />
                            ))}
                        </div>
                    </div>
                ))
            )}

            {confirmDelete && (
                <div style={styles.overlay} onClick={() => setConfirmDelete(null)}>
                    <div style={styles.dialog} onClick={(e) => e.stopPropagation()}>
                        <h3 style={styles.dialogTitle}>Delete Credential</h3>
                        <p style={styles.subheading}>This removes the credential from BAS vault storage.</p>
                        <div style={styles.actions}>
                            <button style={styles.btnSecondary} onClick={() => setConfirmDelete(null)}>Cancel</button>
                            <button style={{ ...styles.btnPrimary, background: '#ff6b6b' }} onClick={() => { void handleDelete(confirmDelete); }}>Delete</button>
                        </div>
                    </div>
                </div>
            )}

            {showDialog && (
                <AddEntryDialog
                    editEntry={editingEntry}
                    onSave={handleSave}
                    onClose={() => { setShowDialog(false); setEditingEntry(undefined); }}
                />
            )}
        </div>
    );
}

const styles: Record<string, React.CSSProperties> = {
    page: { padding: 24, maxWidth: 960, margin: '0 auto', fontFamily: "'Inter', system-ui, sans-serif", color: '#d1d5db' },
    header: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 14 },
    heading: { margin: 0, fontSize: 22 },
    subheading: { fontSize: 12, color: '#8b939f', marginTop: 4 },
    banner: { padding: '10px 12px', borderRadius: 8, border: '1px solid rgba(78,205,196,0.16)', background: 'rgba(78,205,196,0.05)', marginBottom: 12, fontSize: 12 },
    alerts: { display: 'flex', flexDirection: 'column', gap: 6, marginBottom: 12 },
    alertItem: { padding: '8px 10px', borderRadius: 8, background: 'rgba(255,217,61,0.08)', border: '1px solid rgba(255,217,61,0.2)', fontSize: 12 },
    grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 12 },
    groupTitle: { fontSize: 12, textTransform: 'uppercase', color: '#9aa2ad', marginBottom: 10, letterSpacing: '0.5px' },
    card: { border: '1px solid rgba(255,255,255,0.08)', borderRadius: 10, padding: 12, background: 'rgba(255,255,255,0.02)' },
    cardHead: { display: 'flex', justifyContent: 'space-between', gap: 8, marginBottom: 8 },
    cardTitle: { fontSize: 14, fontWeight: 600 },
    cardSub: { fontSize: 11, color: '#8b939f', marginTop: 3 },
    progressTrack: { height: 4, background: 'rgba(255,255,255,0.08)', borderRadius: 4, overflow: 'hidden', marginTop: 8 },
    progressFill: { height: '100%', background: '#4ecdc4' },
    warningText: { fontSize: 11, color: '#ffd93d', marginTop: 4 },
    empty: { padding: 24, textAlign: 'center', border: '1px dashed rgba(255,255,255,0.16)', borderRadius: 10, color: '#8b939f' },
    overlay: { position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 },
    dialog: { width: '100%', maxWidth: 520, background: '#171b22', border: '1px solid rgba(255,255,255,0.14)', borderRadius: 10, padding: 14 },
    dialogTitle: { margin: 0, marginBottom: 10, fontSize: 16 },
    label: { display: 'block', fontSize: 12, marginBottom: 5, color: '#a7afba' },
    input: { width: '100%', borderRadius: 6, border: '1px solid rgba(255,255,255,0.12)', background: 'rgba(255,255,255,0.04)', color: '#e5e7eb', padding: '8px 10px', marginBottom: 10, boxSizing: 'border-box' },
    actions: { display: 'flex', justifyContent: 'flex-end', gap: 8, marginTop: 10 },
    row: { display: 'flex', gap: 8 },
    btnPrimary: { border: 'none', borderRadius: 6, padding: '8px 12px', background: '#4ecdc4', color: '#0a0a0a', fontWeight: 600, cursor: 'pointer' },
    btnSecondary: { border: '1px solid rgba(255,255,255,0.18)', borderRadius: 6, padding: '8px 12px', background: 'rgba(255,255,255,0.05)', color: '#d1d5db', cursor: 'pointer' },
    btnSmall: { border: '1px solid rgba(255,255,255,0.16)', borderRadius: 6, padding: '4px 8px', background: 'rgba(255,255,255,0.04)', color: '#cbd5e1', fontSize: 11, cursor: 'pointer' },
    error: { padding: '8px 10px', borderRadius: 8, background: 'rgba(255,107,107,0.1)', border: '1px solid rgba(255,107,107,0.26)', color: '#ffb4b4', fontSize: 12 },
};
