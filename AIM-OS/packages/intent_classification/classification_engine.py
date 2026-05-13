"""
Classification Engine

Core classification logic that transforms raw user input into structured MissionIntent objects.
Implements multi-axis classification with confidence scoring and facet generation.
"""

from __future__ import annotations
import re
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass
import logging

from .mission_intent import (
    MissionIntent, PrimaryCategory, LifecycleStage, ScopeLevel, 
    ClarityState, MissionStatus
)

logger = logging.getLogger(__name__)


@dataclass
class ClassificationResult:
    """Result of intent classification process."""
    
    mission_intent: MissionIntent
    classification_confidence: float
    processing_time_ms: float
    warnings: List[str]
    errors: List[str]


class ClassificationEngine:
    """
    Core classification engine for intent classification.
    
    Transforms raw user input into structured MissionIntent objects using
    multi-axis classification with confidence scoring and facet generation.
    """
    
    def __init__(self):
        """Initialize the classification engine."""
        self._category_patterns = self._build_category_patterns()
        self._lifecycle_patterns = self._build_lifecycle_patterns()
        self._scope_patterns = self._build_scope_patterns()
        self._clarity_patterns = self._build_clarity_patterns()
        self._facet_keywords = self._build_facet_keywords()
        
        # Classification weights for confidence calculation
        self._weights = {
            'category': 0.3,
            'lifecycle': 0.25,
            'scope': 0.2,
            'clarity': 0.15,
            'facets': 0.1
        }
    
    def classify_intent(self, raw_intent: str, context: Optional[Dict[str, Any]] = None) -> ClassificationResult:
        """
        Classify raw user intent into structured MissionIntent.
        
        Args:
            raw_intent: Raw user input to classify
            context: Optional context information for classification
            
        Returns:
            ClassificationResult with classified mission intent
        """
        import time
        start_time = time.time()
        
        warnings = []
        errors = []
        
        try:
            # Normalize input
            normalized_intent = self._normalize_intent(raw_intent)
            
            # Classify each axis
            category_result = self._classify_category(normalized_intent, context)
            lifecycle_result = self._classify_lifecycle(normalized_intent, context)
            scope_result = self._classify_scope(normalized_intent, context)
            clarity_result = self._classify_clarity(normalized_intent, context)
            facets_result = self._generate_facets(normalized_intent, context)
            
            # Calculate overall confidence
            confidence = self._calculate_confidence([
                category_result, lifecycle_result, scope_result, clarity_result, facets_result
            ])
            
            # Calculate complexity score
            complexity = self._calculate_complexity(normalized_intent, category_result, scope_result)
            
            # Generate behavior controls
            allowed_actions, blocked_actions = self._generate_behavior_controls(
                category_result, lifecycle_result, scope_result, clarity_result, confidence
            )
            
            # Generate risk assessment
            risk_level, stop_conditions, blast_radius = self._assess_risk(
                category_result, lifecycle_result, scope_result, clarity_result, complexity, confidence
            )
            
            # Create mission intent
            mission_intent = MissionIntent(
                raw_intent=raw_intent,
                primary_category=category_result['category'],
                lifecycle_stage=lifecycle_result['stage'],
                scope_level=scope_result['level'],
                clarity_state=clarity_result['state'],
                facets=facets_result['facets'],
                confidence_level=confidence,
                complexity_score=complexity,
                allowed_actions=allowed_actions,
                blocked_actions=blocked_actions,
                risk_level=risk_level,
                stop_conditions=stop_conditions,
                blast_radius=blast_radius
            )
            
            # Check for escalation requirements
            if mission_intent.requires_escalation():
                mission_intent.escalation_required = True
                mission_intent.escalation_reason = mission_intent.get_escalation_reason()
                warnings.append(f"Mission requires escalation: {mission_intent.escalation_reason}")
            
            processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            return ClassificationResult(
                mission_intent=mission_intent,
                classification_confidence=confidence,
                processing_time_ms=processing_time,
                warnings=warnings,
                errors=errors
            )
            
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            errors.append(f"Classification failed: {str(e)}")
            
            # Return minimal mission intent on error
            mission_intent = MissionIntent(
                raw_intent=raw_intent,
                primary_category=PrimaryCategory.INVESTIGATION,
                lifecycle_stage=LifecycleStage.IDEATION,
                scope_level=ScopeLevel.LOCAL_FUNCTION,
                clarity_state=ClarityState.EXPLORATORY,
                confidence_level=0.0
            )
            
            processing_time = (time.time() - start_time) * 1000
            
            return ClassificationResult(
                mission_intent=mission_intent,
                classification_confidence=0.0,
                processing_time_ms=processing_time,
                warnings=warnings,
                errors=errors
            )
    
    def _normalize_intent(self, intent: str) -> str:
        """Normalize user intent for classification."""
        # Convert to lowercase
        normalized = intent.lower().strip()
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Remove common filler words that don't affect classification
        filler_words = ['please', 'can you', 'could you', 'would you', 'i need', 'i want']
        for word in filler_words:
            normalized = normalized.replace(word, '')
        
        return normalized.strip()
    
    def _classify_category(self, intent: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Classify primary category."""
        best_category = PrimaryCategory.INVESTIGATION
        best_score = 0.0
        
        for category, patterns in self._category_patterns.items():
            score = self._calculate_pattern_score(intent, patterns)
            if score > best_score:
                best_score = score
                best_category = category
        
        return {
            'category': best_category,
            'confidence': best_score,
            'patterns_matched': self._get_matched_patterns(intent, self._category_patterns[best_category])
        }
    
    def _classify_lifecycle(self, intent: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Classify lifecycle stage."""
        best_stage = LifecycleStage.IDEATION
        best_score = 0.0
        
        for stage, patterns in self._lifecycle_patterns.items():
            score = self._calculate_pattern_score(intent, patterns)
            if score > best_score:
                best_score = score
                best_stage = stage
        
        return {
            'stage': best_stage,
            'confidence': best_score,
            'patterns_matched': self._get_matched_patterns(intent, self._lifecycle_patterns[best_stage])
        }
    
    def _classify_scope(self, intent: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Classify scope level."""
        best_level = ScopeLevel.LOCAL_FUNCTION
        best_score = 0.0
        
        for level, patterns in self._scope_patterns.items():
            score = self._calculate_pattern_score(intent, patterns)
            if score > best_score:
                best_score = score
                best_level = level
        
        return {
            'level': best_level,
            'confidence': best_score,
            'patterns_matched': self._get_matched_patterns(intent, self._scope_patterns[best_level])
        }
    
    def _classify_clarity(self, intent: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Classify clarity state."""
        best_state = ClarityState.EXPLORATORY
        best_score = 0.0
        
        for state, patterns in self._clarity_patterns.items():
            score = self._calculate_pattern_score(intent, patterns)
            if score > best_score:
                best_score = score
                best_state = state
        
        return {
            'state': best_state,
            'confidence': best_score,
            'patterns_matched': self._get_matched_patterns(intent, self._clarity_patterns[best_state])
        }
    
    def _generate_facets(self, intent: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate contextual facets for the mission."""
        facets = []
        
        for category, keywords in self._facet_keywords.items():
            for keyword in keywords:
                if keyword.lower() in intent.lower():
                    facets.append(category)
                    break
        
        return {
            'facets': facets,
            'confidence': len(facets) / len(self._facet_keywords) if self._facet_keywords else 0.0
        }
    
    def _calculate_pattern_score(self, intent: str, patterns: List[str]) -> float:
        """Calculate pattern matching score for intent."""
        if not patterns:
            return 0.0
        
        matches = 0
        for pattern in patterns:
            if re.search(pattern, intent, re.IGNORECASE):
                matches += 1
        
        return matches / len(patterns)
    
    def _get_matched_patterns(self, intent: str, patterns: List[str]) -> List[str]:
        """Get list of patterns that matched the intent."""
        matched = []
        for pattern in patterns:
            if re.search(pattern, intent, re.IGNORECASE):
                matched.append(pattern)
        return matched
    
    def _calculate_confidence(self, results: List[Dict[str, Any]]) -> float:
        """Calculate overall classification confidence."""
        total_confidence = 0.0
        total_weight = 0.0
        
        for i, result in enumerate(results):
            weight_key = ['category', 'lifecycle', 'scope', 'clarity', 'facets'][i]
            weight = self._weights[weight_key]
            confidence = result.get('confidence', 0.0)
            
            total_confidence += confidence * weight
            total_weight += weight
        
        return total_confidence / total_weight if total_weight > 0 else 0.0
    
    def _calculate_complexity(self, intent: str, category_result: Dict, scope_result: Dict) -> float:
        """Calculate mission complexity score."""
        complexity = 0.0
        
        # Base complexity from category
        category_complexity = {
            PrimaryCategory.NEW_SYSTEM_DESIGN: 0.9,
            PrimaryCategory.EXISTING_SYSTEM_ENHANCEMENT: 0.7,
            PrimaryCategory.BUG_FIX: 0.3,
            PrimaryCategory.PERFORMANCE_OPTIMIZATION: 0.6,
            PrimaryCategory.REFACTORING: 0.8,
            PrimaryCategory.TESTING: 0.4,
            PrimaryCategory.DOCUMENTATION: 0.2,
            PrimaryCategory.RESEARCH_PROBE: 0.5,
            PrimaryCategory.ANALYSIS: 0.4,
            PrimaryCategory.INTEGRATION: 0.7,
            PrimaryCategory.DEPLOYMENT: 0.6,
            PrimaryCategory.MAINTENANCE: 0.3,
            PrimaryCategory.INVESTIGATION: 0.5
        }
        complexity += category_complexity.get(category_result['category'], 0.5) * 0.4
        
        # Scope complexity
        scope_complexity = {
            ScopeLevel.LOCAL_FUNCTION: 0.2,
            ScopeLevel.SINGLE_MODULE: 0.4,
            ScopeLevel.MULTI_SERVICE: 0.7,
            ScopeLevel.WHOLE_PLATFORM: 0.9
        }
        complexity += scope_complexity.get(scope_result['level'], 0.5) * 0.3
        
        # Intent length complexity
        intent_length = len(intent.split())
        if intent_length > 50:
            complexity += 0.2
        elif intent_length > 20:
            complexity += 0.1
        
        # Keyword complexity indicators
        complex_keywords = ['complex', 'difficult', 'challenging', 'sophisticated', 'advanced']
        for keyword in complex_keywords:
            if keyword in intent.lower():
                complexity += 0.1
                break
        
        return min(complexity, 1.0)
    
    def _generate_behavior_controls(self, category_result: Dict, lifecycle_result: Dict, 
                                  scope_result: Dict, clarity_result: Dict, confidence: float) -> Tuple[Set[str], Set[str]]:
        """Generate allowed and blocked actions based on classification."""
        allowed_actions = set()
        blocked_actions = set()
        
        # Base actions based on lifecycle stage
        if lifecycle_result['stage'] == LifecycleStage.IDEATION:
            allowed_actions.update(['research', 'analyze', 'explore', 'investigate'])
            blocked_actions.update(['implement', 'deploy', 'modify_code'])
        elif lifecycle_result['stage'] == LifecycleStage.ARCHITECTURE:
            allowed_actions.update(['design', 'plan', 'document', 'analyze'])
            blocked_actions.update(['deploy', 'modify_code'])
        elif lifecycle_result['stage'] == LifecycleStage.IMPLEMENTATION:
            allowed_actions.update(['implement', 'code', 'test', 'modify_code'])
        elif lifecycle_result['stage'] == LifecycleStage.INTEGRATION:
            allowed_actions.update(['integrate', 'test', 'deploy'])
        elif lifecycle_result['stage'] == LifecycleStage.HARDENING:
            allowed_actions.update(['test', 'optimize', 'secure'])
        elif lifecycle_result['stage'] == LifecycleStage.STABILIZATION:
            allowed_actions.update(['monitor', 'maintain', 'document'])
        
        # Scope-based restrictions
        if scope_result['level'] == ScopeLevel.WHOLE_PLATFORM:
            blocked_actions.update(['modify_code', 'implement', 'deploy'])
            allowed_actions.add('escalate')
        
        # Clarity-based restrictions
        if clarity_result['state'] == ClarityState.EXPLORATORY:
            blocked_actions.update(['implement', 'deploy', 'modify_code'])
            allowed_actions.update(['research', 'explore', 'investigate'])
        
        # Confidence-based restrictions
        if confidence < 0.3:
            blocked_actions.update(['implement', 'deploy', 'modify_code'])
            allowed_actions.add('escalate')
        
        return allowed_actions, blocked_actions
    
    def _assess_risk(self, category_result: Dict, lifecycle_result: Dict, 
                    scope_result: Dict, clarity_result: Dict, complexity: float, confidence: float) -> Tuple[str, List[str], str]:
        """Assess mission risk level and generate stop conditions."""
        risk_factors = []
        
        # High complexity
        if complexity > 0.8:
            risk_factors.append("high_complexity")
        
        # Low confidence
        if confidence < 0.3:
            risk_factors.append("low_confidence")
        
        # Platform-wide scope
        if scope_result['level'] == ScopeLevel.WHOLE_PLATFORM:
            risk_factors.append("platform_scope")
        
        # Implementation with low clarity
        if (lifecycle_result['stage'] in [LifecycleStage.IMPLEMENTATION, LifecycleStage.INTEGRATION] 
            and clarity_result['state'] == ClarityState.EXPLORATORY):
            risk_factors.append("implementation_without_clarity")
        
        # Determine risk level
        if len(risk_factors) >= 3:
            risk_level = "critical"
        elif len(risk_factors) >= 2:
            risk_level = "high"
        elif len(risk_factors) >= 1:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        # Generate stop conditions
        stop_conditions = []
        if "high_complexity" in risk_factors:
            stop_conditions.append("complexity_score > 0.8")
        if "low_confidence" in risk_factors:
            stop_conditions.append("confidence_level < 0.3")
        if "platform_scope" in risk_factors:
            stop_conditions.append("scope_level = whole_platform")
        if "implementation_without_clarity" in risk_factors:
            stop_conditions.append("clarity_state = exploratory + implementation_stage")
        
        # Determine blast radius
        if scope_result['level'] == ScopeLevel.WHOLE_PLATFORM:
            blast_radius = "platform"
        elif scope_result['level'] == ScopeLevel.MULTI_SERVICE:
            blast_radius = "service"
        elif scope_result['level'] == ScopeLevel.SINGLE_MODULE:
            blast_radius = "module"
        else:
            blast_radius = "local"
        
        return risk_level, stop_conditions, blast_radius
    
    def _build_category_patterns(self) -> Dict[PrimaryCategory, List[str]]:
        """Build pattern matching rules for primary categories."""
        return {
            PrimaryCategory.NEW_SYSTEM_DESIGN: [
                r'\b(?:create|build|design|develop|new)\s+(?:system|application|app|service|platform)',
                r'\b(?:from\s+)?scratch',
                r'\b(?:greenfield|new\s+project)'
            ],
            PrimaryCategory.EXISTING_SYSTEM_ENHANCEMENT: [
                r'\b(?:enhance|improve|upgrade|extend|add\s+to)\s+(?:existing|current)',
                r'\b(?:modify|update|refactor)\s+(?:system|application|app|service)',
                r'\b(?:new\s+feature|additional\s+functionality)'
            ],
            PrimaryCategory.BUG_FIX: [
                r'\b(?:fix|debug|resolve|correct)\s+(?:bug|issue|problem|error)',
                r'\b(?:broken|not\s+working|failing)',
                r'\b(?:troubleshoot|diagnose)'
            ],
            PrimaryCategory.PERFORMANCE_OPTIMIZATION: [
                r'\b(?:optimize|improve|speed\s+up|make\s+faster)',
                r'\b(?:performance|efficiency|speed|memory)',
                r'\b(?:bottleneck|slow|laggy)'
            ],
            PrimaryCategory.REFACTORING: [
                r'\b(?:refactor|restructure|reorganize|clean\s+up)',
                r'\b(?:code\s+quality|technical\s+debt)',
                r'\b(?:modernize|update\s+code)'
            ],
            PrimaryCategory.TESTING: [
                r'\b(?:test|testing|unit\s+test|integration\s+test)',
                r'\b(?:coverage|quality\s+assurance|qa)',
                r'\b(?:validate|verify|check)'
            ],
            PrimaryCategory.DOCUMENTATION: [
                r'\b(?:document|documentation|docs|readme)',
                r'\b(?:explain|describe|write\s+about)',
                r'\b(?:guide|tutorial|manual)'
            ],
            PrimaryCategory.RESEARCH_PROBE: [
                r'\b(?:research|investigate|explore|analyze)',
                r'\b(?:find\s+out|discover|learn\s+about)',
                r'\b(?:study|examine|probe)'
            ],
            PrimaryCategory.ANALYSIS: [
                r'\b(?:analyze|analysis|examine|review)',
                r'\b(?:understand|comprehend|figure\s+out)',
                r'\b(?:assess|evaluate|measure)'
            ],
            PrimaryCategory.INTEGRATION: [
                r'\b(?:integrate|connect|combine|merge)',
                r'\b(?:api|interface|connection)',
                r'\b(?:work\s+together|compatibility)'
            ],
            PrimaryCategory.DEPLOYMENT: [
                r'\b(?:deploy|deployment|release|publish)',
                r'\b(?:production|live|go\s+live)',
                r'\b(?:rollout|launch)'
            ],
            PrimaryCategory.MAINTENANCE: [
                r'\b(?:maintain|maintenance|support|upkeep)',
                r'\b(?:keep\s+up|ongoing|regular)',
                r'\b(?:monitor|watch|observe)'
            ],
            PrimaryCategory.INVESTIGATION: [
                r'\b(?:investigate|investigation|look\s+into)',
                r'\b(?:find\s+out|discover|determine)',
                r'\b(?:what\s+is|what\s+happened|why)'
            ]
        }
    
    def _build_lifecycle_patterns(self) -> Dict[LifecycleStage, List[str]]:
        """Build pattern matching rules for lifecycle stages."""
        return {
            LifecycleStage.IDEATION: [
                r'\b(?:idea|concept|brainstorm|think\s+about)',
                r'\b(?:explore|investigate|research)',
                r'\b(?:what\s+if|consider|imagine)'
            ],
            LifecycleStage.ARCHITECTURE: [
                r'\b(?:design|architecture|plan|structure)',
                r'\b(?:blueprint|framework|outline)',
                r'\b(?:how\s+to\s+build|approach|strategy)'
            ],
            LifecycleStage.IMPLEMENTATION: [
                r'\b(?:implement|build|code|develop)',
                r'\b(?:create|make|construct)',
                r'\b(?:write\s+code|programming|coding)'
            ],
            LifecycleStage.INTEGRATION: [
                r'\b(?:integrate|connect|combine|merge)',
                r'\b(?:work\s+together|compatibility)',
                r'\b(?:api|interface|connection)'
            ],
            LifecycleStage.HARDENING: [
                r'\b(?:harden|secure|optimize|tune)',
                r'\b(?:performance|security|reliability)',
                r'\b(?:production\s+ready|robust)'
            ],
            LifecycleStage.STABILIZATION: [
                r'\b(?:stabilize|maintain|support)',
                r'\b(?:monitor|watch|observe)',
                r'\b(?:keep\s+running|operational)'
            ],
            LifecycleStage.DEPRECATION: [
                r'\b(?:deprecate|retire|remove|phase\s+out)',
                r'\b(?:end\s+of\s+life|obsolete|legacy)',
                r'\b(?:sunset|discontinue)'
            ]
        }
    
    def _build_scope_patterns(self) -> Dict[ScopeLevel, List[str]]:
        """Build pattern matching rules for scope levels."""
        return {
            ScopeLevel.LOCAL_FUNCTION: [
                r'\b(?:function|method|procedure|routine)',
                r'\b(?:single\s+function|one\s+function)',
                r'\b(?:local\s+change|small\s+change)'
            ],
            ScopeLevel.SINGLE_MODULE: [
                r'\b(?:module|component|class|file)',
                r'\b(?:single\s+module|one\s+module)',
                r'\b(?:component\s+level|module\s+level)'
            ],
            ScopeLevel.MULTI_SERVICE: [
                r'\b(?:service|services|multiple\s+services)',
                r'\b(?:microservice|distributed)',
                r'\b(?:cross\s+service|between\s+services)'
            ],
            ScopeLevel.WHOLE_PLATFORM: [
                r'\b(?:platform|entire\s+system|whole\s+system)',
                r'\b(?:global|system\s+wide|across\s+everything)',
                r'\b(?:architecture|infrastructure)'
            ]
        }
    
    def _build_clarity_patterns(self) -> Dict[ClarityState, List[str]]:
        """Build pattern matching rules for clarity states."""
        return {
            ClarityState.EXPLORATORY: [
                r'\b(?:explore|investigate|find\s+out|discover)',
                r'\b(?:what\s+is|what\s+happens|how\s+does)',
                r'\b(?:unclear|unknown|not\s+sure)',
                r'\b(?:figure\s+out|understand|learn)'
            ],
            ClarityState.PARTIALLY_DEFINED: [
                r'\b(?:partially|somewhat|kind\s+of)',
                r'\b(?:maybe|possibly|might)',
                r'\b(?:rough\s+idea|general\s+concept)',
                r'\b(?:working\s+on|in\s+progress)'
            ],
            ClarityState.FULLY_DEFINED: [
                r'\b(?:exactly|precisely|specifically)',
                r'\b(?:clear|defined|specified)',
                r'\b(?:detailed|comprehensive|complete)',
                r'\b(?:know\s+exactly|certain|sure)'
            ]
        }
    
    def _build_facet_keywords(self) -> Dict[str, List[str]]:
        """Build keyword mappings for facet generation."""
        return {
            'frontend': ['ui', 'user interface', 'frontend', 'react', 'vue', 'angular', 'html', 'css', 'javascript'],
            'backend': ['backend', 'api', 'server', 'database', 'service', 'microservice'],
            'database': ['database', 'db', 'sql', 'nosql', 'mongodb', 'postgresql', 'mysql'],
            'testing': ['test', 'testing', 'unit test', 'integration test', 'coverage'],
            'deployment': ['deploy', 'deployment', 'production', 'staging', 'ci/cd', 'docker'],
            'security': ['security', 'auth', 'authentication', 'authorization', 'encryption'],
            'performance': ['performance', 'optimization', 'speed', 'memory', 'cpu'],
            'documentation': ['documentation', 'docs', 'readme', 'guide', 'tutorial'],
            'integration': ['integration', 'api', 'webhook', 'sdk', 'library'],
            'monitoring': ['monitoring', 'logging', 'metrics', 'alerting', 'observability']
        }
