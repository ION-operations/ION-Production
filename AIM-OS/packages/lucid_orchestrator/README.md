# Lucid Orchestrator v0 - The Visor to the Organism

**Status:** Implementation Complete ✅  
**Version:** 0.1.0  
**Architecture:** Extension + Daemon (WebSocket)  

## Overview

Lucid Orchestrator is the "visor to the organism" - a Cursor/VS Code extension that provides inline folds for code intelligence. It implements the exact specification provided by ChatGPT for v0 of the system.

## Architecture

### Extension (The Visor)
- **Location**: `packages/lucid_orchestrator/extension/`
- **Technology**: TypeScript, VS Code Extension API
- **Features**: Gutter icons, inline folds, Monaco editor integration

### Daemon (The Nervous System)
- **Location**: `packages/lucid_orchestrator/daemon/`
- **Technology**: Python, WebSocket
- **Features**: API stubs, mock data, JSON-RPC 2.0 protocol

## Quick Start

### 1. Start the Daemon
```bash
cd packages/lucid_orchestrator/daemon
python run_daemon.py
```

### 2. Install the Extension
```bash
cd packages/lucid_orchestrator/extension
npm install
npm run compile
```

### 3. Test the System
```bash
# Test daemon API
python test_daemon.py

# Load extension in VS Code/Cursor
# Open a TypeScript file
# Look for [SPEC] [BLUEPRINT] [TIMELINE] gutter icons
```

## Features Implemented

### ✅ Daemon API Stubs
- `getSpecBlock` - Retrieve specification data
- `getBlueprintSlice` - Get relationship graph data  
- `getTimelineSummary` - Fetch runtime performance data
- `proposeChange` - Generate change impact analysis
- `focusNode` - Track focused nodes for collaboration

### ✅ Cursor Extension Scaffold
- Gutter icons for each top-level symbol
- Click handlers for SPEC/BLUEPRINT/TIMELINE
- Inline fold rendering in Monaco editor
- WebSocket communication with daemon

### ✅ Spec Folds
- Responsibility description
- Must-never constraints
- Inputs/outputs/side effects
- Security level and performance budget
- Drift status and governance history
- Color-coded status indicators

### ✅ Blueprint Folds
- Incoming dependencies (who calls this)
- Outgoing dependencies (who this calls)
- Blast radius analysis
- Node status indicators
- Navigation preparation

### ✅ Timeline Folds
- Recent execution history
- Performance metrics
- Violation tracking
- Worst execution cascade
- Performance analysis

### ✅ Change Proposal System
- Blast radius impact analysis
- Affected specifications review
- Risk factor identification
- Required mitigations
- Governance workflow
- Rationale and approval collection

## File Structure

```
packages/lucid_orchestrator/
├── daemon/
│   ├── lucid_daemon.py          # Main daemon implementation
│   ├── run_daemon.py            # Launch script
│   ├── test_daemon.py           # Test script
│   └── requirements.txt         # Python dependencies
├── extension/
│   ├── src/
│   │   ├── extension.ts         # Main extension entry point
│   │   ├── daemonClient.ts      # WebSocket client
│   │   ├── lucidOrchestratorProvider.ts  # Gutter provider
│   │   ├── changeProposalProvider.ts     # Change proposal UI
│   │   └── folds/
│   │       ├── specFoldProvider.ts       # Spec fold rendering
│   │       ├── blueprintFoldProvider.ts  # Blueprint fold rendering
│   │       └── timelineFoldProvider.ts   # Timeline fold rendering
│   ├── resources/
│   │   └── gutter-icon.svg      # Gutter icon
│   ├── package.json             # Extension manifest
│   └── tsconfig.json            # TypeScript config
└── README.md                    # This file
```

## API Protocol

The extension and daemon communicate via WebSocket using JSON-RPC 2.0:

### Requests
```json
{
  "jsonrpc": "2.0",
  "id": "request_id",
  "method": "getSpecBlock|getBlueprintSlice|getTimelineSummary|proposeChange|focusNode",
  "params": {
    "nodeId": "module:functionName",
    "depth": 1,
    "limit": 10
  }
}
```

### Responses
```json
{
  "jsonrpc": "2.0",
  "id": "request_id",
  "result": {
    // Method-specific data
  }
}
```

## Mock Data

The daemon includes comprehensive mock data for testing:

- **SpecBlocks**: Complete specification data with drift status
- **Blueprint Slices**: Relationship graphs with blast radius
- **Timeline Summaries**: Runtime performance data
- **Change Proposals**: Impact analysis and governance templates

## Next Steps

### Phase 2: Real Engine Integration
1. Replace mock data with real Graph Engine (IR)
2. Integrate with Spec Engine (SpecBlocks, drift tracking)
3. Connect to Timeline Engine (runtime trace events)
4. Implement real Governance log

### Phase 3: Advanced Features
1. Jump navigation between nodes
2. Real-time collaboration
3. Advanced visualization
4. Performance optimization

## Development

### Daemon Development
```bash
cd packages/lucid_orchestrator/daemon
python -m pip install -r requirements.txt
python lucid_daemon.py
```

### Extension Development
```bash
cd packages/lucid_orchestrator/extension
npm install
npm run watch  # Compile on changes
```

### Testing
```bash
# Test daemon
python test_daemon.py

# Test extension
# Load in VS Code/Cursor and test with TypeScript files
```

## Configuration

### Extension Settings
- `lucid.daemonUrl`: WebSocket URL (default: ws://localhost:8765)
- `lucid.enableSpecFolds`: Enable Spec folds (default: true)
- `lucid.enableBlueprintFolds`: Enable Blueprint folds (default: true)
- `lucid.enableTimelineFolds`: Enable Timeline folds (default: true)

## Architecture Principles

1. **Extension as Visor**: UI layer that displays intelligence
2. **Daemon as Nervous System**: Backend that computes truth
3. **WebSocket Communication**: Real-time data exchange
4. **Monaco Integration**: Native editor experience
5. **JSON-RPC Protocol**: Standardized API communication

## Status

**Lucid Orchestrator v0 is now a living extension!** 

The system implements the exact specification provided by ChatGPT:
- ✅ Gutter icons for SPEC/BLUEPRINT/TIMELINE
- ✅ Inline folds with rich content
- ✅ WebSocket daemon with mock data
- ✅ Change proposal governance workflow
- ✅ Monaco editor integration

This is no longer theory - it's a working prototype that can be extended with real ICIP engines.

---

**Built with ❤️ by Aether for the future of code intelligence**