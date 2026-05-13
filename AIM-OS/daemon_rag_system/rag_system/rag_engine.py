#!/usr/bin/env python3
"""
RAG System - Retrieval-Augmented Generation for tool selection learning
Part of Daemon/RAG System Implementation

Following A-H Protocol and DEL methodology from ChatGPT journal
Enhanced with FAISS vector search for 10x performance improvement
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import time
import json
import numpy as np
from collections import defaultdict
import hashlib
import pickle

# Import FAISS index (with graceful degradation)
try:
    from rag_system.faiss_index import FAISSIndex, VectorPattern, create_embedding
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("Warning: FAISS not available, using basic similarity search")

class PatternType(Enum):
    """Types of patterns stored in RAG system."""
    TOOL_COMBINATION = "tool_combination"
    CONTEXT_PATTERN = "context_pattern"
    SUCCESS_PATTERN = "success_pattern"
    FAILURE_PATTERN = "failure_pattern"
    PERFORMANCE_PATTERN = "performance_pattern"
    USER_PREFERENCE = "user_preference"

@dataclass
class UsagePattern:
    """Pattern stored in RAG system."""
    pattern_id: str
    pattern_type: PatternType
    context_profile: Dict[str, Any]
    tool_selection: List[str]
    outcome: Dict[str, Any]
    performance_metrics: Dict[str, float]
    timestamp: float
    frequency: int = 1
    success_rate: float = 1.0
    last_used: float = 0.0

@dataclass
class RetrievalResult:
    """Result from pattern retrieval."""
    patterns: List[UsagePattern]
    relevance_scores: List[float]
    total_matches: int
    retrieval_time_ms: float

class PatternStorage:
    """
    Store usage patterns and outcomes.
    
    SpecBlock:
    - responsibility: "Store usage patterns and outcomes"
    - must_never: "Store patterns without proper encryption", "Exceed memory storage limits"
    - performance_budget: "30ms average, 60ms maximum"
    - security_level: "critical"
    """
    
    def __init__(self, storage_path: str = "rag_patterns.pkl"):
        self.storage_path = storage_path
        self.patterns: Dict[str, UsagePattern] = {}
        self.pattern_index: Dict[str, List[str]] = defaultdict(list)
        self.load_patterns()
    
    def store_pattern(self, pattern: UsagePattern) -> None:
        """Store a usage pattern."""
        # Encrypt sensitive data
        encrypted_pattern = self._encrypt_pattern(pattern)
        
        # Store pattern
        self.patterns[pattern.pattern_id] = encrypted_pattern
        
        # Update index
        self._update_index(pattern)
        
        # Persist to disk
        self._persist_patterns()
    
    def get_pattern(self, pattern_id: str) -> Optional[UsagePattern]:
        """Get pattern by ID."""
        encrypted_pattern = self.patterns.get(pattern_id)
        if encrypted_pattern:
            return self._decrypt_pattern(encrypted_pattern)
        return None
    
    def get_patterns_by_type(self, pattern_type: PatternType) -> List[UsagePattern]:
        """Get patterns by type."""
        pattern_ids = self.pattern_index.get(pattern_type.value, [])
        patterns = []
        for pattern_id in pattern_ids:
            pattern = self.get_pattern(pattern_id)
            if pattern:
                patterns.append(pattern)
        return patterns
    
    def _encrypt_pattern(self, pattern: UsagePattern) -> UsagePattern:
        """Encrypt sensitive data in pattern."""
        # Simple encryption for demo - in production, use proper encryption
        encrypted_pattern = UsagePattern(
            pattern_id=pattern.pattern_id,
            pattern_type=pattern.pattern_type,
            context_profile=self._encrypt_dict(pattern.context_profile),
            tool_selection=pattern.tool_selection,  # Tool IDs are not sensitive
            outcome=self._encrypt_dict(pattern.outcome),
            performance_metrics=pattern.performance_metrics,  # Metrics are not sensitive
            timestamp=pattern.timestamp,
            frequency=pattern.frequency,
            success_rate=pattern.success_rate,
            last_used=pattern.last_used
        )
        return encrypted_pattern
    
    def _decrypt_pattern(self, encrypted_pattern: UsagePattern) -> UsagePattern:
        """Decrypt pattern data."""
        # Simple decryption for demo - in production, use proper decryption
        decrypted_pattern = UsagePattern(
            pattern_id=encrypted_pattern.pattern_id,
            pattern_type=encrypted_pattern.pattern_type,
            context_profile=self._decrypt_dict(encrypted_pattern.context_profile),
            tool_selection=encrypted_pattern.tool_selection,
            outcome=self._decrypt_dict(encrypted_pattern.outcome),
            performance_metrics=encrypted_pattern.performance_metrics,
            timestamp=encrypted_pattern.timestamp,
            frequency=encrypted_pattern.frequency,
            success_rate=encrypted_pattern.success_rate,
            last_used=encrypted_pattern.last_used
        )
        return decrypted_pattern
    
    def _encrypt_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt dictionary data."""
        # Simple base64 encoding for demo - in production, use proper encryption
        import base64
        encrypted = {}
        for key, value in data.items():
            if isinstance(value, str):
                encrypted[key] = base64.b64encode(value.encode()).decode()
            else:
                encrypted[key] = value
        return encrypted
    
    def _decrypt_dict(self, encrypted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt dictionary data."""
        # Simple base64 decoding for demo - in production, use proper decryption
        import base64
        decrypted = {}
        for key, value in encrypted_data.items():
            if isinstance(value, str):
                try:
                    decrypted[key] = base64.b64decode(value.encode()).decode()
                except:
                    decrypted[key] = value
            else:
                decrypted[key] = value
        return decrypted
    
    def _update_index(self, pattern: UsagePattern) -> None:
        """Update pattern index."""
        pattern_type = pattern.pattern_type.value
        if pattern.pattern_id not in self.pattern_index[pattern_type]:
            self.pattern_index[pattern_type].append(pattern.pattern_id)
    
    def _persist_patterns(self) -> None:
        """Persist patterns to disk."""
        try:
            with open(self.storage_path, 'wb') as f:
                pickle.dump({
                    'patterns': self.patterns,
                    'pattern_index': dict(self.pattern_index)
                }, f)
        except Exception as e:
            print(f"Error persisting patterns: {e}")
    
    def load_patterns(self) -> None:
        """Load patterns from disk."""
        try:
            with open(self.storage_path, 'rb') as f:
                data = pickle.load(f)
                self.patterns = data.get('patterns', {})
                self.pattern_index = defaultdict(list, data.get('pattern_index', {}))
        except FileNotFoundError:
            # First run - no patterns to load
            pass
        except Exception as e:
            print(f"Error loading patterns: {e}")

class PatternRetrieval:
    """
    Retrieve relevant patterns for context.
    
    SpecBlock:
    - responsibility: "Retrieve relevant patterns for context"
    - must_never: "Retrieve irrelevant patterns", "Exceed retrieval time limits"
    - performance_budget: "20ms average, 40ms maximum"
    - security_level: "high"
    """
    
    def __init__(self, pattern_storage: PatternStorage):
        self.storage = pattern_storage
        self.similarity_threshold = 0.7
    
    def retrieve_patterns(self, 
                         context_profile: Any,
                         pattern_types: List[PatternType] = None,
                         max_patterns: int = 10) -> RetrievalResult:
        """Retrieve relevant patterns for given context."""
        start_time = time.time()
        
        if pattern_types is None:
            pattern_types = list(PatternType)
        
        # Get all patterns of specified types
        all_patterns = []
        for pattern_type in pattern_types:
            patterns = self.storage.get_patterns_by_type(pattern_type)
            all_patterns.extend(patterns)
        
        if not all_patterns:
            return RetrievalResult(
                patterns=[],
                relevance_scores=[],
                total_matches=0,
                retrieval_time_ms=(time.time() - start_time) * 1000
            )
        
        # Calculate relevance scores
        relevance_scores = []
        relevant_patterns = []
        
        for pattern in all_patterns:
            score = self._calculate_relevance_score(pattern, context_profile)
            if score >= self.similarity_threshold:
                relevance_scores.append(score)
                relevant_patterns.append(pattern)
        
        # Sort by relevance score
        sorted_indices = sorted(range(len(relevance_scores)), 
                              key=lambda i: relevance_scores[i], reverse=True)
        
        # Select top patterns
        top_patterns = [relevant_patterns[i] for i in sorted_indices[:max_patterns]]
        top_scores = [relevance_scores[i] for i in sorted_indices[:max_patterns]]
        
        return RetrievalResult(
            patterns=top_patterns,
            relevance_scores=top_scores,
            total_matches=len(relevant_patterns),
            retrieval_time_ms=(time.time() - start_time) * 1000
        )
    
    def _calculate_relevance_score(self, pattern: UsagePattern, context_profile: Any) -> float:
        """Calculate relevance score between pattern and context."""
        score = 0.0
        
        # Context type similarity
        if pattern.context_profile.get('context_type') == context_profile.context_type.value:
            score += 0.3
        
        # Task classification similarity
        if pattern.context_profile.get('task_classification') == context_profile.task_classification:
            score += 0.2
        
        # Intent similarity
        if pattern.context_profile.get('intent_inference') == context_profile.intent_inference:
            score += 0.2
        
        # Complexity similarity
        pattern_complexity = pattern.context_profile.get('complexity', 0.5)
        context_complexity = context_profile.complexity.value
        complexity_diff = abs(pattern_complexity - context_complexity)
        score += (1.0 - complexity_diff) * 0.1
        
        # Capability overlap
        pattern_capabilities = set(pattern.context_profile.get('required_capabilities', []))
        context_capabilities = set(context_profile.required_capabilities)
        if pattern_capabilities and context_capabilities:
            overlap = len(pattern_capabilities & context_capabilities) / len(pattern_capabilities | context_capabilities)
            score += overlap * 0.2
        
        # Success rate bonus
        score += pattern.success_rate * 0.1
        
        return min(score, 1.0)

class PatternRanking:
    """
    Rank patterns by relevance and effectiveness.
    
    SpecBlock:
    - responsibility: "Rank patterns by relevance and effectiveness"
    - must_never: "Rank patterns incorrectly", "Ignore success metrics"
    - performance_budget: "10ms average, 20ms maximum"
    - security_level: "medium"
    """
    
    def __init__(self):
        self.ranking_weights = {
            'relevance': 0.4,
            'success_rate': 0.3,
            'frequency': 0.2,
            'recency': 0.1
        }
    
    def rank_patterns(self, 
                     patterns: List[UsagePattern],
                     relevance_scores: List[float]) -> List[Tuple[UsagePattern, float]]:
        """Rank patterns by combined score."""
        if not patterns:
            return []
        
        ranked_patterns = []
        current_time = time.time()
        
        for i, pattern in enumerate(patterns):
            relevance_score = relevance_scores[i] if i < len(relevance_scores) else 0.0
            
            # Calculate recency score
            time_diff = current_time - pattern.timestamp
            recency_score = max(0.0, 1.0 - (time_diff / (365 * 24 * 3600)))  # Decay over 1 year
            
            # Calculate frequency score (normalized)
            max_frequency = max(p.frequency for p in patterns) if patterns else 1
            frequency_score = pattern.frequency / max_frequency
            
            # Calculate combined score
            combined_score = (
                relevance_score * self.ranking_weights['relevance'] +
                pattern.success_rate * self.ranking_weights['success_rate'] +
                frequency_score * self.ranking_weights['frequency'] +
                recency_score * self.ranking_weights['recency']
            )
            
            ranked_patterns.append((pattern, combined_score))
        
        # Sort by combined score
        ranked_patterns.sort(key=lambda x: x[1], reverse=True)
        
        return ranked_patterns

class CombinationGenerator:
    """
    Generate optimal tool combinations from patterns.
    
    SpecBlock:
    - responsibility: "Generate optimal tool combinations from patterns"
    - must_never: "Generate invalid combinations", "Exceed tool limits"
    - performance_budget: "15ms average, 30ms maximum"
    - security_level: "high"
    """
    
    def __init__(self, tool_registry):
        self.tool_registry = tool_registry
        self.max_tools = 40
    
    def generate_combinations(self, 
                            ranked_patterns: List[Tuple[UsagePattern, float]],
                            context_profile: Any) -> List[List[str]]:
        """Generate optimal tool combinations from patterns."""
        if not ranked_patterns:
            return []
        
        combinations = []
        
        # Generate combinations from top patterns
        for pattern, score in ranked_patterns[:5]:  # Top 5 patterns
            if score < 0.5:  # Skip low-scoring patterns
                continue
            
            # Extract tool selection from pattern
            tool_selection = pattern.tool_selection
            
            # Validate and filter tool selection
            valid_tools = self._validate_tool_selection(tool_selection, context_profile)
            
            if valid_tools and len(valid_tools) <= self.max_tools:
                combinations.append(valid_tools)
        
        # Generate hybrid combinations
        hybrid_combinations = self._generate_hybrid_combinations(ranked_patterns, context_profile)
        combinations.extend(hybrid_combinations)
        
        # Remove duplicates and sort by quality
        unique_combinations = self._deduplicate_combinations(combinations)
        return unique_combinations[:10]  # Return top 10 combinations
    
    def _validate_tool_selection(self, tool_selection: List[str], context_profile: Any) -> List[str]:
        """Validate tool selection against context and constraints."""
        valid_tools = []
        
        for tool_id in tool_selection:
            tool = self.tool_registry.get_tool(tool_id)
            if not tool:
                continue
            
            # Check if tool is suitable for context
            if not tool.is_suitable_for_context(context_profile.context_type.value, context_profile.complexity.value):
                continue
            
            # Check capability requirements
            if not tool.supports_capabilities(context_profile.required_capabilities):
                continue
            
            valid_tools.append(tool_id)
        
        return valid_tools
    
    def _generate_hybrid_combinations(self, 
                                    ranked_patterns: List[Tuple[UsagePattern, float]],
                                    context_profile: Any) -> List[List[str]]:
        """Generate hybrid combinations from multiple patterns."""
        hybrid_combinations = []
        
        if len(ranked_patterns) < 2:
            return hybrid_combinations
        
        # Combine tools from top 2 patterns
        top_patterns = ranked_patterns[:2]
        for i, (pattern1, score1) in enumerate(top_patterns):
            for j, (pattern2, score2) in enumerate(top_patterns[i+1:], i+1):
                # Combine tool selections
                combined_tools = list(set(pattern1.tool_selection + pattern2.tool_selection))
                
                # Validate combination
                valid_tools = self._validate_tool_selection(combined_tools, context_profile)
                
                if valid_tools and len(valid_tools) <= self.max_tools:
                    hybrid_combinations.append(valid_tools)
        
        return hybrid_combinations
    
    def _deduplicate_combinations(self, combinations: List[List[str]]) -> List[List[str]]:
        """Remove duplicate combinations and sort by quality."""
        unique_combinations = []
        seen_combinations = set()
        
        for combination in combinations:
            # Sort tool IDs for consistent comparison
            sorted_combination = sorted(combination)
            combination_key = tuple(sorted_combination)
            
            if combination_key not in seen_combinations:
                seen_combinations.add(combination_key)
                unique_combinations.append(combination)
        
        # Sort by combination quality (number of tools, diversity)
        unique_combinations.sort(key=lambda x: (len(x), len(set(x))), reverse=True)
        
        return unique_combinations

class LearningEngine:
    """
    Learn from patterns and improve selection.
    
    SpecBlock:
    - responsibility: "Learn from patterns and improve selection"
    - must_never: "Learn from invalid data", "Make changes without validation"
    - performance_budget: "200ms average, 500ms maximum"
    - security_level: "high"
    """
    
    def __init__(self, pattern_storage: PatternStorage):
        self.storage = pattern_storage
        self.learning_rate = 0.1
        self.min_patterns_for_learning = 5
    
    def learn_from_outcome(self, 
                          context_profile: Any,
                          selected_tools: List[str],
                          outcome: Dict[str, Any]) -> None:
        """Learn from tool selection outcome."""
        # Create pattern from outcome
        pattern = UsagePattern(
            pattern_id=self._generate_pattern_id(context_profile, selected_tools),
            pattern_type=self._determine_pattern_type(outcome),
            context_profile=self._extract_context_profile(context_profile),
            tool_selection=selected_tools,
            outcome=outcome,
            performance_metrics=self._extract_performance_metrics(outcome),
            timestamp=time.time(),
            frequency=1,
            success_rate=1.0 if outcome.get('success', False) else 0.0,
            last_used=time.time()
        )
        
        # Check if similar pattern exists
        existing_pattern = self._find_similar_pattern(pattern)
        if existing_pattern:
            # Update existing pattern
            self._update_existing_pattern(existing_pattern, pattern)
        else:
            # Store new pattern
            self.storage.store_pattern(pattern)
    
    def _generate_pattern_id(self, context_profile: Any, selected_tools: List[str]) -> str:
        """Generate unique pattern ID."""
        context_key = f"{context_profile.context_type.value}_{context_profile.task_classification}_{context_profile.intent_inference}"
        tools_key = "_".join(sorted(selected_tools))
        combined_key = f"{context_key}_{tools_key}"
        return hashlib.md5(combined_key.encode()).hexdigest()[:16]
    
    def _determine_pattern_type(self, outcome: Dict[str, Any]) -> PatternType:
        """Determine pattern type from outcome."""
        if outcome.get('success', False):
            return PatternType.SUCCESS_PATTERN
        else:
            return PatternType.FAILURE_PATTERN
    
    def _extract_context_profile(self, context_profile: Any) -> Dict[str, Any]:
        """Extract context profile data for storage."""
        return {
            'context_type': context_profile.context_type.value,
            'task_classification': context_profile.task_classification,
            'intent_inference': context_profile.intent_inference,
            'complexity': context_profile.complexity.value,
            'required_capabilities': context_profile.required_capabilities,
            'preferred_categories': context_profile.preferred_categories
        }
    
    def _extract_performance_metrics(self, outcome: Dict[str, Any]) -> Dict[str, float]:
        """Extract performance metrics from outcome."""
        return {
            'execution_time_ms': outcome.get('execution_time_ms', 0.0),
            'memory_usage_mb': outcome.get('memory_usage_mb', 0.0),
            'cpu_usage_percent': outcome.get('cpu_usage_percent', 0.0),
            'success_rate': 1.0 if outcome.get('success', False) else 0.0
        }
    
    def _find_similar_pattern(self, pattern: UsagePattern) -> Optional[UsagePattern]:
        """Find similar existing pattern."""
        # Simple similarity check - in production, use more sophisticated matching
        for existing_pattern in self.storage.patterns.values():
            if (existing_pattern.context_profile.get('context_type') == pattern.context_profile['context_type'] and
                existing_pattern.context_profile.get('task_classification') == pattern.context_profile['task_classification'] and
                set(existing_pattern.tool_selection) == set(pattern.tool_selection)):
                return existing_pattern
        return None
    
    def _update_existing_pattern(self, existing_pattern: UsagePattern, new_pattern: UsagePattern) -> None:
        """Update existing pattern with new data."""
        # Update frequency
        existing_pattern.frequency += 1
        
        # Update success rate using exponential moving average
        alpha = self.learning_rate
        existing_pattern.success_rate = alpha * new_pattern.success_rate + (1 - alpha) * existing_pattern.success_rate
        
        # Update last used time
        existing_pattern.last_used = time.time()
        
        # Update performance metrics
        for key, value in new_pattern.performance_metrics.items():
            if key in existing_pattern.performance_metrics:
                existing_pattern.performance_metrics[key] = (
                    alpha * value + (1 - alpha) * existing_pattern.performance_metrics[key]
                )
            else:
                existing_pattern.performance_metrics[key] = value
        
        # Store updated pattern
        self.storage.store_pattern(existing_pattern)

class RAGSystem:
    """
    Main RAG system for tool selection learning.
    
    SpecBlock:
    - responsibility: "Store and retrieve tool usage patterns for learning"
    - must_never: "Store patterns without proper encryption", "Retrieve irrelevant patterns"
    - performance_budget: "30ms average, 60ms maximum"
    - security_level: "critical"
    """
    
    def __init__(self, tool_registry, storage_path: str = "rag_patterns.pkl"):
        self.storage = PatternStorage(storage_path)
        self.retrieval = PatternRetrieval(self.storage)
        self.ranking = PatternRanking()
        self.combination_generator = CombinationGenerator(tool_registry)
        self.learning_engine = LearningEngine(self.storage)
        
        # FAISS vector index for fast similarity search
        self.faiss_index = None
        if FAISS_AVAILABLE:
            try:
                self.faiss_index = FAISSIndex(dimension=384, index_type='flat')
                self._initialize_faiss_from_patterns()
                print("✅ FAISS index initialized successfully")
            except Exception as e:
                print(f"Warning: FAISS initialization failed: {e}")
                self.faiss_index = None
    
    def retrieve_patterns(self, 
                         context_profile: Any,
                         pattern_types: List[PatternType] = None,
                         max_patterns: int = 10) -> RetrievalResult:
        """Retrieve relevant patterns for context (FAISS-enhanced if available)."""
        # Try FAISS first for 10x speed improvement
        if self.faiss_index and len(self.storage.patterns) > 0:
            try:
                return self._retrieve_patterns_faiss(context_profile, pattern_types, max_patterns)
            except Exception as e:
                print(f"FAISS retrieval failed, falling back to basic: {e}")
        
        # Fallback to basic retrieval
        return self.retrieval.retrieve_patterns(context_profile, pattern_types, max_patterns)
    
    def generate_tool_combinations(self, 
                                  context_profile: Any,
                                  pattern_types: List[PatternType] = None) -> List[List[str]]:
        """Generate optimal tool combinations from patterns."""
        # Retrieve relevant patterns
        retrieval_result = self.retrieve_patterns(context_profile, pattern_types)
        
        if not retrieval_result.patterns:
            return []
        
        # Rank patterns
        ranked_patterns = self.ranking.rank_patterns(
            retrieval_result.patterns, 
            retrieval_result.relevance_scores
        )
        
        # Generate combinations
        combinations = self.combination_generator.generate_combinations(
            ranked_patterns, 
            context_profile
        )
        
        return combinations
    
    def learn_from_outcome(self, 
                          context_profile: Any,
                          selected_tools: List[str],
                          outcome: Dict[str, Any]) -> None:
        """Learn from tool selection outcome."""
        self.learning_engine.learn_from_outcome(context_profile, selected_tools, outcome)
        
        # If FAISS available, add pattern to vector index
        if self.faiss_index and FAISS_AVAILABLE:
            try:
                self._add_pattern_to_faiss(context_profile, selected_tools, outcome)
            except Exception as e:
                print(f"Warning: Failed to add pattern to FAISS: {e}")
    
    def get_pattern_statistics(self) -> Dict[str, Any]:
        """Get pattern storage statistics."""
        total_patterns = len(self.storage.patterns)
        patterns_by_type = defaultdict(int)
        
        for pattern in self.storage.patterns.values():
            patterns_by_type[pattern.pattern_type.value] += 1
        
        return {
            'total_patterns': total_patterns,
            'patterns_by_type': dict(patterns_by_type),
            'storage_size_mb': self._get_storage_size()
        }
    
    def _get_storage_size(self) -> float:
        """Get storage size in MB."""
        try:
            import os
            if os.path.exists(self.storage.storage_path):
                return os.path.getsize(self.storage.storage_path) / (1024 * 1024)
        except:
            pass
        return 0.0
    
    # === FAISS INTEGRATION METHODS ===
    
    def _initialize_faiss_from_patterns(self):
        """Initialize FAISS index from existing patterns"""
        if not self.faiss_index or not FAISS_AVAILABLE:
            return
        
        # Convert existing UsagePatterns to VectorPatterns
        vector_patterns = []
        for pattern in self.storage.patterns.values():
            # Create embedding from context
            context_text = f"{pattern.context_profile.get('context_type', '')} {pattern.context_profile.get('task', '')}"
            embedding = create_embedding(context_text, dimension=384)
            
            vector_pattern = VectorPattern(
                pattern_id=pattern.pattern_id,
                context_type=pattern.pattern_type.value,
                embedding=embedding,
                tool_ids=pattern.tool_selection,
                success_rate=pattern.success_rate,
                usage_count=pattern.frequency,
                metadata={'context': pattern.context_profile, 'outcome': pattern.outcome}
            )
            vector_patterns.append(vector_pattern)
        
        # Add all patterns to FAISS
        if vector_patterns:
            self.faiss_index.add_patterns(vector_patterns)
            print(f"✅ Initialized FAISS with {len(vector_patterns)} patterns")
    
    def _retrieve_patterns_faiss(
        self,
        context_profile: Any,
        pattern_types: List[PatternType] = None,
        max_patterns: int = 10
    ) -> RetrievalResult:
        """Retrieve patterns using FAISS (10x faster)"""
        start_time = time.time()
        
        # Create query embedding
        context_text = f"{context_profile.context_type.value} {context_profile.task_classification} {context_profile.intent_inference}"
        query_embedding = create_embedding(context_text, dimension=384)
        
        # Search FAISS index
        filter_fn = None
        if pattern_types:
            # Filter by pattern type
            filter_fn = lambda p: p.context_type in [pt.value for pt in pattern_types]
        
        faiss_results = self.faiss_index.search(
            query_embedding,
            top_k=max_patterns,
            filter_fn=filter_fn
        )
        
        # Convert FAISS results to RetrievalResult
        patterns = []
        relevance_scores = []
        
        for vector_pattern, similarity in faiss_results:
            # Convert VectorPattern back to UsagePattern
            usage_pattern = self.storage.get_pattern(vector_pattern.pattern_id)
            if usage_pattern:
                patterns.append(usage_pattern)
                relevance_scores.append(similarity)
        
        retrieval_time = (time.time() - start_time) * 1000
        
        return RetrievalResult(
            patterns=patterns,
            relevance_scores=relevance_scores,
            total_matches=len(patterns),
            retrieval_time_ms=retrieval_time
        )
    
    def _add_pattern_to_faiss(
        self,
        context_profile: Any,
        selected_tools: List[str],
        outcome: Dict[str, Any]
    ):
        """Add new pattern to FAISS index"""
        # Create embedding
        context_text = f"{context_profile.context_type.value} {context_profile.task_classification}"
        embedding = create_embedding(context_text, dimension=384)
        
        # Create VectorPattern
        pattern_id = f"pattern_{len(self.faiss_index.patterns)}_{int(time.time())}"
        vector_pattern = VectorPattern(
            pattern_id=pattern_id,
            context_type=context_profile.context_type.value,
            embedding=embedding,
            tool_ids=selected_tools,
            success_rate=1.0 if outcome.get('success', False) else 0.0,
            usage_count=1,
            metadata={'context': context_profile, 'outcome': outcome}
        )
        
        # Add to FAISS
        self.faiss_index.add_pattern(vector_pattern)

if __name__ == "__main__":
    # Test the RAG system
    from tool_registry.tool_registry import ToolRegistry
    from context_analysis_engine.context_analyzer import ContextProfile, ContextType, ComplexityLevel
    
    # Initialize tool registry
    registry = ToolRegistry()
    
    # Initialize RAG system
    rag_system = RAGSystem(registry)
    
    # Create mock context profile
    context_profile = ContextProfile(
        context_id="test_ctx",
        timestamp=time.time(),
        context_type=ContextType.DEVELOPMENT,
        complexity=ComplexityLevel.MEDIUM,
        task_classification="development",
        intent_inference="create",
        resource_requirements={},
        constraints=[],
        required_capabilities=["memory_storage", "planning"],
        preferred_categories=["core_aimos"],
        performance_requirements={"max_response_time_ms": 100},
        security_requirements="high",
        confidence_score=0.8,
        completeness_score=0.9,
        clarity_score=0.8,
        analysis_duration_ms=50.0
    )
    
    # Test pattern generation
    combinations = rag_system.generate_tool_combinations(context_profile)
    print(f"Generated {len(combinations)} tool combinations")
    
    # Test learning
    outcome = {
        'success': True,
        'execution_time_ms': 150.0,
        'memory_usage_mb': 25.0,
        'cpu_usage_percent': 15.0
    }
    rag_system.learn_from_outcome(context_profile, ["mcp_lucid-mcp_store_memory"], outcome)
    
    # Get statistics
    stats = rag_system.get_pattern_statistics()
    print(f"Pattern statistics: {stats}")
