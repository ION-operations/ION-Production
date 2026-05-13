---
id: "cloudinary_api_deep_dive"
system: "lucid_chat"
component: "api_integration"
level: "T3"
type: "deep_analysis"
title: "Cloudinary API Deep Dive - Complete Integration Guide"
description: "Comprehensive analysis of Cloudinary API capabilities, endpoints, parameters, workflows, and integration patterns"
created: "2025-01-27T00:00:00Z"
updated: "2025-01-27T00:00:00Z"
author: "aether"
status: "active"
tags: ["cloudinary", "media-management", "image-video", "api-integration", "deep-dive"]
---

# Cloudinary API Deep Dive - Complete Integration Guide

**Purpose:** Comprehensive understanding of Cloudinary API for proper integration  
**Status:** 🔍 **DEEP ANALYSIS COMPLETE**  
**Official Documentation:** https://cloudinary.com/documentation

---

## 🎯 **CLOUDINARY API OVERVIEW**

Cloudinary provides comprehensive media management:
- **Upload** - Upload images, videos, and other media
- **Transformations** - On-the-fly image/video transformations
- **Optimization** - Automatic optimization and format conversion
- **Delivery** - Global CDN delivery
- **Management** - Media library management
- **AI Features** - AI-powered features (background removal, etc.)

**Key Features:**
- Upload API
- Transformation API (URL-based)
- Admin API (management)
- Search API
- AI features
- Video API

---

## 🔐 **AUTHENTICATION**

**Method:** API Key + API Secret (for Admin API) or Signed URLs

**Admin API Authentication:**
```
api_key: YOUR_API_KEY
api_secret: YOUR_API_SECRET
```

**Upload API:**
```
Signature-based authentication
```

**Credentials Management:**
- Obtain from: Cloudinary dashboard
- Store securely in environment variables:
  - `CLOUDINARY_CLOUD_NAME`
  - `CLOUDINARY_API_KEY`
  - `CLOUDINARY_API_SECRET`
- Rate limits: Based on account tier

**Base URLs:**
```
Upload: https://api.cloudinary.com/v1_1/{cloud_name}/image/upload
Admin: https://api.cloudinary.com/v1_1/{cloud_name}/resources
```

---

## 📡 **API ENDPOINTS & CAPABILITIES**

### **1. Upload Image**

**Endpoint:** `POST https://api.cloudinary.com/v1_1/{cloud_name}/image/upload`

**Purpose:** Upload an image

**Request Parameters:**

```typescript
interface CloudinaryUploadRequest {
  // Required
  file: File | string                // File or data URI
  
  // Optional - Upload Parameters
  public_id?: string                 // Public ID (default: auto-generated)
  folder?: string                    // Folder path
  resource_type?: 'image' | 'video' | 'raw' | 'auto'
  type?: 'upload' | 'private' | 'authenticated'
  overwrite?: boolean                // Overwrite existing (default: false)
  invalidate?: boolean               // Invalidate CDN cache (default: false)
  
  // Optional - Transformation Parameters
  transformation?: string            // Transformation string (e.g., 'w_500,h_500,c_fill')
  format?: string                    // Format (e.g., 'jpg', 'png', 'webp', 'auto')
  quality?: string | number          // Quality ('auto', 'auto:good', 'auto:best', or 1-100)
  
  // Optional - Tags and Metadata
  tags?: string[]                    // Tags
  context?: Record<string, string>   // Context metadata
  metadata?: Record<string, string>  // Custom metadata
  
  // Optional - Eager Transformations
  eager?: string                     // Eager transformations (e.g., 'w_500,h_500')
  eager_async?: boolean              // Async eager transformations
  
  // Optional - Other
  use_filename?: boolean             // Use original filename (default: false)
  unique_filename?: boolean          // Unique filename (default: true)
  discard_original_filename?: boolean // Discard original filename
  notification_url?: string          // Webhook URL
  eager_notification_url?: string    // Eager webhook URL
}
```

**Response Structure:**

```typescript
interface CloudinaryUploadResponse {
  public_id: string
  version: number
  signature: string
  width: number
  height: number
  format: string
  resource_type: 'image' | 'video' | 'raw'
  created_at: string
  tags: string[]
  bytes: number
  type: string
  etag: string
  placeholder: boolean
  url: string                      // Delivery URL
  secure_url: string               // HTTPS URL
  access_mode: string
  context?: Record<string, any>
  metadata?: Record<string, any>
  eager?: Array<{
    transformation: string
    width: number
    height: number
    bytes: number
    format: string
    url: string
    secure_url: string
  }>
}
```

---

### **2. Transform Image (URL-based)**

**Purpose:** Transform images via URL parameters

**URL Format:**
```
https://res.cloudinary.com/{cloud_name}/image/upload/{transformations}/{public_id}.{format}
```

**Transformation Parameters:**

```typescript
interface CloudinaryTransformation {
  // Size
  w?: number                        // Width
  h?: number                        // Height
  c?: 'scale' | 'fit' | 'fill' | 'crop' | 'thumb' | 'pad'  // Crop mode
  g?: 'face' | 'auto' | 'center' | 'north' | 'south' | 'east' | 'west' | 'north_east' | 'north_west' | 'south_east' | 'south_west'  // Gravity
  x?: number                        // X offset
  y?: number                        // Y offset
  
  // Quality
  q?: number | 'auto' | 'auto:good' | 'auto:best'  // Quality
  f?: string                        // Format (auto, jpg, png, webp, etc.)
  
  // Effects
  e?: string                        // Effect (e.g., 'blur:300', 'brightness:20')
  b?: string                        // Background color
  o?: number                        // Opacity
  r?: number                        // Rotate
  a?: number                        // Angle
  
  // Text Overlay
  l?: string                        // Text overlay
  fl?: string                       // Text flags
  
  // Other
  dpr?: number                      // Device pixel ratio
  ar?: string                       // Aspect ratio
  z?: number                        // Zoom
}
```

**Example URL:**
```
https://res.cloudinary.com/demo/image/upload/w_500,h_500,c_fill,q_auto,f_auto/sample.jpg
```

---

### **3. Admin API - List Resources**

**Endpoint:** `GET https://api.cloudinary.com/v1_1/{cloud_name}/resources/{resource_type}`

**Purpose:** List uploaded resources

**Query Parameters:**

```typescript
interface CloudinaryListResourcesRequest {
  resource_type?: 'image' | 'video' | 'raw' | 'auto'
  type?: 'upload' | 'private' | 'authenticated'
  prefix?: string                   // Prefix filter
  tags?: boolean                    // Include tags
  context?: boolean                 // Include context
  max_results?: number              // Max results (default: 10, max: 500)
  next_cursor?: string              // Pagination cursor
}
```

**Response:**

```typescript
interface CloudinaryListResourcesResponse {
  resources: CloudinaryUploadResponse[]
  next_cursor?: string
  total_count?: number
}
```

---

### **4. Admin API - Get Resource**

**Endpoint:** `GET https://api.cloudinary.com/v1_1/{cloud_name}/resources/{resource_type}/{type}/{public_id}`

**Purpose:** Get resource details

**Response:** CloudinaryUploadResponse

---

### **5. Admin API - Delete Resource**

**Endpoint:** `DELETE https://api.cloudinary.com/v1_1/{cloud_name}/resources/{resource_type}/{type}/{public_id}`

**Purpose:** Delete a resource

**Response:**

```typescript
interface CloudinaryDeleteResponse {
  result: 'ok' | 'not found'
}
```

---

### **6. Search API**

**Endpoint:** `POST https://api.cloudinary.com/v1_1/{cloud_name}/resources/search`

**Purpose:** Search resources

**Request Body:**

```typescript
interface CloudinarySearchRequest {
  expression?: string               // Search expression
  max_results?: number             // Max results
  next_cursor?: string             // Pagination cursor
  sort_by?: Array<{
    [field: string]: 'asc' | 'desc'
  }>
  aggregate?: string[]              // Aggregations
  with_field?: string[]            // Include fields
}
```

---

## 🔄 **WORKFLOWS**

### **Workflow 1: Upload and Transform**

1. User uploads image
2. Configure upload options (folder, tags, etc.)
3. Set eager transformations (optional)
4. Upload → Get URL
5. Display image with transformations

### **Workflow 2: On-the-Fly Transformation**

1. User selects image
2. Configure transformations (size, crop, effects)
3. Generate transformation URL
4. Display transformed image

### **Workflow 3: Media Library**

1. List resources
2. Search/filter resources
3. View resource details
4. Delete resources
5. Apply transformations

---

## ⚡ **RATE LIMITS**

**Free Tier:**
- 25GB storage
- 25GB bandwidth/month
- Limited transformations

**Paid Tier:**
- Higher limits
- More features

---

## 💰 **PRICING**

**Free Tier:**
- 25GB storage
- 25GB bandwidth/month
- Free forever

**Paid Tier:**
- Pay-as-you-go
- Higher limits

---

## 🎨 **UI COMPONENT REQUIREMENTS**

### **Upload Panel**

**File Upload:**
- Drag-and-drop area
- File input
- Multiple file support
- Progress indicator

**Upload Options:**
- Folder selector
- Tags input
- Public ID input
- Format selector
- Quality selector

**Eager Transformations:**
- Transformation builder
- Preview transformations

**Upload Button:**
- Show loading state
- Progress indicator

### **Transformation Panel**

**Transformation Controls:**
- Width/Height inputs
- Crop mode selector
- Gravity selector
- Quality slider
- Format selector
- Effects panel
- Text overlay panel

**Preview:**
- Before/after comparison
- Transformation URL display

### **Media Library Panel**

**Resource List:**
- Grid/list view
- Thumbnail display
- Resource info
- Actions (view, delete, transform)

**Search/Filter:**
- Search input
- Tag filter
- Folder filter
- Sort options

---

## 🔧 **IMPLEMENTATION NOTES**

### **Service Layer Structure**

```typescript
class CloudinaryService extends BaseAPIService {
  constructor(cloudName?: string, apiKey?: string, apiSecret?: string) {
    super('cloudinary', `https://api.cloudinary.com/v1_1/${cloudName}`, apiKey)
    this.cloudName = cloudName
    this.apiSecret = apiSecret
  }

  async uploadImage(request: CloudinaryUploadRequest): Promise<APIResponse<CloudinaryUploadResponse>>
  async uploadVideo(request: CloudinaryUploadRequest): Promise<APIResponse<CloudinaryUploadResponse>>
  async listResources(request?: CloudinaryListResourcesRequest): Promise<APIResponse<CloudinaryListResourcesResponse>>
  async getResource(publicId: string, resourceType?: string): Promise<APIResponse<CloudinaryUploadResponse>>
  async deleteResource(publicId: string, resourceType?: string): Promise<APIResponse<CloudinaryDeleteResponse>>
  async searchResources(request: CloudinarySearchRequest): Promise<APIResponse<any>>
  
  // Helpers
  generateTransformationURL(publicId: string, transformations: CloudinaryTransformation, format?: string): string
  generateSignedUploadParams(params: Record<string, any>): Record<string, any>
}
```

---

## 📊 **INTEGRATION COMPLEXITY**

**Complexity:** High

**Dependencies:**
- File upload handling
- Image/video processing
- Transformation URL builder
- Media library UI

**Estimated Implementation Time:**
- Service layer: 6-8 hours
- Upload UI: 4-6 hours
- Transformation builder: 6-8 hours
- Media library: 6-8 hours
- Testing: 4-6 hours
- **Total: 26-36 hours**

---

**Status:** Deep dive complete - Ready for implementation  
**Last Updated:** 2025-01-27

