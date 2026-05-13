---
id: "openrouter_api_deep_dive"
system: "lucid_chat"
component: "api_integration"
level: "T3"
type: "deep_analysis"
title: "OpenRouter API Deep Dive - Complete Integration Guide"
description: "Comprehensive analysis of OpenRouter API capabilities - unified access to 100+ LLM models"
created: "2025-01-27T00:00:00Z"
updated: "2025-01-27T00:00:00Z"
author: "aether"
status: "active"
tags: ["openrouter", "llm", "unified-api", "api-integration", "deep-dive"]
---

# OpenRouter API Deep Dive - Complete Integration Guide

**Purpose:** Comprehensive understanding of OpenRouter API for proper integration  
**Status:** 🔍 **DEEP ANALYSIS COMPLETE**  
**Official Documentation:** https://openrouter.ai/docs

---

## 🎯 **OPENROUTER API OVERVIEW**

OpenRouter provides unified access to 100+ LLM models:
- **Chat Completions** - Access to 100+ models from various providers
- **Unified API** - Single API for all models
- **Model Routing** - Automatic model selection
- **Fallback** - Automatic fallback to alternative models
- **Cost Tracking** - Track costs across providers
- **OpenAI-Compatible** - OpenAI API compatibility

**Key Features:**
- 100+ models from multiple providers
- Unified API interface
- Automatic fallback
- Cost tracking
- Free tier available

---

## 🔐 **AUTHENTICATION**

**Method:** Bearer Token (API Key)

**Header:**
```
Authorization: Bearer YOUR_API_KEY
```

**API Key Management:**
- Obtain from: https://openrouter.ai/keys
- Store securely in environment variable: `OPENROUTER_API_KEY`
- Free tier: Limited requests

**Base URL:**
```
https://openrouter.ai/api/v1
```

---

## 📡 **API ENDPOINTS & CAPABILITIES**

### **1. Chat Completions**

**Endpoint:** `POST https://openrouter.ai/api/v1/chat/completions`

**Purpose:** Chat with any model (OpenAI-compatible)

**Request Parameters:**

```typescript
interface OpenRouterChatCompletionRequest {
  // Required
  model: string                     // Model ID (e.g., 'openai/gpt-4', 'anthropic/claude-3-opus', 'meta-llama/llama-3-70b-instruct')
  
  // Required
  messages: Array<{
    role: 'system' | 'user' | 'assistant'
    content: string
  }>
  
  // Optional - Generation Parameters
  temperature?: number              // 0-2
  top_p?: number                    // 0-1
  max_tokens?: number               // Max tokens to generate
  stream?: boolean                  // Stream responses
  stop?: string | string[]          // Stop sequences
  presence_penalty?: number         // -2 to 2
  frequency_penalty?: number        // -2 to 2
  logit_bias?: Record<string, number>
  user?: string
  
  // Optional - Routing
  route?: 'fallback' | 'loadbalance' | string // Model routing strategy
  
  // Optional - Response Format
  response_format?: {
    type: 'text' | 'json_object'
  }
  
  // OpenRouter specific
  transforms?: string[]             // Response transforms
  metadata?: {
    tags?: Record<string, string>
  }
}
```

**Available Models (100+):**
- `openai/gpt-4` - GPT-4
- `openai/gpt-3.5-turbo` - GPT-3.5 Turbo
- `anthropic/claude-3-opus` - Claude 3 Opus
- `anthropic/claude-3-sonnet` - Claude 3 Sonnet
- `meta-llama/llama-3-70b-instruct` - Llama 3 70B
- `google/gemini-pro` - Gemini Pro
- `mistralai/mixtral-8x7b-instruct` - Mixtral
- `togethercomputer/llama-2-70b-chat` - Llama 2
- And 90+ more...

**Response Structure:**

```typescript
interface OpenRouterChatCompletionResponse {
  id: string
  model: string
  created: number
  choices: Array<{
    index: number
    message: {
      role: 'assistant'
      content: string | null
    }
    finish_reason: 'stop' | 'length'
  }>
  usage: {
    prompt_tokens: number
    completion_tokens: number
    total_tokens: number
  }
  // OpenRouter specific
  _meta?: {
    model: {
      id: string
      name: string
    }
    api_key?: {
      id: string
      name: string
    }
    warnings?: string[]
  }
}
```

**Streaming:** Same as OpenAI (SSE format)

---

### **2. List Models**

**Endpoint:** `GET https://openrouter.ai/api/v1/models`

**Purpose:** List all available models

**Response:**

```typescript
interface OpenRouterListModelsResponse {
  data: Array<{
    id: string                      // Model ID
    name: string                    // Model name
    description?: string
    pricing: {
      prompt: string                // Price per 1M prompt tokens
      completion: string            // Price per 1M completion tokens
    }
    context_length: number          // Context window size
    architecture: {
      modality: string
      tokenizer: string
      instruct_type?: string
    }
    top_provider: {
      max_completion_tokens?: number
      is_moderated?: boolean
    }
    per_request_limits?: {
      prompt_tokens?: string
      completion_tokens?: string
    }
  }>
}
```

---

### **3. Get Model Info**

**Endpoint:** `GET https://openrouter.ai/api/v1/models/{modelId}`

**Purpose:** Get specific model information

---

### **4. Generate Key**

**Endpoint:** `POST https://openrouter.ai/api/v1/keys`

**Purpose:** Generate API key

---

## 🔄 **WORKFLOWS**

### **Workflow 1: Chat with Any Model**

1. Browse available models
2. Select model
3. Enter message
4. Configure parameters
5. Submit → Get response
6. Display result

### **Workflow 2: Model Comparison**

1. Select multiple models
2. Send same prompt to all
3. Compare responses
4. Display comparison

### **Workflow 3: Automatic Fallback**

1. Configure primary model
2. Configure fallback models
3. Submit request
4. If primary fails → Use fallback
5. Display result

---

## ⚡ **RATE LIMITS**

**Free Tier:**
- Limited requests

**Paid Tier:**
- Higher limits
- Pay-per-use pricing

---

## 💰 **PRICING**

**Free Tier:**
- Limited requests
- Free forever

**Paid Tier:**
- Pay-per-use
- Pricing varies by model
- Check OpenRouter pricing page for current rates

---

## 🎨 **UI COMPONENT REQUIREMENTS**

### **Model Browser Panel**

**Model List:**
- Search/filter models
- Provider filter
- Capability filter
- Pricing display
- "Use Model" button

**Model Cards:**
- Model name
- Provider
- Pricing
- Context length
- Capabilities

### **Chat Panel**

**Model Selector:**
- Model dropdown (with search)
- Model info display
- Pricing info

**Chat Interface:**
- Message list
- User/assistant messages
- Model indicator
- Streaming indicator

**Generation Parameters:**
- Temperature slider
- Max tokens input
- Top P slider

**Routing Options:**
- Fallback configuration
- Load balancing options

**Streaming Toggle:**
- Enable/disable streaming

---

## 🔧 **IMPLEMENTATION NOTES**

### **Service Layer Structure**

```typescript
class OpenRouterService extends BaseAPIService {
  constructor(apiKey?: string) {
    super('openrouter', 'https://openrouter.ai/api/v1', apiKey)
  }

  async chatCompletion(request: OpenRouterChatCompletionRequest): Promise<APIResponse<OpenRouterChatCompletionResponse>>
  async streamChatCompletion(
    request: Omit<OpenRouterChatCompletionRequest, 'stream'>,
    onChunk: (chunk: OpenRouterChatCompletionChunk) => void
  ): Promise<APIResponse<void>>
  async listModels(): Promise<APIResponse<OpenRouterListModelsResponse>>
  async getModel(modelId: string): Promise<APIResponse<any>>
  
  // Helper methods
  searchModels(query: string, filters?: any): Promise<APIResponse<any>>
  compareModels(modelIds: string[], prompt: string): Promise<APIResponse<any>>
}
```

---

## 📊 **INTEGRATION COMPLEXITY**

**Complexity:** Medium

**Dependencies:**
- Model discovery system
- Model comparison logic
- Fallback handling

**Estimated Implementation Time:**
- Service layer: 6-8 hours
- Model browser: 8-10 hours
- Chat interface: 6-8 hours
- Model comparison: 4-6 hours
- Fallback logic: 4-6 hours
- Testing: 4-6 hours
- **Total: 32-44 hours**

---

**Status:** Deep dive complete - Ready for implementation  
**Last Updated:** 2025-01-27

