#!/usr/bin/env python3
"""
Application entry point for ExamSaaS platform.
"""
import logging
import os

from app import create_app
from app.config import Config

logger = logging.getLogger(__name__)


def main():
    """Run the Flask application."""
    config = Config.from_env()
    app = create_app(config)
    
    host = os.environ.get("FLASK_HOST", "0.0.0.0")
    port = int(os.environ.get("FLASK_PORT", 5000))
    debug = config.DEBUG
    
    logger.info(f"Starting ExamSaaS API on {host}:{port} (debug={debug})")
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    main()
