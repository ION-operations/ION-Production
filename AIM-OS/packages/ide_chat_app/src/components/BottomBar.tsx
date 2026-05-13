/**
 * Bottom Bar Component
 * Status bar and quick actions at the bottom of the window
 * Includes integrated system health status
 */

import React, { useState, useEffect } from 'react'
import { Activity, HardDrive, Cpu, Clock, AlertCircle, CheckCircle } from 'lucide-react'

interface BottomBarProps {
  status?: string
  systemInfo?: {
    cpu?: number
    memory?: number
    disk?: number
  }
}

export const BottomBar: React.FC<BottomBarProps> = ({ status = 'Ready', systemInfo }) => {
  const [healthStatus, setHealthStatus] = useState<'healthy' | 'warning' | 'critical'>('healthy')

  useEffect(() => {
    console.log('[BottomBar] ✅ Component mounted')
    console.log('[BottomBar] DOM element:', document.querySelector('[data-bottom-bar]'))
  }, [])

  // Calculate overall health status from system metrics
  useEffect(() => {
    if (!systemInfo) return

    const cpu = systemInfo.cpu || 0
    const memory = systemInfo.memory || 0
    const disk = systemInfo.disk || 0

    // Determine health status
    const isCritical = cpu > 80 || memory > 85 || disk > 90
    const isWarning = cpu > 60 || memory > 70 || disk > 80

    if (isCritical) {
      setHealthStatus('critical')
    } else if (isWarning) {
      setHealthStatus('warning')
    } else {
      setHealthStatus('healthy')
    }
  }, [systemInfo])

  const getHealthColor = () => {
    switch (healthStatus) {
      case 'critical':
        return 'text-red-400'
      case 'warning':
        return 'text-yellow-400'
      default:
        return 'text-green-400'
    }
  }

  const getHealthIcon = () => {
    switch (healthStatus) {
      case 'critical':
        return <AlertCircle className="w-3 h-3 text-red-400" />
      case 'warning':
        return <AlertCircle className="w-3 h-3 text-yellow-400" />
      default:
        return <CheckCircle className="w-3 h-3 text-green-400" />
    }
  }

  return (
    <div 
      data-bottom-bar="true"
      className="h-7 bg-cursor-sidebar border-t border-cursor-border flex items-center justify-between px-3 text-xs text-cursor-text-secondary select-none fixed bottom-0 left-0 right-0 z-50"
      style={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        zIndex: 9999,
        backgroundColor: '#252526',
        borderTop: '1px solid #454545',
        width: '100%',
        height: '28px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        fontSize: '12px',
        lineHeight: '1.4'
      }}
    >
      {/* Left side - Status */}
      <div className="flex items-center gap-2">
        <div className="flex items-center gap-1.5">
          <div className={`w-1.5 h-1.5 rounded-full ${
            healthStatus === 'critical' ? 'bg-red-500' :
            healthStatus === 'warning' ? 'bg-yellow-500' :
            'bg-green-500'
          }`} />
          <span className="font-normal">{status}</span>
        </div>
        <div className="text-cursor-text-muted" style={{ fontSize: '10px' }}>|</div>
        {/* System Health Status */}
        <div className={`flex items-center gap-1 ${getHealthColor()}`}>
          {getHealthIcon()}
          <span className="font-normal">{healthStatus.toUpperCase()}</span>
        </div>
        <div className="text-cursor-text-muted" style={{ fontSize: '10px' }}>|</div>
        <div className="flex items-center gap-1">
          <Clock className="w-3 h-3" />
          <span>{new Date().toLocaleTimeString()}</span>
        </div>
      </div>

      {/* Right side - System metrics */}
      <div className="flex items-center gap-2">
        {systemInfo?.cpu !== undefined && (
          <div className={`flex items-center gap-1 ${
            systemInfo.cpu > 80 ? 'text-red-400' :
            systemInfo.cpu > 60 ? 'text-yellow-400' :
            ''
          }`}>
            <Cpu className="w-3 h-3" />
            <span>{systemInfo.cpu.toFixed(0)}%</span>
          </div>
        )}
        {systemInfo?.memory !== undefined && (
          <div className={`flex items-center gap-1 ${
            systemInfo.memory > 85 ? 'text-red-400' :
            systemInfo.memory > 70 ? 'text-yellow-400' :
            ''
          }`}>
            <HardDrive className="w-3 h-3" />
            <span>{systemInfo.memory.toFixed(0)}%</span>
          </div>
        )}
        {systemInfo?.disk !== undefined && (
          <div className={`flex items-center gap-1 ${
            systemInfo.disk > 90 ? 'text-red-400' :
            systemInfo.disk > 80 ? 'text-yellow-400' :
            ''
          }`}>
            <Activity className="w-3 h-3" />
            <span>{systemInfo.disk.toFixed(0)}%</span>
          </div>
        )}
      </div>
    </div>
  )
}

