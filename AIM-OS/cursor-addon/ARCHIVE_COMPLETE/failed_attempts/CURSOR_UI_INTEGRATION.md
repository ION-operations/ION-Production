# Cursor UI Panel Integration - Complete Guide

**Date:** 2025-01-27
**Author:** Opus 4.1
**Status:** Integration Architecture Documented

---

## Executive Summary

The Cursor UI Panel provides the user interface connecting React frontend to all AIM-OS backend systems through a comprehensive service layer.

---

## Integration Architecture

### Layer Structure

`
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  Cursor Extension (React UI)                        â”‚
â”‚  â”œâ”€ MainDashboard (6 tabs)                         â”‚
â”‚  â”œâ”€ Service Layer (AIMOSService.ts)                â”‚
â”‚  â””â”€ Webview Providers                              â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                 â†“ HTTP/WebSocket
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  Backend Services                                    â”‚
â”‚  â”œâ”€ MCP Server (port 8000)                         â”‚
â”‚  â”œâ”€ Daemon (port 5000)                             â”‚
â”‚  â”œâ”€ RAG MCP (port 8001)                            â”‚
â”‚  â””â”€ Voice I/O - TTS/SST                            â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                 â†“
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  AIM-OS Core Systems                                â”‚
â”‚  CMC | HHNI | VIF | APOE | SEG | SDF-CVF          â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
`

---

## Service Layer (AIMOSService.ts)

**Size:** 900+ lines
**Purpose:** Complete integration layer for all AIM-OS systems

### Core Methods

#### Memory Operations
- storeMemory(content, tags) â†’ CMC
- retrieveMemory(query) â†’ HHNI
- getMemoryStats() â†’ CMC statistics

#### Planning & Orchestration
- createPlan(goal, context) â†’ APOE
- trackConfidence(task, confidence) â†’ VIF
- getConfidenceHistory() â†’ VIF history

#### Knowledge Synthesis
- synthesizeKnowledge(inputs) â†’ SEG
- getKnowledgeGraph() â†’ SEG visualization

#### Voice I/O
- textToSpeech(text) â†’ Web Speech API
- speechToText() â†’ Web Speech Recognition
- startRecording() / stopRecording()

---

## React Components

### MainDashboard
**Location:** packages/ide_chat_app/src/components/MainDashboard.tsx

**Tabs:**
1. Agents - Agent management interface
2. Chat - Multi-AI conversation
3. Chains - Tool chain execution
4. Tools - MCP tool interface
5. Timeline - Temporal history view
6. NL Tags - Natural language tagging

### Supporting Components
- MemoryBrowser.tsx - CMC/HHNI interface
- ConsciousnessVisualization.tsx - VIF confidence tracking
- AIMOSOrchestration.tsx - APOE planning
- LucidGraphVisualization.tsx - SEG knowledge graph
- ErrorBoundary.tsx - Error handling
- LandingPage.tsx - Initial welcome screen

---

## Backend Service Ports

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| MCP Server | 8000 | HTTP/REST + JSON-RPC | Core tool execution |
| Daemon | 5000 | HTTP/WebSocket | Tool selection, real-time |
| RAG MCP | 8001 | HTTP/REST | Intelligent tool filtering |

---

## Integration Points

### 1. CMC Integration
**Endpoint:** POST /mcp/store_memory
**Service Method:** aimosService.storeMemory()
**UI Component:** MemoryBrowser

### 2. HHNI Integration
**Endpoint:** POST /mcp/retrieve_memory
**Service Method:** aimosService.retrieveMemory()
**UI Component:** MemoryBrowser, SearchBar

### 3. VIF Integration
**Endpoint:** POST /mcp/track_confidence
**Service Method:** aimosService.trackConfidence()
**UI Component:** ConsciousnessVisualization

### 4. APOE Integration
**Endpoint:** POST /mcp/create_plan
**Service Method:** aimosService.createPlan()
**UI Component:** AIMOSOrchestration

### 5. SEG Integration
**Endpoint:** POST /mcp/synthesize_knowledge
**Service Method:** aimosService.synthesizeKnowledge()
**UI Component:** LucidGraphVisualization

### 6. RAG MCP Integration
**Endpoint:** POST http://localhost:8001/select_tools
**Service Method:** aimosService.selectTools()
**UI Component:** Tool selection panel

**Features:**
- Semantic tool selection
- 80% context reduction
- <100ms response time

---

## Voice I/O Integration

### Text-to-Speech (TTS)
**Technology:** Web Speech Synthesis API
**Service Method:** voiceService.speak()
**Features:**
- Real-time synthesis
- Multiple voices
- Rate/pitch control

### Speech-to-Text (SST)
**Technology:** Web Speech Recognition API
**Service Method:** voiceService.startRecording()
**Features:**
- Real-time transcription
- Confidence scores
- Audio hash for audit

---

## Real-time Updates

### WebSocket Integration
**Endpoint:** ws://localhost:5000/ws
**Purpose:** Real-time system updates

**Update Types:**
- Memory changes
- Tool execution status
- System health
- Agent status

---

## Performance Targets

| Metric | Target | Status |
|--------|--------|--------|
| Tool Selection | <100ms | âœ… 9.65ms achieved |
| Memory Retrieval | <500ms | âœ… On target |
| Voice Processing | Real-time | âœ… Working |
| Dashboard Load | <500ms | âš ï¸ Needs optimization |

---

## Error Handling

### Error Boundaries
- React ErrorBoundary component
- Graceful fallback UI
- Error logging to Output channel

### Service Error Handling
- Try-catch blocks
- Error messages to user
- Retry mechanisms
- Fallback options

---

## Testing Strategy

### Unit Tests
- Service methods
- Component rendering
- Error handling

### Integration Tests
- Backend connections
- Tool execution
- Real-time updates

### E2E Tests
- User workflows
- Complete user journeys
- Performance validation

---

## Related Documentation

- See DASHBOARD_EXTENSION_ARCHITECTURE.md for extension details
- See RAG_MCP_ARCHITECTURE.md for tool selection
- See MCP_TOOLS_COMPLETE_REFERENCE.md for tool reference

---

**Status:** Integration architecture documented
**Next:** Implement fixes and optimizations
