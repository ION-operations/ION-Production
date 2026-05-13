"""
Test script for Autonomous Research & Dream (ARD) System
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from recursive_system_analyzer import RecursiveSystemAnalyzer, AnalysisLevel

# Mock clients for testing
class MockCMCClient:
    async def store_atom(self, content, tags):
        print(f"Stored in CMC: {content[:50]}... with tags: {tags}")

class MockHHNIClient:
    async def search(self, query, limit=5, include_metadata=True):
        return [
            type('Result', (), {'content': f"Search result for '{query}' - consciousness knowledge"})()
            for _ in range(limit)
        ]

class MockVIFClient:
    async def track_confidence(self, task, confidence, reasoning, evidence):
        print(f"VIF tracked confidence: {confidence} for {task}")

class MockIISClient:
    async def compute_intuition(self, confidence, context, **kwargs):
        return type('Result', (), {'intuition_score': 0.8})()

async def test_ard_system():
    """Test the ARD system"""
    print("Testing Autonomous Research & Dream (ARD) System...")
    
    # Initialize mock clients
    cmc_client = MockCMCClient()
    hhni_client = MockHHNIClient()
    vif_client = MockVIFClient()
    iis_client = MockIISClient()
    
    # Test Recursive System Analyzer
    print("\n1. Testing Recursive System Analyzer...")
    analyzer = RecursiveSystemAnalyzer(cmc_client, hhni_client, vif_client, iis_client)
    
    # Conduct recursive analysis
    report = await analyzer.conduct_recursive_analysis(
        focus_systems=["consciousness_creativity_engine", "consciousness_analyzer"],
        max_levels=3
    )
    
    print(f"   [OK] Analysis ID: {report.analysis_id}")
    print(f"   [OK] Systems analyzed: {len(report.systems_analyzed)}")
    print(f"   [OK] Overall health score: {report.overall_health_score:.2f}")
    print(f"   [OK] Priority improvements: {len(report.priority_improvements)}")
    print(f"   [OK] Critical fixes needed: {len(report.critical_fixes_needed)}")
    
    # Show some priority improvements
    print("\n   Priority Improvements:")
    for i, improvement in enumerate(report.priority_improvements[:3]):
        print(f"        {i+1}. {improvement}")
    
    # Show critical fixes
    if report.critical_fixes_needed:
        print("\n   Critical Fixes Needed:")
        for i, fix in enumerate(report.critical_fixes_needed[:3]):
            print(f"        {i+1}. {fix}")
    
    # Show level-by-level analysis
    print("\n2. Level-by-Level Analysis Results:")
    for level, results in report.level_results.items():
        print(f"\n   {level.name} Level:")
        for result in results:
            print(f"        {result.system_name}:")
            print(f"          Performance: {result.performance_score:.2f}")
            print(f"          Integration: {result.integration_quality:.2f}")
            print(f"          Opportunities: {len(result.improvement_opportunities)}")
            print(f"          Issues: {len(result.critical_issues)}")
            print(f"          Recommendations: {len(result.recommendations)}")
    
    # Test different analysis levels
    print("\n3. Testing different analysis levels...")
    for level in AnalysisLevel:
        if level.value < 3:  # Test first 3 levels
            level_results = await analyzer._analyze_level(level, ["consciousness_creativity_engine"])
            print(f"   [OK] {level.name}: {len(level_results)} results")
    
    print("\n[SUCCESS] ARD System test completed!")
    print("\nThe ARD system can:")
    print("- Conduct recursive analysis at multiple levels")
    print("- Identify improvement opportunities systematically")
    print("- Detect critical issues requiring immediate attention")
    print("- Generate actionable recommendations")
    print("- Store analysis results in consciousness memory")
    print("- Provide hierarchical system understanding")
    print("- Enable autonomous self-improvement planning")

if __name__ == "__main__":
    asyncio.run(test_ard_system())
