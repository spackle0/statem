import pytest
from status_tiles.config import AppConfig, LogConfig, get_config


def test_log_config_validation():
    """Test log level validation"""
    # Valid log level
    config = LogConfig(level="INFO")
    assert config.level == "INFO"

    # Invalid log level should raise error
    with pytest.raises(ValueError):
        LogConfig(level="INVALID")


def test_app_config_defaults():
    """Test default configuration values"""
    config = AppConfig()
    assert isinstance(config.log, LogConfig)
    assert config.services == {}


def test_config_from_yaml(config_file):
    """Test loading configuration from YAML file"""
    config = AppConfig.from_yaml(config_file)
    assert config.log.level == "INFO"
    assert len(config.services) > 0


def test_get_config_caching(config_file):
    """Test that get_config caches results"""
    config1 = get_config(config_file)
    config2 = get_config(config_file)
    assert config1 is config2  # Should be same instance due to caching


def test_get_config_missing_file():
    """Test fallback to defaults with missing config file"""
    config = get_config("nonexistent.yml")
    assert isinstance(config, AppConfig)
    assert config.log.level == "INFO"
