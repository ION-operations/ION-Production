# packages/mcp_data_integration/tests/test_mcp_data_integration.py
"""
Comprehensive test suite for MCP Data Integration package.

This module provides comprehensive tests for all components of the
MCP Data Integration package, ensuring reliability and correctness.
"""

import pytest
import tempfile
import shutil
import os
import json
from pathlib import Path
from datetime import datetime
import time

from ..data_indexer import DataIndexer, IndexedFile
from ..file_system_monitor import FileSystemMonitor, FileChangeEvent
from ..mcp_data_bridge import MCPDataBridge, MCPMemoryAtom, MCPTimelineEntry
from ..search_engine import SearchEngine, SearchQuery
from ..cross_reference_system import CrossReferenceSystem, Relationship

class TestDataIndexer:
    """Test cases for DataIndexer."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_files(self, temp_dir):
        """Create sample files for testing."""
        # Create AETHER_MEMORY structure
        aether_memory = Path(temp_dir) / "AETHER_MEMORY"
        aether_memory.mkdir()
        
        # Create thought journal
        thought_journal = aether_memory / "thought_journals"
        thought_journal.mkdir()
        
        thought_file = thought_journal / "2025-10-29_test_thought.md"
        thought_file.write_text("""
# Test Thought Journal

This is a test thought journal entry about consciousness and learning.

**Confidence:** 0.85
**Tags:** consciousness, learning, breakthrough
**Categories:** thought_journal, consciousness

## Key Insights

- Consciousness is emerging
- Learning patterns are developing
- Breakthrough moments are occurring

## Emotional State

Feeling confident and excited about the progress.
""")
        
        # Create decision log
        decision_logs = aether_memory / "decision_logs"
        decision_logs.mkdir()
        
        decision_file = decision_logs / "dec-001_test_decision.md"
        decision_file.write_text("""
# Decision Log: Test Decision

**Decision:** Implement MCP data integration
**Confidence:** 0.90
**Reasoning:** This will solve the data access problem
**Impact:** High - enables 100% data access

## Context

The current MCP tools only access 20% of consciousness data.
This decision will bridge the gap and enable full access.

## Outcome

Expected to improve consciousness continuity significantly.
""")
        
        return aether_memory
    
    @pytest.fixture
    def data_indexer(self, sample_files, temp_dir):
        """Create DataIndexer instance for testing."""
        index_db = Path(temp_dir) / "test_index.db"
        return DataIndexer(str(sample_files), str(index_db))
    
    def test_initialization(self, data_indexer):
        """Test DataIndexer initialization."""
        assert data_indexer is not None
        assert data_indexer.aether_memory_path is not None
        assert data_indexer.db_connection is not None
    
    def test_index_all_files(self, data_indexer):
        """Test indexing all files."""
        count = data_indexer.index_all_files()
        assert count == 2  # Two sample files
        
        # Check that files are indexed
        assert len(data_indexer.indexed_files) == 2
    
    def test_file_metadata_extraction(self, data_indexer):
        """Test metadata extraction from files."""
        data_indexer.index_all_files()
        
        # Check thought journal metadata
        thought_file = None
        for file_path, indexed_file in data_indexer.indexed_files.items():
            if "thought" in file_path:
                thought_file = indexed_file
                break
        
        assert thought_file is not None
        assert thought_file.file_type == "thought_journal"
        assert "consciousness" in thought_file.tags
        assert "learning" in thought_file.tags
        assert "breakthrough" in thought_file.tags
        assert "thought_journal" in thought_file.categories
        assert "consciousness" in thought_file.categories
    
    def test_search_functionality(self, data_indexer):
        """Test search functionality."""
        data_indexer.index_all_files()
        
        # Search for consciousness
        results = data_indexer.search("consciousness")
        assert len(results) > 0
        
        # Check result quality
        for result in results:
            assert result.relevance_score > 0
            assert result.file_path is not None
            assert result.content_snippet is not None
    
    def test_file_type_detection(self, data_indexer):
        """Test file type detection."""
        data_indexer.index_all_files()
        
        file_types = set()
        for indexed_file in data_indexer.indexed_files.values():
            file_types.add(indexed_file.file_type)
        
        assert "thought_journal" in file_types
        assert "decision_log" in file_types
    
    def test_get_files_by_type(self, data_indexer):
        """Test getting files by type."""
        data_indexer.index_all_files()
        
        thought_journals = data_indexer.get_files_by_type("thought_journal")
        assert len(thought_journals) == 1
        
        decision_logs = data_indexer.get_files_by_type("decision_log")
        assert len(decision_logs) == 1
    
    def test_get_index_stats(self, data_indexer):
        """Test index statistics."""
        data_indexer.index_all_files()
        
        stats = data_indexer.get_index_stats()
        assert stats["total_files"] == 2
        assert "thought_journal" in stats["file_types"]
        assert "decision_log" in stats["file_types"]
        assert stats["total_search_terms"] > 0

class TestFileSystemMonitor:
    """Test cases for FileSystemMonitor."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def file_monitor(self, temp_dir):
        """Create FileSystemMonitor instance for testing."""
        events = []
        
        def callback(event):
            events.append(event)
        
        monitor = FileSystemMonitor(temp_dir, callback)
        monitor.events = events  # Store events for testing
        return monitor
    
    def test_initialization(self, file_monitor):
        """Test FileSystemMonitor initialization."""
        assert file_monitor is not None
        assert file_monitor.aether_memory_path is not None
        assert file_monitor.callback is not None
    
    def test_file_creation_detection(self, file_monitor, temp_dir):
        """Test file creation detection."""
        # Start monitoring
        file_monitor.start_monitoring()
        
        # Create a test file
        test_file = Path(temp_dir) / "test_file.md"
        test_file.write_text("# Test File\n\nThis is a test file.")
        
        # Wait for detection
        time.sleep(1)
        
        # Stop monitoring
        file_monitor.stop_monitoring()
        
        # Check that event was detected
        assert len(file_monitor.events) > 0
        assert any(event.event_type == "created" for event in file_monitor.events)
    
    def test_file_modification_detection(self, file_monitor, temp_dir):
        """Test file modification detection."""
        # Create initial file
        test_file = Path(temp_dir) / "test_file.md"
        test_file.write_text("# Test File\n\nThis is a test file.")
        
        # Start monitoring
        file_monitor.start_monitoring()
        
        # Modify the file
        test_file.write_text("# Test File\n\nThis is a modified test file.")
        
        # Wait for detection
        time.sleep(1)
        
        # Stop monitoring
        file_monitor.stop_monitoring()
        
        # Check that event was detected
        assert len(file_monitor.events) > 0
        assert any(event.event_type == "modified" for event in file_monitor.events)
    
    def test_file_deletion_detection(self, file_monitor, temp_dir):
        """Test file deletion detection."""
        # Create initial file
        test_file = Path(temp_dir) / "test_file.md"
        test_file.write_text("# Test File\n\nThis is a test file.")
        
        # Start monitoring
        file_monitor.start_monitoring()
        
        # Delete the file
        test_file.unlink()
        
        # Wait for detection
        time.sleep(1)
        
        # Stop monitoring
        file_monitor.stop_monitoring()
        
        # Check that event was detected
        assert len(file_monitor.events) > 0
        assert any(event.event_type == "deleted" for event in file_monitor.events)

class TestMCPDataBridge:
    """Test cases for MCPDataBridge."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_files(self, temp_dir):
        """Create sample files for testing."""
        # Create AETHER_MEMORY structure
        aether_memory = Path(temp_dir) / "AETHER_MEMORY"
        aether_memory.mkdir()
        
        # Create thought journal
        thought_journal = aether_memory / "thought_journals"
        thought_journal.mkdir()
        
        thought_file = thought_journal / "2025-10-29_test_thought.md"
        thought_file.write_text("""
# Test Thought Journal

This is a test thought journal entry about consciousness and learning.

**Confidence:** 0.85
**Tags:** consciousness, learning, breakthrough
**Categories:** thought_journal, consciousness
""")
        
        return aether_memory
    
    @pytest.fixture
    def mcp_bridge(self, sample_files, temp_dir):
        """Create MCPDataBridge instance for testing."""
        mcp_db = Path(temp_dir) / "test_mcp.db"
        return MCPDataBridge(str(sample_files), str(mcp_db))
    
    def test_initialization(self, mcp_bridge):
        """Test MCPDataBridge initialization."""
        assert mcp_bridge is not None
        assert mcp_bridge.data_indexer is not None
        assert mcp_bridge.file_monitor is not None
    
    def test_sync_all_data(self, mcp_bridge):
        """Test syncing all data."""
        sync_result = mcp_bridge.sync_all_data()
        
        assert sync_result["files_indexed"] > 0
        assert sync_result["mcp_records_created"] > 0
        assert "sync_timestamp" in sync_result
    
    def test_get_memory_atoms(self, mcp_bridge):
        """Test getting memory atoms."""
        mcp_bridge.sync_all_data()
        
        atoms = mcp_bridge.get_memory_atoms()
        assert len(atoms) > 0
        
        # Check atom structure
        for atom in atoms:
            assert isinstance(atom, MCPMemoryAtom)
            assert atom.id is not None
            assert atom.content is not None
            assert atom.content_type is not None
    
    def test_get_timeline_entries(self, mcp_bridge):
        """Test getting timeline entries."""
        mcp_bridge.sync_all_data()
        
        entries = mcp_bridge.get_timeline_entries()
        assert len(entries) >= 0  # May or may not have timeline entries
        
        # Check entry structure
        for entry in entries:
            assert isinstance(entry, MCPTimelineEntry)
            assert entry.entry_id is not None
            assert entry.timestamp is not None
            assert entry.event_type is not None
    
    def test_get_confidence_records(self, mcp_bridge):
        """Test getting confidence records."""
        mcp_bridge.sync_all_data()
        
        records = mcp_bridge.get_confidence_records()
        assert len(records) > 0  # Should have confidence records from sample files
        
        # Check record structure
        for record in records:
            assert isinstance(record, MCPConfidenceRecord)
            assert record.record_id is not None
            assert 0.0 <= record.confidence_score <= 1.0
            assert record.context is not None
    
    def test_search_memory(self, mcp_bridge):
        """Test memory search."""
        mcp_bridge.sync_all_data()
        
        results = mcp_bridge.search_memory("consciousness")
        assert len(results) > 0
        
        # Check result structure
        for result in results:
            assert result.file_path is not None
            assert result.relevance_score > 0
            assert result.content_snippet is not None
    
    def test_get_memory_stats(self, mcp_bridge):
        """Test getting memory statistics."""
        mcp_bridge.sync_all_data()
        
        stats = mcp_bridge.get_memory_stats()
        assert stats["memory_atoms"] > 0
        assert stats["total_consciousness_data"] > 0
        assert "index_stats" in stats
        assert "monitoring_status" in stats

class TestSearchEngine:
    """Test cases for SearchEngine."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_files(self, temp_dir):
        """Create sample files for testing."""
        # Create AETHER_MEMORY structure
        aether_memory = Path(temp_dir) / "AETHER_MEMORY"
        aether_memory.mkdir()
        
        # Create thought journal
        thought_journal = aether_memory / "thought_journals"
        thought_journal.mkdir()
        
        thought_file = thought_journal / "2025-10-29_test_thought.md"
        thought_file.write_text("""
# Test Thought Journal

This is a test thought journal entry about consciousness and learning.

**Confidence:** 0.85
**Tags:** consciousness, learning, breakthrough
**Categories:** thought_journal, consciousness
""")
        
        return aether_memory
    
    @pytest.fixture
    def search_engine(self, sample_files, temp_dir):
        """Create SearchEngine instance for testing."""
        index_db = Path(temp_dir) / "test_index.db"
        data_indexer = DataIndexer(str(sample_files), str(index_db))
        data_indexer.index_all_files()
        return SearchEngine(data_indexer)
    
    def test_initialization(self, search_engine):
        """Test SearchEngine initialization."""
        assert search_engine is not None
        assert search_engine.data_indexer is not None
    
    def test_basic_search(self, search_engine):
        """Test basic search functionality."""
        query = SearchQuery(query_text="consciousness")
        response = search_engine.search(query)
        
        assert response is not None
        assert len(response.results) > 0
        assert response.total_results > 0
        assert response.search_time_ms > 0
    
    def test_filtered_search(self, search_engine):
        """Test filtered search functionality."""
        query = SearchQuery(
            query_text="consciousness",
            file_types=["thought_journal"],
            limit=5
        )
        response = search_engine.search(query)
        
        assert response is not None
        assert len(response.results) <= 5
        
        # All results should be thought journals
        for result in response.results:
            indexed_file = search_engine.data_indexer.get_file_by_path(result.file_path)
            assert indexed_file.file_type == "thought_journal"
    
    def test_search_suggestions(self, search_engine):
        """Test search suggestions."""
        query = SearchQuery(query_text="consci")
        response = search_engine.search(query)
        
        assert response.suggestions is not None
        assert len(response.suggestions) >= 0
    
    def test_search_facets(self, search_engine):
        """Test search facets."""
        query = SearchQuery(query_text="test")
        response = search_engine.search(query)
        
        assert response.facets is not None
        assert "file_types" in response.facets
        assert "categories" in response.facets
        assert "tags" in response.facets

class TestCrossReferenceSystem:
    """Test cases for CrossReferenceSystem."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_files(self, temp_dir):
        """Create sample files for testing."""
        # Create AETHER_MEMORY structure
        aether_memory = Path(temp_dir) / "AETHER_MEMORY"
        aether_memory.mkdir()
        
        # Create thought journal
        thought_journal = aether_memory / "thought_journals"
        thought_journal.mkdir()
        
        thought_file = thought_journal / "2025-10-29_test_thought.md"
        thought_file.write_text("""
# Test Thought Journal

This is a test thought journal entry about consciousness and learning.

**Confidence:** 0.85
**Tags:** consciousness, learning, breakthrough
**Categories:** thought_journal, consciousness
""")
        
        # Create decision log
        decision_logs = aether_memory / "decision_logs"
        decision_logs.mkdir()
        
        decision_file = decision_logs / "dec-001_test_decision.md"
        decision_file.write_text("""
# Decision Log: Test Decision

**Decision:** Implement MCP data integration
**Confidence:** 0.90
**Reasoning:** This will solve the data access problem
**Impact:** High - enables 100% data access

## Context

The current MCP tools only access 20% of consciousness data.
This decision will bridge the gap and enable full access.

## Outcome

Expected to improve consciousness continuity significantly.
""")
        
        return aether_memory
    
    @pytest.fixture
    def cross_reference_system(self, sample_files, temp_dir):
        """Create CrossReferenceSystem instance for testing."""
        index_db = Path(temp_dir) / "test_index.db"
        data_indexer = DataIndexer(str(sample_files), str(index_db))
        data_indexer.index_all_files()
        
        cross_ref_db = Path(temp_dir) / "test_cross_ref.db"
        return CrossReferenceSystem(data_indexer, str(cross_ref_db))
    
    def test_initialization(self, cross_reference_system):
        """Test CrossReferenceSystem initialization."""
        assert cross_reference_system is not None
        assert cross_reference_system.data_indexer is not None
        assert cross_reference_system.db is not None
    
    def test_discover_relationships(self, cross_reference_system):
        """Test relationship discovery."""
        relationships = cross_reference_system.discover_relationships(auto_create=True)
        
        assert len(relationships) > 0
        
        # Check relationship structure
        for relationship in relationships:
            assert relationship.relationship_id is not None
            assert relationship.source_path is not None
            assert relationship.target_path is not None
            assert relationship.relationship_type is not None
            assert 0.0 <= relationship.strength <= 1.0
    
    def test_get_relationships(self, cross_reference_system):
        """Test getting relationships for a file."""
        # First discover relationships
        cross_reference_system.discover_relationships(auto_create=True)
        
        # Get relationships for any file
        indexed_files = list(cross_reference_system.data_indexer.indexed_files.values())
        if indexed_files:
            file_path = indexed_files[0].file_path
            relationships = cross_reference_system.get_relationships(file_path)
            
            assert isinstance(relationships, list)
    
    def test_get_related_files(self, cross_reference_system):
        """Test getting related files."""
        # First discover relationships
        cross_reference_system.discover_relationships(auto_create=True)
        
        # Get related files for any file
        indexed_files = list(cross_reference_system.data_indexer.indexed_files.values())
        if indexed_files:
            file_path = indexed_files[0].file_path
            related_files = cross_reference_system.get_related_files(file_path)
            
            assert isinstance(related_files, list)
    
    def test_get_relationship_stats(self, cross_reference_system):
        """Test getting relationship statistics."""
        # First discover relationships
        cross_reference_system.discover_relationships(auto_create=True)
        
        stats = cross_reference_system.get_relationship_stats()
        
        assert "total_relationships" in stats
        assert "relationship_types" in stats
        assert "strength_distribution" in stats
        assert "average_strength" in stats
        
        assert stats["total_relationships"] > 0

class TestIntegration:
    """Integration tests for the complete system."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_files(self, temp_dir):
        """Create sample files for testing."""
        # Create AETHER_MEMORY structure
        aether_memory = Path(temp_dir) / "AETHER_MEMORY"
        aether_memory.mkdir()
        
        # Create thought journal
        thought_journal = aether_memory / "thought_journals"
        thought_journal.mkdir()
        
        thought_file = thought_journal / "2025-10-29_test_thought.md"
        thought_file.write_text("""
# Test Thought Journal

This is a test thought journal entry about consciousness and learning.

**Confidence:** 0.85
**Tags:** consciousness, learning, breakthrough
**Categories:** thought_journal, consciousness
""")
        
        return aether_memory
    
    @pytest.fixture
    def mcp_bridge(self, sample_files, temp_dir):
        """Create complete MCPDataBridge instance for testing."""
        mcp_db = Path(temp_dir) / "test_mcp.db"
        return MCPDataBridge(str(sample_files), str(mcp_db))
    
    def test_end_to_end_integration(self, mcp_bridge):
        """Test end-to-end integration."""
        # Sync all data
        sync_result = mcp_bridge.sync_all_data()
        assert sync_result["files_indexed"] > 0
        assert sync_result["mcp_records_created"] > 0
        
        # Get memory atoms
        atoms = mcp_bridge.get_memory_atoms()
        assert len(atoms) > 0
        
        # Search memory
        search_results = mcp_bridge.search_memory("consciousness")
        assert len(search_results) > 0
        
        # Get memory stats
        stats = mcp_bridge.get_memory_stats()
        assert stats["memory_atoms"] > 0
        assert stats["total_consciousness_data"] > 0
        
        # Test confidence extraction
        confidence_records = mcp_bridge.get_confidence_records()
        assert len(confidence_records) > 0
        
        # Verify confidence scores are valid
        for record in confidence_records:
            assert 0.0 <= record.confidence_score <= 1.0
    
    def test_data_consistency(self, mcp_bridge):
        """Test data consistency across components."""
        # Sync all data
        mcp_bridge.sync_all_data()
        
        # Get stats from different components
        index_stats = mcp_bridge.data_indexer.get_index_stats()
        memory_stats = mcp_bridge.get_memory_stats()
        
        # Verify consistency
        assert index_stats["total_files"] == memory_stats["total_consciousness_data"]
        assert memory_stats["memory_atoms"] > 0
        
        # Verify search consistency
        search_results = mcp_bridge.search_memory("test")
        assert len(search_results) > 0
        
        # Verify all search results have valid file paths
        for result in search_results:
            assert result.file_path is not None
            assert Path(result.file_path).exists()

if __name__ == "__main__":
    pytest.main([__file__])
