#!/usr/bin/env python3
"""
Server Manager - Manage MCP server loading/unloading and resource allocation
Part of Daemon/RAG System Implementation

Following A-H Protocol and DEL methodology from ChatGPT journal
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import time
import json
import subprocess
import threading
import queue
import psutil
import os
from collections import defaultdict

class ServerStatus(Enum):
    """MCP server status."""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"
    UNKNOWN = "unknown"

class ServerPriority(Enum):
    """Server priority levels."""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4

@dataclass
class ServerDefinition:
    """MCP server definition."""
    server_id: str
    name: str
    script_path: str
    config_path: str
    tool_count: int
    priority: ServerPriority
    dependencies: List[str]
    resource_requirements: Dict[str, Any]
    startup_time_ms: int
    shutdown_time_ms: int
    health_check_interval_ms: int
    max_retries: int = 3

@dataclass
class ServerInstance:
    """Running server instance."""
    server_id: str
    process: Optional[subprocess.Popen]
    status: ServerStatus
    start_time: float
    last_health_check: float
    retry_count: int
    error_message: Optional[str] = None
    resource_usage: Dict[str, float] = None

@dataclass
class ResourceAllocation:
    """Resource allocation for servers."""
    memory_mb: float
    cpu_percent: float
    file_descriptors: int
    network_connections: int
    disk_io_mb_per_sec: float

class ServerRegistry:
    """
    Registry of available MCP servers.
    
    SpecBlock:
    - responsibility: "Maintain registry of available MCP servers"
    - must_never: "Provide inaccurate server information", "Fail to update server metadata"
    - performance_budget: "5ms average, 10ms maximum"
    - security_level: "high"
    """
    
    def __init__(self):
        self.servers: Dict[str, ServerDefinition] = {}
        self._initialize_servers()
    
    def _initialize_servers(self) -> None:
        """Initialize available MCP servers."""
        # Core AIM-OS Server (6 tools)
        self._add_server(ServerDefinition(
            server_id="core_aimos_server",
            name="Core AIM-OS Server",
            script_path="lucid_mcp_server.py",
            config_path="test_mcp_configs/lucid_mcp_config.json",
            tool_count=6,
            priority=ServerPriority.CRITICAL,
            dependencies=[],
            resource_requirements={
                "memory_mb": 50,
                "cpu_percent": 10,
                "file_descriptors": 10
            },
            startup_time_ms=2000,
            shutdown_time_ms=1000,
            health_check_interval_ms=30000
        ))
        
        # SCOR Server (3 tools)
        self._add_server(ServerDefinition(
            server_id="scor_server",
            name="SCOR Server",
            script_path="lucid_mcp_server.py",
            config_path="test_mcp_configs/scor_mcp_config.json",
            tool_count=3,
            priority=ServerPriority.HIGH,
            dependencies=[],
            resource_requirements={
                "memory_mb": 30,
                "cpu_percent": 5,
                "file_descriptors": 5
            },
            startup_time_ms=1500,
            shutdown_time_ms=800,
            health_check_interval_ms=30000
        ))
        
        # Snapshot Server (4 tools)
        self._add_server(ServerDefinition(
            server_id="snapshot_server",
            name="Snapshot Server",
            script_path="lucid_mcp_server.py",
            config_path="test_mcp_configs/snapshot_mcp_config.json",
            tool_count=4,
            priority=ServerPriority.MEDIUM,
            dependencies=[],
            resource_requirements={
                "memory_mb": 40,
                "cpu_percent": 8,
                "file_descriptors": 8
            },
            startup_time_ms=1800,
            shutdown_time_ms=900,
            health_check_interval_ms=30000
        ))
        
        # Timeline Server (3 tools)
        self._add_server(ServerDefinition(
            server_id="timeline_server",
            name="Timeline Server",
            script_path="lucid_mcp_server.py",
            config_path="test_mcp_configs/timeline_mcp_config.json",
            tool_count=3,
            priority=ServerPriority.HIGH,
            dependencies=[],
            resource_requirements={
                "memory_mb": 35,
                "cpu_percent": 6,
                "file_descriptors": 6
            },
            startup_time_ms=1600,
            shutdown_time_ms=800,
            health_check_interval_ms=30000
        ))
        
        # Goal Timeline Server (3 tools)
        self._add_server(ServerDefinition(
            server_id="goal_timeline_server",
            name="Goal Timeline Server",
            script_path="lucid_mcp_server.py",
            config_path="test_mcp_configs/goal_timeline_mcp_config.json",
            tool_count=3,
            priority=ServerPriority.HIGH,
            dependencies=[],
            resource_requirements={
                "memory_mb": 35,
                "cpu_percent": 6,
                "file_descriptors": 6
            },
            startup_time_ms=1600,
            shutdown_time_ms=800,
            health_check_interval_ms=30000
        ))
        
        # IIS Server (3 tools)
        self._add_server(ServerDefinition(
            server_id="iis_server",
            name="IIS Server",
            script_path="lucid_mcp_server.py",
            config_path="test_mcp_configs/iis_mcp_config.json",
            tool_count=3,
            priority=ServerPriority.MEDIUM,
            dependencies=[],
            resource_requirements={
                "memory_mb": 30,
                "cpu_percent": 5,
                "file_descriptors": 5
            },
            startup_time_ms=1500,
            shutdown_time_ms=700,
            health_check_interval_ms=30000
        ))
        
        # Co-Agency Server (3 tools)
        self._add_server(ServerDefinition(
            server_id="co_agency_server",
            name="Co-Agency Server",
            script_path="lucid_mcp_server.py",
            config_path="test_mcp_configs/co_agency_mcp_config.json",
            tool_count=3,
            priority=ServerPriority.MEDIUM,
            dependencies=[],
            resource_requirements={
                "memory_mb": 30,
                "cpu_percent": 5,
                "file_descriptors": 5
            },
            startup_time_ms=1500,
            shutdown_time_ms=700,
            health_check_interval_ms=30000
        ))
        
        # Dataset Server (4 tools)
        self._add_server(ServerDefinition(
            server_id="dataset_server",
            name="Dataset Server",
            script_path="lucid_mcp_server.py",
            config_path="test_mcp_configs/dataset_mcp_config.json",
            tool_count=4,
            priority=ServerPriority.MEDIUM,
            dependencies=[],
            resource_requirements={
                "memory_mb": 40,
                "cpu_percent": 8,
                "file_descriptors": 8
            },
            startup_time_ms=1800,
            shutdown_time_ms=900,
            health_check_interval_ms=30000
        ))
        
        # Application Server (3 tools)
        self._add_server(ServerDefinition(
            server_id="application_server",
            name="Application Server",
            script_path="lucid_mcp_server.py",
            config_path="test_mcp_configs/application_mcp_config.json",
            tool_count=3,
            priority=ServerPriority.LOW,
            dependencies=[],
            resource_requirements={
                "memory_mb": 25,
                "cpu_percent": 4,
                "file_descriptors": 4
            },
            startup_time_ms=1200,
            shutdown_time_ms=600,
            health_check_interval_ms=30000
        ))
        
        # Autonomous Server (9 tools)
        self._add_server(ServerDefinition(
            server_id="autonomous_server",
            name="Autonomous Server",
            script_path="lucid_mcp_server.py",
            config_path="test_mcp_configs/autonomous_mcp_config.json",
            tool_count=9,
            priority=ServerPriority.HIGH,
            dependencies=[],
            resource_requirements={
                "memory_mb": 60,
                "cpu_percent": 12,
                "file_descriptors": 12
            },
            startup_time_ms=2500,
            shutdown_time_ms=1200,
            health_check_interval_ms=30000
        ))
        
        # ARD Server (3 tools)
        self._add_server(ServerDefinition(
            server_id="ard_server",
            name="ARD Server",
            script_path="lucid_mcp_server.py",
            config_path="test_mcp_configs/ard_mcp_config.json",
            tool_count=3,
            priority=ServerPriority.MEDIUM,
            dependencies=[],
            resource_requirements={
                "memory_mb": 30,
                "cpu_percent": 5,
                "file_descriptors": 5
            },
            startup_time_ms=1500,
            shutdown_time_ms=700,
            health_check_interval_ms=30000
        ))
        
        # AI Collaboration Server (6 tools)
        self._add_server(ServerDefinition(
            server_id="ai_collaboration_server",
            name="AI Collaboration Server",
            script_path="lucid_mcp_server.py",
            config_path="test_mcp_configs/ai_collaboration_mcp_config.json",
            tool_count=6,
            priority=ServerPriority.MEDIUM,
            dependencies=[],
            resource_requirements={
                "memory_mb": 50,
                "cpu_percent": 10,
                "file_descriptors": 10
            },
            startup_time_ms=2000,
            shutdown_time_ms=1000,
            health_check_interval_ms=30000
        ))
        
        # Observability Server (4 tools)
        self._add_server(ServerDefinition(
            server_id="observability_server",
            name="Observability Server",
            script_path="lucid_mcp_server.py",
            config_path="test_mcp_configs/observability_mcp_config.json",
            tool_count=4,
            priority=ServerPriority.MEDIUM,
            dependencies=[],
            resource_requirements={
                "memory_mb": 40,
                "cpu_percent": 8,
                "file_descriptors": 8
            },
            startup_time_ms=1800,
            shutdown_time_ms=900,
            health_check_interval_ms=30000
        ))
    
    def _add_server(self, server: ServerDefinition) -> None:
        """Add server to registry."""
        self.servers[server.server_id] = server
    
    def get_server(self, server_id: str) -> Optional[ServerDefinition]:
        """Get server by ID."""
        return self.servers.get(server_id)
    
    def get_servers_by_priority(self, priority: ServerPriority) -> List[ServerDefinition]:
        """Get servers by priority."""
        return [server for server in self.servers.values() if server.priority == priority]
    
    def get_all_servers(self) -> List[ServerDefinition]:
        """Get all servers."""
        return list(self.servers.values())
    
    def get_total_tool_count(self) -> int:
        """Get total tool count across all servers."""
        return sum(server.tool_count for server in self.servers.values())

class ProcessManager:
    """
    Manage MCP server processes.
    
    SpecBlock:
    - responsibility: "Manage MCP server processes"
    - must_never: "Start servers without proper validation", "Fail to handle server failures"
    - performance_budget: "100ms average, 200ms maximum"
    - security_level: "high"
    """
    
    def __init__(self):
        self.running_servers: Dict[str, ServerInstance] = {}
        self.process_queue = queue.Queue()
        self.health_check_thread = None
        self.running = False
    
    def start_server(self, server_def: ServerDefinition) -> bool:
        """Start a server process."""
        try:
            # Check if server is already running
            if server_def.server_id in self.running_servers:
                return True
            
            # Start server process
            process = subprocess.Popen(
                ["python", server_def.script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.path.dirname(os.path.abspath(server_def.script_path))
            )
            
            # Create server instance
            server_instance = ServerInstance(
                server_id=server_def.server_id,
                process=process,
                status=ServerStatus.STARTING,
                start_time=time.time(),
                last_health_check=time.time(),
                retry_count=0
            )
            
            # Add to running servers
            self.running_servers[server_def.server_id] = server_instance
            
            # Start health check if not running
            if not self.running:
                self.start_health_check()
            
            return True
            
        except Exception as e:
            print(f"Error starting server {server_def.server_id}: {e}")
            return False
    
    def stop_server(self, server_id: str) -> bool:
        """Stop a server process."""
        try:
            if server_id not in self.running_servers:
                return True
            
            server_instance = self.running_servers[server_id]
            
            if server_instance.process:
                # Graceful shutdown
                server_instance.status = ServerStatus.STOPPING
                server_instance.process.terminate()
                
                # Wait for graceful shutdown
                try:
                    server_instance.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if graceful shutdown fails
                    server_instance.process.kill()
                    server_instance.process.wait()
            
            # Remove from running servers
            del self.running_servers[server_id]
            
            return True
            
        except Exception as e:
            print(f"Error stopping server {server_id}: {e}")
            return False
    
    def get_server_status(self, server_id: str) -> ServerStatus:
        """Get server status."""
        if server_id not in self.running_servers:
            return ServerStatus.STOPPED
        
        server_instance = self.running_servers[server_id]
        return server_instance.status
    
    def is_server_running(self, server_id: str) -> bool:
        """Check if server is running."""
        if server_id not in self.running_servers:
            return False
        
        server_instance = self.running_servers[server_id]
        if not server_instance.process:
            return False
        
        return server_instance.process.poll() is None
    
    def start_health_check(self) -> None:
        """Start health check thread."""
        if self.health_check_thread and self.health_check_thread.is_alive():
            return
        
        self.running = True
        self.health_check_thread = threading.Thread(target=self._health_check_loop, daemon=True)
        self.health_check_thread.start()
    
    def stop_health_check(self) -> None:
        """Stop health check thread."""
        self.running = False
        if self.health_check_thread:
            self.health_check_thread.join(timeout=5)
    
    def _health_check_loop(self) -> None:
        """Health check loop."""
        while self.running:
            try:
                for server_id, server_instance in list(self.running_servers.items()):
                    self._check_server_health(server_id, server_instance)
                
                time.sleep(1)  # Check every second
            except Exception as e:
                print(f"Error in health check loop: {e}")
                time.sleep(5)
    
    def _check_server_health(self, server_id: str, server_instance: ServerInstance) -> None:
        """Check health of a specific server."""
        try:
            if not server_instance.process:
                server_instance.status = ServerStatus.ERROR
                return
            
            # Check if process is still running
            if server_instance.process.poll() is not None:
                server_instance.status = ServerStatus.ERROR
                server_instance.error_message = "Process terminated unexpectedly"
                return
            
            # Update resource usage
            try:
                process = psutil.Process(server_instance.process.pid)
                server_instance.resource_usage = {
                    'memory_mb': process.memory_info().rss / (1024 * 1024),
                    'cpu_percent': process.cpu_percent(),
                    'file_descriptors': process.num_fds() if hasattr(process, 'num_fds') else 0
                }
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
            
            # Update status
            server_instance.status = ServerStatus.RUNNING
            server_instance.last_health_check = time.time()
            
        except Exception as e:
            server_instance.status = ServerStatus.ERROR
            server_instance.error_message = str(e)

class ResourceManager:
    """
    Manage system resources and optimize allocation.
    
    SpecBlock:
    - responsibility: "Manage system resources and optimize allocation"
    - must_never: "Exceed system resource limits", "Allocate resources without validation"
    - performance_budget: "15ms average, 30ms maximum"
    - security_level: "high"
    """
    
    def __init__(self):
        self.max_memory_mb = 1000  # Maximum memory for all servers
        self.max_cpu_percent = 80  # Maximum CPU for all servers
        self.max_file_descriptors = 1000  # Maximum file descriptors
        self.current_allocation = ResourceAllocation(0, 0, 0, 0, 0)
    
    def can_allocate_resources(self, requirements: Dict[str, Any]) -> bool:
        """Check if resources can be allocated."""
        required_memory = requirements.get('memory_mb', 0)
        required_cpu = requirements.get('cpu_percent', 0)
        required_fds = requirements.get('file_descriptors', 0)
        
        return (self.current_allocation.memory_mb + required_memory <= self.max_memory_mb and
                self.current_allocation.cpu_percent + required_cpu <= self.max_cpu_percent and
                self.current_allocation.file_descriptors + required_fds <= self.max_file_descriptors)
    
    def allocate_resources(self, requirements: Dict[str, Any]) -> bool:
        """Allocate resources for a server."""
        if not self.can_allocate_resources(requirements):
            return False
        
        self.current_allocation.memory_mb += requirements.get('memory_mb', 0)
        self.current_allocation.cpu_percent += requirements.get('cpu_percent', 0)
        self.current_allocation.file_descriptors += requirements.get('file_descriptors', 0)
        
        return True
    
    def deallocate_resources(self, requirements: Dict[str, Any]) -> None:
        """Deallocate resources for a server."""
        self.current_allocation.memory_mb -= requirements.get('memory_mb', 0)
        self.current_allocation.cpu_percent -= requirements.get('cpu_percent', 0)
        self.current_allocation.file_descriptors -= requirements.get('file_descriptors', 0)
        
        # Ensure non-negative values
        self.current_allocation.memory_mb = max(0, self.current_allocation.memory_mb)
        self.current_allocation.cpu_percent = max(0, self.current_allocation.cpu_percent)
        self.current_allocation.file_descriptors = max(0, self.current_allocation.file_descriptors)
    
    def get_resource_usage(self) -> Dict[str, float]:
        """Get current resource usage."""
        return {
            'memory_mb': self.current_allocation.memory_mb,
            'cpu_percent': self.current_allocation.cpu_percent,
            'file_descriptors': self.current_allocation.file_descriptors,
            'memory_usage_percent': (self.current_allocation.memory_mb / self.max_memory_mb) * 100,
            'cpu_usage_percent': (self.current_allocation.cpu_percent / self.max_cpu_percent) * 100
        }

class ServerManager:
    """
    Main server manager.
    
    SpecBlock:
    - responsibility: "Manage MCP server loading/unloading and resource allocation"
    - must_never: "Load servers without proper validation", "Exceed system resource limits"
    - performance_budget: "100ms average, 200ms maximum"
    - security_level: "high"
    """
    
    def __init__(self):
        self.registry = ServerRegistry()
        self.process_manager = ProcessManager()
        self.resource_manager = ResourceManager()
        self.max_tools = 40
        self.current_tools = 0
    
    def load_servers(self, server_ids: List[str]) -> Dict[str, bool]:
        """Load specified servers."""
        results = {}
        
        for server_id in server_ids:
            server_def = self.registry.get_server(server_id)
            if not server_def:
                results[server_id] = False
                continue
            
            # Check if server is already running
            if self.process_manager.is_server_running(server_id):
                results[server_id] = True
                continue
            
            # Check resource availability
            if not self.resource_manager.can_allocate_resources(server_def.resource_requirements):
                results[server_id] = False
                continue
            
            # Check tool count limit
            if self.current_tools + server_def.tool_count > self.max_tools:
                results[server_id] = False
                continue
            
            # Start server
            success = self.process_manager.start_server(server_def)
            if success:
                self.resource_manager.allocate_resources(server_def.resource_requirements)
                self.current_tools += server_def.tool_count
            
            results[server_id] = success
        
        return results
    
    def unload_servers(self, server_ids: List[str]) -> Dict[str, bool]:
        """Unload specified servers."""
        results = {}
        
        for server_id in server_ids:
            server_def = self.registry.get_server(server_id)
            if not server_def:
                results[server_id] = False
                continue
            
            # Stop server
            success = self.process_manager.stop_server(server_id)
            if success:
                self.resource_manager.deallocate_resources(server_def.resource_requirements)
                self.current_tools -= server_def.tool_count
            
            results[server_id] = success
        
        return results
    
    def get_server_status(self) -> Dict[str, Any]:
        """Get status of all servers."""
        status = {
            'total_servers': len(self.registry.get_all_servers()),
            'running_servers': len(self.process_manager.running_servers),
            'current_tools': self.current_tools,
            'max_tools': self.max_tools,
            'resource_usage': self.resource_manager.get_resource_usage(),
            'servers': {}
        }
        
        for server_id, server_instance in self.process_manager.running_servers.items():
            status['servers'][server_id] = {
                'status': server_instance.status.value,
                'uptime_seconds': time.time() - server_instance.start_time,
                'resource_usage': server_instance.resource_usage,
                'error_message': server_instance.error_message
            }
        
        return status
    
    def optimize_server_loading(self, required_tools: List[str]) -> List[str]:
        """Optimize server loading based on required tools."""
        # This would implement intelligent server selection based on required tools
        # For now, return a simple selection
        available_servers = []
        for server_def in self.registry.get_all_servers():
            if (self.resource_manager.can_allocate_resources(server_def.resource_requirements) and
                self.current_tools + server_def.tool_count <= self.max_tools):
                available_servers.append(server_def.server_id)
        
        return available_servers[:5]  # Return first 5 available servers
    
    def shutdown_all_servers(self) -> None:
        """Shutdown all running servers."""
        for server_id in list(self.process_manager.running_servers.keys()):
            self.process_manager.stop_server(server_id)
        
        self.process_manager.stop_health_check()
        self.current_tools = 0

if __name__ == "__main__":
    # Test the server manager
    manager = ServerManager()
    
    # Test server loading
    test_servers = ["core_aimos_server", "scor_server", "timeline_server"]
    results = manager.load_servers(test_servers)
    print(f"Server loading results: {results}")
    
    # Test server status
    status = manager.get_server_status()
    print(f"Server status: {json.dumps(status, indent=2)}")
    
    # Test server unloading
    unload_results = manager.unload_servers(test_servers)
    print(f"Server unloading results: {unload_results}")
    
    # Shutdown
    manager.shutdown_all_servers()
