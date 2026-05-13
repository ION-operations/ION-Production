"""
Tests for configuration loader
"""

from __future__ import annotations

import pytest
import tempfile
from pathlib import Path

from sdfcvf.config import (
    ConfigLoader,
    SDFCVFConfig,
    CoverageConfig,
    get_config,
    reload_config
)


class TestConfigLoader:
    """Test configuration loading"""
    
    def test_load_default_config(self):
        """Test loading with default values"""
        config = SDFCVFConfig()
        
        # Check defaults
        assert config.coverage.public_threshold == 0.95
        assert config.coverage.internal_threshold == 0.75
        assert config.composite_metric.threshold == 0.85
        assert config.quintet_parity.threshold == 0.90
        assert config.anti_gaming.max_repetitions == 5
        assert config.performance.pre_commit_max_ms == 500
    
    def test_load_from_yaml(self, tmp_path):
        """Test loading configuration from YAML file"""
        config_file = tmp_path / ".sdfcvf.config.yaml"
        config_file.write_text('''
version: "1.0"

coverage:
  public_api:
    threshold: 0.98
    enforce: true
  internal:
    threshold: 0.80

composite_metric:
  threshold: 0.90

quintet_parity:
  threshold: 0.92

anti_gaming:
  boilerplate:
    max_repetitions: 3

performance:
  pre_commit:
    max_duration_ms: 300
''')
        
        config = ConfigLoader.load(str(config_file))
        
        # Check loaded values
        assert config.coverage.public_threshold == 0.98
        assert config.coverage.internal_threshold == 0.80
        assert config.composite_metric.threshold == 0.90
        assert config.quintet_parity.threshold == 0.92
        assert config.anti_gaming.max_repetitions == 3
        assert config.performance.pre_commit_max_ms == 300
    
    def test_load_with_per_directory_policies(self, tmp_path):
        """Test loading per-directory policies"""
        config_file = tmp_path / ".sdfcvf.config.yaml"
        config_file.write_text('''
coverage:
  public_api:
    threshold: 0.95
  
  per_directory:
    - path: "packages/vif/"
      public_threshold: 0.99
      internal_threshold: 0.85
      reason: "VIF is gold standard"
    
    - path: "packages/test/"
      public_threshold: 0.50
      internal_threshold: 0.30
''')
        
        config = ConfigLoader.load(str(config_file))
        
        # Check per-directory policies loaded
        assert "packages/vif/" in config.per_directory_policies
        assert config.per_directory_policies["packages/vif/"].public_threshold == 0.99
        assert config.per_directory_policies["packages/vif/"].internal_threshold == 0.85
        
        assert "packages/test/" in config.per_directory_policies
        assert config.per_directory_policies["packages/test/"].public_threshold == 0.50
    
    def test_get_coverage_for_path(self, tmp_path):
        """Test getting coverage config for specific path"""
        config_file = tmp_path / ".sdfcvf.config.yaml"
        config_file.write_text('''
coverage:
  public_api:
    threshold: 0.95
  
  per_directory:
    - path: "packages/vif/"
      public_threshold: 0.99
      internal_threshold: 0.85
''')
        
        config = ConfigLoader.load(str(config_file))
        
        # Get coverage for VIF file
        vif_coverage = ConfigLoader.get_coverage_for_path(config, "packages/vif/witness.py")
        assert vif_coverage.public_threshold == 0.99
        
        # Get coverage for non-VIF file (should use default)
        other_coverage = ConfigLoader.get_coverage_for_path(config, "packages/other/file.py")
        assert other_coverage.public_threshold == 0.95
    
    def test_load_missing_file(self):
        """Test loading when config file doesn't exist"""
        config = ConfigLoader.load("/nonexistent/path/.sdfcvf.config.yaml")
        
        # Should return defaults
        assert isinstance(config, SDFCVFConfig)
        assert config.coverage.public_threshold == 0.95
    
    def test_load_invalid_yaml(self, tmp_path):
        """Test loading with invalid YAML"""
        config_file = tmp_path / ".sdfcvf.config.yaml"
        config_file.write_text("invalid: yaml: syntax::")
        
        config = ConfigLoader.load(str(config_file))
        
        # Should return defaults on error
        assert isinstance(config, SDFCVFConfig)
    
    def test_get_config_singleton(self):
        """Test global config singleton"""
        config1 = get_config()
        config2 = get_config()
        
        # Should be same instance
        assert config1 is config2
    
    def test_reload_config(self, tmp_path):
        """Test reloading configuration"""
        config_file = tmp_path / ".sdfcvf.config.yaml"
        config_file.write_text('''
quintet_parity:
  threshold: 0.95
''')
        
        config = reload_config(str(config_file))
        
        assert config.quintet_parity.threshold == 0.95


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])

