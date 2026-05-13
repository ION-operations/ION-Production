/**
 * Agent Chats Drawer Panel
 * Shows list of individual agent chats for quick access
 */

import React, { useState, useEffect } from 'react'
import { Bot, MessageSquare, Clock, Search, X } from 'lucide-react'
import { useAIChat } from '../../hooks/useAIChat'

interface AgentChatsPanelProps {
  onSelectAgent?: (agentName: string) => void
  onSelectThread?: (threadId: string) => void
}

export const AgentChatsPanel: React.FC<AgentChatsPanelProps> = ({ 
  onSelectAgent, 
  onSelectThread 
}) => {
  const { threads, discoveredAgents } = useAIChat()
  const [searchQuery, setSearchQuery] = useState('')

  // Group threads by agent
  const agentThreads = React.useMemo(() => {
    const grouped: { [agent: string]: Array<{ thread_id: string; last_message?: string; timestamp?: string }> } = {}
    
    threads.forEach(thread => {
      // Get agent from participants
      const agent = thread.participants?.[0] || 'Unknown'
      if (!grouped[agent]) {
        grouped[agent] = []
      }
      grouped[agent].push({
        thread_id: thread.thread_id || '',
        last_message: thread.last_message?.content,
        timestamp: thread.last_message?.timestamp
      })
    })

    return grouped
  }, [threads])

  const filteredAgents = React.useMemo(() => {
    if (!searchQuery) return discoveredAgents
    const query = searchQuery.toLowerCase()
    return discoveredAgents.filter(agent => 
      agent.toLowerCase().includes(query) || 
      agentThreads[agent]?.some(t => t.last_message?.toLowerCase().includes(query))
    )
  }, [discoveredAgents, searchQuery, agentThreads])

  return (
    <div className="h-full flex flex-col bg-gray-900 text-white">
      {/* Header */}
      <div className="p-4 border-b border-gray-800">
        <div className="flex items-center gap-2 mb-3">
          <MessageSquare className="w-5 h-5 text-blue-400" />
          <h3 className="font-semibold">Agent Chats</h3>
        </div>
        
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-2 top-2.5 w-4 h-4 text-gray-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search agents or messages..."
            className="w-full bg-gray-800 text-white px-8 py-2 rounded text-sm border border-gray-700 focus:outline-none focus:border-blue-500"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-2 top-2.5 text-gray-400 hover:text-white"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Agent List */}
      <div className="flex-1 overflow-auto">
        {filteredAgents.length === 0 ? (
          <div className="p-8 text-center text-gray-400">
            <Bot className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>No agents found</p>
          </div>
        ) : (
          <div className="space-y-1 p-2">
            {filteredAgents.map(agent => (
              <div key={agent} className="space-y-1">
                {/* Agent Header */}
                <button
                  onClick={() => onSelectAgent?.(agent)}
                  className="w-full p-3 bg-gray-800 hover:bg-gray-700 rounded-lg flex items-center justify-between transition-colors group"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                      <Bot className="w-4 h-4 text-white" />
                    </div>
                    <div className="text-left">
                      <div className="font-medium text-sm">{agent}</div>
                      {agentThreads[agent] && (
                        <div className="text-xs text-gray-400">
                          {agentThreads[agent].length} thread{agentThreads[agent].length !== 1 ? 's' : ''}
                        </div>
                      )}
                    </div>
                  </div>
                  <MessageSquare className="w-4 h-4 text-gray-400 group-hover:text-blue-400" />
                </button>

                {/* Threads for this agent */}
                {agentThreads[agent] && agentThreads[agent].length > 0 && (
                  <div className="ml-4 space-y-1">
                    {agentThreads[agent].slice(0, 3).map((thread, idx) => (
                      <button
                        key={thread.thread_id || idx}
                        onClick={() => {
                          onSelectAgent?.(agent)
                          onSelectThread?.(thread.thread_id || '')
                        }}
                        className="w-full p-2 bg-gray-800/50 hover:bg-gray-700/50 rounded text-left text-xs transition-colors"
                      >
                        <div className="flex items-center gap-2 mb-1">
                          <Clock className="w-3 h-3 text-gray-500" />
                          <span className="text-gray-400">
                            {thread.timestamp ? new Date(thread.timestamp).toLocaleDateString() : 'Recent'}
                          </span>
                        </div>
                        {thread.last_message && (
                          <div className="text-gray-300 truncate">{thread.last_message}</div>
                        )}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

