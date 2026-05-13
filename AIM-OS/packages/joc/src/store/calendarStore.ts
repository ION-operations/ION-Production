/**
 * Calendar Store — Zustand state for calendar & scheduler
 *
 * Manages scheduled events, automation macros, and calendar view state.
 * Encrypted persistence via localStorage.
 */

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import {
    type ScheduledEvent,
    type EventType,
    type EventAction,
    type RecurrenceType,
    createScheduledEvent,
    calculateNextRun,
    scheduleEvent as scheduleTimerEvent,
    cancelTimer,
    stopAllTimers,
} from '../services/schedulerEngine';
import {
    type AutomationMacro,
    type MacroExecution,
    BUILT_IN_MACROS,
} from '../services/automationMacros';
import { encryptedStorage } from '../services/sessionPersist';

// ─── Types ───

export type CalendarView = 'month' | 'week' | 'day';

export interface CalendarStoreState {
    // ─── Data ───
    events: Record<string, ScheduledEvent>;
    macros: Record<string, AutomationMacro>;
    runningMacro: MacroExecution | null;

    // ─── View ───
    view: CalendarView;
    selectedDate: string;        // ISO date string (YYYY-MM-DD)
    viewMonth: number;           // 0-11
    viewYear: number;

    // ─── Event CRUD ───
    addEvent: (
        title: string,
        type: EventType,
        startTime: Date,
        action: EventAction,
        options?: {
            description?: string;
            endTime?: Date;
            recurrence?: RecurrenceType;
            cronExpression?: string;
            tags?: string[];
            color?: string;
            maxRuns?: number;
        },
    ) => string;

    updateEvent: (eventId: string, updates: Partial<ScheduledEvent>) => void;
    deleteEvent: (eventId: string) => void;
    cancelEvent: (eventId: string) => void;
    pauseEvent: (eventId: string) => void;
    resumeEvent: (eventId: string) => void;

    // ─── Macro CRUD ───
    addMacro: (macro: AutomationMacro) => void;
    updateMacro: (macroId: string, updates: Partial<AutomationMacro>) => void;
    deleteMacro: (macroId: string) => void;
    setRunningMacro: (execution: MacroExecution | null) => void;

    // ─── View ───
    setView: (view: CalendarView) => void;
    setSelectedDate: (date: string) => void;
    navigateMonth: (delta: number) => void;

    // ─── Scheduler ───
    initializeScheduler: () => void;
    stopScheduler: () => void;
}

// ─── Store ───

const now = new Date();

export const useCalendarStore = create<CalendarStoreState>()(
    (persist as any)(
        (set: any, get: any) => ({
            events: {},
            macros: Object.fromEntries(BUILT_IN_MACROS.map(m => [m.id, m])),
            runningMacro: null,

            view: 'month' as CalendarView,
            selectedDate: now.toISOString().slice(0, 10),
            viewMonth: now.getMonth(),
            viewYear: now.getFullYear(),

            // ─── Event CRUD ───

            addEvent: (
                title: string,
                type: EventType,
                startTime: Date,
                action: EventAction,
                options?: any,
            ): string => {
                const event = createScheduledEvent(title, type, startTime, action, options);
                set((state: CalendarStoreState) => ({
                    events: { ...state.events, [event.id]: event },
                }));
                // Auto-schedule
                scheduleTimerEvent(event);
                return event.id;
            },

            updateEvent: (eventId: string, updates: Partial<ScheduledEvent>) => {
                const events = { ...get().events };
                if (events[eventId]) {
                    events[eventId] = { ...events[eventId], ...updates, updatedAt: new Date().toISOString() };

                    // Recalculate next run if schedule-related fields changed
                    if (updates.recurrence || updates.cronExpression || updates.startTime) {
                        const nextRun = calculateNextRun(events[eventId]);
                        events[eventId].nextRun = nextRun?.toISOString();
                    }

                    set({ events });
                }
            },

            deleteEvent: (eventId: string) => {
                cancelTimer(eventId);
                set((state: CalendarStoreState) => {
                    const events = { ...state.events };
                    delete events[eventId];
                    return { events };
                });
            },

            cancelEvent: (eventId: string) => {
                cancelTimer(eventId);
                get().updateEvent(eventId, { status: 'cancelled' });
            },

            pauseEvent: (eventId: string) => {
                cancelTimer(eventId);
                get().updateEvent(eventId, { status: 'paused' });
            },

            resumeEvent: (eventId: string) => {
                const event = get().events[eventId];
                if (event) {
                    const nextRun = calculateNextRun(event);
                    get().updateEvent(eventId, {
                        status: 'scheduled',
                        nextRun: nextRun?.toISOString(),
                    });
                    if (nextRun) {
                        scheduleTimerEvent({ ...event, status: 'scheduled', nextRun: nextRun.toISOString() });
                    }
                }
            },

            // ─── Macro CRUD ───

            addMacro: (macro: AutomationMacro) => {
                set((state: CalendarStoreState) => ({
                    macros: { ...state.macros, [macro.id]: macro },
                }));
            },

            updateMacro: (macroId: string, updates: Partial<AutomationMacro>) => {
                const macros = { ...get().macros };
                if (macros[macroId]) {
                    macros[macroId] = { ...macros[macroId], ...updates, updatedAt: new Date().toISOString() };
                    set({ macros });
                }
            },

            deleteMacro: (macroId: string) => {
                set((state: CalendarStoreState) => {
                    const macros = { ...state.macros };
                    delete macros[macroId];
                    return { macros };
                });
            },

            setRunningMacro: (execution: MacroExecution | null) => {
                set({ runningMacro: execution });
            },

            // ─── View ───

            setView: (view: CalendarView) => set({ view }),
            setSelectedDate: (date: string) => set({ selectedDate: date }),

            navigateMonth: (delta: number) => {
                const { viewMonth, viewYear } = get();
                let newMonth = viewMonth + delta;
                let newYear = viewYear;
                if (newMonth < 0) { newMonth = 11; newYear--; }
                if (newMonth > 11) { newMonth = 0; newYear++; }
                set({ viewMonth: newMonth, viewYear: newYear });
            },

            // ─── Scheduler ───

            initializeScheduler: () => {
                const events = Object.values(get().events) as ScheduledEvent[];
                for (const event of events) {
                    if (event.status === 'scheduled') {
                        scheduleTimerEvent(event);
                    }
                }
            },

            stopScheduler: () => {
                stopAllTimers();
            },
        }),
        {
            name: 'aim-os-calendar',
            storage: createJSONStorage(() => encryptedStorage as any),
            partialize: (state: any) => ({
                events: state.events,
                macros: state.macros,
                viewMonth: state.viewMonth,
                viewYear: state.viewYear,
            }),
        },
    ),
);
