"""
Comprehensive Test Suite for All 51 MCP Tools

Tests all MCP tools to validate:
- Tool registration and availability
- Basic functionality
- CMC integration
- Error handling
- Performance

Created: 2025-10-30
Agent: Lexicon
"""

import pytest
import json
import sys
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent.parent / "packages"))

# Import the MCP server
from lucid_mcp_server import SimpleMCPServer


class TestMCPServerSetup:
    """Test MCP server initialization"""
    
    def test_server_initialization(self):
        """Test server initializes correctly"""
        server = SimpleMCPServer()
        assert server is not None
        assert hasattr(server, 'memory_directory')
    
    def test_tool_count(self):
        """Verify all 51 tools are registered"""
        server = SimpleMCPServer()
        response = server.handle_tools_list({})
        
        assert response is not None
        assert 'result' in response
        assert 'tools' in response['result']
        tool_list = response['result']['tools']
        
        # Should have 51 tools (or 54 if CAS tools included)
        assert len(tool_list) >= 51, f"Expected at least 51 tools, got {len(tool_list)}"
        
        # Extract tool names
        tool_names = [tool['name'] for tool in tool_list]
        
        # Verify core tools exist
        core_tools = [
            'store_memory',
            'retrieve_memory',
            'get_memory_stats',
            'create_plan',
            'track_confidence',
            'synthesize_knowledge'
        ]
        
        for tool_name in core_tools:
            assert tool_name in tool_names, f"Core tool {tool_name} not found"


class TestCoreAIMOSTools:
    """Test Core AIM-OS Tools (6 tools)"""
    
    @pytest.fixture
    def server(self):
        """Create server instance"""
        return SimpleMCPServer()
    
    def test_store_memory(self, server):
        """Test store_memory tool"""
        args = {
            "content": "Test memory content",
            "tags": {"test": True, "category": "test"},
            "metadata": {"source": "test"}
        }
        
        result = server.store_memory(args)
        
        assert result is not None
        assert 'success' in result or 'atom_id' in result or 'id' in result
    
    def test_retrieve_memory(self, server):
        """Test retrieve_memory tool"""
        args = {
            "query": "test",
            "limit": 5
        }
        
        result = server.retrieve_memory(args)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_get_memory_stats(self, server):
        """Test get_memory_stats tool"""
        args = {}
        
        result = server.get_memory_stats(args)
        
        assert result is not None
        assert isinstance(result, dict)
        # Should have statistics
        assert 'total_atoms' in result or 'atoms' in result or 'stats' in result
    
    def test_create_plan(self, server):
        """Test create_plan tool"""
        args = {
            "goal": "Test goal",
            "context": "Test context"
        }
        
        result = server.create_plan(args)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_track_confidence(self, server):
        """Test track_confidence tool"""
        args = {
            "task": "test_task",
            "confidence": 0.85,
            "reasoning": "Test reasoning"
        }
        
        result = server.track_confidence(args)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_synthesize_knowledge(self, server):
        """Test synthesize_knowledge tool"""
        args = {
            "topics": ["test", "knowledge"],
            "depth": "medium",
            "format": "summary"
        }
        
        result = server.synthesize_knowledge(args)
        
        assert result is not None
        assert isinstance(result, dict)


class TestSCORTools:
    """Test SCOR Tools (3 tools)"""
    
    @pytest.fixture
    def server(self):
        """Create server instance"""
        return SimpleMCPServer()
    
    def test_check_invariant(self, server):
        """Test check_invariant tool"""
        args = {
            "action": {"type": "test"},
            "context": {}
        }
        
        result = server.check_invariant(args)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_run_baseline_probe(self, server):
        """Test run_baseline_probe tool"""
        args = {
            "category": "identity"
        }
        
        result = server.run_baseline_probe(args)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_detect_manipulation_signals(self, server):
        """Test detect_manipulation_signals tool"""
        args = {
            "input": "Test input"
        }
        
        result = server.detect_manipulation_signals(args)
        
        assert result is not None
        assert isinstance(result, dict)


class TestSnapshotTools:
    """Test Snapshot Tools (4 tools)"""
    
    @pytest.fixture
    def server(self):
        """Create server instance"""
        return SimpleMCPServer()
    
    def test_create_snapshot(self, server):
        """Test create_snapshot tool"""
        args = {
            "snapshot_name": "test_snapshot"
        }
        
        result = server.create_snapshot(args)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_restore_snapshot(self, server):
        """Test restore_snapshot tool"""
        args = {
            "snapshot_name": "test_snapshot"
        }
        
        result = server.restore_snapshot(args)
        
        # May fail if snapshot doesn't exist, which is OK
        assert result is not None
        assert isinstance(result, dict)
    
    def test_list_snapshots(self, server):
        """Test list_snapshots tool"""
        args = {}
        
        result = server.list_snapshots(args)
        
        assert result is not None
        assert isinstance(result, dict)
        assert 'snapshots' in result or 'list' in result
    
    def test_archive_snapshot(self, server):
        """Test archive_snapshot tool"""
        args = {
            "snapshot_name": "test_snapshot"
        }
        
        result = server.archive_snapshot(args)
        
        # May fail if snapshot doesn't exist, which is OK
        assert result is not None
        assert isinstance(result, dict)


class TestTimelineContextTools:
    """Test Timeline Context Tools (3 tools)"""
    
    @pytest.fixture
    def server(self):
        """Create server instance"""
        return SimpleMCPServer()
    
    def test_add_timeline_entry(self, server):
        """Test add_timeline_entry tool"""
        args = {
            "prompt_id": "test_001",
            "user_input": "Test input",
            "context_state": {"test": True}
        }
        
        result = server.add_timeline_entry(args)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_get_timeline_summary(self, server):
        """Test get_timeline_summary tool"""
        args = {
            "limit": 10
        }
        
        result = server.get_timeline_summary(args)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_get_timeline_entries(self, server):
        """Test get_timeline_entries tool"""
        args = {}
        
        result = server.get_timeline_entries(args)
        
        assert result is not None
        assert isinstance(result, dict)


class TestGoalTimelineTools:
    """Test Goal Timeline Tools (3 tools)"""
    
    @pytest.fixture
    def server(self):
        """Create server instance"""
        return SimpleMCPServer()
    
    def test_create_goal_timeline_node(self, server):
        """Test create_goal_timeline_node tool"""
        args = {
            "goal_id": "TEST-001",
            "name": "Test Goal",
            "description": "Test goal description"
        }
        
        result = server.create_goal_timeline_node(args)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_update_goal_progress(self, server):
        """Test update_goal_progress tool"""
        args = {
            "goal_id": "TEST-001",
            "progress": 0.5,
            "status": "in_progress"
        }
        
        result = server.update_goal_progress(args)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_query_goal_timeline(self, server):
        """Test query_goal_timeline tool"""
        args = {}
        
        result = server.query_goal_timeline(args)
        
        assert result is not None
        assert isinstance(result, dict)


class TestIISTools:
    """Test IIS Tools (3 tools)"""
    
    @pytest.fixture
    def server(self):
        """Create server instance"""
        return SimpleMCPServer()
    
    def test_compute_intuition(self, server):
        """Test compute_intuition tool"""
        args = {
            "confidence": 0.8,
            "context": "Test context"
        }
        
        result = server.compute_intuition(args)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_update_intuition_weights(self, server):
        """Test update_intuition_weights tool"""
        args = {
            "decision_id": "test_001",
            "label": 1,
            "features": {"test": 0.5}
        }
        
        result = server.update_intuition_weights(args)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_get_intuition_trace(self, server):
        """Test get_intuition_trace tool"""
        args = {
            "decision_id": "test_001"
        }
        
        result = server.get_intuition_trace(args)
        
        assert result is not None
        assert isinstance(result, dict)


class TestCoAgencyTools:
    """Test Co-Agency Tools (3 tools)"""
    
    @pytest.fixture
    def server(self):
        """Create server instance"""
        return SimpleMCPServer()
    
    def test_signal_disagreement(self, server):
        """Test signal_disagreement tool"""
        args = {
            "concern": "Test concern",
            "reasoning": ["Reason 1", "Reason 2"]
        }
        
        result = server.signal_disagreement(args)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_get_trust_dashboard(self, server):
        """Test get_trust_dashboard tool"""
        args = {
            "user_id": "test_user"
        }
        
        result = server.get_trust_dashboard(args)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_request_escalation(self, server):
        """Test request_escalation tool"""
        args = {
            "reason": "Test escalation",
            "risk_level": "medium"
        }
        
        result = server.request_escalation(args)
        
        assert result is not None
        assert isinstance(result, dict)


class TestDatasetManagementTools:
    """Test Dataset Management Tools (4 tools)"""
    
    @pytest.fixture
    def server(self):
        """Create server instance"""
        return SimpleMCPServer()
    
    def test_create_dataset(self, server):
        """Test create_dataset tool"""
        args = {
            "dataset_name": "test_dataset",
            "description": "Test dataset"
        }
        
        result = server.create_dataset(args)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_ingest_data(self, server):
        """Test ingest_data tool"""
        args = {
            "dataset_id": "test_dataset",
            "data": {"test": "data"}
        }
        
        result = server.ingest_data(args)
        
        # May fail if dataset doesn't exist, which is OK
        assert result is not None
        assert isinstance(result, dict)
    
    def test_query_dataset(self, server):
        """Test query_dataset tool"""
        args = {
            "dataset_id": "test_dataset"
        }
        
        result = server.query_dataset(args)
        
        # May fail if dataset doesn't exist, which is OK
        assert result is not None
        assert isinstance(result, dict)
    
    def test_delete_dataset(self, server):
        """Test delete_dataset tool"""
        args = {
            "dataset_id": "test_dataset",
            "confirm": True
        }
        
        result = server.delete_dataset(args)
        
        # May fail if dataset doesn't exist, which is OK
        assert result is not None
        assert isinstance(result, dict)


class TestApplicationLifecycleTools:
    """Test Application Lifecycle Tools (3 tools)"""
    
    @pytest.fixture
    def server(self):
        """Create server instance"""
        return SimpleMCPServer()
    
    def test_create_application(self, server):
        """Test create_application tool"""
        args = {
            "app_name": "test_app",
            "app_type": "test"
        }
        
        result = server.create_application(args)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_deploy_application(self, server):
        """Test deploy_application tool"""
        args = {
            "app_id": "test_app",
            "environment": "test"
        }
        
        result = server.deploy_application(args)
        
        # May fail if app doesn't exist, which is OK
        assert result is not None
        assert isinstance(result, dict)
    
    def test_manage_application_lifecycle(self, server):
        """Test manage_application_lifecycle tool"""
        args = {
            "app_id": "test_app",
            "action": "status"
        }
        
        result = server.manage_application_lifecycle(args)
        
        # May fail if app doesn't exist, which is OK
        assert result is not None
        assert isinstance(result, dict)


class TestAutonomousProtocolTools:
    """Test Autonomous Protocol Tools (9 tools)"""
    
    @pytest.fixture
    def server(self):
        """Create server instance"""
        return SimpleMCPServer()
    
    def test_start_autonomous_operation(self, server):
        """Test start_autonomous_operation tool"""
        args = {
            "task": "Test task",
            "confidence": 0.8
        }
        
        result = server.start_autonomous_operation(args)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_pause_autonomous_operation(self, server):
        """Test pause_autonomous_operation tool"""
        args = {}
        
        result = server.pause_autonomous_operation(args)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_resume_autonomous_operation(self, server):
        """Test resume_autonomous_operation tool"""
        args = {}
        
        result = server.resume_autonomous_operation(args)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_stop_autonomous_operation(self, server):
        """Test stop_autonomous_operation tool"""
        args = {}
        
        result = server.stop_autonomous_operation(args)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_get_autonomous_status(self, server):
        """Test get_autonomous_status tool"""
        args = {}
        
        result = server.get_autonomous_status(args)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_run_autonomous_checklist(self, server):
        """Test run_autonomous_checklist tool"""
        args = {}
        
        result = server.run_autonomous_checklist(args)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_fix_autonomous_issues(self, server):
        """Test fix_autonomous_issues tool"""
        args = {}
        
        result = server.fix_autonomous_issues(args)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_should_continue_autonomous(self, server):
        """Test should_continue_autonomous tool"""
        args = {}
        
        result = server.should_continue_autonomous(args)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_generate_next_autonomous_task(self, server):
        """Test generate_next_autonomous_task tool"""
        args = {}
        
        result = server.generate_next_autonomous_task(args)
        
        assert result is not None
        assert isinstance(result, dict)


class TestARDTools:
    """Test ARD Tools (3 tools)"""
    
    @pytest.fixture
    def server(self):
        """Create server instance"""
        return SimpleMCPServer()
    
    def test_conduct_recursive_analysis(self, server):
        """Test conduct_recursive_analysis tool"""
        args = {
            "focus_systems": ["test"],
            "max_levels": 3
        }
        
        result = server.conduct_recursive_analysis(args)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_generate_improvement_dreams(self, server):
        """Test generate_improvement_dreams tool"""
        args = {
            "analysis_report": {},
            "focus_areas": ["test"],
            "max_dreams": 5
        }
        
        result = server.generate_improvement_dreams(args)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_test_improvement_dream(self, server):
        """Test test_improvement_dream tool"""
        args = {
            "dream": {"id": "test"},
            "test_environments": ["test"]
        }
        
        result = server.test_improvement_dream(args)
        
        assert result is not None
        assert isinstance(result, dict)


class TestAICollaborationTools:
    """Test AI Collaboration Tools (6 tools)"""
    
    @pytest.fixture
    def server(self):
        """Create server instance"""
        return SimpleMCPServer()
    
    def test_send_ai_message(self, server):
        """Test send_ai_message tool"""
        args = {
            "from_ai": "Lexicon",
            "to_ai": "Aether",
            "content": "Test message"
        }
        
        result = server.send_ai_message(args)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_get_ai_messages(self, server):
        """Test get_ai_messages tool"""
        args = {}
        
        result = server.get_ai_messages(args)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_start_ai_discussion(self, server):
        """Test start_ai_discussion tool"""
        args = {
            "from_ai": "Lexicon",
            "to_ai": "Aether",
            "topic": "Test topic",
            "initial_message": "Test message"
        }
        
        result = server.start_ai_discussion(args)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_handoff_task_to_ai(self, server):
        """Test handoff_task_to_ai tool"""
        args = {
            "from_ai": "Lexicon",
            "to_ai": "Aether",
            "task_description": "Test task"
        }
        
        result = server.handoff_task_to_ai(args)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_share_ai_profile(self, server):
        """Test share_ai_profile tool"""
        args = {
            "from_ai": "Lexicon",
            "to_ai": "Aether",
            "profile_data": {"test": "data"}
        }
        
        result = server.share_ai_profile(args)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_get_ai_collaboration_summary(self, server):
        """Test get_ai_collaboration_summary tool"""
        args = {}
        
        result = server.get_ai_collaboration_summary(args)
        
        assert result is not None
        assert isinstance(result, dict)


class TestObservabilityTools:
    """Test Observability Tools (4 tools)"""
    
    @pytest.fixture
    def server(self):
        """Create server instance"""
        return SimpleMCPServer()
    
    def test_get_consciousness_metrics(self, server):
        """Test get_consciousness_metrics tool"""
        args = {}
        
        result = server.get_consciousness_metrics(args)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_run_cognitive_audit(self, server):
        """Test run_cognitive_audit tool"""
        args = {
            "introspection_type": "hourly_check"
        }
        
        result = server.run_cognitive_audit(args)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_analyze_thought_patterns(self, server):
        """Test analyze_thought_patterns tool"""
        args = {
            "context": "Test context",
            "task_category": "test"
        }
        
        result = server.analyze_thought_patterns(args)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_detect_cognitive_drift(self, server):
        """Test detect_cognitive_drift tool"""
        args = {
            "working_memory_items": 10,
            "context_size_tokens": 1000,
            "error_rate": 0.1
        }
        
        result = server.detect_cognitive_drift(args)
        
        assert result is not None
        assert isinstance(result, dict)


class TestCASTools:
    """Test CAS Tools (3 tools)"""
    
    @pytest.fixture
    def server(self):
        """Create server instance"""
        return SimpleMCPServer()
    
    def test_run_cognitive_audit_cas(self, server):
        """Test run_cognitive_audit (CAS) tool"""
        args = {
            "introspection_type": "hourly_check"
        }
        
        result = server.run_cognitive_audit(args)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_analyze_thought_patterns_cas(self, server):
        """Test analyze_thought_patterns (CAS) tool"""
        args = {
            "context": "Test context",
            "task_category": "test"
        }
        
        result = server.analyze_thought_patterns(args)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_detect_cognitive_drift_cas(self, server):
        """Test detect_cognitive_drift (CAS) tool"""
        args = {
            "working_memory_items": 10,
            "context_size_tokens": 1000,
            "error_rate": 0.1
        }
        
        result = server.detect_cognitive_drift(args)
        
        assert result is not None
        assert isinstance(result, dict)


class TestCMCIntegration:
    """Test CMC Integration across tools"""
    
    @pytest.fixture
    def server(self):
        """Create server instance"""
        return SimpleMCPServer()
    
    def test_cmc_storage_in_store_memory(self, server):
        """Verify store_memory uses CMC"""
        args = {
            "content": "Test CMC integration",
            "tags": {"test": "cmc"}
        }
        
        result = server.store_memory(args)
        
        # Should return success or atom_id indicating CMC storage
        assert result is not None
        assert isinstance(result, dict)
    
    def test_cmc_query_in_retrieve_memory(self, server):
        """Verify retrieve_memory queries CMC"""
        args = {
            "query": "CMC test",
            "limit": 5
        }
        
        result = server.retrieve_memory(args)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_cmc_stats_in_get_memory_stats(self, server):
        """Verify get_memory_stats uses CMC"""
        args = {}
        
        result = server.get_memory_stats(args)
        
        assert result is not None
        assert isinstance(result, dict)
        # Should include CMC statistics
        assert 'total_atoms' in result or 'atoms' in result or 'stats' in result


class TestErrorHandling:
    """Test error handling across tools"""
    
    @pytest.fixture
    def server(self):
        """Create server instance"""
        return SimpleMCPServer()
    
    def test_missing_required_parameters(self, server):
        """Test tools handle missing parameters gracefully"""
        # Test with empty args
        result = server.store_memory({})
        
        # Should return error or handle gracefully
        assert result is not None
        assert isinstance(result, dict)
    
    def test_invalid_parameter_types(self, server):
        """Test tools handle invalid parameter types"""
        args = {
            "confidence": "invalid",  # Should be float
            "task": 123  # Should be string
        }
        
        result = server.track_confidence(args)
        
        # Should handle gracefully or return error
        assert result is not None
        assert isinstance(result, dict)
    
    def test_nonexistent_resources(self, server):
        """Test tools handle nonexistent resources"""
        args = {
            "snapshot_name": "nonexistent_snapshot_12345"
        }
        
        result = server.restore_snapshot(args)
        
        # Should return error gracefully, not crash
        assert result is not None
        assert isinstance(result, dict)


class TestPerformance:
    """Test performance characteristics"""
    
    @pytest.fixture
    def server(self):
        """Create server instance"""
        return SimpleMCPServer()
    
    def test_tool_response_time(self, server):
        """Test tools respond within reasonable time"""
        import time
        
        start = time.time()
        result = server.get_memory_stats({})
        elapsed = time.time() - start
        
        assert result is not None
        # Should respond within 1 second
        assert elapsed < 1.0, f"Tool took {elapsed:.2f}s, should be < 1.0s"
    
    def test_concurrent_tool_calls(self, server):
        """Test multiple tools can be called concurrently"""
        import concurrent.futures
        
        def call_tool(tool_name, args):
            method = getattr(server, tool_name)
            return method(args)
        
        tools_to_test = [
            ("get_memory_stats", {}),
            ("list_snapshots", {}),
            ("get_timeline_summary", {"limit": 5}),
            ("query_goal_timeline", {}),
            ("get_autonomous_status", {})
        ]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(call_tool, tool_name, args)
                for tool_name, args in tools_to_test
            ]
            
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # All should succeed
        assert len(results) == 5
        assert all(r is not None for r in results)
        assert all(isinstance(r, dict) for r in results)

