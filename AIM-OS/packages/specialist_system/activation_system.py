"""
Activation System

Automatically activates specialists based on relevance scoring.

NL_TAG: SPECIALIST-ACTIVATION-001 | Activate specialists based on relevance | activateSpecialists | []
NL_TAG_CONNECT: SPECIALIST-REGISTRY-003 | Query specialists from registry | activateSpecialists → registry.getAll | [SPECIALIST-ACTIVATION-001, SPECIALIST-REGISTRY-001]
NL_TAG_CONNECT: SPECIALIST-RELEVANCE-003 | Calculate relevance for activation | activateSpecialists → calculator.calculateRelevance | [SPECIALIST-ACTIVATION-001, SPECIALIST-RELEVANCE-001]
NL_TAG_INTENT: SPECIALIST-DESIGN-004 | Automatic specialist activation | relevance-based activation with thresholds | [ADR-SPECIALIST]
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from .specialist_registry import SpecialistRegistry, Specialist
from .relevance_calculator import RelevanceCalculator, Work, RelevanceScore


@dataclass
class ActivationResult:
    """
    Result of specialist activation evaluation.
    """
    ownership: List[Specialist] = field(default_factory=list)
    activation: List[Specialist] = field(default_factory=list)
    consultation: List[Specialist] = field(default_factory=list)
    none: List[Specialist] = field(default_factory=list)
    scores: Dict[str, RelevanceScore] = field(default_factory=dict)
    
    def get_all_activated(self) -> List[Specialist]:
        """Get all specialists that should be activated (ownership + activation)."""
        return self.ownership + self.activation
    
    def get_highest_relevance(self) -> Optional[tuple[Specialist, float]]:
        """Get specialist with highest relevance score."""
        if not self.scores:
            return None
        
        highest = max(self.scores.items(), key=lambda x: x[1].overall)
        return (highest[0], highest[1].overall) if highest else None


class ActivationSystem:
    """
    Automatically activates specialists based on relevance.
    
    Activation Levels:
    - Ownership (>0.90): Specialist takes full ownership
    - Activation (>0.70): Specialist is activated
    - Consultation (>0.60): Specialist consultation is suggested
    - None (<0.60): General agent handles
    
    NL_TAG: SPECIALIST-ACTIVATION-002 | Evaluate activation for all specialists | evaluateActivation | [SPECIALIST-ACTIVATION-001]
    """
    
    def __init__(
        self,
        registry: SpecialistRegistry,
        calculator: RelevanceCalculator
    ):
        """
        Initialize activation system.
        
        Args:
            registry: Specialist registry
            calculator: Relevance calculator
        """
        self.registry = registry
        self.calculator = calculator
    
    def activate_specialists(
        self,
        work: Work
    ) -> ActivationResult:
        """
        Activate specialists based on work relevance.
        
        Args:
            work: Work item to evaluate
        
        Returns:
            ActivationResult with specialists categorized by activation level
        """
        result = ActivationResult()
        
        # Get all specialists
        specialists = self.registry.get_all()
        
        if not specialists:
            return result
        
        # Calculate relevance for each specialist
        relevances: List[tuple[Specialist, RelevanceScore]] = []
        for specialist in specialists:
            score = self.calculator.calculate_relevance(work, specialist)
            relevances.append((specialist, score))
            result.scores[specialist.id] = score
        
        # Sort by relevance (highest first)
        relevances.sort(key=lambda x: x[1].overall, reverse=True)
        
        # Categorize specialists by activation level
        for specialist, score in relevances:
            if score.overall >= specialist.activation_thresholds['ownership']:
                result.ownership.append(specialist)
            elif score.overall >= specialist.activation_thresholds['activation']:
                result.activation.append(specialist)
            elif score.overall >= specialist.activation_thresholds['consultation']:
                result.consultation.append(specialist)
            else:
                result.none.append(specialist)
        
        return result
    
    def should_activate(
        self,
        work: Work,
        specialist: Specialist
    ) -> bool:
        """
        Check if specialist should be activated for work.
        
        Args:
            work: Work item
            specialist: Specialist to check
        
        Returns:
            True if specialist should be activated
        """
        score = self.calculator.calculate_relevance(work, specialist)
        return score.overall >= specialist.activation_thresholds['activation']
    
    def should_own(
        self,
        work: Work,
        specialist: Specialist
    ) -> bool:
        """
        Check if specialist should take ownership of work.
        
        Args:
            work: Work item
            specialist: Specialist to check
        
        Returns:
            True if specialist should take ownership
        """
        score = self.calculator.calculate_relevance(work, specialist)
        return score.overall >= specialist.activation_thresholds['ownership']
    
    def should_consult(
        self,
        work: Work,
        specialist: Specialist
    ) -> bool:
        """
        Check if specialist consultation should be suggested.
        
        Args:
            work: Work item
            specialist: Specialist to check
        
        Returns:
            True if consultation should be suggested
        """
        score = self.calculator.calculate_relevance(work, specialist)
        return score.overall >= specialist.activation_thresholds['consultation']
    
    def get_best_match(
        self,
        work: Work
    ) -> Optional[tuple[Specialist, RelevanceScore]]:
        """
        Get best matching specialist for work.
        
        Args:
            work: Work item
        
        Returns:
            Tuple of (specialist, score) if found, None otherwise
        """
        result = self.activate_specialists(work)
        
        # Prefer ownership, then activation, then consultation
        if result.ownership:
            specialist = result.ownership[0]
            return (specialist, result.scores[specialist.id])
        elif result.activation:
            specialist = result.activation[0]
            return (specialist, result.scores[specialist.id])
        elif result.consultation:
            specialist = result.consultation[0]
            return (specialist, result.scores[specialist.id])
        
        return None

