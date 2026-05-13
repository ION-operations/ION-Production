"""Performance Tracker Component for CAF

Tracks performance of capability activation, measuring effectiveness,
efficiency, and quality to enable continuous improvement.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
import uuid

from .models import PerformanceMetrics, ActivationResult, CapabilityDecision


class PerformanceTracker:
    """Track performance of capability activation"""
    
    def __init__(self):
        """Initialize performance tracker"""
        self.performance_history: List[PerformanceMetrics] = []
        self.capability_stats: Dict[str, Dict[str, Any]] = {}
    
    def track_performance(
        self,
        activation_result: ActivationResult,
        outcome: Optional[Dict[str, Any]] = None
    ) -> PerformanceMetrics:
        """Track performance of capability activation
        
        Args:
            activation_result: Activation result to track
            outcome: Optional outcome metrics (success, quality, satisfaction)
            
        Returns:
            PerformanceMetrics with tracked performance data
        """
        outcome = outcome or {}
        
        # Calculate metrics
        success = activation_result.success
        activation_time_ms = activation_result.activation_time_ms
        effectiveness_score = activation_result.effectiveness_score
        quality_maintained = outcome.get("quality_maintained", effectiveness_score)
        user_satisfaction = outcome.get("user_satisfaction", effectiveness_score)
        
        # Calculate success rate for this capability
        success_rate = self._calculate_success_rate(activation_result.capability)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            activation_result, quality_maintained, user_satisfaction
        )
        
        # Create performance metrics
        metrics = PerformanceMetrics(
            activation_id=activation_result.activation_id,
            capability_id=activation_result.capability,
            success=success,
            activation_time_ms=activation_time_ms,
            effectiveness_score=effectiveness_score,
            quality_maintained=quality_maintained,
            user_satisfaction=user_satisfaction,
            success_rate=success_rate,
            recommendations=recommendations
        )
        
        # Store in history
        self.performance_history.append(metrics)
        
        # Update capability stats
        self._update_capability_stats(metrics)
        
        return metrics
    
    def _calculate_success_rate(self, capability_id: str) -> float:
        """Calculate success rate for a capability"""
        capability_results = [
            m for m in self.performance_history 
            if m.capability_id == capability_id
        ]
        
        if not capability_results:
            return 1.0  # Default to 100% if no history
        
        successful = sum(1 for m in capability_results if m.success)
        return successful / len(capability_results)
    
    def _generate_recommendations(
        self,
        activation_result: ActivationResult,
        quality_maintained: float,
        user_satisfaction: float
    ) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        # Performance-based recommendations
        if activation_result.activation_time_ms > 1000:
            recommendations.append("Consider optimizing activation time")
        
        if activation_result.effectiveness_score < 0.7:
            recommendations.append("Consider improving effectiveness")
        
        if quality_maintained < 0.8:
            recommendations.append("Focus on maintaining quality")
        
        if user_satisfaction < 0.8:
            recommendations.append("Improve user satisfaction")
        
        # Confidence-based recommendations
        if activation_result.confidence < 0.7:
            recommendations.append("Increase confidence threshold or improve context analysis")
        
        return recommendations
    
    def _update_capability_stats(self, metrics: PerformanceMetrics):
        """Update capability statistics"""
        capability_id = metrics.capability_id
        
        if capability_id not in self.capability_stats:
            self.capability_stats[capability_id] = {
                "total_activations": 0,
                "successful_activations": 0,
                "total_time_ms": 0.0,
                "total_effectiveness": 0.0,
                "total_quality": 0.0,
                "total_satisfaction": 0.0
            }
        
        stats = self.capability_stats[capability_id]
        stats["total_activations"] += 1
        if metrics.success:
            stats["successful_activations"] += 1
        stats["total_time_ms"] += metrics.activation_time_ms
        stats["total_effectiveness"] += metrics.effectiveness_score
        stats["total_quality"] += metrics.quality_maintained
        stats["total_satisfaction"] += metrics.user_satisfaction
    
    def get_performance_insights(
        self,
        capability_id: str,
        time_range_days: int = 30
    ) -> Dict[str, Any]:
        """Get performance insights for a capability
        
        Args:
            capability_id: Capability ID to analyze
            time_range_days: Number of days to look back
            
        Returns:
            Dictionary with performance insights
        """
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=time_range_days)
        
        # Filter metrics for this capability and time range
        relevant_metrics = [
            m for m in self.performance_history
            if m.capability_id == capability_id and m.timestamp >= cutoff_time
        ]
        
        if not relevant_metrics:
            return {
                "capability_id": capability_id,
                "no_data": True,
                "message": f"No performance data for {capability_id} in last {time_range_days} days"
            }
        
        # Calculate averages
        total_time = sum(m.activation_time_ms for m in relevant_metrics)
        total_effectiveness = sum(m.effectiveness_score for m in relevant_metrics)
        total_quality = sum(m.quality_maintained for m in relevant_metrics)
        total_satisfaction = sum(m.user_satisfaction for m in relevant_metrics)
        successful = sum(1 for m in relevant_metrics if m.success)
        
        count = len(relevant_metrics)
        
        insights = {
            "capability_id": capability_id,
            "time_range_days": time_range_days,
            "total_activations": count,
            "successful_activations": successful,
            "success_rate": successful / count if count > 0 else 0.0,
            "avg_activation_time_ms": total_time / count if count > 0 else 0.0,
            "avg_effectiveness": total_effectiveness / count if count > 0 else 0.0,
            "avg_quality": total_quality / count if count > 0 else 0.0,
            "avg_satisfaction": total_satisfaction / count if count > 0 else 0.0,
            "effectiveness_trend": self._calculate_trend(relevant_metrics, "effectiveness_score"),
            "optimization_opportunities": self._identify_optimization_opportunities(relevant_metrics)
        }
        
        return insights
    
    def _calculate_trend(
        self,
        metrics: List[PerformanceMetrics],
        field: str
    ) -> str:
        """Calculate trend for a metric field"""
        if len(metrics) < 2:
            return "insufficient_data"
        
        # Split into halves
        mid = len(metrics) // 2
        first_half = metrics[:mid]
        second_half = metrics[mid:]
        
        first_avg = sum(getattr(m, field) for m in first_half) / len(first_half)
        second_avg = sum(getattr(m, field) for m in second_half) / len(second_half)
        
        diff = second_avg - first_avg
        
        if diff > 0.05:
            return "improving"
        elif diff < -0.05:
            return "degrading"
        else:
            return "stable"
    
    def _identify_optimization_opportunities(
        self,
        metrics: List[PerformanceMetrics]
    ) -> List[str]:
        """Identify optimization opportunities"""
        opportunities = []
        
        if not metrics:
            return opportunities
        
        # Check activation time
        avg_time = sum(m.activation_time_ms for m in metrics) / len(metrics)
        if avg_time > 500:
            opportunities.append("Reduce activation time")
        
        # Check effectiveness
        avg_effectiveness = sum(m.effectiveness_score for m in metrics) / len(metrics)
        if avg_effectiveness < 0.8:
            opportunities.append("Improve effectiveness")
        
        # Check success rate
        success_rate = sum(1 for m in metrics if m.success) / len(metrics)
        if success_rate < 0.9:
            opportunities.append("Improve success rate")
        
        return opportunities
    
    def update_learning_models(
        self,
        activation_id: str,
        performance_metrics: PerformanceMetrics
    ) -> Dict[str, Any]:
        """Update learning models based on performance
        
        Args:
            activation_id: Activation ID
            performance_metrics: Performance metrics
            
        Returns:
            Dictionary with learning update results
        """
        # In a full implementation, this would update ML models
        # For now, return update status
        
        models_updated = []
        improvement_score = 0.0
        
        # Simulate model updates based on performance
        if performance_metrics.success:
            models_updated.append("trigger_patterns")
            improvement_score += 0.1
        
        if performance_metrics.effectiveness_score > 0.8:
            models_updated.append("decision_trees")
            improvement_score += 0.1
        
        if performance_metrics.quality_maintained > 0.9:
            models_updated.append("quality_models")
            improvement_score += 0.1
        
        return {
            "activation_id": activation_id,
            "models_updated": models_updated,
            "improvement_score": min(1.0, improvement_score),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def query_performance_history(
        self,
        capability_id: Optional[str] = None,
        min_effectiveness: float = 0.0,
        start_time: Optional[datetime] = None
    ) -> List[PerformanceMetrics]:
        """Query performance history"""
        results = self.performance_history
        
        # Filter by capability
        if capability_id:
            results = [m for m in results if m.capability_id == capability_id]
        
        # Filter by effectiveness
        results = [m for m in results if m.effectiveness_score >= min_effectiveness]
        
        # Filter by time
        if start_time:
            results = [m for m in results if m.timestamp >= start_time]
        
        return results

