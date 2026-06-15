"""
tests/test_project.py
Unit tests for the Project model.
Tests cover creation, validation, progress, overdue detection, and serialisation.
"""

import unittest
from datetime import date, timedelta
from models.project import Project


class TestProjectCreation(unittest.TestCase):
    """Tests for creating Project instances."""

    def setUp(self):
        """Reset the class-level ID counter before each test."""
        Project.next_id = 1

    def test_create_project_with_required_fields(self):
        """A project created with required fields should store them correctly."""
        p = Project(title="Student Portal", owner_id=1)
        self.assertEqual(p.title, "Student Portal")
        self.assertEqual(p.owner_id, 1)

    def test_project_id_is_assigned_automatically(self):
        """A new project should receive a unique integer ID."""
        p = Project(title="Student Portal", owner_id=1)
        self.assertIsInstance(p.id, int)
        self.assertGreater(p.id, 0)

    def test_project_ids_auto_increment(self):
        """Each new project should get an ID one higher than the previous."""
        p1 = Project("Project A", owner_id=1)
        p2 = Project("Project B", owner_id=1)
        self.assertEqual(p2.id, p1.id + 1)

    def test_default_status_is_planning(self):
        """Status should default to 'Planning' when not provided."""
        p = Project("Student Portal", owner_id=1)
        self.assertEqual(p.status, "Planning")

    def test_task_ids_defaults_to_empty_list(self):
        """task_ids should be an empty list when not provided."""
        p = Project("Student Portal", owner_id=1)
        self.assertEqual(p.task_ids, [])

    def test_description_defaults_to_empty_string(self):
        """description should default to an empty string."""
        p = Project("Student Portal", owner_id=1)
        self.assertEqual(p.description, "")


class TestProjectValidation(unittest.TestCase):
    """Tests for Project field validation via property setters."""

    def setUp(self):
        Project.next_id = 1

    def test_valid_status_values_are_accepted(self):
        """All three valid status values should be accepted without error."""
        for status in ("Planning", "In Progress", "Completed"):
            p = Project("Test", owner_id=1, status=status)
            self.assertEqual(p.status, status)

    def test_invalid_status_raises_value_error(self):
        """An unrecognised status should raise a ValueError."""
        with self.assertRaises(ValueError):
            Project("Test", owner_id=1, status="Archived")

    def test_status_setter_raises_on_invalid_value(self):
        """Assigning an invalid status via the setter should raise ValueError."""
        p = Project("Test", owner_id=1)
        with self.assertRaises(ValueError):
            p.status = "Unknown"

    def test_status_can_be_updated_via_setter(self):
        """Status should be updatable to any valid value via the setter."""
        p = Project("Test", owner_id=1)
        p.status = "In Progress"
        self.assertEqual(p.status, "In Progress")


class TestProjectOverdue(unittest.TestCase):
    """Tests for overdue detection logic."""

    def setUp(self):
        Project.next_id = 1

    def test_project_with_past_due_date_is_overdue(self):
        """A non-completed project with a past due date should be overdue."""
        past = (date.today() - timedelta(days=1)).isoformat()
        p = Project("Test", owner_id=1, due_date=past, status="In Progress")
        self.assertTrue(p.is_overdue())

    def test_completed_project_is_never_overdue(self):
        """A completed project should never be flagged as overdue."""
        past = (date.today() - timedelta(days=1)).isoformat()
        p = Project("Test", owner_id=1, due_date=past, status="Completed")
        self.assertFalse(p.is_overdue())

    def test_project_with_future_due_date_is_not_overdue(self):
        """A project with a future due date should not be overdue."""
        future = (date.today() + timedelta(days=7)).isoformat()
        p = Project("Test", owner_id=1, due_date=future)
        self.assertFalse(p.is_overdue())

    def test_project_with_no_due_date_is_not_overdue(self):
        """A project without a due date should not be flagged as overdue."""
        p = Project("Test", owner_id=1)
        self.assertFalse(p.is_overdue())


class TestProjectSerialisation(unittest.TestCase):
    """Tests for to_dict() and from_dict() round-trips."""

    def setUp(self):
        Project.next_id = 1

    def test_to_dict_contains_all_fields(self):
        """to_dict() should include all project fields."""
        p = Project("Student Portal", owner_id=1, description="Test",
                    due_date="2025-12-31", status="In Progress",
                    task_ids=[1, 2], project_id=99)
        d = p.to_dict()
        self.assertEqual(d["id"], 99)
        self.assertEqual(d["title"], "Student Portal")
        self.assertEqual(d["owner_id"], 1)
        self.assertEqual(d["description"], "Test")
        self.assertEqual(d["due_date"], "2025-12-31")
        self.assertEqual(d["status"], "In Progress")
        self.assertEqual(d["task_ids"], [1, 2])

    def test_from_dict_restores_all_fields(self):
        """from_dict() should recreate a Project with matching attributes."""
        data = {
            "id": 10,
            "title": "Dev Portal",
            "owner_id": 3,
            "description": "Internal tool",
            "due_date": "2026-01-01",
            "status": "Planning",
            "task_ids": [5, 6, 7],
        }
        p = Project.from_dict(data)
        self.assertEqual(p.id, 10)
        self.assertEqual(p.title, "Dev Portal")
        self.assertEqual(p.task_ids, [5, 6, 7])

    def test_round_trip_preserves_data(self):
        """Serialising then deserialising should produce an identical object."""
        original = Project("Student Portal", owner_id=2,
                           description="School system", status="In Progress",
                           task_ids=[1, 2, 3], project_id=5)
        restored = Project.from_dict(original.to_dict())
        self.assertEqual(restored.id, original.id)
        self.assertEqual(restored.title, original.title)
        self.assertEqual(restored.status, original.status)
        self.assertEqual(restored.task_ids, original.task_ids)


class TestProjectMagicMethods(unittest.TestCase):
    """Tests for __str__ and __repr__."""

    def setUp(self):
        Project.next_id = 1

    def test_str_contains_title(self):
        """__str__ should include the project title."""
        p = Project("Student Portal", owner_id=1, project_id=1)
        self.assertIn("Student Portal", str(p))

    def test_str_contains_status(self):
        """__str__ should include the current status."""
        p = Project("Student Portal", owner_id=1, status="In Progress", project_id=1)
        self.assertIn("In Progress", str(p))

    def test_repr_starts_with_class_name(self):
        """__repr__ should start with 'Project('."""
        p = Project("Student Portal", owner_id=1, project_id=1)
        self.assertTrue(repr(p).startswith("Project("))


if __name__ == "__main__":
    unittest.main()