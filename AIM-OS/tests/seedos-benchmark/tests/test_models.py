"""Tests for TaskFlow models."""

import pytest
from taskflow.models import Task


def test_task_creation():
    task = Task(title="Test task", priority=2)
    assert task.title == "Test task"
    assert task.priority == 2
    assert task.status == "pending"
    assert task.id is not None


def test_task_complete():
    task = Task(title="Complete me")
    task.complete()
    assert task.status == "done"
    assert task.completed_at is not None


def test_task_to_dict():
    task = Task(title="Dict test", description="testing")
    d = task.to_dict()
    assert d["title"] == "Dict test"
    assert "id" in d


def test_task_from_dict():
    data = {"title": "From dict", "priority": "3", "status": "in_progress"}
    task = Task.from_dict(data)
    assert task.title == "From dict"
    assert task.priority == 3


def test_task_validate_empty_title():
    task = Task(title="")
    errors = task.validate()
    assert "Title is required" in errors


def test_task_validate_bad_priority():
    task = Task(title="Test", priority=99)
    errors = task.validate()
    assert any("priority" in e.lower() for e in errors)


# TODO: test_task_validate_bad_status — currently no status validation exists
