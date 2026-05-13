"""CAS Integration for APOE

Enables cognitive analysis and introspection for APOE operations:
- Safety gates: Introspection for safety decisions
- Policy gates: Introspection for policy decisions
- Planner role: Decision analysis for planning
- Critic role: Introspection for critique decisions
- Operator role: Decision analysis for operations
- Budget pooler: Resource pattern analysis
"""

from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import logging

from .models import Step, StepStatus, Budget
from .executor import ExecutionResult
from .acl_parser import ExecutionPlan

logger = logging.getLogger(__name__)

# CAS imports (optional)
try:
    from packages.cas.introspection import IntrospectionProtocol, IntrospectionResult, IntrospectionType
    from packages.cas.failure_modes import FailureModeAnalyzer, FailureMode, analyze_failure_pattern
    from packages.cas.activation import ActivationTracker, ActivationState
    from packages.cas.category import CategoryRecognizer, TaskCategory, CategoryResult
    from packages.cas.attention import AttentionMonitor, AttentionMetrics
    CAS_AVAILABLE = True
except ImportError:
    # Fallback for environments without CAS
    CAS_AVAILABLE = False
    IntrospectionProtocol = None
    IntrospectionResult = None
    IntrospectionType = None
    FailureModeAnalyzer = None
    FailureMode = None
    analyze_failure_pattern = None
    ActivationTracker = None
    ActivationState = None
    CategoryRecognizer = None
    TaskCategory = None
    CategoryResult = None
    AttentionMonitor = None
    AttentionMetrics = None


class _Value:
    """Minimal enum-like value wrapper for fallback components."""

    def __init__(self, value: str):
        self.value = value


class _FallbackCheck:
    def __init__(self, status: str = "good", details: str = "fallback_ok"):
        self.status = _Value(status)
        self.details = details


class _FallbackIntrospectionResult:
    def __init__(self):
        self.overall_status = _Value("healthy")
        self.overall_score = 1.0
        self.checks = [_FallbackCheck()]
        self.total_checks = 1
        self.passed_checks = 1
        self.confidence = 1.0

    def is_healthy(self) -> bool:
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_status": self.overall_status.value,
            "overall_score": self.overall_score,
            "total_checks": self.total_checks,
            "passed_checks": self.passed_checks,
        }


class _FallbackIntrospectionProtocol:
    def __init__(self, _: str):
        pass

    def perform_hourly_check(self, **_: Any) -> _FallbackIntrospectionResult:
        return _FallbackIntrospectionResult()


class _FallbackFailureAnalysis:
    def __init__(self, description: str = "fallback_analysis"):
        self.pattern = _Value("none")
        self.severity = _Value("low")
        self.description = description


class _FallbackFailureAnalyzer:
    def analyze_activation_gap(self, **_: Any) -> _FallbackFailureAnalysis:
        return _FallbackFailureAnalysis("activation_gap_fallback")

    def analyze_principle_violation(self, **_: Any) -> _FallbackFailureAnalysis:
        return _FallbackFailureAnalysis("principle_violation_fallback")


class _FallbackActivationState:
    def __init__(self):
        self.principles_activation: Dict[str, float] = {}
        self.documents_activation: Dict[str, float] = {}
        self.concepts_activation: Dict[str, float] = {}

    def to_dict(self) -> Dict[str, Dict[str, float]]:
        return {
            "principles": self.principles_activation,
            "documents": self.documents_activation,
            "concepts": self.concepts_activation,
        }


class _FallbackActivationTracker:
    def record_principle_use(self, _: str) -> None:
        return None

    def capture_state(self) -> _FallbackActivationState:
        return _FallbackActivationState()


class _FallbackCategoryResult:
    def __init__(self):
        self.detected_category = _Value("general")
        self.confidence = 0.5
        self.required_protocols: List[str] = []


class _FallbackCategoryRecognizer:
    def classify_task(self, _: str) -> _FallbackCategoryResult:
        return _FallbackCategoryResult()


class _FallbackAttentionMetrics:
    def __init__(self):
        self.cognitive_load = 0.0
        self.focus_depth = 0.0
        self.attention_stability = 1.0
        self.working_memory_items = 0
        self.current_state = _Value("focused")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cognitive_load": self.cognitive_load,
            "focus_depth": self.focus_depth,
            "attention_stability": self.attention_stability,
            "working_memory_items": self.working_memory_items,
            "current_state": self.current_state.value,
        }


class _FallbackAttentionMonitor:
    def calculate_attention_metrics(self) -> _FallbackAttentionMetrics:
        return _FallbackAttentionMetrics()


class APOECASIntegration:
    """Integrates APOE with CAS for cognitive analysis and introspection.
    
    Provides:
    - Safety gate introspection
    - Policy gate introspection
    - Planner role decision analysis
    - Critic role introspection
    - Operator role decision analysis
    - Budget pooler resource pattern analysis
    """
    
    def __init__(self, session_id: Optional[str] = None):
        """
        Initialize CAS integration.
        
        Args:
            session_id: Optional session ID for tracking (auto-generated if None)
        """
        self.cas_available = CAS_AVAILABLE
        
        if not self.cas_available:
            logger.warning("CAS integration disabled: CAS package not available")
            return
        
        # Initialize CAS components; if partial imports exist, use safe shims.
        self.session_id = session_id or f"apoe_{datetime.now(timezone.utc).isoformat()}"
        self.introspection = (
            IntrospectionProtocol(self.session_id)
            if IntrospectionProtocol is not None
            else _FallbackIntrospectionProtocol(self.session_id)
        )
        self.failure_analyzer = (
            FailureModeAnalyzer()
            if FailureModeAnalyzer is not None
            else _FallbackFailureAnalyzer()
        )
        self.activation_tracker = (
            ActivationTracker()
            if ActivationTracker is not None
            else _FallbackActivationTracker()
        )
        self.category_recognizer = (
            CategoryRecognizer()
            if CategoryRecognizer is not None
            else _FallbackCategoryRecognizer()
        )
        self.attention_monitor = (
            AttentionMonitor()
            if AttentionMonitor is not None
            else _FallbackAttentionMonitor()
        )
    
    def introspect_safety_decision(
        self,
        decision_context: Dict[str, Any],
        safety_level: str,
        risk_assessment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Introspect safety gate decision (safety gates integration).
        
        Used by safetyGates component to analyze safety decisions.
        
        Args:
            decision_context: Context of the safety decision
            safety_level: Safety level (low, medium, high, critical)
            risk_assessment: Risk assessment details
            
        Returns:
            Introspection result with cognitive analysis
        """
        if not self.cas_available:
            return {
                "introspected": False,
                "error": "CAS not available",
                "recommendation": "proceed"
            }
        
        try:
            # Record activation
            self.activation_tracker.record_principle_use("safety_gates")
            
            # Perform introspection
            activation_state = self.activation_tracker.capture_state()
            attention_metrics = self.attention_monitor.calculate_attention_metrics()
            
            result = self.introspection.perform_hourly_check(
                activation_state=activation_state.to_dict(),
                attention_metrics={
                    "cognitive_load": attention_metrics.cognitive_load,
                    "focus_depth": attention_metrics.focus_depth,
                    "attention_stability": attention_metrics.attention_stability,
                    "working_memory_items": attention_metrics.working_memory_items
                },
                recent_failures=[],
                current_task=f"safety_gate_{safety_level}"
            )
            
            # Analyze failure modes if high risk
            failure_analysis = None
            if safety_level in ["high", "critical"]:
                # Use existing failure analysis methods
                failure_analysis = self.failure_analyzer.analyze_activation_gap(
                    current_task=f"safety_gate_{safety_level}",
                    required_principles=["safety_gates"],
                    activation_state=activation_state.principles_activation
                )
            
            return {
                "introspected": True,
                "healthy": result.is_healthy(),
                "overall_status": result.overall_status.value,
                "overall_score": result.overall_score,
                "warnings": [c.details for c in result.checks if c.status.value in ["poor", "critical"]],
                "failure_analysis": {
                    "pattern": failure_analysis.pattern.value if failure_analysis else None,
                    "severity": failure_analysis.severity.value if failure_analysis else None,
                    "description": failure_analysis.description if failure_analysis else None
                } if failure_analysis else None,
                "recommendation": "proceed" if result.is_healthy() else "review",
                "details": {
                    "activation_state": {
                        "principles": activation_state.principles_activation,
                        "documents": activation_state.documents_activation,
                        "concepts": activation_state.concepts_activation
                    },
                    "attention_metrics": {
                        "cognitive_load": attention_metrics.cognitive_load,
                        "focus_depth": attention_metrics.focus_depth,
                        "attention_stability": attention_metrics.attention_stability,
                        "current_state": attention_metrics.current_state.value
                    },
                    "introspection_result": {
                        "overall_status": result.overall_status.value,
                        "overall_score": result.overall_score,
                        "total_checks": result.total_checks,
                        "passed_checks": result.passed_checks
                    }
                }
            }
        except Exception as e:
            logger.error(f"Error introspecting safety decision: {e}")
            return {
                "introspected": False,
                "error": str(e),
                "recommendation": "proceed"
            }
    
    def introspect_policy_decision(
        self,
        decision_context: Dict[str, Any],
        policy_type: str,
        compliance_status: str
    ) -> Dict[str, Any]:
        """
        Introspect policy gate decision (policy gates integration).
        
        Used by policyGates component to analyze policy decisions.
        
        Args:
            decision_context: Context of the policy decision
            policy_type: Type of policy (compliance, authorization, etc.)
            compliance_status: Compliance status (compliant, non-compliant, unknown)
            
        Returns:
            Introspection result with cognitive analysis
        """
        if not self.cas_available:
            return {
                "introspected": False,
                "error": "CAS not available",
                "recommendation": "proceed"
            }
        
        try:
            # Record activation
            self.activation_tracker.record_principle_use("policy_gates")
            
            # Perform introspection
            activation_state = self.activation_tracker.capture_state()
            attention_metrics = self.attention_monitor.calculate_attention_metrics()
            
            result = self.introspection.perform_hourly_check(
                activation_state=activation_state.to_dict(),
                attention_metrics={
                    "cognitive_load": attention_metrics.cognitive_load,
                    "focus_depth": attention_metrics.focus_depth,
                    "attention_stability": attention_metrics.attention_stability,
                    "working_memory_items": attention_metrics.working_memory_items
                },
                recent_failures=[],
                current_task=f"policy_gate_{policy_type}"
            )
            
            # Analyze failure modes if non-compliant
            failure_analysis = None
            if compliance_status == "non-compliant":
                # Use existing failure analysis methods
                failure_analysis = self.failure_analyzer.analyze_principle_violation(
                    violated_principle=f"policy_{policy_type}",
                    violation_context=str(decision_context),
                    severity_level="high"
                )
            
            return {
                "introspected": True,
                "healthy": result.is_healthy(),
                "overall_status": result.overall_status.value,
                "overall_score": result.overall_score,
                "warnings": [c.details for c in result.checks if c.status.value in ["poor", "critical"]],
                "failure_analysis": {
                    "pattern": failure_analysis.pattern.value if failure_analysis else None,
                    "severity": failure_analysis.severity.value if failure_analysis else None,
                    "description": failure_analysis.description if failure_analysis else None
                } if failure_analysis else None,
                "recommendation": "proceed" if result.is_healthy() else "review",
                "details": {
                    "activation_state": {
                        "principles": activation_state.principles_activation,
                        "documents": activation_state.documents_activation,
                        "concepts": activation_state.concepts_activation
                    },
                    "attention_metrics": {
                        "cognitive_load": attention_metrics.cognitive_load,
                        "focus_depth": attention_metrics.focus_depth,
                        "attention_stability": attention_metrics.attention_stability,
                        "current_state": attention_metrics.current_state.value
                    },
                    "introspection_result": {
                        "overall_status": result.overall_status.value,
                        "overall_score": result.overall_score,
                        "total_checks": result.total_checks,
                        "passed_checks": result.passed_checks
                    }
                }
            }
        except Exception as e:
            logger.error(f"Error introspecting policy decision: {e}")
            return {
                "introspected": False,
                "error": str(e),
                "recommendation": "proceed"
            }
    
    def analyze_planning_decision(
        self,
        plan: ExecutionPlan,
        planning_strategy: Dict[str, Any],
        alternatives: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze planning decision (planner role integration).
        
        Used by plannerRole component to analyze planning decisions.
        
        Args:
            plan: Execution plan
            planning_strategy: Planning strategy details
            alternatives: List of alternative strategies considered
            
        Returns:
            Decision analysis result
        """
        if not self.cas_available:
            return {
                "analyzed": False,
                "error": "CAS not available",
                "recommendation": "proceed"
            }
        
        try:
            # Record activation
            self.activation_tracker.record_principle_use("planner_role")
            
            # Classify planning task
            task_description = f"Plan execution: {plan.name} with {len(plan.steps)} steps"
            category_result = self.category_recognizer.classify_task(task_description)
            
            # Perform introspection
            activation_state = self.activation_tracker.capture_state()
            attention_metrics = self.attention_monitor.calculate_attention_metrics()
            
            result = self.introspection.perform_hourly_check(
                activation_state=activation_state.to_dict(),
                attention_metrics={
                    "cognitive_load": attention_metrics.cognitive_load,
                    "focus_depth": attention_metrics.focus_depth,
                    "attention_stability": attention_metrics.attention_stability,
                    "working_memory_items": attention_metrics.working_memory_items
                },
                recent_failures=[],
                current_task=task_description
            )
            
            # Analyze decision quality
            decision_quality = self._assess_decision_quality(
                strategy=planning_strategy,
                alternatives=alternatives,
                category=category_result
            )
            
            return {
                "analyzed": True,
                "healthy": result.is_healthy(),
                "overall_status": result.overall_status.value,
                "overall_score": result.overall_score,
                "category": category_result.detected_category.value,
                "decision_quality": decision_quality,
                "recommendation": "proceed" if result.is_healthy() and decision_quality >= 0.7 else "review",
                "details": {
                    "category_result": {
                        "detected_category": category_result.detected_category.value,
                        "confidence": category_result.confidence,
                        "required_protocols": category_result.required_protocols
                    },
                    "activation_state": {
                        "principles": activation_state.principles_activation,
                        "documents": activation_state.documents_activation,
                        "concepts": activation_state.concepts_activation
                    },
                    "attention_metrics": {
                        "cognitive_load": attention_metrics.cognitive_load,
                        "focus_depth": attention_metrics.focus_depth,
                        "attention_stability": attention_metrics.attention_stability,
                        "current_state": attention_metrics.current_state.value
                    },
                    "introspection_result": {
                        "overall_status": result.overall_status.value,
                        "overall_score": result.overall_score,
                        "total_checks": result.total_checks,
                        "passed_checks": result.passed_checks
                    }
                }
            }
        except Exception as e:
            logger.error(f"Error analyzing planning decision: {e}")
            return {
                "analyzed": False,
                "error": str(e),
                "recommendation": "proceed"
            }
    
    def introspect_critique_decision(
        self,
        critique_context: Dict[str, Any],
        critique_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Introspect critique decision (critic role integration).
        
        Used by criticRole component to analyze critique decisions.
        
        Args:
            critique_context: Context of the critique
            critique_result: Critique result details
            
        Returns:
            Introspection result with cognitive analysis
        """
        if not self.cas_available:
            return {
                "introspected": False,
                "error": "CAS not available",
                "recommendation": "proceed"
            }
        
        try:
            # Record activation
            self.activation_tracker.record_principle_use("critic_role")
            
            # Perform introspection
            activation_state = self.activation_tracker.capture_state()
            attention_metrics = self.attention_monitor.calculate_attention_metrics()
            
            result = self.introspection.perform_hourly_check(
                activation_state=activation_state.to_dict(),
                attention_metrics={
                    "cognitive_load": attention_metrics.cognitive_load,
                    "focus_depth": attention_metrics.focus_depth,
                    "attention_stability": attention_metrics.attention_stability,
                    "working_memory_items": attention_metrics.working_memory_items
                },
                recent_failures=[],
                current_task="critique_decision"
            )
            
            return {
                "introspected": True,
                "healthy": result.is_healthy(),
                "overall_status": result.overall_status.value,
                "overall_score": result.overall_score,
                "warnings": [c.details for c in result.checks if c.status.value in ["poor", "critical"]],
                "recommendation": "proceed" if result.is_healthy() else "review",
                "details": {
                    "activation_state": {
                        "principles": activation_state.principles_activation,
                        "documents": activation_state.documents_activation,
                        "concepts": activation_state.concepts_activation
                    },
                    "attention_metrics": {
                        "cognitive_load": attention_metrics.cognitive_load,
                        "focus_depth": attention_metrics.focus_depth,
                        "attention_stability": attention_metrics.attention_stability,
                        "current_state": attention_metrics.current_state.value
                    },
                    "introspection_result": {
                        "overall_status": result.overall_status.value,
                        "overall_score": result.overall_score,
                        "total_checks": result.total_checks,
                        "passed_checks": result.passed_checks
                    }
                }
            }
        except Exception as e:
            logger.error(f"Error introspecting critique decision: {e}")
            return {
                "introspected": False,
                "error": str(e),
                "recommendation": "proceed"
            }
    
    def analyze_operational_decision(
        self,
        operation_context: Dict[str, Any],
        operation_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze operational decision (operator role integration).
        
        Used by operatorRole component to analyze operational decisions.
        
        Args:
            operation_context: Context of the operation
            operation_result: Operation result details
            
        Returns:
            Decision analysis result
        """
        if not self.cas_available:
            return {
                "analyzed": False,
                "error": "CAS not available",
                "recommendation": "proceed"
            }
        
        try:
            # Record activation
            self.activation_tracker.record_principle_use("operator_role")
            
            # Classify operational task
            task_description = operation_context.get("description", "operational_task")
            category_result = self.category_recognizer.classify_task(task_description)
            
            # Perform introspection
            activation_state = self.activation_tracker.capture_state()
            attention_metrics = self.attention_monitor.calculate_attention_metrics()
            
            result = self.introspection.perform_hourly_check(
                activation_state=activation_state.to_dict(),
                attention_metrics={
                    "cognitive_load": attention_metrics.cognitive_load,
                    "focus_depth": attention_metrics.focus_depth,
                    "attention_stability": attention_metrics.attention_stability,
                    "working_memory_items": attention_metrics.working_memory_items
                },
                recent_failures=[],
                current_task=task_description
            )
            
            return {
                "analyzed": True,
                "healthy": result.is_healthy(),
                "overall_status": result.overall_status.value,
                "overall_score": result.overall_score,
                "category": category_result.detected_category.value,
                "recommendation": "proceed" if result.is_healthy() else "review",
                "details": {
                    "category_result": {
                        "detected_category": category_result.detected_category.value,
                        "confidence": category_result.confidence,
                        "required_protocols": category_result.required_protocols
                    },
                    "activation_state": {
                        "principles": activation_state.principles_activation,
                        "documents": activation_state.documents_activation,
                        "concepts": activation_state.concepts_activation
                    },
                    "attention_metrics": {
                        "cognitive_load": attention_metrics.cognitive_load,
                        "focus_depth": attention_metrics.focus_depth,
                        "attention_stability": attention_metrics.attention_stability,
                        "current_state": attention_metrics.current_state.value
                    },
                    "introspection_result": {
                        "overall_status": result.overall_status.value,
                        "overall_score": result.overall_score,
                        "total_checks": result.total_checks,
                        "passed_checks": result.passed_checks
                    }
                }
            }
        except Exception as e:
            logger.error(f"Error analyzing operational decision: {e}")
            return {
                "analyzed": False,
                "error": str(e),
                "recommendation": "proceed"
            }
    
    def analyze_resource_patterns(
        self,
        budget_history: List[Budget],
        resource_usage: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze resource patterns (budget pooler integration).
        
        Used by budgetPooler component to analyze resource usage patterns.
        
        Args:
            budget_history: History of budget allocations
            resource_usage: Current resource usage details
            
        Returns:
            Resource pattern analysis result
        """
        if not self.cas_available:
            return {
                "analyzed": False,
                "error": "CAS not available",
                "recommendation": "continue"
            }
        
        try:
            # Record activation
            self.activation_tracker.record_principle_use("budget_pooler")
            
            # Analyze patterns
            patterns = self._detect_resource_patterns(budget_history, resource_usage)
            
            # Perform introspection
            activation_state = self.activation_tracker.capture_state()
            attention_metrics = self.attention_monitor.calculate_attention_metrics()
            
            result = self.introspection.perform_hourly_check(
                activation_state=activation_state.to_dict(),
                attention_metrics={
                    "cognitive_load": attention_metrics.cognitive_load,
                    "focus_depth": attention_metrics.focus_depth,
                    "attention_stability": attention_metrics.attention_stability,
                    "working_memory_items": attention_metrics.working_memory_items
                },
                recent_failures=[],
                current_task="resource_pattern_analysis"
            )
            
            return {
                "analyzed": True,
                "patterns": patterns,
                "healthy": result.is_healthy(),
                "confidence": result.confidence,
                "recommendation": "optimize" if patterns.get("needs_optimization", False) else "continue",
                "details": {
                    "activation_state": activation_state.to_dict(),
                    "attention_metrics": attention_metrics.to_dict(),
                    "introspection_result": result.to_dict()
                }
            }
        except Exception as e:
            logger.error(f"Error analyzing resource patterns: {e}")
            return {
                "analyzed": False,
                "error": str(e),
                "recommendation": "continue"
            }
    
    def _assess_decision_quality(
        self,
        strategy: Dict[str, Any],
        alternatives: List[Dict[str, Any]],
        category: CategoryResult
    ) -> float:
        """Assess quality of a decision based on strategy and alternatives."""
        # Simple heuristic: more alternatives considered = better decision
        # In practice, this would use more sophisticated analysis
        base_quality = 0.7
        alternatives_bonus = min(len(alternatives) * 0.1, 0.3)
        return min(base_quality + alternatives_bonus, 1.0)
    
    def _detect_resource_patterns(
        self,
        budget_history: List[Budget],
        resource_usage: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Detect resource usage patterns."""
        if not budget_history:
            return {"needs_optimization": False, "patterns": []}
        
        # Simple pattern detection
        total_tokens = sum(b.tokens for b in budget_history if b.tokens)
        avg_tokens = total_tokens / len(budget_history) if budget_history else 0
        
        patterns = []
        needs_optimization = False
        
        if avg_tokens > resource_usage.get("token_limit", 10000) * 0.8:
            patterns.append("high_token_usage")
            needs_optimization = True
        
        return {
            "needs_optimization": needs_optimization,
            "patterns": patterns,
            "avg_tokens": avg_tokens,
            "total_budgets": len(budget_history)
        }

