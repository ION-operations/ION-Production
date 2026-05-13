"""
Consciousness Health Monitor

Monitors system health and generates alerts for consciousness systems.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)

@dataclass
class HealthCheck:
    """Represents a health check result"""
    system_name: str
    check_type: str
    status: str  # healthy, warning, critical, error
    message: str
    timestamp: datetime
    metrics: Dict[str, Any]

class HealthMonitor:
    """Monitors system health and generates alerts"""
    
    def __init__(self, metrics_collector, alert_system):
        self.metrics_collector = metrics_collector
        self.alert_system = alert_system
        self.running = False
        self.health_thresholds = {
            "response_time_ms": 1000,
            "error_rate_percent": 5.0,
            "memory_usage_percent": 80.0,
            "cpu_usage_percent": 80.0
        }
    
    async def start_monitoring(self):
        """Start the health monitoring loop"""
        self.running = True
        logger.info("Starting consciousness health monitoring")
        
        while self.running:
            try:
                await self.perform_health_checks()
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Error in health monitoring: {e}")
                await asyncio.sleep(30)
    
    async def stop_monitoring(self):
        """Stop the health monitoring loop"""
        self.running = False
        logger.info("Stopped consciousness health monitoring")
    
    async def perform_health_checks(self):
        """Perform health checks on all consciousness systems"""
        systems = ["cmc", "hhni", "vif", "apoe", "sdfcvf", "iis"]
        
        for system in systems:
            try:
                health_status = await self.check_system_health(system)
                
                # Send alert if system is not healthy
                if health_status["overall_health"] != "healthy":
                    await self.alert_system.send_alert(health_status)
                    
            except Exception as e:
                logger.error(f"Error checking health for {system}: {e}")
    
    async def check_system_health(self, system_name: str) -> Dict[str, Any]:
        """Check overall health of a consciousness system"""
        health_status = {
            "system_name": system_name,
            "overall_health": "healthy",
            "checks": [],
            "alerts": []
        }
        
        try:
            # Check response times
            response_time_check = await self.check_response_times(system_name)
            health_status["checks"].append(response_time_check)
            
            # Check error rates
            error_rate_check = await self.check_error_rates(system_name)
            health_status["checks"].append(error_rate_check)
            
            # Check resource usage
            resource_check = await self.check_resource_usage(system_name)
            health_status["checks"].append(resource_check)
            
            # Determine overall health
            health_status["overall_health"] = self.determine_overall_health(health_status["checks"])
            
            # Generate alerts if needed
            if health_status["overall_health"] != "healthy":
                health_status["alerts"] = self.generate_health_alerts(health_status["checks"])
            
        except Exception as e:
            logger.error(f"Error checking health for {system_name}: {e}")
            health_status["overall_health"] = "error"
            health_status["alerts"] = [f"Health check error: {e}"]
        
        return health_status
    
    async def check_response_times(self, system_name: str) -> HealthCheck:
        """Check response time health for a system"""
        try:
            # In a real implementation, this would get actual response time data
            # For now, we'll simulate based on system name
            if system_name == "cmc":
                response_time = 150.0
            elif system_name == "hhni":
                response_time = 50.0
            elif system_name == "vif":
                response_time = 75.0
            elif system_name == "apoe":
                response_time = 200.0
            elif system_name == "sdfcvf":
                response_time = 100.0
            elif system_name == "iis":
                response_time = 125.0
            else:
                response_time = 100.0
            
            # Determine status based on threshold
            threshold = self.health_thresholds.get("response_time_ms", 1000)
            if response_time > threshold:
                status = "critical"
                message = f"Response time {response_time}ms exceeds threshold {threshold}ms"
            elif response_time > threshold * 0.8:
                status = "warning"
                message = f"Response time {response_time}ms approaching threshold {threshold}ms"
            else:
                status = "healthy"
                message = f"Response time {response_time}ms is within acceptable range"
            
            return HealthCheck(
                system_name=system_name,
                check_type="response_time",
                status=status,
                message=message,
                timestamp=datetime.now(),
                metrics={"response_time_ms": response_time, "threshold_ms": threshold}
            )
            
        except Exception as e:
            logger.error(f"Error checking response times for {system_name}: {e}")
            return HealthCheck(
                system_name=system_name,
                check_type="response_time",
                status="error",
                message=f"Error checking response times: {e}",
                timestamp=datetime.now(),
                metrics={}
            )
    
    async def check_error_rates(self, system_name: str) -> HealthCheck:
        """Check error rate health for a system"""
        try:
            # In a real implementation, this would get actual error rate data
            # For now, we'll simulate based on system name
            if system_name == "cmc":
                error_rate = 2.0
            elif system_name == "hhni":
                error_rate = 1.0
            elif system_name == "vif":
                error_rate = 0.5
            elif system_name == "apoe":
                error_rate = 3.0
            elif system_name == "sdfcvf":
                error_rate = 1.5
            elif system_name == "iis":
                error_rate = 2.5
            else:
                error_rate = 1.0
            
            # Determine status based on threshold
            threshold = self.health_thresholds.get("error_rate_percent", 5.0)
            if error_rate > threshold:
                status = "critical"
                message = f"Error rate {error_rate}% exceeds threshold {threshold}%"
            elif error_rate > threshold * 0.6:
                status = "warning"
                message = f"Error rate {error_rate}% approaching threshold {threshold}%"
            else:
                status = "healthy"
                message = f"Error rate {error_rate}% is within acceptable range"
            
            return HealthCheck(
                system_name=system_name,
                check_type="error_rate",
                status=status,
                message=message,
                timestamp=datetime.now(),
                metrics={"error_rate_percent": error_rate, "threshold_percent": threshold}
            )
            
        except Exception as e:
            logger.error(f"Error checking error rates for {system_name}: {e}")
            return HealthCheck(
                system_name=system_name,
                check_type="error_rate",
                status="error",
                message=f"Error checking error rates: {e}",
                timestamp=datetime.now(),
                metrics={}
            )
    
    async def check_resource_usage(self, system_name: str) -> HealthCheck:
        """Check resource usage health for a system"""
        try:
            # In a real implementation, this would get actual resource usage data
            # For now, we'll simulate based on system name
            if system_name == "cmc":
                memory_usage = 65.0
                cpu_usage = 55.0
            elif system_name == "hhni":
                memory_usage = 45.0
                cpu_usage = 40.0
            elif system_name == "vif":
                memory_usage = 35.0
                cpu_usage = 30.0
            elif system_name == "apoe":
                memory_usage = 75.0
                cpu_usage = 70.0
            elif system_name == "sdfcvf":
                memory_usage = 50.0
                cpu_usage = 45.0
            elif system_name == "iis":
                memory_usage = 60.0
                cpu_usage = 55.0
            else:
                memory_usage = 50.0
                cpu_usage = 50.0
            
            # Determine status based on thresholds
            memory_threshold = self.health_thresholds.get("memory_usage_percent", 80.0)
            cpu_threshold = self.health_thresholds.get("cpu_usage_percent", 80.0)
            
            if memory_usage > memory_threshold or cpu_usage > cpu_threshold:
                status = "critical"
                message = f"High resource usage: Memory {memory_usage}%, CPU {cpu_usage}%"
            elif memory_usage > memory_threshold * 0.8 or cpu_usage > cpu_threshold * 0.8:
                status = "warning"
                message = f"Resource usage approaching limits: Memory {memory_usage}%, CPU {cpu_usage}%"
            else:
                status = "healthy"
                message = f"Resource usage normal: Memory {memory_usage}%, CPU {cpu_usage}%"
            
            return HealthCheck(
                system_name=system_name,
                check_type="resource_usage",
                status=status,
                message=message,
                timestamp=datetime.now(),
                metrics={
                    "memory_usage_percent": memory_usage,
                    "cpu_usage_percent": cpu_usage,
                    "memory_threshold_percent": memory_threshold,
                    "cpu_threshold_percent": cpu_threshold
                }
            )
            
        except Exception as e:
            logger.error(f"Error checking resource usage for {system_name}: {e}")
            return HealthCheck(
                system_name=system_name,
                check_type="resource_usage",
                status="error",
                message=f"Error checking resource usage: {e}",
                timestamp=datetime.now(),
                metrics={}
            )
    
    def determine_overall_health(self, checks: List[HealthCheck]) -> str:
        """Determine overall system health based on individual checks"""
        if not checks:
            return "unknown"
        
        critical_issues = sum(1 for check in checks if check.status == "critical")
        warning_issues = sum(1 for check in checks if check.status == "warning")
        error_issues = sum(1 for check in checks if check.status == "error")
        
        if critical_issues > 0 or error_issues > 0:
            return "critical"
        elif warning_issues > 2:
            return "warning"
        else:
            return "healthy"
    
    def generate_health_alerts(self, checks: List[HealthCheck]) -> List[str]:
        """Generate health alerts based on check results"""
        alerts = []
        
        for check in checks:
            if check.status == "critical":
                alerts.append(f"CRITICAL: {check.system_name} {check.check_type} - {check.message}")
            elif check.status == "warning":
                alerts.append(f"WARNING: {check.system_name} {check.check_type} - {check.message}")
            elif check.status == "error":
                alerts.append(f"ERROR: {check.system_name} {check.check_type} - {check.message}")
        
        return alerts
