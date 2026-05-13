---
id: "meshy_6_api_complete_reference"
system: "lucid_ide"
component: "meshy_api_integration"
level: "T4"
type: "complete_reference"
title: "Meshy 6 API - Complete Reference Guide"
description: "Comprehensive reference for Meshy API v6 including all capabilities, requirements, usage patterns, and integration details"
created: "2025-01-27T00:00:00Z"
updated: "2025-12-24T00:00:00Z"
author: "aether"
status: "active"
tags: ["meshy", "meshy-6", "api-v6", "3d-generation", "complete-reference"]
---

# Meshy 6 API - Complete Reference Guide

**Purpose:** Complete reference for Meshy API v6 capabilities, requirements, and integration  
**Status:** ✅ **COMPREHENSIVE REFERENCE COMPLETE**  
**API Version:** Meshy “6 Preview” (select via `ai_model: "latest"`)  
**Base URLs:**
- **OpenAPI v2 (most endpoints):** `https://api.meshy.ai/openapi/v2`
- **OpenAPI v1 (rigging/animation, per docs):** `https://api.meshy.ai/openapi/v1`

---

## 🎯 **OVERVIEW**

Meshy API v6 is the latest version of Meshy's 3D generation API, offering enhanced capabilities for text-to-3D, image-to-3D, remeshing, texturing, rigging, and animation. This guide consolidates all knowledge about Meshy 6 API usage requirements and abilities.

---

## 🚀 **MESHY 6 KEY FEATURES**

### **Core Capabilities**

1. **Text-to-3D** - Generate 3D models from text descriptions
2. **Image-to-3D** - Convert 2D images into 3D models
3. **Multi-Image-to-3D** - Generate 3D models from multiple images
4. **Remesh** - Optimize and refine 3D model topology
5. **AI Texturing** - Apply AI-generated textures to models
6. **Rigging & Animation** - Automate rigging and animation processes
7. **Webhook Support** - Real-time task status notifications (NEW in v6)

### **AI Model Versions**

Meshy 6 API supports multiple AI model versions:

- **`latest`** - Meshy 6 Preview (default, recommended)
- **`meshy-5`** - Meshy 5 (previous generation)
- **`meshy-4`** - Meshy 4 (legacy)

**Recommendation:** Use `latest` for best quality and newest features.

---

## 📡 **API ENDPOINTS**

### **1. Text-to-3D**

**Endpoint:** `POST /v2/text-to-3d`

**Two-Stage Workflow:**
- **Stage 1: Preview** - Generates mesh-only 3D model (faster)
- **Stage 2: Refine** - Adds textures and PBR maps (slower, higher quality)

**Request Parameters:**

```typescript
{
  // Preview stage
  prompt: string                    // Required for preview: Text description (max 600 chars)
  mode: 'preview' | 'refine'       // Required: Stage selector

  // Refine stage
  preview_task_id?: string         // Required for refine: preview task must be SUCCEEDED

  art_style?: 'realistic' | 'sculpture'  // Optional: Style preference
  seed?: number                    // Optional: For reproducibility
  ai_model?: 'meshy-4' | 'meshy-5' | 'latest'  // Optional: Default 'latest'
  topology?: 'quad' | 'triangle'   // Optional: Default 'triangle'
  target_polycount?: number        // Optional: 100-300,000, default 30,000
  should_remesh?: boolean          // Optional: Default true
  symmetry_mode?: 'off' | 'auto' | 'on'  // Optional: Default 'auto'
  pose_mode?: '' | 'a-pose' | 't-pose'   // Optional: A/T pose selection
  is_a_t_pose?: boolean            // Deprecated in docs: use pose_mode instead
  moderation?: boolean             // Optional: Default false
  
  // Refine-only parameters
  enable_pbr?: boolean             // Optional: Generate PBR maps
  texture_prompt?: string          // Optional: Texture description (max 600 chars)
  texture_image_url?: string       // Optional: Image URL or data URI for texture guidance
}
```

**Response:**

```typescript
{
  result: string  // Task ID (k-sortable UUID)
}
```

**Workflow Example:**

```typescript
// Stage 1: Preview
const previewResult = await meshyService.textTo3D({
  prompt: 'A futuristic robot',
  mode: 'preview',
  art_style: 'realistic',
  ai_model: 'latest',  // Meshy 6
})

// Stage 2: Refine (after preview completes)
const refineResult = await meshyService.textTo3D({
  mode: 'refine',
  preview_task_id: previewResult.data.id,
  enable_pbr: true,
  texture_prompt: 'Metallic chrome with blue LED lights',
  ai_model: 'latest',  // Meshy 6
})
```

---

### **2. Image-to-3D**

**Endpoint:** `POST /v2/image-to-3d`

**Request Parameters:**

```typescript
{
  image_url: string                 // Required: public URL or Data URI (.jpg/.jpeg/.png)

  // Generation controls
  ai_model?: 'meshy-4' | 'meshy-5' | 'latest'
  topology?: 'quad' | 'triangle'
  target_polycount?: number         // 100-300,000
  symmetry_mode?: 'off' | 'auto' | 'on'
  should_remesh?: boolean
  save_pre_remeshed_model?: boolean // Store extra GLB pre-remesh (only if should_remesh=true)

  // Texturing controls
  should_texture?: boolean           // Skip texture stage if false
  enable_pbr?: boolean
  texture_prompt?: string            // Max 600 chars
  texture_image_url?: string         // public URL or Data URI

  // Pose controls
  pose_mode?: '' | 'a-pose' | 't-pose'
  is_a_t_pose?: boolean              // Deprecated in docs: use pose_mode instead

  moderation?: boolean
}
```

**Response:** Same as Text-to-3D

**Example:**

```typescript
const imageDataUri = await fileToDataUri(imageFile) // data:<mime>;base64,<...>
const result = await meshyService.imageTo3D({
  image_url: imageDataUri,
  should_texture: true,
  ai_model: 'latest',  // Meshy 6
})
```

---

### **3. Multi-Image-to-3D**

**Endpoint:** `POST /v2/multi-image-to-3d`

**Request Parameters:**

```typescript
{
  image_url: string[]               // Required: 1–4 images, each is public URL or Data URI

  // Controls (subset mirrors Image-to-3D)
  ai_model?: 'meshy-5' | 'latest'   // Docs note Meshy 6 Preview for texture
  topology?: 'quad' | 'triangle'
  target_polycount?: number
  symmetry_mode?: 'off' | 'auto' | 'on'
  should_remesh?: boolean
  save_pre_remeshed_model?: boolean
  should_texture?: boolean
  enable_pbr?: boolean
  pose_mode?: '' | 'a-pose' | 't-pose'
  texture_prompt?: string
  texture_image_url?: string
  moderation?: boolean
}
```

**Response:** Same as Text-to-3D

---

### **4. Remesh (Model Optimization)**

**Endpoint:** `POST /v2/remesh`

**Request Parameters:**

```typescript
{
  // Provide ONE of:
  input_task_id?: string            // Completed Image-to-3D or Text-to-3D task ID
  model_url?: string                // Public URL or Data URI (.glb/.gltf/.obj/.fbx/.stl)

  target_format?: Array<'glb' | 'fbx' | 'obj' | 'usdz' | 'blend' | 'stl'> // Default ['glb']
  topology?: 'quad' | 'triangle'
  target_polycount?: number         // 100–300,000
  resize_height?: number            // meters; 0 = no resize
  convert_format_only?: boolean     // If true, ignore topology/resize/polycount
}
```

**Response:** Same as Text-to-3D

**Use Case:** Optimize polygon count for performance or reduce file size.

---

### **5. Retexture (AI Texturing)**

**Endpoint:** `POST /v2/retexture`

**Request Parameters:**

```typescript
{
  model_url: string                 // Required: Public URL or Data URI (.glb/.gltf/.obj/.fbx/.stl)
  text_style_prompt: string         // Required if image_style_url not provided (max 600 chars)
  image_style_url?: string          // Optional: Public URL or Data URI (style reference)
  enable_pbr?: boolean
}
```

**Response:** Same as Text-to-3D

**PBR Maps Generated:**
- `base_color` - Base color texture
- `metallic` - Metallic map
- `roughness` - Roughness map
- `normal` - Normal map

---

### **6. Rigging & Animation**

**Endpoints:** (documented under OpenAPI v1)
- **Rigging:** `POST /openapi/v1/rigging`
- **Animation:** `POST /openapi/v1/animations`

**Request Parameters:**

```typescript
// Rigging
{
  input_task_id?: string            // Required if model_url not provided
  model_url?: string                // Required if input_task_id not provided (textured humanoid GLB)
  height_meters?: number            // Default 1.7
  texture_image_url?: string        // Optional base color texture (PNG) via URL or Data URI
}

// Animation
{
  rig_task_id: string               // Required: completed rigging task id
  action_id: number                 // Required: animation action id (see Animation Library Reference)
  post_process?: {
    operation_type: 'change_fps' | 'fbx2usdz' | 'extract_armature'
    fps?: 24 | 25 | 30 | 60         // Only for change_fps; default 30
  }
}
```

**Response:** Same as Text-to-3D

**Use Case:** Automatically add skeletal structure and animation capabilities to 3D models.

---

### **7. Task Status**

**Important:** Task retrieval is per-feature. Use the matching “Retrieve a … Task” endpoint for the task type.

**Common retrieve endpoints (OpenAPI v2):**
- `GET /v2/text-to-3d/{id}` (works for both preview + refine)
- `GET /v2/image-to-3d/{id}`
- `GET /v2/multi-image-to-3d/{id}`
- `GET /v2/remesh/{id}`
- `GET /v2/retexture/{id}`

**OpenAPI v1 (rigging/animation):**
- `GET /openapi/v1/rigging/{id}`
- `GET /openapi/v1/animations/{id}`

**Streaming:** Docs provide “Stream a … Task” endpoints using Server-Sent Events (SSE) for these task types.

**Response:**

```typescript
{
  id: string                       // Task ID (k-sortable UUID)
  model_urls?: {
    glb?: string                   // GLB file URL
    fbx?: string                   // FBX file URL
    usdz?: string                   // USDZ file URL
    obj?: string                   // OBJ file URL
    mtl?: string                   // MTL file URL
  }
  prompt?: string
  art_style?: string
  texture_prompt?: string
  texture_image_url?: string
  thumbnail_url?: string           // Preview image URL
  video_url?: string               // Preview video URL
  progress: number                 // 0-100
  seed?: number
  started_at: number               // Timestamp in milliseconds
  created_at: number               // Timestamp in milliseconds
  finished_at: number              // Timestamp in milliseconds
  status: 'PENDING' | 'IN_PROGRESS' | 'SUCCEEDED' | 'FAILED' | 'CANCELED'
  texture_urls?: Array<{
    base_color?: string
    metallic?: string
    normal?: string
    roughness?: string
  }>
  preceding_tasks?: number
  task_error?: {
    message: string
  }
}
```

---

### **8. Balance Check**

**Endpoint:** `GET /v2/balance`

**Response:**

```typescript
{
  balance: number  // Current API credit balance
}
```

---

## 🔐 **AUTHENTICATION & SETUP**

### **1. Account Creation**

1. Register at [meshy.ai](https://www.meshy.ai)
2. Navigate to API settings
3. Generate API key

### **2. API Key Format**

```
msy_...
```

**Format:** `msy_` prefix followed by alphanumeric string

### **3. Authentication Header**

```typescript
headers: {
  'Authorization': `Bearer ${apiKey}`,
  'Content-Type': 'application/json'
}
```

### **4. Environment Configuration**

```bash
# .env
MESHY_API_KEY=msy_...
```

---

## 💳 **PRICING & CREDITS**

### **Credit System**

Meshy API pricing is credit-based (pay-before-you-go). Official docs provide a per-call credit breakdown.

**Common costs (from docs):**
- **Text to 3D (Preview) – Mesh generation:** Meshy‑6 models: **20 credits**; other models: **5 credits**
- **Text to 3D (Refine) – Texture generation:** **10 credits**
- **Image to 3D:** Meshy‑6 models: **20 credits (no texture)** / **30 credits (with texture)**; other models: **5 credits (no texture)** / **15 credits (with texture)**
- **Multi Image to 3D:** **5 credits (no texture)** / **15 credits (with texture)**
- **Retexture:** **10 credits**
- **Remesh:** **5 credits**
- **Auto‑rigging:** **5 credits**
- **Animation:** **3 credits**

---

## ⚡ **RATE LIMITS & CONCURRENCY**

### **How rate limits work (docs)**

Rate limits are measured in two ways:
- **Requests per Second**: network requests per second
- **Queue Tasks**: concurrent *generation tasks* allowed at once

**Queue Tasks include:** Text to 3D, Image to 3D, Text to Texture (Retexture), Remesh.  
**Not included:** endpoints like Upload and Balance.

Limits are **per account**, shared across **all API keys**.

**Example (Pro tier, from docs UI):** 20 requests/second, 10 queue tasks.

### **Best Practices**

1. **Polling Interval:** 2-5 seconds (recommended: 2 seconds)
2. **Concurrent Tasks:** Queue tasks if limit reached
3. **Error Handling:** Implement exponential backoff
4. **Rate Limit Headers:** Check response headers for rate limit info

### **Rate Limit Handling**

```typescript
// Example: Queue requests if rate limit reached
if (response.status === 429) {
  // Two 429 cases are documented:
  // - RateLimitExceeded (too many requests/sec)
  // - NoMoreConcurrentTask (too many concurrent generation tasks)
  //
  // Handle by queuing locally and retrying with backoff.
}
```

---

## 🔔 **WEBHOOK SUPPORT (NEW IN MESHY 6)**

### **Webhook Configuration**

Meshy 6 supports webhooks for real-time task status notifications.

**Benefits:**
- No polling required
- Instant notifications
- Reduced API calls
- Better scalability

### **Webhook Setup**

1. Configure webhook URL in Meshy dashboard
2. Receive POST requests when task status changes
3. Store/ack payload quickly; process asynchronously

**Webhook Payload:**

```typescript
{
  task_id: string
  status: 'PENDING' | 'IN_PROGRESS' | 'SUCCEEDED' | 'FAILED' | 'CANCELED'
  progress: number
  model_urls?: {
    glb?: string
    // ... other formats
  }
  // ... other task fields
}
```

**Delivery requirement (docs):** Your server must respond with HTTP status < 400. Responses >= 400 are treated as failed delivery; repeated failures can delay updates and may auto-disable the webhook.

---

## 📊 **PARAMETER REFERENCE**

### **Art Styles**

- **`realistic`** - Photorealistic rendering
- **`sculpture`** - Artistic sculpture style

### **Topology Options**

- **`triangle`** - Decimated triangular mesh (default)
- **`quad`** - Quad-dominant mesh (better for animation)

### **Symmetry Modes**

- **`auto`** - Automatic symmetry detection (recommended)
- **`on`** - Enforce symmetry
- **`off`** - Disable symmetry

### **Polycount Ranges**

- **Minimum:** 100 polygons
- **Maximum:** 300,000 polygons
- **Default:** 30,000 polygons

**Recommendations:**
- **Low-poly:** 1,000-10,000 (games, mobile)
- **Medium-poly:** 10,000-50,000 (general use)
- **High-poly:** 50,000-300,000 (detailed models, renders)

---

## 🎨 **TEXTURE & PBR MAPS**

### **PBR Maps (Physically Based Rendering)**

When `enable_pbr: true`:

1. **Base Color** - Main texture map
2. **Metallic** - Metallic properties
3. **Roughness** - Surface roughness
4. **Normal** - Surface detail

### **Texture Guidance**

**Texture Prompt:**
- Max 600 characters
- Describes desired texture style
- Example: "Rustic wood with metal accents"

**Texture Image:**
- Image URL or data URI
- Guides texture generation
- Can be combined with texture prompt

---

## 🔄 **WORKFLOW PATTERNS**

### **Pattern 1: Quick Preview**

```typescript
// Fast preview generation
const preview = await meshyService.textTo3D({
  prompt: 'A chair',
  mode: 'preview',
  ai_model: 'latest',  // Meshy 6
})

// Poll for completion
const result = await meshyService.pollTaskStatus(preview.data.id)
```

**Time:** ~2-5 minutes

---

### **Pattern 2: Full Quality with Textures**

```typescript
// Stage 1: Preview
const preview = await meshyService.textTo3D({
  prompt: 'A futuristic robot',
  mode: 'preview',
  ai_model: 'latest',
})

await meshyService.pollTaskStatus(preview.data.id)

// Stage 2: Refine with textures
const refined = await meshyService.textTo3D({
  mode: 'refine',
  preview_task_id: preview.data.id,
  enable_pbr: true,
  texture_prompt: 'Metallic chrome with blue LED lights',
  ai_model: 'latest',
})

await meshyService.pollTaskStatus(refined.data.id)
```

**Time:** ~10-15 minutes

---

### **Pattern 3: Image-to-3D with Optimization**

```typescript
// Convert image to 3D
const model = await meshyService.imageTo3D({
  image_url: imageDataUri,
  should_texture: true,
  ai_model: 'latest',
})

await meshyService.pollTaskStatus(model.data.id)

// Optimize polygon count
const optimized = await meshyService.remesh({
  input_task_id: model.data.id,
  target_polycount: 10000,  // Reduce to 10K
  topology: 'triangle',
})

await meshyService.pollTaskStatus(optimized.data.id)
```

**Time:** ~15-20 minutes

---

### **Pattern 4: Complete Pipeline**

```typescript
// 1. Generate from text
const generated = await meshyService.textTo3D({
  prompt: 'A character',
  mode: 'preview',
  ai_model: 'latest',
})
await meshyService.pollTaskStatus(generated.data.id)

// 2. Add textures
const textured = await meshyService.textTo3D({
  mode: 'refine',
  preview_task_id: generated.data.id,
  enable_pbr: true,
  ai_model: 'latest',
})
await meshyService.pollTaskStatus(textured.data.id)

// 3. Optimize
const optimized = await meshyService.remesh({
  input_task_id: textured.data.id,
  target_polycount: 15000,
})

// 4. Add rigging
const rigged = await meshyService.rig({
  input_task_id: optimized.data.id,
})
```

**Time:** ~20-30 minutes

---

## 🛠️ **INTEGRATION REQUIREMENTS**

### **Dependencies**

```json
{
  "dependencies": {
    "@react-three/fiber": "^8.15.0",
    "@react-three/drei": "^9.88.0",
    "three": "^0.158.0"
  }
}
```

### **Service Implementation**

**Base Service Class:**

```typescript
class MeshyService extends BaseAPIService {
  constructor(apiKey?: string) {
    super('meshy', 'https://api.meshy.ai/openapi/v2', apiKey)
  }

  protected getDefaultHeaders(): Record<string, string> {
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${this.apiKey}`,
    }
  }
}
```

### **Polling System**

```typescript
async pollTaskStatus(
  taskId: string,
  onProgress?: (progress: number, status: string) => void,
  interval: number = 2000,
  maxAttempts: number = 150
): Promise<APIResponse<Meshy3DResult>> {
  // Poll every 2 seconds for up to 5 minutes
  // Call onProgress callback with updates
  // Return when task completes or fails
}
```

---

## 🚨 **ERROR HANDLING**

### **Common Errors**

**401 Unauthorized:**
- Invalid or missing API key
- Solution: Verify API key in environment variables

**429 Rate Limit:**
- Too many requests
- Solution: Implement exponential backoff, queue requests

**400 Bad Request:**
- Invalid parameters
- Solution: Validate request parameters before sending

**404 Not Found:**
- Invalid task ID
- Solution: Verify task ID exists

**500 Server Error:**
- Meshy API issue
- Solution: Retry with exponential backoff

### **Error Response Format**

```typescript
{
  error: {
    message: string
    code?: string
  }
}
```

---

## 📈 **PERFORMANCE OPTIMIZATION**

### **Best Practices**

1. **Use Preview Mode First** - Faster, lower cost
2. **Batch Requests** - Queue multiple tasks
3. **Cache Results** - Store completed models
4. **Optimize Polycount** - Use appropriate polygon counts
5. **Webhook Instead of Polling** - Reduce API calls (if available)

### **Performance Metrics**

- **Preview Generation:** 2-5 minutes
- **Refine Generation:** 5-10 minutes
- **Remesh:** 1-3 minutes
- **Retexture:** 3-7 minutes
- **Rigging:** 5-10 minutes

---

## 🔍 **MESHY 6 SPECIFIC FEATURES**

### **Enhanced Quality**

- **Better Geometry** - Improved mesh topology
- **Higher Resolution** - Better detail preservation
- **Improved Textures** - More realistic PBR maps

### **New Capabilities**

- **Webhook Support** - Real-time notifications
- **Better Multi-Image** - Improved multi-view reconstruction
- **Enhanced Rigging** - Better bone placement

### **Performance Improvements**

- **Faster Generation** - Optimized processing
- **Better Concurrency** - More concurrent tasks
- **Improved Reliability** - Better error handling

---

## 📚 **EXISTING IMPLEMENTATIONS**

### **DAC v2 IDE**

**Location:** `ide_orchestration/prototypes/dac/`

**Components:**
- ✅ `ComprehensiveMeshyPanel.tsx` (1,180 lines) - Full UI
- ✅ `MeshyService.ts` (410 lines) - Service layer
- ✅ `Model3DViewer.tsx` - Three.js viewer
- ✅ `ProgressMonitor.tsx` - Progress tracking
- ✅ Meshy Store (Zustand) - State management

**Status:** ✅ **PRODUCTION READY**

### **Lucid Image 3D App**

**Location:** `Documentation/appexamples/lucidimage/project/`

**Status:** ⏳ **READY FOR INTEGRATION**

**Integration Steps:**
1. Copy components from DAC v2 IDE
2. Configure API key
3. Add to 3D page drawer

---

## ✅ **CHECKLIST FOR MESHY 6 INTEGRATION**

### **Setup**

- [ ] Create Meshy account
- [ ] Generate API key
- [ ] Configure environment variables
- [ ] Verify API key works (balance check)

### **Implementation**

- [ ] Copy MeshyService from DAC v2 IDE
- [ ] Copy ComprehensiveMeshyPanel component
- [ ] Copy Model3DViewer component
- [ ] Copy ProgressMonitor component
- [ ] Set up Zustand store (or adapt)

### **Configuration**

- [ ] Set `ai_model: 'latest'` for Meshy 6
- [ ] Configure polling interval (2 seconds)
- [ ] Set up error handling
- [ ] Implement rate limit handling

### **Testing**

- [ ] Test text-to-3D (preview mode)
- [ ] Test text-to-3D (refine mode)
- [ ] Test image-to-3D
- [ ] Test remesh
- [ ] Test retexture
- [ ] Test rigging
- [ ] Test error handling
- [ ] Test rate limits

### **Optimization**

- [ ] Implement webhook support (if available)
- [ ] Add request queuing
- [ ] Cache completed models
- [ ] Optimize polygon counts
- [ ] Monitor API usage

---

## 📖 **REFERENCES**

### **Official Documentation**

- **Meshy API Docs:** https://docs.meshy.ai/en/api/
- **Authentication:** https://docs.meshy.ai/en/api/authentication
- **Pricing:** https://docs.meshy.ai/en/api/pricing
- **Rate Limits:** https://docs.meshy.ai/api/rate-limits

### **Internal Documentation**

- **Deep Dive:** `MESHY_API_DEEP_DIVE.md`
- **Integration Guide:** `MESHY_API_LUCID_3D_INTEGRATION_COMPLETE.md`
- **Service Implementation:** `ide_orchestration/prototypes/dac/src/services/lucid-chat/threeD/MeshyService.ts`

### **Code References**

- **Comprehensive Panel:** `ide_orchestration/prototypes/dac/src/components/lucid-chat/meshy/ComprehensiveMeshyPanel.tsx`
- **Model Viewer:** `ide_orchestration/prototypes/dac/src/components/lucid-chat/threeD/Model3DViewer.tsx`
- **Progress Monitor:** `ide_orchestration/prototypes/dac/src/components/lucid-chat/ProgressMonitor.tsx`

---

## 🎯 **SUMMARY**

### **Meshy 6 API Capabilities**

✅ **Text-to-3D** - Two-stage workflow (preview → refine)  
✅ **Image-to-3D** - Single and multi-image support  
✅ **Remesh** - Topology optimization  
✅ **Retexture** - AI-powered texturing with PBR maps  
✅ **Rigging & Animation** - Automated rigging  
✅ **Webhook Support** - Real-time notifications (NEW)  
✅ **Multiple AI Models** - Meshy 4, 5, and 6 (latest)  

### **Key Requirements**

- **API Key:** Required for all requests
- **Credits:** Credit-based pricing system
- **Rate Limits:** 20 req/s, 10 concurrent tasks (Pro tier)
- **Polling:** 2-second interval recommended
- **Error Handling:** Exponential backoff for retries

### **Best Practices**

- Use `ai_model: 'latest'` for Meshy 6
- Start with preview mode for faster results
- Use webhooks instead of polling (if available)
- Optimize polygon counts for target use case
- Implement proper error handling and retries

---

**Status:** ✅ **COMPLETE REFERENCE GUIDE**  
**Last Updated:** 2025-01-27  
**API Version:** v6 (Latest)  
**Next Steps:** Integrate into Lucid Image 3D app using existing DAC v2 IDE components

