"""VIF Integration for SDF-CVF

Enables VIF witnesses as quartet traces and quality validation.

Integration Points:
- Use VIF witnesses as quartet traces
- Validate change requests with VIF confidence
- Track provenance for quartet elements
- Generate verification reports
"""

from __future__ import annotations
import os
from typing import Dict, Any, Optional, List, Literal
from datetime import datetime, timezone

# VIF imports (optional)
try:
    from packages.vif.witness import VIF, ConfidenceBand
    from packages.vif.cmc_integration import create_witness_and_store
    VIF_AVAILABLE = True
except ImportError:
    # Fallback for environments without VIF
    VIF_AVAILABLE = False
    VIF = None
    ConfidenceBand = None
    create_witness_and_store = None


IntegrationMode = Literal["strict", "auto", "fallback", "mocked"]
_VALID_INTEGRATION_MODES = {"strict", "auto", "fallback", "mocked"}
_DEFAULT_INTEGRATION_MODE = os.getenv("AIMOS_SDFCVF_VIF_MODE", "strict")


def _resolve_integration_mode(integration_mode: Optional[IntegrationMode]) -> str:
    mode = (integration_mode or _DEFAULT_INTEGRATION_MODE).strip().lower()
    if mode not in _VALID_INTEGRATION_MODES:
        valid = ", ".join(sorted(_VALID_INTEGRATION_MODES))
        raise ValueError(f"Invalid integration_mode '{mode}'. Expected one of: {valid}")
    return mode


def _is_available(
    package_available: bool,
    integration_mode: str,
    client: Optional[Any] = None,
) -> bool:
    if integration_mode == "strict":
        return False
    if integration_mode in {"auto", "fallback"}:
        return package_available or client is not None
    return True


class VIFIntegration:
    """Integrates SDF-CVF with VIF for witness-based traces and quality validation.
    
    Provides:
    - VIF witnesses as quartet traces
    - Change validation with confidence checks
    - Provenance tracking for quartet elements
    - Verification report generation
    """
    
    def __init__(
        self,
        vif_client: Optional[Any] = None,
        integration_mode: Optional[IntegrationMode] = None,
    ):
        """
        Initialize VIF integration.
        
        Args:
            vif_client: VIF client instance (optional, for testing can be None)
        """
        self.integration_mode = _resolve_integration_mode(integration_mode)
        self.vif_available = _is_available(
            package_available=VIF_AVAILABLE,
            integration_mode=self.integration_mode,
            client=vif_client,
        )
        self.vif = vif_client
        
        if not self.vif_available:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning("VIF integration disabled: VIF package not available")
    
    def create_trace_witness(
        self,
        operation: str,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        confidence: float = 0.95
    ) -> Optional[Dict[str, Any]]:
        """
        Create VIF witness for quartet trace.
        
        Used by quartetDetector to create witnesses for quartet elements.
        
        Args:
            operation: Operation name (e.g., "detect_quartet", "calculate_parity")
            inputs: Input data for the operation
            outputs: Output data from the operation
            confidence: Confidence in the operation (0.0-1.0)
            
        Returns:
            VIF witness dictionary if successful, None if VIF not available
        """
        if not self.vif_available:
            return None
        
        try:
            # Create VIF witness directly (VIF is a Pydantic model)
            # Note: VIF requires context_snapshot_id, but we can use a placeholder for trace-only witnesses
            witness = VIF(
                model_id="sdfcvf-v1",
                model_provider="aether",
                context_snapshot_id="sdfcvf-trace-snapshot",  # Placeholder for trace-only witnesses
                prompt_hash=VIF.hash_text(str(inputs)) if hasattr(VIF, 'hash_text') else "",
                prompt_tokens=len(str(inputs).split()) if inputs else 0,
                confidence_score=confidence,
                confidence_band=ConfidenceBand.A if confidence >= 0.90 else (ConfidenceBand.B if confidence >= 0.70 else ConfidenceBand.C) if ConfidenceBand else None,
                output_hash=VIF.hash_text(str(outputs)) if hasattr(VIF, 'hash_text') else "",
                output_tokens=len(str(outputs).split()) if outputs else 0,
                total_tokens=len(str(inputs).split()) + len(str(outputs).split()) if inputs and outputs else 0,
            )
            
            # Add operation metadata to witness
            witness_metadata = witness.model_dump() if hasattr(witness, 'model_dump') else {
                "operation": operation,
                "inputs": inputs,
                "outputs": outputs,
                "confidence": confidence,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            return witness_metadata
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error creating VIF witness: {e}")
            return None
    
    def validate_change_request(
        self,
        change_request: Dict[str, Any],
        min_confidence: float = 0.70
    ) -> Dict[str, Any]:
        """
        Validate change request using VIF confidence checks.
        
        Used by qualityGateManager for quality validation.
        
        Args:
            change_request: Change request data
            min_confidence: Minimum confidence threshold
            
        Returns:
            Validation result with 'valid' and 'confidence' fields
        """
        if not self.vif_available:
            return {
                "valid": False,
                "error": "VIF not available",
                "confidence": 0.0
            }
        
        try:
            # Extract confidence from change request
            confidence = change_request.get("confidence", 0.95)
            
            valid = confidence >= min_confidence
            
            return {
                "valid": valid,
                "confidence": confidence,
                "min_confidence": min_confidence,
                "message": f"Change request {'valid' if valid else 'invalid'} (confidence: {confidence:.2f})"
            }
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error validating change request with VIF: {e}")
            return {
                "valid": False,
                "error": str(e),
                "confidence": 0.0
            }
    
    def get_provenance_trace(
        self,
        quartet_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get provenance trace for quartet from VIF.
        
        Used for traceability and audit purposes.
        
        Args:
            quartet_id: Unique identifier for the quartet
            
        Returns:
            Provenance trace dictionary if available, None otherwise
        """
        if not self.vif_available:
            return None
        
        try:
            # Simplified implementation (would query VIF for actual provenance)
            return {
                "quartet_id": quartet_id,
                "provenance": {
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "source": "sdfcvf",
                    "witnesses": []
                }
            }
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error getting provenance trace from VIF: {e}")
            return None
    
    def generate_verification_report(
        self,
        parity_result: Any,
        quartet_id: str
    ) -> Dict[str, Any]:
        """
        Generate verification report using VIF validation.
        
        Used for quality reporting and compliance.
        
        Args:
            parity_result: ParityResult or QuintetParityResult instance
            quartet_id: Unique identifier for the quartet
            
        Returns:
            Verification report dictionary
        """
        if not self.vif_available:
            return {
                "valid": False,
                "error": "VIF not available",
                "report": {}
            }
        
        try:
            parity_score = getattr(parity_result, 'parity_score', 0.0)
            complete = getattr(parity_result, 'complete', False)
            
            return {
                "valid": parity_score >= 0.90 and complete,
                "parity_score": parity_score,
                "complete": complete,
                "quartet_id": quartet_id,
                "verification_timestamp": datetime.now(timezone.utc).isoformat(),
                "report": {
                    "parity_validation": "passed" if parity_score >= 0.90 else "failed",
                    "completeness": "complete" if complete else "incomplete",
                    "recommendations": [] if parity_score >= 0.90 else [
                        "Improve quartet alignment",
                        "Ensure all quartet elements present"
                    ]
                }
            }
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error generating verification report with VIF: {e}")
            return {
                "valid": False,
                "error": str(e),
                "report": {}
            }

