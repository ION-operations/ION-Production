---
id: "deepinfra_api_deep_dive"
system: "lucid_chat"
component: "api_integration"
level: "T3"
type: "deep_analysis"
title: "DeepInfra API Deep Dive - Complete Integration Guide"
description: "Comprehensive analysis of DeepInfra API capabilities, endpoints, parameters, workflows, and integration patterns"
created: "2025-01-27T00:00:00Z"
updated: "2025-01-27T00:00:00Z"
author: "aether"
status: "active"
tags: ["deepinfra", "ai-models", "api-integration", "deep-dive", "comprehensive"]
---

# DeepInfra API Deep Dive - Complete Integration Guide

**Purpose:** Comprehensive understanding of DeepInfra API for ALL model types  
**Status:** 🔍 **DEEP ANALYSIS COMPLETE**  
**Official Documentation:** https://deepinfra.com/docs (verify URL)

---

## 🎯 **DEEPINFRA API OVERVIEW**

DeepInfra is a cloud platform providing access to **100+ AI models** with focus on:
- **Open Source LLMs** - Llama, Mistral, Mixtral, Qwen, etc.
- **Image Generation** - Stable Diffusion, SDXL, Flux, etc.
- **Embeddings** - Text embeddings, image embeddings
- **Code Generation** - Code completion, code explanation
- **Multimodal** - Vision-language models, image understanding

**Key Features:**
- **High Performance** - Optimized inference, low latency
- **Cost Effective** - Competitive pricing
- **REST API** - Simple REST interface
- **Streaming** - Real-time streaming support
- **Batch Processing** - Batch inference support
- **Custom Models** - Deploy custom models
- **Rate Limits** - Generous free tier

---

## 🔐 **AUTHENTICATION**

**Method:** Bearer Token (API Key)

**Header:**
```
Authorization: Bearer YOUR_API_KEY
```

**API Key Management:**
- Obtain from: https://deepinfra.com/dash/api_keys (verify URL)
- Store securely in environment variable: `DEEPINFRA_API_KEY`
- Rate limits: Based on account tier

**Base URL:**
```
https://api.deepinfra.com/v1
```

---

## 📡 **CORE API ENDPOINTS**

### **1. Chat Completion (LLM Models)**

**Endpoint:** `POST https://api.deepinfra.com/v1/chat/completions`

**Purpose:** Chat with language models

**Request Parameters:**

```typescript
interface DeepInfraChatCompletionRequest {
  // Required
  model: string                    // Model identifier (e.g., 'meta-llama/Meta-Llama-3-70B-Instruct')
  
  // Required
  messages: Array<{
    role: 'system' | 'user' | 'assistant'
    content: string | Array<{
      type: 'text' | 'image_url'
      text?: string
      image_url?: {
        url: string
      }
    }>
  }>
  
  // Optional - Generation Parameters
  temperature?: number             // 0-2 (default: 1.0)
  top_p?: number                   // 0-1 (default: 1.0)
  top_k?: number                   // 1-100 (default: null)
  max_tokens?: number              // Max tokens to generate
  min_tokens?: number              // Min tokens to generate
  repetition_penalty?: number      // 0-2 (default: 1.0)
  frequency_penalty?: number       // -2 to 2 (default: 0)
  presence_penalty?: number        // -2 to 2 (default: 0)
  stop?: string[]                  // Stop sequences
  seed?: number                    // Random seed
  
  // Optional - Streaming
  stream?: boolean                 // Stream responses
  
  // Optional - Other
  n?: number                       // Number of completions (default: 1)
  user?: string                    // User identifier
  response_format?: {
    type: 'json_object'           // Force JSON output
  }
}
```

**Available Models:**

**Llama Models:**
- `meta-llama/Meta-Llama-3-70B-Instruct`
- `meta-llama/Meta-Llama-3-8B-Instruct`
- `meta-llama/Meta-Llama-3.1-70B-Instruct`
- `meta-llama/Meta-Llama-3.1-8B-Instruct`

**Mistral Models:**
- `mistralai/Mistral-7B-Instruct-v0.2`
- `mistralai/Mixtral-8x7B-Instruct-v0.1`
- `mistralai/Mixtral-8x22B-Instruct-v0.1`

**Other Models:**
- `Qwen/Qwen2.5-72B-Instruct`
- `google/gemma-2-27b-it`
- `microsoft/Phi-3-medium-4k-instruct`
- `01-ai/Yi-1.5-34B-Chat-4bits`
- Many more...

**Response Structure:**

```typescript
interface DeepInfraChatCompletionResponse {
  id: string
  object: 'chat.completion'
  created: number                  // Unix timestamp
  model: string
  choices: Array<{
    index: number
    message: {
      role: 'assistant'
      content: string
    }
    finish_reason: 'stop' | 'length' | 'tool_calls' | 'content_filter'
    logprobs?: {
      content: Array<{
        token: string
        logprob: number
        top_logprobs: Array<{
          token: string
          logprob: number
        }>
      }>
    }
  }>
  usage: {
    prompt_tokens: number
    completion_tokens: number
    total_tokens: number
  }
}
```

**Streaming Response:**

For streaming (`stream: true`), responses are Server-Sent Events (SSE):

```
data: {"id":"...","object":"chat.completion.chunk","created":1234567890,"model":"...","choices":[{"index":0,"delta":{"role":"assistant","content":"Hello"},"finish_reason":null}]}

data: {"id":"...","object":"chat.completion.chunk","created":1234567890,"model":"...","choices":[{"index":0,"delta":{"content":" world"},"finish_reason":null}]}

data: [DONE]
```

---

### **2. Text Completion**

**Endpoint:** `POST https://api.deepinfra.com/v1/completions`

**Purpose:** Complete text (legacy endpoint, use chat/completions)

**Request Parameters:**

```typescript
interface DeepInfraCompletionRequest {
  model: string                    // Required
  prompt: string                   // Required
  suffix?: string
  max_tokens?: number
  temperature?: number
  top_p?: number
  top_k?: number
  n?: number
  stream?: boolean
  logprobs?: number
  echo?: boolean
  stop?: string[]
  presence_penalty?: number
  frequency_penalty?: number
  best_of?: number
  logit_bias?: Record<string, number>
  user?: string
}
```

**Response:** Similar to chat completion

---

### **3. Image Generation**

**Endpoint:** `POST https://api.deepinfra.com/v1/inference/{model}`

**Purpose:** Generate images (varies by model)

**Request Parameters:**

```typescript
interface DeepInfraImageGenerationRequest {
  // Model-specific input (varies by model)
  prompt: string                   // Required for most models
  negative_prompt?: string
  num_inference_steps?: number
  guidance_scale?: number
  width?: number
  height?: number
  seed?: number
  num_images?: number
  // ... model-specific parameters
}
```

**Available Image Models:**
- `stability-ai/stable-diffusion-xl-base-1.0`
- `stability-ai/sdxl-turbo`
- `black-forest-labs/flux-dev`
- `runwayml/stable-diffusion-v1-5`
- Many more...

**Response:**

```typescript
interface DeepInfraImageGenerationResponse {
  images?: string[]                // Base64 encoded images or URLs
  // Model-specific response structure
}
```

---

### **4. Embeddings**

**Endpoint:** `POST https://api.deepinfra.com/v1/embeddings`

**Purpose:** Generate text embeddings

**Request Parameters:**

```typescript
interface DeepInfraEmbeddingsRequest {
  model: string                    // Required (e.g., 'BAAI/bge-large-en-v1.5')
  input: string | string[]         // Required: Text or array of texts
  encoding_format?: 'float' | 'base64'
  user?: string
}
```

**Response:**

```typescript
interface DeepInfraEmbeddingsResponse {
  object: 'list'
  data: Array<{
    object: 'embedding'
    embedding: number[] | string   // Array of floats or base64 string
    index: number
  }>
  model: string
  usage: {
    prompt_tokens: number
    total_tokens: number
  }
}
```

---

### **5. List Models**

**Endpoint:** `GET https://api.deepinfra.com/v1/models`

**Purpose:** List available models

**Response:**

```typescript
interface DeepInfraListModelsResponse {
  data: Array<{
    id: string                     // Model identifier
    object: 'model'
    created: number
    owned_by: string
    permission: Array<{
      id: string
      object: 'model_permission'
      created: number
      allow_create_engine: boolean
      allow_sampling: boolean
      allow_logprobs: boolean
      allow_search_indices: boolean
      allow_view: boolean
      allow_fine_tuning: boolean
      organization: string
      group: string | null
      is_blocking: boolean
    }>
    root: string
    parent: string | null
  }>
  object: 'list'
}
```

---

### **6. Get Model**

**Endpoint:** `GET https://api.deepinfra.com/v1/models/{model_id}`

**Purpose:** Get details about a specific model

**Response:** Model object

---

## 🔄 **WORKFLOWS**

### **Workflow 1: Chat Completion**

1. User selects model
2. Configure system message (optional)
3. User enters message
4. Configure generation parameters (temperature, max_tokens, etc.)
5. Submit → Stream or wait for completion
6. Display response
7. Continue conversation

### **Workflow 2: Image Generation**

1. User selects image model
2. Enter prompt
3. Configure parameters (size, steps, guidance, etc.)
4. Submit → Poll for completion
5. Display generated image(s)
6. Download or regenerate

### **Workflow 3: Embeddings**

1. User enters text(s)
2. Select embedding model
3. Submit → Get embeddings
4. Display embedding vector
5. Use for similarity search, clustering, etc.

---

## ⚡ **RATE LIMITS**

**Free Tier:**
- Generous free tier
- Rate limits vary by model

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
- Pricing varies by model
- Typically $0.0001-0.01 per 1K tokens for LLMs
- Image generation: ~$0.001-0.01 per image

**Note:** Check DeepInfra pricing page for current rates.

---

## 🎨 **UI COMPONENT REQUIREMENTS**

### **Chat Completion Panel**

**Model Selector:**
- Searchable dropdown
- Group by model family (Llama, Mistral, etc.)
- Show model capabilities
- Show pricing

**System Message:**
- Textarea for system prompt
- Examples/templates

**Chat Interface:**
- Message list
- User/assistant messages
- Streaming indicator
- Token usage display

**Generation Parameters:**
- Temperature slider (0-2)
- Max tokens input
- Top P slider (0-1)
- Top K input
- Repetition penalty slider
- Stop sequences input
- Seed input

**Streaming Toggle:**
- Enable/disable streaming
- Show streaming indicator

### **Image Generation Panel**

**Model Selector:**
- Image model dropdown
- Model info display

**Prompt Input:**
- Textarea for prompt
- Negative prompt input
- Character counter

**Parameter Controls:**
- Width/Height inputs
- Inference steps slider
- Guidance scale slider
- Seed input
- Number of images selector

**Generate Button:**
- Show loading state
- Progress indicator

**Image Display:**
- Grid view for multiple images
- Full-size view
- Download buttons

### **Embeddings Panel**

**Text Input:**
- Single text or multiple texts
- Text area or list

**Model Selector:**
- Embedding model dropdown

**Generate Button:**
- Show loading state

**Results Display:**
- Embedding vector display
- Vector visualization
- Similarity calculator
- Export options

---

## 🔧 **IMPLEMENTATION NOTES**

### **Service Layer Structure**

```typescript
class DeepInfraService extends BaseAPIService {
  constructor(apiKey?: string) {
    super('deepinfra', 'https://api.deepinfra.com/v1', apiKey)
  }

  // Chat Completion
  async chatCompletion(request: DeepInfraChatCompletionRequest): Promise<APIResponse<DeepInfraChatCompletionResponse>>
  async streamChatCompletion(
    request: Omit<DeepInfraChatCompletionRequest, 'stream'>,
    onChunk: (chunk: DeepInfraChatCompletionChunk) => void
  ): Promise<APIResponse<void>>
  
  // Text Completion
  async completion(request: DeepInfraCompletionRequest): Promise<APIResponse<DeepInfraCompletionResponse>>
  
  // Image Generation
  async generateImage(
    model: string,
    request: DeepInfraImageGenerationRequest
  ): Promise<APIResponse<DeepInfraImageGenerationResponse>>
  
  // Embeddings
  async createEmbeddings(request: DeepInfraEmbeddingsRequest): Promise<APIResponse<DeepInfraEmbeddingsResponse>>
  
  // Model Discovery
  async listModels(): Promise<APIResponse<DeepInfraListModelsResponse>>
  async getModel(modelId: string): Promise<APIResponse<DeepInfraModel>>
  
  // Helpers
  async searchModels(query: string, category?: string): Promise<APIResponse<DeepInfraModel[]>>
}
```

### **State Management**

```typescript
interface DeepInfraState {
  // Model Selection
  selectedModel: string | null
  availableModels: DeepInfraModel[]
  
  // Chat
  messages: Array<{
    role: 'system' | 'user' | 'assistant'
    content: string
    timestamp: Date
  }>
  systemMessage: string
  isStreaming: boolean
  streamingContent: string
  
  // Generation Parameters
  temperature: number
  maxTokens: number
  topP: number
  topK?: number
  repetitionPenalty: number
  
  // Image Generation
  imagePrompt: string
  negativePrompt: string
  imageWidth: number
  imageHeight: number
  numInferenceSteps: number
  guidanceScale: number
  seed?: number
  
  // Results
  chatResponse: string | null
  images: string[]
  embeddings: number[][]
  
  // Status
  isGenerating: boolean
  error: string | null
  
  // Usage
  usage: {
    promptTokens: number
    completionTokens: number
    totalTokens: number
  }
}
```

---

## 📊 **INTEGRATION COMPLEXITY**

**Complexity:** Very High

**Dependencies:**
- DeepInfra API client
- Streaming support (SSE)
- Multiple model type handlers
- Chat interface
- Image generation UI
- Embeddings visualization
- State management (Zustand)

**Estimated Implementation Time:**
- Service layer: 8-10 hours
- Chat interface: 6-8 hours
- Image generation UI: 4-6 hours
- Embeddings UI: 3-4 hours
- Model discovery: 3-4 hours
- Streaming support: 4-6 hours
- Testing: 6-8 hours
- **Total: 34-46 hours**

---

## ✅ **CHECKLIST**

### **Service Layer**
- [ ] DeepInfraChatCompletionRequest interface
- [ ] chatCompletion method
- [ ] streamChatCompletion method
- [ ] completion method
- [ ] generateImage method
- [ ] createEmbeddings method
- [ ] listModels method
- [ ] getModel method
- [ ] Error handling
- [ ] Rate limit handling

### **UI Components**
- [ ] Model selector with search
- [ ] Chat interface
- [ ] Streaming indicator
- [ ] Generation parameter controls
- [ ] Image generation panel
- [ ] Embeddings panel
- [ ] Token usage display
- [ ] Error display

### **Testing**
- [ ] Test chat completion
- [ ] Test streaming
- [ ] Test image generation
- [ ] Test embeddings
- [ ] Test model discovery
- [ ] Test error handling
- [ ] Test rate limits

---

**Status:** Deep dive complete - Ready for implementation  
**Last Updated:** 2025-01-27  
**Next:** Implement service layer and UI components

