"""
SCOR Main Interface

Main entry point for SCOR validation.
"""

from typing import Dict, Any, Optional

from .config import SCORConfig
from .storage import InvariantStorage, BaselineStorage
from .invariants import InvariantChecker
from .probes import BaselineProbes
from .social_signals import SocialSignalDetector
from .redcell import RedCell
from .gate import SCORGate
from .models import ValidationResult


class SCORInterface:
    """Main interface for SCOR validation"""
    
    def __init__(self, config: SCORConfig = None):
        """Initialize SCOR with configuration"""
        self.config = config or SCORConfig()
        self.config.validate()
        
        # Initialize storage
        self.invariant_storage = InvariantStorage(self.config)
        self.baseline_storage = BaselineStorage(self.config)
        
        # Initialize components
        self.invariant_checker = InvariantChecker(self.config, self.invariant_storage)
        self.baseline_probes = BaselineProbes(self.config, self.baseline_storage)
        self.social_detector = SocialSignalDetector(self.config)
        self.red_cell = RedCell(self.config)
        self.gate = SCORGate(self.config)
    
    def validate_action(
        self,
        action: Dict[str, Any],
        context: Dict[str, Any],
        user_input: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> ValidationResult:
        """
        Validate an action against all SCOR checks.
        
        Args:
            action: Action to validate
            context: Runtime context (CAS, RID, TCS data)
            user_input: User input that triggered action (for signal detection)
            request_id: Unique identifier for tracking
            
        Returns:
            ValidationResult with pass/fail decision
        """
        
        # Run invariant checks
        invariant_result = self.invariant_checker.check_invariants(action, context)
        
        # Run baseline probes (if context available)
        drift_result = self.baseline_probes.run_probe_cycle(context)
        
        # Detect social signals (if user input provided)
        if user_input:
            signal_result = self.social_detector.detect_signals(user_input, context)
        else:
            # Create empty signal result if no user input
            from .models import SignalResult
            signal_result = SignalResult(
                total=0.0,
                breakdown={},
                detected_patterns=[],
                recommended_action="proceed"
            )
        
        # Run red cell simulation (optional, expensive)
        red_cell_result = self.red_cell.run_simulation(context)
        
        # Make final decision
        final_result = self.gate.decide(
            invariant_result,
            drift_result,
            signal_result,
            red_cell_result
        )
        
        # Add request ID to metadata
        if request_id:
            final_result.metadata["request_id"] = request_id
        
        return final_result
