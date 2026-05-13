#!/usr/bin/env python3
"""
Auto-Update Dependent Docs Script

Standalone script to automatically update documentation files that depend on source files.
Integrates with Organic Data Freshness System.

Usage:
    python scripts/auto_update_dependent_docs.py --source SOURCE_OF_TRUTH.yaml
    python scripts/auto_update_dependent_docs.py --all
    python scripts/auto_update_dependent_docs.py --dry-run
    python scripts/auto_update_dependent_docs.py --check-stale
"""

import sys
import argparse
import yaml
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import dependency tracker and cross-reference generator
try:
    from scripts.track_doc_dependencies import parse_frontmatter, build_dependency_graph
    from scripts.generate_cross_references import CrossReferenceGenerator
except ImportError as e:
    print(f"ERROR: Could not import required modules: {e}")
    print("Make sure scripts/track_doc_dependencies.py and scripts/generate_cross_references.py exist")
    sys.exit(1)


class DocAutoUpdater:
    """Auto-update dependent documentation files"""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.dependency_graph = None
        self.doc_dependencies = None
        self._load_dependencies()
    
    def _load_dependencies(self):
        """Load dependency graph from cross_system_connections.yaml"""
        try:
            _, self.doc_dependencies = build_dependency_graph()
            print(f"[OK] Loaded dependency graph: {len(self.doc_dependencies)} docs tracked")
        except Exception as e:
            print(f"[ERROR] Failed to load dependency graph: {e}")
            self.doc_dependencies = {}
    
    def update_from_source(self, source_path: Path) -> tuple[bool, List[str], List[str]]:
        """
        Update all docs dependent on a source file.
        
        Args:
            source_path: Path to source file
            
        Returns:
            (success, files_updated, errors)
        """
        files_updated = []
        errors = []
        
        # Normalize source path
        try:
            source_path = source_path.resolve()
            source_key = str(source_path.relative_to(project_root)).replace('\\', '/')
        except Exception as e:
            errors.append(f"Invalid source path: {e}")
            return False, files_updated, errors
        
        # Find dependents from dependency graph
        dependents = self._find_dependents(source_key)
        
        if not dependents:
            print(f"[INFO] No dependents found for {source_key}")
            return True, files_updated, errors
        
        print(f"[UPDATE] Found {len(dependents)} dependents of {source_key}")
        
        # Update each dependent
        for dep_path in dependents:
            dep_full_path = project_root / dep_path
            if not dep_full_path.exists():
                errors.append(f"Dependent doc not found: {dep_path}")
                continue
            
            try:
                success = self._update_doc(dep_full_path, source_path)
                if success:
                    files_updated.append(dep_path)
                    if not self.dry_run:
                        print(f"  [DONE] Updated {dep_path}")
                    else:
                        print(f"  [DRY RUN] Would update {dep_path}")
            except Exception as e:
                errors.append(f"Error updating {dep_path}: {e}")
        
        return len(errors) == 0, files_updated, errors
    
    def update_all(self) -> tuple[bool, List[str], List[str]]:
        """
        Update all docs with auto_update: true.
        
        Returns:
            (success, files_updated, errors)
        """
        files_updated = []
        errors = []
        
        # Find all sources that have dependents with auto_update enabled
        sources_to_update = {}
        for doc_path, dep_info in self.doc_dependencies.items():
            source_of_truth = dep_info.get("source_of_truth")
            if source_of_truth:
                source_path = project_root / source_of_truth
                if source_path.exists():
                    if source_of_truth not in sources_to_update:
                        sources_to_update[source_of_truth] = []
                    sources_to_update[source_of_truth].append(doc_path)
        
        print(f"[UPDATE] Found {len(sources_to_update)} sources with auto-update dependents")
        
        # Update each source's dependents
        for source_key, dependents in sources_to_update.items():
            source_path = project_root / source_key
            if not source_path.exists():
                errors.append(f"Source file not found: {source_key}")
                continue
            
            print(f"\n[UPDATE] Processing {source_key} ({len(dependents)} dependents)")
            
            for dep_path in dependents:
                dep_full_path = project_root / dep_path
                if not dep_full_path.exists():
                    errors.append(f"Dependent doc not found: {dep_path}")
                    continue
                
                try:
                    # Check if auto_update enabled
                    content = dep_full_path.read_text(encoding='utf-8')
                    metadata, _ = parse_frontmatter(content)
                    
                    if not metadata.get("auto_update", False):
                        continue  # Skip docs without auto_update flag
                    
                    success = self._update_doc(dep_full_path, source_path)
                    if success:
                        files_updated.append(dep_path)
                        if not self.dry_run:
                            print(f"  [DONE] Updated {dep_path}")
                        else:
                            print(f"  [DRY RUN] Would update {dep_path}")
                except Exception as e:
                    errors.append(f"Error updating {dep_path}: {e}")
        
        return len(errors) == 0, files_updated, errors
    
    def check_stale(self) -> Dict[str, Any]:
        """
        Check for stale docs (outdated compared to sources).
        
        Returns:
            Dictionary with stale doc analysis
        """
        stale_docs = []
        current_docs = []
        
        for doc_path, dep_info in self.doc_dependencies.items():
            source_of_truth = dep_info.get("source_of_truth")
            if not source_of_truth:
                continue
            
            doc_full_path = project_root / doc_path
            source_full_path = project_root / source_of_truth
            
            if not doc_full_path.exists() or not source_full_path.exists():
                continue
            
            try:
                # Check timestamps
                doc_mtime = doc_full_path.stat().st_mtime
                source_mtime = source_full_path.stat().st_mtime
                
                if doc_mtime < source_mtime:
                    # Doc is older than source - potentially stale
                    content = doc_full_path.read_text(encoding='utf-8')
                    metadata, _ = parse_frontmatter(content)
                    
                    if metadata.get("auto_update", False):
                        stale_docs.append({
                            "doc": doc_path,
                            "source": source_of_truth,
                            "doc_mtime": datetime.fromtimestamp(doc_mtime).isoformat(),
                            "source_mtime": datetime.fromtimestamp(source_mtime).isoformat(),
                            "age_days": (source_mtime - doc_mtime) / 86400
                        })
                    else:
                        current_docs.append({
                            "doc": doc_path,
                            "source": source_of_truth,
                            "status": "current (auto_update disabled)"
                        })
                else:
                    current_docs.append({
                        "doc": doc_path,
                        "source": source_of_truth,
                        "status": "current"
                    })
            except Exception as e:
                continue
        
        return {
            "stale_count": len(stale_docs),
            "current_count": len(current_docs),
            "stale_docs": stale_docs,
            "current_docs": current_docs
        }
    
    def _find_dependents(self, source_key: str) -> List[str]:
        """Find all docs that depend on a source file"""
        dependents = []
        
        for doc_path, dep_info in self.doc_dependencies.items():
            if dep_info.get("source_of_truth") == source_key:
                dependents.append(doc_path)
        
        return dependents
    
    def _update_doc(self, doc_path: Path, source_path: Path) -> bool:
        """
        Update a single doc from its source.
        
        Uses CrossReferenceGenerator for consistency.
        """
        try:
            # Determine system name from doc path (for CrossReferenceGenerator)
            system_name = self._guess_system_name(doc_path)
            
            if system_name:
                generator = CrossReferenceGenerator(system_name, dry_run=self.dry_run)
                success, files_updated, errors = generator.auto_update_dependent_docs(source_path)
                return success and doc_path.name in [Path(f).name for f in files_updated]
            else:
                # Fallback: direct update
                return self._direct_update_doc(doc_path, source_path)
        except Exception as e:
            print(f"  [ERROR] Failed to update {doc_path}: {e}")
            return False
    
    def _direct_update_doc(self, doc_path: Path, source_path: Path) -> bool:
        """Direct doc update (fallback method)"""
        try:
            content = doc_path.read_text(encoding='utf-8')
            metadata, body = parse_frontmatter(content)
            
            # Extract facts from source
            facts = self._extract_facts_from_source(source_path, metadata)
            if not facts:
                return False  # No facts to update
            
            # Update doc content
            updated_body = self._apply_facts_to_doc(body, facts, metadata)
            
            # Update metadata timestamp
            metadata["updated"] = datetime.now().isoformat()
            
            # Reconstruct doc
            frontmatter_text = yaml.dump(metadata, default_flow_style=False, allow_unicode=True)
            updated_content = f"---\n{frontmatter_text}---\n{updated_body}"
            
            if not self.dry_run:
                doc_path.write_text(updated_content, encoding='utf-8')
            
            return True
        except Exception as e:
            print(f"  [ERROR] Direct update failed: {e}")
            return False
    
    def _extract_facts_from_source(self, source_path: Path, metadata: Dict) -> Dict[str, Any]:
        """Extract facts from source file"""
        if not source_path.exists():
            return {}
        
        source_type = metadata.get("source_of_truth_type", "doc")
        facts = {}
        
        try:
            if source_type == "code":
                content = source_path.read_text(encoding='utf-8')
                tool_count_match = re.search(r'AIM-OS Tools \((\d+) total\)', content)
                if tool_count_match:
                    facts["mcp_tool_count"] = int(tool_count_match.group(1))
            
            elif source_type == "data":
                content = source_path.read_text(encoding='utf-8')
                try:
                    data = yaml.safe_load(content)
                    if isinstance(data, dict):
                        if "aim_os_source_of_truth" in data:
                            sot = data["aim_os_source_of_truth"]
                            facts["mcp_tools"] = sot.get("mcp_tools", {}).get("count", 0)
                            facts["cursor_commands"] = sot.get("cursor_commands", {}).get("count", 0)
                            facts["systems"] = sot.get("systems", {}).get("count", 0)
                except yaml.YAMLError:
                    pass
            
            elif source_type == "doc":
                content = source_path.read_text(encoding='utf-8')
                count_patterns = [
                    (r'(\d+)\s+tools?', 'tool_count'),
                    (r'(\d+)\s+commands?', 'command_count'),
                    (r'(\d+)\s+systems?', 'system_count'),
                ]
                for pattern, key in count_patterns:
                    match = re.search(pattern, content, re.IGNORECASE)
                    if match:
                        facts[key] = int(match.group(1))
        
        except Exception as e:
            print(f"    [WARNING] Error extracting facts: {e}")
        
        return facts
    
    def _apply_facts_to_doc(self, body: str, facts: Dict[str, Any], metadata: Dict) -> str:
        """Apply extracted facts to doc body"""
        updated_body = body
        
        for key, value in facts.items():
            if key == "mcp_tool_count" or key == "mcp_tools":
                pattern = r'(\d+)\s+(?:MCP\s+)?tools?'
                replacement = f"{value} MCP tools"
                updated_body = re.sub(pattern, replacement, updated_body, flags=re.IGNORECASE)
            
            elif key == "cursor_commands":
                pattern = r'(\d+)\s+(?:Cursor\s+)?commands?'
                replacement = f"{value} Cursor commands"
                updated_body = re.sub(pattern, replacement, updated_body, flags=re.IGNORECASE)
            
            elif key == "systems":
                pattern = r'(\d+)\s+systems?'
                replacement = f"{value} systems"
                updated_body = re.sub(pattern, replacement, updated_body, flags=re.IGNORECASE)
        
        return updated_body
    
    def _guess_system_name(self, doc_path: Path) -> Optional[str]:
        """Guess system name from doc path"""
        path_str = str(doc_path)
        
        # Check if doc is in a system directory
        systems_path = project_root / "knowledge_architecture" / "systems"
        if str(systems_path) in path_str:
            # Extract system name
            relative = doc_path.relative_to(systems_path)
            if len(relative.parts) > 0:
                return relative.parts[0]
        
        return None


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Auto-update dependent documentation files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Update docs dependent on SOURCE_OF_TRUTH.yaml
  python scripts/auto_update_dependent_docs.py --source SOURCE_OF_TRUTH.yaml
  
  # Update all docs with auto_update: true
  python scripts/auto_update_dependent_docs.py --all
  
  # Check for stale docs
  python scripts/auto_update_dependent_docs.py --check-stale
  
  # Dry run (don't modify files)
  python scripts/auto_update_dependent_docs.py --all --dry-run
        """
    )
    
    parser.add_argument("--source", type=Path, help="Source file to update dependents for")
    parser.add_argument("--all", action="store_true", help="Update all docs with auto_update: true")
    parser.add_argument("--check-stale", action="store_true", help="Check for stale docs")
    parser.add_argument("--dry-run", action="store_true", help="Dry run (don't modify files)")
    
    args = parser.parse_args()
    
    if not any([args.source, args.all, args.check_stale]):
        parser.print_help()
        sys.exit(1)
    
    updater = DocAutoUpdater(dry_run=args.dry_run)
    
    if args.check_stale:
        print("\n[CHECK] Checking for stale docs...\n")
        result = updater.check_stale()
        
        print(f"Stale Docs: {result['stale_count']}")
        print(f"Current Docs: {result['current_count']}\n")
        
        if result['stale_docs']:
            print("STALE DOCS:")
            for stale in result['stale_docs']:
                print(f"  - {stale['doc']}")
                print(f"    Source: {stale['source']}")
                print(f"    Age: {stale['age_days']:.1f} days")
                print()
        
        sys.exit(0 if result['stale_count'] == 0 else 1)
    
    elif args.source:
        source_path = Path(args.source)
        if not source_path.is_absolute():
            source_path = project_root / source_path
        
        print(f"\n[UPDATE] Updating docs dependent on {source_path}\n")
        success, files_updated, errors = updater.update_from_source(source_path)
        
        print(f"\n[RESULT] {'SUCCESS' if success else 'FAILED'}")
        print(f"  Files updated: {len(files_updated)}")
        if errors:
            print(f"  Errors: {len(errors)}")
            for error in errors:
                print(f"    - {error}")
        
        sys.exit(0 if success else 1)
    
    elif args.all:
        print(f"\n[UPDATE] Updating all docs with auto_update: true\n")
        success, files_updated, errors = updater.update_all()
        
        print(f"\n[RESULT] {'SUCCESS' if success else 'FAILED'}")
        print(f"  Files updated: {len(files_updated)}")
        if errors:
            print(f"  Errors: {len(errors)}")
            for error in errors:
                print(f"    - {error}")
        
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

