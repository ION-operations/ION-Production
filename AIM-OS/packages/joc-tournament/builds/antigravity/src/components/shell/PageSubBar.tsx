import React from 'react';
import { useShellStore, WORKSPACES } from '../../store/shellStore';

export function PageSubBar() {
    const { activeWorkspace } = useShellStore();
    const ws = WORKSPACES.find((w) => w.id === activeWorkspace);

    return (
        <div className="subbar">
            <div className="subbar-title">
                <span className="subbar-dot" />
                <span>{ws?.title || 'Mission Control'}</span>
            </div>
            <span className="subbar-breadcrumb">
                {ws?.navGroup.toUpperCase()} › {ws?.title}
            </span>
            <div className="subbar-actions">
                <button className="subbar-btn">⟳ Refresh</button>
                <button className="subbar-btn">⊞ Layout</button>
            </div>
        </div>
    );
}
