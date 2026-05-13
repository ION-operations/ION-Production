// Context Ledger Component
// Shows budget, token usage, and detailed context information

import React, { useState, useMemo } from 'react'
import { Database, X, TrendingDown, Trash2, Filter } from 'lucide-react'
import { MessageContextInfo, ContextUse } from '../utils/summaryAtoms'
import { AssembledContext } from '../utils/assemble'

interface ContextLedgerProps {
  assembledContext: AssembledContext | null
  contextInfo: Record<string, MessageContextInfo[]>
  channelId: string
  budget: number
  onDemote?: (ids: string[]) => void
  onUnpinAll?: () => void
  onClearPriorities?: () => void
}

export const ContextLedger: React.FC<ContextLedgerProps> = ({
  assembledContext: propAssembledContext,
  contextInfo: propContextInfo,
  channelId: propChannelId,
  budget: propBudget,
  onDemote,
  onUnpinAll,
  onClearPriorities
}) => {
  // Use context if available, otherwise use props
  const context = useAIChatContext()
  const assembledContext = propAssembledContext ?? context.assembledContext
  const contextInfo = Object.keys(propContextInfo).length > 0 ? propContextInfo : context.contextInfo
  const channelId = propChannelId || context.selectedChannel
  const budget = propBudget || context.budget
  const [sortBy, setSortBy] = useState<'score' | 'tokens' | 'agent'>('score')
  const [filterAgent, setFilterAgent] = useState<string | null>(null)
  
  const channelInfo = contextInfo[channelId] || []
  
  // Prepare items for display
  const items = useMemo(() => {
    let items = channelInfo.map(info => {
      // Get dominant agent and level
      const dominantUse = info.uses.length > 0 
        ? info.uses.reduce((max, use) => use.tokens > max.tokens ? use : max, info.uses[0])
        : null
      
      return {
        id: info.id,
        title: `Message ${info.id.slice(0, 8)}...`,
        level: dominantUse?.level ?? 'micro',
        tokens: info.totalTokensInPack,
        agent: dominantUse?.agent ?? 'none',
        reasons: dominantUse?.reasons ?? [],
        included: info.included,
        score: info.significance
      }
    })
    
    // Filter by agent
    if (filterAgent) {
      items = items.filter(item => item.agent === filterAgent)
    }
    
    // Sort
    items.sort((a, b) => {
      switch (sortBy) {
        case 'tokens':
          return b.tokens - a.tokens
        case 'agent':
          return a.agent.localeCompare(b.agent)
        case 'score':
        default:
          return b.score - a.score
      }
    })
    
    return items
  }, [channelInfo, sortBy, filterAgent])
  
  const totalUsed = assembledContext?.totalTokens ?? 0
  const free = budget - totalUsed
  const usagePercent = budget > 0 ? Math.round((totalUsed / budget) * 100) : 0
  
  // Get unique agents
  const agents = useMemo(() => {
    const agentSet = new Set<string>()
    channelInfo.forEach(info => {
      info.uses.forEach(use => agentSet.add(use.agent))
    })
    return Array.from(agentSet).sort()
  }, [channelInfo])
  
  return (
    <div className="h-full flex flex-col bg-gray-950 text-gray-200">
      {/* Header */}
      <div className="border-b border-gray-800 p-3">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-semibold text-gray-200">Context Ledger</h3>
          <div className="flex items-center gap-2">
            {/* Filter by agent */}
            {agents.length > 0 && (
              <select
                value={filterAgent || ''}
                onChange={(e) => setFilterAgent(e.target.value || null)}
                className="text-xs bg-gray-900 border border-gray-700 rounded px-2 py-1 text-gray-300"
              >
                <option value="">All Agents</option>
                {agents.map(agent => (
                  <option key={agent} value={agent}>{agent}</option>
                ))}
              </select>
            )}
            
            {/* Sort */}
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as 'score' | 'tokens' | 'agent')}
              className="text-xs bg-gray-900 border border-gray-700 rounded px-2 py-1 text-gray-300"
            >
              <option value="score">Sort by Score</option>
              <option value="tokens">Sort by Tokens</option>
              <option value="agent">Sort by Agent</option>
            </select>
          </div>
        </div>
        
        {/* Budget Bar */}
        <div className="space-y-1">
          <div className="flex items-center justify-between text-xs text-gray-400">
            <span>Budget: {budget.toLocaleString()} tokens</span>
            <span>{usagePercent}% used</span>
          </div>
          <div className="w-full h-2 bg-gray-900 rounded-full overflow-hidden">
            <div
              className={`h-full transition-all ${
                usagePercent > 90 ? 'bg-red-600' :
                usagePercent > 75 ? 'bg-yellow-600' :
                'bg-blue-600'
              }`}
              style={{ width: `${Math.min(100, usagePercent)}%` }}
            />
          </div>
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span>Used: {totalUsed.toLocaleString()}</span>
            <span>Free: {free.toLocaleString()}</span>
          </div>
        </div>
        
        {/* Batch Actions */}
        {(onDemote || onUnpinAll || onClearPriorities) && (
          <div className="flex items-center gap-2 mt-3 pt-3 border-t border-gray-800">
            {onDemote && (
              <button
                onClick={() => {
                  const topN = items.filter(i => i.included).slice(0, 3).map(i => i.id)
                  if (topN.length > 0) onDemote(topN)
                }}
                className="text-xs px-2 py-1 rounded bg-gray-800 hover:bg-gray-700 text-gray-300 transition-colors flex items-center gap-1"
                title="Demote top 3 items"
              >
                <TrendingDown className="w-3 h-3" />
                Demote Top 3
              </button>
            )}
            {onUnpinAll && (
              <button
                onClick={onUnpinAll}
                className="text-xs px-2 py-1 rounded bg-gray-800 hover:bg-gray-700 text-gray-300 transition-colors flex items-center gap-1"
              >
                <X className="w-3 h-3" />
                Unpin All
              </button>
            )}
            {onClearPriorities && (
              <button
                onClick={onClearPriorities}
                className="text-xs px-2 py-1 rounded bg-gray-800 hover:bg-gray-700 text-gray-300 transition-colors flex items-center gap-1"
              >
                <Trash2 className="w-3 h-3" />
                Clear Priorities
              </button>
            )}
          </div>
        )}
      </div>
      
      {/* Items Table */}
      <div className="flex-1 overflow-y-auto">
        {items.length === 0 ? (
          <div className="p-4 text-center text-sm text-gray-500">
            No context items
          </div>
        ) : (
          <table className="w-full text-xs">
            <thead className="sticky top-0 bg-gray-900 border-b border-gray-800">
              <tr>
                <th className="text-left p-2 text-gray-400 font-semibold">Item</th>
                <th className="text-left p-2 text-gray-400 font-semibold">Level</th>
                <th className="text-right p-2 text-gray-400 font-semibold">Tokens</th>
                <th className="text-left p-2 text-gray-400 font-semibold">Agent</th>
                <th className="text-left p-2 text-gray-400 font-semibold">Reasons</th>
                <th className="text-right p-2 text-gray-400 font-semibold">Score</th>
              </tr>
            </thead>
            <tbody>
              {items.map(item => (
                <tr
                  key={item.id}
                  className={`border-b border-gray-900 hover:bg-gray-900/50 transition-colors ${
                    item.included ? '' : 'opacity-50'
                  }`}
                >
                  <td className="p-2">
                    <div className="flex items-center gap-1">
                      {item.included ? (
                        <div className="w-1.5 h-1.5 rounded-full bg-blue-500" />
                      ) : (
                        <div className="w-1.5 h-1.5 rounded-full bg-gray-700" />
                      )}
                      <span className="font-mono text-[10px]">{item.title}</span>
                    </div>
                  </td>
                  <td className="p-2">
                    <span className={`px-1.5 py-0.5 rounded text-[10px] ${
                      item.level === 'macro' ? 'bg-purple-600/20 text-purple-300' :
                      item.level === 'meso' ? 'bg-blue-600/20 text-blue-300' :
                      item.level === 'micro' ? 'bg-green-600/20 text-green-300' :
                      'bg-gray-600/20 text-gray-300'
                    }`}>
                      {item.level}
                    </span>
                  </td>
                  <td className="p-2 text-right font-mono text-[10px] text-gray-400">
                    {item.tokens.toLocaleString()}
                  </td>
                  <td className="p-2">
                    <span className="text-[10px] text-gray-400">{item.agent}</span>
                  </td>
                  <td className="p-2">
                    <div className="flex flex-wrap gap-1">
                      {item.reasons.slice(0, 3).map((reason, idx) => (
                        <span
                          key={idx}
                          className="px-1 py-0.5 rounded text-[10px] bg-gray-800 text-gray-400"
                        >
                          {reason}
                        </span>
                      ))}
                      {item.reasons.length > 3 && (
                        <span className="text-[10px] text-gray-500">
                          +{item.reasons.length - 3}
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="p-2 text-right">
                    <span className="text-[10px] font-semibold text-gray-300">
                      {(item.score * 100).toFixed(0)}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
      
      {/* Footer Summary */}
      <div className="border-t border-gray-800 p-2 bg-gray-900/50">
        <div className="flex items-center justify-between text-xs text-gray-400">
          <span>{items.length} items</span>
          <span>{items.filter(i => i.included).length} included</span>
        </div>
      </div>
    </div>
  )
}

