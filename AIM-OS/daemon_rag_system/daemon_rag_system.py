#!/usr/bin/env python3
"""
Daemon/RAG System - Main integration system
Part of Daemon/RAG System Implementation

Following A-H Protocol and DEL methodology from ChatGPT journal
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import time
import json
import threading
import queue
from collections import defaultdict

# Import all subsystems
from tool_registry.tool_registry import ToolRegistry, ToolCategory
from context_analysis_engine.context_analyzer import ContextAnalysisEngine, ContextType, ComplexityLevel
from tool_selection_engine.tool_selector import ToolSelectionEngine, SelectionStrategy
from rag_system.rag_engine import RAGSystem, PatternType
from server_manager.server_manager import ServerManager
from performance_monitor.performance_monitor import PerformanceMonitor
from learning_system.learning_system import LearningSystem
from resource_manager.resource_manager import ResourceManager

class DaemonStatus(Enum):
    """Daemon status."""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"

@dataclass
class DaemonConfig:
    """Daemon configuration."""
    max_tools: int = 40
    context_analysis_timeout_ms: int = 100
    tool_selection_timeout_ms: int = 50
    server_management_timeout_ms: int = 200
    learning_enabled: bool = True
    performance_monitoring_enabled: bool = True
    resource_optimization_enabled: bool = True
    log_level: str = "INFO"

@dataclass
class DaemonMetrics:
    """Daemon performance metrics."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time_ms: float = 0.0
    context_analysis_time_ms: float = 0.0
    tool_selection_time_ms: float = 0.0
    server_management_time_ms: float = 0.0
    learning_time_ms: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0

class DaemonRAGSystem:
    """
    Main daemon/RAG system integrating all components.
    
    SpecBlock:
    - responsibility: "Orchestrate intelligent MCP tool selection and server management"
    - must_never: "Exceed 40-tool limit", "Make selections without considering context"
    - performance_budget: "200ms average, 400ms maximum"
    - security_level: "critical"
    """
    
    def __init__(self, config: DaemonConfig = None):
        self.config = config or DaemonConfig()
        self.status = DaemonStatus.STOPPED
        self.metrics = DaemonMetrics()
        
        # Initialize subsystems
        self.tool_registry = ToolRegistry()
        self.context_analyzer = ContextAnalysisEngine()
        self.tool_selector = ToolSelectionEngine(self.tool_registry)
        self.rag_system = RAGSystem(self.tool_registry)
        self.server_manager = ServerManager()
        self.performance_monitor = PerformanceMonitor()
        self.learning_system = LearningSystem(self.rag_system)
        self.resource_manager = ResourceManager()
        
        # Request queue for processing
        self.request_queue = queue.Queue()
        self.response_queue = queue.Queue()
        
        # Processing thread
        self.processing_thread = None
        self.running = False
    
    def start(self) -> bool:
        """Start the daemon system."""
        try:
            self.status = DaemonStatus.STARTING
            
            # Start processing thread
            self.running = True
            self.processing_thread = threading.Thread(target=self._processing_loop, daemon=True)
            self.processing_thread.start()
            
            # Start performance monitoring
            if self.config.performance_monitoring_enabled:
                self.performance_monitor.start()
            
            self.status = DaemonStatus.RUNNING
            return True
            
        except Exception as e:
            print(f"Error starting daemon: {e}")
            self.status = DaemonStatus.ERROR
            return False
    
    def stop(self) -> bool:
        """Stop the daemon system."""
        try:
            self.status = DaemonStatus.STOPPING
            
            # Stop processing
            self.running = False
            if self.processing_thread:
                self.processing_thread.join(timeout=5)
            
            # Stop performance monitoring
            if self.config.performance_monitoring_enabled:
                self.performance_monitor.stop()
            
            # Shutdown all servers
            self.server_manager.shutdown_all_servers()
            
            self.status = DaemonStatus.STOPPED
            return True
            
        except Exception as e:
            print(f"Error stopping daemon: {e}")
            self.status = DaemonStatus.ERROR
            return False
    
    def process_request(self, user_input: str, environment: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a user request and return tool selection."""
        start_time = time.time()
        
        try:
            self.metrics.total_requests += 1
            
            # Set default environment
            if environment is None:
                environment = {}
            
            # Step 1: Context Analysis
            context_start = time.time()
            context_profile = self.context_analyzer.analyze_context(user_input, environment)
            context_time = (time.time() - context_start) * 1000
            self.metrics.context_analysis_time_ms = context_time
            
            # Step 2: Tool Selection
            selection_start = time.time()
            selection_result = self.tool_selector.select_tools(
                context_profile=context_profile,
                strategy=SelectionStrategy.BALANCED
            )
            selection_time = (time.time() - selection_start) * 1000
            self.metrics.tool_selection_time_ms = selection_time
            
            # Step 3: Server Management
            server_start = time.time()
            server_results = self._manage_servers(selection_result.selected_tools)
            server_time = (time.time() - server_start) * 1000
            self.metrics.server_management_time_ms = server_time
            
            # Step 4: Learning (if enabled)
            learning_time = 0.0
            if self.config.learning_enabled:
                learning_start = time.time()
                self._learn_from_selection(context_profile, selection_result.selected_tools)
                learning_time = (time.time() - learning_start) * 1000
                self.metrics.learning_time_ms = learning_time
            
            # Calculate total response time
            total_time = (time.time() - start_time) * 1000
            self.metrics.average_response_time_ms = (
                (self.metrics.average_response_time_ms * (self.metrics.total_requests - 1) + total_time) / 
                self.metrics.total_requests
            )
            
            # Update success metrics
            if selection_result.selected_tools:
                self.metrics.successful_requests += 1
            else:
                self.metrics.failed_requests += 1
            
            # Prepare response
            response = {
                'success': len(selection_result.selected_tools) > 0,
                'selected_tools': selection_result.selected_tools,
                'context_profile': {
                    'context_type': context_profile.context_type.value,
                    'complexity': context_profile.complexity.value,
                    'task_classification': context_profile.task_classification,
                    'intent_inference': context_profile.intent_inference,
                    'confidence_score': context_profile.confidence_score
                },
                'selection_result': {
                    'total_score': selection_result.total_score,
                    'capability_coverage': selection_result.capability_coverage,
                    'performance_estimate': selection_result.performance_estimate,
                    'strategy_used': selection_result.strategy_used.value,
                    'reasoning': selection_result.reasoning
                },
                'server_management': server_results,
                'performance_metrics': {
                    'total_time_ms': total_time,
                    'context_analysis_time_ms': context_time,
                    'tool_selection_time_ms': selection_time,
                    'server_management_time_ms': server_time,
                    'learning_time_ms': learning_time
                },
                'daemon_metrics': {
                    'total_requests': self.metrics.total_requests,
                    'successful_requests': self.metrics.successful_requests,
                    'failed_requests': self.metrics.failed_requests,
                    'average_response_time_ms': self.metrics.average_response_time_ms
                }
            }
            
            return response
            
        except Exception as e:
            self.metrics.failed_requests += 1
            return {
                'success': False,
                'error': str(e),
                'selected_tools': [],
                'performance_metrics': {
                    'total_time_ms': (time.time() - start_time) * 1000
                }
            }
    
    def _manage_servers(self, selected_tools: List[str]) -> Dict[str, Any]:
        """Manage servers based on selected tools."""
        try:
            # Determine which servers are needed for selected tools
            required_servers = self._determine_required_servers(selected_tools)
            
            # Get currently running servers
            current_status = self.server_manager.get_server_status()
            running_servers = list(current_status['servers'].keys())
            
            # Determine servers to start/stop
            servers_to_start = [s for s in required_servers if s not in running_servers]
            servers_to_stop = [s for s in running_servers if s not in required_servers]
            
            # Start required servers
            start_results = {}
            if servers_to_start:
                start_results = self.server_manager.load_servers(servers_to_start)
            
            # Stop unnecessary servers
            stop_results = {}
            if servers_to_stop:
                stop_results = self.server_manager.unload_servers(servers_to_stop)
            
            return {
                'required_servers': required_servers,
                'servers_to_start': servers_to_start,
                'servers_to_stop': servers_to_stop,
                'start_results': start_results,
                'stop_results': stop_results,
                'current_status': current_status
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'required_servers': [],
                'servers_to_start': [],
                'servers_to_stop': [],
                'start_results': {},
                'stop_results': {}
            }
    
    def _determine_required_servers(self, selected_tools: List[str]) -> List[str]:
        """Determine which servers are required for selected tools."""
        required_servers = []
        
        # Map tools to servers
        tool_to_server = {
            'mcp_lucid-mcp_store_memory': 'core_aimos_server',
            'mcp_lucid-mcp_retrieve_memory': 'core_aimos_server',
            'mcp_lucid-mcp_get_memory_stats': 'core_aimos_server',
            'mcp_lucid-mcp_create_plan': 'core_aimos_server',
            'mcp_lucid-mcp_track_confidence': 'core_aimos_server',
            'mcp_lucid-mcp_synthesize_knowledge': 'core_aimos_server',
            'mcp_lucid-mcp_check_invariant': 'scor_server',
            'mcp_lucid-mcp_run_baseline_probe': 'scor_server',
            'mcp_lucid-mcp_detect_manipulation_signals': 'scor_server',
            'mcp_lucid-mcp_create_snapshot': 'snapshot_server',
            'mcp_lucid-mcp_restore_snapshot': 'snapshot_server',
            'mcp_lucid-mcp_list_snapshots': 'snapshot_server',
            'mcp_lucid-mcp_archive_snapshot': 'snapshot_server',
            'mcp_lucid-mcp_add_timeline_entry': 'timeline_server',
            'mcp_lucid-mcp_get_timeline_summary': 'timeline_server',
            'mcp_lucid-mcp_get_timeline_entries': 'timeline_server',
            'mcp_lucid-mcp_create_goal_timeline_node': 'goal_timeline_server',
            'mcp_lucid-mcp_update_goal_progress': 'goal_timeline_server',
            'mcp_lucid-mcp_query_goal_timeline': 'goal_timeline_server',
            'mcp_lucid-mcp_compute_intuition': 'iis_server',
            'mcp_lucid-mcp_update_intuition_weights': 'iis_server',
            'mcp_lucid-mcp_get_intuition_trace': 'iis_server',
            'mcp_lucid-mcp_signal_disagreement': 'co_agency_server',
            'mcp_lucid-mcp_get_trust_dashboard': 'co_agency_server',
            'mcp_lucid-mcp_request_escalation': 'co_agency_server',
            'mcp_lucid-mcp_create_dataset': 'dataset_server',
            'mcp_lucid-mcp_ingest_data': 'dataset_server',
            'mcp_lucid-mcp_query_dataset': 'dataset_server',
            'mcp_lucid-mcp_delete_dataset': 'dataset_server',
            'mcp_lucid-mcp_create_application': 'application_server',
            'mcp_lucid-mcp_deploy_application': 'application_server',
            'mcp_lucid-mcp_manage_application_lifecycle': 'application_server',
            'mcp_lucid-mcp_start_autonomous_operation': 'autonomous_server',
            'mcp_lucid-mcp_pause_autonomous_operation': 'autonomous_server',
            'mcp_lucid-mcp_resume_autonomous_operation': 'autonomous_server',
            'mcp_lucid-mcp_stop_autonomous_operation': 'autonomous_server',
            'mcp_lucid-mcp_get_autonomous_status': 'autonomous_server',
            'mcp_lucid-mcp_run_autonomous_checklist': 'autonomous_server',
            'mcp_lucid-mcp_fix_autonomous_issues': 'autonomous_server',
            'mcp_lucid-mcp_should_continue_autonomous': 'autonomous_server',
            'mcp_lucid-mcp_generate_next_autonomous_task': 'autonomous_server',
            'mcp_lucid-mcp_conduct_recursive_analysis': 'ard_server',
            'mcp_lucid-mcp_generate_improvement_dreams': 'ard_server',
            'mcp_lucid-mcp_test_improvement_dream': 'ard_server',
            'mcp_lucid-mcp_send_ai_message': 'ai_collaboration_server',
            'mcp_lucid-mcp_get_ai_messages': 'ai_collaboration_server',
            'mcp_lucid-mcp_start_ai_discussion': 'ai_collaboration_server',
            'mcp_lucid-mcp_handoff_task_to_ai': 'ai_collaboration_server',
            'mcp_lucid-mcp_share_ai_profile': 'ai_collaboration_server',
            'mcp_lucid-mcp_get_ai_collaboration_summary': 'ai_collaboration_server',
            'mcp_lucid-mcp_get_consciousness_metrics': 'observability_server',
            'mcp_lucid-mcp_get_autonomous_status': 'observability_server',
            'mcp_lucid-mcp_get_trust_dashboard': 'observability_server',
            'mcp_lucid-mcp_get_memory_stats': 'observability_server'
        }
        
        # Find required servers
        for tool_id in selected_tools:
            server_id = tool_to_server.get(tool_id)
            if server_id and server_id not in required_servers:
                required_servers.append(server_id)
        
        return required_servers
    
    def _learn_from_selection(self, context_profile, selected_tools: List[str]) -> None:
        """Learn from tool selection for future improvements."""
        try:
            # Create outcome data
            outcome = {
                'success': len(selected_tools) > 0,
                'timestamp': time.time(),
                'context_type': context_profile.context_type.value,
                'task_classification': context_profile.task_classification,
                'intent_inference': context_profile.intent_inference,
                'complexity': context_profile.complexity.value,
                'selected_tools_count': len(selected_tools),
                'performance_metrics': {
                    'context_analysis_time_ms': self.metrics.context_analysis_time_ms,
                    'tool_selection_time_ms': self.metrics.tool_selection_time_ms,
                    'server_management_time_ms': self.metrics.server_management_time_ms
                }
            }
            
            # Learn from outcome
            self.rag_system.learn_from_outcome(context_profile, selected_tools, outcome)
            
        except Exception as e:
            print(f"Error in learning: {e}")
    
    def _processing_loop(self) -> None:
        """Main processing loop."""
        while self.running:
            try:
                # Process requests from queue
                if not self.request_queue.empty():
                    request = self.request_queue.get(timeout=1)
                    response = self.process_request(request['user_input'], request.get('environment'))
                    self.response_queue.put(response)
                
                time.sleep(0.1)  # Small delay to prevent busy waiting
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error in processing loop: {e}")
                time.sleep(1)
    
    def get_status(self) -> Dict[str, Any]:
        """Get daemon status and metrics."""
        return {
            'status': self.status.value,
            'metrics': {
                'total_requests': self.metrics.total_requests,
                'successful_requests': self.metrics.successful_requests,
                'failed_requests': self.metrics.failed_requests,
                'success_rate': self.metrics.successful_requests / max(1, self.metrics.total_requests),
                'average_response_time_ms': self.metrics.average_response_time_ms,
                'context_analysis_time_ms': self.metrics.context_analysis_time_ms,
                'tool_selection_time_ms': self.metrics.tool_selection_time_ms,
                'server_management_time_ms': self.metrics.server_management_time_ms,
                'learning_time_ms': self.metrics.learning_time_ms
            },
            'server_status': self.server_manager.get_server_status(),
            'resource_usage': self.resource_manager.get_resource_usage(),
            'configuration': {
                'max_tools': self.config.max_tools,
                'learning_enabled': self.config.learning_enabled,
                'performance_monitoring_enabled': self.config.performance_monitoring_enabled,
                'resource_optimization_enabled': self.config.resource_optimization_enabled
            }
        }
    
    def get_rag_statistics(self) -> Dict[str, Any]:
        """Get RAG system statistics."""
        return self.rag_system.get_pattern_statistics()
    
    def export_configuration(self, filepath: str) -> None:
        """Export daemon configuration to file."""
        config_data = {
            'daemon_config': {
                'max_tools': self.config.max_tools,
                'context_analysis_timeout_ms': self.config.context_analysis_timeout_ms,
                'tool_selection_timeout_ms': self.config.tool_selection_timeout_ms,
                'server_management_timeout_ms': self.config.server_management_timeout_ms,
                'learning_enabled': self.config.learning_enabled,
                'performance_monitoring_enabled': self.config.performance_monitoring_enabled,
                'resource_optimization_enabled': self.config.resource_optimization_enabled,
                'log_level': self.config.log_level
            },
            'tool_registry': {
                'total_tools': self.tool_registry.get_tool_count(),
                'tools_by_category': {
                    category.value: len(self.tool_registry.get_tools_by_category(category))
                    for category in ToolCategory
                }
            },
            'server_registry': {
                'total_servers': len(self.server_manager.registry.get_all_servers()),
                'total_tool_capacity': self.server_manager.registry.get_total_tool_count()
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(config_data, f, indent=2)

if __name__ == "__main__":
    # Test the daemon/RAG system
    config = DaemonConfig(
        max_tools=40,
        learning_enabled=True,
        performance_monitoring_enabled=True,
        resource_optimization_enabled=True
    )
    
    daemon = DaemonRAGSystem(config)
    
    # Start daemon
    if daemon.start():
        print("Daemon started successfully")
        
        # Test request processing
        test_input = "I need to store this important information in memory and create a plan for implementing the daemon system"
        test_environment = {
            'session_info': {'user_id': 'test_user', 'session_id': 'test_session'},
            'system_state': {'memory_available': 1000, 'cpu_available': 80},
            'constraints': ['40_tool_limit', 'performance_critical']
        }
        
        response = daemon.process_request(test_input, test_environment)
        print(f"Response: {json.dumps(response, indent=2)}")
        
        # Get status
        status = daemon.get_status()
        print(f"Status: {json.dumps(status, indent=2)}")
        
        # Get RAG statistics
        rag_stats = daemon.get_rag_statistics()
        print(f"RAG Statistics: {json.dumps(rag_stats, indent=2)}")
        
        # Export configuration
        daemon.export_configuration("daemon_config.json")
        print("Configuration exported to daemon_config.json")
        
        # Stop daemon
        daemon.stop()
        print("Daemon stopped")
    else:
        print("Failed to start daemon")
