---
id: "eden_ai_api_deep_dive"
system: "lucid_chat"
component: "api_integration"
level: "T3"
type: "deep_analysis"
title: "Eden AI API Deep Dive - Complete Integration Guide"
description: "Comprehensive analysis of Eden AI API capabilities - unified access to multiple AI providers with free tier"
created: "2025-01-27T00:00:00Z"
updated: "2025-01-27T00:00:00Z"
author: "aether"
status: "active"
tags: ["eden-ai", "unified-api", "multi-provider", "free-tier", "api-integration", "deep-dive"]
---

# Eden AI API Deep Dive - Complete Integration Guide

**Purpose:** Comprehensive understanding of Eden AI API for proper integration  
**Status:** 🔍 **DEEP ANALYSIS COMPLETE**  
**Official Documentation:** https://docs.edenai.co

---

## 🎯 **EDEN AI API OVERVIEW**

Eden AI provides unified access to multiple AI providers:
- **Text Analysis** - Sentiment, entity extraction, keyword extraction
- **Image Analysis** - Object detection, face detection, OCR
- **Speech** - Speech-to-text, text-to-speech
- **Translation** - Language translation
- **Text Generation** - LLM access
- **Image Generation** - Image generation
- **Video Analysis** - Video analysis
- **Multiple Providers** - Access to 50+ AI providers
- **Free Tier** - 1 request/second free

**Key Features:**
- Unified API for 50+ providers
- Automatic provider fallback
- Free tier available
- Single API key
- Provider comparison

---

## 🔐 **AUTHENTICATION**

**Method:** API Key

**Header:**
```
Authorization: Bearer YOUR_API_KEY
```

**API Key Management:**
- Obtain from: https://app.edenai.run/user/register
- Store securely in environment variable: `EDEN_AI_API_KEY`
- Free tier: 1 request/second

**Base URL:**
```
https://api.edenai.run/v2
```

---

## 📡 **API ENDPOINTS & CAPABILITIES**

### **1. Text Analysis**

**Endpoint:** `POST https://api.edenai.run/v2/text/sentiment_analysis`

**Purpose:** Sentiment analysis

**Request Parameters:**

```typescript
interface EdenAISentimentAnalysisRequest {
  texts: string[]                   // Required
  providers?: string[]              // Provider names (e.g., ['amazon', 'google', 'ibm'])
  language?: string                  // Language code
  fallback_providers?: string[]     // Fallback providers
  show_original_response?: boolean   // Show original provider response
}
```

**Available Providers:**
- Amazon Comprehend
- Google Cloud Natural Language
- IBM Watson
- Microsoft Azure
- OpenAI
- And more...

**Response:**

```typescript
interface EdenAISentimentAnalysisResponse {
  results: Record<string, {        // Provider name -> result
    status: 'success' | 'error'
    sentiment: number              // -1 to 1
    sentiment_label: 'positive' | 'negative' | 'neutral'
    items?: Array<{
      sentiment: number
      sentiment_label: string
      text: string
    }>
    original_response?: any
    error?: {
      error: string
    }
  }>
  meta: {
    provider: string
    rate: {
      limit: number
      remaining: number
      reset: string
    }
  }
}
```

---

### **2. Entity Extraction**

**Endpoint:** `POST https://api.edenai.run/v2/text/named_entity_recognition`

**Purpose:** Extract entities from text

**Request:**

```typescript
interface EdenAIEntityExtractionRequest {
  texts: string[]                   // Required
  providers?: string[]
  language?: string
  fallback_providers?: string[]
}
```

---

### **3. Object Detection**

**Endpoint:** `POST https://api.edenai.run/v2/image/object_detection`

**Purpose:** Detect objects in images

**Request:**

```typescript
interface EdenAIObjectDetectionRequest {
  providers?: string[]
  file?: File                      // Image file
  file_url?: string                // Image URL
  fallback_providers?: string[]
}
```

---

### **4. OCR**

**Endpoint:** `POST https://api.edenai.run/v2/ocr/ocr`

**Purpose:** Extract text from images

**Request:**

```typescript
interface EdenAIOCRRequest {
  providers?: string[]
  file?: File
  file_url?: string
  language?: string
  fallback_providers?: string[]
}
```

---

### **5. Speech-to-Text**

**Endpoint:** `POST https://api.edenai.run/v2/audio/speech_to_text_async`

**Purpose:** Transcribe audio

**Request:**

```typescript
interface EdenAISpeechToTextRequest {
  providers?: string[]
  file?: File
  file_url?: string
  language?: string
  speakers?: number                // Number of speakers
  fallback_providers?: string[]
}
```

---

### **6. Text-to-Speech**

**Endpoint:** `POST https://api.edenai.run/v2/audio/text_to_speech`

**Purpose:** Generate speech

**Request:**

```typescript
interface EdenAITextToSpeechRequest {
  providers?: string[]
  text: string                     // Required
  language?: string
  option?: string                  // Voice option
  fallback_providers?: string[]
}
```

---

### **7. Translation**

**Endpoint:** `POST https://api.edenai.run/v2/translation/automatic_translation`

**Purpose:** Translate text

**Request:**

```typescript
interface EdenAITranslationRequest {
  providers?: string[]
  texts: string[]                  // Required
  source_language?: string
  target_language: string          // Required
  fallback_providers?: string[]
}
```

---

### **8. Text Generation**

**Endpoint:** `POST https://api.edenai.run/v2/text/generation`

**Purpose:** Generate text with LLMs

**Request:**

```typescript
interface EdenAITextGenerationRequest {
  providers?: string[]
  text: string                     // Required: Prompt
  max_tokens?: number
  temperature?: number
  fallback_providers?: string[]
}
```

---

### **9. Image Generation**

**Endpoint:** `POST https://api.edenai.run/v2/image/generation`

**Purpose:** Generate images

**Request:**

```typescript
interface EdenAIImageGenerationRequest {
  providers?: string[]
  text: string                     // Required: Prompt
  resolution?: string
  num_images?: number
  fallback_providers?: string[]
}
```

---

### **10. List Providers**

**Endpoint:** `GET https://api.edenai.run/v2/providers`

**Purpose:** List available providers

---

## 🔄 **WORKFLOWS**

### **Workflow 1: Multi-Provider Comparison**

1. User selects task (e.g., sentiment analysis)
2. Select multiple providers
3. Submit request
4. Compare results from all providers
5. Display comparison

### **Workflow 2: Automatic Fallback**

1. User selects primary provider
2. Configure fallback providers
3. Submit request
4. If primary fails → Use fallback
5. Display result

---

## ⚡ **RATE LIMITS**

**Free Tier:**
- 1 request/second
- No credit card required

**Paid Tier:**
- Higher limits
- Pay-per-use pricing

---

## 💰 **PRICING**

**Free Tier:**
- 1 request/second
- Free forever

**Paid Tier:**
- Pay-per-use
- Pricing varies by provider
- Check Eden AI pricing page for current rates

---

## 🎨 **UI COMPONENT REQUIREMENTS**

### **Provider Selection Panel**

**Provider Browser:**
- List all providers
- Filter by capability
- Provider comparison
- "Select Provider" button

**Provider Cards:**
- Provider name
- Capabilities
- Pricing info
- Performance metrics

### **Task Panel**

**Task Selector:**
- Task type dropdown
- Provider selector (multi-select)
- Fallback configuration

**Input Area:**
- Task-specific input
- File upload (if applicable)

**Submit Button:**
- Show loading state

**Results Display:**
- Provider comparison view
- Individual provider results
- Best result highlight
- Fallback indicator

---

## 🔧 **IMPLEMENTATION NOTES**

### **Service Layer Structure**

```typescript
class EdenAIService extends BaseAPIService {
  constructor(apiKey?: string) {
    super('eden-ai', 'https://api.edenai.run/v2', apiKey)
  }

  async sentimentAnalysis(request: EdenAISentimentAnalysisRequest): Promise<APIResponse<EdenAISentimentAnalysisResponse>>
  async entityExtraction(request: EdenAIEntityExtractionRequest): Promise<APIResponse<any>>
  async objectDetection(request: EdenAIObjectDetectionRequest): Promise<APIResponse<any>>
  async ocr(request: EdenAIOCRRequest): Promise<APIResponse<any>>
  async speechToText(request: EdenAISpeechToTextRequest): Promise<APIResponse<any>>
  async textToSpeech(request: EdenAITextToSpeechRequest): Promise<APIResponse<any>>
  async translate(request: EdenAITranslationRequest): Promise<APIResponse<any>>
  async generateText(request: EdenAITextGenerationRequest): Promise<APIResponse<any>>
  async generateImage(request: EdenAIImageGenerationRequest): Promise<APIResponse<any>>
  async listProviders(): Promise<APIResponse<any>>
  
  // Helper methods
  compareProviders(task: string, providers: string[], input: any): Promise<APIResponse<any>>
}
```

---

## 📊 **INTEGRATION COMPLEXITY**

**Complexity:** High

**Dependencies:**
- Provider discovery system
- Multi-provider comparison
- Fallback handling
- Provider-specific result normalization

**Estimated Implementation Time:**
- Service layer: 10-12 hours
- Provider browser: 8-10 hours
- Task panels: 10-12 hours
- Comparison UI: 6-8 hours
- Fallback logic: 4-6 hours
- Testing: 6-8 hours
- **Total: 44-56 hours**

---

**Status:** Deep dive complete - Ready for implementation  
**Last Updated:** 2025-01-27

