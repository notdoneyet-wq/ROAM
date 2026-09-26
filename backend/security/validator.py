"""
ROAM — Tool Argument Validator
Validates arguments passed to tools to prevent abuse.
"""

from __future__ import annotations

import re
from urllib.parse import urlparse


def validate_tool_args(tool_name: str, args: dict) -> tuple[bool, list[str]]:
    """
    Validate tool arguments for safety and correctness.
    Returns (is_valid, list_of_issues).
    """
    issues: list[str] = []

    # General string length validation
    for key, value in args.items():
        if isinstance(value, str) and len(value) > 1000:
            issues.append(f"Argument '{key}' exceeds maximum length of 1000 characters")

    # Numeric range validation
    numeric_ranges = {
        "duration_days": (1, 30),
        "travellers": (1, 20),
        "budget_inr": (1000, 10_000_000),
        "budget_per_night": (100, 100_000),
        "month": (1, 12),
        "buffer_percent": (0, 0.5),
    }

    for key, (min_val, max_val) in numeric_ranges.items():
        if key in args:
            try:
                val = float(args[key])
                if val < min_val or val > max_val:
                    issues.append(f"Argument '{key}' = {val} is outside valid range [{min_val}, {max_val}]")
            except (ValueError, TypeError):
                issues.append(f"Argument '{key}' must be a number")

    # URL validation
    if "url" in args:
        url = args["url"]
        if not _is_safe_url(url):
            issues.append(f"URL '{url[:50]}...' is not allowed")

    # Destination validation — prevent path traversal
    for key in ("destination", "origin"):
        if key in args:
            val = str(args[key])
            if any(c in val for c in ["../", "..\\", "/etc/", "~/"]):
                issues.append(f"Argument '{key}' contains path traversal characters")
            if len(val) > 100:
                issues.append(f"Argument '{key}' is unreasonably long")

    return len(issues) == 0, issues


def _is_safe_url(url: str) -> bool:
    """Check if a URL is safe to access."""
    try:
        parsed = urlparse(url)
    except Exception:
        return False

    # Must have a scheme
    if parsed.scheme not in ("http", "https"):
        return False

    # No private/internal IPs
    hostname = parsed.hostname or ""
    private_patterns = [
        r"^localhost$",
        r"^127\.",
        r"^10\.",
        r"^172\.(1[6-9]|2[0-9]|3[01])\.",
        r"^192\.168\.",
        r"^0\.0\.0\.0$",
        r"^::1$",
        r"^fc00:",
        r"^fd00:",
        r"\.local$",
        r"\.internal$",
    ]
    for pattern in private_patterns:
        if re.match(pattern, hostname, re.IGNORECASE):
            return False

    # No suspicious ports
    port = parsed.port
    if port and port not in (80, 443, 8080, 8443):
        return False

    return True


def validate_api_key_not_exposed(response_data: dict | str) -> bool:
    """
    Check that no API keys or secrets are accidentally included in response data.
    Returns True if safe, False if secrets detected.
    """
    text = str(response_data)
    
    # Patterns that look like API keys
    secret_patterns = [
        r"[A-Za-z0-9_-]{30,}",  # Long alphanumeric strings (potential keys)
        r"sk-[A-Za-z0-9]{20,}",  # OpenAI-style keys
        r"AIza[A-Za-z0-9_-]{30,}",  # Google API keys
        r"AKIA[A-Z0-9]{16}",  # AWS keys
    ]
    
    # Keyword indicators
    secret_keywords = [
        "api_key", "api-key", "apikey", "secret_key", "secret-key",
        "access_token", "auth_token", "password", "private_key",
    ]
    
    text_lower = text.lower()
    for keyword in secret_keywords:
        if keyword in text_lower:
            # Check if it's a value assignment, not just a label
            if re.search(rf'{keyword}\s*[=:]\s*["\']?\w{{10,}}', text_lower):
                return False

    return True
