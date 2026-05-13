---
id: "assembly_ai_api_deep_dive"
system: "lucid_chat"
component: "api_integration"
level: "T3"
type: "deep_analysis"
title: "Assembly AI API Deep Dive - Complete Integration Guide"
description: "Comprehensive analysis of Assembly AI API capabilities - advanced speech recognition with generous free tier"
created: "2025-01-27T00:00:00Z"
updated: "2025-01-27T00:00:00Z"
author: "aether"
status: "active"
tags: ["assembly-ai", "speech-recognition", "asr", "free-tier", "api-integration", "deep-dive"]
---

# Assembly AI API Deep Dive - Complete Integration Guide

**Purpose:** Comprehensive understanding of Assembly AI API for proper integration  
**Status:** 🔍 **DEEP ANALYSIS COMPLETE**  
**Official Documentation:** https://www.assemblyai.com/docs

---

## 🎯 **ASSEMBLY AI API OVERVIEW**

Assembly AI provides advanced speech recognition:
- **Transcription** - High-accuracy speech-to-text
- **Speaker Diarization** - Identify different speakers
- **Sentiment Analysis** - Analyze sentiment in speech
- **Entity Detection** - Detect entities in speech
- **Topic Detection** - Detect topics
- **PII Redaction** - Redact PII automatically
- **Auto Chapters** - Automatic chapter generation
- **Free Tier** - 416 free hours/month

**Key Features:**
- High accuracy transcription
- Speaker diarization
- Sentiment analysis
- PII redaction
- Auto chapters
- Generous free tier

---

## 🔐 **AUTHENTICATION**

**Method:** API Key

**Header:**
```
authorization: YOUR_API_KEY
```

**API Key Management:**
- Obtain from: https://www.assemblyai.com/app/account
- Store securely in environment variable: `ASSEMBLY_AI_API_KEY`
- Free tier: 416 hours/month

**Base URL:**
```
https://api.assemblyai.com/v2
```

---

## 📡 **API ENDPOINTS & CAPABILITIES**

### **1. Submit Transcription**

**Endpoint:** `POST https://api.assemblyai.com/v2/transcript`

**Purpose:** Submit audio for transcription

**Request Parameters:**

```typescript
interface AssemblyAITranscriptionRequest {
  // Required (one of)
  audio_url?: string                 // URL to audio file
  audio_data?: string                // Base64 encoded audio
  
  // Optional - Transcription Settings
  language_code?: string             // Language code (e.g., 'en', 'es', 'fr')
  speaker_labels?: boolean           // Enable speaker diarization (default: false)
  speakers_expected?: number         // Expected number of speakers
  
  // Optional - Advanced Features
  sentiment_analysis?: boolean       // Analyze sentiment (default: false)
  entity_detection?: boolean        // Detect entities (default: false)
  iab_categories?: boolean          // Detect IAB categories (default: false)
  auto_chapters?: boolean           // Generate auto chapters (default: false)
  summarization?: boolean           // Generate summary
  summary_model?: 'informative' | 'conversational' | 'catchy'
  summary_type?: 'bullets' | 'headline' | 'paragraph'
  
  // Optional - PII Redaction
  redact_pii?: boolean              // Redact PII (default: false)
  redact_pii_policies?: Array<'phone_number' | 'ssn' | 'credit_card' | 'bank_account' | 'email' | 'person_name' | 'date_of_birth' | 'address' | 'drivers_license' | 'medical_record' | 'us_passport' | 'credit_card_cvv' | 'nationality' | 'event' | 'language' | 'location' | 'money_amount' | 'person_age' | 'organization' | 'percent' | 'political_affiliation' | 'religion' | 'state' | 'time' | 'url' | 'username' | 'zip_code'>
  redact_pii_sub?: 'entity_type' | 'hash' | 'entity_name'
  
  // Optional - Custom Vocabulary
  word_boost?: string[]             // Words to boost
  boost_param?: 'default' | 'high'  // Boost parameter
  
  // Optional - Filtering
  filter_profanity?: boolean        // Filter profanity (default: false)
  disfluencies?: boolean            // Include disfluencies (default: false)
  punctuate?: boolean               // Add punctuation (default: true)
  format_text?: boolean             // Format text (default: true)
  
  // Optional - Other
  dual_channel?: boolean            // Dual channel audio
  audio_start_from?: number         // Start time (ms)
  audio_end_at?: number             // End time (ms)
  webhook_url?: string              // Webhook URL
  webhook_auth_header_name?: string // Webhook auth header
  webhook_auth_header_value?: string // Webhook auth header value
}
```

**Response:**

```typescript
interface AssemblyAITranscriptionResponse {
  id: string                        // Transcript ID
  status: 'queued' | 'processing' | 'completed' | 'error'
  audio_url?: string
  text?: string                     // Transcribed text (when completed)
  words?: Array<{
    text: string
    start: number                   // Start time (ms)
    end: number                     // End time (ms)
    confidence: number
    speaker?: string                // Speaker label (if speaker_labels enabled)
  }>
  utterances?: Array<{              // Speaker diarization
    start: number
    end: number
    confidence: number
    speaker: string
    text: string
    words: Array<{
      text: string
      start: number
      end: number
      confidence: number
    }>
  }>
  sentiment_analysis_results?: Array<{
    text: string
    start: number
    end: number
    confidence: number
    sentiment: 'POSITIVE' | 'NEGATIVE' | 'NEUTRAL'
  }>
  entities?: Array<{
    entity_type: string
    text: string
    start: number
    end: number
  }>
  iab_categories_result?: {
    status: string
    results: Array<{
      text: string
      labels: Array<{
        relevance: number
        label: string
      }>
      timestamp: {
        start: number
        end: number
      }
    }>
    summary: Record<string, number>
  }
  chapters?: Array<{
    headlines: string[]
    summary: string
    gist: string
    start: number
    end: number
  }>
  summary?: string
  error?: string
}
```

---

### **2. Get Transcription**

**Endpoint:** `GET https://api.assemblyai.com/v2/transcript/{transcript_id}`

**Purpose:** Get transcription status and results

---

### **3. List Transcriptions**

**Endpoint:** `GET https://api.assemblyai.com/v2/transcript`

**Purpose:** List all transcriptions

**Query Parameters:**

```typescript
interface AssemblyAIListTranscriptionsRequest {
  limit?: number                    // Results per page (default: 10)
  status?: 'queued' | 'processing' | 'completed' | 'error'
  created_on?: string               // Filter by date
}
```

---

### **4. Delete Transcription**

**Endpoint:** `DELETE https://api.assemblyai.com/v2/transcript/{transcript_id}`

**Purpose:** Delete transcription

---

### **5. Upload Audio**

**Endpoint:** `POST https://api.assemblyai.com/v2/upload`

**Purpose:** Upload audio file

**Request:** Multipart form data

**Response:**

```typescript
interface AssemblyAIUploadResponse {
  upload_url: string                // Use this URL in transcription request
}
```

---

## 🔄 **WORKFLOWS**

### **Workflow 1: Basic Transcription**

1. User uploads audio file
2. Submit transcription request
3. Poll for completion
4. Display transcribed text

### **Workflow 2: Advanced Transcription**

1. User uploads audio file
2. Enable features:
   - Speaker diarization
   - Sentiment analysis
   - Auto chapters
   - PII redaction
3. Submit → Poll → Display results
4. Show speakers, sentiment, chapters

---

## ⚡ **RATE LIMITS**

**Free Tier:**
- 416 hours/month free
- No credit card required

**Paid Tier:**
- Higher limits
- Pay-per-use pricing

---

## 💰 **PRICING**

**Free Tier:**
- 416 hours/month free
- Free forever

**Paid Tier:**
- $0.00025 per second (~$0.90/hour)
- Check Assembly AI pricing page for current rates

---

## 🎨 **UI COMPONENT REQUIREMENTS**

### **Transcription Panel**

**Audio Upload:**
- File upload
- URL input
- Audio player
- Recording option

**Feature Toggles:**
- Speaker diarization
- Sentiment analysis
- Entity detection
- Auto chapters
- PII redaction
- Custom vocabulary

**Transcribe Button:**
- Show loading state
- Progress indicator

**Results Display:**
- Transcribed text
- Speaker labels (if enabled)
- Sentiment indicators (if enabled)
- Chapters (if enabled)
- Word-level timestamps
- Download transcript

---

## 🔧 **IMPLEMENTATION NOTES**

### **Service Layer Structure**

```typescript
class AssemblyAIService extends BaseAPIService {
  constructor(apiKey?: string) {
    super('assembly-ai', 'https://api.assemblyai.com/v2', apiKey)
  }

  protected getDefaultHeaders(): Record<string, string> {
    return {
      'authorization': this.apiKey!,
      'Content-Type': 'application/json',
    }
  }

  async submitTranscription(request: AssemblyAITranscriptionRequest): Promise<APIResponse<AssemblyAITranscriptionResponse>>
  async getTranscription(transcriptId: string): Promise<APIResponse<AssemblyAITranscriptionResponse>>
  async pollTranscription(
    transcriptId: string,
    onProgress?: (status: string) => void,
    interval?: number
  ): Promise<APIResponse<AssemblyAITranscriptionResponse>>
  async listTranscriptions(options?: AssemblyAIListTranscriptionsRequest): Promise<APIResponse<any>>
  async deleteTranscription(transcriptId: string): Promise<APIResponse<void>>
  async uploadAudio(file: File): Promise<APIResponse<AssemblyAIUploadResponse>>
}
```

---

## 📊 **INTEGRATION COMPLEXITY**

**Complexity:** Medium-High

**Dependencies:**
- Audio handling
- Polling mechanism
- Speaker diarization visualization
- Sentiment visualization

**Estimated Implementation Time:**
- Service layer: 6-8 hours
- Upload UI: 4-6 hours
- Transcription UI: 6-8 hours
- Advanced features UI: 6-8 hours
- Polling logic: 3-4 hours
- Testing: 4-6 hours
- **Total: 29-40 hours**

---

**Status:** Deep dive complete - Ready for implementation  
**Last Updated:** 2025-01-27

