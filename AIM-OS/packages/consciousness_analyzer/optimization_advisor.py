"""
Consciousness Optimization Advisor

Generates optimization recommendations for consciousness systems.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import asyncio
import logging

logger = logging.getLogger(__name__)

@dataclass
class OptimizationRecommendation:
    """Represents an optimization recommendation"""
    system_name: str
    recommendation_type: str
    category: str
    description: str
    priority: str  # high, medium, low
    estimated_improvement: str
    implementation_effort: str
    timestamp: datetime

class OptimizationAdvisor:
    """Generates optimization recommendations for consciousness systems"""
    
    def __init__(self, performance_analyzer, health_monitor):
        self.performance_analyzer = performance_analyzer
        self.health_monitor = health_monitor
        self.running = False
        self.recommendation_history = []
    
    async def start_analysis(self):
        """Start the optimization analysis loop"""
        self.running = True
        logger.info("Starting consciousness optimization analysis")
        
        while self.running:
            try:
                await self.perform_optimization_analysis()
                await asyncio.sleep(300)  # Analyze every 5 minutes
            except Exception as e:
                logger.error(f"Error in optimization analysis: {e}")
                await asyncio.sleep(300)
    
    async def stop_analysis(self):
        """Stop the optimization analysis loop"""
        self.running = False
        logger.info("Stopped consciousness optimization analysis")
    
    async def perform_optimization_analysis(self):
        """Perform optimization analysis on all consciousness systems"""
        systems = ["cmc", "hhni", "vif", "apoe", "sdfcvf", "iis"]
        
        for system in systems:
            try:
                recommendations = await self.generate_optimization_recommendations(system)
                
                if recommendations:
                    self.recommendation_history.extend(recommendations)
                    logger.info(f"Generated {len(recommendations)} optimization recommendations for {system}")
                    
            except Exception as e:
                logger.error(f"Error generating recommendations for {system}: {e}")
    
    async def generate_optimization_recommendations(self, system_name: str) -> List[OptimizationRecommendation]:
        """Generate optimization recommendations for a system"""
        recommendations = []
        
        try:
            # Get performance analysis
            performance = await self.performance_analyzer.analyze_system_performance(system_name)
            
            # Get health status
            health = await self.health_monitor.check_system_health(system_name)
            
            # Generate recommendations based on analysis
            if performance.performance_level == "poor":
                recommendations.extend(self.generate_performance_optimizations(system_name, performance))
            
            if health["overall_health"] != "healthy":
                recommendations.extend(self.generate_health_optimizations(system_name, health))
            
            # Cross-system optimization recommendations
            cross_system_recs = await self.generate_cross_system_recommendations(system_name)
            recommendations.extend(cross_system_recs)
            
        except Exception as e:
            logger.error(f"Error generating recommendations for {system_name}: {e}")
            recommendations.append(OptimizationRecommendation(
                system_name=system_name,
                recommendation_type="error_handling",
                category="system",
                description=f"Error generating recommendations: {e}",
                priority="high",
                estimated_improvement="Unknown",
                implementation_effort="Low",
                timestamp=datetime.now()
            ))
        
        return recommendations
    
    def generate_performance_optimizations(self, system_name: str, performance) -> List[OptimizationRecommendation]:
        """Generate performance-specific optimizations"""
        recommendations = []
        
        # Response time optimizations
        if performance.metrics.get("response_time_ms", 0) > 1000:
            recommendations.append(OptimizationRecommendation(
                system_name=system_name,
                recommendation_type="performance",
                category="caching",
                description="Implement Redis caching for frequently accessed data",
                priority="high",
                estimated_improvement="30-50% response time reduction",
                implementation_effort="Medium",
                timestamp=datetime.now()
            ))
            
            recommendations.append(OptimizationRecommendation(
                system_name=system_name,
                recommendation_type="performance",
                category="database",
                description="Optimize database queries and add indexes",
                priority="high",
                estimated_improvement="20-40% response time reduction",
                implementation_effort="Medium",
                timestamp=datetime.now()
            ))
        
        # Throughput optimizations
        if performance.metrics.get("throughput_ops_per_sec", 0) < 50:
            recommendations.append(OptimizationRecommendation(
                system_name=system_name,
                recommendation_type="performance",
                category="scaling",
                description="Implement horizontal scaling with load balancing",
                priority="medium",
                estimated_improvement="2-3x throughput increase",
                implementation_effort="High",
                timestamp=datetime.now()
            ))
        
        # Variability optimizations
        response_time_stddev = performance.metrics.get("response_time_stddev", 0)
        avg_response_time = performance.metrics.get("response_time_ms", 0)
        if response_time_stddev > avg_response_time * 0.5:
            recommendations.append(OptimizationRecommendation(
                system_name=system_name,
                recommendation_type="performance",
                category="stability",
                description="Implement circuit breakers and retry mechanisms",
                priority="medium",
                estimated_improvement="20-30% variability reduction",
                implementation_effort="Medium",
                timestamp=datetime.now()
            ))
        
        return recommendations
    
    def generate_health_optimizations(self, system_name: str, health: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Generate health-specific optimizations"""
        recommendations = []
        
        # Check individual health checks
        for check in health.get("checks", []):
            if check.status == "critical":
                if check.check_type == "response_time":
                    recommendations.append(OptimizationRecommendation(
                        system_name=system_name,
                        recommendation_type="health",
                        category="performance",
                        description="Critical response time issue - implement immediate optimizations",
                        priority="high",
                        estimated_improvement="50-70% response time improvement",
                        implementation_effort="High",
                        timestamp=datetime.now()
                    ))
                
                elif check.check_type == "error_rate":
                    recommendations.append(OptimizationRecommendation(
                        system_name=system_name,
                        recommendation_type="health",
                        category="reliability",
                        description="Critical error rate - implement comprehensive error handling",
                        priority="high",
                        estimated_improvement="80-90% error rate reduction",
                        implementation_effort="High",
                        timestamp=datetime.now()
                    ))
                
                elif check.check_type == "resource_usage":
                    recommendations.append(OptimizationRecommendation(
                        system_name=system_name,
                        recommendation_type="health",
                        category="resources",
                        description="Critical resource usage - optimize memory and CPU usage",
                        priority="high",
                        estimated_improvement="30-50% resource usage reduction",
                        implementation_effort="Medium",
                        timestamp=datetime.now()
                    ))
            
            elif check.status == "warning":
                if check.check_type == "response_time":
                    recommendations.append(OptimizationRecommendation(
                        system_name=system_name,
                        recommendation_type="health",
                        category="performance",
                        description="Response time approaching limits - implement preventive optimizations",
                        priority="medium",
                        estimated_improvement="20-30% response time improvement",
                        implementation_effort="Medium",
                        timestamp=datetime.now()
                    ))
                
                elif check.check_type == "resource_usage":
                    recommendations.append(OptimizationRecommendation(
                        system_name=system_name,
                        recommendation_type="health",
                        category="resources",
                        description="Resource usage approaching limits - implement resource optimization",
                        priority="medium",
                        estimated_improvement="15-25% resource usage reduction",
                        implementation_effort="Low",
                        timestamp=datetime.now()
                    ))
        
        return recommendations
    
    async def generate_cross_system_recommendations(self, system_name: str) -> List[OptimizationRecommendation]:
        """Generate cross-system optimization recommendations"""
        recommendations = []
        
        # System-specific cross-system recommendations
        if system_name == "cmc":
            recommendations.append(OptimizationRecommendation(
                system_name=system_name,
                recommendation_type="integration",
                category="caching",
                description="Integrate with HHNI for intelligent caching based on search patterns",
                priority="medium",
                estimated_improvement="25-35% memory efficiency improvement",
                implementation_effort="Medium",
                timestamp=datetime.now()
            ))
        
        elif system_name == "hhni":
            recommendations.append(OptimizationRecommendation(
                system_name=system_name,
                recommendation_type="integration",
                category="performance",
                description="Integrate with VIF for confidence-based search result ranking",
                priority="medium",
                estimated_improvement="15-25% search accuracy improvement",
                implementation_effort="Medium",
                timestamp=datetime.now()
            ))
        
        elif system_name == "vif":
            recommendations.append(OptimizationRecommendation(
                system_name=system_name,
                recommendation_type="integration",
                category="learning",
                description="Integrate with IIS for improved confidence calibration",
                priority="low",
                estimated_improvement="10-20% confidence accuracy improvement",
                implementation_effort="Low",
                timestamp=datetime.now()
            ))
        
        elif system_name == "apoe":
            recommendations.append(OptimizationRecommendation(
                system_name=system_name,
                recommendation_type="integration",
                category="orchestration",
                description="Integrate with SDF-CVF for quality-aware task scheduling",
                priority="medium",
                estimated_improvement="20-30% task completion quality improvement",
                implementation_effort="Medium",
                timestamp=datetime.now()
            ))
        
        elif system_name == "sdfcvf":
            recommendations.append(OptimizationRecommendation(
                system_name=system_name,
                recommendation_type="integration",
                category="quality",
                description="Integrate with all systems for comprehensive quality monitoring",
                priority="high",
                estimated_improvement="30-40% overall system quality improvement",
                implementation_effort="High",
                timestamp=datetime.now()
            ))
        
        elif system_name == "iis":
            recommendations.append(OptimizationRecommendation(
                system_name=system_name,
                recommendation_type="integration",
                category="learning",
                description="Integrate with all systems for pattern recognition and learning",
                priority="medium",
                estimated_improvement="25-35% overall system intelligence improvement",
                implementation_effort="High",
                timestamp=datetime.now()
            ))
        
        return recommendations
    
    def get_recommendations_by_priority(self, priority: str = None) -> List[OptimizationRecommendation]:
        """Get recommendations filtered by priority"""
        if priority is None:
            return self.recommendation_history
        
        return [rec for rec in self.recommendation_history if rec.priority == priority]
    
    def get_recommendations_by_system(self, system_name: str) -> List[OptimizationRecommendation]:
        """Get recommendations for a specific system"""
        return [rec for rec in self.recommendation_history if rec.system_name == system_name]
    
    def get_recommendations_by_category(self, category: str) -> List[OptimizationRecommendation]:
        """Get recommendations for a specific category"""
        return [rec for rec in self.recommendation_history if rec.category == category]
    
    def get_recent_recommendations(self, hours: int = 24) -> List[OptimizationRecommendation]:
        """Get recommendations from the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [rec for rec in self.recommendation_history if rec.timestamp > cutoff_time]
    
    def get_recommendation_summary(self) -> Dict[str, Any]:
        """Get a summary of all recommendations"""
        if not self.recommendation_history:
            return {
                "total_recommendations": 0,
                "by_priority": {},
                "by_system": {},
                "by_category": {},
                "recent_count": 0
            }
        
        summary = {
            "total_recommendations": len(self.recommendation_history),
            "by_priority": {},
            "by_system": {},
            "by_category": {},
            "recent_count": len(self.get_recent_recommendations(24))
        }
        
        # Count by priority
        for rec in self.recommendation_history:
            priority = rec.priority
            summary["by_priority"][priority] = summary["by_priority"].get(priority, 0) + 1
        
        # Count by system
        for rec in self.recommendation_history:
            system = rec.system_name
            summary["by_system"][system] = summary["by_system"].get(system, 0) + 1
        
        # Count by category
        for rec in self.recommendation_history:
            category = rec.category
            summary["by_category"][category] = summary["by_category"].get(category, 0) + 1
        
        return summary
