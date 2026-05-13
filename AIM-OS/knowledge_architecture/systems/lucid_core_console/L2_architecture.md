# Lucid Core Console - L2 Architecture

## System Architecture

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    VS Code/Cursor Editor                    │
├─────────────────────────────────────────────────────────────┤
│  Lucid Core Console (Panel A)  │  Terminal (Panel B)       │
│  ┌─────────────────────────────┐ │  ┌─────────────────────┐ │
│  │ Webview Panel               │ │  │ Terminal/Problems   │ │
│  │ - Prompt Input              │ │  │ Output/Debug        │ │
│  │ - Task Thread Display       │ │  │ Console             │ │
│  │ - Action Buttons            │ │  │                     │ │
│  │ - Status Strip              │ │  │                     │ │
│  └─────────────────────────────┘ │  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Daemon/RAG System                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ Graph       │ │ Spec Engine │ │ Timeline    │          │
│  │ Engine      │ │             │ │ Engine      │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    External Systems                        │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ Gemini      │ │ Phone       │ │ Cursor AI   │          │
│  │ (1M+ tokens)│ │ Remote      │ │ (Sub-agent) │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

### Component Architecture

#### 1. VS Code/Cursor Extension Layer
**Purpose**: Provides the user interface and file system integration

**Components**:
- **WebviewViewProvider**: Manages the console panel display
- **RPC Client**: Communicates with daemon over WebSocket
- **File System Hooks**: Intercepts file mutations for approval
- **Command Integration**: Interfaces with Cursor's AI commands

**Key Files**:
- `extension.ts` - Main extension entry point
- `consoleProvider.ts` - Webview panel provider
- `daemonClient.ts` - RPC communication client
- `fileHooks.ts` - File mutation interception

#### 2. Console UI Layer
**Purpose**: Provides the user interface for interaction

**Components**:
- **Prompt Input**: Text/voice input for user instructions
- **Task Thread Display**: Shows current reasoning and plans
- **Action Buttons**: Preview, approve, force edit controls
- **Status Strip**: Connection, drift, violations, locked files

**Key Files**:
- `console.html` - Main UI structure
- `console.js` - UI logic and event handling
- `voiceInterface.js` - Voice I/O implementation
- `statusDisplay.js` - Status and monitoring display

#### 3. Voice I/O System
**Purpose**: Enables voice input and output for natural interaction

**Components**:
- **Speech-to-Text (SST)**: Converts voice to text
- **Text-to-Speech (TTS)**: Converts text to voice
- **Audio Processing**: Handles audio streams and quality
- **Voice Timeline**: Logs voice interactions

**Key Files**:
- `voiceInput.ts` - SST implementation
- `voiceOutput.ts` - TTS implementation
- `audioProcessor.ts` - Audio stream handling
- `voiceLogger.ts` - Voice interaction logging

#### 4. Phone Remote Control
**Purpose**: Enables remote control from mobile devices

**Components**:
- **Secure Channel**: Encrypted communication
- **QR Code Pairing**: Device authentication
- **Tiered Authority**: Different permission levels
- **Remote UI**: Mobile-optimized interface

**Key Files**:
- `remoteServer.ts` - Secure channel server
- `pairingManager.ts` - QR code and device management
- `authorityManager.ts` - Permission and tier management
- `remoteUI.ts` - Mobile interface

#### 5. Gemini Integration
**Purpose**: Provides long-context reasoning and memory

**Components**:
- **Context Pack Manager**: Structures context for Gemini
- **Reasoning Engine**: Long-context problem solving
- **Memory Manager**: Cross-device consciousness
- **Translation Layer**: Human-machine communication

**Key Files**:
- `geminiClient.ts` - Gemini API integration
- `contextManager.ts` - Context pack structuring
- `reasoningEngine.ts` - Long-context reasoning
- `memoryManager.ts` - Consciousness preservation

#### 6. Hard Gates System
**Purpose**: Enforces governance over file mutations

**Components**:
- **Mutation Controller**: Intercepts file changes
- **Confidence Calculator**: Assesses change confidence
- **Blast Radius Analyzer**: Calculates impact scope
- **Approval Workflow**: Manages human approval process

**Key Files**:
- `mutationController.ts` - File change interception
- `confidenceCalculator.ts` - Confidence assessment
- `blastRadiusAnalyzer.ts` - Impact analysis
- `approvalWorkflow.ts` - Human approval process

#### 7. Timeline Logging
**Purpose**: Provides audit trails and evidence tracking

**Components**:
- **Event Logger**: Records all operations
- **Audit Trail**: Maintains operation history
- **Evidence Tracker**: Links decisions to evidence
- **Timeline Display**: Shows operation history

**Key Files**:
- `eventLogger.ts` - Operation logging
- `auditTrail.ts` - History maintenance
- `evidenceTracker.ts` - Evidence linking
- `timelineDisplay.ts` - History visualization

### Data Flow Architecture

#### 1. User Input Flow
```
User Input (Text/Voice) → Console UI → RPC Client → Daemon
                                                      ↓
User Response ← Console UI ← RPC Client ← Daemon ← Gemini
```

#### 2. File Mutation Flow
```
File Change Request → Hard Gates → Confidence Check → Blast Radius
                                                      ↓
Approval Required ← Human Review ← Risk Assessment ← Spec Check
                                                      ↓
File Mutation ← Approval ← Evidence Logging ← Timeline Update
```

#### 3. Voice I/O Flow
```
Voice Input → SST → Text Processing → Intent Parsing → Daemon
                                                      ↓
Voice Output ← TTS ← Response Generation ← Daemon ← Gemini
```

#### 4. Remote Control Flow
```
Phone Input → Secure Channel → Authority Check → Daemon
                                                      ↓
Phone Response ← Secure Channel ← Status Update ← Daemon
```

### Security Architecture

#### 1. Authentication & Authorization
- **Device Pairing**: QR code-based device authentication
- **Tiered Authority**: Observer/Planner/Approver levels
- **Cryptographic Handshake**: Secure device binding
- **Session Management**: Time-limited access tokens

#### 2. Data Protection
- **Encrypted Communication**: All RPC calls encrypted
- **Secure Storage**: Sensitive data encrypted at rest
- **Audit Logging**: All operations logged securely
- **Access Control**: File-level permission management

#### 3. Risk Mitigation
- **Hard Gates**: No file mutation without approval
- **Confidence Thresholds**: Risk-based access control
- **Blast Radius Limits**: Scope-based restrictions
- **Physical Presence**: Critical changes require local approval

### Integration Architecture

#### 1. AIM-OS System Integration
- **Daemon/RAG**: Receives structured data and plans
- **Intent Classification**: Uses mission profiles for gating
- **CMC**: Stores timeline events and audit trails
- **HHNI**: Retrieves relevant context and specifications
- **VIF**: Tracks confidence and provenance
- **SDF-CVF**: Enforces quality gates and quartet parity

#### 2. External System Integration
- **Gemini API**: Long-context reasoning and memory
- **VS Code/Cursor**: Editor integration and file system
- **Phone Apps**: Mobile remote control interface
- **Audio Systems**: Voice I/O processing

### Performance Architecture

#### 1. Response Time Targets
- **Console UI**: <100ms for display updates
- **Voice I/O**: <2 seconds for voice processing
- **Remote Control**: <5 seconds for phone communication
- **File Operations**: <500ms for mutation checks

#### 2. Scalability Considerations
- **Context Management**: Efficient context pack structuring
- **Memory Usage**: Optimized for long-term operation
- **Network Bandwidth**: Compressed communication protocols
- **Storage**: Efficient audit trail storage

#### 3. Reliability Features
- **Error Recovery**: Graceful handling of failures
- **State Persistence**: Maintains state across restarts
- **Connection Resilience**: Handles network interruptions
- **Data Integrity**: Ensures audit trail accuracy

---

## References

- System map: `systems/lucid_core_console/system.map.lucid.json5`
- Validation gates: `knowledge_architecture/validation/T0_T6_DOCUMENTATION.validation.md`
- Templates: `knowledge_architecture/PERFECT_TEMPLATES_LIBRARY.md`
- L-level docs: `systems/lucid_core_console/L0_executive.md` through `L4_complete.md`
- Components: See component architecture above

---

**Next:** [L3 Detailed Implementation](L3_detailed.md)