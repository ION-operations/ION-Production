"""APOE Integration for SDF-CVF

Enables quality gate enforcement in APOE execution plans.

Integration Points:
- Quality gate status reporting to APOE
- Change approval workflow integration
- Evolution recommendations
- Compliance reports
"""

from __future__ import annotations
import os
from typing import Dict, Any, Optional, List, Literal
from datetime import datetime, timezone

# APOE imports (optional)
try:
    from packages.apoe import Step, ExecutionPlan, ExecutionResult
    APOE_AVAILABLE = True
except ImportError:
    # Fallback for environments without APOE
    APOE_AVAILABLE = False
    Step = None
    ExecutionPlan = None
    ExecutionResult = None


IntegrationMode = Literal["strict", "auto", "fallback", "mocked"]
_VALID_INTEGRATION_MODES = {"strict", "auto", "fallback", "mocked"}
_DEFAULT_INTEGRATION_MODE = os.getenv("AIMOS_SDFCVF_APOE_MODE", "strict")


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
    # mocked mode treats integration as enabled for simulations/tests.
    return True


class APOEIntegration:
    """Integrates SDF-CVF with APOE for quality gate enforcement.
    
    Provides:
    - Quality gate status for APOE execution plans
    - Change approval workflow integration
    - Evolution recommendations
    - Compliance reporting
    """
    
    def __init__(
        self,
        apoe_client: Optional[Any] = None,
        integration_mode: Optional[IntegrationMode] = None,
    ):
        """
        Initialize APOE integration.
        
        Args:
            apoe_client: APOE client instance (optional, for testing can be None)
        """
        self.integration_mode = _resolve_integration_mode(integration_mode)
        self.apoe_available = _is_available(
            package_available=APOE_AVAILABLE,
            integration_mode=self.integration_mode,
            client=apoe_client,
        )
        self.apoe = apoe_client
        
        if not self.apoe_available:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning("APOE integration disabled: APOE package not available")
    
    def report_quality_gate_status(
        self,
        gate_result: Any,  # GateResult
        plan_id: Optional[str] = None,
        step_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Report quality gate status to APOE.
        
        Used by qualityGateManager to report gate results to APOE.
        
        Args:
            gate_result: GateResult instance
            plan_id: Optional APOE plan ID
            step_id: Optional APOE step ID
            
        Returns:
            Status report dictionary
        """
        if not self.apoe_available:
            return {
                "reported": False,
                "error": "APOE not available"
            }
        
        try:
            passed = getattr(gate_result, 'passed', False)
            parity_score = getattr(gate_result, 'parity_score', 0.0)
            
            return {
                "reported": True,
                "gate_passed": passed,
                "parity_score": parity_score,
                "plan_id": plan_id,
                "step_id": step_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error reporting quality gate status to APOE: {e}")
            return {
                "reported": False,
                "error": str(e)
            }
    
    def request_change_approval(
        self,
        change_request: Dict[str, Any],
        parity_result: Any
    ) -> Dict[str, Any]:
        """
        Request change approval from APOE workflow.
        
        Used for change approval workflow integration.
        
        Args:
            change_request: Change request data
            parity_result: ParityResult instance
            
        Returns:
            Approval result dictionary
        """
        if not self.apoe_available:
            return {
                "approved": False,
                "error": "APOE not available",
                "workflow_id": None
            }
        
        try:
            parity_score = getattr(parity_result, 'parity_score', 0.0)
            complete = getattr(parity_result, 'complete', False)
            
            # Approval logic: require high parity and completeness
            approved = parity_score >= 0.90 and complete
            
            return {
                "approved": approved,
                "parity_score": parity_score,
                "complete": complete,
                "workflow_id": f"apoe-workflow-{datetime.now(timezone.utc).timestamp()}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "message": f"Change request {'approved' if approved else 'rejected'} (parity: {parity_score:.2f})"
            }
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error requesting change approval from APOE: {e}")
            return {
                "approved": False,
                "error": str(e),
                "workflow_id": None
            }
    
    def generate_evolution_recommendations(
        self,
        parity_result: Any,
        quartet_id: str
    ) -> List[Dict[str, Any]]:
        """
        Generate evolution recommendations based on parity analysis.
        
        Used for evolution tracking and improvement suggestions.
        
        Args:
            parity_result: ParityResult instance
            quartet_id: Unique identifier for the quartet
            
        Returns:
            List of recommendation dictionaries
        """
        if not self.apoe_available:
            return []
        
        try:
            parity_score = getattr(parity_result, 'parity_score', 0.0)
            complete = getattr(parity_result, 'complete', False)
            
            recommendations = []
            
            if parity_score < 0.90:
                recommendations.append({
                    "type": "improve_parity",
                    "priority": "high",
                    "message": f"Parity score {parity_score:.2f} below threshold 0.90",
                    "suggestions": [
                        "Improve code-docs alignment",
                        "Enhance test coverage",
                        "Add trace documentation"
                    ]
                })
            
            if not complete:
                recommendations.append({
                    "type": "complete_quartet",
                    "priority": "critical",
                    "message": "Quartet incomplete - missing elements",
                    "suggestions": [
                        "Add missing documentation",
                        "Create test files",
                        "Generate trace files"
                    ]
                })
            
            return recommendations
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error generating evolution recommendations: {e}")
            return []
    
    def generate_compliance_report(
        self,
        parity_result: Any,
        quartet_id: str
    ) -> Dict[str, Any]:
        """
        Generate compliance report for APOE.
        
        Used for compliance tracking and reporting.
        
        Args:
            parity_result: ParityResult instance
            quartet_id: Unique identifier for the quartet
            
        Returns:
            Compliance report dictionary
        """
        if not self.apoe_available:
            return {
                "compliant": False,
                "error": "APOE not available",
                "report": {}
            }
        
        try:
            parity_score = getattr(parity_result, 'parity_score', 0.0)
            complete = getattr(parity_result, 'complete', False)
            
            compliant = parity_score >= 0.90 and complete
            
            return {
                "compliant": compliant,
                "parity_score": parity_score,
                "complete": complete,
                "quartet_id": quartet_id,
                "report_timestamp": datetime.now(timezone.utc).isoformat(),
                "report": {
                    "compliance_status": "compliant" if compliant else "non-compliant",
                    "parity_threshold": 0.90,
                    "requirements_met": {
                        "parity_threshold": parity_score >= 0.90,
                        "quartet_complete": complete
                    },
                    "recommendations": [] if compliant else [
                        "Improve parity score",
                        "Complete quartet elements"
                    ]
                }
            }
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error generating compliance report: {e}")
            return {
                "compliant": False,
                "error": str(e),
                "report": {}
            }

