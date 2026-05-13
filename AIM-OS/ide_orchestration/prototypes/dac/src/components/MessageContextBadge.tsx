// Message Context Badge Component
// Shows significance score, inclusion status, and quick actions

import React from 'react'
import { Pin, TrendingUp, X } from 'lucide-react'
import { MessageContextInfo, ContextOverride, SummaryAtom } from '../utils/summaryAtoms'

interface MessageContextBadgeProps {
  messageId: string
  atom?: SummaryAtom
  contextInfo?: MessageContextInfo
  override?: ContextOverride
  packTotal: number
  onPromote: (id: string) => void
  onPin: (id: string, pinned: boolean) => void
  onForce: (id: string, level: 'macro' | 'meso' | 'micro' | 'raw' | null) => void
  onPriority: (id: string, prio: number) => void
}

export const MessageContextBadge: React.FC<MessageContextBadgeProps> = ({
  messageId,
  atom,
  contextInfo,
  override,
  packTotal,
  onPromote,
  onPin,
  onForce,
  onPriority
}) => {
  if (!atom && !contextInfo) return null
  
  const significance = atom?.sig.score ?? contextInfo?.significance ?? 0
  const included = contextInfo?.included ?? false
  const used = contextInfo?.totalTokensInPack ?? 0
  const share = packTotal > 0 ? Math.round((used / packTotal) * 100) : 0
  const level = override?.forcedLevel ?? atom?.level ?? 'micro'
  const prio = override?.priority ?? 0
  
  // Heat color based on significance
  const heatColor = (sig: number, included: boolean): string => {
    const hue = 120 - Math.round(sig * 90) // 120=green → 30=amber
    const alpha = included ? 0.9 : 0.3
    return `hsla(${hue}, 80%, 50%, ${alpha})`
  }
  
  // Dominant level from context uses
  const dominantLevel = (): 'macro' | 'meso' | 'micro' | 'raw' => {
    if (contextInfo?.uses && contextInfo.uses.length > 0) {
      const levels = contextInfo.uses.map(u => u.level)
      const counts: Record<string, number> = {}
      levels.forEach(l => {
        counts[l] = (counts[l] || 0) + 1
      })
      const sorted = Object.entries(counts).sort((a, b) => b[1] - a[1])
      return (sorted[0]?.[0] as 'macro' | 'meso' | 'micro' | 'raw') ?? 'micro'
    }
    return level as 'macro' | 'meso' | 'micro' | 'raw'
  }
  
  const currentLevel = dominantLevel()
  
  return (
    <div className="flex items-center gap-2 bg-gray-900/60 rounded px-2 py-1 border border-gray-800 text-xs">
      {/* Heat strip */}
      <div
        className="w-1 h-5 rounded"
        style={{ background: heatColor(significance, included) }}
        title={`Significance: ${(significance * 100).toFixed(0)}%`}
      />
      
      {/* Tokens + share */}
      <span className="text-[11px] text-gray-400">
        {included ? `${used.toLocaleString()} tok` : 'not included'}
        {included && share > 0 ? ` • ${share}%` : ''}
      </span>
      
      {/* Level pills */}
      <div className="flex gap-1">
        {(['macro', 'meso', 'micro', 'raw'] as const).map(lv => (
          <button
            key={lv}
            className={`px-1.5 py-0.5 text-[10px] rounded transition-colors ${
              lv === currentLevel
                ? 'bg-blue-600 text-white'
                : 'bg-gray-800 text-gray-400 hover:text-white hover:bg-gray-700'
            }`}
            onClick={() => onForce(messageId, lv === currentLevel ? null : lv)}
            title={`Force level: ${lv}`}
          >
            {lv}
          </button>
        ))}
        {override?.forcedLevel && (
          <button
            className="px-1.5 py-0.5 text-[10px] rounded bg-gray-800 text-gray-400 hover:text-white hover:bg-gray-700"
            onClick={() => onForce(messageId, null)}
            title="Clear forced level"
          >
            <X className="w-3 h-3" />
          </button>
        )}
      </div>
      
      {/* Pin button */}
      <button
        className={`px-1.5 py-0.5 text-[10px] rounded transition-colors ${
          override?.pinned
            ? 'bg-amber-600 text-white'
            : 'bg-gray-800 text-gray-400 hover:text-white hover:bg-gray-700'
        }`}
        onClick={() => onPin(messageId, !override?.pinned)}
        title={override?.pinned ? 'Unpin message' : 'Pin message'}
      >
        <Pin className={`w-3 h-3 ${override?.pinned ? 'fill-current' : ''}`} />
      </button>
      
      {/* Promote button */}
      <button
        className="px-1.5 py-0.5 text-[10px] rounded bg-gray-800 text-gray-400 hover:text-white hover:bg-gray-700 transition-colors"
        onClick={() => onPromote(messageId)}
        title="Promote message (increase half-life)"
      >
        <TrendingUp className="w-3 h-3" />
      </button>
      
      {/* Priority slider */}
      <div className="flex items-center gap-1 ml-1">
        <span className="text-[10px] text-gray-500">prio</span>
        <input
          type="range"
          min={-1}
          max={1}
          step={0.1}
          value={prio}
          onChange={(e) => onPriority(messageId, parseFloat(e.target.value))}
          className="w-20 accent-blue-600"
          title={`Priority: ${prio > 0 ? '+' : ''}${prio.toFixed(1)}`}
        />
        {prio !== 0 && (
          <span className="text-[10px] text-gray-400 w-8 text-right">
            {prio > 0 ? '+' : ''}{prio.toFixed(1)}
          </span>
        )}
      </div>
      
      {/* Significance score */}
      <div className="ml-auto text-[10px] text-gray-500">
        {(significance * 100).toFixed(0)}%
      </div>
    </div>
  )
}

