# Static Site Generator (ssg)

A lightweight Python static site generator that transforms Markdown content into HTML using Jinja2 templates, with support for YAML configuration, syntax‑highlighted code blocks, and a simple development server.

## Installation

```bash
git clone https://github.com/MidnightOnMars/l5-static-site-generator.git
cd l5-static-site-generator
python -m venv .venv
source .venv/bin/activate
pip install jinja2 pyyaml pygments markdown
```

## Quick start

```text
my‑site/
├─ content/          # Markdown files
├─ templates/        # Jinja2 templates
└─ site.yaml         # Configuration file
```

1. Create the directories above and add at least one Markdown file in `content/`.
2. Add a template (e.g., `templates/page.html`).
3. Create a minimal `site.yaml` (or rely on defaults).
4. Build the site:

```bash
python -m ssg build
```

The generated HTML will appear in the `output/` directory.

## Configuration reference (`site.yaml`)

| Key               | Default               | Description |
|-------------------|-----------------------|-------------|
| `title`           | `"My Site"`           | Site title (used in templates). |
| `base_url`        | `"/"`                 | Base URL for generated links. |
| `content_dir`     | `"content"`           | Directory containing Markdown files. |
| `output_dir`      | `"output"`            | Directory where HTML files are written. |
| `template_dir`    | `"templates"`         | Directory containing Jinja2 templates. |
| `default_template`| `"page.html"`         | Fallback template for pages without a specific `template` front‑matter. |
| `highlight_style`| `"monokai"`           | Pygments style for code highlighting. |

All keys are optional; omitted keys fall back to the defaults above.

## Content format

Markdown files may start with a YAML front‑matter block delimited by `---`:

```yaml
---
title: "My First Post"
date: "2024-01-01"
template: "post.html"
draft: false
tags: ["example", "demo"]
---
```

Supported front‑matter fields:

* `title` – page title (defaults to a title derived from the filename).
* `template` – name of the Jinja2 template to use.
* `date` – optional publication date.
* `draft` – if `true`, the page is excluded from navigation and output.
* Any additional keys are exposed to the template via `page.<key>`.

Markdown features are provided by the `markdown` library with the extensions `fenced_code`, `codehilite`, and `extra`.

## Directory structure convention

```
content/          → source Markdown files (mirrored hierarchy)
templates/        → Jinja2 templates
output/           → generated HTML (mirrored hierarchy)
site.yaml         → optional configuration file
```

A file `content/blog/post.md` becomes `output/blog/post/index.html`. An `index.md` file maps to the directory root (`output/blog/index.html`).

## CLI commands

| Command | Description |
|---------|-------------|
| `ssg build [-c CONFIG]` | Build the site. `CONFIG` defaults to `site.yaml`. |
| `ssg clean [-c CONFIG]` | Remove the generated `output/` directory. |
| `ssg serve [-c CONFIG] [--host HOST] [--port PORT]` | Start a development server (default `localhost:8000`) that watches `content/` and `templates/` for changes and rebuilds automatically. |

## Template variables

* `page.title` – page title.  
* `page.content` – rendered HTML content (safe for insertion).  
* `page.date` – optional date.  
* `page.slug` – URL slug derived from the file path.  
* `page.url` – full URL (`base_url` + `slug`).  
* `page.<extra>` – any additional front‑matter fields.  

* `site` – the full configuration dictionary (e.g., `site.title`).  

* `nav` – list of navigation items (each with `title`, `url`, `children`). Generated from non‑draft pages and sorted alphabetically.

---

Enjoy building your static site with **ssg**!