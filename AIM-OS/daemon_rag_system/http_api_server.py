#!/usr/bin/env python3
"""
Daemon/RAG System - HTTP API Server

HTTP API server for daemon system, exposing REST endpoints for Cursor UI integration.
Provides endpoints for health checks, status, request processing, and real-time updates.

Author: Solo
Date: 2025-10-30
Purpose: Enable Cursor UI integration via HTTP API (port 5000)
"""

from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from datetime import datetime
import json
import asyncio
import logging
from pathlib import Path
import sys

# Add daemon_rag_system to path
sys.path.insert(0, str(Path(__file__).parent))

from daemon_rag_system import DaemonRAGSystem, DaemonConfig, DaemonStatus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Daemon/RAG System API",
    description="HTTP API for Daemon/RAG System - Intelligent MCP Tool Selection",
    version="1.0.0"
)

# CORS middleware for Cursor UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to Cursor UI origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global daemon instance
daemon: Optional[DaemonRAGSystem] = None

# Request Models
class ProcessRequestModel(BaseModel):
    """Request model for processing user input"""
    user_input: str = Field(..., description="User input text")
    environment: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Environment context")
    max_tools: Optional[int] = Field(default=40, description="Maximum tools to select")
    strategy: Optional[str] = Field(default="BALANCED", description="Selection strategy")

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    daemon_status: str
    version: str = "1.0.0"

class StatusResponse(BaseModel):
    """Daemon status response"""
    status: str
    metrics: Dict[str, Any]
    server_status: Dict[str, Any]
    resource_usage: Dict[str, Any]
    configuration: Dict[str, Any]

class ProcessResponse(BaseModel):
    """Request processing response"""
    success: bool
    selected_tools: List[str]
    context_profile: Dict[str, Any]
    selection_result: Dict[str, Any]
    server_management: Optional[Dict[str, Any]] = None
    performance_metrics: Dict[str, Any]
    daemon_metrics: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None
    error: Optional[str] = None

# Initialize daemon on startup
@app.on_event("startup")
async def startup_event():
    """Initialize daemon system on startup"""
    global daemon
    try:
        config = DaemonConfig(
            max_tools=40,
            learning_enabled=True,
            performance_monitoring_enabled=True
        )
        daemon = DaemonRAGSystem(config)
        success = daemon.start()
        if success:
            logger.info("Daemon system started successfully")
        else:
            logger.error("Failed to start daemon system")
            daemon = None
    except Exception as e:
        logger.error(f"Error starting daemon: {e}")
        daemon = None

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown daemon system on shutdown"""
    global daemon
    if daemon:
        try:
            daemon.stop()
            logger.info("Daemon system stopped")
        except Exception as e:
            logger.error(f"Error stopping daemon: {e}")

# API Endpoints

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy" if daemon else "unavailable",
        timestamp=datetime.now().isoformat(),
        daemon_status=daemon.status.value if daemon else "stopped",
        version="1.0.0"
    )

@app.get("/api/status", response_model=StatusResponse)
async def get_status():
    """Get daemon status and metrics"""
    if not daemon:
        raise HTTPException(status_code=503, detail="Daemon not initialized")
    
    status = daemon.get_status()
    return StatusResponse(**status)

@app.post("/api/requests", response_model=ProcessResponse)
async def process_request(request: ProcessRequestModel):
    """Process a user request and return tool selection"""
    if not daemon:
        raise HTTPException(status_code=503, detail="Daemon not initialized")
    
    try:
        # Process request
        response = daemon.process_request(
            user_input=request.user_input,
            environment=request.environment or {}
        )
        
        return ProcessResponse(**response)
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tools")
async def get_tools():
    """Get available tools from registry"""
    if not daemon:
        raise HTTPException(status_code=503, detail="Daemon not initialized")
    
    try:
        tools = daemon.tool_registry.get_all_tools()
        return {
            "total_tools": len(tools),
            "tools": [
                {
                    "tool_id": tool.tool_id,
                    "name": tool.name,
                    "category": tool.category.value if hasattr(tool.category, 'value') else str(tool.category),
                    "capabilities": tool.capabilities,
                    "description": tool.description
                }
                for tool in tools
            ]
        }
    except Exception as e:
        logger.error(f"Error getting tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rag/statistics")
async def get_rag_statistics():
    """Get RAG system statistics"""
    if not daemon:
        raise HTTPException(status_code=503, detail="Daemon not initialized")
    
    try:
        stats = daemon.get_rag_statistics()
        return stats
    except Exception as e:
        logger.error(f"Error getting RAG statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/requests/{request_id}")
async def get_request_status(request_id: str):
    """Get status of a specific request (placeholder for future async support)"""
    # For now, requests are synchronous
    # In future, this can track async request status
    return {
        "request_id": request_id,
        "status": "completed",
        "message": "Synchronous requests complete immediately"
    }

@app.get("/api/stream")
async def stream_updates():
    """Stream real-time updates (Server-Sent Events)"""
    if not daemon:
        raise HTTPException(status_code=503, detail="Daemon not initialized")
    
    async def event_generator():
        """Generate SSE events"""
        while True:
            try:
                # Get current status
                status = daemon.get_status()
                yield f"data: {json.dumps(status)}\n\n"
                await asyncio.sleep(2)  # Update every 2 seconds
            except Exception as e:
                logger.error(f"Error in event stream: {e}")
                break
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")

# Main entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)

