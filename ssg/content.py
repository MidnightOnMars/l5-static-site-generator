"""
Content loading and page representation.
"""

import os
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import yaml

FRONT_MATTER_REGEX = re.compile(r'^---\s*$.*?^---\s*$', re.DOTALL | re.MULTILINE)

def _parse_front_matter(text: str) -> (Dict, str):
    """
    Split a markdown file into front matter (as a dict) and body text.
    If no front matter is present, returns an empty dict and the original text.
    """
    if text.startswith('---'):
        parts = text.split('---', 2)
        if len(parts) >= 3:
            # parts[1] is the YAML front matter, parts[2] is the body
            fm = yaml.safe_load(parts[1]) or {}
            body = parts[2].lstrip('\n')
            return fm, body
    return {}, text

def _slug_from_path(rel_path: Path) -> str:
    """
    Convert a relative path like ``blog/post.md`` into a URL slug.
    Handles ``index.md`` specially.
    """
    parts = rel_path.with_suffix('').parts  # drop .md
    if parts[-1] == "index":
        # ``content/blog/index.md`` -> ``blog/``
        slug = "/".join(parts[:-1])
    else:
        slug = "/".join(parts)
    return slug

def _title_from_filename(name: str) -> str:
    """
    Derive a title from a filename (e.g. ``my-cool-page.md`` -> ``My Cool Page``).
    """
    base = Path(name).stem
    words = base.replace('-', ' ').replace('_', ' ').split()
    return " ".join(w.capitalize() for w in words)

@dataclass
class Page:
    source_path: Path
    slug: str
    title: str
    template: Optional[str] = None
    date: Optional[str] = None
    draft: bool = False
    content: str = ""
    extra: Dict = field(default_factory=dict)

def load_content(config: dict) -> List[Page]:
    """
    Walk the content directory, parse markdown files, and return a list of Page objects.
    """
    content_root = Path(config["content_dir"])
    pages: List[Page] = []
    if not content_root.is_dir():
        # Missing content directory is not an error; return empty list.
        return pages

    for md_path in content_root.rglob("*.md"):
        rel_path = md_path.relative_to(content_root)
        with md_path.open("r", encoding="utf-8") as f:
            raw = f.read()
        front, body = _parse_front_matter(raw)

        title = front.get("title")
        if not title:
            title = _title_from_filename(md_path.name)

        page = Page(
            source_path=md_path,
            slug=_slug_from_path(rel_path),
            title=title,
            template=front.get("template"),
            date=front.get("date"),
            draft=bool(front.get("draft", False)),
            content=body,
            extra={k: v for k, v in front.items() if k not in {"title", "template", "date", "draft"}}
        )
        pages.append(page)

    return pages