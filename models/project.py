"""
models/project.py
Project model for DevTrack CLI.
Represents a software development project with tasks and an owner.
"""

from datetime import date
from typing import List

VALID_STATUSES = {"Planning", "In Progress", "Completed"}


class Project:
    """
    Represents a software development project.

    A project is owned by one developer (User) and can hold many tasks.

    Class Attributes:
        next_id (int): Auto-incrementing counter for unique IDs.

    Attributes:
        id (int): Unique project ID.
        title (str): Project title.
        description (str): Short project description.
        due_date (str | None): ISO-8601 due date string (YYYY-MM-DD).
        status (str): Current status — 'Planning', 'In Progress', or 'Completed'.
        owner_id (int): ID of the owning developer.
        task_ids (list[int]): IDs of tasks belonging to this project.
    """

    next_id: int = 1  # class-level ID counter

    def __init__(
        self,
        title: str,
        owner_id: int,
        description: str = "",
        due_date: str = None,
        status: str = "Planning",
        task_ids: list = None,
        project_id: int = None,
    ):
        # Assign ID
        if project_id is not None:
            self.id = project_id
            if project_id >= Project.next_id:
                Project.next_id = project_id + 1
        else:
            self.id = Project.next_id
            Project.next_id += 1

        self.title = title
        self.owner_id = owner_id
        self.description = description
        self.due_date = due_date
        self.status = status          # validated via setter
        self.task_ids: List[int] = task_ids or []

    # ── Properties ────────────────────────────────────────────────────────────

    @property
    def status(self) -> str:
        """Return the current project status."""
        return self._status

    @status.setter
    def status(self, value: str):
        """Validate that the status is one of the allowed values."""
        if value not in VALID_STATUSES:
            raise ValueError(
                f"Status must be one of {VALID_STATUSES}, got '{value}'."
            )
        self._status = value

    # ── Helpers ───────────────────────────────────────────────────────────────

    def is_overdue(self) -> bool:
        """Return True if the project's due date has passed and it is not Completed."""
        if self.due_date and self.status != "Completed":
            try:
                return date.today() > date.fromisoformat(self.due_date)
            except ValueError:
                return False
        return False

    # ── Class methods ─────────────────────────────────────────────────────────

    @classmethod
    def from_dict(cls, data: dict) -> "Project":
        """Create a Project instance from a dictionary."""
        return cls(
            title=data["title"],
            owner_id=data["owner_id"],
            description=data.get("description", ""),
            due_date=data.get("due_date"),
            status=data.get("status", "Planning"),
            task_ids=data.get("task_ids", []),
            project_id=data["id"],
        )

    # ── Serialisation ─────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """Serialise the Project to a JSON-compatible dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "owner_id": self.owner_id,
            "description": self.description,
            "due_date": self.due_date,
            "status": self.status,
            "task_ids": self.task_ids,
        }

    # ── Magic methods ─────────────────────────────────────────────────────────

    def __str__(self) -> str:
        overdue = " ⚠ OVERDUE" if self.is_overdue() else ""
        return f"[{self.id}] {self.title} | {self.status}{overdue}"

    def __repr__(self) -> str:
        return (
            f"Project(id={self.id!r}, title={self.title!r}, "
            f"status={self.status!r})"
        )