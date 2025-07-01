#!/usr/bin/env python3
"""
Halo Blog Tools Plugin for Dify
Main entry point for the plugin
"""

import os
import logging
from dotenv import load_dotenv
from dify_plugin import DifyPluginEnv, Plugin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_plugin() -> Plugin:
    """Create and configure the Halo Blog Tools plugin."""
    try:
        # Load environment variables from .env file only if INSTALL_METHOD is not already set
        if not os.getenv('INSTALL_METHOD'):
            load_dotenv()
        
        # Log environment setup
        install_method = os.getenv('INSTALL_METHOD')
        remote_host = os.getenv('REMOTE_INSTALL_HOST')
        remote_port = os.getenv('REMOTE_INSTALL_PORT')
        remote_key = os.getenv('REMOTE_INSTALL_KEY')
        
        logger.info(f"Plugin starting with install method: {install_method}")
        if remote_host:
            logger.info(f"Remote host configured: {remote_host}:{remote_port}")
        if remote_key:
            logger.info(f"Remote key configured: {'*' * max(0, len(remote_key) - 8) + remote_key[-8:] if len(remote_key) > 8 else '*' * len(remote_key)}")
        
        plugin = Plugin(DifyPluginEnv())
        logger.info("Halo Blog Tools plugin initialized successfully")
        return plugin
        
    except Exception as e:
        logger.error(f"Failed to initialize plugin: {e}")
        raise


if __name__ == '__main__':
    try:
        # Start the plugin daemon
        logger.info("Starting Halo Blog Tools plugin...")
        plugin = create_plugin()
        plugin.run()
    except KeyboardInterrupt:
        logger.info("Plugin stopped by user")
    except Exception as e:
        logger.error(f"Plugin failed to start: {e}")
        raise 