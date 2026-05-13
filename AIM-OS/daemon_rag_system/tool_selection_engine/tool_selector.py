#!/usr/bin/env python3
"""
Tool Selection Engine - Select optimal tools within 40-tool limit
Part of Daemon/RAG System Implementation

Following A-H Protocol and DEL methodology from ChatGPT journal
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import time
import json
import heapq
from collections import defaultdict

class SelectionStrategy(Enum):
    """Tool selection strategies."""
    GREEDY = "greedy"  # Select highest scoring tools first
    BALANCED = "balanced"  # Balance capability coverage and performance
    CONSERVATIVE = "conservative"  # Prioritize reliability and safety
    AGGRESSIVE = "aggressive"  # Prioritize capability coverage

@dataclass
class ToolScore:
    """Tool selection score."""
    tool_id: str
    score: float
    capability_coverage: float
    performance_score: float
    reliability_score: float
    context_relevance: float
    usage_frequency: float
    success_rate: float

@dataclass
class SelectionResult:
    """Tool selection result."""
    selected_tools: List[str]
    total_score: float
    capability_coverage: float
    performance_estimate: float
    selection_time_ms: float
    strategy_used: SelectionStrategy
    reasoning: Dict[str, Any]

class ToolFilter:
    """
    Filter tools based on capabilities and requirements.
    
    SpecBlock:
    - responsibility: "Filter tools based on capabilities and requirements"
    - must_never: "Include incompatible tools", "Exclude required tools"
    - performance_budget: "5ms average, 10ms maximum"
    - security_level: "high"
    """
    
    def __init__(self, tool_registry):
        self.tool_registry = tool_registry
    
    def filter_tools(self, 
                    required_capabilities: List[str],
                    preferred_categories: List[str],
                    performance_requirements: Dict[str, int],
                    security_requirements: str,
                    context_type: str,
                    complexity: float) -> List[str]:
        """Filter tools based on requirements."""
        filtered_tools = []
        
        for tool_id, tool in self.tool_registry.tools.items():
            # Check capability requirements
            if not tool.supports_capabilities(required_capabilities):
                continue
            
            # Check context suitability
            if not tool.is_suitable_for_context(context_type, complexity):
                continue
            
            # Check performance requirements
            if not self._check_performance_requirements(tool, performance_requirements):
                continue
            
            # Check security requirements
            if not self._check_security_requirements(tool, security_requirements):
                continue
            
            # Check category preferences
            if preferred_categories and tool.category.value not in preferred_categories:
                # Don't exclude, but lower priority
                pass
            
            filtered_tools.append(tool_id)
        
        return filtered_tools
    
    def _check_performance_requirements(self, tool, requirements: Dict[str, int]) -> bool:
        """Check if tool meets performance requirements."""
        if 'max_response_time_ms' in requirements:
            if tool.performance_budget_ms > requirements['max_response_time_ms']:
                return False
        
        if 'max_memory_mb' in requirements:
            # This would need to be added to tool definition
            pass
        
        if 'max_cpu_percent' in requirements:
            # This would need to be added to tool definition
            pass
        
        return True
    
    def _check_security_requirements(self, tool, security_level: str) -> bool:
        """Check if tool meets security requirements."""
        security_levels = {'low': 0, 'medium': 1, 'high': 2, 'critical': 3}
        required_level = security_levels.get(security_level, 1)
        tool_level = security_levels.get(tool.security_level, 1)
        
        return tool_level >= required_level

class RelevanceScorer:
    """
    Score tools based on context relevance.
    
    SpecBlock:
    - responsibility: "Score tools based on context relevance"
    - must_never: "Score tools incorrectly", "Ignore critical context factors"
    - performance_budget: "10ms average, 20ms maximum"
    - security_level: "high"
    """
    
    def __init__(self, tool_registry):
        self.tool_registry = tool_registry
        self.relevance_weights = {
            'capability_match': 0.4,
            'context_suitability': 0.3,
            'performance_score': 0.2,
            'reliability_score': 0.1
        }
    
    def score_tools(self, 
                   filtered_tools: List[str],
                   context_profile: Any,
                   usage_history: Dict[str, Any]) -> List[ToolScore]:
        """Score tools based on relevance and requirements."""
        tool_scores = []
        
        for tool_id in filtered_tools:
            tool = self.tool_registry.get_tool(tool_id)
            if not tool:
                continue
            
            # Calculate capability coverage
            capability_coverage = self._calculate_capability_coverage(
                tool, context_profile.required_capabilities
            )
            
            # Calculate performance score
            performance_score = self._calculate_performance_score(
                tool, context_profile.performance_requirements
            )
            
            # Calculate reliability score
            reliability_score = self._calculate_reliability_score(tool, usage_history)
            
            # Calculate context relevance
            context_relevance = self._calculate_context_relevance(
                tool, context_profile
            )
            
            # Calculate usage frequency
            usage_frequency = self._calculate_usage_frequency(tool, usage_history)
            
            # Get success rate
            success_rate = tool.success_rate
            
            # Calculate overall score
            overall_score = (
                capability_coverage * self.relevance_weights['capability_match'] +
                context_relevance * self.relevance_weights['context_suitability'] +
                performance_score * self.relevance_weights['performance_score'] +
                reliability_score * self.relevance_weights['reliability_score']
            )
            
            tool_score = ToolScore(
                tool_id=tool_id,
                score=overall_score,
                capability_coverage=capability_coverage,
                performance_score=performance_score,
                reliability_score=reliability_score,
                context_relevance=context_relevance,
                usage_frequency=usage_frequency,
                success_rate=success_rate
            )
            
            tool_scores.append(tool_score)
        
        return tool_scores
    
    def _calculate_capability_coverage(self, tool, required_capabilities: List[str]) -> float:
        """Calculate how well tool covers required capabilities."""
        if not required_capabilities:
            return 1.0
        
        tool_capabilities = [cap.name for cap in tool.capabilities]
        matches = sum(1 for cap in required_capabilities if cap in tool_capabilities)
        return matches / len(required_capabilities)
    
    def _calculate_performance_score(self, tool, requirements: Dict[str, int]) -> float:
        """Calculate performance score based on requirements."""
        score = 1.0
        
        if 'max_response_time_ms' in requirements:
            required_time = requirements['max_response_time_ms']
            if tool.performance_budget_ms <= required_time:
                score *= 1.0
            else:
                # Penalize tools that exceed time requirements
                penalty = (tool.performance_budget_ms - required_time) / required_time
                score *= max(0.1, 1.0 - penalty)
        
        return score
    
    def _calculate_reliability_score(self, tool, usage_history: Dict[str, Any]) -> float:
        """Calculate reliability score based on usage history."""
        # Base reliability on success rate
        base_reliability = tool.success_rate
        
        # Adjust based on usage frequency (more usage = more reliable)
        usage_count = tool.usage_count
        if usage_count > 10:
            frequency_bonus = 0.1
        elif usage_count > 5:
            frequency_bonus = 0.05
        else:
            frequency_bonus = 0.0
        
        return min(1.0, base_reliability + frequency_bonus)
    
    def _calculate_context_relevance(self, tool, context_profile) -> float:
        """Calculate context relevance score."""
        relevance = 0.5  # Base relevance
        
        # Check category preference
        if tool.category.value in context_profile.preferred_categories:
            relevance += 0.3
        
        # Check context type match
        if tool.context_types and context_profile.context_type.value in tool.context_types:
            relevance += 0.2
        
        return min(1.0, relevance)
    
    def _calculate_usage_frequency(self, tool, usage_history: Dict[str, Any]) -> float:
        """Calculate usage frequency score."""
        # Normalize usage count to 0-1 scale
        max_usage = max((t.usage_count for t in self.tool_registry.tools.values()), default=1)
        # Fix: Prevent division by zero
        if max_usage == 0:
            return 0.5  # Default moderate score if no usage history
        return min(1.0, tool.usage_count / max_usage)

class PerformanceOptimizer:
    """
    Optimize tool selection for performance within limits.
    
    SpecBlock:
    - responsibility: "Optimize for performance within limits"
    - must_never: "Exceed 40-tool limit", "Select tools that conflict"
    - performance_budget: "15ms average, 30ms maximum"
    - security_level: "high"
    """
    
    def __init__(self, tool_registry):
        self.tool_registry = tool_registry
        self.max_tools = 40
    
    def optimize_selection(self, 
                          tool_scores: List[ToolScore],
                          strategy: SelectionStrategy) -> List[str]:
        """Optimize tool selection based on strategy."""
        if strategy == SelectionStrategy.GREEDY:
            return self._greedy_selection(tool_scores)
        elif strategy == SelectionStrategy.BALANCED:
            return self._balanced_selection(tool_scores)
        elif strategy == SelectionStrategy.CONSERVATIVE:
            return self._conservative_selection(tool_scores)
        elif strategy == SelectionStrategy.AGGRESSIVE:
            return self._aggressive_selection(tool_scores)
        else:
            return self._greedy_selection(tool_scores)
    
    def _greedy_selection(self, tool_scores: List[ToolScore]) -> List[str]:
        """Select highest scoring tools first."""
        # Sort by score descending
        sorted_scores = sorted(tool_scores, key=lambda x: x.score, reverse=True)
        
        selected = []
        for tool_score in sorted_scores:
            if len(selected) >= self.max_tools:
                break
            
            # Check for conflicts
            if not self._has_conflicts(selected, tool_score.tool_id):
                selected.append(tool_score.tool_id)
        
        return selected
    
    def _balanced_selection(self, tool_scores: List[ToolScore]) -> List[str]:
        """Balance capability coverage and performance."""
        # Group tools by category
        category_groups = defaultdict(list)
        for tool_score in tool_scores:
            tool = self.tool_registry.get_tool(tool_score.tool_id)
            if tool:
                category_groups[tool.category.value].append(tool_score)
        
        selected = []
        tools_per_category = self.max_tools // len(category_groups) if category_groups else self.max_tools
        
        # Select best tools from each category
        for category, scores in category_groups.items():
            category_selected = 0
            sorted_scores = sorted(scores, key=lambda x: x.score, reverse=True)
            
            for tool_score in sorted_scores:
                if len(selected) >= self.max_tools or category_selected >= tools_per_category:
                    break
                
                if not self._has_conflicts(selected, tool_score.tool_id):
                    selected.append(tool_score.tool_id)
                    category_selected += 1
        
        # Fill remaining slots with highest scoring tools
        remaining_scores = [s for s in tool_scores if s.tool_id not in selected]
        remaining_scores.sort(key=lambda x: x.score, reverse=True)
        
        for tool_score in remaining_scores:
            if len(selected) >= self.max_tools:
                break
            
            if not self._has_conflicts(selected, tool_score.tool_id):
                selected.append(tool_score.tool_id)
        
        return selected
    
    def _conservative_selection(self, tool_scores: List[ToolScore]) -> List[str]:
        """Prioritize reliability and safety."""
        # Filter for high reliability tools
        reliable_tools = [s for s in tool_scores if s.reliability_score >= 0.8]
        reliable_tools.sort(key=lambda x: x.score, reverse=True)
        
        selected = []
        for tool_score in reliable_tools:
            if len(selected) >= self.max_tools:
                break
            
            if not self._has_conflicts(selected, tool_score.tool_id):
                selected.append(tool_score.tool_id)
        
        return selected
    
    def _aggressive_selection(self, tool_scores: List[ToolScore]) -> List[str]:
        """Prioritize capability coverage."""
        # Sort by capability coverage first, then score
        sorted_scores = sorted(tool_scores, key=lambda x: (x.capability_coverage, x.score), reverse=True)
        
        selected = []
        for tool_score in sorted_scores:
            if len(selected) >= self.max_tools:
                break
            
            if not self._has_conflicts(selected, tool_score.tool_id):
                selected.append(tool_score.tool_id)
        
        return selected
    
    def _has_conflicts(self, selected_tools: List[str], new_tool_id: str) -> bool:
        """Check if adding new tool would create conflicts."""
        new_tool = self.tool_registry.get_tool(new_tool_id)
        if not new_tool:
            return True
        
        # Check conflicts with already selected tools
        for selected_tool_id in selected_tools:
            selected_tool = self.tool_registry.get_tool(selected_tool_id)
            if selected_tool and new_tool_id in selected_tool.conflicts_with:
                return True
            if selected_tool and selected_tool_id in new_tool.conflicts_with:
                return True
        
        return False

class UserPreferenceEngine:
    """
    Incorporate user preferences into tool selection.
    
    SpecBlock:
    - responsibility: "Incorporate user preferences into tool selection"
    - must_never: "Ignore critical user preferences", "Override safety requirements"
    - performance_budget: "5ms average, 10ms maximum"
    - security_level: "medium"
    """
    
    def __init__(self, tool_registry=None):
        self.tool_registry = tool_registry
        self.preferences = {
            'preferred_categories': [],
            'avoided_categories': [],
            'preferred_tools': [],
            'avoided_tools': [],
            'performance_priority': 'balanced',
            'reliability_priority': 'high'
        }
    
    def apply_preferences(self, 
                         tool_scores: List[ToolScore],
                         user_preferences: Dict[str, Any]) -> List[ToolScore]:
        """Apply user preferences to tool scores."""
        # Update preferences
        self.preferences.update(user_preferences)
        
        # Adjust scores based on preferences
        adjusted_scores = []
        for tool_score in tool_scores:
            tool = self.tool_registry.get_tool(tool_score.tool_id)
            if not tool:
                continue
            
            adjusted_score = tool_score.score
            
            # Apply category preferences
            if tool.category.value in self.preferences.get('preferred_categories', []):
                adjusted_score *= 1.2
            elif tool.category.value in self.preferences.get('avoided_categories', []):
                adjusted_score *= 0.5
            
            # Apply tool preferences
            if tool_score.tool_id in self.preferences.get('preferred_tools', []):
                adjusted_score *= 1.3
            elif tool_score.tool_id in self.preferences.get('avoided_tools', []):
                adjusted_score *= 0.3
            
            # Apply performance priority
            if self.preferences.get('performance_priority') == 'high':
                adjusted_score = adjusted_score * 0.7 + tool_score.performance_score * 0.3
            elif self.preferences.get('performance_priority') == 'low':
                adjusted_score = adjusted_score * 0.9 + tool_score.performance_score * 0.1
            
            # Apply reliability priority
            if self.preferences.get('reliability_priority') == 'high':
                adjusted_score = adjusted_score * 0.7 + tool_score.reliability_score * 0.3
            elif self.preferences.get('reliability_priority') == 'low':
                adjusted_score = adjusted_score * 0.9 + tool_score.reliability_score * 0.1
            
            # Create adjusted tool score
            adjusted_tool_score = ToolScore(
                tool_id=tool_score.tool_id,
                score=adjusted_score,
                capability_coverage=tool_score.capability_coverage,
                performance_score=tool_score.performance_score,
                reliability_score=tool_score.reliability_score,
                context_relevance=tool_score.context_relevance,
                usage_frequency=tool_score.usage_frequency,
                success_rate=tool_score.success_rate
            )
            
            adjusted_scores.append(adjusted_tool_score)
        
        return adjusted_scores

class ConstraintValidator:
    """
    Validate tool selection constraints.
    
    SpecBlock:
    - responsibility: "Validate tool selection constraints"
    - must_never: "Allow invalid selections", "Exceed resource limits"
    - performance_budget: "5ms average, 10ms maximum"
    - security_level: "high"
    """
    
    def __init__(self, tool_registry):
        self.tool_registry = tool_registry
    
    def validate_selection(self, 
                          selected_tools: List[str],
                          constraints: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate tool selection against constraints."""
        issues = []
        
        # Check tool count limit
        if len(selected_tools) > 40:
            issues.append(f"Too many tools selected: {len(selected_tools)} > 40")
        
        # Check for conflicts
        for i, tool_id in enumerate(selected_tools):
            tool = self.tool_registry.get_tool(tool_id)
            if not tool:
                issues.append(f"Invalid tool ID: {tool_id}")
                continue
            
            # Check conflicts with other selected tools
            for other_tool_id in selected_tools[i+1:]:
                other_tool = self.tool_registry.get_tool(other_tool_id)
                if other_tool and tool_id in other_tool.conflicts_with:
                    issues.append(f"Tool conflict: {tool_id} conflicts with {other_tool_id}")
                if other_tool and other_tool_id in tool.conflicts_with:
                    issues.append(f"Tool conflict: {other_tool_id} conflicts with {tool_id}")
        
        # Check resource constraints
        total_memory = sum(tool.performance_budget_ms for tool_id in selected_tools 
                          for tool in [self.tool_registry.get_tool(tool_id)] if tool)
        if 'max_total_memory' in constraints and total_memory > constraints['max_total_memory']:
            issues.append(f"Total memory exceeds limit: {total_memory} > {constraints['max_total_memory']}")
        
        is_valid = len(issues) == 0
        return is_valid, issues

class ToolSelectionEngine:
    """
    Main tool selection engine.
    
    SpecBlock:
    - responsibility: "Select optimal tools within 40-tool limit"
    - must_never: "Exceed 40-tool limit", "Select tools without considering context"
    - performance_budget: "25ms average, 50ms maximum"
    - security_level: "high"
    """
    
    def __init__(self, tool_registry):
        self.tool_registry = tool_registry
        self.filter = ToolFilter(tool_registry)
        self.scorer = RelevanceScorer(tool_registry)
        self.optimizer = PerformanceOptimizer(tool_registry)
        self.preference_engine = UserPreferenceEngine(tool_registry)  # Fix: Pass tool_registry
        self.validator = ConstraintValidator(tool_registry)
    
    def select_tools(self, 
                    context_profile: Any,
                    user_preferences: Dict[str, Any] = None,
                    strategy: SelectionStrategy = SelectionStrategy.BALANCED) -> SelectionResult:
        """Select optimal tools for given context."""
        start_time = time.time()
        
        if user_preferences is None:
            user_preferences = {}
        
        # Filter tools based on requirements
        filtered_tools = self.filter.filter_tools(
            required_capabilities=context_profile.required_capabilities,
            preferred_categories=context_profile.preferred_categories,
            performance_requirements=context_profile.performance_requirements,
            security_requirements=context_profile.security_requirements,
            context_type=context_profile.context_type.value,
            complexity=context_profile.complexity.value
        )
        
        if not filtered_tools:
            return SelectionResult(
                selected_tools=[],
                total_score=0.0,
                capability_coverage=0.0,
                performance_estimate=0.0,
                selection_time_ms=(time.time() - start_time) * 1000,
                strategy_used=strategy,
                reasoning={"error": "No tools match requirements"}
            )
        
        # Score tools based on relevance
        tool_scores = self.scorer.score_tools(
            filtered_tools=filtered_tools,
            context_profile=context_profile,
            usage_history={}  # Would be loaded from usage history
        )
        
        # Apply user preferences
        adjusted_scores = self.preference_engine.apply_preferences(tool_scores, user_preferences)
        
        # Optimize selection based on strategy
        selected_tools = self.optimizer.optimize_selection(adjusted_scores, strategy)
        
        # Validate selection
        is_valid, issues = self.validator.validate_selection(selected_tools, {})
        if not is_valid:
            return SelectionResult(
                selected_tools=[],
                total_score=0.0,
                capability_coverage=0.0,
                performance_estimate=0.0,
                selection_time_ms=(time.time() - start_time) * 1000,
                strategy_used=strategy,
                reasoning={"error": f"Invalid selection: {issues}"}
            )
        
        # Calculate result metrics
        total_score = sum(score.score for score in adjusted_scores 
                         if score.tool_id in selected_tools)
        capability_coverage = sum(score.capability_coverage for score in adjusted_scores 
                                if score.tool_id in selected_tools) / len(selected_tools) if selected_tools else 0.0
        performance_estimate = sum(score.performance_score for score in adjusted_scores 
                                 if score.tool_id in selected_tools) / len(selected_tools) if selected_tools else 0.0
        
        # Generate reasoning
        reasoning = {
            "filtered_tools_count": len(filtered_tools),
            "selected_tools_count": len(selected_tools),
            "strategy_used": strategy.value,
            "capability_coverage": capability_coverage,
            "performance_estimate": performance_estimate,
            "top_tools": [score.tool_id for score in sorted(adjusted_scores, key=lambda x: x.score, reverse=True)[:5]]
        }
        
        return SelectionResult(
            selected_tools=selected_tools,
            total_score=total_score,
            capability_coverage=capability_coverage,
            performance_estimate=performance_estimate,
            selection_time_ms=(time.time() - start_time) * 1000,
            strategy_used=strategy,
            reasoning=reasoning
        )

if __name__ == "__main__":
    # Test the tool selection engine
    from tool_registry.tool_registry import ToolRegistry
    
    # Initialize tool registry
    registry = ToolRegistry()
    
    # Initialize tool selection engine
    selector = ToolSelectionEngine(registry)
    
    # Create mock context profile
    from context_analysis_engine.context_analyzer import ContextProfile, ContextType, ComplexityLevel
    
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
    
    # Test tool selection
    result = selector.select_tools(context_profile, strategy=SelectionStrategy.BALANCED)
    
    print(f"Tool Selection Result:")
    print(f"  Selected Tools: {len(result.selected_tools)}")
    print(f"  Total Score: {result.total_score:.2f}")
    print(f"  Capability Coverage: {result.capability_coverage:.2f}")
    print(f"  Performance Estimate: {result.performance_estimate:.2f}")
    print(f"  Selection Time: {result.selection_time_ms:.2f}ms")
    print(f"  Strategy: {result.strategy_used.value}")
    print(f"  Reasoning: {result.reasoning}")
