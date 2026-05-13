"""
Router API Server - Integration Tests

# NL_TAG: ROUTER-API-TEST-002 | Integration tests for Router API server with MCP integration | test_mcp_integration | []
# NL_TAG_CONNECT: ROUTER-API-TEST-MCP-001 | Integration tests verify MCP client integration | test_mcp_integration → MCPClient | [ROUTER-API-TEST-002, ROUTER-API-MCP-001]
# NL_TAG_INTENT: ROUTER-API-DESIGN-008 | Integration tests ensure API server works with real MCP client | Integration testing | [ADR-TESTING]
# NL_TAG_SPEC: ROUTER-API-SPEC-009 | Validates integration test coverage for MCP, PLIx, and APOE flows | Integration test coverage | [integration_coverage.json]
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch
import httpx
import asyncio

from router_api_server.main import create_app
from router_api_server.mcp_client import MCPClient
from router_api_server.services.router_service import RouterService
from router_api_server.services.log_sentinels_service import LogSentinelsService


@pytest.fixture
def mock_httpx_client():
    """Mock httpx client for MCP calls."""
    with patch('router_api_server.mcp_client.httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "result": "test"}
        mock_response.raise_for_status = Mock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client_class.return_value.__aexit__.return_value = None
        yield mock_client


@pytest.fixture
def mcp_client(mock_httpx_client):
    """MCP client with mocked HTTP client."""
    return MCPClient(command_server_url="http://localhost:5001")


@pytest.fixture
def router_service(mcp_client):
    """Router service with real MCP client."""
    return RouterService(mcp_client=mcp_client)


@pytest.fixture
def log_sentinels_service(mcp_client):
    """Log-Sentinels service with real MCP client."""
    return LogSentinelsService(mcp_client=mcp_client)


@pytest.fixture
def client(router_service, log_sentinels_service):
    """Test client with real services."""
    app = create_app()
    app.state.router_service = router_service
    app.state.log_sentinels_service = log_sentinels_service
    return TestClient(app)


class TestMCPIntegration:
    """Test MCP client integration."""
    
    @pytest.mark.asyncio
    async def test_mcp_client_execute_tool(self, mcp_client, mock_httpx_client):
        """Test MCP client tool execution."""
        result = await mcp_client.execute_tool(
            tool_name="mcp_lucid-mcp_store_memory",
            arguments={"content": "test", "tags": {}}
        )
        
        assert result["success"] is True
        mock_httpx_client.post.assert_called_once()
        call_args = mock_httpx_client.post.call_args
        assert call_args[0][0] == "http://localhost:5001/mcp/execute"
        assert call_args[1]["json"]["tool"] == "mcp_lucid-mcp_store_memory"
    
    @pytest.mark.asyncio
    async def test_mcp_client_retry_on_failure(self, mcp_client, mock_httpx_client):
        """Test MCP client retry logic."""
        # First two calls fail, third succeeds
        mock_response_fail = Mock()
        mock_response_fail.status_code = 500
        mock_response_fail.text = "Internal Server Error"
        mock_response_fail.raise_for_status = Mock(side_effect=httpx.HTTPStatusError(
            "Server Error", request=Mock(), response=mock_response_fail
        ))
        
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {"success": True}
        mock_response_success.raise_for_status = Mock()
        
        mock_httpx_client.post = AsyncMock(side_effect=[
            mock_response_fail,
            mock_response_fail,
            mock_response_success
        ])
        
        result = await mcp_client.execute_tool(
            tool_name="test_tool",
            arguments={},
            retries=3
        )
        
        assert result["success"] is True
        assert mock_httpx_client.post.call_count == 3
    
    @pytest.mark.asyncio
    async def test_mcp_client_batch_execute(self, mcp_client, mock_httpx_client):
        """Test MCP client batch execution."""
        tools = [
            ("mcp_lucid-mcp_store_memory", {"content": "test1"}),
            ("mcp_lucid-mcp_retrieve_memory", {"query": "test"})
        ]
        
        results = await mcp_client.batch_execute(tools, max_parallel=2)
        
        assert len(results) == 2
        assert all(r["success"] for r in results)
        assert mock_httpx_client.post.call_count == 2


class TestRouterServiceIntegration:
    """Test Router service integration with MCP."""
    
    @pytest.mark.asyncio
    async def test_router_service_get_tool_proposals(self, router_service, mock_httpx_client):
        """Test Router service tool proposal generation."""
        # Mock Router.decide() to return a plan
        with patch.object(router_service.router, 'decide', new_callable=AsyncMock) as mock_decide:
            from router.types import ToolCallPlan, ToolCallStep
            mock_plan = ToolCallPlan(
                plan_id="test-plan",
                steps=[
                    ToolCallStep(
                        id="step1",
                        tool="test_tool",
                        args={},
                        description="Test tool"
                    )
                ]
            )
            mock_decide.return_value = mock_plan
            
            result = await router_service.get_tool_proposals(
                goal="test goal",
                task="test task",
                confidence=0.8,
                files=[],
                errors=[],
                agent_intent="execute"
            )
            
            assert "tools" in result
            assert "suggestions" in result
            mock_decide.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_router_service_execute_tool_with_plix(self, router_service, mock_httpx_client):
        """Test Router service tool execution with PLIx integration."""
        # Mock PLIx compiler and APOE executor
        with patch.object(router_service.plix_compiler, 'compile_tool_execution', new_callable=AsyncMock) as mock_compile, \
             patch.object(router_service.apoe_executor, 'execute_plan', new_callable=AsyncMock) as mock_execute:
            
            from router_api_server.integrations.plix_compiler import ExecutionPlan
            mock_plan = ExecutionPlan(
                plan_id="test-plan",
                steps=[{"id": "step1", "action": "test_tool", "inputs": {}}],
                roles={"test_role": "test_role"},
                gates=[],
                budget={"max_cost": 1.0, "max_time": 300000, "max_tokens": 10000}
            )
            mock_compile.return_value = mock_plan
            mock_execute.return_value = {
                "success": True,
                "outcome": {"test": "result"},
                "intent_achieved": True,
                "evidence": {}
            }
            
            result = await router_service.execute_tool(
                tool_name="test_tool",
                args={"param": "value"}
            )
            
            assert result["success"] is True
            assert result["intent_achieved"] is True
            mock_compile.assert_called_once()
            mock_execute.assert_called_once()


class TestLogSentinelsServiceIntegration:
    """Test Log-Sentinels service integration with MCP."""
    
    @pytest.mark.asyncio
    async def test_log_sentinels_service_get_scout_reports(self, log_sentinels_service):
        """Test Log-Sentinels service Scout report generation."""
        # Mock pipeline.collect_and_process()
        with patch.object(log_sentinels_service.pipeline, 'collect_and_process', new_callable=AsyncMock) as mock_process:
            mock_process.return_value = {
                "scout_reports": [],
                "forensics_reports": []
            }
            
            reports = await log_sentinels_service.get_scout_reports()
            
            assert isinstance(reports, list)
            mock_process.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_log_sentinels_service_run_tool(self, log_sentinels_service, mock_httpx_client):
        """Test Log-Sentinels service tool execution."""
        result = await log_sentinels_service.run_tool("test_tool")
        
        assert result["success"] is True
        mock_httpx_client.post.assert_called_once()

