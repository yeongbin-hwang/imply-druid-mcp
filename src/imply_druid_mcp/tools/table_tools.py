"""Table read-only tools for MCP."""

from typing import Any

import httpx
from mcp.types import Tool, TextContent

from ..client import ImplyClient
from ..config import get_config
from ..utils import format_http_error, format_json


def get_table_tools() -> list[Tool]:
    """Get list of table tools.

    Returns:
        List of table tool definitions
    """
    return [
        Tool(
            name="list_tables",
            description="List all tables in the Druid project with their metadata.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="get_table_schema",
            description="Get detailed schema information for a specific table.",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the table",
                    },
                },
                "required": ["table_name"],
            },
        ),
    ]


async def handle_table_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls for table operations.

    Args:
        name: Tool name
        arguments: Tool arguments

    Returns:
        Tool execution results
    """
    config = get_config()

    try:
        async with ImplyClient(config) as client:
            if name == "list_tables":
                result = await client.list_tables()
                tables = result.get("values", [])

                if not tables:
                    return [TextContent(type="text", text="No tables found in the project.")]

                # Format table list
                table_list = "\n".join(
                    [
                        f"- {table.get('name', 'unknown')}: {table.get('type', 'unknown')} "
                        f"({table.get('availability', 'unknown')})"
                        for table in tables
                    ]
                )

                return [
                    TextContent(
                        type="text",
                        text=f"Tables in project ({len(tables)} total):\n\n{table_list}",
                    )
                ]

            elif name == "get_table_schema":
                table_name = arguments.get("table_name")
                if not table_name:
                    raise ValueError("table_name is required")

                result = await client.get_table(table_name)
                return [
                    TextContent(
                        type="text",
                        text=f"Table schema for '{table_name}':\n\n{format_json(result)}",
                    )
                ]

            else:
                raise ValueError(f"Unknown tool: {name}")

    except httpx.HTTPStatusError as e:
        error_msg = format_http_error(e)
        return [TextContent(type="text", text=f"Error: {error_msg}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
