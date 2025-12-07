# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-12-08

### Added

- Dashboard tools: `list_dashboards`, `get_dashboard`
- Data Cube tools: `list_data_cubes`, `get_data_cube`, `query_data_cube`
- Pivot SQL query support for data cubes (v0 API)
- Path parameter validation to prevent path traversal attacks
- Tool name constants for better maintainability

### Security

- Disabled HTTP redirects to prevent credential leaks
- Masked project_id in logs (shows only first 4 chars)
- Improved error handling: generic messages for unexpected errors, detailed messages only for validation errors

### Changed

- Refactored tool routing to use module-level constants

## [0.1.1] - 2025-11-27

### Fixed

- Fixed server startup error (removed unused read_only_mode reference)

## [0.1.0] - 2025-11-27

### Added

- Initial release
- SQL query execution (synchronous via `execute_sql_query`)
- Async query execution (`execute_async_query`)
- Query result retrieval (`get_query_results`)
- Query status checking (`get_query_status`)
- Query cancellation (`cancel_query`)
- Table listing (`list_tables`)
- Table schema retrieval (`get_table_schema`)
- Claude Desktop integration support
- Support for AWS, GCP, and Azure cloud providers
