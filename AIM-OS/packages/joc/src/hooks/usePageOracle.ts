/**
 * ═══════════════════════════════════════════════════════════════
 * PageOracleAPI — Canon-compliant interface for Oracle↔Page control
 * ═══════════════════════════════════════════════════════════════
 *
 * This module defines the contract between the Aether Oracle and
 * individual JOC pages. Pages register their capabilities, expose
 * their state, and subscribe to Oracle commands via this API.
 *
 * The Oracle uses this to:
 *   - Programmatically invoke page actions (dispatch, schedule, etc.)
 *   - Read page state without UI interaction
 *   - Subscribe to page events (user actions, state changes)
 *   - Coordinate multi-page workflows
 */

import { useEffect, useRef, useCallback } from 'react';
import { useOracleStore, type OracleSystem, type PermissionLevel } from '../store/oracleStore';
import type { PageType } from '../store/jocStore';

// ─── Core Types ───

/** A single action that Oracle can invoke on a page */
export interface OraclePageAction {
    /** Unique action identifier (e.g., 'dispatch.send', 'calendar.createEvent') */
    id: string;
    /** Human-readable label */
    label: string;
    /** Which Oracle system this action belongs to */
    system: OracleSystem;
    /** Action description for the Oracle to understand */
    description: string;
    /** Minimum permission level required to execute */
    minPermission: PermissionLevel;
    /** Parameter schema — what the Oracle needs to provide */
    params?: OracleActionParam[];
    /** Execute the action */
    execute: (params: Record<string, unknown>) => Promise<OracleActionResult>;
}

/** Parameter definition for an Oracle action */
export interface OracleActionParam {
    name: string;
    type: 'string' | 'number' | 'boolean' | 'select' | 'array';
    required: boolean;
    description: string;
    options?: string[]; // For 'select' type
    default?: unknown;
}

/** Result of an Oracle action execution */
export interface OracleActionResult {
    success: boolean;
    message: string;
    data?: Record<string, unknown>;
    error?: string;
}

/** A page event that Oracle can subscribe to */
export interface OraclePageEvent {
    type: string;
    page: PageType;
    timestamp: number;
    data: Record<string, unknown>;
}

/** Registration object that a page provides to the Oracle */
export interface PageOracleRegistration {
    /** Which page this registration belongs to */
    page: PageType;
    /** Actions the Oracle can invoke */
    actions: OraclePageAction[];
    /** Current page state getter */
    getState: () => Record<string, unknown>;
    /** Whether this page is currently active/mounted */
    active: boolean;
}

// ─── Oracle Event Bus ───

type EventHandler = (event: OraclePageEvent) => void;

class OracleEventBus {
    private handlers: Map<string, Set<EventHandler>> = new Map();
    private registrations: Map<PageType, PageOracleRegistration> = new Map();

    /** Register a page's Oracle capabilities */
    register(registration: PageOracleRegistration): void {
        this.registrations.set(registration.page, registration);
        this.emit({
            type: 'page:registered',
            page: registration.page,
            timestamp: Date.now(),
            data: {
                actions: registration.actions.map(a => ({
                    id: a.id,
                    label: a.label,
                    system: a.system,
                    minPermission: a.minPermission,
                })),
            },
        });
    }

    /** Unregister a page (when unmounted) */
    unregister(page: PageType): void {
        this.registrations.delete(page);
        this.emit({
            type: 'page:unregistered',
            page: page,
            timestamp: Date.now(),
            data: {},
        });
    }

    /** Get a page's registration */
    getRegistration(page: PageType): PageOracleRegistration | undefined {
        return this.registrations.get(page);
    }

    /** Get all registered pages */
    getAllRegistrations(): Map<PageType, PageOracleRegistration> {
        return new Map(this.registrations);
    }

    /** Get all available actions across all pages */
    getAllActions(): OraclePageAction[] {
        const actions: OraclePageAction[] = [];
        for (const reg of this.registrations.values()) {
            if (reg.active) {
                actions.push(...reg.actions);
            }
        }
        return actions;
    }

    /** Execute an action by ID, checking permissions */
    async executeAction(
        actionId: string,
        params: Record<string, unknown>,
        oracleMode: string,
        permissions: Record<OracleSystem, PermissionLevel>,
    ): Promise<OracleActionResult> {
        // Find the action across all registrations
        let targetAction: OraclePageAction | undefined;
        let targetPage: PageType | undefined;

        for (const [page, reg] of this.registrations) {
            const action = reg.actions.find(a => a.id === actionId);
            if (action) {
                targetAction = action;
                targetPage = page;
                break;
            }
        }

        if (!targetAction || !targetPage) {
            return { success: false, message: `Action "${actionId}" not found`, error: 'ACTION_NOT_FOUND' };
        }

        // Check Oracle mode
        if (oracleMode === 'offline') {
            return { success: false, message: 'Oracle is offline', error: 'ORACLE_OFFLINE' };
        }

        // Check permission level
        const systemPerm = permissions[targetAction.system];
        const permLevels: PermissionLevel[] = ['manual', 'supervised', 'auto'];
        const requiredLevel = permLevels.indexOf(targetAction.minPermission);
        const currentLevel = permLevels.indexOf(systemPerm);

        if (currentLevel < requiredLevel) {
            return {
                success: false,
                message: `Insufficient permission for ${targetAction.label}. Required: ${targetAction.minPermission}, current: ${systemPerm}`,
                error: 'PERMISSION_DENIED',
            };
        }

        // Execute
        try {
            const result = await targetAction.execute(params);
            this.emit({
                type: 'action:executed',
                page: targetPage,
                timestamp: Date.now(),
                data: { actionId, params, result },
            });
            return result;
        } catch (err) {
            const errorMsg = err instanceof Error ? err.message : String(err);
            return { success: false, message: `Action failed: ${errorMsg}`, error: 'EXECUTION_ERROR' };
        }
    }

    /** Subscribe to events */
    on(eventType: string, handler: EventHandler): () => void {
        if (!this.handlers.has(eventType)) {
            this.handlers.set(eventType, new Set());
        }
        this.handlers.get(eventType)!.add(handler);

        // Return unsubscribe function
        return () => {
            this.handlers.get(eventType)?.delete(handler);
        };
    }

    /** Subscribe to all events */
    onAny(handler: EventHandler): () => void {
        return this.on('*', handler);
    }

    /** Emit an event */
    emit(event: OraclePageEvent): void {
        // Notify specific handlers
        const specific = this.handlers.get(event.type);
        if (specific) {
            for (const handler of specific) {
                try { handler(event); } catch { /* swallow */ }
            }
        }
        // Notify wildcard handlers
        const wildcard = this.handlers.get('*');
        if (wildcard) {
            for (const handler of wildcard) {
                try { handler(event); } catch { /* swallow */ }
            }
        }
    }
}

// ─── Singleton Instance ───

export const oracleEventBus = new OracleEventBus();

// ─── React Hook: usePageOracle ───

/**
 * Hook for pages to register their Oracle capabilities.
 * Call this in any page component to make it Oracle-controllable.
 *
 * @example
 * ```tsx
 * function DispatchPage() {
 *   usePageOracle('dispatch', {
 *     actions: [
 *       {
 *         id: 'dispatch.send',
 *         label: 'Send Dispatch',
 *         system: 'dispatch',
 *         description: 'Send a prompt to selected AI providers',
 *         minPermission: 'supervised',
 *         params: [
 *           { name: 'prompt', type: 'string', required: true, description: 'The prompt to send' },
 *           { name: 'targets', type: 'array', required: true, description: 'Target AI providers' },
 *         ],
 *         execute: async (params) => {
 *           await sendDispatch(params.prompt as string, params.targets as string[]);
 *           return { success: true, message: 'Dispatch sent successfully' };
 *         },
 *       },
 *     ],
 *     getState: () => ({ currentPrompt, selectedTargets, pendingDispatches }),
 *   });
 * }
 * ```
 */
export function usePageOracle(
    page: PageType,
    config: {
        actions: OraclePageAction[];
        getState: () => Record<string, unknown>;
    },
): {
    /** Emit a page event for Oracle to observe */
    emitEvent: (type: string, data: Record<string, unknown>) => void;
    /** Check if Oracle has permission for a system */
    hasPermission: (system: OracleSystem, minLevel: PermissionLevel) => boolean;
    /** Current Oracle mode */
    oracleMode: string;
} {
    const { mode, permissions } = useOracleStore();
    const configRef = useRef(config);
    configRef.current = config;

    // Register on mount, unregister on unmount
    useEffect(() => {
        oracleEventBus.register({
            page,
            actions: configRef.current.actions,
            getState: configRef.current.getState,
            active: true,
        });

        return () => {
            oracleEventBus.unregister(page);
        };
    }, [page]);

    // Update registration when actions change
    useEffect(() => {
        const existing = oracleEventBus.getRegistration(page);
        if (existing) {
            oracleEventBus.register({
                ...existing,
                actions: config.actions,
                getState: config.getState,
            });
        }
    }, [page, config.actions, config.getState]);

    const emitEvent = useCallback((type: string, data: Record<string, unknown>) => {
        oracleEventBus.emit({
            type,
            page,
            timestamp: Date.now(),
            data,
        });
    }, [page]);

    const hasPermission = useCallback((system: OracleSystem, minLevel: PermissionLevel) => {
        if (mode === 'offline') return false;
        const permLevels: PermissionLevel[] = ['manual', 'supervised', 'auto'];
        return permLevels.indexOf(permissions[system]) >= permLevels.indexOf(minLevel);
    }, [mode, permissions]);

    return {
        emitEvent,
        hasPermission,
        oracleMode: mode,
    };
}

// ─── React Hook: useOracleSubscription ───

/**
 * Subscribe to Oracle events from any component.
 * Useful for monitoring pages, the Oracle page itself, or the BottomBar.
 */
export function useOracleSubscription(
    eventType: string,
    handler: EventHandler,
): void {
    const handlerRef = useRef(handler);
    handlerRef.current = handler;

    useEffect(() => {
        const unsub = oracleEventBus.on(eventType, (event) => {
            handlerRef.current(event);
        });
        return unsub;
    }, [eventType]);
}
