# ICIP Presentation & API Layer - L3 Detailed Implementation

**Detail Level:** 3 of 5 (10,000 words)  
**Context Budget:** ~160k tokens  
**Purpose:** Detailed implementation guide for Presentation & API Layer with AIM-OS integration

---

## Implementation Overview

The ICIP Presentation & API Layer implementation provides a comprehensive interface system that bridges the gap between the Integrated Codebase Intelligence Platform and external consumers. This implementation focuses on creating robust, scalable, and intelligent APIs that leverage the full power of the AIM-OS consciousness infrastructure.

### Core Implementation Principles

1. **Type-Safe Implementation**: Comprehensive type definitions and validation
2. **Async-First Design**: Non-blocking operations throughout
3. **Error Resilience**: Comprehensive error handling and recovery
4. **Performance Optimization**: Efficient data processing and delivery
5. **AIM-OS Integration**: Deep integration with consciousness systems
6. **Real-Time Capabilities**: WebSocket-based live communication
7. **Security by Design**: Built-in security and privacy protection

### Project Structure

```
packages/presentation_api_layer/
├── src/
│   ├── api/
│   │   ├── gateway/
│   │   │   ├── rest_server.py
│   │   │   ├── graphql_server.py
│   │   │   ├── grpc_server.py
│   │   │   └── auth_middleware.py
│   │   ├── endpoints/
│   │   │   ├── codebase.py
│   │   │   ├── analytics.py
│   │   │   ├── collaboration.py
│   │   │   └── insights.py
│   │   └── schemas/
│   │       ├── request_schemas.py
│   │       ├── response_schemas.py
│   │       └── validation_schemas.py
│   ├── websocket/
│   │   ├── connection_manager.py
│   │   ├── event_bus.py
│   │   ├── room_manager.py
│   │   └── message_router.py
│   ├── visualization/
│   │   ├── graph_renderer.py
│   │   ├── chart_renderer.py
│   │   ├── timeline_renderer.py
│   │   └── dashboard_builder.py
│   ├── ui/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── layouts/
│   │   └── hooks/
│   ├── integration/
│   │   ├── cmc_integration.py
│   │   ├── hhni_integration.py
│   │   ├── vif_integration.py
│   │   ├── tcs_integration.py
│   │   ├── apoe_integration.py
│   │   ├── seg_integration.py
│   │   └── iis_integration.py
│   ├── services/
│   │   ├── cache_service.py
│   │   ├── auth_service.py
│   │   ├── rate_limit_service.py
│   │   └── monitoring_service.py
│   ├── models/
│   │   ├── api_models.py
│   │   ├── websocket_models.py
│   │   ├── visualization_models.py
│   │   └── ui_models.py
│   ├── utils/
│   │   ├── response_utils.py
│   │   ├── error_utils.py
│   │   ├── validation_utils.py
│   │   └── performance_utils.py
│   └── main.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docs/
│   ├── api_documentation.md
│   ├── websocket_protocol.md
│   └── ui_components.md
├── requirements.txt
├── pyproject.toml
└── README.md
```

### Core Implementation

#### API Gateway Implementation

```python
# src/api/gateway/rest_server.py
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from ..endpoints import codebase, analytics, collaboration, insights
from ..schemas import request_schemas, response_schemas
from ..services import auth_service, rate_limit_service, cache_service
from ..integration import cmc_integration, hhni_integration, vif_integration
from ..utils import response_utils, error_utils, performance_utils

logger = logging.getLogger(__name__)

class RESTServer:
    """REST API server implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.app = FastAPI(
            title="ICIP Presentation API",
            description="Integrated Codebase Intelligence Platform API",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        self._setup_middleware()
        self._setup_routes()
        self._setup_error_handlers()
        
        # Initialize services
        self.auth_service = auth_service.AuthService(config)
        self.rate_limit_service = rate_limit_service.RateLimitService(config)
        self.cache_service = cache_service.CacheService(config)
        
        # Initialize AIM-OS integrations
        self.cmc_integration = cmc_integration.CMCIntegration(config)
        self.hhni_integration = hhni_integration.HHNIIntegration(config)
        self.vif_integration = vif_integration.VIFIntegration(config)
    
    def _setup_middleware(self):
        """Setup middleware for the FastAPI application."""
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.get("cors_origins", ["*"]),
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"]
        )
        
        # Gzip compression
        self.app.add_middleware(GZipMiddleware, minimum_size=1000)
        
        # Custom middleware for authentication and rate limiting
        self.app.middleware("http")(self._auth_middleware)
        self.app.middleware("http")(self._rate_limit_middleware)
        self.app.middleware("http")(self._performance_middleware)
    
    def _setup_routes(self):
        """Setup API routes."""
        # Health check
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "timestamp": datetime.utcnow()}
        
        # API routes
        self.app.include_router(
            codebase.router,
            prefix="/api/v1/codebase",
            tags=["codebase"]
        )
        self.app.include_router(
            analytics.router,
            prefix="/api/v1/analytics",
            tags=["analytics"]
        )
        self.app.include_router(
            collaboration.router,
            prefix="/api/v1/collaboration",
            tags=["collaboration"]
        )
        self.app.include_router(
            insights.router,
            prefix="/api/v1/insights",
            tags=["insights"]
        )
    
    def _setup_error_handlers(self):
        """Setup error handlers."""
        @self.app.exception_handler(HTTPException)
        async def http_exception_handler(request: Request, exc: HTTPException):
            return await error_utils.handle_http_exception(request, exc)
        
        @self.app.exception_handler(Exception)
        async def general_exception_handler(request: Request, exc: Exception):
            return await error_utils.handle_general_exception(request, exc)
    
    async def _auth_middleware(self, request: Request, call_next):
        """Authentication middleware."""
        # Skip auth for health check and public endpoints
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Extract token from request
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        
        if not token:
            return JSONResponse(
                status_code=401,
                content={"error": "Authentication required"}
            )
        
        # Validate token
        user = await self.auth_service.validate_token(token)
        if not user:
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid token"}
            )
        
        # Add user to request state
        request.state.user = user
        
        return await call_next(request)
    
    async def _rate_limit_middleware(self, request: Request, call_next):
        """Rate limiting middleware."""
        # Check rate limit
        if not await self.rate_limit_service.check_rate_limit(request):
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded"}
            )
        
        return await call_next(request)
    
    async def _performance_middleware(self, request: Request, call_next):
        """Performance monitoring middleware."""
        start_time = datetime.utcnow()
        
        response = await call_next(request)
        
        # Calculate response time
        response_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Log performance metrics
        await performance_utils.log_performance_metrics(
            request, response, response_time
        )
        
        return response
    
    async def start(self):
        """Start the REST server."""
        logger.info("Starting REST API server...")
        # Server startup logic
        pass
    
    async def stop(self):
        """Stop the REST server."""
        logger.info("Stopping REST API server...")
        # Server shutdown logic
        pass
```

#### WebSocket Hub Implementation

```python
# src/websocket/connection_manager.py
import asyncio
import json
import logging
from typing import Dict, Set, Optional, Any
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from dataclasses import dataclass

from .event_bus import EventBus
from .room_manager import RoomManager
from .message_router import MessageRouter
from ..integration import tcs_integration, cmc_integration
from ..models import websocket_models
from ..utils import error_utils

logger = logging.getLogger(__name__)

@dataclass
class Connection:
    """WebSocket connection representation."""
    websocket: WebSocket
    user_id: str
    room_id: Optional[str] = None
    connected_at: datetime = None
    last_activity: datetime = None
    metadata: Dict[str, Any] = None

class ConnectionManager:
    """WebSocket connection manager."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connections: Dict[str, Connection] = {}
        self.room_connections: Dict[str, Set[str]] = {}
        self.event_bus = EventBus(config)
        self.room_manager = RoomManager(config)
        self.message_router = MessageRouter(config)
        
        # Initialize AIM-OS integrations
        self.tcs_integration = tcs_integration.TCSIntegration(config)
        self.cmc_integration = cmc_integration.CMCIntegration(config)
        
        # Start background tasks
        asyncio.create_task(self._heartbeat_monitor())
        asyncio.create_task(self._cleanup_inactive_connections())
    
    async def connect(self, websocket: WebSocket, user_id: str) -> str:
        """Establish a new WebSocket connection."""
        try:
            await websocket.accept()
            
            # Create connection
            connection_id = f"conn_{user_id}_{datetime.utcnow().timestamp()}"
            connection = Connection(
                websocket=websocket,
                user_id=user_id,
                connected_at=datetime.utcnow(),
                last_activity=datetime.utcnow(),
                metadata={}
            )
            
            # Store connection
            self.connections[connection_id] = connection
            
            # Store user context in CMC
            await self.cmc_integration.store_user_context(user_id, {
                "connection_id": connection_id,
                "connected_at": connection.connected_at,
                "metadata": connection.metadata
            })
            
            # Send connection confirmation
            await self._send_message(connection_id, {
                "type": "connection_established",
                "connection_id": connection_id,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            logger.info(f"WebSocket connection established: {connection_id}")
            return connection_id
            
        except Exception as e:
            logger.error(f"Failed to establish WebSocket connection: {e}")
            await error_utils.handle_websocket_error(websocket, e)
            raise
    
    async def disconnect(self, connection_id: str):
        """Disconnect a WebSocket connection."""
        if connection_id in self.connections:
            connection = self.connections[connection_id]
            
            # Remove from room if in one
            if connection.room_id:
                await self.leave_room(connection_id, connection.room_id)
            
            # Close WebSocket
            try:
                await connection.websocket.close()
            except Exception as e:
                logger.warning(f"Error closing WebSocket: {e}")
            
            # Remove connection
            del self.connections[connection_id]
            
            # Update user context in CMC
            await self.cmc_integration.update_user_context(connection.user_id, {
                "disconnected_at": datetime.utcnow(),
                "connection_duration": (datetime.utcnow() - connection.connected_at).total_seconds()
            })
            
            logger.info(f"WebSocket connection closed: {connection_id}")
    
    async def join_room(self, connection_id: str, room_id: str) -> bool:
        """Join a room."""
        if connection_id not in self.connections:
            return False
        
        connection = self.connections[connection_id]
        
        # Leave current room if in one
        if connection.room_id:
            await self.leave_room(connection_id, connection.room_id)
        
        # Join new room
        await self.room_manager.join_room(room_id, connection_id)
        connection.room_id = room_id
        
        # Add to room connections
        if room_id not in self.room_connections:
            self.room_connections[room_id] = set()
        self.room_connections[room_id].add(connection_id)
        
        # Send room join confirmation
        await self._send_message(connection_id, {
            "type": "room_joined",
            "room_id": room_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Broadcast to room
        await self._broadcast_to_room(room_id, {
            "type": "user_joined",
            "user_id": connection.user_id,
            "timestamp": datetime.utcnow().isoformat()
        }, exclude_connection=connection_id)
        
        logger.info(f"Connection {connection_id} joined room {room_id}")
        return True
    
    async def leave_room(self, connection_id: str, room_id: str) -> bool:
        """Leave a room."""
        if connection_id not in self.connections:
            return False
        
        connection = self.connections[connection_id]
        
        if connection.room_id != room_id:
            return False
        
        # Leave room
        await self.room_manager.leave_room(room_id, connection_id)
        connection.room_id = None
        
        # Remove from room connections
        if room_id in self.room_connections:
            self.room_connections[room_id].discard(connection_id)
            if not self.room_connections[room_id]:
                del self.room_connections[room_id]
        
        # Send room leave confirmation
        await self._send_message(connection_id, {
            "type": "room_left",
            "room_id": room_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Broadcast to room
        await self._broadcast_to_room(room_id, {
            "type": "user_left",
            "user_id": connection.user_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        logger.info(f"Connection {connection_id} left room {room_id}")
        return True
    
    async def send_message(self, connection_id: str, message: Dict[str, Any]) -> bool:
        """Send a message to a specific connection."""
        if connection_id not in self.connections:
            return False
        
        connection = self.connections[connection_id]
        
        try:
            await connection.websocket.send_text(json.dumps(message))
            connection.last_activity = datetime.utcnow()
            return True
        except Exception as e:
            logger.error(f"Failed to send message to {connection_id}: {e}")
            await self.disconnect(connection_id)
            return False
    
    async def broadcast_to_room(self, room_id: str, message: Dict[str, Any], exclude_connection: Optional[str] = None) -> int:
        """Broadcast a message to all connections in a room."""
        if room_id not in self.room_connections:
            return 0
        
        sent_count = 0
        for connection_id in self.room_connections[room_id]:
            if connection_id != exclude_connection:
                if await self.send_message(connection_id, message):
                    sent_count += 1
        
        return sent_count
    
    async def handle_message(self, connection_id: str, message: str):
        """Handle incoming WebSocket message."""
        if connection_id not in self.connections:
            return
        
        try:
            data = json.loads(message)
            connection = self.connections[connection_id]
            
            # Update activity
            connection.last_activity = datetime.utcnow()
            
            # Route message
            await self.message_router.route_message(connection_id, data)
            
            # Store interaction in CMC
            await self.cmc_integration.store_interaction(connection.user_id, {
                "type": "websocket_message",
                "message": data,
                "timestamp": datetime.utcnow()
            })
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON message from {connection_id}: {e}")
            await self._send_message(connection_id, {
                "type": "error",
                "error": "Invalid JSON message",
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            logger.error(f"Error handling message from {connection_id}: {e}")
            await error_utils.handle_websocket_error(self.connections[connection_id].websocket, e)
    
    async def _heartbeat_monitor(self):
        """Monitor connection heartbeats."""
        while True:
            try:
                current_time = datetime.utcnow()
                inactive_connections = []
                
                for connection_id, connection in self.connections.items():
                    # Check if connection is inactive
                    if (current_time - connection.last_activity).total_seconds() > 300:  # 5 minutes
                        inactive_connections.append(connection_id)
                
                # Disconnect inactive connections
                for connection_id in inactive_connections:
                    await self.disconnect(connection_id)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in heartbeat monitor: {e}")
                await asyncio.sleep(60)
    
    async def _cleanup_inactive_connections(self):
        """Clean up inactive connections."""
        while True:
            try:
                current_time = datetime.utcnow()
                connections_to_remove = []
                
                for connection_id, connection in self.connections.items():
                    # Check if connection has been inactive for too long
                    if (current_time - connection.last_activity).total_seconds() > 3600:  # 1 hour
                        connections_to_remove.append(connection_id)
                
                # Remove inactive connections
                for connection_id in connections_to_remove:
                    await self.disconnect(connection_id)
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")
                await asyncio.sleep(300)
    
    async def _send_message(self, connection_id: str, message: Dict[str, Any]) -> bool:
        """Internal method to send a message."""
        return await self.send_message(connection_id, message)
    
    async def _broadcast_to_room(self, room_id: str, message: Dict[str, Any], exclude_connection: Optional[str] = None) -> int:
        """Internal method to broadcast to room."""
        return await self.broadcast_to_room(room_id, message, exclude_connection)
```

#### Visualization Engine Implementation

```python
# src/visualization/graph_renderer.py
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import asyncio

from ..integration import hhni_integration, seg_integration
from ..models import visualization_models
from ..utils import performance_utils

logger = logging.getLogger(__name__)

@dataclass
class GraphNode:
    """Graph node representation."""
    id: str
    label: str
    type: str
    properties: Dict[str, Any]
    position: Tuple[float, float]
    size: float
    color: str
    metadata: Dict[str, Any]

@dataclass
class GraphEdge:
    """Graph edge representation."""
    id: str
    source: str
    target: str
    type: str
    properties: Dict[str, Any]
    weight: float
    color: str
    metadata: Dict[str, Any]

@dataclass
class GraphLayout:
    """Graph layout configuration."""
    algorithm: str
    parameters: Dict[str, Any]
    dimensions: Tuple[int, int]
    spacing: float
    metadata: Dict[str, Any]

class GraphRenderer:
    """Graph visualization renderer."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Initialize AIM-OS integrations
        self.hhni_integration = hhni_integration.HHNIIntegration(config)
        self.seg_integration = seg_integration.SEGIntegration(config)
        
        # Layout algorithms
        self.layout_algorithms = {
            "force_directed": self._force_directed_layout,
            "hierarchical": self._hierarchical_layout,
            "circular": self._circular_layout,
            "grid": self._grid_layout
        }
    
    async def render_codebase_graph(self, codebase_id: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Render codebase as interactive graph."""
        try:
            # Get codebase data from HHNI
            codebase_data = await self.hhni_integration.get_codebase_graph(codebase_id)
            
            # Extract nodes and edges
            nodes = await self._extract_graph_nodes(codebase_data)
            edges = await self._extract_graph_edges(codebase_data)
            
            # Apply layout algorithm
            layout_algorithm = options.get("layout", "force_directed")
            layout_params = options.get("layout_params", {})
            
            if layout_algorithm in self.layout_algorithms:
                nodes = await self.layout_algorithms[layout_algorithm](nodes, edges, layout_params)
            
            # Apply visual styling
            nodes = await self._apply_node_styling(nodes, options)
            edges = await self._apply_edge_styling(edges, options)
            
            # Generate graph metadata
            metadata = await self._generate_graph_metadata(codebase_data, options)
            
            # Create graph representation
            graph = {
                "nodes": [self._serialize_node(node) for node in nodes],
                "edges": [self._serialize_edge(edge) for edge in edges],
                "metadata": metadata,
                "layout": {
                    "algorithm": layout_algorithm,
                    "parameters": layout_params
                },
                "rendered_at": datetime.utcnow().isoformat()
            }
            
            # Store graph in CMC for future reference
            await self._store_graph_in_cmc(codebase_id, graph)
            
            return graph
            
        except Exception as e:
            logger.error(f"Error rendering codebase graph: {e}")
            raise
    
    async def render_relationship_graph(self, source_id: str, relationship_type: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Render relationship graph for specific entity."""
        try:
            # Get relationship data from HHNI
            relationship_data = await self.hhni_integration.get_relationship_graph(source_id, relationship_type)
            
            # Extract nodes and edges
            nodes = await self._extract_relationship_nodes(relationship_data)
            edges = await self._extract_relationship_edges(relationship_data)
            
            # Apply layout
            layout_algorithm = options.get("layout", "force_directed")
            layout_params = options.get("layout_params", {})
            
            if layout_algorithm in self.layout_algorithms:
                nodes = await self.layout_algorithms[layout_algorithm](nodes, edges, layout_params)
            
            # Apply styling
            nodes = await self._apply_relationship_styling(nodes, options)
            edges = await self._apply_relationship_edge_styling(edges, options)
            
            # Generate metadata
            metadata = await self._generate_relationship_metadata(relationship_data, options)
            
            # Create graph representation
            graph = {
                "nodes": [self._serialize_node(node) for node in nodes],
                "edges": [self._serialize_edge(edge) for edge in edges],
                "metadata": metadata,
                "layout": {
                    "algorithm": layout_algorithm,
                    "parameters": layout_params
                },
                "rendered_at": datetime.utcnow().isoformat()
            }
            
            return graph
            
        except Exception as e:
            logger.error(f"Error rendering relationship graph: {e}")
            raise
    
    async def render_timeline_graph(self, timeline_id: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Render timeline as interactive graph."""
        try:
            # Get timeline data from TCS
            timeline_data = await self.tcs_integration.get_timeline_graph(timeline_id)
            
            # Extract timeline nodes and edges
            nodes = await self._extract_timeline_nodes(timeline_data)
            edges = await self._extract_timeline_edges(timeline_data)
            
            # Apply timeline-specific layout
            nodes = await self._timeline_layout(nodes, edges, options)
            
            # Apply timeline styling
            nodes = await self._apply_timeline_styling(nodes, options)
            edges = await self._apply_timeline_edge_styling(edges, options)
            
            # Generate timeline metadata
            metadata = await self._generate_timeline_metadata(timeline_data, options)
            
            # Create timeline graph representation
            graph = {
                "nodes": [self._serialize_node(node) for node in nodes],
                "edges": [self._serialize_edge(edge) for edge in edges],
                "metadata": metadata,
                "layout": {
                    "algorithm": "timeline",
                    "parameters": options.get("layout_params", {})
                },
                "rendered_at": datetime.utcnow().isoformat()
            }
            
            return graph
            
        except Exception as e:
            logger.error(f"Error rendering timeline graph: {e}")
            raise
    
    async def _extract_graph_nodes(self, codebase_data: Dict[str, Any]) -> List[GraphNode]:
        """Extract graph nodes from codebase data."""
        nodes = []
        
        for node_data in codebase_data.get("nodes", []):
            node = GraphNode(
                id=node_data["id"],
                label=node_data.get("label", node_data["id"]),
                type=node_data.get("type", "unknown"),
                properties=node_data.get("properties", {}),
                position=(0, 0),  # Will be set by layout algorithm
                size=node_data.get("size", 1.0),
                color=node_data.get("color", "#888888"),
                metadata=node_data.get("metadata", {})
            )
            nodes.append(node)
        
        return nodes
    
    async def _extract_graph_edges(self, codebase_data: Dict[str, Any]) -> List[GraphEdge]:
        """Extract graph edges from codebase data."""
        edges = []
        
        for edge_data in codebase_data.get("edges", []):
            edge = GraphEdge(
                id=edge_data["id"],
                source=edge_data["source"],
                target=edge_data["target"],
                type=edge_data.get("type", "unknown"),
                properties=edge_data.get("properties", {}),
                weight=edge_data.get("weight", 1.0),
                color=edge_data.get("color", "#888888"),
                metadata=edge_data.get("metadata", {})
            )
            edges.append(edge)
        
        return edges
    
    async def _force_directed_layout(self, nodes: List[GraphNode], edges: List[GraphEdge], params: Dict[str, Any]) -> List[GraphNode]:
        """Apply force-directed layout algorithm."""
        # Implementation of force-directed layout
        # This is a simplified version - in practice, you'd use a proper physics simulation
        
        # Initialize positions randomly
        import random
        for node in nodes:
            node.position = (
                random.uniform(-100, 100),
                random.uniform(-100, 100)
            )
        
        # Apply force-directed algorithm
        iterations = params.get("iterations", 100)
        for _ in range(iterations):
            # Calculate forces
            forces = {}
            for node in nodes:
                forces[node.id] = [0, 0]
            
            # Repulsive forces between all nodes
            for i, node1 in enumerate(nodes):
                for j, node2 in enumerate(nodes):
                    if i != j:
                        dx = node1.position[0] - node2.position[0]
                        dy = node1.position[1] - node2.position[1]
                        distance = (dx * dx + dy * dy) ** 0.5
                        
                        if distance > 0:
                            force = params.get("repulsion", 1000) / (distance * distance)
                            forces[node1.id][0] += force * dx / distance
                            forces[node1.id][1] += force * dy / distance
            
            # Attractive forces for connected nodes
            for edge in edges:
                source_node = next((n for n in nodes if n.id == edge.source), None)
                target_node = next((n for n in nodes if n.id == edge.target), None)
                
                if source_node and target_node:
                    dx = target_node.position[0] - source_node.position[0]
                    dy = target_node.position[1] - source_node.position[1]
                    distance = (dx * dx + dy * dy) ** 0.5
                    
                    if distance > 0:
                        force = params.get("attraction", 0.1) * distance
                        forces[source_node.id][0] += force * dx / distance
                        forces[source_node.id][1] += force * dy / distance
                        forces[target_node.id][0] -= force * dx / distance
                        forces[target_node.id][1] -= force * dy / distance
            
            # Update positions
            damping = params.get("damping", 0.9)
            for node in nodes:
                node.position = (
                    node.position[0] + forces[node.id][0] * damping,
                    node.position[1] + forces[node.id][1] * damping
                )
        
        return nodes
    
    async def _hierarchical_layout(self, nodes: List[GraphNode], edges: List[GraphEdge], params: Dict[str, Any]) -> List[GraphNode]:
        """Apply hierarchical layout algorithm."""
        # Implementation of hierarchical layout
        # This is a simplified version - in practice, you'd use a proper hierarchical algorithm
        
        # Group nodes by type or level
        node_groups = {}
        for node in nodes:
            node_type = node.type
            if node_type not in node_groups:
                node_groups[node_type] = []
            node_groups[node_type].append(node)
        
        # Position nodes in hierarchical levels
        level_height = params.get("level_height", 100)
        level_spacing = params.get("level_spacing", 200)
        
        for level, group_nodes in enumerate(node_groups.values()):
            y = level * level_spacing
            x_spacing = level_spacing / max(len(group_nodes), 1)
            
            for i, node in enumerate(group_nodes):
                node.position = (
                    (i - len(group_nodes) / 2) * x_spacing,
                    y
                )
        
        return nodes
    
    async def _circular_layout(self, nodes: List[GraphNode], edges: List[GraphEdge], params: Dict[str, Any]) -> List[GraphNode]:
        """Apply circular layout algorithm."""
        radius = params.get("radius", 100)
        center_x = params.get("center_x", 0)
        center_y = params.get("center_y", 0)
        
        angle_step = 2 * 3.14159 / len(nodes)
        
        for i, node in enumerate(nodes):
            angle = i * angle_step
            node.position = (
                center_x + radius * math.cos(angle),
                center_y + radius * math.sin(angle)
            )
        
        return nodes
    
    async def _grid_layout(self, nodes: List[GraphNode], edges: List[GraphEdge], params: Dict[str, Any]) -> List[GraphNode]:
        """Apply grid layout algorithm."""
        cols = params.get("cols", int(math.ceil(math.sqrt(len(nodes)))))
        spacing = params.get("spacing", 100)
        
        for i, node in enumerate(nodes):
            row = i // cols
            col = i % cols
            node.position = (
                col * spacing,
                row * spacing
            )
        
        return nodes
    
    async def _apply_node_styling(self, nodes: List[GraphNode], options: Dict[str, Any]) -> List[GraphNode]:
        """Apply visual styling to nodes."""
        styling = options.get("node_styling", {})
        
        for node in nodes:
            # Apply size
            if "size" in styling:
                node.size = styling["size"]
            
            # Apply color
            if "color" in styling:
                node.color = styling["color"]
            
            # Apply type-specific styling
            type_styling = styling.get("types", {}).get(node.type, {})
            if "size" in type_styling:
                node.size = type_styling["size"]
            if "color" in type_styling:
                node.color = type_styling["color"]
        
        return nodes
    
    async def _apply_edge_styling(self, edges: List[GraphEdge], options: Dict[str, Any]) -> List[GraphEdge]:
        """Apply visual styling to edges."""
        styling = options.get("edge_styling", {})
        
        for edge in edges:
            # Apply weight
            if "weight" in styling:
                edge.weight = styling["weight"]
            
            # Apply color
            if "color" in styling:
                edge.color = styling["color"]
            
            # Apply type-specific styling
            type_styling = styling.get("types", {}).get(edge.type, {})
            if "weight" in type_styling:
                edge.weight = type_styling["weight"]
            if "color" in type_styling:
                edge.color = type_styling["color"]
        
        return edges
    
    def _serialize_node(self, node: GraphNode) -> Dict[str, Any]:
        """Serialize graph node for JSON response."""
        return {
            "id": node.id,
            "label": node.label,
            "type": node.type,
            "properties": node.properties,
            "position": {
                "x": node.position[0],
                "y": node.position[1]
            },
            "size": node.size,
            "color": node.color,
            "metadata": node.metadata
        }
    
    def _serialize_edge(self, edge: GraphEdge) -> Dict[str, Any]:
        """Serialize graph edge for JSON response."""
        return {
            "id": edge.id,
            "source": edge.source,
            "target": edge.target,
            "type": edge.type,
            "properties": edge.properties,
            "weight": edge.weight,
            "color": edge.color,
            "metadata": edge.metadata
        }
    
    async def _store_graph_in_cmc(self, codebase_id: str, graph: Dict[str, Any]) -> None:
        """Store graph in CMC for future reference."""
        # Store graph data in CMC
        await self.cmc_integration.store_graph_data(codebase_id, graph)
```

### AIM-OS Integration Implementation

#### CMC Integration

```python
# src/integration/cmc_integration.py
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass

from ...cmc_service.models import CMCAtom, StorageDataMetadata, RoutingMetadata, ConsistencyMetadata
from ...cmc_service.client import CMCClient

logger = logging.getLogger(__name__)

@dataclass
class UserContext:
    """User context model."""
    user_id: str
    session_id: str
    context_data: Dict[str, Any]
    timestamp: datetime
    metadata: Dict[str, Any]

class CMCIntegration:
    """CMC integration for Presentation & API Layer."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.cmc_client = CMCClient(config.get("cmc_url", "http://localhost:8000"))
    
    async def store_user_context(self, user_id: str, context_data: Dict[str, Any]) -> CMCAtom:
        """Store user context in CMC."""
        try:
            # Create context atom
            context_atom = CMCAtom(
                modality="user_context",
                content=str(context_data),
                embedding=await self._generate_embedding(str(context_data)),
                tags=["user_context", user_id],
                hhni_path=f"user_context/{user_id}",
                tpv=datetime.utcnow(),
                vif=0.9,
                metadata=UserContextMetadata(
                    user_id=user_id,
                    session_id=context_data.get("session_id", ""),
                    context_data=context_data,
                    timestamp=datetime.utcnow()
                )
            )
            
            # Store in CMC
            await self.cmc_client.store_atom_with_bitemporal(context_atom)
            
            logger.info(f"Stored user context for user {user_id}")
            return context_atom
            
        except Exception as e:
            logger.error(f"Error storing user context: {e}")
            raise
    
    async def retrieve_user_context(self, user_id: str, context_type: str = None) -> List[Dict[str, Any]]:
        """Retrieve user context from CMC."""
        try:
            # Build query
            query = {
                "modality": "user_context",
                "tags": ["user_context", user_id]
            }
            
            if context_type:
                query["context_type"] = context_type
            
            # Query CMC
            results = await self.cmc_client.query_atoms(query)
            
            # Convert to context format
            contexts = []
            for result in results:
                context = {
                    "user_id": result.metadata.get("user_id"),
                    "session_id": result.metadata.get("session_id"),
                    "context_data": result.metadata.get("context_data", {}),
                    "timestamp": result.tpv,
                    "metadata": result.metadata
                }
                contexts.append(context)
            
            return contexts
            
        except Exception as e:
            logger.error(f"Error retrieving user context: {e}")
            raise
    
    async def store_api_interaction(self, user_id: str, request: Dict[str, Any], response: Dict[str, Any]) -> CMCAtom:
        """Store API interaction in CMC."""
        try:
            # Create interaction atom
            interaction_atom = CMCAtom(
                modality="api_interaction",
                content=f"Request: {request}\nResponse: {response}",
                embedding=await self._generate_embedding(f"Request: {request}\nResponse: {response}"),
                tags=["api_interaction", user_id],
                hhni_path=f"api_interaction/{user_id}",
                tpv=datetime.utcnow(),
                vif=0.8,
                metadata=APIInteractionMetadata(
                    user_id=user_id,
                    request=request,
                    response=response,
                    timestamp=datetime.utcnow()
                )
            )
            
            # Store in CMC
            await self.cmc_client.store_atom_with_bitemporal(interaction_atom)
            
            logger.info(f"Stored API interaction for user {user_id}")
            return interaction_atom
            
        except Exception as e:
            logger.error(f"Error storing API interaction: {e}")
            raise
    
    async def store_websocket_interaction(self, user_id: str, message: Dict[str, Any]) -> CMCAtom:
        """Store WebSocket interaction in CMC."""
        try:
            # Create WebSocket interaction atom
            ws_atom = CMCAtom(
                modality="websocket_interaction",
                content=str(message),
                embedding=await self._generate_embedding(str(message)),
                tags=["websocket_interaction", user_id],
                hhni_path=f"websocket_interaction/{user_id}",
                tpv=datetime.utcnow(),
                vif=0.8,
                metadata=WebSocketInteractionMetadata(
                    user_id=user_id,
                    message=message,
                    timestamp=datetime.utcnow()
                )
            )
            
            # Store in CMC
            await self.cmc_client.store_atom_with_bitemporal(ws_atom)
            
            logger.info(f"Stored WebSocket interaction for user {user_id}")
            return ws_atom
            
        except Exception as e:
            logger.error(f"Error storing WebSocket interaction: {e}")
            raise
    
    async def store_graph_data(self, codebase_id: str, graph: Dict[str, Any]) -> CMCAtom:
        """Store graph data in CMC."""
        try:
            # Create graph atom
            graph_atom = CMCAtom(
                modality="graph_data",
                content=str(graph),
                embedding=await self._generate_embedding(str(graph)),
                tags=["graph_data", codebase_id],
                hhni_path=f"graph_data/{codebase_id}",
                tpv=datetime.utcnow(),
                vif=0.9,
                metadata=GraphDataMetadata(
                    codebase_id=codebase_id,
                    graph=graph,
                    timestamp=datetime.utcnow()
                )
            )
            
            # Store in CMC
            await self.cmc_client.store_atom_with_bitemporal(graph_atom)
            
            logger.info(f"Stored graph data for codebase {codebase_id}")
            return graph_atom
            
        except Exception as e:
            logger.error(f"Error storing graph data: {e}")
            raise
    
    async def _generate_embedding(self, content: str) -> List[float]:
        """Generate embedding for content."""
        # This would use the actual embedding service
        # For now, return a dummy embedding
        return [0.0] * 768
```

#### HHNI Integration

```python
# src/integration/hhni_integration.py
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from ...hhni.client import HHNIClient

logger = logging.getLogger(__name__)

class HHNIIntegration:
    """HHNI integration for Presentation & API Layer."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.hhni_client = HHNIClient(config.get("hhni_url", "http://localhost:8000"))
    
    async def get_codebase_graph(self, codebase_id: str) -> Dict[str, Any]:
        """Get codebase graph from HHNI."""
        try:
            # Query HHNI for codebase graph
            query = {
                "codebase_id": codebase_id,
                "graph_type": "full"
            }
            
            result = await self.hhni_client.query_graph(query)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting codebase graph: {e}")
            raise
    
    async def get_relationship_graph(self, source_id: str, relationship_type: str) -> Dict[str, Any]:
        """Get relationship graph from HHNI."""
        try:
            # Query HHNI for relationship graph
            query = {
                "source_id": source_id,
                "relationship_type": relationship_type,
                "graph_type": "relationship"
            }
            
            result = await self.hhni_client.query_graph(query)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting relationship graph: {e}")
            raise
    
    async def semantic_search(self, query: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Perform semantic search using HHNI."""
        try:
            # Use HHNI for semantic search
            search_results = await self.hhni_client.semantic_search(query, context)
            
            return search_results
            
        except Exception as e:
            logger.error(f"Error performing semantic search: {e}")
            raise
    
    async def get_navigation_suggestions(self, user_id: str, current_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get navigation suggestions from HHNI."""
        try:
            # Query HHNI for navigation suggestions
            query = {
                "user_id": user_id,
                "current_context": current_context,
                "suggestion_type": "navigation"
            }
            
            suggestions = await self.hhni_client.get_suggestions(query)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting navigation suggestions: {e}")
            raise
```

### Error Handling and Validation

#### Error Handler Implementation

```python
# src/utils/error_utils.py
import logging
from typing import Dict, Any, Optional
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from datetime import datetime

logger = logging.getLogger(__name__)

class ErrorHandler:
    """Error handler for Presentation & API Layer."""
    
    @staticmethod
    async def handle_http_exception(request: Request, exc: HTTPException) -> JSONResponse:
        """Handle HTTP exceptions."""
        error_response = {
            "error": {
                "type": "http_exception",
                "status_code": exc.status_code,
                "message": exc.detail,
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": getattr(request.state, "request_id", None)
            }
        }
        
        logger.error(f"HTTP exception: {exc.status_code} - {exc.detail}")
        
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response
        )
    
    @staticmethod
    async def handle_general_exception(request: Request, exc: Exception) -> JSONResponse:
        """Handle general exceptions."""
        error_response = {
            "error": {
                "type": "internal_error",
                "status_code": 500,
                "message": "Internal server error",
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": getattr(request.state, "request_id", None)
            }
        }
        
        logger.error(f"General exception: {exc}", exc_info=True)
        
        return JSONResponse(
            status_code=500,
            content=error_response
        )
    
    @staticmethod
    async def handle_websocket_error(websocket, exc: Exception) -> None:
        """Handle WebSocket errors."""
        try:
            error_message = {
                "type": "error",
                "error": {
                    "type": "websocket_error",
                    "message": str(exc),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
            await websocket.send_text(json.dumps(error_message))
            
        except Exception as e:
            logger.error(f"Error sending WebSocket error message: {e}")
    
    @staticmethod
    async def handle_validation_error(field: str, message: str) -> JSONResponse:
        """Handle validation errors."""
        error_response = {
            "error": {
                "type": "validation_error",
                "status_code": 400,
                "message": f"Validation error in field '{field}': {message}",
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        logger.warning(f"Validation error: {field} - {message}")
        
        return JSONResponse(
            status_code=400,
            content=error_response
        )
```

#### Validation Utilities

```python
# src/utils/validation_utils.py
import re
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ValidationUtils:
    """Validation utilities for Presentation & API Layer."""
    
    @staticmethod
    def validate_user_id(user_id: str) -> bool:
        """Validate user ID format."""
        if not user_id or not isinstance(user_id, str):
            return False
        
        # User ID should be alphanumeric with underscores and hyphens
        pattern = r'^[a-zA-Z0-9_-]+$'
        return bool(re.match(pattern, user_id))
    
    @staticmethod
    def validate_codebase_id(codebase_id: str) -> bool:
        """Validate codebase ID format."""
        if not codebase_id or not isinstance(codebase_id, str):
            return False
        
        # Codebase ID should be alphanumeric with underscores and hyphens
        pattern = r'^[a-zA-Z0-9_-]+$'
        return bool(re.match(pattern, codebase_id))
    
    @staticmethod
    def validate_timestamp(timestamp: Union[str, datetime]) -> bool:
        """Validate timestamp format."""
        if isinstance(timestamp, datetime):
            return True
        
        if isinstance(timestamp, str):
            try:
                datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                return True
            except ValueError:
                return False
        
        return False
    
    @staticmethod
    def validate_pagination_params(page: int, page_size: int) -> bool:
        """Validate pagination parameters."""
        if not isinstance(page, int) or page < 1:
            return False
        
        if not isinstance(page_size, int) or page_size < 1 or page_size > 100:
            return False
        
        return True
    
    @staticmethod
    def validate_graph_options(options: Dict[str, Any]) -> List[str]:
        """Validate graph visualization options."""
        errors = []
        
        # Validate layout algorithm
        valid_layouts = ["force_directed", "hierarchical", "circular", "grid", "timeline"]
        layout = options.get("layout")
        if layout and layout not in valid_layouts:
            errors.append(f"Invalid layout algorithm: {layout}")
        
        # Validate layout parameters
        layout_params = options.get("layout_params", {})
        if not isinstance(layout_params, dict):
            errors.append("Layout parameters must be a dictionary")
        
        # Validate node styling
        node_styling = options.get("node_styling", {})
        if not isinstance(node_styling, dict):
            errors.append("Node styling must be a dictionary")
        
        # Validate edge styling
        edge_styling = options.get("edge_styling", {})
        if not isinstance(edge_styling, dict):
            errors.append("Edge styling must be a dictionary")
        
        return errors
    
    @staticmethod
    def validate_websocket_message(message: Dict[str, Any]) -> List[str]:
        """Validate WebSocket message format."""
        errors = []
        
        # Check required fields
        if "type" not in message:
            errors.append("Message must have 'type' field")
        
        # Validate message type
        valid_types = ["join_room", "leave_room", "send_message", "heartbeat", "subscribe", "unsubscribe"]
        message_type = message.get("type")
        if message_type and message_type not in valid_types:
            errors.append(f"Invalid message type: {message_type}")
        
        # Validate room ID if present
        room_id = message.get("room_id")
        if room_id and not ValidationUtils.validate_codebase_id(room_id):
            errors.append("Invalid room ID format")
        
        return errors
```

### Performance Optimization

#### Caching Service

```python
# src/services/cache_service.py
import asyncio
import json
import logging
from typing import Dict, Any, Optional, Union
from datetime import datetime, timedelta
import hashlib

logger = logging.getLogger(__name__)

class CacheService:
    """Caching service for Presentation & API Layer."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl: Dict[str, datetime] = {}
        self.cleanup_interval = config.get("cache_cleanup_interval", 300)  # 5 minutes
        
        # Start cleanup task
        asyncio.create_task(self._cleanup_expired_cache())
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key in self.cache:
            # Check if expired
            if key in self.cache_ttl and datetime.utcnow() > self.cache_ttl[key]:
                await self.delete(key)
                return None
            
            return self.cache[key]["value"]
        
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        ttl = ttl or self.config.get("default_cache_ttl", 3600)  # 1 hour
        
        self.cache[key] = {
            "value": value,
            "created_at": datetime.utcnow()
        }
        
        if ttl > 0:
            self.cache_ttl[key] = datetime.utcnow() + timedelta(seconds=ttl)
    
    async def delete(self, key: str) -> None:
        """Delete value from cache."""
        if key in self.cache:
            del self.cache[key]
        
        if key in self.cache_ttl:
            del self.cache_ttl[key]
    
    async def clear(self) -> None:
        """Clear all cache."""
        self.cache.clear()
        self.cache_ttl.clear()
    
    async def get_or_set(self, key: str, factory_func, ttl: Optional[int] = None) -> Any:
        """Get value from cache or set it using factory function."""
        value = await self.get(key)
        
        if value is None:
            value = await factory_func()
            await self.set(key, value, ttl)
        
        return value
    
    def generate_cache_key(self, prefix: str, **kwargs) -> str:
        """Generate cache key from prefix and parameters."""
        # Sort kwargs for consistent key generation
        sorted_kwargs = sorted(kwargs.items())
        
        # Create key string
        key_string = f"{prefix}:{':'.join(f'{k}={v}' for k, v in sorted_kwargs)}"
        
        # Hash for shorter keys
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def _cleanup_expired_cache(self) -> None:
        """Clean up expired cache entries."""
        while True:
            try:
                current_time = datetime.utcnow()
                expired_keys = []
                
                for key, expiry_time in self.cache_ttl.items():
                    if current_time > expiry_time:
                        expired_keys.append(key)
                
                for key in expired_keys:
                    await self.delete(key)
                
                logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
                
                await asyncio.sleep(self.cleanup_interval)
                
            except Exception as e:
                logger.error(f"Error in cache cleanup: {e}")
                await asyncio.sleep(self.cleanup_interval)
```

#### Performance Monitoring

```python
# src/utils/performance_utils.py
import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics model."""
    request_id: str
    endpoint: str
    method: str
    response_time: float
    status_code: int
    timestamp: datetime
    metadata: Dict[str, Any]

class PerformanceMonitor:
    """Performance monitor for Presentation & API Layer."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.metrics: List[PerformanceMetrics] = []
        self.max_metrics = config.get("max_metrics", 10000)
    
    async def log_performance_metrics(self, request, response, response_time: float) -> None:
        """Log performance metrics."""
        try:
            # Extract request information
            request_id = getattr(request.state, "request_id", None)
            endpoint = request.url.path
            method = request.method
            status_code = response.status_code
            
            # Create performance metrics
            metrics = PerformanceMetrics(
                request_id=request_id or "unknown",
                endpoint=endpoint,
                method=method,
                response_time=response_time,
                status_code=status_code,
                timestamp=datetime.utcnow(),
                metadata={
                    "user_agent": request.headers.get("user-agent", ""),
                    "content_length": response.headers.get("content-length", 0),
                    "content_type": response.headers.get("content-type", "")
                }
            )
            
            # Store metrics
            self.metrics.append(metrics)
            
            # Trim metrics if too many
            if len(self.metrics) > self.max_metrics:
                self.metrics = self.metrics[-self.max_metrics:]
            
            # Log slow requests
            if response_time > self.config.get("slow_request_threshold", 1.0):
                logger.warning(f"Slow request: {endpoint} took {response_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Error logging performance metrics: {e}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        if not self.metrics:
            return {}
        
        # Calculate statistics
        response_times = [m.response_time for m in self.metrics]
        
        summary = {
            "total_requests": len(self.metrics),
            "average_response_time": sum(response_times) / len(response_times),
            "min_response_time": min(response_times),
            "max_response_time": max(response_times),
            "slow_requests": len([m for m in self.metrics if m.response_time > 1.0]),
            "error_rate": len([m for m in self.metrics if m.status_code >= 400]) / len(self.metrics),
            "endpoints": self._get_endpoint_stats()
        }
        
        return summary
    
    def _get_endpoint_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get endpoint statistics."""
        endpoint_stats = {}
        
        for metric in self.metrics:
            endpoint = metric.endpoint
            
            if endpoint not in endpoint_stats:
                endpoint_stats[endpoint] = {
                    "count": 0,
                    "total_time": 0.0,
                    "min_time": float('inf'),
                    "max_time": 0.0,
                    "errors": 0
                }
            
            stats = endpoint_stats[endpoint]
            stats["count"] += 1
            stats["total_time"] += metric.response_time
            stats["min_time"] = min(stats["min_time"], metric.response_time)
            stats["max_time"] = max(stats["max_time"], metric.response_time)
            
            if metric.status_code >= 400:
                stats["errors"] += 1
        
        # Calculate averages
        for stats in endpoint_stats.values():
            if stats["count"] > 0:
                stats["average_time"] = stats["total_time"] / stats["count"]
                stats["error_rate"] = stats["errors"] / stats["count"]
        
        return endpoint_stats
```

This L3 detailed implementation guide provides comprehensive implementation details for the Presentation & API Layer, including core components, AIM-OS integration patterns, error handling, validation, and performance optimization strategies.
