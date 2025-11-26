"""Utility functions for imply-druid-mcp."""

import json
from typing import Any

import httpx


def format_http_error(error: httpx.HTTPStatusError) -> str:
    """Format HTTP error for user-friendly display.

    Args:
        error: HTTP error

    Returns:
        Formatted error message
    """
    status_code = error.response.status_code

    if status_code == 401:
        return "Authentication failed. Please check your API key or access token."
    elif status_code == 403:
        return "Permission denied. You don't have access to this resource."
    elif status_code == 404:
        return "Resource not found."
    elif status_code == 429:
        return "Rate limit exceeded. Please try again later."
    elif status_code >= 500:
        return f"Server error ({status_code}). Please try again later."
    else:
        try:
            error_detail = error.response.json()
            return f"HTTP {status_code}: {error_detail}"
        except Exception:
            return f"HTTP {status_code}: {error.response.text}"


def format_json(data: dict[str, Any]) -> str:
    """Format dictionary as JSON for display.

    Args:
        data: Dictionary to format

    Returns:
        Formatted JSON string
    """
    return json.dumps(data, indent=2)
