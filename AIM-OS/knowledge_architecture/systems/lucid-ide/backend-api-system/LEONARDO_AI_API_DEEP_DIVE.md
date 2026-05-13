---
id: "leonardo_ai_api_deep_dive"
system: "lucid_chat"
component: "api_integration"
level: "T3"
type: "deep_analysis"
title: "Leonardo AI API Deep Dive - Complete Integration Guide"
description: "Comprehensive analysis of Leonardo AI API capabilities, endpoints, parameters, workflows, and integration patterns"
created: "2025-01-27T00:00:00Z"
updated: "2025-01-27T00:00:00Z"
author: "aether"
status: "active"
tags: ["leonardo-ai", "image-generation", "api-integration", "deep-dive"]
---

# Leonardo AI API Deep Dive - Complete Integration Guide

**Purpose:** Comprehensive understanding of Leonardo AI API for proper integration  
**Status:** 🔍 **DEEP ANALYSIS COMPLETE**  
**Official Documentation:** https://docs.leonardo.ai (verify URL)

---

## 🎯 **LEONARDO AI API OVERVIEW**

Leonardo AI provides advanced image generation capabilities:
- **Text-to-Image** - Generate images from text prompts
- **Image-to-Image** - Transform existing images
- **Image Upscaling** - Upscale images
- **Background Removal** - Remove backgrounds
- **Motion** - Generate motion from images
- **3D Texture Generation** - Generate 3D textures
- **Multiple Models** - Various specialized models

**Key Features:**
- High-quality image generation
- Multiple model options
- Advanced editing capabilities
- Async processing
- Webhook support

---

## 🔐 **AUTHENTICATION**

**Method:** Bearer Token (API Key)

**Header:**
```
Authorization: Bearer YOUR_API_KEY
```

**API Key Management:**
- Obtain from: Leonardo AI dashboard
- Store securely in environment variable: `LEONARDO_AI_API_KEY`
- Rate limits: Based on account tier

**Base URL:**
```
https://cloud.leonardo.ai/api/rest/v1
```

---

## 📡 **API ENDPOINTS & CAPABILITIES**

### **1. Generate Image**

**Endpoint:** `POST https://cloud.leonardo.ai/api/rest/v1/generations`

**Purpose:** Generate image from text prompt

**Request Parameters:**

```typescript
interface LeonardoAIGenerateImageRequest {
  // Required
  prompt: string                    // Text prompt
  
  // Optional - Model Selection
  modelId?: string                  // Model ID (e.g., '6bef9f1b-29cb-40c7-b9df-32a51f5de347')
  presetStyle?: string              // Preset style ID
  
  // Optional - Image Parameters
  num_images?: number               // Number of images (1-8, default: 1)
  width?: number                    // Image width (512, 768, 1024)
  height?: number                   // Image height (512, 768, 1024)
  guidance_scale?: number           // Guidance scale (1-20, default: 7)
  num_inference_steps?: number      // Inference steps (10-60, default: 30)
  seed?: number                     // Random seed
  
  // Optional - Advanced
  negative_prompt?: string          // Negative prompt
  init_image_id?: string            // Initial image ID (for image-to-image)
  init_strength?: number             // Init strength (0-1, for image-to-image)
  scheduler?: string                // Scheduler type
  controlnet?: string               // ControlNet model
  controlnet_conditioning_scale?: number // ControlNet scale
  
  // Optional - Other
  prompt_magic?: boolean            // Enable prompt magic
  prompt_magic_version?: string     // Prompt magic version
  prompt_magic_strength?: number    // Prompt magic strength
  photoReal?: boolean               // Enable PhotoReal mode
  photoReal_strength?: number       // PhotoReal strength
  alchemy?: boolean                 // Enable Alchemy
  highContrast?: boolean            // High contrast
  expand_pose?: boolean            // Expand pose
}
```

**Response Structure:**

```typescript
interface LeonardoAIGenerateImageResponse {
  sdGenerationJob: {
    generationId: string
    apiCreditCost: number
  }
}
```

---

### **2. Get Generation Status**

**Endpoint:** `GET https://cloud.leonardo.ai/api/rest/v1/generations/{generationId}`

**Purpose:** Get status of image generation

**Response:**

```typescript
interface LeonardoAIGenerationStatus {
  generations_by_pk: {
    id: string
    status: 'PENDING' | 'COMPLETE' | 'FAILED'
    generated_images: Array<{
      id: string
      url: string
      nsfw: boolean
      seed: number
      inference_steps: number
      guidance_scale: number
      modelId: string
      prompt: string
      negative_prompt: string
    }>
    prompt: string
    negative_prompt: string
    modelId: string
    width: number
    height: number
    seed: number
    num_images: number
    guidance_scale: number
    inference_steps: number
    createdAt: string
    updatedAt: string
  }
}
```

---

### **3. Upscale Image**

**Endpoint:** `POST https://cloud.leonardo.ai/api/rest/v1/upscale`

**Purpose:** Upscale an image

**Request Parameters:**

```typescript
interface LeonardoAIUpscaleRequest {
  imageId: string                   // Required: Image ID to upscale
  upscaleMultiplier?: number        // Upscale multiplier (2 or 4, default: 2)
}
```

---

### **4. Remove Background**

**Endpoint:** `POST https://cloud.leonardo.ai/api/rest/v1/remove-background`

**Purpose:** Remove background from image

**Request Parameters:**

```typescript
interface LeonardoAIRemoveBackgroundRequest {
  imageId: string                   // Required: Image ID
}
```

---

### **5. List Models**

**Endpoint:** `GET https://cloud.leonardo.ai/api/rest/v1/models`

**Purpose:** List available models

**Response:**

```typescript
interface LeonardoAIModelsResponse {
  custom_models: Array<{
    id: string
    name: string
    description: string
    modelType: string
    createdAt: string
  }>
}
```

---

## 🔄 **WORKFLOWS**

### **Workflow 1: Text-to-Image**

1. User enters prompt
2. Select model
3. Configure parameters (size, steps, guidance)
4. Enable PhotoReal/Alchemy (optional)
5. Submit → Poll status → Display images

### **Workflow 2: Image-to-Image**

1. User uploads image
2. Enter prompt
3. Set init strength
4. Configure other parameters
5. Submit → Poll → Display result

### **Workflow 3: Upscale**

1. User selects generated image
2. Select upscale multiplier
3. Submit → Get upscaled image

---

## ⚡ **RATE LIMITS**

**Free Tier:**
- Limited credits per day

**Paid Tier:**
- Higher rate limits
- More credits

---

## 💰 **PRICING**

**Pay-per-use:**
- Credits-based pricing
- Varies by model and resolution

**Note:** Check Leonardo AI pricing page for current rates.

---

## 🎨 **UI COMPONENT REQUIREMENTS**

### **Image Generation Panel**

**Model Selector:**
- Dropdown with available models
- Model info display

**Prompt Input:**
- Large textarea
- Negative prompt input
- Character counter

**Image Parameters:**
- Width/Height selector
- Number of images selector (1-8)
- Guidance scale slider
- Inference steps slider
- Seed input

**Advanced Options:**
- PhotoReal toggle
- Alchemy toggle
- Prompt Magic toggle
- High Contrast toggle

**Generate Button:**
- Show loading state
- Progress indicator

**Results Display:**
- Image grid
- Download buttons
- Upscale buttons
- Remove background buttons

---

## 🔧 **IMPLEMENTATION NOTES**

### **Service Layer Structure**

```typescript
class LeonardoAIService extends BaseAPIService {
  constructor(apiKey?: string) {
    super('leonardo-ai', 'https://cloud.leonardo.ai/api/rest/v1', apiKey)
  }

  async generateImage(request: LeonardoAIGenerateImageRequest): Promise<APIResponse<LeonardoAIGenerateImageResponse>>
  async getGenerationStatus(generationId: string): Promise<APIResponse<LeonardoAIGenerationStatus>>
  async pollGenerationStatus(
    generationId: string,
    onProgress?: (status: string) => void
  ): Promise<APIResponse<LeonardoAIGenerationStatus>>
  async upscaleImage(request: LeonardoAIUpscaleRequest): Promise<APIResponse<any>>
  async removeBackground(imageId: string): Promise<APIResponse<any>>
  async listModels(): Promise<APIResponse<LeonardoAIModelsResponse>>
}
```

---

## 📊 **INTEGRATION COMPLEXITY**

**Complexity:** Medium-High

**Estimated Implementation Time:**
- Service layer: 4-6 hours
- UI components: 6-8 hours
- Image display: 2-3 hours
- Testing: 3-4 hours
- **Total: 15-21 hours**

---

**Status:** Deep dive complete - Ready for implementation  
**Last Updated:** 2025-01-27

