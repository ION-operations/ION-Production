// Panel Registry Hook - Max V2
// Provides panel initialization and lifecycle management

import React, { useEffect, useRef, useCallback, useState } from 'react'
import { usePanelStore } from '../store/panelStore'
import {
  PANEL_REGISTRY,
  getPanelConfig,
  getAllPanelConfigs,
  getPanelsByCategory,
  getPanelsByZone,
  createPanelFromConfig,
  panelLifecycleManager,
} from '../utils/panelRegistry'
import type { Panel, ZoneType } from '../types/Panel.types'

/**
 * Hook for initializing default panels from registry
 * Ensures all default panels are registered in the panelStore
 */
export function usePanelInitialization() {
  const { panels, addPanel } = usePanelStore()
  const initialized = useRef(false)

  useEffect(() => {
    if (initialized.current) return

    const store = usePanelStore.getState()
    const currentPanelIds = store.panels.map((p) => p.id)
    const registryPanelIds = Object.keys(PANEL_REGISTRY)

    // Add any missing panels from registry
    registryPanelIds.forEach((panelId) => {
      if (!currentPanelIds.includes(panelId)) {
        const config = getPanelConfig(panelId)
        if (config) {
          const panel = createPanelFromConfig(config)
          store.addPanel(panel)
        }
      }
    })

    initialized.current = true
  }, []) // Only run once on mount

  return {
    panels,
    getAllPanelConfigs,
    getPanelsByCategory,
    getPanelsByZone,
  }
}

/**
 * Hook for panel lifecycle management
 */
export function usePanelLifecycle(panelId: string) {
  const { panels, updatePanel } = usePanelStore()
  const panel = panels.find((p) => p.id === panelId)
  const isMountedRef = useRef(false)

  const mount = useCallback(() => {
    if (isMountedRef.current) return
    isMountedRef.current = true
    panelLifecycleManager.mount(panelId, {
      mount: () => {
        console.log(`[MAX] Panel ${panelId} mounted`)
        updatePanel(panelId, { visible: true })
      },
      unmount: () => {
        console.log(`[MAX] Panel ${panelId} unmounted`)
        updatePanel(panelId, { visible: false })
      },
      update: (updates) => {
        updatePanel(panelId, updates)
      },
      isMounted: isMountedRef.current,
    })
  }, [panelId, updatePanel])

  const unmount = useCallback(() => {
    if (!isMountedRef.current) return
    isMountedRef.current = false
    panelLifecycleManager.unmount(panelId)
  }, [panelId])

  useEffect(() => {
    if (panel?.visible && !isMountedRef.current) {
      mount()
    } else if (!panel?.visible && isMountedRef.current) {
      unmount()
    }

    return () => {
      if (isMountedRef.current) {
        unmount()
      }
    }
  }, [panel?.visible, mount, unmount])

  return {
    isMounted: isMountedRef.current,
    mount,
    unmount,
  }
}

/**
 * Hook for lazy loading panels
 */
export function useLazyPanel(panelId: string) {
  const config = getPanelConfig(panelId)
  const [isLoaded, setIsLoaded] = useState(false)
  const [Component, setComponent] = useState<React.ComponentType | null>(null)

  const loadPanel = useCallback(async () => {
    if (isLoaded || !config?.lazyLoad) return

    try {
      // Dynamic import based on component name
      const module = await import(`../components/panels/${config.component}.tsx`)
      setComponent(() => module[config.component])
      setIsLoaded(true)
    } catch (error) {
      console.error(`[MAX] Failed to load panel ${panelId}:`, error)
    }
  }, [panelId, config, isLoaded])

  return {
    Component,
    isLoaded,
    loadPanel,
    shouldLazyLoad: config?.lazyLoad ?? false,
  }
}

