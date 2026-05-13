// Chat Heatmap Panel Component
// Grid visualization of context usage across turns and agents

import React, { useState, useMemo, useRef, useEffect } from 'react'
import { Zap } from 'lucide-react'
import { MessageContextInfo } from '../utils/summaryAtoms'
import { AssembledContext } from '../utils/assemble'
import { ChatMessage } from '../types/chatTypes'
import { useAIChatContext } from '../contexts/AIChatContext'

interface ChatHeatmapPanelProps {
  messages: Array<{ id: string; timestamp: Date; agent?: string }>
  contextInfo: Record<string, MessageContextInfo[]>
  assembledContext: AssembledContext | null
  channelId: string
  onBrushSelect?: (messageIds: string[]) => void
  onPriorityDelta?: (messageIds: string[], delta: number) => void
}

export const ChatHeatmapPanel: React.FC<ChatHeatmapPanelProps> = ({
  messages: propMessages,
  contextInfo: propContextInfo,
  assembledContext: propAssembledContext,
  channelId: propChannelId,
  onBrushSelect,
  onPriorityDelta
}) => {
  // Use context if available, otherwise use props
  const context = useAIChatContext()
  const messages = propMessages.length > 0 ? propMessages : (context.messages[context.selectedChannel] || [])
  const contextInfo = Object.keys(propContextInfo).length > 0 ? propContextInfo : context.contextInfo
  const assembledContext = propAssembledContext ?? context.assembledContext
  const channelId = propChannelId || context.selectedChannel
  const [selectedAgent, setSelectedAgent] = useState<string | 'all'>('all')
  const [brushStart, setBrushStart] = useState<{ x: number; y: number } | null>(null)
  const [brushEnd, setBrushEnd] = useState<{ x: number; y: number } | null>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  
  const channelInfo = contextInfo[channelId] || []
  
  // Get unique agents
  const agents = useMemo(() => {
    const agentSet = new Set<string>()
    channelInfo.forEach(info => {
      info.uses.forEach(use => agentSet.add(use.agent))
    })
    messages.forEach(msg => {
      if (msg.agent) agentSet.add(msg.agent)
    })
    return Array.from(agentSet).sort()
  }, [channelInfo, messages])
  
  // Prepare grid data
  const gridData = useMemo(() => {
    const cellSize = 20
    const rows = selectedAgent === 'all' ? agents.length : 1
    const cols = messages.length
    
    return {
      cellSize,
      rows,
      cols,
      data: messages.map((msg, colIdx) => {
        const info = channelInfo.find(i => i.id === msg.id)
        const uses = info?.uses || []
        
        if (selectedAgent === 'all') {
          return agents.map((agent, rowIdx) => {
            const use = uses.find(u => u.agent === agent)
            return {
              row: rowIdx,
              col: colIdx,
              messageId: msg.id,
              agent,
              included: use ? info?.included ?? false : false,
              score: use?.score ?? 0,
              tokens: use?.tokens ?? 0,
              reasons: use?.reasons ?? []
            }
          })
        } else {
          const use = uses.find(u => u.agent === selectedAgent)
          return [{
            row: 0,
            col: colIdx,
            messageId: msg.id,
            agent: selectedAgent,
            included: use ? info?.included ?? false : false,
            score: use?.score ?? 0,
            tokens: use?.tokens ?? 0,
            reasons: use?.reasons ?? []
          }]
        }
      }).flat()
    }
  }, [messages, channelInfo, agents, selectedAgent])
  
  // Draw heatmap
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    
    const ctx = canvas.getContext('2d')
    if (!ctx) return
    
    const { cellSize, rows, cols, data } = gridData
    
    canvas.width = cols * cellSize
    canvas.height = rows * cellSize
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    // Draw cells
    data.forEach(cell => {
      const x = cell.col * cellSize
      const y = cell.row * cellSize
      
      // Color based on inclusion strength
      const intensity = cell.included ? cell.score : cell.score * 0.3
      const hue = 120 - Math.round(intensity * 90) // Green to amber
      const alpha = cell.included ? 0.8 : 0.3
      
      ctx.fillStyle = `hsla(${hue}, 80%, 50%, ${alpha})`
      ctx.fillRect(x, y, cellSize - 1, cellSize - 1)
      
      // Border
      ctx.strokeStyle = `hsla(${hue}, 80%, 30%, 0.5)`
      ctx.strokeRect(x, y, cellSize - 1, cellSize - 1)
    })
    
    // Draw brush selection
    if (brushStart && brushEnd) {
      const minX = Math.min(brushStart.x, brushEnd.x)
      const maxX = Math.max(brushStart.x, brushEnd.x)
      const minY = Math.min(brushStart.y, brushEnd.y)
      const maxY = Math.max(brushStart.y, brushEnd.y)
      
      ctx.strokeStyle = 'rgba(59, 130, 246, 0.8)'
      ctx.lineWidth = 2
      ctx.strokeRect(minX, minY, maxX - minX, maxY - minY)
      
      ctx.fillStyle = 'rgba(59, 130, 246, 0.1)'
      ctx.fillRect(minX, minY, maxX - minX, maxY - minY)
    }
  }, [gridData, brushStart, brushEnd])
  
  // Handle mouse events for brushing
  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const rect = canvasRef.current?.getBoundingClientRect()
    if (!rect) return
    
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top
    setBrushStart({ x, y })
    setBrushEnd({ x, y })
  }
  
  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!brushStart) return
    
    const rect = canvasRef.current?.getBoundingClientRect()
    if (!rect) return
    
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top
    setBrushEnd({ x, y })
  }
  
  const handleMouseUp = () => {
    if (!brushStart || !brushEnd) return
    
    // Get selected cells
    const { cellSize } = gridData
    const minCol = Math.floor(Math.min(brushStart.x, brushEnd.x) / cellSize)
    const maxCol = Math.floor(Math.max(brushStart.x, brushEnd.x) / cellSize)
    const minRow = Math.floor(Math.min(brushStart.y, brushEnd.y) / cellSize)
    const maxRow = Math.floor(Math.max(brushStart.y, brushEnd.y) / cellSize)
    
    const selectedIds = new Set<string>()
    gridData.data.forEach(cell => {
      if (cell.col >= minCol && cell.col <= maxCol &&
          cell.row >= minRow && cell.row <= maxRow) {
        selectedIds.add(cell.messageId)
      }
    })
    
    if (onBrushSelect && selectedIds.size > 0) {
      onBrushSelect(Array.from(selectedIds))
    }
    
    setBrushStart(null)
    setBrushEnd(null)
  }
  
  return (
    <div className="h-full flex flex-col bg-gray-950 text-gray-200">
      {/* Header */}
      <div className="border-b border-gray-800 p-3">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-semibold text-gray-200 flex items-center gap-2">
            <Zap className="w-4 h-4" />
            Context Heatmap
          </h3>
          <div className="flex items-center gap-2">
            {/* Agent filter */}
            <select
              value={selectedAgent}
              onChange={(e) => setSelectedAgent(e.target.value as string | 'all')}
              className="text-xs bg-gray-900 border border-gray-700 rounded px-2 py-1 text-gray-300"
            >
              <option value="all">All Agents</option>
              {agents.map(agent => (
                <option key={agent} value={agent}>{agent}</option>
              ))}
            </select>
          </div>
        </div>
        
        {/* Legend */}
        <div className="flex items-center gap-4 text-xs text-gray-400">
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded" style={{ background: 'hsla(120, 80%, 50%, 0.8)' }} />
            <span>High significance</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded" style={{ background: 'hsla(60, 80%, 50%, 0.8)' }} />
            <span>Medium significance</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded" style={{ background: 'hsla(30, 80%, 50%, 0.3)' }} />
            <span>Not included</span>
          </div>
        </div>
      </div>
      
      {/* Canvas */}
      <div className="flex-1 overflow-auto p-4" ref={containerRef}>
        <div className="inline-block">
          {/* Row labels */}
          <div className="flex">
            <div className="w-20" /> {/* Spacer */}
            <div className="flex">
              {messages.map((msg, idx) => (
                <div
                  key={msg.id}
                  className="w-5 h-5 text-[8px] text-gray-500 flex items-center justify-center"
                  title={`Turn ${idx + 1}: ${msg.agent || 'user'}`}
                >
                  {idx + 1}
                </div>
              ))}
            </div>
          </div>
          
          {/* Grid with labels */}
          <div className="flex">
            {/* Column labels */}
            <div className="flex flex-col">
              {(selectedAgent === 'all' ? agents : [selectedAgent]).map((agent, idx) => (
                <div
                  key={agent}
                  className="w-20 h-5 text-[8px] text-gray-500 flex items-center justify-end pr-2"
                  title={agent}
                >
                  {agent.slice(0, 8)}
                </div>
              ))}
            </div>
            
            {/* Canvas */}
            <canvas
              ref={canvasRef}
              onMouseDown={handleMouseDown}
              onMouseMove={handleMouseMove}
              onMouseUp={handleMouseUp}
              onMouseLeave={handleMouseUp}
              className="border border-gray-800 rounded cursor-crosshair"
              style={{ imageRendering: 'pixelated' }}
            />
          </div>
        </div>
      </div>
      
      {/* Footer */}
      <div className="border-t border-gray-800 p-2 bg-gray-900/50">
        <div className="text-xs text-gray-400">
          Drag to select multiple messages • {messages.length} turns • {agents.length} agents
        </div>
      </div>
    </div>
  )
}

