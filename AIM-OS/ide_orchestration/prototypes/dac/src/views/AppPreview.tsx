// App Preview View - Hacker-Style Minimalist Design
// Cool, simple browser preview with hacker aesthetic

import React, { useState, useEffect, useCallback } from 'react'
import { Globe, Server, RefreshCw, Power } from 'lucide-react'

interface AppProcess {
  pid: number
  port: number
  command: string
  startedAt: Date
}

interface AppPreviewProps {
  onClose?: () => void
}

export const AppPreview: React.FC<AppPreviewProps> = ({ onClose }) => {
  const [port, setPort] = useState<number | null>(3002) // Default demo port
  const [processes, setProcesses] = useState<AppProcess[]>([])
  const [isRunning, setIsRunning] = useState(true) // Always show demo app
  
  // Initialize with demo app running
  useEffect(() => {
    setIsRunning(true)
    setPort(3002)
    setProcesses([{
      pid: Math.floor(Math.random() * 10000),
      port: 3002,
      command: 'demo app (port 3002)',
      startedAt: new Date()
    }])
  }, [])
  
  // Safe shutdown handler
  const handleShutdown = useCallback(async () => {
    if (!isRunning || processes.length === 0) {
      if (onClose) {
        onClose()
      }
      return
    }
    
    try {
      for (const process of processes) {
        console.log(`[TERMINATE] PID ${process.pid} on port ${process.port}`)
        try {
          await fetch(`http://localhost:${process.port}`, {
            method: 'HEAD',
            signal: AbortSignal.timeout(500)
          })
        } catch (err) {
          // Server might already be down
        }
      }
      
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      setProcesses([])
      setIsRunning(false)
      setPort(null)
      setPreviewUrl('')
      
      if (onClose) {
        onClose()
      }
    } catch (err) {
      console.error('[ERROR] Shutdown failed:', err)
      if (onClose) {
        onClose()
      }
    }
  }, [isRunning, processes, onClose])
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (isRunning && processes.length > 0) {
        handleShutdown()
      }
    }
  }, [isRunning, processes, handleShutdown])
  
  return (
    <div className="h-full flex flex-col bg-black text-green-400 font-mono relative overflow-hidden">
      {/* Hacker-style Header */}
      <div className="px-4 py-2 border-b border-green-900/50 flex items-center justify-between bg-black/80 backdrop-blur-sm">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
            <span className="text-xs font-bold tracking-wider">PREVIEW</span>
          </div>
          {port && (
            <span className="text-xs px-2 py-0.5 border border-green-500/50 bg-green-500/10">
              PORT:{port}
            </span>
          )}
          {isRunning && (
            <span className="text-xs text-green-500/70">
              [ACTIVE]
            </span>
          )}
        </div>
        
        <div className="flex items-center gap-2">
          {isRunning && (
            <>
              <button
                onClick={() => window.location.reload()}
                className="px-2 py-1 text-xs border border-green-500/50 bg-green-500/10 hover:bg-green-500/20 transition-colors"
                title="Refresh"
              >
                <RefreshCw className="w-3 h-3 inline" />
              </button>
            </>
          )}
          {onClose && (
            <button
              onClick={handleShutdown}
              className="px-2 py-1 text-xs border border-red-500/50 bg-red-500/10 hover:bg-red-500/20 text-red-400 transition-colors"
              title="Terminate"
            >
              <Power className="w-3 h-3 inline" />
            </button>
          )}
        </div>
      </div>
      
      {/* Preview Content with Hacker Aesthetic */}
      <div className="flex-1 overflow-hidden relative bg-black">
        {/* Simple Hacker-Style Demo App */}
        <div className="w-full h-full relative z-0 bg-black text-green-400 font-mono overflow-auto">
          <div className="p-8 space-y-6">
            {/* Header */}
            <div className="border-b border-green-500/30 pb-4">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse"></div>
                <h1 className="text-2xl font-bold tracking-wider">DEMO APP</h1>
                <span className="text-xs px-2 py-0.5 border border-green-500/50 bg-green-500/10">
                  v1.0.0
                </span>
              </div>
              <div className="text-xs text-green-500/70">
                [SYSTEM ONLINE] [PORT:{port}] [STATUS:ACTIVE]
              </div>
            </div>
            
            {/* Stats Grid */}
            <div className="grid grid-cols-3 gap-4">
              {[
                { label: 'REQUESTS', value: '1,247', unit: '' },
                { label: 'UPTIME', value: '2h', unit: '34m' },
                { label: 'MEMORY', value: '128', unit: 'MB' },
              ].map((stat, idx) => (
                <div key={idx} className="border border-green-500/30 bg-green-500/5 p-4">
                  <div className="text-xs text-green-500/70 mb-1">{stat.label}</div>
                  <div className="text-xl font-bold">
                    {stat.value} <span className="text-sm text-green-500/70">{stat.unit}</span>
                  </div>
                </div>
              ))}
            </div>
            
            {/* Terminal Output */}
            <div className="border border-green-500/30 bg-black/50 p-4">
              <div className="text-xs text-green-500/70 mb-2">[TERMINAL OUTPUT]</div>
              <div className="space-y-1 text-xs font-mono">
                {[
                  '> Initializing system...',
                  '> Loading modules...',
                  '> [OK] Database connected',
                  '> [OK] API server ready',
                  '> [OK] Cache initialized',
                  '> System ready for requests',
                ].map((line, idx) => (
                  <div key={idx} className="text-green-400">
                    {line}
                  </div>
                ))}
              </div>
            </div>
            
            {/* Activity Log */}
            <div className="border border-green-500/30 bg-black/50 p-4">
              <div className="text-xs text-green-500/70 mb-2">[ACTIVITY LOG]</div>
              <div className="space-y-1 text-xs">
                {[
                  { time: '14:23:45', event: 'User connected', status: 'OK' },
                  { time: '14:23:47', event: 'Data fetch', status: 'OK' },
                  { time: '14:23:50', event: 'Cache hit', status: 'OK' },
                  { time: '14:23:52', event: 'Response sent', status: 'OK' },
                ].map((log, idx) => (
                  <div key={idx} className="flex items-center gap-3 text-green-400">
                    <span className="text-green-500/50 font-mono">{log.time}</span>
                    <span>{log.event}</span>
                    <span className="text-green-500/70">[{log.status}]</span>
                  </div>
                ))}
              </div>
            </div>
            
            {/* Footer */}
            <div className="border-t border-green-500/30 pt-4 text-xs text-green-500/50 text-center">
              [DEMO APPLICATION] [HACKER STYLE UI] [PORT {port}]
            </div>
          </div>
        </div>
      </div>
      
      {/* Bottom Status Bar - Hacker Style */}
      <div className="px-4 py-1 border-t border-green-900/50 bg-black/80 backdrop-blur-sm text-xs flex items-center justify-between">
        <div className="flex items-center gap-4">
          <span className="text-green-500/70">
            STATUS: <span className={isRunning ? 'text-green-400' : 'text-red-400'}>
              {isRunning ? 'ACTIVE' : 'INACTIVE'}
            </span>
          </span>
          {port && (
            <span className="text-green-500/70">
              URL: <span className="text-green-400">localhost:{port}</span>
            </span>
          )}
        </div>
        <div className="text-green-500/50">
          [{new Date().toLocaleTimeString()}]
        </div>
      </div>
    </div>
  )
}
