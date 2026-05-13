"""
Tests for Universal Tag Registry
"""

from __future__ import annotations

import pytest
import tempfile
from pathlib import Path

from nl_tags.universal_registry import UniversalTagRegistry, TagReference, TagStatistics


class TestUniversalTagRegistry:
    """Test universal tag registry"""
    
    def test_register_tag(self):
        """Test registering a tag"""
        registry = UniversalTagRegistry()
        
        tag_data = {
            "id": "VIF-WITNESS-001",
            "kind": "TAG",
            "description": "Create VIF witness",
            "syntax_ref": "create_witness(...)",
            "dependencies": ["VIF-PROV-001"],
            "file_path": "packages/vif/witness.py",
            "line_number": 10
        }
        
        registry.register("VIF-WITNESS-001", tag_data)
        
        # Verify registered
        assert registry.count() == 1
        assert "VIF-WITNESS-001" in registry.tags
        assert "VIF" in registry.by_system
        assert "WITNESS" in registry.by_category
        assert "TAG" in registry.by_type
    
    def test_query_by_system(self):
        """Test querying tags by system"""
        registry = UniversalTagRegistry()
        
        registry.register("VIF-001", {"kind": "TAG"})
        registry.register("VIF-002", {"kind": "TAG"})
        registry.register("CMC-001", {"kind": "TAG"})
        
        vif_tags = registry.query(system="VIF")
        assert len(vif_tags) == 2
        assert "VIF-001" in vif_tags
        assert "VIF-002" in vif_tags
    
    def test_query_by_category(self):
        """Test querying tags by category"""
        registry = UniversalTagRegistry()
        
        registry.register("VIF-WITNESS-001", {"kind": "TAG"})
        registry.register("VIF-WITNESS-002", {"kind": "TAG"})
        registry.register("VIF-CONF-001", {"kind": "TAG"})
        
        witness_tags = registry.query(category="WITNESS")
        assert len(witness_tags) == 2
    
    def test_query_by_type(self):
        """Test querying tags by type"""
        registry = UniversalTagRegistry()
        
        registry.register("VIF-001", {"kind": "TAG"})
        registry.register("VIF-002", {"kind": "CONNECT"})
        registry.register("VIF-003", {"kind": "INTENT"})
        
        connect_tags = registry.query(tag_type="CONNECT")
        assert len(connect_tags) == 1
        assert "VIF-002" in connect_tags
    
    def test_query_multiple_filters(self):
        """Test querying with multiple filters (AND logic)"""
        registry = UniversalTagRegistry()
        
        registry.register("VIF-WITNESS-001", {"kind": "TAG"})
        registry.register("VIF-WITNESS-002", {"kind": "CONNECT"})
        registry.register("CMC-WITNESS-001", {"kind": "TAG"})
        
        result = registry.query(system="VIF", category="WITNESS", tag_type="TAG")
        assert len(result) == 1
        assert "VIF-WITNESS-001" in result
    
    def test_find_dependencies(self):
        """Test finding tag dependencies"""
        registry = UniversalTagRegistry()
        
        registry.register("VIF-001", {"dependencies": ["VIF-002", "VIF-003"]})
        registry.register("VIF-002", {"dependencies": []})
        registry.register("VIF-003", {"dependencies": []})
        
        deps = registry.find_dependencies("VIF-001")
        assert len(deps) == 2
        assert "VIF-002" in deps
        assert "VIF-003" in deps
    
    def test_find_dependents(self):
        """Test finding tags that depend on this tag"""
        registry = UniversalTagRegistry()
        
        registry.register("VIF-001", {"dependencies": ["VIF-CORE-001"]})
        registry.register("VIF-002", {"dependencies": ["VIF-CORE-001"]})
        registry.register("VIF-CORE-001", {"dependencies": []})
        
        dependents = registry.find_dependents("VIF-CORE-001")
        assert len(dependents) == 2
        assert "VIF-001" in dependents
        assert "VIF-002" in dependents
    
    def test_scan_file(self, tmp_path):
        """Test scanning a file for tags"""
        test_file = tmp_path / "test.py"
        test_file.write_text('''
# NL_TAG: TEST-001 | Test function | test_func() -> None | []
def test_func():
    pass

# NL_TAG_CONNECT: TEST-002 | Integration | test_func calls other_func | [TEST-001]
# NL_TAG_INTENT: TEST-003 | Design decision | architectural_pattern | [ADR-001]
''', encoding='utf-8')
        
        registry = UniversalTagRegistry()
        count = registry.scan_file(str(test_file))
        
        assert count == 3
        assert "TEST-001" in registry.tags
        assert "TEST-002" in registry.tags
        assert "TEST-003" in registry.tags
    
    def test_scan_codebase(self, tmp_path):
        """Test scanning entire codebase"""
        # Create test files
        file1 = tmp_path / "file1_TAGGED.py"
        file1.write_text('''
# NL_TAG: TAG-001 | Function 1 | func1() | []
def func1(): pass
''', encoding='utf-8')
        
        file2 = tmp_path / "file2_TAGGED.py"
        file2.write_text('''
# NL_TAG: TAG-002 | Function 2 | func2() | []
def func2(): pass
''', encoding='utf-8')
        
        registry = UniversalTagRegistry()
        count = registry.scan_codebase(str(tmp_path), pattern="*_TAGGED.py")
        
        assert count == 2
        assert "TAG-001" in registry.tags
        assert "TAG-002" in registry.tags
    
    def test_export_import(self, tmp_path):
        """Test exporting and importing registry"""
        registry1 = UniversalTagRegistry()
        
        registry1.register("VIF-001", {"kind": "TAG", "description": "Test"})
        registry1.register("VIF-002", {"kind": "CONNECT", "dependencies": ["VIF-001"]})
        
        # Export
        export_path = tmp_path / "registry.json"
        registry1.export(str(export_path))
        
        # Import into new registry
        registry2 = UniversalTagRegistry()
        registry2.import_from(str(export_path))
        
        # Verify
        assert registry2.count() == 2
        assert "VIF-001" in registry2.tags
        assert "VIF-002" in registry2.tags
        assert "VIF-001" in registry2.find_dependencies("VIF-002")
    
    def test_get_statistics(self):
        """Test getting registry statistics"""
        registry = UniversalTagRegistry()
        
        registry.register("VIF-WITNESS-001", {"kind": "TAG"})
        registry.register("VIF-CONF-001", {"kind": "TAG"})
        registry.register("CMC-STORE-001", {"kind": "TAG"})
        registry.register("VIF-CONNECT-001", {"kind": "CONNECT", "dependencies": ["MISSING-001"]})
        
        stats = registry.get_statistics()
        
        assert stats.total_tags == 4
        assert stats.by_system["VIF"] == 3
        assert stats.by_system["CMC"] == 1
        assert stats.by_category["WITNESS"] == 1
        assert stats.by_type["TAG"] == 3
        assert stats.by_type["CONNECT"] == 1
        assert len(stats.broken_dependencies) == 1
    
    def test_validate(self):
        """Test registry validation"""
        registry = UniversalTagRegistry()
        
        registry.register("VIF-001", {"dependencies": ["VIF-002"]})
        registry.register("VIF-002", {"dependencies": []})
        registry.register("VIF-003", {"dependencies": ["VIF-MISSING"]})
        
        errors = registry.validate()
        
        # Should find missing dependency
        assert len(errors) >= 1
        assert any("VIF-MISSING" in err for err in errors)


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])

