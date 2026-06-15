"""
models/user.py
Developer / User model for DevTrack CLI.
Inherits from Person and adds developer-specific attributes.
"""

from models.person import Person

# Allowed developer roles
VALID_ROLES = {
    "Frontend Developer",
    "Backend Developer",
    "Full Stack Developer",
    "QA Engineer",
    "DevOps Engineer",
    "Data Engineer",
}


class User(Person):
    """
    Represents a developer in the system.

    Inherits name and email from Person.
    Adds a unique ID, role, and list of owned project IDs.

    Class Attributes:
        next_id (int): Auto-incrementing counter for unique IDs.

    Attributes:
        id (int): Unique developer ID.
        role (str): Developer role (e.g. 'Backend Developer').
        project_ids (list[int]): IDs of projects owned by this developer.
    """

    next_id: int = 1  # class-level ID counter

    def __init__(
        self,
        name: str,
        email: str,
        role: str = "Full Stack Developer",
        user_id: int = None,
        project_ids: list = None,
    ):
        super().__init__(name, email)

        # Assign ID — either loaded from storage or auto-generated
        if user_id is not None:
            self.id = user_id
            if user_id >= User.next_id:
                User.next_id = user_id + 1
        else:
            self.id = User.next_id
            User.next_id += 1

        self.role = role
        self.project_ids: list[int] = project_ids or []

    # ── Properties ────────────────────────────────────────────────────────────

    @property
    def role(self) -> str:
        """Return the developer's role."""
        return self._role

    @role.setter
    def role(self, value: str):
        """Accept any non-empty role string (flexible for custom roles)."""
        if not value or not value.strip():
            raise ValueError("Role cannot be empty.")
        self._role = value.strip()

    # ── Class methods ─────────────────────────────────────────────────────────

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Create a User instance from a dictionary (e.g. loaded from JSON)."""
        return cls(
            name=data["name"],
            email=data["email"],
            role=data.get("role", "Full Stack Developer"),
            user_id=data["id"],
            project_ids=data.get("project_ids", []),
        )

    # ── Serialisation ─────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """Serialise the User to a JSON-compatible dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "project_ids": self.project_ids,
        }

    # ── Magic methods ─────────────────────────────────────────────────────────

    def __str__(self) -> str:
        return f"[{self.id}] {self.name} ({self.role}) — {self.email}"

    def __repr__(self) -> str:
        return (
            f"User(id={self.id!r}, name={self.name!r}, "
            f"email={self.email!r}, role={self.role!r})"
        )