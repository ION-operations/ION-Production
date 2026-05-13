// Customization hooks for Max V2
// Provides panel presets, layout templates, and customization features

import { useCallback, useState } from 'react'
import { usePanelStore } from '../store/panelStore'
import type { PanelType, ZoneType } from '../types/Panel.types'

export interface PanelPreset {
  id: string
  name: string
  description: string
  panels: Array<{
    type: PanelType
    zone: ZoneType
    size: number
    visible: boolean
    expanded: boolean
  }>
}

export interface LayoutTemplate {
  id: string
  name: string
  description: string
  category: 'coding' | 'debugging' | 'reviewing' | 'planning' | 'custom'
  zones: Array<{
    type: ZoneType
    size: number
    visible: boolean
  }>
  panels: Array<{
    type: PanelType
    zone: ZoneType
    size: number
    visible: boolean
  }>
}

export const useCustomization = () => {
  const { addPanel, updatePanel } = usePanelStore()
  const [presets, setPresets] = useState<PanelPreset[]>([])
  const [templates, setTemplates] = useState<LayoutTemplate[]>([])

  // Panel Presets
  const createPreset = useCallback((preset: PanelPreset) => {
    setPresets((prev) => [...prev, preset])
  }, [])

  const applyPreset = useCallback(
    (presetId: string) => {
      const preset = presets.find((p) => p.id === presetId)
      if (!preset) return

      preset.panels.forEach((panelConfig) => {
        addPanel({
          id: `panel-${Date.now()}-${Math.random()}`,
          type: panelConfig.type,
          zone: panelConfig.zone,
          size: panelConfig.size,
          minSize: 150,
          maxSize: 600,
          visible: panelConfig.visible,
          expanded: panelConfig.expanded,
          pinned: false,
          order: 0,
          settings: {},
        })
      })
    },
    [presets, addPanel]
  )

  const deletePreset = useCallback((presetId: string) => {
    setPresets((prev) => prev.filter((p) => p.id !== presetId))
  }, [])

  // Layout Templates
  const createTemplate = useCallback((template: LayoutTemplate) => {
    setTemplates((prev) => [...prev, template])
  }, [])

  const applyTemplate = useCallback(
    (templateId: string) => {
      const template = templates.find((t) => t.id === templateId)
      if (!template) return

      // Apply template zones and panels
      template.panels.forEach((panelConfig) => {
        addPanel({
          id: `panel-${Date.now()}-${Math.random()}`,
          type: panelConfig.type,
          zone: panelConfig.zone,
          size: panelConfig.size,
          minSize: 150,
          maxSize: 600,
          visible: panelConfig.visible,
          expanded: true,
          pinned: false,
          order: 0,
          settings: {},
        })
      })
    },
    [templates, addPanel]
  )

  const deleteTemplate = useCallback((templateId: string) => {
    setTemplates((prev) => prev.filter((t) => t.id !== templateId))
  }, [])

  // Initialize default templates
  const initializeDefaultTemplates = useCallback(() => {
    const defaultTemplates: LayoutTemplate[] = [
      {
        id: 'template-coding',
        name: 'Coding',
        description: 'Optimized for coding workflow',
        category: 'coding',
        zones: [
          { type: 'left', size: 250, visible: true },
          { type: 'right', size: 350, visible: true },
          { type: 'bottom', size: 250, visible: true },
        ],
        panels: [
          { type: 'file-explorer', zone: 'left', size: 100, visible: true },
          { type: 'outline', zone: 'right', size: 50, visible: true },
          { type: 'terminal', zone: 'bottom', size: 50, visible: true },
          { type: 'problems', zone: 'bottom', size: 50, visible: true },
        ],
      },
      {
        id: 'template-debugging',
        name: 'Debugging',
        description: 'Optimized for debugging workflow',
        category: 'debugging',
        zones: [
          { type: 'left', size: 250, visible: true },
          { type: 'right', size: 350, visible: true },
          { type: 'bottom', size: 300, visible: true },
        ],
        panels: [
          { type: 'file-explorer', zone: 'left', size: 50, visible: true },
          { type: 'debug-console', zone: 'bottom', size: 60, visible: true },
          { type: 'problems', zone: 'bottom', size: 40, visible: true },
          { type: 'timeline', zone: 'right', size: 50, visible: true },
        ],
      },
      {
        id: 'template-reviewing',
        name: 'Code Review',
        description: 'Optimized for code review workflow',
        category: 'reviewing',
        zones: [
          { type: 'left', size: 300, visible: true },
          { type: 'right', size: 400, visible: true },
          { type: 'bottom', size: 200, visible: true },
        ],
        panels: [
          { type: 'file-explorer', zone: 'left', size: 50, visible: true },
          { type: 'main-chat', zone: 'right', size: 60, visible: true },
          { type: 'problems', zone: 'bottom', size: 100, visible: true },
        ],
      },
    ]

    setTemplates(defaultTemplates)
  }, [])

  return {
    presets,
    templates,
    createPreset,
    applyPreset,
    deletePreset,
    createTemplate,
    applyTemplate,
    deleteTemplate,
    initializeDefaultTemplates,
  }
}

