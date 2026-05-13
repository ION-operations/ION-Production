# ICIP Graph Construction Service - L3 Detailed Implementation Guide

**Detail Level:** 3 of 5 (10,000 words)  
**Context Budget:** ~160k tokens  
**Purpose:** Complete implementation guide for Graph Construction Service with AIM-OS integration

---

## Complete Implementation Guide

### Project Structure

```
packages/icip_graph_construction_service/
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── graph_construction_service.py
│   │   ├── ast_ingestion_service.py
│   │   ├── node_mapping_service.py
│   │   ├── edge_construction_service.py
│   │   ├── graph_assembly_service.py
│   │   └── incremental_construction_service.py
│   ├── mappers/
│   │   ├── __init__.py
│   │   ├── base_mapper.py
│   │   ├── python_mapper.py
│   │   ├── javascript_mapper.py
│   │   ├── typescript_mapper.py
│   │   ├── java_mapper.py
│   │   ├── csharp_mapper.py
│   │   ├── cpp_mapper.py
│   │   ├── c_mapper.py
│   │   ├── go_mapper.py
│   │   ├── rust_mapper.py
│   │   ├── swift_mapper.py
│   │   ├── kotlin_mapper.py
│   │   └── scala_mapper.py
│   ├── constructors/
│   │   ├── __init__.py
│   │   ├── base_constructor.py
│   │   ├── call_edge_constructor.py
│   │   ├── inheritance_edge_constructor.py
│   │   ├── composition_edge_constructor.py
│   │   ├── import_edge_constructor.py
│   │   └── dependency_edge_constructor.py
│   ├── incremental/
│   │   ├── __init__.py
│   │   ├── change_detection_service.py
│   │   ├── delta_construction_service.py
│   │   ├── consistency_checker.py
│   │   └── change_analyzer.py
│   ├── aimos_integration/
│   │   ├── __init__.py
│   │   ├── cmc_integration.py
│   │   ├── hhni_integration.py
│   │   ├── vif_integration.py
│   │   ├── tcs_integration.py
│   │   ├── apoe_integration.py
│   │   ├── seg_integration.py
│   │   └── iis_integration.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── cpg_models.py
│   │   ├── construction_models.py
│   │   ├── change_models.py
│   │   └── incremental_models.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── graph_validator.py
│   │   ├── performance_monitor.py
│   │   ├── error_handler.py
│   │   └── cache_manager.py
│   └── tests/
│       ├── __init__.py
│       ├── test_graph_construction_service.py
│       ├── test_ast_ingestion_service.py
│       ├── test_node_mapping_service.py
│       ├── test_edge_construction_service.py
│       ├── test_graph_assembly_service.py
│       ├── test_incremental_construction_service.py
│       ├── test_aimos_integration.py
│       └── test_performance.py
├── requirements.txt
├── pyproject.toml
├── README.md
└── setup.py
```

### Core Implementation

#### Graph Construction Service Core

```python
# packages/icip_graph_construction_service/src/core/graph_construction_service.py

from __future__ import annotations
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging
from datetime import datetime

from ..models.cpg_models import CPGGraph, CPGNode, CPGEdge, CPGGraphMetadata
from ..models.construction_models import ConstructionRequest, ConstructionResponse, ConstructionOptions, ConstructionStrategy
from ..models.change_models import ChangeDetectionResult, ChangeType, DeltaConstructionResult
from ..aimos_integration.cmc_integration import CMCIntegration
from ..aimos_integration.hhni_integration import HHNIIntegration
from ..aimos_integration.vif_integration import VIFIntegration
from ..aimos_integration.tcs_integration import TCSIntegration
from ..aimos_integration.apoe_integration import APOEIntegration
from ..aimos_integration.seg_integration import SEGIntegration
from ..aimos_integration.iis_integration import IISIntegration
from ..utils.graph_validator import GraphValidator
from ..utils.performance_monitor import PerformanceMonitor
from ..utils.error_handler import ErrorHandler
from ..utils.cache_manager import CacheManager

logger = logging.getLogger(__name__)

class GraphConstructionService:
    """
    Core Graph Construction Service implementation with AIM-OS integration.
    
    This service provides comprehensive graph construction capabilities with seamless
    integration into the AIM-OS consciousness infrastructure.
    """
    
    def __init__(
        self,
        cmc_integration: CMCIntegration,
        hhni_integration: HHNIIntegration,
        vif_integration: VIFIntegration,
        tcs_integration: TCSIntegration,
        apoe_integration: APOEIntegration,
        seg_integration: SEGIntegration,
        iis_integration: IISIntegration,
        cache_manager: Optional[CacheManager] = None,
        performance_monitor: Optional[PerformanceMonitor] = None,
        error_handler: Optional[ErrorHandler] = None
    ):
        self.cmc = cmc_integration
        self.hhni = hhni_integration
        self.vif = vif_integration
        self.tcs = tcs_integration
        self.apoe = apoe_integration
        self.seg = seg_integration
        self.iis = iis_integration
        self.cache = cache_manager or CacheManager()
        self.performance = performance_monitor or PerformanceMonitor()
        self.error_handler = error_handler or ErrorHandler()
        
        # Initialize construction services
        self.ast_ingestion = ASTIngestionService(cmc_integration, vif_integration, tcs_integration)
        self.node_mapping = NodeMappingService(cmc_integration, vif_integration, tcs_integration)
        self.edge_construction = EdgeConstructionService(cmc_integration, vif_integration, tcs_integration)
        self.graph_assembly = GraphAssemblyService(cmc_integration, vif_integration, tcs_integration, hhni_integration)
        self.incremental_construction = IncrementalConstructionService(cmc_integration, vif_integration, tcs_integration)
        
        # Initialize graph validator
        self.graph_validator = GraphValidator()
        
        logger.info("Graph Construction Service initialized with AIM-OS integration")
    
    async def construct_graph(
        self,
        ast: AST,
        language: str,
        file_path: str,
        options: Optional[ConstructionOptions] = None
    ) -> ConstructionResponse:
        """
        Construct CPG from AST using the optimal strategy.
        
        Args:
            ast: Parsed AST from Parser Service
            language: Programming language
            file_path: Path to the file
            options: Optional construction options
            
        Returns:
            ConstructionResponse with CPG and metadata
        """
        try:
            # Start performance monitoring
            with self.performance.monitor_operation("construct_graph"):
                # Create construction request
                request = ConstructionRequest(
                    ast=ast,
                    language=language,
                    file_path=file_path,
                    options=options or ConstructionOptions()
                )
                
                # Check cache first
                cached_result = await self.cache.get_construction_result(request)
                if cached_result:
                    logger.debug(f"Using cached construction result for {file_path}")
                    return cached_result
                
                # Determine construction strategy
                strategy = await self._determine_construction_strategy(request)
                
                # Construct graph using selected strategy
                if strategy == ConstructionStrategy.FULL:
                    result = await self._construct_full_graph(request)
                elif strategy == ConstructionStrategy.INCREMENTAL:
                    result = await self._construct_incremental_graph(request)
                else:
                    raise UnsupportedStrategyError(f"Unsupported strategy: {strategy}")
                
                # Validate constructed graph
                validation_result = await self.graph_validator.validate_graph(result.graph)
                if not validation_result.valid:
                    raise GraphValidationError(validation_result.errors)
                
                # Create construction response
                response = ConstructionResponse(
                    graph=result.graph,
                    strategy=strategy,
                    performance_metrics=result.performance_metrics,
                    confidence=result.confidence,
                    timestamp=datetime.utcnow()
                )
                
                # Cache result
                await self.cache.store_construction_result(request, response)
                
                # Stream to TCS timeline
                await self.tcs.stream_construction_event(response)
                
                # Store in CMC
                await self._store_construction_result_in_cmc(response)
                
                # Track with VIF
                await self._track_construction_provenance(response)
                
                # Synthesize knowledge with SEG
                await self._synthesize_construction_knowledge(response)
                
                # Enhance with IIS
                await self._enhance_construction_with_iis(response)
                
                logger.info(f"Successfully constructed graph for {file_path} using {strategy}")
                return response
                
        except Exception as e:
            logger.error(f"Error constructing graph for {file_path}: {e}")
            await self.error_handler.handle_construction_error(e, request)
            raise
    
    async def construct_graph_batch(
        self,
        files: List[Tuple[AST, str, str]],  # (ast, language, file_path)
        options: Optional[ConstructionOptions] = None
    ) -> List[ConstructionResponse]:
        """
        Construct graphs for multiple files concurrently.
        
        Args:
            files: List of (ast, language, file_path) tuples
            options: Optional construction options
            
        Returns:
            List of ConstructionResponse objects
        """
        try:
            # Create construction tasks
            tasks = [
                self.construct_graph(ast, language, file_path, options)
                for ast, language, file_path in files
            ]
            
            # Execute tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions
            responses = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Error constructing graph for file {i}: {result}")
                    # Create error response
                    error_response = ConstructionResponse(
                        graph=None,
                        strategy=None,
                        performance_metrics=None,
                        confidence=0.0,
                        timestamp=datetime.utcnow(),
                        error=str(result)
                    )
                    responses.append(error_response)
                else:
                    responses.append(result)
            
            logger.info(f"Batch construction completed: {len(responses)} files processed")
            return responses
            
        except Exception as e:
            logger.error(f"Error in batch construction: {e}")
            raise
    
    async def _construct_full_graph(self, request: ConstructionRequest) -> ConstructionResult:
        """Construct complete graph from scratch."""
        try:
            # Ingest AST
            ingestion_result = await self.ast_ingestion.ingest_ast(
                request.ast, request.language, request.file_path
            )
            
            # Map nodes
            cpg_nodes = await self.node_mapping.map_ast_nodes(
                request.ast, request.language
            )
            
            # Construct edges
            cpg_edges = await self.edge_construction.construct_edges(
                cpg_nodes, request.ast, request.language
            )
            
            # Assemble graph
            graph = await self.graph_assembly.assemble_graph(
                cpg_nodes, cpg_edges, request.file_path, request.language
            )
            
            # Calculate performance metrics
            performance_metrics = await self.performance.get_construction_metrics()
            
            # Calculate confidence
            confidence = await self._calculate_construction_confidence(graph)
            
            return ConstructionResult(
                graph=graph,
                performance_metrics=performance_metrics,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"Error in full graph construction: {e}")
            raise
    
    async def _construct_incremental_graph(self, request: ConstructionRequest) -> ConstructionResult:
        """Construct graph incrementally."""
        try:
            # Get previous graph if exists
            previous_graph = await self._get_previous_graph(request.file_path)
            
            # Detect changes
            change_result = await self.incremental_construction.detect_changes(
                request.ast, previous_graph, request.file_path
            )
            
            # Construct delta
            delta_result = await self.incremental_construction.construct_delta(
                change_result, request.ast, previous_graph, request.language
            )
            
            # Apply delta to previous graph
            graph = await self._apply_delta_to_graph(previous_graph, delta_result)
            
            # Calculate performance metrics
            performance_metrics = await self.performance.get_construction_metrics()
            
            # Calculate confidence
            confidence = await self._calculate_construction_confidence(graph)
            
            return ConstructionResult(
                graph=graph,
                performance_metrics=performance_metrics,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"Error in incremental graph construction: {e}")
            raise
    
    async def _determine_construction_strategy(self, request: ConstructionRequest) -> ConstructionStrategy:
        """Determine optimal construction strategy."""
        try:
            # Check if previous graph exists
            previous_graph = await self._get_previous_graph(request.file_path)
            
            if previous_graph is None:
                return ConstructionStrategy.FULL
            
            # Analyze AST complexity
            complexity = await self._analyze_ast_complexity(request.ast)
            
            # Determine strategy based on complexity and change rate
            if complexity < 0.5:
                return ConstructionStrategy.INCREMENTAL
            else:
                return ConstructionStrategy.FULL
                
        except Exception as e:
            logger.error(f"Error determining construction strategy: {e}")
            return ConstructionStrategy.FULL
    
    async def _store_construction_result_in_cmc(self, response: ConstructionResponse) -> None:
        """Store construction result in CMC with bitemporal tracking."""
        try:
            # Convert graph to CMC atoms
            atoms = await self.cmc.convert_graph_to_atoms(response.graph)
            
            # Store with bitemporal tracking
            await self.cmc.store_atoms_with_bitemporal(atoms)
            
            logger.debug("Construction result stored in CMC")
            
        except Exception as e:
            logger.error(f"Error storing construction result in CMC: {e}")
            raise
    
    async def _track_construction_provenance(self, response: ConstructionResponse) -> None:
        """Track construction operation provenance with VIF."""
        try:
            # Create provenance witness
            witness = await self.vif.create_construction_witness(
                operation="construct_graph",
                input_data=response.graph,
                output_data=response,
                confidence=response.confidence,
                strategy=response.strategy.name,
                performance_metrics=response.performance_metrics
            )
            
            # Store witness
            await self.vif.store_witness(witness)
            
            logger.debug("Construction provenance tracked with VIF")
            
        except Exception as e:
            logger.error(f"Error tracking construction provenance: {e}")
            raise
    
    async def _synthesize_construction_knowledge(self, response: ConstructionResponse) -> None:
        """Synthesize construction knowledge with SEG."""
        try:
            # Create knowledge synthesis request
            synthesis_request = await self.seg.create_construction_synthesis_request(response)
            
            # Synthesize knowledge
            synthesis_result = await self.seg.synthesize_construction_knowledge(synthesis_request)
            
            # Store synthesized knowledge
            await self.seg.store_synthesized_knowledge(synthesis_result)
            
            logger.debug("Construction knowledge synthesized with SEG")
            
        except Exception as e:
            logger.error(f"Error synthesizing construction knowledge: {e}")
            raise
    
    async def _enhance_construction_with_iis(self, response: ConstructionResponse) -> None:
        """Enhance construction result with IIS."""
        try:
            # Create IIS enhancement request
            enhancement_request = await self.iis.create_construction_enhancement_request(response)
            
            # Enhance with intuitive intelligence
            enhancement_result = await self.iis.enhance_construction_result(enhancement_request)
            
            # Apply enhancements
            await self.iis.apply_construction_enhancements(response, enhancement_result)
            
            logger.debug("Construction result enhanced with IIS")
            
        except Exception as e:
            logger.error(f"Error enhancing with IIS: {e}")
            raise
```

#### Node Mapping Implementation

```python
# packages/icip_graph_construction_service/src/mappers/python_mapper.py

from __future__ import annotations
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from datetime import datetime
import logging

from ..models.cpg_models import CPGNode, CPGNodeType, CPGNodeMetadata
from ..models.ast_models import ASTNode
from .base_mapper import BaseMapper

logger = logging.getLogger(__name__)

class PythonMapper(BaseMapper):
    """
    Maps Python AST nodes to universal CPG nodes.
    
    Handles Python-specific language constructs and maps them to
    universal CPG node types for consistent graph representation.
    """
    
    def __init__(self):
        super().__init__()
        self.node_type_mapping = self._initialize_node_type_mapping()
        logger.info("Python Mapper initialized")
    
    async def map_node(self, ast_node: ASTNode, language: str) -> CPGNode:
        """Map Python AST node to CPG node."""
        try:
            # Determine CPG node type
            cpg_type = await self._map_node_type(ast_node)
            
            # Extract node properties
            properties = await self._extract_node_properties(ast_node)
            
            # Create CPG node
            cpg_node = CPGNode(
                id=ast_node.id,
                type=cpg_type,
                name=ast_node.name,
                language=language,
                location=ast_node.location,
                properties=properties,
                metadata=CPGNodeMetadata(
                    ast_type=ast_node.type,
                    complexity=ast_node.complexity,
                    quality=ast_node.quality,
                    timestamp=datetime.utcnow()
                )
            )
            
            return cpg_node
            
        except Exception as e:
            logger.error(f"Error mapping Python node: {e}")
            raise
    
    async def _map_node_type(self, ast_node: ASTNode) -> CPGNodeType:
        """Map Python AST node type to CPG node type."""
        try:
            # Get mapping from node type mapping
            cpg_type = self.node_type_mapping.get(ast_node.type)
            
            if cpg_type is None:
                # Default to generic node type
                cpg_type = CPGNodeType.GENERIC
                logger.warning(f"Unknown Python AST node type: {ast_node.type}")
            
            return cpg_type
            
        except Exception as e:
            logger.error(f"Error mapping node type: {e}")
            return CPGNodeType.GENERIC
    
    def _initialize_node_type_mapping(self) -> Dict[str, CPGNodeType]:
        """Initialize Python AST to CPG node type mapping."""
        return {
            # Function definitions
            'FunctionDef': CPGNodeType.FUNCTION,
            'AsyncFunctionDef': CPGNodeType.FUNCTION,
            'Lambda': CPGNodeType.FUNCTION,
            
            # Class definitions
            'ClassDef': CPGNodeType.CLASS,
            
            # Variable assignments
            'Assign': CPGNodeType.VARIABLE,
            'AnnAssign': CPGNodeType.VARIABLE,
            'AugAssign': CPGNodeType.VARIABLE,
            
            # Import statements
            'Import': CPGNodeType.IMPORT,
            'ImportFrom': CPGNodeType.IMPORT,
            
            # Control flow
            'If': CPGNodeType.CONTROL_FLOW,
            'For': CPGNodeType.CONTROL_FLOW,
            'While': CPGNodeType.CONTROL_FLOW,
            'Try': CPGNodeType.CONTROL_FLOW,
            'With': CPGNodeType.CONTROL_FLOW,
            
            # Expressions
            'Call': CPGNodeType.EXPRESSION,
            'Attribute': CPGNodeType.EXPRESSION,
            'Subscript': CPGNodeType.EXPRESSION,
            'ListComp': CPGNodeType.EXPRESSION,
            'DictComp': CPGNodeType.EXPRESSION,
            'SetComp': CPGNodeType.EXPRESSION,
            'GeneratorExp': CPGNodeType.EXPRESSION,
            
            # Literals
            'Constant': CPGNodeType.LITERAL,
            'Num': CPGNodeType.LITERAL,
            'Str': CPGNodeType.LITERAL,
            'Bytes': CPGNodeType.LITERAL,
            'NameConstant': CPGNodeType.LITERAL,
            
            # Collections
            'List': CPGNodeType.COLLECTION,
            'Tuple': CPGNodeType.COLLECTION,
            'Set': CPGNodeType.COLLECTION,
            'Dict': CPGNodeType.COLLECTION,
            
            # Other
            'Name': CPGNodeType.IDENTIFIER,
            'arg': CPGNodeType.PARAMETER,
            'arguments': CPGNodeType.PARAMETER_LIST,
            'keyword': CPGNodeType.KEYWORD_ARGUMENT,
            'Global': CPGNodeType.GLOBAL,
            'Nonlocal': CPGNodeType.NONLOCAL,
            'Pass': CPGNodeType.STATEMENT,
            'Break': CPGNodeType.STATEMENT,
            'Continue': CPGNodeType.STATEMENT,
            'Return': CPGNodeType.STATEMENT,
            'Raise': CPGNodeType.STATEMENT,
            'Assert': CPGNodeType.STATEMENT,
            'Delete': CPGNodeType.STATEMENT,
            'Expr': CPGNodeType.STATEMENT,
            'Module': CPGNodeType.MODULE,
            'Interactive': CPGNodeType.MODULE,
            'Expression': CPGNodeType.MODULE,
            'Suite': CPGNodeType.BLOCK
        }
    
    async def _extract_node_properties(self, ast_node: ASTNode) -> Dict[str, Any]:
        """Extract properties from Python AST node."""
        try:
            properties = {}
            
            # Extract common properties
            if hasattr(ast_node, 'name'):
                properties['name'] = ast_node.name
            
            if hasattr(ast_node, 'lineno'):
                properties['line_number'] = ast_node.lineno
            
            if hasattr(ast_node, 'col_offset'):
                properties['column_offset'] = ast_node.col_offset
            
            # Extract type-specific properties
            if ast_node.type == 'FunctionDef':
                properties.update(await self._extract_function_properties(ast_node))
            elif ast_node.type == 'ClassDef':
                properties.update(await self._extract_class_properties(ast_node))
            elif ast_node.type == 'Import':
                properties.update(await self._extract_import_properties(ast_node))
            elif ast_node.type == 'ImportFrom':
                properties.update(await self._extract_import_from_properties(ast_node))
            
            return properties
            
        except Exception as e:
            logger.error(f"Error extracting node properties: {e}")
            return {}
    
    async def _extract_function_properties(self, ast_node: ASTNode) -> Dict[str, Any]:
        """Extract properties from function definition."""
        properties = {}
        
        try:
            # Extract function-specific properties
            if hasattr(ast_node, 'args'):
                properties['argument_count'] = len(ast_node.args.args) if ast_node.args else 0
                properties['has_defaults'] = bool(ast_node.args.defaults) if ast_node.args else False
                properties['has_varargs'] = bool(ast_node.args.vararg) if ast_node.args else False
                properties['has_kwargs'] = bool(ast_node.args.kwarg) if ast_node.args else False
            
            if hasattr(ast_node, 'decorator_list'):
                properties['decorator_count'] = len(ast_node.decorator_list)
                properties['decorators'] = [d.id for d in ast_node.decorator_list if hasattr(d, 'id')]
            
            if hasattr(ast_node, 'returns'):
                properties['has_return_annotation'] = ast_node.returns is not None
            
            if hasattr(ast_node, 'is_async'):
                properties['is_async'] = ast_node.is_async
            
            return properties
            
        except Exception as e:
            logger.error(f"Error extracting function properties: {e}")
            return {}
    
    async def _extract_class_properties(self, ast_node: ASTNode) -> Dict[str, Any]:
        """Extract properties from class definition."""
        properties = {}
        
        try:
            # Extract class-specific properties
            if hasattr(ast_node, 'bases'):
                properties['base_count'] = len(ast_node.bases)
                properties['bases'] = [base.id for base in ast_node.bases if hasattr(base, 'id')]
            
            if hasattr(ast_node, 'decorator_list'):
                properties['decorator_count'] = len(ast_node.decorator_list)
                properties['decorators'] = [d.id for d in ast_node.decorator_list if hasattr(d, 'id')]
            
            if hasattr(ast_node, 'keywords'):
                properties['keyword_count'] = len(ast_node.keywords)
            
            return properties
            
        except Exception as e:
            logger.error(f"Error extracting class properties: {e}")
            return {}
    
    async def _extract_import_properties(self, ast_node: ASTNode) -> Dict[str, Any]:
        """Extract properties from import statement."""
        properties = {}
        
        try:
            # Extract import-specific properties
            if hasattr(ast_node, 'names'):
                properties['import_count'] = len(ast_node.names)
                properties['imports'] = [name.name for name in ast_node.names]
            
            return properties
            
        except Exception as e:
            logger.error(f"Error extracting import properties: {e}")
            return {}
    
    async def _extract_import_from_properties(self, ast_node: ASTNode) -> Dict[str, Any]:
        """Extract properties from import from statement."""
        properties = {}
        
        try:
            # Extract import from specific properties
            if hasattr(ast_node, 'module'):
                properties['module'] = ast_node.module
            
            if hasattr(ast_node, 'names'):
                properties['import_count'] = len(ast_node.names)
                properties['imports'] = [name.name for name in ast_node.names]
            
            if hasattr(ast_node, 'level'):
                properties['import_level'] = ast_node.level
            
            return properties
            
        except Exception as e:
            logger.error(f"Error extracting import from properties: {e}")
            return {}
```

### AIM-OS Integration Implementation

#### CMC Integration

```python
# packages/icip_graph_construction_service/src/aimos_integration/cmc_integration.py

from __future__ import annotations
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from datetime import datetime
import logging

from ..models.cpg_models import CPGGraph, CPGNode, CPGEdge, CPGGraphMetadata

logger = logging.getLogger(__name__)

class CMCIntegration:
    """
    Integration with CMC (Context Memory Core) for storing graph data.
    
    Converts CPG graphs, nodes, and edges into CMC atoms with
    bitemporal tracking for persistent storage.
    """
    
    def __init__(self, cmc_client: CMCClient):
        self.cmc = cmc_client
        logger.info("CMC Integration initialized")
    
    async def convert_graph_to_atoms(self, graph: CPGGraph) -> List[CMCAtom]:
        """Convert CPG graph to CMC atoms."""
        try:
            atoms = []
            
            # Convert graph nodes to atoms
            for node in graph.nodes:
                atom = await self._convert_node_to_atom(node)
                atoms.append(atom)
            
            # Convert graph edges to atoms
            for edge in graph.edges:
                atom = await self._convert_edge_to_atom(edge)
                atoms.append(atom)
            
            # Convert graph metadata to atom
            metadata_atom = await self._convert_graph_metadata_to_atom(graph.metadata)
            atoms.append(metadata_atom)
            
            logger.debug(f"Converted graph to {len(atoms)} CMC atoms")
            return atoms
            
        except Exception as e:
            logger.error(f"Error converting graph to atoms: {e}")
            raise
    
    async def convert_node_to_atom(self, node: CPGNode) -> CMCAtom:
        """Convert CPG node to CMC atom."""
        try:
            atom = CMCAtom(
                modality="cpg_node",
                content_ref=node.id,
                embedding=node.embedding,
                tags=node.tags,
                hhni_path=node.hhni_path,
                tpv=node.tpv,
                vif=node.vif,
                metadata=NodeMetadata(
                    node_type=node.type,
                    node_name=node.name,
                    node_language=node.language,
                    node_location=node.location,
                    node_properties=node.properties,
                    node_complexity=node.metadata.complexity,
                    node_quality=node.metadata.quality
                )
            )
            
            return atom
            
        except Exception as e:
            logger.error(f"Error converting node to atom: {e}")
            raise
    
    async def convert_edge_to_atom(self, edge: CPGEdge) -> CMCAtom:
        """Convert CPG edge to CMC atom."""
        try:
            atom = CMCAtom(
                modality="cpg_edge",
                content_ref=edge.id,
                embedding=edge.embedding,
                tags=edge.tags,
                hhni_path=edge.hhni_path,
                tpv=edge.tpv,
                vif=edge.vif,
                metadata=EdgeMetadata(
                    edge_type=edge.type,
                    from_node=edge.from_node,
                    to_node=edge.to_node,
                    edge_weight=edge.weight,
                    edge_properties=edge.properties,
                    edge_quality=edge.metadata.quality
                )
            )
            
            return atom
            
        except Exception as e:
            logger.error(f"Error converting edge to atom: {e}")
            raise
    
    async def store_atoms_with_bitemporal(self, atoms: List[CMCAtom]) -> None:
        """Store atoms with bitemporal tracking."""
        try:
            for atom in atoms:
                # Store with bitemporal tracking
                await self.cmc.store_atom_with_bitemporal(atom)
            
            logger.debug(f"Stored {len(atoms)} atoms with bitemporal tracking")
            
        except Exception as e:
            logger.error(f"Error storing atoms with bitemporal tracking: {e}")
            raise
```

### Testing Implementation

#### Unit Tests

```python
# packages/icip_graph_construction_service/src/tests/test_graph_construction_service.py

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from ..core.graph_construction_service import GraphConstructionService
from ..models.cpg_models import CPGGraph, CPGNode, CPGEdge, CPGNodeType
from ..models.construction_models import ConstructionRequest, ConstructionOptions, ConstructionStrategy
from ..aimos_integration.cmc_integration import CMCIntegration
from ..aimos_integration.hhni_integration import HHNIIntegration
from ..aimos_integration.vif_integration import VIFIntegration
from ..aimos_integration.tcs_integration import TCSIntegration
from ..aimos_integration.apoe_integration import APOEIntegration
from ..aimos_integration.seg_integration import SEGIntegration
from ..aimos_integration.iis_integration import IISIntegration

class TestGraphConstructionService:
    """Test cases for Graph Construction Service."""
    
    @pytest.fixture
    def mock_aimos_integrations(self):
        """Create mock AIM-OS integrations."""
        return {
            'cmc': Mock(spec=CMCIntegration),
            'hhni': Mock(spec=HHNIIntegration),
            'vif': Mock(spec=VIFIntegration),
            'tcs': Mock(spec=TCSIntegration),
            'apoe': Mock(spec=APOEIntegration),
            'seg': Mock(spec=SEGIntegration),
            'iis': Mock(spec=IISIntegration)
        }
    
    @pytest.fixture
    def graph_construction_service(self, mock_aimos_integrations):
        """Create Graph Construction Service instance with mock integrations."""
        return GraphConstructionService(
            cmc_integration=mock_aimos_integrations['cmc'],
            hhni_integration=mock_aimos_integrations['hhni'],
            vif_integration=mock_aimos_integrations['vif'],
            tcs_integration=mock_aimos_integrations['tcs'],
            apoe_integration=mock_aimos_integrations['apoe'],
            seg_integration=mock_aimos_integrations['seg'],
            iis_integration=mock_aimos_integrations['iis']
        )
    
    @pytest.fixture
    def sample_ast(self):
        """Create sample AST."""
        return AST(
            nodes=[
                ASTNode(
                    id="node1",
                    type="FunctionDef",
                    name="hello_world",
                    language="python",
                    location=(1, 1),
                    complexity=1.0,
                    quality=0.95
                )
            ],
            edges=[],
            metadata=ASTMetadata(
                language="python",
                file_path="test.py",
                node_count=1,
                edge_count=0,
                complexity=1.0,
                quality=0.95,
                timestamp=datetime.utcnow()
            )
        )
    
    @pytest.fixture
    def sample_cpg_graph(self):
        """Create sample CPG graph."""
        return CPGGraph(
            nodes=[
                CPGNode(
                    id="node1",
                    type=CPGNodeType.FUNCTION,
                    name="hello_world",
                    language="python",
                    location=(1, 1),
                    properties={},
                    metadata=CPGNodeMetadata(
                        ast_type="FunctionDef",
                        complexity=1.0,
                        quality=0.95,
                        timestamp=datetime.utcnow()
                    )
                )
            ],
            edges=[],
            metadata=CPGGraphMetadata(
                file_path="test.py",
                language="python",
                node_count=1,
                edge_count=0,
                construction_timestamp=datetime.utcnow(),
                version="1.0.0"
            )
        )
    
    @pytest.mark.asyncio
    async def test_construct_graph_success(self, graph_construction_service, sample_ast, sample_cpg_graph):
        """Test successful graph construction."""
        # Mock construction result
        graph_construction_service._construct_full_graph = AsyncMock(
            return_value=ConstructionResult(
                graph=sample_cpg_graph,
                performance_metrics={},
                confidence=0.95
            )
        )
        
        # Mock graph validation
        graph_construction_service.graph_validator.validate_graph = AsyncMock(
            return_value=ValidationResult(valid=True, errors=[])
        )
        
        # Mock AIM-OS integrations
        graph_construction_service.tcs.stream_construction_event = AsyncMock()
        graph_construction_service._store_construction_result_in_cmc = AsyncMock()
        graph_construction_service._track_construction_provenance = AsyncMock()
        graph_construction_service._synthesize_construction_knowledge = AsyncMock()
        graph_construction_service._enhance_construction_with_iis = AsyncMock()
        
        # Execute construction
        result = await graph_construction_service.construct_graph(
            ast=sample_ast,
            language="python",
            file_path="test.py",
            options=ConstructionOptions()
        )
        
        # Assertions
        assert result.graph == sample_cpg_graph
        assert result.strategy == ConstructionStrategy.FULL
        assert result.confidence == 0.95
        assert result.timestamp is not None
        
        # Verify AIM-OS integrations were called
        graph_construction_service.tcs.stream_construction_event.assert_called_once()
        graph_construction_service._store_construction_result_in_cmc.assert_called_once()
        graph_construction_service._track_construction_provenance.assert_called_once()
        graph_construction_service._synthesize_construction_knowledge.assert_called_once()
        graph_construction_service._enhance_construction_with_iis.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_construct_graph_batch_success(self, graph_construction_service):
        """Test successful batch graph construction."""
        # Mock individual construction calls
        graph_construction_service.construct_graph = AsyncMock(
            return_value=Mock()
        )
        
        # Execute batch construction
        files = [
            (Mock(), "python", "file1.py"),
            (Mock(), "javascript", "file2.js"),
            (Mock(), "java", "file3.java")
        ]
        
        results = await graph_construction_service.construct_graph_batch(files)
        
        # Assertions
        assert len(results) == 3
        assert graph_construction_service.construct_graph.call_count == 3
    
    @pytest.mark.asyncio
    async def test_construct_graph_error_handling(self, graph_construction_service, sample_ast):
        """Test error handling in graph construction."""
        # Mock construction to raise exception
        graph_construction_service._construct_full_graph = AsyncMock(
            side_effect=Exception("Construction failed")
        )
        
        # Mock error handler
        graph_construction_service.error_handler.handle_construction_error = AsyncMock()
        
        # Execute construction and expect exception
        with pytest.raises(Exception, match="Construction failed"):
            await graph_construction_service.construct_graph(
                ast=sample_ast,
                language="python",
                file_path="test.py",
                options=ConstructionOptions()
            )
        
        # Verify error handler was called
        graph_construction_service.error_handler.handle_construction_error.assert_called_once()
```

This L3 detailed implementation guide provides comprehensive technical details for implementing the Graph Construction Service with full AIM-OS integration, including complete code examples, testing strategies, and performance optimizations.
