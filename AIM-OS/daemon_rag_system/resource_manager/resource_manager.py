#!/usr/bin/env python3
"""
Resource Manager - Manage system resources and optimize allocation
Part of Daemon/RAG System Implementation

Following A-H Protocol and DEL methodology from ChatGPT journal
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import time
import psutil
import threading
import json
from collections import defaultdict, deque

class ResourceType(Enum):
    """Types of system resources."""
    MEMORY = "memory"
    CPU = "cpu"
    DISK = "disk"
    NETWORK = "network"
    FILE_DESCRIPTORS = "file_descriptors"
    THREADS = "threads"

class ResourcePriority(Enum):
    """Resource allocation priorities."""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4

@dataclass
class ResourceAllocation:
    """Resource allocation for a component."""
    component_id: str
    resource_type: ResourceType
    allocated_amount: float
    priority: ResourcePriority
    timestamp: float
    duration: float = 0.0

@dataclass
class ResourceLimit:
    """Resource limit configuration."""
    resource_type: ResourceType
    max_amount: float
    warning_threshold: float
    critical_threshold: float
    unit: str

@dataclass
class ResourceUsage:
    """Current resource usage."""
    resource_type: ResourceType
    current_usage: float
    allocated_usage: float
    available_usage: float
    usage_percentage: float
    timestamp: float

class ResourceMonitor:
    """
    Monitor system resource usage.
    
    SpecBlock:
    - responsibility: "Monitor system resource usage"
    - must_never: "Miss critical resource issues", "Provide inaccurate usage data"
    - performance_budget: "5ms average, 10ms maximum"
    - security_level: "medium"
    """
    
    def __init__(self):
        self.resource_usage_history: Dict[ResourceType, deque] = {
            resource_type: deque(maxlen=100) for resource_type in ResourceType
        }
        self.monitoring_thread = None
        self.running = False
        self.monitoring_interval = 1.0
    
    def start_monitoring(self) -> None:
        """Start resource monitoring."""
        if self.running:
            return
        
        self.running = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
    
    def stop_monitoring(self) -> None:
        """Stop resource monitoring."""
        self.running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
    
    def _monitoring_loop(self) -> None:
        """Main monitoring loop."""
        while self.running:
            try:
                # Collect resource usage
                usage_data = self._collect_resource_usage()
                
                # Store in history
                for resource_type, usage in usage_data.items():
                    self.resource_usage_history[resource_type].append(usage)
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                print(f"Error in resource monitoring: {e}")
                time.sleep(5)
    
    def _collect_resource_usage(self) -> Dict[ResourceType, ResourceUsage]:
        """Collect current resource usage."""
        usage_data = {}
        current_time = time.time()
        
        try:
            # Memory usage
            memory_info = psutil.virtual_memory()
            usage_data[ResourceType.MEMORY] = ResourceUsage(
                resource_type=ResourceType.MEMORY,
                current_usage=memory_info.used / (1024 * 1024),  # MB
                allocated_usage=0.0,  # Will be calculated by ResourceManager
                available_usage=memory_info.available / (1024 * 1024),  # MB
                usage_percentage=memory_info.percent,
                timestamp=current_time
            )
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            usage_data[ResourceType.CPU] = ResourceUsage(
                resource_type=ResourceType.CPU,
                current_usage=cpu_percent,
                allocated_usage=0.0,  # Will be calculated by ResourceManager
                available_usage=100.0 - cpu_percent,
                usage_percentage=cpu_percent,
                timestamp=current_time
            )
            
            # Disk usage
            disk_usage = psutil.disk_usage('/')
            disk_percent = (disk_usage.used / disk_usage.total) * 100
            usage_data[ResourceType.DISK] = ResourceUsage(
                resource_type=ResourceType.DISK,
                current_usage=disk_usage.used / (1024 * 1024),  # MB
                allocated_usage=0.0,  # Will be calculated by ResourceManager
                available_usage=disk_usage.free / (1024 * 1024),  # MB
                usage_percentage=disk_percent,
                timestamp=current_time
            )
            
            # Network usage (simplified)
            network_io = psutil.net_io_counters()
            usage_data[ResourceType.NETWORK] = ResourceUsage(
                resource_type=ResourceType.NETWORK,
                current_usage=network_io.bytes_sent + network_io.bytes_recv,
                allocated_usage=0.0,  # Will be calculated by ResourceManager
                available_usage=float('inf'),  # Network is typically not limited
                usage_percentage=0.0,  # Network usage percentage is not meaningful
                timestamp=current_time
            )
            
            # File descriptors
            try:
                process = psutil.Process()
                fd_count = process.num_fds() if hasattr(process, 'num_fds') else 0
                usage_data[ResourceType.FILE_DESCRIPTORS] = ResourceUsage(
                    resource_type=ResourceType.FILE_DESCRIPTORS,
                    current_usage=fd_count,
                    allocated_usage=0.0,  # Will be calculated by ResourceManager
                    available_usage=1000 - fd_count,  # Assume 1000 max FDs
                    usage_percentage=(fd_count / 1000) * 100,
                    timestamp=current_time
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                usage_data[ResourceType.FILE_DESCRIPTORS] = ResourceUsage(
                    resource_type=ResourceType.FILE_DESCRIPTORS,
                    current_usage=0.0,
                    allocated_usage=0.0,
                    available_usage=1000.0,
                    usage_percentage=0.0,
                    timestamp=current_time
                )
            
            # Threads
            thread_count = threading.active_count()
            usage_data[ResourceType.THREADS] = ResourceUsage(
                resource_type=ResourceType.THREADS,
                current_usage=thread_count,
                allocated_usage=0.0,  # Will be calculated by ResourceManager
                available_usage=100 - thread_count,  # Assume 100 max threads
                usage_percentage=(thread_count / 100) * 100,
                timestamp=current_time
            )
            
        except Exception as e:
            print(f"Error collecting resource usage: {e}")
        
        return usage_data
    
    def get_resource_usage(self, resource_type: ResourceType) -> Optional[ResourceUsage]:
        """Get current resource usage for a specific type."""
        history = self.resource_usage_history.get(resource_type)
        if history:
            return history[-1]
        return None
    
    def get_resource_history(self, resource_type: ResourceType, limit: int = 10) -> List[ResourceUsage]:
        """Get resource usage history."""
        history = self.resource_usage_history.get(resource_type, deque())
        return list(history)[-limit:]

class ResourceAllocator:
    """
    Allocate and manage system resources.
    
    SpecBlock:
    - responsibility: "Allocate and manage system resources"
    - must_never: "Exceed system resource limits", "Allocate resources without validation"
    - performance_budget: "15ms average, 30ms maximum"
    - security_level: "high"
    """
    
    def __init__(self, resource_monitor: ResourceMonitor):
        self.monitor = resource_monitor
        self.allocations: Dict[str, List[ResourceAllocation]] = defaultdict(list)
        self.resource_limits = self._initialize_resource_limits()
        self.allocation_lock = threading.Lock()
    
    def _initialize_resource_limits(self) -> Dict[ResourceType, ResourceLimit]:
        """Initialize resource limits."""
        return {
            ResourceType.MEMORY: ResourceLimit(
                resource_type=ResourceType.MEMORY,
                max_amount=1000.0,  # 1000 MB
                warning_threshold=80.0,  # 80%
                critical_threshold=90.0,  # 90%
                unit="MB"
            ),
            ResourceType.CPU: ResourceLimit(
                resource_type=ResourceType.CPU,
                max_amount=80.0,  # 80%
                warning_threshold=70.0,  # 70%
                critical_threshold=85.0,  # 85%
                unit="percent"
            ),
            ResourceType.DISK: ResourceLimit(
                resource_type=ResourceType.DISK,
                max_amount=10000.0,  # 10000 MB
                warning_threshold=80.0,  # 80%
                critical_threshold=90.0,  # 90%
                unit="MB"
            ),
            ResourceType.NETWORK: ResourceLimit(
                resource_type=ResourceType.NETWORK,
                max_amount=float('inf'),  # No limit
                warning_threshold=0.0,
                critical_threshold=0.0,
                unit="bytes"
            ),
            ResourceType.FILE_DESCRIPTORS: ResourceLimit(
                resource_type=ResourceType.FILE_DESCRIPTORS,
                max_amount=1000.0,  # 1000 FDs
                warning_threshold=80.0,  # 80%
                critical_threshold=90.0,  # 90%
                unit="count"
            ),
            ResourceType.THREADS: ResourceLimit(
                resource_type=ResourceType.THREADS,
                max_amount=100.0,  # 100 threads
                warning_threshold=80.0,  # 80%
                critical_threshold=90.0,  # 90%
                unit="count"
            )
        }
    
    def allocate_resources(self, 
                          component_id: str,
                          resource_requirements: Dict[ResourceType, float],
                          priority: ResourcePriority = ResourcePriority.MEDIUM) -> bool:
        """Allocate resources for a component."""
        with self.allocation_lock:
            # Check if resources can be allocated
            if not self._can_allocate_resources(resource_requirements):
                return False
            
            # Allocate resources
            for resource_type, amount in resource_requirements.items():
                allocation = ResourceAllocation(
                    component_id=component_id,
                    resource_type=resource_type,
                    allocated_amount=amount,
                    priority=priority,
                    timestamp=time.time()
                )
                self.allocations[component_id].append(allocation)
            
            return True
    
    def deallocate_resources(self, component_id: str) -> bool:
        """Deallocate resources for a component."""
        with self.allocation_lock:
            if component_id in self.allocations:
                del self.allocations[component_id]
                return True
            return False
    
    def _can_allocate_resources(self, resource_requirements: Dict[ResourceType, float]) -> bool:
        """Check if resources can be allocated."""
        for resource_type, amount in resource_requirements.items():
            limit = self.resource_limits.get(resource_type)
            if not limit:
                continue
            
            # Get current usage
            current_usage = self.monitor.get_resource_usage(resource_type)
            if not current_usage:
                continue
            
            # Calculate total allocated amount
            total_allocated = self._get_total_allocated_amount(resource_type)
            
            # Check if allocation would exceed limit
            if total_allocated + amount > limit.max_amount:
                return False
        
        return True
    
    def _get_total_allocated_amount(self, resource_type: ResourceType) -> float:
        """Get total allocated amount for a resource type."""
        total = 0.0
        for component_allocations in self.allocations.values():
            for allocation in component_allocations:
                if allocation.resource_type == resource_type:
                    total += allocation.allocated_amount
        return total
    
    def get_allocation_summary(self) -> Dict[str, Any]:
        """Get resource allocation summary."""
        summary = {
            'total_components': len(self.allocations),
            'allocations_by_type': {},
            'total_allocated': {},
            'available_resources': {}
        }
        
        # Calculate allocations by type
        for resource_type in ResourceType:
            total_allocated = self._get_total_allocated_amount(resource_type)
            limit = self.resource_limits.get(resource_type)
            
            summary['allocations_by_type'][resource_type.value] = {
                'total_allocated': total_allocated,
                'max_amount': limit.max_amount if limit else float('inf'),
                'usage_percentage': (total_allocated / limit.max_amount * 100) if limit else 0.0
            }
            
            summary['total_allocated'][resource_type.value] = total_allocated
            
            # Calculate available resources
            current_usage = self.monitor.get_resource_usage(resource_type)
            if current_usage and limit:
                available = max(0, limit.max_amount - total_allocated)
                summary['available_resources'][resource_type.value] = available
            else:
                summary['available_resources'][resource_type.value] = float('inf')
        
        return summary

class ResourceOptimizer:
    """
    Optimize resource allocation and usage.
    
    SpecBlock:
    - responsibility: "Optimize resource allocation and usage"
    - must_never: "Optimize without considering system stability", "Make harmful optimizations"
    - performance_budget: "20ms average, 40ms maximum"
    - security_level: "medium"
    """
    
    def __init__(self, resource_allocator: ResourceAllocator):
        self.allocator = resource_allocator
        self.optimization_history: List[Dict[str, Any]] = []
    
    def optimize_resource_allocation(self) -> List[Dict[str, Any]]:
        """Optimize resource allocation."""
        optimizations = []
        
        # Get current allocation summary
        summary = self.allocator.get_allocation_summary()
        
        # Check for over-allocated resources
        for resource_type_str, allocation_info in summary['allocations_by_type'].items():
            resource_type = ResourceType(resource_type_str)
            usage_percentage = allocation_info['usage_percentage']
            
            if usage_percentage > 90:  # Critical threshold
                optimization = self._optimize_critical_resource(resource_type, allocation_info)
                if optimization:
                    optimizations.append(optimization)
            elif usage_percentage > 80:  # Warning threshold
                optimization = self._optimize_warning_resource(resource_type, allocation_info)
                if optimization:
                    optimizations.append(optimization)
        
        # Check for under-utilized resources
        for resource_type_str, allocation_info in summary['allocations_by_type'].items():
            resource_type = ResourceType(resource_type_str)
            usage_percentage = allocation_info['usage_percentage']
            
            if usage_percentage < 20:  # Under-utilized
                optimization = self._optimize_underutilized_resource(resource_type, allocation_info)
                if optimization:
                    optimizations.append(optimization)
        
        # Store optimization history
        if optimizations:
            self.optimization_history.append({
                'timestamp': time.time(),
                'optimizations': optimizations,
                'summary': summary
            })
        
        return optimizations
    
    def _optimize_critical_resource(self, resource_type: ResourceType, allocation_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Optimize critical resource usage."""
        return {
            'type': 'critical_optimization',
            'resource_type': resource_type.value,
            'current_usage': allocation_info['usage_percentage'],
            'recommendations': [
                'Immediately reduce resource allocation',
                'Implement resource pooling',
                'Add resource monitoring alerts',
                'Consider load balancing',
                'Implement resource cleanup'
            ],
            'priority': 'critical',
            'estimated_impact': 'high'
        }
    
    def _optimize_warning_resource(self, resource_type: ResourceType, allocation_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Optimize warning-level resource usage."""
        return {
            'type': 'warning_optimization',
            'resource_type': resource_type.value,
            'current_usage': allocation_info['usage_percentage'],
            'recommendations': [
                'Monitor resource usage closely',
                'Implement resource quotas',
                'Optimize resource allocation algorithms',
                'Consider resource pre-allocation',
                'Add resource usage alerts'
            ],
            'priority': 'high',
            'estimated_impact': 'medium'
        }
    
    def _optimize_underutilized_resource(self, resource_type: ResourceType, allocation_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Optimize under-utilized resource."""
        return {
            'type': 'underutilized_optimization',
            'resource_type': resource_type.value,
            'current_usage': allocation_info['usage_percentage'],
            'recommendations': [
                'Increase resource allocation for active components',
                'Implement resource sharing',
                'Optimize resource distribution',
                'Consider resource consolidation',
                'Implement dynamic resource scaling'
            ],
            'priority': 'medium',
            'estimated_impact': 'low'
        }
    
    def get_optimization_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get optimization history."""
        return self.optimization_history[-limit:]

class ResourceManager:
    """
    Main resource manager.
    
    SpecBlock:
    - responsibility: "Manage system resources and optimize allocation"
    - must_never: "Exceed system resource limits", "Allocate resources without validation"
    - performance_budget: "15ms average, 30ms maximum"
    - security_level: "high"
    """
    
    def __init__(self):
        self.monitor = ResourceMonitor()
        self.allocator = ResourceAllocator(self.monitor)
        self.optimizer = ResourceOptimizer(self.allocator)
        
        self.optimization_thread = None
        self.running = False
        self.optimization_interval = 30.0  # 30 seconds
    
    def start(self) -> None:
        """Start resource management."""
        if self.running:
            return
        
        self.running = True
        
        # Start monitoring
        self.monitor.start_monitoring()
        
        # Start optimization thread
        self.optimization_thread = threading.Thread(target=self._optimization_loop, daemon=True)
        self.optimization_thread.start()
    
    def stop(self) -> None:
        """Stop resource management."""
        self.running = False
        
        # Stop monitoring
        self.monitor.stop_monitoring()
        
        # Stop optimization thread
        if self.optimization_thread:
            self.optimization_thread.join(timeout=5)
    
    def _optimization_loop(self) -> None:
        """Main optimization loop."""
        while self.running:
            try:
                # Run optimization
                optimizations = self.optimizer.optimize_resource_allocation()
                
                if optimizations:
                    print(f"Resource optimizations applied: {len(optimizations)}")
                
                time.sleep(self.optimization_interval)
                
            except Exception as e:
                print(f"Error in resource optimization: {e}")
                time.sleep(10)
    
    def allocate_resources(self, 
                          component_id: str,
                          resource_requirements: Dict[str, float],
                          priority: str = "medium") -> bool:
        """Allocate resources for a component."""
        # Convert string resource types to enum
        resource_types = {}
        for resource_str, amount in resource_requirements.items():
            try:
                resource_type = ResourceType(resource_str)
                resource_types[resource_type] = amount
            except ValueError:
                print(f"Unknown resource type: {resource_str}")
                continue
        
        # Convert priority string to enum
        priority_enum = ResourcePriority.MEDIUM
        if priority.lower() == "critical":
            priority_enum = ResourcePriority.CRITICAL
        elif priority.lower() == "high":
            priority_enum = ResourcePriority.HIGH
        elif priority.lower() == "low":
            priority_enum = ResourcePriority.LOW
        
        return self.allocator.allocate_resources(component_id, resource_types, priority_enum)
    
    def deallocate_resources(self, component_id: str) -> bool:
        """Deallocate resources for a component."""
        return self.allocator.deallocate_resources(component_id)
    
    def get_resource_usage(self) -> Dict[str, Any]:
        """Get current resource usage."""
        usage = {}
        
        for resource_type in ResourceType:
            resource_usage = self.monitor.get_resource_usage(resource_type)
            if resource_usage:
                usage[resource_type.value] = {
                    'current_usage': resource_usage.current_usage,
                    'allocated_usage': resource_usage.allocated_usage,
                    'available_usage': resource_usage.available_usage,
                    'usage_percentage': resource_usage.usage_percentage,
                    'timestamp': resource_usage.timestamp
                }
        
        return usage
    
    def get_allocation_summary(self) -> Dict[str, Any]:
        """Get resource allocation summary."""
        return self.allocator.get_allocation_summary()
    
    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Get optimization recommendations."""
        return self.optimizer.optimize_resource_allocation()
    
    def get_optimization_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get optimization history."""
        return self.optimizer.get_optimization_history(limit)
    
    def export_resource_data(self, filepath: str) -> None:
        """Export resource data to file."""
        data = {
            'resource_usage': self.get_resource_usage(),
            'allocation_summary': self.get_allocation_summary(),
            'optimization_recommendations': self.get_optimization_recommendations(),
            'optimization_history': self.get_optimization_history(),
            'export_timestamp': time.time()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

if __name__ == "__main__":
    # Test the resource manager
    manager = ResourceManager()
    
    # Start resource management
    manager.start()
    print("Resource management started")
    
    try:
        # Test resource allocation
        test_requirements = {
            'memory': 100.0,  # 100 MB
            'cpu': 20.0,      # 20%
            'file_descriptors': 10.0  # 10 FDs
        }
        
        success = manager.allocate_resources("test_component", test_requirements, "medium")
        print(f"Resource allocation: {'SUCCESS' if success else 'FAILED'}")
        
        # Wait for monitoring to collect data
        time.sleep(2)
        
        # Get resource usage
        usage = manager.get_resource_usage()
        print(f"Resource Usage: {json.dumps(usage, indent=2)}")
        
        # Get allocation summary
        summary = manager.get_allocation_summary()
        print(f"Allocation Summary: {json.dumps(summary, indent=2)}")
        
        # Get optimization recommendations
        recommendations = manager.get_optimization_recommendations()
        print(f"Optimization Recommendations: {json.dumps(recommendations, indent=2)}")
        
        # Test resource deallocation
        success = manager.deallocate_resources("test_component")
        print(f"Resource deallocation: {'SUCCESS' if success else 'FAILED'}")
        
        # Export resource data
        manager.export_resource_data("resource_data.json")
        print("Resource data exported to resource_data.json")
        
    finally:
        # Stop resource management
        manager.stop()
        print("Resource management stopped")
