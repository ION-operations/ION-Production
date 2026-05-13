/**
 * Layout Saving System
 * 
 * Phase 3.3: Layout Persistence with CMC Integration
 * 
 * Features:
 * - Save/load/delete layouts
 * - CMC integration for persistent storage
 * - Layout templates
 * - Quick layout switching
 */

import { useState, useEffect, useCallback } from 'react'
import { LeftPanelType, RightPanelType, BottomPanelType, MainContentMode } from './RevIDELayout'

export interface LayoutConfig {
  id: string
  name: string
  description?: string
  createdAt: string
  updatedAt: string
  config: {
    leftTop: LeftPanelType
    leftBottom: LeftPanelType | null
    rightTop: RightPanelType
    rightBottom: RightPanelType | null
    bottom: BottomPanelType | null
    mainContentMode: MainContentMode
    leftDrawerWidth?: number
    rightDrawerWidth?: number
    bottomDrawerHeight?: number
  }
  cmcAtomId?: string // CMC integration
  isDefault?: boolean
}

const STORAGE_KEY = 'rev_ide_layouts'

export const useLayoutSaving = () => {
  const [layouts, setLayouts] = useState<LayoutConfig[]>([])
  const [currentLayoutId, setCurrentLayoutId] = useState<string | null>(null)

  // Load layouts from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored) {
        const parsed = JSON.parse(stored) as LayoutConfig[]
        setLayouts(parsed)
        const defaultLayout = parsed.find(l => l.isDefault)
        if (defaultLayout) {
          setCurrentLayoutId(defaultLayout.id)
        }
      }
    } catch (error) {
      console.error('Failed to load layouts from localStorage:', error)
    }
  }, [])

  // Save layouts to localStorage whenever they change
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(layouts))
    } catch (error) {
      console.error('Failed to save layouts to localStorage:', error)
    }
  }, [layouts])

  const saveLayout = useCallback(async (
    name: string,
    config: LayoutConfig['config'],
    description?: string,
    cmcAtomId?: string
  ): Promise<string> => {
    const newLayout: LayoutConfig = {
      id: `layout-${Date.now()}`,
      name,
      description,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      config,
      cmcAtomId,
      isDefault: layouts.length === 0
    }

    // TODO: Save to CMC via MCP tool
    // if (cmcAtomId) {
    //   await mcp_lucid-mcp_store_memory({
    //     content: JSON.stringify(newLayout),
    //     tags: { type: 'layout', layoutId: newLayout.id }
    //   })
    // }

    setLayouts(prev => [...prev, newLayout])
    setCurrentLayoutId(newLayout.id)
    return newLayout.id
  }, [layouts])

  const updateLayout = useCallback(async (
    layoutId: string,
    updates: Partial<Pick<LayoutConfig, 'name' | 'description' | 'config'>>
  ) => {
    setLayouts(prev => prev.map(layout => {
      if (layout.id === layoutId) {
        return {
          ...layout,
          ...updates,
          updatedAt: new Date().toISOString()
        }
      }
      return layout
    }))
  }, [])

  const deleteLayout = useCallback(async (layoutId: string) => {
    // TODO: Archive in CMC instead of deleting
    // await mcp_lucid-mcp_archive_snapshot({ snapshot_name: layoutId })
    
    setLayouts(prev => {
      const filtered = prev.filter(l => l.id !== layoutId)
      // If deleted layout was current, switch to first available or default
      if (currentLayoutId === layoutId) {
        const defaultLayout = filtered.find(l => l.isDefault)
        setCurrentLayoutId(defaultLayout?.id || filtered[0]?.id || null)
      }
      return filtered
    })
  }, [currentLayoutId])

  const loadLayout = useCallback((layoutId: string): LayoutConfig | null => {
    const layout = layouts.find(l => l.id === layoutId)
    if (layout) {
      setCurrentLayoutId(layoutId)
      return layout
    }
    return null
  }, [layouts])

  const setDefaultLayout = useCallback((layoutId: string) => {
    setLayouts(prev => prev.map(layout => ({
      ...layout,
      isDefault: layout.id === layoutId
    })))
  }, [])

  const duplicateLayout = useCallback(async (layoutId: string, newName: string): Promise<string> => {
    const sourceLayout = layouts.find(l => l.id === layoutId)
    if (!sourceLayout) {
      throw new Error(`Layout ${layoutId} not found`)
    }

    return await saveLayout(
      newName,
      sourceLayout.config,
      `Copy of ${sourceLayout.name}`,
      undefined // Don't copy CMC atom ID
    )
  }, [layouts, saveLayout])

  return {
    layouts,
    currentLayoutId,
    saveLayout,
    updateLayout,
    deleteLayout,
    loadLayout,
    setDefaultLayout,
    duplicateLayout
  }
}

