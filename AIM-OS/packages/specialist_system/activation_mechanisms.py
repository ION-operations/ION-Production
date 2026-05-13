"""
Activation Mechanisms

Three levels of specialist activation: warning, activation, ownership.

NL_TAG: SPECIALIST-ACTIVATION-003 | Show consultation warning | showConsultationWarning | [SPECIALIST-ACTIVATION-001]
NL_TAG: SPECIALIST-ACTIVATION-004 | Activate specialist | activateSpecialist | [SPECIALIST-ACTIVATION-001]
NL_TAG: SPECIALIST-ACTIVATION-005 | Assign specialist ownership | assignOwnership | [SPECIALIST-ACTIVATION-001]
"""

from typing import Dict, List, Any
from .specialist_registry import Specialist
from .relevance_calculator import Work, RelevanceScore
from .activation_system import ActivationResult


class ActivationMechanisms:
    """
    Three activation mechanisms for specialists.
    
    Provides three levels of activation:
    - Level 1 (0.60-0.69): Consultation warning
    - Level 2 (0.70-0.89): Automatic activation
    - Level 3 (0.90+): Specialist ownership
    
    NL_TAG: SPECIALIST-ACTIVATION-006 | Handle activation mechanisms | handleActivation | [SPECIALIST-ACTIVATION-003, SPECIALIST-ACTIVATION-004, SPECIALIST-ACTIVATION-005]
    """
    
    def show_consultation_warning(
        self,
        work: Work,
        specialist: Specialist,
        relevance: RelevanceScore
    ) -> Dict[str, Any]:
        """
        Show consultation warning (Level 1: 0.60-0.69 relevance).
        
        Args:
            work: Work item
            specialist: Specialist to consult
            relevance: Relevance score
            
        Returns:
            Warning message and metadata
        """
        return {
            'type': 'consultation',
            'level': 1,
            'message': f"⚠️ This work is relevant to {specialist.name} ({relevance.overall:.2f} relevance). Consider consulting.",
            'specialist_id': specialist.id,
            'specialist_name': specialist.name,
            'relevance': relevance.overall,
            'relevance_breakdown': {
                'domain_match': relevance.domain_match,
                'data_connections': relevance.data_connections,
                'system_connections': relevance.system_connections,
                'pattern_recognition': relevance.pattern_recognition,
                'complexity': relevance.complexity
            },
            'action': 'suggest_consultation',
            'work_description': work.description
        }
    
    def activate_specialist(
        self,
        work: Work,
        specialist: Specialist,
        relevance: RelevanceScore
    ) -> Dict[str, Any]:
        """
        Activate specialist (Level 2: 0.70-0.89 relevance).
        
        Args:
            work: Work item
            specialist: Specialist to activate
            relevance: Relevance score
            
        Returns:
            Activation message and metadata
        """
        return {
            'type': 'activation',
            'level': 2,
            'message': f"🔄 Activating {specialist.name} ({relevance.overall:.2f} relevance detected)",
            'specialist_id': specialist.id,
            'specialist_name': specialist.name,
            'relevance': relevance.overall,
            'relevance_breakdown': {
                'domain_match': relevance.domain_match,
                'data_connections': relevance.data_connections,
                'system_connections': relevance.system_connections,
                'pattern_recognition': relevance.pattern_recognition,
                'complexity': relevance.complexity
            },
            'action': 'activate',
            'work_description': work.description,
            'specialist_domain': specialist.domain,
            'specialist_systems': specialist.connections.get('systems', [])
        }
    
    def assign_ownership(
        self,
        work: Work,
        specialist: Specialist,
        relevance: RelevanceScore
    ) -> Dict[str, Any]:
        """
        Assign specialist ownership (Level 3: 0.90+ relevance).
        
        Args:
            work: Work item
            specialist: Specialist taking ownership
            relevance: Relevance score
            
        Returns:
            Ownership message and metadata
        """
        return {
            'type': 'ownership',
            'level': 3,
            'message': f"🎯 {specialist.name} taking ownership ({relevance.overall:.2f} relevance)",
            'specialist_id': specialist.id,
            'specialist_name': specialist.name,
            'relevance': relevance.overall,
            'relevance_breakdown': {
                'domain_match': relevance.domain_match,
                'data_connections': relevance.data_connections,
                'system_connections': relevance.system_connections,
                'pattern_recognition': relevance.pattern_recognition,
                'complexity': relevance.complexity
            },
            'action': 'take_ownership',
            'work_description': work.description,
            'specialist_domain': specialist.domain,
            'specialist_systems': specialist.connections.get('systems', [])
        }
    
    def handle_activation_result(
        self,
        work: Work,
        activation_result: ActivationResult
    ) -> List[Dict[str, Any]]:
        """
        Handle activation result and generate all activation mechanisms.
        
        Processes activation result and generates appropriate mechanisms
        for each activation level (ownership, activation, consultation).
        
        Args:
            work: Work item
            activation_result: Result from activation system
            
        Returns:
            List of activation messages/actions, sorted by priority
        """
        mechanisms = []
        
        # Ownership (highest priority - Level 3)
        for specialist in activation_result.ownership:
            score = activation_result.scores[specialist.id]
            mechanisms.append(
                self.assign_ownership(work, specialist, score)
            )
        
        # Activation (Level 2)
        for specialist in activation_result.activation:
            score = activation_result.scores[specialist.id]
            mechanisms.append(
                self.activate_specialist(work, specialist, score)
            )
        
        # Consultation (lowest priority - Level 1)
        for specialist in activation_result.consultation:
            score = activation_result.scores[specialist.id]
            mechanisms.append(
                self.show_consultation_warning(work, specialist, score)
            )
        
        # Sort by level (highest first: 3, 2, 1)
        mechanisms.sort(key=lambda x: x['level'], reverse=True)
        
        return mechanisms
    
    def get_primary_activation(
        self,
        mechanisms: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Get primary activation mechanism (highest priority).
        
        Args:
            mechanisms: List of activation mechanisms (may be unsorted)
            
        Returns:
            Primary activation mechanism, or None if empty
        """
        if not mechanisms:
            return None
        
        # Sort by level (highest first) and return first
        sorted_mechanisms = sorted(mechanisms, key=lambda x: x.get('level', 0), reverse=True)
        return sorted_mechanisms[0]
    
    def format_activation_summary(
        self,
        mechanisms: List[Dict[str, Any]]
    ) -> str:
        """
        Format activation mechanisms as human-readable summary.
        
        Args:
            mechanisms: List of activation mechanisms
            
        Returns:
            Formatted summary string
        """
        if not mechanisms:
            return "No specialist activation needed."
        
        summary_parts = []
        
        # Group by type
        ownership = [m for m in mechanisms if m['type'] == 'ownership']
        activation = [m for m in mechanisms if m['type'] == 'activation']
        consultation = [m for m in mechanisms if m['type'] == 'consultation']
        
        if ownership:
            names = [m['specialist_name'] for m in ownership]
            summary_parts.append(f"🎯 Ownership: {', '.join(names)}")
        
        if activation:
            names = [m['specialist_name'] for m in activation]
            summary_parts.append(f"🔄 Activated: {', '.join(names)}")
        
        if consultation:
            names = [m['specialist_name'] for m in consultation]
            summary_parts.append(f"⚠️ Consultation: {', '.join(names)}")
        
        return "\n".join(summary_parts)

