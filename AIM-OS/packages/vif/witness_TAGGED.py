"""VIF Witness Schema - Provenance envelope for AI operations"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
import hashlib
import uuid


# NL_TAG: VIF-MODEL-001 | Confidence band enumeration for user trust indicators | ConfidenceBand(str, Enum) | []
# NL_TAG_INTENT: VIF-DESIGN-001 | User-facing confidence indicators for trust calibration | A/B/C bands map to >0.90, 0.70-0.90, <0.70 | [ADR-CONFIDENCE-BANDS]
class ConfidenceBand(str, Enum):
    """Confidence bands for user trust indicators"""
    A = "A"  # High confidence (>0.90)
    B = "B"  # Medium confidence (0.70-0.90)
    C = "C"  # Low confidence (<0.70)


# NL_TAG: VIF-MODEL-002 | Task criticality enumeration for κ-gate thresholds | TaskCriticality(str, Enum) | []
# NL_TAG_INTENT: VIF-DESIGN-002 | Criticality determines abstention threshold | Critical tasks require higher confidence | [ADR-KAPPA-GATES]
class TaskCriticality(str, Enum):
    """Task criticality levels for κ-gate thresholds"""
    CRITICAL = "critical"      # Medical, legal, safety-critical
    IMPORTANT = "important"    # Financial, strategic decisions
    ROUTINE = "routine"        # Standard operations
    LOW_STAKES = "low_stakes"  # Experimental, low-impact


# NL_TAG: VIF-WITNESS-001 | Complete VIF witness envelope with provenance | VIF(BaseModel) | [VIF-MODEL-001, VIF-MODEL-002]
# NL_TAG_CONNECT: VIF-CMC-001 | VIF witnesses stored in CMC as atoms | VIF → store_atom | [VIF-WITNESS-001, CMC-STORE-001]
# NL_TAG_CONNECT: VIF-HHNI-001 | VIF tracks retrieved atoms from HHNI | retrieve_similar → VIF.retrieved_atom_ids | [HHNI-RETRIEVE-001, VIF-WITNESS-001]
# NL_TAG_INTENT: VIF-DESIGN-003 | Witnesses enable deterministic replay and uncertainty quantification | cryptographic hashes + snapshots | [ADR-VIF-WITNESSES]
# NL_TAG_SPEC: VIF-SPEC-001 | Validates VIF witness schema v1.0.0 | VIF.model_validate | [vif_witness_schema_v1.json]
class VIF(BaseModel):
    """Verifiable Intelligence Framework witness envelope
    
    Records complete provenance for an AI operation, enabling:
    - Deterministic replay
    - Uncertainty quantification
    - Behavioral abstention (κ-gating)
    - Confidence bands for user trust
    
    Examples:
        >>> vif = VIF(
        ...     model_id="gpt-4-turbo",
        ...     model_provider="openai",
        ...     context_snapshot_id="snap_123",
        ...     prompt_hash=hashlib.sha256(b"prompt").hexdigest(),
        ...     prompt_tokens=100,
        ...     confidence_score=0.95,
        ...     confidence_band=ConfidenceBand.A,
        ...     output_hash=hashlib.sha256(b"output").hexdigest(),
        ...     output_tokens=50,
        ...     total_tokens=150,
        ... )
        >>> vif.kappa_gate_passed
        True
    """
    
    # === IDENTITY ===
    id: str = Field(
        default_factory=lambda: f"vif_{uuid.uuid4().hex}",
        description="Unique identifier for this witness"
    )
    version: str = Field(
        default="1.0.0",
        description="VIF schema version"
    )
    
    # === WHAT MODEL ===
    model_id: str = Field(
        description="Model identifier (e.g., 'gpt-4-turbo-2025-01-15')"
    )
    model_provider: str = Field(
        description="Provider: 'openai', 'anthropic', 'local', etc."
    )
    weights_hash: Optional[str] = Field(
        default=None,
        description="SHA-256 hash of model weights (if available)"
    )
    
    # === WHAT DATA ===
    context_snapshot_id: str = Field(
        description="CMC snapshot ID capturing full context"
    )
    context_atom_ids: List[str] = Field(
        default_factory=list,
        description="Specific atom IDs used in this operation"
    )
    prompt_template: Optional[str] = Field(
        default=None,
        description="Template before variable substitution"
    )
    prompt_hash: str = Field(
        description="SHA-256 hash of actual prompt sent to model"
    )
    prompt_tokens: int = Field(
        ge=0,
        description="Token count of prompt"
    )
    retrieved_atom_ids: List[str] = Field(
        default_factory=list,
        description="Atoms retrieved from HHNI for context"
    )
    
    # === WHAT TOOLS ===
    tool_ids: List[str] = Field(
        default_factory=list,
        description="Tool IDs used (e.g., ['hhni.retrieve', 'cmc.store'])"
    )
    tool_parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Exact parameters passed to each tool"
    )
    tool_results_hash: Optional[str] = Field(
        default=None,
        description="SHA-256 hash of tool outputs"
    )
    
    # === UNCERTAINTY ===
    confidence_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Model's confidence in output (0.0-1.0)"
    )
    confidence_band: ConfidenceBand = Field(
        description="User-facing confidence indicator (A/B/C)"
    )
    ece_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Expected Calibration Error (if tracked)"
    )
    entropy: float = Field(
        default=0.0,
        ge=0.0,
        description="Output distribution entropy (bits)"
    )
    top_k_probs: List[Tuple[str, float]] = Field(
        default_factory=list,
        description="Top-K token probabilities [(token, prob), ...]"
    )
    
    # === REPLAY ===
    replay_seed: Optional[int] = Field(
        default=None,
        description="Random seed for deterministic reproduction"
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Sampling temperature"
    )
    top_p: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Nucleus sampling parameter"
    )
    top_k: Optional[int] = Field(
        default=None,
        ge=1,
        description="Top-k sampling parameter"
    )
    max_tokens: Optional[int] = Field(
        default=None,
        ge=1,
        description="Maximum output tokens"
    )
    other_params: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional generation parameters"
    )
    
    # === OUTPUT ===
    output_hash: str = Field(
        description="SHA-256 hash of model output"
    )
    output_tokens: int = Field(
        ge=0,
        description="Token count of output"
    )
    total_tokens: int = Field(
        ge=0,
        description="prompt_tokens + output_tokens"
    )
    
    # === META ===
    writer: str = Field(
        default="system",
        description="Who created this witness: 'system', 'user', 'agent_planner'"
    )
    task_criticality: TaskCriticality = Field(
        default=TaskCriticality.ROUTINE,
        description="Criticality level of the task"
    )
    kappa_threshold: float = Field(
        default=0.70,
        ge=0.0,
        le=1.0,
        description="Abstention threshold (κ) for this task"
    )
    kappa_gate_passed: bool = Field(
        default=True,
        description="Did confidence meet κ threshold?"
    )
    
    # === TEMPORAL ===
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this witness was created"
    )
    execution_time_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Operation execution time in milliseconds"
    )
    
    # === LINEAGE ===
    parent_vif_id: Optional[str] = Field(
        default=None,
        description="Parent witness ID (for chained operations)"
    )
    child_vif_ids: List[str] = Field(
        default_factory=list,
        description="Child witness IDs derived from this operation"
    )
    
    # === VALIDATION ===
    signature: Optional[str] = Field(
        default=None,
        description="Cryptographic signature (future implementation)"
    )
    verified: bool = Field(
        default=False,
        description="Has this witness been independently verified?"
    )
    
    model_config = {
        "use_enum_values": False,  # Keep enum objects, not strings
    }
    
    # NL_TAG: VIF-WITNESS-002 | Serialize VIF witness with datetime handling | model_dump(**kwargs) -> Dict[str, Any] | [VIF-WITNESS-001]
    # NL_TAG_SPEC: VIF-SPEC-002 | Ensures ISO8601 datetime format for JSON compatibility | model_dump | [json_serialization_spec]
    def model_dump(self, **kwargs) -> Dict[str, Any]:
        """Override to handle datetime serialization"""
        data = super().model_dump(**kwargs)
        if isinstance(data.get("created_at"), datetime):
            data["created_at"] = data["created_at"].isoformat()
        return data
    
    # NL_TAG: VIF-CONF-001 | Determine confidence band from confidence score | determine_confidence_band() -> ConfidenceBand | [VIF-MODEL-001]
    # NL_TAG_INTENT: VIF-DESIGN-004 | Automatic band assignment reduces user cognitive load | A>=0.90, B>=0.70, C<0.70 | [ADR-CONFIDENCE-BANDS]
    def determine_confidence_band(self) -> ConfidenceBand:
        """Automatically determine confidence band from score"""
        if self.confidence_score >= 0.90:
            return ConfidenceBand.A
        elif self.confidence_score >= 0.70:
            return ConfidenceBand.B
        else:
            return ConfidenceBand.C
    
    # NL_TAG: VIF-GATE-001 | Check if confidence meets κ-gate threshold | check_kappa_gate() -> bool | [VIF-WITNESS-001]
    # NL_TAG_CONNECT: VIF-APOE-001 | κ-gate used by APOE for abstention decisions | check_kappa_gate → abstain_if_below_threshold | [VIF-GATE-001, APOE-ABST-001]
    # NL_TAG_INTENT: VIF-DESIGN-005 | κ-gates enable behavioral abstention for safety | Abstain when uncertain | [ADR-KAPPA-GATES]
    def check_kappa_gate(self) -> bool:
        """Check if confidence meets κ threshold"""
        return self.confidence_score >= self.kappa_threshold
    
    # NL_TAG: VIF-PROV-001 | Add child witness to provenance lineage | add_child(child_vif_id: str) -> None | [VIF-WITNESS-001]
    # NL_TAG_CONNECT: VIF-SEG-001 | Lineage tracked in SEG provenance graphs | add_child → build_provenance_graph | [VIF-PROV-001, SEG-PROV-001]
    # NL_TAG_INTENT: VIF-DESIGN-006 | Lineage enables provenance tracing and audit trails | Parent-child relationships | [ADR-PROVENANCE]
    def add_child(self, child_vif_id: str) -> None:
        """Add a child witness to lineage"""
        if child_vif_id not in self.child_vif_ids:
            self.child_vif_ids.append(child_vif_id)
    
    # NL_TAG: VIF-UTIL-001 | Generate SHA-256 hash of text | hash_text(text: str) -> str | []
    # NL_TAG_INTENT: VIF-DESIGN-007 | Cryptographic hashes ensure immutability and verifiability | SHA-256 for content-addressing | [ADR-CONTENT-ADDRESSING]
    @staticmethod
    def hash_text(text: str) -> str:
        """Generate SHA-256 hash of text"""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()
    
    # NL_TAG: VIF-UTIL-002 | Generate SHA-256 hash of bytes | hash_bytes(data: bytes) -> str | []
    # NL_TAG_INTENT: VIF-DESIGN-008 | Cryptographic hashes for binary data integrity | SHA-256 for binary content | [ADR-CONTENT-ADDRESSING]
    @staticmethod
    def hash_bytes(data: bytes) -> str:
        """Generate SHA-256 hash of bytes"""
        return hashlib.sha256(data).hexdigest()
    
    # NL_TAG: VIF-WITNESS-003 | Convert VIF witness to JSON-serializable dictionary | to_dict() -> Dict[str, Any] | [VIF-WITNESS-002]
    # NL_TAG_CONNECT: VIF-CMC-002 | VIF dict stored in CMC atoms | to_dict → store_atom | [VIF-WITNESS-003, CMC-STORE-001]
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (JSON-serializable)"""
        return self.model_dump(mode="json")
    
    # NL_TAG: VIF-WITNESS-004 | Create VIF witness from dictionary | from_dict(data: Dict[str, Any]) -> VIF | [VIF-WITNESS-001]
    # NL_TAG_CONNECT: VIF-CMC-003 | VIF restored from CMC atom data | retrieve_atom → from_dict | [CMC-RETRIEVE-001, VIF-WITNESS-004]
    # NL_TAG_SPEC: VIF-SPEC-003 | Validates input data against VIF schema | model_validate | [vif_witness_schema_v1.json]
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> VIF:
        """Create VIF from dictionary"""
        return cls.model_validate(data)

