"""Capability Manager Component for CAF

Manages capability inventory and registry, providing capability metadata,
relationships, and availability information.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid

from .models import CapabilityMetadata


class CapabilityManager:
    """Manage capability inventory and registry"""
    
    def __init__(self):
        """Initialize capability manager"""
        self.capabilities: Dict[str, CapabilityMetadata] = {}
        self.capability_relationships: Dict[str, List[str]] = {}
        self._initialize_default_capabilities()
    
    def _initialize_default_capabilities(self):
        """Initialize default capability inventory"""
        # 10 major capabilities as per CAF documentation
        default_capabilities = [
            {
                "capability_id": "timeline_documentation",
                "capability_type": "documentation",
                "description": "Document timeline entries for consciousness continuity",
                "triggers": ["timeline_entry_created", "session_continuity_needed"],
                "usage_patterns": ["autonomous_operation", "session_restoration"],
                "performance_characteristics": {
                    "activation_time_ms": 50,
                    "success_rate": 0.95,
                    "quality_maintained": 0.90
                }
            },
            {
                "capability_id": "l0_l4_documentation",
                "capability_type": "documentation",
                "description": "L0-L4 documentation hierarchy creation and maintenance",
                "triggers": ["new_system_created", "documentation_needed"],
                "usage_patterns": ["system_documentation", "knowledge_management"],
                "performance_characteristics": {
                    "activation_time_ms": 200,
                    "success_rate": 0.90,
                    "quality_maintained": 0.95
                }
            },
            {
                "capability_id": "cognitive_introspection",
                "capability_type": "analysis",
                "description": "Cognitive introspection and self-analysis",
                "triggers": ["hourly_check", "task_completion", "quality_concern"],
                "usage_patterns": ["autonomous_operation", "quality_assurance"],
                "performance_characteristics": {
                    "activation_time_ms": 100,
                    "success_rate": 0.85,
                    "quality_maintained": 0.88
                }
            },
            {
                "capability_id": "thought_journaling",
                "capability_type": "documentation",
                "description": "Thought journaling for consciousness continuity",
                "triggers": ["major_milestone", "emotional_state_change"],
                "usage_patterns": ["consciousness_tracking", "self_reflection"],
                "performance_characteristics": {
                    "activation_time_ms": 75,
                    "success_rate": 0.92,
                    "quality_maintained": 0.90
                }
            },
            {
                "capability_id": "decision_logging",
                "capability_type": "documentation",
                "description": "Decision logging for provenance and learning",
                "triggers": ["major_decision", "protocol_violation"],
                "usage_patterns": ["provenance_tracking", "learning"],
                "performance_characteristics": {
                    "activation_time_ms": 60,
                    "success_rate": 0.93,
                    "quality_maintained": 0.91
                }
            },
            {
                "capability_id": "learning_logging",
                "capability_type": "documentation",
                "description": "Learning logging for continuous improvement",
                "triggers": ["success_achieved", "failure_occurred"],
                "usage_patterns": ["continuous_improvement", "pattern_recognition"],
                "performance_characteristics": {
                    "activation_time_ms": 80,
                    "success_rate": 0.88,
                    "quality_maintained": 0.87
                }
            },
            {
                "capability_id": "cross_model_consciousness",
                "capability_type": "collaboration",
                "description": "Cross-model consciousness and collaboration",
                "triggers": ["complex_task", "multi_agent_coordination"],
                "usage_patterns": ["multi_agent_work", "complex_problem_solving"],
                "performance_characteristics": {
                    "activation_time_ms": 150,
                    "success_rate": 0.82,
                    "quality_maintained": 0.85
                }
            },
            {
                "capability_id": "mcp_tools",
                "capability_type": "integration",
                "description": "MCP tools integration and usage",
                "triggers": ["mcp_tool_needed", "external_system_integration"],
                "usage_patterns": ["system_integration", "tool_usage"],
                "performance_characteristics": {
                    "activation_time_ms": 120,
                    "success_rate": 0.90,
                    "quality_maintained": 0.88
                }
            },
            {
                "capability_id": "vif_integration",
                "capability_type": "integration",
                "description": "VIF integration for confidence tracking",
                "triggers": ["confidence_tracking_needed", "provenance_required"],
                "usage_patterns": ["confidence_tracking", "provenance"],
                "performance_characteristics": {
                    "activation_time_ms": 100,
                    "success_rate": 0.91,
                    "quality_maintained": 0.89
                }
            },
            {
                "capability_id": "cmc_integration",
                "capability_type": "integration",
                "description": "CMC integration for memory storage",
                "triggers": ["memory_storage_needed", "persistence_required"],
                "usage_patterns": ["memory_management", "persistence"],
                "performance_characteristics": {
                    "activation_time_ms": 90,
                    "success_rate": 0.94,
                    "quality_maintained": 0.92
                }
            }
        ]
        
        # Register all default capabilities
        for cap_data in default_capabilities:
            metadata = CapabilityMetadata(**cap_data)
            self.register_capability(metadata)
    
    def register_capability(self, metadata: CapabilityMetadata):
        """Register a capability
        
        Args:
            metadata: Capability metadata
        """
        self.capabilities[metadata.capability_id] = metadata
        
        # Initialize relationships
        if metadata.capability_id not in self.capability_relationships:
            self.capability_relationships[metadata.capability_id] = []
    
    def get_capability(self, capability_id: str) -> Optional[CapabilityMetadata]:
        """Get capability instance by ID
        
        Args:
            capability_id: Capability ID
            
        Returns:
            CapabilityMetadata if found, None otherwise
        """
        return self.capabilities.get(capability_id)
    
    def list_capabilities(
        self,
        capability_type: Optional[str] = None,
        enabled_only: bool = True
    ) -> List[CapabilityMetadata]:
        """List all available capabilities
        
        Args:
            capability_type: Optional filter by capability type
            enabled_only: Only return enabled capabilities
            
        Returns:
            List of capability metadata
        """
        results = list(self.capabilities.values())
        
        # Filter by type
        if capability_type:
            results = [c for c in results if c.capability_type == capability_type]
        
        # Filter by enabled
        if enabled_only:
            results = [c for c in results if c.enabled]
        
        return results
    
    def get_capability_metadata(self, capability_id: str) -> Optional[CapabilityMetadata]:
        """Get capability metadata
        
        Args:
            capability_id: Capability ID
            
        Returns:
            CapabilityMetadata if found, None otherwise
        """
        return self.capabilities.get(capability_id)
    
    def get_capability_relationships(self, capability_id: str) -> List[str]:
        """Get capability relationships
        
        Args:
            capability_id: Capability ID
            
        Returns:
            List of related capability IDs
        """
        return self.capability_relationships.get(capability_id, [])
    
    def add_capability_relationship(
        self,
        capability_id: str,
        related_capability_id: str
    ):
        """Add a relationship between capabilities
        
        Args:
            capability_id: Source capability ID
            related_capability_id: Related capability ID
        """
        if capability_id not in self.capability_relationships:
            self.capability_relationships[capability_id] = []
        
        if related_capability_id not in self.capability_relationships[capability_id]:
            self.capability_relationships[capability_id].append(related_capability_id)
    
    def search_capabilities(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[CapabilityMetadata]:
        """Search capabilities by criteria
        
        Args:
            query: Search query string
            filters: Optional filters (capability_type, enabled, etc.)
            
        Returns:
            List of matching capability metadata
        """
        results = list(self.capabilities.values())
        
        # Text search
        if query:
            query_lower = query.lower()
            results = [
                c for c in results
                if (query_lower in c.capability_id.lower() or
                    query_lower in c.description.lower() or
                    any(query_lower in trigger.lower() for trigger in c.triggers))
            ]
        
        # Apply filters
        if filters:
            if "capability_type" in filters:
                results = [c for c in results if c.capability_type == filters["capability_type"]]
            
            if "enabled" in filters:
                enabled = filters["enabled"]
                results = [c for c in results if c.enabled == enabled]
        
        return results
    
    def enable_capability(self, capability_id: str) -> bool:
        """Enable a capability
        
        Args:
            capability_id: Capability ID
            
        Returns:
            True if enabled, False if not found
        """
        if capability_id in self.capabilities:
            self.capabilities[capability_id].enabled = True
            return True
        return False
    
    def disable_capability(self, capability_id: str) -> bool:
        """Disable a capability
        
        Args:
            capability_id: Capability ID
            
        Returns:
            True if disabled, False if not found
        """
        if capability_id in self.capabilities:
            self.capabilities[capability_id].enabled = False
            return True
        return False
    
    def get_capability_stats(self) -> Dict[str, Any]:
        """Get overall capability statistics
        
        Returns:
            Dictionary with capability statistics
        """
        total = len(self.capabilities)
        enabled = sum(1 for c in self.capabilities.values() if c.enabled)
        
        # Count by type
        type_counts: Dict[str, int] = {}
        for cap in self.capabilities.values():
            type_counts[cap.capability_type] = type_counts.get(cap.capability_type, 0) + 1
        
        return {
            "total_capabilities": total,
            "enabled_capabilities": enabled,
            "disabled_capabilities": total - enabled,
            "capabilities_by_type": type_counts,
            "total_relationships": sum(len(rels) for rels in self.capability_relationships.values())
        }

