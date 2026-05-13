"""Priority-based task scheduler."""

from typing import List
from .models import Task


def get_next_tasks(tasks: List[Task], limit: int = 5) -> List[Task]:
    """
    Get the next tasks to work on, sorted by priority.
    
    Priority order: critical (3) > high (2) > medium (1) > low (0)
    Within same priority, older tasks come first.
    """
    pending = [t for t in tasks if t.status in ("pending", "in_progress")]
    # Sort by priority descending, then created_at ascending
    pending.sort(key=lambda t: (-t.priority, t.created_at))
    return pending[:limit]


def auto_assign(tasks: List[Task], assignees: List[str]) -> dict:
    """
    Auto-assign unassigned tasks to available assignees round-robin.
    Returns mapping of task_id -> assignee.
    """
    unassigned = [t for t in tasks if not t.assignee and t.status == "pending"]
    assignments = {}
    
    for i, task in enumerate(unassigned):
        assignee = assignees[i % len(assignees)]
        task.assignee = assignee
        assignments[task.id] = assignee
    
    return assignments
