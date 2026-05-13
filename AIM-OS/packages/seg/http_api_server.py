#!/usr/bin/env python3
"""
SEG HTTP API Server

HTTP API wrapper for SEG (Shared Evidence Graph) service.
Provides REST endpoints for entity tracking, lineage queries, and provenance tracking.

Author: Aether
Date: 2025-01-27
Purpose: Enable TypeScript clients to track provenance via HTTP API
"""

from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime
import logging
import sys
from pathlib import Path

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from seg.seg_graph import SEGGraph, Entity, Relation, Evidence, RelationType
except ImportError as e:
    logging.warning(f"SEG imports failed: {e}. Using mock mode.")
    SEGGraph = None
    Entity = None
    Relation = None
    Evidence = None
    RelationType = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="SEG API",
    description="HTTP API for Shared Evidence Graph - Provenance Tracking & Entity Lineage",
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

# Global SEG instance
seg_graph: Optional[SEGGraph] = None

# Request/Response Models
class EntityCreateRequest(BaseModel):
    """Request model for entity creation"""
    id: str = Field(..., description="Entity ID")
    type: str = Field(default="quaternion_entity", description="Entity type")
    name: str = Field(..., description="Entity name")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Entity attributes (including qaddr)")

class EntityResponse(BaseModel):
    """Response model for entity"""
    id: str
    type: str
    name: str
    attributes: Dict[str, Any]

class EvidenceCreateRequest(BaseModel):
    """Request model for evidence creation"""
    id: Optional[str] = None
    content: str = Field(..., description="Evidence content")
    source: str = Field(default="quaternion_kernel", description="Evidence source")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

class RelationCreateRequest(BaseModel):
    """Request model for relation creation"""
    source_id: str = Field(..., description="Source entity ID")
    target_id: str = Field(..., description="Target entity ID")
    relation_type: str = Field(..., description="Relation type")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

class SyscallTrackRequest(BaseModel):
    """Request model for syscall tracking"""
    entity_id: str = Field(..., description="Entity ID")
    syscall_type: str = Field(..., description="Syscall type (place|move|sense|emit)")
    success: bool = Field(..., description="Whether syscall succeeded")
    errors: List[str] = Field(default_factory=list, description="Error messages if failed")

class LineageResponse(BaseModel):
    """Response model for entity lineage"""
    entities: List[EntityResponse] = Field(..., description="Lineage entities")

class RelationsResponse(BaseModel):
    """Response model for entity relations"""
    relations: List[Dict[str, Any]] = Field(..., description="Relations")

# Initialize SEG on startup
@app.on_event("startup")
async def startup_event():
    """Initialize SEG graph"""
    global seg_graph
    
    try:
        if SEGGraph is None:
            logger.warning("SEG not available, using mock mode")
            return
        
        # Initialize SEG graph
        seg_graph = SEGGraph()
        
        logger.info("SEG initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize SEG: {e}")
        logger.warning("Continuing in mock mode")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "seg_available": seg_graph is not None,
        "version": "1.0.0"
    }

@app.post("/entities", response_model=EntityResponse)
async def create_entity(request: EntityCreateRequest):
    """Create entity in SEG"""
    if seg_graph is None:
        raise HTTPException(status_code=503, detail="SEG not available")
    
    try:
        # Create entity
        entity = Entity(
            id=request.id,
            type=request.type,
            name=request.name,
            attributes=request.attributes
        )
        
        # Add to graph
        added_entity = seg_graph.add_entity(entity)
        
        return EntityResponse(
            id=added_entity.id,
            type=added_entity.type,
            name=added_entity.name,
            attributes=added_entity.attributes
        )
    except Exception as e:
        logger.error(f"Entity creation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Entity creation failed: {str(e)}")

@app.post("/evidence", response_model=Dict[str, str])
async def create_evidence(request: EvidenceCreateRequest):
    """Create evidence in SEG"""
    if seg_graph is None:
        raise HTTPException(status_code=503, detail="SEG not available")
    
    try:
        # Create evidence
        evidence_id = request.id or f"evidence_{datetime.now().timestamp()}"
        evidence = Evidence(
            id=evidence_id,
            content=request.content,
            source=request.source,
            confidence=request.confidence
        )
        
        # Add to graph
        added_evidence = seg_graph.add_evidence(evidence)
        
        return {"id": added_evidence.id, "status": "created"}
    except Exception as e:
        logger.error(f"Evidence creation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Evidence creation failed: {str(e)}")

@app.post("/relations", response_model=Dict[str, str])
async def create_relation(request: RelationCreateRequest):
    """Create relation in SEG"""
    if seg_graph is None:
        raise HTTPException(status_code=503, detail="SEG not available")
    
    try:
        # Map relation_type string to RelationType enum
        if RelationType:
            type_map = {
                "derives_from": RelationType.DERIVES_FROM,
                "has_evidence": RelationType.SUPPORTS,
                "supports": RelationType.SUPPORTS,
                "contradicts": RelationType.CONTRADICTS,
            }
            relation_type = type_map.get(request.relation_type.lower(), RelationType.SUPPORTS)
        else:
            relation_type = request.relation_type
        
        # Create relation
        relation = Relation(
            id=f"rel_{request.source_id}_{request.relation_type}_{request.target_id}_{int(datetime.now().timestamp())}",
            source_id=request.source_id,
            target_id=request.target_id,
            relation_type=relation_type if isinstance(relation_type, str) else relation_type.value,
            confidence=request.confidence
        )
        
        # Add to graph
        added_relation = seg_graph.add_relation(relation)
        
        return {"id": added_relation.id, "status": "created"}
    except Exception as e:
        logger.error(f"Relation creation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Relation creation failed: {str(e)}")

@app.post("/track-syscall", response_model=Dict[str, str])
async def track_syscall(request: SyscallTrackRequest):
    """Track syscall execution in SEG"""
    if seg_graph is None:
        raise HTTPException(status_code=503, detail="SEG not available")
    
    try:
        # Create evidence for syscall
        evidence_id = f"{request.entity_id}_{request.syscall_type}_{int(datetime.now().timestamp())}"
        evidence_content = f"{request.syscall_type} syscall on {request.entity_id}"
        if request.errors:
            evidence_content += f" (errors: {', '.join(request.errors)})"
        
        evidence_request = EvidenceCreateRequest(
            id=evidence_id,
            content=evidence_content,
            source="quaternion_kernel",
            confidence=1.0 if request.success else 0.0
        )
        
        await create_evidence(evidence_request)
        
        # Create relation from entity to evidence
        relation_request = RelationCreateRequest(
            source_id=request.entity_id,
            target_id=evidence_id,
            relation_type="has_evidence",
            confidence=1.0
        )
        
        await create_relation(relation_request)
        
        return {"status": "tracked", "evidence_id": evidence_id}
    except Exception as e:
        logger.error(f"Syscall tracking failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Syscall tracking failed: {str(e)}")

@app.get("/entities/{entity_id}/lineage", response_model=LineageResponse)
async def get_entity_lineage(entity_id: str):
    """Get entity lineage (provenance chain)"""
    if seg_graph is None:
        raise HTTPException(status_code=503, detail="SEG not available")
    
    try:
        # Get lineage from SEG
        lineage = seg_graph.get_entity_history(entity_id)
        
        # Transform to response format
        entities = []
        for entity in lineage:
            entities.append(EntityResponse(
                id=entity.id,
                type=entity.type,
                name=entity.name,
                attributes=entity.attributes
            ))
        
        return LineageResponse(entities=entities)
    except Exception as e:
        logger.error(f"Lineage query failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lineage query failed: {str(e)}")

@app.get("/entities/{entity_id}/relations", response_model=RelationsResponse)
async def get_entity_relations(entity_id: str):
    """Get entity relations"""
    if seg_graph is None:
        raise HTTPException(status_code=503, detail="SEG not available")
    
    try:
        # Get relations from SEG
        incoming = seg_graph.get_incoming_relations(entity_id)
        outgoing = seg_graph.get_outgoing_relations(entity_id)
        
        # Transform to response format
        relations = []
        for relation in incoming + outgoing:
            relations.append({
                "id": relation.id,
                "source_id": relation.source_id,
                "target_id": relation.target_id,
                "relation_type": relation.relation_type.value if hasattr(relation.relation_type, 'value') else str(relation.relation_type),
                "confidence": relation.confidence
            })
        
        return RelationsResponse(relations=relations)
    except Exception as e:
        logger.error(f"Relations query failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Relations query failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5002)

