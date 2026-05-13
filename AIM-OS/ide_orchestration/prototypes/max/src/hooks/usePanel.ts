// Panel-specific hooks for Max V2
// Provides panel management, state, and lifecycle hooks

import { useCallback } from 'react'
import { usePanelStore } from '../store/panelStore'
import type { Panel, ZoneType } from '../types/Panel.types'

export const usePanel = (panelId: string) => {
  const {
    panels,
    selectedPanel,
    updatePanel,
    deletePanel,
    movePanel,
    resizePanel,
    setSelectedPanel,
  } = usePanelStore()

  const panel = panels.find((p) => p.id === panelId)

  const update = useCallback(
    (updates: Partial<Panel>) => {
      updatePanel(panelId, updates)
    },
    [panelId, updatePanel]
  )

  const remove = useCallback(() => {
    deletePanel(panelId)
  }, [panelId, deletePanel])

  const move = useCallback(
    (targetZone: ZoneType) => {
      movePanel(panelId, targetZone)
    },
    [panelId, movePanel]
  )

  const resize = useCallback(
    (size: number) => {
      resizePanel(panelId, size)
    },
    [panelId, resizePanel]
  )

  const select = useCallback(() => {
    setSelectedPanel(panel || null)
  }, [panel, setSelectedPanel])

  const toggleVisibility = useCallback(() => {
    if (panel) {
      updatePanel(panelId, { visible: !panel.visible })
    }
  }, [panel, panelId, updatePanel])

  const toggleExpanded = useCallback(() => {
    if (panel) {
      updatePanel(panelId, { expanded: !panel.expanded })
    }
  }, [panel, panelId, updatePanel])

  const togglePinned = useCallback(() => {
    if (panel) {
      updatePanel(panelId, { pinned: !panel.pinned })
    }
  }, [panel, panelId, updatePanel])

  return {
    panel,
    isSelected: selectedPanel?.id === panelId,
    update,
    remove,
    move,
    resize,
    select,
    toggleVisibility,
    toggleExpanded,
    togglePinned,
  }
}

