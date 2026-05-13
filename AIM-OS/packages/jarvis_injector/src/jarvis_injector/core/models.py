from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

from jarvis_injector.core.enums import AdapterKind, ArtifactKind, DispatchState, Initiator, PolicyMode


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Rect(BaseModel):
    x: int
    y: int
    width: int
    height: int


class SearchRegion(BaseModel):
    anchor: str = "window"
    x: int
    y: int
    w: int
    h: int


class CdpProfile(BaseModel):
    remote_debugging_port: int = 9222
    host: str = "127.0.0.1"
    user_data_dir: str | None = None
    url_patterns: list[str] = Field(default_factory=list)
    avoid_url_patterns: list[str] = Field(default_factory=list)
    title_patterns: list[str] = Field(default_factory=list)


class UiaCaptureProfile(BaseModel):
    max_depth: int = 18
    region_names: list[str] = Field(default_factory=list)
    panel_automation_id_patterns: list[str] = Field(default_factory=list)
    panel_class_hints: list[str] = Field(default_factory=list)
    message_automation_id_prefixes: list[str] = Field(default_factory=list)
    message_class_hints: list[str] = Field(default_factory=list)
    human_message_hints: list[str] = Field(default_factory=list)
    assistant_message_hints: list[str] = Field(default_factory=list)
    input_automation_id_patterns: list[str] = Field(default_factory=list)
    input_class_hints: list[str] = Field(default_factory=list)
    ignore_offscreen: bool = True
    min_visible_ratio: float = 0.08


class ExecutionPolicy(BaseModel):
    mode: PolicyMode = PolicyMode.SEMI_AUTONOMOUS
    allow_window_activation: bool = True
    allow_mouse_control: bool = True
    allow_keyboard_injection: bool = True
    allow_browser_cdp: bool = True
    allow_visual_fallback: bool = True
    allow_model_repair: bool = True
    require_verification: bool = True
    require_approval_for_new_apps: bool = True
    require_approval_for_destructive_actions: bool = True


class TargetProfile(BaseModel):
    id: str
    display_name: str
    process_hints: list[str] = Field(default_factory=list)
    title_regex: str | None = None
    class_hints: list[str] = Field(default_factory=list)
    preferred_adapters: list[AdapterKind] = Field(default_factory=list)
    regions: dict[str, SearchRegion] = Field(default_factory=dict)
    submit_policy: list[str] = Field(default_factory=list)
    verification_policy: list[str] = Field(default_factory=list)
    cdp: CdpProfile | None = None
    uia: UiaCaptureProfile | None = None
    policy: ExecutionPolicy = Field(default_factory=ExecutionPolicy)


class WindowFingerprint(BaseModel):
    target_id: str
    process_name: str
    class_name: str
    dpi_scale: int = 100
    title_hash: str
    captured_at: datetime = Field(default_factory=utc_now)


class ResolvedWindow(BaseModel):
    hwnd: int
    title: str
    process_name: str
    pid: int
    class_name: str
    is_minimized: bool
    is_visible: bool
    bounds: Rect


class AdapterProbe(BaseModel):
    adapter: AdapterKind
    supported: bool
    confidence: float = 0.0
    reason: str | None = None


class AdapterSelection(BaseModel):
    adapter: AdapterKind
    confidence: float
    reason: str | None = None


class LocateResult(BaseModel):
    adapter: AdapterKind
    locator_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ActionResult(BaseModel):
    success: bool
    detail: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class VerificationSignal(BaseModel):
    name: str
    passed: bool
    detail: str | None = None


class VerificationResult(BaseModel):
    passed: bool
    manual_review_required: bool = False
    signals: list[VerificationSignal] = Field(default_factory=list)


class ExecutionArtifacts(BaseModel):
    screenshot_paths: list[str] = Field(default_factory=list)
    matched_template_ids: list[str] = Field(default_factory=list)
    saved_artifact_ids: list[str] = Field(default_factory=list)


class ArtifactDescriptor(BaseModel):
    id: str
    kind: ArtifactKind
    target_id: str
    path: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)


class MouseTrajectoryArtifact(BaseModel):
    id: str
    target_id: str
    anchor_mode: str = "window_relative"
    target_ref: str
    path_kind: str = "bezier"
    points: list[list[float]] = Field(default_factory=list)
    duration_ms: int = 300
    easing: str = "ease_out"
    verify: list[str] = Field(default_factory=list)


class WorkflowStep(BaseModel):
    id: str
    op: str
    args: dict[str, Any] = Field(default_factory=dict)


class WorkflowDefinition(BaseModel):
    id: str
    name: str
    target_ids: list[str] = Field(default_factory=list)
    steps: list[WorkflowStep] = Field(default_factory=list)


class DispatchRequest(BaseModel):
    target_id: str
    command_text: str
    correlation_id: str | None = None
    preferred_adapter: AdapterKind | None = None
    allow_repair: bool = True
    wait_for_completion: bool = False
    initiated_by: Initiator = Initiator.CLI


class DispatchAccepted(BaseModel):
    execution_id: str
    state: DispatchState


class DispatchResult(BaseModel):
    execution_id: str
    target_id: str
    state: DispatchState
    adapter_used: AdapterKind | None = None
    verification: VerificationResult
    timings_ms: dict[str, int] = Field(default_factory=dict)
    artifacts: ExecutionArtifacts = Field(default_factory=ExecutionArtifacts)
    repair_applied: bool = False
    error: str | None = None
    completed_at: datetime = Field(default_factory=utc_now)


class ExecutionRecord(BaseModel):
    execution_id: str
    request: DispatchRequest
    state: DispatchState
    result: DispatchResult | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class HealthStatus(BaseModel):
    status: str
    service: str
    version: str
    queue_depth: int
    adapters: dict[str, bool]


class TargetSummary(BaseModel):
    id: str
    display_name: str
    preferred_adapters: list[AdapterKind]
    verification_policy: list[str]


class TargetProbeResult(BaseModel):
    target: TargetSummary
    window: ResolvedWindow | None = None
    adapter_probes: list[AdapterProbe] = Field(default_factory=list)
    fingerprint: WindowFingerprint | None = None


class DispatchContext(BaseModel):
    execution_id: str
    request: DispatchRequest
    target: TargetProfile
    policy: ExecutionPolicy
    window: ResolvedWindow | None = None
    adapter_selection: AdapterSelection | None = None
    locate_result: LocateResult | None = None
    verification: VerificationResult | None = None
    artifacts: ExecutionArtifacts = Field(default_factory=ExecutionArtifacts)
    timings_ms: dict[str, int] = Field(default_factory=dict)
