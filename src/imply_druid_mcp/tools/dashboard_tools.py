"""Dashboard read-only tools for MCP."""

import logging
from typing import Any

import httpx
from mcp.types import Tool, TextContent

from ..client import ImplyClient
from ..config import get_config
from ..utils import format_http_error, format_json

logger = logging.getLogger("imply-druid-mcp")

# Tool names for this module
DASHBOARD_TOOL_NAMES = ["list_dashboards", "get_dashboard"]


def get_dashboard_tools() -> list[Tool]:
    """Get list of dashboard tools.

    Returns:
        List of dashboard tool definitions
    """
    return [
        Tool(
            name="list_dashboards",
            description="List all dashboards in the Imply project with their metadata.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="get_dashboard",
            description="Get detailed information about a specific dashboard including its configuration.",
            inputSchema={
                "type": "object",
                "properties": {
                    "dashboard_id": {
                        "type": "string",
                        "description": "ID of the dashboard",
                    },
                },
                "required": ["dashboard_id"],
            },
        ),
    ]


async def handle_dashboard_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls for dashboard operations.

    Args:
        name: Tool name
        arguments: Tool arguments

    Returns:
        Tool execution results
    """
    config = get_config()

    try:
        async with ImplyClient(config) as client:
            if name == "list_dashboards":
                result = await client.list_dashboards()
                dashboards = result.get("values", [])

                if not dashboards:
                    return [TextContent(type="text", text="No dashboards found in the project.")]

                # Format dashboard list
                dashboard_list = "\n".join(
                    [
                        f"- {dashboard.get('title', 'Untitled')} (ID: {dashboard.get('id', 'unknown')})"
                        for dashboard in dashboards
                    ]
                )

                return [
                    TextContent(
                        type="text",
                        text=f"Dashboards in project ({len(dashboards)} total):\n\n{dashboard_list}",
                    )
                ]

            elif name == "get_dashboard":
                dashboard_id = arguments.get("dashboard_id")
                if not dashboard_id:
                    raise ValueError("dashboard_id is required")

                result = await client.get_dashboard(dashboard_id)
                return [
                    TextContent(
                        type="text",
                        text=f"Dashboard details for '{dashboard_id}':\n\n{format_json(result)}",
                    )
                ]

            else:
                raise ValueError(f"Unknown tool: {name}")

    except httpx.HTTPStatusError as e:
        error_msg = format_http_error(e)
        return [TextContent(type="text", text=f"Error: {error_msg}")]
    except ValueError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except Exception as e:
        logger.error(f"Dashboard tool error: {e}", exc_info=True)
        return [
            TextContent(
                type="text",
                text="Error: An unexpected error occurred while processing the request.",
            )
        ]
