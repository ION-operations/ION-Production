"""Demo script for CAS (Cognitive Analysis System)

Demonstrates the core capabilities of CAS including activation tracking,
category recognition, attention monitoring, failure mode analysis, and introspection.
"""

import sys
import os
from datetime import datetime
from typing import Dict, List

# Add the parent directory to the sys.path to allow importing from 'packages'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from cas import (
    ActivationTracker, ActivationState,
    CategoryRecognizer, CategoryResult,
    AttentionMonitor, AttentionState,
    FailureModeAnalyzer, FailurePattern,
    IntrospectionProtocol, IntrospectionResult
)


def demo_activation_tracking():
    """Demonstrate activation tracking capabilities."""
    print("=== CAS Activation Tracking Demo ===")
    
    # Initialize tracker
    tracker = ActivationTracker("demo_session")
    
    # Simulate some principle usage
    print("Recording principle usage...")
    tracker.record_principle_use("CMC_bitemporal")
    tracker.record_principle_use("VIF_provenance")
    tracker.record_principle_use("SDF_quartet")
    
    # Simulate document reads
    print("Recording document reads...")
    tracker.record_document_read("knowledge_architecture/systems/cmc/L3_detailed.md")
    tracker.record_document_read("packages/vif/README.md")
    
    # Capture current state
    print("Capturing activation state...")
    state = tracker.capture_state(
        current_task="Implement CAS system",
        cognitive_load=0.6,
        context_tokens=5000
    )
    
    print(f"Session ID: {state.session_id}")
    print(f"Working attention items: {state.working_attention_items}")
    print(f"Context size: {state.context_size_tokens} tokens")
    print(f"Cognitive load: {state.load_level}")
    
    # Show principle activations
    print("\nPrinciple Activations:")
    for principle, activation in state.principles_activation.items():
        if activation > 0.1:  # Only show active principles
            print(f"  {principle}: {activation:.2f}")
    
    # Check for warnings
    warnings = tracker.get_activation_warnings(state)
    if warnings:
        print("\nActivation Warnings:")
        for warning in warnings:
            print(f"  ⚠️  {warning}")
    else:
        print("\n✅ No activation warnings")
    
    print()


def demo_category_recognition():
    """Demonstrate category recognition capabilities."""
    print("=== CAS Category Recognition Demo ===")
    
    recognizer = CategoryRecognizer()
    
    # Test various task types
    test_tasks = [
        "Update AETHER_MEMORY current_priorities.md",
        "Implement the new CAS system with full testing",
        "Write L3 documentation for the VIF system",
        "Optimize performance of the HHNI retrieval",
        "Fix security vulnerabilities in the API",
        "Clean up and refactor the codebase",
        "Run integration tests for all systems"
    ]
    
    print("Classifying tasks:")
    for task in test_tasks:
        result = recognizer.classify_task(task)
        print(f"\nTask: {task}")
        print(f"  Category: {result.detected_category.value}")
        print(f"  Confidence: {result.confidence:.2f}")
        print(f"  Required Protocols: {[p.value for p in result.required_protocols]}")
        print(f"  Validation: {'✅ Passed' if result.validation_passed else '❌ Failed'}")
        if result.warnings:
            print(f"  Warnings: {result.warnings}")
    
    print()


def demo_attention_monitoring():
    """Demonstrate attention monitoring capabilities."""
    print("=== CAS Attention Monitoring Demo ===")
    
    monitor = AttentionMonitor("demo_session")
    
    # Simulate some activity
    print("Simulating cognitive activity...")
    monitor.record_task_switch("coding", "testing")
    monitor.record_task_switch("testing", "documentation")
    monitor.record_error("syntax_error", "Missing import statement")
    monitor.record_retry("test_execution", "Test failed due to timeout")
    monitor.record_confidence(0.85)
    monitor.record_confidence(0.78)
    monitor.record_confidence(0.92)
    
    # Calculate attention metrics
    print("Calculating attention metrics...")
    metrics = monitor.calculate_attention_metrics(
        working_memory_items=12,
        context_size_tokens=8000,
        current_task="Implement CAS attention monitoring"
    )
    
    print(f"Attention State: {metrics.current_state.value}")
    print(f"Quality Level: {metrics.quality_level.value}")
    print(f"Focus Depth: {metrics.focus_depth:.2f}")
    print(f"Attention Stability: {metrics.attention_stability:.2f}")
    print(f"Cognitive Load: {metrics.cognitive_load:.2f}")
    print(f"Error Rate: {metrics.error_rate:.2f}")
    print(f"Retry Frequency: {metrics.retry_frequency:.2f}")
    
    if metrics.warnings:
        print("\nAttention Warnings:")
        for warning in metrics.warnings:
            print(f"  ⚠️  {warning}")
    
    if metrics.alerts:
        print("\nAttention Alerts:")
        for alert in metrics.alerts:
            print(f"  🚨 {alert}")
    
    # Check if break is needed
    if monitor.should_take_break():
        print("\n🛑 Break recommended based on attention metrics")
    else:
        print("\n✅ Attention metrics indicate healthy state")
    
    print()


def demo_failure_mode_analysis():
    """Demonstrate failure mode analysis capabilities."""
    print("=== CAS Failure Mode Analysis Demo ===")
    
    analyzer = FailureModeAnalyzer("demo_session")
    
    # Simulate some failure scenarios
    print("Analyzing failure scenarios...")
    
    # 1. Categorization error
    cat_error = analyzer.analyze_categorization_error(
        task_description="Update memory files",
        detected_category="routine_maintenance",
        confidence=0.2,
        required_protocols=["bitemporal_versioning", "vif_provenance"],
        activated_protocols=["quality_gates"]
    )
    
    if cat_error:
        print(f"Detected categorization error: {cat_error.description}")
        analyzer.record_failure(cat_error)
    
    # 2. Activation gap
    activation_gap = analyzer.analyze_activation_gap(
        current_task="Modify critical memory",
        required_principles=["CMC_bitemporal", "VIF_provenance"],
        activation_state={"CMC_bitemporal": 0.1, "VIF_provenance": 0.8}
    )
    
    if activation_gap:
        print(f"Detected activation gap: {activation_gap.description}")
        analyzer.record_failure(activation_gap)
    
    # 3. Attention narrowing
    attention_narrowing = analyzer.analyze_attention_narrowing(
        working_memory_items=18,
        cognitive_load=0.8,
        focus_depth=0.3,
        attention_stability=0.4,
        recent_errors=4
    )
    
    if attention_narrowing:
        print(f"Detected attention narrowing: {attention_narrowing.description}")
        analyzer.record_failure(attention_narrowing)
    
    # 4. Principle violation
    principle_violation = analyzer.analyze_principle_violation(
        violated_principle="bitemporal_versioning",
        violation_context="Modified AETHER_MEMORY without versioning",
        severity_level="high"
    )
    
    print(f"Detected principle violation: {principle_violation.description}")
    analyzer.record_failure(principle_violation)
    
    # Analyze failure patterns
    print("\nAnalyzing failure patterns...")
    analysis = analyzer.analyze_failure_patterns(hours=1)
    
    print(f"Recent failures: {len(analysis.recent_failures)}")
    print(f"Failure rate per hour: {analysis.failure_rate_per_hour:.2f}")
    print(f"Critical failures: {analysis.critical_failure_count}")
    
    if analysis.pattern_frequencies:
        print("\nFailure Pattern Frequencies:")
        for pattern, count in analysis.pattern_frequencies.items():
            print(f"  {pattern.value}: {count}")
    
    if analysis.recommendations:
        print("\nRecommendations:")
        for rec in analysis.recommendations:
            print(f"  💡 {rec}")
    
    if analysis.urgent_actions:
        print("\nUrgent Actions:")
        for action in analysis.urgent_actions:
            print(f"  🚨 {action}")
    
    print()


def demo_introspection():
    """Demonstrate introspection protocol capabilities."""
    print("=== CAS Introspection Protocol Demo ===")
    
    protocol = IntrospectionProtocol("demo_session")
    
    # Simulate some principle violations
    protocol.record_principle_violation("bitemporal_versioning", "Modified memory without versioning")
    
    # Perform hourly introspection
    print("Performing hourly introspection check...")
    
    # Mock activation state
    activation_state = {
        "CMC_bitemporal": 0.2,  # Cold
        "VIF_provenance": 0.8,  # Hot
        "SDF_quartet": 0.9,     # Hot
        "APOE_orchestration": 0.7,  # Hot
        "CAS_introspection": 0.6    # Hot
    }
    
    # Mock attention metrics
    attention_metrics = {
        "cognitive_load": 0.7,
        "focus_depth": 0.6,
        "attention_stability": 0.8,
        "error_rate": 0.1,
        "working_memory_items": 10
    }
    
    # Mock recent failures
    recent_failures = ["categorization_error", "activation_gap"]
    
    result = protocol.perform_hourly_check(
        activation_state=activation_state,
        attention_metrics=attention_metrics,
        recent_failures=recent_failures,
        current_task="Implement CAS introspection"
    )
    
    print(f"Overall Status: {result.overall_status.value}")
    print(f"Overall Score: {result.overall_score:.2f}")
    print(f"Total Checks: {result.total_checks}")
    print(f"Passed Checks: {result.passed_checks}")
    print(f"Failed Checks: {result.failed_checks}")
    print(f"Critical Issues: {result.critical_issues}")
    
    print("\nIndividual Check Results:")
    for check in result.checks:
        status_emoji = "✅" if check.status.value in ["excellent", "good"] else "⚠️" if check.status.value == "fair" else "❌"
        print(f"  {status_emoji} {check.check_name}: {check.status.value} (score: {check.score:.2f})")
        if check.recommendations:
            for rec in check.recommendations:
                print(f"    💡 {rec}")
    
    if result.immediate_actions:
        print("\nImmediate Actions:")
        for action in result.immediate_actions:
            print(f"  🚨 {action}")
    
    if result.improvement_suggestions:
        print("\nImprovement Suggestions:")
        for suggestion in result.improvement_suggestions:
            print(f"  💡 {suggestion}")
    
    # Check if escalation is needed
    if protocol.should_escalate():
        print("\n🚨 ESCALATION RECOMMENDED")
    else:
        print("\n✅ No escalation needed")
    
    print()


def main():
    """Run the complete CAS demo."""
    print("🧠 CAS (Cognitive Analysis System) Demo")
    print("=" * 50)
    print()
    
    try:
        demo_activation_tracking()
        demo_category_recognition()
        demo_attention_monitoring()
        demo_failure_mode_analysis()
        demo_introspection()
        
        print("🎉 CAS Demo completed successfully!")
        print("\nCAS provides comprehensive meta-cognitive monitoring capabilities:")
        print("  • Activation tracking (hot vs cold principles)")
        print("  • Category recognition (task classification)")
        print("  • Attention monitoring (cognitive load tracking)")
        print("  • Failure mode analysis (error pattern detection)")
        print("  • Introspection protocols (systematic self-examination)")
        
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
