# ICIP Data Storage Layer - L3 Detailed Implementation Guide

**Detail Level:** 3 of 5 (10,000 words)  
**Context Budget:** ~160k tokens  
**Purpose:** Complete implementation guide for Data Storage Layer with AIM-OS integration

---

## Complete Implementation Guide

### Project Structure

```
packages/icip_data_storage/
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── storage_service.py
│   │   ├── data_router.py
│   │   ├── query_interface.py
│   │   ├── consistency_manager.py
│   │   └── backup_manager.py
│   ├── backends/
│   │   ├── __init__.py
│   │   ├── neo4j_backend.py
│   │   ├── influxdb_backend.py
│   │   ├── elasticsearch_backend.py
│   │   ├── clickhouse_backend.py
│   │   └── redis_backend.py
│   ├── interfaces/
│   │   ├── __init__.py
│   │   ├── graph_interface.py
│   │   ├── timeseries_interface.py
│   │   ├── search_interface.py
│   │   ├── analytical_interface.py
│   │   └── cache_interface.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── storage_models.py
│   │   ├── query_models.py
│   │   ├── consistency_models.py
│   │   └── backup_models.py
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
│   │   ├── storage_utils.py
│   │   ├── query_utils.py
│   │   ├── performance_monitor.py
│   │   └── error_handler.py
│   └── tests/
│       ├── __init__.py
│       ├── test_storage_service.py
│       ├── test_backends.py
│       ├── test_aimos_integration.py
│       └── test_performance.py
├── requirements.txt
├── pyproject.toml
├── README.md
└── setup.py
```

### Core Implementation

#### Storage Service Core

```python
# packages/icip_data_storage/src/core/storage_service.py

from __future__ import annotations
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging
from datetime import datetime

from ..models.storage_models import StorageRequest, StorageResponse, StorageData, StorageOptions
from ..aimos_integration.cmc_integration import CMCIntegration
from ..aimos_integration.hhni_integration import HHNIIntegration
from ..aimos_integration.vif_integration import VIFIntegration
from ..aimos_integration.tcs_integration import TCSIntegration
from ..aimos_integration.apoe_integration import APOEIntegration
from ..aimos_integration.seg_integration import SEGIntegration
from ..aimos_integration.iis_integration import IISIntegration
from ..utils.performance_monitor import PerformanceMonitor
from ..utils.error_handler import ErrorHandler

logger = logging.getLogger(__name__)

class StorageService:
    """
    Core Storage Service implementation with AIM-OS integration.
    
    This service provides comprehensive data storage capabilities with seamless
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
        self.performance = performance_monitor or PerformanceMonitor()
        self.error_handler = error_handler or ErrorHandler()
        
        # Initialize core components
        self.data_router = DataRouter(cmc_integration, vif_integration, tcs_integration)
        self.query_interface = QueryInterface(cmc_integration, vif_integration, tcs_integration)
        self.consistency_manager = ConsistencyManager(cmc_integration, vif_integration, tcs_integration)
        self.backup_manager = BackupManager(cmc_integration, vif_integration, tcs_integration)
        
        logger.info("Storage Service initialized with AIM-OS integration")
    
    async def store_data(
        self,
        request: StorageRequest
    ) -> StorageResponse:
        """
        Execute data storage with full AIM-OS integration.
        
        Args:
            request: Storage request with data and configuration
            
        Returns:
            StorageResponse with storage result and metadata
        """
        try:
            # Start performance monitoring
            with self.performance.monitor_operation("data_storage"):
                # Route data to appropriate backend
                routing_result = await self.data_router.route_data(request.storage_data)
                
                # Store data in selected backend
                storage_result = await self._store_in_backend(routing_result)
                
                # Ensure data consistency
                consistency_result = await self.consistency_manager.ensure_consistency(storage_result)
                
                # Create storage response
                response = StorageResponse(
                    storage_data=request.storage_data,
                    routing_result=routing_result,
                    storage_result=storage_result,
                    consistency_result=consistency_result,
                    storage_config=request.storage_config,
                    storage_time=datetime.utcnow(),
                    metadata=storage_result.metadata
                )
                
                # Stream to TCS timeline
                await self.tcs.stream_storage_event(response)
                
                # Store in CMC
                await self._store_storage_data_in_cmc(response)
                
                # Track with VIF
                await self._track_storage_provenance(response)
                
                # Synthesize knowledge with SEG
                await self._synthesize_storage_knowledge(response)
                
                # Enhance with IIS
                await self._enhance_storage_with_iis(response)
                
                logger.info(f"Successfully stored data: {request.storage_data.id}")
                return response
                
        except Exception as e:
            logger.error(f"Error storing data: {e}")
            await self.error_handler.handle_storage_error(e, request)
            raise
    
    async def query_data(
        self,
        query: UnifiedQuery
    ) -> QueryResult:
        """
        Execute data query with full AIM-OS integration.
        
        Args:
            query: Unified query for data retrieval
            
        Returns:
            QueryResult with retrieved data and metadata
        """
        try:
            # Start performance monitoring
            with self.performance.monitor_operation("data_query"):
                # Execute query using appropriate interface
                result = await self.query_interface.execute_query(query)
                
                # Stream query event
                await self.tcs.stream_query_event("data_queried", {
                    "query_type": query.query_type,
                    "result_count": len(result.data),
                    "execution_time": result.execution_time
                })
                
                # Store query in CMC
                await self._store_query_in_cmc(query, result)
                
                # Track with VIF
                await self._track_query_provenance(query, result)
                
                logger.info(f"Successfully executed query: {query.query_id}")
                return result
                
        except Exception as e:
            logger.error(f"Error querying data: {e}")
            raise
```

#### Data Router Implementation

```python
# packages/icip_data_storage/src/core/data_router.py

from __future__ import annotations
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from datetime import datetime
import logging

from ..models.storage_models import StorageData, RoutingResult, DataType, BackendType
from ..backends.neo4j_backend import Neo4jBackend
from ..backends.influxdb_backend import InfluxDBBackend
from ..backends.elasticsearch_backend import ElasticsearchBackend
from ..backends.clickhouse_backend import ClickHouseBackend
from ..backends.redis_backend import RedisBackend
from ..aimos_integration.cmc_integration import CMCIntegration
from ..aimos_integration.vif_integration import VIFIntegration
from ..aimos_integration.tcs_integration import TCSIntegration

logger = logging.getLogger(__name__)

class DataRouter:
    """
    Data router for various storage backends with AIM-OS integration.
    
    Routes data to appropriate storage backends based on data type and
    access patterns, with integration into AIM-OS systems for tracking.
    """
    
    def __init__(self, cmc: CMCIntegration, vif: VIFIntegration, tcs: TCSIntegration):
        self.cmc = cmc
        self.vif = vif
        self.tcs = tcs
        self.backends = {
            BackendType.NEO4J: Neo4jBackend(),
            BackendType.INFLUXDB: InfluxDBBackend(),
            BackendType.ELASTICSEARCH: ElasticsearchBackend(),
            BackendType.CLICKHOUSE: ClickHouseBackend(),
            BackendType.REDIS: RedisBackend()
        }
        logger.info("Data Router initialized")
    
    async def route_data(self, storage_data: StorageData) -> RoutingResult:
        """Route data to appropriate storage backend."""
        try:
            # Analyze data type
            data_type = await self._analyze_data_type(storage_data)
            
            # Analyze access patterns
            access_pattern = await self._analyze_access_pattern(storage_data)
            
            # Select optimal backend
            backend_type = await self._select_optimal_backend(data_type, access_pattern)
            
            # Get backend instance
            backend = self.backends.get(backend_type)
            if not backend:
                raise UnsupportedBackendTypeError(f"Unsupported backend type: {backend_type}")
            
            # Route data
            routing_time = await self._route_to_backend(storage_data, backend)
            
            # Create routing result
            result = RoutingResult(
                storage_data=storage_data,
                backend_type=backend_type,
                routing_time=routing_time,
                metadata={
                    "data_type": data_type,
                    "access_pattern": access_pattern,
                    "routing_strategy": "content_based"
                }
            )
            
            # Stream routing event
            await self.tcs.stream_routing_event("data_routed", {
                "data_id": storage_data.id,
                "data_type": data_type,
                "backend_type": backend_type,
                "routing_time": routing_time
            })
            
            # Store routing in CMC
            await self._store_routing_in_cmc(result)
            
            # Track with VIF
            await self._track_routing_provenance(result)
            
            logger.info(f"Successfully routed data to {backend_type}: {storage_data.id}")
            return result
            
        except Exception as e:
            logger.error(f"Error routing data: {e}")
            raise
    
    async def _analyze_data_type(self, storage_data: StorageData) -> DataType:
        """Analyze data type to determine optimal backend."""
        try:
            # Analyze content structure
            content = storage_data.content
            
            # Check for graph-like structures
            if self._has_graph_structure(content):
                return DataType.GRAPH
            
            # Check for time-series data
            if self._has_timeseries_structure(content):
                return DataType.TIMESERIES
            
            # Check for searchable content
            if self._has_searchable_content(content):
                return DataType.SEARCHABLE
            
            # Check for analytical data
            if self._has_analytical_structure(content):
                return DataType.ANALYTICAL
            
            # Default to cache for simple data
            return DataType.CACHE
            
        except Exception as e:
            logger.error(f"Error analyzing data type: {e}")
            return DataType.CACHE  # Default fallback
    
    async def _analyze_access_pattern(self, storage_data: StorageData) -> str:
        """Analyze access patterns to optimize routing."""
        try:
            # Analyze metadata for access patterns
            metadata = storage_data.metadata
            
            # Check for read-heavy patterns
            if metadata.get("read_frequency", 0) > metadata.get("write_frequency", 0):
                return "read_heavy"
            
            # Check for write-heavy patterns
            if metadata.get("write_frequency", 0) > metadata.get("read_frequency", 0):
                return "write_heavy"
            
            # Check for balanced patterns
            return "balanced"
            
        except Exception as e:
            logger.error(f"Error analyzing access pattern: {e}")
            return "balanced"  # Default fallback
    
    async def _select_optimal_backend(self, data_type: DataType, access_pattern: str) -> BackendType:
        """Select optimal backend based on data type and access pattern."""
        try:
            # Map data types to backends
            type_backend_map = {
                DataType.GRAPH: BackendType.NEO4J,
                DataType.TIMESERIES: BackendType.INFLUXDB,
                DataType.SEARCHABLE: BackendType.ELASTICSEARCH,
                DataType.ANALYTICAL: BackendType.CLICKHOUSE,
                DataType.CACHE: BackendType.REDIS
            }
            
            # Get base backend
            backend_type = type_backend_map.get(data_type, BackendType.REDIS)
            
            # Adjust based on access pattern
            if access_pattern == "read_heavy" and backend_type == BackendType.REDIS:
                # Use Redis for read-heavy cache data
                pass
            elif access_pattern == "write_heavy" and backend_type == BackendType.INFLUXDB:
                # Use InfluxDB for write-heavy time-series data
                pass
            
            return backend_type
            
        except Exception as e:
            logger.error(f"Error selecting optimal backend: {e}")
            return BackendType.REDIS  # Default fallback
```

#### Neo4j Backend Implementation

```python
# packages/icip_data_storage/src/backends/neo4j_backend.py

from __future__ import annotations
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from datetime import datetime
import logging
from neo4j import GraphDatabase

from ..models.storage_models import StorageData, StorageResult, GraphData, NodeData, EdgeData

logger = logging.getLogger(__name__)

class Neo4jBackend:
    """
    Neo4j backend for graph data storage.
    
    Provides graph database functionality for storing and querying
    Code Property Graph (CPG) data.
    """
    
    def __init__(self, uri: str, username: str, password: str):
        self.uri = uri
        self.username = username
        self.password = password
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        logger.info("Neo4j Backend initialized")
    
    async def store_data(self, storage_data: StorageData) -> StorageResult:
        """Store data in Neo4j database."""
        try:
            # Convert to graph data
            graph_data = await self._convert_to_graph_data(storage_data)
            
            # Store nodes
            node_results = []
            for node in graph_data.nodes:
                node_result = await self._store_node(node)
                node_results.append(node_result)
            
            # Store edges
            edge_results = []
            for edge in graph_data.edges:
                edge_result = await self._store_edge(edge)
                edge_results.append(edge_result)
            
            # Create storage result
            result = StorageResult(
                data_id=storage_data.id,
                backend_type="neo4j",
                storage_time=datetime.utcnow(),
                data_size=len(storage_data.content),
                quality_score=0.9,  # High quality for graph data
                metadata={
                    "nodes_stored": len(node_results),
                    "edges_stored": len(edge_results),
                    "graph_id": graph_data.id
                }
            )
            
            logger.info(f"Successfully stored graph data in Neo4j: {storage_data.id}")
            return result
            
        except Exception as e:
            logger.error(f"Error storing data in Neo4j: {e}")
            raise
    
    async def query_data(self, query: str) -> List[Dict[str, Any]]:
        """Query data from Neo4j database."""
        try:
            with self.driver.session() as session:
                result = session.run(query)
                records = [record.data() for record in result]
                return records
                
        except Exception as e:
            logger.error(f"Error querying Neo4j: {e}")
            raise
    
    async def _convert_to_graph_data(self, storage_data: StorageData) -> GraphData:
        """Convert storage data to graph data."""
        try:
            # Parse content as graph data
            content = storage_data.content
            
            # Extract nodes and edges from content
            nodes = await self._extract_nodes(content)
            edges = await self._extract_edges(content)
            
            # Create graph data
            graph_data = GraphData(
                id=storage_data.id,
                nodes=nodes,
                edges=edges,
                metadata=storage_data.metadata
            )
            
            return graph_data
            
        except Exception as e:
            logger.error(f"Error converting to graph data: {e}")
            raise
    
    async def _store_node(self, node: NodeData) -> Dict[str, Any]:
        """Store a single node in Neo4j."""
        try:
            with self.driver.session() as session:
                query = """
                CREATE (n:Node {
                    id: $id,
                    label: $label,
                    properties: $properties,
                    created_at: datetime()
                })
                RETURN n
                """
                
                result = session.run(query, {
                    "id": node.id,
                    "label": node.label,
                    "properties": node.properties
                })
                
                record = result.single()
                return record.data() if record else {}
                
        except Exception as e:
            logger.error(f"Error storing node: {e}")
            raise
    
    async def _store_edge(self, edge: EdgeData) -> Dict[str, Any]:
        """Store a single edge in Neo4j."""
        try:
            with self.driver.session() as session:
                query = """
                MATCH (a:Node {id: $from_id})
                MATCH (b:Node {id: $to_id})
                CREATE (a)-[r:RELATIONSHIP {
                    type: $type,
                    properties: $properties,
                    created_at: datetime()
                }]->(b)
                RETURN r
                """
                
                result = session.run(query, {
                    "from_id": edge.from_id,
                    "to_id": edge.to_id,
                    "type": edge.type,
                    "properties": edge.properties
                })
                
                record = result.single()
                return record.data() if record else {}
                
        except Exception as e:
            logger.error(f"Error storing edge: {e}")
            raise
```

### AIM-OS Integration Implementation

#### CMC Integration

```python
# packages/icip_data_storage/src/aimos_integration/cmc_integration.py

from __future__ import annotations
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from datetime import datetime
import logging

from ..models.storage_models import StorageResponse, StorageData, QueryResult

logger = logging.getLogger(__name__)

class CMCIntegration:
    """
    Integration with CMC (Context Memory Core) for storing storage data.
    
    Converts storage operations into CMC atoms with bitemporal tracking
    for persistent storage and retrieval.
    """
    
    def __init__(self, cmc_client: CMCClient):
        self.cmc = cmc_client
        logger.info("CMC Integration initialized")
    
    async def convert_storage_response_to_atoms(self, response: StorageResponse) -> List[CMCAtom]:
        """Convert storage response to CMC atoms."""
        try:
            atoms = []
            
            # Convert storage data to atom
            if response.storage_data:
                storage_atom = CMCAtom(
                    modality="data_storage",
                    content_ref=f"stored_{response.storage_time.isoformat()}",
                    content=response.storage_data.content,
                    embedding=await self._generate_embedding(response.storage_data.content),
                    tags=["storage", response.storage_data.data_type, response.storage_result.backend_type],
                    hhni_path=f"storage/{response.storage_data.data_type}/{response.storage_data.id}",
                    tpv=datetime.utcnow(),
                    vif=response.storage_result.quality_score,
                    metadata=StorageDataMetadata(
                        data_id=response.storage_data.id,
                        data_type=response.storage_data.data_type,
                        backend_type=response.storage_result.backend_type,
                        storage_time=response.storage_time,
                        data_size=response.storage_result.data_size,
                        quality_score=response.storage_result.quality_score
                    )
                )
                atoms.append(storage_atom)
            
            # Convert routing result to atom
            if response.routing_result:
                routing_atom = CMCAtom(
                    modality="data_routing",
                    content_ref=f"routed_{response.storage_time.isoformat()}",
                    content=str(response.routing_result.metadata),
                    embedding=await self._generate_embedding(str(response.routing_result.metadata)),
                    tags=["storage", "routing", response.routing_result.backend_type],
                    hhni_path=f"storage/routing/{response.storage_data.id}",
                    tpv=datetime.utcnow(),
                    vif=0.9,
                    metadata=RoutingMetadata(
                        data_id=response.storage_data.id,
                        backend_type=response.routing_result.backend_type,
                        routing_time=response.routing_result.routing_time,
                        routing_strategy=response.routing_result.metadata.get("routing_strategy", "unknown")
                    )
                )
                atoms.append(routing_atom)
            
            logger.debug(f"Converted storage response to {len(atoms)} CMC atoms")
            return atoms
            
        except Exception as e:
            logger.error(f"Error converting storage response to atoms: {e}")
            raise
```

### Testing Implementation

#### Unit Tests

```python
# packages/icip_data_storage/src/tests/test_storage_service.py

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from ..core.storage_service import StorageService
from ..models.storage_models import StorageRequest, StorageData
from ..aimos_integration.cmc_integration import CMCIntegration
from ..aimos_integration.hhni_integration import HHNIIntegration
from ..aimos_integration.vif_integration import VIFIntegration
from ..aimos_integration.tcs_integration import TCSIntegration
from ..aimos_integration.apoe_integration import APOEIntegration
from ..aimos_integration.seg_integration import SEGIntegration
from ..aimos_integration.iis_integration import IISIntegration

class TestStorageService:
    """Test cases for Storage Service."""
    
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
    def storage_service(self, mock_aimos_integrations):
        """Create Storage Service instance with mock integrations."""
        return StorageService(
            cmc_integration=mock_aimos_integrations['cmc'],
            hhni_integration=mock_aimos_integrations['hhni'],
            vif_integration=mock_aimos_integrations['vif'],
            tcs_integration=mock_aimos_integrations['tcs'],
            apoe_integration=mock_aimos_integrations['apoe'],
            seg_integration=mock_aimos_integrations['seg'],
            iis_integration=mock_aimos_integrations['iis']
        )
    
    @pytest.fixture
    def sample_storage_request(self):
        """Create sample storage request."""
        return StorageRequest(
            storage_data=StorageData(
                id="test_data",
                data_type="graph",
                content="test content",
                metadata={}
            ),
            storage_config={}
        )
    
    @pytest.mark.asyncio
    async def test_store_data_success(self, storage_service, sample_storage_request):
        """Test successful data storage."""
        # Mock data routing
        storage_service.data_router.route_data = AsyncMock(
            return_value=Mock()
        )
        
        # Mock storage in backend
        storage_service._store_in_backend = AsyncMock(
            return_value=Mock()
        )
        
        # Mock consistency management
        storage_service.consistency_manager.ensure_consistency = AsyncMock(
            return_value=Mock()
        )
        
        # Mock AIM-OS integrations
        storage_service.tcs.stream_storage_event = AsyncMock()
        storage_service._store_storage_data_in_cmc = AsyncMock()
        storage_service._track_storage_provenance = AsyncMock()
        storage_service._synthesize_storage_knowledge = AsyncMock()
        storage_service._enhance_storage_with_iis = AsyncMock()
        
        # Execute storage
        response = await storage_service.store_data(sample_storage_request)
        
        # Assertions
        assert response is not None
        assert response.storage_data == sample_storage_request.storage_data
        assert response.storage_time is not None
        
        # Verify AIM-OS integrations were called
        storage_service.tcs.stream_storage_event.assert_called_once()
        storage_service._store_storage_data_in_cmc.assert_called_once()
        storage_service._track_storage_provenance.assert_called_once()
        storage_service._synthesize_storage_knowledge.assert_called_once()
        storage_service._enhance_storage_with_iis.assert_called_once()
```

This L3 detailed implementation guide provides comprehensive technical details for implementing the Data Storage Layer with full AIM-OS integration, including complete code examples, testing strategies, and performance optimizations.
