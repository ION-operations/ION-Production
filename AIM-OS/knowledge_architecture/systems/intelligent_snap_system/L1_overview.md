---
id: "intelligent_snap_system_l1"
type: "system_overview"
system: "intelligent_snap_system"
title: "Intelligent Snap System - Overview"
version: "2.0.0"
created: "2025-12-03"
author: "Aether"
status: "production_ready"
word_count: 950
tags: ["3d", "snapping", "alignment", "lumin3d"]
---

# Intelligent Snap System - Overview (L1)

## **The Problem**

Traditional 3D modeling tools have primitive snapping:
- **Grid-only:** Just snap to grid, nothing intelligent
- **No visual feedback:** Can't preview position before snapping
- **Manual alignment:** Spend 5-10 minutes per object positioning
- **No AI assistance:** No understanding of layout intent
- **Poor UX:** Trial-and-error until alignment looks right

This creates frustration and slow workflows, especially for complex scenes.

## **The Solution: 8-Type Intelligent Snap System with Ghost Preview**

**Lumin3D's snap system combines:**
1. **8 intelligent snap types** (from grid to AI layout inference)
2. **Real-time ghost preview** when hovering snap options3. **Physics-based attraction** (magnetic + gravity)
4. **AI semantic understanding** of UI layouts
5. **Performance optimization** via LOD for large models

---

## **8 Snap Types (Existing Implementation)**

### **1. Grid Snapping (Classic)**
**What:** Align to pixel-perfect grid system  
**Use Case:** Precise positioning, technical drawings  
**Settings:**
- Grid size: 5px (fine) to 50px (coarse)
- Threshold: 5px-50px snap radius
- Visual: Grid lines displayed on canvas

**Example:** Positioning UI elements in 10px grid for consistency

---

### **2. Element Snapping (Alignment)**
**What:** Snap to edges and centers of other elements  
**Features:**
- Edge detection (top, right, bottom, left)
- Center alignment (horizontal, vertical, both)
- Distance measurements shown
- Color-coded snap lines:
  - Blue: Edge alignment
  - Green: Center alignment
  - Purple: Distributed spacing

**Example:** Aligning buttons in a toolbar to each other's edges

---

### **3. Guide Snapping (Manual)**
**What:** Snap to user-created guide lines  
**Features:**
- Drag guides from rulers
- Lock guides to prevent accidental movement
- Auto-hide when not snapping
- Customizable guide colors

**Example:** Creating consistent margins across a design

---

### **4. Magnetic Snapping (Physics-Based)**
**What:** Magnetic attraction to nearby elements  
**How it works:**
```typescript
// Magnetic force calculation
F_magnetic = MagneticStrength * (1 / distance²) * mass

// Gradually pulls object toward nearby snap points
if (distance < MagneticRadius) {
  position += (targetPosition - position) * MagneticStrength
}
```

**Settings:**
- Magnetic strength: 0-100% (default 75%)
- Magnetic radius: 15px-100px
- Visual: Pulsing glow around snap targets

**Example:** Elements "sucked into" alignment automatically as you drag near

---

### **5. Semantic Snapping (AI-Powered)**
**What:** Smart snapping to UI component areas  
**AI Features:**
- Recognizes UI patterns (header, sidebar, footer, etc.)
- Detects semantic zones (nav, content, aside)
- Infers layout intent from existing elements
- Suggests optimal placement

**Example:** New button automatically snaps to toolbar zone, not content area

---

### **6. Gravity Snapping (CSS Layout-Aware)**
**What:** Intelligent layout-aware positioning using CSS gravity fields  
**How it works:**
```typescript
// CSS Gravity calculation
gravityWell = analyzeLayoutContext(targetElement)

if (gravityWell.display === 'flex') {
  gravityForce = calculateFlexGravity(position, gravityWell)
  position += gravityForce * GravityStrength
}
```

**Features:**
- Flexbox flow prediction
- CSS Grid cell optimization
- Responsive breakpoint awareness
- Parent-child relationship understanding

**Example:** Elements automatically flow into flexbox containers with proper spacing

---

### **7. Fluid Dynamics (Natural Flow)**
**What:** Elements flow and adjust naturally like liquid  
**Physics:**
- Liquid-like element behavior
- Pressure-based repositioning
- Flow visualization particles
- Adaptive container sizing

**Visual Feedback:**
- Animated flow particles
- Ripple effects when inserting
- Other elements smoothly adjust
- Container expands/contracts naturally

**Example:** Inserting element into list pushes others down smoothly

---

### **8. Layout Inference (AI Pattern Recognition)**
**What:** AI-powered layout pattern recognition and prediction  
**ML Features:**
- Learns from existing layout patterns
- Predicts user intent
- Suggests optimal positions based on context
- Adapts to user's design style over time

**Predictions:**
- "Snap to match existing button spacing"
- "Align with sidebar pattern"
- "Continue grid rhythm"
- "Match existing component layout"

**Example:** AI recognizes 3-column card layout, suggests 4th card position automatically

---

## **Ghost Preview System (NEW - Phase 3)**

### **The Innovation**

When hovering over snap option buttons in the snap panel, show a **transparent ghost copy** of the object at the target position.

### **User Flow**

1. User selects object to snap
2. Snap panel appears with options:
   - Snap to Top
   - Snap to Right  
   - Snap to Bottom
   - Snap to Left
   - Snap to Center X
   - Snap to Center Y
   - Snap to Center XY
3. **User hovers "Snap to Top" button**
4. **→ Ghost appears** showing object at top position (transparent, 50% opacity)
5. User sees exact final position before clicking
6. User clicks button → Object snaps, ghost disappears

### **Ghost Visual Design**

**Ghost Object Appearance:**
- **Opacity:** 50% transparent
- **Material:** Wireframe + transparent fill
- **Color:** Cyan (#00ffff) for valid, Yellow (#ffff00) for tight fit, Red (#ff0000) for collision
- **Measurements:** Distance from current position shown
- **Snap Lines:** Alignment guides displayed

**Performance Optimization (LOD):**

| Object Complexity | Ghost Rendering | Performance |
|-------------------|-----------------|-------------|
| **Simple** (<1k polys) | Full geometry + materials | <5ms ✅ |
| **Medium** (1k-10k polys) | 50% polygon reduction | <10ms ✅ |
| **Large** (10k-100k polys) | Bounding box + wireframe | <15ms ✅ |
| **Huge** (>100k polys) | Bounding box only | <20ms ✅ |

**Auto-Detection:**
```typescript
const polyCount = object.geometry.attributes.position.count / 3

if (polyCount < 1000) {
  return 'full_detail'
} else if (polyCount < 10000) {
  return 'simplified_mesh'
} else if (polyCount < 100000) {
  return 'wireframe'
} else {
  return 'bounding_box'
}
```

---

## **Snap Presets (Quick Configuration)**

### **1. Precise Mode**
- Grid: 5px
- Threshold: 8px
- Gravity: 40%
- Magnetic: 60%
- Best for: Technical drawings, UI design

### **2. Balanced Mode (Default)**
- Grid: 10px
- Threshold: 15px
- Gravity: 60%
- Magnetic: 75%
- Best for: General 3D modeling

### **3. Magnetic Mode**
- Grid: 15px
- Threshold: 20px
- Gravity: 80%
- Magnetic: 90%
- Best for: Quick roughing, concept work

### **4. Fluid Mode**
- Grid: 20px
- Threshold: 25px
- Gravity: 90%
- Magnetic: 95%
- Fluid: 100%
- Best for: Organic layouts, responsive design

---

## **Visual Feedback Options**

User can toggle:
- ✅ **Show Snap Lines** - Alignment guides during drag
- ✅ **Show Gravity Wells** - Visualize CSS gravity fields
- ✅ **Show Magnetic Fields** - Display magnetic attraction zones
- ✅ **Show Fluid Flow** - Animate element flow adjustments
- ✅ **Show Semantic Zones** - Highlight UI component areas
- ✅ **Show Measurements** - Display dimensions and distances
- ✅ **Show CSS Properties** - Generated CSS in tooltips

---

## **Integration with Lumin3D**

### **Existing Code Locations**

1. **SnapConfigPanel.tsx** - Configuration UI (409 lines)
   - 8 snap type toggles
   - 6 fine-tuning sliders
   - 4 preset buttons
   - 7 visual feedback options

2. **Scene3D.tsx** - 3D rendering (2545 lines)
   - `renderSnapPreview()` - Basic snap visualization
   - `renderPartHighlight()` - Part highlighting for snapping
   - Ghost preview foundation exists ✅

3. **Canvas.tsx** - 2D implementation (778 lines)
   - Layout inference logic
   - Fluid dynamics calculations
   - Semantic zone detection

### **New Components Needed**

1. **GhostPreviewRenderer.tsx** (NEW)
   - Hover-triggered ghost rendering
   - LOD optimization
   - Performance monitoring

2. **LODManager.ts** (NEW)
   - Auto-detect polygon count
   - Generate simplified meshes
   - Cache LOD versions

3. **SnapOptionPanel.tsx** (Enhancement)
   - Add hover listeners to snap buttons
   - Trigger ghost preview on hover
   - Calculate target positions

---

## **Success Metrics**

### **Phase 1 (Existing - Complete)**
- ✅ 8 snap types implemented
- ✅ Basic snap preview working
- ✅ Configuration panel complete

### **Phase 2 (NEW - In Progress)**
- ⏳ Hover panel ghost preview
- ⏳ LOD optimization
- ⏳ Performance targets met

**Target Metrics (Phase 2):**
- Ghost render time: <20ms for all object types
- Frame rate: 60 FPS maintained during preview
- User testing: 80%+ prefer ghost preview vs no preview
- Positioning time: 70%+ reduction (10 min → 3 min avg)

---

**Next:** Read L2 for detailed ghost preview architecture and implementation design.

