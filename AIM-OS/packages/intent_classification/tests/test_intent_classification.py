"""
Comprehensive tests for Intent Classification System

Tests all components including classification engine, enforcement layer,
timeline integration, and mission intent data models.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from intent_classification.mission_intent import (
    MissionIntent, PrimaryCategory, LifecycleStage, ScopeLevel, 
    ClarityState, MissionStatus
)
from intent_classification.classification_engine import ClassificationEngine, ClassificationResult
from intent_classification.enforcement_layer import EnforcementLayer, EnforcementAction, EnforcementResult
from intent_classification.timeline_integration import TimelineIntegration, TimelineEvent, TimelineEventType


class TestMissionIntent:
    """Test MissionIntent data model."""
    
    def test_mission_intent_creation(self):
        """Test basic mission intent creation."""
        intent = MissionIntent(
            raw_intent="Create a new user authentication system",
            primary_category=PrimaryCategory.NEW_SYSTEM_DESIGN,
            lifecycle_stage=LifecycleStage.IDEATION,
            scope_level=ScopeLevel.MULTI_SERVICE,
            clarity_state=ClarityState.PARTIALLY_DEFINED,
            confidence_level=0.8,
            complexity_score=0.7
        )
        
        assert intent.raw_intent == "Create a new user authentication system"
        assert intent.primary_category == PrimaryCategory.NEW_SYSTEM_DESIGN
        assert intent.lifecycle_stage == LifecycleStage.IDEATION
        assert intent.scope_level == ScopeLevel.MULTI_SERVICE
        assert intent.clarity_state == ClarityState.PARTIALLY_DEFINED
        assert intent.confidence_level == 0.8
        assert intent.complexity_score == 0.7
    
    def test_confidence_validation(self):
        """Test confidence level validation."""
        with pytest.raises(ValueError, match="Confidence level must be between 0.0 and 1.0"):
            MissionIntent(confidence_level=1.5)
        
        with pytest.raises(ValueError, match="Confidence level must be between 0.0 and 1.0"):
            MissionIntent(confidence_level=-0.1)
    
    def test_complexity_validation(self):
        """Test complexity score validation."""
        with pytest.raises(ValueError, match="Complexity score must be between 0.0 and 1.0"):
            MissionIntent(complexity_score=1.5)
        
        with pytest.raises(ValueError, match="Complexity score must be between 0.0 and 1.0"):
            MissionIntent(complexity_score=-0.1)
    
    def test_facet_management(self):
        """Test facet addition and removal."""
        intent = MissionIntent()
        
        intent.add_facet("frontend")
        assert "frontend" in intent.facets
        
        intent.add_facet("  BACKEND  ")  # Test normalization
        assert "backend" in intent.facets
        
        intent.remove_facet("frontend")
        assert "frontend" not in intent.facets
        assert "backend" in intent.facets
    
    def test_action_management(self):
        """Test action management."""
        intent = MissionIntent()
        
        intent.add_allowed_action("implement")
        assert intent.is_action_allowed("implement")
        
        intent.add_blocked_action("implement")
        assert not intent.is_action_allowed("implement")
        assert "implement" not in intent.allowed_actions
    
    def test_escalation_requirements(self):
        """Test escalation requirement detection."""
        # Low confidence should require escalation
        intent = MissionIntent(confidence_level=0.2)
        assert intent.requires_escalation()
        assert "Low confidence level" in intent.get_escalation_reason()
        
        # Platform scope with implementation should require escalation
        intent = MissionIntent(
            scope_level=ScopeLevel.WHOLE_PLATFORM,
            lifecycle_stage=LifecycleStage.IMPLEMENTATION
        )
        assert intent.requires_escalation()
        
        # High complexity should require escalation
        intent = MissionIntent(complexity_score=0.9)
        assert intent.requires_escalation()
    
    def test_serialization(self):
        """Test mission intent serialization and deserialization."""
        intent = MissionIntent(
            raw_intent="Test intent",
            primary_category=PrimaryCategory.BUG_FIX,
            lifecycle_stage=LifecycleStage.IMPLEMENTATION,
            scope_level=ScopeLevel.SINGLE_MODULE,
            clarity_state=ClarityState.FULLY_DEFINED,
            confidence_level=0.9,
            complexity_score=0.3
        )
        
        # Test to_dict
        data = intent.to_dict()
        assert data["raw_intent"] == "Test intent"
        assert data["primary_category"] == "bug_fix"
        assert data["lifecycle_stage"] == "implementation"
        
        # Test from_dict
        restored_intent = MissionIntent.from_dict(data)
        assert restored_intent.raw_intent == intent.raw_intent
        assert restored_intent.primary_category == intent.primary_category
        assert restored_intent.lifecycle_stage == intent.lifecycle_stage


class TestClassificationEngine:
    """Test ClassificationEngine functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.engine = ClassificationEngine()
    
    def test_classify_new_system_design(self):
        """Test classification of new system design intent."""
        result = self.engine.classify_intent("Create a new user authentication system")
        
        assert result.mission_intent.primary_category == PrimaryCategory.NEW_SYSTEM_DESIGN
        assert result.classification_confidence > 0.0
        assert result.mission_intent.raw_intent == "Create a new user authentication system"
    
    def test_classify_bug_fix(self):
        """Test classification of bug fix intent."""
        result = self.engine.classify_intent("Fix the login bug that's causing errors")
        
        assert result.mission_intent.primary_category == PrimaryCategory.BUG_FIX
        assert result.classification_confidence > 0.0
    
    def test_classify_performance_optimization(self):
        """Test classification of performance optimization intent."""
        result = self.engine.classify_intent("Optimize the database queries for better performance")
        
        assert result.mission_intent.primary_category == PrimaryCategory.PERFORMANCE_OPTIMIZATION
        assert result.classification_confidence > 0.0
    
    def test_classify_research_probe(self):
        """Test classification of research probe intent."""
        result = self.engine.classify_intent("Research the best authentication methods")
        
        assert result.mission_intent.primary_category == PrimaryCategory.RESEARCH_PROBE
        assert result.classification_confidence > 0.0
    
    def test_lifecycle_stage_classification(self):
        """Test lifecycle stage classification."""
        # Ideation stage
        result = self.engine.classify_intent("I'm thinking about building a new system")
        assert result.mission_intent.lifecycle_stage == LifecycleStage.IDEATION
        
        # Implementation stage
        result = self.engine.classify_intent("I need to implement the user login feature")
        assert result.mission_intent.lifecycle_stage == LifecycleStage.IMPLEMENTATION
    
    def test_scope_level_classification(self):
        """Test scope level classification."""
        # Local function scope
        result = self.engine.classify_intent("Fix this function to handle errors better")
        assert result.mission_intent.scope_level == ScopeLevel.LOCAL_FUNCTION
        
        # Platform scope
        result = self.engine.classify_intent("Redesign the entire platform architecture")
        assert result.mission_intent.scope_level == ScopeLevel.WHOLE_PLATFORM
    
    def test_clarity_state_classification(self):
        """Test clarity state classification."""
        # Exploratory state
        result = self.engine.classify_intent("I'm not sure what's wrong, need to investigate")
        assert result.mission_intent.clarity_state == ClarityState.EXPLORATORY
        
        # Fully defined state
        result = self.engine.classify_intent("I need to implement exactly this specific feature")
        assert result.mission_intent.clarity_state == ClarityState.FULLY_DEFINED
    
    def test_facet_generation(self):
        """Test facet generation."""
        result = self.engine.classify_intent("Create a React frontend with authentication")
        
        assert "frontend" in result.mission_intent.facets
        assert "authentication" in result.mission_intent.facets or "auth" in result.mission_intent.facets
    
    def test_complexity_calculation(self):
        """Test complexity score calculation."""
        # Simple intent
        result = self.engine.classify_intent("Fix a small bug")
        assert result.mission_intent.complexity_score < 0.5
        
        # Complex intent
        result = self.engine.classify_intent("Design and implement a complex distributed authentication system with advanced security features")
        assert result.mission_intent.complexity_score > 0.5
    
    def test_behavior_controls_generation(self):
        """Test behavior controls generation."""
        # Ideation stage should block implementation
        result = self.engine.classify_intent("I'm thinking about a new system")
        assert "implement" in result.mission_intent.blocked_actions
        assert "research" in result.mission_intent.allowed_actions
        
        # Implementation stage should allow implementation
        result = self.engine.classify_intent("I need to implement this feature")
        assert "implement" in result.mission_intent.allowed_actions
    
    def test_error_handling(self):
        """Test error handling in classification."""
        # Test with empty intent
        result = self.engine.classify_intent("")
        assert result.mission_intent.primary_category == PrimaryCategory.INVESTIGATION
        assert result.classification_confidence == 0.0
        assert len(result.errors) > 0


class TestEnforcementLayer:
    """Test EnforcementLayer functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.enforcement = EnforcementLayer()
    
    def test_allow_action(self):
        """Test allowing an action."""
        intent = MissionIntent(
            primary_category=PrimaryCategory.BUG_FIX,
            lifecycle_stage=LifecycleStage.IMPLEMENTATION,
            scope_level=ScopeLevel.SINGLE_MODULE,
            clarity_state=ClarityState.FULLY_DEFINED,
            confidence_level=0.8,
            complexity_score=0.3
        )
        intent.add_allowed_action("implement")
        
        result = self.enforcement.evaluate_action("implement", intent)
        
        assert result.action == EnforcementAction.ALLOW
        assert result.confidence > 0.0
    
    def test_block_explicitly_blocked_action(self):
        """Test blocking an explicitly blocked action."""
        intent = MissionIntent()
        intent.add_blocked_action("implement")
        
        result = self.enforcement.evaluate_action("implement", intent)
        
        assert result.action == EnforcementAction.BLOCK
        assert "explicitly blocked" in result.reason
    
    def test_escalate_low_confidence(self):
        """Test escalation for low confidence."""
        intent = MissionIntent(confidence_level=0.2)
        
        result = self.enforcement.evaluate_action("implement", intent)
        
        assert result.action == EnforcementAction.ESCALATE
        assert result.escalation_required
        assert "confidence" in result.escalation_reason.lower()
    
    def test_escalate_high_complexity(self):
        """Test escalation for high complexity with implementation action."""
        intent = MissionIntent(complexity_score=0.9)
        
        result = self.enforcement.evaluate_action("implement", intent)
        
        assert result.action == EnforcementAction.ESCALATE
        assert result.escalation_required
        assert "complexity" in result.escalation_reason.lower()
    
    def test_block_platform_scope_implementation(self):
        """Test blocking platform scope implementation actions."""
        intent = MissionIntent(
            scope_level=ScopeLevel.WHOLE_PLATFORM,
            lifecycle_stage=LifecycleStage.IMPLEMENTATION
        )
        
        result = self.enforcement.evaluate_action("implement", intent)
        
        assert result.action in [EnforcementAction.BLOCK, EnforcementAction.REQUIRE_APPROVAL]
        assert result.escalation_required
    
    def test_block_exploratory_implementation(self):
        """Test blocking implementation actions in exploratory state."""
        intent = MissionIntent(
            clarity_state=ClarityState.EXPLORATORY,
            lifecycle_stage=LifecycleStage.IMPLEMENTATION
        )
        
        result = self.enforcement.evaluate_action("implement", intent)
        
        assert result.action == EnforcementAction.BLOCK
        assert result.escalation_required
        assert "exploratory" in result.escalation_reason.lower()
    
    def test_lifecycle_restrictions(self):
        """Test lifecycle stage restrictions."""
        # Ideation stage should block implementation
        intent = MissionIntent(lifecycle_stage=LifecycleStage.IDEATION)
        
        result = self.enforcement.evaluate_action("implement", intent)
        
        assert result.action == EnforcementAction.BLOCK
        assert "ideation" in result.reason.lower()
        
        # Implementation stage should allow implementation
        intent = MissionIntent(lifecycle_stage=LifecycleStage.IMPLEMENTATION)
        
        result = self.enforcement.evaluate_action("implement", intent)
        
        assert result.action == EnforcementAction.ALLOW
    
    def test_stop_conditions(self):
        """Test stop condition evaluation."""
        intent = MissionIntent(
            confidence_level=0.2,
            stop_conditions=["confidence_level < 0.3"]
        )
        
        result = self.enforcement.evaluate_action("implement", intent)
        
        assert result.action == EnforcementAction.BLOCK
        assert "stop conditions" in result.reason.lower()


class TestTimelineIntegration:
    """Test TimelineIntegration functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.timeline = TimelineIntegration()
    
    def test_log_mission_created(self):
        """Test logging mission creation."""
        intent = MissionIntent(
            raw_intent="Test mission",
            primary_category=PrimaryCategory.BUG_FIX,
            confidence_level=0.8
        )
        
        event = self.timeline.log_mission_created(intent, 0.8)
        
        assert event.event_type == TimelineEventType.MISSION_CREATED
        assert event.mission_id == intent.mission_id
        assert event.action_attempted == "create_mission"
        assert event.decision == "mission_created"
    
    def test_log_action_attempted(self):
        """Test logging action attempt."""
        intent = MissionIntent(confidence_level=0.8)
        enforcement_result = EnforcementResult(
            action=EnforcementAction.ALLOW,
            reason="Action allowed",
            confidence=0.9,
            required_approvals=[],
            warnings=[],
            stop_conditions_triggered=[],
            escalation_required=False
        )
        
        event = self.timeline.log_action_attempted("implement", intent, enforcement_result)
        
        assert event.event_type == TimelineEventType.ACTION_ALLOWED
        assert event.action_attempted == "implement"
        assert event.decision == "allow"
    
    def test_log_mission_completed(self):
        """Test logging mission completion."""
        intent = MissionIntent(confidence_level=0.8)
        artifacts = ["test_file.py", "documentation.md"]
        
        event = self.timeline.log_mission_completed(intent, "Successfully completed", artifacts)
        
        assert event.event_type == TimelineEventType.MISSION_COMPLETED
        assert event.artifacts_produced == artifacts
        assert "Successfully completed" in event.rationale
    
    def test_get_mission_timeline(self):
        """Test getting mission timeline."""
        intent = MissionIntent(confidence_level=0.8)
        
        # Log some events
        self.timeline.log_mission_created(intent, 0.8)
        self.timeline.log_mission_completed(intent, "Completed", [])
        
        timeline = self.timeline.get_mission_timeline(intent.mission_id)
        
        assert len(timeline) == 2
        assert timeline[0].event_type == TimelineEventType.MISSION_CREATED
        assert timeline[1].event_type == TimelineEventType.MISSION_COMPLETED
    
    def test_get_event_statistics(self):
        """Test getting event statistics."""
        intent = MissionIntent(confidence_level=0.8)
        
        # Log some events
        self.timeline.log_mission_created(intent, 0.8)
        self.timeline.log_mission_completed(intent, "Completed", [])
        
        stats = self.timeline.get_event_statistics()
        
        assert stats["total_events"] == 2
        assert stats["missions_tracked"] == 1
        assert stats["event_counts"][TimelineEventType.MISSION_CREATED] == 1
        assert stats["event_counts"][TimelineEventType.MISSION_COMPLETED] == 1


class TestIntegration:
    """Test integration between components."""
    
    def test_full_classification_workflow(self):
        """Test complete classification workflow."""
        engine = ClassificationEngine()
        enforcement = EnforcementLayer()
        timeline = TimelineIntegration()
        
        # Classify intent
        result = engine.classify_intent("Create a new authentication system")
        
        # Log classification
        timeline.log_mission_classified(result.mission_intent, {
            'classification_confidence': result.classification_confidence,
            'processing_time_ms': result.processing_time_ms,
            'warnings': result.warnings,
            'errors': result.errors
        })
        
        # Evaluate action
        enforcement_result = enforcement.evaluate_action("implement", result.mission_intent)
        
        # Log action attempt
        timeline.log_action_attempted("implement", result.mission_intent, enforcement_result)
        
        # Verify results
        assert result.mission_intent.primary_category == PrimaryCategory.NEW_SYSTEM_DESIGN
        assert result.classification_confidence > 0.0
        assert enforcement_result.action in [EnforcementAction.ALLOW, EnforcementAction.ESCALATE, EnforcementAction.REQUIRE_APPROVAL]
        
        # Verify timeline
        mission_timeline = timeline.get_mission_timeline(result.mission_intent.mission_id)
        assert len(mission_timeline) == 2  # classification + action attempt
    
    def test_escalation_workflow(self):
        """Test escalation workflow."""
        engine = ClassificationEngine()
        enforcement = EnforcementLayer()
        timeline = TimelineIntegration()
        
        # Classify low-confidence intent
        result = engine.classify_intent("I'm not sure what to do")
        
        # Evaluate action
        enforcement_result = enforcement.evaluate_action("implement", result.mission_intent)
        
        # Log escalation
        if enforcement_result.escalation_required:
            timeline.log_escalation_required(
                result.mission_intent,
                enforcement_result.escalation_reason,
                {"confidence": result.mission_intent.confidence_level}
            )
        
        # Verify escalation
        assert enforcement_result.escalation_required
        assert enforcement_result.action == EnforcementAction.ESCALATE
        
        # Verify timeline
        mission_timeline = timeline.get_mission_timeline(result.mission_intent.mission_id)
        escalation_events = [e for e in mission_timeline if e.event_type == TimelineEventType.ESCALATION_REQUIRED]
        assert len(escalation_events) == 1


if __name__ == "__main__":
    pytest.main([__file__])
