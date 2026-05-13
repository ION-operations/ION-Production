"""
Relevance Calculator

Calculates relevance of work to specialists using multi-factor algorithm.

NL_TAG: SPECIALIST-RELEVANCE-001 | Calculate work relevance to specialist | calculateRelevance | []
NL_TAG_CONNECT: SPECIALIST-HHNI-001 | Use HHNI for data connections | calculateDataConnections → hhni.search | [SPECIALIST-RELEVANCE-001, HHNI-SEARCH-001]
NL_TAG_CONNECT: SPECIALIST-SEG-001 | Use SEG for pattern recognition | calculatePatternRecognition → seg.getPatterns | [SPECIALIST-RELEVANCE-001, SEG-PATTERN-001]
NL_TAG_INTENT: SPECIALIST-DESIGN-002 | Multi-factor relevance scoring | domain + data + system + pattern + complexity | [ADR-SPECIALIST]
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from .specialist_registry import Specialist


@dataclass
class Work:
    """
    Work item that needs specialist evaluation.
    
    Represents a piece of work that may benefit from specialist expertise.
    """
    description: str
    domain: Optional[List[str]] = None
    systems: Optional[List[str]] = None
    data: Optional[List[str]] = None
    patterns: Optional[List[str]] = None
    complexity: Optional[float] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.domain is None:
            self.domain = []
        if self.systems is None:
            self.systems = []
        if self.data is None:
            self.data = []
        if self.patterns is None:
            self.patterns = []
        if self.complexity is None:
            self.complexity = 0.5  # Default moderate complexity


@dataclass
class RelevanceScore:
    """
    Detailed relevance score breakdown.
    """
    overall: float
    domain_match: float
    data_connections: float
    system_connections: float
    pattern_recognition: float
    complexity: float
    factors: Dict[str, float]  # Original relevance factors used


class RelevanceCalculator:
    """
    Calculates relevance of work to specialists.
    
    Uses multi-factor algorithm:
    - Domain Match (40%): Does work match specialist's domain?
    - Data Connections (25%): Are retrieved data linked to specialist?
    - System Connections (20%): Does work involve systems specialist knows?
    - Pattern Recognition (10%): Does work match specialist's patterns?
    - Complexity (5%): Is work complex enough to need specialist?
    
    NL_TAG: SPECIALIST-RELEVANCE-002 | Calculate individual relevance factors | calculateDomainMatch, calculateDataConnections, etc. | [SPECIALIST-RELEVANCE-001]
    """
    
    def __init__(self):
        """Initialize relevance calculator."""
        # Default relevance factor weights (can be overridden by specialist)
        self.default_factors = {
            'domain_match': 0.40,
            'data_connections': 0.25,
            'system_connections': 0.20,
            'pattern_recognition': 0.10,
            'complexity': 0.05
        }
    
    def calculate_relevance(
        self,
        work: Work,
        specialist: Specialist
    ) -> RelevanceScore:
        """
        Calculate relevance of work to specialist.
        
        Args:
            work: Work item to evaluate
            specialist: Specialist to evaluate against
            
        Returns:
            RelevanceScore with overall score and breakdown
        """
        # Use specialist's relevance factors if available, otherwise defaults
        factors = specialist.relevance_factors or self.default_factors
        
        # Calculate individual factors
        domain_match = self._calculate_domain_match(work, specialist)
        data_connections = self._calculate_data_connections(work, specialist)
        system_connections = self._calculate_system_connections(work, specialist)
        pattern_recognition = self._calculate_pattern_recognition(work, specialist)
        complexity = self._calculate_complexity(work)
        
        # Calculate overall relevance
        overall = (
            factors['domain_match'] * domain_match +
            factors['data_connections'] * data_connections +
            factors['system_connections'] * system_connections +
            factors['pattern_recognition'] * pattern_recognition +
            factors['complexity'] * complexity
        )
        
        # Ensure score is between 0.0 and 1.0
        overall = max(0.0, min(1.0, overall))
        
        return RelevanceScore(
            overall=overall,
            domain_match=domain_match,
            data_connections=data_connections,
            system_connections=system_connections,
            pattern_recognition=pattern_recognition,
            complexity=complexity,
            factors=factors
        )
    
    def _calculate_domain_match(
        self,
        work: Work,
        specialist: Specialist
    ) -> float:
        """
        Calculate domain match score.
        
        Args:
            work: Work item
            specialist: Specialist
            
        Returns:
            Score between 0.0 and 1.0
        """
        if not work.domain or not specialist.domain:
            return 0.0
        
        # Calculate intersection over union (Jaccard similarity)
        work_domains = set(work.domain)
        specialist_domains = set(specialist.domain)
        
        intersection = work_domains & specialist_domains
        union = work_domains | specialist_domains
        
        if not union:
            return 0.0
        
        return len(intersection) / len(union)
    
    def _calculate_data_connections(
        self,
        work: Work,
        specialist: Specialist
    ) -> float:
        """
        Calculate data connections score.
        
        Args:
            work: Work item
            specialist: Specialist
            
        Returns:
            Score between 0.0 and 1.0
        """
        if not work.data:
            return 0.0
        
        specialist_data = set(specialist.connections.get('data', []))
        work_data = set(work.data)
        
        if not specialist_data:
            return 0.0
        
        # Calculate how many work data items are connected to specialist
        matches = work_data & specialist_data
        
        if not work_data:
            return 0.0
        
        return len(matches) / len(work_data)
    
    def _calculate_system_connections(
        self,
        work: Work,
        specialist: Specialist
    ) -> float:
        """
        Calculate system connections score.
        
        Args:
            work: Work item
            specialist: Specialist
            
        Returns:
            Score between 0.0 and 1.0
        """
        if not work.systems:
            return 0.0
        
        specialist_systems = set(specialist.connections.get('systems', []))
        work_systems = set(work.systems)
        
        if not specialist_systems:
            return 0.0
        
        # Calculate how many work systems are connected to specialist
        matches = work_systems & specialist_systems
        
        if not work_systems:
            return 0.0
        
        return len(matches) / len(work_systems)
    
    def _calculate_pattern_recognition(
        self,
        work: Work,
        specialist: Specialist
    ) -> float:
        """
        Calculate pattern recognition score.
        
        Args:
            work: Work item
            specialist: Specialist
            
        Returns:
            Score between 0.0 and 1.0
        """
        if not work.patterns:
            return 0.0
        
        specialist_patterns = set(specialist.connections.get('patterns', []))
        work_patterns = set(work.patterns)
        
        if not specialist_patterns:
            return 0.0
        
        # Calculate how many work patterns match specialist patterns
        matches = work_patterns & specialist_patterns
        
        if not work_patterns:
            return 0.0
        
        return len(matches) / len(work_patterns)
    
    def _calculate_complexity(
        self,
        work: Work
    ) -> float:
        """
        Calculate complexity score.
        
        Args:
            work: Work item
            
        Returns:
            Score between 0.0 and 1.0 (work.complexity normalized)
        """
        # Normalize complexity to 0.0-1.0 range
        # If complexity is None, default to 0.5 (moderate)
        complexity = work.complexity or 0.5
        return max(0.0, min(1.0, complexity))

