/**
 * Cursor Extension Entry Point
 * Renders MainDashboard (multi-tab UI with Agents, Chat, Chains, Tools, Timeline, NL Tags)
 * 
 * CRITICAL FIX: Changed from AgentManagementDashboard to MainDashboard
 * Date: 2025-10-31
 * Agent: Sonnet (fixing React UI loading issue)
 */

import React from 'react'
import ReactDOM from 'react-dom/client'
import MainDashboard from './components/MainDashboard'
import { ErrorBoundary } from './components/ErrorBoundary'
import './index.css'

// Create root and render MainDashboard (NOT AgentManagementDashboard)
console.log('[AIM-OS] ========================================');
console.log('[AIM-OS] main-cursor.tsx loaded - attempting to mount React UI');
console.log('[AIM-OS] Document ready state:', document.readyState);
console.log('[AIM-OS] Window location:', window.location.href);
console.log('[AIM-OS] ========================================');

const rootElement = document.getElementById('root')
if (rootElement) {
  console.log('[AIM-OS] ✅ Root element found, mounting React...');
  try {
    ReactDOM.createRoot(rootElement).render(
      <React.StrictMode>
        <ErrorBoundary>
          <div className="h-screen w-screen overflow-hidden">
            <MainDashboard />
          </div>
        </ErrorBoundary>
      </React.StrictMode>
    );
    console.log('[AIM-OS] ✅ React UI mounted successfully!');
  } catch (error) {
    console.error('[AIM-OS] ❌ Error mounting React UI:', error);
    // Render error UI directly if mount fails
    rootElement.innerHTML = `
      <div style="padding: 20px; color: white; background: #1e1e1e; height: 100vh;">
        <h2 style="color: #ff6b6b;">❌ Failed to Mount React UI</h2>
        <p>Error: ${error instanceof Error ? error.message : 'Unknown error'}</p>
        <p>Check Developer Console for details.</p>
      </div>
    `;
  }
} else {
  console.error('[AIM-OS] ❌ Root element not found - React UI cannot load!');
  console.error('[AIM-OS] Document body:', document.body);
  console.error('[AIM-OS] Document HTML:', document.documentElement.innerHTML.substring(0, 500));
  
  // Show error in document if root doesn't exist
  document.body.innerHTML = `
    <div style="padding: 20px; color: white; background: #1e1e1e; height: 100vh;">
      <h2 style="color: #ff6b6b;">❌ Root Element Not Found</h2>
      <p>The React root element (&lt;div id="root"&gt;) is missing from the HTML.</p>
      <p>Check Developer Console for details.</p>
    </div>
  `;
}

