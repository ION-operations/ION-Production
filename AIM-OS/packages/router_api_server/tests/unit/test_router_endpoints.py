"""
Router API Server - Unit Tests

# NL_TAG: ROUTER-API-TEST-001 | Unit tests for Router API endpoints | test_router_endpoints | []
# NL_TAG_CONNECT: ROUTER-API-TEST-SERVICE-001 | Unit tests mock RouterService | test_router_endpoints → RouterService | [ROUTER-API-TEST-001, ROUTER-API-SERVICE-001]
# NL_TAG_INTENT: ROUTER-API-DESIGN-007 | Unit tests ensure API endpoints work correctly with mocked dependencies | Test-driven development | [ADR-TESTING]
# NL_TAG_SPEC: ROUTER-API-SPEC-008 | Validates unit test coverage ≥80% for all endpoints | Test coverage | [coverage_report.json]
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any
import json

from router_api_server.main import create_app
from router_api_server.services.router_service import RouterService
from router_api_server.services.log_sentinels_service import LogSentinelsService
from router_api_server.mcp_client import MCPClient


@pytest.fixture
def mock_mcp_client():
    """Mock MCP client."""
    client = Mock(spec=MCPClient)
    client.execute_tool = AsyncMock(return_value={"success": True, "result": "test"})
    return client


@pytest.fixture
def mock_router_service(mock_mcp_client):
    """Mock Router service."""
    service = Mock(spec=RouterService)
    service.get_tool_proposals = AsyncMock(return_value={
        "tools": [
            {
                "tool_name": "test_tool",
                "rationale": "Test tool",
                "draft_arguments": {},
                "confidence": 0.8,
                "probability": 0.9
            }
        ],
        "suggestions": [],
        "plan_id": "test-plan-123"
    })
    service.get_telemetry = AsyncMock(return_value={
        "avg_latency": 150.0,
        "latency_trend": "stable",
        "success_rate": 0.85,
        "success_trend": "up",
        "avg_cost": 0.05,
        "cost_trend": "stable",
        "tools": []
    })
    service.execute_tool = AsyncMock(return_value={
        "success": True,
        "result": {"test": "result"},
        "plan_id": "test-plan-123"
    })
    return service


@pytest.fixture
def mock_log_sentinels_service(mock_mcp_client):
    """Mock Log-Sentinels service."""
    service = Mock(spec=LogSentinelsService)
    service.get_scout_reports = AsyncMock(return_value=[])
    service.get_forensics_reports = AsyncMock(return_value=[])
    service.get_telemetry = AsyncMock(return_value={
        "scout_calls": 42,
        "forensics_calls": 8,
        "escalations": 2,
        "tool_suggestions": 15,
        "timeline": []
    })
    service.run_tool = AsyncMock(return_value={
        "success": True,
        "result": {"test": "result"}
    })
    return service


@pytest.fixture
def client(mock_router_service, mock_log_sentinels_service):
    """Test client with mocked services."""
    app = create_app()
    app.state.router_service = mock_router_service
    app.state.log_sentinels_service = mock_log_sentinels_service
    return TestClient(app)


class TestRouterEndpoints:
    """Test Router API endpoints."""
    
    def test_get_tools_success(self, client, mock_router_service):
        """Test GET /api/router/tools success."""
        response = client.get(
            "/api/router/tools",
            params={
                "goal": "test goal",
                "task": "test task",
                "confidence": 0.8,
                "agent_intent": "execute"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "tools" in data
        assert "suggestions" in data
        assert len(data["tools"]) == 1
        assert data["tools"][0]["tool_name"] == "test_tool"
        mock_router_service.get_tool_proposals.assert_called_once()
    
    def test_get_tools_missing_params(self, client):
        """Test GET /api/router/tools with missing params."""
        response = client.get("/api/router/tools")
        assert response.status_code == 422  # Validation error
    
    def test_get_telemetry_success(self, client, mock_router_service):
        """Test GET /api/router/telemetry success."""
        response = client.get("/api/router/telemetry")
        
        assert response.status_code == 200
        data = response.json()
        assert "avg_latency" in data
        assert "success_rate" in data
        assert data["success_rate"] == 0.85
        mock_router_service.get_telemetry.assert_called_once()
    
    def test_execute_tool_success(self, client, mock_router_service):
        """Test POST /api/router/execute success."""
        response = client.post(
            "/api/router/execute",
            json={
                "tool": "test_tool",
                "args": {"param": "value"}
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "result" in data
        mock_router_service.execute_tool.assert_called_once_with(
            tool_name="test_tool",
            args={"param": "value"}
        )
    
    def test_execute_tool_invalid_request(self, client):
        """Test POST /api/router/execute with invalid request."""
        response = client.post("/api/router/execute", json={})
        assert response.status_code == 422  # Validation error
    
    def test_execute_tool_service_error(self, client, mock_router_service):
        """Test POST /api/router/execute with service error."""
        mock_router_service.execute_tool = AsyncMock(side_effect=ValueError("Tool not found"))
        
        response = client.post(
            "/api/router/execute",
            json={
                "tool": "nonexistent_tool",
                "args": {}
            }
        )
        
        assert response.status_code == 404
        assert "Tool not found" in response.json()["detail"]


class TestLogSentinelsEndpoints:
    """Test Log-Sentinels API endpoints."""
    
    def test_get_scouts_success(self, client, mock_log_sentinels_service):
        """Test GET /api/log-sentinels/scouts success."""
        response = client.get("/api/log-sentinels/scouts")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        mock_log_sentinels_service.get_scout_reports.assert_called_once()
    
    def test_get_forensics_success(self, client, mock_log_sentinels_service):
        """Test GET /api/log-sentinels/forensics success."""
        response = client.get("/api/log-sentinels/forensics")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        mock_log_sentinels_service.get_forensics_reports.assert_called_once()
    
    def test_get_telemetry_success(self, client, mock_log_sentinels_service):
        """Test GET /api/log-sentinels/telemetry success."""
        response = client.get("/api/log-sentinels/telemetry")
        
        assert response.status_code == 200
        data = response.json()
        assert "scout_calls" in data
        assert data["scout_calls"] == 42
        mock_log_sentinels_service.get_telemetry.assert_called_once()
    
    def test_run_tool_success(self, client, mock_log_sentinels_service):
        """Test POST /api/log-sentinels/run-tool success."""
        response = client.post(
            "/api/log-sentinels/run-tool",
            json={"tool": "test_tool"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        mock_log_sentinels_service.run_tool.assert_called_once_with("test_tool")
    
    def test_run_tool_invalid_request(self, client):
        """Test POST /api/log-sentinels/run-tool with invalid request."""
        response = client.post("/api/log-sentinels/run-tool", json={})
        assert response.status_code == 422  # Validation error


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_check(self, client):
        """Test GET /health."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "router-log-sentinels-api-server"

