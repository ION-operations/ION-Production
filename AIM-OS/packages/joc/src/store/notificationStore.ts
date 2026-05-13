import { create } from 'zustand';

// ─── Types ───

export type NotificationType = 'success' | 'warning' | 'error' | 'info';

export interface Notification {
    id: string;
    type: NotificationType;
    title: string;
    message: string;
    timestamp: number;
    read: boolean;
    autoDismiss?: boolean;
}

interface NotificationState {
    notifications: Notification[];
    toasts: Notification[];
    panelOpen: boolean;
    addNotification: (type: NotificationType, title: string, message: string) => void;
    dismissToast: (id: string) => void;
    markRead: (id: string) => void;
    markAllRead: () => void;
    clearAll: () => void;
    togglePanel: () => void;
}

// ─── Store ───

export const useNotificationStore = create<NotificationState>((set) => ({
    notifications: [
        { id: '1', type: 'success', title: 'Dispatch Complete', message: 'Parallel dispatch to ChatGPT + Gemini finished successfully', timestamp: Date.now() - 120000, read: false },
        { id: '2', type: 'info', title: 'Session Refreshed', message: 'ChatGPT session cookies refreshed automatically', timestamp: Date.now() - 300000, read: false },
        { id: '3', type: 'warning', title: 'Token Budget Exceeded', message: 'Context attachment exceeds Ollama limit (8K tokens)', timestamp: Date.now() - 600000, read: true },
        { id: '4', type: 'error', title: 'Claude Session Expired', message: 'Claude session cookies expired — reconnect required', timestamp: Date.now() - 3600000, read: true },
        { id: '5', type: 'success', title: 'Memory Stored', message: 'Synthesized result saved to CMC atom store', timestamp: Date.now() - 7200000, read: true },
    ],
    toasts: [],
    panelOpen: false,

    addNotification: (type, title, message) => {
        const notif: Notification = {
            id: String(Date.now()),
            type, title, message,
            timestamp: Date.now(),
            read: false,
            autoDismiss: type !== 'error',
        };
        set(state => ({
            notifications: [notif, ...state.notifications],
            toasts: [...state.toasts, notif],
        }));
        // Auto-dismiss toast after 5s
        if (notif.autoDismiss) {
            setTimeout(() => {
                set(state => ({ toasts: state.toasts.filter(t => t.id !== notif.id) }));
            }, 5000);
        }
    },

    dismissToast: (id) => set(state => ({
        toasts: state.toasts.filter(t => t.id !== id)
    })),

    markRead: (id) => set(state => ({
        notifications: state.notifications.map(n => n.id === id ? { ...n, read: true } : n)
    })),

    markAllRead: () => set(state => ({
        notifications: state.notifications.map(n => ({ ...n, read: true }))
    })),

    clearAll: () => set({ notifications: [] }),

    togglePanel: () => set(state => ({ panelOpen: !state.panelOpen })),
}));
