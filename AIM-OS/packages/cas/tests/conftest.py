"""Pytest configuration for CAS tests.

This conftest.py file ensures that the CAS package can be imported correctly
by adding the packages directory to sys.path, allowing tests to use 'from cas import ...'
"""
import sys
import os
from pathlib import Path

# Add packages directory to Python path for imports
# __file__ is packages/cas/tests/conftest.py
# parent.parent.parent = packages directory (workspace root)
# parent.parent = packages directory
packages_dir = Path(__file__).parent.parent.parent.absolute()
if str(packages_dir) not in sys.path:
    sys.path.insert(0, str(packages_dir))

