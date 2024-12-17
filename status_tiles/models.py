from datetime import datetime
from enum import Enum
from typing import Any, Dict

from pydantic import BaseModel


class ServiceStatus(str, Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ServiceState(BaseModel):
    name: str
    status: ServiceStatus
    last_checked: datetime
    details: Dict[str, Any] = {}


class ServiceConfig(BaseModel):
    name: str
    type: str
    config: Dict[str, Any]
    polling_interval: int = 300  # 5 minutes default
