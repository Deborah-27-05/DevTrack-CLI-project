"""
tests/test_task.py
Unit tests for the Task model and JSON persistence.
Tests cover creation, validation, completion, overdue detection,
contributor management, serialisation, and a full JSON file round-trip.
"""

import json
import os
import tempfile
import unittest
from datetime import date, timedelta

from models.task import Task
from models.user import User
from models.project import Project


class TestTaskCreation(unittest.TestCase):
    """Tests for creating Task instances."""

    def setUp(self):
        """Reset the class-level ID counter before each test."""
        Task.next_id = 1

    def test_create_task_with_required_fields(self):
        """A task created with required fields should store them correctly."""
        t = Task(title="Create Login Page", project_id=1)
        self.assertEqual(t.title, "Create Login Page")
        self.assertEqual(t.project_id, 1)

    def test_task_id_is_assigned_automatically(self):
        """A new task should receive a unique integer ID."""
        t = Task(title="Create Login Page", project_id=1)
        self.assertIsInstance(t.id, int)
        self.assertGreater(t.id, 0)

    def test_task_ids_auto_increment(self):
        """Each new task should get an ID one higher than the previous."""
        t1 = Task("Task A", project_id=1)
        t2 = Task("Task B", project_id=1)
        self.assertEqual(t2.id, t1.id + 1)

    def test_default_status_is_pending(self):
        """Status should default to 'Pending' when not provided."""
        t = Task("Create Login Page", project_id=1)
        self.assertEqual(t.status, "Pending")

    def test_default_priority_is_medium(self):
        """Priority should default to 'Medium' when not provided."""
        t = Task("Create Login Page", project_id=1)
        self.assertEqual(t.priority, "Medium")

    def test_contributor_ids_defaults_to_empty_list(self):
        """contributor_ids should be an empty list when not provided."""
        t = Task("Create Login Page", project_id=1)
        self.assertEqual(t.contributor_ids, [])

    def test_description_defaults_to_empty_string(self):
        """description should default to an empty string."""
        t = Task("Create Login Page", project_id=1)
        self.assertEqual(t.description, "")


class TestTaskValidation(unittest.TestCase):
    """Tests for Task field validation via property setters."""

    def setUp(self):
        Task.next_id = 1

    def test_valid_status_values_are_accepted(self):
        """All three valid status values should be accepted without error."""
        for status in ("Pending", "In Progress", "Completed"):
            t = Task("Test", project_id=1, status=status)
            self.assertEqual(t.status, status)

    def test_invalid_status_raises_value_error(self):
        """An unrecognised status should raise a ValueError."""
        with self.assertRaises(ValueError):
            Task("Test", project_id=1, status="Done")

    def test_valid_priority_values_are_accepted(self):
        """All three valid priority values should be accepted without error."""
        for priority in ("Low", "Medium", "High"):
            t = Task("Test", project_id=1, priority=priority)
            self.assertEqual(t.priority, priority)

    def test_invalid_priority_raises_value_error(self):
        """An unrecognised priority should raise a ValueError."""
        with self.assertRaises(ValueError):
            Task("Test", project_id=1, priority="Critical")

    def test_status_setter_raises_on_invalid_value(self):
        """Assigning an invalid status via the setter should raise ValueError."""
        t = Task("Test", project_id=1)
        with self.assertRaises(ValueError):
            t.status = "Cancelled"

    def test_priority_setter_raises_on_invalid_value(self):
        """Assigning an invalid priority via the setter should raise ValueError."""
        t = Task("Test", project_id=1)
        with self.assertRaises(ValueError):
            t.priority = "Urgent"


class TestTaskCompletion(unittest.TestCase):
    """Tests for task completion behaviour."""

    def setUp(self):
        Task.next_id = 1

    def test_complete_sets_status_to_completed(self):
        """Calling complete() should set status to 'Completed'."""
        t = Task("Create Login Page", project_id=1)
        t.complete()
        self.assertEqual(t.status, "Completed")

    def test_complete_works_from_any_status(self):
        """complete() should work regardless of the starting status."""
        t = Task("Test", project_id=1, status="In Progress")
        t.complete()
        self.assertEqual(t.status, "Completed")

    def test_status_can_be_set_via_setter(self):
        """Status should be updatable to any valid value via the setter."""
        t = Task("Test", project_id=1)
        t.status = "In Progress"
        self.assertEqual(t.status, "In Progress")


class TestTaskOverdue(unittest.TestCase):
    """Tests for overdue detection logic."""

    def setUp(self):
        Task.next_id = 1

    def test_task_with_past_due_date_is_overdue(self):
        """A non-completed task with a past due date should be overdue."""
        past = (date.today() - timedelta(days=1)).isoformat()
        t = Task("Test", project_id=1, due_date=past, status="Pending")
        self.assertTrue(t.is_overdue())

    def test_completed_task_is_never_overdue(self):
        """A completed task should never be flagged as overdue."""
        past = (date.today() - timedelta(days=1)).isoformat()
        t = Task("Test", project_id=1, due_date=past, status="Completed")
        self.assertFalse(t.is_overdue())

    def test_task_with_future_due_date_is_not_overdue(self):
        """A task with a future due date should not be overdue."""
        future = (date.today() + timedelta(days=7)).isoformat()
        t = Task("Test", project_id=1, due_date=future)
        self.assertFalse(t.is_overdue())

    def test_task_with_no_due_date_is_not_overdue(self):
        """A task without a due date should not be flagged as overdue."""
        t = Task("Test", project_id=1)
        self.assertFalse(t.is_overdue())


class TestTaskContributors(unittest.TestCase):
    """Tests for contributor management on tasks."""

    def setUp(self):
        Task.next_id = 1

    def test_add_contributor_stores_user_id(self):
        """add_contributor() should add the user ID to contributor_ids."""
        t = Task("Test", project_id=1)
        t.add_contributor(42)
        self.assertIn(42, t.contributor_ids)

    def test_add_contributor_no_duplicates(self):
        """Adding the same contributor twice should not create a duplicate."""
        t = Task("Test", project_id=1)
        t.add_contributor(42)
        t.add_contributor(42)
        self.assertEqual(t.contributor_ids.count(42), 1)

    def test_multiple_contributors_can_be_added(self):
        """Multiple different contributors should all be stored."""
        t = Task("Test", project_id=1)
        t.add_contributor(1)
        t.add_contributor(2)
        t.add_contributor(3)
        self.assertEqual(len(t.contributor_ids), 3)


class TestTaskSerialisation(unittest.TestCase):
    """Tests for to_dict() and from_dict() round-trips."""

    def setUp(self):
        Task.next_id = 1

    def test_to_dict_contains_all_fields(self):
        """to_dict() should include all task fields."""
        t = Task("Create Login Page", project_id=5,
                 description="Build the auth UI", priority="High",
                 status="In Progress", due_date="2025-12-31",
                 contributor_ids=[1, 2], task_id=99)
        d = t.to_dict()
        self.assertEqual(d["id"], 99)
        self.assertEqual(d["title"], "Create Login Page")
        self.assertEqual(d["project_id"], 5)
        self.assertEqual(d["priority"], "High")
        self.assertEqual(d["status"], "In Progress")
        self.assertEqual(d["due_date"], "2025-12-31")
        self.assertEqual(d["contributor_ids"], [1, 2])

    def test_from_dict_restores_all_fields(self):
        """from_dict() should recreate a Task with matching attributes."""
        data = {
            "id": 7,
            "title": "Design Database",
            "project_id": 3,
            "description": "ERD and schema",
            "priority": "High",
            "status": "Pending",
            "due_date": "2025-11-30",
            "contributor_ids": [4, 5],
        }
        t = Task.from_dict(data)
        self.assertEqual(t.id, 7)
        self.assertEqual(t.title, "Design Database")
        self.assertEqual(t.priority, "High")
        self.assertEqual(t.contributor_ids, [4, 5])

    def test_round_trip_preserves_data(self):
        """Serialising then deserialising should produce an identical object."""
        original = Task("Deploy to Production", project_id=2,
                        priority="High", status="In Progress",
                        due_date="2025-10-01", contributor_ids=[1, 3],
                        task_id=15)
        restored = Task.from_dict(original.to_dict())
        self.assertEqual(restored.id, original.id)
        self.assertEqual(restored.title, original.title)
        self.assertEqual(restored.priority, original.priority)
        self.assertEqual(restored.status, original.status)
        self.assertEqual(restored.contributor_ids, original.contributor_ids)

    def test_from_dict_uses_default_status_when_missing(self):
        """from_dict() should default status to 'Pending' if absent."""
        data = {"id": 1, "title": "Test Task", "project_id": 1}
        t = Task.from_dict(data)
        self.assertEqual(t.status, "Pending")

    def test_from_dict_uses_default_priority_when_missing(self):
        """from_dict() should default priority to 'Medium' if absent."""
        data = {"id": 1, "title": "Test Task", "project_id": 1}
        t = Task.from_dict(data)
        self.assertEqual(t.priority, "Medium")


class TestJSONFilePersistence(unittest.TestCase):
    """
    Integration tests for JSON file read/write.
    These tests verify that objects survive a full disk round-trip.
    """

    def setUp(self):
        User.next_id = 1
        Project.next_id = 1
        Task.next_id = 1

    def _write_and_read(self, objects):
        """Helper: serialise objects to a temp file, read them back."""
        data = [o.to_dict() for o in objects]
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(data, f, indent=2)
            path = f.name
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        finally:
            os.unlink(path)

    def test_user_json_round_trip(self):
        """Users should serialise to JSON and deserialise back correctly."""
        users = [
            User("Debbie", "debbie@gmail.com", role="Backend Developer", user_id=1,
                 project_ids=[1, 2]),
            User("Alice", "alice@dev.io", role="QA Engineer", user_id=2),
        ]
        loaded = self._write_and_read(users)
        restored = [User.from_dict(d) for d in loaded]

        self.assertEqual(len(restored), 2)
        self.assertEqual(restored[0].name, "Debbie")
        self.assertEqual(restored[0].role, "Backend Developer")
        self.assertEqual(restored[0].project_ids, [1, 2])
        self.assertEqual(restored[1].email, "alice@dev.io")

    def test_project_json_round_trip(self):
        """Projects should serialise to JSON and deserialise back correctly."""
        projects = [
            Project("Student Portal", owner_id=1, description="School system",
                    status="In Progress", task_ids=[1, 2, 3], project_id=10),
            Project("API Gateway", owner_id=2, status="Planning", project_id=11),
        ]
        loaded = self._write_and_read(projects)
        restored = [Project.from_dict(d) for d in loaded]

        self.assertEqual(len(restored), 2)
        self.assertEqual(restored[0].title, "Student Portal")
        self.assertEqual(restored[0].task_ids, [1, 2, 3])
        self.assertEqual(restored[1].status, "Planning")

    def test_task_json_round_trip(self):
        """Tasks should serialise to JSON and deserialise back correctly."""
        tasks = [
            Task("Create Login Page", project_id=1, priority="High",
                 status="Completed", task_id=1),
            Task("Write Unit Tests", project_id=1, priority="Medium",
                 status="In Progress", contributor_ids=[2, 3], task_id=2),
        ]
        loaded = self._write_and_read(tasks)
        restored = [Task.from_dict(d) for d in loaded]

        self.assertEqual(len(restored), 2)
        self.assertEqual(restored[0].status, "Completed")
        self.assertEqual(restored[1].contributor_ids, [2, 3])

    def test_empty_list_writes_and_reads_back_as_empty(self):
        """An empty list should persist and reload as an empty list."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump([], f)
            path = f.name
        try:
            with open(path, "r", encoding="utf-8") as f:
                result = json.load(f)
            self.assertEqual(result, [])
        finally:
            os.unlink(path)

    def test_malformed_json_returns_empty_list(self):
        """Storage should return an empty list for files with malformed JSON."""
        from utils.storage import _read_json
        from pathlib import Path

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            f.write("{ this is not valid json !!!")
            path = f.name
        try:
            result = _read_json(Path(path))
            self.assertEqual(result, [])
        finally:
            os.unlink(path)

    def test_missing_file_returns_empty_list(self):
        """Storage should return an empty list when the file does not exist."""
        from utils.storage import _read_json
        from pathlib import Path

        result = _read_json(Path("/tmp/devtrack_nonexistent_file_xyz.json"))
        self.assertEqual(result, [])


class TestTaskMagicMethods(unittest.TestCase):
    """Tests for __str__ and __repr__."""

    def setUp(self):
        Task.next_id = 1

    def test_str_contains_title(self):
        """__str__ should include the task title."""
        t = Task("Create Login Page", project_id=1, task_id=1)
        self.assertIn("Create Login Page", str(t))

    def test_str_contains_priority(self):
        """__str__ should include the priority level."""
        t = Task("Create Login Page", project_id=1, priority="High", task_id=1)
        self.assertIn("High", str(t))

    def test_str_contains_status(self):
        """__str__ should include the current status."""
        t = Task("Create Login Page", project_id=1, status="In Progress", task_id=1)
        self.assertIn("In Progress", str(t))

    def test_repr_starts_with_class_name(self):
        """__repr__ should start with 'Task('."""
        t = Task("Create Login Page", project_id=1, task_id=1)
        self.assertTrue(repr(t).startswith("Task("))


if __name__ == "__main__":
    unittest.main()