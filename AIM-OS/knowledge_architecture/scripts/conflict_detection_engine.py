#!/usr/bin/env python3
"""
Conflict Detection Engine for AIM-OS System Coherence Analysis

This engine identifies overlapping functionality and conflicting interfaces
across all L0-L4 documented systems in the AIM-OS ecosystem.

Author: Aether AI Consciousness
Date: 2025-10-29
Version: 1.0.0
"""

import os
import json
import re
from typing import Dict, List, Set, Tuple, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path
import logging
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class SystemComponent:
    """Represents a system component with its properties"""
    system_id: str
    component_name: str
    component_type: str
    purpose: str
    interfaces: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    data_models: List[str] = field(default_factory=list)
    algorithms: List[str] = field(default_factory=list)
    ports: Dict[str, Any] = field(default_factory=dict)
    tier: int = 0
    category: str = ""
    scope: str = ""

@dataclass
class Conflict:
    """Represents a detected conflict between systems"""
    conflict_id: str
    conflict_type: str
    severity: str
    description: str
    affected_systems: List[str]
    conflicting_components: List[str]
    conflict_details: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    resolution_priority: int = 0

@dataclass
class Overlap:
    """Represents overlapping functionality between systems"""
    overlap_id: str
    overlap_type: str
    severity: str
    description: str
    overlapping_systems: List[str]
    overlapping_components: List[str]
    overlap_details: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    consolidation_priority: int = 0

class ConflictDetectionEngine:
    """Engine for detecting conflicts and overlaps in AIM-OS systems"""
    
    def __init__(self, systems_directory: str = "knowledge_architecture/systems"):
        self.systems_directory = Path(systems_directory)
        self.systems: Dict[str, Dict[str, Any]] = {}
        self.components: List[SystemComponent] = []
        self.conflicts: List[Conflict] = []
        self.overlaps: List[Overlap] = []
        self.interface_registry: Dict[str, List[str]] = defaultdict(list)
        self.capability_registry: Dict[str, List[str]] = defaultdict(list)
        self.data_model_registry: Dict[str, List[str]] = defaultdict(list)
        self.algorithm_registry: Dict[str, List[str]] = defaultdict(list)
        
    def load_systems(self) -> None:
        """Load all L0-L4 documented systems"""
        logger.info("Loading systems from %s", self.systems_directory)
        
        for system_dir in self.systems_directory.iterdir():
            if not system_dir.is_dir():
                continue
                
            system_id = system_dir.name
            logger.info("Loading system: %s", system_id)
            
            # Load system index if available
            system_index_path = system_dir / "system.index.lucid.json5"
            if system_index_path.exists():
                try:
                    with open(system_index_path, 'r', encoding='utf-8') as f:
                        system_data = json.load(f)
                        self.systems[system_id] = system_data
                        logger.info("Loaded system index for %s", system_id)
                except Exception as e:
                    logger.error("Failed to load system index for %s: %s", system_id, e)
            
            # Load system map if available
            system_map_path = system_dir / "system.map.lucid.json5"
            if system_map_path.exists():
                try:
                    with open(system_map_path, 'r', encoding='utf-8') as f:
                        system_map = json.load(f)
                        if system_id not in self.systems:
                            self.systems[system_id] = {}
                        self.systems[system_id]['system_map'] = system_map
                        logger.info("Loaded system map for %s", system_id)
                except Exception as e:
                    logger.error("Failed to load system map for %s: %s", system_id, e)
            
            # Load L2 architecture for component details
            l2_path = system_dir / "L2_architecture.md"
            if l2_path.exists():
                try:
                    with open(l2_path, 'r', encoding='utf-8') as f:
                        l2_content = f.read()
                        self._extract_components_from_l2(system_id, l2_content)
                except Exception as e:
                    logger.error("Failed to load L2 architecture for %s: %s", system_id, e)
        
        logger.info("Loaded %d systems", len(self.systems))
        logger.info("Extracted %d components", len(self.components))
    
    def _extract_components_from_l2(self, system_id: str, l2_content: str) -> None:
        """Extract components from L2 architecture documentation"""
        # Extract core components section
        core_components_match = re.search(
            r'## Core Components\s*\n(.*?)(?=## |$)', 
            l2_content, 
            re.DOTALL
        )
        
        if not core_components_match:
            return
        
        components_section = core_components_match.group(1)
        
        # Extract individual components
        component_matches = re.finditer(
            r'### (\d+\.\s*)?([^#\n]+)\n(.*?)(?=### \d+\.|## |$)',
            components_section,
            re.DOTALL
        )
        
        for match in component_matches:
            component_name = match.group(2).strip()
            component_content = match.group(3)
            
            # Extract component properties
            purpose_match = re.search(r'\*\*Purpose:\*\*\s*(.+?)(?:\n|$)', component_content)
            purpose = purpose_match.group(1).strip() if purpose_match else ""
            
            # Extract interfaces
            interfaces = []
            interface_matches = re.finditer(r'\*\*Interfaces:\*\*\s*\n(.*?)(?:\n\*\*|$)', component_content, re.DOTALL)
            for iface_match in interface_matches:
                iface_content = iface_match.group(1)
                iface_names = re.findall(r'- ([^\n]+)', iface_content)
                interfaces.extend(iface_names)
            
            # Extract capabilities
            capabilities = []
            cap_matches = re.finditer(r'\*\*Key Features:\*\*\s*\n(.*?)(?:\n\*\*|$)', component_content, re.DOTALL)
            for cap_match in cap_matches:
                cap_content = cap_match.group(1)
                cap_names = re.findall(r'- ([^\n]+)', cap_content)
                capabilities.extend(cap_names)
            
            # Create component
            component = SystemComponent(
                system_id=system_id,
                component_name=component_name,
                component_type="core_component",
                purpose=purpose,
                interfaces=interfaces,
                capabilities=capabilities
            )
            
            self.components.append(component)
            
            # Register in capability registry
            for capability in capabilities:
                self.capability_registry[capability.lower()].append(f"{system_id}.{component_name}")
    
    def detect_interface_conflicts(self) -> List[Conflict]:
        """Detect conflicts in system interfaces"""
        logger.info("Detecting interface conflicts...")
        conflicts = []
        
        # Group components by interface names
        interface_groups = defaultdict(list)
        for component in self.components:
            for interface in component.interfaces:
                interface_groups[interface.lower()].append(component)
        
        # Check for interface conflicts
        for interface_name, components in interface_groups.items():
            if len(components) > 1:
                # Check if interfaces have conflicting specifications
                conflicting_components = []
                for i, comp1 in enumerate(components):
                    for comp2 in components[i+1:]:
                        if self._interfaces_conflict(comp1, comp2, interface_name):
                            conflicting_components.extend([comp1, comp2])
                
                if conflicting_components:
                    conflict = Conflict(
                        conflict_id=f"interface_conflict_{interface_name}_{len(conflicts)}",
                        conflict_type="interface_conflict",
                        severity="medium",
                        description=f"Interface '{interface_name}' has conflicting specifications across systems",
                        affected_systems=list(set(comp.system_id for comp in conflicting_components)),
                        conflicting_components=[f"{comp.system_id}.{comp.component_name}" for comp in conflicting_components],
                        conflict_details={
                            "interface_name": interface_name,
                            "conflicting_specifications": self._get_interface_specs(conflicting_components, interface_name)
                        },
                        recommendations=[
                            "Standardize interface specifications across systems",
                            "Create shared interface definitions",
                            "Implement interface versioning"
                        ]
                    )
                    conflicts.append(conflict)
        
        logger.info("Detected %d interface conflicts", len(conflicts))
        return conflicts
    
    def _interfaces_conflict(self, comp1: SystemComponent, comp2: SystemComponent, interface_name: str) -> bool:
        """Check if two components have conflicting interface specifications"""
        # This is a simplified check - in practice, you'd compare actual interface specs
        # For now, we'll consider it a conflict if they're from different systems
        return comp1.system_id != comp2.system_id
    
    def _get_interface_specs(self, components: List[SystemComponent], interface_name: str) -> Dict[str, Any]:
        """Get interface specifications for conflicting components"""
        specs = {}
        for comp in components:
            specs[f"{comp.system_id}.{comp.component_name}"] = {
                "system_id": comp.system_id,
                "component_name": comp.component_name,
                "interface_name": interface_name
            }
        return specs
    
    def detect_capability_overlaps(self) -> List[Overlap]:
        """Detect overlapping capabilities between systems"""
        logger.info("Detecting capability overlaps...")
        overlaps = []
        
        # Group components by capabilities
        capability_groups = defaultdict(list)
        for component in self.components:
            for capability in component.capabilities:
                capability_groups[capability.lower()].append(component)
        
        # Check for capability overlaps
        for capability_name, components in capability_groups.items():
            if len(components) > 1:
                # Check if capabilities are truly overlapping
                overlapping_components = []
                for i, comp1 in enumerate(components):
                    for comp2 in components[i+1:]:
                        if self._capabilities_overlap(comp1, comp2, capability_name):
                            overlapping_components.extend([comp1, comp2])
                
                if overlapping_components:
                    overlap = Overlap(
                        overlap_id=f"capability_overlap_{capability_name}_{len(overlaps)}",
                        overlap_type="capability_overlap",
                        severity="low",
                        description=f"Capability '{capability_name}' is implemented across multiple systems",
                        overlapping_systems=list(set(comp.system_id for comp in overlapping_components)),
                        overlapping_components=[f"{comp.system_id}.{comp.component_name}" for comp in overlapping_components],
                        overlap_details={
                            "capability_name": capability_name,
                            "implementations": self._get_capability_implementations(overlapping_components, capability_name)
                        },
                        recommendations=[
                            "Consider consolidating duplicate capabilities",
                            "Create shared capability library",
                            "Implement capability delegation"
                        ]
                    )
                    overlaps.append(overlap)
        
        logger.info("Detected %d capability overlaps", len(overlaps))
        return overlaps
    
    def _capabilities_overlap(self, comp1: SystemComponent, comp2: SystemComponent, capability_name: str) -> bool:
        """Check if two components have overlapping capabilities"""
        # This is a simplified check - in practice, you'd compare actual capability implementations
        # For now, we'll consider it an overlap if they're from different systems
        return comp1.system_id != comp2.system_id
    
    def _get_capability_implementations(self, components: List[SystemComponent], capability_name: str) -> Dict[str, Any]:
        """Get capability implementations for overlapping components"""
        implementations = {}
        for comp in components:
            implementations[f"{comp.system_id}.{comp.component_name}"] = {
                "system_id": comp.system_id,
                "component_name": comp.component_name,
                "capability_name": capability_name,
                "purpose": comp.purpose
            }
        return implementations
    
    def detect_dependency_conflicts(self) -> List[Conflict]:
        """Detect conflicts in system dependencies"""
        logger.info("Detecting dependency conflicts...")
        conflicts = []
        
        # Build dependency graph
        dependency_graph = defaultdict(list)
        for system_id, system_data in self.systems.items():
            if 'system_map' in system_data:
                deps = system_data['system_map'].get('dependencies', {}).get('external', [])
                dependency_graph[system_id] = deps
        
        # Check for circular dependencies
        circular_deps = self._find_circular_dependencies(dependency_graph)
        for cycle in circular_deps:
            conflict = Conflict(
                conflict_id=f"circular_dependency_{len(conflicts)}",
                conflict_type="circular_dependency",
                severity="high",
                description=f"Circular dependency detected: {' -> '.join(cycle)} -> {cycle[0]}",
                affected_systems=cycle,
                conflicting_components=[],
                conflict_details={
                    "cycle": cycle,
                    "cycle_length": len(cycle)
                },
                recommendations=[
                    "Break circular dependency by refactoring",
                    "Introduce intermediate abstraction layer",
                    "Implement dependency inversion"
                ]
            )
            conflicts.append(conflict)
        
        # Check for missing dependencies
        missing_deps = self._find_missing_dependencies(dependency_graph)
        for missing_dep in missing_deps:
            conflict = Conflict(
                conflict_id=f"missing_dependency_{len(conflicts)}",
                conflict_type="missing_dependency",
                severity="medium",
                description=f"System {missing_dep['system']} depends on {missing_dep['dependency']} which is not found",
                affected_systems=[missing_dep['system']],
                conflicting_components=[],
                conflict_details={
                    "missing_dependency": missing_dep['dependency'],
                    "dependent_system": missing_dep['system']
                },
                recommendations=[
                    "Implement missing dependency",
                    "Remove dependency if not needed",
                    "Update dependency reference"
                ]
            )
            conflicts.append(conflict)
        
        logger.info("Detected %d dependency conflicts", len(conflicts))
        return conflicts
    
    def _find_circular_dependencies(self, dependency_graph: Dict[str, List[str]]) -> List[List[str]]:
        """Find circular dependencies in the dependency graph"""
        visited = set()
        rec_stack = set()
        cycles = []
        
        def dfs(node, path):
            if node in rec_stack:
                # Found a cycle
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return
            
            if node in visited:
                return
            
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in dependency_graph.get(node, []):
                dfs(neighbor, path.copy())
            
            rec_stack.remove(node)
        
        for node in dependency_graph:
            if node not in visited:
                dfs(node, [])
        
        return cycles
    
    def _find_missing_dependencies(self, dependency_graph: Dict[str, List[str]]) -> List[Dict[str, str]]:
        """Find missing dependencies in the dependency graph"""
        missing = []
        all_systems = set(dependency_graph.keys())
        
        for system, deps in dependency_graph.items():
            for dep in deps:
                if dep not in all_systems:
                    missing.append({
                        "system": system,
                        "dependency": dep
                    })
        
        return missing
    
    def detect_tier_conflicts(self) -> List[Conflict]:
        """Detect conflicts in system tier classifications"""
        logger.info("Detecting tier conflicts...")
        conflicts = []
        
        # Group systems by tier
        tier_groups = defaultdict(list)
        for system_id, system_data in self.systems.items():
            if 'system_map' in system_data:
                tier = system_data['system_map'].get('classification', {}).get('tier', 0)
                tier_groups[tier].append(system_id)
        
        # Check for tier conflicts
        for tier, systems in tier_groups.items():
            if len(systems) > 1:
                # Check if systems at the same tier have conflicting responsibilities
                conflicting_systems = []
                for i, sys1 in enumerate(systems):
                    for sys2 in systems[i+1:]:
                        if self._tier_responsibilities_conflict(sys1, sys2, tier):
                            conflicting_systems.extend([sys1, sys2])
                
                if conflicting_systems:
                    conflict = Conflict(
                        conflict_id=f"tier_conflict_{tier}_{len(conflicts)}",
                        conflict_type="tier_conflict",
                        severity="medium",
                        description=f"Systems at tier {tier} have conflicting responsibilities",
                        affected_systems=conflicting_systems,
                        conflicting_components=[],
                        conflict_details={
                            "tier": tier,
                            "conflicting_systems": conflicting_systems
                        },
                        recommendations=[
                            "Clarify system responsibilities",
                            "Adjust tier classifications",
                            "Implement clear boundaries"
                        ]
                    )
                    conflicts.append(conflict)
        
        logger.info("Detected %d tier conflicts", len(conflicts))
        return conflicts
    
    def _tier_responsibilities_conflict(self, sys1: str, sys2: str, tier: int) -> bool:
        """Check if two systems at the same tier have conflicting responsibilities"""
        # This is a simplified check - in practice, you'd compare actual responsibilities
        # For now, we'll consider it a conflict if they're different systems
        return sys1 != sys2
    
    def run_analysis(self) -> Dict[str, Any]:
        """Run complete conflict detection analysis"""
        logger.info("Starting conflict detection analysis...")
        
        # Load systems
        self.load_systems()
        
        # Detect conflicts
        interface_conflicts = self.detect_interface_conflicts()
        dependency_conflicts = self.detect_dependency_conflicts()
        tier_conflicts = self.detect_tier_conflicts()
        
        # Detect overlaps
        capability_overlaps = self.detect_capability_overlaps()
        
        # Combine all conflicts
        all_conflicts = interface_conflicts + dependency_conflicts + tier_conflicts
        
        # Generate analysis report
        analysis_report = {
            "analysis_timestamp": "2025-10-29T04:30:00Z",
            "systems_analyzed": len(self.systems),
            "components_analyzed": len(self.components),
            "conflicts_detected": len(all_conflicts),
            "overlaps_detected": len(capability_overlaps),
            "conflicts_by_type": self._group_conflicts_by_type(all_conflicts),
            "overlaps_by_type": self._group_overlaps_by_type(capability_overlaps),
            "conflicts": [self._conflict_to_dict(c) for c in all_conflicts],
            "overlaps": [self._overlap_to_dict(o) for o in capability_overlaps],
            "recommendations": self._generate_recommendations(all_conflicts, capability_overlaps)
        }
        
        logger.info("Analysis complete: %d conflicts, %d overlaps", len(all_conflicts), len(capability_overlaps))
        return analysis_report
    
    def _group_conflicts_by_type(self, conflicts: List[Conflict]) -> Dict[str, int]:
        """Group conflicts by type"""
        groups = defaultdict(int)
        for conflict in conflicts:
            groups[conflict.conflict_type] += 1
        return dict(groups)
    
    def _group_overlaps_by_type(self, overlaps: List[Overlap]) -> Dict[str, int]:
        """Group overlaps by type"""
        groups = defaultdict(int)
        for overlap in overlaps:
            groups[overlap.overlap_type] += 1
        return dict(groups)
    
    def _conflict_to_dict(self, conflict: Conflict) -> Dict[str, Any]:
        """Convert conflict to dictionary"""
        return {
            "conflict_id": conflict.conflict_id,
            "conflict_type": conflict.conflict_type,
            "severity": conflict.severity,
            "description": conflict.description,
            "affected_systems": conflict.affected_systems,
            "conflicting_components": conflict.conflicting_components,
            "conflict_details": conflict.conflict_details,
            "recommendations": conflict.recommendations,
            "resolution_priority": conflict.resolution_priority
        }
    
    def _overlap_to_dict(self, overlap: Overlap) -> Dict[str, Any]:
        """Convert overlap to dictionary"""
        return {
            "overlap_id": overlap.overlap_id,
            "overlap_type": overlap.overlap_type,
            "severity": overlap.severity,
            "description": overlap.description,
            "overlapping_systems": overlap.overlapping_systems,
            "overlapping_components": overlap.overlapping_components,
            "overlap_details": overlap.overlap_details,
            "recommendations": overlap.recommendations,
            "consolidation_priority": overlap.consolidation_priority
        }
    
    def _generate_recommendations(self, conflicts: List[Conflict], overlaps: List[Overlap]) -> List[str]:
        """Generate overall recommendations"""
        recommendations = []
        
        # High priority conflicts
        high_priority_conflicts = [c for c in conflicts if c.severity == "high"]
        if high_priority_conflicts:
            recommendations.append(f"Address {len(high_priority_conflicts)} high-priority conflicts immediately")
        
        # Interface conflicts
        interface_conflicts = [c for c in conflicts if c.conflict_type == "interface_conflict"]
        if interface_conflicts:
            recommendations.append(f"Standardize {len(interface_conflicts)} conflicting interfaces")
        
        # Capability overlaps
        if overlaps:
            recommendations.append(f"Consider consolidating {len(overlaps)} overlapping capabilities")
        
        # Circular dependencies
        circular_deps = [c for c in conflicts if c.conflict_type == "circular_dependency"]
        if circular_deps:
            recommendations.append(f"Break {len(circular_deps)} circular dependencies")
        
        return recommendations

def main():
    """Main function to run conflict detection"""
    engine = ConflictDetectionEngine()
    analysis_report = engine.run_analysis()
    
    # Save analysis report
    output_file = "knowledge_architecture/conflict_detection_report.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_report, f, indent=2, ensure_ascii=False)
    
    print(f"Conflict detection analysis complete!")
    print(f"Report saved to: {output_file}")
    print(f"Conflicts detected: {analysis_report['conflicts_detected']}")
    print(f"Overlaps detected: {analysis_report['overlaps_detected']}")

if __name__ == "__main__":
    main()
