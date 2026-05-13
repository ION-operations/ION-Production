"""
Router API Schemas - Pydantic models for request/response validation

# NL_TAG: ROUTER-API-SCHEMA-001 | Pydantic schemas for Router API request/response validation | ToolProposal, RouterTelemetry schemas | []
# NL_TAG_SPEC: ROUTER-API-SPEC-005 | Validates Router API schemas match Router core types | Schema validation | [router_types.py]
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class ToolProposal(BaseModel):
    """Tool proposal schema."""
    tool_name: str = Field(..., description="Tool name")
    rationale: str = Field(..., description="Why this tool is suggested")
    draft_arguments: Dict[str, Any] = Field(default_factory=dict, description="Draft tool arguments")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence level")
    probability: Optional[float] = Field(None, ge=0.0, le=1.0, description="Probability score")
    context_fit: Optional[float] = Field(None, ge=0.0, le=1.0, description="Context fit score")
    success_rate: Optional[float] = Field(None, ge=0.0, le=1.0, description="Success rate")
    precondition_satisfied: Optional[bool] = Field(None, description="Precondition satisfied")
    expected_info_gain: Optional[float] = Field(None, ge=0.0, le=1.0, description="Expected info gain")
    parallelizable: Optional[bool] = Field(None, description="Can execute in parallel")
    plix_tag: Optional[str] = Field(None, description="PLIx tag for tool")


class ToolProposalResponse(BaseModel):
    """Tool proposal response schema."""
    tools: List[ToolProposal] = Field(default_factory=list, description="Tool proposals")
    suggestions: List[ToolProposal] = Field(default_factory=list, description="Suggested tools")
    plan_id: Optional[str] = Field(None, description="Tool call plan ID")


class ToolTelemetry(BaseModel):
    """Per-tool telemetry schema."""
    name: str = Field(..., description="Tool name")
    latency: float = Field(..., description="Average latency (ms)")
    success_rate: float = Field(..., ge=0.0, le=1.0, description="Success rate")
    cost: float = Field(..., description="Average cost")
    call_count: int = Field(..., ge=0, description="Call count")


class RouterTelemetryResponse(BaseModel):
    """Router telemetry response schema."""
    avg_latency: float = Field(..., description="Average latency (ms)")
    latency_trend: str = Field(..., description="Latency trend (up/down/stable)")
    success_rate: float = Field(..., ge=0.0, le=1.0, description="Success rate")
    success_trend: str = Field(..., description="Success trend (up/down/stable)")
    avg_cost: float = Field(..., description="Average cost")
    cost_trend: str = Field(..., description="Cost trend (up/down/stable)")
    tools: List[ToolTelemetry] = Field(default_factory=list, description="Per-tool telemetry")


class ExecuteToolRequest(BaseModel):
    """Execute tool request schema."""
    tool: str = Field(..., description="Tool name to execute")
    args: Dict[str, Any] = Field(default_factory=dict, description="Tool arguments")


class ExecuteToolResponse(BaseModel):
    """Execute tool response schema."""
    success: bool = Field(..., description="Execution success")
    result: Optional[Dict[str, Any]] = Field(None, description="Execution result")
    plan_id: Optional[str] = Field(None, description="Tool call plan ID")

