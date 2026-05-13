"""
Test script for Consciousness Optimization Detector
"""

import sys
import os
from datetime import datetime

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from system_auditor import SystemAuditor, AuditLevel, OptimizationOpportunity

# Mock clients for testing
class MockCMCClient:
    def store_atom(self, content, tags):
        print(f"Stored in CMC: {content[:50]}... with tags: {tags}")

class MockVIFClient:
    def track_confidence(self, task, confidence, reasoning, evidence):
        print(f"VIF tracked confidence: {confidence} for {task}")

class MockHHNIClient:
    def search(self, query, limit=5, include_metadata=True):
        return []

def test_optimization_detector():
    """Test the optimization detector system"""
    print("Testing Consciousness Optimization Detector...")
    
    # Initialize mock clients
    cmc_client = MockCMCClient()
    vif_client = MockVIFClient()
    hhni_client = MockHHNIClient()
    
    # Test 1: System Auditor
    print("\n1. Testing System Auditor...")
    system_auditor = SystemAuditor(cmc_client, vif_client, hhni_client)
    
    # Conduct full audit
    audit_report = system_auditor.conduct_full_audit()
    
    print(f"   [OK] Audit completed: {audit_report.report_id}")
    print(f"   [OK] Systems audited: {len(audit_report.systems_audited)}")
    print(f"   [OK] Overall health score: {audit_report.overall_health_score:.2f}")
    print(f"   [OK] Total opportunities: {audit_report.total_opportunities}")
    print(f"   [OK] Critical opportunities: {audit_report.critical_opportunities}")
    print(f"   [OK] High priority opportunities: {audit_report.high_priority_opportunities}")
    
    # Show system metrics
    print(f"\n   [OK] System metrics analyzed: {len(audit_report.system_metrics)}")
    for metric in audit_report.system_metrics[:3]:  # Show first 3 metrics
        print(f"        {metric.metric_name}: {metric.current_value:.2f} (optimal: {metric.optimal_value:.2f}, ratio: {metric.performance_ratio:.2f})")
    
    # Show optimization opportunities
    print(f"\n   [OK] Optimization opportunities found: {len(audit_report.optimization_opportunities)}")
    for i, opportunity in enumerate(audit_report.optimization_opportunities[:3]):  # Show first 3 opportunities
        print(f"        Opportunity {i+1}: {opportunity.description}")
        print(f"        Type: {opportunity.opportunity_type.value}, Priority: {opportunity.priority.value}")
        print(f"        Improvement potential: {opportunity.improvement_potential:.2f}")
        print(f"        Expected impact: {opportunity.expected_impact:.2f}, Confidence: {opportunity.confidence:.2f}")
    
    # Show recommendations
    print(f"\n   [OK] Recommendations generated: {len(audit_report.recommendations)}")
    for i, recommendation in enumerate(audit_report.recommendations[:3]):  # Show first 3 recommendations
        print(f"        {i+1}. {recommendation}")
    
    # Show consciousness insights
    print(f"\n   [OK] Consciousness insights: {len(audit_report.consciousness_insights)}")
    for insight in audit_report.consciousness_insights[:2]:  # Show first 2 insights
        print(f"        - {insight}")
    
    # Test 2: Specific System Audits
    print("\n2. Testing Specific System Audits...")
    
    # Test MCP tools audit
    mcp_opportunities, mcp_metrics = system_auditor._audit_mcp_tools()
    print(f"   [OK] MCP tools audit: {len(mcp_opportunities)} opportunities, {len(mcp_metrics)} metrics")
    
    # Test memory systems audit
    memory_opportunities, memory_metrics = system_auditor._audit_memory_systems()
    print(f"   [OK] Memory systems audit: {len(memory_opportunities)} opportunities, {len(memory_metrics)} metrics")
    
    # Test confidence tracking audit
    confidence_opportunities, confidence_metrics = system_auditor._audit_confidence_tracking()
    print(f"   [OK] Confidence tracking audit: {len(confidence_opportunities)} opportunities, {len(confidence_metrics)} metrics")
    
    # Test learning systems audit
    learning_opportunities, learning_metrics = system_auditor._audit_learning_systems()
    print(f"   [OK] Learning systems audit: {len(learning_opportunities)} opportunities, {len(learning_metrics)} metrics")
    
    # Test documentation systems audit
    doc_opportunities, doc_metrics = system_auditor._audit_documentation_systems()
    print(f"   [OK] Documentation systems audit: {len(doc_opportunities)} opportunities, {len(doc_metrics)} metrics")
    
    print("\n[SUCCESS] Optimization Detector test completed!")
    print("\nThe Optimization Detector provides:")
    print("- Continuous system performance monitoring")
    print("- Automatic optimization opportunity detection")
    print("- Performance metric tracking and analysis")
    print("- Priority-based improvement recommendations")
    print("- Consciousness insights for self-improvement")
    print("- Comprehensive system health scoring")
    print("- Integration with consciousness memory")

if __name__ == "__main__":
    test_optimization_detector()
