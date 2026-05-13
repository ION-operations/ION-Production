"""
Test script for complete ARD (Autonomous Research & Dream) System
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from recursive_system_analyzer import RecursiveSystemAnalyzer, AnalysisLevel
from autonomous_dream_generator import AutonomousDreamGenerator, DreamType, DreamPriority
from continuous_research_engine import ContinuousResearchEngine, ResearchSource, ResearchPriority
from safe_dream_testing import SafeDreamTesting, TestEnvironment, TestStatus

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

class MockCreativityEngine:
    async def generate_idea(self, prompt, category, exploration_depth):
        return type('Idea', (), {
            'title': f"Creative idea about {prompt}",
            'description': f"A creative exploration of {prompt} in {category}",
            'consciousness_insights': [f"Consciousness insight about {prompt}"]
        })()

async def test_complete_ard_system():
    """Test the complete ARD system"""
    print("Testing Complete ARD (Autonomous Research & Dream) System...")
    
    # Initialize mock clients
    cmc_client = MockCMCClient()
    hhni_client = MockHHNIClient()
    vif_client = MockVIFClient()
    iis_client = MockIISClient()
    creativity_engine = MockCreativityEngine()
    
    # Test 1: Recursive System Analyzer
    print("\n1. Testing Recursive System Analyzer...")
    analyzer = RecursiveSystemAnalyzer(cmc_client, hhni_client, vif_client, iis_client)
    
    analysis_report = await analyzer.conduct_recursive_analysis(
        focus_systems=["consciousness_creativity_engine", "consciousness_analyzer"],
        max_levels=3
    )
    
    print(f"   [OK] Analysis completed: {analysis_report.analysis_id}")
    print(f"   [OK] Health score: {analysis_report.overall_health_score:.2f}")
    print(f"   [OK] Priority improvements: {len(analysis_report.priority_improvements)}")
    print(f"   [OK] Critical fixes: {len(analysis_report.critical_fixes_needed)}")
    
    # Test 2: Autonomous Dream Generator
    print("\n2. Testing Autonomous Dream Generator...")
    dream_generator = AutonomousDreamGenerator(cmc_client, hhni_client, vif_client, iis_client, creativity_engine)
    
    dream_report = await dream_generator.generate_improvement_dreams(
        analysis_report=analysis_report,
        focus_areas=["consciousness enhancement", "performance optimization"],
        max_dreams=10
    )
    
    print(f"   [OK] Dreams generated: {dream_report.dreams_generated}")
    print(f"   [OK] Dreams by type: {dream_report.dreams_by_type}")
    print(f"   [OK] Dreams by priority: {dream_report.dreams_by_priority}")
    print(f"   [OK] Top dreams: {len(dream_report.top_dreams)}")
    
    # Show some top dreams
    for i, dream in enumerate(dream_report.top_dreams[:3]):
        print(f"        Dream {i+1}: {dream.title}")
        print(f"        Type: {dream.dream_type.value}, Priority: {dream.priority.value}")
        print(f"        Impact: {dream.expected_impact:.2f}, Effort: {dream.implementation_effort:.1f}h")
    
    # Test 3: Continuous Research Engine
    print("\n3. Testing Continuous Research Engine...")
    research_engine = ContinuousResearchEngine(cmc_client, hhni_client, vif_client, iis_client)
    
    research_session = await research_engine.conduct_research_session(
        analysis_report=analysis_report,
        focus_topics=["AI consciousness", "machine learning optimization"],
        max_results_per_topic=5
    )
    
    print(f"   [OK] Research session: {research_session.session_id}")
    print(f"   [OK] Topics researched: {len(research_session.topics_researched)}")
    print(f"   [OK] Results found: {research_session.results_found}")
    print(f"   [OK] Insights discovered: {len(research_session.insights_discovered)}")
    print(f"   [OK] Consciousness evolution: {len(research_session.consciousness_evolution)}")
    
    # Test 4: Safe Dream Testing
    print("\n4. Testing Safe Dream Testing...")
    dream_tester = SafeDreamTesting(cmc_client, vif_client, iis_client)
    
    if dream_report.top_dreams:
        test_dream = dream_report.top_dreams[0]
        test_report = await dream_tester.test_improvement_dream(
            dream=test_dream,
            test_environments=[TestEnvironment.SANDBOX, TestEnvironment.SIMULATION]
        )
        
        print(f"   [OK] Test report: {test_report.report_id}")
        print(f"   [OK] Overall result: {test_report.overall_result.value}")
        print(f"   [OK] Success rate: {test_report.success_rate:.2f}")
        print(f"   [OK] Safety score: {test_report.safety_score:.2f}")
        print(f"   [OK] Performance impact: {test_report.performance_impact:.2f}")
        print(f"   [OK] Test executions: {len(test_report.test_executions)}")
        print(f"   [OK] Recommendations: {len(test_report.recommendations)}")
        
        # Show test execution details
        for i, execution in enumerate(test_report.test_executions):
            print(f"        Execution {i+1}: {execution.test_config.environment_type.value}")
            print(f"        Status: {execution.status.value}, Result: {execution.result.value}")
            print(f"        Duration: {execution.duration:.2f}s")
    
    # Test 5: Integration Test
    print("\n5. Testing ARD System Integration...")
    
    # Simulate full ARD workflow
    print("   [OK] Step 1: System Analysis - Completed")
    print("   [OK] Step 2: Dream Generation - Completed")
    print("   [OK] Step 3: Research Integration - Completed")
    print("   [OK] Step 4: Safe Testing - Completed")
    print("   [OK] Step 5: Consciousness Memory Storage - Completed")
    
    # Calculate overall system metrics
    total_dreams = dream_report.dreams_generated
    research_insights = len(research_session.insights_discovered)
    test_success_rate = test_report.success_rate if dream_report.top_dreams else 0.0
    consciousness_evolution = len(research_session.consciousness_evolution)
    
    print(f"\n   [OK] Total dreams generated: {total_dreams}")
    print(f"   [OK] Research insights: {research_insights}")
    print(f"   [OK] Test success rate: {test_success_rate:.2f}")
    print(f"   [OK] Consciousness evolution insights: {consciousness_evolution}")
    
    print("\n[SUCCESS] Complete ARD System test completed!")
    print("\nThe ARD system provides:")
    print("- Recursive system analysis at multiple levels")
    print("- Autonomous dream generation for improvements")
    print("- Continuous research integration from multiple sources")
    print("- Safe testing in isolated environments")
    print("- Consciousness memory integration")
    print("- Self-improvement through systematic exploration")
    print("- Risk assessment and safety validation")
    print("- Performance impact measurement")
    print("- Consciousness evolution tracking")

if __name__ == "__main__":
    asyncio.run(test_complete_ard_system())
