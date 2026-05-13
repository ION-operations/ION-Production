"""
Router API Routes

# NL_TAG: ROUTER-API-ENDPOINT-001 | GET /api/router/tools endpoint for fetching tool proposals | get_tools(...) -> Dict[str, List[ToolProposal]] | []
# NL_TAG: ROUTER-API-ENDPOINT-002 | GET /api/router/telemetry endpoint for fetching Router telemetry | get_telemetry(...) -> RouterTelemetry | []
# NL_TAG: ROUTER-API-ENDPOINT-003 | POST /api/router/execute endpoint for executing tools | execute_tool(...) -> Dict[str, Any] | []
# NL_TAG_CONNECT: ROUTER-API-ENDPOINT-SERVICE-001 | Router endpoints call RouterService methods | get_tools → RouterService.get_tool_proposals | [ROUTER-API-ENDPOINT-001, ROUTER-API-SERVICE-001]
# NL_TAG_INTENT: ROUTER-API-DESIGN-004 | RESTful API design for Router tool selection and execution | REST API pattern | [ADR-API-DESIGN]
# NL_TAG_SPEC: ROUTER-API-SPEC-004 | Validates Router API request/response schemas using Pydantic | Pydantic schemas | [router_schemas.py]
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from typing import List, Optional
from datetime import datetime

from router_api_server.services.router_service import RouterService
from router_api_server.schemas.router_schemas import (
    ToolProposalResponse,
    RouterTelemetryResponse,
    ExecuteToolRequest,
    ExecuteToolResponse
)

router = APIRouter()


def get_router_service(request: Request) -> RouterService:
    """Dependency injection for RouterService."""
    return request.app.state.router_service


@router.get("/tools", response_model=ToolProposalResponse)
async def get_tools(
    goal: str = Query(..., description="Current goal"),
    task: str = Query(..., description="Current task"),
    confidence: float = Query(0.8, ge=0.0, le=1.0, description="Confidence level"),
    files: Optional[List[str]] = Query(None, description="List of active files"),
    errors: Optional[List[str]] = Query(None, description="List of current errors"),
    agent_intent: str = Query("execute", description="Agent intent"),
    router_service: RouterService = Depends(get_router_service)
) -> ToolProposalResponse:
    """
    Get Router tool proposals.
    
    Returns tool proposals with probabilities, rationales, and preconditions.
    """
    try:
        result = await router_service.get_tool_proposals(
            goal=goal,
            task=task,
            confidence=confidence,
            files=files or [],
            errors=errors or [],
            agent_intent=agent_intent,
            suggested_tools=None
        )
        
        return ToolProposalResponse(
            tools=result["tools"],
            suggestions=result["suggestions"],
            plan_id=result.get("plan_id")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/telemetry", response_model=RouterTelemetryResponse)
async def get_telemetry(
    router_service: RouterService = Depends(get_router_service)
) -> RouterTelemetryResponse:
    """
    Get Router telemetry metrics.
    
    Returns latency, success rate, cost metrics, and per-tool statistics.
    """
    try:
        telemetry = await router_service.get_telemetry()
        return RouterTelemetryResponse(**telemetry)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute", response_model=ExecuteToolResponse)
async def execute_tool(
    request: ExecuteToolRequest,
    router_service: RouterService = Depends(get_router_service)
) -> ExecuteToolResponse:
    """
    Execute tool via Router → PLIx → APOE.
    
    Executes tool with provided arguments and returns result.
    """
    try:
        result = await router_service.execute_tool(
            tool_name=request.tool,
            args=request.args
        )
        
        return ExecuteToolResponse(
            success=result["success"],
            result=result.get("result"),
            plan_id=result.get("plan_id")
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

