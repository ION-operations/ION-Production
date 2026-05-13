"""
Router & Log-Sentinels API Server - Main FastAPI Application

# NL_TAG: ROUTER-API-SERVER-001 | Main FastAPI application for Router and Log-Sentinels API endpoints | create_app() -> FastAPI | []
# NL_TAG_CONNECT: ROUTER-API-MCP-001 | API server uses MCP client for AIM-OS integration | create_app → MCPClient | [ROUTER-API-SERVER-001, ROUTER-API-MCP-001]
# NL_TAG_INTENT: ROUTER-API-DESIGN-001 | FastAPI chosen for async support, automatic OpenAPI docs, and Python ecosystem compatibility | FastAPI framework | [ADR-API-SERVER]
# NL_TAG_SPEC: ROUTER-API-SPEC-001 | Validates API request/response schemas using Pydantic | Pydantic models | [api_schemas.py]
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import logging
from typing import Optional
import os

from router_api_server.mcp_client import MCPClient
from router_api_server.services.router_service import RouterService
from router_api_server.services.log_sentinels_service import LogSentinelsService
from router_api_server.routes import router_routes, log_sentinels_routes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Returns:
        Configured FastAPI app instance
    """
    app = FastAPI(
        title="Router & Log-Sentinels API Server",
        description="API server for Router (APOE-MCP Router) and Log-Sentinels (Hybrid Log Analysis System)",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:3000"],  # DAC V2 IDE ports
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize MCP client
    mcp_client = MCPClient(
        command_server_url=os.getenv("COMMAND_SERVER_URL", "http://localhost:5001")
    )
    
    # Initialize services
    router_service = RouterService(mcp_client=mcp_client)
    log_sentinels_service = LogSentinelsService(mcp_client=mcp_client)
    
    # Dependency injection
    def get_router_service() -> RouterService:
        return router_service
    
    def get_log_sentinels_service() -> LogSentinelsService:
        return log_sentinels_service
    
    # Store services in app state for dependency injection
    app.state.router_service = router_service
    app.state.log_sentinels_service = log_sentinels_service
    
    # Include routers
    app.include_router(
        router_routes.router,
        prefix="/api/router",
        tags=["router"]
    )
    
    app.include_router(
        log_sentinels_routes.router,
        prefix="/api/log-sentinels",
        tags=["log-sentinels"]
    )
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "service": "router-log-sentinels-api-server",
            "version": "1.0.0"
        }
    
    logger.info("Router & Log-Sentinels API Server initialized")
    
    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

