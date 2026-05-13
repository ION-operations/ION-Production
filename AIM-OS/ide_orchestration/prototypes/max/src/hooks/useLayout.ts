// Layout management hooks for Max V2
// Provides layout save/load, templates, and management

import { useCallback } from 'react'
import { usePanelStore } from '../store/panelStore'
import type { Layout } from '../types/Panel.types'

export const useLayout = () => {
  const {
    layouts,
    currentLayout,
    setCurrentLayout,
    addLayout,
    updateLayout,
    deleteLayout,
    saveLayout,
    loadLayout,
    resetLayout,
  } = usePanelStore()

  const save = useCallback(
    (name: string) => {
      saveLayout(name)
    },
    [saveLayout]
  )

  const load = useCallback(
    (layoutId: string) => {
      loadLayout(layoutId)
    },
    [loadLayout]
  )

  const reset = useCallback(() => {
    resetLayout()
  }, [resetLayout])

  const update = useCallback(
    (layoutId: string, updates: Partial<Layout>) => {
      updateLayout(layoutId, updates)
    },
    [updateLayout]
  )

  const remove = useCallback(
    (layoutId: string) => {
      deleteLayout(layoutId)
    },
    [deleteLayout]
  )

  const createTemplate = useCallback(
    (name: string, template: Partial<Layout>) => {
      const layout: Layout = {
        id: `layout-${Date.now()}`,
        name,
        zones: template.zones || [],
        panels: template.panels || [],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      }
      addLayout(layout)
      return layout
    },
    [addLayout]
  )

  return {
    layouts,
    currentLayout,
    setCurrentLayout,
    save,
    load,
    reset,
    update,
    remove,
    createTemplate,
  }
}

