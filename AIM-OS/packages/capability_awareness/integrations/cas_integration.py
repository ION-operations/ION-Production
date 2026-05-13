"""CAS Integration for CAF

Integrates CAF with CAS (Cognitive Analysis System) for cognitive state
monitoring and introspection during capability activation.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

try:
    from cas import IntrospectionProtocol, AttentionMonitor
    from cas.introspection import IntrospectionType
    from cas.attention import AttentionState
    CAS_AVAILABLE = True
except ImportError:
    CAS_AVAILABLE = False
    IntrospectionProtocol = None
    AttentionMonitor = None
    IntrospectionType = None
    AttentionState = None


class CASIntegration:
    """CAS integration for CAF cognitive monitoring"""
    
    def __init__(self, session_id: Optional[str] = None):
        """Initialize CAS integration
        
        Args:
            session_id: Optional session ID for CAS
        """
        self.enabled = CAS_AVAILABLE
        self.session_id = session_id or "caf_session"
        
        if self.enabled:
            try:
                self.introspection = IntrospectionProtocol(self.session_id)
                self.attention_monitor = AttentionMonitor(self.session_id)
            except Exception:
                self.introspection = None
                self.attention_monitor = None
        else:
            self.introspection = None
            self.attention_monitor = None
    
    def check_cognitive_state(self) -> Dict[str, Any]:
        """Check current cognitive state
        
        Returns:
            Dictionary with cognitive state information
        """
        if not self.enabled or not self.attention_monitor:
            return {
                "available": False,
                "message": "CAS not available"
            }
        
        try:
            attention_state = self.attention_monitor.get_current_state()
            
            return {
                "available": True,
                "attention_state": attention_state.state.value if hasattr(attention_state.state, 'value') else str(attention_state.state),
                "cognitive_load": attention_state.cognitive_load,
                "focus_areas": attention_state.focus_areas,
                "timestamp": attention_state.timestamp.isoformat() if hasattr(attention_state, 'timestamp') else None
            }
        except Exception as e:
            return {
                "available": False,
                "error": str(e)
            }
    
    def run_introspection(
        self,
        introspection_type: IntrospectionType = IntrospectionType.HOURLY_CHECK
    ) -> Optional[Any]:
        """Run cognitive introspection
        
        Args:
            introspection_type: Type of introspection
            
        Returns:
            IntrospectionResult if available, None otherwise
        """
        if not self.enabled or not self.introspection:
            return None
        
        try:
            result = self.introspection.run_introspection(introspection_type)
            return result
        except Exception:
            return None
    
    def should_activate_capability(
        self,
        capability_type: str,
        confidence: float
    ) -> Dict[str, Any]:
        """Check if capability should be activated based on cognitive state
        
        Args:
            capability_type: Type of capability
            confidence: Confidence score
            
        Returns:
            Dictionary with activation recommendation
        """
        cognitive_state = self.check_cognitive_state()
        
        if not cognitive_state.get("available"):
            return {
                "should_activate": True,
                "reason": "CAS not available, default to activate"
            }
        
        # Check cognitive load
        cognitive_load = cognitive_state.get("cognitive_load", 0.5)
        
        if cognitive_load > 0.9:
            return {
                "should_activate": False,
                "reason": "Cognitive load too high",
                "cognitive_load": cognitive_load
            }
        
        if cognitive_load > 0.7 and confidence < 0.8:
            return {
                "should_activate": False,
                "reason": "High cognitive load and low confidence",
                "cognitive_load": cognitive_load,
                "confidence": confidence
            }
        
        return {
            "should_activate": True,
            "reason": "Cognitive state allows activation",
            "cognitive_load": cognitive_load
        }

