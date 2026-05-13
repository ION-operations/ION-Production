---
id: "replicate_stable_diffusion_api_deep_dive"
system: "lucid_chat"
component: "api_integration"
level: "T3"
type: "deep_analysis"
title: "Replicate Stable Diffusion API Deep Dive - Complete Integration Guide"
description: "Comprehensive analysis of Replicate API for Stable Diffusion and other image generation models"
created: "2025-01-27T00:00:00Z"
updated: "2025-01-27T00:00:00Z"
author: "aether"
status: "active"
tags: ["replicate", "stable-diffusion", "image-generation", "api-integration", "deep-dive"]
---

# Replicate Stable Diffusion API Deep Dive - Complete Integration Guide

**Purpose:** Comprehensive understanding of Replicate API for Stable Diffusion integration  
**Status:** 🔍 **DEEP ANALYSIS IN PROGRESS**  
**Official Documentation:** https://replicate.com/docs

---

## 🎯 **REPLICATE API OVERVIEW**

Replicate is a platform that provides access to various AI models, including:
- **Stable Diffusion** (multiple versions: SDXL, SD 1.5, etc.)
- **ControlNet** models
- **Image-to-Image** models
- **Inpainting** models
- **Upscaling** models
- **Many other AI models** (not just image generation)

**Key Features:**
- Access to 100+ pre-trained models
- Simple REST API
- Pay-per-use pricing
- Async prediction system
- Webhook support
- Model versioning

---

## 🔐 **AUTHENTICATION**

**Method:** Bearer Token (API Token)

**Header:**
```
Authorization: Token YOUR_API_TOKEN
```

**API Token Management:**
- Obtain from: https://replicate.com/account/api-tokens
- Store securely in environment variable: `REPLICATE_API_TOKEN`
- Rate limits: Based on account tier

---

## 📡 **API ENDPOINTS & CAPABILITIES**

### **1. Create Prediction**

**Endpoint:** `POST https://api.replicate.com/v1/predictions`

**Purpose:** Run a model prediction (e.g., generate image)

**Request Parameters:**

```typescript
interface ReplicateCreatePredictionRequest {
  // Required
  version: string                  // Model version ID (e.g., "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b")
  
  // Required - Input parameters (varies by model)
  input: {
    // Stable Diffusion Common Parameters
    prompt: string                 // Text prompt (required)
    negative_prompt?: string       // What to avoid
    num_outputs?: number           // Number of images (1-4, default: 1)
    guidance_scale?: number        // How closely to follow prompt (1-20, default: 7.5)
    num_inference_steps?: number  // Number of denoising steps (1-500, default: 50)
    seed?: number                 // Random seed for reproducibility
    width?: number                // Image width (must be multiple of 8)
    height?: number               // Image height (must be multiple of 8)
    
    // SDXL Specific Parameters
    prompt_strength?: number      // Strength of prompt (0-1)
    refine?: string               // Refinement option
    scheduler?: string            // Scheduler type
    lora_scale?: number           // LoRA scale
    
    // Image-to-Image Parameters
    image?: string                // Input image URL or base64
    image_prompt?: string         // Prompt for image-to-image
    prompt_strength?: number      // How much to change image (0-1)
    
    // Inpainting Parameters
    mask?: string                 // Mask image URL or base64
    mask_prompt?: string          // Prompt for inpainting
    
    // ControlNet Parameters
    controlnet_conditioning_scale?: number  // ControlNet strength
    controlnet_image?: string              // ControlNet input image
    
    // Upscaling Parameters
    scale?: number                // Upscale factor
    face_enhance?: boolean        // Face enhancement
    
    // Other model-specific parameters
    [key: string]: any           // Additional model-specific params
  }
  
  // Optional
  webhook?: string                // Webhook URL for completion notification
  webhook_events_filter?: string[] // Events to trigger webhook
  stream?: boolean                // Stream prediction output
}
```

**Common Stable Diffusion Models:**

1. **Stable Diffusion XL (SDXL):**
   - Model: `stability-ai/sdxl`
   - Latest version: Check API for current version ID
   - Supports: Text-to-image, high resolution

2. **Stable Diffusion 1.5:**
   - Model: `stability-ai/stable-diffusion`
   - Supports: Text-to-image, image-to-image, inpainting

3. **Stable Diffusion 2.1:**
   - Model: `stability-ai/stable-diffusion-2-1`
   - Supports: Text-to-image, image-to-image

4. **ControlNet Models:**
   - Various ControlNet models available
   - Enable structured control over generation

**Response Structure:**

```typescript
interface ReplicatePredictionResponse {
  id: string                      // Prediction ID
  version: string                  // Model version ID
  urls: {
    get: string                   // Get prediction status
    cancel: string                 // Cancel prediction
    stream?: string               // Stream URL (if streaming)
  }
  created_at: string              // ISO 8601 timestamp
  started_at?: string             // When prediction started
  completed_at?: string           // When prediction completed
  status: 'starting' | 'processing' | 'succeeded' | 'failed' | 'canceled'
  input: Record<string, any>      // Input parameters
  output?: string | string[]       // Output (URL(s) or data)
  error?: string                  // Error message
  logs?: string                   // Logs (if available)
  metrics?: {
    predict_time?: number         // Prediction time in seconds
  }
}
```

**Workflow:**
1. User selects model
2. Configure input parameters
3. Submit prediction → Get prediction ID
4. Poll prediction status → Monitor progress
5. When status = 'succeeded', get output URL(s)
6. Display image(s) in UI

**UI Requirements:**
- Model selector (dropdown with search)
- Prompt input field
- Negative prompt input (optional)
- Parameter controls (guidance_scale, steps, etc.)
- Image display area
- Status indicator
- Progress display
- Download buttons

---

### **2. Get Prediction**

**Endpoint:** `GET https://api.replicate.com/v1/predictions/{prediction_id}`

**Purpose:** Get status and output of a prediction

**Response:** Same as Create Prediction response

**Use Case:** Polling for async predictions

---

### **3. List Predictions**

**Endpoint:** `GET https://api.replicate.com/v1/predictions`

**Purpose:** List all predictions (with pagination)

**Query Parameters:**

```typescript
interface ReplicateListPredictionsQuery {
  cursor?: string                 // Pagination cursor
  limit?: number                  // Results per page (default: 100)
}
```

**Response:**

```typescript
interface ReplicateListPredictionsResponse {
  previous?: string               // Previous page cursor
  next?: string                  // Next page cursor
  results: ReplicatePredictionResponse[]
}
```

---

### **4. Cancel Prediction**

**Endpoint:** `POST https://api.replicate.com/v1/predictions/{prediction_id}/cancel`

**Purpose:** Cancel a running prediction

**Response:** Updated prediction object with status='canceled'

---

### **5. List Models**

**Endpoint:** `GET https://api.replicate.com/v1/models`

**Purpose:** List available models (with search/filter)

**Query Parameters:**

```typescript
interface ReplicateListModelsQuery {
  cursor?: string
  limit?: number
  query?: string                  // Search query
  owner?: string                  // Filter by owner
}
```

**Response:**

```typescript
interface ReplicateListModelsResponse {
  previous?: string
  next?: string
  results: Array<{
    url: string                   // Model URL
    owner: string                 // Owner username
    name: string                  // Model name
    description?: string
    visibility: 'public' | 'private'
    github_url?: string
    paper_url?: string
    license_url?: string
    cover_image_url?: string
    default_example?: {
      input: Record<string, any>
      output: any
    }
    latest_version?: {
      id: string
      created_at: string
      cog_version: string
    }
  }>
}
```

---

### **6. Get Model**

**Endpoint:** `GET https://api.replicate.com/v1/models/{owner}/{model_name}`

**Purpose:** Get details about a specific model

**Response:** Model object with versions, examples, etc.

---

### **7. Get Model Version**

**Endpoint:** `GET https://api.replicate.com/v1/models/{owner}/{model_name}/versions/{version_id}`

**Purpose:** Get details about a specific model version

**Response:**

```typescript
interface ReplicateModelVersion {
  id: string
  created_at: string
  cog_version: string
  openapi_schema: {
    // OpenAPI schema defining input/output
    components: {
      schemas: {
        Input: {
          type: 'object'
          properties: Record<string, any>
          required?: string[]
        }
        Output: {
          type: 'object' | 'array' | 'string'
        }
      }
    }
  }
}
```

**Use Case:** Dynamically discover model parameters

---

## 🔄 **WORKFLOWS**

### **Workflow 1: Text-to-Image Generation**

1. User selects Stable Diffusion model (e.g., SDXL)
2. Enter prompt
3. Configure parameters:
   - Negative prompt (optional)
   - Number of outputs (1-4)
   - Guidance scale (1-20)
   - Inference steps (1-500)
   - Width/Height (multiples of 8)
   - Seed (for reproducibility)
4. Submit prediction → Get prediction ID
5. Poll status every 1-2 seconds
6. When status = 'succeeded', get output URL(s)
7. Display image(s) in grid
8. Allow downloads

### **Workflow 2: Image-to-Image**

1. User selects image-to-image model
2. Upload input image
3. Enter prompt
4. Configure prompt_strength (0-1)
5. Configure other parameters
6. Submit → Poll → Display result

### **Workflow 3: Inpainting**

1. User selects inpainting model
2. Upload image
3. Upload mask (or draw mask)
4. Enter prompt
5. Configure parameters
6. Submit → Poll → Display result

### **Workflow 4: Upscaling**

1. User selects upscaling model
2. Upload image
3. Configure scale factor
4. Configure face_enhance (if available)
5. Submit → Poll → Display result

---

## ⚡ **RATE LIMITS**

**Free Tier:**
- Limited predictions per month
- Lower rate limits

**Paid Tier:**
- Higher rate limits
- Pay-per-use pricing

**Rate Limit Headers:**
```
x-ratelimit-limit: 100
x-ratelimit-remaining: 99
x-ratelimit-reset: 2025-01-27T18:00:00Z
```

---

## 💰 **PRICING**

**Pay-per-use:**
- Each prediction costs based on:
  - Model used
  - Compute time
  - Output size

**Example Pricing (may vary):**
- SDXL: ~$0.003-0.01 per image
- SD 1.5: ~$0.002-0.005 per image
- Upscaling: ~$0.001-0.003 per image

**Note:** Check Replicate pricing page for current rates.

---

## 🎨 **UI COMPONENT REQUIREMENTS**

### **Main Generation Panel**

**Model Selector:**
- Searchable dropdown
- Show model descriptions
- Show example outputs
- Group by category (Text-to-Image, Image-to-Image, etc.)

**Prompt Input:**
- Large textarea
- Character counter
- Examples/tips

**Negative Prompt Input:**
- Textarea (optional)
- Collapsible section
- Examples

**Parameter Controls:**

**Number of Outputs:**
- Number input or slider: 1-4
- Show estimated cost

**Guidance Scale:**
- Slider: 1-20 (default: 7.5)
- Show description: "How closely to follow prompt"
- Real-time preview of effect

**Inference Steps:**
- Slider: 1-500 (default: 50)
- Show description: "More steps = higher quality but slower"
- Show estimated time

**Width/Height:**
- Number inputs (must be multiples of 8)
- Preset buttons: "512x512", "768x768", "1024x1024", etc.
- Aspect ratio lock option

**Seed:**
- Number input
- Randomize button
- Use same seed checkbox

**Advanced Parameters (Collapsible):**
- Model-specific parameters
- Discovered from model version schema

**Generate Button:**
- Large, prominent
- Show loading state
- Disable during generation

**Status Display:**
- Status badge: "Starting" | "Processing" | "Succeeded" | "Failed"
- Progress indicator (if available)
- Time elapsed

**Image Display Area:**
- Grid layout for multiple images
- Full-size view on click
- Download buttons
- Share buttons

**Error Display:**
- Red alert box
- Error message
- Retry button

### **Image-to-Image Panel**

**Input Image Upload:**
- Drag-and-drop area
- File picker
- Image preview
- Format validation

**Prompt Input:**
- Same as main panel

**Prompt Strength:**
- Slider: 0-1 (default: 0.8)
- Show description: "How much to change image"

**Other Parameters:**
- Same as main panel

**Result Display:**
- Side-by-side: Input | Output
- Download buttons

### **Inpainting Panel**

**Image Upload:**
- Same as image-to-image

**Mask Upload/Drawing:**
- Upload mask image OR
- Draw mask on image (canvas)
- Show mask overlay

**Prompt Input:**
- Same as main panel

**Result Display:**
- Original | Masked | Result
- Download buttons

---

## 🔧 **IMPLEMENTATION NOTES**

### **Service Layer Structure**

```typescript
class ReplicateService extends BaseAPIService {
  constructor(apiToken?: string) {
    super('replicate', 'https://api.replicate.com/v1', apiToken)
  }

  async createPrediction(request: ReplicateCreatePredictionRequest): Promise<APIResponse<ReplicatePredictionResponse>>
  async getPrediction(predictionId: string): Promise<APIResponse<ReplicatePredictionResponse>>
  async listPredictions(query?: ReplicateListPredictionsQuery): Promise<APIResponse<ReplicateListPredictionsResponse>>
  async cancelPrediction(predictionId: string): Promise<APIResponse<ReplicatePredictionResponse>>
  async listModels(query?: ReplicateListModelsQuery): Promise<APIResponse<ReplicateListModelsResponse>>
  async getModel(owner: string, modelName: string): Promise<APIResponse<ReplicateModel>>
  async getModelVersion(owner: string, modelName: string, versionId: string): Promise<APIResponse<ReplicateModelVersion>>
  
  // Helper methods
  async pollPrediction(predictionId: string, onProgress?: (status: string) => void): Promise<APIResponse<ReplicatePredictionResponse>>
  async getStableDiffusionModels(): Promise<APIResponse<ReplicateModel[]>>
}
```

### **State Management**

```typescript
interface ReplicateState {
  // Model Selection
  selectedModel: string | null
  selectedVersion: string | null
  availableModels: ReplicateModel[]
  
  // Generation Parameters
  prompt: string
  negativePrompt: string
  numOutputs: number
  guidanceScale: number
  numInferenceSteps: number
  width: number
  height: number
  seed?: number
  
  // Current Prediction
  currentPrediction: ReplicatePredictionResponse | null
  isGenerating: boolean
  status: string
  
  // Results
  images: string[]
  error: string | null
  
  // History
  history: Array<{
    predictionId: string
    prompt: string
    images: string[]
    model: string
    timestamp: Date
  }>
}
```

### **Dynamic Parameter Discovery**

Since Replicate models have different parameters, we should:
1. Fetch model version schema on model selection
2. Dynamically generate UI controls based on schema
3. Validate inputs against schema
4. Show/hide parameters based on model type

### **Polling Strategy**

```typescript
async pollPrediction(
  predictionId: string,
  onProgress?: (status: string, output?: any) => void,
  interval: number = 2000,
  maxAttempts: number = 300 // 10 minutes max
): Promise<APIResponse<ReplicatePredictionResponse>> {
  let attempts = 0
  while (attempts < maxAttempts) {
    const result = await this.getPrediction(predictionId)
    if (!result.success) return result
    
    const { status, output } = result.data!
    if (onProgress) onProgress(status, output)
    
    if (status === 'succeeded') return result
    if (status === 'failed' || status === 'canceled') {
      return {
        success: false,
        error: result.data!.error || 'Prediction failed',
      }
    }
    
    await new Promise(resolve => setTimeout(resolve, interval))
    attempts++
  }
  
  return {
    success: false,
    error: 'Prediction timeout',
  }
}
```

---

## 📊 **INTEGRATION COMPLEXITY**

**Complexity:** High

**Dependencies:**
- Replicate API client
- Dynamic UI generation (for model-specific parameters)
- Image display components
- File upload components
- State management (Zustand)
- Polling logic

**Estimated Implementation Time:**
- Service layer: 4-6 hours
- UI components: 6-8 hours
- Dynamic parameter discovery: 3-4 hours
- Testing: 3-4 hours
- **Total: 16-22 hours**

---

## ✅ **CHECKLIST**

### **Service Layer**
- [ ] ReplicateCreatePredictionRequest interface
- [ ] ReplicatePredictionResponse interface
- [ ] createPrediction method
- [ ] getPrediction method
- [ ] listPredictions method
- [ ] cancelPrediction method
- [ ] listModels method
- [ ] getModel method
- [ ] getModelVersion method
- [ ] pollPrediction helper
- [ ] Error handling
- [ ] Rate limit handling

### **UI Components**
- [ ] Model selector with search
- [ ] Dynamic parameter controls
- [ ] Prompt input
- [ ] Negative prompt input
- [ ] Parameter sliders/inputs
- [ ] Image display grid
- [ ] Status indicator
- [ ] Progress display
- [ ] Download buttons
- [ ] Error display
- [ ] Loading states
- [ ] History panel

### **Testing**
- [ ] Test SDXL generation
- [ ] Test SD 1.5 generation
- [ ] Test image-to-image
- [ ] Test inpainting
- [ ] Test upscaling
- [ ] Test error handling
- [ ] Test polling
- [ ] Test model discovery

---

**Status:** Deep dive complete - Ready for implementation  
**Last Updated:** 2025-01-27  
**Next:** Implement service layer and UI components

