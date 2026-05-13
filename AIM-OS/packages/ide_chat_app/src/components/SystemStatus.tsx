import React, { useEffect, useState } from 'react'
import { aimosClient } from '../lib/aimos-client'

interface SystemStatus {
  status: string
  systems?: {
    cmc?: string
    hhni?: string
    vif?: string
    seg?: string
    apoe?: string
  }
}

export const SystemStatus: React.FC = () => {
  const [status, setStatus] = useState<SystemStatus>({ status: 'offline' })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const systemStatus = await aimosClient.getSystemStatus()
        setStatus(systemStatus)
      } catch (error) {
        console.error('Failed to check system status:', error)
        setStatus({ status: 'error' })
      } finally {
        setLoading(false)
      }
    }

    checkStatus()
    const interval = setInterval(checkStatus, 10000) // Check every 10 seconds

    return () => clearInterval(interval)
  }, [])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online':
        return 'text-green-500'
      case 'offline':
        return 'text-red-500'
      case 'error':
        return 'text-orange-500'
      default:
        return 'text-gray-500'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online':
        return '●'
      case 'offline':
        return '○'
      case 'error':
        return '⚠'
      default:
        return '○'
    }
  }

  if (loading) {
    return (
      <div className="flex items-center gap-2 text-sm text-gray-500">
        <span>Checking status...</span>
      </div>
    )
  }

  return (
    <div className="flex items-center gap-2 text-sm">
      <span className={getStatusColor(status.status)}>
        {getStatusIcon(status.status)}
      </span>
      <span className="text-gray-600">AIM-OS {status.status}</span>
      {status.systems && (
        <div className="flex items-center gap-1 text-xs text-gray-400">
          {status.systems.cmc && (
            <span title="CMC Status" className={getStatusColor(status.systems.cmc)}>
              C
            </span>
          )}
          {status.systems.hhni && (
            <span title="HHNI Status" className={getStatusColor(status.systems.hhni)}>
              H
            </span>
          )}
          {status.systems.vif && (
            <span title="VIF Status" className={getStatusColor(status.systems.vif)}>
              V
            </span>
          )}
          {status.systems.seg && (
            <span title="SEG Status" className={getStatusColor(status.systems.seg)}>
              S
            </span>
          )}
          {status.systems.apoe && (
            <span title="APOE Status" className={getStatusColor(status.systems.apoe)}>
              A
            </span>
          )}
        </div>
      )}
    </div>
  )
}
