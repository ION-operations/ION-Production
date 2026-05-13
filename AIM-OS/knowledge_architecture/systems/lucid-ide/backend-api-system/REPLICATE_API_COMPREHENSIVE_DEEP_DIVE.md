---
id: "replicate_api_comprehensive_deep_dive"
system: "lucid_chat"
component: "api_integration"
level: "T3"
type: "deep_analysis"
title: "Replicate API Comprehensive Deep Dive - Complete Integration Guide"
description: "Comprehensive analysis of Replicate API covering ALL model types, dynamic discovery, workflows, and integration patterns"
created: "2025-01-27T00:00:00Z"
updated: "2025-01-27T00:00:00Z"
author: "aether"
status: "active"
tags: ["replicate", "ai-models", "api-integration", "deep-dive", "comprehensive"]
---

# Replicate API Comprehensive Deep Dive - Complete Integration Guide

**Purpose:** Comprehensive understanding of Replicate API for ALL model types  
**Status:** 🔍 **DEEP ANALYSIS COMPLETE**  
**Official Documentation:** https://replicate.com/docs  
**OpenAPI Schema:** https://api.replicate.com/openapi.json

---

## 🎯 **REPLICATE API OVERVIEW**

Replicate is a cloud platform providing access to **1000+ AI models** across multiple categories:
- **Image Generation** - Stable Diffusion, SDXL, Flux, Midjourney-style models
- **Image Editing** - Inpainting, outpainting, upscaling, style transfer
- **Video Generation** - Animate, video-to-video, text-to-video
- **Audio** - Music generation, TTS, audio enhancement
- **Text/LLM** - Language models, text generation, embeddings
- **Code** - Code generation, code explanation
- **3D** - 3D model generation, mesh processing
- **Other** - OCR, object detection, pose estimation, etc.

**Key Features:**
- **Universal API** - Same interface for all models
- **Dynamic Model Discovery** - Discover models and their parameters at runtime
- **Async Predictions** - Long-running operations with polling
- **Webhooks** - Get notified when predictions complete
- **Streaming** - Real-time output streaming
- **Versioning** - Model version control
- **Pay-per-use** - Only pay for compute time used

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

**Base URL:**
```
https://api.replicate.com/v1
```

---

## 📡 **CORE API ENDPOINTS**

### **1. Create Prediction**

**Endpoint:** `POST https://api.replicate.com/v1/predictions`

**Purpose:** Run any model prediction

**Request Parameters:**

```typescript
interface ReplicateCreatePredictionRequest {
  // Required
  version: string                  // Model version ID (full hash or owner/model:version)
  
  // Required - Input parameters (completely dynamic, varies by model)
  input: Record<string, any>       // Model-specific input schema
  
  // Optional
  webhook?: string                 // Webhook URL for completion notification
  webhook_events_filter?: Array<'start' | 'output' | 'logs' | 'completed'>
  stream?: boolean                 // Stream output in real-time
}
```

**Model Version Formats:**
- Full hash: `39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b`
- Owner/model:version: `stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b`
- Latest: `stability-ai/sdxl:latest` (uses latest version)

**Response Structure:**

```typescript
interface ReplicatePredictionResponse {
  id: string                      // Prediction ID
  version: string                  // Model version ID
  urls: {
    get: string                   // GET prediction status
    cancel: string                 // Cancel prediction
    stream?: string               // Stream URL (if streaming)
  }
  created_at: string              // ISO 8601 timestamp
  started_at?: string
  completed_at?: string
  status: 'starting' | 'processing' | 'succeeded' | 'failed' | 'canceled'
  input: Record<string, any>      // Input parameters
  output?: any                     // Output (type varies by model)
  error?: string
  logs?: string
  metrics?: {
    predict_time?: number         // Prediction time in seconds
  }
  model?: string                   // Model identifier
  version?: {
    id: string
    created_at: string
    cog_version: string
    openapi_schema: {
      components: {
        schemas: {
          Input: {
            type: 'object'
            properties: Record<string, any>
            required?: string[]
          }
          Output: {
            type: any
          }
        }
      }
    }
  }
}
```

**Workflow:**
1. User selects model
2. Discover model schema (get model version)
3. Generate UI controls from schema
4. User fills parameters
5. Submit prediction → Get prediction ID
6. Poll status → Monitor progress
7. When status = 'succeeded', get output
8. Display result(s)

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
  limit?: number                  // Results per page (default: 100, max: 100)
}
```

**Response:**

```typescript
interface ReplicateListPredictionsResponse {
  previous?: string
  next?: string
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
  limit?: number                  // Default: 100, max: 100
  query?: string                  // Search query
  owner?: string                  // Filter by owner
  visibility?: 'public' | 'private'
  sort?: 'created' | 'updated' | 'trending'
}
```

**Response:**

```typescript
interface ReplicateListModelsResponse {
  previous?: string
  next?: string
  results: Array<{
    url: string                   // Model URL (e.g., 'owner/model-name')
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
      openapi_schema: {
        components: {
          schemas: {
            Input: {
              type: 'object'
              properties: Record<string, any>
              required?: string[]
            }
            Output: {
              type: any
            }
          }
        }
      }
    }
    run_count?: number            // Number of runs
    cover_image_url?: string
    example?: string              // Example prediction URL
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

**Purpose:** Get details about a specific model version (including input/output schema)

**Response:**

```typescript
interface ReplicateModelVersion {
  id: string
  created_at: string
  cog_version: string
  openapi_schema: {
    components: {
      schemas: {
        Input: {
          type: 'object'
          properties: Record<string, any>
          required?: string[]
        }
        Output: {
          type: any
        }
      }
    }
  }
  model?: {
    url: string
    owner: string
    name: string
  }
}
```

**Critical:** This endpoint provides the OpenAPI schema that defines:
- Input parameter types, constraints, defaults
- Output structure
- Required vs optional parameters

---

### **8. List Model Versions**

**Endpoint:** `GET https://api.replicate.com/v1/models/{owner}/{model_name}/versions`

**Purpose:** List all versions of a model

**Response:**

```typescript
interface ReplicateListModelVersionsResponse {
  previous?: string
  next?: string
  results: ReplicateModelVersion[]
}
```

---

## 🔄 **DYNAMIC MODEL DISCOVERY WORKFLOW**

### **Step 1: Discover Models**

```typescript
// List all models or search
const models = await replicateService.listModels({
  query: 'stable diffusion',
  sort: 'trending',
  limit: 50
})
```

### **Step 2: Get Model Schema**

```typescript
// Get latest version schema
const model = await replicateService.getModel('stability-ai', 'sdxl')
const version = model.latest_version!

// Extract input schema
const inputSchema = version.openapi_schema.components.schemas.Input
const properties = inputSchema.properties
const required = inputSchema.required || []
```

### **Step 3: Generate UI Controls**

```typescript
// Dynamically generate UI controls based on schema
function generateUIControls(schema: OpenAPISchema) {
  const controls = []
  
  for (const [key, prop] of Object.entries(schema.properties)) {
    const isRequired = schema.required?.includes(key)
    const control = {
      name: key,
      type: prop.type, // 'string', 'number', 'boolean', 'array', 'object'
      required: isRequired,
      default: prop.default,
      description: prop.description,
      // Handle constraints
      min: prop.minimum,
      max: prop.maximum,
      enum: prop.enum,
      format: prop.format, // 'uri', 'base64', etc.
    }
    controls.push(control)
  }
  
  return controls
}
```

### **Step 4: User Fills Parameters**

User interacts with dynamically generated UI controls.

### **Step 5: Submit Prediction**

```typescript
const prediction = await replicateService.createPrediction({
  version: model.latest_version!.id,
  input: {
    prompt: userInput.prompt,
    num_outputs: userInput.num_outputs,
    // ... all other parameters from UI
  }
})
```

### **Step 6: Poll for Results**

```typescript
const result = await replicateService.pollPrediction(
  prediction.id,
  (status, output) => {
    // Update UI with progress
    updateProgress(status, output)
  }
)
```

---

## 📊 **COMMON MODEL CATEGORIES & PARAMETERS**

### **Image Generation Models**

**Common Parameters:**
- `prompt` (string, required) - Text description
- `negative_prompt` (string, optional) - What to avoid
- `num_outputs` (number, 1-4) - Number of images
- `guidance_scale` (number, 1-20) - How closely to follow prompt
- `num_inference_steps` (number, 1-500) - Denoising steps
- `seed` (number, optional) - Random seed
- `width` (number) - Image width (must be multiple of 8)
- `height` (number) - Image height (must be multiple of 8)
- `scheduler` (string, optional) - Scheduler type
- `safety_tolerance` (number, optional) - NSFW filter strength

**Model Examples:**
- `stability-ai/sdxl` - Stable Diffusion XL
- `stability-ai/stable-diffusion` - SD 1.5
- `black-forest-labs/flux-dev` - Flux model
- `luma/dream-machine` - Dream Machine

### **Image-to-Image Models**

**Additional Parameters:**
- `image` (string, required) - Input image URL or base64
- `prompt_strength` (number, 0-1) - How much to change image
- `image_prompt` (string, optional) - Prompt for transformation

### **Inpainting Models**

**Additional Parameters:**
- `image` (string, required) - Input image
- `mask` (string, required) - Mask image
- `prompt` (string, required) - What to paint

### **Upscaling Models**

**Additional Parameters:**
- `image` (string, required) - Image to upscale
- `scale` (number, optional) - Upscale factor
- `face_enhance` (boolean, optional) - Enhance faces

### **Video Generation Models**

**Common Parameters:**
- `prompt` (string, required) - Video description
- `image` (string, optional) - Starting image
- `duration` (number, optional) - Video duration in seconds
- `fps` (number, optional) - Frames per second
- `motion_bucket_id` (number, optional) - Motion intensity

**Model Examples:**
- `anotherjesse/zeroscope-v2-xl` - Video generation
- `stability-ai/stable-video-diffusion` - SVD

### **Audio Models**

**Common Parameters:**
- `prompt` (string, required) - Audio description
- `duration` (number, optional) - Duration in seconds
- `model_version` (string, optional) - Model version

**Model Examples:**
- `meta/musicgen` - Music generation
- `openai/whisper` - Speech recognition

### **Text/LLM Models**

**Common Parameters:**
- `prompt` (string, required) - Text prompt
- `max_length` (number, optional) - Max tokens
- `temperature` (number, 0-1) - Randomness
- `top_p` (number, 0-1) - Nucleus sampling
- `system_prompt` (string, optional) - System message

**Model Examples:**
- `meta/llama-2-70b-chat` - Llama 2
- `mistralai/mixtral-8x7b-instruct-v0.1` - Mixtral

---

## 🔄 **POLLING STRATEGY**

```typescript
async pollPrediction(
  predictionId: string,
  onProgress?: (status: string, output?: any, logs?: string) => void,
  interval: number = 2000,
  maxAttempts: number = 300 // 10 minutes max
): Promise<APIResponse<ReplicatePredictionResponse>> {
  let attempts = 0
  
  while (attempts < maxAttempts) {
    const result = await this.getPrediction(predictionId)
    
    if (!result.success || !result.data) {
      return result
    }
    
    const { status, output, logs } = result.data
    
    // Call progress callback
    if (onProgress) {
      onProgress(status, output, logs)
    }
    
    // Check completion
    if (status === 'succeeded') {
      return result
    }
    
    if (status === 'failed' || status === 'canceled') {
      return {
        success: false,
        error: result.data.error || 'Prediction failed',
        metadata: result.metadata,
      }
    }
    
    // Wait before next poll
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

## 🎨 **UI COMPONENT REQUIREMENTS**

### **Model Browser Panel**

**Search/Filter:**
- Search input
- Category filter (Image, Video, Audio, Text, etc.)
- Owner filter
- Sort options (trending, created, updated)
- Pagination

**Model Cards:**
- Model name and owner
- Description
- Cover image
- Run count
- Latest version badge
- Example output preview
- "Use Model" button

### **Model Details Panel**

**Model Info:**
- Full description
- Owner info
- GitHub/Paper links
- License info
- Example inputs/outputs

**Version Selector:**
- List all versions
- Show version dates
- Select version

**Schema Viewer:**
- Input schema display
- Output schema display
- Parameter descriptions

### **Dynamic Parameter Panel**

**Auto-Generated Controls:**
- Text inputs (for strings)
- Number inputs (for numbers, with min/max)
- Sliders (for ranges)
- Dropdowns (for enums)
- Checkboxes (for booleans)
- File uploads (for image/file inputs)
- JSON editors (for objects/arrays)

**Parameter Groups:**
- Required parameters (highlighted)
- Optional parameters (collapsible)
- Advanced parameters (collapsible)

**Validation:**
- Real-time validation
- Show errors
- Format hints (e.g., "Must be multiple of 8")

### **Prediction Panel**

**Status Display:**
- Status badge
- Progress indicator
- Logs display (if available)
- Time elapsed

**Output Display:**
- Images: Grid view
- Videos: Video player
- Audio: Audio player
- Text: Text display
- JSON: JSON viewer
- Files: Download buttons

**Actions:**
- Cancel prediction
- Download output
- Share prediction
- Create variation

---

## 🔧 **IMPLEMENTATION NOTES**

### **Service Layer Structure**

```typescript
class ReplicateService extends BaseAPIService {
  constructor(apiToken?: string) {
    super('replicate', 'https://api.replicate.com/v1', apiToken)
  }

  // Core endpoints
  async createPrediction(request: ReplicateCreatePredictionRequest): Promise<APIResponse<ReplicatePredictionResponse>>
  async getPrediction(predictionId: string): Promise<APIResponse<ReplicatePredictionResponse>>
  async listPredictions(query?: ReplicateListPredictionsQuery): Promise<APIResponse<ReplicateListPredictionsResponse>>
  async cancelPrediction(predictionId: string): Promise<APIResponse<ReplicatePredictionResponse>>
  
  // Model discovery
  async listModels(query?: ReplicateListModelsQuery): Promise<APIResponse<ReplicateListModelsResponse>>
  async getModel(owner: string, modelName: string): Promise<APIResponse<ReplicateModel>>
  async getModelVersion(owner: string, modelName: string, versionId: string): Promise<APIResponse<ReplicateModelVersion>>
  async listModelVersions(owner: string, modelName: string): Promise<APIResponse<ReplicateListModelVersionsResponse>>
  
  // Helpers
  async pollPrediction(
    predictionId: string,
    onProgress?: (status: string, output?: any, logs?: string) => void
  ): Promise<APIResponse<ReplicatePredictionResponse>>
  
  async searchModels(query: string, category?: string): Promise<APIResponse<ReplicateModel[]>>
  
  // Schema utilities
  parseInputSchema(version: ReplicateModelVersion): InputSchema
  generateUIControls(schema: InputSchema): UIControl[]
  validateInput(input: Record<string, any>, schema: InputSchema): ValidationResult
}
```

### **Dynamic Schema Parsing**

```typescript
interface InputSchema {
  properties: Record<string, ParameterDefinition>
  required: string[]
}

interface ParameterDefinition {
  type: 'string' | 'number' | 'boolean' | 'array' | 'object'
  description?: string
  default?: any
  minimum?: number
  maximum?: number
  enum?: any[]
  format?: string
  items?: ParameterDefinition // For arrays
  properties?: Record<string, ParameterDefinition> // For objects
}

function parseInputSchema(version: ReplicateModelVersion): InputSchema {
  const openapiSchema = version.openapi_schema
  const inputSchema = openapiSchema.components.schemas.Input
  
  return {
    properties: inputSchema.properties || {},
    required: inputSchema.required || [],
  }
}
```

### **State Management**

```typescript
interface ReplicateState {
  // Model Discovery
  availableModels: ReplicateModel[]
  selectedModel: ReplicateModel | null
  selectedVersion: ReplicateModelVersion | null
  modelSchema: InputSchema | null
  
  // Search/Filter
  searchQuery: string
  categoryFilter: string | null
  sortBy: 'trending' | 'created' | 'updated'
  
  // Current Prediction
  currentPrediction: ReplicatePredictionResponse | null
  predictionInput: Record<string, any>
  isGenerating: boolean
  status: string
  progress: number
  
  // Results
  output: any
  logs: string
  error: string | null
  
  // History
  predictions: ReplicatePredictionResponse[]
}
```

---

## ⚡ **RATE LIMITS**

**Free Tier:**
- Limited predictions per month
- Lower rate limits

**Paid Tier:**
- Higher rate limits
- Pay-per-use pricing

**Rate Limit Handling:**
- Implement exponential backoff
- Track usage
- Show usage counter

---

## 💰 **PRICING**

**Pay-per-use:**
- Each prediction costs based on:
  - Model used
  - Compute time
  - Output size

**Example Pricing (varies by model):**
- SDXL: ~$0.003-0.01 per image
- Video generation: ~$0.05-0.20 per second
- LLM inference: ~$0.0001-0.001 per token

**Note:** Check Replicate pricing page for current rates.

---

## 📊 **INTEGRATION COMPLEXITY**

**Complexity:** Very High

**Dependencies:**
- Replicate API client
- Dynamic UI generation system
- Schema parser
- Multiple output type handlers (images, videos, audio, text, JSON)
- Polling system
- State management (Zustand)

**Estimated Implementation Time:**
- Service layer: 8-10 hours
- Dynamic UI generation: 12-16 hours
- Model browser: 6-8 hours
- Output handlers: 8-10 hours
- Testing: 6-8 hours
- **Total: 40-52 hours**

---

## ✅ **CHECKLIST**

### **Service Layer**
- [ ] All core endpoints implemented
- [ ] Model discovery endpoints
- [ ] Schema parsing utilities
- [ ] Polling system
- [ ] Error handling
- [ ] Rate limit handling

### **UI Components**
- [ ] Model browser with search/filter
- [ ] Model details panel
- [ ] Dynamic parameter generator
- [ ] Parameter input controls (all types)
- [ ] Prediction status display
- [ ] Output handlers (images, videos, audio, text, JSON)
- [ ] Logs display
- [ ] History panel

### **Testing**
- [ ] Test model discovery
- [ ] Test schema parsing
- [ ] Test dynamic UI generation
- [ ] Test image generation models
- [ ] Test video generation models
- [ ] Test audio models
- [ ] Test text/LLM models
- [ ] Test polling
- [ ] Test error handling

---

**Status:** Deep dive complete - Ready for implementation  
**Last Updated:** 2025-01-27  
**Next:** Implement service layer and dynamic UI generation system

