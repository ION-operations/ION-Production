# L3 Detailed Implementation Guide: Context Frames System

## Implementation Architecture

### Core Data Structures

#### ContextFrame
```python
@dataclass
class ContextFrame:
    """Mandatory context frame for every system component"""
    component_id: str
    system_id: str
    identity: str
    purpose: str
    active_contract: str
    blast_radius: str
    open_wounds: List[str]
    mutation_eligibility: bool
    critical_constraints: List[str]
    last_updated: datetime
    version: str
    
    def is_valid(self) -> bool:
        """Validate context frame completeness"""
        required_fields = [
            self.identity, self.purpose, self.active_contract,
            self.blast_radius, self.mutation_eligibility
        ]
        return all(field for field in required_fields)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'component_id': self.component_id,
            'system_id': self.system_id,
            'identity': self.identity,
            'purpose': self.purpose,
            'active_contract': self.active_contract,
            'blast_radius': self.blast_radius,
            'open_wounds': self.open_wounds,
            'mutation_eligibility': self.mutation_eligibility,
            'critical_constraints': self.critical_constraints,
            'last_updated': self.last_updated.isoformat(),
            'version': self.version
        }
```

#### ContextMeshMap
```python
@dataclass
class ContextMeshMap:
    """Network-aware dependency map for system components"""
    component_id: str
    dependencies: List[Dependency]
    constraints: List[Constraint]
    critical_paths: List[CriticalPath]
    impact_surfaces: List[ImpactSurface]
    last_updated: datetime
    version: str
    
    def get_dependencies(self, mutation_type: str) -> List[Dependency]:
        """Get dependencies relevant to specific mutation type"""
        return [dep for dep in self.dependencies 
                if mutation_type in dep.affected_mutations]
    
    def calculate_impact_radius(self, mutation_type: str) -> float:
        """Calculate impact radius for specific mutation type"""
        relevant_deps = self.get_dependencies(mutation_type)
        return sum(dep.impact_weight for dep in relevant_deps)
```

#### DeepContextAppendix
```dataclass
class DeepContextAppendix:
    """Comprehensive historical documentation for complex decision-making"""
    component_id: str
    design_history: List[DesignDecision]
    incident_log: List[Incident]
    frontier_ideas: List[FrontierIdea]
    decision_rationale: Dict[str, str]
    alternative_considerations: Dict[str, List[str]]
    lessons_learned: List[LessonLearned]
    last_updated: datetime
    version: str
```

### Core Algorithms

#### Context Frame Generation Algorithm
```python
def generate_context_frame(component: SystemComponent) -> ContextFrame:
    """Generate context frame for a system component"""
    # Extract identity and purpose
    identity = extract_identity(component)
    purpose = extract_purpose(component)
    
    # Determine active contract
    active_contract = determine_active_contract(component)
    
    # Calculate blast radius
    blast_radius = calculate_blast_radius(component)
    
    # Identify open wounds
    open_wounds = identify_open_wounds(component)
    
    # Determine mutation eligibility
    mutation_eligibility = determine_mutation_eligibility(component)
    
    # Extract critical constraints
    critical_constraints = extract_critical_constraints(component)
    
    return ContextFrame(
        component_id=component.id,
        system_id=component.system_id,
        identity=identity,
        purpose=purpose,
        active_contract=active_contract,
        blast_radius=blast_radius,
        open_wounds=open_wounds,
        mutation_eligibility=mutation_eligibility,
        critical_constraints=critical_constraints,
        last_updated=datetime.now(),
        version="1.0"
    )
```

#### Context Mesh Map Building Algorithm
```python
def build_context_mesh_map(component: SystemComponent) -> ContextMeshMap:
    """Build context mesh map for a system component"""
    # Analyze dependencies
    dependencies = analyze_dependencies(component)
    
    # Extract constraints
    constraints = extract_constraints(component)
    
    # Identify critical paths
    critical_paths = identify_critical_paths(component, dependencies)
    
    # Calculate impact surfaces
    impact_surfaces = calculate_impact_surfaces(component, dependencies)
    
    return ContextMeshMap(
        component_id=component.id,
        dependencies=dependencies,
        constraints=constraints,
        critical_paths=critical_paths,
        impact_surfaces=impact_surfaces,
        last_updated=datetime.now(),
        version="1.0"
    )
```

#### Context Loading Algorithm
```python
def load_context(component_id: str, operation_type: str) -> ContextBundle:
    """Load appropriate context for specific operation"""
    # Always load context frame
    context_frame = load_context_frame(component_id)
    
    # Load context mesh map if needed
    context_mesh_map = None
    if operation_type in ["mutation", "integration", "analysis"]:
        context_mesh_map = load_context_mesh_map(component_id)
    
    # Load deep context appendix if needed
    deep_context = None
    if operation_type in ["complex_decision", "architecture_change", "crisis_response"]:
        deep_context = load_deep_context_appendix(component_id)
    
    return ContextBundle(
        context_frame=context_frame,
        context_mesh_map=context_mesh_map,
        deep_context=deep_context,
        loaded_at=datetime.now()
    )
```

### Integration Patterns

#### L0-L4 Documentation Integration
```python
class DocumentationIntegration:
    def __init__(self, documentation_system):
        self.documentation_system = documentation_system
    
    def enhance_context_with_docs(self, context_frame: ContextFrame) -> ContextFrame:
        """Enhance context frame with L0-L4 documentation references"""
        docs = self.documentation_system.get_documentation(context_frame.component_id)
        
        # Add documentation references to context frame
        context_frame.documentation_references = {
            'l0': docs.get('l0_executive'),
            'l1': docs.get('l1_overview'),
            'l2': docs.get('l2_architecture'),
            'l3': docs.get('l3_detailed'),
            'l4': docs.get('l4_complete')
        }
        
        return context_frame
```

#### System Map Integration
```python
class SystemMapIntegration:
    def __init__(self, system_map_service):
        self.system_map_service = system_map_service
    
    def build_mesh_map_from_system_map(self, component_id: str) -> ContextMeshMap:
        """Build context mesh map from system map data"""
        system_map = self.system_map_service.get_system_map(component_id)
        
        # Convert system map topology to context mesh map
        dependencies = []
        for connection in system_map.connections:
            dependency = Dependency(
                target_component=connection.target,
                relationship_type=connection.type,
                impact_weight=connection.weight,
                affected_mutations=connection.affected_operations
            )
            dependencies.append(dependency)
        
        return ContextMeshMap(
            component_id=component_id,
            dependencies=dependencies,
            constraints=system_map.constraints,
            critical_paths=system_map.critical_paths,
            impact_surfaces=system_map.impact_surfaces,
            last_updated=datetime.now(),
            version="1.0"
        )
```

### Configuration and Policies

#### Context Frame Templates
```yaml
context_frame_templates:
  system:
    identity: "System: {name}"
    purpose: "Purpose: {description}"
    active_contract: "Contract: {contract}"
    blast_radius: "Blast Radius: {radius}"
    open_wounds: "Open Wounds: {wounds}"
    mutation_eligibility: "Mutation Eligible: {eligible}"
    critical_constraints: "Constraints: {constraints}"
  
  component:
    identity: "Component: {name}"
    purpose: "Purpose: {description}"
    active_contract: "Contract: {contract}"
    blast_radius: "Blast Radius: {radius}"
    open_wounds: "Open Wounds: {wounds}"
    mutation_eligibility: "Mutation Eligible: {eligible}"
    critical_constraints: "Constraints: {constraints}"
  
  file:
    identity: "File: {name}"
    purpose: "Purpose: {description}"
    active_contract: "Contract: {contract}"
    blast_radius: "Blast Radius: {radius}"
    open_wounds: "Open Wounds: {wounds}"
    mutation_eligibility: "Mutation Eligible: {eligible}"
    critical_constraints: "Constraints: {constraints}"
```

#### Context Loading Policies
```yaml
context_loading_policies:
  operation_types:
    read:
      required_layers: [context_frame]
      optional_layers: []
    
    simple_edit:
      required_layers: [context_frame, context_mesh_map]
      optional_layers: []
    
    complex_edit:
      required_layers: [context_frame, context_mesh_map]
      optional_layers: [deep_context]
    
    architecture_change:
      required_layers: [context_frame, context_mesh_map, deep_context]
      optional_layers: []
    
    crisis_response:
      required_layers: [context_frame, context_mesh_map, deep_context]
      optional_layers: []
```

### Performance Considerations

#### Caching Strategy
- **Context Frame Cache**: Always-loaded cache for context frames
- **Context Mesh Map Cache**: Frequently accessed cache for mesh maps
- **Deep Context Cache**: Lazy-loaded cache for deep context
- **Invalidation Strategy**: Smart invalidation based on system changes

#### Lazy Loading Implementation
- **Layer-based Loading**: Load only required context layers
- **Operation-based Loading**: Load context based on operation type
- **Predictive Loading**: Pre-load likely needed context
- **Background Loading**: Load context in background when possible

#### Memory Management
- **Context Size Limits**: Limit size of loaded context
- **Context Cleanup**: Clean up unused context
- **Memory Monitoring**: Monitor context memory usage
- **Garbage Collection**: Regular cleanup of old context