import React, { useState, useEffect } from 'react'
import { Activity, Cpu, HardDrive, Terminal, X, RefreshCw, Trash2, AlertCircle, Camera } from 'lucide-react'

interface ProcessInfo {
  pid: number
  name: string
  cpu: number
  memory: number
  command: string
  parentPid?: number
}

interface PortInfo {
  port: number
  protocol: string
  pid: number
  processName: string
  status: string
}

interface SystemInfo {
  cpu: {
    usage: number
    cores: number
    model: string
  }
  memory: {
    total: number
    used: number
    free: number
    percentage: number
  }
  disk: {
    total: number
    used: number
    free: number
    percentage: number
  }
  platform: string
  arch: string
  nodeVersion: string
  electronVersion: string
}

declare global {
  interface Window {
    systemAPI?: {
      getProcesses: () => Promise<{ success: boolean; processes?: ProcessInfo[]; error?: string }>
      getPorts: () => Promise<{ success: boolean; ports?: PortInfo[]; error?: string }>
      getSystemInfo: () => Promise<{ success: boolean; info?: SystemInfo; error?: string }>
      killProcess: (pid: number) => Promise<{ success: boolean; error?: string }>
      closePort: (port: number) => Promise<{ success: boolean; error?: string }>
      getTerminals: () => Promise<{ success: boolean; terminals?: any[]; error?: string }>
    }
    electronAPI?: {
      invoke: (channel: string, ...args: any[]) => Promise<any>
    }
  }
}

export const SystemTools: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'processes' | 'ports' | 'system' | 'terminals' | 'capture'>('processes')
  const [processes, setProcesses] = useState<ProcessInfo[]>([])
  const [ports, setPorts] = useState<PortInfo[]>([])
  const [systemInfo, setSystemInfo] = useState<SystemInfo | null>(null)
  const [loading, setLoading] = useState(false)
  const [filter, setFilter] = useState('')
  const [sortBy, setSortBy] = useState<'cpu' | 'memory' | 'name'>('cpu')

  // Template capture state
  const [capturing, setCapturing] = useState(false)

  // Start template capture
  const handleStartCapture = async () => {
    if (!window.electronAPI) {
      alert('Template capture is only available in the Electron app')
      return
    }

    setCapturing(true)
    try {
      const result = await window.electronAPI.invoke('overlay:show')
      if (!result.success) {
        alert(`Failed to start capture: ${result.error}`)
        setCapturing(false)
      }
    } catch (error) {
      console.error('Failed to start capture:', error)
      alert('Failed to start template capture')
      setCapturing(false)
    }
  }

  // Listen for capture result
  useEffect(() => {
    const handleCaptureResult = (event: CustomEvent) => {
      const data = event.detail
      setCapturing(false)
      // Forward to MainDashboard via window event
      window.dispatchEvent(new CustomEvent('capture-result', { detail: data }))
    }

    window.addEventListener('capture-result', handleCaptureResult as EventListener)
    
    return () => {
      window.removeEventListener('capture-result', handleCaptureResult as EventListener)
    }
  }, [])

  // Fetch processes
  const fetchProcesses = async () => {
    if (!window.systemAPI) return
    
    setLoading(true)
    try {
      const result = await window.systemAPI.getProcesses()
      if (result.success && result.processes) {
        setProcesses(result.processes)
      }
    } catch (error) {
      console.error('Failed to fetch processes:', error)
    } finally {
      setLoading(false)
    }
  }

  // Fetch ports
  const fetchPorts = async () => {
    if (!window.systemAPI) return
    
    setLoading(true)
    try {
      const result = await window.systemAPI.getPorts()
      if (result.success && result.ports) {
        setPorts(result.ports)
      }
    } catch (error) {
      console.error('Failed to fetch ports:', error)
    } finally {
      setLoading(false)
    }
  }

  // Fetch system info
  const fetchSystemInfo = async () => {
    if (!window.systemAPI) return
    
    setLoading(true)
    try {
      const result = await window.systemAPI.getSystemInfo()
      if (result.success && result.info) {
        setSystemInfo(result.info)
      }
    } catch (error) {
      console.error('Failed to fetch system info:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (activeTab === 'processes') {
      fetchProcesses()
      const interval = setInterval(fetchProcesses, 3000) // Refresh every 3 seconds
      return () => clearInterval(interval)
    } else if (activeTab === 'ports') {
      fetchPorts()
      const interval = setInterval(fetchPorts, 5000) // Refresh every 5 seconds
      return () => clearInterval(interval)
    } else if (activeTab === 'system') {
      fetchSystemInfo()
      const interval = setInterval(fetchSystemInfo, 10000) // Refresh every 10 seconds
      return () => clearInterval(interval)
    }
  }, [activeTab])

  // Filter processes
  const filteredProcesses = processes.filter(p => {
    if (!filter) return true
    const query = filter.toLowerCase()
    return p.name.toLowerCase().includes(query) ||
           p.command.toLowerCase().includes(query) ||
           p.pid.toString().includes(query)
  })

  // Sort processes
  const sortedProcesses = [...filteredProcesses].sort((a, b) => {
    switch (sortBy) {
      case 'cpu':
        return b.cpu - a.cpu
      case 'memory':
        return b.memory - a.memory
      case 'name':
        return a.name.localeCompare(b.name)
      default:
        return 0
    }
  })

  // Filter AIM-OS processes
  const aimosProcesses = sortedProcesses.filter(p => 
    p.name.toLowerCase().includes('python') ||
    p.name.toLowerCase().includes('node') ||
    p.name.toLowerCase().includes('electron') ||
    p.command.includes('lucid') ||
    p.command.includes('mcp') ||
    p.command.includes('aimos') ||
    p.command.includes('daemon')
  )

  // Filter ports
  const filteredPorts = ports.filter(p => {
    if (!filter) return true
    const query = filter.toLowerCase()
    return p.port.toString().includes(query) ||
           p.processName.toLowerCase().includes(query) ||
           p.protocol.toLowerCase().includes(query)
  })

  // AIM-OS ports (5000, 5001, etc.)
  const aimosPorts = filteredPorts.filter(p => 
    p.port === 5000 || // Daemon
    p.port === 5001 || // Command Server
    p.port === 3000 || // Vite dev server
    p.processName.toLowerCase().includes('python') ||
    p.processName.toLowerCase().includes('node') ||
    p.processName.toLowerCase().includes('electron')
  )

  // Kill process
  const handleKillProcess = async (pid: number) => {
    if (!confirm(`Kill process ${pid}?`)) return
    
    if (!window.systemAPI) return
    
    try {
      const result = await window.systemAPI.killProcess(pid)
      if (result.success) {
        await fetchProcesses()
      } else {
        alert(`Failed to kill process: ${result.error}`)
      }
    } catch (error) {
      console.error('Failed to kill process:', error)
      alert('Failed to kill process')
    }
  }

  // Close port
  const handleClosePort = async (port: number) => {
    if (!confirm(`Close port ${port}?`)) return
    
    if (!window.systemAPI) return
    
    try {
      const result = await window.systemAPI.closePort(port)
      if (result.success) {
        await fetchPorts()
      } else {
        alert(`Failed to close port: ${result.error}`)
      }
    } catch (error) {
      console.error('Failed to close port:', error)
      alert('Failed to close port')
    }
  }

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  return (
    <div className="h-full flex flex-col bg-gray-900 text-white">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-800">
        <div className="flex items-center gap-4">
          <Activity className="w-6 h-6 text-blue-400" />
          <h2 className="text-xl font-semibold">System Tools</h2>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => {
              if (activeTab === 'processes') fetchProcesses()
              else if (activeTab === 'ports') fetchPorts()
              else if (activeTab === 'system') fetchSystemInfo()
            }}
            disabled={loading}
            className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 inline mr-1 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-800 bg-gray-800/50">
        <button
          onClick={() => setActiveTab('processes')}
          className={`px-4 py-2 text-sm font-medium transition-colors ${
            activeTab === 'processes' 
              ? 'border-b-2 border-blue-500 text-blue-400' 
              : 'text-gray-400 hover:text-gray-200'
          }`}
        >
          Task Manager
        </button>
        <button
          onClick={() => setActiveTab('ports')}
          className={`px-4 py-2 text-sm font-medium transition-colors ${
            activeTab === 'ports' 
              ? 'border-b-2 border-blue-500 text-blue-400' 
              : 'text-gray-400 hover:text-gray-200'
          }`}
        >
          Port Manager
        </button>
        <button
          onClick={() => setActiveTab('system')}
          className={`px-4 py-2 text-sm font-medium transition-colors ${
            activeTab === 'system' 
              ? 'border-b-2 border-blue-500 text-blue-400' 
              : 'text-gray-400 hover:text-gray-200'
          }`}
        >
          System Info
        </button>
        <button
          onClick={() => setActiveTab('capture')}
          className={`px-4 py-2 text-sm font-medium transition-colors ${
            activeTab === 'capture' 
              ? 'border-b-2 border-blue-500 text-blue-400' 
              : 'text-gray-400 hover:text-gray-200'
          }`}
        >
          Template Capture
        </button>
        <button
          onClick={() => setActiveTab('terminals')}
          className={`px-4 py-2 text-sm font-medium transition-colors ${
            activeTab === 'terminals' 
              ? 'border-b-2 border-blue-500 text-blue-400' 
              : 'text-gray-400 hover:text-gray-200'
          }`}
        >
          Terminals
        </button>
      </div>

      {/* Filters */}
      <div className="p-4 border-b border-gray-800 bg-gray-800/50">
        <div className="flex items-center gap-4">
          <input
            type="text"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            placeholder="Search..."
            className="flex-1 bg-gray-900 text-white px-3 py-2 rounded border border-gray-700 text-sm focus:outline-none focus:border-blue-500"
          />
          {activeTab === 'processes' && (
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as 'cpu' | 'memory' | 'name')}
              className="bg-gray-900 text-white px-3 py-2 rounded border border-gray-700 text-sm focus:outline-none focus:border-blue-500"
            >
              <option value="cpu">Sort by CPU</option>
              <option value="memory">Sort by Memory</option>
              <option value="name">Sort by Name</option>
            </select>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-4">
        {activeTab === 'processes' && (
          <div className="space-y-4">
            {/* AIM-OS Processes Section */}
            {aimosProcesses.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                  <AlertCircle className="w-5 h-5 text-yellow-400" />
                  AIM-OS Processes
                </h3>
                <div className="bg-gray-800/50 rounded-lg overflow-hidden">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-800">
                      <tr>
                        <th className="px-4 py-2 text-left">PID</th>
                        <th className="px-4 py-2 text-left">Name</th>
                        <th className="px-4 py-2 text-right">CPU %</th>
                        <th className="px-4 py-2 text-right">Memory</th>
                        <th className="px-4 py-2 text-left">Command</th>
                        <th className="px-4 py-2 text-center">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {aimosProcesses.map((proc) => (
                        <tr key={proc.pid} className="border-t border-gray-700 hover:bg-gray-800">
                          <td className="px-4 py-2">{proc.pid}</td>
                          <td className="px-4 py-2 font-medium">{proc.name}</td>
                          <td className="px-4 py-2 text-right">
                            <span className={proc.cpu > 50 ? 'text-red-400' : proc.cpu > 20 ? 'text-yellow-400' : 'text-green-400'}>
                              {proc.cpu.toFixed(1)}%
                            </span>
                          </td>
                          <td className="px-4 py-2 text-right">{formatBytes(proc.memory)}</td>
                          <td className="px-4 py-2 text-xs text-gray-400 truncate max-w-xs">{proc.command}</td>
                          <td className="px-4 py-2 text-center">
                            <button
                              onClick={() => handleKillProcess(proc.pid)}
                              className="px-2 py-1 bg-red-600 hover:bg-red-700 rounded text-xs"
                            >
                              Kill
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* All Processes */}
            <div>
              <h3 className="text-lg font-semibold mb-2">All Processes</h3>
              <div className="bg-gray-800/50 rounded-lg overflow-hidden">
                <table className="w-full text-sm">
                  <thead className="bg-gray-800">
                    <tr>
                      <th className="px-4 py-2 text-left">PID</th>
                      <th className="px-4 py-2 text-left">Name</th>
                      <th className="px-4 py-2 text-right">CPU %</th>
                      <th className="px-4 py-2 text-right">Memory</th>
                      <th className="px-4 py-2 text-left">Command</th>
                      <th className="px-4 py-2 text-center">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sortedProcesses.slice(0, 100).map((proc) => (
                      <tr key={proc.pid} className="border-t border-gray-700 hover:bg-gray-800">
                        <td className="px-4 py-2">{proc.pid}</td>
                        <td className="px-4 py-2">{proc.name}</td>
                        <td className="px-4 py-2 text-right">
                          <span className={proc.cpu > 50 ? 'text-red-400' : proc.cpu > 20 ? 'text-yellow-400' : 'text-green-400'}>
                            {proc.cpu.toFixed(1)}%
                          </span>
                        </td>
                        <td className="px-4 py-2 text-right">{formatBytes(proc.memory)}</td>
                        <td className="px-4 py-2 text-xs text-gray-400 truncate max-w-xs">{proc.command}</td>
                        <td className="px-4 py-2 text-center">
                          <button
                            onClick={() => handleKillProcess(proc.pid)}
                            className="px-2 py-1 bg-red-600 hover:bg-red-700 rounded text-xs"
                          >
                            Kill
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {sortedProcesses.length > 100 && (
                  <div className="p-4 text-center text-sm text-gray-400">
                    Showing first 100 of {sortedProcesses.length} processes
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'ports' && (
          <div className="space-y-4">
            {/* AIM-OS Ports */}
            {aimosPorts.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                  <AlertCircle className="w-5 h-5 text-yellow-400" />
                  AIM-OS Ports
                </h3>
                <div className="bg-gray-800/50 rounded-lg overflow-hidden">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-800">
                      <tr>
                        <th className="px-4 py-2 text-left">Port</th>
                        <th className="px-4 py-2 text-left">Protocol</th>
                        <th className="px-4 py-2 text-left">Process</th>
                        <th className="px-4 py-2 text-left">PID</th>
                        <th className="px-4 py-2 text-left">Status</th>
                        <th className="px-4 py-2 text-center">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {aimosPorts.map((port) => (
                        <tr key={`${port.port}-${port.protocol}`} className="border-t border-gray-700 hover:bg-gray-800">
                          <td className="px-4 py-2 font-medium">{port.port}</td>
                          <td className="px-4 py-2">{port.protocol.toUpperCase()}</td>
                          <td className="px-4 py-2">{port.processName}</td>
                          <td className="px-4 py-2">{port.pid}</td>
                          <td className="px-4 py-2">
                            <span className={`px-2 py-0.5 rounded text-xs ${
                              port.status === 'LISTENING' ? 'bg-green-900/20 text-green-400' : 'bg-gray-800 text-gray-400'
                            }`}>
                              {port.status}
                            </span>
                          </td>
                          <td className="px-4 py-2 text-center">
                            <button
                              onClick={() => handleClosePort(port.port)}
                              className="px-2 py-1 bg-red-600 hover:bg-red-700 rounded text-xs"
                            >
                              Close
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* All Ports */}
            <div>
              <h3 className="text-lg font-semibold mb-2">All Open Ports</h3>
              <div className="bg-gray-800/50 rounded-lg overflow-hidden">
                <table className="w-full text-sm">
                  <thead className="bg-gray-800">
                    <tr>
                      <th className="px-4 py-2 text-left">Port</th>
                      <th className="px-4 py-2 text-left">Protocol</th>
                      <th className="px-4 py-2 text-left">Process</th>
                      <th className="px-4 py-2 text-left">PID</th>
                      <th className="px-4 py-2 text-left">Status</th>
                      <th className="px-4 py-2 text-center">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredPorts.map((port) => (
                      <tr key={`${port.port}-${port.protocol}`} className="border-t border-gray-700 hover:bg-gray-800">
                        <td className="px-4 py-2">{port.port}</td>
                        <td className="px-4 py-2">{port.protocol.toUpperCase()}</td>
                        <td className="px-4 py-2">{port.processName}</td>
                        <td className="px-4 py-2">{port.pid}</td>
                        <td className="px-4 py-2">
                          <span className={`px-2 py-0.5 rounded text-xs ${
                            port.status === 'LISTENING' ? 'bg-green-900/20 text-green-400' : 'bg-gray-800 text-gray-400'
                          }`}>
                            {port.status}
                          </span>
                        </td>
                        <td className="px-4 py-2 text-center">
                          <button
                            onClick={() => handleClosePort(port.port)}
                            className="px-2 py-1 bg-red-600 hover:bg-red-700 rounded text-xs"
                          >
                            Close
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'system' && systemInfo && (
          <div className="space-y-4">
            {/* System Overview */}
            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 bg-gray-800 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Cpu className="w-5 h-5 text-blue-400" />
                  <span className="font-semibold">CPU</span>
                </div>
                <div className="text-2xl font-bold">{systemInfo.cpu.usage.toFixed(1)}%</div>
                <div className="text-sm text-gray-400 mt-1">
                  {systemInfo.cpu.cores} cores • {systemInfo.cpu.model}
                </div>
              </div>
              <div className="p-4 bg-gray-800 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <HardDrive className="w-5 h-5 text-green-400" />
                  <span className="font-semibold">Memory</span>
                </div>
                <div className="text-2xl font-bold">{systemInfo.memory.percentage.toFixed(1)}%</div>
                <div className="text-sm text-gray-400 mt-1">
                  {formatBytes(systemInfo.memory.used)} / {formatBytes(systemInfo.memory.total)}
                </div>
              </div>
            </div>

            {/* System Details */}
            <div className="p-4 bg-gray-800 rounded-lg">
              <h3 className="text-lg font-semibold mb-4">System Details</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-gray-400 mb-1">Platform</div>
                  <div className="font-semibold">{systemInfo.platform}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-400 mb-1">Architecture</div>
                  <div className="font-semibold">{systemInfo.arch}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-400 mb-1">Node.js Version</div>
                  <div className="font-semibold">{systemInfo.nodeVersion}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-400 mb-1">Electron Version</div>
                  <div className="font-semibold">{systemInfo.electronVersion}</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'terminals' && (
          <div className="space-y-4">
            <div className="p-4 bg-gray-800 rounded-lg">
              <h3 className="text-lg font-semibold mb-4">Terminals</h3>
              <p className="text-gray-400">
                Terminal viewer - integration with Cursor terminals coming soon
              </p>
            </div>
          </div>
        )}

        {activeTab === 'capture' && (
          <div className="space-y-4">
            <div className="p-4 bg-gray-800 rounded-lg">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Camera className="w-5 h-5 text-blue-400" />
                Template Capture
              </h3>
              <p className="text-gray-400 mb-4">
                Capture UI elements as templates for macro automation. Draw a rectangle over any window to capture a screenshot.
              </p>
              
              <button
                onClick={handleStartCapture}
                disabled={capturing || !window.electronAPI}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <Camera className="w-4 h-4" />
                {capturing ? 'Capturing...' : 'Start Template Capture'}
              </button>

              {!window.electronAPI && (
                <p className="text-yellow-400 text-sm mt-2">
                  Template capture is only available in the Electron app
                </p>
              )}

              {capturing && (
                <div className="mt-4 p-3 bg-blue-900/20 border border-blue-500 rounded text-sm text-blue-300">
                  <p>Overlay window opened. Draw a rectangle over the UI element you want to capture.</p>
                  <p className="mt-2 text-xs">Press Enter to capture, ESC to cancel</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

