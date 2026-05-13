#!/usr/bin/env python3
"""
Cross-Reference Generator

Generates missing cross-references across all L/T-level documentation using system maps, indexes, and cross-system connections.
Integrates with Documentation Governance & Cross-Reference Protocol.

Usage:
    python scripts/generate_cross_references.py --system cmc
    python scripts/generate_cross_references.py --core-systems
    python scripts/generate_cross_references.py --all
    python scripts/generate_cross_references.py --dry-run
"""

import sys
import json
import yaml
import json5
import argparse
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from dataclasses import dataclass, asdict


# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import dependency tracker functions
try:
    from scripts.track_doc_dependencies import parse_frontmatter, extract_dependencies, build_dependency_graph
except ImportError:
    # Fallback if import fails
    def parse_frontmatter(content: str):
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
        if not match:
            return {}, content
        try:
            metadata = yaml.safe_load(match.group(1)) or {}
            return metadata, match.group(2)
        except yaml.YAMLError:
            return {}, content


# External systems (not AIM-OS systems, so we skip them)
EXTERNAL_SYSTEMS = {
    "storage", "vector", "graph", "embedding", "audit", "ci", "llm",
    "storage.external", "vector.faiss", "graph.neo4j", "daemon.ragsystem"
}

# System hierarchy (for layer classification)
SYSTEM_HIERARCHY = {
    # Layer 1: Memory & Knowledge Foundation
    "layer1": ["cmc", "seg"],
    # Layer 2: Intelligence Processing
    "layer2": ["hhni", "vif", "sdfcvf"],
    # Layer 3: Orchestration & Planning
    "layer3": ["apoe"],
    # Layer 4: Consciousness Engine
    "layer4": ["cognitive_analysis", "timeline_context_system", "intuitive_intelligence_system"]
}

@dataclass
class CrossReferenceGenerationResult:
    """Cross-reference generation result"""
    system_name: str
    generation_date: str
    related_systems_section_generated: bool
    doc_links_added_to_map: bool
    system_index_updated: bool
    cross_system_yaml_updated: bool
    overall_success: bool
    files_updated: List[str]
    sections_generated: List[str]
    errors: List[str]

class CrossReferenceGenerator:
    """Generates missing cross-references"""
    
    def __init__(self, system_name: str, dry_run: bool = False):
        self.system_name = system_name
        self.system_path = project_root / "knowledge_architecture" / "systems" / system_name
        self.dry_run = dry_run
        
        # Load system resources
        self.system_map = self._load_system_map()
        self.system_index = self._load_system_index()
        self.cross_system_connections = self._load_cross_system_connections()
        
    def generate(self) -> CrossReferenceGenerationResult:
        """Run complete cross-reference generation"""
        dry_run_label = " (DRY RUN)" if self.dry_run else ""
        print(f"Generating cross-references for {self.system_name}{dry_run_label}...")
        
        files_updated = []
        sections_generated = []
        errors = []
        
        # Step 1: Generate Related Systems section
        related_systems_generated, gen1_files, gen1_sections, gen1_errors = self._generate_related_systems_section()
        files_updated.extend(gen1_files)
        sections_generated.extend(gen1_sections)
        errors.extend(gen1_errors)
        
        # Step 2: Add doc links to system map
        doc_links_added, gen2_files, gen2_errors = self._add_doc_links_to_system_map()
        files_updated.extend(gen2_files)
        errors.extend(gen2_errors)
        
        # Step 3: Update system index
        system_index_updated, gen3_files, gen3_errors = self._update_system_index()
        files_updated.extend(gen3_files)
        errors.extend(gen3_errors)
        
        # Step 4: Update cross-system connections YAML
        yaml_updated, gen4_files, gen4_errors = self._update_cross_system_yaml()
        files_updated.extend(gen4_files)
        errors.extend(gen4_errors)
        
        # Overall success
        overall_success = len(errors) == 0
        
        result = CrossReferenceGenerationResult(
            system_name=self.system_name,
            generation_date=datetime.now().isoformat(),
            related_systems_section_generated=related_systems_generated,
            doc_links_added_to_map=doc_links_added,
            system_index_updated=system_index_updated,
            cross_system_yaml_updated=yaml_updated,
            overall_success=overall_success,
            files_updated=files_updated,
            sections_generated=sections_generated,
            errors=errors
        )
        
        return result
    
    def _generate_related_systems_section(self) -> tuple[bool, List[str], List[str], List[str]]:
        """Generate Related Systems section in T2 architecture"""
        files_updated = []
        sections_generated = []
        errors = []
        
        # Load T2 doc
        t2_path = self.system_path / "T2_architecture.md"
        if not t2_path.exists():
            errors.append(f"T2 architecture not found: {t2_path}")
            return False, files_updated, sections_generated, errors
        
        content = t2_path.read_text(encoding="utf-8")
        
        # Check if Related Systems section already exists
        # If it exists but doesn't have "Systems That Depend On Us", replace it
        has_section = "## Related Systems" in content or "## 🔗 RELATED SYSTEMS" in content or "## RELATED SYSTEMS" in content
        has_dependents_subsection = "### **Systems That Depend On Us**" in content
        
        if has_section and has_dependents_subsection:
            print(f"  [OK] Related Systems section already has hybrid structure")
            return True, files_updated, sections_generated, errors
        
        # Need to replace old section with new hybrid section
        if has_section:
            print(f"  [UPDATE] Upgrading Related Systems section to hybrid structure")
        
        # Generate section from system map
        if not self.system_map:
            errors.append(f"System map not found for {self.system_name}")
            return False, files_updated, sections_generated, errors
        
        section = self._build_related_systems_section()
        sections_generated.append("Related Systems section (hybrid)")
        
        # Replace existing section or add new one
        if has_section:
            # Find and replace existing Related Systems section
            import re
            # Match from "## Related Systems" or "## 🔗 RELATED SYSTEMS" to next ## or end
            pattern = r'## (?:🔗 )?RELATED SYSTEMS.*?(?=\n## |\Z)'
            replacement = section.rstrip()
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        else:
            # Add section before references
            if "## REFERENCES" in content:
                content = content.replace("## REFERENCES", f"{section}\n\n---\n\n## REFERENCES")
            else:
                content += f"\n\n---\n\n{section}"
        
        # Save updated T2 doc
        if not self.dry_run:
            t2_path.write_text(content, encoding="utf-8")
            files_updated.append(str(t2_path))
            print(f"  [DONE] Added Related Systems section to T2 architecture")
        else:
            print(f"  [DRY RUN] Would add Related Systems section to T2 architecture")
        
        return True, files_updated, sections_generated, errors
    
    def _build_related_systems_section(self) -> str:
        """Build Related Systems section content with hybrid approach"""
        section = "## 🔗 RELATED SYSTEMS\n\n"
        
        # Part 1: Systems We Depend On (from ports)
        section += "### **Systems We Depend On**\n\n"
        
        # Extract related systems from ports
        related_systems = {}
        external_systems = []
        for port in self.system_map.get("ports", []):
            if "connectsToSystem" in port:
                system_id = port["connectsToSystem"]
                system_name = system_id.split(".")[0]
                
                # Check if external
                if system_name in EXTERNAL_SYSTEMS or system_id in EXTERNAL_SYSTEMS:
                    external_systems.append(system_name)
                    continue
                
                if system_name not in related_systems:
                    related_systems[system_name] = {
                        "relationship": port.get("direction", "bidirectional"),
                        "integration_point": port.get("portId", ""),
                        "data_exchanged": port.get("whatIsExchanged", []),
                        "security_level": port.get("security_level", "medium")
                    }
        
        # Generate subsections for each related system
        for system_name, details in sorted(related_systems.items()):
            section += f"#### **{system_name.upper()}**\n"
            section += f"**Relationship:** {details['relationship']}\n"
            section += f"**Integration Point:** {details['integration_point']}\n"
            
            if details['data_exchanged']:
                data_preview = ', '.join(details['data_exchanged'][:3])
                if len(details['data_exchanged']) > 3:
                    data_preview += f" (+ {len(details['data_exchanged']) - 3} more)"
                section += f"**Data Exchanged:** {data_preview}\n"
            
            section += f"**Security Level:** {details['security_level']}\n"
            section += f"**Docs:** `knowledge_architecture/systems/{system_name}/T0_executive.md`\n\n"
        
        # Part 2: Systems That Depend On Us (find by scanning all T2 docs)
        section += "\n### **Systems That Depend On Us**\n\n"
        dependent_systems = self._find_dependent_systems()
        
        if dependent_systems:
            # Group by layer
            by_layer = {}
            for dep_system in dependent_systems:
                layer = self._get_system_layer(dep_system)
                if layer not in by_layer:
                    by_layer[layer] = []
                by_layer[layer].append(dep_system)
            
            # Generate by layer
            layer_names = {5: "Layer 5 (Infrastructure)", 6: "Layer 6 (Application)", 0: "Other Systems"}
            for layer in sorted(by_layer.keys()):
                layer_name = layer_names.get(layer, f"Layer {layer}")
                systems_list = ', '.join(sorted(by_layer[layer]))
                section += f"**{layer_name}:** {systems_list}\n\n"
            
            section += f"**Total Dependent Systems:** {len(dependent_systems)}\n\n"
        else:
            section += "*No dependent systems found*\n\n"
        
        # External systems note
        if external_systems:
            section += "### **External Systems**\n\n"
            section += f"**External Dependencies:** {', '.join(sorted(set(external_systems)))}\n\n"
        
        section += "**Integration Details:** See system map (`system.map.lucid.json5`) for complete integration topology.\n"
        
        return section
    
    def _find_dependent_systems(self) -> List[str]:
        """Find all systems that depend on this system by scanning T2 docs"""
        dependent_systems = []
        systems_path = project_root / "knowledge_architecture" / "systems"
        
        # Scan all systems
        for system_dir in systems_path.iterdir():
            if not system_dir.is_dir():
                continue
            
            system_name = system_dir.name
            
            # Skip self
            if system_name == self.system_name:
                continue
            
            # Check if T2 doc exists
            t2_path = system_dir / "T2_architecture.md"
            if not t2_path.exists():
                continue
            
            # Check if T2 doc references this system
            try:
                content = t2_path.read_text(encoding="utf-8")
                
                # Simple check: does content mention our system name?
                # (More sophisticated extraction would be better, but this works)
                system_patterns = [
                    self.system_name.upper(),
                    self.system_name.lower(),
                    self.system_name.title(),
                    self.system_name.replace("_", "-"),
                    self.system_name.replace("_", " ").title()
                ]
                
                for pattern in system_patterns:
                    if pattern in content:
                        dependent_systems.append(system_name)
                        break
            except Exception as e:
                continue  # Skip if can't read
        
        return sorted(set(dependent_systems))
    
    def _get_system_layer(self, system_name: str) -> int:
        """Get system layer from hierarchy"""
        for layer_num, (layer_key, systems) in enumerate(SYSTEM_HIERARCHY.items(), start=1):
            if system_name in systems:
                return layer_num
        
        # Guess layer based on system characteristics
        # Layer 5 systems (infrastructure supporting consciousness)
        layer5_keywords = ["monitoring", "intelligence", "integration", "protocol", "enhancement", "mcp", "rag", "daemon", "tools"]
        for keyword in layer5_keywords:
            if keyword in system_name:
                return 5
        
        # Layer 6 systems (applications)
        layer6_keywords = ["app", "console", "mobile", "editor", "icip", "ui", "agent"]
        for keyword in layer6_keywords:
            if keyword in system_name:
                return 6
        
        return 0  # Unknown layer
    
    def _add_doc_links_to_system_map(self) -> tuple[bool, List[str], List[str]]:
        """Add documentation links to system map"""
        files_updated = []
        errors = []
        
        if not self.system_map:
            errors.append(f"System map not found for {self.system_name}")
            return False, files_updated, errors
        
        # Find existing T-level docs
        existing_docs = {}
        for level in ["T0", "T1", "T2", "T3", "T4", "T5", "T6"]:
            doc_path = self.system_path / f"{level}_{self._get_doc_type_for_level(level)}.md"
            if doc_path.exists():
                existing_docs[level] = f"knowledge_architecture/systems/{self.system_name}/{doc_path.name}"
        
        if not existing_docs:
            print(f"  [WARNING] No T-level docs found for {self.system_name}")
            return True, files_updated, errors
        
        # Add documentation section if missing
        if "documentation" not in self.system_map:
            self.system_map["documentation"] = {}
        
        # Add doc links
        links_added = 0
        for level, path in existing_docs.items():
            if level not in self.system_map["documentation"]:
                self.system_map["documentation"][level] = path
                links_added += 1
        
        if links_added > 0:
            # Save updated system map
            system_map_path = self.system_path / "system.map.lucid.json5"
            if not self.dry_run:
                with open(system_map_path, "w", encoding="utf-8") as f:
                    json5.dump(self.system_map, f, indent=2)
                files_updated.append(str(system_map_path))
                print(f"  [DONE] Added {links_added} doc links to system map")
            else:
                print(f"  [DRY RUN] Would add {links_added} doc links to system map")
        else:
            print(f"  [OK] System map already has all doc links")
        
        return True, files_updated, errors
    
    def _update_system_index(self) -> tuple[bool, List[str], List[str]]:
        """Update system index with map link"""
        files_updated = []
        errors = []
        
        if not self.system_index:
            print(f"  [WARNING] System index not found for {self.system_name}")
            return True, files_updated, errors  # Not critical
        
        # Check if system map link exists
        if "systemMap" in self.system_index:
            print(f"  [OK] System index already has system map link")
            return True, files_updated, errors
        
        # Add system map link
        self.system_index["systemMap"] = {
            "mapFile": "./system.map.lucid.json5"
        }
        
        # Save updated system index
        system_index_path = self.system_path / "system.index.lucid.json5"
        if not self.dry_run:
            with open(system_index_path, "w", encoding="utf-8") as f:
                json5.dump(self.system_index, f, indent=2)
            files_updated.append(str(system_index_path))
            print(f"  [DONE] Added system map link to system index")
        else:
            print(f"  [DRY RUN] Would add system map link to system index")
        
        return True, files_updated, errors
    
    def _update_cross_system_yaml(self) -> tuple[bool, List[str], List[str]]:
        """Update cross-system connections YAML with doc references"""
        files_updated = []
        errors = []
        
        if not self.cross_system_connections:
            print(f"  [WARNING] Cross-system connections YAML not found")
            return True, files_updated, errors  # Not critical
        
        # Find system in YAML
        system_key = self.system_name.upper()
        if system_key not in self.cross_system_connections.get("systems", {}):
            print(f"  [WARNING] System '{self.system_name}' not found in cross-system connections YAML")
            return True, files_updated, errors  # Not critical
        
        system_data = self.cross_system_connections["systems"][system_key]
        
        # Check if docs field exists
        if "docs" in system_data:
            print(f"  [OK] Cross-system connections YAML already has docs reference")
            return True, files_updated, errors
        
        # Add docs field
        system_data["docs"] = f"knowledge_architecture/systems/{self.system_name}/"
        
        # Save updated YAML
        yaml_path = project_root / "knowledge_architecture" / "NAVIGATION" / "cross_system_connections.yaml"
        if not self.dry_run:
            with open(yaml_path, "w", encoding="utf-8") as f:
                yaml.dump(self.cross_system_connections, f, default_flow_style=False, allow_unicode=True)
            files_updated.append(str(yaml_path))
            print(f"  [DONE] Added docs reference to cross-system connections YAML")
        else:
            print(f"  [DRY RUN] Would add docs reference to cross-system connections YAML")
        
        return True, files_updated, errors
    
    def _get_doc_type_for_level(self, level: str) -> str:
        """Get document type for level"""
        types = {
            "T0": "executive",
            "T1": "overview",
            "T2": "architecture",
            "T3": "detailed",
            "T4": "complete",
            "T5": "deep_dive",
            "T6": "academic"
        }
        return types.get(level, "unknown")
    
    def _load_system_map(self) -> Optional[Dict]:
        """Load system map"""
        system_map_path = self.system_path / "system.map.lucid.json5"
        if not system_map_path.exists():
            return None
        
        try:
            with open(system_map_path, "r", encoding="utf-8") as f:
                return json5.load(f)
        except Exception as e:
            print(f"WARNING: Could not load system map: {e}", file=sys.stderr)
            return None
    
    def _load_system_index(self) -> Optional[Dict]:
        """Load system index"""
        system_index_path = self.system_path / "system.index.lucid.json5"
        if not system_index_path.exists():
            return None
        
        try:
            with open(system_index_path, "r", encoding="utf-8") as f:
                return json5.load(f)
        except Exception as e:
            print(f"WARNING: Could not load system index: {e}", file=sys.stderr)
            return None
    
    def auto_update_dependent_docs(self, source_path: Optional[Path] = None) -> tuple[bool, List[str], List[str]]:
        """
        Auto-update docs that depend on a source file.
        
        If source_path is provided, updates only docs dependent on that source.
        Otherwise, updates all docs that have auto_update: true in metadata.
        """
        files_updated = []
        errors = []
        
        # Load dependency graph from cross_system_connections.yaml
        dependency_info = self._load_doc_dependencies()
        if not dependency_info:
            print(f"  [WARNING] Could not load doc dependencies")
            return False, files_updated, errors
        
        # Determine which sources to update
        if source_path:
            # Update dependents of specific source
            source_key = str(source_path.relative_to(project_root)).replace('\\', '/')
            sources_to_update = {source_key: dependency_info.get(source_key, {})}
        else:
            # Update all sources that have dependents with auto_update: true
            sources_to_update = {}
            for source, info in dependency_info.items():
                dependents = info.get("dependents", [])
                # Check if any dependents have auto_update: true
                for dep_path in dependents:
                    dep_full_path = project_root / dep_path
                    if dep_full_path.exists():
                        try:
                            content = dep_full_path.read_text(encoding='utf-8')
                            metadata, _ = parse_frontmatter(content)
                            if metadata.get("auto_update", False):
                                if source not in sources_to_update:
                                    sources_to_update[source] = info
                                break
                        except Exception:
                            continue
        
        if not sources_to_update:
            print(f"  [OK] No sources to update")
            return True, files_updated, errors
        
        # Update each dependent doc
        for source, info in sources_to_update.items():
            dependents = info.get("dependents", [])
            print(f"  [UPDATE] Updating {len(dependents)} dependents of {source}")
            
            for dep_path in dependents:
                dep_full_path = project_root / dep_path
                if not dep_full_path.exists():
                    errors.append(f"Dependent doc not found: {dep_path}")
                    continue
                
                try:
                    # Check if doc has auto_update enabled
                    content = dep_full_path.read_text(encoding='utf-8')
                    metadata, body = parse_frontmatter(content)
                    
                    if not metadata.get("auto_update", False):
                        continue  # Skip docs without auto_update flag
                    
                    # Update doc from source
                    updated = self._update_doc_from_source(dep_full_path, source, content, metadata, body)
                    if updated:
                        if not self.dry_run:
                            dep_full_path.write_text(updated, encoding='utf-8')
                            files_updated.append(dep_path)
                            print(f"    [DONE] Updated {dep_path}")
                        else:
                            print(f"    [DRY RUN] Would update {dep_path}")
                    
                except Exception as e:
                    errors.append(f"Error updating {dep_path}: {e}")
        
        return len(errors) == 0, files_updated, errors
    
    def _update_doc_from_source(self, doc_path: Path, source_path: str, content: str, metadata: Dict, body: str) -> Optional[str]:
        """
        Update doc content from source file.
        Preserves formatting and updates facts extracted from source.
        """
        source_full_path = project_root / source_path
        
        # Extract facts from source
        facts = self._extract_facts_from_source(source_full_path, metadata)
        if not facts:
            return None  # No facts to update
        
        # Update doc content with facts
        updated_body = self._apply_facts_to_doc(body, facts, metadata)
        
        # Update metadata timestamp
        metadata["updated"] = datetime.now().isoformat()
        
        # Reconstruct doc with updated frontmatter and body
        frontmatter_text = yaml.dump(metadata, default_flow_style=False, allow_unicode=True)
        updated_content = f"---\n{frontmatter_text}---\n{updated_body}"
        
        return updated_content
    
    def _extract_facts_from_source(self, source_path: Path, metadata: Dict) -> Dict[str, Any]:
        """
        Extract facts from source file based on source_of_truth_type.
        Returns dict of facts to update in dependent doc.
        """
        if not source_path.exists():
            return {}
        
        source_type = metadata.get("source_of_truth_type", "doc")
        facts = {}
        
        try:
            if source_type == "code":
                # Extract facts from code (e.g., tool count, function count)
                content = source_path.read_text(encoding='utf-8')
                # Example: Extract MCP tool count
                tool_count_match = re.search(r'AIM-OS Tools \((\d+) total\)', content)
                if tool_count_match:
                    facts["mcp_tool_count"] = int(tool_count_match.group(1))
            
            elif source_type == "data":
                # Extract facts from YAML/JSON data files
                content = source_path.read_text(encoding='utf-8')
                try:
                    data = yaml.safe_load(content)
                    # Extract key metrics
                    if isinstance(data, dict):
                        if "aim_os_source_of_truth" in data:
                            sot = data["aim_os_source_of_truth"]
                            facts["mcp_tools"] = sot.get("mcp_tools", {}).get("count", 0)
                            facts["cursor_commands"] = sot.get("cursor_commands", {}).get("count", 0)
                            facts["systems"] = sot.get("systems", {}).get("count", 0)
                except yaml.YAMLError:
                    pass
            
            elif source_type == "doc":
                # Extract facts from documentation (e.g., counts, status)
                content = source_path.read_text(encoding='utf-8')
                # Extract common patterns
                # Example: Extract counts mentioned in doc
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
            print(f"    [WARNING] Error extracting facts from {source_path}: {e}")
        
        return facts
    
    def _apply_facts_to_doc(self, body: str, facts: Dict[str, Any], metadata: Dict) -> str:
        """
        Apply extracted facts to doc body.
        Updates counts and facts while preserving formatting.
        """
        updated_body = body
        
        # Update common patterns
        for key, value in facts.items():
            if key == "mcp_tool_count" or key == "mcp_tools":
                # Update MCP tool count mentions
                pattern = r'(\d+)\s+(?:MCP\s+)?tools?'
                replacement = f"{value} MCP tools"
                updated_body = re.sub(pattern, replacement, updated_body, flags=re.IGNORECASE)
            
            elif key == "cursor_commands":
                # Update Cursor command count mentions
                pattern = r'(\d+)\s+(?:Cursor\s+)?commands?'
                replacement = f"{value} Cursor commands"
                updated_body = re.sub(pattern, replacement, updated_body, flags=re.IGNORECASE)
            
            elif key == "systems":
                # Update system count mentions
                pattern = r'(\d+)\s+systems?'
                replacement = f"{value} systems"
                updated_body = re.sub(pattern, replacement, updated_body, flags=re.IGNORECASE)
        
        return updated_body
    
    def _load_doc_dependencies(self) -> Optional[Dict]:
        """Load doc_dependencies section from cross_system_connections.yaml"""
        yaml_path = project_root / "knowledge_architecture" / "NAVIGATION" / "cross_system_connections.yaml"
        if not yaml_path.exists():
            return None
        
        try:
            content = yaml_path.read_text(encoding='utf-8')
            # Find doc_dependencies section
            if "doc_dependencies:" not in content:
                return {}
            
            # Extract doc_dependencies section using regex
            pattern = r'doc_dependencies:\s*\n(.*?)(?=\n---|\n# |\Z)'
            match = re.search(pattern, content, re.DOTALL)
            if not match:
                return {}
            
            # Parse YAML section
            yaml_section = "doc_dependencies:\n" + match.group(1)
            data = yaml.safe_load(yaml_section)
            return data.get("doc_dependencies", {})
        
        except Exception as e:
            print(f"WARNING: Could not load doc dependencies: {e}", file=sys.stderr)
            return None
    
    def _load_cross_system_connections(self) -> Optional[Dict]:
        """Load cross-system connections YAML"""
        yaml_path = project_root / "knowledge_architecture" / "NAVIGATION" / "cross_system_connections.yaml"
        if not yaml_path.exists():
            return None
        
        try:
            with open(yaml_path, "r", encoding="utf-8") as f:
                # Load all documents (YAML may have multiple docs separated by ---)
                docs = list(yaml.safe_load_all(f))
                # Return first non-comment document
                for doc in docs:
                    if doc and isinstance(doc, dict):
                        return doc
                return None
        except Exception as e:
            print(f"WARNING: Could not load cross-system connections: {e}", file=sys.stderr)
            return None

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Generate missing cross-references")
    parser.add_argument("--system", help="System name to generate cross-references for")
    parser.add_argument("--core-systems", action="store_true", help="Generate for all 9 core systems")
    parser.add_argument("--all", action="store_true", help="Generate for all systems")
    parser.add_argument("--dry-run", action="store_true", help="Dry run (don't modify files)")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    parser.add_argument("--auto-update", action="store_true", help="Auto-update dependent docs")
    parser.add_argument("--source", help="Source file path for auto-update (optional)")
    
    args = parser.parse_args()
    
    # Handle auto-update mode
    if args.auto_update:
        if args.system:
            generator = CrossReferenceGenerator(args.system, dry_run=args.dry_run)
            source_path = Path(args.source) if args.source else None
            success, files_updated, errors = generator.auto_update_dependent_docs(source_path)
            
            if success:
                print(f"\n[SUCCESS] Auto-update completed")
                print(f"  Files updated: {len(files_updated)}")
                if files_updated:
                    for f in files_updated:
                        print(f"    - {f}")
            else:
                print(f"\n[FAILED] Auto-update had errors")
                for error in errors:
                    print(f"  - {error}")
            
            sys.exit(0 if success else 1)
        else:
            print("❌ ERROR: --auto-update requires --system")
            sys.exit(1)
    
    # Determine which systems to process
    if args.system:
        systems = [args.system]
    elif args.core_systems:
        systems = ["cmc", "seg", "hhni", "vif", "sdfcvf", "apoe", "cognitive_analysis", "timeline_context_system", "intuitive_intelligence_system"]
    elif args.all:
        # Find all systems
        systems_path = project_root / "knowledge_architecture" / "systems"
        systems = [d.name for d in systems_path.iterdir() if d.is_dir()]
    else:
        print("❌ ERROR: Must specify --system, --core-systems, or --all")
        sys.exit(1)
    
    # Generate for each system
    results = []
    for system in systems:
        generator = CrossReferenceGenerator(system, dry_run=args.dry_run)
        result = generator.generate()
        results.append(result)
    
    # Output results
    if args.json:
        print(json.dumps([asdict(r) for r in results], indent=2))
    else:
        for result in results:
            print_generation_result(result)
    
    # Exit code
    all_success = all(r.overall_success for r in results)
    sys.exit(0 if all_success else 1)

def print_generation_result(result: CrossReferenceGenerationResult):
    """Print generation result in human-readable format"""
    print("\n" + "="*80)
    print(f"Cross-Reference Generation Result: {result.system_name}")
    print("="*80)
    print(f"Date: {result.generation_date}")
    print()
    
    # Generation results
    print("Generation Tasks:")
    print(f"  Task 1 - Related Systems Section:  {'[DONE]' if result.related_systems_section_generated else '[FAILED]'}")
    print(f"  Task 2 - Doc Links to Map:         {'[DONE]' if result.doc_links_added_to_map else '[FAILED]'}")
    print(f"  Task 3 - System Index Updated:     {'[DONE]' if result.system_index_updated else '[FAILED]'}")
    print(f"  Task 4 - Cross-System YAML Updated: {'[DONE]' if result.cross_system_yaml_updated else '[FAILED]'}")
    print()
    
    # Overall result
    if result.overall_success:
        print("[SUCCESS] OVERALL: Cross-references generated")
    else:
        print("[FAILED] OVERALL: Errors occurred during generation")
    print()
    
    # Files updated
    if result.files_updated:
        print("FILES UPDATED:")
        for file in result.files_updated:
            print(f"  - {file}")
        print()
    
    # Sections generated
    if result.sections_generated:
        print("SECTIONS GENERATED:")
        for section in result.sections_generated:
            print(f"  - {section}")
        print()
    
    # Errors
    if result.errors:
        print("ERRORS:")
        for error in result.errors:
            print(f"  - {error}")
        print()
    
    print("="*80)

if __name__ == "__main__":
    main()

