"""CSV-based task storage."""

import csv
import os
from typing import List, Optional
from .models import Task


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DEFAULT_FILE = os.path.join(DATA_DIR, "tasks.csv")

FIELDNAMES = [
    "id", "title", "description", "priority", "status",
    "created_at", "completed_at", "duration_hours", "assignee", "tags"
]


def load_tasks(filepath: str = DEFAULT_FILE) -> List[Task]:
    """Load all tasks from CSV file."""
    if not os.path.exists(filepath):
        return []

    tasks = []
    with open(filepath, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tasks.append(Task.from_dict(row))
    return tasks


def save_tasks(tasks: List[Task], filepath: str = DEFAULT_FILE) -> None:
    """Save all tasks to CSV file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for task in tasks:
            writer.writerow(task.to_dict())


def get_task(task_id: str, filepath: str = DEFAULT_FILE) -> Optional[Task]:
    """Get a single task by ID."""
    tasks = load_tasks(filepath)
    for task in tasks:
        if task.id == task_id:
            return task
    return None


def add_task(task: Task, filepath: str = DEFAULT_FILE) -> Task:
    """Add a new task."""
    tasks = load_tasks(filepath)
    # BUG: no duplicate ID check — can create tasks with same ID
    tasks.append(task)
    save_tasks(tasks, filepath)
    return task


def update_task(task_id: str, updates: dict, filepath: str = DEFAULT_FILE) -> Optional[Task]:
    """Update an existing task."""
    tasks = load_tasks(filepath)
    for i, task in enumerate(tasks):
        if task.id == task_id:
            for key, value in updates.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            save_tasks(tasks, filepath)
            return task
    return None


def delete_task(task_id: str, filepath: str = DEFAULT_FILE) -> bool:
    """Delete a task by ID."""
    tasks = load_tasks(filepath)
    original_len = len(tasks)
    tasks = [t for t in tasks if t.id != task_id]
    if len(tasks) < original_len:
        save_tasks(tasks, filepath)
        return True
    return False
