"""
tests/test_user.py
Unit tests for the User model.
Tests cover creation, validation, serialisation, and ID auto-increment.
"""

import unittest
from models.user import User


class TestUserCreation(unittest.TestCase):
    """Tests for creating User instances."""

    def setUp(self):
        """Reset the class-level ID counter before each test."""
        User.next_id = 1

    def test_create_user_with_valid_data(self):
        """A user created with valid data should store all fields correctly."""
        u = User(name="Debbie", email="debbie@gmail.com", role="Backend Developer")
        self.assertEqual(u.name, "Debbie")
        self.assertEqual(u.email, "debbie@gmail.com")
        self.assertEqual(u.role, "Backend Developer")

    def test_user_id_is_assigned_automatically(self):
        """A new user should receive a unique integer ID."""
        u = User(name="Debbie", email="debbie@gmail.com")
        self.assertIsInstance(u.id, int)
        self.assertGreater(u.id, 0)

    def test_user_ids_auto_increment(self):
        """Each new user should get an ID one higher than the previous."""
        u1 = User("Alice", "alice@example.com")
        u2 = User("Bob", "bob@example.com")
        self.assertEqual(u2.id, u1.id + 1)

    def test_default_role_is_full_stack(self):
        """Role should default to 'Full Stack Developer' when not provided."""
        u = User("Debbie", "debbie@gmail.com")
        self.assertEqual(u.role, "Full Stack Developer")

    def test_startup_ids_defaults_to_empty_list(self):
        """project_ids should be an empty list when not provided."""
        u = User("Debbie", "debbie@gmail.com")
        self.assertEqual(u.project_ids, [])


class TestUserValidation(unittest.TestCase):
    """Tests for User field validation via property setters."""

    def setUp(self):
        User.next_id = 1

    def test_invalid_email_raises_value_error(self):
        """An invalid email format should raise a ValueError."""
        with self.assertRaises(ValueError):
            User(name="Debbie", email="not-an-email")

    def test_empty_name_raises_value_error(self):
        """An empty name should raise a ValueError."""
        with self.assertRaises(ValueError):
            User(name="", email="debbie@gmail.com")

    def test_whitespace_only_name_raises_value_error(self):
        """A name containing only whitespace should raise a ValueError."""
        with self.assertRaises(ValueError):
            User(name="   ", email="debbie@gmail.com")

    def test_email_is_normalised_to_lowercase(self):
        """Email addresses should be stored in lowercase."""
        u = User("Debbie", "DEBBIE@GMAIL.COM")
        self.assertEqual(u.email, "debbie@gmail.com")

    def test_name_is_stripped_of_whitespace(self):
        """Leading and trailing whitespace should be stripped from names."""
        u = User("  Debbie  ", "debbie@gmail.com")
        self.assertEqual(u.name, "Debbie")

    def test_empty_role_raises_value_error(self):
        """An empty role string should raise a ValueError."""
        with self.assertRaises(ValueError):
            User("Debbie", "debbie@gmail.com", role="")


class TestUserSerialisation(unittest.TestCase):
    """Tests for to_dict() and from_dict() round-trips."""

    def setUp(self):
        User.next_id = 1

    def test_to_dict_contains_all_fields(self):
        """to_dict() should include id, name, email, role, and project_ids."""
        u = User("Debbie", "debbie@gmail.com", role="Backend Developer", user_id=5)
        d = u.to_dict()
        self.assertEqual(d["id"], 5)
        self.assertEqual(d["name"], "Debbie")
        self.assertEqual(d["email"], "debbie@gmail.com")
        self.assertEqual(d["role"], "Backend Developer")
        self.assertIn("project_ids", d)

    def test_from_dict_restores_all_fields(self):
        """from_dict() should recreate a User with matching attributes."""
        data = {
            "id": 42,
            "name": "Alice",
            "email": "alice@dev.io",
            "role": "QA Engineer",
            "project_ids": [1, 2, 3],
        }
        u = User.from_dict(data)
        self.assertEqual(u.id, 42)
        self.assertEqual(u.name, "Alice")
        self.assertEqual(u.email, "alice@dev.io")
        self.assertEqual(u.role, "QA Engineer")
        self.assertEqual(u.project_ids, [1, 2, 3])

    def test_round_trip_preserves_data(self):
        """Serialising then deserialising should produce an identical object."""
        original = User("Debbie", "debbie@gmail.com", role="Backend Developer",
                        user_id=7, project_ids=[10, 20])
        restored = User.from_dict(original.to_dict())
        self.assertEqual(restored.id, original.id)
        self.assertEqual(restored.name, original.name)
        self.assertEqual(restored.email, original.email)
        self.assertEqual(restored.role, original.role)
        self.assertEqual(restored.project_ids, original.project_ids)

    def test_from_dict_uses_default_role_when_missing(self):
        """from_dict() should default role to 'Full Stack Developer' if absent."""
        data = {"id": 1, "name": "Bob", "email": "bob@test.com"}
        u = User.from_dict(data)
        self.assertEqual(u.role, "Full Stack Developer")


class TestUserMagicMethods(unittest.TestCase):
    """Tests for __str__ and __repr__."""

    def setUp(self):
        User.next_id = 1

    def test_str_contains_name(self):
        """__str__ should include the developer's name."""
        u = User("Debbie", "debbie@gmail.com", user_id=1)
        self.assertIn("Debbie", str(u))

    def test_str_contains_role(self):
        """__str__ should include the developer's role."""
        u = User("Debbie", "debbie@gmail.com", role="Backend Developer", user_id=1)
        self.assertIn("Backend Developer", str(u))

    def test_repr_starts_with_class_name(self):
        """__repr__ should start with 'User('."""
        u = User("Debbie", "debbie@gmail.com", user_id=1)
        self.assertTrue(repr(u).startswith("User("))


if __name__ == "__main__":
    unittest.main()