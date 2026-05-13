import React from 'react'

interface Props {
  planningActive: boolean
  codingActive: boolean
}

// Minimal non-invasive visual cue when both agents are active in drawers.
// Positioned fixed so it doesn't interfere with existing panel layout.
export const ChatBridgeIndicator: React.FC<Props> = ({ planningActive, codingActive }) => {
  const active = planningActive && codingActive
  if (!active) return null
  return (
    <div className="fixed top-16 right-4 z-40">
      <div className="px-3 py-2 rounded-lg bg-blue-600/90 text-white shadow-lg border border-white/20 text-xs">
        <span className="font-semibold">Agents collaborating</span>
        <span className="ml-2 opacity-90">(Planning ↔ Coding)</span>
      </div>
    </div>
  )
}
