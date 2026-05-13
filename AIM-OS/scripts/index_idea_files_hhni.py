#!/usr/bin/env python3
"""Index idea files using HHNI.

This script indexes all idea files in the ideas/ directory using HHNI's
HierarchicalIndex.index_document() method.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, Any

# Add packages to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "packages"))

from hhni.hierarchical_index import HierarchicalIndex, IndexLevel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

IDEAS_DIR = Path(__file__).parent.parent / "ideas"
INDEX_OUTPUT = Path(__file__).parent.parent / "knowledge_architecture" / "AETHER_MEMORY" / "investigations" / "HHNI_IDEA_INDEX.json"


def read_frontmatter_and_content(file_path: Path) -> tuple[Dict[str, Any], str]:
    """Read frontmatter and content from markdown file."""
    content = file_path.read_text(encoding="utf-8")
    
    # Extract frontmatter if present
    frontmatter = {}
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                import yaml
                frontmatter = yaml.safe_load(parts[1]) or {}
                content = parts[2].strip()
            except Exception as e:
                logger.warning(f"Could not parse frontmatter in {file_path}: {e}")
    
    return frontmatter, content


def index_idea_files():
    """Index all idea files using HHNI."""
    index = HierarchicalIndex()
    indexed_files = []
    
    # Find all markdown files in ideas directory
    idea_files = list(IDEAS_DIR.rglob("*.md"))
    logger.info(f"Found {len(idea_files)} idea files to index")
    
    for file_path in idea_files:
        try:
            # Skip index files
            if file_path.name in ["IDEAS_INDEX.md", "REGISTRY.md", "README.md"]:
                continue
            
            frontmatter, content = read_frontmatter_and_content(file_path)
            
            if not content.strip():
                logger.warning(f"Skipping empty file: {file_path}")
                continue
            
            # Create doc_id from file path
            doc_id = str(file_path.relative_to(IDEAS_DIR.parent)).replace("\\", "/").replace("/", "_").replace(".md", "")
            
            # Prepare metadata
            metadata = {
                "file_path": str(file_path.relative_to(IDEAS_DIR.parent)),
                "file_name": file_path.name,
                **frontmatter
            }
            
            # Index the document
            root_id = index.index_document(content, doc_id=doc_id, metadata=metadata)
            
            indexed_files.append({
                "doc_id": doc_id,
                "file_path": str(file_path.relative_to(IDEAS_DIR.parent)),
                "root_id": root_id,
                "metadata": metadata
            })
            
            logger.info(f"Indexed: {file_path.name} (doc_id: {doc_id})")
            
        except Exception as e:
            logger.error(f"Error indexing {file_path}: {e}")
            continue
    
    # Save index to file
    index_dict = index.to_dict()
    INDEX_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    INDEX_OUTPUT.write_text(json.dumps(index_dict, indent=2), encoding="utf-8")
    
    # Save summary
    summary = {
        "total_files_indexed": len(indexed_files),
        "total_nodes": len(index.nodes),
        "indexed_files": indexed_files
    }
    
    summary_path = INDEX_OUTPUT.parent / "HHNI_IDEA_INDEX_SUMMARY.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    
    logger.info(f"Indexing complete: {len(indexed_files)} files indexed, {len(index.nodes)} nodes created")
    logger.info(f"Index saved to: {INDEX_OUTPUT}")
    logger.info(f"Summary saved to: {summary_path}")
    
    return index, indexed_files


if __name__ == "__main__":
    index, indexed_files = index_idea_files()
    print(f"\nIndexing complete!")
    print(f"   Files indexed: {len(indexed_files)}")
    print(f"   Total nodes: {len(index.nodes)}")
    print(f"   Index saved to: {INDEX_OUTPUT}")

