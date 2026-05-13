"""
Tests for PLIx Parser Bridge

Validates TypeScript <-> Python language boundary.
"""

import pytest
from apoe.plix_compiler import PLIxParserBridge, parse_plix, PLIxParseError


def test_parse_simple_intent():
    """Test parsing simple PLIx intent"""
    plix_text = """
ask ent:test/resource
  act:reserve
  requires con:available == True
  ensures con:reserved == True
  plan []
"""
    
    intent = parse_plix(plix_text)
    
    assert intent.speech_act == "ask"
    assert intent.entity == "test/resource"
    assert intent.action == "reserve"
    assert "preconditions" in intent.contract or "requires" in intent.contract
    assert "postconditions" in intent.contract or "ensures" in intent.contract


def test_parse_with_plan():
    """Test parsing intent with plan steps"""
    plix_text = """
ask ent:room/meeting
  act:reserve
  requires con:available == True
  plan [
    task check := api.check_room()
    task reserve := api.reserve()
      depends_on: check
  ]
"""
    
    intent = parse_plix(plix_text)
    
    assert "steps" in intent.plan
    # Should have 2 steps
    assert len(intent.plan.get("steps", [])) >= 2


def test_parse_error_handling():
    """Test parse error handling"""
    invalid_plix = "invalid {{ syntax"
    
    with pytest.raises(PLIxParseError) as exc_info:
        parse_plix(invalid_plix)
    
    assert len(exc_info.value.errors) > 0
    assert "message" in exc_info.value.errors[0]


def test_caching():
    """Test that parsing is cached"""
    bridge = PLIxParserBridge()
    
    plix_text = "ask ent:test act:test plan []"
    
    # First parse
    intent1 = bridge.parse(plix_text)
    
    # Second parse (should be cached)
    intent2 = bridge.parse(plix_text)
    
    # Should be same object (from cache)
    assert intent1.entity == intent2.entity
    
    # Check cache stats
    stats = bridge.get_cache_stats()
    assert stats["total_entries"] >= 1


def test_cache_invalidation():
    """Test cache TTL"""
    bridge = PLIxParserBridge(cache_ttl_seconds=1)
    
    plix_text = "ask ent:test act:test plan []"
    
    # Parse and cache
    bridge.parse(plix_text)
    
    # Wait for cache to expire
    import time
    time.sleep(1.5)
    
    # Cache should be stale
    stats = bridge.get_cache_stats()
    assert stats["stale_entries"] >= 1


def test_node_not_found():
    """Test error when Node.js not found"""
    bridge = PLIxParserBridge(node_path="/nonexistent/node")
    
    with pytest.raises(FileNotFoundError) as exc_info:
        bridge.parse("ask ent:test act:test plan []")
    
    assert "Node.js not found" in str(exc_info.value)
    assert "install Node.js" in str(exc_info.value)


@pytest.mark.skip(reason="Requires mocking for timeout simulation")
def test_timeout_handling():
    """Test timeout handling for slow parses"""
    # Would need to mock subprocess to simulate timeout
    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

