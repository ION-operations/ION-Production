"""
Log-Sentinels API Schemas - Pydantic models for request/response validation

# NL_TAG: LOG-SENTINELS-API-SCHEMA-001 | Pydantic schemas for Log-Sentinels API request/response validation | ScoutReport, ForensicsReport schemas | []
# NL_TAG_SPEC: LOG-SENTINELS-API-SPEC-003 | Validates Log-Sentinels API schemas match Log-Sentinels core types | Schema validation | [log_sentinels_types.py]
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class Severity(str, Enum):
    """Severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ScoutReportResponse(BaseModel):
    """Scout report response schema."""
    window_id: str = Field(..., description="Window ID")
    summary: str = Field(..., description="Analysis summary")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence level")
    severity: Severity = Field(..., description="Severity level")
    tags: List[str] = Field(default_factory=list, description="Tags (components/APIs)")
    suggested_tools: List[str] = Field(default_factory=list, description="Suggested MCP tools")
    timestamp: str = Field(..., description="Report timestamp (ISO format)")


class FixSuggestion(BaseModel):
    """Fix suggestion schema."""
    patch: Optional[str] = Field(None, description="Patch code")
    steps: Optional[List[str]] = Field(None, description="Fix steps")


class GateStatus(BaseModel):
    """VIF gate status schema."""
    passed: bool = Field(..., description="Gate passed")
    reasons: Optional[List[str]] = Field(None, description="Gate failure reasons")


class ForensicsReportResponse(BaseModel):
    """Forensics report response schema."""
    window_id: str = Field(..., description="Window ID")
    summary: str = Field(..., description="Analysis summary")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence level")
    severity: Severity = Field(..., description="Severity level")
    tags: List[str] = Field(default_factory=list, description="Tags (components/APIs)")
    suggested_tools: List[str] = Field(default_factory=list, description="Suggested MCP tools")
    timestamp: str = Field(..., description="Report timestamp (ISO format)")
    root_cause: Optional[str] = Field(None, description="Root cause analysis")
    fix_suggestion: Optional[FixSuggestion] = Field(None, description="Fix suggestion")
    evidence: List[str] = Field(default_factory=list, description="Evidence references (SEG)")
    gate: Optional[GateStatus] = Field(None, description="VIF gate status")


class TimelineEntry(BaseModel):
    """Timeline entry schema."""
    timestamp: str = Field(..., description="Entry timestamp (ISO format)")
    scout_calls: int = Field(..., ge=0, description="Scout calls count")
    forensics_calls: int = Field(..., ge=0, description="Forensics calls count")
    escalations: int = Field(..., ge=0, description="Escalations count")


class LogSentinelsTelemetryResponse(BaseModel):
    """Log-Sentinels telemetry response schema."""
    scout_calls: int = Field(..., ge=0, description="Total Scout calls")
    forensics_calls: int = Field(..., ge=0, description="Total Forensics calls")
    escalations: int = Field(..., ge=0, description="Total escalations")
    tool_suggestions: int = Field(..., ge=0, description="Total tool suggestions")
    timeline: List[TimelineEntry] = Field(default_factory=list, description="Timeline entries")


class RunToolRequest(BaseModel):
    """Run tool request schema."""
    tool: str = Field(..., description="Tool name to execute")


class RunToolResponse(BaseModel):
    """Run tool response schema."""
    success: bool = Field(..., description="Execution success")
    result: Optional[Dict[str, Any]] = Field(None, description="Execution result")

