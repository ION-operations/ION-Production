"""
Deep Expansion Layer (DEL) - Step D of A-H Protocol

This module implements the Deep Expansion Layer, which is responsible for:
- Recursively expanding every detail to maximum depth
- Predicting scope, dimensionality, test demand, Tier classification
- Defining rollout sequencing before any code is written
- Creating Context Mesh Map (CMM) for every meaningful unit

Following A-H Protocol methodology from ChatGPT journal.
"""

from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import json
import time
import uuid
from .intent_capture import IntentProfile, IntentType
from .hypothesis_formation import Hypothesis
from .context_mapping import ContextMap, ContextNode, DependencyType

class TierLevel(Enum):
    """Tier classification for system components."""
    TIER_0 = "tier_0"  # Cosmetic/internal changes
    TIER_1 = "tier_1"  # Minor functional changes
    TIER_2 = "tier_2"  # Significant functional changes
    TIER_3 = "tier_3"  # Major architectural changes

class ComplexityLevel(Enum):
    """Complexity levels for expansion analysis."""
    SIMPLE = "simple"  # < 1 day work
    MODERATE = "moderate"  # 1-3 days work
    COMPLEX = "complex"  # 3-7 days work
    VERY_COMPLEX = "very_complex"  # 1-2 weeks work
    EXTREME = "extreme"  # 2+ weeks work

@dataclass
class ExpansionNode:
    """A node in the deep expansion tree."""
    id: str
    name: str
    description: str
    tier: TierLevel
    complexity: ComplexityLevel
    estimated_effort_hours: float
    test_demand_score: float
    blast_radius: str
    dependencies: List[str]
    sub_components: List[str]
    rollout_sequence: int
    must_never_vows: List[str]
    perf_security_budget: Dict[str, Any]
    required_tests: List[str]
    owner_track: str
    context_mesh_map: Optional[Dict[str, Any]] = None
    parent_id: Optional[str] = None
    depth_level: int = 0
    is_leaf: bool = False

@dataclass
class ExpansionAnalysis:
    """Complete analysis of a system's deep expansion."""
    root_node_id: str
    total_nodes: int
    total_effort_hours: float
    max_depth: int
    tier_distribution: Dict[TierLevel, int]
    complexity_distribution: Dict[ComplexityLevel, int]
    critical_path: List[str]
    rollout_sequence: List[str]
    risk_factors: List[str]
    test_coverage_required: float
    blast_radius_analysis: Dict[str, Any]
    spec_coverage_index: float
    created_at: float
    version: str = "1.0"

class DeepExpansionLayer:
    """
    Deep Expansion Layer for A-H Protocol Step D.
    
    Recursively expands every detail to maximum depth, providing complete
    system analysis before implementation begins.
    """
    
    def __init__(self, config_path: str = "del_config.json"):
        """Initialize the Deep Expansion Layer."""
        self.config = self._load_config(config_path)
        self.expansion_patterns = self._load_expansion_patterns()
        self.tier_classification_rules = self._load_tier_rules()
        self.complexity_estimation_rules = self._load_complexity_rules()
        self.test_demand_patterns = self._load_test_patterns()
        
    def expand_system(self, intent_profile: IntentProfile, context_map: ContextMap, 
                     hypotheses: List[Hypothesis], context: Dict[str, Any] = None) -> ExpansionAnalysis:
        """
        Perform deep expansion analysis of a system.
        
        Args:
            intent_profile: The captured intent profile
            context_map: The context mapping from Step C
            hypotheses: List of hypotheses from Step B
            context: Additional context data
            
        Returns:
            ExpansionAnalysis: Complete deep expansion analysis
        """
        if context is None:
            context = {}
            
        # Create root expansion node
        root_node = self._create_root_node(intent_profile, context_map, context)
        
        # Recursively expand all components
        expansion_tree = self._recursive_expand(root_node, intent_profile, context_map, 
                                              hypotheses, context, max_depth=5)
        
        # Analyze the complete expansion tree
        analysis = self._analyze_expansion_tree(expansion_tree, intent_profile, context)
        
        return analysis
    
    def _create_root_node(self, intent_profile: IntentProfile, context_map: ContextMap, 
                         context: Dict[str, Any]) -> ExpansionNode:
        """Create the root node for expansion analysis."""
        root_id = f"root_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        # Determine tier based on intent type and scope
        tier = self._classify_tier(intent_profile, context_map)
        
        # Estimate complexity
        complexity = self._estimate_complexity(intent_profile, context_map)
        
        # Calculate effort estimation
        effort_hours = self._calculate_effort_hours(complexity, tier, context_map)
        
        # Calculate test demand
        test_demand = self._calculate_test_demand(intent_profile, context_map)
        
        # Determine blast radius
        blast_radius = self._calculate_blast_radius(intent_profile, context_map)
        
        # Generate must-never vows
        must_never_vows = self._generate_must_never_vows(intent_profile, context_map)
        
        # Set performance/security budget
        perf_security_budget = self._calculate_perf_security_budget(intent_profile, context_map)
        
        # Generate required tests
        required_tests = self._generate_required_tests(intent_profile, context_map)
        
        # Determine owner track
        owner_track = self._determine_owner_track(intent_profile, context)
        
        return ExpansionNode(
            id=root_id,
            name=f"Root: {intent_profile.raw_intent[:50]}...",
            description=f"Deep expansion root for: {intent_profile.raw_intent}",
            tier=tier,
            complexity=complexity,
            estimated_effort_hours=effort_hours,
            test_demand_score=test_demand,
            blast_radius=blast_radius,
            dependencies=[],
            sub_components=[],
            rollout_sequence=0,
            must_never_vows=must_never_vows,
            perf_security_budget=perf_security_budget,
            required_tests=required_tests,
            owner_track=owner_track,
            depth_level=0,
            is_leaf=False
        )
    
    def _recursive_expand(self, node: ExpansionNode, intent_profile: IntentProfile, 
                         context_map: ContextMap, hypotheses: List[Hypothesis], 
                         context: Dict[str, Any], max_depth: int = 5) -> Dict[str, ExpansionNode]:
        """Recursively expand a node and all its sub-components."""
        expansion_tree = {node.id: node}
        
        if node.depth_level >= max_depth:
            node.is_leaf = True
            return expansion_tree
        
        # Generate sub-components based on node type and context
        sub_components = self._generate_sub_components(node, intent_profile, context_map, 
                                                      hypotheses, context)
        
        node.sub_components = [comp.id for comp in sub_components]
        
        # Add sub-components to tree
        for sub_comp in sub_components:
            sub_comp.parent_id = node.id
            sub_comp.depth_level = node.depth_level + 1
            expansion_tree[sub_comp.id] = sub_comp
            
            # Recursively expand sub-components
            sub_tree = self._recursive_expand(sub_comp, intent_profile, context_map, 
                                            hypotheses, context, max_depth)
            expansion_tree.update(sub_tree)
        
        return expansion_tree
    
    def _generate_sub_components(self, node: ExpansionNode, intent_profile: IntentProfile, 
                                context_map: ContextMap, hypotheses: List[Hypothesis], 
                                context: Dict[str, Any]) -> List[ExpansionNode]:
        """Generate sub-components for a given node."""
        sub_components = []
        
        # Generate components based on intent type
        if intent_profile.intent_type == IntentType.PROTOCOL_IMPLEMENTATION:
            sub_components.extend(self._generate_protocol_components(node, context))
        elif intent_profile.intent_type == IntentType.FEATURE_DEVELOPMENT:
            sub_components.extend(self._generate_feature_components(node, context))
        elif intent_profile.intent_type == IntentType.SYSTEM_ENHANCEMENT:
            sub_components.extend(self._generate_enhancement_components(node, context))
        elif intent_profile.intent_type == IntentType.PERFORMANCE_OPTIMIZATION:
            sub_components.extend(self._generate_optimization_components(node, context))
        else:
            sub_components.extend(self._generate_generic_components(node, context))
        
        # Generate components based on context map relationships
        for relationship in context_map.relationships:
            if relationship.from_node == node.id or relationship.to_node == node.id:
                related_comp = self._generate_relationship_component(node, relationship, context)
                if related_comp:
                    sub_components.append(related_comp)
        
        # Generate components based on hypotheses
        for hypothesis in hypotheses:
            if hypothesis.confidence > 0.7:  # Only high-confidence hypotheses
                hyp_comp = self._generate_hypothesis_component(node, hypothesis, context)
                if hyp_comp:
                    sub_components.append(hyp_comp)
        
        return sub_components
    
    def _classify_tier(self, intent_profile: IntentProfile, context_map: ContextMap) -> TierLevel:
        """Classify the tier level based on intent and context."""
        # High-level classification based on intent type
        if intent_profile.intent_type in [IntentType.BUG_FIX, IntentType.DOCUMENTATION_UPDATE]:
            return TierLevel.TIER_0
        elif intent_profile.intent_type in [IntentType.MAINTENANCE, IntentType.PERFORMANCE_OPTIMIZATION]:
            return TierLevel.TIER_1
        elif intent_profile.intent_type in [IntentType.FEATURE_DEVELOPMENT, IntentType.SYSTEM_ENHANCEMENT]:
            return TierLevel.TIER_2
        else:  # PROTOCOL_IMPLEMENTATION, SECURITY_HARDENING, etc.
            return TierLevel.TIER_3
    
    def _estimate_complexity(self, intent_profile: IntentProfile, context_map: ContextMap) -> ComplexityLevel:
        """Estimate complexity level based on intent and context."""
        # Base complexity on intent type
        base_complexity = {
            IntentType.BUG_FIX: ComplexityLevel.SIMPLE,
            IntentType.DOCUMENTATION_UPDATE: ComplexityLevel.SIMPLE,
            IntentType.MAINTENANCE: ComplexityLevel.SIMPLE,
            IntentType.PERFORMANCE_OPTIMIZATION: ComplexityLevel.MODERATE,
            IntentType.FEATURE_DEVELOPMENT: ComplexityLevel.COMPLEX,
            IntentType.SYSTEM_ENHANCEMENT: ComplexityLevel.COMPLEX,
            IntentType.PROTOCOL_IMPLEMENTATION: ComplexityLevel.VERY_COMPLEX,
            IntentType.SECURITY_HARDENING: ComplexityLevel.VERY_COMPLEX,
            IntentType.AUDIT_REVIEW: ComplexityLevel.MODERATE,
            IntentType.INTEGRATION_WORK: ComplexityLevel.COMPLEX
        }
        
        complexity = base_complexity.get(intent_profile.intent_type, ComplexityLevel.MODERATE)
        
        # Adjust based on context map complexity
        if len(context_map.nodes) > 10:
            if complexity == ComplexityLevel.SIMPLE:
                complexity = ComplexityLevel.MODERATE
            elif complexity == ComplexityLevel.MODERATE:
                complexity = ComplexityLevel.COMPLEX
            elif complexity == ComplexityLevel.COMPLEX:
                complexity = ComplexityLevel.VERY_COMPLEX
        
        # Adjust based on confidence level
        if intent_profile.confidence_level < 0.5:
            if complexity == ComplexityLevel.SIMPLE:
                complexity = ComplexityLevel.MODERATE
            elif complexity == ComplexityLevel.MODERATE:
                complexity = ComplexityLevel.COMPLEX
        
        return complexity
    
    def _calculate_effort_hours(self, complexity: ComplexityLevel, tier: TierLevel, 
                               context_map: ContextMap) -> float:
        """Calculate estimated effort in hours."""
        base_hours = {
            ComplexityLevel.SIMPLE: 4,
            ComplexityLevel.MODERATE: 16,
            ComplexityLevel.COMPLEX: 40,
            ComplexityLevel.VERY_COMPLEX: 80,
            ComplexityLevel.EXTREME: 160
        }
        
        effort = base_hours[complexity]
        
        # Adjust based on tier
        tier_multiplier = {
            TierLevel.TIER_0: 0.5,
            TierLevel.TIER_1: 0.8,
            TierLevel.TIER_2: 1.2,
            TierLevel.TIER_3: 1.5
        }
        
        effort *= tier_multiplier[tier]
        
        # Adjust based on context map size
        if len(context_map.nodes) > 5:
            effort *= 1.2
        if len(context_map.nodes) > 10:
            effort *= 1.5
        
        return round(effort, 1)
    
    def _calculate_test_demand(self, intent_profile: IntentProfile, context_map: ContextMap) -> float:
        """Calculate test demand score (0.0 to 1.0)."""
        base_score = 0.5
        
        # Adjust based on intent type
        if intent_profile.intent_type in [IntentType.SECURITY_HARDENING, IntentType.PROTOCOL_IMPLEMENTATION]:
            base_score = 0.9
        elif intent_profile.intent_type in [IntentType.FEATURE_DEVELOPMENT, IntentType.SYSTEM_ENHANCEMENT]:
            base_score = 0.8
        elif intent_profile.intent_type in [IntentType.PERFORMANCE_OPTIMIZATION, IntentType.INTEGRATION_WORK]:
            base_score = 0.7
        elif intent_profile.intent_type in [IntentType.BUG_FIX, IntentType.AUDIT_REVIEW]:
            base_score = 0.6
        
        # Adjust based on confidence level
        if intent_profile.confidence_level < 0.7:
            base_score += 0.2
        
        # Adjust based on context map complexity
        if len(context_map.nodes) > 5:
            base_score += 0.1
        if len(context_map.relationships) > 10:
            base_score += 0.1
        
        return min(base_score, 1.0)
    
    def _calculate_blast_radius(self, intent_profile: IntentProfile, context_map: ContextMap) -> str:
        """Calculate blast radius of changes."""
        if intent_profile.intent_type in [IntentType.BUG_FIX, IntentType.DOCUMENTATION_UPDATE]:
            return "local"
        elif intent_profile.intent_type in [IntentType.MAINTENANCE, IntentType.PERFORMANCE_OPTIMIZATION]:
            return "component"
        elif intent_profile.intent_type in [IntentType.FEATURE_DEVELOPMENT, IntentType.SYSTEM_ENHANCEMENT]:
            return "module"
        elif intent_profile.intent_type in [IntentType.PROTOCOL_IMPLEMENTATION, IntentType.SECURITY_HARDENING]:
            return "system"
        else:
            return "platform"
    
    def _generate_must_never_vows(self, intent_profile: IntentProfile, context_map: ContextMap) -> List[str]:
        """Generate must-never vows based on intent and context."""
        vows = []
        
        # Base vows for all intents
        vows.extend([
            "Never break existing functionality",
            "Never compromise data integrity",
            "Never bypass security controls"
        ])
        
        # Intent-specific vows
        if intent_profile.intent_type == IntentType.SECURITY_HARDENING:
            vows.extend([
                "Never reduce security measures",
                "Never expose sensitive data",
                "Never bypass authentication"
            ])
        elif intent_profile.intent_type == IntentType.PERFORMANCE_OPTIMIZATION:
            vows.extend([
                "Never reduce functionality for performance",
                "Never compromise code readability",
                "Never skip error handling"
            ])
        elif intent_profile.intent_type == IntentType.PROTOCOL_IMPLEMENTATION:
            vows.extend([
                "Never deviate from protocol standards",
                "Never skip validation steps",
                "Never bypass governance controls"
            ])
        
        return vows
    
    def _calculate_perf_security_budget(self, intent_profile: IntentProfile, context_map: ContextMap) -> Dict[str, Any]:
        """Calculate performance and security budget constraints."""
        budget = {
            "max_response_time_ms": 1000,
            "max_memory_usage_mb": 512,
            "max_cpu_usage_percent": 80,
            "security_level": "high",
            "encryption_required": True,
            "audit_logging_required": True
        }
        
        # Adjust based on intent type
        if intent_profile.intent_type == IntentType.PERFORMANCE_OPTIMIZATION:
            budget["max_response_time_ms"] = 500
            budget["max_cpu_usage_percent"] = 60
        elif intent_profile.intent_type == IntentType.SECURITY_HARDENING:
            budget["security_level"] = "maximum"
            budget["encryption_required"] = True
        elif intent_profile.intent_type == IntentType.BUG_FIX:
            budget["max_response_time_ms"] = 2000  # More lenient for bug fixes
        
        return budget
    
    def _generate_required_tests(self, intent_profile: IntentProfile, context_map: ContextMap) -> List[str]:
        """Generate list of required tests."""
        tests = ["unit_tests", "integration_tests"]
        
        # Add tests based on intent type
        if intent_profile.intent_type in [IntentType.SECURITY_HARDENING, IntentType.PROTOCOL_IMPLEMENTATION]:
            tests.extend(["security_tests", "compliance_tests", "penetration_tests"])
        elif intent_profile.intent_type == IntentType.PERFORMANCE_OPTIMIZATION:
            tests.extend(["performance_tests", "load_tests", "stress_tests"])
        elif intent_profile.intent_type in [IntentType.FEATURE_DEVELOPMENT, IntentType.SYSTEM_ENHANCEMENT]:
            tests.extend(["functional_tests", "acceptance_tests", "regression_tests"])
        
        # Add tests based on complexity
        if len(context_map.nodes) > 5:
            tests.extend(["end_to_end_tests", "system_tests"])
        
        return tests
    
    def _determine_owner_track(self, intent_profile: IntentProfile, context: Dict[str, Any]) -> str:
        """Determine the owner track for this work."""
        # Default to development track
        track = "development"
        
        # Adjust based on intent type
        if intent_profile.intent_type == IntentType.SECURITY_HARDENING:
            track = "security"
        elif intent_profile.intent_type == IntentType.PERFORMANCE_OPTIMIZATION:
            track = "performance"
        elif intent_profile.intent_type == IntentType.PROTOCOL_IMPLEMENTATION:
            track = "architecture"
        elif intent_profile.intent_type == IntentType.AUDIT_REVIEW:
            track = "compliance"
        
        # Adjust based on context
        if context.get("requires_approval", False):
            track = "governance"
        
        return track
    
    def _analyze_expansion_tree(self, expansion_tree: Dict[str, ExpansionNode], 
                               intent_profile: IntentProfile, context: Dict[str, Any]) -> ExpansionAnalysis:
        """Analyze the complete expansion tree and generate analysis."""
        total_nodes = len(expansion_tree)
        total_effort = sum(node.estimated_effort_hours for node in expansion_tree.values())
        max_depth = max(node.depth_level for node in expansion_tree.values())
        
        # Calculate tier distribution
        tier_dist = {}
        for tier in TierLevel:
            tier_dist[tier] = sum(1 for node in expansion_tree.values() if node.tier == tier)
        
        # Calculate complexity distribution
        complexity_dist = {}
        for complexity in ComplexityLevel:
            complexity_dist[complexity] = sum(1 for node in expansion_tree.values() if node.complexity == complexity)
        
        # Find critical path (longest dependency chain)
        critical_path = self._find_critical_path(expansion_tree)
        
        # Generate rollout sequence
        rollout_sequence = self._generate_rollout_sequence(expansion_tree)
        
        # Identify risk factors
        risk_factors = self._identify_risk_factors(expansion_tree, intent_profile)
        
        # Calculate test coverage requirement
        test_coverage = sum(node.test_demand_score for node in expansion_tree.values()) / total_nodes
        
        # Analyze blast radius
        blast_radius_analysis = self._analyze_blast_radius(expansion_tree)
        
        # Calculate spec coverage index
        spec_coverage_index = self._calculate_spec_coverage_index(expansion_tree)
        
        return ExpansionAnalysis(
            root_node_id=list(expansion_tree.keys())[0],
            total_nodes=total_nodes,
            total_effort_hours=total_effort,
            max_depth=max_depth,
            tier_distribution=tier_dist,
            complexity_distribution=complexity_dist,
            critical_path=critical_path,
            rollout_sequence=rollout_sequence,
            risk_factors=risk_factors,
            test_coverage_required=test_coverage,
            blast_radius_analysis=blast_radius_analysis,
            spec_coverage_index=spec_coverage_index,
            created_at=time.time()
        )
    
    def _find_critical_path(self, expansion_tree: Dict[str, ExpansionNode]) -> List[str]:
        """Find the critical path through the expansion tree."""
        # Simple implementation - find the longest path by effort
        paths = []
        
        def find_paths(node_id: str, current_path: List[str], visited: Set[str]):
            if node_id in visited:
                return
            
            visited.add(node_id)
            current_path.append(node_id)
            
            node = expansion_tree[node_id]
            if not node.sub_components:
                paths.append(current_path.copy())
            else:
                for sub_id in node.sub_components:
                    find_paths(sub_id, current_path, visited.copy())
            
            current_path.pop()
        
        # Start from root nodes (nodes with no parent)
        root_nodes = [node_id for node_id, node in expansion_tree.items() if node.parent_id is None]
        for root_id in root_nodes:
            find_paths(root_id, [], set())
        
        # Return the path with highest total effort
        if not paths:
            return []
        
        best_path = max(paths, key=lambda path: sum(expansion_tree[node_id].estimated_effort_hours for node_id in path))
        return best_path
    
    def _generate_rollout_sequence(self, expansion_tree: Dict[str, ExpansionNode]) -> List[str]:
        """Generate rollout sequence based on dependencies and effort."""
        # Simple implementation - sort by effort and dependencies
        nodes = list(expansion_tree.values())
        nodes.sort(key=lambda node: (node.depth_level, -node.estimated_effort_hours))
        return [node.id for node in nodes]
    
    def _identify_risk_factors(self, expansion_tree: Dict[str, ExpansionNode], 
                              intent_profile: IntentProfile) -> List[str]:
        """Identify risk factors in the expansion tree."""
        risks = []
        
        # High complexity risks
        high_complexity_nodes = [node for node in expansion_tree.values() 
                               if node.complexity in [ComplexityLevel.VERY_COMPLEX, ComplexityLevel.EXTREME]]
        if high_complexity_nodes:
            risks.append(f"High complexity components: {len(high_complexity_nodes)} nodes")
        
        # High tier risks
        high_tier_nodes = [node for node in expansion_tree.values() 
                          if node.tier == TierLevel.TIER_3]
        if high_tier_nodes:
            risks.append(f"High-tier components requiring approval: {len(high_tier_nodes)} nodes")
        
        # Large blast radius risks
        large_blast_nodes = [node for node in expansion_tree.values() 
                           if node.blast_radius in ["system", "platform"]]
        if large_blast_nodes:
            risks.append(f"Large blast radius components: {len(large_blast_nodes)} nodes")
        
        # Low confidence risks
        if intent_profile.confidence_level < 0.7:
            risks.append("Low confidence in intent classification")
        
        return risks
    
    def _analyze_blast_radius(self, expansion_tree: Dict[str, ExpansionNode]) -> Dict[str, Any]:
        """Analyze blast radius distribution."""
        blast_radius_counts = {}
        for node in expansion_tree.values():
            blast_radius_counts[node.blast_radius] = blast_radius_counts.get(node.blast_radius, 0) + 1
        
        return {
            "distribution": blast_radius_counts,
            "max_blast_radius": max(blast_radius_counts.keys(), key=lambda x: ["local", "component", "module", "system", "platform"].index(x)),
            "high_risk_components": len([node for node in expansion_tree.values() 
                                       if node.blast_radius in ["system", "platform"]])
        }
    
    def _calculate_spec_coverage_index(self, expansion_tree: Dict[str, ExpansionNode]) -> float:
        """Calculate spec coverage index (0.0 to 1.0)."""
        total_nodes = len(expansion_tree)
        if total_nodes == 0:
            return 0.0
        
        # Calculate coverage based on various factors
        coverage_factors = []
        
        # Test coverage factor
        avg_test_demand = sum(node.test_demand_score for node in expansion_tree.values()) / total_nodes
        coverage_factors.append(avg_test_demand)
        
        # Documentation factor (simplified)
        doc_factor = 0.8  # Assume 80% documentation coverage
        coverage_factors.append(doc_factor)
        
        # Specification factor (simplified)
        spec_factor = 0.9  # Assume 90% specification coverage
        coverage_factors.append(spec_factor)
        
        return sum(coverage_factors) / len(coverage_factors)
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "max_expansion_depth": 5,
                "default_effort_multiplier": 1.0,
                "test_coverage_threshold": 0.8
            }
    
    def _load_expansion_patterns(self) -> Dict[str, Any]:
        """Load expansion patterns for different component types."""
        return {
            "protocol_implementation": [
                "intent_capture", "hypothesis_formation", "context_mapping",
                "deep_expansion", "confidence_gates", "context_mesh_maps",
                "implementation", "audit_memory"
            ],
            "feature_development": [
                "requirements", "design", "implementation", "testing", "documentation"
            ],
            "system_enhancement": [
                "analysis", "design", "refactoring", "testing", "deployment"
            ],
            "performance_optimization": [
                "profiling", "bottleneck_analysis", "optimization", "testing", "monitoring"
            ]
        }
    
    def _load_tier_rules(self) -> Dict[str, Any]:
        """Load tier classification rules."""
        return {
            "tier_0_keywords": ["cosmetic", "internal", "documentation", "bug_fix"],
            "tier_1_keywords": ["maintenance", "optimization", "minor"],
            "tier_2_keywords": ["feature", "enhancement", "moderate"],
            "tier_3_keywords": ["protocol", "security", "architecture", "major"]
        }
    
    def _load_complexity_rules(self) -> Dict[str, Any]:
        """Load complexity estimation rules."""
        return {
            "simple_threshold": 1,
            "moderate_threshold": 3,
            "complex_threshold": 7,
            "very_complex_threshold": 14
        }
    
    def _load_test_patterns(self) -> Dict[str, Any]:
        """Load test demand patterns."""
        return {
            "high_test_demand": ["security", "protocol", "critical"],
            "medium_test_demand": ["feature", "enhancement", "integration"],
            "low_test_demand": ["documentation", "cosmetic", "maintenance"]
        }
    
    # Placeholder methods for component generation
    def _generate_protocol_components(self, node: ExpansionNode, context: Dict[str, Any]) -> List[ExpansionNode]:
        """Generate components for protocol implementation."""
        # Implementation would generate specific protocol components
        return []
    
    def _generate_feature_components(self, node: ExpansionNode, context: Dict[str, Any]) -> List[ExpansionNode]:
        """Generate components for feature development."""
        # Implementation would generate specific feature components
        return []
    
    def _generate_enhancement_components(self, node: ExpansionNode, context: Dict[str, Any]) -> List[ExpansionNode]:
        """Generate components for system enhancement."""
        # Implementation would generate specific enhancement components
        return []
    
    def _generate_optimization_components(self, node: ExpansionNode, context: Dict[str, Any]) -> List[ExpansionNode]:
        """Generate components for performance optimization."""
        # Implementation would generate specific optimization components
        return []
    
    def _generate_generic_components(self, node: ExpansionNode, context: Dict[str, Any]) -> List[ExpansionNode]:
        """Generate generic components."""
        # Implementation would generate generic components
        return []
    
    def _generate_relationship_component(self, node: ExpansionNode, relationship: Any, context: Dict[str, Any]) -> Optional[ExpansionNode]:
        """Generate component based on relationship."""
        # Implementation would generate relationship-based components
        return None
    
    def _generate_hypothesis_component(self, node: ExpansionNode, hypothesis: Hypothesis, context: Dict[str, Any]) -> Optional[ExpansionNode]:
        """Generate component based on hypothesis."""
        # Implementation would generate hypothesis-based components
        return None
