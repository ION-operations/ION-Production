# ICIP GNN Service - L3 Detailed Implementation Guide

**Detail Level:** 3 of 5 (10,000 words)  
**Context Budget:** ~160k tokens  
**Purpose:** Complete implementation guide for GNN Service with AIM-OS integration

---

## Complete Implementation Guide

### Project Structure

```
packages/icip_gnn_service/
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── gnn_service.py
│   │   ├── graph_preprocessor.py
│   │   ├── model_selector.py
│   │   ├── gnn_processor.py
│   │   ├── feature_extractor.py
│   │   └── insight_generator.py
│   ├── engines/
│   │   ├── __init__.py
│   │   ├── base_engine.py
│   │   ├── gcn_engine.py
│   │   ├── gat_engine.py
│   │   ├── graphsage_engine.py
│   │   ├── transformer_engine.py
│   │   └── gin_engine.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── gcn_model.py
│   │   ├── gat_model.py
│   │   ├── graphsage_model.py
│   │   ├── transformer_model.py
│   │   └── gin_model.py
│   ├── features/
│   │   ├── __init__.py
│   │   ├── node_feature_extractor.py
│   │   ├── edge_feature_extractor.py
│   │   ├── graph_feature_extractor.py
│   │   └── semantic_feature_extractor.py
│   ├── insights/
│   │   ├── __init__.py
│   │   ├── pattern_insight_generator.py
│   │   ├── quality_insight_generator.py
│   │   ├── recommendation_insight_generator.py
│   │   └── anomaly_insight_generator.py
│   ├── aimos_integration/
│   │   ├── __init__.py
│   │   ├── cmc_integration.py
│   │   ├── hhni_integration.py
│   │   ├── vif_integration.py
│   │   ├── tcs_integration.py
│   │   ├── apoe_integration.py
│   │   ├── seg_integration.py
│   │   └── iis_integration.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── graph_utils.py
│   │   ├── feature_utils.py
│   │   ├── model_utils.py
│   │   ├── performance_monitor.py
│   │   ├── error_handler.py
│   │   └── cache_manager.py
│   └── tests/
│       ├── __init__.py
│       ├── test_gnn_service.py
│       ├── test_graph_preprocessor.py
│       ├── test_model_selector.py
│       ├── test_gnn_processor.py
│       ├── test_feature_extractor.py
│       ├── test_insight_generator.py
│       ├── test_aimos_integration.py
│       └── test_performance.py
├── requirements.txt
├── pyproject.toml
├── README.md
└── setup.py
```

### Core Implementation

#### GNN Service Core

```python
# packages/icip_gnn_service/src/core/gnn_service.py

from __future__ import annotations
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging
from datetime import datetime

from ..models.gnn_models import GNNResult, ExtractedFeatures, GeneratedInsights, PreprocessedGraph
from ..models.processing_models import ProcessingRequest, ProcessingResponse, ProcessingOptions, ProcessingStrategy
from ..aimos_integration.cmc_integration import CMCIntegration
from ..aimos_integration.hhni_integration import HHNIIntegration
from ..aimos_integration.vif_integration import VIFIntegration
from ..aimos_integration.tcs_integration import TCSIntegration
from ..aimos_integration.apoe_integration import APOEIntegration
from ..aimos_integration.seg_integration import SEGIntegration
from ..aimos_integration.iis_integration import IISIntegration
from ..utils.graph_utils import GraphValidator
from ..utils.performance_monitor import PerformanceMonitor
from ..utils.error_handler import ErrorHandler
from ..utils.cache_manager import CacheManager

logger = logging.getLogger(__name__)

class GNNService:
    """
    Core GNN Service implementation with AIM-OS integration.
    
    This service provides comprehensive GNN processing capabilities with seamless
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
        
        # Initialize processing services
        self.graph_preprocessor = GraphPreprocessor(cmc_integration, vif_integration, tcs_integration)
        self.model_selector = ModelSelector(cmc_integration, vif_integration, tcs_integration)
        self.gnn_processor = GNNProcessor(cmc_integration, vif_integration, tcs_integration)
        self.feature_extractor = FeatureExtractor(cmc_integration, vif_integration, tcs_integration)
        self.insight_generator = InsightGenerator(cmc_integration, vif_integration, tcs_integration)
        
        # Initialize graph validator
        self.graph_validator = GraphValidator()
        
        logger.info("GNN Service initialized with AIM-OS integration")
    
    async def process_graph(
        self,
        cpg: CPGGraph,
        task_type: str,
        file_path: str,
        options: Optional[ProcessingOptions] = None
    ) -> ProcessingResponse:
        """
        Process CPG using GNN algorithms.
        
        Args:
            cpg: Code Property Graph from Graph Construction Service
            task_type: Type of task (classification, regression, clustering, etc.)
            file_path: Path to the file
            options: Optional processing options
            
        Returns:
            ProcessingResponse with GNN results and metadata
        """
        try:
            # Start performance monitoring
            with self.performance.monitor_operation("process_graph"):
                # Create processing request
                request = ProcessingRequest(
                    cpg=cpg,
                    task_type=task_type,
                    file_path=file_path,
                    options=options or ProcessingOptions()
                )
                
                # Check cache first
                cached_result = await self.cache.get_processing_result(request)
                if cached_result:
                    logger.debug(f"Using cached processing result for {file_path}")
                    return cached_result
                
                # Determine processing strategy
                strategy = await self._determine_processing_strategy(request)
                
                # Process graph using selected strategy
                if strategy == ProcessingStrategy.BATCH:
                    result = await self._process_batch(request)
                elif strategy == ProcessingStrategy.STREAMING:
                    result = await self._process_streaming(request)
                elif strategy == ProcessingStrategy.INCREMENTAL:
                    result = await self._process_incremental(request)
                else:
                    raise UnsupportedStrategyError(f"Unsupported strategy: {strategy}")
                
                # Validate processing result
                validation_result = await self.graph_validator.validate_gnn_result(result.gnn_result)
                if not validation_result.valid:
                    raise GNNValidationError(validation_result.errors)
                
                # Create processing response
                response = ProcessingResponse(
                    gnn_result=result.gnn_result,
                    extracted_features=result.extracted_features,
                    generated_insights=result.generated_insights,
                    strategy=strategy,
                    performance_metrics=result.performance_metrics,
                    confidence=result.confidence,
                    timestamp=datetime.utcnow()
                )
                
                # Cache result
                await self.cache.store_processing_result(request, response)
                
                # Stream to TCS timeline
                await self.tcs.stream_processing_event(response)
                
                # Store in CMC
                await self._store_processing_result_in_cmc(response)
                
                # Track with VIF
                await self._track_processing_provenance(response)
                
                # Synthesize knowledge with SEG
                await self._synthesize_processing_knowledge(response)
                
                # Enhance with IIS
                await self._enhance_processing_with_iis(response)
                
                logger.info(f"Successfully processed graph for {file_path} using {strategy}")
                return response
                
        except Exception as e:
            logger.error(f"Error processing graph for {file_path}: {e}")
            await self.error_handler.handle_processing_error(e, request)
            raise
    
    async def process_graph_batch(
        self,
        files: List[Tuple[CPGGraph, str, str]],  # (cpg, task_type, file_path)
        options: Optional[ProcessingOptions] = None
    ) -> List[ProcessingResponse]:
        """
        Process multiple graphs concurrently.
        
        Args:
            files: List of (cpg, task_type, file_path) tuples
            options: Optional processing options
            
        Returns:
            List of ProcessingResponse objects
        """
        try:
            # Create processing tasks
            tasks = [
                self.process_graph(cpg, task_type, file_path, options)
                for cpg, task_type, file_path in files
            ]
            
            # Execute tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions
            responses = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Error processing graph for file {i}: {result}")
                    # Create error response
                    error_response = ProcessingResponse(
                        gnn_result=None,
                        extracted_features=None,
                        generated_insights=None,
                        strategy=None,
                        performance_metrics=None,
                        confidence=0.0,
                        timestamp=datetime.utcnow(),
                        error=str(result)
                    )
                    responses.append(error_response)
                else:
                    responses.append(result)
            
            logger.info(f"Batch processing completed: {len(responses)} files processed")
            return responses
            
        except Exception as e:
            logger.error(f"Error in batch processing: {e}")
            raise
    
    async def _process_batch(self, request: ProcessingRequest) -> ProcessingResult:
        """Process graph using batch strategy."""
        try:
            # Preprocess graph
            preprocessed_graph = await self.graph_preprocessor.preprocess_graph(
                request.cpg, request.task_type
            )
            
            # Select model
            model = await self.model_selector.select_model(
                preprocessed_graph, request.task_type
            )
            
            # Process with GNN
            gnn_result = await self.gnn_processor.process_graph(
                preprocessed_graph, model
            )
            
            # Extract features
            extracted_features = await self.feature_extractor.extract_features(
                gnn_result, request.task_type
            )
            
            # Generate insights
            generated_insights = await self.insight_generator.generate_insights(
                extracted_features, request.task_type
            )
            
            # Calculate performance metrics
            performance_metrics = await self.performance.get_processing_metrics()
            
            # Calculate confidence
            confidence = await self._calculate_processing_confidence(gnn_result)
            
            return ProcessingResult(
                gnn_result=gnn_result,
                extracted_features=extracted_features,
                generated_insights=generated_insights,
                performance_metrics=performance_metrics,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"Error in batch processing: {e}")
            raise
```

#### GCN Engine Implementation

```python
# packages/icip_gnn_service/src/engines/gcn_engine.py

from __future__ import annotations
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from datetime import datetime
import logging
import torch
import torch.nn as nn
import torch.nn.functional as F

from ..models.gnn_models import GNNResult, NodeEmbedding, EdgeEmbedding, GraphEmbedding
from ..aimos_integration.cmc_integration import CMCIntegration
from ..aimos_integration.vif_integration import VIFIntegration
from ..aimos_integration.tcs_integration import TCSIntegration

logger = logging.getLogger(__name__)

class GCNEngine:
    """
    Graph Convolutional Network engine for GNN processing.
    
    Implements GCN algorithm for node classification, feature extraction,
    and graph-level tasks.
    """
    
    def __init__(self, cmc: CMCIntegration, vif: VIFIntegration, tcs: TCSIntegration):
        self.cmc = cmc
        self.vif = vif
        self.tcs = tcs
        self.model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info("GCN Engine initialized")
    
    async def process(self, preprocessed_graph: PreprocessedGraph, model: GNNModel) -> GNNResult:
        """Process graph using GCN."""
        try:
            # Load model if not already loaded
            if self.model is None:
                self.model = await self._load_model(model)
            
            # Prepare input data
            input_data = await self._prepare_input_data(preprocessed_graph)
            
            # Run GCN forward pass
            with torch.no_grad():
                # Node embeddings
                node_embeddings = self.model.forward(input_data.x, input_data.edge_index)
                
                # Edge embeddings
                edge_embeddings = await self._compute_edge_embeddings(
                    node_embeddings, input_data.edge_index
                )
                
                # Graph embedding
                graph_embedding = await self._compute_graph_embedding(node_embeddings)
            
            # Create GNN result
            result = GNNResult(
                node_embeddings=node_embeddings,
                edge_embeddings=edge_embeddings,
                graph_embedding=graph_embedding,
                model_type='gcn',
                confidence=0.95,
                timestamp=datetime.utcnow()
            )
            
            # Stream processing events
            await self.tcs.stream_gcn_processing_events(result)
            
            # Store in CMC
            await self._store_gcn_result_in_cmc(result)
            
            # Track with VIF
            await self._track_gcn_processing_provenance(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing with GCN: {e}")
            raise
    
    async def _load_model(self, model: GNNModel) -> GCNModel:
        """Load GCN model."""
        try:
            # Create GCN model
            gcn_model = GCNModel(
                input_dim=model.input_dim,
                hidden_dim=model.hidden_dim,
                output_dim=model.output_dim,
                num_layers=model.num_layers,
                dropout=model.dropout
            )
            
            # Load weights if available
            if model.weights_path:
                gcn_model.load_state_dict(torch.load(model.weights_path))
            
            # Move to device
            gcn_model = gcn_model.to(self.device)
            
            # Set to evaluation mode
            gcn_model.eval()
            
            return gcn_model
            
        except Exception as e:
            logger.error(f"Error loading GCN model: {e}")
            raise
    
    async def _prepare_input_data(self, preprocessed_graph: PreprocessedGraph) -> InputData:
        """Prepare input data for GCN."""
        try:
            # Convert node features to tensor
            node_features = torch.tensor(preprocessed_graph.node_features, dtype=torch.float32)
            
            # Convert edge indices to tensor
            edge_indices = []
            for edge in preprocessed_graph.edges:
                edge_indices.append([edge.from_node, edge.to_node])
            edge_index = torch.tensor(edge_indices, dtype=torch.long).t().contiguous()
            
            # Create input data
            input_data = InputData(
                x=node_features,
                edge_index=edge_index,
                batch_size=len(preprocessed_graph.nodes)
            )
            
            return input_data
            
        except Exception as e:
            logger.error(f"Error preparing input data: {e}")
            raise
    
    async def _compute_edge_embeddings(
        self,
        node_embeddings: torch.Tensor,
        edge_index: torch.Tensor
    ) -> List[EdgeEmbedding]:
        """Compute edge embeddings from node embeddings."""
        try:
            edge_embeddings = []
            
            for i in range(edge_index.size(1)):
                from_node = edge_index[0, i].item()
                to_node = edge_index[1, i].item()
                
                # Concatenate node embeddings
                edge_embedding = torch.cat([
                    node_embeddings[from_node],
                    node_embeddings[to_node]
                ])
                
                edge_embeddings.append(EdgeEmbedding(
                    from_node=from_node,
                    to_node=to_node,
                    embedding=edge_embedding.tolist()
                ))
            
            return edge_embeddings
            
        except Exception as e:
            logger.error(f"Error computing edge embeddings: {e}")
            raise
    
    async def _compute_graph_embedding(self, node_embeddings: torch.Tensor) -> GraphEmbedding:
        """Compute graph-level embedding from node embeddings."""
        try:
            # Global mean pooling
            graph_embedding = torch.mean(node_embeddings, dim=0)
            
            return GraphEmbedding(
                embedding=graph_embedding.tolist(),
                pooling_method='mean',
                node_count=node_embeddings.size(0)
            )
            
        except Exception as e:
            logger.error(f"Error computing graph embedding: {e}")
            raise

class GCNModel(nn.Module):
    """Graph Convolutional Network model."""
    
    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int, num_layers: int, dropout: float = 0.5):
        super(GCNModel, self).__init__()
        
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim
        self.num_layers = num_layers
        self.dropout = dropout
        
        # Build layers
        self.layers = nn.ModuleList()
        
        # Input layer
        self.layers.append(nn.Linear(input_dim, hidden_dim))
        
        # Hidden layers
        for _ in range(num_layers - 2):
            self.layers.append(nn.Linear(hidden_dim, hidden_dim))
        
        # Output layer
        self.layers.append(nn.Linear(hidden_dim, output_dim))
        
        # Dropout
        self.dropout_layer = nn.Dropout(dropout)
    
    def forward(self, x: torch.Tensor, edge_index: torch.Tensor) -> torch.Tensor:
        """Forward pass through GCN."""
        # Apply layers
        for i, layer in enumerate(self.layers):
            x = layer(x)
            
            # Apply activation function (except for last layer)
            if i < len(self.layers) - 1:
                x = F.relu(x)
                x = self.dropout_layer(x)
        
        return x
```

### AIM-OS Integration Implementation

#### CMC Integration

```python
# packages/icip_gnn_service/src/aimos_integration/cmc_integration.py

from __future__ import annotations
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from datetime import datetime
import logging

from ..models.gnn_models import GNNResult, ExtractedFeatures, GeneratedInsights

logger = logging.getLogger(__name__)

class CMCIntegration:
    """
    Integration with CMC (Context Memory Core) for storing GNN data.
    
    Converts GNN results, features, and insights into CMC atoms with
    bitemporal tracking for persistent storage.
    """
    
    def __init__(self, cmc_client: CMCClient):
        self.cmc = cmc_client
        logger.info("CMC Integration initialized")
    
    async def convert_gnn_result_to_atoms(self, gnn_result: GNNResult) -> List[CMCAtom]:
        """Convert GNN result to CMC atoms."""
        try:
            atoms = []
            
            # Convert node embeddings to atoms
            for i, embedding in enumerate(gnn_result.node_embeddings):
                atom = CMCAtom(
                    modality="gnn_node_embedding",
                    content_ref=f"node_{i}",
                    embedding=embedding,
                    tags=["gnn", "embedding", "node"],
                    hhni_path=f"gnn/node_embeddings/{i}",
                    tpv=datetime.utcnow(),
                    vif=gnn_result.confidence,
                    metadata=NodeEmbeddingMetadata(
                        node_id=i,
                        embedding_dim=len(embedding),
                        model_type=gnn_result.model_type,
                        confidence=gnn_result.confidence
                    )
                )
                atoms.append(atom)
            
            # Convert edge embeddings to atoms
            for i, edge_embedding in enumerate(gnn_result.edge_embeddings):
                atom = CMCAtom(
                    modality="gnn_edge_embedding",
                    content_ref=f"edge_{i}",
                    embedding=edge_embedding.embedding,
                    tags=["gnn", "embedding", "edge"],
                    hhni_path=f"gnn/edge_embeddings/{i}",
                    tpv=datetime.utcnow(),
                    vif=gnn_result.confidence,
                    metadata=EdgeEmbeddingMetadata(
                        from_node=edge_embedding.from_node,
                        to_node=edge_embedding.to_node,
                        embedding_dim=len(edge_embedding.embedding),
                        model_type=gnn_result.model_type,
                        confidence=gnn_result.confidence
                    )
                )
                atoms.append(atom)
            
            # Convert graph embedding to atom
            graph_atom = CMCAtom(
                modality="gnn_graph_embedding",
                content_ref="graph",
                embedding=gnn_result.graph_embedding.embedding,
                tags=["gnn", "embedding", "graph"],
                hhni_path="gnn/graph_embeddings/graph",
                tpv=datetime.utcnow(),
                vif=gnn_result.confidence,
                metadata=GraphEmbeddingMetadata(
                    embedding_dim=len(gnn_result.graph_embedding.embedding),
                    pooling_method=gnn_result.graph_embedding.pooling_method,
                    node_count=gnn_result.graph_embedding.node_count,
                    model_type=gnn_result.model_type,
                    confidence=gnn_result.confidence
                )
            )
            atoms.append(graph_atom)
            
            logger.debug(f"Converted GNN result to {len(atoms)} CMC atoms")
            return atoms
            
        except Exception as e:
            logger.error(f"Error converting GNN result to atoms: {e}")
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
# packages/icip_gnn_service/src/tests/test_gnn_service.py

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from ..core.gnn_service import GNNService
from ..models.gnn_models import GNNResult, ExtractedFeatures, GeneratedInsights
from ..models.processing_models import ProcessingRequest, ProcessingOptions, ProcessingStrategy
from ..aimos_integration.cmc_integration import CMCIntegration
from ..aimos_integration.hhni_integration import HHNIIntegration
from ..aimos_integration.vif_integration import VIFIntegration
from ..aimos_integration.tcs_integration import TCSIntegration
from ..aimos_integration.apoe_integration import APOEIntegration
from ..aimos_integration.seg_integration import SEGIntegration
from ..aimos_integration.iis_integration import IISIntegration

class TestGNNService:
    """Test cases for GNN Service."""
    
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
    def gnn_service(self, mock_aimos_integrations):
        """Create GNN Service instance with mock integrations."""
        return GNNService(
            cmc_integration=mock_aimos_integrations['cmc'],
            hhni_integration=mock_aimos_integrations['hhni'],
            vif_integration=mock_aimos_integrations['vif'],
            tcs_integration=mock_aimos_integrations['tcs'],
            apoe_integration=mock_aimos_integrations['apoe'],
            seg_integration=mock_aimos_integrations['seg'],
            iis_integration=mock_aimos_integrations['iis']
        )
    
    @pytest.fixture
    def sample_cpg(self):
        """Create sample CPG."""
        return CPGGraph(
            nodes=[],
            edges=[],
            metadata=CPGGraphMetadata(
                file_path="test.py",
                language="python",
                node_count=0,
                edge_count=0,
                construction_timestamp=datetime.utcnow(),
                version="1.0.0"
            )
        )
    
    @pytest.fixture
    def sample_gnn_result(self):
        """Create sample GNN result."""
        return GNNResult(
            node_embeddings=[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
            edge_embeddings=[],
            graph_embedding=GraphEmbedding(embedding=[0.25, 0.35, 0.45], pooling_method="mean", node_count=2),
            model_type="gcn",
            confidence=0.95,
            timestamp=datetime.utcnow()
        )
    
    @pytest.mark.asyncio
    async def test_process_graph_success(self, gnn_service, sample_cpg, sample_gnn_result):
        """Test successful graph processing."""
        # Mock processing result
        gnn_service._process_batch = AsyncMock(
            return_value=ProcessingResult(
                gnn_result=sample_gnn_result,
                extracted_features=Mock(),
                generated_insights=Mock(),
                performance_metrics={},
                confidence=0.95
            )
        )
        
        # Mock graph validation
        gnn_service.graph_validator.validate_gnn_result = AsyncMock(
            return_value=ValidationResult(valid=True, errors=[])
        )
        
        # Mock AIM-OS integrations
        gnn_service.tcs.stream_processing_event = AsyncMock()
        gnn_service._store_processing_result_in_cmc = AsyncMock()
        gnn_service._track_processing_provenance = AsyncMock()
        gnn_service._synthesize_processing_knowledge = AsyncMock()
        gnn_service._enhance_processing_with_iis = AsyncMock()
        
        # Execute processing
        result = await gnn_service.process_graph(
            cpg=sample_cpg,
            task_type="classification",
            file_path="test.py",
            options=ProcessingOptions()
        )
        
        # Assertions
        assert result.gnn_result == sample_gnn_result
        assert result.strategy == ProcessingStrategy.BATCH
        assert result.confidence == 0.95
        assert result.timestamp is not None
        
        # Verify AIM-OS integrations were called
        gnn_service.tcs.stream_processing_event.assert_called_once()
        gnn_service._store_processing_result_in_cmc.assert_called_once()
        gnn_service._track_processing_provenance.assert_called_once()
        gnn_service._synthesize_processing_knowledge.assert_called_once()
        gnn_service._enhance_processing_with_iis.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_graph_batch_success(self, gnn_service):
        """Test successful batch graph processing."""
        # Mock individual processing calls
        gnn_service.process_graph = AsyncMock(
            return_value=Mock()
        )
        
        # Execute batch processing
        files = [
            (Mock(), "classification", "file1.py"),
            (Mock(), "regression", "file2.py"),
            (Mock(), "clustering", "file3.py")
        ]
        
        results = await gnn_service.process_graph_batch(files)
        
        # Assertions
        assert len(results) == 3
        assert gnn_service.process_graph.call_count == 3
    
    @pytest.mark.asyncio
    async def test_process_graph_error_handling(self, gnn_service, sample_cpg):
        """Test error handling in graph processing."""
        # Mock processing to raise exception
        gnn_service._process_batch = AsyncMock(
            side_effect=Exception("Processing failed")
        )
        
        # Mock error handler
        gnn_service.error_handler.handle_processing_error = AsyncMock()
        
        # Execute processing and expect exception
        with pytest.raises(Exception, match="Processing failed"):
            await gnn_service.process_graph(
                cpg=sample_cpg,
                task_type="classification",
                file_path="test.py",
                options=ProcessingOptions()
            )
        
        # Verify error handler was called
        gnn_service.error_handler.handle_processing_error.assert_called_once()
```

This L3 detailed implementation guide provides comprehensive technical details for implementing the GNN Service with full AIM-OS integration, including complete code examples, testing strategies, and performance optimizations.
