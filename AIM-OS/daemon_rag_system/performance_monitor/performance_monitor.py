#!/usr/bin/env python3
"""
Performance Monitor - Monitor system performance and provide optimization recommendations
Part of Daemon/RAG System Implementation

Following A-H Protocol and DEL methodology from ChatGPT journal
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import time
import psutil
import threading
import json
from collections import deque, defaultdict

class MetricType(Enum):
    """Types of performance metrics."""
    RESPONSE_TIME = "response_time"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    SUCCESS_RATE = "success_rate"

@dataclass
class PerformanceMetric:
    """Performance metric data point."""
    metric_type: MetricType
    value: float
    timestamp: float
    component: str
    context: Dict[str, Any] = None

@dataclass
class PerformanceAlert:
    """Performance alert."""
    alert_id: str
    metric_type: MetricType
    threshold: float
    current_value: float
    severity: str
    message: str
    timestamp: float
    component: str

class PerformanceCollector:
    """
    Collect performance metrics from system.
    
    SpecBlock:
    - responsibility: "Collect performance metrics from system"
    - must_never: "Miss critical performance issues", "Provide inaccurate metrics"
    - performance_budget: "10ms average, 25ms maximum"
    - security_level: "medium"
    """
    
    def __init__(self, max_metrics: int = 1000):
        self.max_metrics = max_metrics
        self.metrics: deque = deque(maxlen=max_metrics)
        self.metrics_by_component: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_metrics))
        self.metrics_by_type: Dict[MetricType, deque] = defaultdict(lambda: deque(maxlen=max_metrics))
    
    def collect_system_metrics(self) -> List[PerformanceMetric]:
        """Collect system-level performance metrics."""
        metrics = []
        current_time = time.time()
        
        try:
            # Memory usage
            memory_info = psutil.virtual_memory()
            metrics.append(PerformanceMetric(
                metric_type=MetricType.MEMORY_USAGE,
                value=memory_info.percent,
                timestamp=current_time,
                component="system",
                context={"total_mb": memory_info.total / (1024 * 1024), "available_mb": memory_info.available / (1024 * 1024)}
            ))
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            metrics.append(PerformanceMetric(
                metric_type=MetricType.CPU_USAGE,
                value=cpu_percent,
                timestamp=current_time,
                component="system"
            ))
            
            # Disk usage
            disk_usage = psutil.disk_usage('/')
            metrics.append(PerformanceMetric(
                metric_type=MetricType.MEMORY_USAGE,  # Reusing memory type for disk
                value=(disk_usage.used / disk_usage.total) * 100,
                timestamp=current_time,
                component="system",
                context={"total_gb": disk_usage.total / (1024**3), "used_gb": disk_usage.used / (1024**3)}
            ))
            
        except Exception as e:
            print(f"Error collecting system metrics: {e}")
        
        return metrics
    
    def collect_component_metrics(self, component: str, metrics_data: Dict[str, float]) -> List[PerformanceMetric]:
        """Collect component-specific performance metrics."""
        metrics = []
        current_time = time.time()
        
        for metric_name, value in metrics_data.items():
            metric_type = self._map_metric_name_to_type(metric_name)
            if metric_type:
                metric = PerformanceMetric(
                    metric_type=metric_type,
                    value=value,
                    timestamp=current_time,
                    component=component
                )
                metrics.append(metric)
        
        return metrics
    
    def add_metrics(self, metrics: List[PerformanceMetric]) -> None:
        """Add metrics to collection."""
        for metric in metrics:
            self.metrics.append(metric)
            self.metrics_by_component[metric.component].append(metric)
            self.metrics_by_type[metric.metric_type].append(metric)
    
    def get_metrics_by_component(self, component: str, limit: int = 100) -> List[PerformanceMetric]:
        """Get metrics for specific component."""
        return list(self.metrics_by_component[component])[-limit:]
    
    def get_metrics_by_type(self, metric_type: MetricType, limit: int = 100) -> List[PerformanceMetric]:
        """Get metrics of specific type."""
        return list(self.metrics_by_type[metric_type])[-limit:]
    
    def get_latest_metrics(self, limit: int = 100) -> List[PerformanceMetric]:
        """Get latest metrics."""
        return list(self.metrics)[-limit:]
    
    def _map_metric_name_to_type(self, metric_name: str) -> Optional[MetricType]:
        """Map metric name to metric type."""
        mapping = {
            'response_time_ms': MetricType.RESPONSE_TIME,
            'memory_usage_mb': MetricType.MEMORY_USAGE,
            'cpu_usage_percent': MetricType.CPU_USAGE,
            'throughput_requests_per_sec': MetricType.THROUGHPUT,
            'error_rate': MetricType.ERROR_RATE,
            'success_rate': MetricType.SUCCESS_RATE
        }
        return mapping.get(metric_name)

class PerformanceAnalyzer:
    """
    Analyze performance metrics and detect issues.
    
    SpecBlock:
    - responsibility: "Analyze performance metrics and detect issues"
    - must_never: "Miss critical performance issues", "Provide inaccurate analysis"
    - performance_budget: "15ms average, 30ms maximum"
    - security_level: "medium"
    """
    
    def __init__(self):
        self.thresholds = {
            MetricType.RESPONSE_TIME: 400.0,  # 400ms max response time
            MetricType.MEMORY_USAGE: 80.0,    # 80% max memory usage
            MetricType.CPU_USAGE: 80.0,       # 80% max CPU usage
            MetricType.THROUGHPUT: 10.0,      # 10 requests per second min
            MetricType.ERROR_RATE: 5.0,       # 5% max error rate
            MetricType.SUCCESS_RATE: 95.0     # 95% min success rate
        }
    
    def analyze_metrics(self, metrics: List[PerformanceMetric]) -> List[PerformanceAlert]:
        """Analyze metrics and generate alerts."""
        alerts = []
        
        # Group metrics by type and component
        metrics_by_type = defaultdict(list)
        metrics_by_component = defaultdict(list)
        
        for metric in metrics:
            metrics_by_type[metric.metric_type].append(metric)
            metrics_by_component[metric.component].append(metric)
        
        # Analyze each metric type
        for metric_type, type_metrics in metrics_by_type.items():
            if not type_metrics:
                continue
            
            # Calculate statistics
            values = [m.value for m in type_metrics]
            avg_value = sum(values) / len(values)
            max_value = max(values)
            min_value = min(values)
            
            # Check thresholds
            threshold = self.thresholds.get(metric_type)
            if threshold is not None:
                if metric_type in [MetricType.RESPONSE_TIME, MetricType.MEMORY_USAGE, MetricType.CPU_USAGE, MetricType.ERROR_RATE]:
                    # Higher is worse
                    if max_value > threshold:
                        severity = self._calculate_severity(max_value, threshold, "high")
                        alert = PerformanceAlert(
                            alert_id=f"{metric_type.value}_{int(time.time())}",
                            metric_type=metric_type,
                            threshold=threshold,
                            current_value=max_value,
                            severity=severity,
                            message=f"{metric_type.value} exceeded threshold: {max_value:.2f} > {threshold:.2f}",
                            timestamp=time.time(),
                            component=type_metrics[0].component
                        )
                        alerts.append(alert)
                
                elif metric_type in [MetricType.THROUGHPUT, MetricType.SUCCESS_RATE]:
                    # Lower is worse
                    if min_value < threshold:
                        severity = self._calculate_severity(threshold, min_value, "low")
                        alert = PerformanceAlert(
                            alert_id=f"{metric_type.value}_{int(time.time())}",
                            metric_type=metric_type,
                            threshold=threshold,
                            current_value=min_value,
                            severity=severity,
                            message=f"{metric_type.value} below threshold: {min_value:.2f} < {threshold:.2f}",
                            timestamp=time.time(),
                            component=type_metrics[0].component
                        )
                        alerts.append(alert)
        
        return alerts
    
    def _calculate_severity(self, value: float, threshold: float, direction: str) -> str:
        """Calculate alert severity based on how much threshold is exceeded."""
        if direction == "high":
            ratio = value / threshold
        else:
            ratio = threshold / value
        
        if ratio >= 2.0:
            return "critical"
        elif ratio >= 1.5:
            return "high"
        elif ratio >= 1.2:
            return "medium"
        else:
            return "low"
    
    def get_performance_summary(self, metrics: List[PerformanceMetric]) -> Dict[str, Any]:
        """Get performance summary from metrics."""
        if not metrics:
            return {}
        
        # Group by metric type
        metrics_by_type = defaultdict(list)
        for metric in metrics:
            metrics_by_type[metric.metric_type].append(metric)
        
        summary = {}
        for metric_type, type_metrics in metrics_by_type.items():
            values = [m.value for m in type_metrics]
            summary[metric_type.value] = {
                'count': len(values),
                'average': sum(values) / len(values),
                'minimum': min(values),
                'maximum': max(values),
                'latest': values[-1] if values else 0
            }
        
        return summary

class PerformanceOptimizer:
    """
    Provide performance optimization recommendations.
    
    SpecBlock:
    - responsibility: "Provide performance optimization recommendations"
    - must_never: "Provide incorrect recommendations", "Ignore critical performance issues"
    - performance_budget: "20ms average, 40ms maximum"
    - security_level: "medium"
    """
    
    def __init__(self):
        self.optimization_rules = {
            MetricType.RESPONSE_TIME: self._optimize_response_time,
            MetricType.MEMORY_USAGE: self._optimize_memory_usage,
            MetricType.CPU_USAGE: self._optimize_cpu_usage,
            MetricType.THROUGHPUT: self._optimize_throughput,
            MetricType.ERROR_RATE: self._optimize_error_rate,
            MetricType.SUCCESS_RATE: self._optimize_success_rate
        }
    
    def get_optimization_recommendations(self, alerts: List[PerformanceAlert]) -> List[Dict[str, Any]]:
        """Get optimization recommendations based on alerts."""
        recommendations = []
        
        for alert in alerts:
            if alert.metric_type in self.optimization_rules:
                rule_func = self.optimization_rules[alert.metric_type]
                recommendation = rule_func(alert)
                if recommendation:
                    recommendations.append(recommendation)
        
        return recommendations
    
    def _optimize_response_time(self, alert: PerformanceAlert) -> Dict[str, Any]:
        """Optimize response time."""
        return {
            'metric_type': 'response_time',
            'severity': alert.severity,
            'current_value': alert.current_value,
            'threshold': alert.threshold,
            'recommendations': [
                'Optimize context analysis algorithm',
                'Improve tool selection efficiency',
                'Cache frequently used patterns',
                'Reduce server management overhead',
                'Implement request batching'
            ],
            'priority': 'high' if alert.severity in ['critical', 'high'] else 'medium'
        }
    
    def _optimize_memory_usage(self, alert: PerformanceAlert) -> Dict[str, Any]:
        """Optimize memory usage."""
        return {
            'metric_type': 'memory_usage',
            'severity': alert.severity,
            'current_value': alert.current_value,
            'threshold': alert.threshold,
            'recommendations': [
                'Implement memory pooling',
                'Reduce pattern storage size',
                'Optimize data structures',
                'Implement garbage collection',
                'Use lazy loading for patterns'
            ],
            'priority': 'high' if alert.severity in ['critical', 'high'] else 'medium'
        }
    
    def _optimize_cpu_usage(self, alert: PerformanceAlert) -> Dict[str, Any]:
        """Optimize CPU usage."""
        return {
            'metric_type': 'cpu_usage',
            'severity': alert.severity,
            'current_value': alert.current_value,
            'threshold': alert.threshold,
            'recommendations': [
                'Optimize algorithm complexity',
                'Implement caching strategies',
                'Use asynchronous processing',
                'Reduce context analysis frequency',
                'Implement request queuing'
            ],
            'priority': 'high' if alert.severity in ['critical', 'high'] else 'medium'
        }
    
    def _optimize_throughput(self, alert: PerformanceAlert) -> Dict[str, Any]:
        """Optimize throughput."""
        return {
            'metric_type': 'throughput',
            'severity': alert.severity,
            'current_value': alert.current_value,
            'threshold': alert.threshold,
            'recommendations': [
                'Implement parallel processing',
                'Optimize request handling',
                'Reduce response time',
                'Implement connection pooling',
                'Use load balancing'
            ],
            'priority': 'high' if alert.severity in ['critical', 'high'] else 'medium'
        }
    
    def _optimize_error_rate(self, alert: PerformanceAlert) -> Dict[str, Any]:
        """Optimize error rate."""
        return {
            'metric_type': 'error_rate',
            'severity': alert.severity,
            'current_value': alert.current_value,
            'threshold': alert.threshold,
            'recommendations': [
                'Improve error handling',
                'Add input validation',
                'Implement retry mechanisms',
                'Add comprehensive logging',
                'Improve error recovery'
            ],
            'priority': 'critical' if alert.severity in ['critical', 'high'] else 'high'
        }
    
    def _optimize_success_rate(self, alert: PerformanceAlert) -> Dict[str, Any]:
        """Optimize success rate."""
        return {
            'metric_type': 'success_rate',
            'severity': alert.severity,
            'current_value': alert.current_value,
            'threshold': alert.threshold,
            'recommendations': [
                'Improve tool selection accuracy',
                'Enhance context analysis',
                'Optimize server management',
                'Improve error handling',
                'Add fallback mechanisms'
            ],
            'priority': 'critical' if alert.severity in ['critical', 'high'] else 'high'
        }

class PerformanceMonitor:
    """
    Main performance monitor.
    
    SpecBlock:
    - responsibility: "Monitor system performance and provide optimization recommendations"
    - must_never: "Miss critical performance issues", "Provide inaccurate performance metrics"
    - performance_budget: "10ms average, 25ms maximum"
    - security_level: "medium"
    """
    
    def __init__(self, collection_interval: float = 1.0):
        self.collection_interval = collection_interval
        self.collector = PerformanceCollector()
        self.analyzer = PerformanceAnalyzer()
        self.optimizer = PerformanceOptimizer()
        
        self.monitoring_thread = None
        self.running = False
        self.alerts: List[PerformanceAlert] = []
    
    def start(self) -> None:
        """Start performance monitoring."""
        if self.running:
            return
        
        self.running = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
    
    def stop(self) -> None:
        """Stop performance monitoring."""
        self.running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
    
    def _monitoring_loop(self) -> None:
        """Main monitoring loop."""
        while self.running:
            try:
                # Collect system metrics
                system_metrics = self.collector.collect_system_metrics()
                self.collector.add_metrics(system_metrics)
                
                # Analyze metrics
                recent_metrics = self.collector.get_latest_metrics(100)
                alerts = self.analyzer.analyze_metrics(recent_metrics)
                
                # Add new alerts
                for alert in alerts:
                    if not any(a.alert_id == alert.alert_id for a in self.alerts):
                        self.alerts.append(alert)
                
                # Keep only recent alerts (last 100)
                self.alerts = self.alerts[-100:]
                
                time.sleep(self.collection_interval)
                
            except Exception as e:
                print(f"Error in performance monitoring: {e}")
                time.sleep(5)
    
    def add_component_metrics(self, component: str, metrics_data: Dict[str, float]) -> None:
        """Add component-specific metrics."""
        metrics = self.collector.collect_component_metrics(component, metrics_data)
        self.collector.add_metrics(metrics)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        recent_metrics = self.collector.get_latest_metrics(100)
        summary = self.analyzer.get_performance_summary(recent_metrics)
        
        return {
            'summary': summary,
            'alerts': [
                {
                    'alert_id': alert.alert_id,
                    'metric_type': alert.metric_type.value,
                    'severity': alert.severity,
                    'message': alert.message,
                    'timestamp': alert.timestamp,
                    'component': alert.component
                }
                for alert in self.alerts[-20:]  # Last 20 alerts
            ],
            'total_alerts': len(self.alerts),
            'collection_interval': self.collection_interval
        }
    
    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Get optimization recommendations."""
        return self.optimizer.get_optimization_recommendations(self.alerts)
    
    def get_metrics_by_component(self, component: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get metrics for specific component."""
        metrics = self.collector.get_metrics_by_component(component, limit)
        return [
            {
                'metric_type': metric.metric_type.value,
                'value': metric.value,
                'timestamp': metric.timestamp,
                'component': metric.component,
                'context': metric.context
            }
            for metric in metrics
        ]
    
    def get_metrics_by_type(self, metric_type: MetricType, limit: int = 100) -> List[Dict[str, Any]]:
        """Get metrics of specific type."""
        metrics = self.collector.get_metrics_by_type(metric_type, limit)
        return [
            {
                'metric_type': metric.metric_type.value,
                'value': metric.value,
                'timestamp': metric.timestamp,
                'component': metric.component,
                'context': metric.context
            }
            for metric in metrics
        ]
    
    def export_metrics(self, filepath: str) -> None:
        """Export metrics to file."""
        metrics_data = {
            'summary': self.get_performance_summary(),
            'recommendations': self.get_optimization_recommendations(),
            'export_timestamp': time.time()
        }
        
        with open(filepath, 'w') as f:
            json.dump(metrics_data, f, indent=2)

if __name__ == "__main__":
    # Test the performance monitor
    monitor = PerformanceMonitor(collection_interval=0.5)
    
    # Start monitoring
    monitor.start()
    print("Performance monitoring started")
    
    try:
        # Add some test metrics
        for i in range(10):
            test_metrics = {
                'response_time_ms': 100 + i * 10,
                'memory_usage_mb': 50 + i * 5,
                'cpu_usage_percent': 20 + i * 2,
                'success_rate': 95 - i
            }
            monitor.add_component_metrics('test_component', test_metrics)
            time.sleep(0.1)
        
        # Wait for monitoring to collect data
        time.sleep(2)
        
        # Get performance summary
        summary = monitor.get_performance_summary()
        print(f"Performance Summary: {json.dumps(summary, indent=2)}")
        
        # Get optimization recommendations
        recommendations = monitor.get_optimization_recommendations()
        print(f"Optimization Recommendations: {json.dumps(recommendations, indent=2)}")
        
        # Export metrics
        monitor.export_metrics("performance_metrics.json")
        print("Metrics exported to performance_metrics.json")
        
    finally:
        # Stop monitoring
        monitor.stop()
        print("Performance monitoring stopped")
