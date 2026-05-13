---
id: "runway_ml_api_deep_dive"
system: "lucid_chat"
component: "api_integration"
level: "T3"
type: "deep_analysis"
title: "Runway ML API Deep Dive - Complete Integration Guide"
description: "Comprehensive analysis of Runway ML API capabilities, endpoints, parameters, workflows, and integration patterns"
created: "2025-01-27T00:00:00Z"
updated: "2025-01-27T00:00:00Z"
author: "aether"
status: "active"
tags: ["runway", "video-generation", "api-integration", "deep-dive"]
---

# Runway ML API Deep Dive - Complete Integration Guide

**Purpose:** Comprehensive understanding of Runway ML API for proper integration  
**Status:** 🔍 **DEEP ANALYSIS COMPLETE**  
**Official Documentation:** https://docs.runwayml.com (verify URL)

---

## 🎯 **RUNWAY ML API OVERVIEW**

Runway ML provides advanced AI video generation and editing capabilities:
- **Gen-2** - Text-to-video generation
- **Gen-3** - Latest video generation model
- **Image-to-Video** - Convert images to videos
- **Video-to-Video** - Transform existing videos
- **Inpainting** - Edit specific parts of videos
- **Motion Brush** - Add motion to specific areas
- **Frame Interpolation** - Increase frame rate
- **Video Editing** - Various video editing tools

**Key Features:**
- High-quality video generation
- Multiple video models
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
- Obtain from: Runway ML dashboard
- Store securely in environment variable: `RUNWAY_API_KEY`
- Rate limits: Based on account tier

**Base URL:**
```
https://api.runwayml.com/v1
```

---

## 📡 **API ENDPOINTS & CAPABILITIES**

### **1. Generate Video**

**Endpoint:** `POST https://api.runwayml.com/v1/generate`

**Purpose:** Generate video from text or image

**Request Parameters:**

```typescript
interface RunwayGenerateVideoRequest {
  // Required
  model: 'gen-2' | 'gen-3' | string  // Model version
  
  // Required - Text-to-Video
  prompt: string                      // Video description
  
  // Optional - Image-to-Video
  image?: string                       // Input image URL or base64
  
  // Optional - Video Parameters
  duration?: number                    // Video duration in seconds (3-10)
  aspect_ratio?: '16:9' | '9:16' | '1:1' | '4:3' | '3:4'
  resolution?: '1280x768' | '768x1280' | '1024x1024' | '1280x720' | '720x1280'
  fps?: number                        // Frames per second (24, 30, 60)
  seed?: number                       // Random seed
  
  // Optional - Advanced
  motion_bucket_id?: number          // Motion intensity (1-255)
  watermark?: boolean                 // Add watermark (default: false)
  extend?: number                     // Extend video duration
  
  // Optional - Webhook
  webhook_url?: string                // Webhook for completion
}
```

**Response Structure:**

```typescript
interface RunwayGenerateVideoResponse {
  id: string                          // Task ID
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress?: number                   // 0-100
  video_url?: string                  // Video URL when completed
  thumbnail_url?: string              // Thumbnail URL
  error?: string
  created_at: string
  completed_at?: string
}
```

**Workflow:**
1. User enters prompt (and/or uploads image)
2. Configure video parameters
3. Submit → Get task ID
4. Poll status → Monitor progress
5. When status = 'completed', get video URL
6. Display video player

---

### **2. Get Task Status**

**Endpoint:** `GET https://api.runwayml.com/v1/tasks/{task_id}`

**Purpose:** Get status of a video generation task

**Response:** Same as Generate Video response

---

### **3. Video Editing Endpoints**

**Endpoint:** `POST https://api.runwayml.com/v1/edit`

**Purpose:** Edit existing videos

**Request Parameters:**

```typescript
interface RunwayEditVideoRequest {
  // Required
  video_url: string                   // Input video URL
  
  // Required - Edit Type
  edit_type: 'inpaint' | 'motion_brush' | 'extend' | 'interpolate'
  
  // Inpainting Parameters
  mask?: string                       // Mask image URL or base64
  prompt?: string                     // Edit description
  
  // Motion Brush Parameters
  brush_strokes?: Array<{
    x: number
    y: number
    frame: number
    direction?: number
  }>
  
  // Frame Interpolation Parameters
  target_fps?: number                 // Target FPS
  
  // Other Parameters
  seed?: number
}
```

---

## 🔄 **WORKFLOWS**

### **Workflow 1: Text-to-Video**

1. User enters prompt
2. Select model (Gen-2 or Gen-3)
3. Configure parameters (duration, aspect ratio, resolution, fps)
4. Set motion intensity
5. Submit → Poll → Display video

### **Workflow 2: Image-to-Video**

1. User uploads image
2. Enter prompt (optional)
3. Configure parameters
4. Submit → Poll → Display video

### **Workflow 3: Video Editing**

1. User uploads video
2. Select edit type (inpaint, motion brush, etc.)
3. Configure edit parameters
4. Submit → Poll → Display edited video

---

## ⚡ **RATE LIMITS**

**Free Tier:**
- Limited credits per month
- Lower rate limits

**Paid Tier:**
- Higher rate limits
- Pay-per-use pricing

---

## 💰 **PRICING**

**Pay-per-use:**
- Gen-2: ~$0.05 per second of video
- Gen-3: ~$0.10-0.20 per second of video
- Editing: Varies by operation

**Note:** Check Runway ML pricing page for current rates.

---

## 🎨 **UI COMPONENT REQUIREMENTS**

### **Video Generation Panel**

**Model Selector:**
- Dropdown: Gen-2 | Gen-3
- Show model capabilities

**Prompt Input:**
- Large textarea
- Character counter
- Examples

**Image Upload (Optional):**
- Drag-and-drop area
- Image preview
- For image-to-video

**Video Parameters:**
- Duration slider (3-10 seconds)
- Aspect ratio selector
- Resolution selector
- FPS selector
- Motion intensity slider (1-255)
- Seed input

**Generate Button:**
- Show loading state
- Progress indicator

**Video Player:**
- Video playback
- Download button
- Share button

---

## 🔧 **IMPLEMENTATION NOTES**

### **Service Layer Structure**

```typescript
class RunwayMLService extends BaseAPIService {
  constructor(apiKey?: string) {
    super('runway', 'https://api.runwayml.com/v1', apiKey)
  }

  async generateVideo(request: RunwayGenerateVideoRequest): Promise<APIResponse<RunwayGenerateVideoResponse>>
  async getTaskStatus(taskId: string): Promise<APIResponse<RunwayGenerateVideoResponse>>
  async editVideo(request: RunwayEditVideoRequest): Promise<APIResponse<RunwayGenerateVideoResponse>>
  async pollTaskStatus(
    taskId: string,
    onProgress?: (progress: number, status: string) => void
  ): Promise<APIResponse<RunwayGenerateVideoResponse>>
}
```

---

## 📊 **INTEGRATION COMPLEXITY**

**Complexity:** High

**Estimated Implementation Time:**
- Service layer: 4-6 hours
- UI components: 6-8 hours
- Video player: 2-3 hours
- Testing: 3-4 hours
- **Total: 15-21 hours**

---

**Status:** Deep dive complete - Ready for implementation  
**Last Updated:** 2025-01-27

