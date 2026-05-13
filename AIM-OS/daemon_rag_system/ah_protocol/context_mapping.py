"""
Context Mapping System - Step C of A-H Protocol

This module implements the Context Mapping step, which is responsible for:
- Mapping the broader context and dependencies
- Creating comprehensive context maps showing relationships
- Identifying external dependencies and constraints
- Documenting user workflows and touchpoints
- Noting political or organizational considerations

Following A-H Protocol methodology from ChatGPT journal.
"""

from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import json
import time
import networkx as nx
from .intent_capture import IntentProfile
from .hypothesis_formation import Hypothesis

class DependencyType(Enum):
    """Types of dependencies between context nodes."""
    HARD_DEPENDENCY = "hard_dependency"  # Required for functionality
    SOFT_DEPENDENCY = "soft_dependency"  # Nice to have, not critical
    CONFLICT = "conflict"  # Cannot coexist
    OPTIONAL = "optional"  # May be useful but not required
    BLOCKING = "blocking"  # Prevents progress if not available
    FACILITATING = "facilitating"  # Makes things easier but not required

@dataclass
class ContextNode:
    """A node in the context map representing a system, component, or entity."""
    id: str
    name: str
    type: str
    description: str
    dependencies: List[str]  # IDs of nodes this depends on
    dependents: List[str]  # IDs of nodes that depend on this
    constraints: List[str]
    resources_required: Dict[str, Any]
    impact_level: int  # 0-3 scale
    criticality: str  # "critical", "high", "medium", "low"
    availability: str  # "available", "unavailable", "partial", "unknown"
    owner: str
    last_updated: float
    version: str = "1.0"

@dataclass
class ContextRelationship:
    """A relationship between two context nodes."""
    from_node: str
    to_node: str
    relationship_type: DependencyType
    strength: float  # 0.0-1.0
    description: str
    constraints: List[str]
    risks: List[str]
    mitigation_strategies: List[str]

@dataclass
class ContextMap:
    """Complete context map with nodes, relationships, and analysis."""
    id: str
    name: str
    nodes: Dict[str, ContextNode]
    relationships: List[ContextRelationship]
    critical_paths: List[List[str]]
    risk_factors: List[str]
    mitigation_strategies: List[str]
    external_dependencies: List[str]
    organizational_factors: List[str]
    user_workflows: List[Dict[str, Any]]
    created_at: float
    updated_at: float
    version: str = "1.0"

class ContextMapping:
    """
    Context Mapping System for A-H Protocol Step C.
    
    Creates comprehensive context maps showing relationships and dependencies
    for the captured intent and generated hypotheses.
    """
    
    def __init__(self, config_path: str = "context_mapping_config.json"):
        """Initialize the Context Mapping system."""
        self.config = self._load_config(config_path)
        self.system_registry = self._load_system_registry()
        self.dependency_patterns = self._load_dependency_patterns()
        self.risk_patterns = self._load_risk_patterns()
        self.organizational_patterns = self._load_organizational_patterns()
        
    def map_context(self, intent_profile: IntentProfile, hypotheses: List[Hypothesis], 
                   context: Dict[str, Any] = None) -> ContextMap:
        """
        Create comprehensive context map for the intent and hypotheses.
        
        Args:
            intent_profile: The captured intent profile
            hypotheses: List of generated hypotheses
            context: Additional context data
            
        Returns:
            ContextMap: Complete context map with analysis
        """
        if context is None:
            context = {}
            
        map_id = f"context_map_{int(time.time())}"
        
        # Identify all relevant systems and components
        relevant_systems = self._identify_relevant_systems(intent_profile, hypotheses, context)
        
        # Map dependencies and relationships
        relationships = self._map_relationships(relevant_systems, intent_profile, context)
        
        # Identify critical paths
        critical_paths = self._identify_critical_paths(relevant_systems, relationships)
        
        # Assess risk factors
        risk_factors = self._assess_risk_factors(relevant_systems, relationships, intent_profile)
        
        # Generate mitigation strategies
        mitigation_strategies = self._generate_mitigation_strategies(risk_factors, relevant_systems)
        
        # Identify external dependencies
        external_dependencies = self._identify_external_dependencies(relevant_systems, context)
        
        # Identify organizational factors
        organizational_factors = self._identify_organizational_factors(intent_profile, context)
        
        # Document user workflows
        user_workflows = self._document_user_workflows(intent_profile, relevant_systems, context)
        
        return ContextMap(
            id=map_id,
            name=f"Context Map for {intent_profile.intent_type.value}",
            nodes=relevant_systems,
            relationships=relationships,
            critical_paths=critical_paths,
            risk_factors=risk_factors,
            mitigation_strategies=mitigation_strategies,
            external_dependencies=external_dependencies,
            organizational_factors=organizational_factors,
            user_workflows=user_workflows,
            created_at=time.time(),
            updated_at=time.time()
        )
    
    def _identify_relevant_systems(self, intent_profile: IntentProfile, 
                                 hypotheses: List[Hypothesis], 
                                 context: Dict[str, Any]) -> Dict[str, ContextNode]:
        """Identify all systems relevant to the intent and hypotheses."""
        systems = {}
        
        # Add systems from intent profile
        if "active_project" in intent_profile.context_data:
            project = intent_profile.context_data["active_project"]
            systems[f"project_{project}"] = ContextNode(
                id=f"project_{project}",
                name=f"Project {project}",
                type="project",
                description=f"Main project context: {project}",
                dependencies=[],
                dependents=[],
                constraints=intent_profile.constraints,
                resources_required={"cpu": "medium", "memory": "medium", "storage": "medium"},
                impact_level=3,
                criticality="critical",
                availability="available",
                owner="project_owner",
                last_updated=time.time()
            )
        
        # Add systems from hypotheses
        for hypothesis in hypotheses:
            for dep in hypothesis.dependencies:
                if dep not in systems:
                    systems[dep] = self._create_system_node(dep, "hypothesis_dependency")
        
        # Add systems from context
        if "open_files" in context:
            for file_path in context["open_files"]:
                system_name = self._extract_system_from_path(file_path)
                if system_name and system_name not in systems:
                    systems[system_name] = self._create_system_node(system_name, "file_system")
        
        # Add LUCID systems (always relevant for AIM-OS)
        lucid_systems = [
            "L0_L4_Documentation",
            "A_H_Protocol",
            "Confidence_Gated_Controls",
            "Context_Mesh_Maps",
            "Deep_Expansion_Layer",
            "Dynamic_Cursor_Rules",
            "Daemon_RAG_System"
        ]
        
        for system in lucid_systems:
            if system not in systems:
                systems[system] = self._create_system_node(system, "lucid_system")
        
        # Add external systems based on intent type
        external_systems = self._identify_external_systems(intent_profile)
        for system in external_systems:
            if system not in systems:
                systems[system] = self._create_system_node(system, "external_system")
        
        return systems
    
    def _create_system_node(self, system_name: str, system_type: str) -> ContextNode:
        """Create a context node for a system."""
        # Determine criticality and impact based on system type
        criticality_map = {
            "project": "critical",
            "lucid_system": "high",
            "hypothesis_dependency": "medium",
            "file_system": "low",
            "external_system": "medium"
        }
        
        impact_map = {
            "project": 3,
            "lucid_system": 2,
            "hypothesis_dependency": 1,
            "file_system": 0,
            "external_system": 1
        }
        
        return ContextNode(
            id=system_name.lower().replace(" ", "_"),
            name=system_name,
            type=system_type,
            description=f"System: {system_name}",
            dependencies=[],
            dependents=[],
            constraints=[],
            resources_required={"cpu": "low", "memory": "low", "storage": "low"},
            impact_level=impact_map.get(system_type, 1),
            criticality=criticality_map.get(system_type, "medium"),
            availability="available",
            owner="system_owner",
            last_updated=time.time()
        )
    
    def _extract_system_from_path(self, file_path: str) -> Optional[str]:
        """Extract system name from file path."""
        # Extract system name from common path patterns
        if "daemon_rag_system" in file_path:
            return "Daemon_RAG_System"
        elif "ah_protocol" in file_path:
            return "A_H_Protocol"
        elif "l0_l4" in file_path.lower():
            return "L0_L4_Documentation"
        elif "dynamic_cursor_rules" in file_path:
            return "Dynamic_Cursor_Rules"
        elif "knowledge_architecture" in file_path:
            return "Knowledge_Architecture"
        return None
    
    def _identify_external_systems(self, intent_profile: IntentProfile) -> List[str]:
        """Identify external systems based on intent type."""
        external_systems = []
        
        if intent_profile.intent_type.value == "feature_development":
            external_systems.extend([
                "Development_Environment",
                "Version_Control_System",
                "CI_CD_Pipeline",
                "Testing_Framework"
            ])
        elif intent_profile.intent_type.value == "bug_fix":
            external_systems.extend([
                "Debugging_Tools",
                "Logging_System",
                "Monitoring_System"
            ])
        elif intent_profile.intent_type.value == "protocol_implementation":
            external_systems.extend([
                "Protocol_Specification",
                "Compliance_Framework",
                "Validation_System"
            ])
        
        return external_systems
    
    def _map_relationships(self, systems: Dict[str, ContextNode], 
                         intent_profile: IntentProfile, 
                         context: Dict[str, Any]) -> List[ContextRelationship]:
        """Map relationships between systems."""
        relationships = []
        
        # Create a graph to analyze dependencies
        G = nx.DiGraph()
        for system_id, system in systems.items():
            G.add_node(system_id, **system.__dict__)
        
        # Add relationships based on system types and dependencies
        for system_id, system in systems.items():
            # LUCID systems have specific relationships
            if system.type == "lucid_system":
                relationships.extend(self._map_lucid_relationships(system_id, systems))
            elif system.type == "project":
                relationships.extend(self._map_project_relationships(system_id, systems))
            elif system.type == "hypothesis_dependency":
                relationships.extend(self._map_hypothesis_relationships(system_id, systems))
        
        # Add relationships based on intent type
        relationships.extend(self._map_intent_relationships(intent_profile, systems))
        
        # Add relationships based on context
        relationships.extend(self._map_context_relationships(context, systems))
        
        return relationships
    
    def _map_lucid_relationships(self, system_id: str, systems: Dict[str, ContextNode]) -> List[ContextRelationship]:
        """Map relationships for LUCID systems."""
        relationships = []
        
        lucid_dependencies = {
            "A_H_Protocol": ["L0_L4_Documentation", "Confidence_Gated_Controls"],
            "L0_L4_Documentation": ["Knowledge_Architecture"],
            "Confidence_Gated_Controls": ["A_H_Protocol"],
            "Context_Mesh_Maps": ["A_H_Protocol", "Deep_Expansion_Layer"],
            "Deep_Expansion_Layer": ["A_H_Protocol"],
            "Dynamic_Cursor_Rules": ["L0_L4_Documentation", "A_H_Protocol"],
            "Daemon_RAG_System": ["A_H_Protocol", "Context_Mesh_Maps"]
        }
        
        if system_id in lucid_dependencies:
            for dep in lucid_dependencies[system_id]:
                if dep in systems:
                    relationships.append(ContextRelationship(
                        from_node=system_id,
                        to_node=dep,
                        relationship_type=DependencyType.HARD_DEPENDENCY,
                        strength=0.9,
                        description=f"{system_id} depends on {dep}",
                        constraints=[],
                        risks=["dependency_unavailable"],
                        mitigation_strategies=["ensure_dependency_availability"]
                    ))
        
        return relationships
    
    def _map_project_relationships(self, system_id: str, systems: Dict[str, ContextNode]) -> List[ContextRelationship]:
        """Map relationships for project systems."""
        relationships = []
        
        # Project depends on all LUCID systems
        for other_id, other_system in systems.items():
            if other_system.type == "lucid_system":
                relationships.append(ContextRelationship(
                    from_node=system_id,
                    to_node=other_id,
                    relationship_type=DependencyType.HARD_DEPENDENCY,
                    strength=0.8,
                    description=f"Project depends on {other_id}",
                    constraints=[],
                    risks=["lucid_system_unavailable"],
                    mitigation_strategies=["maintain_lucid_system_availability"]
                ))
        
        return relationships
    
    def _map_hypothesis_relationships(self, system_id: str, systems: Dict[str, ContextNode]) -> List[ContextRelationship]:
        """Map relationships for hypothesis dependencies."""
        relationships = []
        
        # Hypothesis dependencies typically depend on LUCID systems
        for other_id, other_system in systems.items():
            if other_system.type == "lucid_system":
                relationships.append(ContextRelationship(
                    from_node=system_id,
                    to_node=other_id,
                    relationship_type=DependencyType.SOFT_DEPENDENCY,
                    strength=0.6,
                    description=f"{system_id} benefits from {other_id}",
                    constraints=[],
                    risks=["dependency_unavailable"],
                    mitigation_strategies=["find_alternative_dependencies"]
                ))
        
        return relationships
    
    def _map_intent_relationships(self, intent_profile: IntentProfile, systems: Dict[str, ContextNode]) -> List[ContextRelationship]:
        """Map relationships based on intent type."""
        relationships = []
        
        if intent_profile.intent_type.value == "protocol_implementation":
            # Protocol implementation depends heavily on A-H Protocol
            if "A_H_Protocol" in systems:
                relationships.append(ContextRelationship(
                    from_node="protocol_implementation",
                    to_node="A_H_Protocol",
                    relationship_type=DependencyType.HARD_DEPENDENCY,
                    strength=1.0,
                    description="Protocol implementation requires A-H Protocol",
                    constraints=["protocol_must_be_complete"],
                    risks=["protocol_incomplete"],
                    mitigation_strategies=["complete_protocol_first"]
                ))
        
        return relationships
    
    def _map_context_relationships(self, context: Dict[str, Any], systems: Dict[str, ContextNode]) -> List[ContextRelationship]:
        """Map relationships based on context data."""
        relationships = []
        
        # Add relationships based on open files
        if "open_files" in context:
            for file_path in context["open_files"]:
                system_name = self._extract_system_from_path(file_path)
                if system_name and system_name in systems:
                    # File system depends on the system it belongs to
                    relationships.append(ContextRelationship(
                        from_node=f"file_{system_name.lower()}",
                        to_node=system_name,
                        relationship_type=DependencyType.HARD_DEPENDENCY,
                        strength=0.9,
                        description=f"File system depends on {system_name}",
                        constraints=[],
                        risks=["system_unavailable"],
                        mitigation_strategies=["maintain_system_availability"]
                    ))
        
        return relationships
    
    def _identify_critical_paths(self, systems: Dict[str, ContextNode], 
                               relationships: List[ContextRelationship]) -> List[List[str]]:
        """Identify critical paths through the system."""
        critical_paths = []
        
        # Create a graph for path analysis
        G = nx.DiGraph()
        for system_id in systems:
            G.add_node(system_id)
        
        for rel in relationships:
            if rel.relationship_type in [DependencyType.HARD_DEPENDENCY, DependencyType.BLOCKING]:
                G.add_edge(rel.from_node, rel.to_node, weight=rel.strength)
        
        # Find critical paths (longest paths with high impact)
        high_impact_systems = [s_id for s_id, s in systems.items() if s.impact_level >= 2]
        
        for start_system in high_impact_systems:
            for end_system in high_impact_systems:
                if start_system != end_system:
                    try:
                        path = nx.shortest_path(G, start_system, end_system)
                        if len(path) > 1:  # Only consider paths with dependencies
                            critical_paths.append(path)
                    except nx.NetworkXNoPath:
                        pass
        
        # Remove duplicate paths and sort by length
        unique_paths = []
        for path in critical_paths:
            if path not in unique_paths:
                unique_paths.append(path)
        
        return sorted(unique_paths, key=len, reverse=True)
    
    def _assess_risk_factors(self, systems: Dict[str, ContextNode], 
                           relationships: List[ContextRelationship],
                           intent_profile: IntentProfile) -> List[str]:
        """Assess risk factors in the context map."""
        risks = []
        
        # System availability risks
        unavailable_systems = [s_id for s_id, s in systems.items() if s.availability != "available"]
        if unavailable_systems:
            risks.append(f"Unavailable systems: {', '.join(unavailable_systems)}")
        
        # High dependency risks
        high_dependency_systems = []
        for system_id, system in systems.items():
            if len(system.dependencies) > 3:
                high_dependency_systems.append(system_id)
        
        if high_dependency_systems:
            risks.append(f"High dependency systems: {', '.join(high_dependency_systems)}")
        
        # Critical path risks
        if len(self._identify_critical_paths(systems, relationships)) > 5:
            risks.append("Complex critical paths increase failure risk")
        
        # Intent-specific risks
        if intent_profile.urgency_level == "high":
            risks.append("High urgency increases implementation risk")
        
        if intent_profile.complexity_score > 0.7:
            risks.append("High complexity increases implementation risk")
        
        # Resource risks
        high_resource_systems = [s_id for s_id, s in systems.items() 
                               if s.resources_required.get("cpu") == "high" or 
                                  s.resources_required.get("memory") == "high"]
        if high_resource_systems:
            risks.append(f"High resource requirements: {', '.join(high_resource_systems)}")
        
        return risks
    
    def _generate_mitigation_strategies(self, risk_factors: List[str], 
                                      systems: Dict[str, ContextNode]) -> List[str]:
        """Generate mitigation strategies for identified risks."""
        strategies = []
        
        for risk in risk_factors:
            if "Unavailable systems" in risk:
                strategies.append("Implement fallback systems for critical dependencies")
                strategies.append("Create alternative implementation paths")
            elif "High dependency" in risk:
                strategies.append("Reduce system coupling through abstraction layers")
                strategies.append("Implement dependency injection patterns")
            elif "Complex critical paths" in risk:
                strategies.append("Simplify system architecture")
                strategies.append("Break down complex dependencies")
            elif "High urgency" in risk:
                strategies.append("Implement risk mitigation checkpoints")
                strategies.append("Prepare rollback procedures")
            elif "High complexity" in risk:
                strategies.append("Break down into smaller, manageable components")
                strategies.append("Implement comprehensive testing")
            elif "High resource requirements" in risk:
                strategies.append("Optimize resource usage")
                strategies.append("Implement resource monitoring and scaling")
        
        # Add general mitigation strategies
        strategies.extend([
            "Implement comprehensive monitoring and alerting",
            "Create detailed documentation and runbooks",
            "Establish regular backup and recovery procedures",
            "Conduct regular risk assessments and reviews"
        ])
        
        return strategies
    
    def _identify_external_dependencies(self, systems: Dict[str, ContextNode], 
                                      context: Dict[str, Any]) -> List[str]:
        """Identify external dependencies."""
        external_deps = []
        
        # Add external systems
        for system_id, system in systems.items():
            if system.type == "external_system":
                external_deps.append(system.name)
        
        # Add context-based external dependencies
        if "active_project" in context:
            external_deps.append(f"Project infrastructure for {context['active_project']}")
        
        # Add common external dependencies
        external_deps.extend([
            "Internet connectivity",
            "Development tools and IDEs",
            "Version control systems",
            "CI/CD pipelines",
            "Testing frameworks",
            "Documentation systems"
        ])
        
        return external_deps
    
    def _identify_organizational_factors(self, intent_profile: IntentProfile, 
                                       context: Dict[str, Any]) -> List[str]:
        """Identify organizational factors."""
        factors = []
        
        # Stakeholder factors
        for stakeholder in intent_profile.primary_stakeholders:
            factors.append(f"Stakeholder requirements: {stakeholder}")
        
        # Constraint factors
        for constraint in intent_profile.constraints:
            factors.append(f"Organizational constraint: {constraint}")
        
        # Project factors
        if "active_project" in context:
            factors.append(f"Project context: {context['active_project']}")
        
        # General organizational factors
        factors.extend([
            "LUCID Development Protocol compliance requirements",
            "AIM-OS architecture standards",
            "Quality assurance processes",
            "Documentation standards",
            "Testing requirements"
        ])
        
        return factors
    
    def _document_user_workflows(self, intent_profile: IntentProfile, 
                               systems: Dict[str, ContextNode], 
                               context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Document user workflows."""
        workflows = []
        
        # Primary workflow based on intent type
        primary_workflow = {
            "name": f"Primary workflow for {intent_profile.intent_type.value}",
            "steps": [
                "Capture intent and requirements",
                "Generate hypotheses",
                "Map context and dependencies",
                "Execute implementation",
                "Validate and test",
                "Document and deliver"
            ],
            "stakeholders": intent_profile.primary_stakeholders,
            "systems_involved": list(systems.keys()),
            "estimated_duration": intent_profile.estimated_effort
        }
        workflows.append(primary_workflow)
        
        # A-H Protocol workflow
        ah_workflow = {
            "name": "A-H Protocol workflow",
            "steps": [
                "A: Intent Capture",
                "B: Hypothesis Formation",
                "C: Context Mapping",
                "D: Deep Expansion Layer",
                "E: Context Mesh Map",
                "F: Confidence-Gated Controls",
                "G: Implementation",
                "H: Audit/Memory/Continuity"
            ],
            "stakeholders": ["aether_ai", "human_operator"],
            "systems_involved": ["A_H_Protocol", "L0_L4_Documentation"],
            "estimated_duration": "high"
        }
        workflows.append(ah_workflow)
        
        return workflows
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "max_critical_paths": 10,
                "risk_threshold": 0.7,
                "dependency_strength_threshold": 0.5,
                "max_mitigation_strategies": 20
            }
    
    def _load_system_registry(self) -> Dict[str, Any]:
        """Load system registry with known systems."""
        return {
            "A_H_Protocol": {
                "type": "lucid_system",
                "criticality": "high",
                "dependencies": ["L0_L4_Documentation"]
            },
            "L0_L4_Documentation": {
                "type": "lucid_system",
                "criticality": "high",
                "dependencies": []
            },
            "Daemon_RAG_System": {
                "type": "lucid_system",
                "criticality": "high",
                "dependencies": ["A_H_Protocol"]
            }
        }
    
    def _load_dependency_patterns(self) -> Dict[str, List[str]]:
        """Load patterns for identifying dependencies."""
        return {
            "hard_dependency": ["requires", "depends on", "needs", "must have"],
            "soft_dependency": ["benefits from", "enhanced by", "improved with"],
            "conflict": ["conflicts with", "incompatible with", "blocks"],
            "optional": ["optional", "nice to have", "can use"]
        }
    
    def _load_risk_patterns(self) -> Dict[str, List[str]]:
        """Load patterns for identifying risks."""
        return {
            "availability_risk": ["unavailable", "offline", "down", "broken"],
            "performance_risk": ["slow", "bottleneck", "overloaded", "resource constrained"],
            "security_risk": ["vulnerable", "insecure", "exposed", "compromised"],
            "compatibility_risk": ["incompatible", "version mismatch", "deprecated"]
        }
    
    def _load_organizational_patterns(self) -> Dict[str, List[str]]:
        """Load patterns for identifying organizational factors."""
        return {
            "stakeholder": ["user", "customer", "admin", "developer", "manager"],
            "constraint": ["budget", "time", "resource", "policy", "compliance"],
            "requirement": ["must", "required", "mandatory", "essential", "critical"]
        }

# Example usage and testing
if __name__ == "__main__":
    # Test the Context Mapping system
    context_mapping = ContextMapping()
    
    # Create test intent profile and hypotheses
    from .intent_capture import IntentProfile, IntentType
    from .hypothesis_formation import Hypothesis, HypothesisStatus
    
    intent_profile = IntentProfile(
        id="test_intent",
        raw_intent="Implement A-H Protocol in daemon/RAG system",
        intent_type=IntentType.PROTOCOL_IMPLEMENTATION,
        primary_stakeholders=["aether_ai", "human_operator"],
        constraints=["time_constraint", "LUCID_compliance"],
        success_criteria=["Protocol implemented", "Tests passing"],
        non_negotiable_requirements=["LUCID compliance"],
        confidence_level=0.8,
        complexity_score=0.7,
        urgency_level="high",
        estimated_effort="high",
        risk_factors=["technical_complexity"],
        dependencies=["A-H Protocol", "L0-L4 standards"],
        context_data={"active_project": "AIM-OS"},
        timestamp=time.time()
    )
    
    hypotheses = [
        Hypothesis(
            id="test_hyp_1",
            description="Implement A-H Protocol using systematic approach",
            assumptions=["Protocol is well-defined"],
            testable_conditions=["All steps can be implemented"],
            expected_outcomes=["Complete implementation"],
            validation_method="protocol_testing",
            priority=1,
            confidence=0.8,
            impact_score=0.9,
            effort_estimate="high",
            status=HypothesisStatus.TESTABLE,
            evidence=[],
            refutation_conditions=["Protocol incomplete"],
            dependencies=["A_H_Protocol", "L0_L4_Documentation"],
            risks=["complexity"],
            success_metrics=["completeness"],
            created_at=time.time(),
            updated_at=time.time()
        )
    ]
    
    context = {
        "active_project": "AIM-OS",
        "open_files": ["daemon_rag_system/daemon_rag_system.py"],
        "current_task_track": "AH_PROTOCOL_IMPLEMENTATION"
    }
    
    context_map = context_mapping.map_context(intent_profile, hypotheses, context)
    
    print("Context Map Created:")
    print(f"ID: {context_map.id}")
    print(f"Name: {context_map.name}")
    print(f"Nodes: {len(context_map.nodes)}")
    print(f"Relationships: {len(context_map.relationships)}")
    print(f"Critical Paths: {len(context_map.critical_paths)}")
    print(f"Risk Factors: {len(context_map.risk_factors)}")
    print(f"Mitigation Strategies: {len(context_map.mitigation_strategies)}")
    print()
    
    print("Nodes:")
    for node_id, node in context_map.nodes.items():
        print(f"  {node_id}: {node.name} ({node.type}) - {node.criticality}")
    
    print("\nRelationships:")
    for rel in context_map.relationships[:5]:  # Show first 5
        print(f"  {rel.from_node} -> {rel.to_node} ({rel.relationship_type.value})")
    
    print("\nRisk Factors:")
    for risk in context_map.risk_factors:
        print(f"  - {risk}")
    
    print("\nContext Mapping System test completed successfully!")
