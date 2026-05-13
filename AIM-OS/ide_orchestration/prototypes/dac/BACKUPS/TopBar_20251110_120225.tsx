// Top Bar Component
// VSCode-style menu bar, command palette, agent status, confidence indicators, layout management

import React, { useState, useEffect, useRef } from 'react'
import { CommandPalette } from './CommandPalette'
import { LayoutManager } from './LayoutManager'
import { PanelPresets } from './PanelPresets'
import { PanelCustomization } from './PanelCustomization'
import { MenuBar } from './MenuBar'
import { Activity, Database, Brain, Layout as LayoutIcon, Settings, ChevronUp, ChevronDown, X } from 'lucide-react'

interface OpenFile {
  id: string
  path: string
  name: string
  openedAt: Date
}

interface TopBarProps {
  cmcStats: any
  casMetrics: any
  topPanelOpen: boolean
  onTopPanelToggle: () => void
  mainView?: 'code' | 'evolution' | 'consciousness' | 'orchestration' | 'app-preview'
  openFiles?: OpenFile[]
  activeFileId?: string
  onFileSelect?: (fileId: string) => void
  onFileClose?: (fileId: string, e: React.MouseEvent) => void
  showFileDropdown?: boolean
  onFileDropdownToggle?: () => void
  leftPanelRightEdge?: number
}

export const TopBar: React.FC<TopBarProps> = ({
  cmcStats,
  casMetrics,
  topPanelOpen,
  onTopPanelToggle,
  mainView,
  openFiles = [],
  activeFileId,
  onFileSelect,
  onFileClose,
  showFileDropdown = false,
  onFileDropdownToggle,
  leftPanelRightEdge = 48
}) => {
  const [showPresets, setShowPresets] = useState(false)
  const [showCustomization, setShowCustomization] = useState(false)
  const tabBarRef = useRef<HTMLDivElement>(null)
  const menuBarRef = useRef<HTMLDivElement>(null)
  const topBarRef = useRef<HTMLDivElement>(null)
  const rightControlsRef = useRef<HTMLDivElement>(null)
  const [relativeDividerPosition, setRelativeDividerPosition] = useState<number>(32) // Divider position relative to top bar
  const [rightControlsWidth, setRightControlsWidth] = useState<number>(300) // Width of right controls
  
  // Calculate divider position relative to top bar container - simplified, no minimum constraint
  useEffect(() => {
    const updateDividerPosition = () => {
      if (!topBarRef.current) {
        setRelativeDividerPosition(32)
        return
      }
      
      const topBarRect = topBarRef.current.getBoundingClientRect()
      const screenWidth = window.innerWidth
      
      // Clamp leftPanelRightEdge to reasonable values
      const clampedInput = Math.max(32, Math.min(leftPanelRightEdge || 32, screenWidth - 100))
      
      // Convert to relative coordinates (top bar might not start at x=0)
      const relativeEdge = clampedInput - topBarRect.left
      
      // Simple clamp: ensure it's within reasonable bounds
      const maxAllowed = screenWidth - 300 // Leave space for right controls
      const finalPosition = Math.max(32, Math.min(relativeEdge, maxAllowed))
      
      setRelativeDividerPosition(finalPosition)
    }
    
    updateDividerPosition()
    const interval = setInterval(updateDividerPosition, 50)
    window.addEventListener('resize', updateDividerPosition)
    
    return () => {
      clearInterval(interval)
      window.removeEventListener('resize', updateDividerPosition)
    }
  }, [leftPanelRightEdge])
  
  // Measure right controls width to prevent tabs from overlapping
  useEffect(() => {
    const updateRightControlsWidth = () => {
      if (rightControlsRef.current) {
        const width = rightControlsRef.current.offsetWidth
        setRightControlsWidth(width + 8) // Add some padding
      }
    }
    
    updateRightControlsWidth()
    const resizeObserver = new ResizeObserver(updateRightControlsWidth)
    if (rightControlsRef.current) {
      resizeObserver.observe(rightControlsRef.current)
    }
    
    window.addEventListener('resize', updateRightControlsWidth)
    
    return () => {
      resizeObserver.disconnect()
      window.removeEventListener('resize', updateRightControlsWidth)
    }
  }, [])
  
  // Close file dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (showFileDropdown && !(e.target as Element).closest('.file-dropdown-container')) {
        onFileDropdownToggle?.()
      }
    }
    if (showFileDropdown) {
      document.addEventListener('mousedown', handleClickOutside)
      return () => document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [showFileDropdown, onFileDropdownToggle])
  
  return (
    <div className="bg-gray-950 border-b border-gray-800 flex flex-col">
      {/* Main Top Bar */}
      <div ref={topBarRef} className="h-8 flex items-center relative">
        {/* VSCode-style Menu Bar */}
        <div ref={menuBarRef} data-menu-bar className="flex items-center h-full px-2 flex-shrink-0">
          <MenuBar />
        </div>
        
        {/* Divider - Aligns with left panel right edge */}
        <div 
          className="absolute top-0 bottom-0 w-px bg-gray-800 transition-all duration-200 z-30"
          style={{
            left: `${Math.max(32, Math.min(relativeDividerPosition, window.innerWidth - 400))}px`
          }}
        />
        
        {/* Top Panel Toggle Button - Anchored to right side of divider */}
          <button
          onClick={onTopPanelToggle}
          className={`absolute w-6 h-6 rounded flex items-center justify-center transition-colors z-30 ${
            topPanelOpen
              ? 'bg-gray-800 text-gray-100' 
              : 'text-gray-400 hover:bg-gray-800 hover:text-gray-200'
            }`}
          style={{
            left: `${Math.max(32, Math.min(relativeDividerPosition + 4, window.innerWidth - 400))}px`
          }}
          title={topPanelOpen ? "Hide Top Panel" : "Show Top Panel"}
        >
          {topPanelOpen ? (
            <ChevronUp className="w-4 h-4" />
          ) : (
            <ChevronDown className="w-4 h-4" />
          )}
        </button>
        
        {/* Tab Bar - Only shown when in code editor mode */}
        {mainView === 'code' && openFiles.length > 0 && (
          <div 
            ref={tabBarRef} 
            className="absolute top-0 bottom-0 left-0 flex items-center overflow-hidden pointer-events-none z-20"
            style={{
              paddingLeft: `${Math.max(32, Math.min(relativeDividerPosition + 32, window.innerWidth - 400))}px`,
              right: `${rightControlsWidth}px`
            }}
          >
            {/* Tab Container - Starts right after divider + button */}
            <div className="flex items-center gap-1 px-2 overflow-x-auto overflow-y-hidden pointer-events-auto">
              {openFiles.slice(0, 8).map((file) => {
                const isActive = activeFileId === file.id
                const timeAgo = Math.floor((Date.now() - file.openedAt.getTime()) / 1000 / 60)
                return (
                  <div
                    key={file.id}
                    onClick={() => onFileSelect?.(file.id)}
                    className={`flex items-center gap-1 px-2 py-1 rounded-t text-xs cursor-pointer transition-colors border-b-2 ${
                      isActive
                        ? 'bg-gray-900 text-gray-100 border-blue-500'
                        : 'bg-gray-950 text-gray-400 border-transparent hover:bg-gray-900 hover:text-gray-300'
            }`}
                    title={`${file.path} • Opened ${timeAgo}m ago`}
                  >
                    <span className="truncate max-w-[120px]">{file.name}</span>
                    {onFileClose && (
                      <button
                        onClick={(e) => onFileClose(file.id, e)}
                        className="ml-1 hover:bg-gray-800 rounded p-0.5 transition-colors"
                        title="Close"
                      >
                        <X className="w-3 h-3" />
          </button>
                    )}
                  </div>
                )
              })}
              {openFiles.length > 8 && (
                <div className="relative file-dropdown-container">
          <button
                    onClick={onFileDropdownToggle}
                    className="px-2 py-1 rounded-t text-xs bg-gray-950 text-gray-400 hover:bg-gray-900 hover:text-gray-300 border-b-2 border-transparent"
          >
                    +{openFiles.length - 8} more
          </button>
                  {showFileDropdown && (
                    <div className="absolute top-full left-0 mt-1 bg-gray-900 border border-gray-700 rounded shadow-lg z-50 max-h-64 overflow-y-auto min-w-[200px]">
                      {openFiles.slice(8).map((file) => {
                        const isActive = activeFileId === file.id
                        const timeAgo = Math.floor((Date.now() - file.openedAt.getTime()) / 1000 / 60)
                        return (
                          <div
                            key={file.id}
                            onClick={() => {
                              onFileSelect?.(file.id)
                              onFileDropdownToggle?.()
                            }}
                            className={`px-3 py-2 text-xs cursor-pointer hover:bg-gray-800 flex items-center justify-between ${
                              isActive ? 'bg-gray-800 text-gray-100' : 'text-gray-400'
            }`}
          >
                            <span className="truncate flex-1">{file.name}</span>
                            <span className="text-[10px] text-gray-500 ml-2">{timeAgo}m</span>
                          </div>
                        )
                      })}
                    </div>
                  )}
                </div>
              )}
        </div>
      </div>
        )}
      
        {/* Right side controls - Pushed to right edge */}
        <div ref={rightControlsRef} className="flex items-center justify-end gap-1 px-2 ml-auto relative z-40 bg-gray-950 flex-shrink-0">
        {/* Layout Management */}
        <div className="relative">
          <button
            onClick={() => setShowPresets(!showPresets)}
              className="p-1 hover:bg-gray-900 rounded text-gray-400 hover:text-gray-100 transition-colors flex items-center gap-1"
            title="Panel Presets"
          >
              <LayoutIcon className="w-3 h-3" />
          </button>
          {showPresets && (
              <div className="absolute top-full right-0 mt-1 z-50 w-80">
              <PanelPresets onClose={() => setShowPresets(false)} />
            </div>
          )}
        </div>
        
        <LayoutManager />
        
        {/* Panel Customization */}
        <button
          onClick={() => setShowCustomization(!showCustomization)}
            className="p-1 hover:bg-gray-900 rounded text-gray-400 hover:text-gray-100 transition-colors"
          title="Panel Customization"
        >
            <Settings className="w-3 h-3" />
        </button>
        {showCustomization && (
          <PanelCustomization onClose={() => setShowCustomization(false)} />
        )}
        
        {/* AIM-OS Status Indicators */}
        {cmcStats && (
            <div className="flex items-center gap-1 text-[10px] text-gray-400">
              <Database className="w-2.5 h-2.5" />
              <span>CMC: {cmcStats?.total_atoms || 0}</span>
          </div>
        )}
        
        {casMetrics && (
            <div className="flex items-center gap-1 text-[10px] text-gray-400">
              <Brain className="w-2.5 h-2.5" />
            <span>CAS: {casMetrics?.health || 'unknown'}</span>
          </div>
        )}
        
          <div className="flex items-center gap-1 text-[10px] text-gray-400">
            <Activity className="w-2.5 h-2.5" />
            <span>{casMetrics?.health === 'good' ? '🟢' : '🟡'}</span>
        </div>
        
          <div className="text-[10px] text-gray-500 font-medium">
          Port: 3002
        </div>
        
        <CommandPalette />
        </div>
      </div>
    </div>
  )
}

