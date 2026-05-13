"""Task data models."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class Task:
    """Represents a single task."""
    title: str
    description: str = ""
    priority: int = 0  # 0=low, 1=medium, 2=high, 3=critical
    status: str = "pending"  # pending, in_progress, done, cancelled
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    duration_hours: float = 0.0
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    assignee: str = ""
    tags: str = ""  # comma-separated

    def complete(self):
        """Mark task as done."""
        self.status = "done"
        self.completed_at = datetime.now().isoformat()

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "duration_hours": self.duration_hours,
            "assignee": self.assignee,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Create Task from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            title=data["title"],
            description=data.get("description", ""),
            priority=int(data.get("priority", 0)),
            status=data.get("status", "pending"),
            created_at=data.get("created_at", datetime.now().isoformat()),
            completed_at=data.get("completed_at"),
            duration_hours=float(data.get("duration_hours", 0)),
            assignee=data.get("assignee", ""),
            tags=data.get("tags", ""),
        )

    def validate(self):
        """Validate task data. Returns list of errors."""
        errors = []
        if not self.title:
            errors.append("Title is required")
        if self.priority not in (0, 1, 2, 3):
            errors.append(f"Invalid priority: {self.priority}")
        # BUG: status validation is missing — any string accepted
        return errors
