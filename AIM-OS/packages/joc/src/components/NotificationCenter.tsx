import { useNotificationStore, type NotificationType } from '../store/notificationStore';

// ─── Component ───

export function NotificationCenter() {
    const { notifications, toasts, panelOpen, dismissToast, markRead, markAllRead, clearAll, togglePanel } = useNotificationStore();

    const unreadCount = notifications.filter(n => !n.read).length;

    const typeStyles: Record<NotificationType, { icon: string; color: string; bg: string }> = {
        success: { icon: '✓', color: '#4ecdc4', bg: 'rgba(78,205,196,0.08)' },
        warning: { icon: '⚠', color: '#ffd93d', bg: 'rgba(255,217,61,0.08)' },
        error: { icon: '✕', color: '#ff6b6b', bg: 'rgba(255,107,107,0.08)' },
        info: { icon: 'ℹ', color: '#00d4ff', bg: 'rgba(0,212,255,0.08)' },
    };

    const timeAgo = (ts: number) => {
        const diff = Date.now() - ts;
        if (diff < 60000) return 'Just now';
        if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
        return `${Math.floor(diff / 86400000)}d ago`;
    };

    return (
        <>
            {/* ─── Toast Stack ─── */}
            <div className="notif-toast-stack">
                {toasts.map(toast => {
                    const st = typeStyles[toast.type];
                    return (
                        <div key={toast.id} className="notif-toast" style={{ borderLeftColor: st.color }}>
                            <span className="notif-toast-icon" style={{ color: st.color }}>{st.icon}</span>
                            <div className="notif-toast-content">
                                <div className="notif-toast-title">{toast.title}</div>
                                <div className="notif-toast-msg">{toast.message}</div>
                            </div>
                            <button className="notif-toast-close" onClick={() => dismissToast(toast.id)}>✕</button>
                        </div>
                    );
                })}
            </div>

            {/* ─── Bell ─── */}
            <button className="notif-bell" onClick={togglePanel}>
                🔔
                {unreadCount > 0 && <span className="notif-bell-badge">{unreadCount}</span>}
            </button>

            {/* ─── Panel ─── */}
            {panelOpen && (
                <div className="notif-panel-overlay" onClick={togglePanel}>
                    <div className="notif-panel" onClick={e => e.stopPropagation()}>
                        <div className="notif-panel-header">
                            <span className="notif-panel-title">Notifications ({unreadCount} unread)</span>
                            <div className="notif-panel-actions">
                                <button className="notif-action-btn" onClick={markAllRead}>Mark all read</button>
                                <button className="notif-action-btn" onClick={clearAll}>Clear</button>
                            </div>
                        </div>
                        <div className="notif-panel-list">
                            {notifications.length === 0 && (
                                <div className="notif-empty">No notifications</div>
                            )}
                            {notifications.map(n => {
                                const st = typeStyles[n.type];
                                return (
                                    <div key={n.id} className={`notif-item ${n.read ? 'read' : ''}`}
                                        style={{ background: n.read ? 'transparent' : st.bg }}
                                        onClick={() => markRead(n.id)}>
                                        <span className="notif-item-icon" style={{ color: st.color }}>{st.icon}</span>
                                        <div className="notif-item-content">
                                            <div className="notif-item-title">{n.title}</div>
                                            <div className="notif-item-msg">{n.message}</div>
                                        </div>
                                        <span className="notif-item-time">{timeAgo(n.timestamp)}</span>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}
