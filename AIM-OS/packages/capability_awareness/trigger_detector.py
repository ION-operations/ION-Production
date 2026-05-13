"""Trigger Detector Component for CAF

Detects trigger signals for capability activation, identifying explicit,
implicit, pattern, and context triggers that indicate capability needs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid

from .models import TriggerSignal, TriggerType, ContextAnalysis


@dataclass
class TriggerPattern:
    """Pattern definition for trigger detection"""
    pattern_id: str
    pattern_type: TriggerType
    capability_type: str
    conditions: Dict[str, Any]
    confidence: float
    priority: float
    reasoning_template: str = ""


class TriggerDetector:
    """Detect trigger signals for capability activation"""
    
    def __init__(self):
        """Initialize trigger detector"""
        self.trigger_patterns: List[TriggerPattern] = []
        self.trigger_history: List[TriggerSignal] = []
        self._initialize_default_patterns()
    
    def _initialize_default_patterns(self):
        """Initialize default trigger patterns"""
        # Explicit trigger patterns
        self.trigger_patterns.append(TriggerPattern(
            pattern_id="proceed_explicit",
            pattern_type=TriggerType.EXPLICIT,
            capability_type="autonomous_operation",
            conditions={"user_input": ["proceed", "continue", "go ahead"]},
            confidence=0.9,
            priority=1.0,
            reasoning_template="User explicitly requested to proceed"
        ))
        
        self.trigger_patterns.append(TriggerPattern(
            pattern_id="check_status_explicit",
            pattern_type=TriggerType.EXPLICIT,
            capability_type="status_reporting",
            conditions={"user_input": ["check", "status", "update"]},
            confidence=0.85,
            priority=1.0,
            reasoning_template="User explicitly requested status check"
        ))
        
        # Implicit trigger patterns
        self.trigger_patterns.append(TriggerPattern(
            pattern_id="quality_degrading_implicit",
            pattern_type=TriggerType.IMPLICIT,
            capability_type="quality_assurance",
            conditions={"system_state.quality": "degrading"},
            confidence=0.75,
            priority=2.0,
            reasoning_template="System quality is degrading, quality assurance needed"
        ))
        
        self.trigger_patterns.append(TriggerPattern(
            pattern_id="blockers_detected_implicit",
            pattern_type=TriggerType.IMPLICIT,
            capability_type="problem_solving",
            conditions={"system_state.blockers": "non_empty"},
            confidence=0.8,
            priority=2.0,
            reasoning_template="Blockers detected, problem-solving capability needed"
        ))
        
        # Pattern trigger patterns
        self.trigger_patterns.append(TriggerPattern(
            pattern_id="frequent_activities_pattern",
            pattern_type=TriggerType.PATTERN,
            capability_type="pattern_recognition",
            conditions={"temporal_context.activity_count": "> 3"},
            confidence=0.7,
            priority=3.0,
            reasoning_template="Frequent activities detected, pattern recognition needed"
        ))
        
        # Context trigger patterns
        self.trigger_patterns.append(TriggerPattern(
            pattern_id="autonomous_work_context",
            pattern_type=TriggerType.CONTEXT,
            capability_type="autonomous_operation",
            conditions={"agent_state": "working_autonomously"},
            confidence=0.65,
            priority=2.0,
            reasoning_template="Agent working autonomously, autonomous operation capability active"
        ))
    
    def detect_triggers(self, context_analysis: ContextAnalysis) -> List[TriggerSignal]:
        """Detect trigger signals for capability activation
        
        Args:
            context_analysis: Context analysis result
            
        Returns:
            List of detected trigger signals, sorted by priority and confidence
        """
        triggers = []
        
        # Detect explicit triggers
        explicit_triggers = self._detect_explicit_triggers(context_analysis)
        triggers.extend(explicit_triggers)
        
        # Detect implicit triggers
        implicit_triggers = self._detect_implicit_triggers(context_analysis)
        triggers.extend(implicit_triggers)
        
        # Detect pattern triggers
        pattern_triggers = self._detect_pattern_triggers(context_analysis)
        triggers.extend(pattern_triggers)
        
        # Detect context triggers
        context_triggers = self._detect_context_triggers(context_analysis)
        triggers.extend(context_triggers)
        
        # Prioritize triggers
        prioritized_triggers = self._prioritize_triggers(triggers)
        
        # Store in history
        self.trigger_history.extend(prioritized_triggers)
        
        return prioritized_triggers
    
    def _detect_explicit_triggers(self, context_analysis: ContextAnalysis) -> List[TriggerSignal]:
        """Detect explicit triggers (direct signals)"""
        triggers = []
        
        # Get user input from context (if available)
        user_intent = context_analysis.user_intent.lower()
        
        for pattern in self.trigger_patterns:
            if pattern.pattern_type != TriggerType.EXPLICIT:
                continue
            
            # Check if pattern matches
            if self._pattern_matches(pattern, context_analysis):
                trigger = TriggerSignal(
                    trigger_type=TriggerType.EXPLICIT,
                    capability_type=pattern.capability_type,
                    pattern_id=pattern.pattern_id,
                    confidence=pattern.confidence,
                    priority=pattern.priority,
                    reasoning=pattern.reasoning_template,
                    context={"user_intent": user_intent}
                )
                triggers.append(trigger)
        
        return triggers
    
    def _detect_implicit_triggers(self, context_analysis: ContextAnalysis) -> List[TriggerSignal]:
        """Detect implicit triggers (subtle signals)"""
        triggers = []
        
        system_state = context_analysis.system_state
        
        for pattern in self.trigger_patterns:
            if pattern.pattern_type != TriggerType.IMPLICIT:
                continue
            
            # Check if pattern matches
            if self._pattern_matches(pattern, context_analysis):
                trigger = TriggerSignal(
                    trigger_type=TriggerType.IMPLICIT,
                    capability_type=pattern.capability_type,
                    pattern_id=pattern.pattern_id,
                    confidence=pattern.confidence,
                    priority=pattern.priority,
                    reasoning=pattern.reasoning_template,
                    context={"system_state": system_state}
                )
                triggers.append(trigger)
        
        return triggers
    
    def _detect_pattern_triggers(self, context_analysis: ContextAnalysis) -> List[TriggerSignal]:
        """Detect pattern triggers (recurring patterns)"""
        triggers = []
        
        temporal_context = context_analysis.temporal_context
        
        for pattern in self.trigger_patterns:
            if pattern.pattern_type != TriggerType.PATTERN:
                continue
            
            # Check if pattern matches
            if self._pattern_matches(pattern, context_analysis):
                trigger = TriggerSignal(
                    trigger_type=TriggerType.PATTERN,
                    capability_type=pattern.capability_type,
                    pattern_id=pattern.pattern_id,
                    confidence=pattern.confidence,
                    priority=pattern.priority,
                    reasoning=pattern.reasoning_template,
                    context={"temporal_context": temporal_context}
                )
                triggers.append(trigger)
        
        return triggers
    
    def _detect_context_triggers(self, context_analysis: ContextAnalysis) -> List[TriggerSignal]:
        """Detect context triggers (contextual signals)"""
        triggers = []
        
        situation = context_analysis.situation
        
        for pattern in self.trigger_patterns:
            if pattern.pattern_type != TriggerType.CONTEXT:
                continue
            
            # Check if pattern matches
            if self._pattern_matches(pattern, context_analysis):
                trigger = TriggerSignal(
                    trigger_type=TriggerType.CONTEXT,
                    capability_type=pattern.capability_type,
                    pattern_id=pattern.pattern_id,
                    confidence=pattern.confidence,
                    priority=pattern.priority,
                    reasoning=pattern.reasoning_template,
                    context={"situation": situation}
                )
                triggers.append(trigger)
        
        return triggers
    
    def _pattern_matches(self, pattern: TriggerPattern, context_analysis: ContextAnalysis) -> bool:
        """Check if a pattern matches the context analysis"""
        conditions = pattern.conditions
        
        # Check user_input conditions
        if "user_input" in conditions:
            user_intent = context_analysis.user_intent.lower()
            required_words = conditions["user_input"]
            if not any(word in user_intent for word in required_words):
                return False
        
        # Check system_state conditions
        if "system_state.quality" in conditions:
            quality = context_analysis.system_state.get("quality", "unknown")
            if quality != conditions["system_state.quality"]:
                return False
        
        if "system_state.blockers" in conditions:
            blockers = context_analysis.system_state.get("blockers", [])
            if conditions["system_state.blockers"] == "non_empty" and not blockers:
                return False
        
        # Check temporal_context conditions
        if "temporal_context.activity_count" in conditions:
            activity_count = len(context_analysis.temporal_context.get("recent_activities", []))
            condition = conditions["temporal_context.activity_count"]
            if condition.startswith(">") and activity_count <= int(condition[1:].strip()):
                return False
        
        # Check agent_state conditions
        if "agent_state" in conditions:
            # Would need agent_state in context_analysis - simplified for now
            pass
        
        return True
    
    def _prioritize_triggers(self, triggers: List[TriggerSignal]) -> List[TriggerSignal]:
        """Prioritize triggers by confidence and priority"""
        # Sort by priority (lower is higher priority), then by confidence (higher is better)
        return sorted(
            triggers,
            key=lambda t: (t.priority, -t.confidence)
        )
    
    def register_trigger_pattern(self, pattern: TriggerPattern):
        """Register a new trigger pattern"""
        self.trigger_patterns.append(pattern)
    
    def query_trigger_history(
        self,
        capability_type: Optional[str] = None,
        trigger_type: Optional[TriggerType] = None,
        min_confidence: float = 0.0
    ) -> List[TriggerSignal]:
        """Query trigger history"""
        results = self.trigger_history
        
        # Filter by capability type
        if capability_type:
            results = [t for t in results if t.capability_type == capability_type]
        
        # Filter by trigger type
        if trigger_type:
            results = [t for t in results if t.trigger_type == trigger_type]
        
        # Filter by confidence
        results = [t for t in results if t.confidence >= min_confidence]
        
        return results

