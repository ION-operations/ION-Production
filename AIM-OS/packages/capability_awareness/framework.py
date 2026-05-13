"""CAF Main Framework

Combines all components into a unified Capability Awareness Framework.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime

from .context_analyzer import ContextAnalyzer, ContextAnalysis
from .trigger_detector import TriggerDetector, TriggerSignal
from .decision_tree_engine import DecisionTreeEngine, CapabilityDecision
from .capability_activation import CapabilityActivation, ActivationResult
from .performance_tracker import PerformanceTracker, PerformanceMetrics
from .capability_manager import CapabilityManager, CapabilityMetadata

# Import integrations
from .integrations.cmc_integration import CMCIntegration
from .integrations.vif_integration import VIFIntegration
from .integrations.cas_integration import CASIntegration
from .integrations.apoe_integration import APOEIntegration


class CapabilityAwarenessFramework:
    """Main framework for organic capability recognition"""
    
    def __init__(
        self,
        memory_store=None,
        vif_service=None,
        enable_learning: bool = True
    ):
        """Initialize CAF
        
        Args:
            memory_store: Optional CMC memory store for persistence
            vif_service: Optional VIF service for confidence tracking
            enable_learning: Enable learning from performance
        """
        self.memory_store = memory_store
        self.vif_service = vif_service
        self.enable_learning = enable_learning
        
        # Initialize components
        self.context_analyzer = ContextAnalyzer()
        self.trigger_detector = TriggerDetector()
        self.decision_tree_engine = DecisionTreeEngine()
        self.capability_activation = CapabilityActivation()
        self.performance_tracker = PerformanceTracker()
        self.capability_manager = CapabilityManager()
        
        # Initialize integrations
        self.cmc_integration = CMCIntegration(memory_store)
        self.vif_integration = VIFIntegration(vif_service)
        self.cas_integration = CASIntegration()
        self.apoe_integration = APOEIntegration()
        
        # Register capabilities from manager to activation
        self._register_capabilities()
    
    def _register_capabilities(self):
        """Register capabilities from manager to activation engine"""
        for capability_id, metadata in self.capability_manager.capabilities.items():
            self.capability_activation.register_capability(
                capability_id=capability_id,
                capability_type=metadata.capability_type,
                default_parameters=metadata.performance_characteristics
            )
    
    def recognize_and_activate(
        self,
        context_input: Dict[str, Any]
    ) -> ActivationResult:
        """Complete capability recognition and activation flow
        
        Args:
            context_input: Context input dictionary
            
        Returns:
            ActivationResult with activation outcome
        """
        # Step 1: Analyze context
        context_analysis = self.context_analyzer.analyze_context(context_input)
        
        # Step 2: Detect triggers
        triggers = self.trigger_detector.detect_triggers(context_analysis)
        
        if not triggers:
            return ActivationResult(
                success=False,
                error="No triggers detected",
                capability="none"
            )
        
        # Step 3: Navigate decision tree
        decision = self.decision_tree_engine.navigate_decision_tree(
            triggers=triggers,
            context=context_analysis
        )
        
        if not decision:
            return ActivationResult(
                success=False,
                error="No capability selected",
                capability="none"
            )
        
        # Step 4: Activate capability
        activation_result = self.capability_activation.activate_capability(
            decision=decision,
            context=context_analysis
        )
        
        # Step 5: Track performance
        if activation_result.success and self.enable_learning:
            performance_metrics = self.performance_tracker.track_performance(
                activation_result=activation_result,
                outcome={"success": True}
            )
            
            # Store in CMC if available
            if self.cmc_integration.enabled:
                self.cmc_integration.store_performance_metrics(performance_metrics)
            
            # Update learning models
            if self.enable_learning:
                self.performance_tracker.update_learning_models(
                    activation_id=activation_result.activation_id,
                    performance_metrics=performance_metrics
                )
        
        # Store context analysis and decision in CMC if available
        if self.cmc_integration.enabled:
            self.cmc_integration.store_context_analysis(context_analysis)
            if decision:
                self.cmc_integration.store_capability_decision(decision)
        
        return activation_result
    
    def configure_trigger_detection(
        self,
        enable_explicit: bool = True,
        enable_implicit: bool = True,
        enable_pattern: bool = True,
        enable_context: bool = True
    ):
        """Configure trigger detection
        
        Args:
            enable_explicit: Enable explicit trigger detection
            enable_implicit: Enable implicit trigger detection
            enable_pattern: Enable pattern trigger detection
            enable_context: Enable context trigger detection
        """
        # Store configuration (can be used to filter triggers)
        self.trigger_config = {
            "explicit": enable_explicit,
            "implicit": enable_implicit,
            "pattern": enable_pattern,
            "context": enable_context
        }
    
    def configure_decision_trees(
        self,
        enable_caching: bool = True,
        enable_learning: bool = True,
        confidence_threshold: float = 0.6
    ):
        """Configure decision trees
        
        Args:
            enable_caching: Enable decision caching
            enable_learning: Enable learning from decisions
            confidence_threshold: Minimum confidence threshold
        """
        self.decision_config = {
            "enable_caching": enable_caching,
            "enable_learning": enable_learning,
            "confidence_threshold": confidence_threshold
        }
    
    def configure_performance_tracking(
        self,
        track_activation_time: bool = True,
        track_effectiveness: bool = True,
        track_efficiency: bool = True,
        update_learning: bool = True
    ):
        """Configure performance tracking
        
        Args:
            track_activation_time: Track activation time
            track_effectiveness: Track effectiveness
            track_efficiency: Track efficiency
            update_learning: Update learning models
        """
        self.performance_config = {
            "track_activation_time": track_activation_time,
            "track_effectiveness": track_effectiveness,
            "track_efficiency": track_efficiency,
            "update_learning": update_learning
        }
        self.enable_learning = update_learning
    
    # Delegate methods to components
    def register_capability(self, metadata: CapabilityMetadata):
        """Register a capability"""
        self.capability_manager.register_capability(metadata)
        self.capability_activation.register_capability(
            capability_id=metadata.capability_id,
            capability_type=metadata.capability_type,
            default_parameters=metadata.performance_characteristics
        )
    
    def list_capabilities(self, capability_type: Optional[str] = None) -> List[CapabilityMetadata]:
        """List all capabilities"""
        return self.capability_manager.list_capabilities(capability_type=capability_type)
    
    def search_capabilities(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[CapabilityMetadata]:
        """Search capabilities"""
        return self.capability_manager.search_capabilities(query, filters)
    
    def get_performance_insights(self, capability_id: str, time_range_days: int = 30) -> Dict[str, Any]:
        """Get performance insights"""
        return self.performance_tracker.get_performance_insights(capability_id, time_range_days)

