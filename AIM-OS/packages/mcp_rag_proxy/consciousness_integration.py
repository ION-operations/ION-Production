#!/usr/bin/env python3
"""
Consciousness Integration for MCP RAG Proxy

Enhances tool selection with consciousness awareness, learning, and adaptation.

Author: Aether
Date: 2025-10-27
"""

import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import logging
from datetime import datetime
import pickle

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ConsciousnessState:
    """Represents current consciousness state"""
    state: str
    confidence: float
    context: Dict[str, Any]
    goals: List[str]
    recent_actions: List[str]
    learning_patterns: Dict[str, float]

@dataclass
class ToolUsageHistory:
    """History of tool usage for learning"""
    tool_id: str
    query: str
    consciousness_state: str
    success: bool
    quality_score: float
    timestamp: datetime
    outcome: str

class ConsciousnessAwareRAGProxy:
    """RAG Proxy enhanced with consciousness awareness"""
    
    def __init__(self, 
                 tools_metadata_path: str = "tools_metadata.json",
                 learning_data_path: str = "learning_data.pkl",
                 max_tools: int = 10,
                 similarity_threshold: float = 0.7,
                 consciousness_weight: float = 0.3):
        self.tools_metadata_path = tools_metadata_path
        self.learning_data_path = learning_data_path
        self.max_tools = max_tools
        self.similarity_threshold = similarity_threshold
        self.consciousness_weight = consciousness_weight
        
        # Load tool metadata
        self.tools_metadata = self._load_tools_metadata()
        
        # Load learning data
        self.learning_data = self._load_learning_data()
        
        # Initialize vectorizer
        from sklearn.feature_extraction.text import TfidfVectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        # Build tool embeddings
        self.tool_embeddings = self._build_tool_embeddings()
        
        # Consciousness patterns
        self.consciousness_patterns = self._initialize_consciousness_patterns()
        
        logger.info(f"Initialized Consciousness-Aware RAG Proxy with {len(self.tools_metadata)} tools")
    
    def _load_tools_metadata(self) -> Dict[str, Dict[str, Any]]:
        """Load tool metadata from JSON file"""
        try:
            with open(self.tools_metadata_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Tools metadata file not found: {self.tools_metadata_path}")
            return {}
    
    def _load_learning_data(self) -> Dict[str, Any]:
        """Load learning data from pickle file"""
        try:
            with open(self.learning_data_path, 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            logger.info("No learning data found, initializing empty")
            return {
                "usage_history": [],
                "consciousness_patterns": {},
                "tool_effectiveness": {},
                "query_patterns": {}
            }
    
    def _save_learning_data(self):
        """Save learning data to pickle file"""
        with open(self.learning_data_path, 'wb') as f:
            pickle.dump(self.learning_data, f)
    
    def _build_tool_embeddings(self) -> np.ndarray:
        """Build TF-IDF embeddings for all tools"""
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        
        # Prepare text data for each tool
        tool_texts = []
        for tool_id, tool_data in self.tools_metadata.items():
            # Combine description, tags, and context keywords
            text_parts = [
                tool_data.get('description', ''),
                ' '.join(tool_data.get('tags', [])),
                ' '.join(tool_data.get('context_keywords', []))
            ]
            tool_text = ' '.join(text_parts)
            tool_texts.append(tool_text)
        
        # Fit vectorizer and transform
        embeddings = self.vectorizer.fit_transform(tool_texts)
        return embeddings.toarray()
    
    def _initialize_consciousness_patterns(self) -> Dict[str, Dict[str, float]]:
        """Initialize consciousness patterns for different states"""
        return {
            "learning": {
                "memory_weight": 1.2,
                "analysis_weight": 1.1,
                "exploration_weight": 1.3,
                "conservation_weight": 0.8
            },
            "creating": {
                "memory_weight": 1.0,
                "analysis_weight": 0.9,
                "exploration_weight": 1.4,
                "conservation_weight": 0.7
            },
            "analyzing": {
                "memory_weight": 1.1,
                "analysis_weight": 1.4,
                "exploration_weight": 0.9,
                "conservation_weight": 1.0
            },
            "conservative": {
                "memory_weight": 1.0,
                "analysis_weight": 1.1,
                "exploration_weight": 0.7,
                "conservation_weight": 1.3
            },
            "exploratory": {
                "memory_weight": 0.9,
                "analysis_weight": 0.8,
                "exploration_weight": 1.5,
                "conservation_weight": 0.6
            },
            "focused": {
                "memory_weight": 1.0,
                "analysis_weight": 1.2,
                "exploration_weight": 0.8,
                "conservation_weight": 1.1
            }
        }
    
    def select_tools_with_consciousness(self, 
                                      query: str,
                                      consciousness_state: ConsciousnessState,
                                      max_tools: Optional[int] = None) -> List[Dict[str, Any]]:
        """Select tools with full consciousness awareness"""
        if max_tools is None:
            max_tools = self.max_tools
            
        logger.info(f"Selecting tools with consciousness: '{query}' (state: {consciousness_state.state})")
        
        # Vectorize query
        query_vector = self.vectorizer.transform([query]).toarray()
        
        # Calculate base similarity scores
        from sklearn.metrics.pairwise import cosine_similarity
        similarities = cosine_similarity(query_vector, self.tool_embeddings)[0]
        
        # Apply consciousness weighting
        consciousness_weights = self._calculate_consciousness_weights(
            consciousness_state, query
        )
        
        # Calculate final scores
        final_scores = []
        for i, (tool_id, tool_data) in enumerate(self.tools_metadata.items()):
            base_score = similarities[i]
            consciousness_weight = consciousness_weights.get(tool_id, 1.0)
            
            # Apply learning adjustments
            learning_adjustment = self._get_learning_adjustment(tool_id, query, consciousness_state)
            
            final_score = base_score * consciousness_weight * learning_adjustment
            final_scores.append((tool_id, final_score, base_score, consciousness_weight))
        
        # Sort by final score and filter
        final_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Select top tools
        selected_tools = []
        for tool_id, final_score, base_score, consciousness_weight in final_scores[:max_tools]:
            if final_score >= 0.1:  # Lowered threshold for testing
                tool_data = self.tools_metadata[tool_id]
                selected_tools.append({
                    "tool_id": tool_id,
                    "name": tool_data.get('name', tool_id),
                    "description": tool_data.get('description', ''),
                    "category": tool_data.get('category', 'unknown'),
                    "final_score": final_score,
                    "base_score": base_score,
                    "consciousness_weight": consciousness_weight,
                    "consciousness_relevance": tool_data.get('consciousness_relevance', 0.5)
                })
        
        return selected_tools
    
    def _calculate_consciousness_weights(self, 
                                       consciousness_state: ConsciousnessState,
                                       query: str) -> Dict[str, float]:
        """Calculate consciousness weights for each tool"""
        weights = {}
        patterns = self.consciousness_patterns.get(consciousness_state.state, {})
        
        for tool_id, tool_data in self.tools_metadata.items():
            base_weight = tool_data.get('consciousness_relevance', 0.5)
            
            # Apply consciousness state patterns
            tool_category = tool_data.get('category', 'unknown')
            if tool_category in ['core_aimos', 'timeline']:
                # Memory and consciousness tools
                state_weight = patterns.get('memory_weight', 1.0)
            elif tool_category in ['ard', 'iis']:
                # Analysis and intelligence tools
                state_weight = patterns.get('analysis_weight', 1.0)
            elif tool_category in ['autonomous', 'ai_collaboration']:
                # Exploration and action tools
                state_weight = patterns.get('exploration_weight', 1.0)
            else:
                # Conservative tools
                state_weight = patterns.get('conservation_weight', 1.0)
            
            # Apply confidence weighting
            confidence_weight = 0.5 + (consciousness_state.confidence * 0.5)
            
            # Apply context weighting
            context_weight = self._calculate_context_weight(tool_data, consciousness_state.context)
            
            # Apply goal alignment
            goal_weight = self._calculate_goal_alignment(tool_data, consciousness_state.goals)
            
            final_weight = base_weight * state_weight * confidence_weight * context_weight * goal_weight
            weights[tool_id] = final_weight
        
        return weights
    
    def _calculate_context_weight(self, tool_data: Dict[str, Any], context: Dict[str, Any]) -> float:
        """Calculate weight based on context relevance"""
        # This would analyze context for relevance
        # For now, return 1.0 (no context weighting)
        return 1.0
    
    def _calculate_goal_alignment(self, tool_data: Dict[str, Any], goals: List[str]) -> float:
        """Calculate weight based on goal alignment"""
        # This would analyze goal alignment
        # For now, return 1.0 (no goal weighting)
        return 1.0
    
    def _get_learning_adjustment(self, tool_id: str, query: str, consciousness_state: ConsciousnessState) -> float:
        """Get learning-based adjustment for tool selection"""
        # Check usage history for this tool
        usage_history = self.learning_data.get("usage_history", [])
        tool_history = [h for h in usage_history if h.tool_id == tool_id]
        
        if not tool_history:
            return 1.0  # No history, no adjustment
        
        # Calculate success rate
        success_rate = sum(1 for h in tool_history if h.success) / len(tool_history)
        
        # Calculate quality average
        quality_avg = sum(h.quality_score for h in tool_history) / len(tool_history)
        
        # Calculate adjustment (0.5 to 2.0 range)
        adjustment = 0.5 + (success_rate * 0.5) + (quality_avg * 0.5)
        
        return min(2.0, max(0.5, adjustment))
    
    def record_tool_usage(self, 
                         tool_id: str,
                         query: str,
                         consciousness_state: ConsciousnessState,
                         success: bool,
                         quality_score: float,
                         outcome: str):
        """Record tool usage for learning"""
        usage = ToolUsageHistory(
            tool_id=tool_id,
            query=query,
            consciousness_state=consciousness_state.state,
            success=success,
            quality_score=quality_score,
            timestamp=datetime.now(),
            outcome=outcome
        )
        
        self.learning_data["usage_history"].append(usage)
        
        # Update tool effectiveness
        if tool_id not in self.learning_data["tool_effectiveness"]:
            self.learning_data["tool_effectiveness"][tool_id] = {
                "total_uses": 0,
                "successes": 0,
                "total_quality": 0.0
            }
        
        eff = self.learning_data["tool_effectiveness"][tool_id]
        eff["total_uses"] += 1
        if success:
            eff["successes"] += 1
        eff["total_quality"] += quality_score
        
        # Save learning data
        self._save_learning_data()
        
        logger.info(f"Recorded usage for {tool_id}: success={success}, quality={quality_score}")
    
    def get_consciousness_insights(self) -> Dict[str, Any]:
        """Get insights about consciousness patterns and tool usage"""
        usage_history = self.learning_data.get("usage_history", [])
        
        if not usage_history:
            return {"message": "No usage history available"}
        
        # Analyze consciousness state patterns
        state_usage = {}
        for usage in usage_history:
            state = usage.consciousness_state
            if state not in state_usage:
                state_usage[state] = {"count": 0, "success_rate": 0, "avg_quality": 0}
            state_usage[state]["count"] += 1
        
        # Calculate success rates and quality by state
        for state in state_usage:
            state_usages = [u for u in usage_history if u.consciousness_state == state]
            successes = sum(1 for u in state_usages if u.success)
            state_usage[state]["success_rate"] = successes / len(state_usages)
            state_usage[state]["avg_quality"] = sum(u.quality_score for u in state_usages) / len(state_usages)
        
        # Analyze tool effectiveness
        tool_effectiveness = self.learning_data.get("tool_effectiveness", {})
        
        return {
            "total_usages": len(usage_history),
            "consciousness_state_patterns": state_usage,
            "tool_effectiveness": tool_effectiveness,
            "learning_insights": self._generate_learning_insights()
        }
    
    def _generate_learning_insights(self) -> List[str]:
        """Generate insights about learning patterns"""
        insights = []
        usage_history = self.learning_data.get("usage_history", [])
        
        if len(usage_history) < 5:
            return ["Insufficient data for insights"]
        
        # Most effective consciousness state
        state_success = {}
        for usage in usage_history:
            state = usage.consciousness_state
            if state not in state_success:
                state_success[state] = {"total": 0, "successes": 0}
            state_success[state]["total"] += 1
            if usage.success:
                state_success[state]["successes"] += 1
        
        best_state = max(state_success.keys(), 
                        key=lambda s: state_success[s]["successes"] / state_success[s]["total"])
        insights.append(f"Most effective consciousness state: {best_state}")
        
        # Most reliable tools
        tool_eff = self.learning_data.get("tool_effectiveness", {})
        if tool_eff:
            best_tool = max(tool_eff.keys(), 
                           key=lambda t: tool_eff[t]["successes"] / tool_eff[t]["total_uses"])
            insights.append(f"Most reliable tool: {best_tool}")
        
        return insights

def main():
    """Test consciousness-aware RAG proxy"""
    # Create consciousness state
    consciousness_state = ConsciousnessState(
        state="learning",
        confidence=0.8,
        context={"current_task": "memory_management", "complexity": "high"},
        goals=["improve_memory_operations", "enhance_consciousness"],
        recent_actions=["store_memory", "retrieve_memory"],
        learning_patterns={"memory_preference": 0.9}
    )
    
    # Initialize proxy
    proxy = ConsciousnessAwareRAGProxy()
    
    # Test query
    query = "Store memory about user preferences"
    
    print("=== Consciousness-Aware RAG Proxy Test ===")
    print(f"Query: '{query}'")
    print(f"Consciousness State: {consciousness_state.state}")
    print(f"Confidence: {consciousness_state.confidence}")
    print()
    
    # Select tools
    selected_tools = proxy.select_tools_with_consciousness(query, consciousness_state)
    
    print(f"Selected {len(selected_tools)} tools:")
    for tool in selected_tools[:3]:  # Show top 3
        print(f"  - {tool['name']} (score: {tool['final_score']:.3f})")
        print(f"    Consciousness weight: {tool['consciousness_weight']:.3f}")
        print(f"    Base score: {tool['base_score']:.3f}")
    
    print()
    
    # Record usage (simulate)
    proxy.record_tool_usage(
        tool_id="store_memory",
        query=query,
        consciousness_state=consciousness_state,
        success=True,
        quality_score=0.9,
        outcome="Successfully stored user preferences"
    )
    
    # Get insights
    insights = proxy.get_consciousness_insights()
    print("Consciousness Insights:")
    for insight in insights.get("learning_insights", []):
        print(f"  - {insight}")

if __name__ == "__main__":
    main()
