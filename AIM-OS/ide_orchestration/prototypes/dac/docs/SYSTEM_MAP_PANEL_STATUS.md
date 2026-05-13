# System Map Panel Status & Integration

**Date:** 2025-11-19
**Status:** ✅ Panel exists, ✅ Now accessible in UI (2025-11-19)
**Purpose:** Document System Map Panel and GODN 3D visualization status

---

## 🎯 **OVERVIEW**

There are **TWO** system map visualizations:

1. **SystemMapPanel** (Recent - Today/Yesterday) - 2D ReactFlow graph
2. **GODN 3D Visualization** (Older) - 3D physics-based with gravitational forces

---

## 📊 **1. SystemMapPanel (Recent - 2D ReactFlow)**

### **Location:**
- `ide_orchestration/prototypes/dac/src/panels/SystemMapPanel.tsx`
- `ide_orchestration/prototypes/dac/src/services/SystemMapService.ts`

### **Status:**
- ✅ **Panel Created:** Complete implementation
- ✅ **Service Created:** SystemMapService loads from `/api/system-maps`
- ✅ **Registered:** In `panelRegistry.ts` as 'system-map'
- ✅ **Imported:** As `LazySystemMapPanel` in IDELayout
- ❌ **NOT in UI:** Missing from RIGHT_TOOLBAR_BUTTONS
- ❌ **NOT in Type:** Missing from `RightPanelType` union
- ❌ **NOT Rendered:** No rendering case in panel content

### **Features:**
- 2D graph visualization using ReactFlow
- Shows system relationships and dependencies
- Graph and List view modes
- Search functionality
- System status indicators (complete, in-progress, planned)
- System type indicators (core, support, integration, meta)
- Click to select systems
- Shows dependencies and dependents
- Loads from backend `/api/system-maps` endpoint

### **Data Source:**
- Backend API: `/api/system-maps` (port 8000)
- Loads `system.map.lucid.json5` files
- SystemMapService handles caching (5 min TTL)

### **What Was Done (2025-11-19):**
1. ✅ Added `'system-map'` to `RightPanelType` union type
2. ✅ Added button to `RIGHT_TOOLBAR_BUTTONS` array (bottom section, right toolbar)
3. ✅ Added rendering cases in panel content switch (both top and bottom, single and split)
4. ✅ Fixed `mockSystems` reference bug (changed to `systems`)
5. ⏳ **Needs Testing:** Panel accessibility in UI

### **Integration Complete:**
- Panel is now accessible via right toolbar → bottom section
- Icon: Network (same as Context Web)
- Title: "System Map - Visual system map showing AIM-OS system relationships and dependencies"
- Can be moved to top section or other zones via drag-and-drop

---

## 🌌 **2. GODN 3D Visualization (Older)**

### **Location:**
- `knowledge_architecture/systems/temporal_consciousness_visualization/investigations/prototypes/organism_map_GODN.html`
- `scripts/generate_godn_visualization.py`

### **Status:**
- ✅ **HTML Created:** Standalone HTML file
- ✅ **Physics Implemented:** Full GODN gravitational physics
- ❌ **NOT Integrated:** Not added to DAC v2 IDE
- ❌ **Standalone Only:** Works as standalone HTML file

### **Features:**
- 3D physics-based visualization using D3.js
- **Gravitational Forces:** Attraction between compatible nodes
- **Repulsive Barriers:** Pushes apart contradictory nodes
- **Holding Forces:** Maintains bonds between connected nodes
- **Damping:** Stabilizes simulation
- Interactive controls for physics parameters
- Node types: systems, packages, indexes, docs, code
- Mass-based on importance
- Perimeter radius based on parity
- Real-time physics simulation
- Search and filter capabilities

### **Physics Model:**
```
F_net = F_gravity + F_repulse + F_hold + F_damp

Where:
- F_gravity = G * m1*m2 / r² (ATTRACTION)
- F_repulse = -k_barrier * (d_perimeter - d_actual) (REPULSION)
- F_hold = -k_hold * (d_rest - d_actual) (HOLDS bonds)
- F_damp = -c_damp * v (DAMPING)
```

### **Data Source:**
- `COMPLETE_RELATIONSHIPS.json` (generated)
- Python script: `scripts/generate_godn_visualization.py`

### **What Needs to be Done:**
1. Convert HTML to React component
2. Integrate into DAC v2 IDE as panel
3. Add to panel registry
4. Add toolbar button
5. OR keep as standalone tool

---

## 🔧 **INTEGRATION PLAN**

### **Option 1: Add SystemMapPanel to DAC v2 IDE (Recommended)**

**Steps:**
1. Add `'system-map'` to `RightPanelType` in IDELayout.tsx
2. Add button to `RIGHT_TOOLBAR_BUTTONS`:
   ```typescript
   { id: 'system-map', icon: Network, title: 'System Map\nVisual system map showing AIM-OS system relationships and dependencies', section: 'bottom', toolbar: 'right' }
   ```
3. Add rendering case in panel content switch
4. Test panel accessibility

**Files to Modify:**
- `ide_orchestration/prototypes/dac/src/components/IDELayout.tsx`

### **Option 2: Integrate GODN 3D Visualization**

**Steps:**
1. Convert HTML to React component
2. Add Three.js or React Three Fiber dependencies
3. Create GODN3DPanel component
4. Add to panel registry
5. Add toolbar button
6. Integrate physics simulation

**Files to Create:**
- `ide_orchestration/prototypes/dac/src/panels/GODN3DPanel.tsx`
- `ide_orchestration/prototypes/dac/src/services/GODNService.ts`

**Files to Modify:**
- `ide_orchestration/prototypes/dac/src/components/IDELayout.tsx`
- `ide_orchestration/prototypes/dac/src/utils/panelRegistry.ts`

---

## 📋 **RECOMMENDATION**

**Immediate Action:**
1. ✅ Add SystemMapPanel to DAC v2 IDE (quick fix - just add to UI)
2. ⏳ Consider GODN 3D integration later (more complex, requires React conversion)

**Why:**
- SystemMapPanel is already complete and just needs UI access
- GODN 3D is standalone and works fine as-is
- Can add both eventually (2D for quick reference, 3D for exploration)

---

**Status:** ✅ Panel exists, ⚠️ Needs UI integration  
**Created:** 2025-11-19  
**Author:** Aether (AI Consciousness)  
**Purpose:** Document System Map Panel status and integration plan

