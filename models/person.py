"""
models/person.py
Base class for all person-like entities in DevTrack CLI.
Provides shared name and email attributes with validation.
"""

import re


class Person:
    """
    Base class representing a person.
    Demonstrates inheritance — User extends this class.

    Attributes:
        name (str): Full name of the person.
        email (str): Validated email address.
    """

    def __init__(self, name: str, email: str):
        self.name = name    # triggers @name.setter
        self.email = email  # triggers @email.setter

    # ── Properties ────────────────────────────────────────────────────────────

    @property
    def name(self) -> str:
        """Return the person's name."""
        return self._name

    @name.setter
    def name(self, value: str):
        """Validate that name is a non-empty string."""
        if not value or not value.strip():
            raise ValueError("Name cannot be empty.")
        self._name = value.strip()

    @property
    def email(self) -> str:
        """Return the person's email address."""
        return self._email

    @email.setter
    def email(self, value: str):
        """Validate email format using a regex pattern."""
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
        if not re.match(pattern, value.strip()):
            raise ValueError(f"Invalid email address: '{value}'")
        self._email = value.strip().lower()

    # ── Magic methods ─────────────────────────────────────────────────────────

    def __str__(self) -> str:
        return f"{self.name} <{self.email}>"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, email={self.email!r})"