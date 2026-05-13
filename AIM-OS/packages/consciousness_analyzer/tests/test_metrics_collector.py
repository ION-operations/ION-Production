"""
Tests for Consciousness Metrics Collector
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from consciousness_analyzer.metrics_collector import ConsciousnessMetricsCollector, SystemMetric

class TestConsciousnessMetricsCollector:
    """Test cases for ConsciousnessMetricsCollector"""
    
    @pytest.fixture
    def collector_config(self):
        """Test configuration for metrics collector"""
        return {
            'collection_interval': 0.1,
            'buffer_size': 10
        }
    
    @pytest.fixture
    def collector(self, collector_config):
        """Create a metrics collector instance for testing"""
        return ConsciousnessMetricsCollector(collector_config)
    
    def test_initialization(self, collector):
        """Test metrics collector initialization"""
        assert collector.collection_interval == 0.1
        assert collector.buffer_size == 10
        assert collector.running == False
        assert len(collector.metrics_buffer) == 0
    
    def test_system_metric_creation(self):
        """Test SystemMetric dataclass creation"""
        metric = SystemMetric(
            system_name="test_system",
            metric_type="test_metric",
            value=123.45,
            timestamp=datetime.now(),
            metadata={"test": "data"}
        )
        
        assert metric.system_name == "test_system"
        assert metric.metric_type == "test_metric"
        assert metric.value == 123.45
        assert isinstance(metric.timestamp, datetime)
        assert metric.metadata == {"test": "data"}
    
    @pytest.mark.asyncio
    async def test_start_stop_collection(self, collector):
        """Test starting and stopping metrics collection"""
        # Mock the collect_metrics method to avoid actual collection
        collector.collect_metrics = AsyncMock()
        
        # Start collection
        collection_task = asyncio.create_task(collector.start_collection())
        
        # Let it run for a short time
        await asyncio.sleep(0.2)
        
        # Stop collection
        await collector.stop_collection()
        
        # Wait for task to complete
        await collection_task
        
        # Verify collect_metrics was called
        assert collector.collect_metrics.call_count > 0
        assert collector.running == False
    
    @pytest.mark.asyncio
    async def test_collect_cmc_metrics(self, collector):
        """Test CMC metrics collection"""
        # Mock the CMC metric methods
        collector.get_cmc_memory_usage = AsyncMock(return_value=1024.0)
        collector.get_cmc_storage_efficiency = AsyncMock(return_value=0.85)
        collector.get_cmc_operation_count = AsyncMock(return_value=10.0)
        
        # Collect CMC metrics
        metrics = await collector.collect_cmc_metrics()
        
        # Verify metrics were collected
        assert len(metrics) == 3
        
        # Check memory usage metric
        memory_metric = next(m for m in metrics if m.metric_type == "memory_usage_bytes")
        assert memory_metric.system_name == "cmc"
        assert memory_metric.value == 1024.0
        assert memory_metric.metadata["component"] == "memory_store"
        
        # Check storage efficiency metric
        storage_metric = next(m for m in metrics if m.metric_type == "storage_efficiency_ratio")
        assert storage_metric.system_name == "cmc"
        assert storage_metric.value == 0.85
        assert storage_metric.metadata["component"] == "storage"
        
        # Check operation count metric
        ops_metric = next(m for m in metrics if m.metric_type == "operations_per_second")
        assert ops_metric.system_name == "cmc"
        assert ops_metric.value == 10.0
        assert ops_metric.metadata["component"] == "operations"
    
    @pytest.mark.asyncio
    async def test_collect_hhni_metrics(self, collector):
        """Test HHNI metrics collection"""
        # Mock the HHNI metric methods
        collector.get_hhni_search_latency = AsyncMock(return_value=50.0)
        collector.get_hhni_index_efficiency = AsyncMock(return_value=0.92)
        collector.get_hhni_search_accuracy = AsyncMock(return_value=95.0)
        
        # Collect HHNI metrics
        metrics = await collector.collect_hhni_metrics()
        
        # Verify metrics were collected
        assert len(metrics) == 3
        
        # Check search latency metric
        latency_metric = next(m for m in metrics if m.metric_type == "search_latency_ms")
        assert latency_metric.system_name == "hhni"
        assert latency_metric.value == 50.0
        assert latency_metric.metadata["component"] == "search_engine"
        
        # Check index efficiency metric
        efficiency_metric = next(m for m in metrics if m.metric_type == "index_efficiency_ratio")
        assert efficiency_metric.system_name == "hhni"
        assert efficiency_metric.value == 0.92
        assert efficiency_metric.metadata["component"] == "index"
        
        # Check search accuracy metric
        accuracy_metric = next(m for m in metrics if m.metric_type == "search_accuracy_percent")
        assert accuracy_metric.system_name == "hhni"
        assert accuracy_metric.value == 95.0
        assert accuracy_metric.metadata["component"] == "search_engine"
    
    @pytest.mark.asyncio
    async def test_store_metrics(self, collector):
        """Test metrics storage"""
        # Create test metrics
        test_metrics = [
            SystemMetric(
                system_name="test_system",
                metric_type="test_metric",
                value=123.45,
                timestamp=datetime.now(),
                metadata={"test": "data"}
            )
        ]
        
        # Mock the store_metrics_batch method
        collector.store_metrics_batch = AsyncMock()
        
        # Store metrics
        await collector.store_metrics(test_metrics)
        
        # Verify metrics were added to buffer
        assert len(collector.metrics_buffer) == 1
        assert collector.metrics_buffer[0] == test_metrics[0]
    
    @pytest.mark.asyncio
    async def test_flush_metrics_buffer(self, collector):
        """Test metrics buffer flushing"""
        # Add test metrics to buffer
        test_metrics = [
            SystemMetric(
                system_name="test_system",
                metric_type="test_metric",
                value=123.45,
                timestamp=datetime.now(),
                metadata={"test": "data"}
            )
        ]
        collector.metrics_buffer = test_metrics
        
        # Mock the store_metrics_batch method
        collector.store_metrics_batch = AsyncMock()
        
        # Flush buffer
        await collector.flush_metrics_buffer()
        
        # Verify buffer was cleared
        assert len(collector.metrics_buffer) == 0
        
        # Verify store_metrics_batch was called
        collector.store_metrics_batch.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_auto_flush_on_buffer_full(self, collector):
        """Test automatic buffer flushing when buffer is full"""
        # Set small buffer size for testing
        collector.buffer_size = 2
        
        # Mock the store_metrics_batch method
        collector.store_metrics_batch = AsyncMock()
        
        # Add metrics until buffer is full
        for i in range(3):
            metric = SystemMetric(
                system_name="test_system",
                metric_type="test_metric",
                value=float(i),
                timestamp=datetime.now(),
                metadata={"test": "data"}
            )
            await collector.store_metrics([metric])
        
        # Verify store_metrics_batch was called
        assert collector.store_metrics_batch.call_count > 0
    
    @pytest.mark.asyncio
    async def test_error_handling_in_collection(self, collector):
        """Test error handling during metrics collection"""
        # Mock a method to raise an exception
        collector.get_cmc_memory_usage = AsyncMock(side_effect=Exception("Test error"))
        collector.get_cmc_storage_efficiency = AsyncMock(return_value=0.85)
        collector.get_cmc_operation_count = AsyncMock(return_value=10.0)
        
        # Collect CMC metrics (should handle error gracefully)
        metrics = await collector.collect_cmc_metrics()
        
        # Should still return some metrics despite the error
        assert len(metrics) == 2  # storage_efficiency and operation_count
        assert all(m.metric_type != "memory_usage_bytes" for m in metrics)
    
    @pytest.mark.asyncio
    async def test_collect_metrics_integration(self, collector):
        """Test full metrics collection integration"""
        # Mock all metric collection methods
        collector.get_cmc_memory_usage = AsyncMock(return_value=1024.0)
        collector.get_cmc_storage_efficiency = AsyncMock(return_value=0.85)
        collector.get_cmc_operation_count = AsyncMock(return_value=10.0)
        collector.get_hhni_search_latency = AsyncMock(return_value=50.0)
        collector.get_hhni_index_efficiency = AsyncMock(return_value=0.92)
        collector.get_hhni_search_accuracy = AsyncMock(return_value=95.0)
        collector.get_vif_avg_confidence = AsyncMock(return_value=0.85)
        collector.get_vif_provenance_count = AsyncMock(return_value=1000.0)
        collector.get_apoe_task_completion_rate = AsyncMock(return_value=98.0)
        collector.get_apoe_resource_utilization = AsyncMock(return_value=75.0)
        collector.get_sdfcvf_avg_quality_score = AsyncMock(return_value=0.88)
        collector.get_sdfcvf_parity_score = AsyncMock(return_value=0.95)
        collector.get_iis_intuition_accuracy = AsyncMock(return_value=87.0)
        collector.get_iis_pattern_recognition_rate = AsyncMock(return_value=92.0)
        collector.store_metrics_batch = AsyncMock()
        
        # Collect all metrics
        await collector.collect_metrics()
        
        # Verify all metric collection methods were called
        assert collector.get_cmc_memory_usage.call_count == 1
        assert collector.get_cmc_storage_efficiency.call_count == 1
        assert collector.get_cmc_operation_count.call_count == 1
        assert collector.get_hhni_search_latency.call_count == 1
        assert collector.get_hhni_index_efficiency.call_count == 1
        assert collector.get_hhni_search_accuracy.call_count == 1
        assert collector.get_vif_avg_confidence.call_count == 1
        assert collector.get_vif_provenance_count.call_count == 1
        assert collector.get_apoe_task_completion_rate.call_count == 1
        assert collector.get_apoe_resource_utilization.call_count == 1
        assert collector.get_sdfcvf_avg_quality_score.call_count == 1
        assert collector.get_sdfcvf_parity_score.call_count == 1
        assert collector.get_iis_intuition_accuracy.call_count == 1
        assert collector.get_iis_pattern_recognition_rate.call_count == 1
