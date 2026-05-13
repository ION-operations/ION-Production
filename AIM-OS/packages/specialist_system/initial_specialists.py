"""
Initial Specialist Registration

Registers the initial set of specialists (UI Specialist, Lex, Codex, Solo).

NL_TAG: SPECIALIST-REGISTRY-004 | Register initial specialists | registerInitialSpecialists | [SPECIALIST-REGISTRY-001]
"""

from .specialist_registry import SpecialistRegistry, Specialist


def register_initial_specialists(registry: SpecialistRegistry) -> None:
    """
    Register initial specialists in the registry.
    
    Args:
        registry: Specialist registry to register specialists in
    """
    # UI Specialist
    ui_specialist = Specialist(
        id='ui-specialist',
        name='UI Specialist',
        domain=['UI', 'UX', 'Design', 'Frontend', 'Components'],
        description='Universal UI/UX specialist - works on any UI project (web, mobile, desktop). Expert in design systems, components, accessibility, and user experience.',
        connections={
            'systems': ['React', 'Vue', 'Angular', 'Svelte', 'Tailwind', 'Design Systems', 'Figma', 'Sketch'],
            'data': ['design-tokens', 'component-libraries', 'ux-patterns', 'accessibility-standards'],
            'patterns': ['component-patterns', 'layout-patterns', 'interaction-patterns', 'responsive-design']
        },
        relevance_factors={
            'domain_match': 0.40,
            'data_connections': 0.25,
            'system_connections': 0.20,
            'pattern_recognition': 0.10,
            'complexity': 0.05
        },
        activation_thresholds={
            'ownership': 0.90,
            'activation': 0.70,
            'consultation': 0.60
        }
    )
    registry.register(ui_specialist)
    
    # Lex (Lexicon)
    lex_specialist = Specialist(
        id='lex',
        name='Lex',
        domain=['Language', 'Lexicon', 'Grammar', 'Translation'],
        description='Language definition specialist - defines and manages lexicons for special languages (PLIx, Smalltalk-like, etc.). Expert in language design, grammar, and translation.',
        connections={
            'systems': ['PLIx', 'Smalltalk-like', 'Language Compilers', 'Translation Systems'],
            'data': ['language-specs', 'lexicon-definitions', 'grammar-rules', 'translation-rules'],
            'patterns': ['lexicon-patterns', 'language-patterns', 'translation-patterns', 'grammar-patterns']
        },
        relevance_factors={
            'domain_match': 0.40,
            'data_connections': 0.25,
            'system_connections': 0.20,
            'pattern_recognition': 0.10,
            'complexity': 0.05
        },
        activation_thresholds={
            'ownership': 0.90,
            'activation': 0.70,
            'consultation': 0.60
        }
    )
    registry.register(lex_specialist)
    
    # Codex (Chat)
    codex_specialist = Specialist(
        id='codex',
        name='Codex',
        domain=['Chat', 'Conversation', 'Communication'],
        description='Chat and conversation specialist - designs and builds chat interfaces. Expert in conversation patterns, message threading, and real-time communication.',
        connections={
            'systems': ['Chat Systems', 'Conversation Patterns', 'AI Chat', 'Message Threading'],
            'data': ['chat-patterns', 'conversation-patterns', 'message-patterns', 'threading-patterns'],
            'patterns': ['chat-patterns', 'conversation-patterns', 'message-patterns', 'real-time-patterns']
        },
        relevance_factors={
            'domain_match': 0.40,
            'data_connections': 0.25,
            'system_connections': 0.20,
            'pattern_recognition': 0.10,
            'complexity': 0.05
        },
        activation_thresholds={
            'ownership': 0.90,
            'activation': 0.70,
            'consultation': 0.60
        }
    )
    registry.register(codex_specialist)
    
    # Solo (Integration)
    solo_specialist = Specialist(
        id='solo',
        name='Solo',
        domain=['Backend Integration', 'APIs'],
        description='Backend integration specialist - connects UI to any backend (REST, GraphQL, WebSocket, AIM-OS APIs). Expert in API design, integration patterns, and real-time updates.',
        connections={
            'systems': ['REST', 'GraphQL', 'WebSocket', 'AIM-OS APIs', 'HTTP', 'gRPC'],
            'data': ['api-specs', 'integration-patterns', 'backend-patterns', 'real-time-patterns'],
            'patterns': ['api-patterns', 'integration-patterns', 'backend-patterns', 'real-time-patterns']
        },
        relevance_factors={
            'domain_match': 0.40,
            'data_connections': 0.25,
            'system_connections': 0.20,
            'pattern_recognition': 0.10,
            'complexity': 0.05
        },
        activation_thresholds={
            'ownership': 0.90,
            'activation': 0.70,
            'consultation': 0.60
        }
    )
    registry.register(solo_specialist)
    
    # Math Specialist
    math_specialist = Specialist(
        id='math-specialist',
        name='Math Specialist',
        domain=['Mathematics', 'Computation', 'Statistics', 'Data Analysis', 'Scientific Computing'],
        description='Mathematics and computational specialist - expert in mathematical modeling, data analysis, visualization, and scientific computing. Works with numerical computation, symbolic math, statistics, and data visualization.',
        connections={
            'systems': ['NumPy', 'SciPy', 'Matplotlib', 'SymPy', 'Pandas', 'Jupyter', 'LaTeX', 'Wolfram', 'MATLAB'],
            'data': ['mathematical-models', 'datasets', 'statistical-data', 'numerical-results', 'formulas', 'equations'],
            'patterns': ['mathematical-patterns', 'computational-patterns', 'visualization-patterns', 'analysis-patterns', 'modeling-patterns']
        },
        relevance_factors={
            'domain_match': 0.40,
            'data_connections': 0.25,
            'system_connections': 0.20,
            'pattern_recognition': 0.10,
            'complexity': 0.05
        },
        activation_thresholds={
            'ownership': 0.90,
            'activation': 0.70,
            'consultation': 0.60
        }
    )
    registry.register(math_specialist)


def get_initial_specialists() -> list[Specialist]:
    """
    Get list of initial specialists (without registering).
    
    Returns:
        List of initial specialists
    """
    registry = SpecialistRegistry()
    register_initial_specialists(registry)
    return registry.get_all()

