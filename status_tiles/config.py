# status_tiles/config.py
from copy import deepcopy
from pathlib import Path
from typing import Annotated, Any, Optional

from pydantic import Field
from pydantic_settings import BaseSettings

DEFAULT_CONFIGS = {
    "http_check": {"url": "https://example.com", "timeout": 5, "name": "Example Website"},
    "system_check": {"cpu_threshold": 90.0, "memory_threshold": 90.0},
}


class Settings(BaseSettings):
    """Application settings"""

    # App configuration
    debug: bool = False
    app_name: str = "Status Tiles"

    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8000

    # Logging configuration
    log_level: str = "INFO"
    log_file: Optional[str] = None

    # Plugin configuration
    plugin_configs: Annotated[dict[str, dict[str, Any]], Field(
            default_factory=lambda: deepcopy(DEFAULT_CONFIGS)
    )]
    # Check intervals (in seconds)
    check_interval: int = 60
    refresh_interval: int = 30

    # Cache configuration
    cache_ttl: int = 30

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


def get_settings() -> Settings:
    """Get application settings"""
    env_file = Path(".env")
    if not env_file.exists():
        print("Warning: .env file not found, using default settings")
    return Settings()
