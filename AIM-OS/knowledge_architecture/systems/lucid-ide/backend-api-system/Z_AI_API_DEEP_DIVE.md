---
id: "z_ai_api_deep_dive"
system: "lucid_chat"
component: "api_integration"
level: "T3"
type: "deep_analysis"
title: "Z.ai API Deep Dive - Complete Integration Guide"
description: "Comprehensive analysis of Z.ai (Zhipu AI) API capabilities, endpoints, parameters, workflows, and integration patterns"
created: "2025-01-27T00:00:00Z"
updated: "2025-01-27T00:00:00Z"
author: "aether"
status: "active"
tags: ["z-ai", "zhipu", "llm", "api-integration", "deep-dive"]
---

# Z.ai API Deep Dive - Complete Integration Guide

**Purpose:** Comprehensive understanding of Z.ai API for proper integration  
**Status:** 🔍 **DEEP ANALYSIS COMPLETE**  
**Official Documentation:** https://docs.z.ai

---

## 🎯 **Z.AI API OVERVIEW**

Z.ai (formerly Zhipu AI) provides GLM series models:
- **Chat Completions** - GLM-4.6, GLM-4.5-X, GLM-4.5-AirX
- **Embeddings** - Text embeddings
- **Image Generation** - Image generation capabilities
- **OpenAI-Compatible** - OpenAI API compatibility
- **Multiple Languages** - Chinese and English support

**Key Features:**
- OpenAI-compatible API
- GLM series models
- Chinese language support
- Python and Java SDKs
- Cost-effective pricing

---

## 🔐 **AUTHENTICATION**

**Method:** Bearer Token (API Key)

**Header:**
```
Authorization: Bearer YOUR_API_KEY
```

**API Key Management:**
- Obtain from: https://z.ai/model-api (international) or https://open.bigmodel.cn/ (China)
- Store securely in environment variable: `Z_AI_API_KEY`
- Rate limits: Based on account tier

**Base URL:**
```
https://open.bigmodel.cn/api/paas/v4
```

---

## 📡 **API ENDPOINTS & CAPABILITIES**

### **1. Chat Completions**

**Endpoint:** `POST https://open.bigmodel.cn/api/paas/v4/chat/completions`

**Purpose:** Chat with GLM models (OpenAI-compatible)

**Request Parameters:**

```typescript
interface ZAIChatCompletionRequest {
  // Required
  model: 'glm-4.6' | 'glm-4.5-x' | 'glm-4.5-airx' | 'glm-4' | 'glm-3-turbo' | string
  
  // Required
  messages: Array<{
    role: 'system' | 'user' | 'assistant'
    content: string
  }>
  
  // Optional - Generation Parameters
  temperature?: number              // 0-2 (default: 0.95)
  top_p?: number                    // 0-1 (default: 0.7)
  max_tokens?: number               // Max tokens to generate
  stream?: boolean                  // Stream responses
  stop?: string | string[]          // Stop sequences
  presence_penalty?: number         // -2 to 2
  frequency_penalty?: number        // -2 to 2
  user?: string
  
  // Optional - Function Calling
  tools?: Array<{
    type: 'function'
    function: {
      name: string
      description?: string
      parameters: Record<string, any> // JSON Schema
    }
  }>
  tool_choice?: 'none' | 'auto' | {
    type: 'function'
    function: {
      name: string
    }
  }
  
  // Optional - Response Format
  response_format?: {
    type: 'text' | 'json_object'
  }
}
```

**Available Models:**
- `glm-4.6` - Latest, most capable
- `glm-4.5-x` - High performance
- `glm-4.5-airx` - Fast, efficient
- `glm-4` - Previous generation
- `glm-3-turbo` - Turbo model

**Response Structure:**

```typescript
interface ZAIChatCompletionResponse {
  id: string
  object: 'chat.completion'
  created: number
  model: string
  choices: Array<{
    index: number
    message: {
      role: 'assistant'
      content: string | null
      tool_calls?: Array<{
        id: string
        type: 'function'
        function: {
          name: string
          arguments: string
        }
      }>
    }
    finish_reason: 'stop' | 'length' | 'tool_calls'
  }>
  usage: {
    prompt_tokens: number
    completion_tokens: number
    total_tokens: number
  }
}
```

**Streaming:** Same as OpenAI (SSE format)

---

### **2. Embeddings**

**Endpoint:** `POST https://open.bigmodel.cn/api/paas/v4/embeddings`

**Purpose:** Generate embeddings (OpenAI-compatible)

**Request:**

```typescript
interface ZAIEmbeddingsRequest {
  model: string                     // e.g., 'embedding-2'
  input: string | string[]          // Required
  encoding_format?: 'float' | 'base64'
  dimensions?: number
  user?: string
}
```

**Response:** Same format as OpenAI embeddings

---

### **3. Image Generation**

**Endpoint:** `POST https://open.bigmodel.cn/api/paas/v4/images/generations`

**Purpose:** Generate images

**Request:**

```typescript
interface ZAIImageGenerationRequest {
  prompt: string                    // Required
  model?: string
  n?: number                        // Number of images
  size?: string                     // Image size
  quality?: string
  response_format?: 'url' | 'b64_json'
  user?: string
}
```

---

## 🔄 **WORKFLOWS**

### **Workflow 1: Chat Completion**

1. User enters message
2. Select GLM model
3. Configure parameters
4. Enable streaming (optional)
5. Submit → Stream or wait → Display response

---

## ⚡ **RATE LIMITS**

**Varies by:**
- Account tier
- Model selected

**Check Z.ai dashboard for quotas**

---

## 💰 **PRICING**

**Pay-per-use:**
- Competitive pricing
- Check Z.ai pricing page for current rates

---

## 🎨 **UI COMPONENT REQUIREMENTS**

### **Chat Panel**

**Model Selector:**
- Dropdown with GLM models
- Model info display

**Chat Interface:**
- Message list
- User/assistant messages
- Streaming indicator

**Generation Parameters:**
- Temperature slider
- Max tokens input
- Top P slider

**Streaming Toggle:**
- Enable/disable streaming

---

## 🔧 **IMPLEMENTATION NOTES**

### **Service Layer Structure**

```typescript
class ZAIService extends BaseAPIService {
  constructor(apiKey?: string) {
    super('z-ai', 'https://open.bigmodel.cn/api/paas/v4', apiKey)
  }

  // OpenAI-compatible methods
  async chatCompletion(request: ZAIChatCompletionRequest): Promise<APIResponse<ZAIChatCompletionResponse>>
  async streamChatCompletion(
    request: Omit<ZAIChatCompletionRequest, 'stream'>,
    onChunk: (chunk: ZAIChatCompletionChunk) => void
  ): Promise<APIResponse<void>>
  async createEmbeddings(request: ZAIEmbeddingsRequest): Promise<APIResponse<any>>
  async generateImage(request: ZAIImageGenerationRequest): Promise<APIResponse<any>>
}
```

**OpenAI Compatibility:**

Since Z.ai is OpenAI-compatible, you can use OpenAI SDK:

```typescript
import OpenAI from 'openai'

const client = new OpenAI({
  apiKey: process.env.Z_AI_API_KEY,
  baseURL: 'https://open.bigmodel.cn/api/paas/v4',
})
```

---

## 📊 **INTEGRATION COMPLEXITY**

**Complexity:** Low-Medium (OpenAI-compatible)

**Estimated Implementation Time:**
- Service layer: 2-3 hours (can use OpenAI SDK)
- UI components: 4-5 hours
- Streaming support: 2-3 hours
- Testing: 2-3 hours
- **Total: 10-14 hours**

---

**Status:** Deep dive complete - Ready for implementation  
**Last Updated:** 2025-01-27

