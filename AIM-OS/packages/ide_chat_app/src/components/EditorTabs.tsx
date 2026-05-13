import React from 'react'
import { X, Pin, PinOff } from 'lucide-react'
import { useEditorStore } from '../store/editorStore'

export const EditorTabs: React.FC = () => {
  const { tabs, activeTabId, setActiveTab, closeTab, togglePinTab } = useEditorStore()

  const handleCloseTab = (e: React.MouseEvent, tabId: string) => {
    e.stopPropagation()
    closeTab(tabId)
  }

  const handlePinTab = (e: React.MouseEvent, tabId: string) => {
    e.stopPropagation()
    togglePinTab(tabId)
  }

  if (tabs.length === 0) {
    return null
  }

  return (
    <div className="flex items-end bg-gray-900 border-b border-gray-700 overflow-x-auto">
      {tabs.map((tab) => {
        const isActive = tab.id === activeTabId
        const displayName = tab.fileName.split('/').pop() || tab.fileName

        return (
          <div
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`
              relative flex items-center gap-2 px-4 py-2 cursor-pointer
              border-b-2 transition-colors group
              ${isActive 
                ? 'bg-gray-800 border-blue-500' 
                : 'bg-gray-900 border-transparent hover:bg-gray-850'
              }
            `}
            style={{ minWidth: '120px', maxWidth: '200px' }}
          >
            {/* Pin Icon */}
            <button
              onClick={(e) => handlePinTab(e, tab.id)}
              className="opacity-0 group-hover:opacity-100 transition-opacity"
              title={tab.isPinned ? 'Unpin' : 'Pin'}
            >
              {tab.isPinned ? (
                <Pin className="w-3 h-3 text-yellow-400" />
              ) : (
                <PinOff className="w-3 h-3 text-gray-500" />
              )}
            </button>

            {/* Tab Name */}
            <span 
              className={`
                truncate flex-1 text-sm
                ${isActive ? 'text-gray-100' : 'text-gray-400'}
                ${tab.isDirty ? 'italic' : ''}
              `}
              title={tab.fileName}
            >
              {displayName}
            </span>

            {/* Dirty Indicator */}
            {tab.isDirty && (
              <span className="w-2 h-2 rounded-full bg-blue-500" />
            )}

            {/* Close Button */}
            <button
              onClick={(e) => handleCloseTab(e, tab.id)}
              className="opacity-0 group-hover:opacity-100 transition-opacity hover:bg-gray-700 rounded p-0.5"
              title="Close"
            >
              <X className="w-4 h-4 text-gray-400" />
            </button>

            {/* Active Indicator */}
            {isActive && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-500" />
            )}
          </div>
        )
      })}
    </div>
  )
}
