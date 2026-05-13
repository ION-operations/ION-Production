"""NL Tags Package - Demo Script

Demonstrates NL tag extraction and storage capabilities.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from packages.nl_tags.tag_parser import NLTagParser
from packages.nl_tags.tag_registry import NLTagRegistry


def demo_tag_extraction():
    """Demonstrate tag extraction"""
    print("=" * 60)
    print("NL Tag Extraction Demo")
    print("=" * 60)
    
    parser = NLTagParser()
    
    # Example Python file
    python_code = """# NL: Validates user authentication token
def validate_token(token: str) -> bool:
    if not token:
        return False
    return len(token) > 10

# NL: Processes payment transaction
async def process_payment(amount: float, user_id: str) -> dict:
    # Process payment logic
    return {"status": "success", "transaction_id": "12345"}
"""
    
    # Write to temp file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(python_code)
        file_path = f.name
    
    try:
        # Extract tags
        tags = parser.parse_file(file_path)
        
        print(f"\nExtracted {len(tags)} tags from {file_path}:")
        for i, tag in enumerate(tags, 1):
            print(f"\n  Tag {i}:")
            print(f"    Text: {tag.tag_text}")
            print(f"    Line: {tag.line_start}")
            print(f"    Language: {tag.language}")
            print(f"    Code Block Preview: {tag.code_block[:50] if tag.code_block else 'N/A'}...")
        
    finally:
        import os
        os.unlink(file_path)


def demo_registry():
    """Demonstrate tag registry"""
    print("\n" + "=" * 60)
    print("NL Tag Registry Demo")
    print("=" * 60)
    
    registry = NLTagRegistry()
    
    # Example: Get tags for a real file (if exists)
    test_file = "packages/vif/witness.py"
    if Path(test_file).exists():
        tags = registry.get_tags_for_file(test_file)
        print(f"\nFound {len(tags)} tags in {test_file}")
        
        if tags:
            print("\nSample tags:")
            for tag in tags[:3]:  # Show first 3
                print(f"  - {tag.tag_text[:50]}...")
    else:
        print(f"\nTest file {test_file} not found, skipping")


if __name__ == "__main__":
    demo_tag_extraction()
    demo_registry()
    print("\n" + "=" * 60)
    print("Demo Complete!")
    print("=" * 60)


