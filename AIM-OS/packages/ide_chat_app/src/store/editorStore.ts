import { create } from 'zustand'

export interface EditorTab {
  id: string
  fileName: string
  content: string
  language: string
  isDirty: boolean
  isPinned: boolean
  readOnly?: boolean
}

interface EditorState {
  tabs: EditorTab[]
  activeTabId: string | null
  openTab: (tab: Omit<EditorTab, 'isDirty' | 'isPinned'>) => string
  closeTab: (tabId: string) => void
  setActiveTab: (tabId: string | null) => void
  updateTabContent: (tabId: string, content: string) => void
  markTabDirty: (tabId: string, isDirty: boolean) => void
  togglePinTab: (tabId: string) => void
  getActiveTab: () => EditorTab | null
}

export const useEditorStore = create<EditorState>((set, get) => ({
  tabs: [],
  activeTabId: null,

  openTab: (tab) => {
    const tabs = get().tabs
    const existingTab = tabs.find(t => t.fileName === tab.fileName)
    
    if (existingTab) {
      set({ activeTabId: existingTab.id })
      return existingTab.id
    }

    const newTab: EditorTab = {
      ...tab,
      id: `tab_${Date.now()}`,
      isDirty: false,
      isPinned: false,
    }

    set({
      tabs: [...tabs, newTab],
      activeTabId: newTab.id,
    })

    return newTab.id
  },

  closeTab: (tabId) => {
    const tabs = get().tabs
    const tab = tabs.find(t => t.id === tabId)
    
    // Don't close if dirty and not saved
    if (tab?.isDirty) {
      // TODO: Show save prompt
      return
    }

    const newTabs = tabs.filter(t => t.id !== tabId)
    const activeTabId = get().activeTabId === tabId
      ? newTabs.length > 0 ? newTabs[newTabs.length - 1].id : null
      : get().activeTabId

    set({
      tabs: newTabs,
      activeTabId,
    })
  },

  setActiveTab: (tabId) => {
    set({ activeTabId: tabId })
  },

  updateTabContent: (tabId, content) => {
    const tabs = get().tabs
    const tab = tabs.find(t => t.id === tabId)
    if (!tab) return

    const isDirty = content !== tab.content

    set({
      tabs: tabs.map(t =>
        t.id === tabId
          ? { ...t, content, isDirty }
          : t
      ),
    })
  },

  markTabDirty: (tabId, isDirty) => {
    const tabs = get().tabs
    set({
      tabs: tabs.map(t =>
        t.id === tabId ? { ...t, isDirty } : t
      ),
    })
  },

  togglePinTab: (tabId) => {
    const tabs = get().tabs
    set({
      tabs: tabs.map(t =>
        t.id === tabId ? { ...t, isPinned: !t.isPinned } : t
      ),
    })
  },

  getActiveTab: () => {
    const { tabs, activeTabId } = get()
    return tabs.find(t => t.id === activeTabId) || null
  },
}))
