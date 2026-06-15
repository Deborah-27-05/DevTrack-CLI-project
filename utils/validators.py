# """
# utils/validators.py
# Shared validation helpers for DevTrack CLI.
# """

# import re
# from datetime import date


# def validate_email(email: str) -> bool:
#     """Return True if the string is a valid email address."""
#     pattern = r"^[\w\.-]+@[\w-]+\.[a-zA-Z]{2,}$"
#     return bool(re.match(pattern, email.strip()))


# def validate_date(date_str: str) -> bool:
#     """Return True if the string is a valid ISO-8601 date (YYYY-MM-DD)."""
#     try:
#         date.fromisoformat(date_str)
#         return True
#     except ValueError:
#         return False


# def validate_choice(value: str, choices: set) -> bool:
#     """Return True if value is one of the allowed choices."""
#     return value.strip() in choices

# def validate_task(title: str, description: str, due_date: str, priority: str) -> tuple:
#     title = title.strip()
#     description = description.strip()

#     if not title:
#         raise ValueError("Task title cannot be empty")

#     if priority.strip() not in {"Low", "Medium", "High"}:
#         raise ValueError("Invalid priority")

#     if not validate_date(due_date):
#         raise ValueError("Invalid due date")

#     return {
#         "title": title,
#         "description": description,
#         "due_date": due_date,
#         "priority": priority
#     }

"""
utils/validators.py
Shared validation helpers for DevTrack CLI.
"""

import re
from datetime import date


# ─────────────────────────────────────────────
# Basic Validators
# ─────────────────────────────────────────────

def validate_email(email: str) -> bool:
    """Check if email is in a valid format."""
    if not isinstance(email, str):
        return False

    email = email.strip()
    pattern = r"^[\w\.-]+@[\w-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_date(date_str: str) -> bool:
    """Check if string is a valid YYYY-MM-DD date."""
    if not isinstance(date_str, str):
        return False

    try:
        date.fromisoformat(date_str.strip())
        return True
    except (ValueError, AttributeError):
        return False


def validate_choice(value: str, choices: set) -> bool:
    """Check if a value is within allowed choices."""
    if not isinstance(value, str):
        return False

    return value.strip() in choices


# ─────────────────────────────────────────────
# Task Validator (STRICT ENTRY GATE)
# ─────────────────────────────────────────────

def validate_task(title: str, description: str, due_date: str, priority: str):
    title = title.strip()
    description = description.strip()

    if not title:
        raise ValueError("Task title cannot be empty")

    if not description:
        raise ValueError("Task description cannot be empty")

    if priority.strip() not in {"Low", "Medium", "High"}:
        raise ValueError("Invalid priority")

    if not validate_date(due_date):
        raise ValueError("Invalid due date")

    return title, description, due_date, priority.strip()