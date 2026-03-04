"""
Configuration handling for the static site generator.
"""

import os
import yaml
from pathlib import Path

class ConfigError(Exception):
    """Raised when the configuration file cannot be parsed."""
    pass

DEFAULTS = {
    "title": "My Site",
    "base_url": "/",
    "content_dir": "content",
    "output_dir": "output",
    "template_dir": "templates",
    "default_template": "page.html",
    "highlight_style": "monokai",
}

def load_config(path: str = None) -> dict:
    """
    Load configuration from a YAML file and merge with defaults.

    Args:
        path: Optional path to a YAML configuration file. If omitted,
              ``site.yaml`` in the current working directory is used.

    Returns:
        A dictionary containing the complete configuration.

    Raises:
        ConfigError: If the YAML file exists but cannot be parsed.
    """
    config_path = Path(path) if path else Path("site.yaml")
    config = {}
    if config_path.is_file():
        try:
            with config_path.open("r", encoding="utf-8") as f:
                raw = yaml.safe_load(f) or {}
                if not isinstance(raw, dict):
                    raise ConfigError("Configuration file must contain a mapping.")
                config = raw
        except yaml.YAMLError as exc:
            raise ConfigError(f"Error parsing configuration file: {exc}") from exc
    # Merge defaults (user values override defaults)
    merged = DEFAULTS.copy()
    merged.update(config)
    # Resolve paths relative to the project root
    merged["content_dir"] = str(Path(merged["content_dir"]))
    merged["output_dir"] = str(Path(merged["output_dir"]))
    merged["template_dir"] = str(Path(merged["template_dir"]))
    return merged