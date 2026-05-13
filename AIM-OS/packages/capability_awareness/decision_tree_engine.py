"""Decision Tree Engine Component for CAF

Navigates decision trees to select capabilities, using hierarchical decision
trees with branching logic for consistent and reliable capability activation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid

from .models import CapabilityDecision, TriggerSignal, ContextAnalysis


@dataclass
class DecisionNode:
    """A node in the decision tree"""
    node_id: str
    condition: str  # Condition to evaluate
    capability: Optional[str] = None  # Capability if this is a leaf node
    children: List[DecisionNode] = field(default_factory=list)
    reasoning: str = ""


class DecisionTreeEngine:
    """Navigate decision trees to select capabilities"""
    
    def __init__(self):
        """Initialize decision tree engine"""
        self.decision_trees: Dict[str, DecisionNode] = {}
        self.decision_history: List[CapabilityDecision] = []
        self._initialize_default_trees()
    
    def _initialize_default_trees(self):
        """Initialize default decision trees"""
        # Decision tree for autonomous operation
        autonomous_tree = DecisionNode(
            node_id="root_autonomous",
            condition="has_autonomous_trigger",
            children=[
                DecisionNode(
                    node_id="high_confidence",
                    condition="confidence >= 0.8",
                    capability="autonomous_operation",
                    reasoning="High confidence trigger, proceed autonomously"
                ),
                DecisionNode(
                    node_id="medium_confidence",
                    condition="confidence >= 0.6",
                    capability="autonomous_operation_with_validation",
                    reasoning="Medium confidence trigger, proceed with validation"
                ),
                DecisionNode(
                    node_id="low_confidence",
                    condition="confidence < 0.6",
                    capability="coordination_needed",
                    reasoning="Low confidence trigger, coordinate before proceeding"
                )
            ]
        )
        self.decision_trees["autonomous_operation"] = autonomous_tree
        
        # Decision tree for quality assurance
        quality_tree = DecisionNode(
            node_id="root_quality",
            condition="has_quality_trigger",
            children=[
                DecisionNode(
                    node_id="quality_degrading",
                    condition="system_state.quality == 'degrading'",
                    capability="quality_assurance",
                    reasoning="Quality degrading, activate quality assurance"
                ),
                DecisionNode(
                    node_id="quality_good",
                    condition="system_state.quality == 'good'",
                    capability="quality_monitoring",
                    reasoning="Quality good, continue monitoring"
                )
            ]
        )
        self.decision_trees["quality_assurance"] = quality_tree
    
    def navigate_decision_tree(
        self,
        triggers: List[TriggerSignal],
        context: ContextAnalysis
    ) -> Optional[CapabilityDecision]:
        """Navigate decision tree to select capabilities
        
        Args:
            triggers: List of detected trigger signals
            context: Context analysis result
            
        Returns:
            CapabilityDecision with selected capability, or None if no decision
        """
        if not triggers:
            return None
        
        # Select primary trigger (highest priority, highest confidence)
        primary_trigger = triggers[0]
        
        # Determine which decision tree to use
        tree_name = self._select_tree(primary_trigger, context)
        
        if tree_name not in self.decision_trees:
            # Fallback: use capability type from trigger
            return self._create_simple_decision(primary_trigger, context)
        
        # Navigate the decision tree
        tree = self.decision_trees[tree_name]
        selected_capability = self._evaluate_tree(tree, triggers, context)
        
        if not selected_capability:
            return None
        
        # Create decision
        decision = CapabilityDecision(
            capability=selected_capability["capability"],
            capability_type=primary_trigger.capability_type,
            confidence=primary_trigger.confidence,
            reasoning=selected_capability["reasoning"],
            alternatives=self._get_alternatives(triggers),
            context={"tree_name": tree_name, "trigger_count": len(triggers)},
            trigger_signals=triggers,
            parameters=selected_capability.get("parameters", {})
        )
        
        # Store in history
        self.decision_history.append(decision)
        
        return decision
    
    def _select_tree(self, trigger: TriggerSignal, context: ContextAnalysis) -> str:
        """Select which decision tree to use"""
        # Map capability type to tree name
        capability_type = trigger.capability_type
        
        if "autonomous" in capability_type:
            return "autonomous_operation"
        elif "quality" in capability_type:
            return "quality_assurance"
        else:
            # Default tree name based on capability type
            return capability_type.replace("_", "_")
    
    def _evaluate_tree(
        self,
        node: DecisionNode,
        triggers: List[TriggerSignal],
        context: ContextAnalysis
    ) -> Optional[Dict[str, Any]]:
        """Recursively evaluate decision tree"""
        # If this is a leaf node (has capability), return it
        if node.capability:
            return {
                "capability": node.capability,
                "reasoning": node.reasoning
            }
        
        # Evaluate condition
        if not self._evaluate_condition(node.condition, triggers, context):
            return None
        
        # Evaluate children
        for child in node.children:
            result = self._evaluate_tree(child, triggers, context)
            if result:
                return result
        
        return None
    
    def _evaluate_condition(
        self,
        condition: str,
        triggers: List[TriggerSignal],
        context: ContextAnalysis
    ) -> bool:
        """Evaluate a condition in the decision tree"""
        # Simple condition evaluation
        if condition == "has_autonomous_trigger":
            return any("autonomous" in t.capability_type for t in triggers)
        
        if condition == "has_quality_trigger":
            return any("quality" in t.capability_type for t in triggers)
        
        if condition.startswith("confidence"):
            # Parse confidence condition
            if ">=" in condition:
                threshold = float(condition.split(">=")[1].strip())
                return triggers[0].confidence >= threshold if triggers else False
            elif "<" in condition:
                threshold = float(condition.split("<")[1].strip())
                return triggers[0].confidence < threshold if triggers else False
        
        if condition.startswith("system_state"):
            # Parse system state condition
            parts = condition.split("==")
            if len(parts) == 2:
                key = parts[0].strip().replace("system_state.", "")
                value = parts[1].strip().strip("'\"")
                return context.system_state.get(key) == value
        
        return False
    
    def _create_simple_decision(
        self,
        trigger: TriggerSignal,
        context: ContextAnalysis
    ) -> CapabilityDecision:
        """Create a simple decision without decision tree"""
        decision = CapabilityDecision(
            capability=trigger.capability_type,
            capability_type=trigger.capability_type,
            confidence=trigger.confidence,
            reasoning=f"Direct capability selection from trigger: {trigger.reasoning}",
            alternatives=[],
            context={"method": "simple"},
            trigger_signals=[trigger]
        )
        
        self.decision_history.append(decision)
        return decision
    
    def _get_alternatives(self, triggers: List[TriggerSignal]) -> List[str]:
        """Get alternative capabilities from other triggers"""
        if len(triggers) <= 1:
            return []
        
        # Return capability types from other triggers
        return [t.capability_type for t in triggers[1:5]]  # Max 4 alternatives
    
    def get_decision_path(self, decision_id: str) -> List[str]:
        """Get decision tree path for a decision"""
        decision = next(
            (d for d in self.decision_history if d.decision_id == decision_id),
            None
        )
        
        if not decision:
            return []
        
        # Build path from decision context
        path = []
        if "tree_name" in decision.context:
            path.append(f"Tree: {decision.context['tree_name']}")
        path.append(f"Capability: {decision.capability}")
        path.append(f"Confidence: {decision.confidence:.2f}")
        
        return path
    
    def query_decision_history(
        self,
        capability_type: Optional[str] = None,
        min_confidence: float = 0.0,
        start_time: Optional[datetime] = None
    ) -> List[CapabilityDecision]:
        """Query decision history"""
        results = self.decision_history
        
        # Filter by capability type
        if capability_type:
            results = [d for d in results if d.capability_type == capability_type]
        
        # Filter by confidence
        results = [d for d in results if d.confidence >= min_confidence]
        
        # Filter by time
        if start_time:
            results = [d for d in results if d.timestamp >= start_time]
        
        return results

