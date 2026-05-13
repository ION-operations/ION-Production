import { useState, useMemo, useCallback } from 'react';
import { useCalendarStore, type CalendarView } from '../store/calendarStore';
import {
    type ScheduledEvent,
    type EventType,
    type RecurrenceType,
    type ActionType,
    getEventsForDate,
    getUpcomingEvents,
} from '../services/schedulerEngine';
import {
    type AutomationMacro,
    executeMacro,
    type MacroStep,
} from '../services/automationMacros';

// ─── Constants ───

const MONTH_NAMES = ['January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'];
const DAY_NAMES = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

const eventTypeConfig: Record<EventType, { icon: string; color: string }> = {
    mission: { icon: '🚀', color: '#4ecdc4' },
    macro: { icon: '🔁', color: '#a78bfa' },
    reminder: { icon: '🔔', color: '#ffd93d' },
    maintenance: { icon: '🔧', color: '#f97316' },
    checkpoint: { icon: '📍', color: '#60a5fa' },
    custom: { icon: '📌', color: '#888' },
};

const actionOptions: { value: ActionType; label: string }[] = [
    { value: 'launch_mission', label: '🚀 Launch Mission' },
    { value: 'run_macro', label: '🔁 Run Macro' },
    { value: 'health_check', label: '🏥 Health Check' },
    { value: 'auto_rotate', label: '🔄 Auto-Rotate Sessions' },
    { value: 'vault_reset', label: '📊 Reset Vault Stats' },
    { value: 'notify', label: '🔔 Notification' },
    { value: 'custom_script', label: '⚙️ Custom Script' },
];

// ─── Add Event Dialog ───

function AddEventDialog({ onClose, initialDate }: { onClose: () => void; initialDate?: string }) {
    const { addEvent } = useCalendarStore();
    const [title, setTitle] = useState('');
    const [type, setType] = useState<EventType>('mission');
    const [date, setDate] = useState(initialDate || new Date().toISOString().slice(0, 10));
    const [time, setTime] = useState('09:00');
    const [recurrence, setRecurrence] = useState<RecurrenceType>('once');
    const [cronExpr, setCronExpr] = useState('');
    const [actionType, setActionType] = useState<ActionType>('launch_mission');
    const [description, setDescription] = useState('');
    const [color, setColor] = useState('#4ecdc4');

    const handleSave = () => {
        if (!title.trim()) return;
        const startTime = new Date(`${date}T${time}:00`);

        addEvent(title, type, startTime, { type: actionType }, {
            description: description || undefined,
            recurrence,
            cronExpression: recurrence === 'cron' ? cronExpr : undefined,
            color,
        });
        onClose();
    };

    return (
        <div style={sty.dialogOverlay} onClick={onClose}>
            <div style={sty.dialog} onClick={e => e.stopPropagation()}>
                <div style={sty.dialogHeader}>
                    <span style={{ fontSize: 16, fontWeight: 600 }}>📅 New Event</span>
                    <button style={sty.dialogClose} onClick={onClose}>✕</button>
                </div>
                <div style={sty.dialogBody}>
                    <label style={sty.fieldLabel}>Title *</label>
                    <input style={sty.input} value={title} onChange={e => setTitle(e.target.value)}
                        placeholder="e.g., Daily Research Dispatch" />

                    <div style={{ display: 'flex', gap: 12 }}>
                        <div style={{ flex: 1 }}>
                            <label style={sty.fieldLabel}>Type</label>
                            <select style={sty.select} value={type}
                                onChange={e => setType(e.target.value as EventType)}>
                                {Object.entries(eventTypeConfig).map(([k, v]) => (
                                    <option key={k} value={k}>{v.icon} {k}</option>
                                ))}
                            </select>
                        </div>
                        <div style={{ flex: 1 }}>
                            <label style={sty.fieldLabel}>Action</label>
                            <select style={sty.select} value={actionType}
                                onChange={e => setActionType(e.target.value as ActionType)}>
                                {actionOptions.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                            </select>
                        </div>
                    </div>

                    <div style={{ display: 'flex', gap: 12 }}>
                        <div style={{ flex: 1 }}>
                            <label style={sty.fieldLabel}>Date</label>
                            <input style={sty.input} type="date" value={date}
                                onChange={e => setDate(e.target.value)} />
                        </div>
                        <div style={{ flex: 1 }}>
                            <label style={sty.fieldLabel}>Time</label>
                            <input style={sty.input} type="time" value={time}
                                onChange={e => setTime(e.target.value)} />
                        </div>
                    </div>

                    <label style={sty.fieldLabel}>Recurrence</label>
                    <select style={sty.select} value={recurrence}
                        onChange={e => setRecurrence(e.target.value as RecurrenceType)}>
                        <option value="once">Once</option>
                        <option value="daily">Daily</option>
                        <option value="weekly">Weekly</option>
                        <option value="monthly">Monthly</option>
                        <option value="cron">Cron Expression</option>
                    </select>

                    {recurrence === 'cron' && (
                        <>
                            <label style={sty.fieldLabel}>Cron Expression</label>
                            <input style={sty.input} value={cronExpr} onChange={e => setCronExpr(e.target.value)}
                                placeholder="e.g., 0 8 * * 1-5 (weekdays at 8am)" />
                        </>
                    )}

                    <label style={sty.fieldLabel}>Description</label>
                    <input style={sty.input} value={description} onChange={e => setDescription(e.target.value)}
                        placeholder="Optional details" />

                    <label style={sty.fieldLabel}>Color</label>
                    <div style={{ display: 'flex', gap: 8, marginTop: 4 }}>
                        {['#4ecdc4', '#a78bfa', '#ffd93d', '#f97316', '#60a5fa', '#ff6b6b', '#34d399', '#888'].map(c => (
                            <button key={c} onClick={() => setColor(c)}
                                style={{
                                    width: 28, height: 28, borderRadius: '50%', background: c, border: color === c ? '2px solid #fff' : '2px solid transparent',
                                    cursor: 'pointer', transition: 'border-color 0.2s',
                                }} />
                        ))}
                    </div>
                </div>
                <div style={sty.dialogFooter}>
                    <button style={sty.cancelBtn} onClick={onClose}>Cancel</button>
                    <button style={sty.saveBtn} onClick={handleSave} disabled={!title.trim()}>
                        Create Event
                    </button>
                </div>
            </div>
        </div>
    );
}

// ─── Month Grid ───

function MonthGrid({ events, selectedDate, onSelectDate }: {
    events: ScheduledEvent[];
    selectedDate: string;
    onSelectDate: (date: string) => void;
}) {
    const { viewMonth, viewYear } = useCalendarStore();

    const cells = useMemo(() => {
        const firstDay = new Date(viewYear, viewMonth, 1);
        const lastDay = new Date(viewYear, viewMonth + 1, 0);
        const startDow = (firstDay.getDay() + 6) % 7; // Monday=0

        const result: { date: Date; isCurrentMonth: boolean }[] = [];

        // Previous month padding
        for (let i = startDow - 1; i >= 0; i--) {
            const d = new Date(viewYear, viewMonth, -i);
            result.push({ date: d, isCurrentMonth: false });
        }

        // Current month
        for (let i = 1; i <= lastDay.getDate(); i++) {
            result.push({ date: new Date(viewYear, viewMonth, i), isCurrentMonth: true });
        }

        // Next month padding
        while (result.length % 7 !== 0) {
            const last = result[result.length - 1].date;
            const next = new Date(last);
            next.setDate(next.getDate() + 1);
            result.push({ date: next, isCurrentMonth: false });
        }

        return result;
    }, [viewMonth, viewYear]);

    const today = new Date().toISOString().slice(0, 10);

    return (
        <div>
            <div style={sty.gridHeader}>
                {DAY_NAMES.map(d => <div key={d} style={sty.gridDayName}>{d}</div>)}
            </div>
            <div style={sty.grid}>
                {cells.map((cell, i) => {
                    const dateStr = cell.date.toISOString().slice(0, 10);
                    const dayEvents = getEventsForDate(events, cell.date);
                    const isToday = dateStr === today;
                    const isSelected = dateStr === selectedDate;

                    return (
                        <div key={i}
                            onClick={() => onSelectDate(dateStr)}
                            style={{
                                ...sty.gridCell,
                                opacity: cell.isCurrentMonth ? 1 : 0.3,
                                background: isSelected ? 'rgba(78, 205, 196, 0.08)' : isToday ? 'rgba(255, 255, 255, 0.03)' : 'transparent',
                                borderColor: isSelected ? 'rgba(78, 205, 196, 0.3)' : 'rgba(255,255,255,0.04)',
                            }}>
                            <span style={{
                                ...sty.gridDayNum,
                                color: isToday ? '#4ecdc4' : '#aaa',
                                fontWeight: isToday ? 700 : 400,
                            }}>
                                {cell.date.getDate()}
                            </span>
                            <div style={sty.gridDots}>
                                {dayEvents.slice(0, 3).map((evt, j) => (
                                    <span key={j} style={{
                                        ...sty.eventDot,
                                        background: evt.color || eventTypeConfig[evt.type]?.color || '#888',
                                    }} title={evt.title} />
                                ))}
                                {dayEvents.length > 3 && (
                                    <span style={{ fontSize: 9, color: '#666' }}>+{dayEvents.length - 3}</span>
                                )}
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}

// ─── Upcoming Rail ───

function UpcomingRail({ events }: { events: ScheduledEvent[] }) {
    const upcoming = useMemo(() => getUpcomingEvents(events, 24), [events]);

    if (upcoming.length === 0) {
        return (
            <div style={sty.railSection}>
                <div style={sty.railTitle}>⏱ Upcoming (24h)</div>
                <div style={{ fontSize: 12, color: '#666', padding: '12px 0' }}>No events in the next 24 hours</div>
            </div>
        );
    }

    return (
        <div style={sty.railSection}>
            <div style={sty.railTitle}>⏱ Upcoming (24h)</div>
            {upcoming.map(evt => {
                const cfg = eventTypeConfig[evt.type];
                const time = evt.nextRun ? new Date(evt.nextRun).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false }) : '—';
                return (
                    <div key={evt.id} style={sty.railItem}>
                        <span style={{ ...sty.railDot, background: evt.color || cfg.color }} />
                        <span style={sty.railTime}>{time}</span>
                        <span style={sty.railEventTitle}>{cfg.icon} {evt.title}</span>
                        {evt.recurrence !== 'once' && (
                            <span style={sty.railBadge}>{evt.recurrence}</span>
                        )}
                    </div>
                );
            })}
        </div>
    );
}

// ─── Macro Panel ───

function MacroPanel() {
    const { macros, setRunningMacro, updateMacro } = useCalendarStore();
    const macroList = Object.values(macros) as AutomationMacro[];
    const [runningId, setRunningId] = useState<string | null>(null);

    const handleRun = useCallback(async (macro: AutomationMacro) => {
        setRunningId(macro.id);

        await executeMacro(
            macro,
            async (s: MacroStep, _ctx: any) => {
                // Placeholder handler — logs step execution
                console.log(`[Macro ${macro.name}] Executing step: ${s.name} (${s.type})`);
            },
            (execution) => {
                setRunningMacro(execution);
            },
        );

        updateMacro(macro.id, {
            lastRun: new Date().toISOString(),
            runCount: macro.runCount + 1,
        });

        setRunningId(null);
        setRunningMacro(null);
    }, [setRunningMacro, updateMacro]);

    return (
        <div style={sty.railSection}>
            <div style={sty.railTitle}>🔁 Automation Macros</div>
            {macroList.map(macro => (
                <div key={macro.id} style={sty.macroItem}>
                    <span style={{ fontSize: 18 }}>{macro.icon}</span>
                    <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ fontSize: 13, fontWeight: 600, color: '#e0e0e0' }}>{macro.name}</div>
                        <div style={{ fontSize: 11, color: '#888', marginTop: 2 }}>
                            {macro.trigger === 'scheduled' ? `⏰ scheduled` : macro.trigger}
                            {macro.lastRun && ` · last: ${new Date(macro.lastRun).toLocaleDateString()}`}
                        </div>
                    </div>
                    <button
                        style={{
                            ...sty.runBtn,
                            opacity: runningId === macro.id ? 0.5 : 1,
                        }}
                        onClick={() => handleRun(macro)}
                        disabled={runningId === macro.id}
                    >
                        {runningId === macro.id ? '⏳' : '▶'} {runningId === macro.id ? 'Running' : 'Run'}
                    </button>
                </div>
            ))}
        </div>
    );
}

// ─── Selected Day Events ───

function DayEvents({ events, date }: { events: ScheduledEvent[]; date: string }) {
    const { deleteEvent, cancelEvent } = useCalendarStore();
    const dayEvents = useMemo(() => getEventsForDate(events, new Date(date)), [events, date]);

    const dateLabel = new Date(date + 'T00:00:00').toLocaleDateString('en-US', {
        weekday: 'long', month: 'long', day: 'numeric',
    });

    return (
        <div style={sty.railSection}>
            <div style={sty.railTitle}>📋 {dateLabel}</div>
            {dayEvents.length === 0 ? (
                <div style={{ fontSize: 12, color: '#666', padding: '12px 0' }}>No events on this day</div>
            ) : (
                dayEvents.map(evt => {
                    const cfg = eventTypeConfig[evt.type];
                    const time = new Date(evt.startTime).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false });
                    return (
                        <div key={evt.id} style={sty.dayEventItem}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                <span style={{ ...sty.railDot, background: evt.color || cfg.color }} />
                                <span style={{ fontSize: 12, color: '#888', fontVariantNumeric: 'tabular-nums' }}>{time}</span>
                                <span style={{ fontSize: 13, color: '#e0e0e0', fontWeight: 500 }}>{cfg.icon} {evt.title}</span>
                            </div>
                            <div style={{ display: 'flex', gap: 4 }}>
                                {evt.status !== 'cancelled' && (
                                    <button style={sty.smallBtn} onClick={() => cancelEvent(evt.id)}>✕</button>
                                )}
                                <button style={{ ...sty.smallBtn, color: '#ff6b6b' }} onClick={() => deleteEvent(evt.id)}>🗑</button>
                            </div>
                        </div>
                    );
                })
            )}
        </div>
    );
}

// ─── Week View ───

const HOURS = Array.from({ length: 24 }, (_, i) => i);
const WEEK_DAY_FULL = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

function WeekView({ events, selectedDate, onSelectDate }: {
    events: ScheduledEvent[];
    selectedDate: string;
    onSelectDate: (date: string) => void;
}) {
    const weekDays = useMemo(() => {
        const sel = new Date(selectedDate + 'T00:00:00');
        const dayOfWeek = (sel.getDay() + 6) % 7; // Monday=0
        const monday = new Date(sel);
        monday.setDate(monday.getDate() - dayOfWeek);
        return Array.from({ length: 7 }, (_, i) => {
            const d = new Date(monday);
            d.setDate(d.getDate() + i);
            return d;
        });
    }, [selectedDate]);

    const today = new Date().toISOString().slice(0, 10);

    return (
        <div style={{ overflowX: 'auto' as const }}>
            {/* Day headers */}
            <div style={{ display: 'grid', gridTemplateColumns: '56px repeat(7, 1fr)', gap: 0 }}>
                <div style={{ ...ws.timeGutter, borderBottom: '1px solid rgba(255,255,255,0.06)' }} />
                {weekDays.map((d, i) => {
                    const ds = d.toISOString().slice(0, 10);
                    const isToday = ds === today;
                    const isSel = ds === selectedDate;
                    return (
                        <div key={i} onClick={() => onSelectDate(ds)} style={{
                            ...ws.dayHeader,
                            background: isSel ? 'rgba(78, 205, 196, 0.06)' : 'transparent',
                            cursor: 'pointer',
                        }}>
                            <span style={{ fontSize: 10, color: '#666', textTransform: 'uppercase' as const }}>{WEEK_DAY_FULL[i].slice(0, 3)}</span>
                            <span style={{
                                fontSize: 18, fontWeight: isToday ? 700 : 500,
                                color: isToday ? '#4ecdc4' : isSel ? '#e0e0e0' : '#aaa',
                                background: isToday ? 'rgba(78,205,196,0.15)' : 'transparent',
                                borderRadius: '50%', width: 32, height: 32,
                                display: 'flex', alignItems: 'center', justifyContent: 'center',
                            }}>
                                {d.getDate()}
                            </span>
                        </div>
                    );
                })}
            </div>

            {/* Hourly grid */}
            <div style={{ maxHeight: 600, overflowY: 'auto' as const }}>
                {HOURS.map(hour => (
                    <div key={hour} style={{ display: 'grid', gridTemplateColumns: '56px repeat(7, 1fr)', gap: 0, minHeight: 48 }}>
                        <div style={ws.timeLabel}>
                            {hour.toString().padStart(2, '0')}:00
                        </div>
                        {weekDays.map((d, di) => {
                            const dayEvents = getEventsForDate(events, d).filter(e => {
                                const h = new Date(e.startTime).getHours();
                                return h === hour;
                            });
                            return (
                                <div key={di} style={ws.hourCell}>
                                    {dayEvents.map(evt => {
                                        const cfg = eventTypeConfig[evt.type];
                                        return (
                                            <div key={evt.id} style={{
                                                ...ws.weekEvent,
                                                background: `${evt.color || cfg.color}20`,
                                                borderLeft: `3px solid ${evt.color || cfg.color}`,
                                            }}>
                                                <span style={{ fontSize: 10 }}>{cfg.icon}</span>
                                                <span style={{ fontSize: 10, color: '#e0e0e0', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' as const }}>{evt.title}</span>
                                            </div>
                                        );
                                    })}
                                </div>
                            );
                        })}
                    </div>
                ))}
            </div>
        </div>
    );
}

// ─── Day View ───

function DayView({ events, date }: { events: ScheduledEvent[]; date: string }) {
    const dayEvents = useMemo(() => getEventsForDate(events, new Date(date)), [events, date]);

    const dateLabel = new Date(date + 'T00:00:00').toLocaleDateString('en-US', {
        weekday: 'long', month: 'long', day: 'numeric', year: 'numeric',
    });

    const now = new Date();
    const isToday = date === now.toISOString().slice(0, 10);
    const currentHour = now.getHours();
    const currentMinute = now.getMinutes();

    return (
        <div>
            <div style={{ fontSize: 15, fontWeight: 600, color: '#e0e0e0', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
                📋 {dateLabel}
                {isToday && <span style={{ fontSize: 10, color: '#4ecdc4', background: 'rgba(78,205,196,0.1)', padding: '2px 8px', borderRadius: 4 }}>Today</span>}
            </div>

            <div style={{ maxHeight: 600, overflowY: 'auto' as const }}>
                {HOURS.map(hour => {
                    const hourEvents = dayEvents.filter(e => new Date(e.startTime).getHours() === hour);
                    const isCurrentHour = isToday && hour === currentHour;

                    return (
                        <div key={hour} style={{
                            display: 'flex', gap: 0, minHeight: 56,
                            borderBottom: '1px solid rgba(255,255,255,0.04)',
                            position: 'relative' as const,
                        }}>
                            {/* Time label */}
                            <div style={{
                                ...ds.timeLabel,
                                color: isCurrentHour ? '#4ecdc4' : '#666',
                                fontWeight: isCurrentHour ? 600 : 400,
                            }}>
                                {hour.toString().padStart(2, '0')}:00
                            </div>

                            {/* Event area */}
                            <div style={ds.eventArea}>
                                {hourEvents.map(evt => {
                                    const cfg = eventTypeConfig[evt.type];
                                    const minutes = new Date(evt.startTime).getMinutes();
                                    return (
                                        <div key={evt.id} style={{
                                            ...ds.dayEvent,
                                            background: `${evt.color || cfg.color}15`,
                                            borderLeft: `3px solid ${evt.color || cfg.color}`,
                                        }}>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                                                <span>{cfg.icon}</span>
                                                <span style={{ fontWeight: 600, fontSize: 13, color: '#e0e0e0' }}>{evt.title}</span>
                                                <span style={{ fontSize: 11, color: '#888' }}>
                                                    {hour.toString().padStart(2, '0')}:{minutes.toString().padStart(2, '0')}
                                                </span>
                                            </div>
                                            {evt.description && (
                                                <div style={{ fontSize: 11, color: '#888', marginTop: 2 }}>{evt.description}</div>
                                            )}
                                            <div style={{ display: 'flex', gap: 6, marginTop: 4 }}>
                                                {evt.recurrence !== 'once' && (
                                                    <span style={{ fontSize: 9, color: '#a78bfa', background: 'rgba(167,139,250,0.1)', padding: '1px 6px', borderRadius: 3 }}>
                                                        {evt.recurrence}
                                                    </span>
                                                )}
                                                <span style={{ fontSize: 9, color: '#888', background: 'rgba(255,255,255,0.04)', padding: '1px 6px', borderRadius: 3 }}>
                                                    {evt.action.type.replace(/_/g, ' ')}
                                                </span>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>

                            {/* Current time indicator */}
                            {isCurrentHour && (
                                <div style={{
                                    position: 'absolute' as const,
                                    top: `${(currentMinute / 60) * 100}%`,
                                    left: 56, right: 0,
                                    height: 2, background: '#ff6b6b',
                                    zIndex: 2,
                                }}>
                                    <div style={{
                                        position: 'absolute' as const, left: -4, top: -3,
                                        width: 8, height: 8, borderRadius: '50%', background: '#ff6b6b',
                                    }} />
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
}

// ─── Main Page ───

export function CalendarPage() {
    const {
        events, viewMonth, viewYear, selectedDate, view,
        setView, setSelectedDate, navigateMonth,
    } = useCalendarStore();
    const [showAddDialog, setShowAddDialog] = useState(false);

    const eventsList = Object.values(events) as ScheduledEvent[];

    // Navigation helpers for week/day views
    const navigateWeek = useCallback((delta: number) => {
        const d = new Date(selectedDate + 'T00:00:00');
        d.setDate(d.getDate() + delta * 7);
        setSelectedDate(d.toISOString().slice(0, 10));
        // Sync month if needed
        if (d.getMonth() !== viewMonth || d.getFullYear() !== viewYear) {
            navigateMonth(delta > 0 ? 1 : -1);
        }
    }, [selectedDate, setSelectedDate, viewMonth, viewYear, navigateMonth]);

    const navigateDay = useCallback((delta: number) => {
        const d = new Date(selectedDate + 'T00:00:00');
        d.setDate(d.getDate() + delta);
        setSelectedDate(d.toISOString().slice(0, 10));
    }, [selectedDate, setSelectedDate]);

    // Get nav label based on view
    const navLabel = useMemo(() => {
        if (view === 'month') return `${MONTH_NAMES[viewMonth]} ${viewYear}`;
        if (view === 'week') {
            const sel = new Date(selectedDate + 'T00:00:00');
            const dayOfWeek = (sel.getDay() + 6) % 7;
            const monday = new Date(sel);
            monday.setDate(monday.getDate() - dayOfWeek);
            const sunday = new Date(monday);
            sunday.setDate(sunday.getDate() + 6);
            const mStr = monday.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            const sStr = sunday.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            return `${mStr} – ${sStr}, ${monday.getFullYear()}`;
        }
        return new Date(selectedDate + 'T00:00:00').toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' });
    }, [view, viewMonth, viewYear, selectedDate]);

    const handleNavPrev = () => {
        if (view === 'month') navigateMonth(-1);
        else if (view === 'week') navigateWeek(-1);
        else navigateDay(-1);
    };
    const handleNavNext = () => {
        if (view === 'month') navigateMonth(1);
        else if (view === 'week') navigateWeek(1);
        else navigateDay(1);
    };

    return (
        <div style={sty.page}>
            {/* ─── Header ─── */}
            <div style={sty.header}>
                <div>
                    <div style={sty.title}>📅 AIM-OS Calendar</div>
                    <div style={sty.subtitle}>
                        {eventsList.length} event{eventsList.length !== 1 ? 's' : ''} · Timed AI ops & automation scheduling
                    </div>
                </div>
                <button style={sty.addBtn} onClick={() => setShowAddDialog(true)}>
                    + Add Event
                </button>
            </div>

            {/* ─── Navigation ─── */}
            <div style={sty.nav}>
                <div style={sty.navLeft}>
                    <button style={sty.navArrow} onClick={handleNavPrev}>◀</button>
                    <span style={sty.navMonth}>{navLabel}</span>
                    <button style={sty.navArrow} onClick={handleNavNext}>▶</button>
                    <button style={{ ...sty.navArrow, marginLeft: 8, fontSize: 11 }} onClick={() => {
                        const today = new Date().toISOString().slice(0, 10);
                        setSelectedDate(today);
                    }}>Today</button>
                </div>
                <div style={sty.viewTabs}>
                    {(['month', 'week', 'day'] as CalendarView[]).map(v => (
                        <button key={v} onClick={() => setView(v)}
                            style={{
                                ...sty.viewTab,
                                background: view === v ? 'rgba(78, 205, 196, 0.15)' : 'transparent',
                                color: view === v ? '#4ecdc4' : '#888',
                                borderColor: view === v ? 'rgba(78, 205, 196, 0.3)' : 'rgba(255,255,255,0.06)',
                            }}>
                            {v.charAt(0).toUpperCase() + v.slice(1)}
                        </button>
                    ))}
                </div>
            </div>

            {/* ─── Main Content ─── */}
            <div style={sty.content}>
                {/* Left: Calendar View */}
                <div style={sty.calendarCol}>
                    {view === 'month' && (
                        <>
                            <MonthGrid events={eventsList} selectedDate={selectedDate} onSelectDate={setSelectedDate} />
                            <DayEvents events={eventsList} date={selectedDate} />
                        </>
                    )}
                    {view === 'week' && (
                        <WeekView events={eventsList} selectedDate={selectedDate} onSelectDate={(d) => { setSelectedDate(d); setView('day'); }} />
                    )}
                    {view === 'day' && (
                        <DayView events={eventsList} date={selectedDate} />
                    )}
                </div>

                {/* Right: Sidebar */}
                <div style={sty.sidebarCol}>
                    <UpcomingRail events={eventsList} />
                    <MacroPanel />
                </div>
            </div>

            {/* ─── Add Event Dialog ─── */}
            {showAddDialog && (
                <AddEventDialog
                    onClose={() => setShowAddDialog(false)}
                    initialDate={selectedDate}
                />
            )}
        </div>
    );
}

// ─── Styles ───

const sty: Record<string, React.CSSProperties> = {
    page: { padding: 24, maxWidth: 1100, margin: '0 auto', fontFamily: "'Inter', system-ui, sans-serif" },
    header: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 },
    title: { fontSize: 22, fontWeight: 700, color: '#e0e0e0', letterSpacing: '-0.3px' },
    subtitle: { fontSize: 12, color: '#888', marginTop: 4 },
    addBtn: {
        background: 'linear-gradient(135deg, #a78bfa, #8b5cf6)', color: '#fff', fontWeight: 600,
        fontSize: 13, border: 'none', borderRadius: 8, padding: '10px 20px', cursor: 'pointer',
    },

    // Nav
    nav: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 },
    navLeft: { display: 'flex', alignItems: 'center', gap: 12 },
    navArrow: {
        background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)',
        borderRadius: 6, color: '#aaa', cursor: 'pointer', fontSize: 14, padding: '6px 10px',
    },
    navMonth: { fontSize: 18, fontWeight: 600, color: '#e0e0e0', minWidth: 180, textAlign: 'center' as const },
    viewTabs: { display: 'flex', gap: 4 },
    viewTab: {
        border: '1px solid', borderRadius: 6, padding: '6px 14px', cursor: 'pointer',
        fontSize: 12, fontWeight: 500, transition: 'all 0.2s',
    },

    // Layout
    content: { display: 'flex', gap: 20 },
    calendarCol: { flex: 1, minWidth: 0 },
    sidebarCol: { width: 320, flexShrink: 0 },

    // Grid
    gridHeader: { display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 2, marginBottom: 4 },
    gridDayName: { textAlign: 'center' as const, fontSize: 11, color: '#666', fontWeight: 600, padding: 6, textTransform: 'uppercase' as const },
    grid: { display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 2 },
    gridCell: {
        border: '1px solid', borderRadius: 6, padding: '8px 6px', minHeight: 72, cursor: 'pointer',
        transition: 'background 0.2s, border-color 0.2s',
    },
    gridDayNum: { fontSize: 13, display: 'block', marginBottom: 4 },
    gridDots: { display: 'flex', gap: 3, flexWrap: 'wrap' as const },
    eventDot: { width: 6, height: 6, borderRadius: '50%', display: 'inline-block' },

    // Rail sections
    railSection: {
        background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.06)',
        borderRadius: 10, padding: 16, marginBottom: 12,
    },
    railTitle: { fontSize: 13, fontWeight: 600, color: '#aaa', marginBottom: 12, textTransform: 'uppercase' as const, letterSpacing: '0.5px' },
    railItem: { display: 'flex', alignItems: 'center', gap: 8, padding: '8px 0', borderBottom: '1px solid rgba(255,255,255,0.04)' },
    railDot: { width: 8, height: 8, borderRadius: '50%', flexShrink: 0 },
    railTime: { fontSize: 12, color: '#888', fontVariantNumeric: 'tabular-nums', minWidth: 42 },
    railEventTitle: { fontSize: 13, color: '#e0e0e0', flex: 1 },
    railBadge: {
        fontSize: 10, color: '#a78bfa', background: 'rgba(167,139,250,0.1)',
        borderRadius: 4, padding: '2px 6px', textTransform: 'uppercase' as const,
    },

    // Macro panel
    macroItem: {
        display: 'flex', alignItems: 'center', gap: 10, padding: '10px 0',
        borderBottom: '1px solid rgba(255,255,255,0.04)',
    },
    runBtn: {
        background: 'rgba(78, 205, 196, 0.1)', border: '1px solid rgba(78, 205, 196, 0.2)',
        borderRadius: 6, color: '#4ecdc4', cursor: 'pointer', fontSize: 11, padding: '5px 12px',
        fontWeight: 600,
    },

    // Day events
    dayEventItem: {
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        padding: '8px 0', borderBottom: '1px solid rgba(255,255,255,0.04)',
    },
    smallBtn: {
        background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)',
        borderRadius: 4, color: '#888', cursor: 'pointer', fontSize: 11, padding: '3px 6px',
    },

    // Dialog
    dialogOverlay: {
        position: 'fixed' as const, inset: 0, background: 'rgba(0,0,0,0.6)',
        display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000,
    },
    dialog: {
        background: '#1a1a2e', border: '1px solid rgba(255,255,255,0.1)',
        borderRadius: 12, width: '100%', maxWidth: 480, maxHeight: '80vh', overflow: 'auto' as const,
    },
    dialogHeader: {
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        padding: '16px 20px', borderBottom: '1px solid rgba(255,255,255,0.06)', color: '#e0e0e0',
    },
    dialogClose: { background: 'none', border: 'none', color: '#888', cursor: 'pointer', fontSize: 18 },
    dialogBody: { padding: '16px 20px' },
    dialogFooter: {
        display: 'flex', justifyContent: 'flex-end', gap: 10, padding: '12px 20px',
        borderTop: '1px solid rgba(255,255,255,0.06)',
    },
    fieldLabel: { display: 'block', fontSize: 12, color: '#aaa', marginBottom: 6, marginTop: 12 },
    input: {
        width: '100%', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.1)',
        borderRadius: 6, padding: '10px 12px', fontSize: 13, color: '#e0e0e0', outline: 'none',
        boxSizing: 'border-box' as const,
    },
    select: {
        width: '100%', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.1)',
        borderRadius: 6, padding: '10px 12px', fontSize: 13, color: '#e0e0e0', outline: 'none',
        boxSizing: 'border-box' as const,
    },
    cancelBtn: {
        background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)',
        borderRadius: 6, padding: '8px 16px', color: '#aaa', cursor: 'pointer', fontSize: 13,
    },
    saveBtn: {
        background: 'linear-gradient(135deg, #a78bfa, #8b5cf6)', border: 'none',
        borderRadius: 6, padding: '8px 20px', color: '#fff', fontWeight: 600, cursor: 'pointer', fontSize: 13,
    },
};

// ─── Week View Styles ───
const ws: Record<string, React.CSSProperties> = {
    timeGutter: { width: 56, flexShrink: 0 },
    dayHeader: {
        display: 'flex', flexDirection: 'column' as const, alignItems: 'center', gap: 4,
        padding: '8px 4px', borderBottom: '1px solid rgba(255,255,255,0.06)',
        borderRight: '1px solid rgba(255,255,255,0.04)',
    },
    timeLabel: {
        width: 56, fontSize: 11, color: '#666', padding: '4px 8px 0 0',
        textAlign: 'right' as const, fontVariantNumeric: 'tabular-nums',
        borderRight: '1px solid rgba(255,255,255,0.06)',
    },
    hourCell: {
        borderRight: '1px solid rgba(255,255,255,0.04)',
        borderBottom: '1px solid rgba(255,255,255,0.04)',
        padding: 2, minHeight: 48,
    },
    weekEvent: {
        display: 'flex', alignItems: 'center', gap: 3, padding: '2px 4px',
        borderRadius: 3, marginBottom: 1, overflow: 'hidden',
    },
};

// ─── Day View Styles ───
const ds: Record<string, React.CSSProperties> = {
    timeLabel: {
        width: 56, flexShrink: 0, fontSize: 12, padding: '4px 8px 0 0',
        textAlign: 'right' as const, fontVariantNumeric: 'tabular-nums',
        borderRight: '1px solid rgba(255,255,255,0.06)',
    },
    eventArea: { flex: 1, padding: '4px 8px', minWidth: 0 },
    dayEvent: {
        padding: '8px 10px', borderRadius: 6, marginBottom: 4,
    },
};
