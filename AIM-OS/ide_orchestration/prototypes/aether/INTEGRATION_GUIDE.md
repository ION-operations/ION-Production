# Integration Guide
## Integrating Panel Store with Layout Component

**Created:** 2025-11-08  
**Agent:** Aether  
**Purpose:** Guide for integrating panelStore with AetherIDELayout  
**Status:** Integration Guide Complete

---

## 🎯 **INTEGRATION OVERVIEW**

This guide shows how to integrate the Zustand panel store with the AetherIDELayout component to enable:
- Panel state management
- Layout persistence
- Panel presets
- Drag-drop panel movement

---

## 🔧 **INTEGRATION STEPS**

### **Step 1: Import Panel Store**

```typescript
import { usePanelStore } from '@/stores'
import type { PanelZone, PanelId } from '@/stores'
```

### **Step 2: Replace Local State**

**Before:**
```typescript
const [leftPanel, setLeftPanel] = useState<LeftPanelType>('explorer')
const [mainContent, setMainContent] = useState<MainContentType>('code')
const [rightPanel, setRightPanel] = useState<RightPanelType>('context-web')
const [bottomPanel, setBottomPanel] = useState<BottomPanelType>('terminal')
```

**After:**
```typescript
const { 
  panels, 
  getPanelsByZone, 
  getActivePanel,
  movePanel,
  togglePanel 
} = usePanelStore()

// Get active panels per zone
const leftPanels = getPanelsByZone('left')
const activeLeftPanel = getActivePanel('left')
```

### **Step 3: Initialize Default Panels**

```typescript
useEffect(() => {
  // Initialize default panels if not already set
  const { panels: currentPanels } = usePanelStore.getState()
  
  if (Object.keys(currentPanels).length === 0) {
    // Add default panels
    usePanelStore.getState().addPanel({
      id: 'file-explorer',
      zone: 'left',
      size: 300,
      minSize: 200,
      maxSize: 400,
      visible: true,
      order: 0
    })
    
    // Add more default panels...
  }
}, [])
```

### **Step 4: Update Panel Rendering**

**Before:**
```typescript
{leftPanel === 'explorer' && <FileExplorerPanel data={mockFileTree} />}
{leftPanel === 'components' && <ComponentLibraryPanel />}
```

**After:**
```typescript
{leftPanels.map(panel => {
  if (!panel.visible) return null
  
  switch (panel.id) {
    case 'file-explorer':
      return <FileExplorerPanel key={panel.id} data={mockFileTree} />
    case 'components':
      return <ComponentLibraryPanel key={panel.id} />
    // ... more cases
    default:
      return null
  }
})}
```

### **Step 5: Add Panel Controls**

```typescript
// Panel toggle button
<button
  onClick={() => togglePanel('file-explorer')}
  className={panels['file-explorer']?.visible ? 'active' : ''}
>
  Files
</button>

// Panel move handler
const handleMovePanel = (panelId: PanelId, targetZone: PanelZone) => {
  movePanel(panelId, targetZone)
}
```

### **Step 6: Add Layout Preset UI**

```typescript
const { 
  layoutPresets, 
  saveLayoutPreset, 
  loadLayoutPreset,
  currentPreset 
} = usePanelStore()

// Save current layout
const handleSaveLayout = () => {
  const name = prompt('Layout name:')
  if (name) {
    saveLayoutPreset(name, 'Custom layout')
  }
}

// Load layout
const handleLoadLayout = (presetName: string) => {
  loadLayoutPreset(presetName)
}

// Layout preset selector
<select value={currentPreset || ''} onChange={(e) => loadLayoutPreset(e.target.value)}>
  <option value="">Default</option>
  {Object.keys(layoutPresets).map(name => (
    <option key={name} value={name}>{name}</option>
  ))}
</select>
```

---

## 📋 **COMPLETE INTEGRATION EXAMPLE**

```typescript
import React, { useEffect } from 'react'
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels'
import { usePanelStore } from '@/stores'
import type { PanelZone, PanelId } from '@/stores'
import { FileExplorerPanel, CodeEditorPanel } from './panels'

export const AetherIDELayout: React.FC = () => {
  const {
    panels,
    getPanelsByZone,
    getActivePanel,
    movePanel,
    togglePanel,
    setPanelSize,
    layoutPresets,
    saveLayoutPreset,
    loadLayoutPreset,
    currentPreset
  } = usePanelStore()

  // Initialize default panels
  useEffect(() => {
    const { panels: currentPanels } = usePanelStore.getState()
    if (Object.keys(currentPanels).length === 0) {
      // Initialize defaults
      usePanelStore.getState().addPanel({
        id: 'file-explorer',
        zone: 'left',
        size: 300,
        visible: true,
        order: 0
      })
      // ... more defaults
    }
  }, [])

  // Get panels by zone
  const leftPanels = getPanelsByZone('left')
  const rightPanels = getPanelsByZone('right')
  const bottomPanels = getPanelsByZone('bottom')
  const mainPanels = getPanelsByZone('main')

  return (
    <div className="h-screen w-screen flex flex-col">
      {/* Top Bar with Layout Controls */}
      <div className="h-12 bg-gray-800 border-b border-gray-700 flex items-center justify-between px-4">
        <div>Aether IDE</div>
        <div className="flex items-center gap-2">
          {/* Layout Preset Selector */}
          <select
            value={currentPreset || ''}
            onChange={(e) => e.target.value && loadLayoutPreset(e.target.value)}
            className="text-xs bg-gray-700 text-gray-300 px-2 py-1 rounded"
          >
            <option value="">Default Layout</option>
            {Object.keys(layoutPresets).map(name => (
              <option key={name} value={name}>{name}</option>
            ))}
          </select>
          
          {/* Save Layout Button */}
          <button
            onClick={() => {
              const name = prompt('Layout name:')
              if (name) saveLayoutPreset(name, 'Custom layout')
            }}
            className="text-xs bg-blue-600 text-white px-2 py-1 rounded hover:bg-blue-700"
          >
            Save Layout
          </button>
        </div>
      </div>

      {/* Main Layout */}
      <PanelGroup direction="vertical" className="flex-1">
        <Panel defaultSize={75} minSize={50}>
          <PanelGroup direction="horizontal">
            {/* Left Drawer */}
            <Panel defaultSize={300} minSize={200} maxSize={400}>
              <div className="h-full bg-gray-800 border-r border-gray-700 flex flex-col">
                {/* Panel Tabs */}
                <div className="flex border-b border-gray-700">
                  {leftPanels.map(panel => (
                    <button
                      key={panel.id}
                      onClick={() => togglePanel(panel.id)}
                      className={`px-3 py-2 text-xs ${
                        panel.visible
                          ? 'bg-gray-700 text-blue-400'
                          : 'text-gray-400 hover:text-gray-200'
                      }`}
                    >
                      {panel.id}
                    </button>
                  ))}
                </div>
                
                {/* Panel Content */}
                <div className="flex-1 overflow-auto">
                  {leftPanels
                    .filter(panel => panel.visible)
                    .map(panel => {
                      switch (panel.id) {
                        case 'file-explorer':
                          return <FileExplorerPanel key={panel.id} />
                        // ... more cases
                        default:
                          return null
                      }
                    })}
                </div>
              </div>
            </Panel>

            <PanelResizeHandle className="w-1 bg-gray-700 hover:bg-gray-600" />

            {/* Main Content */}
            <Panel defaultSize={50} minSize={30}>
              {/* Similar structure for main content */}
            </Panel>

            <PanelResizeHandle className="w-1 bg-gray-700 hover:bg-gray-600" />

            {/* Right Drawer */}
            <Panel defaultSize={400} minSize={300} maxSize={600}>
              {/* Similar structure for right drawer */}
            </Panel>
          </PanelGroup>
        </Panel>

        <PanelResizeHandle className="h-1 bg-gray-700 hover:bg-gray-600" />

        {/* Bottom Drawer */}
        <Panel defaultSize={300} minSize={200} maxSize={600}>
          {/* Similar structure for bottom drawer */}
        </Panel>
      </PanelGroup>
    </div>
  )
}
```

---

## 🎯 **BEST PRACTICES**

1. **Initialize Defaults:** Always initialize default panels on mount
2. **Filter Visible:** Only render visible panels
3. **Handle Missing:** Handle missing panel IDs gracefully
4. **Preserve State:** Use Zustand persist for state persistence
5. **Performance:** Use selectors to avoid unnecessary re-renders

---

## 🔄 **MIGRATION CHECKLIST**

- [ ] Import usePanelStore
- [ ] Replace local state with panelStore
- [ ] Initialize default panels
- [ ] Update panel rendering logic
- [ ] Add panel controls (toggle, move)
- [ ] Add layout preset UI
- [ ] Test panel persistence
- [ ] Test layout presets
- [ ] Verify panel state restoration

---

**Status:** Integration Guide Complete  
**Next:** Apply integration to AetherIDELayout component 💙

