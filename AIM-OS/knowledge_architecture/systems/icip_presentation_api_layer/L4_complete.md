# ICIP Presentation & API Layer - L4 Complete Documentation

**Detail Level:** 4 of 5 (15,000+ words)  
**Context Budget:** ~240k tokens  
**Purpose:** Complete reference documentation for Presentation & API Layer with AIM-OS integration

---

## Complete Reference Documentation

### System Overview

The ICIP Presentation & API Layer is a comprehensive interface system that serves as the primary gateway between the Integrated Codebase Intelligence Platform and external consumers. It provides unified access to all ICIP capabilities through multiple protocol interfaces, real-time WebSocket communication, interactive visualization components, and intelligent user interfaces that leverage the full power of the AIM-OS consciousness infrastructure.

### Architecture Deep Dive

#### Core Components

1. **API Gateway** (`api/gateway/`)
   - REST API server for HTTP-based interactions
   - GraphQL server for flexible query interface
   - gRPC server for high-performance binary protocol
   - Authentication and authorization middleware
   - Rate limiting and request routing

2. **WebSocket Hub** (`websocket/`)
   - Connection management and lifecycle
   - Real-time event distribution
   - Room-based collaboration
   - Message routing and authentication
   - Heartbeat monitoring and recovery

3. **Visualization Engine** (`visualization/`)
   - Interactive graph rendering
   - Chart and analytics visualization
   - Timeline and temporal data display
   - Dashboard building and customization
   - Export and sharing capabilities

4. **User Interface** (`ui/`)
   - React-based component library
   - Dashboard and analytics views
   - Code exploration interface
   - Collaboration tools and features
   - Settings and configuration panels

#### Data Models

```python
@dataclass
class APIRequest:
    """API request model."""
    request_id: str
    user_id: str
    endpoint: str
    method: str
    headers: Dict[str, str]
    query_params: Dict[str, Any]
    body: Optional[Dict[str, Any]]
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class APIResponse:
    """API response model."""
    request_id: str
    status_code: int
    headers: Dict[str, str]
    body: Dict[str, Any]
    response_time: float
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class WebSocketMessage:
    """WebSocket message model."""
    message_id: str
    connection_id: str
    user_id: str
    message_type: str
    content: Dict[str, Any]
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class VisualizationData:
    """Visualization data model."""
    visualization_id: str
    visualization_type: str
    data: Dict[str, Any]
    options: Dict[str, Any]
    metadata: Dict[str, Any]
    timestamp: datetime

@dataclass
class UserSession:
    """User session model."""
    session_id: str
    user_id: str
    connection_id: str
    room_id: Optional[str]
    created_at: datetime
    last_activity: datetime
    metadata: Dict[str, Any]
```

#### API Endpoints

```python
# REST API Endpoints
class CodebaseEndpoints:
    """Codebase-related API endpoints."""
    
    @app.get("/codebase/{codebase_id}")
    async def get_codebase(codebase_id: str, user: User = Depends(get_current_user)):
        """Get codebase information."""
        pass
    
    @app.get("/codebase/{codebase_id}/graph")
    async def get_codebase_graph(codebase_id: str, options: GraphOptions = Depends()):
        """Get codebase graph visualization."""
        pass
    
    @app.get("/codebase/{codebase_id}/search")
    async def search_codebase(codebase_id: str, query: str, filters: SearchFilters = Depends()):
        """Search codebase content."""
        pass

class AnalyticsEndpoints:
    """Analytics-related API endpoints."""
    
    @app.get("/analytics/metrics")
    async def get_metrics(codebase_id: str, time_range: TimeRange = Depends()):
        """Get codebase metrics."""
        pass
    
    @app.get("/analytics/trends")
    async def get_trends(codebase_id: str, metric: str, time_range: TimeRange = Depends()):
        """Get metric trends."""
        pass
    
    @app.get("/analytics/insights")
    async def get_insights(codebase_id: str, context: Dict[str, Any] = Depends()):
        """Get intelligent insights."""
        pass

class CollaborationEndpoints:
    """Collaboration-related API endpoints."""
    
    @app.post("/collaboration/room")
    async def create_room(room_data: RoomData, user: User = Depends(get_current_user)):
        """Create collaboration room."""
        pass
    
    @app.get("/collaboration/room/{room_id}")
    async def get_room(room_id: str, user: User = Depends(get_current_user)):
        """Get room information."""
        pass
    
    @app.post("/collaboration/room/{room_id}/join")
    async def join_room(room_id: str, user: User = Depends(get_current_user)):
        """Join collaboration room."""
        pass

class InsightsEndpoints:
    """Insights-related API endpoints."""
    
    @app.get("/insights/recommendations")
    async def get_recommendations(user_id: str, context: Dict[str, Any] = Depends()):
        """Get personalized recommendations."""
        pass
    
    @app.get("/insights/patterns")
    async def get_patterns(codebase_id: str, pattern_type: str = Depends()):
        """Get code patterns."""
        pass
    
    @app.get("/insights/predictions")
    async def get_predictions(codebase_id: str, prediction_type: str = Depends()):
        """Get predictive insights."""
        pass
```

#### WebSocket Protocol

```python
# WebSocket Message Types
class WebSocketMessageTypes:
    """WebSocket message type definitions."""
    
    # Connection management
    CONNECTION_ESTABLISHED = "connection_established"
    CONNECTION_CLOSED = "connection_closed"
    HEARTBEAT = "heartbeat"
    
    # Room management
    JOIN_ROOM = "join_room"
    LEAVE_ROOM = "leave_room"
    ROOM_JOINED = "room_joined"
    ROOM_LEFT = "room_left"
    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"
    
    # Collaboration
    SEND_MESSAGE = "send_message"
    MESSAGE_RECEIVED = "message_received"
    CURSOR_UPDATE = "cursor_update"
    SELECTION_UPDATE = "selection_update"
    
    # Real-time updates
    CODEBASE_UPDATED = "codebase_updated"
    METRICS_UPDATED = "metrics_updated"
    INSIGHTS_UPDATED = "insights_updated"
    
    # Error handling
    ERROR = "error"
    VALIDATION_ERROR = "validation_error"

# WebSocket Message Handlers
class WebSocketMessageHandler:
    """WebSocket message handler."""
    
    async def handle_join_room(self, connection_id: str, message: Dict[str, Any]) -> None:
        """Handle join room message."""
        room_id = message.get("room_id")
        if not room_id:
            await self._send_error(connection_id, "Room ID required")
            return
        
        success = await self.connection_manager.join_room(connection_id, room_id)
        if not success:
            await self._send_error(connection_id, "Failed to join room")
    
    async def handle_leave_room(self, connection_id: str, message: Dict[str, Any]) -> None:
        """Handle leave room message."""
        room_id = message.get("room_id")
        if not room_id:
            await self._send_error(connection_id, "Room ID required")
            return
        
        success = await self.connection_manager.leave_room(connection_id, room_id)
        if not success:
            await self._send_error(connection_id, "Failed to leave room")
    
    async def handle_send_message(self, connection_id: str, message: Dict[str, Any]) -> None:
        """Handle send message."""
        content = message.get("content")
        room_id = message.get("room_id")
        
        if not content or not room_id:
            await self._send_error(connection_id, "Content and room ID required")
            return
        
        # Broadcast message to room
        await self.connection_manager.broadcast_to_room(room_id, {
            "type": "message_received",
            "content": content,
            "sender": connection_id,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def handle_cursor_update(self, connection_id: str, message: Dict[str, Any]) -> None:
        """Handle cursor update."""
        cursor_data = message.get("cursor_data")
        room_id = message.get("room_id")
        
        if not cursor_data or not room_id:
            await self._send_error(connection_id, "Cursor data and room ID required")
            return
        
        # Broadcast cursor update to room
        await self.connection_manager.broadcast_to_room(room_id, {
            "type": "cursor_update",
            "cursor_data": cursor_data,
            "sender": connection_id,
            "timestamp": datetime.utcnow().isoformat()
        }, exclude_connection=connection_id)
```

#### Visualization Components

```python
# Graph Visualization Components
class GraphVisualization:
    """Graph visualization component."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.renderer = GraphRenderer(config)
        self.layout_engine = LayoutEngine(config)
        self.styling_engine = StylingEngine(config)
    
    async def render_codebase_graph(self, codebase_id: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Render codebase as interactive graph."""
        # Get codebase data
        codebase_data = await self._get_codebase_data(codebase_id)
        
        # Extract graph structure
        nodes, edges = await self._extract_graph_structure(codebase_data)
        
        # Apply layout algorithm
        layout_algorithm = options.get("layout", "force_directed")
        nodes = await self.layout_engine.apply_layout(nodes, edges, layout_algorithm, options)
        
        # Apply visual styling
        nodes = await self.styling_engine.apply_node_styling(nodes, options)
        edges = await self.styling_engine.apply_edge_styling(edges, options)
        
        # Generate interactive features
        interactive_features = await self._generate_interactive_features(nodes, edges, options)
        
        # Create graph representation
        graph = {
            "nodes": [self._serialize_node(node) for node in nodes],
            "edges": [self._serialize_edge(edge) for edge in edges],
            "interactive_features": interactive_features,
            "metadata": await self._generate_graph_metadata(codebase_data, options),
            "rendered_at": datetime.utcnow().isoformat()
        }
        
        return graph
    
    async def render_relationship_graph(self, source_id: str, relationship_type: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Render relationship graph."""
        # Get relationship data
        relationship_data = await self._get_relationship_data(source_id, relationship_type)
        
        # Extract relationship structure
        nodes, edges = await self._extract_relationship_structure(relationship_data)
        
        # Apply layout
        layout_algorithm = options.get("layout", "hierarchical")
        nodes = await self.layout_engine.apply_layout(nodes, edges, layout_algorithm, options)
        
        # Apply styling
        nodes = await self.styling_engine.apply_relationship_styling(nodes, options)
        edges = await self.styling_engine.apply_relationship_edge_styling(edges, options)
        
        # Generate interactive features
        interactive_features = await self._generate_relationship_interactive_features(nodes, edges, options)
        
        # Create relationship graph
        graph = {
            "nodes": [self._serialize_node(node) for node in nodes],
            "edges": [self._serialize_edge(edge) for edge in edges],
            "interactive_features": interactive_features,
            "metadata": await self._generate_relationship_metadata(relationship_data, options),
            "rendered_at": datetime.utcnow().isoformat()
        }
        
        return graph

# Chart Visualization Components
class ChartVisualization:
    """Chart visualization component."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.chart_renderer = ChartRenderer(config)
        self.data_processor = DataProcessor(config)
    
    async def render_metrics_chart(self, metrics_data: Dict[str, Any], chart_type: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Render metrics as chart."""
        # Process metrics data
        processed_data = await self.data_processor.process_metrics_data(metrics_data, chart_type)
        
        # Generate chart configuration
        chart_config = await self._generate_chart_config(chart_type, processed_data, options)
        
        # Render chart
        chart = await self.chart_renderer.render_chart(chart_config)
        
        return chart
    
    async def render_trend_chart(self, trend_data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """Render trend data as chart."""
        # Process trend data
        processed_data = await self.data_processor.process_trend_data(trend_data)
        
        # Generate trend chart configuration
        chart_config = await self._generate_trend_chart_config(processed_data, options)
        
        # Render trend chart
        chart = await self.chart_renderer.render_trend_chart(chart_config)
        
        return chart

# Timeline Visualization Components
class TimelineVisualization:
    """Timeline visualization component."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.timeline_renderer = TimelineRenderer(config)
        self.event_processor = EventProcessor(config)
    
    async def render_timeline(self, timeline_data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """Render timeline visualization."""
        # Process timeline data
        processed_events = await self.event_processor.process_timeline_events(timeline_data)
        
        # Generate timeline configuration
        timeline_config = await self._generate_timeline_config(processed_events, options)
        
        # Render timeline
        timeline = await self.timeline_renderer.render_timeline(timeline_config)
        
        return timeline
    
    async def render_collaboration_timeline(self, collaboration_data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """Render collaboration timeline."""
        # Process collaboration events
        processed_events = await self.event_processor.process_collaboration_events(collaboration_data)
        
        # Generate collaboration timeline configuration
        timeline_config = await self._generate_collaboration_timeline_config(processed_events, options)
        
        # Render collaboration timeline
        timeline = await self.timeline_renderer.render_collaboration_timeline(timeline_config)
        
        return timeline
```

### AIM-OS Integration Details

#### CMC Integration

The Presentation & API Layer integrates with the Context Memory Core (CMC) to provide intelligent context-aware responses and maintain conversation history:

```python
class CMCIntegration:
    async def store_user_context(self, user_id: str, context_data: Dict[str, Any]) -> CMCAtom:
        """Store user context in CMC with bitemporal tracking."""
        context_atom = CMCAtom(
            modality="user_context",
            content=str(context_data),
            embedding=await self.generate_embedding(str(context_data)),
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
        
        await self.cmc.store_atom_with_bitemporal(context_atom)
        return context_atom
    
    async def retrieve_user_context(self, user_id: str, context_type: str = None) -> List[Dict[str, Any]]:
        """Retrieve user context from CMC."""
        query = {
            "modality": "user_context",
            "tags": ["user_context", user_id]
        }
        
        if context_type:
            query["context_type"] = context_type
        
        results = await self.cmc.query_atoms(query)
        return [self._convert_to_context(result) for result in results]
    
    async def store_api_interaction(self, user_id: str, request: Dict[str, Any], response: Dict[str, Any]) -> CMCAtom:
        """Store API interaction in CMC."""
        interaction_atom = CMCAtom(
            modality="api_interaction",
            content=f"Request: {request}\nResponse: {response}",
            embedding=await self.generate_embedding(f"Request: {request}\nResponse: {response}"),
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
        
        await self.cmc.store_atom_with_bitemporal(interaction_atom)
        return interaction_atom
```

#### HHNI Integration

The Presentation & API Layer leverages the Hierarchical Hypergraph Network Index (HHNI) for intelligent data retrieval and navigation:

```python
class HHNIIntegration:
    async def get_codebase_graph(self, codebase_id: str) -> Dict[str, Any]:
        """Get codebase graph from HHNI."""
        query = {
            "codebase_id": codebase_id,
            "graph_type": "full"
        }
        
        result = await self.hhni.query_graph(query)
        return result
    
    async def semantic_search(self, query: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Perform semantic search using HHNI."""
        search_results = await self.hhni.semantic_search(query, context)
        return search_results
    
    async def get_navigation_suggestions(self, user_id: str, current_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get navigation suggestions from HHNI."""
        query = {
            "user_id": user_id,
            "current_context": current_context,
            "suggestion_type": "navigation"
        }
        
        suggestions = await self.hhni.get_suggestions(query)
        return suggestions
```

#### VIF Integration

The Presentation & API Layer uses the Verification and Integrity Framework (VIF) for response validation and quality assurance:

```python
class VIFIntegration:
    async def validate_response(self, response: APIResponse) -> ValidationResult:
        """Validate API response with VIF."""
        # Validate response structure
        structure_validation = await self.vif.validate_structure(response)
        
        # Validate response content
        content_validation = await self.vif.validate_content(response)
        
        # Calculate confidence score
        confidence_score = await self.vif.calculate_confidence(response)
        
        return ValidationResult(
            is_valid=structure_validation.is_valid and content_validation.is_valid,
            confidence_score=confidence_score,
            issues=structure_validation.issues + content_validation.issues
        )
    
    async def track_response_provenance(self, response: APIResponse) -> None:
        """Track response provenance with VIF."""
        provenance = ProvenanceRecord(
            operation="api_response",
            input_data=response.request,
            output_data=response.body,
            confidence_score=response.metadata.get("confidence_score", 0.8),
            witnesses=response.metadata.get("witnesses", []),
            timestamp=datetime.utcnow()
        )
        
        await self.vif.store_provenance(provenance)
```

#### TCS Integration

The Presentation & API Layer integrates with the Timeline Context System (TCS) for real-time event streaming and collaboration:

```python
class TCSIntegration:
    async def stream_event_to_clients(self, event: TimelineEvent, room_id: str) -> None:
        """Stream event to TCS and WebSocket clients."""
        # Stream event to TCS
        await self.tcs.add_event(event)
        
        # Broadcast to WebSocket clients in room
        await self.websocket_hub.broadcast_to_room(room_id, {
            "type": "timeline_event",
            "event": event.to_dict(),
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def get_timeline_events(self, room_id: str, time_range: TimeRange) -> List[TimelineEvent]:
        """Get timeline events for room."""
        query = {
            "room_id": room_id,
            "start_time": time_range.start_time,
            "end_time": time_range.end_time
        }
        
        events = await self.tcs.query_events(query)
        return events
```

#### APOE Integration

The Presentation & API Layer uses the AI-Powered Orchestration Engine (APOE) for intelligent request processing and response generation:

```python
class APOEIntegration:
    async def orchestrate_request(self, request: APIRequest) -> APIResponse:
        """Orchestrate complex API request using APOE."""
        # Create orchestration plan
        plan = await self.apoe.create_plan(APOETask(
            task_type="api_request",
            input_data=request,
            requirements=APOERequirements(
                max_latency=request.metadata.get("max_latency", 5000),
                quality_threshold=request.metadata.get("quality_threshold", 0.8),
                resource_limits=request.metadata.get("resource_limits", {})
            )
        ))
        
        # Execute plan
        result = await self.apoe.execute_plan(plan)
        
        # Generate response
        response = await self._generate_response(result)
        
        return response
    
    async def plan_visualization_strategy(self, visualization_request: Dict[str, Any]) -> VisualizationPlan:
        """Plan visualization strategy using APOE."""
        task = APOETask(
            task_type="visualization",
            input_data=visualization_request,
            requirements=APOERequirements(
                max_latency=10000,
                quality_threshold=0.9,
                resource_limits={"memory": "2GB", "cpu": "50%"}
            )
        )
        
        plan = await self.apoe.create_plan(task)
        return plan
```

#### SEG Integration

The Presentation & API Layer leverages the Shared Evidence Graph (SEG) for knowledge synthesis and intelligent insights:

```python
class SEGIntegration:
    async def synthesize_insights(self, user_context: Dict[str, Any]) -> List[Insight]:
        """Synthesize insights using SEG."""
        # Synthesize knowledge from SEG
        knowledge_graph = await self.seg.synthesize_knowledge(
            topics=["codebase_analysis", "user_behavior", "collaboration_patterns"],
            context=user_context,
            depth="medium"
        )
        
        # Generate insights
        insights = await self._generate_insights(knowledge_graph)
        
        return insights
    
    async def get_recommendations(self, user_id: str, context: Dict[str, Any]) -> List[Recommendation]:
        """Get personalized recommendations using SEG."""
        # Query SEG for relevant knowledge
        knowledge = await self.seg.query_knowledge({
            "user_id": user_id,
            "context": context,
            "knowledge_types": ["recommendations", "patterns", "insights"]
        })
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(knowledge)
        
        return recommendations
```

#### IIS Integration

The Presentation & API Layer uses the Intuitive Intelligence System (IIS) for enhanced user experience and intelligent interface adaptation:

```python
class IISIntegration:
    async def enhance_user_experience(self, user_context: Dict[str, Any]) -> UXEnhancement:
        """Enhance user experience using IIS."""
        # Calculate intuition score
        intuition_score = await self.iis.compute_intuition(
            confidence=user_context.get("confidence", 0.8),
            context=user_context,
            retrieval_quality=user_context.get("retrieval_quality", 0.8),
            meta_pattern_similarity=user_context.get("pattern_similarity", 0.7),
            emotional_salience=user_context.get("emotional_salience", 0.5),
            evolution_alignment=user_context.get("evolution_alignment", 0.8)
        )
        
        # Enhance user experience based on intuition
        enhancement = await self._enhance_ux(user_context, intuition_score)
        
        return enhancement
    
    async def adapt_interface(self, user_id: str, interface_data: Dict[str, Any]) -> InterfaceAdaptation:
        """Adapt interface based on user behavior using IIS."""
        # Analyze user behavior patterns
        behavior_analysis = await self.iis.analyze_behavior_patterns(user_id, interface_data)
        
        # Generate interface adaptations
        adaptations = await self._generate_interface_adaptations(behavior_analysis)
        
        return adaptations
```

### Security Implementation

#### Authentication and Authorization

```python
class AuthService:
    """Authentication service implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.jwt_secret = config.get("jwt_secret")
        self.jwt_algorithm = config.get("jwt_algorithm", "HS256")
        self.token_expiry = config.get("token_expiry", 3600)
    
    async def validate_token(self, token: str) -> Optional[User]:
        """Validate JWT token."""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            user_id = payload.get("user_id")
            
            if not user_id:
                return None
            
            # Get user from database
            user = await self._get_user(user_id)
            return user
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    async def generate_token(self, user: User) -> str:
        """Generate JWT token for user."""
        payload = {
            "user_id": user.id,
            "email": user.email,
            "roles": user.roles,
            "exp": datetime.utcnow() + timedelta(seconds=self.token_expiry)
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        return token
    
    async def refresh_token(self, refresh_token: str) -> Optional[str]:
        """Refresh JWT token."""
        # Validate refresh token
        user = await self.validate_refresh_token(refresh_token)
        if not user:
            return None
        
        # Generate new token
        new_token = await self.generate_token(user)
        return new_token

class AuthorizationService:
    """Authorization service implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.role_permissions = config.get("role_permissions", {})
    
    async def check_permission(self, user: User, resource: str, action: str) -> bool:
        """Check if user has permission for resource and action."""
        # Check role-based permissions
        for role in user.roles:
            role_perms = self.role_permissions.get(role, {})
            if resource in role_perms and action in role_perms[resource]:
                return True
        
        # Check resource-based permissions
        resource_perms = await self._get_resource_permissions(resource)
        if action in resource_perms and user.id in resource_perms[action]:
            return True
        
        return False
    
    async def check_api_access(self, user: User, endpoint: str, method: str) -> bool:
        """Check if user has access to API endpoint."""
        # Extract resource and action from endpoint
        resource = endpoint.split("/")[0]
        action = method.lower()
        
        return await self.check_permission(user, resource, action)
```

#### Data Protection

```python
class DataProtectionService:
    """Data protection service implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.encryption_key = config.get("encryption_key")
        self.encryption_algorithm = config.get("encryption_algorithm", "AES-256-GCM")
    
    async def encrypt_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt sensitive data."""
        encrypted_data = {}
        
        for key, value in data.items():
            if self._is_sensitive_field(key):
                encrypted_value = await self._encrypt_value(value)
                encrypted_data[key] = encrypted_value
            else:
                encrypted_data[key] = value
        
        return encrypted_data
    
    async def decrypt_sensitive_data(self, encrypted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt sensitive data."""
        decrypted_data = {}
        
        for key, value in encrypted_data.items():
            if self._is_sensitive_field(key):
                decrypted_value = await self._decrypt_value(value)
                decrypted_data[key] = decrypted_value
            else:
                decrypted_data[key] = value
        
        return decrypted_data
    
    async def anonymize_user_data(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize user data for privacy."""
        anonymized_data = user_data.copy()
        
        # Remove or anonymize sensitive fields
        sensitive_fields = ["email", "phone", "address", "ssn", "credit_card"]
        
        for field in sensitive_fields:
            if field in anonymized_data:
                if field == "email":
                    anonymized_data[field] = f"user_{hash(anonymized_data[field])}@example.com"
                else:
                    anonymized_data[field] = "[ANONYMIZED]"
        
        return anonymized_data
    
    def _is_sensitive_field(self, field_name: str) -> bool:
        """Check if field contains sensitive data."""
        sensitive_fields = ["password", "token", "secret", "key", "credential"]
        return any(sensitive in field_name.lower() for sensitive in sensitive_fields)
    
    async def _encrypt_value(self, value: str) -> str:
        """Encrypt a single value."""
        # Implementation would use actual encryption
        return f"encrypted_{value}"
    
    async def _decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt a single value."""
        # Implementation would use actual decryption
        return encrypted_value.replace("encrypted_", "")
```

### Performance Optimization

#### Caching Strategy

```python
class AdvancedCacheService:
    """Advanced caching service with multiple cache layers."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.memory_cache = {}
        self.redis_cache = RedisCache(config.get("redis_url"))
        self.cdn_cache = CDNCache(config.get("cdn_url"))
        self.cache_ttl = config.get("cache_ttl", 3600)
    
    async def get(self, key: str, cache_level: str = "memory") -> Optional[Any]:
        """Get value from specified cache level."""
        if cache_level == "memory":
            return self.memory_cache.get(key)
        elif cache_level == "redis":
            return await self.redis_cache.get(key)
        elif cache_level == "cdn":
            return await self.cdn_cache.get(key)
        
        return None
    
    async def set(self, key: str, value: Any, cache_level: str = "memory", ttl: Optional[int] = None) -> None:
        """Set value in specified cache level."""
        ttl = ttl or self.cache_ttl
        
        if cache_level == "memory":
            self.memory_cache[key] = value
        elif cache_level == "redis":
            await self.redis_cache.set(key, value, ttl)
        elif cache_level == "cdn":
            await self.cdn_cache.set(key, value, ttl)
    
    async def get_or_set(self, key: str, factory_func, cache_level: str = "memory", ttl: Optional[int] = None) -> Any:
        """Get value from cache or set it using factory function."""
        value = await self.get(key, cache_level)
        
        if value is None:
            value = await factory_func()
            await self.set(key, value, cache_level, ttl)
        
        return value
    
    async def invalidate_pattern(self, pattern: str, cache_level: str = "all") -> None:
        """Invalidate cache entries matching pattern."""
        if cache_level in ["memory", "all"]:
            keys_to_remove = [key for key in self.memory_cache.keys() if pattern in key]
            for key in keys_to_remove:
                del self.memory_cache[key]
        
        if cache_level in ["redis", "all"]:
            await self.redis_cache.delete_pattern(pattern)
        
        if cache_level in ["cdn", "all"]:
            await self.cdn_cache.invalidate_pattern(pattern)
```

#### Performance Monitoring

```python
class AdvancedPerformanceMonitor:
    """Advanced performance monitoring with detailed metrics."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.metrics = []
        self.alert_thresholds = config.get("alert_thresholds", {})
        self.monitoring_interval = config.get("monitoring_interval", 60)
        
        # Start monitoring tasks
        asyncio.create_task(self._monitor_performance())
        asyncio.create_task(self._check_alerts())
    
    async def log_performance_metrics(self, request, response, response_time: float) -> None:
        """Log detailed performance metrics."""
        metrics = PerformanceMetrics(
            request_id=getattr(request.state, "request_id", None),
            endpoint=request.url.path,
            method=request.method,
            response_time=response_time,
            status_code=response.status_code,
            timestamp=datetime.utcnow(),
            metadata={
                "user_agent": request.headers.get("user-agent", ""),
                "content_length": response.headers.get("content-length", 0),
                "content_type": response.headers.get("content-type", ""),
                "cache_hit": response.headers.get("x-cache-hit", "false") == "true",
                "database_queries": getattr(request.state, "db_queries", 0),
                "memory_usage": getattr(request.state, "memory_usage", 0)
            }
        )
        
        self.metrics.append(metrics)
        
        # Trim metrics if too many
        if len(self.metrics) > self.config.get("max_metrics", 10000):
            self.metrics = self.metrics[-self.config.get("max_metrics", 10000):]
    
    async def _monitor_performance(self) -> None:
        """Monitor performance metrics continuously."""
        while True:
            try:
                # Calculate performance statistics
                stats = self._calculate_performance_stats()
                
                # Log performance summary
                logger.info(f"Performance stats: {stats}")
                
                # Store metrics in external monitoring system
                await self._store_metrics_in_external_system(stats)
                
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Error in performance monitoring: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _check_alerts(self) -> None:
        """Check for performance alerts."""
        while True:
            try:
                # Check response time alerts
                avg_response_time = self._calculate_average_response_time()
                if avg_response_time > self.alert_thresholds.get("response_time", 2.0):
                    await self._send_alert("High response time", f"Average response time: {avg_response_time:.2f}s")
                
                # Check error rate alerts
                error_rate = self._calculate_error_rate()
                if error_rate > self.alert_thresholds.get("error_rate", 0.05):
                    await self._send_alert("High error rate", f"Error rate: {error_rate:.2%}")
                
                # Check memory usage alerts
                memory_usage = self._calculate_memory_usage()
                if memory_usage > self.alert_thresholds.get("memory_usage", 0.8):
                    await self._send_alert("High memory usage", f"Memory usage: {memory_usage:.2%}")
                
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Error in alert checking: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    def _calculate_performance_stats(self) -> Dict[str, Any]:
        """Calculate performance statistics."""
        if not self.metrics:
            return {}
        
        response_times = [m.response_time for m in self.metrics]
        
        return {
            "total_requests": len(self.metrics),
            "average_response_time": sum(response_times) / len(response_times),
            "min_response_time": min(response_times),
            "max_response_time": max(response_times),
            "p95_response_time": self._calculate_percentile(response_times, 95),
            "p99_response_time": self._calculate_percentile(response_times, 99),
            "error_rate": len([m for m in self.metrics if m.status_code >= 400]) / len(self.metrics),
            "cache_hit_rate": len([m for m in self.metrics if m.metadata.get("cache_hit", False)]) / len(self.metrics)
        }
    
    def _calculate_percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile of values."""
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile / 100)
        return sorted_values[min(index, len(sorted_values) - 1)]
    
    async def _send_alert(self, alert_type: str, message: str) -> None:
        """Send performance alert."""
        # Implementation would send alert to monitoring system
        logger.warning(f"Performance alert: {alert_type} - {message}")
```

### Testing Strategy

#### Unit Tests

```python
class TestAPIGateway:
    """Unit tests for API Gateway."""
    
    @pytest.mark.asyncio
    async def test_rest_server_startup(self):
        """Test REST server startup."""
        config = {"test": True}
        server = RESTServer(config)
        
        # Test server initialization
        assert server.app is not None
        assert server.auth_service is not None
        assert server.rate_limit_service is not None
    
    @pytest.mark.asyncio
    async def test_authentication_middleware(self):
        """Test authentication middleware."""
        config = {"test": True}
        server = RESTServer(config)
        
        # Test valid token
        valid_token = "valid_token"
        # Mock auth service
        server.auth_service.validate_token = AsyncMock(return_value=User(id="test_user"))
        
        # Test invalid token
        invalid_token = "invalid_token"
        server.auth_service.validate_token = AsyncMock(return_value=None)
    
    @pytest.mark.asyncio
    async def test_rate_limiting_middleware(self):
        """Test rate limiting middleware."""
        config = {"test": True}
        server = RESTServer(config)
        
        # Test rate limit check
        server.rate_limit_service.check_rate_limit = AsyncMock(return_value=True)
        
        # Test rate limit exceeded
        server.rate_limit_service.check_rate_limit = AsyncMock(return_value=False)

class TestWebSocketHub:
    """Unit tests for WebSocket Hub."""
    
    @pytest.mark.asyncio
    async def test_connection_management(self):
        """Test WebSocket connection management."""
        config = {"test": True}
        connection_manager = ConnectionManager(config)
        
        # Test connection establishment
        websocket = Mock()
        user_id = "test_user"
        
        connection_id = await connection_manager.connect(websocket, user_id)
        assert connection_id is not None
        assert connection_id in connection_manager.connections
    
    @pytest.mark.asyncio
    async def test_room_management(self):
        """Test room management."""
        config = {"test": True}
        connection_manager = ConnectionManager(config)
        
        # Test room joining
        connection_id = "test_connection"
        room_id = "test_room"
        
        success = await connection_manager.join_room(connection_id, room_id)
        assert success is True
    
    @pytest.mark.asyncio
    async def test_message_handling(self):
        """Test message handling."""
        config = {"test": True}
        connection_manager = ConnectionManager(config)
        
        # Test message handling
        connection_id = "test_connection"
        message = {"type": "test_message", "content": "test"}
        
        await connection_manager.handle_message(connection_id, json.dumps(message))

class TestVisualizationEngine:
    """Unit tests for Visualization Engine."""
    
    @pytest.mark.asyncio
    async def test_graph_rendering(self):
        """Test graph rendering."""
        config = {"test": True}
        graph_renderer = GraphRenderer(config)
        
        # Test codebase graph rendering
        codebase_id = "test_codebase"
        options = {"layout": "force_directed"}
        
        graph = await graph_renderer.render_codebase_graph(codebase_id, options)
        assert graph is not None
        assert "nodes" in graph
        assert "edges" in graph
    
    @pytest.mark.asyncio
    async def test_chart_rendering(self):
        """Test chart rendering."""
        config = {"test": True}
        chart_renderer = ChartRenderer(config)
        
        # Test metrics chart rendering
        metrics_data = {"metric1": 100, "metric2": 200}
        chart_type = "bar"
        options = {}
        
        chart = await chart_renderer.render_metrics_chart(metrics_data, chart_type, options)
        assert chart is not None
        assert "data" in chart
        assert "config" in chart
```

#### Integration Tests

```python
class TestAIMOSIntegration:
    """Integration tests for AIM-OS integration."""
    
    @pytest.mark.asyncio
    async def test_cmc_integration(self):
        """Test CMC integration."""
        config = {"test": True}
        cmc_integration = CMCIntegration(config)
        
        # Test user context storage
        user_id = "test_user"
        context_data = {"session_id": "test_session", "data": "test"}
        
        atom = await cmc_integration.store_user_context(user_id, context_data)
        assert atom is not None
        assert atom.modality == "user_context"
    
    @pytest.mark.asyncio
    async def test_hhni_integration(self):
        """Test HHNI integration."""
        config = {"test": True}
        hhni_integration = HHNIIntegration(config)
        
        # Test codebase graph retrieval
        codebase_id = "test_codebase"
        
        graph = await hhni_integration.get_codebase_graph(codebase_id)
        assert graph is not None
    
    @pytest.mark.asyncio
    async def test_vif_integration(self):
        """Test VIF integration."""
        config = {"test": True}
        vif_integration = VIFIntegration(config)
        
        # Test response validation
        response = APIResponse(
            request_id="test_request",
            status_code=200,
            headers={},
            body={"data": "test"},
            response_time=0.5,
            timestamp=datetime.utcnow(),
            metadata={}
        )
        
        validation_result = await vif_integration.validate_response(response)
        assert validation_result is not None
```

#### End-to-End Tests

```python
class TestE2EAPI:
    """End-to-end tests for API."""
    
    @pytest.mark.asyncio
    async def test_full_api_workflow(self):
        """Test complete API workflow."""
        # Start test server
        config = {"test": True}
        server = RESTServer(config)
        await server.start()
        
        try:
            # Test API endpoints
            async with AsyncClient(app=server.app, base_url="http://test") as client:
                # Test health check
                response = await client.get("/health")
                assert response.status_code == 200
                
                # Test codebase endpoint
                response = await client.get("/api/v1/codebase/test_codebase")
                assert response.status_code == 200
                
                # Test analytics endpoint
                response = await client.get("/api/v1/analytics/metrics?codebase_id=test_codebase")
                assert response.status_code == 200
                
                # Test insights endpoint
                response = await client.get("/api/v1/insights/recommendations?user_id=test_user")
                assert response.status_code == 200
        
        finally:
            await server.stop()
    
    @pytest.mark.asyncio
    async def test_websocket_workflow(self):
        """Test complete WebSocket workflow."""
        # Start test server
        config = {"test": True}
        server = RESTServer(config)
        await server.start()
        
        try:
            # Test WebSocket connection
            async with websockets.connect("ws://test/ws") as websocket:
                # Test connection establishment
                message = await websocket.recv()
                assert json.loads(message)["type"] == "connection_established"
                
                # Test room joining
                join_message = {"type": "join_room", "room_id": "test_room"}
                await websocket.send(json.dumps(join_message))
                
                # Test message sending
                send_message = {"type": "send_message", "content": "test", "room_id": "test_room"}
                await websocket.send(json.dumps(send_message))
                
                # Test message receiving
                message = await websocket.recv()
                assert json.loads(message)["type"] == "message_received"
        
        finally:
            await server.stop()
```

### Deployment and Operations

#### Docker Configuration

```dockerfile
# Dockerfile for Presentation & API Layer
FROM node:18-alpine AS frontend-build

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci --only=production

COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY --from=frontend-build /app/frontend/dist ./static/

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["python", "-m", "src.main"]
```

#### Kubernetes Configuration

```yaml
# kubernetes.yaml for Presentation & API Layer
apiVersion: apps/v1
kind: Deployment
metadata:
  name: presentation-api-layer
  labels:
    app: presentation-api-layer
spec:
  replicas: 3
  selector:
    matchLabels:
      app: presentation-api-layer
  template:
    metadata:
      labels:
        app: presentation-api-layer
    spec:
      containers:
      - name: presentation-api-layer
        image: presentation-api-layer:latest
        ports:
        - containerPort: 8000
        env:
        - name: CMC_URL
          value: "http://cmc-service:8000"
        - name: HHNI_URL
          value: "http://hhni-service:8000"
        - name: VIF_URL
          value: "http://vif-service:8000"
        - name: TCS_URL
          value: "http://tcs-service:8000"
        - name: APOE_URL
          value: "http://apoe-service:8000"
        - name: SEG_URL
          value: "http://seg-service:8000"
        - name: IIS_URL
          value: "http://iis-service:8000"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: presentation-api-layer-service
spec:
  selector:
    app: presentation-api-layer
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: presentation-api-layer-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - api.icip.example.com
    secretName: icip-tls
  rules:
  - host: api.icip.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: presentation-api-layer-service
            port:
              number: 80
```

#### Monitoring Configuration

```yaml
# monitoring.yaml for Presentation & API Layer
apiVersion: v1
kind: ConfigMap
metadata:
  name: presentation-api-monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    scrape_configs:
    - job_name: 'presentation-api-layer'
      static_configs:
      - targets: ['presentation-api-layer-service:80']
      metrics_path: /metrics
      scrape_interval: 5s
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      containers:
      - name: prometheus
        image: prom/prometheus:latest
        ports:
        - containerPort: 9090
        volumeMounts:
        - name: config
          mountPath: /etc/prometheus
      volumes:
      - name: config
        configMap:
          name: presentation-api-monitoring
---
apiVersion: v1
kind: Service
metadata:
  name: prometheus-service
spec:
  selector:
    app: prometheus
  ports:
  - protocol: TCP
    port: 9090
    targetPort: 9090
  type: ClusterIP
```

This L4 complete documentation provides comprehensive reference information for the Presentation & API Layer, including detailed implementation examples, integration patterns, testing strategies, and operational considerations.
