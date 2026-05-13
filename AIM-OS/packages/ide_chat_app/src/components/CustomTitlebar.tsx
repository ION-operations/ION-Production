import React, { useState, useEffect } from 'react'
import { Minimize2, Maximize2, X, Square } from 'lucide-react'

interface CustomTitlebarProps {
  title?: string
}

declare global {
  interface Window {
    windowControls?: {
      minimize: () => Promise<{ success: boolean }>
      maximize: () => Promise<{ success: boolean; isMaximized?: boolean }>
      close: () => Promise<{ success: boolean }>
      isMaximized: () => Promise<{ success: boolean; isMaximized?: boolean }>
      onMaximizeChange?: (callback: (isMaximized: boolean) => void) => void
    }
  }
}

export const CustomTitlebar: React.FC<CustomTitlebarProps> = ({ title = 'AIM-OS Dashboard' }) => {
  const [isMaximized, setIsMaximized] = useState(false)
  const [hasWindowControls, setHasWindowControls] = useState(false)

  useEffect(() => {
    // Debug: Check if windowControls is available
    const hasControls = typeof window !== 'undefined' && window.windowControls !== undefined
    setHasWindowControls(hasControls)
    console.log('[CustomTitlebar] ✅ Component mounted')
    console.log('[CustomTitlebar] windowControls available:', hasControls)
    console.log('[CustomTitlebar] DOM element:', document.querySelector('[data-titlebar]'))

    // Check initial maximize state
    const checkMaximized = async () => {
      if (window.windowControls?.isMaximized) {
        const result = await window.windowControls.isMaximized()
        if (result.success) {
          setIsMaximized(result.isMaximized || false)
        }
      }
    }
    checkMaximized()

    // Listen for maximize changes
    if (window.windowControls?.onMaximizeChange) {
      window.windowControls.onMaximizeChange(setIsMaximized)
    }
  }, [])

  const handleMinimize = async () => {
    if (window.windowControls?.minimize) {
      await window.windowControls.minimize()
    }
  }

  const handleMaximize = async () => {
    if (window.windowControls?.maximize) {
      const result = await window.windowControls.maximize()
      if (result.success) {
        setIsMaximized(result.isMaximized || false)
      }
    }
  }

  const handleClose = async () => {
    if (window.windowControls?.close) {
      await window.windowControls.close()
    }
  }

  // Always render titlebar - if windowControls not available, show fallback
  return (
    <div
      data-titlebar="true"
      className={`h-10 border-b flex items-center justify-between px-4 select-none z-50 fixed top-0 left-0 right-0 ${
        hasWindowControls 
          ? 'bg-gray-900 border-gray-800' 
          : 'bg-red-900 border-red-600 border-b-2'
      }`}
      style={{
        WebkitAppRegion: hasWindowControls ? 'drag' : 'no-drag',
        appRegion: hasWindowControls ? 'drag' : 'no-drag',
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 9999,
        backgroundColor: hasWindowControls ? '#111827' : '#7f1d1d', // Force visible background
        width: '100%',
        height: '40px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      } as React.CSSProperties & { WebkitAppRegion?: string; appRegion?: string }}
    >
      {/* Title */}
      <div className={`flex items-center gap-2 text-sm font-medium ${
        hasWindowControls ? 'text-gray-300' : 'text-red-400'
      }`}>
        {hasWindowControls ? (
          <>
            <span className="text-blue-400 font-bold">🚀 AIM-OS</span>
            <span className="text-gray-500">|</span>
            <span>{title}</span>
          </>
        ) : (
          <>
            <span className="font-bold text-lg">⚠️ windowControls NOT AVAILABLE</span>
            <span className="text-red-300 text-xs">Check console</span>
          </>
        )}
      </div>

      {/* Window Controls */}
      {hasWindowControls ? (
        <div
          className="flex items-center gap-1"
          style={{
            WebkitAppRegion: 'no-drag',
            appRegion: 'no-drag'
          } as React.CSSProperties & { WebkitAppRegion?: string; appRegion?: string }}
        >
          {/* DevTools Button (Debug) */}
          <button
            onClick={() => {
              const win = window as any
              if (win.electronAPI?.invoke) {
                win.electronAPI.invoke('toggle-devtools')
              } else if (win.electron?.remote) {
                win.electron.remote.getCurrentWindow().webContents.toggleDevTools()
              }
            }}
            className="w-8 h-8 flex items-center justify-center hover:bg-gray-800 text-gray-400 hover:text-gray-200 transition-colors text-xs"
            title="Toggle DevTools (F12)"
          >
            🔧
          </button>
          
          {/* Minimize Button */}
          <button
            onClick={handleMinimize}
            className="w-10 h-10 flex items-center justify-center hover:bg-gray-800 text-gray-400 hover:text-gray-200 transition-colors"
            title="Minimize"
          >
            <Minimize2 className="w-4 h-4" />
          </button>

          {/* Maximize/Restore Button */}
          <button
            onClick={handleMaximize}
            className="w-10 h-10 flex items-center justify-center hover:bg-gray-800 text-gray-400 hover:text-gray-200 transition-colors"
            title={isMaximized ? 'Restore' : 'Maximize'}
          >
            {isMaximized ? (
              <Square className="w-3.5 h-3.5" />
            ) : (
              <Maximize2 className="w-4 h-4" />
            )}
          </button>

          {/* Close Button */}
          <button
            onClick={handleClose}
            className="w-10 h-10 flex items-center justify-center hover:bg-red-600 text-gray-400 hover:text-white transition-colors"
            title="Close"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      ) : (
        <div className="text-red-400 text-xs">Waiting for preload...</div>
      )}
    </div>
  )
}

