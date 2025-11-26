# imply-druid-mcp

[![PyPI version](https://badge.fury.io/py/imply-druid-mcp.svg)](https://badge.fury.io/py/imply-druid-mcp)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A read-only MCP (Model Context Protocol) server for Imply Cloud/Druid databases. Query and explore your Druid data through Claude and other AI assistants.

## Features

### Supported ✅

- **SQL Query Execution**
  - Synchronous query execution
  - Asynchronous query execution (for large datasets)
- **Query Management**
  - Check query status
  - Retrieve query results
  - Cancel running queries
- **Table Operations**
  - List all tables in project
  - Get table schema details

### Not Supported ❌

- Data Ingestion
- Table/Schema Creation or Modification
- User/Permission Management
- Supervisor Management

## Tools

### Query Tools

| Tool | Description |
|------|-------------|
| `execute_sql_query` | Execute a SQL query synchronously and return results immediately |
| `execute_async_query` | Execute a SQL query asynchronously for large datasets. Returns a query ID |
| `get_query_results` | Retrieve results from an async query using query ID |
| `get_query_status` | Check the execution status of an async query |
| `cancel_query` | Cancel a running async query |

### Table Tools

| Tool | Description |
|------|-------------|
| `list_tables` | List all tables (datasources) in the Druid project |
| `get_table_schema` | Get detailed schema information for a specific table |

## API Mapping

This MCP server maps to the [Imply Polaris API](https://docs.imply.io/api/polaris/api-reference):

| MCP Tool | Imply API Endpoint |
|----------|-------------------|
| `execute_sql_query` | `POST /v1/projects/{projectId}/query/sql` |
| `execute_async_query` | `POST /v1/projects/{projectId}/query/sql/statements` |
| `get_query_results` | `GET /v1/projects/{projectId}/query/sql/statements/{queryId}/results` |
| `get_query_status` | `GET /v1/projects/{projectId}/query/sql/statements/{queryId}` |
| `cancel_query` | `DELETE /v1/projects/{projectId}/query/sql/statements/{queryId}` |
| `list_tables` | `GET /v1/projects/{projectId}/tables` |
| `get_table_schema` | `GET /v1/projects/{projectId}/tables/{tableName}` |

## Installation

### Using uvx (Recommended)

```bash
uvx imply-druid-mcp
```

### Using pip

```bash
pip install imply-druid-mcp
imply-druid-mcp
```

### Using pipx

```bash
pipx install imply-druid-mcp
imply-druid-mcp
```

## Configuration

| Environment Variable | Required | Default | Description |
|---------------------|----------|---------|-------------|
| `IMPLY_ORGANIZATION` | Yes | - | Imply Cloud organization name |
| `IMPLY_REGION` | Yes | - | Region (e.g., `us-east-1`) |
| `IMPLY_CLOUD_PROVIDER` | Yes | - | Cloud provider: `aws`, `gcp`, or `azure` |
| `IMPLY_PROJECT_ID` | Yes | - | Imply project ID |
| `IMPLY_API_KEY` | Yes* | - | Imply API key |
| `IMPLY_ACCESS_TOKEN` | Yes* | - | OAuth access token (alternative) |
| `LOG_LEVEL` | No | `INFO` | Logging level |
| `DEFAULT_QUERY_TIMEOUT_MS` | No | `30000` | Default query timeout (ms) |
| `MAX_QUERY_LENGTH` | No | `10000` | Maximum SQL query length |

*Either `IMPLY_API_KEY` or `IMPLY_ACCESS_TOKEN` is required.

## Claude Desktop Setup

Add to your Claude Desktop config file:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "imply-druid": {
      "command": "uvx",
      "args": ["imply-druid-mcp"],
      "env": {
        "IMPLY_ORGANIZATION": "your-org",
        "IMPLY_REGION": "us-east-1",
        "IMPLY_CLOUD_PROVIDER": "aws",
        "IMPLY_PROJECT_ID": "your-project-id",
        "IMPLY_API_KEY": "your-api-key"
      }
    }
  }
}
```

## Usage Examples

```
User: Show me all tables in my Druid project

Claude: [Uses list_tables]
- wikipedia (datasource)
- events (datasource)
- metrics (datasource)
```

```
User: Query the top 10 records from wikipedia table

Claude: [Uses execute_sql_query with "SELECT * FROM wikipedia LIMIT 10"]
[Results displayed]
```

## Development

```bash
git clone https://github.com/yeongbin-hwang/imply-druid-mcp.git
cd imply-druid-mcp
pip install -e ".[dev]"
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Resources

- [MCP Protocol](https://modelcontextprotocol.io/)
- [Imply Cloud Docs](https://docs.imply.io/)
- [Apache Druid](https://druid.apache.org/)
