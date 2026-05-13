# Perfect Project Structure Specification

**Date:** 2026-01-10  
**Status:** FINAL DESIGN - READY FOR APPROVAL  
**Approach:** Build perfect project folders, copy data from existing apps

---

## 🎯 **STRATEGIC APPROACH**

**Core Principle:**
- Leave existing `Documentation/appexamples/` as-is (preserve history)
- Build new `projects/` folder with perfect project structures
- Copy relevant data from existing apps to organized perfect projects
- Gradual migration, less risky, preserves originals

**Benefits:**
- ✅ Preserves original apps (no breaking changes)
- ✅ Creates clean, organized versions
- ✅ Allows gradual migration
- ✅ Less risky than reorganizing existing
- ✅ Can compare old vs new easily

---

## 📊 **PROPOSED PROJECT STRUCTURE**

### **Root Structure:**

```
projects/
  water-simulation/
    standalonewaves-v7/
    oceansim-v1/
    reference/
  
  image-editing/
    lucid-image-editor/
    v3-canvas-editor/
    tools/
  
  canvas-rendering/
    canvas-chronicle-v3/
  
  3d-tools/
    3d-canvas-studio/
    tools/
  
  visual-effects/
    effects-library/
    volumetric-clouds/
  
  ui-editors/
    ui-editor/
  
  standalone/
    code-reflex-orchestra/
    cursor-addon/
    modelmaker-examples/
```

---

## 🏗️ **STANDARD PROJECT STRUCTURE**

### **Monorepo Root Structure:**

```
projects/                       # Root of monorepo
  package.json                  # Root workspace config (REQUIRED)
  pnpm-workspace.yaml           # Workspace configuration (REQUIRED)
  pnpm-lock.yaml                # Single lock file (auto-generated)
  .npmrc                         # pnpm configuration (REQUIRED)
  node_modules/                  # SINGLE shared node_modules (pnpm hard links)
  
  [project groups...]
  packages/                      # Shared packages (optional)
    shared-ui/                   # Shared UI components
    shared-utils/                # Shared utilities
    shared-types/                # Shared TypeScript types
```

### **Every Project Follows This Structure:**

```
project-name/
  README.md                     # Project overview (REQUIRED)
  package.json                  # Workspace package config (REQUIRED)
  tsconfig.json                 # TypeScript config (if applicable)
  vite.config.ts                # Vite config (if applicable)
  [other config files]
  
  src/                          # Source code
    [code structure]
  
  docs/                         # Documentation
    README.md                   # Documentation index
    ARCHITECTURE.md             # Architecture docs (if applicable)
    API.md                      # API docs (if applicable)
    CHANGELOG.md                # Changelog (if applicable)
    [other docs]
  
  tests/                        # Test files
    [test structure]
  
  .gitignore                    # Git ignore rules
  # NO node_modules (uses root shared node_modules)
  [other project files]
```

### **Key Difference:**
- ❌ **Before:** Each app has its own `node_modules/` (gigabytes of duplicates)
- ✅ **After:** Single root `node_modules/` shared via pnpm hard links (70-90% space savings)

---

## 📋 **PROJECT SPECIFICATIONS**

### **1. Water Simulation Projects**

#### **1.1 standalonewaves-v7** (PRIMARY - Current Working App)

**Source:** `Documentation/appexamples/standalonewaves`  
**Purpose:** Working water simulation with sphere physics  
**Engine:** gptwaves-v7 (extracted from gptwaves)  
**Status:** Active development

**Structure:**
```
projects/water-simulation/standalonewaves-v7/
  README.md                    # Overview, quick start, features
  package.json
  tsconfig.json
  vite.config.ts
  
  src/
    engines/
      gptwaves-v7/            # Main engine (copied from standalonewaves)
        components/
        hooks/
        shaders/
        utils/
        GptwavesV7Scene.tsx
    components/                # Shared components
    types/                     # TypeScript types
    App.tsx
  
  docs/
    README.md                  # Documentation index
    ARCHITECTURE.md            # System architecture
    PHYSICS.md                 # Physics documentation
    PERFORMANCE.md             # Performance optimization
    SETTINGS.md                # Settings documentation
    SAM_MAPPING.md             # System Architecture Map
    CHANGELOG.md
  
  tests/
    [test files]
```

**Migration Strategy:**
1. Copy `standalonewaves/src/` to `projects/water-simulation/standalonewaves-v7/src/`
2. Copy `standalonewaves/package.json` to new location (workspace package)
3. Copy relevant docs from `standalonewaves/docs/` to `docs/`
4. Consolidate S.A.M. mapping documents
5. **DO NOT copy node_modules** - Use root shared node_modules
6. Run `pnpm install` from root to install dependencies

---

#### **1.2 oceansim-v1** (FUTURE - Advanced Ocean Physics)

**Source:** `Documentation/appexamples/oceansim` (if exists) + master plan  
**Purpose:** Hyper-realistic ocean physics  
**Status:** Planned/Future

**Structure:**
```
projects/water-simulation/oceansim-v1/
  README.md                    # Overview, vision, roadmap
  docs/
    MASTER_PLAN.md             # Complete master plan
    ARCHITECTURE.md            # Planned architecture
    PHYSICS.md                 # Advanced physics spec
```

**Migration Strategy:**
- Start fresh based on master plan
- Reference standalonewaves-v7 for concepts
- Build perfect from ground up

---

#### **1.3 reference/** (REFERENCE - Not Migrated)

**Purpose:** Reference implementations (stay in original location)  
**Strategy:** Keep all reference apps in `Documentation/appexamples/` as-is

**List:**
- webgl-water-threejs
- webgl-water
- webgl-fluid-interactive
- webgl-fluid-source
- lovable-waves
- hierarchical-water-system
- wave-physics-encyclopedia
- wave-to-3d
- standalone-wave-sim
- dli-waves
- cosmic-observatory-isolated

---

### **2. Image Editing Projects**

#### **2.1 lucid-image-editor** (PRIMARY - Main Comprehensive Editor)

**Source:** `Documentation/appexamples/lucidimage`  
**Purpose:** Full-featured image editor (300+ docs, comprehensive)  
**Status:** Active development

**Structure:**
```
projects/image-editing/lucid-image-editor/
  README.md                    # Overview, quick start, features
  package.json
  tsconfig.json
  vite.config.ts
  
  src/
    project/                   # Main app code (from lucidimage/project/)
      components/
      pages/
      [other code]
  
  docs/
    README.md                  # Documentation index
    ARCHITECTURE.md            # System architecture
    VOICE_CONTROLS.md          # 229+ voice commands
    API.md                     # API documentation
    TOOLS.md                   # Tool documentation
    CHANGELOG.md
  
  tests/
    [test files]
```

**Migration Strategy:**
1. Copy `lucidimage/project/` to `projects/image-editing/lucid-image-editor/src/project/`
2. Consolidate 300+ docs from `lucidimage/` into organized `docs/` structure
3. Create master documentation index
4. Integrate tools from `image_editing_tools/`

---

#### **2.2 v3-canvas-editor** (ALTERNATIVE - Perfect V3 Canvas)

**Source:** `version-aura` + `v3-image-editor-fresh`  
**Purpose:** Perfect V3 canvas implementation (alternative/future)  
**Status:** Could become main editor or reference

**Structure:**
```
projects/image-editing/v3-canvas-editor/
  README.md                    # Overview, V3 compliance, features
  package.json
  tsconfig.json
  vite.config.ts
  
  src/
    lib/
      canvas/
        core/                  # From version-aura
        rendering/             # From version-aura
        v6/                    # V6 Organic Flow
        tools/                 # Tool handlers
        workers/               # Web workers
        utils/                 # Utilities
    pages/
      CanvasAura.tsx           # Main canvas component
  
  docs/
    README.md                  # Documentation index
    V3_MASTER_BLUEPRINT.md     # V3 specification
    GOLDEN_PATH_RULES.md       # 16 Golden Path Rules
    ARCHITECTURE.md            # System architecture
    API.md                     # API documentation
    CHANGELOG.md
  
  tests/
    [test files]
```

**Migration Strategy:**
1. Copy `version-aura/src/lib/canvas/` as base (perfect V3)
2. Integrate best features from `v3-image-editor-fresh`
3. Reference `v3-image-editor-codex` and `v3-canvas-quickstart` for concepts
4. Follow V3 Master Blueprint strictly

---

#### **2.3 tools/** (SHARED - Tool Libraries)

**Purpose:** Shared tool libraries across all image editing projects

**Structure:**
```
projects/image-editing/tools/
  magic-wand/
    README.md
    src/
      [best magic wand implementation]
  
  lasso/
    README.md
    src/
      [best lasso implementation]
  
  selection/
    README.md
    src/
      [best selection system]
  
  library/
    README.md
    docs/
      [tool documentation from image_editing_tools]
```

**Migration Strategy:**
1. Review all implementations in `magic_wand_systems/`
2. Choose best implementation, copy to `tools/magic-wand/`
3. Repeat for `lasso_systems/` and `SELECTION_SYSTEMS/`
4. Copy tool documentation from `image_editing_tools/`

---

### **3. Canvas/Rendering Projects**

#### **3.1 canvas-chronicle-v3** (PRIMARY - Unified Canvas Chronicle)

**Source:** `canvas-chronicle` + `canvas-chronicle-v2`  
**Purpose:** Unified canvas rendering system  
**Sub-projects:** pixelforge-pro, pixelforge-v2 (inside canvas-chronicle)

**Structure:**
```
projects/canvas-rendering/canvas-chronicle-v3/
  README.md                    # Overview, features
  package.json
  tsconfig.json
  vite.config.ts
  
  src/
    [main canvas chronicle code]
  
  pixelforge-pro/              # Sub-project (from canvas-chronicle/pixelforge-pro/)
    README.md
    src/
    docs/
  
  pixelforge-v2/               # Sub-project (from canvas-chronicle/pixelforge-v2/)
    README.md
    src/
    docs/
  
  docs/
    README.md                  # Documentation index
    ARCHITECTURE.md            # System architecture
    V3_API_CONTRACTS.md        # From canvas-chronicle/docs/
    V3_COMPONENT_ARCHITECTURE.md
    V3_DATA_FLOW_DIAGRAMS.md
    CHANGELOG.md
  
  tests/
    [test files]
```

**Migration Strategy:**
1. Copy `canvas-chronicle/src/` to `projects/canvas-rendering/canvas-chronicle-v3/src/`
2. Keep `pixelforge-pro/` and `pixelforge-v2/` as sub-projects (already inside)
3. Copy docs from `canvas-chronicle/docs/`
4. Integrate best features from `canvas-chronicle-v2` if different

---

### **4. 3D Tools Projects**

#### **4.1 3d-canvas-studio** (PRIMARY - Main 3D Canvas)

**Source:** `3d-canvas-studio`  
**Purpose:** Main 3D canvas studio  
**Tools:** From `3d_editor_tools`

**Structure:**
```
projects/3d-tools/3d-canvas-studio/
  README.md                    # Overview, features
  package.json
  tsconfig.json
  vite.config.ts
  
  src/
    [main 3D canvas code]
  
  docs/
    README.md                  # Documentation index
    ARCHITECTURE.md            # System architecture
    TOOLS.md                   # Tool documentation (from 3d_editor_tools)
    API.md                     # API documentation
    CHANGELOG.md
  
  tests/
    [test files]
```

**Migration Strategy:**
1. Copy `3d-canvas-studio/src/` to `projects/3d-tools/3d-canvas-studio/src/`
2. Integrate tool documentation from `3d_editor_tools/`
3. Copy relevant tools from `wizardwand/`, `2d3dclone/`, `2d3dtopo/` to `tools/`

---

#### **4.2 tools/** (SHARED - 3D Tool Libraries)

**Structure:**
```
projects/3d-tools/tools/
  clone-stamp/                 # From 2d3dclone
    README.md
    src/
  
  topology/                    # From 2d3dtopo
    README.md
    src/
  
  wizard-wand/                 # From wizardwand
    README.md
    src/
```

---

### **5. Visual Effects Projects**

#### **5.1 effects-library** (PRIMARY - Unified Effects)

**Source:** `effects` + `newladdedeffects`  
**Purpose:** Unified effects library

**Structure:**
```
projects/visual-effects/effects-library/
  README.md                    # Overview, available effects
  package.json
  tsconfig.json
  vite.config.ts
  
  src/
    effects/
      nebula/
      lava/
      [other effects from newladdedeffects]
  
  docs/
    README.md                  # Documentation index
    EFFECTS.md                 # All effects documentation
    API.md                     # API documentation
    CHANGELOG.md
  
  tests/
    [test files]
```

**Migration Strategy:**
1. Copy `effects/` to base
2. Extract all effects from `newladdedeffects/` zip files
3. Organize by effect type

---

#### **5.2 volumetric-clouds** (SEPARATE - Volumetric Clouds)

**Source:** `volumetric-clouds`  
**Purpose:** Volumetric cloud rendering (can be shared with water simulation)

**Structure:**
```
projects/visual-effects/volumetric-clouds/
  README.md                    # Overview, features
  package.json
  tsconfig.json
  vite.config.ts
  
  src/
    [volumetric cloud code]
  
  docs/
    README.md                  # Documentation index
    ARCHITECTURE.md            # System architecture
    API.md                     # API documentation
    CHANGELOG.md
  
  tests/
    [test files]
```

---

### **6. UI Editors Projects**

#### **6.1 ui-editor** (PRIMARY - Unified UI Editor)

**Source:** `UIedit` + `DynamicModularUI_Isolated`  
**Purpose:** Unified UI component editor

**Structure:**
```
projects/ui-editors/ui-editor/
  README.md                    # Overview, features
  package.json
  tsconfig.json
  vite.config.ts
  
  src/
    [main UI editor code]
  
  neumorphism-editor/          # Sub-project (from DynamicModularUI_Isolated/NeumorphismEditor)
    README.md
    src/
  
  docs/
    README.md                  # Documentation index
    ARCHITECTURE.md            # System architecture
    API.md                     # API documentation
    CHANGELOG.md
  
  tests/
    [test files]
```

---

### **7. Standalone Projects**

#### **7.1 code-reflex-orchestra**

**Source:** `code-reflex-orchestra`  
**Purpose:** Code reflex orchestra (standalone project)

**Structure:**
```
projects/standalone/code-reflex-orchestra/
  README.md
  [project structure]
```

---

#### **7.2 cursor-addon**

**Source:** `cursor-addon`  
**Purpose:** Cursor extension (standalone project)

**Structure:**
```
projects/standalone/cursor-addon/
  README.md
  [project structure]
```

---

#### **7.3 modelmaker-examples**

**Source:** `modelmaker-examples`  
**Purpose:** Model maker examples (standalone project)

**Structure:**
```
projects/standalone/modelmaker-examples/
  README.md
  [project structure]
```

---

## 🎯 **MIGRATION STRATEGY**

### **Phase 0: Setup Monorepo Infrastructure** ⭐ **NEW - CRITICAL**
1. Create `projects/` folder at workspace root
2. Create root `package.json` with workspace configuration
3. Create `pnpm-workspace.yaml` with workspace definitions
4. Create `.npmrc` with pnpm configuration
5. Install pnpm (if not installed): `npm install -g pnpm`
6. Test workspace setup: `pnpm install`

**See:** `Documentation/DEPENDENCY_MANAGEMENT_ANALYSIS.md` for complete monorepo setup

### **Phase 1: Create Perfect Project Structure**
1. Create folder structure for each project group
2. Create standard structure templates
3. **NO node_modules in projects** - Use root shared node_modules

### **Phase 2: Migrate Primary Projects First**
1. **standalonewaves-v7** (highest priority - current working app)
2. **lucid-image-editor** (main comprehensive editor)
3. **canvas-chronicle-v3** (unified canvas)

### **Phase 3: Migrate Secondary Projects**
1. **v3-canvas-editor** (alternative/future)
2. **3d-canvas-studio** (3D tools)
3. **effects-library** (visual effects)

### **Phase 4: Migrate Tools and Libraries**
1. Image editing tools
2. 3D tools
3. Shared utilities

### **Phase 5: Migrate Standalone Projects**
1. code-reflex-orchestra
2. cursor-addon
3. modelmaker-examples

---

## 📋 **STANDARDS AND GUIDELINES**

### **README.md Requirements:**

Every project MUST have a README.md with:
- **Project Overview** - What is this project?
- **Quick Start** - How to get started?
- **Features** - What can it do?
- **Installation** - How to install?
- **Usage** - How to use?
- **Documentation** - Where to find docs?
- **Status** - Current development status

### **Documentation Standards:**

- `docs/README.md` - Documentation index (REQUIRED)
- `docs/ARCHITECTURE.md` - System architecture (if applicable)
- `docs/API.md` - API documentation (if applicable)
- `docs/CHANGELOG.md` - Changelog (if applicable)
- All docs in Markdown format
- Follow AIM-OS documentation standards

### **Code Standards:**

- TypeScript for all new code
- Follow existing code style
- Comprehensive type definitions
- Proper error handling
- Documentation comments

---

## ✅ **APPROVAL CHECKLIST**

Before starting migration:

- [ ] User approves project structure design
- [ ] User approves migration strategy
- [ ] User approves primary projects list
- [ ] User approves standards and guidelines
- [ ] Create `projects/` folder structure
- [ ] Begin Phase 1 migration

---

**Status:** FINAL DESIGN - READY FOR USER APPROVAL  
**Next Step:** User approval, then begin Phase 1 migration
