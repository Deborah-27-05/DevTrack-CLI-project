"""
utils/validators.py
Shared validation helpers for DevTrack CLI.
"""

import re
from datetime import date


def validate_email(email: str) -> bool:
    """Return True if the string is a valid email address."""
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
    return bool(re.match(pattern, email.strip()))


def validate_date(date_str: str) -> bool:
    """Return True if the string is a valid ISO-8601 date (YYYY-MM-DD)."""
    try:
        date.fromisoformat(date_str)
        return True
    except ValueError:
        return False


def validate_choice(value: str, choices: set) -> bool:
    """Return True if value is one of the allowed choices."""
    return value in choices