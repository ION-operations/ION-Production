"""
Unit Tests: MasterIndex
"""

import pytest
import tempfile
import os
from datetime import datetime
from deepsearch.master_index import MasterIndex


@pytest.fixture
def index():
    """Create temporary index for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        index_path = os.path.join(tmpdir, "test_index.db")
        idx = MasterIndex(index_path)
        yield idx
        idx.close()


def test_index_initialization(index):
    """Test index initializes correctly"""
    assert index.conn is not None
    assert os.path.exists(index.index_path)


def test_add_source(index):
    """Test adding source to index"""
    index.add_source(
        url="https://example.com/page",
        content="Test content",
        trust_score=0.8,
        entropy=0.7,
        metadata={'author': 'Test'}
    )
    
    source = index.get_source("https://example.com/page")
    
    assert source is not None
    assert source['url'] == "https://example.com/page"
    assert source['trust_score'] == 0.8
    assert source['entropy'] == 0.7


def test_get_source_not_found(index):
    """Test getting non-existent source returns None"""
    source = index.get_source("https://notfound.com")
    
    assert source is None


def test_update_source(index):
    """Test updating existing source"""
    url = "https://example.com/page"
    
    # Add initial
    index.add_source(url, "content1", 0.5, 0.5)
    
    # Update
    index.add_source(url, "content2", 0.9, 0.8)
    
    source = index.get_source(url)
    
    # Should have new scores
    assert source['trust_score'] == 0.9
    assert source['entropy'] == 0.8


def test_needs_update_new_source(index):
    """Test needs_update for new source"""
    assert index.needs_update("https://new.com", "content")


def test_needs_update_same_content(index):
    """Test needs_update for unchanged content"""
    url = "https://example.com"
    content = "Test content"
    
    index.add_source(url, content, 0.5, 0.5)
    
    # Same content should not need update
    assert not index.needs_update(url, content)


def test_needs_update_changed_content(index):
    """Test needs_update for changed content"""
    url = "https://example.com"
    
    index.add_source(url, "content1", 0.5, 0.5)
    
    # Different content should need update
    assert index.needs_update(url, "content2")


def test_query_no_filters(index):
    """Test querying without filters"""
    # Add multiple sources
    index.add_source("https://site1.com", "content1", 0.8, 0.7)
    index.add_source("https://site2.com", "content2", 0.6, 0.5)
    index.add_source("https://site3.com", "content3", 0.9, 0.8)
    
    results = index.query()
    
    # Should return all 3, sorted by quality (trust * entropy)
    assert len(results) == 3
    assert results[0]['url'] == "https://site3.com"  # Highest quality


def test_query_min_trust_filter(index):
    """Test querying with min trust filter"""
    index.add_source("https://high.com", "content1", 0.9, 0.7)
    index.add_source("https://low.com", "content2", 0.4, 0.5)
    
    results = index.query(min_trust=0.7)
    
    # Should only return high trust source
    assert len(results) == 1
    assert results[0]['url'] == "https://high.com"


def test_query_min_entropy_filter(index):
    """Test querying with min entropy filter"""
    index.add_source("https://diverse.com", "content1", 0.7, 0.9)
    index.add_source("https://simple.com", "content2", 0.7, 0.3)
    
    results = index.query(min_entropy=0.7)
    
    # Should only return high entropy source
    assert len(results) == 1
    assert results[0]['url'] == "https://diverse.com"


def test_query_limit(index):
    """Test query result limit"""
    for i in range(10):
        index.add_source(f"https://site{i}.com", f"content{i}", 0.5, 0.5)
    
    results = index.query(limit=5)
    
    assert len(results) == 5


def test_file_hash_tracking(index):
    """Test file hash update tracking"""
    file_path = "/path/to/file.txt"
    content = "File content"
    
    index.update_file_hash(file_path, content)
    
    # Should not need update for same content
    assert not index.file_needs_update(file_path, content)


def test_file_needs_update_changed(index):
    """Test file needs update when content changes"""
    file_path = "/path/to/file.txt"
    
    index.update_file_hash(file_path, "content1")
    
    # Changed content should need update
    assert index.file_needs_update(file_path, "content2")


def test_get_stats(index):
    """Test getting index statistics"""
    index.add_source("https://site1.com", "content1", 0.8, 0.7)
    index.add_source("https://site2.com", "content2", 0.6, 0.5)
    
    stats = index.get_stats()
    
    assert 'total_sources' in stats
    assert 'avg_trust' in stats
    assert 'avg_entropy' in stats
    assert stats['total_sources'] == 2


def test_clear(index):
    """Test clearing index"""
    index.add_source("https://test.com", "content", 0.5, 0.5)
    
    index.clear()
    
    results = index.query()
    assert len(results) == 0


def test_hash_content_consistency():
    """Test content hashing is consistent"""
    hash1 = MasterIndex._hash_content("test content")
    hash2 = MasterIndex._hash_content("test content")
    
    assert hash1 == hash2


def test_hash_content_different():
    """Test different content produces different hash"""
    hash1 = MasterIndex._hash_content("content1")
    hash2 = MasterIndex._hash_content("content2")
    
    assert hash1 != hash2

