"""
Configuration Loader for SDF-CVF Quintet Parity

Loads and validates .sdfcvf.config.yaml configuration file.
Provides configuration to quintet parity system.
"""

from __future__ import annotations

import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# NL_TAG: SDFCVF-MODEL-010 | Coverage threshold configuration | CoverageConfig(public_threshold: float = 0.95, internal_threshold: float = 0.75, enforce: bool = True, severity: str = "error") | []
@dataclass
class CoverageConfig:
    """Coverage threshold configuration"""
    public_threshold: float = 0.95
    internal_threshold: float = 0.75
    enforce: bool = True
    severity: str = "error"

# NL_TAG: SDFCVF-MODEL-011 | Composite metric configuration | CompositeMetricConfig(threshold: float = 0.85, enforce: bool = True, weights: Dict[str, float] = {...}, thresholds: Dict[str, float] = {...}) | []
@dataclass
class CompositeMetricConfig:
    """Composite metric configuration"""
    threshold: float = 0.85
    enforce: bool = True
    weights: Dict[str, float] = field(default_factory=lambda: {
        "signature": 0.4,
        "name": 0.3,
        "doc": 0.2,
        "spec": 0.1
    })
    thresholds: Dict[str, float] = field(default_factory=lambda: {
        "signature": 0.90,
        "name": 0.85,
        "doc": 0.80,
        "spec": 0.90
    })

# NL_TAG: SDFCVF-MODEL-012 | Quintet parity threshold configuration | QuintetParityConfig(threshold: float = 0.90, enforce: bool = True, pairwise_thresholds: Dict[str, float] = {...}, weights: Dict[str, float] = {...}) | []
@dataclass
class QuintetParityConfig:
    """Quintet parity threshold configuration"""
    threshold: float = 0.90
    enforce: bool = True
    pairwise_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "code_docs": 0.85,
        "code_tests": 0.85,
        "code_traces": 0.80,
        "code_tags": 0.85,
        "docs_tests": 0.90,
        "docs_traces": 0.85,
        "docs_tags": 0.90,
        "tests_traces": 0.80,
        "tests_tags": 0.85,
        "traces_tags": 0.80
    })
    weights: Dict[str, float] = field(default_factory=lambda: {
        "code_tags": 1.5,
        "docs_tags": 1.2,
        "default": 1.0
    })

# NL_TAG: SDFCVF-MODEL-013 | Anti-gaming checks configuration | AntiGamingConfig(boilerplate_enabled: bool = True, max_repetitions: int = 5, duplicate_ids_enabled: bool = True, min_length_enabled: bool = True, min_length_characters: int = 10, generic_words_enabled: bool = True, generic_words: List[str] = [...], generic_threshold: float = 0.30) | []
@dataclass
class AntiGamingConfig:
    """Anti-gaming checks configuration"""
    boilerplate_enabled: bool = True
    max_repetitions: int = 5
    duplicate_ids_enabled: bool = True
    min_length_enabled: bool = True
    min_length_characters: int = 10
    generic_words_enabled: bool = True
    generic_words: List[str] = field(default_factory=lambda: [
        "function", "method", "class", "helper", "utility", "generic"
    ])
    generic_threshold: float = 0.30

# NL_TAG: SDFCVF-MODEL-014 | Performance budget configuration | PerformanceConfig(pre_commit_max_ms: int = 500, pre_commit_p50_ms: int = 200, full_analysis_max_seconds: int = 5, incremental_enabled: bool = True) | []
@dataclass
class PerformanceConfig:
    """Performance budget configuration"""
    pre_commit_max_ms: int = 500
    pre_commit_p50_ms: int = 200
    full_analysis_max_seconds: int = 5
    incremental_enabled: bool = True

# NL_TAG: SDFCVF-MODEL-015 | Complete SDF-CVF configuration | SDFCVFConfig(version: str = "1.0", coverage: CoverageConfig = ..., composite_metric: CompositeMetricConfig = ..., quintet_parity: QuintetParityConfig = ..., anti_gaming: AntiGamingConfig = ..., performance: PerformanceConfig = ..., per_directory_policies: Dict[str, CoverageConfig] = {...}) | []
@dataclass
class SDFCVFConfig:
    """Complete SDF-CVF configuration"""
    version: str = "1.0"
    coverage: CoverageConfig = field(default_factory=CoverageConfig)
    composite_metric: CompositeMetricConfig = field(default_factory=CompositeMetricConfig)
    quintet_parity: QuintetParityConfig = field(default_factory=QuintetParityConfig)
    anti_gaming: AntiGamingConfig = field(default_factory=AntiGamingConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    
    # Per-directory policies
    per_directory_policies: Dict[str, CoverageConfig] = field(default_factory=dict)

# NL_TAG: SDFCVF-CONFIG-001 | Configuration loader for SDF-CVF | ConfigLoader | []
class ConfigLoader:
    """Load SDF-CVF configuration from YAML file"""
    
    DEFAULT_CONFIG_PATH = ".sdfcvf.config.yaml"
    
    # NL_TAG: SDFCVF-CONFIG-002 | Load configuration from YAML file | load(config_path: Optional[str] = None) -> SDFCVFConfig | [SDFCVF-CONFIG-001, SDFCVF-MODEL-015]
    @classmethod
    def load(cls, config_path: Optional[str] = None) -> SDFCVFConfig:
        """
        Load configuration from YAML file
        
        Args:
            config_path: Path to config file (default: .sdfcvf.config.yaml in repo root)
            
        Returns:
            SDFCVFConfig with loaded settings
        """
        if config_path is None:
            config_path = cls._find_config_file()
        
        if not config_path or not Path(config_path).exists():
            # Return default configuration
            return SDFCVFConfig()
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            return cls._parse_config(data)
        
        except Exception as e:
            print(f"Warning: Failed to load config from {config_path}: {e}")
            print("Using default configuration")
            return SDFCVFConfig()
    
    @classmethod
    def _find_config_file(cls) -> Optional[str]:
        """Find config file in current directory or parent directories"""
        current = Path.cwd()
        
        # Try current directory and up to 5 parent directories
        for _ in range(5):
            config_path = current / cls.DEFAULT_CONFIG_PATH
            if config_path.exists():
                return str(config_path)
            
            parent = current.parent
            if parent == current:
                break
            current = parent
        
        return None
    
    @classmethod
    def _parse_config(cls, data: Dict) -> SDFCVFConfig:
        """Parse configuration data from YAML"""
        config = SDFCVFConfig()
        
        # Parse version
        if "version" in data:
            config.version = data["version"]
        
        # Parse coverage
        if "coverage" in data:
            coverage_data = data["coverage"]
            config.coverage = CoverageConfig(
                public_threshold=coverage_data.get("public_api", {}).get("threshold", 0.95),
                internal_threshold=coverage_data.get("internal", {}).get("threshold", 0.75),
                enforce=coverage_data.get("public_api", {}).get("enforce", True),
                severity=coverage_data.get("public_api", {}).get("severity", "error")
            )
            
            # Parse per-directory policies
            per_dir = coverage_data.get("per_directory", [])
            for policy in per_dir:
                path = policy.get("path", "")
                if path:
                    config.per_directory_policies[path] = CoverageConfig(
                        public_threshold=policy.get("public_threshold", 0.95),
                        internal_threshold=policy.get("internal_threshold", 0.75),
                        enforce=True
                    )
        
        # Parse composite metric
        if "composite_metric" in data:
            cm_data = data["composite_metric"]
            config.composite_metric = CompositeMetricConfig(
                threshold=cm_data.get("threshold", 0.85),
                enforce=cm_data.get("enforce", True),
                weights=cm_data.get("weights", config.composite_metric.weights),
                thresholds=cm_data.get("thresholds", config.composite_metric.thresholds)
            )
        
        # Parse quintet parity
        if "quintet_parity" in data:
            qp_data = data["quintet_parity"]
            config.quintet_parity = QuintetParityConfig(
                threshold=qp_data.get("threshold", 0.90),
                enforce=qp_data.get("enforce", True),
                pairwise_thresholds=qp_data.get("pairwise_thresholds", config.quintet_parity.pairwise_thresholds),
                weights=qp_data.get("weights", config.quintet_parity.weights)
            )
        
        # Parse anti-gaming
        if "anti_gaming" in data:
            ag_data = data["anti_gaming"]
            config.anti_gaming = AntiGamingConfig(
                boilerplate_enabled=ag_data.get("boilerplate", {}).get("enabled", True),
                max_repetitions=ag_data.get("boilerplate", {}).get("max_repetitions", 5),
                duplicate_ids_enabled=ag_data.get("duplicate_ids", {}).get("enabled", True),
                min_length_enabled=ag_data.get("min_length", {}).get("enabled", True),
                min_length_characters=ag_data.get("min_length", {}).get("characters", 10),
                generic_words_enabled=ag_data.get("generic_words", {}).get("enabled", True),
                generic_words=ag_data.get("generic_words", {}).get("words", config.anti_gaming.generic_words),
                generic_threshold=ag_data.get("generic_words", {}).get("threshold", 0.30)
            )
        
        # Parse performance
        if "performance" in data:
            perf_data = data["performance"]
            config.performance = PerformanceConfig(
                pre_commit_max_ms=perf_data.get("pre_commit", {}).get("max_duration_ms", 500),
                pre_commit_p50_ms=perf_data.get("pre_commit", {}).get("max_duration_p50_ms", 200),
                full_analysis_max_seconds=perf_data.get("full_analysis", {}).get("max_duration_seconds", 5),
                incremental_enabled=perf_data.get("incremental", {}).get("enabled", True)
            )
        
        return config
    
    @classmethod
    def get_coverage_for_path(cls, config: SDFCVFConfig, file_path: str) -> CoverageConfig:
        """
        Get coverage configuration for specific file path
        
        Checks per-directory policies and returns appropriate thresholds.
        """
        file_path_obj = Path(file_path)
        
        # Check each per-directory policy
        for policy_path, policy_config in config.per_directory_policies.items():
            policy_path_obj = Path(policy_path)
            
            # Check if file is under this policy path
            try:
                file_path_obj.relative_to(policy_path_obj)
                return policy_config
            except ValueError:
                continue
        
        # No specific policy, return default
        return config.coverage


# Global configuration instance
_config: Optional[SDFCVFConfig] = None

# NL_TAG: SDFCVF-CONFIG-003 | Get singleton SDF-CVF configuration | get_config() -> SDFCVFConfig | [SDFCVF-CONFIG-002]
def get_config() -> SDFCVFConfig:
    """Get global configuration instance (lazy loaded)"""
    global _config
    if _config is None:
        _config = ConfigLoader.load()
    return _config

# NL_TAG: SDFCVF-CONFIG-004 | Reload SDF-CVF configuration from file | reload_config(config_path: Optional[str] = None) -> SDFCVFConfig | [SDFCVF-CONFIG-002]
def reload_config(config_path: Optional[str] = None) -> SDFCVFConfig:
    """Reload configuration from file"""
    global _config
    _config = ConfigLoader.load(config_path)
    return _config

