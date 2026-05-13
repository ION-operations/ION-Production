---
id: ide_chat_app_T2_architecture
system: ide_chat_app
component: null
level: T2
type: architecture
title: IDE Chat App Architecture
description: 2,000-word architecture document for IDE Chat Application
audience: developers, architects, implementation planning
confidence_threshold: 0.70
token_cost: 2000
word_count: 2000
created: 2025-11-18T00:00:00Z
updated: 2025-11-18T00:00:00Z
author: codex
status: complete
tags: ["ide", "chat", "ui", "react", "integration", "cursor", "architecture"]
dependencies: ["ide_chat_app_T1_overview"]
related_docs: ["INTEGRATION_ARCHITECTURE.md", "cursor-addon_T2_architecture"]
version: v1.0.0
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs.

# IDE Chat App – T2 Architecture (≈2000 words)

## System Architecture Overview

IDE Chat App implements a React-based frontend architecture that provides UI integration for all AIM-OS consciousness capabilities. The architecture follows a three-layer pattern with clear separation of concerns: frontend UI, service layer, and backend integration.

**Architectural Principles:**
- **Component-Based Design:** React components for modularity and reusability
- **Service Layer Abstraction:** TypeScript services abstract backend complexity
- **Multi-Mode Deployment:** Extension, standalone, and development modes
- **Real-Time Updates:** WebSocket and polling for live data
- **Type Safety:** Full TypeScript coverage for reliability
- **Performance:** Vite build system for fast development and optimized production

## Component Architecture

### 1. Frontend UI Layer

**Location:** `packages/ide_chat_app/src/`

**Framework Stack:**
- React 18 with hooks and functional components
- TypeScript for type safety
- Vite for build tooling
- Tailwind CSS for styling
- Zustand for state management
- React Router for navigation (if needed)

**Main Components:**

**Dashboard Components:**
- `App.tsx` - Main application entry point
- `LayoutSelector.tsx` - Layout management
- `PanelRegistry.tsx` - Panel registration system
- `PanelPresets.tsx` - Panel configuration presets

**Tab Components (6 Tabs):**
1. **Agents Tab:**
   - Agent management interface
   - Agent status monitoring
   - Agent communication

2. **Chat Tab:**
   - Chat interface with AIM-OS
   - Message history
   - Voice I/O integration

3. **Chains Tab:**
   - Prompt chain visualization
   - Chain execution monitoring
   - Chain management

4. **Tools Tab:**
   - MCP tools browser
   - Tool execution interface
   - Tool documentation

5. **Timeline Tab:**
   - Timeline visualization
   - Context tracking
   - Session continuity

6. **NL Tags Tab:**
   - NL tag browser
   - Tag coverage visualization
   - Tag validation

**Core UI Components:**
- `MemoryBrowser.tsx` - Memory browsing interface
- `MemoryBrowserEnhanced.tsx` - Enhanced memory browser
- `ConsciousnessVisualization.tsx` - Consciousness metrics visualization
- `ContextExplorer.tsx` - Context exploration interface
- `SearchBar.tsx` - Search interface
- `SystemDashboard.tsx` - System status dashboard
- `AIMOSOrchestration.tsx` - Orchestration interface
- `WorkflowManager.tsx` - Workflow management
- `LucidGraphVisualization.tsx` - Graph visualization
- `ToolQualityDashboard.tsx` - Tool quality metrics

**Panel System:**
- `BasePanel.tsx` - Base panel component
- `PanelManagementModal.tsx` - Panel management
- `AIMemoryPanel.tsx` - AI memory panel
- `ContextWebPanel.tsx` - Context web panel
- `EvolutionExplorer.tsx` - Evolution exploration
- `DebugConsolePanel.tsx` - Debug console

### 2. Service Layer

**Location:** `packages/ide_chat_app/src/services/`

**AIMOSService.ts:**
- Core AIM-OS integration service
- Methods for all core systems:
  - `storeMemory()` - Store in CMC
  - `retrieveMemory()` - Retrieve from HHNI
  - `getMemoryStats()` - Get CMC statistics
  - `searchContext()` - Search using HHNI
  - `trackConfidence()` - Track VIF confidence
  - `getConfidenceHistory()` - Get confidence history
  - `createPlan()` - Create APOE plan
  - `synthesizeKnowledge()` - Synthesize SEG knowledge
- Error handling and retry logic
- Type-safe API interfaces

**VoiceService.ts:**
- Text-to-Speech (TTS) using Web Speech Synthesis API
- Speech-to-Text (SST) using Web Speech Recognition API
- Real-time transcription
- Confidence scores
- Audio hash for audit trail
- Timeline logging

**HttpLucidDaemonService.ts:**
- HTTP client for Lucid Orchestrator daemon
- Endpoint: `http://localhost:5000`
- Daemon communication
- Status monitoring

**RealtimeCollaborationService.ts:**
- Real-time collaboration features
- WebSocket connections
- Live updates
- Multi-user support

**AnalyticsService.ts:**
- Analytics and metrics collection
- Performance monitoring
- Usage tracking
- Error reporting

### 3. Backend Integration

**MCP Server Integration:**
- Primary: `lucid_mcp_server.py` (port 8000)
- Protocol: JSON-RPC 2.0 stdio
- Tools: 84 MCP tools available
- Integration: Via Extension Command Server or direct HTTP

**Lucid Daemon:**
- HTTP API on port 5000
- Orchestration services
- Status monitoring

**RAG MCP Proxy:**
- Python service on port 8001
- Intelligent tool selection
- Semantic search for tools
- Context-aware filtering

**Automation Engine:**
- Python service on port 8000/automation
- Automation capabilities
- Task execution

## Integration Patterns

### Pattern 1: Extension Mode

**Flow:**
```
Cursor IDE → cursor-addon → ide_chat_app (React UI) → Services → MCP/HTTP APIs → Core Systems
```

**Characteristics:**
- Embedded in cursor-addon as webview
- Uses Extension Command Server for MCP access
- Shared state with extension
- Limited to extension capabilities

### Pattern 2: Standalone Mode (Electron)

**Flow:**
```
Electron App → ide_chat_app (React UI) → Services → HTTP APIs → Extension Command Server → MCP → Core Systems
```

**Characteristics:**
- Standalone Electron application
- Full desktop app capabilities
- HTTP API integration
- Independent from Cursor IDE

### Pattern 3: Development Mode

**Flow:**
```
Vite Dev Server → ide_chat_app (React UI) → Services → HTTP APIs → Backend Services → Core Systems
```

**Characteristics:**
- Local development server
- Hot module replacement
- Fast iteration
- Direct backend access

## Data Flow

### Memory Operations

**Store Memory:**
```
UI Component → AIMOSService.storeMemory() → HTTP POST /mcp/store_memory → MCP Server → CMC
```

**Retrieve Memory:**
```
UI Component → AIMOSService.retrieveMemory() → HTTP POST /mcp/retrieve_memory → MCP Server → HHNI → CMC
```

### Search Operations

**Search Context:**
```
UI Component → AIMOSService.searchContext() → HTTP POST /mcp/retrieve_memory → MCP Server → HHNI
```

### Confidence Tracking

**Track Confidence:**
```
UI Component → AIMOSService.trackConfidence() → HTTP POST /mcp/track_confidence → MCP Server → VIF
```

### Orchestration

**Create Plan:**
```
UI Component → AIMOSService.createPlan() → HTTP POST /mcp/create_plan → MCP Server → APOE
```

### Knowledge Synthesis

**Synthesize Knowledge:**
```
UI Component → AIMOSService.synthesizeKnowledge() → HTTP POST /mcp/synthesize_knowledge → MCP Server → SEG
```

## State Management

**Zustand Stores:**
- Global state management
- Service state
- UI state
- Cache management

**State Structure:**
- Service connections
- Cache data
- UI preferences
- Session state

## Error Handling

**Service Layer:**
- Try-catch blocks
- Retry logic
- Error boundaries
- User-friendly error messages

**UI Layer:**
- Error boundaries
- Loading states
- Error displays
- Recovery mechanisms

## Performance Optimization

**Build System:**
- Vite for fast builds
- Code splitting
- Tree shaking
- Production optimizations

**Runtime:**
- Component memoization
- Lazy loading
- Virtual scrolling
- Debouncing/throttling

## Security

**API Security:**
- HTTPS in production
- Authentication tokens
- CORS configuration
- Input validation

**Data Security:**
- Secure storage
- Encrypted communication
- Audit trails
- Privacy protection

## Testing

**Unit Tests:**
- Component tests
- Service tests
- Utility tests

**Integration Tests:**
- API integration tests
- End-to-end tests
- Performance tests

## Deployment

**Build Process:**
1. TypeScript compilation
2. Vite build
3. Asset optimization
4. Bundle generation

**Extension Integration:**
- Copy dist/ to cursor-addon/dist/
- Extension packages React UI
- Shared build process

**Standalone Deployment:**
- Electron packaging
- Installer generation
- Auto-update support

## Future Enhancements

- Enhanced visualization components
- Real-time collaboration improvements
- Performance optimizations
- Additional core system integrations
- Mobile responsive design

---

**Status:** Production-ready, integrated with cursor-addon

**See:** `INTEGRATION_ARCHITECTURE.md` in package directory for detailed integration documentation

