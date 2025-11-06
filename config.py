"""Root-level config module for backward compatibility with main_ui.py.

This module provides a simple interface that main_ui.py expects,
bridging to the actual configuration system in src/config.py.
"""

from src.config import load_app_config

# Load the app config
_app_config = load_app_config()


class config:
    """Configuration object that mimics the old config interface."""

    scene = _app_config.scene
    app = _app_config.app
    ui = _app_config.ui
    llm = _app_config.llm
    heysol = _app_config.heysol
    chat = _app_config.chat
    prompts = _app_config.prompts
