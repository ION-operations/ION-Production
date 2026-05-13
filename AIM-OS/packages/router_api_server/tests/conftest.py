"""
Router API Server - Test Configuration

# NL_TAG: ROUTER-API-TEST-CONFIG-001 | Test configuration for Router API server | pytest.ini, conftest.py | []
# NL_TAG_INTENT: ROUTER-API-DESIGN-010 | Test configuration ensures consistent test execution | Test configuration | [ADR-TESTING]
"""

import pytest
import sys
from pathlib import Path

# Add packages directory to path
packages_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(packages_dir))

# Pytest configuration
pytest_plugins = []

