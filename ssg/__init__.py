"""
ssg package public API.
Provides build() and clean() functions that orchestrate the static site generation pipeline.
"""

from .config import load_config, ConfigError
from .content import load_content
from .navigation import build_navigation
from .renderer import render_pages

def build(config_path: str = None) -> dict:
    """
    Build the static site.

    Args:
        config_path: Optional path to a YAML configuration file. If None,
                     the default ``site.yaml`` in the current working directory
                     is used.

    Returns:
        A summary dictionary with keys ``pages_built`` and ``output_dir``.
    """
    cfg = load_config(config_path)
    pages = load_content(cfg)
    # Exclude draft pages from the build pipeline
    pages = [p for p in pages if not getattr(p, "draft", False)]
    nav = build_navigation(pages, cfg)
    render_pages(pages, nav, cfg)
    return {"pages_built": len(pages), "output_dir": cfg["output_dir"]}

def clean(config_path: str = None) -> str:
    """
    Remove the output directory.

    Args:
        config_path: Optional path to a YAML configuration file. If None,
                     the default ``site.yaml`` is used to locate the output_dir.

    Returns:
        A confirmation message.
    """
    cfg = load_config(config_path)
    import shutil
    import os
    out_dir = cfg["output_dir"]
    if os.path.isdir(out_dir):
        shutil.rmtree(out_dir)
    return f"Removed output directory: {out_dir}"