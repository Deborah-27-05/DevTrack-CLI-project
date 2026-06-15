"""
main.py
DevTrack CLI — Entry Point.

All argparse commands are defined and dispatched here.
Data is loaded once at startup and persisted after every write operation.

Usage:
    python main.py <command> [options]
    python main.py --help
"""

import argparse
import logging
import os

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "WARNING"),
    format="%(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ── Models ────────────────────────────────────────────────────────────────────
from models.user import User, VALID_ROLES
from models.project import Project, VALID_STATUSES as PROJECT_STATUSES
from models.task import Task, VALID_STATUSES as TASK_STATUSES, VALID_PRIORITIES

# ── Utils ─────────────────────────────────────────────────────────────────────
from utils.storage import load_all, save_all
from utils.validators import validate_email, validate_date
from utils.display import (
    console, success, error, info,
    print_users_table, print_projects_table, print_tasks_table,
    print_project_progress, print_dashboard,
)


# ═════════════════════════════════════════════════════════════════════════════
# Lookup helpers
# ═════════════════════════════════════════════════════════════════════════════

def _find_user(users: list, name_or_id: str):
    """Find a user by name (case-insensitive) or numeric ID."""
    if name_or_id.isdigit():
        return next((u for u in users if u.id == int(name_or_id)), None)
    return next(
        (u for u in users if u.name.lower() == name_or_id.lower()), None
    )


def _find_project(projects: list, title_or_id: str):
    """Find a project by title (case-insensitive) or numeric ID."""
    if title_or_id.isdigit():
        return next((p for p in projects if p.id == int(title_or_id)), None)
    return next(
        (p for p in projects if p.title.lower() == title_or_id.lower()), None
    )


def _find_task(tasks: list, task_id: str):
    """Find a task by numeric ID."""
    if not task_id.isdigit():
        return None
    return next((t for t in tasks if t.id == int(task_id)), None)


# ═════════════════════════════════════════════════════════════════════════════
# Command handlers
# ═════════════════════════════════════════════════════════════════════════════

# ── add-user ──────────────────────────────────────────────────────────────────

def cmd_add_user(args, users, projects, tasks):
    """Register a new developer."""
    if not validate_email(args.email):
        error(f"Invalid email address: '{args.email}'")
        return
    if any(u.email.lower() == args.email.lower() for u in users):
        error(f"A developer with email '{args.email}' already exists.")
        return
    try:
        user = User(name=args.name, email=args.email, role=args.role)
    except ValueError as exc:
        error(str(exc))
        return
    users.append(user)
    save_all(users, projects, tasks)
    success(f"Developer '{user.name}' registered (ID {user.id}).")


# ── list-users ────────────────────────────────────────────────────────────────

def cmd_list_users(args, users, projects, tasks):
    """Display all registered developers."""
    print_users_table(users, projects)


# ── add-project ───────────────────────────────────────────────────────────────

def cmd_add_project(args, users, projects, tasks):
    """Create a new software project and assign it to a developer."""
    owner = _find_user(users, args.user)
    if not owner:
        error(f"Developer '{args.user}' not found. Register them first with add-user.")
        return
    if any(p.title.lower() == args.title.lower() for p in projects):
        error(f"A project named '{args.title}' already exists.")
        return
    if args.due_date and not validate_date(args.due_date):
        error(f"Invalid date '{args.due_date}'. Use YYYY-MM-DD format.")
        return
    try:
        project = Project(
            title=args.title,
            owner_id=owner.id,
            description=args.description or "",
            due_date=args.due_date,
        )
    except ValueError as exc:
        error(str(exc))
        return
    projects.append(project)
    owner.project_ids.append(project.id)
    save_all(users, projects, tasks)
    success(f"Project '{project.title}' created (ID {project.id}) for {owner.name}.")


# ── list-projects ─────────────────────────────────────────────────────────────

def cmd_list_projects(args, users, projects, tasks):
    """Display all projects, optionally filtered by status."""
    filtered = projects
    if args.status:
        filtered = [p for p in projects if p.status.lower() == args.status.lower()]
    print_projects_table(filtered, users)


# ── update-project ────────────────────────────────────────────────────────────

def cmd_update_project(args, users, projects, tasks):
    """Update a project's status or details."""
    project = _find_project(projects, args.project)
    if not project:
        error(f"Project '{args.project}' not found.")
        return
    if args.status:
        try:
            project.status = args.status
        except ValueError as exc:
            error(str(exc))
            return
    if args.description:
        project.description = args.description
    if args.due_date:
        if not validate_date(args.due_date):
            error(f"Invalid date '{args.due_date}'. Use YYYY-MM-DD format.")
            return
        project.due_date = args.due_date
    save_all(users, projects, tasks)
    success(f"Project '{project.title}' updated.")


# ── user-projects ─────────────────────────────────────────────────────────────

def cmd_user_projects(args, users, projects, tasks):
    """Show all projects owned by a developer."""
    user = _find_user(users, args.user)
    if not user:
        error(f"Developer '{args.user}' not found.")
        return
    user_projects = [p for p in projects if p.owner_id == user.id]
    if not user_projects:
        info(f"No projects found for '{user.name}'.")
    else:
        console.print(f"\n[bold cyan]Projects owned by {user.name}:[/bold cyan]")
        print_projects_table(user_projects, users)


# ── search-project ────────────────────────────────────────────────────────────

def cmd_search_project(args, users, projects, tasks):
    """Search projects by keyword across title and description."""
    kw = args.keyword.lower()
    results = [
        p for p in projects
        if kw in p.title.lower() or kw in p.description.lower()
    ]
    if not results:
        info(f"No projects matching '{args.keyword}'.")
    else:
        print_projects_table(results, users)


# ── add-task ──────────────────────────────────────────────────────────────────

def cmd_add_task(args, users, projects, tasks):
    """Create a task and attach it to a project."""
    project = _find_project(projects, args.project)
    if not project:
        error(f"Project '{args.project}' not found.")
        return

    priority = args.priority or "Medium"
    if priority not in VALID_PRIORITIES:
        error(f"Invalid priority '{priority}'. Choose from: {', '.join(VALID_PRIORITIES)}")
        return

    if args.due_date and not validate_date(args.due_date):
        error(f"Invalid date '{args.due_date}'. Use YYYY-MM-DD format.")
        return

    # Optional contributor assignment
    contributor_ids = []
    if args.assign:
        contributor = _find_user(users, args.assign)
        if not contributor:
            error(f"Developer '{args.assign}' not found.")
            return
        contributor_ids = [contributor.id]

    try:
        task = Task(
            title=args.title,
            project_id=project.id,
            description=args.description or "",
            priority=priority,
            due_date=args.due_date,
            contributor_ids=contributor_ids,
        )
    except ValueError as exc:
        error(str(exc))
        return

    tasks.append(task)
    project.task_ids.append(task.id)
    save_all(users, projects, tasks)
    success(f"Task '{task.title}' (ID {task.id}) added to '{project.title}'.")


# ── list-tasks ────────────────────────────────────────────────────────────────

def cmd_list_tasks(args, users, projects, tasks):
    """List tasks, optionally filtered by project or status."""
    filtered = tasks
    project_title = ""

    if args.project:
        project = _find_project(projects, args.project)
        if not project:
            error(f"Project '{args.project}' not found.")
            return
        filtered = [t for t in tasks if t.project_id == project.id]
        project_title = project.title

    if args.status:
        filtered = [t for t in filtered if t.status.lower() == args.status.lower()]

    if args.priority:
        filtered = [t for t in filtered if t.priority.lower() == args.priority.lower()]

    print_tasks_table(filtered, users, project_title)


# ── update-task ───────────────────────────────────────────────────────────────

def cmd_update_task(args, users, projects, tasks):
    """Update a task's fields."""
    task = _find_task(tasks, args.id)
    if not task:
        error(f"Task with ID '{args.id}' not found.")
        return
    if args.title:
        task.title = args.title
    if args.description:
        task.description = args.description
    if args.status:
        try:
            task.status = args.status
        except ValueError as exc:
            error(str(exc))
            return
    if args.priority:
        try:
            task.priority = args.priority
        except ValueError as exc:
            error(str(exc))
            return
    if args.due_date:
        if not validate_date(args.due_date):
            error(f"Invalid date '{args.due_date}'. Use YYYY-MM-DD.")
            return
        task.due_date = args.due_date
    if args.assign:
        contributor = _find_user(users, args.assign)
        if not contributor:
            error(f"Developer '{args.assign}' not found.")
            return
        task.add_contributor(contributor.id)
    save_all(users, projects, tasks)
    success(f"Task '{task.title}' updated.")


# ── complete-task ─────────────────────────────────────────────────────────────

def cmd_complete_task(args, users, projects, tasks):
    """Mark a task as Completed."""
    task = _find_task(tasks, args.id)
    if not task:
        error(f"Task with ID '{args.id}' not found.")
        return
    if task.status == "Completed":
        info(f"Task '{task.title}' is already completed.")
        return
    task.complete()
    save_all(users, projects, tasks)
    success(f"Task '{task.title}' marked as Completed.")


# ── assign-contributor ────────────────────────────────────────────────────────

def cmd_assign_contributor(args, users, projects, tasks):
    """Add a developer as a contributor to a task."""
    task = _find_task(tasks, args.id)
    if not task:
        error(f"Task with ID '{args.id}' not found.")
        return
    user = _find_user(users, args.user)
    if not user:
        error(f"Developer '{args.user}' not found.")
        return
    if user.id in task.contributor_ids:
        info(f"'{user.name}' is already a contributor to this task.")
        return
    task.add_contributor(user.id)
    save_all(users, projects, tasks)
    success(f"'{user.name}' added as contributor to task '{task.title}'.")


# ── project-progress ──────────────────────────────────────────────────────────

def cmd_project_progress(args, users, projects, tasks):
    """Show task-completion progress for a project."""
    project = _find_project(projects, args.project)
    if not project:
        error(f"Project '{args.project}' not found.")
        return
    print_project_progress(project, tasks)


# ── dashboard ─────────────────────────────────────────────────────────────────

def cmd_dashboard(args, users, projects, tasks):
    """Show the overall statistics dashboard."""
    print_dashboard(users, projects, tasks)


# ── overdue-tasks ─────────────────────────────────────────────────────────────

def cmd_overdue_tasks(args, users, projects, tasks):
    """List all overdue tasks."""
    overdue = [t for t in tasks if t.is_overdue()]
    if not overdue:
        success("No overdue tasks! 🎉")
    else:
        console.print(f"\n[bold red]⚠  {len(overdue)} Overdue Task(s)[/bold red]")
        print_tasks_table(overdue, users)


# ═════════════════════════════════════════════════════════════════════════════
# Argument parser
# ═════════════════════════════════════════════════════════════════════════════

def build_parser() -> argparse.ArgumentParser:
    """Build and return the argparse CLI parser with all subcommands."""
    parser = argparse.ArgumentParser(
        prog="devtrack",
        description="⚡ DevTrack CLI — Developer Project Management",
    )
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")
    sub.required = True

    # ── add-user ──────────────────────────────────────────────────
    p = sub.add_parser("add-user", help="Register a new developer")
    p.add_argument("--name", required=True, help="Developer's full name")
    p.add_argument("--email", required=True, help="Developer's email address")
    p.add_argument(
        "--role",
        default="Full Stack Developer",
        help="Developer role (default: 'Full Stack Developer')",
    )

    # ── list-users ────────────────────────────────────────────────
    sub.add_parser("list-users", help="List all registered developers")

    # ── add-project ───────────────────────────────────────────────
    p = sub.add_parser("add-project", help="Create a new project")
    p.add_argument("--user", required=True, help="Owner name or ID")
    p.add_argument("--title", required=True, help="Project title")
    p.add_argument("--description", help="Short project description")
    p.add_argument("--due-date", dest="due_date", help="Due date (YYYY-MM-DD)")

    # ── list-projects ─────────────────────────────────────────────
    p = sub.add_parser("list-projects", help="List all projects")
    p.add_argument(
        "--status",
        choices=list(PROJECT_STATUSES),
        help="Filter by status",
    )

    # ── update-project ────────────────────────────────────────────
    p = sub.add_parser("update-project", help="Update a project")
    p.add_argument("--project", required=True, help="Project title or ID")
    p.add_argument(
        "--status",
        choices=list(PROJECT_STATUSES),
        help="New status",
    )
    p.add_argument("--description", help="New description")
    p.add_argument("--due-date", dest="due_date", help="New due date (YYYY-MM-DD)")

    # ── user-projects ─────────────────────────────────────────────
    p = sub.add_parser("user-projects", help="Show projects for a developer")
    p.add_argument("--user", required=True, help="Developer name or ID")

    # ── search-project ────────────────────────────────────────────
    p = sub.add_parser("search-project", help="Search projects by keyword")
    p.add_argument("--keyword", required=True, help="Search keyword")

    # ── add-task ──────────────────────────────────────────────────
    p = sub.add_parser("add-task", help="Add a task to a project")
    p.add_argument("--project", required=True, help="Project title or ID")
    p.add_argument("--title", required=True, help="Task title")
    p.add_argument("--description", help="Task description")
    p.add_argument(
        "--priority",
        choices=list(VALID_PRIORITIES),
        default="Medium",
        help="Task priority (default: Medium)",
    )
    p.add_argument("--due-date", dest="due_date", help="Due date (YYYY-MM-DD)")
    p.add_argument("--assign", help="Assign a contributor (name or ID)")

    # ── list-tasks ────────────────────────────────────────────────
    p = sub.add_parser("list-tasks", help="List tasks")
    p.add_argument("--project", help="Filter by project title or ID")
    p.add_argument(
        "--status",
        choices=list(TASK_STATUSES),
        help="Filter by status",
    )
    p.add_argument(
        "--priority",
        choices=list(VALID_PRIORITIES),
        help="Filter by priority",
    )

    # ── update-task ───────────────────────────────────────────────
    p = sub.add_parser("update-task", help="Update a task")
    p.add_argument("--id", required=True, help="Task ID")
    p.add_argument("--title", help="New title")
    p.add_argument("--description", help="New description")
    p.add_argument(
        "--status",
        choices=list(TASK_STATUSES),
        help="New status",
    )
    p.add_argument(
        "--priority",
        choices=list(VALID_PRIORITIES),
        help="New priority",
    )
    p.add_argument("--due-date", dest="due_date", help="New due date (YYYY-MM-DD)")
    p.add_argument("--assign", help="Add a contributor (name or ID)")

    # ── complete-task ─────────────────────────────────────────────
    p = sub.add_parser("complete-task", help="Mark a task as completed")
    p.add_argument("--id", required=True, help="Task ID")

    # ── assign-contributor ────────────────────────────────────────
    p = sub.add_parser("assign-contributor", help="Add a developer to a task")
    p.add_argument("--id", required=True, help="Task ID")
    p.add_argument("--user", required=True, help="Developer name or ID")

    # ── project-progress ──────────────────────────────────────────
    p = sub.add_parser("project-progress", help="Show progress for a project")
    p.add_argument("--project", required=True, help="Project title or ID")

    # ── dashboard ─────────────────────────────────────────────────
    sub.add_parser("dashboard", help="Show overall statistics dashboard")

    # ── overdue-tasks ─────────────────────────────────────────────
    sub.add_parser("overdue-tasks", help="List all overdue tasks")

    return parser


# ═════════════════════════════════════════════════════════════════════════════
# Command dispatch map
# ═════════════════════════════════════════════════════════════════════════════

COMMAND_MAP = {
    "add-user": cmd_add_user,
    "list-users": cmd_list_users,
    "add-project": cmd_add_project,
    "list-projects": cmd_list_projects,
    "update-project": cmd_update_project,
    "user-projects": cmd_user_projects,
    "search-project": cmd_search_project,
    "add-task": cmd_add_task,
    "list-tasks": cmd_list_tasks,
    "update-task": cmd_update_task,
    "complete-task": cmd_complete_task,
    "assign-contributor": cmd_assign_contributor,
    "project-progress": cmd_project_progress,
    "dashboard": cmd_dashboard,
    "overdue-tasks": cmd_overdue_tasks,
}


# ═════════════════════════════════════════════════════════════════════════════
# Entry point
# ═════════════════════════════════════════════════════════════════════════════

def main():
    """Parse CLI arguments, load data, dispatch to the correct handler."""
    parser = build_parser()
    args = parser.parse_args()

    # Load all collections once
    users, projects, tasks = load_all()

    handler = COMMAND_MAP.get(args.command)
    if handler:
        handler(args, users, projects, tasks)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()