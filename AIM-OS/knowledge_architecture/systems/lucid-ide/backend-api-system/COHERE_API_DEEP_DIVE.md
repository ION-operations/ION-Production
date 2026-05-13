---
id: "cohere_api_deep_dive"
system: "lucid_chat"
component: "api_integration"
level: "T3"
type: "deep_analysis"
title: "Cohere API Deep Dive - Complete Integration Guide"
description: "Comprehensive analysis of Cohere API capabilities including Chat, Embeddings, Rerank, Classify, and more"
created: "2025-01-27T00:00:00Z"
updated: "2025-01-27T00:00:00Z"
author: "aether"
status: "active"
tags: ["cohere", "llm", "rag", "api-integration", "deep-dive"]
---

# Cohere API Deep Dive - Complete Integration Guide

**Purpose:** Comprehensive understanding of Cohere API for proper integration  
**Status:** 🔍 **DEEP ANALYSIS COMPLETE**  
**Official Documentation:** https://docs.cohere.com

---

## 🎯 **COHERE API OVERVIEW**

Cohere provides enterprise-focused AI capabilities:
- **Chat** - Command R, Command R+ models
- **Embeddings** - Text embeddings (multilingual)
- **Rerank** - Rerank search results
- **Classify** - Text classification
- **Generate** - Text generation
- **Summarize** - Text summarization
- **RAG** - Retrieval-Augmented Generation focus

**Key Features:**
- Enterprise-focused
- RAG optimization
- Multilingual support
- Free prototyping tier
- Strong embeddings

---

## 🔐 **AUTHENTICATION**

**Method:** Bearer Token (API Key)

**Header:**
```
Authorization: Bearer YOUR_API_KEY
```

**API Key Management:**
- Obtain from: Cohere dashboard
- Store securely in environment variable: `COHERE_API_KEY`
- Free tier: 100 requests/minute

**Base URL:**
```
https://api.cohere.com/v1
```

---

## 📡 **API ENDPOINTS & CAPABILITIES**

### **1. Chat**

**Endpoint:** `POST https://api.cohere.com/v1/chat`

**Purpose:** Chat with Command models

**Request Parameters:**

```typescript
interface CohereChatRequest {
  // Required
  model?: 'command-r-plus' | 'command-r' | 'command' | 'command-light' | 'command-nightly' | 'command-light-nightly'
  
  // Required
  message: string                   // User message
  
  // Optional - Conversation
  chat_history?: Array<{
    role: 'USER' | 'CHATBOT'
    message: string
  }>
  
  // Optional - Generation Parameters
  temperature?: number              // 0-5 (default: 0.3)
  max_tokens?: number               // Max tokens (default: 4096)
  k?: number                        // Top K (default: 0)
  p?: number                        // Top P (default: 0.75)
  frequency_penalty?: number        // 0-1 (default: 0)
  presence_penalty?: number         // 0-1 (default: 0)
  
  // Optional - RAG
  documents?: Array<{
    id?: string
    title?: string
    text: string
    url?: string
  }>
  connectors?: Array<{
    id: string
    user_access_token?: string
    continue_on_failure?: boolean
  }>
  
  // Optional - Tool Use
  tools?: Array<{
    name: string
    description: string
    parameter_definitions: Record<string, {
      description: string
      type: string
      required: boolean
    }>
  }>
  tool_results?: Array<{
    call: {
      name: string
      parameters: Record<string, any>
    }
    outputs: Array<Record<string, any>>
  }>
  
  // Optional - Other
  preamble?: string                 // System message
  prompt_truncation?: 'AUTO' | 'OFF'
  stream?: boolean                  // Stream responses
}
```

**Response Structure:**

```typescript
interface CohereChatResponse {
  text: string
  generation_id: string
  citations?: Array<{
    start: number
    end: number
    text: string
    document_ids: string[]
  }>
  documents?: Array<{
    id: string
    title?: string
    text: string
    url?: string
  }>
  search_queries?: Array<{
    text: string
    generation_id: string
  }>
  search_results?: Array<{
    search_query: {
      text: string
      generation_id: string
    }
    connector: {
      id: string
    }
    document_ids: string[]
  }>
  tool_calls?: Array<{
    name: string
    parameters: Record<string, any>
  }>
  finish_reason: 'COMPLETE' | 'ERROR' | 'ERROR_TOXIC' | 'ERROR_LIMIT' | 'USER_CANCEL' | 'MAX_TOKENS'
  meta?: {
    api_version: {
      version: string
    }
    billed_units?: {
      input_tokens: number
      output_tokens: number
    }
    tokens?: {
      input_tokens: number
      output_tokens: number
    }
  }
}
```

---

### **2. Embed**

**Endpoint:** `POST https://api.cohere.com/v1/embed`

**Purpose:** Generate embeddings

**Request Parameters:**

```typescript
interface CohereEmbedRequest {
  // Required
  model?: 'embed-english-v3.0' | 'embed-multilingual-v3.0' | 'embed-english-light-v3.0' | 'embed-multilingual-light-v3.0'
  
  // Required
  texts: string[]                   // Texts to embed
  
  // Optional
  input_type?: 'search_document' | 'search_query' | 'classification' | 'clustering' | 'rerank'
  truncate?: 'NONE' | 'START' | 'END'
  compression_codebook?: 'default'
}
```

**Response:**

```typescript
interface CohereEmbedResponse {
  id: string
  embeddings: number[][]
  texts: string[]
  meta?: {
    api_version: {
      version: string
    }
    billed_units?: {
      input_tokens: number
    }
  }
}
```

---

### **3. Rerank**

**Endpoint:** `POST https://api.cohere.com/v1/rerank`

**Purpose:** Rerank search results

**Request Parameters:**

```typescript
interface CohereRerankRequest {
  // Required
  model?: 'rerank-english-v3.0' | 'rerank-multilingual-v3.0'
  
  // Required
  query: string                     // Search query
  
  // Required
  documents: string[]                // Documents to rerank
  
  // Optional
  top_n?: number                    // Top N results (default: length of documents)
  return_documents?: boolean        // Return documents (default: false)
  max_chunks_per_doc?: number       // Max chunks per doc
}
```

**Response:**

```typescript
interface CohereRerankResponse {
  id: string
  results: Array<{
    index: number
    relevance_score: number
    document?: {
      text: string
    }
  }>
  meta?: {
    api_version: {
      version: string
    }
    billed_units?: {
      search_units: number
    }
  }
}
```

---

### **4. Classify**

**Endpoint:** `POST https://api.cohere.com/v1/classify`

**Purpose:** Classify text

**Request Parameters:**

```typescript
interface CohereClassifyRequest {
  // Required
  model?: 'embed-english-v3.0' | 'embed-multilingual-v3.0'
  
  // Required
  inputs: string[]                  // Texts to classify
  
  // Required (one of)
  examples?: Array<{
    text: string
    label: string
  }>
  preset?: string                   // Preset classifier
  
  // Optional
  truncate?: 'NONE' | 'START' | 'END'
}
```

**Response:**

```typescript
interface CohereClassifyResponse {
  id: string
  classifications: Array<{
    id: string
    input: string
    prediction: string
    confidence: number
    labels: Record<string, {
      confidence: number
    }>
  }>
  meta?: {
    api_version: {
      version: string
    }
  }
}
```

---

### **5. Generate**

**Endpoint:** `POST https://api.cohere.com/v1/generate`

**Purpose:** Generate text

**Request Parameters:**

```typescript
interface CohereGenerateRequest {
  model?: string                    // Model name
  prompt: string                    // Required
  max_tokens?: number
  temperature?: number
  k?: number
  p?: number
  frequency_penalty?: number
  presence_penalty?: number
  stop_sequences?: string[]
  return_likelihoods?: 'GENERATION' | 'ALL' | 'NONE'
  truncate?: 'NONE' | 'START' | 'END'
  stream?: boolean
}
```

---

### **6. Summarize**

**Endpoint:** `POST https://api.cohere.com/v1/summarize`

**Purpose:** Summarize text

**Request Parameters:**

```typescript
interface CohereSummarizeRequest {
  text: string                      // Required
  length?: 'short' | 'medium' | 'long'
  format?: 'paragraph' | 'bullets'
  model?: string
  extractiveness?: 'low' | 'medium' | 'high'
  temperature?: number
  additional_command?: string
}
```

---

## 🔄 **WORKFLOWS**

### **Workflow 1: Chat with RAG**

1. User enters query
2. Provide documents (optional)
3. Configure RAG settings
4. Submit → Get response with citations
5. Display response with source documents

### **Workflow 2: Embeddings + Rerank**

1. User enters search query
2. Get initial search results
3. Generate embeddings for query and results
4. Rerank results
5. Display reranked results

### **Workflow 3: Classification**

1. User enters text(s)
2. Provide examples or use preset
3. Submit → Get classifications
4. Display predictions with confidence scores

---

## ⚡ **RATE LIMITS**

**Free Tier:**
- 100 requests/minute
- Unlimited API calls for prototyping

**Paid Tier:**
- Higher rate limits
- Pay-per-use pricing

---

## 💰 **PRICING**

**Free Tier:**
- 100 requests/minute
- Free forever for prototyping

**Paid Tier:**
- Command R+: ~$3/$15 per 1M input/output tokens
- Command R: ~$0.50/$1.50 per 1M tokens
- Embeddings: ~$0.10/$0.10 per 1M tokens
- Rerank: ~$1 per 1K search units

**Note:** Check Cohere pricing page for current rates.

---

## 🎨 **UI COMPONENT REQUIREMENTS**

### **Chat Panel**

**Model Selector:**
- Dropdown with Command models
- Model info display

**Chat Interface:**
- Message list
- User/assistant messages
- Citations display
- Source documents display
- Tool use display

**RAG Configuration:**
- Documents input
- Connectors selector
- RAG settings

**Generation Parameters:**
- Temperature slider
- Max tokens input

### **Rerank Panel**

**Query Input:**
- Search query input

**Documents Input:**
- Documents list
- Add/remove documents

**Rerank Button:**
- Show loading state

**Results Display:**
- Reranked results with scores
- Relevance indicators

---

## 🔧 **IMPLEMENTATION NOTES**

### **Service Layer Structure**

```typescript
class CohereService extends BaseAPIService {
  constructor(apiKey?: string) {
    super('cohere', 'https://api.cohere.com/v1', apiKey)
  }

  async chat(request: CohereChatRequest): Promise<APIResponse<CohereChatResponse>>
  async streamChat(
    request: Omit<CohereChatRequest, 'stream'>,
    onChunk: (chunk: CohereChatChunk) => void
  ): Promise<APIResponse<void>>
  async embed(request: CohereEmbedRequest): Promise<APIResponse<CohereEmbedResponse>>
  async rerank(request: CohereRerankRequest): Promise<APIResponse<CohereRerankResponse>>
  async classify(request: CohereClassifyRequest): Promise<APIResponse<CohereClassifyResponse>>
  async generate(request: CohereGenerateRequest): Promise<APIResponse<any>>
  async summarize(request: CohereSummarizeRequest): Promise<APIResponse<any>>
}
```

---

## 📊 **INTEGRATION COMPLEXITY**

**Complexity:** Medium-High

**Dependencies:**
- RAG implementation
- Reranking logic
- Classification handling

**Estimated Implementation Time:**
- Service layer: 6-8 hours
- Chat interface: 6-8 hours
- RAG integration: 6-8 hours
- Rerank UI: 4-6 hours
- Classification UI: 4-6 hours
- Testing: 4-6 hours
- **Total: 30-42 hours**

---

**Status:** Deep dive complete - Ready for implementation  
**Last Updated:** 2025-01-27

