#!/usr/bin/env python3
"""
Index Organized Floating Files with HHNI
Indexes all organized floating files in knowledge_architecture/FLOATING_FILES_ORGANIZED/,
organized_root_files/, and documentation_standards/PERFECT_STANDARDS/
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from packages.hhni.hierarchical_index import HierarchicalIndex

def extract_frontmatter(content: str) -> tuple[Dict[str, Any], str]:
    """Extract frontmatter metadata from markdown file."""
    metadata = {}
    body = content
    
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter_text = parts[1].strip()
            body = parts[2].strip()
            
            # Parse frontmatter (simple YAML-like parsing)
            for line in frontmatter_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    metadata[key] = value
    
    return metadata, body

def index_organized_files():
    """Index all organized floating files."""
    print("[*] Starting HHNI indexing of organized floating files...")
    print("=" * 70)
    
    # Initialize HHNI
    index = HierarchicalIndex()
    
    # Directories to index
    directories = [
        {
            'path': Path('knowledge_architecture/FLOATING_FILES_ORGANIZED'),
            'name': 'Knowledge Architecture Floating Files',
            'prefix': 'ka_float_'
        },
        {
            'path': Path('organized_root_files'),
            'name': 'Root Directory Organized Files',
            'prefix': 'root_org_'
        },
        {
            'path': Path('knowledge_architecture/documentation_standards/PERFECT_STANDARDS'),
            'name': 'Perfect Standards',
            'prefix': 'perfect_std_'
        }
    ]
    
    indexed_files = []
    total_nodes = 0
    
    for dir_info in directories:
        dir_path = dir_info['path']
        dir_name = dir_info['name']
        prefix = dir_info['prefix']
        
        if not dir_path.exists():
            print(f"[!] Directory not found: {dir_path}")
            continue
        
        print(f"\n[>] Indexing {dir_name}...")
        print(f"   Path: {dir_path}")
        
        # Find all markdown files recursively
        md_files = list(dir_path.rglob('*.md'))
        print(f"   Found {len(md_files)} markdown files")
        
        for file_path in md_files:
            try:
                # Read file
                content = file_path.read_text(encoding='utf-8')
                
                # Extract metadata
                metadata, body = extract_frontmatter(content)
                
                # Create doc_id using absolute path then making relative
                try:
                    relative_path = str(file_path.relative_to(Path.cwd()))
                except ValueError:
                    # Fallback: use absolute path converted to relative format
                    cwd_parts = Path.cwd().parts
                    file_parts = file_path.parts
                    # Find common prefix
                    common_len = 0
                    for i in range(min(len(cwd_parts), len(file_parts))):
                        if cwd_parts[i] == file_parts[i]:
                            common_len += 1
                        else:
                            break
                    # Get relative parts
                    relative_parts = file_parts[common_len:]
                    relative_path = '/'.join(relative_parts)
                
                doc_id = f"{prefix}{relative_path.replace('/', '_').replace('\\', '_')}"
                
                # Enhanced metadata
                enhanced_metadata = {
                    'file_path': relative_path,
                    'directory': dir_name,
                    'category': file_path.parent.name,
                    'file_name': file_path.name,
                    'indexed_at': datetime.now().isoformat(),
                    **metadata
                }
                
                # Index document - use absolute path for file_path in metadata
                root_id = index.index_document(
                    content=body,
                    doc_id=doc_id,
                    metadata=enhanced_metadata
                )
                
                # Count nodes created for this document (approx: 1 root + sections + paragraphs + sentences)
                # We'll count from the index structure
                nodes_created = 0
                for node_id, node in index.nodes.items():
                    if node.metadata.get('doc_id') == doc_id:
                        nodes_created += 1
                
                indexed_files.append({
                    'doc_id': doc_id,
                    'file_path': relative_path,
                    'directory': dir_name,
                    'category': file_path.parent.name,
                    'nodes_created': nodes_created,
                    'metadata': enhanced_metadata
                })
                
                total_nodes += nodes_created
                
                print(f"   [+] Indexed: {file_path.name} ({nodes_created} nodes)")
                
            except Exception as e:
                print(f"   [-] Error indexing {file_path.name}: {e}")
                continue
    
    print("\n" + "=" * 70)
    print(f"[+] Indexing complete!")
    print(f"   Files indexed: {len(indexed_files)}")
    print(f"   Total nodes created: {len(index.nodes):,}")
    
    # Save index
    index_path = Path('HHNI_FLOATING_FILES_INDEX.json')
    print(f"\n[*] Saving index to {index_path}...")
    
    index_data = {
        'indexed_at': datetime.now().isoformat(),
        'total_files': len(indexed_files),
        'total_nodes': total_nodes,
        'files': indexed_files
    }
    
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)
    
    print(f"[+] Index saved to {index_path}")
    
    # Save summary
    summary_path = Path('HHNI_FLOATING_FILES_INDEX_SUMMARY.json')
    print(f"\n[*] Saving summary to {summary_path}...")
    
    summary = {
        'indexed_at': datetime.now().isoformat(),
        'total_files': len(indexed_files),
        'total_nodes': len(index.nodes),
        'files_by_directory': {},
        'files_by_category': {}
    }
    
    for file_info in indexed_files:
        dir_name = file_info['directory']
        category = file_info['category']
        
        if dir_name not in summary['files_by_directory']:
            summary['files_by_directory'][dir_name] = 0
        summary['files_by_directory'][dir_name] += 1
        
        if category not in summary['files_by_category']:
            summary['files_by_category'][category] = 0
        summary['files_by_category'][category] += 1
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"[+] Summary saved to {summary_path}")
    
    # Print summary
    print("\n" + "=" * 70)
    print("[*] INDEXING SUMMARY")
    print("=" * 70)
    print(f"Total files indexed: {len(indexed_files)}")
    print(f"Total nodes created: {len(index.nodes):,}")
    print(f"\nFiles by directory:")
    for dir_name, count in summary['files_by_directory'].items():
        print(f"  {dir_name}: {count} files")
    print(f"\nFiles by category:")
    for category, count in sorted(summary['files_by_category'].items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {category}: {count} files")
    if len(summary['files_by_category']) > 10:
        print(f"  ... and {len(summary['files_by_category']) - 10} more categories")
    
    return index, indexed_files, len(index.nodes)

if __name__ == '__main__':
    try:
        index, indexed_files, total_nodes = index_organized_files()
        print("\n[+] HHNI indexing of organized floating files complete!")
        sys.exit(0)
    except Exception as e:
        print(f"\n[-] Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
