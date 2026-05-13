// Panel Preview Component - Renders mini UI preview of a panel
import React from 'react'
import { PanelDefinition } from '../utils/panelRegistry'

interface PanelPreviewProps {
  panelId: string
  panelName: string
  category: string
  status: string
  hasErrors: boolean
  errorCount: number
  renderCount: number
  mountCount: number
  estimatedMemoryMB: number
  loadTime?: number
  onClick?: () => void
  isSelected?: boolean
}

export const PanelPreview: React.FC<PanelPreviewProps> = ({
  panelId,
  panelName,
  category,
  status,
  hasErrors,
  errorCount,
  renderCount,
  mountCount,
  estimatedMemoryMB,
  loadTime,
  onClick,
  isSelected
}) => {
  const getCategoryColor = (cat: string) => {
    switch (cat) {
      case 'left': return 'border-blue-500/50 bg-blue-900/10'
      case 'right': return 'border-purple-500/50 bg-purple-900/10'
      case 'bottom': return 'border-green-500/50 bg-green-900/10'
      case 'main': return 'border-yellow-500/50 bg-yellow-900/10'
      case 'view': return 'border-orange-500/50 bg-orange-900/10'
      default: return 'border-gray-500/50 bg-gray-900/10'
    }
  }

  const getStatusColor = (stat: string) => {
    switch (stat) {
      case 'mounted': return 'bg-green-500/20 text-green-400 border-green-500/30'
      case 'cached': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
      case 'loading': return 'bg-blue-500/20 text-blue-400 border-blue-500/30'
      case 'error': return 'bg-red-500/20 text-red-400 border-red-500/30'
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30'
    }
  }

  // Generate a visual preview based on panel type
  const renderPreview = () => {
    // Create a mini representation of the panel UI
    return (
      <div className="w-full h-20 bg-gray-900 rounded border border-gray-700 overflow-hidden relative">
        {/* Panel-specific preview patterns */}
        {category === 'left' && (
          <div className="p-1.5 space-y-1">
            <div className="h-1.5 bg-gray-700 rounded w-3/4"></div>
            <div className="h-1.5 bg-gray-700 rounded w-1/2"></div>
            <div className="h-1.5 bg-gray-700 rounded w-5/6"></div>
            <div className="h-1.5 bg-gray-700 rounded w-2/3"></div>
            <div className="h-1.5 bg-gray-700 rounded w-4/5"></div>
          </div>
        )}
        {category === 'right' && (
          <div className="p-1.5 space-y-1">
            <div className="h-2 bg-gray-700 rounded"></div>
            <div className="h-2 bg-gray-700 rounded w-4/5"></div>
            <div className="h-2 bg-gray-700 rounded w-3/5"></div>
            <div className="h-2 bg-gray-700 rounded w-2/3"></div>
          </div>
        )}
        {category === 'bottom' && (
          <div className="p-1.5 flex items-center gap-1">
            <div className="h-3 bg-gray-700 rounded flex-1"></div>
            <div className="h-3 bg-gray-700 rounded flex-1"></div>
            <div className="h-3 bg-gray-700 rounded flex-1"></div>
          </div>
        )}
        {(category === 'main' || category === 'view') && (
          <div className="p-1.5">
            <div className="h-2.5 bg-gray-700 rounded mb-1"></div>
            <div className="h-2.5 bg-gray-700 rounded mb-1 w-5/6"></div>
            <div className="h-2.5 bg-gray-700 rounded w-4/6 mb-1"></div>
            <div className="h-2.5 bg-gray-700 rounded w-3/4"></div>
          </div>
        )}
        
        {/* Status overlay indicators */}
        {hasErrors && (
          <div className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full border border-red-700 shadow-sm"></div>
        )}
        {status === 'mounted' && (
          <div className="absolute top-1 left-1 w-2 h-2 bg-green-500 rounded-full border border-green-700 shadow-sm"></div>
        )}
        {status === 'cached' && (
          <div className="absolute top-1 left-1 w-2 h-2 bg-yellow-500 rounded-full border border-yellow-700 shadow-sm"></div>
        )}
        
        {/* Loading indicator */}
        {status === 'loading' && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-900/80">
            <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          </div>
        )}
      </div>
    )
  }

  return (
    <div
      onClick={onClick}
      className={`p-3 rounded-lg border-2 cursor-pointer transition-all ${
        isSelected 
          ? `${getCategoryColor(category)} border-opacity-100 shadow-lg scale-[1.02]` 
          : `${getCategoryColor(category)} border-opacity-50 hover:border-opacity-75 hover:shadow-md`
      }`}
    >
      {/* Preview */}
      <div className="mb-2">
        {renderPreview()}
      </div>
      
      {/* Panel Info */}
      <div className="space-y-1.5">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-semibold text-gray-200 truncate flex-1">{panelName}</h3>
          <span className={`px-1.5 py-0.5 rounded text-[9px] font-medium ${getStatusColor(status)}`}>
            {status}
          </span>
        </div>
        
        <div className="flex items-center gap-2 text-[10px] text-gray-400">
          <span className="truncate">{panelId}</span>
          {hasErrors && (
            <span className="px-1 py-0.5 bg-red-900/50 text-red-300 rounded text-[9px]">
              {errorCount}
            </span>
          )}
        </div>
        
        {/* Quick Metrics */}
        <div className="grid grid-cols-3 gap-1 text-[9px] text-gray-500 pt-1 border-t border-gray-800">
          <div className="text-center">
            <div className="font-medium text-gray-400">{renderCount}</div>
            <div className="text-[8px]">renders</div>
          </div>
          <div className="text-center">
            <div className="font-medium text-gray-400">{mountCount}</div>
            <div className="text-[8px]">mounts</div>
          </div>
          <div className="text-center">
            <div className="font-medium text-gray-400">{estimatedMemoryMB}MB</div>
            <div className="text-[8px]">memory</div>
          </div>
        </div>
      </div>
    </div>
  )
}

