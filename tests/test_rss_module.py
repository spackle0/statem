import pytest
from status_tiles.models import ServiceStatus
from status_tiles.service_modules.rss_module import RSSModule


@pytest.fixture
def rss_config():
    return {"name": "Test Feed", "feed_url": "https://example.com/feed.xml", "timeout": 10}


@pytest.fixture
def rss_module(rss_config):
    return RSSModule(rss_config)


@pytest.mark.asyncio
async def test_healthy_feed(rss_module, mocker):
    """Test successful RSS feed parsing"""
    mock_response = mocker.AsyncMock()
    mock_response.status = 200
    mock_response.text = mocker.AsyncMock(
        return_value="""
        <?xml version="1.0"?>
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
        </rss>
    """
    )

    mock_session = mocker.AsyncMock()
    mock_session.__aenter__.return_value = mock_response

    mocker.patch("aiohttp.ClientSession", return_value=mock_session)

    status = await rss_module.get_status()

    assert status.status == ServiceStatus.HEALTHY
    assert status.name == "Test Feed"
    assert "title" in status.details
    assert status.details["entries_count"] == 1


@pytest.mark.asyncio
async def test_unhealthy_feed_http_error(rss_module, mocker):
    """Test handling of HTTP errors"""
    mock_response = mocker.AsyncMock()
    mock_response.status = 404

    mock_session = mocker.AsyncMock()
    mock_session.__aenter__.return_value = mock_response

    mocker.patch("aiohttp.ClientSession", return_value=mock_session)

    status = await rss_module.get_status()

    assert status.status == ServiceStatus.UNHEALTHY
    assert "HTTP 404" in status.details["error"]


@pytest.mark.asyncio
async def test_unhealthy_feed_parse_error(rss_module, mocker):
    """Test handling of feed parsing errors"""
    mock_response = mocker.AsyncMock()
    mock_response.status = 200
    mock_response.text = mocker.AsyncMock(return_value="Invalid XML")

    mock_session = mocker.AsyncMock()
    mock_session.__aenter__.return_value = mock_response

    mocker.patch("aiohttp.ClientSession", return_value=mock_session)

    status = await rss_module.get_status()

    assert status.status == ServiceStatus.UNHEALTHY
    assert "error" in status.details


def test_config_schema(rss_module):
    """Test configuration schema validation"""
    schema = rss_module.get_config_schema()
    assert "name" in schema["properties"]
    assert "feed_url" in schema["properties"]
    assert "timeout" in schema["properties"]
    assert "name" in schema["required"]
    assert "feed_url" in schema["required"]
