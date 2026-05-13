/**
 * Connection Status Component
 * 
 * Phase 1.4: Connection Management
 * 
 * Displays MCP connection status with auto-reconnect
 */

import React, { useState, useEffect } from 'react'
import { Wifi, WifiOff, RefreshCw, AlertCircle, CheckCircle2 } from 'lucide-react'
import { getMCPConnectionStatus, checkMCPConnection } from '../services/mcpToolService'

interface ConnectionStatusProps {
  className?: string
  showLabel?: boolean
}

export const ConnectionStatus: React.FC<ConnectionStatusProps> = ({ 
  className = '', 
  showLabel = true 
}) => {
  const [status, setStatus] = useState<'connected' | 'disconnected' | 'checking'>('checking')
  const [isReconnecting, setIsReconnecting] = useState(false)

  useEffect(() => {
    // Initial check
    const updateStatus = () => {
      setStatus(getMCPConnectionStatus())
    }
    updateStatus()

    // Poll every 5 seconds
    const interval = setInterval(updateStatus, 5000)
    return () => clearInterval(interval)
  }, [])

  const handleReconnect = async () => {
    setIsReconnecting(true)
    try {
      await checkMCPConnection()
      setStatus(getMCPConnectionStatus())
    } finally {
      setIsReconnecting(false)
    }
  }

  const getStatusIcon = () => {
    switch (status) {
      case 'connected':
        return <CheckCircle2 className="w-4 h-4 text-green-500" />
      case 'disconnected':
        return <WifiOff className="w-4 h-4 text-red-500" />
      case 'checking':
        return <RefreshCw className="w-4 h-4 text-yellow-500 animate-spin" />
    }
  }

  const getStatusText = () => {
    switch (status) {
      case 'connected':
        return 'MCP Connected'
      case 'disconnected':
        return 'MCP Disconnected'
      case 'checking':
        return 'Checking...'
    }
  }

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      {getStatusIcon()}
      {showLabel && (
        <span className={`text-sm ${
          status === 'connected' ? 'text-green-500' : 
          status === 'disconnected' ? 'text-red-500' : 
          'text-yellow-500'
        }`}>
          {getStatusText()}
        </span>
      )}
      {status === 'disconnected' && (
        <button
          onClick={handleReconnect}
          disabled={isReconnecting}
          className="px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1"
          title="Reconnect to MCP server"
        >
          <RefreshCw className={`w-3 h-3 ${isReconnecting ? 'animate-spin' : ''}`} />
          Reconnect
        </button>
      )}
    </div>
  )
}

