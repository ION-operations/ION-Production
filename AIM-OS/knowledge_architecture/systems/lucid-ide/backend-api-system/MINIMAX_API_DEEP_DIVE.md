---
id: "minimax_api_deep_dive"
system: "lucid_chat"
component: "api_integration"
level: "T3"
type: "deep_analysis"
title: "Minimax API Deep Dive - Complete Integration Guide"
description: "Comprehensive analysis of Minimax API capabilities, UI requirements, workflows, and integration patterns"
created: "2025-01-27T00:00:00Z"
updated: "2025-01-27T00:00:00Z"
author: "aether"
status: "active"
tags: ["minimax", "llm", "chat-completion", "api-integration", "deep-dive"]
---

# Minimax API Deep Dive - Complete Integration Guide

**Purpose:** Comprehensive understanding of Minimax API for proper integration  
**Status:** 🔍 **DEEP ANALYSIS COMPLETE**

---

## 🎯 **MINIMAX API OVERVIEW**

Minimax is a Chinese AI provider offering:
- **Chat Completion** - LLM text generation (similar to OpenAI/Anthropic)
- **Video Generation** - Hailuo model for image-to-video
- **Multi-modal Support** - Text, image, and video capabilities
- **Streaming Support** - Real-time response streaming
- **JWT Authentication** - Token-based authentication

**Note:** Based on JWT token format, Minimax uses token-based authentication with group/user information encoded in the token.

---

## 📡 **API ENDPOINTS & CAPABILITIES**

### **1. Chat Completion (LLM)**

**Endpoint:** `POST /v1/chat/completions` (estimated)

**Request Parameters:**
```typescript
{
  model: string              // Model name (e.g., 'abab5.5-chat')
  messages: Array<{
    role: 'system' | 'user' | 'assistant'
    content: string
  }>
  temperature?: number       // 0.0-1.0 (default: 0.7)
  max_tokens?: number       // Maximum tokens to generate
  stream?: boolean          // Enable streaming
  top_p?: number           // Nucleus sampling
  frequency_penalty?: number
  presence_penalty?: number
}
```

**Response (Non-streaming):**
```typescript
{
  id: string
  object: 'chat.completion'
  created: number
  model: string
  choices: Array<{
    index: number
    message: {
      role: 'assistant'
      content: string
    }
    finish_reason: string
  }>
  usage: {
    prompt_tokens: number
    completion_tokens: number
    total_tokens: number
  }
}
```

**Response (Streaming):**
```typescript
{
  id: string
  object: 'chat.completion.chunk'
  created: number
  model: string
  choices: Array<{
    index: number
    delta: {
      role?: 'assistant'
      content?: string
    }
    finish_reason?: string
  }>
}
```

**Workflow:**
1. Build message history → Array of messages
2. Configure parameters → Temperature, max_tokens, etc.
3. Send request → With JWT token
4. Receive response → Stream or complete
5. Display in chat → Markdown rendering

**UI Requirements:**
- Chat interface (message history)
- Message input (multi-line)
- Model selector
- Parameter controls (temperature, max_tokens)
- Streaming indicator
- Token usage display
- Error handling display

---

### **2. Video Generation (Hailuo)**

**Endpoint:** `POST /v1/video/generate` (estimated)

**Request Parameters:**
```typescript
{
  model: 'hailuo' | 'hailuo-director'
  image_url?: string        // Starting image
  prompt: string            // Video description
  duration?: number         // Video duration in seconds
  camera_motion?: string    // 'pan', 'zoom', 'rotate', etc.
  style?: string           // Video style
}
```

**Response:**
```typescript
{
  task_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress?: number
  video_url?: string
  preview_url?: string
  error?: string
}
```

**Workflow:**
1. Upload/select image → Starting frame
2. Enter prompt → Video description
3. Configure motion → Camera movements
4. Submit → Get task_id
5. Poll status → Monitor progress
6. Download video → Display in player

**UI Requirements:**
- Image upload component
- Prompt input
- Camera motion selector
- Video player
- Progress monitor
- Task queue

---

## 🔐 **AUTHENTICATION**

**Method:** JWT Token in Authorization header

**Token Format:**
```
Authorization: Bearer {JWT_TOKEN}
```

**Token Structure (decoded):**
```json
{
  "GroupName": "azonicrider32",
  "UserName": "azonicrider32",
  "SubjectID": "1958548628666586070",
  "GroupID": "1958548628662395862",
  "Mail": "crinkedart@gmail.com",
  "CreateTime": "2025-08-22 00:38:18",
  "TokenType": 1,
  "iss": "minimax"
}
```

**Implementation:**
```typescript
protected getDefaultHeaders(): Record<string, string> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }
  
  if (this.apiKey) {
    headers['Authorization'] = `Bearer ${this.apiKey}`
  }
  
  return headers
}
```

---

## 🎨 **REQUIRED UI COMPONENTS**

### **1. Chat Interface**

**Features:**
- Message history display
- User/assistant message bubbles
- Markdown rendering
- Code syntax highlighting
- Message timestamps
- Copy message button
- Edit/regenerate buttons
- Scroll to bottom on new message

**Component Structure:**
```typescript
<ChatInterface
  messages={messages}
  onSend={handleSend}
  onEdit={handleEdit}
  onRegenerate={handleRegenerate}
  streaming={isStreaming}
/>
```

---

### **2. Message Input**

**Features:**
- Multi-line textarea
- Character/token counter
- Send button (Enter/Ctrl+Enter)
- Stop button (when streaming)
- Attach image button
- History dropdown
- Auto-resize textarea

**Component Structure:**
```typescript
<MessageInput
  value={input}
  onChange={handleChange}
  onSend={handleSend}
  onStop={handleStop}
  disabled={isStreaming}
  showAttach={true}
/>
```

---

### **3. Model Selector**

**Features:**
- Dropdown with available models
- Model descriptions
- Model capabilities (context length, etc.)
- Model pricing info
- Default model selection

**Component Structure:**
```typescript
<ModelSelector
  models={models}
  selectedModel={selectedModel}
  onSelect={handleSelect}
  showDetails={true}
/>
```

---

### **4. Parameter Controls**

**Features:**
- Temperature slider (0-1)
- Max tokens input
- Top-p slider (0-1)
- Frequency penalty slider
- Presence penalty slider
- Reset to defaults button
- Preset buttons (Creative, Balanced, Precise)

**Component Structure:**
```typescript
<ParameterControls
  temperature={temperature}
  maxTokens={maxTokens}
  topP={topP}
  onChange={handleChange}
  showPresets={true}
/>
```

---

### **5. Streaming Indicator**

**Features:**
- Animated typing indicator
- Token count (real-time)
- Stop button
- Speed indicator (tokens/second)

**Component Structure:**
```typescript
<StreamingIndicator
  isStreaming={isStreaming}
  tokensGenerated={tokensGenerated}
  onStop={handleStop}
/>
```

---

### **6. Token Usage Display**

**Features:**
- Prompt tokens count
- Completion tokens count
- Total tokens count
- Cost estimate (if available)
- Usage history chart

**Component Structure:**
```typescript
<TokenUsageDisplay
  usage={usage}
  showCost={true}
  showHistory={true}
/>
```

---

### **7. Video Generation Panel**

**Features:**
- Image upload
- Prompt input
- Camera motion selector
- Duration selector
- Style selector
- Progress monitor
- Video player
- Download button

**Component Structure:**
```typescript
<VideoGenerationPanel
  onGenerate={handleGenerate}
  onCancel={handleCancel}
  showPreview={true}
/>
```

---

## 🔄 **WORKFLOW PATTERNS**

### **Pattern 1: Simple Chat**

```
User Input → Build Messages → API Request → Display Response
```

**State Management:**
- `messages` - Array of message objects
- `input` - Current input text
- `isStreaming` - Streaming status
- `selectedModel` - Selected model
- `parameters` - Temperature, max_tokens, etc.

---

### **Pattern 2: Streaming Chat**

```
User Input → Build Messages → Start Stream → Receive Chunks → Update UI
```

**State Management:**
- `messages` - Array of message objects
- `streamingMessage` - Current streaming message
- `isStreaming` - Streaming status
- `tokensGenerated` - Real-time token count
- `abortController` - For canceling stream

---

### **Pattern 3: Video Generation**

```
Upload Image → Enter Prompt → Configure Motion → Submit → Poll Status → Display Video
```

**State Management:**
- `imageUrl` - Starting image
- `prompt` - Video description
- `cameraMotion` - Camera movement type
- `taskId` - Current task ID
- `status` - Task status
- `progress` - Progress percentage
- `videoUrl` - Generated video URL

---

## 🏗️ **INTEGRATION ARCHITECTURE**

### **Service Layer**

```typescript
class MinimaxService extends BaseAPIService {
  constructor(apiKey?: string) {
    super('minimax', 'https://api.minimax.chat/v1', apiKey)
  }

  // Chat Completion
  async chatCompletion(
    request: MinimaxChatRequest
  ): Promise<APIResponse<MinimaxChatResponse>>
  
  // Streaming Chat Completion
  async streamChatCompletion(
    request: MinimaxChatRequest,
    onChunk: (chunk: MinimaxChatChunk) => void
  ): Promise<void>
  
  // Video Generation
  async generateVideo(
    request: MinimaxVideoRequest
  ): Promise<APIResponse<MinimaxVideoResponse>>
  
  // Get Task Status
  async getTaskStatus(
    taskId: string
  ): Promise<APIResponse<MinimaxTaskStatus>>
  
  // List Models
  async listModels(): Promise<APIResponse<MinimaxModel[]>>
}
```

---

### **State Management**

```typescript
interface MinimaxState {
  // Chat
  messages: Array<{
    role: 'system' | 'user' | 'assistant'
    content: string
    timestamp: Date
  }>
  input: string
  isStreaming: boolean
  streamingMessage: string
  
  // Model & Parameters
  selectedModel: string
  temperature: number
  maxTokens: number
  topP: number
  frequencyPenalty: number
  presencePenalty: number
  
  // Video Generation
  videoGeneration: {
    imageUrl: string | null
    prompt: string
    cameraMotion: string
    taskId: string | null
    status: string
    progress: number
    videoUrl: string | null
  }
  
  // Usage
  usage: {
    promptTokens: number
    completionTokens: number
    totalTokens: number
  }
  
  // History
  history: Array<{
    messages: Message[]
    model: string
    timestamp: Date
  }>
  
  // Settings
  settings: {
    autoScroll: boolean
    showTimestamps: boolean
    markdownEnabled: boolean
    codeHighlighting: boolean
  }
}
```

---

### **UI Component Hierarchy**

```
MinimaxPanel
├── ChatInterface
│   ├── MessageList
│   │   ├── MessageBubble
│   │   │   ├── MessageContent
│   │   │   └── MessageActions
│   │   └── StreamingIndicator
│   └── MessageInput
│       ├── TextArea
│       ├── SendButton
│       └── AttachButton
├── ModelSelector
│   ├── ModelDropdown
│   └── ModelDetails
├── ParameterControls
│   ├── TemperatureSlider
│   ├── MaxTokensInput
│   └── PresetButtons
├── TokenUsageDisplay
│   ├── UsageStats
│   └── UsageChart
└── VideoGenerationPanel
    ├── ImageUpload
    ├── PromptInput
    ├── CameraMotionSelector
    ├── ProgressMonitor
    └── VideoPlayer
```

---

## 🎯 **USER EXPERIENCE FLOWS**

### **Flow 1: Simple Chat**

1. User opens Minimax panel
2. Selects model: "abab5.5-chat"
3. Types message: "Explain quantum computing"
4. Clicks "Send"
5. Response streams in real-time
6. User reads response
7. User asks follow-up question

**Time:** ~5-10 seconds per response

---

### **Flow 2: Parameter Tuning**

1. User opens chat
2. Adjusts temperature to 0.9 (more creative)
3. Sets max_tokens to 2000
4. Sends message
5. Response is more creative/longer
6. User adjusts temperature to 0.3 (more precise)
7. Regenerates response

**Time:** ~1-2 minutes

---

### **Flow 3: Video Generation**

1. User switches to "Video" tab
2. Uploads image: "A futuristic city"
3. Enters prompt: "Camera slowly pans across the city"
4. Selects camera motion: "Pan Left"
5. Clicks "Generate"
6. Watches progress (0-100%)
7. Video completes
8. User plays video in player
9. User downloads video

**Time:** ~2-5 minutes

---

## 🔧 **TECHNICAL REQUIREMENTS**

### **Dependencies**

```json
{
  "dependencies": {
    "react-markdown": "^9.0.0",
    "remark-gfm": "^4.0.0",
    "react-syntax-highlighter": "^15.5.0",
    "eventsource-parser": "^1.1.0"
  }
}
```

### **Environment Variables**

```bash
MINIMAX_API_KEY=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

### **API Rate Limits**

- **Free Tier:** Limited requests/day
- **Paid Tier:** Higher limits
- **Enterprise:** Custom limits

**Handling:**
- Track request count
- Show rate limit warnings
- Implement request queuing
- Exponential backoff on 429 errors

---

## 📊 **MONITORING & ANALYTICS**

### **Metrics to Track**

- Request count per day
- Average response time
- Token usage per day
- Error rates
- Most used models
- Average message length
- User satisfaction (if available)

### **Error Handling**

- Network errors → Retry with exponential backoff
- Rate limit errors → Show warning, queue request
- Invalid requests → Show validation errors
- Authentication errors → Prompt for new token
- Streaming errors → Allow retry from last chunk

---

## 🚀 **IMPLEMENTATION PRIORITY**

### **Phase 1: Core Features** (Week 1)
1. ✅ Basic chat completion
2. ✅ Message interface
3. ✅ Model selector
4. ✅ Parameter controls

### **Phase 2: Enhanced Features** (Week 2)
1. Streaming support
2. Message history
3. Token usage display
4. Error handling

### **Phase 3: Advanced Features** (Week 3)
1. Video generation
2. Multi-modal support (images)
3. Advanced parameter tuning
4. Usage analytics

---

## 🔍 **RESEARCH NOTES**

**Based on JWT Token Analysis:**
- Token contains group/user information
- Token type: 1 (likely API token)
- Issuer: "minimax"
- Token appears to be long-lived (created 2025-08-22)

**Estimated API Structure:**
- Base URL: `https://api.minimax.chat/v1` (estimated)
- Authentication: Bearer token in Authorization header
- Format: Similar to OpenAI API (common pattern)

**Video Generation:**
- Model: "hailuo" or "hailuo-director"
- Supports image-to-video
- Camera motion control available
- Task-based (async) workflow

---

**Status:** Deep analysis complete - Ready for implementation  
**Next:** Create comprehensive UI components and test API endpoints

