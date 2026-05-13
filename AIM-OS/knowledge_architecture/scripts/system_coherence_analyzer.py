#!/usr/bin/env python3
"""
System Coherence Analyzer

Automated analysis of all 21 L0-L4 documented systems to ensure coherence,
prevent conflicts, and identify missing connections before implementation.

This script uses MCP tools to automate the analysis process while preserving
the existing large todo list.
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class SystemInfo:
    """Information about a system from L0-L4 documentation"""
    system_id: str
    name: str
    purpose: str
    tier: int
    category: str
    type: str
    scope: str
    interfaces: List[Dict[str, Any]]
    dependencies: List[str]
    data_models: List[Dict[str, Any]]
    algorithms: List[Dict[str, Any]]
    configuration: Dict[str, Any]
    l0_doc_path: str
    l1_doc_path: str
    l2_doc_path: str
    l3_doc_path: str
    l4_doc_path: str
    system_map_path: str
    system_index_path: str
    usage_envelope_path: str

@dataclass
class Conflict:
    """Represents a conflict between systems"""
    conflict_id: str
    conflict_type: str
    severity: str
    systems_involved: List[str]
    description: str
    resolution_suggestions: List[str]
    confidence: float
    timestamp: datetime

@dataclass
class Duplication:
    """Represents a duplication between systems"""
    duplication_id: str
    duplication_type: str
    systems_involved: List[str]
    description: str
    consolidation_suggestions: List[str]
    confidence: float
    timestamp: datetime

@dataclass
class MissingConnection:
    """Represents a missing connection between systems"""
    connection_id: str
    connection_type: str
    systems_involved: List[str]
    description: str
    integration_suggestions: List[str]
    confidence: float
    timestamp: datetime

@dataclass
class CoherenceReport:
    """Comprehensive coherence analysis report"""
    report_id: str
    timestamp: datetime
    systems_analyzed: int
    conflicts_found: int
    duplications_found: int
    missing_connections_found: int
    conflicts: List[Conflict]
    duplications: List[Duplication]
    missing_connections: List[MissingConnection]
    recommendations: List[str]
    implementation_roadmap: Dict[str, Any]

class SystemCoherenceAnalyzer:
    """Main analyzer class for system coherence analysis"""
    
    def __init__(self):
        self.systems: List[SystemInfo] = []
        self.conflicts: List[Conflict] = []
        self.duplications: List[Duplication] = []
        self.missing_connections: List[MissingConnection] = []
        self.systems_dir = project_root / "knowledge_architecture" / "systems"
        
    async def load_all_systems(self) -> List[SystemInfo]:
        """Load all systems from L0-L4 documentation"""
        logger.info("Loading all systems from L0-L4 documentation...")
        
        systems = []
        for system_dir in self.systems_dir.iterdir():
            if system_dir.is_dir() and not system_dir.name.startswith('.'):
                system_info = await self.load_system_info(system_dir)
                if system_info:
                    systems.append(system_info)
                    logger.info(f"Loaded system: {system_info.name}")
        
        self.systems = systems
        logger.info(f"Loaded {len(systems)} systems")
        return systems
    
    async def load_system_info(self, system_dir: Path) -> Optional[SystemInfo]:
        """Load system information from L0-L4 documentation"""
        try:
            # Load L0 executive summary
            l0_path = system_dir / "L0_executive.md"
            if not l0_path.exists():
                logger.warning(f"L0 document not found for {system_dir.name}")
                return None
            
            l0_content = l0_path.read_text(encoding='utf-8')
            
            # Load system map
            system_map_path = system_dir / "system.map.lucid.json5"
            system_map = {}
            if system_map_path.exists():
                system_map = json.loads(system_map_path.read_text(encoding='utf-8'))
            
            # Load system index
            system_index_path = system_dir / "system.index.lucid.json5"
            system_index = {}
            if system_index_path.exists():
                system_index = json.loads(system_index_path.read_text(encoding='utf-8'))
            
            # Extract system information
            system_id = system_dir.name
            name = system_map.get('purpose', system_id)
            purpose = l0_content.split('**Purpose:**')[1].split('\n')[0].strip() if '**Purpose:**' in l0_content else name
            
            classification = system_map.get('classification', {})
            tier = classification.get('tier', 1)
            category = classification.get('category', 'unknown')
            type_info = classification.get('type', 'unknown')
            scope = classification.get('scope', 'unknown')
            
            # Extract interfaces from system map
            interfaces = []
            internal_topology = system_map.get('internal_topology', {})
            if 'core_components' in internal_topology:
                for comp_id, comp_info in internal_topology['core_components'].items():
                    if 'ports' in comp_info:
                        for port_name, port_info in comp_info['ports'].items():
                            interfaces.append({
                                'component': comp_id,
                                'port': port_name,
                                'type': port_info.get('type', 'unknown'),
                                'input': port_info.get('input', []),
                                'output': port_info.get('output', [])
                            })
            
            # Extract dependencies
            dependencies = system_map.get('dependencies', {}).get('external', [])
            
            # Extract data models
            data_models = []
            if 'data_models' in internal_topology:
                for model_id, model_info in internal_topology['data_models'].items():
                    data_models.append({
                        'id': model_id,
                        'type': model_info.get('type', 'unknown'),
                        'purpose': model_info.get('purpose', ''),
                        'fields': model_info.get('fields', {})
                    })
            
            # Extract algorithms
            algorithms = []
            if 'algorithms' in internal_topology:
                for algo_id, algo_info in internal_topology['algorithms'].items():
                    algorithms.append({
                        'id': algo_id,
                        'type': algo_info.get('type', 'unknown'),
                        'purpose': algo_info.get('purpose', ''),
                        'method': algo_info.get('method', 'unknown'),
                        'inputs': algo_info.get('inputs', []),
                        'outputs': algo_info.get('outputs', [])
                    })
            
            # Extract configuration
            configuration = system_map.get('configuration', {})
            
            return SystemInfo(
                system_id=system_id,
                name=name,
                purpose=purpose,
                tier=tier,
                category=category,
                type=type_info,
                scope=scope,
                interfaces=interfaces,
                dependencies=dependencies,
                data_models=data_models,
                algorithms=algorithms,
                configuration=configuration,
                l0_doc_path=str(l0_path),
                l1_doc_path=str(system_dir / "L1_overview.md"),
                l2_doc_path=str(system_dir / "L2_architecture.md"),
                l3_doc_path=str(system_dir / "L3_detailed.md"),
                l4_doc_path=str(system_dir / "L4_complete.md"),
                system_map_path=str(system_map_path),
                system_index_path=str(system_index_path),
                usage_envelope_path=str(system_dir / "usage.envelope.md")
            )
            
        except Exception as e:
            logger.error(f"Error loading system {system_dir.name}: {e}")
            return None
    
    async def detect_conflicts(self) -> List[Conflict]:
        """Detect conflicts between systems"""
        logger.info("Detecting conflicts between systems...")
        
        conflicts = []
        
        # API Conflicts
        api_conflicts = await self.detect_api_conflicts()
        conflicts.extend(api_conflicts)
        
        # Data Model Conflicts
        data_conflicts = await self.detect_data_model_conflicts()
        conflicts.extend(data_conflicts)
        
        # Resource Conflicts
        resource_conflicts = await self.detect_resource_conflicts()
        conflicts.extend(resource_conflicts)
        
        # Behavioral Conflicts
        behavioral_conflicts = await self.detect_behavioral_conflicts()
        conflicts.extend(behavioral_conflicts)
        
        # Security Conflicts
        security_conflicts = await self.detect_security_conflicts()
        conflicts.extend(security_conflicts)
        
        self.conflicts = conflicts
        logger.info(f"Found {len(conflicts)} conflicts")
        return conflicts
    
    async def detect_api_conflicts(self) -> List[Conflict]:
        """Detect API conflicts between systems"""
        conflicts = []
        
        # Group systems by API patterns
        api_patterns = {}
        for system in self.systems:
            for interface in system.interfaces:
                if interface['type'] == 'api':
                    pattern = f"{interface.get('method', 'GET')}:{interface.get('path', '')}"
                    if pattern not in api_patterns:
                        api_patterns[pattern] = []
                    api_patterns[pattern].append(system.system_id)
        
        # Find conflicts
        for pattern, systems in api_patterns.items():
            if len(systems) > 1:
                conflicts.append(Conflict(
                    conflict_id=f"api_conflict_{pattern.replace(':', '_').replace('/', '_')}",
                    conflict_type="api_conflict",
                    severity="medium",
                    systems_involved=systems,
                    description=f"Multiple systems use the same API pattern: {pattern}",
                    resolution_suggestions=[
                        "Standardize API patterns across systems",
                        "Use versioning to differentiate APIs",
                        "Consolidate similar APIs into shared services"
                    ],
                    confidence=0.8,
                    timestamp=datetime.now()
                ))
        
        return conflicts
    
    async def detect_data_model_conflicts(self) -> List[Conflict]:
        """Detect data model conflicts between systems"""
        conflicts = []
        
        # Group data models by field names
        field_usage = {}
        for system in self.systems:
            for model in system.data_models:
                for field_name, field_type in model.get('fields', {}).items():
                    if field_name not in field_usage:
                        field_usage[field_name] = []
                    field_usage[field_name].append({
                        'system': system.system_id,
                        'model': model['id'],
                        'type': field_type
                    })
        
        # Find conflicts
        for field_name, usages in field_usage.items():
            if len(usages) > 1:
                # Check for type conflicts
                types = set(usage['type'] for usage in usages)
                if len(types) > 1:
                    systems = list(set(usage['system'] for usage in usages))
                    conflicts.append(Conflict(
                        conflict_id=f"data_model_conflict_{field_name}",
                        conflict_type="data_model_conflict",
                        severity="high",
                        systems_involved=systems,
                        description=f"Field '{field_name}' has conflicting types: {', '.join(types)}",
                        resolution_suggestions=[
                            "Standardize field types across systems",
                            "Use data transformation layers",
                            "Create unified data models"
                        ],
                        confidence=0.9,
                        timestamp=datetime.now()
                    ))
        
        return conflicts
    
    async def detect_resource_conflicts(self) -> List[Conflict]:
        """Detect resource conflicts between systems"""
        conflicts = []
        
        # Check for port conflicts
        port_usage = {}
        for system in self.systems:
            config = system.configuration
            if 'api' in config and 'port' in config['api']:
                port = config['api']['port']
                if port not in port_usage:
                    port_usage[port] = []
                port_usage[port].append(system.system_id)
        
        # Find port conflicts
        for port, systems in port_usage.items():
            if len(systems) > 1:
                conflicts.append(Conflict(
                    conflict_id=f"port_conflict_{port}",
                    conflict_type="resource_conflict",
                    severity="critical",
                    systems_involved=systems,
                    description=f"Multiple systems use the same port: {port}",
                    resolution_suggestions=[
                        "Assign unique ports to each system",
                        "Use port ranges for different system types",
                        "Implement port management system"
                    ],
                    confidence=1.0,
                    timestamp=datetime.now()
                ))
        
        return conflicts
    
    async def detect_behavioral_conflicts(self) -> List[Conflict]:
        """Detect behavioral conflicts between systems"""
        conflicts = []
        
        # Check for conflicting business logic
        logic_patterns = {}
        for system in self.systems:
            for algorithm in system.algorithms:
                if algorithm['type'] == 'business_logic':
                    pattern = algorithm.get('method', '')
                    if pattern not in logic_patterns:
                        logic_patterns[pattern] = []
                    logic_patterns[pattern].append(system.system_id)
        
        # Find conflicts
        for pattern, systems in logic_patterns.items():
            if len(systems) > 1 and pattern:
                conflicts.append(Conflict(
                    conflict_id=f"behavioral_conflict_{pattern}",
                    conflict_type="behavioral_conflict",
                    severity="medium",
                    systems_involved=systems,
                    description=f"Multiple systems use conflicting business logic: {pattern}",
                    resolution_suggestions=[
                        "Standardize business logic across systems",
                        "Create shared business logic services",
                        "Implement business rule engine"
                    ],
                    confidence=0.7,
                    timestamp=datetime.now()
                ))
        
        return conflicts
    
    async def detect_security_conflicts(self) -> List[Conflict]:
        """Detect security conflicts between systems"""
        conflicts = []
        
        # Check for conflicting security models
        security_models = {}
        for system in self.systems:
            config = system.configuration
            if 'security' in config:
                model = config['security'].get('authentication', 'unknown')
                if model not in security_models:
                    security_models[model] = []
                security_models[model].append(system.system_id)
        
        # Find conflicts
        for model, systems in security_models.items():
            if len(systems) > 1 and model != 'unknown':
                conflicts.append(Conflict(
                    conflict_id=f"security_conflict_{model}",
                    conflict_type="security_conflict",
                    severity="high",
                    systems_involved=systems,
                    description=f"Multiple systems use different security models: {model}",
                    resolution_suggestions=[
                        "Standardize security models across systems",
                        "Implement unified authentication system",
                        "Use security gateway for authentication"
                    ],
                    confidence=0.8,
                    timestamp=datetime.now()
                ))
        
        return conflicts
    
    async def detect_duplications(self) -> List[Duplication]:
        """Detect duplications between systems"""
        logger.info("Detecting duplications between systems...")
        
        duplications = []
        
        # Functional Duplication
        func_duplications = await self.detect_functional_duplications()
        duplications.extend(func_duplications)
        
        # Data Duplication
        data_duplications = await self.detect_data_duplications()
        duplications.extend(data_duplications)
        
        # Interface Duplication
        interface_duplications = await self.detect_interface_duplications()
        duplications.extend(interface_duplications)
        
        # Logic Duplication
        logic_duplications = await self.detect_logic_duplications()
        duplications.extend(logic_duplications)
        
        self.duplications = duplications
        logger.info(f"Found {len(duplications)} duplications")
        return duplications
    
    async def detect_functional_duplications(self) -> List[Duplication]:
        """Detect functional duplications between systems"""
        duplications = []
        
        # Group systems by purpose similarity
        purpose_groups = {}
        for system in self.systems:
            purpose_key = system.purpose.lower().replace(' ', '_')
            if purpose_key not in purpose_groups:
                purpose_groups[purpose_key] = []
            purpose_groups[purpose_key].append(system.system_id)
        
        # Find duplications
        for purpose_key, systems in purpose_groups.items():
            if len(systems) > 1:
                duplications.append(Duplication(
                    duplication_id=f"functional_duplication_{purpose_key}",
                    duplication_type="functional_duplication",
                    systems_involved=systems,
                    description=f"Multiple systems have similar purposes: {purpose_key}",
                    consolidation_suggestions=[
                        "Consolidate similar systems into unified components",
                        "Create shared service layer",
                        "Implement system specialization"
                    ],
                    confidence=0.8,
                    timestamp=datetime.now()
                ))
        
        return duplications
    
    async def detect_data_duplications(self) -> List[Duplication]:
        """Detect data duplications between systems"""
        duplications = []
        
        # Group data models by similarity
        model_groups = {}
        for system in self.systems:
            for model in system.data_models:
                model_key = f"{model['id']}_{len(model.get('fields', {}))}"
                if model_key not in model_groups:
                    model_groups[model_key] = []
                model_groups[model_key].append({
                    'system': system.system_id,
                    'model': model
                })
        
        # Find duplications
        for model_key, usages in model_groups.items():
            if len(usages) > 1:
                systems = [usage['system'] for usage in usages]
                duplications.append(Duplication(
                    duplication_id=f"data_duplication_{model_key}",
                    duplication_type="data_duplication",
                    systems_involved=systems,
                    description=f"Multiple systems have similar data models: {model_key}",
                    consolidation_suggestions=[
                        "Create shared data models",
                        "Implement data transformation layers",
                        "Use common data access layer"
                    ],
                    confidence=0.7,
                    timestamp=datetime.now()
                ))
        
        return duplications
    
    async def detect_interface_duplications(self) -> List[Duplication]:
        """Detect interface duplications between systems"""
        duplications = []
        
        # Group interfaces by similarity
        interface_groups = {}
        for system in self.systems:
            for interface in system.interfaces:
                interface_key = f"{interface.get('type', 'unknown')}_{len(interface.get('input', []))}_{len(interface.get('output', []))}"
                if interface_key not in interface_groups:
                    interface_groups[interface_key] = []
                interface_groups[interface_key].append({
                    'system': system.system_id,
                    'interface': interface
                })
        
        # Find duplications
        for interface_key, usages in interface_groups.items():
            if len(usages) > 1:
                systems = [usage['system'] for usage in usages]
                duplications.append(Duplication(
                    duplication_id=f"interface_duplication_{interface_key}",
                    duplication_type="interface_duplication",
                    systems_involved=systems,
                    description=f"Multiple systems have similar interfaces: {interface_key}",
                    consolidation_suggestions=[
                        "Standardize interfaces across systems",
                        "Create shared interface libraries",
                        "Implement interface versioning"
                    ],
                    confidence=0.6,
                    timestamp=datetime.now()
                ))
        
        return duplications
    
    async def detect_logic_duplications(self) -> List[Duplication]:
        """Detect logic duplications between systems"""
        duplications = []
        
        # Group algorithms by similarity
        algorithm_groups = {}
        for system in self.systems:
            for algorithm in system.algorithms:
                algo_key = f"{algorithm.get('type', 'unknown')}_{algorithm.get('method', 'unknown')}"
                if algo_key not in algorithm_groups:
                    algorithm_groups[algo_key] = []
                algorithm_groups[algo_key].append({
                    'system': system.system_id,
                    'algorithm': algorithm
                })
        
        # Find duplications
        for algo_key, usages in algorithm_groups.items():
            if len(usages) > 1:
                systems = [usage['system'] for usage in usages]
                duplications.append(Duplication(
                    duplication_id=f"logic_duplication_{algo_key}",
                    duplication_type="logic_duplication",
                    systems_involved=systems,
                    description=f"Multiple systems have similar algorithms: {algo_key}",
                    consolidation_suggestions=[
                        "Create shared algorithm libraries",
                        "Implement common processing services",
                        "Use algorithm composition patterns"
                    ],
                    confidence=0.7,
                    timestamp=datetime.now()
                ))
        
        return duplications
    
    async def detect_missing_connections(self) -> List[MissingConnection]:
        """Detect missing connections between systems"""
        logger.info("Detecting missing connections between systems...")
        
        missing_connections = []
        
        # Missing Dependencies
        missing_deps = await self.detect_missing_dependencies()
        missing_connections.extend(missing_deps)
        
        # Orphaned Systems
        orphaned = await self.detect_orphaned_systems()
        missing_connections.extend(orphaned)
        
        # Circular Dependencies
        circular = await self.detect_circular_dependencies()
        missing_connections.extend(circular)
        
        # Missing Interfaces
        missing_interfaces = await self.detect_missing_interfaces()
        missing_connections.extend(missing_interfaces)
        
        self.missing_connections = missing_connections
        logger.info(f"Found {len(missing_connections)} missing connections")
        return missing_connections
    
    async def detect_missing_dependencies(self) -> List[MissingConnection]:
        """Detect missing dependencies between systems"""
        missing_connections = []
        
        # Check for systems that should depend on each other
        for system in self.systems:
            for other_system in self.systems:
                if system.system_id != other_system.system_id:
                    # Check if systems should be connected based on purpose similarity
                    if self.should_be_connected(system, other_system):
                        if other_system.system_id not in system.dependencies:
                            missing_connections.append(MissingConnection(
                                connection_id=f"missing_dependency_{system.system_id}_{other_system.system_id}",
                                connection_type="missing_dependency",
                                systems_involved=[system.system_id, other_system.system_id],
                                description=f"System {system.system_id} should depend on {other_system.system_id}",
                                integration_suggestions=[
                                    f"Add {other_system.system_id} to {system.system_id} dependencies",
                                    f"Create interface between {system.system_id} and {other_system.system_id}",
                                    f"Implement data flow between {system.system_id} and {other_system.system_id}"
                                ],
                                confidence=0.6,
                                timestamp=datetime.now()
                            ))
        
        return missing_connections
    
    async def detect_orphaned_systems(self) -> List[MissingConnection]:
        """Detect orphaned systems with no connections"""
        missing_connections = []
        
        for system in self.systems:
            if not system.dependencies and not self.has_outgoing_connections(system):
                missing_connections.append(MissingConnection(
                    connection_id=f"orphaned_system_{system.system_id}",
                    connection_type="orphaned_system",
                    systems_involved=[system.system_id],
                    description=f"System {system.system_id} appears to be orphaned with no connections",
                    integration_suggestions=[
                        f"Connect {system.system_id} to other systems",
                        f"Add {system.system_id} to system integration map",
                        f"Create interfaces for {system.system_id}"
                    ],
                    confidence=0.8,
                    timestamp=datetime.now()
                ))
        
        return missing_connections
    
    async def detect_circular_dependencies(self) -> List[MissingConnection]:
        """Detect circular dependencies between systems"""
        missing_connections = []
        
        # Build dependency graph
        dependency_graph = {}
        for system in self.systems:
            dependency_graph[system.system_id] = system.dependencies
        
        # Check for cycles
        visited = set()
        rec_stack = set()
        
        def has_cycle(system_id):
            if system_id in rec_stack:
                return True
            if system_id in visited:
                return False
            
            visited.add(system_id)
            rec_stack.add(system_id)
            
            for dep in dependency_graph.get(system_id, []):
                if has_cycle(dep):
                    return True
            
            rec_stack.remove(system_id)
            return False
        
        for system in self.systems:
            if has_cycle(system.system_id):
                missing_connections.append(MissingConnection(
                    connection_id=f"circular_dependency_{system.system_id}",
                    connection_type="circular_dependency",
                    systems_involved=[system.system_id],
                    description=f"System {system.system_id} has circular dependencies",
                    integration_suggestions=[
                        f"Break circular dependency for {system.system_id}",
                        f"Refactor dependency structure for {system.system_id}",
                        f"Use dependency injection for {system.system_id}"
                    ],
                    confidence=0.9,
                    timestamp=datetime.now()
                ))
        
        return missing_connections
    
    async def detect_missing_interfaces(self) -> List[MissingConnection]:
        """Detect missing interfaces between systems"""
        missing_connections = []
        
        # Check for systems that should have interfaces but don't
        for system in self.systems:
            if not system.interfaces and system.tier > 0:
                missing_connections.append(MissingConnection(
                    connection_id=f"missing_interface_{system.system_id}",
                    connection_type="missing_interface",
                    systems_involved=[system.system_id],
                    description=f"System {system.system_id} has no interfaces defined",
                    integration_suggestions=[
                        f"Define interfaces for {system.system_id}",
                        f"Create API specification for {system.system_id}",
                        f"Add interface documentation for {system.system_id}"
                    ],
                    confidence=0.7,
                    timestamp=datetime.now()
                ))
        
        return missing_connections
    
    def should_be_connected(self, system1: SystemInfo, system2: SystemInfo) -> bool:
        """Determine if two systems should be connected"""
        # Check for purpose similarity
        purpose1 = system1.purpose.lower()
        purpose2 = system2.purpose.lower()
        
        # Common keywords that suggest connection
        connection_keywords = [
            'memory', 'storage', 'data', 'database',
            'api', 'interface', 'service', 'client',
            'monitor', 'analysis', 'detection', 'audit',
            'security', 'authentication', 'authorization',
            'performance', 'metrics', 'logging', 'alerting'
        ]
        
        for keyword in connection_keywords:
            if keyword in purpose1 and keyword in purpose2:
                return True
        
        # Check for tier compatibility
        if system1.tier == 1 and system2.tier > 1:  # Core system should connect to higher tier
            return True
        
        return False
    
    def has_outgoing_connections(self, system: SystemInfo) -> bool:
        """Check if system has outgoing connections"""
        # Check if other systems depend on this system
        for other_system in self.systems:
            if other_system.system_id != system.system_id:
                if system.system_id in other_system.dependencies:
                    return True
        return False
    
    async def generate_coherence_report(self) -> CoherenceReport:
        """Generate comprehensive coherence analysis report"""
        logger.info("Generating coherence analysis report...")
        
        # Generate recommendations
        recommendations = []
        
        # Conflict recommendations
        if self.conflicts:
            recommendations.append(f"Resolve {len(self.conflicts)} conflicts found between systems")
            for conflict in self.conflicts:
                recommendations.extend(conflict.resolution_suggestions)
        
        # Duplication recommendations
        if self.duplications:
            recommendations.append(f"Eliminate {len(self.duplications)} duplications found between systems")
            for duplication in self.duplications:
                recommendations.extend(duplication.consolidation_suggestions)
        
        # Missing connection recommendations
        if self.missing_connections:
            recommendations.append(f"Add {len(self.missing_connections)} missing connections between systems")
            for connection in self.missing_connections:
                recommendations.extend(connection.integration_suggestions)
        
        # Generate implementation roadmap
        implementation_roadmap = {
            "phase_1": {
                "name": "Critical Issues Resolution",
                "duration": "2 weeks",
                "tasks": [
                    "Resolve critical conflicts",
                    "Eliminate high-priority duplications",
                    "Add critical missing connections"
                ]
            },
            "phase_2": {
                "name": "System Integration",
                "duration": "2 weeks",
                "tasks": [
                    "Complete system integration",
                    "Implement missing interfaces",
                    "Validate system coherence"
                ]
            },
            "phase_3": {
                "name": "Optimization and Testing",
                "duration": "1 week",
                "tasks": [
                    "Performance optimization",
                    "Comprehensive testing",
                    "Documentation updates"
                ]
            }
        }
        
        report = CoherenceReport(
            report_id=f"coherence_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.now(),
            systems_analyzed=len(self.systems),
            conflicts_found=len(self.conflicts),
            duplications_found=len(self.duplications),
            missing_connections_found=len(self.missing_connections),
            conflicts=self.conflicts,
            duplications=self.duplications,
            missing_connections=self.missing_connections,
            recommendations=recommendations,
            implementation_roadmap=implementation_roadmap
        )
        
        logger.info("Coherence analysis report generated")
        return report
    
    async def save_report(self, report: CoherenceReport, output_dir: Path):
        """Save coherence report to files"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save JSON report
        json_path = output_dir / f"{report.report_id}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(report), f, indent=2, default=str)
        
        # Save Markdown report
        md_path = output_dir / f"{report.report_id}.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(f"# System Coherence Analysis Report\n\n")
            f.write(f"**Report ID:** {report.report_id}\n")
            f.write(f"**Generated:** {report.timestamp}\n")
            f.write(f"**Systems Analyzed:** {report.systems_analyzed}\n\n")
            
            f.write(f"## Summary\n\n")
            f.write(f"- **Conflicts Found:** {report.conflicts_found}\n")
            f.write(f"- **Duplications Found:** {report.duplications_found}\n")
            f.write(f"- **Missing Connections Found:** {report.missing_connections_found}\n\n")
            
            if report.conflicts:
                f.write(f"## Conflicts\n\n")
                for conflict in report.conflicts:
                    f.write(f"### {conflict.conflict_id}\n")
                    f.write(f"**Type:** {conflict.conflict_type}\n")
                    f.write(f"**Severity:** {conflict.severity}\n")
                    f.write(f"**Systems:** {', '.join(conflict.systems_involved)}\n")
                    f.write(f"**Description:** {conflict.description}\n")
                    f.write(f"**Suggestions:**\n")
                    for suggestion in conflict.resolution_suggestions:
                        f.write(f"- {suggestion}\n")
                    f.write(f"\n")
            
            if report.duplications:
                f.write(f"## Duplications\n\n")
                for duplication in report.duplications:
                    f.write(f"### {duplication.duplication_id}\n")
                    f.write(f"**Type:** {duplication.duplication_type}\n")
                    f.write(f"**Systems:** {', '.join(duplication.systems_involved)}\n")
                    f.write(f"**Description:** {duplication.description}\n")
                    f.write(f"**Suggestions:**\n")
                    for suggestion in duplication.consolidation_suggestions:
                        f.write(f"- {suggestion}\n")
                    f.write(f"\n")
            
            if report.missing_connections:
                f.write(f"## Missing Connections\n\n")
                for connection in report.missing_connections:
                    f.write(f"### {connection.connection_id}\n")
                    f.write(f"**Type:** {connection.connection_type}\n")
                    f.write(f"**Systems:** {', '.join(connection.systems_involved)}\n")
                    f.write(f"**Description:** {connection.description}\n")
                    f.write(f"**Suggestions:**\n")
                    for suggestion in connection.integration_suggestions:
                        f.write(f"- {suggestion}\n")
                    f.write(f"\n")
            
            f.write(f"## Implementation Roadmap\n\n")
            for phase_id, phase in report.implementation_roadmap.items():
                f.write(f"### {phase['name']}\n")
                f.write(f"**Duration:** {phase['duration']}\n")
                f.write(f"**Tasks:**\n")
                for task in phase['tasks']:
                    f.write(f"- {task}\n")
                f.write(f"\n")
        
        logger.info(f"Report saved to {output_dir}")
        return json_path, md_path

async def main():
    """Main function to run system coherence analysis"""
    logger.info("Starting System Coherence Analysis...")
    
    # Create analyzer
    analyzer = SystemCoherenceAnalyzer()
    
    try:
        # Load all systems
        systems = await analyzer.load_all_systems()
        if not systems:
            logger.error("No systems found to analyze")
            return
        
        # Detect conflicts
        conflicts = await analyzer.detect_conflicts()
        
        # Detect duplications
        duplications = await analyzer.detect_duplications()
        
        # Detect missing connections
        missing_connections = await analyzer.detect_missing_connections()
        
        # Generate report
        report = await analyzer.generate_coherence_report()
        
        # Save report
        output_dir = project_root / "knowledge_architecture" / "reports" / "coherence_analysis"
        json_path, md_path = await analyzer.save_report(report, output_dir)
        
        logger.info(f"System Coherence Analysis completed successfully!")
        logger.info(f"Report saved to: {json_path} and {md_path}")
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"SYSTEM COHERENCE ANALYSIS SUMMARY")
        print(f"{'='*60}")
        print(f"Systems Analyzed: {report.systems_analyzed}")
        print(f"Conflicts Found: {report.conflicts_found}")
        print(f"Duplications Found: {report.duplications_found}")
        print(f"Missing Connections Found: {report.missing_connections_found}")
        print(f"Report ID: {report.report_id}")
        print(f"Report Files: {json_path}, {md_path}")
        print(f"{'='*60}\n")
        
    except Exception as e:
        logger.error(f"Error during analysis: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
