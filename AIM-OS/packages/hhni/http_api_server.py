#!/usr/bin/env python3
"""
HHNI HTTP API Server

HTTP API wrapper for HHNI (Hierarchical Hypergraph Neural Index) service.
Provides REST endpoints for tag resolution and semantic search.

Author: Aether
Date: 2025-01-27
Purpose: Enable TypeScript clients to query HHNI via HTTP API
"""

from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime
import logging
import sys
from pathlib import Path

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from hhni.hierarchical_index import HierarchicalIndex, IndexLevel
    from hhni.retrieval import TwoStageRetriever, RetrievalConfig
    from hhni.models import HHNINode
except ImportError as e:
    logging.warning(f"HHNI imports failed: {e}. Using mock mode.")
    HierarchicalIndex = None
    IndexLevel = None
    TwoStageRetriever = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="HHNI API",
    description="HTTP API for Hierarchical Hypergraph Neural Index - Tag Resolution & Semantic Search",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global HHNI instance
hhni_index: Optional[HierarchicalIndex] = None
retriever: Optional[TwoStageRetriever] = None

# Request/Response Models
class QueryRequest(BaseModel):
    """Request model for HHNI query"""
    query: str = Field(..., description="Query string")
    max_results: int = Field(default=10, description="Maximum results to return")
    target_level: str = Field(default="paragraph", description="Target index level (system|section|paragraph|sentence|subword)")

class QueryResponse(BaseModel):
    """Response model for HHNI query"""
    results: List[Dict[str, Any]] = Field(..., description="Query results")
    count: int = Field(..., description="Number of results")

class NodeResponse(BaseModel):
    """Response model for HHNI node"""
    id: str
    content: Optional[str] = None
    summary: Optional[str] = None
    score: float = Field(default=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    qaddr: Optional[Dict[str, Any]] = None

class TagResolutionRequest(BaseModel):
    """Request model for tag → QAddr resolution"""
    tag: str = Field(..., description="PLIX tag to resolve")

class TagResolutionResponse(BaseModel):
    """Response model for tag resolution"""
    tag: str
    qaddr: Optional[Dict[str, Any]] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    source: str = Field(default="hhni")

# Initialize HHNI on startup
@app.on_event("startup")
async def startup_event():
    """Initialize HHNI index and retriever"""
    global hhni_index, retriever
    
    try:
        if HierarchicalIndex is None:
            logger.warning("HHNI not available, using mock mode")
            return
        
        # Initialize hierarchical index
        hhni_index = HierarchicalIndex()
        
        # Initialize retriever
        config = RetrievalConfig(
            token_budget=4000,
            coarse_k=20,
            top_k_after_dvns=10,
            min_relevance=0.3
        )
        retriever = TwoStageRetriever(hierarchical_index=hhni_index, config=config)
        
        logger.info("HHNI initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize HHNI: {e}")
        logger.warning("Continuing in mock mode")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "hhni_available": hhni_index is not None,
        "version": "1.0.0"
    }

@app.post("/query", response_model=QueryResponse)
async def query_hhni(request: QueryRequest):
    """Query HHNI for semantic search"""
    if hhni_index is None:
        raise HTTPException(status_code=503, detail="HHNI not available")
    
    try:
        # Map target_level string to IndexLevel enum
        level_map = {
            "system": IndexLevel.SYSTEM,
            "section": IndexLevel.SECTION,
            "paragraph": IndexLevel.PARAGRAPH,
            "sentence": IndexLevel.SENTENCE,
            "subword": IndexLevel.SUBWORD,
        }
        target_level = level_map.get(request.target_level.lower(), IndexLevel.PARAGRAPH)
        
        # Query HHNI
        if retriever:
            # Use two-stage retriever
            result = retriever.retrieve(
                request.query,
                target_level=target_level,
                token_budget=4000
            )
            
            # Transform results
            results = []
            for item in result.selected_items:
                node = item.node
                results.append({
                    "id": node.id,
                    "content": node.content,
                    "summary": node.summary,
                    "score": item.score,
                    "metadata": {
                        "level": node.level.value if hasattr(node.level, 'value') else str(node.level),
                        "path": node.path,
                        "tags": dict(node.tags) if hasattr(node, 'tags') else {},
                    },
                    "qaddr": _extract_qaddr_from_node(node)
                })
        else:
            # Fallback to simple query
            nodes = hhni_index.query(
                request.query,
                target_level=target_level,
                max_results=request.max_results
            )
            
            results = []
            for node in nodes:
                results.append({
                    "id": node.id,
                    "content": node.content,
                    "summary": node.summary,
                    "score": 1.0,  # Default score
                    "metadata": {
                        "level": node.level.value if hasattr(node.level, 'value') else str(node.level),
                        "path": node.path,
                    },
                    "qaddr": _extract_qaddr_from_node(node)
                })
        
        return QueryResponse(results=results, count=len(results))
    except Exception as e:
        logger.error(f"HHNI query failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@app.get("/nodes/{node_id}", response_model=NodeResponse)
async def get_node(node_id: str):
    """Get HHNI node by ID"""
    if hhni_index is None:
        raise HTTPException(status_code=503, detail="HHNI not available")
    
    try:
        # Get node from index
        node = hhni_index.nodes.get(node_id)
        if not node:
            raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
        
        return NodeResponse(
            id=node.id,
            content=node.content,
            summary=node.summary,
            score=1.0,
            metadata={
                "level": node.level.value if hasattr(node.level, 'value') else str(node.level),
                "path": node.path,
                "tags": dict(node.tags) if hasattr(node, 'tags') else {},
            },
            qaddr=_extract_qaddr_from_node(node)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get node failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Get node failed: {str(e)}")

@app.post("/resolve-tag", response_model=TagResolutionResponse)
async def resolve_tag(request: TagResolutionRequest):
    """Resolve PLIX tag to QAddr"""
    if hhni_index is None:
        raise HTTPException(status_code=503, detail="HHNI not available")
    
    try:
        # Query HHNI for tag
        query_request = QueryRequest(
            query=request.tag,
            max_results=1,
            target_level="paragraph"
        )
        
        query_response = await query_hhni(query_request)
        
        if query_response.results:
            top_result = query_response.results[0]
            qaddr = top_result.get("qaddr")
            
            return TagResolutionResponse(
                tag=request.tag,
                qaddr=qaddr,
                confidence=0.9 if qaddr else 0.0,
                source="hhni"
            )
        else:
            return TagResolutionResponse(
                tag=request.tag,
                qaddr=None,
                confidence=0.0,
                source="hhni"
            )
    except Exception as e:
        logger.error(f"Tag resolution failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Tag resolution failed: {str(e)}")

def _extract_qaddr_from_node(node: Any) -> Optional[Dict[str, Any]]:
    """Extract QAddr from HHNI node metadata"""
    if not hasattr(node, 'tags'):
        return None
    
    tags = dict(node.tags) if hasattr(node.tags, 'items') else {}
    
    # Look for QAddr in tags or metadata
    if 'qaddr' in tags:
        qaddr = tags['qaddr']
        if isinstance(qaddr, dict):
            return qaddr
        elif isinstance(qaddr, str):
            try:
                import json
                return json.loads(qaddr)
            except:
                return None
    
    # Try to construct QAddr from individual tag components
    qaddr = {}
    if 'qaddr_n' in tags:
        qaddr['n'] = int(tags['qaddr_n'])
    if 'qaddr_l' in tags:
        qaddr['l'] = tags['qaddr_l']
    if 'qaddr_s' in tags:
        qaddr['s'] = tags['qaddr_s']
    if 'morton_key' in tags:
        qaddr['morton_key'] = int(tags['morton_key'])
    if 's3_bin' in tags:
        qaddr['s3_bin'] = int(tags['s3_bin'])
    
    return qaddr if qaddr else None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)

