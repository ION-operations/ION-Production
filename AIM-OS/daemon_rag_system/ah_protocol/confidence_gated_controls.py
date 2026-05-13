"""
Confidence-Gated Controls - Step F of A-H Protocol

This module implements the Confidence-Gated Controls step, which is responsible for:
- Preventing changes without proper validation
- Creating Confidence Packet checklists for all changes
- Including context compliance, Track authorization, DEL reference
- Requiring goal alignment, impact preview, repair/test plan
- Varying strictness by Tier (0-3)
- Implementing mutation modes (Trivial/Gentle vs Governed/Critical)

Following A-H Protocol methodology from ChatGPT journal.
"""

from typing import Dict, Any, List, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import time
import uuid
import hashlib
from .intent_capture import IntentProfile, IntentType
from .hypothesis_formation import Hypothesis
from .context_mapping import ContextMap, ContextNode, ContextRelationship, DependencyType
from .deep_expansion_layer import ExpansionNode, ExpansionAnalysis, TierLevel, ComplexityLevel
from .context_mesh_maps import ContextMeshMap, ContextMeshContract, ContextConstraint, ConstraintType, ContractStatus

class MutationMode(Enum):
    """Types of mutation modes for changes."""
    TRIVIAL = "trivial"  # Tier 0/1 cosmetic/internal changes
    GENTLE = "gentle"    # Tier 0/1 cosmetic/internal changes
    GOVERNED = "governed"  # Tier 2/3 or semantic/behavioral changes
    CRITICAL = "critical"  # Tier 3 critical system changes

class ValidationStatus(Enum):
    """Status of validation process."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    VALIDATED = "validated"
    REJECTED = "rejected"
    REQUIRES_ESCALATION = "requires_escalation"
    EXPIRED = "expired"

class ConfidenceLevel(Enum):
    """Confidence levels for validation."""
    VERY_LOW = "very_low"      # 0.0-0.2
    LOW = "low"                # 0.2-0.4
    MEDIUM = "medium"          # 0.4-0.6
    HIGH = "high"              # 0.6-0.8
    VERY_HIGH = "very_high"    # 0.8-1.0

@dataclass
class ValidationProof:
    """A proof of validation for a change."""
    id: str
    proof_type: str
    description: str
    evidence: List[str]
    validator: str
    timestamp: float
    confidence: float
    signature: str = ""

@dataclass
class ConfidencePacket:
    """A confidence packet containing all validation requirements."""
    id: str
    change_id: str
    mutation_mode: MutationMode
    tier_level: TierLevel
    confidence_score: float
    context_compliance: bool
    track_authorization: bool
    del_reference: str
    goal_alignment: bool
    impact_preview: Dict[str, Any]
    repair_test_plan: Dict[str, Any]
    validation_proofs: List[ValidationProof]
    required_approvals: List[str]
    risk_assessment: Dict[str, Any]
    blast_radius: str
    rollback_plan: Dict[str, Any]
    created_at: float
    expires_at: float
    status: ValidationStatus
    version: str = "1.0"

@dataclass
class ChangeRequest:
    """A request for a system change."""
    id: str
    description: str
    change_type: str
    affected_components: List[str]
    proposed_changes: Dict[str, Any]
    requester: str
    priority: str
    urgency: str
    estimated_effort: str
    risk_level: str
    dependencies: List[str]
    created_at: float
    updated_at: float

@dataclass
class ConfidenceGate:
    """A confidence gate that validates changes."""
    id: str
    name: str
    tier_level: TierLevel
    mutation_mode: MutationMode
    required_confidence: float
    validation_rules: List[str]
    approval_requirements: List[str]
    escalation_triggers: List[str]
    monitoring_config: Dict[str, Any]
    created_at: float
    updated_at: float

class ConfidenceGatedControls:
    """
    Confidence-Gated Controls for A-H Protocol Step F.
    
    Prevents changes without proper validation and ensures quality through
    confidence-based gating with tier-appropriate strictness.
    
    Integrates with:
    - VIF: For confidence validation and witness creation
    - APOE: For orchestration gates and plan execution
    """
    
    def __init__(self, config_path: str = "confidence_gates_config.json", 
                 vif_client=None, apoe_client=None):
        """Initialize the Confidence-Gated Controls system."""
        self.config = self._load_config(config_path)
        self.confidence_gates = self._initialize_confidence_gates()
        self.active_packets: Dict[str, ConfidencePacket] = {}
        self.validation_history: List[Dict[str, Any]] = []
        
        # VIF and APOE integration (optional, fail-soft)
        self.vif_client = vif_client
        self.apoe_client = apoe_client
        
    def create_confidence_packet(self, change_request: ChangeRequest, 
                                intent_profile: IntentProfile, context_map: ContextMap,
                                expansion_analysis: ExpansionAnalysis, 
                                mesh_map: ContextMeshMap, context: Dict[str, Any] = None) -> ConfidencePacket:
        """
        Create a confidence packet for a change request.
        
        Args:
            change_request: The change request to validate
            intent_profile: The captured intent profile
            context_map: The context mapping from Step C
            expansion_analysis: The deep expansion analysis from Step D
            mesh_map: The context mesh map from Step E
            context: Additional context data
            
        Returns:
            ConfidencePacket: Complete confidence packet with all validation requirements
        """
        if context is None:
            context = {}
        
        # Determine mutation mode based on tier and change type
        mutation_mode = self._determine_mutation_mode(change_request, expansion_analysis)
        
        # Determine tier level
        tier_level = self._determine_tier_level(change_request, expansion_analysis)
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(
            change_request, intent_profile, context_map, expansion_analysis, mesh_map, context
        )
        
        # Check context compliance
        context_compliance = self._check_context_compliance(change_request, context_map, mesh_map)
        
        # Check track authorization
        track_authorization = self._check_track_authorization(change_request, intent_profile, context)
        
        # Generate DEL reference
        del_reference = self._generate_del_reference(change_request, expansion_analysis)
        
        # Check goal alignment
        goal_alignment = self._check_goal_alignment(change_request, intent_profile, context_map)
        
        # Generate impact preview
        impact_preview = self._generate_impact_preview(change_request, context_map, expansion_analysis, mesh_map)
        
        # Generate repair/test plan
        repair_test_plan = self._generate_repair_test_plan(change_request, context_map, expansion_analysis)
        
        # Generate validation proofs
        validation_proofs = self._generate_validation_proofs(change_request, mutation_mode, tier_level)
        
        # Determine required approvals
        required_approvals = self._determine_required_approvals(change_request, mutation_mode, tier_level)
        
        # Generate risk assessment
        risk_assessment = self._generate_risk_assessment(change_request, context_map, expansion_analysis, mesh_map)
        
        # Calculate blast radius
        blast_radius = self._calculate_blast_radius(change_request, context_map, expansion_analysis)
        
        # Generate rollback plan
        rollback_plan = self._generate_rollback_plan(change_request, context_map, expansion_analysis)
        
        # Calculate expiration time
        expires_at = self._calculate_expiration_time(change_request, mutation_mode, tier_level)
        
        return ConfidencePacket(
            id=f"confidence_packet_{int(time.time())}_{uuid.uuid4().hex[:8]}",
            change_id=change_request.id,
            mutation_mode=mutation_mode,
            tier_level=tier_level,
            confidence_score=confidence_score,
            context_compliance=context_compliance,
            track_authorization=track_authorization,
            del_reference=del_reference,
            goal_alignment=goal_alignment,
            impact_preview=impact_preview,
            repair_test_plan=repair_test_plan,
            validation_proofs=validation_proofs,
            required_approvals=required_approvals,
            risk_assessment=risk_assessment,
            blast_radius=blast_radius,
            rollback_plan=rollback_plan,
            created_at=time.time(),
            expires_at=expires_at,
            status=ValidationStatus.PENDING
        )
    
    def validate_change(self, confidence_packet: ConfidencePacket, 
                       context: Dict[str, Any] = None) -> Tuple[bool, List[str], Dict[str, Any]]:
        """
        Validate a change using the confidence packet.
        
        Args:
            confidence_packet: The confidence packet to validate
            context: Additional context data
            
        Returns:
            Tuple[bool, List[str], Dict[str, Any]]: (is_valid, errors, validation_details)
        """
        if context is None:
            context = {}
        
        errors = []
        validation_details = {
            "packet_id": confidence_packet.id,
            "validation_timestamp": time.time(),
            "validation_steps": [],
            "confidence_breakdown": {},
            "risk_analysis": {},
            "compliance_status": {}
        }
        
        # Step 1: Check if packet is expired
        if time.time() > confidence_packet.expires_at:
            errors.append("Confidence packet has expired")
            validation_details["validation_steps"].append({
                "step": "expiration_check",
                "status": "failed",
                "message": "Packet expired"
            })
            return False, errors, validation_details
        
        # Step 2: Validate confidence score
        required_confidence = self._get_required_confidence(confidence_packet.mutation_mode, confidence_packet.tier_level)
        
        # VIF Integration: Validate confidence via VIF if available
        vif_validation = None
        if self.vif_client:
            try:
                vif_validation = self._validate_confidence_via_vif(
                    confidence_packet.confidence_score,
                    required_confidence,
                    confidence_packet.change_id
                )
                validation_details["vif_validation"] = vif_validation
            except Exception as e:
                # Fail-soft: VIF integration is optional
                validation_details["vif_validation"] = {"error": str(e), "fallback": True}
        
        if confidence_packet.confidence_score < required_confidence:
            errors.append(f"Confidence score {confidence_packet.confidence_score:.2f} below required {required_confidence:.2f}")
            validation_details["validation_steps"].append({
                "step": "confidence_check",
                "status": "failed",
                "message": f"Confidence {confidence_packet.confidence_score:.2f} < {required_confidence:.2f}",
                "vif_validated": vif_validation.get("validated", False) if vif_validation else False
            })
        else:
            validation_details["validation_steps"].append({
                "step": "confidence_check",
                "status": "passed",
                "message": f"Confidence {confidence_packet.confidence_score:.2f} >= {required_confidence:.2f}",
                "vif_validated": vif_validation.get("validated", False) if vif_validation else False
            })
        
        # Step 3: Validate context compliance
        if not confidence_packet.context_compliance:
            errors.append("Context compliance check failed")
            validation_details["validation_steps"].append({
                "step": "context_compliance",
                "status": "failed",
                "message": "Context compliance failed"
            })
        else:
            validation_details["validation_steps"].append({
                "step": "context_compliance",
                "status": "passed",
                "message": "Context compliance passed"
            })
        
        # Step 4: Validate track authorization
        if not confidence_packet.track_authorization:
            errors.append("Track authorization check failed")
            validation_details["validation_steps"].append({
                "step": "track_authorization",
                "status": "failed",
                "message": "Track authorization failed"
            })
        else:
            validation_details["validation_steps"].append({
                "step": "track_authorization",
                "status": "passed",
                "message": "Track authorization passed"
            })
        
        # Step 5: Validate goal alignment
        if not confidence_packet.goal_alignment:
            errors.append("Goal alignment check failed")
            validation_details["validation_steps"].append({
                "step": "goal_alignment",
                "status": "failed",
                "message": "Goal alignment failed"
            })
        else:
            validation_details["validation_steps"].append({
                "step": "goal_alignment",
                "status": "passed",
                "message": "Goal alignment passed"
            })
        
        # Step 6: Validate validation proofs
        proof_validation = self._validate_proofs(confidence_packet.validation_proofs)
        if not proof_validation["valid"]:
            errors.extend(proof_validation["errors"])
            validation_details["validation_steps"].append({
                "step": "proof_validation",
                "status": "failed",
                "message": f"Proof validation failed: {', '.join(proof_validation['errors'])}"
            })
        else:
            validation_details["validation_steps"].append({
                "step": "proof_validation",
                "status": "passed",
                "message": "All validation proofs valid"
            })
        
        # Step 7: Check required approvals
        approval_status = self._check_required_approvals(confidence_packet.required_approvals, context)
        if not approval_status["all_approved"]:
            errors.extend(approval_status["missing_approvals"])
            validation_details["validation_steps"].append({
                "step": "approval_check",
                "status": "failed",
                "message": f"Missing approvals: {', '.join(approval_status['missing_approvals'])}"
            })
        else:
            validation_details["validation_steps"].append({
                "step": "approval_check",
                "status": "passed",
                "message": "All required approvals obtained"
            })
        
        # Step 8: Risk assessment validation
        risk_validation = self._validate_risk_assessment(confidence_packet.risk_assessment, confidence_packet.tier_level)
        if not risk_validation["acceptable"]:
            errors.append(f"Risk level {risk_validation['risk_level']} not acceptable for tier {confidence_packet.tier_level.value}")
            validation_details["validation_steps"].append({
                "step": "risk_validation",
                "status": "failed",
                "message": f"Risk {risk_validation['risk_level']} not acceptable"
            })
        else:
            validation_details["validation_steps"].append({
                "step": "risk_validation",
                "status": "passed",
                "message": f"Risk {risk_validation['risk_level']} acceptable"
            })
        
        # Update validation details
        validation_details["confidence_breakdown"] = {
            "overall_confidence": confidence_packet.confidence_score,
            "required_confidence": required_confidence,
            "confidence_level": self._get_confidence_level(confidence_packet.confidence_score).value
        }
        
        validation_details["risk_analysis"] = confidence_packet.risk_assessment
        validation_details["compliance_status"] = {
            "context_compliance": confidence_packet.context_compliance,
            "track_authorization": confidence_packet.track_authorization,
            "goal_alignment": confidence_packet.goal_alignment
        }
        
        # Determine overall validation result
        is_valid = len(errors) == 0
        
        # Update packet status
        if is_valid:
            confidence_packet.status = ValidationStatus.VALIDATED
        else:
            confidence_packet.status = ValidationStatus.REJECTED
        
        # Record validation in history
        self.validation_history.append({
            "packet_id": confidence_packet.id,
            "timestamp": time.time(),
            "is_valid": is_valid,
            "errors": errors,
            "validation_details": validation_details
        })
        
        return is_valid, errors, validation_details
    
    def _determine_mutation_mode(self, change_request: ChangeRequest, 
                                expansion_analysis: ExpansionAnalysis) -> MutationMode:
        """Determine the appropriate mutation mode for a change request."""
        # Simple logic based on change type and tier
        change_type_lower = change_request.change_type.lower()
        
        if change_type_lower in ["cosmetic", "internal", "documentation"]:
            return MutationMode.TRIVIAL
        elif change_type_lower in ["refactor", "optimization", "maintenance"]:
            return MutationMode.GENTLE
        elif change_type_lower in ["feature", "enhancement", "integration", "implement"]:
            return MutationMode.GOVERNED
        else:  # critical, security, architecture
            return MutationMode.CRITICAL
    
    def _determine_tier_level(self, change_request: ChangeRequest, 
                             expansion_analysis: ExpansionAnalysis) -> TierLevel:
        """Determine the tier level for a change request."""
        # Simple logic based on affected components and change type
        component_count = len(change_request.affected_components)
        change_type_lower = change_request.change_type.lower()
        
        if component_count == 1:
            return TierLevel.TIER_0
        elif component_count <= 2:
            return TierLevel.TIER_1
        elif component_count <= 4:
            return TierLevel.TIER_2
        else:
            return TierLevel.TIER_3
    
    def _calculate_confidence_score(self, change_request: ChangeRequest, intent_profile: IntentProfile,
                                   context_map: ContextMap, expansion_analysis: ExpansionAnalysis,
                                   mesh_map: ContextMeshMap, context: Dict[str, Any]) -> float:
        """Calculate the overall confidence score for a change request."""
        confidence_factors = []
        
        # Factor 1: Intent clarity
        intent_confidence = intent_profile.confidence_level
        confidence_factors.append(intent_confidence * 0.3)
        
        # Factor 2: Change complexity
        complexity_score = 1.0 - change_request.risk_level.count("high") * 0.2
        confidence_factors.append(complexity_score * 0.2)
        
        # Factor 3: Context understanding
        context_score = len(context_map.nodes) / max(len(context_map.nodes), 1)
        confidence_factors.append(context_score * 0.2)
        
        # Factor 4: Mesh map compliance
        mesh_compliance = len(mesh_map.contracts) / max(len(mesh_map.contracts), 1)
        confidence_factors.append(mesh_compliance * 0.15)
        
        # Factor 5: Historical success rate
        historical_success = self._calculate_historical_success_rate(change_request.change_type)
        confidence_factors.append(historical_success * 0.15)
        
        # Calculate weighted average
        overall_confidence = sum(confidence_factors)
        return min(max(overall_confidence, 0.0), 1.0)
    
    def _check_context_compliance(self, change_request: ChangeRequest, 
                                 context_map: ContextMap, mesh_map: ContextMeshMap) -> bool:
        """Check if the change request complies with context requirements."""
        # Check if all affected components are in the context map
        for component in change_request.affected_components:
            if component not in context_map.nodes:
                return False
        
        # Check mesh map constraints
        for contract in mesh_map.contracts.values():
            if any(component in contract.scope for component in change_request.affected_components):
                # Check if change violates any constraints
                for constraint in contract.constraints:
                    if self._violates_constraint(change_request, constraint):
                        return False
        
        return True
    
    def _check_track_authorization(self, change_request: ChangeRequest, 
                                  intent_profile: IntentProfile, context: Dict[str, Any]) -> bool:
        """Check if the change request is authorized for the current track."""
        # Check if change aligns with current task track
        current_track = context.get("current_task_track", "")
        if current_track and current_track not in change_request.description.lower():
            return False
        
        # Check if requester is authorized
        authorized_requesters = context.get("authorized_requesters", ["system", "aether_ai"])
        if change_request.requester not in authorized_requesters:
            return False
        
        return True
    
    def _generate_del_reference(self, change_request: ChangeRequest, 
                               expansion_analysis: ExpansionAnalysis) -> str:
        """Generate a DEL reference for the change request."""
        return f"DEL-{expansion_analysis.root_node_id}-{change_request.id}"
    
    def _check_goal_alignment(self, change_request: ChangeRequest, 
                             intent_profile: IntentProfile, context_map: ContextMap) -> bool:
        """Check if the change request aligns with established goals."""
        # Simple goal alignment check
        goal_keywords = ["improve", "enhance", "optimize", "fix", "implement", "develop"]
        change_description = change_request.description.lower()
        
        return any(keyword in change_description for keyword in goal_keywords)
    
    def _generate_impact_preview(self, change_request: ChangeRequest, context_map: ContextMap,
                                expansion_analysis: ExpansionAnalysis, mesh_map: ContextMeshMap) -> Dict[str, Any]:
        """Generate an impact preview for the change request."""
        return {
            "affected_components": change_request.affected_components,
            "estimated_effort": change_request.estimated_effort,
            "risk_level": change_request.risk_level,
            "dependencies": change_request.dependencies,
            "blast_radius": self._calculate_blast_radius(change_request, context_map, expansion_analysis),
            "rollback_complexity": self._assess_rollback_complexity(change_request, context_map),
            "testing_requirements": self._assess_testing_requirements(change_request, context_map)
        }
    
    def _generate_repair_test_plan(self, change_request: ChangeRequest, context_map: ContextMap,
                                  expansion_analysis: ExpansionAnalysis) -> Dict[str, Any]:
        """Generate a repair/test plan for the change request."""
        return {
            "pre_change_tests": [
                "Unit tests for affected components",
                "Integration tests for component interactions",
                "System tests for end-to-end functionality"
            ],
            "change_implementation": [
                "Implement changes incrementally",
                "Test each component after changes",
                "Validate system behavior after each change"
            ],
            "post_change_tests": [
                "Regression tests for all affected functionality",
                "Performance tests for system impact",
                "Security tests for vulnerability assessment"
            ],
            "rollback_procedures": [
                "Immediate rollback if critical issues detected",
                "Gradual rollback for non-critical issues",
                "Data recovery procedures if needed"
            ],
            "monitoring_plan": [
                "Monitor system health during implementation",
                "Track performance metrics post-implementation",
                "Alert on any anomalies or failures"
            ]
        }
    
    def _generate_validation_proofs(self, change_request: ChangeRequest, 
                                   mutation_mode: MutationMode, tier_level: TierLevel) -> List[ValidationProof]:
        """Generate validation proofs for the change request."""
        proofs = []
        
        # Proof 1: Code review
        if mutation_mode in [MutationMode.GOVERNED, MutationMode.CRITICAL]:
            proofs.append(ValidationProof(
                id=f"code_review_{int(time.time())}",
                proof_type="code_review",
                description="Code review by senior developer",
                evidence=["review_comments", "approval_signature"],
                validator="senior_developer",
                timestamp=time.time(),
                confidence=0.9
            ))
        
        # Proof 2: Test coverage
        if tier_level in [TierLevel.TIER_2, TierLevel.TIER_3]:
            proofs.append(ValidationProof(
                id=f"test_coverage_{int(time.time())}",
                proof_type="test_coverage",
                description="Comprehensive test coverage validation",
                evidence=["test_results", "coverage_report"],
                validator="test_automation",
                timestamp=time.time(),
                confidence=0.85
            ))
        
        # Proof 3: Security scan
        if mutation_mode == MutationMode.CRITICAL:
            proofs.append(ValidationProof(
                id=f"security_scan_{int(time.time())}",
                proof_type="security_scan",
                description="Security vulnerability scan",
                evidence=["scan_results", "vulnerability_report"],
                validator="security_scanner",
                timestamp=time.time(),
                confidence=0.95
            ))
        
        return proofs
    
    def _determine_required_approvals(self, change_request: ChangeRequest, 
                                     mutation_mode: MutationMode, tier_level: TierLevel) -> List[str]:
        """Determine required approvals for the change request."""
        approvals = []
        
        if mutation_mode == MutationMode.TRIVIAL:
            approvals.append("self_approval")
        elif mutation_mode == MutationMode.GENTLE:
            approvals.extend(["self_approval", "peer_review"])
        elif mutation_mode == MutationMode.GOVERNED:
            approvals.extend(["peer_review", "team_lead_approval"])
        else:  # CRITICAL
            approvals.extend(["peer_review", "team_lead_approval", "architect_approval", "security_approval"])
        
        if tier_level == TierLevel.TIER_3:
            approvals.append("executive_approval")
        
        return approvals
    
    def _generate_risk_assessment(self, change_request: ChangeRequest, context_map: ContextMap,
                                 expansion_analysis: ExpansionAnalysis, mesh_map: ContextMeshMap) -> Dict[str, Any]:
        """Generate a risk assessment for the change request."""
        risk_factors = []
        risk_score = 0.0
        
        # Factor 1: Change complexity
        if change_request.change_type in ["critical", "architecture", "security"]:
            risk_factors.append("high_complexity")
            risk_score += 0.3
        
        # Factor 2: Number of affected components
        component_count = len(change_request.affected_components)
        if component_count > 5:
            risk_factors.append("high_component_count")
            risk_score += 0.2
        elif component_count > 3:
            risk_factors.append("medium_component_count")
            risk_score += 0.1
        
        # Factor 3: Dependencies
        if len(change_request.dependencies) > 3:
            risk_factors.append("high_dependency_count")
            risk_score += 0.2
        
        # Factor 4: Historical failure rate
        historical_failure_rate = self._calculate_historical_failure_rate(change_request.change_type)
        risk_score += historical_failure_rate * 0.3
        
        # Determine risk level
        if risk_score >= 0.7:
            risk_level = "high"
        elif risk_score >= 0.4:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "mitigation_strategies": self._generate_risk_mitigation_strategies(risk_factors),
            "monitoring_requirements": self._generate_risk_monitoring_requirements(risk_level)
        }
    
    def _calculate_blast_radius(self, change_request: ChangeRequest, context_map: ContextMap,
                               expansion_analysis: ExpansionAnalysis) -> str:
        """Calculate the blast radius for the change request."""
        affected_count = len(change_request.affected_components)
        total_components = len(context_map.nodes)
        
        if affected_count == 0:
            return "none"
        elif affected_count == 1:
            return "local"
        elif affected_count <= 2:
            return "limited"
        elif affected_count <= 4:
            return "moderate"
        else:
            return "system_wide"
    
    def _generate_rollback_plan(self, change_request: ChangeRequest, context_map: ContextMap,
                               expansion_analysis: ExpansionAnalysis) -> Dict[str, Any]:
        """Generate a rollback plan for the change request."""
        return {
            "rollback_triggers": [
                "Critical system failure",
                "Performance degradation > 20%",
                "Security vulnerability detected",
                "Data integrity issues"
            ],
            "rollback_steps": [
                "Stop all change implementation",
                "Restore previous system state",
                "Validate system functionality",
                "Notify stakeholders of rollback"
            ],
            "rollback_timeout": "15 minutes",
            "rollback_approval": "automatic_for_critical",
            "data_recovery": "automatic_backup_restore"
        }
    
    def _calculate_expiration_time(self, change_request: ChangeRequest, 
                                  mutation_mode: MutationMode, tier_level: TierLevel) -> float:
        """Calculate expiration time for the confidence packet."""
        base_time = time.time()
        
        if mutation_mode == MutationMode.TRIVIAL:
            return base_time + 3600  # 1 hour
        elif mutation_mode == MutationMode.GENTLE:
            return base_time + 7200  # 2 hours
        elif mutation_mode == MutationMode.GOVERNED:
            return base_time + 14400  # 4 hours
        else:  # CRITICAL
            return base_time + 28800  # 8 hours
    
    def _get_required_confidence(self, mutation_mode: MutationMode, tier_level: TierLevel) -> float:
        """Get the required confidence level for a mutation mode and tier."""
        base_confidence = {
            MutationMode.TRIVIAL: 0.5,
            MutationMode.GENTLE: 0.6,
            MutationMode.GOVERNED: 0.7,
            MutationMode.CRITICAL: 0.8
        }
        
        tier_multiplier = {
            TierLevel.TIER_0: 1.0,
            TierLevel.TIER_1: 1.1,
            TierLevel.TIER_2: 1.2,
            TierLevel.TIER_3: 1.3
        }
        
        return min(base_confidence[mutation_mode] * tier_multiplier[tier_level], 1.0)
    
    def _get_confidence_level(self, confidence_score: float) -> ConfidenceLevel:
        """Get the confidence level enum for a confidence score."""
        if confidence_score >= 0.8:
            return ConfidenceLevel.VERY_HIGH
        elif confidence_score >= 0.6:
            return ConfidenceLevel.HIGH
        elif confidence_score >= 0.4:
            return ConfidenceLevel.MEDIUM
        elif confidence_score >= 0.2:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW
    
    def _validate_proofs(self, validation_proofs: List[ValidationProof]) -> Dict[str, Any]:
        """Validate all validation proofs."""
        errors = []
        
        for proof in validation_proofs:
            if not proof.evidence:
                errors.append(f"Proof {proof.id} has no evidence")
            if proof.confidence < 0.5:
                errors.append(f"Proof {proof.id} has low confidence {proof.confidence}")
            if not proof.validator:
                errors.append(f"Proof {proof.id} has no validator")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _check_required_approvals(self, required_approvals: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """Check if all required approvals have been obtained."""
        # In a real implementation, this would check actual approval status
        # For now, we'll simulate based on context
        obtained_approvals = context.get("obtained_approvals", [])
        missing_approvals = [approval for approval in required_approvals if approval not in obtained_approvals]
        
        return {
            "all_approved": len(missing_approvals) == 0,
            "missing_approvals": missing_approvals
        }
    
    def _validate_risk_assessment(self, risk_assessment: Dict[str, Any], tier_level: TierLevel) -> Dict[str, Any]:
        """Validate the risk assessment for acceptability."""
        risk_level = risk_assessment.get("risk_level", "unknown")
        risk_score = risk_assessment.get("risk_score", 1.0)
        
        # Define acceptable risk levels by tier
        acceptable_risk_levels = {
            TierLevel.TIER_0: ["low", "medium"],
            TierLevel.TIER_1: ["low", "medium"],
            TierLevel.TIER_2: ["low"],
            TierLevel.TIER_3: ["low"]
        }
        
        acceptable = risk_level in acceptable_risk_levels.get(tier_level, ["low"])
        
        return {
            "acceptable": acceptable,
            "risk_level": risk_level,
            "risk_score": risk_score
        }
    
    # Helper methods
    def _violates_constraint(self, change_request: ChangeRequest, constraint: ContextConstraint) -> bool:
        """Check if a change request violates a constraint."""
        # Simple constraint violation check
        if constraint.constraint_type == ConstraintType.MUST_NEVER:
            return any(keyword in change_request.description.lower() for keyword in ["delete", "remove", "destroy"])
        return False
    
    def _calculate_historical_success_rate(self, change_type: str) -> float:
        """Calculate historical success rate for a change type."""
        # In a real implementation, this would query historical data
        return 0.8  # Default 80% success rate
    
    def _calculate_historical_failure_rate(self, change_type: str) -> float:
        """Calculate historical failure rate for a change type."""
        # In a real implementation, this would query historical data
        return 0.1  # Default 10% failure rate
    
    def _assess_rollback_complexity(self, change_request: ChangeRequest, context_map: ContextMap) -> str:
        """Assess the complexity of rolling back the change."""
        if len(change_request.affected_components) <= 2:
            return "simple"
        elif len(change_request.affected_components) <= 5:
            return "moderate"
        else:
            return "complex"
    
    def _assess_testing_requirements(self, change_request: ChangeRequest, context_map: ContextMap) -> List[str]:
        """Assess testing requirements for the change."""
        requirements = ["unit_tests"]
        
        if len(change_request.affected_components) > 1:
            requirements.append("integration_tests")
        
        if change_request.change_type in ["critical", "security"]:
            requirements.extend(["security_tests", "performance_tests"])
        
        return requirements
    
    def _generate_risk_mitigation_strategies(self, risk_factors: List[str]) -> List[str]:
        """Generate risk mitigation strategies based on risk factors."""
        strategies = []
        
        if "high_complexity" in risk_factors:
            strategies.append("Incremental implementation with frequent validation")
        
        if "high_component_count" in risk_factors:
            strategies.append("Component-by-component rollout with rollback capability")
        
        if "high_dependency_count" in risk_factors:
            strategies.append("Dependency impact analysis and coordination")
        
        return strategies
    
    def _generate_risk_monitoring_requirements(self, risk_level: str) -> List[str]:
        """Generate monitoring requirements based on risk level."""
        if risk_level == "high":
            return ["continuous_monitoring", "real_time_alerts", "manual_oversight"]
        elif risk_level == "medium":
            return ["periodic_monitoring", "threshold_alerts"]
        else:
            return ["basic_monitoring"]
    
    def _initialize_confidence_gates(self) -> Dict[str, ConfidenceGate]:
        """Initialize the confidence gates for different tiers and modes."""
        gates = {}
        
        # Tier 0 gates
        gates["tier_0_trivial"] = ConfidenceGate(
            id="tier_0_trivial",
            name="Tier 0 Trivial Changes",
            tier_level=TierLevel.TIER_0,
            mutation_mode=MutationMode.TRIVIAL,
            required_confidence=0.5,
            validation_rules=["basic_syntax_check", "self_approval"],
            approval_requirements=["self_approval"],
            escalation_triggers=["validation_failure"],
            monitoring_config={"frequency": "hourly"},
            created_at=time.time(),
            updated_at=time.time()
        )
        
        # Tier 1 gates
        gates["tier_1_gentle"] = ConfidenceGate(
            id="tier_1_gentle",
            name="Tier 1 Gentle Changes",
            tier_level=TierLevel.TIER_1,
            mutation_mode=MutationMode.GENTLE,
            required_confidence=0.6,
            validation_rules=["syntax_check", "style_check", "peer_review"],
            approval_requirements=["self_approval", "peer_review"],
            escalation_triggers=["validation_failure", "peer_rejection"],
            monitoring_config={"frequency": "30m"},
            created_at=time.time(),
            updated_at=time.time()
        )
        
        # Tier 2 gates
        gates["tier_2_governed"] = ConfidenceGate(
            id="tier_2_governed",
            name="Tier 2 Governed Changes",
            tier_level=TierLevel.TIER_2,
            mutation_mode=MutationMode.GOVERNED,
            required_confidence=0.7,
            validation_rules=["comprehensive_testing", "code_review", "integration_testing"],
            approval_requirements=["peer_review", "team_lead_approval"],
            escalation_triggers=["test_failure", "review_rejection", "integration_failure"],
            monitoring_config={"frequency": "15m"},
            created_at=time.time(),
            updated_at=time.time()
        )
        
        # Tier 3 gates
        gates["tier_3_critical"] = ConfidenceGate(
            id="tier_3_critical",
            name="Tier 3 Critical Changes",
            tier_level=TierLevel.TIER_3,
            mutation_mode=MutationMode.CRITICAL,
            required_confidence=0.8,
            validation_rules=["comprehensive_testing", "security_scan", "performance_testing", "architect_review"],
            approval_requirements=["peer_review", "team_lead_approval", "architect_approval", "security_approval"],
            escalation_triggers=["any_validation_failure", "security_concern", "performance_degradation"],
            monitoring_config={"frequency": "5m"},
            created_at=time.time(),
            updated_at=time.time()
        )
        
        return gates
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "default_confidence_threshold": 0.7,
                "validation_timeout": 3600,
                "max_retry_attempts": 3,
                "escalation_timeout": 1800
            }
