"""Configuration management for Imply Druid MCP Server."""

import os
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class ImplyConfig(BaseModel):
    """Configuration for Imply Cloud/Druid connection."""

    organization: str = Field(..., description="Imply organization name")
    region: str = Field(default="us-east-1", description="Cloud region")
    cloud_provider: str = Field(default="aws", description="Cloud provider (aws, gcp, azure)")
    project_id: str = Field(..., description="Imply project ID")
    api_key: Optional[str] = Field(default=None, description="API key for authentication")
    access_token: Optional[str] = Field(
        default=None, description="OAuth access token (alternative to API key)"
    )

    # Server settings
    server_name: str = Field(default="Imply Druid MCP Server", description="MCP server name")
    log_level: str = Field(default="INFO", description="Logging level")

    # Query settings
    default_query_timeout_ms: int = Field(
        default=30000, description="Default query timeout in milliseconds"
    )
    max_query_length: int = Field(default=10000, description="Maximum query length")

    @field_validator("cloud_provider")
    @classmethod
    def validate_cloud_provider(cls, v: str) -> str:
        """Validate cloud provider value."""
        allowed = ["aws", "gcp", "azure"]
        if v.lower() not in allowed:
            raise ValueError(f"cloud_provider must be one of {allowed}")
        return v.lower()

    @field_validator("api_key", "access_token")
    @classmethod
    def validate_credentials(cls, v: Optional[str], info) -> Optional[str]:
        """Ensure at least one authentication method is provided."""
        # This will be called for both fields
        return v

    def model_post_init(self, __context) -> None:
        """Validate that at least one auth method is provided."""
        if not self.api_key and not self.access_token:
            raise ValueError("Either api_key or access_token must be provided")

    @property
    def base_url(self) -> str:
        """Construct the base URL for Imply API."""
        return f"https://{self.organization}.{self.region}.{self.cloud_provider}.api.imply.io"

    @property
    def auth_header(self) -> dict[str, str]:
        """Get authentication header."""
        if self.api_key:
            return {"Authorization": f"Basic {self.api_key}"}
        elif self.access_token:
            return {"Authorization": f"Bearer {self.access_token}"}
        raise ValueError("No authentication credentials available")

    @classmethod
    def from_env(cls) -> "ImplyConfig":
        """Create configuration from environment variables."""
        return cls(
            organization=os.getenv("IMPLY_ORGANIZATION", ""),
            region=os.getenv("IMPLY_REGION", "us-east-1"),
            cloud_provider=os.getenv("IMPLY_CLOUD_PROVIDER", "aws"),
            project_id=os.getenv("IMPLY_PROJECT_ID", ""),
            api_key=os.getenv("IMPLY_API_KEY"),
            access_token=os.getenv("IMPLY_ACCESS_TOKEN"),
            server_name=os.getenv("MCP_SERVER_NAME", "Imply Druid MCP Server"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            default_query_timeout_ms=int(os.getenv("DEFAULT_QUERY_TIMEOUT_MS", "30000")),
            max_query_length=int(os.getenv("MAX_QUERY_LENGTH", "10000")),
        )


# Global configuration instance
_config: Optional[ImplyConfig] = None


def get_config() -> ImplyConfig:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = ImplyConfig.from_env()
    return _config


def set_config(config: ImplyConfig) -> None:
    """Set the global configuration instance (useful for testing)."""
    global _config
    _config = config
