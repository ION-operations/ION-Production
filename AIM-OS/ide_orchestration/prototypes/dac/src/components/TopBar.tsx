// Top Bar Component
// VSCode-style menu bar, command palette, agent status, confidence indicators, layout management

import React, { useState, useEffect, useRef } from 'react'
import { LayoutManager } from './LayoutManager'
import { PanelPresets } from './PanelPresets'
import { PanelCustomization } from './PanelCustomization'
import { MenuBar } from './MenuBar'
import { ViteCacheService } from '../services/ViteCacheService'
import { Activity, Database, Brain, Layout as LayoutIcon, Settings, ChevronUp, ChevronDown, X, Code, FileText, GitBranch, Globe, Network, Eye, MessageSquare, User, LogOut, Bell, HelpCircle, PanelLeftClose, PanelLeftOpen, PanelRightClose, PanelRightOpen, PanelBottomClose, PanelBottomOpen, RefreshCw, Server } from 'lucide-react'

type MainViewType = 'code' | 'evolution' | 'consciousness' | 'orchestration' | 'app-preview' | 'document-editor' | 'file-preview' | 'canvas' | 'manager-ai-chat' | 'backend-design'

interface OpenFile {
  id: string
  path: string
  name: string
  openedAt: Date
  commit?: string
  isGitVersion?: boolean
}

interface TopBarProps {
  cmcStats: any
  casMetrics: any
  topPanelOpen: boolean
  onTopPanelToggle: () => void
  mainView?: MainViewType
  onMainViewChange?: (view: MainViewType) => void
  openFiles?: OpenFile[]
  activeFileId?: string
  onFileSelect?: (fileId: string) => void
  onFileClose?: (fileId: string, e: React.MouseEvent) => void
  leftPanelRightEdge?: number
  rightPanelLeftEdge?: number
  rightPanelOpen?: boolean
  onSaveLayout?: (view: MainViewType, name?: string) => void
  onRestoreLayout?: (panelState: any) => void
  // Panel toggle handlers
  leftPanelOpen?: boolean
  rightPanelOpen?: boolean
  bottomPanelOpen?: boolean
  onLeftPanelToggle?: () => void
  onRightPanelToggle?: () => void
  onBottomPanelToggle?: () => void
  // Account handlers
  onAccountClick?: () => void
  onSignOut?: () => void
  userName?: string
}

export const TopBar: React.FC<TopBarProps> = ({
  cmcStats,
  casMetrics,
  topPanelOpen,
  onTopPanelToggle,
  mainView,
  onMainViewChange,
  openFiles = [],
  activeFileId,
  onFileSelect,
  onFileClose,
  leftPanelRightEdge = 48,
  rightPanelLeftEdge,
  rightPanelOpen = true,
  onSaveLayout,
  onRestoreLayout,
  leftPanelOpen = true,
  rightPanelOpen: rightPanelOpenProp = true,
  bottomPanelOpen = true,
  onLeftPanelToggle,
  onRightPanelToggle,
  onBottomPanelToggle,
  onAccountClick,
  onSignOut,
  userName,
}) => {
  const [showPresets, setShowPresets] = useState(false)
  const [showCustomization, setShowCustomization] = useState(false)
  const menuBarRef = useRef<HTMLDivElement>(null)
  const topBarRef = useRef<HTMLDivElement>(null)
  const rightControlsRef = useRef<HTMLDivElement>(null)
  const mainViewButtonsRef = useRef<HTMLDivElement>(null)
  const [relativeDividerPosition, setRelativeDividerPosition] = useState<number>(32) // Divider position relative to top bar
  const [rightControlsWidth, setRightControlsWidth] = useState<number>(300) // Width of right controls
  const [useIcons, setUseIcons] = useState(false) // Whether to show icons instead of text
  const [showCacheMenu, setShowCacheMenu] = useState(false)
  const [cacheInfo, setCacheInfo] = useState<any>(null)
  const [isClearingCache, setIsClearingCache] = useState(false)
  
  // Main view buttons configuration
  const mainViewButtons: Array<{ id: MainViewType; icon: React.ComponentType<{ className?: string }>; label: string }> = [
    { id: 'code', icon: Code, label: 'Code' },
    { id: 'file-preview', icon: Eye, label: 'Preview' },
    { id: 'canvas', icon: FileText, label: 'Canvas' },
    { id: 'manager-ai-chat', icon: MessageSquare, label: 'AI Chat' },
    { id: 'document-editor', icon: FileText, label: 'Document' },
    { id: 'evolution', icon: GitBranch, label: 'Evolution' },
    { id: 'consciousness', icon: Brain, label: 'Consciousness' },
    { id: 'orchestration', icon: Network, label: 'Orchestration' },
    { id: 'app-preview', icon: Globe, label: 'App' },
    { id: 'backend-design', icon: Server, label: 'Backend' },
  ]
  
  // Check if we should use icons based on available width
  useEffect(() => {
    const checkWidth = () => {
      if (!topBarRef.current || !mainViewButtonsRef.current || !rightControlsRef.current) return
      
      const topBarWidth = topBarRef.current.offsetWidth
      const menuBarWidth = menuBarRef.current?.offsetWidth || 0
      const rightControlsWidth = rightControlsRef.current.offsetWidth
      const dividerPosition = relativeDividerPosition + 32 // Divider + toggle button
      const availableWidth = topBarWidth - menuBarWidth - dividerPosition - rightControlsWidth - 16 // padding
      
      // Calculate minimum width needed for text buttons
      const textButtonWidth = 80 // Approximate width per text button
      const iconButtonWidth = 28 // Approximate width per icon button
      const textButtonsWidth = mainViewButtons.length * textButtonWidth
      const iconButtonsWidth = mainViewButtons.length * iconButtonWidth
      
      setUseIcons(availableWidth < textButtonsWidth && availableWidth >= iconButtonsWidth)
    }
    
    checkWidth()
    window.addEventListener('resize', checkWidth)
    return () => window.removeEventListener('resize', checkWidth)
  }, [relativeDividerPosition, rightControlsWidth])
  
  // Load cache info when menu opens
  useEffect(() => {
    if (showCacheMenu) {
      loadCacheInfo()
    }
  }, [showCacheMenu])
  
  const loadCacheInfo = async () => {
    const info = await ViteCacheService.getCacheInfo()
    setCacheInfo(info)
  }
  
  const handleClearCache = async (types: 'build' | 'deps' | 'all' = 'all') => {
    setIsClearingCache(true)
    try {
      const result = await ViteCacheService.clearCache({ types })
      if (result.success) {
        // Reload cache info
        await loadCacheInfo()
        // Show success message (could use toast notification)
        console.log(`Cache cleared: ${result.cleared?.join(', ')}. Freed: ${ViteCacheService.formatBytes(result.freed || 0)}`)
      } else {
        console.error('Failed to clear cache:', result.error)
      }
    } finally {
      setIsClearingCache(false)
    }
  }
  
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
  
  // Measure right controls width
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
        
        {/* Main View Buttons - Between divider and right controls */}
        {onMainViewChange && (
          <div 
            ref={mainViewButtonsRef}
            className="absolute top-0 bottom-0 flex items-center gap-1 px-2 z-20"
            style={{
              left: `${Math.max(32, Math.min(relativeDividerPosition + 32, window.innerWidth - 400))}px`,
              right: rightPanelOpen && rightPanelLeftEdge ? `${window.innerWidth - rightPanelLeftEdge + rightControlsWidth}px` : `${rightControlsWidth}px`
            }}
          >
            {mainViewButtons.map((btn) => {
              const Icon = btn.icon
              const isActive = mainView === btn.id
              return (
                <button
                  key={btn.id}
                  onClick={() => onMainViewChange(btn.id)}
                  className={`px-2 py-1 rounded text-xs transition-colors flex items-center gap-1 ${
                    isActive
                      ? 'bg-gray-800 text-gray-100' 
                      : 'text-gray-400 hover:bg-gray-900 hover:text-gray-300'
                  }`}
                  title={btn.label}
                >
                  {useIcons ? (
                    <Icon className="w-3 h-3" />
                  ) : (
                    <>
                      <Icon className="w-3 h-3" />
                      <span className="whitespace-nowrap">{btn.label}</span>
                    </>
                  )}
                </button>
              )
            })}
          </div>
        )}
        
        {/* Divider - Aligns with right panel left edge */}
        {rightPanelOpen && rightPanelLeftEdge && (
          <div 
            className="absolute top-0 bottom-0 w-px bg-gray-800 transition-all duration-200 z-30"
            style={{
              left: `${Math.max(leftPanelRightEdge || 32, Math.min(rightPanelLeftEdge, window.innerWidth - 50))}px`
            }}
          />
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
          
          <LayoutManager 
            currentView={mainView || 'code'}
            onSaveLayout={onSaveLayout}
            onRestoreLayout={onRestoreLayout}
          />
          
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
          
          {/* Cache Management */}
          <div className="relative">
            <button
              onClick={() => setShowCacheMenu(!showCacheMenu)}
              className="p-1 hover:bg-gray-900 rounded text-gray-400 hover:text-gray-100 transition-colors"
              title="Clear Vite Cache"
              disabled={isClearingCache}
            >
              <RefreshCw className={`w-3 h-3 ${isClearingCache ? 'animate-spin' : ''}`} />
            </button>
            {showCacheMenu && (
              <div className="absolute top-full right-0 mt-1 z-50 w-64 bg-gray-800 border border-gray-700 rounded-lg shadow-xl">
                <div className="p-3">
                  <div className="text-xs font-semibold text-gray-300 mb-2">Vite Cache</div>
                  {cacheInfo ? (
                    <>
                      <div className="text-xs text-gray-400 mb-3 space-y-1">
                        <div>Build: {ViteCacheService.formatBytes(cacheInfo.buildCache.size)}</div>
                        <div>Deps: {ViteCacheService.formatBytes(cacheInfo.depsCache.size)}</div>
                        <div className="pt-1 border-t border-gray-700">Total: {ViteCacheService.formatBytes(cacheInfo.totalSize)}</div>
                      </div>
                      <div className="space-y-1">
                        <button
                          onClick={() => handleClearCache('all')}
                          disabled={isClearingCache}
                          className="w-full px-2 py-1.5 text-xs text-left text-gray-400 hover:bg-gray-700 hover:text-gray-200 rounded flex items-center gap-2 disabled:opacity-50"
                        >
                          <RefreshCw className={`w-3 h-3 ${isClearingCache ? 'animate-spin' : ''}`} />
                          Clear All Caches
                        </button>
                        <button
                          onClick={() => handleClearCache('build')}
                          disabled={isClearingCache}
                          className="w-full px-2 py-1.5 text-xs text-left text-gray-400 hover:bg-gray-700 hover:text-gray-200 rounded flex items-center gap-2 disabled:opacity-50"
                        >
                          <RefreshCw className={`w-3 h-3 ${isClearingCache ? 'animate-spin' : ''}`} />
                          Clear Build Cache
                        </button>
                        <button
                          onClick={() => handleClearCache('deps')}
                          disabled={isClearingCache}
                          className="w-full px-2 py-1.5 text-xs text-left text-gray-400 hover:bg-gray-700 hover:text-gray-200 rounded flex items-center gap-2 disabled:opacity-50"
                        >
                          <RefreshCw className={`w-3 h-3 ${isClearingCache ? 'animate-spin' : ''}`} />
                          Clear Dependencies Cache
                        </button>
                      </div>
                    </>
                  ) : (
                    <div className="text-xs text-gray-500">Loading cache info...</div>
                  )}
                  <button
                    onClick={() => setShowCacheMenu(false)}
                    className="mt-2 w-full px-2 py-1 text-xs text-gray-500 hover:text-gray-300"
                  >
                    Close
                  </button>
                </div>
              </div>
            )}
          </div>
          
          {/* Panel Toggle Buttons */}
          {onLeftPanelToggle && (
            <button
              onClick={onLeftPanelToggle}
              className={`w-6 h-6 rounded flex items-center justify-center transition-colors ${
                leftPanelOpen
                  ? 'bg-gray-800 text-gray-100' 
                  : 'text-gray-400 hover:bg-gray-800 hover:text-gray-200'
              }`}
              title={leftPanelOpen ? "Hide Left Panel" : "Show Left Panel"}
            >
              {leftPanelOpen ? (
                <PanelLeftClose className="w-3.5 h-3.5" />
              ) : (
                <PanelLeftOpen className="w-3.5 h-3.5" />
              )}
            </button>
          )}
          
          {onBottomPanelToggle && (
            <button
              onClick={onBottomPanelToggle}
              className={`w-6 h-6 rounded flex items-center justify-center transition-colors ${
                bottomPanelOpen
                  ? 'bg-gray-800 text-gray-100' 
                  : 'text-gray-400 hover:bg-gray-800 hover:text-gray-200'
              }`}
              title={bottomPanelOpen ? "Hide Bottom Panel" : "Show Bottom Panel"}
            >
              {bottomPanelOpen ? (
                <PanelBottomClose className="w-3.5 h-3.5" />
              ) : (
                <PanelBottomOpen className="w-3.5 h-3.5" />
              )}
            </button>
          )}
          
          {onRightPanelToggle && (
            <button
              onClick={onRightPanelToggle}
              className={`w-6 h-6 rounded flex items-center justify-center transition-colors ${
                rightPanelOpenProp
                  ? 'bg-gray-800 text-gray-100' 
                  : 'text-gray-400 hover:bg-gray-800 hover:text-gray-200'
              }`}
              title={rightPanelOpenProp ? "Hide Right Panel" : "Show Right Panel"}
            >
              {rightPanelOpenProp ? (
                <PanelRightClose className="w-3.5 h-3.5" />
              ) : (
                <PanelRightOpen className="w-3.5 h-3.5" />
              )}
            </button>
          )}
          
          {/* Divider */}
          <div className="w-px h-4 bg-gray-700 mx-1" />
          
          {/* Notifications */}
          <button
            className="p-1 hover:bg-gray-900 rounded text-gray-400 hover:text-gray-100 transition-colors relative"
            title="Notifications"
          >
            <Bell className="w-3.5 h-3.5" />
            {/* Notification badge - can be conditionally shown */}
            {/* <span className="absolute top-0 right-0 w-1.5 h-1.5 bg-red-500 rounded-full" /> */}
          </button>
          
          {/* Help */}
          <button
            className="p-1 hover:bg-gray-900 rounded text-gray-400 hover:text-gray-100 transition-colors"
            title="Help & Documentation"
          >
            <HelpCircle className="w-3.5 h-3.5" />
          </button>
          
          {/* Account Menu */}
          <div className="relative group">
            <button
              onClick={onAccountClick}
              className="p-1 hover:bg-gray-900 rounded text-gray-400 hover:text-gray-100 transition-colors flex items-center gap-1.5"
              title={userName || "Account"}
            >
              <User className="w-3.5 h-3.5" />
              {userName && (
                <span className="text-[10px] text-gray-300">{userName}</span>
              )}
            </button>
            
            {/* Account Dropdown - shown on hover/click */}
            {onAccountClick && (
              <div className="absolute top-full right-0 mt-1 w-48 bg-gray-800 border border-gray-700 rounded-lg shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-50">
                <div className="p-2">
                  {userName && (
                    <div className="px-2 py-1.5 text-xs text-gray-300 border-b border-gray-700 mb-1">
                      {userName}
                    </div>
                  )}
                  <button
                    onClick={onSignOut}
                    className="w-full px-2 py-1.5 text-xs text-left text-gray-400 hover:bg-gray-700 hover:text-gray-200 rounded flex items-center gap-2"
                  >
                    <LogOut className="w-3 h-3" />
                    Sign Out
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

