---
id: "together_ai_api_deep_dive"
system: "lucid_chat"
component: "api_integration"
level: "T3"
type: "deep_analysis"
title: "Together AI API Deep Dive - Complete Integration Guide"
description: "Comprehensive analysis of Together AI API capabilities - unified inference platform with free tier"
created: "2025-01-27T00:00:00Z"
updated: "2025-01-27T00:00:00Z"
author: "aether"
status: "active"
tags: ["together-ai", "llm", "unified-inference", "free-tier", "api-integration", "deep-dive"]
---

# Together AI API Deep Dive - Complete Integration Guide

**Purpose:** Comprehensive understanding of Together AI API for proper integration  
**Status:** 🔍 **DEEP ANALYSIS COMPLETE**  
**Official Documentation:** https://docs.together.ai

---

## 🎯 **TOGETHER AI API OVERVIEW**

Together AI provides unified inference platform:
- **Chat Completions** - Multiple models (Llama, Mistral, Mixtral, etc.)
- **Embeddings** - Text embeddings
- **Image Generation** - Image generation
- **Fine-tuning** - Custom model fine-tuning
- **Free Tier** - Generous free tier
- **OpenAI-Compatible** - OpenAI API compatibility

**Key Features:**
- Unified platform for multiple models
- Free tier available
- OpenAI-compatible API
- Fine-tuning support
- Streaming support

---

## 🔐 **AUTHENTICATION**

**Method:** Bearer Token (API Key)

**Header:**
```
Authorization: Bearer YOUR_API_KEY
```

**API Key Management:**
- Obtain from: https://api.together.xyz
- Store securely in environment variable: `TOGETHER_API_KEY`
- Free tier: $25 credit/month

**Base URL:**
```
https://api.together.xyz/v1
```

---

## 📡 **API ENDPOINTS & CAPABILITIES**

### **1. Chat Completions**

**Endpoint:** `POST https://api.together.xyz/v1/chat/completions`

**Purpose:** Chat with models (OpenAI-compatible)

**Request Parameters:**

```typescript
interface TogetherAIChatCompletionRequest {
  // Required
  model: 'meta-llama/Llama-3-70b-chat-hf' | 'mistralai/Mixtral-8x7B-Instruct-v0.1' | 'mistralai/Mistral-7B-Instruct-v0.2' | string
  
  // Required
  messages: Array<{
    role: 'system' | 'user' | 'assistant'
    content: string
  }>
  
  // Optional - Generation Parameters
  temperature?: number              // 0-2 (default: 1.0)
  top_p?: number                    // 0-1 (default: 1.0)
  top_k?: number                    // 1-100
  max_tokens?: number               // Max tokens to generate
  stream?: boolean                  // Stream responses
  stop?: string | string[]          // Stop sequences
  presence_penalty?: number         // -2 to 2
  frequency_penalty?: number        // -2 to 2
  repetition_penalty?: number        // 0-2
  logit_bias?: Record<string, number>
  user?: string
  
  // Optional - Response Format
  response_format?: {
    type: 'text' | 'json_object'
  }
  
  // Together AI specific
  safety_model?: string
  stop_sequences?: string[]
}
```

**Available Models:**
- `meta-llama/Llama-3-70b-chat-hf` - Llama 3 70B
- `meta-llama/Llama-3-8b-chat-hf` - Llama 3 8B
- `mistralai/Mixtral-8x7B-Instruct-v0.1` - Mixtral 8x7B
- `mistralai/Mistral-7B-Instruct-v0.2` - Mistral 7B
- `togethercomputer/llama-2-70b-chat` - Llama 2 70B
- `meta-llama/Llama-2-70b-chat-hf` - Llama 2 70B
- And many more...

**Response Structure:**

```typescript
interface TogetherAIChatCompletionResponse {
  id: string
  object: 'chat.completion'
  created: number
  model: string
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
}
```

**Streaming:** Same as OpenAI (SSE format)

---

### **2. Embeddings**

**Endpoint:** `POST https://api.together.xyz/v1/embeddings`

**Purpose:** Generate embeddings

**Request:**

```typescript
interface TogetherAIEmbeddingsRequest {
  model: string                     // e.g., 'togethercomputer/m2-bert-80M-8k-retrieval'
  input: string | string[]          // Required
  encoding_format?: 'float' | 'base64'
}
```

---

### **3. Image Generation**

**Endpoint:** `POST https://api.together.xyz/v1/images/generations`

**Purpose:** Generate images

**Request:**

```typescript
interface TogetherAIImageGenerationRequest {
  prompt: string                    // Required
  model?: string
  n?: number
  size?: string
  response_format?: 'url' | 'b64_json'
  user?: string
}
```

---

### **4. Fine-tuning**

**Endpoint:** `POST https://api.together.xyz/v1/fine_tuning/jobs`

**Purpose:** Create fine-tuning job

**Request:**

```typescript
interface TogetherAIFineTuningRequest {
  model: string                     // Base model
  training_file: string              // Training file ID
  hyperparameters?: {
    n_epochs?: number
    batch_size?: number
    learning_rate?: number
  }
  suffix?: string                   // Model name suffix
}
```

---

## 🔄 **WORKFLOWS**

### **Workflow 1: Chat Completion**

1. User enters message
2. Select model
3. Configure parameters
4. Enable streaming (optional)
5. Submit → Get response
6. Display result

### **Workflow 2: Fine-tuning**

1. Prepare training data
2. Upload training file
3. Create fine-tuning job
4. Monitor job status
5. Use fine-tuned model

---

## ⚡ **RATE LIMITS**

**Free Tier:**
- $25 credit/month
- Rate limits apply

**Paid Tier:**
- Higher limits
- Pay-per-use pricing

---

## 💰 **PRICING**

**Free Tier:**
- $25 credit/month
- Free forever

**Paid Tier:**
- Pay-per-use
- Competitive pricing
- Check Together AI pricing page for current rates

---

## 🎨 **UI COMPONENT REQUIREMENTS**

### **Chat Panel**

**Model Selector:**
- Dropdown with Together AI models
- Model info display

**Chat Interface:**
- Message list
- User/assistant messages
- Streaming indicator

**Generation Parameters:**
- Temperature slider
- Max tokens input
- Top P slider
- Repetition penalty slider

**Streaming Toggle:**
- Enable/disable streaming

---

## 🔧 **IMPLEMENTATION NOTES**

### **Service Layer Structure**

```typescript
class TogetherAIService extends BaseAPIService {
  constructor(apiKey?: string) {
    super('together-ai', 'https://api.together.xyz/v1', apiKey)
  }

  async chatCompletion(request: TogetherAIChatCompletionRequest): Promise<APIResponse<TogetherAIChatCompletionResponse>>
  async streamChatCompletion(
    request: Omit<TogetherAIChatCompletionRequest, 'stream'>,
    onChunk: (chunk: TogetherAIChatCompletionChunk) => void
  ): Promise<APIResponse<void>>
  async createEmbeddings(request: TogetherAIEmbeddingsRequest): Promise<APIResponse<any>>
  async generateImage(request: TogetherAIImageGenerationRequest): Promise<APIResponse<any>>
  async createFineTuningJob(request: TogetherAIFineTuningRequest): Promise<APIResponse<any>>
  async listModels(): Promise<APIResponse<any>>
}
```

---

## 📊 **INTEGRATION COMPLEXITY**

**Complexity:** Low-Medium (OpenAI-compatible)

**Estimated Implementation Time:**
- Service layer: 3-4 hours
- UI components: 5-6 hours
- Fine-tuning UI: 4-6 hours
- Streaming support: 2-3 hours
- Testing: 3-4 hours
- **Total: 17-23 hours**

---

**Status:** Deep dive complete - Ready for implementation  
**Last Updated:** 2025-01-27

