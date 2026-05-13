import React from 'react';
import { TopBar, LeftRail, LeftDrawer, BottomBar, AssistantRail } from './shell';
import { MissionControl } from './MissionControl';

// ═══════════════════════════════════════════════════════════════
// J.A.R.V.I.S. Shell — The Instrument Chassis
//
// Layout:
// ┌─────────────────────────────────────────────┐
// │ TopBar                                       │
// ├────┬────────┬──────────────────┬─────────────┤
// │Left│ Left   │                  │ Assistant   │
// │Rail│ Drawer │  Main Content    │ Rail        │
// │    │        │  (Mission Ctrl)  │             │
// ├────┴────────┴──────────────────┴─────────────┤
// │ BottomBar                                     │
// └───────────────────────────────────────────────┘
// ═══════════════════════════════════════════════════════════════

export const App: React.FC = () => {
  return (
    <div className="jarvis-shell">
      <TopBar />
      <div className="jarvis-body">
        <LeftRail />
        <div className="jarvis-workspace">
          <LeftDrawer />
          <main className="jarvis-content">
            <MissionControl />
          </main>
        </div>
        <AssistantRail />
      </div>
      <BottomBar />
    </div>
  );
};
