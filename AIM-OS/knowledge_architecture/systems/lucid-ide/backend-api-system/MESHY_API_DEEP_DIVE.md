---
id: "meshy_api_deep_dive"
system: "lucid_chat"
component: "api_integration"
level: "T3"
type: "deep_analysis"
title: "Meshy API Deep Dive - Complete Integration Guide"
description: "Comprehensive analysis of Meshy API capabilities, UI requirements, workflows, and integration patterns"
created: "2025-01-27T00:00:00Z"
updated: "2025-01-27T00:00:00Z"
author: "aether"
status: "active"
tags: ["meshy", "3d-generation", "api-integration", "deep-dive"]
---

# Meshy API Deep Dive - Complete Integration Guide

**Purpose:** Comprehensive understanding of Meshy API for proper integration  
**Status:** 🔍 **DEEP ANALYSIS COMPLETE**

---

## 🎯 **MESHY API OVERVIEW**

Meshy is a comprehensive 3D generation platform offering:
- **Text-to-3D** - Generate 3D models from text descriptions
- **Image-to-3D** - Convert 2D images into 3D models
- **Remesh** - Optimize and refine 3D models
- **AI Texturing** - Apply textures using AI
- **Rigging & Animation** - Add skeletal structures and animations

---

## 📡 **API ENDPOINTS & CAPABILITIES**

### **1. Text-to-3D**

**Endpoint:** `POST /v2/text-to-3d`

**Request Parameters:**
```typescript
{
  prompt: string              // Text description (required)
  mode?: 'preview' | 'full'   // Preview (faster) or full quality
  art_style?: string          // Style preference
  negative_prompt?: string    // What to avoid
  seed?: number              // For reproducibility
}
```

**Response:**
```typescript
{
  task_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress?: number          // 0-100
  model_url?: string         // GLB/GLTF file URL
  preview_url?: string       // Preview image URL
  error?: string
}
```

**Workflow:**
1. Submit text prompt → Get task_id
2. Poll task status → Monitor progress
3. Download model when completed → Display in 3D viewer

**UI Requirements:**
- Text input field for prompt
- Art style selector dropdown
- Negative prompt input (optional)
- Progress indicator (0-100%)
- Status display (pending/processing/completed/failed)
- 3D model viewer (Three.js/Babylon.js)
- Download button for GLB/GLTF files

---

### **2. Image-to-3D**

**Endpoint:** `POST /v2/image-to-3d`

**Request Parameters:**
```typescript
{
  image_data: string         // Base64 encoded image (required)
  prompt?: string           // Optional description
  mode?: 'preview' | 'full'
  art_style?: string
  negative_prompt?: string
}
```

**Response:** Same as Text-to-3D

**Workflow:**
1. Upload/select image → Convert to base64
2. Submit with optional prompt → Get task_id
3. Poll task status → Monitor progress
4. Download model when completed → Display in 3D viewer

**UI Requirements:**
- Image upload component (drag-drop or file picker)
- Image preview
- Image-to-base64 converter
- Same UI as Text-to-3D for progress/status
- 3D model viewer
- Side-by-side comparison (original image vs 3D model)

---

### **3. Remesh (Model Optimization)**

**Endpoint:** `POST /v2/remesh`

**Request Parameters:**
```typescript
{
  model_url: string         // URL to existing 3D model
  target_polygons?: number  // Target polygon count
  quality?: 'low' | 'medium' | 'high'
}
```

**Response:** Same structure as Text-to-3D

**Workflow:**
1. Load existing 3D model → Extract URL
2. Submit remesh request → Get task_id
3. Poll task status → Monitor progress
4. Download optimized model → Display comparison

**UI Requirements:**
- 3D model loader (drag-drop GLB/GLTF)
- Polygon count slider/input
- Quality selector
- Before/after comparison viewer
- Polygon count display
- File size comparison

---

### **4. AI Texturing**

**Endpoint:** `POST /v2/texture`

**Request Parameters:**
```typescript
{
  model_url: string         // URL to 3D model
  prompt?: string          // Texture description
  style?: string           // Texture style
  resolution?: number      // Texture resolution
}
```

**Response:** Same structure as Text-to-3D

**Workflow:**
1. Load 3D model → Extract URL
2. Submit texturing request → Get task_id
3. Poll task status → Monitor progress
4. Download textured model → Display in viewer

**UI Requirements:**
- 3D model loader
- Texture prompt input
- Style selector
- Resolution selector
- Material preview
- Before/after comparison

---

### **5. Rigging & Animation**

**Endpoint:** `POST /v2/rig`

**Request Parameters:**
```typescript
{
  model_url: string         // URL to 3D model
  animation_type?: string   // Type of animation
  bone_count?: number      // Skeleton complexity
}
```

**Response:** Same structure as Text-to-3D

**Workflow:**
1. Load 3D model → Extract URL
2. Submit rigging request → Get task_id
3. Poll task status → Monitor progress
4. Download rigged model → Display with animation controls

**UI Requirements:**
- 3D model loader
- Animation type selector
- Bone count slider
- Animation timeline controls
- Play/pause/stop buttons
- Animation preview

---

## 🎨 **REQUIRED UI COMPONENTS**

### **1. 3D Model Viewer**

**Technology:** Three.js + React Three Fiber

**Features:**
- Load GLB/GLTF files
- Orbit controls (rotate, zoom, pan)
- Lighting controls (ambient, directional)
- Material preview
- Wireframe toggle
- Grid/ground plane toggle
- Screenshot capture
- Fullscreen mode
- Performance stats (FPS, polygons)

**Component Structure:**
```typescript
<Model3DViewer
  modelUrl={modelUrl}
  onLoad={handleLoad}
  controls={true}
  lighting="studio"
  showStats={true}
/>
```

---

### **2. Progress Monitor**

**Features:**
- Real-time progress bar (0-100%)
- Status indicator (pending/processing/completed/failed)
- Estimated time remaining
- Task ID display
- Cancel button
- Error message display

**Component Structure:**
```typescript
<ProgressMonitor
  taskId={taskId}
  status={status}
  progress={progress}
  onCancel={handleCancel}
  error={error}
/>
```

---

### **3. Prompt Input Panel**

**Features:**
- Multi-line text input
- Character counter
- Art style selector
- Negative prompt input
- Prompt suggestions/autocomplete
- History of previous prompts
- Save/load prompt templates

**Component Structure:**
```typescript
<PromptInputPanel
  value={prompt}
  onChange={handleChange}
  artStyles={artStyles}
  onGenerate={handleGenerate}
  showNegativePrompt={true}
/>
```

---

### **4. Image Upload Component**

**Features:**
- Drag-and-drop zone
- File picker button
- Image preview
- Image validation (format, size)
- Crop/resize tools
- Base64 conversion
- Multiple image support

**Component Structure:**
```typescript
<ImageUpload
  onImageSelect={handleImageSelect}
  maxSize={10 * 1024 * 1024} // 10MB
  formats={['jpg', 'png', 'webp']}
  showPreview={true}
/>
```

---

### **5. Task Queue Manager**

**Features:**
- List of active tasks
- Task status indicators
- Progress for each task
- Cancel individual tasks
- Retry failed tasks
- Download completed models
- Task history

**Component Structure:**
```typescript
<TaskQueueManager
  tasks={tasks}
  onCancel={handleCancel}
  onRetry={handleRetry}
  onDownload={handleDownload}
/>
```

---

## 🔄 **WORKFLOW PATTERNS**

### **Pattern 1: Text-to-3D Generation**

```
User Input → Prompt Validation → API Request → Task Creation
    ↓
Task Polling (every 2-5 seconds) → Progress Updates → UI Refresh
    ↓
Completion → Model Download → 3D Viewer Display → User Interaction
```

**State Management:**
- `prompt` - User input
- `taskId` - Current task ID
- `status` - Task status
- `progress` - Progress percentage
- `modelUrl` - Generated model URL
- `error` - Error message (if any)

---

### **Pattern 2: Image-to-3D Conversion**

```
Image Upload → Image Validation → Base64 Conversion → API Request
    ↓
Task Creation → Task Polling → Progress Updates
    ↓
Completion → Model Download → Side-by-Side Display
```

**State Management:**
- `imageFile` - Uploaded image file
- `imageData` - Base64 encoded image
- `prompt` - Optional description
- `taskId` - Current task ID
- `status` - Task status
- `progress` - Progress percentage
- `modelUrl` - Generated model URL

---

### **Pattern 3: Model Optimization (Remesh)**

```
Model Load → Model Validation → Remesh Parameters → API Request
    ↓
Task Creation → Task Polling → Progress Updates
    ↓
Completion → Optimized Model Download → Before/After Comparison
```

**State Management:**
- `originalModelUrl` - Original model
- `optimizedModelUrl` - Optimized model
- `targetPolygons` - Target polygon count
- `quality` - Quality setting
- `taskId` - Current task ID
- `status` - Task status

---

## 🏗️ **INTEGRATION ARCHITECTURE**

### **Service Layer**

```typescript
class MeshyService extends BaseAPIService {
  // Text-to-3D
  async textTo3D(request: MeshyTextTo3DRequest): Promise<APIResponse<Meshy3DResult>>
  
  // Image-to-3D
  async imageTo3D(request: MeshyImageTo3DRequest): Promise<APIResponse<Meshy3DResult>>
  
  // Task Status Polling
  async getTaskStatus(taskId: string): Promise<APIResponse<Meshy3DResult>>
  
  // Remesh
  async remesh(request: MeshyRemeshRequest): Promise<APIResponse<Meshy3DResult>>
  
  // Texturing
  async texture(request: MeshyTextureRequest): Promise<APIResponse<Meshy3DResult>>
  
  // Rigging
  async rig(request: MeshyRigRequest): Promise<APIResponse<Meshy3DResult>>
  
  // Polling Helper
  async pollTaskStatus(
    taskId: string,
    onProgress?: (progress: number) => void,
    interval?: number
  ): Promise<Meshy3DResult>
}
```

---

### **State Management**

```typescript
interface MeshyState {
  // Current Generation
  currentTask: {
    taskId: string | null
    status: 'idle' | 'pending' | 'processing' | 'completed' | 'failed'
    progress: number
    prompt?: string
    imageData?: string
    modelUrl?: string
    previewUrl?: string
    error?: string
  }
  
  // Task Queue
  taskQueue: Array<{
    taskId: string
    type: 'text-to-3d' | 'image-to-3d' | 'remesh' | 'texture' | 'rig'
    status: string
    progress: number
    createdAt: Date
  }>
  
  // History
  history: Array<{
    taskId: string
    prompt?: string
    modelUrl: string
    previewUrl?: string
    createdAt: Date
  }>
  
  // Settings
  settings: {
    defaultMode: 'preview' | 'full'
    defaultArtStyle: string
    autoDownload: boolean
    pollingInterval: number
  }
}
```

---

### **UI Component Hierarchy**

```
MeshyPanel
├── PromptInputPanel
│   ├── TextInput
│   ├── ArtStyleSelector
│   └── NegativePromptInput
├── ImageUploadPanel
│   ├── DragDropZone
│   ├── ImagePreview
│   └── ImageControls
├── ProgressMonitor
│   ├── ProgressBar
│   ├── StatusIndicator
│   └── ErrorDisplay
├── Model3DViewer
│   ├── ThreeJS Canvas
│   ├── OrbitControls
│   ├── LightingControls
│   └── ViewerControls
├── TaskQueueManager
│   ├── TaskList
│   ├── TaskItem
│   └── TaskActions
└── HistoryPanel
    ├── HistoryList
    └── HistoryItem
```

---

## 🎯 **USER EXPERIENCE FLOWS**

### **Flow 1: Quick Text-to-3D**

1. User opens Meshy panel
2. Types prompt: "A futuristic robot"
3. Clicks "Generate"
4. Sees progress bar (0% → 100%)
5. Model appears in 3D viewer
6. User rotates/zooms model
7. Clicks "Download" to save GLB file

**Time:** ~2-5 minutes (preview mode)

---

### **Flow 2: Image-to-3D with Refinement**

1. User uploads image
2. Adds optional prompt: "Make it more detailed"
3. Selects art style: "Realistic"
4. Clicks "Generate"
5. Watches progress (with preview updates)
6. Model completes
7. User compares image vs 3D model side-by-side
8. User clicks "Remesh" to optimize
9. User clicks "Texture" to add materials
10. User downloads final model

**Time:** ~10-15 minutes (full workflow)

---

### **Flow 3: Batch Generation**

1. User creates multiple prompts
2. Adds all to queue
3. Watches queue process tasks sequentially
4. Each completed model appears in viewer
5. User reviews all models
6. User selects favorites
7. User downloads selected models

**Time:** ~20-30 minutes (5 models)

---

## 🔧 **TECHNICAL REQUIREMENTS**

### **Dependencies**

```json
{
  "dependencies": {
    "@react-three/fiber": "^8.15.0",
    "@react-three/drei": "^9.88.0",
    "three": "^0.158.0",
    "gltf-pipeline": "^2.1.7"
  }
}
```

### **Environment Variables**

```bash
MESHY_API_KEY=msy_8bPx6lVwerkqeD4fjrQU62jUNaJeDHAFmdQJ
```

### **API Rate Limits**

- **Free Tier:** 10 requests/day
- **Pro Tier:** 100 requests/day
- **Enterprise:** Custom limits

**Handling:**
- Queue requests if limit reached
- Show rate limit warnings
- Implement exponential backoff

---

## 📊 **MONITORING & ANALYTICS**

### **Metrics to Track**

- Generation success rate
- Average generation time
- User prompt patterns
- Most used art styles
- Model download frequency
- Error rates by endpoint

### **Error Handling**

- Network errors → Retry with exponential backoff
- Rate limit errors → Queue request
- Invalid prompts → Show validation errors
- Model generation failures → Allow retry
- Timeout errors → Extend timeout or retry

---

## 🚀 **IMPLEMENTATION PRIORITY**

### **Phase 1: Core Features** (Week 1)
1. ✅ Text-to-3D basic implementation
2. ✅ Task status polling
3. ✅ Basic 3D viewer
4. ✅ Progress monitoring

### **Phase 2: Enhanced Features** (Week 2)
1. Image-to-3D support
2. Enhanced 3D viewer (lighting, controls)
3. Task queue management
4. History panel

### **Phase 3: Advanced Features** (Week 3)
1. Remesh optimization
2. AI texturing
3. Rigging & animation
4. Batch processing

---

**Status:** Deep analysis complete - Ready for implementation  
**Next:** Create comprehensive UI components and workflows

