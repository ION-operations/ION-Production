"""
VIF Cross-Model Extensions

Extends the VIF (Verifiable Intelligence Framework) to support cross-model consciousness,
enabling comprehensive provenance tracking, confidence calibration, and deterministic
replay across different AI models while maintaining existing VIF capabilities.
"""

import uuid
import hashlib
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum

from vif.witness import VIF, ConfidenceBand, TaskCriticality


@dataclass
# NL_TAG: VIF-MODEL-001 | Validation result | class ValidationResult | []
class ValidationResult:
    """Validation result"""
    field: str
    valid: bool
    message: str


@dataclass
# NL_TAG: VIF-MODEL-002 | Data transformation | class Transformation | []
class Transformation:
    """Data transformation"""
    transformation_id: str = field(default_factory=lambda: f"trans_{uuid.uuid4().hex}")
    transformation_type: str = ""
    transformation_data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


# NL_TAG: VIF-MODEL-003 | Validation status enumeration | class ValidationStatus | []
class ValidationStatus(Enum):
    """Validation status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


# NL_TAG: VIF-MODEL-004 | Transfer mode enumeration | class TransferMode | []
class TransferMode(Enum):
    """Transfer mode enumeration"""
    IMMEDIATE = "immediate"
    BATCH = "batch"
    ASYNC = "async"


# NL_TAG: VIF-MODEL-005 | Context format enumeration | class ContextFormat | []
class ContextFormat(Enum):
    """Context format enumeration"""
    MINIMAL = "minimal"
    STRUCTURED = "structured"
    ENRICHED = "enriched"


# NL_TAG: VIF-MODEL-006 | Replay status enumeration | class ReplayStatus | []
# NL_TAG_INTENT: VIF-INTENT-001 | Design decision: replay | ReplayStatus | [ADR-TBD]
class ReplayStatus(Enum):
    """Replay status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


# Core Cross-Model Data Structures

@dataclass
# NL_TAG: VIF-MODEL-007 | Knowledge transfer metadata | class KnowledgeTransfer | []
class KnowledgeTransfer:
    """Knowledge transfer metadata"""
    
    transfer_id: str = field(default_factory=lambda: f"transfer_{uuid.uuid4().hex}")
    transfer_timestamp: datetime = field(default_factory=datetime.now)
    
    # Transfer Source
    source_model: str = ""
    source_context_hash: str = ""
    
    # Transfer Target
    target_model: str = ""
    target_context_hash: str = ""
    
    # Transfer Content
    insight_content: str = ""
    insight_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Transfer Quality
    transfer_quality_score: float = 0.0
    transfer_completeness: float = 0.0
    transfer_accuracy: float = 0.0
    
    # Transfer Validation
    validation_checks: List[str] = field(default_factory=list)
    validation_results: List[ValidationResult] = field(default_factory=list)
    
    # Transfer Metrics
    transfer_latency: float = 0.0
    transfer_size: int = 0
    transfer_compression_ratio: float = 0.0


@dataclass
# NL_TAG: VIF-MODEL-008 | Single step in provenance chain | class ProvenanceStep | []
# NL_TAG_INTENT: VIF-INTENT-002 | Design decision: provenance | ProvenanceStep | [ADR-TBD]
class ProvenanceStep:
    """Single step in provenance chain"""
    
    step_id: str = field(default_factory=lambda: f"step_{uuid.uuid4().hex}")
    step_timestamp: datetime = field(default_factory=datetime.now)
    
    # Step Information
    step_type: str = ""
    step_description: str = ""
    step_model: str = ""
    
    # Step Data
    input_hash: str = ""
    output_hash: str = ""
    transformation_hash: str = ""
    
    # Step Quality
    step_confidence: float = 0.0
    step_quality_score: float = 0.0
    
    # Step Validation
    validation_status: ValidationStatus = ValidationStatus.PENDING
    validation_results: List[ValidationResult] = field(default_factory=list)


@dataclass
# NL_TAG: VIF-MODEL-009 | Provenance chain verification | class ChainVerification | []
# NL_TAG_INTENT: VIF-INTENT-003 | Design decision: provenance | ChainVerification | [ADR-TBD]
class ChainVerification:
    """Provenance chain verification"""
    
    verification_id: str = field(default_factory=lambda: f"verify_{uuid.uuid4().hex}")
    verification_timestamp: datetime = field(default_factory=datetime.now)
    
    # Verification Results
    chain_integrity: bool = False
    chain_completeness: bool = False
    chain_consistency: bool = False
    
    # Verification Metrics
    verification_confidence: float = 0.0
    verification_quality_score: float = 0.0
    
    # Verification Details
    integrity_checks: List[str] = field(default_factory=list)
    completeness_checks: List[str] = field(default_factory=list)
    consistency_checks: List[str] = field(default_factory=list)


@dataclass
# NL_TAG: VIF-MODEL-010 | Interaction between models | class ModelInteraction | []
class ModelInteraction:
    """Interaction between models"""
    
    interaction_id: str = field(default_factory=lambda: f"inter_{uuid.uuid4().hex}")
    interaction_timestamp: datetime = field(default_factory=datetime.now)
    
    # Interaction Participants
    source_model: str = ""
    target_model: str = ""
    
    # Interaction Content
    interaction_type: str = ""
    interaction_content: str = ""
    interaction_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Interaction Quality
    interaction_quality: float = 0.0
    interaction_confidence: float = 0.0
    
    # Interaction Validation
    validation_results: List[ValidationResult] = field(default_factory=list)
    validation_confidence: float = 0.0


@dataclass
# NL_TAG: VIF-MODEL-011 | Data lineage tracking | class DataLineage | []
class DataLineage:
    """Data lineage tracking"""
    
    lineage_id: str = field(default_factory=lambda: f"lineage_{uuid.uuid4().hex}")
    lineage_timestamp: datetime = field(default_factory=datetime.now)
    
    # Lineage Information
    data_source: str = ""
    data_transformations: List[Transformation] = field(default_factory=list)
    data_destinations: List[str] = field(default_factory=list)
    
    # Lineage Quality
    lineage_completeness: float = 0.0
    lineage_accuracy: float = 0.0
    
    # Lineage Validation
    lineage_validation: List[ValidationResult] = field(default_factory=list)


@dataclass
# NL_TAG: VIF-MODEL-012 | Lineage verification results | class LineageVerification | []
class LineageVerification:
    """Lineage verification results"""
    
    verification_id: str = field(default_factory=lambda: f"lineage_verify_{uuid.uuid4().hex}")
    verification_timestamp: datetime = field(default_factory=datetime.now)
    
    # Verification Results
    lineage_integrity: bool = False
    lineage_completeness: bool = False
    lineage_consistency: bool = False
    
    # Verification Metrics
    verification_confidence: float = 0.0
    verification_quality_score: float = 0.0


@dataclass
# NL_TAG: VIF-MODEL-013 | Trust chain verification | class TrustChain | []
class TrustChain:
    """Trust chain verification"""
    
    trust_id: str = field(default_factory=lambda: f"trust_{uuid.uuid4().hex}")
    trust_timestamp: datetime = field(default_factory=datetime.now)
    
    # Trust Information
    trust_anchors: List[str] = field(default_factory=list)
    trust_paths: List[List[str]] = field(default_factory=list)
    
    # Trust Quality
    trust_score: float = 0.0
    trust_confidence: float = 0.0
    
    # Trust Validation
    trust_validation: List[ValidationResult] = field(default_factory=list)


@dataclass
# NL_TAG: VIF-MODEL-014 | Cross-model provenance chain | class CrossModelProvenance | []
# NL_TAG_INTENT: VIF-INTENT-004 | Design decision: provenance | CrossModelProvenance | [ADR-TBD]
class CrossModelProvenance:
    """Cross-model provenance chain"""
    
    provenance_id: str = field(default_factory=lambda: f"prov_{uuid.uuid4().hex}")
    provenance_timestamp: datetime = field(default_factory=datetime.now)
    
    # Provenance Chain
    provenance_chain: List[ProvenanceStep] = field(default_factory=list)
    chain_verification: ChainVerification = field(default_factory=ChainVerification)
    
    # Model Interactions
    model_interactions: List[ModelInteraction] = field(default_factory=list)
    interaction_quality: float = 0.0
    
    # Data Lineage
    data_lineage: DataLineage = field(default_factory=DataLineage)
    lineage_verification: LineageVerification = field(default_factory=LineageVerification)
    
    # Trust & Verification
    trust_chain: TrustChain = field(default_factory=TrustChain)
    verification_status: str = "pending"


@dataclass
# NL_TAG: VIF-MODEL-015 | Transfer validation results | class TransferValidation | []
class TransferValidation:
    """Transfer validation results"""
    
    validation_id: str = field(default_factory=lambda: f"transfer_val_{uuid.uuid4().hex}")
    validation_timestamp: datetime = field(default_factory=datetime.now)
    
    # Validation Results
    transfer_valid: bool = False
    quality_valid: bool = False
    completeness_valid: bool = False
    
    # Validation Metrics
    validation_confidence: float = 0.0
    validation_quality_score: float = 0.0
    
    # Validation Details
    validation_checks: List[str] = field(default_factory=list)
    validation_results: List[ValidationResult] = field(default_factory=list)


@dataclass
# NL_TAG: VIF-MODEL-016 | Cost optimization tracking | class CostOptimization | []
class CostOptimization:
    """Cost optimization tracking"""
    
    optimization_id: str = field(default_factory=lambda: f"cost_{uuid.uuid4().hex}")
    optimization_timestamp: datetime = field(default_factory=datetime.now)
    
    # Cost Tracking
    total_cost: float = 0.0
    cost_breakdown: Dict[str, float] = field(default_factory=dict)
    
    # Cost Optimization
    optimization_strategy: str = ""
    optimization_effectiveness: float = 0.0
    
    # Cost Comparison
    baseline_cost: float = 0.0
    optimized_cost: float = 0.0
    cost_reduction_percentage: float = 0.0
    
    # Cost Metrics
    cost_per_token: float = 0.0
    cost_per_quality_point: float = 0.0
    cost_efficiency_score: float = 0.0


@dataclass
# NL_TAG: VIF-MODEL-017 | Quality trend over time | class QualityTrend | []
# NL_TAG_INTENT: VIF-INTENT-005 | Design decision: quality | QualityTrend | [ADR-TBD]
class QualityTrend:
    """Quality trend over time"""
    
    trend_id: str = field(default_factory=lambda: f"trend_{uuid.uuid4().hex}")
    trend_timestamp: datetime = field(default_factory=datetime.now)
    
    # Trend Information
    trend_type: str = ""
    trend_direction: str = ""
    trend_magnitude: float = 0.0
    
    # Trend Data
    trend_data_points: List[float] = field(default_factory=list)
    trend_time_points: List[datetime] = field(default_factory=list)
    
    # Trend Quality
    trend_confidence: float = 0.0
    trend_reliability: float = 0.0


@dataclass
# NL_TAG: VIF-MODEL-018 | Quality prediction | class QualityPrediction | []
# NL_TAG_INTENT: VIF-INTENT-006 | Design decision: quality | QualityPrediction | [ADR-TBD]
class QualityPrediction:
    """Quality prediction"""
    
    prediction_id: str = field(default_factory=lambda: f"pred_{uuid.uuid4().hex}")
    prediction_timestamp: datetime = field(default_factory=datetime.now)
    
    # Prediction Information
    prediction_type: str = ""
    prediction_horizon: float = 0.0
    
    # Prediction Data
    predicted_quality: float = 0.0
    prediction_confidence: float = 0.0
    prediction_uncertainty: float = 0.0
    
    # Prediction Validation
    prediction_accuracy: float = 0.0
    prediction_reliability: float = 0.0


@dataclass
# NL_TAG: VIF-MODEL-019 | Quality preservation tracking | class QualityPreservation | []
# NL_TAG_INTENT: VIF-INTENT-007 | Design decision: quality | QualityPreservation | [ADR-TBD]
class QualityPreservation:
    """Quality preservation tracking"""
    
    preservation_id: str = field(default_factory=lambda: f"preserve_{uuid.uuid4().hex}")
    preservation_timestamp: datetime = field(default_factory=datetime.now)
    
    # Preservation Information
    preservation_strategy: str = ""
    preservation_effectiveness: float = 0.0
    
    # Preservation Metrics
    quality_before: float = 0.0
    quality_after: float = 0.0
    quality_degradation: float = 0.0
    
    # Preservation Validation
    preservation_validation: List[ValidationResult] = field(default_factory=list)


@dataclass
# NL_TAG: VIF-MODEL-020 | Cross-model quality metrics | class CrossModelQuality | []
# NL_TAG_INTENT: VIF-INTENT-008 | Design decision: quality | CrossModelQuality | [ADR-TBD]
class CrossModelQuality:
    """Cross-model quality metrics"""
    
    quality_id: str = field(default_factory=lambda: f"qual_{uuid.uuid4().hex}")
    quality_timestamp: datetime = field(default_factory=datetime.now)
    
    # Quality Metrics
    overall_quality_score: float = 0.0
    quality_breakdown: Dict[str, float] = field(default_factory=dict)
    
    # Quality Preservation
    quality_preservation_score: float = 0.0
    quality_degradation: float = 0.0
    
    # Quality Validation
    quality_validation_results: List[ValidationResult] = field(default_factory=list)
    quality_confidence: float = 0.0
    
    # Quality Trends
    quality_trends: List[QualityTrend] = field(default_factory=list)
    quality_predictions: List[QualityPrediction] = field(default_factory=list)


@dataclass
# NL_TAG: VIF-MODEL-021 | Cross-model validation results | class CrossModelValidation | []
class CrossModelValidation:
    """Cross-model validation results"""
    
    validation_id: str = field(default_factory=lambda: f"val_{uuid.uuid4().hex}")
    validation_timestamp: datetime = field(default_factory=datetime.now)
    
    # Validation Scope
    validation_scope: str = ""
    validation_level: str = ""
    
    # Validation Results
    validation_results: List[ValidationResult] = field(default_factory=list)
    validation_confidence: float = 0.0
    
    # Validation Quality
    validation_quality_score: float = 0.0
    validation_completeness: float = 0.0
    
    # Validation Metrics
    validation_latency: float = 0.0
    validation_accuracy: float = 0.0
    validation_precision: float = 0.0


@dataclass
# NL_TAG: VIF-MODEL-022 | Replay configuration | class ReplayConfiguration | []
# NL_TAG_INTENT: VIF-INTENT-009 | Design decision: replay | ReplayConfiguration | [ADR-TBD]
class ReplayConfiguration:
    """Replay configuration"""
    
    config_id: str = field(default_factory=lambda: f"replay_config_{uuid.uuid4().hex}")
    config_timestamp: datetime = field(default_factory=datetime.now)
    
    # Configuration Settings
    replay_mode: str = "deterministic"
    replay_environment: str = "production"
    replay_timeout: float = 300.0
    
    # Configuration Options
    enable_validation: bool = True
    enable_metrics: bool = True
    enable_logging: bool = True
    
    # Configuration Parameters
    config_parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
# NL_TAG: VIF-MODEL-023 | Replay environment | class ReplayEnvironment | []
# NL_TAG_INTENT: VIF-INTENT-010 | Design decision: replay | ReplayEnvironment | [ADR-TBD]
class ReplayEnvironment:
    """Replay environment"""
    
    environment_id: str = field(default_factory=lambda: f"env_{uuid.uuid4().hex}")
    environment_timestamp: datetime = field(default_factory=datetime.now)
    
    # Environment Information
    environment_name: str = ""
    environment_type: str = ""
    environment_version: str = ""
    
    # Environment Configuration
    environment_config: Dict[str, Any] = field(default_factory=dict)
    environment_dependencies: List[str] = field(default_factory=list)
    
    # Environment Validation
    environment_valid: bool = False
    environment_validation: List[ValidationResult] = field(default_factory=list)


@dataclass
# NL_TAG: VIF-MODEL-024 | Data for replay | class ReplayData | []
# NL_TAG_INTENT: VIF-INTENT-011 | Design decision: replay | ReplayData | [ADR-TBD]
class ReplayData:
    """Data for replay"""
    
    data_id: str = field(default_factory=lambda: f"replay_data_{uuid.uuid4().hex}")
    data_timestamp: datetime = field(default_factory=datetime.now)
    
    # Data Information
    data_type: str = ""
    data_format: str = ""
    data_size: int = 0
    
    # Data Content
    data_content: Dict[str, Any] = field(default_factory=dict)
    data_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Data Validation
    data_valid: bool = False
    data_validation: List[ValidationResult] = field(default_factory=list)


@dataclass
# NL_TAG: VIF-MODEL-025 | Replay validation results | class ReplayValidation | []
# NL_TAG_INTENT: VIF-INTENT-012 | Design decision: replay | ReplayValidation | [ADR-TBD]
class ReplayValidation:
    """Replay validation results"""
    
    validation_id: str = field(default_factory=lambda: f"replay_val_{uuid.uuid4().hex}")
    validation_timestamp: datetime = field(default_factory=datetime.now)
    
    # Validation Results
    replay_valid: bool = False
    replay_accurate: bool = False
    replay_consistent: bool = False
    
    # Validation Metrics
    validation_confidence: float = 0.0
    validation_quality_score: float = 0.0
    
    # Validation Details
    validation_checks: List[str] = field(default_factory=list)
    validation_results: List[ValidationResult] = field(default_factory=list)


@dataclass
# NL_TAG: VIF-MODEL-026 | Deterministic replay capabilities | class DeterministicReplay | []
# NL_TAG_INTENT: VIF-INTENT-013 | Design decision: deterministic | DeterministicReplay | [ADR-TBD]
class DeterministicReplay:
    """Deterministic replay capabilities"""
    
    replay_id: str = field(default_factory=lambda: f"replay_{uuid.uuid4().hex}")
    replay_timestamp: datetime = field(default_factory=datetime.now)
    
    # Replay Configuration
    replay_configuration: ReplayConfiguration = field(default_factory=ReplayConfiguration)
    replay_environment: ReplayEnvironment = field(default_factory=ReplayEnvironment)
    
    # Replay Data
    replay_data: ReplayData = field(default_factory=ReplayData)
    replay_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Replay Validation
    replay_validation: ReplayValidation = field(default_factory=ReplayValidation)
    replay_accuracy: float = 0.0
    
    # Replay Metrics
    replay_latency: float = 0.0
    replay_success_rate: float = 0.0
    replay_consistency: float = 0.0


@dataclass
# NL_TAG: VIF-MODEL-027 | Cross-model performance metrics | class CrossModelMetrics | []
class CrossModelMetrics:
    """Cross-model performance metrics"""
    
    metrics_id: str = field(default_factory=lambda: f"metrics_{uuid.uuid4().hex}")
    metrics_timestamp: datetime = field(default_factory=datetime.now)
    
    # Metrics Information
    metrics_type: str = ""
    metrics_scope: str = ""
    
    # Metrics Data
    metrics_data: Dict[str, Any] = field(default_factory=dict)
    metrics_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Metrics Quality
    metrics_quality_score: float = 0.0
    metrics_confidence: float = 0.0


@dataclass
# NL_TAG: VIF-MODEL-028 | Analytics and insights | class AnalyticsData | []
class AnalyticsData:
    """Analytics and insights"""
    
    analytics_id: str = field(default_factory=lambda: f"analytics_{uuid.uuid4().hex}")
    analytics_timestamp: datetime = field(default_factory=datetime.now)
    
    # Analytics Information
    analytics_type: str = ""
    analytics_scope: str = ""
    
    # Analytics Data
    analytics_data: Dict[str, Any] = field(default_factory=dict)
    analytics_insights: List[str] = field(default_factory=list)
    
    # Analytics Quality
    analytics_quality_score: float = 0.0
    analytics_confidence: float = 0.0


# Main Cross-Model VIF Schema

@dataclass
# NL_TAG: VIF-MODEL-029 | Extended VIF schema for cross-model consciousness | class CrossModelVIF | []
class CrossModelVIF:
    """Extended VIF schema for cross-model consciousness"""
    
    # Identity
    vif_id: str = field(default_factory=lambda: f"vif_{uuid.uuid4().hex}")
    timestamp: datetime = field(default_factory=datetime.now)
    version: str = "2.0.0"
    
    # Cross-Model Information
    insight_model_id: str = ""
    insight_model_version: str = ""
    execution_model_id: str = ""
    execution_model_version: str = ""
    
    # Insight Information
    insight_id: str = ""
    insight_confidence: float = 0.0
    insight_quality_score: float = 0.0
    
    # Knowledge Transfer
    knowledge_transfer: KnowledgeTransfer = field(default_factory=KnowledgeTransfer)
    transfer_confidence: float = 0.0
    transfer_validation: TransferValidation = field(default_factory=TransferValidation)
    
    # Cross-Model Provenance
    cross_model_provenance: CrossModelProvenance = field(default_factory=CrossModelProvenance)
    model_interactions: List[ModelInteraction] = field(default_factory=list)
    
    # Cost Optimization
    cost_optimization: CostOptimization = field(default_factory=CostOptimization)
    cost_breakdown: Dict[str, float] = field(default_factory=dict)
    
    # Quality Assurance
    cross_model_quality: CrossModelQuality = field(default_factory=CrossModelQuality)
    quality_preservation: QualityPreservation = field(default_factory=QualityPreservation)
    
    # Validation & Replay
    cross_model_validation: CrossModelValidation = field(default_factory=CrossModelValidation)
    deterministic_replay: DeterministicReplay = field(default_factory=DeterministicReplay)
    
    # Monitoring & Analytics
    cross_model_metrics: CrossModelMetrics = field(default_factory=CrossModelMetrics)
    analytics_data: AnalyticsData = field(default_factory=AnalyticsData)
    
    # Legacy VIF Compatibility
    legacy_vif: Optional[VIF] = None
    
    # NL_TAG: VIF-MODEL-030 | Convert to dictionary | to_dict(self) | []
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "vif_id": self.vif_id,
            "timestamp": self.timestamp.isoformat(),
            "version": self.version,
            "insight_model_id": self.insight_model_id,
            "insight_model_version": self.insight_model_version,
            "execution_model_id": self.execution_model_id,
            "execution_model_version": self.execution_model_version,
            "insight_id": self.insight_id,
            "insight_confidence": self.insight_confidence,
            "insight_quality_score": self.insight_quality_score,
            "transfer_confidence": self.transfer_confidence,
            "cost_breakdown": self.cost_breakdown
        }
    
    # NL_TAG: VIF-MODEL-031 | Calculate hash of the VIF | calculate_hash(self) | []
    def calculate_hash(self) -> str:
        """Calculate hash of the VIF"""
        data = self.to_dict()
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    # NL_TAG: VIF-MODEL-032 | Validate the cross-model VIF | validate(self) | []
    # NL_TAG_SPEC: VIF-SPEC-001 | Validates validate specification | validate | [spec_file_TBD]
    def validate(self) -> List[ValidationResult]:
        """Validate the cross-model VIF"""
        validation_results = []
        
        # Validate required fields
        if not self.insight_model_id:
            validation_results.append(ValidationResult(
                field="insight_model_id",
                valid=False,
                message="Insight model ID is required"
            ))
        
        if not self.execution_model_id:
            validation_results.append(ValidationResult(
                field="execution_model_id",
                valid=False,
                message="Execution model ID is required"
            ))
        
        # Validate confidence scores
        if not 0.0 <= self.insight_confidence <= 1.0:
            validation_results.append(ValidationResult(
                field="insight_confidence",
                valid=False,
                message="Insight confidence must be between 0.0 and 1.0"
            ))
        
        if not 0.0 <= self.insight_quality_score <= 1.0:
            validation_results.append(ValidationResult(
                field="insight_quality_score",
                valid=False,
                message="Insight quality score must be between 0.0 and 1.0"
            ))
        
        # Validate transfer confidence
        if not 0.0 <= self.transfer_confidence <= 1.0:
            validation_results.append(ValidationResult(
                field="transfer_confidence",
                valid=False,
                message="Transfer confidence must be between 0.0 and 1.0"
            ))
        
        return validation_results
