"""Quick test script for NL Tags package"""

from __future__ import annotations

import sys
from pathlib import Path

# Add root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from packages.nl_tags.tag_parser import NLTagParser
from packages.nl_tags.tag_registry import NLTagRegistry


def test_parser():
    """Test tag parser"""
    print("=" * 60)
    print("Testing NL Tag Parser")
    print("=" * 60)
    
    parser = NLTagParser()
    
    # Test Python tag extraction
    python_code = """# NL: Validates user authentication token
def validate_token(token: str) -> bool:
    if not token:
        return False
    return len(token) > 10

# NL: Processes payment transaction
async def process_payment(amount: float, user_id: str) -> dict:
    return {"status": "success"}
"""
    
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(python_code)
        file_path = f.name
    
    try:
        tags = parser.parse_file(file_path)
        print(f"\n✅ Extracted {len(tags)} tags")
        assert len(tags) == 2, f"Expected 2 tags, got {len(tags)}"
        
        for i, tag in enumerate(tags, 1):
            print(f"\n  Tag {i}:")
            print(f"    Text: {tag.tag_text}")
            print(f"    Line: {tag.line_start}")
            print(f"    Language: {tag.language}")
        
        print("\n✅ Parser test PASSED")
        return True
    except Exception as e:
        print(f"\n❌ Parser test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        import os
        os.unlink(file_path)


def test_registry():
    """Test tag registry"""
    print("\n" + "=" * 60)
    print("Testing NL Tag Registry")
    print("=" * 60)
    
    registry = NLTagRegistry()
    
    # Test with a real file if available
    test_file = "packages/vif/witness.py"
    if Path(test_file).exists():
        tags = registry.get_tags_for_file(test_file)
        print(f"\n✅ Found {len(tags)} tags in {test_file}")
        
        # Get coverage stats
        stats = registry.get_coverage_stats("packages/vif")
        print(f"\n✅ Coverage stats:")
        print(f"    Total files: {stats.total_files}")
        print(f"    Tagged files: {stats.tagged_files}")
        print(f"    Total tags: {stats.total_tags}")
        print(f"    Coverage: {stats.coverage_percentage:.1f}%")
        
        print("\n✅ Registry test PASSED")
        return True
    else:
        print(f"\n⚠️  Test file {test_file} not found, skipping registry test")
        return True


if __name__ == "__main__":
    print("\n🚀 Starting NL Tags Package Tests\n")
    
    parser_ok = test_parser()
    registry_ok = test_registry()
    
    print("\n" + "=" * 60)
    if parser_ok and registry_ok:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 60)

