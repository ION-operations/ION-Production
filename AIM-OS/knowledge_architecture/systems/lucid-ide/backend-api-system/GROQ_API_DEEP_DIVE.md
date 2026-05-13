---
id: "groq_api_deep_dive"
system: "lucid_chat"
component: "api_integration"
level: "T3"
type: "deep_analysis"
title: "Groq API Deep Dive - Complete Integration Guide"
description: "Comprehensive analysis of Groq API capabilities - ultra-fast LLM inference with free tier"
created: "2025-01-27T00:00:00Z"
updated: "2025-01-27T00:00:00Z"
author: "aether"
status: "active"
tags: ["groq", "llm", "fast-inference", "free-tier", "api-integration", "deep-dive"]
---

# Groq API Deep Dive - Complete Integration Guide

**Purpose:** Comprehensive understanding of Groq API for proper integration  
**Status:** 🔍 **DEEP ANALYSIS COMPLETE**  
**Official Documentation:** https://console.groq.com/docs

---

## 🎯 **GROQ API OVERVIEW**

Groq provides ultra-fast LLM inference:
- **Chat Completions** - Multiple models (Llama, Mixtral, Gemma, etc.)
- **Ultra-Fast Inference** - Fastest inference speeds
- **Free Tier** - Generous free tier
- **OpenAI-Compatible** - OpenAI API compatibility
- **Multiple Models** - Access to various open models

**Key Features:**
- Fastest inference speeds
- Free tier available
- OpenAI-compatible API
- Multiple model options
- Streaming support

---

## 🔐 **AUTHENTICATION**

**Method:** Bearer Token (API Key)

**Header:**
```
Authorization: Bearer YOUR_API_KEY
```

**API Key Management:**
- Obtain from: https://console.groq.com
- Store securely in environment variable: `GROQ_API_KEY`
- Free tier: 14,400 requests/day

**Base URL:**
```
https://api.groq.com/openai/v1
```

---

## 📡 **API ENDPOINTS & CAPABILITIES**

### **1. Chat Completions**

**Endpoint:** `POST https://api.groq.com/openai/v1/chat/completions`

**Purpose:** Chat with models (OpenAI-compatible)

**Request Parameters:**

```typescript
interface GroqChatCompletionRequest {
  // Required
  model: 'llama-3.1-70b-versatile' | 'llama-3.1-8b-instant' | 'mixtral-8x7b-32768' | 'gemma-7b-it' | 'llama-3-70b-8192' | string
  
  // Required
  messages: Array<{
    role: 'system' | 'user' | 'assistant'
    content: string
  }>
  
  // Optional - Generation Parameters
  temperature?: number              // 0-2 (default: 1.0)
  top_p?: number                    // 0-1 (default: 1.0)
  max_tokens?: number               // Max tokens to generate
  stream?: boolean                  // Stream responses
  stop?: string | string[]          // Stop sequences
  presence_penalty?: number         // -2 to 2
  frequency_penalty?: number        // -2 to 2
  logit_bias?: Record<string, number>
  user?: string
  
  // Optional - Response Format
  response_format?: {
    type: 'text' | 'json_object'
  }
}
```

**Available Models:**
- `llama-3.1-70b-versatile` - Most capable
- `llama-3.1-8b-instant` - Fast, efficient
- `mixtral-8x7b-32768` - Mixtral with 32K context
- `gemma-7b-it` - Google Gemma
- `llama-3-70b-8192` - Llama 3 with 8K context
- And more...

**Response Structure:**

```typescript
interface GroqChatCompletionResponse {
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

### **2. List Models**

**Endpoint:** `GET https://api.groq.com/openai/v1/models`

**Purpose:** List available models

---

## 🔄 **WORKFLOWS**

### **Workflow 1: Fast Chat Completion**

1. User enters message
2. Select model
3. Configure parameters
4. Enable streaming (optional)
5. Submit → Get ultra-fast response
6. Display result

---

## ⚡ **RATE LIMITS**

**Free Tier:**
- 14,400 requests/day
- 30 requests/minute

**Paid Tier:**
- Higher limits
- Pay-per-use pricing

---

## 💰 **PRICING**

**Free Tier:**
- 14,400 requests/day
- Free forever

**Paid Tier:**
- Pay-per-use
- Very competitive pricing
- Check Groq pricing page for current rates

---

## 🎨 **UI COMPONENT REQUIREMENTS**

### **Chat Panel**

**Model Selector:**
- Dropdown with Groq models
- Speed indicator (ultra-fast)

**Chat Interface:**
- Message list
- User/assistant messages
- Speed indicator
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
class GroqService extends BaseAPIService {
  constructor(apiKey?: string) {
    super('groq', 'https://api.groq.com/openai/v1', apiKey)
  }

  // OpenAI-compatible methods
  async chatCompletion(request: GroqChatCompletionRequest): Promise<APIResponse<GroqChatCompletionResponse>>
  async streamChatCompletion(
    request: Omit<GroqChatCompletionRequest, 'stream'>,
    onChunk: (chunk: GroqChatCompletionChunk) => void
  ): Promise<APIResponse<void>>
  async listModels(): Promise<APIResponse<any>>
}
```

**OpenAI Compatibility:**

Since Groq is OpenAI-compatible, you can use OpenAI SDK:

```typescript
import OpenAI from 'openai'

const client = new OpenAI({
  apiKey: process.env.GROQ_API_KEY,
  baseURL: 'https://api.groq.com/openai/v1',
})
```

---

## 📊 **INTEGRATION COMPLEXITY**

**Complexity:** Low (OpenAI-compatible)

**Estimated Implementation Time:**
- Service layer: 2-3 hours (can use OpenAI SDK)
- UI components: 4-5 hours
- Streaming support: 2-3 hours
- Testing: 2-3 hours
- **Total: 10-14 hours**

---

**Status:** Deep dive complete - Ready for implementation  
**Last Updated:** 2025-01-27

