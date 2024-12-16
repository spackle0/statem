import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Dict

import yaml
from fastapi import FastAPI
from stevedore import driver

from .config import get_config
from .logger import setup_logging
from .models import ServiceConfig
from .service_modules.base import ServiceModule

# Service registry
services: Dict[str, ServiceModule] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown events"""
    # Startup
    config = get_config()
    setup_logging(level=config.log.level, format=config.log.format)
    logger = logging.getLogger("status_tiles")

    config_path = Path("config.yml")
    if not config_path.exists():
        logger.warning("No config.yml found. Using default configuration.")
        yield
        return

    with open(config_path) as f:
        config = yaml.safe_load(f)

    for service_config in config.get("services", []):
        try:
            service_cfg = ServiceConfig(**service_config)
            mgr = driver.DriverManager(
                namespace="status_tiles.modules",
                name=service_cfg.type,
                invoke_on_load=True,
                invoke_args=(service_cfg.config,),
            )
            services[service_cfg.name] = mgr.driver
            logger.info(f"Loaded service module: {service_cfg.name}")
        except Exception as e:
            logger.error(f"Failed to load service {service_config.get('name')}: {e}")

    yield

    # Shutdown
    # Clean up any resources here
    services.clear()


app = FastAPI(title="Status Tiles", lifespan=lifespan)
logger = logging.getLogger(__name__)

# Rest of the api.py code remains the same...
