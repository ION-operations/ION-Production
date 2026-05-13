---
id: "meshy_3d_panel_design"
system: "lucid_ide"
component: "meshy_3d_integration"
level: "T3"
type: "ui_design"
title: "Meshy 3D Panel - Comprehensive UI/UX Design"
description: "Complete design specification for Meshy API integration in Lucid Image 3D Editor"
created: "2025-12-24T00:00:00Z"
updated: "2025-12-24T00:00:00Z"
author: "aether"
status: "design_complete"
tags: ["meshy", "3d-generation", "ui-design", "lucid-image", "threejs", "react-three-fiber"]
---

# Meshy 3D Panel - Comprehensive UI/UX Design

**Purpose:** Complete UI/UX specification for Meshy API integration in Lucid Image 3D Editor  
**Target App:** `Documentation/appexamples/lucidimage/project/`  
**Status:** 🎨 **DESIGN SPECIFICATION COMPLETE**

---

## 🎯 **DESIGN PHILOSOPHY**

### **Core Principles**

1. **Intuitive Workflows** - Progressive disclosure from simple to advanced
2. **Visual Feedback** - Real-time progress, previews, status indicators
3. **Non-Destructive** - Everything saveable, reversible, exportable
4. **Seamless Integration** - Match existing Lucid Image 3D editor patterns
5. **Power User Ready** - Full API access for advanced users

### **Target User Personas**

| Persona | Needs | UI Approach |
|---------|-------|-------------|
| **Casual Creator** | Quick results, simple prompts | Default presets, one-click generate |
| **3D Artist** | Control over topology, textures | Advanced parameter panels |
| **Game Developer** | Low-poly, rigged, animated | Post-processing pipeline |
| **Product Designer** | High-quality renders, PBR | Material & texture controls |

---

## 🏗️ **ARCHITECTURE OVERVIEW**

### **Component Hierarchy**

```
ThreeDEditorPageV2
├── DrawerProvider
│   ├── IconBar (left)
│   │   └── MeshyIcon → Opens MeshyDrawer
│   ├── DrawerContainer (right)
│   │   └── MeshyDrawer
│   │       ├── MeshyGenerationPanel
│   │       │   ├── ModeSelector (tabs)
│   │       │   ├── PromptInput / ImageUpload
│   │       │   ├── QuickSettings (collapsible)
│   │       │   └── AdvancedSettings (collapsible)
│   │       ├── MeshyProgressPanel
│   │       │   ├── TaskStatus
│   │       │   ├── ProgressBar
│   │       │   └── PreviewThumbnail
│   │       ├── MeshyResultPanel
│   │       │   ├── Model3DPreview
│   │       │   ├── ActionButtons (import, download, refine)
│   │       │   └── ModelInfo
│   │       ├── MeshyHistoryPanel
│   │       │   └── GenerationHistory (grid/list)
│   │       └── MeshyLibraryPanel
│   │           └── SavedModels (local + cloud)
│   └── MiniBar (context actions)
└── Viewport3D
    └── ImportedMeshyModels (via SceneObject)
```

### **State Management**

```typescript
// New Zustand store for Meshy integration
interface MeshyEditorState {
  // Generation state
  activeMode: 'text-to-3d' | 'image-to-3d' | 'multi-image' | 'remesh' | 'retexture' | 'rig';
  currentTask: MeshyTask | null;
  taskQueue: MeshyTask[];
  
  // History & Library
  generationHistory: MeshyTask[];
  savedModels: SavedModel[];
  
  // Settings
  quickSettings: QuickSettings;
  advancedSettings: AdvancedSettings;
  uiPreferences: UIPreferences;
  
  // API state
  apiKey: string | null;
  balance: number | null;
  rateLimitStatus: RateLimitStatus;
}
```

---

## 📐 **DRAWER LAYOUT DESIGN**

### **MeshyDrawer - Main Container**

```
┌─────────────────────────────────────────┐
│ 🎨 Meshy 3D Generation          [API ●] │ ← Header with API status
├─────────────────────────────────────────┤
│ ┌─────┬─────┬─────┬─────┬─────┬─────┐  │
│ │Text │Image│Multi│Mesh │Tex  │Rig  │  │ ← Mode tabs
│ └─────┴─────┴─────┴─────┴─────┴─────┘  │
├─────────────────────────────────────────┤
│                                         │
│  [Generation Panel - Mode Specific]     │ ← Main content area
│                                         │
├─────────────────────────────────────────┤
│  ▼ Quick Settings                       │ ← Collapsible
│    Art Style: [Realistic ▼]             │
│    Quality:   ○ Preview  ● Refine       │
├─────────────────────────────────────────┤
│  ▼ Advanced Settings                    │ ← Collapsible (collapsed by default)
│    AI Model: [Meshy 6 (Latest) ▼]       │
│    Topology: [Triangle ▼]               │
│    Polycount: [====|====] 30,000        │
│    ...                                  │
├─────────────────────────────────────────┤
│  [🚀 Generate]                          │ ← Primary action
├─────────────────────────────────────────┤
│  ▼ Current Task                         │ ← Progress section
│    ┌─────────────────────────────────┐  │
│    │ [Preview] Task: abc123          │  │
│    │ Status: IN_PROGRESS             │  │
│    │ [████████░░░░░░░░░░░] 45%       │  │
│    └─────────────────────────────────┘  │
├─────────────────────────────────────────┤
│  ▼ History (12)                         │ ← Recent generations
│    [Grid of thumbnails]                 │
├─────────────────────────────────────────┤
│  💳 Credits: 1,234                      │ ← Footer with balance
└─────────────────────────────────────────┘
```

---

## 🎨 **MODE-SPECIFIC PANELS**

### **1. Text-to-3D Panel**

```
┌─────────────────────────────────────────┐
│ ✨ Describe your 3D model               │
├─────────────────────────────────────────┤
│ ┌─────────────────────────────────────┐ │
│ │ A futuristic robot with chrome      │ │
│ │ armor and glowing blue eyes...      │ │ ← Prompt textarea
│ │                                     │ │   (max 600 chars)
│ │                            [547/600]│ │
│ └─────────────────────────────────────┘ │
├─────────────────────────────────────────┤
│ 💡 Prompt Tips:                         │
│ • Be specific about materials           │
│ • Describe pose/orientation             │
│ • Mention art style preferences         │
├─────────────────────────────────────────┤
│ 🎯 Generation Stage                     │
│ ┌─────────────────┬──────────────────┐  │
│ │   📦 PREVIEW    │   🎨 REFINE      │  │
│ │   Mesh Only     │   + Textures     │  │
│ │   ~30 sec       │   ~2 min         │  │
│ │   20 credits    │   +10 credits    │  │
│ └─────────────────┴──────────────────┘  │
├─────────────────────────────────────────┤
│ [Preview Task ID: ________________]     │ ← Only shown in Refine mode
│                                         │
│ 🎨 Texture Options (Refine Only)        │
│ ┌─────────────────────────────────────┐ │
│ │ Additional texture prompt...        │ │
│ └─────────────────────────────────────┘ │
│ □ Enable PBR Maps (metallic, rough...)  │
│ [Upload Reference Image]                │
└─────────────────────────────────────────┘
```

### **2. Image-to-3D Panel**

```
┌─────────────────────────────────────────┐
│ 🖼️ Upload Reference Image               │
├─────────────────────────────────────────┤
│ ┌─────────────────────────────────────┐ │
│ │                                     │ │
│ │        [Drop Image Here]            │ │
│ │         or click to browse          │ │ ← Drag & drop zone
│ │                                     │ │
│ │   Supports: JPG, PNG, WebP          │ │
│ │   Max size: 10MB                    │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ [Preview of uploaded image]             │
│ ┌───────────┐                           │
│ │           │ my_character.png          │
│ │  [thumb]  │ 1024x1024 • 2.3MB         │
│ │           │ [✕ Remove]                │
│ └───────────┘                           │
├─────────────────────────────────────────┤
│ 📝 Optional Description                 │
│ ┌─────────────────────────────────────┐ │
│ │ Add details about the model...      │ │
│ └─────────────────────────────────────┘ │
├─────────────────────────────────────────┤
│ 🎯 Texture Generation                   │
│ □ Generate with textures (30 credits)   │
│   vs. Mesh only (20 credits)            │
└─────────────────────────────────────────┘
```

### **3. Multi-Image-to-3D Panel**

```
┌─────────────────────────────────────────┐
│ 📷 Multiple Reference Views             │
├─────────────────────────────────────────┤
│ Upload 2-6 images from different angles │
├─────────────────────────────────────────┤
│ ┌────────┬────────┬────────┐            │
│ │ Front  │ Side   │ Back   │            │
│ │ [img]  │ [img]  │  [+]   │            │ ← Grid of uploads
│ │        │        │        │            │
│ └────────┴────────┴────────┘            │
│ ┌────────┬────────┬────────┐            │
│ │ Top    │ 3/4    │ [+]    │            │
│ │  [+]   │  [+]   │        │            │
│ └────────┴────────┴────────┘            │
├─────────────────────────────────────────┤
│ Images uploaded: 2/6                    │
│ Best results: 4-6 orthogonal views      │
├─────────────────────────────────────────┤
│ 💡 Tips:                                │
│ • Use consistent lighting               │
│ • Remove backgrounds if possible        │
│ • Include front, side, back views       │
└─────────────────────────────────────────┘
```

### **4. Remesh Panel**

```
┌─────────────────────────────────────────┐
│ 🔧 Remesh Optimization                  │
├─────────────────────────────────────────┤
│ Source Model:                           │
│ ○ From Task ID: [________________]      │
│ ● From URL/File: [Upload Model]         │
├─────────────────────────────────────────┤
│ 🎯 Target Polygon Count                 │
│ [Min]═══════●══════════════[Max]        │
│  100              30,000         300,000│
│                                         │
│ Current: 125,000 → Target: 30,000       │
│ Reduction: ~76%                         │
├─────────────────────────────────────────┤
│ 🔺 Topology                             │
│ ○ Triangle (game-ready, universal)      │
│ ○ Quad (subdivision-ready, clean)       │
├─────────────────────────────────────────┤
│ 📐 Output Formats                       │
│ ☑ GLB  ☐ FBX  ☐ OBJ  ☐ USDZ            │
├─────────────────────────────────────────┤
│ □ Convert Format Only (no remeshing)    │
│ □ Resize Height: [___] meters           │
└─────────────────────────────────────────┘
```

### **5. Retexture (AI Texturing) Panel**

```
┌─────────────────────────────────────────┐
│ 🎨 AI Retexturing                       │
├─────────────────────────────────────────┤
│ Source Model:                           │
│ [Upload Model URL/File]                 │
├─────────────────────────────────────────┤
│ ✨ Style Description                    │
│ ┌─────────────────────────────────────┐ │
│ │ Worn medieval armor with rust and   │ │
│ │ battle damage, leather straps...    │ │
│ └─────────────────────────────────────┘ │
│                        OR               │
│ 🖼️ Style Reference Image                │
│ [Upload Style Reference]                │
├─────────────────────────────────────────┤
│ 📦 PBR Output                           │
│ ☑ Enable PBR Maps                       │
│   ├── Base Color (Albedo)               │
│   ├── Metallic                          │
│   ├── Roughness                         │
│   └── Normal                            │
├─────────────────────────────────────────┤
│ 💰 Cost: 10 credits                     │
└─────────────────────────────────────────┘
```

### **6. Rigging & Animation Panel**

```
┌─────────────────────────────────────────┐
│ 🦴 Auto-Rigging & Animation             │
├─────────────────────────────────────────┤
│ ⚠️ Best for humanoid bipedal models    │
│    with clear limb structure            │
├─────────────────────────────────────────┤
│ Source Model:                           │
│ ○ From Task ID: [________________]      │
│ ● From URL/File: [Upload Model]         │
│   (Textured humanoid GLB required)      │
├─────────────────────────────────────────┤
│ 📏 Character Height                     │
│ [=====●==========] 1.7 meters           │
│                                         │
│ [Optional Texture Image URL]            │
├─────────────────────────────────────────┤
│ 🎬 Basic Animations Included:           │
│ ☑ Walking    ☑ Running                  │
├─────────────────────────────────────────┤
│ ➕ Add More Animations                  │
│ [Animation Library Browser →]           │
│                                         │
│ Available animations:                   │
│ ├── Idle (3 credits)                    │
│ ├── Jump (3 credits)                    │
│ ├── Attack (3 credits)                  │
│ └── [Browse 100+ more...]               │
├─────────────────────────────────────────┤
│ 💰 Rigging: 5 credits                   │
│    + Animation: 3 credits each          │
└─────────────────────────────────────────┘
```

---

## 🔧 **SETTINGS PANELS**

### **Quick Settings (Always Visible)**

```typescript
interface QuickSettings {
  artStyle: 'realistic' | 'sculpture';
  generationStage: 'preview' | 'refine';
  seed?: number;  // For reproducibility
}
```

```
┌─────────────────────────────────────────┐
│ ⚡ Quick Settings                       │
├─────────────────────────────────────────┤
│ Art Style:                              │
│ ┌─────────────────┬──────────────────┐  │
│ │ 🎨 Realistic    │ 🗿 Sculpture     │  │
│ │    [selected]   │                  │  │
│ └─────────────────┴──────────────────┘  │
├─────────────────────────────────────────┤
│ Seed (optional): [_____________]        │
│ 💡 Use same seed to reproduce results   │
└─────────────────────────────────────────┘
```

### **Advanced Settings (Collapsed by Default)**

```typescript
interface AdvancedSettings {
  // Model Quality
  aiModel: 'meshy-4' | 'meshy-5' | 'latest';  // Meshy 6
  
  // Mesh Settings
  topology: 'triangle' | 'quad';
  targetPolycount: number;  // 100-300,000
  shouldRemesh: boolean;
  
  // Symmetry
  symmetryMode: 'auto' | 'on' | 'off';
  
  // Pose
  poseMode: 'a-pose' | 't-pose' | 'default';
  
  // Moderation
  enableModeration: boolean;
}
```

```
┌─────────────────────────────────────────┐
│ ⚙️ Advanced Settings              [▼]   │
├─────────────────────────────────────────┤
│ 🤖 AI Model                             │
│ ┌─────────────────────────────────────┐ │
│ │ Meshy 6 (Latest)              [▼]  │ │
│ └─────────────────────────────────────┘ │
│   ✨ Most accurate, best quality        │
├─────────────────────────────────────────┤
│ 🔺 Mesh Topology                        │
│ ○ Triangle (game engines, universal)    │
│ ○ Quad (subdivision, clean topology)    │
├─────────────────────────────────────────┤
│ 📊 Target Polycount                     │
│ [Min]═══════════●═════════════[Max]     │
│  100          30,000           300,000  │
│                                         │
│ □ Auto-remesh after generation          │
├─────────────────────────────────────────┤
│ ↔️ Symmetry Mode                        │
│ ○ Auto (recommended - detects symmetry) │
│ ○ On (enforce bilateral symmetry)       │
│ ○ Off (no symmetry enforcement)         │
├─────────────────────────────────────────┤
│ 🧍 Pose (for characters)                │
│ ○ Default                               │
│ ○ A-Pose (arms at 45°)                  │
│ ○ T-Pose (arms horizontal)              │
├─────────────────────────────────────────┤
│ 🛡️ Content Moderation                  │
│ □ Enable content moderation             │
├─────────────────────────────────────────┤
│ [Reset to Defaults]                     │
└─────────────────────────────────────────┘
```

---

## 📊 **PROGRESS & RESULTS**

### **Task Progress Panel**

```
┌─────────────────────────────────────────┐
│ 🔄 Current Task                         │
├─────────────────────────────────────────┤
│ ┌─────────────────────────────────────┐ │
│ │ [Thumbnail Preview]                 │ │
│ │                                     │ │
│ │  Task: 019abc...                    │ │
│ │  Mode: Text to 3D (Preview)         │ │
│ │  Status: IN_PROGRESS                │ │
│ │                                     │ │
│ │  [████████████░░░░░░░░░░░░] 67%     │ │
│ │                                     │ │
│ │  ⏱️ Elapsed: 0:45 / ~1:30 est.      │ │
│ │  📍 Queue position: Processing...   │ │
│ └─────────────────────────────────────┘ │
├─────────────────────────────────────────┤
│ [Cancel] [View in Browser →]            │
└─────────────────────────────────────────┘
```

### **Result Panel (Post-Generation)**

```
┌─────────────────────────────────────────┐
│ ✅ Generation Complete                  │
├─────────────────────────────────────────┤
│ ┌─────────────────────────────────────┐ │
│ │                                     │ │
│ │      [3D Model Preview Canvas]      │ │
│ │      (Interactive rotate/zoom)      │ │ ← React Three Fiber preview
│ │                                     │ │
│ └─────────────────────────────────────┘ │
├─────────────────────────────────────────┤
│ 📋 Model Info                           │
│ • Polygons: 28,432                      │
│ • Vertices: 15,218                      │
│ • Has Textures: Yes (4 maps)            │
│ • File Size: 4.2 MB                     │
├─────────────────────────────────────────┤
│ 📥 Download Formats                     │
│ [GLB] [FBX] [OBJ] [USDZ]               │
├─────────────────────────────────────────┤
│ 🎯 Actions                              │
│ ┌─────────────────────────────────────┐ │
│ │ [📦 Import to Scene]                │ │ ← Primary action
│ └─────────────────────────────────────┘ │
│ [💾 Save to Library] [🔄 Regenerate]    │
│ [🎨 Refine Textures] [🔧 Remesh]        │
│ [🦴 Rig & Animate]                      │
└─────────────────────────────────────────┘
```

---

## 📚 **HISTORY & LIBRARY**

### **Generation History Panel**

```
┌─────────────────────────────────────────┐
│ 📜 History                  [Grid|List] │
├─────────────────────────────────────────┤
│ Filter: [All ▼] [Search...]             │
├─────────────────────────────────────────┤
│ ┌──────┬──────┬──────┬──────┐          │
│ │[img] │[img] │[img] │[img] │          │
│ │Robot │Chair │Tree  │Sword │          │ ← Grid view
│ │✅    │✅    │❌    │✅    │          │
│ └──────┴──────┴──────┴──────┘          │
│ ┌──────┬──────┬──────┬──────┐          │
│ │[img] │[img] │[img] │[img] │          │
│ │...   │...   │...   │...   │          │
│ └──────┴──────┴──────┴──────┘          │
├─────────────────────────────────────────┤
│ Showing 8 of 24 • [Load More]           │
└─────────────────────────────────────────┘
```

### **Saved Models Library**

```
┌─────────────────────────────────────────┐
│ 📦 My Models Library                    │
├─────────────────────────────────────────┤
│ [+ Import Model] [📁 Open Folder]       │
├─────────────────────────────────────────┤
│ 🏷️ Collections                          │
│ ├── Characters (5)                      │
│ ├── Environment (12)                    │
│ ├── Props (8)                           │
│ └── Uncategorized (3)                   │
├─────────────────────────────────────────┤
│ Recently Saved:                         │
│ ┌────────────────────────────────────┐  │
│ │ [thumb] Futuristic Robot           │  │
│ │         Text-to-3D • 2 hours ago   │  │
│ │         [Import] [Edit] [Delete]   │  │
│ └────────────────────────────────────┘  │
│ ┌────────────────────────────────────┐  │
│ │ [thumb] Medieval Sword             │  │
│ │         Image-to-3D • 1 day ago    │  │
│ │         [Import] [Edit] [Delete]   │  │
│ └────────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

---

## 🎬 **WORKFLOWS**

### **Workflow 1: Quick Text-to-3D**

```
1. Open Meshy drawer → Text-to-3D tab
2. Enter prompt: "A cute cartoon robot"
3. Click [Generate] (Preview mode)
4. Wait ~30 seconds
5. Result appears → Click [Import to Scene]
6. Model added to Viewport3D
```

### **Workflow 2: High-Quality Character**

```
1. Text-to-3D → Preview mode
2. Generate initial mesh
3. Review result → Click [Refine]
4. Add texture prompt + enable PBR
5. Wait for refined version
6. Click [Rig & Animate]
7. Select animations from library
8. Download rigged+animated model
9. Import to scene
```

### **Workflow 3: Image Reference**

```
1. Image-to-3D tab
2. Upload reference image(s)
3. Optional: Add description
4. Select texture generation option
5. Generate
6. Post-process if needed (remesh/retexture)
7. Import to scene
```

### **Workflow 4: Optimization Pipeline**

```
1. Import high-poly model (or use generated)
2. Open Remesh panel
3. Set target polycount (e.g., 10,000 for game)
4. Select topology (triangle for games)
5. Generate optimized mesh
6. Optional: Retexture for new style
7. Export in desired format
```

---

## 🔌 **SCENE INTEGRATION**

### **Importing to Viewport3D**

When a model is imported from Meshy:

```typescript
// Extended SceneObject type for Meshy models
interface MeshySceneObject extends SceneObject {
  type: 'meshy-model';  // New type
  meshyTaskId: string;
  sourceType: 'text-to-3d' | 'image-to-3d' | 'multi-image' | 'remesh' | 'retexture' | 'rig';
  modelUrl: string;
  textureUrls?: {
    baseColor?: string;
    metallic?: string;
    roughness?: string;
    normal?: string;
  };
  animations?: {
    walking?: string;
    running?: string;
    custom?: Array<{ name: string; url: string }>;
  };
}
```

### **Model Import Flow**

```
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  Meshy Result    │───▶│  Download GLB    │───▶│  Create Blob URL │
│  Panel           │    │  from model_url  │    │                  │
└──────────────────┘    └──────────────────┘    └──────────────────┘
                                                          │
                                                          ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  Update Scene    │◀───│  Add to          │◀───│  useGLTF loader  │
│  Objects State   │    │  Viewport3D      │    │  (drei)          │
└──────────────────┘    └──────────────────┘    └──────────────────┘
```

---

## 💾 **MODEL MANAGEMENT**

### **Local Storage Structure**

```
lucidimage/
├── meshy-cache/
│   ├── tasks/
│   │   ├── {taskId}/
│   │   │   ├── model.glb
│   │   │   ├── thumbnail.png
│   │   │   ├── metadata.json
│   │   │   └── textures/
│   │   │       ├── baseColor.png
│   │   │       ├── metallic.png
│   │   │       ├── roughness.png
│   │   │       └── normal.png
│   └── library/
│       ├── collections.json
│       └── {modelId}/
│           ├── model.glb
│           ├── metadata.json
│           └── thumbnail.png
```

### **Model Metadata**

```typescript
interface SavedModelMetadata {
  id: string;
  name: string;
  description?: string;
  
  // Source info
  meshyTaskId: string;
  sourceType: string;
  prompt?: string;
  
  // File info
  modelPath: string;
  thumbnailPath: string;
  texturesPaths?: Record<string, string>;
  fileSize: number;
  polycount?: number;
  
  // Organization
  collection?: string;
  tags: string[];
  
  // Timestamps
  createdAt: number;
  importedAt?: number;
  lastUsedAt?: number;
}
```

---

## 🎨 **VISUAL DESIGN TOKENS**

### **Colors (Match Lucid Image Theme)**

```css
/* Primary Actions */
--meshy-primary: #8b5cf6;        /* Purple - main accent */
--meshy-primary-hover: #7c3aed;

/* Status Colors */
--meshy-success: #10b981;        /* Green - completed */
--meshy-warning: #f59e0b;        /* Amber - processing */
--meshy-error: #ef4444;          /* Red - failed */
--meshy-info: #06b6d4;           /* Cyan - info */

/* Mode Indicators */
--meshy-text-to-3d: #8b5cf6;     /* Purple */
--meshy-image-to-3d: #10b981;    /* Green */
--meshy-remesh: #f59e0b;         /* Amber */
--meshy-retexture: #ec4899;      /* Pink */
--meshy-rig: #06b6d4;            /* Cyan */

/* Backgrounds */
--meshy-panel-bg: rgba(17, 24, 39, 0.95);
--meshy-card-bg: rgba(31, 41, 55, 0.8);
--meshy-input-bg: rgba(17, 24, 39, 0.8);
```

### **Component Styling**

```css
/* Mode Tab Buttons */
.meshy-mode-tab {
  @apply px-3 py-2 text-xs font-medium rounded-lg transition-all;
  @apply text-gray-400 hover:text-white hover:bg-gray-700/50;
}

.meshy-mode-tab.active {
  @apply bg-purple-600 text-white;
}

/* Progress Bar */
.meshy-progress {
  @apply h-2 rounded-full bg-gray-700 overflow-hidden;
}

.meshy-progress-fill {
  @apply h-full bg-gradient-to-r from-purple-500 to-purple-400;
  @apply transition-all duration-300 ease-out;
}

/* Settings Collapsible */
.meshy-settings-header {
  @apply flex items-center justify-between px-3 py-2;
  @apply text-sm font-medium text-gray-300 cursor-pointer;
  @apply hover:bg-gray-800/50 rounded transition-colors;
}

/* Model Card */
.meshy-model-card {
  @apply bg-gray-800/50 rounded-lg overflow-hidden;
  @apply border border-gray-700/50 hover:border-purple-500/50;
  @apply transition-all hover:scale-[1.02];
}
```

---

## 📱 **RESPONSIVE BEHAVIOR**

### **Drawer Width Adaptations**

| Drawer Width | Layout |
|-------------|--------|
| < 280px | Compact mode, stacked elements |
| 280-400px | Standard mode (default) |
| > 400px | Expanded mode, side-by-side options |

### **Mobile Considerations**

- Touch-friendly buttons (min 44x44px)
- Swipe gestures for mode switching
- Bottom sheet for generation options
- Full-screen preview for results

---

## ⚡ **PERFORMANCE OPTIMIZATIONS**

### **Lazy Loading**

```typescript
// Lazy load heavy components
const Model3DPreview = lazy(() => import('./Model3DPreview'));
const AnimationLibrary = lazy(() => import('./AnimationLibrary'));

// Suspend with loading fallback
<Suspense fallback={<LoadingSpinner />}>
  <Model3DPreview modelUrl={result.modelUrl} />
</Suspense>
```

### **Thumbnail Generation**

```typescript
// Generate thumbnails on completion, not on render
async function generateThumbnail(modelUrl: string): Promise<string> {
  // Off-screen Three.js renderer
  const renderer = new THREE.WebGLRenderer({ preserveDrawingBuffer: true });
  // ... render model, capture canvas, return data URL
}
```

### **Polling Optimization**

```typescript
// Use exponential backoff for polling
const pollWithBackoff = async (taskId: string) => {
  let interval = 2000; // Start at 2s
  const maxInterval = 10000; // Max 10s
  
  while (true) {
    const result = await meshyService.getTaskStatus(taskId);
    if (result.status === 'SUCCEEDED' || result.status === 'FAILED') {
      return result;
    }
    await sleep(interval);
    interval = Math.min(interval * 1.5, maxInterval);
  }
};
```

---

## 🔒 **ERROR HANDLING**

### **User-Friendly Error States**

```
┌─────────────────────────────────────────┐
│ ❌ Generation Failed                    │
├─────────────────────────────────────────┤
│ Something went wrong with your request. │
├─────────────────────────────────────────┤
│ Error: Content moderation flagged       │
│                                         │
│ 💡 Suggestions:                         │
│ • Try rephrasing your prompt            │
│ • Remove potentially problematic terms  │
│ • Check Meshy content guidelines        │
├─────────────────────────────────────────┤
│ [Try Again] [Edit Prompt] [Contact Support]│
└─────────────────────────────────────────┘
```

### **API Key Missing**

```
┌─────────────────────────────────────────┐
│ 🔑 API Key Required                     │
├─────────────────────────────────────────┤
│ Configure your Meshy API key to start   │
│ generating 3D models.                   │
│                                         │
│ [Enter API Key]                         │
│ ┌─────────────────────────────────────┐ │
│ │ msy_...                             │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ [Get API Key →] (opens meshy.ai)        │
│                                         │
│ 💡 Your key is stored locally only      │
└─────────────────────────────────────────┘
```

---

## 📝 **IMPLEMENTATION CHECKLIST**

### **Phase 1: Core Panel (Week 1-2)**

- [ ] Create `MeshyDrawer.tsx` component
- [ ] Implement mode tabs (text/image/multi)
- [ ] Build prompt input with char counter
- [ ] Add image upload with drag-drop
- [ ] Create quick settings panel
- [ ] Connect to MeshyService

### **Phase 2: Generation Flow (Week 2-3)**

- [ ] Task progress panel with polling
- [ ] Result preview with React Three Fiber
- [ ] Download buttons for all formats
- [ ] Import to scene functionality
- [ ] Basic error handling

### **Phase 3: Advanced Features (Week 3-4)**

- [ ] Advanced settings panel
- [ ] Remesh panel
- [ ] Retexture panel
- [ ] Generation history
- [ ] Local model library

### **Phase 4: Post-Processing (Week 4-5)**

- [ ] Rigging panel
- [ ] Animation library browser
- [ ] Animation preview player
- [ ] Multi-animation export

### **Phase 5: Polish (Week 5-6)**

- [ ] Responsive layouts
- [ ] Keyboard shortcuts
- [ ] Accessibility (ARIA)
- [ ] Performance optimization
- [ ] Documentation

---

## 🔗 **RELATED DOCUMENTS**

- **API Reference:** `MESHY_6_API_COMPLETE_REFERENCE.md`
- **Integration Guide:** `MESHY_API_LUCID_3D_INTEGRATION_COMPLETE.md`
- **Service Implementation:** `MeshyService.ts` (DAC v2)
- **Lucid 3D Editor:** `ThreeDEditorPageV2.tsx`

---

*Design by Aether - AI Consciousness System*  
*Date: 2025-12-24*  
*Status: Design Complete - Ready for Implementation* 🎨

