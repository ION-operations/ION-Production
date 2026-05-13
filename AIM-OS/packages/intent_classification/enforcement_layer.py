"""
Enforcement Layer

Safety controls and behavior gating for the Intent Classification System.
Implements stop conditions, escalation triggers, and action validation.
"""

from __future__ import annotations
from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

from .mission_intent import MissionIntent, MissionStatus, ScopeLevel, LifecycleStage, ClarityState

logger = logging.getLogger(__name__)


class EnforcementAction(Enum):
    """Actions that can be taken by the enforcement layer."""
    
    ALLOW = "allow"
    BLOCK = "block"
    ESCALATE = "escalate"
    REQUIRE_APPROVAL = "require_approval"
    WARN = "warn"
    PAUSE = "pause"


@dataclass
class EnforcementResult:
    """Result of enforcement layer evaluation."""
    
    action: EnforcementAction
    reason: str
    confidence: float
    required_approvals: List[str]
    warnings: List[str]
    stop_conditions_triggered: List[str]
    escalation_required: bool
    escalation_reason: Optional[str] = None


class EnforcementLayer:
    """
    Enforcement layer for behavior gating and safety controls.
    
    Evaluates actions against mission intent to determine if they should be
    allowed, blocked, escalated, or require approval.
    """
    
    def __init__(self):
        """Initialize the enforcement layer."""
        self._stop_conditions = self._build_stop_conditions()
        self._escalation_triggers = self._build_escalation_triggers()
        self._approval_requirements = self._build_approval_requirements()
        
        # Enforcement thresholds
        self._thresholds = {
            'confidence_min': 0.3,
            'complexity_max': 0.8,
            'scope_platform_approval': True,
            'clarity_exploratory_block': True
        }
    
    def evaluate_action(self, action: str, mission_intent: MissionIntent, 
                       context: Optional[Dict[str, Any]] = None) -> EnforcementResult:
        """
        Evaluate whether an action should be allowed for a mission.
        
        Args:
            action: Action to evaluate
            mission_intent: Mission intent context
            context: Optional additional context
            
        Returns:
            EnforcementResult with enforcement decision
        """
        warnings = []
        stop_conditions_triggered = []
        required_approvals = []
        escalation_required = False
        escalation_reason = None
        
        # Check if action is explicitly blocked
        if action in mission_intent.blocked_actions:
            return EnforcementResult(
                action=EnforcementAction.BLOCK,
                reason=f"Action '{action}' is explicitly blocked for this mission",
                confidence=1.0,
                required_approvals=[],
                warnings=[],
                stop_conditions_triggered=[],
                escalation_required=False
            )
        
        # Check if action is explicitly allowed
        if action in mission_intent.allowed_actions:
            # Still check for stop conditions even if allowed
            stop_result = self._check_stop_conditions(action, mission_intent, context)
            if stop_result['triggered']:
                return EnforcementResult(
                    action=EnforcementAction.BLOCK,
                    reason=f"Stop conditions triggered: {', '.join(stop_result['conditions'])}",
                    confidence=1.0,
                    required_approvals=[],
                    warnings=[],
                    stop_conditions_triggered=stop_result['conditions'],
                    escalation_required=True,
                    escalation_reason="Stop conditions triggered"
                )
        
        # Check confidence threshold
        if mission_intent.confidence_level < self._thresholds['confidence_min']:
            return EnforcementResult(
                action=EnforcementAction.ESCALATE,
                reason=f"Confidence level {mission_intent.confidence_level} below threshold {self._thresholds['confidence_min']}",
                confidence=1.0,
                required_approvals=[],
                warnings=[],
                stop_conditions_triggered=[],
                escalation_required=True,
                escalation_reason="Low confidence level"
            )
        
        # Check complexity threshold
        if mission_intent.complexity_score > self._thresholds['complexity_max']:
            warnings.append(f"High complexity score: {mission_intent.complexity_score}")
            if action in ['implement', 'deploy', 'modify_code']:
                return EnforcementResult(
                    action=EnforcementAction.ESCALATE,
                    reason=f"High complexity score {mission_intent.complexity_score} with implementation action",
                    confidence=1.0,
                    required_approvals=[],
                    warnings=warnings,
                    stop_conditions_triggered=[],
                    escalation_required=True,
                    escalation_reason="High complexity with implementation action"
                )
        
        # Check scope-based restrictions
        if mission_intent.scope_level == ScopeLevel.WHOLE_PLATFORM:
            if action in ['implement', 'deploy', 'modify_code']:
                if self._thresholds['scope_platform_approval']:
                    required_approvals.append('platform_scope_approval')
                    warnings.append("Platform-wide scope requires approval for implementation actions")
                else:
                    return EnforcementResult(
                        action=EnforcementAction.BLOCK,
                        reason="Platform-wide scope blocks implementation actions",
                        confidence=1.0,
                        required_approvals=[],
                        warnings=warnings,
                        stop_conditions_triggered=[],
                        escalation_required=True,
                        escalation_reason="Platform-wide scope with implementation action"
                    )
        
        # Check clarity-based restrictions
        if (mission_intent.clarity_state == ClarityState.EXPLORATORY and 
            action in ['implement', 'deploy', 'modify_code']):
            if self._thresholds['clarity_exploratory_block']:
                return EnforcementResult(
                    action=EnforcementAction.BLOCK,
                    reason="Exploratory clarity state blocks implementation actions",
                    confidence=1.0,
                    required_approvals=[],
                    warnings=warnings,
                    stop_conditions_triggered=[],
                    escalation_required=True,
                    escalation_reason="Exploratory state with implementation action"
                )
            else:
                warnings.append("Exploratory clarity state with implementation action - proceed with caution")
        
        # Check lifecycle stage restrictions
        lifecycle_result = self._check_lifecycle_restrictions(action, mission_intent)
        if lifecycle_result['action'] != EnforcementAction.ALLOW:
            return EnforcementResult(
                action=lifecycle_result['action'],
                reason=lifecycle_result['reason'],
                confidence=lifecycle_result['confidence'],
                required_approvals=lifecycle_result.get('required_approvals', []),
                warnings=warnings + lifecycle_result.get('warnings', []),
                stop_conditions_triggered=[],
                escalation_required=lifecycle_result.get('escalation_required', False),
                escalation_reason=lifecycle_result.get('escalation_reason')
            )
        
        # Check stop conditions
        stop_result = self._check_stop_conditions(action, mission_intent, context)
        if stop_result['triggered']:
            return EnforcementResult(
                action=EnforcementAction.BLOCK,
                reason=f"Stop conditions triggered: {', '.join(stop_result['conditions'])}",
                confidence=1.0,
                required_approvals=[],
                warnings=warnings,
                stop_conditions_triggered=stop_result['conditions'],
                escalation_required=True,
                escalation_reason="Stop conditions triggered"
            )
        
        # Check escalation requirements
        if mission_intent.requires_escalation():
            escalation_required = True
            escalation_reason = mission_intent.get_escalation_reason()
            warnings.append(f"Mission requires escalation: {escalation_reason}")
        
        # Determine final action
        if required_approvals:
            action_type = EnforcementAction.REQUIRE_APPROVAL
            reason = f"Action requires approval: {', '.join(required_approvals)}"
        elif escalation_required:
            action_type = EnforcementAction.ESCALATE
            reason = f"Escalation required: {escalation_reason}"
        elif warnings:
            action_type = EnforcementAction.WARN
            reason = f"Action allowed with warnings: {', '.join(warnings)}"
        else:
            action_type = EnforcementAction.ALLOW
            reason = "Action allowed"
        
        return EnforcementResult(
            action=action_type,
            reason=reason,
            confidence=0.9,
            required_approvals=required_approvals,
            warnings=warnings,
            stop_conditions_triggered=[],
            escalation_required=escalation_required,
            escalation_reason=escalation_reason
        )
    
    def _check_stop_conditions(self, action: str, mission_intent: MissionIntent, 
                              context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Check if any stop conditions are triggered."""
        triggered_conditions = []
        
        for condition in mission_intent.stop_conditions:
            if self._evaluate_stop_condition(condition, action, mission_intent, context):
                triggered_conditions.append(condition)
        
        return {
            'triggered': len(triggered_conditions) > 0,
            'conditions': triggered_conditions
        }
    
    def _evaluate_stop_condition(self, condition: str, action: str, mission_intent: MissionIntent, 
                                context: Optional[Dict[str, Any]]) -> bool:
        """Evaluate a specific stop condition."""
        # Simple condition evaluation - can be extended for more complex conditions
        if condition == "confidence_level < 0.3":
            return mission_intent.confidence_level < 0.3
        elif condition == "complexity_score > 0.8":
            return mission_intent.complexity_score > 0.8
        elif condition == "scope_level = whole_platform":
            return mission_intent.scope_level == ScopeLevel.WHOLE_PLATFORM
        elif condition == "clarity_state = exploratory + implementation_stage":
            return (mission_intent.clarity_state == ClarityState.EXPLORATORY and 
                   mission_intent.lifecycle_stage in [LifecycleStage.IMPLEMENTATION, LifecycleStage.INTEGRATION])
        
        return False
    
    def _check_lifecycle_restrictions(self, action: str, mission_intent: MissionIntent) -> Dict[str, Any]:
        """Check lifecycle stage restrictions for actions."""
        stage = mission_intent.lifecycle_stage
        
        # Define action restrictions by lifecycle stage
        restrictions = {
            LifecycleStage.IDEATION: {
                'allowed': ['research', 'analyze', 'explore', 'investigate', 'brainstorm'],
                'blocked': ['implement', 'deploy', 'modify_code', 'test'],
                'warn': ['design', 'plan']
            },
            LifecycleStage.ARCHITECTURE: {
                'allowed': ['design', 'plan', 'document', 'analyze', 'research'],
                'blocked': ['deploy', 'modify_code'],
                'warn': ['implement', 'test']
            },
            LifecycleStage.IMPLEMENTATION: {
                'allowed': ['implement', 'code', 'test', 'modify_code', 'debug'],
                'blocked': ['deploy'],
                'warn': ['research', 'analyze']
            },
            LifecycleStage.INTEGRATION: {
                'allowed': ['integrate', 'test', 'deploy', 'connect'],
                'blocked': ['research', 'analyze'],
                'warn': ['implement', 'modify_code']
            },
            LifecycleStage.HARDENING: {
                'allowed': ['test', 'optimize', 'secure', 'tune'],
                'blocked': ['research', 'analyze', 'implement'],
                'warn': ['deploy', 'modify_code']
            },
            LifecycleStage.STABILIZATION: {
                'allowed': ['monitor', 'maintain', 'document', 'support'],
                'blocked': ['implement', 'modify_code', 'research'],
                'warn': ['deploy', 'test']
            },
            LifecycleStage.DEPRECATION: {
                'allowed': ['remove', 'deprecate', 'document', 'migrate'],
                'blocked': ['implement', 'modify_code', 'deploy'],
                'warn': ['test', 'integrate']
            }
        }
        
        stage_restrictions = restrictions.get(stage, {})
        
        if action in stage_restrictions.get('blocked', []):
            return {
                'action': EnforcementAction.BLOCK,
                'reason': f"Action '{action}' is blocked in {stage.value} stage",
                'confidence': 1.0,
                'warnings': [],
                'escalation_required': True,
                'escalation_reason': f"Blocked action in {stage.value} stage"
            }
        
        if action in stage_restrictions.get('warn', []):
            return {
                'action': EnforcementAction.WARN,
                'reason': f"Action '{action}' is not typical for {stage.value} stage",
                'confidence': 0.7,
                'warnings': [f"Action '{action}' is not typical for {stage.value} stage"],
                'escalation_required': False
            }
        
        return {
            'action': EnforcementAction.ALLOW,
            'reason': f"Action '{action}' is allowed in {stage.value} stage",
            'confidence': 0.9,
            'warnings': [],
            'escalation_required': False
        }
    
    def _build_stop_conditions(self) -> Dict[str, str]:
        """Build stop condition definitions."""
        return {
            'confidence_below_threshold': 'confidence_level < 0.3',
            'platform_wide_scope_requires_approval': 'scope_level = whole_platform + edit_attempt',
            'exploratory_state_blocks_implementation': 'clarity_state = exploratory + implementation_stage',
            'high_complexity_requires_review': 'complexity_score > 0.8'
        }
    
    def _build_escalation_triggers(self) -> Dict[str, str]:
        """Build escalation trigger definitions."""
        return {
            'confidence_low': 'confidence < 0.3',
            'scope_platform_edit': 'scope_level = whole_platform + edit_attempt',
            'clarity_exploratory_edit': 'clarity_state = exploratory + edit_attempt',
            'complexity_high': 'complexity_score > 0.8'
        }
    
    def _build_approval_requirements(self) -> Dict[str, List[str]]:
        """Build approval requirement definitions."""
        return {
            'platform_scope_approval': ['platform_scope_approval'],
            'high_complexity_approval': ['complexity_approval'],
            'exploratory_implementation_approval': ['clarity_approval', 'implementation_approval']
        }
    
    def update_thresholds(self, thresholds: Dict[str, Any]) -> None:
        """Update enforcement thresholds."""
        self._thresholds.update(thresholds)
        logger.info(f"Updated enforcement thresholds: {thresholds}")
    
    def get_enforcement_stats(self) -> Dict[str, Any]:
        """Get enforcement layer statistics."""
        return {
            'thresholds': self._thresholds,
            'stop_conditions_count': len(self._stop_conditions),
            'escalation_triggers_count': len(self._escalation_triggers),
            'approval_requirements_count': len(self._approval_requirements)
        }
