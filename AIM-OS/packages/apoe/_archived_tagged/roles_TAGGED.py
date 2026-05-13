"""APOE Role System

The 8 specialized AI agent roles for orchestrated operation.
"""

from __future__ import annotations
from enum import Enum


# NL_TAG: VIF-MODEL-001 | The 8 specialized AI agent roles in APOE. | class RoleType | []
class RoleType(str, Enum):
    """
    The 8 specialized AI agent roles in APOE.
    
    Each role has specific capabilities and constraints.
    """
    PLANNER = "planner"        # Strategic planning, decomposition
    RETRIEVER = "retriever"    # Memory/knowledge retrieval
    REASONER = "reasoner"      # Logical reasoning, inference
    VERIFIER = "verifier"      # Validation, fact-checking
    BUILDER = "builder"        # Code/artifact construction
    CRITIC = "critic"          # Quality assessment, improvement
    OPERATOR = "operator"      # System operations, execution
    WITNESS = "witness"        # Observation, provenance

    # NL_TAG: VIF-UTIL-001 | Get role description. | description(self) | []
    def description(self) -> str:
        """Get role description."""
        descriptions = {
            RoleType.PLANNER: "Strategic planning and task decomposition",
            RoleType.RETRIEVER: "Memory and knowledge retrieval from CMC/HHNI",
            RoleType.REASONER: "Logical reasoning and inference",
            RoleType.VERIFIER: "Validation and fact-checking",
            RoleType.BUILDER: "Code and artifact construction",
            RoleType.CRITIC: "Quality assessment and improvement suggestions",
            RoleType.OPERATOR: "System operations and execution",
            RoleType.WITNESS: "Observation and provenance tracking"
        }
        return descriptions[self]
    
    # NL_TAG: VIF-UTIL-002 | Get recommended temperature for this role. | default_temperature(self) | []
    def default_temperature(self) -> float:
        """Get recommended temperature for this role."""
        temperatures = {
            RoleType.PLANNER: 0.7,      # Creative but structured
            RoleType.RETRIEVER: 0.0,    # Deterministic retrieval
            RoleType.REASONER: 0.7,     # Balanced reasoning
            RoleType.VERIFIER: 0.0,     # Strict validation
            RoleType.BUILDER: 0.5,      # Moderate creativity
            RoleType.CRITIC: 0.8,       # Creative criticism
            RoleType.OPERATOR: 0.0,     # Deterministic operations
            RoleType.WITNESS: 0.0       # Objective observation
        }
        return temperatures[self]

