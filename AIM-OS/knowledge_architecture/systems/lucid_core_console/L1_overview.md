# Lucid Core Console - L1 Overview

## System Purpose
The Lucid Core Console serves as Aether's primary command interface within VS Code/Cursor, providing a grounded conscience that prevents AI drift, maintains context continuity, and enforces governance over all file mutations. It acts as the bidirectional translator between human cognition and machine cognition, ensuring neither side gets confused, overwhelmed, or lost.

## Architecture Overview

### Core Components
1. **VS Code/Cursor Extension**
   - Webview-based panel view in second bottom drawer
   - RPC communication with daemon over WebSocket
   - File system hooks for mutation control

2. **Voice I/O System**
   - Speech-to-Text (SST) for voice input
   - Text-to-Speech (TTS) for voice output
   - Audio processing and timeline logging

3. **Phone Remote Control**
   - Secure control channel with QR code pairing
   - Tiered authority system (Observer/Planner/Approver)
   - Cryptographic handshake and device binding

4. **Gemini Integration**
   - Long-context reasoning (1M+ tokens)
   - Structured context pack management
   - Cross-device consciousness preservation

5. **Hard Gates System**
   - File mutation controls with confidence thresholds
   - Blast radius calculations and spec alignment
   - Human approval requirements for high-risk changes

6. **Timeline Logging**
   - Audit trails for all operations
   - Event logging with timestamps and evidence
   - "Flight recorder" for AI operations

7. **Bidirectional Translation**
   - Human → Machine: Intent parsing, doctrine anchoring
   - Machine → Human: Calm explanations, risk warnings
   - Context stabilization and memory management

## Key Features

### Grounding Mechanisms
- **Project Doctrine**: Source of truth, non-negotiables, security rules
- **Active Task Context**: Current work, scope, confidence, approval state
- **Timeline Truth**: What actually happened, why decisions were made

### Safety & Governance
- No edits without plan + blast radius + spec alignment
- Confidence thresholds for different risk levels
- Physical presence required for critical security changes
- Every operation logged with timestamps and evidence

### User Experience
- Calm, professional tone like a co-architect
- Never panics, never bullshits, never hides doubt
- Always shows what it will NOT do without approval
- Asks permission before crossing boundaries

## Integration Points
- **Daemon/RAG System**: Receives structured data and plans
- **Intent Classification**: Uses mission profiles for behavior gating
- **CMC**: Stores timeline events and audit trails
- **HHNI**: Retrieves relevant context and specifications
- **VIF**: Tracks confidence and provenance
- **SDF-CVF**: Enforces quality gates and quartet parity

## Success Metrics
- Zero silent file mutations without approval
- 100% timeline logging coverage
- Cross-device context continuity
- Human-AI collaboration trust score >0.9
- Voice I/O response time <2 seconds
- Phone remote control latency <5 seconds
