---
id: "perplexity_api_deep_dive"
system: "lucid_chat"
component: "api_integration"
level: "T3"
type: "deep_analysis"
title: "Perplexity API Deep Dive - Complete Integration Guide"
description: "Comprehensive analysis of Perplexity API capabilities, endpoints, parameters, workflows, and integration patterns"
created: "2025-01-27T00:00:00Z"
updated: "2025-01-27T00:00:00Z"
author: "aether"
status: "active"
tags: ["perplexity", "search", "ai-search", "api-integration", "deep-dive"]
---

# Perplexity API Deep Dive - Complete Integration Guide

**Purpose:** Comprehensive understanding of Perplexity API for proper integration  
**Status:** 🔍 **DEEP ANALYSIS COMPLETE**  
**Official Documentation:** https://docs.perplexity.ai (verify URL)

---

## 🎯 **PERPLEXITY API OVERVIEW**

Perplexity provides AI-powered search and chat capabilities:
- **Chat Completion** - AI chat with web search
- **Search** - Real-time web search with citations
- **Answer** - Direct answers with sources
- **Streaming** - Real-time streaming responses
- **Multiple Models** - Different models for different use cases

**Key Features:**
- Real-time web search integration
- Source citations
- Multiple model options
- Streaming support
- Context-aware responses

---

## 🔐 **AUTHENTICATION**

**Method:** Bearer Token (API Key)

**Header:**
```
Authorization: Bearer YOUR_API_KEY
```

**API Key Management:**
- Obtain from: Perplexity dashboard
- Store securely in environment variable: `PERPLEXITY_API_KEY`
- Rate limits: Based on account tier

**Base URL:**
```
https://api.perplexity.ai
```

---

## 📡 **API ENDPOINTS & CAPABILITIES**

### **1. Chat Completion**

**Endpoint:** `POST https://api.perplexity.ai/chat/completions`

**Purpose:** AI chat with web search capabilities

**Request Parameters:**

```typescript
interface PerplexityChatCompletionRequest {
  // Required
  model: 'llama-3.1-sonar-small-128k-online' | 'llama-3.1-sonar-large-128k-online' | 'llama-3.1-sonar-huge-128k-online' | 'sonar' | 'sonar-pro'
  
  // Required
  messages: Array<{
    role: 'system' | 'user' | 'assistant'
    content: string
  }>
  
  // Optional - Generation Parameters
  temperature?: number              // 0-2 (default: 0.2)
  top_p?: number                    // 0-1 (default: 0.9)
  top_k?: number                    // 0-100
  max_tokens?: number               // Max tokens to generate
  stream?: boolean                  // Stream responses
  
  // Optional - Search Control
  search_recency_filter?: 'month' | 'week' | 'day' | 'hour'  // Recency filter
  search_domain_filter?: string[]  // Domain filter
  return_citations?: boolean        // Return citations (default: true)
  return_images?: boolean           // Return images (default: false)
  return_related_questions?: boolean // Return related questions (default: false)
  
  // Optional - Other
  presence_penalty?: number          // -2 to 2
  frequency_penalty?: number        // -2 to 2
}
```

**Available Models:**
- `llama-3.1-sonar-small-128k-online` - Fast, cost-effective
- `llama-3.1-sonar-large-128k-online` - Balanced
- `llama-3.1-sonar-huge-128k-online` - Highest quality
- `sonar` - Alias for small
- `sonar-pro` - Alias for large

**Response Structure:**

```typescript
interface PerplexityChatCompletionResponse {
  id: string
  model: string
  object: 'chat.completion'
  created: number
  choices: Array<{
    index: number
    finish_reason: 'stop' | 'length' | 'tool_calls'
    message: {
      role: 'assistant'
      content: string
    }
    delta?: {
      role?: 'assistant'
      content?: string
    }
  }>
  usage: {
    prompt_tokens: number
    completion_tokens: number
    total_tokens: number
  }
  citations?: Array<{
    text: string
    url: string
    title?: string
  }>
  images?: string[]
  related_questions?: string[]
}
```

**Streaming Response:**

For streaming (`stream: true`), responses are Server-Sent Events (SSE):

```
data: {"id":"...","object":"chat.completion.chunk","created":1234567890,"model":"...","choices":[{"index":0,"delta":{"content":"Hello"},"finish_reason":null}]}

data: {"id":"...","object":"chat.completion.chunk","created":1234567890,"model":"...","choices":[{"index":0,"delta":{"content":" world"},"finish_reason":null}]}

data: [DONE]
```

---

## 🔄 **WORKFLOWS**

### **Workflow 1: Chat with Search**

1. User enters message
2. Select model
3. Configure search options (recency, domains)
4. Enable citations/images/related questions
5. Submit → Stream or wait for response
6. Display response with citations
7. Show related questions

### **Workflow 2: Research Query**

1. User enters research question
2. Configure search depth
3. Enable all return options
4. Submit → Get comprehensive response
5. Display answer with citations and images

---

## ⚡ **RATE LIMITS**

**Free Tier:**
- Limited requests per month

**Paid Tier:**
- Higher rate limits
- Pay-per-use pricing

---

## 💰 **PRICING**

**Pay-per-use:**
- Small model: ~$0.0001 per 1K tokens
- Large model: ~$0.0003 per 1K tokens
- Huge model: ~$0.001 per 1K tokens

**Note:** Check Perplexity pricing page for current rates.

---

## 🎨 **UI COMPONENT REQUIREMENTS**

### **Chat Panel**

**Model Selector:**
- Dropdown with model options
- Show model capabilities

**Chat Interface:**
- Message list
- User/assistant messages
- Citations display (inline or sidebar)
- Images display
- Related questions display

**Search Options:**
- Recency filter selector
- Domain filter input
- Return citations toggle
- Return images toggle
- Return related questions toggle

**Generation Parameters:**
- Temperature slider
- Max tokens input
- Top P slider

**Streaming Toggle:**
- Enable/disable streaming
- Streaming indicator

---

## 🔧 **IMPLEMENTATION NOTES**

### **Service Layer Structure**

```typescript
class PerplexityService extends BaseAPIService {
  constructor(apiKey?: string) {
    super('perplexity', 'https://api.perplexity.ai', apiKey)
  }

  async chatCompletion(request: PerplexityChatCompletionRequest): Promise<APIResponse<PerplexityChatCompletionResponse>>
  async streamChatCompletion(
    request: Omit<PerplexityChatCompletionRequest, 'stream'>,
    onChunk: (chunk: PerplexityChatCompletionChunk) => void
  ): Promise<APIResponse<void>>
}
```

---

## 📊 **INTEGRATION COMPLEXITY**

**Complexity:** Medium-High

**Estimated Implementation Time:**
- Service layer: 3-4 hours
- Chat interface: 5-6 hours
- Citations display: 2-3 hours
- Streaming support: 3-4 hours
- Testing: 3-4 hours
- **Total: 16-21 hours**

---

**Status:** Deep dive complete - Ready for implementation  
**Last Updated:** 2025-01-27

