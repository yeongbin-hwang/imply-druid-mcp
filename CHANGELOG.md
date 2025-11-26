# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
