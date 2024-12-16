import argparse
import sys
from pathlib import Path

import uvicorn

from status_tiles.api import app  # Import the FastAPI app
from status_tiles.config import get_config
from status_tiles.logger import setup_logging


def main():
    parser = argparse.ArgumentParser(description="Status Tiles Service")
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to"
    )
    parser.add_argument(
        "--config",
        type=Path,
        default="config.yml",
        help="Path to config file"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload"
    )

    args = parser.parse_args()

    # Load config and setup logging early
    try:
        config = get_config(args.config)
        setup_logging(
            level=config.log.level,
            format=config.log.format
        )
    except Exception as e:
        print(f"Failed to initialize: {e}", file=sys.stderr)
        sys.exit(1)

    uvicorn.run(
        app,  # Pass the app directly instead of a string
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=config.log.level.lower()
    )

if __name__ == "__main__":
    main()

# Export the app for uvicorn to find
__all__ = ['app']
