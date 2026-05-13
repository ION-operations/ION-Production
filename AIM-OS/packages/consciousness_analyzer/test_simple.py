"""
Simple test script for Consciousness System Analyzer
"""

import asyncio
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from consciousness_analyzer import ConsciousnessMetricsCollector, SystemMetric
from datetime import datetime

async def test_basic_functionality():
    """Test basic functionality of the consciousness analyzer"""
    print("Testing Consciousness System Analyzer...")
    
    # Test SystemMetric creation
    print("1. Testing SystemMetric creation...")
    metric = SystemMetric(
        system_name="test_system",
        metric_type="test_metric",
        value=123.45,
        timestamp=datetime.now(),
        metadata={"test": "data"}
    )
    print(f"   [OK] Created metric: {metric.system_name} - {metric.metric_type} = {metric.value}")
    
    # Test ConsciousnessMetricsCollector initialization
    print("2. Testing ConsciousnessMetricsCollector initialization...")
    config = {
        'collection_interval': 0.1,
        'buffer_size': 10
    }
    collector = ConsciousnessMetricsCollector(config)
    print(f"   [OK] Initialized collector with interval: {collector.collection_interval}s")
    
    # Test CMC metrics collection
    print("3. Testing CMC metrics collection...")
    try:
        cmc_metrics = await collector.collect_cmc_metrics()
        print(f"   [OK] Collected {len(cmc_metrics)} CMC metrics")
        for metric in cmc_metrics:
            print(f"     - {metric.metric_type}: {metric.value}")
    except Exception as e:
        print(f"   [ERROR] Error collecting CMC metrics: {e}")
    
    # Test HHNI metrics collection
    print("4. Testing HHNI metrics collection...")
    try:
        hhni_metrics = await collector.collect_hhni_metrics()
        print(f"   [OK] Collected {len(hhni_metrics)} HHNI metrics")
        for metric in hhni_metrics:
            print(f"     - {metric.metric_type}: {metric.value}")
    except Exception as e:
        print(f"   [ERROR] Error collecting HHNI metrics: {e}")
    
    # Test metrics storage
    print("5. Testing metrics storage...")
    try:
        test_metrics = [metric]
        await collector.store_metrics(test_metrics)
        print(f"   [OK] Stored {len(test_metrics)} metrics in buffer")
        print(f"   [OK] Buffer size: {len(collector.metrics_buffer)}")
    except Exception as e:
        print(f"   [ERROR] Error storing metrics: {e}")
    
    print("\n[SUCCESS] Basic functionality test completed!")

if __name__ == "__main__":
    asyncio.run(test_basic_functionality())
