"""
Rendering engine: markdown → HTML + Jinja2 templates.
"""

import os
from pathlib import Path
from typing import List, Dict

import markdown
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

def _ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def render_pages(pages: List[object], navigation: List[Dict], config: dict) -> None:
    """
    Render each page using its template (or the default) and write the output HTML.
    """
    env = Environment(
        loader=FileSystemLoader(config["template_dir"]),
        autoescape=select_autoescape(["html", "xml"])
    )
    # Enable code highlighting with the configured style
    md = markdown.Markdown(
        extensions=["fenced_code", "codehilite", "extra"],
        extension_configs={
            "codehilite": {
                "css_class": "highlight",
                "pygments_style": config.get("highlight_style", "monokai")
            }
        }
    )

    for page in pages:
        template_name = page.template or config["default_template"]
        try:
            tmpl = env.get_template(template_name)
        except Exception as exc:
            raise RuntimeError(f"Template '{template_name}' not found: {exc}")

        # Convert markdown body to HTML
        html_body = md.convert(page.content)
        # Reset markdown instance for next conversion (clears state)
        md.reset()
        # Mark HTML as safe for Jinja2 autoescaping
        html_body = Markup(html_body)

        # Build page context
        page_ctx = {
            "title": page.title,
            "content": html_body,
            "date": getattr(page, "date", None),
            "slug": page.slug,
            "url": f"{config.get('base_url', '/').rstrip('/')}/{page.slug}/" if page.slug else config.get("base_url", "/"),
            **page.extra
        }

        rendered = tmpl.render(page=page_ctx, site=config, nav=navigation)

        # Determine output path
        out_dir = Path(config["output_dir"])
        if page.slug:
            target_dir = out_dir / page.slug
        else:
            target_dir = out_dir
        _ensure_dir(target_dir)
        out_file = target_dir / "index.html"
        out_file.write_text(rendered, encoding="utf-8")