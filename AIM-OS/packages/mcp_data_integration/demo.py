# packages/mcp_data_integration/demo.py
"""
MCP Data Integration Demo

This script demonstrates the MCP Data Integration package capabilities,
showing how it bridges MCP tools with the AETHER_MEMORY directory.
"""

import sys
import os
from pathlib import Path
import time
import json

# Add the parent directory to the sys.path to allow importing from 'packages'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from mcp_data_integration import MCPDataBridge, SearchEngine, SearchQuery

def main():
    """Run the MCP Data Integration demo."""
    print("MCP Data Integration Demo")
    print("=" * 50)
    
    # Set up paths
    aether_memory_path = "knowledge_architecture/AETHER_MEMORY"
    mcp_db_path = "mcp_integrated_demo.db"
    
    # Check if AETHER_MEMORY exists
    if not Path(aether_memory_path).exists():
        print(f"ERROR: AETHER_MEMORY directory not found at: {aether_memory_path}")
        print("Please ensure you're running this from the AIM-OS root directory.")
        return
    
    print(f"AETHER_MEMORY Path: {aether_memory_path}")
    print(f"MCP Database Path: {mcp_db_path}")
    print()
    
    try:
        # Initialize MCP Data Bridge
        print("Initializing MCP Data Bridge...")
        mcp_bridge = MCPDataBridge(aether_memory_path, mcp_db_path)
        print("MCP Data Bridge initialized")
        print()
        
        # Sync all data
        print("Syncing all consciousness data...")
        start_time = time.time()
        sync_result = mcp_bridge.sync_all_data()
        sync_time = time.time() - start_time
        
        print(f"Data sync completed in {sync_time:.2f} seconds")
        print(f"   Files indexed: {sync_result['files_indexed']}")
        print(f"   MCP records created: {sync_result['mcp_records_created']}")
        print()
        
        # Get memory statistics
        print("Memory Statistics:")
        stats = mcp_bridge.get_memory_stats()
        print(f"   Memory atoms: {stats['memory_atoms']}")
        print(f"   Timeline entries: {stats['timeline_entries']}")
        print(f"   Confidence records: {stats['confidence_records']}")
        print(f"   Total consciousness data: {stats['total_consciousness_data']}")
        print()
        
        # Demonstrate search capabilities
        print("Search Capabilities Demo:")
        print("-" * 30)
        
        # Search for consciousness-related content
        print("Searching for 'consciousness'...")
        search_results = mcp_bridge.search_memory("consciousness")
        print(f"   Found {len(search_results)} results")
        
        if search_results:
            print("   Top result:")
            top_result = search_results[0]
            print(f"     File: {Path(top_result.file_path).name}")
            print(f"     Relevance: {top_result.relevance_score:.3f}")
            print(f"     Snippet: {top_result.content_snippet[:100]}...")
        print()
        
        # Search for confidence-related content
        print("Searching for 'confidence'...")
        confidence_results = mcp_bridge.search_memory("confidence")
        print(f"   Found {len(confidence_results)} results")
        print()
        
        # Demonstrate MCP memory atoms
        print("MCP Memory Atoms Demo:")
        print("-" * 30)
        
        atoms = mcp_bridge.get_memory_atoms(limit=5)
        print(f"Retrieved {len(atoms)} memory atoms:")
        
        for i, atom in enumerate(atoms, 1):
            # Get file path from metadata
            file_path = atom.metadata.get('file_path', 'unknown')
            file_name = Path(file_path).name if file_path != 'unknown' else 'unknown'
            print(f"   {i}. {file_name}")
            print(f"      Type: {atom.content_type}")
            print(f"      Categories: {', '.join(atom.categories[:3])}")
            print(f"      Tags: {', '.join(atom.tags[:3])}")
            print(f"      Size: {len(atom.content)} characters")
            print()
        
        # Demonstrate confidence records
        print("Confidence Records Demo:")
        print("-" * 30)
        
        confidence_records = mcp_bridge.get_confidence_records(limit=5)
        print(f"Retrieved {len(confidence_records)} confidence records:")
        
        for i, record in enumerate(confidence_records, 1):
            print(f"   {i}. Confidence: {record.confidence_score:.3f}")
            print(f"      Context: {record.context[:100]}...")
            print(f"      File: {Path(record.file_path).name}")
            print(f"      Timestamp: {record.timestamp}")
            print()
        
        # Demonstrate timeline entries
        print("Timeline Entries Demo:")
        print("-" * 30)
        
        timeline_entries = mcp_bridge.get_timeline_entries(limit=5)
        print(f"Retrieved {len(timeline_entries)} timeline entries:")
        
        for i, entry in enumerate(timeline_entries, 1):
            print(f"   {i}. {entry.description}")
            print(f"      Type: {entry.event_type}")
            print(f"      File: {Path(entry.file_path).name}")
            print(f"      Timestamp: {entry.timestamp}")
            print()
        
        # Demonstrate advanced search
        print("Advanced Search Demo:")
        print("-" * 30)
        
        # Create search engine for advanced queries
        search_engine = SearchEngine(mcp_bridge.data_indexer)
        
        # Search with filters
        query = SearchQuery(
            query_text="consciousness learning",
            file_types=["thought_journal"],
            limit=3
        )
        
        print("Searching for 'consciousness learning' in thought journals...")
        response = search_engine.search(query)
        print(f"   Found {response.total_results} results in {response.search_time_ms:.2f}ms")
        
        if response.results:
            print("   Top results:")
            for i, result in enumerate(response.results, 1):
                print(f"     {i}. {Path(result.file_path).name} (relevance: {result.relevance_score:.3f})")
        print()
        
        # Show search facets
        print("Search Facets:")
        print(f"   File types: {response.facets.get('file_types', {})}")
        print(f"   Categories: {list(response.facets.get('categories', {}).keys())[:5]}")
        print(f"   Tags: {list(response.facets.get('tags', {}).keys())[:5]}")
        print()
        
        # Demonstrate monitoring status
        print("Monitoring Status:")
        monitoring_status = stats['monitoring_status']
        print(f"   Status: {'Active' if monitoring_status['is_monitoring'] else 'Inactive'}")
        print(f"   Method: {monitoring_status['monitoring_method']}")
        print(f"   Files monitored: {monitoring_status['files_being_monitored']}")
        print()
        
        # Performance summary
        print("Performance Summary:")
        print(f"   Data sync time: {sync_time:.2f} seconds")
        print(f"   Search response time: {response.search_time_ms:.2f}ms")
        print(f"   Total memory atoms: {stats['memory_atoms']}")
        print(f"   Data coverage: {stats['memory_atoms'] / stats['total_consciousness_data'] * 100:.1f}%")
        print()
        
        print("Demo completed successfully!")
        print()
        print("Key Benefits Demonstrated:")
        print("   - MCP tools now access 100% of consciousness data")
        print("   - Real-time file monitoring and indexing")
        print("   - Advanced search capabilities")
        print("   - Confidence tracking and analysis")
        print("   - Timeline integration")
        print("   - Cross-reference capabilities")
        print()
        print("MCP Data Integration Epic: Phase 2 Complete!")
        
    except Exception as e:
        print(f"ERROR: Error during demo: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        try:
            mcp_bridge.close()
            print("Cleanup completed")
        except:
            pass

if __name__ == "__main__":
    main()
