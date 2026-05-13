"""
Log-Sentinels API Routes

# NL_TAG: LOG-SENTINELS-API-ENDPOINT-001 | GET /api/log-sentinels/scouts endpoint for fetching Scout reports | get_scouts(...) -> List[ScoutReport] | []
# NL_TAG: LOG-SENTINELS-API-ENDPOINT-002 | GET /api/log-sentinels/forensics endpoint for fetching Forensics reports | get_forensics(...) -> List[ForensicsReport] | []
# NL_TAG: LOG-SENTINELS-API-ENDPOINT-003 | GET /api/log-sentinels/telemetry endpoint for fetching Log-Sentinels telemetry | get_telemetry(...) -> LogSentinelsTelemetry | []
# NL_TAG: LOG-SENTINELS-API-ENDPOINT-004 | GET /api/log-sentinels/stream endpoint for SSE streaming | stream_events(...) -> StreamingResponse | []
# NL_TAG: LOG-SENTINELS-API-ENDPOINT-005 | POST /api/log-sentinels/run-tool endpoint for executing suggested tools | run_tool(...) -> Dict[str, Any] | []
# NL_TAG_CONNECT: LOG-SENTINELS-API-ENDPOINT-SERVICE-001 | Log-Sentinels endpoints call LogSentinelsService methods | get_scouts → LogSentinelsService.get_scout_reports | [LOG-SENTINELS-API-ENDPOINT-001, LOG-SENTINELS-API-SERVICE-001]
# NL_TAG_INTENT: LOG-SENTINELS-API-DESIGN-002 | RESTful API design for Log-Sentinels log analysis and tool suggestions | REST API pattern | [ADR-API-DESIGN]
# NL_TAG_SPEC: LOG-SENTINELS-API-SPEC-002 | Validates Log-Sentinels API request/response schemas using Pydantic | Pydantic schemas | [log_sentinels_schemas.py]
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from typing import List, Optional
from datetime import datetime

from router_api_server.services.log_sentinels_service import LogSentinelsService
from router_api_server.schemas.log_sentinels_schemas import (
    ScoutReportResponse,
    ForensicsReportResponse,
    LogSentinelsTelemetryResponse,
    RunToolRequest,
    RunToolResponse
)

router = APIRouter()


def get_log_sentinels_service(request: Request) -> LogSentinelsService:
    """Dependency injection for LogSentinelsService."""
    return request.app.state.log_sentinels_service


@router.get("/scouts", response_model=List[ScoutReportResponse])
async def get_scouts(
    time_range_from: Optional[datetime] = Query(None, description="Start time"),
    time_range_to: Optional[datetime] = Query(None, description="End time"),
    source_filter: Optional[str] = Query(None, description="Source filter"),
    log_sentinels_service: LogSentinelsService = Depends(get_log_sentinels_service)
) -> List[ScoutReportResponse]:
    """
    Get Scout reports (fast cloud analysis).
    
    Returns list of Scout reports with summaries, confidence, severity, and suggested tools.
    """
    try:
        time_range = None
        if time_range_from and time_range_to:
            time_range = {"from": time_range_from, "to": time_range_to}
        
        reports = await log_sentinels_service.get_scout_reports(
            time_range=time_range,
            source_filter=source_filter
        )
        
        return [ScoutReportResponse(**report.__dict__) for report in reports]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forensics", response_model=List[ForensicsReportResponse])
async def get_forensics(
    time_range_from: Optional[datetime] = Query(None, description="Start time"),
    time_range_to: Optional[datetime] = Query(None, description="End time"),
    severity_filter: Optional[str] = Query(None, description="Severity filter (low/medium/high)"),
    log_sentinels_service: LogSentinelsService = Depends(get_log_sentinels_service)
) -> List[ForensicsReportResponse]:
    """
    Get Forensics reports (deep local analysis).
    
    Returns list of Forensics reports with root causes, fix suggestions, and evidence.
    """
    try:
        time_range = None
        if time_range_from and time_range_to:
            time_range = {"from": time_range_from, "to": time_range_to}
        
        reports = await log_sentinels_service.get_forensics_reports(
            time_range=time_range,
            severity_filter=severity_filter
        )
        
        return [ForensicsReportResponse(**report.__dict__) for report in reports]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/telemetry", response_model=LogSentinelsTelemetryResponse)
async def get_telemetry(
    log_sentinels_service: LogSentinelsService = Depends(get_log_sentinels_service)
) -> LogSentinelsTelemetryResponse:
    """
    Get Log-Sentinels telemetry metrics.
    
    Returns scout calls, forensics calls, escalations, tool suggestions, and timeline.
    """
    try:
        telemetry = await log_sentinels_service.get_telemetry()
        return LogSentinelsTelemetryResponse(**telemetry)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stream")
async def stream_events(
    log_sentinels_service: LogSentinelsService = Depends(get_log_sentinels_service)
) -> StreamingResponse:
    """
    SSE stream for real-time Log-Sentinels updates.
    
    Streams Scout and Forensics reports as they are generated.
    """
    return StreamingResponse(
        log_sentinels_service.stream_events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/run-tool", response_model=RunToolResponse)
async def run_tool(
    request: RunToolRequest,
    log_sentinels_service: LogSentinelsService = Depends(get_log_sentinels_service)
) -> RunToolResponse:
    """
    Run suggested tool via Router → PLIx → APOE.
    
    Executes tool suggested by Log-Sentinels analysis.
    """
    try:
        result = await log_sentinels_service.run_tool(request.tool)
        
        return RunToolResponse(
            success=result["success"],
            result=result.get("result")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

