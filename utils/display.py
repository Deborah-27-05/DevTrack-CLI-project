"""
utils/display.py
All CLI display functions for DevTrack CLI.
Uses the 'rich' library for colour tables and panels.
Falls back to clean plain-text output if rich is not installed.
"""

import re

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import box

    RICH = True
except ImportError:
    RICH = False


# ── Console wrapper ───────────────────────────────────────────────────────────

class _PlainConsole:
    """Minimal Console shim used when rich is unavailable."""

    def print(self, *args, **kwargs):
        text = " ".join(str(a) for a in args)
        text = re.sub(r"\[/?[^\]]*\]", "", text)  # strip rich markup tags
        print(text)


console = Console() if RICH else _PlainConsole()


# ── Feedback helpers ──────────────────────────────────────────────────────────

def success(msg: str):
    """Print a green success message."""
    console.print(f"[bold green]✔[/bold green]  {msg}" if RICH else f"✔  {msg}")


def error(msg: str):
    """Print a red error message."""
    console.print(f"[bold red]✘[/bold red]  {msg}" if RICH else f"✘  {msg}")


def info(msg: str):
    """Print a cyan informational message."""
    console.print(f"[cyan]ℹ[/cyan]  {msg}" if RICH else f"ℹ  {msg}")


# ── Plain-text table fallback ─────────────────────────────────────────────────

def _plain_table(headers: list, rows: list, title: str = ""):
    """Render a simple fixed-width table when rich is unavailable."""
    if title:
        print(f"\n{'─' * 62}")
        print(f"  {title}")
        print(f"{'─' * 62}")
    col_widths = [
        max(len(str(h)), max((len(str(r[i])) for r in rows), default=0))
        for i, h in enumerate(headers)
    ]
    fmt = "  ".join(f"{{:<{w}}}" for w in col_widths)
    print(fmt.format(*headers))
    print("  ".join("─" * w for w in col_widths))
    for row in rows:
        print(fmt.format(*[str(c) for c in row]))
    print()


# ── User table ────────────────────────────────────────────────────────────────

def print_users_table(users, projects):
    """Display all developers in a table."""
    if not users:
        info("No developers registered yet.")
        return

    project_map = {p.id: p.title for p in projects}

    if RICH:
        table = Table(
            title="👩‍💻 Registered Developers",
            box=box.ROUNDED,
            border_style="cyan",
        )
        table.add_column("ID", style="dim", width=5)
        table.add_column("Name", style="bold white")
        table.add_column("Email", style="cyan")
        table.add_column("Role", style="magenta")
        table.add_column("Projects")

        for u in users:
            titles = (
                ", ".join(
                    project_map[pid]
                    for pid in u.project_ids
                    if pid in project_map
                )
                or "—"
            )
            table.add_row(str(u.id), u.name, u.email, u.role, titles)

        console.print(table)
    else:
        rows = [
            [
                u.id,
                u.name,
                u.email,
                u.role,
                ", ".join(
                    project_map[pid]
                    for pid in u.project_ids
                    if pid in project_map
                )
                or "—",
            ]
            for u in users
        ]
        _plain_table(["ID", "Name", "Email", "Role", "Projects"], rows, "Developers")


# ── Project table ─────────────────────────────────────────────────────────────

def print_projects_table(projects, users):
    """Display all projects in a table."""
    if not projects:
        info("No projects found.")
        return

    user_map = {u.id: u.name for u in users}
    status_colors = {
        "Planning": "yellow",
        "In Progress": "blue",
        "Completed": "green",
    }

    if RICH:
        table = Table(
            title="📁 Projects",
            box=box.ROUNDED,
            border_style="green",
        )
        table.add_column("ID", style="dim", width=5)
        table.add_column("Title", style="bold white")
        table.add_column("Owner", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Due Date", style="dim")
        table.add_column("Overdue?", justify="center")

        for p in projects:
            sc = status_colors.get(p.status, "white")
            overdue = "[red]⚠ Yes[/red]" if p.is_overdue() else "[green]No[/green]"
            table.add_row(
                str(p.id),
                p.title,
                user_map.get(p.owner_id, "Unknown"),
                f"[{sc}]{p.status}[/{sc}]",
                p.due_date or "—",
                overdue,
            )
        console.print(table)
    else:
        rows = [
            [
                p.id,
                p.title,
                user_map.get(p.owner_id, "?"),
                p.status,
                p.due_date or "—",
                "Yes" if p.is_overdue() else "No",
            ]
            for p in projects
        ]
        _plain_table(
            ["ID", "Title", "Owner", "Status", "Due Date", "Overdue?"],
            rows,
            "Projects",
        )


# ── Task table ────────────────────────────────────────────────────────────────

def print_tasks_table(tasks, users=None, project_title: str = ""):
    """Display tasks in a table, optionally scoped to a project."""
    if not tasks:
        info("No tasks found.")
        return

    user_map = {u.id: u.name for u in (users or [])}
    title = "📋 Tasks" + (f" — {project_title}" if project_title else "")

    priority_colors = {"High": "red", "Medium": "yellow", "Low": "green"}
    status_colors = {
        "Completed": "green",
        "In Progress": "blue",
        "Pending": "dim",
    }

    if RICH:
        table = Table(title=title, box=box.ROUNDED, border_style="blue")
        table.add_column("ID", style="dim", width=5)
        table.add_column("Title", style="bold white")
        table.add_column("Priority", justify="center")
        table.add_column("Status", justify="center")
        table.add_column("Due Date", style="dim")
        table.add_column("Overdue?", justify="center")
        table.add_column("Contributors", style="cyan")

        for t in tasks:
            pc = priority_colors.get(t.priority, "white")
            sc = status_colors.get(t.status, "white")
            overdue = "[red]⚠ Yes[/red]" if t.is_overdue() else "[green]No[/green]"
            contribs = (
                ", ".join(
                    user_map[uid]
                    for uid in t.contributor_ids
                    if uid in user_map
                )
                or "—"
            )
            table.add_row(
                str(t.id),
                t.title,
                f"[{pc}]{t.priority}[/{pc}]",
                f"[{sc}]{t.status}[/{sc}]",
                t.due_date or "—",
                overdue,
                contribs,
            )
        console.print(table)
    else:
        rows = [
            [
                t.id,
                t.title,
                t.priority,
                t.status,
                t.due_date or "—",
                "Yes" if t.is_overdue() else "No",
                ", ".join(
                    user_map[uid]
                    for uid in t.contributor_ids
                    if uid in user_map
                )
                or "—",
            ]
            for t in tasks
        ]
        _plain_table(
            ["ID", "Title", "Priority", "Status", "Due", "Overdue?", "Contributors"],
            rows,
            title,
        )


# ── Project progress ──────────────────────────────────────────────────────────

def print_project_progress(project, tasks):
    """Show task completion progress for a single project."""
    project_tasks = [t for t in tasks if t.project_id == project.id]
    total = len(project_tasks)
    completed = sum(1 for t in project_tasks if t.status == "Completed")
    pct = int((completed / total * 100)) if total else 0

    if RICH:
        bar_filled = int(pct / 5)      # 20-block bar
        bar = "█" * bar_filled + "░" * (20 - bar_filled)
        color = "green" if pct >= 75 else "yellow" if pct >= 40 else "red"

        console.print(f"\n[bold]{project.title}[/bold]")
        console.print(f"  [{color}]{bar}[/{color}]  [{color}]{pct}%[/{color}]")
        console.print(
            f"  Completed Tasks : [bold]{completed}/{total}[/bold]"
        )
        console.print(f"  Status          : {project.status}\n")
    else:
        bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
        print(f"\n{project.title}")
        print(f"  {bar}  {pct}%")
        print(f"  Completed Tasks : {completed}/{total}")
        print(f"  Status          : {project.status}\n")


# ── Dashboard ─────────────────────────────────────────────────────────────────

def print_dashboard(users, projects, tasks):
    """Display a high-level statistics dashboard."""
    total_users = len(users)
    total_projects = len(projects)
    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t.status == "Completed")
    pending_tasks = sum(1 for t in tasks if t.status == "Pending")
    in_progress_tasks = sum(1 for t in tasks if t.status == "In Progress")
    overdue_tasks = sum(1 for t in tasks if t.is_overdue())
    overdue_projects = sum(1 for p in projects if p.is_overdue())

    if RICH:
        console.print()
        console.print(
            Panel.fit(
                "[bold cyan]⚡ DevTrack CLI — Dashboard[/bold cyan]",
                border_style="cyan",
            )
        )
        stats = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
        stats.add_column(style="bold white")
        stats.add_column(style="cyan", justify="right")

        stats.add_row("👩‍💻 Developers", str(total_users))
        stats.add_row("📁 Total Projects", str(total_projects))
        stats.add_row("📋 Total Tasks", str(total_tasks))
        stats.add_row("✅ Completed Tasks", str(completed_tasks))
        stats.add_row("🔄 In Progress Tasks", str(in_progress_tasks))
        stats.add_row("⏳ Pending Tasks", str(pending_tasks))
        stats.add_row("⚠  Overdue Tasks", f"[red]{overdue_tasks}[/red]")
        stats.add_row("⚠  Overdue Projects", f"[red]{overdue_projects}[/red]")
        console.print(stats)
    else:
        print("\n" + "=" * 42)
        print("  ⚡ DevTrack CLI — Dashboard")
        print("=" * 42)
        print(f"  Developers       : {total_users}")
        print(f"  Total Projects   : {total_projects}")
        print(f"  Total Tasks      : {total_tasks}")
        print(f"  Completed Tasks  : {completed_tasks}")
        print(f"  In Progress      : {in_progress_tasks}")
        print(f"  Pending Tasks    : {pending_tasks}")
        print(f"  Overdue Tasks    : {overdue_tasks}")
        print(f"  Overdue Projects : {overdue_projects}")

    # Project breakdown
    if projects:
        console.print("\n[bold]Project Status Breakdown:[/bold]") if RICH else print("\nProject Status Breakdown:")
        status_map = {}
        for p in projects:
            status_map[p.status] = status_map.get(p.status, 0) + 1
        for status in ["Planning", "In Progress", "Completed"]:
            count = status_map.get(status, 0)
            bar = "█" * count + "░" * max(0, 5 - count)
            print(f"  {status:<14} {bar}  {count}")

    print()