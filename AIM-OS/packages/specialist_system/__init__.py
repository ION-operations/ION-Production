"""
Specialist System - Domain Expert Agents with Automatic Activation

This package implements the specialist agent system, enabling domain experts
to be automatically activated when their expertise is needed.

Core Components:
- SpecialistRegistry: Maintains registry of all specialists
- RelevanceCalculator: Calculates relevance of work to specialists
- DataOrganizer: Organizes specialist data hierarchically
- ActivationSystem: Automatically activates specialists based on relevance
"""

from .specialist_registry import SpecialistRegistry, Specialist
from .relevance_calculator import RelevanceCalculator, Work, RelevanceScore
from .data_organization import DataOrganizer, SpecialistData
from .activation_system import ActivationSystem, ActivationResult
from .work_detector import WorkDetector, IntentAnalysis
from .activation_mechanisms import ActivationMechanisms
from .initial_specialists import register_initial_specialists, get_initial_specialists
from .math_tools import MathTools

__all__ = [
    'SpecialistRegistry',
    'Specialist',
    'RelevanceCalculator',
    'Work',
    'RelevanceScore',
    'DataOrganizer',
    'SpecialistData',
    'ActivationSystem',
    'ActivationResult',
    'WorkDetector',
    'IntentAnalysis',
    'ActivationMechanisms',
    'register_initial_specialists',
    'get_initial_specialists',
    'MathTools',
]

__version__ = '0.1.0'

