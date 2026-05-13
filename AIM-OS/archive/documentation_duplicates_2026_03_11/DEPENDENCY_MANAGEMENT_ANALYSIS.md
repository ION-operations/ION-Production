# Dependency Management Analysis

**Date:** 2026-01-10  
**Status:** ANALYZING DEPENDENCY DUPLICATION  
**Purpose:** Design smart dependency management for perfect project structure

---

## 🎯 **PROBLEM STATEMENT**

### **Current Issues:**
- 🚨 **Gigabytes of duplicate dependencies** across apps
- 🚨 **Same packages installed 50+ times** (one per app)
- 🚨 **Waste of disk space** (node_modules in each app)
- 🚨 **Slow installs** (installing same packages repeatedly)
- 🚨 **Version conflicts** (different versions of same package)
- 🚨 **Hard to manage** (update packages in 50+ places)

### **User's Concern:**
"We have a TON of duplicate dependencies across apps. like gigabytes. how can we manage this smarter?"

---

## 🔍 **CURRENT SITUATION ANALYSIS**

### **Dependency Structure:**
```
Documentation/appexamples/
  standalonewaves/
    node_modules/          # Full dependency tree
    package.json
  lucidimage/
    project/
      node_modules/        # Full dependency tree
      package.json
  v3-image-editor-fresh/
    node_modules/          # Full dependency tree
    package.json
  canvas-chronicle/
    node_modules/          # Full dependency tree
    package.json
  [50+ more apps with node_modules]
```

### **Problems:**
1. **Each app has its own `node_modules/`** - Duplicate dependencies
2. **No shared dependencies** - Same packages installed 50+ times
3. **Gigabytes wasted** - Each `node_modules/` can be 100MB-1GB+
4. **Version conflicts** - Different apps use different versions
5. **Hard to update** - Update packages in 50+ places
6. **No dependency deduplication** - npm/yarn don't deduplicate across projects

---

## ✅ **SOLUTION: MONOREPO WITH WORKSPACES**

### **Best Approach: pnpm Workspaces**

**Why pnpm?**
- ✅ **Hard links** - Shares packages across workspaces (saves space)
- ✅ **Deduplication** - Automatic dependency deduplication
- ✅ **Fast installs** - Only downloads unique packages once
- ✅ **Strict** - Prevents phantom dependencies
- ✅ **Disk efficient** - 70-90% disk space savings vs npm/yarn

**Why Workspaces?**
- ✅ **Single root `node_modules/`** - Shared dependencies
- ✅ **Workspace packages** - Can reference local packages
- ✅ **Hoisting** - Dependencies hoisted to root when possible
- ✅ **Centralized management** - Update packages in one place

---

## 🏗️ **PROPOSED STRUCTURE**

### **Monorepo Structure with pnpm Workspaces:**

```
projects/                      # Root of monorepo
  package.json                 # Root workspace config
  pnpm-workspace.yaml          # Workspace configuration
  pnpm-lock.yaml               # Single lock file
  node_modules/                # SINGLE shared node_modules (pnpm hard links)
  
  water-simulation/
    standalonewaves-v7/
      package.json             # Workspace package
      src/
      docs/
      tests/
      # NO node_modules (uses root)
  
  image-editing/
    lucid-image-editor/
      package.json             # Workspace package
      src/
      docs/
      tests/
      # NO node_modules (uses root)
  
  canvas-rendering/
    canvas-chronicle-v3/
      package.json             # Workspace package
      src/
      docs/
      tests/
      # NO node_modules (uses root)
  
  packages/                    # Shared packages (optional)
    shared-ui/                 # Shared UI components
      package.json
      src/
    shared-utils/              # Shared utilities
      package.json
      src/
    shared-types/              # Shared TypeScript types
      package.json
      src/
```

---

## 📋 **IMPLEMENTATION PLAN**

### **Phase 1: Setup Monorepo Structure**

#### **1.1 Create Root package.json:**

```json
{
  "name": "aim-os-projects",
  "version": "1.0.0",
  "private": true,
  "description": "AIM-OS Projects Monorepo",
  "packageManager": "pnpm@8.15.0",
  "scripts": {
    "install:all": "pnpm install",
    "build:all": "pnpm -r build",
    "dev:all": "pnpm -r --parallel dev",
    "test:all": "pnpm -r test",
    "clean": "pnpm -r exec rm -rf node_modules dist",
    "lint:all": "pnpm -r lint"
  },
  "engines": {
    "node": ">=18.0.0",
    "pnpm": ">=8.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "typescript": "^5.0.0"
  }
}
```

#### **1.2 Create pnpm-workspace.yaml:**

```yaml
packages:
  # Water simulation projects
  - 'water-simulation/*'
  
  # Image editing projects
  - 'image-editing/*'
  - 'image-editing/tools/*'
  
  # Canvas rendering projects
  - 'canvas-rendering/*'
  
  # 3D tools projects
  - '3d-tools/*'
  - '3d-tools/tools/*'
  
  # Visual effects projects
  - 'visual-effects/*'
  
  # UI editors projects
  - 'ui-editors/*'
  
  # Standalone projects
  - 'standalone/*'
  
  # Shared packages
  - 'packages/*'
```

#### **1.3 Create .npmrc (pnpm configuration):**

```
# Use hard links (saves space)
link-workspace-packages=true

# Hoist dependencies to root
shamefully-hoist=false
public-hoist-pattern[]=*eslint*
public-hoist-pattern[]=*prettier*

# Strict (prevents phantom dependencies)
strict-peer-dependencies=true

# Auto install peers
auto-install-peers=true

# Save exact versions
save-exact=true
```

---

### **Phase 2: Dependency Analysis**

#### **2.1 Analyze Common Dependencies:**

**Tools to analyze:**
- `pnpm why <package>` - Why is package installed?
- `pnpm list` - List all dependencies
- `pnpm outdated` - Check for outdated packages
- `pnpm licenses list` - List all licenses

**Common dependencies to identify:**
- React, React-DOM
- TypeScript, @types/*
- Vite, vite plugins
- Three.js, @react-three/fiber
- UI libraries (shadcn/ui, tailwindcss)
- Testing (vitest, jest)
- Linting (eslint, prettier)

#### **2.2 Create Shared Dependencies:**

**Option 1: Root devDependencies (Recommended)**
- Common dev dependencies at root (TypeScript, ESLint, Prettier)
- All workspaces inherit from root

**Option 2: Shared Package**
- Create `packages/shared-deps` package
- Common dependencies as peer dependencies
- All workspaces depend on shared-deps

---

### **Phase 3: Migration Strategy**

#### **3.1 For Each Project:**

1. **Copy package.json** to new location
2. **Remove node_modules** (don't copy)
3. **Update import paths** if needed (workspace references)
4. **Test install** - `pnpm install` from root
5. **Test build** - `pnpm build` from workspace
6. **Test dev** - `pnpm dev` from workspace

#### **3.2 Dependency Consolidation:**

1. **Identify common versions** - Group by version
2. **Standardize versions** - Use same version everywhere
3. **Update package.json** - Update to standard versions
4. **Test compatibility** - Ensure all projects work

#### **3.3 Workspace References:**

**Before (separate apps):**
```json
{
  "dependencies": {
    "some-package": "^1.0.0"
  }
}
```

**After (workspace reference):**
```json
{
  "dependencies": {
    "some-package": "workspace:*",
    "@shared/utils": "workspace:*"
  }
}
```

---

### **Phase 4: Shared Packages (Optional)**

#### **4.1 Create Shared Packages:**

**packages/shared-ui:**
```json
{
  "name": "@shared/ui",
  "version": "1.0.0",
  "main": "./src/index.ts",
  "types": "./src/index.ts",
  "exports": {
    ".": "./src/index.ts"
  }
}
```

**packages/shared-utils:**
```json
{
  "name": "@shared/utils",
  "version": "1.0.0",
  "main": "./src/index.ts",
  "types": "./src/index.ts",
  "exports": {
    ".": "./src/index.ts"
  }
}
```

#### **4.2 Use Shared Packages:**

```typescript
// In workspace package.json
{
  "dependencies": {
    "@shared/ui": "workspace:*",
    "@shared/utils": "workspace:*"
  }
}

// In code
import { Button } from '@shared/ui';
import { formatDate } from '@shared/utils';
```

---

## 📊 **EXPECTED BENEFITS**

### **Disk Space Savings:**
- **Before:** 50+ apps × 100MB-1GB each = 5-50GB
- **After:** Single node_modules with hard links = 500MB-5GB
- **Savings:** 70-90% disk space reduction

### **Install Time Savings:**
- **Before:** Install 50+ times = hours
- **After:** Install once = minutes
- **Savings:** 80-95% time reduction

### **Management Benefits:**
- ✅ **Single lock file** - `pnpm-lock.yaml`
- ✅ **Centralized updates** - Update in one place
- ✅ **Version consistency** - Same versions everywhere
- ✅ **Workspace references** - Share code between projects
- ✅ **Build optimization** - Turborepo/Nx for caching

---

## 🔧 **TOOLS AND COMMANDS**

### **pnpm Workspace Commands:**

```bash
# Install all dependencies
pnpm install

# Install in specific workspace
pnpm --filter standalonewaves-v7 install

# Run script in all workspaces
pnpm -r build

# Run script in specific workspace
pnpm --filter standalonewaves-v7 build

# Run script in parallel
pnpm -r --parallel dev

# Add dependency to workspace
pnpm --filter standalonewaves-v7 add react

# Add dev dependency to workspace
pnpm --filter standalonewaves-v7 add -D typescript

# Add dependency to root
pnpm add -w -D typescript

# List all dependencies
pnpm list --depth=0

# Check outdated packages
pnpm outdated

# Why is package installed?
pnpm why react
```

### **Optional: Turborepo (Build Caching)**

```json
// turbo.json
{
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**"]
    },
    "dev": {
      "cache": false
    },
    "test": {
      "dependsOn": ["build"],
      "outputs": []
    }
  }
}
```

---

## 🎯 **MIGRATION CHECKLIST**

### **Phase 1: Setup**
- [ ] Create `projects/` folder structure
- [ ] Create root `package.json`
- [ ] Create `pnpm-workspace.yaml`
- [ ] Create `.npmrc`
- [ ] Install pnpm (if not installed)

### **Phase 2: Analysis**
- [ ] Analyze common dependencies
- [ ] Identify version conflicts
- [ ] Create dependency consolidation plan
- [ ] Design shared packages (if needed)

### **Phase 3: Migration**
- [ ] Migrate primary projects (standalonewaves-v7, lucid-image-editor)
- [ ] Test workspace setup
- [ ] Consolidate dependencies
- [ ] Migrate remaining projects

### **Phase 4: Optimization**
- [ ] Create shared packages (optional)
- [ ] Setup Turborepo (optional)
- [ ] Optimize build scripts
- [ ] Document workspace usage

---

## ✅ **RECOMMENDATIONS**

### **1. Use pnpm Workspaces (Recommended)**
- Best disk space savings
- Fast installs
- Strict dependency management
- Easy to use

### **2. Start with Primary Projects**
- Migrate standalonewaves-v7 first
- Migrate lucid-image-editor second
- Test and validate
- Migrate remaining projects

### **3. Consolidate Dependencies**
- Identify common dependencies
- Standardize versions
- Move common devDependencies to root
- Use workspace references for shared code

### **4. Optional Enhancements**
- Create shared packages (UI, utils, types)
- Setup Turborepo for build caching
- Use pnpm patch for patching dependencies

---

## 📚 **REFERENCES**

- **pnpm Workspaces:** https://pnpm.io/workspaces
- **pnpm Configuration:** https://pnpm.io/npmrc
- **Turborepo:** https://turbo.build/repo
- **Nx:** https://nx.dev

---

**Status:** ANALYSIS COMPLETE - READY FOR IMPLEMENTATION  
**Next Step:** User approval, then begin Phase 1 setup
