from datetime import datetime
from typing import Any, Dict

import aiohttp
import feedparser

from ..models import ServiceState, ServiceStatus
from .base import ServiceModule


class RSSModule(ServiceModule):
    def __init__(self, config: Dict[str, Any]):
        self.name = config["name"]
        self.feed_url = config["feed_url"]
        self.timeout = config.get("timeout", 30)

    async def get_status(self) -> ServiceState:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.feed_url, timeout=self.timeout) as response:
                    if response.status != 200:
                        return ServiceState(
                            name=self.name,
                            status=ServiceStatus.UNHEALTHY,
                            last_checked=datetime.utcnow(),
                            details={"error": f"HTTP {response.status}"},
                        )

                    content = await response.text()
                    feed = feedparser.parse(content)

                    if feed.bozo:  # Feed parsing error
                        return ServiceState(
                            name=self.name,
                            status=ServiceStatus.UNHEALTHY,
                            last_checked=datetime.utcnow(),
                            details={"error": str(feed.bozo_exception)},
                        )

                    return ServiceState(
                        name=self.name,
                        status=ServiceStatus.HEALTHY,
                        last_checked=datetime.utcnow(),
                        details={
                            "title": feed.feed.get("title", "Unknown"),
                            "last_updated": feed.feed.get("updated", "Unknown"),
                            "entries_count": len(feed.entries),
                        },
                    )
        except Exception as e:
            return ServiceState(
                name=self.name,
                status=ServiceStatus.UNHEALTHY,
                last_checked=datetime.utcnow(),
                details={"error": str(e)},
            )

    def get_config_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "feed_url": {"type": "string", "format": "uri"},
                "timeout": {"type": "number", "default": 30},
            },
            "required": ["name", "feed_url"],
        }
