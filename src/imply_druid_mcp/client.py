"""HTTP client for Imply Cloud/Druid API."""

import httpx
from typing import Any, Optional
from .config import ImplyConfig
from .utils import validate_path_param


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
            follow_redirects=False,  # Disabled to prevent credential leak on redirect
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
        validated_id = validate_path_param(query_id, "query_id")
        response = await self.client.get(
            f"/v1/projects/{self.project_id}/query/sql/statements/{validated_id}/results"
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
        validated_id = validate_path_param(query_id, "query_id")
        response = await self.client.get(
            f"/v1/projects/{self.project_id}/query/sql/statements/{validated_id}"
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
        validated_id = validate_path_param(query_id, "query_id")
        response = await self.client.delete(
            f"/v1/projects/{self.project_id}/query/sql/statements/{validated_id}"
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
        validated_name = validate_path_param(table_name, "table_name")
        response = await self.client.get(f"/v1/projects/{self.project_id}/tables/{validated_name}")
        response.raise_for_status()
        return response.json()

    # Dashboard Operations

    async def list_dashboards(self) -> dict[str, Any]:
        """List all dashboards in the project.

        Returns:
            List of dashboards with metadata
        """
        response = await self.client.get(f"/v1/projects/{self.project_id}/dashboards")
        response.raise_for_status()
        return response.json()

    async def get_dashboard(self, dashboard_id: str) -> dict[str, Any]:
        """Get details about a specific dashboard.

        Args:
            dashboard_id: ID of the dashboard

        Returns:
            Dashboard details including configuration
        """
        validated_id = validate_path_param(dashboard_id, "dashboard_id")
        response = await self.client.get(
            f"/v1/projects/{self.project_id}/dashboards/{validated_id}"
        )
        response.raise_for_status()
        return response.json()

    # Data Cube Operations

    async def list_data_cubes(self) -> dict[str, Any]:
        """List all data cubes in the project.

        Returns:
            List of data cubes with metadata
        """
        response = await self.client.get(f"/v1/projects/{self.project_id}/data-cubes")
        response.raise_for_status()
        return response.json()

    async def get_data_cube(self, cube_id: str) -> dict[str, Any]:
        """Get details about a specific data cube.

        Args:
            cube_id: ID of the data cube

        Returns:
            Data cube details including dimensions and measures
        """
        validated_id = validate_path_param(cube_id, "cube_id")
        response = await self.client.get(
            f"/v1/projects/{self.project_id}/data-cubes/{validated_id}"
        )
        response.raise_for_status()
        return response.json()

    # Pivot Query Operations (v0 API)

    async def query_data_cube(
        self, query_string: str, exact_results_only: bool = False
    ) -> dict[str, Any]:
        """Execute SQL query against a data cube (Pivot).

        Args:
            query_string: SQL query with special syntax:
                - FROM "datacube"."CUBE_ID"
                - DIM:dimension_name or DIMENSION_BY_ID('id')
                - MEASURE_BY_ID('measure_id')
            exact_results_only: If true, precise results for TopN/COUNT DISTINCT

        Returns:
            Query results with data array
        """
        payload = {
            "queryString": query_string,
            "exactResultsOnly": exact_results_only,
        }
        # Note: v0 API endpoint
        response = await self.client.post(
            f"/v0/projects/{self.project_id}/pivot/data-cube-sql/query",
            json=payload,
        )
        response.raise_for_status()
        return response.json()
