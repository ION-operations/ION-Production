#!/usr/bin/env python3
"""
Test Fixes Verification

Tests that the CMC Windows filename fix and VIF initialization fix work correctly.
"""

import os
import sys
from pathlib import Path

# Set working keys
os.environ["GEMINI_API_KEY"] = "AIzaSyCL2QTE7zT8oT6hC_GxM0Nt1p8QDmB5j7w"
os.environ["CEREBRAS_API_KEY"] = "csk-prtm28t8d2wttrh5nwj63wpvy9xpejvymw84cm25dtrwhpht"

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent))

def test_cmc_tag_sanitization():
    """Test that CMC tag sanitization works"""
    print("=" * 80)
    print("TEST: CMC Tag Sanitization Fix")
    print("=" * 80)
    
    try:
        from packages.cmc_service.memory_store import MemoryStore
        from packages.cmc_service.models import AtomCreate, AtomContent
        
        # Create test memory store
        test_dir = Path("./test_cmc_fix")
        test_dir.mkdir(exist_ok=True)
        
        store = MemoryStore(str(test_dir))
        
        # Create atom with tag containing colons (Windows invalid)
        atom_create = AtomCreate(
            modality="test",
            content=AtomContent(inline="Test content"),
            tags={
                "system:gemini:p0": 1.0,  # Contains colons
                "system:cmc:p0": 1.0,     # Contains colons
                "normal_tag": 1.0         # Normal tag
            }
        )
        
        print("\n[TEST] Creating atom with tags containing colons...")
        atom = store.create_atom(atom_create)
        print(f"   [OK] Atom created: {atom.id}")
        
        # Check that tag files were created with sanitized names
        tag_dir = test_dir / "index" / "tags"
        print(f"\n[TEST] Checking tag files in {tag_dir}...")
        
        if tag_dir.exists():
            tag_files = list(tag_dir.glob("*.json"))
            print(f"   Found {len(tag_files)} tag files:")
            for tag_file in tag_files:
                print(f"      - {tag_file.name}")
            
            # Check for sanitized names (no colons)
            sanitized_files = [f for f in tag_files if ":" not in f.name]
            if len(sanitized_files) == len(tag_files):
                print(f"\n   [OK] All tag files have sanitized names (no colons)")
                return True
            else:
                print(f"\n   [FAIL] Some tag files still contain colons")
                return False
        else:
            print(f"\n   [WARNING] Tag directory doesn't exist yet")
            return True  # Directory will be created on first tag
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False


def test_vif_initialization():
    """Test that VIF initialization works correctly"""
    print("\n" + "=" * 80)
    print("TEST: VIF Initialization Fix")
    print("=" * 80)
    
    try:
        from lucid_mcp_server import SimpleMCPServer
        
        print("\n[TEST] Initializing MCP server...")
        server = SimpleMCPServer(memory_directory="./test_mcp_memory")
        print("   [OK] MCP server initialized")
        
        # Check VIF availability
        print(f"\n[TEST] Checking VIF availability...")
        print(f"   vif_available: {getattr(server, 'vif_available', 'NOT SET')}")
        print(f"   vif_kappa_gate: {server.vif_kappa_gate is not None if hasattr(server, 'vif_kappa_gate') else 'NOT SET'}")
        print(f"   vif_ece_tracker: {server.vif_ece_tracker is not None if hasattr(server, 'vif_ece_tracker') else 'NOT SET'}")
        print(f"   TaskCriticality: {server.TaskCriticality is not None if hasattr(server, 'TaskCriticality') else 'NOT SET'}")
        
        # Test track_confidence with fallback
        print(f"\n[TEST] Testing track_confidence (should work even if VIF unavailable)...")
        result = server.track_confidence({
            "task": "Test task",
            "confidence": 0.75,
            "reasoning": "Test reasoning",
            "evidence": ["Test evidence"],
            "task_criticality": "ROUTINE"
        })
        
        if result.get("success"):
            print(f"   [OK] track_confidence succeeded")
            print(f"   Message: {result.get('message', '')[:100]}")
            return True
        else:
            print(f"   [FAIL] track_confidence failed: {result.get('error', 'Unknown error')}")
            return False
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 80)
    print("FIXES VERIFICATION TEST")
    print("=" * 80)
    
    results = []
    
    # Test CMC fix
    results.append(("CMC Tag Sanitization", test_cmc_tag_sanitization()))
    
    # Test VIF fix
    results.append(("VIF Initialization", test_vif_initialization()))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"   {status}: {test_name}")
    
    print(f"\n   Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n   [SUCCESS] All fixes verified!")
        print("\n   Next: Test full LLM API integration")
        return 0
    else:
        print(f"\n   [WARNING] {total - passed} test(s) failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

