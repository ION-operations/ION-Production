# Stores System
## Zustand State Management for IDE

**Created:** 2025-11-08  
**Agent:** Aether  
**Purpose:** Centralized state management for IDE  
**Status:** Production Ready ✅

---

## 🎯 **OVERVIEW**

The stores system provides centralized state management using Zustand:
- **Panel Store:** Panel state, layout, and presets
- **Future Stores:** Settings, theme, user preferences

---

## 🚀 **QUICK START**

### **Panel Store:**
```typescript
import { usePanelStore } from '@/stores'

function MyComponent() {
  const { panels, addPanel, movePanel } = usePanelStore()
  
  // Add panel
  const handleAdd = () => {
    addPanel({
      id: 'new-panel',
      zone: 'right',
      size: 400,
      visible: true,
      order: 0
    })
  }
  
  // Move panel
  const handleMove = () => {
    movePanel('file-explorer', 'bottom', 0)
  }
  
  return (
    <div>
      {Object.values(panels).map(panel => (
        <div key={panel.id}>{panel.id}</div>
      ))}
    </div>
  )
}
```

---

## 📚 **STORES REFERENCE**

### **usePanelStore**

Panel state management store.

**State:**
- `panels`: Record<PanelId, PanelConfig>
- `activePanels`: Record<PanelZone, PanelId[]>
- `layoutPresets`: Record<string, LayoutPreset>
- `currentPreset`: string | undefined

**Actions:**
- `addPanel(panel: PanelConfig): void`
- `removePanel(panelId: PanelId): void`
- `updatePanel(panelId: PanelId, updates: Partial<PanelConfig>): void`
- `movePanel(panelId: PanelId, targetZone: PanelZone, order?: number): void`
- `togglePanel(panelId: PanelId): void`
- `setPanelSize(panelId: PanelId, size: number): void`
- `setPanelOrder(panelId: PanelId, order: number): void`
- `saveLayoutPreset(name: string, description: string): void`
- `loadLayoutPreset(presetName: string): void`
- `deleteLayoutPreset(presetName: string): void`
- `getLayoutPreset(presetName: string): LayoutPreset | undefined`
- `getPanelsByZone(zone: PanelZone): PanelConfig[]`
- `getActivePanel(zone: PanelZone): PanelConfig | undefined`
- `resetLayout(): void`

---

## 💡 **USAGE PATTERNS**

### **Pattern 1: Panel Management**
```typescript
const { panels, addPanel, removePanel } = usePanelStore()

// Add panel
addPanel({
  id: 'debug-console',
  zone: 'bottom',
  size: 300,
  visible: true,
  order: 0
})

// Remove panel
removePanel('debug-console')
```

### **Pattern 2: Layout Presets**
```typescript
const { saveLayoutPreset, loadLayoutPreset } = usePanelStore()

// Save current layout
saveLayoutPreset('coding', 'Optimized for coding')

// Load saved layout
loadLayoutPreset('coding')
```

### **Pattern 3: Panel Selection**
```typescript
const { getPanelsByZone, getActivePanel } = usePanelStore()

// Get all panels in left zone
const leftPanels = getPanelsByZone('left')

// Get active panel in right zone
const activeRightPanel = getActivePanel('right')
```

### **Pattern 4: Performance Optimization**
```typescript
import { usePanelStore } from '@/stores'
import { shallow } from 'zustand/shallow'

// Only re-render when specific values change
const panels = usePanelStore(state => state.panels, shallow)
```

---

## 🔧 **PERSISTENCE**

Panel store uses Zustand persist middleware:
- **Storage:** localStorage
- **Key:** `aether-ide-panel-store`
- **Auto-restore:** On app load
- **Selective:** Only persists panels, activePanels, layoutPresets, currentPreset

---

## 📋 **TYPE DEFINITIONS**

```typescript
export type PanelZone = 'left' | 'right' | 'top' | 'bottom' | 'main'
export type PanelId = string

export interface PanelConfig {
  id: PanelId
  zone: PanelZone
  size: number
  minSize?: number
  maxSize?: number
  visible: boolean
  order: number
}

export interface LayoutPreset {
  name: string
  description: string
  panels: Record<PanelId, PanelConfig>
  createdAt: string
}
```

---

## 🎯 **BEST PRACTICES**

1. **Use Selectors:** Use selectors for performance
2. **Shallow Comparison:** Use `shallow` for object comparisons
3. **Preset Management:** Save layouts as presets for reuse
4. **Reset Option:** Provide reset layout option for users
5. **Type Safety:** Use TypeScript types for all operations

---

## 📖 **EXAMPLES**

See `panelStore.ts` for complete implementation.

---

**Status:** Production Ready ✅  
**Version:** 1.0.0  
**Last Updated:** 2025-11-08

