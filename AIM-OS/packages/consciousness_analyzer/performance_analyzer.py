"""
Consciousness Performance Analyzer

Analyzes performance metrics and identifies optimization opportunities.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import asyncio
import logging

logger = logging.getLogger(__name__)

@dataclass
class PerformanceAnalysis:
    """Represents a performance analysis result"""
    system_name: str
    analysis_type: str
    performance_level: str
    metrics: Dict[str, float]
    recommendations: List[str]
    timestamp: datetime

class PerformanceAnalyzer:
    """
    Analyzes consciousness system performance metrics.
    
    Integrates with CAS for introspection and cognitive analysis.
    """
    
    def __init__(self, time_series_db, cas_client=None):
        self.db = time_series_db
        self.cas_client = cas_client  # CAS integration for introspection
        self.performance_thresholds = {
            "response_time_ms": 1000,
            "error_rate_percent": 5.0,
            "memory_usage_percent": 80.0,
            "cpu_usage_percent": 80.0,
            "throughput_ops_per_sec": 100
        }
    
    async def analyze_system_performance(self, system_name: str, time_window: str = "1h") -> PerformanceAnalysis:
        """Analyze overall performance for a specific system"""
        try:
            # Get response time analysis
            response_time_analysis = await self.analyze_response_times(system_name, time_window)
            
            # Get error rate analysis
            error_rate_analysis = await self.analyze_error_rates(system_name, time_window)
            
            # Get resource utilization analysis
            resource_analysis = await self.analyze_resource_utilization(system_name, time_window)
            
            # Get throughput analysis
            throughput_analysis = await self.analyze_throughput(system_name, time_window)
            
            # Combine all analyses
            combined_metrics = {
                **response_time_analysis["metrics"],
                **error_rate_analysis["metrics"],
                **resource_analysis["metrics"],
                **throughput_analysis["metrics"]
            }
            
            # Generate overall performance level
            performance_level = self.determine_overall_performance_level(combined_metrics)
            
            # Generate recommendations
            recommendations = self.generate_performance_recommendations(combined_metrics)
            
            # Create analysis result
            analysis = PerformanceAnalysis(
                system_name=system_name,
                analysis_type="comprehensive",
                performance_level=performance_level,
                metrics=combined_metrics,
                recommendations=recommendations,
                timestamp=datetime.now()
            )
            
            # CAS Integration: Notify CAS about performance analysis (fail-soft)
            if self.cas_client:
                try:
                    self._notify_cas_performance_analysis(analysis)
                except Exception as e:
                    # Fail-soft: CAS integration is optional
                    logger.debug(f"[CAS INTEGRATION WARNING] {e}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing performance for {system_name}: {e}")
            return PerformanceAnalysis(
                system_name=system_name,
                analysis_type="comprehensive",
                performance_level="unknown",
                metrics={},
                recommendations=["Error in analysis - check system logs"],
                timestamp=datetime.now()
            )
    
    async def analyze_response_times(self, system_name: str, time_window: str = "1h") -> Dict[str, Any]:
        """Analyze response times for a specific system"""
        try:
            # Query response time metrics
            query = f"""
            SELECT avg(value) as avg_response_time,
                   max(value) as max_response_time,
                   min(value) as min_response_time,
                   stddev(value) as stddev_response_time,
                   count(value) as sample_count
            FROM metrics
            WHERE system_name = '{system_name}'
            AND metric_type = 'response_time_ms'
            AND timestamp > NOW() - INTERVAL '{time_window}'
            """
            
            results = await self.db.query(query)
            
            if not results or not results[0]['avg_response_time']:
                return {
                    "metrics": {"response_time_ms": 0, "response_time_stddev": 0},
                    "performance_level": "no_data",
                    "recommendations": ["No response time data available"]
                }
            
            avg_time = results[0]['avg_response_time']
            max_time = results[0]['max_response_time']
            min_time = results[0]['min_response_time']
            stddev = results[0]['stddev_response_time'] or 0
            sample_count = results[0]['sample_count']
            
            # Determine performance level
            if avg_time < 100:
                performance_level = "excellent"
            elif avg_time < 500:
                performance_level = "good"
            elif avg_time < 1000:
                performance_level = "fair"
            else:
                performance_level = "poor"
            
            # Generate recommendations
            recommendations = []
            if avg_time > 1000:
                recommendations.append("Consider implementing caching mechanisms")
                recommendations.append("Review database query optimization")
                recommendations.append("Check for blocking operations")
            
            if stddev > avg_time * 0.5:
                recommendations.append("High variability detected - investigate load balancing")
                recommendations.append("Consider implementing circuit breakers")
                recommendations.append("Review resource allocation")
            
            if sample_count < 10:
                recommendations.append("Low sample count - increase monitoring frequency")
            
            return {
                "metrics": {
                    "response_time_ms": avg_time,
                    "response_time_max": max_time,
                    "response_time_min": min_time,
                    "response_time_stddev": stddev,
                    "sample_count": sample_count
                },
                "performance_level": performance_level,
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Error analyzing response times for {system_name}: {e}")
            return {
                "metrics": {"response_time_ms": 0},
                "performance_level": "error",
                "recommendations": [f"Error analyzing response times: {e}"]
            }
    
    async def analyze_error_rates(self, system_name: str, time_window: str = "1h") -> Dict[str, Any]:
        """Analyze error rates for a specific system"""
        try:
            # Query error metrics
            query = f"""
            SELECT 
                sum(case when metric_type = 'error_count' then value else 0 end) as total_errors,
                sum(case when metric_type = 'operation_count' then value else 0 end) as total_operations,
                count(distinct timestamp) as time_periods
            FROM metrics
            WHERE system_name = '{system_name}'
            AND metric_type IN ('error_count', 'operation_count')
            AND timestamp > NOW() - INTERVAL '{time_window}'
            """
            
            results = await self.db.query(query)
            
            if not results or not results[0]['total_operations']:
                return {
                    "metrics": {"error_rate_percent": 0},
                    "performance_level": "no_data",
                    "recommendations": ["No error rate data available"]
                }
            
            total_errors = results[0]['total_errors'] or 0
            total_operations = results[0]['total_operations']
            error_rate = (total_errors / total_operations) * 100 if total_operations > 0 else 0
            
            # Determine performance level
            if error_rate < 1.0:
                performance_level = "excellent"
            elif error_rate < 3.0:
                performance_level = "good"
            elif error_rate < 5.0:
                performance_level = "fair"
            else:
                performance_level = "poor"
            
            # Generate recommendations
            recommendations = []
            if error_rate > 5.0:
                recommendations.append("High error rate detected - investigate error sources")
                recommendations.append("Implement better error handling and recovery")
                recommendations.append("Review system stability and dependencies")
            
            if error_rate > 1.0:
                recommendations.append("Consider implementing retry mechanisms")
                recommendations.append("Add more comprehensive error logging")
            
            return {
                "metrics": {
                    "error_rate_percent": error_rate,
                    "total_errors": total_errors,
                    "total_operations": total_operations
                },
                "performance_level": performance_level,
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Error analyzing error rates for {system_name}: {e}")
            return {
                "metrics": {"error_rate_percent": 0},
                "performance_level": "error",
                "recommendations": [f"Error analyzing error rates: {e}"]
            }
    
    async def analyze_resource_utilization(self, system_name: str, time_window: str = "1h") -> Dict[str, Any]:
        """Analyze resource utilization for a specific system"""
        try:
            # Query resource metrics
            query = f"""
            SELECT 
                avg(case when metric_type = 'memory_usage_percent' then value end) as avg_memory_usage,
                max(case when metric_type = 'memory_usage_percent' then value end) as max_memory_usage,
                avg(case when metric_type = 'cpu_usage_percent' then value end) as avg_cpu_usage,
                max(case when metric_type = 'cpu_usage_percent' then value end) as max_cpu_usage
            FROM metrics
            WHERE system_name = '{system_name}'
            AND metric_type IN ('memory_usage_percent', 'cpu_usage_percent')
            AND timestamp > NOW() - INTERVAL '{time_window}'
            """
            
            results = await self.db.query(query)
            
            if not results:
                return {
                    "metrics": {"memory_usage_percent": 0, "cpu_usage_percent": 0},
                    "performance_level": "no_data",
                    "recommendations": ["No resource utilization data available"]
                }
            
            avg_memory = results[0]['avg_memory_usage'] or 0
            max_memory = results[0]['max_memory_usage'] or 0
            avg_cpu = results[0]['avg_cpu_usage'] or 0
            max_cpu = results[0]['max_cpu_usage'] or 0
            
            # Determine performance level based on resource usage
            if max_memory > 90 or max_cpu > 90:
                performance_level = "poor"
            elif max_memory > 80 or max_cpu > 80:
                performance_level = "fair"
            elif max_memory > 70 or max_cpu > 70:
                performance_level = "good"
            else:
                performance_level = "excellent"
            
            # Generate recommendations
            recommendations = []
            if max_memory > 90:
                recommendations.append("High memory usage detected - consider memory optimization")
                recommendations.append("Review memory leaks and inefficient data structures")
                recommendations.append("Consider increasing memory allocation")
            
            if max_cpu > 90:
                recommendations.append("High CPU usage detected - optimize processing algorithms")
                recommendations.append("Consider implementing async processing")
                recommendations.append("Review CPU-intensive operations")
            
            if avg_memory > 80 or avg_cpu > 80:
                recommendations.append("Consistently high resource usage - consider scaling")
                recommendations.append("Review resource allocation and optimization")
            
            return {
                "metrics": {
                    "memory_usage_percent": avg_memory,
                    "memory_usage_max": max_memory,
                    "cpu_usage_percent": avg_cpu,
                    "cpu_usage_max": max_cpu
                },
                "performance_level": performance_level,
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Error analyzing resource utilization for {system_name}: {e}")
            return {
                "metrics": {"memory_usage_percent": 0, "cpu_usage_percent": 0},
                "performance_level": "error",
                "recommendations": [f"Error analyzing resource utilization: {e}"]
            }
    
    async def analyze_throughput(self, system_name: str, time_window: str = "1h") -> Dict[str, Any]:
        """Analyze throughput for a specific system"""
        try:
            # Query throughput metrics
            query = f"""
            SELECT 
                avg(value) as avg_throughput,
                max(value) as max_throughput,
                min(value) as min_throughput,
                stddev(value) as throughput_stddev
            FROM metrics
            WHERE system_name = '{system_name}'
            AND metric_type = 'throughput_ops_per_sec'
            AND timestamp > NOW() - INTERVAL '{time_window}'
            """
            
            results = await self.db.query(query)
            
            if not results or not results[0]['avg_throughput']:
                return {
                    "metrics": {"throughput_ops_per_sec": 0},
                    "performance_level": "no_data",
                    "recommendations": ["No throughput data available"]
                }
            
            avg_throughput = results[0]['avg_throughput']
            max_throughput = results[0]['max_throughput']
            min_throughput = results[0]['min_throughput']
            stddev = results[0]['throughput_stddev'] or 0
            
            # Determine performance level
            threshold = self.performance_thresholds.get('throughput_ops_per_sec', 100)
            if avg_throughput > threshold * 1.5:
                performance_level = "excellent"
            elif avg_throughput > threshold:
                performance_level = "good"
            elif avg_throughput > threshold * 0.5:
                performance_level = "fair"
            else:
                performance_level = "poor"
            
            # Generate recommendations
            recommendations = []
            if avg_throughput < threshold * 0.5:
                recommendations.append("Low throughput detected - investigate bottlenecks")
                recommendations.append("Consider optimizing processing algorithms")
                recommendations.append("Review resource allocation and scaling")
            
            if stddev > avg_throughput * 0.3:
                recommendations.append("High throughput variability - investigate load patterns")
                recommendations.append("Consider implementing load balancing")
                recommendations.append("Review system stability")
            
            return {
                "metrics": {
                    "throughput_ops_per_sec": avg_throughput,
                    "throughput_max": max_throughput,
                    "throughput_min": min_throughput,
                    "throughput_stddev": stddev
                },
                "performance_level": performance_level,
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Error analyzing throughput for {system_name}: {e}")
            return {
                "metrics": {"throughput_ops_per_sec": 0},
                "performance_level": "error",
                "recommendations": [f"Error analyzing throughput: {e}"]
            }
    
    def determine_overall_performance_level(self, metrics: Dict[str, float]) -> str:
        """Determine overall performance level based on combined metrics"""
        # Weight different metrics based on importance
        weights = {
            "response_time_ms": 0.3,
            "error_rate_percent": 0.3,
            "memory_usage_percent": 0.2,
            "cpu_usage_percent": 0.2
        }
        
        performance_scores = []
        
        # Response time score
        if "response_time_ms" in metrics:
            response_time = metrics["response_time_ms"]
            if response_time < 100:
                performance_scores.append(4)  # excellent
            elif response_time < 500:
                performance_scores.append(3)  # good
            elif response_time < 1000:
                performance_scores.append(2)  # fair
            else:
                performance_scores.append(1)  # poor
        
        # Error rate score
        if "error_rate_percent" in metrics:
            error_rate = metrics["error_rate_percent"]
            if error_rate < 1.0:
                performance_scores.append(4)  # excellent
            elif error_rate < 3.0:
                performance_scores.append(3)  # good
            elif error_rate < 5.0:
                performance_scores.append(2)  # fair
            else:
                performance_scores.append(1)  # poor
        
        # Resource usage scores
        for resource in ["memory_usage_percent", "cpu_usage_percent"]:
            if resource in metrics:
                usage = metrics[resource]
                if usage < 70:
                    performance_scores.append(4)  # excellent
                elif usage < 80:
                    performance_scores.append(3)  # good
                elif usage < 90:
                    performance_scores.append(2)  # fair
                else:
                    performance_scores.append(1)  # poor
        
        if not performance_scores:
            return "unknown"
        
        # Calculate weighted average
        avg_score = sum(performance_scores) / len(performance_scores)
        
        if avg_score >= 3.5:
            return "excellent"
        elif avg_score >= 2.5:
            return "good"
        elif avg_score >= 1.5:
            return "fair"
        else:
            return "poor"
    
    def generate_performance_recommendations(self, metrics: Dict[str, float]) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        # Response time recommendations
        if metrics.get("response_time_ms", 0) > 1000:
            recommendations.append("Implement caching for frequently accessed data")
            recommendations.append("Optimize database queries and indexes")
            recommendations.append("Consider implementing async processing")
        
        # Error rate recommendations
        if metrics.get("error_rate_percent", 0) > 5.0:
            recommendations.append("Implement comprehensive error handling")
            recommendations.append("Add retry mechanisms with exponential backoff")
            recommendations.append("Review system stability and dependencies")
        
        # Resource usage recommendations
        if metrics.get("memory_usage_percent", 0) > 80:
            recommendations.append("Optimize memory usage and data structures")
            recommendations.append("Implement memory pooling and reuse")
            recommendations.append("Consider increasing memory allocation")
        
        if metrics.get("cpu_usage_percent", 0) > 80:
            recommendations.append("Optimize CPU-intensive operations")
            recommendations.append("Implement parallel processing where possible")
            recommendations.append("Review algorithm efficiency")
        
        # Throughput recommendations
        if metrics.get("throughput_ops_per_sec", 0) < 50:
            recommendations.append("Optimize processing algorithms")
            recommendations.append("Implement horizontal scaling")
            recommendations.append("Review system bottlenecks")
        
        return recommendations
    
    def _notify_cas_performance_analysis(self, analysis: PerformanceAnalysis):
        """Notify CAS about performance analysis for introspection"""
        if not self.cas_client:
            return
        
        try:
            # Check if CAS has introspection protocol
            if hasattr(self.cas_client, 'introspection') or hasattr(self.cas_client, 'IntrospectionProtocol'):
                # Create performance analysis summary for CAS
                analysis_summary = {
                    "system_name": analysis.system_name,
                    "analysis_type": analysis.analysis_type,
                    "performance_level": analysis.performance_level,
                    "metrics": analysis.metrics,
                    "recommendations": analysis.recommendations,
                    "timestamp": analysis.timestamp.isoformat()
                }
                
                # Try to record performance analysis in CAS
                # CAS can use this for introspection and cognitive analysis
                if hasattr(self.cas_client, 'record_performance_analysis'):
                    self.cas_client.record_performance_analysis(analysis_summary)
                elif hasattr(self.cas_client, 'record_principle_violation'):
                    # Use principle violation for poor performance to notify CAS
                    if analysis.performance_level in ["poor", "fair"]:
                        self.cas_client.record_principle_violation(
                            principle="system_performance",
                            violation_type="performance_analysis",
                            details=f"Performance level: {analysis.performance_level} for {analysis.system_name}",
                            context=analysis_summary
                        )
        except Exception as e:
            # Fail-soft: CAS integration is optional enhancement
            logger.debug(f"[CAS NOTIFICATION WARNING] {e}")
