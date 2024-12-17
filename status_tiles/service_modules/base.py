from abc import ABC, abstractmethod
from typing import Any, Dict

from ..models import ServiceState


class ServiceModule(ABC):
    """Base class for all service monitoring modules"""

    @abstractmethod
    async def get_status(self) -> ServiceState:
        """Fetch and return the current status of the service"""
        pass

    @abstractmethod
    def get_config_schema(self) -> Dict[str, Any]:
        """Return the configuration schema for this module"""
        pass
