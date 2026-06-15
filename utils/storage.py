"""
utils/storage.py
JSON persistence layer for DevTrack CLI.
Handles all load and save operations for users, projects, and tasks.
"""

import json
import logging
from pathlib import Path

from models.user import User
from models.project import Project
from models.task import Task
from typing import List, Tuple

logger = logging.getLogger(__name__)

# ── File paths ────────────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
USERS_FILE = DATA_DIR / "users.json"
PROJECTS_FILE = DATA_DIR / "projects.json"
TASKS_FILE = DATA_DIR / "tasks.json"


def _ensure_data_dir():
    """Create the data/ directory if it does not exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


# ── Generic helpers ───────────────────────────────────────────────────────────

def _read_json(filepath: Path) -> list:
    """
    Read and parse a JSON file.

    Returns an empty list if the file does not exist or contains invalid JSON.
    """
    if not filepath.exists():
        logger.debug("File not found, returning []: %s", filepath)
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError as exc:
        logger.error("Malformed JSON in %s: %s", filepath, exc)
        return []
    except OSError as exc:
        logger.error("Cannot read %s: %s", filepath, exc)
        return []


def _write_json(filepath: Path, data: list):
    """
    Serialise a list of dicts and write it to a JSON file.
    Creates the data directory if needed.
    """
    _ensure_data_dir()
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.debug("Saved %d records to %s", len(data), filepath)
    except OSError as exc:
        logger.error("Cannot write to %s: %s", filepath, exc)


# ── Users ─────────────────────────────────────────────────────────────────────
from typing import List
def load_users() -> List[User]:
    """Load all users from users.json and return as User objects."""
    return [User.from_dict(d) for d in _read_json(USERS_FILE)]


def save_users(users: List[User]):
    """Persist a list of User objects to users.json."""
    _write_json(USERS_FILE, [u.to_dict() for u in users])


# ── Projects ──────────────────────────────────────────────────────────────────

def load_projects() -> List[Project]:
    """Load all projects from projects.json and return as Project objects."""
    return [Project.from_dict(d) for d in _read_json(PROJECTS_FILE)]


def save_projects(projects: List[Project]):
    """Persist a list of Project objects to projects.json."""
    _write_json(PROJECTS_FILE, [p.to_dict() for p in projects])


# ── Tasks ─────────────────────────────────────────────────────────────────────

def load_tasks() -> List[Task]:
    """Load all tasks from tasks.json and return as Task objects."""
    return [Task.from_dict(d) for d in _read_json(TASKS_FILE)]


def save_tasks(tasks: List[Task]):
    """Persist a list of Task objects to tasks.json."""
    _write_json(TASKS_FILE, [t.to_dict() for t in tasks])


# ── Convenience ───────────────────────────────────────────────────────────────

def load_all() -> Tuple[List[User], List[Project], List[Task]]:
    """Load all three collections at once. Called once at CLI startup."""
    _ensure_data_dir()
    return load_users(), load_projects(), load_tasks()


def save_all(users: List[User], projects: List[Project], tasks: List[Task]):
    """Persist all three collections. Called after every mutating command."""
    save_users(users)
    save_projects(projects)
    save_tasks(tasks)