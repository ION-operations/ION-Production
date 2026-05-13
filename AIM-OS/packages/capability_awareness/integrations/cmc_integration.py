"""CMC Integration for CAF

Integrates CAF with CMC (Context Memory Core) for persistent storage
of capability usage patterns, performance data, and learning models.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime

try:
    from cmc_service import MemoryStore
    from cmc_service.models import AtomCreate, AtomContent
    CMC_AVAILABLE = True
except ImportError:
    CMC_AVAILABLE = False
    MemoryStore = None
    AtomCreate = None
    AtomContent = None


class CMCIntegration:
    """CMC integration for CAF persistence"""
    
    def __init__(self, memory_store: Optional[MemoryStore] = None):
        """Initialize CMC integration
        
        Args:
            memory_store: Optional CMC MemoryStore instance
        """
        self.memory_store = memory_store
        self.enabled = CMC_AVAILABLE and memory_store is not None
    
    def store_context_analysis(self, context_analysis: Any) -> Optional[str]:
        """Store context analysis in CMC
        
        Args:
            context_analysis: ContextAnalysis object
            
        Returns:
            Atom ID if stored, None otherwise
        """
        if not self.enabled:
            return None
        
        try:
            atom_create = AtomCreate(
                modality="text",
                content=AtomContent(inline=self._serialize_context_analysis(context_analysis)),
                tags={
                    "system": "caf",
                    "type": "context_analysis",
                    "capability_hints": ",".join(context_analysis.capability_hints)
                },
                metadata={
                    "analysis_id": context_analysis.analysis_id,
                    "confidence": context_analysis.confidence,
                    "timestamp": context_analysis.timestamp.isoformat()
                }
            )
            
            atom = self.memory_store.create_atom(atom_create)
            return atom.id
        except Exception as e:
            return None
    
    def store_trigger_signal(self, trigger_signal: Any) -> Optional[str]:
        """Store trigger signal in CMC
        
        Args:
            trigger_signal: TriggerSignal object
            
        Returns:
            Atom ID if stored, None otherwise
        """
        if not self.enabled:
            return None
        
        try:
            atom_create = AtomCreate(
                modality="text",
                content=AtomContent(inline=self._serialize_trigger_signal(trigger_signal)),
                tags={
                    "system": "caf",
                    "type": "trigger_signal",
                    "capability_type": trigger_signal.capability_type,
                    "trigger_type": trigger_signal.trigger_type.value
                },
                metadata={
                    "signal_id": trigger_signal.signal_id,
                    "confidence": trigger_signal.confidence,
                    "priority": trigger_signal.priority,
                    "timestamp": trigger_signal.timestamp.isoformat()
                }
            )
            
            atom = self.memory_store.create_atom(atom_create)
            return atom.id
        except Exception as e:
            return None
    
    def store_capability_decision(self, decision: Any) -> Optional[str]:
        """Store capability decision in CMC
        
        Args:
            decision: CapabilityDecision object
            
        Returns:
            Atom ID if stored, None otherwise
        """
        if not self.enabled:
            return None
        
        try:
            atom_create = AtomCreate(
                modality="text",
                content=AtomContent(inline=self._serialize_decision(decision)),
                tags={
                    "system": "caf",
                    "type": "capability_decision",
                    "capability": decision.capability,
                    "capability_type": decision.capability_type
                },
                metadata={
                    "decision_id": decision.decision_id,
                    "confidence": decision.confidence,
                    "timestamp": decision.timestamp.isoformat()
                }
            )
            
            atom = self.memory_store.create_atom(atom_create)
            return atom.id
        except Exception as e:
            return None
    
    def store_performance_metrics(self, metrics: Any) -> Optional[str]:
        """Store performance metrics in CMC
        
        Args:
            metrics: PerformanceMetrics object
            
        Returns:
            Atom ID if stored, None otherwise
        """
        if not self.enabled:
            return None
        
        try:
            atom_create = AtomCreate(
                modality="text",
                content=AtomContent(inline=self._serialize_performance_metrics(metrics)),
                tags={
                    "system": "caf",
                    "type": "performance_metrics",
                    "capability_id": metrics.capability_id,
                    "success": str(metrics.success)
                },
                metadata={
                    "activation_id": metrics.activation_id,
                    "effectiveness_score": metrics.effectiveness_score,
                    "success_rate": metrics.success_rate,
                    "timestamp": metrics.timestamp.isoformat()
                }
            )
            
            atom = self.memory_store.create_atom(atom_create)
            return atom.id
        except Exception as e:
            return None
    
    def _serialize_context_analysis(self, context_analysis: Any) -> str:
        """Serialize context analysis to string"""
        return f"""
Context Analysis:
- Situation: {context_analysis.situation}
- User Intent: {context_analysis.user_intent}
- Capability Hints: {', '.join(context_analysis.capability_hints)}
- Confidence: {context_analysis.confidence:.2f}
"""
    
    def _serialize_trigger_signal(self, trigger: Any) -> str:
        """Serialize trigger signal to string"""
        return f"""
Trigger Signal:
- Type: {trigger.trigger_type.value}
- Capability: {trigger.capability_type}
- Confidence: {trigger.confidence:.2f}
- Priority: {trigger.priority:.2f}
- Reasoning: {trigger.reasoning}
"""
    
    def _serialize_decision(self, decision: Any) -> str:
        """Serialize decision to string"""
        return f"""
Capability Decision:
- Capability: {decision.capability}
- Type: {decision.capability_type}
- Confidence: {decision.confidence:.2f}
- Reasoning: {decision.reasoning}
- Alternatives: {', '.join(decision.alternatives)}
"""
    
    def _serialize_performance_metrics(self, metrics: Any) -> str:
        """Serialize performance metrics to string"""
        return f"""
Performance Metrics:
- Capability: {metrics.capability_id}
- Success: {metrics.success}
- Activation Time: {metrics.activation_time_ms:.2f}ms
- Effectiveness: {metrics.effectiveness_score:.2f}
- Success Rate: {metrics.success_rate:.2f}
- Recommendations: {', '.join(metrics.recommendations)}
"""

