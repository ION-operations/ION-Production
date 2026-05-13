from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class CaptureSourceKind(StrEnum):
    DOM = "dom"
    UIA = "uia"
    PLAINTEXT = "plaintext"
    LIVE = "live"


class InlineSpanType(StrEnum):
    TEXT = "text"
    INLINE_CODE = "inline_code"
    LINK = "link"
    CITATION = "citation"
    STATUS = "status"


class BlockType(StrEnum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    LIST = "list"
    CODE_BLOCK = "code_block"
    TABLE = "table"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    STATUS_LINE = "status_line"
    QUOTE = "quote"
    UNKNOWN = "unknown_block"


class InlineSpan(BaseModel):
    type: InlineSpanType
    text: str
    href: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class MessageBlock(BaseModel):
    id: str
    type: BlockType
    text: str | None = None
    spans: list[InlineSpan] = Field(default_factory=list)
    children: list["MessageBlock"] = Field(default_factory=list)
    items: list[list[InlineSpan]] = Field(default_factory=list)
    rows: list[list[str]] = Field(default_factory=list)
    language: str | None = None
    level: int | None = None
    ordered: bool | None = None
    tool_name: str | None = None
    tool_status: str | None = None
    arguments: dict[str, Any] | list[Any] | str | None = None
    collapsed: bool | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class UiTreeNode(BaseModel):
    name: str | None = None
    value: str | None = None
    control_type: str | None = None
    automation_id: str | None = None
    class_name: str | None = None
    is_enabled: bool | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    children: list["UiTreeNode"] = Field(default_factory=list)


class CaptureVerification(BaseModel):
    stable: bool = False
    completeness_score: float = 0.0
    indicators: list[str] = Field(default_factory=list)


class CaptureSource(BaseModel):
    adapter: str
    kind: CaptureSourceKind
    confidence: float
    provider: str | None = None


class CaptureRequest(BaseModel):
    target_id: str
    provider: str | None = None
    source_preference: list[CaptureSourceKind] = Field(
        default_factory=lambda: [CaptureSourceKind.LIVE, CaptureSourceKind.DOM, CaptureSourceKind.UIA, CaptureSourceKind.PLAINTEXT]
    )
    html_snapshot: str | None = None
    uia_tree: UiTreeNode | list[UiTreeNode] | None = None
    plain_text: str | None = None
    message_role: str = "assistant"
    include_collapsed_tool_content: bool = False
    live_timeout_ms: int = 5000
    metadata: dict[str, Any] = Field(default_factory=dict)


class CapturedMessage(BaseModel):
    target_id: str
    message_id: str
    captured_at: datetime = Field(default_factory=utc_now)
    source: CaptureSource
    verification: CaptureVerification
    blocks: list[MessageBlock] = Field(default_factory=list)
    plaintext: str
    markdown: str
    metadata: dict[str, Any] = Field(default_factory=dict)


MessageBlock.model_rebuild()
UiTreeNode.model_rebuild()
