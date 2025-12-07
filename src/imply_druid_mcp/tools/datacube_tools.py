"""Data cube read-only tools for MCP."""

import logging
from typing import Any

import httpx
from mcp.types import Tool, TextContent

from ..client import ImplyClient
from ..config import get_config
from ..utils import format_http_error, format_json, MAX_DISPLAY_ROWS

logger = logging.getLogger("imply-druid-mcp")

# Tool names for this module
DATACUBE_TOOL_NAMES = ["list_data_cubes", "get_data_cube", "query_data_cube"]


def get_datacube_tools() -> list[Tool]:
    """Get list of data cube tools.

    Returns:
        List of data cube tool definitions
    """
    return [
        Tool(
            name="list_data_cubes",
            description="List all data cubes in the Imply project with their metadata.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="get_data_cube",
            description="Get detailed information about a specific data cube including dimensions and measures.",
            inputSchema={
                "type": "object",
                "properties": {
                    "cube_id": {
                        "type": "string",
                        "description": "ID of the data cube (from list_data_cubes)",
                    },
                },
                "required": ["cube_id"],
            },
        ),
        Tool(
            name="query_data_cube",
            description=(
                "Execute SQL query against a data cube (Pivot). Use 'source' from list_data_cubes. "
                'Syntax: FROM "datacube"."SOURCE", "DIM:dimension_name", MEASURE_BY_ID(\'measure_id\')'
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query_string": {
                        "type": "string",
                        "description": "SQL query with data cube syntax",
                    },
                    "exact_results_only": {
                        "type": "boolean",
                        "description": "Use exact results for TopN/COUNT DISTINCT (default: false)",
                        "default": False,
                    },
                },
                "required": ["query_string"],
            },
        ),
    ]


async def handle_datacube_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls for data cube operations.

    Args:
        name: Tool name
        arguments: Tool arguments

    Returns:
        Tool execution results
    """
    config = get_config()

    try:
        async with ImplyClient(config) as client:
            if name == "list_data_cubes":
                result = await client.list_data_cubes()
                cubes = result.get("values", [])

                if not cubes:
                    return [TextContent(type="text", text="No data cubes found in the project.")]

                # Format data cube list with id, title, source
                cube_list = "\n".join(
                    [
                        f"- ID: {cube.get('id', 'unknown')}\n"
                        f"  Title: {cube.get('title', 'No title')}\n"
                        f"  Source: {cube.get('source', 'unknown')}"
                        for cube in cubes
                    ]
                )

                return [
                    TextContent(
                        type="text",
                        text=f"Data cubes in project ({len(cubes)} total):\n\n{cube_list}",
                    )
                ]

            elif name == "get_data_cube":
                cube_id = arguments.get("cube_id")
                if not cube_id:
                    raise ValueError("cube_id is required")

                result = await client.get_data_cube(cube_id)
                return [
                    TextContent(
                        type="text",
                        text=f"Data cube details for '{cube_id}':\n\n{format_json(result)}",
                    )
                ]

            elif name == "query_data_cube":
                query_string = arguments.get("query_string")
                if not query_string:
                    raise ValueError("query_string is required")

                exact_results_only = arguments.get("exact_results_only", False)

                result = await client.query_data_cube(query_string, exact_results_only)

                # Format the result
                # Data format: row 0 = column names, rows 1-2 = type info, rows 3+ = data
                data = result.get("data", [])
                if len(data) <= 3:
                    return [TextContent(type="text", text="Query returned no results.")]

                columns = data[0]
                rows = data[3:]

                output = f"Query Results ({len(rows)} rows):\n\n"
                output += "Columns: " + ", ".join(str(c) for c in columns) + "\n\n"

                for row in rows[:MAX_DISPLAY_ROWS]:
                    output += " | ".join(str(v) for v in row) + "\n"

                if len(rows) > MAX_DISPLAY_ROWS:
                    output += f"\n... and {len(rows) - MAX_DISPLAY_ROWS} more rows"

                return [TextContent(type="text", text=output)]

            else:
                raise ValueError(f"Unknown tool: {name}")

    except httpx.HTTPStatusError as e:
        error_msg = format_http_error(e)
        return [TextContent(type="text", text=f"Error: {error_msg}")]
    except ValueError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except Exception as e:
        logger.error(f"Data cube tool error: {e}", exc_info=True)
        return [
            TextContent(
                type="text",
                text="Error: An unexpected error occurred while processing the request.",
            )
        ]
