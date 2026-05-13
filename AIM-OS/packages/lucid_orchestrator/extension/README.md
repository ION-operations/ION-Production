# Lucid Orchestrator Extension

The visor to the organism - inline folds for code intelligence.

## Features

- **SPEC Folds**: View natural language specifications for code units
- **BLUEPRINT Folds**: See relationship graphs and blast radius
- **TIMELINE Folds**: Monitor runtime performance and violations
- **Change Proposals**: Governance workflow for code changes

## Installation

1. Install the extension in VS Code/Cursor
2. Start the Lucid Daemon: `python packages/lucid_orchestrator/daemon/lucid_daemon.py`
3. Open a TypeScript/JavaScript file
4. Look for `[SPEC] [BLUEPRINT] [TIMELINE]` gutter icons next to functions/components

## Usage

### Viewing Specs
Click on `[SPEC]` to see:
- Responsibility description
- Must-never constraints
- Inputs/outputs/side effects
- Security level and performance budget
- Drift status and governance history

### Viewing Blueprints
Click on `[BLUEPRINT]` to see:
- Incoming dependencies (who calls this)
- Outgoing dependencies (who this calls)
- Blast radius analysis
- Navigation to related nodes

### Viewing Timelines
Click on `[TIMELINE]` to see:
- Recent execution history
- Performance metrics
- Violation tracking
- Worst execution cascade

### Proposing Changes
Click `[PROPOSE CHANGE]` in a SPEC fold to:
- See blast radius impact
- Review affected specifications
- Accept risks and provide rationale
- Submit governance workflow

## Configuration

- `lucid.daemonUrl`: WebSocket URL for Lucid Daemon (default: ws://localhost:8765)
- `lucid.enableSpecFolds`: Enable Spec inline folds (default: true)
- `lucid.enableBlueprintFolds`: Enable Blueprint inline folds (default: true)
- `lucid.enableTimelineFolds`: Enable Timeline inline folds (default: true)

## Development

```bash
# Install dependencies
npm install

# Compile TypeScript
npm run compile

# Watch for changes
npm run watch

# Run tests
npm test
```

## Architecture

The extension communicates with the Lucid Daemon via WebSocket using JSON-RPC 2.0 protocol. The daemon provides:

- `getSpecBlock`: Retrieve specification data
- `getBlueprintSlice`: Get relationship graph data
- `getTimelineSummary`: Fetch runtime performance data
- `proposeChange`: Generate change impact analysis
- `focusNode`: Track focused nodes for collaboration

## License

MIT
