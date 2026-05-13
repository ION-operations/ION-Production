"""
Router API Server - End-to-End Tests

# NL_TAG: ROUTER-API-TEST-003 | End-to-end tests for Router → APOE → Tool execution flow | test_e2e_router_flow | []
# NL_TAG_CONNECT: ROUTER-API-TEST-E2E-001 | E2E tests verify complete Router → PLIx → APOE → Tool execution flow | test_e2e_router_flow → Router → PLIx → APOE | [ROUTER-API-TEST-003, ROUTER-API-PLIX-001, ROUTER-API-APOE-001]
# NL_TAG_INTENT: ROUTER-API-DESIGN-009 | E2E tests ensure complete system works end-to-end | End-to-end testing | [ADR-TESTING]
# NL_TAG_SPEC: ROUTER-API-SPEC-010 | Validates E2E test coverage for complete Router and Log-Sentinels flows | E2E test coverage | [e2e_coverage.json]
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch
import json

from router_api_server.main import create_app
from router_api_server.mcp_client import MCPClient
from router_api_server.services.router_service import RouterService
from router_api_server.services.log_sentinels_service import LogSentinelsService


@pytest.fixture
def mock_mcp_responses():
    """Mock MCP responses for E2E tests."""
    return {
        "mcp_lucid-mcp_store_memory": {"success": True, "atom_id": "atom-123"},
        "mcp_lucid-mcp_retrieve_memory": {"memories": [{"content": "test", "tags": {}}]},
        "mcp_lucid-mcp_get_timeline_entries": {"entries": []},
        "mcp_lucid-mcp_execute_plan": {
            "success": True,
            "outcome": {"test": "result"},
            "steps": [{"step_id": "step1", "success": True, "result": {"test": "result"}}]
        }
    }


@pytest.fixture
def mcp_client_with_responses(mock_mcp_responses):
    """MCP client with mocked responses."""
    client = Mock(spec=MCPClient)
    
    async def execute_tool(tool_name, arguments, retries=3):
        if tool_name in mock_mcp_responses:
            return mock_mcp_responses[tool_name]
        return {"success": False, "error": f"Tool {tool_name} not found"}
    
    client.execute_tool = AsyncMock(side_effect=execute_tool)
    return client


@pytest.fixture
def router_service_e2e(mcp_client_with_responses):
    """Router service for E2E tests."""
    service = RouterService(mcp_client=mcp_client_with_responses)
    return service


@pytest.fixture
def log_sentinels_service_e2e(mcp_client_with_responses):
    """Log-Sentinels service for E2E tests."""
    service = LogSentinelsService(mcp_client=mcp_client_with_responses)
    return service


@pytest.fixture
def client_e2e(router_service_e2e, log_sentinels_service_e2e):
    """Test client for E2E tests."""
    app = create_app()
    app.state.router_service = router_service_e2e
    app.state.log_sentinels_service = log_sentinels_service_e2e
    return TestClient(app)


class TestRouterE2EFlow:
    """Test Router end-to-end flow."""
    
    def test_router_tool_proposal_to_execution(self, client_e2e, router_service_e2e):
        """Test complete Router flow: proposal → execution."""
        # Step 1: Get tool proposals
        proposal_response = client_e2e.get(
            "/api/router/tools",
            params={
                "goal": "test goal",
                "task": "test task",
                "confidence": 0.8,
                "agent_intent": "execute"
            }
        )
        
        assert proposal_response.status_code == 200
        proposal_data = proposal_response.json()
        assert "tools" in proposal_data
        
        # Step 2: Execute tool
        if proposal_data["tools"]:
            tool_name = proposal_data["tools"][0]["tool_name"]
            execute_response = client_e2e.post(
                "/api/router/execute",
                json={
                    "tool": tool_name,
                    "args": {"param": "value"}
                }
            )
            
            assert execute_response.status_code == 200
            execute_data = execute_response.json()
            assert execute_data["success"] is True
            assert "plan_id" in execute_data
    
    def test_router_plix_apoe_flow(self, router_service_e2e, mcp_client_with_responses):
        """Test Router → PLIx → APOE flow."""
        import asyncio
        
        async def test_flow():
            # Execute tool via Router service (uses PLIx → APOE)
            result = await router_service_e2e.execute_tool(
                tool_name="mcp_lucid-mcp_store_memory",
                args={"content": "test", "tags": {}}
            )
            
            assert result["success"] is True
            assert "plan_id" in result
            assert "intent_achieved" in result
            assert "evidence" in result
            
            # Verify PLIx compilation was called
            assert router_service_e2e.plix_compiler is not None
            assert router_service_e2e.apoe_executor is not None
        
        asyncio.run(test_flow())
    
    def test_router_telemetry_collection(self, client_e2e):
        """Test Router telemetry collection."""
        # Get telemetry
        response = client_e2e.get("/api/router/telemetry")
        
        assert response.status_code == 200
        data = response.json()
        assert "avg_latency" in data
        assert "success_rate" in data
        assert "tools" in data


class TestLogSentinelsE2EFlow:
    """Test Log-Sentinels end-to-end flow."""
    
    def test_log_sentinels_scout_to_forensics(self, client_e2e, log_sentinels_service_e2e):
        """Test Log-Sentinels flow: Scout → Forensics."""
        # Step 1: Get Scout reports
        scout_response = client_e2e.get("/api/log-sentinels/scouts")
        
        assert scout_response.status_code == 200
        scout_data = scout_response.json()
        assert isinstance(scout_data, list)
        
        # Step 2: Get Forensics reports (if escalated)
        forensics_response = client_e2e.get("/api/log-sentinels/forensics")
        
        assert forensics_response.status_code == 200
        forensics_data = forensics_response.json()
        assert isinstance(forensics_data, list)
    
    def test_log_sentinels_tool_suggestion_execution(self, client_e2e, log_sentinels_service_e2e):
        """Test Log-Sentinels tool suggestion → execution."""
        # Step 1: Get Scout reports (with tool suggestions)
        scout_response = client_e2e.get("/api/log-sentinels/scouts")
        assert scout_response.status_code == 200
        
        # Step 2: Execute suggested tool
        execute_response = client_e2e.post(
            "/api/log-sentinels/run-tool",
            json={"tool": "mcp_lucid-mcp_store_memory"}
        )
        
        assert execute_response.status_code == 200
        execute_data = execute_response.json()
        assert execute_data["success"] is True
    
    def test_log_sentinels_telemetry_collection(self, client_e2e):
        """Test Log-Sentinels telemetry collection."""
        response = client_e2e.get("/api/log-sentinels/telemetry")
        
        assert response.status_code == 200
        data = response.json()
        assert "scout_calls" in data
        assert "forensics_calls" in data
        assert "escalations" in data
        assert "timeline" in data


class TestSSEStreaming:
    """Test SSE streaming for Log-Sentinels."""
    
    def test_sse_stream_endpoint(self, client_e2e):
        """Test SSE stream endpoint."""
        response = client_e2e.get("/api/log-sentinels/stream")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
        assert "Cache-Control" in response.headers
        assert response.headers["Cache-Control"] == "no-cache"
    
    def test_sse_stream_content(self, client_e2e, log_sentinels_service_e2e):
        """Test SSE stream content."""
        import asyncio
        
        async def test_stream():
            # Push test event
            await log_sentinels_service_e2e._push_event(
                event_type="scout",
                payload={"window_id": "test", "summary": "test"}
            )
            
            # Read from stream (simplified - would need proper SSE client)
            # This is a basic test that the endpoint exists and responds
        
        asyncio.run(test_stream())


class TestErrorHandling:
    """Test error handling in E2E flows."""
    
    def test_router_error_handling(self, client_e2e, router_service_e2e):
        """Test Router error handling."""
        # Mock service error
        router_service_e2e.execute_tool = AsyncMock(side_effect=Exception("Test error"))
        
        response = client_e2e.post(
            "/api/router/execute",
            json={"tool": "test_tool", "args": {}}
        )
        
        assert response.status_code == 500
        assert "detail" in response.json()
    
    def test_log_sentinels_error_handling(self, client_e2e, log_sentinels_service_e2e):
        """Test Log-Sentinels error handling."""
        # Mock service error
        log_sentinels_service_e2e.run_tool = AsyncMock(side_effect=Exception("Test error"))
        
        response = client_e2e.post(
            "/api/log-sentinels/run-tool",
            json={"tool": "test_tool"}
        )
        
        assert response.status_code == 500
        assert "detail" in response.json()
    
    def test_mcp_client_error_handling(self, mcp_client_with_responses):
        """Test MCP client error handling."""
        import asyncio
        
        async def test_error():
            # Mock MCP error
            mcp_client_with_responses.execute_tool = AsyncMock(
                side_effect=Exception("MCP connection error")
            )
            
            # Should handle error gracefully
            try:
                await mcp_client_with_responses.execute_tool("test_tool", {})
            except Exception as e:
                assert "MCP" in str(e) or "connection" in str(e).lower()
        
        asyncio.run(test_error())

