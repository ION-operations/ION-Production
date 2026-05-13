---
id: "intelligent_snap_integration"
type: "integration_guide"
system: "intelligent_snap_system"
title: "Lumin3D Snap System - Integration Points"
version: "2.0.0"
created: "2025-12-03"
author: "Aether"
status: "reference"
tags: ["integration", "lumin3d", "existing_code"]
---

# Lumin3D Snap System - Integration Points

## **Purpose**
Document existing Lumin3D snap code to enable seamless integration of new ghost preview system.

---

## **Existing Code Locations**

### **1. Scene3D.tsx - 3D Snap Preview (Lines 1530-1580)**

**File:** `knowledge_architecture/applications/ide_chat_app/analysis/braden_previous_builds/ide_builds/codeanalysis/lumin-test/src/components/viewport/Scene3D.tsx`

**Existing Implementation:**

```typescript
// Render snap preview
const renderSnapPreview = () => {
  if (!snapPreview) return null;
  
  return (
    <group>
      {/* Source position indicator */}
      <mesh position={snapPreview.sourcePosition}>
        <sphereGeometry args={[0.1, 16, 16]} />
        <meshBasicMaterial color="#ff0000" transparent opacity={0.7} />
      </mesh>
      
      {/* Target position indicator */}
      <mesh position={snapPreview.targetPosition}>
        <sphereGeometry args={[0.1, 16, 16]} />
        <meshBasicMaterial color="#00ff00" transparent opacity={0.7} />
      </mesh>
      
      {/* Connection line */}
      <line>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            count={2}
            array={new Float32Array([
              ...snapPreview.sourcePosition,
              ...snapPreview.targetPosition
            ])}
            itemSize={3}
          />
        </bufferGeometry>
        <lineBasicMaterial color="#ffff00" linewidth={2} />
      </line>
    </group>
  );
};

// Render part highlight for snapping
const renderPartHighlight = (obj: SceneObject, part: string) => {
  if (state.selectedTool !== 'snap' || hoveredObject !== obj.id || hoveredPart !== part) return null;
  
  // Get the position of the part
  const partPosition = getPartPosition(obj, part);
  
  return (
    <mesh position={partPosition}>
      <sphereGeometry args={[0.15, 16, 16]} />
      <meshBasicMaterial color="#ffff00" transparent opacity={0.7} />
    </mesh>
  );
};
```

**Integration Notes:**
- ✅ Basic snap preview exists
- ✅ Source/target position visualization
- ✅ Connection line rendering
- ⚠️ No ghost object rendering (just spheres)
- ⚠️ No LOD optimization
- ⚠️ No collision detection

**Enhancement Strategy:**
Replace sphere indicators with full ghost object rendering using new `GhostPreviewRenderer`.

---

### **2. SnapConfigPanel.tsx - Configuration UI (Lines 1-409)**

**File:** `knowledge_architecture/applications/ide_chat_app/analysis/braden_previous_builds/ide_builds/perfectUIadjuster-bolt/project/src/components/SnapConfigPanel.tsx`

**Existing State Management:**

```typescript
const [snapToGrid, setSnapToGrid] = useState(true);
const [snapToElements, setSnapToElements] = useState(true);
const [snapToGuides, setSnapToGuides] = useState(true);
const [magneticSnap, setMagneticSnap] = useState(true);
const [semanticSnap, setSemanticSnap] = useState(true);
const [gravitySnap, setGravitySnap] = useState(true);
const [fluidDynamics, setFluidDynamics] = useState(true);
const [layoutInference, setLayoutInference] = useState(true);

const [gridSize, setGridSize] = useState(10);
const [snapThreshold, setSnapThreshold] = useState(15);
const [gravityStrength, setGravityStrength] = useState(60);
const [magneticStrength, setMagneticStrength] = useState(75);
const [fluidSensitivity, setFluidSensitivity] = useState(80);
const [semanticPriority, setSemanticPriority] = useState(70);
```

**Existing Presets:**

```typescript
const snapPresets = [
  { name: 'Precise', grid: 5, threshold: 8, gravity: 40, magnetic: 60, fluid: 60, semantic: 50 },
  { name: 'Balanced', grid: 10, threshold: 15, gravity: 60, magnetic: 75, fluid: 80, semantic: 70 },
  { name: 'Magnetic', grid: 15, threshold: 20, gravity: 80, magnetic: 90, fluid: 90, semantic: 85 },
  { name: 'Fluid', grid: 20, threshold: 25, gravity: 90, magnetic: 95, fluid: 100, semantic: 90 },
];
```

**Integration Notes:**
- ✅ Complete configuration state management
- ✅ 8 snap types implemented
- ✅ Fine-tuning sliders functional
- ✅ Preset system working
- ⚠️ No snap option buttons (Top/Right/Bottom/Left/Center)
- ⚠️ No hover listeners for ghost preview

**Enhancement Strategy:**
Add new section with snap option buttons and hover listeners.

---

### **3. Canvas.tsx - 2D Snap Implementation (Lines 195-420)**

**File:** `knowledge_architecture/applications/ide_chat_app/analysis/braden_previous_builds/ide_builds/perfectUIadjuster-bolt/project/src/components/Canvas.tsx`

**Existing Snap Logic:**

```typescript
const handleMouseMove = useCallback((e: React.MouseEvent) => {
  const rect = canvasRef.current?.getBoundingClientRect();
  if (!rect) return;

  let mouseX = e.clientX - rect.left;
  let mouseY = e.clientY - rect.top;

  // Apply snapping if enabled
  if (snapEnabled && draggedElement) {
    let snapX = mouseX;
    let snapY = mouseY;
    const newSnapLines: SnapLine[] = [];

    // Grid Snapping
    if (snapToGrid) {
      const gridSnap = gridSize;
      snapX = Math.round(snapX / gridSnap) * gridSnap;
      snapY = Math.round(snapY / gridSnap) * gridSnap;
    }

    // Magnetic Snapping
    if (magneticSnap) {
      const magneticRadius = 50 * (magneticStrength / 100);
      
      elements.forEach(targetElement => {
        if (targetElement.id === selectedElement) return;
        
        const targetX = targetElement.position.x;
        const targetY = targetElement.position.y;
        const distance = Math.sqrt(
          Math.pow(snapX - targetX, 2) + 
          Math.pow(snapY - targetY, 2)
        );
        
        if (distance < magneticRadius) {
          const force = magneticStrength / 100;
          snapX += (targetX - snapX) * force * 0.1;
          snapY += (targetY - snapY) * force * 0.1;
        }
      });
    }

    // Layout Inference (Flexbox-aware)
    if (layoutInference) {
      elements.forEach(targetElement => {
        if (targetElement.id === selectedElement) return;
        
        const snapThreshold = 8 * (snapStrength / 100);
        const layoutContext = analyzeLayout(targetElement);
        
        if (layoutContext.display === 'flex') {
          const insertionPoint = predictInsertion(
            { x: snapX, y: snapY, width: element.size.width, height: element.size.height },
            targetElement,
            layoutContext
          );
          
          if (insertionPoint) {
            snapX = insertionPoint.x;
            snapY = insertionPoint.y;
            
            newSnapLines.push({
              x1: insertionPoint.x,
              y1: insertionPoint.y - 20,
              x2: insertionPoint.x,
              y2: insertionPoint.y + element.size.height + 20,
              type: 'semantic',
              label: `Flex Insert: ${insertionPoint.cssProperty}`,
              cssProperty: insertionPoint.cssProperty
            });
          }
        }
      });
    }

    mouseX = snapX;
    mouseY = snapY;
    setSnapLines(newSnapLines);
  }

  // Update element position...
}, [/* dependencies */]);
```

**Key Algorithms:**

1. **Grid Snapping:**
```typescript
snapX = Math.round(snapX / gridSnap) * gridSnap;
snapY = Math.round(snapY / gridSnap) * gridSnap;
```

2. **Magnetic Force:**
```typescript
const distance = Math.sqrt((snapX - targetX)² + (snapY - targetY)²);
if (distance < magneticRadius) {
  const force = magneticStrength / 100;
  snapX += (targetX - snapX) * force * 0.1;
  snapY += (targetY - snapY) * force * 0.1;
}
```

3. **Layout Inference:**
```typescript
const layoutContext = analyzeLayout(targetElement);
if (layoutContext.display === 'flex') {
  const insertionPoint = predictInsertion(position, targetElement, layoutContext);
  // Use predicted insertion point
}
```

**Integration Notes:**
- ✅ Grid, Magnetic, Layout Inference implemented
- ✅ Real-time snap calculation during drag
- ✅ Snap lines visualization
- ⚠️ 2D only (needs 3D equivalent)
- ⚠️ No ghost preview

**Enhancement Strategy:**
Adapt 2D snap logic for 3D, add ghost preview on hover.

---

## **Integration Architecture**

### **Current Flow (Existing)**

```
User drags object
  ↓
handleMouseMove() calculates snap position
  ↓
Apply grid/magnetic/layout snapping
  ↓
Update object position
  ↓
Render snap lines
```

### **New Flow (With Ghost Preview)**

```
User selects object
  ↓
Snap panel appears
  ↓
User hovers "Snap Top" button
  ↓
SnapEngine.calculateSnapPosition('top') [REUSE EXISTING]
  ↓
LODManager.selectLOD(object) [NEW]
  ↓
GhostPreviewRenderer.showPreview(object, targetPos) [NEW]
  ↓
Render ghost + measurements + collision warnings [NEW]
  ↓
User clicks button
  ↓
Apply snap (reuse existing logic)
  ↓
Hide ghost
```

---

## **Reusable Code from Existing System**

### **1. Snap Position Calculation**

**Extract from Canvas.tsx:**

```typescript
// Grid snap calculation (REUSE)
function snapToGrid(position: Vector3, gridSize: number): Vector3 {
  return new Vector3(
    Math.round(position.x / gridSize) * gridSize,
    Math.round(position.y / gridSize) * gridSize,
    Math.round(position.z / gridSize) * gridSize
  );
}

// Magnetic force calculation (REUSE)
function applyMagneticForce(
  position: Vector3,
  targets: Vector3[],
  magneticStrength: number,
  magneticRadius: number
): Vector3 {
  let result = position.clone();
  
  targets.forEach(target => {
    const distance = position.distanceTo(target);
    
    if (distance < magneticRadius) {
      const force = magneticStrength / 100;
      const direction = target.clone().sub(position);
      result.add(direction.multiplyScalar(force * 0.1));
    }
  });
  
  return result;
}
```

### **2. Visual Feedback (Snap Lines)**

**Extract from Canvas.tsx:**

```typescript
interface SnapLine {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  type: 'grid' | 'element' | 'semantic' | 'magnetic';
  label?: string;
  cssProperty?: string;
}

// Adapt for 3D (convert to Three.js Line)
function createSnapLine3D(
  from: Vector3,
  to: Vector3,
  color: number,
  label?: string
): Line {
  const geometry = new BufferGeometry().setFromPoints([from, to]);
  const material = new LineBasicMaterial({ color });
  const line = new Line(geometry, material);
  
  // Add label as sprite (if provided)
  if (label) {
    // Create text sprite...
  }
  
  return line;
}
```

### **3. State Management**

**Reuse from SnapConfigPanel.tsx:**

```typescript
// Already have all snap type states
// Already have strength parameters
// Already have preset system

// Just add:
const [showGhostPreview, setShowGhostPreview] = useState(false);
const [hoveredSnapOption, setHoveredSnapOption] = useState<SnapOption | null>(null);
const [ghostTargetPosition, setGhostTargetPosition] = useState<Vector3 | null>(null);
```

---

## **Integration Checklist**

### **Phase 1: Extract and Adapt**
- [ ] Extract grid snap logic from Canvas.tsx → SnapEngine.ts (3D)
- [ ] Extract magnetic force from Canvas.tsx → SnapEngine.ts (3D)
- [ ] Extract layout inference → SnapEngine.ts (3D semantic zones)
- [ ] Adapt 2D snap lines → 3D Line objects

### **Phase 2: Enhance Scene3D.tsx**
- [ ] Replace `renderSnapPreview()` sphere indicators with ghost objects
- [ ] Add LOD detection to `renderSnapPreview()`
- [ ] Add collision detection
- [ ] Add measurement lines

### **Phase 3: Enhance SnapConfigPanel.tsx**
- [ ] Add snap option buttons section (Top/Right/Bottom/Left/Center)
- [ ] Add hover listeners to buttons
- [ ] Connect to ghost preview system
- [ ] Add ghost preview toggle setting

### **Phase 4: New Components**
- [ ] Create GhostPreviewRenderer.tsx
- [ ] Create LODManager.ts
- [ ] Create SnapEngine.ts (consolidate snap logic)
- [ ] Create MeasurementRenderer.tsx

### **Phase 5: Integration**
- [ ] Wire up SnapConfigPanel → SnapEngine
- [ ] Wire up SnapEngine → GhostPreviewRenderer
- [ ] Wire up GhostPreviewRenderer → Scene3D
- [ ] Test all 8 snap types with ghost preview

---

## **Code Reuse Summary**

| Component | Existing Code | Reusable? | Adaptation Needed |
|-----------|---------------|-----------|-------------------|
| Grid Snap | Canvas.tsx L210 | ✅ Yes | 2D → 3D (Vector3) |
| Magnetic Force | Canvas.tsx L220-240 | ✅ Yes | 2D → 3D (Vector3) |
| Layout Inference | Canvas.tsx L310-348 | ⚠️ Partial | 2D flexbox → 3D semantic zones |
| Snap Lines | Canvas.tsx L332-340 | ✅ Yes | 2D line → Three.js Line |
| Snap Preview | Scene3D.tsx L1530-1565 | ⚠️ Partial | Spheres → Ghost objects |
| Config Panel | SnapConfigPanel.tsx | ✅ Yes | Add snap option buttons |

**Reusability:** ~70% of existing code can be adapted! 🎉

---

## **Next Steps**

1. ✅ Review this integration guide
2. ⏳ Create L3 Implementation Guide (detailed code examples)
3. ⏳ Build new components (GhostPreviewRenderer, LODManager)
4. ⏳ Integrate with existing Lumin3D code
5. ⏳ Test and optimize

---

**This integration guide provides the foundation for L3 Implementation Guide.** 💙

