"""Main MCP server for Imply Druid."""

import asyncio
import logging
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .config import get_config
from .tools.query_tools import get_query_tools, handle_query_tool, QUERY_TOOL_NAMES
from .tools.table_tools import get_table_tools, handle_table_tool, TABLE_TOOL_NAMES
from .tools.dashboard_tools import get_dashboard_tools, handle_dashboard_tool, DASHBOARD_TOOL_NAMES
from .tools.datacube_tools import get_datacube_tools, handle_datacube_tool, DATACUBE_TOOL_NAMES

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("imply-druid-mcp")


def create_server() -> Server:
    """Create and configure the MCP server.

    Returns:
        Configured MCP server instance
    """
    # Load configuration
    try:
        config = get_config()
        # Mask project_id for security (show only first 4 chars)
        masked_project_id = config.project_id[:4] + "****" if len(config.project_id) > 4 else "****"
        logger.info(f"Loaded configuration for project: {masked_project_id}")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        raise

    # Create server
    server = Server(config.server_name)

    # Collect all tools
    all_tools = []
    all_tools.extend(get_query_tools())
    all_tools.extend(get_table_tools())
    all_tools.extend(get_dashboard_tools())
    all_tools.extend(get_datacube_tools())

    logger.info(f"Registered {len(all_tools)} tools")

    # Register list_tools handler
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List all available tools."""
        return all_tools

    # Register call_tool handler
    @server.call_tool()
    async def call_tool(name: str, arguments: Any) -> list[TextContent]:
        """Handle tool calls by routing to appropriate handler."""
        logger.info(f"Calling tool: {name}")

        # Query tools
        if name in QUERY_TOOL_NAMES:
            return await handle_query_tool(name, arguments)

        # Table tools
        elif name in TABLE_TOOL_NAMES:
            return await handle_table_tool(name, arguments)

        # Dashboard tools
        elif name in DASHBOARD_TOOL_NAMES:
            return await handle_dashboard_tool(name, arguments)

        # Data cube tools
        elif name in DATACUBE_TOOL_NAMES:
            return await handle_datacube_tool(name, arguments)

        else:
            logger.error(f"Unknown tool requested: {name}")
            return [TextContent(type="text", text=f"Error: Unknown tool '{name}'")]

    logger.info("MCP server initialized successfully")

    return server


async def main() -> None:
    """Main entry point for the MCP server."""
    logger.info("Starting Imply Druid MCP Server...")

    try:
        server = create_server()

        # Run the server using stdio transport
        async with stdio_server() as (read_stream, write_stream):
            logger.info("Server running on stdio transport")
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options(),
            )
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        # Log error type only, full stack trace may contain sensitive info
        logger.error(f"Server error: {type(e).__name__}")
        raise
    finally:
        logger.info("Server stopped")


def run() -> None:
    """Run the server (entry point for command line)."""
    asyncio.run(main())


if __name__ == "__main__":
    run()
