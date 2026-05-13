// Helper function to wrap panels with BasePanel and toggle functionality
// This file provides utilities for panel updates

export const createPanelWrapper = (panelId: string, togglePanelVisibility: (id: string) => void) => {
  return () => {
    const handleTogglePanel = (e: CustomEvent) => {
      if (e.detail.panelId === panelId) {
        togglePanelVisibility(panelId)
      }
    }
    window.addEventListener('togglePanel', handleTogglePanel as EventListener)
    return () => {
      window.removeEventListener('togglePanel', handleTogglePanel as EventListener)
    }
  }
}

