# L4 Complete Reference: Context Frames System

## API Reference

### Context Frame API

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
    documentation_references: Optional[Dict[str, str]] = None
    
    def is_valid(self) -> bool:
        """Validate context frame completeness"""
        required_fields = [
            self.identity, self.purpose, self.active_contract,
            self.blast_radius, self.mutation_eligibility
        ]
        return all(field for field in required_fields)
    
    def get_risk_level(self) -> str:
        """Get risk level based on blast radius and open wounds"""
        if self.blast_radius == "system-wide" and self.open_wounds:
            return "high"
        elif self.blast_radius in ["component-wide", "multi-component"]:
            return "medium"
        else:
            return "low"
    
    def can_mutate(self, mutation_type: str) -> bool:
        """Check if component can be mutated for specific type"""
        if not self.mutation_eligibility:
            return False
        
        # Check if mutation type is allowed
        allowed_mutations = self.get_allowed_mutations()
        return mutation_type in allowed_mutations
    
    def get_allowed_mutations(self) -> List[str]:
        """Get list of allowed mutation types"""
        if not self.mutation_eligibility:
            return []
        
        # Base allowed mutations
        allowed = ["read", "simple_edit"]
        
        # Add based on blast radius
        if self.blast_radius in ["local", "component-wide"]:
            allowed.extend(["refactor", "optimize"])
        
        if self.blast_radius in ["multi-component", "system-wide"]:
            allowed.extend(["architecture_change", "integration"])
        
        return allowed
    
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
            'version': self.version,
            'documentation_references': self.documentation_references
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContextFrame':
        """Create from dictionary"""
        return cls(
            component_id=data['component_id'],
            system_id=data['system_id'],
            identity=data['identity'],
            purpose=data['purpose'],
            active_contract=data['active_contract'],
            blast_radius=data['blast_radius'],
            open_wounds=data['open_wounds'],
            mutation_eligibility=data['mutation_eligibility'],
            critical_constraints=data['critical_constraints'],
            last_updated=datetime.fromisoformat(data['last_updated']),
            version=data['version'],
            documentation_references=data.get('documentation_references')
        )
```

#### ContextFrameGenerator
```python
class ContextFrameGenerator:
    """Generates and manages context frames for system components"""
    
    def __init__(self, metadata_service: MetadataService, template_service: TemplateService):
        self.metadata_service = metadata_service
        self.template_service = template_service
    
    def generate_context_frame(self, component_id: str) -> ContextFrame:
        """Generate context frame for a component"""
        # Get component metadata
        metadata = self.metadata_service.get_component_metadata(component_id)
        
        # Get template for component type
        template = self.template_service.get_template(metadata.component_type)
        
        # Generate context frame
        context_frame = ContextFrame(
            component_id=component_id,
            system_id=metadata.system_id,
            identity=template.format_identity(metadata),
            purpose=template.format_purpose(metadata),
            active_contract=template.format_contract(metadata),
            blast_radius=template.format_blast_radius(metadata),
            open_wounds=template.format_open_wounds(metadata),
            mutation_eligibility=template.format_mutation_eligibility(metadata),
            critical_constraints=template.format_constraints(metadata),
            last_updated=datetime.now(),
            version="1.0"
        )
        
        return context_frame
    
    def update_context_frame(self, component_id: str, updates: Dict[str, Any]) -> bool:
        """Update context frame with new information"""
        try:
            context_frame = self.get_context_frame(component_id)
            if not context_frame:
                return False
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(context_frame, key):
                    setattr(context_frame, key, value)
            
            context_frame.last_updated = datetime.now()
            
            # Save updated context frame
            self.save_context_frame(context_frame)
            return True
        except Exception as e:
            logger.error(f"Failed to update context frame for {component_id}: {e}")
            return False
    
    def validate_context_frame(self, context_frame: ContextFrame) -> ValidationResult:
        """Validate context frame completeness and accuracy"""
        errors = []
        warnings = []
        
        # Check required fields
        if not context_frame.identity:
            errors.append("Identity is required")
        
        if not context_frame.purpose:
            errors.append("Purpose is required")
        
        if not context_frame.active_contract:
            errors.append("Active contract is required")
        
        # Check blast radius validity
        valid_blast_radiuses = ["local", "component-wide", "multi-component", "system-wide"]
        if context_frame.blast_radius not in valid_blast_radiuses:
            errors.append(f"Invalid blast radius: {context_frame.blast_radius}")
        
        # Check open wounds format
        if not isinstance(context_frame.open_wounds, list):
            errors.append("Open wounds must be a list")
        
        # Check mutation eligibility consistency
        if not context_frame.mutation_eligibility and context_frame.blast_radius == "system-wide":
            warnings.append("System-wide component with no mutation eligibility")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
```

### Context Mesh Map API

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
    
    def get_critical_paths(self, mutation_type: str) -> List[CriticalPath]:
        """Get critical paths affected by specific mutation type"""
        return [path for path in self.critical_paths 
                if mutation_type in path.affected_mutations]
    
    def validate_dependencies(self) -> ValidationResult:
        """Validate dependency consistency"""
        errors = []
        warnings = []
        
        # Check for circular dependencies
        if self.has_circular_dependencies():
            errors.append("Circular dependencies detected")
        
        # Check for missing dependencies
        missing_deps = self.find_missing_dependencies()
        if missing_deps:
            warnings.append(f"Missing dependencies: {missing_deps}")
        
        # Check constraint consistency
        constraint_errors = self.validate_constraints()
        errors.extend(constraint_errors)
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def has_circular_dependencies(self) -> bool:
        """Check for circular dependencies"""
        # Implementation for circular dependency detection
        visited = set()
        rec_stack = set()
        
        def has_cycle(node):
            visited.add(node)
            rec_stack.add(node)
            
            for dep in self.dependencies:
                if dep.source == node:
                    if dep.target not in visited:
                        if has_cycle(dep.target):
                            return True
                    elif dep.target in rec_stack:
                        return True
            
            rec_stack.remove(node)
            return False
        
        for dep in self.dependencies:
            if dep.source not in visited:
                if has_cycle(dep.source):
                    return True
        
        return False
```

### Deep Context API

#### DeepContextAppendix
```python
@dataclass
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
    
    def get_decision_context(self, decision_id: str) -> Optional[DecisionContext]:
        """Get context for a specific decision"""
        if decision_id not in self.decision_rationale:
            return None
        
        rationale = self.decision_rationale[decision_id]
        alternatives = self.alternative_considerations.get(decision_id, [])
        
        return DecisionContext(
            decision_id=decision_id,
            rationale=rationale,
            alternatives=alternatives,
            timestamp=self.get_decision_timestamp(decision_id)
        )
    
    def add_lesson_learned(self, lesson: LessonLearned) -> bool:
        """Add a new lesson learned"""
        try:
            self.lessons_learned.append(lesson)
            self.last_updated = datetime.now()
            return True
        except Exception as e:
            logger.error(f"Failed to add lesson learned: {e}")
            return False
    
    def get_relevant_lessons(self, context: str) -> List[LessonLearned]:
        """Get lessons relevant to specific context"""
        relevant_lessons = []
        for lesson in self.lessons_learned:
            if lesson.is_relevant_to_context(context):
                relevant_lessons.append(lesson)
        return relevant_lessons
```

## Configuration Reference

### Context Frame Templates
```yaml
# Templates for different component types
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

### Context Loading Policies
```yaml
# Policies for context loading based on operation type
context_loading_policies:
  operation_types:
    read:
      required_layers: [context_frame]
      optional_layers: []
      cache_strategy: "always"
    
    simple_edit:
      required_layers: [context_frame, context_mesh_map]
      optional_layers: []
      cache_strategy: "frequent"
    
    complex_edit:
      required_layers: [context_frame, context_mesh_map]
      optional_layers: [deep_context]
      cache_strategy: "on_demand"
    
    architecture_change:
      required_layers: [context_frame, context_mesh_map, deep_context]
      optional_layers: []
      cache_strategy: "on_demand"
    
    crisis_response:
      required_layers: [context_frame, context_mesh_map, deep_context]
      optional_layers: []
      cache_strategy: "immediate"
```

## Error Handling

### Common Error Scenarios

#### Context Frame Not Found
```python
class ContextFrameNotFoundError(Exception):
    """Raised when context frame is not found"""
    def __init__(self, component_id: str):
        self.component_id = component_id
        super().__init__(f"Context frame not found for component {component_id}")
```

#### Invalid Context Frame
```python
class InvalidContextFrameError(Exception):
    """Raised when context frame is invalid"""
    def __init__(self, component_id: str, validation_errors: List[str]):
        self.component_id = component_id
        self.validation_errors = validation_errors
        super().__init__(
            f"Invalid context frame for component {component_id}: {validation_errors}"
        )
```

#### Context Loading Failure
```python
class ContextLoadingError(Exception):
    """Raised when context loading fails"""
    def __init__(self, component_id: str, operation_type: str, error_message: str):
        self.component_id = component_id
        self.operation_type = operation_type
        self.error_message = error_message
        super().__init__(
            f"Failed to load context for {component_id} ({operation_type}): {error_message}"
        )
```

### Error Recovery

#### Automatic Recovery
- **Retry Logic**: Automatic retry for transient failures
- **Fallback Mechanisms**: Fallback to cached context when possible
- **Graceful Degradation**: Continue operation with reduced context

#### Manual Recovery
- **Error Reporting**: Detailed error reports for manual intervention
- **Recovery Procedures**: Step-by-step recovery procedures
- **Support Escalation**: Escalation to support team for complex issues

## Testing Reference

### Unit Tests
```python
class TestContextFrameGenerator:
    def test_generate_context_frame(self):
        """Test context frame generation"""
        generator = ContextFrameGenerator(mock_metadata, mock_template)
        component_id = "test-component"
        
        context_frame = generator.generate_context_frame(component_id)
        
        assert context_frame.component_id == component_id
        assert context_frame.identity is not None
        assert context_frame.purpose is not None
        assert context_frame.is_valid()
    
    def test_validate_context_frame(self):
        """Test context frame validation"""
        generator = ContextFrameGenerator(mock_metadata, mock_template)
        
        # Valid context frame
        valid_frame = create_valid_context_frame()
        result = generator.validate_context_frame(valid_frame)
        assert result.is_valid
        
        # Invalid context frame
        invalid_frame = create_invalid_context_frame()
        result = generator.validate_context_frame(invalid_frame)
        assert not result.is_valid
        assert len(result.errors) > 0
```

### Integration Tests
```python
class TestContextLoadingIntegration:
    def test_end_to_end_context_loading(self):
        """Test complete context loading flow"""
        # Setup
        generator = ContextFrameGenerator(real_metadata, real_template)
        mesh_builder = ContextMeshMapBuilder(real_dependency_service)
        context_loader = ContextLoader(real_cache_service)
        
        # Generate context frame
        context_frame = generator.generate_context_frame("test-component")
        
        # Build context mesh map
        mesh_map = mesh_builder.build_context_mesh_map("test-component")
        
        # Load context for operation
        context_bundle = context_loader.load_context("test-component", "complex_edit")
        
        # Verify context bundle
        assert context_bundle.context_frame is not None
        assert context_bundle.context_mesh_map is not None
        assert context_bundle.deep_context is not None
```

### Performance Tests
```python
class TestContextPerformance:
    def test_large_system_context_loading(self):
        """Test context loading for large system"""
        context_loader = ContextLoader(real_cache_service)
        
        # Create large system with many components
        system_id = "large-system"
        components = create_large_system_components(1000)
        
        # Load context for all components
        start_time = time.time()
        context_bundles = []
        for component in components:
            bundle = context_loader.load_context(component.id, "read")
            context_bundles.append(bundle)
        loading_time = time.time() - start_time
        
        # Should complete within reasonable time
        assert loading_time < 5.0  # 5 seconds for 1000 components
        assert len(context_bundles) == 1000
```