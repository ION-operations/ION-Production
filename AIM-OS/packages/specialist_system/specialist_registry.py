"""
Specialist Registry System

Maintains registry of all specialist agents with their domains, connections,
and activation thresholds.

NL_TAG: SPECIALIST-REGISTRY-001 | Maintain specialist registry | SpecialistRegistry | []
NL_TAG_CONNECT: SPECIALIST-CMC-001 | Store specialists in CMC | register → cmc.storeAtom | [SPECIALIST-REGISTRY-001, CMC-STORE-001]
NL_TAG_INTENT: SPECIALIST-DESIGN-001 | Enable automatic specialist discovery | domain/system queries | [ADR-SPECIALIST]
NL_TAG_SPEC: SPECIALIST-SPEC-001 | Validates specialist schema | validate_specialist | [specialist_schema.json]
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class Specialist:
    """
    Specialist agent definition.
    
    Represents a domain expert with deep knowledge in specific areas.
    """
    id: str
    name: str
    domain: List[str]  # Domain areas (e.g., ["UI", "UX", "Design"])
    description: str
    connections: Dict[str, List[str]] = field(default_factory=lambda: {
        'systems': [],
        'data': [],
        'patterns': []
    })
    relevance_factors: Dict[str, float] = field(default_factory=lambda: {
        'domain_match': 0.40,
        'data_connections': 0.25,
        'system_connections': 0.20,
        'pattern_recognition': 0.10,
        'complexity': 0.05
    })
    activation_thresholds: Dict[str, float] = field(default_factory=lambda: {
        'ownership': 0.90,
        'activation': 0.70,
        'consultation': 0.60
    })
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate specialist data after initialization."""
        if not self.id:
            raise ValueError("Specialist ID is required")
        if not self.name:
            raise ValueError("Specialist name is required")
        if not self.domain:
            raise ValueError("Specialist must have at least one domain")
        if sum(self.relevance_factors.values()) != 1.0:
            raise ValueError("Relevance factors must sum to 1.0")
        if not (0.0 <= self.activation_thresholds['consultation'] <= 
                self.activation_thresholds['activation'] <= 
                self.activation_thresholds['ownership'] <= 1.0):
            raise ValueError("Activation thresholds must be in ascending order (0.0-1.0)")
    
    def to_dict(self) -> Dict:
        """Convert specialist to dictionary for storage."""
        return {
            'id': self.id,
            'name': self.name,
            'domain': self.domain,
            'description': self.description,
            'connections': self.connections,
            'relevance_factors': self.relevance_factors,
            'activation_thresholds': self.activation_thresholds,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Specialist':
        """Create specialist from dictionary."""
        data = data.copy()
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)


class SpecialistRegistry:
    """
    Registry for all specialist agents.
    
    Maintains a registry of specialists and provides query capabilities
    for finding specialists by domain, system, or other criteria.
    
    NL_TAG: SPECIALIST-REGISTRY-002 | Query specialists by domain/system | findByDomain, findBySystem | [SPECIALIST-REGISTRY-001]
    NL_TAG_CONNECT: SPECIALIST-CMC-002 | Load specialists from CMC | loadFromCMC → cmc.queryAtoms | [SPECIALIST-REGISTRY-001, CMC-QUERY-001]
    """
    
    def __init__(self):
        """Initialize specialist registry."""
        self._specialists: Dict[str, Specialist] = {}
        self._domain_index: Dict[str, Set[str]] = {}  # domain -> set of specialist IDs
        self._system_index: Dict[str, Set[str]] = {}  # system -> set of specialist IDs
    
    def register(self, specialist: Specialist) -> None:
        """
        Register a specialist in the registry.
        
        Args:
            specialist: Specialist to register
            
        Raises:
            ValueError: If specialist ID already exists
        """
        if specialist.id in self._specialists:
            raise ValueError(f"Specialist with ID '{specialist.id}' already registered")
        
        self._specialists[specialist.id] = specialist
        
        # Update domain index
        for domain in specialist.domain:
            if domain not in self._domain_index:
                self._domain_index[domain] = set()
            self._domain_index[domain].add(specialist.id)
        
        # Update system index
        for system in specialist.connections.get('systems', []):
            if system not in self._system_index:
                self._system_index[system] = set()
            self._system_index[system].add(specialist.id)
    
    def get(self, specialist_id: str) -> Optional[Specialist]:
        """
        Get specialist by ID.
        
        Args:
            specialist_id: ID of specialist to retrieve
            
        Returns:
            Specialist if found, None otherwise
        """
        return self._specialists.get(specialist_id)
    
    def get_all(self) -> List[Specialist]:
        """
        Get all registered specialists.
        
        Returns:
            List of all specialists
        """
        return list(self._specialists.values())
    
    def find_by_domain(self, domain: str) -> List[Specialist]:
        """
        Find specialists by domain.
        
        Args:
            domain: Domain to search for
            
        Returns:
            List of specialists in the domain
        """
        specialist_ids = self._domain_index.get(domain, set())
        return [self._specialists[sid] for sid in specialist_ids if sid in self._specialists]
    
    def find_by_system(self, system: str) -> List[Specialist]:
        """
        Find specialists by system.
        
        Args:
            system: System to search for
            
        Returns:
            List of specialists connected to the system
        """
        specialist_ids = self._system_index.get(system, set())
        return [self._specialists[sid] for sid in specialist_ids if sid in self._specialists]
    
    def find_by_domains(self, domains: List[str]) -> List[Specialist]:
        """
        Find specialists by multiple domains (union).
        
        Args:
            domains: List of domains to search for
            
        Returns:
            List of specialists in any of the domains
        """
        specialist_ids = set()
        for domain in domains:
            specialist_ids.update(self._domain_index.get(domain, set()))
        return [self._specialists[sid] for sid in specialist_ids if sid in self._specialists]
    
    def find_by_systems(self, systems: List[str]) -> List[Specialist]:
        """
        Find specialists by multiple systems (union).
        
        Args:
            systems: List of systems to search for
            
        Returns:
            List of specialists connected to any of the systems
        """
        specialist_ids = set()
        for system in systems:
            specialist_ids.update(self._system_index.get(system, set()))
        return [self._specialists[sid] for sid in specialist_ids if sid in self._specialists]
    
    def update(self, specialist: Specialist) -> None:
        """
        Update an existing specialist.
        
        Args:
            specialist: Updated specialist
            
        Raises:
            ValueError: If specialist ID doesn't exist
        """
        if specialist.id not in self._specialists:
            raise ValueError(f"Specialist with ID '{specialist.id}' not found")
        
        # Remove old indexes
        old_specialist = self._specialists[specialist.id]
        for domain in old_specialist.domain:
            if domain in self._domain_index:
                self._domain_index[domain].discard(specialist.id)
        for system in old_specialist.connections.get('systems', []):
            if system in self._system_index:
                self._system_index[system].discard(specialist.id)
        
        # Update specialist
        specialist.updated_at = datetime.now()
        
        # Update in registry (don't call register to avoid duplicate check)
        self._specialists[specialist.id] = specialist
        
        # Add to new indexes
        for domain in specialist.domain:
            if domain not in self._domain_index:
                self._domain_index[domain] = set()
            self._domain_index[domain].add(specialist.id)
        for system in specialist.connections.get('systems', []):
            if system not in self._system_index:
                self._system_index[system] = set()
            self._system_index[system].add(specialist.id)
    
    def remove(self, specialist_id: str) -> None:
        """
        Remove a specialist from the registry.
        
        Args:
            specialist_id: ID of specialist to remove
            
        Raises:
            ValueError: If specialist ID doesn't exist
        """
        if specialist_id not in self._specialists:
            raise ValueError(f"Specialist with ID '{specialist_id}' not found")
        
        specialist = self._specialists[specialist_id]
        
        # Remove from indexes
        for domain in specialist.domain:
            if domain in self._domain_index:
                self._domain_index[domain].discard(specialist_id)
        for system in specialist.connections.get('systems', []):
            if system in self._system_index:
                self._system_index[system].discard(specialist_id)
        
        # Remove specialist
        del self._specialists[specialist_id]
    
    def count(self) -> int:
        """
        Get total number of registered specialists.
        
        Returns:
            Number of specialists
        """
        return len(self._specialists)
    
    def get_domains(self) -> List[str]:
        """
        Get all unique domains.
        
        Returns:
            List of all domains
        """
        return sorted(self._domain_index.keys())
    
    def get_systems(self) -> List[str]:
        """
        Get all unique systems.
        
        Returns:
            List of all systems
        """
        return sorted(self._system_index.keys())

