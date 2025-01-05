import logging
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, field_validator


class LogConfig(BaseModel):
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    @field_validator("level")
    def validate_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()


class ServiceConfig(BaseModel):
    name: str
    type: str
    config: Dict[str, Any]  # Currently allows any values
    polling_interval: int = 300

    # Add validation for known config values:
    @field_validator("config")
    def validate_config(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        required_keys = {"url", "timeout"}  # example required keys
        missing = required_keys - v.keys()
        if missing:
            raise ValueError(f"Missing required config keys: {missing}")
        return v


class AppConfig(BaseModel):
    log: LogConfig = LogConfig()
    services: List[ServiceConfig]

    model_config = {
        "validate_default": True,
        "extra": "allow"
    }

    def __init__(self, **data):
        super().__init__(**data)
        if 'services' not in data:
            self.services = []

    @classmethod
    def from_yaml(cls, path: Path | str) -> "AppConfig":
        """Load configuration from YAML file.

        Args:
            path: Path to YAML configuration file

        Returns:
            AppConfig: Loaded configuration

        Raises:
            FileNotFoundError: If configuration file doesn't exist
            ValidationError: If configuration is invalid
            YAMLError: If YAML parsing fails
        """
        path = Path(path)
        # Ignore SonarQube false positive: Path.exists() is a no-argument method
        # See: https://docs.python.org/3/library/pathlib.html#pathlib.Path.exists
        if not path.exists(): # NOSONAR
            raise FileNotFoundError(f"Configuration file not found: {path}")

        with path.open() as f:
            config_data = yaml.safe_load(f)

        return cls.model_validate(config_data)


@lru_cache()
def get_config(config_path: Optional[Path | str] = None) -> AppConfig:
    """
    Get application configuration, using cached values if available.

    Args:
        config_path: Optional path to config file. If not provided,
                    looks for config.yml in current directory.
    """
    if config_path is None:
        config_path = Path("config.yml")

    try:
        return AppConfig.from_yaml(config_path)
    except Exception as e:
        logging.error(f"Error loading configuration: {e}")
        # Return default configuration
        return AppConfig()


def load_config(config_path: Path | str = "config.yml") -> AppConfig:
    """
    Load configuration from YAML file. This is a non-cached version
    that's useful for testing and reloading config.
    """
    return AppConfig.from_yaml(config_path)
