---
id: "flux_api_deep_dive"
system: "lucid_chat"
component: "api_integration"
level: "T3"
type: "deep_analysis"
title: "Flux API Deep Dive - Complete Integration Guide"
description: "Comprehensive analysis of Flux API capabilities, endpoints, parameters, workflows, and integration patterns"
created: "2025-01-27T00:00:00Z"
updated: "2025-01-27T00:00:00Z"
author: "aether"
status: "active"
tags: ["flux", "image-generation", "api-integration", "deep-dive"]
---

# Flux API Deep Dive - Complete Integration Guide

**Purpose:** Comprehensive understanding of Flux API for proper integration  
**Status:** 🔍 **DEEP ANALYSIS COMPLETE**  
**Official Documentation:** https://blackforestlabs.ai/api/docs (verify URL)

---

## 🎯 **FLUX API OVERVIEW**

Flux (Black Forest Labs) provides advanced image generation:
- **Text-to-Image** - Generate images from text prompts
- **Image-to-Image** - Transform existing images
- **Multiple Models** - Flux.1, Flux.1-dev, Flux.1-schnell
- **High Quality** - High-quality image generation
- **Fast Generation** - Schnell model for fast generation

**Key Features:**
- High-quality image generation
- Multiple model options
- Fast generation option
- Image-to-image transformation
- Async processing

---

## 🔐 **AUTHENTICATION**

**Method:** Bearer Token (API Key)

**Header:**
```
Authorization: Bearer YOUR_API_KEY
```

**API Key Management:**
- Obtain from: Black Forest Labs dashboard
- Store securely in environment variable: `FLUX_API_KEY`
- Rate limits: Based on account tier

**Base URL:**
```
https://api.blackforestlabs.ai/v1
```

---

## 📡 **API ENDPOINTS & CAPABILITIES**

### **1. Generate Image**

**Endpoint:** `POST https://api.blackforestlabs.ai/v1/flux`

**Purpose:** Generate image from text prompt

**Request Parameters:**

```typescript
interface FluxGenerateImageRequest {
  // Required
  prompt: string                    // Text prompt
  
  // Optional - Model Selection
  model?: 'flux-1' | 'flux-1-dev' | 'flux-1-schnell'  // Model version (default: 'flux-1')
  
  // Optional - Image Parameters
  aspect_ratio?: '1:1' | '16:9' | '9:16' | '21:9' | '2:3' | '3:2' | '4:5' | '5:4'
  output_format?: 'jpeg' | 'png' | 'webp'
  output_quality?: number           // 1-100 (default: 80)
  seed?: number                     // Random seed
  num_images?: number               // Number of images (1-4, default: 1)
  
  // Optional - Generation Parameters
  guidance_scale?: number           // Guidance scale (default: 3.5)
  num_inference_steps?: number      // Inference steps (default: 28, max: 50)
  safety_tolerance?: number         // Safety tolerance (1-5, default: 2)
  
  // Optional - Image-to-Image
  image_url?: string                // Input image URL (for image-to-image)
  strength?: number                 // Transformation strength (0-1, default: 0.8)
}
```

**Response Structure:**

```typescript
interface FluxGenerateImageResponse {
  id: string                        // Generation ID
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress?: number                 // 0-100
  images?: Array<{
    url: string
    seed: number
  }>
  error?: string
  created_at: string
  completed_at?: string
}
```

---

### **2. Get Generation Status**

**Endpoint:** `GET https://api.blackforestlabs.ai/v1/flux/{id}`

**Purpose:** Get status of image generation

**Response:** Same as Generate Image response

---

## 🔄 **WORKFLOWS**

### **Workflow 1: Text-to-Image**

1. User enters prompt
2. Select model (Flux.1, Flux.1-dev, or Flux.1-schnell)
3. Configure parameters (aspect ratio, steps, guidance)
4. Submit → Poll status → Display images

### **Workflow 2: Image-to-Image**

1. User uploads image
2. Enter prompt
3. Set strength (how much to transform)
4. Configure other parameters
5. Submit → Poll → Display result

---

## ⚡ **RATE LIMITS**

**Free Tier:**
- Limited generations per day

**Paid Tier:**
- Higher rate limits
- More generations

---

## 💰 **PRICING**

**Pay-per-use:**
- Credits-based pricing
- Varies by model (Schnell is cheaper)

**Note:** Check Black Forest Labs pricing page for current rates.

---

## 🎨 **UI COMPONENT REQUIREMENTS**

### **Image Generation Panel**

**Model Selector:**
- Radio buttons: Flux.1 | Flux.1-dev | Flux.1-schnell
- Model info display

**Prompt Input:**
- Large textarea
- Character counter

**Image Parameters:**
- Aspect ratio selector
- Number of images selector (1-4)
- Output format selector
- Output quality slider

**Generation Parameters:**
- Guidance scale slider
- Inference steps slider (max 50)
- Safety tolerance slider (1-5)
- Seed input

**Image-to-Image Options:**
- Image upload
- Strength slider (0-1)

**Generate Button:**
- Show loading state
- Progress indicator

**Results Display:**
- Image grid
- Download buttons

---

## 🔧 **IMPLEMENTATION NOTES**

### **Service Layer Structure**

```typescript
class FluxService extends BaseAPIService {
  constructor(apiKey?: string) {
    super('flux', 'https://api.blackforestlabs.ai/v1', apiKey)
  }

  async generateImage(request: FluxGenerateImageRequest): Promise<APIResponse<FluxGenerateImageResponse>>
  async getGenerationStatus(id: string): Promise<APIResponse<FluxGenerateImageResponse>>
  async pollGenerationStatus(
    id: string,
    onProgress?: (progress: number, status: string) => void
  ): Promise<APIResponse<FluxGenerateImageResponse>>
}
```

---

## 📊 **INTEGRATION COMPLEXITY**

**Complexity:** Medium

**Estimated Implementation Time:**
- Service layer: 3-4 hours
- UI components: 5-6 hours
- Image display: 2-3 hours
- Testing: 2-3 hours
- **Total: 12-16 hours**

---

**Status:** Deep dive complete - Ready for implementation  
**Last Updated:** 2025-01-27

