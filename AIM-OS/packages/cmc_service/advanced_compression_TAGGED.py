"""
Advanced Compression Strategies for CMC Service

This module provides multiple compression algorithms and intelligent
compression selection based on data type, size, and performance requirements.
"""

import gzip
import zlib

# Optional compression libraries
try:
    import lz4.frame
    LZ4_AVAILABLE = True
except ImportError:
    LZ4_AVAILABLE = False

try:
    import brotli
    BROTLI_AVAILABLE = True
except ImportError:
    BROTLI_AVAILABLE = False
import json
import logging
from typing import Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import time

logger = logging.getLogger(__name__)


# NL_TAG: VIF-MODEL-001 | Available compression algorithms | class CompressionAlgorithm | []
class CompressionAlgorithm(Enum):
    """Available compression algorithms"""
    NONE = "none"
    GZIP = "gzip"
    LZ4 = "lz4"
    BROTLI = "brotli"
    ZLIB = "zlib"


@dataclass
# NL_TAG: VIF-MODEL-002 | Result of compression operation | class CompressionResult | []
class CompressionResult:
    """Result of compression operation"""
    algorithm: CompressionAlgorithm
    original_size: int
    compressed_size: int
    compression_ratio: float
    compression_time: float
    decompression_time: float
    data: bytes
    
    @property
    def space_saved(self) -> int:
        """Calculate space saved in bytes"""
        return self.original_size - self.compressed_size
    
    @property
    def efficiency_score(self) -> float:
        """Calculate compression efficiency (ratio / time)"""
        if self.compression_time == 0:
            return float('inf')
        return self.compression_ratio / self.compression_time


# NL_TAG: VIF-MODEL-003 | Intelligent compression strategy selection | class CompressionStrategy | []
class CompressionStrategy:
    """Intelligent compression strategy selection"""
    
    def __init__(self):
        self.algorithm_performance = {
            CompressionAlgorithm.GZIP: {"ratio": 0.7, "speed": 0.8, "memory": 0.6},
            CompressionAlgorithm.LZ4: {"ratio": 0.6, "speed": 0.95, "memory": 0.9},
            CompressionAlgorithm.BROTLI: {"ratio": 0.8, "speed": 0.6, "memory": 0.5},
            CompressionAlgorithm.ZLIB: {"ratio": 0.65, "speed": 0.85, "memory": 0.7},
        }
    
    def select_algorithm(self, 
                        data_size: int, 
                        data_type: str = "text",
                        priority: str = "balanced") -> CompressionAlgorithm:
        """Select best compression algorithm based on data characteristics"""
        
        # For very small data, no compression
        if data_size < 100:
            return CompressionAlgorithm.NONE
        
        # For very large data, prioritize ratio
        if data_size > 1024 * 1024:  # 1MB
            if priority == "ratio":
                return CompressionAlgorithm.BROTLI
            else:
                return CompressionAlgorithm.GZIP
        
        # For medium data, balance speed and ratio
        if data_size > 1024:  # 1KB
            if priority == "speed":
                return CompressionAlgorithm.LZ4
            elif priority == "ratio":
                return CompressionAlgorithm.BROTLI
            else:
                return CompressionAlgorithm.GZIP
        
        # For small data, prioritize speed
        return CompressionAlgorithm.LZ4


# NL_TAG: VIF-MODEL-004 | Advanced compression system with multiple algorithms | class AdvancedCompressor | []
class AdvancedCompressor:
    """Advanced compression system with multiple algorithms"""
    
    def __init__(self):
        self.strategy = CompressionStrategy()
        self.compression_stats = {
            algorithm: {"count": 0, "total_time": 0.0, "total_ratio": 0.0}
            for algorithm in CompressionAlgorithm
        }
    
    def compress(self, 
                data: Union[str, bytes, Dict[str, Any]], 
                algorithm: Optional[CompressionAlgorithm] = None,
                priority: str = "balanced") -> CompressionResult:
        """Compress data using specified or auto-selected algorithm"""
        
        # Convert data to bytes
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        elif isinstance(data, dict):
            data_bytes = json.dumps(data, separators=(',', ':')).encode('utf-8')
        else:
            data_bytes = data
        
        original_size = len(data_bytes)
        
        # Auto-select algorithm if not specified
        if algorithm is None:
            algorithm = self.strategy.select_algorithm(
                original_size, 
                priority=priority
            )
        
        # Skip compression for very small data
        if algorithm == CompressionAlgorithm.NONE:
            return CompressionResult(
                algorithm=algorithm,
                original_size=original_size,
                compressed_size=original_size,
                compression_ratio=1.0,
                compression_time=0.0,
                decompression_time=0.0,
                data=data_bytes
            )
        
        # Compress data
        start_time = time.time()
        compressed_data = self._compress_data(data_bytes, algorithm)
        compression_time = time.time() - start_time
        
        # Test decompression time
        start_time = time.time()
        self._decompress_data(compressed_data, algorithm)
        decompression_time = time.time() - start_time
        
        compressed_size = len(compressed_data)
        compression_ratio = compressed_size / original_size if original_size > 0 else 1.0
        
        # Update statistics
        self.compression_stats[algorithm]["count"] += 1
        self.compression_stats[algorithm]["total_time"] += compression_time
        self.compression_stats[algorithm]["total_ratio"] += compression_ratio
        
        return CompressionResult(
            algorithm=algorithm,
            original_size=original_size,
            compressed_size=compressed_size,
            compression_ratio=compression_ratio,
            compression_time=compression_time,
            decompression_time=decompression_time,
            data=compressed_data
        )
    
    def _compress_data(self, data: bytes, algorithm: CompressionAlgorithm) -> bytes:
        """Compress data using specified algorithm"""
        try:
            if algorithm == CompressionAlgorithm.GZIP:
                return gzip.compress(data)
            elif algorithm == CompressionAlgorithm.LZ4:
                if LZ4_AVAILABLE:
                    return lz4.frame.compress(data)
                else:
                    logger.warning("LZ4 not available, falling back to gzip")
                    return gzip.compress(data)
            elif algorithm == CompressionAlgorithm.BROTLI:
                if BROTLI_AVAILABLE:
                    return brotli.compress(data)
                else:
                    logger.warning("Brotli not available, falling back to gzip")
                    return gzip.compress(data)
            elif algorithm == CompressionAlgorithm.ZLIB:
                return zlib.compress(data)
            else:
                return data
        except Exception as e:
            logger.error(f"Compression failed with {algorithm}: {e}")
            return data
    
    def _decompress_data(self, data: bytes, algorithm: CompressionAlgorithm) -> bytes:
        """Decompress data using specified algorithm"""
        try:
            if algorithm == CompressionAlgorithm.GZIP:
                return gzip.decompress(data)
            elif algorithm == CompressionAlgorithm.LZ4:
                if LZ4_AVAILABLE:
                    return lz4.frame.decompress(data)
                else:
                    logger.warning("LZ4 not available, falling back to gzip")
                    return gzip.decompress(data)
            elif algorithm == CompressionAlgorithm.BROTLI:
                if BROTLI_AVAILABLE:
                    return brotli.decompress(data)
                else:
                    logger.warning("Brotli not available, falling back to gzip")
                    return gzip.decompress(data)
            elif algorithm == CompressionAlgorithm.ZLIB:
                return zlib.decompress(data)
            else:
                return data
        except Exception as e:
            logger.error(f"Decompression failed with {algorithm}: {e}")
            return data
    
    def get_compression_stats(self) -> Dict[str, Any]:
        """Get compression statistics"""
        stats = {}
        for algorithm, data in self.compression_stats.items():
            if data["count"] > 0:
                stats[algorithm.value] = {
                    "count": data["count"],
                    "avg_time": data["total_time"] / data["count"],
                    "avg_ratio": data["total_ratio"] / data["count"]
                }
        return stats
    
    def reset_stats(self):
        """Reset compression statistics"""
        for algorithm in self.compression_stats:
            self.compression_stats[algorithm] = {"count": 0, "total_time": 0.0, "total_ratio": 0.0}


# NL_TAG: VIF-MODEL-005 | Adaptive compression that learns from usage patterns | class AdaptiveCompressor | []
class AdaptiveCompressor:
    """Adaptive compression that learns from usage patterns"""
    
    def __init__(self):
        self.compressor = AdvancedCompressor()
        self.usage_patterns = {}
        self.performance_history = []
    
    def compress_adaptive(self, 
                         data: Union[str, bytes, Dict[str, Any]], 
                         context: str = "default") -> CompressionResult:
        """Compress data using adaptive algorithm selection"""
        
        # Convert data to bytes
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        elif isinstance(data, dict):
            data_bytes = json.dumps(data, separators=(',', ':')).encode('utf-8')
        else:
            data_bytes = data
        
        data_size = len(data_bytes)
        
        # Get context-specific performance data
        if context in self.usage_patterns:
            pattern = self.usage_patterns[context]
            # Select algorithm based on historical performance for this context
            best_algorithm = self._select_best_algorithm(pattern, data_size)
        else:
            # Use default strategy for new contexts
            best_algorithm = self.compressor.strategy.select_algorithm(data_size)
        
        # Compress with selected algorithm
        result = self.compressor.compress(data_bytes, best_algorithm)
        
        # Update usage patterns
        self._update_usage_pattern(context, data_size, result)
        
        return result
    
    def _select_best_algorithm(self, pattern: Dict[str, Any], data_size: int) -> CompressionAlgorithm:
        """Select best algorithm based on usage pattern"""
        # Simple heuristic: choose algorithm with best efficiency score for similar data sizes
        best_algorithm = CompressionAlgorithm.GZIP
        best_score = 0.0
        
        for algorithm, stats in pattern.items():
            if algorithm in [a.value for a in CompressionAlgorithm]:
                # Calculate efficiency score based on historical performance
                efficiency = stats.get("avg_ratio", 0.5) / max(stats.get("avg_time", 0.001), 0.001)
                if efficiency > best_score:
                    best_score = efficiency
                    best_algorithm = CompressionAlgorithm(algorithm)
        
        return best_algorithm
    
    def _update_usage_pattern(self, context: str, data_size: int, result: CompressionResult):
        """Update usage pattern with new compression result"""
        if context not in self.usage_patterns:
            self.usage_patterns[context] = {}
        
        algorithm_key = result.algorithm.value
        if algorithm_key not in self.usage_patterns[context]:
            self.usage_patterns[context][algorithm_key] = {
                "count": 0,
                "total_time": 0.0,
                "total_ratio": 0.0,
                "size_ranges": {}
            }
        
        # Update algorithm stats
        pattern = self.usage_patterns[context][algorithm_key]
        pattern["count"] += 1
        pattern["total_time"] += result.compression_time
        pattern["total_ratio"] += result.compression_ratio
        
        # Update size range stats
        size_range = self._get_size_range(data_size)
        if size_range not in pattern["size_ranges"]:
            pattern["size_ranges"][size_range] = {"count": 0, "avg_ratio": 0.0}
        
        range_stats = pattern["size_ranges"][size_range]
        range_stats["count"] += 1
        range_stats["avg_ratio"] = (range_stats["avg_ratio"] * (range_stats["count"] - 1) + 
                                   result.compression_ratio) / range_stats["count"]
    
    def _get_size_range(self, size: int) -> str:
        """Get size range category"""
        if size < 100:
            return "tiny"
        elif size < 1024:
            return "small"
        elif size < 1024 * 1024:
            return "medium"
        else:
            return "large"
    
    def get_usage_patterns(self) -> Dict[str, Any]:
        """Get usage patterns for analysis"""
        return self.usage_patterns


# Global compressor instances
_compressor = AdvancedCompressor()
_adaptive_compressor = AdaptiveCompressor()


# NL_TAG: VIF-UTIL-001 | Compress data using advanced compression strategies | compress_data(data, algorithm, priority) | []
def compress_data(data: Union[str, bytes, Dict[str, Any]], 
                 algorithm: Optional[CompressionAlgorithm] = None,
                 priority: str = "balanced") -> CompressionResult:
    """Compress data using advanced compression strategies"""
    return _compressor.compress(data, algorithm, priority)


# NL_TAG: VIF-UTIL-002 | Compress data using adaptive compression | compress_adaptive(data, context) | []
def compress_adaptive(data: Union[str, bytes, Dict[str, Any]], 
                     context: str = "default") -> CompressionResult:
    """Compress data using adaptive compression"""
    return _adaptive_compressor.compress_adaptive(data, context)


# NL_TAG: VIF-UTIL-003 | Get compression statistics | get_compression_stats() | []
def get_compression_stats() -> Dict[str, Any]:
    """Get compression statistics"""
    return _compressor.get_compression_stats()


# NL_TAG: VIF-UTIL-004 | Get usage patterns for analysis | get_usage_patterns() | []
def get_usage_patterns() -> Dict[str, Any]:
    """Get usage patterns for analysis"""
    return _adaptive_compressor.get_usage_patterns()


# NL_TAG: VIF-UTIL-005 | Reset compression statistics | reset_compression_stats() | []
def reset_compression_stats():
    # NL_TAG: VIF-UTIL-006 | Calculate space saved in bytes | space_saved(self) | []
    def space_saved(self) -> int:
        """Calculate space saved in bytes"""
        return self.original_size - self.compressed_size
    
    @property
    # NL_TAG: VIF-UTIL-007 | Calculate compression efficiency (ratio / time) | efficiency_score(self) | []
    def efficiency_score(self) -> float:
        """Calculate compression efficiency (ratio / time)"""
        if self.compression_time == 0:
            return float('inf')
        return self.compression_ratio / self.compression_time


class CompressionStrategy:
    """Intelligent compression strategy selection"""
    
    # NL_TAG: VIF-UTIL-008 |   init   | __init__(self) | []
    def __init__(self):
        self.algorithm_performance = {
            CompressionAlgorithm.GZIP: {"ratio": 0.7, "speed": 0.8, "memory": 0.6},
            CompressionAlgorithm.LZ4: {"ratio": 0.6, "speed": 0.95, "memory": 0.9},
            CompressionAlgorithm.BROTLI: {"ratio": 0.8, "speed": 0.6, "memory": 0.5},
            CompressionAlgorithm.ZLIB: {"ratio": 0.65, "speed": 0.85, "memory": 0.7},
        }
    
    # NL_TAG: VIF-UTIL-009 | Select best compression algorithm based on data characteristics | select_algorithm(self, data_size, data_type, priority) | []
    def select_algorithm(self, 
                        data_size: int, 
                        data_type: str = "text",
                        priority: str = "balanced") -> CompressionAlgorithm:
        """Select best compression algorithm based on data characteristics"""
        
        # For very small data, no compression
        if data_size < 100:
            return CompressionAlgorithm.NONE
        
        # For very large data, prioritize ratio
        if data_size > 1024 * 1024:  # 1MB
            if priority == "ratio":
                return CompressionAlgorithm.BROTLI
            else:
                return CompressionAlgorithm.GZIP
        
        # For medium data, balance speed and ratio
        if data_size > 1024:  # 1KB
            if priority == "speed":
                return CompressionAlgorithm.LZ4
            elif priority == "ratio":
                return CompressionAlgorithm.BROTLI
            else:
                return CompressionAlgorithm.GZIP
        
        # For small data, prioritize speed
        return CompressionAlgorithm.LZ4


class AdvancedCompressor:
    """Advanced compression system with multiple algorithms"""
    
    # NL_TAG: VIF-UTIL-010 |   init   | __init__(self) | []
    def __init__(self):
        self.strategy = CompressionStrategy()
        self.compression_stats = {
            algorithm: {"count": 0, "total_time": 0.0, "total_ratio": 0.0}
            for algorithm in CompressionAlgorithm
        }
    
    # NL_TAG: VIF-UTIL-011 | Compress data using specified or auto-selected algorithm | compress(self, data, algorithm, priority) | []
    def compress(self, 
                data: Union[str, bytes, Dict[str, Any]], 
                algorithm: Optional[CompressionAlgorithm] = None,
                priority: str = "balanced") -> CompressionResult:
        """Compress data using specified or auto-selected algorithm"""
        
        # Convert data to bytes
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        elif isinstance(data, dict):
            data_bytes = json.dumps(data, separators=(',', ':')).encode('utf-8')
        else:
            data_bytes = data
        
        original_size = len(data_bytes)
        
        # Auto-select algorithm if not specified
        if algorithm is None:
            algorithm = self.strategy.select_algorithm(
                original_size, 
                priority=priority
            )
        
        # Skip compression for very small data
        if algorithm == CompressionAlgorithm.NONE:
            return CompressionResult(
                algorithm=algorithm,
                original_size=original_size,
                compressed_size=original_size,
                compression_ratio=1.0,
                compression_time=0.0,
                decompression_time=0.0,
                data=data_bytes
            )
        
        # Compress data
        start_time = time.time()
        compressed_data = self._compress_data(data_bytes, algorithm)
        compression_time = time.time() - start_time
        
        # Test decompression time
        start_time = time.time()
        self._decompress_data(compressed_data, algorithm)
        decompression_time = time.time() - start_time
        
        compressed_size = len(compressed_data)
        compression_ratio = compressed_size / original_size if original_size > 0 else 1.0
        
        # Update statistics
        self.compression_stats[algorithm]["count"] += 1
        self.compression_stats[algorithm]["total_time"] += compression_time
        self.compression_stats[algorithm]["total_ratio"] += compression_ratio
        
        return CompressionResult(
            algorithm=algorithm,
            original_size=original_size,
            compressed_size=compressed_size,
            compression_ratio=compression_ratio,
            compression_time=compression_time,
            decompression_time=decompression_time,
            data=compressed_data
        )
    
    # NL_TAG: VIF-UTIL-012 | Compress data using specified algorithm | _compress_data(self, data, algorithm) | []
    def _compress_data(self, data: bytes, algorithm: CompressionAlgorithm) -> bytes:
        """Compress data using specified algorithm"""
        try:
            if algorithm == CompressionAlgorithm.GZIP:
                return gzip.compress(data)
            elif algorithm == CompressionAlgorithm.LZ4:
                if LZ4_AVAILABLE:
                    return lz4.frame.compress(data)
                else:
                    logger.warning("LZ4 not available, falling back to gzip")
                    return gzip.compress(data)
            elif algorithm == CompressionAlgorithm.BROTLI:
                if BROTLI_AVAILABLE:
                    return brotli.compress(data)
                else:
                    logger.warning("Brotli not available, falling back to gzip")
                    return gzip.compress(data)
            elif algorithm == CompressionAlgorithm.ZLIB:
                return zlib.compress(data)
            else:
                return data
        except Exception as e:
            logger.error(f"Compression failed with {algorithm}: {e}")
            return data
    
    # NL_TAG: VIF-UTIL-013 | Decompress data using specified algorithm | _decompress_data(self, data, algorithm) | []
    def _decompress_data(self, data: bytes, algorithm: CompressionAlgorithm) -> bytes:
        """Decompress data using specified algorithm"""
        try:
            if algorithm == CompressionAlgorithm.GZIP:
                return gzip.decompress(data)
            elif algorithm == CompressionAlgorithm.LZ4:
                if LZ4_AVAILABLE:
                    return lz4.frame.decompress(data)
                else:
                    logger.warning("LZ4 not available, falling back to gzip")
                    return gzip.decompress(data)
            elif algorithm == CompressionAlgorithm.BROTLI:
                if BROTLI_AVAILABLE:
                    return brotli.decompress(data)
                else:
                    logger.warning("Brotli not available, falling back to gzip")
                    return gzip.decompress(data)
            elif algorithm == CompressionAlgorithm.ZLIB:
                return zlib.decompress(data)
            else:
                return data
        except Exception as e:
            logger.error(f"Decompression failed with {algorithm}: {e}")
            return data
    
    # NL_TAG: VIF-UTIL-014 | Get compression statistics | get_compression_stats(self) | []
    def get_compression_stats(self) -> Dict[str, Any]:
        """Get compression statistics"""
        stats = {}
        for algorithm, data in self.compression_stats.items():
            if data["count"] > 0:
                stats[algorithm.value] = {
                    "count": data["count"],
                    "avg_time": data["total_time"] / data["count"],
                    "avg_ratio": data["total_ratio"] / data["count"]
                }
        return stats
    
    # NL_TAG: VIF-UTIL-015 | Reset compression statistics | reset_stats(self) | []
    def reset_stats(self):
        """Reset compression statistics"""
        for algorithm in self.compression_stats:
            self.compression_stats[algorithm] = {"count": 0, "total_time": 0.0, "total_ratio": 0.0}


class AdaptiveCompressor:
    """Adaptive compression that learns from usage patterns"""
    
    # NL_TAG: VIF-UTIL-016 |   init   | __init__(self) | []
    def __init__(self):
        self.compressor = AdvancedCompressor()
        self.usage_patterns = {}
        self.performance_history = []
    
    # NL_TAG: VIF-UTIL-017 | Compress data using adaptive algorithm selection | compress_adaptive(self, data, context) | []
    def compress_adaptive(self, 
                         data: Union[str, bytes, Dict[str, Any]], 
                         context: str = "default") -> CompressionResult:
        """Compress data using adaptive algorithm selection"""
        
        # Convert data to bytes
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        elif isinstance(data, dict):
            data_bytes = json.dumps(data, separators=(',', ':')).encode('utf-8')
        else:
            data_bytes = data
        
        data_size = len(data_bytes)
        
        # Get context-specific performance data
        if context in self.usage_patterns:
            pattern = self.usage_patterns[context]
            # Select algorithm based on historical performance for this context
            best_algorithm = self._select_best_algorithm(pattern, data_size)
        else:
            # Use default strategy for new contexts
            best_algorithm = self.compressor.strategy.select_algorithm(data_size)
        
        # Compress with selected algorithm
        result = self.compressor.compress(data_bytes, best_algorithm)
        
        # Update usage patterns
        self._update_usage_pattern(context, data_size, result)
        
        return result
    
    # NL_TAG: VIF-UTIL-018 | Select best algorithm based on usage pattern | _select_best_algorithm(self, pattern, data_size) | []
    def _select_best_algorithm(self, pattern: Dict[str, Any], data_size: int) -> CompressionAlgorithm:
        """Select best algorithm based on usage pattern"""
        # Simple heuristic: choose algorithm with best efficiency score for similar data sizes
        best_algorithm = CompressionAlgorithm.GZIP
        best_score = 0.0
        
        for algorithm, stats in pattern.items():
            if algorithm in [a.value for a in CompressionAlgorithm]:
                # Calculate efficiency score based on historical performance
                efficiency = stats.get("avg_ratio", 0.5) / max(stats.get("avg_time", 0.001), 0.001)
                if efficiency > best_score:
                    best_score = efficiency
                    best_algorithm = CompressionAlgorithm(algorithm)
        
        return best_algorithm
    
    # NL_TAG: VIF-UTIL-019 | Update usage pattern with new compression result | _update_usage_pattern(self, context, data_size, result) | []
    def _update_usage_pattern(self, context: str, data_size: int, result: CompressionResult):
        """Update usage pattern with new compression result"""
        if context not in self.usage_patterns:
            self.usage_patterns[context] = {}
        
        algorithm_key = result.algorithm.value
        if algorithm_key not in self.usage_patterns[context]:
            self.usage_patterns[context][algorithm_key] = {
                "count": 0,
                "total_time": 0.0,
                "total_ratio": 0.0,
                "size_ranges": {}
            }
        
        # Update algorithm stats
        pattern = self.usage_patterns[context][algorithm_key]
        pattern["count"] += 1
        pattern["total_time"] += result.compression_time
        pattern["total_ratio"] += result.compression_ratio
        
        # Update size range stats
        size_range = self._get_size_range(data_size)
        if size_range not in pattern["size_ranges"]:
            pattern["size_ranges"][size_range] = {"count": 0, "avg_ratio": 0.0}
        
        range_stats = pattern["size_ranges"][size_range]
        range_stats["count"] += 1
        range_stats["avg_ratio"] = (range_stats["avg_ratio"] * (range_stats["count"] - 1) + 
                                   result.compression_ratio) / range_stats["count"]
    
    # NL_TAG: VIF-UTIL-020 | Get size range category | _get_size_range(self, size) | []
    def _get_size_range(self, size: int) -> str:
        """Get size range category"""
        if size < 100:
            return "tiny"
        elif size < 1024:
            return "small"
        elif size < 1024 * 1024:
            return "medium"
        else:
            return "large"
    
    # NL_TAG: VIF-UTIL-021 | Get usage patterns for analysis | get_usage_patterns(self) | []
    def get_usage_patterns(self) -> Dict[str, Any]:
        """Get usage patterns for analysis"""
        return self.usage_patterns


# Global compressor instances
_compressor = AdvancedCompressor()
_adaptive_compressor = AdaptiveCompressor()


def compress_data(data: Union[str, bytes, Dict[str, Any]], 
                 algorithm: Optional[CompressionAlgorithm] = None,
                 priority: str = "balanced") -> CompressionResult:
    """Compress data using advanced compression strategies"""
    return _compressor.compress(data, algorithm, priority)


def compress_adaptive(data: Union[str, bytes, Dict[str, Any]], 
                     context: str = "default") -> CompressionResult:
    """Compress data using adaptive compression"""
    return _adaptive_compressor.compress_adaptive(data, context)


def get_compression_stats() -> Dict[str, Any]:
    """Get compression statistics"""
    return _compressor.get_compression_stats()


def get_usage_patterns() -> Dict[str, Any]:
    """Get usage patterns for analysis"""
    return _adaptive_compressor.get_usage_patterns()


def reset_compression_stats():
    """Reset compression statistics"""
    _compressor.reset_stats()
    _adaptive_compressor.usage_patterns.clear()
