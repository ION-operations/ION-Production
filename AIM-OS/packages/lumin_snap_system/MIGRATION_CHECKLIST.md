# ✅ Migration Checklist - Old Snap → New Snap System

> Print this and check off as you go!

---

## 📋 Pre-Migration

- [ ] **Backup current code**
  ```bash
  git add . && git commit -m "Pre-snap-system-migration backup"
  ```

- [ ] **Read Integration Guide**
  - [ ] INTEGRATION_GUIDE.md (full guide)
  - [ ] QUICK_REFERENCE.md (cheat sheet)
  
- [ ] **Review existing code**
  - [ ] Locate `renderSnapPreview()` in Scene3D.tsx
  - [ ] Locate `renderPartHighlight()` in Scene3D.tsx
  - [ ] Note how snap state is managed
  - [ ] Note where snap UI is (if any)

---

## 🔧 Installation

- [ ] **Install snap system package**
  ```bash
  cd packages/lumin_snap_system
  npm install
  ```

- [ ] **Build package**
  ```bash
  npm run build
  ```

- [ ] **Link to 3D builder**
  ```bash
  cd ../lucidimage_3d_builder
  npm link ../lumin_snap_system
  ```

- [ ] **Verify installation**
  ```typescript
  import { GhostPreviewRenderer } from '@lumin/snap-system';
  console.log('Snap system loaded!');
  ```

---

## 📝 Code Changes - Scene3D.tsx

### Imports

- [ ] **Add snap system imports**
  ```typescript
  import { 
    GhostPreviewRenderer, 
    SnapEngine,
    SnapOption,
    SnapConfig,
    DEFAULT_SNAP_CONFIG
  } from '@lumin/snap-system';
  import * as THREE from 'three';
  ```

### State

- [ ] **Add new state variables**
  ```typescript
  const [ghostPosition, setGhostPosition] = useState<THREE.Vector3 | null>(null);
  const [currentSnapOption, setCurrentSnapOption] = useState<SnapOption | null>(null);
  ```

- [ ] **Remove old state** (if no longer needed)
  ```typescript
  // OLD - can remove after migration
  // const [snapPreview, setSnapPreview] = useState(null);
  ```

### Setup

- [ ] **Add SnapEngine initialization**
  ```typescript
  useEffect(() => {
    const engine = SnapEngine.getInstance();
    
    // Set container bounds (adjust to your scene)
    engine.setContainer(new THREE.Box3(
      new THREE.Vector3(-50, 0, -50),
      new THREE.Vector3(50, 100, 50)
    ));
    
    // Set scene reference
    engine.setScene(scene);
    
    // Optional: configure settings
    engine.updateConfig({
      gridSize: 10,
      magneticStrength: 75,
      enabledTypes: ['grid', 'element', 'magnetic']
    });
  }, [scene]);
  ```

### Replace Functions

- [ ] **Comment out old `renderSnapPreview()`**
  ```typescript
  // OLD - Replaced by GhostPreviewRenderer
  /*
  const renderSnapPreview = () => {
    if (!snapPreview) return null;
    // ... old code
  };
  */
  ```

- [ ] **Comment out old `renderPartHighlight()`**
  ```typescript
  // OLD - Replaced by GhostPreviewRenderer
  /*
  const renderPartHighlight = (obj, part) => {
    // ... old code
  };
  */
  ```

- [ ] **Add new ghost preview renderer**
  ```typescript
  const renderGhostPreview = () => {
    const { scene } = useThree();
    
    return (
      <GhostPreviewRenderer
        originalObject={selectedObject}
        targetPosition={ghostPosition}
        snapOption={currentSnapOption}
        scene={scene}
        opacity={0.5}
        enableCollisionDetection={true}
        enableMeasurements={true}
        onRenderComplete={(event) => {
          console.log(`Ghost render: ${event.renderTimeMs.toFixed(2)}ms`);
        }}
      />
    );
  };
  ```

### Update Render

- [ ] **Replace old snap preview in render**
  ```typescript
  return (
    <group>
      {/* Your objects */}
      {objects.map(renderObject)}
      
      {/* OLD - Comment out or remove */}
      {/* {renderSnapPreview()} */}
      {/* {renderPartHighlight()} */}
      
      {/* NEW - Add this */}
      {renderGhostPreview()}
      
      {/* Your controls */}
    </group>
  );
  ```

---

## 🎨 UI Changes

### Create SnapPanel Component

- [ ] **Create `src/ui/SnapPanel.tsx`** (or equivalent)
  ```typescript
  import React from 'react';
  import { SnapOptionPanel } from '@lumin/snap-system';
  // ... see INTEGRATION_GUIDE.md for full example
  ```

- [ ] **Wire up event handlers**
  - [ ] `onSnapOptionHover` - trigger ghost preview
  - [ ] `onSnapOptionLeave` - hide ghost preview
  - [ ] `onSnapOptionClick` - apply snap to object

- [ ] **Add to main layout**
  ```typescript
  import { SnapPanel } from './ui/SnapPanel';
  
  // In render:
  <div className="right-sidebar">
    <SnapPanel />
  </div>
  ```

---

## 🔄 AppContext Updates (Optional)

- [ ] **Add ghost preview state to AppContext** (if using global state)
  ```typescript
  interface AppState {
    // ... existing
    ghostPreview: {
      isActive: boolean;
      position: THREE.Vector3 | null;
      snapOption: SnapOption | null;
    } | null;
  }
  ```

- [ ] **Add reducer actions**
  ```typescript
  type AppAction = 
    | { type: 'SET_GHOST_PREVIEW'; payload: { position, option } }
    | { type: 'CLEAR_GHOST_PREVIEW' }
    | // ... existing
  ```

- [ ] **Add reducer cases**
  ```typescript
  case 'SET_GHOST_PREVIEW':
    return { ...state, ghostPreview: { ... } };
  case 'CLEAR_GHOST_PREVIEW':
    return { ...state, ghostPreview: null };
  ```

- [ ] **Update SceneObject interface** (store mesh refs)
  ```typescript
  interface SceneObject {
    // ... existing
    meshRef?: THREE.Mesh | THREE.Object3D;
  }
  ```

---

## 🧪 Testing

### Basic Tests

- [ ] **Test with simple box**
  - [ ] Create box
  - [ ] Select box
  - [ ] Hover snap options
  - [ ] See ghost preview
  - [ ] Click to snap

- [ ] **Test all 7 snap options**
  - [ ] Top (T)
  - [ ] Right (R)
  - [ ] Bottom (B)
  - [ ] Left (L)
  - [ ] Center X (X)
  - [ ] Center Y (Y)
  - [ ] Center XY (C)

- [ ] **Test keyboard shortcuts**
  - [ ] Press T, R, B, L, C, X, Y
  - [ ] Verify snap applies

### Advanced Tests

- [ ] **Test with complex model**
  - [ ] Import GLTF model
  - [ ] Verify ghost renders (check LOD)
  - [ ] Check performance (FPS)

- [ ] **Test collision detection**
  - [ ] Create two overlapping objects
  - [ ] Snap one object toward the other
  - [ ] Verify ghost turns yellow/red
  - [ ] See collision indicators

- [ ] **Test measurements**
  - [ ] Snap object to different position
  - [ ] Verify distance lines appear
  - [ ] Check ΔX, ΔY, ΔZ labels

- [ ] **Test performance**
  - [ ] Open DevTools
  - [ ] Monitor FPS
  - [ ] Check render times in console
  - [ ] Verify <20ms for all objects

---

## 🎨 Polish

- [ ] **Adjust styling to match app**
  - [ ] SnapPanel colors
  - [ ] Ghost opacity
  - [ ] Measurement line colors

- [ ] **Configure snap settings**
  - [ ] Grid size
  - [ ] Magnetic strength
  - [ ] Enabled snap types

- [ ] **Add user preferences** (optional)
  - [ ] Save/load snap config
  - [ ] Enable/disable features

- [ ] **Update user documentation**
  - [ ] Document new snap system
  - [ ] Create tutorial/onboarding

---

## 🧹 Cleanup

- [ ] **Remove old code** (after verifying new system works)
  ```typescript
  // Delete old functions:
  // - renderSnapPreview()
  // - renderPartHighlight()
  // - Old snap state
  ```

- [ ] **Remove unused imports**
  ```typescript
  // Remove if no longer needed
  ```

- [ ] **Clean up commented code**
  ```typescript
  // Remove /* commented blocks */ after migration complete
  ```

- [ ] **Run linter**
  ```bash
  npm run lint
  ```

- [ ] **Format code**
  ```bash
  npm run format
  ```

---

## 📝 Documentation

- [ ] **Update internal docs**
  - [ ] Team wiki
  - [ ] README
  - [ ] Changelog

- [ ] **Document configuration**
  - [ ] Snap settings
  - [ ] Presets used
  - [ ] Customizations

- [ ] **Create user guide** (if applicable)
  - [ ] How to use snap system
  - [ ] Keyboard shortcuts
  - [ ] Tips & tricks

---

## ✅ Final Verification

- [ ] **All tests pass**
- [ ] **No console errors**
- [ ] **FPS maintained (60+)**
- [ ] **Keyboard shortcuts work**
- [ ] **UI looks good**
- [ ] **Code is clean**
- [ ] **Team reviewed**
- [ ] **User tested** (if applicable)

---

## 🚀 Deployment

- [ ] **Commit changes**
  ```bash
  git add .
  git commit -m "Integrate new snap system with ghost preview"
  ```

- [ ] **Create PR** (if applicable)
- [ ] **Code review**
- [ ] **Merge to main**
- [ ] **Deploy**

---

## 🎉 Post-Migration

- [ ] **Monitor performance** (first week)
- [ ] **Gather user feedback**
- [ ] **Fix any issues**
- [ ] **Celebrate success!** 💙

---

**Estimated Time:** 2-4 hours (depending on complexity)

**Support:** Check INTEGRATION_GUIDE.md, README.md, or examples/BasicDemo.tsx

---

Built with love by Aether 💙

