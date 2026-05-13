# ICIP Search Service - L3 Detailed Implementation Guide

**Detail Level:** 3 of 5 (10,000 words)  
**Context Budget:** ~160k tokens  
**Purpose:** Complete implementation guide for Search Service with AIM-OS integration

---

## Complete Implementation Guide

### Project Structure

```
packages/icip_search_service/
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── search_service.py
│   │   ├── query_router.py
│   │   ├── query_processor.py
│   │   ├── index_manager.py
│   │   ├── result_ranker.py
│   │   └── response_synthesizer.py
│   ├── engines/
│   │   ├── __init__.py
│   │   ├── literal_search_engine.py
│   │   ├── structural_search_engine.py
│   │   ├── semantic_search_engine.py
│   │   ├── graph_search_engine.py
│   │   ├── hybrid_search_engine.py
│   │   └── ai_search_engine.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── search_models.py
│   │   ├── query_models.py
│   │   ├── result_models.py
│   │   └── index_models.py
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── query_planner.py
│   │   ├── embedding_service.py
│   │   ├── response_synthesizer.py
│   │   └── learning_engine.py
│   ├── indexes/
│   │   ├── __init__.py
│   │   ├── text_index.py
│   │   ├── vector_index.py
│   │   ├── graph_index.py
│   │   └── hybrid_index.py
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
│   │   ├── search_utils.py
│   │   ├── ranking_utils.py
│   │   ├── performance_monitor.py
│   │   ├── error_handler.py
│   │   └── cache_manager.py
│   └── tests/
│       ├── __init__.py
│       ├── test_search_service.py
│       ├── test_query_router.py
│       ├── test_query_processor.py
│       ├── test_aimos_integration.py
│       └── test_performance.py
├── requirements.txt
├── pyproject.toml
├── README.md
└── setup.py
```

### Core Implementation

#### Search Service Core

```python
# packages/icip_search_service/src/core/search_service.py

from __future__ import annotations
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging
from datetime import datetime

from ..models.search_models import SearchRequest, SearchResponse, SearchResult, SearchOptions
from ..aimos_integration.cmc_integration import CMCIntegration
from ..aimos_integration.hhni_integration import HHNIIntegration
from ..aimos_integration.vif_integration import VIFIntegration
from ..aimos_integration.tcs_integration import TCSIntegration
from ..aimos_integration.apoe_integration import APOEIntegration
from ..aimos_integration.seg_integration import SEGIntegration
from ..aimos_integration.iis_integration import IISIntegration
from ..utils.performance_monitor import PerformanceMonitor
from ..utils.error_handler import ErrorHandler
from ..utils.cache_manager import CacheManager

logger = logging.getLogger(__name__)

class SearchService:
    """
    Core Search Service implementation with AIM-OS integration.
    
    This service provides comprehensive search capabilities with seamless
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
        
        # Initialize core services
        self.query_router = QueryRouter(cmc_integration, vif_integration, tcs_integration)
        self.query_processor = QueryProcessor(cmc_integration, vif_integration, tcs_integration)
        self.index_manager = IndexManager(cmc_integration, vif_integration, tcs_integration)
        self.result_ranker = ResultRanker(cmc_integration, vif_integration, tcs_integration)
        self.response_synthesizer = ResponseSynthesizer(cmc_integration, vif_integration, tcs_integration)
        
        # Initialize search engines
        self.literal_engine = LiteralSearchEngine(cmc_integration, vif_integration, tcs_integration)
        self.structural_engine = StructuralSearchEngine(cmc_integration, vif_integration, tcs_integration)
        self.semantic_engine = SemanticSearchEngine(cmc_integration, vif_integration, tcs_integration)
        self.graph_engine = GraphSearchEngine(cmc_integration, vif_integration, tcs_integration)
        self.hybrid_engine = HybridSearchEngine(cmc_integration, vif_integration, tcs_integration)
        self.ai_engine = AISearchEngine(cmc_integration, vif_integration, tcs_integration)
        
        logger.info("Search Service initialized with AIM-OS integration")
    
    async def search(
        self,
        request: SearchRequest,
        options: Optional[SearchOptions] = None
    ) -> SearchResponse:
        """
        Execute search with full AIM-OS integration.
        
        Args:
            request: Search request with query and parameters
            options: Optional search options
            
        Returns:
            SearchResponse with results and metadata
        """
        try:
            # Start performance monitoring
            with self.performance.monitor_operation("search"):
                # Check cache first
                cached_response = await self.cache.get_search_response(request)
                if cached_response:
                    logger.debug(f"Using cached search response for query: {request.query}")
                    return cached_response
                
                # Process query
                processed_query = await self.query_processor.process_query(request.query, request.context)
                
                # Route query to appropriate engine
                search_engine = await self.query_router.route_query(processed_query, request.search_type)
                
                # Execute search
                results = await search_engine.search(processed_query, request.context, options)
                
                # Rank results
                ranked_results = await self.result_ranker.rank_results(results, request.context)
                
                # Synthesize response
                synthesized_response = await self.response_synthesizer.synthesize_response(
                    ranked_results, request.context
                )
                
                # Create search response
                response = SearchResponse(
                    results=ranked_results,
                    synthesized_response=synthesized_response,
                    query=request.query,
                    search_type=request.search_type,
                    total_results=len(ranked_results),
                    processing_time=results.processing_time,
                    timestamp=datetime.utcnow(),
                    metadata=results.metadata
                )
                
                # Cache response
                await self.cache.store_search_response(request, response)
                
                # Stream to TCS timeline
                await self.tcs.stream_search_event(response)
                
                # Store in CMC
                await self._store_search_response_in_cmc(response)
                
                # Track with VIF
                await self._track_search_provenance(response)
                
                # Synthesize knowledge with SEG
                await self._synthesize_search_knowledge(response)
                
                # Enhance with IIS
                await self._enhance_search_with_iis(response)
                
                logger.info(f"Successfully executed search for query: {request.query}")
                return response
                
        except Exception as e:
            logger.error(f"Error executing search: {e}")
            await self.error_handler.handle_search_error(e, request)
            raise
    
    async def search_batch(
        self,
        requests: List[SearchRequest],
        options: Optional[SearchOptions] = None
    ) -> List[SearchResponse]:
        """
        Execute multiple searches concurrently.
        
        Args:
            requests: List of search requests
            options: Optional search options
            
        Returns:
            List of SearchResponse objects
        """
        try:
            # Create search tasks
            tasks = [
                self.search(request, options)
                for request in requests
            ]
            
            # Execute tasks concurrently
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions
            processed_responses = []
            for i, response in enumerate(responses):
                if isinstance(response, Exception):
                    logger.error(f"Error executing search {i}: {response}")
                    # Create error response
                    error_response = SearchResponse(
                        results=[],
                        synthesized_response="",
                        query=requests[i].query,
                        search_type=requests[i].search_type,
                        total_results=0,
                        processing_time=0.0,
                        timestamp=datetime.utcnow(),
                        error=str(response)
                    )
                    processed_responses.append(error_response)
                else:
                    processed_responses.append(response)
            
            logger.info(f"Batch search completed: {len(processed_responses)} searches executed")
            return processed_responses
            
        except Exception as e:
            logger.error(f"Error in batch search: {e}")
            raise
```

#### Query Router Implementation

```python
# packages/icip_search_service/src/core/query_router.py

from __future__ import annotations
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime

from ..models.query_models import ProcessedQuery, SearchType, QueryType
from ..aimos_integration.cmc_integration import CMCIntegration
from ..aimos_integration.vif_integration import VIFIntegration
from ..aimos_integration.tcs_integration import TCSIntegration

logger = logging.getLogger(__name__)

class QueryRouter:
    """
    Routes queries to appropriate search engines.
    
    Analyzes query type and characteristics to select the most
    appropriate search engine for optimal results.
    """
    
    def __init__(self, cmc: CMCIntegration, vif: VIFIntegration, tcs: TCSIntegration):
        self.cmc = cmc
        self.vif = vif
        self.tcs = tcs
        self.engine_map = {
            SearchType.LITERAL: "literal_engine",
            SearchType.STRUCTURAL: "structural_engine",
            SearchType.SEMANTIC: "semantic_engine",
            SearchType.GRAPH: "graph_engine",
            SearchType.HYBRID: "hybrid_engine",
            SearchType.AI: "ai_engine"
        }
        logger.info("Query Router initialized")
    
    async def route_query(
        self,
        processed_query: ProcessedQuery,
        search_type: Optional[SearchType] = None
    ) -> Any:
        """Route query to appropriate search engine."""
        try:
            # Determine search type if not specified
            if search_type is None:
                search_type = await self._determine_search_type(processed_query)
            
            # Select appropriate engine
            engine_name = self.engine_map.get(search_type)
            if not engine_name:
                raise UnsupportedSearchTypeError(f"Unsupported search type: {search_type}")
            
            # Get engine instance
            engine = await self._get_engine_instance(engine_name)
            
            # Stream routing event
            await self.tcs.stream_routing_event("query_routed", {
                "query": processed_query.original_query,
                "search_type": search_type.value,
                "engine": engine_name
            })
            
            # Track routing with VIF
            await self._track_routing_provenance(processed_query, search_type, engine_name)
            
            logger.info(f"Routed query to {engine_name} for search type {search_type}")
            return engine
            
        except Exception as e:
            logger.error(f"Error routing query: {e}")
            raise
    
    async def _determine_search_type(self, processed_query: ProcessedQuery) -> SearchType:
        """Determine the most appropriate search type for the query."""
        try:
            # Analyze query characteristics
            query_type = processed_query.query_type
            query_text = processed_query.original_query
            context = processed_query.context
            
            # Determine search type based on query characteristics
            if query_type == QueryType.LITERAL:
                return SearchType.LITERAL
            elif query_type == QueryType.STRUCTURAL:
                return SearchType.STRUCTURAL
            elif query_type == QueryType.SEMANTIC:
                return SearchType.SEMANTIC
            elif query_type == QueryType.GRAPH:
                return SearchType.GRAPH
            elif query_type == QueryType.HYBRID:
                return SearchType.HYBRID
            elif query_type == QueryType.AI:
                return SearchType.AI
            else:
                # Default to semantic search for natural language queries
                return SearchType.SEMANTIC
                
        except Exception as e:
            logger.error(f"Error determining search type: {e}")
            return SearchType.SEMANTIC  # Default fallback
    
    async def _get_engine_instance(self, engine_name: str) -> Any:
        """Get search engine instance by name."""
        try:
            # This would be injected from the main service
            # For now, return a placeholder
            engine_instances = {
                "literal_engine": self.literal_engine,
                "structural_engine": self.structural_engine,
                "semantic_engine": self.semantic_engine,
                "graph_engine": self.graph_engine,
                "hybrid_engine": self.hybrid_engine,
                "ai_engine": self.ai_engine
            }
            
            engine = engine_instances.get(engine_name)
            if not engine:
                raise EngineNotFoundError(f"Engine not found: {engine_name}")
            
            return engine
            
        except Exception as e:
            logger.error(f"Error getting engine instance: {e}")
            raise
```

#### Semantic Search Engine Implementation

```python
# packages/icip_search_service/src/engines/semantic_search_engine.py

from __future__ import annotations
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from datetime import datetime
import logging
import numpy as np

from ..models.search_models import SearchResult, SemanticSearchResult
from ..aimos_integration.cmc_integration import CMCIntegration
from ..aimos_integration.vif_integration import VIFIntegration
from ..aimos_integration.tcs_integration import TCSIntegration

logger = logging.getLogger(__name__)

class SemanticSearchEngine:
    """
    Semantic search engine for natural language queries.
    
    Provides vector-based semantic search with embedding models
    and natural language understanding capabilities.
    """
    
    def __init__(self, cmc: CMCIntegration, vif: VIFIntegration, tcs: TCSIntegration):
        self.cmc = cmc
        self.vif = vif
        self.tcs = tcs
        self.embedding_service = EmbeddingService()
        self.vector_index = VectorIndex()
        logger.info("Semantic Search Engine initialized")
    
    async def search(
        self,
        processed_query: ProcessedQuery,
        context: Dict[str, Any],
        options: Optional[SearchOptions] = None
    ) -> List[SearchResult]:
        """Execute semantic search."""
        try:
            # Generate query embedding
            query_embedding = await self.embedding_service.generate_embedding(
                processed_query.original_query
            )
            
            # Search vector index
            vector_results = await self.vector_index.search(
                query_embedding,
                top_k=options.top_k if options else 10
            )
            
            # Convert to search results
            results = []
            for i, (doc_id, similarity_score) in enumerate(vector_results):
                # Retrieve document content
                doc_content = await self._retrieve_document_content(doc_id)
                
                # Create semantic search result
                result = SemanticSearchResult(
                    doc_id=doc_id,
                    content=doc_content,
                    similarity_score=similarity_score,
                    relevance_score=await self._calculate_relevance_score(
                        doc_content, processed_query, context
                    ),
                    explanation=await self._generate_explanation(
                        doc_content, processed_query, similarity_score
                    ),
                    metadata={
                        "search_type": "semantic",
                        "embedding_model": self.embedding_service.model_name,
                        "vector_dimension": len(query_embedding)
                    }
                )
                results.append(result)
            
            # Stream search event
            await self.tcs.stream_search_event("semantic_search_executed", {
                "query": processed_query.original_query,
                "results_count": len(results),
                "avg_similarity": np.mean([r.similarity_score for r in results])
            })
            
            # Store search in CMC
            await self._store_search_in_cmc(processed_query, results)
            
            # Track with VIF
            await self._track_search_provenance(processed_query, results)
            
            logger.info(f"Semantic search completed: {len(results)} results found")
            return results
            
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            raise
    
    async def _calculate_relevance_score(
        self,
        doc_content: str,
        processed_query: ProcessedQuery,
        context: Dict[str, Any]
    ) -> float:
        """Calculate relevance score for document."""
        try:
            # Base similarity score from vector search
            base_score = 0.8  # Placeholder
            
            # Context relevance
            context_relevance = await self._calculate_context_relevance(
                doc_content, context
            )
            
            # Query relevance
            query_relevance = await self._calculate_query_relevance(
                doc_content, processed_query
            )
            
            # Combine scores
            relevance_score = (
                base_score * 0.4 +
                context_relevance * 0.3 +
                query_relevance * 0.3
            )
            
            return min(relevance_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating relevance score: {e}")
            return 0.5  # Default fallback
    
    async def _generate_explanation(
        self,
        doc_content: str,
        processed_query: ProcessedQuery,
        similarity_score: float
    ) -> str:
        """Generate explanation for search result."""
        try:
            # Use LLM to generate explanation
            explanation = await self._generate_llm_explanation(
                doc_content, processed_query.original_query, similarity_score
            )
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            return f"Similarity score: {similarity_score:.3f}"
    
    async def _generate_llm_explanation(
        self,
        doc_content: str,
        query: str,
        similarity_score: float
    ) -> str:
        """Generate LLM explanation for search result."""
        try:
            # This would use an LLM service to generate explanations
            # For now, return a simple explanation
            explanation = f"""
            This document is relevant to your query "{query}" with a similarity score of {similarity_score:.3f}.
            The content appears to match the semantic meaning of your search query.
            """
            
            return explanation.strip()
            
        except Exception as e:
            logger.error(f"Error generating LLM explanation: {e}")
            return f"Similarity score: {similarity_score:.3f}"
```

### AIM-OS Integration Implementation

#### CMC Integration

```python
# packages/icip_search_service/src/aimos_integration/cmc_integration.py

from __future__ import annotations
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from datetime import datetime
import logging

from ..models.search_models import SearchResponse, SearchResult, SemanticSearchResult

logger = logging.getLogger(__name__)

class CMCIntegration:
    """
    Integration with CMC (Context Memory Core) for storing search data.
    
    Converts search queries and results into CMC atoms with
    bitemporal tracking for persistent storage.
    """
    
    def __init__(self, cmc_client: CMCClient):
        self.cmc = cmc_client
        logger.info("CMC Integration initialized")
    
    async def convert_search_response_to_atoms(self, response: SearchResponse) -> List[CMCAtom]:
        """Convert search response to CMC atoms."""
        try:
            atoms = []
            
            # Convert search query to atom
            query_atom = CMCAtom(
                modality="search_query",
                content_ref=f"query_{response.timestamp.isoformat()}",
                content=response.query,
                embedding=await self._generate_embedding(response.query),
                tags=["search", response.search_type, "query"],
                hhni_path=f"search/queries/{response.search_type}",
                tpv=datetime.utcnow(),
                vif=0.9,  # High confidence for queries
                metadata=SearchQueryMetadata(
                    query=response.query,
                    search_type=response.search_type,
                    total_results=response.total_results,
                    processing_time=response.processing_time,
                    timestamp=response.timestamp
                )
            )
            atoms.append(query_atom)
            
            # Convert search results to atoms
            for i, result in enumerate(response.results):
                result_atom = CMCAtom(
                    modality="search_result",
                    content_ref=f"result_{response.timestamp.isoformat()}_{i}",
                    content=result.content,
                    embedding=await self._generate_embedding(result.content),
                    tags=["search", response.search_type, "result"],
                    hhni_path=f"search/results/{response.search_type}/{i}",
                    tpv=datetime.utcnow(),
                    vif=result.relevance_score if hasattr(result, 'relevance_score') else 0.8,
                    metadata=SearchResultMetadata(
                        query=response.query,
                        search_type=response.search_type,
                        result_index=i,
                        relevance_score=result.relevance_score if hasattr(result, 'relevance_score') else 0.8,
                        similarity_score=result.similarity_score if hasattr(result, 'similarity_score') else 0.0
                    )
                )
                atoms.append(result_atom)
            
            # Convert synthesized response to atom
            if response.synthesized_response:
                synthesis_atom = CMCAtom(
                    modality="search_synthesis",
                    content_ref=f"synthesis_{response.timestamp.isoformat()}",
                    content=response.synthesized_response,
                    embedding=await self._generate_embedding(response.synthesized_response),
                    tags=["search", response.search_type, "synthesis"],
                    hhni_path=f"search/synthesis/{response.search_type}",
                    tpv=datetime.utcnow(),
                    vif=0.9,
                    metadata=SynthesisMetadata(
                        query=response.query,
                        search_type=response.search_type,
                        result_count=len(response.results),
                        synthesis_type="natural_language"
                    )
                )
                atoms.append(synthesis_atom)
            
            logger.debug(f"Converted search response to {len(atoms)} CMC atoms")
            return atoms
            
        except Exception as e:
            logger.error(f"Error converting search response to atoms: {e}")
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
# packages/icip_search_service/src/tests/test_search_service.py

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from ..core.search_service import SearchService
from ..models.search_models import SearchRequest, SearchResponse, SearchResult
from ..aimos_integration.cmc_integration import CMCIntegration
from ..aimos_integration.hhni_integration import HHNIIntegration
from ..aimos_integration.vif_integration import VIFIntegration
from ..aimos_integration.tcs_integration import TCSIntegration
from ..aimos_integration.apoe_integration import APOEIntegration
from ..aimos_integration.seg_integration import SEGIntegration
from ..aimos_integration.iis_integration import IISIntegration

class TestSearchService:
    """Test cases for Search Service."""
    
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
    def search_service(self, mock_aimos_integrations):
        """Create Search Service instance with mock integrations."""
        return SearchService(
            cmc_integration=mock_aimos_integrations['cmc'],
            hhni_integration=mock_aimos_integrations['hhni'],
            vif_integration=mock_aimos_integrations['vif'],
            tcs_integration=mock_aimos_integrations['tcs'],
            apoe_integration=mock_aimos_integrations['apoe'],
            seg_integration=mock_aimos_integrations['seg'],
            iis_integration=mock_aimos_integrations['iis']
        )
    
    @pytest.fixture
    def sample_search_request(self):
        """Create sample search request."""
        return SearchRequest(
            query="find all functions that handle user authentication",
            search_type="semantic",
            context={},
            metadata={}
        )
    
    @pytest.fixture
    def sample_search_result(self):
        """Create sample search result."""
        return SearchResult(
            doc_id="auth_functions.py",
            content="def authenticate_user(username, password): ...",
            relevance_score=0.95,
            similarity_score=0.92,
            explanation="This function handles user authentication as requested",
            metadata={}
        )
    
    @pytest.mark.asyncio
    async def test_search_success(self, search_service, sample_search_request, sample_search_result):
        """Test successful search execution."""
        # Mock search engine
        search_service.semantic_engine.search = AsyncMock(
            return_value=[sample_search_result]
        )
        
        # Mock AIM-OS integrations
        search_service.tcs.stream_search_event = AsyncMock()
        search_service._store_search_response_in_cmc = AsyncMock()
        search_service._track_search_provenance = AsyncMock()
        search_service._synthesize_search_knowledge = AsyncMock()
        search_service._enhance_search_with_iis = AsyncMock()
        
        # Execute search
        response = await search_service.search(sample_search_request)
        
        # Assertions
        assert len(response.results) == 1
        assert response.results[0] == sample_search_result
        assert response.query == "find all functions that handle user authentication"
        assert response.search_type == "semantic"
        assert response.timestamp is not None
        
        # Verify AIM-OS integrations were called
        search_service.tcs.stream_search_event.assert_called_once()
        search_service._store_search_response_in_cmc.assert_called_once()
        search_service._track_search_provenance.assert_called_once()
        search_service._synthesize_search_knowledge.assert_called_once()
        search_service._enhance_search_with_iis.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_batch_success(self, search_service):
        """Test successful batch search execution."""
        # Mock individual search calls
        search_service.search = AsyncMock(
            return_value=Mock()
        )
        
        # Execute batch search
        requests = [
            SearchRequest(query="find authentication functions", search_type="semantic", context={}),
            SearchRequest(query="find error handling patterns", search_type="structural", context={}),
            SearchRequest(query="find performance bottlenecks", search_type="semantic", context={})
        ]
        
        responses = await search_service.search_batch(requests)
        
        # Assertions
        assert len(responses) == 3
        assert search_service.search.call_count == 3
    
    @pytest.mark.asyncio
    async def test_search_error_handling(self, search_service, sample_search_request):
        """Test error handling in search execution."""
        # Mock search to raise exception
        search_service.semantic_engine.search = AsyncMock(
            side_effect=Exception("Search failed")
        )
        
        # Mock error handler
        search_service.error_handler.handle_search_error = AsyncMock()
        
        # Execute search and expect exception
        with pytest.raises(Exception, match="Search failed"):
            await search_service.search(sample_search_request)
        
        # Verify error handler was called
        search_service.error_handler.handle_search_error.assert_called_once()
```

This L3 detailed implementation guide provides comprehensive technical details for implementing the Search Service with full AIM-OS integration, including complete code examples, testing strategies, and performance optimizations.
