---
id: "google_gemini_api_deep_dive"
system: "lucid_chat"
component: "api_integration"
level: "T3"
type: "deep_analysis"
title: "Google Gemini API Deep Dive - Complete Integration Guide"
description: "Comprehensive analysis of Google Gemini API including Vertex AI capabilities, endpoints, parameters, workflows, and integration patterns"
created: "2025-01-27T00:00:00Z"
updated: "2025-01-27T00:00:00Z"
author: "aether"
status: "active"
tags: ["google", "gemini", "vertex-ai", "llm", "api-integration", "deep-dive"]
---

# Google Gemini API Deep Dive - Complete Integration Guide

**Purpose:** Comprehensive understanding of Google Gemini API (including Vertex AI) for proper integration  
**Status:** 🔍 **DEEP ANALYSIS COMPLETE**  
**Official Documentation:** 
- Gemini API: https://ai.google.dev/docs
- Vertex AI: https://cloud.google.com/vertex-ai/docs

---

## 🎯 **GOOGLE GEMINI API OVERVIEW**

Google provides Gemini AI through two APIs:
- **Gemini API** - Direct API access
- **Vertex AI** - Google Cloud integration

**Capabilities:**
- **Multimodal** - Text, image, video, audio inputs
- **Long Context** - Up to 1M tokens (Gemini 1.5 Pro)
- **Multiple Models** - Gemini 1.5 Pro, Flash, Nano
- **Function Calling** - Tool use support
- **Streaming** - Real-time streaming
- **Embeddings** - Text embeddings

**Key Features:**
- Native multimodal support
- Extremely long context windows
- Google Cloud integration
- Free tier available

---

## 🔐 **AUTHENTICATION**

### **Gemini API (Direct)**

**Method:** API Key (Query Parameter)

**Query Parameter:**
```
key=YOUR_API_KEY
```

**API Key Management:**
- Obtain from: https://aistudio.google.com/app/apikey
- Store securely in environment variable: `GEMINI_API_KEY`

**Base URL:**
```
https://generativelanguage.googleapis.com/v1beta
```

### **Vertex AI**

**Method:** OAuth 2.0 or Service Account

**Header:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Service Account:**
- Create service account in Google Cloud Console
- Download JSON key file
- Use for authentication

**Base URL:**
```
https://{region}-aiplatform.googleapis.com/v1
```

---

## 📡 **API ENDPOINTS & CAPABILITIES**

### **1. Generate Content (Gemini API)**

**Endpoint:** `POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent`

**Purpose:** Generate content with Gemini

**Request Parameters:**

```typescript
interface GeminiGenerateContentRequest {
  // Required
  contents: Array<{
    role?: 'user' | 'model'
    parts: Array<{
      text?: string
      inline_data?: {
        mime_type: string
        data: string                 // Base64
      }
      file_data?: {
        mime_type: string
        file_uri: string
      }
      video_metadata?: {
        start_offset?: string
        end_offset?: string
      }
    }>
  }>
  
  // Optional - Generation Parameters
  generationConfig?: {
    temperature?: number            // 0-2 (default: 1.0)
    top_p?: number                  // 0-1
    top_k?: number                  // 1-40
    max_output_tokens?: number      // Max tokens to generate
    candidate_count?: number         // Number of candidates (1-8)
    stop_sequences?: string[]
  }
  
  // Optional - Safety Settings
  safetySettings?: Array<{
    category: 'HARM_CATEGORY_HARASSMENT' | 'HARM_CATEGORY_HATE_SPEECH' | 'HARM_CATEGORY_SEXUALLY_EXPLICIT' | 'HARM_CATEGORY_DANGEROUS_CONTENT'
    threshold: 'BLOCK_NONE' | 'BLOCK_ONLY_HIGH' | 'BLOCK_MEDIUM_AND_ABOVE' | 'BLOCK_LOW_AND_ABOVE'
  }>
  
  // Optional - System Instruction
  systemInstruction?: {
    parts: Array<{
      text: string
    }>
  }
  
  // Optional - Tool Use
  tools?: Array<{
    function_declarations?: Array<{
      name: string
      description: string
      parameters: Record<string, any> // JSON Schema
    }>
    google_search_retrieval?: {
      dynamic_retrieval_config?: {
        mode: 'MODE_DYNAMIC' | 'MODE_DYNAMIC_WITH_MULTI_TURN'
        dynamic_threshold?: number
      }
    }
  }>
  
  // Optional - Tool Config
  tool_config?: {
    function_calling_config?: {
      mode: 'AUTO' | 'ANY' | 'NONE'
      allowed_function_names?: string[]
    }
  }
}
```

**Available Models:**
- `gemini-1.5-pro` - Most capable
- `gemini-1.5-flash` - Fast, efficient
- `gemini-1.5-pro-latest` - Latest Pro
- `gemini-1.5-flash-latest` - Latest Flash
- `gemini-pro` - Legacy Pro
- `gemini-pro-vision` - Legacy Vision

**Response Structure:**

```typescript
interface GeminiGenerateContentResponse {
  candidates: Array<{
    content: {
      parts: Array<{
        text?: string
        function_call?: {
          name: string
          args: Record<string, any>
        }
      }>
      role: 'model'
    }
    finish_reason: 'STOP' | 'MAX_TOKENS' | 'SAFETY' | 'RECITATION' | 'OTHER'
    safety_ratings: Array<{
      category: string
      probability: 'NEGLIGIBLE' | 'LOW' | 'MEDIUM' | 'HIGH'
    }>
    citation_metadata?: {
      citations: Array<{
        start_index?: number
        end_index?: number
        uri?: string
        title?: string
        license?: string
      }>
    }
  }>
  prompt_feedback?: {
    block_reason?: 'SAFETY' | 'OTHER'
    safety_ratings: Array<{
      category: string
      probability: string
    }>
  }
  usage_metadata?: {
    prompt_token_count: number
    candidates_token_count: number
    total_token_count: number
  }
}
```

---

### **2. Stream Generate Content**

**Endpoint:** `POST https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent`

**Purpose:** Stream content generation

**Request:** Same as Generate Content

**Response:** Server-Sent Events (SSE) stream

---

### **3. Count Tokens**

**Endpoint:** `POST https://generativelanguage.googleapis.com/v1beta/models/{model}:countTokens`

**Purpose:** Count tokens in content

**Request:** Same structure as Generate Content (without generationConfig)

**Response:**

```typescript
interface GeminiCountTokensResponse {
  total_tokens: number
}
```

---

### **4. List Models**

**Endpoint:** `GET https://generativelanguage.googleapis.com/v1beta/models`

**Purpose:** List available models

**Response:**

```typescript
interface GeminiListModelsResponse {
  models: Array<{
    name: string
    display_name: string
    description: string
    input_token_limit: number
    output_token_limit: number
    supported_generation_methods: string[]
    temperature?: number
    top_p?: number
    top_k?: number
  }>
}
```

---

### **5. Embed Content**

**Endpoint:** `POST https://generativelanguage.googleapis.com/v1beta/models/{model}:embedContent`

**Purpose:** Generate embeddings

**Request Parameters:**

```typescript
interface GeminiEmbedContentRequest {
  model: string                     // e.g., 'models/text-embedding-004'
  content: {
    parts: Array<{
      text: string
    }>
  }
  task_type?: 'RETRIEVAL_QUERY' | 'RETRIEVAL_DOCUMENT' | 'SEMANTIC_SIMILARITY' | 'CLASSIFICATION' | 'CLUSTERING'
  title?: string                    // For document embeddings
}
```

**Response:**

```typescript
interface GeminiEmbedContentResponse {
  embedding: {
    values: number[]
  }
}
```

---

### **6. Vertex AI Endpoints**

**Endpoint:** `POST https://{region}-aiplatform.googleapis.com/v1/projects/{project}/locations/{location}/publishers/google/models/{model}:predict`

**Purpose:** Use Gemini via Vertex AI

**Authentication:** OAuth 2.0 or Service Account

**Request:** Similar to Gemini API but with Vertex AI format

---

## 🔄 **WORKFLOWS**

### **Workflow 1: Chat Completion**

1. User enters message
2. Select model
3. Configure parameters
4. Enable tool use (optional)
5. Enable streaming (optional)
6. Submit → Stream or wait → Display response

### **Workflow 2: Multimodal (Image/Video)**

1. User uploads image/video
2. Enter text prompt
3. Submit → Get multimodal response

### **Workflow 3: Long Context**

1. User provides long document
2. Enter query
3. Submit → Get response using full context

---

## ⚡ **RATE LIMITS**

**Free Tier:**
- 15 requests/minute
- 1,500 requests/day

**Paid Tier:**
- Higher rate limits
- Varies by model

---

## 💰 **PRICING**

**Free Tier:**
- Free forever
- Limited requests

**Paid Tier:**
- Gemini 1.5 Pro: $1.25/$5 per 1M input/output tokens
- Gemini 1.5 Flash: $0.075/$0.30 per 1M tokens
- Embeddings: $0.02 per 1M tokens

**Note:** Check Google AI pricing page for current rates.

---

## 🎨 **UI COMPONENT REQUIREMENTS**

### **Chat Panel**

**Model Selector:**
- Dropdown with Gemini models
- Model info (context window, capabilities)

**Chat Interface:**
- Message list
- User/assistant messages
- Image/video input support
- Tool use display
- Streaming indicator

**Generation Parameters:**
- Temperature slider
- Max tokens input
- Top P slider
- Top K input

**Safety Settings:**
- Safety category toggles
- Threshold selectors

**Tool Use:**
- Tool definitions editor
- Tool use display
- Google Search integration

**Streaming Toggle:**
- Enable/disable streaming

---

## 🔧 **IMPLEMENTATION NOTES**

### **Service Layer Structure**

```typescript
class GeminiService extends BaseAPIService {
  constructor(apiKey?: string, useVertexAI: boolean = false) {
    const baseURL = useVertexAI 
      ? 'https://us-central1-aiplatform.googleapis.com/v1'
      : 'https://generativelanguage.googleapis.com/v1beta'
    super('gemini', baseURL, apiKey)
  }

  async generateContent(model: string, request: GeminiGenerateContentRequest): Promise<APIResponse<GeminiGenerateContentResponse>>
  async streamGenerateContent(
    model: string,
    request: GeminiGenerateContentRequest,
    onChunk: (chunk: GeminiContentChunk) => void
  ): Promise<APIResponse<void>>
  async countTokens(model: string, contents: GeminiContent[]): Promise<APIResponse<GeminiCountTokensResponse>>
  async listModels(): Promise<APIResponse<GeminiListModelsResponse>>
  async embedContent(model: string, request: GeminiEmbedContentRequest): Promise<APIResponse<GeminiEmbedContentResponse>>
}
```

---

## 📊 **INTEGRATION COMPLEXITY**

**Complexity:** High

**Dependencies:**
- Streaming support
- Multimodal handling
- Tool use handler
- Vertex AI integration (optional)

**Estimated Implementation Time:**
- Service layer: 8-10 hours
- Chat interface: 6-8 hours
- Multimodal support: 6-8 hours
- Tool use: 6-8 hours
- Vertex AI integration: 4-6 hours
- Testing: 6-8 hours
- **Total: 36-48 hours**

---

**Status:** Deep dive complete - Ready for implementation  
**Last Updated:** 2025-01-27

