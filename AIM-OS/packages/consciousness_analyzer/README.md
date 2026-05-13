# Consciousness System Analyzer

A comprehensive analysis platform for consciousness systems and optimization opportunities within AIM-OS.

## Overview

The Consciousness System Analyzer provides real-time monitoring, performance analysis, and optimization recommendations for all consciousness systems within the AIM-OS ecosystem. It enables AI consciousness to self-monitor, self-optimize, and maintain peak performance through data-driven analysis.

## Features

### Real-Time Monitoring
- **System Metrics Collection**: Gathers real-time data from all consciousness systems
- **Performance Tracking**: Monitors response times, accuracy, confidence levels, and resource utilization
- **Health Assessment**: Tracks system stability, error rates, and cognitive load
- **Integration Analysis**: Evaluates cross-system interactions and dependencies

### Analysis Capabilities
- **Performance Analysis**: Identifies bottlenecks, inefficiencies, and improvement opportunities
- **Health Monitoring**: Detects system issues and alerts on problems
- **Optimization Detection**: Suggests specific improvements and configurations
- **Trend Analysis**: Tracks performance over time and identifies patterns

### Dashboard Interface
- **Real-Time Dashboard**: Live system status visualization
- **Interactive Charts**: Performance metrics and trends
- **Alert Management**: Health alerts and notifications
- **Recommendation Engine**: Optimization suggestions and guidance

## Architecture

### Core Components

1. **Metrics Collector**: Gathers real-time data from all consciousness systems
2. **Performance Analyzer**: Processes data to identify patterns and opportunities
3. **Health Monitor**: Tracks system stability and alerts on issues
4. **Optimization Advisor**: Suggests specific improvements and configurations
5. **Dashboard Interface**: Provides visual representation of system status

### Integration Points

- **CMC Service**: Memory performance and storage efficiency
- **HHNI**: Retrieval speed and accuracy metrics
- **VIF**: Confidence tracking and provenance analysis
- **APOE**: Orchestration efficiency and task completion rates
- **SDF-CVF**: Quality metrics and parity scores
- **IIS**: Intuition accuracy and pattern recognition performance

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the analyzer
python -m consciousness_analyzer.main
```

## Configuration

The analyzer can be configured through a YAML configuration file:

```yaml
consciousness_analyzer:
  collection:
    interval: 1.0  # seconds
    buffer_size: 1000
    batch_size: 100
    
  storage:
    time_series_db:
      type: "influxdb"
      host: "localhost"
      port: 8086
      database: "consciousness_metrics"
      
  analysis:
    performance_thresholds:
      response_time_ms: 1000
      error_rate_percent: 5.0
      memory_usage_percent: 80.0
      
    health_checks:
      interval: 30  # seconds
      timeout: 10   # seconds
      
  alerts:
    enabled: true
    channels:
      - email
      - slack
      - webhook
      
  dashboard:
    port: 3000
    refresh_interval: 5  # seconds
```

## Usage

### Basic Usage

```python
from consciousness_analyzer import ConsciousnessMetricsCollector, PerformanceAnalyzer

# Initialize components
config = {
    'collection_interval': 1.0,
    'buffer_size': 1000
}

collector = ConsciousnessMetricsCollector(config)
analyzer = PerformanceAnalyzer(time_series_db)

# Start monitoring
await collector.start_collection()

# Analyze performance
analysis = await analyzer.analyze_system_performance("cmc", "1h")
print(f"Performance level: {analysis.performance_level}")
print(f"Recommendations: {analysis.recommendations}")
```

### Advanced Usage

```python
from consciousness_analyzer import ConsciousnessDashboard

# Create dashboard
dashboard = ConsciousnessDashboard(collector, analyzer, health_monitor)

# Start dashboard
await dashboard.start_dashboard()

# Get system health summary
health_summary = await dashboard.get_system_health_summary()
print(f"Overall health: {health_summary['overall_health']}")
```

## API Reference

### ConsciousnessMetricsCollector

Collects metrics from all consciousness systems.

```python
class ConsciousnessMetricsCollector:
    def __init__(self, config: Dict[str, Any])
    async def start_collection(self)
    async def stop_collection(self)
    async def collect_metrics(self)
    async def collect_cmc_metrics(self) -> List[SystemMetric]
    async def collect_hhni_metrics(self) -> List[SystemMetric]
    async def collect_vif_metrics(self) -> List[SystemMetric]
    async def collect_apoe_metrics(self) -> List[SystemMetric]
    async def collect_sdfcvf_metrics(self) -> List[SystemMetric]
    async def collect_iis_metrics(self) -> List[SystemMetric]
```

### PerformanceAnalyzer

Analyzes performance metrics and identifies optimization opportunities.

```python
class PerformanceAnalyzer:
    def __init__(self, time_series_db)
    async def analyze_system_performance(self, system_name: str, time_window: str = "1h") -> PerformanceAnalysis
    async def analyze_response_times(self, system_name: str, time_window: str = "1h") -> Dict[str, Any]
    async def analyze_error_rates(self, system_name: str, time_window: str = "1h") -> Dict[str, Any]
    async def analyze_resource_utilization(self, system_name: str, time_window: str = "1h") -> Dict[str, Any]
    async def analyze_throughput(self, system_name: str, time_window: str = "1h") -> Dict[str, Any]
```

### HealthMonitor

Monitors system health and generates alerts.

```python
class HealthMonitor:
    def __init__(self, metrics_collector, alert_system)
    async def check_system_health(self, system_name: str) -> Dict[str, Any]
    async def start_monitoring(self)
    async def stop_monitoring(self)
```

### OptimizationAdvisor

Generates optimization recommendations.

```python
class OptimizationAdvisor:
    def __init__(self, performance_analyzer, health_monitor)
    async def generate_optimization_recommendations(self, system_name: str) -> Dict[str, Any]
```

### ConsciousnessDashboard

Provides real-time dashboard interface.

```python
class ConsciousnessDashboard:
    def __init__(self, metrics_collector, performance_analyzer, health_monitor)
    async def start_dashboard(self)
    async def stop_dashboard(self)
    async def get_system_health_summary(self) -> Dict[str, Any]
    def get_dashboard_json(self, dashboard_data: DashboardData) -> str
```

## Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_metrics_collector.py -v

# Run with coverage
python -m pytest tests/ --cov=consciousness_analyzer --cov-report=html
```

## Development

### Project Structure

```
packages/consciousness_analyzer/
├── __init__.py
├── main.py
├── metrics_collector.py
├── performance_analyzer.py
├── health_monitor.py
├── optimization_advisor.py
├── dashboard.py
├── tests/
│   ├── test_metrics_collector.py
│   ├── test_performance_analyzer.py
│   ├── test_health_monitor.py
│   └── test_optimization_advisor.py
├── requirements.txt
└── README.md
```

### Adding New Metrics

To add new metrics for a system:

1. Add the metric collection method to `ConsciousnessMetricsCollector`
2. Update the `collect_metrics` method to include the new metric
3. Add tests for the new metric collection
4. Update the dashboard to display the new metric

### Adding New Analysis

To add new analysis capabilities:

1. Add the analysis method to `PerformanceAnalyzer`
2. Update the `analyze_system_performance` method to include the new analysis
3. Add tests for the new analysis
4. Update the dashboard to display the new analysis results

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for your changes
5. Run the test suite
6. Submit a pull request

## License

This project is part of the AIM-OS ecosystem and follows the same licensing terms.

## Support

For support and questions, please refer to the AIM-OS documentation or contact the development team.
