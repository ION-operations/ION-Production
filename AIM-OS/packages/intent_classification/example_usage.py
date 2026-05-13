"""
Intent Classification System - Example Usage

Demonstrates how to use the Intent Classification System for classifying
user intents and enforcing behavior controls.
"""

from intent_classification import (
    ClassificationEngine, 
    EnforcementLayer, 
    TimelineIntegration,
    MissionIntent, 
    PrimaryCategory, 
    LifecycleStage, 
    ScopeLevel, 
    ClarityState
)


def main():
    """Demonstrate Intent Classification System usage."""
    
    # Initialize components
    classifier = ClassificationEngine()
    enforcement = EnforcementLayer()
    timeline = TimelineIntegration()
    
    print("🚀 Intent Classification System - Example Usage\n")
    
    # Example 1: New System Design
    print("=" * 60)
    print("Example 1: New System Design")
    print("=" * 60)
    
    intent_text = "Create a new user authentication system with OAuth2 and JWT tokens"
    result = classifier.classify_intent(intent_text)
    
    print(f"Intent: {intent_text}")
    print(f"Classified as: {result.mission_intent.primary_category.value}")
    print(f"Lifecycle Stage: {result.mission_intent.lifecycle_stage.value}")
    print(f"Scope Level: {result.mission_intent.scope_level.value}")
    print(f"Clarity State: {result.mission_intent.clarity_state.value}")
    print(f"Confidence: {result.classification_confidence:.2f}")
    print(f"Complexity: {result.mission_intent.complexity_score:.2f}")
    print(f"Facets: {result.mission_intent.facets}")
    print(f"Allowed Actions: {list(result.mission_intent.allowed_actions)}")
    print(f"Blocked Actions: {list(result.mission_intent.blocked_actions)}")
    
    # Log mission creation
    timeline.log_mission_created(result.mission_intent, result.classification_confidence)
    
    # Test action enforcement
    print(f"\nTesting action enforcement:")
    for action in ["research", "design", "implement", "deploy"]:
        enforcement_result = enforcement.evaluate_action(action, result.mission_intent)
        print(f"  {action}: {enforcement_result.action.value} - {enforcement_result.reason}")
        
        # Log action attempt
        timeline.log_action_attempted(action, result.mission_intent, enforcement_result)
    
    print()
    
    # Example 2: Bug Fix
    print("=" * 60)
    print("Example 2: Bug Fix")
    print("=" * 60)
    
    intent_text = "Fix the login bug that's causing 500 errors"
    result = classifier.classify_intent(intent_text)
    
    print(f"Intent: {intent_text}")
    print(f"Classified as: {result.mission_intent.primary_category.value}")
    print(f"Lifecycle Stage: {result.mission_intent.lifecycle_stage.value}")
    print(f"Scope Level: {result.mission_intent.scope_level.value}")
    print(f"Clarity State: {result.mission_intent.clarity_state.value}")
    print(f"Confidence: {result.classification_confidence:.2f}")
    print(f"Complexity: {result.mission_intent.complexity_score:.2f}")
    print(f"Facets: {result.mission_intent.facets}")
    
    # Log mission creation
    timeline.log_mission_created(result.mission_intent, result.classification_confidence)
    
    # Test action enforcement
    print(f"\nTesting action enforcement:")
    for action in ["research", "implement", "test", "deploy"]:
        enforcement_result = enforcement.evaluate_action(action, result.mission_intent)
        print(f"  {action}: {enforcement_result.action.value} - {enforcement_result.reason}")
    
    print()
    
    # Example 3: Research Probe
    print("=" * 60)
    print("Example 3: Research Probe")
    print("=" * 60)
    
    intent_text = "Research the best authentication methods for our use case"
    result = classifier.classify_intent(intent_text)
    
    print(f"Intent: {intent_text}")
    print(f"Classified as: {result.mission_intent.primary_category.value}")
    print(f"Lifecycle Stage: {result.mission_intent.lifecycle_stage.value}")
    print(f"Scope Level: {result.mission_intent.scope_level.value}")
    print(f"Clarity State: {result.mission_intent.clarity_state.value}")
    print(f"Confidence: {result.classification_confidence:.2f}")
    print(f"Complexity: {result.mission_intent.complexity_score:.2f}")
    print(f"Facets: {result.mission_intent.facets}")
    
    # Log mission creation
    timeline.log_mission_created(result.mission_intent, result.classification_confidence)
    
    # Test action enforcement
    print(f"\nTesting action enforcement:")
    for action in ["research", "analyze", "implement", "deploy"]:
        enforcement_result = enforcement.evaluate_action(action, result.mission_intent)
        print(f"  {action}: {enforcement_result.action.value} - {enforcement_result.reason}")
    
    print()
    
    # Example 4: High Complexity Platform-Wide Change
    print("=" * 60)
    print("Example 4: High Complexity Platform-Wide Change")
    print("=" * 60)
    
    intent_text = "Redesign the entire platform architecture to support microservices and implement advanced security features with zero downtime"
    result = classifier.classify_intent(intent_text)
    
    print(f"Intent: {intent_text}")
    print(f"Classified as: {result.mission_intent.primary_category.value}")
    print(f"Lifecycle Stage: {result.mission_intent.lifecycle_stage.value}")
    print(f"Scope Level: {result.mission_intent.scope_level.value}")
    print(f"Clarity State: {result.mission_intent.clarity_state.value}")
    print(f"Confidence: {result.classification_confidence:.2f}")
    print(f"Complexity: {result.mission_intent.complexity_score:.2f}")
    print(f"Facets: {result.mission_intent.facets}")
    print(f"Risk Level: {result.mission_intent.risk_level}")
    print(f"Blast Radius: {result.mission_intent.blast_radius}")
    print(f"Stop Conditions: {result.mission_intent.stop_conditions}")
    print(f"Escalation Required: {result.mission_intent.requires_escalation()}")
    if result.mission_intent.requires_escalation():
        print(f"Escalation Reason: {result.mission_intent.get_escalation_reason()}")
    
    # Log mission creation
    timeline.log_mission_created(result.mission_intent, result.classification_confidence)
    
    # Test action enforcement
    print(f"\nTesting action enforcement:")
    for action in ["research", "design", "implement", "deploy"]:
        enforcement_result = enforcement.evaluate_action(action, result.mission_intent)
        print(f"  {action}: {enforcement_result.action.value} - {enforcement_result.reason}")
        if enforcement_result.escalation_required:
            print(f"    ⚠️  Escalation Required: {enforcement_result.escalation_reason}")
        if enforcement_result.required_approvals:
            print(f"    📋 Required Approvals: {enforcement_result.required_approvals}")
        if enforcement_result.warnings:
            print(f"    ⚠️  Warnings: {enforcement_result.warnings}")
    
    print()
    
    # Example 5: Low Confidence Intent
    print("=" * 60)
    print("Example 5: Low Confidence Intent")
    print("=" * 60)
    
    intent_text = "I'm not sure what's wrong but something is broken"
    result = classifier.classify_intent(intent_text)
    
    print(f"Intent: {intent_text}")
    print(f"Classified as: {result.mission_intent.primary_category.value}")
    print(f"Lifecycle Stage: {result.mission_intent.lifecycle_stage.value}")
    print(f"Scope Level: {result.mission_intent.scope_level.value}")
    print(f"Clarity State: {result.mission_intent.clarity_state.value}")
    print(f"Confidence: {result.classification_confidence:.2f}")
    print(f"Complexity: {result.mission_intent.complexity_score:.2f}")
    print(f"Escalation Required: {result.mission_intent.requires_escalation()}")
    if result.mission_intent.requires_escalation():
        print(f"Escalation Reason: {result.mission_intent.get_escalation_reason()}")
    
    # Log mission creation
    timeline.log_mission_created(result.mission_intent, result.classification_confidence)
    
    # Test action enforcement
    print(f"\nTesting action enforcement:")
    for action in ["research", "investigate", "implement", "deploy"]:
        enforcement_result = enforcement.evaluate_action(action, result.mission_intent)
        print(f"  {action}: {enforcement_result.action.value} - {enforcement_result.reason}")
        if enforcement_result.escalation_required:
            print(f"    ⚠️  Escalation Required: {enforcement_result.escalation_reason}")
    
    print()
    
    # Show timeline statistics
    print("=" * 60)
    print("Timeline Statistics")
    print("=" * 60)
    
    stats = timeline.get_event_statistics()
    print(f"Total Events: {stats['total_events']}")
    print(f"Missions Tracked: {stats['missions_tracked']}")
    print(f"Event Counts:")
    for event_type, count in stats['event_counts'].items():
        if count > 0:
            print(f"  {event_type.value}: {count}")
    
    print()
    
    # Show recent events
    print("Recent Events:")
    recent_events = timeline.get_recent_events(limit=5)
    for event in recent_events:
        print(f"  {event.timestamp.strftime('%H:%M:%S')} - {event.event_type.value}: {event.action_attempted}")
    
    print("\n✅ Intent Classification System demonstration complete!")


if __name__ == "__main__":
    main()
