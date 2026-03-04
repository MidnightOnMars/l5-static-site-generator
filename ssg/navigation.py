"""
Navigation tree construction.
"""

from typing import List, Dict
from .content import Page

def build_navigation(pages: List[Page], config: dict) -> List[Dict]:
    """
    Build a flat navigation list for all non‑draft pages.
    Each entry is a dict with ``title``, ``url`` and ``children`` (empty list).
    The list is sorted alphabetically by title.
    """
    base = config.get("base_url", "/")
    if not base.endswith("/"):
        base += "/"

    nav_items = []
    for page in pages:
        if getattr(page, "draft", False):
            continue
        url = f"{base}{page.slug}/" if page.slug else f"{base}"
        nav_items.append({
            "title": page.title,
            "url": url,
            "children": []
        })

    # Sort alphabetically by title
    nav_items.sort(key=lambda x: x["title"].lower())
    return nav_items