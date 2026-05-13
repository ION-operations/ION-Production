#!/usr/bin/env python3
"""
Learning System - Learn from tool usage patterns and improve selection
Part of Daemon/RAG System Implementation

Following A-H Protocol and DEL methodology from ChatGPT journal
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import time
import json
import numpy as np
from collections import defaultdict, deque
import threading
import queue

class LearningPhase(Enum):
    """Learning phases."""
    EXPLORATION = "exploration"
    EXPLOITATION = "exploitation"
    ADAPTATION = "adaptation"
    CONSOLIDATION = "consolidation"

class LearningMetric(Enum):
    """Learning metrics."""
    ACCURACY = "accuracy"
    EFFICIENCY = "efficiency"
    RELIABILITY = "reliability"
    ADAPTABILITY = "adaptability"
    CONSISTENCY = "consistency"

@dataclass
class LearningData:
    """Learning data point."""
    context_profile: Dict[str, Any]
    selected_tools: List[str]
    outcome: Dict[str, Any]
    performance_metrics: Dict[str, float]
    timestamp: float
    learning_phase: LearningPhase

@dataclass
class LearningInsight:
    """Learning insight."""
    insight_id: str
    insight_type: str
    description: str
    confidence: float
    evidence: List[Dict[str, Any]]
    timestamp: float
    impact_score: float

class PatternLearner:
    """
    Learn patterns from usage data.
    
    SpecBlock:
    - responsibility: "Learn patterns from usage data"
    - must_never: "Learn from invalid data", "Make changes without validation"
    - performance_budget: "50ms average, 100ms maximum"
    - security_level: "high"
    """
    
    def __init__(self, rag_system):
        self.rag_system = rag_system
        self.learning_data: deque = deque(maxlen=1000)
        self.pattern_frequency: Dict[str, int] = defaultdict(int)
        self.success_patterns: Dict[str, float] = defaultdict(float)
        self.failure_patterns: Dict[str, float] = defaultdict(float)
    
    def learn_from_data(self, learning_data: LearningData) -> None:
        """Learn from learning data."""
        # Store learning data
        self.learning_data.append(learning_data)
        
        # Extract pattern key
        pattern_key = self._extract_pattern_key(learning_data)
        
        # Update pattern frequency
        self.pattern_frequency[pattern_key] += 1
        
        # Update success/failure patterns
        if learning_data.outcome.get('success', False):
            self.success_patterns[pattern_key] += 1
        else:
            self.failure_patterns[pattern_key] += 1
        
        # Learn in RAG system
        self.rag_system.learn_from_outcome(
            learning_data.context_profile,
            learning_data.selected_tools,
            learning_data.outcome
        )
    
    def _extract_pattern_key(self, learning_data: LearningData) -> str:
        """Extract pattern key from learning data."""
        context = learning_data.context_profile
        tools = sorted(learning_data.selected_tools)
        
        key_parts = [
            context.get('context_type', 'unknown'),
            context.get('task_classification', 'unknown'),
            context.get('intent_inference', 'unknown'),
            str(len(tools)),
            '_'.join(tools[:3])  # First 3 tools for key
        ]
        
        return '|'.join(key_parts)
    
    def get_pattern_success_rate(self, pattern_key: str) -> float:
        """Get success rate for a pattern."""
        total_occurrences = self.pattern_frequency.get(pattern_key, 0)
        if total_occurrences == 0:
            return 0.0
        
        success_count = self.success_patterns.get(pattern_key, 0)
        return success_count / total_occurrences
    
    def get_learning_insights(self) -> List[LearningInsight]:
        """Get learning insights from patterns."""
        insights = []
        
        # Analyze pattern success rates
        for pattern_key in self.pattern_frequency:
            success_rate = self.get_pattern_success_rate(pattern_key)
            frequency = self.pattern_frequency[pattern_key]
            
            if frequency >= 3:  # Only consider patterns with sufficient data
                if success_rate >= 0.8:
                    insight = LearningInsight(
                        insight_id=f"success_pattern_{int(time.time())}",
                        insight_type="success_pattern",
                        description=f"Pattern '{pattern_key}' has high success rate: {success_rate:.2%}",
                        confidence=min(success_rate, 1.0),
                        evidence=[{"pattern_key": pattern_key, "success_rate": success_rate, "frequency": frequency}],
                        timestamp=time.time(),
                        impact_score=success_rate * frequency
                    )
                    insights.append(insight)
                elif success_rate <= 0.3:
                    insight = LearningInsight(
                        insight_id=f"failure_pattern_{int(time.time())}",
                        insight_type="failure_pattern",
                        description=f"Pattern '{pattern_key}' has low success rate: {success_rate:.2%}",
                        confidence=1.0 - success_rate,
                        evidence=[{"pattern_key": pattern_key, "success_rate": success_rate, "frequency": frequency}],
                        timestamp=time.time(),
                        impact_score=(1.0 - success_rate) * frequency
                    )
                    insights.append(insight)
        
        return insights

class AdaptiveLearner:
    """
    Adaptive learning based on performance feedback.
    
    SpecBlock:
    - responsibility: "Adapt learning based on performance feedback"
    - must_never: "Adapt without sufficient data", "Make harmful adaptations"
    - performance_budget: "30ms average, 60ms maximum"
    - security_level: "high"
    """
    
    def __init__(self):
        self.learning_rate = 0.1
        self.adaptation_threshold = 0.1
        self.performance_history: deque = deque(maxlen=100)
        self.adaptation_history: List[Dict[str, Any]] = []
    
    def adapt_learning(self, performance_metrics: Dict[str, float]) -> Dict[str, Any]:
        """Adapt learning based on performance metrics."""
        # Store performance metrics
        self.performance_history.append({
            'timestamp': time.time(),
            'metrics': performance_metrics
        })
        
        # Calculate performance trend
        if len(self.performance_history) < 10:
            return {'adaptation': 'insufficient_data'}
        
        # Analyze recent performance
        recent_performance = self._analyze_recent_performance()
        
        # Determine if adaptation is needed
        adaptation_needed = self._should_adapt(recent_performance)
        
        if adaptation_needed:
            adaptation = self._perform_adaptation(recent_performance)
            self.adaptation_history.append(adaptation)
            return adaptation
        else:
            return {'adaptation': 'no_change_needed'}
    
    def _analyze_recent_performance(self) -> Dict[str, Any]:
        """Analyze recent performance trends."""
        if len(self.performance_history) < 10:
            return {}
        
        recent_data = list(self.performance_history)[-10:]
        
        # Calculate trends for each metric
        trends = {}
        for metric_name in recent_data[0]['metrics']:
            values = [data['metrics'][metric_name] for data in recent_data]
            trend = self._calculate_trend(values)
            trends[metric_name] = trend
        
        return {
            'trends': trends,
            'average_performance': {
                metric: np.mean([data['metrics'][metric] for data in recent_data])
                for metric in recent_data[0]['metrics']
            },
            'performance_variance': {
                metric: np.var([data['metrics'][metric] for data in recent_data])
                for metric in recent_data[0]['metrics']
            }
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction for values."""
        if len(values) < 2:
            return 'stable'
        
        # Simple linear trend calculation
        x = np.arange(len(values))
        y = np.array(values)
        
        # Calculate slope
        slope = np.polyfit(x, y, 1)[0]
        
        if slope > self.adaptation_threshold:
            return 'improving'
        elif slope < -self.adaptation_threshold:
            return 'declining'
        else:
            return 'stable'
    
    def _should_adapt(self, performance_analysis: Dict[str, Any]) -> bool:
        """Determine if adaptation is needed."""
        if not performance_analysis:
            return False
        
        trends = performance_analysis.get('trends', {})
        
        # Adapt if any critical metric is declining
        critical_metrics = ['success_rate', 'accuracy', 'efficiency']
        for metric in critical_metrics:
            if metric in trends and trends[metric] == 'declining':
                return True
        
        # Adapt if performance variance is too high
        variance = performance_analysis.get('performance_variance', {})
        for metric, var in variance.items():
            if var > 0.1:  # High variance threshold
                return True
        
        return False
    
    def _perform_adaptation(self, performance_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Perform learning adaptation."""
        adaptation = {
            'timestamp': time.time(),
            'type': 'performance_adaptation',
            'changes': [],
            'reasoning': []
        }
        
        trends = performance_analysis.get('trends', {})
        
        # Adapt based on trends
        for metric, trend in trends.items():
            if trend == 'declining':
                if metric == 'success_rate':
                    adaptation['changes'].append({
                        'component': 'tool_selection',
                        'change': 'increase_confidence_threshold',
                        'value': 0.05
                    })
                    adaptation['reasoning'].append(f"Success rate declining, increasing confidence threshold")
                
                elif metric == 'response_time':
                    adaptation['changes'].append({
                        'component': 'context_analysis',
                        'change': 'optimize_analysis_algorithm',
                        'value': 0.1
                    })
                    adaptation['reasoning'].append(f"Response time increasing, optimizing analysis algorithm")
                
                elif metric == 'memory_usage':
                    adaptation['changes'].append({
                        'component': 'pattern_storage',
                        'change': 'reduce_pattern_storage',
                        'value': 0.1
                    })
                    adaptation['reasoning'].append(f"Memory usage increasing, reducing pattern storage")
        
        return adaptation

class LearningMetrics:
    """
    Track and analyze learning metrics.
    
    SpecBlock:
    - responsibility: "Track and analyze learning metrics"
    - must_never: "Provide inaccurate metrics", "Miss critical learning indicators"
    - performance_budget: "20ms average, 40ms maximum"
    - security_level: "medium"
    """
    
    def __init__(self):
        self.metrics_history: Dict[LearningMetric, deque] = {
            metric: deque(maxlen=100) for metric in LearningMetric
        }
        self.learning_phases: deque = deque(maxlen=100)
        self.insights_generated: int = 0
        self.adaptations_performed: int = 0
    
    def track_metric(self, metric: LearningMetric, value: float, context: Dict[str, Any] = None) -> None:
        """Track a learning metric."""
        self.metrics_history[metric].append({
            'value': value,
            'timestamp': time.time(),
            'context': context or {}
        })
    
    def track_learning_phase(self, phase: LearningPhase, duration: float) -> None:
        """Track learning phase."""
        self.learning_phases.append({
            'phase': phase,
            'duration': duration,
            'timestamp': time.time()
        })
    
    def get_learning_summary(self) -> Dict[str, Any]:
        """Get learning summary."""
        summary = {
            'insights_generated': self.insights_generated,
            'adaptations_performed': self.adaptations_performed,
            'current_phase': self._get_current_phase(),
            'metrics': {}
        }
        
        # Calculate metric statistics
        for metric, history in self.metrics_history.items():
            if history:
                values = [entry['value'] for entry in history]
                summary['metrics'][metric.value] = {
                    'count': len(values),
                    'average': np.mean(values),
                    'minimum': np.min(values),
                    'maximum': np.max(values),
                    'latest': values[-1] if values else 0
                }
        
        return summary
    
    def _get_current_phase(self) -> str:
        """Get current learning phase."""
        if not self.learning_phases:
            return 'unknown'
        
        # Return the most recent phase
        return self.learning_phases[-1]['phase'].value
    
    def get_learning_trends(self) -> Dict[str, str]:
        """Get learning trends."""
        trends = {}
        
        for metric, history in self.metrics_history.items():
            if len(history) >= 5:
                values = [entry['value'] for entry in history]
                trend = self._calculate_trend(values)
                trends[metric.value] = trend
        
        return trends
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend for values."""
        if len(values) < 2:
            return 'stable'
        
        # Simple trend calculation
        recent_avg = np.mean(values[-3:])
        earlier_avg = np.mean(values[:3])
        
        if recent_avg > earlier_avg * 1.05:
            return 'improving'
        elif recent_avg < earlier_avg * 0.95:
            return 'declining'
        else:
            return 'stable'

class LearningSystem:
    """
    Main learning system.
    
    SpecBlock:
    - responsibility: "Learn from tool usage patterns and improve selection"
    - must_never: "Learn from invalid data", "Make changes without proper validation"
    - performance_budget: "200ms average, 500ms maximum"
    - security_level: "high"
    """
    
    def __init__(self, rag_system):
        self.rag_system = rag_system
        self.pattern_learner = PatternLearner(rag_system)
        self.adaptive_learner = AdaptiveLearner()
        self.metrics = LearningMetrics()
        
        self.learning_queue = queue.Queue()
        self.learning_thread = None
        self.running = False
    
    def start(self) -> None:
        """Start learning system."""
        if self.running:
            return
        
        self.running = True
        self.learning_thread = threading.Thread(target=self._learning_loop, daemon=True)
        self.learning_thread.start()
    
    def stop(self) -> None:
        """Stop learning system."""
        self.running = False
        if self.learning_thread:
            self.learning_thread.join(timeout=5)
    
    def learn_from_selection(self, 
                           context_profile: Any,
                           selected_tools: List[str],
                           outcome: Dict[str, Any],
                           performance_metrics: Dict[str, float]) -> None:
        """Learn from tool selection."""
        learning_data = LearningData(
            context_profile=self._extract_context_profile(context_profile),
            selected_tools=selected_tools,
            outcome=outcome,
            performance_metrics=performance_metrics,
            timestamp=time.time(),
            learning_phase=self._determine_learning_phase()
        )
        
        # Add to learning queue
        self.learning_queue.put(learning_data)
    
    def _learning_loop(self) -> None:
        """Main learning loop."""
        while self.running:
            try:
                # Process learning data
                if not self.learning_queue.empty():
                    learning_data = self.learning_queue.get(timeout=1)
                    self._process_learning_data(learning_data)
                
                time.sleep(0.1)
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error in learning loop: {e}")
                time.sleep(1)
    
    def _process_learning_data(self, learning_data: LearningData) -> None:
        """Process learning data."""
        # Learn patterns
        self.pattern_learner.learn_from_data(learning_data)
        
        # Track metrics
        self._track_learning_metrics(learning_data)
        
        # Adaptive learning
        adaptation = self.adaptive_learner.adapt_learning(learning_data.performance_metrics)
        if adaptation.get('adaptation') != 'no_change_needed':
            self.metrics.adaptations_performed += 1
        
        # Generate insights
        insights = self.pattern_learner.get_learning_insights()
        if insights:
            self.metrics.insights_generated += len(insights)
    
    def _extract_context_profile(self, context_profile: Any) -> Dict[str, Any]:
        """Extract context profile data."""
        return {
            'context_type': context_profile.context_type.value,
            'task_classification': context_profile.task_classification,
            'intent_inference': context_profile.intent_inference,
            'complexity': context_profile.complexity.value,
            'required_capabilities': context_profile.required_capabilities,
            'preferred_categories': context_profile.preferred_categories
        }
    
    def _determine_learning_phase(self) -> LearningPhase:
        """Determine current learning phase."""
        # Simple phase determination based on learning data count
        data_count = len(self.pattern_learner.learning_data)
        
        if data_count < 10:
            return LearningPhase.EXPLORATION
        elif data_count < 50:
            return LearningPhase.EXPLOITATION
        elif data_count < 100:
            return LearningPhase.ADAPTATION
        else:
            return LearningPhase.CONSOLIDATION
    
    def _track_learning_metrics(self, learning_data: LearningData) -> None:
        """Track learning metrics."""
        # Calculate accuracy
        accuracy = 1.0 if learning_data.outcome.get('success', False) else 0.0
        self.metrics.track_metric(LearningMetric.ACCURACY, accuracy)
        
        # Calculate efficiency
        response_time = learning_data.performance_metrics.get('response_time_ms', 0)
        efficiency = max(0, 1.0 - (response_time / 1000.0))  # Normalize to 0-1
        self.metrics.track_metric(LearningMetric.EFFICIENCY, efficiency)
        
        # Calculate reliability
        success_rate = learning_data.outcome.get('success_rate', 0.5)
        self.metrics.track_metric(LearningMetric.RELIABILITY, success_rate)
        
        # Calculate adaptability
        adaptation_count = self.metrics.adaptations_performed
        adaptability = min(1.0, adaptation_count / 10.0)  # Normalize to 0-1
        self.metrics.track_metric(LearningMetric.ADAPTABILITY, adaptability)
        
        # Calculate consistency
        consistency = 1.0 - learning_data.performance_metrics.get('variance', 0.0)
        self.metrics.track_metric(LearningMetric.CONSISTENCY, consistency)
        
        # Track learning phase
        phase_duration = 1.0  # Assume 1 second per learning data point
        self.metrics.track_learning_phase(learning_data.learning_phase, phase_duration)
    
    def get_learning_status(self) -> Dict[str, Any]:
        """Get learning system status."""
        return {
            'running': self.running,
            'learning_data_count': len(self.pattern_learner.learning_data),
            'pattern_count': len(self.pattern_learner.pattern_frequency),
            'success_patterns': len(self.pattern_learner.success_patterns),
            'failure_patterns': len(self.pattern_learner.failure_patterns),
            'learning_summary': self.metrics.get_learning_summary(),
            'learning_trends': self.metrics.get_learning_trends(),
            'queue_size': self.learning_queue.qsize()
        }
    
    def get_learning_insights(self) -> List[LearningInsight]:
        """Get current learning insights."""
        return self.pattern_learner.get_learning_insights()
    
    def export_learning_data(self, filepath: str) -> None:
        """Export learning data to file."""
        learning_data = {
            'learning_status': self.get_learning_status(),
            'insights': [
                {
                    'insight_id': insight.insight_id,
                    'insight_type': insight.insight_type,
                    'description': insight.description,
                    'confidence': insight.confidence,
                    'evidence': insight.evidence,
                    'timestamp': insight.timestamp,
                    'impact_score': insight.impact_score
                }
                for insight in self.get_learning_insights()
            ],
            'export_timestamp': time.time()
        }
        
        with open(filepath, 'w') as f:
            json.dump(learning_data, f, indent=2)

if __name__ == "__main__":
    # Test the learning system
    from rag_system.rag_engine import RAGSystem
    from tool_registry.tool_registry import ToolRegistry
    
    # Initialize dependencies
    registry = ToolRegistry()
    rag_system = RAGSystem(registry)
    
    # Initialize learning system
    learning_system = LearningSystem(rag_system)
    
    # Start learning system
    learning_system.start()
    print("Learning system started")
    
    try:
        # Simulate learning data
        from context_analysis_engine.context_analyzer import ContextProfile, ContextType, ComplexityLevel
        
        for i in range(20):
            context_profile = ContextProfile(
                context_id=f"test_ctx_{i}",
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
            
            outcome = {
                'success': i % 3 != 0,  # 2/3 success rate
                'execution_time_ms': 100 + i * 5,
                'memory_usage_mb': 50 + i * 2,
                'cpu_usage_percent': 20 + i
            }
            
            performance_metrics = {
                'response_time_ms': 100 + i * 5,
                'memory_usage_mb': 50 + i * 2,
                'cpu_usage_percent': 20 + i,
                'variance': 0.1 + i * 0.01
            }
            
            learning_system.learn_from_selection(
                context_profile,
                ["mcp_lucid-mcp_store_memory", "mcp_lucid-mcp_create_plan"],
                outcome,
                performance_metrics
            )
            
            time.sleep(0.1)
        
        # Wait for learning to process
        time.sleep(2)
        
        # Get learning status
        status = learning_system.get_learning_status()
        print(f"Learning Status: {json.dumps(status, indent=2)}")
        
        # Get learning insights
        insights = learning_system.get_learning_insights()
        print(f"Learning Insights: {len(insights)} insights generated")
        
        # Export learning data
        learning_system.export_learning_data("learning_data.json")
        print("Learning data exported to learning_data.json")
        
    finally:
        # Stop learning system
        learning_system.stop()
        print("Learning system stopped")
