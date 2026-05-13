"""Duration anomaly detection for tasks."""

import statistics
from typing import List, Tuple
from .models import Task


def detect_anomalies(tasks: List[Task], threshold: float = 2.0) -> List[Tuple[Task, str]]:
    """
    Detect anomalies in task durations using z-score method.
    
    Args:
        tasks: List of tasks to analyze
        threshold: Z-score threshold for anomaly (default 2.0)
    
    Returns:
        List of (task, reason) tuples for anomalous tasks
    """
    # Filter to completed tasks with duration
    completed = [t for t in tasks if t.status == "done" and t.duration_hours > 0]
    
    if len(completed) < 3:
        return []
    
    durations = [t.duration_hours for t in completed]
    mean = statistics.mean(durations)
    stdev = statistics.stdev(durations)
    
    # BUG: division by zero if all durations are identical (stdev=0)
    anomalies = []
    for task in completed:
        z_score = (task.duration_hours - mean) / stdev
        if abs(z_score) > threshold:
            direction = "unusually long" if z_score > 0 else "unusually short"
            anomalies.append((task, f"{direction} (z={z_score:.2f}, duration={task.duration_hours}h, avg={mean:.1f}h)"))
    
    return anomalies


def get_summary_stats(tasks: List[Task]) -> dict:
    """Get summary statistics for tasks."""
    total = len(tasks)
    if total == 0:
        return {"total": 0}
    
    by_status = {}
    by_priority = {}
    
    for task in tasks:
        by_status[task.status] = by_status.get(task.status, 0) + 1
        by_priority[task.priority] = by_priority.get(task.priority, 0) + 1
    
    completed = [t for t in tasks if t.duration_hours > 0]
    avg_duration = statistics.mean([t.duration_hours for t in completed]) if completed else 0
    
    return {
        "total": total,
        "by_status": by_status,
        "by_priority": by_priority,
        "avg_duration_hours": round(avg_duration, 2),
        "completion_rate": round(by_status.get("done", 0) / total * 100, 1),
    }
