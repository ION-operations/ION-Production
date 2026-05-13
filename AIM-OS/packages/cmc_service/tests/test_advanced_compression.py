"""
Tests for Advanced Compression Strategies
"""

import pytest
import json
import time
from advanced_compression import (
    AdvancedCompressor,
    AdaptiveCompressor,
    CompressionAlgorithm,
    CompressionResult,
    compress_data,
    compress_adaptive,
    get_compression_stats,
    get_usage_patterns,
    reset_compression_stats
)


class TestAdvancedCompressor:
    """Test AdvancedCompressor class"""
    
    def test_compression_algorithms(self):
        """Test all compression algorithms"""
        compressor = AdvancedCompressor()
        test_data = "This is a test string for compression testing. " * 100
        
        # Test each algorithm
        for algorithm in CompressionAlgorithm:
            result = compressor.compress(test_data, algorithm)
            
            assert isinstance(result, CompressionResult)
            assert result.algorithm == algorithm
            assert result.original_size > 0
            assert result.compressed_size >= 0
            assert 0 <= result.compression_ratio <= 1
            assert result.compression_time >= 0
            assert result.decompression_time >= 0
            assert isinstance(result.data, bytes)
    
    def test_compression_ratio(self):
        """Test compression ratio calculation"""
        compressor = AdvancedCompressor()
        test_data = "This is a test string for compression testing. " * 1000
        
        result = compressor.compress(test_data, CompressionAlgorithm.GZIP)
        
        assert result.compression_ratio < 1.0  # Should compress
        assert result.space_saved > 0
        assert result.efficiency_score > 0
    
    def test_auto_algorithm_selection(self):
        """Test automatic algorithm selection"""
        compressor = AdvancedCompressor()
        
        # Test different data sizes
        small_data = "small"
        medium_data = "medium data " * 100
        large_data = "large data " * 10000
        
        # Small data should use LZ4 or NONE
        result_small = compressor.compress(small_data)
        assert result_small.algorithm in [CompressionAlgorithm.LZ4, CompressionAlgorithm.NONE]
        
        # Medium data should use GZIP or LZ4
        result_medium = compressor.compress(medium_data)
        assert result_medium.algorithm in [CompressionAlgorithm.GZIP, CompressionAlgorithm.LZ4]
        
        # Large data should use GZIP or BROTLI
        result_large = compressor.compress(large_data)
        assert result_large.algorithm in [CompressionAlgorithm.GZIP, CompressionAlgorithm.BROTLI]
    
    def test_priority_selection(self):
        """Test priority-based algorithm selection"""
        compressor = AdvancedCompressor()
        test_data = "test data " * 1000
        
        # Speed priority should prefer LZ4
        result_speed = compressor.compress(test_data, priority="speed")
        assert result_speed.algorithm == CompressionAlgorithm.LZ4
        
        # Ratio priority should prefer BROTLI
        result_ratio = compressor.compress(test_data, priority="ratio")
        assert result_ratio.algorithm == CompressionAlgorithm.BROTLI
    
    def test_compression_stats(self):
        """Test compression statistics tracking"""
        compressor = AdvancedCompressor()
        test_data = "test data " * 100
        
        # Compress with different algorithms
        compressor.compress(test_data, CompressionAlgorithm.GZIP)
        compressor.compress(test_data, CompressionAlgorithm.LZ4)
        compressor.compress(test_data, CompressionAlgorithm.GZIP)
        
        stats = compressor.get_compression_stats()
        
        assert "gzip" in stats
        assert "lz4" in stats
        assert stats["gzip"]["count"] == 2
        assert stats["lz4"]["count"] == 1
        assert stats["gzip"]["avg_time"] > 0
        assert stats["lz4"]["avg_ratio"] > 0
    
    def test_reset_stats(self):
        """Test statistics reset"""
        compressor = AdvancedCompressor()
        test_data = "test data " * 100
        
        # Compress some data
        compressor.compress(test_data, CompressionAlgorithm.GZIP)
        
        # Check stats exist
        stats_before = compressor.get_compression_stats()
        assert len(stats_before) > 0
        
        # Reset stats
        compressor.reset_stats()
        
        # Check stats are reset
        stats_after = compressor.get_compression_stats()
        assert len(stats_after) == 0


class TestAdaptiveCompressor:
    """Test AdaptiveCompressor class"""
    
    def test_adaptive_compression(self):
        """Test adaptive compression"""
        compressor = AdaptiveCompressor()
        test_data = "test data " * 1000
        
        # First compression should use default strategy
        result1 = compressor.compress_adaptive(test_data, "test_context")
        assert isinstance(result1, CompressionResult)
        
        # Second compression should use learned pattern
        result2 = compressor.compress_adaptive(test_data, "test_context")
        assert isinstance(result2, CompressionResult)
        
        # Usage patterns should be updated
        patterns = compressor.get_usage_patterns()
        assert "test_context" in patterns
    
    def test_context_learning(self):
        """Test context-based learning"""
        compressor = AdaptiveCompressor()
        test_data = "test data " * 1000
        
        # Compress with different contexts
        compressor.compress_adaptive(test_data, "context1")
        compressor.compress_adaptive(test_data, "context2")
        compressor.compress_adaptive(test_data, "context1")
        
        patterns = compressor.get_usage_patterns()
        assert "context1" in patterns
        assert "context2" in patterns
        assert patterns["context1"]["gzip"]["count"] == 2
        assert patterns["context2"]["gzip"]["count"] == 1
    
    def test_size_range_tracking(self):
        """Test size range tracking"""
        compressor = AdaptiveCompressor()
        
        # Test different size ranges
        tiny_data = "tiny"
        small_data = "small " * 10
        medium_data = "medium " * 100
        large_data = "large " * 1000
        
        compressor.compress_adaptive(tiny_data, "test_context")
        compressor.compress_adaptive(small_data, "test_context")
        compressor.compress_adaptive(medium_data, "test_context")
        compressor.compress_adaptive(large_data, "test_context")
        
        patterns = compressor.get_usage_patterns()
        context_pattern = patterns["test_context"]
        # Get the first available algorithm
        algorithm_key = list(context_pattern.keys())[0]
        context_pattern = context_pattern[algorithm_key]
        
        # Check that size ranges are tracked (at least some of them)
        size_ranges = context_pattern["size_ranges"]
        assert len(size_ranges) >= 2  # Should have at least 2 size ranges
        assert "tiny" in size_ranges or "small" in size_ranges


class TestCompressionFunctions:
    """Test compression functions"""
    
    def test_compress_data_function(self):
        """Test compress_data function"""
        test_data = "test data " * 100
        
        result = compress_data(test_data)
        assert isinstance(result, CompressionResult)
        assert result.original_size > 0
    
    def test_compress_adaptive_function(self):
        """Test compress_adaptive function"""
        test_data = "test data " * 100
        
        result = compress_adaptive(test_data, "test_context")
        assert isinstance(result, CompressionResult)
        assert result.original_size > 0
    
    def test_get_compression_stats_function(self):
        """Test get_compression_stats function"""
        test_data = "test data " * 100
        
        # Compress some data
        compress_data(test_data, CompressionAlgorithm.GZIP)
        
        # Get stats
        stats = get_compression_stats()
        assert isinstance(stats, dict)
    
    def test_get_usage_patterns_function(self):
        """Test get_usage_patterns function"""
        test_data = "test data " * 100
        
        # Compress with adaptive
        compress_adaptive(test_data, "test_context")
        
        # Get patterns
        patterns = get_usage_patterns()
        assert isinstance(patterns, dict)
    
    def test_reset_compression_stats_function(self):
        """Test reset_compression_stats function"""
        test_data = "test data " * 100
        
        # Compress some data
        compress_data(test_data, CompressionAlgorithm.GZIP)
        
        # Get stats
        stats_before = get_compression_stats()
        assert len(stats_before) > 0
        
        # Reset stats
        reset_compression_stats()
        
        # Check stats are reset
        stats_after = get_compression_stats()
        assert len(stats_after) == 0


class TestCompressionIntegration:
    """Test compression integration with different data types"""
    
    def test_string_compression(self):
        """Test string compression"""
        test_string = "This is a test string for compression testing. " * 100
        
        result = compress_data(test_string)
        assert isinstance(result, CompressionResult)
        assert result.original_size > 0
        assert result.compression_ratio < 1.0
    
    def test_bytes_compression(self):
        """Test bytes compression"""
        test_bytes = b"This is test bytes for compression testing. " * 100
        
        result = compress_data(test_bytes)
        assert isinstance(result, CompressionResult)
        assert result.original_size > 0
        assert result.compression_ratio < 1.0
    
    def test_dict_compression(self):
        """Test dictionary compression"""
        test_dict = {
            "key1": "value1",
            "key2": "value2",
            "nested": {
                "inner_key": "inner_value",
                "numbers": [1, 2, 3, 4, 5]
            }
        }
        
        result = compress_data(test_dict)
        assert isinstance(result, CompressionResult)
        assert result.original_size > 0
        # For small data, compression might not be applied
        assert result.compression_ratio <= 1.0
    
    def test_large_data_compression(self):
        """Test large data compression"""
        large_data = "This is a large test string for compression testing. " * 10000
        
        result = compress_data(large_data)
        assert isinstance(result, CompressionResult)
        assert result.original_size > 100000  # Should be large
        assert result.compression_ratio < 0.5  # Should compress well
    
    def test_compression_roundtrip(self):
        """Test compression and decompression roundtrip"""
        compressor = AdvancedCompressor()
        original_data = "This is test data for roundtrip testing. " * 100
        
        # Compress
        result = compressor.compress(original_data, CompressionAlgorithm.GZIP)
        
        # Decompress
        decompressed = compressor._decompress_data(result.data, result.algorithm)
        
        # Should match original
        assert decompressed.decode('utf-8') == original_data


if __name__ == "__main__":
    pytest.main([__file__])
