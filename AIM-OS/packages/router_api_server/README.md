"""
Router API Server - README

# Router & Log-Sentinels API Server

API server connecting Router and Log-Sentinels frontend (DAC V2 IDE) to backend (Python core modules).

## Architecture

```
DAC V2 IDE Frontend (React)
    ↓ HTTP Requests
API Server (FastAPI)
    ↓ Python Calls
Router/Log-Sentinels Core (Python)
    ↓ MCP Integration
Command Server (HTTP :5001)
    ↓ MCP Client
MCP Server (stdio)
    ↓ Direct Access
AIM-OS Systems (CMC, VIF, SEG, HHNI, TCS, APOE)
```

## Installation

```bash
cd packages/router_api_server
pip install -r requirements.txt
```

## Running

```bash
uvicorn router_api_server.main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

### Router Endpoints

- `GET /api/router/tools` - Get tool proposals
- `GET /api/router/telemetry` - Get Router telemetry
- `POST /api/router/execute` - Execute tool

### Log-Sentinels Endpoints

- `GET /api/log-sentinels/scouts` - Get Scout reports
- `GET /api/log-sentinels/forensics` - Get Forensics reports
- `GET /api/log-sentinels/telemetry` - Get Log-Sentinels telemetry
- `GET /api/log-sentinels/stream` - SSE stream for real-time updates
- `POST /api/log-sentinels/run-tool` - Run suggested tool

## Integration

- **MCP Integration:** Uses Command Server HTTP wrapper (`POST /mcp/execute`)
- **PLIx Integration:** Tool execution compiles to PLIx contracts → APOE ExecutionPlans
- **NL Tags:** All endpoints tagged for quartet/quintet parity

## Status

✅ **ALL PHASES COMPLETE - PRODUCTION READY**

✅ Phase 1: API Server Foundation (COMPLETE)
✅ Phase 2: Router API Endpoints (COMPLETE)
✅ Phase 3: Log-Sentinels API Endpoints (COMPLETE)
✅ Phase 4: PLIx Integration (COMPLETE)
✅ Phase 5: NL Tags (COMPLETE)
✅ Phase 6: Testing & Validation (COMPLETE)
✅ Phase 7: Documentation & Deployment (COMPLETE)

**See:** `COMPLETE_SUMMARY.md` for full implementation details

