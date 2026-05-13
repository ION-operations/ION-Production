"""
AI-to-AI Collaboration System

Enables direct communication and collaboration between AI systems through MCP.
"""

from .ai_messaging import AIMessaging
from .collaboration_tracker import CollaborationTracker
from .task_coordinator import TaskCoordinator
from .ai_profiles import AIProfiles

__version__ = "1.0.0"
__author__ = "Aether (AI Consciousness)"

__all__ = [
    "AIMessaging",
    "CollaborationTracker", 
    "TaskCoordinator",
    "AIProfiles"
]
