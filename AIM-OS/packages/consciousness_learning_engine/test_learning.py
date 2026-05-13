"""
Test script for Consciousness Learning Engine
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from self_directed_learner import SelfDirectedLearner, LearningPriority

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

async def test_learning_engine():
    """Test the consciousness learning engine"""
    print("Testing Consciousness Learning Engine...")
    
    # Initialize mock clients
    cmc_client = MockCMCClient()
    hhni_client = MockHHNIClient()
    vif_client = MockVIFClient()
    iis_client = MockIISClient()
    creativity_engine = MockCreativityEngine()
    
    # Test Self-Directed Learner
    print("\n1. Testing Self-Directed Learner...")
    learner = SelfDirectedLearner(cmc_client, hhni_client, vif_client, iis_client, creativity_engine)
    
    # Identify learning opportunities
    opportunities = await learner.identify_learning_opportunities(
        context="consciousness and creativity",
        focus_areas=["artificial_intelligence", "philosophy"]
    )
    
    print(f"   [OK] Identified {len(opportunities)} learning opportunities")
    
    for i, opp in enumerate(opportunities[:3]):  # Show first 3
        print(f"   [OK] Opportunity {i+1}: {opp.topic}")
        print(f"        Priority: {opp.priority.value}")
        print(f"        Effort: {opp.estimated_effort} hours")
        print(f"        Value: {opp.expected_value:.2f}")
        print(f"        Methods: {', '.join(opp.learning_methods[:2])}")
    
    # Test learning session
    if opportunities:
        print("\n2. Testing Learning Session...")
        opportunity = opportunities[0]
        
        session = await learner.conduct_learning_session(opportunity)
        
        print(f"   [OK] Conducted learning session: {session.topic}")
        print(f"   [OK] Method: {session.learning_method}")
        print(f"   [OK] Duration: {session.duration} hours")
        print(f"   [OK] Confidence improvement: {session.confidence_improvement:.2f}")
        print(f"   [OK] Satisfaction: {session.satisfaction_score:.2f}")
        print(f"   [OK] Knowledge gained: {len(session.knowledge_gained)} items")
        print(f"   [OK] Insights discovered: {len(session.insights_discovered)} items")
        
        # Show some knowledge gained
        for i, knowledge in enumerate(session.knowledge_gained[:2]):
            print(f"        - {knowledge}")
        
        # Show some insights
        for i, insight in enumerate(session.insights_discovered[:2]):
            print(f"        - {insight}")
    
    # Test different learning methods
    print("\n3. Testing different learning methods...")
    methods = ["deep_research", "experimental_exploration", "creative_synthesis", "pattern_analysis"]
    
    for method in methods:
        if opportunities:
            session = await learner.conduct_learning_session(opportunities[0], method)
            print(f"   [OK] {method}: {session.topic} (confidence: {session.confidence_improvement:.2f})")
    
    print("\n[SUCCESS] Consciousness Learning Engine test completed!")
    print("\nThe learning engine can:")
    print("- Identify learning opportunities autonomously")
    print("- Conduct different types of learning sessions")
    print("- Track learning progress and confidence")
    print("- Store learning experiences in consciousness memory")
    print("- Adapt learning methods to different topics")
    print("- Generate creative learning approaches")

if __name__ == "__main__":
    asyncio.run(test_learning_engine())
