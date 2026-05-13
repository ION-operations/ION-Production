---
id: "deepl_api_deep_dive"
system: "lucid_chat"
component: "api_integration"
level: "T3"
type: "deep_analysis"
title: "DeepL API Deep Dive - Complete Integration Guide"
description: "Comprehensive analysis of DeepL API capabilities, endpoints, parameters, workflows, and integration patterns"
created: "2025-01-27T00:00:00Z"
updated: "2025-01-27T00:00:00Z"
author: "aether"
status: "active"
tags: ["deepl", "translation", "api-integration", "deep-dive"]
---

# DeepL API Deep Dive - Complete Integration Guide

**Purpose:** Comprehensive understanding of DeepL API for proper integration  
**Status:** 🔍 **DEEP ANALYSIS COMPLETE**  
**Official Documentation:** https://www.deepl.com/docs-api

---

## 🎯 **DEEPL API OVERVIEW**

DeepL provides high-quality translation:
- **Text Translation** - Translate text between languages
- **Document Translation** - Translate entire documents
- **Glossary Support** - Custom glossaries
- **Formality Control** - Control formality level
- **30+ Languages** - Support for 30+ languages

**Key Features:**
- Highest quality translations
- Formality control
- Glossary support
- Document translation
- Usage statistics

---

## 🔐 **AUTHENTICATION**

**Method:** API Key (Header)

**Header:**
```
Authorization: DeepL-Auth-Key YOUR_API_KEY
```

**API Key Management:**
- Obtain from: DeepL API dashboard
- Store securely in environment variable: `DEEPL_API_KEY`
- Free tier: 500,000 characters/month

**Base URL:**
```
https://api-free.deepl.com/v2  (Free tier)
https://api.deepl.com/v2        (Paid tier)
```

---

## 📡 **API ENDPOINTS & CAPABILITIES**

### **1. Translate Text**

**Endpoint:** `POST https://api.deepl.com/v2/translate`

**Purpose:** Translate text

**Request Parameters:**

```typescript
interface DeepLTranslateRequest {
  // Required
  text: string | string[]           // Text(s) to translate
  target_lang: string                // Target language code (e.g., 'EN', 'ES', 'FR')
  
  // Optional
  source_lang?: string               // Source language code (auto-detect if not provided)
  split_sentences?: '0' | '1' | 'nonewlines'  // Sentence splitting (default: '1')
  preserve_formatting?: '0' | '1'    // Preserve formatting (default: '0')
  formality?: 'default' | 'more' | 'less' | 'prefer_more' | 'prefer_less'
  glossary_id?: string               // Glossary ID
  tag_handling?: string              // XML/HTML tag handling
  outline_detection?: '0' | '1'      // Outline detection (default: '1')
  non_splitting_tags?: string        // Comma-separated XML tags
  splitting_tags?: string            // Comma-separated XML tags
  ignore_tags?: string               // Comma-separated XML tags
}
```

**Headers:**
```
Authorization: DeepL-Auth-Key YOUR_API_KEY
Content-Type: application/x-www-form-urlencoded
```

**Response Structure:**

```typescript
interface DeepLTranslateResponse {
  translations: Array<{
    detected_source_language?: string
    text: string
  }>
}
```

---

### **2. List Supported Languages**

**Endpoint:** `GET https://api.deepl.com/v2/languages`

**Purpose:** List supported languages

**Query Parameters:**

```typescript
interface DeepLLanguagesRequest {
  type?: 'source' | 'target'         // Language type (default: both)
}
```

**Response:**

```typescript
interface DeepLLanguagesResponse extends Array<{
  language: string                   // Language code
  name: string                       // Language name
}>
```

---

### **3. Usage Statistics**

**Endpoint:** `GET https://api.deepl.com/v2/usage`

**Purpose:** Get usage statistics

**Response:**

```typescript
interface DeepLUsageResponse {
  character_count: number            // Characters used
  character_limit: number            // Character limit
}
```

---

### **4. Translate Document**

**Endpoint:** `POST https://api.deepl.com/v2/document`

**Purpose:** Upload document for translation

**Request:** Multipart form data

**Response:**

```typescript
interface DeepLDocumentResponse {
  document_id: string
  document_key: string
}
```

---

## 🔄 **WORKFLOWS**

### **Workflow 1: Translate Text**

1. User enters text
2. Select source language (or auto-detect)
3. Select target language
4. Configure formality
5. Submit → Display translation

### **Workflow 2: Document Translation**

1. User uploads document
2. Select source and target languages
3. Submit → Get document ID
4. Poll status → Download translated document

---

## ⚡ **RATE LIMITS**

**Free Tier:**
- 500,000 characters/month
- Rate limits apply

**Paid Tier:**
- Higher limits
- No rate limits (Pro)

---

## 💰 **PRICING**

**Free Tier:**
- 500,000 characters/month
- Free forever

**Paid Tier:**
- €4.99/month for Starter
- Higher character limits

---

## 🎨 **UI COMPONENT REQUIREMENTS**

### **Translation Panel**

**Source Language:**
- Language selector
- Auto-detect toggle

**Target Language:**
- Language selector

**Text Input:**
- Source textarea
- Character counter

**Formality Control:**
- Formality selector (default/more/less)

**Translate Button:**
- Show loading state

**Translation Display:**
- Translated text
- Detected language
- Copy button
- Swap languages button

**Usage Display:**
- Character count
- Character limit
- Usage percentage

---

## 🔧 **IMPLEMENTATION NOTES**

### **Service Layer Structure**

```typescript
class DeepLService extends BaseAPIService {
  constructor(apiKey?: string, isFree: boolean = false) {
    const baseURL = isFree ? 'https://api-free.deepl.com/v2' : 'https://api.deepl.com/v2'
    super('deepl', baseURL, apiKey)
  }

  protected getDefaultHeaders(): Record<string, string> {
    return {
      'Authorization': `DeepL-Auth-Key ${this.apiKey}`,
      'Content-Type': 'application/x-www-form-urlencoded',
    }
  }

  async translate(request: DeepLTranslateRequest): Promise<APIResponse<DeepLTranslateResponse>>
  async listLanguages(type?: 'source' | 'target'): Promise<APIResponse<DeepLLanguagesResponse>>
  async getUsage(): Promise<APIResponse<DeepLUsageResponse>>
  async translateDocument(file: File, targetLang: string, sourceLang?: string): Promise<APIResponse<DeepLDocumentResponse>>
  
  // Helpers
  async translateText(text: string, targetLang: string, sourceLang?: string, formality?: string): Promise<APIResponse<string>>
}
```

---

## 📊 **INTEGRATION COMPLEXITY**

**Complexity:** Low-Medium

**Estimated Implementation Time:**
- Service layer: 3-4 hours
- UI components: 4-5 hours
- Document translation: 3-4 hours
- Testing: 2-3 hours
- **Total: 12-16 hours**

---

**Status:** Deep dive complete - Ready for implementation  
**Last Updated:** 2025-01-27

