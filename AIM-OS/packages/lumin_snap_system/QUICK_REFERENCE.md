# ⚡ Quick Reference - Lumin Snap System

> **TL;DR** for experienced developers who want to integrate fast

---

## 🚀 3-Minute Integration

### 1. Install (30 seconds)

```bash
cd packages/lumin_snap_system && npm install && npm run build
cd ../lucidimage_3d_builder && npm link ../lumin_snap_system
```

### 2. Import (10 seconds)

```typescript
import { GhostPreviewRenderer, SnapOptionPanel, SnapEngine } from '@lumin/snap-system';
```

### 3. Setup (1 minute)

```typescript
// Add state
const [ghostPos, setGhostPos] = useState<THREE.Vector3 | null>(null);
const [snapOpt, setSnapOpt] = useState<SnapOption | null>(null);

// Initialize
useEffect(() => {
  const engine = SnapEngine.getInstance();
  engine.setContainer(new THREE.Box3(new THREE.Vector3(-50, 0, -50), new THREE.Vector3(50, 100, 50)));
  engine.setScene(scene);
}, [scene]);
```

### 4. Render (30 seconds)

```typescript
// In Canvas:
<GhostPreviewRenderer originalObject={selected} targetPosition={ghostPos} snapOption={snapOpt} scene={scene} />

// In UI:
<SnapOptionPanel 
  selectedObject={selected}
  onSnapOptionHover={({targetPosition}) => setGhostPos(targetPosition)}
  onSnapOptionLeave={() => setGhostPos(null)}
  onSnapOptionClick={({targetPosition}) => selected.position.copy(targetPosition)}
/>
```

---

## 📋 Cheat Sheet

### Key Components

| Component | Purpose | Required Props |
|-----------|---------|----------------|
| `GhostPreviewRenderer` | 3D ghost visualization | `originalObject`, `targetPosition`, `snapOption`, `scene` |
| `SnapOptionPanel` | UI snap buttons | `selectedObject`, `onSnapOptionHover`, `onSnapOptionLeave`, `onSnapOptionClick` |
| `SnapEngine` | Position calculations | Call `setContainer()`, `setScene()` |
| `LODManager` | Performance optimization | Auto-used by GhostPreviewRenderer |

### Keyboard Shortcuts

```
T = Top        R = Right       B = Bottom      L = Left
C = Center     X = Center X    Y = Center Y
```

### LOD Levels

```
<1k polys    → Full Detail    (<5ms)
1k-10k       → Simplified     (<10ms)
10k-100k     → Wireframe      (<15ms)
>100k        → Bounding Box   (<20ms)
```

### Configuration

```typescript
SnapEngine.getInstance().updateConfig({
  gridSize: 10,           // Grid snap interval
  magneticStrength: 75,   // 0-100
  magneticRadius: 50,     // Units
  enabledTypes: ['grid', 'element', 'magnetic']
});
```

### Presets

```typescript
SnapEngine.getInstance().applyPreset('Precise');   // CAD-like
SnapEngine.getInstance().applyPreset('Balanced');  // Default
SnapEngine.getInstance().applyPreset('Magnetic');  // Quick layout
SnapEngine.getInstance().applyPreset('Fluid');     // Organic
```

---

## 🔧 Common Tasks

### Task: Calculate snap position manually

```typescript
const engine = SnapEngine.getInstance();
const targetPos = engine.calculateSnapPosition(myMesh, 'snap_top');
myMesh.position.copy(targetPos);
```

### Task: Check collision before snap

```typescript
const wouldCollide = engine.wouldCollide(myMesh, targetPosition);
if (wouldCollide) {
  console.warn('Collision detected!');
}
```

### Task: Get performance stats

```typescript
<GhostPreviewRenderer
  onRenderComplete={({renderTimeMs, lodLevel, polygonCount}) => {
    console.log(`${lodLevel}: ${renderTimeMs}ms, ${polygonCount} polys`);
  }}
/>
```

### Task: Disable features for performance

```typescript
<GhostPreviewRenderer
  enableCollisionDetection={false}
  enableMeasurements={false}
  opacity={0.3}
/>
```

### Task: Clear LOD cache

```typescript
LODManager.getInstance().clearCache();
```

---

## 🐛 Quick Troubleshooting

| Problem | Fix |
|---------|-----|
| Ghost doesn't appear | Check `selectedObject` is THREE.Mesh, not null |
| Wrong snap position | Verify `setContainer()` bounds match your scene |
| Collisions not detected | Call `engine.setScene(scene)` |
| Shortcuts don't work | Set `showShortcuts={true}` and object is selected |
| Poor performance | Check `onRenderComplete` for render time >20ms |

---

## 📁 File Structure

```
Your App:
src/
├── components/viewport/Scene3D.tsx     # Add GhostPreviewRenderer here
├── ui/SnapPanel.tsx                    # NEW: Create this
└── context/AppContext.tsx              # Add ghost state (optional)

Integration Points:
1. Scene3D.tsx   → Import components, add to render
2. SnapPanel.tsx → Create new UI component
3. AppContext    → Add state (or use local state)
```

---

## 💡 Pro Tips

1. **Start simple:** Test with a box first, then add complex models
2. **Monitor performance:** Use `onRenderComplete` callback
3. **Configure wisely:** Use presets, don't over-tweak
4. **Cache LOD objects:** Cleared automatically, but can manual clear
5. **Keyboard shortcuts:** Users love them - enable by default!

---

## 📚 Full Documentation

- **Integration Guide:** `INTEGRATION_GUIDE.md` (comprehensive)
- **API Reference:** `README.md` (complete API docs)
- **Examples:** `examples/BasicDemo.tsx` (working demo)
- **Tests:** `src/__tests__/` (usage examples)

---

**Questions?** Check the full Integration Guide!

Built with love by Aether 💙

