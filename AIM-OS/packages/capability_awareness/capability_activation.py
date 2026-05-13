"""Capability Activation Component for CAF

Activates selected capabilities with optimized parameters, coordinating
capability execution and monitoring activation results.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Callable
import uuid
import time

from .models import ActivationResult, CapabilityDecision, ContextAnalysis


@dataclass
class CapabilityRegistry:
    """Registry entry for a capability"""
    capability_id: str
    capability_type: str
    activation_function: Optional[Callable] = None
    default_parameters: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True


class CapabilityActivation:
    """Activate selected capabilities with optimized parameters"""
    
    def __init__(self):
        """Initialize capability activation engine"""
        self.capability_registry: Dict[str, CapabilityRegistry] = {}
        self.activation_history: List[ActivationResult] = []
        self.active_activations: Dict[str, ActivationResult] = {}
        self._initialize_default_capabilities()
    
    def _initialize_default_capabilities(self):
        """Initialize default capability registry"""
        # Register default capabilities (placeholder functions for now)
        self.register_capability(
            capability_id="autonomous_operation",
            capability_type="autonomous_operation",
            activation_function=self._default_autonomous_activation,
            default_parameters={"enable_validation": True}
        )
        
        self.register_capability(
            capability_id="quality_assurance",
            capability_type="quality_assurance",
            activation_function=self._default_quality_activation,
            default_parameters={"check_threshold": 0.7}
        )
        
        self.register_capability(
            capability_id="status_reporting",
            capability_type="status_reporting",
            activation_function=self._default_status_activation,
            default_parameters={}
        )
        
        self.register_capability(
            capability_id="coordination_needed",
            capability_type="coordination",
            activation_function=self._default_coordination_activation,
            default_parameters={}
        )
    
    def register_capability(
        self,
        capability_id: str,
        capability_type: str,
        activation_function: Optional[Callable] = None,
        default_parameters: Optional[Dict[str, Any]] = None
    ):
        """Register a capability for activation"""
        self.capability_registry[capability_id] = CapabilityRegistry(
            capability_id=capability_id,
            capability_type=capability_type,
            activation_function=activation_function,
            default_parameters=default_parameters or {},
            enabled=True
        )
    
    def activate_capability(
        self,
        decision: CapabilityDecision,
        context: ContextAnalysis,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ActivationResult:
        """Activate selected capability with optimized parameters
        
        Args:
            decision: Capability decision to activate
            context: Context analysis result
            parameters: Optional parameters to override defaults
            
        Returns:
            ActivationResult with activation outcome
        """
        start_time = time.time()
        
        # Get capability from registry
        capability_reg = self.capability_registry.get(decision.capability)
        
        if not capability_reg:
            # Try to find by capability_type
            capability_reg = next(
                (r for r in self.capability_registry.values() 
                 if r.capability_type == decision.capability_type),
                None
            )
        
        if not capability_reg or not capability_reg.enabled:
            return ActivationResult(
                decision_id=decision.decision_id,
                capability=decision.capability,
                success=False,
                error=f"Capability '{decision.capability}' not found or disabled",
                confidence=decision.confidence
            )
        
        # Merge parameters
        merged_parameters = {**capability_reg.default_parameters}
        if decision.parameters:
            merged_parameters.update(decision.parameters)
        if parameters:
            merged_parameters.update(parameters)
        
        # Optimize parameters for context
        optimized_parameters = self._optimize_parameters(
            merged_parameters, context, decision
        )
        
        # Activate capability
        try:
            if capability_reg.activation_function:
                result = capability_reg.activation_function(
                    decision=decision,
                    context=context,
                    parameters=optimized_parameters
                )
            else:
                # Default activation
                result = {"status": "activated", "message": f"Capability {decision.capability} activated"}
            
            activation_time_ms = (time.time() - start_time) * 1000
            
            # Create activation result
            activation_result = ActivationResult(
                decision_id=decision.decision_id,
                capability=decision.capability,
                parameters=optimized_parameters,
                success=True,
                result=result,
                activation_time_ms=activation_time_ms,
                confidence=decision.confidence,
                effectiveness_score=self._calculate_effectiveness(decision, result),
                metadata={"capability_type": capability_reg.capability_type}
            )
            
        except Exception as e:
            activation_time_ms = (time.time() - start_time) * 1000
            activation_result = ActivationResult(
                decision_id=decision.decision_id,
                capability=decision.capability,
                parameters=optimized_parameters,
                success=False,
                error=str(e),
                activation_time_ms=activation_time_ms,
                confidence=decision.confidence
            )
        
        # Store in history
        self.activation_history.append(activation_result)
        
        # Track active activation
        self.active_activations[activation_result.activation_id] = activation_result
        
        return activation_result
    
    def _optimize_parameters(
        self,
        parameters: Dict[str, Any],
        context: ContextAnalysis,
        decision: CapabilityDecision
    ) -> Dict[str, Any]:
        """Optimize parameters for context"""
        optimized = parameters.copy()
        
        # Adjust based on confidence
        if decision.confidence < 0.7:
            # Lower confidence → add validation
            optimized["enable_validation"] = True
            optimized["require_confirmation"] = True
        
        # Adjust based on system state
        quality = context.system_state.get("quality", "unknown")
        if quality == "degrading":
            optimized["enable_quality_checks"] = True
        
        # Adjust based on context hints
        if context.capability_hints:
            optimized["context_hints"] = context.capability_hints
        
        return optimized
    
    def _calculate_effectiveness(
        self,
        decision: CapabilityDecision,
        result: Any
    ) -> float:
        """Calculate effectiveness score for activation"""
        # Base effectiveness from decision confidence
        effectiveness = decision.confidence
        
        # Adjust based on result
        if isinstance(result, dict):
            if result.get("status") == "activated":
                effectiveness += 0.1
            if result.get("success"):
                effectiveness += 0.1
        
        return min(1.0, effectiveness)
    
    def monitor_activation(self, activation_id: str) -> Optional[ActivationResult]:
        """Monitor ongoing activation
        
        Args:
            activation_id: Activation ID to monitor
            
        Returns:
            Current activation result, or None if not found
        """
        return self.active_activations.get(activation_id)
    
    def handle_failure(
        self,
        activation_result: ActivationResult,
        context: ContextAnalysis
    ) -> Optional[ActivationResult]:
        """Handle activation failure gracefully
        
        Args:
            activation_result: Failed activation result
            context: Context analysis
            
        Returns:
            Alternative activation result if available, None otherwise
        """
        # Try alternative capabilities
        decision = next(
            (d for d in self.activation_history 
             if d.decision_id == activation_result.decision_id),
            None
        )
        
        if not decision:
            return None
        
        # Try alternatives from decision
        for alt_capability in decision.alternatives[:3]:  # Try up to 3 alternatives
            alt_reg = self.capability_registry.get(alt_capability)
            if alt_reg and alt_reg.enabled:
                # Create alternative decision
                alt_decision = CapabilityDecision(
                    capability=alt_capability,
                    capability_type=alt_reg.capability_type,
                    confidence=decision.confidence * 0.8,  # Slightly lower confidence
                    reasoning=f"Alternative to failed {decision.capability}",
                    context=decision.context
                )
                
                # Try alternative activation
                alt_result = self.activate_capability(alt_decision, context)
                if alt_result.success:
                    return alt_result
        
        return None
    
    def coordinate_activations(
        self,
        decisions: List[CapabilityDecision],
        context: ContextAnalysis
    ) -> List[ActivationResult]:
        """Coordinate multiple capability activations
        
        Args:
            decisions: List of capability decisions
            context: Context analysis
            
        Returns:
            List of activation results
        """
        results = []
        
        # Sort by priority (higher confidence first)
        sorted_decisions = sorted(
            decisions,
            key=lambda d: d.confidence,
            reverse=True
        )
        
        # Activate in order
        for decision in sorted_decisions:
            result = self.activate_capability(decision, context)
            results.append(result)
            
            # Stop if critical failure
            if not result.success and decision.confidence >= 0.9:
                break
        
        return results
    
    # Default activation functions
    def _default_autonomous_activation(
        self,
        decision: CapabilityDecision,
        context: ContextAnalysis,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Default autonomous operation activation"""
        return {
            "status": "activated",
            "message": "Autonomous operation enabled",
            "parameters": parameters
        }
    
    def _default_quality_activation(
        self,
        decision: CapabilityDecision,
        context: ContextAnalysis,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Default quality assurance activation"""
        return {
            "status": "activated",
            "message": "Quality assurance checks enabled",
            "parameters": parameters
        }
    
    def _default_status_activation(
        self,
        decision: CapabilityDecision,
        context: ContextAnalysis,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Default status reporting activation"""
        return {
            "status": "activated",
            "message": "Status reporting enabled",
            "parameters": parameters
        }
    
    def _default_coordination_activation(
        self,
        decision: CapabilityDecision,
        context: ContextAnalysis,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Default coordination activation"""
        return {
            "status": "activated",
            "message": "Coordination enabled",
            "parameters": parameters
        }
    
    def query_activation_history(
        self,
        capability_id: Optional[str] = None,
        min_confidence: float = 0.0,
        success_only: bool = False
    ) -> List[ActivationResult]:
        """Query activation history"""
        results = self.activation_history
        
        # Filter by capability
        if capability_id:
            results = [r for r in results if r.capability == capability_id]
        
        # Filter by confidence
        results = [r for r in results if r.confidence >= min_confidence]
        
        # Filter by success
        if success_only:
            results = [r for r in results if r.success]
        
        return results

