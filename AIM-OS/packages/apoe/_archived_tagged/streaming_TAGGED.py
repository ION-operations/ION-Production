"""Streaming Results for APOE

Real-time result updates during plan execution.
"""

from __future__ import annotations
from typing import Dict, Any, Callable, Optional, AsyncIterator
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio


# NL_TAG: VIF-MODEL-001 | Types of streaming events. | class StreamEventType | []
class StreamEventType(str, Enum):
    """Types of streaming events."""
    PLAN_START = "plan_start"
    STEP_START = "step_start"
    STEP_PROGRESS = "step_progress"
    STEP_COMPLETE = "step_complete"
    STEP_ERROR = "step_error"
    GATE_CHECK = "gate_check"
    PLAN_COMPLETE = "plan_complete"
    PLAN_ERROR = "plan_error"


@dataclass
# NL_TAG: VIF-MODEL-002 | Event emitted during plan execution. | class StreamEvent | []
class StreamEvent:
    """Event emitted during plan execution."""
    type: StreamEventType
    timestamp: datetime
    data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.type.value,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data
        }


# NL_TAG: VIF-MODEL-003 | Executor that streams results in real-time. | class StreamingExecutor | []
class StreamingExecutor:
    """Executor that streams results in real-time."""
    
    def __init__(
        self,
        on_event: Optional[Callable[[StreamEvent], None]] = None
    ):
        """
        Initialize streaming executor.
        
        Args:
            on_event: Callback for each event (optional)
        """
        self.on_event = on_event
        self.events: list[StreamEvent] = []
        self._cancelled = False
    
    def cancel(self):
        """Cancel execution."""
        self._cancelled = True
    
    def is_cancelled(self) -> bool:
        """Check if execution was cancelled."""
        return self._cancelled
    
    def emit(self, event_type: StreamEventType, data: Dict[str, Any]):
        """
        Emit an event.
        
        Args:
            event_type: Type of event
            data: Event data
        """
        event = StreamEvent(
            type=event_type,
            timestamp=datetime.utcnow(),
            data=data
        )
        
        # Store event
        self.events.append(event)
        
        # Call callback if provided
        if self.on_event:
            self.on_event(event)
    
    async def execute_plan_streaming(
        self,
        plan,
        step_executor: Callable
    ) -> Dict[str, Any]:
        """
        Execute plan with streaming updates.
        
        Args:
            plan: ExecutionPlan to execute
            step_executor: Function to execute individual steps
        
        Returns:
            Execution results
        """
        # Emit plan start
        self.emit(StreamEventType.PLAN_START, {
            "plan_name": plan.name,
            "step_count": len(plan.steps)
        })
        
        results = {}
        errors = []
        
        try:
            # Execute each step
            for step in plan.steps:
                # Check cancellation
                if self._cancelled:
                    self.emit(StreamEventType.PLAN_ERROR, {
                        "error": "Execution cancelled by user",
                        "completed_steps": list(results.keys())
                    })
                    return {
                        "success": False,
                        "error": "Cancelled",
                        "results": results
                    }
                
                # Emit step start
                self.emit(StreamEventType.STEP_START, {
                    "step_id": step.id,
                    "step_name": step.name,
                    "role": step.role.value if hasattr(step.role, 'value') else str(step.role)
                })
                
                try:
                    # Execute step
                    if asyncio.iscoroutinefunction(step_executor):
                        result = await step_executor(step)
                    else:
                        result = step_executor(step)
                    
                    results[step.id] = result
                    
                    # Emit step complete
                    self.emit(StreamEventType.STEP_COMPLETE, {
                        "step_id": step.id,
                        "result": result
                    })
                    
                except Exception as e:
                    # Emit step error
                    self.emit(StreamEventType.STEP_ERROR, {
                        "step_id": step.id,
                        "error": str(e),
                        "error_type": type(e).__name__
                    })
                    errors.append({
                        "step_id": step.id,
                        "error": str(e)
                    })
            
            # Emit plan complete
            self.emit(StreamEventType.PLAN_COMPLETE, {
                "total_steps": len(plan.steps),
                "completed": len(results),
                "errors": len(errors)
            })
            
            return {
                "success": len(errors) == 0,
                "results": results,
                "errors": errors if errors else None
            }
            
        except Exception as e:
            # Emit plan error
            self.emit(StreamEventType.PLAN_ERROR, {
                "error": str(e),
                "error_type": type(e).__name__,
                "completed_steps": list(results.keys())
            })
            
            return {
                "success": False,
                "error": str(e),
                "results": results
            }
    
    def get_events(self) -> list[StreamEvent]:
        """Get all emitted events."""
        return self.events.copy()
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current progress."""
        completed_steps = sum(
            1 for e in self.events 
            if e.type == StreamEventType.STEP_COMPLETE
        )
        
        error_steps = sum(
            1 for e in self.events 
            if e.type == StreamEventType.STEP_ERROR
        )
        
        # Find total steps from plan_start event
        total_steps = 0
        for e in self.events:
            if e.type == StreamEventType.PLAN_START:
                total_steps = e.data.get("step_count", 0)
                break
        
        return {
            "total_steps": total_steps,
            "completed": completed_steps,
            "errors": error_steps,
            "progress_pct": (completed_steps / total_steps * 100) if total_steps > 0 else 0.0
        }


# NL_TAG: VIF-UTIL-001 | Stream plan execution as async iterator. | stream_plan_execution(plan, step_executor) | []
async def stream_plan_execution(
    plan,
    step_executor: Callable
) -> AsyncIterator[StreamEvent]:
    """
    Stream plan execution as async iterator.
    
    Args:
        plan: ExecutionPlan to execute
        step_executor: Function to execute steps
    
    Yields:
        StreamEvent objects
    """
    queue: asyncio.Queue[Optional[StreamEvent]] = asyncio.Queue()
    
    def on_event(event: StreamEvent):
        """Callback to add events to queue."""
        asyncio.create_task(queue.put(event))
    
    executor = StreamingExecutor(on_event=on_event)
    
    # Start execution in background
    exec_task = asyncio.create_task(
        executor.execute_plan_streaming(plan, step_executor)
    )
    
    # Yield events as they arrive
    while not exec_task.done() or not queue.empty():
        try:
            event = await asyncio.wait_for(queue.get(), timeout=0.1)
            yield event
        except asyncio.TimeoutError:
            continue
    
    # Ensure execution completes
    await exec_task


# NL_TAG: VIF-MODEL-004 | Track and report execution progress. | class ProgressTracker | []
class ProgressTracker:
    # NL_TAG: VIF-UTIL-002 | Convert to dictionary. | to_dict(self) | []
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.type.value,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data
        }


class StreamingExecutor:
    """Executor that streams results in real-time."""
    
    # NL_TAG: VIF-UTIL-003 | Initialize streaming executor. | __init__(self, on_event) | []
    def __init__(
        self,
        on_event: Optional[Callable[[StreamEvent], None]] = None
    ):
        """
        Initialize streaming executor.
        
        Args:
            on_event: Callback for each event (optional)
        """
        self.on_event = on_event
        self.events: list[StreamEvent] = []
        self._cancelled = False
    
    # NL_TAG: VIF-UTIL-004 | Cancel execution. | cancel(self) | []
    def cancel(self):
        """Cancel execution."""
        self._cancelled = True
    
    # NL_TAG: VIF-UTIL-005 | Check if execution was cancelled. | is_cancelled(self) | []
    def is_cancelled(self) -> bool:
        """Check if execution was cancelled."""
        return self._cancelled
    
    # NL_TAG: VIF-UTIL-006 | Emit an event. | emit(self, event_type, data) | []
    def emit(self, event_type: StreamEventType, data: Dict[str, Any]):
        """
        Emit an event.
        
        Args:
            event_type: Type of event
            data: Event data
        """
        event = StreamEvent(
            type=event_type,
            timestamp=datetime.utcnow(),
            data=data
        )
        
        # Store event
        self.events.append(event)
        
        # Call callback if provided
        if self.on_event:
            self.on_event(event)
    
    # NL_TAG: VIF-UTIL-007 | Execute plan with streaming updates. | execute_plan_streaming(self, plan, step_executor) | []
    async def execute_plan_streaming(
        self,
        plan,
        step_executor: Callable
    ) -> Dict[str, Any]:
        """
        Execute plan with streaming updates.
        
        Args:
            plan: ExecutionPlan to execute
            step_executor: Function to execute individual steps
        
        Returns:
            Execution results
        """
        # Emit plan start
        self.emit(StreamEventType.PLAN_START, {
            "plan_name": plan.name,
            "step_count": len(plan.steps)
        })
        
        results = {}
        errors = []
        
        try:
            # Execute each step
            for step in plan.steps:
                # Check cancellation
                if self._cancelled:
                    self.emit(StreamEventType.PLAN_ERROR, {
                        "error": "Execution cancelled by user",
                        "completed_steps": list(results.keys())
                    })
                    return {
                        "success": False,
                        "error": "Cancelled",
                        "results": results
                    }
                
                # Emit step start
                self.emit(StreamEventType.STEP_START, {
                    "step_id": step.id,
                    "step_name": step.name,
                    "role": step.role.value if hasattr(step.role, 'value') else str(step.role)
                })
                
                try:
                    # Execute step
                    if asyncio.iscoroutinefunction(step_executor):
                        result = await step_executor(step)
                    else:
                        result = step_executor(step)
                    
                    results[step.id] = result
                    
                    # Emit step complete
                    self.emit(StreamEventType.STEP_COMPLETE, {
                        "step_id": step.id,
                        "result": result
                    })
                    
                except Exception as e:
                    # Emit step error
                    self.emit(StreamEventType.STEP_ERROR, {
                        "step_id": step.id,
                        "error": str(e),
                        "error_type": type(e).__name__
                    })
                    errors.append({
                        "step_id": step.id,
                        "error": str(e)
                    })
            
            # Emit plan complete
            self.emit(StreamEventType.PLAN_COMPLETE, {
                "total_steps": len(plan.steps),
                "completed": len(results),
                "errors": len(errors)
            })
            
            return {
                "success": len(errors) == 0,
                "results": results,
                "errors": errors if errors else None
            }
            
        except Exception as e:
            # Emit plan error
            self.emit(StreamEventType.PLAN_ERROR, {
                "error": str(e),
                "error_type": type(e).__name__,
                "completed_steps": list(results.keys())
            })
            
            return {
                "success": False,
                "error": str(e),
                "results": results
            }
    
    # NL_TAG: VIF-UTIL-008 | Get all emitted events. | get_events(self) | []
    def get_events(self) -> list[StreamEvent]:
        """Get all emitted events."""
        return self.events.copy()
    
    # NL_TAG: VIF-UTIL-009 | Get current progress. | get_progress(self) | []
    def get_progress(self) -> Dict[str, Any]:
        """Get current progress."""
        completed_steps = sum(
            1 for e in self.events 
            if e.type == StreamEventType.STEP_COMPLETE
        )
        
        error_steps = sum(
            1 for e in self.events 
            if e.type == StreamEventType.STEP_ERROR
        )
        
        # Find total steps from plan_start event
        total_steps = 0
        for e in self.events:
            if e.type == StreamEventType.PLAN_START:
                total_steps = e.data.get("step_count", 0)
                break
        
        return {
            "total_steps": total_steps,
            "completed": completed_steps,
            "errors": error_steps,
            "progress_pct": (completed_steps / total_steps * 100) if total_steps > 0 else 0.0
        }


async def stream_plan_execution(
    plan,
    step_executor: Callable
) -> AsyncIterator[StreamEvent]:
    """
    Stream plan execution as async iterator.
    
    Args:
        plan: ExecutionPlan to execute
        step_executor: Function to execute steps
    
    Yields:
        StreamEvent objects
    """
    queue: asyncio.Queue[Optional[StreamEvent]] = asyncio.Queue()
    
    # NL_TAG: VIF-UTIL-010 | Callback to add events to queue. | on_event(event) | []
    def on_event(event: StreamEvent):
        """Callback to add events to queue."""
        asyncio.create_task(queue.put(event))
    
    executor = StreamingExecutor(on_event=on_event)
    
    # Start execution in background
    exec_task = asyncio.create_task(
        executor.execute_plan_streaming(plan, step_executor)
    )
    
    # Yield events as they arrive
    while not exec_task.done() or not queue.empty():
        try:
            event = await asyncio.wait_for(queue.get(), timeout=0.1)
            yield event
        except asyncio.TimeoutError:
            continue
    
    # Ensure execution completes
    await exec_task


class ProgressTracker:
    """Track and report execution progress."""
    
    # NL_TAG: VIF-UTIL-011 |   init   | __init__(self) | []
    def __init__(self):
        self.steps_total = 0
        self.steps_completed = 0
        self.steps_failed = 0
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
    
    # NL_TAG: VIF-UTIL-012 | Handle streaming events to update progress. | on_event(self, event) | []
    def on_event(self, event: StreamEvent):
        """Handle streaming events to update progress."""
        if event.type == StreamEventType.PLAN_START:
            self.steps_total = event.data.get("step_count", 0)
            self.start_time = event.timestamp
        
        elif event.type == StreamEventType.STEP_COMPLETE:
            self.steps_completed += 1
        
        elif event.type == StreamEventType.STEP_ERROR:
            self.steps_failed += 1
        
        elif event.type in [StreamEventType.PLAN_COMPLETE, StreamEventType.PLAN_ERROR]:
            self.end_time = event.timestamp
    
    # NL_TAG: VIF-UTIL-013 | Get progress statistics. | get_stats(self) | []
    def get_stats(self) -> Dict[str, Any]:
        """Get progress statistics."""
        stats = {
            "total": self.steps_total,
            "completed": self.steps_completed,
            "failed": self.steps_failed,
            "remaining": self.steps_total - self.steps_completed - self.steps_failed,
            "progress_pct": (self.steps_completed / self.steps_total * 100) if self.steps_total > 0 else 0.0
        }
        
        if self.start_time:
            stats["start_time"] = self.start_time.isoformat()
            
            if self.end_time:
                duration = (self.end_time - self.start_time).total_seconds()
                stats["duration_seconds"] = duration
                stats["plan_completed"] = True
            else:
                # Still running
                duration = (datetime.utcnow() - self.start_time).total_seconds()
                stats["duration_seconds"] = duration
                stats["plan_completed"] = False
        
        return stats

