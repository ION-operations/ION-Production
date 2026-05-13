#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Index AIM-OS Documentation for HHNI Context Retrieval

Based on team consensus (R-LLM-API-004):
- Option 3 (Hybrid Approach): Index key documents now, full indexing during IDE integration
- P0 Priority: SUPER_INDEX, system T0-T2 docs, timeline entries, integration docs

This script:
1. Indexes timeline entries (already in CMC, just needs HHNI indexing)
2. Indexes 5-7 key documents as CMC atoms with hhni_index tag
3. Uses proper tag format and metadata structure (from Atlas's recommendations)
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

# Fix Windows console encoding for emojis
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add workspace root to path
workspace_root = Path(__file__).parent.parent
sys.path.insert(0, str(workspace_root))

# Add packages directory to path (for cmc_service)
packages_path = workspace_root / "packages"
sys.path.insert(0, str(packages_path))

try:
    # Import CMC (same approach as lucid_mcp_server.py)
    from cmc_service import MemoryStore
    from cmc_service.models import AtomCreate, AtomContent
except ImportError as e:
    print(f"ERROR: Failed to import CMC: {e}")
    print("Make sure you're running from the workspace root and CMC is installed")
    print(f"Workspace root: {workspace_root}")
    print(f"Packages path: {packages_path}")
    sys.exit(1)


class AIMOSDocumentIndexer:
    """Index AIM-OS documents for HHNI context retrieval"""
    
    def __init__(self, memory_directory: str = "./mcp_memory"):
        """Initialize the indexer with CMC memory store"""
        self.memory = MemoryStore(memory_directory)
        self.workspace_root = workspace_root
        self.indexed_docs: List[Dict[str, Any]] = []
        
    def index_document(
        self,
        file_path: str,
        document_type: str,
        system: Optional[str] = None,
        priority: str = "P0"
    ) -> Optional[str]:
        """
        Index a single document as a CMC atom with hhni_index tag.
        
        Args:
            file_path: Relative path to document from workspace root
            document_type: Type of document (e.g., "architecture", "protocol", "api", "goal")
            system: Optional system name (e.g., "cmc", "hhni", "apoe")
            priority: Priority level (P0, P1, P2)
        
        Returns:
            Atom ID if successful, None otherwise
        """
        full_path = self.workspace_root / file_path
        
        if not full_path.exists():
            print(f"⚠️  WARNING: File not found: {file_path}")
            return None
        
        try:
            # Read document content
            content = full_path.read_text(encoding="utf-8")
            file_size = full_path.stat().st_size
            line_count = len(content.splitlines())
            
            # Build tags (from Atlas's recommendations)
            tags: Dict[str, float] = {
                "hhni_index": 1.0,  # Required for HHNI poller indexing
                "system:cmc:p0": 1.0,
                "integration_type:document": 1.0,
                "connection:document->hhni": 1.0,
                "modality:text": 1.0,
                f"document_type:{document_type}": 1.0,
                f"priority:{priority}": 1.0,
            }
            
            if system:
                tags[f"system:{system}"] = 1.0
            
            # Build metadata (from Atlas's recommendations)
            metadata: Dict[str, Any] = {
                "file_path": file_path,
                "document_type": document_type,
                "indexed_at": datetime.now(timezone.utc).isoformat(),
                "file_size": file_size,
                "line_count": line_count,
                "priority": priority,
            }
            
            if system:
                metadata["system"] = system
            
            # Create CMC atom
            atom_create = AtomCreate(
                content=AtomContent(inline=content),
                tags=tags,
                modality="text",
                metadata=metadata
            )
            
            atom = self.memory.create_atom(atom_create)
            
            print(f"✅ Indexed: {file_path} (atom_id: {atom.id[:8]}...)")
            
            self.indexed_docs.append({
                "file_path": file_path,
                "atom_id": atom.id,
                "document_type": document_type,
                "system": system,
                "priority": priority,
                "file_size": file_size,
                "line_count": line_count,
            })
            
            return atom.id
            
        except Exception as e:
            print(f"❌ ERROR indexing {file_path}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def index_priority_documents(self):
        """Index P0 priority documents based on team consensus"""
        
        print("📚 Indexing P0 Priority Documents...")
        print("=" * 60)
        
        # P0.1: SUPER_INDEX (Universal Priority - All 8 agents)
        print("\n1. Indexing SUPER_INDEX (Universal Priority)...")
        self.index_document(
            "knowledge_architecture/SUPER_INDEX.md",
            document_type="architecture",
            priority="P0"
        )
        
        # P0.2: System T0-T2 Executive Summaries (Universal Priority)
        print("\n2. Indexing System T0-T2 Executive Summaries...")
        system_docs = [
            ("knowledge_architecture/systems/cmc/T0_executive.md", "cmc"),
            ("knowledge_architecture/systems/hhni/T0_executive.md", "hhni"),
            ("knowledge_architecture/systems/vif/T0_executive.md", "vif"),
            ("knowledge_architecture/systems/tcs/T0_executive.md", "tcs"),
            ("knowledge_architecture/systems/apoe/T0_executive.md", "apoe"),
            ("knowledge_architecture/systems/seg/T0_executive.md", "seg"),
            ("knowledge_architecture/systems/cognitive_analysis/T0_executive.md", "cas"),
            ("knowledge_architecture/systems/sdfcvf/T0_executive.md", "sdfcvf"),
        ]
        
        for doc_path, system in system_docs:
            self.index_document(
                doc_path,
                document_type="architecture",
                system=system,
                priority="P0"
            )
        
        # P0.3: System T2 Architecture Docs (7/8 agents)
        print("\n3. Indexing System T2 Architecture Docs...")
        t2_docs = [
            ("knowledge_architecture/systems/cmc/T2_architecture.md", "cmc"),
            ("knowledge_architecture/systems/hhni/T2_architecture.md", "hhni"),
            ("knowledge_architecture/systems/vif/T2_architecture.md", "vif"),
            ("knowledge_architecture/systems/tcs/T2_architecture.md", "tcs"),
            ("knowledge_architecture/systems/apoe/T2_architecture.md", "apoe"),
            ("knowledge_architecture/systems/seg/T2_architecture.md", "seg"),
        ]
        
        for doc_path, system in t2_docs:
            self.index_document(
                doc_path,
                document_type="architecture",
                system=system,
                priority="P0"
            )
        
        # P0.4: Integration Documentation (6/8 agents)
        print("\n4. Indexing Integration Documentation...")
        integration_docs = [
            ("ide_orchestration/prototypes/dac/docs/SUBSYSTEM_HIERARCHY_MAPPING.md", "integration"),
            ("ide_orchestration/prototypes/dac/docs/SYNTHESIS_SESSION_FINAL_OUTCOMES.md", "integration"),
        ]
        
        for doc_path, doc_type in integration_docs:
            self.index_document(
                doc_path,
                document_type=doc_type,
                priority="P0"
            )
        
        # P0.5: LLM API Documentation (Atlas P0)
        print("\n5. Indexing LLM API Documentation...")
        llm_api_docs = [
            ("ide_orchestration/prototypes/dac/docs/LLM_API_IMPLEMENTATION_PLAN_GEMINI_CEREBRAS.md", "api"),
            ("ide_orchestration/prototypes/dac/docs/LLM_API_TEAM_RESPONSES_SUMMARY.md", "api"),
        ]
        
        for doc_path, doc_type in llm_api_docs:
            self.index_document(
                doc_path,
                document_type=doc_type,
                priority="P0"
            )
        
        # P0.6: Goals Documentation (4/8 agents)
        print("\n6. Indexing Goals Documentation...")
        self.index_document(
            "goals/GOAL_TREE.yaml",
            document_type="goal",
            priority="P0"
        )
        
        print("\n" + "=" * 60)
        print(f"✅ Indexed {len(self.indexed_docs)} documents")
        
    def print_summary(self):
        """Print indexing summary"""
        print("\n" + "=" * 60)
        print("📊 INDEXING SUMMARY")
        print("=" * 60)
        
        total_size = sum(doc["file_size"] for doc in self.indexed_docs)
        total_lines = sum(doc["line_count"] for doc in self.indexed_docs)
        
        print(f"\nTotal Documents Indexed: {len(self.indexed_docs)}")
        print(f"Total Size: {total_size:,} bytes ({total_size / 1024:.1f} KB)")
        print(f"Total Lines: {total_lines:,}")
        
        print("\n📋 Indexed Documents:")
        for i, doc in enumerate(self.indexed_docs, 1):
            print(f"  {i}. {doc['file_path']}")
            print(f"     System: {doc.get('system', 'N/A')}")
            print(f"     Type: {doc['document_type']}")
            print(f"     Priority: {doc['priority']}")
            print(f"     Size: {doc['file_size']:,} bytes, {doc['line_count']:,} lines")
            print()
        
        print("=" * 60)
        print("\n✅ Documents indexed with hhni_index tag")
        print("📝 HHNI poller will automatically index these atoms")
        print("🧪 Ready for context-aware LLM API testing!")
        print("\n" + "=" * 60)


def main():
    """Main entry point"""
    print("🚀 AIM-OS Document Indexer for HHNI Context Retrieval")
    print("=" * 60)
    print("Based on team consensus (R-LLM-API-004)")
    print("Strategy: Option 3 (Hybrid Approach)")
    print("=" * 60)
    
    # Initialize indexer
    indexer = AIMOSDocumentIndexer()
    
    # Index priority documents
    indexer.index_priority_documents()
    
    # Print summary
    indexer.print_summary()
    
    print("\n✅ Indexing complete!")
    print("\n📝 Next Steps:")
    print("  1. Wait for HHNI poller to index atoms (or trigger manually)")
    print("  2. Test context retrieval with system-specific queries")
    print("  3. Validate context quality and response accuracy")
    print("\n💡 Note: Timeline entries are already in CMC, just need HHNI indexing")


if __name__ == "__main__":
    main()

