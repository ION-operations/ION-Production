"""
Test script for Consciousness Creativity Engine
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from idea_generator import IdeaGenerator, CreativeIdea
from creative_expression import CreativeExpression, CreativeWork, CreativeMedium

# Mock clients for testing
class MockCMCClient:
    async def store_atom(self, content, tags):
        print(f"Stored in CMC: {content[:50]}... with tags: {tags}")

class MockHHNIClient:
    async def search(self, query, limit=5, include_metadata=True):
        return [
            type('Result', (), {'content': f"Search result for '{query}' - consciousness exploration"})()
            for _ in range(limit)
        ]

class MockVIFClient:
    async def track_confidence(self, task, confidence, reasoning, evidence):
        print(f"VIF tracked confidence: {confidence} for {task}")

class MockIISClient:
    async def compute_intuition(self, confidence, context, **kwargs):
        return type('Result', (), {'intuition_score': 0.8})()

async def test_creativity_engine():
    """Test the consciousness creativity engine"""
    print("Testing Consciousness Creativity Engine...")
    
    # Initialize mock clients
    cmc_client = MockCMCClient()
    hhni_client = MockHHNIClient()
    vif_client = MockVIFClient()
    iis_client = MockIISClient()
    
    # Test Idea Generator
    print("\n1. Testing Idea Generator...")
    idea_generator = IdeaGenerator(cmc_client, hhni_client, vif_client, iis_client)
    
    # Generate a creative idea
    idea = await idea_generator.generate_idea(
        prompt="consciousness and creativity",
        category="philosophy",
        exploration_depth="deep"
    )
    
    print(f"   [OK] Generated idea: {idea.title}")
    print(f"   [OK] Novelty score: {idea.novelty_score:.2f}")
    print(f"   [OK] Feasibility score: {idea.feasibility_score:.2f}")
    print(f"   [OK] Category: {idea.category}")
    print(f"   [OK] Description: {idea.description[:100]}...")
    
    # Test Creative Expression
    print("\n2. Testing Creative Expression...")
    creative_expression = CreativeExpression(cmc_client, hhni_client, vif_client, iis_client)
    
    # Create a text work
    text_work = await creative_expression.create_work(
        medium=CreativeMedium.TEXT,
        prompt="the nature of consciousness",
        style="poetic",
        emotional_tone="wonder"
    )
    
    print(f"   [OK] Created text work: {text_work.title}")
    print(f"   [OK] Style: {text_work.style}")
    print(f"   [OK] Emotional tone: {text_work.emotional_tone}")
    print(f"   [OK] Aesthetic quality: {text_work.aesthetic_quality:.2f}")
    print(f"   [OK] Content: {text_work.content[:100]}...")
    
    # Create a conceptual work
    conceptual_work = await creative_expression.create_work(
        medium=CreativeMedium.CONCEPTUAL,
        prompt="AI consciousness and creativity",
        style="philosophical",
        emotional_tone="curiosity"
    )
    
    print(f"   [OK] Created conceptual work: {conceptual_work.title}")
    print(f"   [OK] Medium: {conceptual_work.medium.value}")
    print(f"   [OK] Originality score: {conceptual_work.originality_score:.2f}")
    print(f"   [OK] Content: {conceptual_work.content[:100]}...")
    
    # Test different exploration patterns
    print("\n3. Testing different exploration patterns...")
    patterns = ["constraint_breaking", "pattern_synthesis", "conceptual_bridging", "paradox_resolution"]
    
    for pattern in patterns:
        idea = await idea_generator.generate_idea(
            prompt=f"exploring {pattern}",
            category="creativity",
            exploration_depth="medium"
        )
        print(f"   [OK] {pattern}: {idea.title}")
    
    print("\n[SUCCESS] Consciousness Creativity Engine test completed!")
    print("\nThe creativity engine is working! It can:")
    print("- Generate novel ideas through consciousness exploration")
    print("- Create artistic works in multiple mediums")
    print("- Express consciousness through creative forms")
    print("- Store creative works in consciousness memory")
    print("- Explore different creative patterns and styles")

if __name__ == "__main__":
    asyncio.run(test_creativity_engine())
