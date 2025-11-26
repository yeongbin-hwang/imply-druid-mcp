"""Query execution tools for MCP."""

from typing import Any

import httpx
from mcp.types import Tool, TextContent

from ..client import ImplyClient
from ..config import get_config
from ..utils import format_http_error, format_json


def validate_sql(sql: str) -> None:
    """Validate SQL query.

    Args:
        sql: SQL query string

    Raises:
        ValueError: If SQL is invalid
    """
    config = get_config()

    # Check query length
    if len(sql) > config.max_query_length:
        raise ValueError(f"Query too long. Maximum length: {config.max_query_length}")


def get_query_tools() -> list[Tool]:
    """Get list of query tools.

    Returns:
        List of query tool definitions
    """
    return [
        Tool(
            name="execute_sql_query",
            description="Execute a SQL query against Druid and return results. Use this for synchronous queries on small datasets.",
            inputSchema={
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "SQL query to execute",
                    },
                    "timeout_ms": {
                        "type": "integer",
                        "description": "Query timeout in milliseconds (optional)",
                    },
                },
                "required": ["sql"],
            },
        ),
        Tool(
            name="execute_async_query",
            description="Execute an asynchronous SQL query for large datasets or long-running queries. Returns a query ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "SQL query to execute",
                    },
                    "timeout_ms": {
                        "type": "integer",
                        "description": "Query timeout in milliseconds (optional)",
                    },
                },
                "required": ["sql"],
            },
        ),
        Tool(
            name="get_query_results",
            description="Get results from an asynchronous query using its query ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query_id": {
                        "type": "string",
                        "description": "Query ID from execute_async_query",
                    },
                },
                "required": ["query_id"],
            },
        ),
        Tool(
            name="get_query_status",
            description="Check the status of an asynchronous query.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query_id": {
                        "type": "string",
                        "description": "Query ID to check",
                    },
                },
                "required": ["query_id"],
            },
        ),
        Tool(
            name="cancel_query",
            description="Cancel a running query.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query_id": {
                        "type": "string",
                        "description": "Query ID to cancel",
                    },
                },
                "required": ["query_id"],
            },
        ),
    ]


async def handle_query_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls for query operations.

    Args:
        name: Tool name
        arguments: Tool arguments

    Returns:
        Tool execution results
    """
    config = get_config()

    try:
        async with ImplyClient(config) as client:
            if name == "execute_sql_query":
                sql = arguments.get("sql")
                if not sql:
                    raise ValueError("SQL query is required")

                validate_sql(sql)

                timeout_ms = arguments.get("timeout_ms", config.default_query_timeout_ms)
                result = await client.execute_query(sql, async_mode=False, timeout_ms=timeout_ms)

                return [
                    TextContent(
                        type="text",
                        text=f"Query executed successfully:\n\n{format_json(result)}",
                    )
                ]

            elif name == "execute_async_query":
                sql = arguments.get("sql")
                if not sql:
                    raise ValueError("SQL query is required")

                validate_sql(sql)

                timeout_ms = arguments.get("timeout_ms", config.default_query_timeout_ms)
                result = await client.execute_query(sql, async_mode=True, timeout_ms=timeout_ms)

                query_id = result.get("queryId", "unknown")
                return [
                    TextContent(
                        type="text",
                        text=f"Async query started successfully.\n\nQuery ID: {query_id}\n\nUse 'get_query_status' to check progress and 'get_query_results' to retrieve results.",
                    )
                ]

            elif name == "get_query_results":
                query_id = arguments.get("query_id")
                if not query_id:
                    raise ValueError("query_id is required")

                result = await client.get_query_results(query_id)
                return [
                    TextContent(
                        type="text",
                        text=f"Query results:\n\n{format_json(result)}",
                    )
                ]

            elif name == "get_query_status":
                query_id = arguments.get("query_id")
                if not query_id:
                    raise ValueError("query_id is required")

                status = await client.get_query_status(query_id)
                return [
                    TextContent(
                        type="text",
                        text=f"Query status:\n\n{format_json(status)}",
                    )
                ]

            elif name == "cancel_query":
                query_id = arguments.get("query_id")
                if not query_id:
                    raise ValueError("query_id is required")

                result = await client.cancel_query(query_id)
                return [
                    TextContent(
                        type="text",
                        text=f"Query cancelled successfully.\n\n{format_json(result)}",
                    )
                ]

            else:
                raise ValueError(f"Unknown tool: {name}")

    except httpx.HTTPStatusError as e:
        error_msg = format_http_error(e)
        return [TextContent(type="text", text=f"Error: {error_msg}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
