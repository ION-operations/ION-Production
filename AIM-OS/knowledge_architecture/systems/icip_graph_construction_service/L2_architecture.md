# ICIP Graph Construction Service - L2 Architecture

**Detail Level:** 2 of 5 (2000 words)  
**Context Budget:** ~32k tokens  
**Purpose:** Deep dive into Graph Construction Service architecture and AIM-OS integration

---

## System Architecture Deep Dive

### Architectural Principles

The Graph Construction Service is founded on four core principles that enable its advanced capabilities and seamless AIM-OS integration:

#### 1. Unified Graph Model
**Principle**: Create a language-agnostic representation that unifies all code elements.

**Implementation**:
- **Universal Node Types**: Functions, classes, variables, types, files, modules
- **Standardized Edges**: Calls, inheritance, composition, imports, dependencies
- **Consistent Properties**: Metadata, types, locations, complexity metrics
- **Semantic Annotations**: Rich semantic information for AI understanding

**AIM-OS Integration**:
- **CMC Storage**: CPG nodes become CMC atoms with bitemporal tracking
- **HHNI Indexing**: Graph structure enables physics-based retrieval
- **VIF Provenance**: Construction operations tracked with confidence scores
- **SEG Knowledge**: Graph patterns synthesized into knowledge graphs

#### 2. Incremental Construction
**Principle**: Build and maintain the graph incrementally as code changes.

**Implementation**:
- **Change Detection**: Identify what has changed in the codebase
- **Delta Construction**: Only reconstruct affected parts of the graph
- **Consistency Maintenance**: Ensure graph remains consistent after changes
- **Performance Optimization**: Minimize construction time and resource usage

**AIM-OS Integration**:
- **TCS Timeline**: Incremental changes stream to timeline
- **CMC Updates**: Graph updates stored as CMC atoms
- **VIF Tracking**: Change operations tracked with provenance
- **APOE Orchestration**: Change operations orchestrated through APOE

#### 3. Multi-Language Support
**Principle**: Support all programming languages with consistent graph representation.

**Implementation**:
- **Language Mappers**: Convert language-specific ASTs to universal nodes
- **Type Unification**: Unify type systems across languages
- **Relationship Mapping**: Map language-specific relationships to universal edges
- **Semantic Preservation**: Preserve language-specific semantics

**AIM-OS Integration**:
- **IIS Intuition**: Language-specific understanding enhanced by intuitive intelligence
- **SEG Synthesis**: Multi-language patterns synthesized into knowledge
- **APOE Planning**: Language-specific insights compiled into execution plans
- **SDF-CVF Gating**: Multi-language quality ensured through gating

#### 4. Real-Time Processing
**Principle**: Process changes in real-time for live codebase intelligence.

**Implementation**:
- **Event-Driven Architecture**: Changes trigger immediate graph updates
- **Streaming Processing**: Continuous processing of code changes
- **Low-Latency Updates**: Minimal delay between change and graph update
- **Scalable Processing**: Handle high-frequency changes efficiently

**AIM-OS Integration**:
- **TCS Timeline**: Real-time changes stream to timeline
- **CMC Storage**: Real-time graph updates stored as CMC atoms
- **VIF Tracking**: Real-time operations tracked with confidence
- **APOE Orchestration**: Real-time changes trigger execution plans

### Graph Construction Pipeline

#### Stage 1: AST Ingestion

**Purpose**: Receive and validate parsed ASTs from the Parser Service.

**Implementation**:
```python
class ASTIngestionService:
    def __init__(self, cmc: CMCIntegration, vif: VIFIntegration, tcs: TCSIntegration):
        self.cmc = cmc
        self.vif = vif
        self.tcs = tcs
        self.ast_queue = asyncio.Queue()
        
    async def ingest_ast(self, ast: AST, language: str, file_path: str) -> None:
        """Ingest AST for graph construction."""
        try:
            # Validate AST
            validation_result = await self._validate_ast(ast, language)
            if not validation_result.valid:
                raise InvalidASTError(validation_result.errors)
            
            # Create ingestion event
            ingestion_event = ASTIngestionEvent(
                ast=ast,
                language=language,
                file_path=file_path,
                timestamp=datetime.utcnow()
            )
            
            # Stream to TCS timeline
            await self.tcs.stream_ast_ingestion_event(ingestion_event)
            
            # Store in CMC
            await self._store_ast_in_cmc(ingestion_event)
            
            # Track with VIF
            await self._track_ast_ingestion_provenance(ingestion_event)
            
            # Queue for processing
            await self.ast_queue.put(ingestion_event)
            
        except Exception as e:
            logger.error(f"Error ingesting AST: {e}")
            raise
    
    async def _validate_ast(self, ast: AST, language: str) -> ValidationResult:
        """Validate AST before processing."""
        # Validate AST structure
        structure_validation = await self._validate_ast_structure(ast)
        
        # Validate language compatibility
        language_validation = await self._validate_language_compatibility(ast, language)
        
        # Validate semantic consistency
        semantic_validation = await self._validate_semantic_consistency(ast)
        
        return ValidationResult(
            valid=structure_validation.valid and language_validation.valid and semantic_validation.valid,
            errors=structure_validation.errors + language_validation.errors + semantic_validation.errors
        )
```

**AIM-OS Integration**:
- **CMC Storage**: ASTs stored as CMC atoms with bitemporal tracking
- **VIF Provenance**: Ingestion operations tracked with confidence scores
- **TCS Timeline**: Ingestion events stream to timeline
- **APOE Orchestration**: Ingestion triggers construction planning

#### Stage 2: Node Mapping

**Purpose**: Map AST nodes to universal CPG nodes.

**Implementation**:
```python
class NodeMappingService:
    def __init__(self, cmc: CMCIntegration, vif: VIFIntegration, tcs: TCSIntegration):
        self.cmc = cmc
        self.vif = vif
        self.tcs = tcs
        self.language_mappers = self._initialize_language_mappers()
        
    async def map_ast_nodes(self, ast: AST, language: str) -> List[CPGNode]:
        """Map AST nodes to CPG nodes."""
        try:
            # Get language mapper
            mapper = self.language_mappers.get(language)
            if not mapper:
                raise UnsupportedLanguageError(f"Unsupported language: {language}")
            
            # Map nodes
            cpg_nodes = []
            for ast_node in ast.nodes:
                cpg_node = await mapper.map_node(ast_node, language)
                cpg_nodes.append(cpg_node)
            
            # Stream mapping events
            await self.tcs.stream_node_mapping_events(cpg_nodes)
            
            # Store in CMC
            await self._store_cpg_nodes_in_cmc(cpg_nodes)
            
            # Track with VIF
            await self._track_node_mapping_provenance(cpg_nodes, ast)
            
            return cpg_nodes
            
        except Exception as e:
            logger.error(f"Error mapping AST nodes: {e}")
            raise
    
    def _initialize_language_mappers(self) -> Dict[str, LanguageMapper]:
        """Initialize language-specific mappers."""
        return {
            'python': PythonMapper(),
            'javascript': JavaScriptMapper(),
            'typescript': TypeScriptMapper(),
            'java': JavaMapper(),
            'csharp': CSharpMapper(),
            'cpp': CppMapper(),
            'c': CMapper(),
            'go': GoMapper(),
            'rust': RustMapper(),
            'swift': SwiftMapper(),
            'kotlin': KotlinMapper(),
            'scala': ScalaMapper()
        }
```

**AIM-OS Integration**:
- **CMC Storage**: CPG nodes stored as CMC atoms
- **VIF Provenance**: Mapping operations tracked with confidence
- **TCS Timeline**: Mapping events stream to timeline
- **SEG Synthesis**: Node patterns synthesized into knowledge

#### Stage 3: Edge Construction

**Purpose**: Create relationships between CPG nodes.

**Implementation**:
```python
class EdgeConstructionService:
    def __init__(self, cmc: CMCIntegration, vif: VIFIntegration, tcs: TCSIntegration):
        self.cmc = cmc
        self.vif = vif
        self.tcs = tcs
        self.edge_constructors = self._initialize_edge_constructors()
        
    async def construct_edges(self, cpg_nodes: List[CPGNode], ast: AST, language: str) -> List[CPGEdge]:
        """Construct edges between CPG nodes."""
        try:
            # Get edge constructor
            constructor = self.edge_constructors.get(language)
            if not constructor:
                raise UnsupportedLanguageError(f"Unsupported language: {language}")
            
            # Construct edges
            cpg_edges = []
            
            # Function call edges
            call_edges = await constructor.construct_call_edges(cpg_nodes, ast)
            cpg_edges.extend(call_edges)
            
            # Inheritance edges
            inheritance_edges = await constructor.construct_inheritance_edges(cpg_nodes, ast)
            cpg_edges.extend(inheritance_edges)
            
            # Composition edges
            composition_edges = await constructor.construct_composition_edges(cpg_nodes, ast)
            cpg_edges.extend(composition_edges)
            
            # Import edges
            import_edges = await constructor.construct_import_edges(cpg_nodes, ast)
            cpg_edges.extend(import_edges)
            
            # Dependency edges
            dependency_edges = await constructor.construct_dependency_edges(cpg_nodes, ast)
            cpg_edges.extend(dependency_edges)
            
            # Stream edge construction events
            await self.tcs.stream_edge_construction_events(cpg_edges)
            
            # Store in CMC
            await self._store_cpg_edges_in_cmc(cpg_edges)
            
            # Track with VIF
            await self._track_edge_construction_provenance(cpg_edges, ast)
            
            return cpg_edges
            
        except Exception as e:
            logger.error(f"Error constructing edges: {e}")
            raise
```

**AIM-OS Integration**:
- **CMC Storage**: CPG edges stored as CMC atoms
- **VIF Provenance**: Edge construction tracked with confidence
- **TCS Timeline**: Edge construction events stream to timeline
- **SEG Synthesis**: Edge patterns synthesized into knowledge

#### Stage 4: Graph Assembly

**Purpose**: Assemble the complete CPG from nodes and edges.

**Implementation**:
```python
class GraphAssemblyService:
    def __init__(self, cmc: CMCIntegration, vif: VIFIntegration, tcs: TCSIntegration, hhni: HHNIIntegration):
        self.cmc = cmc
        self.vif = vif
        self.tcs = tcs
        self.hhni = hhni
        self.graph_builder = CPGGraphBuilder()
        
    async def assemble_graph(
        self,
        cpg_nodes: List[CPGNode],
        cpg_edges: List[CPGEdge],
        file_path: str,
        language: str
    ) -> CPGGraph:
        """Assemble complete CPG from nodes and edges."""
        try:
            # Create graph
            graph = await self.graph_builder.build_graph(cpg_nodes, cpg_edges)
            
            # Add metadata
            graph.metadata = CPGGraphMetadata(
                file_path=file_path,
                language=language,
                node_count=len(cpg_nodes),
                edge_count=len(cpg_edges),
                construction_timestamp=datetime.utcnow(),
                version="1.0.0"
            )
            
            # Validate graph
            validation_result = await self._validate_graph(graph)
            if not validation_result.valid:
                raise InvalidGraphError(validation_result.errors)
            
            # Index for HHNI
            await self._index_graph_for_hhni(graph)
            
            # Stream assembly events
            await self.tcs.stream_graph_assembly_events(graph)
            
            # Store in CMC
            await self._store_graph_in_cmc(graph)
            
            # Track with VIF
            await self._track_graph_assembly_provenance(graph)
            
            return graph
            
        except Exception as e:
            logger.error(f"Error assembling graph: {e}")
            raise
    
    async def _index_graph_for_hhni(self, graph: CPGGraph) -> None:
        """Index graph for HHNI retrieval."""
        try:
            # Create HHNI index
            index = await self.hhni.create_graph_index(graph)
            
            # Optimize for physics
            optimized_index = await self.hhni.optimize_graph_index(index)
            
            # Store index
            await self.hhni.store_graph_index(optimized_index)
            
        except Exception as e:
            logger.error(f"Error indexing graph for HHNI: {e}")
            raise
```

**AIM-OS Integration**:
- **CMC Storage**: Complete graph stored as CMC atoms
- **HHNI Indexing**: Graph indexed for physics-based retrieval
- **VIF Provenance**: Assembly operations tracked with confidence
- **TCS Timeline**: Assembly events stream to timeline

### Incremental Construction

#### Change Detection

**Purpose**: Identify what has changed in the codebase.

**Implementation**:
```python
class ChangeDetectionService:
    def __init__(self, cmc: CMCIntegration, vif: VIFIntegration, tcs: TCSIntegration):
        self.cmc = cmc
        self.vif = vif
        self.tcs = tcs
        self.change_detector = CodeChangeDetector()
        
    async def detect_changes(
        self,
        current_ast: AST,
        previous_ast: Optional[AST],
        file_path: str
    ) -> ChangeDetectionResult:
        """Detect changes between current and previous AST."""
        try:
            if previous_ast is None:
                # First time processing
                return ChangeDetectionResult(
                    change_type=ChangeType.FULL,
                    affected_nodes=[],
                    affected_edges=[],
                    confidence=1.0
                )
            
            # Compare ASTs
            comparison_result = await self.change_detector.compare_asts(current_ast, previous_ast)
            
            # Determine change type
            change_type = await self._determine_change_type(comparison_result)
            
            # Identify affected nodes and edges
            affected_nodes = await self._identify_affected_nodes(comparison_result)
            affected_edges = await self._identify_affected_edges(comparison_result)
            
            # Create change detection result
            result = ChangeDetectionResult(
                change_type=change_type,
                affected_nodes=affected_nodes,
                affected_edges=affected_edges,
                confidence=comparison_result.confidence,
                timestamp=datetime.utcnow()
            )
            
            # Stream change detection events
            await self.tcs.stream_change_detection_events(result)
            
            # Store in CMC
            await self._store_change_detection_in_cmc(result)
            
            # Track with VIF
            await self._track_change_detection_provenance(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error detecting changes: {e}")
            raise
```

**AIM-OS Integration**:
- **CMC Storage**: Change detection results stored as CMC atoms
- **VIF Provenance**: Change detection tracked with confidence
- **TCS Timeline**: Change detection events stream to timeline
- **APOE Orchestration**: Changes trigger reconstruction planning

#### Delta Construction

**Purpose**: Reconstruct only affected parts of the graph.

**Implementation**:
```python
class DeltaConstructionService:
    def __init__(self, cmc: CMCIntegration, vif: VIFIntegration, tcs: TCSIntegration):
        self.cmc = cmc
        self.vif = vif
        self.tcs = tcs
        self.delta_builder = DeltaGraphBuilder()
        
    async def construct_delta(
        self,
        change_result: ChangeDetectionResult,
        current_ast: AST,
        previous_graph: CPGGraph,
        language: str
    ) -> DeltaConstructionResult:
        """Construct delta changes to the graph."""
        try:
            # Determine construction strategy
            strategy = await self._determine_construction_strategy(change_result)
            
            # Construct delta
            if strategy == ConstructionStrategy.INCREMENTAL:
                delta_result = await self._construct_incremental_delta(change_result, current_ast, previous_graph, language)
            elif strategy == ConstructionStrategy.PARTIAL:
                delta_result = await self._construct_partial_delta(change_result, current_ast, previous_graph, language)
            else:
                delta_result = await self._construct_full_delta(change_result, current_ast, previous_graph, language)
            
            # Stream delta construction events
            await self.tcs.stream_delta_construction_events(delta_result)
            
            # Store in CMC
            await self._store_delta_construction_in_cmc(delta_result)
            
            # Track with VIF
            await self._track_delta_construction_provenance(delta_result)
            
            return delta_result
            
        except Exception as e:
            logger.error(f"Error constructing delta: {e}")
            raise
```

**AIM-OS Integration**:
- **CMC Storage**: Delta construction results stored as CMC atoms
- **VIF Provenance**: Delta construction tracked with confidence
- **TCS Timeline**: Delta construction events stream to timeline
- **APOE Orchestration**: Delta construction orchestrated through APOE

### Performance Characteristics

#### Construction Performance
- **Node Mapping**: <1ms per 100 nodes
- **Edge Construction**: <2ms per 100 edges
- **Graph Assembly**: <5ms per 1000 nodes
- **Delta Construction**: <10ms for typical changes

#### Scalability
- **Concurrent Construction**: 50+ files per second
- **Memory Usage**: <200MB per 100,000 nodes
- **CPU Usage**: <30% on 8-core system
- **Disk I/O**: <5MB/s for typical workloads

#### Reliability
- **Construction Success Rate**: >99.9%
- **Consistency Validation**: 100% of graphs validated
- **Error Recovery**: Automatic error recovery
- **Monitoring**: Real-time construction monitoring

This L2 architecture provides comprehensive technical details for implementing the Graph Construction Service with full AIM-OS integration, including incremental construction, performance characteristics, and scalability considerations.
