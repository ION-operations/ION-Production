"""
Intent Capture System - Step A of A-H Protocol

This module implements the Intent Capture step, which is responsible for:
- Capturing the raw intent and initial vision
- Identifying primary stakeholders and their needs
- Extracting constraints and non-negotiable requirements
- Defining success criteria
- Assessing confidence and complexity levels

Following A-H Protocol methodology from ChatGPT journal.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import re
import json
import time

class IntentType(Enum):
    """Types of intents that can be captured."""
    FEATURE_DEVELOPMENT = "feature_development"
    BUG_FIX = "bug_fix"
    SYSTEM_ENHANCEMENT = "system_enhancement"
    PROTOCOL_IMPLEMENTATION = "protocol_implementation"
    AUDIT_REVIEW = "audit_review"
    DOCUMENTATION_UPDATE = "documentation_update"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    SECURITY_HARDENING = "security_hardening"
    INTEGRATION_WORK = "integration_work"
    MAINTENANCE = "maintenance"

@dataclass
class IntentProfile:
    """Structured profile of captured intent."""
    id: str
    raw_intent: str
    intent_type: IntentType
    primary_stakeholders: List[str]
    constraints: List[str]
    success_criteria: List[str]
    non_negotiable_requirements: List[str]
    confidence_level: float
    complexity_score: float
    urgency_level: str
    estimated_effort: str
    risk_factors: List[str]
    dependencies: List[str]
    context_data: Dict[str, Any]
    timestamp: float
    version: str = "1.0"

class IntentCapture:
    """
    Intent Capture System for A-H Protocol Step A.
    
    Captures and structures raw intent from user input, providing a foundation
    for the entire A-H Protocol workflow.
    """
    
    def __init__(self, config_path: str = "intent_capture_config.json"):
        """Initialize the Intent Capture system."""
        self.config = self._load_config(config_path)
        self.intent_patterns = self._load_intent_patterns()
        self.stakeholder_patterns = self._load_stakeholder_patterns()
        self.constraint_patterns = self._load_constraint_patterns()
        self.risk_patterns = self._load_risk_patterns()
        
    def capture_intent(self, user_input: str, context: Dict[str, Any] = None) -> IntentProfile:
        """
        Capture and structure the raw intent from user input.
        
        Args:
            user_input: The raw user input expressing intent
            context: Additional context data (project info, active files, etc.)
            
        Returns:
            IntentProfile: Structured profile of the captured intent
        """
        if context is None:
            context = {}
            
        # Generate unique ID for this intent
        intent_id = f"intent_{int(time.time())}_{hash(user_input) % 10000}"
        
        # Classify intent type
        intent_type = self._classify_intent_type(user_input)
        
        # Extract stakeholders
        stakeholders = self._extract_stakeholders(user_input, context)
        
        # Identify constraints
        constraints = self._identify_constraints(user_input, context)
        
        # Define success criteria
        success_criteria = self._define_success_criteria(user_input, intent_type, context)
        
        # Extract non-negotiable requirements
        non_negotiable = self._extract_non_negotiable_requirements(user_input, context)
        
        # Calculate confidence and complexity
        confidence = self._calculate_confidence(user_input, context)
        complexity = self._calculate_complexity(user_input, context)
        
        # Assess urgency
        urgency = self._assess_urgency(user_input, context)
        
        # Estimate effort
        effort = self._estimate_effort(intent_type, complexity, context)
        
        # Identify risk factors
        risk_factors = self._identify_risk_factors(user_input, intent_type, context)
        
        # Identify dependencies
        dependencies = self._identify_dependencies(user_input, context)
        
        return IntentProfile(
            id=intent_id,
            raw_intent=user_input,
            intent_type=intent_type,
            primary_stakeholders=stakeholders,
            constraints=constraints,
            success_criteria=success_criteria,
            non_negotiable_requirements=non_negotiable,
            confidence_level=confidence,
            complexity_score=complexity,
            urgency_level=urgency,
            estimated_effort=effort,
            risk_factors=risk_factors,
            dependencies=dependencies,
            context_data=context,
            timestamp=time.time()
        )
    
    def _classify_intent_type(self, user_input: str) -> IntentType:
        """Classify the type of intent based on user input."""
        user_lower = user_input.lower()
        
        # Performance optimization patterns (check first to avoid conflicts)
        if any(pattern in user_lower for pattern in [
            "optimize performance", "performance optimization", "optimize the performance",
            "speed up", "make faster", "improve speed", "reduce latency", "increase throughput"
        ]):
            return IntentType.PERFORMANCE_OPTIMIZATION
            
        # Bug fix patterns
        if any(pattern in user_lower for pattern in [
            "fix", "bug", "error", "issue", "problem", "resolve", "correct",
            "debug", "troubleshoot", "repair"
        ]):
            return IntentType.BUG_FIX
            
        # Audit review patterns (check before security to catch "security audit")
        if any(pattern in user_lower for pattern in [
            "audit", "review", "inspect", "examine", "validate", "verify",
            "check", "assess", "evaluate", "security audit"
        ]):
            return IntentType.AUDIT_REVIEW
            
        # Security hardening patterns
        if any(pattern in user_lower for pattern in [
            "security", "secure", "harden", "vulnerability", "threat", "attack",
            "encrypt", "authentication", "authorization"
        ]):
            return IntentType.SECURITY_HARDENING
            
        # Documentation update patterns
        if any(pattern in user_lower for pattern in [
            "document", "documentation", "update docs", "write", "create docs",
            "l0", "l1", "l2", "l3", "l4", "readme", "wiki"
        ]):
            return IntentType.DOCUMENTATION_UPDATE
            
        # Protocol implementation patterns
        if any(pattern in user_lower for pattern in [
            "protocol", "standard", "compliance", "adhere", "follow", "implement protocol",
            "ah protocol", "l0-l4", "lucid", "governance"
        ]):
            return IntentType.PROTOCOL_IMPLEMENTATION
            
        # System enhancement patterns (broader patterns)
        if any(pattern in user_lower for pattern in [
            "enhance", "improve", "upgrade", "refactor", "modernize",
            "streamline", "system improvement", "optimize"
        ]):
            return IntentType.SYSTEM_ENHANCEMENT
            
        # Feature development patterns
        if any(pattern in user_lower for pattern in [
            "implement", "create", "build", "develop", "add feature", "new feature",
            "extend", "improve functionality"
        ]):
            return IntentType.FEATURE_DEVELOPMENT
            
        # Integration work patterns
        if any(pattern in user_lower for pattern in [
            "integrate", "connect", "merge", "combine", "link", "bridge",
            "integration", "connectivity"
        ]):
            return IntentType.INTEGRATION_WORK
            
        # Maintenance patterns
        if any(pattern in user_lower for pattern in [
            "maintain", "maintenance", "update", "upkeep", "support",
            "monitor", "manage"
        ]):
            return IntentType.MAINTENANCE
            
        # Default to system enhancement for unclear cases
        return IntentType.SYSTEM_ENHANCEMENT
    
    def _extract_stakeholders(self, user_input: str, context: Dict[str, Any]) -> List[str]:
        """Extract primary stakeholders from user input and context."""
        stakeholders = []
        
        # Extract from user input
        user_lower = user_input.lower()
        
        # Common stakeholder patterns
        if "user" in user_lower or "users" in user_lower:
            stakeholders.append("end_users")
        if "developer" in user_lower or "dev" in user_lower:
            stakeholders.append("developers")
        if "admin" in user_lower or "administrator" in user_lower:
            stakeholders.append("administrators")
        if "aether" in user_lower or "ai" in user_lower:
            stakeholders.append("aether_ai")
        if "braden" in user_lower or "human" in user_lower:
            stakeholders.append("human_operator")
        if "system" in user_lower:
            stakeholders.append("system")
        
        # Extract from context
        if "active_project" in context:
            stakeholders.append(f"project_{context['active_project']}")
        if "current_task_track" in context:
            stakeholders.append(f"track_{context['current_task_track']}")
        
        # Default stakeholders based on intent type
        if not stakeholders:
            stakeholders = ["aether_ai", "human_operator"]
            
        return list(set(stakeholders))  # Remove duplicates
    
    def _identify_constraints(self, user_input: str, context: Dict[str, Any]) -> List[str]:
        """Identify constraints and limitations."""
        constraints = []
        user_lower = user_input.lower()
        
        # Time constraints
        if any(pattern in user_lower for pattern in [
            "urgent", "asap", "immediately", "deadline", "by", "before", "time"
        ]):
            constraints.append("time_constraint")
            
        # Resource constraints
        if any(pattern in user_lower for pattern in [
            "budget", "cost", "expensive", "cheap", "resource", "memory", "cpu"
        ]):
            constraints.append("resource_constraint")
            
        # Technical constraints
        if any(pattern in user_lower for pattern in [
            "compatibility", "legacy", "old", "version", "platform", "os"
        ]):
            constraints.append("technical_constraint")
            
        # Security constraints
        if any(pattern in user_lower for pattern in [
            "secure", "private", "confidential", "encrypt", "permission"
        ]):
            constraints.append("security_constraint")
            
        # Performance constraints
        if any(pattern in user_lower for pattern in [
            "fast", "slow", "performance", "latency", "throughput"
        ]):
            constraints.append("performance_constraint")
            
        # Context-based constraints
        if "active_project" in context:
            constraints.append(f"project_{context['active_project']}_constraints")
            
        return constraints
    
    def _define_success_criteria(self, user_input: str, intent_type: IntentType, context: Dict[str, Any]) -> List[str]:
        """Define measurable success criteria."""
        criteria = []
        user_lower = user_input.lower()
        
        # Extract explicit success criteria
        if "success" in user_lower or "criteria" in user_lower:
            # Look for patterns like "success when", "criteria:", etc.
            success_patterns = re.findall(r'(?:success|criteria)[:\s]+([^.]+)', user_lower)
            criteria.extend(success_patterns)
        
        # Intent-type specific criteria
        if intent_type == IntentType.FEATURE_DEVELOPMENT:
            criteria.extend([
                "Feature implemented and functional",
                "Tests pass with 90%+ coverage",
                "Documentation updated (L0-L4)",
                "Performance meets requirements"
            ])
        elif intent_type == IntentType.BUG_FIX:
            criteria.extend([
                "Bug resolved and verified",
                "No regression in existing functionality",
                "Root cause identified and documented",
                "Prevention measures implemented"
            ])
        elif intent_type == IntentType.SYSTEM_ENHANCEMENT:
            criteria.extend([
                "Enhancement implemented successfully",
                "Performance improved by measurable amount",
                "System stability maintained",
                "User experience improved"
            ])
        elif intent_type == IntentType.PROTOCOL_IMPLEMENTATION:
            criteria.extend([
                "Protocol fully implemented",
                "All protocol steps followed",
                "Compliance verified",
                "Documentation complete"
            ])
        elif intent_type == IntentType.AUDIT_REVIEW:
            criteria.extend([
                "Comprehensive audit completed",
                "All issues identified and documented",
                "Recommendations provided",
                "Action plan created"
            ])
        
        # Default criteria
        if not criteria:
            criteria = [
                "Task completed successfully",
                "Quality standards met",
                "Documentation updated",
                "Tests passing"
            ]
            
        return criteria
    
    def _extract_non_negotiable_requirements(self, user_input: str, context: Dict[str, Any]) -> List[str]:
        """Extract non-negotiable requirements."""
        requirements = []
        user_lower = user_input.lower()
        
        # Extract explicit non-negotiables
        if any(pattern in user_lower for pattern in [
            "must", "required", "mandatory", "essential", "critical", "non-negotiable"
        ]):
            # Look for patterns like "must be", "required to", etc.
            requirement_patterns = re.findall(r'(?:must|required|mandatory|essential|critical)[:\s]+([^.]+)', user_lower)
            requirements.extend(requirement_patterns)
        
        # Always include LUCID compliance
        requirements.append("LUCID Development Protocol compliance")
        requirements.append("L0-L4 documentation standards")
        requirements.append("Zero hallucinations policy")
        requirements.append("Test-driven development")
        
        # Context-based requirements
        if "active_project" in context and context["active_project"] == "AIM-OS":
            requirements.append("AIM-OS architecture compliance")
            requirements.append("Aether consciousness standards")
        
        return requirements
    
    def _calculate_confidence(self, user_input: str, context: Dict[str, Any]) -> float:
        """Calculate confidence level for intent capture."""
        confidence = 0.5  # Base confidence
        
        # Length and detail of input
        word_count = len(user_input.split())
        if word_count > 50:
            confidence += 0.1
        elif word_count > 20:
            confidence += 0.05
        
        # Specificity indicators
        if any(word in user_input.lower() for word in [
            "implement", "create", "build", "fix", "optimize", "enhance"
        ]):
            confidence += 0.1
            
        # Context availability
        if context and len(context) > 0:
            confidence += 0.1
            
        # Technical terms present
        technical_terms = [
            "api", "database", "algorithm", "architecture", "protocol",
            "system", "component", "module", "function", "class"
        ]
        if any(term in user_input.lower() for term in technical_terms):
            confidence += 0.1
            
        return min(1.0, confidence)
    
    def _calculate_complexity(self, user_input: str, context: Dict[str, Any]) -> float:
        """Calculate complexity score for the intent."""
        complexity = 0.3  # Base complexity
        
        # Word count factor
        word_count = len(user_input.split())
        complexity += min(0.3, word_count / 100)
        
        # Technical complexity indicators
        technical_indicators = [
            "algorithm", "architecture", "integration", "optimization",
            "security", "performance", "scalability", "distributed"
        ]
        for indicator in technical_indicators:
            if indicator in user_input.lower():
                complexity += 0.1
                
        # Multiple systems mentioned
        system_indicators = ["system", "component", "module", "service", "api"]
        system_count = sum(1 for indicator in system_indicators if indicator in user_input.lower())
        complexity += min(0.2, system_count * 0.05)
        
        # Context complexity
        if context and "active_project" in context:
            if context["active_project"] == "AIM-OS":
                complexity += 0.1  # AIM-OS is complex
                
        return min(1.0, complexity)
    
    def _assess_urgency(self, user_input: str, context: Dict[str, Any]) -> str:
        """Assess urgency level."""
        user_lower = user_input.lower()
        
        if any(pattern in user_lower for pattern in [
            "urgent", "critical", "asap", "immediately", "emergency", "blocking"
        ]):
            return "high"
        elif any(pattern in user_lower for pattern in [
            "soon", "priority", "important", "deadline", "schedule"
        ]):
            return "medium"
        else:
            return "low"
    
    def _estimate_effort(self, intent_type: IntentType, complexity: float, context: Dict[str, Any]) -> str:
        """Estimate effort required."""
        base_effort = {
            IntentType.BUG_FIX: 0.3,
            IntentType.DOCUMENTATION_UPDATE: 0.2,
            IntentType.MAINTENANCE: 0.2,
            IntentType.PERFORMANCE_OPTIMIZATION: 0.6,
            IntentType.SECURITY_HARDENING: 0.7,
            IntentType.FEATURE_DEVELOPMENT: 0.8,
            IntentType.SYSTEM_ENHANCEMENT: 0.8,
            IntentType.INTEGRATION_WORK: 0.9,
            IntentType.PROTOCOL_IMPLEMENTATION: 1.0,
            IntentType.AUDIT_REVIEW: 0.7
        }
        
        effort_score = base_effort.get(intent_type, 0.5) + complexity
        
        if effort_score < 0.4:
            return "low"
        elif effort_score < 0.7:
            return "medium"
        elif effort_score < 1.0:
            return "high"
        else:
            return "very_high"
    
    def _identify_risk_factors(self, user_input: str, intent_type: IntentType, context: Dict[str, Any]) -> List[str]:
        """Identify potential risk factors."""
        risks = []
        user_lower = user_input.lower()
        
        # Technical risks
        if any(pattern in user_lower for pattern in [
            "complex", "difficult", "challenging", "untested", "experimental"
        ]):
            risks.append("technical_complexity")
            
        # Time risks
        if any(pattern in user_lower for pattern in [
            "urgent", "deadline", "time", "quick", "fast"
        ]):
            risks.append("time_pressure")
            
        # Integration risks
        if any(pattern in user_lower for pattern in [
            "integrate", "connect", "api", "external", "third-party"
        ]):
            risks.append("integration_complexity")
            
        # Data risks
        if any(pattern in user_lower for pattern in [
            "data", "database", "migration", "backup", "restore"
        ]):
            risks.append("data_integrity")
            
        # Security risks
        if any(pattern in user_lower for pattern in [
            "security", "secure", "vulnerability", "attack", "hack"
        ]):
            risks.append("security_impact")
            
        # Performance risks
        if any(pattern in user_lower for pattern in [
            "performance", "slow", "optimize", "scalability"
        ]):
            risks.append("performance_impact")
            
        return risks
    
    def _identify_dependencies(self, user_input: str, context: Dict[str, Any]) -> List[str]:
        """Identify dependencies for the intent."""
        dependencies = []
        user_lower = user_input.lower()
        
        # Extract explicit dependencies
        if "depend" in user_lower or "require" in user_lower:
            dep_patterns = re.findall(r'(?:depend|require)[:\s]+([^.]+)', user_lower)
            dependencies.extend(dep_patterns)
            
        # Context-based dependencies
        if "active_project" in context:
            dependencies.append(f"project_{context['active_project']}_infrastructure")
            
        if "current_task_track" in context:
            dependencies.append(f"track_{context['current_task_track']}_completion")
            
        # Always include LUCID dependencies
        dependencies.extend([
            "LUCID Development Protocol",
            "L0-L4 documentation standards",
            "Aether consciousness framework"
        ])
        
        return dependencies
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "default_confidence_threshold": 0.7,
                "default_complexity_threshold": 0.5,
                "max_stakeholders": 10,
                "max_constraints": 20
            }
    
    def _load_intent_patterns(self) -> Dict[str, List[str]]:
        """Load intent classification patterns."""
        return {
            "feature_development": [
                "implement", "create", "build", "develop", "add feature", "new feature"
            ],
            "bug_fix": [
                "fix", "bug", "error", "issue", "problem", "resolve", "correct"
            ],
            "system_enhancement": [
                "optimize", "enhance", "improve", "upgrade", "refactor", "modernize"
            ],
            "protocol_implementation": [
                "protocol", "standard", "compliance", "adhere", "follow"
            ],
            "audit_review": [
                "audit", "review", "inspect", "examine", "validate", "verify"
            ]
        }
    
    def _load_stakeholder_patterns(self) -> Dict[str, List[str]]:
        """Load stakeholder identification patterns."""
        return {
            "end_users": ["user", "users", "customer", "client"],
            "developers": ["developer", "dev", "programmer", "coder"],
            "administrators": ["admin", "administrator", "ops", "operations"],
            "aether_ai": ["aether", "ai", "artificial intelligence"],
            "human_operator": ["braden", "human", "operator", "user"]
        }
    
    def _load_constraint_patterns(self) -> Dict[str, List[str]]:
        """Load constraint identification patterns."""
        return {
            "time_constraint": ["urgent", "asap", "immediately", "deadline"],
            "resource_constraint": ["budget", "cost", "expensive", "cheap"],
            "technical_constraint": ["compatibility", "legacy", "old", "version"],
            "security_constraint": ["secure", "private", "confidential", "encrypt"]
        }
    
    def _load_risk_patterns(self) -> Dict[str, List[str]]:
        """Load risk identification patterns."""
        return {
            "technical_complexity": ["complex", "difficult", "challenging"],
            "time_pressure": ["urgent", "deadline", "time", "quick"],
            "integration_complexity": ["integrate", "connect", "api", "external"],
            "data_integrity": ["data", "database", "migration", "backup"]
        }

# Example usage and testing
if __name__ == "__main__":
    # Test the Intent Capture system
    intent_capture = IntentCapture()
    
    # Test case 1: Feature development
    test_input_1 = "I need to implement the new A-H Protocol workflow in the daemon/RAG system. This is critical for our AI consciousness development."
    context_1 = {
        "active_project": "AIM-OS",
        "current_task_track": "AH_PROTOCOL_IMPLEMENTATION",
        "open_files": ["daemon_rag_system/daemon_rag_system.py"]
    }
    
    profile_1 = intent_capture.capture_intent(test_input_1, context_1)
    print("Test Case 1 - Feature Development:")
    print(f"Intent Type: {profile_1.intent_type}")
    print(f"Stakeholders: {profile_1.primary_stakeholders}")
    print(f"Constraints: {profile_1.constraints}")
    print(f"Success Criteria: {profile_1.success_criteria}")
    print(f"Confidence: {profile_1.confidence_level:.2f}")
    print(f"Complexity: {profile_1.complexity_score:.2f}")
    print(f"Urgency: {profile_1.urgency_level}")
    print(f"Effort: {profile_1.estimated_effort}")
    print()
    
    # Test case 2: Bug fix
    test_input_2 = "Fix the memory leak in the RAG system that's causing performance issues."
    context_2 = {
        "active_project": "AIM-OS",
        "current_task_track": "BUG_FIX"
    }
    
    profile_2 = intent_capture.capture_intent(test_input_2, context_2)
    print("Test Case 2 - Bug Fix:")
    print(f"Intent Type: {profile_2.intent_type}")
    print(f"Stakeholders: {profile_2.primary_stakeholders}")
    print(f"Risk Factors: {profile_2.risk_factors}")
    print(f"Confidence: {profile_2.confidence_level:.2f}")
    print(f"Complexity: {profile_2.complexity_score:.2f}")
    print()
    
    # Test case 3: Audit review
    test_input_3 = "Conduct a comprehensive audit of the daemon/RAG system's adherence to A-H Protocol standards."
    context_3 = {
        "active_project": "AIM-OS",
        "current_task_track": "SYSTEM_AUDIT"
    }
    
    profile_3 = intent_capture.capture_intent(test_input_3, context_3)
    print("Test Case 3 - Audit Review:")
    print(f"Intent Type: {profile_3.intent_type}")
    print(f"Stakeholders: {profile_3.primary_stakeholders}")
    print(f"Success Criteria: {profile_3.success_criteria}")
    print(f"Confidence: {profile_3.confidence_level:.2f}")
    print(f"Complexity: {profile_3.complexity_score:.2f}")
    print()
    
    print("Intent Capture System test completed successfully!")
