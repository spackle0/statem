from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient
from status_tiles.api import app


@pytest.fixture
def test_config():
    return {
        "log": {"level": "INFO", "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"},
        "services": [
            {
                "name": "Test RSS",
                "type": "rss",
                "config": {"name": "Test Feed", "feed_url": "https://example.com/feed.xml", "timeout": 10},
                "polling_interval": 300,
            }
        ],
    }


@pytest.fixture
def config_file(tmp_path: Path, test_config):
    config_path = tmp_path / "config.yml"
    with open(config_path, "w") as f:
        yaml.dump(test_config, f)
    return config_path


@pytest.fixture
def client():
    return TestClient(app)
