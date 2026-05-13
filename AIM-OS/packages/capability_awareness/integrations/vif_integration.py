"""VIF Integration for CAF

Integrates CAF with VIF (Verifiable Intelligence Framework) for confidence
tracking, provenance, and behavioral abstention (κ-gating).
"""

from __future__ import annotations

from typing import Any, Dict, Optional

try:
    from vif import VIF, ConfidenceBand, TaskCriticality, KappaGate, create_witness_and_store
    VIF_AVAILABLE = True
except ImportError:
    VIF_AVAILABLE = False
    VIF = None
    ConfidenceBand = None
    TaskCriticality = None
    KappaGate = None
    create_witness_and_store = None


class VIFIntegration:
    """VIF integration for CAF confidence tracking"""
    
    def __init__(self, vif_service: Optional[Any] = None):
        """Initialize VIF integration
        
        Args:
            vif_service: Optional VIF service instance
        """
        self.vif_service = vif_service
        self.enabled = VIF_AVAILABLE
        
        if self.enabled:
            try:
                self.kappa_gate = KappaGate()
            except Exception:
                self.kappa_gate = None
        else:
            self.kappa_gate = None
    
    def track_confidence(
        self,
        task: str,
        confidence: float,
        task_criticality: TaskCriticality = TaskCriticality.ROUTINE,
        reasoning: str = "",
        evidence: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Track confidence using VIF
        
        Args:
            task: Task description
            confidence: Confidence score (0-1)
            task_criticality: Task criticality level
            reasoning: Reasoning for confidence
            evidence: Optional evidence list
            
        Returns:
            Dictionary with confidence tracking results
        """
        if not self.enabled or not self.kappa_gate:
            return {
                "tracked": False,
                "confidence": confidence,
                "message": "VIF not available"
            }
        
        try:
            # Check κ-gate
            gate_result = self.kappa_gate.check(confidence, task_criticality)
            
            # Determine confidence band
            if confidence >= 0.9:
                band = ConfidenceBand.A
            elif confidence >= 0.7:
                band = ConfidenceBand.B
            else:
                band = ConfidenceBand.C
            
            return {
                "tracked": True,
                "confidence": confidence,
                "confidence_band": band.value,
                "kappa_gate_passed": gate_result.passed,
                "kappa_gate_status": gate_result.status.value if hasattr(gate_result.status, 'value') else str(gate_result.status),
                "task_criticality": task_criticality.value,
                "reasoning": reasoning,
                "evidence": evidence or []
            }
        except Exception as e:
            return {
                "tracked": False,
                "confidence": confidence,
                "error": str(e)
            }
    
    def create_witness(
        self,
        model_id: str,
        context_snapshot_id: str,
        prompt_hash: str,
        confidence_score: float,
        output_hash: Optional[str] = None
    ) -> Optional[str]:
        """Create VIF witness for capability activation
        
        Args:
            model_id: Model identifier
            context_snapshot_id: CMC snapshot ID
            prompt_hash: Prompt hash
            confidence_score: Confidence score
            output_hash: Optional output hash
            
        Returns:
            Witness ID if created, None otherwise
        """
        if not self.enabled or not create_witness_and_store:
            return None
        
        try:
            witness = create_witness_and_store(
                model_id=model_id,
                context_snapshot_id=context_snapshot_id,
                prompt_hash=prompt_hash,
                confidence_score=confidence_score,
                output_hash=output_hash
            )
            return witness.id if witness else None
        except Exception:
            return None

