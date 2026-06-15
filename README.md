#  DevTrack CLI — Developer Project Management System

A Python-based Command-Line Interface (CLI) application for managing developers, software projects, and tasks. Built for development teams who want a fast, terminal-friendly way to track work without leaving the command line.

---

##  Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
  - [Developer Commands](#developer-commands)
  - [Project Commands](#project-commands)
  - [Task Commands](#task-commands)
  - [Dashboard & Reports](#dashboard--reports)
- [OOP Concepts Demonstrated](#oop-concepts-demonstrated)
- [Running Tests](#running-tests)
- [Known Limitations](#known-limitations)

---

## Project Overview

DevTrack CLI lets you register developers, create projects, assign tasks, track progress, and spot overdue work — all from the terminal. All data is stored locally in JSON files so nothing is lost between sessions.

---

## Features

- **Developer Management** — Register, list, and look up developers by name or ID
- **Project Management** — Create projects, assign owners, update status, search by keyword
- **Task Management** — Create tasks with priorities and due dates, assign contributors
- **Many-to-Many Contributors** — A task can have multiple contributors; a developer can contribute to many tasks
- **Project Progress** — See completed vs total tasks with a visual progress bar
- **Overdue Detection** — Automatically flags tasks and projects past their due date
- **Statistics Dashboard** — At-a-glance summary of the whole system
- **JSON Persistence** — Data loads on startup and saves after every change
- **Rich CLI Output** — Colour-coded tables and panels via the `rich` library (falls back to plain text if not installed)

---

## Project Structure

```
devtrack_cli/
├── main.py                  # CLI entry point — all argparse commands
├── requirements.txt         # Python dependencies
├── README.md
│
├── models/
│   ├── __init__.py
│   ├── person.py            # Base Person class (inherited by User)
│   ├── user.py              # Developer / User model
│   ├── project.py           # Project model
│   └── task.py              # Task model
│
├── utils/
│   ├── __init__.py
│   ├── storage.py           # JSON load and save for all collections
│   ├── validators.py        # Email, date, and choice validators
│   └── display.py           # Rich tables, dashboard, and progress display
│
├── data/
│   ├── users.json           # Persisted developer records
│   ├── projects.json        # Persisted project records
│   └── tasks.json           # Persisted task records
│
└── tests/
    ├── __init__.py
    ├── test_user.py         # Unit tests for User model
    ├── test_project.py      # Unit tests for Project model
    └── test_task.py         # Unit tests for Task model + JSON persistence
```

---

## Installation

### 1. Clone the repository

```bash
git clone git@github.com:Deborah-27-05/DevTrack-CLI-project.git
cd DevTrack-CLI
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Usage

All commands follow this pattern:

```bash
python main.py <command> [options]
python main.py --help
```

---

### Developer Commands

**Register a new developer**
```bash
python main.py add-user --name "Debbie" --email "debbie@gmail.com" --role "Backend Developer"
```

**List all developers**
```bash
python main.py list-users
```

---

### Project Commands

**Create a project**
```bash
python main.py add-project --user "Debbie" --title "Student Portal" --description "School management system"
```

**Create a project with a due date**
```bash
python main.py add-project --user "Debbie" --title "Student Portal" \
  --description "School management system" --due-date "2025-12-31"
```

**List all projects**
```bash
python main.py list-projects
```

**Filter projects by status**
```bash
python main.py list-projects --status "In Progress"
```

**Update a project's status or due date**
```bash
python main.py update-project --project "Student Portal" --status "In Progress"
python main.py update-project --project "Student Portal" --due-date "2026-03-01"
```

**Show all projects owned by a developer**
```bash
python main.py user-projects --user "Debbie"
```

**Search projects by keyword**
```bash
python main.py search-project --keyword "portal"
```

---

### Task Commands

**Add a task to a project**
```bash
python main.py add-task --project "Student Portal" --title "Create Login Page" --priority High
```

**Add a task with a due date and contributor**
```bash
python main.py add-task --project "Student Portal" --title "Design Database Schema" \
  --priority High --due-date "2025-11-15" --assign "Debbie"
```

**List all tasks**
```bash
python main.py list-tasks
```

**List tasks for a specific project**
```bash
python main.py list-tasks --project "Student Portal"
```

**Filter tasks by status or priority**
```bash
python main.py list-tasks --status "Pending"
python main.py list-tasks --priority "High"
```

**Update a task**
```bash
python main.py update-task --id 1 --status "In Progress"
python main.py update-task --id 1 --priority "High" --due-date "2025-12-01"
```

**Assign a contributor to a task**
```bash
python main.py assign-contributor --id 1 --user "Debbie"
```

**Mark a task as complete**
```bash
python main.py complete-task --id 1
```

---

### Dashboard & Reports

**Show project progress**
```bash
python main.py project-progress --project "Student Portal"
```

Example output:
```
Student Portal
  ████████████░░░░░░░░  60%
  Completed Tasks : 3/5
  Status          : In Progress
```

**Show the overall dashboard**
```bash
python main.py dashboard
```

Example output:
```
⚡ DevTrack CLI — Dashboard
  Developers        : 3
  Total Projects    : 5
  Total Tasks       : 18
  Completed Tasks   : 11
  In Progress Tasks : 4
  Pending Tasks     : 3
  Overdue Tasks     : 2
  Overdue Projects  : 1
```

**List all overdue tasks**
```bash
python main.py overdue-tasks
```

---

## OOP Concepts Demonstrated

| Concept | Where |
|---|---|
| **Inheritance** | `User` extends `Person` |
| **Encapsulation** | `@property` setters validate `email`, `role`, `status`, `priority` |
| **Class Attributes** | `User.next_id`, `Project.next_id`, `Task.next_id` — auto-increment IDs |
| **Class Methods** | `from_dict()` on all models — create objects from JSON |
| **`__str__`** | Clean single-line summary on all models |
| **`__repr__`** | Developer-friendly representation on all models |

---

## Running Tests

```bash
# Using unittest (built-in, no install needed)
python -m unittest discover tests -v

# Using pytest (if installed)
pytest tests/ -v
```

---

## Known Limitations

- Project titles and developer names must be unique — they are used as identifiers in commands
- No authentication or multi-user sessions — all data lives in a single shared JSON store
- The `rich` library is required for colour output; if unavailable the app falls back to plain-text tables automatically
- Date validation accepts any valid YYYY-MM-DD string but does not check for logical ranges (e.g. dates in the past)
- No undo / history — changes are saved immediately after every command

---

## Dependencies

| Package | Purpose |
|---|---|
| `rich` | Colour tables, panels, and progress display |

All other code uses Python's standard library: `argparse`, `json`, `logging`, `re`, `datetime`, `pathlib`, `unittest`.

---

## License

MIT