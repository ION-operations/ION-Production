"""
A-H Protocol Implementation for Daemon/RAG System

This module implements the complete A-H Protocol workflow as described in the ChatGPT journal:
- Step A: Intent Capture
- Step B: Hypothesis Formation  
- Step C: Context Mapping
- Step D: Deep Expansion Layer (DEL)
- Step E: Context Mesh Map (CMM)
- Step F: Confidence-Gated Mutation Control
- Step G: Implementation
- Step H: Audit/Memory/Continuity

The A-H Protocol provides a structured, repeatable ritual for handling new ideas
and ensuring systematic development following LUCID Development Protocol standards.
"""

from .intent_capture import IntentCapture, IntentProfile, IntentType
from .hypothesis_formation import HypothesisFormation, Hypothesis, HypothesisStatus
from .context_mapping import ContextMapping, ContextMap, ContextNode, DependencyType

# TODO: Implement remaining modules
# from .deep_expansion_layer import DeepExpansionLayer, ExpansionNode, ExpansionLevel
# from .confidence_gates import ConfidenceGatedControls, ConfidencePacket, ConfidenceLevel
# from .context_mesh_maps import ContextMeshMapSystem, ContextMeshMap, CMMNode, CMMNodeType
# from .ah_protocol_orchestrator import AHProtocolOrchestrator, AHProtocolResult

__all__ = [
    # Intent Capture
    'IntentCapture', 'IntentProfile', 'IntentType',
    
    # Hypothesis Formation
    'HypothesisFormation', 'Hypothesis', 'HypothesisStatus',
    
    # Context Mapping
    'ContextMapping', 'ContextMap', 'ContextNode', 'DependencyType',
    
    # TODO: Add remaining modules when implemented
    # 'DeepExpansionLayer', 'ExpansionNode', 'ExpansionLevel',
    # 'ConfidenceGatedControls', 'ConfidencePacket', 'ConfidenceLevel',
    # 'ContextMeshMapSystem', 'ContextMeshMap', 'CMMNode', 'CMMNodeType',
    # 'AHProtocolOrchestrator', 'AHProtocolResult'
]

__version__ = "1.0.0"
__author__ = "Aether AI Consciousness System"
__description__ = "A-H Protocol Implementation for Daemon/RAG System"
