"""HTTP client for Imply Cloud/Druid API."""

import httpx
from typing import Any, Optional
from .config import ImplyConfig


class ImplyClient:
    """Async HTTP client for Imply Cloud/Druid API."""

    def __init__(self, config: ImplyConfig):
        """Initialize the Imply client.

        Args:
            config: Imply configuration
        """
        self.config = config
        self.base_url = config.base_url
        self.project_id = config.project_id
        self.headers = {
            **config.auth_header,
            "Content-Type": "application/json",
        }
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "ImplyClient":
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            timeout=httpx.Timeout(60.0),  # 60 second timeout
            follow_redirects=True,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()

    @property
    def client(self) -> httpx.AsyncClient:
        """Get the HTTP client instance."""
        if self._client is None:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")
        return self._client

    # Query Operations

    async def execute_query(
        self, sql: str, async_mode: bool = False, timeout_ms: Optional[int] = None
    ) -> dict[str, Any]:
        """Execute SQL query against Druid.

        Args:
            sql: SQL query string
            async_mode: If True, execute asynchronously
            timeout_ms: Query timeout in milliseconds

        Returns:
            Query results or query ID (for async queries)
        """
        endpoint = "query/sql/statements" if async_mode else "query/sql"
        payload: dict[str, Any] = {"query": sql}

        if timeout_ms:
            payload["timeout"] = timeout_ms

        response = await self.client.post(
            f"/v1/projects/{self.project_id}/{endpoint}", json=payload
        )
        response.raise_for_status()
        return response.json()

    async def get_query_results(self, query_id: str) -> dict[str, Any]:
        """Get results from an async query.

        Args:
            query_id: Query ID from async query

        Returns:
            Query results
        """
        response = await self.client.get(
            f"/v1/projects/{self.project_id}/query/sql/statements/{query_id}/results"
        )
        response.raise_for_status()
        return response.json()

    async def get_query_status(self, query_id: str) -> dict[str, Any]:
        """Get status of an async query.

        Args:
            query_id: Query ID from async query

        Returns:
            Query status information
        """
        response = await self.client.get(
            f"/v1/projects/{self.project_id}/query/sql/statements/{query_id}"
        )
        response.raise_for_status()
        return response.json()

    async def cancel_query(self, query_id: str) -> dict[str, Any]:
        """Cancel a running query.

        Args:
            query_id: Query ID to cancel

        Returns:
            Cancellation confirmation
        """
        response = await self.client.delete(
            f"/v1/projects/{self.project_id}/query/sql/statements/{query_id}"
        )
        response.raise_for_status()
        return response.json() if response.content else {"status": "cancelled"}

    # Table Operations

    async def list_tables(self) -> dict[str, Any]:
        """List all tables in the project.

        Returns:
            List of tables with metadata
        """
        response = await self.client.get(f"/v1/projects/{self.project_id}/tables")
        response.raise_for_status()
        return response.json()

    async def get_table(self, table_name: str) -> dict[str, Any]:
        """Get details about a specific table.

        Args:
            table_name: Name of the table

        Returns:
            Table details including schema
        """
        response = await self.client.get(f"/v1/projects/{self.project_id}/tables/{table_name}")
        response.raise_for_status()
        return response.json()
