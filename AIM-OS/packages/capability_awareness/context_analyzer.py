"""Context Analyzer Component for CAF

Analyzes current context for capability needs, understanding situation,
user intent, system state, and temporal context to extract capability hints.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid

from .models import ContextAnalysis


class ContextAnalyzer:
    """Analyze context for capability needs"""
    
    def __init__(self):
        """Initialize context analyzer"""
        self.analysis_history: List[ContextAnalysis] = []
    
    def analyze_context(self, context_input: Dict[str, Any]) -> ContextAnalysis:
        """Analyze current context for capability needs
        
        Args:
            context_input: Dictionary containing:
                - user_input: User's input text
                - current_task: Current task being worked on
                - agent_state: Current agent state
                - recent_activities: List of recent activities
                - system_state: Dictionary of system state metrics
                
        Returns:
            ContextAnalysis with capability hints and confidence
        """
        # Extract components
        user_input = context_input.get("user_input", "")
        current_task = context_input.get("current_task", "")
        agent_state = context_input.get("agent_state", "")
        recent_activities = context_input.get("recent_activities", [])
        system_state = context_input.get("system_state", {})
        
        # Analyze situation
        situation = self._analyze_situation(user_input, current_task, agent_state)
        
        # Analyze user intent
        user_intent = self._analyze_user_intent(user_input, context_input)
        
        # Analyze system state
        system_state_analysis = self._analyze_system_state(system_state)
        
        # Analyze temporal context
        temporal_context = self._analyze_temporal_context(recent_activities)
        
        # Extract capability hints
        capability_hints = self._extract_capability_hints(
            situation, user_intent, system_state_analysis, temporal_context
        )
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            situation, user_intent, capability_hints
        )
        
        # Create analysis result
        analysis = ContextAnalysis(
            situation=situation,
            user_intent=user_intent,
            system_state=system_state_analysis,
            temporal_context=temporal_context,
            capability_hints=capability_hints,
            confidence=confidence
        )
        
        # Store in history
        self.analysis_history.append(analysis)
        
        return analysis
    
    def _analyze_situation(
        self, 
        user_input: str, 
        current_task: str, 
        agent_state: str
    ) -> str:
        """Analyze current situation and context"""
        # Simple keyword-based situation analysis
        situation_parts = []
        
        if current_task:
            situation_parts.append(f"Working on: {current_task}")
        
        if agent_state:
            situation_parts.append(f"Agent state: {agent_state}")
        
        if user_input:
            # Extract action verbs
            action_words = ["proceed", "start", "begin", "complete", "check", "update"]
            detected_actions = [w for w in action_words if w in user_input.lower()]
            if detected_actions:
                situation_parts.append(f"User action: {', '.join(detected_actions)}")
        
        return " | ".join(situation_parts) if situation_parts else "No specific situation detected"
    
    def _analyze_user_intent(
        self, 
        user_input: str, 
        context_input: Dict[str, Any]
    ) -> str:
        """Determine user intent and goals"""
        user_input_lower = user_input.lower()
        
        # Pattern matching for common intents
        if any(word in user_input_lower for word in ["proceed", "continue", "go ahead"]):
            return "Continue current work autonomously"
        elif any(word in user_input_lower for word in ["check", "status", "update"]):
            return "Check status or get update"
        elif any(word in user_input_lower for word in ["start", "begin", "implement"]):
            return "Start new task or implementation"
        elif any(word in user_input_lower for word in ["complete", "finish", "done"]):
            return "Complete current task"
        else:
            return "General interaction"
    
    def _analyze_system_state(self, system_state: Dict[str, Any]) -> Dict[str, Any]:
        """Assess current system state"""
        # Extract key metrics
        return {
            "quality": system_state.get("quality", "unknown"),
            "alignment": system_state.get("alignment", "unknown"),
            "progress": system_state.get("progress", 0.0),
            "blockers": system_state.get("blockers", []),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def _analyze_temporal_context(self, recent_activities: List[str]) -> Dict[str, Any]:
        """Consider temporal aspects"""
        return {
            "recent_activities": recent_activities[-5:],  # Last 5 activities
            "activity_count": len(recent_activities),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def _extract_capability_hints(
        self,
        situation: str,
        user_intent: str,
        system_state: Dict[str, Any],
        temporal_context: Dict[str, Any]
    ) -> List[str]:
        """Extract hints about needed capabilities"""
        hints = []
        
        # Capability hints based on user intent
        user_intent_lower = user_intent.lower()
        if "autonomous" in user_intent_lower or "proceed" in user_intent_lower:
            hints.append("autonomous_operation")
            hints.append("decision_making")
        
        if "check" in user_intent_lower or "status" in user_intent_lower:
            hints.append("status_reporting")
            hints.append("coordination")
        
        if "implement" in user_intent_lower or "start" in user_intent_lower:
            hints.append("task_execution")
            hints.append("planning")
        
        # Capability hints based on system state
        quality = system_state.get("quality", "unknown")
        if quality == "degrading":
            hints.append("quality_assurance")
            hints.append("cognitive_introspection")
        
        if system_state.get("blockers"):
            hints.append("problem_solving")
            hints.append("coordination")
        
        # Capability hints based on recent activities
        recent = temporal_context.get("recent_activities", [])
        if len(recent) > 3:
            hints.append("pattern_recognition")
        
        return list(set(hints))  # Remove duplicates
    
    def _calculate_confidence(
        self,
        situation: str,
        user_intent: str,
        capability_hints: List[str]
    ) -> float:
        """Calculate confidence in context analysis"""
        # Base confidence
        confidence = 0.5
        
        # Increase confidence if we have clear signals
        if situation and situation != "No specific situation detected":
            confidence += 0.1
        
        if user_intent and user_intent != "General interaction":
            confidence += 0.2
        
        if capability_hints:
            confidence += min(0.2, len(capability_hints) * 0.05)
        
        return min(1.0, confidence)
    
    def query_context_history(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        min_confidence: float = 0.0
    ) -> List[ContextAnalysis]:
        """Query context analysis history"""
        results = self.analysis_history
        
        # Filter by time range
        if start_time:
            results = [a for a in results if a.timestamp >= start_time]
        if end_time:
            results = [a for a in results if a.timestamp <= end_time]
        
        # Filter by confidence
        results = [a for a in results if a.confidence >= min_confidence]
        
        return results

