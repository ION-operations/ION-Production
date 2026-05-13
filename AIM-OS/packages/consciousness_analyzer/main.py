"""
Consciousness System Analyzer - Main Application

Main entry point for the consciousness system analyzer.
"""

import asyncio
import logging
import signal
import sys
from typing import Dict, Any

from consciousness_analyzer import (
    ConsciousnessMetricsCollector,
    PerformanceAnalyzer,
    HealthMonitor,
    OptimizationAdvisor,
    ConsciousnessDashboard
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ConsciousnessAnalyzerApp:
    """Main application class for the consciousness system analyzer"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.running = False
        
        # Initialize components
        self.metrics_collector = ConsciousnessMetricsCollector(
            config.get('metrics_collector', {})
        )
        
        # Mock time series database for now
        self.time_series_db = MockTimeSeriesDB()
        
        self.performance_analyzer = PerformanceAnalyzer(self.time_series_db)
        self.health_monitor = HealthMonitor(self.metrics_collector, MockAlertSystem())
        self.optimization_advisor = OptimizationAdvisor(
            self.performance_analyzer, 
            self.health_monitor
        )
        self.dashboard = ConsciousnessDashboard(
            self.metrics_collector,
            self.performance_analyzer,
            self.health_monitor
        )
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
    
    async def start(self):
        """Start the consciousness analyzer application"""
        logger.info("Starting Consciousness System Analyzer...")
        self.running = True
        
        try:
            # Start all components
            tasks = [
                asyncio.create_task(self.metrics_collector.start_collection()),
                asyncio.create_task(self.dashboard.start_dashboard()),
                asyncio.create_task(self.health_monitor.start_monitoring()),
                asyncio.create_task(self.optimization_advisor.start_analysis())
            ]
            
            # Wait for all tasks to complete
            await asyncio.gather(*tasks)
            
        except Exception as e:
            logger.error(f"Error in main application: {e}")
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Shutdown the consciousness analyzer application"""
        logger.info("Shutting down Consciousness System Analyzer...")
        
        try:
            # Stop all components
            await self.metrics_collector.stop_collection()
            await self.dashboard.stop_dashboard()
            await self.health_monitor.stop_monitoring()
            await self.optimization_advisor.stop_analysis()
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
        
        logger.info("Consciousness System Analyzer stopped")

class MockTimeSeriesDB:
    """Mock time series database for testing"""
    
    async def query(self, query: str):
        """Mock query method"""
        # Return mock data based on query
        if "response_time_ms" in query:
            return [{
                "avg_response_time": 150.0,
                "max_response_time": 300.0,
                "min_response_time": 50.0,
                "stddev_response_time": 75.0,
                "sample_count": 100
            }]
        elif "error_count" in query:
            return [{
                "total_errors": 5,
                "total_operations": 1000,
                "time_periods": 10
            }]
        elif "memory_usage_percent" in query:
            return [{
                "avg_memory_usage": 65.0,
                "max_memory_usage": 80.0,
                "avg_cpu_usage": 55.0,
                "max_cpu_usage": 70.0
            }]
        elif "throughput_ops_per_sec" in query:
            return [{
                "avg_throughput": 120.0,
                "max_throughput": 150.0,
                "min_throughput": 90.0,
                "throughput_stddev": 20.0
            }]
        else:
            return []

class MockAlertSystem:
    """Mock alert system for testing"""
    
    async def send_alert(self, alert_data):
        """Mock send alert method"""
        logger.info(f"Mock alert sent: {alert_data}")

class MockHealthMonitor:
    """Mock health monitor for testing"""
    
    async def start_monitoring(self):
        """Mock start monitoring method"""
        logger.info("Mock health monitoring started")
    
    async def stop_monitoring(self):
        """Mock stop monitoring method"""
        logger.info("Mock health monitoring stopped")

class MockOptimizationAdvisor:
    """Mock optimization advisor for testing"""
    
    async def start_analysis(self):
        """Mock start analysis method"""
        logger.info("Mock optimization analysis started")
    
    async def stop_analysis(self):
        """Mock stop analysis method"""
        logger.info("Mock optimization analysis stopped")

def main():
    """Main entry point"""
    # Default configuration
    config = {
        'metrics_collector': {
            'collection_interval': 1.0,
            'buffer_size': 1000
        },
        'dashboard': {
            'refresh_interval': 5.0
        },
        'health_monitor': {
            'check_interval': 30.0
        },
        'optimization_advisor': {
            'analysis_interval': 60.0
        }
    }
    
    # Create and run the application
    app = ConsciousnessAnalyzerApp(config)
    
    try:
        asyncio.run(app.start())
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
