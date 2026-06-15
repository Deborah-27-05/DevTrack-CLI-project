"""
models/task.py
Task model for DevTrack CLI.
Represents a development task inside a project, with priority and contributor support.
"""

from datetime import date
from typing import List

VALID_STATUSES = {"Pending", "In Progress", "Completed"}
VALID_PRIORITIES = {"Low", "Medium", "High"}


class Task:
    """
    Represents a task inside a software project.

    Tasks have a priority and status, both validated via property setters.
    A task can have multiple contributors (many-to-many with Users).

    Class Attributes:
        next_id (int): Auto-incrementing counter for unique IDs.

    Attributes:
        id (int): Unique task ID.
        title (str): Task title.
        description (str): Optional task description.
        priority (str): 'Low', 'Medium', or 'High'.
        status (str): 'Pending', 'In Progress', or 'Completed'.
        due_date (str | None): ISO-8601 due date string.
        project_id (int): ID of the owning project.
        contributor_ids (list[int]): IDs of contributing developers.
    """

    next_id: int = 1  # class-level ID counter

    def __init__(
        self,
        title: str,
        project_id: int,
        description: str = "",
        priority: str = "Medium",
        status: str = "Pending",
        due_date: str = None,
        contributor_ids: list = None,
        task_id: int = None,
    ):
        # Assign ID
        if task_id is not None:
            self.id = task_id
            if task_id >= Task.next_id:
                Task.next_id = task_id + 1
        else:
            self.id = Task.next_id
            Task.next_id += 1

        self.title = title
        self.project_id = project_id
        self.description = description
        self.priority = priority        # validated via setter
        self.status = status            # validated via setter
        self.due_date = due_date
        self.contributor_ids: List[int] = contributor_ids or []

    # ── Properties ────────────────────────────────────────────────────────────

    @property
    def status(self) -> str:
        """Return the current task status."""
        return self._status

    @status.setter
    def status(self, value: str):
        """Validate status against allowed values."""
        if value not in VALID_STATUSES:
            raise ValueError(
                f"Status must be one of {VALID_STATUSES}, got '{value}'."
            )
        self._status = value

    @property
    def priority(self) -> str:
        """Return the task priority."""
        return self._priority

    @priority.setter
    def priority(self, value: str):
        """Validate priority against allowed values."""
        if value not in VALID_PRIORITIES:
            raise ValueError(
                f"Priority must be one of {VALID_PRIORITIES}, got '{value}'."
            )
        self._priority = value

    # ── Helpers ───────────────────────────────────────────────────────────────

    def is_overdue(self) -> bool:
        """Return True if the task is past its due date and not completed."""
        if self.due_date and self.status != "Completed":
            try:
                return date.today() > date.fromisoformat(self.due_date)
            except ValueError:
                return False
        return False

    def complete(self):
        """Mark this task as Completed."""
        self.status = "Completed"

    def add_contributor(self, user_id: int):
        """Add a contributor by user ID (no duplicates)."""
        if user_id not in self.contributor_ids:
            self.contributor_ids.append(user_id)

    # ── Class methods ─────────────────────────────────────────────────────────

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Create a Task instance from a dictionary."""
        return cls(
            title=data["title"],
            project_id=data["project_id"],
            description=data.get("description", ""),
            priority=data.get("priority", "Medium"),
            status=data.get("status", "Pending"),
            due_date=data.get("due_date"),
            contributor_ids=data.get("contributor_ids", []),
            task_id=data["id"],
        )

    # ── Serialisation ─────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """Serialise the Task to a JSON-compatible dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "project_id": self.project_id,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "due_date": self.due_date,
            "contributor_ids": self.contributor_ids,
        }

    # ── Magic methods ─────────────────────────────────────────────────────────

    def __str__(self) -> str:
        overdue = " ⚠ OVERDUE" if self.is_overdue() else ""
        return (
            f"[{self.id}] {self.title} | {self.priority} | "
            f"{self.status}{overdue}"
        )

    def __repr__(self) -> str:
        return (
            f"Task(id={self.id!r}, title={self.title!r}, "
            f"priority={self.priority!r}, status={self.status!r})"
        )