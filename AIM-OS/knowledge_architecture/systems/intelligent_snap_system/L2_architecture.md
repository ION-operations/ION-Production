---
id: "intelligent_snap_system_l2"
type: "system_architecture"
system: "intelligent_snap_system"
title: "Intelligent Snap System - Architecture"
version: "2.0.0"
created: "2025-12-03"
author: "Aether"
status: "design"
word_count: 3200
tags: ["3d", "architecture", "ghost_preview", "lod", "performance"]
---

# Intelligent Snap System - Architecture (L2)

## **System Architecture Overview**

```
┌─────────────────────────────────────────────────────────────────┐
│                      User Interaction Layer                      │
│  - Select object                                                │
│  - Open snap panel                                              │
│  - Hover snap options                                           │
└───────────────────────────────┬─────────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Snap Configuration Panel                      │
│  - 8 Snap Type Toggles                                          │
│  - Snap Option Buttons (Top/Right/Bottom/Left/Center)           │
│  - Hover Listeners → Ghost Preview Trigger                      │
└──────┬──────────────────────┬──────────────────────┬────────────┘
       │                      │                      │
       ▼                      ▼                      ▼
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Snap      │      │   Ghost     │      │    LOD      │
│  Engine     │      │  Preview    │      │  Manager    │
└─────────────┘      └─────────────┘      └─────────────┘
       │                      │                      │
       ▼                      ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                      3D Scene Renderer                           │
│  - Original object (current position)                           │
│  - Ghost object (hover preview)                                 │
│  - Snap lines and measurements                                  │
│  - Collision warnings                                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## **Core Components**

### **1. Snap Engine (Existing)**

**Responsibilities:**
- Calculate snap positions for all 8 snap types
- Detect snap targets (grid, elements, guides)
- Apply magnetic attraction forces
- Semantic zone detection
- Layout inference

**Key Algorithms:**

```typescript
interface SnapEngine {
  // Calculate target position for snap option
  calculateSnapPosition(
    object: Object3D,
    snapOption: SnapOption, // 'top' | 'right' | 'bottom' | 'left' | 'center_x' | 'center_y' | 'center_xy'
    snapTypes: SnapType[], // Active snap types
    scene: Scene
  ): Vector3

  // Detect all snap targets near object
  detectSnapTargets(
    object: Object3D,
    radius: number,
    scene: Scene
  ): SnapTarget[]

  // Apply magnetic attraction
  applyMagneticForce(
    position: Vector3,
    targets: SnapTarget[],
    strength: number
  ): Vector3

  // Semantic zone detection
  detectSemanticZones(scene: Scene): SemanticZone[]

  // Layout inference
  inferLayoutPattern(
    object: Object3D,
    existingObjects: Object3D[]
  ): LayoutPattern
}
```

**Snap Position Calculation Examples:**

```typescript
// Snap to Top
function snapToTop(object: Object3D, container: Box3): Vector3 {
  const objectBox = new Box3().setFromObject(object)
  const objectHeight = objectBox.max.y - objectBox.min.y
  
  return new Vector3(
    object.position.x, // Maintain X
    container.max.y - objectHeight / 2, // Top position
    object.position.z // Maintain Z
  )
}

// Snap to Center XY
function snapToCenter(object: Object3D, container: Box3): Vector3 {
  const center = new Vector3()
  container.getCenter(center)
  
  return new Vector3(
    center.x, // Center X
    center.y, // Center Y
    object.position.z // Maintain Z (or center.z for 3D center)
  )
}

// Magnetic Snap (Physics-Based)
function applyMagneticSnap(
  position: Vector3,
  targets: SnapTarget[],
  magneticStrength: number
): Vector3 {
  let resultPosition = position.clone()
  
  targets.forEach(target => {
    const distance = position.distanceTo(target.position)
    
    if (distance < MAGNETIC_RADIUS) {
      const force = magneticStrength * (1 / (distance * distance))
      const direction = target.position.clone().sub(position).normalize()
      
      resultPosition.add(direction.multiplyScalar(force))
    }
  })
  
  return resultPosition
}
```

---

### **2. Ghost Preview System (NEW)**

**Responsibilities:**
- Render transparent ghost object at target position
- Trigger on hover of snap option buttons
- Auto-select LOD level based on polygon count
- Show measurements and alignment guides
- Collision detection and warnings

**Architecture:**

```typescript
interface GhostPreviewSystem {
  // Main entry point - triggered on hover
  showGhostPreview(
    originalObject: Object3D,
    snapOption: SnapOption,
    targetPosition: Vector3
  ): void

  // Hide ghost when hover ends
  hideGhostPreview(): void

  // Update ghost position if hover changes
  updateGhostPosition(newPosition: Vector3): void

  // Check for collisions
  detectCollisions(
    ghostObject: Object3D,
    scene: Scene
  ): Collision[]
}

class GhostPreviewRenderer {
  private ghostObject: Object3D | null = null
  private lodLevel: LODLevel
  private measurements: MeasurementLine[]
  private collisionWarnings: CollisionWarning[]
  
  constructor(
    private scene: Scene,
    private camera: Camera,
    private renderer: WebGLRenderer
  ) {}
  
  showPreview(
    original: Object3D,
    targetPosition: Vector3,
    snapOption: SnapOption
  ): void {
    // 1. Determine LOD level
    this.lodLevel = LODManager.selectLOD(original)
    
    // 2. Create ghost object based on LOD
    this.ghostObject = this.createGhostObject(original, this.lodLevel)
    
    // 3. Position ghost at target
    this.ghostObject.position.copy(targetPosition)
    
    // 4. Add ghost to scene
    this.scene.add(this.ghostObject)
    
    // 5. Create measurements
    this.measurements = this.createMeasurements(
      original.position,
      targetPosition
    )
    
    // 6. Detect collisions
    this.collisionWarnings = this.detectCollisions(this.ghostObject)
    
    // 7. Apply color based on collision status
    this.applyGhostColor(this.collisionWarnings.length === 0)
  }
  
  createGhostObject(
    original: Object3D,
    lodLevel: LODLevel
  ): Object3D {
    let ghost: Object3D
    
    switch (lodLevel) {
      case 'full_detail':
        // Clone entire object with materials
        ghost = original.clone()
        this.applyGhostMaterial(ghost, 0.5)
        break
        
      case 'simplified_mesh':
        // Use simplified geometry (50% reduction)
        ghost = original.clone()
        const simplified = LODManager.simplifyMesh(
          ghost as Mesh,
          0.5 // 50% polygon reduction
        )
        ghost = simplified
        this.applyGhostMaterial(ghost, 0.5)
        break
        
      case 'wireframe':
        // Bounding box + wireframe
        const box = new Box3().setFromObject(original)
        const boxHelper = new Box3Helper(box, 0x00ffff)
        ghost = boxHelper
        break
        
      case 'bounding_box':
        // Bounding box only
        const bbox = new Box3().setFromObject(original)
        const boxGeo = new BoxGeometry(
          bbox.max.x - bbox.min.x,
          bbox.max.y - bbox.min.y,
          bbox.max.z - bbox.min.z
        )
        const boxMat = new MeshBasicMaterial({
          color: 0x00ffff,
          wireframe: true,
          transparent: true,
          opacity: 0.5
        })
        ghost = new Mesh(boxGeo, boxMat)
        break
    }
    
    return ghost
  }
  
  applyGhostMaterial(object: Object3D, opacity: number): void {
    object.traverse(child => {
      if (child instanceof Mesh) {
        const material = child.material.clone()
        material.transparent = true
        material.opacity = opacity
        material.wireframe = false
        material.depthWrite = false // Prevent z-fighting
        child.material = material
      }
    })
  }
  
  createMeasurements(
    from: Vector3,
    to: Vector3
  ): MeasurementLine[] {
    const measurements: MeasurementLine[] = []
    
    // Distance measurement
    const distance = from.distanceTo(to)
    measurements.push({
      from,
      to,
      label: `${distance.toFixed(2)} units`,
      color: 0xffff00
    })
    
    // X/Y/Z component measurements
    measurements.push({
      from: new Vector3(from.x, from.y, from.z),
      to: new Vector3(to.x, from.y, from.z),
      label: `ΔX: ${(to.x - from.x).toFixed(2)}`,
      color: 0xff0000
    })
    
    measurements.push({
      from: new Vector3(to.x, from.y, from.z),
      to: new Vector3(to.x, to.y, from.z),
      label: `ΔY: ${(to.y - from.y).toFixed(2)}`,
      color: 0x00ff00
    })
    
    measurements.push({
      from: new Vector3(to.x, to.y, from.z),
      to: new Vector3(to.x, to.y, to.z),
      label: `ΔZ: ${(to.z - from.z).toFixed(2)}`,
      color: 0x0000ff
    })
    
    return measurements
  }
  
  detectCollisions(ghost: Object3D): CollisionWarning[] {
    const warnings: CollisionWarning[] = []
    const ghostBox = new Box3().setFromObject(ghost)
    
    // Check all objects in scene
    this.scene.traverse(object => {
      if (object === ghost || !object.visible) return
      if (!(object instanceof Mesh)) return
      
      const objectBox = new Box3().setFromObject(object)
      
      if (ghostBox.intersectsBox(objectBox)) {
        warnings.push({
          object,
          severity: this.calculateCollisionSeverity(ghostBox, objectBox)
        })
      }
    })
    
    return warnings
  }
  
  applyGhostColor(isValid: boolean): void {
    const color = isValid ? 0x00ffff : 0xff0000 // Cyan or Red
    
    this.ghostObject.traverse(child => {
      if (child instanceof Mesh && child.material) {
        child.material.color.setHex(color)
      }
    })
  }
}
```

---

### **3. LOD Manager (NEW - Critical for Performance)**

**Purpose:** Automatically select level of detail based on polygon count to maintain 60 FPS.

**LOD Levels:**

| Level | Polygon Range | Ghost Rendering | Performance |
|-------|---------------|-----------------|-------------|
| **Full Detail** | <1,000 | Full geometry + materials | <5ms |
| **Simplified Mesh** | 1,000-10,000 | 50% polygon reduction | <10ms |
| **Wireframe** | 10,000-100,000 | Bounding box + wireframe | <15ms |
| **Bounding Box** | >100,000 | Bounding box only | <20ms |

**Implementation:**

```typescript
enum LODLevel {
  FULL_DETAIL = 'full_detail',
  SIMPLIFIED_MESH = 'simplified_mesh',
  WIREFRAME = 'wireframe',
  BOUNDING_BOX = 'bounding_box'
}

class LODManager {
  private static lodCache: Map<string, Object3D> = new Map()
  
  // Auto-detect appropriate LOD level
  static selectLOD(object: Object3D): LODLevel {
    const polyCount = this.countPolygons(object)
    
    if (polyCount < 1000) {
      return LODLevel.FULL_DETAIL
    } else if (polyCount < 10000) {
      return LODLevel.SIMPLIFIED_MESH
    } else if (polyCount < 100000) {
      return LODLevel.WIREFRAME
    } else {
      return LODLevel.BOUNDING_BOX
    }
  }
  
  // Count total polygons in object (including children)
  static countPolygons(object: Object3D): number {
    let count = 0
    
    object.traverse(child => {
      if (child instanceof Mesh && child.geometry) {
        const positions = child.geometry.attributes.position
        if (positions) {
          count += positions.count / 3 // 3 vertices per triangle
        }
      }
    })
    
    return count
  }
  
  // Simplify mesh using edge collapse algorithm
  static simplifyMesh(mesh: Mesh, targetRatio: number): Mesh {
    // Check cache first
    const cacheKey = `${mesh.uuid}_${targetRatio}`
    if (this.lodCache.has(cacheKey)) {
      return this.lodCache.get(cacheKey).clone()
    }
    
    // Use Three.js SimplifyModifier (or custom implementation)
    const modifier = new SimplifyModifier()
    const simplified = modifier.modify(
      mesh.geometry,
      Math.floor(mesh.geometry.attributes.position.count * targetRatio)
    )
    
    const simplifiedMesh = new Mesh(
      simplified,
      mesh.material.clone()
    )
    
    // Cache for reuse
    this.lodCache.set(cacheKey, simplifiedMesh)
    
    return simplifiedMesh.clone()
  }
  
  // Generate bounding box representation
  static createBoundingBox(object: Object3D): Mesh {
    const box = new Box3().setFromObject(object)
    
    const size = new Vector3()
    box.getSize(size)
    
    const geometry = new BoxGeometry(size.x, size.y, size.z)
    const material = new MeshBasicMaterial({
      color: 0x00ffff,
      wireframe: true,
      transparent: true,
      opacity: 0.5
    })
    
    const bbox = new Mesh(geometry, material)
    
    const center = new Vector3()
    box.getCenter(center)
    bbox.position.copy(center)
    
    return bbox
  }
}
```

---

### **4. Snap Option Panel UI (Enhancement)**

**Current Implementation:**  
SnapConfigPanel.tsx has basic snap type toggles.

**NEW: Hover-Triggered Ghost Preview**

```typescript
interface SnapOptionPanelProps {
  selectedObject: Object3D
  onSnapOptionHover: (option: SnapOption, targetPos: Vector3) => void
  onSnapOptionLeave: () => void
  onSnapOptionClick: (option: SnapOption) => void
}

const SnapOptionPanel: React.FC<SnapOptionPanelProps> = ({
  selectedObject,
  onSnapOptionHover,
  onSnapOptionLeave,
  onSnapOptionClick
}) => {
  const snapOptions: SnapOption[] = [
    { id: 'snap_top', label: 'Snap Top', icon: ArrowUp },
    { id: 'snap_right', label: 'Snap Right', icon: ArrowRight },
    { id: 'snap_bottom', label: 'Snap Bottom', icon: ArrowDown },
    { id: 'snap_left', label: 'Snap Left', icon: ArrowLeft },
    { id: 'snap_center_x', label: 'Center X', icon: AlignCenter },
    { id: 'snap_center_y', label: 'Center Y', icon: AlignCenter },
    { id: 'snap_center_xy', label: 'Center XY', icon: Crosshair }
  ]
  
  return (
    <div className="snap-option-panel">
      <h3>Snap Options</h3>
      <div className="snap-grid">
        {snapOptions.map(option => (
          <button
            key={option.id}
            className="snap-option-btn"
            onMouseEnter={() => {
              // Calculate target position
              const targetPos = calculateSnapPosition(
                selectedObject,
                option.id
              )
              // Trigger ghost preview
              onSnapOptionHover(option, targetPos)
            }}
            onMouseLeave={() => {
              // Hide ghost preview
              onSnapOptionLeave()
            }}
            onClick={() => {
              // Apply snap
              onSnapOptionClick(option)
            }}
          >
            <option.icon />
            <span>{option.label}</span>
          </button>
        ))}
      </div>
    </div>
  )
}
```

---

## **Performance Optimization Strategies**

### **1. LOD Selection (Automatic)**
- Auto-detect polygon count
- Select appropriate LOD level
- Cache simplified meshes
- Reuse cached versions on subsequent hovers

### **2. Lazy Ghost Creation**
- Don't create ghost until hover
- Destroy ghost after hover ends (200ms delay)
- Pool ghost objects for reuse

### **3. Simplified Materials**
- Use MeshBasicMaterial for ghosts (no lighting calculations)
- Disable shadows for ghosts
- Set depthWrite = false (prevent z-fighting)

### **4. Render Optimization**
- Render ghosts in separate render pass
- Use lower resolution for ghost shadows
- Disable anti-aliasing for ghosts (if needed)

### **5. Collision Detection Optimization**
- Use bounding boxes for initial collision check
- Only detailed collision for nearby objects
- Throttle collision detection (every 100ms, not per frame)

---

## **Visual Feedback System**

### **Color Coding**

| Condition | Color | Meaning |
|-----------|-------|---------|
| Valid position | Cyan (#00ffff) | Safe to snap |
| Tight fit | Yellow (#ffff00) | Close to other objects |
| Collision | Red (#ff0000) | Overlapping with objects |
| Magnetic attraction | Purple (#ff00ff) | Being pulled by magnetic field |

### **Measurements Display**

```typescript
interface MeasurementDisplay {
  // Distance from current position
  totalDistance: {
    value: number
    label: string
    color: number
  }
  
  // Component distances (X, Y, Z)
  components: {
    axis: 'X' | 'Y' | 'Z'
    value: number
    color: number
  }[]
  
  // Snap alignment lines
  snapLines: {
    from: Vector3
    to: Vector3
    type: 'horizontal' | 'vertical' | 'depth'
    color: number
  }[]
}
```

### **Collision Warnings**

```typescript
interface CollisionWarning {
  object: Object3D
  severity: 'minor' | 'moderate' | 'severe'
  penetrationDepth: number
  resolution: 'adjust_position' | 'resize_object' | 'remove_obstacle'
}
```

---

## **Integration Points**

### **With Existing Snap Engine**
- Ghost preview uses same snap position calculations
- Leverages existing snap target detection
- Reuses magnetic attraction logic

### **With Scene Renderer**
- Ghost added as temporary scene object
- Uses same camera/lighting
- Rendered in post-processing pass

### **With UI Panel**
- Hover listeners on snap buttons
- Real-time position updates
- Click confirmation applies snap

---

## **Data Flow Diagrams**

### **Ghost Preview Trigger Flow**

```
User hovers "Snap Top" button
  ↓
UI Panel → onSnapOptionHover(option, targetPos)
  ↓
Snap Engine → calculateSnapPosition(object, 'top')
  ↓
LOD Manager → selectLOD(object)
  ↓
Ghost Preview Renderer → createGhostObject(object, lodLevel)
  ↓
Ghost Preview Renderer → position ghost at targetPos
  ↓
Collision Detector → detectCollisions(ghostObject)
  ↓
Measurement System → createMeasurements(currentPos, targetPos)
  ↓
Scene Renderer → render ghost + measurements + warnings
  ↓
Visual Feedback → color code based on collisions

Total Latency: 15-30ms (60 FPS maintained) ✅
```

### **Ghost Preview Update Flow (Hover Changes)**

```
User moves mouse to different snap button
  ↓
Previous ghost → fadeOut(200ms)
  ↓
New ghost → createGhostObject()
  ↓
Position updated → targetPos changed
  ↓
Measurements updated
  ↓
Render new ghost
```

---

## **Scalability Considerations**

### **Scene Complexity**
- **Small scenes (<100 objects):** Full collision detection
- **Medium scenes (100-1000 objects):** Spatial partitioning (octree)
- **Large scenes (>1000 objects):** Only check nearby objects (radius-based)

### **Object Complexity**
- **Simple objects:** Always full detail ghost
- **Complex objects:** LOD based on polygon count
- **Imported models:** Cache simplified versions permanently

---

**Next:** Read L3 for complete implementation guide with code examples and performance profiling.

