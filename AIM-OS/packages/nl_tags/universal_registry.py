"""
Universal Tag Registry - Cross-System NL Tag Tracking

Central registry for all NL tags across the entire AIM-OS codebase.
Enables cross-system awareness, querying, validation, and propagation.

Features:
- Register tags from any system
- Query by system, category, type, file, line
- Find dependencies and dependents
- Scan codebase for all tags
- Export/import for persistence
- Validate tag uniqueness

Usage:
    # Create registry
    registry = UniversalTagRegistry()
    
    # Scan codebase
    count = registry.scan_codebase("packages/")
    print(f"Registered {count} tags")
    
    # Query tags
    vif_tags = registry.query(system="vif")
    connect_tags = registry.query(tag_type="CONNECT")
    
    # Export
    registry.export("tag_registry.json")
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field
from collections import defaultdict

# Import NLTag if available
try:
    from packages.nl_tags.models import NLTag, NLTagKind
except ImportError:
    print("Warning: packages.nl_tags.models not available")
    NLTag = None
    NLTagKind = None


@dataclass
class TagReference:
    """Reference to where a tag is used"""
    file_path: str
    line_number: int
    context: str  # Surrounding code context
    reference_type: str  # "definition", "dependency", "mention"


@dataclass
class TagStatistics:
    """Statistics about tags in the registry"""
    total_tags: int
    by_system: Dict[str, int]
    by_category: Dict[str, int]
    by_type: Dict[str, int]
    by_file: Dict[str, int]
    orphaned_tags: List[str]  # Tags with no references
    broken_dependencies: List[Tuple[str, str]]  # (tag_id, missing_dep)


class UniversalTagRegistry:
    """Central registry for all NL tags across codebase"""
    
    def __init__(self):
        # Core storage
        self.tags: Dict[str, Any] = {}  # tag_id -> tag data
        
        # Indexes for fast lookup
        self.by_system: Dict[str, Set[str]] = defaultdict(set)
        self.by_category: Dict[str, Set[str]] = defaultdict(set)
        self.by_type: Dict[str, Set[str]] = defaultdict(set)
        self.by_file: Dict[str, Set[str]] = defaultdict(set)
        
        # References
        self.references: Dict[str, List[TagReference]] = defaultdict(list)
        
        # Dependency tracking
        self.dependencies: Dict[str, Set[str]] = defaultdict(set)  # tag_id -> dep_ids
        self.dependents: Dict[str, Set[str]] = defaultdict(set)  # tag_id -> dependent_ids
    
    def register(self, tag_id: str, tag_data: Dict[str, Any]) -> None:
        """Register a tag in the universal registry
        
        Args:
            tag_id: Unique tag identifier (e.g., "VIF-WITNESS-001")
            tag_data: Tag data dictionary
        """
        self.tags[tag_id] = tag_data
        
        # Extract system (e.g., "VIF" from "VIF-WITNESS-001")
        parts = tag_id.split("-")
        if len(parts) >= 2:
            system = parts[0]
            category = parts[1] if len(parts) > 1 else "UNKNOWN"
            
            self.by_system[system].add(tag_id)
            self.by_category[category].add(tag_id)
        
        # Index by type
        tag_type = tag_data.get("kind", "TAG")
        self.by_type[tag_type].add(tag_id)
        
        # Index by file
        file_path = tag_data.get("file_path")
        if file_path:
            self.by_file[file_path].add(tag_id)
        
        # Track dependencies
        deps = tag_data.get("dependencies", [])
        if deps:
            self.dependencies[tag_id] = set(deps)
            for dep_id in deps:
                self.dependents[dep_id].add(tag_id)
    
    def get(self, tag_id: str) -> Optional[Dict[str, Any]]:
        """Get tag by ID"""
        return self.tags.get(tag_id)
    
    def query(
        self,
        system: Optional[str] = None,
        category: Optional[str] = None,
        tag_type: Optional[str] = None,
        file_path: Optional[str] = None
    ) -> List[str]:
        """Query tags with filters
        
        Returns list of matching tag IDs.
        Multiple filters are AND'd together.
        """
        # Start with all tags
        result = set(self.tags.keys())
        
        # Apply filters
        if system:
            result &= self.by_system.get(system, set())
        if category:
            result &= self.by_category.get(category, set())
        if tag_type:
            result &= self.by_type.get(tag_type, set())
        if file_path:
            result &= self.by_file.get(file_path, set())
        
        return list(result)
    
    def find_dependencies(self, tag_id: str) -> List[str]:
        """Find all tags this tag depends on"""
        return list(self.dependencies.get(tag_id, set()))
    
    def find_dependents(self, tag_id: str) -> List[str]:
        """Find all tags that depend on this tag"""
        return list(self.dependents.get(tag_id, set()))
    
    def add_reference(self, tag_id: str, ref: TagReference) -> None:
        """Add a reference to where tag is used"""
        self.references[tag_id].append(ref)
    
    def get_references(self, tag_id: str) -> List[TagReference]:
        """Get all references for a tag"""
        return self.references.get(tag_id, [])
    
    def scan_file(self, file_path: str) -> int:
        """Scan a file for NL tags and register them
        
        Returns number of tags found.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            count = 0
            
            # Regex for NL tags  
            # Format: # NL_TAG[_KIND]: TAG-ID | description | syntax | [deps]
            tag_pattern = r'#\s*NL_TAG(?:_(\w+))?\s*:\s*([A-Z]+-[A-Z0-9]+-\d+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*\[([^\]]*)\]'
            
            for i, line in enumerate(lines, 1):
                match = re.search(tag_pattern, line)
                if match:
                    tag_kind = match.group(1) or "TAG"
                    tag_id = match.group(2)
                    description = match.group(3).strip()
                    syntax_ref = match.group(4).strip()
                    deps_str = match.group(5).strip()
                    
                    # Parse dependencies
                    deps = []
                    if deps_str:
                        deps = [d.strip() for d in deps_str.split(',') if d.strip()]
                    
                    # Register tag
                    tag_data = {
                        "id": tag_id,
                        "kind": tag_kind,
                        "description": description,
                        "syntax_ref": syntax_ref,
                        "dependencies": deps,
                        "file_path": file_path,
                        "line_number": i
                    }
                    
                    self.register(tag_id, tag_data)
                    count += 1
            
            return count
        
        except Exception as e:
            print(f"Error scanning {file_path}: {e}")
            return 0
    
    def scan_codebase(self, root_dir: str, pattern: str = "**/*_TAGGED.py") -> int:
        """Scan entire codebase for tags
        
        Args:
            root_dir: Root directory to scan
            pattern: Glob pattern for files to scan
            
        Returns:
            Total number of tags registered
        """
        root_path = Path(root_dir)
        count = 0
        
        for file_path in root_path.glob(pattern):
            if file_path.is_file():
                count += self.scan_file(str(file_path))
        
        return count
    
    def export(self, output_path: str) -> None:
        """Export registry to JSON"""
        data = {
            "tags": self.tags,
            "by_system": {k: list(v) for k, v in self.by_system.items()},
            "by_category": {k: list(v) for k, v in self.by_category.items()},
            "by_type": {k: list(v) for k, v in self.by_type.items()},
            "by_file": {k: list(v) for k, v in self.by_file.items()},
            "dependencies": {k: list(v) for k, v in self.dependencies.items()},
            "dependents": {k: list(v) for k, v in self.dependents.items()},
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def import_from(self, input_path: str) -> None:
        """Import registry from JSON"""
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.tags = data.get("tags", {})
        self.by_system = {k: set(v) for k, v in data.get("by_system", {}).items()}
        self.by_category = {k: set(v) for k, v in data.get("by_category", {}).items()}
        self.by_type = {k: set(v) for k, v in data.get("by_type", {}).items()}
        self.by_file = {k: set(v) for k, v in data.get("by_file", {}).items()}
        self.dependencies = {k: set(v) for k, v in data.get("dependencies", {}).items()}
        self.dependents = {k: set(v) for k, v in data.get("dependents", {}).items()}
    
    def get_statistics(self) -> TagStatistics:
        """Get comprehensive statistics about registered tags"""
        # Find orphaned tags (no references except definition)
        orphaned = []
        for tag_id in self.tags:
            refs = self.references.get(tag_id, [])
            definition_refs = [r for r in refs if r.reference_type == "definition"]
            other_refs = [r for r in refs if r.reference_type != "definition"]
            
            if len(definition_refs) > 0 and len(other_refs) == 0:
                orphaned.append(tag_id)
        
        # Find broken dependencies
        broken = []
        for tag_id, deps in self.dependencies.items():
            for dep_id in deps:
                if dep_id not in self.tags:
                    broken.append((tag_id, dep_id))
        
        return TagStatistics(
            total_tags=len(self.tags),
            by_system={k: len(v) for k, v in self.by_system.items()},
            by_category={k: len(v) for k, v in self.by_category.items()},
            by_type={k: len(v) for k, v in self.by_type.items()},
            by_file={k: len(v) for k, v in self.by_file.items()},
            orphaned_tags=orphaned,
            broken_dependencies=broken
        )
    
    def validate(self) -> List[str]:
        """Validate registry for issues
        
        Returns list of validation errors.
        """
        errors = []
        
        # Check for duplicate IDs
        seen_ids = set()
        for tag_id in self.tags:
            if tag_id in seen_ids:
                errors.append(f"Duplicate tag ID: {tag_id}")
            seen_ids.add(tag_id)
        
        # Check for missing dependencies
        for tag_id, deps in self.dependencies.items():
            for dep_id in deps:
                if dep_id not in self.tags and not dep_id.startswith("ADR-") and not dep_id.endswith(".json"):
                    errors.append(f"Tag {tag_id} depends on missing tag: {dep_id}")
        
        return errors
    
    def count(self) -> int:
        """Get total number of registered tags"""
        return len(self.tags)
    
    def clear(self) -> None:
        """Clear all registered tags"""
        self.tags.clear()
        self.by_system.clear()
        self.by_category.clear()
        self.by_type.clear()
        self.by_file.clear()
        self.references.clear()
        self.dependencies.clear()
        self.dependents.clear()

