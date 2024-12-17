import logging
from unittest.mock import MagicMock

import aiohttp
import pytest
from status_tiles.models import ServiceStatus
from status_tiles.service_modules.rss_module import RSSModule

# Set up logging for tests
logging.basicConfig(level=logging.DEBUG)


@pytest.fixture
def rss_config():
    return {"name": "Test Feed", "feed_url": "https://example.com/feed.xml", "timeout": 10}


@pytest.fixture
def rss_module(rss_config):
    return RSSModule(rss_config)


@pytest.fixture
def valid_rss_content():
    return """<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
    <channel>
        <title>Test Feed</title>
        <link>http://example.com</link>
        <description>Test Description</description>
        <item>
            <title>Test Item</title>
            <link>http://example.com/item</link>
            <description>Test Item Description</description>
        </item>
    </channel>
</rss>"""


class MockResponse:
    def __init__(self, status, text_data):
        self.status = status
        self._text = text_data

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def text(self):
        return self._text


@pytest.mark.asyncio
async def test_healthy_feed(rss_module, valid_rss_content, mocker, caplog):
    """Test successful RSS feed parsing"""
    caplog.set_level(logging.DEBUG)

    session_mock = MagicMock()
    response_mock = MockResponse(200, valid_rss_content)

    session_mock.__aenter__.return_value = session_mock
    session_mock.__aexit__.return_value = None
    session_mock.get.return_value = response_mock

    mocker.patch("aiohttp.ClientSession", return_value=session_mock)

    status = await rss_module.get_status()

    # Print debug information
    print(f"\nResponse content: {valid_rss_content[:200]}...")
    print(f"Status: {status.status}")
    print(f"Details: {status.details}")

    assert status.status == ServiceStatus.HEALTHY, f"Feed parsing failed: {status.details}"
    assert status.name == "Test Feed"
    assert "title" in status.details
    assert status.details["entries_count"] == 1


@pytest.mark.asyncio
async def test_unhealthy_feed_http_error(rss_module, mocker, caplog):
    """Test handling of HTTP errors"""
    caplog.set_level(logging.DEBUG)

    session_mock = MagicMock()
    response_mock = MockResponse(404, "Not Found")

    session_mock.__aenter__.return_value = session_mock
    session_mock.__aexit__.return_value = None
    session_mock.get.return_value = response_mock

    mocker.patch("aiohttp.ClientSession", return_value=session_mock)

    status = await rss_module.get_status()
    assert status.status == ServiceStatus.UNHEALTHY
    assert "HTTP 404" in status.details["error"]


@pytest.mark.asyncio
async def test_unhealthy_feed_parse_error(rss_module, mocker):
    """Test handling of feed parsing errors"""
    session_mock = MagicMock()
    response_mock = MockResponse(200, "Invalid XML")

    session_mock.__aenter__.return_value = session_mock
    session_mock.__aexit__.return_value = None
    session_mock.get.return_value = response_mock

    mocker.patch("aiohttp.ClientSession", return_value=session_mock)

    status = await rss_module.get_status()
    assert status.status == ServiceStatus.UNHEALTHY
    assert "error" in status.details


@pytest.mark.asyncio
async def test_connection_error(rss_module, mocker):
    """Test handling of connection errors"""
    session_mock = MagicMock()
    session_mock.__aenter__.side_effect = aiohttp.ClientError("Connection failed")

    mocker.patch("aiohttp.ClientSession", return_value=session_mock)

    status = await rss_module.get_status()
    assert status.status == ServiceStatus.UNHEALTHY
    assert "Connection failed" in status.details["error"]


def test_config_schema(rss_module):
    """Test configuration schema validation"""
    schema = rss_module.get_config_schema()
    assert "name" in schema["properties"]
    assert "feed_url" in schema["properties"]
    assert "timeout" in schema["properties"]
    assert "name" in schema["required"]
    assert "feed_url" in schema["required"]
