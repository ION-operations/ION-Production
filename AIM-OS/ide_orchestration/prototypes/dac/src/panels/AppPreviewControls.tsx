// App Preview Controls Panel - Bottom Panel
// Browser console, port info, terminal, and cache management for app preview

import React, { useState, useEffect, useRef } from 'react'
import { BasePanel } from '../components/BasePanel'
import { 
  Globe, Server, Terminal, AlertCircle, 
  CheckCircle, XCircle, Info, Trash2,
  Database, HardDrive, RefreshCw, Power
} from 'lucide-react'

interface ConsoleMessage {
  id: string
  timestamp: Date
  level: 'log' | 'info' | 'warn' | 'error'
  message: string
  source?: string
}

interface PortInfo {
  port: number
  protocol: 'http' | 'https'
  status: 'active' | 'inactive'
  processId?: number
  startedAt?: Date
  uptime?: number
  requests?: number
  memoryUsage?: number
  cpuUsage?: number
}

interface CacheInfo {
  totalSize: number
  itemCount: number
  lastCleared?: Date
  items: Array<{
    url: string
    size: number
    type: string
    cachedAt: Date
  }>
}

export const AppPreviewControls: React.FC = () => {
  const [port, setPort] = useState<number | null>(3002)
  const [portInfo, setPortInfo] = useState<PortInfo | null>(null)
  const [consoleMessages, setConsoleMessages] = useState<ConsoleMessage[]>([])
  const [selectedTab, setSelectedTab] = useState<'console' | 'port' | 'terminal' | 'cache'>('console')
  const [terminalOutput, setTerminalOutput] = useState<string[]>([])
  const [cacheInfo, setCacheInfo] = useState<CacheInfo | null>(null)
  const terminalEndRef = useRef<HTMLDivElement>(null)
  
  // Detect port info with detailed metrics
  useEffect(() => {
    if (port) {
      const startTime = Date.now() - 3600000 // 1 hour ago
      setPortInfo({
        port: port,
        protocol: 'http',
        status: 'active',
        processId: Math.floor(Math.random() * 10000),
        startedAt: new Date(startTime),
        uptime: Math.floor((Date.now() - startTime) / 1000),
        requests: Math.floor(Math.random() * 1000) + 500,
        memoryUsage: Math.floor(Math.random() * 200) + 50, // MB
        cpuUsage: Math.random() * 30 + 5 // percentage
      })
    }
  }, [port])
  
  // Initialize cache info
  useEffect(() => {
    setCacheInfo({
      totalSize: 2456789, // bytes
      itemCount: 42,
      lastCleared: new Date(Date.now() - 7200000), // 2 hours ago
      items: [
        { url: 'http://localhost:3002/index.html', size: 15234, type: 'document', cachedAt: new Date(Date.now() - 3600000) },
        { url: 'http://localhost:3002/main.js', size: 456789, type: 'script', cachedAt: new Date(Date.now() - 1800000) },
        { url: 'http://localhost:3002/styles.css', size: 123456, type: 'stylesheet', cachedAt: new Date(Date.now() - 900000) },
        { url: 'http://localhost:3002/logo.png', size: 234567, type: 'image', cachedAt: new Date(Date.now() - 600000) },
      ]
    })
  }, [])
  
  // Simulate console messages from browser
  useEffect(() => {
    const interval = setInterval(() => {
      const levels: ConsoleMessage['level'][] = ['log', 'info', 'warn', 'error']
      const level = levels[Math.floor(Math.random() * levels.length)]
      
      const messages = [
        'Component rendered successfully',
        'API request completed',
        'State updated',
        'Route changed',
        'Warning: Deprecated API usage',
        'Error: Failed to fetch data'
      ]
      
      setConsoleMessages(prev => [...prev.slice(-49), {
        id: `msg_${Date.now()}`,
        timestamp: new Date(),
        level,
        message: messages[Math.floor(Math.random() * messages.length)],
        source: 'browser'
      }])
    }, 3000)
    
    return () => clearInterval(interval)
  }, [])
  
  // Simulate terminal output
  useEffect(() => {
    const interval = setInterval(() => {
      setTerminalOutput(prev => [...prev.slice(-49), `[${new Date().toLocaleTimeString()}] Server running on port ${port}`])
      if (terminalEndRef.current) {
        terminalEndRef.current.scrollIntoView({ behavior: 'smooth' })
      }
    }, 5000)
    
    return () => clearInterval(interval)
  }, [port])
  
  const getLevelColor = (level: ConsoleMessage['level']) => {
    switch (level) {
      case 'error': return 'text-red-400 bg-red-900/30 border-red-700'
      case 'warn': return 'text-yellow-400 bg-yellow-900/30 border-yellow-700'
      case 'info': return 'text-blue-400 bg-blue-900/30 border-blue-700'
      case 'log': return 'text-gray-400 bg-gray-900/30 border-gray-700'
    }
  }
  
  const getLevelIcon = (level: ConsoleMessage['level']) => {
    switch (level) {
      case 'error': return <XCircle className="w-3 h-3" />
      case 'warn': return <AlertCircle className="w-3 h-3" />
      case 'info': return <Info className="w-3 h-3" />
      case 'log': return <CheckCircle className="w-3 h-3" />
    }
  }
  
  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }
  
  const formatUptime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60
    return `${hours}h ${minutes}m ${secs}s`
  }
  
  const handleClearCache = () => {
    if (cacheInfo) {
      setCacheInfo({
        totalSize: 0,
        itemCount: 0,
        lastCleared: new Date(),
        items: []
      })
    }
  }
  
  return (
    <BasePanel
      id="panel-app-preview-controls"
      title="App Preview Controls"
      icon={Globe}
      description="Browser console, port info, terminal, and cache management"
      showFooter={false}
      headerClassName="p-3"
    >
      {/* Tab Selector */}
      <div className="flex border-b border-gray-700">
        {(['console', 'port', 'terminal', 'cache'] as const).map(tab => (
          <button
            key={tab}
            onClick={() => setSelectedTab(tab)}
            className={`flex-1 px-3 py-2 text-xs font-semibold transition-colors ${
              selectedTab === tab
                ? 'bg-gray-800 text-blue-400 border-b-2 border-blue-400'
                : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/50'
            }`}
          >
            {tab === 'console' && 'Console'}
            {tab === 'port' && 'Port Info'}
            {tab === 'terminal' && 'Terminal'}
            {tab === 'cache' && 'Cache'}
          </button>
        ))}
      </div>
      
      {/* Tab Content */}
      <div className="flex-1 overflow-auto">
        {selectedTab === 'console' && (
          <div className="p-2 space-y-1">
            {consoleMessages.length === 0 ? (
              <div className="text-center text-gray-500 py-8 text-xs">
                No console messages
              </div>
            ) : (
              consoleMessages.map(msg => (
                <div
                  key={msg.id}
                  className={`p-2 rounded text-xs border ${getLevelColor(msg.level)}`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    {getLevelIcon(msg.level)}
                    <span className="text-[10px] font-mono text-gray-500">
                      {msg.timestamp.toLocaleTimeString()}
                    </span>
                    {msg.source && (
                      <span className="text-[10px] px-1 py-0.5 rounded bg-gray-700 text-gray-400">
                        {msg.source}
                      </span>
                    )}
                  </div>
                  <div className="text-gray-300">{msg.message}</div>
                </div>
              ))
            )}
          </div>
        )}
        
        {selectedTab === 'port' && portInfo && (
          <div className="p-4 space-y-3">
            {/* Port Status Card */}
            <div className="bg-gray-800 rounded p-3 border border-gray-700">
              <div className="flex items-center gap-2 mb-3">
                <Server className="w-4 h-4 text-blue-400" />
                <h3 className="text-sm font-semibold text-gray-200">Port Information</h3>
              </div>
              
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-gray-400">Port:</span>
                  <span className="text-gray-200 font-mono">{portInfo.port}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Protocol:</span>
                  <span className="text-gray-200 uppercase">{portInfo.protocol}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Status:</span>
                  <span className={portInfo.status === 'active' ? 'text-green-400' : 'text-red-400'}>
                    {portInfo.status.toUpperCase()}
                  </span>
                </div>
                {portInfo.processId && (
                  <div className="flex justify-between">
                    <span className="text-gray-400">Process ID:</span>
                    <span className="text-gray-200 font-mono">{portInfo.processId}</span>
                  </div>
                )}
                {portInfo.startedAt && (
                  <div className="flex justify-between">
                    <span className="text-gray-400">Started:</span>
                    <span className="text-gray-200 text-[10px]">
                      {portInfo.startedAt.toLocaleString()}
                    </span>
                  </div>
                )}
                {portInfo.uptime !== undefined && (
                  <div className="flex justify-between">
                    <span className="text-gray-400">Uptime:</span>
                    <span className="text-gray-200 font-mono">{formatUptime(portInfo.uptime)}</span>
                  </div>
                )}
                {portInfo.requests !== undefined && (
                  <div className="flex justify-between">
                    <span className="text-gray-400">Requests:</span>
                    <span className="text-gray-200 font-mono">{portInfo.requests.toLocaleString()}</span>
                  </div>
                )}
                {portInfo.memoryUsage !== undefined && (
                  <div className="flex justify-between">
                    <span className="text-gray-400">Memory:</span>
                    <span className="text-gray-200 font-mono">{portInfo.memoryUsage} MB</span>
                  </div>
                )}
                {portInfo.cpuUsage !== undefined && (
                  <div className="flex justify-between">
                    <span className="text-gray-400">CPU:</span>
                    <span className="text-gray-200 font-mono">{portInfo.cpuUsage.toFixed(1)}%</span>
                  </div>
                )}
                <div className="col-span-2 flex justify-between border-t border-gray-700 pt-2 mt-2">
                  <span className="text-gray-400">URL:</span>
                  <a
                    href={`${portInfo.protocol}://localhost:${portInfo.port}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-400 hover:text-blue-300 underline text-[10px]"
                  >
                    {portInfo.protocol}://localhost:{portInfo.port}
                  </a>
                </div>
              </div>
            </div>
            
            {/* Process Management */}
            <div className="bg-gray-800 rounded p-3 border border-gray-700">
              <h3 className="text-xs font-semibold text-gray-400 mb-2 flex items-center gap-2">
                <Power className="w-3 h-3" />
                Process Management
              </h3>
              <div className="flex gap-2">
                <button className="flex-1 px-2 py-1 rounded text-xs bg-red-600 text-white hover:bg-red-700 flex items-center justify-center gap-1">
                  <Power className="w-3 h-3" />
                  Stop
                </button>
                <button className="flex-1 px-2 py-1 rounded text-xs bg-gray-700 text-gray-300 hover:bg-gray-600 flex items-center justify-center gap-1">
                  <RefreshCw className="w-3 h-3" />
                  Restart
                </button>
              </div>
            </div>
          </div>
        )}
        
        {selectedTab === 'terminal' && (
          <div className="h-full flex flex-col bg-gray-950">
            <div className="flex-1 overflow-auto p-2 font-mono text-xs">
              {terminalOutput.length === 0 ? (
                <div className="text-gray-500 py-8 text-center">
                  No terminal output
                </div>
              ) : (
                terminalOutput.map((line, idx) => (
                  <div key={idx} className="text-green-400 mb-1">
                    {line}
                  </div>
                ))
              )}
              <div ref={terminalEndRef} />
            </div>
            <div className="p-2 border-t border-gray-700 flex items-center gap-2">
              <input
                type="text"
                placeholder="Enter command..."
                className="flex-1 bg-gray-900 border border-gray-700 rounded px-2 py-1 text-xs text-gray-300 outline-none focus:border-blue-500"
              />
              <button className="px-2 py-1 rounded bg-gray-700 text-gray-300 hover:bg-gray-600 text-xs">
                Send
              </button>
            </div>
          </div>
        )}
        
        {selectedTab === 'cache' && cacheInfo && (
          <div className="p-4 space-y-3">
            {/* Cache Summary */}
            <div className="bg-gray-800 rounded p-3 border border-gray-700">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Database className="w-4 h-4 text-blue-400" />
                  <h3 className="text-sm font-semibold text-gray-200">Cache Information</h3>
                </div>
                <button
                  onClick={handleClearCache}
                  className="px-2 py-1 rounded text-xs bg-red-600 text-white hover:bg-red-700 flex items-center gap-1"
                >
                  <Trash2 className="w-3 h-3" />
                  Clear
                </button>
              </div>
              
              <div className="grid grid-cols-2 gap-2 text-xs mb-3">
                <div className="flex justify-between">
                  <span className="text-gray-400">Total Size:</span>
                  <span className="text-gray-200 font-mono">{formatBytes(cacheInfo.totalSize)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Items:</span>
                  <span className="text-gray-200 font-mono">{cacheInfo.itemCount}</span>
                </div>
                {cacheInfo.lastCleared && (
                  <div className="col-span-2 flex justify-between border-t border-gray-700 pt-2 mt-2">
                    <span className="text-gray-400">Last Cleared:</span>
                    <span className="text-gray-200 text-[10px]">
                      {cacheInfo.lastCleared.toLocaleString()}
                    </span>
                  </div>
                )}
              </div>
            </div>
            
            {/* Cache Items List */}
            <div className="bg-gray-800 rounded p-3 border border-gray-700">
              <h3 className="text-xs font-semibold text-gray-400 mb-2 flex items-center gap-2">
                <HardDrive className="w-3 h-3" />
                Cached Items ({cacheInfo.items.length})
              </h3>
              <div className="space-y-1 max-h-64 overflow-auto">
                {cacheInfo.items.length === 0 ? (
                  <div className="text-center text-gray-500 py-4 text-xs">
                    No cached items
                  </div>
                ) : (
                  cacheInfo.items.map((item, idx) => (
                    <div key={idx} className="p-2 rounded bg-gray-900/50 border border-gray-700 text-xs">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-gray-300 font-mono text-[10px] truncate flex-1">
                          {item.url}
                        </span>
                        <span className="text-gray-500 text-[10px] ml-2">
                          {formatBytes(item.size)}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-gray-500 text-[10px] px-1 py-0.5 rounded bg-gray-700">
                          {item.type}
                        </span>
                        <span className="text-gray-500 text-[10px]">
                          {item.cachedAt.toLocaleTimeString()}
                        </span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </BasePanel>
  )
}
