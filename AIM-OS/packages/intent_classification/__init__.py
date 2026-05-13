"""
Intent Classification System - Core Package

A cognitive gateway for Aether's decision-making process, transforming raw user input 
into structured, actionable mission profiles that govern all subsequent behavior.

This system provides:
- Multi-axis intent classification
- Behavior gating and risk assessment
- Mission management and timeline integration
- Enforcement layer for safety controls
"""

from .mission_intent import MissionIntent, MissionStatus, PrimaryCategory, LifecycleStage, ScopeLevel, ClarityState
from .classification_engine import ClassificationEngine
from .enforcement_layer import EnforcementLayer
from .timeline_integration import TimelineIntegration

__version__ = "1.0.0"
__all__ = [
    "MissionIntent",
    "MissionStatus", 
    "PrimaryCategory",
    "LifecycleStage",
    "ScopeLevel",
    "ClarityState",
    "ClassificationEngine",
    "EnforcementLayer",
    "TimelineIntegration"
]
