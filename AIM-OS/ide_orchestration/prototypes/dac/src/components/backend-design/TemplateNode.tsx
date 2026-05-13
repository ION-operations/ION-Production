// Template Node Component - n8n/Lucidchart-style visual node
// Beautiful, animated, and fully interactive

import React, { memo, useState } from 'react'
import { Handle, Position, NodeProps, NodeResizer } from 'reactflow'
import { Check, AlertCircle, X, Play, Loader2, Settings, Copy, Trash2 } from 'lucide-react'
import { TemplateNodeData, TemplateStatus } from './types'
import { getCategoryConfig } from './templates'

interface TemplateNodeComponentProps extends NodeProps<TemplateNodeData> {
  onDuplicate?: (nodeId: string) => void
  onDelete?: (nodeId: string) => void
  onOpenSettings?: (nodeId: string) => void
}

export const TemplateNode = memo<TemplateNodeComponentProps>(({ 
  id,
  data, 
  selected,
  dragging,
  onDuplicate,
  onDelete,
  onOpenSettings,
}) => {
  const [isHovered, setIsHovered] = useState(false)
  const category = getCategoryConfig(data.type)!
  const Icon = data.icon
  
  // Status styling
  const statusConfig: Record<TemplateStatus, { icon: React.ComponentType<{className?: string}>, color: string, bg: string, pulse?: boolean }> = {
    configured: { icon: Check, color: 'text-green-400', bg: 'bg-green-500/20' },
    incomplete: { icon: AlertCircle, color: 'text-yellow-400', bg: 'bg-yellow-500/20' },
    error: { icon: X, color: 'text-red-400', bg: 'bg-red-500/20' },
    running: { icon: Loader2, color: 'text-blue-400', bg: 'bg-blue-500/20', pulse: true },
    success: { icon: Check, color: 'text-emerald-400', bg: 'bg-emerald-500/20' },
  }
  
  const status = statusConfig[data.status]
  const StatusIcon = status.icon

  return (
    <div
      className={`
        group relative transition-all duration-300 ease-out
        ${dragging ? 'scale-105 rotate-1' : 'scale-100'}
        ${selected ? 'z-10' : 'z-0'}
      `}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Glow effect on selection */}
      {selected && (
        <div 
          className="absolute -inset-2 rounded-2xl opacity-50 blur-xl transition-opacity"
          style={{ backgroundColor: category.accentColor }}
        />
      )}
      
      {/* Main node container */}
      <div 
        className={`
          relative w-44 rounded-xl overflow-hidden
          backdrop-blur-sm transition-all duration-300
          ${category.bgColor} 
          border-2 ${selected ? 'border-opacity-100' : 'border-opacity-50'}
          ${category.borderColor}
          ${selected ? 'shadow-2xl' : 'shadow-lg'}
          ${isHovered && !selected ? 'shadow-xl scale-[1.02]' : ''}
        `}
        style={{
          boxShadow: selected 
            ? `0 0 30px ${category.accentColor}40, 0 20px 40px rgba(0,0,0,0.3)` 
            : '0 10px 30px rgba(0,0,0,0.2)',
        }}
      >
        {/* Header with icon and category color */}
        <div 
          className="p-3 border-b border-gray-700/50"
          style={{ 
            background: `linear-gradient(135deg, ${category.accentColor}20 0%, transparent 100%)` 
          }}
        >
          <div className="flex items-start gap-3">
            {/* Icon container with gradient */}
            <div 
              className={`
                w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0
                ${category.bgColor} border ${category.borderColor}
                shadow-inner transition-transform duration-300
                ${isHovered ? 'scale-110' : ''}
              `}
              style={{
                background: `linear-gradient(135deg, ${category.accentColor}30 0%, ${category.accentColor}10 100%)`,
              }}
            >
              <Icon className={`w-5 h-5 ${category.color}`} />
            </div>
            
            {/* Title and description */}
            <div className="flex-1 min-w-0">
              <div className="text-xs font-semibold text-gray-100 truncate leading-tight">
                {data.name}
              </div>
              <div className="text-[10px] text-gray-400 mt-0.5 line-clamp-2 leading-snug">
                {data.description}
              </div>
            </div>
          </div>
        </div>
        
        {/* Status bar */}
        <div className="px-3 py-2 flex items-center justify-between bg-gray-900/50">
          <div className={`flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] ${status.bg} ${status.color}`}>
            <StatusIcon className={`w-3 h-3 ${status.pulse ? 'animate-spin' : ''}`} />
            <span className="capitalize font-medium">{data.status}</span>
          </div>
          
          <div className="text-[10px] text-gray-500">
            v{data.version}
          </div>
        </div>
        
        {/* Execution indicator (when running) */}
        {data.status === 'running' && (
          <div className="absolute inset-x-0 bottom-0 h-0.5 bg-blue-500 overflow-hidden">
            <div className="h-full w-1/3 bg-blue-300 animate-[shimmer_1s_infinite]" />
          </div>
        )}
        
        {/* Hover action buttons */}
        <div className={`
          absolute top-2 right-2 flex items-center gap-1 transition-all duration-200
          ${isHovered || selected ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-2'}
        `}>
          {onOpenSettings && (
            <button
              onClick={(e) => { e.stopPropagation(); onOpenSettings(id) }}
              className="w-6 h-6 rounded bg-gray-800/80 hover:bg-gray-700 flex items-center justify-center text-gray-400 hover:text-gray-200 transition-colors"
              title="Settings"
            >
              <Settings className="w-3 h-3" />
            </button>
          )}
          {onDuplicate && (
            <button
              onClick={(e) => { e.stopPropagation(); onDuplicate(id) }}
              className="w-6 h-6 rounded bg-gray-800/80 hover:bg-gray-700 flex items-center justify-center text-gray-400 hover:text-gray-200 transition-colors"
              title="Duplicate"
            >
              <Copy className="w-3 h-3" />
            </button>
          )}
          {onDelete && (
            <button
              onClick={(e) => { e.stopPropagation(); onDelete(id) }}
              className="w-6 h-6 rounded bg-red-900/50 hover:bg-red-800 flex items-center justify-center text-red-400 hover:text-red-200 transition-colors"
              title="Delete"
            >
              <Trash2 className="w-3 h-3" />
            </button>
          )}
        </div>
        
        {/* Play button for testing */}
        {data.status === 'configured' && isHovered && (
          <button
            className={`
              absolute -right-3 top-1/2 -translate-y-1/2 
              w-7 h-7 rounded-full flex items-center justify-center
              bg-green-600 hover:bg-green-500 text-white shadow-lg
              transition-all duration-300 transform
              hover:scale-110 hover:shadow-green-500/50
            `}
            title="Test this template"
          >
            <Play className="w-3.5 h-3.5 ml-0.5" />
          </button>
        )}
      </div>
      
      {/* Input handles (left side) */}
      {data.inputs?.map((input, index) => (
        <Handle
          key={input.id}
          type="target"
          position={Position.Left}
          id={input.id}
          className={`
            !w-3 !h-3 !border-2 !border-gray-500 !bg-gray-700
            hover:!bg-gray-500 hover:!scale-125
            transition-all duration-200
            ${input.required ? '!border-orange-400' : ''}
          `}
          style={{
            top: `${30 + (index * 30)}px`,
          }}
          title={`${input.name}${input.required ? ' (required)' : ''}`}
        />
      ))}
      
      {/* Default input handle if no inputs defined */}
      {(!data.inputs || data.inputs.length === 0) && (
        <Handle
          type="target"
          position={Position.Left}
          className={`
            !w-3 !h-3 !border-2 !border-gray-500 !bg-gray-700
            hover:!bg-gray-500 hover:!scale-125
            transition-all duration-200
          `}
          style={{ top: '50%' }}
        />
      )}
      
      {/* Output handles (right side) */}
      {data.outputs?.map((output, index) => (
        <Handle
          key={output.id}
          type="source"
          position={Position.Right}
          id={output.id}
          className={`
            !w-3 !h-3 !border-2 !border-gray-500 !bg-gray-700
            hover:!bg-blue-400 hover:!border-blue-400 hover:!scale-125
            transition-all duration-200
          `}
          style={{
            top: `${30 + (index * 30)}px`,
            backgroundColor: category.accentColor,
            borderColor: category.accentColor,
          }}
          title={output.name}
        />
      ))}
      
      {/* Default output handle if no outputs defined */}
      {(!data.outputs || data.outputs.length === 0) && (
        <Handle
          type="source"
          position={Position.Right}
          className={`
            !w-3 !h-3 !border-2 !bg-gray-700
            hover:!scale-125 transition-all duration-200
          `}
          style={{ 
            top: '50%',
            backgroundColor: category.accentColor,
            borderColor: category.accentColor,
          }}
        />
      )}
      
      {/* Connection lines glow effect */}
      <style>{`
        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(400%); }
        }
      `}</style>
    </div>
  )
})

TemplateNode.displayName = 'TemplateNode'

export default TemplateNode

