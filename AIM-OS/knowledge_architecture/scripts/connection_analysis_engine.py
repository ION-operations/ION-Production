#!/usr/bin/env python3
"""
Connection Analysis Engine for AIM-OS System Coherence Analysis

This engine identifies missing dependencies and system awareness
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
class MissingConnection:
    """Represents a missing connection between systems"""
    connection_id: str
    connection_type: str
    severity: str
    description: str
    source_system: str
    target_system: str
    missing_connection_details: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    implementation_priority: int = 0

@dataclass
class SystemAwarenessGap:
    """Represents a gap in system awareness"""
    gap_id: str
    gap_type: str
    severity: str
    description: str
    affected_system: str
    missing_awareness: List[str] = field(default_factory=list)
    gap_details: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    awareness_priority: int = 0

class ConnectionAnalysisEngine:
    """Engine for analyzing system connections and awareness gaps"""
    
    def __init__(self, systems_directory: str = "knowledge_architecture/systems"):
        self.systems_directory = Path(systems_directory)
        self.systems: Dict[str, Dict[str, Any]] = {}
        self.system_maps: Dict[str, Dict[str, Any]] = {}
        self.system_indexes: Dict[str, Dict[str, Any]] = {}
        self.missing_connections: List[MissingConnection] = []
        self.awareness_gaps: List[SystemAwarenessGap] = []
        self.connection_graph: Dict[str, Set[str]] = defaultdict(set)
        self.awareness_matrix: Dict[str, Set[str]] = defaultdict(set)
        
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
                        self.system_indexes[system_id] = system_data
                        logger.info("Loaded system index for %s", system_id)
                except Exception as e:
                    logger.error("Failed to load system index for %s: %s", system_id, e)
            
            # Load system map if available
            system_map_path = system_dir / "system.map.lucid.json5"
            if system_map_path.exists():
                try:
                    with open(system_map_path, 'r', encoding='utf-8') as f:
                        system_map = json.load(f)
                        self.system_maps[system_id] = system_map
                        logger.info("Loaded system map for %s", system_id)
                except Exception as e:
                    logger.error("Failed to load system map for %s: %s", system_id, e)
        
        # Build connection graph
        self._build_connection_graph()
        
        # Build awareness matrix
        self._build_awareness_matrix()
        
        logger.info("Loaded %d systems", len(self.systems))
    
    def _build_connection_graph(self) -> None:
        """Build connection graph from system maps"""
        logger.info("Building connection graph...")
        
        for system_id, system_map in self.system_maps.items():
            # Extract dependencies
            dependencies = system_map.get('dependencies', {})
            external_deps = dependencies.get('external', [])
            internal_deps = dependencies.get('internal', [])
            
            # Add external dependencies
            for dep in external_deps:
                self.connection_graph[system_id].add(dep)
            
            # Add internal dependencies
            for dep in internal_deps:
                self.connection_graph[system_id].add(dep)
            
            # Extract connections from boundary tendrils
            boundary_tendrils = system_map.get('boundary_tendrils', {})
            input_ports = boundary_tendrils.get('input_ports', {})
            output_ports = boundary_tendrils.get('output_ports', {})
            
            # Add connections from input ports
            for port_name, port_config in input_ports.items():
                if 'source' in port_config:
                    source = port_config['source']
                    if isinstance(source, str):
                        self.connection_graph[system_id].add(source)
                    elif isinstance(source, list):
                        for s in source:
                            self.connection_graph[system_id].add(s)
            
            # Add connections from output ports
            for port_name, port_config in output_ports.items():
                if 'target' in port_config:
                    target = port_config['target']
                    if isinstance(target, str):
                        self.connection_graph[target].add(system_id)
                    elif isinstance(target, list):
                        for t in target:
                            self.connection_graph[t].add(system_id)
    
    def _build_awareness_matrix(self) -> None:
        """Build awareness matrix from system indexes"""
        logger.info("Building awareness matrix...")
        
        for system_id, system_index in self.system_indexes.items():
            # Extract connections from system index
            connections = system_index.get('connections', {})
            upstream = connections.get('upstream', [])
            downstream = connections.get('downstream', [])
            lateral = connections.get('lateral', [])
            
            # Add upstream awareness
            for conn in upstream:
                target_system = conn.get('system', '')
                if target_system:
                    self.awareness_matrix[system_id].add(target_system)
            
            # Add downstream awareness
            for conn in downstream:
                target_system = conn.get('system', '')
                if target_system:
                    self.awareness_matrix[system_id].add(target_system)
            
            # Add lateral awareness
            for conn in lateral:
                target_system = conn.get('system', '')
                if target_system:
                    self.awareness_matrix[system_id].add(target_system)
    
    def detect_missing_dependencies(self) -> List[MissingConnection]:
        """Detect missing dependencies between systems"""
        logger.info("Detecting missing dependencies...")
        missing_connections = []
        
        # Get all system IDs
        all_systems = set(self.system_maps.keys())
        
        # Check for missing dependencies
        for system_id, dependencies in self.connection_graph.items():
            for dep in dependencies:
                if dep not in all_systems:
                    missing_connection = MissingConnection(
                        connection_id=f"missing_dependency_{system_id}_{dep}_{len(missing_connections)}",
                        connection_type="missing_dependency",
                        severity="high",
                        description=f"System {system_id} depends on {dep} which is not found",
                        source_system=system_id,
                        target_system=dep,
                        missing_connection_details={
                            "dependency_type": "external",
                            "missing_system": dep,
                            "dependent_system": system_id
                        },
                        recommendations=[
                            "Implement missing dependency system",
                            "Remove dependency if not needed",
                            "Update dependency reference"
                        ]
                    )
                    missing_connections.append(missing_connection)
        
        logger.info("Detected %d missing dependencies", len(missing_connections))
        return missing_connections
    
    def detect_missing_connections(self) -> List[MissingConnection]:
        """Detect missing connections between systems"""
        logger.info("Detecting missing connections...")
        missing_connections = []
        
        # Get all system IDs
        all_systems = set(self.system_maps.keys())
        
        # Check for missing connections based on system purpose
        for system_id, system_map in self.system_maps.items():
            purpose = system_map.get('purpose', '').lower()
            classification = system_map.get('classification', {})
            tier = classification.get('tier', 0)
            category = classification.get('category', '')
            
            # Find potential connections based on purpose and category
            potential_connections = self._find_potential_connections(
                system_id, purpose, tier, category, all_systems
            )
            
            # Check if connections are missing
            for potential_conn in potential_connections:
                if potential_conn not in self.connection_graph[system_id]:
                    missing_connection = MissingConnection(
                        connection_id=f"missing_connection_{system_id}_{potential_conn}_{len(missing_connections)}",
                        connection_type="missing_connection",
                        severity="medium",
                        description=f"System {system_id} should connect to {potential_conn} based on purpose and category",
                        source_system=system_id,
                        target_system=potential_conn,
                        missing_connection_details={
                            "connection_type": "potential",
                            "reason": "purpose_category_match",
                            "source_purpose": purpose,
                            "source_category": category,
                            "target_system": potential_conn
                        },
                        recommendations=[
                            "Implement connection to potential system",
                            "Verify connection necessity",
                            "Update system map with connection"
                        ]
                    )
                    missing_connections.append(missing_connection)
        
        logger.info("Detected %d missing connections", len(missing_connections))
        return missing_connections
    
    def _find_potential_connections(self, system_id: str, purpose: str, tier: int, 
                                  category: str, all_systems: Set[str]) -> List[str]:
        """Find potential connections based on system purpose and category"""
        potential_connections = []
        
        # Define connection patterns based on purpose keywords
        purpose_patterns = {
            'memory': ['storage', 'database', 'cache', 'persistence'],
            'orchestration': ['execution', 'planning', 'workflow', 'coordination'],
            'safety': ['validation', 'monitoring', 'audit', 'compliance'],
            'learning': ['adaptation', 'improvement', 'optimization', 'analysis'],
            'coordination': ['communication', 'synchronization', 'consensus', 'collaboration'],
            'monitoring': ['metrics', 'logging', 'observability', 'health'],
            'security': ['authentication', 'authorization', 'encryption', 'audit']
        }
        
        # Find systems that match purpose patterns
        for pattern, keywords in purpose_patterns.items():
            if any(keyword in purpose for keyword in keywords):
                for other_system in all_systems:
                    if other_system != system_id:
                        other_system_map = self.system_maps.get(other_system, {})
                        other_purpose = other_system_map.get('purpose', '').lower()
                        other_category = other_system_map.get('classification', {}).get('category', '')
                        
                        # Check if other system matches pattern
                        if any(keyword in other_purpose for keyword in keywords):
                            potential_connections.append(other_system)
        
        # Find systems in same category
        if category:
            for other_system in all_systems:
                if other_system != system_id:
                    other_system_map = self.system_maps.get(other_system, {})
                    other_category = other_system_map.get('classification', {}).get('category', '')
                    if other_category == category:
                        potential_connections.append(other_system)
        
        return list(set(potential_connections))
    
    def detect_awareness_gaps(self) -> List[SystemAwarenessGap]:
        """Detect gaps in system awareness"""
        logger.info("Detecting awareness gaps...")
        awareness_gaps = []
        
        # Get all system IDs
        all_systems = set(self.system_maps.keys())
        
        # Check for awareness gaps
        for system_id, aware_systems in self.awareness_matrix.items():
            # Find systems that should be aware of this system
            should_be_aware = self._find_systems_that_should_be_aware(system_id, all_systems)
            
            # Find missing awareness
            missing_awareness = []
            for should_aware_system in should_be_aware:
                if should_aware_system not in aware_systems:
                    missing_awareness.append(should_aware_system)
            
            if missing_awareness:
                gap = SystemAwarenessGap(
                    gap_id=f"awareness_gap_{system_id}_{len(awareness_gaps)}",
                    gap_type="system_awareness",
                    severity="medium",
                    description=f"System {system_id} is not aware of {len(missing_awareness)} systems it should know about",
                    affected_system=system_id,
                    missing_awareness=missing_awareness,
                    gap_details={
                        "missing_systems": missing_awareness,
                        "current_awareness": list(aware_systems),
                        "should_be_aware": should_be_aware
                    },
                    recommendations=[
                        "Update system awareness matrix",
                        "Implement awareness mechanisms",
                        "Add system discovery protocols"
                    ]
                )
                awareness_gaps.append(gap)
        
        logger.info("Detected %d awareness gaps", len(awareness_gaps))
        return awareness_gaps
    
    def _find_systems_that_should_be_aware(self, system_id: str, all_systems: Set[str]) -> List[str]:
        """Find systems that should be aware of the given system"""
        should_be_aware = []
        
        system_map = self.system_maps.get(system_id, {})
        purpose = system_map.get('purpose', '').lower()
        classification = system_map.get('classification', {})
        tier = classification.get('tier', 0)
        category = classification.get('category', '')
        
        # Find systems that depend on this system
        for other_system in all_systems:
            if other_system != system_id:
                other_dependencies = self.connection_graph.get(other_system, set())
                if system_id in other_dependencies:
                    should_be_aware.append(other_system)
        
        # Find systems in same category
        if category:
            for other_system in all_systems:
                if other_system != system_id:
                    other_system_map = self.system_maps.get(other_system, {})
                    other_category = other_system_map.get('classification', {}).get('category', '')
                    if other_category == category:
                        should_be_aware.append(other_system)
        
        # Find systems that provide services this system needs
        if 'memory' in purpose:
            for other_system in all_systems:
                if other_system != system_id:
                    other_purpose = self.system_maps.get(other_system, {}).get('purpose', '').lower()
                    if 'storage' in other_purpose or 'database' in other_purpose:
                        should_be_aware.append(other_system)
        
        if 'orchestration' in purpose:
            for other_system in all_systems:
                if other_system != system_id:
                    other_purpose = self.system_maps.get(other_system, {}).get('purpose', '').lower()
                    if 'execution' in other_purpose or 'workflow' in other_purpose:
                        should_be_aware.append(other_system)
        
        return list(set(should_be_aware))
    
    def detect_integration_gaps(self) -> List[MissingConnection]:
        """Detect gaps in system integration"""
        logger.info("Detecting integration gaps...")
        missing_connections = []
        
        # Get all system IDs
        all_systems = set(self.system_maps.keys())
        
        # Check for integration gaps
        for system_id, system_map in self.system_maps.items():
            classification = system_map.get('classification', {})
            tier = classification.get('tier', 0)
            category = classification.get('category', '')
            
            # Find systems that should integrate with this system
            should_integrate = self._find_systems_that_should_integrate(
                system_id, tier, category, all_systems
            )
            
            # Check if integration is missing
            for should_integrate_system in should_integrate:
                if should_integrate_system not in self.connection_graph[system_id]:
                    missing_connection = MissingConnection(
                        connection_id=f"integration_gap_{system_id}_{should_integrate_system}_{len(missing_connections)}",
                        connection_type="integration_gap",
                        severity="medium",
                        description=f"System {system_id} should integrate with {should_integrate_system}",
                        source_system=system_id,
                        target_system=should_integrate_system,
                        missing_connection_details={
                            "integration_type": "functional",
                            "reason": "tier_category_match",
                            "source_tier": tier,
                            "source_category": category,
                            "target_system": should_integrate_system
                        },
                        recommendations=[
                            "Implement integration between systems",
                            "Create integration interfaces",
                            "Update system maps with integration"
                        ]
                    )
                    missing_connections.append(missing_connection)
        
        logger.info("Detected %d integration gaps", len(missing_connections))
        return missing_connections
    
    def _find_systems_that_should_integrate(self, system_id: str, tier: int, 
                                          category: str, all_systems: Set[str]) -> List[str]:
        """Find systems that should integrate with the given system"""
        should_integrate = []
        
        # Find systems in same tier
        for other_system in all_systems:
            if other_system != system_id:
                other_system_map = self.system_maps.get(other_system, {})
                other_tier = other_system_map.get('classification', {}).get('tier', 0)
                if other_tier == tier:
                    should_integrate.append(other_system)
        
        # Find systems in same category
        if category:
            for other_system in all_systems:
                if other_system != system_id:
                    other_system_map = self.system_maps.get(other_system, {})
                    other_category = other_system_map.get('classification', {}).get('category', '')
                    if other_category == category:
                        should_integrate.append(other_system)
        
        # Find systems that provide complementary functionality
        system_map = self.system_maps.get(system_id, {})
        purpose = system_map.get('purpose', '').lower()
        
        if 'orchestration' in purpose:
            for other_system in all_systems:
                if other_system != system_id:
                    other_purpose = self.system_maps.get(other_system, {}).get('purpose', '').lower()
                    if 'execution' in other_purpose or 'workflow' in other_purpose:
                        should_integrate.append(other_system)
        
        if 'monitoring' in purpose:
            for other_system in all_systems:
                if other_system != system_id:
                    other_purpose = self.system_maps.get(other_system, {}).get('purpose', '').lower()
                    if 'metrics' in other_purpose or 'logging' in other_purpose:
                        should_integrate.append(other_system)
        
        return list(set(should_integrate))
    
    def detect_data_flow_gaps(self) -> List[MissingConnection]:
        """Detect gaps in data flow between systems"""
        logger.info("Detecting data flow gaps...")
        missing_connections = []
        
        # Get all system IDs
        all_systems = set(self.system_maps.keys())
        
        # Check for data flow gaps
        for system_id, system_map in self.system_maps.items():
            purpose = system_map.get('purpose', '').lower()
            
            # Find systems that should receive data from this system
            should_receive_data = self._find_systems_that_should_receive_data(
                system_id, purpose, all_systems
            )
            
            # Check if data flow is missing
            for should_receive_system in should_receive_data:
                if should_receive_system not in self.connection_graph[system_id]:
                    missing_connection = MissingConnection(
                        connection_id=f"data_flow_gap_{system_id}_{should_receive_system}_{len(missing_connections)}",
                        connection_type="data_flow_gap",
                        severity="medium",
                        description=f"System {system_id} should send data to {should_receive_system}",
                        source_system=system_id,
                        target_system=should_receive_system,
                        missing_connection_details={
                            "data_flow_type": "output",
                            "reason": "purpose_match",
                            "source_purpose": purpose,
                            "target_system": should_receive_system
                        },
                        recommendations=[
                            "Implement data flow between systems",
                            "Create data transfer protocols",
                            "Update system maps with data flow"
                        ]
                    )
                    missing_connections.append(missing_connection)
        
        logger.info("Detected %d data flow gaps", len(missing_connections))
        return missing_connections
    
    def _find_systems_that_should_receive_data(self, system_id: str, purpose: str, 
                                             all_systems: Set[str]) -> List[str]:
        """Find systems that should receive data from the given system"""
        should_receive_data = []
        
        # Define data flow patterns based on purpose
        data_flow_patterns = {
            'memory': ['orchestration', 'monitoring', 'analysis'],
            'orchestration': ['execution', 'workflow', 'coordination'],
            'monitoring': ['alerting', 'reporting', 'analysis'],
            'learning': ['optimization', 'adaptation', 'improvement'],
            'safety': ['validation', 'compliance', 'audit']
        }
        
        # Find systems that should receive data
        for pattern, target_types in data_flow_patterns.items():
            if pattern in purpose:
                for other_system in all_systems:
                    if other_system != system_id:
                        other_purpose = self.system_maps.get(other_system, {}).get('purpose', '').lower()
                        if any(target_type in other_purpose for target_type in target_types):
                            should_receive_data.append(other_system)
        
        return list(set(should_receive_data))
    
    def run_analysis(self) -> Dict[str, Any]:
        """Run complete connection analysis"""
        logger.info("Starting connection analysis...")
        
        # Load systems
        self.load_systems()
        
        # Detect missing connections
        missing_dependencies = self.detect_missing_dependencies()
        missing_connections = self.detect_missing_connections()
        integration_gaps = self.detect_integration_gaps()
        data_flow_gaps = self.detect_data_flow_gaps()
        
        # Detect awareness gaps
        awareness_gaps = self.detect_awareness_gaps()
        
        # Combine all missing connections
        all_missing_connections = (missing_dependencies + missing_connections + 
                                 integration_gaps + data_flow_gaps)
        
        # Generate analysis report
        analysis_report = {
            "analysis_timestamp": "2025-10-29T04:30:00Z",
            "systems_analyzed": len(self.system_maps),
            "missing_connections_detected": len(all_missing_connections),
            "awareness_gaps_detected": len(awareness_gaps),
            "missing_connections_by_type": self._group_missing_connections_by_type(all_missing_connections),
            "awareness_gaps_by_type": self._group_awareness_gaps_by_type(awareness_gaps),
            "missing_connections": [self._missing_connection_to_dict(c) for c in all_missing_connections],
            "awareness_gaps": [self._awareness_gap_to_dict(g) for g in awareness_gaps],
            "recommendations": self._generate_recommendations(all_missing_connections, awareness_gaps)
        }
        
        logger.info("Analysis complete: %d missing connections, %d awareness gaps", 
                   len(all_missing_connections), len(awareness_gaps))
        return analysis_report
    
    def _group_missing_connections_by_type(self, missing_connections: List[MissingConnection]) -> Dict[str, int]:
        """Group missing connections by type"""
        groups = defaultdict(int)
        for connection in missing_connections:
            groups[connection.connection_type] += 1
        return dict(groups)
    
    def _group_awareness_gaps_by_type(self, awareness_gaps: List[SystemAwarenessGap]) -> Dict[str, int]:
        """Group awareness gaps by type"""
        groups = defaultdict(int)
        for gap in awareness_gaps:
            groups[gap.gap_type] += 1
        return dict(groups)
    
    def _missing_connection_to_dict(self, connection: MissingConnection) -> Dict[str, Any]:
        """Convert missing connection to dictionary"""
        return {
            "connection_id": connection.connection_id,
            "connection_type": connection.connection_type,
            "severity": connection.severity,
            "description": connection.description,
            "source_system": connection.source_system,
            "target_system": connection.target_system,
            "missing_connection_details": connection.missing_connection_details,
            "recommendations": connection.recommendations,
            "implementation_priority": connection.implementation_priority
        }
    
    def _awareness_gap_to_dict(self, gap: SystemAwarenessGap) -> Dict[str, Any]:
        """Convert awareness gap to dictionary"""
        return {
            "gap_id": gap.gap_id,
            "gap_type": gap.gap_type,
            "severity": gap.severity,
            "description": gap.description,
            "affected_system": gap.affected_system,
            "missing_awareness": gap.missing_awareness,
            "gap_details": gap.gap_details,
            "recommendations": gap.recommendations,
            "awareness_priority": gap.awareness_priority
        }
    
    def _generate_recommendations(self, missing_connections: List[MissingConnection], 
                                awareness_gaps: List[SystemAwarenessGap]) -> List[str]:
        """Generate overall recommendations"""
        recommendations = []
        
        # High priority missing connections
        high_priority_connections = [c for c in missing_connections if c.severity == "high"]
        if high_priority_connections:
            recommendations.append(f"Address {len(high_priority_connections)} high-priority missing connections immediately")
        
        # Missing dependencies
        missing_dependencies = [c for c in missing_connections if c.connection_type == "missing_dependency"]
        if missing_dependencies:
            recommendations.append(f"Implement {len(missing_dependencies)} missing dependency systems")
        
        # Integration gaps
        integration_gaps = [c for c in missing_connections if c.connection_type == "integration_gap"]
        if integration_gaps:
            recommendations.append(f"Implement {len(integration_gaps)} missing integrations")
        
        # Data flow gaps
        data_flow_gaps = [c for c in missing_connections if c.connection_type == "data_flow_gap"]
        if data_flow_gaps:
            recommendations.append(f"Implement {len(data_flow_gaps)} missing data flows")
        
        # Awareness gaps
        if awareness_gaps:
            recommendations.append(f"Address {len(awareness_gaps)} system awareness gaps")
        
        return recommendations

def main():
    """Main function to run connection analysis"""
    engine = ConnectionAnalysisEngine()
    analysis_report = engine.run_analysis()
    
    # Save analysis report
    output_file = "knowledge_architecture/connection_analysis_report.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_report, f, indent=2, ensure_ascii=False)
    
    print(f"Connection analysis complete!")
    print(f"Report saved to: {output_file}")
    print(f"Missing connections detected: {analysis_report['missing_connections_detected']}")
    print(f"Awareness gaps detected: {analysis_report['awareness_gaps_detected']}")

if __name__ == "__main__":
    main()
