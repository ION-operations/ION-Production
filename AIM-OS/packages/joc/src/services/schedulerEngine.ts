/**
 * Scheduler Engine — Cron-like event scheduling for AIM-OS
 *
 * Manages timed events with recurrence support.
 * Uses setTimeout-based scheduling with automatic rescheduling for recurring events.
 */

// ─── Types ───

export type EventType = 'mission' | 'macro' | 'reminder' | 'maintenance' | 'checkpoint' | 'custom';
export type RecurrenceType = 'once' | 'daily' | 'weekly' | 'monthly' | 'cron';
export type EventStatus = 'scheduled' | 'running' | 'completed' | 'failed' | 'cancelled' | 'paused';

export type ActionType =
    | 'launch_mission'
    | 'run_macro'
    | 'vault_reset'
    | 'health_check'
    | 'auto_rotate'
    | 'notify'
    | 'custom_script';

export interface EventAction {
    type: ActionType;
    payload?: Record<string, any>;
}

export interface ScheduledEvent {
    id: string;
    title: string;
    description?: string;
    type: EventType;
    startTime: string;           // ISO timestamp
    endTime?: string;            // ISO timestamp (optional end time)
    recurrence: RecurrenceType;
    cronExpression?: string;     // e.g., "0 8 * * *" for daily 8am
    action: EventAction;
    status: EventStatus;
    tags: string[];
    color?: string;              // UI display color
    lastRun?: string;            // ISO timestamp
    nextRun?: string;            // ISO timestamp
    runCount: number;
    maxRuns?: number;            // Stop after N runs (undefined = unlimited)
    createdAt: string;
    updatedAt: string;
}

// ─── Cron Parser (simplified) ───

interface CronFields {
    minute: number[];
    hour: number[];
    dayOfMonth: number[];
    month: number[];
    dayOfWeek: number[];
}

function parseCronField(field: string, min: number, max: number): number[] {
    if (field === '*') return Array.from({ length: max - min + 1 }, (_, i) => i + min);

    const values: number[] = [];
    for (const part of field.split(',')) {
        if (part.includes('/')) {
            const [range, step] = part.split('/');
            const stepNum = parseInt(step);
            const start = range === '*' ? min : parseInt(range);
            for (let i = start; i <= max; i += stepNum) values.push(i);
        } else if (part.includes('-')) {
            const [a, b] = part.split('-').map(Number);
            for (let i = a; i <= b; i++) values.push(i);
        } else {
            values.push(parseInt(part));
        }
    }
    return values.filter(v => v >= min && v <= max);
}

function parseCron(expression: string): CronFields | null {
    const parts = expression.trim().split(/\s+/);
    if (parts.length !== 5) return null;

    return {
        minute: parseCronField(parts[0], 0, 59),
        hour: parseCronField(parts[1], 0, 23),
        dayOfMonth: parseCronField(parts[2], 1, 31),
        month: parseCronField(parts[3], 1, 12),
        dayOfWeek: parseCronField(parts[4], 0, 6),
    };
}

/**
 * Get the next occurrence from a cron expression after a given date.
 */
export function getNextCronTime(expression: string, after: Date = new Date()): Date | null {
    const fields = parseCron(expression);
    if (!fields) return null;

    const candidate = new Date(after);
    candidate.setSeconds(0, 0);
    candidate.setMinutes(candidate.getMinutes() + 1); // Start from next minute

    // Search up to 366 days ahead
    for (let i = 0; i < 527040; i++) { // 366 * 24 * 60
        const m = candidate.getMinutes();
        const h = candidate.getHours();
        const dom = candidate.getDate();
        const mon = candidate.getMonth() + 1;
        const dow = candidate.getDay();

        if (
            fields.minute.includes(m) &&
            fields.hour.includes(h) &&
            fields.dayOfMonth.includes(dom) &&
            fields.month.includes(mon) &&
            fields.dayOfWeek.includes(dow)
        ) {
            return candidate;
        }

        candidate.setMinutes(candidate.getMinutes() + 1);
    }

    return null;
}

// ─── Next Run Calculator ───

export function calculateNextRun(event: ScheduledEvent, afterDate: Date = new Date()): Date | null {
    switch (event.recurrence) {
        case 'once': {
            const t = new Date(event.startTime);
            return t > afterDate ? t : null;
        }
        case 'daily': {
            const base = new Date(event.startTime);
            const next = new Date(afterDate);
            next.setHours(base.getHours(), base.getMinutes(), base.getSeconds(), 0);
            if (next <= afterDate) next.setDate(next.getDate() + 1);
            return next;
        }
        case 'weekly': {
            const base = new Date(event.startTime);
            const targetDay = base.getDay();
            const next = new Date(afterDate);
            next.setHours(base.getHours(), base.getMinutes(), base.getSeconds(), 0);
            const diff = (targetDay - next.getDay() + 7) % 7 || 7;
            if (next <= afterDate || next.getDay() !== targetDay) {
                next.setDate(next.getDate() + (next.getDay() === targetDay && next > afterDate ? 0 : diff));
            }
            return next;
        }
        case 'monthly': {
            const base = new Date(event.startTime);
            const next = new Date(afterDate);
            next.setDate(base.getDate());
            next.setHours(base.getHours(), base.getMinutes(), base.getSeconds(), 0);
            if (next <= afterDate) next.setMonth(next.getMonth() + 1);
            return next;
        }
        case 'cron': {
            if (!event.cronExpression) return null;
            return getNextCronTime(event.cronExpression, afterDate);
        }
        default:
            return null;
    }
}

// ─── Event Creation Helper ───

export function createScheduledEvent(
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
): ScheduledEvent {
    const now = new Date().toISOString();
    const event: ScheduledEvent = {
        id: `evt-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
        title,
        description: options?.description,
        type,
        startTime: startTime.toISOString(),
        endTime: options?.endTime?.toISOString(),
        recurrence: options?.recurrence || 'once',
        cronExpression: options?.cronExpression,
        action,
        status: 'scheduled',
        tags: options?.tags || [],
        color: options?.color,
        runCount: 0,
        maxRuns: options?.maxRuns,
        createdAt: now,
        updatedAt: now,
    };

    // Calculate next run
    const nextRun = calculateNextRun(event);
    if (nextRun) event.nextRun = nextRun.toISOString();

    return event;
}

// ─── Scheduler Runtime ───

const _timers: Map<string, ReturnType<typeof setTimeout>> = new Map();
let _actionHandler: ((event: ScheduledEvent) => Promise<void>) | null = null;
let _onEventUpdate: ((eventId: string, updates: Partial<ScheduledEvent>) => void) | null = null;

/**
 * Register the action handler and event update callback.
 */
export function registerHandlers(
    actionHandler: (event: ScheduledEvent) => Promise<void>,
    onEventUpdate: (eventId: string, updates: Partial<ScheduledEvent>) => void,
): void {
    _actionHandler = actionHandler;
    _onEventUpdate = onEventUpdate;
}

/**
 * Schedule an event for execution.
 */
export function scheduleEvent(event: ScheduledEvent): void {
    // Cancel existing timer if any
    cancelTimer(event.id);

    if (event.status === 'cancelled' || event.status === 'paused') return;
    if (event.maxRuns && event.runCount >= event.maxRuns) return;

    const nextRun = event.nextRun ? new Date(event.nextRun) : calculateNextRun(event);
    if (!nextRun) return;

    const delayMs = nextRun.getTime() - Date.now();
    if (delayMs < 0) return; // Past event

    // Cap setTimeout to ~24 days (max safe integer for setTimeout)
    const safeDelay = Math.min(delayMs, 2_000_000_000);

    const timer = setTimeout(async () => {
        _timers.delete(event.id);

        if (!_actionHandler) return;

        // Update status
        _onEventUpdate?.(event.id, { status: 'running' });

        try {
            await _actionHandler(event);
            const now = new Date().toISOString();
            const newRunCount = event.runCount + 1;

            // Calculate next run for recurring events
            const updatedEvent = { ...event, runCount: newRunCount, lastRun: now };
            const nextNextRun = calculateNextRun(updatedEvent, new Date());

            _onEventUpdate?.(event.id, {
                status: nextNextRun ? 'scheduled' : 'completed',
                lastRun: now,
                runCount: newRunCount,
                nextRun: nextNextRun?.toISOString(),
                updatedAt: now,
            });

            // Re-schedule if recurring
            if (nextNextRun && (!event.maxRuns || newRunCount < event.maxRuns)) {
                scheduleEvent({ ...updatedEvent, nextRun: nextNextRun.toISOString(), status: 'scheduled' });
            }
        } catch (err: any) {
            _onEventUpdate?.(event.id, {
                status: 'failed',
                updatedAt: new Date().toISOString(),
            });
        }
    }, safeDelay);

    _timers.set(event.id, timer);
}

/**
 * Cancel a scheduled event timer.
 */
export function cancelTimer(eventId: string): void {
    const timer = _timers.get(eventId);
    if (timer) {
        clearTimeout(timer);
        _timers.delete(eventId);
    }
}

/**
 * Stop all scheduled timers.
 */
export function stopAllTimers(): void {
    for (const [id, timer] of _timers) {
        clearTimeout(timer);
    }
    _timers.clear();
}

/**
 * Get upcoming events within the next N hours.
 */
export function getUpcomingEvents(events: ScheduledEvent[], hours: number = 24): ScheduledEvent[] {
    const cutoff = new Date(Date.now() + hours * 3600_000);
    return events
        .filter(e => {
            if (e.status === 'cancelled') return false;
            const next = e.nextRun ? new Date(e.nextRun) : null;
            return next && next <= cutoff;
        })
        .sort((a, b) => {
            const aTime = a.nextRun ? new Date(a.nextRun).getTime() : Infinity;
            const bTime = b.nextRun ? new Date(b.nextRun).getTime() : Infinity;
            return aTime - bTime;
        });
}

/**
 * Get events for a specific date.
 */
export function getEventsForDate(events: ScheduledEvent[], date: Date): ScheduledEvent[] {
    const dayStart = new Date(date);
    dayStart.setHours(0, 0, 0, 0);
    const dayEnd = new Date(date);
    dayEnd.setHours(23, 59, 59, 999);

    return events.filter(e => {
        const start = new Date(e.startTime);
        // For recurring events, check if they run on this date
        if (e.recurrence !== 'once') {
            const nextRun = calculateNextRun(e, dayStart);
            return nextRun && nextRun <= dayEnd;
        }
        return start >= dayStart && start <= dayEnd;
    });
}
