"""
Timeline Integration

Integration with AIM-OS timeline system for audit trails and learning.
Tracks mission events, decisions, and outcomes for continuous improvement.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
import json

from .mission_intent import MissionIntent, MissionStatus
from .enforcement_layer import EnforcementResult, EnforcementAction

logger = logging.getLogger(__name__)


class TimelineEventType(Enum):
    """Types of timeline events."""
    
    MISSION_CREATED = "mission_created"
    MISSION_CLASSIFIED = "mission_classified"
    ACTION_ATTEMPTED = "action_attempted"
    ACTION_ALLOWED = "action_allowed"
    ACTION_BLOCKED = "action_blocked"
    ACTION_ESCALATED = "action_escalated"
    MISSION_UPDATED = "mission_updated"
    MISSION_COMPLETED = "mission_completed"
    MISSION_CANCELLED = "mission_cancelled"
    STOP_CONDITION_TRIGGERED = "stop_condition_triggered"
    ESCALATION_REQUIRED = "escalation_required"
    APPROVAL_REQUIRED = "approval_required"


@dataclass
class TimelineEvent:
    """Timeline event for audit and learning."""
    
    event_id: str
    mission_id: str
    event_type: TimelineEventType
    timestamp: datetime
    action_attempted: Optional[str] = None
    decision: Optional[str] = None
    rationale: Optional[str] = None
    risks_seen: List[str] = field(default_factory=list)
    artifacts_produced: List[str] = field(default_factory=list)
    confidence_level: Optional[float] = None
    enforcement_result: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert timeline event to dictionary for serialization."""
        return {
            "event_id": self.event_id,
            "mission_id": self.mission_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "action_attempted": self.action_attempted,
            "decision": self.decision,
            "rationale": self.rationale,
            "risks_seen": self.risks_seen,
            "artifacts_produced": self.artifacts_produced,
            "confidence_level": self.confidence_level,
            "enforcement_result": self.enforcement_result,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TimelineEvent:
        """Create timeline event from dictionary."""
        # Convert enum value back to enum instance
        data["event_type"] = TimelineEventType(data["event_type"])
        
        # Convert datetime string back to datetime object
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        
        return cls(**data)


class TimelineIntegration:
    """
    Timeline integration for audit trails and learning.
    
    Tracks mission events, decisions, and outcomes to enable continuous
    improvement and provide audit trails for the Intent Classification System.
    """
    
    def __init__(self, timeline_client: Optional[Any] = None):
        """
        Initialize timeline integration.
        
        Args:
            timeline_client: Optional timeline client for external integration
        """
        self.timeline_client = timeline_client
        self._event_buffer: List[TimelineEvent] = []
        self._max_buffer_size = 100
        
        # Event counters for statistics
        self._event_counts = {event_type: 0 for event_type in TimelineEventType}
        self._mission_events: Dict[str, List[TimelineEvent]] = {}
    
    def log_mission_created(self, mission_intent: MissionIntent, 
                           classification_confidence: float) -> TimelineEvent:
        """Log mission creation event."""
        event = TimelineEvent(
            event_id=self._generate_event_id(),
            mission_id=mission_intent.mission_id,
            event_type=TimelineEventType.MISSION_CREATED,
            timestamp=datetime.utcnow(),
            action_attempted="create_mission",
            decision="mission_created",
            rationale=f"Mission created with {mission_intent.primary_category.value} category",
            confidence_level=classification_confidence,
            metadata={
                "primary_category": mission_intent.primary_category.value,
                "lifecycle_stage": mission_intent.lifecycle_stage.value,
                "scope_level": mission_intent.scope_level.value,
                "clarity_state": mission_intent.clarity_state.value,
                "facets": mission_intent.facets,
                "complexity_score": mission_intent.complexity_score
            }
        )
        
        self._add_event(event)
        return event
    
    def log_mission_classified(self, mission_intent: MissionIntent, 
                              classification_result: Dict[str, Any]) -> TimelineEvent:
        """Log mission classification event."""
        event = TimelineEvent(
            event_id=self._generate_event_id(),
            mission_id=mission_intent.mission_id,
            event_type=TimelineEventType.MISSION_CLASSIFIED,
            timestamp=datetime.utcnow(),
            action_attempted="classify_intent",
            decision="intent_classified",
            rationale=f"Intent classified as {mission_intent.primary_category.value}",
            confidence_level=mission_intent.confidence_level,
            metadata={
                "classification_confidence": classification_result.get('classification_confidence', 0.0),
                "processing_time_ms": classification_result.get('processing_time_ms', 0.0),
                "warnings": classification_result.get('warnings', []),
                "errors": classification_result.get('errors', [])
            }
        )
        
        self._add_event(event)
        return event
    
    def log_action_attempted(self, action: str, mission_intent: MissionIntent, 
                            enforcement_result: EnforcementResult) -> TimelineEvent:
        """Log action attempt event."""
        event_type = self._get_action_event_type(enforcement_result.action)
        
        event = TimelineEvent(
            event_id=self._generate_event_id(),
            mission_id=mission_intent.mission_id,
            event_type=event_type,
            timestamp=datetime.utcnow(),
            action_attempted=action,
            decision=enforcement_result.action.value,
            rationale=enforcement_result.reason,
            risks_seen=self._extract_risks(mission_intent, enforcement_result),
            confidence_level=mission_intent.confidence_level,
            enforcement_result=enforcement_result.__dict__,
            metadata={
                "mission_status": mission_intent.mission_status.value,
                "escalation_required": enforcement_result.escalation_required,
                "required_approvals": enforcement_result.required_approvals,
                "warnings": enforcement_result.warnings
            }
        )
        
        self._add_event(event)
        return event
    
    def log_mission_updated(self, mission_intent: MissionIntent, 
                           update_type: str, update_data: Dict[str, Any]) -> TimelineEvent:
        """Log mission update event."""
        event = TimelineEvent(
            event_id=self._generate_event_id(),
            mission_id=mission_intent.mission_id,
            event_type=TimelineEventType.MISSION_UPDATED,
            timestamp=datetime.utcnow(),
            action_attempted="update_mission",
            decision="mission_updated",
            rationale=f"Mission updated: {update_type}",
            confidence_level=mission_intent.confidence_level,
            metadata={
                "update_type": update_type,
                "update_data": update_data,
                "mission_status": mission_intent.mission_status.value
            }
        )
        
        self._add_event(event)
        return event
    
    def log_mission_completed(self, mission_intent: MissionIntent, 
                             completion_reason: str, artifacts: List[str]) -> TimelineEvent:
        """Log mission completion event."""
        event = TimelineEvent(
            event_id=self._generate_event_id(),
            mission_id=mission_intent.mission_id,
            event_type=TimelineEventType.MISSION_COMPLETED,
            timestamp=datetime.utcnow(),
            action_attempted="complete_mission",
            decision="mission_completed",
            rationale=f"Mission completed: {completion_reason}",
            artifacts_produced=artifacts,
            confidence_level=mission_intent.confidence_level,
            metadata={
                "completion_reason": completion_reason,
                "artifacts_count": len(artifacts),
                "mission_duration": self._calculate_mission_duration(mission_intent)
            }
        )
        
        self._add_event(event)
        return event
    
    def log_stop_condition_triggered(self, mission_intent: MissionIntent, 
                                   stop_condition: str, context: Dict[str, Any]) -> TimelineEvent:
        """Log stop condition triggered event."""
        event = TimelineEvent(
            event_id=self._generate_event_id(),
            mission_id=mission_intent.mission_id,
            event_type=TimelineEventType.STOP_CONDITION_TRIGGERED,
            timestamp=datetime.utcnow(),
            action_attempted="check_stop_conditions",
            decision="stop_condition_triggered",
            rationale=f"Stop condition triggered: {stop_condition}",
            risks_seen=[stop_condition],
            confidence_level=mission_intent.confidence_level,
            metadata={
                "stop_condition": stop_condition,
                "context": context,
                "mission_status": mission_intent.mission_status.value
            }
        )
        
        self._add_event(event)
        return event
    
    def log_escalation_required(self, mission_intent: MissionIntent, 
                               escalation_reason: str, escalation_data: Dict[str, Any]) -> TimelineEvent:
        """Log escalation required event."""
        event = TimelineEvent(
            event_id=self._generate_event_id(),
            mission_id=mission_intent.mission_id,
            event_type=TimelineEventType.ESCALATION_REQUIRED,
            timestamp=datetime.utcnow(),
            action_attempted="escalate_mission",
            decision="escalation_required",
            rationale=f"Escalation required: {escalation_reason}",
            risks_seen=[escalation_reason],
            confidence_level=mission_intent.confidence_level,
            metadata={
                "escalation_reason": escalation_reason,
                "escalation_data": escalation_data,
                "mission_status": mission_intent.mission_status.value
            }
        )
        
        self._add_event(event)
        return event
    
    def get_mission_timeline(self, mission_id: str) -> List[TimelineEvent]:
        """Get timeline events for a specific mission."""
        return self._mission_events.get(mission_id, [])
    
    def get_recent_events(self, limit: int = 50) -> List[TimelineEvent]:
        """Get recent timeline events."""
        all_events = []
        for mission_events in self._mission_events.values():
            all_events.extend(mission_events)
        
        # Sort by timestamp (most recent first)
        all_events.sort(key=lambda e: e.timestamp, reverse=True)
        return all_events[:limit]
    
    def get_event_statistics(self) -> Dict[str, Any]:
        """Get timeline event statistics."""
        total_events = sum(self._event_counts.values())
        
        return {
            "total_events": total_events,
            "event_counts": self._event_counts.copy(),
            "missions_tracked": len(self._mission_events),
            "buffer_size": len(self._event_buffer),
            "max_buffer_size": self._max_buffer_size
        }
    
    def flush_events(self) -> List[TimelineEvent]:
        """Flush buffered events to external timeline system."""
        if not self.timeline_client:
            logger.warning("No timeline client configured, events remain in buffer")
            return []
        
        try:
            # Convert events to external format
            external_events = []
            for event in self._event_buffer:
                external_event = self._convert_to_external_format(event)
                external_events.append(external_event)
            
            # Send to external timeline system
            result = self.timeline_client.batch_create_events(external_events)
            
            if result.get('success', False):
                logger.info(f"Successfully flushed {len(external_events)} events to timeline system")
                self._event_buffer.clear()
                return external_events
            else:
                logger.error(f"Failed to flush events: {result.get('error', 'Unknown error')}")
                return []
                
        except Exception as e:
            logger.error(f"Error flushing events to timeline system: {e}")
            return []
    
    def _add_event(self, event: TimelineEvent) -> None:
        """Add event to timeline."""
        # Add to mission-specific events
        if event.mission_id not in self._mission_events:
            self._mission_events[event.mission_id] = []
        self._mission_events[event.mission_id].append(event)
        
        # Add to buffer
        self._event_buffer.append(event)
        
        # Update counters
        self._event_counts[event.event_type] += 1
        
        # Flush buffer if it's full
        if len(self._event_buffer) >= self._max_buffer_size:
            self.flush_events()
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID."""
        import uuid
        return str(uuid.uuid4())
    
    def _get_action_event_type(self, enforcement_action: EnforcementAction) -> TimelineEventType:
        """Get timeline event type from enforcement action."""
        mapping = {
            EnforcementAction.ALLOW: TimelineEventType.ACTION_ALLOWED,
            EnforcementAction.BLOCK: TimelineEventType.ACTION_BLOCKED,
            EnforcementAction.ESCALATE: TimelineEventType.ACTION_ESCALATED,
            EnforcementAction.REQUIRE_APPROVAL: TimelineEventType.APPROVAL_REQUIRED,
            EnforcementAction.WARN: TimelineEventType.ACTION_ALLOWED,
            EnforcementAction.PAUSE: TimelineEventType.ACTION_BLOCKED
        }
        return mapping.get(enforcement_action, TimelineEventType.ACTION_ATTEMPTED)
    
    def _extract_risks(self, mission_intent: MissionIntent, 
                      enforcement_result: EnforcementResult) -> List[str]:
        """Extract risk information from mission and enforcement result."""
        risks = []
        
        if mission_intent.risk_level in ['high', 'critical']:
            risks.append(f"High risk level: {mission_intent.risk_level}")
        
        if mission_intent.complexity_score > 0.8:
            risks.append(f"High complexity: {mission_intent.complexity_score}")
        
        if mission_intent.confidence_level < 0.3:
            risks.append(f"Low confidence: {mission_intent.confidence_level}")
        
        if enforcement_result.escalation_required:
            risks.append(f"Escalation required: {enforcement_result.escalation_reason}")
        
        if enforcement_result.stop_conditions_triggered:
            risks.extend([f"Stop condition: {condition}" for condition in enforcement_result.stop_conditions_triggered])
        
        return risks
    
    def _calculate_mission_duration(self, mission_intent: MissionIntent) -> Optional[float]:
        """Calculate mission duration in seconds."""
        if mission_intent.mission_status == MissionStatus.COMPLETED:
            duration = (datetime.utcnow() - mission_intent.created_at).total_seconds()
            return duration
        return None
    
    def _convert_to_external_format(self, event: TimelineEvent) -> Dict[str, Any]:
        """Convert timeline event to external system format."""
        return {
            "id": event.event_id,
            "mission_id": event.mission_id,
            "type": event.event_type.value,
            "timestamp": event.timestamp.isoformat(),
            "data": {
                "action_attempted": event.action_attempted,
                "decision": event.decision,
                "rationale": event.rationale,
                "risks_seen": event.risks_seen,
                "artifacts_produced": event.artifacts_produced,
                "confidence_level": event.confidence_level,
                "enforcement_result": event.enforcement_result,
                "metadata": event.metadata
            }
        }
