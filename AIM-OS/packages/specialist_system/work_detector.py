"""
Work Detection System

Converts chat input and intent analysis into Work objects for specialist evaluation.

NL_TAG: SPECIALIST-WORK-001 | Detect work from chat input | detectWork | []
NL_TAG_CONNECT: SPECIALIST-INTENT-001 | Use intent analysis for work detection | detectWork → intentAnalysis | [SPECIALIST-WORK-001]
NL_TAG_INTENT: SPECIALIST-DESIGN-005 | Automatic work detection from chat | chat input → Work object | [ADR-SPECIALIST]
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from .relevance_calculator import Work


@dataclass
class IntentAnalysis:
    """
    Intent analysis result from chat orchestrator.
    
    Represents the structured intent analysis that can be used
    to enhance work detection.
    """
    intent: str  # 'question', 'task', 'exploration', etc.
    mode: str  # 'thinking', 'building', 'communicating', etc.
    domains: Optional[List[str]] = None  # Detected domains
    systems: Optional[List[str]] = None  # Detected systems
    complexity: Optional[float] = None  # 0.0-1.0
    
    def __post_init__(self):
        """Initialize default values."""
        if self.domains is None:
            self.domains = []
        if self.systems is None:
            self.systems = []
        if self.complexity is None:
            self.complexity = 0.5  # Default moderate complexity


class WorkDetector:
    """
    Detects work from chat input and converts to Work objects.
    
    Analyzes chat messages to extract:
    - Domain keywords (UI, Language, Chat, Integration)
    - System keywords (React, PLIx, REST, etc.)
    - Data references (from context)
    - Pattern indicators
    - Complexity assessment
    
    NL_TAG: SPECIALIST-WORK-002 | Extract work details from input | extractWorkDetails | [SPECIALIST-WORK-001]
    """
    
    def __init__(self):
        """Initialize work detector with keyword mappings."""
        # Domain keywords mapping
        self.domain_keywords: Dict[str, List[str]] = {
            'UI': ['ui', 'ux', 'design', 'component', 'button', 'form', 'interface', 'frontend', 'layout', 'styling', 'css', 'visual'],
            'Language': ['language', 'lexicon', 'grammar', 'pli', 'pli', 'syntax', 'parser', 'compiler', 'interpreter', 'translation'],
            'Chat': ['chat', 'conversation', 'message', 'dialogue', 'communication', 'discussion', 'thread', 'reply'],
            'Integration': ['api', 'rest', 'graphql', 'websocket', 'backend', 'integration', 'endpoint', 'service', 'microservice'],
            'Mathematics': ['math', 'mathematical', 'equation', 'formula', 'calculate', 'computation', 'statistics', 'data analysis', 'plot', 'graph', 'visualization', 'numpy', 'scipy', 'matplotlib', 'sympy', 'pandas', 'numerical', 'symbolic', 'algebra', 'calculus', 'linear algebra', 'matrix', 'vector']
        }
        
        # System keywords mapping
        self.system_keywords: Dict[str, List[str]] = {
            'React': ['react', 'jsx', 'component', 'hooks', 'redux'],
            'Vue': ['vue', 'nuxt', 'vuex'],
            'Angular': ['angular', 'ng-'],
            'PLIx': ['pli', 'pli', 'planning language'],
            'Tailwind': ['tailwind', 'tailwindcss', 'tw-'],
            'REST': ['rest', 'api', 'endpoint', 'http', 'https'],
            'GraphQL': ['graphql', 'query', 'mutation', 'subscription'],
            'WebSocket': ['websocket', 'ws', 'socket.io', 'real-time'],
            'NumPy': ['numpy', 'np', 'array', 'numerical'],
            'SciPy': ['scipy', 'scientific', 'optimization', 'integration'],
            'Matplotlib': ['matplotlib', 'plt', 'plot', 'graph', 'visualization', 'chart'],
            'SymPy': ['sympy', 'symbolic', 'equation', 'solve', 'algebra'],
            'Pandas': ['pandas', 'pd', 'dataframe', 'data analysis', 'csv']
        }
        
        # Pattern indicators
        self.pattern_keywords: Dict[str, List[str]] = {
            'component-patterns': ['component', 'reusable', 'pattern', 'template', 'widget'],
            'layout-patterns': ['layout', 'grid', 'flexbox', 'responsive', 'mobile'],
            'lexicon-patterns': ['lexicon', 'vocabulary', 'dictionary', 'word', 'term'],
            'api-patterns': ['endpoint', 'route', 'handler', 'controller', 'service']
        }
    
    def detect_work(
        self,
        message: str,
        intent_analysis: Optional[IntentAnalysis] = None
    ) -> Work:
        """
        Detect work from chat message.
        
        Args:
            message: User chat message
            intent_analysis: Optional intent analysis from chat orchestrator
            
        Returns:
            Work object for specialist evaluation
        """
        # Extract domains
        domains = self._extract_domains(message, intent_analysis)
        
        # Extract systems
        systems = self._extract_systems(message, intent_analysis)
        
        # Extract data references (from context)
        data = self._extract_data_references(message)
        
        # Extract patterns
        patterns = self._extract_patterns(message)
        
        # Assess complexity
        complexity = self._assess_complexity(message, intent_analysis)
        
        return Work(
            description=message,
            domain=domains,
            systems=systems,
            data=data,
            patterns=patterns,
            complexity=complexity
        )
    
    def _extract_domains(
        self,
        message: str,
        intent_analysis: Optional[IntentAnalysis]
    ) -> List[str]:
        """
        Extract domain keywords from message.
        
        Args:
            message: Chat message
            intent_analysis: Optional intent analysis
            
        Returns:
            List of detected domains
        """
        message_lower = message.lower()
        domains = []
        
        # Use intent analysis if available
        if intent_analysis and intent_analysis.domains:
            domains.extend(intent_analysis.domains)
        
        # Extract from keywords
        for domain, keywords in self.domain_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                if domain not in domains:
                    domains.append(domain)
        
        return domains
    
    def _extract_systems(
        self,
        message: str,
        intent_analysis: Optional[IntentAnalysis]
    ) -> List[str]:
        """
        Extract system keywords from message.
        
        Args:
            message: Chat message
            intent_analysis: Optional intent analysis
            
        Returns:
            List of detected systems
        """
        message_lower = message.lower()
        systems = []
        
        # Use intent analysis if available
        if intent_analysis and intent_analysis.systems:
            systems.extend(intent_analysis.systems)
        
        # Extract from keywords
        for system, keywords in self.system_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                if system not in systems:
                    systems.append(system)
        
        return systems
    
    def _extract_data_references(self, message: str) -> List[str]:
        """
        Extract data references from message.
        
        TODO: Integrate with HHNI to detect data references from context.
        For now, returns empty list.
        
        Args:
            message: Chat message
            
        Returns:
            List of detected data references
        """
        # TODO: Integrate with HHNI to detect data references
        # For now, return empty list
        return []
    
    def _extract_patterns(self, message: str) -> List[str]:
        """
        Extract pattern indicators from message.
        
        TODO: Integrate with SEG to detect patterns.
        For now, uses keyword matching.
        
        Args:
            message: Chat message
            
        Returns:
            List of detected patterns
        """
        message_lower = message.lower()
        patterns = []
        
        # Extract from keywords
        for pattern, keywords in self.pattern_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                if pattern not in patterns:
                    patterns.append(pattern)
        
        return patterns
    
    def _assess_complexity(
        self,
        message: str,
        intent_analysis: Optional[IntentAnalysis]
    ) -> float:
        """
        Assess work complexity.
        
        Args:
            message: Chat message
            intent_analysis: Optional intent analysis
            
        Returns:
            Complexity score (0.0-1.0)
        """
        # Use intent analysis if available
        if intent_analysis and intent_analysis.complexity is not None:
            return max(0.0, min(1.0, intent_analysis.complexity))
        
        # Simple heuristic: longer messages = more complex
        word_count = len(message.split())
        
        # Also consider question marks (questions tend to be simpler)
        is_question = '?' in message
        
        # Also consider action words (tasks tend to be more complex)
        action_words = ['build', 'create', 'implement', 'design', 'develop', 'refactor', 'optimize']
        has_action = any(word in message.lower() for word in action_words)
        
        if word_count < 10:
            base_complexity = 0.3  # Simple
        elif word_count < 30:
            base_complexity = 0.5  # Moderate
        elif word_count < 60:
            base_complexity = 0.7  # Complex
        else:
            base_complexity = 0.9  # Very complex
        
        # Adjust based on question/action
        if is_question:
            base_complexity *= 0.8  # Questions are simpler
        if has_action:
            base_complexity *= 1.1  # Actions are more complex
        
        return max(0.0, min(1.0, base_complexity))

