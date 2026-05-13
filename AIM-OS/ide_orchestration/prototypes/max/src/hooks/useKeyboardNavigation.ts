// Keyboard Navigation Hook for Max V2
// Provides keyboard shortcuts and navigation for panels and layout

import { useEffect, useCallback } from 'react'
import { usePanelStore } from '../store/panelStore'

export interface KeyboardShortcuts {
  [key: string]: () => void
}

export const useKeyboardNavigation = () => {
  const {
    panels,
    selectedPanel,
    setSelectedPanel,
    updatePanel,
    movePanel,
    deletePanel,
  } = usePanelStore()

  // Navigate between panels
  const navigateToNextPanel = useCallback(() => {
    if (panels.length === 0) return

    const visiblePanels = panels.filter((p) => p.visible).sort((a, b) => a.order - b.order)
    if (visiblePanels.length === 0) return

    const currentIndex = selectedPanel
      ? visiblePanels.findIndex((p) => p.id === selectedPanel.id)
      : -1

    const nextIndex = (currentIndex + 1) % visiblePanels.length
    setSelectedPanel(visiblePanels[nextIndex])
  }, [panels, selectedPanel, setSelectedPanel])

  const navigateToPreviousPanel = useCallback(() => {
    if (panels.length === 0) return

    const visiblePanels = panels.filter((p) => p.visible).sort((a, b) => a.order - b.order)
    if (visiblePanels.length === 0) return

    const currentIndex = selectedPanel
      ? visiblePanels.findIndex((p) => p.id === selectedPanel.id)
      : -1

    const prevIndex = currentIndex <= 0 ? visiblePanels.length - 1 : currentIndex - 1
    setSelectedPanel(visiblePanels[prevIndex])
  }, [panels, selectedPanel, setSelectedPanel])

  // Panel actions
  const togglePanelVisibility = useCallback(() => {
    if (selectedPanel) {
      updatePanel(selectedPanel.id, { visible: !selectedPanel.visible })
    }
  }, [selectedPanel, updatePanel])

  const closeSelectedPanel = useCallback(() => {
    if (selectedPanel) {
      updatePanel(selectedPanel.id, { visible: false })
    }
  }, [selectedPanel, updatePanel])

  const deleteSelectedPanel = useCallback(() => {
    if (selectedPanel) {
      deletePanel(selectedPanel.id)
      setSelectedPanel(null)
    }
  }, [selectedPanel, deletePanel, setSelectedPanel])

  // Keyboard shortcuts
  const shortcuts: KeyboardShortcuts = {
    // Panel navigation
    'ArrowRight': navigateToNextPanel,
    'ArrowLeft': navigateToPreviousPanel,
    'Tab': navigateToNextPanel,
    'Shift+Tab': navigateToPreviousPanel,
    
    // Panel actions
    'Escape': closeSelectedPanel,
    'Delete': deleteSelectedPanel,
    'h': togglePanelVisibility, // Hide/show panel
    
    // Layout actions (to be implemented)
    'Ctrl+S': () => {
      // Save layout
      console.log('Save layout (to be implemented)')
    },
    'Ctrl+L': () => {
      // Load layout
      console.log('Load layout (to be implemented)')
    },
  }

  // Handle keyboard events
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      // Don't handle shortcuts when typing in inputs
      if (
        e.target instanceof HTMLInputElement ||
        e.target instanceof HTMLTextAreaElement ||
        (e.target instanceof HTMLElement && e.target.isContentEditable)
      ) {
        return
      }

      const key = e.shiftKey ? `Shift+${e.key}` : e.key
      const ctrlKey = e.ctrlKey || e.metaKey
      const shortcutKey = ctrlKey ? `Ctrl+${e.key}` : key

      const handler = shortcuts[shortcutKey]
      if (handler) {
        e.preventDefault()
        e.stopPropagation()
        handler()
      }
    },
    [shortcuts]
  )

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown)
    return () => {
      window.removeEventListener('keydown', handleKeyDown)
    }
  }, [handleKeyDown])

  return {
    navigateToNextPanel,
    navigateToPreviousPanel,
    togglePanelVisibility,
    closeSelectedPanel,
    deleteSelectedPanel,
    shortcuts,
  }
}

