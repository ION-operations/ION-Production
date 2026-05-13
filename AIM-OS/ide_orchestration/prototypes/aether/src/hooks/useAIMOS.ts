import { useState, useEffect } from 'react'
import { useCMC } from './useCMC'
import { useHHNI } from './useHHNI'
import { useVIF } from './useVIF'
import { useSEG } from './useSEG'
import { useAPOE } from './useAPOE'
import { useTCS } from './useTCS'
import { useCAS } from './useCAS'
import { useSDFCVF } from './useSDFCVF'
import type { AIMOSHook } from './types'

// Re-export all types
export type * from './types'

/**
 * useAIMOS Hook
 * 
 * Unified hook interface for all 8 AIM-OS systems
 * Composes individual system hooks into a single interface
 * 
 * @returns AIMOSHook with all 8 systems and connection status
 */
export function useAIMOS(): AIMOSHook {
  const [isConnected, setIsConnected] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'connecting' | 'error'>('disconnected')
  const [error, setError] = useState<Error | null>(null)

  // Use individual hooks
  const cmc = useCMC()
  const hhni = useHHNI()
  const vif = useVIF()
  const seg = useSEG()
  const apoe = useAPOE()
  const tcs = useTCS()
  const cas = useCAS()
  const sdfcvf = useSDFCVF()

  // Check connection status
  useEffect(() => {
    // TODO: Implement real connection check
    // For now, use mock data mode
    setIsConnected(false)
    setConnectionStatus('disconnected')
  }, [])

  return {
    cmc,
    hhni,
    vif,
    seg,
    apoe,
    tcs,
    cas,
    sdfcvf,
    isConnected,
    connectionStatus,
    error
  }
}
