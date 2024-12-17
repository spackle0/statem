import asyncio
import logging
from unittest.mock import MagicMock

import aiohttp
import pytest
from status_tiles.models import ServiceStatus
from status_tiles.service_modules.http_module import HTTPModule

# Set up logging for tests
logging.basicConfig(level=logging.DEBUG)


@pytest.fixture
def http_config():
    return {
        "name": "Test HTTP Service",
        "url": "https://example.com/health",
        "method": "GET",
        "timeout": 10,
        "expected_status": 200
    }


@pytest.fixture
def http_module(http_config):
    return HTTPModule(http_config)


class MockResponse:
    def __init__(self, status):
        self.status = status

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.mark.asyncio
async def test_healthy_service(http_module, mocker):
    """Test successful HTTP request"""
    session_mock = MagicMock()
    response_mock = MockResponse(200)

    session_mock.__aenter__.return_value = session_mock
    session_mock.__aexit__.return_value = None
    session_mock.request.return_value = response_mock

    mocker.patch('aiohttp.ClientSession', return_value=session_mock)

    status = await http_module.get_status()

    assert status.status == ServiceStatus.HEALTHY
    assert status.name == "Test HTTP Service"
    assert "response_time_ms" in status.details
    assert status.details["status_code"] == 200


@pytest.mark.asyncio
async def test_unhealthy_service_wrong_status(http_module, mocker):
    """Test handling of unexpected HTTP status"""
    session_mock = MagicMock()
    response_mock = MockResponse(500)

    session_mock.__aenter__.return_value = session_mock
    session_mock.__aexit__.return_value = None
    session_mock.request.return_value = response_mock

    mocker.patch('aiohttp.ClientSession', return_value=session_mock)

    status = await http_module.get_status()

    assert status.status == ServiceStatus.UNHEALTHY
    assert "error" in status.details
    assert "500" in status.details["error"]


@pytest.mark.asyncio
async def test_timeout_error(http_module, mocker):
    """Test handling of timeout errors"""
    session_mock = MagicMock()
    session_mock.__aenter__.return_value = session_mock
    session_mock.request.side_effect = asyncio.TimeoutError()

    mocker.patch('aiohttp.ClientSession', return_value=session_mock)

    status = await http_module.get_status()

    assert status.status == ServiceStatus.UNHEALTHY
    assert "Request timed out" == status.details["error"]  # Exact match


@pytest.mark.asyncio
async def test_connection_error(http_module, mocker):
    """Test handling of connection errors"""
    session_mock = MagicMock()
    session_mock.__aenter__.return_value = session_mock
    session_mock.request.side_effect = aiohttp.ClientError("Connection failed")

    mocker.patch('aiohttp.ClientSession', return_value=session_mock)

    status = await http_module.get_status()

    assert status.status == ServiceStatus.UNHEALTHY
    assert "Connection failed" in status.details["error"]


@pytest.mark.asyncio
async def test_post_request_with_body(mocker):
    """Test POST request with body"""
    config = {
        "name": "Test POST Service",
        "url": "https://example.com/api",
        "method": "POST",
        "body": {"key": "value"},
        "headers": {"Content-Type": "application/json"},
        "expected_status": 201
    }
    http_module = HTTPModule(config)

    session_mock = MagicMock()
    response_mock = MockResponse(201)

    session_mock.__aenter__.return_value = session_mock
    session_mock.__aexit__.return_value = None
    session_mock.request.return_value = response_mock

    mocker.patch('aiohttp.ClientSession', return_value=session_mock)

    status = await http_module.get_status()

    assert status.status == ServiceStatus.HEALTHY
    session_mock.request.assert_called_once_with(
            method="POST",
            url="https://example.com/api",
            headers={"Content-Type": "application/json"},
            json={"key": "value"},
            timeout=30,
            ssl=True
    )


@pytest.mark.asyncio
async def test_custom_headers(mocker):
    """Test request with custom headers"""
    config = {
        "name": "Test Headers Service",
        "url": "https://example.com/api",
        "headers": {
            "Authorization": "Bearer token123",
            "Custom-Header": "value"
        }
    }
    http_module = HTTPModule(config)

    session_mock = MagicMock()
    response_mock = MockResponse(200)

    session_mock.__aenter__.return_value = session_mock
    session_mock.__aexit__.return_value = None
    session_mock.request.return_value = response_mock

    mocker.patch('aiohttp.ClientSession', return_value=session_mock)

    status = await http_module.get_status()

    assert status.status == ServiceStatus.HEALTHY
    session_mock.request.assert_called_once_with(
            method="GET",
            url="https://example.com/api",
            headers={
                "Authorization": "Bearer token123",
                "Custom-Header": "value"
            },
            json=None,
            timeout=30,
            ssl=True
    )


def test_config_schema(http_module):
    """Test configuration schema validation"""
    schema = http_module.get_config_schema()
    assert "name" in schema["properties"]
    assert "url" in schema["properties"]
    assert "method" in schema["properties"]
    assert "timeout" in schema["properties"]
    assert "headers" in schema["properties"]
    assert "body" in schema["properties"]
    assert set(schema["required"]) == {"name", "url"}
