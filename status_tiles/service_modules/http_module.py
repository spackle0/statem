import asyncio
from datetime import datetime
from typing import Any, Dict

import aiohttp

from ..models import ServiceState, ServiceStatus
from .base import ServiceModule


class HTTPModule(ServiceModule):
    """Module for monitoring HTTP endpoints"""

    def __init__(self, config: Dict[str, Any]):
        self.name = config["name"]
        self.url = config["url"]
        self.method = config.get("method", "GET")
        self.timeout = config.get("timeout", 30)
        self.expected_status = config.get("expected_status", 200)
        self.headers = config.get("headers", {})
        self.body = config.get("body")
        self.verify_ssl = config.get("verify_ssl", True)

    async def get_status(self) -> ServiceState:
        try:
            start_time = datetime.now()
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=self.method,
                    url=self.url,
                    headers=self.headers,
                    json=self.body if self.body else None,
                    timeout=self.timeout,
                    ssl=self.verify_ssl,
                ) as response:
                    end_time = datetime.now()
                    response_time = (end_time - start_time).total_seconds() * 1000  # in ms

                    details = {"status_code": response.status, "response_time_ms": round(response_time, 2)}

                    if response.status == self.expected_status:
                        return ServiceState(
                            name=self.name,
                            status=ServiceStatus.HEALTHY,
                            last_checked=datetime.utcnow(),
                            details=details,
                        )
                    else:
                        details["error"] = f"Expected status {self.expected_status}, got {response.status}"
                        return ServiceState(
                            name=self.name,
                            status=ServiceStatus.UNHEALTHY,
                            last_checked=datetime.utcnow(),
                            details=details,
                        )

        except asyncio.TimeoutError:
            return ServiceState(
                name=self.name,
                status=ServiceStatus.UNHEALTHY,
                last_checked=datetime.utcnow(),
                details={"error": "Request timed out"},
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
                "url": {"type": "string", "format": "uri"},
                "method": {
                    "type": "string",
                    "enum": ["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"],
                    "default": "GET",
                },
                "timeout": {"type": "number", "default": 30},
                "expected_status": {"type": "integer", "default": 200},
                "headers": {"type": "object", "additionalProperties": {"type": "string"}, "default": {}},
                "body": {"type": ["object", "null"], "default": None},
                "verify_ssl": {"type": "boolean", "default": True},
            },
            "required": ["name", "url"],
        }
