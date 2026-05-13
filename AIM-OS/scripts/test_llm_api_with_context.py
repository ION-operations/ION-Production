#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test LLM API with HHNI Context Retrieval

Tests the full pipeline:
1. HHNI context retrieval
2. Context formatting for LLM
3. LLM API call with context
4. Response validation

Based on team consensus (R-LLM-API-004) testing recommendations.
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional

# Fix Windows console encoding for emojis
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add workspace root to path
workspace_root = Path(__file__).parent.parent
sys.path.insert(0, str(workspace_root))
packages_path = workspace_root / "packages"
sys.path.insert(0, str(packages_path))

try:
    from hhni import HierarchicalIndex
    from hhni.retrieval import TwoStageRetriever, RetrievalConfig
    from packages.api_service_registry.llm import get_api_registry
    from cmc_service import MemoryStore
except ImportError as e:
    print(f"ERROR: Failed to import dependencies: {e}")
    sys.exit(1)


class LLMContextTester:
    """Test LLM API with HHNI context retrieval"""
    
    def __init__(self, memory_directory: str = "./mcp_memory"):
        """Initialize tester with HHNI and LLM API registry"""
        self.memory_directory = memory_directory
        
        # Initialize CMC memory store
        self.memory = MemoryStore(memory_directory)
        
        # Initialize HHNI index (empty - will be populated from CMC)
        self.hhni_index = HierarchicalIndex()
        
        # Initialize LLM API registry
        self.api_registry = get_api_registry()
        
        # Build HHNI index from CMC atoms (similar to MCP server)
        self._build_hhni_index()
        
        # Initialize TwoStageRetriever with full DVNS physics pipeline
        retrieval_config = RetrievalConfig(
            token_budget=4000,  # Default token budget
            coarse_k=100,  # Initial candidate pool
            min_relevance=0.3,  # Minimum relevance threshold
            dvns_iterations=50,  # DVNS optimization iterations
            enable_conflict_resolution=True,
            enable_compression=True
        )
        self.hhni_retriever = TwoStageRetriever(
            hierarchical_index=self.hhni_index,
            config=retrieval_config
        )
    
    def _build_hhni_index(self):
        """Build HHNI index from CMC atoms (similar to MCP server _build_hhni_index)"""
        print("\n🔨 Building HHNI Index from CMC...")
        print("=" * 60)
        
        if not self.memory:
            print("❌ ERROR: Memory store not initialized")
            return
        
        if self.hhni_index is None:
            print("❌ ERROR: HHNI index not initialized")
            return
        
        try:
            # Get all atoms from CMC
            atoms = list(self.memory.list_atoms(limit=1000))
            
            print(f"📊 Found {len(atoms)} atoms in CMC")
            
            if not atoms:
                print("⚠️  WARNING: No atoms found in CMC")
                return
            
            # Filter atoms with hhni_index tag
            indexed_count = 0
            skipped_count = 0
            error_count = 0
            
            for atom in atoms:
                try:
                    # Check if atom has hhni_index tag
                    if "hhni_index" not in atom.tags:
                        skipped_count += 1
                        continue
                    
                    # Extract content from atom
                    content = ""
                    if hasattr(atom, 'content') and atom.content:
                        if hasattr(atom.content, 'inline') and atom.content.inline:
                            content = atom.content.inline
                        elif hasattr(atom.content, 'uri') and atom.content.uri:
                            # For URI content, we'd need to read the file
                            # For now, skip URI content
                            continue
                        elif isinstance(atom.content, str):
                            content = atom.content
                    
                    if not content:
                        print(f"⚠️  WARNING: Atom {atom.id[:8]}... has no content")
                        skipped_count += 1
                        continue
                    
                    # Index document in HHNI
                    doc_id = f"atom_{atom.id}"
                    index_metadata = {
                        "atom_id": atom.id,
                        "modality": getattr(atom, 'modality', 'text'),
                        "tags": dict(getattr(atom, 'tags', {})),
                        "metadata": dict(getattr(atom, 'metadata', {})),
                    }
                    
                    if hasattr(atom, 'created_at') and atom.created_at:
                        index_metadata["created_at"] = atom.created_at.isoformat()
                    
                    # Index document
                    self.hhni_index.index_document(
                        content=content,
                        doc_id=doc_id,
                        metadata=index_metadata
                    )
                    indexed_count += 1
                    
                    if indexed_count <= 3:
                        print(f"   ✅ Indexed: {doc_id[:20]}... ({len(content)} chars)")
                    
                except Exception as e:
                    error_count += 1
                    print(f"⚠️  Warning: Failed to index atom {atom.id[:8] if hasattr(atom, 'id') else 'unknown'}...: {e}")
                    if error_count <= 3:
                        import traceback
                        traceback.print_exc()
                    continue
            
            print(f"\n✅ HHNI Index Building Complete:")
            print(f"   Indexed: {indexed_count} atoms")
            print(f"   Skipped (no hhni_index tag): {skipped_count}")
            print(f"   Errors: {error_count}")
            print(f"   Total nodes in index: {len(self.hhni_index)}")
            
            if indexed_count == 0:
                print("\n⚠️  WARNING: No atoms were indexed!")
                print("   This could mean:")
                print("   - No atoms have 'hhni_index' tag")
                print("   - Atoms have no content")
                print("   - Indexing failed silently")
            
        except Exception as e:
            print(f"❌ ERROR: Failed to build HHNI index: {e}")
            import traceback
            traceback.print_exc()
        
    def test_context_retrieval(self, query: str, token_budget: Optional[int] = None) -> Dict[str, Any]:
        """
        Test HHNI context retrieval.
        
        Args:
            query: Natural language query
            token_budget: Optional token budget for context window validation
        
        Returns:
            Retrieval result with context items
        """
        print(f"\n🔍 Testing Context Retrieval...")
        print(f"Query: {query}")
        print("=" * 60)
        
        try:
            # Retrieve context from HHNI
            retrieval_result = self.hhni_retriever.retrieve(
                query=query,
                token_budget=token_budget or 4000
            )
            
            print(f"\n✅ Context Retrieved:")
            print(f"   Selected Items: {len(retrieval_result.selected_items)}")
            print(f"   Total Tokens: {retrieval_result.total_tokens}")
            print(f"   Relevance Scores: {[item.relevance for item in retrieval_result.selected_items[:5]]}")
            
            # Format context items for LLM
            context_items = []
            for item in retrieval_result.selected_items:
                context_items.append({
                    "content": item.content,
                    "relevance": item.relevance,
                    "source_id": item.source_id,
                    "tokens": item.estimated_tokens if hasattr(item, 'estimated_tokens') else 0
                })
            
            print(f"\n📋 Context Items (first 3):")
            for i, item in enumerate(context_items[:3], 1):
                print(f"   {i}. Relevance: {item['relevance']:.3f}, Tokens: {item['tokens']}")
                print(f"      Content preview: {item['content'][:100]}...")
            
            return {
                "success": True,
                "context_items": context_items,
                "total_items": len(context_items),
                "total_tokens": retrieval_result.total_tokens,
                "retrieval_result": retrieval_result
            }
            
        except Exception as e:
            print(f"❌ ERROR: Context retrieval failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "context_items": []
            }
    
    async def test_llm_api_with_context(
        self,
        query: str,
        provider: str = "gemini",
        context_items: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Test LLM API call with context.
        
        Args:
            query: User query
            provider: LLM provider (gemini, cerebras)
            context_items: Optional context items from HHNI
        
        Returns:
            LLM API response with context
        """
        print(f"\n🤖 Testing LLM API with Context...")
        print(f"Provider: {provider}")
        print(f"Query: {query}")
        print(f"Context Items: {len(context_items) if context_items else 0}")
        print("=" * 60)
        
        try:
            # Get LLM client
            client = self.api_registry.get_client(provider)
            if not client:
                return {
                    "success": False,
                    "error": f"Provider {provider} not available"
                }
            
            # Prepare messages
            messages = [
                {
                    "role": "user",
                    "content": query
                }
            ]
            
            # Call LLM API with context
            response = await client.chat(
                messages=messages,
                context_items=context_items,
                token_budget=4000 if context_items else None
            )
            
            print(f"\n✅ LLM Response:")
            print(f"   Model: {response.get('model', 'unknown')}")
            print(f"   Tokens Used: {response.get('tokens_used', 0)}")
            print(f"   Provider: {response.get('provider', 'unknown')}")
            print(f"\n📝 Response Content:")
            print(f"   {response.get('content', '')[:500]}...")
            
            return {
                "success": True,
                "response": response,
                "model": response.get("model"),
                "tokens_used": response.get("tokens_used", 0),
                "provider": response.get("provider")
            }
            
        except Exception as e:
            print(f"❌ ERROR: LLM API call failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e)
            }
    
    def test_full_pipeline(self, query: str, provider: str = "gemini") -> Dict[str, Any]:
        """
        Test full pipeline: HHNI retrieval → LLM API call.
        
        Args:
            query: User query
            provider: LLM provider (gemini, cerebras)
        
        Returns:
            Full pipeline test results
        """
        print(f"\n🚀 Testing Full Pipeline...")
        print(f"Query: {query}")
        print(f"Provider: {provider}")
        print("=" * 60)
        
        # Step 1: Retrieve context
        retrieval_result = self.test_context_retrieval(query)
        
        if not retrieval_result["success"]:
            return {
                "success": False,
                "error": "Context retrieval failed",
                "retrieval_result": retrieval_result
            }
        
        # Step 2: Call LLM API with context
        context_items = retrieval_result.get("context_items", [])
        
        # Run async LLM call
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        llm_result = loop.run_until_complete(
            self.test_llm_api_with_context(
                query=query,
                provider=provider,
                context_items=context_items
            )
        )
        
        # Step 3: Validate results
        validation = {
            "context_retrieved": retrieval_result["success"],
            "context_items_count": len(context_items),
            "llm_response_received": llm_result["success"],
            "response_mentions_aimos": "AIM-OS" in llm_result.get("response", {}).get("content", "").upper() if llm_result.get("success") else False
        }
        
        print(f"\n✅ Pipeline Test Complete:")
        print(f"   Context Retrieved: {validation['context_retrieved']}")
        print(f"   Context Items: {validation['context_items_count']}")
        print(f"   LLM Response: {validation['llm_response_received']}")
        print(f"   Mentions AIM-OS: {validation['response_mentions_aimos']}")
        
        return {
            "success": validation["context_retrieved"] and validation["llm_response_received"],
            "validation": validation,
            "retrieval_result": retrieval_result,
            "llm_result": llm_result
        }


def main():
    """Main entry point"""
    print("🧪 LLM API Context Retrieval Tester")
    print("=" * 60)
    print("Testing full pipeline: HHNI → LLM API")
    print("=" * 60)
    
    # Initialize tester
    tester = LLMContextTester()
    
    # Test queries from team consensus
    test_queries = [
        {
            "query": "What is HHNI and how does it work?",
            "provider": "gemini",
            "description": "Basic context retrieval - HHNI system"
        },
        {
            "query": "How does HHNI integrate with CMC?",
            "provider": "gemini",
            "description": "Cross-system context - HHNI ↔ CMC integration"
        },
        {
            "query": "What is the LLM API architecture for context retrieval?",
            "provider": "gemini",
            "description": "LLM API specific query"
        }
    ]
    
    results = []
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n\n{'='*60}")
        print(f"TEST {i}/{len(test_queries)}: {test['description']}")
        print(f"{'='*60}")
        
        result = tester.test_full_pipeline(
            query=test["query"],
            provider=test["provider"]
        )
        
        results.append({
            "test": test,
            "result": result
        })
        
        # Brief pause between tests
        import time
        time.sleep(2)
    
    # Print summary
    print(f"\n\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for r in results if r["result"].get("success"))
    total = len(results)
    
    print(f"\nTests Passed: {passed}/{total}")
    
    for i, result in enumerate(results, 1):
        status = "✅ PASS" if result["result"].get("success") else "❌ FAIL"
        print(f"\n{i}. {result['test']['description']}: {status}")
        if result["result"].get("success"):
            validation = result["result"].get("validation", {})
            print(f"   Context Items: {validation.get('context_items_count', 0)}")
            print(f"   Mentions AIM-OS: {validation.get('response_mentions_aimos', False)}")
        else:
            print(f"   Error: {result['result'].get('error', 'Unknown error')}")
    
    print(f"\n{'='*60}")
    print("✅ Testing complete!")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

